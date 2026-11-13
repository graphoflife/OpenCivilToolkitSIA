"""
opencivil/decke/geometrie.py -- Vielecke in der Ebene der Decke.

VERANTWORTUNG:
Was die Streifenmethode an Geometrie braucht, und nur das: Fläche,
Schwerpunkt und Umlaufsinn eines Vielecks, ob ein Punkt darin liegt, die
Zerlegung in Dreiecke, das Abschneiden an einer Halbebene und an einem
konvexen Vieleck, und die Breite eines konvexen Vielecks quer zu einer
Richtung -- das Stück einer Last, das ein Streifen trägt.

PUNKTE UND VIELECKE:
Ein Punkt ist ein Paar ``(x, y)`` in m, ``x`` nach rechts, ``y`` nach oben.
Ein Vieleck ist eine Folge von Punkten ohne Wiederholung des ersten am Ende.
Was hier ein konvexes Vieleck verlangt, verlangt es im Gegenuhrzeigersinn;
:func:`gegen_uhrzeiger` dreht eines um.

RICHTUNG UND QUERRICHTUNG:
Ein Streifen läuft in Richtung ``n``; quer dazu steht ``t``, ``n`` um 90°
im Gegenuhrzeigersinn gedreht. Längs misst ``s = p·n``, quer ``τ = p·t``.
"""

from __future__ import annotations

import math
from typing import List, Optional, Sequence, Tuple

Punkt = Tuple[float, float]
Vieleck = Sequence[Punkt]

#: Was in m als gleich gilt -- das Zeichenfenster rundet auf ein Millionstel.
TOLERANZ = 1e-7


def richtung(winkel: float) -> Tuple[Punkt, Punkt]:
    """``(n, t)`` zu einem Winkel gegen die x-Achse, im Gegenuhrzeigersinn."""
    c, s = math.cos(winkel), math.sin(winkel)
    if abs(c) < 1e-15:
        c = 0.0
    if abs(s) < 1e-15:
        s = 0.0
    return (c, s), (-s, c)


def skalar(p: Punkt, r: Punkt) -> float:
    return p[0] * r[0] + p[1] * r[1]


def flaeche(v: Vieleck) -> float:
    """Die Fläche mit Vorzeichen: im Gegenuhrzeigersinn positiv."""
    a = 0.0
    for i, p in enumerate(v):
        q = v[(i + 1) % len(v)]
        a += p[0] * q[1] - q[0] * p[1]
    return 0.5 * a


def schwerpunkt(v: Vieleck) -> Punkt:
    """Der Flächenschwerpunkt -- bei einem entarteten Vieleck das Mittel der Ecken."""
    a = flaeche(v)
    if abs(a) < TOLERANZ ** 2:
        return (sum(p[0] for p in v) / len(v), sum(p[1] for p in v) / len(v))
    cx = cy = 0.0
    for i, p in enumerate(v):
        q = v[(i + 1) % len(v)]
        k = p[0] * q[1] - q[0] * p[1]
        cx += (p[0] + q[0]) * k
        cy += (p[1] + q[1]) * k
    return (cx / (6.0 * a), cy / (6.0 * a))


def gegen_uhrzeiger(v: Vieleck) -> List[Punkt]:
    return list(v) if flaeche(v) >= 0.0 else list(reversed(v))


def bereinigt(v: Vieleck) -> List[Punkt]:
    """Ohne doppelte Ecken und ohne Ecken auf einer Geraden mit ihren Nachbarn."""
    punkte: List[Punkt] = []
    for p in v:
        if not punkte or abs(p[0] - punkte[-1][0]) > TOLERANZ or abs(p[1] - punkte[-1][1]) > TOLERANZ:
            punkte.append((p[0], p[1]))
    while len(punkte) > 1 and abs(punkte[0][0] - punkte[-1][0]) <= TOLERANZ \
            and abs(punkte[0][1] - punkte[-1][1]) <= TOLERANZ:
        punkte.pop()
    geaendert = True
    while geaendert and len(punkte) >= 3:
        geaendert = False
        for i in range(len(punkte)):
            a, b, c = punkte[i - 1], punkte[i], punkte[(i + 1) % len(punkte)]
            kreuz = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
            laenge = math.hypot(c[0] - a[0], c[1] - a[1])
            if abs(kreuz) <= TOLERANZ * max(laenge, TOLERANZ):
                del punkte[i]
                geaendert = True
                break
    return punkte


