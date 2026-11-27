"""
opencivil/decke/fem/auswertung.py -- die FEM an einer Stelle, längs eines Schnitts, im Träger.

VERANTWORTUNG:
Was Bilder und Bericht von einem Fall der FEM lesen, in denselben Formen
wie bei der Streifenmethode (:mod:`~opencivil.decke.schnitt`): die Werte an
einer Stelle, den Verlauf längs eines Schnitts, Moment und Querkraft eines
Trägers und die Stellen, an denen die grössten Werte gesucht werden. Neu
gerechnet wird hier nichts: über ein Dreieck ist jede Grösse linear
zwischen den geglätteten Werten an seinen Ecken
(:mod:`~opencivil.decke.fem.rechnung`), ``v_0`` der Betrag aus ``v_x`` und
``v_y`` dort.

DAS BILD DER PLATTE:
Jedes Dreieck des Netzes ist eine Zelle (:func:`bild`). In ihrem
Schwerpunkt stehen die Werte dort, und ihr Gefälle ist das der Ebene durch
die Werte an ihren Ecken -- dasselbe, was die Streifenmethode für eine
Zelle ausgleicht (:func:`~opencivil.decke.feld.gefaelle`): auf einem
Dreieck trifft die Ebene die Ecken genau, für ``v_0`` beinahe.

LÄNGS EINES SCHNITTS:
In jedem Dreieck, durch das er läuft, sieht der Verlauf an Eintritt und
Austritt hin, knapp innen (:data:`~opencivil.decke.feld.INNEN`): so
springt er, wo die Werte über eine Kante springen, und dazwischen ist er
genau -- ``v_0`` hat dort, wo er gekrümmt ist, sein Grösstes an einem Ende.

DER TRÄGER:
Sein Moment und seine Querkraft über die ganze Breite ``b``: was der Balken
trägt und was die Platte über die Breite trägt, ``b`` mal das Mittel von
``m_t`` und ``v_t`` quer zu seiner Achse, in seiner Richtung ``t``
(Entscheid 10 des Plans vom 2026-11-27). So hat auch ein Träger ohne Höhe
seine Schnittkräfte: dann trägt nur die Platte. Quer wird an :data:`QUER`
gleich verteilten Stellen gemittelt, längs an beiden Enden jedes Stücks
und in seiner Mitte.
"""

from __future__ import annotations

import math
from typing import List, Sequence, Tuple, Union

from opencivil.decke import geometrie as geo
from opencivil.decke.feld import INNEN, Bild, Schnittkraefte
from opencivil.decke.fem.belastung import schwerpunktkoordinaten
from opencivil.decke.fem.rechnung import GROESSEN, Femergebnis, Femfall, Femwerte
from opencivil.decke.geometrie import Punkt
from opencivil.decke.modell import Traeger
from opencivil.decke.schnitt import Balkenkraefte, Verlauf, in_platten, lagerstellen

#: An so vielen Stellen quer zum Träger wird die Platte gemittelt -- gerade, damit keine auf der Achse liegt.
QUER = 8

#: Die Schwerpunktkoordinaten des Schwerpunkts.
MITTE = (1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0)


def gemischt(ecken: Sequence[Femwerte], anteile: Sequence[float]) -> Femwerte:
    """Die Werte an einer Stelle eines Dreiecks aus denen an seinen Ecken, mit ihren Schwerpunktkoordinaten."""
    return Femwerte(*(sum(l * getattr(w, n) for l, w in zip(anteile, ecken))
                      for n in ("mx", "my", "mxy", "vx", "vy", "w")))


def an_stelle(ergebnis: Femergebnis, fall: Femfall, p: Punkt) -> Femwerte:
    """Die Werte an der Stelle ``p`` -- neben den Platten null."""
    e, anteile = ergebnis.raster.bei(p)
    return gemischt(fall.ecken[e], anteile) if e >= 0 else Femwerte()


def proben(ergebnis: Femergebnis, fall: Femfall) -> List[Tuple[Punkt, Femwerte]]:
    """
    Wo Bild und Bericht die grössten Werte suchen: an jedem Knoten je Sektor
    -- über ein Dreieck linear, liegen sie dort; ``v_0`` auch, denn der
    Betrag ist am grössten an einer Ecke.
    """
    knoten = ergebnis.netz.knoten
    return [(knoten[k], w) for k, w in zip(ergebnis.glaettung.knoten, fall.sektoren)]


