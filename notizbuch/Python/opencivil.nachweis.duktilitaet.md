---
erzeugt: 15e609e0656a
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/duktilitaet.py
> Duktilitaetsnachweis ueber die Druckzonenhoehe.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/duktilitaet.py)

## VERANTWORTUNG

Prueft je Bewehrungslage, ob die Druckzone schlank genug bleibt:

```
0.85 * x * b * f_cd = A_s * f_sd        (Kraeftegleichgewicht, M_Ed = 0)
x / d <= (x/d)_max                      (Vorgabe 0.35, hoechstens 0.5)
```

Eine flache Druckzone heisst: der Stahl fliesst lange, bevor der Beton
versagt. Der Querschnitt kuendigt sein Versagen an, statt ploetzlich zu
brechen -- darum wird hier keine Tragfaehigkeit nachgewiesen, sondern ein
Verhaeltnis.


## JE LAGE, EIN URTEIL JE LAGE

Anders als M-N und Querkraft gilt dieser Nachweis fuer eine einzelne
Bewehrungslage. Gerechnet werden die beiden Lagen der Tragrichtung -- die
untere traegt das Feld-, die obere das Stuetzmoment. In der Zusammenfassung
steht die unguenstigere: geht die auf, gehen beide auf. Die Urteile sind
dafuer als Teile derselben Frage gestempelt (siehe
[[opencivil.core.berechnung#Nachweis.teilurteile|teilurteile]]); gezaehlt werden
trotzdem beide, denn die Bewehrungssuche misst ihren Fortschritt an der Summe
der Rueckstaende.

Eine unbewehrte Lage ist kein Fehler der Beschreibung: sie bekommt ein Urteil
mit Hinweis statt einer Zahl -- und ist damit die unguenstigere, steht also
auch in der Tabelle.


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

Vorgabe ist 0.35. Sie laesst sich je Platte setzen, hoechstens auf 0.5
(`QuerschnittEintrag.x_d_max`). Weicht sie von der Vorgabe ab, sagt das die
Herleitung -- eine andere Grenze ist eine Annahme, die man im Bericht finden
muss.

## Inhalt

### Lagenergebnis

```python
@dataclass
class Lagenergebnis
```

Was der Nachweis fuer eine Lage gefunden hat.

- `lage: Bewehrungslage`
- `a_s: float = 0.0` – Summe der Bewehrungsquerschnitte dieser Lage, in m^2.
- `z: float = 0.0` – Gemeinsamer Schwerpunkt ab Oberkante, in m.
- `d: float = 0.0` – Statische Hoehe ab der gedrueckten Randfaser, in m.
- `f_sd: float = 0.0` – Stahlspannung im Gleichgewicht -- die fliessende Bewehrung, in Pa.
- `x: float = 0.0` – Druckzonenhoehe bei M_Ed = 0, in m.
- `verhaeltnis: float = 0.0`
- `erfuellungsgrad: float = 0.0`
- `erfuellt: bool = False`
- `begruendung: str = ''`
- `hinweis: str = ''`

#### Lagenergebnis.machbar

```python
@property
def machbar(self) -> bool
```

### druckzonenhoehe

```python
def druckzonenhoehe(*, a_s: float, f_sd: float, b: float, f_cd: float) -> float
```

`x` aus dem Kraeftegleichgewicht bei reiner Biegung.

`0.85 * x * b * f_cd = A_s * f_sd`, aufgeloest nach `x`. Alles in
SI-Basis; Rueckgabe in m. Dieselbe Formel wie beim Eckpunkt *reine Biegung*
der Handrechnung -- sie steht dort schon einmal, weil sie dort einen
anderen Zweck hat, aber es ist dieselbe Gleichgewichtsbedingung.

### Duktilitaet

```python
class Duktilitaet(Nachweis)
```

Duktilitaetsnachweis je Bewehrungslage.

Ein Nachweis fuer die ganze Platte, ein Urteil je Lage. Die Lagen einer
Platte gehoeren zusammen und stehen darum unter einer Ueberschrift; sie auf
zwei Nachweise zu verteilen ergaebe zwei fast leere Abschnitte.

Ob er ueberhaupt gefuehrt wird, entscheidet ein einziger Schalter am
Querschnitt; welche Lagen er ansieht, sagt der Aufbau, und wie tief die
Druckzone reichen darf, `grenze`.

- `THEMA = 'Duktilität'`

#### Duktilitaet.pruefe

```python
def pruefe(self, e: Eingaben, p: Protokoll)
```

#### Duktilitaet._grenze

```python
def _grenze(self, nummer: int) -> Wert
```

Die zulaessige bezogene Druckzonenhoehe -- Widerstand und Herleitung.

#### Duktilitaet._protokoll_lage

```python
def _protokoll_lage(self, p: Protokoll, e: Eingaben, erg: Lagenergebnis, breite: str) -> None
```

Die Herleitung einer Lage, aus Vorlagen: jede Formel steht einmal mit
Symbolen da, die Fassung mit Zahlen und Einheiten entsteht daraus.


## Konstanten

- `GRENZE = 0.35` – Groesste zulaessige bezogene Druckzonenhoehe -- die Vorgabe.
- `DUKTILITAETSBEDINGUNG = 'Bedingung der Duktilität'` – Die Seite im Notizbuch: die Bedingung der Platte und die des gezeichneten Querschnitts sind dieselbe.
- `HOECHSTENS = 0.5` – So weit laesst sich die Grenze hoechstens anheben.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.material.basis]]
- [[opencivil.querschnitt.platte]]
- [[opencivil.querschnitt.werkstoffgesetz]]

## Gebraucht von

- [[opencivil.nachweis.richtungsnachweise]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.platte]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.web.api]]

## Formeln aus diesem Modul

- [[Bedingung der Duktilität]] · `Duktilitaet._protokoll_ansatz`
- [[Bezogene Druckzonenhöhe]] · `Duktilitaet._protokoll_lage`
- [[Druckzonenhöhe bei reiner Biegung]] · `Duktilitaet._protokoll_lage`
- [[Kräftegleichgewicht bei M_Ed = 0]] · `Duktilitaet._protokoll_ansatz`
