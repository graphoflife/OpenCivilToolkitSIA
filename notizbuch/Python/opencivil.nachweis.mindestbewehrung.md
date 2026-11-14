---
erzeugt: 41e87d72edf9
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/mindestbewehrung.py
> Mindestbewehrung gegen breite Risse bei Zwang.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/mindestbewehrung.py)

## VERANTWORTUNG

Prueft, ob die Bewehrung uebernehmen kann, was der Beton beim Reissen abgibt --
ohne dabei ueber die zulaessige Stahlspannung zu kommen: die Begrenzung der
Rissbreiten unter aufgezwungenen oder behinderten Verformungen, beim
Erreichen von `f_ct,eff` (SIA 262:2025, 4.4.2.3.4, Tabelle 17, Zeile 2).


## WARUM

Eine aufgezwungene Verkuerzung oder Kruemmung zieht den Querschnitt, bis er
reisst, und der Beton gibt seine Zugkraft an die Bewehrung ab. Nimmt sie sie
nur mit hoher Spannung auf, werden die Risse breit. Das sproede Versagen ist
ein anderer Nachweis ([[opencivil.nachweis.sproedes_versagen]],
4.3.1.2): dort steht der Widerstand gegen die Rissbeanspruchung.


## RISSNORMALKRAFT (Normalkraft-Zwaengung)


```
h_eff    = min(500 mm; h)   falls begrenzt, sonst h
k_t      = 1 / (1 + 0.5 * h_eff)          h_eff in Metern
f_ct,eff = k_t * f_ctm
N_Riss   = h_eff/2 * b * f_ct,eff
N_s,adm  = A_s * sigma_s,adm  >=  N_Riss
```

`h_eff/2` ist die gezogene Haelfte des Querschnitts, je Lage. `k_t` traegt
dem Rechnung, dass eine dicke Platte nicht ueber ihre ganze Hoehe gleichzeitig
reisst (4.4.1.3, (99), (100)). Bei massigen Bauteilen darf die Zugzone auf
250 mm je gezogenem Rand beschraenkt werden, unter zentrischem Zug also auf
500 mm; dieselbe Dicke gilt dann fuer `k_t` (4.4.2.3.7).


## ZULAESSIGE STAHLSPANNUNG

Bei *normaler* Anforderung gilt `f_yk` -- die Bewehrung darf bis an die
Fliessgrenze gehen. Bei *erhoehter* und *hoher* Anforderung begrenzt
zusaetzlich die nominelle Rissbreite, 0.5 und 0.2 mm (Tabelle 17):

```
sigma_s,adm = min( sqrt(9 * E_s * f_ctm * w_nom / durchmesser); f_yk )
```

`f_yk` und nicht `f_yd`: so steht es in Tabelle 17 und in (102).


## EINHEITEN

Alles in SI-Basis. Die Wurzelformel ist dimensionell stimmig -- `E_s * f_ctm`
gibt Pa^2, `w_nom/durchmesser` ist dimensionslos, die Wurzel also Pa.

## Inhalt

### Rissgroessen

```python
@dataclass(frozen=True)
class Rissgroessen
```

Was allein von der Platte abhaengt, nicht von der einzelnen Lage.

- `h_eff: float` – Rissaktive Plattendicke in m.
- `k_t: float`
- `f_ct_eff: float`
- `N_Riss: float` – Risskraft in N, bezogen auf die betrachtete Breite.

### rissnormalkraft

```python
def rissnormalkraft(*, h: float, b: float, f_ctm: float, begrenzt: bool) -> Rissgroessen
```

Die Kraft, die der Beton beim Reissen abgibt.

Alles in SI-Basis; `h` und `b` in m, `f_ctm` in Pa, Rueckgabe in N.

### zulaessige_stahlspannung

```python
def zulaessige_stahlspannung(*, anforderung: Rissanforderung, f_yk: float, E_s: float, f_ctm: float, durchmesser: float) -> float
```

Die Spannung, bis zu der die Bewehrung beansprucht werden darf.

