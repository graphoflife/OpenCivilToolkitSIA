---
erzeugt: 29a75bd7fe20
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/eintraege.py
> die Teile einer Projektbeschreibung.
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/eintraege.py)

## VERANTWORTUNG

Material, Bewehrungsposten und -lagen, Buegel, Lastfaelle -- jedes als
Datenklasse, die sich als JSON speichern und wieder einlesen laesst. Dazu die
Leser, mit denen `aus_dict` Zahlen, Pflichtfelder, Schalter und alte
Dateiformate aufnimmt.

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

Der Weg hinein bleibt je Klasse von Hand: dort stehen Vorgaben, alte
Dateiformate und Pruefungen, und das ist Arbeit und kein Spiegel.

#### Beschreibung.als_dict

```python
def als_dict(self) -> dict
```

### MaterialEintrag

```python
@dataclass
class MaterialEintrag(Beschreibung)
```

Ein Baustoff, wie ihn die Oberflaeche beschreibt: eine Normsorte nach SIA,
die bleibt, wie sie ist, oder ein eigenes Material mit einer Sorte als
Vorlage.

- `kennung: str`
- `art: str` – `beton` oder `betonstahl`.
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

#### MaterialEintrag.aus_dict

```python
@classmethod
def aus_dict(cls, d: Mapping[str, Any]) -> 'MaterialEintrag'
```

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

#### PostenEintrag.aus_dict

```python
@classmethod
def aus_dict(cls, d: Mapping[str, Any]) -> 'PostenEintrag'
```

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

#### LageEintrag.aus_dict

