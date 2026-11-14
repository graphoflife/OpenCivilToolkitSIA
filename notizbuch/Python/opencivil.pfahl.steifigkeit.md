---
erzeugt: dc085921fb55
art: modul
tags: [modul]
---
> [!abstract] opencivil/pfahl/steifigkeit.py
> wie steif ein Pfahl im Boden steht, und wie er sich verformt.
> Paket [[opencivil.pfahl]] · [Quelltext](../../opencivil/pfahl/steifigkeit.py)

## VERANTWORTUNG

Die Prozedur [[opencivil.pfahl.steifigkeit#Pfahlsteifigkeit|Pfahlsteifigkeit]]: der Pfahl als Stab auf Federn
([[opencivil.pfahl.bettung|.bettung]]), längs und quer. Sie liefert

* die Federn am Kopf mit dem charakteristischen Verformungsmodul E_s,k
  (SIA 267:2013, 5.3.2.8): längs auf Druck k_v und auf Zug k_v,Z, quer bei
  frei drehbarem Kopf k_h, dazu die Steifigkeitsmatrix des Kopfs -- K_HH,
  K_HM, K_MM -- für ein Modell des Tragwerks darüber. Sie hängen an keiner
  Kombination und stehen als Kennzahlen unter dem Pfahl;
* je Kombination die Verläufe über die Tiefe, mit E_s,d = E_s,k / γ_E
  (5.3.2.5): Setzung und Normalkraft, Verschiebung, Verdrehung, Moment,
  Querkraft und Bettungsdruck -- im Befund ([[opencivil.pfahl.steifigkeit#Steifigkeitsbefund|Steifigkeitsbefund]]).


## DIE FEDERN DES BODENS

* am Mantel je Meter Pfahl k_l = B · π · D mit B ≈ 0.42 · E_s (Cassan,
  Kap. 12.8) -- null in einer Schicht, deren Mantelreibung als null
  eingegeben ist: Cassan zählt nur die Schicht, in der der Pfahl trägt;
* am Fuss K_b = A_b · R / D = π · D · R / 4 mit R ≈ 4.5 · E_s der Schicht am
  Fuss: Cassan setzt dort σ_F = R · s / D -- nur auf Druck, und nur, wo der
  Fuss trägt ([[opencivil.pfahl.pfahl#Pfahl.fuss_traegt|fuss_traegt]]);
* quer k_s = E_s / D (SIA 267:2013, 9.5.4.5, (53)), je Meter Pfahl also
  k_s · D = E_s, vom Terrain bis in die Tiefe t_red von null an linear
  wachsend.


## DIE FEDERN AM KOPF

Das System ist linear; abgelesen wird an einer Probelast von 1 MN. Quer
zweimal: mit frei drehbarem Kopf (k_h = H / y_0) und mit eingespanntem
(K_HH = H / y_0, K_HM = M_0 / y_0, M_0 die Reaktion). Weil k_h = K_HH −
K_HM² / K_MM, folgt daraus die Drehfeder K_MM ohne dritte Rechnung.


## NACH VORGABE, NICHT NACHGESCHLAGEN (notizbuch/Notizen/TODO.md)

* Die Abminderung nahe dem Terrain, linear von null bis t_red: die Norm
  verlangt nur, k_s dort abzumindern, das Buch sagt, die Stützkraft an der
  Oberfläche sei null (Kap. 12.10).
* Der Mikropfahl mit Cassans Werten für Bohrpfähle.
* Der Querschnitt ungerissen und ohne Bewehrung: beim Bohrpfahl der Beton
  mit E_cm, beim Mikropfahl das Tragglied allein, ohne den Mörtel.
* γ_E = 1.5, der kleinste Wert, den 5.3.2.5 zulässt.
* Längs und quer getrennt: keine Rechnung nach Theorie zweiter Ordnung
  (9.5.3.4.3 verlangt dafür eine eigene Untersuchung).
* Keine Feder am Mantel, wo q_s,k null eingegeben ist; eine Feder am Fuss,
  wo R_a,k aus einem Versuch kommt.


## EINHEITEN

SI-Basis.

## Inhalt

### Baugrund

```python
@dataclass(frozen=True)
class Baugrund
```

Was die Bettung aus den Eingaben braucht, in SI -- z ab Terrain.

- `grenzen: Tuple[Tuple[float, float], ...]`
- `E_s: Tuple[float, ...]`
- `mantel: Tuple[bool, ...]` – Je Schicht, ob der Mantel in ihr trägt -- sonst hat er längs keine Feder.
- `t_K: float`
- `L: float`
- `D: float`
- `t_red: float`

#### Baugrund.z_F

```python
@property
def z_F(self) -> float
```

#### Baugrund.stuecke

```python
def stuecke(self) -> List[Tuple[int, float, float]]
```

Je Schicht das Stück des Pfahls in ihr: Schicht, Ober- und Unterkante.

#### Baugrund.schicht_am_fuss

```python
def schicht_am_fuss(self) -> int
```

Die Schicht, auf der der Fuss steht -- an einer Grenze die untere.

#### Baugrund.abminderung

```python
def abminderung(self, z: float) -> float
```

Wie viel der Bettung quer in der Tiefe z wirkt: bis t_red linear von null an.

#### Baugrund.strecken

```python
def strecken(self, gamma: float) -> List[Strecke]
```

Die Strecken des Pfahls, z ab Kopf, mit E_s / `gamma`: je Schicht
eine, an t_red geteilt -- darüber wächst die Bettung quer linear.

#### Baugrund.fussfeder

```python
def fussfeder(self, gamma: float) -> float
```

K_b = π · D · R / 4 mit R = 4.5 · E_s / `gamma` der Schicht am Fuss.

### Verlauf

```python
@dataclass(frozen=True)
class Verlauf
```

Was eine Kombination mit dem Pfahl macht, über die Tiefe ab Terrain, in
SI. Quer nur, wo eine Querkraft oder ein Moment am Kopf wirkt.

- `name: str`
- `N_Ed: float`
- `H_Ed: float`
- `M_Ed: float`
- `z: List[float]`
- `w: List[float]`
- `N: List[float]`
- `N_b: float` – Die Kraft der Feder am Fuss.
- `y: Optional[List[float]] = None`
- `theta: Optional[List[float]] = None`
- `M: Optional[List[float]] = None`
- `V: Optional[List[float]] = None`
- `p: Optional[List[float]] = None` – Der Bettungsdruck: die Bettungskraft je Meter durch D, in Pa.

#### Verlauf.quer

```python
@property
def quer(self) -> bool
```

### Steifigkeitsbefund

```python
@dataclass
class Steifigkeitsbefund
```

Die Verläufe je Kombination, für Bild und Zusammenfassung.

- `eingespannt: bool`
- `verlaeufe: List[Verlauf] = field(default_factory=list)`

### _extrem

```python
def _extrem(z: Sequence[float], werte: Sequence[float]) -> Tuple[float, float]
```

Der Wert mit dem grössten Betrag und seine Tiefe.

### Pfahlsteifigkeit

```python
class Pfahlsteifigkeit(Prozedur)
```

Siehe Dateikopf.

- `THEMA = 'Pfahlsteifigkeit'`

#### Pfahlsteifigkeit.kennung

```python
@staticmethod
def kennung(pfahl: Pfahl) -> str
```

Unter welcher Kennung die Steifigkeit eines Pfahls rechnet -- und ihr Befund steht.

#### Pfahlsteifigkeit.rechne

```python
def rechne(self, e: Eingaben, p: Protokoll) -> Ausfuehrung
```

#### Pfahlsteifigkeit._querschnitt

```python
def _querschnitt(self, e: Eingaben, p: Protokoll, werte: Zwischenwerte) -> Tuple[Wert, Wert]
```

EA und EI: der Beton des Bohrpfahls, das Tragglied des Mikropfahls.

#### Pfahlsteifigkeit._bettung

```python
def _bettung(self, e: Eingaben, p: Protokoll, werte: Zwischenwerte, grund: Baugrund) -> None
```

Die Federn des Bodens, charakteristisch: je Schicht als Tabelle, dazu der Fuss.

#### Pfahlsteifigkeit._kombinationen

```python
def _kombinationen(self, p: Protokoll, grund: Baugrund, EA: float, EI: float, schritt: float, befund: Steifigkeitsbefund) -> None
```

Die Verläufe mit E_s,d = E_s,k / γ_E: längs immer, quer, wo eine Last quer wirkt.

#### Pfahlsteifigkeit._tabellen

```python
def _tabellen(self, p: Protokoll, befund: Steifigkeitsbefund) -> None
```

Je Kombination die Werte am Kopf und die grössten über die Tiefe.


## Konstanten

- `GAMMA_E = 1.5` – Der Widerstandsbeiwert des Verformungsmoduls, wo eine zu kleine Steifigkeit zum Versagen führt -- der kleinste, den die Norm zulässt.
- `GAMMA_E_REFERENZ = 'SIA 267:2013, 5.3.2.5'`
- `PROBE = 1000000.0` – Die Probelast am Kopf, an der die Federn abgelesen werden, in N und Nm.
- `SCHRITT_LAMBDA = 0.2` – So lang ist ein Element höchstens, gemessen an der elastischen Länge 1/λ.
- `FEDERN = (('k_v', 'k_v', MN_PRO_M, 0, 'Längsfeder auf Druck', 'N/w am Kopf, mi…` – Die Federn am Kopf, als Kennzahlen: Kurzname, Zeichen, Einheit, Stellen, Beschriftung, Erklärung. Quer zwei Stellen: ein Mikropfahl ist dort rund tausendmal weicher als ein Bohrpfahl, seine Drehfeder etwa 0.15 MNm/rad.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.pfahl.bettung]]
- [[opencivil.pfahl.boden]]
- [[opencivil.pfahl.buch]]
- [[opencivil.pfahl.pfahl]]

## Gebraucht von

- [[opencivil.projekt.aufbau.pfahl]]
- [[opencivil.web.pfahldaten]]

## Formeln aus diesem Modul

- [[Abgeminderte Bettung am Terrain]] · `Pfahlsteifigkeit._bettung`
- [[Bemessungswert des Verformungsmoduls]] · `Pfahlsteifigkeit._kombinationen`
- [[Bettungsmodul quer zum Pfahl]] · `Pfahlsteifigkeit._bettung`
- [[Biegesteifigkeit des Pfahls]] · `Pfahlsteifigkeit._querschnitt`
- [[Dehnsteifigkeit des Pfahls]] · `Pfahlsteifigkeit._querschnitt`
- [[Drehfeder des Pfahlkopfs]] · `Pfahlsteifigkeit._federn`
- [[Feder am Pfahlfuss]] · `Pfahlsteifigkeit._bettung`
- [[Feder am Pfahlmantel]] · `Pfahlsteifigkeit._bettung`
- [[Gebetteter Pfahl]] · `Pfahlsteifigkeit._federn`
- [[Kopplung am Pfahlkopf]] · `Pfahlsteifigkeit._federn`
- [[Längsfeder des Pfahlkopfs]] · `Pfahlsteifigkeit._federn`
- [[Querfeder des eingespannten Pfahlkopfs]] · `Pfahlsteifigkeit._federn`
- [[Querfeder des frei drehbaren Pfahlkopfs]] · `Pfahlsteifigkeit._federn`
