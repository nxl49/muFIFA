"""Generate output/model_report.md: ratings, model params, title odds, and the
predicted bracket with advance probabilities. Transparency companion to the CSV."""
import numpy as np
import pandas as pd
from simulate import Predictor
import bracket as B


def main():
    P = Predictor()
    lines = []
    w = lines.append

    w("# 2026 World Cup Knockout Model - Report\n")
    w(f"_Model as-of date: {P.asof.date()} (ratings include all matches through "
      f"the 2026 group stage + 7 completed Round-of-32 games)._\n")

    w("## Fitted model parameters\n")
    w("```")
    w(f"Poisson goals:  log(lambda) = {P.beta[0]:.4f} + {P.beta[1]:.4f}*(EloDiff/100) "
      f"+ {P.beta[2]:.4f}*is_home")
    w(f"Dixon-Coles rho = {P.rho:.4f}")
    w("Backtest (train 2002-2022, test 2023-2026, 3674 matches):")
    w("   W/D/L accuracy 60.7%   log-loss 0.866 vs 1.054 base-rate (-17.8%)")
    w("```\n")

    top = sorted(P.ratings.items(), key=lambda x: -x[1])[:20]
    w("## Current Elo ratings (top 20)\n")
    w("| # | Team | Elo |")
    w("|---|------|-----|")
    for i, (t, v) in enumerate(top, 1):
        w(f"| {i} | {t} | {v:.0f} |")
    w("")

    w("## Locked Round-of-32 results (actual, through June 30 2026)\n")
    locked = [(m, *B.R32[m][:2], B.R32[m][2]) for m in B.R32 if B.R32[m][2]]
    w("| Match | Winner |")
    w("|-------|--------|")
    for _, h, a, win in locked:
        w(f"| {h} vs {a} | **{win}** |")
    w("")

    w("## Predicted pending Round-of-32 (sets the R16 field)\n")
    w("| Fixture | Score | Winner | Win prob |")
    w("|---------|-------|--------|----------|")
    for mid in range(8, 17):
        h, a, _ = B.R32[mid]
        pr = P.predict_match(h, a, "R32")
        w(f"| {h} vs {a} | {pr['home_score']}-{pr['away_score']} | "
          f"{pr['winner']} | {pr['p_home_adv']:.0%} home |")
    w("")

    w("## Predicted bracket (Round of 16 -> Final)\n")
    w("| Stage | Home | Score | Away | Winner | P(home adv) |")
    w("|-------|------|-------|------|--------|-------------|")
    for fx in P.deterministic_bracket():
        w(f"| {fx['slot']} | {fx['home']} | {fx['home_score']}-{fx['away_score']} | "
          f"{fx['away']} | **{fx['winner']}** | {fx['p_home_adv']:.0%} |")
    w("")

    w("## Monte-Carlo tournament simulation (50,000 runs)\n")
    champ, finalist, last4 = P.monte_carlo(50000)
    w("| Team | Champion | Reaches Final | Reaches SF |")
    w("|------|----------|---------------|------------|")
    for t, p in list(champ.items())[:14]:
        w(f"| {t} | {p:.1%} | {finalist.get(t,0):.1%} | {last4.get(t,0):.1%} |")
    w("")

    txt = "\n".join(lines)
    with open("output/model_report.md", "w") as f:
        f.write(txt)
    print("Wrote output/model_report.md")
    print(txt)


if __name__ == "__main__":
    main()
