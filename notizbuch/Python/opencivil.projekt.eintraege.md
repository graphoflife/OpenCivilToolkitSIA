---
erzeugt: c7802508903c
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/eintraege.py
> die Teile einer Projektbeschreibung.
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/eintraege.py)

## VERANTWORTUNG

Material, Bewehrungsposten und -lagen, Buegel, Lastfaelle -- jedes als
Datenklasse, die sich als JSON speichern und wieder einlesen laesst. Gelesen
und geprueft wird jeder Eintrag ueber seine Felder: was eines annehmen darf,
steht an ihm ([[opencivil.projekt.lesen]]).

Die Platte, die diese Teile zusammenhaelt, steht in
[[opencivil.projekt.platte]]; das ganze Projekt in
[[opencivil.projekt.projekt]].

## Inhalt

### Beschreibung

```python
@dataclass
class Beschreibung
```

Gemeinsamer Boden aller Beschreibungsteile.

Der Weg nach draussen sind die Felder der Datenklasse, nicht mehr. Von
Hand geschrieben war `als_dict` ein Spiegel, der nur stimmt, solange
jemand ihn nachfuehrt -- neun Stueck, zusammen gut hundert Zeilen, deren
ganze Aufgabe war, identisch zu etwas zu sein, das die Standardbibliothek
schon kann.

Seit der Zwischenspeicher ([[opencivil.web.speicher]]) seinen Abdruck
daraus bildet, waere ein vergessenes Feld auch nicht mehr bloss eine
unvollstaendige Datei: die Aenderung faende sich im Abdruck nicht wieder,
das Bauteil gaelte als unveraendert, und die Oberflaeche zeigte eine alte
Zahl. Von allen Fehlern der schlimmste -- und mit dieser Zeile gibt es ihn
nicht.

