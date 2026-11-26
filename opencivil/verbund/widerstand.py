"""
opencivil/verbund/widerstand.py -- was ein Verbundquerschnitt in einem Lastfall aufnimmt.

VERANTWORTUNG:
Zu einem Lastfall -- ``N``, die Momente um den Bezugspunkt, die Querkraefte
-- der plastische Widerstand des gezeichneten Verbundquerschnitts nach
SIA 264:2014, ohne Herleitung, in N, mm und N/mm² (:func:`rechnen`); dazu
der Widerstand bei ``N = 0`` zu einer Seite (:func:`biegewiderstand`). Die
Herleitung schreiben :mod:`opencivil.nachweis.qa_verbund` und
:mod:`opencivil.nachweis.qa_verbund_kennzahlen`. Der Reihe nach:

* grosse Querkraft mindert die Bleche, in denen sie steht, wie im Stahl
  (:func:`~opencivil.stahlbau.widerstand.abmindern`): die Querkraft traegt
  der Stahl allein (4.3.2.2);
* der plastische Zustand bei ``N_Ed`` in der Richtung des Moments, je
  Gruppe mit ihrer Festigkeit: Baustahl ``±f_y/γ_a``, Beton gedrueckt
  ``0.85 f_ck/γ_c``, gezogen nichts (4.3.2.1), Betonstahl ``±f_sk/γ_s``
  (5.1.2.1; 4.1.3);
* ob er gilt: jedes Blech in Klasse 1 oder 2 (4.2.2, Tabelle 2), und wo
  ein Moment Betonstahl zieht, dieser in der Duktilitaetsklasse B oder C
  (5.1.2.3); sonst steht grau, warum nicht (:attr:`Fall.grund`);
* ``β`` nach 5.1.2.2, wo ein Baustahl S420 oder S460 ist.

DER MASSSTAB:
Wie beim Stahl (:mod:`opencivil.stahlbau.widerstand`): ``N`` bleibt, das
Moment waechst in seiner Richtung, bis der Widerstand erreicht ist --
``α = M_Rd/M_Ed``. Ohne Moment ``N_Rd/N_Ed``. Traegt schon die Normalkraft
allein nicht, misst ``α`` sie.

5.1.2.3 -- nach Vorgabe, nicht nachgeschlagen:
Die Norm nennt den Fall des negativen Moments eines Traegers: die Platte
gezogen. Der Querschnitt weiss nicht, was Platte ist; gefragt wird darum
jeder Betonstahl, den ein Moment zieht. Ohne Moment gilt die Regel nicht.

β (5.1.2.2, Figur 1):
``x_p`` ist der Abstand der Nulllinie vom gedrueckten Rand des Betons, ``h``
die Hoehe des ganzen Querschnitts quer zu ihr. ``β = 1`` bis ``x_p/h =
0.15``, dann gerade bis 0.85 bei 0.4. Darueber endet die Figur; das Werkzeug
rechnet dort nicht (nach Vorgabe, nicht nachgeschlagen). Ob ein Baustahl
S420 oder S460 ist, sagt seine Fliessgrenze bis 40 mm Dicke: ab 420 N/mm²
(nach Vorgabe, nicht nachgeschlagen).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Tuple

from opencivil.material.basis import Baustoffart
from opencivil.material.betonstahl import duktilitaetsklasse
from opencivil.querschnitt.biegung import Biegung
from opencivil.querschnitt.geometrie import Punkt
from opencivil.querschnitt.plastisch import DRUCK, ZUG, Linie, Starrplastisch, Zustand
from opencivil.querschnitt.zugseite import Zugseite
from opencivil.stahlbau import widerstand as wd
from opencivil.stahlbau.querschnitt import Blechzustand, Teil, normale
from opencivil.verbund.querschnitt import Verbundquerschnitt

REFERENZ_PLASTISCH = "SIA 264:2014, 5.1.2.1; 4.1.3"
REFERENZ_KLASSE = ("SIA 264:2014, 4.2.2.1, Tabellen 2 und 3; 5.2.1.3; SIA 263:2013, "
                   "Tabellen 5a und 5b")
REFERENZ_BETA = "SIA 264:2014, 5.1.2.2, Figur 1"
REFERENZ_DUKTIL = "SIA 264:2014, 5.1.2.3"
REFERENZ_QUERKRAFT = "SIA 264:2014, 4.3.2.2; SIA 263:2013, 5.1.5.1, (43)"
REFERENZ_SCHUB = "SIA 264:2014, 4.3.2.2; SIA 263:2013, 5.1.4.1, (41)"

#: Ab welcher Fliessgrenze bis 40 mm ein Baustahl als S420 oder S460 zaehlt, in N/mm².
HOCHFEST = 420.0

#: Figur 1: bis wo ``β = 1`` gilt, wo die Gerade endet und mit welchem Wert.
BETA_AB, BETA_BIS, BETA_ENDE = 0.15, 0.4, 0.85

#: Warum ein Fall grau bleibt.
UEBER_KLASSE_2 = ("Ein Blech liegt über Klasse 2: plastisch darf der Verbundquerschnitt so nicht "
                  "rechnen, und elastisch nach 5.1.2.4 und 5.1.2.5 rechnet ihn das Werkzeug "
                  "noch nicht.")
UEBER_FIGUR_1 = ("x_p/h liegt über 0.4, wo Figur 1 endet: dort rechnet das Werkzeug den "
                 "Biegewiderstand nicht (nach Vorgabe, nicht nachgeschlagen).")


def duktil_text(namen: Sequence[str]) -> str:
    """Warum ein gezogener Betonstahl den plastischen Widerstand verbietet (5.1.2.3)."""
    liste = ", ".join(f"«{n}»" for n in namen)
    return (f"Gezogener Betonstahl {liste} ist nicht in der Duktilitätsklasse B oder C: "
            f"plastisch darf der Verbundquerschnitt so nicht rechnen (5.1.2.3), und elastisch "
            f"rechnet ihn das Werkzeug noch nicht.")


@dataclass(frozen=True)
class Beta:
    """``x_p`` und ``h`` nach 5.1.2.2 an einer Nulllinie, in mm -- und was daraus folgt."""

    x_p: float
    h: float

    @property
    def verhaeltnis(self) -> float:
        return self.x_p / self.h

    @property
    def beta(self) -> Optional[float]:
        """``β`` nach Figur 1 -- ``None`` ueber 0.4, wo sie endet."""
        r = self.verhaeltnis
        if r <= BETA_AB:
            return 1.0
        if r <= BETA_BIS:
            return 1.0 - (1.0 - BETA_ENDE) * (r - BETA_AB) / (BETA_BIS - BETA_AB)
        return None


@dataclass
class Fall:
    """Was ein Lastfall am Verbundquerschnitt ergibt -- siehe Dateikopf. In N und N·mm."""

    N: float
    M_y: float
    M_z: float
    moment: float
    """Wie gross das Moment ist (:meth:`~opencivil.querschnitt.biegung.Biegung.betrag`)."""

    querkraefte: Tuple[wd.Querkraft, ...]
    abgemindert: wd.Abgemindert
    starr: Starrplastisch
    linie: Linie
    """Die plastische Nulllinie -- ohne Moment gleichmaessig gedrueckt oder gezogen."""

    zustaende: List[Blechzustand]
    freie: List[Teil]
    """Die frei gezeichneten Flaechen aus Baustahl, die gedrueckt sind."""

    klasse: int
    """1, 2 oder 3 fuer «über 2» (:mod:`opencivil.verbund.querschnitt`)."""

    plastisch: Optional[Zustand] = None
    beta: Optional[Beta] = None
    """Nur mit einem Baustahl S420 oder S460 und gedruecktem Beton."""

    sproede: List[str] = field(default_factory=list)
    """Die Namen der gezogenen Betonstaehle, die nicht in Klasse B oder C sind (5.1.2.3)."""

    grund: str = ""
    """Warum der Fall grau bleibt -- leer, wo er rechnet."""

    alpha: Optional[float] = None
    alpha_N: Optional[float] = None
    """Wo die Normalkraft allein nicht traegt: um welchen Faktor sie kleiner sein muesste."""

    @property
    def ohne_moment(self) -> bool:
        return self.moment <= wd.KEIN_MOMENT

    @property
    def faktor_beta(self) -> float:
        return self.beta.beta if self.beta is not None and self.beta.beta is not None else 1.0


def _fall(verbund: Verbundquerschnitt, ab: wd.Abgemindert, starr: Starrplastisch,
          eps: Sequence[float], N: float, M_y: float, M_z: float, moment: float,
          querkraefte: Sequence[wd.Querkraft], linie: Linie) -> Fall:
    """Der Fall mit den Klassen an der Nulllinie -- grau, wo ein Blech ueber Klasse 2 liegt."""
    zustaende = verbund.zustaende(linie, eps, ab.stahl)
    freie = verbund.freie_gedrueckt(linie)
    klasse = max([z.klasse for z in zustaende] + [3 for _ in freie], default=1)
    return Fall(N, M_y, M_z, moment, tuple(querkraefte), ab, starr, linie, zustaende, freie,
                klasse, grund=UEBER_KLASSE_2 if klasse > 2 else "")


def sproede_gezogen(verbund: Verbundquerschnitt, linie: Linie) -> List[str]:
    """Die gezogenen Betonstaehle, die nicht in der Duktilitaetsklasse B oder C sind (5.1.2.3)."""
    namen: List[str] = []
    for s in verbund.weitere:
        stoff = verbund.gruppen[s.gruppe].stoff
        if s.gewicht > 0.0 and stoff.art is Baustoffart.BETONSTAHL \
                and linie.d((s.werte.y_S, s.werte.z_S)) > 0.0 \
                and duktilitaetsklasse(stoff.sorte) not in ("B", "C") and stoff.name not in namen:
            namen.append(stoff.name)
    return namen


def _bewerten(fall: Fall, verbund: Verbundquerschnitt, hochfest: bool) -> None:
    """5.1.2.3 und ``β`` an einem plastischen Zustand mit Moment -- siehe Dateikopf."""
    linie = fall.plastisch.linie
    fall.sproede = sproede_gezogen(verbund, linie)
    if fall.sproede and not fall.grund:
        fall.grund = duktil_text(fall.sproede)
    if hochfest:
        x_p = verbund.druckzone_beton(linie)
        if x_p > 0.0:
            fall.beta = Beta(x_p, verbund.hoehe(linie.n))
            if fall.beta.beta is None and not fall.grund:
                fall.grund = UEBER_FIGUR_1


def rechnen(verbund: Verbundquerschnitt, zug: Sequence[float], druck: Sequence[float],
            eps: Sequence[float], N: float, M_y: float, M_z: float,
            querkraefte: Sequence[wd.Querkraft], bezug: Punkt, biegung: Biegung,
            hochfest: bool) -> Fall:
    """
    Ein Lastfall am Verbundquerschnitt -- siehe Dateikopf. ``zug`` und
    ``druck`` je Gruppe die Festigkeiten, ``eps`` je Gruppe des Stahls sein
    ``ε``; ``M_y`` und ``M_z``, wie sie zaehlen
    (:meth:`~opencivil.querschnitt.biegung.Biegung.wirkt`); ``hochfest``, ob
    ein Baustahl S420 oder S460 ist.
    """
    ab = wd.abmindern(verbund.stahl, querkraefte)
    starr = verbund.starr(zug, druck, ab.stahl)
    moment = biegung.betrag(M_y, M_z)
    gleichmaessig = DRUCK if N < 0.0 else ZUG
    N_Rd = starr.zugkraft if N >= 0.0 else -starr.druckkraft
    if moment <= wd.KEIN_MOMENT:
        fall = _fall(verbund, ab, starr, eps, N, M_y, M_z, moment, querkraefte, gleichmaessig)
        if not fall.grund:
            fall.alpha = N_Rd / N if N != 0.0 else math.inf
        return fall
    pl = starr.zustand(N, M_y, M_z, bezug, biegung.neigung(M_y))
    if pl is None:
        fall = _fall(verbund, ab, starr, eps, N, M_y, M_z, moment, querkraefte, gleichmaessig)
        fall.grund, fall.alpha_N = "", N_Rd / N
        return fall
    fall = _fall(verbund, ab, starr, eps, N, M_y, M_z, moment, querkraefte, pl.linie)
    fall.plastisch = pl
    _bewerten(fall, verbund, hochfest)
    if not fall.grund:
        fall.alpha = fall.faktor_beta * biegung.betrag(pl.M_y, pl.M_z) / moment
    return fall


def biegewiderstand(verbund: Verbundquerschnitt, zug: Sequence[float], druck: Sequence[float],
                    eps: Sequence[float], seite: Zugseite, bezug: Punkt,
                    hochfest: bool) -> Fall:
    """
    Der Widerstand bei ``N = 0`` gegen ein Moment, das ``seite`` zieht --
    die Nulllinie parallel zu y oder z. Sein Moment steht in
    :attr:`Fall.plastisch`, mit ``β`` mal :attr:`Fall.faktor_beta`.
    """
    ab = wd.abmindern(verbund.stahl, ())
    starr = verbund.starr(zug, druck)
    n = normale(seite)
    linie = Linie(n, starr.nulllinie(n))
    pl = Zustand(linie, *starr.kraefte(linie, bezug))
    fall = _fall(verbund, ab, starr, eps, 0.0, pl.M_y, pl.M_z,
                 math.hypot(pl.M_y, pl.M_z), (), linie)
    fall.plastisch = pl
    _bewerten(fall, verbund, hochfest)
    return fall
