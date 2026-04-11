# =============================================================================
# transform.py
# Limpeza, padronização e consolidação das séries brutas
# =============================================================================

import pandas as pd
import numpy as np

from utils import (
    DATA_RAW,
    DATA_PROC,
    START_DATE,
    END_DATE,
    load_csv,
    save_csv,
    validate_dataframe,
    resample_monthly,
    get_logger,
)

logger = get_logger(__name__)


# ─── Limpeza individual por série ────────────────────────────────────────────

def _clean_daily(filename: str, col: str) -> pd.DataFrame:
    """
    Carrega uma série diária bruta, aplica forward fill e valida.

    Parâmetros
    ----------
    filename : str   Nome do arquivo em data/raw/ (sem extensão)
    col : str        Nome esperado da coluna

    Retorno
    -------
    pd.DataFrame com DatetimeIndex diário, sem NaN no meio da série.
    """
    df = load_csv(filename, folder=DATA_RAW)

    # garante que o índice é datetime
    df.index = pd.to_datetime(df.index)
    df.index.name = "data"

    # mantém apenas a coluna de interesse
    if col not in df.columns:
        msg = (
            f"Coluna '{col}' não encontrada em '{filename}'. "
            f"Disponíveis: {list(df.columns)}"
        )
        raise KeyError(msg)
    df = df[[col]]

    # remove linhas totalmente nulas (ex: feriados sem dados)
    df = df.dropna(how="all")

    # forward fill para fins de semana / feriados entre datas válidas
    df = df.ffill()

    # recorta período do projeto
    df = df.loc[START_DATE:END_DATE]

    validate_dataframe(df, name=filename)
    daily_nans = df[col].isna().sum()
    logger.info(
        f"  {filename}: {len(df)} obs. diárias — "
        f"NaN restantes: {daily_nans}"
    )
    return df


def _clean_monthly(filename: str, col: str) -> pd.DataFrame:
    """
    Carrega uma série mensal bruta e valida.
    Séries mensais não recebem forward fill — valores ausentes são mantidos
    para análise posterior.
    """
    df = load_csv(filename, folder=DATA_RAW)
    df.index = pd.to_datetime(df.index)
    df.index.name = "data"

    if col not in df.columns:
        raise KeyError(f"Coluna '{col}' não encontrada em '{filename}'.")
    df = df[[col]]

    df = df.loc[START_DATE:END_DATE]

    monthly_nans = df[col].isna().sum()
    logger.info(f"  {filename}: {len(df)} obs. mensais — NaN: {monthly_nans}")
    return df


# ─── Transformações individuais ──────────────────────────────────────────────

def transform_usd_brl() -> pd.DataFrame:
    return _clean_daily("usd_brl_raw", "usd_brl")


def transform_ibovespa() -> pd.DataFrame:
    return _clean_daily("ibovespa_raw", "ibovespa")


def transform_dxy() -> pd.DataFrame:
    return _clean_daily("dxy_raw", "dxy")


def transform_vix() -> pd.DataFrame:
    return _clean_daily("vix_raw", "vix")


def transform_petroleo_wti() -> pd.DataFrame:
    return _clean_daily("petroleo_wti_raw", "petroleo_wti")


def transform_soja() -> pd.DataFrame:
    return _clean_daily("soja_raw", "soja")


def transform_selic() -> pd.DataFrame:
    return _clean_daily("selic_raw", "selic")


def transform_ipca() -> pd.DataFrame:
    return _clean_monthly("ipca_raw", "ipca_mensal")


def transform_fed_funds() -> pd.DataFrame:
    # Fed Funds é mensal no FRED — tratado como série mensal
    return _clean_monthly("fed_funds_raw", "fed_funds")


def transform_minerio_ferro() -> pd.DataFrame:
    return _clean_monthly("minerio_ferro_raw", "minerio_ferro")


def transform_embi_brasil() -> pd.DataFrame:
    return _clean_daily("embi_brasil_raw", "embi_brasil")


# ─── Resample e consolidação ─────────────────────────────────────────────────

def _resample_series(df: pd.DataFrame, method: str = "last") -> pd.DataFrame:
    """Reamostra uma série diária para frequência mensal."""
    return resample_monthly(df, method=method)


