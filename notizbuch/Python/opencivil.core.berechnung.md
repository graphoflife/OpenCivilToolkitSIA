---
erzeugt: c2bac80c50bd
art: modul
tags: [modul]
---
> [!abstract] opencivil/core/berechnung.py
> Berechnungen als Objekte.
> Paket [[opencivil.core]] · [Quelltext](../../opencivil/core/berechnung.py)

## VERANTWORTUNG

Jeder Rechenschritt ist ein Objekt, das weiss, welche Werte es braucht, welche
es liefert, wie gerechnet wird und wie das Ergebnis aufzuschreiben ist.


## DREI AUSPRAEGUNGEN

* [[opencivil.core.berechnung#Formel|Formel]]   -- ein Einzeiler: eine Ausgabe, eine analytische Formel.
* [[opencivil.core.berechnung#Prozedur|Prozedur]] -- ein ganzer Ablauf: mehrere Ausgaben, Iterationen,
  Fallunterscheidungen; schreibt ihren Ablauf selbst ins Protokoll.
* [[opencivil.core.berechnung#Nachweis|Nachweis]] -- ein Vergleich von Einwirkung und Widerstand mit Urteil
  und Erfuellungsgrad.


## VARIANTEN -- WELCHE FORMEL GILT?

?
Oft haengt es von den vorhandenen Eingaben ab, welche Formel anzuwenden ist.
Dafuer duerfen mehrere Berechnungen denselben Wert liefern. Der Loeser waehlt
unter ihnen in zwei Stufen:

1. *Verfuegbarkeit* -- sind alle Pflichteingaben ueberhaupt beschaffbar?
2. *Anwendbarkeit*  -- [[opencivil.core.berechnung#Berechnung.anwendbar|Berechnung.anwendbar]] darf zusaetzlich von den
   tatsaechlichen Zahlenwerten abhaengen (z.B. "nur fuer f_ck \<= 50 N/mm^2").

Die Begruendung der Wahl landet im Protokoll -- der Leser sieht, warum gerade
diese Formel gegriffen hat.


## FEHLER WERDEN NICHT VERSCHLUCKT

Im alten Code fing der Wertzugriff jede Ausnahme ab, warnte und lieferte einen
veralteten Wert zurueck -- eine defekte Formel ergab damit eine plausible
falsche Zahl. Hier fuehrt jeder Rechenfehler zu einem [[opencivil.core.berechnung#BerechnungsFehler|BerechnungsFehler]]
mit Angabe der schuldigen Berechnung; die urspruengliche Ausnahme bleibt als
Ursache erhalten.

## Inhalt

### BerechnungsFehler

```python
class BerechnungsFehler(Exception)
```

Eine Berechnung ist gescheitert. Die Ursache bleibt angehaengt.

### Eingabebezug

```python
@dataclass(frozen=True)
class Eingabebezug
```

Bindet einen lokalen Formelnamen an eine globale Wert-ID.

- `name: str` – Kurzer Name in Formel und Vorlage, z.B. `f_ck`.
- `wert_id: str` – Globale ID des Wertes, z.B. `beton.C30_37.f_ck`.
- `optional: bool = False` – Wenn True, darf der Wert fehlen; die Berechnung prueft mit `hat()`.

### Befundbezug

```python
@dataclass(frozen=True)
class Befundbezug
```

Bindet einen lokalen Namen an den Befund einer anderen Berechnung.

Fuer eine Rechnung, die mehr als eine Zahl einer anderen braucht: die
Querkraft den Momentenwiderstand bei ihrer Normalkraft samt seiner
Herleitung, das Knicken die Resistenzlinie der Tragsicherheit. Der
Loeser rechnet die andere Berechnung vorher und reicht ihren Befund
durch ([[opencivil.core.berechnung#Eingaben.befund|Eingaben.befund]]) -- die Abhaengigkeit steht so im Graphen,
wie ein Wert es tut.

- `name: str`
- `berechnung_id: str`

### Eingaben

```python
class Eingaben(Mapping[str, Wert])
```

Die aufgeloesten Eingaben einer Berechnung, unter ihren lokalen Namen.

Ist selbst eine `Mapping`, damit sie direkt an die LaTeX-Hilfen
weitergereicht werden kann. Die Befunde anderer Berechnungen
([[opencivil.core.berechnung#Befundbezug|Befundbezug]]) stehen daneben, unter [[opencivil.core.berechnung#Eingaben.befund|befund]].

#### Eingaben.befund

```python
def befund(self, name: str) -> Any
```

Der Befund einer anderen Berechnung, unter seinem lokalen Namen.

#### Eingaben.hat

```python
def hat(self, name: str) -> bool
```

Prueft, ob eine optionale Eingabe vorliegt.

#### Eingaben.g

```python
def g(self, name: str) -> Groesse
```

Nur die Groesse -- die Kurzform fuers Rechnen.

#### Eingaben.groessen

```python
def groessen(self) -> Dict[str, Groesse]
```

Alle Eingaben als `name -> Groesse`, passend fuer `funktion(**...)`.

#### Eingaben.teilmenge

```python
def teilmenge(self, *namen: str) -> 'Eingaben'
```

Auswahl einzelner Eingaben -- praktisch fuer LaTeX-Vorlagen.

### Ausfuehrung

```python
@dataclass(frozen=True)
class Ausfuehrung
```

Was eine Berechnung in einem Lauf liefert: ihre Ausgaben -- und, wo es
mehr gibt, ihre Urteile und ihren Befund.

Der **Befund** ist alles, was ueber die Ausgabewerte hinausgeht und
spaeter jemand lesen will: Resistenzlinien, Fallergebnisse, das Ergebnis
eines Balkensystems. Er steht nach dem Lauf in der Loesung
([[opencivil.core.rechenwerk#Loesung|befunde]]), nicht am Objekt.
Ein Objekt beschreibt eine Rechnung, eine Loesung haelt fest, was sie
ergab -- so laesst sich eine Loesung aufheben und wiederverwenden, ohne
die Objekte umzuhaengen, die sie hervorgebracht haben.

[[opencivil.core.berechnung#Berechnung.rechne|Berechnung.rechne]] liefert die Ausgaben als Groessen,
[[opencivil.core.berechnung#Berechnung.ausfuehren|Berechnung.ausfuehren]] daraus Werte.

- `ausgaben: Mapping[str, Any]`
- `urteile: Tuple['NachweisUrteil', ...] = ()`
- `befund: Any = None`

### Fallbefund

```python
@dataclass
class Fallbefund
```

Der Befund eines Nachweises, der je Fall oder je Lage rechnet: was er
dabei fand, in der Reihenfolge seiner Urteile.

- `ergebnisse: list = field(default_factory=list)`

### Berechnung

```python
class Berechnung(ABC)
```

Basisklasse aller Rechenschritte.

Unterklassen implementieren [[opencivil.core.berechnung#Berechnung.rechne|rechne]]. Aufgerufen wird immer
[[opencivil.core.berechnung#Berechnung.ausfuehren|ausfuehren]], das die Ergebnisse prueft und in [[opencivil.core.wert#Wert|Wert]] verpackt.

Eine Berechnung darf ohne Ausgabe sein -- ein Nachweis ohne Lastfall, ein
Balkensystem: was sie findet, steht dann allein in ihrem Befund. Zum
Rechnen nennt man sie unter ihrer ID als Ziel (siehe
[[opencivil.core.rechenwerk#Rechenwerk.loese|loese]]).

- `THEMA: str = ''` – Unter welchem Thema ihre Formeln in der Formelsammlung stehen -- ein Nachweis nennt sich selbst. Leer: das Thema ihres Abschnitts.

#### Berechnung.thema

```python
@property
def thema(self) -> str
```

#### Berechnung.ausgabe_ids

```python
@property
def ausgabe_ids(self) -> Tuple[str, ...]
```

#### Berechnung.pflicht_eingaben

```python
@property
def pflicht_eingaben(self) -> Tuple[str, ...]
```

Wert-IDs, ohne die nicht gerechnet werden kann.

#### Berechnung.optionale_eingaben

```python
@property
def optionale_eingaben(self) -> Tuple[str, ...]
```

#### Berechnung.alle_eingaben

```python
@property
def alle_eingaben(self) -> Tuple[str, ...]
```

#### Berechnung.ausgabe_def

```python
def ausgabe_def(self, wert_id: str) -> WertDef
```

#### Berechnung.ausgabe_quelle

```python
@property
def ausgabe_quelle(self) -> Quelle
```

Als was die Ergebnisse gelten sollen.

Normalfall ist `BERECHNET`. [[opencivil.core.berechnung#Vorgabe|Vorgabe]] setzt das auf `VORGABE`,
damit im Bericht erkennbar bleibt, dass hier nichts hergeleitet wurde.

#### Berechnung.anwendbar

```python
def anwendbar(self, eingaben: Eingaben) -> Tuple[bool, str]
```

Darf diese Variante mit diesen Werten verwendet werden?

Standardmaessig ja. Ueberschreiben, wenn die Gueltigkeit vom Zahlenwert
abhaengt, z.B.:

```
def anwendbar(self, e):
    if e.g("f_ck") > Groesse(50, MPA):
        return False, "gilt nur bis C50/60"
    return True, "f_ck liegt im Gueltigkeitsbereich"
```

:return: (anwendbar, Begruendung fuers Protokoll)

#### Berechnung.rechne

```python
@abstractmethod
def rechne(self, e: Eingaben, p: Protokoll) -> Union[Mapping[str, Groesse], Ausfuehrung]
```

Fuehrt die Rechnung aus und schreibt sie ins Protokoll.

:param e: aufgeloeste Eingaben unter ihren lokalen Namen
:param p: Mitschrift -- hier wird die Herleitung festgehalten
:return: `{Wert-ID: Groesse}` fuer jede deklarierte Ausgabe --
oder eine [[opencivil.core.berechnung#Ausfuehrung|Ausfuehrung]] mit diesen Groessen, wo es dazu
Urteile oder einen Befund gibt

#### Berechnung.ausfuehren

```python
def ausfuehren(self, e: Eingaben, p: Protokoll) -> Ausfuehrung
```

Ruft [[opencivil.core.berechnung#Berechnung.rechne|rechne]] auf und prueft dessen Ergebnis.

Verpackt jede Groesse in einen [[opencivil.core.wert#Wert|Wert]] mit der deklarierten
Definition -- dabei wird auch die Dimension geprueft. Urteile und
Befund reicht es unveraendert durch.

### Formel

```python
class Formel(Berechnung)
```

Eine Ausgabe, eine analytische Formel.

Die Vorlage wird nur *analytisch* geschrieben; die Fassung mit Zahlen und
Einheiten entsteht daraus automatisch:

```python
Formel(
    id="beton.C30_37.f_cd",
    ausgabe=f_cd_def,
    eingaben={"eta_fc": "beton.C30_37.eta_fc",
              "f_ck":   "beton.C30_37.f_ck",
              "gamma_c":"beton.C30_37.gamma_c"},
    vorlage=r"\frac{@eta_fc \cdot @f_ck}{@gamma_c}",
    funktion=lambda eta_fc, f_ck, gamma_c: eta_fc * f_ck / gamma_c,
)
```

ergibt im Bericht:

```
f_{cd} = \frac{\eta_{fc} \cdot f_{ck}}{\gamma_c}
       = \frac{0.933 \cdot 30\,\mathrm{N/mm^2}}{1.5}
       = 18.7\,\mathrm{N/mm^2}
```

#### Formel.anwendbar

```python
def anwendbar(self, eingaben: Eingaben) -> Tuple[bool, str]
```

#### Formel.rechne

```python
def rechne(self, e: Eingaben, p: Protokoll) -> Mapping[str, Groesse]
```

### Vorgabe

```python
class Vorgabe(Berechnung)
```

Liefert einen festen Wert ohne Herleitung -- Normvorgabe oder Vorlagenwert.

Erlaubt es, auch Konstanten (Teilsicherheitsbeiwerte, Tabellenwerte) als
ordentliche Knoten im Rechengraph zu fuehren, statt sie im Code zu
verstecken. Der Benutzer kann sie damit ueberall gleich ueberschreiben.

#### Vorgabe.ausgabe_quelle

```python
@property
def ausgabe_quelle(self) -> Quelle
```

#### Vorgabe.rechne

```python
def rechne(self, e: Eingaben, p: Protokoll) -> Mapping[str, Groesse]
```

### Prozedur

```python
class Prozedur(Berechnung)
```

Ein mehrstufiger Ablauf: Iterationen, Fallunterscheidungen, mehrere Ausgaben.

Unterklassen implementieren [[opencivil.core.berechnung#Prozedur|rechne]] und schreiben dabei ihren Ablauf
ins Protokoll -- Ansatz, Startwerte, Zwischenschritte (gerne als Tabelle),
Abbruchkriterium, Ergebnis. Der Leser muss die Rechnung von Hand
nachvollziehen koennen; nur das Endergebnis auszugeben genuegt nicht.

Beispielgeruest:

```
class Nulllinienlage(Prozedur):
    def rechne(self, e, p):
        p.text("Die Nulllinie wird iterativ aus dem Kraeftegleichgewicht bestimmt.")
        zeilen = []
        for schritt in range(...):
            ...
            zeilen.append([Mathe(str(schritt)), Mathe(x.formatiert(1)),
                           Mathe(fehler.formatiert(2))])
        p.tabelle([Mathe("i"), Mathe("x"), Mathe(r"\Delta F")], zeilen,
                  titel="Iterationsverlauf")
        p.formel(...)
        return {...}
```

### grad_def

```python
def grad_def(id: str, symbol: str, beschreibung: str, referenz: str='') -> WertDef
```

Die Definition eines Erfuellungsgrads -- fuer jeden Nachweis dieselbe.

Frueher legte jeder Nachweis seine eigene an, mit eigener Stellenzahl, und
die Werttabelle rundete an [[opencivil.core.wert#grad_als_text|grad_als_text]] vorbei: dort stand 0.996
als «1», neben «nicht erfuellt».

### grad_formel

```python
def grad_formel(p: Protokoll, definition: WertDef, grad: float, widerstand: Wert, einwirkung: Wert, erfuellt: bool, *, mit_urteil: bool=False) -> None
```

Die Zeile mit dem Erfuellungsgrad -- in jedem Nachweis dieselbe Form,
Widerstand durch Einwirkung.

Der Grad setzt sich selbst ([[opencivil.core.wert#grad_als_text|grad_als_text]]). Stuende im Nenner eine
Null, bleibt es bei den Symbolen. Ohne Normverweis -- den traegt die
Zeile, aus der Widerstand und Einwirkung kommen.

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
- `name: str = ''` – Wie das Urteil heisst: Langname, Richtung und Fall, «Biegung und Normalkraft x – Feld». Gestempelt von [[opencivil.core.berechnung#Nachweis.rechne|Nachweis.rechne]] aus [[opencivil.core.berechnung#Nachweis.langname|langname]] und [[opencivil.core.berechnung#NachweisUrteil|fall]] -- ein Nachweis baut ihn nicht selbst. Frueher tat das jeder, und jeder etwas anders («M-N-Nachweis x – Feld», «Duktilität – 2. Lage», «Stahlspannung (Rissbreite) x – …»).
- `begruendung: str = ''`
- `einwirkung: Optional[Wert] = None`
- `widerstand: Optional[Wert] = None`
- `art: str = ''` – Kurzzeichen der Nachweisart -- `M-N` oder `V`. Zusammen mit [[opencivil.core.berechnung#NachweisUrteil|fall]] ergibt es die knappe Bezeichnung fuer die Zusammenfassung. Getrennt gefuehrt und nicht aus [[opencivil.core.berechnung#NachweisUrteil|name]] herausgeschnitten: den langen Namen zu zerlegen hiesse, aus Anzeigetext auf Bedeutung zu schliessen -- genau der Fehler, der die Nachweise mehrerer Platten schon einmal in dieselbe Tabelle gepackt hat.
- `langname: str = ''` – Die Nachweisart ausgeschrieben -- `Biegung und Normalkraft (x)`. Steht in der Zusammenfassung in einer eigenen Spalte neben [[opencivil.core.berechnung#NachweisUrteil|fall]]. Sie wird hier gefuehrt und nicht in der Schnittstelle aus [[opencivil.core.berechnung#NachweisUrteil|art]] nachgeschlagen: eine Tabelle von Kuerzeln auf Klartext waere eine zweite Stelle, an der jeder neue Nachweis eingetragen werden muss -- und die eine, die man vergisst. Die Tragrichtung gehoert hier hinein, wo eine da ist. In der Zeile steht sie sonst nirgends, und zwei Kombinationen gleichen Namens in x und y saehen in der Tabelle gleich aus.
- `fall: str = ''` – Bezeichnung dieses einen Falls -- der eingestellte Name, wo es einen gibt. Bei einer Einwirkungskombination ist das ihr Name, bei einem Nachweis je Lage die Lage. Ohne Richtung: die steht in [[opencivil.core.berechnung#Nachweis.langname|langname]].
- `hinweis: str = ''` – Was in der Zusammenfassung sichtbar dabeistehen muss. Fuer den Fall, dass sich gar kein Widerstand bestimmen liess -- keine Bewehrung auf der gezogenen Seite, eine Buegeldefinition ohne Bezug in dieser Richtung, eine Lage, die es nicht gibt. Dann steht in der Tabelle eine Null oder ein Strich, und eine Null erklaert sich nicht von selbst. Getrennt von [[opencivil.core.berechnung#NachweisUrteil|begruendung]]: die traegt jedes Urteil, auch das erfuellte, und gehoert in den Tooltip. Dieses Feld setzt nur, wer etwas zu melden hat -- die Pruefung weiss es, die Schnittstelle soll es nicht aus einer Null erraten muessen.
- `ziel: str = ''` – Wert-ID des Erfuellungsgrads, der dieses Urteil traegt. Das Ziel, mit dem sich genau dieser Nachweis samt allem, was er braucht, nachrechnen laesst -- das Auge in der Zusammenfassung. Gesetzt von der Pruefung: nur sie weiss, welcher ihrer Grade zu welchem Fall gehoert.
- `sammel: bool = False` – Ob dieses Urteil eines von mehreren zur selben Frage ist. Die Nachweise, die je Bewehrungslage rechnen, faellen ein Urteil je Lage. Beantwortet ist die Frage aber von der schlechtesten: geht die auf, gehen die anderen erst recht auf. In Tabelle und Bericht steht darum nur sie -- siehe [[opencivil.core.berechnung#NachweisUrteil|Loesung.gefuehrte_urteile]]. Gerechnet und *gezaehlt* werden trotzdem alle. Die Bewehrungssuche misst ihren Fortschritt an der Summe der Rueckstaende; saehe sie nur das Minimum, stuende sie, sobald zwei Lagen gleich schlecht sind -- kein einzelner Schritt hebt dann das Minimum, und die Suche gaebe auf, obwohl der naechste Durchmesser offensichtlich hilft.
- `still: bool = False` – Ob dieses Urteil aus einem ausgeschalteten Nachweis stammt. Es zaehlt dann nicht in der Zusammenfassung und nicht im Gesamturteil -- sichtbar wird es nur als Hinweis darunter, und auch nur, wenn es nicht aufgeht.
- `raum: str = ''` – Namensraum des Nachweises, der dieses Urteil gefaellt hat. Wird von [[opencivil.core.berechnung#Nachweis.rechne|Nachweis.rechne]] gesetzt, nicht beim Erzeugen -- so kann kein Nachweis ihn vergessen oder falsch angeben. Die Oberflaeche gruppiert danach; ohne ihn muesste sie aus dem Anzeigetext zurueckschliessen, welche Platte gemeint ist, und das geht schief, sobald zwei Platten dieselben Richtungen tragen.

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

Unterklassen implementieren [[opencivil.core.berechnung#Nachweis.pruefe|pruefe]] statt [[opencivil.core.berechnung#Nachweis.rechne|rechne]]. Die
Urteile gehen mit der [[opencivil.core.berechnung#Ausfuehrung|Ausfuehrung]] in die Loesung
([[opencivil.core.rechenwerk#Loesung|urteile]]) -- der Bericht baut
daraus die Nachweistabelle. Am Objekt bleibt nichts: es beschreibt den
Nachweis, die Loesung haelt fest, wie er ausging.

- `still: bool = False` – Ob der Nachweis mitrechnet, ohne in die Herleitung zu kommen. Ausgeschaltete Nachweise verschwinden nicht, sie werden still: gerechnet wird weiter, in der Zusammenfassung stehen sie nicht, und wenn einer von ihnen nicht aufgeht, steht darunter ein Hinweis. Das ist der Unterschied zwischen «interessiert mich gerade nicht» und «gilt nicht» -- und nur das erste trifft auf einen Schalter zu, den jemand umgelegt hat.
- `LANGNAME: str = ''` – Wie der Nachweis in der Zusammenfassung heisst, Spalte «Nachweis». Leer: sein Thema. Getrennt vom Thema, weil beide anders ordnen. Die Formelsammlung ordnet nach dem, was gerechnet wird -- «Zwängung auf Biegung». Die Zusammenfassung ordnet nach der Frage, die beantwortet wird -- «Risse: Zwängung Biegung», bei den anderen Rissnachweisen.
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
[[opencivil.core.berechnung#NachweisUrteil|NachweisUrteil.sammel]].

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

- `FormelFunktion = Callable[..., Union[Groesse, EmpirischesErgebnis]]` – Eine Rechenfunktion bekommt die Eingaben als Groessen unter ihren lokalen Namen und liefert eine Groesse -- oder ein EmpirischesErgebnis, wenn die Normformel dimensionell inhomogen ist.

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]

## Gebraucht von

- [[opencivil.bericht.zusammenfassung]]
- [[opencivil.core.rechenwerk]]
- [[opencivil.ergebnis]]
- [[opencivil.geotechnik.grundbruch]]
- [[opencivil.material.basis]]
- [[opencivil.nachweis.biegung_normalkraft]]
- [[opencivil.nachweis.duktilitaet]]
- [[opencivil.nachweis.fehlende_bewehrung]]
- [[opencivil.nachweis.kennzahlen]]
- [[opencivil.nachweis.knicken]]
- [[opencivil.nachweis.mindestbewehrung]]
- [[opencivil.nachweis.qa_gebrauch]]
- [[opencivil.nachweis.qa_knicken]]
- [[opencivil.nachweis.querkraft]]
- [[opencivil.nachweis.rechenwahl]]
- [[opencivil.nachweis.richtungsnachweise]]
- [[opencivil.nachweis.schiefe_biegung]]
- [[opencivil.nachweis.schubwandnachweis]]
- [[opencivil.nachweis.spannungsbegrenzung]]
- [[opencivil.nachweis.sproedes_versagen]]
- [[opencivil.nachweis.stabgrenzen]]
- [[opencivil.nachweis.verformung]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.platte]]
- [[opencivil.querschnitt.schnittanalyse]]
- [[opencivil.stabwerk.rechnung]]
- [[opencivil.web.diagrammdaten]]

## Formeln aus diesem Modul

- [[Erfüllungsgrad]] · `grad_formel`
