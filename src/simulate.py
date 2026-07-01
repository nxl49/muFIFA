"""
Bracket simulator: turns the fitted goal model into knockout predictions.

Two outputs:
  * Deterministic most-likely bracket  -> used to fill the prediction template.
    For each match we pick the winner with the higher advance-probability and a
    coherent representative scoreline (most-likely non-loss score for the winner).
  * Monte-Carlo simulation (N runs)     -> title / round-reached probabilities
    for the methodology note (confidence around the single-path prediction).

Knockout draws are resolved by extra time (goals ~ Poisson at 1/3 rate) then a
penalty shootout modelled as near-coin-flip with a small edge to the stronger
team. Reported score excludes penalty-shootout goals (per template rules).
"""
import numpy as np
import pandas as pd
from ratings import compute_elo, HOME_ADV
from model import (build_training, fit_poisson, fit_rho, expected_goals,
                   score_matrix)
import bracket as B


class Predictor:
    def __init__(self, results_csv="data/results.csv", shootouts_csv="data/shootouts.csv"):
        r = pd.read_csv(results_csv)
        self.ratings, annotated = compute_elo(r)
        asof = annotated["date"].max()
        self.beta = fit_poisson(build_training(annotated, asof))
        self.rho = fit_rho(annotated, self.beta, asof)
        self.asof = asof
        # keep raw results/shootouts so R32 winners can be auto-read once played
        self.results = r.copy()
        self.results["date"] = pd.to_datetime(self.results["date"])
        try:
            self.shootouts = pd.read_csv(shootouts_csv)
            self.shootouts["date"] = pd.to_datetime(self.shootouts["date"])
        except (FileNotFoundError, OSError):
            self.shootouts = None

    def actual_r32_winner(self, home, away):
        """Return the real winner of a Round-of-32 fixture if the dataset has the
        result (incl. penalty shootouts); else None. Lets predictions auto-update
        after `bash data/download.sh` refreshes the dataset."""
        df = self.results
        m = df[(df["tournament"] == "FIFA World Cup")
               & (df["date"] >= "2026-06-28") & (df["date"] < "2026-07-04")
               & (((df["home_team"] == home) & (df["away_team"] == away))
                  | ((df["home_team"] == away) & (df["away_team"] == home)))]
        if len(m) == 0 or pd.isna(m.iloc[0]["home_score"]):
            return None
        row = m.iloc[0]
        hs, as_ = int(row["home_score"]), int(row["away_score"])
        if hs > as_:
            return row["home_team"]
        if as_ > hs:
            return row["away_team"]
        if self.shootouts is not None:                       # regulation draw -> shootout
            sh = self.shootouts[(self.shootouts["date"] == row["date"])
                                & (self.shootouts[["home_team", "away_team"]]
                                   .isin([home, away]).all(axis=1))]
            if len(sh):
                return sh.iloc[0]["winner"]
        return None

    def lambdas(self, home, away, rnd):
        rd = (self.ratings[home] - self.ratings[away]) / 100.0
        lh = expected_goals(self.beta, rd, B.host_adv(home, rnd))
        la = expected_goals(self.beta, -rd, B.host_adv(away, rnd))
        return lh, la

    def elo_winprob_draw(self, home, away, rnd):
        """P(home wins | it reaches a shootout) via Elo expectation."""
        adv = (B.host_adv(home, rnd) - B.host_adv(away, rnd)) * HOME_ADV
        dr = (self.ratings[home] + adv) - self.ratings[away]
        return 1.0 / (1.0 + 10 ** (-dr / 400.0))

    # ---- deterministic single-path prediction -----------------------------
    def predict_match(self, home, away, rnd):
        lh, la = self.lambdas(home, away, rnd)
        M = score_matrix(lh, la, self.rho)
        p_home_reg = np.tril(M, -1).sum()
        p_away_reg = np.triu(M, 1).sum()
        p_draw = np.trace(M)
        s = self.elo_winprob_draw(home, away, rnd)          # home edge in a shootout
        p_home_adv = p_home_reg + p_draw * s
        winner = home if p_home_adv >= 0.5 else away
        p_winner_reg = p_home_reg if winner == home else p_away_reg

        # Representative scoreline reflects the most-likely OUTCOME CATEGORY:
        # if the winner is more likely to win in regulation than to draw, report
        # the modal decisive score; otherwise report the modal draw (advance on
        # penalties). Then pick the highest-probability exact score in that class.
        n = M.shape[0]
        decisive = p_winner_reg >= p_draw
        best, bestp = None, -1.0
        for i in range(n):
            for j in range(n):
                if decisive:
                    ok = (i > j) if winner == home else (j > i)
                else:
                    ok = (i == j)
                if ok and M[i, j] > bestp:
                    bestp, best = M[i, j], (i, j)
        hs, as_ = best
        return {
            "home": home, "away": away, "round": rnd,
            "home_score": hs, "away_score": as_, "winner": winner,
            "xg_home": round(lh, 2), "xg_away": round(la, 2),
            "p_home_adv": round(p_home_adv, 3),
            "lh": lh, "la": la,
        }

    def r32_winner(self, mid, rnd="R32"):
        h, a, locked = B.R32[mid]
        if locked:                                   # hand-locked in bracket.py
            return locked
        actual = self.actual_r32_winner(h, a)        # real result once dataset has it
        if actual:
            return actual
        return self.predict_match(h, a, rnd)["winner"]   # else model prediction

    def deterministic_bracket(self):
        """Resolve R32(pending)->R16->QF->SF->Final. Returns ordered fixtures."""
        fixtures = []

        # R16 teams from R32 winners
        r16_teams = {k: (self.r32_winner(f_home), self.r32_winner(f_away))
                     for k, (f_home, f_away) in B.R16.items()}

        r16_win = {}
        for k in "ABCDEFGH":
            h, a = r16_teams[k]
            p = self.predict_match(h, a, "R16"); p["slot"] = f"R16-{k}"
            fixtures.append(p); r16_win[k] = p["winner"]

        qf_win = {}
        for q, (fh, fa) in B.QF.items():
            h, a = r16_win[fh], r16_win[fa]
            p = self.predict_match(h, a, "QF"); p["slot"] = f"QF{q}"
            fixtures.append(p); qf_win[q] = p["winner"]

        sf_win, sf_lose = {}, {}
        for sfi, (fh, fa) in B.SF.items():
            h, a = qf_win[fh], qf_win[fa]
            p = self.predict_match(h, a, "SF"); p["slot"] = f"SF{sfi}"
            fixtures.append(p)
            sf_win[sfi] = p["winner"]
            sf_lose[sfi] = a if p["winner"] == h else h

        # Third-place play-off: the two beaten semifinalists.
        h, a = sf_lose[B.THIRD_PLACE[0]], sf_lose[B.THIRD_PLACE[1]]
        p = self.predict_match(h, a, "Third"); p["slot"] = "Third"
        fixtures.append(p)

        # Final
        h, a = sf_win[B.FINAL[0]], sf_win[B.FINAL[1]]
        p = self.predict_match(h, a, "Final"); p["slot"] = "Final"
        fixtures.append(p)
        return fixtures

    # ---- Monte-Carlo (probabilities) --------------------------------------
    def _sample_result(self, home, away, rnd, rng):
        lh, la = self.lambdas(home, away, rnd)
        hs = rng.poisson(lh); as_ = rng.poisson(la)
        if hs != as_:
            return home if hs > as_ else away
        # extra time (1/3 rate)
        hs += rng.poisson(lh / 3.0); as_ += rng.poisson(la / 3.0)
        if hs != as_:
            return home if hs > as_ else away
        # shootout: near coin-flip w/ small elo edge
        s = 0.5 + 0.5 * (self.elo_winprob_draw(home, away, rnd) - 0.5)
        return home if rng.random() < s else away

    def monte_carlo(self, n=50000, seed=42):
        rng = np.random.default_rng(seed)
        champ = {}; finalist = {}; last4 = {}
        for _ in range(n):
            r32w = {mid: (lk if (lk := B.R32[mid][2]) else
                          self._sample_result(*B.R32[mid][:2], "R32", rng))
                    for mid in B.R32}
            r16w = {}
            for k, (fh, fa) in B.R16.items():
                r16w[k] = self._sample_result(r32w[fh], r32w[fa], "R16", rng)
            qfw = {}
            for q, (fh, fa) in B.QF.items():
                qfw[q] = self._sample_result(r16w[fh], r16w[fa], "QF", rng)
            sfw = {}
            for sfi, (fh, fa) in B.SF.items():
                t = self._sample_result(qfw[fh], qfw[fa], "SF", rng)
                sfw[sfi] = t
                last4[qfw[fh]] = last4.get(qfw[fh], 0) + 1
                last4[qfw[fa]] = last4.get(qfw[fa], 0) + 1
            fh, fa = sfw[B.FINAL[0]], sfw[B.FINAL[1]]
            finalist[fh] = finalist.get(fh, 0) + 1
            finalist[fa] = finalist.get(fa, 0) + 1
            c = self._sample_result(fh, fa, "Final", rng)
            champ[c] = champ.get(c, 0) + 1
        f = lambda d: {k: v / n for k, v in sorted(d.items(), key=lambda x: -x[1])}
        return f(champ), f(finalist), f(last4)


if __name__ == "__main__":
    P = Predictor()
    print(f"Model asof {P.asof.date()} | beta={np.round(P.beta,3)} rho={P.rho:.3f}\n")

    print("=== Pending R32 predictions (to set the R16 field) ===")
    for mid in range(8, 17):
        h, a, _ = B.R32[mid]
        pr = P.predict_match(h, a, "R32")
        print(f"  {h} vs {a}: {pr['home_score']}-{pr['away_score']} -> {pr['winner']} "
              f"(adv {pr['p_home_adv']:.0%} home)")

    print("\n=== Deterministic most-likely bracket ===")
    for fx in P.deterministic_bracket():
        print(f"  [{fx['slot']:>6}] {fx['home']:>22} {fx['home_score']}-{fx['away_score']} "
              f"{fx['away']:<22} => {fx['winner']}")

    print("\n=== Monte-Carlo title odds (50k sims) ===")
    champ, finalist, last4 = P.monte_carlo(50000)
    for t, p in list(champ.items())[:12]:
        print(f"  {t:<22} champion {p:5.1%} | final {finalist.get(t,0):5.1%} | SF {last4.get(t,0):5.1%}")
