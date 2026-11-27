"""
opencivil/decke/fem/glaetten.py -- die Schnittkräfte an den Knoten.

VERANTWORTUNG:
Das Dreieck DKT gibt Momente, die über jedes Dreieck linear sind, an einer
gemeinsamen Kante aber nicht zusammenpassen. Für Bilder und Bericht gilt an
jedem Knoten das Mittel der Dreiecke um ihn, nach ihrer Fläche gewichtet --
über das Dreieck dazwischen linear, so dass das Bild an einer Kante nicht
springt. Gemittelt wird nur, wo die Platte durchläuft: an einem Lager,
einem Träger, einer Linienlast oder der Fuge zweier verschieden steifer
Platten springen die Schnittkräfte, und jede Seite behält ihren Wert
(:attr:`~opencivil.decke.fem.netz.Netz.trennkanten`). Die Dreiecke um einen
Knoten zerfallen so in Sektoren, und jeder hat sein Mittel.

Nach Vorgabe, nicht nachgeschlagen: wie gemittelt wird, regelt keine Norm.
Geprüft ist es an der gelenkig gelagerten Rechteckplatte nach Navier
(``tests/test_decke_fem.py``).
"""

from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

from opencivil.decke.fem.netz import Netz, kante

#: Je Dreieck und Ecke ein Tupel von Werten -- alle Tupel gleich lang.
Eckwerte = Sequence[Sequence[Sequence[float]]]


class Glaettung:
    """
    Je Ecke jedes Dreiecks ihr Sektor (:attr:`sektor`), und je Sektor sein
    Knoten, eines seiner Dreiecke und die Fläche aller.
    """

    def __init__(self, netz: Netz) -> None:
        self.netz = netz
        self.flaechen = [netz.flaeche(e) for e in range(len(netz.dreiecke))]
        self.sektor: List[List[int]] = [[0, 0, 0] for _ in netz.dreiecke]
        self.knoten: List[int] = []
        self.dreieck: List[int] = []
        self.gewicht: List[float] = []
        self.an: Dict[int, List[int]] = {}
        """Je Knoten seine Sektoren."""
        um: Dict[int, List[Tuple[int, int]]] = {}
        for e, d in enumerate(netz.dreiecke):
            for i, k in enumerate(d):
                um.setdefault(k, []).append((e, i))
        for k, ecken in um.items():
            self._sektoren(k, ecken)

    def _sektoren(self, k: int, ecken: List[Tuple[int, int]]) -> None:
        """Die Dreiecke um den Knoten ``k`` in Sektoren: verbunden über Kanten, die keine Trennkanten sind."""
        eltern = list(range(len(ecken)))

        def wurzel(i: int) -> int:
            while eltern[i] != i:
                eltern[i] = eltern[eltern[i]]
                i = eltern[i]
            return i

        an: Dict[int, List[int]] = {}
        for nr, (e, i) in enumerate(ecken):
            d = self.netz.dreiecke[e]
            for m in (d[(i + 1) % 3], d[(i + 2) % 3]):
                an.setdefault(m, []).append(nr)
        for m, nrn in an.items():
            if len(nrn) == 2 and kante(k, m) not in self.netz.trennkanten:
                a, b = wurzel(nrn[0]), wurzel(nrn[1])
                if a != b:
                    eltern[b] = a
        nummer: Dict[int, int] = {}
        for nr, (e, i) in enumerate(ecken):
            w = wurzel(nr)
            if w not in nummer:
                nummer[w] = len(self.gewicht)
                self.knoten.append(k)
                self.dreieck.append(e)
                self.gewicht.append(0.0)
                self.an.setdefault(k, []).append(nummer[w])
            s = nummer[w]
            self.sektor[e][i] = s
            self.gewicht[s] += self.flaechen[e]

    def mitteln(self, werte: Eckwerte) -> List[Tuple[float, ...]]:
        """Je Sektor das Mittel -- aus den Werten jedes Dreiecks an seinen Ecken."""
        breite = len(werte[0][0]) if werte else 0
        summen = [[0.0] * breite for _ in self.gewicht]
        for e, (ecken, A) in enumerate(zip(werte, self.flaechen)):
            for s, wert in zip(self.sektor[e], ecken):
                summe = summen[s]
                for j in range(breite):
                    summe[j] += A * wert[j]
        return [tuple(x / g for x in summe) for summe, g in zip(summen, self.gewicht)]
