"""
opencivil/querschnitt/randzone.py -- der Beton nahe am Rand eines gezeichneten Querschnitts.

VERANTWORTUNG:
Je Polygon die Flaeche, die hoechstens ``abstand`` vom Rand des Bauteils
liegt (:func:`flaechen_am_rand`). Gebraucht von der Zwaengung auf
Normalkraft: bei massigen Bauteilen darf die mitwirkende Zugzone auf 250 mm
entlang der gezogenen Raender beschraenkt werden (SIA 262:2025, 4.4.2.3.7),
und unter zentrischem Zug sind alle Raender gezogen.

DER RAND DES BAUTEILS:
Jede Kante zwischen Material und Leere: die Umrisse aussen und die Raender
der Aussparungen. Nicht dazu gehoert, wo zwei Materialien aneinander
grenzen -- ein Polygon in einem anderen, oder zwei, die sich entlang einer
Kante beruehren.

WIE GERECHNET WIRD:
Auf waagrechten Linien. Je Linie die Strecken, die einem Polygon gehoeren
(in ihm, in keinem seiner Kinder), geschnitten mit denen, die naeher als
``abstand`` an einer Randkante liegen: um jede Kante liegt ein Streifen mit
runden Enden, und jede Linie schneidet ihn in einer Strecke. Die Linien
liegen in Baendern zwischen den Hoehen, an denen die Strecken springen oder
knicken -- an den Ecken, den Ecken ± ``abstand`` und den Ecken der
Streifen --, in jedem Band mindestens eine, sonst nach seiner Hoehe
verteilt. Bei Rechtecken ist das genau; eine einspringende Ecke zieht einen
Kreisbogen, dort liegt der Fehler unter einem Promille.

EINHEITEN:
Keine -- die der Punkte, wie in :mod:`opencivil.querschnitt.geometrie`.
"""

from __future__ import annotations

import math
from typing import List, Optional, Sequence, Tuple

from opencivil.querschnitt.geometrie import TOLERANZ, Punkt

Strecke = Tuple[float, float]
Kante = Tuple[Punkt, Punkt]

#: Wie viele Linien ueber die Hoehe des Querschnitts verteilt werden -- dazu
#: wenigstens eine je Band.
LINIEN = 400


def flaechen_am_rand(polygone: Sequence[Sequence[Punkt]], eltern: Sequence[Optional[int]],
                     traegt: Sequence[bool], abstand: float) -> List[float]:
    """
    Je Polygon die Flaeche, die ihm gehoert und hoechstens ``abstand`` vom
    Rand des Bauteils liegt. ``eltern`` sagt, worin jedes liegt
    (:func:`~opencivil.querschnitt.geometrie.verschachteln`), ``traegt``, ob
    es Material hat; eine Aussparung besitzt nichts, ihre Flaeche ist null.
    """
    kinder = [[c for c, e in enumerate(eltern) if e == i] for i in range(len(polygone))]
    kanten = _randkanten(polygone, eltern, traegt)
    hoehen = _bandgrenzen(polygone, kanten, abstand)
    gesamt = hoehen[-1] - hoehen[0]
    flaechen = [0.0] * len(polygone)
    for unten, oben in zip(hoehen, hoehen[1:]):
        n = max(1, round(LINIEN * (oben - unten) / gesamt))
        breite = (oben - unten) / n
        for k in range(n):
            z = unten + (k + 0.5) * breite
            nahe = _vereinigen([s for s in (_streifen(a, b, abstand, z) for a, b in kanten)
                                if s is not None])
            innen = [_innen(p, z) for p in polygone]
            for i in range(len(polygone)):
                if traegt[i]:
                    eigen = _abziehen(innen[i], _vereinigen(
                        [s for c in kinder[i] for s in innen[c]]))
                    flaechen[i] += _laenge(_schneiden(eigen, nahe)) * breite
    return flaechen


# ===========================================================================
# Der Rand und die Baender
# ===========================================================================


def _kanten(punkte: Sequence[Punkt]) -> List[Kante]:
    return [(punkte[i - 1], punkte[i]) for i in range(len(punkte))]


def _randkanten(polygone: Sequence[Sequence[Punkt]], eltern: Sequence[Optional[int]],
                traegt: Sequence[bool]) -> List[Kante]:
    """
    Die Kanten zwischen Material und Leere. Ein Polygon traegt sie bei, wenn
    innen anderes liegt als aussen; wo zwei solche Kanten aufeinander liegen,
    grenzt auf beiden Seiten dasselbe -- Material an Material oder Leere an
    Leere --, und das Stueck faellt weg.
    """
    def aussen_fest(i: int) -> bool:
        e = eltern[i]
        return e is not None and traegt[e]

    kandidaten = [(i, k) for i, p in enumerate(polygone) if traegt[i] != aussen_fest(i)
                  for k in _kanten(p)]
    rand: List[Kante] = []
    for i, (a, b) in kandidaten:
        decken = [_deckung(a, b, c, d) for j, (c, d) in kandidaten if j != i]
        rand += _reste(a, b, [t for t in decken if t is not None])
    return rand


def _deckung(a: Punkt, b: Punkt, c: Punkt, d: Punkt) -> Optional[Strecke]:
    """Welches Stueck der Kante a–b die Kante c–d deckt, als Parameter in [0, 1] -- oder nichts."""
    ry, rz = b[0] - a[0], b[1] - a[1]
    l2 = ry * ry + rz * rz
    if l2 <= TOLERANZ * TOLERANZ:
        return None
    laenge = math.sqrt(l2)
    for p in (c, d):
        if abs(ry * (p[1] - a[1]) - rz * (p[0] - a[0])) / laenge > TOLERANZ:
            return None
    t = sorted(((p[0] - a[0]) * ry + (p[1] - a[1]) * rz) / l2 for p in (c, d))
    lo, hi = max(t[0], 0.0), min(t[1], 1.0)
    return (lo, hi) if hi > lo else None


