# Metodologia

Este documento detalha as escolhas metodológicas do projeto, descrevendo cada etapa do pipeline analítico, as decisões técnicas tomadas e as justificativas para os métodos utilizados.

---

## 1. Visão geral do pipeline

```
Fontes externas
      │
      ▼
[1. Coleta] ──► data/raw/
      │
      ▼
[2. Transformação] ──► data/processed/
      │
      ▼
[3. Análise Exploratória]
      │
      ▼
[4. Análise Macroeconômica]
      │
      ▼
[5. Correlações e Modelagem]
      │
      ▼
[6. Comunicação dos Resultados]
```

---

## 2. Coleta de dados

### 2.1 Estratégia de coleta

A coleta é realizada via APIs públicas e arquivos disponibilizados por instituições oficiais, priorizando dados primários sempre que possível.

| Fonte | Método | Biblioteca |
|---|---|---|
| Banco Central (SGS) | API REST | `python-bcb` |
| IBGE (SIDRA) | API REST | `sidrapy` |
| FRED | API REST | `fredapi` |
| Yahoo Finance | API não oficial | `yfinance` |
| IPEADATA | Download CSV | `requests` + `pandas` |

### 2.2 Período de coleta

- **Início:** 01/01/2010
- **Fim:** 31/12/2026 (ou data mais recente disponível)
- Dados anteriores a 2010 não são coletados para manter o foco do projeto

### 2.3 Armazenamento bruto

Cada série é salva individualmente em `data/raw/` no formato `.csv`, com o nome padronizado `{variavel}_{fonte}.csv`. Nenhuma transformação é aplicada nesta etapa — os dados são preservados exatamente como recebidos.

---

## 3. Transformação e preparação

### 3.1 Padronização de datas

- Todas as séries são convertidas para o tipo `datetime` com `pd.to_datetime()`
- O índice de todas as séries é definido como a coluna `data`
- Formato padrão: `YYYY-MM-DD`

### 3.2 Tratamento de valores ausentes

| Tipo de dado | Estratégia |
|---|---|
| Séries diárias (câmbio, bolsa) | Forward fill (`ffill`) para fins de semana e feriados |
| Séries mensais (IPCA) | Sem interpolação — mantido o valor mensal original |
| Dados pontuais ausentes | Avaliados caso a caso; documentados no notebook |

### 3.3 Reamostragem (resample)

Para a análise principal, todas as séries diárias são reamostradas para frequência **mensal**, utilizando o último valor disponível no mês (`resample('ME').last()`). Isso garante consistência ao combinar séries com periodicidades diferentes.

### 3.4 Consolidação

Após a padronização individual, todas as séries são unidas em um único `DataFrame` via `pd.merge()` com `how='inner'`, garantindo que apenas os períodos com dados completos sejam incluídos na análise principal.

O dataset final é salvo em `data/processed/dataset_analitico.csv`.

---

## 4. Análise exploratória

### 4.1 Evolução histórica

- Gráfico de linha do USD/BRL ao longo do período completo
- Anotação de eventos macroeconômicos relevantes no gráfico
- Decomposição visual em subperíodos (ex: 2010–2014, 2015–2018, 2019–2022, 2023–2026)

### 4.2 Estatísticas descritivas por período

Para cada subperíodo definido:
- Média, mediana, mínimo, máximo
- Desvio padrão
- Variação percentual acumulada

### 4.3 Análise de volatilidade

- **Retorno diário:** variação percentual dia a dia (`pct_change()`)
- **Volatilidade rolling:** desvio padrão dos retornos em janela de 21 dias úteis (~1 mês)
- Identificação dos períodos de maior volatilidade com base nos percentis 90 e 95

---

## 5. Análise macroeconômica

### 5.1 Comparação visual

Gráficos com dois eixos Y (câmbio + variável macroeconômica) para identificar padrões visuais de co-movimento entre:
- USD/BRL × Selic
- USD/BRL × IPCA acumulado 12m
- USD/BRL × Fed Funds Rate
- USD/BRL × DXY
- USD/BRL × Ibovespa
- USD/BRL × VIX
- USD/BRL × EMBI+ Brasil

### 5.2 Contextualização por eventos

Os seguintes eventos são marcados na série histórica com anotações visuais:

| Período | Evento |
|---|---|
| 2013 | Crise do "taper tantrum" (Fed sinaliza fim do QE) |
| 2014–2015 | Crise fiscal e rebaixamento do rating do Brasil |
| 2016 | Impeachment de Dilma Rousseff |
| 2018 | Greve dos caminhoneiros; eleições presidenciais |
| 2020 | Pandemia de COVID-19 |
| 2021–2022 | Alta dos juros nos EUA; crise fiscal doméstica |
| 2023–2026 | Ciclo de política monetária; âncora fiscal |

---

## 6. Correlações e modelagem

### 6.1 Análise de correlação

- **Correlação de Pearson** entre USD/BRL e cada variável explicativa
- Heatmap de correlação entre todas as variáveis
- Correlação rolling (janela de 12 meses) para avaliar estabilidade temporal das correlações

> ⚠️ Correlação não implica causalidade. Os resultados são tratados como exploratórios.

### 6.2 Regressão linear simples

Para cada variável explicativa, estima-se uma regressão simples:

```
USD/BRL_t = β₀ + β₁ × X_t + ε_t
```

Métricas reportadas: R², coeficiente estimado, p-valor e intervalo de confiança.

### 6.3 Regressão linear múltipla

Modelo com múltiplas variáveis explicativas selecionadas com base nas correlações e na teoria econômica:

```
USD/BRL_t = β₀ + β₁·DXY_t + β₂·EMBI_t + β₃·spread_juros_t + β₄·VIX_t + ε_t
```

Avaliação de:
- Multicolinearidade (VIF)
- Resíduos (normalidade, autocorrelação via teste de Durbin-Watson)
- Ajuste do modelo (R² ajustado, AIC/BIC)

### 6.4 Limitações do modelo

- A relação câmbio–juros é bidirecional (endogeneidade); a regressão OLS não captura essa dinâmica
- Variáveis omitidas relevantes (expectativas, fluxo de capitais) podem inflar os resíduos
- O modelo é **descritivo e exploratório**, não preditivo

---

## 7. Comunicação dos resultados

### 7.1 Gráficos

Todos os gráficos são gerados com `matplotlib`/`seaborn` para versões estáticas e `plotly` para versões interativas. Exportados em `.png` (300 dpi) para `reports/figures/`.

### 7.2 Dashboard

O dashboard interativo em Streamlit (`dashboard/app.py`) permite:
- Selecionar o período de análise
- Visualizar o câmbio com anotações de eventos
- Comparar USD/BRL com as variáveis macroeconômicas
- Consultar estatísticas descritivas por período

### 7.3 Relatórios

- `reports/project_summary.md` — resumo executivo do projeto
- `reports/insights_finais.md` — síntese dos principais achados analíticos
