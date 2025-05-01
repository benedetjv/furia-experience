import os
import json
from sklearn.neighbors import NearestNeighbors
index = faiss.read_index("index.faiss")
import numpy as np
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import requests
from utils import image_to_base64
from scrapers.ranking import buscar_posicao_furia, buscar_top_30
from scrapers.lineup import buscar_lineup_furia
from scrapers.noticias import buscar_noticias
from scrapers.calendario import buscar_partida_furia_hoje

load_dotenv()

# Variáveis de ambiente
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

if not OPENAI_API_KEY:
    raise RuntimeError("❌ OPENAI_API_KEY não encontrada.")

# Função para enviar notificação ao Discord
def notificar_discord(msg: str):
    if DISCORD_WEBHOOK_URL:
        try:
            requests.post(DISCORD_WEBHOOK_URL, json={"content": msg})
        except Exception as e:
            print("Erro ao enviar webhook:", e)

# 1) set_page_config deve ser primeiro
st.set_page_config(page_title="FURIA Experience 🦁", page_icon="🎽", layout="wide")

# 2) Caches para scrapers
@st.cache_data(ttl=300)
def load_posicao():    return buscar_posicao_furia()
@st.cache_data(ttl=300)
def load_top30():      return buscar_top_30()
@st.cache_data(ttl=300)
def load_lineup():     return buscar_lineup_furia()
@st.cache_data(ttl=300)
def load_noticias():   return buscar_noticias()

# 3) RAG API setup
@st.cache_resource
def load_rag_api():
    if not os.path.exists("index.faiss") or not os.path.exists("meta.json"):
        raise RuntimeError("Gere index.faiss e meta.json com build_index_api.py")
    index = faiss.read_index("index.faiss")
    with open("meta.json","r",encoding="utf-8") as f:
        meta = json.load(f)
    client = OpenAI(api_key=OPENAI_API_KEY)
    return index, meta, client

try:
    index, meta, client = load_rag_api()
except RuntimeError as e:
    st.error(f"❌ Erro ao inicializar RAG API: {e}")
    st.stop()

def retrieve_api(query: str, k: int=3) -> list[str]:
    resp = client.embeddings.create(model="text-embedding-3-small", input=[query])
    q_emb = np.array(resp.data[0].embedding, dtype="float32")[None,:]
    _, I = index.search(q_emb, k)
    return [ meta[i]["text"] for i in I[0] ]

# 4) Branding
logo_b64 = image_to_base64("assets/logofuria.png")
HEADER_HTML = f"""
<div style="text-align:center; margin:2rem 0;">
  <img src="data:image/png;base64,{logo_b64}" width="180"/>
  <h1>FURIA Experience 🦁</h1>
  <h4>O chatbot da FURIA para o torcedor furioso!</h4>
</div>
"""

PAGES = [
    "🏠 Home",
    "🏆 Ranking da FURIA",
    "🎯 Line-up da FURIA",
    "📰 Notícias Recentes",
    "🗕️ FURIA joga hoje?",
    "💬 Modo Bate-Papo"
]

if "page" not in st.session_state:
    st.session_state.page = PAGES[0]
if "history" not in st.session_state:
    st.session_state.history = []

if st.session_state.page == "🏠 Home":
    st.markdown(HEADER_HTML, unsafe_allow_html=True)

st.selectbox("Selecione uma opção:", PAGES, index=PAGES.index(st.session_state.page), key="page")
page = st.session_state.page

if page == "🏠 Home":
    pass

elif page == "🏆 Ranking da FURIA":
    st.header("🏆 Ranking da FURIA e Top 30 HLTV")
    if "posicao" not in st.session_state or "top30" not in st.session_state:
        with st.spinner("Buscando ranking…"):
            st.session_state.posicao = load_posicao()
            st.session_state.top30   = load_top_30()
    st.success(st.session_state.posicao)
    df = st.session_state.top30
    if isinstance(df, str):
        st.error(df)
    else:
        df2 = (df.copy().reset_index(drop=True)
                 .drop(columns=["Posição"], errors="ignore"))
        df2["Pontos"] = (df2["Pontos"].astype(str)
                           .str.replace(r"[^\d]","",regex=True)
                           .astype(int))
        df2.insert(0,"Posição", df2.index+1)
        df2 = df2[["Posição","Time","Pontos"]]
        styled = (df2.style.hide(axis="index")
                  .format({"Pontos":"{:,}"})
                  .set_properties(subset=["Posição","Time"], **{"text-align":"left"})
                  .set_properties(subset=["Pontos"], **{"text-align":"right"}))
        st.dataframe(styled, use_container_width=True, height=500)

