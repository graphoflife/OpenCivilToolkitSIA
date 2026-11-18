"""
opencivil/projekt/aufbau/balkensystem3d.py -- ein 3D-Balkensystem wird Rechnung.

VERANTWORTUNG:
Wie ein 2D-Balkensystem (:mod:`~opencivil.projekt.aufbau.balkensystem`),
im Raum: aus einem
:class:`~opencivil.projekt.balkensystem3d.Balkensystem3dEintrag` das
Stabwerk in SI (:func:`modell_von`) und daraus die Rechnung mit
aufgeloesten Materialien und Querschnitten (:func:`bauen`). Was beide gleich
pruefen und aufloesen, kommt von dort -- auch ein Querschnitt aus einer
Platte oder Querschnittsanalyse, deren I_T sie dann rechnet, und das
Material «gemäss Querschnitt»; hier
steht nur, was der Raum anders macht: der Drehwinkel in rad, eine Last an
einem Knoten als Vektor, ein Profil, das sich um beide Achsen biegt.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from opencivil.projekt.aufbau.balkensystem import (
    Modell, Uebersetzung, stabquerschnitt_von, stabwerk_bauen,
)
from opencivil.projekt.aufbau.kern import Aufbau, Bauteil
from opencivil.projekt.balkensystem3d import Balkensystem3dEintrag, RaumknotenlastEintrag
from opencivil.projekt.staebe import MATERIAL_DES_QUERSCHNITTS
from opencivil.stabwerk3d.modell import Knoten, Knotenlast, Lager, Stab, Stablast, System
from opencivil.stabwerk3d.raum import ACHSEN, mal
from opencivil.stabwerk3d.rechnung import Balkensystem3d

if TYPE_CHECKING:
    from opencivil.projekt.aufbau import Bauteilart


def modell_von(eintrag: Balkensystem3dEintrag) -> Modell:
    """Das Stabwerk zum Rechnen, in SI (:mod:`opencivil.stabwerk3d.modell`)."""
    u = Uebersetzung(eintrag, weitere_stoffe=(MATERIAL_DES_QUERSCHNITTS,))
    staebe = [Stab(**u.stab(l), drehung=math.radians(l.drehung)) for l in eintrag.linien]
    lager = u.lager(Lager)
    u.stablasten(Stablast)
    u.knotenlasten(_knotenlast)
    return u.modell(System, Knoten, staebe, lager)


def _knotenlast(p: RaumknotenlastEintrag, wert: float) -> Knotenlast:
    """Eine Kraft in ihre Richtung oder ein Moment um sie -- in den Achsen des Systems."""
    vektor = mal(wert, p.richtung.vektor(ACHSEN))
    return Knotenlast(p.knoten, M=vektor) if p.art == "moment" else Knotenlast(p.knoten, F=vektor)


def bauen(art: "Bauteilart", eintrag: Balkensystem3dEintrag, aufbau: Aufbau) -> Bauteil:
    """Ein 3D-Balkensystem -- seine Querschnitte aufgeloest wie in der Ebene."""
    return stabwerk_bauen(Balkensystem3d, art, eintrag, aufbau, modell_von(eintrag),
                          [stabquerschnitt_von(q, aufbau, eintrag.wo)
                           for q in eintrag.querschnitte])
