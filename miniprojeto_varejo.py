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

