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
from typing import TYPE_CHECKING, Callable, List, Mapping, Optional, Tuple

from opencivil.core.einheiten import GRAD, Groesse
from opencivil.core.latex import Mathe
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import kennung_aus
from opencivil.material.basis import mit_index
from opencivil.material.betonstahl import FLIESSDEHNUNG
from opencivil.querschnitt.gesetzwahl import Werkstoffsatz, betongesetz, wirksamer_modul
from opencivil.querschnitt.werkstoffgesetz import BetonUngerissen
from opencivil.spannungsanalyse.art import Analyseart
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
                modul: Optional[Modullinie] = None) -> None:
    """
    Wie die Linie entstand -- mit den Zahlen dieses Falls, und ohne sie in der
    Formelsammlung, die daraus «Spannung-Dehnung-Analyse» bildet. Mit
    ``modul`` dazu, wie aus ihr der aequivalente E-Modul wird.

    ``paar`` ist das Loeserpaar einer Platte oder eines gezeichneten
    Querschnitts. Was nur die Art des Bauteils weiss -- die Tiefe, der Riss,
    die Dehnung am Ende, der reine Betonquerschnitt --, schreibt es selbst
    (``tiefe``, ``herleitung_riss``, ``herleitung_dehnung_am_ende``,
    ``herleitung_bezug``); der Rest ist derselbe Text.
    """
    ab = len(p.bloecke)
    w = Zwischenwerte(f"{raum}.analyse.{re.sub(r'[^0-9A-Za-z]+', '_', fall.name)}")
    momente = linie.art is Analyseart.MOMENT_KRUEMMUNG

    def ein(name: str) -> "Wert":
        return werte[paar.ids[name]]

    p.titel(f"{THEMA}: {fall.name}", raum=raum)
    p.erklaerung(
        "Eine Spannung-Dehnung-Analyse hält nichts gegen etwas: sie zeigt, was "
        "der Querschnitt tut. Gerechnet wird mit dem Faserintegral der Nachweise "
        "und mit der Kriechzahl, dem Wertesatz und der Rechenart, die die "
        "Analyse wählt.")
    wahl = paar.wahl
    phi = w.zahl("phi", r"\varphi", wahl.kriechzahl, stellen=2)
    E_c_eff = w.spannung("E_c_eff", "E_{c,eff}",
                         wirksamer_modul(ein("E_cm").groesse.si, wahl.kriechzahl))
    p.formel(E_c_eff, r"\frac{@E_cm}{1 + @phi}", {"E_cm": ein("E_cm"), "phi": phi},
             titel="Wirksamer Elastizitätsmodul")

    p.erklaerung(
        "Ungerissen (Zustand I) trägt der Beton Druck und Zug, linear mit E_c,eff "
        "– bis zum Riss: wo der Querschnitt reisst, sagt die Rissbedingung am "
        "Bruttoquerschnitt, und nur dort zählt die Zugfestigkeit. Darüber gilt "
        "der ungerissene Zustand nicht mehr, auch nicht zum Vergleich. Gerissen "
        "(Zustand II) trägt der Beton keinen Zug, und im Druck gilt das Gesetz der "
        "gewählten Rechenart.")
    # Die Gesetze, wie die Loeser sie rechnen -- aus derselben Stelle
    # (:func:`~opencivil.querschnitt.gesetzwahl.betongesetz`); sie schreiben sich selbst.
    beton = {"f_c": ein("f_c"), "E_c": E_c_eff, "eps_c1d": ein("eps_c1d"),
             "eps_c2d": ein("eps_c2d")}
    BetonUngerissen(E_c=E_c_eff.groesse.si).protokoll(p, beton, titel="Ungerissen (Zustand I)")
    betongesetz(wahl, f_c=beton["f_c"].groesse.si, E_cm=ein("E_cm").groesse.si,
                eps_c1d=beton["eps_c1d"].groesse.si, eps_c2d=beton["eps_c2d"].groesse.si
                ).protokoll(p, beton, titel="Gerissen (Zustand II)", basis=w.basis)
    if wahl.art.mit_block:
        p.erklaerung(
            "Der Spannungsblock ist ein Modell für den Bruch: unter "
            "(1 − 0.85)·ε_c2d trägt der Beton darin nichts. Über dem Riss ist die "
            "Linie mit ihm darum weicher als der Querschnitt; ihr Ende ist der "
            "Widerstand der 0.85·x-Vereinfachung. Ein Modul hängt an ihm nicht: "
            "die Kriechzahl wirkt nur auf den ungerissenen Teil.")
    else:
        p.erklaerung(
            "Unter 1 rechnet die Parabel k_σ nicht: dort hätte ihr Nenner im "
            "ansteigenden Ast eine Nullstelle. So weit kommt es mit dem kriechweichen "
            "Modul und charakteristischen Werten; mit k_σ = 1 ist der Beton bis f_c "
            "bei ε_c1d linear.")
    if wahl.satz is Werkstoffsatz.CHARAKTERISTISCH:
        p.text("Mit charakteristischen Werten: f_ck statt f_cd, f_yk statt f_yd.")

    h = paar.tiefe(w, ein)
    paar.herleitung_riss(p, w, linie, ein, h)

    p.erklaerung(
        "Der Fliessbeginn ist der Punkt, an dem die am stärksten gezogene Lage die "
        "Fliessdehnung erreicht. Danach wächst die Kraft nur noch wenig: die "
        "Druckzone wird kleiner, der Hebelarm grösser, und der Beton füllt sein "
        "Gesetz, bis eine Grenzdehnung erreicht ist. Im Bild heisst die Kraft beim "
        "Fliessbeginn M_y bzw. N_y, am Ende M_Rd bzw. N_Rd – mit "
        "charakteristischen Werten Rk statt Rd. Das Ende ist der Widerstand der "
        "Tragsicherheit, wenn sie dieselbe Rechenwahl trifft.")
    # Je Stahl seine Fliessdehnung -- unten und oben duerfen verschiedene liegen.
    for stahl in paar.staehle:
        f_s, E_s = werte[stahl.id_von(wahl.satz.stahl)], werte[stahl.id_von("E_s")]
        name, symbol = (("eps_y", r"\varepsilon_{y}") if len(paar.staehle) == 1 else
                        (f"eps_y_{kennung_aus(stahl.id)}",
                         mit_index(r"\varepsilon_{y}", stahl.symbol_index)))
        p.formel(w.dehnung(name, symbol, f_s.groesse.si / E_s.groesse.si),
                 r"\frac{@f_s}{@E_s}", {"f_s": f_s, "E_s": E_s},
                 titel="Dehnung bei Fliessbeginn", name=FLIESSDEHNUNG)
    p.erklaerung(
        "Den gerissenen Teil rechnet die Linie über die Verformung, nicht über die "
        "Kraft: zu jeder Krümmung (bei der N-ε-Linie: zu jeder Dehnung) wird die "
        "Ebene gesucht, die die festgehaltene Grösse trägt. Sie endet bei der "
        "grössten Verformung, zu der es noch ein Gleichgewicht gibt – dort ist die "
        "erste Grenzdehnung erreicht. Es sind dieselben Grenzen wie im "
        "Dehnungsfächer der genauen M-N-Linie.")
    p.ansatz(r"\varepsilon_{c,Rand} \ge -\varepsilon_{c2d} \qquad "
             r"-\varepsilon_{ud} \le \varepsilon_{s,i} \le \varepsilon_{ud} \qquad "
             r"\varepsilon\left(z_C\right) \ge -\varepsilon_{c1d}, \quad "
             r"z_C = h \cdot \left(1 - \frac{\varepsilon_{c1d}}{\varepsilon_{c2d}}\right)",
             titel="Grenzdehnungen am Ende der Linie")
    if linie.bruch is not None:
        b = linie.bruch
        oben = w.dehnung("eps_oben", r"\varepsilon_{oben}", b.eps_oben)
        unten = w.dehnung("eps_unten", r"\varepsilon_{unten}", b.eps_unten)
        neigung = b.ebene.neigung if b.ebene is not None else 0.0
        tiefe, zeichen = h, ""
        if neigung != 0.0:
            # Gekippt gelten die Raender senkrecht zur Nulllinie, und die
            # Linie laeuft ueber den Anteil der Kruemmung senkrecht zur Achse.
            theta = w.wert("theta", r"\vartheta", Groesse(math.degrees(neigung), GRAD), stellen=1)
            p.erklaerung(
                "Am Ende ist die Nulllinie um ϑ gegen die Achse der Biegung gedreht, im "
                "Gegenuhrzeigersinn positiv: so bleibt kein Moment um die andere Achse. "
                "Die Randdehnungen gelten senkrecht zu ihr, über die Tiefe h_ϑ des Betons "
                "in dieser Richtung.")
            p.wert(theta, titel="Neigung der Nulllinie am Ende")
            tiefe = w.laenge("h_theta", r"h_{\vartheta}", b.ebene.loeser.h,
                             "Tiefe des Betons senkrecht zur Nulllinie")
            zeichen = r" \cdot \cos\left(@theta\right)"
        if momente:
            p.formel(w.kruemmung("chi_u", r"\chi_{u}", b.verformung),
                     r"\frac{@eps_unten - @eps_oben}{@h}" + zeichen,
                     {"eps_unten": unten, "eps_oben": oben, "h": tiefe,
                      **({"theta": theta} if zeichen else {})},
                     titel="Grösste Krümmung")
        else:
            paar.herleitung_dehnung_am_ende(p, w, b, oben, unten, tiefe)
        p.text(f"Massgebend: {b.massgebend}.")
    if modul is not None:
        _herleitung_modul(p, w, modul,
                          bezug=lambda: paar.herleitung_bezug(p, w, momente, ein, h),
                          bezugsort=paar.bezugsort)
    p.herkunft_stempeln(THEMA, ab=ab)


