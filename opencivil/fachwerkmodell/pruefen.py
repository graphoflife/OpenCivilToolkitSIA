"""
opencivil/fachwerkmodell/pruefen.py -- was einem Fachwerkmodell fehlt oder an ihm nicht stimmt.

VERANTWORTUNG:
Die Meldungen eines Modells, bevor ein Fachwerk gesucht wird, in dieser
Folge:

- ein Umriss, aus dem sich nicht rechnen lässt -- zu wenig Ecken, sich
  selbst kreuzend, ohne Fläche: rot;
- noch keine Scheibe: grau;
- ein Loch neben jeder Scheibe: ein Hinweis, es nimmt nichts weg;
- ein Lager oder eine Last neben der Scheibe oder in einem Loch: rot;
- noch kein Lager, oder Lager, die die Scheibe noch nicht halten -- sie
  könnte sich verschieben oder drehen: grau, mit der Bewegung, die bleibt;
- keine Last: grau, «Keine Last → kein Fachwerk.».

Was nur fehlt, steht grau und hält die Rechnung an; was falsch ist, steht
rot (Benutzer, 2026-11-19). Ein Fachwerk braucht beides nicht: es
genügt, dass die Lager die Scheibe als starren Körper halten.

DIE LAGER HALTEN DIE SCHEIBE, WENN:
keine Bewegung der starren Scheibe -- verschoben um ``(u, v)``, gedreht um
``θ`` -- jedes Lager in seiner Richtung stehen lässt. Ein Lager bei
``(x, y)``, fest in x, verlangt ``u − θ·y = 0``, fest in y ``v + θ·x = 0``;
drei unabhängige solche Gleichungen halten sie. Sind es weniger, sagt die
Bewegung, die bleibt, was fehlt: eine Verschiebung oder eine Drehung um
einen Punkt -- etwa um das einzige Lager.
"""

from __future__ import annotations

import math
from typing import List, Optional, Sequence, Tuple

from opencivil.decke import geometrie as geo
from opencivil.decke.herleitung import als_ort
from opencivil.fachwerkmodell.modell import Lager, Modell, Umriss
from opencivil.querschnitt.geometrie import GeometrieFehler, polygon_pruefen
from opencivil.stabwerk.system import Meldung

#: Unter dieser Zahl gilt ein Rest der Gleichungen der Lager als null -- in
#: Koordinaten, die auf die Grösse der Lagerung bezogen sind.
SCHRANKE = 1e-9

#: Ab dieser Kraft in N zählt eine Last -- darunter ist sie null.
KEINE_KRAFT = 1e-9


def pruefen(modell: Modell) -> List[Meldung]:
    """Siehe Dateikopf -- leer, wenn sich ein Fachwerk suchen lässt."""
    meldungen = [m for u in (*modell.scheiben, *modell.loecher) if (m := _umriss(u)) is not None]
    if not modell.scheiben:
        meldungen.append(Meldung("Noch keine Scheibe – ihren Umriss zeichnen.",
                                 fehler=False, unfertig=True))
    elif not meldungen:
        meldungen += [Meldung(f"Das Loch {l.name} liegt neben jeder Scheibe – es nimmt nichts weg.",
                              (l.name,), fehler=False)
                      for l in modell.loecher if not any(_ueberlappen(l, s) for s in modell.scheiben)]
        for teil, was in [*((l, "Das Lager") for l in modell.lager),
                          *((f, "Die Last") for f in modell.lasten)]:
            grund = _ohne_material(modell, teil.ort)
            if grund:
                meldungen.append(Meldung(f"{was} {teil.name} liegt {grund}.", (teil.name,)))
    if not modell.lager:
        meldungen.append(Meldung("Noch kein Lager – die Scheibe an einem Punkt halten.",
                                 fehler=False, unfertig=True))
    else:
        bewegung = beweglich(modell.lager)
        if bewegung:
            meldungen.append(Meldung(f"Die Lager halten die Scheibe noch nicht: sie kann sich "
                                     f"{bewegung}.", tuple(l.name for l in modell.lager),
                                     fehler=False, unfertig=True))
    if not any(math.hypot(f.F_x, f.F_y) > KEINE_KRAFT for f in modell.lasten):
        meldungen.append(Meldung("Keine Last → kein Fachwerk.", fehler=False, unfertig=True))
    return meldungen


