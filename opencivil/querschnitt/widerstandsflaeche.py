"""
opencivil/querschnitt/widerstandsflaeche.py -- die Flaeche aller Bruchzustaende, geschnitten.

VERANTWORTUNG:
Alle Bruchzustaende eines Querschnitts zusammen bilden im Raum
(N, M_y, M_z) eine geschlossene Flaeche; jeder Faecher
(:meth:`~opencivil.querschnitt.interaktion.Querschnitt.faecher`) ist eine
Linie darauf. Das Interaktionsdiagramm der Querschnittsanalyse ist ein
Schnitt durch sie, bei festem N, M_y oder M_z (:func:`schnitt`). Nur das
Bild liest ihn, kein Nachweis rechnet damit. Bis 2026-11-20 stand er in
:mod:`opencivil.querschnitt.interaktion`.

EINHEITEN:
SI-Basis: Newton und Newtonmeter.
"""

from __future__ import annotations

import math
from typing import Dict, List, Sequence, Tuple
from weakref import WeakKeyDictionary

from opencivil.querschnitt.interaktion import Bruchpunkt, Punkt, Querschnitt

#: Stuetzstellen je Abschnitt fuer die Flaeche der Widerstaende -- weniger als
#: fuer eine Linie; die Luecken fuellt das Halbieren.
FLAECHE_SCHRITTE = 8

#: Neigungen, mit denen die Flaeche der Widerstaende abgetastet wird -- alle 5°.
FLAECHE_NEIGUNGEN = 72

#: Stufen in N, auf denen die Flaeche bei festem Moment geschnitten wird. Zu den
#: Enden hin dichter, wo sie sich zum reinen Zug und Druck schliesst.
SCHNITT_STUFEN = 120

#: Wonach geschnitten werden kann.
GROESSEN = ("N", "M_y", "M_z")

#: Je Stufe in N der Umriss ``(M_y, M_z)`` ueber alle Neigungen.
Stufen = List[Tuple[float, List[Punkt]]]

#: Die Stufen je Querschnitt und Zahl der Neigungen, solange es den
#: Querschnitt gibt: ein anderer Schnitt durch dieselbe Flaeche liest
#: dieselben Faecher. Bis 2026-11-20 trug der Querschnitt sie selbst.
_STUFEN: WeakKeyDictionary[Querschnitt, Dict[int, Stufen]] = WeakKeyDictionary()


def schnitt(q: Querschnitt, fest: str, wert: float,
            neigungen: int = FLAECHE_NEIGUNGEN) -> List[Tuple[float, float, float]]:
    """
    Die Flaeche aller Bruchzustaende im Raum (N, M_y, M_z), geschnitten bei
    einem festen Wert von N, M_y oder M_z: ein geschlossener Zug von Punkten
    ``(N, M_y, M_z)``, auf dem die feste Groesse diesen Wert hat. Leer, wo
    die Ebene die Flaeche nicht trifft.

    Bei festem N je Neigung der Punkt des Faechers mit diesem N -- dieselbe
    Suche wie im Nachweis. Bei festem Moment die Faecher aller Neigungen,
    je auf Stufen in N gelesen; auf jeder Stufe schneidet die Gerade des
    festen Moments den Umriss in zwei Punkten. Zwischen den Stuetzstellen
    eines Faechers wird dabei linear gelesen: genau genug fuer ein Bild,
    nachgewiesen wird damit nichts.
    """
    if fest == "N":
        punkte = [q.bei_normalkraft(2.0 * math.pi * k / neigungen, wert)
                  for k in range(neigungen)]
        return [(p.N, p.M_y, p.M_z) for p in punkte if p is not None]
    if fest not in GROESSEN:
        raise ValueError(f"Geschnitten wird bei N, M_y oder M_z, nicht bei '{fest}'.")
    achse = 0 if fest == "M_y" else 1
    rechts: List[Tuple[float, float]] = []
    links: List[Tuple[float, float]] = []
    for N, umriss in _flaechenstufen(q, neigungen):
        andere = _schnittstellen(umriss, achse, wert)
        if andere:
            rechts.append((N, max(andere)))
            links.append((N, min(andere)))
    zug = rechts + list(reversed(links))
    if achse == 0:
        return [(N, wert, m) for N, m in zug]
    return [(N, m, wert) for N, m in zug]


def _flaechenstufen(q: Querschnitt, neigungen: int) -> Stufen:
    """
    Je Stufe in N der Umriss ``(M_y, M_z)`` ueber alle Neigungen -- aus den
    Faechern, einmal je Querschnitt. Die Stufen liegen wie die Knoten von
    Tschebyschow zwischen reinem Zug und reinem Druck, ohne die Enden: dort
    zieht sich der Umriss auf einen Punkt zusammen.
    """
    je_zahl = _STUFEN.setdefault(q, {})
    if neigungen not in je_zahl:
        zug, druck = q.normalkraft_grenzen()
        mitte, halb = (zug + druck) / 2.0, (zug - druck) / 2.0
        faecher = [q.faecher(2.0 * math.pi * k / neigungen, FLAECHE_SCHRITTE)
                   for k in range(neigungen)]
        stufen = []
        for j in range(SCHNITT_STUFEN):
            N = mitte + halb * math.cos(math.pi * (j + 0.5) / SCHNITT_STUFEN)
            stufen.append((N, [_bei_n_gelesen(f, N) for f in faecher]))
        je_zahl[neigungen] = stufen
    return je_zahl[neigungen]


def _bei_n_gelesen(faecher: Sequence[Bruchpunkt], N: float) -> Punkt:
    """
    ``(M_y, M_z)`` auf einem Faecher bei diesem N, linear zwischen den beiden
    Stuetzstellen, zwischen denen N liegt. Vom Zug zum Druck nimmt N ab.
    """
    unten, oben = 0, len(faecher) - 1
    if N >= faecher[unten].N:
        return faecher[unten].M_y, faecher[unten].M_z
    if N <= faecher[oben].N:
        return faecher[oben].M_y, faecher[oben].M_z
    while oben - unten > 1:
        mitte = (unten + oben) // 2
        if faecher[mitte].N >= N:
            unten = mitte
        else:
            oben = mitte
    a, b = faecher[unten], faecher[oben]
    t = (a.N - N) / (a.N - b.N) if a.N != b.N else 0.0
    return a.M_y + t * (b.M_y - a.M_y), a.M_z + t * (b.M_z - a.M_z)


def _schnittstellen(umriss: Sequence[Punkt], achse: int, wert: float) -> List[float]:
    """
    Wo die Gerade ``Punkt[achse] = wert`` den geschlossenen Umriss kreuzt --
    die andere Koordinate jeder Stelle.
    """
    andere = 1 - achse
    stellen: List[float] = []
    for i, a in enumerate(umriss):
        b = umriss[(i + 1) % len(umriss)]
        da, db = a[achse] - wert, b[achse] - wert
        if da == 0.0:
            stellen.append(a[andere])
        elif da * db < 0.0:
            stellen.append(a[andere] + da / (da - db) * (b[andere] - a[andere]))
    return stellen
