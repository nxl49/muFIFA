# 2026 World Cup Knockout Model - Report

_Model as-of date: 2026-07-03 (ratings include all matches through the completed 2026 Round of 32). Predictions run from the actual Round of 16._

## Fitted model parameters

```
Poisson goals:  log(lambda) = 0.0999 + 0.1841*(EloDiff/100) + 0.2440*is_home
Dixon-Coles rho = -0.0472
Backtest (train 2002-2022, test 2023-2026, 3674 matches):
   W/D/L accuracy 60.7%   log-loss 0.866 vs 1.054 base-rate (-17.8%)
```

## Current Elo ratings (top 20)

| # | Team | Elo |
|---|------|-----|
| 1 | Argentina | 2222 |
| 2 | Spain | 2221 |
| 3 | France | 2197 |
| 4 | England | 2118 |
| 5 | Brazil | 2112 |
| 6 | Colombia | 2088 |
| 7 | Portugal | 2076 |
| 8 | Mexico | 2056 |
| 9 | Netherlands | 2049 |
| 10 | Morocco | 2034 |
| 11 | Switzerland | 2012 |
| 12 | Norway | 2005 |
| 13 | Germany | 1996 |
| 14 | Belgium | 1988 |
| 15 | Japan | 1976 |
| 16 | Ecuador | 1956 |
| 17 | Croatia | 1943 |
| 18 | Italy | 1928 |
| 19 | Turkey | 1925 |
| 20 | Denmark | 1924 |

## Actual Round of 16 fixtures (from completed Round of 32)

| # | Fixture |
|---|---------|
| 1 | Canada vs Morocco |
| 2 | Paraguay vs France |
| 3 | Brazil vs Norway |
| 4 | Mexico vs England |
| 5 | Portugal vs Spain |
| 6 | United States vs Belgium |
| 7 | Argentina vs Egypt |
| 8 | Switzerland vs Colombia |

## Predicted bracket (Round of 16 -> Final)

| Stage | Home | Score | Away | Winner | P(home adv) |
|-------|------|-------|------|--------|-------------|
| R16-0 | Canada | 0-1 | Morocco | **Morocco** | 29% |
| R16-1 | Paraguay | 0-1 | France | **France** | 15% |
| R16-2 | Brazil | 1-0 | Norway | **Brazil** | 65% |
| R16-3 | Mexico | 1-0 | England | **Mexico** | 51% |
| R16-4 | Portugal | 0-1 | Spain | **Spain** | 30% |
| R16-5 | United States | 1-0 | Belgium | **United States** | 50% |
| R16-6 | Argentina | 2-0 | Egypt | **Argentina** | 90% |
| R16-7 | Switzerland | 0-1 | Colombia | **Colombia** | 39% |
| QF-0 | Morocco | 0-1 | France | **France** | 28% |
| QF-1 | Brazil | 1-0 | Mexico | **Brazil** | 58% |
| QF-2 | Spain | 1-0 | United States | **Spain** | 81% |
| QF-3 | Argentina | 1-0 | Colombia | **Argentina** | 69% |
| SF-0 | France | 1-0 | Brazil | **France** | 62% |
| SF-1 | Spain | 0-1 | Argentina | **Argentina** | 50% |
| Third | Brazil | 0-1 | Spain | **Spain** | 35% |
| Final | France | 0-1 | Argentina | **Argentina** | 46% |

## Monte-Carlo tournament simulation (50,000 runs)

| Team | Champion | Reaches Final | Reaches SF |
|------|----------|---------------|------------|
| Argentina | 23.5% | 37.7% | 61.3% |
| France | 21.1% | 39.2% | 61.0% |
| Spain | 18.9% | 30.3% | 52.5% |
| Brazil | 7.4% | 16.8% | 34.0% |
| England | 6.1% | 13.5% | 26.9% |
| Colombia | 4.8% | 10.5% | 23.0% |
| Mexico | 3.9% | 10.4% | 24.4% |
| Morocco | 3.8% | 11.0% | 25.2% |
| Portugal | 3.5% | 7.8% | 19.6% |
| Switzerland | 1.7% | 4.6% | 12.5% |
| Norway | 1.7% | 5.4% | 14.7% |
| Belgium | 1.4% | 4.3% | 14.2% |
| United States | 1.4% | 4.1% | 13.7% |
| Paraguay | 0.4% | 2.0% | 7.0% |
