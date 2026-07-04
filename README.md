# ⚽ muFIFA — 2026 World Cup Knockout Predictor

A machine-learning model that predicts the 2026 FIFA World Cup knockout stage
(**Round of 16 → Final**, incl. the third-place play-off) and fills the
competition submission template with scorelines, goalscorers (by shirt number),
and the advancing team.

> **Headline prediction: 🇦🇷 Argentina champions**, beating France in the final;
> Brazil and Spain the other semifinalists.

### Deliverables
| # | Deliverable | Path |
|---|-------------|------|
| 1 | **ML notebook** (runs top-to-bottom, generates everything) | [`notebooks/mufifa_worldcup_2026.ipynb`](notebooks/mufifa_worldcup_2026.ipynb) |
| 2 | **Filled submission CSV** — matches the platform's **currently active** template (Quarterfinal→Final; the Round-of-16 submission window has closed) | [`output/predictions.csv`](output/predictions.csv) |
| – | Full R16→Final reference (all 16 fixtures, for the record) | [`output/predictions_full_r16_final.csv`](output/predictions_full_r16_final.csv) |
| – | Model report (ratings, params, title odds) | [`output/model_report.md`](output/model_report.md) |
| – | Modular source (mirror of the notebook) | [`src/`](src/) |

> **Note on templates:** the submission platform's template shape changes as
> the tournament progresses. [`templates/mufifa26_template_qf_final.csv`](templates/mufifa26_template_qf_final.csv)
> is the currently-active one (`QF_001`…`F_001`, `"TBD"` placeholders); the
> earlier [`templates/mufifa26_template_r16_final.csv`](templates/mufifa26_template_r16_final.csv)
> (`R16_001`…`F_001`) is kept for reference. `src/build_predictions.py` takes
> the template path as an argument, so pointing it at whichever template the
> platform currently accepts regenerates the correctly-shaped CSV.

---

## Approach (Pipeline A)

```
 historical results (1872–2026)               2026 squad numbers (verified)
        │                                              │
        ▼                                              ▼
  ┌────────────┐   ┌────────────────────┐   ┌──────────────────────┐
  │ Elo ratings │──▶│ Poisson goal model │──▶│ bracket simulation   │──▶ predictions.csv
  │ (chrono     │   │ + Dixon-Coles      │   │ (deterministic path  │
  │  replay)    │   │ (trained by MLE)   │   │  + 50k Monte-Carlo)  │
  └────────────┘   └────────────────────┘   └──────────────────────┘
                                                     │
                          scorer propensity (goalscorers.csv) ┘
```

1. **Elo ratings** — every international match since 1872 replayed in date order
   (importance-weighted `K`, goal-difference multiplier, home advantage). Ratings
   already reflect 2026 group-stage + early-knockout form.
2. **Trained goal model** — weighted **Poisson regression** mapping *(Elo diff,
   home/host) → expected goals*, with a **Dixon-Coles** low-score correction.
   Both fit by maximum likelihood on the modern era (2002+), recency-weighted.
3. **Simulation** — the exact bracket (adjacency verified against the already-
   scheduled Canada-vs-Morocco R16 fixture) resolved as a **deterministic
   most-likely path** (for the submission) and a **50,000-run Monte-Carlo** (for
   title odds). Draws → extra time (⅓-rate goals) → near-coin-flip shootout.
4. **Scorers** — each team's recent goalscorers (recency-weighted, own goals
   removed) ranked and mapped to verified 2026 shirt numbers.

## Why this is trustworthy

Strict temporal backtest — train on 2002-2022, predict W/D/L on **3,674 matches
from 2023-2026 the model never saw** (Elo uses only pre-match info → no leakage):

| Metric | Model | Base-rate baseline |
|--------|-------|--------------------|
| 3-way accuracy | **60.8 %** | — |
| Log-loss | **0.865** | 1.054 (**−17.9 %**) |

## Run it

```bash
python3 -m venv .venv
.venv/bin/pip install numpy pandas scipy matplotlib jupyter nbconvert
bash data/download.sh          # fetch the datasets (a pinned snapshot is committed)

# Option A — the notebook (recommended):
.venv/bin/jupyter notebook notebooks/mufifa_worldcup_2026.ipynb

# Option B — scripts:
.venv/bin/python src/validate.py          # honest backtest
.venv/bin/python src/build_predictions.py # -> output/predictions.csv
.venv/bin/python src/report.py            # -> output/model_report.md
```

## Round of 16 field (actual — Round of 32 complete)

The Round of 32 is done, so predictions run from the **actual** R16 fixtures,
hard-coded in [`src/bracket.py`](src/bracket.py) and verified against the official
bracket:

| QF | Round-of-16 fixtures feeding it |
|----|---------------------------------|
| QF1 | Canada–Morocco · Paraguay–France |
| QF2 | Brazil–Norway · Mexico–England |
| QF3 | Portugal–Spain · USA–Belgium |
| QF4 | Argentina–Egypt · Switzerland–Colombia |

To regenerate after a later round is played, refresh the data and re-run — ratings
update automatically from the new results:

```bash
bash data/download.sh
.venv/bin/python src/build_predictions.py   # -> output/predictions.csv
```

## Data
- **Results / goalscorers / shootouts** — [martj42/international_results](https://github.com/martj42/international_results)
  (49k matches, 48k goal records; current through July 2026 incl. scheduled fixtures).
  A snapshot is committed under `data/` so predictions are exactly reproducible.
- **2026 shirt numbers & Round-of-32 results** — official FA/press releases and
  live match reporting (June–July 2026), verified per player.

## Honest limitations
- **Winners/bracket are far more reliable than exact scores.** Football is
  low-scoring and high-variance; every predicted knockout scoreline is the single
  *most-likely* exact score (usually 1-0 between good sides).
- **Scorers are best-effort** — the top goal threat is the optimal single guess.
- Host-advantage handling assumes USA plays all knockouts at home and Mexico is at
  home through the R16; Canada's R16 is in the USA (treated neutral).

## Repo layout
```
notebooks/mufifa_worldcup_2026.ipynb   the ML notebook (deliverable 1)
src/ratings.py                          Elo engine
src/model.py                            Poisson + Dixon-Coles goal model
src/validate.py                         temporal backtest
src/bracket.py                          2026 bracket + locked R32 results
src/simulate.py                         deterministic + Monte-Carlo simulator
src/squads.py                           2026 shirt numbers
src/build_predictions.py                fills the template -> output/predictions.csv
src/report.py                           model_report.md generator
templates/mufifa26_template_qf_final.csv  active template (QF -> Final)
templates/mufifa26_template_r16_final.csv earlier template (R16 -> Final, reference)
output/predictions.csv                  filled submission (deliverable 2)
data/                                    dataset snapshot + download.sh
```
