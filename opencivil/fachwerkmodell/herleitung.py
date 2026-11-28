"""
opencivil/fachwerkmodell/herleitung.py -- wie ein Fachwerkmodell seine Rechnung aufschreibt.

VERANTWORTUNG:
Die Scheibe in Tabellen -- Scheiben und Löcher mit ihrer Fläche, die Lager
mit dem, was sie halten, die Lasten mit ihrer Summe --, dann das gefundene
Fachwerk: wie es gesucht wurde, je nach Verfahren, seine Stäbe mit ihren
Kräften, das Ziel V der Optimierung und was die Lager aufnehmen. Zuletzt
die Meldungen: rot, was falsch ist, sonst als Hinweis.

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
from opencivil.fachwerkmodell import form, simp, skelett, suche
from opencivil.fachwerkmodell.form import Formeinstellung
from opencivil.fachwerkmodell.modell import Umriss
from opencivil.fachwerkmodell.nachrechnung import Nachrechnung
from opencivil.fachwerkmodell.suche import ZUG_ACHSPARALLEL, Einstellung, Suchergebnis

if TYPE_CHECKING:
    from opencivil.fachwerkmodell.werk import Fachwerkbefund, Verfahrenseinstellung

#: Was das Fachwerkmodell annimmt.
ANNAHME = (
    "Ein Fachwerkmodell der Scheibe: Druckstreben und Zugglieder tragen die Lasten im "
    "Gleichgewicht zu den Lagern. Ohne Material und ohne Dicke – Fachwerk und Kräfte hängen nur "
    "von Form, Lagern und Lasten ab; bemessen wird hier nichts.")


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
        zeilen = [[f.name, als_ort(f.ort), Mathe(fest(f.F_x / 1e3, 1)), Mathe(fest(-f.F_y / 1e3, 1))]
                  for f in m.lasten]
        if len(m.lasten) > 1:
            zeilen.append(["Summe", "", Mathe(fest(math.fsum(f.F_x for f in m.lasten) / 1e3, 1)),
                           Mathe(fest(-math.fsum(f.F_y for f in m.lasten) / 1e3, 1))])
        p.tabelle(["Last", "Ort [m]", Mathe(r"F_h\ [\mathrm{kN}] \rightarrow"),
                   Mathe(r"F_v\ [\mathrm{kN}] \downarrow")], zeilen, titel="Lasten")
    if befund.gefunden is not None and befund.nachrechnung is not None:
        p.titel("Fachwerk", ebene=3)
        if isinstance(befund.einstellung, Formeinstellung):
            _aus_der_form(p, befund.gefunden, befund.einstellung)
        else:
            _gesucht(p, befund.gefunden, befund.einstellung)
        _fachwerk(p, befund.nachrechnung)
    for meldung in befund.meldungen + befund.zum_fachwerk:
        (p.warnung if meldung.fehler else p.hinweis)(meldung.text)


def _gesucht(p: Protokoll, gefunden: Suchergebnis, einstellung: Einstellung) -> None:
    """Wie die Ground Structure das Fachwerk suchte."""
    wie = (f"nach Runde {gefunden.runden} kam keiner mehr dazu" if gefunden.fertig
           else f"angehalten nach Runde {gefunden.runden}")
    zug = (f" {ZUG_ACHSPARALLEL}: ein geneigter Stab trägt nur Druck." if einstellung.zug_achsparallel
           else "")
    p.text(
        f"Gesucht nach dem Verfahren Ground Structure ({suche.QUELLE}): Knoten im Raster der Weite "
        f"h = {einstellung.weite:g} m, dazu die Punkte der Lager und Lasten und die Ecken der "
        f"Umrisse; je zwei Knoten ein möglicher Stab, wenn er ganz im Material liegt – "
        f"{gefunden.moeglich} Stäbe.{zug} Eine lineare Optimierung wählt die Kräfte im Gleichgewicht "
        f"mit dem kleinsten V; Runde um Runde kommen die Stäbe dazu, die V noch senken – "
        f"{wie}, mit {gefunden.im_modell} Stäben im Modell. {_danach(einstellung)}")
    _ziel(p)


def _aus_der_form(p: Protokoll, gefunden: Suchergebnis, einstellung: Formeinstellung) -> None:
    """Wie SIMP die Form fand und das Werkzeug aus ihr das Fachwerk las."""
    elemente = sum(z != "-" for z in gefunden.form)
    if not gefunden.fertig:
        wie = f"angehalten nach Schritt {gefunden.runden}"
    elif gefunden.runden >= form.HOECHSTENS_SCHRITTE:
        wie = f"nach {gefunden.runden} Schritten, so vielen wie höchstens"
    else:
        wie = (f"nach {gefunden.runden} Schritten änderte sich keine Dichte mehr um "
               f"{form.GENUG:g}")
    p.text(
        f"Gesucht nach dem Verfahren SIMP ({simp.QUELLE}): die Scheibe in {elemente} quadratische "
        f"Elemente der Seite h = {einstellung.weite:g} m geteilt, jedes mit einer Dichte zwischen 0 "
        f"und 1, gemittelt über die Nachbarn bis {simp.FILTER:g} h. Die Steifigkeit eines Elements "
        f"wächst mit der {simp.P:g}. Potenz seiner Dichte; so lohnt sich halbes Material nicht. "
        f"Schritt um Schritt verteilen sich {einstellung.volumen * 100:g} % der Fläche so, dass die "
        f"Scheibe unter den Lasten am steifsten ist – {wie}.")
    p.ansatz(r"c = F^{T} U \;\rightarrow\; \min \qquad K(\tilde{\rho}) \, U = F \qquad "
             r"\sum_e \tilde{\rho}_e \, A_e = \bar{\rho} \, A \qquad "
             r"E_e = E_{min} + \tilde{\rho}_e^{\,p} \left( E_0 - E_{min} \right)",
             titel="Ziel der Form", referenz=f"{simp.QUELLE}, Gl. (1), (2) und (9)",
             name="Steifste Form")
    p.text(
        f"Aus der Form liest das Werkzeug das Fachwerk ({skelett.QUELLE}): ihre Mittellinien, mit "
        f"Knoten, wo eine endet, sich verzweigt oder knickt, und an jedem Lager und jeder Last. Je "
        f"zwei Knoten sind ein möglicher Stab, wenn er ganz im Material liegt – {gefunden.moeglich} "
        f"Stäbe; einer neben der Form kostet in der Optimierung bis {skelett.NEBEN:g}-mal so viel "
        f"wie in ihr. Dieselbe lineare Optimierung wie bei der Ground Structure wählt die Kräfte "
        f"im Gleichgewicht mit dem kleinsten V. {_danach(einstellung)}")
    _ziel(p)


def _danach(einstellung: "Verfahrenseinstellung") -> str:
    """Was nach der Optimierung mit dem Fachwerk geschieht -- in beiden Verfahren gleich."""
    return (f"Danach fallen die Stäbe unter {einstellung.N_min * 100:g} % der grössten Kraft weg, "
            f"und das Gleichgewicht wird ohne sie neu gesucht; zwei Stäbe in einer Flucht durch "
            f"einen Knoten ohne Last und Lager werden einer.")


def _ziel(p: Protokoll) -> None:
    """Was die Optimierung der Kräfte klein macht -- in beiden Verfahren dasselbe."""
    p.ansatz(r"V = \sum_i l_i \, \left( w_Z \, N_i^{+} + w_D \, N_i^{-} \right) "
             r"\;\rightarrow\; \min", titel="Ziel der Optimierung", referenz=suche.QUELLE,
             name="Leichtestes Fachwerk")


def _fachwerk(p: Protokoll, n: Nachrechnung) -> None:
    """Die Stäbe des Fachwerks, sein V und die Kräfte der Lager."""
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
