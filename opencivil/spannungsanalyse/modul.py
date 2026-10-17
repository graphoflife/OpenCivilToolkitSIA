"""
opencivil/spannungsanalyse/modul.py -- der aequivalente E-Modul.

VERANTWORTUNG:
Die letzten zwei Fragen: eine Linie, umgerechnet in den Modul, den ein
reiner, ungerissener, elastischer Betonquerschnitt braeuchte, um sich gleich
stark zu kruemmen oder zu dehnen (:class:`Modullinie`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from opencivil.spannungsanalyse.art import Analyseart
from opencivil.spannungsanalyse.linie import Linie


# ===========================================================================
# Der aequivalente E-Modul
# ===========================================================================

#: Unter diesem Anteil der groessten Kraft der Linie gilt eine Kraft als null --
#: der erste Punkt einer gerissen beginnenden Linie traegt null bis auf die
#: Schranke des Loesers.
NULLKRAFT = 1e-6


@dataclass(frozen=True)
class Modulpunkt:
    """
    Ein Punkt der Linie des aequivalenten Moduls: die laufende Kraft und der
    Modul, der dort gilt -- dazu beide Zustaende zum Vergleich, wie bei der
    Linie, aus der er stammt.
    """

    kraft: float
    modul: Optional[float]
    """In Pa; ``None``, wo er nichts sagt."""

    gerissen: bool
    modul_I: Optional[float]
    modul_II: Optional[float]


@dataclass
class Modullinie:
    """
    Der aequivalente E-Modul ueber dem Moment oder ueber der Normalkraft.

    Der Modul, den ein reiner Betonquerschnitt braeuchte -- ungerissen, ohne
    Stahl, elastisch --, um sich unter der laufenden Kraft gleich stark zu
    kruemmen bzw. zu dehnen wie der bewehrte Querschnitt::

        E_eq = M / (I_c · (chi - chi_0))       I_c = b·h³/12
        E_eq = N / (A_c · (eps_m - eps_0))     A_c = b·h

    Gezaehlt wird ab dem Zustand ohne laufende Kraft -- ``chi_0`` bei M = 0
    unter der festen Normalkraft, ``eps_0`` bei N = 0 unter dem festen
    Moment --, nach Vorgabe (2026-10-11). Was die festgehaltene Kraft allein
    verformt, kann ein gerader, ungerissener Betonquerschnitt nicht abbilden:
    bei unsymmetrischer Bewehrung kruemmt schon eine Normalkraft, und ein
    gerissener Querschnitt dehnt sich schon unter dem Moment allein. Ab null
    gezaehlt, ergaebe das nahe null Ausreisser -- am Beispiel bei M = 30 kNm
    und N = 16 kN 99 500 N/mm², fast das Dreifache von E_cm. Ist die feste
    Kraft null, ist es genau ``M = E·I·chi`` bzw. ``N = E·A·eps``.

    Umgerechnet wird jeder Punkt der :class:`Linie`; gerechnet wird nichts
    Neues. So kann diese Linie nichts anderes zeigen als die M-chi- oder
    N-eps-Linie daneben.
    """

    art: Analyseart
    linie: Linie
    """Die M-chi- oder N-eps-Linie, aus der umgerechnet wird."""

    bezug: float
    """``I_c`` in m⁴ bzw. ``A_c`` in m² -- der reine Betonquerschnitt."""

    null: float
    """Die Verformung ohne laufende Kraft: ``chi_0`` bzw. ``eps_0``."""

    E_cm: float
    """Zum Vergleich: ``E_eq/E_cm`` ist der Faktor, um den man E_cm abmindert."""

    punkte: List[Modulpunkt] = field(default_factory=list)

    def modul(self, kraft: float, verformung: float) -> Optional[float]:
        """``Kraft / (Bezug · (Verformung − null))`` -- ``None``, wo das nichts sagt."""
        aenderung = verformung - self.null
        if kraft == 0.0 or aenderung == 0.0:
            return None
        return kraft / (self.bezug * aenderung)

    @property
    def ungerissen(self) -> Optional[float]:
        """Der Modul des ungerissenen Teils -- dort ist der Querschnitt linear."""
        return next((p.modul for p in reversed(self.punkte)
                     if not p.gerissen and p.modul is not None), None)

    @property
    def riss(self) -> Optional[float]:
        """Der Modul gleich nach dem Riss, bei derselben Kraft."""
        sprung = self.linie.sprung
        return None if sprung is None else self.modul(sprung[1].kraft, sprung[1].verformung)

    @property
    def fliessen(self) -> Optional[float]:
        f = self.linie.fliessen
        return None if f is None else self.modul(f.kraft, f.verformung)

    @property
    def ende(self) -> Optional[float]:
        """Der Modul am Ende der Linie -- beim Bruch, oder ungerissen, wenn sie es bleibt."""
        return next((p.modul for p in reversed(self.punkte) if p.modul is not None), None)


def aequivalenter_modul(linie: Linie, *, I_c: float, A_c: float, E_cm: float) -> Modullinie:
    """
    Die M-chi- oder N-eps-Linie als Linie des aequivalenten Moduls -- siehe
    :class:`Modullinie`. Beide Vergleichszustaende zaehlen ab ihrer eigenen
    Verformung ohne laufende Kraft. ``I_c`` und ``A_c`` sind der reine
    Betonquerschnitt, an dem sich der Modul misst.
    """
    momente = linie.art is Analyseart.MOMENT_KRUEMMUNG
    art = Analyseart.MOMENT_EMODUL if momente else Analyseart.NORMALKRAFT_EMODUL
    bezug = I_c if momente else A_c
    if not linie.punkte:
        return Modullinie(art, linie, bezug, 0.0, E_cm)

    # Der erste Punkt ist der Zustand ohne laufende Kraft -- ungerissen bei
    # null, oder gerissen bis auf die Schranke des Loesers.
    massstab = max(abs(p.kraft) for p in linie.punkte) or 1.0
    erster = linie.punkte[0]
    ohne = abs(erster.kraft) <= NULLKRAFT * massstab
    null, null_I, null_II = ((erster.verformung, erster.verformung_I, erster.verformung_II)
                             if ohne else (0.0, 0.0, 0.0))
    modul = Modullinie(art, linie, bezug, null, E_cm)

    def geteilt(kraft: float, verformung: Optional[float],
                ab: Optional[float]) -> Optional[float]:
        if verformung is None or ab is None or kraft == 0.0 or verformung == ab:
            return None
        return kraft / (bezug * (verformung - ab))

    for p in (linie.punkte[1:] if ohne else linie.punkte):
        modul.punkte.append(Modulpunkt(
            kraft=p.kraft, modul=geteilt(p.kraft, p.verformung, null), gerissen=p.gerissen,
            modul_I=geteilt(p.kraft, p.verformung_I, null_I),
            modul_II=geteilt(p.kraft, p.verformung_II, null_II)))

    # Bei null ist der Modul null durch null. Ungerissen ist der Querschnitt
    # linear: dort gilt der Wert des naechsten Punkts genau, und die Linie
    # beginnt bei null statt beim ersten Schritt.
    if ohne and not erster.gerissen and modul.punkte and not modul.punkte[0].gerissen:
        naechster = modul.punkte[0]
        modul.punkte.insert(0, Modulpunkt(
            kraft=0.0, modul=naechster.modul, gerissen=False,
            modul_I=naechster.modul_I, modul_II=naechster.modul_II))
    return modul
