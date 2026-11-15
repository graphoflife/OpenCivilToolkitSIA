---
erzeugt: df3c850136ec
art: modul
tags: [modul]
---
> [!abstract] opencivil/web/balkendaten.py
> was die Oberflaeche von einem Balkensystem zeigt.
> Paket [[opencivil.web]] · [Quelltext](../../opencivil/web/balkendaten.py)

## VERANTWORTUNG

Aus dem Befund eines gerechneten Systems, eben oder im Raum
([[opencivil.stabwerk.rechnung#Systembefund|Systembefund]]), die Daten fuer die
Oberflaeche, in den Einheiten der Anzeige -- kN, kNm, mm, mrad, Stellen in m:

* mit jeder Rechnung eine knappe Uebersicht ([[opencivil.web.balkendaten#uebersicht|uebersicht]]): die
  Meldungen mit den Elementen, die sie betreffen, die Knoten ohne
  Drehsteifigkeit, und je Fall die Extremwerte je Stab, die Grenzwerte
  ueber alle ([[opencivil.stabwerk.verlauf#grenzwerte|grenzwerte]]) und die
  Lagerkraefte;
* auf Anfrage die Verlaeufe eines Falls fuer die Bilder ([[opencivil.web.balkendaten#verlauf|verlauf]]):
  je Stab seine Lage und Proben der Schnittgroessen und der Verschiebung,
  je Knoten seine Verschiebung und Drehung -- oder dass seine Drehung nicht
  bestimmbar ist --, und die groesste Verschiebung;
* je Querschnitt sein Umriss fuer das Bildchen in seiner Zeile
  ([[opencivil.web.balkendaten#umrisse|umrisse]]);
* je Linie ihre Achsen, eben und im Raum ([[opencivil.web.balkendaten#stabachsen|stabachsen]]), fuer die
  gestrichelte Faser, die Zugseite und die Lasten in den Richtungen des
  Stabs -- die Oberflaeche legt sie nicht selbst.


## EBEN UND IM RAUM IN EINER FORM

Was sich unterscheidet -- die Achsen, die Groessen, die Lagerkraefte --,
steht je einmal in einer [[opencivil.web.balkendaten#Darstellung|Darstellung]] ([[opencivil.web.balkendaten#Konstanten|EBEN]], [[opencivil.web.balkendaten#Konstanten|RAUM]]);
welche gilt, sagt die Art der Rechnung. Eine Lage oder Verschiebung ist eine
Liste mit einer Zahl je Achse des Systems -- `[x, z]` in der Ebene,
`[x, y, z]` im Raum --, die Drehung eines Knotens eine Liste mit einer Zahl
je Drehachse. Ein Stab hat seine Achsen im System: `x` laengs, `z` zur
gestrichelten Faser, im Raum dazu `y` ([[opencivil.stabwerk3d.stab]]) --
dorthin traegt ein Bild einen positiven Wert auf. In der Ebene steht `y`
jedes Stabs senkrecht auf ihr, wie `y` des Systems: ein Stab zeigt dort
die Achsen, die heissen wie die des Systems.

Die Verlaeufe sind gross; mit jeder Rechnung mitgeliefert, machten sie jede
Eingabe langsamer, auch wenn niemand die Bilder ansieht -- dasselbe wie bei
den Diagrammen der Querschnittsanalyse. Gerechnet wird hier nichts, nur
umgerechnet und in Listen gelegt.

## Inhalt

### Darstellung

```python
@dataclass(frozen=True)
class Darstellung
```

Was eben und im Raum verschieden ist -- die Form der Daten bleibt dieselbe.

- `achsen: Tuple[str, ...]` – Die Achsen des Systems, in der Folge der Koordinaten.
- `drehachsen: Tuple[Optional[str], ...]` – Um welche Achse sich ein Knoten dreht, in der Folge des Rechenkerns -- in der Ebene um keine, die einen Namen hat: die Drehung liegt in ihr.
- `groessen: Dict[str, Anzeigegroesse]` – Was die Proben eines Stabs je Stelle tragen, ausser `x` und der Verschiebung -- und wovon die Uebersicht je Stab und Fall den kleinsten und den groessten Wert hat.
- `schnittgroessen: Tuple[str, ...]` – Welche der `groessen` Schnittgroessen sind -- die Zusammenfassung zeigt sie.
- `durchbiegungen: Tuple[Tuple[str, str], ...]` – Die Durchbiegungen gegen die Sehne, je mit der Achse des Stabs, in die sie positiv zeigt.
- `felder: Dict[str, str] = field(default_factory=dict)` – Je Groesse ihr Feld im Verlauf, wo es anders heisst ([[opencivil.stabwerk.verlauf#Konstanten|IN_DER_EBENE]]).

#### Darstellung.feld

```python
def feld(self, groesse: str) -> str
```

#### Darstellung.lage

```python
def lage(self, v: Any) -> Dict[str, Any]
```

Anfang und Achsen eines Stabs im System, aus seinem Verlauf -- in den Achsen der Darstellung.

#### Darstellung.stabachsen

```python
def stabachsen(self, achsen: Tuple[Vektor, Vektor, Vektor]) -> Dict[str, List[float]]
```

Die Achsen `(x, y, z)` eines Stabs im System, die die Darstellung
zeigt, in ihren Koordinaten -- in der Ebene x und z (siehe Dateikopf).

#### Darstellung.drehungen

```python
@property
def drehungen(self) -> Tuple[str, ...]
```

Wie die Drehungen eines Knotens heissen: `φ`, im Raum `φ_x`, `φ_y`, `φ_z`.

#### Darstellung._lagerwerte

```python
def _lagerwerte(self)
```

Je Wert einer Lagerkraft, in der Folge des Rechenkerns, seine
Groesse, seine Achse und ob er ein Moment ist: erst je Achse eine
Kraft, dann je Drehachse ein Moment.

#### Darstellung.lagerkraefte

```python
@property
def lagerkraefte(self) -> Tuple[Anzeigegroesse, ...]
```

Die Werte einer Lagerkraft, in der Folge des Rechenkerns.

#### Darstellung.als_dict

```python
def als_dict(self) -> Dict[str, Any]
```

Fuer den Katalog: Namen, Zeichen, Einheiten und Stellen.

### uebersicht

```python
def uebersicht(befund: Optional[Systembefund]) -> Dict[str, Any]
```

Was die Oberflaeche nach jeder Rechnung von einem System weiss -- ohne
die Verlaeufe. Ohne Befund lief es nicht, etwa weil ein Baustoff fehlt.

### _fall

```python
def _fall(befund: Systembefund, d: Darstellung, fall: Fall) -> Dict[str, Any]
```

Je Stab und Groesse der kleinste, der groesste und der massgebende Wert
als `[x, Wert]`, je Groesse dieselben ueber alle Staebe mit dem Stab --
und die Lagerkraefte.

### verlauf

```python
def verlauf(befund: Systembefund, name: str) -> Dict[str, Any]
```

Die Bilder eines Falls: je Stab die Proben, je Knoten Verschiebung und
Drehung, und die groesste Verschiebung in mm -- genau, nicht aus den
Proben ([[opencivil.stabwerk.verlauf#Stabverlauf.groesste_verschiebung|groesste_verschiebung]]).

### faelle

```python
def faelle(befund: Optional[Systembefund]) -> List[str]
```

Die Namen der gerechneten Faelle, Lastfaelle zuerst.

### umrisse

```python
def umrisse(system: Stabwerksrechnung, loesung: Any) -> Dict[str, List[List[List[float]]]]
```

Je Querschnitt eines Systems sein Umriss in mm, fuer das Bildchen in
seiner Zeile (Benutzer, 2026-10-24) -- ihn kennt jeder Querschnitt selbst
([[opencivil.stabwerk.stabquerschnitt#Stabquerschnitt.umriss|umriss]]).
Ein Querschnitt, der nicht geht, hat keinen.

### stabachsen

```python
def stabachsen(rechnung: Stabwerksrechnung) -> Dict[str, Dict[str, List[float]]]
```

Je Linie eines Systems ihre Achsen, wie der Rechenkern sie legt
([[opencivil.stabwerk.art#Art|achsen]]) -- auch ohne Rechnung, auch
fuer eine Linie ohne Stab, in den Koordinaten der Zeichnung
([[opencivil.web.balkendaten#Darstellung.stabachsen|Darstellung.stabachsen]]). Eine Linie ohne Laenge hat keine.


## Konstanten

- `PROBEN_JE_STAB = 24` – Wie viele Stuecke ein Stab im Bild mindestens hat -- dazu jede Grenze und jeder Extremwert.
- `EBEN = Darstellung(achsen=('x', 'z'), drehachsen=(None,), groessen={'N': Anz…` – Das 2D-Balkensystem.
- `RAUM = Darstellung(achsen=('x', 'y', 'z'), drehachsen=('x', 'y', 'z'), groes…` – Das 3D-Balkensystem.
- `_DARSTELLUNGEN = {art.EBENE: EBEN, art.RAUM: RAUM}` – Welche Darstellung zu welcher Art der Rechnung gehoert.

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.stabwerk.art]]
- [[opencivil.stabwerk.rechnung]]
- [[opencivil.stabwerk.system]]
- [[opencivil.stabwerk.verlauf]]
- [[opencivil.stabwerk3d.raum]]
- [[opencivil.web.anzeige]]

## Gebraucht von

- [[opencivil.web.api]]
- [[opencivil.web.dienst]]
- [[opencivil.web.systemkatalog]]
- [[opencivil.web.zeichendaten]]
