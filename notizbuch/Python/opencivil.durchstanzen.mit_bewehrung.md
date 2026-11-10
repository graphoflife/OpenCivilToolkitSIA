---
erzeugt: f9b1aea79ba7
art: modul
tags: [modul]
---
> [!abstract] opencivil/durchstanzen/mit_bewehrung.py
> der Nachweis mit Durchstanzbewehrung und Stahlpilz.
> Paket [[opencivil.durchstanzen]] · [Quelltext](../../opencivil/durchstanzen/mit_bewehrung.py)

## VERANTWORTUNG

Was der Durchstanznachweis tut, wenn der Beton allein nicht reicht: das
kleinste ancoPLUS suchen ([[opencivil.durchstanzen.bewehrung#bemessen|.bewehrung.bemessen]]) und die vier Nachweise
mit ihm schreiben (SIA 262:2025, 4.3.6.5.1) -- Bewehrung (66), (68), (69),
Verformungsvermögen (67), erste Betondruckdiagonale (70) und ausserhalb der
Bewehrung (4.3.6.5.10, Figur 26). Gerechnet wird jede Bedingung einmal, in
[[opencivil.durchstanzen.pruefung|.pruefung]]; die Suche fragt die Prüfung, die Herleitung schreibt
dieselben Zahlen.

Der Stahl der Anker ist der der Biegebewehrung -- ancoPLUS ist aus B500B.
k_sys ist der Faktor aus dem Gutachten des Produkts anstelle der 2 in (70),
wie 4.3.6.5.9 es zulässt ([[opencivil.durchstanzen.produkte#k_sys|.produkte.k_sys]]).


## IM ÄUSSEREN SCHNITT

d_v,out reicht von der Zugbewehrung bis zu den Köpfen der Anker auf der
Druckseite: d − c_v (Figur 26). k_e ist das des inneren Schnitts -- aus der
Näherung dasselbe; aus der Exzentrizität wäre es aussen grösser, der Wert
von innen liegt auf der sicheren Seite. Abgezogen wird die Flächenlast
innerhalb des äusseren Schnitts (4.3.6.2.6).


## DER STAHLPILZ (4.3.6.6)

Bricht an einer Innenstütze die erste Betondruckdiagonale, hilft mehr
Bewehrung nicht. Dann wird der kleinste ZEUS gewählt, der zwischen die
Überdeckungen passt und mit dem die Platte ausserhalb seiner Stege hält:
ohne Leisten, sonst mit Leisten um ihn -- dieselben Schritte wie an der
Stütze, mit dem Pilz als gestützter Fläche (4.3.6.6.2). Seine Fläche reicht
bis an die Enden der Stege; die wirksame Höhe reicht von der Zugbewehrung bis
zur Unterkante des Pilzes, d_v = d − 20 mm (gelesen, nicht nachgeschlagen).
Den Widerstand des Pilzes selbst (4.3.6.6.1) bestätigt der Hersteller.


## EINHEITEN

SI-Basis; Kräfte in N.

## Inhalt

### Grundlage

```python
@dataclass(frozen=True)
class Grundlage
```

Was der Nachweis ohne Bewehrung schon gerechnet hat -- als Prüfung des
Schnitts um die Stütze und als die Werte, mit denen seine Herleitung sie
zeigt.

- `innen: Schnittpruefung`
- `d: Wert`
- `d_v: Wert`
- `k_e: Wert`
- `k_r: Wert`
- `tau_cd: Wert`
- `u: Wert`
- `psi: Wert`
- `V_d: Wert` – Die Querkraft im Schnitt um die Stütze, die Flächenlast darin abgezogen.
- `V_Rd_c: Wert`
- `masse: Dict[str, float]`
- `umriss: Tuple[Punkt, ...]`

### Ort

```python
@dataclass(frozen=True)
class Ort
```

Wo die Leisten ansetzen: an der Stütze oder um den Stahlpilz (4.3.6.6.2) --
die gestützte Fläche, der Schnitt um sie und die Werte, mit denen die
Herleitung ihn zeigt.

- `zusatz: str` – Was hinter dem Namen eines Urteils steht: leer, oder «um den Stahlpilz».
- `vorsilbe: str` – Die Vorsilbe der Zwischenwerte, damit Stütze und Pilz nebeneinander stehen können.
- `umriss: Tuple[Punkt, ...]`
- `r_zu: Callable[[float], Sequence[Stueck]]` – Der geschlossene Schnitt im Abstand r um die gestützte Fläche.
- `pruefung: Schnittpruefung`
- `ausnahme: bool` – Ob der Faktor des Gutachtens erhöht ist -- Innenstütze und Wandende.
- `schatten: Tuple[Schatten, ...]` – Die Schatten der Aussparungen am Schnitt um diese Fläche: dort liegt keine Leiste.
- `d_v: Optional[Wert] = None`
- `u: Optional[Wert] = None`
- `V_d: Optional[Wert] = None`
- `V_Rd_c: Optional[Wert] = None` – Wie die Herleitung den Schnitt zeigt -- fehlt nur in der stummen Suche nach dem Pilz.

### _Werte

```python
@dataclass(frozen=True)
class _Werte
```

Was jede Rechnung mit Bewehrung braucht, als Zahlen und als Werte der Herleitung.

- `e: Eingaben`
- `g: Grundlage`
- `f_yd: Wert`
- `E_s: Wert`
- `f_ctm: Wert`
- `c_v: float`
- `h_A: Wert`
- `d_v_out: Wert`

### nachweisen

```python
def nachweisen(n: 'Durchstanzen', e: Eingaben, p: Protokoll, w: Zwischenwerte, g: Grundlage) -> Tuple[List[NachweisUrteil], Optional[Leistenpruefung], Optional[Pilzbefund]]
```

Die Durchstanzbewehrung suchen und mit ihr nachweisen -- und wo die erste
Druckdiagonale an einer Innenstütze bricht, einen Stahlpilz. Zurück kommen
die Urteile, die Leisten und der Pilz, so weit es sie gibt.

### _suchen

```python
def _suchen(n: 'Durchstanzen', werte: _Werte, ort: Ort) -> Optional[Leistenpruefung]
```

Das kleinste ancoPLUS für diesen Ort, mit seiner Prüfung -- siehe [[opencivil.durchstanzen.bewehrung#bemessen|.bewehrung.bemessen]].

### _leisten_schreiben

```python
def _leisten_schreiben(n: 'Durchstanzen', p: Protokoll, w: Zwischenwerte, werte: _Werte, ort: Ort, pruefung: Leistenpruefung) -> List[NachweisUrteil]
```

Die vier Nachweise mit diesen Leisten, wie die Prüfung sie gerechnet hat.

### _pilz_pruefen

```python
def _pilz_pruefen(n: 'Durchstanzen', werte: _Werte, pilz: Stahlpilz) -> Pilzbefund
```

Die gestützte Fläche des Pilzes und der Schnitt im Abstand d_v/2 um sie, geprüft ohne Leisten.

### _pilzort

```python
def _pilzort(n: 'Durchstanzen', werte: _Werte, befund: Pilzbefund, d_v: Optional[Wert]=None, u: Optional[Wert]=None, V_d: Optional[Wert]=None, V_Rd_c: Optional[Wert]=None) -> Ort
```

Der Pilz als Ort der Leisten: seine Fläche, der Schnitt um ihn und dessen Schatten.

### _pilz_suchen

```python
def _pilz_suchen(n: 'Durchstanzen', werte: _Werte) -> Optional[Tuple[Pilzbefund, Optional[Leistenpruefung]]]
```

Der kleinste ZEUS, der zwischen die Überdeckungen passt, über die Stütze
hinausreicht und mit dem die Platte ausserhalb hält -- ohne Leisten oder
mit Leisten um ihn, die alle vier Nachweise erfüllen.

Ein Pilz, dessen Druckdiagonale nicht einmal mit dem ganzen Umfang um ihn
hielte -- der Hülle samt dem Bogen d_v/2 rundum, ohne Abzüge --, fällt
weg, bevor sein Schnitt gerechnet wird: so bleibt die Suche schnell.

### _mit_pilz

```python
def _mit_pilz(n: 'Durchstanzen', p: Protokoll, w: Zwischenwerte, werte: _Werte, befund: Pilzbefund, leisten: Optional[Leistenpruefung]) -> Tuple[List[NachweisUrteil], Optional[Leistenpruefung], Pilzbefund]
```

Die Herleitung mit dem gewählten Pilz: der Schnitt um ihn mit denselben
Schritten wie um die Stütze, ohne Leisten oder mit Leisten um ihn.


## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.nachweis]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.durchstanzen.bewehrung]]
- [[opencivil.durchstanzen.herleitung]]
- [[opencivil.durchstanzen.nachweis]]
- [[opencivil.durchstanzen.produkte]]
- [[opencivil.durchstanzen.pruefung]]
- [[opencivil.durchstanzen.schnitt]]

## Gebraucht von

- [[opencivil.durchstanzen.nachweis]]

## Formeln aus diesem Modul

- [[Anrechenbare Durchstanzbewehrung]] · `_leisten_schreiben`
- [[Beitrag der Durchstanzbewehrung]] · `_leisten_schreiben`
- [[Durchstanzbewehrung an der Fliessgrenze]] · `_leisten_schreiben`
- [[Halbe Querkraft für das Verformungsvermögen]] · `_leisten_schreiben`
- [[Platz für die Durchstanzbewehrung]] · `nachweisen`
- [[Querkraft für die Durchstanzbewehrung]] · `_leisten_schreiben`
- [[Spannung in der Durchstanzbewehrung]] · `_leisten_schreiben`
- [[Widerstand der ersten Betondruckdiagonale]] · `_leisten_schreiben`
- [[Wirksame statische Höhe im äusseren Nachweisschnitt]] · `_leisten_schreiben`
- [[Wirksame statische Höhe um den Stahlpilz]] · `_mit_pilz`
