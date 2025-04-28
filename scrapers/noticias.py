# scrapers/noticias.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def criar_driver():
    service = Service('chromedriver-win64/chromedriver.exe')
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36')
    options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

    driver = webdriver.Chrome(service=service, options=options)
    return driver

def buscar_noticias():
    driver = criar_driver()
    try:
        driver.get('https://www.hltv.org/')

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "newsline"))
        )

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        noticias = soup.find_all('a', class_="newsline article")[:10]

        lista_noticias = []
        for noticia in noticias:
            titulo_tag = noticia.find('div', class_='newstext')
            if titulo_tag:
                titulo = titulo_tag.get_text(strip=True)
                link = "https://www.hltv.org" + noticia['href']
                lista_noticias.append({"titulo": titulo, "link": link})

        return lista_noticias

    except Exception as e:
        return f"Erro ao buscar notícias: {e}"

    finally:
        driver.quit()