def _reste(a: Punkt, b: Punkt, decken: Sequence[Strecke]) -> List[Kante]:
    """Die Stuecke der Kante a–b, die keine andere deckt."""
    def punkt(t: float) -> Punkt:
        return (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))
    return [(punkt(lo), punkt(hi)) for lo, hi in _abziehen([(0.0, 1.0)], _vereinigen(decken))]


def _bandgrenzen(polygone: Sequence[Sequence[Punkt]], kanten: Sequence[Kante],
                 abstand: float) -> List[float]:
    """Die Hoehen, an denen die Strecken einer Linie springen oder knicken -- aufsteigend."""
    alle = [p[1] for poly in polygone for p in poly]
    unten, oben = min(alle), max(alle)
    for a, b in kanten:
        ry, rz = b[0] - a[0], b[1] - a[1]
        laenge = math.hypot(ry, rz)
        # Die Ecken des Rechtecks liegen um die Normale (-rz, ry)/laenge daneben.
        quer = ry / laenge * abstand if laenge > 0.0 else 0.0
        for p in (a, b):
            alle += [p[1] - abstand, p[1] + abstand, p[1] - quer, p[1] + quer]
    hoehen: List[float] = []
    for z in sorted(min(max(z, unten), oben) for z in alle):
        if not hoehen or z - hoehen[-1] > TOLERANZ:
            hoehen.append(z)
    return hoehen


# ===========================================================================
# Eine Linie
# ===========================================================================


def _innen(punkte: Sequence[Punkt], z: float) -> List[Strecke]:
    """Wo die Linie auf der Hoehe ``z`` im Polygon liegt -- keine Ecke liegt auf ihr."""
    schnitte = sorted(a[0] + (z - a[1]) * (b[0] - a[0]) / (b[1] - a[1])
                      for a, b in _kanten(punkte) if (a[1] > z) != (b[1] > z))
    return list(zip(schnitte[::2], schnitte[1::2]))


def _streifen(a: Punkt, b: Punkt, abstand: float, z: float) -> Optional[Strecke]:
    """
    Wo die Linie auf der Hoehe ``z`` naeher als ``abstand`` an der Kante a–b
    liegt: im Kreis um eine der Ecken oder im Rechteck daneben. Der Streifen
    ist konvex, die Linie schneidet ihn in einer Strecke.
    """
    teile = []
    for p in (a, b):
        rest = abstand * abstand - (z - p[1]) ** 2
        if rest > 0.0:
            halb = math.sqrt(rest)
            teile.append((p[0] - halb, p[0] + halb))
    ry, rz = b[0] - a[0], b[1] - a[1]
    laenge = math.hypot(ry, rz)
    if laenge > 0.0:
        uy, uz = ry / laenge, rz / laenge
        laengs = _zwischen(uy, (z - a[1]) * uz, 0.0, laenge, a[0])
        quer = _zwischen(-uz, (z - a[1]) * uy, -abstand, abstand, a[0])
        if laengs is not None and quer is not None:
            lo, hi = max(laengs[0], quer[0]), min(laengs[1], quer[1])
            if hi > lo:
                teile.append((lo, hi))
    if not teile:
        return None
    return (min(t[0] for t in teile), max(t[1] for t in teile))


def _zwischen(faktor: float, rest: float, unten: float, oben: float,
              y0: float) -> Optional[Strecke]:
    """Die ``y`` mit ``unten <= (y - y0)·faktor + rest <= oben`` -- alle, wenn ``faktor`` null ist."""
    if abs(faktor) <= 1e-12:
        return (-math.inf, math.inf) if unten <= rest <= oben else None
    g1, g2 = y0 + (unten - rest) / faktor, y0 + (oben - rest) / faktor
    return (min(g1, g2), max(g1, g2))


# ===========================================================================
# Strecken auf einer Linie
# ===========================================================================


def _vereinigen(strecken: Sequence[Strecke]) -> List[Strecke]:
    """Die Strecken, sortiert und ohne Ueberlappung."""
    ergebnis: List[Strecke] = []
    for lo, hi in sorted(strecken):
        if ergebnis and lo <= ergebnis[-1][1]:
            ergebnis[-1] = (ergebnis[-1][0], max(ergebnis[-1][1], hi))
        else:
            ergebnis.append((lo, hi))
    return ergebnis


def _schneiden(a: Sequence[Strecke], b: Sequence[Strecke]) -> List[Strecke]:
    """Was in beiden liegt -- beide sortiert und ohne Ueberlappung."""
    ergebnis: List[Strecke] = []
    i = j = 0
    while i < len(a) and j < len(b):
        lo, hi = max(a[i][0], b[j][0]), min(a[i][1], b[j][1])
        if hi > lo:
            ergebnis.append((lo, hi))
        if a[i][1] < b[j][1]:
            i += 1
        else:
            j += 1
    return ergebnis


def _abziehen(a: Sequence[Strecke], b: Sequence[Strecke]) -> List[Strecke]:
    """Was in ``a`` liegt und nicht in ``b`` -- beide sortiert und ohne Ueberlappung."""
    ergebnis: List[Strecke] = []
    for lo, hi in a:
        for blo, bhi in b:
            if bhi <= lo or blo >= hi:
                continue
            if blo > lo:
                ergebnis.append((lo, blo))
            lo = bhi
            if lo >= hi:
                break
        if hi > lo:
            ergebnis.append((lo, hi))
    return ergebnis


def _laenge(strecken: Sequence[Strecke]) -> float:
    return sum(hi - lo for lo, hi in strecken)
