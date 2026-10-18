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

GESETZE MIT SPRUNG:
Gelesen wird die Spannung in der Mitte jeder Faser. Bei einem stetigen Gesetz
ist das genau genug. Springt es -- der Spannungsblock --, springt mit jeder
Faser, die den Knick ueberschreitet, auch N, und keine Ebene trifft eine
verlangte Normalkraft genau. Ein solches Gesetz hat darum ``mittel(eps_a,
eps_b)``, die mittlere Spannung ueber einen linear verlaufenden Bereich. Wo
eine Faser ihre Dicke kennt (``dicken``, beim Stab ``dicke`` fuer das
verdraengte Material), wird damit gemittelt.

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
from typing import List, Optional, Sequence, Tuple, Union

from opencivil.querschnitt.werkstoffgesetz import Gesetz

#: Fasern ueber die Plattenhoehe -- und Streifen, wo der gezeichnete
#: Querschnitt wie die Platte rechnet. 60 reichen: die Betonspannung ist
#: stetig, und der Fehler der Mittelpunktsregel faellt mit dem Quadrat der
#: Faserdicke.
FASERN = 60


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
    dicken: Optional[Tuple[float, ...]] = None
    """Ausdehnung jeder Faser in ``v`` -- gebraucht, wenn das Gesetz springt."""


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
    dicke: float = 0.0
    """Ausdehnung in ``v`` fuer das verdraengte Material, wenn dessen Gesetz springt."""


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
        def gemittelt(g: Fasergruppe) -> bool:
            return g.dicken is not None and g.gesetz.mittel is not None

        def einzeln(g: Fasergruppe):
            n = len(g.arme)
            return tuple(zip(
                g.arme,
                g.flaechen if isinstance(g.flaechen, tuple) else (g.flaechen,) * n,
                g.quer if g.quer is not None else (0.0,) * n))

        # Gerufen wird ``funktion`` jedes Gesetzes, ohne den Umweg ueber
        # ``__call__``, der je Aufruf ein Fuenftel kostete.
        self._gleich = tuple((g.gesetz.funktion, g.arme, g.flaechen) for g in self.gruppen
                             if g.quer is None and not isinstance(g.flaechen, tuple)
                             and not gemittelt(g))
        self._einzeln = tuple(
            (g.gesetz.funktion, einzeln(g)) for g in self.gruppen
            if not (g.quer is None and not isinstance(g.flaechen, tuple)) and not gemittelt(g))
        self._gemittelt = tuple(
            (g.gesetz.mittel, tuple((arm, a, u, d / 2.0)
                                    for (arm, a, u), d in zip(einzeln(g), g.dicken)))
            for g in self.gruppen if gemittelt(g))
        self._staebe = tuple(
            (s.arm, s.flaeche, s.gesetz.funktion,
             None if s.verdraengt is None else s.verdraengt.funktion, s.quer,
             s.verdraengt.mittel if s.verdraengt is not None and s.dicke > 0.0 else None,
             s.dicke / 2.0)
            for s in self.staebe)

    @property
    def springt(self) -> bool:
        """
        Ob ein Gesetz springt und darum ueber die Faser gemittelt wird -- der
        Spannungsblock, auch wo ein Stab ihn verdraengt.
        """
        return bool(self._gemittelt) or any(s[5] is not None for s in self._staebe)

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
        for mittel, fasern in self._gemittelt:
            for arm, flaeche, u, halb in fasern:
                kraft = mittel(eps_m + chi * (arm - halb), eps_m + chi * (arm + halb)) * flaeche
                N += kraft
                M += kraft * arm
                M_quer += kraft * u

        schief = self.schief
        for arm, flaeche, gesetz, verdraengt, quer, mittel, halb in self._staebe:
            eps = eps_m + chi * arm
            if verdraengt is None:
                kraft = gesetz(eps) * flaeche
            elif mittel is None:
                kraft = (gesetz(eps) - verdraengt(eps)) * flaeche
            else:
                kraft = (gesetz(eps) - mittel(eps - chi * halb, eps + chi * halb)) * flaeche
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
    """
    An der Stelle ``arm`` muss die Dehnung zwischen ``eps_min`` und ``eps_max``
    liegen. ``name`` sagt, was dort liegt -- «Stahl der 1. Lage» --, fuer
    die Mitschrift und fuer Meldungen. Bis 2026-10-18 reisten die Namen als
    eigenes Tupel neben den Grenzen durch sechs Gegenstaende und wurden nach
    ihrer Stelle zugeordnet.
    """

    arm: float
    eps_min: float
    """Groesste zulaessige Stauchung, negativ."""

    eps_max: float
    """Groesste zulaessige Dehnung, positiv; ``inf``, wo es keine gibt."""

    name: str = ""


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

    def verletzt(self, eps_m: float, chi: float, *,
                 toleranz: float = 0.0) -> List[Tuple[Dehnungsgrenze, float]]:
        """
        Die Grenzen, an denen die Ebene ``eps_m + chi·arm`` aus ihrem Bereich
        faellt, je mit der Dehnung dort -- an denselben Grenzen, in denen der
        Loeser sucht. ``toleranz`` laesst eine gerundete Eingabe gelten.
        """
        return [(g, eps) for g in self.grenzen for eps in (eps_m + chi * g.arm,)
                if eps < g.eps_min - toleranz or eps > g.eps_max + toleranz]

    def kruemmungsfenster(self, eps_m: float) -> Optional[Tuple[float, float]]:
        """
        In welchem Bereich ``chi`` liegen darf, damit an keiner Grenze die
        Dehnung aus ihrem Bereich faellt -- bei dieser Dehnung ``eps_m`` im
        Bezugspunkt. Das Gegenstueck zu :meth:`fenster`, fuer Linien, die
        ueber die Dehnung statt ueber die Kruemmung laufen.

        Unbegrenzt bleibt eine Seite nie: dafuer sorgen zwei Grenzen auf
        verschiedenen Seiten des Bezugspunkts, und jeder Querschnitt hat zwei
        Raender.
        """
        unten, oben = -math.inf, math.inf
        for g in self.grenzen:
            tief, hoch = g.eps_min - eps_m, g.eps_max - eps_m
            if g.arm > 0.0:
                unten, oben = max(unten, tief / g.arm), min(oben, hoch / g.arm)
            elif g.arm < 0.0:
                unten, oben = max(unten, hoch / g.arm), min(oben, tief / g.arm)
            elif not tief <= 0.0 <= hoch:
                return None
        return (unten, oben) if unten <= oben else None

    def kruemmungsgrenze(self, *, positiv: bool) -> float:
        """
        Die groesste Kruemmung (als Betrag), bei der noch ein Fenster bleibt.

        Fuer jedes Paar von Grenzen ``k`` und ``l``, deren Abstand die
        Kruemmung dehnt, gilt ``|chi| <= (eps_max_l - eps_min_k) / Abstand``.
        Massgebend ist das engste Paar. Bei der Platte ist das meist die
        unterste Lage gegen den oberen Rand, ``(eps_ud + eps_c2d) / d``.
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
