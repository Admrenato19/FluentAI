import streamlit as st
import anthropic
import json
import re
import datetime
import base64

st.set_page_config(
    page_title="FluentAI - Aprenda Inglês",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');
:root {
    --bg:#0D0D0F; --surface:#16161A; --surface2:#1E1E24;
    --accent:#E8FF47; --accent2:#FF6B6B; --accent3:#47CFFF;
    --text:#F0EFE9; --muted:#7A7A8A; --border:#2A2A35; --radius:16px;
}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;background-color:var(--bg);color:var(--text);}
.stApp{background-color:var(--bg);}
[data-testid="stSidebar"]{background-color:var(--surface)!important;border-right:1px solid var(--border);}
[data-testid="stSidebar"] *{color:var(--text)!important;}
#MainMenu,footer,header{visibility:hidden;}
.stButton>button{background:var(--accent)!important;color:var(--bg)!important;border:none!important;border-radius:8px!important;font-family:'Syne',sans-serif!important;font-weight:700!important;padding:0.6rem 1.5rem!important;transition:all 0.2s ease!important;}
.stButton>button:hover{transform:translateY(-2px);box-shadow:0 6px 20px rgba(232,255,71,0.3)!important;}
.stTextInput>div>div>input,.stTextArea>div>div>textarea,.stSelectbox>div>div{background-color:var(--surface2)!important;border:1px solid var(--border)!important;border-radius:10px!important;color:var(--text)!important;}
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:1.5rem;margin-bottom:1rem;transition:border-color 0.2s ease;}
.card:hover{border-color:var(--accent);}
.card-accent{background:linear-gradient(135deg,#1a1a20 0%,#1e1e2a 100%);border:1px solid var(--accent);border-radius:var(--radius);padding:1.5rem;margin-bottom:1rem;}
h1,h2,h3{font-family:'Syne',sans-serif!important;font-weight:800!important;color:var(--text)!important;}
.muted-text{color:var(--muted);font-size:0.9rem;}
.tag{display:inline-block;background:var(--surface2);border:1px solid var(--border);border-radius:20px;padding:3px 12px;font-size:0.8rem;color:var(--muted);margin:2px;}
.msg-user{background:var(--surface2);border-radius:16px 16px 4px 16px;padding:1rem 1.2rem;margin:0.5rem 0;border-left:3px solid var(--accent);max-width:85%;margin-left:auto;}
.msg-ai{background:var(--surface);border-radius:16px 16px 16px 4px;padding:1rem 1.2rem;margin:0.5rem 0;border-left:3px solid var(--accent3);max-width:85%;}
.flashcard{background:linear-gradient(145deg,var(--surface),var(--surface2));border:2px solid var(--accent);border-radius:20px;padding:3rem 2rem;text-align:center;min-height:200px;display:flex;flex-direction:column;align-items:center;justify-content:center;transition:all 0.3s ease;}
.flashcard:hover{transform:scale(1.01);box-shadow:0 10px 40px rgba(232,255,71,0.15);}
.stProgress>div>div>div{background-color:var(--accent)!important;}
[data-testid="stMetric"]{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:1rem;}
[data-testid="stMetricValue"]{color:var(--accent)!important;font-family:'Syne',sans-serif!important;}
.stTabs [data-baseweb="tab-list"]{background:var(--surface)!important;border-radius:10px!important;gap:4px;}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:var(--muted)!important;border-radius:8px!important;}
.stTabs [aria-selected="true"]{background:var(--accent)!important;color:var(--bg)!important;font-weight:600!important;}
.rec-btn{background:#FF6B6B!important;animation:pulse 1.5s infinite;}
@keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(255,107,107,0.4);}50%{box-shadow:0 0 0 8px rgba(255,107,107,0);}}
iframe{border-radius:12px;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# WEB SPEECH API — TTS + STT component
# ─────────────────────────────────────────────────────────────────
TTS_COMPONENT = """
<div id="tts-root" style="display:none;">
  <audio id="tts-audio" style="display:none;"></audio>
</div>
<script>
function fluentSpeak(text, lang='en-US', rate=0.9, pitch=1.0) {
  if (!('speechSynthesis' in window)) return;
  window.speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.lang = lang; u.rate = rate; u.pitch = pitch;
  const voices = window.speechSynthesis.getVoices();
  const preferred = voices.find(v => v.lang.startsWith('en') && (v.name.includes('Google') || v.name.includes('Natural')));
  if (preferred) u.voice = preferred;
  window.speechSynthesis.speak(u);
}
window.fluentSpeak = fluentSpeak;
</script>
"""

def tts_button_html(text: str, label: str = "🔊 Ouvir", rate: float = 0.85) -> str:
    safe = text.replace("'", "\\'").replace("\n", " ")
    return f"""
<button onclick="fluentSpeak('{safe}', 'en-US', {rate})"
  style="background:#E8FF47;color:#0D0D0F;border:none;border-radius:8px;
  padding:8px 18px;font-weight:700;cursor:pointer;font-size:0.9rem;
  font-family:Syne,sans-serif;transition:all 0.2s;">
  {label}
</button>
"""

STT_COMPONENT = """
<div style="display:flex;flex-direction:column;gap:12px;">
  <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
    <button id="btn-start" onclick="startRec()"
      style="background:#E8FF47;color:#0D0D0F;border:none;border-radius:8px;
      padding:10px 20px;font-weight:700;cursor:pointer;font-family:Syne,sans-serif;">
      🎙️ Gravar
    </button>
    <button id="btn-stop" onclick="stopRec()" disabled
      style="background:#FF6B6B;color:#fff;border:none;border-radius:8px;
      padding:10px 20px;font-weight:700;cursor:pointer;font-family:Syne,sans-serif;opacity:0.4;">
      ⏹ Parar
    </button>
    <span id="rec-status" style="color:#7A7A8A;font-size:0.85rem;">Clique em Gravar e fale em inglês</span>
  </div>
  <div id="rec-output" style="background:#1E1E24;border:1px solid #2A2A35;border-radius:12px;
    padding:1rem;min-height:60px;color:#F0EFE9;font-size:1rem;line-height:1.6;"></div>
  <button onclick="sendToAnalysis()"
    style="background:#47CFFF;color:#0D0D0F;border:none;border-radius:8px;
    padding:10px 20px;font-weight:700;cursor:pointer;font-family:Syne,sans-serif;display:none;"
    id="btn-analyze">
    🤖 Analisar com IA
  </button>
</div>

<script>
let recognition = null;
let finalText = '';

function startRec() {
  const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRec) {
    document.getElementById('rec-status').innerText = '❌ Seu browser não suporta gravação. Use Chrome.';
    return;
  }
  recognition = new SpeechRec();
  recognition.lang = 'en-US';
  recognition.interimResults = true;
  recognition.continuous = true;
  finalText = '';

  recognition.onstart = () => {
    document.getElementById('btn-start').disabled = true;
    document.getElementById('btn-stop').disabled = false;
    document.getElementById('btn-stop').style.opacity = '1';
    document.getElementById('rec-status').innerHTML = '<span style="color:#FF6B6B;">● Gravando...</span>';
    document.getElementById('rec-output').innerText = '';
    document.getElementById('btn-analyze').style.display = 'none';
  };

  recognition.onresult = (e) => {
    let interim = '';
    for (let i = e.resultIndex; i < e.results.length; i++) {
      if (e.results[i].isFinal) finalText += e.results[i][0].transcript + ' ';
      else interim += e.results[i][0].transcript;
    }
    document.getElementById('rec-output').innerText = finalText + interim;
  };

  recognition.onend = () => {
    document.getElementById('btn-start').disabled = false;
    document.getElementById('btn-stop').disabled = true;
    document.getElementById('btn-stop').style.opacity = '0.4';
    document.getElementById('rec-status').innerText = 'Gravação encerrada.';
    if (finalText.trim()) {
      document.getElementById('btn-analyze').style.display = 'block';
    }
  };

  recognition.onerror = (e) => {
    document.getElementById('rec-status').innerText = '❌ Erro: ' + e.error;
  };

  recognition.start();
}

function stopRec() {
  if (recognition) recognition.stop();
}

function sendToAnalysis() {
  const text = finalText.trim();
  if (!text) return;
  const encoded = encodeURIComponent(text);
  window.parent.postMessage({type:'stt_result', text}, '*');
  const el = document.getElementById('rec-status');
  el.innerText = '✅ Texto capturado! Cole no campo de análise acima.';
  navigator.clipboard.writeText(text).catch(()=>{});
  document.getElementById('rec-output').style.border = '1px solid #E8FF47';
}
</script>
"""

# ─────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────
for k, v in {
    "api_key": "", "conversation": [], "xp": 0, "streak": 0,
    "fc_index": 0, "fc_show_answer": False, "flashcard_decks": None,
    "yt_transcript": [], "yt_video_id": "", "tts_enabled": True,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────────
# CLAUDE API
# ─────────────────────────────────────────────────────────────────
def ask_claude(prompt: str, max_tokens: int = 1000) -> str:
    try:
        client = anthropic.Anthropic(api_key=st.session_state.api_key)
        msg = client.messages.create(
            model="claude-sonnet-4-20250514", max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text
    except anthropic.AuthenticationError:
        st.error("❌ API Key inválida.")
    except anthropic.RateLimitError:
        st.error("⚠️ Rate limit. Aguarde alguns segundos.")
    except Exception as e:
        st.error(f"Erro: {e}")
    return ""

def ask_claude_chat(messages: list, system: str, max_tokens: int = 800) -> str:
    try:
        client = anthropic.Anthropic(api_key=st.session_state.api_key)
        msg = client.messages.create(
            model="claude-sonnet-4-20250514", max_tokens=max_tokens,
            system=system, messages=messages,
        )
        return msg.content[0].text
    except anthropic.AuthenticationError:
        st.error("❌ API Key inválida.")
    except anthropic.RateLimitError:
        st.error("⚠️ Rate limit. Aguarde alguns segundos.")
    except Exception as e:
        st.error(f"Erro: {e}")
    return ""

# ─────────────────────────────────────────────────────────────────
# YOUTUBE HELPERS
# ─────────────────────────────────────────────────────────────────
def extract_video_id(url: str) -> str:
    for pattern in [r'v=([^&\s]+)', r'youtu\.be/([^?\s]+)', r'embed/([^?\s]+)']:
        m = re.search(pattern, url)
        if m:
            return m.group(1)
    return ""

def get_transcript(video_id: str) -> list:
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        ytt = YouTubeTranscriptApi()
        transcript = ytt.fetch(video_id)
        return [{"text": s.text, "start": s.start, "duration": s.duration} for s in transcript]
    except Exception as e:
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            ytt = YouTubeTranscriptApi()
            transcript_list = ytt.list(video_id)
            for t in transcript_list:
                fetched = t.fetch()
                return [{"text": s.text, "start": s.start, "duration": s.duration} for s in fetched]
        except Exception as e2:
            st.error(f"Não foi possível obter legendas: {e2}")
            return []

def transcript_to_text(transcript: list, max_chars: int = 3000) -> str:
    full = " ".join(s["text"].replace("\n", " ") for s in transcript)
    return full[:max_chars] + ("..." if len(full) > max_chars else "")

def transcript_to_segments(transcript: list, chunk_size: int = 5) -> list:
    """Group transcript into readable chunks of N entries."""
    chunks = []
    for i in range(0, len(transcript), chunk_size):
        group = transcript[i:i+chunk_size]
        text = " ".join(s["text"].replace("\n", " ") for s in group)
        start = group[0]["start"]
        chunks.append({"text": text, "start": int(start)})
    return chunks

# ─────────────────────────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────────────────────────
SAMPLE_SCENES = {
    "🦁 O Rei Leão — 'Remember who you are'": {
        "en": "You have forgotten who you are and so have forgotten me. Look inside yourself, Simba. You are more than what you have become. You must take your place in the Circle of Life.",
        "pt": "Você esqueceu quem você é e, por isso, me esqueceu também. Olhe dentro de si mesmo, Simba. Você é mais do que se tornou. Você deve assumir seu lugar no Ciclo da Vida.",
        "vocab": ["forgotten", "inside yourself", "Circle of Life", "become"],
        "level": "Intermediário",
        "tips": "Contrações: 'you have' → 'you've'. Repita com voz grave e pausada.",
    },
    "🕷️ Homem-Aranha — 'Great power'": {
        "en": "With great power comes great responsibility. This is my gift, my curse. Who am I? I'm Spider-Man.",
        "pt": "Com grande poder vem grande responsabilidade. Esse é meu dom, minha maldição. Quem sou eu? Sou o Homem-Aranha.",
        "vocab": ["responsibility", "gift", "curse"],
        "level": "Básico",
        "tips": "Frase curta e rítmica. Repita 5x acelerando progressivamente.",
    },
    "🧙 Harry Potter — Plataforma 9¾": {
        "en": "It's the same every year, packed with Muggles of course. Come on. Platform nine and three-quarters this way! Not to worry. Not to worry.",
        "pt": "É a mesma coisa todo ano, cheio de Trouxas. Venha. Plataforma nove e três quartos por aqui! Não se preocupe.",
        "vocab": ["packed", "Muggles", "platform", "three-quarters"],
        "level": "Intermediário",
        "tips": "Sotaque britânico. 'Three-quarters' → 'three-KWORters'.",
    },
    "🤖 Interestelar — Cooper": {
        "en": "We used to look up at the sky and wonder at our place in the stars. Now we just look down and worry about our place in the dirt.",
        "pt": "Costumávamos olhar para o céu e nos perguntar sobre nosso lugar nas estrelas. Agora apenas olhamos para baixo.",
        "vocab": ["wonder", "place in the stars", "dirt"],
        "level": "Avançado",
        "tips": "Fala poética e lenta. Imite o ritmo melancólico do Cooper.",
    },
    "🧠 Breaking Bad — 'I am the danger'": {
        "en": "I am not in danger, Skyler. I am the danger. A guy opens his door and gets shot, and you think that of me? No. I am the one who knocks.",
        "pt": "Eu não estou em perigo, Skyler. Eu sou o perigo. Um cara abre a porta e leva um tiro, e você pensa isso de mim? Não.",
        "vocab": ["danger", "opens his door", "the one who knocks"],
        "level": "Intermediário",
        "tips": "Pause dramática antes de 'I am the danger'. Fale devagar e com intensidade.",
    },
}

PERSONAS = {
    "🎓 Prof. Alex — Paciente": {
        "desc": "Didático, explica erros com calma e foca na evolução gradual.",
        "system": "You are Professor Alex, a patient English teacher for Brazilian intermediate learners. Correct errors gently, continue the conversation naturally. Keep responses concise (3-5 sentences).",
        "voice_rate": 0.8,
    },
    "🎬 Sam — Cinéfilo": {
        "desc": "Usa referências de filmes e séries, conversa casual e divertida.",
        "system": "You are Sam, a movie fan who teaches English through pop culture. Reference movies and shows naturally. Correct mistakes smoothly. Max 4 sentences.",
        "voice_rate": 0.9,
    },
    "💼 Jordan — Business": {
        "desc": "Inglês profissional, entrevistas e e-mails corporativos.",
        "system": "You are Jordan, a business English coach. Focus on professional vocabulary and communication. Keep responses practical.",
        "voice_rate": 0.85,
    },
    "🌍 Maya — Conversação livre": {
        "desc": "Papo informal, como uma amiga nativa.",
        "system": "You are Maya, a native English speaker having a casual conversation. Be natural, use contractions and occasional slang. Model correct English subtly.",
        "voice_rate": 0.95,
    },
}

TOPIC_STARTERS = {
    "🎬 Filmes e séries": "Let's talk about movies and series! What's the last thing you watched?",
    "✈️ Viagens": "Have you ever traveled abroad, or is there a place you'd love to visit?",
    "🍕 Comida": "What's your favorite meal? Do you like trying different cuisines?",
    "💼 Trabalho": "Tell me about what you do for work! What are your career goals?",
    "🎮 Hobbies": "What do you do in your free time? Any hobbies you'd like to share?",
}

DEFAULT_DECKS = {
    "🎬 Cinema & Séries": [
        {"en":"plot twist","pt":"reviravolta na trama","example":"The plot twist at the end left everyone shocked.","level":0,"next_review":""},
        {"en":"binge-watch","pt":"maratonar séries","example":"I binge-watched the entire season over the weekend.","level":0,"next_review":""},
        {"en":"cliffhanger","pt":"final suspenso/em aberto","example":"The season finale ended on a cliffhanger!","level":0,"next_review":""},
        {"en":"spoiler","pt":"revelar algo do enredo","example":"Don't spoil the movie for me!","level":0,"next_review":""},
        {"en":"blockbuster","pt":"grande sucesso de bilheteria","example":"Avengers is a massive blockbuster.","level":0,"next_review":""},
        {"en":"sequel","pt":"continuação/sequência","example":"The sequel was even better than the original.","level":0,"next_review":""},
        {"en":"subtitles","pt":"legendas","example":"I always watch foreign films with subtitles.","level":0,"next_review":""},
        {"en":"cast","pt":"elenco","example":"The cast of this series is incredible.","level":0,"next_review":""},
    ],
    "💼 Dia a Dia": [
        {"en":"hang out","pt":"sair com amigos","example":"Do you want to hang out this weekend?","level":0,"next_review":""},
        {"en":"figure out","pt":"descobrir/resolver","example":"I can't figure out this problem.","level":0,"next_review":""},
        {"en":"give up","pt":"desistir","example":"Don't give up on your dreams!","level":0,"next_review":""},
        {"en":"look forward to","pt":"estar ansioso por","example":"I'm looking forward to the weekend.","level":0,"next_review":""},
        {"en":"by the way","pt":"a propósito","example":"By the way, did you see that movie?","level":0,"next_review":""},
        {"en":"deal with","pt":"lidar com","example":"I have to deal with a lot of stress.","level":0,"next_review":""},
        {"en":"catch up","pt":"colocar o papo em dia","example":"Let's catch up over coffee!","level":0,"next_review":""},
    ],
    "🧠 Gramática": [
        {"en":"I used to + verb","pt":"Eu costumava (passado habitual)","example":"I used to watch cartoons every morning.","level":0,"next_review":""},
        {"en":"I wish + past","pt":"Queria que... (desejo irreal)","example":"I wish I spoke perfect English.","level":0,"next_review":""},
        {"en":"Have you ever...?","pt":"Você já...? (present perfect)","example":"Have you ever been to New York?","level":0,"next_review":""},
    ],
}
INTERVAL_DAYS = [0, 1, 3, 7, 14, 30]

if st.session_state.flashcard_decks is None:
    st.session_state.flashcard_decks = {k: [dict(c) for c in v] for k, v in DEFAULT_DECKS.items()}

def get_due_cards(deck):
    today = datetime.date.today().isoformat()
    return [i for i, c in enumerate(deck) if not c.get("next_review") or c["next_review"] <= today]

def update_card_review(deck, idx, quality):
    level = deck[idx].get("level", 0)
    level = min(level + 1, len(INTERVAL_DAYS) - 1) if quality >= 3 else max(level - 1, 0)
    deck[idx]["level"] = level
    deck[idx]["next_review"] = (datetime.date.today() + datetime.timedelta(days=INTERVAL_DAYS[level])).isoformat()
    return deck

# ─────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:1rem 0;'>
      <div style='font-family:Syne,sans-serif;font-size:1.6rem;font-weight:800;color:#E8FF47;'>🎬 FluentAI</div>
      <div style='color:#7A7A8A;font-size:0.85rem;margin-top:4px;'>Inglês com IA + Cinema</div>
    </div>""", unsafe_allow_html=True)
    st.divider()
    c1, c2 = st.columns(2)
    with c1: st.metric("⚡ XP", st.session_state.xp)
    with c2: st.metric("🔥 Streak", f"{st.session_state.streak}d")
    st.divider()
    st.markdown("**🔑 Anthropic API Key**")
    api_in = st.text_input("Key", value=st.session_state.api_key, type="password",
                            placeholder="sk-ant-...", label_visibility="collapsed")
    if api_in:
        st.session_state.api_key = api_in
        st.success("✓ Salva")
    st.divider()
    st.session_state.tts_enabled = st.toggle("🔊 Professor fala (TTS)", value=st.session_state.tts_enabled)
    st.markdown("<div class='muted-text'>TTS usa Web Speech API do browser — Chrome recomendado.</div>", unsafe_allow_html=True)

# Inject TTS engine once
st.components.v1.html(TTS_COMPONENT, height=0)

# ─────────────────────────────────────────────────────────────────
# HEADER + TABS
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<div style='padding:1.5rem 0 0.5rem;'>
  <h1 style='font-size:2rem;margin:0;'>Inglês com <span style='color:#E8FF47;'>IA + Cinema</span></h1>
  <p style='color:#7A7A8A;margin-top:0.3rem;'>Shadowing, YouTube, conversação com voz e flashcards</p>
</div>""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎬 Shadowing", "▶️ YouTube", "🤖 Conversação", "🃏 Flashcards", "📊 Progresso"])

# ═══════════════════════════════════════════════════════════════
# TAB 1 — SHADOWING (cenas pré-definidas)
# ═══════════════════════════════════════════════════════════════
with tab1:
    st.markdown("<h2>🎬 Shadowing com Filmes & Séries</h2>", unsafe_allow_html=True)
    st.markdown("<p class='muted-text'>Ouça a cena, repita em voz alta e receba feedback da IA.</p>", unsafe_allow_html=True)

    col_sel, col_info = st.columns([2, 1])
    with col_sel:
        scene_name = st.selectbox("Cena", list(SAMPLE_SCENES.keys()), label_visibility="collapsed")
    scene = SAMPLE_SCENES[scene_name]
    with col_info:
        lc = {"Básico":"#47CFFF","Intermediário":"#E8FF47","Avançado":"#FF6B6B"}.get(scene["level"],"#E8FF47")
        st.markdown(f"<div style='padding-top:0.5rem'><span style='background:{lc}22;color:{lc};border:1px solid {lc}55;border-radius:20px;padding:4px 14px;font-size:0.85rem;font-weight:600;'>{scene['level']}</span></div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class='card-accent' style='margin-top:1rem;'>
      <div style='font-size:0.75rem;color:#7A7A8A;letter-spacing:2px;text-transform:uppercase;margin-bottom:0.8rem;'>🇺🇸 Original</div>
      <div style='font-size:1.15rem;line-height:1.9;font-weight:500;color:#F0EFE9;'>"{scene['en']}"</div>
    </div>""", unsafe_allow_html=True)

    col_tts, col_slow = st.columns([1, 1])
    with col_tts:
        st.markdown(tts_button_html(scene["en"], "🔊 Ouvir (velocidade normal)", rate=0.9), unsafe_allow_html=True)
    with col_slow:
        st.markdown(tts_button_html(scene["en"], "🐢 Ouvir devagar", rate=0.6), unsafe_allow_html=True)

    if st.checkbox("📖 Mostrar tradução"):
        st.markdown(f"""
        <div class='card' style='border-color:#47CFFF44;'>
          <div style='font-size:0.75rem;color:#47CFFF;letter-spacing:2px;text-transform:uppercase;margin-bottom:0.5rem;'>🇧🇷 Tradução</div>
          <div style='color:#B0B0C0;line-height:1.7;'>"{scene['pt']}"</div>
        </div>""", unsafe_allow_html=True)

    st.markdown(f"<div style='margin:0.5rem 0 1rem;'><span style='font-size:0.8rem;color:#7A7A8A;'>📌 Vocabulário: </span>{''.join(f'<span class=tag>{w}</span>' for w in scene['vocab'])}</div>", unsafe_allow_html=True)
    st.info(f"💡 **Dica:** {scene['tips']}")

    st.markdown("---")
    st.markdown("### 🎙️ Sua vez — fale e receba feedback")

    stt_tab, text_tab = st.tabs(["🎙️ Gravar voz", "✍️ Digitar"])

    with stt_tab:
        st.markdown("<p class='muted-text'>Clique em Gravar, fale a cena em inglês, depois clique em Analisar.</p>", unsafe_allow_html=True)
        st.components.v1.html(STT_COMPONENT, height=200)
        st.markdown("<div class='muted-text' style='margin-top:0.5rem;'>💡 O texto reconhecido aparece acima. Copie e cole no campo abaixo para analisar.</div>", unsafe_allow_html=True)
        voice_text = st.text_area("Texto capturado pela voz:", placeholder="Cole aqui o que foi reconhecido...", height=80, key="voice_paste_shadow")
        if st.button("🤖 Analisar gravação", use_container_width=True, key="analyze_voice_shadow"):
            if not st.session_state.api_key:
                st.error("Insira sua API Key!")
            elif not voice_text.strip():
                st.warning("Grave ou cole o texto primeiro.")
            else:
                with st.spinner("Analisando..."):
                    r = ask_claude(f"""English teacher for Brazilian intermediate learner using shadowing method.
Original scene: "{scene['en']}"
Student said: "{voice_text}"
Give feedback in PT-BR: 1) o que foi bem 2) dicas de pronúncia/ritmo 3) frase-chave para focar 4) encorajamento. Conciso e motivador.""")
                    if r:
                        st.markdown(f"<div class='card' style='border-color:#47CFFF;'><div style='color:#47CFFF;font-weight:700;margin-bottom:0.8rem;'>🤖 Feedback</div>{r}</div>", unsafe_allow_html=True)
                        st.session_state.xp += 15
                        st.success(f"🎉 +15 XP! Total: {st.session_state.xp}")

    with text_tab:
        user_attempt = st.text_area("✍️ Escreva o que você falou:", placeholder="Type here...", height=100, key="text_shadow")
        fb_type = st.radio("Análise:", ["🎯 Pronúncia/ritmo","📝 Gramática","💬 Vocabulário","🌟 Completa"], horizontal=True)
        if st.button("🤖 Analisar texto", use_container_width=True, key="analyze_text_shadow"):
            if not st.session_state.api_key:
                st.error("Insira sua API Key!")
            elif not user_attempt.strip():
                st.warning("Escreva algo!")
            else:
                with st.spinner("Analisando..."):
                    r = ask_claude(f"""English teacher, shadowing method, Brazilian intermediate learner.
Original: "{scene['en']}"
Student wrote: "{user_attempt}"
Analysis: {fb_type}
Feedback em PT-BR, amigável: 1) pontos positivos 2) dicas específicas 3) frase-chave 4) encorajamento.""")
                    if r:
                        st.markdown(f"<div class='card' style='border-color:#47CFFF;'><div style='color:#47CFFF;font-weight:700;margin-bottom:0.8rem;'>🤖 Feedback</div>{r}</div>", unsafe_allow_html=True)
                        st.session_state.xp += 15
                        st.success(f"🎉 +15 XP! Total: {st.session_state.xp}")

# ═══════════════════════════════════════════════════════════════
# TAB 2 — YOUTUBE SHADOWING
# ═══════════════════════════════════════════════════════════════
with tab2:
    st.markdown("<h2>▶️ Shadowing com YouTube</h2>", unsafe_allow_html=True)
    st.markdown("<p class='muted-text'>Cole qualquer link do YouTube em inglês — extraímos as legendas e você pratica shadowing real.</p>", unsafe_allow_html=True)

    st.markdown("""
    <div class='card' style='border-color:#E8FF4744;'>
      <b style='color:#E8FF47;'>💡 Dicas de vídeos para iniciantes/intermediários:</b><br>
      <span class='muted-text'>TED-Ed · BBC Learning English · EnglishClass101 · Friends clips · Crash Course</span>
    </div>""", unsafe_allow_html=True)

    yt_url = st.text_input("🔗 Cole o link do YouTube:", placeholder="https://www.youtube.com/watch?v=...")

    col_load, col_clear = st.columns([2, 1])
    with col_load:
        load_btn = st.button("▶️ Carregar vídeo e legendas", use_container_width=True)
    with col_clear:
        if st.button("🗑️ Limpar", use_container_width=True):
            st.session_state.yt_transcript = []
            st.session_state.yt_video_id = ""
            st.rerun()

    if load_btn and yt_url.strip():
        vid = extract_video_id(yt_url.strip())
        if not vid:
            st.error("URL inválida. Use um link do YouTube.")
        else:
            with st.spinner("Carregando vídeo e legendas..."):
                transcript = get_transcript(vid)
                if transcript:
                    st.session_state.yt_transcript = transcript
                    st.session_state.yt_video_id = vid
                    st.success(f"✅ {len(transcript)} segmentos de legenda carregados!")
                else:
                    st.warning("Não foi possível obter legendas. Tente outro vídeo com legendas ativadas.")

    if st.session_state.yt_video_id:
        vid = st.session_state.yt_video_id
        transcript = st.session_state.yt_transcript

        # Embed YouTube video
        st.markdown(f"""
        <div style='margin:1rem 0;'>
          <iframe width="100%" height="360"
            src="https://www.youtube.com/embed/{vid}?cc_load_policy=1&cc_lang_pref=en"
            frameborder="0" allowfullscreen
            style='border-radius:12px;'></iframe>
        </div>""", unsafe_allow_html=True)

        # Transcript segments
        segments = transcript_to_segments(transcript, chunk_size=4)

        st.markdown("### 📜 Legendas para praticar shadowing")
        st.markdown("<p class='muted-text'>Selecione um trecho, ouça a pronúncia e repita em voz alta.</p>", unsafe_allow_html=True)

        seg_idx = st.selectbox(
            "Trecho:",
            range(len(segments)),
            format_func=lambda i: f"[{int(segments[i]['start']//60):02d}:{int(segments[i]['start']%60):02d}] {segments[i]['text'][:60]}...",
            label_visibility="collapsed",
        )
        seg = segments[seg_idx]

        st.markdown(f"""
        <div class='card-accent'>
          <div style='font-size:0.75rem;color:#7A7A8A;letter-spacing:2px;text-transform:uppercase;margin-bottom:0.8rem;'>
            ⏱ {int(seg['start']//60):02d}:{int(seg['start']%60):02d}
          </div>
          <div style='font-size:1.2rem;line-height:1.9;font-weight:500;color:#F0EFE9;'>"{seg['text']}"</div>
        </div>""", unsafe_allow_html=True)

        col_h, col_s = st.columns(2)
        with col_h:
            st.markdown(tts_button_html(seg["text"], "🔊 Ouvir trecho", rate=0.85), unsafe_allow_html=True)
        with col_s:
            st.markdown(tts_button_html(seg["text"], "🐢 Ouvir devagar", rate=0.6), unsafe_allow_html=True)

        st.markdown(f"<div style='margin-top:0.5rem;'><a href='https://www.youtube.com/watch?v={vid}&t={seg['start']}s' target='_blank' style='color:#47CFFF;font-size:0.85rem;'>▶ Abrir este trecho no YouTube</a></div>", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 🤖 Análise do trecho com IA")

        yt_stt_tab, yt_text_tab = st.tabs(["🎙️ Gravar voz", "✍️ Digitar"])

        with yt_stt_tab:
            st.components.v1.html(STT_COMPONENT, height=200)
            yt_voice = st.text_area("Texto capturado:", placeholder="Cole aqui...", height=70, key="yt_voice")
            if st.button("🤖 Analisar voz", use_container_width=True, key="yt_analyze_voice"):
                if not st.session_state.api_key:
                    st.error("Insira sua API Key!")
                elif not yt_voice.strip():
                    st.warning("Cole o texto reconhecido!")
                else:
                    with st.spinner("Analisando..."):
                        r = ask_claude(f"""English teacher, shadowing method.
Original from YouTube: "{seg['text']}"
Student said: "{yt_voice}"
Feedback em PT-BR: pronúncia, ritmo, vocabulário. Seja encorajador e específico.""")
                        if r:
                            st.markdown(f"<div class='card' style='border-color:#47CFFF;'><b style='color:#47CFFF;'>🤖 Feedback</b><br><br>{r}</div>", unsafe_allow_html=True)
                            st.session_state.xp += 15
                            st.success(f"🎉 +15 XP!")

        with yt_text_tab:
            yt_text = st.text_area("Escreva o que você disse:", placeholder="Type here...", height=80, key="yt_text")
            if st.button("🤖 Analisar texto", use_container_width=True, key="yt_analyze_text"):
                if not st.session_state.api_key:
                    st.error("Insira sua API Key!")
                elif not yt_text.strip():
                    st.warning("Escreva algo!")
                else:
                    with st.spinner("Analisando..."):
                        r = ask_claude(f"""English teacher, shadowing method.
Original: "{seg['text']}"
Student wrote: "{yt_text}"
Feedback em PT-BR: pronúncia, ritmo, vocabulário. Encorajador e específico.""")
                        if r:
                            st.markdown(f"<div class='card' style='border-color:#47CFFF;'><b style='color:#47CFFF;'>🤖 Feedback</b><br><br>{r}</div>", unsafe_allow_html=True)
                            st.session_state.xp += 15
                            st.success(f"🎉 +15 XP!")

        # Full transcript as context for Claude
        st.markdown("---")
        st.markdown("### 💬 Pergunte sobre o vídeo")
        full_text = transcript_to_text(transcript, max_chars=2500)
        yt_q = st.text_input("Dúvida sobre o vídeo:", placeholder="Ex: O que significa 'figure out'? Qual o tom do vídeo?")
        if st.button("❓ Perguntar", use_container_width=True) and yt_q.strip():
            if not st.session_state.api_key:
                st.error("Insira sua API Key!")
            else:
                with st.spinner("Analisando vídeo..."):
                    r = ask_claude(f"""You are an English teacher. The student is watching a YouTube video. Here is the transcript:
"{full_text}"
Student question (in Portuguese): "{yt_q}"
Answer in PT-BR, teacher-style, friendly and educational.""", max_tokens=600)
                    if r:
                        st.markdown(f"<div class='card' style='border-color:#E8FF47;'><b style='color:#E8FF47;'>🤖 Professor</b><br><br>{r}</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# TAB 3 — CONVERSAÇÃO COM VOZ
# ═══════════════════════════════════════════════════════════════
with tab3:
    st.markdown("<h2>🤖 Conversação com Voz</h2>", unsafe_allow_html=True)
    st.markdown("<p class='muted-text'>Converse em inglês com o professor IA — fale ou escreva, e ouça as respostas.</p>", unsafe_allow_html=True)

    cp, ct = st.columns(2)
    with cp:
        st.markdown("**Professor:**")
        persona_name = st.selectbox("P", list(PERSONAS.keys()), label_visibility="collapsed")
    with ct:
        st.markdown("**Tema:**")
        topic = st.selectbox("T", ["💬 Livre"] + list(TOPIC_STARTERS.keys()), label_visibility="collapsed")

    persona = PERSONAS[persona_name]
    st.markdown(f"<div class='card'><span style='color:#E8FF47;font-weight:600;'>{persona_name}</span><br><span class='muted-text'>{persona['desc']}</span></div>", unsafe_allow_html=True)

    c_new, c_lvl = st.columns([1, 1])
    with c_new:
        if st.button("🔄 Nova conversa", use_container_width=True):
            st.session_state.conversation = []
            st.rerun()
    with c_lvl:
        correction = st.selectbox("Correção", ["🟡 Suave","🔴 Detalhada","🟢 Só elogios"], label_visibility="collapsed")

    if not st.session_state.conversation and topic != "💬 Livre":
        starter = TOPIC_STARTERS.get(topic,"")
        if starter:
            st.session_state.conversation.append({"role":"assistant","content":starter})

    # Chat display
    if not st.session_state.conversation:
        st.markdown("""<div style='text-align:center;padding:2rem;color:#7A7A8A;'>
          <div style='font-size:2.5rem;margin-bottom:0.5rem;'>💬</div>
          <div>Comece a conversa abaixo — fale ou escreva em inglês!</div>
        </div>""", unsafe_allow_html=True)
    else:
        for msg in st.session_state.conversation:
            if msg["role"] == "user":
                st.markdown(f"<div class='msg-user'><span style='font-size:0.75rem;color:#E8FF47;font-weight:600;'>VOCÊ</span><br>{msg['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='msg-ai'><span style='font-size:0.75rem;color:#47CFFF;font-weight:600;'>PROFESSOR IA</span><br>{msg['content']}</div>", unsafe_allow_html=True)
                if st.session_state.tts_enabled:
                    st.markdown(tts_button_html(msg["content"], "🔊 Ouvir resposta", rate=persona["voice_rate"]), unsafe_allow_html=True)

    st.markdown("---")

    input_mode = st.radio("Como quer responder?", ["✍️ Digitar","🎙️ Gravar voz"], horizontal=True)

    correction_map = {
        "🟡 Suave": "Correct errors subtly by modeling correct English naturally.",
        "🔴 Detalhada": "Explicitly point out errors and explain the correct form briefly in Portuguese.",
        "🟢 Só elogios": "Be very encouraging, only correct critical errors.",
    }
    system = f"{persona['system']}\n\nCorrection: {correction_map[correction]}\n\nAlways respond in English. Brief grammar notes in Portuguese at the end if needed."

    if input_mode == "✍️ Digitar":
        user_msg = st.text_area("Em inglês:", placeholder="Type in English...", height=90, key="conv_type")
        c_send, c_tr = st.columns([2, 1])
        with c_send:
            send = st.button("📤 Enviar", use_container_width=True)
        with c_tr:
            translate = st.button("🇧🇷→🇺🇸", use_container_width=True)

        if translate and user_msg.strip() and st.session_state.api_key:
            with st.spinner("Traduzindo..."):
                tr = ask_claude_chat([{"role":"user","content":f"Translate to natural intermediate English: {user_msg}"}],
                                     "You are a translator. Return ONLY the English translation.")
                if tr: st.info(f"🇺🇸 **{tr}**")

        if send and user_msg.strip():
            if not st.session_state.api_key:
                st.error("Insira sua API Key!")
            else:
                st.session_state.conversation.append({"role":"user","content":user_msg})
                with st.spinner("Respondendo..."):
                    r = ask_claude_chat(st.session_state.conversation, system)
                    if r:
                        st.session_state.conversation.append({"role":"assistant","content":r})
                        st.session_state.xp += 10
                        st.rerun()

    else:  # Gravar voz
        st.markdown("<p class='muted-text'>Grave sua fala em inglês. O texto será enviado ao professor IA.</p>", unsafe_allow_html=True)
        st.components.v1.html(STT_COMPONENT, height=210)
        voice_conv = st.text_area("Texto reconhecido (cole aqui):", placeholder="Cole o texto gravado...", height=70, key="conv_voice")
        if st.button("📤 Enviar gravação", use_container_width=True) and voice_conv.strip():
            if not st.session_state.api_key:
                st.error("Insira sua API Key!")
            else:
                st.session_state.conversation.append({"role":"user","content":voice_conv})
                with st.spinner("Professor respondendo..."):
                    r = ask_claude_chat(st.session_state.conversation, system)
                    if r:
                        st.session_state.conversation.append({"role":"assistant","content":r})
                        st.session_state.xp += 10
                        st.rerun()

    if st.session_state.conversation:
        u = [m for m in st.session_state.conversation if m["role"]=="user"]
        words = sum(len(m["content"].split()) for m in u)
        st.markdown(f"<div class='muted-text' style='margin-top:1rem;'>📊 {len(u)} mensagens · {words} palavras · +{len(u)*10} XP</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# TAB 4 — FLASHCARDS
# ═══════════════════════════════════════════════════════════════
with tab4:
    st.markdown("<h2>🃏 Flashcards com Revisão Espaçada</h2>", unsafe_allow_html=True)
    ft1, ft2, ft3 = st.tabs(["📚 Estudar","🗂️ Gerenciar","✨ Gerar com IA"])

    with ft1:
        cd, cs = st.columns([2, 1])
        with cd:
            deck_name = st.selectbox("Baralho", list(st.session_state.flashcard_decks.keys()), label_visibility="collapsed")
        deck = st.session_state.flashcard_decks[deck_name]
        due = get_due_cards(deck)
        with cs:
            st.markdown(f"<div style='padding:0.5rem 0;'><span style='color:#E8FF47;font-weight:700;font-size:1.2rem;'>{len(due)}</span> <span class='muted-text'>p/ revisar</span></div>", unsafe_allow_html=True)

        if not due:
            st.markdown("""<div style='text-align:center;padding:3rem;'>
              <div style='font-size:3rem;'>🎉</div><h3 style='color:#E8FF47;'>Tudo em dia!</h3>
              <p class='muted-text'>Volte amanhã!</p></div>""", unsafe_allow_html=True)
        else:
            if st.session_state.fc_index >= len(due): st.session_state.fc_index = 0
            card_idx = due[st.session_state.fc_index]
            card = deck[card_idx]
            lvl_labels = ["🌱 Novo","🔵 Fácil","🟡 Médio","🟠 Difícil","🟢 Dominado","⭐ Expert"]
            lvl = card.get("level", 0)

            st.progress(st.session_state.fc_index / len(due))
            st.markdown(f"<div class='muted-text' style='text-align:right;'>{st.session_state.fc_index+1}/{len(due)}</div>", unsafe_allow_html=True)

            st.markdown(f"""<div class='flashcard'>
              <div style='font-size:0.75rem;color:#7A7A8A;letter-spacing:2px;text-transform:uppercase;margin-bottom:1rem;'>🇺🇸 Inglês</div>
              <div style='font-size:2rem;font-family:Syne,sans-serif;font-weight:800;color:#E8FF47;margin-bottom:0.5rem;'>{card["en"]}</div>
              <div style='font-size:0.8rem;color:#7A7A8A;'>{lvl_labels[min(lvl,5)]}</div>
            </div>""", unsafe_allow_html=True)

            fc1, fc2 = st.columns(2)
            with fc1:
                if st.button("👁️ Ver resposta" if not st.session_state.fc_show_answer else "🙈 Esconder", use_container_width=True):
                    st.session_state.fc_show_answer = not st.session_state.fc_show_answer
                    st.rerun()
            with fc2:
                st.markdown(tts_button_html(card["en"], "🔊 Ouvir pronúncia", rate=0.8), unsafe_allow_html=True)

            if st.session_state.fc_show_answer:
                st.markdown(f"""<div class='card' style='text-align:center;border-color:#47CFFF;'>
                  <div style='font-size:0.75rem;color:#47CFFF;letter-spacing:2px;text-transform:uppercase;margin-bottom:0.5rem;'>🇧🇷 Português</div>
                  <div style='font-size:1.4rem;font-weight:600;color:#F0EFE9;margin-bottom:0.8rem;'>{card["pt"]}</div>
                  <div style='font-size:0.85rem;color:#7A7A8A;font-style:italic;'>"{card["example"]}"</div>
                </div>""", unsafe_allow_html=True)
                st.markdown(tts_button_html(card["example"], "🔊 Ouvir exemplo", rate=0.85), unsafe_allow_html=True)

                st.markdown("**Como foi?**")
                r1,r2,r3,r4 = st.columns(4)
                for col,label,q in [(r1,"😰 Errei",0),(r2,"🤔 Difícil",2),(r3,"😊 Lembrei",3),(r4,"🚀 Fácil!",5)]:
                    with col:
                        if st.button(label, use_container_width=True, key=f"fc_{q}_{deck_name}"):
                            st.session_state.flashcard_decks[deck_name] = update_card_review(
                                st.session_state.flashcard_decks[deck_name], card_idx, q)
                            st.session_state.fc_index += 1
                            st.session_state.fc_show_answer = False
                            st.session_state.xp += (q+1)*3
                            st.rerun()

    with ft2:
        st.markdown("### ➕ Adicionar card")
        tgt = st.selectbox("Baralho:", list(st.session_state.flashcard_decks.keys()), key="add_deck")
        an1, an2 = st.columns(2)
        with an1: new_en = st.text_input("Inglês")
        with an2: new_pt = st.text_input("Português")
        new_ex = st.text_input("Exemplo em inglês")
        if st.button("💾 Adicionar") and new_en and new_pt:
            st.session_state.flashcard_decks[tgt].append({"en":new_en,"pt":new_pt,"example":new_ex or f"Example with '{new_en}'.","level":0,"next_review":""})
            st.success(f"✅ '{new_en}' adicionado!")
        st.markdown("### 🗂️ Novo baralho")
        new_dk = st.text_input("Nome (ex: '🏖️ Viagens')")
        if st.button("Criar") and new_dk:
            if new_dk not in st.session_state.flashcard_decks:
                st.session_state.flashcard_decks[new_dk] = []
                st.success(f"'{new_dk}' criado!")
            else: st.warning("Já existe!")

    with ft3:
        st.markdown("### ✨ Gerar flashcards com IA")
        gen_t = st.text_input("Tema:", placeholder="Ex: phrasal verbs com 'get', vocabulário de viagem...")
        gq, gl = st.columns(2)
        with gq: gen_qty = st.slider("Cards:", 3, 15, 8)
        with gl: gen_lvl = st.select_slider("Nível:", ["Básico","Intermediário","Avançado"], value="Intermediário")
        gen_dk = st.selectbox("Baralho destino:", list(st.session_state.flashcard_decks.keys()), key="gen_dk")
        if st.button("🤖 Gerar", use_container_width=True):
            if not st.session_state.api_key: st.error("Insira sua API Key!")
            elif not gen_t.strip(): st.warning("Descreva um tema!")
            else:
                with st.spinner(f"Gerando {gen_qty} flashcards..."):
                    r = ask_claude(f"""Create {gen_qty} English flashcards for Brazilian Portuguese speaker at {gen_lvl} level about: {gen_t}
Return ONLY valid JSON array, no markdown:
[{{"en":"expression","pt":"tradução","example":"Example sentence."}}]""")
                    if r:
                        try:
                            m = re.search(r'\[.*\]', r, re.DOTALL)
                            if m:
                                cards = json.loads(m.group())
                                added = 0
                                for c in cards:
                                    if "en" in c and "pt" in c:
                                        st.session_state.flashcard_decks[gen_dk].append({"en":c["en"],"pt":c["pt"],"example":c.get("example",f"Example with {c['en']}."), "level":0,"next_review":""})
                                        added += 1
                                st.success(f"✅ {added} cards adicionados!")
                                st.session_state.xp += added*5
                                st.rerun()
                        except Exception as e:
                            st.error(f"Erro: {e}")

# ═══════════════════════════════════════════════════════════════
# TAB 5 — PROGRESSO
# ═══════════════════════════════════════════════════════════════
with tab5:
    st.markdown("<h2>📊 Seu Progresso</h2>", unsafe_allow_html=True)
    xp = st.session_state.xp
    level = xp//100+1
    xp_in = xp%100
    lvl_names = ["Iniciante","Explorador","Estudante","Comunicador","Fluente","Expert","Mestre"]
    lvl_name = lvl_names[min(level-1,6)]
    m1,m2,m3,m4 = st.columns(4)
    with m1: st.metric("⚡ XP", xp)
    with m2: st.metric("🏅 Nível", f"{level} — {lvl_name}")
    with m3: st.metric("🔥 Streak", f"{st.session_state.streak}d")
    with m4:
        tc = sum(len(v) for v in st.session_state.flashcard_decks.values())
        st.metric("🃏 Cards", tc)
    st.markdown(f"<div class='card' style='margin-top:1rem;'><div style='display:flex;justify-content:space-between;'><span style='color:#E8FF47;font-weight:700;'>Nível {level}: {lvl_name}</span><span class='muted-text'>{xp_in}/100 XP</span></div></div>", unsafe_allow_html=True)
    st.progress(xp_in/100)
    st.markdown("---")
    st.markdown("### 🃏 Status dos Flashcards")
    for dn, cards in st.session_state.flashcard_decks.items():
        today = datetime.date.today().isoformat()
        due_n = sum(1 for c in cards if not c.get("next_review") or c["next_review"] <= today)
        mastered = sum(1 for c in cards if c.get("level",0)>=4)
        total = len(cards)
        p1,p2,p3,p4 = st.columns([3,1,1,1])
        with p1: st.markdown(f"**{dn}**")
        with p2: st.markdown(f"<span style='color:{'#FF6B6B' if due_n>0 else '#47CFFF'};font-weight:700;'>{due_n}</span> <span class='muted-text'>revisar</span>", unsafe_allow_html=True)
        with p3: st.markdown(f"<span style='color:#E8FF47;font-weight:700;'>{mastered}</span> <span class='muted-text'>dominou</span>", unsafe_allow_html=True)
        with p4: st.markdown(f"<span class='muted-text'>{total} total</span>", unsafe_allow_html=True)
        if total>0: st.progress(mastered/total)
    st.markdown("---")
    for icon,title,desc in [
        ("🎬","Shadowing diário","15–20 min/dia é mais eficaz que 2h no fim de semana."),
        ("▶️","YouTube real","Pratique com conteúdo autêntico — notícias, Ted Talks, vlogs."),
        ("🎙️","Fale sem medo","O reconhecimento de voz treina sua pronúncia de verdade."),
        ("🃏","Revisão espaçada","Revise os cards no horário certo — ciência, não força de vontade."),
    ]:
        st.markdown(f"<div class='card' style='display:flex;gap:1rem;align-items:flex-start;'><div style='font-size:1.8rem;'>{icon}</div><div><div style='font-weight:700;color:#F0EFE9;'>{title}</div><div class='muted-text'>{desc}</div></div></div>", unsafe_allow_html=True)
    with st.expander("⚙️ Configurações"):
        s1,s2 = st.columns(2)
        with s1:
            if st.button("🔄 Resetar XP"):
                st.session_state.xp = 0; st.session_state.streak = 0; st.rerun()
        with s2:
            b = st.number_input("XP manual:", 0, 500, 0, 10)
            if st.button("➕ Adicionar") and b>0:
                st.session_state.xp += b; st.rerun()
