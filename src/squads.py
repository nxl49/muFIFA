"""
2026 World Cup jersey numbers for the primary goal threats of every team that
appears as a scorer in the predicted bracket. Numbers verified from official /
press squad-number releases (England FA, RFEF, FFF, US Soccer, and reporting
on the Argentina / Brazil / Morocco / Colombia number reveals), June 2026.

Only the realistic goalscorers per team are listed - enough to map the
data-driven scorer ranking (from goalscorers.csv) onto shirt numbers.
"""

SQUAD_NUMBERS = {
    "Argentina":     {"Lionel Messi": 10, "Lautaro Martínez": 22, "Julián Álvarez": 9},
    "France":        {"Kylian Mbappé": 10, "Ousmane Dembélé": 7, "Randal Kolo Muani": 12},
    "Brazil":        {"Vinícius Júnior": 7, "Raphinha": 11, "Neymar": 10, "Matheus Cunha": 19},
    "Spain":         {"Mikel Oyarzabal": 21, "Ferran Torres": 7, "Lamine Yamal": 19,
                      "Mikel Merino": 6, "Dani Olmo": 10, "Gavi": 9},
    "England":       {"Harry Kane": 9, "Jude Bellingham": 10, "Bukayo Saka": 7},
    "Morocco":       {"Ayoub El Kaabi": 20, "Brahim Díaz": 10, "Achraf Hakimi": 2},
    "United States": {"Christian Pulisic": 10, "Weston McKennie": 8},
    "Colombia":      {"Luis Díaz": 7, "James Rodríguez": 10, "Jhon Córdoba": 9},
}

# Accent / spelling variants that appear in goalscorers.csv -> canonical name.
NAME_ALIASES = {
    "Julián Alvarez": "Julián Álvarez",
    "Vinicius Júnior": "Vinícius Júnior",
    "Vinicius Junior": "Vinícius Júnior",
}


def canonical(name: str) -> str:
    return NAME_ALIASES.get(name, name)
