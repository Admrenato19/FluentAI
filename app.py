import streamlit as st
import anthropic
import json, re, datetime, random

st.set_page_config(
    page_title="FluentAI",
    page_icon="🎙️",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={},
)

# ─────────────────────────────────────────────────────────────────
# SPEAK-STYLE CSS — light, coral, mobile-first
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
  --bg: #F7F7F8;
  --surface: #FFFFFF;
  --border: #EBEBED;
  --coral: #FF4B4B;
  --coral-light: #FFF0F0;
  --coral-mid: #FFD6D6;
  --text: #1A1A2E;
  --muted: #8A8A9A;
  --green: #22C55E;
  --blue: #3B82F6;
  --radius: 18px;
  --shadow: 0 2px 16px rgba(0,0,0,0.07);
}

html, body, [class*="css"] {
  font-family: 'Inter', sans-serif !important;
  background: var(--bg) !important;
  color: var(--text) !important;
}

.stApp { background: var(--bg) !important; max-width: 480px; margin: 0 auto; }

/* Hide ALL Streamlit chrome */
#MainMenu { visibility: hidden !important; display: none !important; }
footer { visibility: hidden !important; display: none !important; }
header { visibility: hidden !important; display: none !important; }
[data-testid="stSidebar"] { visibility: hidden !important; display: none !important; }
[data-testid="stToolbar"] { visibility: hidden !important; display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
[data-testid="stStatusWidget"] { display: none !important; }
.stDeployButton { display: none !important; }
button[kind="header"] { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }

/* Remove streamlit padding */
.block-container { padding: 0 1rem 6rem !important; max-width: 480px !important; margin-top: 0 !important; }

/* Typography */
h1 { font-size: 1.7rem !important; font-weight: 800 !important; color: var(--text) !important; margin-bottom: .2rem !important; }
h2 { font-size: 1.3rem !important; font-weight: 700 !important; color: var(--text) !important; }
h3 { font-size: 1.1rem !important; font-weight: 600 !important; color: var(--text) !important; }

/* Buttons */
.stButton > button {
  background: var(--coral) !important;
  color: white !important;
  border: none !important;
  border-radius: 14px !important;
  font-family: 'Inter', sans-serif !important;
  font-weight: 600 !important;
  font-size: .95rem !important;
  padding: .75rem 1.5rem !important;
  transition: all .15s !important;
  box-shadow: 0 4px 14px rgba(255,75,75,.25) !important;
}
.stButton > button:hover {
  transform: translateY(-1px) !important;
  box-shadow: 0 6px 20px rgba(255,75,75,.35) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* Secondary button style via class */
.btn-ghost > button {
  background: var(--surface) !important;
  color: var(--text) !important;
  border: 1.5px solid var(--border) !important;
  box-shadow: none !important;
}

/* Inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
  background: var(--surface) !important;
  border: 1.5px solid var(--border) !important;
  border-radius: 12px !important;
  color: var(--text) !important;
  font-family: 'Inter', sans-serif !important;
}

/* Cards */
.card {
  background: var(--surface);
  border-radius: var(--radius);
  padding: 1.2rem;
  margin-bottom: .75rem;
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
}
.card-coral {
  background: var(--coral-light);
  border-radius: var(--radius);
  padding: 1.2rem;
  margin-bottom: .75rem;
  border: 1px solid var(--coral-mid);
}

/* Video card */
.vid-card {
  background: var(--surface);
  border-radius: var(--radius);
  overflow: hidden;
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
  margin-bottom: .75rem;
  transition: transform .15s;
}
.vid-card:hover { transform: translateY(-2px); }
.vid-thumb { width: 100%; aspect-ratio: 16/9; object-fit: cover; }
.vid-meta { padding: .9rem 1rem; }

/* Chat bubbles */
.bubble-user {
  background: var(--coral);
  color: white;
  border-radius: 18px 18px 4px 18px;
  padding: .85rem 1.1rem;
  margin: .4rem 0 .4rem 3rem;
  font-size: .95rem;
  line-height: 1.5;
}
.bubble-ai {
  background: var(--surface);
  color: var(--text);
  border-radius: 18px 18px 18px 4px;
  padding: .85rem 1.1rem;
  margin: .4rem 3rem .4rem 0;
  font-size: .95rem;
  line-height: 1.5;
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
}

/* Mic button */
.mic-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: .5rem;
  padding: 1.5rem 0;
}
.mic-btn {
  width: 84px; height: 84px;
  border-radius: 50%;
  background: var(--coral);
  border: none;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  font-size: 2rem;
  box-shadow: 0 6px 24px rgba(255,75,75,.35);
  transition: all .2s;
}
.mic-btn:hover { transform: scale(1.07); box-shadow: 0 8px 30px rgba(255,75,75,.45); }
.mic-btn.active {
  background: #cc0000;
  animation: pulse 1.2s infinite;
}
@keyframes pulse {
  0%,100% { box-shadow: 0 0 0 0 rgba(255,75,75,.5); }
  50% { box-shadow: 0 0 0 16px rgba(255,75,75,0); }
}

/* Bottom nav */
.bottom-nav {
  position: fixed;
  bottom: 0; left: 50%;
  transform: translateX(-50%);
  width: 100%; max-width: 480px;
  background: var(--surface);
  border-top: 1px solid var(--border);
  display: flex;
  z-index: 999;
  padding: .4rem 0 .6rem;
  box-shadow: 0 -4px 20px rgba(0,0,0,.06);
}
.nav-item {
  flex: 1;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  gap: 2px;
  cursor: pointer;
  padding: .3rem 0;
  font-size: .7rem;
  font-weight: 600;
  color: var(--muted);
  border: none; background: none;
  transition: color .15s;
}
.nav-item.active { color: var(--coral); }
.nav-icon { font-size: 1.35rem; }

/* Badges */
.badge {
  display: inline-block;
  border-radius: 20px;
  padding: 3px 10px;
  font-size: .73rem;
  font-weight: 600;
}
.badge-green { background: #dcfce7; color: #16a34a; }
.badge-yellow { background: #fef9c3; color: #ca8a04; }
.badge-red { background: #fee2e2; color: #dc2626; }
.badge-blue { background: #dbeafe; color: #2563eb; }
.badge-coral { background: var(--coral-light); color: var(--coral); }

/* Progress bar */
.stProgress > div > div > div { background: var(--coral) !important; }

/* Metrics */
[data-testid="stMetric"] {
  background: var(--surface);
  border-radius: var(--radius);
  padding: 1rem;
  border: 1px solid var(--border);
  box-shadow: var(--shadow);
}
[data-testid="stMetricValue"] {
  color: var(--coral) !important;
  font-family: 'Inter', sans-serif !important;
  font-weight: 800 !important;
}

/* Tabs override */
.stTabs [data-baseweb="tab-list"] {
  background: var(--border) !important;
  border-radius: 12px !important;
  gap: 3px;
  padding: 3px;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  color: var(--muted) !important;
  border-radius: 10px !important;
  font-weight: 600 !important;
}
.stTabs [aria-selected="true"] {
  background: var(--surface) !important;
  color: var(--coral) !important;
}

/* Flashcard */
.flashcard {
  background: var(--surface);
  border: 2px solid var(--coral-mid);
  border-radius: 24px;
  padding: 2.5rem 1.5rem;
  text-align: center;
  min-height: 180px;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  box-shadow: var(--shadow);
}

/* Stat card */
.stat-card {
  background: var(--surface);
  border-radius: var(--radius);
  padding: 1.1rem 1.2rem;
  border: 1px solid var(--border);
  box-shadow: var(--shadow);
  display: flex; align-items: center; gap: 1rem;
  margin-bottom: .6rem;
}
.stat-icon { font-size: 1.8rem; }
.stat-val { font-size: 1.5rem; font-weight: 800; color: var(--coral); }
.stat-label { font-size: .8rem; color: var(--muted); font-weight: 500; }

iframe { border-radius: 14px !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# TTS — Web Speech API
# ─────────────────────────────────────────────────────────────────
st.components.v1.html("""
<script>
function fluentSpeak(text, rate=0.88) {
  if (!('speechSynthesis' in window)) return;
  window.speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.lang = 'en-US'; u.rate = rate; u.pitch = 1.0;
  const voices = window.speechSynthesis.getVoices();
  const pref = voices.find(v => v.lang.startsWith('en') && (v.name.includes('Google') || v.name.includes('Natural')));
  if (pref) u.voice = pref;
  window.speechSynthesis.speak(u);
}
window.fluentSpeak = fluentSpeak;
</script>
""", height=0)

def tts_btn(text, label="🔊", rate=0.88):
    safe = text.replace("'", "\\'").replace("\n", " ").replace('"', '\\"')[:500]
    return f'<button onclick="fluentSpeak(\'{safe}\',{rate})" style="background:var(--coral,#FF4B4B);color:white;border:none;border-radius:10px;padding:7px 16px;font-weight:600;cursor:pointer;font-size:.85rem;font-family:Inter,sans-serif;margin:4px 4px 4px 0;">{label}</button>'

# ─────────────────────────────────────────────────────────────────
# AUTO-SILENCE STT — continuous, sends on silence
# ─────────────────────────────────────────────────────────────────
STT_AUTO_HTML = """
<div id="stt-container" style="display:flex;flex-direction:column;align-items:center;gap:12px;padding:1rem 0;">
  <button id="mic-btn" onclick="toggleMic()" style="
    width:84px;height:84px;border-radius:50%;
    background:#FF4B4B;border:none;cursor:pointer;
    font-size:2rem;color:white;
    box-shadow:0 6px 24px rgba(255,75,75,.35);
    transition:all .2s;
  ">🎙️</button>
  <span id="mic-status" style="color:#8A8A9A;font-size:.85rem;font-family:Inter,sans-serif;">Tap to speak</span>
  <div id="transcript-box" style="
    background:#fff;border:1.5px solid #EBEBED;border-radius:14px;
    padding:.8rem 1rem;min-height:52px;width:100%;max-width:380px;
    color:#1A1A2E;font-size:.95rem;line-height:1.6;font-family:Inter,sans-serif;
    box-sizing:border-box;
  "></div>
  <button id="send-btn" onclick="sendTranscript()" style="
    display:none;
    background:#FF4B4B;color:white;border:none;border-radius:12px;
    padding:10px 28px;font-weight:600;cursor:pointer;
    font-size:.9rem;font-family:Inter,sans-serif;
    box-shadow:0 4px 14px rgba(255,75,75,.25);
  ">Send →</button>
</div>
<script>
let rec = null, final_t = '', silenceTimer = null, isListening = false;

function toggleMic() {
  if (isListening) stopRec();
  else startRec();
}

function startRec() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) { document.getElementById('mic-status').innerText = '❌ Use Chrome'; return; }
  rec = new SR();
  rec.lang = 'en-US';
  rec.interimResults = true;
  rec.continuous = true;
  final_t = '';

  rec.onstart = () => {
    isListening = true;
    document.getElementById('mic-btn').style.background = '#cc0000';
    document.getElementById('mic-btn').style.animation = 'pulse 1.2s infinite';
    document.getElementById('mic-btn').innerHTML = '⏹';
    document.getElementById('mic-status').innerHTML = '<span style="color:#FF4B4B">● Listening...</span>';
    document.getElementById('send-btn').style.display = 'none';
    document.getElementById('transcript-box').innerText = '';
  };

  rec.onresult = (e) => {
    let tmp = '';
    for (let i = e.resultIndex; i < e.results.length; i++) {
      if (e.results[i].isFinal) final_t += e.results[i][0].transcript + ' ';
      else tmp += e.results[i][0].transcript;
    }
    document.getElementById('transcript-box').innerText = final_t + tmp;
    // Reset silence timer
    clearTimeout(silenceTimer);
    silenceTimer = setTimeout(() => { if (isListening) stopRec(); }, 1800);
  };

  rec.onend = () => {
    isListening = false;
    document.getElementById('mic-btn').style.background = '#FF4B4B';
    document.getElementById('mic-btn').style.animation = '';
    document.getElementById('mic-btn').innerHTML = '🎙️';
    if (final_t.trim()) {
      document.getElementById('mic-status').innerText = 'Got it! Send when ready.';
      document.getElementById('send-btn').style.display = 'inline-block';
    } else {
      document.getElementById('mic-status').innerText = 'Tap to speak';
    }
  };

  rec.onerror = (e) => {
    document.getElementById('mic-status').innerText = '❌ Error: ' + e.error;
    isListening = false;
  };
  rec.start();
}

function stopRec() { clearTimeout(silenceTimer); if (rec) rec.stop(); }

function sendTranscript() {
  const text = document.getElementById('transcript-box').innerText.trim();
  if (!text) return;
  // Copy to clipboard so user can paste if needed, but also set streamlit input
  navigator.clipboard.writeText(text).catch(() => {});
  document.getElementById('mic-status').innerText = '✅ Copied! Paste below if needed.';
  document.getElementById('send-btn').style.display = 'none';
  // Try to find streamlit text area and set value
  const areas = window.parent.document.querySelectorAll('textarea');
  for (const area of areas) {
    if (area.placeholder && area.placeholder.includes('transcri')) {
      const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
      nativeInputValueSetter.call(area, text);
      area.dispatchEvent(new Event('input', { bubbles: true }));
      break;
    }
  }
}
</script>
<style>
@keyframes pulse {
  0%,100% { box-shadow: 0 0 0 0 rgba(255,75,75,.5); }
  50% { box-shadow: 0 0 0 16px rgba(255,75,75,0); }
}
</style>
"""

# ─────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────
defaults = {
    "api_key": "",
    "yt_api_key": "",
    "page": "home",
    # video context
    "yt_video_id": "",
    "yt_video_title": "",
    "yt_transcript": [],
    # conversations
    "conversation": [],
    "conv_video_id": "",   # which video the conversation is about
    # weekly
    "weekly_videos": [],
    "weekly_generated_date": "",
    # flashcards
    "flashcard_decks": None,
    "fc_index": 0,
    "fc_show_answer": False,
    # metrics
    "metric_conversations": 0,
    "metric_minutes": 0,
    "metric_flashcards_reviewed": 0,
    "metric_videos_studied": set(),
    "conv_start_time": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────────
# CLAUDE API
# ─────────────────────────────────────────────────────────────────
def ask_claude(prompt, max_tokens=1000):
    try:
        c = anthropic.Anthropic(api_key=st.session_state.api_key)
        m = c.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        return m.content[0].text
    except anthropic.AuthenticationError:
        st.error("❌ Invalid Claude API Key.")
    except anthropic.RateLimitError:
        st.error("⚠️ Rate limit. Please wait.")
    except Exception as e:
        st.error(f"Claude error: {e}")
    return ""

def ask_claude_chat(messages, system, max_tokens=800):
    try:
        c = anthropic.Anthropic(api_key=st.session_state.api_key)
        m = c.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            system=system,
            messages=messages
        )
        return m.content[0].text
    except anthropic.AuthenticationError:
        st.error("❌ Invalid Claude API Key.")
    except anthropic.RateLimitError:
        st.error("⚠️ Rate limit. Please wait.")
    except Exception as e:
        st.error(f"Claude error: {e}")
    return ""

# ─────────────────────────────────────────────────────────────────
# YOUTUBE HELPERS
# ─────────────────────────────────────────────────────────────────
def extract_video_id(url):
    for p in [r'v=([^&\s]+)', r'youtu\.be/([^?\s]+)', r'embed/([^?\s]+)']:
        m = re.search(p, url)
        if m: return m.group(1)
    return ""

def get_transcript(video_id):
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        ytt = YouTubeTranscriptApi()
        t = ytt.fetch(video_id)
        return [{"text": s.text, "start": s.start, "duration": s.duration} for s in t]
    except Exception:
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            ytt = YouTubeTranscriptApi()
            for t in ytt.list(video_id):
                f = t.fetch()
                return [{"text": s.text, "start": s.start, "duration": s.duration} for s in f]
        except Exception as e2:
            st.error(f"No subtitles available: {e2}")
            return []

def transcript_to_text(transcript, max_chars=3000):
    full = " ".join(s["text"].replace("\n", " ") for s in transcript)
    return full[:max_chars] + ("..." if len(full) > max_chars else "")

def search_youtube(query, max_results=6, yt_key=None):
    if not yt_key: return []
    try:
        from googleapiclient.discovery import build
        yt = build("youtube", "v3", developerKey=yt_key)
        res = yt.search().list(
            q=query, part="snippet", type="video",
            maxResults=max_results, relevanceLanguage="en", safeSearch="strict"
        ).execute()
        videos = []
        for item in res.get("items", []):
            vid = item["id"]["videoId"]
            snip = item["snippet"]
            videos.append({
                "id": vid,
                "title": snip["title"],
                "channel": snip["channelTitle"],
                "thumbnail": snip["thumbnails"]["medium"]["url"],
                "url": f"https://www.youtube.com/watch?v={vid}",
            })
        return videos
    except Exception as e:
        st.warning(f"YouTube search failed: {e}")
        return []

# ─────────────────────────────────────────────────────────────────
# CURATED VIDEOS
# ─────────────────────────────────────────────────────────────────
CURATED_VIDEOS = [
    {"id": "_ZBKX-6Gz6A", "title": "How language shapes the way we think", "channel": "TED", "level": "Intermediate", "type": "TED Talk", "duration": "14:03"},
    {"id": "8S0FDjFBj8o", "title": "The linguistic genius of babies", "channel": "TED", "level": "Intermediate", "type": "TED Talk", "duration": "10:18"},
    {"id": "Unzc731iCUY", "title": "Think like a coder", "channel": "TED-Ed", "level": "Beginner", "type": "TED-Ed", "duration": "5:37"},
    {"id": "arj7oStGLkU", "title": "TED's secret to great public speaking", "channel": "TED", "level": "Intermediate", "type": "TED Talk", "duration": "7:35"},
    {"id": "eIho2S0ZahI", "title": "The power of introverts", "channel": "TED", "level": "Advanced", "type": "TED Talk", "duration": "19:04"},
    {"id": "4bFYmMqq_Hs", "title": "6 Minute English — Technology", "channel": "BBC Learning English", "level": "Beginner", "type": "BBC Learning", "duration": "6:00"},
    {"id": "YsA3PK8bQd8", "title": "English at Work — Job interview", "channel": "BBC Learning English", "level": "Intermediate", "type": "BBC Learning", "duration": "5:48"},
    {"id": "BMukniszEiA", "title": "A day in the life of a New Yorker", "channel": "Nathaniel Drew", "level": "Intermediate", "type": "Vlog", "duration": "11:24"},
    {"id": "H14bBuluwB8", "title": "How I learned English fluently", "channel": "Nathaniel Drew", "level": "Beginner", "type": "Vlog", "duration": "9:41"},
    {"id": "NiECCdXCPeE", "title": "The science of sleep", "channel": "TED-Ed", "level": "Intermediate", "type": "TED-Ed", "duration": "4:42"},
    {"id": "GK_vRtHJZu4", "title": "Why do we dream?", "channel": "TED-Ed", "level": "Beginner", "type": "TED-Ed", "duration": "5:46"},
    {"id": "fmaG9EAZe90", "title": "How to argue — Philosophical reasoning", "channel": "Crash Course", "level": "Advanced", "type": "Educational", "duration": "9:52"},
]

def get_week_key():
    today = datetime.date.today()
    return f"{today.year}-W{today.isocalendar()[1]}"

def generate_weekly_curated():
    random.seed(int(get_week_key().replace("-W", "")))
    pool = CURATED_VIDEOS.copy()
    random.shuffle(pool)
    return pool[:4]

# ─────────────────────────────────────────────────────────────────
# FLASHCARDS
# ─────────────────────────────────────────────────────────────────
DEFAULT_DECKS = {
    "🎬 From Videos": [],
    "💼 Daily Life": [
        {"en": "hang out", "pt": "sair com amigos", "example": "Want to hang out this weekend?", "level": 0, "next_review": ""},
        {"en": "figure out", "pt": "descobrir/resolver", "example": "I can't figure out this problem.", "level": 0, "next_review": ""},
        {"en": "give up", "pt": "desistir", "example": "Don't give up on your dreams!", "level": 0, "next_review": ""},
        {"en": "deal with", "pt": "lidar com", "example": "I have to deal with a lot of stress.", "level": 0, "next_review": ""},
        {"en": "catch up", "pt": "colocar o papo em dia", "example": "Let's catch up over coffee!", "level": 0, "next_review": ""},
    ],
}
INTERVAL_DAYS = [0, 1, 3, 7, 14, 30]

if st.session_state.flashcard_decks is None:
    st.session_state.flashcard_decks = {k: [dict(c) for c in v] for k, v in DEFAULT_DECKS.items()}

def get_due(deck):
    today = datetime.date.today().isoformat()
    return [i for i, c in enumerate(deck) if not c.get("next_review") or c["next_review"] <= today]

def update_review(deck, idx, q):
    lvl = deck[idx].get("level", 0)
    lvl = min(lvl + 1, 5) if q >= 3 else max(lvl - 1, 0)
    deck[idx]["level"] = lvl
    deck[idx]["next_review"] = (datetime.date.today() + datetime.timedelta(days=INTERVAL_DAYS[lvl])).isoformat()
    return deck

def generate_flashcards_from_video(video_title, transcript_text):
    prompt = f"""You are an English teacher for Brazilian learners.
Based on this video transcript, extract 6 useful English expressions, phrasal verbs, or vocabulary.
Video: "{video_title}"
Transcript excerpt: "{transcript_text[:1500]}"

Return ONLY valid JSON array:
[{{"en":"expression","pt":"tradução em português","example":"example sentence from the video context."}}]"""
    r = ask_claude(prompt, max_tokens=600)
    if r:
        try:
            m = re.search(r'\[.*\]', r, re.DOTALL)
            if m:
                cards = json.loads(m.group())
                return [{"en": c["en"], "pt": c["pt"], "example": c.get("example", ""), "level": 0, "next_review": ""} for c in cards if "en" in c and "pt" in c]
        except Exception:
            pass
    return []

# ─────────────────────────────────────────────────────────────────
# NAVIGATION — SVG icons, no emoji
# ─────────────────────────────────────────────────────────────────
SVG = {
    "home": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>',
    "videos": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="15" height="14" rx="2"/><path d="m17 8 5-3v14l-5-3"/></svg>',
    "talk": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="22"/><line x1="8" y1="22" x2="16" y2="22"/></svg>',
    "cards": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="5" width="20" height="14" rx="2"/><line x1="2" y1="10" x2="22" y2="10"/></svg>',
    "settings": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
}

NAV_ITEMS = [
    ("home", "Home"),
    ("videos", "Videos"),
    ("talk", "Talk"),
    ("cards", "Cards"),
    ("settings", "Settings"),
]

# Handle URL page param
query_params = st.query_params
if "page" in query_params:
    st.session_state.page = query_params["page"]

page = st.session_state.page

nav_html = '<div class="bottom-nav">'
for key, label in NAV_ITEMS:
    active = "active" if page == key else ""
    nav_html += f'<a href="?page={key}" class="nav-item {active}" style="text-decoration:none;">{SVG[key]}<span>{label}</span></a>'
nav_html += '</div>'
st.markdown(nav_html, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# PAGE: HOME
# ═══════════════════════════════════════════════════════════════
if page == "home":
    st.markdown("<div style='padding:1.5rem 0 .5rem;'><h1>Good day! 👋</h1><p style='color:#8A8A9A;margin-top:.2rem;'>Practice English with AI-powered conversations</p></div>", unsafe_allow_html=True)

    # API key nudge
    if not st.session_state.api_key:
        st.markdown("<a href='?page=settings' style='text-decoration:none;'><div class='card-coral' style='cursor:pointer;'><b style='color:#FF4B4B;'>🔑 Add your API Key</b><br><span style='color:#8A8A9A;font-size:.9rem;'>Tap here to go to Settings and paste your Anthropic key.</span></div></a>", unsafe_allow_html=True)

    # Weekly pick
    week = get_week_key()
    if not st.session_state.weekly_videos or st.session_state.weekly_generated_date != week:
        with st.spinner("Selecting this week's videos..."):
            if st.session_state.yt_api_key:
                queries = ["TED talk english intermediate 2024", "BBC learning english 2024"]
                all_vids = []
                for q in queries:
                    all_vids.extend(search_youtube(q, max_results=2, yt_key=st.session_state.yt_api_key))
                seen = set(); unique = []
                for v in all_vids:
                    if v["id"] not in seen:
                        seen.add(v["id"]); unique.append(v)
                st.session_state.weekly_videos = unique[:4] if unique else generate_weekly_curated()
            else:
                st.session_state.weekly_videos = generate_weekly_curated()
            st.session_state.weekly_generated_date = week

    st.markdown("<h2 style='margin-bottom:.5rem;'>This week's picks</h2>", unsafe_allow_html=True)
    featured = st.session_state.weekly_videos[0] if st.session_state.weekly_videos else None
    if featured:
        lvl = featured.get("level", "Intermediate")
        badge_cls = {"Beginner": "badge-green", "Intermediate": "badge-yellow", "Advanced": "badge-red"}.get(lvl, "badge-yellow")
        st.markdown(f"""
        <div class='vid-card'>
          <img class='vid-thumb' src='https://img.youtube.com/vi/{featured["id"]}/mqdefault.jpg'/>
          <div class='vid-meta'>
            <span class='badge {badge_cls}'>{lvl}</span>
            <div style='font-weight:700;font-size:1rem;color:#1A1A2E;margin:.4rem 0 .2rem;line-height:1.4;'>{featured["title"][:65]}{"..." if len(featured["title"])>65 else ""}</div>
            <div style='font-size:.8rem;color:#8A8A9A;'>{featured.get("channel","")} {f"· {featured.get('duration','')}" if featured.get('duration') else ""}</div>
          </div>
        </div>""", unsafe_allow_html=True)
        if st.button("▶ Study this video", use_container_width=True, key="home_study"):
            with st.spinner("Loading transcript..."):
                t = get_transcript(featured["id"])
                if t:
                    st.session_state.yt_video_id = featured["id"]
                    st.session_state.yt_video_title = featured["title"]
                    st.session_state.yt_transcript = t
                    st.session_state.metric_videos_studied.add(featured["id"])
                    st.session_state.page = "talk"
                    st.session_state.conv_video_id = featured["id"]
                    st.session_state.conversation = []
                    st.query_params["page"] = "talk"
                    st.rerun()
                else:
                    st.warning("No subtitles available for this video.")

    # Rest of weekly videos
    if len(st.session_state.weekly_videos) > 1:
        st.markdown("<h3 style='margin:.8rem 0 .4rem;'>More this week</h3>", unsafe_allow_html=True)
        for v in st.session_state.weekly_videos[1:]:
            lvl = v.get("level", "Intermediate")
            badge_cls = {"Beginner": "badge-green", "Intermediate": "badge-yellow", "Advanced": "badge-red"}.get(lvl, "badge-yellow")
            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown(f"<img src='https://img.youtube.com/vi/{v['id']}/default.jpg' style='width:100%;border-radius:10px;aspect-ratio:16/9;object-fit:cover;'/>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div style='font-weight:600;font-size:.9rem;color:#1A1A2E;line-height:1.4;'>{v['title'][:55]}{'...' if len(v['title'])>55 else ''}</div><div style='font-size:.78rem;color:#8A8A9A;margin-top:2px;'>{v.get('channel','')} · <span class='badge {badge_cls}' style='font-size:.7rem;'>{lvl}</span></div>", unsafe_allow_html=True)
                if st.button("Study", key=f"home_v_{v['id']}", use_container_width=True):
                    with st.spinner("Loading..."):
                        t = get_transcript(v["id"])
                        if t:
                            st.session_state.yt_video_id = v["id"]
                            st.session_state.yt_video_title = v["title"]
                            st.session_state.yt_transcript = t
                            st.session_state.metric_videos_studied.add(v["id"])
                            st.session_state.page = "talk"
                            st.session_state.conv_video_id = v["id"]
                            st.session_state.conversation = []
                            st.query_params["page"] = "talk"
                            st.rerun()

    st.markdown("<div style='margin-top:1rem;'>", unsafe_allow_html=True)
    if st.button("🎙️ Start free conversation", use_container_width=True, key="home_free_talk"):
        st.session_state.page = "talk"
        st.session_state.conv_video_id = ""
        st.session_state.conversation = []
        st.query_params["page"] = "talk"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# PAGE: VIDEOS
# ═══════════════════════════════════════════════════════════════
elif page == "videos":
    st.markdown("<h1 style='padding-top:1.5rem;'>Videos</h1>", unsafe_allow_html=True)

    search_mode = st.radio("", ["📋 Curated list", "🔎 Search YouTube", "🔗 Paste link"], horizontal=True, label_visibility="collapsed")

    selected_vid_id = ""
    selected_vid_title = ""

    if search_mode == "🔎 Search YouTube":
        if not st.session_state.yt_api_key:
            st.info("Add your YouTube API Key in Settings to enable live search.")
        sq = st.text_input("Search:", placeholder="e.g. TED talk habits English")
        if st.button("Search", use_container_width=True) and sq:
            if st.session_state.yt_api_key:
                with st.spinner("Searching..."):
                    results = search_youtube(sq, max_results=6, yt_key=st.session_state.yt_api_key)
                    st.session_state["search_results"] = results if results else []
            else:
                kw = sq.lower()
                filtered = [v for v in CURATED_VIDEOS if kw in v["title"].lower() or kw in v.get("type", "").lower()]
                st.session_state["search_results"] = filtered if filtered else CURATED_VIDEOS[:6]
                st.info("Showing curated list (no YouTube API Key).")

        for v in st.session_state.get("search_results", []):
            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown(f"<img src='https://img.youtube.com/vi/{v['id']}/default.jpg' style='width:100%;border-radius:10px;aspect-ratio:16/9;object-fit:cover;'/>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div style='font-weight:600;font-size:.9rem;'>{v['title'][:55]}{'...' if len(v['title'])>55 else ''}</div><div style='font-size:.78rem;color:#8A8A9A;'>{v.get('channel','')}</div>", unsafe_allow_html=True)
                if st.button("▶ Study", key=f"sr_{v['id']}", use_container_width=True):
                    selected_vid_id = v["id"]; selected_vid_title = v["title"]

    elif search_mode == "🔗 Paste link":
        yt_url = st.text_input("YouTube URL:", placeholder="https://www.youtube.com/watch?v=...")
        if st.button("Load video", use_container_width=True) and yt_url.strip():
            vid = extract_video_id(yt_url.strip())
            if vid: selected_vid_id = vid; selected_vid_title = yt_url
            else: st.error("Invalid URL.")

    else:  # Curated
        lvl_filter = st.selectbox("Level:", ["All", "Beginner", "Intermediate", "Advanced"])
        type_filter = st.selectbox("Type:", ["All", "TED Talk", "TED-Ed", "BBC Learning", "Vlog", "Educational"])
        filtered = [
            v for v in CURATED_VIDEOS
            if (lvl_filter == "All" or v.get("level") == lvl_filter)
            and (type_filter == "All" or v.get("type") == type_filter)
        ]
        for v in filtered:
            lvl = v.get("level", "")
            badge_cls = {"Beginner": "badge-green", "Intermediate": "badge-yellow", "Advanced": "badge-red"}.get(lvl, "badge-yellow")
            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown(f"<img src='https://img.youtube.com/vi/{v['id']}/default.jpg' style='width:100%;border-radius:10px;aspect-ratio:16/9;object-fit:cover;'/>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div style='font-weight:600;font-size:.9rem;'>{v['title'][:55]}{'...' if len(v['title'])>55 else ''}</div><div style='font-size:.78rem;color:#8A8A9A;margin-top:2px;'>{v['channel']} · {v.get('duration','')} · <span class='badge {badge_cls}' style='font-size:.7rem;'>{lvl}</span></div>", unsafe_allow_html=True)
                if st.button("▶ Study", key=f"cur_{v['id']}", use_container_width=True):
                    selected_vid_id = v["id"]; selected_vid_title = v["title"]

    if selected_vid_id:
        with st.spinner("Loading transcript..."):
            t = get_transcript(selected_vid_id)
            if t:
                st.session_state.yt_video_id = selected_vid_id
                st.session_state.yt_video_title = selected_vid_title
                st.session_state.yt_transcript = t
                st.session_state.metric_videos_studied.add(selected_vid_id)
                st.session_state.page = "talk"
                st.session_state.conv_video_id = selected_vid_id
                st.session_state.conversation = []
                st.query_params["page"] = "talk"
                st.rerun()
            else:
                st.warning("No subtitles available. Try another video.")

# ═══════════════════════════════════════════════════════════════
# PAGE: TALK
# ═══════════════════════════════════════════════════════════════
elif page == "talk":
    has_video = bool(st.session_state.conv_video_id and st.session_state.yt_transcript)

    if has_video:
        title = st.session_state.yt_video_title
        vid_id = st.session_state.yt_video_id
        st.markdown(f"<div style='padding-top:1.2rem;'><h2 style='margin-bottom:.1rem;'>Talk about</h2><div style='color:#8A8A9A;font-size:.9rem;margin-bottom:.8rem;'>🎬 {title[:50]}{'...' if len(title)>50 else ''}</div></div>", unsafe_allow_html=True)
        with st.expander("▶ Watch video"):
            st.markdown(f'<iframe width="100%" height="220" src="https://www.youtube.com/embed/{vid_id}?cc_load_policy=1&cc_lang_pref=en" frameborder="0" allowfullscreen></iframe>', unsafe_allow_html=True)

        system = f"""You are an engaging English conversation partner for a Brazilian learner.
The student has just watched a YouTube video titled: "{title}".
Video transcript context: "{transcript_to_text(st.session_state.yt_transcript, 2000)}"

Your role:
- Have a natural flowing conversation about the video content
- Ask follow-up questions to keep the conversation going
- Gently model correct English (don't explicitly correct unless asked)
- Keep responses concise (2-4 sentences) — this is a spoken conversation
- Occasionally introduce vocabulary from the video naturally
- Be warm, encouraging, and curious"""
    else:
        st.markdown("<div style='padding-top:1.2rem;'><h2>Free conversation</h2><p style='color:#8A8A9A;font-size:.9rem;'>Practice English — talk about anything!</p></div>", unsafe_allow_html=True)
        system = """You are an engaging English conversation partner for a Brazilian learner.
Your role:
- Have natural, flowing conversations on any topic
- Keep responses concise (2-4 sentences) — this is a spoken conversation
- Gently model correct English without explicitly correcting
- Ask follow-up questions to keep the conversation alive
- Be warm, encouraging, and genuinely curious"""

    # Start conversation
    if not st.session_state.conversation:
        if st.session_state.api_key:
            with st.spinner("Starting conversation..."):
                if has_video:
                    opener = ask_claude_chat([], system + "\n\nStart the conversation with one engaging question about the video. Be warm and brief.")
                else:
                    opener = ask_claude_chat([], system + "\n\nGreet the student warmly and ask one simple question to start the conversation.")
                if opener:
                    st.session_state.conversation = [{"role": "assistant", "content": opener}]
                    st.session_state.metric_conversations += 1
                    st.session_state.conv_start_time = datetime.datetime.now()
                    if st.session_state.tts_enabled if hasattr(st.session_state, 'tts_enabled') else True:
                        pass
                    st.rerun()
        else:
            st.markdown("<a href='?page=settings' style='text-decoration:none;'><div class='card-coral' style='cursor:pointer;'><b style='color:#FF4B4B;'>🔑 Add your API Key</b><br><span style='color:#8A8A9A;font-size:.9rem;'>Tap here to go to Settings.</span></div></a>", unsafe_allow_html=True)

    # Chat history
    for msg in st.session_state.conversation:
        if msg["role"] == "user":
            st.markdown(f"<div class='bubble-user'>{msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bubble-ai'>{msg['content']}</div>", unsafe_allow_html=True)
            st.markdown(tts_btn(msg["content"], "🔊 Listen", 0.88), unsafe_allow_html=True)

    st.markdown("---")

    # Voice input
    input_mode = st.radio("", ["🎙️ Voice", "✍️ Type"], horizontal=True, label_visibility="collapsed")

    if input_mode == "🎙️ Voice":
        st.components.v1.html(STT_AUTO_HTML, height=220)
        voice_text = st.text_area("Transcribed text:", placeholder="transcri...", height=70, key="talk_voice", label_visibility="collapsed")
        if st.button("Send →", use_container_width=True, key="send_voice") and voice_text.strip():
            if not st.session_state.api_key:
                st.error("Go to Settings to add your API Key.")
            else:
                st.session_state.conversation.append({"role": "user", "content": voice_text.strip()})
                with st.spinner(""):
                    r = ask_claude_chat(st.session_state.conversation, system)
                    if r:
                        st.session_state.conversation.append({"role": "assistant", "content": r})
                        if st.session_state.conv_start_time:
                            elapsed = (datetime.datetime.now() - st.session_state.conv_start_time).seconds // 60
                            st.session_state.metric_minutes = max(st.session_state.metric_minutes, elapsed)
                        st.rerun()
    else:
        typed = st.text_area("Your message:", placeholder="Type in English...", height=85, key="talk_type", label_visibility="collapsed")
        c1, c2 = st.columns([3, 1])
        with c1:
            if st.button("Send →", use_container_width=True, key="send_typed") and typed.strip():
                if not st.session_state.api_key:
                    st.error("Go to Settings to add your API Key.")
                else:
                    st.session_state.conversation.append({"role": "user", "content": typed.strip()})
                    with st.spinner(""):
                        r = ask_claude_chat(st.session_state.conversation, system)
                        if r:
                            st.session_state.conversation.append({"role": "assistant", "content": r})
                            if st.session_state.conv_start_time:
                                elapsed = (datetime.datetime.now() - st.session_state.conv_start_time).seconds // 60
                                st.session_state.metric_minutes = max(st.session_state.metric_minutes, elapsed)
                            st.rerun()
        with c2:
            if st.button("🔄 New", use_container_width=True, key="new_conv"):
                st.session_state.conversation = []
                st.session_state.conv_start_time = None
                st.rerun()

    # Generate flashcards from this conversation
    if has_video and len(st.session_state.conversation) >= 6:
        st.markdown("---")
        if st.button("✨ Save flashcards from this video", use_container_width=True):
            if not st.session_state.api_key:
                st.error("Go to Settings to add your API Key.")
            else:
                with st.spinner("Generating flashcards..."):
                    cards = generate_flashcards_from_video(
                        st.session_state.yt_video_title,
                        transcript_to_text(st.session_state.yt_transcript)
                    )
                    if cards:
                        st.session_state.flashcard_decks["🎬 From Videos"].extend(cards)
                        st.success(f"✅ {len(cards)} flashcards added to 'From Videos' deck!")
                    else:
                        st.warning("Couldn't generate flashcards.")

# ═══════════════════════════════════════════════════════════════
# PAGE: CARDS (FLASHCARDS)
# ═══════════════════════════════════════════════════════════════
elif page == "cards":
    st.markdown("<h1 style='padding-top:1.5rem;'>Flashcards</h1>", unsafe_allow_html=True)
    fc_tab1, fc_tab2, fc_tab3 = st.tabs(["📚 Study", "🗂️ Manage", "✨ Generate"])

    with fc_tab1:
        deck_name = st.selectbox("Deck:", list(st.session_state.flashcard_decks.keys()), label_visibility="collapsed")
        deck = st.session_state.flashcard_decks[deck_name]
        due = get_due(deck)

        if not deck:
            st.markdown("<div class='card' style='text-align:center;padding:2rem;'><div style='font-size:2.5rem;'>📭</div><p style='color:#8A8A9A;'>No cards yet.<br>Generate from a video or add manually.</p></div>", unsafe_allow_html=True)
        elif not due:
            st.markdown("<div class='card' style='text-align:center;padding:2rem;'><div style='font-size:2.5rem;'>🎉</div><h3 style='color:#FF4B4B;'>All caught up!</h3><p style='color:#8A8A9A;'>Come back tomorrow!</p></div>", unsafe_allow_html=True)
        else:
            if st.session_state.fc_index >= len(due):
                st.session_state.fc_index = 0
            ci = due[st.session_state.fc_index]
            card = deck[ci]
            lvls = ["🌱 New", "🔵 Easy", "🟡 Medium", "🟠 Hard", "🟢 Mastered", "⭐ Expert"]

            st.progress(st.session_state.fc_index / len(due))
            st.markdown(f"<p style='text-align:right;color:#8A8A9A;font-size:.85rem;'>{st.session_state.fc_index+1}/{len(due)}</p>", unsafe_allow_html=True)

            st.markdown(f"""<div class='flashcard'>
              <div style='font-size:.7rem;color:#8A8A9A;letter-spacing:2px;text-transform:uppercase;margin-bottom:.8rem;'>🇺🇸 English</div>
              <div style='font-size:1.8rem;font-weight:800;color:#FF4B4B;margin-bottom:.4rem;'>{card["en"]}</div>
              <div style='font-size:.8rem;color:#8A8A9A;'>{lvls[min(card.get("level",0),5)]}</div>
            </div>""", unsafe_allow_html=True)

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("👁️ Show answer" if not st.session_state.fc_show_answer else "🙈 Hide", use_container_width=True):
                    st.session_state.fc_show_answer = not st.session_state.fc_show_answer; st.rerun()
            with col_b:
                st.markdown(tts_btn(card["en"], "🔊 Pronunciation", 0.8), unsafe_allow_html=True)

            if st.session_state.fc_show_answer:
                st.markdown(f"""<div class='card' style='text-align:center;border-color:#FF4B4B44;margin-top:.5rem;'>
                  <div style='font-size:.7rem;color:#FF4B4B;letter-spacing:2px;text-transform:uppercase;margin-bottom:.4rem;'>🇧🇷 Portuguese</div>
                  <div style='font-size:1.3rem;font-weight:700;margin-bottom:.6rem;'>{card["pt"]}</div>
                  <div style='font-size:.85rem;color:#8A8A9A;font-style:italic;'>"{card["example"]}"</div>
                </div>""", unsafe_allow_html=True)
                st.markdown(tts_btn(card["example"], "🔊 Example", 0.85), unsafe_allow_html=True)
                st.markdown("**How was it?**")
                r1, r2, r3, r4 = st.columns(4)
                for col, label, q in [(r1, "😰 Hard", 0), (r2, "🤔 OK", 2), (r3, "😊 Good", 3), (r4, "🚀 Easy", 5)]:
                    with col:
                        if st.button(label, use_container_width=True, key=f"fc_{q}_{deck_name}"):
                            st.session_state.flashcard_decks[deck_name] = update_review(
                                st.session_state.flashcard_decks[deck_name], ci, q)
                            st.session_state.fc_index += 1
                            st.session_state.fc_show_answer = False
                            st.session_state.metric_flashcards_reviewed += 1
                            st.rerun()

    with fc_tab2:
        st.markdown("### Add card")
        tgt = st.selectbox("Deck:", list(st.session_state.flashcard_decks.keys()), key="add_dk")
        fa1, fa2 = st.columns(2)
        with fa1: new_en = st.text_input("English")
        with fa2: new_pt = st.text_input("Portuguese")
        new_ex = st.text_input("Example sentence")
        if st.button("Add card", use_container_width=True) and new_en and new_pt:
            st.session_state.flashcard_decks[tgt].append({"en": new_en, "pt": new_pt, "example": new_ex or f"Example with '{new_en}'.", "level": 0, "next_review": ""})
            st.success(f"✅ '{new_en}' added!")
        st.markdown("### New deck")
        new_dk = st.text_input("Deck name:")
        if st.button("Create deck", use_container_width=True) and new_dk:
            if new_dk not in st.session_state.flashcard_decks:
                st.session_state.flashcard_decks[new_dk] = []; st.success(f"'{new_dk}' created!")
            else:
                st.warning("Deck already exists.")

    with fc_tab3:
        st.markdown("### Generate from video")
        if st.session_state.yt_video_id and st.session_state.yt_transcript:
            st.markdown(f"<div class='card-coral'>🎬 <b>{st.session_state.yt_video_title[:50]}</b></div>", unsafe_allow_html=True)
            if st.button("✨ Generate flashcards from last video", use_container_width=True):
                if not st.session_state.api_key:
                    st.error("Go to Settings to add your API Key.")
                else:
                    with st.spinner("Generating..."):
                        cards = generate_flashcards_from_video(
                            st.session_state.yt_video_title,
                            transcript_to_text(st.session_state.yt_transcript)
                        )
                        if cards:
                            st.session_state.flashcard_decks["🎬 From Videos"].extend(cards)
                            st.success(f"✅ {len(cards)} cards added to 'From Videos'!")
                        else:
                            st.warning("Couldn't generate. Try again.")
        else:
            st.info("Study a video first to generate flashcards from it.")

        st.markdown("### Generate by topic")
        gt = st.text_input("Topic:", placeholder="e.g. phrasal verbs, travel, technology...")
        gcols = st.columns(2)
        with gcols[0]: gqty = st.slider("Cards:", 3, 15, 8)
        with gcols[1]: glvl = st.select_slider("Level:", ["Beginner", "Intermediate", "Advanced"], value="Intermediate")
        gdk = st.selectbox("Add to deck:", list(st.session_state.flashcard_decks.keys()), key="gdk")
        if st.button("🤖 Generate", use_container_width=True):
            if not st.session_state.api_key: st.error("Add your API Key first.")
            elif not gt.strip(): st.warning("Enter a topic.")
            else:
                with st.spinner("Generating..."):
                    r = ask_claude(f'Create {gqty} English flashcards for Brazilian {glvl} level about: {gt}\nReturn ONLY valid JSON array:\n[{{"en":"word","pt":"tradução","example":"Sentence."}}]')
                    if r:
                        try:
                            m = re.search(r'\[.*\]', r, re.DOTALL)
                            if m:
                                cards = json.loads(m.group()); added = 0
                                for c in cards:
                                    if "en" in c and "pt" in c:
                                        st.session_state.flashcard_decks[gdk].append({"en": c["en"], "pt": c["pt"], "example": c.get("example", ""), "level": 0, "next_review": ""})
                                        added += 1
                                st.success(f"✅ {added} cards added!"); st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

# ═══════════════════════════════════════════════════════════════
# PAGE: PROGRESS
# ═══════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════
# PAGE: SETTINGS (replaces hidden sidebar — API keys + progress)
# ═══════════════════════════════════════════════════════════════
elif page == "settings":
    st.markdown("<div style='padding-top:1.5rem;'></div>", unsafe_allow_html=True)

    # App logo / header
    st.markdown("""
    <div style='text-align:center;padding:1.5rem 0 1rem;'>
      <div style='width:64px;height:64px;background:#FF4B4B;border-radius:18px;margin:0 auto .8rem;display:flex;align-items:center;justify-content:center;'>
        <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="22"/></svg>
      </div>
      <div style='font-size:1.4rem;font-weight:800;color:#1A1A2E;'>FluentAI</div>
      <div style='font-size:.85rem;color:#8A8A9A;'>English learning with AI</div>
    </div>
    """, unsafe_allow_html=True)

    # API Keys section
    st.markdown("<div style='font-weight:700;font-size:1rem;margin:.8rem 0 .4rem;'>API Keys</div>", unsafe_allow_html=True)

    st.markdown("<div class='card' style='padding:1.3rem;'>", unsafe_allow_html=True)
    st.markdown("<div style='font-weight:600;font-size:.9rem;margin-bottom:.2rem;'>Anthropic (Claude AI)</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:.8rem;color:#8A8A9A;margin-bottom:.5rem;'>Required for conversations and flashcard generation</div>", unsafe_allow_html=True)
    api_in = st.text_input(
        "anthropic_key",
        value=st.session_state.api_key,
        type="password",
        placeholder="sk-ant-api...",
        label_visibility="collapsed"
    )
    if api_in != st.session_state.api_key:
        st.session_state.api_key = api_in
        st.rerun()
    if st.session_state.api_key:
        st.markdown("<div style='color:#22C55E;font-size:.82rem;font-weight:600;margin-top:.3rem;'>✓ Connected</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='color:#FF4B4B;font-size:.82rem;font-weight:600;margin-top:.3rem;'>Not set</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card' style='padding:1.3rem;'>", unsafe_allow_html=True)
    st.markdown("<div style='font-weight:600;font-size:.9rem;margin-bottom:.2rem;'>YouTube Data API <span style='background:#f3f4f6;color:#8A8A9A;border-radius:6px;padding:1px 7px;font-size:.75rem;font-weight:500;'>Optional</span></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:.8rem;color:#8A8A9A;margin-bottom:.5rem;'>Enables live YouTube search. Without it, curated videos are used.</div>", unsafe_allow_html=True)
    yt_in = st.text_input(
        "yt_key",
        value=st.session_state.yt_api_key,
        type="password",
        placeholder="AIza...",
        label_visibility="collapsed"
    )
    if yt_in != st.session_state.yt_api_key:
        st.session_state.yt_api_key = yt_in
        st.rerun()
    if st.session_state.yt_api_key:
        st.markdown("<div style='color:#22C55E;font-size:.82rem;font-weight:600;margin-top:.3rem;'>✓ Connected</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Progress section
    st.markdown("<div style='font-weight:700;font-size:1rem;margin:1.2rem 0 .4rem;'>Your Progress</div>", unsafe_allow_html=True)

    s1, s2 = st.columns(2)
    s3, s4 = st.columns(2)
    with s1:
        st.markdown(f"<div class='card' style='text-align:center;padding:1.1rem .8rem;'><div style='font-size:1.6rem;font-weight:800;color:#FF4B4B;'>{st.session_state.metric_conversations}</div><div style='font-size:.78rem;color:#8A8A9A;font-weight:500;'>Conversations</div></div>", unsafe_allow_html=True)
    with s2:
        st.markdown(f"<div class='card' style='text-align:center;padding:1.1rem .8rem;'><div style='font-size:1.6rem;font-weight:800;color:#FF4B4B;'>{st.session_state.metric_minutes}m</div><div style='font-size:.78rem;color:#8A8A9A;font-weight:500;'>Minutes practiced</div></div>", unsafe_allow_html=True)
    with s3:
        st.markdown(f"<div class='card' style='text-align:center;padding:1.1rem .8rem;'><div style='font-size:1.6rem;font-weight:800;color:#FF4B4B;'>{st.session_state.metric_flashcards_reviewed}</div><div style='font-size:.78rem;color:#8A8A9A;font-weight:500;'>Cards reviewed</div></div>", unsafe_allow_html=True)
    with s4:
        st.markdown(f"<div class='card' style='text-align:center;padding:1.1rem .8rem;'><div style='font-size:1.6rem;font-weight:800;color:#FF4B4B;'>{len(st.session_state.metric_videos_studied)}</div><div style='font-size:.78rem;color:#8A8A9A;font-weight:500;'>Videos studied</div></div>", unsafe_allow_html=True)

    # Flashcard decks
    st.markdown("<div style='font-weight:700;font-size:1rem;margin:1.2rem 0 .4rem;'>Flashcard decks</div>", unsafe_allow_html=True)
    today = datetime.date.today().isoformat()
    has_decks = False
    for dn, cards in st.session_state.flashcard_decks.items():
        total = len(cards)
        if total == 0: continue
        has_decks = True
        due_n = sum(1 for c in cards if not c.get("next_review") or c["next_review"] <= today)
        mastered = sum(1 for c in cards if c.get("level", 0) >= 4)
        st.markdown(f"""<div class='card' style='padding:1rem 1.2rem;'>
          <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:.5rem;'>
            <span style='font-weight:600;font-size:.9rem;'>{dn}</span>
            <span style='font-size:.8rem;color:#8A8A9A;'>{total} cards</span>
          </div>
          <div style='display:flex;gap:1rem;margin-bottom:.5rem;'>
            <span style='font-size:.8rem;color:{"#FF4B4B" if due_n>0 else "#22C55E"};font-weight:600;'>{due_n} to review</span>
            <span style='font-size:.8rem;color:#22C55E;font-weight:600;'>{mastered} mastered</span>
          </div>
        </div>""", unsafe_allow_html=True)
        st.progress(mastered / total)
    if not has_decks:
        st.markdown("<div style='color:#8A8A9A;font-size:.9rem;'>No cards yet. Study a video to generate some!</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1.2rem;'></div>", unsafe_allow_html=True)
    if st.button("Reset all progress", use_container_width=True):
        st.session_state.metric_conversations = 0
        st.session_state.metric_minutes = 0
        st.session_state.metric_flashcards_reviewed = 0
        st.session_state.metric_videos_studied = set()
        st.rerun()
