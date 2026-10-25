---
erzeugt: 683ad3f4134f
art: modul
tags: [modul]
---
> [!abstract] opencivil/querschnitt/lagenaufbau.py
> wo die Bewehrung einer Platte liegt.
> Paket [[opencivil.querschnitt]] · [Quelltext](../../opencivil/querschnitt/lagenaufbau.py)

## VERANTWORTUNG

Der Lagenaufbau ([[opencivil.querschnitt.lagenaufbau#Lagenaufbau|Lagenaufbau]]) rechnet je Bewehrungsposten seine
Tiefe ab Oberkante und seinen Querschnitt, dazu Bewehrungsmass und
Distanzhalter. Die Nachweise fassen die Posten einer Lage mit den Helfern
hier zusammen: Querschnitt, gemeinsamer Schwerpunkt und statische Hoehe
([[opencivil.querschnitt.lagenaufbau#lage_aus_posten|lage_aus_posten]], [[opencivil.querschnitt.lagenaufbau#protokoll_lage|protokoll_lage]]).


## EIN POSTEN, EINE GESTALT

Ein Posten reist als [[opencivil.querschnitt.lagenaufbau#Postenbezug|Postenbezug]] -- Lage, Art, Posten und seine
Werte. Bis 2026-10-25 reiste er als Tupel ``(Lage, Art, Posten, ID von A_s,
ID von z)``, wurde rund zwanzigmal nach Stelle zerlegt, und seine Marke
`1g` entstand an neun Stellen neu. Bis dahin stand all das auch in
[[opencivil.querschnitt.platte]], die damit ueber 1000 Zeilen kam.

## Inhalt

### Postenbezug

```python
@dataclass(frozen=True)
class Postenbezug
```

Ein Bewehrungsposten einer Platte samt den Werten, die ihn beschreiben --
siehe Dateikopf. Angelegt nur von der Platte
([[opencivil.querschnitt.platte#Plattenquerschnitt|Plattenquerschnitt]]), die auch
Marke, Index und Bezeichnung bildet.

Ein Nachweis liest die Werte eines Postens unter Namen mit dessen
[[opencivil.querschnitt.lagenaufbau#Postenbezug|marke]] ([[opencivil.querschnitt.lagenaufbau#Postenbezug.name|name]]): `a_s_1g`, `z_1g`, `phi_1g`. So lesen
sie auch die Helfer hier.

- `lage: Bewehrungslage`
- `art: Postenart`
- `posten: Bewehrungsposten`
- `marke: str` – Kurzform fuer die Namen der Werte, z.B. `1g`.
- `index: str` – Der Symbolindex, z.B. `1,x,g`: Lage, Richtung, Art -- in dieser Reihenfolge, und immer alle drei. Damit ist jedes Symbol eindeutig, auch wenn zwei Lagen dieselbe Richtung tragen. Die Handrechnung braucht denselben Index fuer ihre zusammengefassten Lagen.
- `bezeichnung: str` – `1. Lage Grundbewehrung`.
- `phi_def: WertDef` – Der Stabdurchmesser.
- `as_def: WertDef` – Der Bewehrungsquerschnitt, aus dem Lagenaufbau.
- `z_def: WertDef` – Die Tiefe ab Oberkante, aus dem Lagenaufbau -- nicht die statische Hoehe.

#### Postenbezug.name

```python
def name(self, groesse: str) -> str
```

Der Name, unter dem ein Nachweis eine Groesse des Postens liest: `a_s_1g`.

#### Postenbezug.bezuege

```python
def bezuege(self, *groessen: str) -> List[Eingabebezug]
```

Diese Groessen des Postens -- `a_s`, `z`, `phi` -- als Eingaben, je unter [[opencivil.querschnitt.lagenaufbau#Postenbezug.name|name]].

### lagenindex

```python
def lagenindex(posten: Sequence[Postenbezug]) -> str
```

Der Symbolindex einer Lage aus ihren Posten -- `1,x` statt `1,x,g`.

Gerechnet wird mit der ganzen Lage, nicht mit einem Posten; ein
Postenindex am Symbol behauptete etwas anderes. Hat die Lage nur einen
Posten, ist dessen Index auch ihrer -- dann heisst `A_s` so wie in der
Tabelle der Platte.

### statische_hoehe

```python
def statische_hoehe(z: float, h: float, seite: Zugseite) -> float
```

Die statische Hoehe einer Lage in der Tiefe `z` unter der Oberkante,
gemessen ab dem gedrueckten Rand: unten `d = z`, oben `d = h - z` --
die Zahl zur Zeile von [[opencivil.querschnitt.lagenaufbau#protokoll_statische_hoehe|protokoll_statische_hoehe]]. Wer `z`
stehen liesse, bekaeme bei den oberen Lagen eine Zahl, die keine
statische Hoehe ist.

### lage_aus_posten

```python
def lage_aus_posten(e: Eingaben, posten: Sequence[Postenbezug]) -> Tuple[float, Optional[float], Optional[float]]
```

Querschnitt, gemeinsamer Schwerpunkt und statische Hoehe einer Lage aus
ihren Posten -- die Zahlen, die [[opencivil.querschnitt.lagenaufbau#protokoll_lage|protokoll_lage]] herleitet. Der
Nachweis liest dafuer je Posten `a_s` und `z`
([[opencivil.querschnitt.lagenaufbau#Postenbezug.bezuege|Postenbezug.bezuege]]), dazu die Dicke `h`.

Grundbewehrung und Zulage liegen auf leicht verschiedenen Hoehen, gehoeren
aber zur selben Lage: es zaehlt ihr gemeinsamer Schwerpunkt. Ohne Stahl
gibt es weder Schwerpunkt noch Hoehe, beide `None`. Bis 2026-10-18
rechneten drei Nachweise das je fuer sich.

### protokoll_lage

```python
def protokoll_lage(p: Protokoll, e: Eingaben, werte: Zwischenwerte, posten: Sequence[Postenbezug], *, a_s: float, z: Optional[float]=None, d: float=0.0) -> Tuple[Wert, Optional[Wert]]
```

Querschnitt und statische Hoehe einer Lage, aus ihren Posten hergeleitet
-- gelesen wie bei [[opencivil.querschnitt.lagenaufbau#lage_aus_posten|lage_aus_posten]].

Liegen Grundbewehrung und Zulage in der Lage, stehen Summe und gemeinsamer
Schwerpunkt da -- sonst fiele der Schwerpunkt vom Himmel. Ohne `z` nur
der Querschnitt. Zurueck kommen `A_s` und `d` fuer die Formeln danach.

### protokoll_statische_hoehe

```python
def protokoll_statische_hoehe(p: Protokoll, d: Wert, *, h: Wert, z: Wert, seite: Zugseite) -> None
```

Die statische Hoehe einer gezogenen Lage, gemessen ab dem gedrueckten Rand.

Eine untere Lage misst ab der Oberkante, `d = z`; eine obere ab der
Unterkante, `d = h - z`. Mehrere Nachweise brauchen diese Zeile -- steht
sie an einer Stelle, sagt «unten» in allen dasselbe.

### Lagenaufbau

```python
class Lagenaufbau(Prozedur)
```

Bestimmt statische Hoehe und Bewehrungsquerschnitt aller Posten.

Beides in einem Zug und in einer Tabelle. Frueher stand fuer jeden Posten
eine eigene Flaechenformel in der Herleitung -- fuenf Lagen ergaben fuenf
gleich aussehende Bloecke, in denen sich nur die Zahlen unterschieden. Die
Formel steht jetzt einmal da, die Ergebnisse stehen in der Tabelle.

**STAPELUNG**

Die Lagen werden je Seite von aussen nach innen gestapelt. Die Huelle einer
Lage beginnt bei der Ueberdeckung und waechst um den groessten Durchmesser
der davorliegenden Lage. `d` wird von der gezogenen Randfaser aus
gemessen -- bei den unteren Lagen von der Unterkante, bei den oberen von
der Oberkante.

Wie Grundbewehrung und Zulage innerhalb einer Lage zueinander liegen, sagt
[[opencivil.querschnitt.platte#Bewehrungslage|unguenstig]].

#### Lagenaufbau.rechne

```python
def rechne(self, e: Eingaben, p: Protokoll) -> Mapping[str, Groesse]
```

#### Lagenaufbau._kennzahlen

```python
def _kennzahlen(self, p: Protokoll, e: Eingaben, h: Groesse, b: Groesse, flaechen: Mapping[str, Groesse], kanten: Mapping[int, Tuple[float, float]], breiten: Mapping[str, Groesse]) -> Dict[str, Groesse]
```

Bewehrungsmass und Hoehe der Distanzhalter.

Beides sind Angaben fuer die Ausfuehrung, keine Nachweisgroessen -- sie
gehoeren aber in den Kern und nicht in die Oberflaeche, damit sie in der
Herleitung stehen und sich zurueckverfolgen lassen.


## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.material.betonstahl]]
- [[opencivil.querschnitt.platte]]
- [[opencivil.querschnitt.zugseite]]

## Gebraucht von

- [[opencivil.nachweis.duktilitaet]]
- [[opencivil.nachweis.handrechnung]]
- [[opencivil.nachweis.mindestbewehrung]]
- [[opencivil.nachweis.querkraft]]
- [[opencivil.nachweis.rechenwahl]]
- [[opencivil.nachweis.verformung]]
- [[opencivil.querschnitt.platte]]

## Formeln aus diesem Modul

- [[Bewehrung der Lage]] · `protokoll_lage`
- [[Bewehrungsmass je Kubikmeter Beton]] · `Lagenaufbau._kennzahlen`
- [[Bewehrungsquerschnitt über die Breite b]] · `Lagenaufbau.rechne`
- [[Höhe der Distanzhalter]] · `Lagenaufbau._kennzahlen`
- [[Schwerpunkt der zusammengefassten Lage]] · `protokoll_lage`
- [[Statische Höhe]] · `protokoll_statische_hoehe`
