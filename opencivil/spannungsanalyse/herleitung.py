"""
opencivil/spannungsanalyse/herleitung.py -- wie eine Linie entstand.

VERANTWORTUNG:
Die Herleitung einer Linie und ihres Moduls, mit den Zahlen des Falls --
daraus bildet die Formelsammlung ihr Thema (:data:`THEMA`). Was nur die Art
des Bauteils weiss, schreibt das Paar (:class:`~opencivil.spannungsanalyse.linie.Paar`).
"""

from __future__ import annotations

import math
import re
from typing import TYPE_CHECKING, List, Mapping, Optional, Tuple

from opencivil.core.einheiten import GRAD, Groesse
from opencivil.core.latex import Mathe
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.spannungsanalyse.linie import Linie, Paar
from opencivil.spannungsanalyse.modul import Modullinie

if TYPE_CHECKING:
    from opencivil.core.wert import Wert

#: Unter diesem Thema steht in der Formelsammlung, wie die Linien entstehen.
THEMA = "Spannung-Dehnung-Analyse"


# ===========================================================================
# Herleitung -- fuer die Formelsammlung
# ===========================================================================


def herleitung(p: Protokoll, fall, paar: Paar, linie: Linie,
                werte: Mapping[str, "Wert"], raum: str,
                modul: Optional[Modullinie] = None,
                raender: Tuple[str, str] = ("oben", "unten")) -> None:
    """
    Wie die Linie entstand -- mit den Zahlen dieses Falls, und ohne sie in der
    Formelsammlung, die daraus «Spannung-Dehnung-Analyse» bildet. Mit
    ``modul`` dazu, wie aus ihr der aequivalente E-Modul wird. ``raender``
    nennt die Raender bei z = 0 und z = h, wie die Analyse sie nennt
    (:attr:`~opencivil.spannungsanalyse.analysen.Analyse.raender`): bei Zug
    links heisst die Randdehnung bei z = 0 «rechts», nicht «oben».

    ``paar`` ist das Loeserpaar einer Platte oder eines gezeichneten
    Querschnitts. Was vor dem Ende der Linie steht -- die Gesetze, den Riss,
    das Fliessen, die Grenzdehnungen --, schreibt das Paar
    (``herleitung_gesetze``): mit Beton alle gleich
    (:class:`~opencivil.spannungsanalyse.riss.Bruttoriss`), ohne Beton ohne
    Riss (:class:`~opencivil.spannungsanalyse.rissfrei.RissfreiesPaar`).
    Was nur die Art des Bauteils weiss -- die Dehnung am Ende, der Bezug des
    Moduls --, schreibt es ebenso selbst. Der Rest ist derselbe Text.
    """
    ab = len(p.bloecke)
    w = Zwischenwerte(f"{raum}.analyse.{re.sub(r'[^0-9A-Za-z]+', '_', fall.name)}")

    def ein(name: str) -> "Wert":
        return werte[paar.ids[name]]

    p.titel(f"{THEMA}: {fall.name}", raum=raum)
    p.erklaerung(
        "Eine Spannung-Dehnung-Analyse hält nichts gegen etwas: sie zeigt, was "
        "der Querschnitt tut. Gerechnet wird mit dem Faserintegral der Nachweise "
        "und mit den Werkstoffgesetzen, die die Analyse wählt.")
    h, A, I = paar.herleitung_gesetze(p, w, linie, ein, werte)
    if linie.bruch is not None:
        b = linie.bruch
        oben = w.dehnung("eps_oben", rf"\varepsilon_{{{raender[0]}}}", b.eps_oben)
        unten = w.dehnung("eps_unten", rf"\varepsilon_{{{raender[1]}}}", b.eps_unten)
        neigung = b.ebene.neigung if b.ebene is not None else 0.0
        tiefe, zeichen = h, ""
        if neigung != 0.0:
            # Gekippt gelten die Raender senkrecht zur Nulllinie, und die
            # Linie laeuft ueber den Anteil der Kruemmung senkrecht zur Achse.
            theta = w.wert("theta", r"\vartheta", Groesse(math.degrees(neigung), GRAD), stellen=1)
            p.erklaerung(
                "Am Ende ist die Nulllinie um ϑ gegen die Achse der Biegung gedreht, im "
                "Gegenuhrzeigersinn positiv: so bleibt kein Moment um die andere Achse. "
                "Die Randdehnungen gelten senkrecht zu ihr, über die Tiefe h_ϑ des "
                "Querschnitts in dieser Richtung.")
            p.wert(theta, titel="Neigung der Nulllinie am Ende")
            tiefe = w.laenge("h_theta", r"h_{\vartheta}", b.ebene.loeser.h,
                             "Tiefe des Querschnitts senkrecht zur Nulllinie")
            zeichen = r" \cdot \cos\left(@theta\right)"
        if linie.art.ueber_moment:
            p.formel(w.kruemmung("chi_u", r"\chi_{u}", b.verformung),
                     r"\frac{@eps_unten - @eps_oben}{@h}" + zeichen,
                     {"eps_unten": unten, "eps_oben": oben, "h": tiefe,
                      **({"theta": theta} if zeichen else {})},
                     titel="Grösste Krümmung")
        else:
            paar.herleitung_dehnung_am_ende(p, w, b, oben, unten, tiefe)
        p.text(f"Massgebend: {b.massgebend}.")
    if modul is not None:
        _herleitung_modul(p, w, modul, paar, A, I)
    p.herkunft_stempeln(THEMA, ab=ab)


