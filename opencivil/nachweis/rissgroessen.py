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
  Nulllinie; «einachsig» bleibt sie parallel zur Achse der Biegung, und es
  gilt ``W = I/v``. Bei der Platte, einem Rechteck, ist es beide Male
  ``b·h²/6`` (:func:`rissmoment_rechteck`, :func:`bruttoquerschnitt_rechteck`);
* **die Rissnormalkraft bei einem Moment**: die Zugkraft, bei der
  ``f_ct,eff`` zum ersten Mal irgendwo erreicht wird (:func:`rissnormalkraft`)
  -- fuer die Spannung-Dehnung-Analysen, der Platte wie des gezeichneten
  Querschnitts (:mod:`opencivil.spannungsanalyse.riss`).

So hat es der Benutzer am 2026-10-17 entschieden. Bis dahin standen die
Rissgroessen viermal da -- im sproeden Versagen, in den Richtungsnachweisen
und in den beiden Paaren der Analyse --, und sie sagten schon Verschiedenes:
das Rissmoment rechnete auch einachsig mit ``I_yz``, die Analyse ohne, und
fuer die rissaktive Dicke unter Zug gab es vier Regeln.

DIE PLATTE UNTER ZUG:
Ihre Breite ``b`` ist ein Streifen, keine Abmessung des Bauteils: in ihrer
Ebene ist die Platte unbegrenzt. Unter Zug reisst sie darum ueber ihre Dicke,
``t = h``, auch bei einem Streifen, der schmaler ist als die Platte dick.

DIE VORSPANNUNG:
Spannglieder mit Vordehnung druecken den Beton schon ohne Last, je mit
ihrer Kraft nach allen Verlusten an ihrer Stelle (:class:`Vorspannung`).
Am Bruttoquerschnitt ist das eine Normalkraft und ein Moment, und ihre
Spannung an jeder Ecke kommt zu der aus der Einwirkung: der gezogene Rand
reisst spaeter, der andere frueher. So rechnen alle, die den Riss des
gezeichneten Querschnitts brauchen -- das sproede Versagen (4.3.1.2 laesst
die Vorspannung zu), die Zwaengung auf Biegung, deren Stahlspannung
ebenfalls mit ihr gerechnet ist, und die Spannung-Dehnung-Analysen
(4.4.3.2.4). Schlaff angesetzte Glieder zaehlen nicht: ihre Vorspannung
steht in den Lastfaellen.

Die Uebertragung der Regeln der Platte auf den gezeichneten Querschnitt
geschieht nach Vorgabe: SIA 262:2025, 4.4.1.3 nimmt die kleinste Abmessung
des Zuggurts und legt ``h/3`` nur fuer Platten und Rechtecke unter Biegung
fest. Fuer andere Formen ist das offen (``notizbuch/Notizen/TODO.md``).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Callable, List, Optional, Tuple

from opencivil.core.berechnung import Eingabebezug, Eingaben
from opencivil.core.einheiten import M, MIO_MM3, MIO_MM4, Groesse
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert
from opencivil.querschnitt.analyse import Querschnittsanalyse
from opencivil.querschnitt.biegung import EINACHSIG, SCHIEF, Biegung

#: Teiler der Hoehe in Biegerichtung im Beiwert: unter Biegung zaehlt bei
#: Platten und Rechtecken ein Drittel der Hoehe, unter Zug die kleinste
#: Abmessung des gezogenen Teils, bei der Platte also die ganze Dicke.
#: SIA 262:2025, 4.4.1.3.
MOMENTENTEILER = 3.0

#: Woher ``k_t`` und ``f_ct,eff`` kommen -- fuer jeden Nachweis dieselbe Stelle.
REFERENZ_BEIWERT = "SIA 262:2025, 4.4.1.3, (100)"
REFERENZ_ZUGFESTIGKEIT = "SIA 262:2025, 4.4.1.3, (99)"

