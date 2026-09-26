"""
opencivil/bewehrungssuche/buegel.py -- die Querkraftbewehrung suchen.

VERANTWORTUNG:
Die duennsten Buegel, mit denen der Querkraftnachweis aufgeht -- nach der
Laengsbewehrung, denn ohne statische Hoehe gibt es keinen
Querkraftwiderstand.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Sequence

from opencivil.bewehrungssuche.bewertung import arbeitskopie, bewerte
from opencivil.bewehrungssuche.laengs import TEILUNGEN

#: Buegel dicker als ⌀26 biegt niemand -- die Buegelsuche bleibt darunter.
BUEGELDURCHMESSER: Tuple[float, ...] = (8, 10, 12, 14, 16, 18, 20, 22, 26)


# ===========================================================================
# Querkraftbewehrung
# ===========================================================================

@dataclass
class Buegelloesung:
    """Was die Suche nach den Buegeln gefunden hat."""

    gefunden: bool = False
    durchmesser: float = 0.0
    teilung: float = 0.0
    """Teilung in beiden Richtungen -- ein Buegelraster ist quadratisch."""

    stahlvolumen: float = 0.0
    """Buegelquerschnitt je Flaecheneinheit, in mm²/m² -- das Mass, nach dem
    verglichen wird. Bei Buegeln zaehlt nicht die Flaeche je Streifen, sondern
    wie dicht sie stehen."""

    begruendung: str = ""


def buegel_suchen(projekt, kennung: str, *,
                  teilungen: Sequence[float] = TEILUNGEN,
                  durchmesser: Sequence[float] = BUEGELDURCHMESSER) -> Buegelloesung:
    """
    Die duennsten Buegel, mit denen der Querkraftnachweis aufgeht.

    Gesucht wird ueber Durchmesser und Rasterweite; das Raster ist quadratisch
    (``s_x = s_y``), weil eine Platte in beiden Richtungen gleich durchstanzt
    wird. Verglichen wird ueber den Buegelquerschnitt je Flaecheneinheit --
    ein dicker Stab weit auseinander kann weniger Stahl sein als ein duenner
    eng, und teurer ist er trotzdem seltener.

    Geht es ohne Buegel, kommt das heraus: Durchmesser null.
    """
    teilungen = sorted(t for t in teilungen if t > 0) or list(TEILUNGEN)
    durchmesser = sorted(d for d in durchmesser if d > 0) or list(BUEGELDURCHMESSER)

    # Mit der vorhandenen Laengsbewehrung: die Buegel kommen danach, und ohne
    # statische Hoehe gibt es keinen Querkraftwiderstand.
    arbeit = arbeitskopie(projekt, kennung, kraefte=True, leeren=False)
    eintrag = arbeit.querschnitt(kennung)
    buegel = eintrag.querkraftbewehrung

    # Erst ohne: was man nicht braucht, soll nicht eingebaut werden.
    buegel.durchmesser = 0
    if bewerte(arbeit).erfuellt():
        return Buegelloesung(
            gefunden=True, durchmesser=0.0, teilung=0.0,
            begruendung="Ohne Bügel erfüllt.")

    beste: Optional[Buegelloesung] = None
    for teilung in teilungen:
        buegel.abstand_x = teilung
        buegel.abstand_y = teilung
        buegel.anzahl_y = None
        for d in durchmesser:
            buegel.durchmesser = d
            if not bewerte(arbeit).erfuellt():
                continue
            volumen = math.pi * d * d / 4.0 / (teilung * teilung) * 1e6
            if beste is None or volumen < beste.stahlvolumen:
                beste = Buegelloesung(
                    gefunden=True, durchmesser=d, teilung=teilung,
                    stahlvolumen=volumen,
                    begruendung=(f"⌀{d:.0f}@{teilung:.0f} – "
                                 f"{volumen:.0f} mm²/m²."))
            break        # Groessere Durchmesser bei derselben Teilung sind
                         # nur mehr Stahl fuer dieselbe Aussage.
    if beste is None:
        return Buegelloesung(begruendung=(
            "Kein Bügel aus Liste und Teilungen erfüllt den Querkraftnachweis."))
    return beste


def buegel_uebernehmen(projekt, kennung: str, loesung: Buegelloesung) -> None:
    """Die gefundenen Buegel in die Platte schreiben."""
    buegel = projekt.querschnitt(kennung).querkraftbewehrung
    buegel.durchmesser = loesung.durchmesser
    if loesung.teilung > 0:
        buegel.abstand_x = loesung.teilung
        buegel.abstand_y = loesung.teilung
        buegel.anzahl_y = None
