# Mini-Projeto Avaliativo - Análise Exploratória da Base Varejo SENAI SCTEC

**Curso:** Análise de Dados com Python [T2]
**Módulo:** 1 - Semana 07
**Tema:** Análise Exploratória de Dados aplicada ao varejo

## 1. Sobre o projeto

Este projeto realiza uma Análise Exploratória de Dados sobre a base `Varejo.csv`, com o objetivo de transformar uma base bruta de compras em uma versão mais limpa, organizada e adequada para análises.

Durante o processo do desenvolvimento, foram aplicadas etapas de carregamento, diagnóstico, limpeza, padronização, validação e geração de estatísticas descritivas. A análise foi feita principalmente com `pandas`, mas também foi utilizada leitura nativa com `csv.DictReader` para demonstrar uma inspeção inicial do arquivo CSV.

Como a base não possui uma coluna de valor monetário, a análise foi conduzida com foco em volume de registros, quantidade de compras únicas e frequência de produtos, categorias, segmentos e clientes.

## 2. Estrutura do repositório

projeto_avaliativo_varejo
│
├── dados/
│   └── Varejo.csv
│
├── saidas/
│   ├── varejo_limpo.csv
│   └── saida_terminal.txt
│
├── miniprojeto_varejo.py
└── README.md

## 3. Como executar o projeto

### Execução no VS Code

1. Abra a pasta do projeto no VS Code.
2. Verifique se o arquivo `Varejo.csv` está dentro da pasta `dados/`.
3. Abra o terminal na pasta do projeto.
4. Execute o comando:

python miniprojeto_varejo.py

Ao final da execução, o programa exibe um relatório no terminal e salva a base tratada na pasta `saidas/`.

## 4. Bibliotecas utilizadas

* `pandas`: leitura, limpeza, transformação, agrupamento e análise dos dados.
* `numpy`: tratamento de valores nulos com `np.nan`.
* `csv`: leitura nativa estruturada do arquivo CSV.
* `datetime`: conversão de strings de data para o formato de data.
* `pathlib`: organização dos caminhos dos arquivos no projeto.

## 5. Etapas realizadas

### 5.1 Leitura e inspeção inicial

A base foi carregada inicialmente com `csv.DictReader`, usando recursos nativos do Python. Essa etapa permitiu verificar as colunas, a quantidade de registros e o primeiro registro da base.

Depois disso, a análise principal foi feita com `pandas.read_csv()`, utilizando separador `;` e encoding `latin1`.

### 5.2 Diagnóstico da base

Foram analisados:

* quantidade de linhas e colunas;
* tipos de dados;
* valores nulos;
* duplicatas;
* colunas vazias geradas por separadores extras;
* categorias inconsistentes;
* datas inválidas;
* consistência do identificador de compra.

### 5.3 Limpeza e padronização dos dados

Durante a limpeza, foram realizadas as seguintes ações:

* remoção de colunas vazias;
* conversão de textos como `NULL`, `N/A` e campos vazios para valores nulos reais;
* padronização de textos com remoção de espaços extras;
* conversão de colunas de identificação para tipo inteiro;
* preenchimento de categorias vazias ou inconsistentes com `Sem Categoria`;
* tratamento de nulos nas dimensões de cliente e produto;
* conversão da coluna `DATA` usando o módulo `datetime`;
* validação da regra do identificador de compra;
* remoção de duplicatas relevantes;
* geração de uma base limpa em CSV.

### 5.4 Tratamento de categorias e nulos

A coluna de categoria do produto (`PR_CAT`) recebeu um tratamento específico. Quando a categoria estava vazia, nula ou com valor inconsistente, como `#N/D`, ela foi preenchida com `Sem Categoria`.

Também foram tratados nulos em campos dimensionais:

* `CL_GENERO`, `CL_SEG` e `PR_NOME`: preenchidos com `Nao informado`, para preservar os registros de compra sem inventar uma categoria específica.
* `CL_FHL`: preenchido com a mediana, pois é uma coluna numérica e a mediana reduz o impacto de valores extremos.
* `CL_EC`: preenchido com a moda, por representar uma dimensão categórica/codificada.

