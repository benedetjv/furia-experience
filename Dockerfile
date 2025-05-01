# Usa imagem base com Python 3.11
FROM python:3.11-slim

# Instala Chrome e Chromedriver (essencial para Selenium)
RUN apt-get update && apt-get install -y \
    wget unzip curl gnupg \
    chromium-driver chromium

# Define variáveis de ambiente para o Selenium
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Define diretório de trabalho
WORKDIR /app

# Copia arquivos do projeto
COPY . .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta padrão do Streamlit
EXPOSE 7860

# Comando padrão ao iniciar o container
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