def _umriss(u: Umriss) -> Optional[Meldung]:
    """Was an einem Umriss nicht stimmt -- rot, mit seinem Namen."""
    try:
        polygon_pruefen(u.ecken, u.name)
    except GeometrieFehler as fehler:
        return Meldung(str(fehler), (u.name,))
    return None


def _ohne_material(modell: Modell, ort: geo.Punkt) -> str:
    """Warum bei ``ort`` kein Material ist, als Satzteil -- leer, wenn welches da ist."""
    if not modell.in_scheibe(ort):
        return f"bei {als_ort(ort)} neben der Scheibe"
    loch = modell.loch_bei(ort)
    return f"im Loch {loch.name}" if loch is not None else ""


def _ueberlappen(a: Umriss, b: Umriss) -> bool:
    """
    Ob zwei Umrisse Fläche gemeinsam haben -- auch wenn einer ganz im
    anderen liegt; berühren sie sich nur am Rand, nicht. Je zwei ihrer
    konvexen Stücke (:func:`~opencivil.decke.geometrie.dreiecke`)
    geschnitten: ``a`` und ``b`` sind geprüft, sie kreuzen sich nicht selbst.
    """
    return any(geo.schnitt(s, t) for s in geo.dreiecke(a.ecken) for t in geo.dreiecke(b.ecken))


def beweglich(lager: Sequence[Lager]) -> str:
    """
    Wie sich die starre Scheibe trotz ``lager`` noch bewegen kann, als
    Satzteil nach «sie kann sich» -- leer, wenn die Lager sie halten.
    """
    zeilen, mitte, gross = _gleichungen(lager)
    rang, frei = _rang(zeilen)
    if rang == 3:
        return ""
    if rang < 2 or frei is None:
        return "verschieben und drehen"
    u, v, theta = frei
    if abs(theta) <= SCHRANKE * max(abs(u), abs(v)):
        if abs(v) <= SCHRANKE * abs(u):
            return "in x verschieben"
        if abs(u) <= SCHRANKE * abs(v):
            return "in y verschieben"
        return f"schräg verschieben, in Richtung {als_ort((u / math.hypot(u, v), v / math.hypot(u, v)))}"
    pol = (mitte[0] - v / theta * gross, mitte[1] + u / theta * gross)
    an = next((l.name for l in lager if math.dist(l.ort, pol) <= geo.TOLERANZ * max(gross, 1.0)), None)
    return f"um das Lager {an} drehen" if an else f"um den Punkt {als_ort(pol)} drehen"


def _gleichungen(lager: Sequence[Lager]) -> Tuple[List[List[float]], geo.Punkt, float]:
    """
    Je Richtung, in der ein Lager hält, die Zeile ``(u, v, θ)`` seiner
    Gleichung -- in Koordinaten um die Mitte der Lager, geteilt durch ihre
    Ausdehnung, damit die Schranke nicht von der Grösse abhängt. Dazu Mitte
    und Ausdehnung.
    """
    xs, ys = [l.ort[0] for l in lager], [l.ort[1] for l in lager]
    mitte = (0.5 * (min(xs) + max(xs)), 0.5 * (min(ys) + max(ys)))
    gross = max(max(xs) - min(xs), max(ys) - min(ys), 1.0)
    zeilen = []
    for l in lager:
        x, y = (l.ort[0] - mitte[0]) / gross, (l.ort[1] - mitte[1]) / gross
        if l.halt.x:
            zeilen.append([1.0, 0.0, -y])
        if l.halt.y:
            zeilen.append([0.0, 1.0, x])
    return zeilen, mitte, gross


def _rang(zeilen: List[List[float]]) -> Tuple[int, Optional[Tuple[float, float, float]]]:
    """
    Der Rang der Zeilen -- und bei Rang 2 die Bewegung, die sie stehen
    lassen: das Kreuzprodukt zweier unabhängiger Zeilen.
    """
    unabhaengig: List[List[float]] = []
    rest = [list(z) for z in zeilen]
    for z in rest:
        for basis in unabhaengig:
            k = max(range(3), key=lambda i: abs(basis[i]))
            f = z[k] / basis[k]
            z[:] = [a - f * b for a, b in zip(z, basis)]
        if max(abs(a) for a in z) > SCHRANKE:
            unabhaengig.append(z)
    if len(unabhaengig) != 2:
        return min(len(unabhaengig), 3), None
    a, b = unabhaengig
    return 2, (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
