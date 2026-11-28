---
erzeugt: 69c6050a4e41
art: modul
tags: [modul]
---
> [!abstract] opencivil/mauerwerk/werk.py
> eine Mauerwerkswand im Rechenwerk.
> Paket [[opencivil.mauerwerk]] · [Quelltext](../../opencivil/mauerwerk/werk.py)

## VERANTWORTUNG

Was eine Wand im Rechenwerk anmeldet: ihre Vorgaben ([[opencivil.mauerwerk.werk#Konstanten|VORGABEN]]) –
in der Maske die Kachel «Mauerwerk», in der Herleitung ein Kasten – und
eine Prozedur, die ihre Zeichnung prüft ([[opencivil.mauerwerk.pruefen|pruefen]]),
die Werte ihres Mauerwerks liest, an den Mindestwerten misst und nach ihrer Wahl umrechnet
([[opencivil.mauerwerk.kennwerte|kennwerte]]), die Pfeiler bestimmt
([[opencivil.mauerwerk.modell#pfeiler|pfeiler]]) und die Herleitung schreibt
([[opencivil.mauerwerk.herleitung|herleitung]]).


## DAS ERGEBNIS

kommt als Befund in die Lösung ([[opencivil.mauerwerk.werk#Wandbefund|Wandbefund]]); Zeichnung und
Zusammenfassung lesen es dort. Eine Wand, der etwas fehlt, ist ein Befund
mit Meldung und keine Ausnahme: der Rest des Projekts rechnet weiter.


## NOCH OHNE LASTEN

Lastfälle und Nachweise kommen in den nächsten Schritten (Plan vom
2026-11-27, Schritt 14 b–e). Bis dahin rechnet die Wand ihre Form und ihre
Werte.

## Inhalt

### Wandbefund

```python
@dataclass
class Wandbefund
```

Was die Rechnung fand: die Wand, ihr Mauerwerk, ihre Meldungen, Werte und Pfeiler.

- `wand: Wand`
- `mauerwerk: str` – Der Name ihres Mauerwerks.
- `material: Dict[str, float]` – Je Kurzname, was die Wand von ihrem Mauerwerk liest ([[opencivil.mauerwerk.kennwerte#Konstanten|.kennwerte.GELESEN]]).
- `werte: Wandwerte`
- `t: float` – Ihre Dicke, in m.
- `meldungen: List[Meldung]` – Was an der Zeichnung falsch ist oder fehlt – die der Beschreibung zuerst.
- `zum_mauerwerk: List[Meldung] = field(default_factory=list)` – Was zu Mauerwerk und Dicke zu sagen ist: Werte unter den Mindestwerten deklarierten Mauerwerks, eine unübliche Dicke – in der Maske bei ihren Feldern.
- `gezeichnet: bool = False` – Ob ihre Zeichnung rechnet: keine Meldung zu Umriss, Öffnungen oder Stürzen hält sie auf.
- `pfeiler: List[Pfeiler] = field(default_factory=list)` – Leer, solange sie nicht [[opencivil.mauerwerk.werk#Wandbefund|gezeichnet]] ist.

#### Wandbefund.alle_meldungen

```python
@property
def alle_meldungen(self) -> List[Meldung]
```

Was zur Zeichnung zu sagen ist, dann was zu Mauerwerk und Dicke.

#### Wandbefund.bereit

```python
@property
def bereit(self) -> bool
```

Ob die Wand rechnet: keine Meldung hält sie auf.

### WandProzedur

```python
class WandProzedur(Prozedur)
```

Die ganze Wand, geprüft, umgerechnet und aufgeschrieben.

#### WandProzedur.rechne

```python
def rechne(self, e: Eingaben, p: Protokoll) -> Ausfuehrung
```

### Mauerwerkswand

```python
class Mauerwerkswand(Rechenobjekt)
```

Eine Wand aus Mauerwerk, fertig für das Rechenwerk.

- `WAS = 'Mauerwerk'`

#### Mauerwerkswand.baustoffe

```python
@property
def baustoffe(self) -> Sequence[Baustoff]
```

#### Mauerwerkswand.abschnitt

```python
def abschnitt(self) -> Abschnitt
```

#### Mauerwerkswand.ziele

```python
def ziele(self) -> List[str]
```

Was ein Lauf rechnen muss: die Wand.

#### Mauerwerkswand.rechnen_und_schreiben

```python
def rechnen_und_schreiben(self, e: Eingaben, p: Protokoll) -> Ausfuehrung
```

Die Wand geprüft, ihre Werte umgerechnet, Pfeiler bestimmt, Herleitung geschrieben.


## Konstanten

- `THEMA = 'Mauerwerk'` – Unter welchem Thema ihre Herleitung in der Formelsammlung steht.
- `VORGABEN = (Gruppe('Mauerwerk', lambda: (Feld('t', 't_w', MM, 'Dicke der Wand', …` – Was die Wand aus ihrer Beschreibung liest ([[opencivil.core.vorgaben]]).

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.rechenobjekt]]
- [[opencivil.core.vorgaben]]
- [[opencivil.core.wert]]
- [[opencivil.material.basis]]
- [[opencivil.mauerwerk.herleitung]]
- [[opencivil.mauerwerk.kennwerte]]
- [[opencivil.mauerwerk.modell]]
- [[opencivil.mauerwerk.pruefen]]
- [[opencivil.stabwerk.system]]

## Gebraucht von

- [[opencivil.mauerwerk.herleitung]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.aufbau.mauerwerk]]
- [[opencivil.web.api]]
- [[opencivil.web.mauerwerkdaten]]