def _herleitung_modul(p: Protokoll, w: Zwischenwerte, modul: Modullinie, paar: Paar,
                      A: "Wert", I: "Wert") -> None:
    """
    Der aequivalente Modul: sein Bezug, die Formel und der Modul an den Ecken
    der Linie -- jede Zeile mit Kraft und Verformung, also von Hand
    nachzurechnen. Beim Stahlbeton ist der Bezug der reine Betonquerschnitt,
    der Bruttoquerschnitt des Risses mit seinem ``A`` und ``I``; ohne Beton
    der Querschnitt selbst (:attr:`~opencivil.spannungsanalyse.linie.Paar.modulbezug`).
    """
    bezug = modul.bezug
    p.erklaerung(
        f"{bezug.erklaerung} Gezählt wird "
        "ab dem Zustand ohne laufende Kraft: was die festgehaltene Kraft allein "
        "verformt, kann ein solcher Querschnitt nicht abbilden. Ist sie null, ist es "
        "genau M = E·I·χ bzw. N = E·A·ε.")
    if modul.art.ueber_moment:
        I_bezug = paar.herleitung_traegheit(p, w, I)
        p.ansatz(rf"E_{{eq}} = \frac{{M}}{{{I_bezug.symbol} \cdot \left(\chi - \chi_0\right)}}",
                 titel="Äquivalenter E-Modul über dem Moment")
        p.wert(w.kruemmung("chi_0", r"\chi_0", modul.null),
               titel="Krümmung ohne Moment, unter der festen Normalkraft")
        kopf = [Mathe(r"M\ [\mathrm{kNm}]"), Mathe(r"\chi - \chi_0\ [\mathrm{m}^{-1}]")]
        verformung = lambda v: f"{v - modul.null:.5f}"
    else:
        A_bezug = paar.herleitung_flaeche(p, w, A)
        p.ansatz(rf"E_{{eq}} = \frac{{N}}{{{A_bezug.symbol} \cdot "
                 r"\left(\varepsilon_m - \varepsilon_0\right)}",
                 titel="Äquivalenter E-Modul über der Normalkraft")
        p.wert(w.dehnung("eps_0", r"\varepsilon_0", modul.null, stellen=4),
               titel=f"Dehnung {paar.bezugsort} ohne Normalkraft, unter dem festen Moment")
        kopf = [Mathe(r"N\ [\mathrm{kN}]"), Mathe(r"\varepsilon_m - \varepsilon_0\ [‰]")]
        verformung = lambda v: f"{(v - modul.null) * 1e3:.4f}"

    linie = modul.linie
    ecken: List[Tuple[str, float, float]] = []
    if linie.sprung is not None:
        vor, nach = linie.sprung
        ecken += [("ungerissen, beim Riss", vor.kraft, vor.verformung),
                  ("gerissen, beim Riss", nach.kraft, nach.verformung)]
    elif linie.punkte and not linie.am_bruch:
        ecken.append(("ungerissen", linie.punkte[-1].kraft, linie.punkte[-1].verformung))
    if linie.fliessen is not None:
        ecken.append(("Fliessbeginn", linie.fliessen.kraft, linie.fliessen.verformung))
    if linie.am_bruch:
        ecken.append(("Ende", linie.punkte[-1].kraft, linie.punkte[-1].verformung))
    zeilen = []
    for name, kraft, v in ecken:
        E = modul.modul(kraft, v)
        if E is None:
            continue
        zeilen.append([name, Mathe(f"{kraft / 1e3:.1f}"), Mathe(verformung(v)),
                       Mathe(f"{E / 1e6:.0f}"), Mathe(f"{E / bezug.E:.3f}")])
    if zeilen:
        p.tabelle(kopf=["Punkt", *kopf, Mathe(r"E_{eq}\ [\mathrm{N/mm^2}]"),
                        Mathe(rf"E_{{eq}}/{bezug.zeichen}")],
                  zeilen=zeilen, titel="Der äquivalente Modul an den Ecken der Linie",
                  ausrichtung="lrrrr")