elif page == "🎯 Line-up da FURIA":
    st.header("🎯 Line-up Atual da FURIA")
    with st.spinner("Buscando lineup…"):
        jogadores, coach = load_lineup()
    st.markdown(f"**Jogadores:** {', '.join(jogadores)}")
    st.markdown(f"**Coach:** {coach}")

elif page == "📰 Notícias Recentes":
    st.header("📰 Notícias Recentes da HLTV")
    if "noticias" not in st.session_state:
        with st.spinner("Buscando notícias…"):
            st.session_state.noticias = load_noticias()
    noticias = st.session_state.noticias
    if isinstance(noticias,str):
        st.error(noticias)
    else:
        for n in noticias:
            st.markdown(f"- [{n['titulo']}]({n['link']})")

elif page == "🗕️ FURIA joga hoje?":
    st.header("🗕️ Partidas da FURIA Hoje")
    if st.button("🔄 Consultar"):
        with st.spinner("Consultando…"):
            jogos = buscar_partida_furia_hoje()
        if isinstance(jogos,list):
            st.success("Hoje a FURIA joga:")
            for j in jogos:
                st.write(f"- {j}")
        else:
            st.info(jogos)

elif page == "💬 Modo Bate-Papo":
    st.header("💬 Modo Bate-Papo")

    chat_container = st.container()

    with st.form("chat_form", clear_on_submit=True):
        pergunta = st.text_input("Digite sua pergunta…", key="input")
        c1, c2 = st.columns([1,1])
        with c1:
            enviar = st.form_submit_button("Enviar")
        with c2:
            limpar = st.form_submit_button("Limpar histórico")

        if limpar:
            st.session_state.history = []

        elif enviar and pergunta:
            st.session_state.history.append({"role":"user","text":pergunta})
            notificar_discord(f"🦁 Pergunta feita ao FURIA Experience: {pergunta}")

            low = pergunta.lower()
            if "posição" in low or "ranking" in low:
                pos_msg = load_posicao()
                import re
                m = re.search(r"posição\s*(\d+)", pos_msg)
                p = m.group(1) if m else "?"
                pts = re.search(r"com\s*(\d+)", pos_msg)
                pts = pts.group(1) if pts else "?"
                resposta = (
                    f"A FURIA está na {p}ª posição do ranking HLTV com {pts} pontos. "
                    "Confira em https://www.hltv.org/ranking/teams"
                )

            elif "line-up" in low or "jogadores" in low:
                jogs, coach = load_lineup()
                resposta = (
                    f"A line-up atual da FURIA é: {', '.join(jogs)} "
                    f"(Coach: {coach}). Veja em https://www.hltv.org/team/8297/furia"
                )

            else:
                with st.spinner("🕗 Buscando resposta, aguarde..."):
                    docs = retrieve_api(pergunta, k=3)
                    contexto = "\n\n---\n\n".join(docs)
                    system = (
                        "Você é um assistente especialista em FURIA CS:GO. "
                        "Use apenas este contexto para responder:\n\n"
                        f"{contexto}\n\n"
                        "Se não souber, diga que não sabe."
                    )
                    resp = client.chat.completions.create(
                        model="ft:gpt-3.5-turbo-0125:estagio::BR4cYEAw",
                        messages=[
                            {"role":"system","content":system},
                            {"role":"user","content":pergunta}
                        ],
                        temperature=0.7,
                    )
                    resposta = resp.choices[0].message.content.strip()

                if any(k in resposta.lower() for k in ["não sei","desculpe"]):
                    resposta = (
                        "😕 Infelizmente não posso te responder sobre isso. "
                        "Pode fazer outra pergunta?"
                    )

            st.session_state.history.append({"role":"bot","text":resposta})

    with chat_container:
        for msg in st.session_state.history:
            who = "Você" if msg["role"]=="user" else "FURIA"
            st.markdown(f"**{who}:** {msg['text']}")