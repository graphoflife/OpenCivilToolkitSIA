---
erzeugt: 5e8bb5e47382
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
  Drehsteifigkeit, und je Fall die Extremwerte und die Lagerkraefte;
* auf Anfrage die Verlaeufe eines Falls fuer die Bilder ([[opencivil.web.balkendaten#verlauf|verlauf]]):
  je Stab seine Lage und Proben der Schnittgroessen und der Verschiebung,
  je Knoten seine Verschiebung und Drehung -- oder dass seine Drehung nicht
  bestimmbar ist;
* je Querschnitt sein Umriss fuer das Bildchen in seiner Zeile
  ([[opencivil.web.balkendaten#umrisse|umrisse]]);
* im Raum je Linie ihre Achsen ([[opencivil.web.balkendaten#stabachsen|stabachsen]]), fuer die gestrichelte
  Faser und die Lasten in den Richtungen des Stabs.


## EBEN UND IM RAUM IN EINER FORM

Was sich unterscheidet -- die Achsen, die Groessen, die Lagerkraefte --,
steht je einmal in einer [[opencivil.web.balkendaten#Darstellung|Darstellung]] ([[opencivil.web.balkendaten#Konstanten|EBEN]], [[opencivil.web.balkendaten#Konstanten|RAUM]]);
welche gilt, sagt die Art des Befunds. Eine Lage oder Verschiebung ist eine
Liste mit einer Zahl je Achse des Systems -- `[x, z]` in der Ebene,
`[x, y, z]` im Raum --, die Drehung eines Knotens eine Liste mit einer Zahl
je Drehachse. Ein Stab hat seine Achsen im System: `x` laengs, `z` zur
gestrichelten Faser, im Raum dazu `y` ([[opencivil.stabwerk3d.stab]]) --
dorthin traegt ein Bild einen positiven Wert auf.

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
- `lage: Callable[[Any], Dict[str, Any]]` – Anfang und Achsen eines Stabs im System, aus seinem Verlauf.

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

### verlauf

```python
def verlauf(befund: Systembefund, name: str) -> Dict[str, Any]
```

Die Bilder eines Falls: je Stab die Proben, je Knoten Verschiebung und Drehung.

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
def stabachsen(system: Raumsystem) -> Dict[str, Dict[str, List[float]]]
```

Je Linie eines Systems im Raum ihre Achsen `x`, `y` und `z` im
System -- wie der Rechenkern sie legt ([[opencivil.stabwerk3d.stab#achsen|achsen]]),
auch ohne Rechnung. Eine Linie ohne Laenge hat keine.


## Konstanten

- `PROBEN_JE_STAB = 24` – Wie viele Stuecke ein Stab im Bild mindestens hat -- dazu jede Grenze und jeder Extremwert.
- `EBEN = Darstellung(achsen=('x', 'z'), drehachsen=(None,), groessen={'N': Anz…` – Das 2D-Balkensystem.
- `RAUM = Darstellung(achsen=('x', 'y', 'z'), drehachsen=('x', 'y', 'z'), groes…` – Das 3D-Balkensystem.
- `_DARSTELLUNGEN = {Systembefund: EBEN, Raumbefund: RAUM}` – Welche Darstellung zu welchem Befund gehoert -- nach seiner Klasse.

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.stabwerk.rechnung]]
- [[opencivil.stabwerk.system]]
- [[opencivil.stabwerk3d.modell]]
- [[opencivil.stabwerk3d.rechnung]]
- [[opencivil.stabwerk3d.stab]]
- [[opencivil.web.anzeige]]

## Gebraucht von

- [[opencivil.web.api]]
- [[opencivil.web.dienst]]
- [[opencivil.web.systemkatalog]]
- [[opencivil.web.zeichendaten]]
