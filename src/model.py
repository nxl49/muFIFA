"""
Trained goal model: maps Elo strength -> expected goals, with a Dixon-Coles
low-score correction. This is the machine-learning core.

Two components, both fit by maximum likelihood on historical results:

1. Poisson regression for goals scored by a team:
       log(lambda) = b0 + b1 * (elo_team - elo_opp)/100 + b2 * is_home
   Fit on a stacked (team-perspective) view of every modern match, with
   exponential time-decay weighting so recent football counts more.

2. Dixon-Coles dependence parameter rho, correcting the independent-Poisson
   under-prediction of 0-0 / 1-0 / 0-1 / 1-1 scorelines. Fit by MLE given (1).

The fitted params are used by simulate.py to build score-probability matrices.
"""
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import poisson
from ratings import compute_elo

MODERN_FROM = "2002-01-01"     # calibrate scoring on the modern era
HALF_LIFE_DAYS = 365 * 8       # time-decay half life for the goals model


def build_training(annotated: pd.DataFrame, asof: pd.Timestamp):
    """Stacked team-perspective rows from played matches in the modern era."""
    d = annotated[annotated["date"] >= MODERN_FROM].copy()
    # weight by recency
    age_days = (asof - d["date"]).dt.days.clip(lower=0)
    w = 0.5 ** (age_days / HALF_LIFE_DAYS)
    d["w"] = w

    neutral = d["neutral"].fillna(False).astype(bool)
    # home perspective row
    home = pd.DataFrame({
        "goals": d["home_score"].astype(int),
        "elo_diff": (d["rh_pre"] - d["ra_pre"]) / 100.0,
        "is_home": (~neutral).astype(float),
        "w": d["w"],
    })
    # away perspective row
    away = pd.DataFrame({
        "goals": d["away_score"].astype(int),
        "elo_diff": (d["ra_pre"] - d["rh_pre"]) / 100.0,
        "is_home": 0.0,                      # away team never has home adv
        "w": d["w"],
    })
    return pd.concat([home, away], ignore_index=True)


def fit_poisson(train: pd.DataFrame):
    """Weighted Poisson regression -> [b0, b1, b2]."""
    y = train["goals"].values.astype(float)
    X = np.column_stack([np.ones(len(train)), train["elo_diff"].values, train["is_home"].values])
    w = train["w"].values

    def nll(beta):
        eta = X @ beta
        eta = np.clip(eta, -3, 3)
        lam = np.exp(eta)
        return -np.sum(w * (y * eta - lam))     # Poisson log-lik (drop const)

    res = minimize(nll, np.array([0.0, 0.3, 0.2]), method="BFGS")
    return res.x


def expected_goals(beta, elo_diff_per100, is_home):
    eta = beta[0] + beta[1] * elo_diff_per100 + beta[2] * is_home
    return float(np.exp(np.clip(eta, -3, 3)))


# ---- Dixon-Coles correction -------------------------------------------------
def dc_tau(i, j, lh, la, rho):
    if i == 0 and j == 0:
        return 1.0 - lh * la * rho
    if i == 0 and j == 1:
        return 1.0 + lh * rho
    if i == 1 and j == 0:
        return 1.0 + la * rho
    if i == 1 and j == 1:
        return 1.0 - rho
    return 1.0


def fit_rho(annotated: pd.DataFrame, beta, asof: pd.Timestamp):
    """MLE for the Dixon-Coles rho on modern played matches."""
    d = annotated[annotated["date"] >= MODERN_FROM].copy()
    neutral = d["neutral"].fillna(False).astype(bool)
    ed = (d["rh_pre"] - d["ra_pre"]).values / 100.0
    hs = d["home_score"].astype(int).values
    as_ = d["away_score"].astype(int).values
    home_adv = (~neutral).astype(float).values
    age_days = (asof - d["date"]).dt.days.clip(lower=0).values
    w = 0.5 ** (age_days / HALF_LIFE_DAYS)

    lh = np.exp(np.clip(beta[0] + beta[1] * ed + beta[2] * home_adv, -3, 3))
    la = np.exp(np.clip(beta[0] - beta[1] * ed, -3, 3))
    # only low-score cells are affected; restrict for speed
    mask = (hs <= 1) & (as_ <= 1)

    def nll(rho_arr):
        rho = rho_arr[0]
        tau = np.ones(len(d))
        for idx in np.where(mask)[0]:
            tau[idx] = dc_tau(hs[idx], as_[idx], lh[idx], la[idx], rho)
        tau = np.clip(tau, 1e-6, None)
        return -np.sum(w * np.log(tau))

    res = minimize(nll, np.array([-0.05]), method="Nelder-Mead")
    return float(res.x[0])


def score_matrix(lh, la, rho, maxg=10):
    """DC-corrected probability matrix P[i,j] for home=i, away=j goals."""
    i = np.arange(maxg + 1)
    ph = poisson.pmf(i, lh)
    pa = poisson.pmf(i, la)
    M = np.outer(ph, pa)
    for a in (0, 1):
        for b in (0, 1):
            M[a, b] *= dc_tau(a, b, lh, la, rho)
    return M / M.sum()


if __name__ == "__main__":
    r = pd.read_csv("data/results.csv")
    ratings, annotated = compute_elo(r)
    asof = annotated["date"].max()
    train = build_training(annotated, asof)
    beta = fit_poisson(train)
    rho = fit_rho(annotated, beta, asof)
    print("Training rows:", len(train), "| asof:", asof.date())
    print(f"Poisson beta: intercept={beta[0]:.4f}  elo_diff/100={beta[1]:.4f}  is_home={beta[2]:.4f}")
    print(f"Dixon-Coles rho: {rho:.4f}")

    # sanity: expected goals for a few matchups
    def show(h, a, neutral=True):
        rd = (ratings[h] - ratings[a]) / 100.0
        lh = expected_goals(beta, rd, 0 if neutral else 1)
        la = expected_goals(beta, -rd, 0)
        M = score_matrix(lh, la, rho)
        # win/draw/loss
        pdraw = np.trace(M)
        phome = np.tril(M, -1).sum()
        paway = np.triu(M, 1).sum()
        ml = np.unravel_index(M.argmax(), M.shape)
        print(f"{h} vs {a}: xG {lh:.2f}-{la:.2f} | P(H/D/A)={phome:.2f}/{pdraw:.2f}/{paway:.2f} "
              f"| most-likely {ml[0]}-{ml[1]}")

    print("\n=== Sanity checks (neutral venue) ===")
    show("Argentina", "Cape Verde")
    show("Brazil", "Norway")
    show("France", "Paraguay")
    show("Canada", "Morocco")
    show("Spain", "Austria")
    show("United States", "Bosnia and Herzegovina")
