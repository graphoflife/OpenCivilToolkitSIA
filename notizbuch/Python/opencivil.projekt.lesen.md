---
erzeugt: 2f2161abf43e
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/lesen.py
> was in einer Projektdatei stehen darf, und wie es gelesen wird.
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/lesen.py)

## VERANTWORTUNG

Ein Leser fuer jeden Eintrag und eine Pruefung fuer jedes Feld, beide aus den
Feldern der Datenklassen. Was ein Feld annehmen darf, steht an ihm selbst:

* sein Typ -- Text, Zahl, ganze Zahl, Schalter, Liste, Zuordnung, Eintrag;
* eine Wahl ([[opencivil.projekt.lesen#einer_von|einer_von]]) -- die Werte, die es gibt;
* eine Untergrenze ([[opencivil.projekt.lesen#nicht_negativ|nicht_negativ]]);
* ein Text ohne Vorgabe ist Pflicht und darf nicht leer sein.


## STRENG

Gelesen wird, was dasteht, und nichts sonst. Ein Feld, das es nicht gibt, ein
Text statt einer Zahl, eine Wahl, die es nicht gibt -- jedes meldet sich, mit
dem Ort in der Datei und dem Wert. Umgedeutet wird nichts: ein unbekanntes
Feld ist meist ein Tippfehler, und ein still uebergangener Tippfehler rechnet
mit der Vorgabe statt mit der Zahl des Benutzers. Alte Dateiformate liest
niemand mehr; alte Speicherstaende muessen seit 2026-10-11 nicht mehr gehen
(Benutzer).

Was fehlt, bekommt die Vorgabe: die des Feldes -- und bei einem Eintrag, der
in einem Eintrag steht, die eines frischen an dieser Stelle. Die Rechenwahl
des Knickens rechnet ohne Angabe praezise, nicht von Hand wie eine Rechenwahl
fuer sich.


## EINE TUER

Dieselbe Pruefung laeuft vor jedem Rechnen ueber das ganze Projekt
([[opencivil.projekt.projekt#Projekt.pruefen|pruefen]]). Was in Python gebaut
wurde, ohne Datei, geht durch dieselbe Tuer wie eine Datei: ein «festt» im
Linienlager meldet sich hier und wird nicht still zur Feder.

Was erst das Rechnen braucht -- eine Dicke groesser als null, das Material,
auf das eine Platte zeigt --, prueft der Aufbau. Eine abgelegte Platte mit
h = 0 soll sich oeffnen und korrigieren lassen.

## Inhalt

### ProjektFehler

```python
class ProjektFehler(Exception)
```

Die Projektbeschreibung ist in sich nicht stimmig.

### einer_von

```python
def einer_von(moeglich: Iterable[Any], vorgabe: Any=dataclasses.MISSING) -> Any
```

Ein Feld, das nur einen dieser Werte annimmt -- die Pruefung kennt sie von hier.

### nicht_negativ

```python
def nicht_negativ(vorgabe: float) -> Any
```

Eine Zahl, die nicht unter null liegen kann -- eine Kriechzahl etwa.

### sorten

```python
def sorten(art: str) -> Mapping[str, Any]
```

Die Normsorten einer Materialart.

### lesen

```python
def lesen(cls: type, roh: Any, wo: str, basis: Any=None) -> Any
```

Ein Eintrag der Klasse `cls` aus `roh`, einem Woerterbuch aus der Datei.

`wo` nennt den Ort in Meldungen. `basis` ist der Eintrag, dessen Werte
fuer fehlende Felder gelten -- ohne sie die Vorgaben der Klasse. Jeder
gelesene Eintrag ist danach geprueft ([[opencivil.projekt.lesen#felder_pruefen|felder_pruefen]]).

### _wert_lesen

```python
def _wert_lesen(roh: Any, typ: Any, wo: str, feld: str, vorbild: Any) -> Any
```

Ein Feld aus der Datei. Eintraege und Listen von Eintraegen werden
gelesen; Zahlen bleiben, was sie sind -- nur eine ganze Zahl aus JSON wird
dort, wo eine Zahl hingehoert, zur Gleitkommazahl, und eine ganze
Gleitkommazahl dort, wo eine ganze Zahl hingehoert, zur ganzen. Ob der
Wert passt, sagt danach [[opencivil.projekt.lesen#felder_pruefen|felder_pruefen]].

### _zahl_lesen

```python
def _zahl_lesen(roh: Any, typ: Any) -> Any
```

Eine Zahl, wie JSON sie bringt, in der Art des Feldes -- alles andere unveraendert.

### ort

```python
def ort(cls: type, roh: Any) -> str
```

Wie ein Eintrag fuer sich in Meldungen heisst: «Platte 'Decke'», ohne
Namen mit seiner Kennung, sonst nur seine Art.

### _ort_roh

```python
def _ort_roh(element: Any, cls: type, wo: str, feld: str, i: int) -> str
```

Wie ein Listenelement in Meldungen heisst -- aus der Datei, vor dem Lesen.

### _ort

```python
def _ort(cls: type, name: Any, kennung: Any, wo: str, feld: str, i: int) -> str
```

Ein Bauteil oder Material heisst wie in der Oberflaeche -- «Platte 'Decke'»,
und dort beginnt der Ort neu; alles darin nach seinem Feld und seinem
Namen, ohne Namen nach seiner Nummer: «lagen 2».

### _benannt

```python
def _benannt(bezeichnung: str, name: Any, kennung: Any) -> Optional[str]
```

«Platte 'Decke'», ohne Namen «Platte q1» -- `None` ohne beides.

### felder_pruefen

```python
def felder_pruefen(eintrag: Any, wo: str, *, tief: bool=True) -> None
```

Prueft jedes Feld eines Eintrags gegen das, was an ihm steht: Typ, Wahl,
Pflicht, Untergrenze. `tief`: auch jeden Eintrag darin.

### _blatt_pruefen

```python
def _blatt_pruefen(wert: Any, typ: Any, f: dataclasses.Field, wo: str) -> None
```

Ein Text, eine Zahl, ein Schalter -- und was an seinem Feld steht.

### _typen

```python
@functools.lru_cache(maxsize=None)
def _typen(cls: type) -> Dict[str, Any]
```

Die Typen der Felder, aufgeloest -- je Klasse einmal.

### _art

```python
def _art(typ: Any)
```

Was fuer ein Feld es ist: `optional`, `liste`, `zuordnung`,
`eintrag` -- mit dem Typ darin -- oder ein Blatt.

### _vorgabe

```python
def _vorgabe(f: dataclasses.Field) -> Any
```

Die Vorgabe eines Feldes -- auch eine aus `default_factory` --, sonst [[opencivil.projekt.lesen#Konstanten|_KEINE]].

### _zeigen

```python
def _zeigen(wert: Any) -> str
```

Ein Wert, wie er in einer Meldung steht -- ein Text in Anfuehrungszeichen.


## Konstanten

- `_KEINE = object()` – Ein Feld ohne Vorgabe.

## Braucht

- [[opencivil.material.beton]]
- [[opencivil.material.betonstahl]]

## Gebraucht von

- [[opencivil.projekt]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.balkensystem]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.grundbruch]]
- [[opencivil.projekt.platte]]
- [[opencivil.projekt.projekt]]
- [[opencivil.projekt.querschnittsanalyse]]
