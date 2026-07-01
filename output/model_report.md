# 2026 World Cup Knockout Model - Report

_Model as-of date: 2026-06-29 (ratings include all matches through the 2026 group stage + 7 completed Round-of-32 games)._

## Fitted model parameters

```
Poisson goals:  log(lambda) = 0.0997 + 0.1841*(EloDiff/100) + 0.2442*is_home
Dixon-Coles rho = -0.0471
Backtest (train 2002-2022, test 2023-2026, 3674 matches):
   W/D/L accuracy 60.7%   log-loss 0.866 vs 1.054 base-rate (-17.8%)
```

## Current Elo ratings (top 20)

| # | Team | Elo |
|---|------|-----|
| 1 | Argentina | 2220 |
| 2 | Spain | 2205 |
| 3 | France | 2186 |
| 4 | Brazil | 2112 |
| 5 | England | 2108 |
| 6 | Colombia | 2083 |
| 7 | Portugal | 2054 |
| 8 | Netherlands | 2049 |
| 9 | Morocco | 2034 |
| 10 | Mexico | 2024 |
| 11 | Germany | 1996 |
| 12 | Ecuador | 1988 |
| 13 | Norway | 1985 |
| 14 | Switzerland | 1978 |
| 15 | Japan | 1976 |
| 16 | Croatia | 1965 |
| 17 | Belgium | 1963 |
| 18 | Italy | 1928 |
| 19 | Turkey | 1925 |
| 20 | Denmark | 1924 |

## Locked Round-of-32 results (actual, through June 30 2026)

| Match | Winner |
|-------|--------|
| South Africa vs Canada | **Canada** |
| Netherlands vs Morocco | **Morocco** |
| France vs Sweden | **France** |
| Germany vs Paraguay | **Paraguay** |
| Ivory Coast vs Norway | **Norway** |
| Brazil vs Japan | **Brazil** |
| Mexico vs Ecuador | **Mexico** |

## Predicted pending Round-of-32 (sets the R16 field)

| Fixture | Score | Winner | Win prob |
|---------|-------|--------|----------|
| England vs DR Congo | 1-0 | England | 85% home |
| Belgium vs Senegal | 1-0 | Belgium | 59% home |
| United States vs Bosnia and Herzegovina | 2-0 | United States | 86% home |
| Switzerland vs Algeria | 1-0 | Switzerland | 62% home |
| Spain vs Austria | 1-0 | Spain | 85% home |
| Portugal vs Croatia | 1-0 | Portugal | 63% home |
| Argentina vs Cape Verde | 2-0 | Argentina | 97% home |
| Colombia vs Ghana | 2-0 | Colombia | 92% home |
| Australia vs Egypt | 1-0 | Australia | 58% home |

## Predicted bracket (Round of 16 -> Final)

| Stage | Home | Score | Away | Winner | P(home adv) |
|-------|------|-------|------|--------|-------------|
| R16-A | Canada | 0-1 | Morocco | **Morocco** | 29% |
| R16-B | France | 1-0 | Paraguay | **France** | 84% |
| R16-C | Norway | 0-1 | Brazil | **Brazil** | 32% |
| R16-D | Mexico | 0-1 | England | **England** | 47% |
| R16-E | Belgium | 0-1 | United States | **United States** | 48% |
| R16-F | Switzerland | 0-1 | Spain | **Spain** | 21% |
| R16-G | Portugal | 0-1 | Argentina | **Argentina** | 27% |
| R16-H | Colombia | 1-0 | Australia | **Colombia** | 73% |
| QF1 | Morocco | 0-1 | France | **France** | 29% |
| QF2 | England | 0-1 | Brazil | **Brazil** | 50% |
| QF3 | United States | 0-1 | Spain | **Spain** | 20% |
| QF4 | Argentina | 1-0 | Colombia | **Argentina** | 69% |
| SF1 | France | 1-0 | Brazil | **France** | 61% |
| SF2 | Spain | 0-1 | Argentina | **Argentina** | 48% |
| Third | Brazil | 0-1 | Spain | **Spain** | 37% |
| Final | France | 0-1 | Argentina | **Argentina** | 45% |

## Monte-Carlo tournament simulation (50,000 runs)

| Team | Champion | Reaches Final | Reaches SF |
|------|----------|---------------|------------|
| Argentina | 21.5% | 33.8% | 51.7% |
| France | 21.4% | 38.2% | 59.4% |
| Spain | 18.8% | 30.6% | 52.6% |
| Brazil | 8.9% | 19.1% | 37.5% |
| Colombia | 6.1% | 13.4% | 26.7% |
| England | 5.4% | 12.1% | 23.9% |
| Morocco | 4.4% | 11.8% | 26.1% |
| Mexico | 3.4% | 9.4% | 23.9% |
| Portugal | 2.2% | 5.0% | 10.9% |
| Norway | 1.6% | 5.0% | 14.0% |
| United States | 1.5% | 4.6% | 15.1% |
| Belgium | 1.0% | 3.3% | 10.3% |
| Switzerland | 1.0% | 3.1% | 9.6% |
| Paraguay | 0.5% | 2.2% | 7.4% |
