---
erzeugt: b51cd78ec94b
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/kennzahlen.py
> was eine Platte aufnimmt, ohne Einwirkung.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/kennzahlen.py)

## VERANTWORTUNG

Die Kennzahlen der Platte in x, gerechnet immer -- ob es Lastfaelle gibt oder
nicht (Benutzer, 2026-10-16). Die Zusammenfassung zeigt sie unter jeder
Platte:

* aus der Handrechnung mit Bemessungswerten: `M_Rd+` und `M_Rd-` bei
  `N_Ed = 0`, `N_Rd+` und `N_Rd-` bei `M_Ed = 0`, dazu `x/d` bei
  `N_Ed = 0` je gezogene Seite;
* der Querkraftwiderstand bei `N_Ed = 0`. Ohne Buegel `V_Rd,max`, das
  Kleinere beider Seiten bei `M_Ed = 0`, und `V_Rd,min`, das Kleinere
  bei `M_Ed = M_Rd`. Mit Buegeln der Widerstand bei der guenstigsten
  Neigung, `V_Rd(alpha_opt)` -- auch er das Kleinere beider Seiten.

x/d je Seite, das Kleinere beider Seiten auch mit Buegeln und die
Handrechnung mit Bemessungswerten hat der Benutzer am 2026-10-16 bestaetigt.

Die Vergroesserungsfaktoren omega_w und omega_w' rechnet
[[opencivil.nachweis.verformung#Vergroesserungsfaktor|Vergroesserungsfaktor]]; die
Zusammenfassung stellt sie dazu.


## NICHTS ZWEIMAL

Rechnet die Tragsicherheit von Hand mit Bemessungswerten -- die Vorgabe --,
lesen die Kennzahlen deren Linie aus ihrem Befund und leiten nichts ein
zweites Mal her; sonst rechnen sie eine eigene, mit Herleitung (dasselbe
Muster wie das Knicken). Die Querkraft rechnet mit den Funktionen ihres
Nachweises: [[opencivil.nachweis.querkraft#beiwert_k_g|beiwert_k_g]],
[[opencivil.nachweis.querkraft#widerstand|widerstand]],
[[opencivil.nachweis.querkraft#neigungen|neigungen]].


## WAS DIE GRENZEN BEDEUTEN

Ohne Buegel ist bei `M_Ed = 0` die Dehnung null und `k_d = 1`; bei
`M_Ed = M_Rd` ist sie `f_yd/E_s`, gleich wie gross `M_Rd` ist.
Dazwischen liegt jeder Widerstand ohne Normalkraft.

## Inhalt

### Plattenkennzahlen

```python
class Plattenkennzahlen(Prozedur)
```

Die Kennzahlen einer Platte in x -- siehe Dateikopf.

- `THEMA = 'Kennzahlen'`

#### Plattenkennzahlen.rechne

```python
def rechne(self, e: Eingaben, p: Protokoll) -> Dict[str, Groesse]
```

#### Plattenkennzahlen._handrechnung

```python
def _handrechnung(self, e: Eingaben, p: Protokoll, werte: Zwischenwerte, ergebnis: Dict[str, Groesse]) -> Dict[bool, float]
```

M_Rd und x/d bei N = 0, N_Rd bei M = 0 -- aus der Linie der Handrechnung.

#### Plattenkennzahlen._auf_der_linie

```python
def _auf_der_linie(self, p: Protokoll, linie, ergebnis: Dict[str, Groesse], achse: geo.Achse, positiv: bool, kurz: str, titel: str) -> float
```

Ein Widerstand auf der Linie, die Gegengroesse null -- hergeleitet, wie
die Linie ihn findet: als Eckpunkt oder zwischen zweien.

#### Plattenkennzahlen._hoehen

```python
def _hoehen(self, e: Eingaben, werte: Zwischenwerte, p: Protokoll, beiwerte: Kurvenbeiwerte, positiv: bool, hoch: str) -> Optional[Tuple[Wert, Wert]]
```

`d` und `d_v` der gezogenen Seite, hergeleitet -- `None` ohne Zugbewehrung.

#### Plattenkennzahlen._kleinstes

```python
def _kleinstes(self, p: Protokoll, ergebnis: Dict[str, Groesse], kurz: str, teile: List[Wert], titel: str) -> None
```

Das Kleinere der Seiten -- bei nur einer Seite sie selbst.


## Konstanten

- `WAHL = Rechenwahl()` – Womit die Kennzahlen rechnen: die Handrechnung mit Bemessungswerten.
- `SEITEN = ((True, 'unten', '+'), (False, 'oben', '-'))` – Die beiden Seiten: ob der Zug unten liegt, wie sie heisst, ihr Zeichen.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.nachweis.biegung_normalkraft]]
- [[opencivil.nachweis.linie]]
- [[opencivil.nachweis.querkraft]]
- [[opencivil.nachweis.rechenwahl]]
- [[opencivil.querschnitt.fachwerk]]
- [[opencivil.querschnitt.gesetzwahl]]
- [[opencivil.querschnitt.platte]]

## Gebraucht von

- [[opencivil.projekt.aufbau]]

## Formeln aus diesem Modul

- [[Beiwert für die statische Höhe]] · `Plattenkennzahlen._ohne_buegel`
- [[Bezogene Druckzonenhöhe]] · `Plattenkennzahlen._handrechnung`
- [[Fliessdehnung]] · `Plattenkennzahlen._ohne_buegel`
- [[Kleinerer Widerstand beider Seiten]] · `Plattenkennzahlen._kleinstes`
- [[Querkraftwiderstand mit Querkraftbewehrung]] · `Plattenkennzahlen._mit_buegeln`
- [[Querkraftwiderstand ohne Bügel bei M_Ed = 0]] · `Plattenkennzahlen._ohne_buegel`
- [[Querkraftwiderstand ohne Querkraftbewehrung]] · `Plattenkennzahlen._ohne_buegel`
- [[Teilung in y aus der Stabzahl]] · `Plattenkennzahlen._mit_buegeln`
- [[Widerstand der Bügel]] · `Plattenkennzahlen._mit_buegeln`
- [[Widerstand der Druckdiagonalen]] · `Plattenkennzahlen._mit_buegeln`
- [[Wirksame Höhe (Einlage nicht massgebend)]] · `Plattenkennzahlen._hoehen`
- [[Wirksame Höhe, um die Einlage vermindert]] · `Plattenkennzahlen._hoehen`
