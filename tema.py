import tkinter as tk

TEMAS: dict[str, dict[str, str]] = {
    "dark": {
        "bg":          "#1e1e2e",   # fundo principal
        "sidebar":     "#181825",   # fundo da barra lateral
        "input_bg":    "#313244",   # fundo dos campos de entrada
        "text":        "#cdd6f4",   # texto principal
        "subtext":     "#a6adc8",   # texto secundário / rótulos
        "accent":      "#89b4fa",   # cor de destaque / botão primário
        "user_bubble": "#313244",   # bolha do usuário
        "ia_bubble":   "#45475a",   # bolha da IA
        "btn_bg":      "#89b4fa",   # fundo botão primário
        "btn_fg":      "#1e1e2e",   # texto botão primário
        "btn_hover":   "#74c7ec",   # hover botão primário
        "entry_fg":    "#cdd6f4",   # texto dentro dos inputs
        "border":      "#45475a",   # bordas
        "danger":      "#f38ba8",   # botões de perigo / erro
    },
    "light": {
        "bg":          "#eff1f5",
        "sidebar":     "#e6e9ef",
        "input_bg":    "#ffffff",
        "text":        "#4c4f69",
        "subtext":     "#6c6f85",
        "accent":      "#1e66f5",
        "user_bubble": "#dce0e8",
        "ia_bubble":   "#ffffff",
        "btn_bg":      "#1e66f5",
        "btn_fg":      "#ffffff",
        "btn_hover":   "#04a5e5",
        "entry_fg":    "#4c4f69",
        "border":      "#bcc0cc",
        "danger":      "#d20f39",
    },
}

#  FONTES

FONTE_PRINCIPAL = "Segoe UI"

FONTES = {
    "titulo":    (FONTE_PRINCIPAL, 26, "bold"),
    "secao":     (FONTE_PRINCIPAL, 14, "bold"),
    "label":     (FONTE_PRINCIPAL, 11),
    "label_sm":  (FONTE_PRINCIPAL, 10),
    "label_xs":  (FONTE_PRINCIPAL,  8),
    "input":     (FONTE_PRINCIPAL, 12),
    "mensagem":  (FONTE_PRINCIPAL, 11),
    "btn":       (FONTE_PRINCIPAL, 11, "bold"),
    "btn_sm":    (FONTE_PRINCIPAL,  9, "bold"),
    "btn_tema":  (FONTE_PRINCIPAL,  9),
}

#  HELPERS DE WIDGETS ESTILIZADOS

def obter_tema(nome: str) -> dict[str, str]:
#  Retorna o dicionário de cores do tema solicitado.
    return TEMAS[nome]


def criar_btn(parent, texto: str, tema: dict, cmd=None, *,
              secondary: bool = False,
              danger: bool    = False,
              small: bool     = False) -> tk.Button:
   
    #Cria um botão estilizado de acordo com o tema atual.

    #Parâmetros
    #secondary : fundo neutro, sem destaque
    #danger    : vermelho, para ações destrutivas
    #small     : fonte e padding menores
    
    if danger:
        bg, fg = tema["danger"], "#ffffff"
    elif secondary:
        bg, fg = tema["input_bg"], tema["text"]
    else:
        bg, fg = tema["btn_bg"], tema["btn_fg"]

    fonte = FONTES["btn_sm"] if small else FONTES["btn"]
    pad_y = 4 if small else 6

    btn = tk.Button(
        parent, text=texto, command=cmd,
        font=fonte, bg=bg, fg=fg,
        relief="flat", bd=0, cursor="hand2",
        padx=10, pady=pad_y,
    )

    # efeito hover somente no botão primário
    hover_bg = tema["btn_hover"] if not danger and not secondary else bg
    btn.bind("<Enter>", lambda _: btn.configure(bg=hover_bg))
    btn.bind("<Leave>", lambda _: btn.configure(bg=bg))

    return btn

def criar_btn_tema(parent, tema_atual_var: tk.StringVar,
                   tema: dict, cmd_trocar) -> tk.Button:
    
    #Cria o botão de alternância dark/light.
    #O rótulo muda conforme o tema ativo.
    
    label = "☀ Modo Claro" if tema_atual_var.get() == "dark" else "🌙 Modo Escuro"
    return tk.Button(
        parent, text=label,
        font=FONTES["btn_tema"],
        bg=tema["input_bg"], fg=tema["subtext"],
        relief="flat", bd=0, cursor="hand2",
        command=cmd_trocar,
    )

def aplicar_fundo(widget, tema: dict, chave: str = "bg"):
    #Atalho para configurar cor de fundo de qualquer widget.
    widget.configure(bg=tema[chave])
