"""
opencivil/fachwerkmodell/simp.py -- das Material einer Scheibe zur steifsten Form verteilt.

VERANTWORTUNG:
Das Verfahren SIMP nach Andreassen, Clausen, Schevenels, Lazarov &
Sigmund (2011): die Scheibe in quadratische Elemente der Netzweite h
geteilt (:func:`netz`), je Element eine Dichte zwischen null und eins.
Ein Schritt (:func:`schritt`) rechnet die Scheibe mit diesen Dichten
linear elastisch, fragt, wie stark jedes Element die Nachgiebigkeit
senkte, und verteilt das Material neu -- so viel, wie der Volumenanteil
erlaubt. Schritt um Schritt wächst so die steifste Form.

DAS ELEMENT:
Vier Knoten, bilinear, im ebenen Spannungszustand, Dicke eins
(:func:`elementsteifigkeit`). Ohne Material hat es noch E_min = 10⁻⁹ der
vollen Steifigkeit, damit nichts frei schwebt; dazwischen gilt
``E = E_min + ρ^p · (1 − E_min)`` mit p = 3 -- halbe Dichten lohnen sich
so nicht, und die Form wird klar (Gl. (1) der Quelle).

DER FILTER:
Ein Element sieht nicht seine eigene Dichte, sondern ihr Mittel über die
Nachbarn bis 1.5 h, gewichtet mit ``r_min − Abstand`` (Gl. (8) und (9));
so bleiben keine Schachbretter stehen, und die Form hängt kaum am Netz.
Die Ableitungen gehen über den Filter zurück auf die Dichten (Gl. (10)).
Die Änderung je Schritt ist höchstens 0.2, der Multiplikator der
Bedingung für das Volumen kommt aus einer Halbierung (Gl. (3) und (4)).

KEIN MATERIAL:
E und ν sind keine Eigenschaften des Bauteils: die Form hängt nur an
ihrem Verhältnis. ν = 0.2 wie für Beton (SIA 262:2025, 3.1.2.3.5), E = 1.
Die Lasten zählen bezogen auf die grösste.

DIE GRENZE:
Mehr als :data:`HOECHSTENS_ELEMENTE` Elemente rechnet das Werkzeug nicht
-- auf der Seite dauerte jeder Schritt gegen zwei Sekunden (nach Vorgabe,
nicht nachgeschlagen).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from operator import mul
from typing import Dict, List, Sequence, Tuple

from opencivil.decke import geometrie as geo
from opencivil.decke.geometrie import Punkt
from opencivil.fachwerkmodell.modell import Modell
from opencivil.stabwerk.matrix import Profilmatrix, Zerlegung, nummerierung

#: Wo das Verfahren nachzulesen ist.
QUELLE = "Andreassen et al. (2011)"

#: Wie viele Elemente das Netz höchstens hat -- nach Vorgabe, nicht nachgeschlagen.
HOECHSTENS_ELEMENTE = 2500

#: Die Steifigkeit eines Elements ohne Material, bezogen auf die volle -- wie in der Quelle.
E_MIN = 1e-9

#: Der Exponent, mit dem die Dichte in die Steifigkeit eingeht -- wie in den Beispielen der Quelle.
P = 3.0

#: Die Querdehnzahl -- wie für Beton; die Quelle nimmt 0.3 (nach Vorgabe, nicht nachgeschlagen).
NU = 0.2

#: Der Radius des Filters, in Netzweiten -- wie im ersten Beispiel der Quelle.
FILTER = 1.5

#: Um wie viel sich eine Dichte je Schritt höchstens ändert -- wie in der Quelle.
BEWEGUNG = 0.2


class NetzFehler(Exception):
    """Das Netz lässt sich so nicht rechnen: der Satz sagt, warum und was zu tun ist."""


@dataclass(frozen=True)
class Netz:
    """Die Elemente einer Scheibe, ihre Freiheitsgrade, die Last und der Filter."""

    modell: Modell
    weite: float
    ursprung: Punkt
    """Die Ecke unten links des Rechtecks um die Scheiben, in m."""

    spalten: int
    zeilen: int
    """Wie viele Elemente das Rechteck in x und in y fasst."""

    elemente: Tuple[Tuple[int, int], ...]
    """Je Element sein Platz ``(i, j)`` im Rechteck -- nur die im Material, Zeile um Zeile von unten."""

    freiheitsgrade: Tuple[Tuple[int, ...], ...]
    """Je Element seine acht Unbekannten, je Ecke x und y -- ``-1``, wo ein Lager hält."""

    unbekannte: int
    last: Tuple[float, ...]
    """Je Unbekannte die Last, bezogen auf die grösste."""

    filter: Tuple[Tuple[Tuple[int, float], ...], ...]
    """Je Element die Nachbarn im Filter und ihr Gewicht -- die Gewichte zusammen eins."""

    zurueck: Tuple[Tuple[Tuple[int, float], ...], ...]
    """Je Element, mit welchem Gewicht es in die gefilterte Dichte seiner Nachbarn eingeht."""

    anteil: Tuple[float, ...]
    """Je Element, wie viel es zum Volumen der gefilterten Dichten gibt."""

    profil: Tuple[int, ...]
    """Je Unbekannte die erste Spalte ihrer Zeile in der Steifigkeitsmatrix."""

    eintraege: Tuple[Tuple[Tuple[int, int, float], ...], ...]
    """Je Element, wohin seine Steifigkeit geht: Zeile, Platz in der Zeile, Wert bei voller Dichte."""

    def mitte(self, platz: Tuple[int, int]) -> Punkt:
        """Die Mitte des Elements am Platz ``(i, j)``, in m."""
        i, j = platz
        return (self.ursprung[0] + (i + 0.5) * self.weite, self.ursprung[1] + (j + 0.5) * self.weite)


@dataclass(frozen=True)
class Schritt:
    """Was ein Schritt gibt."""

    dichte: Tuple[float, ...]
    """Die neuen Dichten, je Element -- die der Optimierung, noch nicht gefiltert."""

    aenderung: float
    """Wie stark sich die Dichten höchstens änderten."""

    nachgiebigkeit: float
    """``fᵀ · u`` mit den Dichten vor dem Schritt, die Last bezogen auf die grösste."""


def elementsteifigkeit(nu: float = NU) -> Tuple[Tuple[float, ...], ...]:
    """
    Die Steifigkeit eines quadratischen Elements mit E = 1 und der Dicke
    eins, 8 × 8, die Ecken unten links, unten rechts, oben rechts, oben
    links, je x und y. Aus vier Punkten nach Gauss -- genau für das
    bilineare Element; quadratisch hängt sie nicht an seiner Grösse.
    """
    ecken = ((-1, -1), (1, -1), (1, 1), (-1, 1))
    d = 1.0 / (1.0 - nu * nu)
    D = ((d, d * nu, 0.0), (d * nu, d, 0.0), (0.0, 0.0, d * (1.0 - nu) / 2.0))
    K = [[0.0] * 8 for _ in range(8)]
    g = 1.0 / math.sqrt(3.0)
    for xi in (-g, g):
        for eta in (-g, g):
            # Ableitungen nach x und y bei der Weite 2 -- die Grösse kürzt sich.
            dx = [0.25 * a * (1 + eta * b) for a, b in ecken]
            dy = [0.25 * b * (1 + xi * a) for a, b in ecken]
            B = ([v for k in range(4) for v in (dx[k], 0.0)],
                 [v for k in range(4) for v in (0.0, dy[k])],
                 [v for k in range(4) for v in (dy[k], dx[k])])
            DB = [[sum(D[r][s] * B[s][c] for s in range(3)) for c in range(8)] for r in range(3)]
            for r in range(8):
                for c in range(8):
                    K[r][c] += sum(B[s][r] * DB[s][c] for s in range(3))
    return tuple(tuple(z) for z in K)


#: Die Steifigkeit des vollen Elements (:func:`elementsteifigkeit`).
KE = elementsteifigkeit()


def netz(modell: Modell, weite: float) -> Netz:
    """
    Das Netz der Scheibe mit der Netzweite ``weite`` in m: je Quadrat des
    Rasters ein Element, wenn seine Mitte im Material liegt. Ein Lager und
    eine Last gehen an die nächste Ecke eines Elements. Das Modell ist
    geprüft. Wirft :class:`NetzFehler`, wenn es zu viele Elemente wären.
    """
    (x0, y0), nx, ny = raster(modell, weite)
    if nx * ny > 4 * HOECHSTENS_ELEMENTE:
        raise NetzFehler(_zu_viele(modell, weite, f"weit über {HOECHSTENS_ELEMENTE}"))
    elemente = [(i, j) for j in range(ny) for i in range(nx)
                if modell.im_material((x0 + (i + 0.5) * weite, y0 + (j + 0.5) * weite))]
    if len(elemente) > HOECHSTENS_ELEMENTE:
        raise NetzFehler(_zu_viele(modell, weite, str(len(elemente))))
    if not elemente:
        raise NetzFehler(f"Mit der Netzweite {weite:g} m liegt kein Element in der Scheibe – bitte "
                         f"eine kleinere wählen.")
    ecken = [((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)) for i, j in elemente]
    knoten = sorted({k for e in ecken for k in e}, key=lambda k: (k[1], k[0]))
    nachbarn: Dict[Tuple[int, int], set] = {k: set() for k in knoten}
    for e in ecken:
        for k in e:
            nachbarn[k].update(e)
    folge = nummerierung(knoten, nachbarn)
    ort = lambda k: (x0 + k[0] * weite, y0 + k[1] * weite)  # noqa: E731 -- nur hier
    halt: Dict[Tuple[int, int], List[bool]] = {}
    for lager in modell.lager:
        k = _naechster(knoten, ort, lager.ort)
        h = halt.setdefault(k, [False, False])
        h[0] = h[0] or lager.halt.x
        h[1] = h[1] or lager.halt.y
    platz: Dict[Tuple[Tuple[int, int], int], int] = {}
    for k in folge:
        for r in (0, 1):
            if not halt.get(k, (False, False))[r]:
                platz[(k, r)] = len(platz)
    n = len(platz)
    last = [0.0] * n
    groesste = max(math.hypot(f.F_x, f.F_y) for f in modell.lasten)
    for f in modell.lasten:
        k = _naechster(knoten, ort, f.ort)
        for r, wert in ((0, f.F_x), (1, f.F_y)):
            if (k, r) in platz:
                last[platz[(k, r)]] += wert / groesste
    freiheitsgrade = tuple(tuple(platz.get((k, r), -1) for k in e for r in (0, 1)) for e in ecken)
    K = Profilmatrix.aus_gruppen(n, ([d for d in f if d >= 0] for f in freiheitsgrade))
    eintraege = []
    for f in freiheitsgrade:
        liste = []
        for p in range(8):
            for q in range(p + 1):
                a, b = f[p], f[q]
                if a < 0 or b < 0:
                    continue
                zeile, spalte = (a, b) if a >= b else (b, a)
                liste.append((zeile, spalte - K.erste[zeile], KE[p][q]))
        eintraege.append(tuple(liste))
    filter_, zurueck, anteil = _filter(elemente, FILTER)
    return Netz(modell=modell, weite=weite, ursprung=(x0, y0), spalten=nx, zeilen=ny,
                elemente=tuple(elemente), freiheitsgrade=freiheitsgrade, unbekannte=n,
                last=tuple(last), filter=filter_, zurueck=zurueck, anteil=anteil,
                profil=tuple(K.erste), eintraege=tuple(eintraege))


def raster(modell: Modell, weite: float) -> Tuple[Punkt, int, int]:
    """
    Das Raster der Elemente: die Ecke unten links des Rechtecks um die
    Scheiben, in m, und wie viele Felder der Weite ``weite`` es in x und in
    y fasst.
    """
    xs = [p[0] for s in modell.scheiben for p in s.ecken]
    ys = [p[1] for s in modell.scheiben for p in s.ecken]
    x0, y0 = min(xs), min(ys)
    return ((x0, y0), max(1, math.ceil((max(xs) - x0) / weite - 1e-9)),
            max(1, math.ceil((max(ys) - y0) / weite - 1e-9)))


def _naechster(knoten, ort, p: Punkt):
    """Die Ecke eines Elements, die ``p`` am nächsten liegt -- bei gleichem Abstand die erste."""
    return min(knoten, key=lambda k: math.dist(ort(k), p))


def _zu_viele(modell: Modell, weite: float, anzahl: str) -> str:
    """Der Satz, wenn das Netz zu fein ist -- mit einer Netzweite, die passt, auf 1 cm genau."""
    flaeche = sum(abs(geo.flaeche(s.ecken)) for s in modell.scheiben)
    passt = max(math.ceil(100.0 * math.sqrt(flaeche / HOECHSTENS_ELEMENTE)) / 100.0, weite + 0.01)
    return (f"Mit der Netzweite {weite:g} m lägen {anzahl} Elemente in der Scheibe – mehr als "
            f"{HOECHSTENS_ELEMENTE} rechnet das Werkzeug nicht. Bitte die Netzweite mindestens "
            f"{passt:g} m wählen.")


def _filter(elemente: Sequence[Tuple[int, int]], radius: float):
    """Je Element die Nachbarn bis ``radius`` Netzweiten mit ihren Gewichten -- siehe Dateikopf."""
    platz = {e: k for k, e in enumerate(elemente)}
    r = int(math.floor(radius))
    roh = []
    for i, j in elemente:
        nahe = []
        for di in range(-r, r + 1):
            for dj in range(-r, r + 1):
                k = platz.get((i + di, j + dj))
                w = radius - math.hypot(di, dj)
                if k is not None and w > 0.0:
                    nahe.append((k, w))
        roh.append(nahe)
    filter_ = tuple(tuple((k, w / sum(x for _, x in nahe)) for k, w in nahe) for nahe in roh)
    zurueck: List[List[Tuple[int, float]]] = [[] for _ in elemente]
    for e, nahe in enumerate(filter_):
        for k, w in nahe:
            zurueck[k].append((e, w))
    anteil = tuple(sum(w for _, w in z) for z in zurueck)
    return filter_, tuple(tuple(z) for z in zurueck), anteil


def gefiltert(n: Netz, x: Sequence[float]) -> List[float]:
    """Die Dichten, die die Elemente sehen: je das gewichtete Mittel über die Nachbarn."""
    return [sum(w * x[k] for k, w in nahe) for nahe in n.filter]


def schritt(n: Netz, x: Sequence[float], volumen: float) -> Schritt:
    """
    Ein Schritt der Optimierung (Dateikopf): die Scheibe mit den Dichten
    ``x`` gerechnet, das Material nach Optimality Criteria neu verteilt.
    Wirft :class:`NetzFehler`, wenn ein Teil der Scheibe an keinem Lager hängt.
    """
    rho = gefiltert(n, x)
    steif = [E_MIN + r ** P * (1.0 - E_MIN) for r in rho]
    K = Profilmatrix(n.unbekannte, n.profil)
    zeilen = K.zeilen
    for s, liste in zip(steif, n.eintraege):
        for zeile, spalte, wert in liste:
            zeilen[zeile][spalte] += s * wert
    z = Zerlegung(K)
    if z.singulaer:
        raise NetzFehler(f"Mit der Netzweite {n.weite:g} m hängt ein Teil der Scheibe an keinem "
                         f"Lager – er könnte sich frei bewegen.")
    u = z.loese(n.last)
    u.append(0.0)  # an -1: wo ein Lager hält
    energie = []
    for f in n.freiheitsgrade:
        ue = [u[d] for d in f]
        energie.append(sum(map(mul, ue, [sum(map(mul, zeile, ue)) for zeile in KE])))
    nachgiebigkeit = sum(map(mul, n.last, u))
    # Die Ableitung je Element nach seiner gefilterten Dichte, dann zurück auf die Dichte.
    roh = [-P * r ** (P - 1.0) * (1.0 - E_MIN) * c for r, c in zip(rho, energie)]
    dc = [sum(w * roh[e] for e, w in z_) for z_ in n.zurueck]
    faktor = [math.sqrt(max(-d, 0.0) / a) for d, a in zip(dc, n.anteil)]
    ziel = volumen * len(x)
    l1, l2 = 0.0, 1e9
    neu = list(x)
    while (l2 - l1) / (l1 + l2) > 1e-3:
        lm = 0.5 * (l1 + l2)
        s = 1.0 / math.sqrt(lm)
        neu = [max(0.0, xe - BEWEGUNG, min(1.0, xe + BEWEGUNG, xe * b * s))
               for xe, b in zip(x, faktor)]
        if sum(map(mul, neu, n.anteil)) > ziel:
            l1 = lm
        else:
            l2 = lm
    aenderung = max(abs(a - b) for a, b in zip(neu, x))
    return Schritt(dichte=tuple(neu), aenderung=aenderung, nachgiebigkeit=nachgiebigkeit)
