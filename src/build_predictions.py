"""
End-to-end: build the filled prediction template (Round of 16 -> Final).

Pipeline:
  ratings (Elo) -> goal model (Poisson + Dixon-Coles) -> deterministic bracket
  -> scorer assignment -> output/predictions.csv

Scorer assignment is data-driven: each team's goalscorers over the last few
years (recency-weighted, own goals removed) are ranked, and the top-ranked
players with a known 2026 shirt number are chosen, one per predicted goal.
"""
import pandas as pd
import numpy as np
from simulate import Predictor
from squads import SQUAD_NUMBERS, canonical
import bracket as B

TEMPLATE = "templates/mufifa26_template.csv"


def scorer_ranking(goalscorers_csv="data/goalscorers.csv", since="2021-01-01",
                   half_life_years=2.5):
    g = pd.read_csv(goalscorers_csv)
    g["date"] = pd.to_datetime(g["date"])
    asof = g["date"].max()
    g = g[(~g["own_goal"].fillna(False)) & (g["date"] >= since)].copy()
    g["w"] = 0.5 ** ((asof - g["date"]).dt.days / (365 * half_life_years))
    g["player"] = g["scorer"].map(canonical)
    ranked = (g.groupby(["team", "player"])["w"].sum()
              .reset_index().sort_values(["team", "w"], ascending=[True, False]))
    out = {}
    for team, sub in ranked.groupby("team"):
        out[team] = list(sub["player"])
    return out


def pick_scorers(team, n_goals, ranking):
    """Return jersey numbers (list) for a team scoring n_goals."""
    if n_goals <= 0:
        return []
    numbers = SQUAD_NUMBERS.get(team, {})
    chosen = []
    for name in ranking.get(team, []):
        if name in numbers and numbers[name] not in chosen:
            chosen.append(numbers[name])
        if len(chosen) >= n_goals:
            break
    if not chosen and numbers:                       # fallback: top-numbered attacker
        chosen = [sorted(numbers.values())[0]]
    while len(chosen) < n_goals and chosen:          # a player can score again
        chosen.append(chosen[0])
    return chosen[:n_goals]


def main():
    P = Predictor()
    ranking = scorer_ranking()
    fixtures = P.deterministic_bracket()

    # index predictions by the official match_id
    by_id = {}
    for fx in fixtures:
        mid = B.MATCH_IDS[fx["slot"]]
        hs, as_ = fx["home_score"], fx["away_score"]
        by_id[mid] = {
            "home_team": fx["home"],
            "away_team": fx["away"],
            "predicted_home_score": hs,
            "predicted_away_score": as_,
            "predicted_scorers_home": ";".join(map(str, pick_scorers(fx["home"], hs, ranking))),
            "predicted_scorers_away": ";".join(map(str, pick_scorers(fx["away"], as_, ranking))),
            "predicted_winner": fx["winner"],
        }

    # fill the official template row-by-row, preserving its match_id order
    tmpl = pd.read_csv(TEMPLATE, dtype=str, keep_default_na=False)
    for i, row in tmpl.iterrows():
        pred = by_id.get(row["match_id"])
        if pred:
            for k, v in pred.items():
                tmpl.at[i, k] = v
    df = tmpl
    out = "output/predictions.csv"
    df.to_csv(out, index=False)

    # validate the "scorers <= score" rule and that every row is filled
    ok = True
    for _, r in df.iterrows():
        nh = 0 if r.predicted_scorers_home == "" else len(r.predicted_scorers_home.split(";"))
        na = 0 if r.predicted_scorers_away == "" else len(r.predicted_scorers_away.split(";"))
        if nh > int(r.predicted_home_score) or na > int(r.predicted_away_score):
            ok = False
            print("RULE VIOLATION:", r.to_dict())
        if not r.home_team or not r.predicted_winner:
            ok = False
            print("UNFILLED ROW:", r["match_id"])
    print(f"Wrote {out}  ({len(df)} rows) | scorers<=score + all-filled: {'OK' if ok else 'FAILED'}\n")
    with pd.option_context("display.max_columns", None, "display.width", 220):
        print(df.to_string(index=False))
    return df


if __name__ == "__main__":
    main()
