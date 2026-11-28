"""
opencivil/fachwerkmodell/herleitung.py -- wie ein Fachwerkmodell seine Rechnung aufschreibt.

VERANTWORTUNG:
Die Scheibe in Tabellen -- Scheiben und Löcher mit ihrer Fläche, die Lager
mit dem, was sie halten, die Lasten mit ihrer Summe --, dann das gefundene
Fachwerk: wie es gesucht wurde, seine Stäbe mit ihren Kräften, das Ziel V
der Optimierung und was die Lager aufnehmen. Zuletzt die Meldungen: rot,
was falsch ist, sonst als Hinweis.

EINHEITEN:
Orte in m, Flächen in m², Kräfte in kN: ``F_h`` nach rechts, ``F_v`` nach
unten positiv, wie in der Maske; eine Stabkraft ``N`` mit Zug positiv.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Sequence

from opencivil.core.latex import Mathe, fest
from opencivil.core.protokoll import Protokoll
from opencivil.decke import geometrie as geo
from opencivil.decke.herleitung import als_ort
from opencivil.fachwerkmodell.modell import Umriss
from opencivil.fachwerkmodell.nachrechnung import Nachrechnung
from opencivil.fachwerkmodell.suche import QUELLE, ZUG_ACHSPARALLEL, Einstellung, Suchergebnis

if TYPE_CHECKING:
    from opencivil.fachwerkmodell.werk import Fachwerkbefund

#: Was das Fachwerkmodell annimmt.
ANNAHME = (
    "Ein Fachwerkmodell der Scheibe: Druckstreben und Zugglieder tragen die Lasten im "
    "Gleichgewicht zu den Lagern. Ohne Material und ohne Dicke – Fachwerk und Kräfte hängen nur "
    "von Form, Lagern und Lasten ab; bemessen wird hier nichts.")


def schreiben(p: Protokoll, befund: "Fachwerkbefund", einstellung: Einstellung) -> None:
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
        zeilen = [[f.name, als_ort(f.ort), Mathe(fest(f.F_x / 1e3, 1)), Mathe(fest(-f.F_y / 1e3, 1))]
                  for f in m.lasten]
        if len(m.lasten) > 1:
            zeilen.append(["Summe", "", Mathe(fest(math.fsum(f.F_x for f in m.lasten) / 1e3, 1)),
                           Mathe(fest(-math.fsum(f.F_y for f in m.lasten) / 1e3, 1))])
        p.tabelle(["Last", "Ort [m]", Mathe(r"F_h\ [\mathrm{kN}] \rightarrow"),
                   Mathe(r"F_v\ [\mathrm{kN}] \downarrow")], zeilen, titel="Lasten")
    if befund.gefunden is not None and befund.nachrechnung is not None:
        _fachwerk(p, befund.gefunden, befund.nachrechnung, einstellung)
    for meldung in befund.meldungen + befund.zum_fachwerk:
        (p.warnung if meldung.fehler else p.hinweis)(meldung.text)


def _fachwerk(p: Protokoll, gefunden: Suchergebnis, n: Nachrechnung,
              einstellung: Einstellung) -> None:
    """Wie das Fachwerk gesucht wurde, seine Stäbe, sein V und die Kräfte der Lager."""
    p.titel("Fachwerk", ebene=3)
    wie = (f"nach Runde {gefunden.runden} kam keiner mehr dazu" if gefunden.fertig
           else f"angehalten nach Runde {gefunden.runden}")
    zug = (f" {ZUG_ACHSPARALLEL}: ein geneigter Stab trägt nur Druck." if einstellung.zug_achsparallel
           else "")
    p.text(
        f"Gesucht nach dem Verfahren Ground Structure ({QUELLE}): Knoten im Raster der Weite "
        f"h = {einstellung.weite:g} m, dazu die Punkte der Lager und Lasten und die Ecken der "
        f"Umrisse; je zwei Knoten ein möglicher Stab, wenn er ganz im Material liegt – "
        f"{gefunden.moeglich} Stäbe.{zug} Eine lineare Optimierung wählt die Kräfte im Gleichgewicht "
        f"mit dem kleinsten V; Runde um Runde kommen die Stäbe dazu, die V noch senken – "
        f"{wie}, mit {gefunden.im_modell} Stäben im Modell. Danach fallen die Stäbe unter "
        f"{einstellung.N_min * 100:g} % der grössten Kraft weg, und das Gleichgewicht wird ohne "
        f"sie neu gesucht; zwei Stäbe in einer Flucht durch einen Knoten ohne Last und Lager "
        f"werden einer.")
    p.ansatz(r"V = \sum_i l_i \, \left( w_Z \, N_i^{+} + w_D \, N_i^{-} \right) "
             r"\;\rightarrow\; \min", titel="Ziel der Optimierung", referenz=QUELLE,
             name="Leichtestes Fachwerk")
    fw = n.fachwerk
    if not fw.staebe:
        p.text("Kein Stab trägt: die Lasten lassen sich so nicht zu den Lagern tragen – welche "
               "offen bleiben, sagen die Meldungen.")
        return
    zeilen = [[Mathe(str(i)), als_ort(fw.knoten[a]), als_ort(fw.knoten[b]), Mathe(fest(l, 2)),
               Mathe(fest(N / 1e3, 1)), "Zug" if N > 0 else "Druck"]
              for i, ((a, b, N), l) in enumerate(zip(fw.staebe, n.laengen), start=1)]
    p.tabelle(["Stab", "von [m]", "bis [m]", Mathe(r"l\ [\mathrm{m}]"),
               Mathe(r"N\ [\mathrm{kN}]"), ""],
              zeilen, titel=f"Stäbe – {len(zeilen)}, nach der Grösse ihrer Kraft")
    p.gleichung(rf"V = {fest(n.V / 1e3, 1)}\ \mathrm{{kNm}} \qquad w_Z = {fest(n.w_Z, 2)},\ w_D = 1",
                titel="Ziel des Fachwerks")
    if n.lagerkraefte:
        p.tabelle(["Lager", "Ort [m]", Mathe(r"R_x\ [\mathrm{kN}] \rightarrow"),
                   Mathe(r"R_y\ [\mathrm{kN}] \uparrow")],
                  [[k.lager.name, als_ort(k.lager.ort), Mathe(fest(k.R_x / 1e3, 1)),
                    Mathe(fest(k.R_y / 1e3, 1))] for k in n.lagerkraefte], titel="Lagerkräfte")
    if n.im_gleichgewicht:
        p.text("Nachgerechnet: an jedem Knoten heben sich Stabkräfte, Lasten und Lagerkräfte auf.")


def _umrisse(p: Protokoll, umrisse: Sequence[Umriss], was: str, titel: str) -> None:
    if umrisse:
        p.tabelle([was, "Ecken", Mathe(r"A\ [\mathrm{m}^{2}]")],
                  [[u.name, Mathe(str(len(u.ecken))), Mathe(fest(abs(geo.flaeche(u.ecken)), 2))]
                   for u in umrisse], titel=titel)
