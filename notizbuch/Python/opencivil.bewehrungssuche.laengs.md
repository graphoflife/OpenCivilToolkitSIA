---
erzeugt: 8146540c4375
art: modul
tags: [modul]
---
> [!abstract] opencivil/bewehrungssuche/laengs.py
> die Laengsbewehrung suchen.
> Paket [[opencivil.bewehrungssuche]] · [Quelltext](../../opencivil/bewehrungssuche/laengs.py)

## VERANTWORTUNG

Findet zu einer Platte die kleinste Bewehrung, mit der alle *eingeschalteten*
Nachweise aufgehen. Gesucht wird ueber Durchmesser und Teilung; die Anordnung
-- welche Lage es gibt und in welche Richtung sie traegt -- bleibt, wie sie
eingegeben wurde.


## WARUM ES SUCHEN UND NICHT RECHNEN IST

Eine Bewehrung liesse sich fuer einen einzelnen Nachweis geschlossen
bestimmen. Fuer alle zusammen nicht: der Duktilitaetsnachweis wird durch mehr
Stahl *schlechter*, die uebrigen besser. Zwischen beiden liegt ein Fenster,
und ob es offen ist, weiss man erst, wenn man hineingeschaut hat.


## DAS VERFAHREN


```
fuer jede Teilung s aus der Liste:
    alle gesuchten Posten auf den kleinsten Durchmesser
    wiederhole:
        rechnen, alle eingeschalteten Urteile einsammeln
        gehen alle auf -> fertig
        sonst: jeden Posten einzeln einen Durchmesser groesser probieren
               und den Schritt nehmen, der den schlechtesten
               Erfuellungsgrad am weitesten hebt
        hebt kein Schritt ihn -> mit dieser Teilung geht es nicht
von allen Loesungen die mit der kleinsten Stahlflaeche
```

Der Schritt wird also nicht geraten, sondern ausprobiert. Das kostet je Runde
eine Rechnung pro Posten -- bei rund dreissig Millisekunden je Rechnung ist
das der guenstigere Handel gegenueber einer Regel, die bei
Duktilitaetsversagen in die falsche Richtung liefe.


## DER MINDESTDURCHMESSER

