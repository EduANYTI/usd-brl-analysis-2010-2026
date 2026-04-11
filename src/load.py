# =============================================================================
# load.py
# Funções de acesso ao dataset analítico processado
# Ponto de entrada único para notebooks, dashboard e scripts de análise
# =============================================================================

import pandas as pd

from utils import (
    DATA_PROC,
    DATA_RAW,
    START_DATE,
    END_DATE,
    load_csv,
    get_logger,
)

logger = get_logger(__name__)


# ─── Constantes ──────────────────────────────────────────────────────────────

DATASET_FILE = "dataset_analitico"

# Colunas brutas (originais das fontes)
COLS_RAW = [
    "usd_brl",
    "ibovespa",
    "dxy",
    "vix",
    "petroleo_wti",
    "soja",
    "selic",
    "ipca_mensal",
    "fed_funds",
    "minerio_ferro",
    "embi_brasil",
]

# Colunas derivadas (calculadas no transform.py)
COLS_DERIVED = [
    "usd_brl_retorno",
    "usd_brl_volatilidade",
    "spread_juros",
    "ipca_acumulado_12m",
]

ALL_COLS = COLS_RAW + COLS_DERIVED


# ─── Carregamento principal ──────────────────────────────────────────────────

def load_dataset(
    start: str | None = None,
    end: str | None = None,
    columns: list[str] | None = None,
    drop_na: bool = False,
) -> pd.DataFrame:
    """
    Carrega o dataset analítico consolidado.

    Parâmetros
    ----------
    start : str, opcional
        Data inicial no formato 'YYYY-MM-DD'. Padrão: START_DATE do projeto.
    end : str, opcional
        Data final no formato 'YYYY-MM-DD'. Padrão: END_DATE do projeto.
    columns : list[str], opcional
        Subconjunto de colunas a retornar. Padrão: todas.
    drop_na : bool
        Se True, remove linhas com qualquer NaN. Padrão: False.

    Retorno
    -------
    pd.DataFrame com DatetimeIndex mensal.

    Exemplo
    -------
    >>> df = load_dataset(
    ...     start="2015-01-01", columns=["usd_brl", "selic", "vix"]
    ... )
    """
    df = load_csv(DATASET_FILE, folder=DATA_PROC)

    # recorte temporal
    _start = start or START_DATE
    _end = end or END_DATE
    df = df.loc[_start:_end]

    # seleção de colunas
    if columns:
        missing = [c for c in columns if c not in df.columns]
        if missing:
            raise KeyError(f"Colunas não encontradas no dataset: {missing}")
        df = df[columns]

    if drop_na:
        antes = len(df)
        df = df.dropna()
        logger.info(f"drop_na: {antes - len(df)} linhas removidas.")

    months = df.shape[0]
    cols = df.shape[1]
    logger.info(f"Dataset carregado: {months} meses × {cols} colunas")
    return df


# ─── Atalhos por grupo de variáveis ──────────────────────────────────────────

def load_cambio() -> pd.DataFrame:
    """Retorna apenas as colunas relacionadas ao câmbio USD/BRL."""
    cols = ["usd_brl", "usd_brl_retorno", "usd_brl_volatilidade"]
    return load_dataset(columns=[c for c in cols if c in ALL_COLS])


def load_juros() -> pd.DataFrame:
    """Retorna Selic, Fed Funds e spread de juros."""
    return load_dataset(columns=["selic", "fed_funds", "spread_juros"])


def load_risco() -> pd.DataFrame:
    """Retorna indicadores de risco: VIX, EMBI+ e Ibovespa."""
    return load_dataset(columns=["vix", "embi_brasil", "ibovespa"])


def load_inflacao() -> pd.DataFrame:
    """Retorna IPCA mensal e acumulado 12 meses."""
    return load_dataset(columns=["ipca_mensal", "ipca_acumulado_12m"])


def load_commodities() -> pd.DataFrame:
    """Retorna Petróleo WTI, Soja e Minério de Ferro."""
    return load_dataset(columns=["petroleo_wti", "soja", "minerio_ferro"])


# ─── Carregamento de séries brutas ───────────────────────────────────────────

def load_raw(series_name: str) -> pd.DataFrame:
    """
    Carrega uma série bruta de data/raw/.

    Parâmetros
    ----------
    series_name : str
        Nome da série sem sufixo '_raw'. Ex: 'usd_brl', 'selic'.

    Retorno
    -------
    pd.DataFrame com DatetimeIndex.

    Exemplo
    -------
    >>> df_raw = load_raw("usd_brl")
    """
    filename = f"{series_name}_raw"
    df = load_csv(filename, folder=DATA_RAW)
    logger.info(f"Série bruta carregada: {filename} ({len(df)} linhas)")
    return df


# ─── Diagnóstico ─────────────────────────────────────────────────────────────

def dataset_info() -> None:
    """
    Imprime um resumo do dataset analítico:
    período, shape, cobertura e NaN por coluna.
    """
    df = load_dataset()

    print("=" * 55)
    print("DATASET ANALÍTICO — USD/BRL 2010–2026")
    print("=" * 55)
    print(f"Período   : {df.index.min().date()} → {df.index.max().date()}")
    print(f"Observações: {df.shape[0]} meses")
    print(f"Variáveis : {df.shape[1]} colunas")
    print()
    print("NaN por coluna:")
    nan_counts = df.isna().sum()
    for col, count in nan_counts.items():
        pct = count / len(df) * 100
        flag = " ⚠" if pct > 5 else ""
        print(f"  {col:<30} {count:>4} ({pct:5.1f}%){flag}")
    print("=" * 55)


# ─── Execução direta ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    dataset_info()
