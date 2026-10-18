"""
opencivil/web/speicher.py -- was vom letzten Lauf noch gilt.

VERANTWORTUNG:
Behaelt je Bauteil die Loesung seines Laufs ueber Anfragen hinweg und gibt
sie zurueck, solange die Eingaben dieses Bauteils unveraendert sind. Wer eine
Zahl an Platte 2 aendert, soll nicht Platte 1 mitrechnen.

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
Die ganze :class:`~opencivil.core.rechenwerk.Loesung` des Bauteils: Werte,
Herleitung, Urteile und die Befunde -- Interaktionslinien, Fallergebnisse,
das Ergebnis eines Balkensystems. Die Bilder lesen dort, nicht an den
Rechenobjekten; die eines frischen Aufbaus taugen darum so gut wie die von
damals.

Daneben, in einem zweiten Speicher derselben Art, die Zeichendaten seiner
Spannung-Dehnung-Analysen, unter demselben Abdruck: sie lesen nur seinen
Eintrag, die Materialien und die Werte, die daraus folgen. Bis 2026-10-18
rechnete jede Rechnung alle Analysen neu, auch die unveraenderter Bauteile --
am Pruefprojekt «jeder Nachweis» zwei Drittel jeder Rechnung.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Generic, Mapping, Optional, Sequence, Tuple, TypeVar

from opencivil.projekt import BAUTEILE

#: Was ein Speicher je Bauteil aufbewahrt -- eine Loesung oder Zeichendaten.
T = TypeVar("T")

#: Wie viele Bauteile hoechstens aufbewahrt werden. Ein Projekt mit mehr
#: Platten als das laeuft nicht langsamer als ohne Speicher -- es gewinnt nur
#: nichts mehr. Die Grenze ist gegen ein Gedaechtnis, das nie kleiner wird.
PLAETZE = 32


def abdruck(projekt_dict: Mapping[str, Any], kennung: str,
            bezuege: Sequence[str] = ()) -> str:
    """
    Der Fingerabdruck eines Bauteils: woran sich entscheidet, ob es noch gilt.

    Enthalten ist sein ganzer Eintrag und *alle* Materialien. Nicht nur die
    verwendeten: welches Material eine Lage benutzt, steht in derselben
    Beschreibung, und ein Vergleich, der erst herausfinden muss, welche
    Kennung wohin zeigt, waere genau die Stelle, an der man eines vergisst.
    Materialien sind ein paar Zeilen JSON; sie mitzuzaehlen kostet nichts.

    Dazu die Eintraege der Bauteile, deren Werte es liest (``bezuege``,
    :attr:`~opencivil.projekt.aufbau.Bauteil.bezuege`): ein Balkensystem
    rechnet mit der Dicke einer Platte, also gilt es nicht mehr, wenn sie
    sich aendert.
    """
    eintraege = {e.get("kennung"): e for art in BAUTEILE
                 for e in (projekt_dict.get(art.liste) or [])}
    return json.dumps(
        {"querschnitt": eintraege.get(kennung), "materialien": projekt_dict.get("materialien"),
         "bezuege": [eintraege.get(b) for b in bezuege]},
        sort_keys=True, ensure_ascii=False, default=str)


class Ergebnisspeicher(Generic[T]):
    """
    Das Gedaechtnis zwischen zwei Anfragen.

    Ein Eintrag je Bauteil, geschluesselt nach Kennung und nur gueltig,
    solange der Abdruck stimmt. Was darin liegt, sagt, wer ihn anlegt: die
    Loesung eines Laufs, der die Baustoffe mitgebracht bekam -- sie enthaelt
    nur, was das Bauteil selbst gerechnet hat --, oder die Zeichendaten
    seiner Analysen. Der Speicher liegt im Modul und damit im Prozess: beim
    Server ist das die laufende Sitzung, im Browser der offene Reiter. Eine
    Ablage auf der Platte waere ein zweiter Ort fuer dieselbe Wahrheit.
    """

    def __init__(self, plaetze: int = PLAETZE) -> None:
        self._eintraege: Dict[str, Tuple[str, T]] = {}
        self._plaetze = plaetze
        self.treffer = 0
        self.fehlgriffe = 0

    def hole(self, kennung: str, stempel: str) -> Optional[T]:
        eintrag = self._eintraege.get(kennung)
        if eintrag is None or eintrag[0] != stempel:
            self.fehlgriffe += 1
            return None
        self.treffer += 1
        return eintrag[1]

    def merken(self, kennung: str, stempel: str, teil: T) -> None:
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