#: Warum die Vorspannung den Riss verschiebt: die Rissbeanspruchung darf sie
#: beruecksichtigen, und unter Gebrauchslast zaehlt eine vorhandene
#: Druckspannung.
REFERENZ_VORSPANNUNG = "SIA 262:2025, 4.3.1.2; 4.4.3.2.4"

#: Groesste rissaktive Dicke unter Zug, in m -- wo die Begrenzung eingeschaltet
#: ist: massige Bauteile, je gezogenem Rand 250 mm (SIA 262:2025, 4.4.2.3.7).
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
    h: Wert, f_ctm: Wert, teiler: float, titel: str = "Beiwert für die Plattendicke",
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
             titel=titel, referenz=REFERENZ_BEIWERT, empirisch={"h": M},
             name="Beiwert für die Dicke")
    wirksam = werte.spannung("f_ct_eff", "f_{ct,eff}", f_ct_eff, stellen=2)
    p.formel(wirksam, r"@k_t \cdot @f_ctm", {"k_t": beiwert, "f_ctm": f_ctm},
             titel="Wirksame Zugfestigkeit", referenz=REFERENZ_ZUGFESTIGKEIT)
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
    die Eingaben ``h``, ``b`` und ``f_ctm``; ``referenz`` ist die Stelle des
    Nachweises, der die Rissbeanspruchung braucht -- 4.3.1.2 beim spröden
    Versagen, Tabelle 17 bei der Zwängung.
    """
    f_ct_eff = protokoll_zugfestigkeit(
        p, Zwischenwerte(basis), k_t=g.k_t, f_ct_eff=g.f_ct_eff, h=e["h"],
        f_ctm=e["f_ctm"], teiler=MOMENTENTEILER)
    p.formel(rissmoment_wert(basis, g), r"@f_ct_eff \cdot \frac{@h^{2} \cdot @b}{6}",
             {"f_ct_eff": f_ct_eff, "h": e["h"], "b": e["b"]},
             titel="Rissmoment des ungerissenen Querschnitts", referenz=referenz)


# ===========================================================================
# Der Bruttoquerschnitt -- gezeichnet oder das Rechteck der Platte
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
class Druckglied:
    """Ein Spannglied mit Vordehnung: seine Kraft drueckt den Beton an seiner Stelle."""

    name: str
    P: float
    """Die Spannkraft nach allen Verlusten, N."""

    P_id: str
    y: float
    z: float
    """Seine Lage vom Schwerpunkt aus, m."""


@dataclass(frozen=True)
class Vorspannung:
    """
    Was die Spannglieder mit Vordehnung am Bruttoquerschnitt wecken -- siehe
    Dateikopf: Normalkraft und Momente ihrer Kraefte, als Druck an ihrer
    Stelle, in SI, Zug positiv, die Momente wie eine Einwirkung.
    """

    glieder: Tuple[Druckglied, ...]
    A: float
    A_id: str

    @property
    def N(self) -> float:
        return -sum(g.P for g in self.glieder)

    @property
    def M_y(self) -> float:
        # M_y = -Σ F·z' mit der Kraft F = -P, die das Glied auf den Beton gibt.
        return sum(g.P * g.z for g in self.glieder)

    @property
    def M_z(self) -> float:
        return sum(g.P * g.y for g in self.glieder)

    @property
    def ids(self) -> Tuple[str, ...]:
        """Was ihre Herleitung liest (:func:`protokoll_vorspannung`): Flaeche und Spannkraefte."""
        return (self.A_id,) + tuple(g.P_id for g in self.glieder)


@dataclass(frozen=True)
class Bruttoquerschnitt:
    """
    Der ungerissene Bruttoquerschnitt ohne Stahl: Traegheitsmomente um den
    Schwerpunkt und die Ecken des Betons -- in SI. Dazu die Vorspannung, wo
    ein Spannglied mit Vordehnung den Beton drueckt.
    """

    I_y: float
    I_z: float
    I_yz: float
    ecken: Tuple[Ecke, ...]
    biegung: Biegung = SCHIEF
    """Ob die Nulllinie kippt oder waagrecht bleibt -- wie die Analyse rechnet."""

    vorspannung: Optional[Vorspannung] = None

    def traegheit(self, um_y: bool) -> float:
        """
        Wie stark sich der Querschnitt unter reiner Biegung um eine Achse
        kruemmt, als Traegheitsmoment, m⁴: «einachsig» ``I`` um diese Achse.
        Kippt die Nulllinie, kruemmt er sich senkrecht zur Achse staerker,
        als ``I`` allein sagt -- wie einer mit ``I - I_yz²/I_quer``. Sonst
        zeigte ein ungerissener unsymmetrischer Querschnitt schon seiner Form
        wegen einen kleineren Modul. Der aequivalente Modul jeder
        Spannung-Dehnung-Analyse misst sich daran, mit Beton wie ohne.
        """
        I, quer = (self.I_y, self.I_z) if um_y else (self.I_z, self.I_y)
        return I if self.biegung.einachsig else I - self.I_yz ** 2 / quer

    def ausdehnung(self, um_y: bool) -> Tuple[float, float]:
        """Die Hoehe in Biegerichtung und die Breite quer dazu, in m -- aus der Zeichnung."""
        breite_y = (max(e.punkt[0] for e in self.ecken) - min(e.punkt[0] for e in self.ecken)) * 1e-3
        hoehe_z = (max(e.punkt[1] for e in self.ecken) - min(e.punkt[1] for e in self.ecken)) * 1e-3
        return (hoehe_z, breite_y) if um_y else (breite_y, hoehe_z)

    def einheitsspannung(self, ecke: Ecke, M_y: float, M_z: float) -> float:
        """
        Die Spannung an der Ecke beim Moment ``(M_y, M_z)``, Zug positiv -- bei
        einem Moment von eins in dieser Richtung die Einheitsspannung.
        Einachsig bleibt die Nulllinie parallel zur Achse der Biegung, ohne
        ``I_yz``.
        """
        if self.biegung.einachsig:
            return -(M_y * ecke.z / self.I_y + M_z * ecke.y / self.I_z)
        nenner = self.I_y * self.I_z - self.I_yz * self.I_yz
        return -(M_y * (self.I_z * ecke.z - self.I_yz * ecke.y)
                 + M_z * (self.I_y * ecke.y - self.I_yz * ecke.z)) / nenner

    def vorspannung_an(self, ecke: Ecke) -> float:
        """
        Die Spannung, die die Vorspannung an der Ecke weckt, Zug positiv --
        null ohne sie. Einachsig zaehlt ihr Moment um z nicht, wie bei jeder
        Einwirkung.
        """
        v = self.vorspannung
        if v is None:
            return 0.0
        return v.N / v.A + self.einheitsspannung(ecke, *self.biegung.wirkt(v.M_y, v.M_z))


def rissbezuege(analyse: Querschnittsanalyse) -> List[Eingabebezug]:
    """
    Was der Bruttoquerschnitt liest, ueber die Grundbezuege hinaus: die
    Traegheitsmomente und die Flaeche -- an ihr misst sich die Vorspannung.
    """
    return [Eingabebezug(k, analyse.id_von(k)) for k in ("I_y", "I_z", "I_yz", "A")]


def bruttoquerschnitt(analyse: Querschnittsanalyse,
                      wert: Callable[[str], float]) -> Bruttoquerschnitt:
    """
    Der Bruttoquerschnitt eines gezeichneten Querschnitts. ``wert`` liefert
    zu einer Wert-ID die Zahl in SI -- aus den Eingaben eines Nachweises mit
    :func:`rissbezuege` (:meth:`~opencivil.core.berechnung.Eingaben.si_nach_id`)
    oder aus einer Loesung.
    """
    y_S, z_S = wert(analyse.id_von("y_S")), wert(analyse.id_von("z_S"))
    return Bruttoquerschnitt(
        I_y=wert(analyse.id_von("I_y")), I_z=wert(analyse.id_von("I_z")),
        I_yz=wert(analyse.id_von("I_yz")),
        ecken=tuple(Ecke(y=p[0] * 1e-3 - y_S, z=p[1] * 1e-3 - z_S, punkt=p, stoff=stoff,
                         f_ctm=abs(wert(stoff.id_von("f_ctm"))))
                    for p, stoff in analyse.beton_ecken),
        biegung=analyse.biegung, vorspannung=_vorspannung(analyse, wert, y_S, z_S))


def _vorspannung(analyse: Querschnittsanalyse, wert: Callable[[str], float],
                 y_S: float, z_S: float) -> Optional[Vorspannung]:
    """Die Vorspannung der Analyse -- ``None`` ohne Glied mit Vordehnung."""
    kraefte = analyse.glieder.spannkraefte() if analyse.glieder is not None else []
    if not kraefte:
        return None
    A_id = analyse.id_von("A")
    return Vorspannung(
        glieder=tuple(Druckglied(name=g.name, P=wert(P_id), P_id=P_id,
                                 y=g.von[0] * 1e-3 - y_S, z=g.von[1] * 1e-3 - z_S)
                      for g, P_id in kraefte),
        A=wert(A_id), A_id=A_id)


def bruttoquerschnitt_rechteck(*, h: float, b: float, stoff: Any,
                               f_ctm: float) -> Bruttoquerschnitt:
    """
    Der Bruttoquerschnitt der Platte: das Rechteck ``b × h`` aus ihrem Beton,
    um seinen Schwerpunkt, einachsig -- fuer ihre Spannung-Dehnung-Analyse.
    Alles in SI.
    """
    ecken = tuple(Ecke(y=y, z=z, punkt=(y * 1e3, z * 1e3), stoff=stoff, f_ctm=f_ctm)
                  for y in (-b / 2.0, b / 2.0) for z in (-h / 2.0, h / 2.0))
    return Bruttoquerschnitt(I_y=b * h ** 3 / 12.0, I_z=h * b ** 3 / 12.0, I_yz=0.0,
                             ecken=ecken, biegung=EINACHSIG)


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

    sigma_p: float = 0.0
    """Die Spannung aus der Vorspannung an der Ecke, Pa -- null ohne sie."""


def rissmoment(q: Bruttoquerschnitt, M_y: float, M_z: float) -> Rissmoment:
    """
    Das Rissmoment in der Richtung ``(M_y, M_z)`` -- einem Moment von eins:
    das Moment unter reiner Biegung, bei dem ``f_ct,eff`` zum ersten Mal
    irgendwo erreicht wird. Es reisst die Ecke, die dafuer das kleinste
    Moment braucht: bei mehreren Betonen die mit der groessten Spannung,
    gemessen an ihrer Zugfestigkeit, mit Vorspannung die, an der ihr Druck
    am wenigsten aufzuheben ist.
    """
    hoehe, _ = q.ausdehnung(M_y != 0.0)
    k_t = beiwert_dicke(rissaktive_dicke(h=hoehe, zug=False))
    gezogen = [(ecke, q.einheitsspannung(ecke, M_y, M_z)) for ecke in q.ecken]
    ecke, sigma = min((es for es in gezogen if es[1] > 0.0),
                      key=lambda es: (k_t * es[0].f_ctm - q.vorspannung_an(es[0])) / es[1])
    W = 1.0 / sigma
    f_ct_eff = k_t * ecke.f_ctm
    sigma_p = q.vorspannung_an(ecke)
    return Rissmoment(ecke=ecke, W=W, hoehe=hoehe, k_t=k_t, f_ct_eff=f_ct_eff,
                      M_Riss=(f_ct_eff - sigma_p) * W, sigma_p=sigma_p)


@dataclass(frozen=True)
class Rissnormalkraft:
    """Die Rissnormalkraft bei einem Moment -- und woraus sie entsteht."""

    ecke: Ecke
    """Die Ecke, die zuerst ihre Zugfestigkeit erreicht."""

    sigma_M: float
    """Die Spannung, die das Moment allein an ihr weckt, Pa."""

    f_ct_eff: float
    N_Riss: float
    """in N."""

    sigma_p: float = 0.0
    """Die Spannung aus der Vorspannung an der Ecke, Pa -- null ohne sie."""


def rissnormalkraft(q: Bruttoquerschnitt, M_y: float, M_z: float, *,
                    k_t: float, A: float) -> Rissnormalkraft:
    """
    Die Zugkraft, bei der der ungerissene Bruttoquerschnitt beim Moment
    ``(M_y, M_z)`` -- in Nm, nicht von eins -- zum ersten Mal irgendwo
    ``f_ct,eff = k_t·f_ctm`` erreicht: ``N_Riss = (f_ct,eff - σ_p - σ_M)·A``
    an der Ecke, an der das am wenigsten Zug braucht, mit der Spannung
    ``σ_p`` aus der Vorspannung. ``k_t`` gilt fuer die rissaktive Dicke unter
    Zug (:func:`rissaktive_dicke`).
    """
    def an(ecke: Ecke) -> Tuple[float, Ecke, float, float, float]:
        sigma = q.einheitsspannung(ecke, M_y, M_z)
        f_ct_eff = k_t * ecke.f_ctm
        sigma_p = q.vorspannung_an(ecke)
        return (f_ct_eff - sigma_p - sigma) * A, ecke, sigma, f_ct_eff, sigma_p

    N_Riss, ecke, sigma, f_ct_eff, sigma_p = min((an(ecke) for ecke in q.ecken),
                                                 key=lambda t: t[0])
    return Rissnormalkraft(ecke=ecke, sigma_M=sigma, f_ct_eff=f_ct_eff, N_Riss=N_Riss,
                           sigma_p=sigma_p)


def protokoll_spannung_ungerissen(p: Protokoll, biegung: Biegung) -> None:
    """Wie der ungerissene Querschnitt Spannung traegt -- der Ansatz des Rissmoments."""
    if biegung.einachsig:
        p.ansatz(r"\sigma(z) = -\frac{M_y \cdot z'}{I_y} \qquad z' = z - z_S",
                 titel="Spannung im ungerissenen Querschnitt, Nulllinie waagrecht")
        return
    p.ansatz(r"\sigma(y, z) = -\frac{M_y\,(I_z z' - I_{yz} y') + "
             r"M_z\,(I_y y' - I_{yz} z')}{I_y I_z - I_{yz}^2}"
             r"\qquad y' = y - y_S,\ z' = z - z_S",
             titel="Spannung im ungerissenen Querschnitt")


def protokoll_traegheit(p: Protokoll, werte: Zwischenwerte, q: Bruttoquerschnitt, um_y: bool,
                        I: Wert, *, name: str, symbol: str, titel: str) -> Wert:
    """
    :meth:`Bruttoquerschnitt.traegheit` in die Herleitung, unter ``name`` und
    ``symbol``: einachsig ``I`` selbst, gekippt ``I - I_yz²/I_quer``.
    """
    bezug = werte.wert(name, symbol, Groesse.aus_si(q.traegheit(um_y), MIO_MM4), stellen=1)
    if q.biegung.einachsig:
        p.wert(bezug, titel=titel)
        return bezug
    quer = werte.wert("I_quer", "I_z" if um_y else "I_y",
                      Groesse.aus_si(q.I_z if um_y else q.I_y, MIO_MM4), stellen=1)
    p.formel(bezug, r"@I - \frac{@Iyz^{2}}{@quer}",
             {"I": I, "Iyz": werte.wert("Iyz", "I_{yz}", Groesse.aus_si(q.I_yz, MIO_MM4), 1),
              "quer": quer},
             titel=f"{titel}, Nulllinie gekippt")
    return bezug


def protokoll_ecke(p: Protokoll, ecke: Ecke) -> None:
    """Welche Ecke zuerst reisst -- in der Zeichnung, mit ihrem Beton."""
    p.text(f"Gezogenster Betonpunkt: y = {ecke.punkt[0]:g} mm, z = {ecke.punkt[1]:g} mm "
           f"({ecke.stoff.name}).")


def protokoll_widerstandsmoment(p: Protokoll, werte: Zwischenwerte, q: Bruttoquerschnitt,
                                ecke: Ecke, W: float, M_y: float, M_z: float) -> Wert:
    """
    ``W = 1/σ`` an der Ecke bei einem Moment von eins in der Richtung
    ``(M_y, M_z)``, um y -- einachsig ``I_y/v``, sonst mit ``I_yz``.
    """
    W = werte.wert("W", "W", Groesse.aus_si(W, MIO_MM3), 2)
    I_y = werte.wert("Iy", "I_y", Groesse.aus_si(q.I_y, MIO_MM4), 1)
    if q.biegung.einachsig:
        p.formel(W, r"\frac{@Iy}{@v}", {
            "Iy": I_y,
            "v": werte.laenge("v", "v", -M_y * ecke.z, "Abstand des gezogenen Rands vom Schwerpunkt"),
        }, titel="Widerstandsmoment zum gezogenen Rand, Nulllinie waagrecht")
    else:
        p.formel(W, _w_vorlage(M_y, M_z), {
            "Iy": I_y,
            "Iz": werte.wert("Iz", "I_z", Groesse.aus_si(q.I_z, MIO_MM4), 1),
            "Iyz": werte.wert("Iyz", "I_{yz}", Groesse.aus_si(q.I_yz, MIO_MM4), 1),
            "y": werte.laenge("y", "y'", ecke.y),
            "z": werte.laenge("z", "z'", ecke.z),
        }, titel="Widerstandsmoment zum gezogensten Betonpunkt")
    return W


def protokoll_vorspannung(p: Protokoll, werte: Zwischenwerte, q: Bruttoquerschnitt,
                          ecke: Ecke, ein: Callable[[str], Wert]) -> Optional[Wert]:
    """
    Die Spannung ``σ_p``, die die Vorspannung an der Ecke weckt, hergeleitet
    -- ``None`` ohne sie. ``ein`` liefert zu einer Wert-ID den Wert: die
    Spannkraefte und die Flaeche.
    """
    v = q.vorspannung
    if v is None:
        return None
    p.erklaerung(
        "Die Spannglieder mit Vordehnung drücken den Beton schon ohne Last, je mit "
        "ihrer Kraft nach allen Verlusten an ihrer Stelle: am Bruttoquerschnitt eine "
        "Normalkraft und ein Moment. Ihre Spannung an der Ecke, die reisst, kommt zu der "
        "aus der Einwirkung.")
    mehrere = len(v.glieder) > 1
    kraefte = {f"P{i}": ein(g.P_id) for i, g in enumerate(v.glieder)}
    N_p = werte.kraft("N_p", "N_p", v.N, "Normalkraft aus der Vorspannung, Druck negativ")
    p.formel(N_p, "-" + _summe([f"@P{i}" for i in range(len(v.glieder))]), kraefte,
             titel="Normalkraft aus der Vorspannung", referenz=REFERENZ_VORSPANNUNG)
    momente = {}
    for achse, M in q.biegung.momente(v.M_y, v.M_z):
        quer = "z" if achse == "y" else "y"
        abstaende = {f"a{i}": werte.laenge(
            f"{quer}_p{i + 1}", rf"{quer}'_{{p{f',{i + 1}' if mehrere else ''}}}",
            getattr(g, quer), f"Lage von {g.name}, vom Schwerpunkt aus")
            for i, g in enumerate(v.glieder)}
        momente[achse] = werte.moment(f"M_p_{achse}", f"M_{{p,{achse}}}", M,
                                      f"Moment aus der Vorspannung um {achse}")
        p.formel(momente[achse],
                 _summe([rf"@P{i} \cdot @a{i}" for i in range(len(v.glieder))]),
                 {**kraefte, **abstaende}, titel=f"Moment aus der Vorspannung um {achse}",
                 referenz=REFERENZ_VORSPANNUNG, name="Moment aus der Vorspannung")
    sigma_p = werte.spannung("sigma_p", r"\sigma_p", q.vorspannung_an(ecke),
                             "aus der Vorspannung, an der Ecke", stellen=2)
    traeg = lambda kurz, symbol, si, was: werte.wert(kurz, symbol, Groesse.aus_si(si, MIO_MM4), 1,
                                                     f"{was} des Bruttoquerschnitts")
    teile = {"N": N_p, "A": ein(v.A_id), "Iy": traeg("Iy", "I_y", q.I_y, "Trägheitsmoment um y"),
             "z": werte.laenge("z", "z'", ecke.z, "Lage der Ecke, vom Schwerpunkt aus")}
    titel = "Spannung aus der Vorspannung an der Ecke"
    if q.biegung.einachsig:
        p.formel(sigma_p, r"\frac{@N}{@A} - \frac{@My \cdot @z}{@Iy}",
                 {**teile, "My": momente["y"]}, titel=titel, referenz=REFERENZ_VORSPANNUNG)
        return sigma_p
    p.formel(sigma_p,
             r"\frac{@N}{@A} - \frac{@My\,(@Iz \cdot @z - @Iyz \cdot @y)"
             r" + @Mz\,(@Iy \cdot @y - @Iyz \cdot @z)}{@Iy \cdot @Iz - @Iyz^{2}}",
             {**teile, "My": momente["y"], "Mz": momente["z"],
              "Iz": traeg("Iz", "I_z", q.I_z, "Trägheitsmoment um z"),
              "Iyz": traeg("Iyz", "I_{yz}", q.I_yz, "Deviationsmoment"),
              "y": werte.laenge("y", "y'", ecke.y, "Lage der Ecke, vom Schwerpunkt aus")},
             titel=titel, referenz=REFERENZ_VORSPANNUNG)
    return sigma_p


def _summe(teile: List[str]) -> str:
    """Eine Summe in einer Vorlage -- geklammert, sobald es mehr als ein Glied ist."""
    return teile[0] if len(teile) == 1 else r"\left(" + " + ".join(teile) + r"\right)"


def protokoll_rissmoment(p: Protokoll, e: Eingaben, analyse: Querschnittsanalyse,
                         werte: Zwischenwerte, q: Bruttoquerschnitt, riss: Rissmoment,
                         M_y: float, M_z: float, *, referenz: str) -> Wert:
    """
    Die Herleitung von :func:`rissmoment` -- zurueck kommt ``M_Riss``.
    ``referenz`` wie bei :func:`protokoll_rissmoment_rechteck`.
    """
    ecke = riss.ecke
    protokoll_ecke(p, ecke)
    h = werte.laenge("h", "h", riss.hoehe)
    f_ct_eff = protokoll_zugfestigkeit(
        p, werte, k_t=riss.k_t, f_ct_eff=riss.f_ct_eff, h=h,
        f_ctm=e[ecke.stoff.eingabename("f_ctm")], teiler=MOMENTENTEILER,
        titel="Beiwert für die Höhe in Biegerichtung")
    W = protokoll_widerstandsmoment(p, werte, q, ecke, riss.W, M_y, M_z)
    M_Riss = werte.moment("M_Riss", "M_{Riss}", riss.M_Riss)
    sigma_p = protokoll_vorspannung(p, werte, q, ecke, e.nach_id())
    if sigma_p is None:
        p.formel(M_Riss, r"@f \cdot @W", {"f": f_ct_eff, "W": W},
                 titel="Rissmoment des ungerissenen Querschnitts", referenz=referenz)
    else:
        p.formel(M_Riss, r"\left(@f - @sp\right) \cdot @W",
                 {"f": f_ct_eff, "sp": sigma_p, "W": W},
                 titel="Rissmoment des ungerissenen, vorgespannten Querschnitts",
                 referenz=referenz)
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
