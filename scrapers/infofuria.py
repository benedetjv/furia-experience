# scrapers/infofuria.py

from playwright.async_api import async_playwright

async def buscar_semanas_top30():
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto('https://www.hltv.org/team/8297/furia#tab-infoBox')
            await page.wait_for_selector('.team-statline')

            statlines = await page.locator('.team-statline').all_text_contents()

            for stat in statlines:
                if "Weeks in top30 for core" in stat:
                    semanas = stat.split(":")[-1].strip()
                    await browser.close()
                    return f"A FURIA esteve no Top 30 da HLTV por {semanas} semanas!"

            await browser.close()
            return "Não encontrei a informação sobre semanas no Top 30."

    except Exception as e:
        return f"Erro ao buscar semanas no Top 30: {e}"

async def buscar_conquistas():
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto('https://www.hltv.org/team/8297/furia#tab-achievementsBox')
            await page.wait_for_selector('.achievement-row')

            conquistas = await page.locator('.achievement-row').all_text_contents()

            maiores_conquistas = [c for c in conquistas if any(x in c.lower() for x in ['major', 'lan', 'masters', 'grand slam'])]

            await browser.close()

            if maiores_conquistas:
                resposta = "Principais conquistas da FURIA:\n" + "\n".join(f"- {c}" for c in maiores_conquistas)
                return resposta
            else:
                return "Não encontrei conquistas de Major ou LAN."

    except Exception as e:
        return f"Erro ao buscar conquistas: {e}"

async def buscar_ultimas_partidas():
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto('https://www.hltv.org/team/8297/furia#tab-matchesBox')
            await page.wait_for_selector('.matchInfo')

            partidas = await page.locator('.matchInfo').all_text_contents()
            resultados = await page.locator('td.result').all_text_contents()

            resposta = []
            for i in range(min(5, len(partidas))):
                resultado = resultados[i].strip()
                adversario = partidas[i].strip()

                placar = resultado.split(":")
                if len(placar) == 2:
                    furia_score = int(placar[0].strip())
                    adversario_score = int(placar[1].strip())

                    status = "Venceu" if furia_score > adversario_score else "Perdeu"
                    resposta.append(f"{status} contra {adversario} ({resultado})")

            await browser.close()

            if resposta:
                return "Últimos 5 jogos da FURIA:\n" + "\n".join(f"- {r}" for r in resposta)
            else:
                return "Não encontrei últimas partidas da FURIA."

    except Exception as e:
        return f"Erro ao buscar últimas partidas: {e}"
