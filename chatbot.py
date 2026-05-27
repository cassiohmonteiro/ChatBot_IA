import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from openai import OpenAI
import hashlib
import uuid
from datetime import datetime
from tema import TEMAS, FONTES, obter_tema, criar_btn, criar_btn_tema


# CONFIGURAÇÃO  –  coloque sua chave aqui

API_KEY = "coloque sua chave aqui"  # obtenha em https://openrouter.ai/dashboard    

# BANCO DE DADOS EM MEMÓRIA

usuarios = {}          # { username: { "senha_hash": str } }
conversas  = {}        # { conv_id: { "titulo": str, "owner": str, "mensagens": list } }

def hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode()).hexdigest()

#  CRUD – USUÁRIOS

def criar_usuario(username: str, senha: str) -> tuple[bool, str]:
    if not username or not senha:
        return False, "Usuário e senha não podem ser vazios."
    if username in usuarios:
        return False, "Usuário já existe."
    usuarios[username] = {"senha_hash": hash_senha(senha)}
    return True, "Usuário criado com sucesso."

def autenticar_usuario(username: str, senha: str) -> bool:
    u = usuarios.get(username)
    return u is not None and u["senha_hash"] == hash_senha(senha)

def alterar_senha(username: str, nova_senha: str) -> tuple[bool, str]:
    if username not in usuarios:
        return False, "Usuário não encontrado."
    usuarios[username]["senha_hash"] = hash_senha(nova_senha)
    return True, "Senha alterada com sucesso."

def deletar_usuario(username: str):
    usuarios.pop(username, None)
    # Remove conversas do usuário
    ids_remover = [cid for cid, c in conversas.items() if c["owner"] == username]
    for cid in ids_remover:
        conversas.pop(cid)

#  CRUD – CONVERSAS

def criar_conversa(owner: str, titulo: str = "") -> str:
    cid = str(uuid.uuid4())
    titulo = titulo or f"Conversa {datetime.now().strftime('%d/%m %H:%M')}"
    conversas[cid] = {"titulo": titulo, "owner": owner, "mensagens": []}
    return cid

def listar_conversas(owner: str) -> list[tuple[str, str]]:
    return [(cid, c["titulo"]) for cid, c in conversas.items() if c["owner"] == owner]

def renomear_conversa(cid: str, novo_titulo: str):
    if cid in conversas:
        conversas[cid]["titulo"] = novo_titulo

def deletar_conversa(cid: str):
    conversas.pop(cid, None)

def adicionar_mensagem(cid: str, role: str, content: str):
    if cid in conversas:
        conversas[cid]["mensagens"].append({"role": role, "content": content})

def obter_mensagens(cid: str) -> list:
    return conversas.get(cid, {}).get("mensagens", [])