def _herleitung_modul(p: Protokoll, w: Zwischenwerte, modul: Modullinie, *,
                      bezug: Callable[[], "Wert"], bezugsort: str) -> None:
    """
    Der aequivalente Modul: der reine Betonquerschnitt, die Formel und der
    Modul an den Ecken der Linie -- jede Zeile mit Kraft und Verformung, also
    von Hand nachzurechnen. ``bezug`` schreibt den reinen Betonquerschnitt
    hin, wie ihn die Art des Bauteils kennt, und gibt ihn zurueck;
    ``bezugsort`` sagt, wo die Mitteldehnung gilt.
    """
    momente = modul.art is Analyseart.MOMENT_EMODUL
    p.erklaerung(
        "Der äquivalente E-Modul ist der Modul, den ein reiner Betonquerschnitt "
        "bräuchte – ungerissen, ohne Stahl, elastisch –, um sich unter der laufenden "
        "Kraft gleich stark zu verformen wie der bewehrte Querschnitt. Gezählt wird "
        "ab dem Zustand ohne laufende Kraft: was die festgehaltene Kraft allein "
        "verformt, kann ein solcher Querschnitt nicht abbilden. Ist sie null, ist es "
        "genau M = E·I·χ bzw. N = E·A·ε.")
    if momente:
        bezug()
        p.ansatz(r"E_{eq} = \frac{M}{I_c \cdot \left(\chi - \chi_0\right)}",
                 titel="Äquivalenter E-Modul über dem Moment")
        p.wert(w.kruemmung("chi_0", r"\chi_0", modul.null),
               titel="Krümmung ohne Moment, unter der festen Normalkraft")
        kopf = [Mathe(r"M\ [\mathrm{kNm}]"), Mathe(r"\chi - \chi_0\ [\mathrm{m}^{-1}]")]
        verformung = lambda v: f"{v - modul.null:.5f}"
    else:
        bezug()
        p.ansatz(r"E_{eq} = \frac{N}{A_c \cdot \left(\varepsilon_m - \varepsilon_0\right)}",
                 titel="Äquivalenter E-Modul über der Normalkraft")
        p.wert(w.dehnung("eps_0", r"\varepsilon_0", modul.null, stellen=4),
               titel=f"Dehnung {bezugsort} ohne Normalkraft, unter dem festen Moment")
        kopf = [Mathe(r"N\ [\mathrm{kN}]"), Mathe(r"\varepsilon_m - \varepsilon_0\ [‰]")]
        verformung = lambda v: f"{(v - modul.null) * 1e3:.4f}"

    linie = modul.linie
    ecken: List[Tuple[str, float, float]] = []
    if linie.sprung is not None:
        vor, nach = linie.sprung
        ecken += [("ungerissen, beim Riss", vor.kraft, vor.verformung),
                  ("gerissen, beim Riss", nach.kraft, nach.verformung)]
    elif linie.punkte and not linie.punkte[-1].gerissen:
        ecken.append(("ungerissen", linie.punkte[-1].kraft, linie.punkte[-1].verformung))
    if linie.fliessen is not None:
        ecken.append(("Fliessbeginn", linie.fliessen.kraft, linie.fliessen.verformung))
    if linie.punkte and linie.punkte[-1].gerissen:
        ecken.append(("Ende", linie.punkte[-1].kraft, linie.punkte[-1].verformung))
    zeilen = []
    for name, kraft, v in ecken:
        E = modul.modul(kraft, v)
        if E is None:
            continue
        zeilen.append([name, Mathe(f"{kraft / 1e3:.1f}"), Mathe(verformung(v)),
                       Mathe(f"{E / 1e6:.0f}"), Mathe(f"{E / modul.E_cm:.3f}")])
    if zeilen:
        p.tabelle(kopf=["Punkt", *kopf, Mathe(r"E_{eq}\ [\mathrm{N/mm^2}]"),
                        Mathe(r"E_{eq}/E_{cm}")],
                  zeilen=zeilen, titel="Der äquivalente Modul an den Ecken der Linie",
                  ausrichtung="lrrrr")
