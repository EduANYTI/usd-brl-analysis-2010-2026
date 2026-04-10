# Dicionário de Dados

Este documento descreve todas as variáveis utilizadas no projeto, suas fontes, unidades, periodicidade e observações relevantes para a análise.

---

## 1. Variável principal

### `usd_brl` — Taxa de câmbio USD/BRL

| Atributo | Detalhe |
|---|---|
| **Descrição** | Cotação do dólar americano em reais (preço de venda) |
| **Unidade** | BRL por 1 USD |
| **Periodicidade** | Diária (dias úteis) |
| **Período** | Jan/2010 – Dez/2026 |
| **Fonte** | Banco Central do Brasil — SGS (série 1) ou Yahoo Finance (`BRL=X`) |
| **Coluna no dataset** | `usd_brl` |
| **Observações** | Cotação PTAX de venda. Fins de semana e feriados são preenchidos por forward fill após coleta. |

---

## 2. Variáveis macroeconômicas — Brasil

### `selic` — Taxa Selic

| Atributo | Detalhe |
|---|---|
| **Descrição** | Taxa básica de juros da economia brasileira, definida pelo Copom |
| **Unidade** | % ao ano |
| **Periodicidade** | Diária (meta vigente no dia) |
| **Fonte** | Banco Central do Brasil — SGS (série 432) |
| **Coluna no dataset** | `selic` |
| **Observações** | Utilizada a meta da Selic. Para análise mensal, usa-se o valor vigente no último dia útil do mês. |

---

### `ipca` — Inflação (IPCA)

| Atributo | Detalhe |
|---|---|
| **Descrição** | Índice Nacional de Preços ao Consumidor Amplo — inflação oficial do Brasil |
| **Unidade** | % ao mês (variação mensal) |
| **Periodicidade** | Mensal |
| **Fonte** | IBGE via SIDRA (tabela 1737) ou Banco Central — SGS (série 433) |
| **Coluna no dataset** | `ipca_mensal` |
| **Observações** | Para análise acumulada, calcular soma rolling de 12 meses. |

---

### `ibovespa` — Índice Bovespa

| Atributo | Detalhe |
|---|---|
| **Descrição** | Principal índice de ações da bolsa brasileira (B3) |
| **Unidade** | Pontos |
| **Periodicidade** | Diária (dias úteis) |
| **Fonte** | Yahoo Finance (ticker: `^BVSP`) |
| **Coluna no dataset** | `ibovespa` |
| **Observações** | Usado como proxy do apetite por risco doméstico. Correlação negativa com USD/BRL é esperada em períodos de estresse. |

---

## 3. Variáveis macroeconômicas — EUA

### `fed_funds` — Taxa de juros dos EUA (Fed Funds Rate)

| Atributo | Detalhe |
|---|---|
| **Descrição** | Taxa de juros de referência do Federal Reserve |
| **Unidade** | % ao ano |
| **Periodicidade** | Diária (valor vigente) |
| **Fonte** | FRED — Federal Reserve Bank of St. Louis (série `FEDFUNDS`) |
| **Coluna no dataset** | `fed_funds` |
| **Observações** | Aumentos nos juros dos EUA tendem a fortalecer o dólar globalmente, pressionando moedas emergentes. |

---

### `dxy` — Índice do Dólar (DXY)

| Atributo | Detalhe |
|---|---|
| **Descrição** | Índice que mede o valor do dólar frente a uma cesta de seis moedas principais |
| **Unidade** | Índice (base 100 = março/1973) |
| **Periodicidade** | Diária |
| **Fonte** | Yahoo Finance (ticker: `DX-Y.NYB`) |
| **Coluna no dataset** | `dxy` |
| **Observações** | Captura o fortalecimento global do dólar, separando o efeito externo do efeito doméstico sobre o BRL. |

---

## 4. Commodities

### `petroleo_wti` — Petróleo WTI

| Atributo | Detalhe |
|---|---|
| **Descrição** | Preço do petróleo bruto West Texas Intermediate |
| **Unidade** | USD por barril |
| **Periodicidade** | Diária |
| **Fonte** | Yahoo Finance (ticker: `CL=F`) ou FRED (série `DCOILWTICO`) |
| **Coluna no dataset** | `petroleo_wti` |

---

### `soja` — Soja

| Atributo | Detalhe |
|---|---|
| **Descrição** | Preço futuro da soja no mercado internacional |
| **Unidade** | USD por bushel |
| **Periodicidade** | Diária |
| **Fonte** | Yahoo Finance (ticker: `ZS=F`) |
| **Coluna no dataset** | `soja` |

---

### `minerio_ferro` — Minério de Ferro

| Atributo | Detalhe |
|---|---|
| **Descrição** | Preço do minério de ferro no mercado internacional |
| **Unidade** | USD por tonelada métrica |
| **Periodicidade** | Mensal |
| **Fonte** | FRED (série `PIORECRUSDM`) |
| **Coluna no dataset** | `minerio_ferro` |

---

## 5. Indicadores de risco

### `embi_brasil` — EMBI+ Brasil

| Atributo | Detalhe |
|---|---|
| **Descrição** | Emerging Market Bond Index — mede o risco-país do Brasil (spread sobre T-bonds dos EUA) |
| **Unidade** | Pontos-base (bps) |
| **Periodicidade** | Diária |
| **Fonte** | IPEA (série IPEADATA) ou JP Morgan via fontes secundárias |
| **Coluna no dataset** | `embi_brasil` |
| **Observações** | Alta do EMBI indica aumento do risco percebido e costuma acompanhar depreciação do real. |

---

### `vix` — Índice VIX

| Atributo | Detalhe |
|---|---|
| **Descrição** | Índice de volatilidade implícita do mercado americano (CBOE) — mede o "medo" do mercado global |
| **Unidade** | Pontos |
| **Periodicidade** | Diária |
| **Fonte** | Yahoo Finance (ticker: `^VIX`) |
| **Coluna no dataset** | `vix` |
| **Observações** | Picos do VIX coincidem com crises globais (2008, 2020). Alta do VIX tende a depreciar moedas emergentes. |

---

## 6. Variáveis derivadas (calculadas no projeto)

| Coluna | Descrição | Fórmula |
|---|---|---|
| `usd_brl_retorno` | Retorno diário do câmbio | `pct_change()` |
| `usd_brl_volatilidade` | Volatilidade rolling 21 dias | `rolling(21).std()` |
| `spread_juros` | Diferencial de juros BRL-USD | `selic - fed_funds` |
| `ipca_acumulado_12m` | IPCA acumulado em 12 meses | `rolling(12).sum()` |

---

## 7. Dataset consolidado

Todos os dados são consolidados em um único arquivo após o pipeline de transformação:

- **Arquivo:** `data/processed/dataset_analitico.csv`
- **Frequência:** Mensal (resample das séries diárias)
- **Índice:** `data` (formato `YYYY-MM-DD`, último dia útil do mês)
- **Encoding:** UTF-8
- **Separador:** `,`
