---
erzeugt: 108ed713e76f
art: modul
tags: [modul]
---
> [!abstract] opencivil/stahlbau/klasse.py
> die Querschnittsklasse nach SIA 263:2013.
> Paket [[opencivil.stahlbau]] · [Quelltext](../../opencivil/stahlbau/klasse.py)

## VERANTWORTUNG

Die Regeln, nach denen ein Blech in eine Querschnittsklasse faellt: die
Grenzschlankheiten der Tabellen 5a (beidseitig gestuetzte Scheiben und das
Rundrohr) und 5b (einseitig gestuetzte) mit `ε` -- und fuer die Klasse 4
die mitwirkende Breite nach 4.5.3, mit den kleinsten Beulwerten der
Tabelle 9 -- im Kasten mit dem genaueren Abminderungsfaktor (70). Woher `α` und `ψ` kommen und wo ein Blech liegt, weiss der
Querschnitt ([[opencivil.stahlbau.querschnitt]]); hier stehen nur die
Formeln der Norm, jede an einer Stelle.

α UND ψ:
`α` ist der Anteil der Breite, der plastisch gedrueckt ist, `ψ` das
Verhaeltnis der elastischen Spannungen an den Raendern, Druck positiv: 1 bei
gleichmaessigem Druck, -1 bei Biegung um die Mitte. Beim einseitig
gestuetzten Blech zaehlt dazu, welcher Rand staerker gedrueckt ist: der
freie (Tabelle 5b, mittlere Zeilen, `k₁`) oder der gehaltene (untere,
`k₂`) -- plastisch und elastisch je fuer sich, denn die beiden Nulllinien
muessen nicht parallel liegen. Gedrueckt ist ganz, was `α = 1` und `ψ = 1` hat: dafuer nennt
Tabelle 5b eigene Grenzen, 14 ε statt 21 ε √k₁ = 13.8 ε.


## AUSSERHALB DER BEREICHE

nach Vorgabe, nicht nachgeschlagen
`k₁` gilt fuer ψ ≥ -3, `k₂` fuer ψ ≥ -1 und der kleinste Beulwert der
beidseitig gelenkig gelagerten Scheibe fuer ψ ≥ -1.2. Darunter gilt der Wert
am Rand des Bereichs: alle drei wachsen, je weiter ψ faellt -- der Randwert
liegt auf der sicheren Seite. Ebenso der Beulwert eines einseitig gehaltenen
Blechs fuer seine mitwirkende Breite: Tabelle 9 nennt ihn nur fuer ψ = 1, 0
und -1, und dort trifft ihn `k₁` oder `k₂` der Tabelle 5b auf 1 %. Und
(70) rechnet mit ψ nicht unter -3, wie `k₁`.


## DER KASTEN

Fuer Kastentraeger sei die Naeherung ρ = 0.9/λ_p zu ungenau (4.5.3.4); dort
gilt (70). Ein Rechteckrohr ist ein Kasten -- und (70) gilt hier fuer jede
seiner Waende, nicht nur fuer den Druckflansch, den 5.6.4.3 nennt (nach
Vorgabe, nicht nachgeschlagen).

## Inhalt

### epsilon

```python
def epsilon(f_y: float) -> float
```

`ε = √(235/f_y)`, `f_y` in N/mm² (Tabelle 5b, unten).

### Grenzen

```python
@dataclass(frozen=True)
class Grenzen
```

Die groesste Schlankheit `c/t` (beim Rohr `D/t`) der Klassen 1, 2 und 3.

- `werte: Tuple[float, float, float]`

#### Grenzen.klasse

```python
def klasse(self, schlankheit: float) -> int
```

Die kleinste Klasse, deren Grenze die Schlankheit einhaelt -- sonst 4.

### k_1

```python
def k_1(psi: float) -> float
```

Beulwert, wenn der freie Rand gedrueckt ist (Tabelle 5b) -- siehe Dateikopf fuer ψ \< -3.

### k_2

```python
def k_2(psi: float) -> float
```

Beulwert, wenn der gehaltene Rand gedrueckt ist (Tabelle 5b) -- siehe Dateikopf fuer ψ \< -1.

### grenzen

```python
def grenzen(halterung: Halterung, eps: float, alpha: float, psi: Optional[float], *, frei_pl: bool=False, frei_el: bool=False) -> Grenzen
```

Die Grenzen eines Blechs -- siehe Dateikopf. `alpha` null heisst
plastisch nicht gedrueckt, `psi` `None` elastisch nicht gedrueckt:
dort gilt keine Grenze der Klassen 1 und 2, hier keine der Klasse 3.
`frei_pl` und `frei_el`: ob der freie Rand plastisch und elastisch
der staerker gedrueckte ist.

### beulwert

```python
def beulwert(halterung: Halterung, psi: float, frei_gedrueckt: bool=False) -> float
```

Der kleinste Beulwert `k` fuer die mitwirkende Breite (Tabelle 9):
beidseitig gelenkig gelagert nach der Formel der Tabelle, einseitig nach
`k₁` oder `k₂` -- siehe Dateikopf.

### plattenschlankheit

```python
def plattenschlankheit(b: float, t: float, eps: float, k: float) -> float
```

Die bezogene Plattenschlankheit `λ_p = (b/t) / (28.4 ε √k)` (4.5.3.3).

### abminderung

```python
def abminderung(lambda_p: float) -> float
```

Der Abminderungsfaktor `ρ = 0.9/λ_p` der mitwirkenden Breite (4.5.3.3), hoechstens 1.

### abminderung_kasten

```python
def abminderung_kasten(lambda_p: float, psi: float) -> float
```

Der Abminderungsfaktor einer beidseitig gestuetzten Wand im Kasten, (70),
hoechstens 1 -- siehe Dateikopf.


## Konstanten

- `REFERENZ_KLASSE = 'SIA 263:2013, 4.3.1, Tabellen 5a und 5b'` – Wo die Grenzen stehen -- je Halterung ihre Tabelle ([[opencivil.stahlprofile.bleche#Halterung.tabelle|Halterung.tabelle]]).
- `REFERENZ_EPSILON = 'SIA 263:2013, Tabelle 5b'`
- `REFERENZ_BEULWERT = 'SIA 263:2013, 4.5.3.7, Tabelle 9'`
- `REFERENZ_BREITE = 'SIA 263:2013, 4.5.3.2, (11); 4.5.3.3'`
- `REFERENZ_KASTEN = 'SIA 263:2013, 4.5.3.4; 5.6.4.3, (70)'`
- `OHNE = math.inf` – Ohne Grenze -- ein Blech, das nicht gedrueckt ist.

## Braucht

- [[opencivil.stahlprofile.bleche]]

## Gebraucht von

- [[opencivil.nachweis.qa_stahl_kennzahlen]]
- [[opencivil.nachweis.qa_stahl_werte]]
- [[opencivil.stahlbau.querschnitt]]
