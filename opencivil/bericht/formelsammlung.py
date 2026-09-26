"""
opencivil/bericht/formelsammlung.py -- jede Formel einmal, ohne Zahlen.

VERANTWORTUNG:
Sammelt aus einer Herleitung je Thema -- «Beton», «Querkraft», «Knicken» --
die Formeln in ihrer symbolischen Fassung, ``Symbol = Formel``, mit Titel
und Normstelle, und die Erklaerungen dazu. Die Herleitung zeigt Formeln mit
Zahlen und laesst die Erklaerungen weg; hier ist es umgekehrt: keine Zahlen,
dafuer das Warum.

ZWEI SAMMLUNGEN:
* Die ganze, zum Nachschlagen (:func:`vollstaendig`): jede Formel des
  Werkzeugs, gleich welches Projekt offen ist und welche Nachweise darin
  laufen. Die Oberflaeche zeigt sie; vorab erzeugt von
  ``python3 -m opencivil.web.bruecke``.
* Die eines Laufs (:func:`formelsammlung`): im Bericht als «Verwendete
  Formeln» -- die Erklaerungen zu dem, was er rechnet, und nicht zu allem.

JEDE FORMEL EINMAL:
Dieselbe Formel steht in der Herleitung oft mehrfach -- je Lage, je Fall, je
Platte, mit anderen Indizes an den Symbolen, fuer das negative Moment mit
Minus davor. Erkannt wird sie an ihrer Vorlage (``@name``-Form, siehe
:attr:`Formelzeile.vorlage`, ohne fuehrendes Minus) und dem Grundzeichen ihres
Ergebnisses; gezeigt wird die erste Fassung. Ein Ansatz ohne Zahlen
(:meth:`Protokoll.ansatz`) ist schon symbolisch und zaehlt mit seinem LaTeX.
Und was gesetzt gleich aussieht, ist dieselbe Formel: Summe und Schwerpunkt
einer Lage schreiben Handrechnung und Lagennachweise mit anderen
Platzhalternamen.

Einmal im ganzen Lauf, nicht je Thema: gemeinsame Bausteine -- die statische
Hoehe, der Querschnittsloeser, die Zugfestigkeit -- stehen beim ersten Thema,
das sie braucht, und nicht bei jedem noch einmal.

WOHER DAS THEMA KOMMT:
Das Rechenwerk stempelt es auf jeden Block, den eine Berechnung schreibt
(:meth:`Protokoll.herkunft_stempeln`).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from opencivil.core.latex import ohne_namen_im_index
from opencivil.core.protokoll import GleichungBlock, Protokoll, TextBlock


@dataclass
class Thema:
    name: str
    erklaerungen: List[TextBlock] = field(default_factory=list)
    formeln: List[GleichungBlock] = field(default_factory=list)

    @property
    def bloecke(self) -> List[GleichungBlock | TextBlock]:
        """Wie das Thema dasteht, im Bericht und am Bildschirm: erst das Warum."""
        return [*self.erklaerungen, *self.formeln]


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


def _schluessel(block: GleichungBlock | TextBlock) -> Optional[tuple]:
    """Woran derselbe Eintrag wiederzuerkennen ist -- ``None``: er gehoert nicht hinein."""
    if isinstance(block, TextBlock):
        return ("text", block.text) if block.erklaerung else None
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


def formelsammlung(protokoll: Protokoll) -> List[Thema]:
    """Je Thema, in der Folge ihres ersten Auftretens, Erklaerungen und Formeln."""
    themen: Dict[str, Thema] = {}
    gesehen: Set[tuple] = set()
    gesetzt: Set[str] = set()
    for block in protokoll.alle_bloecke():
        if not isinstance(block, (GleichungBlock, TextBlock)) or not block.thema:
            continue
        thema = themen.setdefault(block.thema, Thema(block.thema))
        schluessel = _schluessel(block)
        if schluessel is None or schluessel in gesehen:
            continue
        gesehen.add(schluessel)
        if isinstance(block, TextBlock):
            thema.erklaerungen.append(TextBlock(text=block.text))
            continue
        formel = _symbolisch(block)
        if formel.latex not in gesetzt:
            gesetzt.add(formel.latex)
            thema.formeln.append(formel)
    return [t for t in themen.values() if t.bloecke]


def vollstaendig() -> List[Thema]:
    """
    Jede Formel des Werkzeugs, zum Nachschlagen -- gleich, welches Projekt
    offen ist und welche Nachweise darin laufen.

    Gesammelt aus :meth:`Projekt.beispiel` und :meth:`Projekt.jeder_nachweis`,
    die zusammen jeden Nachweis laut fuehren, mit allen Kennwerten der
    Baustoffe (``alle_ziele``: sonst fehlte etwa ε_yd). Im schnellen Aufbau:
    die Grenzkraftsuche beim Knicken schreibt keine eigene Formel, und ganz
    stille Nachweise schreiben nichts -- dieselbe Sammlung, Zeichen fuer
    Zeichen, in einem Zehntel der Zeit.
    """
    # Erst hier: das Paket projekt laedt beim Import den Bericht und damit
    # dieses Modul.
    from opencivil.projekt import Projekt

    protokoll = Protokoll()
    for projekt in (Projekt.beispiel(), Projekt.jeder_nachweis()):
        aufbau = projekt.aufbauen(schnell=True)
        protokoll.anfuegen(*aufbau.werk.loese(*aufbau.alle_ziele()).protokoll.bloecke)
    return formelsammlung(protokoll)


def anfuegen(p: Protokoll, themen: List[Thema]) -> None:
    """Fuer den Bericht: je Thema ein Titel, die Erklaerungen, dann die Formeln."""
    for thema in themen:
        p.titel(thema.name)
        p.anfuegen(*thema.bloecke)
