"""
opencivil/decke/herleitung.py -- wie eine Decke ihre Rechnung aufschreibt.

VERANTWORTUNG:
Die Herleitung der Streifenmethode, so dass man sie von Hand nachvollziehen
kann: die Decke in Tabellen -- Platten, Linienlager, Stützen, Unterzüge --,
die Streifen je Richtung, in welcher Reihenfolge die Träger rechnen, wie die
Last auf die Richtungen geht, und die Meldungen.

EINHEITEN:
Längen in m, Dicken und Stützen in mm, Winkel in Grad gegen x, E in N/mm²,
Gewichte in kN/m².
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Optional

from opencivil.core.latex import Mathe, fest
from opencivil.core.protokoll import Protokoll
from opencivil.decke import geometrie as geo
from opencivil.decke.modell import Aufteilung, Decke
from opencivil.decke.rechnung import Ergebnis
from opencivil.decke.streifen import richtungen_der_platte

if TYPE_CHECKING:
    from opencivil.decke.werk import Deckenbefund, Deckensystem

#: Was die Streifenmethode annimmt -- die Steifigkeit nach Vorgabe, nicht nachgeschlagen.
ANNAHME = (
    "Streifenmethode (Stahlbeton II, 7.2 Platten, Folien 27 bis 39): jede Last geht in Streifen "
    "zweier Richtungen zu den Lagern, ohne Drillmomente – eine Gleichgewichtslösung und damit ein "
    "unterer Grenzwert der Traglast. Statisch unbestimmte Streifen sind elastisch gelöst, mit "
    "E_cm · h³/12 je Meter der ungerissenen Platte (nach Vorgabe, nicht nachgeschlagen); ein "
    "Unterzug trägt als Flächenlager mit gleichmässiger Pressung über seine Breite (Folie 33).")

#: Die automatische Aufteilung in Worten -- die Regel steht in :mod:`~opencivil.decke.aufteilung`.
AUTOMATISCH = (
    "Automatisch, nach Folie 31 verallgemeinert: je Zelle zweier Feldstreifen trägt die Richtung, "
    "die Lager hat. Tragen beide, geht die Last zum nahen Rand, wenn sie näher als ein Viertel der "
    "kürzeren Spannweite an einem Lager liegt, sonst in die kürzere Spannweite; nahe zweier "
    "Ränder und bei gleicher Spannweite je zur Hälfte. Ein Kragarm zählt doppelt (nach Vorgabe, "
    "nicht nachgeschlagen).")


def schreiben(p: Protokoll, system: "Deckensystem", befund: "Deckenbefund") -> None:
    """Die ganze Herleitung einer Decke."""
    p.annahme(ANNAHME)
    _platten(p, system, befund.gerechnet)
    _lager(p, befund.gerechnet, befund.ergebnis)
    for m in befund.meldungen:
        (p.warnung if m.fehler else p.hinweis)(m.text)
    e = befund.ergebnis
    if e is None or e.aufteilungen is None:
        return
    _streifen(p, e)
    _aufteilung(p, befund.gerechnet)


def _ort(p) -> str:
    return f"({fest(p[0], 2)}, {fest(p[1], 2)})"


def _platten(p: Protokoll, system: "Deckensystem", decke: Decke) -> None:
    zeilen = []
    for platte in decke.platten:
        beton = system.betone.get(platte.name)
        r1, r2 = (math.degrees(w) for w in platte.richtungen)
        zeilen.append([
            platte.name, Mathe(fest(abs(geo.flaeche(list(platte.ecken))), 2)),
            Mathe(fest(platte.h * 1e3, 0)), beton.name if beton is not None else "–",
            Mathe(fest(platte.E / 1e6, 0)) if platte.E else "–",
            Mathe(fest(platte.wichte * platte.h / 1e3, 2)) if platte.wichte else "–",
            Mathe(f"{fest(r1, 1)},\\ {fest(r2, 1)}"),
        ])
    if zeilen:
        p.tabelle(["Platte", Mathe(r"A\ [\mathrm{m}^{2}]"), Mathe(r"h\ [\mathrm{mm}]"), "Beton",
                   Mathe(r"E_{cm}\ [\mathrm{N/mm}^{2}]"), Mathe(r"g_k\ [\mathrm{kN/m}^{2}]"),
                   Mathe(r"\varphi_1,\ \varphi_2\ [°]")], zeilen, titel="Platten")
        p.text("Das Eigengewicht je m² ist ρ · g · h, mit der Dichte des Stahlbetons und "
               "g = 10 m/s².")


def _lager(p: Protokoll, decke: Decke, e: Optional[Ergebnis]) -> None:
    ja = {True: "ja", False: "nein"}
    if decke.linienlager:
        p.tabelle(["Linienlager", "von", "bis", Mathe(r"L\ [\mathrm{m}]"), "vertikal", "eingespannt"],
                  [[l.name, _ort(l.a), _ort(l.b), Mathe(fest(math.dist(l.a, l.b), 2)),
                    ja[l.vertikal], ja[l.eingespannt]] for l in decke.linienlager],
                  titel="Linienlager")
    if decke.stuetzen:
        bereiche = e.zerlegung.stuetzenbereiche if e is not None and e.zerlegung else {}
        zeilen = []
        for s in decke.stuetzen:
            bereich = bereiche.get(s.name)
            if bereich:
                lx = geo.bereich(bereich, (1.0, 0.0))
                ly = geo.bereich(bereich, (0.0, 1.0))
                masse = f"{fest(lx[1] - lx[0], 2)} × {fest(ly[1] - ly[0], 2)}"
            else:
                masse = "–"
            zeilen.append([s.name, _ort(s.ort), f"{fest(s.bx * 1e3, 0)} × {fest(s.by * 1e3, 0)}",
                           masse, "von Hand" if s.lx is not None else "von selbst"])
        p.tabelle(["Stütze", "Ort", Mathe(r"b_x \times b_y\ [\mathrm{mm}]"),
                   Mathe(r"l_x \times l_y\ [\mathrm{m}]"), "Stützenbereich"], zeilen, titel="Stützen")
    if decke.unterzuege:
        p.tabelle(["Unterzug", "von", "bis", Mathe(r"b\ [\mathrm{m}]"), "Stufe"],
                  [[u.name, _ort(u.a), _ort(u.b), Mathe(fest(u.breite, 2)), str(u.stufe)]
                   for u in decke.unterzuege], titel="Versteckte Unterzüge")


def _streifen(p: Protokoll, e: Ergebnis) -> None:
    z = e.zerlegung
    zeilen = []
    for r in z.richtungen:
        feld = z.feldstreifen(r)
        if not feld:
            continue
        breiten = [s.breite for s in feld]
        zeilen.append([r.name, Mathe(fest(math.degrees(r.winkel), 1)), str(len(feld)),
                       Mathe(f"{fest(min(breiten), 3)} \\ldots {fest(max(breiten), 3)}"),
                       f"{feld[0].name} … {feld[-1].name}"])
    p.tabelle(["Richtung", Mathe(r"\varphi\ [°]"), "Feldstreifen", Mathe(r"b\ [\mathrm{m}]"), "Namen"],
              zeilen, titel="Streifen")
    p.text(f"Je Richtung sind die Streifen höchstens {fest(e.decke.streifenbreite, 2)} m breit; "
           "geteilt wird an jeder Ecke einer Platte, jedem Rand eines Unterzugs und Stützenbereichs "
           "und jedem Ende eines Linienlagers.")
    if z.unterzuege:
        reihe = [f"{u.name} (Stufe {u.stufe})" for u in sorted(z.unterzuege, key=lambda s: s.stufe)]
        p.text("Gerechnet wird von unten nach oben: zuerst die Feldstreifen, dann die Unterzüge, "
               "jeder nach denen tieferer Stufe: " + ", ".join(reihe) + ". Was ein Träger an "
               "Lagerkraft abgibt, ist die Last dessen, auf dem er liegt.")


def _aufteilung(p: Protokoll, decke: Decke) -> None:
    if decke.aufteilung is Aufteilung.FEST:
        p.text(f"Aufteilung fest: {fest(decke.anteil * 100.0, 0)} % der Last in Richtung 1, "
               f"{fest((1.0 - decke.anteil) * 100.0, 0)} % in Richtung 2.")
    else:
        p.text(AUTOMATISCH)
    if decke.zonen:
        p.tabelle(["Zone", Mathe(r"A\ [\mathrm{m}^{2}]"), "in Richtung 1", "in Richtung 2"],
                  [[zone.name, Mathe(fest(abs(geo.flaeche(list(zone.ecken))), 2)),
                    f"{fest(zone.anteil * 100.0, 0)} %", f"{fest((1.0 - zone.anteil) * 100.0, 0)} %"]
                   for zone in decke.zonen], titel="Zonen – sie gehen der Aufteilung vor")
    richtungen = {richtungen_der_platte(pl)[0].name + " / " + richtungen_der_platte(pl)[1].name
                  for pl in decke.platten}
    if len(richtungen) > 1:
        p.text("Die Platten tragen in verschiedenen Richtungen: "
               + "; ".join(sorted(richtungen)) + ". Die Aufteilung gilt je Platte in ihren zwei Richtungen.")
