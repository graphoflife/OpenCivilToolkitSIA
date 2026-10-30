---
erzeugt: 44ebc6c65d8c
art: modul
tags: [modul]
---
> [!abstract] opencivil/durchstanzen/mit_bewehrung.py
> der Nachweis mit Durchstanzbewehrung und Stahlpilz.
> Paket [[opencivil.durchstanzen]] · [Quelltext](../../opencivil/durchstanzen/mit_bewehrung.py)

## VERANTWORTUNG

Was der Durchstanznachweis rechnet, wenn der Beton allein nicht reicht:
welches ancoPLUS es braucht ([[opencivil.durchstanzen.bewehrung#bemessen|.bewehrung.bemessen]]), und die vier
Nachweise mit ihm, je mit Herleitung und Urteil (SIA 262:2025, 4.3.6.5.1):

```
Bewehrung        V_d − V_Rd,c ≤ V_Rd,s = ΣA_sw · k_e · σ_sd        (66), (68), (69)
Verformung       V_d / 2 ≤ ΣA_sw · k_e · f_yd                       (67)
Druckdiagonale   V_d ≤ min[k_sys · k_r; 3.5] · τ_cd · d_v · u        (70), 4.3.6.5.9
ausserhalb       V_d,out ≤ k_r · τ_cd · d_v,out · u_out             4.3.6.5.10, Figur 26
```

Die Anker stehen senkrecht (β = 90°, sin β = 1). Der Stahl der Anker ist
der der Biegebewehrung -- ancoPLUS ist aus B500B. k_sys ist der Faktor aus
dem Gutachten des Produkts anstelle der 2 in (70), wie 4.3.6.5.9 es zulässt
([[opencivil.durchstanzen.produkte#k_sys|.produkte.k_sys]]).


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
ohne Leisten, sonst mit Leisten um ihn -- dieselben vier Nachweise, mit dem
Pilz als gestützter Fläche (4.3.6.6.2). Seine Fläche reicht bis an die Enden
der Stege; die wirksame Höhe reicht von der Zugbewehrung bis zur Unterkante
des Pilzes, d_v = d − 20 mm (gelesen, nicht nachgeschlagen). Den Widerstand
des Pilzes selbst (4.3.6.6.1) bestätigt der Hersteller.


## EINHEITEN

SI-Basis; Kräfte in N.

## Inhalt

### Grundlage

```python
@dataclass(frozen=True)
class Grundlage
```

Was der Nachweis ohne Bewehrung schon gerechnet hat -- der mit Bewehrung baut darauf.

- `d: Wert`
- `d_v: Wert`
- `k_e: Wert`
- `k_r: Wert`
- `tau_cd: Wert`
- `u: Wert`
- `psi: Wert`
- `V_d: Wert` – Die Querkraft im inneren Schnitt, die Flächenlast darin abgezogen.
- `V_Rd_c: Wert`
- `masse: Dict[str, float]`
- `umriss: Tuple[Punkt, ...]`

### Ort

```python
@dataclass(frozen=True)
class Ort
```

Wo die Leisten ansetzen: an der Stütze, oder um den Stahlpilz (4.3.6.6.2).

- `zusatz: str` – Was hinter dem Namen eines Urteils steht: leer, oder «um den Stahlpilz».
- `kurz: str` – Die Vorsilbe der Zwischenwerte, damit Stütze und Pilz nebeneinander stehen können.
- `umriss: Tuple[Punkt, ...]`
- `r_zu: Callable[[float], Sequence[Stueck]]` – Der geschlossene Schnitt im Abstand r um die gestützte Fläche.
- `d_v: Wert`
- `u: Wert`
- `V_d: Wert`
- `V_Rd_c: Wert`
- `ausnahme: bool` – Ob der Faktor des Gutachtens erhöht ist -- Innenstütze und Wandende.

### Pilzbefund

```python
@dataclass(frozen=True)
class Pilzbefund
```

Der gewählte Stahlpilz: welcher, seine gestützte Fläche und der Schnitt um sie. m.

- `pilz: Stahlpilz`
- `umriss: Tuple[Punkt, ...]`
- `schnitt: Nachweisschnitt`
- `d_v: float`

### Bewehrungsbefund

```python
@dataclass(frozen=True)
class Bewehrungsbefund
```

Was die Bemessung vorschlägt und was es trägt -- fürs Bild und die
Zusammenfassung. Leisten an der Stütze, ein Pilz ohne Leisten, oder ein
Pilz mit Leisten um ihn. Der äussere Nachweis ist der um die Leisten,
ohne Leisten der um den Pilz. N, m.

- `vorschlag: Optional[Vorschlag]`
- `pilz: Optional[Pilzbefund]`
- `sigma_sd: float`
- `V_Rd_s: float`
- `V_Rd_max: float`
- `k_sys: float`
- `d_v_out: float`
- `u_out: float`
- `V_d_out: float`
- `V_Rd_c_out: float`

### spannung

```python
def spannung(E_s: float, psi: float, f_ctm: float, f_yd: float, d: float, phi: float) -> float
```

σ_sd nach Gleichung (69).

### widerstand

```python
def widerstand(k_r: float, tau_cd: float, d_v: float, u: float) -> float
```

V_Rd,c nach (58) -- im äusseren Schnitt mit d_v,out (4.3.6.5.10), am Pilz mit seinem d_v.

### druckdiagonale

```python
def druckdiagonale(k_sys: float, k_r: float, tau_cd: float, d_v: float, u: float) -> float
```

V_Rd,max nach (70), mit dem Faktor des Gutachtens (4.3.6.5.9).

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

#### _Werte.sigma

```python
def sigma(self, phi: float) -> float
```

#### _Werte.flaechenlast

```python
def flaechenlast(self, flaeche: float) -> float
```

### nachweisen

```python
def nachweisen(n: 'Durchstanzen', e: Eingaben, p: Protokoll, w: Zwischenwerte, g: Grundlage) -> Tuple[List[NachweisUrteil], Optional[Bewehrungsbefund], Dict[str, Groesse]]
```

Die Durchstanzbewehrung suchen und mit ihr nachweisen -- und wo die erste
Druckdiagonale an einer Innenstütze bricht, einen Stahlpilz. Zurück kommen
die Urteile, der Befund und die Grade, die ohne Urteil bleiben (ein Pilz,
der ohne Leisten auskommt, braucht keine Bewehrung).

### _suchen

```python
def _suchen(n: 'Durchstanzen', werte: _Werte, ort: Ort) -> Optional[Vorschlag]
```

Das kleinste ancoPLUS für diesen Ort -- siehe [[opencivil.durchstanzen.bewehrung#bemessen|.bewehrung.bemessen]].

### _mit_leisten

```python
def _mit_leisten(n: 'Durchstanzen', p: Protokoll, w: Zwischenwerte, werte: _Werte, ort: Ort, vorschlag: Vorschlag, pilz: Optional[Pilzbefund]=None) -> Tuple[List[NachweisUrteil], Bewehrungsbefund, bool]
```

Die vier Nachweise mit diesen Leisten, mit Herleitung. Zurück: die Urteile,
der Befund und ob die erste Druckdiagonale bricht.

### _umfang

```python
def _umfang(p: Protokoll, w: Zwischenwerte, g: Grundlage, a: Auswertung, name: str, index: str, genitiv: str, nominativ: str, referenz: str) -> Wert
```

Ein Schnitt, wie er zählt: in der Platte, ohne was nicht zählt, mit k_e --
für den äusseren Schnitt (`index` «out») und den um den Pilz («P»).

### _querkraft

```python
def _querkraft(e: Eingaben, p: Protokoll, w: Zwischenwerte, flaeche: float, name: str, symbol: str, name_A: str, symbol_A: str, wo: str, index: str) -> Wert
```

V_d in einem Schnitt ausserhalb: die Flächenlast darin abgezogen
(4.3.6.2.6). Die Platzhalter tragen den Index, wie in [[opencivil.durchstanzen.mit_bewehrung#_umfang|_umfang]].

### _pilzflaeche

```python
def _pilzflaeche(werte: _Werte, n: 'Durchstanzen', pilz: Stahlpilz) -> Tuple[Tuple[Punkt, ...], Nachweisschnitt, float]
```

Die gestützte Fläche des Pilzes, der Schnitt im Abstand d_v/2 um sie und sein d_v.

### _pilz_suchen

```python
def _pilz_suchen(n: 'Durchstanzen', werte: _Werte) -> Optional[Tuple[Pilzbefund, Optional[Vorschlag]]]
```

Der kleinste ZEUS, der zwischen die Überdeckungen passt, über die Stütze
hinausreicht und mit dem die Platte ausserhalb hält -- ohne Leisten oder
mit Leisten um ihn, die alle vier Nachweise erfüllen.

Ein Pilz, dessen Druckdiagonale nicht einmal mit dem ganzen Umfang um ihn
hielte -- der Hülle samt dem Bogen d_v/2 rundum, ohne Abzüge --, fällt
weg, bevor sein Schnitt gerechnet wird: so bleibt die Suche schnell.

### _pilzort

```python
def _pilzort(befund: Pilzbefund, d_v: Wert, u: Wert, V_d: Wert, V_Rd_c: Wert) -> Ort
```

Der Pilz als Ort der Leisten: seine Fläche, sein d_v, der Schnitt um ihn.

### _mit_pilz

```python
def _mit_pilz(n: 'Durchstanzen', p: Protokoll, w: Zwischenwerte, werte: _Werte, befund: Pilzbefund, vorschlag: Optional[Vorschlag]) -> Tuple[List[NachweisUrteil], Bewehrungsbefund, Dict[str, Groesse]]
```

Die Herleitung mit dem gewählten Pilz: die Platte ausserhalb, ohne oder mit Leisten.


## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.durchstanzen.bewehrung]]
- [[opencivil.durchstanzen.nachweis]]
- [[opencivil.durchstanzen.produkte]]
- [[opencivil.durchstanzen.schnitt]]
- [[opencivil.durchstanzen.stelle]]

## Gebraucht von

- [[opencivil.durchstanzen.nachweis]]
- [[opencivil.web.durchstanzdaten]]

## Formeln aus diesem Modul

- [[Anrechenbare Durchstanzbewehrung]] · `_mit_leisten`
- [[Äusserer Nachweisschnitt ohne das, was nicht zählt]] · `_umfang`
- [[Beitrag der Durchstanzbewehrung]] · `_mit_leisten`
- [[Durchstanzbewehrung an der Fliessgrenze]] · `_mit_leisten`
- [[Durchstanzwiderstand im äusseren Nachweisschnitt]] · `_mit_leisten`
- [[Durchstanzwiderstand ohne Durchstanzbewehrung]] · `_mit_pilz`
- [[Halbe Querkraft für das Verformungsvermögen]] · `_mit_leisten`
- [[Platz für die Durchstanzbewehrung]] · `nachweisen`
- [[Querkraft für die Durchstanzbewehrung]] · `_mit_leisten`
- [[Querkraft im äusseren Nachweisschnitt]] · `_querkraft`
- [[Querkraft im Schnitt um den Stahlpilz]] · `_querkraft`
- [[Schnitt um den Stahlpilz ohne das, was nicht zählt]] · `_umfang`
- [[Spannung in der Durchstanzbewehrung]] · `_mit_leisten`
- [[Widerstand der ersten Betondruckdiagonale]] · `_mit_leisten`
- [[Wirksame statische Höhe im äusseren Nachweisschnitt]] · `_mit_leisten`
- [[Wirksame statische Höhe um den Stahlpilz]] · `_mit_pilz`
- [[Wirksamer Umfang des äusseren Nachweisschnitts]] · `_umfang`
- [[Wirksamer Umfang des Schnitts um den Stahlpilz]] · `_umfang`
