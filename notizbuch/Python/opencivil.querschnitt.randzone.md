---
erzeugt: bc6118ede0c9
art: modul
tags: [modul]
---
> [!abstract] opencivil/querschnitt/randzone.py
> der Beton nahe am Rand eines gezeichneten Querschnitts.
> Paket [[opencivil.querschnitt]] · [Quelltext](../../opencivil/querschnitt/randzone.py)

## VERANTWORTUNG

Je Polygon die Flaeche, die hoechstens `abstand` vom Rand des Bauteils
liegt ([[opencivil.querschnitt.randzone#flaechen_am_rand|flaechen_am_rand]]). Gebraucht von der Zwaengung auf
Normalkraft: bei massigen Bauteilen darf die mitwirkende Zugzone auf 250 mm
entlang der gezogenen Raender beschraenkt werden (SIA 262:2025, 4.4.2.3.7),
und unter zentrischem Zug sind alle Raender gezogen.


## DER RAND DES BAUTEILS

Jede Kante zwischen Material und Leere: die Umrisse aussen und die Raender
der Aussparungen. Nicht dazu gehoert, wo zwei Materialien aneinander
grenzen -- ein Polygon in einem anderen, oder zwei, die sich entlang einer
Kante beruehren.


## WIE GERECHNET WIRD

Auf waagrechten Linien. Je Linie die Strecken, die einem Polygon gehoeren
(in ihm, in keinem seiner Kinder), geschnitten mit denen, die naeher als
`abstand` an einer Randkante liegen: um jede Kante liegt ein Streifen mit
runden Enden, und jede Linie schneidet ihn in einer Strecke. Die Linien
liegen in Baendern zwischen den Hoehen, an denen die Strecken springen oder
knicken -- an den Ecken, den Ecken ± `abstand` und den Ecken der
Streifen --, in jedem Band mindestens eine, sonst nach seiner Hoehe
verteilt. Bei Rechtecken ist das genau; eine einspringende Ecke zieht einen
Kreisbogen, dort liegt der Fehler unter einem Promille.


## EINHEITEN

Keine -- die der Punkte, wie in [[opencivil.querschnitt.geometrie]].

## Inhalt

### flaechen_am_rand

```python
def flaechen_am_rand(polygone: Sequence[Sequence[Punkt]], eltern: Sequence[Optional[int]], traegt: Sequence[bool], abstand: float) -> List[float]
```

Je Polygon die Flaeche, die ihm gehoert und hoechstens `abstand` vom
Rand des Bauteils liegt. `eltern` sagt, worin jedes liegt
([[opencivil.querschnitt.geometrie#verschachteln|verschachteln]]), `traegt`, ob
es Material hat; eine Aussparung besitzt nichts, ihre Flaeche ist null.

### _randkanten

```python
def _randkanten(polygone: Sequence[Sequence[Punkt]], eltern: Sequence[Optional[int]], traegt: Sequence[bool]) -> List[Kante]
```

Die Kanten zwischen Material und Leere. Ein Polygon traegt sie bei, wenn
innen anderes liegt als aussen; wo zwei solche Kanten aufeinander liegen,
grenzt auf beiden Seiten dasselbe -- Material an Material oder Leere an
Leere --, und das Stueck faellt weg.

### _deckung

```python
def _deckung(a: Punkt, b: Punkt, c: Punkt, d: Punkt) -> Optional[Strecke]
```

Welches Stueck der Kante a–b die Kante c–d deckt, als Parameter in [0, 1] -- oder nichts.

### _reste

```python
def _reste(a: Punkt, b: Punkt, decken: Sequence[Strecke]) -> List[Kante]
```

Die Stuecke der Kante a–b, die keine andere deckt.

### _bandgrenzen

```python
def _bandgrenzen(polygone: Sequence[Sequence[Punkt]], kanten: Sequence[Kante], abstand: float) -> List[float]
```

Die Hoehen, an denen die Strecken einer Linie springen oder knicken -- aufsteigend.

### _innen

```python
def _innen(punkte: Sequence[Punkt], z: float) -> List[Strecke]
```

Wo die Linie auf der Hoehe `z` im Polygon liegt -- keine Ecke liegt auf ihr.

### _streifen

```python
def _streifen(a: Punkt, b: Punkt, abstand: float, z: float) -> Optional[Strecke]
```

Wo die Linie auf der Hoehe `z` naeher als `abstand` an der Kante a–b
liegt: im Kreis um eine der Ecken oder im Rechteck daneben. Der Streifen
ist konvex, die Linie schneidet ihn in einer Strecke.

### _zwischen

```python
def _zwischen(faktor: float, rest: float, unten: float, oben: float, y0: float) -> Optional[Strecke]
```

Die `y` mit `unten <= (y - y0)·faktor + rest <= oben` -- alle, wenn `faktor` null ist.

### _vereinigen

```python
def _vereinigen(strecken: Sequence[Strecke]) -> List[Strecke]
```

Die Strecken, sortiert und ohne Ueberlappung.

### _schneiden

```python
def _schneiden(a: Sequence[Strecke], b: Sequence[Strecke]) -> List[Strecke]
```

Was in beiden liegt -- beide sortiert und ohne Ueberlappung.

### _abziehen

```python
def _abziehen(a: Sequence[Strecke], b: Sequence[Strecke]) -> List[Strecke]
```

Was in `a` liegt und nicht in `b` -- beide sortiert und ohne Ueberlappung.


## Konstanten

- `LINIEN = 400` – Wie viele Linien ueber die Hoehe des Querschnitts verteilt werden -- dazu wenigstens eine je Band.

## Braucht

- [[opencivil.querschnitt.geometrie]]

## Gebraucht von

- [[opencivil.nachweis.qa_gebrauch]]
