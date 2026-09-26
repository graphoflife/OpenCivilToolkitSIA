"""
opencivil/bericht/formelsammlung.py -- jede Formel des Laufs einmal, ohne Zahlen.

VERANTWORTUNG:
Sammelt aus der Herleitung je Thema -- «Beton», «Querkraft», «Knicken» --
die Formeln in ihrer symbolischen Fassung, ``Symbol = Formel``, mit Titel
und Normstelle, und die Erklaerungen dazu. Die Herleitung zeigt Formeln mit
Zahlen und laesst die Erklaerungen weg; hier ist es umgekehrt: keine Zahlen,
dafuer das Warum.

JEDE FORMEL EINMAL:
Dieselbe Formel steht in der Herleitung oft mehrfach -- je Lage, je Fall, je
Platte, mit anderen Indizes an den Symbolen, fuer das negative Moment mit
Minus davor. Erkannt wird sie an ihrer Vorlage (``@name``-Form, siehe
:attr:`Formelzeile.vorlage`, ohne fuehrendes Minus) und dem Grundzeichen ihres
Ergebnisses; gezeigt wird die erste Fassung. Ein Ansatz ohne Zahlen
(:meth:`Protokoll.ansatz`) ist schon symbolisch und zaehlt mit seinem LaTeX.

Einmal im ganzen Lauf, nicht je Thema: gemeinsame Bausteine -- die statische
Hoehe, der Querschnittsloeser, die Zugfestigkeit -- stehen beim ersten Thema,
das sie braucht, und nicht bei jedem noch einmal.

WOHER THEMA UND RAUM KOMMEN:
Das Thema stempelt das Rechenwerk auf jeden Block, den eine Berechnung
schreibt (:meth:`Protokoll.herkunft_stempeln`). Der Raum ist der des
Abschnitts, in dem der Block steht -- gelesen am Abschnittstitel, wie in
:meth:`Protokoll.nach_abschnitten`. Er sagt, bei welchem Bestandteil eine
Formel vorkam; danach grenzt die Oberflaeche «Aktuelle Seite» ein.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from opencivil.core.latex import ohne_namen_im_index
from opencivil.core.protokoll import GleichungBlock, Protokoll, TextBlock, TitelBlock


@dataclass
class Eintrag:
    """Eine Formel oder eine Erklaerung -- mit den Raeumen, in denen sie vorkam."""

    block: GleichungBlock | TextBlock
    raeume: List[str] = field(default_factory=list)


@dataclass
class Thema:
    name: str
    erklaerungen: List[Eintrag] = field(default_factory=list)
    formeln: List[Eintrag] = field(default_factory=list)

    @property
    def eintraege(self) -> List[Eintrag]:
        """Wie das Thema dasteht, im Bericht und am Bildschirm: erst das Warum."""
        return self.erklaerungen + self.formeln


#: Eine Zahlenangabe in einem Titel: ``= -300.0 kN``. Die Herleitung nennt
#: damit den Fall, die Sammlung zeigt die Formel ohne ihn. Nur mit
#: Nachkommastelle -- ``bei M_Ed = 0`` ist eine Bedingung und bleibt.
_ZAHLENANGABE = re.compile(r"\s*=\s*-?\d[\d,]*\.\d+(?:\s*[^\s–,;)]+)?")


def _titel(titel: str) -> str:
    """«Widerstand bei festgehaltenem N_Ed = -300.0 kN» ohne die Zahl."""
    return _ZAHLENANGABE.sub("", titel)


#: Das Grundzeichen eines Ergebnisses: ``\sigma_{s,adm,2,x}`` -> ``\sigma``.
#: Ohne Index, denn der traegt Lage und Richtung; mit Zeichen, denn zwei
#: Formeln mit derselben kurzen Vorlage (``@z``) und verschiedenen Ergebnissen
#: sind verschiedene Formeln.
_GRUNDZEICHEN = re.compile(r"^[^_^({]*")


#: Fallwerte im Ergebnissymbol: ``V_{Rd,x}(M_{Ed} = 150\,\mathrm{kNm}, ...)``.
#: Erkannt an der Einheit -- eine Bedingung wie ``(N_{Ed}=0)`` bleibt.
_FALLWERTE = re.compile(r"\([^()]*\\mathrm\{[^()]*\)")


def _schluessel(block: GleichungBlock) -> Optional[tuple]:
    """Woran dieselbe Formel wiederzuerkennen ist -- ``None``: es gibt keine Symbolfassung."""
    if block.ansatz:
        return ("ansatz", block.latex)
    zeile = block.formelzeile
    if zeile is None or zeile.vorlage is None:
        return None
    return ("formel", _GRUNDZEICHEN.match(zeile.symbol).group(0),
            zeile.vorlage.removeprefix("-"))


def _symbolisch(block: GleichungBlock) -> GleichungBlock:
    """
    Die Formel ohne Zahlen, ``Symbol = Formel``. Gebaut erst fuer einen neuen
    Schluessel -- neun von zehn Gleichungen sind Wiederholungen.
    """
    latex = block.latex
    if not block.ansatz:
        zeile = block.formelzeile
        symbol = _FALLWERTE.sub("", zeile.symbol)
        # Die Sammlung meint die Formel, nicht den Fall und nicht die Sorte.
        latex = ohne_namen_im_index(" ".join(filter(None, [
            f"{symbol} = {zeile.analytisch}", zeile.einheiten])))
    return GleichungBlock(latex=latex, titel=_titel(block.titel), referenz=block.referenz)


def _merken(eintraege: List[Eintrag], nach_schluessel: Dict[tuple, Eintrag],
            schluessel: tuple, neu: Callable[[], GleichungBlock | TextBlock],
            raum: str) -> None:
    eintrag = nach_schluessel.get(schluessel)
    if eintrag is None:
        eintrag = nach_schluessel[schluessel] = Eintrag(neu())
        eintraege.append(eintrag)
    if raum and raum not in eintrag.raeume:
        eintrag.raeume.append(raum)


def formelsammlung(protokoll: Protokoll) -> List[Thema]:
    """Je Thema, in der Folge ihres ersten Auftretens, Erklaerungen und Formeln."""
    themen: Dict[str, Thema] = {}
    gesehen: Dict[tuple, Eintrag] = {}
    raum = ""
    for block in protokoll.alle_bloecke():
        if isinstance(block, TitelBlock) and block.raum:
            raum = block.raum
        if not isinstance(block, (GleichungBlock, TextBlock)) or not block.thema:
            continue
        thema = themen.setdefault(block.thema, Thema(block.thema))
        if isinstance(block, TextBlock):
            if block.erklaerung:
                _merken(thema.erklaerungen, gesehen, ("text", block.text),
                        lambda: TextBlock(text=block.text), raum)
            continue
        schluessel = _schluessel(block)
        if schluessel is not None:
            _merken(thema.formeln, gesehen, schluessel, lambda: _symbolisch(block), raum)
    return [t for t in themen.values() if t.eintraege]


def anfuegen(p: Protokoll, themen: List[Thema]) -> None:
    """Fuer den Bericht: je Thema ein Titel, die Erklaerungen, dann die Formeln."""
    for thema in themen:
        p.titel(thema.name)
        p.anfuegen(*(e.block for e in thema.eintraege))
