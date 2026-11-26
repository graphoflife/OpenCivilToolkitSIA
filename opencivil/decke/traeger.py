"""
opencivil/decke/traeger.py -- ein Streifen als Durchlaufträger.

VERANTWORTUNG:
Ein Streifen der Decke ist ein Balken über seine Lager. Hier wird er
gerechnet, in zwei Schritten:

1. **Elastisch**, mit den Lagern als Punkten: die Lagerkräfte eines statisch
   unbestimmten Streifens folgen aus der Biegelinie -- mit den Elementen des
   Stabwerks (:mod:`opencivil.stabwerk.stab`), Knoten an den Lagern und wo
   die Steifigkeit wechselt. Zwischen den Knoten ist die Hermite-Biegelinie
   die genaue Lösung; die Lagerkräfte stimmen exakt. Über das erste und das
   letzte Lager hinaus ragt der Streifen frei: dort ist er statisch
   bestimmt, und seine Last geht als Kraft und Moment an das Lager.
2. **Statik**: mit diesen Lagerkräften laufen Querkraft und Moment vom
   Anfang des Streifens bis zu seinem Ende, gerechnet wie in einem ebenen
   Stab des Stabwerks, starr (:func:`statik`). Ein Flächenlager -- ein
   versteckter Unterzug, eine Stütze -- drückt dabei nicht in einem Punkt,
   sondern gleichmässig über seine Breite; so steht es in der Vorlesung
   («Flächenlager mit gleichmässiger Pressung», Stahlbeton II, 7.2 Platten,
   Folie 33), und so rechnet die Musterlösung des Kolloquiums 4 ihr
   Stützmoment von −10.9 auf −7.3 kNm/m herunter.

VORZEICHEN:
``s`` läuft vom Anfang des Trägers, in m. Lasten wirken nach unten und
sind dann positiv, Lagerkräfte nach oben, Lagermomente im
Gegenuhrzeigersinn. ``M > 0`` zieht unten (Feldmoment), ``V = dM/ds``::

    M(s) = Σ_links [F_k · (s − s_k) − C_k] − ∫_links p(σ) · (s − σ) dσ

Am Ende eines Trägers sind V und M null -- eine Probe, die
:func:`statik` macht.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple, Union

from opencivil.stabwerk import stab as st
from opencivil.stabwerk.matrix import Profilmatrix, Zerlegung
from opencivil.stabwerk.verlauf import EbenesIntervall, ebener_verlauf

#: Was in m als dieselbe Stelle gilt.
GLEICH = 1e-9

#: Ein Wechsel der Steifigkeit näher als so viel an einem anderen Knoten gilt
#: dort, in m. Als eigenes Element zwischen freien Knoten wäre ein so kurzes
#: Stück fast starr: sein Pivot fiele unter die Schranke der Zerlegung
#: (:data:`~opencivil.stabwerk.matrix.SCHRANKE`), und sie hielte den Knoten
#: still fest wie ein Lager, das es nicht gibt -- bei 1 mm zwischen zwei
#: Wechseln schon. So schmal wirkt ein Wechsel auf die Lagerkräfte kaum;
#: die 1 cm sind nach Vorgabe, nicht nachgeschlagen.
WECHSEL = 1e-2


@dataclass(frozen=True)
class Streckenlast:
    """Eine Last je Länge, linear von ``a`` nach ``b``, in N/m -- nach unten positiv."""

    a: float
    b: float
    p_a: float
    p_b: float

    def bei(self, s: float) -> float:
        if self.b <= self.a:
            return self.p_a
        return self.p_a + (s - self.a) / (self.b - self.a) * (self.p_b - self.p_a)

    @property
    def summe(self) -> float:
        return 0.5 * (self.p_a + self.p_b) * (self.b - self.a)

    def mal(self, faktor: float) -> "Streckenlast":
        return Streckenlast(self.a, self.b, self.p_a * faktor, self.p_b * faktor)

    def verschoben(self, um: float) -> "Streckenlast":
        return Streckenlast(self.a + um, self.b + um, self.p_a, self.p_b)


@dataclass(frozen=True)
class Einzellast:
    """Eine Kraft in N an der Stelle ``a`` (nach unten positiv) und ein Moment ``C`` in Nm (Gegenuhrzeigersinn)."""

    a: float
    P: float = 0.0
    C: float = 0.0

    def mal(self, faktor: float) -> "Einzellast":
        return Einzellast(self.a, self.P * faktor, self.C * faktor)

    def verschoben(self, um: float) -> "Einzellast":
        return Einzellast(self.a + um, self.P, self.C)


Teillast = Union[Streckenlast, Einzellast]


@dataclass(frozen=True)
class Halt:
    """Ein Lager am Träger, als Punkt: ``vertikal`` hält die Höhe, ``eingespannt`` die Drehung."""

    s: float
    vertikal: bool
    eingespannt: bool


def stabil(halte: Sequence[Halt]) -> bool:
    """
    Ob die Lager den Träger halten: zwei Höhenlager an verschiedenen
    Stellen -- oder eines und eine Einspannung.
    """
    hoehen = sorted(h.s for h in halte if h.vertikal)
    verschieden = bool(hoehen) and hoehen[-1] - hoehen[0] > GLEICH
    return verschieden or (bool(hoehen) and any(h.eingespannt for h in halte))


class Balken:
    """
    Der elastische Durchlaufträger: Knoten, Elemente, die zerlegte
    Steifigkeitsmatrix -- einmal gebaut, für jeden Fall nur noch gelöst.
    """

    def __init__(self, L: float, abschnitte: Sequence[Tuple[float, float, float]],
                 halte: Sequence[Halt]) -> None:
        """
        ``abschnitte``: ``(von, bis, EI)`` in m und Nm², lückenlos von 0 bis
        ``L``. Knoten stehen an den Lagern und dazwischen, wo die Steifigkeit
        wechselt (:data:`WECHSEL`) -- nicht an den freien Enden: bis
        2026-11-26 war jedes ein Element, und eines von einem Mikrometer, ein
        Lager knapp neben dem Rand der Platte, hielt die Zerlegung still fest.
        Die Probe des Gleichgewichts hielt dann die ganze Decke an.
        """
        self.L = L
        self.halte = list(halte)
        self.knoten: List[float] = []
        for s in sorted(min(max(h.s, 0.0), L) for h in halte) or [0.0, L]:
            if not self.knoten or s - self.knoten[-1] > GLEICH:
                self.knoten.append(s)
        erstes, letztes = self.knoten[0], self.knoten[-1]
        for (_, g, links), (_, _, rechts) in zip(abschnitte, abschnitte[1:]):
            if links != rechts and erstes < g < letztes and all(abs(g - k) > WECHSEL for k in self.knoten):
                self.knoten.append(g)
        self.knoten.sort()
        self.elemente: List[Tuple[int, float]] = []
        for i, (a, b) in enumerate(zip(self.knoten, self.knoten[1:])):
            mitte = 0.5 * (a + b)
            EI = next((e for von, bis, e in abschnitte if von - GLEICH <= mitte <= bis + GLEICH),
                      abschnitte[0][2])
            self.elemente.append((i, EI))
        gehalten = set()
        for h in halte:
            k = self.knoten_bei(h.s)
            if h.vertikal:
                gehalten.add(2 * k)
            if h.eingespannt:
                gehalten.add(2 * k + 1)
        self._nummer: Dict[int, int] = {}
        for f in range(2 * len(self.knoten)):
            if f not in gehalten:
                self._nummer[f] = len(self._nummer)
        self.stabil = stabil(halte)
        self._zerlegung: Optional[Zerlegung] = None
        if self.stabil:
            gruppen = [[self._nummer[f] for f in range(2 * i, 2 * i + 4) if f in self._nummer]
                       for i, _ in self.elemente]
            K = Profilmatrix.aus_gruppen(len(self._nummer), gruppen)
            for i, EI in self.elemente:
                k = self._steifigkeit(i, EI)
                for p, f in enumerate(range(2 * i, 2 * i + 4)):
                    for q, g in enumerate(range(2 * i, 2 * i + 4)):
                        if f in self._nummer and g in self._nummer and self._nummer[g] <= self._nummer[f]:
                            K.addiere(self._nummer[f], self._nummer[g], k[p][q])
            self._zerlegung = Zerlegung(K)

    def knoten_bei(self, s: float) -> int:
        return min(range(len(self.knoten)), key=lambda i: abs(self.knoten[i] - s))

    def _steifigkeit(self, i: int, EI: float) -> List[List[float]]:
        """Der Biegeteil der Stabsteifigkeit: ``v1, θ1, v2, θ2``."""
        k = st.steifigkeit(self.knoten[i + 1] - self.knoten[i], 1.0, EI)
        stellen = (1, 2, 4, 5)
        return [[k[p][q] for q in stellen] for p in stellen]

    def lagerkraefte(self, lasten: Sequence[Teillast]) -> List[Tuple[float, float]]:
        """
        Je Lager die Kraft nach oben ``F`` und das Moment ``C`` im
        Gegenuhrzeigersinn, die es auf den Träger ausübt -- elastisch, mit
        den Lagern als Punkten.
        """
        if not self.stabil:
            raise ValueError("Der Träger ist beweglich.")
        stablasten = [st.Strecke(l.a, l.b, py_a=-l.p_a, py_b=-l.p_b) if isinstance(l, Streckenlast)
                      else st.Punkt(l.a, Py=-l.P, M=l.C) for l in lasten]
        # Die freien Enden: ihre Last als Kraft und Moment am ersten und am
        # letzten Lager. Eine Einzellast auf dem letzten gehört dem Ende.
        knotenlast = [0.0] * (2 * len(self.knoten))
        for k, von, bis, ende in ((0, 0.0, self.knoten[0], False),
                                  (len(self.knoten) - 1, self.knoten[-1], self.L, True)):
            F, C = _resultante(st.aufteilen(stablasten, von, bis, ende=ende), self.knoten[k] - von)
            knotenlast[2 * k] += F
            knotenlast[2 * k + 1] += C
        f = [0.0] * len(self._nummer)
        for g, w in enumerate(knotenlast):
            if g in self._nummer:
                f[self._nummer[g]] += w
        f_elemente = []
        for i, _ in self.elemente:
            a, b = self.knoten[i], self.knoten[i + 1]
            voll = st.knotenlasten(b - a, st.aufteilen(stablasten, a, b, ende=False))
            fe = [voll[1], voll[2], voll[4], voll[5]]
            f_elemente.append(fe)
            for p, g in enumerate(range(2 * i, 2 * i + 4)):
                if g in self._nummer:
                    f[self._nummer[g]] += fe[p]
        x = self._zerlegung.loese(f) if self._nummer else []
        d = [x[self._nummer[g]] if g in self._nummer else 0.0 for g in range(2 * len(self.knoten))]
        r = [-w for w in knotenlast]
        for (i, EI), fe in zip(self.elemente, f_elemente):
            k = self._steifigkeit(i, EI)
            de = d[2 * i:2 * i + 4]
            for p in range(4):
                r[2 * i + p] += sum(k[p][q] * de[q] for q in range(4)) - fe[p]
        heraus = []
        for h in self.halte:
            k = self.knoten_bei(h.s)
            heraus.append((r[2 * k] if h.vertikal else 0.0, r[2 * k + 1] if h.eingespannt else 0.0))
        return heraus


def _resultante(lasten: Sequence[st.Teillast], x0: float) -> Tuple[float, float]:
    """
    Kraft quer und Moment um ``x0`` -- im Gegenuhrzeigersinn, in den Achsen
    eines ebenen Stabs -- der Lasten eines freien Endes.
    """
    F = C = 0.0
    for l in lasten:
        if isinstance(l, st.Punkt):
            F += l.Py
            C += l.M + (l.a - x0) * l.Py
            continue
        lang, c, zu = l.b - l.a, l.a - x0, l.py_b - l.py_a
        F += 0.5 * (l.py_a + l.py_b) * lang
        C += lang * (l.py_a * (lang / 2.0 + c) + zu * (lang / 3.0 + c / 2.0) + 0.5 * (l.m_a + l.m_b))
    return F, C


# ===========================================================================
# Statik
# ===========================================================================


def statik(L: float, lasten: Sequence[Teillast]) -> List[EbenesIntervall]:
    """
    Querkraft und Moment längs des Trägers, von links: aus allen Kräften auf
    ihn -- Lasten nach unten, Lagerkräfte als Einzellasten oder Pressungen
    nach oben (negativ). Gerechnet wie ein ebener Stab des Stabwerks, starr
    (:func:`~opencivil.stabwerk.verlauf.ebener_verlauf` mit ``EI = ∞``): die
    Biegelinie braucht hier niemand. Bis 2026-11-20 integrierte die Decke
    Querkraft und Moment ein zweites Mal selbst.

    Was näher als :data:`GLEICH` beieinanderliegt, gilt als eine Stelle --
    der Rand eines Lagers und die Grenze eines Streifens unterscheiden sich
    oft nur in der Rundung. Wirft, wenn am Ende etwas übrig bleibt: dann
    stehen die Kräfte nicht im Gleichgewicht.
    """
    raster = [0.0]
    for s in sorted(s for l in lasten for s in ((l.a, l.b) if isinstance(l, Streckenlast) else (l.a,))):
        if s - raster[-1] > GLEICH and L - s > GLEICH:
            raster.append(s)
    raster.append(L)

    def eingerastet(s: float) -> float:
        return min(raster, key=lambda r: abs(r - s))

    # In den Achsen eines ebenen Stabs: quer nach oben positiv, Momente im
    # Gegenuhrzeigersinn -- die Lasten der Decke wirken nach unten.
    stablasten: List[st.Teillast] = []
    for l in lasten:
        if isinstance(l, Einzellast):
            stablasten.append(st.Punkt(eingerastet(l.a), Py=-l.P, M=l.C))
            continue
        a, b = eingerastet(l.a), eingerastet(l.b)
        if b > a:
            stablasten.append(st.Strecke(a, b, py_a=-l.p_a, py_b=-l.p_b))
        elif l.summe:
            stablasten.append(st.Punkt(a, Py=-l.summe))
    teile = ebener_verlauf(L=L, x0=0.0, s=(0.0,) * 6, d=(0.0,) * 6, lasten=stablasten,
                           EI=math.inf, laengs=False)

    # Was am Ende angreift, laesst V und M dort springen -- danach muss
    # nichts uebrig sein.
    am_ende = [l for l in stablasten if isinstance(l, st.Punkt) and l.a == L]
    V = teile[-1].V(L) + sum(l.Py for l in am_ende)
    M = teile[-1].M(L) - sum(l.M for l in am_ende)
    gesamt = sum(abs(l.summe) if isinstance(l, Streckenlast) else abs(l.P) for l in lasten)
    if abs(V) > 1e-6 * max(gesamt, 1.0) or abs(M) > 1e-6 * max(gesamt * max(L, 1.0), 1.0):
        raise ArithmeticError(f"Der Träger steht nicht im Gleichgewicht: am Ende V = {V:.6g} N, "
                              f"M = {M:.6g} Nm.")
    return teile


def wert(teile: Sequence[EbenesIntervall], groesse: str, s: float, links: bool = False) -> float:
    """``V`` oder ``M`` an der Stelle ``s`` -- an einem Sprung rechts davon, mit ``links`` links davon."""
    kandidaten = [t for t in teile if t.x0 - GLEICH <= s <= t.x1 + GLEICH]
    if not kandidaten:
        return 0.0
    teil = kandidaten[0] if links else kandidaten[-1]
    return getattr(teil, groesse)(s)
