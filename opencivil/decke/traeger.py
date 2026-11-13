"""
opencivil/decke/traeger.py -- ein Streifen als Durchlaufträger.

VERANTWORTUNG:
Ein Streifen der Decke ist ein Balken über seine Lager. Hier wird er
gerechnet, in zwei Schritten:

1. **Elastisch**, mit den Lagern als Punkten: die Lagerkräfte eines statisch
   unbestimmten Streifens folgen aus der Biegelinie -- mit den Elementen des
   Stabwerks (:mod:`opencivil.stabwerk.stab`), Knoten an den Enden, den
   Lagern und wo die Steifigkeit wechselt. Zwischen den Knoten ist die
   Hermite-Biegelinie die genaue Lösung; die Lagerkräfte stimmen exakt.
2. **Statik**: mit diesen Lagerkräften laufen Querkraft und Moment vom
   Anfang des Streifens bis zu seinem Ende. Ein Flächenlager -- ein
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

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple, Union

from opencivil.stabwerk import stab as st
from opencivil.stabwerk.matrix import Profilmatrix, Zerlegung
from opencivil.stabwerk.verlauf import NULL, Polynom

#: Was in m als dieselbe Stelle gilt.
GLEICH = 1e-9


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
        """``abschnitte``: ``(von, bis, EI)`` in m und Nm², lückenlos von 0 bis ``L``."""
        self.L = L
        self.halte = list(halte)
        stellen = [0.0, L] + [h.s for h in halte] + [g for a, b, _ in abschnitte for g in (a, b)]
        self.knoten: List[float] = []
        for s in sorted(min(max(s, 0.0), L) for s in stellen):
            if not self.knoten or s - self.knoten[-1] > GLEICH:
                self.knoten.append(s)
        self.knoten[-1] = L
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
        f_elemente = []
        f = [0.0] * len(self._nummer)
        letztes = len(self.elemente) - 1
        for i, _ in self.elemente:
            a, b = self.knoten[i], self.knoten[i + 1]
            teil = st.aufteilen(stablasten, a, b, ende=i == letztes)
            voll = st.knotenlasten(b - a, teil)
            fe = [voll[1], voll[2], voll[4], voll[5]]
            f_elemente.append(fe)
            for p, g in enumerate(range(2 * i, 2 * i + 4)):
                if g in self._nummer:
                    f[self._nummer[g]] += fe[p]
        x = self._zerlegung.loese(f)
        d = [x[self._nummer[g]] if g in self._nummer else 0.0 for g in range(2 * len(self.knoten))]
        r = [0.0] * (2 * len(self.knoten))
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


# ===========================================================================
# Statik
# ===========================================================================


@dataclass(frozen=True)
class Stueck:
    """Ein Stück des Trägers ohne Laststelle: Querkraft, Moment und Last als Polynome in ``s``."""

    a: float
    b: float
    V: Polynom
    M: Polynom
    p: Polynom
    """Die Last nach unten, samt Pressung der Flächenlager (negativ)."""


def statik(L: float, lasten: Sequence[Teillast]) -> List[Stueck]:
    """
    Querkraft und Moment längs des Trägers, von links: aus allen Kräften
    auf ihn -- Lasten nach unten, Lagerkräfte als Einzellasten oder
    Pressungen nach oben (negativ). Wirft, wenn am Ende etwas übrig bleibt:
    dann stehen die Kräfte nicht im Gleichgewicht.
    """
    stellen = [0.0, L]
    for l in lasten:
        stellen.extend((l.a, l.b) if isinstance(l, Streckenlast) else (l.a,))
    raster: List[float] = []
    for s in sorted(stellen):
        if not raster or s - raster[-1] > GLEICH:
            raster.append(s)

    def eingerastet(s: float) -> float:
        return min(raster, key=lambda r: abs(r - s))

    punkte: Dict[float, Tuple[float, float]] = {}
    strecken: List[Streckenlast] = []
    for l in lasten:
        if isinstance(l, Einzellast):
            s = eingerastet(l.a)
            P, C = punkte.get(s, (0.0, 0.0))
            punkte[s] = (P + l.P, C + l.C)
        else:
            a, b = eingerastet(l.a), eingerastet(l.b)
            if b > a:
                strecken.append(Streckenlast(a, b, l.p_a, l.p_b))
            elif l.summe:
                s = a
                P, C = punkte.get(s, (0.0, 0.0))
                punkte[s] = (P + l.summe, C)
    V0 = M0 = 0.0
    P, C = punkte.get(raster[0], (0.0, 0.0))
    V0, M0 = V0 - P, M0 - C
    heraus: List[Stueck] = []
    for xa, xb in zip(raster, raster[1:]):
        p = NULL
        for l in strecken:
            if l.a <= xa + GLEICH and l.b >= xb - GLEICH:
                p = p + Polynom.durch(l.a, l.p_a, l.b, l.p_b)
        V = Polynom((V0,)) - p.stammfunktion(xa)
        M = Polynom((M0,)) + V.stammfunktion(xa)
        heraus.append(Stueck(xa, xb, V, M, p))
        P, C = punkte.get(xb, (0.0, 0.0))
        V0, M0 = V(xb) - P, M(xb) - C
    gesamt = sum(abs(l.summe) for l in strecken) + sum(abs(P) for P, _ in punkte.values())
    if abs(V0) > 1e-6 * max(gesamt, 1.0) or abs(M0) > 1e-6 * max(gesamt * max(L, 1.0), 1.0):
        raise ArithmeticError(f"Der Träger steht nicht im Gleichgewicht: am Ende V = {V0:.6g} N, "
                              f"M = {M0:.6g} Nm.")
    return heraus


def wert(stuecke: Sequence[Stueck], groesse: str, s: float, links: bool = False) -> float:
    """``V`` oder ``M`` an der Stelle ``s`` -- an einem Sprung rechts davon, mit ``links`` links davon."""
    kandidaten = [t for t in stuecke if t.a - GLEICH <= s <= t.b + GLEICH]
    if not kandidaten:
        return 0.0
    teil = kandidaten[0] if links else kandidaten[-1]
    return getattr(teil, groesse)(s)


def extreme(stuecke: Sequence[Stueck], groesse: str) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """``((s, kleinster), (s, grösster))`` von ``V`` oder ``M`` -- an Grenzen und wo die Ableitung null ist."""
    werte = []
    for t in stuecke:
        funktion = getattr(t, groesse)
        for s in [t.a, t.b] + funktion.ableitung().nullstellen(t.a, t.b):
            werte.append((s, funktion(s)))
    return min(werte, key=lambda w: w[1]), max(werte, key=lambda w: w[1])
