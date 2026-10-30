---
erzeugt: ce5791d5624b
art: modul
tags: [modul]
---
> [!abstract] opencivil/durchstanzen/nachweis.py
> der Durchstanznachweis nach SIA 262:2025, 4.3.6.
> Paket [[opencivil.durchstanzen]] · [Quelltext](../../opencivil/durchstanzen/nachweis.py)

## VERANTWORTUNG

Der Nachweis [[opencivil.durchstanzen.nachweis#Durchstanzen|Durchstanzen]] an einer Durchstanzstelle: der
Durchstanzwiderstand ohne Durchstanzbewehrung (4.3.6.3) gegen den
Bemessungswert der Querkraft, mit allem, was er braucht -- der statischen
Höhe (4.3.6.2.1), dem Nachweisschnitt (4.3.6.2.2 und 4.3.6.2.3,
[[opencivil.durchstanzen.schnitt|.schnitt]]), k_e (4.3.6.2.4 und 4.3.6.2.5), den Lasten im Schnitt
(4.3.6.2.6) und der Plattenrotation (4.3.6.4).


## DIE RECHNUNG


```
V_Rd,c = k_r · τ_cd · d_v · u                              (58)
k_r    = 1 / (0.45 + 0.18 · ψ · d · k_g)  ≤ 2              (59), d in mm
ψ      = 1.5 · r_s / d · f_yd / E_s · (m_sd / m_Rd)^(3/2)   (60)
u      = k_e · u_red
```

`u_red` ist der Nachweisschnitt ohne das, was nach Figur 23 nicht zählt;
`d` die mittlere statische Höhe der beiden Lagen der Zugbewehrung und
`d_v` die wirksame -- gleich `d`, solange die gestützte Fläche nicht in die
Platte reicht (Figur 21).


## DIE PLATTENROTATION (4.3.6.4.2)

In Näherungsstufe 1 ist `m_sd/m_Rd = 1`; in Stufe 2 kommen die Momente im
Stützstreifen aus den Gleichungen (62) bis (65), in Stufe 3 gibt sie der
Benutzer an, mit 1.2 statt 1.5 vor der Klammer. `r_s = 0.22 · l` in den
Stufen 1 und 2 (4.3.6.4.4). Massgebend ist die grössere Rotation der beiden
Richtungen. Für Wandende und Wandecke nennt 4.3.6.4.7 keine Momente; dort
rechnet Stufe 2 wie Stufe 1, und die Herleitung sagt es.


## DIE BREITE DER STÜTZSTREIFEN

(Figur 25), gelesen (nicht nachgeschlagen)
`b_s = 1.5 · √(r_sx · r_sy) ≤ l_min`. Ein Streifen senkrecht zum Rand einer
Randstütze und die Randstreifen einer Eckstütze sind auf `b_sr` begrenzt:
die Breite, die zwei Linien unter 45° von den inneren Ecken der Stütze am
Plattenrand einschliessen, `b_sr = b_x + 2 · (b_y + a_y)` für den Streifen
in y, entsprechend in x, höchstens `b_s`.


## EINHEITEN

SI-Basis; wo die Norm in mm rechnet (59), sagt es die Herleitung.

## Inhalt

### Rotation

```python
@dataclass(frozen=True)
class Rotation
```

Die Plattenrotation in einer Richtung: r_s, m_sd/m_Rd und ψ.

- `richtung: Richtung`
- `r_s: float`
- `m_sd: Optional[float]`
- `m_Rd: Optional[float]`
- `psi: float`

### Durchstanzbefund

```python
@dataclass(frozen=True)
class Durchstanzbefund
```

Was der Nachweis gefunden hat -- für die Zusammenfassung und das Bild.
Längen in m, Kräfte in N.

- `d: float`
- `d_v: float`
- `schnitt: Nachweisschnitt`
- `k_e: float`
- `u: float`
- `V_d: float`
- `V_d_red: float`
- `rotationen: Tuple[Rotation, ...]`
- `psi: float`
- `k_r: float`
- `V_Rd_c: float`
- `umriss: Tuple[Punkt, ...]`
- `aussparungen: Tuple[Tuple[Punkt, ...], ...]`
- `raender: Tuple[Tuple[Punkt, float], ...]` – Je Plattenrand ein Punkt auf ihm und die Richtung, in die die Platte liegt (rad).
- `bewehrung: Optional[Bewehrungsbefund] = None` – Die vorgeschlagene Durchstanzbewehrung -- `None`, wo der Beton allein reicht.

### Durchstanzen

```python
class Durchstanzen(Nachweis)
```

Der Durchstanznachweis an einer Durchstanzstelle -- siehe Dateikopf.

- `THEMA = 'Durchstanzen'`
- `ART = 'DS'`
- `LANGNAME = 'Durchstanzen'`

#### Durchstanzen.mit_graden

```python
@property
def mit_graden(self) -> Tuple[WertDef, ...]
```

Die Grade der vier Nachweise mit Durchstanzbewehrung (4.3.6.5.1).

#### Durchstanzen.nicht_fuehrbar

```python
def nicht_fuehrbar(self, grund: str) -> List[NachweisUrteil]
```

Die vier Urteile mit Durchstanzbewehrung, wo sich keine finden liess.

#### Durchstanzen.pruefe

```python
def pruefe(self, e: Eingaben, p: Protokoll) -> Ausfuehrung
```

#### Durchstanzen._statische_hoehe

```python
def _statische_hoehe(self, e: Eingaben, p: Protokoll, w: Zwischenwerte) -> Tuple[Wert, Wert, Dict[Richtung, Wert]]
```

Die statischen Höhen der beiden Lagen, ihr Mittel d und die wirksame d_v (4.3.6.2.1).

#### Durchstanzen._nachweisschnitt

```python
def _nachweisschnitt(self, e: Eingaben, p: Protokoll, w: Zwischenwerte, schnitt: Nachweisschnitt, masse: Dict[str, float], d_v: Wert) -> Wert
```

Der Nachweisschnitt und was von ihm nicht zählt: `u_red`, noch ohne k_e.

#### Durchstanzen._exzentrizitaet

```python
def _exzentrizitaet(self, e: Eingaben, a: Auswertung, masse: Dict[str, float]) -> Tuple[float, float]
```

e_u: von dem Schwerpunkt der zählenden Teile des Schnitts zur Resultierenden
der Auflagerkraft -- je Komponente, in m.

#### Durchstanzen._k_e

```python
def _k_e(self, e: Eingaben, p: Protokoll, w: Zwischenwerte, a: Auswertung, e_u: Tuple[float, float]) -> Wert
```

Der Beiwert k_e: aus der Näherung (4.3.6.2.5) oder aus der Exzentrizität (57).

#### Durchstanzen._lasten

```python
def _lasten(self, e: Eingaben, p: Protokoll, w: Zwischenwerte, a: Auswertung) -> Wert
```

Der Bemessungswert der Querkraft, ohne die Flächenlast innerhalb des Schnitts (4.3.6.2.6).

#### Durchstanzen._rotation

```python
def _rotation(self, e: Eingaben, p: Protokoll, w: Zwischenwerte, d: Wert, hoehen: Dict[Richtung, Wert], V_d: Wert, e_u: Tuple[float, float], masse: Dict[str, float]) -> Tuple[Tuple[Rotation, ...], Wert]
```

ψ je Richtung und die massgebende -- die grössere (4.3.6.4.1).

#### Durchstanzen._m_Rd

```python
def _m_Rd(self, e: Eingaben, p: Protokoll, w: Zwischenwerte, r: Richtung, d_r: Wert) -> Wert
```

Der Biegewiderstand je Meter im Stützstreifen, aus dem Kräftegleichgewicht (Spannungsblock).

#### Durchstanzen._m_sd

```python
def _m_sd(self, e: Eingaben, p: Protokoll, w: Zwischenwerte, r_s: Dict[Richtung, Wert], V_d: Wert, e_u: Tuple[float, float], masse: Dict[str, float]) -> Dict[Richtung, Optional[Wert]]
```

Die mittleren Momente im Stützstreifen in Näherungsstufe 2 (4.3.6.4.7).

#### Durchstanzen._b_sr

```python
def _b_sr(self, p: Protokoll, w: Zwischenwerte, r: Richtung, b_s: Wert, masse: Dict[str, float]) -> Wert
```

Die Breite eines Streifens senkrecht zum Rand oder eines Randstreifens an
der Ecke (Figur 25) -- siehe Dateikopf.

#### Durchstanzen._k_r

```python
def _k_r(self, e: Eingaben, p: Protokoll, w: Zwischenwerte, psi: Wert, d: Wert) -> Wert
```

Der Beiwert k_r (59), mit k_g nach 4.3.3.2.1.

### _mehrzahl

```python
def _mehrzahl(lage: Lage) -> str
```

«Innenstützen», «Wandenden» -- wie die Näherung von 4.3.6.2.5 sie nennt.

### angaben

```python
def angaben(stelle: Durchstanzstelle, werte: Dict[str, Wert]) -> GleichungBlock
```

Was über der Tabelle steht: Lage, Platte, Beton und die Masse, wie gerechnet.

### kennwerttabelle

```python
def kennwerttabelle(befund: Durchstanzbefund) -> TabellenBlock
```

Die Grössen, aus denen der Widerstand entsteht -- eine Zeile je Grösse. Mit
Durchstanzbewehrung dazu das Produkt und die Widerstände mit ihm.


## Konstanten

- `K_R_GRENZE = 2.0` – Obere Grenze von k_r (SIA 262:2025, Gleichung (59)).
- `R_S = 0.22` – `r_s = R_S · l` in den Näherungsstufen 1 und 2 (SIA 262:2025, 4.3.6.4.4).
- `ROTATION_MINDEST = 0.02` – Unter dieser Plattenrotation fehlt Verformungsvermögen, wenn keine Durchstanzbewehrung nach (67) liegt (SIA 262:2025, 4.3.6.1.2).

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.durchstanzen.mit_bewehrung]]
- [[opencivil.durchstanzen.schnitt]]
- [[opencivil.durchstanzen.stelle]]
- [[opencivil.nachweis.querkraft_ohne_buegel]]
- [[opencivil.querschnitt.platte]]
- [[opencivil.querschnitt.werkstoffgesetz]]

