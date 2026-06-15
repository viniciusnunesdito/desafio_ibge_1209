import re
import time
from playwright.sync_api import sync_playwright

# Estou usando time.sleep() apenas para testes, após confirmar que o script funciona, substituirei por esperas explícitas do Playwright, para garantir que os elementos estejam prontos para interação antes de clicar ou ler seus valores.

def mais_60(texto: str) -> bool:

    # Captura apenas números de 1 a 3 dígitos, pois identifiquei opções que trazem anos como 2000, 1991 e o importante mesmo são os grupos de idade nesse contexto.
    numeros = re.findall(r'\b\d{1,3}\b', texto)
    if not numeros:
        return False

    return int(numeros[0]) >= 60


def selecionar_grupos(pagina, seletor_wrapper):

    pagina.get_by_role("button", name="Alternar soma dos elementos").click()
    time.sleep(1)
    # Desmarca todos os grupos de idade antes de selecionar para garantir que nenhum grupo indesejado permaneça selecionado, pois o site tem checkboxes pré-selecionadas.
    pagina.locator("#panel-C58-collapse").get_by_role(
        "button", name="Desmarcar todos os elementos"
    ).click()
    time.sleep(1)

    # Usei regex para identificar os grupos de idade, ao invés de assumir que os grupos "60+" sempre terão os mesmos nomes e posições na lista, tornando o script mais versátil a mudanças no site.
    wrapper = pagina.locator(seletor_wrapper)
    itens = wrapper.locator(".item-lista")
    total = itens.count()
    print(f"Total de grupos de idade encontrados: {total}")

    selecionados = 0
    for i in range(total):
        item = itens.nth(i)

        nome_loc = item.locator("span.nome")
        if nome_loc.count() == 0:
            continue

        nome = nome_loc.inner_text().strip()

        if not mais_60(nome):
            print(f"  [ignorado] {nome}")
            continue

        botao = item.locator("button.sidra-toggle")
        if botao.get_attribute("aria-selected") == "true":
            print(f"  ℹ️ Já selecionado: {nome}")
        else:
            botao.click()
            time.sleep(0.5)
            print(f"  ✓ Selecionado: {nome}")

        selecionados += 1

    if selecionados == 0:
        raise RuntimeError(
            "Nenhum grupo de 60+ encontrado. "
            "Verifique se o painel de grupos de idade carregou corretamente."
        )

    print(f"\n✅ {selecionados} grupos de 60+ selecionados.")


def selecionar_ano_mais_recente(pagina, seletor_wrapper):

    # Desmarca todos as opções antes de selecionar para garantir que nada indesejado permaneça selecionado, pois o site tem checkboxes pré-selecionadas.
    pagina.locator("#panel-P-collapse").get_by_role(
        "button", name="Desmarcar todos os elementos"
    ).click()
    time.sleep(2)

    # Leitura de todos os anos disponíveis para identificar o mais recente, ao invés de assumir que o mais recente SEMPRE estará no topo da lista
    wrapper = pagina.locator(seletor_wrapper)
    itens = wrapper.locator(".item-lista")
    total = itens.count()
    print(f"Total de períodos encontrados: {total}")

    ano_mais_recente = None
    indice_mais_recente = None

    for i in range(total):
        item = itens.nth(i)

        nome_loc = item.locator("span.nome")
        if nome_loc.count() == 0:
            continue

        nome = nome_loc.inner_text().strip()

        if not nome.isdigit():
            continue

        ano = int(nome)
        print(f"  [{i}] {ano}")

        if ano_mais_recente is None or ano > ano_mais_recente:
            ano_mais_recente = ano
            indice_mais_recente = i

    if indice_mais_recente is not None:
        print(f"\nAno mais recente: {ano_mais_recente}")

        botao = itens.nth(indice_mais_recente).locator("button.sidra-toggle")
        if botao.get_attribute("aria-selected") == "true":
            print("ℹJá estava selecionado.")
        else:
            print("Clicando para selecionar...")
            botao.click()
            time.sleep(2)
    else:
        print("Nenhum ano encontrado.")


with sync_playwright() as pw:
    navegador = pw.chromium.launch(headless=False)
    pagina = navegador.new_page()

    # Acesso à página inicial e acesso à tabela 1209
    pagina.goto("https://sidra.ibge.gov.br/home/ipca/brasil")
    pagina.get_by_title("Pesquisa Tabela").click()
    pagina.get_by_role("textbox", name="pesquisar").fill("1209")
    pagina.get_by_role("button", name="OK").click()
    time.sleep(2)

    # Filtro: grupo de idade
    selecionar_grupos(
        pagina,
        "#panel-C58-collapse > .janela-borda-dados > .janela-dados > .wrapper-lista",
    )

    # Filtro: ano da pesquisa
    selecionar_ano_mais_recente(
        pagina,
        "#panel-P-collapse > .janela-borda-dados > .janela-dados > .wrapper-lista",
    )

    # Filtro: Unidade territorial

    navegador.close()