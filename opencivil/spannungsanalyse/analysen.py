"""
opencivil/spannungsanalyse/analysen.py -- die Analysen eines Projekts.

VERANTWORTUNG:
Je Bauteil -- Platte oder gezeichneter Querschnitt -- und je Fall die eine
Frage, mit dem Paar seiner Richtung und seiner Wahl, dazu die Herleitung
jeder Linie (:func:`analysen`).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Mapping, Optional, Tuple, Union

from opencivil.core.protokoll import Protokoll, StillesProtokoll
from opencivil.spannungsanalyse.art import Analyseart
from opencivil.spannungsanalyse.bild import (
    Querschnittsbild, aus_dehnungen, aus_schnittgroessen,
)
from opencivil.spannungsanalyse.herleitung import herleitung
from opencivil.spannungsanalyse.linie import Linie, Paar, moment_kruemmung, normalkraft_dehnung
from opencivil.spannungsanalyse.modul import Modullinie, aequivalenter_modul
from opencivil.spannungsanalyse.platte import loeserpaar
from opencivil.spannungsanalyse.schnitt import schnittpaar

if TYPE_CHECKING:
    from opencivil.core.rechenwerk import Loesung
    from opencivil.projekt import Aufbau


# ===========================================================================
# Die Analysen eines Projekts
# ===========================================================================


@dataclass
class Analyse:
    """Ein Spannungsfall der Beschreibung -- und was die Auswertung ergab."""

    fall: Any
    """Der :class:`SpannungsfallEintrag`, wie er in der Beschreibung steht."""

    art: Analyseart
    richtung: Any
    """Die Tragrichtung einer Platte (:class:`Richtung`) oder die Zugseite eines
    gezeichneten Querschnitts (:class:`~opencivil.querschnitt.zugseite.Zugseite`)."""

    richtung_text: str = ""
    """Wie sie neben dem Titel steht -- «x», «Zug unten»."""

    bild: Optional[Querschnittsbild] = None
    kurve: Optional[Union[Linie, "Modullinie"]] = None
    """Die M-chi- oder N-eps-Linie -- oder der aequivalente Modul daraus."""

    paar: Optional[Paar] = None
    """Womit gerechnet wurde -- das Paar mit Kriechzahl, Wertesatz, Betongesetz:
    das der Platte oder das des gezeichneten Querschnitts."""

    hinweis: str = ""
    """Warum es nichts auszuwerten gab, falls es nichts gab."""

    @property
    def moeglich(self) -> bool:
        return self.bild is not None or self.kurve is not None


def auswerten(fall, art: Analyseart, paar: Paar) -> Tuple[
        Optional[Querschnittsbild], Optional[Union[Linie, Modullinie]]]:
    """
    Die eine der sechs Fragen stellen, die dieser Fall stellt -- in SI, an
    das Paar einer Platte oder eines gezeichneten Querschnitts. Gelesen wird
    nur, was die Frage braucht (:attr:`Analyseart.eingaben`), und in der
    Einheit seines Feldes: in der zeigt die Maske die Zahl. Bis 2026-10-18
    rechnete hier ein eigenes ``* 1e3`` -- eine zweite Angabe der Einheit,
    die still um 10³ haette abweichen koennen, wie zuvor beim Grundbruch.
    """
    si = {feld: fall.si(feld) for feld in art.eingaben}
    if art is Analyseart.DEHNUNGEN:
        return aus_dehnungen(paar.gerissen, eps_oben=si["eps_oben"],
                             eps_unten=si["eps_unten"]), None
    if art.linie is Analyseart.MOMENT_KRUEMMUNG:
        linie = moment_kruemmung(paar, N=si["N_Ed"])
    elif art.linie is Analyseart.NORMALKRAFT_DEHNUNG:
        linie = normalkraft_dehnung(paar, M=si["M_Ed"])
    else:
        return aus_schnittgroessen(paar.ebenen().gerissen, N=si["N_Ed"],
                                   M=si["M_Ed"], art=paar.wahl.art), None
    if art.modul:
        return None, aequivalenter_modul(linie, I_c=paar.I_c, A_c=paar.A_c, E_cm=paar.E_cm)
    return None, linie


@dataclass(frozen=True)
class _Bauteilart:
    """
    Wie eine Analyse zu ihrem Bauteil kommt: wo es im Aufbau steht, wie sein
    Paar je Richtung entsteht, wie die Richtung neben dem Titel heisst und was
    dasteht, wo es kein Paar gibt.
    """

    teile: Callable[["Aufbau"], Mapping[str, Any]]
    paar: Callable[..., Optional[Paar]]
    richtung_text: Callable[[Any], str]
    ohne_bewehrung: Callable[[Any], str]


#: Die Platte je Tragrichtung, der gezeichnete Querschnitt je Zugseite.
_BAUTEILARTEN = (
    _Bauteilart(
        teile=lambda aufbau: aufbau.querschnitte, paar=loeserpaar,
        richtung_text=lambda richtung: richtung.value,
        ohne_bewehrung=lambda richtung: (
            f"In {richtung.beschriftung} liegt keine Bewehrung – ohne sie gibt es "
            f"keinen Querschnitt zum Auswerten.")),
    _Bauteilart(
        teile=lambda aufbau: aufbau.querschnittsanalysen, paar=schnittpaar,
        richtung_text=lambda seite: seite.beschriftung,
        ohne_bewehrung=lambda seite: (
            "Der Querschnitt hat keine Bewehrung – ohne sie gibt es nichts zum Auswerten.")),
)


def analysen(aufbau: "Aufbau", loesung: "Loesung",
             protokoll: Optional[Protokoll] = None) -> Dict[str, List[Analyse]]:
    """
    Die Auswertungen am Querschnitt, je Platte und je gezeichnetem Querschnitt.

    Kein Nachweis: hier steht kein Erfuellungsgrad und kein Urteil, sondern
    eine Antwort auf die Frage, was im Querschnitt geschieht. Gerechnet wird
    trotzdem mit demselben Faserintegral und denselben Werkstoffgesetzen wie
    in den Nachweisen -- ein zweites Modell daneben waere eine zweite
    Wahrheit ueber denselben Querschnitt.

    Mit ``protokoll`` schreibt jede Linie dorthin, wie sie entstand -- daraus
    sammelt die Formelsammlung ihr Thema. Eine Schleife fuer beide
    Bauteilarten (:data:`_BAUTEILARTEN`); bis 2026-10-17 stand die des
    gezeichneten Querschnitts ein zweites Mal in dessen Modul, geladen mit
    einem Import in dieser Funktion.
    """
    p = protokoll if protokoll is not None else StillesProtokoll()

    def wert(kid: str) -> float:
        return loesung.werte[kid].groesse.si

    ergebnis: Dict[str, List[Analyse]] = {}
    for art in _BAUTEILARTEN:
        teile = art.teile(aufbau)
        for kennung, faelle in aufbau.spannungsfaelle.items():
            teil = teile.get(kennung)
            if teil is None:
                continue
            paare: Dict[tuple, Optional[Paar]] = {}
            liste: List[Analyse] = []
            for fall in faelle:
                schluessel = (fall.richtung, fall.wahl)
                if schluessel not in paare:
                    try:
                        paare[schluessel] = art.paar(teil, fall.richtung, wert, fall.wahl)
                    except KeyError:
                        # Ein Wert wurde nicht gerechnet -- etwa in einer
                        # Richtung ohne Bewehrung. Dann gibt es nichts auszuwerten.
                        paare[schluessel] = None
                paar = paare[schluessel]
                analyse = Analyse(fall=fall, art=fall.art, richtung=fall.richtung,
                                  richtung_text=art.richtung_text(fall.richtung), paar=paar)
                if paar is None:
                    analyse.hinweis = art.ohne_bewehrung(fall.richtung)
                else:
                    analyse.bild, analyse.kurve = auswerten(fall, analyse.art, paar)
                    kurve = analyse.kurve
                    if kurve is not None:
                        modul = kurve if isinstance(kurve, Modullinie) else None
                        herleitung(p, fall, paar, kurve.linie if modul else kurve,
                                   loesung.werte, teil.id, modul=modul)
                liste.append(analyse)
            ergebnis[kennung] = liste
    return ergebnis
