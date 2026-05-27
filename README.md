# 🤖 Chat IA — Python + Tkinter + OpenRouter

Bem-vindo(a) ao **Chat IA**! Um chat desktop desenvolvido em Python com interface gráfica nativa via Tkinter, integrado à API do OpenRouter.

---

## ✨ Funcionalidades

- 🔐 Login e registro de usuário
- 💬 Múltiplas conversas independentes
- 🌙 Tema Dark / ☀️ Tema Light
- 🗂️ CRUD completo de usuários e conversas
- 🤖 Integração com a API OpenRouter (DeepSeek V3 Pro)

---

## 📋 Pré-requisitos

Antes de começar, você precisa ter instalado:

- [Python 3.10+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/)
- Uma chave de API do [OpenRouter](https://openrouter.ai/)

---

## 🚀 Comece agora

**1. Clone o repositório**

```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
```

**2. Acesse a pasta do projeto**

```bash
cd seu-repositorio
```

**3. Instale as dependências**

```bash
pip install openai
```

**4. Configure sua chave de API**

Abra o arquivo `chat_ia.py` e insira sua chave do OpenRouter na linha indicada:

```python
API_KEY = "sk-or-..."  # ← cole sua chave aqui
```

> Você pode obter sua chave em [openrouter.ai/settings/keys](https://openrouter.ai/settings/keys)

**5. Inicie o aplicativo**

```bash
python chat_ia.py
```

---

## 📁 Estrutura do projeto

```
📁 seu-repositorio/
├── chat_ia.py   # Código principal — lógica e interface
└── tema.py      # Estilização — cores, fontes e widgets
```

---

## 🔄 Trocar o modelo de IA

Por padrão o projeto usa o **DeepSeek V3 Pro**. Para trocar, edite a linha abaixo em `chat_ia.py`:

```python
model="deepseek/deepseek-chat-v3-0324"  # substitua pelo modelo desejado
```

Confira todos os modelos disponíveis em [openrouter.ai/models](https://openrouter.ai/models).

---

## 🛠️ Tecnologias utilizadas

- **Python 3.10+**
- **Tkinter** — interface gráfica nativa
- **OpenAI SDK** — cliente para a API OpenRouter
- **hashlib / uuid / datetime** — bibliotecas nativas Python

---

## ⚠️ Aviso de segurança

Nunca suba sua `API_KEY` para o GitHub. Adicione ao `.gitignore`:

```bash
# .gitignore
*.env
```

Ou use variáveis de ambiente no lugar da chave direta:

```python
import os
API_KEY = os.getenv("OPENROUTER_API_KEY", "")
```
