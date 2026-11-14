---
erzeugt: 2e8da999c5d2
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/duktilitaet.py
> Duktilitaetsnachweis ueber die Druckzonenhoehe.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/duktilitaet.py)

## VERANTWORTUNG

Prueft je Bewehrungslage, ob die Druckzone schlank genug bleibt:

```
0.85 * x * b * f_cd = A_s * f_yd        (Kraeftegleichgewicht, M_Ed = 0)
x / d <= k * 435 N/mm^2 / f_yd          (k: Vorgabe 0.35, hoechstens 0.5)
```

Eine flache Druckzone heisst: der Stahl fliesst lange, bevor der Beton
versagt, und das Bauteil kann Schnittgroessen umlagern. Haelt die Druckzone
die Grenze ein, darf man nach SIA 262:2025, 4.1.4.2.5 umlagern, ohne das
Verformungsvermoegen nachzurechnen -- darum wird hier keine Tragfaehigkeit
nachgewiesen, sondern ein Verhaeltnis.


## JE LAGE, EIN URTEIL JE LAGE

Anders als M-N und Querkraft gilt dieser Nachweis fuer eine einzelne
Bewehrungslage. Gerechnet werden die beiden Lagen der Tragrichtung -- die
untere traegt das Feld-, die obere das Stuetzmoment. In der Zusammenfassung
steht die unguenstigere: geht die auf, gehen beide auf. Die Urteile sind
dafuer als Teile derselben Frage gestempelt (siehe
[[opencivil.core.nachweis#Nachweis.teilurteile|teilurteile]]); gezaehlt werden
trotzdem beide, denn die Bewehrungssuche misst ihren Fortschritt an der Summe
der Rueckstaende.

Eine Lage ohne Stahl gibt die Platte gar nicht erst mit: sie wird nicht
nachgewiesen (Benutzer, 2026-10-19, [[opencivil.projekt.aufbau.platte]]).
Bekommt der Nachweis eine ausdruecklich mit, steht sie mit Hinweis statt
einer Zahl da.


## STATISCHE HOEHE

`d` wird von der **gedrueckten** Randfaser aus gemessen. Bei den unteren
Lagen (1 und 2) liegt der Zug unten, gedrueckt ist oben: `d = z`. Bei den
oberen Lagen umgekehrt: `d = h - z`. Gerechnet wird mit dem gemeinsamen
Schwerpunkt von Grundbewehrung und Zulage -- sie gehoeren zur selben Lage.


## EINHEITEN

Alles in SI-Basis; `x` und `d` in m, Flaechen in m^2, Festigkeiten in Pa.
Das Verhaeltnis `x/d` ist dimensionslos und wird als Einwirkung gegen die
Grenze `(x/d)_max` gehalten.


## DIE GRENZE

Sie haengt am Stahl der Lage, `k * 435 N/mm^2 / f_yd`: bei B500 ist sie
0.35, bei B700B 0.25. Bis 2026-11-14 stand sie fest auf 0.35, auch bei B700B.
Den Beiwert `k` gibt man je Platte an, hoechstens 0.5
(`QuerschnittEintrag.x_d_max`): darueber raet 4.1.4.2.6 ab. Weicht er von
der Vorgabe ab, sagt das die Herleitung -- ein anderer Beiwert ist eine
Annahme, die man im Bericht finden muss.

Die Ziffer setzt ausserdem einen Stahl der Duktilitaetsklasse B oder C und
Beton bis C50/60 voraus. Sonst ist das Verformungsvermoegen nachzurechnen
(4.1.4.2.6), und das kann dieser Nachweis nicht: die Lage steht als nicht
fuehrbar da, mit dem Grund ([[opencivil.nachweis.duktilitaet#hindernis|hindernis]]).

## Inhalt

### grenze

```python
def grenze(beiwert: float, f_yd: float) -> float
```

Die zulaessige bezogene Druckzonenhoehe `k * 435 N/mm^2 / f_yd`; f_yd in Pa.

### hindernis

```python
def hindernis(staehle: Sequence[Baustoff], f_ck: float) -> str
```

Was an den Baustoffen die Bedingung ausschliesst, als Begruendung --
leer, wenn nichts. Ein Stahl ohne Klasse, ein eigener, schliesst nichts
aus: seine Klasse kennt nur, wer ihn angelegt hat.

### protokoll_bedingung

```python
def protokoll_bedingung(p: Protokoll, beiwert: float) -> None
```

Die Bedingung, was sie voraussetzt, und ein abweichender Beiwert.

### protokoll_grenze

```python
def protokoll_grenze(p: Protokoll, werte: Zwischenwerte, grenzwert: Wert, *, beiwert: float, f_yd: Wert) -> None
```

Die Grenze, hergeleitet -- fuer Platte und gezeichneten Querschnitt dieselbe Zeile.

### Lagenergebnis

```python
@dataclass
class Lagenergebnis(Fallausgang)
```

Was der Nachweis fuer eine Lage gefunden hat.

- `lage: Bewehrungslage`
- `a_s: float = 0.0` – Summe der Bewehrungsquerschnitte dieser Lage, in m^2.
- `z: float = 0.0` – Gemeinsamer Schwerpunkt ab Oberkante, in m.
- `d: float = 0.0` – Statische Hoehe ab der gedrueckten Randfaser, in m.
- `f_yd: float = 0.0` – Fliessgrenze der Lage, in Pa -- die Stahlspannung im Gleichgewicht.
- `x: float = 0.0` – Druckzonenhoehe bei M_Ed = 0, in m.
- `verhaeltnis: float = 0.0`
- `grenze: float = 0.0` – (x/d)_max der Lage -- sie haengt an ihrem Stahl.
- `ausgang: Ausgang = NICHT_FUEHRBAR` – x/d gegen (x/d)_max.
- `begruendung: str = ''`

### druckzonenhoehe

```python
def druckzonenhoehe(*, a_s: float, f_yd: float, b: float, f_cd: float) -> float
```

`x` aus dem Kraeftegleichgewicht bei reiner Biegung.

`0.85 * x * b * f_cd = A_s * f_yd`, aufgeloest nach `x`. Alles in
SI-Basis; Rueckgabe in m. Dieselbe Formel wie beim Eckpunkt *reine Biegung*
der Handrechnung -- sie steht dort schon einmal, weil sie dort einen
anderen Zweck hat, aber es ist dieselbe Gleichgewichtsbedingung.

### Duktilitaet

```python
class Duktilitaet(Lagennachweis)
```

Duktilitaetsnachweis je Bewehrungslage ([[opencivil.nachweis.lagennachweis#Lagennachweis|Lagennachweis]]).

Ein Nachweis fuer die ganze Platte, ein Urteil je Lage. Die Lagen einer
Platte gehoeren zusammen und stehen darum unter einer Ueberschrift; sie auf
zwei Nachweise zu verteilen ergaebe zwei fast leere Abschnitte.

Ob er ueberhaupt gefuehrt wird, entscheidet ein einziger Schalter am
Querschnitt; welche Lagen er ansieht, sagt der Aufbau, und wie tief die
Druckzone reichen darf, der Beiwert `beiwert` mit dem Stahl der Lage.

- `THEMA = 'Duktilität'`
- `ART = 'D'`
- `KUERZEL = 'D'`
- `BENENNUNG = 'Duktilität'`
- `REFERENZ = REFERENZ`

#### Duktilitaet.ansatz

```python
def ansatz(self, e: Eingaben, p: Protokoll) -> float
```

f_cd -- und die Herleitung des Ansatzes.

#### Duktilitaet.eine_lage

```python
def eine_lage(self, e: Eingaben, lage: Bewehrungslage, ansatz: float) -> Lagenergebnis
```

#### Duktilitaet.ausgaben_der_lage

```python
def ausgaben_der_lage(self, erg: Lagenergebnis) -> Dict[str, Groesse]
```

#### Duktilitaet._grenze

```python
def _grenze(self, nummer: int, zahl: float) -> Wert
```

Die zulaessige bezogene Druckzonenhoehe -- Widerstand und Herleitung.

#### Duktilitaet.protokoll_lage

```python
def protokoll_lage(self, p: Protokoll, e: Eingaben, erg: Lagenergebnis, ansatz: float) -> None
```

Die Herleitung einer Lage, aus Vorlagen: jede Formel steht einmal mit
Symbolen da, die Fassung mit Zahlen und Einheiten entsteht daraus.


## Konstanten

- `REFERENZ = 'SIA 262:2025, 4.1.4.2.5'`
- `BEIWERT = 0.35` – Der Beiwert k der Grenze -- die Vorgabe der Ziffer.
- `HOECHSTENS = 0.5` – So weit laesst sich der Beiwert hoechstens anheben: darueber raet SIA 262:2025, 4.1.4.2.6 ab.
- `BEZUG_F_YD = 435000000.0` – Die Fliessgrenze, auf die sich der Beiwert bezieht, in Pa: f_yd von B500, so gerundet, wie die Norm sie in die Grenze schreibt.
- `HOECHSTE_FESTIGKEIT = 50000000.0` – Bis zu dieser Festigkeit f_ck, in Pa, gilt die Grenze: C50/60.
- `DUKTILITAETSBEDINGUNG = 'Bedingung der Duktilität'` – Die Seite im Notizbuch: die Bedingung der Platte und die des gezeichneten Querschnitts sind dieselbe.
- `BEDINGUNG = '\\frac{x}{d} \\le k \\cdot \\frac{435\\,\\mathrm{N/mm^2}}{f_{yd}}'` – Die Bedingung -- fuer beide dieselbe, wie die Zeile ihrer Grenze ([[opencivil.nachweis.duktilitaet#protokoll_grenze|protokoll_grenze]]).

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.nachweis]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.material.basis]]
- [[opencivil.material.betonstahl]]
- [[opencivil.nachweis.lagennachweis]]
- [[opencivil.querschnitt.lagenaufbau]]
- [[opencivil.querschnitt.platte]]
- [[opencivil.querschnitt.werkstoffgesetz]]

## Gebraucht von

- [[opencivil.nachweis.richtungsnachweise]]
- [[opencivil.projekt.aufbau.platte]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.web.api]]

## Formeln aus diesem Modul

- [[Bedingung der Duktilität]] · `protokoll_bedingung`
- [[Bezogene Druckzonenhöhe]] · `Duktilitaet.protokoll_lage`
- [[Druckzonenhöhe aus dem Kräftegleichgewicht]] · `Duktilitaet.protokoll_lage`
- [[Grenze der bezogenen Druckzonenhöhe]] · `protokoll_grenze`
- [[Kräftegleichgewicht bei M_Ed = 0]] · `Duktilitaet._protokoll_ansatz`
