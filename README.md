## Pré-requisitos

- Python 3 instalado
- Playwright instalado
- Navegador Chromium disponível pelo Playwright

## Instalação

- Caso ainda não tenha esse projeto no seu computador, clone o repositório com esse código:

```bash
git clone https://github.com/viniciusnunesdito/desafio_ibge_1209
```

- Com o python instalado em sua máquina, basta abrir esse projeto e fazer essas instalações:

```bash
pip install playwright
playwright install chromium
```

## Execução

- Estando com tudo instalado e com o projeto no seu computador, basta utilizar esse comando para executar a automação:

```bash
python main.py
```

## Desafios encontrados

- Sei utilizar muito bem o Selenium, porém após fazer pesquisas, percebi que o playwright poderia ser mais eficiente para o site do SIDRA/IBGE, então tive o desafio de aprender essa tecnologia para utilizar nesse projeto, porém achei ele muito parecido com o Selenium.

- No momento de configurar os filtros das tabelas de grupo de idade e ano da pesquisa, preferi utilizar um método mais trabalhoso, porém mais versátil em caso de mudanças no site. Em vez de usar diretamente os seletores "≥ 60" na tabela de grupos de idade e selecionar o primeiro dado na tabela do ano da pesquisa (que, no estado atual do site, corresponde à opção mais recente), considerei mais adequado criar funções para identificar e selecionar as opções corretas para essa automação, independentemente da posição das caixas de seleção (checkboxes).

- O filtro de Unidade Territorial não utiliza o mesmo tipo de tabela, ele utiliza árvores, então tive que mudar um pouco a abordagem no momento de filtrar somente pela Unidade da Federação, pois se eu "descesse" todos os níveis das árvores, acabaria por desmarcar "Em Grande Região" após ter marcado a árvore pai que é a "Unidade da Federação".

- Na parte do download aprendi a usar o expect_download(), coisa que eu não havia feito anteriormente com Selenium, e até onde sei, o Selenium não tem algo para monitorar downloads.