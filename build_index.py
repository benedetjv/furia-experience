import json
from openai import OpenAI
from dotenv import load_dotenv
import os

print("🟡 Iniciando build_index.py...")

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ ERRO: OPENAI_API_KEY não encontrada.")
    exit()

client = OpenAI(api_key=api_key)
documentos = [
    {"id": "ranking-posicao", "text": "🏆 A FURIA está na posição 16ª com 103 pontos na HLTV."},
    {"id": "ranking-top30", "text": "Top 30 HLTV:\n1. Vitality — 1000\n2. Spirit — 849\n3. MOUZ — 629\n..."},
    {"id": "lineup", "text": "Line-up FURIA: FalleN, yuurih, YEKINDAR, KSCERATO, molodoy; Coach: Sid 'sidde' Macedo."},
    {"id": "noticias", "text": "Notícias HLTV: HEROIC vence CCT Global Finals, Vitality conquista o Grand Slam."},
    {"id": "calendario", "text": "Hoje a FURIA joga: 😔 A FURIA não joga hoje."}
]

for i, doc in enumerate(documentos):
    print(f"📨 Gerando embedding {i+1}/{len(documentos)} → {doc['id']}")
    try:
        resp = client.embeddings.create(
    model="text-embedding-ada-002",
    input=["Teste de embedding"]
)

        if not resp.data:
            raise ValueError("❌ Resposta vazia da OpenAI")
        doc["embedding"] = resp.data[0].embedding
        print(f"✅ Embedding gerado para: {doc['id']}")
    except Exception as e:
        print(f"❌ Erro ao gerar embedding para {doc['id']}: {e}")
        exit(1)

with open("meta.json", "w", encoding="utf-8") as f:
    json.dump(documentos, f, ensure_ascii=False, indent=2)

print("✅ meta.json gerado com sucesso com embeddings reais.")
