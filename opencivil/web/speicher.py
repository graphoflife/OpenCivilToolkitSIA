"""
opencivil/web/speicher.py -- was vom letzten Lauf noch gilt.

VERANTWORTUNG:
Behaelt die Ergebnisse je Bauteil ueber Anfragen hinweg und gibt sie zurueck,
solange die Eingaben dieses Bauteils unveraendert sind. Wer eine Zahl an
Platte 2 aendert, soll nicht Platte 1 mitrechnen.

WARUM DAS NICHT DAS RECHENWERK MACHT:
Innerhalb eines Laufs ist es schon sparsam -- es rechnet nur, was die Ziele
brauchen, und jeden Wert einmal. Was ihm fehlt, ist das Gedaechtnis *zwischen*
zwei Laeufen, und das kann es sich nicht selbst geben: es sieht nur einen
fertigen Graphen und weiss nicht, welche Eingabe der Benutzer angefasst hat.
Das weiss nur, wer die Beschreibung entgegennimmt.

WORAN DIE GUELTIGKEIT HAENGT -- UND WARUM SO GROB:
Am **Abdruck** eines Bauteils: der JSON-Teil, aus dem es gebaut wird, plus die
Materialien, die es verwendet. Nicht feiner. Es waere verlockend, je Nachweis
zu pruefen und beim Aendern einer Einwirkung den Duktilitaetsnachweis stehen
zu lassen -- aber die Nachweise tragen ihre Lastfaelle im Bauch, nicht in
ihren Bezuegen. Ein Knickfall mit geaenderter Normalkraft haette denselben
Bezugsgraphen und dieselben Ausgabekennungen wie vorher; ein feiner Abdruck
saehe keinen Unterschied und gaebe ein falsches Ergebnis heraus, ohne dass
irgendwo etwas auffiele.

Die Regel ist deshalb: **lieber zu viel verwerfen als zu wenig.** Ein Abdruck,
der eine Aenderung uebersieht, liefert falsche Zahlen. Einer, der zu oft
verwirft, kostet Zeit. Von beiden Fehlern ist nur einer hinnehmbar.

WAS AUFBEWAHRT WIRD:
Nicht nur die Zahlen. Die Nachweise merken sich beim Rechnen einiges, was die
Schnittstelle spaeter ausliest -- Interaktionslinien, Fallergebnisse,
Iterationsschritte. Ein uebernommenes Bauteil bringt deshalb seine
*Nachweisobjekte* mit; sonst staende die Zusammenfassung da und das Diagramm
waere leer.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Tuple

from opencivil.core.protokoll import Block
from opencivil.core.rechenwerk import Loesung
from opencivil.core.wert import Wert

#: Wie viele Bauteile hoechstens aufbewahrt werden. Ein Projekt mit mehr
#: Platten als das laeuft nicht langsamer als ohne Speicher -- es gewinnt nur
#: nichts mehr. Die Grenze ist gegen ein Gedaechtnis, das nie kleiner wird.
PLAETZE = 32


def abdruck(projekt_dict: Mapping[str, Any], kennung: str) -> str:
    """
    Der Fingerabdruck einer Platte: woran sich entscheidet, ob sie noch gilt.

    Enthalten ist ihr ganzer Eintrag und *alle* Materialien. Nicht nur die
    verwendeten: welches Material eine Lage benutzt, steht in derselben
    Beschreibung, und ein Vergleich, der erst herausfinden muss, welche
    Kennung wohin zeigt, waere genau die Stelle, an der man eines vergisst.
    Materialien sind ein paar Zeilen JSON; sie mitzuzaehlen kostet nichts.
    """
    eintrag = next((q for q in projekt_dict.get("querschnitte") or []
                    if q.get("kennung") == kennung), None)
    return json.dumps(
        {"querschnitt": eintrag, "materialien": projekt_dict.get("materialien")},
        sort_keys=True, ensure_ascii=False, default=str)


@dataclass
class Teilergebnis:
    """Was ein Bauteil beigetragen hat -- vollstaendig genug zum Wiederholen."""

    werte: Dict[str, Wert] = field(default_factory=dict)
    bloecke: List[Block] = field(default_factory=list)
    reihenfolge: List[str] = field(default_factory=list)
    graph: Dict[str, Any] = field(default_factory=dict)
    urteile: List[Any] = field(default_factory=list)
    nicht_berechenbar: Dict[str, Any] = field(default_factory=dict)
    fehlende: List[Any] = field(default_factory=list)
    teile: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    """Die Nachweisobjekte, nach Feld von :class:`Aufbau` geordnet."""


def als_teil(loesung: Loesung, teile: Mapping[str, Dict[str, Any]],
             *, ohne: Mapping[str, Wert]) -> Teilergebnis:
    """
    Aus einem Lauf das herausloesen, was dieses Bauteil beigetragen hat.

    ``ohne`` sind die Werte, die schon vorher bekannt waren -- die Baustoffe
    etwa. Sie gehoeren zum Lauf, aber nicht zu diesem Bauteil, und beim
    naechsten Mal bringt sie wieder jemand anderes mit.
    """
    return Teilergebnis(
        werte={k: v for k, v in loesung.werte.items() if k not in ohne},
        bloecke=list(loesung.protokoll.bloecke),
        reihenfolge=list(loesung.reihenfolge),
        graph=dict(loesung.graph),
        urteile=list(loesung.urteile),
        nicht_berechenbar=dict(loesung.nicht_berechenbar),
        fehlende=list(loesung.fehlende),
        teile={feld: dict(eintraege) for feld, eintraege in teile.items()},
    )


def verschmelzen(ziel: Loesung, teil: Teilergebnis) -> None:
    """Ein Teilergebnis in die Gesamtloesung einhaengen, in dieser Reihenfolge."""
    ziel.werte.update(teil.werte)
    ziel.protokoll.bloecke.extend(teil.bloecke)
    ziel.reihenfolge.extend(r for r in teil.reihenfolge if r not in ziel.reihenfolge)
    ziel.graph.update(teil.graph)
    ziel.urteile.extend(teil.urteile)
    ziel.nicht_berechenbar.update(teil.nicht_berechenbar)
    ziel.fehlende.extend(teil.fehlende)


class Ergebnisspeicher:
    """
    Das Gedaechtnis zwischen zwei Anfragen.

    Ein Eintrag je Platte, geschluesselt nach Kennung und nur gueltig, solange
    der Abdruck stimmt. Der Speicher liegt im Modul und damit im Prozess: beim
    Server ist das die laufende Sitzung, im Browser der offene Reiter. Eine
    Ablage auf der Platte waere ein zweiter Ort fuer dieselbe Wahrheit.
    """

    def __init__(self, plaetze: int = PLAETZE) -> None:
        self._eintraege: Dict[str, Tuple[str, Teilergebnis]] = {}
        self._plaetze = plaetze
        self.treffer = 0
        self.fehlgriffe = 0

    def hole(self, kennung: str, stempel: str) -> Optional[Teilergebnis]:
        eintrag = self._eintraege.get(kennung)
        if eintrag is None or eintrag[0] != stempel:
            self.fehlgriffe += 1
            return None
        self.treffer += 1
        return eintrag[1]

    def merken(self, kennung: str, stempel: str, teil: Teilergebnis) -> None:
        if kennung in self._eintraege:
            del self._eintraege[kennung]
        elif len(self._eintraege) >= self._plaetze:
            # Der aelteste geht. Ein Wörterbuch behaelt seine Reihenfolge,
            # also ist das der erste Schluessel.
            del self._eintraege[next(iter(self._eintraege))]
        self._eintraege[kennung] = (stempel, teil)

    def aufraeumen(self, kennungen) -> None:
        """Eintraege zu geloeschten Platten wegwerfen."""
        behalten = set(kennungen)
        for k in [k for k in self._eintraege if k not in behalten]:
            del self._eintraege[k]

    def leeren(self) -> None:
        self._eintraege.clear()
        self.treffer = self.fehlgriffe = 0

    @property
    def belegt(self) -> int:
        return len(self._eintraege)
