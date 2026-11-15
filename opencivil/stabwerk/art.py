"""
opencivil/stabwerk/art.py -- eben oder im Raum: was die beiden Balkensysteme unterscheidet.

VERANTWORTUNG:
Der Rechenkern (:mod:`~opencivil.stabwerk.system`) rechnet jedes System im
Raum. Was ein ebenes von einem raeumlichen unterscheidet, steht hier, je
einmal in einer :class:`Art` (:data:`EBENE`, :data:`RAUM`) -- und wie aus
einem ebenen System eines im Raum wird.

DIE EBENE:
Ein ebenes System liegt in der x-z-Ebene und bleibt darin. Ein Ort
verschiebt sich nur in x und z und dreht sich nur um ``-y``, im
Gegenuhrzeigersinn; ein Stab biegt sich nur in dieser Ebene und traegt
keine Torsion. Seine Achse y ist ``-y`` des Systems, z zeigt zur
gestrichelten Faser (:func:`~opencivil.stabwerk3d.stab.achsen_eben`):
``N``, ``V_z`` und ``M_y`` sind damit ``N``, ``V`` und ``M`` von Hand.

AUS DER EBENE IN DEN RAUM:
Ein Knoten ``(x, z)`` liegt bei ``(x, 0, z)``; ``EI`` wird ``EI_y``,
``EI_z`` und ``GI_T`` bleiben null, und ein Linienlager quer haelt in z des
Stabs. Ein Lager haelt die Drehung um y. Eine Kraft bleibt, wohin sie
zeigt -- quer heisst quer in z des Stabs --, ein Moment im
Gegenuhrzeigersinn dreht um ``-y``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Sequence, Tuple

from opencivil.stabwerk import modell as eben
from opencivil.stabwerk.modell import Lastfall
from opencivil.stabwerk3d import stab as st3
from opencivil.stabwerk3d.modell import Knoten, Knotenlast, Lager, Richtung, Stab, Stablast, System
from opencivil.stabwerk3d.raum import ACHSEN, Vektor, skalar

#: Was der Kern je Ort oder Lager abgibt: Verschiebungen, dann Drehungen -- oder Kraefte, dann Momente.
Werte = Tuple[float, ...]

@dataclass(frozen=True)
class Art:
    """Was ein ebenes System von einem im Raum unterscheidet -- siehe Dateikopf."""

    verschiebungen: Tuple[Tuple[str, Vektor], ...]
    """Die Achsen des Systems, entlang derer sich ein Ort verschieben kann, mit Namen -- in der Folge der Ergebnisse."""

    drehungen: Tuple[Tuple[str, Vektor], ...]
    """Die Achsen, um die er sich drehen kann -- in der Ebene eine ohne Namen, ``-y``."""

    raeumlich: bool
    """Ob ein Stab sich auch in seiner x-y-Ebene biegt und Torsion traegt."""

    steifigkeiten: Tuple[str, ...]
    """Die Steifigkeiten, die ein tragender Stab braucht -- Felder seines Modells."""

    ohne_steifigkeit: str
    """Was die Meldung sagt, wenn eine davon nicht groesser als null ist."""

    gelenk: str
    """Wie die Drehung eines Stabendes am Gelenk heisst -- mit ``{stab}``, ``{ende}`` und ``{achse}``."""

    achsen: Callable[[Any, Any, float], Tuple[float, Tuple[Vektor, Vektor, Vektor]]]
    """Laenge und Achsen eines Stabs von ``a`` nach ``b`` mit seinem Drehwinkel."""

    im_raum: Callable[[Any], System]
    """Ein System dieser Art als eines im Raum."""

    def werte(self, kraft: Sequence[float], moment: Sequence[float]) -> Werte:
        """Eine Verschiebung und eine Drehung -- oder Kraft und Moment -- in den Achsen der Art."""
        return (tuple(skalar(kraft, a) for _, a in self.verschiebungen)
                + tuple(skalar(moment, a) for _, a in self.drehungen))


#: Je Richtung einer Kraft in der Ebene die im Raum: quer heisst dort quer in z des Stabs.
_RICHTUNG_IM_RAUM = {
    eben.Lastrichtung.SENKRECHT: Richtung.SENKRECHT,
    eben.Lastrichtung.WAAGRECHT: Richtung.X,
    eben.Lastrichtung.QUER: Richtung.QUER_Z,
    eben.Lastrichtung.LAENGS: Richtung.LAENGS,
}


def _im_raum(system: eben.System) -> System:
    """
    Ein ebenes System als eines im Raum, in der x-z-Ebene -- siehe
    Dateikopf. Was die Ebene nicht kennt, bleibt null; die :data:`EBENE`
    rechnet es nicht.
    """
    return System(
        knoten=[Knoten(k.name, k.x, 0.0, k.z) for k in system.knoten],
        staebe=[Stab(s.name, s.a, s.b, EA=s.EA, EI_y=s.EI, traegt=s.traegt,
                     gelenk_a=s.gelenk_a, gelenk_b=s.gelenk_b, laengs=s.laengs, quer_z=s.quer)
                for s in system.staebe],
        lager=[Lager(l.name, l.knoten, x=l.x, z=l.z, phi_y=l.phi) for l in system.lager],
        lastfaelle=[Lastfall(f.name, [_last_im_raum(l) for l in f.lasten])
                    for f in system.lastfaelle],
        kombinationen=list(system.kombinationen))


def _last_im_raum(last: eben.Last) -> Any:
    """
    Eine Last der Ebene im Raum. Ein Moment im Gegenuhrzeigersinn dreht um
    ``-y`` des Systems -- an einem Stab um sein ``y``, das in der Ebene
    ``-y`` ist (:func:`~opencivil.stabwerk3d.stab.achsen_eben`).
    """
    if isinstance(last, eben.Knotenlast):
        return Knotenlast(last.knoten, F=(last.Fx, 0.0, last.Fz), M=(0.0, -last.M, 0.0))
    richtung = _RICHTUNG_IM_RAUM[last.richtung] if last.art.kraft else Richtung.QUER_Y
    return Stablast(last.stab, last.art, last.wert_a, last.wert_b, richtung, last.von,
                    last.bis, last.projiziert)


#: Ein System im Raum.
RAUM = Art(
    verschiebungen=tuple(zip("xyz", ACHSEN)),
    drehungen=tuple(zip("xyz", ACHSEN)),
    raeumlich=True,
    steifigkeiten=("EA", "EI_y", "EI_z", "GI_T"),
    ohne_steifigkeit="Dehn-, Biege- und Torsionssteifigkeit müssen grösser als null sein.",
    gelenk="θ_{achse}({stab}, {ende})",
    achsen=st3.achsen,
    im_raum=lambda system: system,
)

#: Ein System in der x-z-Ebene -- Drehungen im Gegenuhrzeigersinn, um ``-y``.
EBENE = Art(
    verschiebungen=(("x", ACHSEN[0]), ("z", ACHSEN[2])),
    drehungen=(("", (0.0, -1.0, 0.0)),),
    raeumlich=False,
    steifigkeiten=("EA", "EI_y"),
    ohne_steifigkeit="Dehn- und Biegesteifigkeit müssen grösser als null sein.",
    gelenk="φ({stab}, {ende})",
    achsen=lambda a, b, drehung: st3.achsen_eben(a, b),
    im_raum=_im_raum,
)
