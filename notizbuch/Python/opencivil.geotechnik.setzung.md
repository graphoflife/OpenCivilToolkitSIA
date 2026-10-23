---
erzeugt: 5316108404a2
art: modul
tags: [modul]
---
> [!abstract] opencivil/geotechnik/setzung.py
> die Setzung eines Flachfundaments auf geschichtetem Baugrund.
> Paket [[opencivil.geotechnik]] · [Quelltext](../../opencivil/geotechnik/setzung.py)

## VERANTWORTUNG

Das [[opencivil.geotechnik.setzung#Setzungsfundament|Setzungsfundament]] -- die Lastfläche L × B, die Pressungen in der
Sohle, die zulässige Setzung und die Schichten des Baugrunds mit ihren
M_E-Werten, als Vorgaben im Rechenwerk -- und der Nachweis [[opencivil.geotechnik.setzung#Setzung|Setzung]]:
s ≤ s_zul.


## DAS VERFAHREN (Kap. 8.2 bis 8.5)

Jede Schicht wird in gleich dicke Teilschichten von höchstens Δz_max
zerlegt; eine Schichtgrenze ist immer auch eine Grenze von Teilschichten. Je
Teilschicht:

```
Δs = J̄ · q_W · Δz / M'_E + J̄ · q_E · Δz / M_E        J̄ = (J_o + J_u) / 2
```

Die Pressung aus Wiederbelastung q_W rechnet mit dem Modul der
Wiederbelastung M'_E, die aus Erstbelastung q_E mit dem der Erstbelastung M_E
(Kap. 8.5); beide gibt der Benutzer getrennt an. J̄ mittelt den
Einflussfaktor an Ober- und Unterkante, wie die Spalte «J_K mittel» der
Tabelle 8.4. Die Setzung ist die Summe über alle Teilschichten; unter der
untersten Schicht gilt der Baugrund als unzusammendrückbar (Bild 8.1).


## DER EINFLUSSFAKTOR (Kap. 8.2)

Die Zusatzspannung unter einer gleichmässig belasteten Rechteckfläche nach
Boussinesq, Δσ'_z = J · q. Unter einer Ecke eines Rechtecks a × b in der
Tiefe z ([[opencivil.geotechnik.setzung#einflussfaktor_ecke|einflussfaktor_ecke]]):

```
J_E = 1/(2π) · [arctan(a b / (z R)) + a b z / R · (1/(a² + z²) + 1/(b² + z²))]
R   = √(a² + b² + z²)
```

Unter einem anderen Punkt der Fläche die Summe der vier Rechtecke, die sich in
ihm treffen ([[opencivil.geotechnik.setzung#einflussfaktor|einflussfaktor]]). Welcher Punkt, sagt die
[[opencivil.geotechnik.setzung#Steifigkeit|Steifigkeit]] (Kap. 8.10): beim starren Fundament der kennzeichnende
Punkt K, 0.13 L und 0.13 B von einer Ecke (Bild 8.15) -- dort setzt sich die
schlaffe Last so stark, wie sich das starre Fundament im Mittel setzt; beim
schlaffen die Mitte, wo die Setzungsmulde am tiefsten ist.


## QUELLE

Das Kapitel 8 «Setzungsberechnung», das der Benutzer geliefert hat; der
Abschnitt steht an jeder Formel. Die Formel für J_E steht dort nicht -- das
Kapitel verweist auf Kapitel 3, das nicht vorliegt. Sie gibt die Werte J_K
der Tabelle 8.4 auf die gedruckte Stelle wieder und die Grenztiefen der
Tabelle 8.5 so genau, wie sie dort stehen (tests/test_setzung.py); nicht
nachgeschlagen (notizbuch/Notizen/TODO.md).


## EINHEITEN

Alles in SI-Basis.

## Inhalt

### Steifigkeit

```python
class Steifigkeit(Wahl)
```

Ob das Fundament der Setzungsmulde folgt -- und darum, unter welchem Punkt
gerechnet wird (Kap. 8.10).

- `STARR = 'starr'`
- `SCHLAFF = 'schlaff'`

#### Steifigkeit.beschriftung

```python
@property
def beschriftung(self) -> str
```

Wie sie an der Maske heisst.

#### Steifigkeit.punkt

```python
@property
def punkt(self) -> str
```

Wie der Punkt heisst, unter dem gerechnet wird.

#### Steifigkeit.lage

```python
def lage(self, L: float, B: float) -> Tuple[float, float]
```

Wo dieser Punkt liegt, von einer Ecke aus: längs L und längs B, in m.

### einflussfaktor_ecke

```python
def einflussfaktor_ecke(a: float, b: float, z: float) -> float
```

J_E unter einer Ecke der gleichmässig belasteten Rechteckfläche a × b, in
der Tiefe z -- in m. In der Sohle ein Viertel: die vier Rechtecke um einen
Punkt tragen dort zusammen die ganze Pressung.

### einflussfaktor

```python
def einflussfaktor(L: float, B: float, x: float, y: float, z: float) -> float
```

J unter dem Punkt (x, y) der Fläche L × B, in der Tiefe z: die vier
Rechtecke, die sich in ihm treffen. x längs L, y längs B, von einer Ecke
aus; alles in m.

### einflusslinie

```python
def einflusslinie(L: float, B: float, x: float, y: float, tiefe: float, schritte: int=60) -> List[Tuple[float, float]]
```

J über die Tiefe, von der Sohle bis `tiefe` -- für das Bild. Die
Schritte werden zur Sohle hin dichter: dort ändert sich J am schnellsten.

### Schicht

```python
@dataclass(frozen=True)
class Schicht
```

Eine Schicht des Baugrunds, von der Sohle an nach unten gezählt.

- `name: str`
- `d: Groesse` – Die Dicke der Schicht.
- `M_E: Groesse` – Der M_E-Wert der Erstbelastung.
- `M_E_strich: Groesse` – Der M_E-Wert der Wiederbelastung, M'_E.

### Setzungsfundament

```python
@dataclass
class Setzungsfundament
```

Ein Flachfundament auf geschichtetem Baugrund: die Eingaben als Vorgaben
im Rechenwerk. `B` und `L` sind die Seiten der Lastfläche; die
Schichten liegen von der Sohle an nach unten, z wird ab der Sohle gemessen.

- `name: str`
- `B: Groesse`
- `L: Groesse`
- `q_W: Groesse`
- `q_E: Groesse`
- `s_zul: Groesse`
- `dz: Groesse`
- `steifigkeit: Steifigkeit`
- `schichten: Sequence[Schicht]`
- `praefix: str`
- `definitionen: Dict[str, WertDef] = field(default_factory=dict, init=False)`
- `berechnungen: List[Berechnung] = field(default_factory=list, init=False)`

#### Setzungsfundament.abschnitt

```python
@property
def abschnitt(self) -> Abschnitt
```

Ueberschrift, unter der das Fundament in der Herleitung steht.

#### Setzungsfundament.id_von

```python
def id_von(self, kurzname: str) -> str
```

#### Setzungsfundament.ins_rechenwerk

```python
def ins_rechenwerk(self, werk) -> 'Setzungsfundament'
```

### Teilschicht

```python
@dataclass(frozen=True)
class Teilschicht
```

Eine Zeile der Tabelle: Tiefen in m ab der Sohle, Setzungen in m.

- `schicht: int` – Die Schicht, in der sie liegt -- ihr Platz in der Liste, ab null.
- `z_o: float`
- `z_u: float`
- `J_o: float`
- `J_u: float`
- `ds_W: float`
- `ds_E: float`

#### Teilschicht.mittel

```python
@staticmethod
def mittel(J_o: float, J_u: float) -> float
```

Der Einflussfaktor einer Teilschicht: an Ober- und Unterkante gemittelt (Tabelle 8.4).

#### Teilschicht.J

```python
@property
def J(self) -> float
```

### Schichtsetzung

```python
@dataclass(frozen=True)
class Schichtsetzung
```

Was eine Schicht zur Setzung beiträgt -- Tiefen in m ab der Sohle, Setzungen in m.

- `name: str`
- `z_o: float`
- `z_u: float`
- `s_W: float`
- `s_E: float`

#### Schichtsetzung.s

```python
@property
def s(self) -> float
```

### Setzungsbefund

```python
@dataclass
class Setzungsbefund
```

Was ausser dem Erfüllungsgrad bleibt -- für die Zusammenfassung und das Bild.

- `punkt: Tuple[float, float]` – Wo gerechnet wurde, von einer Ecke aus: längs L und längs B, in m.
- `teilschichten: List[Teilschicht]`
- `schichten: List[Schichtsetzung]`
- `J_fuss: float` – Der Einflussfaktor am Fuss der untersten Schicht.

#### Setzungsbefund.s_W

```python
@property
def s_W(self) -> float
```

#### Setzungsbefund.s_E

```python
@property
def s_E(self) -> float
```

#### Setzungsbefund.s

```python
@property
def s(self) -> float
```

### Setzung

```python
class Setzung(Nachweis)
```

Die Setzung unter dem Punkt, den die Steifigkeit des Fundaments
bestimmt, gegen die zulässige: s ≤ s_zul, der Erfüllungsgrad s_zul / s.

- `THEMA = 'Setzung'`
- `ART = 's'`

#### Setzung.pruefe

```python
def pruefe(self, e: Eingaben, p: Protokoll) -> Ausfuehrung
```

#### Setzung._punkt

```python
def _punkt(self, e: Eingaben, p: Protokoll) -> Tuple[float, float]
```

Wo gerechnet wird -- K oder die Mitte --, mit der Formel für J darunter.

#### Setzung._teilschichten

```python
def _teilschichten(self, e: Eingaben, p: Protokoll, x: float, y: float) -> List[Teilschicht]
```

Jede Schicht in gleich dicke Teilschichten, je eine Zeile der Tabelle.

#### Setzung._schichten

```python
def _schichten(self, e: Eingaben, p: Protokoll, teile: Sequence[Teilschicht], x: float, y: float) -> Setzungsbefund
```

Die Teilschichten je Schicht zusammengezählt -- und was am Fuss noch ankommt.

#### Setzung._fall

```python
@property
def _fall(self) -> str
```

Wie die Zeile der Zusammenfassung heisst: unter welchem Punkt gerechnet wurde.

### angaben

```python
def angaben(fundament: Setzungsfundament, werte: Dict[str, Wert]) -> GleichungBlock
```

Die Angaben über der Tabelle, aus den Werten der Lösung, wie sie gerechnet
wurden: die Lastfläche, die Pressungen und wo gerechnet wird.

### schichttabelle

```python
def schichttabelle(fundament: Setzungsfundament, werte: Dict[str, Wert], befund: Setzungsbefund) -> TabellenBlock
```

Die Schichten, wie man sie im Schnitt sieht: Tiefe, M_E-Werte und ihr Beitrag zur Setzung.


## Konstanten

- `K = 0.13` – Wo der kennzeichnende Punkt K liegt: 0.13 L und 0.13 B von einer Ecke (Bild 8.15).
- `KAP_PRINZIP = 'Kap. 8.2'` – Die Abschnitte des gelieferten Kapitels, an den Formeln als Referenz.
- `KAP_TABELLE = 'Kap. 8.3, Tabelle 8.4'`
- `KAP_EINFLUSSTIEFE = 'Kap. 8.4'`
- `KAP_WIEDERBELASTUNG = 'Kap. 8.5'`
- `KAP_STEIFIGKEIT = 'Kap. 8.10, Bild 8.15'`
- `MODUL = MN_PRO_M2.latex` – Die Einheit der M_E-Werte in den Köpfen der Tabellen.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wahl]]
- [[opencivil.core.wert]]

## Gebraucht von

- [[opencivil.bericht.zusammenfassung]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.aufbau.setzung]]
- [[opencivil.projekt.setzung]]
- [[opencivil.web.api]]
- [[opencivil.web.setzungsdaten]]

## Formeln aus diesem Modul

- [[Einflussfaktor der Rechtecklast]] · `Setzung._punkt`
- [[Gesamtsetzung]] · `Setzung._nachweis`
- [[Lage des Punktes längs B]] · `Setzung._punkt`
- [[Lage des Punktes längs L]] · `Setzung._punkt`
- [[Setzung aus Erstbelastung]] · `Setzung._nachweis`
- [[Setzung aus Wiederbelastung]] · `Setzung._nachweis`
- [[Setzung einer Teilschicht]] · `Setzung.pruefe`
