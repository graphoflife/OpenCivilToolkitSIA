"""
opencivil/fachwerkmodell/skelett.py -- aus der Form des SIMP die möglichen Stäbe eines Fachwerks.

VERANTWORTUNG:
Was das Verfahren SIMP (:mod:`~opencivil.fachwerkmodell.simp`) an
Material verteilt hat, als Fachwerk gelesen (:func:`moegliche_staebe`),
in den Schritten von Xia, Langelaar & Hendriks (2020), Abschnitt 2.3 --
ab dem dritten angepasst:

1. Zur Form gehört ein Element, wenn seine gefilterte Dichte mindestens
   0.5 ist; die Elemente unter Lagern und Lasten immer.
2. Die Form wird ausgedünnt, bis nur ihre Mittellinien bleiben, ein
   Element breit -- nach Zhang & Suen (1984). Äste, die frei enden, fallen
   weg, und was an keinem Lager und keiner Last hängt: sie tragen nichts.
3. Knoten sind, wo eine Linie endet oder sich verzweigt, dazu jedes Lager
   und jede Last genau an ihrem Punkt. Biegt eine Linie zwischen zwei
   Knoten mehr als 1.5 Netzweiten von der Geraden ab, bekommt sie dort
   einen -- nach Douglas & Peucker (1973).
4. Liegen Knoten näher als 5 % der kürzeren Seite des Rechtecks um die
   Scheiben, werden sie einer. Steht ein Stab weniger als 10° schief zur
   Senkrechten oder Waagrechten durch ein Lager oder eine Last, rückt sein
   anderer Knoten genau darauf.

DIE MÖGLICHEN STÄBE:
Die Quelle verbindet die Knoten längs der Linien; das allein wäre oft
beweglich, solange die Form noch nicht ganz klar ist. Hier ist darum jedes
Paar von Knoten ein möglicher Stab, wenn er ganz im Material liegt und
durch keinen dritten Knoten geht. Er kostet in der Optimierung umso mehr,
je mehr von ihm neben der Form liegt -- um ein Element erweitert --, ganz
daneben zehnmal so viel wie ganz in ihr. So folgt das Fachwerk der Form,
wo sie trägt, und hilft sich mit einem Stab daneben, wo sie es nicht tut.
Die Kräfte bestimmt die Optimierung der Ground Structure
(:mod:`~opencivil.fachwerkmodell.suche`).

Aus der Quelle sind die Schwelle 0.5 und die 5 %; die 1.5 Netzweiten, die
10°, das Zehnfache, das Wegfallen der freien Äste und die Paare sind nach
Vorgabe, nicht nachgeschlagen.
"""

from __future__ import annotations

import math
from collections import deque
from typing import Dict, List, Sequence, Set, Tuple

from opencivil.decke import geometrie as geo
from opencivil.decke.geometrie import Punkt
from opencivil.fachwerkmodell.grundstruktur import Grundstruktur, aus_staeben, im_material
from opencivil.fachwerkmodell.simp import Netz, gefiltert

#: Wo die Schritte nachzulesen sind.
QUELLE = "Xia, Langelaar & Hendriks (2020), Abschnitt 2.3"

#: Ab dieser gefilterten Dichte gehört ein Element zur Form.
VOLL_AB = 0.5

#: Wie nahe zwei Knoten liegen dürfen, bezogen auf die kürzere Seite des Rechtecks -- aus der Quelle.
NAHE = 0.05

#: Bis zu welchem Winkel in Grad ein Stab an einem Lager oder einer Last
#: senkrecht oder waagrecht gerückt wird -- nach Vorgabe, nicht nachgeschlagen.
SCHIEF = 10.0

#: Ab wie vielen Netzweiten Abstand von der Geraden eine Linie einen Knick hat --
#: so breit verwischt der Filter die Form (nach Vorgabe, nicht nachgeschlagen).
KNICK = 1.5

#: Wie viel mal mehr ein Stab neben der Form kostet als in ihr -- nach Vorgabe, nicht nachgeschlagen.
NEBEN = 10.0

