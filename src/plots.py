# =============================================================================
# plots.py
# Funções de visualização para análise do USD/BRL 2010–2026
# =============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import seaborn as sns
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from utils import FIGURES_DIR, get_logger

logger = get_logger(__name__)


# ─── Configuração global ─────────────────────────────────────────────────────

PALETTE = {
    "primary":    "#1a1a2e",
    "accent":     "#e94560",
    "secondary":  "#16213e",
    "muted":      "#a8a8b3",
    "positive":   "#2ecc71",
    "negative":   "#e74c3c",
    "neutral":    "#3498db",
    "background": "#f8f9fa",
}

EVENTS = [
    ("2013-05-01", "Taper Tantrum"),
    ("2015-01-01", "Crise fiscal BR"),
    ("2016-05-01", "Impeachment Dilma"),
    ("2018-05-01", "Greve caminhoneiros"),
    ("2020-03-01", "COVID-19"),
    ("2022-03-01", "Fed — ciclo de alta"),
    ("2023-01-01", "Novo governo Lula III"),
]


def set_style() -> None:
    """Aplica o estilo visual padrão do projeto."""
    plt.rcParams.update({
        "figure.facecolor":   PALETTE["background"],
        "axes.facecolor":     PALETTE["background"],
        "axes.edgecolor":     PALETTE["muted"],
        "axes.labelcolor":    PALETTE["primary"],
        "axes.titlesize":     13,
        "axes.labelsize":     11,
        "axes.spines.top":    False,
        "axes.spines.right":  False,
        "xtick.color":        PALETTE["muted"],
        "ytick.color":        PALETTE["muted"],
        "xtick.labelsize":    9,
        "ytick.labelsize":    9,
        "grid.color":         "#e0e0e0",
        "grid.linewidth":     0.6,
        "legend.fontsize":    9,
        "legend.framealpha":  0.7,
        "font.family":        "sans-serif",
        "figure.dpi":         150,
    })


