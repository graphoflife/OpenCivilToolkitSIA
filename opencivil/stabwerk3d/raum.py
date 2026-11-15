"""
opencivil/stabwerk3d/raum.py -- Vektoren, Richtungen und Strecken im Raum.

VERANTWORTUNG:
Die Geometrie des raeumlichen Stabwerks: Vektoren als Tupel ``(x, y, z)``,
Skalar- und Kreuzprodukt, orthonormale Basen aus Richtungen, Punkte auf
Strecken -- und eine Kraft mit ihrem Moment um den Ursprung. Nur die
Standardbibliothek.

GENAUIGKEIT:
Ein Punkt liegt auf einer Strecke, wenn er weniger als :data:`TOLERANZ`
daneben liegt -- so genau rundet das Zeichenfenster. Eine Richtung zaehlt in
einer Basis, wenn von ihr nach Abzug der anderen mehr als 1e-9 bleibt.
"""

from __future__ import annotations

import math
from typing import List, Optional, Sequence, Tuple

#: Wie nahe ein Knoten an einem Stab liegen muss, um mit ihm verbunden zu
#: sein -- in m. Das Zeichenfenster rundet auf ein Millionstel.
TOLERANZ = 1e-6

Vektor = Tuple[float, float, float]

#: Die Achsen des Systems.
ACHSEN: Tuple[Vektor, Vektor, Vektor] = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))

NULL: Vektor = (0.0, 0.0, 0.0)


def skalar(a: Sequence[float], b: Sequence[float]) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def kreuz(a: Sequence[float], b: Sequence[float]) -> Vektor:
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def mal(faktor: float, a: Sequence[float]) -> Vektor:
    return (faktor * a[0], faktor * a[1], faktor * a[2])


def plus(a: Sequence[float], b: Sequence[float]) -> Vektor:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def minus(a: Sequence[float], b: Sequence[float]) -> Vektor:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def betrag(a: Sequence[float]) -> float:
    return math.sqrt(skalar(a, a))


def punkt(p) -> Vektor:
    """Der Ort eines Knotens -- oder von allem, was ``x``, ``y`` und ``z`` hat."""
    return (p.x, p.y, p.z)


def im_system(achsen: Sequence[Vektor], lokal: Sequence[float]) -> Vektor:
    """Ein Vektor in den Achsen eines Stabs, in denen des Systems: ``Rᵀ · v``."""
    return tuple(sum(lokal[i] * achsen[i][j] for i in range(3)) for j in range(3))


def addiere(summe: List[float], ort: Sequence[float], kraft: Sequence[float],
            moment: Sequence[float] = NULL) -> None:
    """Eine Kraft an ``ort`` und ein Moment zur Summe ``(F, M)`` -- das Moment um den Ursprung."""
    um = kreuz(ort, kraft)
    for i in range(3):
        summe[i] += kraft[i]
        summe[3 + i] += um[i] + moment[i]


def orthonormal(vektoren: Sequence[Sequence[float]],
                gegen: Sequence[Vektor] = ()) -> List[Vektor]:
    """Die Richtungen von ``vektoren`` orthonormal, ohne was in ``gegen`` liegt (Gram-Schmidt)."""
    basis: List[Vektor] = []
    for v in vektoren:
        w = tuple(v)
        for b in (*gegen, *basis):
            w = minus(w, mal(skalar(w, b), b))
        n = betrag(w)
        if n > 1e-9:
            basis.append(mal(1.0 / n, w))
    return basis


def in_achsen(raum: Sequence[Vektor], achsen: Sequence[Vektor] = ACHSEN) -> List[Vektor]:
    """
    Eine orthonormale Basis des Raums, den die orthonormalen ``raum``
    aufspannen -- aus den ``achsen``, zuerst die, die am meisten darin
    liegt. Eine Rolle auf waagrechter Bahn ist so frei in x, nicht in -x und
    nicht schief.
    """
    heraus: List[Vektor] = []
    while len(heraus) < len(raum):
        kandidaten = []
        for e in achsen:
            w = NULL
            for r in raum:
                w = plus(w, mal(skalar(e, r), r))
            for h in heraus:
                w = minus(w, mal(skalar(w, h), h))
            kandidaten.append(w)
        w = max(kandidaten, key=betrag)
        # Rundungsreste weg: so bleibt eine Achse genau eine Achse.
        w = tuple(0.0 if abs(c) < 1e-12 else c for c in w)
        heraus.append(mal(1.0 / betrag(w), w))
    return heraus


def stelle_auf(a, b, p) -> Optional[float]:
    """Wo ``p`` auf der Strecke a-b liegt, in m ab a -- ``None``, wenn daneben oder an einem Ende."""
    d = minus(punkt(b), punkt(a))
    L = betrag(d)
    if L <= TOLERANZ:
        return None
    w = minus(punkt(p), punkt(a))
    t = skalar(w, d) / L
    if t <= TOLERANZ or t >= L - TOLERANZ:
        return None
    return t if betrag(minus(w, mal(t / L, d))) <= TOLERANZ else None


def kreuzen(p1, p2, q1, q2) -> bool:
    """Ob sich die Strecken p1-p2 und q1-q2 im Innern beider treffen."""
    r = minus(punkt(p2), punkt(p1))
    s = minus(punkt(q2), punkt(q1))
    w = minus(punkt(p1), punkt(q1))
    a, b, c, d, e = skalar(r, r), skalar(r, s), skalar(s, s), skalar(r, w), skalar(s, w)
    nenner = a * c - b * b
    if nenner <= 1e-12 * a * c:
        return False
    t, u = (b * e - c * d) / nenner, (a * e - b * d) / nenner
    if not (1e-9 < t < 1.0 - 1e-9 and 1e-9 < u < 1.0 - 1e-9):
        return False
    naechste = minus(plus(punkt(p1), mal(t, r)), plus(punkt(q1), mal(u, s)))
    return betrag(naechste) <= TOLERANZ