#: Die acht Nachbarn eines Elements, im Kreis von oben an.
RING = ((0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1))

Platz = Tuple[int, int]


def moegliche_staebe(n: Netz, x: Sequence[float]) -> Grundstruktur:
    """Die möglichen Stäbe der Form mit den Dichten ``x``, je mit ihren Kosten -- siehe Dateikopf."""
    rho = gefiltert(n, x)
    im_netz = set(n.elemente)
    form = {e for e, r in zip(n.elemente, rho) if r >= VOLL_AB}
    # Je Lager und Last ihr Punkt, jeder einmal, und das Element darunter.
    punkte = list(dict.fromkeys([l.ort for l in n.modell.lager] + [f.ort for f in n.modell.lasten]))
    unter: Dict[Platz, int] = {}
    for k, p in enumerate(punkte):
        unter.setdefault(_element_bei(n, im_netz, p), k)
    form |= unter.keys()
    linien = mittellinien(form, set(unter))
    knoten, zu = _knoten(n, linien, unter, punkte)
    staebe = _staebe_der_linien(n, linien, knoten, zu)
    knoten, staebe = _zusammengefasst(n, knoten, staebe, len(punkte))
    knoten = _ausgerichtet(knoten, staebe, len(punkte))
    weiter = _erweitert(form, im_netz)
    umrisse = [u.ecken for u in (*n.modell.scheiben, *n.modell.loecher)]
    paare = [(a, b) for a in range(len(knoten)) for b in range(a + 1, len(knoten))
             if math.dist(knoten[a], knoten[b]) > geo.TOLERANZ
             and im_material(n.modell, umrisse, knoten[a], knoten[b])
             and not any(_auf(knoten[k], knoten[a], knoten[b])
                         for k in range(len(knoten)) if k not in (a, b))]
    aufschlag = [1.0 + (NEBEN - 1.0) * _daneben(n, weiter, knoten[a], knoten[b]) for a, b in paare]
    return aus_staeben(n.modell, knoten, paare, n.weite, aufschlag)


def _element_bei(n: Netz, im_netz: Set[Platz], p: Punkt) -> Platz:
    """Das Element, in dem ``p`` liegt -- oder, liegt es in keinem, das mit der nächsten Mitte."""
    e = (math.floor((p[0] - n.ursprung[0]) / n.weite), math.floor((p[1] - n.ursprung[1]) / n.weite))
    if e in im_netz:
        return e
    return min(n.elemente, key=lambda k: math.dist(n.mitte(k), p))


def ausgeduennt(pixel: Set[Platz], fest: Set[Platz]) -> Set[Platz]:
    """
    Die Mittellinien der Elemente ``pixel`` nach Zhang & Suen (1984): in zwei
    Teilschritten fällt weg, was am Rand liegt, die Linie nicht trennt und
    kein Ende ist -- bis nichts mehr wegfällt. ``fest`` bleibt.
    """
    p = set(pixel)
    while True:
        weg_ganz = False
        for teil in (0, 1):
            weg = []
            for i, j in p:
                if (i, j) in fest:
                    continue
                n = [(i + di, j + dj) in p for di, dj in RING]
                if not 2 <= sum(n) <= 6 or _kreuzungen(n) != 1:
                    continue
                o, _, r, _, u, _, l, _ = n
                if teil == 0 and (o and r and u or r and u and l):
                    continue
                if teil == 1 and (o and r and l or o and u and l):
                    continue
                weg.append((i, j))
            if weg:
                p.difference_update(weg)
                weg_ganz = True
        if not weg_ganz:
            return p


