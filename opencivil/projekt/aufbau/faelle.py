"""
opencivil/projekt/aufbau/faelle.py -- was Balkensystem und Decke an Faellen gleich pruefen.

VERANTWORTUNG:
Die Regeln der Lastfaelle und Kombinationen eines Bauteils, an einer
Stelle: verschiedene Namen, hoechstens ein Lastfall mit dem Eigengewicht,
je Teil eine Kennung, eine Last ohne Lastfall bleibt weg, und die Beiwerte
einer Kombination nach den Namen ihrer Lastfaelle. Was nicht stimmt, steht
in den Meldungen des Bauteils -- ein Fehler haelt das Bauteil auf, der Rest
des Projekts rechnet weiter (bis 2026-10-15 hielten gleiche Fallnamen das
ganze Projekt auf).
"""

from __future__ import annotations

from typing import Any, Dict, List, Sequence, Tuple

from opencivil.projekt.faelle import LastfallEintrag, LastkombinationEintrag
from opencivil.stabwerk.system import Meldung


def doppelte_kennungen(was: str, liste: Sequence[Any]) -> List[Meldung]:
    """
    Je Kennung, die mehrere Teile tragen, ein Fehler: an ihr haengen Lasten
    und Verweise. Bis 2026-10-16 fiel eine Last bei zwei gleichen
    Lastfall-Kennungen still in beide.
    """
    kennungen = [e.kennung for e in liste]
    return [Meldung(f"Mehrere {was} haben die Kennung «{k}» – sie wären nicht zu "
                    f"unterscheiden. Gerechnet wird erst mit verschiedenen.", (k,))
            for k in sorted({k for k in kennungen if kennungen.count(k) > 1})]


def faelle_pruefen(lastfaelle: Sequence[LastfallEintrag],
                   kombinationen: Sequence[LastkombinationEintrag]) -> List[Meldung]:
    """
    Die Faelle werden an ihrem Namen erkannt, zwei gleiche waeren nicht zu
    unterscheiden -- auch nicht ein Lastfall und eine Kombination. Und das
    Eigengewicht gehoert in einen Lastfall, nicht in zwei.
    """
    heraus: List[Meldung] = []
    namen_lf = [lf.name for lf in lastfaelle]
    namen_k = [k.name for k in kombinationen]
    for was, namen in (("Lastfälle", namen_lf), ("Kombinationen", namen_k)):
        for name in sorted({n for n in namen if namen.count(n) > 1}):
            heraus.append(Meldung(f"Mehrere {was} heissen «{name}» – sie wären nicht zu "
                                  f"unterscheiden. Gerechnet wird erst mit verschiedenen Namen."))
    for name in sorted(set(namen_lf) & set(namen_k)):
        heraus.append(Meldung(f"«{name}» heisst ein Lastfall und eine Kombination – die beiden wären "
                              f"nicht zu unterscheiden. Gerechnet wird erst mit verschiedenen Namen."))
    eigen = [lf for lf in lastfaelle if lf.eigengewicht]
    if len(eigen) > 1:
        heraus.append(Meldung(f"Das Eigengewicht bekommen {', '.join(f'«{lf.name}»' for lf in eigen)} – "
                              f"es gehört in einen Lastfall.", tuple(lf.kennung for lf in eigen)))
    return heraus


def ohne_lastfall(kennung: str) -> Meldung:
    """Der Hinweis zu einer Last, deren Lastfall es nicht gibt: sie bleibt weg, der Rest rechnet."""
    return Meldung(f"{kennung}: die Last gehört zu keinem Lastfall – sie wird nicht gerechnet.",
                   (kennung,), fehler=False)


def beiwerte(kombinationen: Sequence[LastkombinationEintrag], lastfaelle: Sequence[LastfallEintrag]
             ) -> Tuple[List[Tuple[str, Dict[str, float]]], List[Meldung]]:
    """
    Je Kombination ihr Name und ihre Beiwerte nach dem Namen des Lastfalls.
    Ein Beiwert fuer einen Lastfall, den es nicht gibt, zaehlt nicht; ein
    Hinweis sagt es.
    """
    name_von = {lf.kennung: lf.name for lf in lastfaelle}
    heraus: List[Tuple[str, Dict[str, float]]] = []
    meldungen: List[Meldung] = []
    for k in kombinationen:
        fremd = [lf for lf in k.faktoren if lf not in name_von]
        if fremd:
            meldungen.append(Meldung(f"Kombination «{k.name}»: einen Lastfall «{fremd[0]}» gibt es nicht – "
                                     f"sein Beiwert zählt nicht.", fehler=False))
        heraus.append((k.name, {name_von[lf]: beiwert for lf, beiwert in k.faktoren.items()
                                if lf in name_von}))
    return heraus, meldungen
