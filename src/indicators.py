# =============================================================================
# indicators.py
# Cálculo de indicadores analíticos sobre o dataset consolidado
# =============================================================================

import pandas as pd
import numpy as np
from typing import Optional

from utils import get_logger

logger = get_logger(__name__)


# ─── Estatísticas descritivas ────────────────────────────────────────────────

def describe_series(df: pd.DataFrame, col: str) -> pd.Series:
    """
    Retorna estatísticas descritivas completas para uma coluna.

    Inclui: count, mean, std, min, 25%, 50%, 75%, max,
    além de skewness e kurtosis.
    """
    s = df[col].dropna()
    stats = s.describe()
    stats["skewness"] = s.skew()
    stats["kurtosis"] = s.kurt()
    return stats


def describe_by_period(
    df: pd.DataFrame,
    col: str,
    periods: dict[str, tuple[str, str]],
) -> pd.DataFrame:
    """
    Calcula estatísticas descritivas de uma coluna por subperíodo.

    Parâmetros
    ----------
    df : pd.DataFrame       Dataset com DatetimeIndex
    col : str               Coluna a analisar
    periods : dict          {'label': ('YYYY-MM-DD', 'YYYY-MM-DD')}

    Retorno
    -------
    pd.DataFrame com uma linha por período.

    Exemplo
    -------
    >>> periods = {
    ...     "Lula II / Dilma I": ("2010-01-01", "2014-12-31"),
    ...     "Crise fiscal":      ("2015-01-01", "2018-12-31"),
    ...     "Bolsonaro":         ("2019-01-01", "2022-12-31"),
    ...     "Lula III":          ("2023-01-01", "2026-12-31"),
    ... }
    >>> describe_by_period(df, "usd_brl", periods)
    """
    rows = []
    for label, (start, end) in periods.items():
        s = df.loc[start:end, col].dropna()
        rows.append({
            "período":       label,
            "início":        start,
            "fim":           end,
            "média":         s.mean(),
            "mediana":       s.median(),
            "mínimo":        s.min(),
            "máximo":        s.max(),
            "desvio_padrão": s.std(),
            "variação_%": (
                (s.iloc[-1] / s.iloc[0] - 1) * 100 if len(s) > 1 else np.nan
            ),
            "n_meses":       len(s),
        })
    return pd.DataFrame(rows).set_index("período")


# ─── Retornos e volatilidade ─────────────────────────────────────────────────

def calc_returns(series: pd.Series) -> pd.Series:
    """Retorno percentual mensal de uma série de preços."""
    return series.pct_change().rename(f"{series.name}_retorno")


def calc_rolling_volatility(
    series: pd.Series,
    window: int = 3,
) -> pd.Series:
    """
    Volatilidade rolling (desvio padrão dos retornos).

    Parâmetros
    ----------
    series : pd.Series   Série de retornos (já em %)
    window : int         Janela em meses (padrão: 3)
    """
    return series.rolling(window).std().rename(f"{series.name}_vol{window}m")


def high_volatility_periods(
    vol_series: pd.Series,
    percentile: float = 90,
) -> pd.Series:
    """
    Retorna máscara booleana com True acima do percentil informado.

    Útil para destacar períodos de estresse no gráfico.
    """
    threshold = vol_series.quantile(percentile / 100)
    return vol_series > threshold


# ─── Correlações ─────────────────────────────────────────────────────────────

def pearson_correlation(
    df: pd.DataFrame,
    target: str = "usd_brl",
) -> pd.Series:
    """
    Correlação de Pearson entre target e todas as demais colunas numéricas.

    Retorno
    -------
    pd.Series ordenada por valor absoluto (desc).
    """
    corr = df.corr(numeric_only=True)[target].drop(target)
    return corr.reindex(corr.abs().sort_values(ascending=False).index)


def rolling_correlation(
    df: pd.DataFrame,
    col_a: str,
    col_b: str,
    window: int = 12,
) -> pd.Series:
    """
    Correlação rolling entre duas colunas.

    Parâmetros
    ----------
    window : int   Janela em meses (padrão: 12)

    Retorno
    -------
    pd.Series com nome '{col_a}_x_{col_b}_corr{window}m'
    """
    name = f"{col_a}_x_{col_b}_corr{window}m"
    return df[col_a].rolling(window).corr(df[col_b]).rename(name)


def correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Matriz de correlação completa entre todas as variáveis numéricas."""
    return df.corr(numeric_only=True).round(3)


# ─── Spread e diferenciais ───────────────────────────────────────────────────

def calc_spread(
    df: pd.DataFrame,
    col_a: str,
    col_b: str,
    name: Optional[str] = None,
) -> pd.Series:
    """
    Calcula o spread (diferença) entre duas colunas.

    Exemplo: spread_juros = selic - fed_funds
    """
    result = df[col_a] - df[col_b]
    result.name = name or f"{col_a}_minus_{col_b}"
    return result


# ─── Máximas e mínimas históricas ────────────────────────────────────────────

def find_extremes(
    series: pd.Series,
    n: int = 5,
) -> pd.DataFrame:
    """
    Retorna as n maiores e n menores observações de uma série.

    Retorno
    -------
    pd.DataFrame com colunas ['data', 'valor', 'tipo']
    """
    s = series.dropna()

    maximas = s.nlargest(n).reset_index()
    maximas.columns = ["data", "valor"]
    maximas["tipo"] = "máxima"

    minimas = s.nsmallest(n).reset_index()
    minimas.columns = ["data", "valor"]
    minimas["tipo"] = "mínima"

    return (
        pd.concat([maximas, minimas])
        .sort_values("data")
        .reset_index(drop=True)
    )


# ─── Acumulados ──────────────────────────────────────────────────────────────

def calc_cumulative_return(series: pd.Series) -> pd.Series:
    """
    Retorno acumulado de uma série de retornos percentuais.
    Útil para comparar depreciação acumulada do BRL ao longo do tempo.

    Retorno
    -------
    pd.Series indexada da mesma forma que a entrada.
    """
    returns = series.dropna()
    cumulative = (1 + returns / 100).cumprod() - 1
    return (cumulative * 100).rename(f"{series.name}_acumulado")


def calc_rolling_mean(series: pd.Series, window: int = 12) -> pd.Series:
    """Média móvel de uma série."""
    return series.rolling(window).mean().rename(f"{series.name}_mm{window}m")


# ─── Subperíodos padrão do projeto ───────────────────────────────────────────

DEFAULT_PERIODS = {
    "Lula II / Dilma I (2010–2014)": ("2010-01-01", "2014-12-31"),
    "Crise fiscal / Temer (2015–2018)": ("2015-01-01", "2018-12-31"),
    "Bolsonaro / COVID (2019–2022)": ("2019-01-01", "2022-12-31"),
    "Lula III (2023–2026)": ("2023-01-01", "2026-12-31"),
}


def summary_by_default_periods(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """
    Atalho: aplica describe_by_period com os subperíodos padrão do projeto.
    """
    return describe_by_period(df, col, DEFAULT_PERIODS)
