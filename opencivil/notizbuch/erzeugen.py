"""
opencivil/notizbuch/erzeugen.py -- alle Seiten, die aus dem Code entstehen.

VERANTWORTUNG:
Fuehrt Formelsammlung und Python-Doku zusammen: die Formelseiten verlinken
die Stelle im Code auf die Seite ihres Moduls, und die Modulseiten nennen die
Formeln, die das Modul schreibt. Die Bruecke schreibt, was hier herauskommt
(:func:`opencivil.web.bruecke.notizbuch_schreiben`).

Ein eigenes Modul, weil beide Seiten voneinander wissen muessen -- und weil
``opencivil.notizbuch`` beim Import nichts laden darf: die Formelsammlung
braucht daraus die Namensregel.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from opencivil.notizbuch import formelseiten
from opencivil.notizbuch.bibliothek import Bibliothek
from opencivil.notizbuch.tresor import Seite


def seiten() -> List[Seite]:
    """Formel-, Themen- und Uebersichtsseiten, dazu je Modul und Paket eine."""
    bibliothek = Bibliothek.lesen()
    formeln, themen = formelseiten.sammeln()
    je_modul: Dict[str, List[Tuple[str, str]]] = {}
    for formel in formeln.values():
        for stelle in formel.codestellen:
            modul, _, wo = stelle.partition(":")
            je_modul.setdefault(modul, []).append((formel.name, wo))
    return [*formelseiten.seiten(formeln, themen, bibliothek.codestelle),
            *bibliothek.seiten(je_modul)]
