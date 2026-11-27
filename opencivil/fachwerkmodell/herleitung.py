"""
opencivil/fachwerkmodell/herleitung.py -- wie ein Fachwerkmodell seine Rechnung aufschreibt.

VERANTWORTUNG:
Die Scheibe in Tabellen -- Scheiben und Löcher mit ihrer Fläche, die Lager
mit dem, was sie halten, die Lasten mit ihrer Summe --, dann die
Meldungen: rot, was falsch ist, sonst als Hinweis.

EINHEITEN:
Orte in m, Flächen in m², Kräfte in kN: ``F_h`` nach rechts, ``F_v`` nach
unten positiv, wie in der Maske.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Sequence

from opencivil.core.latex import Mathe, fest
from opencivil.core.protokoll import Protokoll
from opencivil.decke import geometrie as geo
from opencivil.decke.herleitung import als_ort
from opencivil.fachwerkmodell.modell import Umriss

if TYPE_CHECKING:
    from opencivil.fachwerkmodell.werk import Fachwerkbefund

#: Was das Fachwerkmodell annimmt.
ANNAHME = (
    "Ein Fachwerkmodell der Scheibe: Druckstreben und Zugglieder tragen die Lasten im "
    "Gleichgewicht zu den Lagern. Ohne Material und ohne Dicke – Fachwerk und Kräfte hängen nur "
    "von Form, Lagern und Lasten ab; bemessen wird hier nichts.")

#: kN je N.
KN = 1e-3


def schreiben(p: Protokoll, befund: "Fachwerkbefund") -> None:
    """Die ganze Herleitung -- nichts davon geht in den Befund ein, also still gar keine."""
    if p.still:
        return
    p.annahme(ANNAHME)
    m = befund.modell
    _umrisse(p, m.scheiben, "Scheibe", "Scheiben")
    _umrisse(p, m.loecher, "Loch", "Löcher")
    if m.lager:
        p.tabelle(["Lager", "Ort [m]", "hält"],
                  [[l.name, als_ort(l.ort), l.halt.beschriftung] for l in m.lager], titel="Lager")
    if m.lasten:
        zeilen = [[f.name, als_ort(f.ort), Mathe(fest(f.F_x * KN, 1)), Mathe(fest(-f.F_y * KN, 1))]
                  for f in m.lasten]
        if len(m.lasten) > 1:
            zeilen.append(["Summe", "", Mathe(fest(math.fsum(f.F_x for f in m.lasten) * KN, 1)),
                           Mathe(fest(-math.fsum(f.F_y for f in m.lasten) * KN, 1))])
        p.tabelle(["Last", "Ort [m]", Mathe(r"F_h\ [\mathrm{kN}] \rightarrow"),
                   Mathe(r"F_v\ [\mathrm{kN}] \downarrow")], zeilen, titel="Lasten")
    for meldung in befund.meldungen:
        (p.warnung if meldung.fehler else p.hinweis)(meldung.text)


def _umrisse(p: Protokoll, umrisse: Sequence[Umriss], was: str, titel: str) -> None:
    if umrisse:
        p.tabelle([was, "Ecken", Mathe(r"A\ [\mathrm{m}^{2}]")],
                  [[u.name, Mathe(str(len(u.ecken))), Mathe(fest(abs(geo.flaeche(u.ecken)), 2))]
                   for u in umrisse], titel=titel)