Der Weg hinein ebenso: [[opencivil.projekt.lesen#lesen|lesen]] liest
jeden Eintrag aus seinen Feldern, streng, und prueft ihn mit
[[opencivil.projekt.lesen#felder_pruefen|felder_pruefen]] -- was ein Feld annehmen
darf, steht an ihm. Von Hand waren es 39 Leser, jeder mit eigenen
Vorgaben, Pruefungen und alten Formaten, und die Fassade ging an ihnen
vorbei: ein «festt» aus Python wurde still zur Feder (2026-10-16).

`BEZEICHNUNG`, wo es sie gibt, nennt den Eintrag in Meldungen so wie
die Oberflaeche: «Platte 'Decke'».

Ein Wahlfeld haelt das Mitglied seiner Wahl; wer Text zuweist -- die
Datei, der Konstruktor, die Fassade --, bekommt hier das Mitglied
([[opencivil.projekt.lesen#wahl_aus_text|wahl_aus_text]]).

Was ueber mehrere Felder gilt, steht in [[opencivil.projekt.eintraege#Beschreibung.regeln|regeln]] -- geprueft vor
dem Rechnen, nach den Bereichen der Felder
([[opencivil.projekt.lesen#inhalt_pruefen|inhalt_pruefen]]).

#### Beschreibung.regeln

```python
def regeln(self, wo: str) -> None
```

Die Regeln ueber mehrere Felder -- ohne eigene keine. `wo` nennt den Eintrag.

#### Beschreibung.als_dict

```python
def als_dict(self) -> dict
```

#### Beschreibung.aus_dict

```python
@classmethod
def aus_dict(cls, roh: Mapping[str, Any], wo: Optional[str]=None) -> Any
```

Ein Eintrag aus der Datei -- gelesen und geprueft, siehe [[opencivil.projekt.lesen]].

### MaterialEintrag

```python
@dataclass
class MaterialEintrag(Beschreibung)
```

Ein Baustoff, wie ihn die Oberflaeche beschreibt: eine Normsorte nach SIA,
die bleibt, wie sie ist, oder ein eigenes Material mit einer Sorte als
Vorlage.

- `BEZEICHNUNG = 'Material'`
- `kennung: str`
- `art: Baustoffart`
- `sorte: str` – Die Normsorte -- bei einem eigenen Material die Vorlage seiner Kennwerte.
- `name: str = ''`
- `eigenstaendig: bool = False` – False = Normsorte, Kennwerte gesperrt, Name = Sorte -- nie aenderbar. True = eigenes Material, aenderbar, mit eigenem Namen (BE1, S1 ...).
- `abweichungen: Dict[str, float] = field(default_factory=dict)`
- `ueberschreibungen: Dict[str, float] = field(default_factory=dict)`

#### MaterialEintrag.anzeigename

```python
@property
def anzeigename(self) -> str
```

#### MaterialEintrag.ist_normsorte

```python
@property
def ist_normsorte(self) -> bool
```

#### MaterialEintrag.pruefen

```python
def pruefen(self) -> None
```

Sorte und Name -- die Materialart prueft ihr Feld.

### PostenEintrag

```python
@dataclass
class PostenEintrag(Beschreibung)
```

Grundbewehrung oder Zulage einer Lage.

- `durchmesser: float = 0.0` – in mm; 0 bedeutet: nicht vorhanden.
- `abstand: Optional[float] = 150.0` – Teilung in mm. Genau eines von `abstand` und `anzahl` ist gesetzt.
- `anzahl: Optional[float] = None`

#### PostenEintrag.vorhanden

```python
@property
def vorhanden(self) -> bool
```

#### PostenEintrag.pruefen

```python
def pruefen(self, wo: str) -> None
```

Ein Posten mit Durchmesser braucht eine Teilung oder eine Stabzahl
groesser als null. Bis 2026-10-16 hiess eine Teilung von null still
«kein Stab»: die Maske zeigte ⌀16, gerechnet wurde ohne. Ohne
Durchmesser ist der Posten leer, was sonst auch dasteht.

#### PostenEintrag.als_posten

```python
def als_posten(self) -> Bewehrungsposten
```

#### PostenEintrag.je_meter

```python
def je_meter(self, b: float=1000.0) -> float
```

Bewehrungsquerschnitt in mm²/m. Ueber die Teilung haengt er an keiner
Breite; bei einer Stabzahl liegen die Staebe auf der Breite `b` (mm).

### LageEintrag

```python
@dataclass
class LageEintrag(Beschreibung)
```

Eine der vier Lagen.

- `stahl: str = ''`
- `grund: PostenEintrag = field(default_factory=PostenEintrag)`
- `zulage: PostenEintrag = field(default_factory=lambda: PostenEintrag(durchmesser=0.0))`
- `unguenstig: bool = True` – Ob die inneren Kanten von Grundbewehrung und Zulage fluchten -- siehe [[opencivil.querschnitt.platte#Bewehrungslage|opencivil.querschnitt.platte.Bewehrungslage]].

#### LageEintrag.vorhanden

```python
@property
def vorhanden(self) -> bool
```

### ObergrenzeEintrag

```python
@dataclass
class ObergrenzeEintrag(Beschreibung)
```

Die Obergrenze der automatischen Bewehrung: keine Lage bekommt von der
Suche mehr Querschnitt als Grund und Zulage hier zusammen.

Eingegeben wie eine Lage, je als ⌀ @ Teilung -- es zaehlt aber nur die
Summe in mm²/m. Wie die Suche sie auf Grund und Zulage verteilt, ist frei:
bei ⌀26@150 + ⌀20@150 (5634 mm²/m) darf eine Lage auch ⌀30 + ⌀12 tragen.
Beide ohne Durchmesser heisst: keine Obergrenze.

- `grund: PostenEintrag = field(default_factory=lambda: PostenEintrag(durchmesser=30.0))`
- `zulage: PostenEintrag = field(default_factory=lambda: PostenEintrag(durchmesser=0.0))`

#### ObergrenzeEintrag.je_meter

```python
@property
def je_meter(self) -> float
```

Die Obergrenze in mm²/m -- unendlich, wenn keine gesetzt ist.

### QuerkraftbewehrungEintrag

```python
@dataclass
class QuerkraftbewehrungEintrag(Beschreibung)
```

Die Bügel einer Platte -- ein Raster, ein Durchmesser, zwei Teilungen.

In y darf statt der Teilung eine Stabzahl über die betrachtete Breite
stehen; in x nicht. Siehe
[[opencivil.querschnitt.platte#Querkraftbewehrung|opencivil.querschnitt.platte.Querkraftbewehrung]].

- `durchmesser: float = 0.0` – in mm; 0 bedeutet: keine Querkraftbewehrung.
- `stahl: str = ''`
- `abstand_x: Optional[float] = 200.0`
- `abstand_y: Optional[float] = 200.0`
- `anzahl_y: Optional[float] = None`
- `alpha_min: int = ALPHA_MIN`
- `alpha_max: int = ALPHA_MAX`

#### QuerkraftbewehrungEintrag.vorhanden

```python
@property
def vorhanden(self) -> bool
```

Ob Buegel liegen -- das sagt allein der Durchmesser. Eine Teilung von
null heisst nicht «keine Buegel», sondern ist ein Fehler, und
[[opencivil.projekt.eintraege#QuerkraftbewehrungEintrag.pruefen|pruefen]] sagt es.

#### QuerkraftbewehrungEintrag.ueber_teilung_y

```python
@property
def ueber_teilung_y(self) -> bool
```

In y eine Teilung -- sonst eine Stabzahl. Wie in der Maske: es zaehlt, was dasteht.

#### QuerkraftbewehrungEintrag.pruefen

```python
def pruefen(self, wo: str) -> None
```

Was nicht stimmen kann, soll als Satz beim Benutzer ankommen.

#### QuerkraftbewehrungEintrag.als_bewehrung

```python
def als_bewehrung(self, stahl: Baustoff) -> Querkraftbewehrung
```

Die Buegel fuer den Querschnitt -- erst nach [[opencivil.projekt.eintraege#QuerkraftbewehrungEintrag.pruefen|pruefen]].

### neigungen_pruefen

```python
def neigungen_pruefen(alpha_min: int, alpha_max: int, wo: str) -> None
```

Die Grenzen der Druckfeldneigung -- bei den Buegeln der Platte wie bei den
Schubwaenden des gezeichneten Querschnitts.

### druckfeld_pruefen

```python
def druckfeld_pruefen(k_c: float, wo: str) -> None
```

Die Abminderung der Druckdiagonalen -- eine Festigkeit mal k_c, also groesser als null.

### x_d_max_pruefen

```python
def x_d_max_pruefen(x_d_max: float, wo: str) -> None
```

Die Grenze der bezogenen Druckzonenhoehe im Duktilitaetsnachweis.

### KnickEintrag

```python
@dataclass
class KnickEintrag(Beschreibung)
```

Ein Knicknachweis: Druckkraft, Moment 1. Ordnung, Laenge, Knicklaenge.

Nur in x-Richtung -- eine Knicklaenge gehoert zu einer Tragrichtung, und
in y waere die Breite der Platte die Laenge.

- `name: str`
- `N_Ed: float = 0.0` – in kN, Druck negativ.
- `M_Ed_1: float = 0.0`
- `laenge: float = bereich(3.0, heisst='Systemlänge', einheit=M, ueber=0.0)` – Systemlaenge in m -- geht in die Schiefstellung ein. Bis 2026-10-16 rechnete eine Laenge von null und hiess «erfuellt».
- `knicklaenge: float = bereich(3.0, heisst='Knicklänge', einheit=M, ueber=0.0)` – Knicklaenge in m.
- `aktiv: bool = True` – Ob der Fall gerechnet wird. Ausgeschaltet bleibt er stehen -- eine geloeschte Zeile muesste man neu eintippen, um sie wieder anzusehen.

### VerformungsfallEintrag

```python
@dataclass
class VerformungsfallEintrag(Beschreibung)
```

Ein Verformungsfall: die Durchbiegung, mit der Steifigkeit E_cm
ermittelt, ihre Spannweite und die Seite, die er zieht.

Wie ein Knickfall nur in x-Richtung.

- `name: str`
- `w: float = bereich(0.0, heisst='Durchbiegung w', einheit=MM, ab=0.0)` – Durchbiegung in mm, mit E_cm ermittelt -- ein Betrag.
- `laenge: float = bereich(5.0, heisst='Spannweite L', einheit=M, ueber=0.0)` – Spannweite L in m -- der Grenzwert ist L/350.
- `zugseite: str = einer_von(ZUGSEITEN, 'unten')` – `unten` im Feld, `oben` am Kragarm -- welches rho gilt.
- `aktiv: bool = True` – Ob der Fall gerechnet wird. Ausgeschaltet bleibt er stehen.

### VerformungEintrag

```python
@dataclass
class VerformungEintrag(Beschreibung)
```

Der Verformungsnachweis einer Platte: die Kriechzahl seines
Vergroesserungsfaktors und die Faelle.

phi gilt fuer die Platte und nicht je Fall -- der Faktor wird je Seite
einmal gerechnet ([[opencivil.nachweis.verformung]]).

- `kriechzahl: float = bereich(VERFORMUNG_KRIECHZAHL, heisst='Kriechzahl φ', ab=0.0)` – phi im Vergroesserungsfaktor omega_w, Vorgabe 2.
- `faelle: List[VerformungsfallEintrag] = field(default_factory=list)`

#### VerformungEintrag.fall

```python
def fall(self, name: str, *, w: float, laenge: float, zugseite: str=VerformungsfallEintrag.zugseite) -> VerformungsfallEintrag
```

Einen Fall anfuegen -- w in mm, die Spannweite in m.

### abgeleiteter_fallname

```python
def abgeleiteter_fallname(name: str, anteil: float) -> str
```

Wie ein aus der Tragsicherheit abgeleiteter Lastfall heisst.

Die eine Stelle dafuer: der Aufbau benennt die Faelle so, und die
Namenspruefung muss genau denselben Namen bilden, um einen gleichlautenden
eigenen Fall zu erkennen. `70.0` wird zu «70 %», `62.5` zu «62.5 %».

### SpannungsfallEintrag

```python
@dataclass
class SpannungsfallEintrag(Beschreibung)
```

Eine Auswertung am Querschnitt -- kein Nachweis.

Es wird nichts gegen etwas gehalten: kein Erfuellungsgrad, kein Urteil.
Gefragt wird, was im Querschnitt geschieht, und je nach [[opencivil.projekt.eintraege#SpannungsfallEintrag|art]] von
der einen oder der anderen Seite -- aus Schnittgroessen, aus Dehnungen,
als Momenten-Kruemmungs- oder als Normalkraft-Dehnungs-Linie.

Womit gerechnet wird, waehlt jede Analyse fuer sich: die Kriechzahl, den
Wertesatz und die Rechenart ([[opencivil.nachweis.rechenwahl#Rechenwahl|Rechenwahl]]).

- `name: str`
- `art: Analyseart = Analyseart.SCHNITTGROESSEN` – Was gefragt wird -- siehe [[opencivil.spannungsanalyse#Analyseart|Analyseart]].
- `richtung: Richtung = Richtung.X` – Welche Bewehrung zaehlt. Hier keine Wahl `beide`: ein Bild zeigt einen Querschnitt, und der liegt in einer Richtung.
- `N_Ed: float = 0.0` – in kN, Zug positiv -- fuer `schnittgroessen` und `moment_kruemmung`.
- `M_Ed: float = 0.0` – in kNm -- fuer `schnittgroessen` und `normalkraft_dehnung`.
- `eps_oben: float = -1.0`
- `eps_unten: float = 2.0` – Randdehnungen in Promille -- nur fuer `dehnungen`.
- `kriechzahl: float = bereich(0.0, heisst='Kriechzahl φ', ab=0.0)` – Die Kriechzahl φ dieser Analyse.
- `werkstoffsatz: Werkstoffsatz = Werkstoffsatz.BEMESSUNG` – `bemessung` (f_cd, f_yd) oder `charakteristisch` (f_ck, f_yk).
- `rechenart: Rechenart = einer_von(FASERARTEN, Rechenart.PARABEL)` – `block` oder `parabel` -- siehe [[opencivil.nachweis.rechenwahl#Rechenart|Rechenart]]. Die Handrechnung gibt es hier nicht ([[opencivil.nachweis.rechenwahl#Konstanten|FASERARTEN]]).
- `aktiv: bool = True`

#### SpannungsfallEintrag.wahl

```python
@property
def wahl(self) -> Rechenwahl
```

Womit die Analyse rechnet.

### GebrauchsfallEintrag

```python
@dataclass
class GebrauchsfallEintrag(Beschreibung)
```

Eine Schnittgroessenkombination unter Gebrauchslast.

Wie [[opencivil.projekt.eintraege#KombinationEintrag|KombinationEintrag]], aber ohne Querkraft: begrenzt wird die
Stahlspannung, und dafuer zaehlen Moment und Normalkraft. Ob der Fall
haeufig oder quasi-staendig ist, sagt die Liste, in der er steht.

- `name: str`
- `M_Ed: float = 0.0`
- `N_Ed: float = 0.0`
- `aktiv: bool = True` – Ob dieser Lastfall gerechnet wird. Ausgeschaltet bleibt er stehen.

### eindeutig

```python
def eindeutig(namen: Iterable[str], wo: str, was: str) -> None
```

Fallnamen muessen je Liste eindeutig sein -- auch als Kennung.

Die Nachweise legen ihre Ergebniswerte unter dem Fallnamen ab -- M-N,
Querkraft und Stahlspannung alle drei. Zwei Kombinationen gleichen
Namens fielen darum auf einen Eintrag zusammen: der zweite ueberschrieb
den ersten, und in der Tabelle fehlte eine Zeile. Kein Fehler, keine
Warnung, eine Zahl weniger.

Verschiedene Namen koennen dieselbe Kennung ergeben: «Wand A» und
«Wand-A» werden beide zu «Wand_A» ([[opencivil.core.wert#kennung_aus|kennung_aus]]). Das Rechenwerk
wiese den zweiten zurueck, aber mit einer Meldung ueber Wert-IDs, die an
der Maske niemand versteht. Bis 2026-10-17 pruefte das nur drei der neun
Listen.

Gemeldet statt umbenannt: welcher der beiden gemeint war, weiss nur der
Benutzer, und ein automatisch angehaengtes «(2)» stuende danach in seinem
Bericht. Gefragt wird vor dem Rechnen, nicht beim Oeffnen: zwei gleiche
Namen sind schnell getippt, und ein Projekt, das sich darum nicht mehr
oeffnen liesse, waere schlimmer als eine Meldung beim Rechnen.

### RechenwahlEintrag

```python
@dataclass
class RechenwahlEintrag(Beschreibung)
```

Womit ein Nachweis-Kapitel rechnet: Kriechzahl, Wertesatz, Rechenart --
siehe [[opencivil.nachweis.rechenwahl#Rechenwahl|Rechenwahl]]. So steht sie in
der Tragsicherheit.

Jedes andere Kapitel hat seine Unterklasse, und welche Rechenarten es
anbietet, steht an deren Feld: der Leser prueft es wie jede Wahl. Bis
2026-10-17 prueften fuenf Aufrufer je mit ihrer Liste nach dem Lesen.
Die Kriechzahl des Vergroesserungsfaktors gehoert dem Verformungsnachweis
([[opencivil.projekt.eintraege#VerformungEintrag|VerformungEintrag]]).

- `kriechzahl: float = bereich(0.0, heisst='Kriechzahl φ', ab=0.0)`
- `werkstoffsatz: Werkstoffsatz = Werkstoffsatz.BEMESSUNG`
- `rechenart: Rechenart = einer_von(RECHENARTEN, Rechenart.HANDRECHNUNG)`

#### RechenwahlEintrag.wahl

```python
@property
def wahl(self) -> Rechenwahl
```

Was der Kern daraus rechnet.

### Gebrauchswahl

```python
@dataclass
class Gebrauchswahl(RechenwahlEintrag)
```

Die Stahlspannungen: elastisch, mit charakteristischen Werten -- dazu die Rechenarten der Tragsicherheit.

- `werkstoffsatz: Werkstoffsatz = Werkstoffsatz.CHARAKTERISTISCH`
- `rechenart: Rechenart = einer_von(SPANNUNGSARTEN, Rechenart.ELASTISCH)`

### KnickVerformungswahl

```python
@dataclass
class KnickVerformungswahl(RechenwahlEintrag)
```

Die Ausmitte e_2d beim Knicken: nur praezise ohne Vereinfachung.

- `rechenart: Rechenart = einer_von(VERFORMUNGSARTEN, Rechenart.PARABEL)`

### KnickWiderstandswahl

```python
@dataclass
class KnickWiderstandswahl(RechenwahlEintrag)
```

Der Widerstand beim Knicken: ueber die Fasern, vorgegeben die
0.85·x-Vereinfachung. Bis 2026-10-12 war es die Handrechnung, die es
dort nicht mehr gibt; die Vereinfachung kommt ihr am naechsten.

- `rechenart: Rechenart = einer_von(FASERARTEN, Rechenart.BLOCK)`

### Gebrauchsliste

```python
@dataclass
class Gebrauchsliste(Beschreibung)
```

Die Lastfaelle eines Stahlspannungsnachweises: eigene und abgeleitete.

Eine Platte hat zwei davon, eine haeufige und eine quasi-staendige. Beide
werden gleich gebildet -- die eigenen Faelle, dazu die
Tragsicherheitseinwirkungen mal `anteil` Prozent -- und unterscheiden
sich nur darin, wogegen der Nachweis sie haelt.

Frueher waren das sechs flache Felder an der Platte, und jede Stelle, die
damit arbeitete, setzte die drei zusammengehoerigen wieder ueber ihre
Namen zusammen. Welche Liste haeufig und welche quasi-staendig ist, sagt
das Feld der Platte, in dem sie steht; die Liste selbst weiss es nicht.

Der gezeichnete Querschnitt hat dieselbe Liste mit anderen Faellen
([[opencivil.projekt.querschnittsanalyse#QAGebrauchsliste|QAGebrauchsliste]]): was
darin steht ([[opencivil.projekt.eintraege#Gebrauchsliste|FALL]]), welche Rechenarten sie anbietet (der Typ
ihres Feldes [[opencivil.projekt.eintraege#Gebrauchsliste|wahl]]) und wie ihr Bauteil heisst, wo ein Fall ohne
Bauteil gelesen wird ([[opencivil.projekt.eintraege#Gebrauchsliste|BAUTEIL]]).

- `FALL = GebrauchsfallEintrag`
- `BAUTEIL = 'Platte'`
- `anteil: float = bereich(heisst='Anteil aus der Tragsicherheit', einheit=PROZENT, uebe…` – Welcher Anteil der Tragsicherheitseinwirkungen abgeleitet wird, in %. Null ergaebe Lastfaelle ohne Last -- ein Nachweis, der immer aufgeht und nichts sagt. Ueber hundert waere keine Gebrauchslast mehr. Gemeldet statt begrenzt: wer 700 statt 70 tippt, soll es erfahren und nicht mit 100 weiterrechnen.
- `aus_tragsicherheit: bool = False` – Ob die abgeleiteten Faelle *gefuehrt* werden. Gebildet werden sie immer; ausgeschaltet rechnen sie still mit. Der Anteil ist eine bequeme Abschaetzung und keine Norm, darum stehen die Faelle nur auf Verlangen in der Tabelle.
- `faelle: List[GebrauchsfallEintrag] = field(default_factory=list)` – Eigene Lastfaelle -- neben den abgeleiteten, nicht statt ihrer.
- `wahl: Gebrauchswahl = field(default_factory=Gebrauchswahl)` – Womit die Stahlspannung gerechnet wird -- Vorgabe elastisch, charakteristisch.

#### Gebrauchsliste.lastfall

```python
def lastfall(self, name: str, **werte: float)
```

Einen eigenen Lastfall anfuegen -- kNm und kN, Zug positiv.

#### Gebrauchsliste.namen_pruefen

```python
def namen_pruefen(self, wo: str, kombinationen: List[Any], wort: str) -> None
```

Die Namen dieser Liste, vor dem Rechnen (siehe [[opencivil.projekt.eintraege#eindeutig|eindeutig]]). Je
Liste fuer sich: die beiden Listen landen in getrennten Nachweisen und
damit in getrennten ID-Raeumen, ein Fall «Dauer» darf in beiden stehen.
`kombinationen` sind die Faelle der Tragsicherheit, aus denen
abgeleitet wird -- ihre eigenen Namen hat das Bauteil schon geprueft.
`wo` nennt das Bauteil.

### KombinationEintrag

```python
@dataclass
class KombinationEintrag(Beschreibung)
```

Eine zu pruefende Schnittgroessenkombination.

- `name: str`
- `M_Ed: float = 0.0`
- `N_Ed: float = 0.0`
- `V_Ed: float = 0.0` – Querkraft in kN/m -- für den Querkraftnachweis.
- `art: Erfuellungsart = Erfuellungsart.AUTOMATISCH`
- `aktiv: bool = True` – Ob dieser Lastfall gerechnet wird. Ausgeschaltet bleibt er stehen.


## Konstanten

- `EIGENE_VORSILBE = {'beton': 'BE', 'betonstahl': 'S'}` – Womit die Namen eigener Materialien beginnen: BE1, BE2 ... beim Beton, S1, S2 ... beim Betonstahl (Benutzer, 2026-10-16).
- `HAEUFIG_ANTEIL = 70.0` – Anteil der Tragsicherheitseinwirkungen, der als haeufiger Lastfall gilt -- in Prozent, wie die Maske ihn zeigt. Eine Vorgabe, einstellbar je Platte.
- `QUASISTAENDIG_ANTEIL = 60.0` – Dasselbe fuer die quasi-staendigen Lastfaelle.

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.wert]]
- [[opencivil.material.basis]]
- [[opencivil.nachweis.biegung_normalkraft]]
- [[opencivil.nachweis.duktilitaet]]
- [[opencivil.nachweis.querschnittsloeser]]
- [[opencivil.nachweis.rechenwahl]]
- [[opencivil.nachweis.verformung]]
- [[opencivil.projekt.lesen]]
- [[opencivil.querschnitt.platte]]
- [[opencivil.spannungsanalyse]]

## Gebraucht von

- [[opencivil.projekt]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.balkensystem]]
- [[opencivil.projekt.grundbruch]]
- [[opencivil.projekt.platte]]
- [[opencivil.projekt.projekt]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.projekt.skript]]
- [[opencivil.web.api]]
