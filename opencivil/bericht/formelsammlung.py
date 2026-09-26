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
Das Rechenwerk stempelt beides auf jeden Block, den eine Berechnung schreibt
(:meth:`Protokoll.herkunft_stempeln`). Der Raum sagt, bei welchem Bestandteil
eine Formel vorkam -- danach grenzt die Oberflaeche «Aktuelle Seite» ein.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from opencivil.core.protokoll import GleichungBlock, Protokoll, TextBlock


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

#: Ein Name im Index: ``\alpha_{eff,x,\text{Feld}}``, ``f_{cd,\text{C30/37}}``.
#: Die Sammlung meint die Formel, nicht den Fall und nicht die Sorte.
_NAME_IM_INDEX = re.compile(r",\\text\{[^{}]*\}")


def _symbolisch(block: GleichungBlock) -> Optional[Tuple[str, Tuple[str, ...]]]:
    """Die Formel ohne Zahlen und ihr Schluessel -- ``None``, wo es keine gibt."""
    if block.ansatz:
        return block.latex, ("ansatz", block.latex)
    zeile = block.formelzeile
    if zeile is None or zeile.vorlage is None or zeile.analytisch is None:
        return None
    symbol = _FALLWERTE.sub("", zeile.symbol)
    latex = " ".join(filter(None, [f"{symbol} = {zeile.analytisch}", zeile.einheiten]))
    grund = _GRUNDZEICHEN.match(zeile.symbol).group(0)
    return (_NAME_IM_INDEX.sub("", latex),
            ("formel", grund, zeile.vorlage.removeprefix("-")))


def _merken(eintraege: List[Eintrag], nach_schluessel: Dict[tuple, Eintrag],
            schluessel: tuple, block, raum: str) -> None:
    eintrag = nach_schluessel.get(schluessel)
    if eintrag is None:
        eintrag = nach_schluessel[schluessel] = Eintrag(block)
        eintraege.append(eintrag)
    if raum and raum not in eintrag.raeume:
        eintrag.raeume.append(raum)


def formelsammlung(protokoll: Protokoll) -> List[Thema]:
    """Je Thema, in der Folge ihres ersten Auftretens, Erklaerungen und Formeln."""
    themen: Dict[str, Thema] = {}
    gesehen: Dict[tuple, Eintrag] = {}
    for block in protokoll.alle_bloecke():
        if not isinstance(block, (GleichungBlock, TextBlock)) or not block.thema:
            continue
        thema = themen.setdefault(block.thema, Thema(block.thema))
        if isinstance(block, TextBlock):
            if block.erklaerung:
                _merken(thema.erklaerungen, gesehen, ("text", block.text),
                        TextBlock(text=block.text), block.raum)
            continue
        gefunden = _symbolisch(block)
        if gefunden is None:
            continue
        latex, schluessel = gefunden
        _merken(thema.formeln, gesehen, schluessel,
                GleichungBlock(latex=latex, titel=_titel(block.titel),
                               referenz=block.referenz),
                block.raum)
    return [t for t in themen.values() if t.formeln or t.erklaerungen]


def als_protokoll(themen: List[Thema]) -> Protokoll:
    """Fuer den Bericht: je Thema ein Titel, die Erklaerungen, dann die Formeln."""
    p = Protokoll()
    for thema in themen:
        p.titel(thema.name)
        p.anfuegen(*(e.block for e in thema.erklaerungen),
                   *(e.block for e in thema.formeln))
    return p
