# Resumo Executivo do Projeto

**USD/BRL 2010–2026: evolução, volatilidade e fatores macroeconômicos**

---

## Sobre o projeto

Este projeto analisa a taxa de câmbio dólar americano–real brasileiro (USD/BRL) ao longo de 16 anos, combinando séries temporais, indicadores macroeconômicos e contextualização de eventos históricos para identificar os principais fatores associados à desvalorização do real.

A análise é estruturada em cinco etapas: coleta de dados, análise exploratória, análise macroeconômica, correlações e modelagem, e comunicação dos resultados via dashboard interativo.

---

## Estrutura analítica

| Etapa | Notebook | Descrição |
|---|---|---|
| 1 | `01_coleta_e_preparacao` | Pipeline de extração e consolidação |
| 2 | `02_analise_exploratoria` | Evolução, retornos, volatilidade |
| 3 | `03_analise_macro` | USD/BRL × variáveis macroeconômicas |
| 4 | `04_correlacoes_e_modelagem` | Correlação e regressão OLS |
| 5 | `05_conclusoes_e_insights` | Síntese e relatório final |

---

## Variáveis analisadas

**Principal:** Taxa de câmbio USD/BRL (PTAX venda)

**Explicativas:** Selic, IPCA, Fed Funds Rate, DXY, Ibovespa, Petróleo WTI, Soja, Minério de Ferro, EMBI+ Brasil, VIX

**Derivadas:** retorno mensal, volatilidade rolling, spread de juros, IPCA acumulado 12m

---

## Hipóteses investigadas

- **H1:** instabilidade política e fiscal deprecia o real (indicadores: EMBI+, Ibovespa)
- **H2:** alta dos juros nos EUA fortalece o dólar (indicadores: Fed Funds, DXY)
- **H3:** crises globais aumentam a aversão ao risco e depreciam emergentes (indicador: VIX)
- **H4:** diferencial de juros Brasil–EUA influencia o câmbio (indicador: Spread Selic–Fed Funds)

---

## Achados principais

*Esta seção deve ser preenchida após a execução completa do pipeline.*

Os resultados detalhados estão disponíveis em [`insights_finais.md`](insights_finais.md).

---

## Como reproduzir

```bash
# 1. Instale as dependências
pip install -r requirements.txt

# 2. Configure a chave da API do FRED no arquivo .env
echo "FRED_API_KEY=sua_chave_aqui" > .env

# 3. Execute os notebooks em ordem
jupyter notebook notebooks/

# 4. (Opcional) Rode o dashboard
streamlit run dashboards/app.py
```

---

## Tecnologias utilizadas

Python 3.10+ · pandas · numpy · statsmodels · scikit-learn · matplotlib · seaborn · plotly · streamlit · yfinance · python-bcb · fredapi
