from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

resp = client.embeddings.create(
    model="text-embedding-ada-002",
    input=["Teste de embedding"]
)


print("Embedding gerado com sucesso:", len(resp.data[0].embedding))
