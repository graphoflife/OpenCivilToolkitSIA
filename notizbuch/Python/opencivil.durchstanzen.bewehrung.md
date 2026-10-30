---
erzeugt: d7f46923ce9b
art: modul
tags: [modul]
---
> [!abstract] opencivil/durchstanzen/bewehrung.py
> wo die Durchstanzbewehrung liegt, und welche reicht.
> Paket [[opencivil.durchstanzen]] · [Quelltext](../../opencivil/durchstanzen/bewehrung.py)

## VERANTWORTUNG

Die Leisten um die gestützte Fläche und ihre Anker ([[opencivil.durchstanzen.bewehrung#leisten_anordnen|leisten_anordnen]]),
der äussere Nachweisschnitt um die äussersten Anker ([[opencivil.durchstanzen.bewehrung#aeussere_kandidaten|aeussere_kandidaten]],
Figur 26) und die Suche nach dem kleinsten ancoPLUS, das alle Bedingungen
erfüllt ([[opencivil.durchstanzen.bewehrung#bemessen|bemessen]]). Hier steht keine Herleitung: der Nachweis
([[opencivil.durchstanzen.nachweis|.nachweis]]) schreibt sie für die Bewehrung, die hier gefunden wird.


## DIE ANORDNUNG

Die Leisten stehen senkrecht auf dem Rand der gestützten Fläche, an Ecken und
Rundungen radial. Ihre zweiten Anker liegen auf der Linie im Abstand r_2 um
die gestützte Fläche; entlang dieser Linie stehen zwei Leisten höchstens
e_max auseinander, als Sehne gemessen. Auf jeder geraden Seite steht an
beiden Enden eine Leiste und dazwischen gleichmässig so viele wie nötig, auf
den Rundungen ebenso. Das ist der Grundriss der Herstellerunterlagen, die
Regeln dazu sind die des Produkts ([[opencivil.durchstanzen.produkte|.produkte]]) -- nach Vorgabe, nicht
nachgeschlagen. Eine Leiste, deren Anker nicht mindestens die Überdeckung
tief in der Platte liegen, fällt weg; ebenso eine, deren Anker in eine
Aussparung fallen.


## DER ÄUSSERE SCHNITT (Figur 26)

Er läuft im Abstand 0.5·d_v,out um die äussersten Anker; von einer geraden
Strecke zwischen zwei äussersten Ankern zählen höchstens 1.5·d_v,out von
jedem Ende her. Das ist die Regel der Ecken grosser Stützen (Figur 23a), mit
den äussersten Ankern als Ecken -- gebaut wird er darum wie der Schnitt um
eine Stütze, deren Kern die konvexe Hülle der äussersten Anker und der
Stütze ist ([[opencivil.durchstanzen.schnitt#kandidaten_stuetze|kandidaten_stuetze]]). Am Plattenrand endet er
wie der innere, wenn er so kürzer wird.


## EINHEITEN

SI-Basis, Längen in m, Kräfte in N.

## Inhalt

### Leiste

```python
@dataclass(frozen=True)
class Leiste
```

Eine Leiste: wo sie am Rand der gestützten Fläche ansetzt und wohin sie läuft.

- `wurzel: Punkt`
- `richtung: Punkt`

#### Leiste.anker

```python
def anker(self, radien: Sequence[float]) -> List[Punkt]
```

Die Anker im Abstand `radien` vom Rand der gestützten Fläche.

### _normale

```python
def _normale(a: Punkt, b: Punkt) -> Punkt
```

Nach aussen, für einen Rand gegen den Uhrzeigersinn.

### leisten_anordnen

```python
def leisten_anordnen(stuecke: Sequence[Stueck], r_2: float, e_max: float) -> List[Leiste]
```

Die Leisten um eine gestützte Fläche -- `stuecke` ist der geschlossene
Schnitt im Abstand `r_2` um sie (siehe Dateikopf).

### in_der_platte

```python
def in_der_platte(leisten: Sequence[Leiste], radien: Sequence[float], raender: Sequence[Halbebene], aussparungen: Sequence[Sequence[Punkt]], ueberdeckung: float) -> List[Leiste]
```

Nur die Leisten, deren Anker alle um die Überdeckung in der Platte liegen und keine Aussparung treffen.

### aeussere_kandidaten

```python
def aeussere_kandidaten(leisten: Sequence[Leiste], radien: Sequence[float], umriss: Sequence[Punkt], raender: Sequence[Halbebene], d_v_out: float) -> List[Kandidat]
```

Die Kandidaten des äusseren Schnitts (Figur 26) -- siehe Dateikopf.

### Vorschlag

```python
@dataclass(frozen=True)
class Vorschlag
```

Eine Durchstanzbewehrung, die alle Bedingungen erfüllt -- oder die stärkste,
die sich finden liess (`reicht` falsch). Kräfte in N.

- `typ: produkte.Ankertyp`
- `h_A: float`
- `abstaende: Tuple[float, ...]`
- `leisten: Tuple[Leiste, ...]`
- `anrechenbar: int` – Wie viele Anker je Leiste zwischen 0.35·d_v und d_v liegen (Gleichung (68)).
- `aussen: Nachweisschnitt`
- `reicht: bool`

#### Vorschlag.radien

```python
@property
def radien(self) -> Tuple[float, ...]
```

Die Abstände der Anker vom Rand der gestützten Fläche.

#### Vorschlag.A_sw

```python
@property
def A_sw(self) -> float
```

Die anrechenbare Durchstanzbewehrung: Leisten mal Anker im Bereich mal Fläche.

#### Vorschlag.name

```python
@property
def name(self) -> str
```

«12 × ancoPLUS DA3-0215».

### anrechenbar

```python
def anrechenbar(radien: Sequence[float], d_v: float) -> int
```

Die Anker zwischen 0.35·d_v und d_v vom Rand der gestützten Fläche (Gleichung (68)).

### bemessen

```python
def bemessen(*, d: float, d_v: float, d_v_out: float, h_A: float, r_2_zu: Callable[[float], Sequence[Stueck]], umriss: Sequence[Punkt], raender: Sequence[Halbebene], aussparungen: Sequence[Sequence[Punkt]], achse: Punkt, ueberdeckung: float, noetig: Callable[[produkte.Ankertyp, float], bool], aussen_reicht: Callable[[Nachweisschnitt], bool]) -> Optional[Vorschlag]
```

Das kleinste ancoPLUS, das reicht: der kleinste Durchmesser, mit dem die
Bewehrung im Bereich `noetig` erfüllt, und dazu die kleinste Zahl Anker
je Leiste, mit der der äussere Schnitt `aussen_reicht`. Erst wenn kein
Durchmesser genügt, stehen die Leisten dichter ([[opencivil.durchstanzen.bewehrung#Konstanten|DICHTEN]]).
`noetig(typ, A_sw)` und `aussen_reicht(schnitt)` rechnet der
Nachweis; `r_2_zu(r)` gibt den geschlossenen Schnitt im Abstand r um die
gestützte Fläche.

Reicht nichts, kommt der stärkste Versuch mit `reicht` falsch zurück --
die dichtesten Leisten mit dem grössten Durchmesser und neun Ankern.
`None` nur, wo es kein ancoPLUS gibt: die Platte ist zu dünn, keine
Höhe ist lieferbar, oder keine Leiste findet Platz.


## Konstanten

- `BEREICH_VON = 0.35` – Angerechnet wird die Durchstanzbewehrung zwischen 0.35·d_v und d_v vom Rand der gestützten Fläche (SIA 262:2025, 4.3.6.5.4, Gleichung (68)).
- `ECKENBEREICH_AUSSEN = 1.5` – Von einer Strecke des äusseren Schnitts zwischen zwei äussersten Ankern zählen höchstens 1.5·d_v,out von jedem Ende (SIA 262:2025, Figur 26).
- `DICHTEN = (1.0, 0.75, 0.5)` – Wie dicht die Suche die Leisten stellt, in Teilen von e_max: erst so weit wie erlaubt, dann enger, wenn kein Durchmesser reicht.

## Braucht

- [[opencivil.durchstanzen.produkte]]
- [[opencivil.durchstanzen.schnitt]]
- [[opencivil.querschnitt.geometrie]]

## Gebraucht von

- [[opencivil.durchstanzen.mit_bewehrung]]
