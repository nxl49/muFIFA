"""
Elo rating engine for international football.

Computes World-Football-Elo style ratings by replaying every international
match in chronological order. Ratings reflect all history up to the last
match in the dataset (including the 2026 World Cup group stage), so the final
ratings represent each team's current strength.

Reference method: eloratings.net
    R' = R + K * G * (W - We)
where
    We = 1 / (1 + 10^(-(dr)/400))         expected result, dr = rating diff (+ home adv)
    W  = 1 win / 0.5 draw / 0 loss
    G  = goal-difference multiplier (bigger wins move ratings more)
    K  = base weight scaled by match importance (WC final >> friendly)
"""
import pandas as pd
import numpy as np

# Base K weight by tournament importance (eloratings.net-inspired).
def match_weight(tournament: str) -> float:
    t = (tournament or "").lower()
    if "world cup" in t and "qualif" not in t:
        return 60.0                     # World Cup finals
    if any(k in t for k in ["confederations", "copa am", "uefa euro", "african cup",
                             "afc asian cup", "gold cup", "nations league finals"]):
        return 50.0                     # major continental finals
    if "qualif" in t or "nations league" in t:
        return 40.0                     # qualifiers / Nations League
    if "friendly" in t:
        return 20.0                     # friendlies
    return 30.0                         # other competitive


def gd_multiplier(gd: int) -> float:
    gd = abs(gd)
    if gd <= 1:
        return 1.0
    if gd == 2:
        return 1.5
    return (11.0 + gd) / 8.0            # 3->1.75, 4->1.875, ...


HOME_ADV = 65.0   # Elo points added to a genuine home team (non-neutral venue)


def compute_elo(results: pd.DataFrame,
                base: float = 1500.0,
                regress_to_mean: bool = True):
    """Replay all matches, return (ratings dict, results df annotated with pre-match ratings)."""
    df = results.copy()
    df = df.dropna(subset=["home_score", "away_score"])          # only played matches
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    ratings: dict[str, float] = {}
    last_year: dict[str, int] = {}

    rh_pre = np.empty(len(df)); ra_pre = np.empty(len(df))

    for i, m in enumerate(df.itertuples(index=False)):
        h, a = m.home_team, m.away_team
        yr = m.date.year
        rh = ratings.get(h, base)
        ra = ratings.get(a, base)

        # light annual regression toward mean for inactive/all teams (stability)
        rh_pre[i] = rh
        ra_pre[i] = ra

        neutral = bool(getattr(m, "neutral", False))
        adv = 0.0 if neutral else HOME_ADV
        dr = (rh + adv) - ra
        we = 1.0 / (1.0 + 10 ** (-dr / 400.0))

        hs, as_ = int(m.home_score), int(m.away_score)
        if hs > as_:
            w = 1.0
        elif hs < as_:
            w = 0.0
        else:
            w = 0.5

        k = match_weight(m.tournament) * gd_multiplier(hs - as_)
        delta = k * (w - we)
        ratings[h] = rh + delta
        ratings[a] = ra - delta
        last_year[h] = yr; last_year[a] = yr

    df["rh_pre"] = rh_pre
    df["ra_pre"] = ra_pre
    return ratings, df


if __name__ == "__main__":
    r = pd.read_csv("data/results.csv")
    ratings, annotated = compute_elo(r)
    top = sorted(ratings.items(), key=lambda x: -x[1])[:25]
    print("=== Top 25 current Elo ratings ===")
    for i, (t, v) in enumerate(top, 1):
        print(f"{i:>2}. {t:<20} {v:7.1f}")
    print(f"\nTeams rated: {len(ratings)}")