Die Grundbewehrung jeder Lage ist mindestens so dick -- in x beginnt die
Suche dort und nicht bei null, und eine y-Lage, die duenner ist oder fehlt,
hebt sie darauf an ([[opencivil.bewehrungssuche.laengs#_y_ableiten|_y_ableiten]]). Eine Platte hat oben und unten
in beiden Richtungen ein Netz; eine Lage, die kein Nachweis verlangt, blieb
sonst leer. Die Zulage darf weiter fehlen. Ohne Mindestdurchmesser (null)
darf auch eine Lage leer bleiben.


## DIE OBERGRENZE

Mehr Querschnitt als `automatik_grenze` (Grund und Zulage zusammen, in
mm²/m) bekommt keine x-Lage -- einen Schritt darueber nimmt die Suche gar
nicht erst in Betracht. Damit auch ⌀30@150 erreichbar ist, reicht die Liste
der Durchmesser bis ⌀40; die Grenze haelt die Suche im Zaum.

## Inhalt

### Suchmodus

```python
class Suchmodus(str, Enum)
```

Was gesucht wird und wogegen.

- `GRUND_OHNE = 'grund_ohne'` – Nur die Grundbewehrung, ohne Einwirkungen. Es bleiben die Nachweise, die keine Schnittgroessen brauchen: Duktilitaet, sproedes Versagen und die Rissbreitenbegrenzung unter Zwaengung. Das ist die Bewehrung, die eine Platte unabhaengig von der Belastung braucht.
- `GRUND_MIT = 'grund_mit'` – Nur die Grundbewehrung, aber gegen alle Nachweise.
- `GRUND_OHNE_ZULAGE_MIT = 'grund_ohne_zulage_mit'` – Zwei Schritte: erst die Grundbewehrung ohne Kraefte, dann die Zulage gegen alle Nachweise. So traegt die Grundbewehrung die Anforderungen der Platte und die Zulage die der Belastung -- getrennt sichtbar.

#### Suchmodus.beschriftung

```python
@property
def beschriftung(self) -> str
```

### Loesung

```python
@dataclass
class Loesung
```

Was fuer eine Teilung herauskam.

- `teilung: float`
- `gefunden: bool = False`
- `lagen: List['LageEintrag'] = field(default_factory=list)` – Die vier Lagen, wie die Suche sie hinterlaesst -- die Platte selbst, nicht eine Beschreibung davon. Frueher stand hier ein Woerterbuch aus Marken (`'2g'`, `'3z'`) auf Durchmesser. [[opencivil.bewehrungssuche.laengs#uebernehmen|uebernehmen]] musste die Marken wieder zerlegen, eine eigene Funktion Luecken mit null fuellen, und jede Regel fuer die y-Lagen -- «wie x», «mindestens» -- brauchte dort noch einmal einen Sonderfall. Die Suche hat die fertige Platte aber ohnehin in der Hand.
- `stahlflaeche: float = 0.0` – Summe der Bewehrungsquerschnitte aller Lagen, in mm² ueber die Breite `b` -- das Mass, nach dem die Teilungen verglichen werden.
- `schlechtester: float = 0.0`
- `nachweis: str = ''`
- `begruendung: str = ''`

### Suchergebnis

```python
@dataclass
class Suchergebnis
```

Das Ganze: je Teilung eine Loesung, und welche gewonnen hat.

- `modus: Suchmodus`
- `loesungen: List[Loesung] = field(default_factory=list)`
- `beste: Optional[Loesung] = None`
- `begruendung: str = ''`
- `duktilitaet: str = ''` – Was der Duktilitaetsnachweis zur gefundenen Bewehrung sagt. Gesucht wird ohne ihn -- er wird durch mehr Stahl schlechter, und eine Suche, die von unten aufsteigt, hat gegen ihn kein Mittel. Verschwiegen wird er deshalb nicht: hier steht, ob er mit dem Ergebnis noch aufgeht.
- `duktilitaet_erfuellt: Optional[bool] = None` – Dasselbe als Ja/Nein -- `None`: nichts zu sagen, keine x-Lage bewehrt.

#### Suchergebnis.gefunden

```python
@property
def gefunden(self) -> bool
```

### _gesuchte

```python
def _gesuchte(eintrag, *, arten: Sequence[str]) -> List[Posten]
```

Welche Posten die Suche anfasst: die der Tragrichtung x.

Auch die, die gerade auf null stehen. Frueher blieben die draussen -- eine
leere Lage galt als Entscheidung ueber die Anordnung, die die Suche nicht
treffen sollte. Das war zu vorsichtig: wer die Bewehrung ermitteln laesst,
will wissen, *wo* welche hingehoert, und nicht bloss, wie dick die schon
eingetragene wird.

Die y-Lagen bleiben, wie sie sind. Nachgewiesen wird in y nichts, also
gaebe es dort auch kein Mass, an dem sich ein Durchmesser bemessen liesse
-- die Suche wuerde sie auf null ziehen, und genau das waere falsch: die
y-Bewehrung liegt aussen und bestimmt, wieviel statische Hoehe der
x-Bewehrung bleibt. Was dort liegt, sagt der Benutzer -- oder er laesst
die y-Grundbewehrung der x-Grundbewehrung folgen. Duenner als der
Mindestdurchmesser bleibt sie aber nicht (beides [[opencivil.bewehrungssuche.laengs#_y_ableiten|_y_ableiten]]).

Null ist der Anfang der Zulage -- und der Grundbewehrung nur ohne
Mindestdurchmesser (siehe [[opencivil.bewehrungssuche.laengs#suche|suche]]).

### stufen

```python
def stufen(durchmesser: Sequence[float], mindest: float, *, leer: bool=True) -> List[float]
```

Die Durchmesser, die zur Auswahl stehen -- mit der Null davor, wenn der
Posten fehlen darf (`leer`).

Die Null heisst «nicht vorhanden» und ist dann die unterste Stufe; von ihr
aus steigt die Suche. Darueber kommt nichts unter `mindest`: ein aktiver
Stab soll nicht duenner sein als das, was man verlegen will.

### Stufen

```python
@dataclass(frozen=True)
class Stufen
```

Welche Durchmesser ein Posten der Reihe nach annimmt -- je Art eine
Liste, jede beginnt mit ihrer untersten Stufe.

Die Zulage darf fehlen: ihre Liste beginnt bei null. Die Grundbewehrung
beginnt mit Mindestdurchmesser bei ihm, eine Lage ohne Grundbewehrung gibt
es dann nicht (siehe «Der Mindestdurchmesser» oben). Vorher lag das in
einem Index, der durch vier Funktionen gereicht wurde: bei welcher Stufe
die Grundbewehrung anfaengt.

- `grund: Tuple[float, ...]`
- `zulage: Tuple[float, ...]`

#### Stufen.aus

```python
@classmethod
def aus(cls, durchmesser: Sequence[float], mindest: float) -> 'Stufen'
```

#### Stufen.von

```python
def von(self, posten: Posten) -> Tuple[float, ...]
```

#### Stufen.mindest

```python
@property
def mindest(self) -> float
```

Der duennste Grundstab -- null, wenn eine Lage leer bleiben darf.

### _seiten

```python
def _seiten(eintrag) -> List[Tuple[int, int]]
```

Je Seite das Paar (x-Lage, y-Lage): unten 1 und 2, oben 3 und 4.

### _y_ableiten

```python
def _y_ableiten(eintrag, mindest: float, teilung: float) -> None
```

Was die Suche an den y-Lagen tut -- die eine Regel dafuer.

Folgt y der x-Grundbewehrung (`automatik_y_wie_x`), bekommt jede Seite
die x-Grundbewehrung dieser Seite. Sonst wird eine y-Grundbewehrung, die
duenner ist als der Mindestdurchmesser oder fehlt, auf ihn gehoben, mit
der gesuchten Teilung; eine dickere bleibt, wie sie ist -- mindestens
heisst nicht genau.

Nach jedem Setzen und nicht erst beim Uebernehmen: liegt y aussen, kostet
ihr Durchmesser x die statische Hoehe, und gesucht werden soll mit der
Bewehrung, die hinterher dasteht.

### _ueber_grenze

```python
def _ueber_grenze(eintrag, grenze: float) -> bool
```

Ob eine x-Lage mehr Querschnitt traegt, als die Obergrenze erlaubt (mm²/m).

### _stahlflaeche

```python
def _stahlflaeche(eintrag) -> float
```

Stahlquerschnitt aller Lagen, in mm² ueber die Breite `b`.

### _eine_teilung

```python
def _eine_teilung(projekt, kennung: str, teilung: float, posten: Sequence[Posten], stufen: Stufen) -> Loesung
```

Die kleinste Bewehrung bei dieser Teilung -- oder die Auskunft, dass es
keine gibt.

Aufgestiegen wird von unten: jeder Posten auf der untersten Stufe seiner
Liste ([[opencivil.bewehrungssuche.laengs#Stufen|Stufen]]), dann Runde fuer Runde den Schritt nehmen, der am
meisten bringt.

Ohne Mindestdurchmesser ist der Anfang darum ein Querschnitt, den es so
gar nicht geben kann; er liefert keinen Rueckstand, sondern einen Fehler,
und das ist kein Abbruch, sondern der Grund, ueberhaupt einen Schritt zu
suchen.

### suche

```python
def suche(projekt, kennung: str, *, modus: Suchmodus=Suchmodus.GRUND_OHNE, teilungen: Sequence[float]=TEILUNGEN, durchmesser: Sequence[float]=DURCHMESSER, mindestdurchmesser: float=MINDESTDURCHMESSER) -> Suchergebnis
```

Die kleinste Bewehrung, mit der alle eingeschalteten Nachweise aufgehen.

Mit `mindestdurchmesser` hat die Grundbewehrung jeder Lage wenigstens
ihn -- siehe «Der Mindestdurchmesser» oben. Null: eine Lage darf leer
bleiben.

Zurueck kommt ein [[opencivil.bewehrungssuche.laengs#Suchergebnis|Suchergebnis]]; das Projekt selbst bleibt
unberuehrt. Wer die gefundene Bewehrung uebernehmen will, ruft
[[opencivil.bewehrungssuche.laengs#uebernehmen|uebernehmen]].

### _duktilitaetsbefund

```python
def _duktilitaetsbefund(projekt, kennung: str, loesung: 'Loesung') -> Tuple[str, Optional[bool]]
```

Ob die gefundene Bewehrung die Druckzone noch genuegend begrenzt.

### _absteigen

```python
def _absteigen(projekt, posten, stand, setzen, bewertung: Bewertung, erwartet: int) -> Bewertung
```

Wieder hinunter, solange es noch aufgeht.

Der Aufstieg nimmt in jeder Runde den Schritt, der den Rueckstand am
weitesten senkt -- und der kann ueber das Ziel hinausgehen: ein Posten
landet zwei Stufen hoeher, obwohl eine gereicht haette, weil die zweite
unterwegs am meisten gebracht hat. Hier wird das zurueckgenommen, Stufe um
Stufe, solange alle Nachweise aufgehen.

Ohne diesen Abstieg waere «die kleinste Bewehrung» eine Zusage, die das
Werkzeug nicht haelt: es gaebe Ergebnisse, aus denen sich noch ein
Durchmesser herausnehmen liesse. Hinunter geht es bis zur untersten Stufe
des Postens -- unter den Mindestdurchmesser nicht ([[opencivil.bewehrungssuche.laengs#Stufen|Stufen]]).

### _fuer_teilung

```python
def _fuer_teilung(projekt, kennung: str, teilung: float, modus: Suchmodus, stufen: Stufen) -> Loesung
```

Eine Teilung, je nach Modus in einem oder zwei Schritten.

Die Arbeitsplatte hat die x-Lagen leer (siehe [[opencivil.bewehrungssuche.bewertung#arbeitskopie|arbeitskopie]]); was
nicht gesucht wird -- in den Grund-Modi die Zulage --, bleibt also
ausdruecklich null und steht so auch in der Loesung.

### uebernehmen

```python
def uebernehmen(projekt, kennung: str, loesung: Loesung) -> None
```

Die gefundenen Lagen in die Platte schreiben.


## Konstanten

- `DURCHMESSER = (8, 10, 12, 14, 16, 18, 20, 22, 26, 30, 34, 40)` – Lieferbare Stabdurchmesser in mm, aufsteigend. Die Suche geht sie der Reihe nach durch; was nicht in der Liste steht, kommt nicht heraus. Wie dick es wird, begrenzt die Obergrenze der Platte (`automatik_grenze`).
- `TEILUNGEN = (150.0,)` – Teilungen in mm, die ohne eigene Angabe versucht werden. Die eine uebliche -- jede weitere kostet einen vollstaendigen Suchlauf.
- `MINDESTDURCHMESSER = 10.0` – Kleinster Durchmesser, den die Suche einbaut -- und den die Grundbewehrung jeder Lage mindestens hat. Duenner lohnt sich nicht: die Ersparnis ist gering, und auf der Baustelle will niemand vier Stabdurchmesser auseinanderhalten.
- `RUNDEN = 60` – Obergrenze der Runden je Teilung. Mehr Runden als Posten mal Durchmesser kann es nicht geben -- die Zahl ist der Riegel gegen einen Denkfehler.
- `Posten = Tuple[int, str]` – Ein gesuchter Posten: Lagennummer (1..4) und Art ('grund' oder 'zulage').

## Braucht

- [[opencivil.bewehrungssuche.bewertung]]
- [[opencivil.projekt]]
- [[opencivil.querschnitt.platte]]

## Gebraucht von

- [[opencivil.bewehrungssuche]]
- [[opencivil.bewehrungssuche.buegel]]
- [[opencivil.bewehrungssuche.dicke]]
- [[opencivil.projekt.platte]]