## Gebraucht von

- [[opencivil.bericht.zusammenfassung]]
- [[opencivil.durchstanzen.mit_bewehrung]]
- [[opencivil.projekt.aufbau.durchstanzen]]
- [[opencivil.web.durchstanzdaten]]

## Formeln aus diesem Modul

- [[Abstand zum Momentennullpunkt]] · `Durchstanzen._rotation`
- [[Beiwert der Momentenübertragung]] · `Durchstanzen._k_e`
- [[Beiwert k_r]] · `Durchstanzen._k_r`
- [[Bemessungswert der Querkraft im Nachweisschnitt]] · `Durchstanzen._lasten`
- [[Biegebewehrung im Stützstreifen je Meter]] · `Durchstanzen._m_Rd`
- [[Biegewiderstand im Stützstreifen]] · `Durchstanzen._m_Rd`
- [[Breite des Stützstreifens]] · `Durchstanzen._m_sd`
- [[Breite des Stützstreifens am Plattenrand]] · `Durchstanzen._b_sr`
- [[Druckzonenhöhe im Stützstreifen]] · `Durchstanzen._m_Rd`
- [[Durchmesser des flächengleichen Kreises]] · `Durchstanzen._k_e`
- [[Durchstanzwiderstand ohne Durchstanzbewehrung]] · `Durchstanzen.pruefe`
- [[Flächenlast innerhalb des Nachweisschnitts]] · `Durchstanzen._lasten`
- [[Massgebende Plattenrotation – die grössere]] · `Durchstanzen._rotation`
- [[Mittlere statische Höhe der beiden Lagen der Zugbewehrung]] · `Durchstanzen._statische_hoehe`
- [[Mittleres Moment im Stützstreifen]] · `Durchstanzen._m_sd`
- [[Nachweisschnitt im Abstand d_v∕2]] · `Durchstanzen._nachweisschnitt`
- [[Nachweisschnitt ohne das, was nicht zählt]] · `Durchstanzen._nachweisschnitt`
- [[Nachweisschnitt um das Wandende – 1.5·d_v entlang der Wand]] · `Durchstanzen._nachweisschnitt`
- [[Nachweisschnitt um die Wandecke – je 1.5·d_v entlang der Wände]] · `Durchstanzen._nachweisschnitt`
- [[Plattenrotation]] · `Durchstanzen._rotation`
- [[Statische Höhe der äusseren Lage]] · `Durchstanzen._statische_hoehe`
- [[Statische Höhe der inneren Lage]] · `Durchstanzen._statische_hoehe`
- [[Wirksame Höhe ohne Abzug]] · `Durchstanzen._statische_hoehe`
- [[Wirksamer Umfang des Nachweisschnitts]] · `Durchstanzen.pruefe`
