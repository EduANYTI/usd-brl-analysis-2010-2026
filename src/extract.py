# =============================================================================
# extract.py
# Coleta das séries históricas a partir de fontes públicas
# =============================================================================

import os
import time
from typing import cast

import pandas as pd
import yfinance as yf

from utils import (
    DATA_RAW,
    START_DATE,
    END_DATE,
    save_csv,
    get_logger,
)

logger = get_logger(__name__)


# ─── Yahoo Finance ──────────────────────────────────────────────────────────

def _fetch_yahoo(
    ticker: str, start: str, end: str, col_name: str
) -> pd.DataFrame:
    """
    Baixa a série de fechamento ajustado de um ticker do Yahoo Finance.

    Parâmetros
    ----------
    ticker : str
    start, end : str   Formato 'YYYY-MM-DD'
    col_name : str     Nome da coluna no DataFrame retornado

    Retorno
    -------
    pd.DataFrame com DatetimeIndex e uma coluna renomeada para col_name.
    """
    logger.info(f"Yahoo Finance → {ticker}")
    raw = yf.download(
        ticker, start=start, end=end, progress=False, auto_adjust=True
    )

    if raw is None or raw.empty:
        msg = f"Nenhum dado retornado para o ticker '{ticker}'."
        raise ValueError(msg)

    raw_df = cast(pd.DataFrame, raw)
    df = raw_df[["Close"]].rename(columns={"Close": col_name})
    df.index.name = "data"
    return df


def fetch_usd_brl(
    start: str = START_DATE, end: str = END_DATE
) -> pd.DataFrame:
    """Taxa de câmbio USD/BRL (PTAX aproximada via Yahoo Finance)."""
    df = _fetch_yahoo("BRL=X", start, end, "usd_brl")
    save_csv(df, "usd_brl_raw", folder=DATA_RAW)
    msg = f"usd_brl salvo → {DATA_RAW}/usd_brl_raw.csv  ({len(df)} linhas)"
    logger.info(msg)
    return df


def fetch_ibovespa(
    start: str = START_DATE, end: str = END_DATE
) -> pd.DataFrame:
    """Índice Bovespa (^BVSP)."""
    df = _fetch_yahoo("^BVSP", start, end, "ibovespa")
    save_csv(df, "ibovespa_raw", folder=DATA_RAW)
    msg = f"ibovespa salvo → {DATA_RAW}/ibovespa_raw.csv  ({len(df)} linhas)"
    logger.info(msg)
    return df


def fetch_dxy(start: str = START_DATE, end: str = END_DATE) -> pd.DataFrame:
    """Índice do Dólar (DXY)."""
    df = _fetch_yahoo("DX-Y.NYB", start, end, "dxy")
    save_csv(df, "dxy_raw", folder=DATA_RAW)
    logger.info(f"dxy salvo → {DATA_RAW}/dxy_raw.csv  ({len(df)} linhas)")
    return df


def fetch_vix(start: str = START_DATE, end: str = END_DATE) -> pd.DataFrame:
    """Índice VIX (^VIX)."""
    df = _fetch_yahoo("^VIX", start, end, "vix")
    save_csv(df, "vix_raw", folder=DATA_RAW)
    logger.info(f"vix salvo → {DATA_RAW}/vix_raw.csv  ({len(df)} linhas)")
    return df


def fetch_petroleo_wti(
    start: str = START_DATE, end: str = END_DATE
) -> pd.DataFrame:
    """Petróleo WTI (CL=F)."""
    df = _fetch_yahoo("CL=F", start, end, "petroleo_wti")
    save_csv(df, "petroleo_wti_raw", folder=DATA_RAW)
    msg = f"petroleo_wti salvo → {DATA_RAW}/petroleo_wti_raw.csv"
    msg += f" ({len(df)} linhas)"
    logger.info(msg)
    return df


def fetch_soja(start: str = START_DATE, end: str = END_DATE) -> pd.DataFrame:
    """Soja (ZS=F)."""
    df = _fetch_yahoo("ZS=F", start, end, "soja")
    save_csv(df, "soja_raw", folder=DATA_RAW)
    logger.info(f"soja salvo → {DATA_RAW}/soja_raw.csv  ({len(df)} linhas)")
    return df


# ─── Banco Central (python-bcb / SGS) ───────────────────────────────────────

def _fetch_bcb(
    serie: int, col_name: str, start: str, end: str
) -> pd.DataFrame:
    """
    Coleta uma série do Sistema Gerenciador de Séries Temporais (SGS) do Bacen.

    Parâmetros
    ----------
    serie : int     Código da série no SGS
    col_name : str
    start, end : str

    Retorno
    -------
    pd.DataFrame com DatetimeIndex e uma coluna.
    """
    from bcb import sgs

    logger.info(f"Bacen SGS → série {serie} ({col_name})")
    sgs_data = sgs.get({col_name: serie}, start=start, end=end)
    if isinstance(sgs_data, list):
        if not sgs_data:
            raise ValueError(f"Bacen SGS sem dados para a série {serie}.")
        df = sgs_data[0]
    else:
        df = sgs_data

    df = cast(pd.DataFrame, df)
    df.index.name = "data"
    return df


