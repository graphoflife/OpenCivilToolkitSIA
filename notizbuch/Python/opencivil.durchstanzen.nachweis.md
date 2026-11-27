---
erzeugt: 1f84ccfadcff
art: modul
tags: [modul]
---
> [!abstract] opencivil/durchstanzen/nachweis.py
> der Durchstanznachweis nach SIA 262:2025, 4.3.6.
> Paket [[opencivil.durchstanzen]] · [Quelltext](../../opencivil/durchstanzen/nachweis.py)

## VERANTWORTUNG

Der Nachweis [[opencivil.durchstanzen.nachweis#Durchstanzen|Durchstanzen]] an einer Durchstanzstelle: der
Durchstanzwiderstand ohne Durchstanzbewehrung (4.3.6.3) gegen den
Bemessungswert der Querkraft, mit allem, was er braucht – der statischen
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
`d_v` die wirksame – gleich `d`, solange die gestützte Fläche nicht in die
Platte reicht (Figur 21).


## DIE PLATTENROTATION (4.3.6.4.2)

In Näherungsstufe 1 ist `m_sd/m_Rd = 1`; in Stufe 2 kommen die Momente im
Stützstreifen aus den Gleichungen (62) bis (65), in Stufe 3 gibt sie der
Benutzer an, und in (60) steht 1.2 statt 1.5 als erster Faktor; an Rand- und
Eckstützen gilt dann r_s ≥ 2/3 · b_sr (4.3.6.4.8). `r_s = 0.22 · l` in den
Stufen 1 und 2 (4.3.6.4.4). Massgebend ist die grössere Rotation der beiden
Richtungen. Für Wandende und Wandecke nennt 4.3.6.4.7 keine Momente; dort
rechnet Stufe 2 wie Stufe 1, und die Herleitung sagt es.


## DIE BREITE DER STÜTZSTREIFEN (4.3.6.4.6, Figur 25)

`b_s = 1.5 · √(r_sx · r_sy) ≤ l_min`. Ein Streifen senkrecht zum Rand einer
Randstütze und die Randstreifen einer Eckstütze sind auf `b_sr` begrenzt:
die Breite, die zwei Linien unter 45° von den inneren Ecken der Stütze am
Plattenrand einschliessen, `b_sr = b_x + 2 · (b_y + a_y)` für den Streifen
in y, entsprechend in x. An der Randstütze ist der Streifen
`min[b_s; b_sr]` breit. An der Eckstütze schneidet ihn quer der zweite
Rand ab: die halbe Breite `min[b_s; b_sr]/2` innen, zum zweiten Rand hin
nur bis zu ihm, `b_x/2 + a_x` für den Streifen in y, höchstens ebenso viel.
Bis 2026-11-14 lag er an der Ecke symmetrisch um die Achse, bis zu 50 %
breiter, als Figur 25 ihn zeigt.

DIE KRAFT IN m_sd (Benutzer, 2026-11-26):
Die Gleichungen (62) bis (65) rechnen mit der ganzen Auflagerkraft `V_d`,
ohne die Last innerhalb des Nachweisschnitts abzuziehen. Die Norm sagt nicht
ausdruecklich, welches V_d dort gilt; der Abzug nach 4.3.6.2.6 ist erlaubt,
nicht verlangt. Das Skript «Stahlbeton II, 7.4 Platten» (Kaufmann, FS 2026,
Folie 28) verknuepft m_sd mit der Stuetzenreaktion: die Momente im
Stuetzstreifen entstehen aus der ganzen Stuetzenkraft. Das liegt auf der
sicheren Seite. Den Abzug behaelt die Querkraft im Nachweis, in (66) und
(67) und am aeusseren Schnitt. Bis 2026-11-25 kam m_sd aus V_d,red – bei
einer Bodenplatte mit 150 kN/m² Bodenpressung bis 7 % zu viel Widerstand,
bei einer Decke unter 1 %.


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

### Biegelage

```python
@dataclass(frozen=True)
class Biegelage
```

Eine Lage der Zugbewehrung über der Stütze, wie gerechnet – fürs Bild der Leiste.

- `richtung: Richtung`
- `tiefe: float` – Wie weit ihre Mitte unter der Oberfläche der Zugseite liegt: h − d in ihrer Richtung.
- `durchmesser: float`
- `abstand: float`

### Durchstanzbefund

```python
@dataclass(frozen=True)
class Durchstanzbefund
```

Was der Nachweis gefunden hat – für die Zusammenfassung und das Bild.
Längen in m, Kräfte in N. Leisten und Stahlpilz stehen nur da, wo es sie
braucht; jedes mit seinen eigenen Zahlen.

- `d: float`
- `innen: Schnittpruefung` – Der Schnitt um die gestützte Fläche.
- `rotationen: Tuple[Rotation, ...]`
- `psi: float`
- `k_r: float`
- `V_Rd_c: float`
- `umriss: Tuple[Punkt, ...]`
- `aussparungen: Tuple[Tuple[Punkt, ...], ...]`
- `raender: Tuple[Tuple[Punkt, float], ...]` – Je Plattenrand ein Punkt auf ihm und die Richtung, in die die Platte liegt (rad).
- `lagen: Tuple[Biegelage, ...] = ()` – Die beiden Lagen der Zugbewehrung, die äussere zuerst.
- `leisten: Optional[Leistenpruefung] = None` – Die vorgeschlagene Durchstanzbewehrung mit ihren Nachweisen (4.3.6.5.1).
- `pilz: Optional[Pilzbefund] = None` – Der gewählte Stahlpilz; mit `leisten` stehen die Leisten um ihn.

#### Durchstanzbefund.ohne_einwirkung

```python
@property
def ohne_einwirkung(self) -> bool
```

Ob die Stütze nichts trägt – dann ist nichts durchzustanzen. Die eine
Stelle für Nachweis und Grundriss: dort stand bis 2026-11-27
«V_d = 0 ≤ V_Rd,c – erfüllt, α = ∞».

### Stuetzenschnitt

```python
@dataclass(frozen=True)
class Stuetzenschnitt
```

Der Schnitt um die gestützte Fläche mit allem, was nicht von der
Stützenkraft abhängt – für Nachweis und Kennzahl derselbe.

- `masse: Dict[str, float]`
- `d: Wert`
- `d_v: Wert`
- `hoehen: Dict[Richtung, Wert]`
- `innen: Schnittpruefung`
- `k_e: Wert`
- `u: Wert`
- `e_u: Tuple[float, float]` – Die Exzentrizität der Resultierenden zum Schwerpunkt des Schnitts, je Richtung.

### Widerstand

```python
@dataclass(frozen=True)
class Widerstand
```

Was an der Stütze von der Stützenkraft abhängt: ψ, k_r und V_Rd,c.

- `rotationen: Tuple[Rotation, ...]`
- `psi: Wert`
- `k_r: Wert`
- `tau_cd: Wert`
- `V_Rd_c: Wert`

### Stuetzenrechnung

```python
class Stuetzenrechnung
```

Was der Nachweis ([[opencivil.durchstanzen.nachweis#Durchstanzen|Durchstanzen]]) und die Kennzahl
([[opencivil.durchstanzen.kennzahl#Durchstanzkennzahl|Durchstanzkennzahl]]) an der
Stütze gleich rechnen, je mit seiner Herleitung: den Schnitt um sie
([[opencivil.durchstanzen.nachweis#Stuetzenrechnung._schnitt|_schnitt]]) und ihren Widerstand ohne Durchstanzbewehrung bei einer
Stützenkraft ([[opencivil.durchstanzen.nachweis#Stuetzenrechnung._widerstand|_widerstand]]). Beide sind Berechnungen einer
`stelle`; die Kennzahl rechnet den Widerstand still bei vielen Kräften
und schreibt nur den letzten.

- `stelle: Durchstanzstelle`
- `id: str`

#### Stuetzenrechnung._schnitt

```python
def _schnitt(self, e: Eingaben, p: Protokoll, w: Zwischenwerte, V_d: float) -> Stuetzenschnitt
```

Statische Höhe, Nachweisschnitt, k_e und wirksamer Umfang – `V_d` in N.

#### Stuetzenrechnung._widerstand

```python
def _widerstand(self, e: Eingaben, p: Protokoll, w: Zwischenwerte, g: Stuetzenschnitt, V_d: Wert, ergebnis: Optional[WertDef]=None) -> Widerstand
```

ψ, k_r und V_Rd,c bei der Stützenkraft `V_d`: in Näherungsstufe 2
wachsen die Momente im Stützstreifen mit ihr. `ergebnis` ist die
Definition, die V_Rd,c belegt – sonst ein Zwischenwert.

#### Stuetzenrechnung._statische_hoehe

```python
def _statische_hoehe(self, e: Eingaben, p: Protokoll, w: Zwischenwerte) -> Tuple[Wert, Wert, Dict[Richtung, Wert]]
```

Die statischen Höhen der beiden Lagen, ihr Mittel d und die wirksame d_v (4.3.6.2.1).

#### Stuetzenrechnung._nachweisschnitt

```python
def _nachweisschnitt(self, e: Eingaben, p: Protokoll, w: Zwischenwerte, a: Auswertung, d_v: Wert) -> Wert
```

Der Nachweisschnitt und was von ihm nicht zählt: `u_red`, noch ohne
k_e. Wo die gestützte Fläche eine Formel für u_0 kennt, steht sie da,
sonst die Länge in der Platte; die Abzüge schreibt [[opencivil.durchstanzen.herleitung|.herleitung]],
wie an jedem Schnitt.

#### Stuetzenrechnung._resultierende

```python
def _resultierende(self, e: Eingaben, masse: Masse) -> Punkt
```

Wo die Auflagerkraft angreift: in der Stützenachse, verschoben um die
Exzentrizität e_x, e_y, wo k_e nach (57) sie liest. Von hier misst e_u
an jedem Schnitt – um die Stütze, um die äussersten Anker und um den Pilz.

#### Stuetzenrechnung._rotation

```python
def _rotation(self, e: Eingaben, p: Protokoll, w: Zwischenwerte, d: Wert, hoehen: Dict[Richtung, Wert], e_u: Tuple[float, float], masse: Dict[str, float], V_d: Wert) -> Tuple[Tuple[Rotation, ...], Wert]
```

ψ je Richtung und die massgebende, die grössere (4.3.6.4.1) – bei der Kraft `V_d`.

#### Stuetzenrechnung._m_Rd

```python
def _m_Rd(self, e: Eingaben, p: Protokoll, w: Zwischenwerte, r: Richtung, d_r: Wert) -> Wert
```

Der Biegewiderstand je Meter im Stützstreifen, aus dem Kräftegleichgewicht (Spannungsblock).

#### Stuetzenrechnung._m_sd

```python
def _m_sd(self, e: Eingaben, p: Protokoll, w: Zwischenwerte, r_s: Dict[Richtung, Wert], e_u: Tuple[float, float], masse: Dict[str, float], V_d: Wert) -> Dict[Richtung, Optional[Wert]]
```

Die mittleren Momente im Stützstreifen in Näherungsstufe 2 (4.3.6.4.7),
aus der ganzen Auflagerkraft `V_d` – siehe Dateikopf.

#### Stuetzenrechnung._b_sr

```python
def _b_sr(self, p: Protokoll, w: Zwischenwerte, r: Richtung, rand: Randbreite) -> Wert
```

b_sr des Streifens in `r`: zwischen den Linien unter 45° (Figur 25) – siehe Kopf.

#### Stuetzenrechnung._breite_am_rand

```python
def _breite_am_rand(self, p: Protokoll, w: Zwischenwerte, r: Richtung, b_s: Wert, rand: Randbreite) -> Wert
```

Die Breite eines Streifens, den der Plattenrand begrenzt: höchstens
b_sr, an der Ecke vom zweiten Rand abgeschnitten – siehe Dateikopf.

#### Stuetzenrechnung._r_s_am_rand

```python
def _r_s_am_rand(self, e: Eingaben, p: Protokoll, w: Zwischenwerte, r: Richtung, rand: Randbreite) -> Wert
```

In Stufe 3 an Rand- und Eckstützen: r_s mindestens 2/3 · b_sr (4.3.6.4.8).

#### Stuetzenrechnung._k_r

```python
def _k_r(self, e: Eingaben, p: Protokoll, w: Zwischenwerte, psi: Wert, d: Wert) -> Wert
```

Der Beiwert k_r (59), mit k_g nach 4.3.3.2.1.

### Durchstanzen

```python
class Durchstanzen(Stuetzenrechnung, Nachweis)
```

Der Durchstanznachweis an einer Durchstanzstelle – siehe Dateikopf.

- `THEMA = 'Durchstanzen'`
- `ART = 'DS'`
- `LANGNAME = 'Durchstanzen'`

#### Durchstanzen.mit_graden

```python
@property
def mit_graden(self) -> Tuple[WertDef, ...]
```

Die vier Grade mit Durchstanzbewehrung: die drei Nachweise nach
4.3.6.5.1, der erste geteilt in den Beitrag der Bewehrung (66), (68)
und das Verformungsvermögen (67).

#### Durchstanzen.nicht_fuehrbar

```python
def nicht_fuehrbar(self, grund: str) -> List[NachweisUrteil]
```

Die vier Urteile mit Durchstanzbewehrung, wo sich keine finden liess.

#### Durchstanzen.pruefe

```python
def pruefe(self, e: Eingaben, p: Protokoll) -> Ausfuehrung
```

### angaben

```python
def angaben(stelle: Durchstanzstelle, werte: Dict[str, Wert]) -> GleichungBlock
```

Was über der Tabelle steht: Lage, Platte, Beton und die Masse, wie gerechnet.

### kennwerttabelle

```python
def kennwerttabelle(befund: Durchstanzbefund) -> TabellenBlock
```

Die Grössen, aus denen der Widerstand entsteht – eine Zeile je Grösse. Mit
Stahlpilz und Durchstanzbewehrung dazu, was sie sind und was sie tragen.
Ohne Einwirkung nur der Schnitt: ψ = 0 und k_r = 2 gälten nur ohne Last;
was die Stelle trägt, sagt die Kennzahl ([[opencivil.durchstanzen.kennzahl|.kennzahl]]). Bis 2026-11-27
stand dort V_Rd,c = 866.7 kN, wo die Kennzahl 503.6 kN sagt.


## Konstanten

- `K_R_GRENZE = 2.0` – Obere Grenze von k_r (SIA 262:2025, Gleichung (59)).
- `R_S = 0.22` – `r_s = R_S · l` in den Näherungsstufen 1 und 2 (SIA 262:2025, 4.3.6.4.4).
- `ROTATION_MINDEST = 0.02` – Unter dieser Plattenrotation fehlt Verformungsvermögen, wenn keine Durchstanzbewehrung nach (67) liegt (SIA 262:2025, 4.3.6.1.2).
- `EINZELLASTEN = 'Nicht geprüft: Einzellasten über 0.2·V_d, die näher als 3·d_v am Nac…` – Was der Nachweis nicht prueft, weil er die Lasten um die Stuetze nicht kennt (SIA 262:2025, 4.3.6.2.3, vierter Fall).

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.nachweis]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.durchstanzen.flaeche]]
- [[opencivil.durchstanzen.herleitung]]
- [[opencivil.durchstanzen.mit_bewehrung]]
- [[opencivil.durchstanzen.pruefung]]
- [[opencivil.durchstanzen.schnitt]]
- [[opencivil.durchstanzen.stelle]]
- [[opencivil.nachweis.querkraft_ohne_buegel]]
- [[opencivil.querschnitt.platte]]
- [[opencivil.querschnitt.werkstoffgesetz]]

## Gebraucht von

- [[opencivil.bericht.zusammenfassung]]
- [[opencivil.durchstanzen.kennzahl]]
- [[opencivil.durchstanzen.mit_bewehrung]]
- [[opencivil.projekt.aufbau.durchstanzen]]
- [[opencivil.web.durchstanzdaten]]

## Formeln aus diesem Modul

- [[Abstand zum Momentennullpunkt]] · `Stuetzenrechnung._rotation`
- [[Abstand zum Momentennullpunkt am Plattenrand]] · `Stuetzenrechnung._r_s_am_rand`
- [[Beiwert k_r]] · `Stuetzenrechnung._k_r`
- [[Biegebewehrung im Stützstreifen je Meter]] · `Stuetzenrechnung._m_Rd`
- [[Biegewiderstand im Stützstreifen]] · `Stuetzenrechnung._m_Rd`
- [[Breite des Randstreifens an der Eckstütze]] · `Stuetzenrechnung._breite_am_rand`
- [[Breite des Stützstreifens]] · `Stuetzenrechnung._m_sd`
- [[Breite des Stützstreifens am Plattenrand]] · `Stuetzenrechnung._b_sr`
- [[Breite des Stützstreifens senkrecht zum Rand]] · `Stuetzenrechnung._breite_am_rand`
- [[Druckzonenhöhe im Stützstreifen]] · `Stuetzenrechnung._m_Rd`
- [[Massgebende Plattenrotation – die grössere]] · `Stuetzenrechnung._rotation`
- [[Mittlere statische Höhe der beiden Lagen der Zugbewehrung]] · `Stuetzenrechnung._statische_hoehe`
- [[Mittleres Moment im Stützstreifen]] · `Stuetzenrechnung._m_sd`
- [[Nachweisschnitt im Abstand d_v∕2]] · `Stuetzenrechnung._nachweisschnitt`
- [[Nachweisschnitt um das Wandende – 1.5·d_v entlang der Wand]] · `Stuetzenrechnung._nachweisschnitt`
- [[Nachweisschnitt um die Wandecke – je 1.5·d_v entlang der Wände]] · `Stuetzenrechnung._nachweisschnitt`
- [[Plattenrotation]] · `Stuetzenrechnung._rotation`
- [[Statische Höhe der äusseren Lage]] · `Stuetzenrechnung._statische_hoehe`
- [[Statische Höhe der inneren Lage]] · `Stuetzenrechnung._statische_hoehe`
- [[Wirksame Höhe ohne Abzug]] · `Stuetzenrechnung._statische_hoehe`
