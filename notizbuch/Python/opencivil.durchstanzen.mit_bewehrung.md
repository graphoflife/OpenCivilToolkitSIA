---
erzeugt: 4b8518a5bd57
art: modul
tags: [modul]
---
> [!abstract] opencivil/durchstanzen/mit_bewehrung.py
> der Nachweis mit Durchstanzbewehrung (SIA 262:2025, 4.3.6.5).
> Paket [[opencivil.durchstanzen]] · [Quelltext](../../opencivil/durchstanzen/mit_bewehrung.py)

## VERANTWORTUNG

Was der Durchstanznachweis rechnet, wenn der Beton allein nicht reicht:
welches ancoPLUS es braucht ([[opencivil.durchstanzen.bewehrung#bemessen|.bewehrung.bemessen]]), und die vier
Nachweise mit ihm, je mit Herleitung und Urteil (4.3.6.5.1):

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

### Bewehrungsbefund

```python
@dataclass(frozen=True)
class Bewehrungsbefund
```

Die vorgeschlagene Durchstanzbewehrung und was sie trägt -- fürs Bild und die Zusammenfassung. N, m.

- `vorschlag: Vorschlag`
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

### widerstand_aussen

```python
def widerstand_aussen(k_r: float, tau_cd: float, d_v_out: float, u_out: float) -> float
```

V_Rd,c im äusseren Schnitt: (58) mit d_v,out (4.3.6.5.10).

### nachweisen

```python
def nachweisen(n: 'Durchstanzen', e: Eingaben, p: Protokoll, w: Zwischenwerte, g: Grundlage) -> Tuple[List[NachweisUrteil], Optional[Bewehrungsbefund]]
```

Die Durchstanzbewehrung suchen und mit ihr nachweisen. Zurück kommen die
vier Urteile und der Befund -- ohne Befund, wo es kein ancoPLUS gibt;
dann bleibt es bei einem Hinweis, und die Urteile sagen «nicht führbar».

### _querkraft_aussen

```python
def _querkraft_aussen(e: Eingaben, p: Protokoll, w: Zwischenwerte, flaeche: float) -> Wert
```

V_d im äusseren Schnitt: die Flächenlast darin abgezogen (4.3.6.2.6).


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

- [[Anrechenbare Durchstanzbewehrung]] · `nachweisen`
- [[Äusserer Nachweisschnitt ohne das, was nicht zählt]] · `nachweisen`
- [[Beitrag der Durchstanzbewehrung]] · `nachweisen`
- [[Durchstanzbewehrung an der Fliessgrenze]] · `nachweisen`
- [[Durchstanzwiderstand im äusseren Nachweisschnitt]] · `nachweisen`
- [[Halbe Querkraft für das Verformungsvermögen]] · `nachweisen`
- [[Platz für die Durchstanzbewehrung]] · `nachweisen`
- [[Querkraft für die Durchstanzbewehrung]] · `nachweisen`
- [[Querkraft im äusseren Nachweisschnitt]] · `_querkraft_aussen`
- [[Spannung in der Durchstanzbewehrung]] · `nachweisen`
- [[Widerstand der ersten Betondruckdiagonale]] · `nachweisen`
- [[Wirksame statische Höhe im äusseren Nachweisschnitt]] · `nachweisen`
- [[Wirksamer Umfang des äusseren Nachweisschnitts]] · `nachweisen`