def bild(ergebnis: Femergebnis, fall: Femfall) -> Bild:
    """Je Dreieck des Netzes eine Zelle, mit den Werten in ihrem Schwerpunkt und ihrem Gefälle -- gesucht wird an :func:`proben`."""
    netz = ergebnis.netz
    zellen = [[netz.knoten[k] for k in d] for d in netz.dreiecke]
    mitten = [(geo.schwerpunkt(z), gemischt(ecken, MITTE)) for z, ecken in zip(zellen, fall.ecken)]
    gefaelle = [{g: d.gefaelle([w.groesse(g) for w in ecken]) for g in GROESSEN}
                for d, ecken in zip(ergebnis.system.dreiecke, fall.ecken)]
    return Bild(zellen, mitten, gefaelle, proben(ergebnis, fall))


def verlauf(ergebnis: Femergebnis, fall: Femfall, a: Punkt, b: Punkt) -> Verlauf:
    """Der Verlauf längs des Schnitts von ``a`` nach ``b`` -- ohne Länge leer."""
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    if L <= geo.TOLERANZ:
        return Verlauf(0.0, [], [], [], [])
    e = ((b[0] - a[0]) / L, (b[1] - a[1]) / L)
    netz = ergebnis.netz
    proben_: List[Tuple[float, Union[Schnittkraefte, Balkenkraefte]]] = []
    for d in ergebnis.raster.nahe([a, b]):
        teil = geo.strecke_in_konvex(a, b, [netz.knoten[k] for k in netz.dreiecke[d]])
        if teil is None or (teil[1] - teil[0]) * L <= 2.0 * INNEN:
            continue
        for u in (teil[0] * L + INNEN, teil[1] * L - INNEN):
            p = (a[0] + u * e[0], a[1] + u * e[1])
            proben_.append((u, gemischt(fall.ecken[d], schwerpunktkoordinaten(netz, d, p))))
    proben_.sort(key=lambda x: x[0])
    traeger = [(u0 * L, u1 * L, u.name) for u in ergebnis.decke.traeger
               for u0, u1 in geo.strecke_im_vieleck(a, b, geo.rechteck(u.a, u.b, u.breite))]
    return Verlauf(L, in_platten(ergebnis.decke, a, b, L), proben_,
                   lagerstellen(ergebnis.decke, a, b, e, L), traeger)


def traeger(ergebnis: Femergebnis, fall: Femfall, u: Traeger) -> Verlauf:
    """
    Moment und Querkraft des Trägers ``u`` über seine ganze Breite, längs
    seiner Achse ab ``a`` -- aus seinem Balken und der Platte daneben. Seine
    Lager sind die Linienlager, die er kreuzt, und die Stützen auf ihm.
    """
    L = math.hypot(u.b[0] - u.a[0], u.b[1] - u.a[1])
    t = ((u.b[0] - u.a[0]) / L, (u.b[1] - u.a[1]) / L)
    lager = lagerstellen(ergebnis.decke, u.a, u.b, t, L)
    linie = ergebnis.netz.linie("traeger", u.name)
    if linie is None or not linie.stuecke:
        return Verlauf(L, [], [], lager, [])
    lage = dict(zip(linie.knoten, linie.u))
    balken = fall.traeger.get(u.name, [])
    n = (-t[1], t[0])
    quer = [u.breite * ((j + 0.5) / QUER - 0.5) for j in range(QUER)]
    stuecke: List[Tuple[float, float]] = []
    proben_: List[Tuple[float, Union[Schnittkraefte, Balkenkraefte]]] = []
    for p, q in linie.stuecke:
        s0, s1 = lage[p], lage[q]
        stuecke.append((s0, s1))
        stueck = next((x for x in balken if x.u_p <= 0.5 * (s0 + s1) <= x.u_q), None)
        for s in (s0 + INNEN, 0.5 * (s0 + s1), s1 - INNEN):
            M = V = 0.0
            for tau in quer:
                w = an_stelle(ergebnis, fall, (u.a[0] + s * t[0] + tau * n[0], u.a[1] + s * t[1] + tau * n[1]))
                M += w.mx * t[0] * t[0] + w.my * t[1] * t[1] + 2.0 * w.mxy * t[0] * t[1]
                V += w.vx * t[0] + w.vy * t[1]
            M *= u.breite / QUER
            V *= u.breite / QUER
            if stueck is not None:
                M += stueck.M_p + (stueck.M_q - stueck.M_p) * (s - stueck.u_p) / (stueck.u_q - stueck.u_p)
                V += stueck.V
            proben_.append((s, Balkenkraefte(M, V)))
    return Verlauf(L, geo.vereinigt(stuecke), proben_, lager, [])
