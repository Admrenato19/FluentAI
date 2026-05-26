import streamlit as st
import anthropic
import json, re, datetime, random

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
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap');
:root{--bg:#0D0D0F;--surface:#16161A;--surface2:#1E1E24;--accent:#E8FF47;--accent3:#47CFFF;--text:#F0EFE9;--muted:#7A7A8A;--border:#2A2A35;--radius:16px;}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;background-color:var(--bg);color:var(--text);}
.stApp{background-color:var(--bg);}
[data-testid="stSidebar"]{background-color:var(--surface)!important;border-right:1px solid var(--border);}
[data-testid="stSidebar"] *{color:var(--text)!important;}
#MainMenu,footer,header{visibility:hidden;}
.stButton>button{background:var(--accent)!important;color:var(--bg)!important;border:none!important;border-radius:8px!important;font-family:'Syne',sans-serif!important;font-weight:700!important;padding:0.6rem 1.5rem!important;transition:all .2s!important;}
.stButton>button:hover{transform:translateY(-2px);box-shadow:0 6px 20px rgba(232,255,71,.3)!important;}
.stTextInput>div>div>input,.stTextArea>div>div>textarea,.stSelectbox>div>div{background-color:var(--surface2)!important;border:1px solid var(--border)!important;border-radius:10px!important;color:var(--text)!important;}
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:1.5rem;margin-bottom:1rem;transition:border-color .2s;}
.card:hover{border-color:var(--accent);}
.card-accent{background:linear-gradient(135deg,#1a1a20,#1e1e2a);border:1px solid var(--accent);border-radius:var(--radius);padding:1.5rem;margin-bottom:1rem;}
.card-blue{background:linear-gradient(135deg,#0d1a2a,#0d2035);border:1px solid #47CFFF55;border-radius:var(--radius);padding:1.5rem;margin-bottom:1rem;}
h1,h2,h3{font-family:'Syne',sans-serif!important;font-weight:800!important;color:var(--text)!important;}
.muted-text{color:var(--muted);font-size:.9rem;}
.tag{display:inline-block;background:var(--surface2);border:1px solid var(--border);border-radius:20px;padding:3px 12px;font-size:.8rem;color:var(--muted);margin:2px;}
.msg-user{background:var(--surface2);border-radius:16px 16px 4px 16px;padding:1rem 1.2rem;margin:.5rem 0;border-left:3px solid var(--accent);max-width:85%;margin-left:auto;}
.msg-ai{background:var(--surface);border-radius:16px 16px 16px 4px;padding:1rem 1.2rem;margin:.5rem 0;border-left:3px solid var(--accent3);max-width:85%;}
.flashcard{background:linear-gradient(145deg,var(--surface),var(--surface2));border:2px solid var(--accent);border-radius:20px;padding:3rem 2rem;text-align:center;min-height:200px;display:flex;flex-direction:column;align-items:center;justify-content:center;transition:all .3s;}
.flashcard:hover{transform:scale(1.01);box-shadow:0 10px 40px rgba(232,255,71,.15);}
.stProgress>div>div>div{background-color:var(--accent)!important;}
[data-testid="stMetric"]{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:1rem;}
[data-testid="stMetricValue"]{color:var(--accent)!important;font-family:'Syne',sans-serif!important;}
.stTabs [data-baseweb="tab-list"]{background:var(--surface)!important;border-radius:10px!important;gap:4px;}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:var(--muted)!important;border-radius:8px!important;}
.stTabs [aria-selected="true"]{background:var(--accent)!important;color:var(--bg)!important;font-weight:600!important;}
.vid-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);overflow:hidden;transition:all .2s;cursor:pointer;}
.vid-card:hover{border-color:var(--accent);transform:translateY(-2px);}
.vid-thumb{width:100%;aspect-ratio:16/9;object-fit:cover;}
.vid-meta{padding:.8rem 1rem;}
.badge{display:inline-block;border-radius:20px;padding:2px 10px;font-size:.75rem;font-weight:600;}
.badge-green{background:#47CFFF22;color:#47CFFF;border:1px solid #47CFFF44;}
.badge-yellow{background:#E8FF4722;color:#E8FF47;border:1px solid #E8FF4744;}
.badge-red{background:#FF6B6B22;color:#FF6B6B;border:1px solid #FF6B6B44;}
.badge-purple{background:#A78BFA22;color:#A78BFA;border:1px solid #A78BFA44;}
.weekly-badge{background:linear-gradient(90deg,#E8FF47,#47CFFF);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-family:'Syne',sans-serif;font-weight:800;font-size:1.1rem;}
iframe{border-radius:12px;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# WEB SPEECH API
# ─────────────────────────────────────────────────────────────────
st.components.v1.html("""
<script>
function fluentSpeak(text,rate=0.85){
  if(!('speechSynthesis' in window))return;
  window.speechSynthesis.cancel();
  const u=new SpeechSynthesisUtterance(text);
  u.lang='en-US';u.rate=rate;u.pitch=1.0;
  const voices=window.speechSynthesis.getVoices();
  const pref=voices.find(v=>v.lang.startsWith('en')&&(v.name.includes('Google')||v.name.includes('Natural')));
  if(pref)u.voice=pref;
  window.speechSynthesis.speak(u);
}
window.fluentSpeak=fluentSpeak;
</script>
""", height=0)

def tts_btn(text, label="🔊 Ouvir", rate=0.85):
    safe = text.replace("'","\\'").replace("\n"," ").replace('"','\\"')[:500]
    return f'<button onclick="fluentSpeak(\'{safe}\',{rate})" style="background:#E8FF47;color:#0D0D0F;border:none;border-radius:8px;padding:8px 18px;font-weight:700;cursor:pointer;font-size:.85rem;font-family:Syne,sans-serif;margin:4px 4px 4px 0;">{label}</button>'

STT_HTML = """
<div style="display:flex;flex-direction:column;gap:10px;">
  <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
    <button id="btn-start" onclick="startRec()" style="background:#E8FF47;color:#0D0D0F;border:none;border-radius:8px;padding:9px 18px;font-weight:700;cursor:pointer;font-family:Syne,sans-serif;">🎙️ Gravar</button>
    <button id="btn-stop" onclick="stopRec()" disabled style="background:#FF6B6B;color:#fff;border:none;border-radius:8px;padding:9px 18px;font-weight:700;cursor:pointer;font-family:Syne,sans-serif;opacity:.4;">⏹ Parar</button>
    <span id="rec-st" style="color:#7A7A8A;font-size:.85rem;">Clique em Gravar e fale em inglês</span>
  </div>
  <div id="rec-out" style="background:#1E1E24;border:1px solid #2A2A35;border-radius:10px;padding:.8rem;min-height:55px;color:#F0EFE9;font-size:1rem;line-height:1.6;"></div>
  <p style="color:#7A7A8A;font-size:.8rem;margin:0;">💡 Após parar, copie o texto e cole no campo abaixo.</p>
</div>
<script>
let rec=null,final='';
function startRec(){
  const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
  if(!SR){document.getElementById('rec-st').innerText='❌ Use Chrome.';return;}
  rec=new SR();rec.lang='en-US';rec.interimResults=true;rec.continuous=true;final='';
  rec.onstart=()=>{
    document.getElementById('btn-start').disabled=true;
    document.getElementById('btn-stop').disabled=false;
    document.getElementById('btn-stop').style.opacity='1';
    document.getElementById('rec-st').innerHTML='<span style="color:#FF6B6B">● Gravando...</span>';
    document.getElementById('rec-out').innerText='';
  };
  rec.onresult=(e)=>{
    let tmp='';
    for(let i=e.resultIndex;i<e.results.length;i++){
      if(e.results[i].isFinal)final+=e.results[i][0].transcript+' ';
      else tmp+=e.results[i][0].transcript;
    }
    document.getElementById('rec-out').innerText=final+tmp;
  };
  rec.onend=()=>{
    document.getElementById('btn-start').disabled=false;
    document.getElementById('btn-stop').disabled=true;
    document.getElementById('btn-stop').style.opacity='.4';
    document.getElementById('rec-st').innerText='Gravação encerrada — copie o texto acima.';
    if(final.trim())navigator.clipboard.writeText(final.trim()).catch(()=>{});
    document.getElementById('rec-out').style.border='1px solid #E8FF47';
  };
  rec.onerror=(e)=>{document.getElementById('rec-st').innerText='❌ Erro: '+e.error;};
  rec.start();
}
function stopRec(){if(rec)rec.stop();}
</script>
"""

# ─────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────
for k,v in {
    "api_key":"","yt_api_key":"","conversation":[],"xp":0,"streak":0,
    "fc_index":0,"fc_show_answer":False,"flashcard_decks":None,
    "yt_transcript":[],"yt_video_id":"","yt_video_title":"",
    "tts_enabled":True,"weekly_videos":[],"weekly_generated_date":"",
    "selected_video":None,
}.items():
    if k not in st.session_state: st.session_state[k]=v

# ─────────────────────────────────────────────────────────────────
# CLAUDE API
# ─────────────────────────────────────────────────────────────────
def ask_claude(prompt,max_tokens=1000):
    try:
        c=anthropic.Anthropic(api_key=st.session_state.api_key)
        m=c.messages.create(model="claude-sonnet-4-20250514",max_tokens=max_tokens,
                             messages=[{"role":"user","content":prompt}])
        return m.content[0].text
    except anthropic.AuthenticationError: st.error("❌ API Key Claude inválida.")
    except anthropic.RateLimitError: st.error("⚠️ Rate limit. Aguarde.")
    except Exception as e: st.error(f"Erro Claude: {e}")
    return ""

def ask_claude_chat(messages,system,max_tokens=800):
    try:
        c=anthropic.Anthropic(api_key=st.session_state.api_key)
        m=c.messages.create(model="claude-sonnet-4-20250514",max_tokens=max_tokens,
                             system=system,messages=messages)
        return m.content[0].text
    except anthropic.AuthenticationError: st.error("❌ API Key Claude inválida.")
    except anthropic.RateLimitError: st.error("⚠️ Rate limit. Aguarde.")
    except Exception as e: st.error(f"Erro Claude: {e}")
    return ""

# ─────────────────────────────────────────────────────────────────
# YOUTUBE HELPERS
# ─────────────────────────────────────────────────────────────────
def extract_video_id(url):
    for p in [r'v=([^&\s]+)',r'youtu\.be/([^?\s]+)',r'embed/([^?\s]+)']:
        m=re.search(p,url)
        if m: return m.group(1)
    return ""

def get_transcript(video_id):
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        ytt=YouTubeTranscriptApi()
        t=ytt.fetch(video_id)
        return [{"text":s.text,"start":s.start,"duration":s.duration} for s in t]
    except Exception:
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            ytt=YouTubeTranscriptApi()
            for t in ytt.list(video_id):
                f=t.fetch()
                return [{"text":s.text,"start":s.start,"duration":s.duration} for s in f]
        except Exception as e2:
            st.error(f"Sem legendas disponíveis: {e2}")
            return []

def transcript_to_segments(transcript,chunk=4):
    segs=[]
    for i in range(0,len(transcript),chunk):
        g=transcript[i:i+chunk]
        segs.append({"text":" ".join(s["text"].replace("\n"," ") for s in g),"start":int(g[0]["start"])})
    return segs

def transcript_to_text(transcript,max_chars=2500):
    full=" ".join(s["text"].replace("\n"," ") for s in transcript)
    return full[:max_chars]+("..." if len(full)>max_chars else "")

def search_youtube(query,max_results=6,yt_key=None):
    """Search YouTube using Data API v3."""
    if not yt_key:
        return []
    try:
        from googleapiclient.discovery import build
        yt=build("youtube","v3",developerKey=yt_key)
        res=yt.search().list(
            q=query,part="snippet",type="video",
            maxResults=max_results,
            videoCaptionKey="closedCaption",  # prefer captioned
            relevanceLanguage="en",
            safeSearch="strict",
        ).execute()
        videos=[]
        for item in res.get("items",[]):
            vid=item["id"]["videoId"]
            snip=item["snippet"]
            videos.append({
                "id":vid,
                "title":snip["title"],
                "channel":snip["channelTitle"],
                "description":snip["description"][:120],
                "thumbnail":snip["thumbnails"]["medium"]["url"],
                "url":f"https://www.youtube.com/watch?v={vid}",
            })
        return videos
    except Exception as e:
        st.warning(f"Busca YouTube falhou: {e}")
        return []

def get_video_details(video_ids, yt_key):
    """Get duration and stats for videos."""
    if not yt_key or not video_ids: return {}
    try:
        from googleapiclient.discovery import build
        yt=build("youtube","v3",developerKey=yt_key)
        res=yt.videos().list(part="contentDetails,statistics",id=",".join(video_ids)).execute()
        details={}
        for item in res.get("items",[]):
            dur=item["contentDetails"]["duration"]  # ISO 8601 e.g. PT4M30S
            m=re.search(r'PT(?:(\d+)M)?(?:(\d+)S)?',dur)
            mins=int(m.group(1) or 0) if m else 0
            secs=int(m.group(2) or 0) if m else 0
            details[item["id"]]={"duration":f"{mins}:{secs:02d}","views":int(item.get("statistics",{}).get("viewCount",0))}
        return details
    except: return {}

# ─────────────────────────────────────────────────────────────────
# CURATED VIDEO LIST (fallback when no YouTube API key)
# ─────────────────────────────────────────────────────────────────
CURATED_VIDEOS = [
    # TED Talks
    {"id":"_ZBKX-6Gz6A","title":"How language shapes the way we think","channel":"TED","thumbnail":"https://img.youtube.com/vi/_ZBKX-6Gz6A/mqdefault.jpg","level":"Intermediário","type":"TED Talk","duration":"14:03"},
    {"id":"8S0FDjFBj8o","title":"The linguistic genius of babies","channel":"TED","thumbnail":"https://img.youtube.com/vi/8S0FDjFBj8o/mqdefault.jpg","level":"Intermediário","type":"TED Talk","duration":"10:18"},
    {"id":"Unzc731iCUY","title":"Think like a coder — TED-Ed","channel":"TED-Ed","thumbnail":"https://img.youtube.com/vi/Unzc731iCUY/mqdefault.jpg","level":"Básico","type":"TED-Ed","duration":"5:37"},
    {"id":"arj7oStGLkU","title":"TED's secret to great public speaking","channel":"TED","thumbnail":"https://img.youtube.com/vi/arj7oStGLkU/mqdefault.jpg","level":"Intermediário","type":"TED Talk","duration":"7:35"},
    {"id":"eIho2S0ZahI","title":"The power of introverts","channel":"TED","thumbnail":"https://img.youtube.com/vi/eIho2S0ZahI/mqdefault.jpg","level":"Avançado","type":"TED Talk","duration":"19:04"},
    # BBC / English Learning
    {"id":"4bFYmMqq_Hs","title":"6 Minute English — Technology","channel":"BBC Learning English","thumbnail":"https://img.youtube.com/vi/4bFYmMqq_Hs/mqdefault.jpg","level":"Básico","type":"BBC Learning","duration":"6:00"},
    {"id":"YsA3PK8bQd8","title":"English at Work — Job interview","channel":"BBC Learning English","thumbnail":"https://img.youtube.com/vi/YsA3PK8bQd8/mqdefault.jpg","level":"Intermediário","type":"BBC Learning","duration":"5:48"},
    # Vlogs / day-to-day
    {"id":"BMukniszEiA","title":"A day in the life of a New Yorker","channel":"Nathaniel Drew","thumbnail":"https://img.youtube.com/vi/BMukniszEiA/mqdefault.jpg","level":"Intermediário","type":"Vlog","duration":"11:24"},
    {"id":"H14bBuluwB8","title":"How I learned English fluently","channel":"Nathaniel Drew","thumbnail":"https://img.youtube.com/vi/H14bBuluwB8/mqdefault.jpg","level":"Básico","type":"Vlog","duration":"9:41"},
    # Crash Course / Educational
    {"id":"fmaG9EAZe90","title":"How to argue — Philosophical reasoning","channel":"Crash Course","thumbnail":"https://img.youtube.com/vi/fmaG9EAZe90/mqdefault.jpg","level":"Avançado","type":"Educacional","duration":"9:52"},
    {"id":"NiECCdXCPeE","title":"The science of sleep","channel":"TED-Ed","thumbnail":"https://img.youtube.com/vi/NiECCdXCPeE/mqdefault.jpg","level":"Intermediário","type":"TED-Ed","duration":"4:42"},
    {"id":"GK_vRtHJZu4","title":"Why do we dream?","channel":"TED-Ed","thumbnail":"https://img.youtube.com/vi/GK_vRtHJZu4/mqdefault.jpg","level":"Básico","type":"TED-Ed","duration":"5:46"},
]

SEARCH_PRESETS = {
    "🎤 TED Talks intermediário": "TED talk English learning intermediate subtitles",
    "📺 BBC Learning English": "BBC Learning English 6 minute 2024",
    "🎬 Movie scenes English": "famous movie scenes English subtitles learning",
    "📰 News English simples": "VOA Learning English news slow 2024",
    "🧠 Ciência em inglês": "TED-Ed science English subtitles",
    "💼 Business English": "business English professional communication BBC",
    "🌍 Cultura americana": "American culture daily life English vlog",
    "🎭 Comédia / sitcom": "Friends English learning scene subtitles",
}

# Weekly suggestion logic
def get_week_key():
    today=datetime.date.today()
    return f"{today.year}-W{today.isocalendar()[1]}"

def generate_weekly_curated():
    """Pick 4 varied curated videos for this week."""
    random.seed(int(get_week_key().replace("-W","")))
    types=["TED Talk","TED-Ed","BBC Learning","Vlog","Educacional"]
    selected=[]
    used_types=set()
    pool=CURATED_VIDEOS.copy()
    random.shuffle(pool)
    for v in pool:
        if v["type"] not in used_types or len(selected)<4:
            selected.append(v)
            used_types.add(v["type"])
            if len(selected)==4: break
    return selected

# ─────────────────────────────────────────────────────────────────
# DATA: scenes, personas, flashcards
# ─────────────────────────────────────────────────────────────────
SAMPLE_SCENES = {
    "🦁 Rei Leão — 'Remember who you are'": {"en":"You have forgotten who you are and so have forgotten me. Look inside yourself, Simba. You are more than what you have become. You must take your place in the Circle of Life.","pt":"Você esqueceu quem você é e, por isso, me esqueceu também. Olhe dentro de si mesmo, Simba.","vocab":["forgotten","inside yourself","Circle of Life"],"level":"Intermediário","tips":"Contrações: 'you have'→'you've'. Fale grave e pausado."},
    "🕷️ Homem-Aranha — 'Great power'": {"en":"With great power comes great responsibility. This is my gift, my curse. Who am I? I'm Spider-Man.","pt":"Com grande poder vem grande responsabilidade. Esse é meu dom, minha maldição.","vocab":["responsibility","gift","curse"],"level":"Básico","tips":"Frase rítmica — repita 5x acelerando."},
    "🤖 Interestelar — Cooper": {"en":"We used to look up at the sky and wonder at our place in the stars. Now we just look down and worry about our place in the dirt.","pt":"Costumávamos olhar para o céu e nos perguntar sobre nosso lugar nas estrelas.","vocab":["wonder","place in the stars","dirt"],"level":"Avançado","tips":"Ritmo melancólico e pausado. Bom para entonação."},
    "🧠 Breaking Bad — 'I am the danger'": {"en":"I am not in danger, Skyler. I am the danger. A guy opens his door and gets shot, and you think that of me? No. I am the one who knocks.","pt":"Eu não estou em perigo, Skyler. Eu sou o perigo.","vocab":["danger","the one who knocks"],"level":"Intermediário","tips":"Pause antes de 'I am the danger'. Fale devagar."},
}

PERSONAS = {
    "🎓 Prof. Alex — Paciente":{"desc":"Didático, corrige com calma.","system":"You are Professor Alex, a patient English teacher for Brazilian intermediate learners. Correct errors gently. Keep responses concise (3-5 sentences).","voice_rate":0.80},
    "🎬 Sam — Cinéfilo":{"desc":"Usa referências de filmes, casual e divertido.","system":"You are Sam, a movie fan teaching English through pop culture. Reference movies naturally. Max 4 sentences.","voice_rate":0.90},
    "💼 Jordan — Business":{"desc":"Inglês profissional e corporativo.","system":"You are Jordan, a business English coach. Focus on professional vocabulary. Keep responses practical.","voice_rate":0.85},
    "🌍 Maya — Conversação livre":{"desc":"Papo informal como uma amiga nativa.","system":"You are Maya, a native English speaker in casual conversation. Be natural and friendly. Model correct English subtly.","voice_rate":0.95},
}

TOPIC_STARTERS = {
    "🎬 Filmes e séries":"Let's talk about movies! What's the last thing you watched?",
    "✈️ Viagens":"Have you ever traveled abroad, or somewhere you'd love to visit?",
    "🍕 Comida":"What's your favorite meal? Do you like trying new cuisines?",
    "💼 Trabalho":"Tell me about your work. What are your career goals?",
    "🎮 Hobbies":"What do you do in your free time?",
}

DEFAULT_DECKS = {
    "🎬 Cinema & Séries":[
        {"en":"plot twist","pt":"reviravolta na trama","example":"The plot twist shocked everyone.","level":0,"next_review":""},
        {"en":"binge-watch","pt":"maratonar séries","example":"I binge-watched the whole season.","level":0,"next_review":""},
        {"en":"cliffhanger","pt":"final suspenso","example":"The finale ended on a cliffhanger!","level":0,"next_review":""},
        {"en":"spoiler","pt":"revelar o enredo","example":"Don't spoil the movie!","level":0,"next_review":""},
        {"en":"blockbuster","pt":"grande sucesso de bilheteria","example":"Avengers is a massive blockbuster.","level":0,"next_review":""},
        {"en":"sequel","pt":"continuação","example":"The sequel was even better.","level":0,"next_review":""},
    ],
    "💼 Dia a Dia":[
        {"en":"hang out","pt":"sair com amigos","example":"Want to hang out this weekend?","level":0,"next_review":""},
        {"en":"figure out","pt":"descobrir/resolver","example":"I can't figure out this problem.","level":0,"next_review":""},
        {"en":"give up","pt":"desistir","example":"Don't give up on your dreams!","level":0,"next_review":""},
        {"en":"deal with","pt":"lidar com","example":"I have to deal with a lot of stress.","level":0,"next_review":""},
        {"en":"catch up","pt":"colocar o papo em dia","example":"Let's catch up over coffee!","level":0,"next_review":""},
    ],
    "🧠 Gramática":[
        {"en":"I used to + verb","pt":"Eu costumava (passado habitual)","example":"I used to watch cartoons every morning.","level":0,"next_review":""},
        {"en":"Have you ever...?","pt":"Você já...? (present perfect)","example":"Have you ever been to New York?","level":0,"next_review":""},
        {"en":"I wish + past","pt":"Queria que... (desejo irreal)","example":"I wish I spoke perfect English.","level":0,"next_review":""},
    ],
}
INTERVAL_DAYS=[0,1,3,7,14,30]

if st.session_state.flashcard_decks is None:
    st.session_state.flashcard_decks={k:[dict(c) for c in v] for k,v in DEFAULT_DECKS.items()}

def get_due(deck):
    today=datetime.date.today().isoformat()
    return [i for i,c in enumerate(deck) if not c.get("next_review") or c["next_review"]<=today]

def update_review(deck,idx,q):
    lvl=deck[idx].get("level",0)
    lvl=min(lvl+1,5) if q>=3 else max(lvl-1,0)
    deck[idx]["level"]=lvl
    deck[idx]["next_review"]=(datetime.date.today()+datetime.timedelta(days=INTERVAL_DAYS[lvl])).isoformat()
    return deck

# ─────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div style='font-family:Syne,sans-serif;font-size:1.6rem;font-weight:800;color:#E8FF47;padding:1rem 0 .3rem;'>🎬 FluentAI</div>", unsafe_allow_html=True)
    st.markdown("<div style='color:#7A7A8A;font-size:.85rem;margin-bottom:1rem;'>Inglês com IA + Cinema</div>", unsafe_allow_html=True)
    st.divider()
    c1,c2=st.columns(2)
    with c1: st.metric("⚡ XP",st.session_state.xp)
    with c2: st.metric("🔥 Streak",f"{st.session_state.streak}d")
    st.divider()
    st.markdown("**🔑 API Keys**")
    api_in=st.text_input("Anthropic Key",value=st.session_state.api_key,type="password",placeholder="sk-ant-...",label_visibility="collapsed")
    if api_in: st.session_state.api_key=api_in; st.success("✓ Claude OK")
    yt_in=st.text_input("YouTube Data API Key (opcional)",value=st.session_state.yt_api_key,type="password",placeholder="AIza...",label_visibility="collapsed")
    if yt_in: st.session_state.yt_api_key=yt_in; st.success("✓ YouTube API OK")
    st.markdown("<div class='muted-text'>Sem a YouTube API key, usamos uma lista curada de vídeos incríveis.</div>",unsafe_allow_html=True)
    st.divider()
    st.session_state.tts_enabled=st.toggle("🔊 Professor fala (TTS)",value=st.session_state.tts_enabled)
    st.markdown("<div class='muted-text'>Requer Chrome para melhor resultado.</div>",unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<div style='padding:1.5rem 0 .5rem;'>
  <h1 style='font-size:2rem;margin:0;'>Inglês com <span style='color:#E8FF47;'>IA + Cinema</span></h1>
  <p style='color:#7A7A8A;margin-top:.3rem;'>Sugestões semanais, YouTube, voz e flashcards</p>
</div>""", unsafe_allow_html=True)

tab_weekly,tab_search,tab_shadow,tab_conv,tab_flash,tab_prog = st.tabs([
    "🌟 Semana","🔍 Buscar","🎬 Shadowing","🤖 Conversação","🃏 Flashcards","📊 Progresso"
])

# ═══════════════════════════════════════════════════════════════
# TAB 1 — SUGESTÕES SEMANAIS
# ═══════════════════════════════════════════════════════════════
with tab_weekly:
    st.markdown("<h2>🌟 Vídeos da Semana</h2>",unsafe_allow_html=True)

    week=get_week_key()
    st.markdown(f"<p class='muted-text'>Semana {week} — renovado automaticamente toda segunda-feira</p>",unsafe_allow_html=True)

    # Generate/cache weekly list
    if not st.session_state.weekly_videos or st.session_state.weekly_generated_date!=week:
        with st.spinner("Selecionando vídeos da semana..."):
            if st.session_state.yt_api_key:
                queries=["TED talk english intermediate 2024","BBC learning english 2024 new","English conversation practice intermediate 2024","english vlog natural speech 2024"]
                all_vids=[]
                for q in queries:
                    results=search_youtube(q,max_results=2,yt_key=st.session_state.yt_api_key)
                    all_vids.extend(results)
                # Deduplicate
                seen=set()
                unique=[]
                for v in all_vids:
                    if v["id"] not in seen:
                        seen.add(v["id"])
                        unique.append(v)
                st.session_state.weekly_videos=unique[:4] if unique else generate_weekly_curated()
            else:
                st.session_state.weekly_videos=generate_weekly_curated()
            st.session_state.weekly_generated_date=week

    videos=st.session_state.weekly_videos

    if not videos:
        st.info("Nenhum vídeo disponível. Verifique as API keys.")
    else:
        # Render video cards in 2 columns
        cols=st.columns(2)
        for i,v in enumerate(videos):
            with cols[i%2]:
                lvl=v.get("level","Intermediário")
                vtype=v.get("type","")
                dur=v.get("duration","")
                badge_cls={"Básico":"badge-green","Intermediário":"badge-yellow","Avançado":"badge-red"}.get(lvl,"badge-yellow")
                type_cls={"TED Talk":"badge-purple","TED-Ed":"badge-purple","BBC Learning":"badge-green","Vlog":"badge-yellow","Educacional":"badge-blue"}.get(vtype,"badge-yellow")

                st.markdown(f"""
                <div class='vid-card' style='margin-bottom:1rem;'>
                  <img class='vid-thumb' src='https://img.youtube.com/vi/{v["id"]}/mqdefault.jpg' onerror="this.src='https://img.youtube.com/vi/{v["id"]}/default.jpg'"/>
                  <div class='vid-meta'>
                    <div style='margin-bottom:.5rem;'>
                      <span class='badge {badge_cls}'>{lvl}</span>
                      {f'<span class="badge {type_cls}" style="margin-left:4px;">{vtype}</span>' if vtype else ''}
                      {f'<span class="badge" style="background:#ffffff11;color:#7A7A8A;border:1px solid #2A2A35;margin-left:4px;">⏱ {dur}</span>' if dur else ''}
                    </div>
                    <div style='font-weight:600;font-size:.95rem;color:#F0EFE9;margin-bottom:.3rem;line-height:1.4;'>{v["title"][:70]}{"..." if len(v["title"])>70 else ""}</div>
                    <div style='font-size:.8rem;color:#7A7A8A;'>{v.get("channel","")}</div>
                  </div>
                </div>""", unsafe_allow_html=True)

                btn_col1,btn_col2=st.columns(2)
                with btn_col1:
                    if st.button("▶ Estudar este vídeo",key=f"study_{v['id']}_{i}",use_container_width=True):
                        st.session_state.yt_video_id=v["id"]
                        st.session_state.yt_video_title=v["title"]
                        with st.spinner("Carregando legendas..."):
                            t=get_transcript(v["id"])
                            if t:
                                st.session_state.yt_transcript=t
                                st.success("✅ Pronto! Vá para a aba 🔍 Buscar")
                            else:
                                st.warning("Sem legendas. Tente outro vídeo.")
                with btn_col2:
                    vid_id = v['id']
                    st.markdown(f"<a href='https://www.youtube.com/watch?v={vid_id}' target='_blank'><button style='background:#1E1E24;color:#F0EFE9;border:1px solid #2A2A35;border-radius:8px;padding:8px 12px;cursor:pointer;font-size:.85rem;width:100%;'>🔗 YouTube</button></a>",unsafe_allow_html=True)

        st.markdown("---")
        col_ref,col_ai=st.columns([1,2])
        with col_ref:
            if st.button("🔄 Atualizar sugestões",use_container_width=True):
                st.session_state.weekly_videos=[]
                st.session_state.weekly_generated_date=""
                st.rerun()
        with col_ai:
            if st.button("🤖 Pedir sugestão personalizada ao Claude",use_container_width=True):
                if not st.session_state.api_key:
                    st.error("Insira sua API Key do Claude!")
                else:
                    with st.spinner("Claude está selecionando vídeos para você..."):
                        suggestion=ask_claude("""Você é um professor de inglês especializado para brasileiros de nível intermediário.
Sugira 3 vídeos do YouTube em inglês para praticar shadowing. Para cada um forneça:
- Título exato do vídeo
- Canal
- Por que é bom para shadowing
- Nível: Básico/Intermediário/Avançado
- Uma frase de exemplo do vídeo para praticar

Foque em: TED Talks, BBC Learning English, vlogs autênticos.
Responda em português, de forma animada e motivadora.""", max_tokens=600)
                        if suggestion:
                            st.markdown(f"""<div class='card-blue'><b style='color:#47CFFF;'>🤖 Sugestão do Professor IA</b><br><br>{suggestion}</div>""",unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# TAB 2 — BUSCAR VÍDEOS
# ═══════════════════════════════════════════════════════════════
with tab_search:
    st.markdown("<h2>🔍 Buscar & Carregar Vídeo</h2>",unsafe_allow_html=True)

    search_mode=st.radio("Como quer encontrar o vídeo?",
        ["🔎 Buscar no YouTube","📋 Escolher da lista curada","🔗 Colar link direto"],
        horizontal=True)

    selected_vid_id=""
    selected_vid_title=""

    # ── MODE 1: YouTube Search ──
    if search_mode=="🔎 Buscar no YouTube":
        if not st.session_state.yt_api_key:
            st.info("💡 Para busca ao vivo, adicione sua YouTube Data API Key na barra lateral. Por enquanto, use os temas abaixo ou cole um link.")

        st.markdown("**Temas prontos:**")
        preset_cols=st.columns(4)
        for i,(label,query) in enumerate(SEARCH_PRESETS.items()):
            with preset_cols[i%4]:
                if st.button(label,key=f"preset_{i}",use_container_width=True):
                    st.session_state["search_query"]=query

        search_q=st.text_input("Ou busque livremente:",
            value=st.session_state.get("search_query",""),
            placeholder="Ex: TED talk habits English subtitles")

        if st.button("🔍 Buscar",use_container_width=True) and search_q:
            if st.session_state.yt_api_key:
                with st.spinner("Buscando no YouTube..."):
                    results=search_youtube(search_q,max_results=6,yt_key=st.session_state.yt_api_key)
                    if results:
                        st.session_state["search_results"]=results
                    else:
                        st.warning("Nenhum resultado. Tente outra busca.")
            else:
                # Filter curated by keyword
                kw=search_q.lower()
                filtered=[v for v in CURATED_VIDEOS if kw in v["title"].lower() or kw in v.get("type","").lower() or kw in v["channel"].lower()]
                st.session_state["search_results"]=filtered if filtered else CURATED_VIDEOS[:6]
                st.info("Mostrando da lista curada (sem YouTube API Key).")

        results=st.session_state.get("search_results",[])
        if results:
            st.markdown(f"**{len(results)} vídeos encontrados:**")
            rcols=st.columns(3)
            for i,v in enumerate(results):
                with rcols[i%3]:
                    dur=v.get("duration","")
                    st.markdown(f"""
                    <div class='vid-card' style='margin-bottom:.5rem;'>
                      <img class='vid-thumb' src='https://img.youtube.com/vi/{v["id"]}/mqdefault.jpg'/>
                      <div class='vid-meta'>
                        <div style='font-size:.85rem;font-weight:600;color:#F0EFE9;line-height:1.3;'>{v["title"][:55]}{"..." if len(v["title"])>55 else ""}</div>
                        <div style='font-size:.75rem;color:#7A7A8A;margin-top:3px;'>{v.get("channel","")} {f"· ⏱ {dur}" if dur else ""}</div>
                      </div>
                    </div>""",unsafe_allow_html=True)
                    if st.button("▶ Estudar",key=f"sr_{v['id']}_{i}",use_container_width=True):
                        selected_vid_id=v["id"]
                        selected_vid_title=v["title"]

    # ── MODE 2: Curated List ──
    elif search_mode=="📋 Escolher da lista curada":
        st.markdown("**Selecione um vídeo da nossa lista:**")
        lvl_filter=st.selectbox("Filtrar por nível:",["Todos","Básico","Intermediário","Avançado"])
        type_filter=st.selectbox("Filtrar por tipo:",["Todos","TED Talk","TED-Ed","BBC Learning","Vlog","Educacional"])

        filtered_curated=[
            v for v in CURATED_VIDEOS
            if (lvl_filter=="Todos" or v.get("level")==lvl_filter)
            and (type_filter=="Todos" or v.get("type")==type_filter)
        ]

        cc=st.columns(3)
        for i,v in enumerate(filtered_curated):
            with cc[i%3]:
                lvl=v.get("level","")
                badge_cls={"Básico":"badge-green","Intermediário":"badge-yellow","Avançado":"badge-red"}.get(lvl,"badge-yellow")
                st.markdown(f"""
                <div class='vid-card'>
                  <img class='vid-thumb' src='https://img.youtube.com/vi/{v["id"]}/mqdefault.jpg'/>
                  <div class='vid-meta'>
                    <span class='badge {badge_cls}'>{lvl}</span>
                    <span class='badge badge-purple' style='margin-left:4px;'>{v.get("type","")}</span>
                    <div style='font-size:.85rem;font-weight:600;color:#F0EFE9;margin-top:.4rem;line-height:1.3;'>{v["title"][:55]}{"..." if len(v["title"])>55 else ""}</div>
                    <div style='font-size:.75rem;color:#7A7A8A;margin-top:3px;'>{v["channel"]} · ⏱ {v.get("duration","")}</div>
                  </div>
                </div>""",unsafe_allow_html=True)
                if st.button("▶ Estudar",key=f"cur_{v['id']}_{i}",use_container_width=True):
                    selected_vid_id=v["id"]
                    selected_vid_title=v["title"]

    # ── MODE 3: Direct Link ──
    else:
        yt_url=st.text_input("🔗 Cole o link do YouTube:",placeholder="https://www.youtube.com/watch?v=...")
        if st.button("▶️ Carregar vídeo",use_container_width=True) and yt_url.strip():
            vid=extract_video_id(yt_url.strip())
            if vid:
                selected_vid_id=vid
                selected_vid_title=yt_url
            else:
                st.error("URL inválida.")

    # ── LOAD SELECTED VIDEO ──
    if selected_vid_id:
        with st.spinner("Carregando legendas..."):
            t=get_transcript(selected_vid_id)
            if t:
                st.session_state.yt_video_id=selected_vid_id
                st.session_state.yt_video_title=selected_vid_title
                st.session_state.yt_transcript=t
                st.success(f"✅ '{selected_vid_title[:50]}' carregado — {len(t)} segmentos de legenda!")
            else:
                st.warning("Não foi possível obter legendas. Tente outro vídeo.")

    # ── VIDEO PLAYER ──
    if st.session_state.yt_video_id and st.session_state.yt_transcript:
        vid=st.session_state.yt_video_id
        transcript=st.session_state.yt_transcript
        title=st.session_state.yt_video_title

        st.markdown("---")
        st.markdown(f"### ▶️ {title[:70]}")
        st.markdown(f'<iframe width="100%" height="380" src="https://www.youtube.com/embed/{vid}?cc_load_policy=1&cc_lang_pref=en" frameborder="0" allowfullscreen style="border-radius:12px;"></iframe>',unsafe_allow_html=True)

        segments=transcript_to_segments(transcript,chunk=4)
        st.markdown("### 📜 Praticar um trecho")
        seg_idx=st.selectbox("Trecho:",range(len(segments)),
            format_func=lambda i:f"[{segments[i]['start']//60:02d}:{segments[i]['start']%60:02d}] {segments[i]['text'][:55]}...",
            label_visibility="collapsed")
        seg=segments[seg_idx]

        st.markdown(f"""<div class='card-accent'>
          <div style='font-size:.75rem;color:#7A7A8A;letter-spacing:2px;text-transform:uppercase;margin-bottom:.8rem;'>⏱ {seg['start']//60:02d}:{seg['start']%60:02d}</div>
          <div style='font-size:1.15rem;line-height:1.9;font-weight:500;color:#F0EFE9;'>"{seg['text']}"</div>
        </div>""",unsafe_allow_html=True)

        tc1,tc2=st.columns(2)
        with tc1: st.markdown(tts_btn(seg["text"],"🔊 Ouvir normal",0.85),unsafe_allow_html=True)
        with tc2: st.markdown(tts_btn(seg["text"],"🐢 Ouvir devagar",0.6),unsafe_allow_html=True)
        st.markdown(f"<a href='https://www.youtube.com/watch?v={vid}&t={seg['start']}s' target='_blank' style='color:#47CFFF;font-size:.85rem;'>▶ Abrir neste trecho no YouTube</a>",unsafe_allow_html=True)

        st.markdown("---")
        vt1,vt2=st.tabs(["🎙️ Gravar voz","✍️ Digitar"])
        with vt1:
            st.components.v1.html(STT_HTML,height=195)
            vt_voice=st.text_area("Texto capturado:",placeholder="Cole aqui...",height=70,key="vt_voice")
            if st.button("🤖 Analisar",use_container_width=True,key="vt_analyze_voice") and vt_voice.strip():
                if not st.session_state.api_key: st.error("Insira API Key!")
                else:
                    with st.spinner("Analisando..."):
                        r=ask_claude(f'English teacher. Original: "{seg["text"]}"\nStudent said: "{vt_voice}"\nFeedback em PT-BR: pronúncia, ritmo, vocabulário. Encorajador e específico.')
                        if r:
                            st.markdown(f"<div class='card' style='border-color:#47CFFF;'><b style='color:#47CFFF;'>🤖 Feedback</b><br><br>{r}</div>",unsafe_allow_html=True)
                            st.session_state.xp+=15
        with vt2:
            vt_text=st.text_area("Escreva o que disse:",placeholder="Type here...",height=80,key="vt_text")
            if st.button("🤖 Analisar",use_container_width=True,key="vt_analyze_text") and vt_text.strip():
                if not st.session_state.api_key: st.error("Insira API Key!")
                else:
                    with st.spinner("Analisando..."):
                        r=ask_claude(f'English teacher, shadowing. Original: "{seg["text"]}"\nStudent wrote: "{vt_text}"\nFeedback em PT-BR: pronúncia, ritmo, vocabulário.')
                        if r:
                            st.markdown(f"<div class='card' style='border-color:#47CFFF;'><b style='color:#47CFFF;'>🤖 Feedback</b><br><br>{r}</div>",unsafe_allow_html=True)
                            st.session_state.xp+=15

        st.markdown("---")
        st.markdown("### 💬 Perguntar sobre o vídeo")
        full_text=transcript_to_text(transcript)
        yt_q=st.text_input("Dúvida:",placeholder="Ex: O que significa 'figure out'? Qual o tom do apresentador?")
        if st.button("❓ Perguntar ao Claude",use_container_width=True) and yt_q.strip():
            if not st.session_state.api_key: st.error("Insira API Key!")
            else:
                with st.spinner("Analisando..."):
                    r=ask_claude(f'English teacher. Video transcript:\n"{full_text}"\nStudent question (PT): "{yt_q}"\nAnswer in PT-BR, teacher-style, educational.', max_tokens=600)
                    if r: st.markdown(f"<div class='card-blue'><b style='color:#47CFFF;'>🤖 Professor</b><br><br>{r}</div>",unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# TAB 3 — SHADOWING CLÁSSICO
# ═══════════════════════════════════════════════════════════════
with tab_shadow:
    st.markdown("<h2>🎬 Shadowing com Filmes & Séries</h2>",unsafe_allow_html=True)
    sc1,sc2=st.columns([2,1])
    with sc1: scene_name=st.selectbox("Cena",list(SAMPLE_SCENES.keys()),label_visibility="collapsed")
    scene=SAMPLE_SCENES[scene_name]
    with sc2:
        lc={"Básico":"#47CFFF","Intermediário":"#E8FF47","Avançado":"#FF6B6B"}.get(scene["level"],"#E8FF47")
        st.markdown(f"<div style='padding-top:.5rem'><span style='background:{lc}22;color:{lc};border:1px solid {lc}55;border-radius:20px;padding:4px 14px;font-size:.85rem;font-weight:600;'>{scene['level']}</span></div>",unsafe_allow_html=True)

    st.markdown(f"""<div class='card-accent' style='margin-top:1rem;'>
      <div style='font-size:.75rem;color:#7A7A8A;letter-spacing:2px;text-transform:uppercase;margin-bottom:.8rem;'>🇺🇸 Original</div>
      <div style='font-size:1.15rem;line-height:1.9;font-weight:500;color:#F0EFE9;'>"{scene['en']}"</div>
    </div>""",unsafe_allow_html=True)

    sb1,sb2=st.columns(2)
    with sb1: st.markdown(tts_btn(scene["en"],"🔊 Ouvir normal",0.9),unsafe_allow_html=True)
    with sb2: st.markdown(tts_btn(scene["en"],"🐢 Ouvir devagar",0.6),unsafe_allow_html=True)

    if st.checkbox("📖 Mostrar tradução"):
        pt_text = scene['pt']
        st.markdown(f"<div class='card' style='border-color:#47CFFF44;'><div style='color:#47CFFF;font-size:.75rem;letter-spacing:2px;text-transform:uppercase;margin-bottom:.5rem;'>🇧🇷 Tradução</div><div style='color:#B0B0C0;line-height:1.7;'>{pt_text}</div></div>",unsafe_allow_html=True)

    st.markdown(f"<div style='margin:.5rem 0 1rem;'><span style='font-size:.8rem;color:#7A7A8A;'>📌 Vocab: </span>{''.join(f'<span class=tag>{w}</span>' for w in scene['vocab'])}</div>",unsafe_allow_html=True)
    st.info(f"💡 **Dica:** {scene['tips']}")
    st.markdown("---")

    ss1,ss2=st.tabs(["🎙️ Gravar voz","✍️ Digitar"])
    with ss1:
        st.components.v1.html(STT_HTML,height=195)
        sv=st.text_area("Texto capturado:",placeholder="Cole aqui...",height=70,key="sv")
        if st.button("🤖 Analisar gravação",use_container_width=True,key="sv_btn") and sv.strip():
            if not st.session_state.api_key: st.error("Insira API Key!")
            else:
                with st.spinner("Analisando..."):
                    r=ask_claude(f'Shadowing teacher. Original: "{scene["en"]}"\nStudent: "{sv}"\nFeedback PT-BR: pontos positivos, dicas pronúncia/ritmo, frase-chave, encorajamento.')
                    if r:
                        st.markdown(f"<div class='card' style='border-color:#47CFFF;'><b style='color:#47CFFF;'>🤖 Feedback</b><br><br>{r}</div>",unsafe_allow_html=True)
                        st.session_state.xp+=15; st.success(f"🎉 +15 XP!")
    with ss2:
        st_text=st.text_area("Escreva o que falou:",placeholder="Type here...",height=100,key="st_text")
        fb=st.radio("Análise:",["🎯 Pronúncia/ritmo","📝 Gramática","🌟 Completa"],horizontal=True)
        if st.button("🤖 Analisar texto",use_container_width=True,key="st_btn") and st_text.strip():
            if not st.session_state.api_key: st.error("Insira API Key!")
            else:
                with st.spinner("Analisando..."):
                    r=ask_claude(f'Shadowing teacher, {fb}. Original: "{scene["en"]}"\nStudent: "{st_text}"\nFeedback PT-BR, amigável.')
                    if r:
                        st.markdown(f"<div class='card' style='border-color:#47CFFF;'><b style='color:#47CFFF;'>🤖 Feedback</b><br><br>{r}</div>",unsafe_allow_html=True)
                        st.session_state.xp+=15; st.success(f"🎉 +15 XP!")

# ═══════════════════════════════════════════════════════════════
# TAB 4 — CONVERSAÇÃO
# ═══════════════════════════════════════════════════════════════
with tab_conv:
    st.markdown("<h2>🤖 Conversação com Voz</h2>",unsafe_allow_html=True)
    cp,ct=st.columns(2)
    with cp: persona_name=st.selectbox("Professor",list(PERSONAS.keys()),label_visibility="collapsed")
    with ct: topic=st.selectbox("Tema",["💬 Livre"]+list(TOPIC_STARTERS.keys()),label_visibility="collapsed")
    persona=PERSONAS[persona_name]
    st.markdown(f"<div class='card'><span style='color:#E8FF47;font-weight:600;'>{persona_name}</span><br><span class='muted-text'>{persona['desc']}</span></div>",unsafe_allow_html=True)

    cn,cl=st.columns(2)
    with cn:
        if st.button("🔄 Nova conversa",use_container_width=True): st.session_state.conversation=[]; st.rerun()
    with cl: correction=st.selectbox("Correção",["🟡 Suave","🔴 Detalhada","🟢 Só elogios"],label_visibility="collapsed")

    if not st.session_state.conversation and topic!="💬 Livre":
        s=TOPIC_STARTERS.get(topic,"")
        if s: st.session_state.conversation.append({"role":"assistant","content":s})

    if not st.session_state.conversation:
        st.markdown("<div style='text-align:center;padding:2rem;color:#7A7A8A;'><div style='font-size:2.5rem;'>💬</div><div>Escreva ou grave em inglês abaixo!</div></div>",unsafe_allow_html=True)
    else:
        for msg in st.session_state.conversation:
            if msg["role"]=="user":
                st.markdown(f"<div class='msg-user'><span style='font-size:.75rem;color:#E8FF47;font-weight:600;'>VOCÊ</span><br>{msg['content']}</div>",unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='msg-ai'><span style='font-size:.75rem;color:#47CFFF;font-weight:600;'>PROFESSOR IA</span><br>{msg['content']}</div>",unsafe_allow_html=True)
                if st.session_state.tts_enabled:
                    st.markdown(tts_btn(msg["content"],"🔊 Ouvir",persona["voice_rate"]),unsafe_allow_html=True)

    st.markdown("---")
    input_mode=st.radio("Responder:",["✍️ Digitar","🎙️ Gravar voz"],horizontal=True)
    cmap={"🟡 Suave":"Correct subtly by modeling correct English.","🔴 Detalhada":"Explicitly explain errors in Portuguese.","🟢 Só elogios":"Only correct critical errors, be very encouraging."}
    system=f"{persona['system']}\nCorrection: {cmap[correction]}\nAlways respond in English."

    if input_mode=="✍️ Digitar":
        um=st.text_area("Em inglês:",placeholder="Type in English...",height=85,key="cv_type")
        cs1,cs2=st.columns([2,1])
        with cs1: send=st.button("📤 Enviar",use_container_width=True)
        with cs2: translate=st.button("🇧🇷→🇺🇸",use_container_width=True)
        if translate and um.strip() and st.session_state.api_key:
            with st.spinner("Traduzindo..."):
                tr=ask_claude_chat([{"role":"user","content":f"Translate to natural English: {um}"}],"You are a translator. Return ONLY the English translation.")
                if tr: st.info(f"🇺🇸 **{tr}**")
        if send and um.strip():
            if not st.session_state.api_key: st.error("Insira API Key!")
            else:
                st.session_state.conversation.append({"role":"user","content":um})
                with st.spinner("Respondendo..."):
                    r=ask_claude_chat(st.session_state.conversation,system)
                    if r:
                        st.session_state.conversation.append({"role":"assistant","content":r})
                        st.session_state.xp+=10; st.rerun()
    else:
        st.components.v1.html(STT_HTML,height=195)
        cv_voice=st.text_area("Texto reconhecido:",placeholder="Cole aqui...",height=70,key="cv_voice")
        if st.button("📤 Enviar gravação",use_container_width=True) and cv_voice.strip():
            if not st.session_state.api_key: st.error("Insira API Key!")
            else:
                st.session_state.conversation.append({"role":"user","content":cv_voice})
                with st.spinner("Respondendo..."):
                    r=ask_claude_chat(st.session_state.conversation,system)
                    if r:
                        st.session_state.conversation.append({"role":"assistant","content":r})
                        st.session_state.xp+=10; st.rerun()

    if st.session_state.conversation:
        u=[m for m in st.session_state.conversation if m["role"]=="user"]
        st.markdown(f"<div class='muted-text' style='margin-top:1rem;'>📊 {len(u)} msgs · {sum(len(m['content'].split()) for m in u)} palavras · +{len(u)*10} XP</div>",unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# TAB 5 — FLASHCARDS
# ═══════════════════════════════════════════════════════════════
with tab_flash:
    st.markdown("<h2>🃏 Flashcards com Revisão Espaçada</h2>",unsafe_allow_html=True)
    ft1,ft2,ft3=st.tabs(["📚 Estudar","🗂️ Gerenciar","✨ Gerar com IA"])

    with ft1:
        fd,fs=st.columns([2,1])
        with fd: deck_name=st.selectbox("Baralho",list(st.session_state.flashcard_decks.keys()),label_visibility="collapsed")
        deck=st.session_state.flashcard_decks[deck_name]
        due=get_due(deck)
        with fs: st.markdown(f"<div style='padding:.5rem 0;'><span style='color:#E8FF47;font-weight:700;font-size:1.2rem;'>{len(due)}</span> <span class='muted-text'>p/ revisar</span></div>",unsafe_allow_html=True)

        if not due:
            st.markdown("<div style='text-align:center;padding:3rem;'><div style='font-size:3rem;'>🎉</div><h3 style='color:#E8FF47;'>Tudo em dia!</h3><p class='muted-text'>Volte amanhã!</p></div>",unsafe_allow_html=True)
        else:
            if st.session_state.fc_index>=len(due): st.session_state.fc_index=0
            ci=due[st.session_state.fc_index]; card=deck[ci]
            lvls=["🌱 Novo","🔵 Fácil","🟡 Médio","🟠 Difícil","🟢 Dominado","⭐ Expert"]
            st.progress(st.session_state.fc_index/len(due))
            st.markdown(f"<div class='muted-text' style='text-align:right;'>{st.session_state.fc_index+1}/{len(due)}</div>",unsafe_allow_html=True)
            st.markdown(f"""<div class='flashcard'>
              <div style='font-size:.75rem;color:#7A7A8A;letter-spacing:2px;text-transform:uppercase;margin-bottom:1rem;'>🇺🇸 Inglês</div>
              <div style='font-size:2rem;font-family:Syne,sans-serif;font-weight:800;color:#E8FF47;margin-bottom:.5rem;'>{card["en"]}</div>
              <div style='font-size:.8rem;color:#7A7A8A;'>{lvls[min(card.get("level",0),5)]}</div>
            </div>""",unsafe_allow_html=True)
            ff1,ff2=st.columns(2)
            with ff1:
                if st.button("👁️ Ver resposta" if not st.session_state.fc_show_answer else "🙈 Esconder",use_container_width=True):
                    st.session_state.fc_show_answer=not st.session_state.fc_show_answer; st.rerun()
            with ff2: st.markdown(tts_btn(card["en"],"🔊 Pronúncia",0.8),unsafe_allow_html=True)

            if st.session_state.fc_show_answer:
                st.markdown(f"""<div class='card' style='text-align:center;border-color:#47CFFF;'>
                  <div style='font-size:.75rem;color:#47CFFF;letter-spacing:2px;text-transform:uppercase;margin-bottom:.5rem;'>🇧🇷</div>
                  <div style='font-size:1.4rem;font-weight:600;color:#F0EFE9;margin-bottom:.8rem;'>{card["pt"]}</div>
                  <div style='font-size:.85rem;color:#7A7A8A;font-style:italic;'>"{card["example"]}"</div>
                </div>""",unsafe_allow_html=True)
                st.markdown(tts_btn(card["example"],"🔊 Ouvir exemplo",0.85),unsafe_allow_html=True)
                st.markdown("**Como foi?**")
                fr1,fr2,fr3,fr4=st.columns(4)
                for col,label,q in [(fr1,"😰 Errei",0),(fr2,"🤔 Difícil",2),(fr3,"😊 Lembrei",3),(fr4,"🚀 Fácil!",5)]:
                    with col:
                        if st.button(label,use_container_width=True,key=f"fc_{q}_{deck_name}"):
                            st.session_state.flashcard_decks[deck_name]=update_review(st.session_state.flashcard_decks[deck_name],ci,q)
                            st.session_state.fc_index+=1; st.session_state.fc_show_answer=False
                            st.session_state.xp+=(q+1)*3; st.rerun()

    with ft2:
        st.markdown("### ➕ Adicionar card")
        tgt=st.selectbox("Baralho:",list(st.session_state.flashcard_decks.keys()),key="add_dk")
        fa1,fa2=st.columns(2)
        with fa1: new_en=st.text_input("Inglês")
        with fa2: new_pt=st.text_input("Português")
        new_ex=st.text_input("Exemplo")
        if st.button("💾 Adicionar") and new_en and new_pt:
            st.session_state.flashcard_decks[tgt].append({"en":new_en,"pt":new_pt,"example":new_ex or f"Example with '{new_en}'.","level":0,"next_review":""})
            st.success(f"✅ '{new_en}' adicionado!")
        st.markdown("### 🗂️ Novo baralho")
        new_dk=st.text_input("Nome (ex: '🏖️ Viagens')")
        if st.button("Criar") and new_dk:
            if new_dk not in st.session_state.flashcard_decks:
                st.session_state.flashcard_decks[new_dk]=[]; st.success(f"'{new_dk}' criado!")
            else: st.warning("Já existe!")

    with ft3:
        st.markdown("### ✨ Gerar com IA")
        gt=st.text_input("Tema:",placeholder="Ex: phrasal verbs, viagem, tecnologia...")
        gq2,gl2=st.columns(2)
        with gq2: gqty=st.slider("Cards:",3,15,8)
        with gl2: glvl=st.select_slider("Nível:",["Básico","Intermediário","Avançado"],value="Intermediário")
        gdk=st.selectbox("Baralho destino:",list(st.session_state.flashcard_decks.keys()),key="gdk")
        if st.button("🤖 Gerar",use_container_width=True):
            if not st.session_state.api_key: st.error("Insira API Key!")
            elif not gt.strip(): st.warning("Descreva um tema!")
            else:
                with st.spinner("Gerando..."):
                    r=ask_claude(f'Create {gqty} English flashcards for Brazilian {glvl} level about: {gt}\nReturn ONLY valid JSON array:\n[{{"en":"word","pt":"tradução","example":"Sentence."}}]')
                    if r:
                        try:
                            m=re.search(r'\[.*\]',r,re.DOTALL)
                            if m:
                                cards=json.loads(m.group()); added=0
                                for c in cards:
                                    if "en" in c and "pt" in c:
                                        st.session_state.flashcard_decks[gdk].append({"en":c["en"],"pt":c["pt"],"example":c.get("example",""),"level":0,"next_review":""})
                                        added+=1
                                st.success(f"✅ {added} cards adicionados!"); st.session_state.xp+=added*5; st.rerun()
                        except Exception as e: st.error(f"Erro: {e}")

# ═══════════════════════════════════════════════════════════════
# TAB 6 — PROGRESSO
# ═══════════════════════════════════════════════════════════════
with tab_prog:
    st.markdown("<h2>📊 Seu Progresso</h2>",unsafe_allow_html=True)
    xp=st.session_state.xp; lvl=xp//100+1; xp_in=xp%100
    lnames=["Iniciante","Explorador","Estudante","Comunicador","Fluente","Expert","Mestre"]
    lname=lnames[min(lvl-1,6)]
    pm1,pm2,pm3,pm4=st.columns(4)
    with pm1: st.metric("⚡ XP",xp)
    with pm2: st.metric("🏅 Nível",f"{lvl} — {lname}")
    with pm3: st.metric("🔥 Streak",f"{st.session_state.streak}d")
    with pm4: st.metric("🃏 Cards",sum(len(v) for v in st.session_state.flashcard_decks.values()))
    st.markdown(f"<div class='card' style='margin-top:1rem;'><div style='display:flex;justify-content:space-between;'><span style='color:#E8FF47;font-weight:700;'>Nível {lvl}: {lname}</span><span class='muted-text'>{xp_in}/100 XP</span></div></div>",unsafe_allow_html=True)
    st.progress(xp_in/100)
    st.markdown("---")
    st.markdown("### 🃏 Flashcards")
    for dn,cards in st.session_state.flashcard_decks.items():
        today=datetime.date.today().isoformat()
        due_n=sum(1 for c in cards if not c.get("next_review") or c["next_review"]<=today)
        mastered=sum(1 for c in cards if c.get("level",0)>=4)
        total=len(cards)
        pp1,pp2,pp3,pp4=st.columns([3,1,1,1])
        with pp1: st.markdown(f"**{dn}**")
        with pp2: st.markdown(f"<span style='color:{'#FF6B6B' if due_n>0 else '#47CFFF'};font-weight:700;'>{due_n}</span> <span class='muted-text'>revisar</span>",unsafe_allow_html=True)
        with pp3: st.markdown(f"<span style='color:#E8FF47;font-weight:700;'>{mastered}</span> <span class='muted-text'>dominou</span>",unsafe_allow_html=True)
        with pp4: st.markdown(f"<span class='muted-text'>{total} total</span>",unsafe_allow_html=True)
        if total>0: st.progress(mastered/total)
    st.markdown("---")
    for icon,title,desc in [
        ("🌟","Sugestões semanais","Novos vídeos toda segunda-feira, selecionados para seu nível."),
        ("🎬","Shadowing diário","15–20 min/dia supera 2h no fim de semana."),
        ("🎙️","Fale sem medo","O reconhecimento de voz treina sua pronúncia de verdade."),
        ("🃏","Revisão espaçada","Ciência, não força de vontade — revise no horário certo."),
    ]:
        st.markdown(f"<div class='card' style='display:flex;gap:1rem;align-items:flex-start;'><div style='font-size:1.8rem;'>{icon}</div><div><div style='font-weight:700;color:#F0EFE9;'>{title}</div><div class='muted-text'>{desc}</div></div></div>",unsafe_allow_html=True)
    with st.expander("⚙️ Configurações"):
        ex1,ex2=st.columns(2)
        with ex1:
            if st.button("🔄 Resetar XP"): st.session_state.xp=0; st.session_state.streak=0; st.rerun()
        with ex2:
            b=st.number_input("XP manual:",0,500,0,10)
            if st.button("➕ Add XP") and b>0: st.session_state.xp+=b; st.rerun()
