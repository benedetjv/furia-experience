import os
import time
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

# 1) Carrega a chave de .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("⚠️ OPENAI_API_KEY não encontrada no .env")

print("🔑 Chave carregada:", api_key[:8] + "…")

# 2) Instancia o client v1.x
client = OpenAI(api_key=api_key)

# 3) Upload do JSONL de treino
print(">> Enviando JSONL de fine-tune…")
upload = client.files.create(
    purpose="fine-tune",
    file=open("furia_finetune.jsonl", "rb")
)
file_id = upload.id
print("  • file_id =", file_id)

# 4) Cria o job de fine-tune via fine_tuning.jobs
print(">> Criando fine-tune job…")
try:
    job = client.fine_tuning.jobs.create(
        training_file=file_id,
        model="gpt-3.5-turbo",
        hyperparameters={
            "n_epochs": 4,
            "learning_rate_multiplier": 0.1
        }
    )
except OpenAIError as e:
    print("❌ Erro ao criar fine-tune:", e)
    exit(1)

ft_id = job.id
print("  • fine_tune_id =", ft_id)

# 5) Polling até terminar
print(">> Aguardando conclusão… (pode levar alguns minutos)")
while True:
    status = client.fine_tuning.jobs.retrieve(ft_id).status
    print(f"   • status = {status}")
    if status in ("succeeded", "failed"):
        break
    time.sleep(20)

# 6) Resultado final
result = client.fine_tuning.jobs.retrieve(ft_id)
print("✅ Fine-tune concluído!")
print("   • Modelo fino-tuned:", result.fine_tuned_model)
print("   • Status:", result.status)

# 7) (Opcional) Lista de eventos do fine-tune
print("\n📋 Eventos do fine-tune:")
events = client.fine_tuning.jobs.list_events(ft_id).data
for e in events:
    ts = time.strftime("%H:%M:%S", time.localtime(e.created_at))
    print(f"  [{ts}] {e.level.upper():7} — {e.message}")
