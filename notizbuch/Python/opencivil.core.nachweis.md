---
erzeugt: 56568ba5a241
art: modul
tags: [modul]
---
> [!abstract] opencivil/core/nachweis.py
> der Nachweis: Einwirkung gegen Widerstand, mit Urteil.
> Paket [[opencivil.core]] · [Quelltext](../../opencivil/core/nachweis.py)

## VERANTWORTUNG

Die Berechnung, die einen Vergleich zieht und ein Urteil faellt
([[opencivil.core.nachweis#Nachweis|Nachweis]]), und was sie dafuer braucht: den Vergleich selbst mit
Erfuellungsgrad und Zeile der Herleitung ([[opencivil.core.nachweis#Vergleich|Vergleich]],
[[opencivil.core.nachweis#KeinVergleich|KeinVergleich]] fuer Faelle ohne Vergleich), das Urteil
([[opencivil.core.nachweis#NachweisUrteil|NachweisUrteil]], [[opencivil.core.nachweis#Fallausgang|Fallausgang]]), die Definition eines
Erfuellungsgrads ([[opencivil.core.nachweis#grad_def|grad_def]]) und den Befund eines Nachweises, der je
Fall rechnet ([[opencivil.core.nachweis#Fallbefund|Fallbefund]]).

Ein Grad, den kein Urteil traegt, ist unbeschraenkt: das setzt
[[opencivil.core.nachweis#Nachweis.rechne|Nachweis.rechne]] fuer jeden Nachweis. Was eine Berechnung allgemein
ist, steht in [[opencivil.core.berechnung]]; bis 2026-11-10 stand der
Nachweis dort mit, und die Datei war ueber tausend Zeilen lang.

## Inhalt

### Fallbefund

```python
@dataclass
class Fallbefund
```

Der Befund eines Nachweises, der je Fall oder je Lage rechnet: was er
dabei fand, in der Reihenfolge seiner Urteile.

- `ergebnisse: list = field(default_factory=list)`

### grad_def

```python
def grad_def(id: str, symbol: str, beschreibung: str, referenz: str='') -> WertDef
```

Die Definition eines Erfuellungsgrads -- fuer jeden Nachweis dieselbe.

Frueher legte jeder Nachweis seine eigene an, mit eigener Stellenzahl, und
die Werttabelle rundete an [[opencivil.core.wert#grad_als_text|grad_als_text]] vorbei: dort stand 0.996
als «1», neben «nicht erfuellt».

### Vergleich

```python
@dataclass(frozen=True)
class Vergleich
```

Was ein Nachweis gegeneinander haelt: die Einwirkung gegen den Widerstand.

Die Regeln dazu stehen hier, fuer jeden Nachweis dieselben. Der
Erfuellungsgrad ist R / E: um welchen Faktor die Einwirkung noch wachsen
duerfte. Der Widerstand gibt die Richtung vor, in der begrenzt wird; wirkt
nichts in dieser Richtung -- E ist null oder wirkt ihr entgegen, etwa ein
gedrueckter Stahl unter der Grenze seiner Zugspannung --, ist der Grad
unbeschraenkt, ∞. Erfuellt ist ein Grad ab eins.

Bis 2026-10-25 schrieb jeder Nachweis beides selbst; zwei setzten statt ∞
eine 1e9, und in der Zusammenfassung stand «1000000000.00».

- `einwirkung: Wert`
- `widerstand: Wert`
- `entscheid: Optional[bool] = None` – Das Urteil, wo nicht der Grad entscheidet, sondern die Geometrie: bei Biegung mit Normalkraft, ob die Einwirkung innerhalb der Resistenzlinie liegt -- der Grad misst dort nur, wie weit. Sonst `None`.

#### Vergleich.grad

```python
@property
def grad(self) -> float
```

#### Vergleich.erfuellt

```python
@property
def erfuellt(self) -> bool
```

#### Vergleich.benannt

```python
def benannt(self, *, einwirkung: Optional[Wert]=None, widerstand: Optional[Wert]=None) -> 'Vergleich'
```

Derselbe Vergleich unter anderen Zeichen -- in der Tabelle steht der
Widerstand mit seiner Bedingung, `M_Rd,x(N_Ed = -300 kN)`, in der
Herleitung kurz. Die Zahlen bleiben; wer andere unterschiebt, bekommt
einen Fehler.

#### Vergleich.bedingung

```python
def bedingung(self, p: Protokoll, titel: str) -> None
```

«E ≤ R» als Zeile, ohne Urteil -- das steht in der Zeile des Grads ([[opencivil.core.nachweis#Vergleich.zeile|zeile]]).

#### Vergleich.zeile

```python
def zeile(self, p: Protokoll, definition: WertDef, *, mit_urteil: bool=False) -> None
```

Die Zeile mit dem Erfuellungsgrad -- in jedem Nachweis dieselbe Form,
Widerstand durch Einwirkung.

Der Grad setzt sich selbst ([[opencivil.core.wert#grad_als_text|grad_als_text]]). Stuende im Nenner
eine Null, bleibt es bei den Symbolen. Ohne Normverweis -- den traegt
die Zeile, aus der Widerstand und Einwirkung kommen.

### KeinVergleich

```python
@dataclass(frozen=True)
class KeinVergleich
```

Der Ausgang eines Falls, in dem nichts gegeneinander steht: der Nachweis
liess sich nicht fuehren ([[opencivil.core.nachweis#Konstanten|NICHT_FUEHRBAR]]) -- es fehlt der
Widerstand, etwa an einer Lage ohne Bewehrung --, oder es gibt nichts zu
begrenzen ([[opencivil.core.nachweis#Konstanten|UNBESCHRAENKT]]), etwa ohne Druck beim Knicken. Was sich
trotzdem zeigen laesst, darf mitkommen.

- `grad: float`
- `erfuellt: bool`
- `einwirkung: Optional[Wert] = None`
- `widerstand: Optional[Wert] = None`

### Fallausgang

```python
class Fallausgang
```

Was ein Fallergebnis aus seinem Ausgang liest -- fuer Herleitung,
Diagramme und Urteil dieselben Zahlen. Wer erbt, fuehrt das Feld
`ausgang` mit der Vorgabe [[opencivil.core.nachweis#Konstanten|NICHT_FUEHRBAR]].

- `ausgang: Ausgang`

#### Fallausgang.machbar

```python
@property
def machbar(self) -> bool
```

Ob etwas gegeneinander steht.

#### Fallausgang.erfuellt

```python
@property
def erfuellt(self) -> bool
```

#### Fallausgang.erfuellungsgrad

```python
@property
def erfuellungsgrad(self) -> float
```

### NachweisUrteil

```python
@dataclass(frozen=True)
class NachweisUrteil
```

Ergebnis eines Nachweises.

`erfuellungsgrad` ist das Verhaeltnis Widerstand/Einwirkung: um welchen
Faktor die Einwirkung noch wachsen duerfte. Werte ab 1 bedeuten erfuellt.

Bewusst nur diese eine Kennzahl -- die Ausnutzung als Kehrwert waere
dieselbe Aussage in anderer Richtung und muesste an jeder Stelle mitgepflegt
und mitgelesen werden.

- `erfuellt: bool`
- `erfuellungsgrad: Groesse`
- `name: str = ''` – Wie das Urteil heisst: Langname, Richtung und Fall, «Biegung und Normalkraft x – Feld». Gestempelt von [[opencivil.core.nachweis#Nachweis.rechne|Nachweis.rechne]] aus [[opencivil.core.nachweis#Nachweis.langname|langname]] und [[opencivil.core.nachweis#NachweisUrteil|fall]] -- ein Nachweis baut ihn nicht selbst. Frueher tat das jeder, und jeder etwas anders («M-N-Nachweis x – Feld», «Duktilität – 2. Lage», «Stahlspannung (Rissbreite) x – …»).
- `begruendung: str = ''`
- `einwirkung: Optional[Wert] = None`
- `widerstand: Optional[Wert] = None`
- `art: str = ''` – Kurzzeichen der Nachweisart -- `M-N` oder `V`. Zusammen mit [[opencivil.core.nachweis#NachweisUrteil|fall]] ergibt es die knappe Bezeichnung fuer die Zusammenfassung. Getrennt gefuehrt und nicht aus [[opencivil.core.nachweis#NachweisUrteil|name]] herausgeschnitten: den langen Namen zu zerlegen hiesse, aus Anzeigetext auf Bedeutung zu schliessen -- genau der Fehler, der die Nachweise mehrerer Platten schon einmal in dieselbe Tabelle gepackt hat.
- `langname: str = ''` – Die Nachweisart ausgeschrieben -- `Biegung und Normalkraft (x)`. Steht in der Zusammenfassung in einer eigenen Spalte neben [[opencivil.core.nachweis#NachweisUrteil|fall]]. Sie wird hier gefuehrt und nicht in der Schnittstelle aus [[opencivil.core.nachweis#NachweisUrteil|art]] nachgeschlagen: eine Tabelle von Kuerzeln auf Klartext waere eine zweite Stelle, an der jeder neue Nachweis eingetragen werden muss -- und die eine, die man vergisst. Die Tragrichtung gehoert hier hinein, wo eine da ist. In der Zeile steht sie sonst nirgends, und zwei Kombinationen gleichen Namens in x und y saehen in der Tabelle gleich aus.
- `fall: str = ''` – Bezeichnung dieses einen Falls -- der eingestellte Name, wo es einen gibt. Bei einer Einwirkungskombination ist das ihr Name, bei einem Nachweis je Lage die Lage. Ohne Richtung: die steht in [[opencivil.core.nachweis#Nachweis.langname|langname]].
- `hinweis: str = ''` – Was in der Zusammenfassung sichtbar dabeistehen muss. Fuer den Fall, dass sich gar kein Widerstand bestimmen liess -- keine Bewehrung auf der gezogenen Seite, eine Buegeldefinition ohne Bezug in dieser Richtung, eine Lage, die es nicht gibt. Dann steht in der Tabelle eine Null oder ein Strich, und eine Null erklaert sich nicht von selbst. Getrennt von [[opencivil.core.nachweis#NachweisUrteil|begruendung]]: die traegt jedes Urteil, auch das erfuellte, und gehoert in den Tooltip. Dieses Feld setzt nur, wer etwas zu melden hat -- die Pruefung weiss es, die Schnittstelle soll es nicht aus einer Null erraten muessen.
- `ziel: str = ''` – Wert-ID des Erfuellungsgrads, der dieses Urteil traegt. Das Ziel, mit dem sich genau dieser Nachweis samt allem, was er braucht, nachrechnen laesst -- das Auge in der Zusammenfassung. Gesetzt von der Pruefung: nur sie weiss, welcher ihrer Grade zu welchem Fall gehoert.
- `sammel: bool = False` – Ob dieses Urteil eines von mehreren zur selben Frage ist. Die Nachweise, die je Bewehrungslage rechnen, faellen ein Urteil je Lage. Beantwortet ist die Frage aber von der schlechtesten: geht die auf, gehen die anderen erst recht auf. In Tabelle und Bericht steht darum nur sie -- siehe [[opencivil.core.nachweis#NachweisUrteil|Loesung.gefuehrte_urteile]]. Gerechnet und *gezaehlt* werden trotzdem alle. Die Bewehrungssuche misst ihren Fortschritt an der Summe der Rueckstaende; saehe sie nur das Minimum, stuende sie, sobald zwei Lagen gleich schlecht sind -- kein einzelner Schritt hebt dann das Minimum, und die Suche gaebe auf, obwohl der naechste Durchmesser offensichtlich hilft.
- `still: bool = False` – Ob dieses Urteil aus einem ausgeschalteten Nachweis stammt. Es zaehlt dann nicht in der Zusammenfassung und nicht im Gesamturteil -- sichtbar wird es nur als Hinweis darunter, und auch nur, wenn es nicht aufgeht.
- `raum: str = ''` – Namensraum des Nachweises, der dieses Urteil gefaellt hat. Wird von [[opencivil.core.nachweis#Nachweis.rechne|Nachweis.rechne]] gesetzt, nicht beim Erzeugen -- so kann kein Nachweis ihn vergessen oder falsch angeben. Die Oberflaeche gruppiert danach; ohne ihn muesste sie aus dem Anzeigetext zurueckschliessen, welche Platte gemeint ist, und das geht schief, sobald zwei Platten dieselben Richtungen tragen.

#### NachweisUrteil.meldenswert

```python
@property
def meldenswert(self) -> bool
```

Ob dieses stille Urteil einen Hinweis wert ist.

Nur was still ist und nicht aufgeht -- und nur, wenn es ueberhaupt
einen Widerstand gibt. Ohne ihn liess sich der Nachweis gar nicht
fuehren (etwa an einer unbewehrten Lage); das ist keine Auskunft
ueber die Bewehrung, sondern darueber, dass es keine gibt.

Die Regel steht hier und nicht in der Schnittstelle: Tabelle,
Konsolenbericht und LaTeX-Dokument stellen dieselbe Frage, und drei
Antworten darauf waeren drei Gelegenheiten, auseinanderzulaufen.

#### NachweisUrteil.gradtext

```python
def gradtext(self, *, latex: bool=False) -> str
```

Der Erfuellungsgrad als Text -- siehe [[opencivil.core.wert#grad_als_text|grad_als_text]].

### Nachweis

```python
class Nachweis(Berechnung)
```

Vergleicht Einwirkung und Widerstand und faellt ein Urteil.

Unterklassen implementieren [[opencivil.core.nachweis#Nachweis.pruefe|pruefe]] statt [[opencivil.core.nachweis#Nachweis.rechne|rechne]]. Die
Urteile gehen mit der [[opencivil.core.berechnung#Ausfuehrung|Ausfuehrung]] in die Loesung
([[opencivil.core.rechenwerk#Loesung|urteile]]) -- der Bericht baut
daraus die Nachweistabelle. Am Objekt bleibt nichts: es beschreibt den
Nachweis, die Loesung haelt fest, wie er ausging.

- `still: bool = False` – Ob der Nachweis mitrechnet, ohne in die Herleitung zu kommen. Ausgeschaltete Nachweise verschwinden nicht, sie werden still: gerechnet wird weiter, in der Zusammenfassung stehen sie nicht, und wenn einer von ihnen nicht aufgeht, steht darunter ein Hinweis. Das ist der Unterschied zwischen «interessiert mich gerade nicht» und «gilt nicht» -- und nur das erste trifft auf einen Schalter zu, den jemand umgelegt hat.
- `LANGNAME: str = ''` – Wie der Nachweis in der Zusammenfassung heisst, Spalte «Nachweis». Leer: sein Thema. Getrennt vom Thema, weil beide anders ordnen. Die Formelsammlung ordnet nach dem, was gerechnet wird -- «Zwängung auf Biegung». Die Zusammenfassung ordnet nach der Frage, die beantwortet wird -- «Risse: Zwängung Biegung», bei den anderen Rissnachweisen.
- `ART: str = ''` – Das Kurzzeichen der Nachweisart in jedem Urteil -- siehe [[opencivil.core.nachweis#NachweisUrteil|NachweisUrteil.art]].
- `richtung = None` – Die Tragrichtung, in der nachgewiesen wird -- `None`, wo es keine gibt.

#### Nachweis.langname

```python
@property
def langname(self) -> str
```

#### Nachweis.urteilsname

```python
def urteilsname(self, langname: str, fall: str) -> str
```

«Biegung und Normalkraft x – Feld»: Langname, Richtung, Fall.

#### Nachweis.leise

```python
def leise(self, schluessel: Any) -> bool
```

Ob dieser Fall nur mitrechnet: einzeln oder mit dem ganzen Nachweis.

#### Nachweis.massgebend

```python
@staticmethod
def massgebend(urteile: Sequence[NachweisUrteil]) -> List[NachweisUrteil]
```

Von mehreren Teilurteilen das schlechteste -- als Liste.

Wer eine Tabelle baut, meint dieses eine; leer bleibt leer.

#### Nachweis.protokoll_massgebend

```python
def protokoll_massgebend(self, p: Protokoll, urteile: Sequence[NachweisUrteil]) -> None
```

Welcher Teil entscheidet, wo es mehrere gibt -- etwa zwei Lagen.

In der Zusammenfassung steht nur der schlechteste; ohne diese Zeile
muesste man die Zahlen der Herleitung selbst vergleichen, um zu wissen,
welcher dort gelandet ist.

#### Nachweis.urteil

```python
def urteil(self, ziel: WertDef, fall: str, ausgang: Ausgang, begruendung: str, *, hinweis: str='', art: str='', langname: str='', still: bool=False) -> NachweisUrteil
```

Das Urteil eines Falls aus seinem Ausgang: erfuellt, Grad, Einwirkung
und Widerstand. `ziel` ist der Erfuellungsgrad, der es traegt.

Steht nichts gegeneinander, kommt der Grund als Hinweis in die
Zusammenfassung -- dort fehlen sonst die Zahlen, und ein Strich
erklaert sich nicht von selbst. Bis 2026-10-25 baute jeder Nachweis
sein Urteil selbst, und «nicht fuehrbar» stand auf vier Arten da.

#### Nachweis.ohne_bewehrung

```python
@staticmethod
def ohne_bewehrung(nummer: int) -> str
```

Die Begruendung einer Lage ohne Stahl -- in jedem Lagennachweis dieselbe.

#### Nachweis.teilurteile

```python
@staticmethod
def teilurteile(urteile: Sequence[NachweisUrteil]) -> List[NachweisUrteil]
```

Dieselben Urteile, jedes als Teil derselben Frage gekennzeichnet.

Zurueck kommt alles: gezaehlt und gerechnet wird jede Lage. Erst die
Darstellung nimmt daraus das schlechteste -- siehe
[[opencivil.core.nachweis#NachweisUrteil|NachweisUrteil.sammel]].

#### Nachweis.stillstellen

```python
def stillstellen(self, alle: Iterable[Any], laut: Iterable[Any]) -> None
```

Festlegen, welche Faelle in der Herleitung stehen und welche nur
mitrechnen.

Sind *alle* still, schweigt der Nachweis ganz -- sonst stuende seine
Ueberschrift samt Ansatz ueber einer Herleitung ohne einen einzigen
Fall darunter.

Ein Schluessel in `laut`, den `alle` nicht kennt, ist ein
Aufbaufehler und wird gemeldet. Stillschweigend uebergangen waere er
die unangenehmste Art von Fehler: der Nachweis verschwaende aus
Tabelle und Herleitung, ohne dass irgendwo etwas danebenstuende --
und gesucht wuerde er dann beim Nachweis und nicht beim Tippfehler.

#### Nachweis.pruefe

```python
@abstractmethod
def pruefe(self, e: Eingaben, p: Protokoll) -> Ausfuehrung
```

Fuehrt den Nachweis und liefert Ausgabewerte samt Urteilen -- und
einen Befund, wo jemand nach dem Lauf mehr lesen will als Zahlen.

:return: [[opencivil.core.berechnung#Ausfuehrung|Ausfuehrung]] mit `{Wert-ID: Groesse}`, den Urteilen
und dem Befund

#### Nachweis.rechne

```python
def rechne(self, e: Eingaben, p: Protokoll) -> Ausfuehrung
```


## Konstanten

- `NICHT_FUEHRBAR = KeinVergleich(0.0, False)`
- `UNBESCHRAENKT = KeinVergleich(math.inf, True)`
- `Ausgang = Union[Vergleich, KeinVergleich]` – Wie ein Fall ausgeht: verglichen, oder ohne Vergleich.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]

## Gebraucht von

- [[opencivil.bericht.zusammenfassung]]
- [[opencivil.core.berechnung]]
- [[opencivil.core.rechenwerk]]
- [[opencivil.durchstanzen.mit_bewehrung]]
- [[opencivil.durchstanzen.nachweis]]
- [[opencivil.ergebnis]]
- [[opencivil.geotechnik.grundbruch]]
- [[opencivil.geotechnik.setzung]]
- [[opencivil.nachweis.biegung_normalkraft]]
- [[opencivil.nachweis.duktilitaet]]
- [[opencivil.nachweis.fehlende_bewehrung]]
- [[opencivil.nachweis.knicken]]
- [[opencivil.nachweis.mindestbewehrung]]
- [[opencivil.nachweis.qa_gebrauch]]
- [[opencivil.nachweis.qa_knicken]]
- [[opencivil.nachweis.querkraft]]
- [[opencivil.nachweis.querkraft_buegel]]
- [[opencivil.nachweis.querkraft_ohne_buegel]]
- [[opencivil.nachweis.richtungsnachweise]]
- [[opencivil.nachweis.schiefe_biegung]]
- [[opencivil.nachweis.schubwandnachweis]]
- [[opencivil.nachweis.spannungsbegrenzung]]
- [[opencivil.nachweis.sproedes_versagen]]
- [[opencivil.nachweis.verformung]]
- [[opencivil.projekt.aufbau.kern]]

## Formeln aus diesem Modul

- [[Erfüllungsgrad]] · `Vergleich.zeile`
