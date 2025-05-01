# scrapers/partidas_furia.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def criar_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    options.binary_location = "/usr/bin/chromium"  # caminho do Chrome no container
    service = Service("/usr/bin/chromedriver")     # caminho do chromedriver no container

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
