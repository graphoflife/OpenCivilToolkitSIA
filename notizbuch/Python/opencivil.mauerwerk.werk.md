---
erzeugt: 51ce3f10df00
art: modul
tags: [modul]
---
> [!abstract] opencivil/mauerwerk/werk.py
> eine Mauerwerkswand im Rechenwerk.
> Paket [[opencivil.mauerwerk]] · [Quelltext](../../opencivil/mauerwerk/werk.py)

## VERANTWORTUNG

Was eine Wand im Rechenwerk anmeldet: ihre Vorgaben ([[opencivil.mauerwerk.werk#Konstanten|VORGABEN]]) –
in der Maske die Kacheln «Mauerwerk» und «Ränder», in der Herleitung ein
Kasten – und eine Prozedur, die ihre Zeichnung prüft
([[opencivil.mauerwerk.pruefen|pruefen]]), die Werte ihres Mauerwerks liest, an
den Mindestwerten misst und nach ihrer Wahl umrechnet
([[opencivil.mauerwerk.kennwerte|kennwerte]]), die Pfeiler bestimmt
([[opencivil.mauerwerk.modell#pfeiler|pfeiler]]), ihre Lasten je Lastfall und
Kombination auf Pfeiler und Stürze verteilt – die lotrechten nach
[[opencivil.mauerwerk.lasten|lasten]], die waagrechten nach
[[opencivil.mauerwerk.scheibe|scheibe]] – und die Herleitung schreibt
([[opencivil.mauerwerk.herleitung|herleitung]]).


## DAS ERGEBNIS

kommt als Befund in die Lösung ([[opencivil.mauerwerk.werk#Wandbefund|Wandbefund]]); Zeichnung,
Zusammenfassung und Nachweise ([[opencivil.mauerwerk.nachweise|nachweise]]) lesen
es dort. Eine Wand, der etwas fehlt, ist ein Befund mit Meldung und keine
Ausnahme: der Rest des Projekts rechnet weiter.

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
- `g_k: float = 0.0` – Ihr Eigengewicht je m² Ansicht, in N/m².
- `e_u: Optional[float] = None` – Die Ausmitte am Fuss in m – `None`, wo er eingespannt ist.
- `faelle: Dict[str, Abtrag] = field(default_factory=dict)` – Je Lastfall, nach seinem Namen, was er Pfeilern und Stürzen gibt; leer, wo nichts rechnet.
- `kombinationen: Dict[str, Abtrag] = field(default_factory=dict)` – Dasselbe je Kombination: die Summe der Lastfälle mit ihren Beiwerten.

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

Die Wand geprüft, ihre Werte umgerechnet, Pfeiler bestimmt, ihre
Lasten verteilt, Herleitung geschrieben.

#### Mauerwerkswand._abtragen

```python
def _abtragen(self, befund: Wandbefund) -> None
```

Je Lastfall und Kombination, was Pfeiler und Stürze tragen – in den Befund.


## Konstanten

- `THEMA = 'Mauerwerk'` – Unter welchem Thema ihre Herleitung in der Formelsammlung steht.
- `VORGABEN = (Gruppe('Mauerwerk', lambda: (Feld('t', 't_w', MM, 'Dicke der Wand', …` – Was die Wand aus ihrer Beschreibung liest ([[opencivil.core.vorgaben]]) – die Ausmitte am Fuss nur, wo er sich drehen kann.

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
- [[opencivil.mauerwerk.lasten]]
- [[opencivil.mauerwerk.modell]]
- [[opencivil.mauerwerk.pruefen]]
- [[opencivil.mauerwerk.scheibe]]
- [[opencivil.stabwerk.system]]

## Gebraucht von

- [[opencivil.mauerwerk.herleitung]]
- [[opencivil.mauerwerk.nachweise]]
- [[opencivil.mauerwerk.schub]]
- [[opencivil.mauerwerk.uebersicht]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.aufbau.mauerwerk]]
- [[opencivil.web.api]]
- [[opencivil.web.mauerwerkdaten]]
