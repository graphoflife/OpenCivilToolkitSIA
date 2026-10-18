---
erzeugt: 83207a5c7c9a
art: modul
tags: [modul]
---
> [!abstract] opencivil/web/speicher.py
> was vom letzten Lauf noch gilt.
> Paket [[opencivil.web]] · [Quelltext](../../opencivil/web/speicher.py)

## VERANTWORTUNG

Behaelt je Bauteil die Loesung seines Laufs ueber Anfragen hinweg und gibt
sie zurueck, solange die Eingaben dieses Bauteils unveraendert sind. Wer eine
Zahl an Platte 2 aendert, soll nicht Platte 1 mitrechnen.


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

Die ganze [[opencivil.core.rechenwerk#Loesung|Loesung]] des Bauteils: Werte,
Herleitung, Urteile und die Befunde -- Interaktionslinien, Fallergebnisse,
das Ergebnis eines Balkensystems. Die Bilder lesen dort, nicht an den
Rechenobjekten; die eines frischen Aufbaus taugen darum so gut wie die von
damals.

Daneben, in einem zweiten Speicher derselben Art, die Zeichendaten seiner
Spannung-Dehnung-Analysen, unter demselben Abdruck: sie lesen nur seinen
Eintrag, die Materialien und die Werte, die daraus folgen. Bis 2026-10-18
rechnete jede Rechnung alle Analysen neu, auch die unveraenderter Bauteile --
am Pruefprojekt «jeder Nachweis» zwei Drittel jeder Rechnung.

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
[[opencivil.projekt.aufbau.kern#Bauteil|bezuege]]): ein Balkensystem
rechnet mit der Dicke einer Platte, also gilt es nicht mehr, wenn sie
sich aendert.

### Ergebnisspeicher

```python
class Ergebnisspeicher(Generic[T])
```

Das Gedaechtnis zwischen zwei Anfragen.

Ein Eintrag je Bauteil, geschluesselt nach Kennung und nur gueltig,
solange der Abdruck stimmt. Was darin liegt, sagt, wer ihn anlegt: die
Loesung eines Laufs, der die Baustoffe mitgebracht bekam -- sie enthaelt
nur, was das Bauteil selbst gerechnet hat --, oder die Zeichendaten
seiner Analysen. Der Speicher liegt im Modul und damit im Prozess: beim
Server ist das die laufende Sitzung, im Browser der offene Reiter. Eine
Ablage auf der Platte waere ein zweiter Ort fuer dieselbe Wahrheit.

#### Ergebnisspeicher.hole

```python
def hole(self, kennung: str, stempel: str) -> Optional[T]
```

#### Ergebnisspeicher.merken

```python
def merken(self, kennung: str, stempel: str, teil: T) -> None
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

- `T = TypeVar('T')` – Was ein Speicher je Bauteil aufbewahrt -- eine Loesung oder Zeichendaten.
- `PLAETZE = 32` – Wie viele Bauteile hoechstens aufbewahrt werden. Ein Projekt mit mehr Platten als das laeuft nicht langsamer als ohne Speicher -- es gewinnt nur nichts mehr. Die Grenze ist gegen ein Gedaechtnis, das nie kleiner wird.

## Braucht

- [[opencivil.projekt]]

## Gebraucht von

- [[opencivil.web.dienst]]