def mittellinien(form: Set[Platz], fest: Set[Platz]) -> Set[Platz]:
    """
    Die Mittellinien der ``form``, ein Element breit: ausgedünnt
    (:func:`ausgeduennt`), dann ohne die Elemente, die keine Verbindung
    tragen -- an einer Stufe einer schrägen Linie bleibt sonst eines zu viel
    --, dann ohne die Äste, die frei enden: ohne Lager und Last am Ende
    trägt ein Ast nichts. Was dann an keinem Lager und keiner Last hängt,
    fällt ganz weg. ``fest`` bleibt.
    """
    p = ausgeduennt(form, fest)
    while True:
        weg = False
        for e in sorted(p, key=lambda k: (k[1], k[0])):
            if e in fest:
                continue
            nachbarn = [(e[0] + di, e[1] + dj) in p for di, dj in RING]
            if sum(nachbarn) <= 1 or _einfach(nachbarn):
                p.discard(e)
                weg = True
        if not weg:
            break
    gesehen: Set[Platz] = set()
    for start in sorted(fest & p, key=lambda k: (k[1], k[0])):
        if start not in gesehen:
            _zusammenhang(start, p, gesehen)
    return gesehen


def _einfach(n: Sequence[bool]) -> bool:
    """
    Ob ein Element einer Linie wegfallen kann, ohne dass sie zerfällt oder
    ein Loch entsteht -- seine Nachbarn ``n`` im Kreis: die Zahl von Yokoi
    für Nachbarn auch über Eck ist eins. Am Ende einer Linie ist sie auch
    eins; dort entscheidet der Aufrufer.
    """
    leer = [not v for v in n]
    return sum(leer[k] and not (leer[k + 1] and leer[(k + 2) % 8]) for k in (0, 2, 4, 6)) == 1


def _kreuzungen(n: Sequence[bool]) -> int:
    """Wie oft der Kreis der Nachbarn von leer auf voll wechselt -- 1 am Ende einer Linie, 2 mitten in ihr."""
    return sum(1 for k in range(8) if not n[k] and n[(k + 1) % 8])


def _knoten(n: Netz, linien: Set[Platz], unter: Dict[Platz, int],
            punkte: Sequence[Punkt]) -> Tuple[List[Punkt], Dict[Platz, int]]:
    """
    Die Knoten der Linien -- zuerst die ``punkte`` der Lager und Lasten --
    und je Element einer Linie, zu welchem Knoten es gehört; die Elemente
    mitten in einer Linie gehören zu keinem. Wo Enden und Verzweigungen
    aneinanderstossen, ist es ein Knoten in ihrer Mitte -- oder, ist ein
    Element unter einem Lager oder einer Last dabei, an dessen Punkt.
    """
    knoten = list(punkte)
    ecke = {e for e in linien if e in unter
            or sum((e[0] + di, e[1] + dj) in linien for di, dj in RING) != 2}
    zu: Dict[Platz, int] = {}
    gesehen: Set[Platz] = set()
    for start in sorted(ecke, key=lambda e: (e[1], e[0])):
        if start in gesehen:
            continue
        gruppe = _zusammenhang(start, ecke, gesehen)
        fest = sorted({unter[e] for e in gruppe if e in unter})
        if fest:
            for e in gruppe:
                zu[e] = min(fest, key=lambda k: math.dist(knoten[k], n.mitte(e)))
        else:
            zu.update({e: len(knoten) for e in gruppe})
            mitten = [n.mitte(e) for e in gruppe]
            knoten.append((sum(p[0] for p in mitten) / len(mitten),
                           sum(p[1] for p in mitten) / len(mitten)))
    return knoten, zu


def _zusammenhang(start: Platz, menge: Set[Platz], gesehen: Set[Platz]) -> List[Platz]:
    """Die Elemente von ``menge``, die über Nachbarn mit ``start`` zusammenhängen."""
    gesehen.add(start)
    gruppe, schlange = [start], deque([start])
    while schlange:
        i, j = schlange.popleft()
        for di, dj in RING:
            e = (i + di, j + dj)
            if e in menge and e not in gesehen:
                gesehen.add(e)
                gruppe.append(e)
                schlange.append(e)
    return gruppe


