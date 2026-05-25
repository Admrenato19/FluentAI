import streamlit as st
import anthropic
import json
import re
import datetime

st.set_page_config(
    page_title="FluentAI - Aprenda Inglês",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

:root {
    --bg: #0D0D0F;
    --surface: #16161A;
    --surface2: #1E1E24;
    --accent: #E8FF47;
    --accent2: #FF6B6B;
    --accent3: #47CFFF;
    --text: #F0EFE9;
    --muted: #7A7A8A;
    --border: #2A2A35;
    --radius: 16px;
}
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}
.stApp { background-color: var(--bg); }
[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * { color: var(--text) !important; }
#MainMenu, footer, header { visibility: hidden; }
.stButton > button {
    background: var(--accent) !important;
    color: var(--bg) !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(232,255,71,0.3) !important;
}
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background-color: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
}
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s ease;
}
.card:hover { border-color: var(--accent); }
.card-accent {
    background: linear-gradient(135deg, #1a1a20 0%, #1e1e2a 100%);
    border: 1px solid var(--accent);
    border-radius: var(--radius);
    padding: 1.5rem;
    margin-bottom: 1rem;
}
h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
    color: var(--text) !important;
}
.accent-text { color: var(--accent); }
.muted-text { color: var(--muted); font-size: 0.9rem; }
.tag {
    display: inline-block;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.8rem;
    color: var(--muted);
    margin: 2px;
}
.msg-user {
    background: var(--surface2);
    border-radius: 16px 16px 4px 16px;
    padding: 1rem 1.2rem;
    margin: 0.5rem 0;
    border-left: 3px solid var(--accent);
    max-width: 85%;
    margin-left: auto;
}
.msg-ai {
    background: var(--surface);
    border-radius: 16px 16px 16px 4px;
    padding: 1rem 1.2rem;
    margin: 0.5rem 0;
    border-left: 3px solid var(--accent3);
    max-width: 85%;
}
.flashcard {
    background: linear-gradient(145deg, var(--surface), var(--surface2));
    border: 2px solid var(--accent);
    border-radius: 20px;
    padding: 3rem 2rem;
    text-align: center;
    min-height: 200px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.3s ease;
}
.flashcard:hover { transform: scale(1.01); box-shadow: 0 10px 40px rgba(232,255,71,0.15); }
.stProgress > div > div > div { background-color: var(--accent) !important; }
[data-testid="stMetric"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem;
}
[data-testid="stMetricValue"] { color: var(--accent) !important; font-family: 'Syne', sans-serif !important; }
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-radius: 10px !important;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--muted) !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTabs [aria-selected="true"] {
    background: var(--accent) !important;
    color: var(--bg) !important;
    font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
defaults = {
    "api_key": "",
    "conversation": [],
    "xp": 0,
    "streak": 0,
    "fc_index": 0,
    "fc_show_answer": False,
    "flashcard_decks": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────
# CLAUDE API HELPERS
# ─────────────────────────────────────────────
def ask_claude(prompt: str, max_tokens: int = 1000) -> str:
    try:
        client = anthropic.Anthropic(api_key=st.session_state.api_key)
        msg = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text
    except anthropic.AuthenticationError:
        st.error("❌ API Key inválida. Verifique na barra lateral.")
    except anthropic.RateLimitError:
        st.error("⚠️ Limite de requisições atingido. Aguarde alguns segundos.")
    except Exception as e:
        st.error(f"Erro na API: {e}")
    return ""

def ask_claude_chat(messages: list, system: str, max_tokens: int = 800) -> str:
    try:
        client = anthropic.Anthropic(api_key=st.session_state.api_key)
        msg = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            system=system,
            messages=messages,
        )
        return msg.content[0].text
    except anthropic.AuthenticationError:
        st.error("❌ API Key inválida. Verifique na barra lateral.")
    except anthropic.RateLimitError:
        st.error("⚠️ Limite de requisições atingido. Aguarde alguns segundos.")
    except Exception as e:
        st.error(f"Erro na API: {e}")
    return ""

# ─────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────
SAMPLE_SCENES = {
    "🦁 O Rei Leão — 'Remember who you are'": {
        "en": "You have forgotten who you are and so have forgotten me. Look inside yourself, Simba. You are more than what you have become. You must take your place in the Circle of Life.",
        "pt": "Você esqueceu quem você é e, por isso, me esqueceu também. Olhe dentro de si mesmo, Simba. Você é mais do que se tornou. Você deve assumir seu lugar no Ciclo da Vida.",
        "vocab": ["forgotten", "inside yourself", "Circle of Life", "become"],
        "level": "Intermediário",
        "tips": "Preste atenção nas contrações: 'you have' → 'you've'. Repita a fala do Mufasa com voz grave e pausada.",
    },
    "🕷️ Homem-Aranha — 'Great power, great responsibility'": {
        "en": "With great power comes great responsibility. This is my gift, my curse. Who am I? I'm Spider-Man.",
        "pt": "Com grande poder vem grande responsabilidade. Esse é meu dom, minha maldição. Quem sou eu? Sou o Homem-Aranha.",
        "vocab": ["responsibility", "gift", "curse"],
        "level": "Básico",
        "tips": "Frase curta e rítmica — ótima para shadowing. Repita 5x acelerando progressivamente.",
    },
    "🧙 Harry Potter — Plataforma 9¾": {
        "en": "It's the same every year, packed with Muggles of course. Come on. Platform nine and three-quarters this way! Not to worry. Not to worry.",
        "pt": "É a mesma coisa todo ano, cheio de Trouxas claro. Venha. Plataforma nove e três quartos por aqui! Não se preocupe. Não se preocupe.",
        "vocab": ["packed", "Muggles", "platform", "three-quarters"],
        "level": "Intermediário",
        "tips": "Note o sotaque britânico. 'Three-quarters' é pronunciado 'three-KWORters'.",
    },
    "🤖 Interestelar — Cooper e Murph": {
        "en": "We used to look up at the sky and wonder at our place in the stars. Now we just look down and worry about our place in the dirt.",
        "pt": "Costumávamos olhar para o céu e nos perguntar sobre nosso lugar nas estrelas. Agora apenas olhamos para baixo e nos preocupamos com nosso lugar na terra.",
        "vocab": ["wonder", "place in the stars", "dirt"],
        "level": "Avançado",
        "tips": "Fala poética e lenta. Imite o ritmo melancólico do Cooper. Bom para entonação.",
    },
    "🧠 Breaking Bad — 'I am the danger'": {
        "en": "I am not in danger, Skyler. I am the danger. A guy opens his door and gets shot, and you think that of me? No. I am the one who knocks.",
        "pt": "Eu não estou em perigo, Skyler. Eu sou o perigo. Um cara abre a porta e leva um tiro, e você pensa isso de mim? Não. Sou eu quem bate.",
        "vocab": ["danger", "opens his door", "the one who knocks"],
        "level": "Intermediário",
        "tips": "Fala icônica! Pratique a pausa dramática antes de 'I am the danger'. Walter White fala devagar e com intensidade.",
    },
}

PERSONAS = {
    "🎓 Prof. Alex — Paciente e didático": {
        "desc": "Explica erros com calma, dá exemplos práticos e foca na evolução gradual.",
        "system": "You are Professor Alex, a patient and didactic English teacher for Brazilian intermediate learners. Always respond in a mix: correct their English gently, then continue the conversation naturally. Use simple but real English. When the student makes mistakes, kindly point them out and show the correct form. Encourage them constantly. Keep responses concise (3-5 sentences max unless explaining grammar).",
    },
    "🎬 Sam — Cinéfilo entusiasmado": {
        "desc": "Adora filmes e séries, usa referências pop, conversa de forma casual e divertida.",
        "system": "You are Sam, an enthusiastic movie and series fan who teaches English through pop culture. You naturally reference movies, shows, quotes. Speak casually and naturally. When the student makes English mistakes, correct them smoothly by repeating their sentence correctly without making it awkward. Keep it fun and conversational. Max 4 sentences per reply.",
    },
    "💼 Jordan — Business English": {
        "desc": "Focado em inglês profissional, entrevistas, apresentações e e-mails corporativos.",
        "system": "You are Jordan, a business English coach. Focus on professional vocabulary, formal communication, job interviews, emails, and presentations. Help the student sound professional in English. Gently correct mistakes and suggest more professional alternatives. Keep responses practical and workplace-oriented.",
    },
    "🌍 Maya — Conversação livre": {
        "desc": "Papo informal sobre qualquer assunto, como uma amiga nativa.",
        "system": "You are Maya, a native English speaker having a casual conversation. Talk about anything the student brings up. Be natural, use contractions, slang occasionally, and speak like a real friend. Subtly model correct English when the student makes errors. Keep it light and engaging.",
    },
}

TOPIC_STARTERS = {
    "🎬 Filmes e séries": "Let's talk about movies and series! What's the last thing you watched? Did you enjoy it?",
    "✈️ Viagens": "I'd love to hear about travel! Have you ever traveled abroad, or is there a place you'd love to visit?",
    "🍕 Comida e cultura": "Food is such a fun topic! What's your favorite meal? Do you like trying different cuisines?",
    "💼 Trabalho e carreira": "Tell me about what you do for work! What are your career goals?",
    "🎮 Hobbies": "What do you do in your free time? Any hobbies or passions you'd like to share?",
    "🌍 Falar sobre si mesmo": "Let's start simple — tell me about yourself! Where are you from and what do you like?",
}

DEFAULT_DECKS = {
    "🎬 Cinema & Séries": [
        {"en": "plot twist", "pt": "reviravolta na trama", "example": "The plot twist at the end left everyone shocked.", "level": 0, "next_review": ""},
        {"en": "binge-watch", "pt": "maratonar (séries)", "example": "I binge-watched the entire season over the weekend.", "level": 0, "next_review": ""},
        {"en": "cliffhanger", "pt": "final suspenso/em aberto", "example": "The season finale ended on a cliffhanger!", "level": 0, "next_review": ""},
        {"en": "spoiler", "pt": "spoiler (revelar algo)", "example": "Don't spoil the movie for me!", "level": 0, "next_review": ""},
        {"en": "blockbuster", "pt": "grande sucesso de bilheteria", "example": "Avengers is a massive blockbuster.", "level": 0, "next_review": ""},
        {"en": "sequel", "pt": "continuação/sequência", "example": "The sequel was even better than the original.", "level": 0, "next_review": ""},
        {"en": "subtitles", "pt": "legendas", "example": "I always watch foreign films with subtitles.", "level": 0, "next_review": ""},
        {"en": "cast", "pt": "elenco", "example": "The cast of this series is incredible.", "level": 0, "next_review": ""},
    ],
    "💼 Inglês do Dia a Dia": [
        {"en": "hang out", "pt": "sair/ficar com amigos", "example": "Do you want to hang out this weekend?", "level": 0, "next_review": ""},
        {"en": "figure out", "pt": "descobrir/resolver", "example": "I can't figure out this problem.", "level": 0, "next_review": ""},
        {"en": "give up", "pt": "desistir", "example": "Don't give up on your dreams!", "level": 0, "next_review": ""},
        {"en": "look forward to", "pt": "estar ansioso por algo", "example": "I'm looking forward to the weekend.", "level": 0, "next_review": ""},
        {"en": "by the way", "pt": "a propósito / aliás", "example": "By the way, did you see that movie?", "level": 0, "next_review": ""},
        {"en": "make up your mind", "pt": "tomar uma decisão", "example": "You need to make up your mind!", "level": 0, "next_review": ""},
        {"en": "deal with", "pt": "lidar com", "example": "I have to deal with a lot of stress.", "level": 0, "next_review": ""},
        {"en": "catch up", "pt": "se atualizar / colocar o papo em dia", "example": "Let's catch up over coffee!", "level": 0, "next_review": ""},
    ],
    "🧠 Gramática Rápida": [
        {"en": "I used to + verb", "pt": "Eu costumava (passado habitual)", "example": "I used to watch cartoons every morning.", "level": 0, "next_review": ""},
        {"en": "I wish + past", "pt": "Queria que... (desejo irreal)", "example": "I wish I spoke perfect English.", "level": 0, "next_review": ""},
        {"en": "Have you ever...?", "pt": "Você já...? (present perfect)", "example": "Have you ever been to New York?", "level": 0, "next_review": ""},
        {"en": "used to vs. would", "pt": "hábito passado (used to = estado/ação; would = só ação)", "example": "I used to be shy. I would practice daily.", "level": 0, "next_review": ""},
    ],
}

INTERVAL_DAYS = [0, 1, 3, 7, 14, 30]

# Init flashcard decks
if st.session_state.flashcard_decks is None:
    st.session_state.flashcard_decks = {k: [dict(c) for c in v] for k, v in DEFAULT_DECKS.items()}

# ─────────────────────────────────────────────
# FLASHCARD HELPERS
# ─────────────────────────────────────────────
def get_due_cards(deck):
    today = datetime.date.today().isoformat()
    return [i for i, c in enumerate(deck) if not c.get("next_review") or c["next_review"] <= today]

def update_card_review(deck, idx, quality):
    level = deck[idx].get("level", 0)
    level = min(level + 1, len(INTERVAL_DAYS) - 1) if quality >= 3 else max(level - 1, 0)
    days = INTERVAL_DAYS[level]
    deck[idx]["level"] = level
    deck[idx]["next_review"] = (datetime.date.today() + datetime.timedelta(days=days)).isoformat()
    return deck

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 1rem 0;'>
        <div style='font-family: Syne, sans-serif; font-size: 1.6rem; font-weight: 800; color: #E8FF47;'>🎬 FluentAI</div>
        <div style='color: #7A7A8A; font-size: 0.85rem; margin-top: 4px;'>Seu professor de inglês com IA</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("⚡ XP", st.session_state.xp)
    with col2:
        st.metric("🔥 Streak", f"{st.session_state.streak}d")

    st.divider()
    st.markdown("**🔑 Anthropic API Key**")
    api_input = st.text_input("API Key", value=st.session_state.api_key, type="password",
                               placeholder="sk-ant-...", label_visibility="collapsed")
    if api_input:
        st.session_state.api_key = api_input
        st.success("✓ API Key salva")

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div style='padding: 1.5rem 0 0.5rem;'>
    <h1 style='font-size: 2rem; margin: 0;'>Aprenda Inglês com <span style='color: #E8FF47;'>IA + Cinema</span></h1>
    <p style='color: #7A7A8A; margin-top: 0.3rem;'>Método shadowing, conversação e flashcards — tudo em um só lugar</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🎬 Shadowing", "🤖 Conversação", "🃏 Flashcards", "📊 Progresso"])

# ═══════════════════════════════════════════════
# TAB 1 — SHADOWING
# ═══════════════════════════════════════════════
with tab1:
    st.markdown("<h2>🎬 Shadowing com Filmes & Séries</h2>", unsafe_allow_html=True)
    st.markdown("<p class='muted-text'>Escolha uma cena, leia em voz alta e receba feedback da IA.</p>", unsafe_allow_html=True)

    col_sel, col_info = st.columns([2, 1])
    with col_sel:
        scene_name = st.selectbox("Cena", list(SAMPLE_SCENES.keys()), label_visibility="collapsed")
    scene = SAMPLE_SCENES[scene_name]
    with col_info:
        lc = {"Básico": "#47CFFF", "Intermediário": "#E8FF47", "Avançado": "#FF6B6B"}.get(scene["level"], "#E8FF47")
        st.markdown(f"<div style='padding-top:0.5rem'><span style='background:{lc}22;color:{lc};border:1px solid {lc}55;border-radius:20px;padding:4px 14px;font-size:0.85rem;font-weight:600;'>{scene['level']}</span></div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class='card-accent' style='margin-top:1rem;'>
        <div style='font-size:0.75rem;color:#7A7A8A;letter-spacing:2px;text-transform:uppercase;margin-bottom:0.8rem;'>🇺🇸 Original</div>
        <div style='font-size:1.2rem;line-height:1.8;font-weight:500;color:#F0EFE9;'>"{scene['en']}"</div>
    </div>
    """, unsafe_allow_html=True)

    if st.checkbox("📖 Mostrar tradução"):
        st.markdown(f"""
        <div class='card' style='border-color:#47CFFF44;'>
            <div style='font-size:0.75rem;color:#47CFFF;letter-spacing:2px;text-transform:uppercase;margin-bottom:0.5rem;'>🇧🇷 Tradução</div>
            <div style='color:#B0B0C0;line-height:1.7;'>"{scene['pt']}"</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"<div style='margin:0.5rem 0 1rem;'><span style='font-size:0.8rem;color:#7A7A8A;'>📌 Vocabulário: </span>{''.join(f'<span class=tag>{w}</span>' for w in scene['vocab'])}</div>", unsafe_allow_html=True)
    st.info(f"💡 **Dica:** {scene['tips']}")

    st.markdown("---")
    st.markdown("### 🎙️ Pratique e receba feedback")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""<div class='card'><b style='color:#E8FF47;'>Como fazer:</b><br><br>
        <b>1.</b> Leia em voz alta<br><b>2.</b> Escreva abaixo<br><b>3.</b> Peça análise IA<br><b>4.</b> Repita 3–5x</div>""", unsafe_allow_html=True)
    with col_b:
        st.markdown("""<div class='card'><b style='color:#47CFFF;'>Por que funciona?</b><br><br>
        Ativa memória muscular vocal, treina ritmo e entonação — método favorito de poliglotas! 🧠</div>""", unsafe_allow_html=True)

    user_attempt = st.text_area("✍️ Escreva o que você falou ou sua versão da cena:",
                                 placeholder="Type here what you said...", height=120)
    feedback_type = st.radio("Tipo de análise:", ["🎯 Pronúncia e ritmo", "📝 Gramática", "💬 Vocabulário", "🌟 Análise completa"], horizontal=True)

    if st.button("🤖 Analisar com IA", use_container_width=True, key="shadow_analyze"):
        if not st.session_state.api_key:
            st.error("⚠️ Insira sua API Key na barra lateral.")
        elif not user_attempt.strip():
            st.warning("Escreva algo para analisar!")
        else:
            with st.spinner("Analisando..."):
                prompt = f"""You are an English teacher specialized in the shadowing method for Brazilian Portuguese speakers with intermediate English level.

The student practiced this scene: "{scene['en']}"
The student wrote/said: "{user_attempt}"
Analysis requested: {feedback_type}

Give feedback in Brazilian Portuguese (PT-BR), friendly and encouraging. Include:
1. What they did well
2. Specific pronunciation/grammar tips for this scene
3. One key phrase to focus on
4. Encouragement

Keep it concise and motivating."""
                response = ask_claude(prompt)
                if response:
                    st.markdown(f"""<div class='card' style='border-color:#47CFFF;margin-top:1rem;'>
                    <div style='color:#47CFFF;font-weight:700;margin-bottom:0.8rem;'>🤖 Feedback do Professor IA</div>
                    <div style='line-height:1.8;'>{response}</div></div>""", unsafe_allow_html=True)
                    st.session_state.xp += 15
                    st.success(f"🎉 +15 XP! Total: {st.session_state.xp} XP")

    st.markdown("---")
    with st.expander("➕ Adicionar cena personalizada"):
        c_title = st.text_input("Nome da cena")
        c_en = st.text_area("Texto em inglês", height=100, key="custom_en")
        c_pt = st.text_area("Tradução em português (opcional)", height=80, key="custom_pt")
        if st.button("💾 Salvar cena") and c_title and c_en:
            SAMPLE_SCENES[c_title] = {"en": c_en, "pt": c_pt, "vocab": [], "level": "Intermediário", "tips": "Pratique em voz alta!"}
            st.success("Cena salva!")

# ═══════════════════════════════════════════════
# TAB 2 — CONVERSAÇÃO
# ═══════════════════════════════════════════════
with tab2:
    st.markdown("<h2>🤖 Conversação com IA</h2>", unsafe_allow_html=True)
    st.markdown("<p class='muted-text'>Pratique inglês com um professor IA. Erros corrigidos naturalmente.</p>", unsafe_allow_html=True)

    col_p, col_t = st.columns(2)
    with col_p:
        st.markdown("**Escolha seu professor:**")
        persona_name = st.selectbox("Professor", list(PERSONAS.keys()), label_visibility="collapsed")
    with col_t:
        st.markdown("**Tema (opcional):**")
        topic = st.selectbox("Tema", ["💬 Livre"] + list(TOPIC_STARTERS.keys()), label_visibility="collapsed")

    persona = PERSONAS[persona_name]
    st.markdown(f"<div class='card'><span style='color:#E8FF47;font-weight:600;'>{persona_name}</span><br><span class='muted-text'>{persona['desc']}</span></div>", unsafe_allow_html=True)

    col_new, col_hint, col_lvl = st.columns(3)
    with col_new:
        if st.button("🔄 Nova conversa", use_container_width=True):
            st.session_state.conversation = []
            st.rerun()
    with col_hint:
        show_hint = st.button("💡 Ajuda", use_container_width=True)
    with col_lvl:
        correction_level = st.selectbox("Correção", ["🟡 Suave", "🔴 Detalhada", "🟢 Só elogios"], label_visibility="collapsed")

    # Auto-start with topic
    if not st.session_state.conversation and topic != "💬 Livre":
        starter = TOPIC_STARTERS.get(topic, "")
        if starter:
            st.session_state.conversation.append({"role": "assistant", "content": starter})

    if not st.session_state.conversation:
        st.markdown("""<div style='text-align:center;padding:2rem;color:#7A7A8A;'>
            <div style='font-size:2.5rem;margin-bottom:0.5rem;'>💬</div>
            <div>Comece escrevendo em inglês abaixo!</div>
            <div style='font-size:0.85rem;margin-top:0.5rem;'>Não tenha medo de errar — é assim que se aprende!</div>
        </div>""", unsafe_allow_html=True)
    else:
        for msg in st.session_state.conversation:
            if msg["role"] == "user":
                st.markdown(f"<div class='msg-user'><span style='font-size:0.75rem;color:#E8FF47;font-weight:600;'>VOCÊ</span><br>{msg['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='msg-ai'><span style='font-size:0.75rem;color:#47CFFF;font-weight:600;'>PROFESSOR IA</span><br>{msg['content']}</div>", unsafe_allow_html=True)

    if show_hint and st.session_state.api_key:
        hint = ask_claude_chat(
            [{"role": "user", "content": f"Give 3 simple English sentences the student could say next in a conversation about: {topic}. Include Portuguese translation for each. Be brief."}],
            persona["system"]
        )
        if hint:
            st.markdown(f"<div class='card' style='border-color:#E8FF47;'><b style='color:#E8FF47;'>💡 Sugestões:</b><br><br>{hint}</div>", unsafe_allow_html=True)

    correction_map = {
        "🟡 Suave": "Correct errors very subtly, mostly by modeling correct English naturally.",
        "🔴 Detalhada": "Explicitly point out grammar/vocabulary errors and explain the correct form in Portuguese.",
        "🟢 Só elogios": "Be very encouraging, only correct critical errors, celebrate every attempt.",
    }

    user_msg = st.text_area("Escreva em inglês:", placeholder="Type in English...", height=100, key="conv_input")

    col_send, col_tr = st.columns([2, 1])
    with col_send:
        send = st.button("📤 Enviar", use_container_width=True)
    with col_tr:
        translate = st.button("🇧🇷→🇺🇸 Traduzir", use_container_width=True)

    if translate and user_msg.strip() and st.session_state.api_key:
        with st.spinner("Traduzindo..."):
            tr = ask_claude_chat(
                [{"role": "user", "content": f"Translate to natural intermediate English: {user_msg}"}],
                "You are a translator. Return ONLY the English translation, nothing else."
            )
            if tr:
                st.info(f"🇺🇸 **{tr}**")

    if send and user_msg.strip():
        if not st.session_state.api_key:
            st.error("⚠️ Insira sua API Key na barra lateral.")
        else:
            st.session_state.conversation.append({"role": "user", "content": user_msg})
            system = f"{persona['system']}\n\nCorrection style: {correction_map.get(correction_level, '')}\n\nIMPORTANT: Always respond in English. If explaining grammar, add a brief note in Portuguese at the end."
            with st.spinner("Respondendo..."):
                response = ask_claude_chat(st.session_state.conversation, system)
                if response:
                    st.session_state.conversation.append({"role": "assistant", "content": response})
                    st.session_state.xp += 10
                    st.rerun()

    if st.session_state.conversation:
        u_msgs = [m for m in st.session_state.conversation if m["role"] == "user"]
        words = sum(len(m["content"].split()) for m in u_msgs)
        st.markdown(f"<div class='muted-text' style='margin-top:1rem;'>📊 {len(u_msgs)} mensagens · {words} palavras praticadas · +{len(u_msgs)*10} XP</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# TAB 3 — FLASHCARDS
# ═══════════════════════════════════════════════
with tab3:
    st.markdown("<h2>🃏 Flashcards com Revisão Espaçada</h2>", unsafe_allow_html=True)
    st.markdown("<p class='muted-text'>Memorize vocabulário com repetição espaçada científica (SRS).</p>", unsafe_allow_html=True)

    fc_tab1, fc_tab2, fc_tab3 = st.tabs(["📚 Estudar", "🗂️ Gerenciar", "✨ Gerar com IA"])

    with fc_tab1:
        col_dk, col_st = st.columns([2, 1])
        with col_dk:
            deck_name = st.selectbox("Baralho", list(st.session_state.flashcard_decks.keys()), label_visibility="collapsed")
        deck = st.session_state.flashcard_decks[deck_name]
        due = get_due_cards(deck)
        with col_st:
            st.markdown(f"<div style='padding:0.5rem 0;'><span style='color:#E8FF47;font-weight:700;font-size:1.2rem;'>{len(due)}</span> <span class='muted-text'>p/ revisar · </span><span style='color:#47CFFF;font-weight:700;'>{len(deck)}</span> <span class='muted-text'>total</span></div>", unsafe_allow_html=True)

        if not due:
            st.markdown("""<div style='text-align:center;padding:3rem;'>
                <div style='font-size:3rem;'>🎉</div>
                <h3 style='color:#E8FF47;'>Tudo em dia!</h3>
                <p class='muted-text'>Volte amanhã para revisar!</p>
            </div>""", unsafe_allow_html=True)
        else:
            if st.session_state.fc_index >= len(due):
                st.session_state.fc_index = 0

            card_idx = due[st.session_state.fc_index]
            card = deck[card_idx]
            level_labels = ["🌱 Novo", "🔵 Fácil", "🟡 Médio", "🟠 Difícil", "🟢 Dominado", "⭐ Expert"]
            lvl = card.get("level", 0)

            st.progress(st.session_state.fc_index / len(due))
            st.markdown(f"<div class='muted-text' style='text-align:right;'>{st.session_state.fc_index + 1} / {len(due)}</div>", unsafe_allow_html=True)

            st.markdown(f"""<div class='flashcard'>
                <div style='font-size:0.75rem;color:#7A7A8A;letter-spacing:2px;text-transform:uppercase;margin-bottom:1rem;'>🇺🇸 Inglês</div>
                <div style='font-size:2rem;font-family:Syne,sans-serif;font-weight:800;color:#E8FF47;margin-bottom:0.5rem;'>{card["en"]}</div>
                <div style='font-size:0.8rem;color:#7A7A8A;margin-top:0.5rem;'>{level_labels[min(lvl, len(level_labels)-1)]}</div>
            </div>""", unsafe_allow_html=True)

            if st.button("👁️ Ver resposta" if not st.session_state.fc_show_answer else "🙈 Esconder", use_container_width=True):
                st.session_state.fc_show_answer = not st.session_state.fc_show_answer
                st.rerun()

            if st.session_state.fc_show_answer:
                st.markdown(f"""<div class='card' style='text-align:center;border-color:#47CFFF;margin-top:0.5rem;'>
                    <div style='font-size:0.75rem;color:#47CFFF;letter-spacing:2px;text-transform:uppercase;margin-bottom:0.5rem;'>🇧🇷 Português</div>
                    <div style='font-size:1.4rem;font-weight:600;color:#F0EFE9;margin-bottom:0.8rem;'>{card["pt"]}</div>
                    <div style='font-size:0.85rem;color:#7A7A8A;font-style:italic;'>"{card["example"]}"</div>
                </div>""", unsafe_allow_html=True)

                st.markdown("**Quão bem você lembrou?**")
                rc1, rc2, rc3, rc4 = st.columns(4)
                for col, label, quality in [(rc1, "😰 Errei", 0), (rc2, "🤔 Difícil", 2), (rc3, "😊 Lembrei", 3), (rc4, "🚀 Fácil!", 5)]:
                    with col:
                        if st.button(label, use_container_width=True, key=f"rate_{quality}_{deck_name}"):
                            st.session_state.flashcard_decks[deck_name] = update_card_review(
                                st.session_state.flashcard_decks[deck_name], card_idx, quality
                            )
                            st.session_state.fc_index += 1
                            st.session_state.fc_show_answer = False
                            st.session_state.xp += (quality + 1) * 3
                            st.rerun()

    with fc_tab2:
        st.markdown("### ➕ Adicionar card")
        tgt = st.selectbox("Adicionar ao baralho:", list(st.session_state.flashcard_decks.keys()), key="add_to_deck")
        cn1, cn2 = st.columns(2)
        with cn1:
            new_en = st.text_input("Inglês")
        with cn2:
            new_pt = st.text_input("Português")
        new_ex = st.text_input("Exemplo (em inglês)")
        if st.button("💾 Adicionar") and new_en and new_pt:
            st.session_state.flashcard_decks[tgt].append({
                "en": new_en, "pt": new_pt,
                "example": new_ex or f"I use '{new_en}' in my daily life.",
                "level": 0, "next_review": ""
            })
            st.success(f"✅ '{new_en}' adicionado!")

        st.markdown("### 🗂️ Novo baralho")
        new_deck = st.text_input("Nome do baralho (ex: '🏖️ Viagens')")
        if st.button("Criar baralho") and new_deck:
            if new_deck not in st.session_state.flashcard_decks:
                st.session_state.flashcard_decks[new_deck] = []
                st.success(f"Baralho '{new_deck}' criado!")
            else:
                st.warning("Já existe!")

    with fc_tab3:
        st.markdown("### ✨ Gerar flashcards com IA")
        st.markdown("<p class='muted-text'>Descreva um tema e a IA cria cards personalizados.</p>", unsafe_allow_html=True)
        gen_topic = st.text_input("Tema:", placeholder="Ex: phrasal verbs com 'get', vocabulário de restaurante...")
        gen_qty = st.slider("Quantidade de cards:", 3, 15, 8)
        gen_level = st.select_slider("Nível:", ["Básico", "Intermediário", "Avançado"], value="Intermediário")
        gen_deck = st.selectbox("Adicionar ao baralho:", list(st.session_state.flashcard_decks.keys()), key="gen_deck")

        if st.button("🤖 Gerar Flashcards", use_container_width=True):
            if not st.session_state.api_key:
                st.error("Insira sua API Key!")
            elif not gen_topic.strip():
                st.warning("Descreva um tema!")
            else:
                with st.spinner(f"Gerando {gen_qty} flashcards..."):
                    prompt = f"""Create {gen_qty} English flashcards for a Brazilian Portuguese speaker at {gen_level} level about: {gen_topic}

Return ONLY a valid JSON array, no markdown, no extra text:
[{{"en": "expression", "pt": "tradução", "example": "Example sentence."}}]"""
                    response = ask_claude(prompt)
                    if response:
                        try:
                            json_match = re.search(r'\[.*\]', response, re.DOTALL)
                            if json_match:
                                cards_data = json.loads(json_match.group())
                                added = 0
                                for c in cards_data:
                                    if "en" in c and "pt" in c:
                                        st.session_state.flashcard_decks[gen_deck].append({
                                            "en": c["en"], "pt": c["pt"],
                                            "example": c.get("example", f"Example with {c['en']}."),
                                            "level": 0, "next_review": ""
                                        })
                                        added += 1
                                st.success(f"✅ {added} cards adicionados a '{gen_deck}'!")
                                st.session_state.xp += added * 5
                                st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao processar. Tente novamente. ({e})")

# ═══════════════════════════════════════════════
# TAB 4 — PROGRESSO
# ═══════════════════════════════════════════════
with tab4:
    st.markdown("<h2>📊 Seu Progresso</h2>", unsafe_allow_html=True)

    xp = st.session_state.xp
    level = xp // 100 + 1
    xp_in_level = xp % 100
    level_names = ["Iniciante", "Explorador", "Estudante", "Comunicador", "Fluente", "Expert", "Mestre"]
    level_name = level_names[min(level - 1, len(level_names) - 1)]

    mc1, mc2, mc3, mc4 = st.columns(4)
    with mc1: st.metric("⚡ XP Total", xp)
    with mc2: st.metric("🏅 Nível", f"{level} — {level_name}")
    with mc3: st.metric("🔥 Sequência", f"{st.session_state.streak} dias")
    with mc4:
        total_cards = sum(len(v) for v in st.session_state.flashcard_decks.values())
        st.metric("🃏 Cards", total_cards)

    st.markdown(f"""<div class='card' style='margin-top:1rem;'>
        <div style='display:flex;justify-content:space-between;margin-bottom:0.5rem;'>
            <span style='color:#E8FF47;font-weight:700;'>Nível {level}: {level_name}</span>
            <span class='muted-text'>{xp_in_level}/100 XP</span>
        </div>
    </div>""", unsafe_allow_html=True)
    st.progress(xp_in_level / 100)

    st.markdown("---")
    st.markdown("### 🃏 Status dos Flashcards")
    for dn, cards in st.session_state.flashcard_decks.items():
        today = datetime.date.today().isoformat()
        due_n = sum(1 for c in cards if not c.get("next_review") or c["next_review"] <= today)
        mastered = sum(1 for c in cards if c.get("level", 0) >= 4)
        total = len(cards)
        pc1, pc2, pc3, pc4 = st.columns([3, 1, 1, 1])
        with pc1: st.markdown(f"**{dn}**")
        with pc2:
            color = "#FF6B6B" if due_n > 0 else "#47CFFF"
            st.markdown(f"<span style='color:{color};font-weight:700;'>{due_n}</span> <span class='muted-text'>revisar</span>", unsafe_allow_html=True)
        with pc3: st.markdown(f"<span style='color:#E8FF47;font-weight:700;'>{mastered}</span> <span class='muted-text'>dominou</span>", unsafe_allow_html=True)
        with pc4: st.markdown(f"<span class='muted-text'>{total} total</span>", unsafe_allow_html=True)
        if total > 0:
            st.progress(mastered / total)

    st.markdown("---")
    st.markdown("### 💡 Dicas para evoluir mais rápido")
    for icon, title, desc in [
        ("🎬", "Shadowing diário", "15–20 min/dia é mais eficaz que 2h no fim de semana."),
        ("🃏", "Revisão espaçada", "Revise os cards no horário certo — o intervalo é calculado cientificamente."),
        ("💬", "Conversação sem medo", "Errar faz parte. O professor IA corrige com gentileza!"),
        ("📺", "Assistir com legendas", "PT → EN → sem legenda. Um episódio por dia já faz diferença."),
    ]:
        st.markdown(f"""<div class='card' style='display:flex;gap:1rem;align-items:flex-start;'>
            <div style='font-size:1.8rem;'>{icon}</div>
            <div><div style='font-weight:700;color:#F0EFE9;'>{title}</div><div class='muted-text'>{desc}</div></div>
        </div>""", unsafe_allow_html=True)

    with st.expander("⚙️ Configurações"):
        sc1, sc2 = st.columns(2)
        with sc1:
            if st.button("🔄 Resetar XP"):
                st.session_state.xp = 0
                st.session_state.streak = 0
                st.rerun()
        with sc2:
            bonus = st.number_input("XP manual:", min_value=0, max_value=500, value=0, step=10)
            if st.button("➕ Adicionar XP") and bonus > 0:
                st.session_state.xp += bonus
                st.rerun()
