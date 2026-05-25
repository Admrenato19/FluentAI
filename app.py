import streamlit as st

st.set_page_config(
    page_title="FluentAI - Aprenda Inglês",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject global CSS
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

.stApp {
    background-color: var(--bg);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * {
    color: var(--text) !important;
}

/* Hide Streamlit branding */
#MainMenu, footer, header {visibility: hidden;}

/* Buttons */
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

/* Inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background-color: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
}

/* Cards */
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

/* Typography */
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

/* Chat bubbles */
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

/* Flashcard */
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

/* Progress bar */
.stProgress > div > div > div {
    background-color: var(--accent) !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem;
}
[data-testid="stMetricValue"] { color: var(--accent) !important; font-family: 'Syne', sans-serif !important; }

/* Tabs */
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

.stRadio > div { gap: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# Session state defaults
defaults = {
    "api_key": "",
    "conversation": [],
    "flashcards": [],
    "flashcard_index": 0,
    "show_answer": False,
    "xp": 0,
    "streak": 0,
    "studied_today": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style='padding: 1rem 0;'>
        <div style='font-family: Syne, sans-serif; font-size: 1.6rem; font-weight: 800; color: #E8FF47;'>
            🎬 FluentAI
        </div>
        <div style='color: #7A7A8A; font-size: 0.85rem; margin-top: 4px;'>Seu professor de inglês com IA</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # XP and streak
    col1, col2 = st.columns(2)
    with col1:
        st.metric("⚡ XP", st.session_state.xp)
    with col2:
        st.metric("🔥 Sequência", f"{st.session_state.streak}d")

    st.divider()

    # API Key
    st.markdown("**🔑 API Key**")
    api_key_input = st.text_input(
        "Anthropic API Key",
        value=st.session_state.api_key,
        type="password",
        placeholder="sk-ant-...",
        label_visibility="collapsed",
    )
    if api_key_input:
        st.session_state.api_key = api_key_input
        st.success("✓ API Key salva")

    st.divider()
    st.markdown("<div class='muted-text'>Navegue pelas abas acima para acessar cada funcionalidade.</div>", unsafe_allow_html=True)

# Main navigation
st.markdown("""
<div style='padding: 1.5rem 0 0.5rem;'>
    <h1 style='font-size: 2rem; margin: 0;'>Aprenda Inglês com <span style='color: #E8FF47;'>IA + Cinema</span></h1>
    <p style='color: #7A7A8A; margin-top: 0.3rem;'>Método shadowing, conversação e flashcards — tudo em um só lugar</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🎬 Shadowing", "🤖 Conversação", "🃏 Flashcards", "📊 Progresso"])

# ─── TAB 1: SHADOWING ───────────────────────────────────────────────────────
with tab1:
    from pages.shadowing import render_shadowing
    render_shadowing()

# ─── TAB 2: CONVERSAÇÃO ─────────────────────────────────────────────────────
with tab2:
    from pages.conversation import render_conversation
    render_conversation()

# ─── TAB 3: FLASHCARDS ──────────────────────────────────────────────────────
with tab3:
    from pages.flashcards import render_flashcards
    render_flashcards()

# ─── TAB 4: PROGRESSO ───────────────────────────────────────────────────────
with tab4:
    from pages.progress import render_progress
    render_progress()
