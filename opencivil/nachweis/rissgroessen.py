"""
opencivil/nachweis/rissgroessen.py -- wann der Beton reisst.

VERANTWORTUNG:
Die Rissgroessen an einer Stelle -- fuer die Nachweise der Platte und des
gezeichneten Querschnitts wie fuer ihre Spannung-Dehnung-Analysen:

* **die rissaktive Dicke** (:func:`rissaktive_dicke`): unter Biegung ein
  Drittel der Hoehe in Biegerichtung, unter Zug die kleinere Abmessung
  ``min(h; b)``, wahlweise hoechstens 500 mm;
* **der Beiwert** ``k_t = 1/(1 + 0.5·t)`` und mit ihm ``f_ct,eff = k_t·f_ctm``
  (:func:`beiwert_dicke`, :func:`protokoll_zugfestigkeit`);
* **das Rissmoment unter reiner Biegung**: das Moment, bei dem ``f_ct,eff``
  am ungerissenen Bruttoquerschnitt zum ersten Mal irgendwo erreicht wird
  (:func:`rissmoment`). Mit dem Deviationsmoment ``I_yz`` kippt die
  Nulllinie; «einachsig» bleibt sie waagrecht, und es gilt ``W = I/v``. Bei
  der Platte, einem Rechteck, ist es beide Male ``b·h²/6``
  (:func:`rissmoment_rechteck`).

So hat es der Benutzer am 2026-10-17 entschieden. Bis dahin standen die
Rissgroessen viermal da -- im sproeden Versagen, in den Richtungsnachweisen
und in den beiden Paaren der Analyse --, und sie sagten schon Verschiedenes:
das Rissmoment rechnete auch einachsig mit ``I_yz``, die Analyse ohne, und
fuer die rissaktive Dicke unter Zug gab es vier Regeln.

DIE PLATTE UNTER ZUG:
Ihre Breite ``b`` ist ein Streifen, keine Abmessung des Bauteils: in ihrer
Ebene ist die Platte unbegrenzt. Unter Zug reisst sie darum ueber ihre Dicke,
``t = h``, auch bei einem Streifen, der schmaler ist als die Platte dick.

Die Uebertragung der Regeln der Platte auf den gezeichneten Querschnitt
geschieht nach Vorgabe, nicht nachgeschlagen (``notizbuch/Notizen/TODO.md``).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, List, Tuple

from opencivil.core.berechnung import Eingabebezug, Eingaben
from opencivil.core.einheiten import M, MIO_MM3, MIO_MM4, Groesse
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert
from opencivil.querschnitt.analyse import Querschnittsanalyse

#: Teiler der Hoehe in Biegerichtung im Beiwert. Unter Biegung reisst der
#: Randbereich, nicht die halbe Hoehe wie beim Zwang. SIA 262:2025, 4.4.1.3.
MOMENTENTEILER = 3.0

#: Groesste rissaktive Dicke unter Zug, in m -- wo die Begrenzung eingeschaltet ist.
DICKENGRENZE = 0.500


def beiwert_dicke(t: float) -> float:
    """
    ``k_t = 1 / (1 + 0.5 * t)`` -- ein dickes Bauteil reisst nicht ueber
    seine ganze Hoehe gleichzeitig.

    Empirisch: ``t`` geht in Metern ein, und Meter ist die SI-Basis. Welche
    Dicke gilt, sagt :func:`rissaktive_dicke`.
    """
    return 1.0 / (1.0 + 0.5 * t)


def rissaktive_dicke(*, h: float, b: float = math.inf, zug: bool,
                     begrenzt: bool = False) -> float:
    """
    Wie dick der Beton reisst, in m. Unter Biegung ein Drittel der Hoehe ``h``
    in Biegerichtung; unter Zug die kleinere Abmessung ``min(h; b)``, mit
    ``begrenzt`` hoechstens :data:`DICKENGRENZE`. Ohne ``b`` -- bei der
    Platte, siehe Dateikopf -- die Dicke ``h``.
    """
    if not zug:
        return h / MOMENTENTEILER
    t = min(h, b)
    return min(DICKENGRENZE, t) if begrenzt else t


def protokoll_zugfestigkeit(
    p: Protokoll, werte: Zwischenwerte, *, k_t: float, f_ct_eff: float,
    h: Wert, f_ctm: Wert, teiler: float, referenz: str,
    titel: str = "Beiwert für die Plattendicke",
) -> Wert:
    """
    Beiwert fuer die Dicke und wirksame Zugfestigkeit, hergeleitet.

    ``teiler`` ist der Anteil der Dicke, der reisst: ein Drittel unter
    Biegung, unter Zug die ganze rissaktive Dicke (``1``). Zurueck kommt
    ``f_ct,eff`` fuer die Zeile danach.
    """
    anteil = "@h" if teiler == 1 else rf"@h/{teiler:.0f}"
    beiwert = werte.zahl("k_t", "k_t", k_t)
    p.formel(beiwert, rf"\frac{{1}}{{1 + 0.5 \cdot {anteil}}}", {"h": h},
             titel=titel, referenz=referenz, empirisch={"h": M},
             name="Beiwert für die Dicke")
    wirksam = werte.spannung("f_ct_eff", "f_{ct,eff}", f_ct_eff, stellen=2)
    p.formel(wirksam, r"@k_t \cdot @f_ctm", {"k_t": beiwert, "f_ctm": f_ctm},
             titel="Wirksame Zugfestigkeit")
    return wirksam


# ===========================================================================
# Das Rechteck: die Platte
# ===========================================================================


@dataclass(frozen=True)
class Rissgroessen:
    """Das Rissmoment eines Rechtecks und was dazu gehoert -- je Platte, nicht je Lage."""

    k_t: float
    f_ct_eff: float
    M_Riss: float
    """Rissmoment in Nm, bezogen auf die betrachtete Breite."""


def rissmoment_rechteck(*, h: float, b: float, f_ctm: float) -> Rissgroessen:
    """
    Das Moment, bei dem das ungerissene Rechteck ``b × h`` aufreisst --
    ``h²·b/6`` ist sein elastisches Widerstandsmoment. Alles in SI-Basis;
    Rueckgabe in Nm.
    """
    k_t = beiwert_dicke(rissaktive_dicke(h=h, zug=False))
    f_ct_eff = k_t * f_ctm
    return Rissgroessen(k_t=k_t, f_ct_eff=f_ct_eff, M_Riss=f_ct_eff * h * h * b / 6.0)


def rissmoment_wert(basis: str, g: Rissgroessen) -> Wert:
    """Das Rissmoment -- die Einwirkung in Tabelle und Herleitung."""
    return Zwischenwerte(basis).moment("M_Riss", "M_{Riss}", g.M_Riss, "Einwirkung")


def protokoll_rissmoment_rechteck(
    p: Protokoll, e: Eingaben, g: Rissgroessen, *, basis: str, referenz: str,
) -> None:
    """
    Das Rissmoment von ``k_t`` an -- fuer das spröde Versagen und die
    Zwängung auf Biegung der Platte dieselben drei Zeilen. Gebraucht werden
    die Eingaben ``h``, ``b`` und ``f_ctm``.
    """
    f_ct_eff = protokoll_zugfestigkeit(
        p, Zwischenwerte(basis), k_t=g.k_t, f_ct_eff=g.f_ct_eff, h=e["h"],
        f_ctm=e["f_ctm"], teiler=MOMENTENTEILER, referenz=referenz)
    p.formel(rissmoment_wert(basis, g), r"@f_ct_eff \cdot \frac{@h^{2} \cdot @b}{6}",
             {"f_ct_eff": f_ct_eff, "h": e["h"], "b": e["b"]},
             titel="Rissmoment des ungerissenen Querschnitts")


# ===========================================================================
# Der gezeichnete Querschnitt
# ===========================================================================


@dataclass(frozen=True)
class Ecke:
    """Eine Ecke des Betons, vom Schwerpunkt aus in m -- und ihr Beton."""

    y: float
    z: float
    punkt: Tuple[float, float]
    """Dieselbe Ecke in der Zeichnung, in mm."""

    stoff: Any
    f_ctm: float


@dataclass(frozen=True)
class Bruttoquerschnitt:
    """
    Der ungerissene Bruttoquerschnitt ohne Stahl: Traegheitsmomente um den
    Schwerpunkt und die Ecken des Betons -- in SI.
    """

    I_y: float
    I_z: float
    I_yz: float
    ecken: Tuple[Ecke, ...]

    def ausdehnung(self, um_y: bool) -> Tuple[float, float]:
        """Die Hoehe in Biegerichtung und die Breite quer dazu, in m -- aus der Zeichnung."""
        breite_y = (max(e.punkt[0] for e in self.ecken) - min(e.punkt[0] for e in self.ecken)) * 1e-3
        hoehe_z = (max(e.punkt[1] for e in self.ecken) - min(e.punkt[1] for e in self.ecken)) * 1e-3
        return (hoehe_z, breite_y) if um_y else (breite_y, hoehe_z)

    def einheitsspannung(self, ecke: Ecke, M_y: float, M_z: float, *,
                         einachsig: bool) -> float:
        """
        Die Spannung an der Ecke bei einem Moment von eins in dieser Richtung,
        Zug positiv. ``einachsig`` mit waagrechter Nulllinie, ohne ``I_yz``.
        """
        if einachsig:
            return -M_y * ecke.z / self.I_y
        nenner = self.I_y * self.I_z - self.I_yz * self.I_yz
        return -(M_y * (self.I_z * ecke.z - self.I_yz * ecke.y)
                 + M_z * (self.I_y * ecke.y - self.I_yz * ecke.z)) / nenner


def rissbezuege(analyse: Querschnittsanalyse) -> List[Eingabebezug]:
    """Was der Bruttoquerschnitt liest, ueber die Grundbezuege hinaus: die Traegheitsmomente."""
    return [Eingabebezug(k, analyse.id_von(k)) for k in ("I_y", "I_z", "I_yz")]


def bruttoquerschnitt(analyse: Querschnittsanalyse, e: Eingaben) -> Bruttoquerschnitt:
    """Der Bruttoquerschnitt eines gezeichneten Querschnitts, aus den Eingaben von :func:`rissbezuege`."""
    y_S, z_S = e.g("y_S").si, e.g("z_S").si
    return Bruttoquerschnitt(
        I_y=e.g("I_y").si, I_z=e.g("I_z").si, I_yz=e.g("I_yz").si,
        ecken=tuple(Ecke(y=p[0] * 1e-3 - y_S, z=p[1] * 1e-3 - z_S, punkt=p, stoff=stoff,
                         f_ctm=abs(analyse.kennwert(e, stoff, "f_ctm")))
                    for p, stoff in analyse.beton_ecken))


@dataclass(frozen=True)
class Rissmoment:
    """Das Rissmoment in einer Richtung -- und woraus es entsteht."""

    ecke: Ecke
    """Die Ecke, die zuerst ihre Zugfestigkeit erreicht."""

    W: float
    """Das Widerstandsmoment zu ihr, m³."""

    hoehe: float
    """Die Ausdehnung des Betons in Biegerichtung, m -- fuer ``k_t``."""

    k_t: float
    f_ct_eff: float
    M_Riss: float
    """in Nm."""


def rissmoment(q: Bruttoquerschnitt, M_y: float, M_z: float, *,
               einachsig: bool) -> Rissmoment:
    """
    Das Rissmoment in der Richtung ``(M_y, M_z)`` -- einem Moment von eins:
    das Moment unter reiner Biegung, bei dem ``f_ct,eff`` zum ersten Mal
    irgendwo erreicht wird. Bei mehreren Betonen reisst zuerst die Ecke mit
    der groessten Spannung, gemessen an ihrer Zugfestigkeit.
    """
    hoehe, _ = q.ausdehnung(M_y != 0.0)
    k_t = beiwert_dicke(rissaktive_dicke(h=hoehe, zug=False))
    gezogen = [(ecke, q.einheitsspannung(ecke, M_y, M_z, einachsig=einachsig))
               for ecke in q.ecken]
    ecke, sigma = max((es for es in gezogen if es[1] > 0.0),
                      key=lambda es: es[1] / es[0].f_ctm)
    W = 1.0 / sigma
    f_ct_eff = k_t * ecke.f_ctm
    return Rissmoment(ecke=ecke, W=W, hoehe=hoehe, k_t=k_t, f_ct_eff=f_ct_eff,
                      M_Riss=f_ct_eff * W)


def protokoll_spannung_ungerissen(p: Protokoll, *, einachsig: bool) -> None:
    """Wie der ungerissene Querschnitt Spannung traegt -- der Ansatz des Rissmoments."""
    if einachsig:
        p.ansatz(r"\sigma(z) = -\frac{M_y \cdot z'}{I_y} \qquad z' = z - z_S",
                 titel="Spannung im ungerissenen Querschnitt, Nulllinie waagrecht")
        return
    p.ansatz(r"\sigma(y, z) = -\frac{M_y\,(I_z z' - I_{yz} y') + "
             r"M_z\,(I_y y' - I_{yz} z')}{I_y I_z - I_{yz}^2}"
             r"\qquad y' = y - y_S,\ z' = z - z_S",
             titel="Spannung im ungerissenen Querschnitt")


def protokoll_rissmoment(p: Protokoll, e: Eingaben, analyse: Querschnittsanalyse,
                         werte: Zwischenwerte, riss: Rissmoment, M_y: float, M_z: float,
                         *, einachsig: bool, referenz: str) -> Wert:
    """Die Herleitung von :func:`rissmoment` -- zurueck kommt ``M_Riss``."""
    ecke = riss.ecke
    p.text(f"Gezogenster Betonpunkt: y = {ecke.punkt[0]:g} mm, z = {ecke.punkt[1]:g} mm "
           f"({ecke.stoff.name}).")
    h = werte.laenge("h", "h", riss.hoehe)
    f_ct_eff = protokoll_zugfestigkeit(
        p, werte, k_t=riss.k_t, f_ct_eff=riss.f_ct_eff, h=h,
        f_ctm=e[analyse._name(ecke.stoff, "f_ctm")], teiler=MOMENTENTEILER,
        referenz=referenz, titel="Beiwert für die Höhe in Biegerichtung")
    W = werte.wert("W", "W", Groesse.aus_si(riss.W, MIO_MM3), 2)
    I_y = werte.wert("Iy", "I_y", Groesse.aus_si(e.g("I_y").si, MIO_MM4), 1)
    if einachsig:
        p.formel(W, r"\frac{@Iy}{@v}", {
            "Iy": I_y,
            "v": werte.laenge("v", "v", -M_y * ecke.z, "Abstand des gezogenen Rands vom Schwerpunkt"),
        }, titel="Widerstandsmoment zum gezogenen Rand, Nulllinie waagrecht")
    else:
        p.formel(W, _w_vorlage(M_y, M_z), {
            "Iy": I_y,
            "Iz": werte.wert("Iz", "I_z", Groesse.aus_si(e.g("I_z").si, MIO_MM4), 1),
            "Iyz": werte.wert("Iyz", "I_{yz}", Groesse.aus_si(e.g("I_yz").si, MIO_MM4), 1),
            "y": werte.laenge("y", "y'", ecke.y),
            "z": werte.laenge("z", "z'", ecke.z),
        }, titel="Widerstandsmoment zum gezogensten Betonpunkt")
    M_Riss = werte.moment("M_Riss", "M_{Riss}", riss.M_Riss)
    p.formel(M_Riss, r"@f \cdot @W", {"f": f_ct_eff, "W": W},
             titel="Rissmoment des ungerissenen Querschnitts")
    return M_Riss


def _w_vorlage(M_y: float, M_z: float) -> str:
    """``W = 1/σ`` bei einem Moment von eins -- je Richtung ausgeschrieben."""
    zaehler = r"@Iy \cdot @Iz - @Iyz^{2}"
    nenner = {
        (1.0, 0.0): r"@Iyz \cdot @y - @Iz \cdot @z",
        (-1.0, 0.0): r"@Iz \cdot @z - @Iyz \cdot @y",
        (0.0, 1.0): r"@Iyz \cdot @z - @Iy \cdot @y",
        (0.0, -1.0): r"@Iy \cdot @y - @Iyz \cdot @z",
    }[(M_y, M_z)]
    return rf"\frac{{{zaehler}}}{{{nenner}}}"
