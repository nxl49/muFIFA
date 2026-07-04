"""
2026 World Cup knockout bracket — from the Round of 16 onward.

The Round of 32 is complete, so the Round of 16 is now an actual, fixed set of
fixtures (taken from the official schedule / results dataset, home team first).
The quarterfinal/semifinal/final tree is the official bracket structure, verified
against Wikipedia and Sky Sports:

    QF1 = W(R16-1) vs W(R16-2)      QF3 = W(R16-5) vs W(R16-6)
    QF2 = W(R16-3) vs W(R16-4)      QF4 = W(R16-7) vs W(R16-8)
    SF1 = W(QF1) vs W(QF2)          SF2 = W(QF3) vs W(QF4)
    Final = W(SF1) vs W(SF2)        3rd  = L(SF1) vs L(SF2)

For the record, the actual Round-of-32 winners that produced this R16 were:
    Canada, Brazil, Paraguay, Morocco, Norway, France, Mexico, England,
    Belgium, United States, Spain, Portugal, Switzerland, Argentina, Colombia, Egypt.
"""

# Actual Round of 16 fixtures (home_team, away_team), in official match_id order.
R16_FIXTURES = [
    ("Canada", "Morocco"),          # R16_001  @ Houston
    ("Paraguay", "France"),         # R16_002  @ Philadelphia
    ("Brazil", "Norway"),           # R16_003  @ East Rutherford
    ("Mexico", "England"),          # R16_004  @ Mexico City  (Mexico host)
    ("Portugal", "Spain"),          # R16_005  @ Dallas
    ("United States", "Belgium"),   # R16_006  @ Seattle       (USA host)
    ("Argentina", "Egypt"),         # R16_007  @ Atlanta
    ("Switzerland", "Colombia"),    # R16_008  @ Vancouver
]

# Bracket tree: 0-based indices into the round below.
QF_PAIRS   = [(0, 1), (2, 3), (4, 5), (6, 7)]   # each QF = winners of these two R16 fixtures
SF_PAIRS   = [(0, 1), (2, 3)]                    # each SF = winners of these two QFs
FINAL_PAIR = (0, 1)                              # final    = winners of the two SFs
THIRD_PAIR = (0, 1)                              # 3rd place = losers of the two SFs

# slot -> official template match_id
MATCH_IDS = {
    "R16-0": "R16_001", "R16-1": "R16_002", "R16-2": "R16_003", "R16-3": "R16_004",
    "R16-4": "R16_005", "R16-5": "R16_006", "R16-6": "R16_007", "R16-7": "R16_008",
    "QF-0": "QF_001", "QF-1": "QF_002", "QF-2": "QF_003", "QF-3": "QF_004",
    "SF-0": "SF_001", "SF-1": "SF_002", "Third": "TP_001", "Final": "F_001",
}
STAGE_LABEL = {"R16": "Round of 16", "QF": "Quarter Final", "SF": "Semi Final",
               "Third": "Third Place Play-off", "Final": "Final"}


def host_adv(team: str, rnd: str) -> float:
    """Home-support boost for host nations playing in their own country.
    Verified against actual venues: USA home in every knockout match (all in the
    USA); Mexico home in the R16 (Mexico City); all other fixtures neutral."""
    if team == "United States":
        return 1.0
    if team == "Mexico" and rnd == "R16":
        return 1.0
    return 0.0
