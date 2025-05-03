# scrapers/ranking.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd

def criar_driver():
    service = Service('chromedriver-win64/chromedriver.exe')  # Caminho correto do driver no seu projeto
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36')
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def buscar_posicao_furia():
    driver = criar_driver()
    try:
        driver.get('https://www.hltv.org/ranking/teams')
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ranked-team"))
        )
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        ranked_teams = soup.find_all("div", class_="ranked-team")

        for team in ranked_teams:
            team_link = team.find("a", class_="moreLink")
            if team_link and "/team/8297/furia" in team_link.get("href", ""):
                position = team.find("span", class_="position").text.strip().replace("#", "")
                points = team.find("span", class_="points").text.strip().replace("(", "").replace(")", "").replace("HLTV points", "").strip()
                return f"\U0001F3C6 A FURIA está na posição {position}ª com {points} pontos na HLTV."

        return "😔 Não encontrei a FURIA no ranking."

    except Exception as e:
        return f"Erro ao buscar ranking: {e}"

    finally:
        driver.quit()

def buscar_top_30():
    driver = criar_driver()
    try:
        driver.get('https://www.hltv.org/ranking/teams')
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ranked-team"))
        )

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        ranked_teams = soup.find_all("div", class_="ranked-team")[:30]

        lista = []
        for team in ranked_teams:
            team_name = team.find("span", class_="name").text.strip()
            position = int(team.find("span", class_="position").text.strip().replace("#", ""))
            points = team.find("span", class_="points").text.strip().replace("(", "").replace(")", "").replace("HLTV points", "").strip()
            lista.append({
                "Posição": position,
                "Time": team_name,
                "Pontos": points
            })

        df = pd.DataFrame(lista).sort_values("Posição").reset_index(drop=True)
        return df

    except Exception as e:
        return f"Erro ao buscar Top 30: {e}"

    finally:
        driver.quit()

def buscar_lineup_furia():
    driver = criar_driver()
    try:
        driver.get('https://www.hltv.org/team/8297/furia#tab-rosterBox')
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "playerNickname"))
        )

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        players = soup.find_all("div", class_="playerNickname")

        jogadores = [p.text.strip() for p in players]
        return jogadores, "Coach não capturado"

    except Exception as e:
        return [], "Erro ao capturar lineup"

    finally:
        driver.quit()
