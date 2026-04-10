# Hipóteses do Projeto

Este documento formaliza as hipóteses analíticas do projeto, apresentando o embasamento teórico de cada uma, os indicadores que serão usados para avaliá-las e os critérios de confirmação ou refutação.

---

## Framework analítico

A taxa de câmbio USD/BRL é determinada por uma combinação de fatores **externos** (condições globais, dólar forte, aversão ao risco) e **internos** (política fiscal, monetária e eventos políticos domésticos). Este projeto não busca construir um modelo preditivo, mas identificar **quais fatores estiveram mais associados às principais oscilações do câmbio** ao longo do período analisado.

As hipóteses abaixo são tratadas como guias da investigação — não como verdades a serem confirmadas, mas como proposições a serem testadas com dados.

---

## H1 — Instabilidade política e fiscal pressiona o real

**Enunciado**
> Períodos de instabilidade política e/ou deterioração fiscal no Brasil estão associados à depreciação do real frente ao dólar.

**Embasamento teórico**

Incerteza política e fiscal aumenta o prêmio de risco exigido por investidores para manter ativos denominados em reais. Isso reduz o fluxo de capital estrangeiro e pressiona o câmbio para cima.

**Indicadores para avaliação**
- EMBI+ Brasil (risco-país)
- Ibovespa (proxy de confiança no mercado doméstico)
- Eventos políticos anotados na série (impeachment, eleições, crises fiscais)

**Critério de avaliação**
- Verificar se picos do EMBI+ e quedas do Ibovespa coincidem visualmente com altas do USD/BRL
- Observar comportamento do câmbio nos 30/60/90 dias seguintes a eventos políticos relevantes

---

## H2 — Juros altos nos EUA fortalecem o dólar e pressionam moedas emergentes

**Enunciado**
> Ciclos de alta dos juros nos Estados Unidos estão associados à valorização do dólar frente ao real e a outras moedas emergentes.

**Embasamento teórico**

Quando o Federal Reserve eleva os juros, o diferencial de retorno entre ativos americanos e emergentes aumenta, incentivando o fluxo de capital para os EUA. Isso valoriza o dólar globalmente e deprecia moedas como o real.

**Indicadores para avaliação**
- Fed Funds Rate
- DXY (índice do dólar frente a moedas desenvolvidas)
- Correlação entre Fed Funds e USD/BRL ao longo do tempo

**Critério de avaliação**
- Correlação positiva entre Fed Funds Rate e USD/BRL nos períodos de ciclo de alta (2015–2018, 2022–2023)
- DXY e USD/BRL com comportamento similar nos mesmos períodos

---

## H3 — Crises globais aumentam a aversão ao risco e depreciam o real

**Enunciado**
> Em momentos de crise global, o aumento da aversão ao risco leva investidores a buscar ativos seguros (dólar, treasuries), o que deprecia moedas emergentes como o real.

**Embasamento teórico**

O dólar funciona como moeda de refúgio (*safe haven*) em períodos de estresse global. Em crises, investidores reduzem exposição a ativos de risco — incluindo emergentes — e aumentam posições em dólar e títulos americanos.

**Indicadores para avaliação**
- VIX (volatilidade implícita — medo do mercado global)
- Comportamento do USD/BRL durante a crise de 2020 (COVID-19) e o *taper tantrum* de 2013
- Correlação entre VIX e USD/BRL

**Critério de avaliação**
- Correlação positiva entre VIX e USD/BRL
- Picos do VIX coincidindo com máximas do USD/BRL nos principais eventos de crise

---

## H4 — O diferencial de juros Brasil–EUA influencia a dinâmica cambial

**Enunciado**
> Quanto maior o diferencial entre a Selic e os juros americanos, menor a pressão de depreciação sobre o real — e vice-versa.

**Embasamento teórico**

A teoria da Paridade Descoberta da Taxa de Juros (UIP) sugere que moedas de países com juros mais altos tendem a se depreciar no longo prazo para compensar o diferencial. Na prática, no curto prazo, juros domésticos elevados atraem capital estrangeiro e podem valorizar a moeda local.

**Indicadores para avaliação**
- `spread_juros` = Selic – Fed Funds Rate
- Correlação entre spread e USD/BRL ao longo do período

**Critério de avaliação**
- Verificar se períodos com spread elevado (Selic bem acima do Fed) coincidem com estabilidade ou apreciação do real
- Observar o comportamento do câmbio quando o spread se estreita (Fed sobe juros enquanto Selic cai ou se mantém)

---

## Resumo das hipóteses

| # | Hipótese resumida | Indicadores-chave | Relação esperada com USD/BRL |
|---|---|---|---|
| H1 | Instabilidade política/fiscal pressiona o real | EMBI+, Ibovespa, eventos | Positiva (EMBI+), negativa (Ibovespa) |
| H2 | Alta dos juros nos EUA fortalece o dólar | Fed Funds, DXY | Positiva |
| H3 | Crises globais depreciam moedas emergentes | VIX | Positiva |
| H4 | Diferencial de juros influencia o câmbio | Spread Selic–Fed Funds | Negativa |

---

## Notas metodológicas

- As hipóteses serão avaliadas de forma **exploratória**, com base em correlações, visualizações e análise contextual — não por meio de testes de hipótese formais (exceto onde indicado).
- A presença de correlação entre variáveis **não implica causalidade**.
- Em diferentes subperíodos, diferentes fatores podem predominar — a análise buscará identificar essa heterogeneidade temporal.
