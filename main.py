from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    navegador = pw.chromium.launch(headless=False)
    pagina = navegador.new_page()
    pagina.goto("https://sidra.ibge.gov.br/home/ipca/brasil")
    pagina.get_by_title("Pesquisa Tabela").click()
    pagina.get_by_role("textbox", name="pesquisar").fill("1209")
    pagina.get_by_role("button", name="OK").click()

    navegador.close()