```python
@classmethod
def aus_dict(cls, d: Mapping[str, Any]) -> 'LageEintrag'
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

#### ObergrenzeEintrag.aus_dict

```python
@classmethod
def aus_dict(cls, d: Mapping[str, Any]) -> 'ObergrenzeEintrag'
```

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

#### QuerkraftbewehrungEintrag.aus_dict

```python
@classmethod
def aus_dict(cls, d: Mapping[str, Any]) -> 'QuerkraftbewehrungEintrag'
```

#### QuerkraftbewehrungEintrag.pruefen

```python
def pruefen(self, wo: str) -> None
```

Was nicht stimmen kann, soll als Satz beim Benutzer ankommen.

#### QuerkraftbewehrungEintrag.als_bewehrung

```python
def als_bewehrung(self, stahl: Optional[Baustoff]) -> Querkraftbewehrung
```

Die Buegel fuer den Querschnitt -- erst nach [[opencivil.projekt.eintraege#QuerkraftbewehrungEintrag.pruefen|pruefen]].

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
- `laenge: float = 3.0` – Systemlaenge in m -- geht in die Schiefstellung ein.
- `knicklaenge: float = 3.0` – Knicklaenge in m.
- `aktiv: bool = True` – Ob der Fall gerechnet wird. Ausgeschaltet bleibt er stehen -- eine geloeschte Zeile muesste man neu eintippen, um sie wieder anzusehen.

#### KnickEintrag.aus_dict

```python
@classmethod
def aus_dict(cls, d: Mapping[str, Any]) -> 'KnickEintrag'
```

### VerformungsfallEintrag

```python
@dataclass
class VerformungsfallEintrag(Beschreibung)
```

Ein Verformungsfall: die Durchbiegung, mit der Steifigkeit E_cm
ermittelt, ihre Spannweite und die Seite, die er zieht.

Wie ein Knickfall nur in x-Richtung.

- `name: str`
- `w: float = 0.0` – Durchbiegung in mm, mit E_cm ermittelt -- ein Betrag.
- `laenge: float = 5.0` – Spannweite L in m -- der Grenzwert ist L/350.
- `zugseite: str = 'unten'` – `unten` im Feld, `oben` am Kragarm -- welches rho gilt.
- `aktiv: bool = True` – Ob der Fall gerechnet wird. Ausgeschaltet bleibt er stehen.

#### VerformungsfallEintrag.zahlen_pruefen

```python
def zahlen_pruefen(self, wo: str) -> None
```

w und L -- erst beim Bauen gefragt, wie die Masse der Platte: eine
abgelegte Platte mit L = 0 soll sich oeffnen und korrigieren lassen.

#### VerformungsfallEintrag.aus_dict

```python
@classmethod
def aus_dict(cls, d: Mapping[str, Any]) -> 'VerformungsfallEintrag'
```

### VerformungEintrag

```python
@dataclass
class VerformungEintrag(Beschreibung)
```

Der Verformungsnachweis einer Platte: die Kriechzahl seines
Vergroesserungsfaktors und die Faelle.

phi gilt fuer die Platte und nicht je Fall -- der Faktor wird je Seite
einmal gerechnet ([[opencivil.nachweis.verformung]]).

- `kriechzahl: float = VERFORMUNG_KRIECHZAHL` – phi im Vergroesserungsfaktor omega_w, Vorgabe 2.
- `faelle: List[VerformungsfallEintrag] = field(default_factory=list)`

#### VerformungEintrag.fall

```python
def fall(self, name: str, *, w: float, laenge: float, zugseite: str=VerformungsfallEintrag.zugseite) -> VerformungsfallEintrag
```

Einen Fall anfuegen -- w in mm, die Spannweite in m.

#### VerformungEintrag.pruefen

```python
def pruefen(self, bauteil: str) -> None
```

#### VerformungEintrag.aus_dict

```python
@classmethod
def aus_dict(cls, d: Mapping[str, Any], *, kriechzahl_alt: float=VERFORMUNG_KRIECHZAHL) -> 'VerformungEintrag'
```

`kriechzahl_alt`: das phi, das bis 2026-10-16 an der Platte stand.

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
In Dateien von vor 2026-10-09 fehlt die Kriechzahl oder steht leer --
sie hiess dort «die der Platte», und das bleibt sie beim Lesen
(`kriechzahl_alt`). Die Rechenart hiess dort `betongesetz`.

- `name: str`
- `art: str = 'schnittgroessen'` – `schnittgroessen`, `dehnungen`, `moment_kruemmung` oder `normalkraft_dehnung` -- siehe [[opencivil.spannungsanalyse#Analyseart|Analyseart]].
- `richtung: str = 'x'` – Welche Bewehrung zaehlt. Hier keine Wahl `beide`: ein Bild zeigt einen Querschnitt, und der liegt in einer Richtung.
- `N_Ed: float = 0.0` – in kN, Zug positiv -- fuer `schnittgroessen` und `moment_kruemmung`.
- `M_Ed: float = 0.0` – in kNm -- fuer `schnittgroessen` und `normalkraft_dehnung`.
- `eps_oben: float = -1.0`
- `eps_unten: float = 2.0` – Randdehnungen in Promille -- nur fuer `dehnungen`.
- `kriechzahl: float = 0.0` – Die Kriechzahl φ dieser Analyse.
- `werkstoffsatz: str = WERKSTOFFSAETZE[0]` – `bemessung` (f_cd, f_yd) oder `charakteristisch` (f_ck, f_yk).
- `rechenart: str = Rechenart.PARABEL.value` – `block` oder `parabel` -- siehe [[opencivil.nachweis.rechenwahl#Rechenart|Rechenart]]. Die Handrechnung gibt es hier nicht ([[opencivil.nachweis.rechenwahl#Konstanten|FASERARTEN]]); eine Datei von vor 2026-10-12, die sie noch waehlt, liest sich als `block`.
- `aktiv: bool = True`

#### SpannungsfallEintrag.aus_dict

```python
@classmethod
def aus_dict(cls, d: Mapping[str, Any], *, kriechzahl_alt: float=0.0) -> 'SpannungsfallEintrag'
```

`kriechzahl_alt` gilt, wo die Kriechzahl fehlt -- siehe Klasse.

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

#### GebrauchsfallEintrag.aus_dict

```python
@classmethod
def aus_dict(cls, d: Mapping[str, Any], wort: str='häufige') -> 'GebrauchsfallEintrag'
```

`wort` nennt die Liste in der Meldung -- «häufige» oder «quasi-ständige».

### eindeutig

```python
def eindeutig(faelle, platte: str, was: str, *, bauteil: str='Platte') -> None
```

Lastfallnamen muessen je Platte und Liste eindeutig sein.

Die Nachweise legen ihre Ergebniswerte unter dem Fallnamen ab -- M-N,
Querkraft und Stahlspannung alle drei. Zwei Kombinationen gleichen
Namens fielen darum auf einen Eintrag zusammen: der zweite ueberschrieb
den ersten, und in der Tabelle fehlte eine Zeile. Kein Fehler, keine
Warnung, eine Zahl weniger.

Gemeldet statt umbenannt: welcher der beiden gemeint war, weiss nur der
Benutzer, und ein automatisch angehaengtes «(2)» stuende danach in seinem
Bericht.

### RechenwahlEintrag

```python
@dataclass
class RechenwahlEintrag(Beschreibung)
```

Womit ein Nachweis-Kapitel rechnet: Kriechzahl, Wertesatz, Rechenart --
siehe [[opencivil.nachweis.rechenwahl#Rechenwahl|Rechenwahl]].

Jedes Kapitel hat seine eigene; die Kriechzahl des Vergroesserungsfaktors
gehoert dem Verformungsnachweis ([[opencivil.projekt.eintraege#VerformungEintrag|VerformungEintrag]]). In einer
Datei von vor 2026-10-09 fehlt die Wahl -- dann gilt, was damals fest
galt: die Rechenart und der Wertesatz des Kapitels (`vorgabe`) und das
phi, das damals an der Platte stand (`kriechzahl_alt`).

- `kriechzahl: float = 0.0`
- `werkstoffsatz: str = WERKSTOFFSAETZE[0]`
- `rechenart: str = Rechenart.HANDRECHNUNG.value`

#### RechenwahlEintrag.gebrauch

```python
@classmethod
def gebrauch(cls) -> 'RechenwahlEintrag'
```

Die Stahlspannungen: elastisch, mit charakteristischen Werten.

#### RechenwahlEintrag.knicken_verformung

```python
@classmethod
def knicken_verformung(cls) -> 'RechenwahlEintrag'
```

Die Ausmitte e_2d: praezise ohne Vereinfachung, mit Bemessungswerten.

#### RechenwahlEintrag.knicken_widerstand

```python
@classmethod
def knicken_widerstand(cls) -> 'RechenwahlEintrag'
```

Der Widerstand beim Knicken: die 0.85·x-Vereinfachung, mit
Bemessungswerten. Bis 2026-10-12 war es die Handrechnung, die es dort
nicht mehr gibt; die Vereinfachung kommt ihr am naechsten.

#### RechenwahlEintrag.wahl

```python
@property
def wahl(self) -> Rechenwahl
```

Was der Kern daraus rechnet.

#### RechenwahlEintrag.pruefen

```python
def pruefen(self, wo: str, arten=RECHENARTEN) -> None
```

Was es nicht gibt, meldet sich -- `arten` sagt, welche Rechenarten gelten.

#### RechenwahlEintrag.aus_dict

```python
@classmethod
def aus_dict(cls, d: Optional[Mapping[str, Any]], *, vorgabe: Optional['RechenwahlEintrag']=None, kriechzahl_alt: Optional[float]=None, wo: str='Rechenwahl', arten=RECHENARTEN) -> 'RechenwahlEintrag'
```

Fehlt `d` oder ein Feld darin, gilt `vorgabe` -- und fuer phi `kriechzahl_alt`.

### _ersetzt

```python
def _ersetzt(rechenart: Any, arten) -> Any
```

Die Rechenart, wie sie heute heisst: was eine alte Datei dort waehlt, wo
es die Wahl nicht mehr gibt, wird zu ihrem Ersatz -- und der, wo es auch
ihn nicht gibt, zu seinem
([[opencivil.nachweis.rechenwahl#Konstanten|ERSATZ_ALTER_WAHL]]). Alles andere
bleibt -- auch Unbekanntes, das die Pruefung danach meldet.

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
darin steht ([[opencivil.projekt.eintraege#Gebrauchsliste|FALL]]), welche Rechenarten sie anbietet
([[opencivil.projekt.eintraege#Gebrauchsliste|ARTEN]]) und wie ihr Bauteil in den Meldungen heisst
([[opencivil.projekt.eintraege#Gebrauchsliste|BAUTEIL]]).

- `FALL = GebrauchsfallEintrag`
- `ARTEN = SPANNUNGSARTEN`
- `BAUTEIL = 'Platte'`
- `anteil: float` – Welcher Anteil der Tragsicherheitseinwirkungen abgeleitet wird, in %.
- `aus_tragsicherheit: bool = False` – Ob die abgeleiteten Faelle *gefuehrt* werden. Gebildet werden sie immer; ausgeschaltet rechnen sie still mit. Der Anteil ist eine bequeme Abschaetzung und keine Norm, darum stehen die Faelle nur auf Verlangen in der Tabelle.
- `faelle: List[GebrauchsfallEintrag] = field(default_factory=list)` – Eigene Lastfaelle -- neben den abgeleiteten, nicht statt ihrer.
- `wahl: RechenwahlEintrag = field(default_factory=RechenwahlEintrag.gebrauch)` – Womit die Stahlspannung gerechnet wird -- Vorgabe elastisch, charakteristisch.

#### Gebrauchsliste.lastfall

```python
def lastfall(self, name: str, **werte: float)
```

Einen eigenen Lastfall anfuegen -- kNm und kN, Zug positiv.

#### Gebrauchsliste.pruefen

```python
def pruefen(self, bauteil: str, kombinationen: List[Any], wort: str) -> None
```

Was an dieser Liste nicht stimmen kann -- `wort` ist «häufige» oder
«quasi-ständige» und steht in der Meldung.

Je Liste fuer sich: die beiden Listen landen in getrennten Nachweisen
und damit in getrennten ID-Raeumen. Ein Fall «Dauer» darf in beiden
stehen. `kombinationen` sind die Faelle der Tragsicherheit, aus
denen abgeleitet wird -- gelesen wird nur ihr Name.

#### Gebrauchsliste.aus_dict

```python
@classmethod
def aus_dict(cls, d: Mapping[str, Any], *, wort: str, vorgabe: float, kriechzahl_alt: Optional[float]=None) -> 'Gebrauchsliste'
```

`kriechzahl_alt`: das phi der Platte, fuer eine Datei ohne Wahl.

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
- `art: str = Erfuellungsart.AUTOMATISCH.value`
- `aktiv: bool = True` – Ob dieser Lastfall gerechnet wird. Ausgeschaltet bleibt er stehen.

#### KombinationEintrag.aus_dict

```python
@classmethod
def aus_dict(cls, d: Mapping[str, Any]) -> 'KombinationEintrag'
```


## Konstanten

- `WERKSTOFFSAETZE = tuple((s.value for s in Werkstoffsatz))` – Mit welchen Festigkeiten ein Werkstoffgesetz rechnen kann, siehe [[opencivil.nachweis.querschnittsloeser#Werkstoffsatz|Werkstoffsatz]]. Gewaehlt in der Querschnittsanalyse und in jeder Spannung-Dehnung-Analyse.
- `BETONGESETZE = (Rechenart.PARABEL.value, Rechenart.BLOCK.value)` – Welche Spannungs-Dehnungs-Beziehung der Beton der Querschnittsanalyse haben kann: Parabel-Rechteck oder der Spannungsblock 0.85·x -- die beiden genauen Rechenarten ([[opencivil.nachweis.rechenwahl#Rechenart|Rechenart]]).
- `EIGENE_VORSILBE = {'beton': 'BE', 'betonstahl': 'S'}` – Womit die Namen eigener Materialien beginnen: BE1, BE2 ... beim Beton, S1, S2 ... beim Betonstahl (Benutzer, 2026-10-16).
- `HAEUFIG_ANTEIL = 70.0` – Anteil der Tragsicherheitseinwirkungen, der als haeufiger Lastfall gilt -- in Prozent, wie die Maske ihn zeigt. Eine Vorgabe, einstellbar je Platte.
- `QUASISTAENDIG_ANTEIL = 60.0` – Dasselbe fuer die quasi-staendigen Lastfaelle.

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.wert]]
- [[opencivil.material.basis]]
- [[opencivil.nachweis.biegung_normalkraft]]
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
