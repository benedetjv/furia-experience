# Base Python image
FROM python:3.11-slim

# Instalações básicas e Chrome
RUN apt-get update && apt-get install -y \
    wget curl gnupg unzip \
    chromium chromium-driver \
    && apt-get clean

# Variáveis para o Selenium
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos para o container
COPY . .

# Instala dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta do Streamlit
EXPOSE 7860

# Comando para iniciar o app
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
