"""
Honest temporal backtest: train the goal model on 2002-2022, predict W/D/L on
2023-2026 matches it never saw. Elo ratings use only pre-match info (rh_pre/
ra_pre are computed chronologically), so there is no rating leakage.

Reports accuracy and multiclass log-loss vs a naive base-rate baseline.
"""
import numpy as np
import pandas as pd
from ratings import compute_elo
from model import build_training, fit_poisson, fit_rho, expected_goals, score_matrix

def wdl_probs(beta, rho, ratings_diff, home_adv):
    lh = expected_goals(beta, ratings_diff, home_adv)
    la = expected_goals(beta, -ratings_diff, 0)
    M = score_matrix(lh, la, rho)
    p_home = np.tril(M, -1).sum()
    p_draw = np.trace(M)
    p_away = np.triu(M, 1).sum()
    return np.array([p_home, p_draw, p_away])

if __name__ == "__main__":
    r = pd.read_csv("data/results.csv")
    ratings, annotated = compute_elo(r)

    cutoff = pd.Timestamp("2023-01-01")
    train_slice = annotated[annotated["date"] < cutoff]
    beta = fit_poisson(build_training(train_slice, cutoff))
    rho = fit_rho(train_slice, beta, cutoff)
    print(f"Trained on { (annotated['date']<cutoff).sum() } matches (pre-2023)")
    print(f"beta={np.round(beta,4)} rho={rho:.4f}\n")

    test = annotated[(annotated["date"] >= cutoff)].dropna(subset=["home_score", "away_score"])
    # focus on competitive-ish, but evaluate all
    n = len(test); correct = 0; ll = 0.0; base_ll = 0.0
    # base rates (home/draw/away) from training
    tr = train_slice.dropna(subset=["home_score","away_score"])
    br = np.array([(tr.home_score>tr.away_score).mean(),
                   (tr.home_score==tr.away_score).mean(),
                   (tr.home_score<tr.away_score).mean()])
    for m in test.itertuples(index=False):
        rd = (m.rh_pre - m.ra_pre)/100.0
        ha = 0.0 if bool(getattr(m,"neutral",False)) else 1.0
        p = wdl_probs(beta, rho, rd, ha)
        p = np.clip(p, 1e-9, None); p /= p.sum()
        if m.home_score>m.away_score: y=0
        elif m.home_score==m.away_score: y=1
        else: y=2
        if p.argmax()==y: correct+=1
        ll += -np.log(p[y])
        base_ll += -np.log(br[y])
    print(f"Test matches (2023-2026): {n}")
    print(f"Accuracy (argmax W/D/L):   {correct/n:.3f}")
    print(f"Model  log-loss:           {ll/n:.4f}")
    print(f"Baseline (base-rate) LL:   {base_ll/n:.4f}")
    print(f"Improvement over baseline: {(base_ll-ll)/n:.4f} nats/match "
          f"({100*(base_ll-ll)/base_ll:.1f}% lower loss)")
