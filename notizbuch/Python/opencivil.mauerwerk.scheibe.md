---
erzeugt: bf7c5dfdae5f
art: modul
tags: [modul]
---
> [!abstract] opencivil/mauerwerk/scheibe.py
> wie die waagrechten Lasten einer Wand zu ihren Pfeilern kommen.
> Paket [[opencivil.mauerwerk]] · [Quelltext](../../opencivil/mauerwerk/scheibe.py)

## VERANTWORTUNG

Die Wand als Scheibe unter Lasten in ihrer Ebene ([[opencivil.mauerwerk.scheibe#abtragen|abtragen]]): je
Pfeiler die Querkraft, die Normalkraft, die das Kippen der Wand in ihm
weckt, und das Moment in der Wandebene an seinem Fuss – in den Abtrag der
lotrechten Lasten ([[opencivil.mauerwerk.lasten#Abtrag|Abtrag]]), dazu das
Moment, mit dem diese neben den Mitten der Pfeiler stehen. Die Norm regelt
das nicht; so rechnet das Werkzeug (nach Vorgabe, nicht nachgeschlagen):

- Über den Öffnungen ist die Wand starr: Stürze, Mauerwerk und Decke halten
  dort zusammen. Die waagrechten Lasten greifen an diesem starren Teil an,
  mit ihrem Hebel; tiefer lässt sie
  [[opencivil.mauerwerk.pruefen#lasten_pruefen|lasten_pruefen]] nicht zu
  ([[opencivil.mauerwerk.scheibe#starr_ab|starr_ab]]).
- Jeder Pfeiler ist am Fuss der Wand eingespannt und oben an den starren
  Teil angeschlossen ([[opencivil.mauerwerk.scheibe#koepfe|koepfe]]): am oberen Rand der höchsten Öffnung
  neben ihm, ohne Öffnung an der Krone. Eine Brüstung zählt nicht.
- Ein Pfeiler wirkt ungerissen mit seiner Steifigkeit auf Biegung,
  E_xd · I, auf Schub, G_d · A / 1.2, und längs, E_xd · A, mit A = b · t_w
  ([[opencivil.mauerwerk.scheibe#steifigkeit|steifigkeit]]).
- Das Moment M_v der lotrechten Lasten neben den Mitten der Pfeiler gleicht
  der starre Teil aus: er gibt es den Pfeilern nach ihrer Biegesteifigkeit,
  je b³, an den Fuss ([[opencivil.mauerwerk.scheibe#anteile|anteile]]). Die Normalkräfte des Lastabtrags
  bleiben, und das Gleichgewicht stimmt: ein Weg, den das Mauerwerk gehen
  kann, nicht der einzige.

Steht nur ein Pfeiler da, ist er ein Kragarm: oben dreht er sich frei. Mit
mehreren hält der starre Teil ihre Köpfe gegen das Drehen, soweit sie längs
steif sind: die Wand kippt, und ein Pfeiler wird gedrückt, ein anderer
entlastet. Gerechnet wird das Gleichgewicht des starren Teils mit seinen
drei Bewegungen – waagrecht, lotrecht, Drehung –, je Pfeiler mit der
Steifigkeit eines Balkens mit Schubverformung, unten eingespannt.


## VORZEICHEN

Kräfte nach rechts und oben positiv, Drehungen im Gegenuhrzeigersinn; die
Normalkraft eines Pfeilers Druck positiv, das Moment an seinem Fuss
positiv, wenn es die Resultierende nach rechts schiebt.


## EINHEITEN

SI: N, m und N·m.

## Inhalt

### starr_ab

```python
def starr_ab(flaeche: Rechteck, oeffnungen: Sequence[Oeffnung]) -> float
```

Ab welcher Höhe die Wand starr ist, in m: über der höchsten Öffnung – ohne eine ganz.

### koepfe

```python
def koepfe(flaeche: Rechteck, oeffnungen: Sequence[Oeffnung], pfeiler: Sequence[Pfeiler]) -> Dict[str, float]
```

Je Pfeiler die Höhe seines Kopfs, in m: der obere Rand der höchsten
Öffnung neben ihm – ohne eine die Krone der Wand.

### Steifigkeit

```python
@dataclass(frozen=True)
class Steifigkeit
```

Ein Pfeiler, unten eingespannt, an seinem Kopf: waagrecht `uu`,
waagrecht und gedreht gekoppelt `up`, gedreht `pp`, längs `a`.

- `uu: float`
- `up: float`
- `pp: float`
- `a: float`

### steifigkeit

```python
def steifigkeit(b: float, h: float, t: float, E: float, G: float) -> Steifigkeit
```

Ein Pfeiler `b` breit, `h` hoch und `t` dick – ein Balken mit Schubverformung.

### antworten

```python
def antworten(pfeiler: Sequence[Pfeiler], koepfe_: Dict[str, float], y0: float, lasten: Sequence[Wandlast], E: float, G: float, t: float) -> Dict[str, Tuple[float, float, float]]
```

Je Pfeiler `(V, N, M_z)` unter den waagrechten Lasten `lasten` –
`koepfe_` nach [[opencivil.mauerwerk.scheibe#koepfe|koepfe]], `y0` der Fuss der Wand. Siehe Dateikopf.

### anteile

```python
def anteile(pfeiler: Sequence[Pfeiler]) -> Dict[str, float]
```

Je Pfeiler sein Anteil am Moment M_v: b³ durch die Summe – siehe Dateikopf.

### abtragen

```python
def abtragen(abtrag: Abtrag, flaeche: Rechteck, oeffnungen: Sequence[Oeffnung], pfeiler: Sequence[Pfeiler], lasten: Sequence[Wandlast], E: float, G: float, t: float) -> None
```

In `abtrag`, was die Scheibe den Pfeilern gibt: ihren Anteil an M_v
und was die waagrechten unter `lasten` bewirken – deren Normalkraft
zählt am Kopf wie am Fuss. `E` und `G` sind E_xd und G_d der Wand in
N/m², `t` ihre Dicke in m.


## Konstanten

- `SCHUBFLAECHE = 1.2` – Um so viel ist die Fläche, die auf Schub wirkt, kleiner als A: ein Rechteck, A / 1.2.

## Braucht

- [[opencivil.mauerwerk.lasten]]
- [[opencivil.mauerwerk.modell]]
- [[opencivil.stabwerk.matrix]]

## Gebraucht von

- [[opencivil.mauerwerk.herleitung]]
- [[opencivil.mauerwerk.pruefen]]
- [[opencivil.mauerwerk.werk]]
