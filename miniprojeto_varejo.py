"""
Mini-Projeto Avaliativo - Modulo 1 - Semana 07
Analise Exploratória de Dados aplicada a base Varejo

Objetivo:
- Carregar, diagnosticar, limpar e sumarizar a base Varejo.csv.
- Gerar estatisticas descritivas sobre numero de filhos dos clientes.
- Explorar padroes de agrupamento com pandas.
- Salvar uma versao limpa da base e exibir um relatorio final no terminal.

Execucao:
    python miniprojeto_varejo.py
"""

import csv
from pathlib import Path

import numpy as np
import pandas as pd
from datetime import datetime


# 1. CONFIGURACOES DO PROJETO

BASE_DIR = Path(__file__).resolve().parent
CAMINHO_DADOS = BASE_DIR / "dados" / "Varejo.csv"
CAMINHO_SAIDA = BASE_DIR / "saidas" / "varejo_limpo.csv"

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 120)


# 2. LEITURA NATIVA COM csv.DictReader

def inspecionar_csv_nativo(caminho: Path, delimitador: str = ";") -> None:
    """
    Faz uma inspecao inicial usando recursos nativos do Python.
    Isso demonstra leitura estruturada com csv.DictReader antes da analise em pandas.
    """
    with open(caminho, mode="r", encoding="latin1", newline="") as arquivo:
        leitor = csv.DictReader(arquivo, delimiter=delimitador)
        colunas = leitor.fieldnames

        total_linhas = 0
        primeira_linha = None

        for linha in leitor:
            total_linhas += 1
            if primeira_linha is None:
                primeira_linha = linha

    print("\n--- INSPECAO NATIVA DO CSV ---")
    print(f"Arquivo: {caminho.name}")
    print(f"Total de registros lidos com csv.DictReader: {total_linhas}")
    print(f"Colunas identificadas: {colunas}")
    print(f"Primeiro registro: {primeira_linha}")


# 3. FUNCOES DE LIMPEZA

def limpar_colunas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove colunas vazias geradas por separadores extras no CSV e padroniza nomes.
    """
    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    colunas_vazias = [
        coluna for coluna in df.columns
        if coluna.startswith("Unnamed") or df[coluna].isna().all()
    ]

    df = df.drop(columns=colunas_vazias)
    return df


def padronizar_textos(df: pd.DataFrame, colunas: list[str]) -> pd.DataFrame:
    """
    Remove espacos extras em colunas de texto.
    """
    df = df.copy()
    for coluna in colunas:
        if coluna in df.columns:
            df[coluna] = df[coluna].astype("string").str.strip()
    return df


def converter_coluna_inteira(df: pd.DataFrame, coluna: str) -> pd.DataFrame:
    """
    Converte uma coluna para numero inteiro, aceitando valores vindos como string.
    A expressao regular remove caracteres que nao fazem parte de numeros.
    """
    serie_limpa = (
        df[coluna]
        .astype("string")
        .str.strip()
        .str.replace(r"[^0-9,\.\-]", "", regex=True)
        .str.replace(",", ".", regex=False)
    )
    df[coluna] = pd.to_numeric(serie_limpa, errors="coerce").astype("Int64")
    return df


def converter_data(valor):
    """
    Converte data no formato brasileiro dd/mm/aaaa usando o modulo datetime.
    Datas invalidas retornam pd.NaT para posterior diagnostico.
    """
    try:
        return datetime.strptime(str(valor).strip(), "%d/%m/%Y")
    except (ValueError, TypeError):
        return pd.NaT


def tratar_categoria(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preenche categorias vazias ou inconsistentes com 'Sem Categoria'.

    A lógica usa if/else explicitamente para atender ao critério do projeto:
    se a categoria estiver vazia, nula ou inconsistente, recebe 'Sem Categoria';
    caso contrário, mantém a categoria original padronizada.
    """
    df = df.copy()
    categorias_invalidas = ["", "NULL", "N/A", "#N/D", "NAN", "<NA>"]

    def corrigir_categoria(valor):
        if pd.isna(valor):
            return "Sem Categoria"

        valor_limpo = str(valor).strip()

        if valor_limpo.upper() in categorias_invalidas:
            return "Sem Categoria"
        else:
            return valor_limpo

    df["PR_CAT"] = df["PR_CAT"].apply(corrigir_categoria).astype("string")

    return df


