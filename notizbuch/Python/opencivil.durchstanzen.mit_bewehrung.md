---
erzeugt: 9c212d712118
art: modul
tags: [modul]
---
> [!abstract] opencivil/durchstanzen/mit_bewehrung.py
> der Nachweis mit Durchstanzbewehrung und Stahlpilz.
> Paket [[opencivil.durchstanzen]] · [Quelltext](../../opencivil/durchstanzen/mit_bewehrung.py)

## VERANTWORTUNG

Was der Durchstanznachweis tut, wenn der Beton allein nicht reicht: das
kleinste ancoPLUS suchen ([[opencivil.durchstanzen.bewehrung#bemessen|.bewehrung.bemessen]]) und mit ihm die drei
Nachweise nach SIA 262:2025, 4.3.6.5.1, schreiben -- den ersten geteilt in
den Beitrag der Bewehrung (66), (68), (69) und das Verformungsvermögen (67),
dazu die erste Betondruckdiagonale (70) und ausserhalb der Bewehrung
(4.3.6.5.10, Figur 26). Gerechnet wird jede Bedingung einmal, in
[[opencivil.durchstanzen.pruefung|.pruefung]]; die Suche fragt die Prüfung, die Herleitung schreibt
dieselben Zahlen.

Die Anker haben ihren eigenen Stahl, B500B ([[opencivil.durchstanzen.stelle#Durchstanzstelle|.stelle.Durchstanzstelle.anker]]):
in (67) und (69) gilt seine Fliessgrenze, nicht die der Biegebewehrung
(4.3.6.5.4). Liegen ihre Köpfe auf der Druckseite tiefer als d_v/6, tragen
(68) und (70) 30 % weniger (5.5.3.11). k_sys ist der Faktor aus dem
Gutachten des Produkts anstelle der 2 in (70), wie 4.3.6.5.9 es zulässt
([[opencivil.durchstanzen.produkte#k_sys|.produkte.k_sys]]).


## IM ÄUSSEREN SCHNITT

d_v,out reicht von der Zugbewehrung bis zur Verankerung der Anker auf der
Druckseite: d − c_v (Figur 26). k_e gilt je Schnitt (4.3.6.5.10 verweist
auf 4.3.6.2.3): die Näherung der gestützten Fläche oder (57) mit der Fläche
und dem Schwerpunkt des äusseren Schnitts. Bis 2026-11-14 galt aussen das
k_e von innen -- an Rand- und Eckstützen bis 20 % zu günstig. Abgezogen
wird die Flächenlast innerhalb des äusseren Schnitts (4.3.6.2.6).


## DER STAHLPILZ (4.3.6.6)

Bricht an einer Innenstütze die erste Betondruckdiagonale, hilft mehr
Bewehrung nicht. Dann wird der kleinste ZEUS gewählt, der zwischen die
Überdeckungen passt und mit dem die Platte ausserhalb seiner Stege hält:
ohne Leisten, sonst mit Leisten um ihn -- dieselben Schritte wie an der
Stütze, mit dem Pilz als gestützter Fläche (4.3.6.6.2). Seine Fläche reicht
bis an die Enden der Stege; die wirksame Höhe reicht von der Zugbewehrung bis
zur Unterkante des Pilzes, d_v = d − 20 mm: 4.3.6.6.2 verweist für d_v auf
4.3.6.2, und Figur 21 misst d_v bis zur Höhe der gestützten Fläche; die 20 mm
sind eine Vorgabe des Herstellers. Den Widerstand des Pilzes selbst
(4.3.6.6.1) bestätigt der Hersteller.


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
- `k_e: Optional[Wert] = None`
- `u: Optional[Wert] = None`
- `V_d: Optional[Wert] = None`
- `V_Rd_c: Optional[Wert] = None` – Wie die Herleitung den Schnitt zeigt -- fehlt nur in der stummen Suche nach dem Pilz.

### _Werte

```python
@dataclass(frozen=True)
class _Werte
```

Was jede Rechnung mit Bewehrung braucht, als Zahlen und als Werte der
Herleitung. f_yd und E_s sind die des Stahls der Anker.

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

### _k_e

```python
def _k_e(n: 'Durchstanzen', werte: _Werte, a: Auswertung) -> float
```

k_e an einem Schnitt um die Anker oder den Pilz: die Näherung gilt für die
gestützte Fläche (4.3.6.2.5), (57) rechnet mit der Fläche und dem
Schwerpunkt dieses Schnitts (4.3.6.2.4).

### _k_e_schreiben

```python
def _k_e_schreiben(n: 'Durchstanzen', p: Protokoll, w: Zwischenwerte, werte: _Werte, a: Auswertung, ix: Index) -> Wert
```

k_e an einem Schnitt um die Anker oder den Pilz, wie [[opencivil.durchstanzen.mit_bewehrung#_k_e|_k_e]] es rechnet.

### _verankerung_schreiben

```python
def _verankerung_schreiben(p: Protokoll, c_v: float, d_v: float, eta: float) -> str
```

Ob die Anker auf der Druckseite genügend verankert sind (5.5.3.11) -- und
was dann vor (68) und (70) steht: nichts, oder der Faktor 0.7.

### _tabelle_21_pruefen

```python
def _tabelle_21_pruefen(p: Protokoll, d: float, vorschlag: Vorschlag) -> None
```

Ein Hinweis, wo das Produkt Tabelle 21 überschreitet -- im Durchmesser
oder im Abstand s_1 der Reihen (5.5.3.8, 5.5.3.12). Ob das Gutachten das
nach 4.3.6.5.6 deckt, ist offen; die Prüfung hält es darum nicht fest.

### _suchen

```python
def _suchen(n: 'Durchstanzen', werte: _Werte, ort: Ort) -> Optional[Leistenpruefung]
```

Das kleinste ancoPLUS für diesen Ort, mit seiner Prüfung -- siehe [[opencivil.durchstanzen.bewehrung#bemessen|.bewehrung.bemessen]].

### _leisten_schreiben

```python
def _leisten_schreiben(n: 'Durchstanzen', p: Protokoll, w: Zwischenwerte, werte: _Werte, ort: Ort, pruefung: Leistenpruefung) -> List[NachweisUrteil]
```

Die Nachweise mit diesen Leisten (4.3.6.5.1), wie die Prüfung sie gerechnet hat.

### _pilz_pruefen

```python
def _pilz_pruefen(n: 'Durchstanzen', werte: _Werte, pilz: Stahlpilz) -> Pilzbefund
```

Die gestützte Fläche des Pilzes und der Schnitt im Abstand d_v/2 um sie, geprüft ohne Leisten.

### _pilzort

```python
def _pilzort(n: 'Durchstanzen', werte: _Werte, befund: Pilzbefund, d_v: Optional[Wert]=None, k_e: Optional[Wert]=None, u: Optional[Wert]=None, V_d: Optional[Wert]=None, V_Rd_c: Optional[Wert]=None) -> Ort
```

Der Pilz als Ort der Leisten: seine Fläche, der Schnitt um ihn und dessen Schatten.

### _pilz_suchen

```python
def _pilz_suchen(n: 'Durchstanzen', werte: _Werte) -> Optional[Tuple[Pilzbefund, Optional[Leistenpruefung]]]
```

Der kleinste ZEUS, der zwischen die Überdeckungen passt, über die Stütze
hinausreicht und mit dem die Platte ausserhalb hält -- ohne Leisten oder
mit Leisten um ihn, die alle Nachweise erfüllen.

Ein Pilz, dessen Druckdiagonale nicht einmal mit dem ganzen Umfang um ihn
hielte -- der Hülle samt dem Bogen d_v/2 rundum, ohne Abzüge, und mit
k_e = 1, wo (57) gilt --, fällt weg, bevor sein Schnitt gerechnet wird: so
bleibt die Suche schnell.

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
- [[opencivil.durchstanzen.stelle]]

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
