# USD/BRL 2010–2026: evolução, volatilidade e fatores macroeconômicos

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458)
![Status](https://img.shields.io/badge/Status-Em%20desenvolvimento-orange)
![License](https://img.shields.io/badge/License-MIT-green)

## Visão geral

Este projeto tem como objetivo analisar a evolução da taxa de câmbio **dólar americano (USD) x real brasileiro (BRL)** entre **2010 e 2026**, identificando padrões históricos, períodos de maior volatilidade e os principais fatores que contribuíram para a valorização do dólar frente ao real ao longo do tempo.

A análise combina **séries temporais**, **indicadores macroeconômicos**, **eventos econômicos e políticos relevantes** e **visualizações analíticas**, com foco em gerar insights claros, contextualizados e úteis para interpretação econômica.

---

## Objetivo

Investigar o comportamento do câmbio **USD/BRL** no período de 2010 a 2026 e avaliar como variáveis econômicas, monetárias e eventos de risco podem ter influenciado os movimentos de alta do dólar frente ao real.

---

## Problema de análise

Ao longo dos últimos anos, o real passou por diversos períodos de desvalorização frente ao dólar. No entanto, a variação cambial não pode ser explicada por um único fator.

Este projeto busca responder, com base em dados:

- quando ocorreram os principais movimentos de alta do dólar;
- quais variáveis macroeconômicas acompanharam essas oscilações;
- como eventos internos e externos impactaram o câmbio;
- quais fatores parecem ter exercido maior influência em diferentes momentos da série histórica.

---

## Perguntas que o projeto busca responder

- Como o dólar variou frente ao real entre 2010 e 2026?
- Quais foram os períodos de maior alta e maior volatilidade?
- Em quais momentos o câmbio apresentou movimentos mais abruptos?
- Como Selic, inflação e juros dos EUA se relacionaram com o USD/BRL?
- Eventos políticos e crises internacionais tiveram impacto perceptível na taxa de câmbio?
- Houve períodos em que fatores domésticos foram mais relevantes que fatores externos?

---

## Hipóteses do projeto

- Períodos de instabilidade política e fiscal no Brasil contribuíram para a desvalorização do real.
- O fortalecimento global do dólar e o aumento dos juros nos Estados Unidos pressionaram moedas emergentes, incluindo o real.
- Em momentos de crise, o aumento da aversão ao risco levou investidores a buscar ativos mais seguros, favorecendo o dólar.
- A diferença entre os juros do Brasil e dos EUA pode ajudar a explicar parte da dinâmica cambial.

---

## Escopo da análise

### Variável principal
- **Taxa de câmbio USD/BRL**

### Variáveis explicativas
- **Selic**
- **IPCA**
- **Juros dos EUA**
- **Ibovespa**
- **Commodities**
- **Indicadores de risco**
- **Eventos macroeconômicos e políticos relevantes**

---

## Fontes de dados

As bases do projeto podem ser obtidas em fontes públicas e amplamente utilizadas em análises econômicas:

- **Banco Central do Brasil**
- **IBGE**
- **IPEA**
- **FRED**
- **Yahoo Finance**
- outras bases públicas complementares

---

## Metodologia

O projeto está estruturado em cinco etapas principais:

### 1. Coleta e preparação dos dados
- importação das séries históricas;
- padronização de datas e colunas;
- tratamento de valores ausentes;
- consolidação das bases em um dataset analítico.

### 2. Análise exploratória
- evolução histórica do USD/BRL;
- médias por período;
- máximas e mínimas;
- variação percentual;
- medidas de volatilidade.

### 3. Análise contextual e macroeconômica
- comparação entre o câmbio e indicadores macroeconômicos;
- leitura dos movimentos com base no contexto econômico e político;
- identificação de eventos relevantes na série.

### 4. Correlações e modelagem
- análise de correlação entre variáveis;
- testes com regressão linear e múltipla;
- avaliação exploratória do peso relativo de diferentes fatores.

### 5. Comunicação dos resultados
- produção de gráficos;
- construção de dashboard interativo;
- síntese de insights em linguagem clara e analítica.

---

## Estrutura do repositório

```bash
usd-brl-analysis-2010-2026/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│   ├── 01_coleta_e_preparacao.ipynb
│   ├── 02_analise_exploratoria.ipynb
│   ├── 03_analise_macro.ipynb
│   ├── 04_correlacoes_e_modelagem.ipynb
│   └── 05_conclusoes_e_insights.ipynb
│
├── src/
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   ├── indicators.py
│   ├── plots.py
│   └── utils.py
│
├── dashboard/
│   └── app.py
│
├── reports/
│   ├── figures/
│   ├── project_summary.md
│   └── insights_finais.md
│
├── docs/
│   ├── metodologia.md
│   ├── dicionario_de_dados.md
│   └── hipoteses_do_projeto.md
│
├── README.md
├── requirements.txt
└── .gitignore