Bei normaler Anforderung `f_yk`. Sonst zusaetzlich begrenzt durch die
nominelle Rissbreite -- je duenner der Stab, desto mehr darf er tragen,
weil sich der Riss auf mehr Staebe verteilt.

Alles in SI-Basis. Ohne Bewehrung (`durchmesser = 0`) faellt die
Begrenzung weg; die Flaeche ist dann ohnehin null und der Nachweis
scheitert an ihr.

### protokoll_zulaessige_stahlspannung

```python
def protokoll_zulaessige_stahlspannung(p: Protokoll, sigma: Wert, *, anforderung: Rissanforderung, f_yk: Wert, E_s: Wert, f_ctm: Wert, durchmesser: Wert, basis: str) -> None
```

Wie [[opencivil.nachweis.mindestbewehrung#zulaessige_stahlspannung|zulaessige_stahlspannung]] zu ihrer Zahl kommt -- eine
Herleitung fuer jeden Nachweis, der sie braucht.

`sigma` ist das Resultat unter dem Symbol, unter dem es im Nachweis
steht; `durchmesser` der Stab, der die Rissbreite bestimmt. Die Formel
ist dimensionsrein -- (N/mm²)² unter der Wurzel -- und steht darum mit
Einheiten da.

### _protokoll_stahlspannung

```python
def _protokoll_stahlspannung(p: Protokoll, e: Eingaben, werte: Zwischenwerte, erg, *, posten: Sequence[Postenbezug], anforderung: Rissanforderung) -> Wert
```

`sigma_s,adm` einer Lage -- fuer beide Zwängungen dieselbe Herleitung.

Liegen mehrere Posten in der Lage und begrenzt die Rissbreite, steht
zuerst da, welcher Stab der dickste ist: er bestimmt die Rissbreite.
Die Spannung gehoert der ganzen Lage und traegt deren Index, wie
Widerstand und Erfuellungsgrad in der Tabelle.

### Lagenergebnis

```python
@dataclass
class Lagenergebnis(Fallausgang)
```

Was der Nachweis fuer eine Lage gefunden hat: N_s,adm gegen N_Riss.

- `lage: Bewehrungslage`
- `a_s: float = 0.0`
- `durchmesser: float = 0.0` – Der groesste Stabdurchmesser der Lage, in m -- er bestimmt die Rissbreite.
- `sigma_s_adm: float = 0.0`
- `N_s_adm: float = 0.0`
- `ausgang: Ausgang = NICHT_FUEHRBAR`
- `begruendung: str = ''`

### Rissnormalkraft

```python
class Rissnormalkraft(Lagennachweis)
```

Zwängung auf Normalkraft: die Rissbreite bei Zwang, beim Erreichen von
`f_ct,eff` ([[opencivil.nachweis.lagennachweis#Lagennachweis|Lagennachweis]]).

Ein Urteil je Lage der Tragrichtung: die untere und die obere müssen beide
die Risskraft aufnehmen können -- ein Zwang kennt keine Zugseite, er
beansprucht den Querschnitt über die ganze Höhe. In der Zusammenfassung
steht die ungünstigere der beiden; die Urteile sind als Teile derselben
Frage gestempelt (siehe `Nachweis.teilurteile`).

- `THEMA = 'Zwängung auf Normalkraft'`
- `ART = 'N_Riss'`
- `LANGNAME = 'Risse: Zwängung Normalkraft'`
- `KUERZEL = 'NR'`
- `BENENNUNG = 'Rissnormalkraft'`
- `REFERENZ = REFERENZ_RISSBREITE`
- `NUR_MIT_STAHL = False`

#### Rissnormalkraft.ansatz

```python
def ansatz(self, e: Eingaben, p: Protokoll) -> Rissgroessen
```

Die Risskraft der gezogenen Querschnittshälfte -- und ihre Herleitung.

#### Rissnormalkraft.eine_lage

```python
def eine_lage(self, e: Eingaben, lage: Bewehrungslage, ansatz: Rissgroessen) -> Lagenergebnis
```

#### Rissnormalkraft._n_riss

```python
def _n_riss(self, groessen: Rissgroessen) -> Wert
```

Die Risskraft -- die Einwirkung in Tabelle und Herleitung.

#### Rissnormalkraft._n_s_adm

```python
def _n_s_adm(self, erg: Lagenergebnis) -> Wert
```

Was die Lage aufnimmt -- der Widerstand in Tabelle und Herleitung.

#### Rissnormalkraft.protokoll_lage

```python
def protokoll_lage(self, p: Protokoll, e: Eingaben, erg: Lagenergebnis, ansatz: Rissgroessen) -> None
```

### Momentlagenergebnis

```python
@dataclass
class Momentlagenergebnis(Fallausgang)
```

Was der Nachweis gegen das Rissmoment fuer eine Lage gefunden hat.

- `lage: Bewehrungslage`
- `a_s: float = 0.0`
- `z_s: float = 0.0` – Gemeinsamer Schwerpunkt der Lage ab Oberkante, in m.
- `d: float = 0.0` – Statische Hoehe ab der gedrueckten Randfaser, in m.
- `durchmesser: float = 0.0`
- `sigma_s_adm: float = 0.0`
- `n: float = 0.0`
- `rho: float = 0.0` – `n * A_s / b`, die Hilfsgroesse der Nulllinie, in m.
- `x: float = 0.0`
- `hebelarm: float = 0.0`
- `M_s_adm: float = 0.0`
- `ausgang: Ausgang = NICHT_FUEHRBAR` – M_s,adm gegen M_Riss -- nicht fuehrbar ohne Bewehrung in der Lage.
- `begruendung: str = ''`

### Biegezwang

```python
class Biegezwang(Nachweis)
```

Was die Zwaengung auf Biegung an der Platte ([[opencivil.nachweis.mindestbewehrung#ZwaengungBiegung|ZwaengungBiegung]])
und am gezeichneten Querschnitt
([[opencivil.nachweis.qa_gebrauch#ZwaengungBiegungQA|ZwaengungBiegungQA]]) teilt: Name,
Thema, Normstelle und den ersten Satz der Herleitung.

Mehr teilen sie nicht. Die Platte rechnet je Lage von Hand, mit dem
Hebelarm `d - x/3`; der gezeichnete Querschnitt sucht je Zugseite das
Moment, bei dem der erste gezogene Stab seine Grenze erreicht. Gleich ist
nur der Vergleich `M_s,adm >= M_Riss` -- ein gemeinsamer Nachweis haette
fast nur weitergereicht (Benutzer, 2026-10-17).

- `THEMA = 'Zwängung auf Biegung'`
- `LANGNAME = 'Risse: Zwängung Biegung'`
- `REFERENZ = REFERENZ_RISSBREITE`
- `ART = 'ZB'`
- `EINLEITUNG = 'Eine aufgezwungene Krümmung erzeugt beim Reissen ein Moment, das die…` – Der erste Satz der Herleitung.

### ZwaengungBiegung

```python
class ZwaengungBiegung(Biegezwang, Lagennachweis)
```

Zwängung auf Biegung, je gewählter Lage.

Zwei Urteile: die untere Lage (positives Moment) und die obere (negatives).
Beim Reissen gibt der Beton sein Moment ab; die Bewehrung muss es
übernehmen können, ohne über `sigma_s,adm` zu kommen.

Der aufnehmbare Moment wird am **gerissenen** Querschnitt bestimmt --
unmittelbar nach dem Riss ist der Querschnitt genau dort, und die
Spannungen sind Gebrauchsspannungen, also elastisch. Eine plastische
Druckzone gibt es in diesem Augenblick nicht.

- `KUERZEL = 'ZB'`
- `BENENNUNG = Biegezwang.THEMA`

#### ZwaengungBiegung.ansatz

```python
def ansatz(self, e: Eingaben, p: Protokoll) -> Wert
```

Das Rissmoment des Rechtecks -- und seine Herleitung.

#### ZwaengungBiegung.eine_lage

```python
def eine_lage(self, e: Eingaben, lage: Bewehrungslage, ansatz: Wert) -> Momentlagenergebnis
```

#### ZwaengungBiegung._m_s_adm

```python
def _m_s_adm(self, erg: Momentlagenergebnis) -> Wert
```

Was die Lage aufnimmt -- der Widerstand in Tabelle und Herleitung.

#### ZwaengungBiegung.protokoll_lage

```python
def protokoll_lage(self, p: Protokoll, e: Eingaben, erg: Momentlagenergebnis, ansatz: Wert) -> None
```

### _erster_E_s

```python
def _erster_E_s(e: Eingaben, lagen: Sequence[Bewehrungslage]) -> Optional[Wert]
```

Der Elastizitaetsmodul fuer die Wertigkeit im Ansatz.

Im Ansatz steht n einmal; je Lage wird es mit dem Stahl dieser Lage
gerechnet. Bei einer Platte mit zwei Sorten weichen die Zahlen dann ab --
massgebend ist, was in der Lagenrechnung steht. `None`, wenn keine der
Lagen einen Stahl traegt.


## Konstanten

- `REFERENZ_RISSBREITE = 'SIA 262:2025, 4.4.2.3.4, Tabelle 17'` – Die Begrenzung der Rissbreite: bei Zwang beim Erreichen von f_ct,eff und unter quasi-staendiger Last -- dieselbe Zeile der Tabelle.
- `REFERENZ_TABELLE = 'SIA 262:2025, Tabelle 17'` – Die Grenzen der Tabelle: die zulaessige Stahlspannung bei normaler Anforderung und die Bedingung sigma_s \<= sigma_s,adm. Sonst gilt die Wurzelformel mit w_nom nach der Tabelle.
- `REFERENZ_WURZELFORMEL = 'SIA 262:2025, 4.4.2.3.4, (102); Tabelle 17'`
- `REFERENZ_DICKE = 'SIA 262:2025, 4.4.1.3'` – Die rissaktive Dicke unter Zug, ohne und mit der Begrenzung massiger Bauteile.
- `REFERENZ_RANDZONE = 'SIA 262:2025, 4.4.2.3.7'`
- `EINLEITUNG_NORMALKRAFT = 'Eine aufgezwungene oder behinderte Verkürzung zieht den Querschnitt,…` – Der erste Satz der Zwaengung auf Normalkraft -- an der Platte wie am gezeichneten Querschnitt.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.nachweis]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.nachweis.lagennachweis]]
- [[opencivil.nachweis.rissanforderung]]
- [[opencivil.nachweis.rissgroessen]]
- [[opencivil.nachweis.zustand2]]
- [[opencivil.querschnitt.gesetzwahl]]
- [[opencivil.querschnitt.lagenaufbau]]
- [[opencivil.querschnitt.platte]]

## Gebraucht von

- [[opencivil.nachweis.qa_gebrauch]]
- [[opencivil.nachweis.spannungsbegrenzung]]
- [[opencivil.nachweis.spannungsgrenzen]]
- [[opencivil.nachweis.stabgrenzen]]
- [[opencivil.projekt.aufbau.platte]]

## Formeln aus diesem Modul

- [[Aufnehmbare Risskraft]] · `Rissnormalkraft.protokoll_lage`
- [[Aufnehmbares Moment der Bewehrung]] · `ZwaengungBiegung.protokoll_lage`
- [[Dickster Stab der Lage]] · `_protokoll_stahlspannung`
- [[Hilfsgrösse der Nulllinie]] · `ZwaengungBiegung.protokoll_lage`
- [[Innerer Hebelarm]] · `ZwaengungBiegung.protokoll_lage`
- [[Nulllinie des gerissenen Querschnitts]] · `ZwaengungBiegung.protokoll_lage`
- [[Rissaktive Plattendicke]] · `Rissnormalkraft._protokoll_ansatz`
- [[Risskraft der gezogenen Querschnittshälfte]] · `Rissnormalkraft._protokoll_ansatz`
- [[Wertigkeit im gerissenen Zustand]] · `ZwaengungBiegung._protokoll_ansatz`
- [[Zulässige Stahlspannung (normale Anforderung)]] · `protokoll_zulaessige_stahlspannung`
- [[Zulässige Stahlspannung (Rissbreite w_nom)]] · `protokoll_zulaessige_stahlspannung`
