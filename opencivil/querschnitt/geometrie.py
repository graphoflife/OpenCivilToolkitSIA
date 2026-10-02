"""
opencivil/querschnitt/geometrie.py -- Ebene Geometrie eines gezeichneten Querschnitts.

VERANTWORTUNG:
Alles, was aus der Zeichnung folgt, bevor ein Werkstoff ins Spiel kommt:
Flaeche, Schwerpunkt und Traegheitsmomente eines Polygons, wie Polygone
ineinanderliegen, wo die Staebe einer Stablinie liegen, ob ein Stab ganz im
Beton steckt und wo eine Gerade ein Polygon schneidet.

WARUM HIER UND NICHT IN DER OBERFLAECHE:
Das Zeichenfenster zeigt Stabpositionen, tatsaechliche Teilungen und
Fehlermeldungen. Gerechnet wird das hier; die Oberflaeche zeichnet, was der
Kern sagt. Eine zweite Fassung der Teilungsregel in JavaScript liefe frueher
oder spaeter auseinander.

EINHEITEN:
Keine. Gerechnet wird in der Einheit der Punkte -- in der Beschreibung sind
das Millimeter --, Flaechen kommen im Quadrat dieser Einheit zurueck.
Umgerechnet wird einmal am Rand, dort wo die Fasern entstehen.

KOORDINATEN:
y nach rechts, z nach oben. Ein Polygon ist eine Folge von Ecken, die erste
wird am Ende nicht wiederholt. Ob es links- oder rechtsherum laeuft, ist gleich.

INEINANDER LIEGEN:
Liegt ein Polygon ganz in einem anderen, ersetzt es dieses dort -- so entsteht
eine Aussparung, spaeter ein Stahlprofil im Beton. Beruehren duerfen sich
Polygone, auch entlang einer ganzen Kante. Teilweise ueberlappen duerfen sie
nicht: welches Material dort gilt, waere eine Willkuer.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Sequence, Tuple

Punkt = Tuple[float, float]

#: Wie nahe zwei Lagen beieinander liegen duerfen, um als gleich zu gelten, in
#: der Einheit der Punkte. Ein Millionstel Millimeter liegt weit unter allem,
#: was jemand zeichnet, und weit ueber dem Rauschen gerechneter Kreispunkte.
TOLERANZ = 1e-6


class GeometrieFehler(ValueError):
    """
    Eine Zeichnung, aus der sich nichts rechnen laesst -- mit dem Grund und
    den Elementen, die er betrifft. Das Zeichenfenster faerbt sie ein.
    """

    def __init__(self, text: str, elemente: Sequence[str] = ()) -> None:
        super().__init__(text)
        self.elemente = tuple(elemente)


# ===========================================================================
# Flaechenwerte
# ===========================================================================


@dataclass(frozen=True)
class Flaechenwerte:
    """
    Flaeche, Schwerpunkt und Traegheitsmomente, bezogen auf den Schwerpunkt.

    ``I_y`` ist das Moment um die y-Achse, also ``∫(z - z_S)² dA``; ``I_z``
    entsprechend ``∫(y - y_S)² dA`` und ``I_yz = ∫(y - y_S)(z - z_S) dA``.
    """

    A: float
    y_S: float
    z_S: float
    I_y: float
    I_z: float
    I_yz: float


#: Ein Querschnitt ohne Flaeche -- der Anfang jeder Summe.
NULL = Flaechenwerte(A=0.0, y_S=0.0, z_S=0.0, I_y=0.0, I_z=0.0, I_yz=0.0)


def flaeche(punkte: Sequence[Punkt]) -> float:
    """Die Flaeche mit Vorzeichen: positiv, wenn das Polygon linksherum laeuft."""
    summe = 0.0
    for (y1, z1), (y2, z2) in _kanten(punkte):
        summe += y1 * z2 - y2 * z1
    return summe / 2.0


def flaechenwerte(punkte: Sequence[Punkt]) -> Flaechenwerte:
    """
    Die Werte eines einfachen Polygons, nach den Formeln aus dem Satz von Gauss.

    Mit ``c_i = y_i·z_(i+1) - y_(i+1)·z_i`` gilt, bezogen auf den Ursprung::

        A     = 1/2  · Σ c_i
        S_z   = 1/6  · Σ (y_i + y_(i+1)) · c_i          = A·y_S
        S_y   = 1/6  · Σ (z_i + z_(i+1)) · c_i          = A·z_S
        I_yy  = 1/12 · Σ (z_i² + z_i·z_(i+1) + z_(i+1)²) · c_i
        I_zz  = 1/12 · Σ (y_i² + y_i·y_(i+1) + y_(i+1)²) · c_i
        I_yz0 = 1/24 · Σ (y_i·z_(i+1) + 2·y_i·z_i + 2·y_(i+1)·z_(i+1)
                          + y_(i+1)·z_i) · c_i

    Laeuft das Polygon rechtsherum, kehren alle Summen das Vorzeichen; geteilt
    durch das Vorzeichen der Flaeche ist das gleichgueltig. Danach mit Steiner
    auf den Schwerpunkt.
    """
    A = s_y = s_z = i_yy = i_zz = i_yz = 0.0
    for (y1, z1), (y2, z2) in _kanten(punkte):
        c = y1 * z2 - y2 * z1
        A += c
        s_z += (y1 + y2) * c
        s_y += (z1 + z2) * c
        i_yy += (z1 * z1 + z1 * z2 + z2 * z2) * c
        i_zz += (y1 * y1 + y1 * y2 + y2 * y2) * c
        i_yz += (y1 * z2 + 2.0 * y1 * z1 + 2.0 * y2 * z2 + y2 * z1) * c
    A /= 2.0
    if abs(A) <= TOLERANZ:
        raise GeometrieFehler("Das Polygon hat keine Fläche.")
    y_S = s_z / 6.0 / A
    z_S = s_y / 6.0 / A
    vorzeichen = 1.0 if A > 0 else -1.0
    flaeche_betrag = abs(A)
    return Flaechenwerte(
        A=flaeche_betrag,
        y_S=y_S,
        z_S=z_S,
        I_y=vorzeichen * i_yy / 12.0 - flaeche_betrag * z_S * z_S,
        I_z=vorzeichen * i_zz / 12.0 - flaeche_betrag * y_S * y_S,
        I_yz=vorzeichen * i_yz / 24.0 - flaeche_betrag * y_S * z_S,
    )


def summe(teile: Sequence[Tuple[float, Flaechenwerte]]) -> Flaechenwerte:
    """
    Die Werte eines zusammengesetzten Querschnitts.

    ``teile`` sind Paare aus Gewicht und Werten. Das Gewicht ist +1 fuer eine
    Flaeche, die zaehlt, und -1 fuer eine, die herausgenommen wird -- eine
    Aussparung. Ueber die Momente um den Ursprung summiert und dann wieder auf
    den gemeinsamen Schwerpunkt bezogen (Steiner hin und zurueck).
    """
    A = s_y = s_z = i_yy = i_zz = i_yz = 0.0
    for gewicht, w in teile:
        a = gewicht * w.A
        A += a
        s_z += a * w.y_S
        s_y += a * w.z_S
        i_yy += gewicht * w.I_y + a * w.z_S * w.z_S
        i_zz += gewicht * w.I_z + a * w.y_S * w.y_S
        i_yz += gewicht * w.I_yz + a * w.y_S * w.z_S
    if A <= TOLERANZ:
        raise GeometrieFehler("Der Querschnitt hat keine Fläche.")
    y_S, z_S = s_z / A, s_y / A
    return Flaechenwerte(A=A, y_S=y_S, z_S=z_S,
                         I_y=i_yy - A * z_S * z_S,
                         I_z=i_zz - A * y_S * y_S,
                         I_yz=i_yz - A * y_S * z_S)


# ===========================================================================
# Punkte, Kanten, Schnitte
# ===========================================================================


def _kanten(punkte: Sequence[Punkt]):
    """Die Kanten eines Polygons, die letzte schliesst zum ersten Punkt."""
    n = len(punkte)
    for i in range(n):
        yield punkte[i], punkte[(i + 1) % n]


def _kreuz(o: Punkt, a: Punkt, b: Punkt) -> float:
    """Das Kreuzprodukt (a - o) × (b - o): > 0 heisst, b liegt links von o→a."""
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def abstand_zur_strecke(p: Punkt, a: Punkt, b: Punkt) -> float:
    """Der kuerzeste Abstand von ``p`` zur Strecke ``a``–``b``."""
    dy, dz = b[0] - a[0], b[1] - a[1]
    laenge2 = dy * dy + dz * dz
    if laenge2 == 0.0:
        return math.hypot(p[0] - a[0], p[1] - a[1])
    t = ((p[0] - a[0]) * dy + (p[1] - a[1]) * dz) / laenge2
    t = min(1.0, max(0.0, t))
    return math.hypot(p[0] - (a[0] + t * dy), p[1] - (a[1] + t * dz))


def abstand_zum_rand(p: Punkt, punkte: Sequence[Punkt]) -> float:
    """Der kuerzeste Abstand von ``p`` zum Rand des Polygons."""
    return min(abstand_zur_strecke(p, a, b) for a, b in _kanten(punkte))


def lage(p: Punkt, punkte: Sequence[Punkt]) -> int:
    """
    Wo ``p`` liegt: +1 innen, 0 auf dem Rand, -1 aussen.

    Erst der Rand mit Toleranz, dann ein Strahl nach rechts: jede Kante, die er
    kreuzt, wechselt zwischen innen und aussen. Halb offene Kanten (unten
    eingeschlossen, oben nicht), damit ein Strahl durch eine Ecke nicht doppelt
    zaehlt.
    """
    if abstand_zum_rand(p, punkte) <= TOLERANZ:
        return 0
    y, z = p
    innen = False
    for (y1, z1), (y2, z2) in _kanten(punkte):
        if (z1 > z) != (z2 > z):
            y_schnitt = y1 + (z - z1) * (y2 - y1) / (z2 - z1)
            if y_schnitt > y:
                innen = not innen
    return 1 if innen else -1


def echt_geschnitten(a1: Punkt, a2: Punkt, b1: Punkt, b2: Punkt) -> bool:
    """
    Ob sich zwei Strecken im Innern beider kreuzen.

    Beruehren -- ein Endpunkt auf der anderen Strecke, gemeinsame Ecke,
    deckungsgleiches Stueck -- zaehlt nicht. Das ist gewollt: Polygone duerfen
    sich beruehren, und eine Aussparung darf am Rand ansetzen.
    """
    d1 = _kreuz(b1, b2, a1)
    d2 = _kreuz(b1, b2, a2)
    d3 = _kreuz(a1, a2, b1)
    d4 = _kreuz(a1, a2, b2)
    # Massstab der Kreuzprodukte: Laenge mal Laenge. Darunter gilt ein Punkt
    # als auf der Geraden liegend.
    grenze = TOLERANZ * (math.hypot(a2[0] - a1[0], a2[1] - a1[1])
                         + math.hypot(b2[0] - b1[0], b2[1] - b1[1]))
    return ((d1 > grenze and d2 < -grenze) or (d1 < -grenze and d2 > grenze)) and \
           ((d3 > grenze and d4 < -grenze) or (d3 < -grenze and d4 > grenze))


def selbstschnitt(punkte: Sequence[Punkt]) -> Optional[Tuple[int, int]]:
    """Das erste Paar nicht benachbarter Kanten, die sich kreuzen -- oder nichts."""
    n = len(punkte)
    kanten = list(_kanten(punkte))
    for i in range(n):
        for j in range(i + 2, n):
            if i == 0 and j == n - 1:
                continue  # die erste und die letzte Kante teilen den Startpunkt
            if echt_geschnitten(*kanten[i], *kanten[j]):
                return i, j
    return None


def polygon_pruefen(punkte: Sequence[Punkt], name: str) -> None:
    """
    Ob sich aus diesem Polygon rechnen laesst. Wirft :class:`GeometrieFehler`
    mit einem Satz, der sagt, was nicht stimmt.
    """
    if len(punkte) < 3:
        raise GeometrieFehler(f"{name}: ein Polygon braucht mindestens drei Punkte.",
                              (name,))
    for i, (a, b) in enumerate(_kanten(punkte)):
        if math.hypot(b[0] - a[0], b[1] - a[1]) <= TOLERANZ:
            raise GeometrieFehler(
                f"{name}: Punkt {i + 1} und Punkt {(i + 1) % len(punkte) + 1} "
                f"liegen aufeinander.", (name,))
    # Die Kreuzung vor der Flaeche: eine Fliege hat rechnerisch keine Flaeche,
    # weil sich ihre beiden Haelften aufheben -- «kreuzen sich» sagt mehr.
    kreuzung = selbstschnitt(punkte)
    if kreuzung is not None:
        i, j = kreuzung
        raise GeometrieFehler(
            f"{name}: die Kanten {i + 1} und {j + 1} kreuzen sich. Ein Polygon "
            f"darf sich nicht selbst überschneiden.", (name,))
    if abs(flaeche(punkte)) <= TOLERANZ:
        raise GeometrieFehler(f"{name}: das Polygon hat keine Fläche.", (name,))


def schnitt_mit_gerade(
    punkte: Sequence[Punkt], normale: Tuple[float, float], v: float,
) -> List[Tuple[float, float]]:
    """
    Wo die Gerade ``n·p = v`` im Polygon liegt -- als Abschnitte auf ihr.

    Gemessen wird entlang der Tangente ``t = (-n_z, n_y)``, also ``u = t·p``.
    ``normale`` muss ein Einheitsvektor sein. Zurueck kommen die Paare
    ``(u_von, u_bis)`` in aufsteigender Folge; ihre Laengen ergeben die Breite
    des Polygons auf dieser Hoehe.

    Gedacht fuer Geraden, die keine Ecke treffen -- die Fasern legen ihre
    Mitten zwischen die Ecken. Trifft eine trotzdem eine Ecke, zaehlt die
    halb offene Regel aus :func:`lage` sie genau einmal.
    """
    n_y, n_z = normale
    t_y, t_z = -n_z, n_y
    schnitte: List[float] = []
    for a, b in _kanten(punkte):
        va = n_y * a[0] + n_z * a[1]
        vb = n_y * b[0] + n_z * b[1]
        if (va > v) != (vb > v):
            anteil = (v - va) / (vb - va)
            y = a[0] + anteil * (b[0] - a[0])
            z = a[1] + anteil * (b[1] - a[1])
            schnitte.append(t_y * y + t_z * z)
    schnitte.sort()
    return [(schnitte[i], schnitte[i + 1]) for i in range(0, len(schnitte) - 1, 2)]


# ===========================================================================
# Wie Polygone zueinander liegen
# ===========================================================================


class Beziehung(str, Enum):
    """Wie zwei Polygone zueinander liegen."""

    ERSTES_IM_ZWEITEN = "erstes_im_zweiten"
    ZWEITES_IM_ERSTEN = "zweites_im_ersten"
    GETRENNT = "getrennt"
    UEBERLAPPEND = "ueberlappend"


def _ganz_in(p: Sequence[Punkt], q: Sequence[Punkt]) -> Optional[bool]:
    """
    Ob ``p`` ganz in ``q`` liegt: ``True``, ganz draussen: ``False``, weder
    noch: ``None``.

    Gezaehlt werden die Ecken von ``p`` und die Mitten seiner Kanten. Eine
    Ecke auf dem Rand von ``q`` sagt nichts; liegt alles auf dem Rand,
    entscheiden die Kantenmitten -- so wird eine Aussparung, die am Rand
    ansetzt, als innen erkannt.
    """
    innen = aussen = False
    proben = list(p) + [((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
                        for a, b in _kanten(p)]
    for punkt in proben:
        wo = lage(punkt, q)
        innen = innen or wo > 0
        aussen = aussen or wo < 0
    if innen and aussen:
        return None
    if innen:
        return True
    if aussen:
        return False
    return None  # alles auf dem Rand: deckungsgleich


def beziehung(p: Sequence[Punkt], q: Sequence[Punkt]) -> Beziehung:
    """
    Wie ``p`` zu ``q`` liegt.

    Zuerst echte Kreuzungen von Kanten -- die bedeuten immer Ueberlappung.
    Ohne sie entscheiden die Proben aus :func:`_ganz_in` in beide Richtungen.
    Deckungsgleiche Polygone ueberlappen.
    """
    for a1, a2 in _kanten(p):
        for b1, b2 in _kanten(q):
            if echt_geschnitten(a1, a2, b1, b2):
                return Beziehung.UEBERLAPPEND
    p_in_q = _ganz_in(p, q)
    q_in_p = _ganz_in(q, p)
    if p_in_q is True and q_in_p is not True:
        return Beziehung.ERSTES_IM_ZWEITEN
    if q_in_p is True and p_in_q is not True:
        return Beziehung.ZWEITES_IM_ERSTEN
    if p_in_q is False and q_in_p is False:
        return Beziehung.GETRENNT
    return Beziehung.UEBERLAPPEND


def verschachteln(
    polygone: Sequence[Sequence[Punkt]], namen: Sequence[str],
) -> Tuple[Optional[int], ...]:
    """
    Je Polygon das, in dem es liegt -- das kleinste, das es ganz enthaelt.

    Wirft :class:`GeometrieFehler`, wenn zwei Polygone teilweise ueberlappen.
    """
    n = len(polygone)
    flaechen = [abs(flaeche(p)) for p in polygone]
    enthaelt = [[False] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            b = beziehung(polygone[i], polygone[j])
            if b is Beziehung.UEBERLAPPEND:
                raise GeometrieFehler(
                    f"{namen[i]} und {namen[j]} überlappen sich teilweise. "
                    f"Polygone dürfen sich berühren oder ganz ineinander "
                    f"liegen, aber nicht teilweise überlappen.", (namen[i], namen[j]))
            if b is Beziehung.ERSTES_IM_ZWEITEN:
                enthaelt[j][i] = True
            elif b is Beziehung.ZWEITES_IM_ERSTEN:
                enthaelt[i][j] = True
    eltern: List[Optional[int]] = []
    for i in range(n):
        huellen = [j for j in range(n) if enthaelt[j][i]]
        eltern.append(min(huellen, key=lambda j: flaechen[j]) if huellen else None)
    return tuple(eltern)


def innerstes(p: Punkt, polygone: Sequence[Sequence[Punkt]]) -> Optional[int]:
    """
    Das kleinste Polygon, in dessen Innern ``p`` liegt -- oder nichts.

    Bei verschachtelten Polygonen ist das das innerste, also das, dessen
    Material an dieser Stelle gilt.
    """
    treffer = [i for i, q in enumerate(polygone) if lage(p, q) > 0]
    if not treffer:
        return None
    return min(treffer, key=lambda i: abs(flaeche(polygone[i])))


def stab_liegt_in(
    p: Punkt, radius: float, polygone: Sequence[Sequence[Punkt]],
    traegt: Sequence[bool],
) -> bool:
    """
    Ob ein runder Stab ganz in einem tragenden Polygon liegt.

    ``traegt`` sagt je Polygon, ob sein Material Bewehrung aufnimmt -- beim
    Stahlbeton: ob es Beton ist. Die Mitte muss im innersten Polygon liegen
    und dieses muss tragen; dazu darf der Stab keinen Rand schneiden, weder
    den aeusseren noch den einer Aussparung.
    """
    innen = innerstes(p, polygone)
    if innen is None or not traegt[innen]:
        return False
    return all(abstand_zum_rand(p, q) >= radius - TOLERANZ for q in polygone)


#: Abstand der Proben entlang einer Wandlinie, in der Einheit der Punkte.
WANDPROBE = 5.0


def strecke_liegt_in(
    a: Punkt, b: Punkt, polygone: Sequence[Sequence[Punkt]], traegt: Sequence[bool],
) -> bool:
    """
    Ob eine Strecke -- eine Schubwand -- ganz in tragenden Polygonen verlaeuft.

    Geprueft wird an Proben alle :data:`WANDPROBE` entlang der Strecke, ohne
    die beiden Enden: eine Wand darf bis an den Rand reichen. Eine Aussparung,
    schmaler als der Probenabstand, faellt dabei durch -- fuenf Millimeter
    liegen unter allem, was als Aussparung gezeichnet wird.
    """
    laenge = math.hypot(b[0] - a[0], b[1] - a[1])
    proben = max(2, int(math.ceil(laenge / WANDPROBE)))
    for k in range(proben):
        t = (k + 0.5) / proben
        innen = innerstes((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])), polygone)
        if innen is None or not traegt[innen]:
            return False
    return True


# ===========================================================================
# Stablinien
# ===========================================================================


class Linienart(str, Enum):
    """Wie die Menge einer Stablinie angegeben ist."""

    FLAECHE = "flaeche"
    """Eine Stahlflaeche, gleichmaessig ueber die Linie verteilt."""

    ANZAHL = "anzahl"
    """So viele Staebe, gleich weit voneinander."""

    TEILUNG = "teilung"
    """Ein Wunschabstand -- gerundet auf den naechsten, der aufgeht."""


@dataclass(frozen=True)
class Stablinie:
    """Eine aufgeloeste Stablinie: wo ihre Staebe liegen."""

    von: Punkt
    bis: Punkt
    laenge: float
    felder: int
    """In wie viele gleiche Felder die Linie geteilt ist; null bei einer Flaeche."""

    teilung: Optional[float]
    """Der tatsaechliche Abstand der Staebe; ``None`` bei einer Flaeche."""

    punkte: Tuple[Punkt, ...]
    """Die Stabmitten; leer bei einer Flaeche."""


def _halb_auf(x: float) -> int:
    """Kaufmaennisch gerundet: 2.5 gibt 3. ``round`` gaebe 2 (zur geraden Zahl)."""
    return int(math.floor(x + 0.5))


def stablinie(
    von: Punkt, bis: Punkt, art: Linienart, wert: float, *,
    starteisen: bool = True, endeisen: bool = True,
) -> Stablinie:
    """
    Wo die Staebe einer Linie liegen.

    Die Linie wird in ``m`` gleiche Felder geteilt, die Staebe sitzen auf den
    Teilpunkten. ``starteisen`` und ``endeisen`` sagen, ob die beiden Enden
    besetzt sind::

        Anzahl n:   m = n - 1 + (0 oder 1 je freies Ende)
        Teilung s:  m = runde(L / s), kaufmaennisch; tatsaechlich L / m

    Bei 1000 mm und s = 150 sind das sieben Felder zu 142.9 mm, mit beiden
    Enden acht Staebe. Bei einer Flaeche gibt es keine Einzelstaebe.
    """
    laenge = math.hypot(bis[0] - von[0], bis[1] - von[1])
    if laenge <= TOLERANZ:
        raise GeometrieFehler("Die Stablinie hat keine Länge.")
    if wert <= 0:
        raise GeometrieFehler({
            Linienart.FLAECHE: "Die Stahlfläche der Linie muss grösser als null sein.",
            Linienart.ANZAHL: "Die Stabzahl der Linie muss grösser als null sein.",
            Linienart.TEILUNG: "Die Teilung der Linie muss grösser als null sein.",
        }[art])
    if art is Linienart.FLAECHE:
        return Stablinie(von=von, bis=bis, laenge=laenge, felder=0,
                         teilung=None, punkte=())

    frei = (0 if starteisen else 1) + (0 if endeisen else 1)
    if art is Linienart.ANZAHL:
        if wert != int(wert):
            raise GeometrieFehler("Die Stabzahl der Linie muss ganz sein.")
        felder = int(wert) - 1 + frei
        if felder < 1:
            raise GeometrieFehler(
                "Ein einzelner Stab kann nicht zugleich am Anfang und am Ende "
                "liegen. Starteisen oder Endeisen ausschalten.")
    else:
        felder = max(1, _halb_auf(laenge / wert))

    erster = 0 if starteisen else 1
    letzter = felder if endeisen else felder - 1
    if letzter < erster:
        raise GeometrieFehler(
            "Auf der Linie bleibt kein Stab: ein Feld, beide Enden frei.")
    punkte = tuple(
        (von[0] + (bis[0] - von[0]) * k / felder,
         von[1] + (bis[1] - von[1]) * k / felder)
        for k in range(erster, letzter + 1))
    return Stablinie(von=von, bis=bis, laenge=laenge, felder=felder,
                     teilung=laenge / felder, punkte=punkte)
