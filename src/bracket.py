"""
2026 World Cup knockout bracket definition.

Adjacency confirmed from the official bracket (Wikipedia knockout-stage page),
cross-validated against the one R16 fixture already scheduled in the results
dataset: Canada vs Morocco = Winner(South Africa/Canada) vs Winner(Netherlands/
Morocco). "home" side = the first-listed feeder (bracket convention).

R32 winners locked from actual results through June 30, 2026 (7 of 16):
  Canada, Brazil, Paraguay, Morocco, Norway, France, Mexico.
The other 9 R32 matches are predicted by the model.
"""

# Round of 32: id -> (home_team, away_team, locked_winner or None)
R32 = {
    1:  ("South Africa", "Canada", "Canada"),
    2:  ("Netherlands", "Morocco", "Morocco"),
    3:  ("France", "Sweden", "France"),
    4:  ("Germany", "Paraguay", "Paraguay"),
    5:  ("Ivory Coast", "Norway", "Norway"),
    6:  ("Brazil", "Japan", "Brazil"),
    7:  ("Mexico", "Ecuador", "Mexico"),
    8:  ("England", "DR Congo", None),
    9:  ("Belgium", "Senegal", None),
    10: ("United States", "Bosnia and Herzegovina", None),
    11: ("Switzerland", "Algeria", None),
    12: ("Spain", "Austria", None),
    13: ("Portugal", "Croatia", None),
    14: ("Argentina", "Cape Verde", None),
    15: ("Colombia", "Ghana", None),
    16: ("Australia", "Egypt", None),
}

# Round of 16: id -> (home_feeder_R32, away_feeder_R32)
R16 = {
    "A": (1, 2),    # W(SA/Canada)      vs W(Neth/Morocco)   -> Canada vs Morocco (anchor)
    "B": (3, 4),    # W(France/Sweden)  vs W(Germany/Paraguay)
    "C": (5, 6),    # W(IvCoast/Norway) vs W(Brazil/Japan)
    "D": (7, 8),    # W(Mexico/Ecuador) vs W(England/DRCongo)
    "E": (9, 10),   # W(Belgium/Senegal) vs W(USA/Bosnia)
    "F": (11, 12),  # W(Switz/Algeria)  vs W(Spain/Austria)
    "G": (13, 14),  # W(Portugal/Croatia) vs W(Argentina/CapeVerde)
    "H": (15, 16),  # W(Colombia/Ghana) vs W(Australia/Egypt)
}

# Quarterfinals: id -> (home_feeder_R16, away_feeder_R16)
QF = {
    1: ("A", "B"),
    2: ("D", "C"),
    3: ("E", "F"),
    4: ("G", "H"),
}

# Semifinals: id -> (home_feeder_QF, away_feeder_QF)
SF = {
    1: (1, 2),
    2: (3, 4),
}

# Final: (home_feeder_SF, away_feeder_SF)
FINAL = (1, 2)

# Third-place play-off: the two beaten semifinalists (losers of SF1 / SF2).
THIRD_PLACE = (1, 2)

# Official template match_id order (mufifa26_template.csv).
MATCH_IDS = {
    "R16-A": "R16_001", "R16-B": "R16_002", "R16-C": "R16_003", "R16-D": "R16_004",
    "R16-E": "R16_005", "R16-F": "R16_006", "R16-G": "R16_007", "R16-H": "R16_008",
    "QF1": "QF_001", "QF2": "QF_002", "QF3": "QF_003", "QF4": "QF_004",
    "SF1": "SF_001", "SF2": "SF_002", "Third": "TP_001", "Final": "F_001",
}

STAGE_LABEL = {"R16": "Round of 16", "QF": "Quarter Final", "SF": "Semi Final",
               "Third": "Third Place Play-off", "Final": "Final"}


def host_adv(team: str, rnd: str) -> float:
    """Home-support boost for host nations playing in their own country.

    2026 venue plan: QF/SF/Final all in the USA. Assumptions:
      - USA: boosted in every knockout match (all played in the USA).
      - Mexico: boosted in R32/R16 (games in Mexico), neutral once rounds move
        to the USA.
      - Canada: neutral in the knockouts (their R16 is in Houston, USA).
    """
    if team == "United States":
        return 1.0
    if team == "Mexico" and rnd in ("R32", "R16"):
        return 1.0
    return 0.0