def _save(fig: Figure, filename: str) -> None:
    """Salva a figura em reports/figures/."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / f"{filename}.png"
    fig.savefig(
        path,
        dpi=300,
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
    )
    logger.info(f"Figura salva: {path}")


def _add_events(
    ax: Axes, series: pd.Series, annotate: bool = True
) -> None:
    """Adiciona linhas verticais e rótulos para os eventos históricos."""
    ymin, ymax = ax.get_ylim()
    for date_str, label in EVENTS:
        date = pd.Timestamp(date_str)
        if series.index.min() <= date <= series.index.max():
            x_date = float(mdates.date2num(date.to_pydatetime()))
            ax.axvline(x_date, color=PALETTE["accent"], linewidth=0.8,
                       linestyle="--", alpha=0.6)
            if annotate:
                ax.text(
                    x_date, ymax * 0.97, label,
                    rotation=90, fontsize=7, color=PALETTE["accent"],
                    va="top", ha="right", alpha=0.8,
                )


# ─── 1. Evolução histórica do USD/BRL ────────────────────────────────────────

def plot_usd_brl_history(
    df: pd.DataFrame,
    col: str = "usd_brl",
    show_events: bool = True,
    save: bool = True,
) -> Figure:
    """
    Gráfico de linha do USD/BRL ao longo do período completo,
    com anotação dos principais eventos históricos.
    """
    set_style()
    fig, ax = plt.subplots(figsize=(14, 5))

    series = df[col].dropna()
    x_vals = mdates.date2num(pd.to_datetime(series.index).to_pydatetime())
    y_vals = series.to_numpy(dtype=float)
    ax.plot(x_vals, y_vals,
            color=PALETTE["primary"], linewidth=1.5, label="USD/BRL")

    # média móvel 12 meses
    mm12 = series.rolling(12).mean()
    mm12_vals = mm12.to_numpy(dtype=float)
    ax.plot(x_vals, mm12_vals,
            color=PALETTE["neutral"], linewidth=1.2,
            linestyle="--", alpha=0.8, label="Média móvel 12m")

    ax.set_title(
        "Taxa de Câmbio USD/BRL — 2010 a 2026",
        fontweight="bold",
        pad=14,
    )
    ax.set_ylabel("R$ / USD")
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.grid(axis="y", linestyle="--")
    ax.legend(loc="upper left")

    if show_events:
        _add_events(ax, series)

    fig.tight_layout()
    if save:
        _save(fig, "01_usd_brl_historico")
    return fig


# ─── 2. Volatilidade rolling ─────────────────────────────────────────────────

def plot_volatility(
    df: pd.DataFrame,
    vol_col: str = "usd_brl_volatilidade",
    pct_threshold: float = 90,
    save: bool = True,
) -> Figure:
    """
    Gráfico da volatilidade rolling do câmbio, com destaque
    nos períodos acima do percentil informado.
    """
    set_style()
    fig, ax = plt.subplots(figsize=(14, 4))

    vol = df[vol_col].dropna()
    x_vals = mdates.date2num(pd.to_datetime(vol.index).to_pydatetime())
    y_vals = vol.to_numpy(dtype=float)
    threshold = vol.quantile(pct_threshold / 100)
    mask = y_vals > float(threshold)

    ax.fill_between(x_vals, y_vals, alpha=0.3, color=PALETTE["neutral"])
    ax.plot(x_vals, y_vals, color=PALETTE["neutral"], linewidth=1)

    # destaca períodos de alta volatilidade
    ax.fill_between(
        x_vals, y_vals,
        where=mask.tolist(),
        alpha=0.5, color=PALETTE["accent"],
        label=f"Acima do p{int(pct_threshold)}",
    )
    ax.axhline(threshold, color=PALETTE["accent"], linewidth=0.8,
               linestyle=":", label=f"Limiar p{int(pct_threshold)}")

    ax.set_title(
        "Volatilidade Rolling do USD/BRL (3 meses)",
        fontweight="bold",
        pad=14,
    )
    ax.set_ylabel("Desvio padrão dos retornos")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.grid(axis="y", linestyle="--")
    ax.legend(loc="upper left")

    fig.tight_layout()
    if save:
        _save(fig, "02_volatilidade_rolling")
    return fig


# ─── 3. Câmbio x variável macroeconômica (eixo duplo) ───────────────────────

def plot_dual_axis(
    df: pd.DataFrame,
    col_macro: str,
    label_macro: str | None = None,
    invert_macro: bool = False,
    save: bool = True,
    filename: str | None = None,
) -> Figure:
    """
    Gráfico com dois eixos Y: USD/BRL (esquerda) e uma variável
    macroeconômica (direita).

    Parâmetros
    ----------
    col_macro : str       Coluna a plotar no eixo direito
    label_macro : str     Rótulo legível para a variável
    invert_macro : bool
        Inverte o eixo direito (ex: Ibovespa — correlação negativa)
    """
    set_style()
    fig, ax1 = plt.subplots(figsize=(14, 5))

    label_macro = label_macro or col_macro
    s_cambio = df["usd_brl"].dropna()
    s_macro = df[col_macro].dropna()
    x_cambio = mdates.date2num(pd.to_datetime(s_cambio.index).to_pydatetime())
    y_cambio = s_cambio.to_numpy(dtype=float)
    x_macro = mdates.date2num(pd.to_datetime(s_macro.index).to_pydatetime())
    y_macro = s_macro.to_numpy(dtype=float)

    # eixo esquerdo — câmbio
    ax1.plot(x_cambio, y_cambio,
             color=PALETTE["primary"], linewidth=1.5, label="USD/BRL")
    ax1.set_ylabel("R$ / USD", color=PALETTE["primary"])
    ax1.tick_params(axis="y", labelcolor=PALETTE["primary"])

    # eixo direito — variável macro
    ax2 = ax1.twinx()
    ax2.plot(x_macro, y_macro,
             color=PALETTE["accent"], linewidth=1.2,
             linestyle="--", alpha=0.85, label=label_macro)
    ax2.set_ylabel(label_macro, color=PALETTE["accent"])
    ax2.tick_params(axis="y", labelcolor=PALETTE["accent"])
    if invert_macro:
        ax2.invert_yaxis()

    ax1.set_title(f"USD/BRL × {label_macro}", fontweight="bold", pad=14)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax1.xaxis.set_major_locator(mdates.YearLocator(2))
    ax1.grid(axis="y", linestyle="--", alpha=0.5)

    # legenda combinada
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    fig.tight_layout()
    if save:
        fname = filename or f"03_cambio_x_{col_macro}"
        _save(fig, fname)
    return fig


# ─── 4. Heatmap de correlação ────────────────────────────────────────────────

def plot_correlation_heatmap(
    df: pd.DataFrame,
    save: bool = True,
) -> Figure:
    """
    Heatmap de correlação de Pearson entre todas as variáveis numéricas.
    """
    set_style()
    corr = df.corr(numeric_only=True).round(2)

    fig, ax = plt.subplots(figsize=(12, 9))
    mask = np.triu(np.ones_like(corr, dtype=bool))

    sns.heatmap(
        corr, mask=mask, annot=True, fmt=".2f",
        cmap="RdBu_r", center=0, vmin=-1, vmax=1,
        linewidths=0.5, linecolor="#e0e0e0",
        annot_kws={"size": 8},
        ax=ax,
    )
    ax.set_title(
        "Matriz de Correlação — Variáveis do Projeto",
        fontweight="bold",
        pad=14,
    )
    fig.tight_layout()

    if save:
        _save(fig, "04_heatmap_correlacao")
    return fig


# ─── 5. Barras — estatísticas por período ────────────────────────────────────

def plot_stats_by_period(
    summary_df: pd.DataFrame,
    metric: str = "média",
    col_label: str = "USD/BRL",
    save: bool = True,
) -> Figure:
    """
    Gráfico de barras horizontais com uma métrica por subperíodo.

    Parâmetros
    ----------
    summary_df : pd.DataFrame   Saída de describe_by_period()
    metric : str                Coluna de summary_df a plotar
    """
    set_style()
    fig, ax = plt.subplots(figsize=(9, 4))

    colors = [PALETTE["neutral"] if v < summary_df[metric].mean()
              else PALETTE["accent"]
              for v in summary_df[metric]]

    ax.barh(
        summary_df.index,
        summary_df[metric],
        color=colors,
        edgecolor="white",
    )
    ax.set_xlabel(f"{metric.capitalize()} — {col_label}")
    ax.set_title(
        f"{col_label}: {metric.capitalize()} por Subperíodo",
        fontweight="bold",
        pad=14,
    )
    ax.axvline(summary_df[metric].mean(), color=PALETTE["muted"],
               linewidth=0.9, linestyle="--", label="Média geral")
    ax.legend(loc="lower right")
    ax.grid(axis="x", linestyle="--")

    fig.tight_layout()
    if save:
        _save(fig, f"05_barras_{metric}_por_periodo")
    return fig


# ─── 6. Correlação rolling ───────────────────────────────────────────────────

def plot_rolling_correlation(
    rolling_corr: pd.Series,
    title: str | None = None,
    save: bool = True,
    filename: str = "06_correlacao_rolling",
) -> Figure:
    """
    Gráfico de linha da correlação rolling entre duas variáveis.
    Área sombreada indica correlação positiva (> 0).
    """
    set_style()
    fig, ax = plt.subplots(figsize=(14, 4))
    x_dt = pd.to_datetime(rolling_corr.index).to_pydatetime()
    x_vals = mdates.date2num(x_dt)
    y_vals = rolling_corr.to_numpy(dtype=float)
    pos_mask = (y_vals > 0).tolist()
    neg_mask = (y_vals <= 0).tolist()

    ax.plot(x_vals, y_vals, color=PALETTE["primary"], linewidth=1.4)
    ax.fill_between(
        x_vals,
        y_vals,
        0,
        where=pos_mask,
        alpha=0.2,
        color=PALETTE["accent"],
        label="Correlação positiva",
    )
    ax.fill_between(
        x_vals,
        y_vals,
        0,
        where=neg_mask,
        alpha=0.2,
        color=PALETTE["neutral"],
        label="Correlação negativa",
    )
    ax.axhline(0, color=PALETTE["muted"], linewidth=0.8, linestyle="--")
    ax.set_ylim(-1.1, 1.1)
    ax.set_ylabel("Correlação de Pearson")
    plot_title = title or str(rolling_corr.name or "Correlação rolling")
    ax.set_title(plot_title, fontweight="bold", pad=14)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.grid(axis="y", linestyle="--")
    ax.legend(loc="lower left")

    fig.tight_layout()
    if save:
        _save(fig, filename)
    return fig
