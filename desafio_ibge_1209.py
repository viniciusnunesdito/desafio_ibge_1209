import re
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

OUTPUT_DIR = Path("dados")
OUTPUT_FILE = OUTPUT_DIR / "populacao_60mais_1209.csv"
TIMEOUT = 30000


def setup_output_dir():
    """Cria a pasta de saída caso não exista."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✅ Pasta de saída pronta: {OUTPUT_DIR.resolve()}")


def selecionar_variavel(pagina):
    try:
        pagina.locator("#panel-V-collapse").get_by_role(
            "button", name="Desmarcar todos os elementos"
        ).wait_for(timeout=TIMEOUT)
        pagina.locator("#panel-V-collapse").get_by_role(
            "button", name="Desmarcar todos os elementos"
        ).click()

        pagina.locator("div").filter(has_text=re.compile(r"^População \(Pessoas\)$")).nth(3).wait_for(timeout=TIMEOUT)
        pagina.locator("div").filter(has_text=re.compile(r"^População \(Pessoas\)$")).nth(3).click()
        print("✅ Variável 'População (Pessoas)' selecionada.")
    except PlaywrightTimeoutError:
        raise RuntimeError("Timeout ao configurar o filtro de variável.")


def mais_60(texto: str) -> bool:
    # Captura apenas números de 1 a 3 dígitos, pois identifiquei opções que trazem anos como 2000, 1991
    # e o importante mesmo são os grupos de idade nesse contexto.
    numeros = re.findall(r'\b\d{1,3}\b', texto)
    if not numeros:
        return False

    return int(numeros[0]) >= 60


def selecionar_grupos(pagina, seletor_wrapper):
    try:
        pagina.get_by_role("button", name="Alternar soma dos elementos").wait_for(timeout=TIMEOUT)
        pagina.get_by_role("button", name="Alternar soma dos elementos").click()

        pagina.locator("#panel-C58-collapse").get_by_role(
            "button", name="Desmarcar todos os elementos"
        ).wait_for(timeout=TIMEOUT)
        # Desmarca todos os grupos de idade antes de selecionar para garantir que nenhum grupo
        # indesejado permaneça selecionado, pois o site tem checkboxes pré-selecionadas.
        pagina.locator("#panel-C58-collapse").get_by_role(
            "button", name="Desmarcar todos os elementos"
        ).click()

        wrapper = pagina.locator(seletor_wrapper)
        wrapper.wait_for(timeout=TIMEOUT)

        # Usei regex para identificar os grupos de idade, ao invés de assumir que os grupos "60+"
        # sempre terão os mesmos nomes e posições na lista, tornando o script mais versátil a mudanças no site.
        itens = wrapper.locator(".item-lista")
        itens.first.wait_for(timeout=TIMEOUT)

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
                print(f"  ✓ Selecionado: {nome}")

            selecionados += 1

        if selecionados == 0:
            raise RuntimeError(
                "Nenhum grupo de 60+ encontrado. "
                "Verifique se o painel de grupos de idade carregou corretamente."
            )

        print(f"\n✅ {selecionados} grupos de 60+ selecionados.")

    except PlaywrightTimeoutError:
        raise RuntimeError("Timeout ao configurar o filtro de grupos de idade.")


def selecionar_ano_mais_recente(pagina, seletor_wrapper):
    try:
        pagina.locator("#panel-P-collapse").get_by_role(
            "button", name="Desmarcar todos os elementos"
        ).wait_for(timeout=TIMEOUT)
        # Desmarca todas as opções antes de selecionar para garantir que nada indesejado permaneça
        # selecionado, pois o site tem checkboxes pré-selecionadas.
        pagina.locator("#panel-P-collapse").get_by_role(
            "button", name="Desmarcar todos os elementos"
        ).click()

        wrapper = pagina.locator(seletor_wrapper)
        wrapper.wait_for(timeout=TIMEOUT)

        itens = wrapper.locator(".item-lista")
        itens.first.wait_for(timeout=TIMEOUT)

        total = itens.count()
        print(f"Total de períodos encontrados: {total}")

        ano_mais_recente = None
        indice_mais_recente = None

        # Leitura de todos os anos disponíveis para identificar o mais recente, ao invés de assumir
        # que o mais recente SEMPRE estará no topo da lista.
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

        if indice_mais_recente is None:
            raise RuntimeError("Nenhum ano encontrado no painel de períodos.")

        print(f"\nAno mais recente: {ano_mais_recente}")

        botao = itens.nth(indice_mais_recente).locator("button.sidra-toggle")
        if botao.get_attribute("aria-selected") == "true":
            print("ℹ️ Já estava selecionado.")
        else:
            botao.click()
            botao.wait_for(timeout=TIMEOUT)
            print(f"✅ Ano {ano_mais_recente} selecionado.")

    except PlaywrightTimeoutError:
        raise RuntimeError("Timeout ao configurar o filtro de ano.")


def selecionar_unidades_federacao(pagina):
    try:
        pagina.locator("#arvore-niveis > li").first.wait_for(timeout=TIMEOUT)

        itens = pagina.locator("#arvore-niveis > li")
        total = itens.count()
        print(f"Total de níveis encontrados: {total}")

        for i in range(total):
            item = itens.nth(i)

            nome_loc = item.locator("> div.item-arvore > div.nome-arvore > div.sidra-check > span.nome")
            if nome_loc.count() == 0:
                continue

            nome = nome_loc.inner_text().strip()
            botao = item.locator("> div.item-arvore > div.nome-arvore > div.sidra-check > button.sidra-toggle")
            selecionado = botao.get_attribute("aria-selected") == "true"

            if "Unidade da Federação" in nome or "UF" in nome.upper():
                if not selecionado:
                    botao.click()
                    botao.wait_for(timeout=TIMEOUT)
                print(f"  ✓ Selecionado: {nome}")
            else:
                if selecionado:
                    botao.click()
                    botao.wait_for(timeout=TIMEOUT)
                print(f"  ✗ Desmarcado: {nome}")

        print("\n✅ Filtro territorial configurado.")

    except PlaywrightTimeoutError:
        raise RuntimeError("Timeout ao configurar o filtro de unidade territorial.")


def fazer_download(pagina):
    """
    Abre o modal de Download, seleciona CSV (BR) e salva em dados/populacao_60mais_1209.csv.
    Usa expect_download() para capturar o evento real de download.
    """
    try:
        print("Abrindo modal de download...")

        pagina.locator("#botao-downloads").wait_for(timeout=TIMEOUT)
        pagina.locator("#botao-downloads").click()

        pagina.locator("#modal-downloads select.select-formato-arquivo").wait_for(timeout=TIMEOUT)
        pagina.locator("#modal-downloads select.select-formato-arquivo").select_option(value="br.csv")

        print("Baixando arquivo...")
        with pagina.expect_download(timeout=TIMEOUT) as download_info:
            pagina.locator("#opcao-downloads").click()

        download = download_info.value
        download.save_as(OUTPUT_FILE)
        print(f"✅ Arquivo salvo em: {OUTPUT_FILE.resolve()}")

    except PlaywrightTimeoutError:
        raise RuntimeError("Timeout ao tentar fazer o download do arquivo.")


with sync_playwright() as pw:
    navegador = pw.chromium.launch(headless=True)
    pagina = navegador.new_page()

    try:
        # Cria a pasta dados/ antes de qualquer coisa
        setup_output_dir()

        # Acesso à página inicial e acesso à tabela 1209
        pagina.goto("https://sidra.ibge.gov.br/")
        pagina.get_by_title("Pesquisa Tabela").wait_for(timeout=TIMEOUT)
        pagina.get_by_title("Pesquisa Tabela").click()

        pagina.get_by_role("textbox", name="pesquisar").wait_for(timeout=TIMEOUT)
        pagina.get_by_role("textbox", name="pesquisar").fill("1209")
        pagina.get_by_role("button", name="OK").click()

        pagina.wait_for_load_state("networkidle", timeout=TIMEOUT)

        # Filtro: Variável — População (Pessoas)
        selecionar_variavel(pagina)

        # Filtro: Grupo de idade — 60 anos ou mais
        selecionar_grupos(
            pagina,
            "#panel-C58-collapse > .janela-borda-dados > .janela-dados > .wrapper-lista",
        )

        # Filtro: Ano da pesquisa — mais recente disponível
        selecionar_ano_mais_recente(
            pagina,
            "#panel-P-collapse > .janela-borda-dados > .janela-dados > .wrapper-lista",
        )

        # Filtro: Unidade territorial — Unidade da Federação
        selecionar_unidades_federacao(pagina)

        # Download do CSV
        fazer_download(pagina)

    except RuntimeError as e:
        print(f"\n❌ Erro: {e}")
        pagina.screenshot(path=str(OUTPUT_DIR / "erro_screenshot.png"))
        print(f"Screenshot salvo em: {OUTPUT_DIR / 'erro_screenshot.png'}")

    finally:
        navegador.close()