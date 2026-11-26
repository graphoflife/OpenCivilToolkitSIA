---
erzeugt: 936e817b47f6
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
* ein Text ohne Vorgabe ist Pflicht und darf nicht leer sein -- ausser einem
  Namen: ohne ihn haelt erst das Rechnen sein Bauteil an
  ([[opencivil.projekt.lesen#inhalt_pruefen|inhalt_pruefen]]);
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
machten daraus wieder das Mitglied. Dasselbe gilt fuer jeden Wert einer
Zuordnung von Wahlen, etwa den Wertesatz je Material ([[opencivil.projekt.lesen#je_material|je_material]]).

## Inhalt

### ProjektFehler

```python
class ProjektFehler(Exception)
```

Die Projektbeschreibung ist in sich nicht stimmig. `grund` sagt, was
nicht stimmt, als Satz mit Punkt; `wo`, wo -- wie der Eintrag in
Meldungen heisst ([[opencivil.projekt.lesen#ort|ort]]), «Platte 'Decke'», tiefer «Pfahl 'P',
Schicht 2» --, leer, wo es das ganze Projekt betrifft. Die Meldung ist
beides: «Platte 'Decke': noch keine Bewehrung.»

Bis 2026-11-20 stand der Ort nur im Text, und wer den Grund an seiner
Stelle brauchte, schnitt ihn wieder heraus.

#### ProjektFehler.grund_bei

```python
def grund_bei(self, wo: str) -> str
```

Der Fehler, wie er an der Stelle `wo` steht, ohne Punkt am Ende:
dort nur der Grund, unter ihr mit dem Rest des Orts -- «Schicht 2:
…» bei «Pfahl 'P'» --, anderswo die ganze Meldung.

### anhalten

```python
def anhalten(grund: str, wo: str) -> None
```

Haelt mit `grund` an der Stelle `wo` an -- nichts, wenn `grund`
leer ist: was ein [[opencivil.core.bereich#Bereich|Bereich]] abweist, als
[[opencivil.projekt.lesen#ProjektFehler|ProjektFehler]].

### einer_von

```python
def einer_von(moeglich: Iterable[Any], vorgabe: Any=dataclasses.MISSING) -> Any
```

Ein Feld, das nur einen dieser Werte annimmt -- die Pruefung kennt sie von hier.

### teil

```python
def teil(fabrik: Callable[[], Any], *, heisst: str) -> Any
```

Ein Feld, das einen ganzen Eintrag haelt -- die Grundbewehrung einer Lage,
die Rechenwahl der Tragsicherheit --, mit dem Wort, unter dem es in
Meldungen steht: wie die Maske es nennt, «Lage 2, Grund», nicht wie die
Datei, «Lage 2, grund» (Benutzer, 2026-11-21). Ein Element einer Liste
nennt seine Klasse (`IM_ORT`, [[opencivil.projekt.lesen#_ort|_ort]]).

### _im_ort

```python
def _im_ort(f: dataclasses.Field) -> str
```

Wie das Feld `f` als Teil eines Orts heisst -- sein Wort ([[opencivil.projekt.lesen#teil|teil]]), sonst sein Name.

### je_material

```python
def je_material(vorgabe: Any, moeglich: Optional[Iterable[Any]]=None) -> Any
```

Ein Feld, das je Material eine Wahl haelt, unter der Kennung des
Materials -- den Wertesatz etwa. Ein Material ohne eigene Wahl waehlt
`vorgabe` ([[opencivil.projekt.lesen#vorgabe_je_material|vorgabe_je_material]]); `moeglich` begrenzt die Wahl
wie bei [[opencivil.projekt.lesen#einer_von|einer_von]]. Eine Zuordnung und keine Liste: zwei Wahlen
fuer dasselbe Material kann es so nicht geben. Bis 2026-11-20 hielt die
Querschnittsanalyse eine Liste und wies doppelte Eintraege eigens ab.

### vorgabe_je_material

```python
def vorgabe_je_material(cls: type, feld: str) -> Any
```

Was ein Material im Feld `feld` ([[opencivil.projekt.lesen#je_material|je_material]]) waehlt, solange es keine eigene Wahl hat.

### bereich

```python
def bereich(vorgabe: Any=dataclasses.MISSING, *, heisst: str, einheit: Optional[Einheit]=None, ueber: Optional[float]=None, ab: Optional[float]=None, bis: Optional[float]=None, unter: Optional[float]=None, bis_feld: Optional[str]=None, quer_zu: Optional[Tuple[str, float]]=None, fabrik: Optional[Callable[[], Any]]=None) -> Any
```

Ein Feld, dessen Zahl in einem [[opencivil.core.bereich#Bereich|Bereich]] liegen muss -- eine
Kriechzahl ab null etwa. Bei einer Liste von Zahlen gilt er fuer jede,
und leer ist sie nie ([[opencivil.projekt.lesen#inhalt_pruefen|inhalt_pruefen]]); ihre Vorgabe kommt dann
aus `fabrik`.

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
(`ueber`, `ab`, `bis`, `unter` wie [[opencivil.core.bereich#Bereich|Bereich]]) und ob sie
ganz sein muss. Hat das Feld Grenzen, dazu, was es sagt, wenn eine Zahl
sie verletzt (`heisst`, `verlangt`: «Dicke h» «muss grösser als null
sein») -- das Feld weist sie mit dem Satz ab, der sonst beim Rechnen
kaeme. Was eine Wahl annehmen kann, steht nicht hier: das sagen die
Wahllisten des Katalogs, mit Beschriftung.

Begrenzt ein Feld ein anderes ([[opencivil.core.bereich#Bereich|Bereich.bis_feld]]), steht das an
beiden, mit dem Namen des anderen Feldes und dem Satz, den das Feld
sagt: `bis_feld` bei α_min, `ab_feld` bei α_max. Ebenso `quer_zu`
an beiden Feldern, mit dem kleinsten Abstand als Linien in Grad
([[opencivil.core.bereich#Bereich|Bereich.quer_zu]], `mindestens`). Die Zahl des anderen Feldes
kennt erst die Maske.

Haelt ein Feld je Material eine Wahl ([[opencivil.projekt.lesen#je_material|je_material]]), steht dort,
was ein Material ohne eigene waehlt: `vorgabe` -- und ist die Wahl
begrenzt, was sie annehmen kann, in ihrer Folge: `wahl`. Danach
stellt die Maske die Rechenart je Beton, mit ihren Stellungen.

Steht es am Feld, steht es einmal. Bis 2026-10-18 standen die Einheiten
des Grundbruchs dreimal da -- am Feld, beim Bauen und in grundbruch.js --,
und wichen zwei davon ab, galt eine Zahl still um 10³ anders.

### feldtypen

```python
def feldtypen(cls: type) -> Dict[str, Dict[str, Any]]
```

Was jedes Feld einer Klasse von Eintraegen haelt -- fuer wer ohne Maske
schreibt, den MCP-Zugang ([[opencivil.mcp]]). `art` ist `zahl`,
`ganz`, `text`, `ja/nein`, `wahl` (mit `wahl`: was sie annehmen
kann, [[opencivil.projekt.lesen#wahl_von|wahl_von]]), `eintrag` (mit `klasse`: ihr Name im Katalog,
[[opencivil.projekt.lesen#katalogname|katalogname]]), `liste` oder `zuordnung` (mit `von`: was darin
steht). `leer`, wo statt eines Wertes auch keiner stehen darf. Einheit
und Grenzen sagt [[opencivil.projekt.lesen#feldangaben|feldangaben]].

### _bereiche

```python
@functools.lru_cache(maxsize=None)
def _bereiche(cls: type) -> Dict[str, Bereich]
```

Die Bereiche der Felder einer Klasse, nach Feldnamen -- je Klasse einmal.

### katalogname

```python
def katalogname(cls: type) -> str
```

Wie eine Klasse von Eintraegen im Katalog der Oberflaeche heisst: ohne
«Eintrag», klein -- `grundbruch`, `raumlinie`. Unter diesem Namen
stehen ihre Feldangaben und ihre Vorlage.

### eintragsklassen

```python
def eintragsklassen(cls: type) -> List[type]
```

Jede Klasse von Eintraegen, die unter `cls` vorkommt, `cls` zuerst --
gefunden auf dem Weg, auf dem [[opencivil.projekt.lesen#lesen|lesen]] eine Datei ablaeuft: durch
Felder, Listen, Zuordnungen und Optionale. Fuer den Katalog der
Feldangaben ([[opencivil.projekt.lesen#feldangaben|feldangaben]]).

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

Kennt eine Klasse ein Feld, das in `roh` fehlt, aber aus dem folgt,
was dasteht -- eine Datei von frueher kennt es noch nicht --, ergaenzt
sie es vorher selbst: `cls.ergaenzt(roh, basis)`, etwa
[[opencivil.projekt.decke#DeckenplatteEintrag.ergaenzt|ergaenzt]].

### _wert_lesen

```python
def _wert_lesen(roh: Any, typ: Any, wo: str, f: dataclasses.Field, vorbild: Any) -> Any
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

### ort_von

```python
def ort_von(eintrag: Any) -> str
```

[[opencivil.projekt.lesen#ort|ort]] eines gelesenen Eintrags -- ein Material heisst nach seiner
Anzeige, ohne eigenen Namen nach der Sorte.

### element_ort

```python
def element_ort(element: Any, cls: type, wo: str, feld: str, i: int) -> str
```

Wie das Element `i` der Liste `feld` in Meldungen heisst -- aus der
Datei, vor dem Lesen. Auch fuer ein neues, das Python anlegt
(`MitStaeben._gelesen`): bis 2026-11-21 hiess es dort nach seiner
Liste, «linien».

### _ort

```python
def _ort(cls: type, name: Any, kennung: Any, wo: str, feld: str, i: int) -> str
```

Ein Bauteil oder Material heisst wie in der Oberflaeche -- «Platte 'Decke'»,
und dort beginnt der Ort neu; alles darin mit seinem Namen, davor das
Wort seiner Klasse (`IM_ORT`: «Wand 'W1'» im Erdbeben, «Kombination
'GZT'»). Bis 2026-11-21 stand ohne Wort das Feld der Datei davor,
«kombinationen 'GZT'»; ein Test wacht, dass jede Klasse eines hat. Nur
Leerzeichen sind kein Name.

Ohne Namen heisst ein Element, wie die Maske es nennt: mit dem Wort
seiner Klasse und seiner Nummer (`IM_ORT`: «Lage 2», «Linie 3» wie in
der Zeichnung einer Querschnittsanalyse), sonst mit seiner Kennung
(«A1», wie im Balkensystem), sonst nach Feld und Nummer. Bis 2026-11-20
hiess es immer nach Feld und Nummer: «lagen 2», «lager 1».

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
def inhalt_pruefen(eintrag: Any, wo: str, ohne: Iterable[str]=()) -> None
```

Prueft, was erst das Rechnen braucht -- nach der Form, vor jedem Rechnen:
jede Zahl gegen ihren Bereich ([[opencivil.projekt.lesen#bereich|bereich]]) -- eine Liste davon mit
mindestens einer --, jeden Eintrag darin ebenso, jede gegen das Feld,
das sie begrenzt ([[opencivil.core.bereich#Bereich|Bereich.bis_feld]], [[opencivil.core.bereich#Bereich|Bereich.quer_zu]]),
und danach die Namen seiner Faelle (`fallnamen()`) und die Regeln des
Eintrags ueber mehrere Felder, `regeln(wo)`. Die Form ist da schon geprueft: ein Eintrag steht, wo
einer hingehoert, eine Zahl, wo eine Zahl hingehoert. Die Felder in
`ohne` prueft, wer sie einzeln prueft -- der Aufbau jedes Material und
jedes Bauteil fuer sich ([[opencivil.projekt.aufbau#aufbauen|aufbauen]]).

Zuerst der Name, wo einer Pflicht ist ([[opencivil.projekt.lesen#_ist_name|_ist_name]]): leer oder nur
Leerzeichen sagt «noch kein Name», wie das Namensfeld ihn abweist.

### _ist_name

```python
def _ist_name(f: dataclasses.Field) -> bool
```

Ob ein Feld der Name seines Eintrags ist, ohne Vorgabe. Leer haelt er
nicht schon das Lesen auf, sondern erst das Rechnen seines Bauteils
([[opencivil.projekt.lesen#inhalt_pruefen|inhalt_pruefen]]): bis 2026-11-19 liess ein leerer Fallname aus
einer bearbeiteten Datei das ganze Projekt nicht mehr oeffnen (Benutzer:
nur seine Platte oder Analyse rechnet nicht).

### _ort_von

```python
def _ort_von(element: Any, wo: str, feld: str, i: int) -> str
```

Wie ein gebautes Listenelement in Meldungen heisst -- wie [[opencivil.projekt.lesen#element_ort|element_ort]] vor dem Lesen.

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

### _wahlzuordnungen

```python
@functools.lru_cache(maxsize=None)
def _wahlzuordnungen(cls: type) -> Dict[str, type]
```

Je Feld, das eine Zuordnung von Wahlen haelt ([[opencivil.projekt.lesen#je_material|je_material]]), die Wahl seiner Werte.

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

### _mitglied

```python
def _mitglied(wahl: type, wert: Any) -> Any
```

Ein Text als Mitglied der Wahl -- ein Text, den es nicht gibt, bleibt Text.

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

- `_BLAETTER = {bool: 'ja/nein', int: 'ganz', float: 'zahl', str: 'text'}` – Wie ein Blatt in [[opencivil.projekt.lesen#feldtypen|feldtypen]] heisst, nach seinem Typ.
- `_KEINE = object()` – Ein Feld ohne Vorgabe.

## Braucht

- [[opencivil.core.bereich]]
- [[opencivil.core.einheiten]]

## Gebraucht von

- [[opencivil.mcp.ausgabe]]
- [[opencivil.mcp.sitzung]]
- [[opencivil.mcp.werkzeuge]]
- [[opencivil.mcp.zeiger]]
- [[opencivil.projekt]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.aufbau.balkensystem]]
- [[opencivil.projekt.aufbau.durchstanzen]]
- [[opencivil.projekt.aufbau.erdbeben]]
- [[opencivil.projekt.aufbau.grundbruch]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.aufbau.pfahl]]
- [[opencivil.projekt.aufbau.platte]]
- [[opencivil.projekt.aufbau.querschnittsanalyse]]
- [[opencivil.projekt.aufbau.setzung]]
- [[opencivil.projekt.balkensystem]]
- [[opencivil.projekt.balkensystem3d]]
- [[opencivil.projekt.decke]]
- [[opencivil.projekt.durchstanzen]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.erdbeben]]
- [[opencivil.projekt.fallnamen]]
- [[opencivil.projekt.grundbruch]]
- [[opencivil.projekt.mappe]]
- [[opencivil.projekt.netz]]
- [[opencivil.projekt.pfahl]]
- [[opencivil.projekt.platte]]
- [[opencivil.projekt.projekt]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.projekt.setzung]]
- [[opencivil.projekt.staebe]]
- [[opencivil.web.api]]
- [[opencivil.web.systemkatalog]]
