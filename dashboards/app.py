import sys
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from load import load_dataset  # noqa: E402
from indicators import (  # noqa: E402
    summary_by_default_periods,
    pearson_correlation,
    rolling_correlation,
    find_extremes,
    calc_returns,
)
from plots import EVENTS  # noqa: E402


# Configuração da página

st.set_page_config(
    page_title="USD/BRL 2010–2026",
    page_icon="💱",
    layout="wide",
    initial_sidebar_state="expanded",
)

PALETTE = {
    "ink": "#18202a",
    "primary": "#0f4c81",
    "accent": "#e76f51",
    "neutral": "#2a9d8f",
    "positive": "#2d9c5e",
    "negative": "#c44536",
    "muted": "#6b7280",
    "surface": "#f5f7fb",
    "panel": "#ffffff",
    "grid": "#dbe3ee",
}

st.markdown(
    """
    <style>
    :root {
        --app-ink: #18202a;
        --app-muted: #5b6678;
        --app-panel: #ffffff;
    }

    html, body, [class*="css"]  {
        font-family: 'IBM Plex Sans', 'Trebuchet MS', sans-serif;
    }

    .stApp {
        background: radial-gradient(
            circle at top right,
            #eef4ff 0%,
            #f8fafc 42%,
            #ffffff 100%
        );
        color: var(--app-ink);
    }

    .stApp p,
    .stApp span,
    .stApp label,
    .stApp li,
    .stApp small,
    .stApp h1,
    .stApp h2,
    .stApp h3,
    .stApp h4,
    .stApp h5,
    .stApp h6,
    .stApp [data-testid="stMarkdownContainer"] {
        color: var(--app-ink) !important;
    }

    .stApp [data-testid="stCaptionContainer"] {
        color: var(--app-muted) !important;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f3f7ff 0%, #ffffff 100%);
        border-right: 1px solid #dde6f2;
    }

    [data-testid="stSidebar"] * {
        color: var(--app-ink) !important;
    }

    [data-testid="stMetric"] {
        background: var(--app-panel);
        border: 1px solid #e7edf6;
        border-radius: 12px;
        padding: 10px 12px;
        box-shadow: 0 3px 12px rgba(15, 76, 129, 0.06);
    }

    [data-baseweb="input"] > div,
    [data-baseweb="select"] > div {
        background: #ffffff !important;
        border-color: #c9d6ea !important;
        color: var(--app-ink) !important;
    }

    [data-baseweb="tab-list"] button {
        color: #2b3444 !important;
        font-weight: 600 !important;
    }

    [data-baseweb="tab-highlight"] {
        background-color: #e76f51 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def _fmt_period(value: pd.Timestamp) -> str:
    return pd.Timestamp(value).strftime("%b/%Y")


def _apply_plot_style(fig: go.Figure, height: int) -> None:
    fig.update_layout(
        height=height,
        hovermode="x unified",
        plot_bgcolor=PALETTE["panel"],
        paper_bgcolor=PALETTE["panel"],
        margin=dict(l=18, r=16, t=48, b=16),
        font=dict(color=PALETTE["ink"], size=13),
        xaxis=dict(
            showgrid=True,
            gridcolor=PALETTE["grid"],
            zeroline=False,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=PALETTE["grid"],
            zeroline=False,
        ),
    )


# Carregamento dos dados


@st.cache_data
def get_data() -> pd.DataFrame:
    return load_dataset()


df_full = get_data()

if df_full.empty:
    st.error(
        "O dataset carregado está vazio. Verifique a etapa de extração e "
        "transformação dos dados."
    )
    st.stop()


# Sidebar

with st.sidebar:
    st.title("💱 USD/BRL")
    st.caption("Análise 2010–2026")
    st.divider()

    st.subheader("⚙️ Filtros")

    date_min = df_full.index.min().to_pydatetime()
    date_max = df_full.index.max().to_pydatetime()

    col1, col2 = st.columns(2)
    with col1:
        start = st.date_input(
            "Início",
            value=date_min,
            min_value=date_min,
            max_value=date_max,
        )
    with col2:
        end = st.date_input(
            "Fim",
            value=date_max,
            min_value=date_min,
            max_value=date_max,
        )

    if start > end:
        st.warning(
            "A data de início é maior que a data final. Os valores foram "
            "invertidos automaticamente."
        )
        start, end = end, start

    show_events = st.toggle("Mostrar eventos históricos", value=True)
    show_event_labels = st.toggle("Mostrar rótulos dos eventos", value=False)
    show_mm = st.toggle("Mostrar média móvel 12m", value=True)

    st.divider()
    st.subheader("📊 Comparar com")

    MACRO_OPTIONS = {
        "Selic (% a.a.)": "selic",
        "Fed Funds Rate (% a.a.)": "fed_funds",
        "Spread Juros (p.p.)": "spread_juros",
        "DXY — Índice do Dólar": "dxy",
        "VIX": "vix",
        "EMBI+ Brasil (bps)": "embi_brasil",
        "Ibovespa (pontos)": "ibovespa",
        "IPCA acumulado 12m (%)": "ipca_acumulado_12m",
        "Petróleo WTI (USD/bbl)": "petroleo_wti",
    }
    macro_label = st.selectbox(
        "Variável macroeconômica",
        list(MACRO_OPTIONS.keys()),
    )
    macro_col = MACRO_OPTIONS[macro_label]
    invert_macro = st.toggle("Inverter eixo da variável", value=False)

    st.divider()
    st.caption("Fontes: Bacen · IBGE · FRED · Yahoo Finance · IPEADATA")


# Recorte temporal

df = df_full[(df_full.index >= str(start)) & (df_full.index <= str(end))]

if df.empty:
    st.error(
        "Não há dados no intervalo selecionado. Ajuste o filtro de datas "
        "para continuar."
    )
    st.stop()


# Cabeçalho

st.title("Taxa de Câmbio USD/BRL — 2010 a 2026")
st.caption(
    "Painel interativo de tendência, risco e relações "
    "macroeconômicas do câmbio."
)

# KPIs
retornos = calc_returns(df["usd_brl"])
k1, k2, k3, k4, k5 = st.columns(5)

k1.metric("Cotação atual", f"R$ {df['usd_brl'].iloc[-1]:.4f}")
k2.metric("Média do período", f"R$ {df['usd_brl'].mean():.4f}")
k3.metric(
    "Máxima",
    f"R$ {df['usd_brl'].max():.4f}",
    delta=_fmt_period(pd.Timestamp(df["usd_brl"].idxmax())),
    delta_color="off",
)
k4.metric(
    "Mínima",
    f"R$ {df['usd_brl'].min():.4f}",
    delta=_fmt_period(pd.Timestamp(df["usd_brl"].idxmin())),
    delta_color="off",
)
k5.metric(
    "Retorno no período",
    f"{((df['usd_brl'].iloc[-1] / df['usd_brl'].iloc[0]) - 1) * 100:.1f}%",
)

st.divider()


# Aba 1: Evolução histórica

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📈 Evolução histórica",
        "🔄 Comparação macro",
        "📐 Correlações",
        "📋 Estatísticas",
    ]
)

with tab1:
    s = df["usd_brl"].dropna()

    fig = go.Figure()

    # Serie principal
    fig.add_trace(
        go.Scatter(
            x=s.index,
            y=s.values,
            name="USD/BRL",
            line=dict(color=PALETTE["primary"], width=2),
            hovertemplate="%{x|%b/%Y}<br>R$ %{y:.4f}<extra></extra>",
        )
    )

    # Media movel
    if show_mm:
        mm = s.rolling(12).mean()
        fig.add_trace(
            go.Scatter(
                x=mm.index,
                y=mm.values,
                name="Média móvel 12m",
                line=dict(color=PALETTE["neutral"], width=1.5, dash="dash"),
                opacity=0.8,
            )
        )

    # Eventos
    if show_events:
        for date_str, label in EVENTS:
            date = pd.Timestamp(date_str)
            if s.index.min() <= date <= s.index.max():
                date_x = date.strftime("%Y-%m-%d")
                fig.add_vline(
                    x=date_x,
                    line_width=1,
                    line_dash="dot",
                    line_color=PALETTE["muted"],
                )
                if show_event_labels:
                    fig.add_annotation(
                        x=date_x,
                        y=1.02,
                        xref="x",
                        yref="paper",
                        text=label,
                        showarrow=False,
                        font=dict(color=PALETTE["muted"], size=10),
                        xanchor="left",
                    )

    fig.update_layout(
        title="USD/BRL — Evolução Histórica",
        yaxis_title="R$ / USD",
        xaxis_title="",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    _apply_plot_style(fig, height=480)
    st.plotly_chart(fig, width="stretch")

    # Volatilidade
    st.subheader("Volatilidade Rolling (3 meses)")
    vol = df["usd_brl_volatilidade"].dropna()
    threshold = vol.quantile(0.90)

    fig_vol = go.Figure()
    fig_vol.add_trace(
        go.Scatter(
            x=vol.index,
            y=vol.values,
            fill="tozeroy",
            fillcolor="rgba(52,152,219,0.15)",
            line=dict(color=PALETTE["neutral"], width=1.5),
            name="Volatilidade",
        )
    )
    fig_vol.add_hline(
        y=threshold,
        line_dash="dot",
        line_color=PALETTE["accent"],
        annotation_text=f"p90 = {threshold:.4f}",
        annotation_font_color=PALETTE["accent"],
    )
    fig_vol.update_layout(
        yaxis_title="σ retornos",
        showlegend=False,
    )
    _apply_plot_style(fig_vol, height=300)
    st.plotly_chart(fig_vol, width="stretch")


# Aba 2: Comparacao macro

with tab2:
    st.subheader(f"USD/BRL × {macro_label}")

    s_cambio = df["usd_brl"].dropna()
    s_macro = df[macro_col].dropna() if macro_col in df.columns else None

    fig2 = make_subplots(specs=[[{"secondary_y": True}]])

    fig2.add_trace(
        go.Scatter(
            x=s_cambio.index,
            y=s_cambio.values,
            name="USD/BRL",
            line=dict(color=PALETTE["primary"], width=2),
        ),
        secondary_y=False,
    )

    if s_macro is not None:
        y_vals = s_macro.astype(float).to_numpy()
        if invert_macro:
            y_vals = s_macro.astype(float).mul(-1).to_numpy()
        fig2.add_trace(
            go.Scatter(
                x=s_macro.index,
                y=y_vals,
                name=macro_label + (" (invertido)" if invert_macro else ""),
                line=dict(color=PALETTE["accent"], width=1.5, dash="dash"),
                opacity=0.85,
            ),
            secondary_y=True,
        )

    if show_events:
        for date_str, label in EVENTS:
            date = pd.Timestamp(date_str)
            if s_cambio.index.min() <= date <= s_cambio.index.max():
                fig2.add_vline(
                    x=date.strftime("%Y-%m-%d"),
                    line_width=0.8,
                    line_dash="dot",
                    line_color=PALETTE["muted"],
                )

    fig2.update_yaxes(title_text="R$ / USD", secondary_y=False)
    fig2.update_yaxes(title_text=macro_label, secondary_y=True)
    fig2.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    _apply_plot_style(fig2, height=480)
    st.plotly_chart(fig2, width="stretch")

    # Rolling correlation
    if macro_col in df.columns:
        rc = rolling_correlation(df, "usd_brl", macro_col, window=12)
        r_total = df["usd_brl"].corr(df[macro_col])

        correlation_caption = (
            f"Correlação de Pearson (período completo): **r = {r_total:+.3f}**"
        )
        st.caption(correlation_caption)

        fig_rc = go.Figure()
        fig_rc.add_trace(
            go.Scatter(
                x=rc.index,
                y=rc.values,
                fill="tozeroy",
                line=dict(color=PALETTE["primary"], width=1.5),
                name="Correlação rolling 12m",
            )
        )
        fig_rc.add_hline(y=0, line_color=PALETTE["muted"], line_dash="dash")
        fig_rc.update_layout(
            title=f"Correlação Rolling 12m — USD/BRL × {macro_label}",
            yaxis=dict(range=[-1.1, 1.1], title="r"),
            showlegend=False,
        )
        _apply_plot_style(fig_rc, height=300)
        st.plotly_chart(fig_rc, width="stretch")


# Aba 3: Correlacoes

with tab3:
    st.subheader("Correlação de Pearson com USD/BRL")

    corr = pearson_correlation(df, target="usd_brl")
    corr_df = corr.reset_index()
    corr_df.columns = ["variável", "correlação"]
    corr_df["magnitude"] = corr_df["correlação"].abs()
    corr_df["sinal"] = corr_df["correlação"].apply(
        lambda v: "Positiva" if v >= 0 else "Negativa"
    )
    corr_df = corr_df.sort_values("magnitude", ascending=True)

    fig_corr = px.bar(
        corr_df,
        x="correlação",
        y="variável",
        orientation="h",
        color="sinal",
        color_discrete_map={
            "Positiva": PALETTE["accent"],
            "Negativa": PALETTE["primary"],
        },
        text="correlação",
        labels={
            "correlação": "r de Pearson",
            "variável": "",
            "sinal": "Direção",
        },
    )
    fig_corr.add_vline(x=0, line_color=PALETTE["muted"], line_dash="dash")
    fig_corr.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    fig_corr.update_traces(texttemplate="%{x:.2f}", textposition="outside")
    _apply_plot_style(fig_corr, height=460)
    st.plotly_chart(fig_corr, width="stretch")

    # Matriz de correlacao
    st.subheader("Matriz de correlação completa")
    cols_num = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    corr_matrix = df[cols_num].corr().round(2)

    fig_heat = px.imshow(
        corr_matrix,
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        text_auto=True,
        aspect="auto",
    )
    fig_heat.update_layout(
        coloraxis_colorbar=dict(title="r"),
    )
    _apply_plot_style(fig_heat, height=600)
    st.plotly_chart(fig_heat, width="stretch")


# Aba 4: Estatisticas

with tab4:
    st.subheader("Estatísticas por subperíodo")
    summary = summary_by_default_periods(df, "usd_brl")
    st.dataframe(summary.round(4), width="stretch")

    st.divider()
    st.subheader("Top 5 máximas e mínimas históricas")
    extremos = find_extremes(df["usd_brl"], n=5)
    extremos["data"] = extremos["data"].dt.strftime("%b/%Y")
    st.dataframe(extremos, width="stretch", hide_index=True)

    st.divider()
    st.subheader("Maiores variações mensais")
    ret = retornos.dropna() * 100
    top_ret = (
        pd.concat(
            [
                ret.nlargest(5).rename("retorno_%"),
                ret.nsmallest(5).rename("retorno_%"),
            ]
        )
        .sort_index()
        .reset_index()
    )
    top_ret.columns = ["data", "retorno_%"]
    top_ret["data"] = top_ret["data"].dt.strftime("%b/%Y")
    top_ret["retorno_%"] = top_ret["retorno_%"].round(2)
    st.dataframe(top_ret, width="stretch", hide_index=True)
