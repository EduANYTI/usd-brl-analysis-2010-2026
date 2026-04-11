# =============================================================================
# utils.py
# Funções auxiliares compartilhadas entre os módulos do projeto
# =============================================================================

import logging
from pathlib import Path
from datetime import datetime

import pandas as pd


# ─── Diretórios do projeto ───────────────────────────────────────────────

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_RAW = ROOT_DIR / "data" / "raw"
DATA_PROC = ROOT_DIR / "data" / "processed"
REPORTS_DIR = ROOT_DIR / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"


def ensure_dirs() -> None:
    """Cria os diretórios do projeto caso não existam."""
    for directory in [DATA_RAW, DATA_PROC, FIGURES_DIR]:
        directory.mkdir(parents=True, exist_ok=True)


# ─── Logging ──────────────────────────────────────────────────────────────

def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Retorna um logger configurado com formato padronizado.

    Parâmetros
    ----------
    name : str
        Nome do logger (geralmente __name__ do módulo chamador).
    level : int
        Nível de log (padrão: logging.INFO).

    Retorno
    -------
    logging.Logger
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(level)
    return logger


# ─── Datas ───────────────────────────────────────────────────────────────────

START_DATE = "2010-01-01"
END_DATE = "2026-12-31"


def parse_date(date_str: str) -> datetime:
    """Converte string 'YYYY-MM-DD' para objeto datetime."""
    return datetime.strptime(date_str, "%Y-%m-%d")


def date_range_str() -> tuple[str, str]:
    """Retorna o par (START_DATE, END_DATE) do projeto."""
    return START_DATE, END_DATE


# ─── Validação de DataFrames ──────────────────────────────────────────────

def validate_dataframe(df: pd.DataFrame, name: str = "DataFrame") -> None:
    """
    Verifica se o DataFrame está no formato esperado:
    - índice do tipo DatetimeIndex
    - sem colunas completamente nulas
    - sem linhas duplicadas no índice

    Lança ValueError se alguma condição não for atendida.

    Parâmetros
    ----------
    df : pd.DataFrame
    name : str
        Nome do DataFrame para mensagens de erro.
    """
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError(f"{name}: o índice deve ser DatetimeIndex.")

    colunas_nulas = [col for col in df.columns if df[col].isna().all()]
    if colunas_nulas:
        msg = f"{name}: colunas completamente nulas: {colunas_nulas}"
        raise ValueError(msg)

    if df.index.duplicated().any():
        raise ValueError(f"{name}: índice contém datas duplicadas.")


# ─── Resample mensal ──────────────────────────────────────────────────────

def resample_monthly(df: pd.DataFrame, method: str = "last") -> pd.DataFrame:
    """
    Reamostra um DataFrame de frequência diária para mensal.

    Parâmetros
    ----------
    df : pd.DataFrame
        DataFrame com DatetimeIndex diário.
    method : str
        Método de agregação: 'last' (padrão), 'mean' ou 'first'.

    Retorno
    -------
    pd.DataFrame com frequência mensal (último dia útil do mês).
    """
    agg = {"last": "last", "mean": "mean", "first": "first"}
    if method not in agg:
        raise ValueError(f"method deve ser um de: {list(agg.keys())}")

    resampler = df.resample("ME")
    return getattr(resampler, agg[method])()


# ─── Persistência ─────────────────────────────────────────────────────────

def save_csv(
    df: pd.DataFrame, filename: str, folder: Path = DATA_PROC
) -> Path:
    """
    Salva um DataFrame como CSV na pasta especificada.

    Parâmetros
    ----------
    df : pd.DataFrame
    filename : str
        Nome do arquivo (sem extensão).
    folder : Path
        Pasta de destino (padrão: data/processed/).

    Retorno
    -------
    Path do arquivo salvo.
    """
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{filename}.csv"
    df.to_csv(path, index=True, encoding="utf-8")
    return path


def load_csv(filename: str, folder: Path = DATA_PROC) -> pd.DataFrame:
    """
    Carrega um CSV da pasta especificada com índice de datas.

    Parâmetros
    ----------
    filename : str
        Nome do arquivo (sem extensão).
    folder : Path
        Pasta de origem (padrão: data/processed/).

    Retorno
    -------
    pd.DataFrame com DatetimeIndex.
    """
    path = folder / f"{filename}.csv"
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    df = pd.read_csv(path, index_col=0, parse_dates=True, encoding="utf-8")
    return df


# ─── Formatação ───────────────────────────────────────────────────────────

def format_brl(value: float) -> str:
    """Formata valor float como BRL monetário. Ex: 5.2345 → 'R$ 5,23'."""
    fmt = f"R$ {value:,.2f}"
    return fmt.replace(",", "X").replace(".", ",").replace("X", ".")


def format_pct(value: float, decimals: int = 2) -> str:
    """Formata um valor float como percentual. Ex: 0.1523 → '15,23%'"""
    return f"{value * 100:.{decimals}f}%".replace(".", ",")
