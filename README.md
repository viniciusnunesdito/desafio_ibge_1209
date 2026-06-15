# Desafio Técnico – Automação RPA SIDRA/IBGE

Automação que navega pelo site do SIDRA/IBGE, localiza a tabela **1209** (População por grupos de idade), configura os filtros para **60 anos ou mais** segmentados por **Unidades da Federação**, e faz o download dos dados em CSV.

---

## Pré-requisitos

- Python 3 instalado
- pip

---

## Instalação

Caso ainda não tenha o Python instalado, baixe em: https://www.python.org/downloads/

Caso ainda não tenha esse projeto no seu computador, clone o repositório:

```bash
git clone https://github.com/viniciusnunesdito/desafio_ibge_1209
```

Abra o projeto e instale as depêndencias abaixo:

```bash
pip install playwright
playwright install chromium
```

---

## Execução

```bash
python desafio_ibge_1209.py
```

---

## Dependências

| Pacote | Função |
|---|---|
| `playwright` | Automação de browser (Chromium) |

---

## Estratégia adotada

A automação inicia obrigatoriamente pela homepage `https://sidra.ibge.gov.br/` e localiza a tabela 1209 através do campo de busca interno do site — digitando "1209" e clicando em OK — sem acessar a URL da tabela diretamente.

Após acessar a tabela, os filtros são configurados na seguinte ordem:

1. **Variável** — seleciona apenas "População (Pessoas)"
2. **Grupo de idade** — desmarca todos e seleciona apenas os grupos de 60 anos ou mais, usando regex para identificar as faixas etárias independente de como o site as nomeia
3. **Ano** — lê todos os anos disponíveis dinamicamente e seleciona o mais recente, sem assumir que ele sempre estará em uma posição fixa na lista
4. **Unidade territorial** — navega pela árvore de níveis territoriais e seleciona apenas "Unidade da Federação", sem descer nos níveis filhos

Por fim, o modal de download é aberto, o formato CSV (BR) é selecionado e o arquivo é salvo automaticamente em `dados/populacao_60mais_1209.csv`.

---

## Principais desafios encontrados

**Aprendizado do Playwright**
Tenho experiência com Selenium, porém após pesquisar percebi que o Playwright seria mais eficiente para o site do SIDRA/IBGE. Achei a transição tranquila pois as duas ferramentas são bastante parecidas.

**Seleção dos grupos de idade**
Em vez de usar seletores fixos assumindo que os grupos "60+" sempre terão os mesmos nomes e posições, criei uma função com regex que identifica qualquer grupo cuja faixa etária comece em 60 ou mais — tornando o script resistente a mudanças no site.

**Seleção do ano mais recente**
Em vez de assumir que o ano mais recente sempre estará no topo da lista, o script lê todos os anos disponíveis, compara os valores e seleciona o maior — independente da ordem em que aparecem.

**Árvore de territórios**
O filtro de Unidade Territorial usa uma estrutura de árvore diferente dos outros painéis. Foi necessário iterar apenas pelos itens de primeiro nível da árvore para não descer nos estados filhos e desmarcar inadvertidamente os territórios corretos.

**Download com expect_download()**
O Playwright oferece o `expect_download()` para capturar o evento real de download antes de clicar no botão, algo que o Selenium não tem de forma nativa e que exigiria monitorar a pasta de downloads manualmente. Essa função foi uma novidade, pois é a primeira vez que utilizo Playwright.