"""
opencivil/decke/fem/delaunay.py -- eine Delaunay-Triangulierung, Punkt für Punkt.

VERANTWORTUNG:
Dreiecke über einer Menge von Punkten, so dass kein Punkt im Umkreis eines
Dreiecks liegt (Bowyer 1981, Watson 1981): ein neuer Punkt löscht die
Dreiecke, in deren Umkreis er liegt, und verbindet sich mit dem Rand des
Lochs. Das Dreieck, in dem er liegt, findet ein Weg vom zuletzt gebauten
aus -- wer die Punkte so einfügt, wie sie nebeneinander liegen, geht nur
wenige Schritte.

Am Anfang steht ein grosses Dreieck um alle Punkte; was an seinen Ecken
hängt, fällt am Ende weg (:meth:`Triangulierung.dreiecke`).

RUNDUNG:
Ein Punkt auf einer Kante gilt als in beiden Dreiecken; liegt er nach der
Rundung knapp neben dem Rand des Lochs, wächst das Loch um das Dreieck
dahinter, statt ein flaches Dreieck zu bauen. Ein Punkt, der schon da ist
(:attr:`Triangulierung.gleich`), kommt nicht ein zweites Mal hinein.
"""

from __future__ import annotations

from typing import List, Optional, Set, Tuple

Punkt = Tuple[float, float]

#: Wie gross das Dreieck um alle Punkte ist, gemessen an ihrer Ausdehnung.
UMFANG = 1e3


def orientierung(a: Punkt, b: Punkt, c: Punkt) -> float:
    """Die doppelte Fläche des Dreiecks ``a, b, c``: positiv im Gegenuhrzeigersinn."""
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def im_umkreis(a: Punkt, b: Punkt, c: Punkt, d: Punkt) -> float:
    """Positiv, wenn ``d`` im Umkreis des Dreiecks ``a, b, c`` (im Gegenuhrzeigersinn) liegt."""
    adx, ady = a[0] - d[0], a[1] - d[1]
    bdx, bdy = b[0] - d[0], b[1] - d[1]
    cdx, cdy = c[0] - d[0], c[1] - d[1]
    ad = adx * adx + ady * ady
    bd = bdx * bdx + bdy * bdy
    cd = cdx * cdx + cdy * cdy
    return adx * (bdy * cd - bd * cdy) - ady * (bdx * cd - bd * cdx) + ad * (bdx * cdy - bdy * cdx)


