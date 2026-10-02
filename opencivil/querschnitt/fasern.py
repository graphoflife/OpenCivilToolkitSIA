"""
opencivil/querschnitt/fasern.py -- Der Querschnitt als Summe von Fasern.

VERANTWORTUNG:
Zwei Dinge, die jede Rechnung an einer ebenen Dehnungsverteilung braucht,
gleich ob Platte oder gezeichneter Querschnitt:

1. **Die inneren Kraefte einer Dehnungsebene.** Fasern mit Lage, Flaeche und
   Werkstoffgesetz, dazu Staebe, die das Material an ihrer Stelle verdraengen.
2. **Die Dehnungsgrenzen.** In welchem Bereich die Ebene liegen darf, damit
   jedes Werkstoffgesetz gilt.

DIE EBENE::

    eps(v) = eps_m + chi * v

``v`` ist der Abstand zur Bezugsachse, gemessen in Zugrichtung: bei der
Platte ``z - h/2`` (z von oben nach unten), beim gezeichneten Querschnitt der
Abstand vom Schwerpunkt entlang der Zugrichtung. Ein positives ``chi`` zieht
also auf der Seite, auf die ``v`` waechst.

``quer`` ist die Lage einer Faser entlang der Nulllinie. Nur wer auch das
Moment um die zweite Achse braucht -- die schiefe Biegung -- gibt sie an. Die
Platte gibt sie nicht an, und ihre Schleife bleibt so schnell wie bisher.

DIE GRENZEN:
Jede Grenze ist eine Stelle ``v`` mit einem zulaessigen Dehnungsbereich. Weil
die Ebene linear ist, wird daraus in ``(eps_m, chi)`` je Grenze ein Streifen
zwischen zwei Geraden, zusammen ein konvexes Vieleck. Bei festem ``chi`` ist
sein Schnitt das Fenster fuer ``eps_m`` -- das braucht der Loeser in
:mod:`opencivil.nachweis.querschnittsloeser`. Sein Rand ist der
Dehnungsfaecher -- das braucht die Interaktionslinie. Eine Regel, zwei Nutzer.

EINHEITEN:
SI-Basis wie im ganzen Querschnittsmodul: Meter, Quadratmeter, Pascal.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Optional, Sequence, Tuple, Union

Gesetz = Callable[[float], float]


@dataclass(frozen=True)
class Schnittkraefte:
    """Was eine Dehnungsebene an inneren Kraeften erzeugt."""

    N: float
    """in N, Zug positiv."""

    M: float
    """in Nm um die Bezugsachse: ``Σ F·v``."""

    M_quer: float = 0.0
    """in Nm, der Arm entlang der Nulllinie: ``Σ F·quer``. Nur bei schiefer
    Biegung; sonst null."""


@dataclass(frozen=True)
class Fasergruppe:
    """
    Fasern aus einem Werkstoff.

    ``flaechen`` ist eine Zahl, wenn alle Fasern gleich gross sind -- dann
    laeuft die Summe ohne Nachschlagen, und das ist die Schleife, die bei der
    Platte hunderttausendfach laeuft. Sonst eine Flaeche je Faser.
    """

    gesetz: Gesetz
    arme: Tuple[float, ...]
    flaechen: Union[float, Tuple[float, ...]]
    quer: Optional[Tuple[float, ...]] = None


@dataclass(frozen=True)
class Stab:
    """
    Ein Bewehrungsstab -- oder ein Stueck einer verschmierten Stablinie.

    ``verdraengt`` ist das Gesetz des Materials, in dem er liegt: an seiner
    Stelle zaehlt der Stab, nicht der Beton, sonst zaehlte dieselbe Flaeche
    zweimal.
    """

    arm: float
    flaeche: float
    gesetz: Gesetz
    verdraengt: Optional[Gesetz] = None
    quer: float = 0.0


class Faserquerschnitt:
    """Fasergruppen und Staebe -- und die Kraefte, die eine Ebene in ihnen weckt."""

    def __init__(self, gruppen: Sequence[Fasergruppe], staebe: Sequence[Stab]) -> None:
        self.gruppen = tuple(gruppen)
        self.staebe = tuple(staebe)
        #: Ob ein Arm entlang der Nulllinie vorkommt -- nur dann laeuft das
        #: zweite Moment mit.
        self.schief = (any(g.quer is not None for g in self.gruppen)
                       or any(s.quer for s in self.staebe))
        # Fuer die Schleife als schlichte Tupel, und jede Fallunterscheidung
        # schon hier entschieden: Entpacken ist schneller als der Zugriff auf
        # die Felder einer Datenklasse, und die Schleife laeuft
        # hunderttausendfach.
        self._gleich = tuple((g.gesetz, g.arme, g.flaechen) for g in self.gruppen
                             if g.quer is None and not isinstance(g.flaechen, tuple))
        self._einzeln = tuple(
            (g.gesetz, tuple(zip(
                g.arme,
                g.flaechen if isinstance(g.flaechen, tuple) else (g.flaechen,) * len(g.arme),
                g.quer if g.quer is not None else (0.0,) * len(g.arme))))
            for g in self.gruppen
            if not (g.quer is None and not isinstance(g.flaechen, tuple)))
        self._staebe = tuple((s.arm, s.flaeche, s.gesetz, s.verdraengt, s.quer)
                             for s in self.staebe)

    def kraefte(self, eps_m: float, chi: float) -> Schnittkraefte:
        """
        Die inneren Kraefte der Ebene ``eps(v) = eps_m + chi·v``.

        Ortsgebundene Namen statt ``self.``: diese Schleife laeuft je Nachweis
        hunderttausende Male, und jeder Zugriff ueber ein Attribut kostet darin
        eine Suche.
        """
        N = 0.0
        M = 0.0
        M_quer = 0.0
        for gesetz, arme, flaeche in self._gleich:
            for arm in arme:
                kraft = gesetz(eps_m + chi * arm) * flaeche
                N += kraft
                M += kraft * arm
        for gesetz, fasern in self._einzeln:
            for arm, flaeche, u in fasern:
                kraft = gesetz(eps_m + chi * arm) * flaeche
                N += kraft
                M += kraft * arm
                M_quer += kraft * u

        schief = self.schief
        for arm, flaeche, gesetz, verdraengt, quer in self._staebe:
            eps = eps_m + chi * arm
            if verdraengt is None:
                kraft = gesetz(eps) * flaeche
            else:
                kraft = (gesetz(eps) - verdraengt(eps)) * flaeche
            N += kraft
            M += kraft * arm
            if schief:
                M_quer += kraft * quer
        return Schnittkraefte(N=N, M=M, M_quer=M_quer)


# ===========================================================================
# Dehnungsgrenzen
# ===========================================================================


@dataclass(frozen=True)
class Dehnungsgrenze:
    """An der Stelle ``arm`` muss die Dehnung zwischen ``eps_min`` und ``eps_max`` liegen."""

    arm: float
    eps_min: float
    """Groesste zulaessige Stauchung, negativ."""

    eps_max: float
    """Groesste zulaessige Dehnung, positiv; ``inf``, wo es keine gibt."""


class Dehnungsgrenzen:
    """Die Grenzen eines Querschnitts -- und was aus ihnen fuer die Ebene folgt."""

    def __init__(self, grenzen: Sequence[Dehnungsgrenze]) -> None:
        if not grenzen:
            raise ValueError("Ein Querschnitt ohne Dehnungsgrenzen hat keinen Bruchzustand.")
        self.grenzen = tuple(grenzen)

    def fenster(self, chi: float) -> Optional[Tuple[float, float]]:
        """
        In welchem Bereich ``eps_m`` liegen darf, damit an keiner Grenze die
        Dehnung aus ihrem Bereich faellt -- bei dieser Kruemmung.

        Jede Grenze verlangt ``eps_min <= eps_m + chi·arm <= eps_max``. Ist das
        Fenster leer, ist die Kruemmung fuer diesen Querschnitt zu gross.
        """
        unten = max(g.eps_min - chi * g.arm for g in self.grenzen)
        oben = min(g.eps_max - chi * g.arm for g in self.grenzen)
        return (unten, oben) if unten <= oben else None

    def kruemmungsgrenze(self, *, positiv: bool) -> float:
        """
        Die groesste Kruemmung (als Betrag), bei der noch ein Fenster bleibt.

        Fuer jedes Paar von Grenzen ``k`` und ``l``, deren Abstand die
        Kruemmung dehnt, gilt ``|chi| <= (eps_max_l - eps_min_k) / Abstand``.
        Massgebend ist das engste Paar. Bei der Platte ist das eines: die
        Unterkante gegen die Oberkante, ``(eps_zug + eps_druck) / h``.
        """
        grenze = math.inf
        for k in self.grenzen:
            for l in self.grenzen:
                abstand = (l.arm - k.arm) if positiv else (k.arm - l.arm)
                if abstand > 0.0:
                    grenze = min(grenze, (l.eps_max - k.eps_min) / abstand)
        if not math.isfinite(grenze):
            raise ValueError("Alle Dehnungsgrenzen liegen an derselben Stelle.")
        return grenze
