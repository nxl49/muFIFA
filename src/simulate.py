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
    def __init__(self, results_csv="data/results.csv"):
        r = pd.read_csv(results_csv)
        self.ratings, annotated = compute_elo(r)
        asof = annotated["date"].max()
        self.beta = fit_poisson(build_training(annotated, asof))
        self.rho = fit_rho(annotated, self.beta, asof)
        self.asof = asof

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

    def deterministic_bracket(self):
        """Resolve the actual R16 fixtures -> QF -> SF -> 3rd/Final. Ordered list."""
        fixtures = []

        # Round of 16 — actual fixtures
        r16_win = []
        for i, (h, a) in enumerate(B.R16_FIXTURES):
            p = self.predict_match(h, a, "R16"); p["slot"] = f"R16-{i}"
            fixtures.append(p); r16_win.append(p["winner"])

        # Quarterfinals
        qf_win = []
        for q, (i, j) in enumerate(B.QF_PAIRS):
            p = self.predict_match(r16_win[i], r16_win[j], "QF"); p["slot"] = f"QF-{q}"
            fixtures.append(p); qf_win.append(p["winner"])

        # Semifinals
        sf_win, sf_lose = [], []
        for si, (i, j) in enumerate(B.SF_PAIRS):
            p = self.predict_match(qf_win[i], qf_win[j], "SF"); p["slot"] = f"SF-{si}"
            fixtures.append(p)
            sf_win.append(p["winner"])
            sf_lose.append(p["away"] if p["winner"] == p["home"] else p["home"])

        # Third-place play-off: the two beaten semifinalists.
        i, j = B.THIRD_PAIR
        p = self.predict_match(sf_lose[i], sf_lose[j], "Third"); p["slot"] = "Third"
        fixtures.append(p)

        # Final
        i, j = B.FINAL_PAIR
        p = self.predict_match(sf_win[i], sf_win[j], "Final"); p["slot"] = "Final"
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
            r16w = [self._sample_result(h, a, "R16", rng) for h, a in B.R16_FIXTURES]
            qfw = [self._sample_result(r16w[i], r16w[j], "QF", rng) for i, j in B.QF_PAIRS]
            sfw = []
            for i, j in B.SF_PAIRS:
                t = self._sample_result(qfw[i], qfw[j], "SF", rng)
                sfw.append(t)
                last4[qfw[i]] = last4.get(qfw[i], 0) + 1
                last4[qfw[j]] = last4.get(qfw[j], 0) + 1
            fh, fa = sfw[B.FINAL_PAIR[0]], sfw[B.FINAL_PAIR[1]]
            finalist[fh] = finalist.get(fh, 0) + 1
            finalist[fa] = finalist.get(fa, 0) + 1
            c = self._sample_result(fh, fa, "Final", rng)
            champ[c] = champ.get(c, 0) + 1
        f = lambda d: {k: v / n for k, v in sorted(d.items(), key=lambda x: -x[1])}
        return f(champ), f(finalist), f(last4)


if __name__ == "__main__":
    P = Predictor()
    print(f"Model asof {P.asof.date()} | beta={np.round(P.beta,3)} rho={P.rho:.3f}\n")

    print("=== Deterministic most-likely bracket (R16 -> Final) ===")
    for fx in P.deterministic_bracket():
        print(f"  [{fx['slot']:>6}] {fx['home']:>22} {fx['home_score']}-{fx['away_score']} "
              f"{fx['away']:<22} => {fx['winner']}")

    print("\n=== Monte-Carlo title odds (50k sims) ===")
    champ, finalist, last4 = P.monte_carlo(50000)
    for t, p in list(champ.items())[:12]:
        print(f"  {t:<22} champion {p:5.1%} | final {finalist.get(t,0):5.1%} | SF {last4.get(t,0):5.1%}")
