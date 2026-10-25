---
erzeugt: 7b6e55abca23
art: modul
tags: [modul]
---
> [!abstract] opencivil/bericht/zusammenfassung.py
> was in der Zusammenfassung steht.
> Paket [[opencivil.bericht]] · [Quelltext](../../opencivil/bericht/zusammenfassung.py)

## VERANTWORTUNG

Je Bauteil -- Platte, Querschnittsanalyse, Grundbruch oder Setzung -- die
gefuehrten Urteile und darunter die still verfehlten; dazu, was ueber der
Nachweistabelle steht (Angaben, Bewehrung, die Faktoren des Grundbruchs oder
die Schichten der Setzung)
und was darunter (Hinweise, stille Maengel). Als Bloecke und Saetze, nicht als
Aussehen: dieselben Stuecke setzt die Oberflaeche
([[opencivil.web.api#zusammenfassungen|opencivil.web.api.zusammenfassungen]]) und der Bericht
([[opencivil.bericht.gliederung#bericht|opencivil.bericht.gliederung.bericht]]), jede Darstellung auf ihre Art.


## WARUM EIN EIGENES MODUL

Vorher baute jede Darstellung ihre Zeilen selbst, und sie liefen schon
auseinander, bevor jemand es merkte: die Oberflaeche nannte einen still
verfehlten Nachweis mit seinem ausgeschriebenen Namen, die Konsole mit dem
langen Urteilsnamen; die eine liess leere Platten weg, die andere nicht; der
Bericht fasste die Nachweise flach zusammen, ohne Platten, sodass zwei
Kombinationen «Feld» zweier Platten nicht zu unterscheiden waren. Welche
Urteile zu einer Platte gehoeren, wie ein Nachweis in der Spalte heisst und
was unter der Tabelle steht, steht jetzt hier und nur hier.

## Inhalt

### Zeile

```python
@dataclass(frozen=True)
class Zeile
```

Ein Urteil, wie es in der Zusammenfassung steht.

- `nachweis: str` – Die Nachweisart ausgeschrieben. Jedes Urteil hat sie: [[opencivil.bericht.zusammenfassung#Zeile|Nachweis.rechne]] stempelt sie auf, aus `LANGNAME` oder dem Thema des Nachweises.
- `fall: str` – Der Fall oder die Lage; leer, wo es keinen gibt.
- `widerstand: Optional[Wert]`
- `einwirkung: Optional[Wert]`
- `urteil: NachweisUrteil` – Fuer alles Weitere: erfuellt, Grad, Begruendung, Hinweis.

#### Zeile.aus

```python
@classmethod
def aus(cls, urteil: NachweisUrteil) -> 'Zeile'
```

#### Zeile.bezeichnung

```python
@property
def bezeichnung(self) -> str
```

Nachweis und Fall in einem -- fuer einen Satz, wo keine Spalten sind.

### Bauteil

```python
@dataclass(frozen=True)
class Bauteil
```

Die Zusammenfassung eines Bauteils -- einer Platte oder einer Analyse.

- `kennung: str`
- `name: str` – Leer fuer die eine Gruppe eines Rechenwerks ohne Bauteile.
- `zeilen: List[Zeile]` – Die gefuehrten Urteile -- je Nachweis mit Lagen nur die schlechtere.
- `stille: List[Zeile]` – Was ausgeschaltet ist und trotzdem nicht aufgeht.
- `art: str = 'platte'` – `platte` oder `querschnittsanalyse` -- was ueber der Tabelle steht, haengt daran.

#### Bauteil.leer

```python
@property
def leer(self) -> bool
```

### Zusammenfassung

```python
@dataclass(frozen=True)
class Zusammenfassung
```

Alle Bauteile, das Gesamturteil und was beim Aufbau auffiel.

- `bauteile: List[Bauteil]`
- `erfuellt: bool` – Ob alle gefuehrten Nachweise aufgehen.
- `gefuehrt: bool` – Ob ueberhaupt einer gefuehrt wurde -- sonst gibt es kein Gesamturteil.
- `warnungen: List[str]`

### zusammenfassen

```python
def zusammenfassen(aufbau: Optional['Aufbau'], loesung: Loesung) -> Zusammenfassung
```

Die Zeilen je Bauteil, in der Reihenfolge der Beschreibung: erst die
Platten, dann die Querschnittsanalysen. Ein Balkensystem fuehrt keine
Nachweise und hat darum hier keine Gruppe -- seine Ergebnisse stehen in
seiner Herleitung.

Die Urteile kommen fertig aus der Loesung: ohne die stillen, und je
Nachweis, der seine Lagen sammelt, nur die schlechteste. Hier zu filtern
hiesse, diese Regel ein zweites Mal zu schreiben.

Ohne Aufbau -- ein Rechenwerk, das keine Bauteile kennt -- stehen alle
Urteile in einer Gruppe ohne Namen. Ein Weg fuer beide Faelle, nicht zwei.

### _groesse

```python
def _groesse(wert: Optional[Wert]) -> Zelle
```

Feste Stellenzahl -- in einer Spalte steht immer dieselbe Groesse.

### nachweistabelle

```python
def nachweistabelle(bauteil: Bauteil) -> TabellenBlock
```

Je gefuehrtes Urteil eine Zeile, in der Folge von [[opencivil.bericht.zusammenfassung#Bauteil|Bauteil.zeilen]].

### hinweise

```python
def hinweise(bauteil: Bauteil) -> List[str]
```

Was unter der Tabelle stehen muss, nach Grund gebuendelt.

Nur was eine Pruefung ausdruecklich meldet (siehe
[[opencivil.core.berechnung#NachweisUrteil|NachweisUrteil.hinweis]]): ein Widerstand von null erklaert sich
nicht von selbst. Eine ganze Tragrichtung ohne Bewehrung laesst aber jeden
ihrer Nachweise aus demselben Grund ausfallen -- sechsmal derselbe Satz
waere keine Erklaerung, sondern eine Wand.

### stiller_hinweis

```python
def stiller_hinweis(zeile: Zeile) -> str
```

Ein ausgeschalteter Nachweis, der nicht aufgeht -- als Satz.

Er steht weder in der Tabelle noch in der Herleitung. Die Begruendung ist
darum das Einzige, was sagt, woran es fehlt.

### angaben

```python
def angaben(aufbau: 'Aufbau', kennung: str, loesung: Loesung) -> Angaben
```

Was ueber der Nachweistabelle eines Bauteils steht: eine Zeile mit den
Angaben und eine Tabelle -- bei der Platte ihre Lagen, bei der
Querschnittsanalyse ihre Staebe und Schubwaende, beim Grundbruch die
Faktoren der Tragfaehigkeitsformel, bei der Setzung die Schichten mit
ihrem Anteil. Die stehen erst nach dem Rechnen fest; darum die Loesung.
Was je Art, sagt [[opencivil.bericht.zusammenfassung#Konstanten|ANGABEN]] -- bis 2026-10-25 wurde die Art durch
Probieren gefunden, ein Register nach dem anderen.

### _befund

```python
def _befund(teil, feld: str, loesung: Loesung)
```

Der Befund seines Nachweises in diesem Feld -- `None`, wenn der Lauf ihn nicht hat.

### kennzahlen

```python
def kennzahlen(aufbau: 'Aufbau', kennung: str, loesung: Loesung) -> List[Tuple[Kennzahl, Wert]]
```

Die Kennzahlen eines Bauteils mit ihren Werten, wie Zusammenfassung und
Bericht sie zeigen -- bei der Platte Bewehrungsmass und Distanzhalter, die
Vergroesserungsfaktoren omega_w und omega_w', die Eckwerte der
Handrechnung und der Querkraftwiderstand bei N_Ed = 0 (Benutzer,
2026-10-16). Welche es gibt und wie sie heissen, sagen ihre Erzeuger
([[opencivil.projekt.aufbau.kern#Bauteil|kennzahlen]]). Was dieser
Lauf nicht gerechnet hat, fehlt: ein Teillauf rechnet nur sein Bauteil.

### kennzahlentabelle

```python
def kennzahlentabelle(zeilen: Sequence[Tuple[Kennzahl, Wert]]) -> TabellenBlock
```

Die Kennzahlen als Tabelle des Berichts: Beschriftung, Zeichen, Wert.

### plattenangaben

```python
def plattenangaben(qs: Plattenquerschnitt) -> GleichungBlock
```

Beton, Dicke und betrachtete Breite -- eine Zeile ueber der Tabelle.

Die Breite in y steht nur da, wenn sie von der eingegebenen abweicht.
Sonst waere es bei jeder Platte dieselbe Zahl zweimal.

### bewehrungsuebersicht

```python
def bewehrungsuebersicht(qs: Plattenquerschnitt, werte: Dict[str, Wert]) -> TabellenBlock
```

Überdeckungen und Lagen, wie man die Platte im Schnitt sieht.

Von oben nach unten gelesen: obere Überdeckung, 4. bis 1. Lage, untere
Überdeckung. Dieselbe Folge wie in der Eingabemaske -- wer beides
nebeneinander hat, soll nicht umdenken müssen.

Grundbewehrung und Zulage stehen in einer Zeile, getrennt durch `+` --
die Lage ist eine Lage, auch wenn sie aus zwei Posten besteht. Zuletzt
die Höhe ihrer Stabachse über der Unterkante, `h - z` aus dem
Lagenaufbau (Benutzer, 2026-10-16); liegen Grund und Zulage verschieden
hoch, beide, getrennt durch `/`.


## Konstanten

- `NACHWEISKOPF = ['Nachweis', 'Bezeichnung', 'Widerstand', 'Einwirkung', Mathe('\\alph…` – Eine Spalte *Urteil* gibt es nicht: sie stand neben dem Erfuellungsgrad und sagte dasselbe noch einmal. *Nachweis* und *Bezeichnung* stehen dagegen getrennt -- vorher stand dort `M-N: Feld`, und zwei Kombinationen gleichen Namens in x und y ergaben zweimal dieselbe Zeile.
- `GRAD_SPALTE = 4` – Welche Spalte den Erfuellungsgrad traegt. Die Oberflaeche hinterlegt genau sie -- zaehlen statt raten, sonst haenge die Einfaerbung an der Reihenfolge der Kopfzeile.
- `STAPEL_SPALTEN = (2, 3)` – Widerstand und Einwirkung: die Oberflaeche setzt sie uebereinander in eine Zelle, der Bericht behaelt beide Spalten.
- `AUSRICHTUNG = 'LLrrr'` – Nachweis und Bezeichnung duerfen umbrechen: mit zwei Formeln daneben liefe die Tabelle im Bericht sonst ueber den Rand.
- `ANGABEN = {'platte': lambda teil, loesung: (plattenangaben(teil.objekt), bewehr…` – Je Bauteilart mit Nachweisen, was ueber ihrer Tabelle steht -- nach dem Namen der Art. Ein Balkensystem hat keine Nachweise und keine Tabelle.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.rechenwerk]]
- [[opencivil.core.wert]]
- [[opencivil.geotechnik.grundbruch]]
- [[opencivil.geotechnik.setzung]]
- [[opencivil.projekt]]
- [[opencivil.querschnitt.platte]]

## Gebraucht von

- [[opencivil.bericht.gliederung]]
- [[opencivil.bericht.konsole]]
- [[opencivil.ergebnis]]
- [[opencivil.web.api]]
