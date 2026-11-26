"""
opencivil/querschnitt/plastisch.py -- Spannungsbloecke an einer geraden Nulllinie, starr-plastisch.

VERANTWORTUNG:
Was der Stahlquerschnitt (:mod:`opencivil.stahlbau.querschnitt`) und der
Verbundquerschnitt (:mod:`opencivil.verbund.querschnitt`) plastisch teilen,
in mm und N/mm²:

* Polygone mit Gewicht in Gruppen (:class:`Stueck`), je Gruppe ein Werkstoff
  mit seiner Festigkeit -- und die Regel, nach der ein Polygon seinen
  Elternteil dort ersetzt, wo es liegt (:func:`stuecke`);
* an einer Nulllinie (:class:`Linie`) je Gruppe die Spannung ``+zug`` auf der
  gezogenen und ``-druck`` auf der gedrueckten Seite (:class:`Starrplastisch`):
  die Kraefte, je Teil die Bloecke mit ihrem Angriffspunkt, die Nulllinie bei
  einer Normalkraft und der Zustand, dessen Moment in die Richtung einer
  Einwirkung zeigt.

Beim Baustahl sind ``zug`` und ``druck`` gleich, beim Beton im Verbund ist
``zug`` null. Wie weit ein Querschnitt so rechnen darf, sagen die Normen;
hier steht nur die Rechnung, an einer Stelle.

VORZEICHEN:
N > 0 Zug; ``M_y = -∫σ (z - z_b) dA`` zieht unten, ``M_z = -∫σ (y - y_b) dA``
links -- um einen Bezugspunkt ``b``.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from functools import cached_property
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from opencivil.core.suche import illinois, winkel_suchen
from opencivil.querschnitt import geometrie as geo
from opencivil.querschnitt.geometrie import Punkt
from opencivil.querschnitt.interaktion import WINKEL_SCHRANKE
from opencivil.querschnitt.interaktion import Querschnitt as Faserquerschnitt


@dataclass(frozen=True)
class Linie:
    """
    Eine Nulllinie ``n·p = v``, in mm: gezogen, wo ``n·p > v``, gedrueckt, wo
    ``n·p < v`` -- ``n`` zeigt zur gezogenen Seite. Mit ``n = (0, 0)`` liegt
    sie ausserhalb des Querschnitts: dann ist alles gedrueckt
    (:data:`DRUCK`) oder alles gezogen (:data:`ZUG`).
    """

    n: Tuple[float, float]
    v: float

    def d(self, p: Punkt) -> float:
        """Wie weit ``p`` auf der gezogenen Seite liegt -- negativ, wo es gedrueckt ist."""
        return self.n[0] * p[0] + self.n[1] * p[1] - self.v


#: Gleichmaessiger Druck und gleichmaessiger Zug -- ohne Nulllinie im Querschnitt.
DRUCK = Linie((0.0, 0.0), 1.0)
ZUG = Linie((0.0, 0.0), -1.0)


@dataclass(frozen=True)
class Stueck:
    """
    Ein Polygon mit Gewicht in einer Gruppe: +1, wo es liegt, -1 im
    Elternteil, den es dort ersetzt, dazwischen ein Anteil -- so mindert die
    Querkraft einen Steg. ``teil`` ist der Index des Teils, zu dem es zaehlt
    -- bei einer Aussparung der des Teils darum --, ``was`` sagt, wofuer ein
    Streifen weggenommen ist.
    """

    gruppe: int
    gewicht: float
    punkte: Tuple[Punkt, ...]
    teil: int
    was: str = ""

    @cached_property
    def werte(self) -> geo.Flaechenwerte:
        return geo.flaechenwerte(self.punkte)


@dataclass(frozen=True)
class Block:
    """Die Kraft einer Zone eines Teils an einer Nulllinie, in N, und wo sie angreift, in mm."""

    teil: int
    was: str
    zone: str
    """«Zug» oder «Druck»."""

    F: float
    punkt: Punkt


@dataclass(frozen=True)
class Zustand:
    """Der Zustand an einer Nulllinie: was die Bloecke tragen, in N und N·mm um den Bezugspunkt."""

    linie: Linie
    N: float
    M_y: float
    M_z: float


def stuecke(punkte: Sequence[Sequence[Punkt]], eltern: Sequence[Optional[int]],
            gruppe_von: Mapping[int, int], teil_von: Mapping[int, int]) -> List[Stueck]:
    """
    Die Stuecke einer Zeichnung: ein Polygon zaehlt in seiner Gruppe mit +1
    und in der seines Elternteils mit -1 -- so nimmt eine Aussparung den
    Werkstoff darum weg, und ein Polygon aus anderem ersetzt ihn dort. Ein
    Polygon ohne Gruppe in ``gruppe_von`` zaehlt nicht mit: fuer diese
    Gruppen ist es eine Aussparung. ``teil_von`` sagt je Polygon mit
    Gruppe, zu welchem Teil es gehoert.
    """
    ergebnis: List[Stueck] = []
    for i, ecken in enumerate(punkte):
        eigene = gruppe_von.get(i)
        fremde = gruppe_von.get(eltern[i]) if eltern[i] is not None else None
        if eigene == fremde:
            continue
        if eigene is not None:
            ergebnis.append(Stueck(eigene, 1.0, tuple(ecken), teil_von[i]))
        if fremde is not None:
            ergebnis.append(Stueck(fremde, -1.0, tuple(ecken), teil_von[eltern[i]]))
    return ergebnis


def _auf(n: Tuple[float, float], p: Punkt) -> float:
    return n[0] * p[0] + n[1] * p[1]


@dataclass(frozen=True)
class Starrplastisch:
    """
    Stuecke mit ihren Festigkeiten, je Gruppe ``zug`` und ``druck`` als
    Betraege in N/mm² -- siehe Dateikopf.
    """

    stuecke: Tuple[Stueck, ...]
    zug: Tuple[float, ...]
    druck: Tuple[float, ...]

    @property
    def zugkraft(self) -> float:
        """Was der Querschnitt ganz gezogen traegt, in N."""
        return sum(s.gewicht * self.zug[s.gruppe] * s.werte.A for s in self.stuecke)

    @property
    def druckkraft(self) -> float:
        """Was er ganz gedrueckt traegt, als Betrag in N."""
        return sum(s.gewicht * self.druck[s.gruppe] * s.werte.A for s in self.stuecke)

    def kraefte(self, linie: Linie, bezug: Punkt) -> Tuple[float, float, float]:
        """Was die Bloecke an der Nulllinie tragen: ``(N, M_y, M_z)`` in N, N·mm um ``bezug``."""
        N = s_y = s_z = 0.0
        for s in self.stuecke:
            a, y, z = geo.jenseits(s.punkte, linie.n, linie.v)
            w = s.werte
            k_z, k_d = s.gewicht * self.zug[s.gruppe], s.gewicht * self.druck[s.gruppe]
            N += k_z * a - k_d * (w.A - a)
            s_y += k_z * y - k_d * (w.A * w.y_S - y)
            s_z += k_z * z - k_d * (w.A * w.z_S - z)
        return N, -(s_z - bezug[1] * N), -(s_y - bezug[0] * N)

    def bloecke(self, linie: Linie) -> List[Block]:
        """
        Je Teil -- und je weggenommenem Streifen -- die Kraft seiner gezogenen
        und seiner gedrueckten Zone an der Nulllinie, mit Angriffspunkt: die
        Probe zu :meth:`kraefte`, Teil fuer Teil.
        """
        summen: Dict[Tuple[int, str], List[float]] = {}
        for s in self.stuecke:
            a, y, z = geo.jenseits(s.punkte, linie.n, linie.v)
            w = s.werte
            k_z, k_d = s.gewicht * self.zug[s.gruppe], s.gewicht * self.druck[s.gruppe]
            summe = summen.setdefault((s.teil, s.was), [0.0] * 6)
            for i, x in enumerate((k_z * a, k_z * y, k_z * z, -k_d * (w.A - a),
                                   -k_d * (w.A * w.y_S - y), -k_d * (w.A * w.z_S - z))):
                summe[i] += x
        bloecke = []
        for (teil, was), (F_z, y_z, z_z, F_d, y_d, z_d) in summen.items():
            for zone, F, y, z in (("Zug", F_z, y_z, z_z), ("Druck", F_d, y_d, z_d)):
                if abs(F) > 1e-9:
                    bloecke.append(Block(teil, was, zone, F, (y / F, z / F)))
        return bloecke

    def nulllinie(self, n: Tuple[float, float], N: float = 0.0) -> Optional[float]:
        """
        Die Nulllinie ``n·p = v`` bei der Normalkraft ``N`` in N. ``None``,
        wo ``N`` jenseits der reinen Zug- oder Druckkraft liegt. Gesucht mit
        Illinois, bis sie auf 1e-9 mm genau liegt: je weiter sie zur
        gezogenen Seite rueckt, desto kleiner die Kraft.
        """
        werte = [_auf(n, p) for s in self.stuecke for p in s.punkte]
        unten, oben = min(werte), max(werte)
        fa, fb = self.zugkraft - N, -self.druckkraft - N
        if fa < 0.0 or fb > 0.0:
            return None
        if fa == 0.0 or fb == 0.0:
            return unten if fa == 0.0 else oben

        def abweichung(v: float) -> Tuple[float, float]:
            gezogen = 0.0
            for s in self.stuecke:
                a = geo.jenseits(s.punkte, n, v)[0]
                gezogen += s.gewicht * (self.zug[s.gruppe] * a
                                        - self.druck[s.gruppe] * (s.werte.A - a))
            return gezogen - N, v

        return illinois(abweichung, unten, fa, oben, fb, schranke_x=1e-9,
                        schranke_f=1e-12 * max(self.zugkraft, self.druckkraft))

    def zustand(self, N: float, M_y: float, M_z: float, bezug: Punkt,
                neigung: Optional[float]) -> Optional[Zustand]:
        """
        Der Zustand bei ``N``, dessen Moment in die Richtung von
        ``(M_y, M_z)`` zeigt -- mit fester Zugrichtung ``neigung``, wo sie
        feststeht (:meth:`~opencivil.querschnitt.biegung.Biegung.neigung`).
        ``None``, wo ``N`` jenseits der reinen Zug- oder Druckkraft liegt.
        Gesucht wird die Neigung der Nulllinie wie beim Stahlbeton
        (:func:`~opencivil.core.suche.winkel_suchen`).
        """
        if N > self.zugkraft or N < -self.druckkraft:
            return None

        def bei(n: Tuple[float, float]) -> Zustand:
            linie = Linie(n, self.nulllinie(n, N))
            return Zustand(linie, *self.kraefte(linie, bezug))

        if neigung is not None:
            return bei((float(round(math.cos(neigung))), float(round(math.sin(neigung)))))
        ziel = math.atan2(M_z, M_y)

        def abweichung(winkel: float) -> Tuple[float, Zustand]:
            zustand = bei((math.cos(winkel), math.sin(winkel)))
            if zustand.M_y == 0.0 and zustand.M_z == 0.0:
                return 0.0, zustand
            return math.remainder(math.atan2(zustand.M_z, zustand.M_y) - ziel,
                                  2.0 * math.pi), zustand

        return winkel_suchen(abweichung, Faserquerschnitt.neigung_fuer(M_y, M_z),
                             schranke=WINKEL_SCHRANKE)