def _staebe_der_linien(n: Netz, linien: Set[Platz], knoten: List[Punkt],
                       zu: Dict[Platz, int]) -> Set[Tuple[int, int]]:
    """
    Je Stück einer Linie zwischen zwei Knoten gerade Stäbe von Knoten zu
    Knoten, wie die Streben eines Fachwerkmodells: biegt das Stück mehr als
    :data:`KNICK` Netzweiten von der Geraden ab, bekommt es dort einen
    Knoten, und jede Hälfte wird ebenso geprüft (:func:`_knicke`). So wird
    auch ein Stück, das zu seinem Knoten zurückkehrt -- um ein Loch der Form
    --, ein Vieleck. Stossen zwei Knoten direkt aneinander, ein Stab; trifft
    ein Stück mehr als zwei Knoten, je zwei ein Stab.
    """
    staebe: Set[Tuple[int, int]] = set()
    for e, k in zu.items():
        for di, dj in RING:
            m = zu.get((e[0] + di, e[1] + dj))
            if m is not None and m != k:
                staebe.add((min(k, m), max(k, m)))
    frei = linien - zu.keys()
    gesehen: Set[Platz] = set()
    for start in sorted(frei, key=lambda e: (e[1], e[0])):
        if start in gesehen:
            continue
        stueck = _zusammenhang(start, frei, gesehen)
        enden = sorted({zu[(e[0] + di, e[1] + dj)] for e in stueck for di, dj in RING
                        if (e[0] + di, e[1] + dj) in zu})
        if len(enden) > 2:
            staebe.update((a, b) for i, a in enumerate(enden) for b in enden[i + 1:])
            continue
        a, b = enden[0], enden[-1]
        anfang = [e for e in stueck if any(zu.get((e[0] + di, e[1] + dj)) == a for di, dj in RING)]
        weg = [knoten[a], *map(n.mitte, _der_reihe_nach(anfang, set(stueck))), knoten[b]]
        folge = [a]
        for k in _knicke(weg, KNICK * n.weite):
            knoten.append(weg[k])
            folge.append(len(knoten) - 1)
        folge.append(b)
        staebe.update((min(p, q), max(p, q)) for p, q in zip(folge, folge[1:]) if p != q)
    return staebe


def _knicke(weg: Sequence[Punkt], grenze: float) -> List[int]:
    """
    Wo ein Weg geknickt ist, in seiner Folge: der Punkt, der am weitesten
    von der Geraden zwischen seinen Enden liegt, wenn mehr als ``grenze`` --
    dann ebenso in den beiden Hälften, nach Douglas & Peucker (1973). Sind
    die Enden ein Punkt, gilt der Abstand zu ihm.
    """
    if len(weg) < 3:
        return []
    a, b = weg[0], weg[-1]
    k, weit = max(((i, _abstand(p, a, b)) for i, p in enumerate(weg[1:-1], start=1)),
                  key=lambda t: t[1])
    if weit <= grenze:
        return []
    return [*_knicke(weg[:k + 1], grenze), k, *(k + i for i in _knicke(weg[k:], grenze))]


