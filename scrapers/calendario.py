# scrapers/partidas_furia.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def criar_driver():
    service = Service('chromedriver-win64/chromedriver.exe')  # caminho correto
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36')
    options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

    driver = webdriver.Chrome(service=service, options=options)
    return driver

def buscar_partida_furia_hoje():
    driver = criar_driver()
    try:
        driver.get('https://www.hltv.org/team/8297/furia#tab-matchesBox')

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "matchesBox"))
        )

        soup = BeautifulSoup(driver.page_source, "html.parser")
        matches_box = soup.find("div", id="matchesBox")

        if not matches_box:
            return "Erro: Não encontrei a seção de partidas."

        upcoming = matches_box.find("div", class_="empty-state")
        if upcoming:
            return "😔 A FURIA não joga hoje."

        partidas = matches_box.select("div.upcomingMatch")
        jogos_hoje = []

        for partida in partidas:
            time1 = partida.select_one(".matchTeam.team1 .matchTeamName").text.strip()
            time2 = partida.select_one(".matchTeam.team2 .matchTeamName").text.strip()
            horario = partida.select_one(".matchTime").text.strip()

            confronto = f"{time1} vs {time2} às {horario}"
            jogos_hoje.append(confronto)

        if jogos_hoje:
            return jogos_hoje
        else:
            return "😔 A FURIA não joga hoje."

    except Exception as e:
        return f"Erro ao buscar partidas da FURIA: {e}"

    finally:
        driver.quit()
