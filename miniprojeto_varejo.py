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


# CHAMADA DA FUNCAO
inspecionar_csv_nativo(CAMINHO_DADOS)


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
    Na base, '#N/D' representa ausencia/inconsistencia de categoria.
    """
    df = df.copy()
    categorias_invalidas = ["", "NULL", "N/A", "#N/D", "NAN", "<NA>"]

    df["PR_CAT"] = df["PR_CAT"].astype("string").str.strip()
    mascara_categoria = df["PR_CAT"].isna() | df["PR_CAT"].isin(categorias_invalidas)
    df.loc[mascara_categoria, "PR_CAT"] = "Sem Categoria"

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

    # Trata categoria vazia/inconsistente.
    qtd_categoria_inconsistente = df["PR_CAT"].isna().sum() + (df["PR_CAT"] == "#N/D").sum()
    df = tratar_categoria(df)
    relatorio["categorias_preenchidas_sem_categoria"] = int(qtd_categoria_inconsistente)

    # Trata campos dimensionais de cliente/produto.
    # Justificativa: campos descritivos nulos sao preenchidos para preservar registros de compra.
    for coluna in ["CL_GENERO", "CL_SEG", "PR_NOME"]:
        if coluna in df.columns:
            df[coluna] = df[coluna].fillna("Nao informado")

    # Trata nulos da coluna numerica de numero de filhos pela mediana.
    # Justificativa: mediana reduz efeito de distribuicoes assimetricas.
    if "CL_FHL" in df.columns:
        mediana_filhos = df["CL_FHL"].median()
        df["CL_FHL"] = df["CL_FHL"].fillna(mediana_filhos)
        df["CL_FHL"] = df["CL_FHL"].astype("Int64")

    # Estado civil e uma dimensao codificada. Se houver nulo, usa a moda.
    if "CL_EC" in df.columns and df["CL_EC"].isna().any():
        moda_estado_civil = df["CL_EC"].mode(dropna=True)[0]
        df["CL_EC"] = df["CL_EC"].fillna(moda_estado_civil)

    # Conversao de data para datetime.
    # A funcao converter_data acima mostra a regra com o modulo datetime;
    # aqui usamos pd.to_datetime de forma vetorizada para executar melhor em 830 mil linhas.
    df["DATA"] = pd.to_datetime(df["DATA"].astype("string").str.strip(), format="%d/%m/%Y", errors="coerce")
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