def ist_konvex(v: Vieleck) -> bool:
    """Ob alle Ecken in dieselbe Richtung abbiegen -- ``v`` bereinigt."""
    vorzeichen = 0
    for i in range(len(v)):
        a, b, c = v[i - 1], v[i], v[(i + 1) % len(v)]
        kreuz = (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])
        if abs(kreuz) <= TOLERANZ ** 2:
            continue
        s = 1 if kreuz > 0 else -1
        if vorzeichen and s != vorzeichen:
            return False
        vorzeichen = s
    return True


def innen(p: Punkt, v: Vieleck) -> bool:
    """Ob ``p`` im Vieleck liegt -- auf dem Rand zählt als innen."""
    x, y = p
    for i, a in enumerate(v):
        b = v[(i + 1) % len(v)]
        if _auf_strecke(p, a, b):
            return True
    drin = False
    for i, a in enumerate(v):
        b = v[(i + 1) % len(v)]
        if (a[1] > y) != (b[1] > y):
            xs = a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1])
            if xs > x:
                drin = not drin
    return drin


def _auf_strecke(p: Punkt, a: Punkt, b: Punkt) -> bool:
    dx, dy = b[0] - a[0], b[1] - a[1]
    laenge = math.hypot(dx, dy)
    if laenge <= TOLERANZ:
        return math.hypot(p[0] - a[0], p[1] - a[1]) <= TOLERANZ
    abstand = abs(dx * (p[1] - a[1]) - dy * (p[0] - a[0])) / laenge
    u = (dx * (p[0] - a[0]) + dy * (p[1] - a[1])) / (laenge * laenge)
    return abstand <= TOLERANZ and -TOLERANZ / laenge <= u <= 1.0 + TOLERANZ / laenge


def dreiecke(v: Vieleck) -> List[List[Punkt]]:
    """
    Ein einfaches Vieleck in konvexe Stücke: ein konvexes bleibt ganz, ein
    anderes wird in Dreiecke zerlegt (Ohren abschneiden). Alle Stücke im
    Gegenuhrzeigersinn.
    """
    punkte = gegen_uhrzeiger(bereinigt(v))
    if len(punkte) < 3:
        return []
    if ist_konvex(punkte):
        return [punkte]
    heraus: List[List[Punkt]] = []
    rest = list(punkte)
    while len(rest) > 3:
        for i in range(len(rest)):
            a, b, c = rest[i - 1], rest[i], rest[(i + 1) % len(rest)]
            kreuz = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
            if kreuz <= TOLERANZ ** 2:
                continue
            ohr = [a, b, c]
            if any(_im_dreieck(p, ohr) for p in rest if p not in ohr):
                continue
            heraus.append(ohr)
            del rest[i]
            break
        else:
            raise ValueError("Das Vieleck schneidet sich selbst.")
    if abs(flaeche(rest)) > TOLERANZ ** 2:
        heraus.append(rest)
    return heraus


def _im_dreieck(p: Punkt, d: Sequence[Punkt]) -> bool:
    for i in range(3):
        a, b = d[i], d[(i + 1) % 3]
        if (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) < -TOLERANZ ** 2:
            return False
    return True


def halbebene(v: Vieleck, r: Punkt, c: float) -> List[Punkt]:
    """Was von ``v`` in ``p·r <= c`` liegt (Sutherland-Hodgman)."""
    heraus: List[Punkt] = []
    n = len(v)
    for i in range(n):
        p, q = v[i], v[(i + 1) % n]
        dp, dq = skalar(p, r) - c, skalar(q, r) - c
        if dp <= 0.0:
            heraus.append(p)
        if (dp < 0.0 < dq) or (dq < 0.0 < dp):
            u = dp / (dp - dq)
            heraus.append((p[0] + u * (q[0] - p[0]), p[1] + u * (q[1] - p[1])))
    return heraus