def _abstand(p: Punkt, a: Punkt, b: Punkt) -> float:
    """Wie weit ``p`` von der Geraden durch ``a`` und ``b`` liegt -- sind sie ein Punkt, von ihm."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    l = math.hypot(dx, dy)
    if l <= geo.TOLERANZ:
        return math.dist(p, a)
    return abs((p[0] - a[0]) * dy - (p[1] - a[1]) * dx) / l


def _der_reihe_nach(anfang: Sequence[Platz], stueck: Set[Platz]) -> List[Platz]:
    """Die Elemente eines Stücks nach ihrem Abstand von ``anfang`` längs des Stücks."""
    gesehen = set(anfang)
    folge, schlange = list(anfang), deque(anfang)
    while schlange:
        i, j = schlange.popleft()
        for di, dj in RING:
            e = (i + di, j + dj)
            if e in stueck and e not in gesehen:
                gesehen.add(e)
                folge.append(e)
                schlange.append(e)
    return folge


def _ausgerichtet(knoten: List[Punkt], staebe: Set[Tuple[int, int]], fest: int) -> List[Punkt]:
    """
    Weicht ein Stab zu einem Lager oder einer Last (den ersten ``fest``)
    weniger als :data:`SCHIEF` von der Senkrechten oder Waagrechten ab,
    rückt sein anderer Knoten genau auf sie: die Mittellinie trifft den
    Punkt oft nur auf ein, zwei Elemente genau, und schon so wenig schief
    hielte ein Lager, das nur in einer Richtung hält, den Stab nicht.
    """
    neu = list(knoten)
    steil = math.tan(math.radians(SCHIEF))
    for a, b in sorted(staebe):
        if (a < fest) == (b < fest):
            continue
        p, q = (a, b) if a < fest else (b, a)
        dx, dy = neu[q][0] - neu[p][0], neu[q][1] - neu[p][1]
        if abs(dx) <= steil * abs(dy):
            neu[q] = (neu[p][0], neu[q][1])
        elif abs(dy) <= steil * abs(dx):
            neu[q] = (neu[q][0], neu[p][1])
    return neu


def _zusammengefasst(n: Netz, knoten: List[Punkt], staebe: Set[Tuple[int, int]],
                     fest: int) -> Tuple[List[Punkt], Set[Tuple[int, int]]]:
    """
    Knoten näher als :data:`NAHE` als einer: in ihrem Mittel -- ist einer
    ein Lager oder eine Last (die ersten ``fest``), an dessen Punkt; zwei
    solche bleiben zwei.
    """
    xs = [p[0] for s in n.modell.scheiben for p in s.ecken]
    ys = [p[1] for s in n.modell.scheiben for p in s.ecken]
    grenze = NAHE * min(max(xs) - min(xs), max(ys) - min(ys))
    wurzel = list(range(len(knoten)))

    def finde(k: int) -> int:
        while wurzel[k] != k:
            wurzel[k] = wurzel[wurzel[k]]
            k = wurzel[k]
        return k

    for a in range(len(knoten)):
        for b in range(a + 1, len(knoten)):
            ra, rb = finde(a), finde(b)
            if ra != rb and math.dist(knoten[a], knoten[b]) < grenze and not (ra < fest and rb < fest):
                wurzel[max(ra, rb)] = min(ra, rb)
    gruppen: Dict[int, List[int]] = {}
    for k in range(len(knoten)):
        gruppen.setdefault(finde(k), []).append(k)
    neu: List[Punkt] = []
    platz: Dict[int, int] = {}
    for r in sorted(gruppen):
        g = gruppen[r]
        platz.update({k: len(neu) for k in g})
        neu.append(knoten[r] if r < fest else (sum(knoten[k][0] for k in g) / len(g),
                                               sum(knoten[k][1] for k in g) / len(g)))
    return neu, {(min(platz[a], platz[b]), max(platz[a], platz[b])) for a, b in staebe
                 if platz[a] != platz[b]}


def _erweitert(form: Set[Platz], im_netz: Set[Platz]) -> Set[Platz]:
    """Die Form und je Element ihre Nachbarn, soweit sie im Netz sind."""
    return form | {(i + di, j + dj) for i, j in form for di, dj in RING if (i + di, j + dj) in im_netz}


def _daneben(n: Netz, form: Set[Platz], a: Punkt, b: Punkt) -> float:
    """Welcher Teil der Strecke ``a → b`` neben den Elementen ``form`` liegt -- geprüft alle Viertel einer Netzweite."""
    teile = max(1, math.ceil(4.0 * math.dist(a, b) / n.weite))
    x0, y0 = n.ursprung
    neben = 0
    for k in range(teile + 1):
        t = k / teile
        x, y = a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])
        i = min(n.spalten - 1, math.floor((x - x0) / n.weite))
        j = min(n.zeilen - 1, math.floor((y - y0) / n.weite))
        neben += (i, j) not in form
    return neben / (teile + 1)


def _auf(p: Punkt, a: Punkt, b: Punkt) -> bool:
    """Ob ``p`` auf der Strecke ``a → b`` liegt, nicht an ihren Enden -- bis auf Rundung."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    l2 = dx * dx + dy * dy
    t = ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / l2
    return 1e-9 < t < 1.0 - 1e-9 and abs((p[0] - a[0]) * dy - (p[1] - a[1]) * dx) <= 1e-9 * l2
