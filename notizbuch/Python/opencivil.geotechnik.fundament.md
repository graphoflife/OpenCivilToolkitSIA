---
erzeugt: b6fc1bd6939a
art: modul
tags: [modul]
---
> [!abstract] opencivil/geotechnik/fundament.py
> ein Flachfundament auf seinem Baugrund.
> Paket [[opencivil.geotechnik]] · [Quelltext](../../opencivil/geotechnik/fundament.py)

## VERANTWORTUNG

Das [[opencivil.geotechnik.fundament#Fundament|Fundament]] -- Boden, Abmessungen, Gelände und Grundwasser als
Vorgaben, dazu die Bemessungswerte der Scherfestigkeit --, die
[[opencivil.geotechnik.fundament#Kombination|Kombination]] einer Einwirkung und was die zwei Nachweise am
Fundament gemeinsam haben ([[opencivil.geotechnik.fundament#Fundamentnachweis|Fundamentnachweis]]): den Grundbruch
([[opencivil.geotechnik.grundbruch|grundbruch]]) und das Gleiten
([[opencivil.geotechnik.gleiten|gleiten]]). Dazu die Angaben über der Tabelle
der Zusammenfassung ([[opencivil.geotechnik.fundament#angaben|angaben]]).

Gerechnet wird mit Bemessungswerten: phi_eff = arctan(tan phi_k / gamma_phi)
und c_eff = c_k / gamma_c, undrainiert s_u,d = s_u,k / gamma_cu (SIA
267:2013, 5.3.2.1, 5.3.2.2). Ein globaler Sicherheitsgrad wie F_stat des
Buches kommt nicht dazu; den Widerstandsbeiwert gamma_R der Norm (8.5.2.1)
setzen beide Nachweise 1.0 (notizbuch/Notizen/TODO.md).


## WINKEL

(Bild 9.2.15 in Lang, Huder, Amann, Puzrin: Bodenmechanik und
Grundbau, 8. Aufl. 2007):
alpha ist die Neigung der Sohle, positiv, wenn sie gegen T ansteigt -- das
Abgleiten wird schwerer; beta die Neigung des Geländes, positiv, wenn es vom
Fundament weg abfällt. N steht normal zur Sohle, T in ihrer Richtung.


## EINHEITEN

Alles in SI-Basis; die Winkel als Groessen in Grad.

## Inhalt

### _boden

```python
def _boden(verhalten: Verhalten) -> Tuple[Feld, ...]
```

Je Verhalten seine Festigkeit; was nicht gilt, steht weder in der
Herleitung noch in der Maske (Benutzer, 2026-11-19). Das Wasser zählt nur
drainiert, über γ' -- undrainiert gelten totale Spannungen.

### Fundament

```python
@dataclass
class Fundament(Rechenobjekt)
```

Ein Flachfundament auf seinem Baugrund: die Eingaben als Vorgaben im
Rechenwerk, dazu die Bemessungswerte -- drainiert phi_eff, c_eff und
gamma', undrainiert s_u,d.

`b` ist die Breite, die kürzere Seite, `L` die Länge; ein
Streifenfundament ist ein sehr langes.

- `WAS = 'Grundbruch'`
- `name: str`
- `verhalten: Verhalten`
- `phi_k: Groesse`
- `gamma_phi: Groesse`
- `c_k: Groesse`
- `gamma_c: Groesse`
- `s_u: Groesse`
- `gamma_cu: Groesse`
- `gamma: Groesse`
- `gamma_w: Groesse`
- `q_Ed: Groesse`
- `b: Groesse`
- `L: Groesse`
- `t1: Groesse`
- `t: Groesse`
- `alpha: Groesse`
- `beta: Groesse`
- `delta_faktor: Groesse`
- `praefix: str`
- `definitionen: Dict[str, WertDef] = field(default_factory=dict, init=False)`
- `berechnungen: List[Berechnung] = field(default_factory=list, init=False)`

#### Fundament.abschnitt

```python
@property
def abschnitt(self) -> Abschnitt
```

Ueberschrift, unter der das Fundament in der Herleitung steht.

### Kombination

```python
@dataclass(frozen=True)
class Kombination
```

Eine Einwirkung auf das Fundament: N normal zur Sohle, T in ihrer Richtung.

- `name: str`
- `N_Ed: Groesse`
- `T_Ed: Groesse`

#### Kombination.kennung

```python
@property
def kennung(self) -> str
```

### Fundamentnachweis

```python
class Fundamentnachweis(Nachweis)
```

Was Grundbruch und Gleiten gemeinsam haben: je Kombination einen
Erfüllungsgrad, die Eingänge aus dem Fundament -- je Verhalten andere --,
Titel und Abschnitt, und wie ein Fall ausgeht ([[opencivil.geotechnik.fundament#Fundamentnachweis.vergleichen|vergleichen]]).
Vorbild ist [[opencivil.pfahl.achse#Achsnachweis|Achsnachweis]].

- `FELD: str = ''` – Wie der Nachweis im Aufbau und in seinen Kennungen heisst: «grundbruch».
- `BODEN: Dict[Verhalten, Tuple[str, ...]] = {}` – Was er je Verhalten vom Boden liest -- drainiert anderes als undrainiert.
- `MASSE: Tuple[str, ...] = ()` – Was er sonst vom Fundament liest, unter jedem Verhalten.

#### Fundamentnachweis.vergleichen

```python
def vergleichen(self, p: Protokoll, k: Kombination, E: Wert, R: Wert, namen: Tuple[str, str]) -> Tuple[Vergleich, str]
```

Die Einwirkung `E` einer Kombination gegen den Widerstand `R`, in
die Herleitung geschrieben, und der Satz für die Nachweistabelle --
«N_Rd = 812.3 kN ≥ N_Ed = 600.0 kN.»; `namen` sind die von E und R.

### angaben

```python
def angaben(fundament: Fundament, werte: Dict[str, Wert]) -> GleichungBlock
```

Die Angaben über der Tabelle, aus den Werten der Lösung, wie sie
gerechnet wurden: in der ersten Zeile der Boden mit seinen
Bemessungswerten, in der zweiten die Masse und das Grundwasser. In einer
Zeile wären es acht Angaben -- breiter als die Spalte.


## Konstanten

- `KAP_AUFLAST = 'Kap. 9.2.5'` – Die dauernde Auflast neben dem Fundament, Kap. 9.2.5 des Buches.
- `_TABELLE_1 = 'SIA 267:2013, 5.3.2.2, Tabelle 1'` – Die Teilfaktoren des Bodens und seine Raumlast.
- `VORGABEN = (Gruppe('Boden', _boden, nach=('verhalten',)), Gruppe('Fundament', la…` – Die Vorgaben des Grundbruchs, je Kasten der Herleitung und Karte der Maske ([[opencivil.core.vorgaben]]). Die Sohlreibung hängt am Reibungswinkel: undrainiert gilt sie nicht.
- `OHNE_GAMMA_R = 'Grundbruch- und Gleitwiderstand ohne Widerstandsbeiwert, γ_R = 1.0. …` – Was beide Widerstände annehmen -- die Norm teilt sie noch durch gamma_R.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.nachweis]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.rechenobjekt]]
- [[opencivil.core.vorgaben]]
- [[opencivil.core.wert]]
- [[opencivil.geotechnik.verhalten]]

## Gebraucht von

- [[opencivil.bericht.zusammenfassung]]
- [[opencivil.geotechnik.gleiten]]
- [[opencivil.geotechnik.grundbruch]]
- [[opencivil.projekt.aufbau.grundbruch]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.web.api]]
- [[opencivil.web.grundbruchdaten]]

## Formeln aus diesem Modul

- [[Bemessungswert der Kohäsion]] · `_c_eff`
- [[Bemessungswert der undrainierten Scherfestigkeit]] · `_s_u_d`
- [[Bemessungswert des Reibungswinkels]] · `_phi_eff`
- [[Raumlast unter Auftrieb]] · `_gamma_auftrieb`