def schnitt(v: Vieleck, konvex: Vieleck) -> List[Punkt]:
    """``v`` geschnitten mit dem konvexen Vieleck ``konvex`` (Gegenuhrzeigersinn) -- leer, wenn nichts bleibt."""
    heraus = list(v)
    for i, a in enumerate(konvex):
        b = konvex[(i + 1) % len(konvex)]
        # innen liegt links der Kante: (b - a) × (p - a) >= 0
        r = (b[1] - a[1], -(b[0] - a[0]))
        heraus = halbebene(heraus, r, skalar(a, r))
        if len(heraus) < 3:
            return []
    return _flaechig(heraus)


def im_band(v: Vieleck, t: Punkt, von: float, bis: float) -> List[Punkt]:
    """Was von ``v`` im Band ``von <= p·t <= bis`` liegt."""
    heraus = halbebene(v, t, bis)
    if len(heraus) >= 3:
        heraus = halbebene(heraus, (-t[0], -t[1]), -von)
    return _flaechig(heraus) if len(heraus) >= 3 else []


def _flaechig(v: List[Punkt]) -> List[Punkt]:
    v = bereinigt(v)
    return v if len(v) >= 3 and abs(flaeche(v)) > TOLERANZ ** 2 else []


def bereich(v: Vieleck, r: Punkt) -> Tuple[float, float]:
    """Kleinstes und grösstes ``p·r`` über die Ecken."""
    werte = [skalar(p, r) for p in v]
    return min(werte), max(werte)


def breite(v: Vieleck, n: Punkt) -> List[Tuple[float, float]]:
    """
    Wie breit das konvexe Vieleck quer zu ``n`` ist, längs ``s = p·n``: die
    Paare ``(s, b)`` an jeder Ecke, aufsteigend in ``s``. Dazwischen ist die
    Breite linear -- die Ränder eines konvexen Vielecks sind dort Geraden.
    Eine Kante quer zu ``n`` am Anfang oder Ende zählt dort mit ihrer Länge.
    """
    t = (-n[1], n[0])
    ecken = [(skalar(p, n), skalar(p, t)) for p in v]
    stellen: List[float] = []
    for s in sorted(e[0] for e in ecken):
        if not stellen or s - stellen[-1] > TOLERANZ:
            stellen.append(s)
    heraus = []
    for s in stellen:
        quer: List[float] = []
        for i, (sa, ta) in enumerate(ecken):
            sb, tb = ecken[(i + 1) % len(ecken)]
            if abs(sb - sa) <= TOLERANZ:
                if abs(sa - s) <= TOLERANZ:
                    quer.extend((ta, tb))
            elif min(sa, sb) - TOLERANZ <= s <= max(sa, sb) + TOLERANZ:
                u = min(1.0, max(0.0, (s - sa) / (sb - sa)))
                quer.append(ta + u * (tb - ta))
        heraus.append((s, max(quer) - min(quer) if quer else 0.0))
    return heraus


def strecke_in_konvex(a: Punkt, b: Punkt, konvex: Vieleck) -> Optional[Tuple[float, float]]:
    """
    Welcher Teil der Strecke ``a → b`` im konvexen Vieleck liegt, als
    Parameter ``(u0, u1)`` mit ``p = a + u·(b - a)`` -- ``None``, wenn keiner
    (Cyrus-Beck).
    """
    u0, u1 = 0.0, 1.0
    d = (b[0] - a[0], b[1] - a[1])
    for i, p in enumerate(konvex):
        q = konvex[(i + 1) % len(konvex)]
        r = (q[1] - p[1], -(q[0] - p[0]))      # aussen positiv
        zaehler = skalar(p, r) - skalar(a, r)
        nenner = skalar(d, r)
        if abs(nenner) <= 1e-12 * math.hypot(*d) * math.hypot(*r):
            if zaehler < -TOLERANZ * math.hypot(*r):
                return None
            continue
        u = zaehler / nenner
        if nenner > 0.0:
            u1 = min(u1, u)
        else:
            u0 = max(u0, u)
        if u0 > u1:
            return None
    return (u0, u1)


