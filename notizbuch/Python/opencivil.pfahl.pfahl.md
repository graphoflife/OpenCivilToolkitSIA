---
erzeugt: e1b6e9e30864
art: modul
tags: [modul]
---
> [!abstract] opencivil/pfahl/pfahl.py
> ein Einzelpfahl in seinem Baugrund.
> Paket [[opencivil.pfahl]] · [Quelltext](../../opencivil/pfahl/pfahl.py)

## VERANTWORTUNG

Der [[opencivil.pfahl.pfahl#Pfahl|Pfahl]]: Art, Masse und Querschnitt, die Schichten des Baugrunds,
das Grundwasser und die Beiwerte des Widerstands -- als Vorgaben im
Rechenwerk, und nur die, die nach den Wahlen gelten ([[opencivil.pfahl.pfahl#Pfahl.kurznamen|Pfahl.kurznamen]]):

* [[opencivil.pfahl.pfahl#Pfahlart|Pfahlart]] -- Bohrpfahl aus Stahlbeton oder Mikropfahl mit einem
  Tragglied aus Stahl ([[opencivil.pfahl.pfahl#Tragglied|Tragglied]]) in einem Verpresskörper;
* [[opencivil.pfahl.pfahl#Grundlage|Grundlage]] -- worauf der äussere Widerstand R_a,k beruht: auf einer
  Berechnung aus den Schichten, auf Erfahrung oder auf einem Versuch, und
  wie gross der Umrechnungsfaktor η_a darum höchstens ist;
* [[opencivil.pfahl.pfahl#Spitze|Spitze]] und [[opencivil.pfahl.pfahl#Abscheren|Abscheren]] -- ob der Fuss trägt und wie;
* [[opencivil.pfahl.pfahl#Kopf|Kopf]] -- ob sich der Kopf frei drehen kann oder eingespannt ist.

Gerechnet wird in den Nachweisen: äusserer Widerstand in
[[opencivil.pfahl.aussen]], innerer in [[opencivil.pfahl.innen]], der
äussere quer zur Achse in [[opencivil.pfahl.quer]], der innere quer in
[[opencivil.pfahl.innen_quer]] -- und die Steifigkeit
in [[opencivil.pfahl.steifigkeit]]. Welche Kombination den Pfahl quer
belastet, sagt [[opencivil.pfahl.pfahl#Pfahl.quer_belastet|Pfahl.quer_belastet]].


## TIEFEN

z zählt ab Oberkante Terrain nach unten. Der Kopf liegt in der Tiefe t_K,
der Fuss in t_K + L. Über dem Kopf trägt der Boden nur als Auflast.


## DER DURCHMESSER

Beim Bohrpfahl der des Pfahls -- verrohrt aussen an der Verrohrung,
unverrohrt der des Bohrwerkzeugs (SIA 267:2013, 9.5.2.4.7); beim
Mikropfahl der des Verpresskörpers, an dem Mantel und Fuss tragen. Das
Tragglied hat seine eigenen Masse.


## EINHEITEN

SI-Basis.

## Inhalt

### Pfahlart

```python
class Pfahlart(Wahl)
```

Was für ein Pfahl -- daran hängen sein Querschnitt und was der Durchmesser meint.

- `BOHRPFAHL = 'bohrpfahl'`
- `MIKROPFAHL = 'mikropfahl'`

#### Pfahlart.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Pfahlart.erklaerung

```python
@property
def erklaerung(self) -> str
```

### Grundlage

```python
class Grundlage(Wahl)
```

Worauf der charakteristische äussere Widerstand R_a,k beruht -- und
darum, wie gross der Umrechnungsfaktor η_a höchstens ist
(SIA 267:2013, 9.5.2.2.5). Aus einer Berechnung oder aus Erfahrung kommt
R_a,k aus den Schichten, aus einem Versuch wird er eingegeben.

- `BERECHNUNG = 'berechnung'`
- `ERFAHRUNG = 'erfahrung'`
- `DYNAMISCH = 'dynamisch'`
- `STATISCH = 'statisch'`

#### Grundlage.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Grundlage.erklaerung

```python
@property
def erklaerung(self) -> str
```

#### Grundlage.eta_grenze

```python
@property
def eta_grenze(self) -> float
```

Der Grenzwert von η_a.

#### Grundlage.referenz

```python
@property
def referenz(self) -> str
```

Wo der Grenzwert steht.

#### Grundlage.aus_versuch

```python
@property
def aus_versuch(self) -> bool
```

Ob R_a,k eingegeben wird, statt aus den Schichten zu folgen.

### Spitze

```python
class Spitze(Wahl)
```

Ob und wie der Fuss trägt.

- `RECHNEN = 'rechnen'`
- `EINGEBEN = 'eingeben'`
- `KEINE = 'keine'`

#### Spitze.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Spitze.erklaerung

```python
@property
def erklaerung(self) -> str
```

### Abscheren

```python
class Abscheren(Wahl)
```

Wie der Boden am Fuss bricht, drainiert. Das Buch empfiehlt, die
Tragfähigkeitsfaktoren für örtliches Abscheren zu nehmen, mit 2/3 von φ
und c: der volle Spitzendruck stellte sich erst bei grossen Setzungen ein
(Kap. 9.2.7, 12.5).

- `OERTLICH = 'oertlich'`
- `ALLGEMEIN = 'allgemein'`

#### Abscheren.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Abscheren.erklaerung

```python
@property
def erklaerung(self) -> str
```

### Tragglied

```python
class Tragglied(Wahl)
```

Was im Mikropfahl trägt: ein Stahlrohr oder ein Vollstab.

- `ROHR = 'rohr'`
- `STAB = 'stab'`

#### Tragglied.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Tragglied.erklaerung

```python
@property
def erklaerung(self) -> str
```

### Kopf

```python
class Kopf(Wahl)
```

Wie der Pfahlkopf gehalten ist -- daran hängt, was eine Querkraft mit ihm macht.

- `FREI = 'frei'`
- `EINGESPANNT = 'eingespannt'`

#### Kopf.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Kopf.erklaerung

```python
@property
def erklaerung(self) -> str
```

### quer_belastet

```python
def quer_belastet(H: float, M: float, kopf: Kopf) -> bool
```

Ob Kräfte am Kopf den Pfahl quer belasten: eine Querkraft, oder ein Moment
am frei drehbaren Kopf -- am eingespannten ist das Moment Reaktion.

### Kombination

```python
@dataclass(frozen=True)
class Kombination
```

Eine Einwirkung auf den Pfahlkopf: die Normalkraft, Druck positiv, die
Querkraft und das Moment -- das Moment dreht wie die Querkraft, wenn sie
über dem Kopf angreift.

- `name: str`
- `N_Ed: Groesse`
- `H_Ed: Groesse = field(default_factory=lambda: Groesse(0.0, KN))`
- `M_Ed: Groesse = field(default_factory=lambda: Groesse(0.0, KNM))`

#### Kombination.kennung

```python
@property
def kennung(self) -> str
```

### Pfahl

```python
@dataclass
class Pfahl(Rechenobjekt)
```

Siehe Dateikopf.

- `WAS = 'Pfahl'`
- `name: str`
- `praefix: str`
- `art: Pfahlart`
- `D: Groesse`
- `L: Groesse`
- `t_K: Groesse` – Die Tiefe des Pfahlkopfs unter Terrain.
- `t_w: Groesse` – Die Tiefe des höchsten Grundwasserspiegels unter Terrain.
- `gamma_w: Groesse`
- `schichten: Sequence[Pfahlschicht]`
- `grundlage: Grundlage`
- `eta_a: Groesse`
- `R_ak: Groesse`
- `R_ak_zug: Groesse` – R_a,k aus einem Versuch, auf Druck und auf Zug -- nur dann.
- `spitze: Spitze`
- `abscheren: Abscheren`
- `q_b: Groesse` – Der Spitzendruck, charakteristisch -- eingegeben.
- `eta_i: Groesse`
- `stahl: Baustoff` – Die Längsbewehrung des Bohrpfahls, das Tragglied des Mikropfahls.
- `beton: Optional[Baustoff]` – Der Beton des Bohrpfahls -- beim Mikropfahl trägt nur der Stahl.
- `n: Groesse`
- `phi_l: Groesse`
- `c: Groesse`
- `phi_w: Groesse`
- `s_w: Groesse` – Bohrpfahl: Zahl und Durchmesser der Längsstäbe, Überdeckung, Durchmesser und Ganghöhe der Wendel.
- `tragglied: Tragglied`
- `d_a: Groesse`
- `t_r: Groesse`
- `dt: Groesse` – Mikropfahl: Aussendurchmesser und Wanddicke des Tragglieds, Abrostung aussen.
- `kopf: Kopf`
- `t_red: Groesse` – Bis in diese Tiefe unter Terrain wächst die Bettung quer von null an.
- `eta_tr: Groesse` – Der Umrechnungsfaktor des äusseren Widerstands quer zur Achse.
- `definitionen: Dict[str, WertDef] = field(default_factory=dict, init=False)`
- `berechnungen: List[Berechnung] = field(default_factory=list, init=False)`

#### Pfahl.abschnitt

```python
@property
def abschnitt(self) -> Abschnitt
```

Ueberschrift, unter der der Pfahl in der Herleitung steht.

#### Pfahl.bohrpfahl

```python
@property
def bohrpfahl(self) -> bool
```

#### Pfahl.quer_belastet

```python
def quer_belastet(self, k: Kombination) -> bool
```

Ob eine Kombination den Pfahl quer belastet ([[opencivil.pfahl.pfahl#Pfahl.quer_belastet|quer_belastet]]).

#### Pfahl.fuss_traegt

```python
@property
def fuss_traegt(self) -> bool
```

Ob der Fuss trägt: nach der Wahl «Fuss» -- mit R_a,k aus einem Versuch
immer, der Versuch hat den ganzen Pfahl belastet.

#### Pfahl.baustoffe

```python
@property
def baustoffe(self) -> Tuple[Baustoff, ...]
```

Keine eigenen -- Beton und Stahl meldet das Projekt an.

#### Pfahl.stoffe

```python
@property
def stoffe(self) -> Tuple[Baustoff, ...]
```

Die Baustoffe des Querschnitts: Beton und Stahl beim Bohrpfahl, Stahl beim Mikropfahl.

#### Pfahl.profil

```python
def profil(self, e: Eingaben) -> Profil
```

Die Schichten und das Wasser als Zahlen, aus den Eingaben eines Nachweises.

#### Pfahl._gruppen

```python
def _gruppen(self) -> List[Tuple[str, Tuple[tuple, ...]]]
```

Je Kasten der Herleitung seine Vorgaben: Kurzname, Symbol, Einheit,
Beschreibung, Stellen, Grösse, Referenz -- nur, was nach den Wahlen gilt.

#### Pfahl._schichtwert

```python
@staticmethod
def _schichtwert(i: int, s: Pfahlschicht, kurz: str) -> tuple
```

Eine Zahl der Schicht i als Vorgabe; «#» in der Beschreibung steht für die Schicht.

#### Pfahl.kurznamen

```python
def kurznamen(self, *gruppen: str) -> List[str]
```

Die Kurznamen der Vorgaben, die gelten -- aus den genannten Kästen, ohne
Angabe aus allen. Die Schichten heissen zusammen «Schicht».


## Konstanten

- `ETA_I_HOECHSTENS = 0.9` – Wie gross der Umrechnungsfaktor des inneren Widerstands höchstens ist -- nur mit verlässlicher Prüfung der Integrität (SIA 267:2013, 9.5.2.4.9).
- `ETA_I_REGEL = 0.8` – Ohne diese Prüfung, in der Regel (SIA 267:2013, 9.5.2.4.4, (51)).

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.rechenobjekt]]
- [[opencivil.core.wahl]]
- [[opencivil.core.wert]]
- [[opencivil.material.basis]]
- [[opencivil.pfahl.boden]]
- [[opencivil.pfahl.buch]]

## Gebraucht von

- [[opencivil.pfahl.achse]]
- [[opencivil.pfahl.aussen]]
- [[opencivil.pfahl.innen]]
- [[opencivil.pfahl.innen_quer]]
- [[opencivil.pfahl.quer]]
- [[opencivil.pfahl.steifigkeit]]
- [[opencivil.pfahl.uebersicht]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.aufbau.pfahl]]
- [[opencivil.projekt.pfahl]]
- [[opencivil.web.api]]
