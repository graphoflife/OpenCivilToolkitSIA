---
erzeugt: 90df82ef6c85
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/lesen.py
> was in einer Projektdatei stehen darf, und wie es gelesen wird.
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/lesen.py)

## VERANTWORTUNG

Die Leser, mit denen die `aus_dict` der Eintraege eine Datei aufnehmen:
Zahlen, Pflichtfelder, Schalter, Teilungen, die Rissanforderung -- und die
alten Formate, die es in gespeicherten Dateien noch gibt (vier Lagen statt
beliebig vieler, flache statt verschachtelter Gebrauchslisten, Lastfaelle
in y).

Ein eigenes Modul, weil sie die Lesefunktionen des ganzen Pakets sind:
[[opencivil.projekt.eintraege|eintraege]], [[opencivil.projekt.projekt#Projekt.platte|platte]] und [[opencivil.projekt.aufbau|aufbau]] brauchen sie alle. Mit
Unterstrich waren sie privat und wurden trotzdem von drei Modulen
importiert.

## Inhalt

### ProjektFehler

```python
class ProjektFehler(Exception)
```

Die Projektbeschreibung ist in sich nicht stimmig.

### zahl

```python
def zahl(d: Mapping[str, Any], feld: str, vorgabe: float) -> float
```

Eine Zahl aus der Beschreibung. Die Vorgabe gilt nur, wenn nichts dasteht.

Bewusst **nicht** `float(d.get(feld) or vorgabe)`: dieser Ausdruck kann
eine eingegebene Null nicht von einem fehlenden Feld unterscheiden und
ersetzt sie stillschweigend. Im Eingabefeld stand dann `h = 0`, gerechnet
wurde mit 300 mm, und die Herleitung schrieb 300 mm hin -- ein Widerspruch,
den niemand sieht. Eine Platte ohne Dicke meldete «alle Nachweise erfüllt».

### kriechzahl_aus

```python
def kriechzahl_aus(d: Mapping[str, Any], feld: str, *, alt: float, wo: str) -> float
```

Die Kriechzahl eines Nachweis-Kapitels oder einer Analyse.

Fehlt sie oder steht sie leer -- in einer Datei von vor 2026-10-09 --,
gilt `alt`: die Kriechzahl der Platte, mit der damals jedes Kapitel
rechnete. So rechnet eine alte Datei wie damals, und eine neue Platte
beginnt mit der Vorgabe ihrer Felder, 0. Die eine Stelle fuer diese Regel.

### pflichtfeld

```python
def pflichtfeld(d: Mapping[str, Any], feld: str, wer: str) -> str
```

Ein Feld, ohne das sich nichts zusammenbauen laesst.

Ohne diese Pruefung kam der nackte `KeyError` bis in die Oberflaeche --
eine Fehlermeldung, die dem Benutzer nichts sagt und nach einem Absturz
aussieht.

### sorten

```python
def sorten(art: str) -> Mapping[str, Any]
```

### vorgabe

```python
def vorgabe(cls, feld: str) -> Any
```

Die Vorgabe eines Feldes, wie die Datenklasse sie festlegt -- auch fuer
Felder mit `default_factory`.

Die Leser nehmen ihre Vorgaben von der Klasse (`cls.h` oder hier) und
schreiben sie nicht noch einmal hin. Stand die Zahl zweimal da -- im Feld
und im Leser, und ein drittes Mal in der Oberflaeche --, gab es drei
Vorgaben, die nur so lange uebereinstimmten, wie niemand eine aenderte.

### rissanforderung_aus

```python
def rissanforderung_aus(wert: Any, vorgabe: str) -> str
```

Die Anforderung an die Rissbildung, oder die Vorgabe.

Eine unbekannte Angabe wird nicht stillschweigend auf 'normal' gezogen --
sie waere die mildeste der drei, und eine stillschweigende Milderung ist
genau das, was ein Nachweiswerkzeug nicht tun darf.

### teilungen_aus

```python
def teilungen_aus(roh, vorgabe) -> List[float]
```

Eine Liste von Teilungen, aufsteigend und ohne Unsinn.

Ohne brauchbare Angabe die Vorgabe: eine leere Liste hiesse, dass die
Suche nichts zu versuchen haette, und das ist kein Zustand, in dem man
eine Oberflaeche stehen lassen will.

### schalter_aus

```python
def schalter_aus(*werte: Any, vorgabe: bool=False) -> bool
```

Ein Schalter aus dem, was in der Datei steht.

Frueher war jeder dieser Nachweise eine Liste von vier Schaltern, einer je
Lage, und die Zwaengung hatte je einen fuer x und y. Nachgewiesen wird nur
noch x, und dort entscheidet die unguenstigere der beiden Lagen -- ein
Schalter genuegt. Eine alte Datei bringt noch die Liste mit: war darin
irgendein Haken gesetzt, gilt der Nachweis als eingeschaltet. Das ist die
Lesart, die nichts wegnimmt, was jemand verlangt hat.

Mehrere Werte, weil aus `zwaengung_x` und `zwaengung_y` einer wird.

### nur_x

```python
def nur_x(d: Mapping[str, Any], was: str) -> None
```

Alte Lastfaelle, die nur in y galten, gehen nicht mehr.

Nachgewiesen wird ausschliesslich x. Ein Lastfall mit `richtung: "y"`
stillschweigend auf x umzudeuten hiesse, eine Zahl an einem anderen
Querschnitt anzusetzen als der Benutzer gemeint hat -- genau die Art von
stiller Aenderung, die ein Nachweiswerkzeug nicht machen darf. `x` und
`beide` gelten unveraendert weiter.

### gebrauchsliste_roh

```python
def gebrauchsliste_roh(d: Mapping[str, Any], feld: str, alt: str) -> Mapping[str, Any]
```

Die Gebrauchsliste einer Platte aus der Datei -- verschachtelt oder flach.

Bis zur [[opencivil.projekt.eintraege#Gebrauchsliste|Gebrauchsliste]] standen die drei Angaben einzeln an der
Platte: `haeufige`, `haeufige_aus_tragsicherheit`, `haeufige_anteil`
und dasselbe fuer `quasistaendige`. Solche Dateien gibt es; sie werden
hier in die neue Form gebracht, geschrieben wird nur noch diese.

### lagen_aus_altem_format

```python
def lagen_aus_altem_format(d: Mapping[str, Any]) -> List[dict]
```

Rechnet eine vor dem Vier-Lagen-Modell gespeicherte Platte um.

Frueher gab es beliebig viele Lagen je Seite, jede mit einem einzigen
Bewehrungssatz. Uebernommen werden die beiden aeussersten je Seite:

```
lagen_unten[0] -> 1. Lage      lagen_oben[0] -> 4. Lage
lagen_unten[1] -> 2. Lage      lagen_oben[1] -> 3. Lage
```

Weitere Lagen der alten Beschreibung gehen dabei verloren -- besser als eine
gespeicherte Datei gar nicht mehr zu oeffnen, aber der Benutzer sollte sie
nachsehen.


## Konstanten

- `BEIDE_RICHTUNGEN = 'beide'` – Wahl der Tragrichtung einer Schnittgroessenkombination -- historisch. Schnittgroessen gehoeren jetzt immer zur Tragrichtung x; die Wahl gibt es nicht mehr. Die Konstante steht noch, um alte Dateien zu lesen.
- `_BESCHRIFTUNG = {'normal': 'Normal', 'erhoeht': 'Erhöht', 'hoch': 'Hoch'}` – Wie die Rissanforderungen an der Maske heissen.
- `RISSANFORDERUNGEN = {wert: _BESCHRIFTUNG[wert] for wert in RISSBREITE}` – Anforderung an die Rissbildung, mit ihrer Beschriftung. Welche es gibt, sagt [[opencivil.nachweis.mindestbewehrung#Konstanten|mindestbewehrung.RISSBREITE]] -- dort steht zu jeder die Rissbreite, und die Liste der Werte soll nur einmal dastehen. Kaeme dort eine dazu, ohne dass sie hier eine Beschriftung hat, scheiterte schon der Import.

## Braucht

- [[opencivil.material.beton]]
- [[opencivil.material.betonstahl]]
- [[opencivil.nachweis.mindestbewehrung]]
- [[opencivil.querschnitt.platte]]

## Gebraucht von

- [[opencivil.projekt]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.balkensystem]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.grundbruch]]
- [[opencivil.projekt.platte]]
- [[opencivil.projekt.projekt]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.projekt.skript]]