def tratar_nulos_dimensoes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Trata nulos das dimensões de cliente e produto.

    Justificativas:
    - CL_GENERO, CL_SEG e PR_NOME são campos descritivos. Por isso, os nulos
      são preenchidos com 'Nao informado' para preservar os registros de compra.
    - CL_FHL é um campo numérico discreto. A mediana foi escolhida porque reduz
      o impacto de valores extremos.
    - CL_EC é uma dimensão codificada/categórica. A moda foi escolhida porque
      representa o valor mais frequente da coluna.
    """
    df = df.copy()

    for coluna in ["CL_GENERO", "CL_SEG", "PR_NOME"]:
        if coluna in df.columns:
            df[coluna] = df[coluna].fillna("Nao informado")

    if "CL_FHL" in df.columns:
        mediana_filhos = df["CL_FHL"].median()
        df["CL_FHL"] = df["CL_FHL"].fillna(mediana_filhos)
        df["CL_FHL"] = df["CL_FHL"].astype("Int64")

    if "CL_EC" in df.columns and df["CL_EC"].isna().any():
        moda_estado_civil = df["CL_EC"].mode(dropna=True)[0]
        df["CL_EC"] = df["CL_EC"].fillna(moda_estado_civil)

    return df

def validar_identificador_compra(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Valida a regra de negocio do CO_ID.
    Um mesmo numero de compra deve estar ligado a uma unica data e a um unico cliente.
    Se houver inconsistencias, os registros sao separados para analise.
    """
    validacao = df.groupby("CO_ID").agg(
        qtd_datas=("DATA", "nunique"),
        qtd_clientes=("CL_ID", "nunique")
    )

    compras_invalidas = validacao[
        (validacao["qtd_datas"] > 1) |
        (validacao["qtd_clientes"] > 1)
    ].index

    df_inconsistente = df[df["CO_ID"].isin(compras_invalidas)].copy()
    df_valido = df[~df["CO_ID"].isin(compras_invalidas)].copy()

    return df_valido, df_inconsistente

# 4. PIPELINE PRINCIPAL

def carregar_dados(caminho: Path) -> pd.DataFrame:
    """
    Carrega a base com pandas.
    O arquivo usa ponto e virgula como separador.
    """
    return pd.read_csv(caminho, sep=";", encoding="latin1")


