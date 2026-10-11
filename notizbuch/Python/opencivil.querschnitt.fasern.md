---
erzeugt: e52c26335a28
art: modul
tags: [modul]
---
> [!abstract] opencivil/querschnitt/fasern.py
> Der Querschnitt als Summe von Fasern.
> Paket [[opencivil.querschnitt]] · [Quelltext](../../opencivil/querschnitt/fasern.py)

## VERANTWORTUNG

Zwei Dinge, die jede Rechnung an einer ebenen Dehnungsverteilung braucht,
gleich ob Platte oder gezeichneter Querschnitt:

1. **Die inneren Kraefte einer Dehnungsebene.** Fasern mit Lage, Flaeche und
   Werkstoffgesetz, dazu Staebe, die das Material an ihrer Stelle verdraengen.
2. **Die Dehnungsgrenzen.** In welchem Bereich die Ebene liegen darf, damit
   jedes Werkstoffgesetz gilt.


## DIE EBENE


```python
eps(v) = eps_m + chi * v
```

`v` ist der Abstand zur Bezugsachse, gemessen in Zugrichtung: bei der
Platte `z - h/2` (z von oben nach unten), beim gezeichneten Querschnitt der
Abstand vom Schwerpunkt entlang der Zugrichtung. Ein positives `chi` zieht
also auf der Seite, auf die `v` waechst.

`quer` ist die Lage einer Faser entlang der Nulllinie. Nur wer auch das
Moment um die zweite Achse braucht -- die schiefe Biegung -- gibt sie an. Die
Platte gibt sie nicht an, und ihre Schleife bleibt so schnell wie bisher.


## GESETZE MIT SPRUNG

Gelesen wird die Spannung in der Mitte jeder Faser. Bei einem stetigen Gesetz
ist das genau genug. Springt es -- der Spannungsblock --, springt mit jeder
Faser, die den Knick ueberschreitet, auch N, und keine Ebene trifft eine
verlangte Normalkraft genau. Ein solches Gesetz hat darum ``mittel(eps_a,
eps_b)``, die mittlere Spannung ueber einen linear verlaufenden Bereich. Wo
eine Faser ihre Dicke kennt (`dicken`, beim Stab `dicke` fuer das
verdraengte Material), wird damit gemittelt.


## DIE GRENZEN

Jede Grenze ist eine Stelle `v` mit einem zulaessigen Dehnungsbereich. Weil
die Ebene linear ist, wird daraus in `(eps_m, chi)` je Grenze ein Streifen
zwischen zwei Geraden, zusammen ein konvexes Vieleck. Bei festem `chi` ist
sein Schnitt das Fenster fuer `eps_m` -- das braucht der Loeser in
[[opencivil.nachweis.querschnittsloeser]]. Sein Rand ist der
Dehnungsfaecher -- das braucht die Interaktionslinie. Eine Regel, zwei Nutzer.


## EINHEITEN

SI-Basis wie im ganzen Querschnittsmodul: Meter, Quadratmeter, Pascal.

## Inhalt

### Schnittkraefte

```python
@dataclass(frozen=True)
class Schnittkraefte
```

Was eine Dehnungsebene an inneren Kraeften erzeugt.

- `N: float` – in N, Zug positiv.
- `M: float` – in Nm um die Bezugsachse: `Σ F·v`.
- `M_quer: float = 0.0` – in Nm, der Arm entlang der Nulllinie: `Σ F·quer`. Nur bei schiefer Biegung; sonst null.

### Fasergruppe

```python
@dataclass(frozen=True)
class Fasergruppe
```

Fasern aus einem Werkstoff.

`flaechen` ist eine Zahl, wenn alle Fasern gleich gross sind -- dann
laeuft die Summe ohne Nachschlagen, und das ist die Schleife, die bei der
Platte hunderttausendfach laeuft. Sonst eine Flaeche je Faser.

- `gesetz: Gesetz`
- `arme: Tuple[float, ...]`
- `flaechen: Union[float, Tuple[float, ...]]`
- `quer: Optional[Tuple[float, ...]] = None`
- `dicken: Optional[Tuple[float, ...]] = None` – Ausdehnung jeder Faser in `v` -- gebraucht, wenn das Gesetz springt.

