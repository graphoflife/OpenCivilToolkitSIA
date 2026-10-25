---
erzeugt: 2ee31d5d9ee6
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/lesen.py
> was in einer Projektdatei stehen darf, und wie es gelesen wird.
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/lesen.py)

## VERANTWORTUNG

Ein Leser fuer jeden Eintrag und eine Pruefung fuer jedes Feld, beide aus den
Feldern der Datenklassen. Was ein Feld annehmen darf, steht an ihm selbst:

* sein Typ -- Text, Zahl, ganze Zahl, Schalter, Liste, Zuordnung, Eintrag,
  oder eine Wahl ([[opencivil.core.wahl#Wahl|Wahl]]), deren Mitglieder es
  annimmt;
* eine Teilmenge davon ([[opencivil.projekt.lesen#einer_von|einer_von]]) -- die Werte, die es gibt;
* ein Text ohne Vorgabe ist Pflicht und darf nicht leer sein;
* ein Bereich ([[opencivil.projekt.lesen#bereich|bereich]]) -- wo seine Zahl liegen muss.


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


## FORM BEIM LESEN, INHALT VOR DEM RECHNEN

Beim Lesen zaehlt die Form: Typ, Wahl, Pflicht. Was erst das Rechnen braucht
-- der Bereich eines Feldes, eine Dicke groesser als null, die Regeln ueber
mehrere Felder (`regeln`) --, prueft [[opencivil.projekt.lesen#inhalt_pruefen|inhalt_pruefen]] vor jedem
Rechnen; das Material, auf das eine Platte zeigt, der Aufbau. Eine abgelegte
Platte mit h = 0 soll sich oeffnen und korrigieren lassen. Bis 2026-10-17
hielt eine negative Kriechzahl schon das Oeffnen auf, eine negative
Ueberdeckung erst das Rechnen.


## WAHLEN SIND MITGLIEDER

Ein Wahlfeld haelt das Mitglied seiner Wahl, nicht den Text: aus «hoch» in
der Datei wird `Rissanforderung.HOCH`, und wer im Code einen Text
zuweist, bekommt ebenso das Mitglied ([[opencivil.projekt.lesen#wahl_aus_text|wahl_aus_text]], aufgerufen von
`Beschreibung.__setattr__`). Geschrieben wird der Text -- `json.dumps`
schreibt eine Wahl als ihren Wert, die Dateien bleiben Zeichen fuer Zeichen
gleich. Bis 2026-10-17 hielten die Felder Text, und rund dreissig Stellen
machten daraus wieder das Mitglied.

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

### Bereich

```python
@dataclasses.dataclass(frozen=True)
class Bereich
```

Wo die Zahl eines Feldes liegen muss -- jede Grenze darf fehlen, `ueber`
und `unter` schliessen die Grenze aus, `ab` und `bis` ein. Geprueft
vor dem Rechnen ([[opencivil.projekt.lesen#inhalt_pruefen|inhalt_pruefen]]).

- `heisst: str` – Wie das Feld in der Meldung heisst -- wie an der Maske: «Dicke h».
- `einheit: Optional[Einheit] = None`
- `ueber: Optional[float] = None`
- `ab: Optional[float] = None`
- `bis: Optional[float] = None`
- `unter: Optional[float] = None`

#### Bereich.pruefen

```python
def pruefen(self, wert: float, wo: str) -> None
```

#### Bereich.verlangt

```python
@property
def verlangt(self) -> str
```

Was die Grenzen verlangen: «muss grösser als null sein».

#### Bereich._zahl

```python
def _zahl(self, wert: float) -> str
```

Eine Zahl mit der Einheit des Feldes: «300 mm», «30°», «0.9».

### bereich

```python
def bereich(vorgabe: Any=dataclasses.MISSING, *, heisst: str, einheit: Optional[Einheit]=None, ueber: Optional[float]=None, ab: Optional[float]=None, bis: Optional[float]=None, unter: Optional[float]=None) -> Any
```

Ein Feld, dessen Zahl in einem [[opencivil.projekt.lesen#Bereich|Bereich]] liegen muss -- eine Kriechzahl ab null etwa.

### als_groesse

```python
def als_groesse(eintrag: Any, feld: str) -> Groesse
```

Die Zahl eines Feldes als Groesse, in der Einheit seines Bereichs -- der,
in der die Maske sie zeigt ([[opencivil.projekt.lesen#feldangaben|feldangaben]]); ohne Einheit
einheitslos. So steht die Einheit einer Eingabe nur an ihrem Feld.

### feldangaben

```python
def feldangaben(cls: type) -> Dict[str, Dict[str, Any]]
```

Was die Oberflaeche je Feld eines Eintrags vom Kern wissen muss, fuer den
Katalog: die Einheit, in der eine Zahl gemeint ist, wo sie liegen muss
(`ueber`, `ab`, `bis`, `unter` wie [[opencivil.projekt.lesen#Bereich|Bereich]]) und ob sie
ganz sein muss. Was eine Wahl annehmen kann, steht nicht hier: das sagen
die Wahllisten des Katalogs, mit Beschriftung.

Steht es am Feld, steht es einmal. Bis 2026-10-18 standen die Einheiten
des Grundbruchs dreimal da -- am Feld, beim Bauen und in grundbruch.js --,
und wichen zwei davon ab, galt eine Zahl still um 10³ anders.

### eintragsklassen

```python
def eintragsklassen(cls: type) -> List[type]
```

Jede Klasse von Eintraegen, die unter `cls` vorkommt, `cls` zuerst --
gefunden auf dem Weg, auf dem [[opencivil.projekt.lesen#lesen|lesen]] eine Datei ablaeuft: durch
Felder, Listen, Zuordnungen und Optionale. Fuer den Katalog der
Feldangaben ([[opencivil.projekt.lesen#feldangaben|feldangaben]]).

### sorten

```python
def sorten(art: str) -> Mapping[str, Any]
```

Die Normsorten einer Materialart.

### unbekanntes_feld

```python
def unbekanntes_feld(wo: str, name: Any, felder: Iterable[str]) -> ProjektFehler
```

Der Fehler zu einem Feld, das es nicht gibt -- mit dem ähnlichsten, das
es gibt. Beim Lesen einer Datei und bei einer Zuweisung aus Python
derselbe Satz.

### lesen

```python
def lesen(cls: type, roh: Any, wo: str, basis: Any=None) -> Any
```

Ein Eintrag der Klasse `cls` aus `roh`, einem Woerterbuch aus der Datei.

`wo` nennt den Ort in Meldungen. `basis` ist der Eintrag, dessen Werte
fuer fehlende Felder gelten -- ohne sie die Vorgaben der Klasse. Jeder
gelesene Eintrag ist danach geprueft ([[opencivil.projekt.lesen#felder_pruefen|felder_pruefen]]).

Aus Python darf `roh` auch schon ein Eintrag der Klasse sein, etwa ein
Stichwort der Fassade: er bleibt, wie er ist, und wird ganz geprueft.

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

Prueft die Form jedes Feldes eines Eintrags gegen das, was an ihm steht:
Typ, Wahl, Pflicht. `tief`: auch jeden Eintrag darin.

### _blatt_pruefen

```python
def _blatt_pruefen(wert: Any, typ: Any, f: dataclasses.Field, wo: str) -> None
```

Ein Text, eine Zahl, ein Schalter, eine Wahl -- und was an seinem Feld steht.

### inhalt_pruefen

```python
def inhalt_pruefen(eintrag: Any, wo: str) -> None
```

Prueft, was erst das Rechnen braucht -- nach der Form, vor jedem Rechnen:
jede Zahl gegen ihren Bereich ([[opencivil.projekt.lesen#bereich|bereich]]), jeden Eintrag darin
ebenso, und danach die Regeln des Eintrags ueber mehrere Felder,
`regeln(wo)`. Die Form ist da schon geprueft: ein Eintrag steht, wo
einer hingehoert, eine Zahl, wo eine Zahl hingehoert.

### _ort_von

```python
def _ort_von(element: Any, wo: str, feld: str, i: int) -> str
```

Wie ein gebautes Listenelement in Meldungen heisst -- wie [[opencivil.projekt.lesen#_ort_roh|_ort_roh]] vor dem Lesen.

### _typen

```python
@functools.lru_cache(maxsize=None)
def _typen(cls: type) -> Dict[str, Any]
```

Die Typen der Felder, aufgeloest -- je Klasse einmal.

### _wahlfelder

```python
@functools.lru_cache(maxsize=None)
def _wahlfelder(cls: type) -> Dict[str, type]
```

Je Wahlfeld einer Datenklasse seine Wahl -- je Klasse einmal.

### wahl_von

```python
def wahl_von(cls: type, feld: str) -> tuple
```

Was ein Wahlfeld annehmen kann -- seine Teilmenge, sonst jedes Mitglied seiner Wahl.

### wahl_aus_text

```python
def wahl_aus_text(cls: type, feld: str, wert: Any) -> Any
```

Text in einem Wahlfeld wird sein Mitglied -- beim Lesen einer Datei und
wo Python einen Text zuweist. Ein Text, den es nicht gibt, bleibt Text:
die Pruefung meldet ihn dann mit seinem Ort ([[opencivil.projekt.lesen#felder_pruefen|felder_pruefen]]).

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

- [[opencivil.core.einheiten]]
- [[opencivil.material.beton]]
- [[opencivil.material.betonstahl]]

## Gebraucht von

- [[opencivil.projekt]]
- [[opencivil.projekt.aufbau.balkensystem]]
- [[opencivil.projekt.aufbau.grundbruch]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.aufbau.platte]]
- [[opencivil.projekt.aufbau.querschnittsanalyse]]
- [[opencivil.projekt.aufbau.setzung]]
- [[opencivil.projekt.balkensystem]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.grundbruch]]
- [[opencivil.projekt.platte]]
- [[opencivil.projekt.projekt]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.projekt.setzung]]
- [[opencivil.web.api]]
