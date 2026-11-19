"""
opencivil/stabwerk3d/herleitung.py -- wie ein 3D-Balkensystem seine Rechnung aufschreibt.

VERANTWORTUNG:
Wie in der Ebene (:mod:`opencivil.stabwerk.herleitung`), im Raum: das
System in Tabellen, die Ansaetze -- der Stab als drei ebene, seine Achsen,
Bettung, arbeitsgleiche Lasten, Gleichungssystem --, die Matrizen mit
Zahlen, solange sie klein genug sind, und je Lastfall und Kombination die
Verschiebungen der Knoten, die Schnittgroessen an den Stabenden, die
Lagerkraefte, die Extremwerte und die Gleichgewichtsprobe. Was die Ebene
schon schreibt -- Zahlen und Matrizen, Unbekannte, den Kopf eines Falls,
Lagerkraefte, Extremwerte, die Probe --, kommt von dort, mit den Groessen
des Raums.

WIE VIEL MIT ZAHLEN:
Die Gesamtmatrix wie in der Ebene; die Matrix eines Stabs, 12 × 12, nur
bis :data:`STAEBE_MIT_MATRIX` Teilstaebe.

EINHEITEN:
Wie in der Ebene: Laengen in m, Verschiebungen in mm, Drehungen in mrad,
Kraefte in kN, Momente in kNm, in den Matrizen kN und m. Die
Schnittgroessen in den Achsen des Stabs (:mod:`~opencivil.stabwerk.verlauf`).
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from opencivil.core.latex import Mathe, fest, text_latex
from opencivil.core.protokoll import Protokoll
from opencivil.stabwerk import herleitung as eben
from opencivil.stabwerk import stab as st
from opencivil.stabwerk.system import UNBESTIMMT, Fall
from opencivil.stabwerk.stabquerschnitt import KOPPLUNG
from opencivil.stabwerk.verlauf import SCHNITTGROESSEN
from opencivil.stabwerk3d import stab as st3
from opencivil.stabwerk3d.modell import Stablast, System
from opencivil.stabwerk3d.raum import ACHSEN, betrag, minus, punkt, skalar

if TYPE_CHECKING:
    from opencivil.stabwerk.rechnung import Systembefund
    from opencivil.stabwerk3d.rechnung import Balkensystem3d

#: Bis zu so vielen Teilstaeben steht die Matrix jedes einzelnen mit Zahlen da.
STAEBE_MIT_MATRIX = 2

#: Was die Steifigkeit und das Gleichgewicht annehmen.
ANNAHME = ("Steifigkeit: E_cm und G_cm des Betons, E_a und G_a des Baustahls oder E und G "
           "eines eigenen Materials, am ungerissenen Querschnitt ohne Bewehrung und ohne "
           "Schubverformung. Bei einem Querschnitt aus einer Platte oder Querschnittsanalyse "
           "wahlweise sein E_eq bei N und M, eine Sekantensteifigkeit (SIA 262:2025, "
           "4.1.4.1.2): es gilt für EA, EI_y und EI_z, die Torsion behält G_cm. y und z gelten "
           "als Hauptachsen des Querschnitts; das Deviationsmoment einer Querschnittsanalyse "
           f"bleibt aussen vor, ab {100 * KOPPLUNG:.0f} % von min(I_y; I_z) mit einem "
           "Hinweis (beides nach Vorgabe, nicht nachgeschlagen). Die Torsion "
           "nach St. Venant, ohne Wölbkrafttorsion und ohne den "
           "Abstand von Schubmittelpunkt und Schwerpunkt (nach Vorgabe, nicht nachgeschlagen). "
           "Beim Beton ungerissen auch die Torsion: Abminderungen für Risse und Kriechen "
           "lässt die Norm zu, sie können aber günstig oder ungünstig wirken (SIA 262:2025, "
           "4.1.4.1.3). Gleichgewicht am unverformten System (Theorie 1. Ordnung): das gilt, "
           "solange die Wirkungen 2. Ordnung klein bleiben (4.1.3.2.2); Kippen und Knicken "
           "sind nachzuweisen.")

#: Was die Durchbiegungen f_y und f_z sind -- und was sie nicht sind.
DURCHBIEGUNG = ("Die Durchbiegungen f_y und f_z misst jeder Stab gegen die Gerade zwischen "
                "seinen Enden, in y und z seiner Achsen. Die Norm misst gegenüber den "
                "Auflagern (SIA 262:2025, 4.4.3.1.1): dasselbe nur, wo ein Stab von Auflager zu "
                "Auflager reicht. Und sie gelten kurzzeitig am ungerissenen Querschnitt; Risse "
                "und Kriechen fehlen.")

#: Die Vorzeichen der Schnittgroessen, in den Achsen des Stabs.
SCHNITTGROESSEN_LATEX = (
    r"\sigma = \frac{N}{A} + \frac{M_y \cdot z}{I_y} + \frac{M_z \cdot y}{I_z} \qquad "
    r"V_z = \frac{\mathrm{d}M_y}{\mathrm{d}x} \qquad V_y = \frac{\mathrm{d}M_z}{\mathrm{d}x}"
)

#: Die Biegelinien, die Laengsverschiebung und die Verdrillung.
BIEGELINIE_LATEX = (
    r"w'' = -\frac{M_y}{EI_y} \qquad v'' = -\frac{M_z}{EI_z} \qquad u' = \frac{N}{EA} "
    r"\qquad \theta_x' = \frac{T}{GI_T}"
)

#: Eine Lagerkraft im Raum, in der Folge des Rechenkerns: Zeichen und Einheit.
LAGERKRAEFTE = (("R_x", "kN"), ("R_y", "kN"), ("R_z", "kN"),
                ("M_x", "kNm"), ("M_y", "kNm"), ("M_z", "kNm"))

#: Die Summen der Gleichgewichtsprobe im Raum -- Momente um den Ursprung.
SUMMEN = ((r"\sum F_x", "kN"), (r"\sum F_y", "kN"), (r"\sum F_z", "kN"),
          (r"\sum M_x", "kNm"), (r"\sum M_y", "kNm"), (r"\sum M_z", "kNm"))

#: Je Schnittgroesse ihre Einheit -- Kraefte in kN, Momente in kNm.
EINHEITEN = {"N": "kN", "V_y": "kN", "V_z": "kN", "T": "kNm", "M_y": "kNm", "M_z": "kNm"}

#: Die Extremwerte im Raum: Feld im Verlauf, Zeichen, Einheit, Faktor von SI
#: und Nachkommastellen -- das Zeichen ist das Feld.
EXTREMWERTE = (*((g, g, EINHEITEN[g], 1e-3, 1) for g in SCHNITTGROESSEN),
               ("f_y", "f_y", "mm", 1e3, 2), ("f_z", "f_z", "mm", 1e3, 2))


def schreiben(p: Protokoll, system: "Balkensystem3d", befund: "Systembefund") -> None:
    """Die ganze Herleitung eines gerechneten Systems."""
    e = befund.ergebnis
    p.annahme(ANNAHME)
    p.annahme(DURCHBIEGUNG)
    _staebe(p, system, befund.gerechnet)
    _lager(p, befund.gerechnet)
    for m in e.meldungen:
        (p.warnung if m.fehler else p.hinweis)(m.text)
    if e.K is None:
        return
    _ansaetze(p, befund)
    eben.unbekannte(p, e)
    for fall in e.faelle:
        _fall(p, befund, fall)


# ===========================================================================
# Das System
# ===========================================================================


def _staebe(p: Protokoll, system: "Balkensystem3d", modell: System) -> None:
    knoten = {k.name: k for k in modell.knoten}
    name = {q.kennung: q.name for q in system.querschnitte}
    zeilen = []
    for stab in modell.staebe:
        a, b = knoten.get(stab.a), knoten.get(stab.b)
        if a is None or b is None:
            continue
        paar = system.paare.get(stab.name)
        steif = paar is not None and stab.traegt and stab.EA > 0.0
        zeilen.append([
            stab.name, f"{stab.a} – {stab.b}", Mathe(fest(betrag(minus(punkt(b), punkt(a))), 3)),
            Mathe(fest(math.degrees(stab.drehung), 1)),
            name[paar[0]] if paar is not None else ("kein Stab" if not stab.traegt else "–"),
            *(Mathe(fest(wert / faktor, 0)) if steif else "–"
              for wert, faktor in ((stab.EA, 1e6), (stab.EI_y, 1e3), (stab.EI_z, 1e3),
                                   (stab.GI_T, 1e3))),
            eben.gelenke_text(stab),
            eben.linienlager_text(("quer y", stab.quer_y), ("quer z", stab.quer_z),
                                  ("längs", stab.laengs)),
        ])
    if zeilen:
        p.tabelle(["Stab", "Knoten", Mathe(r"L\ [\mathrm{m}]"), Mathe(r"\beta\ [°]"),
                   "Querschnitt", Mathe(r"EA\ [\mathrm{MN}]"),
                   Mathe(r"EI_y\ [\mathrm{kNm}^{2}]"), Mathe(r"EI_z\ [\mathrm{kNm}^{2}]"),
                   Mathe(r"GI_T\ [\mathrm{kNm}^{2}]"), "Gelenk", "Linienlager"],
                  zeilen, titel="Stäbe")


def _lager(p: Protokoll, modell: System) -> None:
    if not modell.lager:
        return
    p.tabelle(["Lager", "Knoten", Mathe("x"), Mathe("y"), Mathe("z"), Mathe(r"\varphi_x"),
               Mathe(r"\varphi_y"), Mathe(r"\varphi_z")],
              [[l.name, l.knoten, *(eben.halt_text(h, "kN/m") for h in l.verschiebungen),
                *(eben.halt_text(h, "kNm/rad") for h in l.drehungen)] for l in modell.lager],
              titel="Lager")


def _ansaetze(p: Protokoll, befund: "Systembefund") -> None:
    e, modell = befund.ergebnis, befund.gerechnet
    p.ansatz(st3.ZERLEGUNG_LATEX, titel="Ein Stab im Raum: drei ebene Stäbe",
             name="Zerlegung eines Stabs im Raum")
    p.ansatz(st.STEIFIGKEIT_LATEX, titel="Steifigkeitsmatrix eines ebenen Stabs, in seinen Achsen",
             name="Steifigkeitsmatrix eines Stabs")
    p.ansatz(st3.DREHUNG_LATEX, titel="Von den Achsen des Systems in die des Stabs",
             name="Achsen eines Stabs im Raum")
    p.text("Der Drehwinkel β dreht y und z des Stabs im Rechtssinn um seine x-Achse. Bei einem "
           "lotrechten Stab ist y vor der Drehung die Achse −Y des Systems.")
    if any(t.k_y or t.k_z or t.k_x for t in e.teilstaebe):
        p.ansatz(st.BETTUNG_LATEX, titel="Bettung eines Stabs, je Ebene quer und längs",
                 name="Bettung eines Stabs")
    if any(isinstance(l, Stablast) for f in modell.lastfaelle for l in f.lasten):
        p.ansatz(st.LASTEN_LATEX, titel="Arbeitsgleiche Knotenkräfte der Lasten, je Ebene",
                 name="Arbeitsgleiche Knotenkräfte")
    p.ansatz(eben.GLEICHUNGSSYSTEM_LATEX, titel="Gesamtsteifigkeitsmatrix und Gleichungssystem",
             name="Gleichungssystem der Steifigkeitsmethode")
    if any(t.gelenk_a or t.gelenk_b for t in e.teilstaebe):
        p.text("Ein Gelenk löst am Stabende alle drei Momente, wie ein Kugelgelenk (nach Vorgabe, "
               "nicht nachgeschlagen): das Stabende bekommt eigene Drehungen als Unbekannte. "
               "Mit Gelenken an beiden Enden trägt ein Stab keine Torsion.")
    unbestimmt = e.unbestimmt()
    if unbestimmt:
        p.hinweis(f"{UNBESTIMMT}: {', '.join(unbestimmt)}. Um mindestens eine Achse hält dort "
                  f"nichts die Drehung; sie ist gestrichen und null gesetzt.")
    if len(e.teilstaebe) <= STAEBE_MIT_MATRIX:
        for t in e.teilstaebe:
            p.gleichung(rf"\mathbf{{k}}_{{\text{{{text_latex(eben.teilname(e, t))}}}}} = "
                        + eben.matrix_latex(t.k, 1e-3),
                        titel=f"Steifigkeitsmatrix {eben.teilname(e, t)}, L = {t.L:.3f} m "
                              f"(kN, m)")
    p.ansatz(SCHNITTGROESSEN_LATEX, titel="Schnittgrössen in den Achsen des Stabs",
             name="Schnittgrössen eines Stabs im Raum")
    p.text("V_z = dM_y/dx und V_y = dM_z/dx gelten, wo kein verteiltes Moment liegt. M_z zieht "
           "wie M_y an der Faser auf der positiven Seite seiner Achse (nach Vorgabe, nicht "
           "nachgeschlagen).")
    p.ansatz(BIEGELINIE_LATEX, titel="Biegelinien, Längsverschiebung und Verdrillung",
             name="Biegelinie eines Stabs im Raum")


# ===========================================================================
# Je Fall
# ===========================================================================


def _fall(p: Protokoll, befund: "Systembefund", fall: Fall) -> None:
    eben.kopf_eines_falls(p, befund, fall)
    _verschiebungen(p, befund, fall)
    verlaeufe = befund.verlaeufe(fall.name)
    _stabenden(p, verlaeufe)
    eben.lagerkraefte(p, befund, fall, LAGERKRAEFTE)
    eben.extremwerte(p, verlaeufe, EXTREMWERTE, durchbiegungen=("f_y", "f_z"))
    eben.gleichgewicht(p, fall, SUMMEN)


def _verschiebungen(p: Protokoll, befund: "Systembefund", fall: Fall) -> None:
    """
    Je Knoten seine Verschiebung und Drehung. Eine Drehung um eine Achse
    des Systems, die eine gestrichene Achse beruehrt, ist nicht bestimmbar.
    """
    orte = befund.ergebnis.orte
    zeilen = []
    for k in befund.gerechnet.knoten:
        ort = orte.get(k.name)
        if ort is None:
            continue
        werte = fall.verschiebungen[k.name]
        zeilen.append([k.name, *(Mathe(fest(u * 1e3, 2)) for u in werte[:3]),
                       *("nicht bestimmbar"
                         if any(abs(skalar(o, achse)) > 1e-9 for o in ort.offen)
                         else Mathe(fest(phi * 1e3, 3)) for achse, phi in zip(ACHSEN, werte[3:]))])
    p.tabelle(["Knoten", *(Mathe(rf"u_{a}\ [\mathrm{{mm}}]") for a in "xyz"),
               *(Mathe(rf"\varphi_{a}\ [\mathrm{{mrad}}]") for a in "xyz")],
              zeilen, titel="Verschiebungen der Knoten")


def _stabenden(p: Protokoll, verlaeufe) -> None:
    zeilen = []
    for name, v in verlaeufe.items():
        for ende, werte in (("a", v.bei(0.0)), ("b", v.bei(v.L, links=True))):
            zeilen.append([name, ende, *(Mathe(fest(werte[g] / 1e3, 1)) for g in SCHNITTGROESSEN)])
    p.tabelle(["Stab", "Ende", *(Mathe(rf"{g}\ [\mathrm{{{EINHEITEN[g]}}}]")
                                 for g in SCHNITTGROESSEN)],
              zeilen, titel="Schnittgrössen an den Stabenden")
