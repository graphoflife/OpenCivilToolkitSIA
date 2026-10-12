---
erzeugt: ec4a4b898ee3
art: modul
tags: [modul]
---
> [!abstract] opencivil/web/speicher.py
> was vom letzten Lauf noch gilt.
> Paket [[opencivil.web]] · [Quelltext](../../opencivil/web/speicher.py)

## VERANTWORTUNG

Behaelt die Ergebnisse je Bauteil ueber Anfragen hinweg und gibt sie zurueck,
solange die Eingaben dieses Bauteils unveraendert sind. Wer eine Zahl an
Platte 2 aendert, soll nicht Platte 1 mitrechnen.


## WARUM DAS NICHT DAS RECHENWERK MACHT

Innerhalb eines Laufs ist es schon sparsam -- es rechnet nur, was die Ziele
brauchen, und jeden Wert einmal. Was ihm fehlt, ist das Gedaechtnis *zwischen*
zwei Laeufen, und das kann es sich nicht selbst geben: es sieht nur einen
fertigen Graphen und weiss nicht, welche Eingabe der Benutzer angefasst hat.
Das weiss nur, wer die Beschreibung entgegennimmt.


## WORAN DIE GUELTIGKEIT HAENGT -- UND WARUM SO GROB

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


## WAS AUFBEWAHRT WIRD

Nicht nur die Zahlen. Die Nachweise merken sich beim Rechnen einiges, was die
Schnittstelle spaeter ausliest -- Interaktionslinien, Fallergebnisse,
Iterationsschritte. Ein uebernommenes Bauteil bringt deshalb seine
*Nachweisobjekte* mit; sonst staende die Zusammenfassung da und das Diagramm
waere leer.

## Inhalt

### abdruck

```python
def abdruck(projekt_dict: Mapping[str, Any], kennung: str, bezuege: Sequence[str]=()) -> str
```

Der Fingerabdruck eines Bauteils: woran sich entscheidet, ob es noch gilt.

Enthalten ist sein ganzer Eintrag und *alle* Materialien. Nicht nur die
verwendeten: welches Material eine Lage benutzt, steht in derselben
Beschreibung, und ein Vergleich, der erst herausfinden muss, welche
Kennung wohin zeigt, waere genau die Stelle, an der man eines vergisst.
Materialien sind ein paar Zeilen JSON; sie mitzuzaehlen kostet nichts.

Dazu die Eintraege der Bauteile, deren Werte es liest (`bezuege`,
[[opencivil.projekt.aufbau#Bauteilkopf|Bauteilkopf.bezuege]]): ein Balkensystem rechnet mit der Dicke
einer Platte, also gilt es nicht mehr, wenn sie sich aendert.

### Teilergebnis

```python
@dataclass
class Teilergebnis
```

Was ein Bauteil beigetragen hat -- vollstaendig genug zum Wiederholen.

- `werte: Dict[str, Wert] = field(default_factory=dict)`
- `bloecke: List[Block] = field(default_factory=list)`
- `reihenfolge: List[str] = field(default_factory=list)`
- `graph: Dict[str, Any] = field(default_factory=dict)`
- `urteile: List[Any] = field(default_factory=list)`
- `nicht_berechenbar: Dict[str, Any] = field(default_factory=dict)`
- `fehlende: List[Any] = field(default_factory=list)`
- `teile: Dict[str, Dict[str, Any]] = field(default_factory=dict)` – Die Nachweisobjekte, nach Feld von [[opencivil.web.speicher#Teilergebnis|Aufbau]] geordnet.

### als_teil

```python
def als_teil(loesung: Loesung, teile: Mapping[str, Dict[str, Any]], *, ohne: Mapping[str, Wert]) -> Teilergebnis
```

Aus einem Lauf das herausloesen, was dieses Bauteil beigetragen hat.

`ohne` sind die Werte, die schon vorher bekannt waren -- die Baustoffe
etwa. Sie gehoeren zum Lauf, aber nicht zu diesem Bauteil, und beim
naechsten Mal bringt sie wieder jemand anderes mit.

### verschmelzen

```python
def verschmelzen(ziel: Loesung, teil: Teilergebnis) -> None
```

Ein Teilergebnis in die Gesamtloesung einhaengen, in dieser Reihenfolge.

### Ergebnisspeicher

```python
class Ergebnisspeicher
```

Das Gedaechtnis zwischen zwei Anfragen.

Ein Eintrag je Platte, geschluesselt nach Kennung und nur gueltig, solange
der Abdruck stimmt. Der Speicher liegt im Modul und damit im Prozess: beim
Server ist das die laufende Sitzung, im Browser der offene Reiter. Eine
Ablage auf der Platte waere ein zweiter Ort fuer dieselbe Wahrheit.

#### Ergebnisspeicher.hole

```python
def hole(self, kennung: str, stempel: str) -> Optional[Teilergebnis]
```

#### Ergebnisspeicher.merken

```python
def merken(self, kennung: str, stempel: str, teil: Teilergebnis) -> None
```

#### Ergebnisspeicher.aufraeumen

```python
def aufraeumen(self, kennungen) -> None
```

Eintraege zu geloeschten Platten wegwerfen.

#### Ergebnisspeicher.leeren

```python
def leeren(self) -> None
```

#### Ergebnisspeicher.belegt

```python
@property
def belegt(self) -> int
```


## Konstanten

- `PLAETZE = 32` – Wie viele Bauteile hoechstens aufbewahrt werden. Ein Projekt mit mehr Platten als das laeuft nicht langsamer als ohne Speicher -- es gewinnt nur nichts mehr. Die Grenze ist gegen ein Gedaechtnis, das nie kleiner wird.

## Braucht

- [[opencivil.core.protokoll]]
- [[opencivil.core.rechenwerk]]
- [[opencivil.core.wert]]
- [[opencivil.projekt]]

## Gebraucht von

- [[opencivil.web.dienst]]