class Triangulierung:
    """
    Die Dreiecke über den Punkten, die bisher eingefügt sind. Je Dreieck
    seine Ecken im Gegenuhrzeigersinn und je Ecke das Nachbardreieck über
    der Kante ihr gegenüber (-1: keines).
    """

    def __init__(self, x0: float, y0: float, x1: float, y1: float, gleich: float = 1e-9) -> None:
        """Für Punkte im Rechteck ``x0 … x1 × y0 … y1``; näher als ``gleich`` gilt als derselbe."""
        mx, my = 0.5 * (x0 + x1), 0.5 * (y0 + y1)
        r = max(x1 - x0, y1 - y0, gleich) * UMFANG
        self.punkte: List[Punkt] = [(mx - 2.0 * r, my - r), (mx + 2.0 * r, my - r), (mx, my + 2.0 * r)]
        self.ecken: List[List[int]] = [[0, 1, 2]]
        self.nachbarn: List[List[int]] = [[-1, -1, -1]]
        self.lebt: List[bool] = [True]
        self._frei: List[int] = []
        self._zuletzt = 0
        self.gleich = gleich

    # -- Einfügen ----------------------------------------------------------------

    def einfuegen(self, p: Punkt) -> int:
        """Fügt ``p`` ein und gibt seine Nummer -- die eines gleichen Punkts, wenn es ihn schon gibt."""
        t = self._suche(p)
        for v in self.ecken[t]:
            q = self.punkte[v]
            if abs(q[0] - p[0]) <= self.gleich and abs(q[1] - p[1]) <= self.gleich:
                return v
        neu = len(self.punkte)
        self.punkte.append(p)
        loch = self._loch(t, p)
        rand = self._rand(loch, p)
        anfang, ende, gebaut = {}, {}, []
        for b, c, aussen in rand:
            j = self._dreieck([neu, b, c])
            self.nachbarn[j][0] = aussen
            if aussen >= 0:
                self._umhaengen(aussen, b, c, j)
            anfang[b], ende[c] = j, j
            gebaut.append((j, b, c))
        for j, b, c in gebaut:
            self.nachbarn[j][1] = anfang[c]
            self.nachbarn[j][2] = ende[b]
        # Erst jetzt frei: auf die Plätze des Lochs zeigten bis eben noch Nachbarn.
        for s in loch:
            self.lebt[s] = False
            self._frei.append(s)
        self._zuletzt = gebaut[-1][0]
        return neu

    def _suche(self, p: Punkt) -> int:
        """Das Dreieck, in dem ``p`` liegt -- oder auf dessen Rand: ein Weg vom zuletzt gebauten aus."""
        t = self._zuletzt if self.lebt[self._zuletzt] else self.lebt.index(True)
        start = 0
        for _ in range(4 * len(self.ecken) + 16):
            e = self.ecken[t]
            weiter = None
            for j in range(3):
                k = (start + j) % 3
                b, c = self.punkte[e[(k + 1) % 3]], self.punkte[e[(k + 2) % 3]]
                laenge = abs(c[0] - b[0]) + abs(c[1] - b[1])
                if orientierung(b, c, p) < -1e-12 * laenge * (laenge + abs(p[0] - b[0]) + abs(p[1] - b[1])):
                    weiter = self.nachbarn[t][k]
                    break
            if weiter is None:
                return t
            if weiter < 0:
                raise ValueError(f"Der Punkt ({p[0]:g}, {p[1]:g}) liegt ausserhalb der Triangulierung.")
            t = weiter
            start = (start + 1) % 3
        raise RuntimeError("Die Suche nach dem Dreieck kam nicht an.")

    def _loch(self, t: int, p: Punkt) -> Set[int]:
        """Die Dreiecke, in deren Umkreis ``p`` liegt -- zusammenhängend, von ``t`` aus."""
        loch = {t}
        stapel = [t]
        while stapel:
            s = stapel.pop()
            for n in self.nachbarn[s]:
                if n >= 0 and n not in loch:
                    a, b, c = (self.punkte[v] for v in self.ecken[n])
                    if im_umkreis(a, b, c, p) > 0.0:
                        loch.add(n)
                        stapel.append(n)
        return loch

    def _rand(self, loch: Set[int], p: Punkt) -> List[Tuple[int, int, int]]:
        """
        Der Rand des Lochs als Kanten ``(b, c, aussen)``, jede links von ``p``
        gesehen -- liegt ``p`` auf einer oder knapp daneben, kommt das Dreieck
        dahinter ins Loch, und der Rand wird neu gesucht.
        """
        while True:
            rand: List[Tuple[int, int, int]] = []
            gewachsen = False
            for s in loch:
                e = self.ecken[s]
                for k in range(3):
                    n = self.nachbarn[s][k]
                    if n in loch:
                        continue
                    b, c = e[(k + 1) % 3], e[(k + 2) % 3]
                    pb, pc = self.punkte[b], self.punkte[c]
                    laenge = abs(pc[0] - pb[0]) + abs(pc[1] - pb[1])
                    if orientierung(pb, pc, p) <= 1e-12 * laenge * laenge:
                        if n < 0:
                            raise ValueError("Ein Punkt liegt auf dem Rand der Triangulierung.")
                        loch.add(n)
                        gewachsen = True
                        break
                    rand.append((b, c, n))
                if gewachsen:
                    break
            if not gewachsen:
                return rand

    def _dreieck(self, ecken: List[int]) -> int:
        if self._frei:
            j = self._frei.pop()
            self.ecken[j], self.nachbarn[j], self.lebt[j] = ecken, [-1, -1, -1], True
            return j
        self.ecken.append(ecken)
        self.nachbarn.append([-1, -1, -1])
        self.lebt.append(True)
        return len(self.ecken) - 1

    def _umhaengen(self, aussen: int, b: int, c: int, j: int) -> None:
        """Im Dreieck ``aussen`` zeigt die Kante ``c → b`` nun auf ``j``."""
        e = self.ecken[aussen]
        for k in range(3):
            if e[(k + 1) % 3] == c and e[(k + 2) % 3] == b:
                self.nachbarn[aussen][k] = j
                return
        raise RuntimeError("Die Nachbarn der Triangulierung passen nicht zusammen.")

    # -- Lesen -------------------------------------------------------------------

    def dreiecke(self) -> List[Tuple[int, int, int]]:
        """Die Dreiecke ohne die an den Ecken des Dreiecks um alles, je im Gegenuhrzeigersinn."""
        return [tuple(e) for e, lebt in zip(self.ecken, self.lebt) if lebt and min(e) > 2]

    def kanten(self) -> Set[Tuple[int, int]]:
        """Jede Kante einmal, als ``(kleinere, grössere Nummer)``."""
        heraus: Set[Tuple[int, int]] = set()
        for a, b, c in self.dreiecke():
            for p, q in ((a, b), (b, c), (c, a)):
                heraus.add((p, q) if p < q else (q, p))
        return heraus

    def gefunden(self, p: Punkt) -> Optional[int]:
        """Die Nummer eines Punkts, der mit ``p`` zusammenfällt -- ``None``, wenn keiner."""
        t = self._suche(p)
        for v in self.ecken[t]:
            q = self.punkte[v]
            if abs(q[0] - p[0]) <= self.gleich and abs(q[1] - p[1]) <= self.gleich:
                return v
        return None