### Stab

```python
@dataclass(frozen=True)
class Stab
```

Ein Bewehrungsstab -- oder ein Stueck einer verschmierten Stablinie.

`verdraengt` ist das Gesetz des Materials, in dem er liegt: an seiner
Stelle zaehlt der Stab, nicht der Beton, sonst zaehlte dieselbe Flaeche
zweimal.

- `arm: float`
- `flaeche: float`
- `gesetz: Gesetz`
- `verdraengt: Optional[Gesetz] = None`
- `quer: float = 0.0`
- `dicke: float = 0.0` – Ausdehnung in `v` fuer das verdraengte Material, wenn dessen Gesetz springt.

### Faserquerschnitt

```python
class Faserquerschnitt
```

Fasergruppen und Staebe -- und die Kraefte, die eine Ebene in ihnen weckt.

#### Faserquerschnitt.kraefte

```python
def kraefte(self, eps_m: float, chi: float) -> Schnittkraefte
```

Die inneren Kraefte der Ebene `eps(v) = eps_m + chi·v`.

Ortsgebundene Namen statt `self.`: diese Schleife laeuft je Nachweis
hunderttausende Male, und jeder Zugriff ueber ein Attribut kostet darin
eine Suche.

### _mittel

```python
def _mittel(gesetz: Optional[Gesetz]) -> Optional[Callable[[float, float], float]]
```

Die mittlere Spannung des Gesetzes ueber einen Bereich -- wenn es sie kennt.

### Dehnungsgrenze

```python
@dataclass(frozen=True)
class Dehnungsgrenze
```

An der Stelle `arm` muss die Dehnung zwischen `eps_min` und `eps_max` liegen.

- `arm: float`
- `eps_min: float` – Groesste zulaessige Stauchung, negativ.
- `eps_max: float` – Groesste zulaessige Dehnung, positiv; `inf`, wo es keine gibt.

### Dehnungsgrenzen

```python
class Dehnungsgrenzen
```

Die Grenzen eines Querschnitts -- und was aus ihnen fuer die Ebene folgt.

#### Dehnungsgrenzen.fenster

```python
def fenster(self, chi: float) -> Optional[Tuple[float, float]]
```

In welchem Bereich `eps_m` liegen darf, damit an keiner Grenze die
Dehnung aus ihrem Bereich faellt -- bei dieser Kruemmung.

Jede Grenze verlangt `eps_min <= eps_m + chi·arm <= eps_max`. Ist das
Fenster leer, ist die Kruemmung fuer diesen Querschnitt zu gross.

#### Dehnungsgrenzen.kruemmungsfenster

```python
def kruemmungsfenster(self, eps_m: float) -> Optional[Tuple[float, float]]
```

In welchem Bereich `chi` liegen darf, damit an keiner Grenze die
Dehnung aus ihrem Bereich faellt -- bei dieser Dehnung `eps_m` im
Bezugspunkt. Das Gegenstueck zu [[opencivil.querschnitt.fasern#Dehnungsgrenzen.fenster|fenster]], fuer Linien, die
ueber die Dehnung statt ueber die Kruemmung laufen.

Unbegrenzt bleibt eine Seite nie: dafuer sorgen zwei Grenzen auf
verschiedenen Seiten des Bezugspunkts, und jeder Querschnitt hat zwei
Raender.

#### Dehnungsgrenzen.kruemmungsgrenze

```python
def kruemmungsgrenze(self, *, positiv: bool) -> float
```

Die groesste Kruemmung (als Betrag), bei der noch ein Fenster bleibt.

Fuer jedes Paar von Grenzen `k` und `l`, deren Abstand die
Kruemmung dehnt, gilt `|chi| <= (eps_max_l - eps_min_k) / Abstand`.
Massgebend ist das engste Paar. Bei der Platte ist das eines: die
Unterkante gegen die Oberkante, `(eps_zug + eps_druck) / h`.


## Gebraucht von

- [[opencivil.nachweis.dehnungsfaecher]]
- [[opencivil.nachweis.querschnittsloeser]]
- [[opencivil.querschnitt.interaktion]]