def build_dataset() -> pd.DataFrame:
    """
    Carrega, limpa, reamostra e consolida todas as séries em um único
    DataFrame mensal.

    Retorno
    -------
    pd.DataFrame com DatetimeIndex mensal e todas as variáveis do projeto.
    """
    logger.info("=== Iniciando pipeline de transformação ===")

    # --- séries diárias → resample mensal (último valor do mês) ---
    daily_series = {
        "usd_brl":      transform_usd_brl,
        "ibovespa":     transform_ibovespa,
        "dxy":          transform_dxy,
        "vix":          transform_vix,
        "petroleo_wti": transform_petroleo_wti,
        "soja":         transform_soja,
        "selic":        transform_selic,
        "embi_brasil":  transform_embi_brasil,
    }

    monthly_parts = []
    for name, func in daily_series.items():
        try:
            df_daily = func()
            df_monthly = _resample_series(df_daily, method="last")
            monthly_parts.append(df_monthly)
            logger.info(f"  ✓ {name} reamostrado para mensal")
        except Exception as e:
            logger.error(f"  ✗ Erro em '{name}': {e}")

    # --- séries já mensais ---
    monthly_series = {
        "ipca":         transform_ipca,
        "fed_funds":    transform_fed_funds,
        "minerio_ferro": transform_minerio_ferro,
    }

    for name, func in monthly_series.items():
        try:
            monthly_parts.append(func())
            logger.info(f"  ✓ {name} carregado (mensal)")
        except Exception as e:
            logger.error(f"  ✗ Erro em '{name}': {e}")

    # --- merge de todas as partes ---
    logger.info("Consolidando séries...")
    dataset = monthly_parts[0]
    for part in monthly_parts[1:]:
        dataset = dataset.merge(
            part,
            left_index=True,
            right_index=True,
            how="inner",
        )

    months = dataset.shape[0]
    variables = dataset.shape[1]
    logger.info(f"Dataset consolidado: {months} meses × {variables} variáveis")
    return dataset


# ─── Variáveis derivadas ─────────────────────────────────────────────────────

def add_derived_variables(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula e adiciona variáveis derivadas ao dataset consolidado.

    Variáveis adicionadas
    ---------------------
    - usd_brl_retorno      : variação percentual mensal do câmbio
    - usd_brl_volatilidade : desvio padrão rolling 3 meses dos retornos
    - spread_juros         : Selic – Fed Funds
    - ipca_acumulado_12m   : IPCA acumulado em 12 meses
    """
    df = df.copy()

    if "usd_brl" in df.columns:
        df["usd_brl_retorno"] = df["usd_brl"].pct_change()
        df["usd_brl_volatilidade"] = df["usd_brl_retorno"].rolling(3).std()

    if "selic" in df.columns and "fed_funds" in df.columns:
        df["spread_juros"] = df["selic"] - df["fed_funds"]

    if "ipca_mensal" in df.columns:
        df["ipca_acumulado_12m"] = df["ipca_mensal"].rolling(12).sum()

    # Normaliza valores infinitos para NaN antes de salvar/usar em análises.
    df = df.replace([np.inf, -np.inf], np.nan)

    logger.info("Variáveis derivadas calculadas.")
    return df


# ─── Pipeline completo ───────────────────────────────────────────────────────

def run_transform_pipeline() -> pd.DataFrame:
    """
    Executa o pipeline completo de transformação:
    1. Constrói o dataset consolidado
    2. Adiciona variáveis derivadas
    3. Salva em data/processed/dataset_analitico.csv

    Retorno
    -------
    pd.DataFrame final.
    """
    dataset = build_dataset()
    dataset = add_derived_variables(dataset)

    path = save_csv(dataset, "dataset_analitico", folder=DATA_PROC)
    logger.info(f"=== Dataset salvo em: {path} ===")

    return dataset


# ─── Execução direta ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    df = run_transform_pipeline()
    print(df.tail())
    print(f"\nShape: {df.shape}")
    print(f"\nNaN por coluna:\n{df.isna().sum()}")