def strecke_im_vieleck(a: Punkt, b: Punkt, v: Vieleck) -> List[Tuple[float, float]]:
    """
    Welche Teile der Strecke ``a → b`` im Vieleck liegen -- auch einem nicht
    konvexen --, als Parameter ``(u0, u1)``. Ein Stück auf dem Rand zählt.
    """
    d = (b[0] - a[0], b[1] - a[1])
    laenge = math.hypot(*d)
    if laenge <= TOLERANZ:
        return []
    folge = schnittstellen(a, b, v)
    heraus: List[Tuple[float, float]] = []
    for u0, u1 in zip(folge, folge[1:]):
        if (u1 - u0) * laenge <= TOLERANZ:
            continue
        m = 0.5 * (u0 + u1)
        if innen((a[0] + m * d[0], a[1] + m * d[1]), v):
            if heraus and abs(heraus[-1][1] - u0) * laenge <= TOLERANZ:
                heraus[-1] = (heraus[-1][0], u1)
            else:
                heraus.append((u0, u1))
    return heraus


def schnittstellen(a: Punkt, b: Punkt, v: Vieleck) -> List[float]:
    """
    Wo die Strecke ``a → b`` den Rand des Vielecks trifft oder an einer Ecke
    vorbeigeht, als Parameter in ``[0, 1]`` -- mit 0 und 1, aufsteigend.
    Zwischen zwei Stellen liegt sie ganz innen, ganz aussen oder ganz auf dem Rand.
    """
    d = (b[0] - a[0], b[1] - a[1])
    laenge = math.hypot(*d)
    stellen = {0.0, 1.0}
    if laenge <= TOLERANZ:
        return sorted(stellen)
    for i, p in enumerate(v):
        q = v[(i + 1) % len(v)]
        e = (q[0] - p[0], q[1] - p[1])
        nenner = d[0] * e[1] - d[1] * e[0]
        w = (p[0] - a[0], p[1] - a[1])
        if abs(nenner) <= 1e-12 * laenge * math.hypot(*e):
            for ecke in (p, q):
                u = skalar((ecke[0] - a[0], ecke[1] - a[1]), d) / (laenge * laenge)
                if 0.0 < u < 1.0:
                    stellen.add(u)
            continue
        u = (w[0] * e[1] - w[1] * e[0]) / nenner
        k = (w[0] * d[1] - w[1] * d[0]) / nenner
        if -1e-12 <= k <= 1.0 + 1e-12 and 0.0 < u < 1.0:
            stellen.add(u)
    return sorted(stellen)


def rechteck(a: Punkt, b: Punkt, breite_: float) -> List[Punkt]:
    """Das Rechteck um die Strecke ``a → b``, je ``breite_/2`` zu beiden Seiten -- im Gegenuhrzeigersinn."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    laenge = math.hypot(dx, dy)
    qx, qy = -dy / laenge * breite_ / 2.0, dx / laenge * breite_ / 2.0
    return gegen_uhrzeiger([(a[0] - qx, a[1] - qy), (b[0] - qx, b[1] - qy),
                            (b[0] + qx, b[1] + qy), (a[0] + qx, a[1] + qy)])


def achsrechteck(mitte: Punkt, lx: float, ly: float) -> List[Punkt]:
    """Das Rechteck ``lx × ly`` um ``mitte``, achsparallel, im Gegenuhrzeigersinn."""
    x, y = mitte
    return [(x - lx / 2.0, y - ly / 2.0), (x + lx / 2.0, y - ly / 2.0),
            (x + lx / 2.0, y + ly / 2.0), (x - lx / 2.0, y + ly / 2.0)]


def vereinigt(intervalle: Sequence[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """Intervalle, die sich berühren oder überlappen, zu einem."""
    heraus: List[Tuple[float, float]] = []
    for a, b in sorted(intervalle):
        if heraus and a <= heraus[-1][1] + TOLERANZ:
            heraus[-1] = (heraus[-1][0], max(heraus[-1][1], b))
        else:
            heraus.append((a, b))
    return heraus