### 5.5 Validação da regra de compra

Foi validada a regra do identificador de compra (`CO_ID`). A lógica verifica se um mesmo número de compra está associado a mais de uma data ou a mais de um cliente.

Caso isso aconteça, os registros são separados como inconsistentes. Essa etapa ajuda a garantir que o identificador da compra represente corretamente uma única transação.

### 5.6 Estatísticas descritivas

A coluna `CL_FHL`, que representa o número de filhos dos clientes, foi analisada com estatísticas básicas:

* contagem;
* média;
* mediana;
* desvio padrão;
* moda;
* mínimo;
* quartil 25%;
* quartil 50%;
* quartil 75%;
* máximo.

### 5.7 Agrupamentos

Foram criados agrupamentos para observar padrões na base por:

* gênero do cliente;
* categoria do produto;
* segmento econômico;
* ano da compra;
* produtos mais frequentes.

Como não há coluna de valor monetário, os agrupamentos foram analisados com base na quantidade de itens e na quantidade de compras únicas.

## 6. Principais resultados da limpeza

Após o tratamento dos dados, foram obtidos os seguintes resultados:

* A base original possuía 830.000 registros e 14 colunas.
* Foram identificadas e removidas 4 colunas extras vazias.
* A base final ficou com 733.447 registros e 10 colunas.
* Foram removidas 96.553 duplicatas relevantes.
* Foram encontradas 3.650 categorias inconsistentes, tratadas como `Sem Categoria`.
* Não foram encontradas datas inválidas nem inconsistências entre `CO_ID`, `DATA` e `CL_ID`.

## 7. Insights obtidos na análise

1. A categoria **ALIMENTOS** concentra o maior volume de itens registrados na base.

2. O segmento econômico **B** apresenta o maior volume de itens, compras e clientes.

3. Clientes do gênero **F** aparecem com maior quantidade de itens e compras em comparação ao gênero **M**.

4. A moda e a mediana da coluna `CL_FHL` são 0, indicando predominância de clientes sem filhos registrados.

5. O ano de **2021** apresentou o maior volume de itens e compras no recorte analisado.

6. A existência da categoria `#N/D` mostra um problema de qualidade na origem dos dados, tratado no projeto como `Sem Categoria`.

## 8. Reflexão sobre ETL e qualidade de dados

Este projeto segue uma lógica de ETL, composta por três etapas principais:

* **Extração:** leitura da base bruta `Varejo.csv`, primeiro com `csv.DictReader` e depois com `pandas`.
* **Transformação:** limpeza dos dados, tratamento de nulos, padronização de textos, conversão de tipos, validação de datas, validação de regras de negócio e remoção de duplicatas.
* **Carga:** geração do arquivo `varejo_limpo.csv`, salvo na pasta `saidas/`.

A etapa de transformação foi essencial no projeto, porque uma análise feita sobre dados inconsistentes pode gerar interpretações erradas. Por exemplo, categorias vazias, duplicatas e tipos incorretos podem alterar a contagem de produtos, clientes e compras.

De acordo com o que aprendemos no curso com a prof Amanda, antes de criar dashboards, gráficos ou tomar decisões com base nos números, é necessário garantir que os dados estejam consistentes, documentados e preparados para uso. Neste projeto, a limpeza da base permitiu tornar os dados mais confiáveis e adequados para análises futuras.

## 9. Observações finais

A base utilizada não possui coluna de valor monetário. Por isso, não foi possível calcular métricas como faturamento, ticket médio ou receita por categoria.

Este mini-projeto foi importante para praticar uma etapa fundamental da análise de dados: preparar a base antes de tirar conclusões.
A partir da limpeza, do tratamento de inconsistências e dos agrupamentos, foi possível transformar dados brutos em informações mais organizadas e úteis para análises, relatórios ou futuros dashboards.

