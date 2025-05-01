# build_index.py
import json
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY não encontrada")

client = OpenAI(api_key=api_key)

# Seus textos de base para indexar
documentos = [
    {"id": "ranking", "text": "A FURIA está na 16ª posição com 103 pontos na HLTV."},
    {"id": "lineup", "text": "Line-up FURIA: FalleN, yuurih, YEKINDAR, KSCERATO, molodoy. Coach: Sid 'sidde' Macedo."},
    {"id": "noticias", "text": "Vitality venceu a Grand Final da IEM Melbourne contra Falcons."},
    # adicione mais se quiser
]

# Gera embeddings
for d in documentos:
    resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=[d["text"]]
    )
    d["embedding"] = resp.data[0].embedding

# Salva em meta.json
with open("meta.json", "w", encoding="utf-8") as f:
    json.dump(documentos, f, ensure_ascii=False, indent=2)

print("✅ Embeddings salvos em meta.json")