def fetch_selic(start: str = START_DATE, end: str = END_DATE) -> pd.DataFrame:
    """Meta da Selic — SGS série 432."""
    df = _fetch_bcb(432, "selic", start, end)
    save_csv(df, "selic_raw", folder=DATA_RAW)
    logger.info(f"selic salvo → {DATA_RAW}/selic_raw.csv  ({len(df)} linhas)")
    return df


def fetch_ipca(start: str = START_DATE, end: str = END_DATE) -> pd.DataFrame:
    """IPCA mensal — SGS série 433."""
    df = _fetch_bcb(433, "ipca_mensal", start, end)
    save_csv(df, "ipca_raw", folder=DATA_RAW)
    logger.info(f"ipca salvo → {DATA_RAW}/ipca_raw.csv  ({len(df)} linhas)")
    return df


# ─── FRED (Federal Reserve) ──────────────────────────────────────────────────

def _fetch_fred(
    series_id: str, col_name: str, start: str, end: str
) -> pd.DataFrame:
    """
    Coleta uma série do FRED.
    Requer a variável de ambiente FRED_API_KEY definida no arquivo .env.

    Parâmetros
    ----------
    series_id : str   Código da série no FRED
    col_name : str
    start, end : str
    """
    from fredapi import Fred

    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "Variável de ambiente FRED_API_KEY não encontrada. "
            "Adicione-a ao arquivo .env na raiz do projeto."
        )

    logger.info(f"FRED → série {series_id} ({col_name})")
    fred = Fred(api_key=api_key)
    series = fred.get_series(
        series_id, observation_start=start, observation_end=end
    )
    df = series.to_frame(name=col_name)
    df.index.name = "data"
    return df


def fetch_fed_funds(
    start: str = START_DATE, end: str = END_DATE
) -> pd.DataFrame:
    """Fed Funds Rate — série FEDFUNDS."""
    df = _fetch_fred("FEDFUNDS", "fed_funds", start, end)
    save_csv(df, "fed_funds_raw", folder=DATA_RAW)
    msg = f"fed_funds salvo → {DATA_RAW}/fed_funds_raw.csv ({len(df)} linhas)"
    logger.info(msg)
    return df


def fetch_minerio_ferro(
    start: str = START_DATE, end: str = END_DATE
) -> pd.DataFrame:
    """Minério de ferro — série PIORECRUSDM."""
    df = _fetch_fred("PIORECRUSDM", "minerio_ferro", start, end)
    save_csv(df, "minerio_ferro_raw", folder=DATA_RAW)
    msg = f"minerio_ferro salvo → {DATA_RAW}/minerio_ferro_raw.csv"
    msg += f" ({len(df)} linhas)"
    logger.info(msg)
    return df


# ─── EMBI+ Brasil (IPEADATA) ─────────────────────────────────────────────────

def fetch_embi_brasil(
    start: str = START_DATE, end: str = END_DATE
) -> pd.DataFrame:
    """
    EMBI+ Brasil via IPEADATA (API pública, sem chave).
    Série: JPM366_EMBI366
    """
    import requests

    logger.info("IPEADATA → EMBI+ Brasil")
    url = (
        "http://www.ipeadata.gov.br/api/odata4/ValoresSerie"
        "(SERCODIGO='JPM366_EMBI366')"
    )

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    data = response.json().get("value", [])
    if not data:
        raise ValueError("IPEADATA não retornou dados para o EMBI+.")

    df = pd.DataFrame(data)[["VALDATA", "VALVALOR"]]
    df.columns = ["data", "embi_brasil"]
    df["data"] = pd.to_datetime(df["data"])
    df = df.set_index("data").sort_index()
    df = df.loc[start:end]

    save_csv(df, "embi_brasil_raw", folder=DATA_RAW)
    msg = f"embi_brasil salvo → {DATA_RAW}/embi_brasil_raw.csv"
    msg += f" ({len(df)} linhas)"
    logger.info(msg)
    return df


# ─── Coleta completa ───────────────────────────────────────────────────────

def extract_all(
    start: str = START_DATE, end: str = END_DATE
) -> dict[str, pd.DataFrame]:
    """
    Executa a coleta de todas as séries do projeto.

    Retorno
    -------
    dict com {nome_serie: DataFrame}
    """
    logger.info("=== Iniciando coleta completa ===")

    collectors = {
        "usd_brl":       fetch_usd_brl,
        "ibovespa":      fetch_ibovespa,
        "dxy":           fetch_dxy,
        "vix":           fetch_vix,
        "petroleo_wti":  fetch_petroleo_wti,
        "soja":          fetch_soja,
        "selic":         fetch_selic,
        "ipca":          fetch_ipca,
        "fed_funds":     fetch_fed_funds,
        "minerio_ferro": fetch_minerio_ferro,
        "embi_brasil":   fetch_embi_brasil,
    }

    results = {}
    for name, func in collectors.items():
        try:
            results[name] = func(start=start, end=end)
            time.sleep(0.5)  # evita rate limiting
        except Exception as e:
            logger.error(f"Erro ao coletar '{name}': {e}")

    total = len(results)
    total_collectors = len(collectors)
    logger.info(f"=== Coleta concluída: {total}/{total_collectors} séries ===")
    return results


# ─── Execução direta ──────────────────────────────────────────────────

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    extract_all()