#  APLICAÇÃO PRINCIPAL

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ChatBot IA")
        self.geometry("960x660")
        self.minsize(760, 520)
        self.resizable(True, True)

        self.tema_atual = tk.StringVar(value="dark")
        self.usuario_logado: str | None = None
        self.conversa_atual: str | None = None
        self.cliente_openai = OpenAI(
            api_key=API_KEY,
            base_url="https://openrouter.ai/api/v1"
        ) if API_KEY else None

        self._construir_tela_login()

    # ── helpers de tema ──────────────────────
    @property
    def t(self) -> dict:
        return TEMAS[self.tema_atual.get()]

    def _cor(self, chave: str) -> str:
        return self.t[chave]

    #  TELA DE LOGIN / REGISTRO
    
    def _construir_tela_login(self):
        self._limpar_janela()
        t = self.t
        self.configure(bg=t["bg"])

        frame = tk.Frame(self, bg=t["bg"])
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text="🤖 ChatBot IA", font=("Segoe UI", 26, "bold"),
                 bg=t["bg"], fg=t["accent"]).pack(pady=(0, 24))

        # Campos
        for label, attr in [("Usuário", "entry_user"), ("Senha", "entry_pass")]:
            tk.Label(frame, text=label, font=("Segoe UI", 11),
                     bg=t["bg"], fg=t["subtext"]).pack(anchor="w")
            e = tk.Entry(frame, font=("Segoe UI", 12), bg=t["input_bg"],
                         fg=t["entry_fg"], insertbackground=t["text"],
                         relief="flat", bd=0, width=28,
                         show="*" if label == "Senha" else "")
            e.pack(ipady=6, pady=(2, 10))
            setattr(self, attr, e)

        # Botões
        btn_frame = tk.Frame(frame, bg=t["bg"])
        btn_frame.pack(fill="x", pady=(4, 0))

        self._btn(btn_frame, "Entrar",     self._login).pack(side="left", padx=(0,6), expand=True, fill="x")
        self._btn(btn_frame, "Registrar",  self._registrar, secondary=True).pack(side="left", expand=True, fill="x")

        # Toggle tema
        self._btn_tema(frame).pack(pady=(20, 0))

        self.entry_user.focus()
        self.bind("<Return>", lambda e: self._login())

    def _login(self):
        user = self.entry_user.get().strip()
        senha = self.entry_pass.get()
        if autenticar_usuario(user, senha):
            self.usuario_logado = user
            self._construir_tela_chat()
        else:
            messagebox.showerror("Erro", "Usuário ou senha incorretos.")

    def _registrar(self):
        user  = self.entry_user.get().strip()
        senha = self.entry_pass.get()
        ok, msg = criar_usuario(user, senha)
        if ok:
            messagebox.showinfo("Sucesso", msg)
        else:
            messagebox.showerror("Erro", msg)

    #  TELA PRINCIPAL DE CHAT

    def _construir_tela_chat(self):
        self._limpar_janela()
        t = self.t
        self.configure(bg=t["bg"])
        self.unbind("<Return>")

        # layout raiz 
        self.paned = tk.PanedWindow(self, orient="horizontal",
                                    bg=t["bg"], sashwidth=4,
                                    sashrelief="flat")
        self.paned.pack(fill="both", expand=True)

        # SIDEBAR 
        self.frame_sidebar = tk.Frame(self.paned, bg=t["sidebar"], width=220)
        self.paned.add(self.frame_sidebar, minsize=160)

        # cabeçalho sidebar
        hdr = tk.Frame(self.frame_sidebar, bg=t["sidebar"])
        hdr.pack(fill="x", padx=10, pady=(14, 6))
        tk.Label(hdr, text="💬 Conversas", font=("Segoe UI", 11, "bold"),
                 bg=t["sidebar"], fg=t["text"]).pack(side="left")
        self._btn(hdr, "+", self._nova_conversa, small=True).pack(side="right")

        # lista de conversas
        self.lista_conv_frame = tk.Frame(self.frame_sidebar, bg=t["sidebar"])
        self.lista_conv_frame.pack(fill="both", expand=True, padx=4)

        # rodapé sidebar
        rodape = tk.Frame(self.frame_sidebar, bg=t["sidebar"])
        rodape.pack(fill="x", padx=10, pady=10)
        tk.Label(rodape, text=f"👤 {self.usuario_logado}",
                 font=("Segoe UI", 10), bg=t["sidebar"],
                 fg=t["subtext"]).pack(anchor="w")
        btn_row = tk.Frame(rodape, bg=t["sidebar"])
        btn_row.pack(fill="x", pady=(6, 0))
        self._btn(btn_row, "⚙ Conta",  self._gerenciar_conta, secondary=True, small=True).pack(side="left", padx=(0,4))
        self._btn(btn_row, "Sair",      self._sair, danger=True,    small=True).pack(side="left")
        self._btn_tema(rodape).pack(anchor="w", pady=(6,0))

        # ÁREA DE CHAT 
        self.frame_chat = tk.Frame(self.paned, bg=t["bg"])
        self.paned.add(self.frame_chat, minsize=400)

        # mensagens
        self.frame_msgs = tk.Frame(self.frame_chat, bg=t["bg"])
        self.frame_msgs.pack(fill="both", expand=True, padx=0, pady=0)

        self.canvas = tk.Canvas(self.frame_msgs, bg=t["bg"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.frame_msgs, orient="vertical",
                                        command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.msgs_inner = tk.Frame(self.canvas, bg=t["bg"])
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.msgs_inner, anchor="nw")

        self.msgs_inner.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>",     self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # barra de entrada
        entrada_frame = tk.Frame(self.frame_chat, bg=t["sidebar"], pady=10)
        entrada_frame.pack(fill="x", side="bottom", padx=12, pady=(0,12))

        self.entrada = tk.Text(entrada_frame, height=3, font=("Segoe UI", 11),
                                bg=t["input_bg"], fg=t["entry_fg"],
                                insertbackground=t["text"],
                                relief="flat", bd=0, wrap="word")
        self.entrada.pack(side="left", fill="both", expand=True,
                           padx=(10,8), pady=8)
        self.entrada.bind("<Return>",       self._enviar_enter)
        self.entrada.bind("<Shift-Return>", lambda e: None)

        self._btn(entrada_frame, "Enviar ➤", self._enviar_mensagem).pack(
            side="right", padx=(0,10), pady=8, ipady=8)

        # popula
        self._atualizar_lista_conversas()
        if not listar_conversas(self.usuario_logado):
            cid = criar_conversa(self.usuario_logado)
            self._selecionar_conversa(cid)
        else:
            primeiro = listar_conversas(self.usuario_logado)[0][0]
            self._selecionar_conversa(primeiro)

    # callbacks canvas/scroll 
    def _on_frame_configure(self, _=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # lista de conversas 
    def _atualizar_lista_conversas(self):
        for w in self.lista_conv_frame.winfo_children():
            w.destroy()
        t = self.t
        for cid, titulo in listar_conversas(self.usuario_logado):
            row = tk.Frame(self.lista_conv_frame, bg=t["sidebar"], cursor="hand2")
            row.pack(fill="x", pady=2)

            ativo = (cid == self.conversa_atual)
            cor_bg  = t["accent"]   if ativo else t["sidebar"]
            cor_fg  = t["btn_fg"]   if ativo else t["text"]

            lbl = tk.Label(row, text=titulo[:26], font=("Segoe UI", 10),
                           bg=cor_bg, fg=cor_fg, anchor="w", padx=8, pady=5,
                           cursor="hand2")
            lbl.pack(side="left", fill="x", expand=True)
            lbl.bind("<Button-1>", lambda e, c=cid: self._selecionar_conversa(c))

            # botão renomear / deletar
            menu_btn = tk.Label(row, text="⋮", font=("Segoe UI", 13),
                                bg=cor_bg, fg=cor_fg, padx=6, cursor="hand2")
            menu_btn.pack(side="right")
            menu_btn.bind("<Button-1>", lambda e, c=cid: self._menu_conversa(e, c))

    def _menu_conversa(self, event, cid: str):
        m = tk.Menu(self, tearoff=0)
        t = self.t
        m.configure(bg=t["input_bg"], fg=t["text"], activebackground=t["accent"],
                    activeforeground=t["btn_fg"], relief="flat", bd=0)
        m.add_command(label="✏ Renomear",
                      command=lambda: self._renomear_conversa(cid))
        m.add_command(label="🗑 Deletar",
                      command=lambda: self._deletar_conversa(cid))
        m.tk_popup(event.x_root, event.y_root)

    def _selecionar_conversa(self, cid: str):
        self.conversa_atual = cid
        self._atualizar_lista_conversas()
        self._renderizar_conversa()

    def _nova_conversa(self):
        cid = criar_conversa(self.usuario_logado)
        self._selecionar_conversa(cid)

    def _renomear_conversa(self, cid: str):
        novo = simpledialog.askstring("Renomear", "Novo título:",
                                       parent=self)
        if novo:
            renomear_conversa(cid, novo)
            self._atualizar_lista_conversas()

    def _deletar_conversa(self, cid: str):
        if messagebox.askyesno("Deletar", "Deletar esta conversa?"):
            deletar_conversa(cid)
            self.conversa_atual = None
            convs = listar_conversas(self.usuario_logado)
            if convs:
                self._selecionar_conversa(convs[0][0])
            else:
                cid2 = criar_conversa(self.usuario_logado)
                self._selecionar_conversa(cid2)

    # renderização de mensagens
    def _renderizar_conversa(self):
        for w in self.msgs_inner.winfo_children():
            w.destroy()
        if not self.conversa_atual:
            return
        t = self.t
        for msg in obter_mensagens(self.conversa_atual):
            self._adicionar_bolha(msg["role"], msg["content"])
        self._scroll_para_baixo()

    def _adicionar_bolha(self, role: str, content: str):
        t = self.t
        is_user = (role == "user")

        outer = tk.Frame(self.msgs_inner, bg=t["bg"])
        outer.pack(fill="x", padx=14, pady=4)

        cor_bubble = t["user_bubble"] if is_user else t["ia_bubble"]
        label_txt  = "Você" if is_user else "IA 🤖"
        anchor_val = "e"  if is_user else "w"

        inner = tk.Frame(outer, bg=t["bg"])
        inner.pack(anchor=anchor_val)

        tk.Label(inner, text=label_txt, font=("Segoe UI", 8),
                 bg=t["bg"], fg=t["subtext"]).pack(anchor=anchor_val)

        msg_frame = tk.Frame(inner, bg=cor_bubble,
                             highlightbackground=t["border"],
                             highlightthickness=1)
        msg_frame.pack(anchor=anchor_val)

        tk.Label(msg_frame, text=content, font=("Segoe UI", 11),
                 bg=cor_bubble, fg=t["text"],
                 wraplength=540, justify="left",
                 padx=12, pady=8).pack()

    def _scroll_para_baixo(self):
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    # envio de mensagem
    def _enviar_enter(self, event):
        if event.state & 0x1:   # Shift pressionado → nova linha
            return
        self._enviar_mensagem()
        return "break"

    def _enviar_mensagem(self):
        texto = self.entrada.get("1.0", "end").strip()
        if not texto:
            return
        if not self.conversa_atual:
            self._nova_conversa()
        self.entrada.delete("1.0", "end")

        adicionar_mensagem(self.conversa_atual, "user", texto)
        self._adicionar_bolha("user", texto)
        self._scroll_para_baixo()
        self.update()

        resposta = self._chamar_ia()
        adicionar_mensagem(self.conversa_atual, "assistant", resposta)
        self._adicionar_bolha("assistant", resposta)
        self._scroll_para_baixo()

    def _chamar_ia(self) -> str:
        if not self.cliente_openai:
            return "⚠ Configure sua API_KEY no topo do arquivo."
        try:
            msgs = obter_mensagens(self.conversa_atual)
            res  = self.cliente_openai.chat.completions.create(
                model="deepseek/deepseek-chat-v3-0324",
                messages=msgs
            )
            return res.choices[0].message.content
        except Exception as ex:
            return f"Erro ao chamar a IA: {ex}"

    # gerenciar conta
    def _gerenciar_conta(self):
        t = self.t
        win = tk.Toplevel(self)
        win.title("Gerenciar Conta")
        win.geometry("340x300")
        win.configure(bg=t["bg"])
        win.resizable(False, False)

        tk.Label(win, text="⚙ Gerenciar Conta", font=("Segoe UI", 14, "bold"),
                 bg=t["bg"], fg=t["accent"]).pack(pady=(20, 16))

        tk.Label(win, text="Nova Senha:", font=("Segoe UI", 11),
                 bg=t["bg"], fg=t["subtext"]).pack(anchor="w", padx=24)
        e_senha = tk.Entry(win, show="*", font=("Segoe UI", 12),
                           bg=t["input_bg"], fg=t["entry_fg"],
                           insertbackground=t["text"], relief="flat", width=28)
        e_senha.pack(padx=24, ipady=6, pady=(2,12))

        def salvar_senha():
            ok, msg = alterar_senha(self.usuario_logado, e_senha.get())
            messagebox.showinfo("Conta", msg, parent=win)

        def excluir_conta():
            if messagebox.askyesno("Excluir", "Excluir sua conta?", parent=win):
                deletar_usuario(self.usuario_logado)
                win.destroy()
                self._sair()

        self._btn(win, "Salvar Nova Senha", salvar_senha).pack(padx=24, fill="x", pady=(0,8))
        self._btn(win, "Excluir Conta",     excluir_conta, danger=True).pack(padx=24, fill="x")

    # sair
    def _sair(self):
        self.usuario_logado  = None
        self.conversa_atual  = None
        self._construir_tela_login()

    # troca de tema
    def _trocar_tema(self):
        self.tema_atual.set(
            "light" if self.tema_atual.get() == "dark" else "dark"
        )
        # reconstrói tela atual
        if self.usuario_logado:
            self._construir_tela_chat()
        else:
            self._construir_tela_login()

    def _btn_tema(self, parent) -> tk.Button:
        """Delega para tema.py — botão de alternância dark/light."""
        return criar_btn_tema(parent, self.tema_atual, self.t, self._trocar_tema)

    #  helper de botão estilizado
    def _btn(self, parent, texto: str, cmd=None, *,
             secondary=False, danger=False, small=False) -> tk.Button:
        """Delega para tema.py — botão estilizado."""
        return criar_btn(parent, texto, self.t, cmd,
                         secondary=secondary, danger=danger, small=small)

    # limpar janela 
    def _limpar_janela(self):
        for w in self.winfo_children():
            w.destroy()

#  ENTRY POINT

if __name__ == "__main__":
    app = App()
    app.mainloop()