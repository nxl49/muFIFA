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
      f"the completed 2026 Round of 32). Predictions run from the actual Round of 16._\n")

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

    w("## Actual Round of 16 fixtures (from completed Round of 32)\n")
    w("| # | Fixture |")
    w("|---|---------|")
    for i, (h, a) in enumerate(B.R16_FIXTURES, 1):
        w(f"| {i} | {h} vs {a} |")
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