def limpar_base(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Executa o pipeline de limpeza exigido no mini-projeto.
    """
    relatorio = {}
    df = df.copy()

    relatorio["shape_original"] = df.shape

    # Remove colunas vazias extras e padroniza nomes.
    df = limpar_colunas(df)
    relatorio["shape_sem_colunas_vazias"] = df.shape

    # Converte strings que representam nulos em nulo real do pandas/numpy.
    df = df.replace({
        "NULL": np.nan,
        "N/A": np.nan,
        "": np.nan,
        " ": np.nan
    })

    # Padroniza campos de texto.
    colunas_texto = ["CL_GENERO", "CL_SEG", "PR_CAT", "PR_NOME"]
    df = padronizar_textos(df, colunas_texto)

    # Converte colunas inteiras. IDs nulos sao considerados registros invalidos.
    colunas_inteiras = ["CO_ID", "CL_ID", "CL_EC", "CL_FHL", "PR_ID"]
    for coluna in colunas_inteiras:
        df = converter_coluna_inteira(df, coluna)

    # Remove registros sem identificadores essenciais.
    linhas_antes_ids = len(df)
    df = df.dropna(subset=["CO_ID", "CL_ID", "PR_ID"])
    relatorio["linhas_removidas_ids_nulos"] = linhas_antes_ids - len(df)

    # Trata categoria vazia/inconsistente com lógica if/else.
    qtd_categoria_inconsistente = df["PR_CAT"].isna().sum() + (df["PR_CAT"] == "#N/D").sum()
    df = tratar_categoria(df)
    relatorio["categorias_preenchidas_sem_categoria"] = int(qtd_categoria_inconsistente)

    # Trata nulos das dimensões de cliente/produto com justificativas próprias.
    df = tratar_nulos_dimensoes(df)

    # Conversao de data usando o modulo datetime.
    # A funcao converter_data utiliza datetime.strptime para converter strings
    # no formato brasileiro dd/mm/aaaa. Datas invalidas retornam pd.NaT.
    df["DATA"] = df["DATA"].apply(converter_data)
    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")

    relatorio["datas_invalidas"] = int(df["DATA"].isna().sum())
    df = df.dropna(subset=["DATA"])

    # Valida regra do identificador de compra.
    df, df_compras_inconsistentes = validar_identificador_compra(df)
    relatorio["registros_compra_inconsistentes"] = int(len(df_compras_inconsistentes))

    # Remove duplicatas relevantes.
    # Como nao existe coluna de quantidade, linhas identicas de compra/produto sao tratadas como duplicadas.
    linhas_antes_duplicatas = len(df)
    colunas_duplicidade = [
        "DATA", "CO_ID", "CL_ID", "CL_GENERO", "CL_EC",
        "CL_FHL", "CL_SEG", "PR_ID", "PR_CAT", "PR_NOME"
    ]
    df = df.drop_duplicates(subset=colunas_duplicidade, keep="first")
    relatorio["duplicatas_removidas"] = int(linhas_antes_duplicatas - len(df))

    # Reindexa a base apos remocoes.
    df = df.reset_index(drop=True)
    relatorio["shape_final"] = df.shape

    return df, relatorio


# 5. ANALISES E RELATORIOS

def diagnosticar_base(df: pd.DataFrame, titulo: str) -> None:
    """
    Exibe diagnosticos basicos da base.
    """
    print(f"\n--- {titulo} ---")
    print(f"Registros: {df.shape[0]}")
    print(f"Colunas: {df.shape[1]}")
    print("\nTipos de dados:")
    print(df.dtypes)
    print("\nValores nulos por coluna:")
    print(df.isna().sum())
    print(f"\nDuplicatas exatas: {df.duplicated().sum()}")


def estatisticas_filhos(df: pd.DataFrame) -> pd.Series:
    """
    Gera estatisticas descritivas da coluna de numero de filhos do cliente.
    """
    filhos = pd.to_numeric(df["CL_FHL"], errors="coerce")

    estatisticas = pd.Series({
        "contagem": filhos.count(),
        "media": filhos.mean(),
        "mediana": filhos.median(),
        "desvio_padrao": filhos.std(),
        "moda": filhos.mode(dropna=True).iloc[0] if not filhos.mode(dropna=True).empty else np.nan,
        "minimo": filhos.min(),
        "quartil_25": filhos.quantile(0.25),
        "quartil_50": filhos.quantile(0.50),
        "quartil_75": filhos.quantile(0.75),
        "maximo": filhos.max()
    })

    return estatisticas


def gerar_agrupamentos(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """
    Cria agrupamentos para encontrar padroes operacionais da base.
    Como a base enviada nao possui valor monetario, a analise usa quantidade de itens e numero de compras.
    """
    agrupamentos = {}

    agrupamentos["por_genero"] = (
        df.groupby("CL_GENERO")
        .agg(
            qtd_itens=("PR_ID", "count"),
            qtd_compras=("CO_ID", "nunique"),
            qtd_clientes=("CL_ID", "nunique")
        )
        .sort_values("qtd_itens", ascending=False)
    )

    agrupamentos["por_categoria"] = (
        df.groupby("PR_CAT")
        .agg(
            qtd_itens=("PR_ID", "count"),
            qtd_compras=("CO_ID", "nunique"),
            qtd_produtos=("PR_ID", "nunique")
        )
        .sort_values("qtd_itens", ascending=False)
    )

    agrupamentos["por_segmento"] = (
        df.groupby("CL_SEG")
        .agg(
            qtd_itens=("PR_ID", "count"),
            qtd_compras=("CO_ID", "nunique"),
            qtd_clientes=("CL_ID", "nunique")
        )
        .sort_values("qtd_itens", ascending=False)
    )

    agrupamentos["por_ano"] = (
        df.assign(ANO=df["DATA"].dt.year)
        .groupby("ANO")
        .agg(
            qtd_itens=("PR_ID", "count"),
            qtd_compras=("CO_ID", "nunique")
        )
    )

    agrupamentos["top_produtos"] = (
        df.groupby(["PR_CAT", "PR_NOME"])
        .size()
        .reset_index(name="qtd_itens")
        .sort_values("qtd_itens", ascending=False)
        .head(10)
    )

    return agrupamentos


def imprimir_relatorio_final(df_limpo: pd.DataFrame, relatorio: dict, agrupamentos: dict[str, pd.DataFrame]) -> None:
    """
    Imprime o relatorio final no terminal.
    """
    print("\n" + "=" * 80)
    print("RELATORIO FINAL - ANALISE EXPLORATORIA DA BASE VAREJO")
    print("=" * 80)

    print("\n1. RESUMO DA LIMPEZA")
    print(f"Shape original: {relatorio['shape_original'][0]} linhas x {relatorio['shape_original'][1]} colunas")
    print(f"Shape apos remover colunas vazias: {relatorio['shape_sem_colunas_vazias'][0]} linhas x {relatorio['shape_sem_colunas_vazias'][1]} colunas")
    print(f"Shape final: {relatorio['shape_final'][0]} linhas x {relatorio['shape_final'][1]} colunas")
    print(f"Duplicatas removidas: {relatorio['duplicatas_removidas']}")
    print(f"Categorias preenchidas como 'Sem Categoria': {relatorio['categorias_preenchidas_sem_categoria']}")
    print(f"Datas invalidas encontradas: {relatorio['datas_invalidas']}")
    print(f"Registros com compra inconsistente: {relatorio['registros_compra_inconsistentes']}")

    print("\n2. ESTATISTICAS - NUMERO DE FILHOS DO CLIENTE")
    print(estatisticas_filhos(df_limpo).round(2))

    print("\n3. AGRUPAMENTO POR GENERO")
    print(agrupamentos["por_genero"])

    print("\n4. AGRUPAMENTO POR CATEGORIA")
    print(agrupamentos["por_categoria"])

    print("\n5. AGRUPAMENTO POR SEGMENTO ECONOMICO")
    print(agrupamentos["por_segmento"])

    print("\n6. AGRUPAMENTO POR ANO")
    print(agrupamentos["por_ano"])

    print("\n7. TOP 10 PRODUTOS MAIS FREQUENTES")
    print(agrupamentos["top_produtos"].to_string(index=False))

    print("\n8. CONCLUSOES")
    print("- A base original possui colunas extras vazias, removidas durante a limpeza.")
    print("- Nao foram encontradas datas invalidas nem inconsistencias entre CO_ID, DATA e CL_ID.")
    print("- A categoria '#N/D' foi tratada como problema de qualidade e preenchida como 'Sem Categoria'.")
    print("- A categoria ALIMENTOS concentra a maior quantidade de itens registrados.")
    print("- O segmento economico B apresenta maior volume de itens, compras e clientes.")
    print("- A coluna CL_FHL indica que a moda e a mediana de filhos dos clientes sao 0.")


def main() -> None:
    """
    Executa o projeto completo.
    """
    if not CAMINHO_DADOS.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {CAMINHO_DADOS}")

    inspecionar_csv_nativo(CAMINHO_DADOS)

    df_original = carregar_dados(CAMINHO_DADOS)
    diagnosticar_base(df_original, "DIAGNOSTICO DA BASE ORIGINAL")

    df_limpo, relatorio = limpar_base(df_original)
    diagnosticar_base(df_limpo, "DIAGNOSTICO DA BASE LIMPA")

    agrupamentos = gerar_agrupamentos(df_limpo)
    imprimir_relatorio_final(df_limpo, relatorio, agrupamentos)

    CAMINHO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    df_limpo.to_csv(CAMINHO_SAIDA, index=False, encoding="utf-8-sig")
    print(f"\nBase limpa salva em: {CAMINHO_SAIDA}")


if __name__ == "__main__":
    main()

