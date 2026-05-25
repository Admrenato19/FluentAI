# 🎬 FluentAI — Aprenda Inglês com IA + Cinema

App de aprendizado de inglês com IA, método shadowing, conversação e flashcards com revisão espaçada.

---

## 🚀 Como usar

### Opção 1 — Streamlit Cloud (Grátis, acesso pelo celular)

1. Crie uma conta em [streamlit.io](https://streamlit.io)
2. Crie um repositório no GitHub e suba os arquivos
3. Em Streamlit Cloud → "New app" → selecione o repositório
4. Configure o arquivo `app.py` como entry point
5. Acesse pelo link gerado — funciona no celular!

**Dica de segurança:** No Streamlit Cloud, vá em Settings → Secrets e adicione:
```
ANTHROPIC_API_KEY = "sk-ant-..."
```

### Opção 2 — Rodar localmente

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Rodar o app
streamlit run app.py

# 3. Acessar no celular (mesma rede Wi-Fi)
# O terminal mostrará o endereço: http://192.168.x.x:8501
```

---

## 📁 Estrutura do projeto

```
english_app/
├── app.py                  # App principal
├── requirements.txt        # Dependências
├── pages/
│   ├── shadowing.py        # Módulo de shadowing com filmes/séries
│   ├── conversation.py     # Conversação com professor IA
│   ├── flashcards.py       # Flashcards com revisão espaçada (SRS)
│   └── progress.py         # Progresso e estatísticas
└── utils/
    └── claude_api.py       # Funções para chamar a API do Claude
```

---

## 🔑 API Key

- Crie sua conta em [console.anthropic.com](https://console.anthropic.com)
- Gere uma API Key em API Keys
- Cole no campo da barra lateral do app

---

## ✨ Funcionalidades

| Funcionalidade | Descrição |
|---|---|
| 🎬 Shadowing | Cenas de filmes/séries com feedback de IA |
| 🤖 Conversação | 4 professores IA com estilos diferentes |
| 🃏 Flashcards SRS | Revisão espaçada científica (algoritmo SM-2) |
| ✨ Geração com IA | Crie flashcards sobre qualquer tema |
| 📊 Progresso | XP, níveis e sequência diária |

---

## 💡 Método Shadowing

1. Leia a cena em inglês
2. Fale em voz alta acompanhando o texto
3. Escreva o que você disse no campo de texto
4. Receba feedback detalhado da IA
5. Repita 3–5 vezes

---

Feito com ❤️ usando Streamlit + Claude (Anthropic)
