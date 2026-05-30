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