---
erzeugt: 6495c643db77
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/dehnungsfaecher.py
> Die zulaessigen Dehnungsebenen einer Platte.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/dehnungsfaecher.py)

## VERANTWORTUNG

Wo die Dehnungsebene einer Platte im Bruchzustand liegen darf, an einer
Stelle -- auf zwei Arten geschrieben, fuer zwei Nutzer:

* [[opencivil.nachweis.dehnungsfaecher#faecher|faecher]] faehrt den Rand ab, Ebene fuer Ebene. Daraus baut
  [[opencivil.nachweis.resistenzlinie#Ebenenlinie|Ebenenlinie]] die genaue
  M-N-Resistenzlinie.
* [[opencivil.nachweis.dehnungsfaecher#grenzen|grenzen]] schreibt dieselben Grenzen als Bedingungen an einzelne
  Stellen. Damit endet jede Linie der Spannung-Dehnung-Analyse am selben
  Rand, und die Resistenzlinie sagt, welche Grenze ihren Bruchzustand
  bestimmt.


## WIE DER FAECHER ENTSTEHT

Welche Grenze den Faecher begrenzt, wechselt unterwegs dreimal --
entsprechend wird er in drei Abschnitten je Momentenvorzeichen abgefahren:

```
1a  Drehung um die unterste Lage bei eps_ud; die Oberkante geht von Zug
    bis auf -eps_c2d. Massgebend ist der Stahl.
1b  Drehung um die Oberkante bei -eps_c2d; die Unterkante geht bis auf
    null. Massgebend ist die gedrueckte Randfaser.
1c  Drehung um den Punkt C; die Unterkante geht bis auf -eps_c1d.
    Der Querschnitt ist ganz gedrueckt, massgebend ist eps_c1d.
2a/2b/2c  dasselbe spiegelbildlich mit Zug oben     (M < 0)
```

Der Punkt C liegt bei z_C = h * (1 - eps_c1d / eps_c2d) ab dem gedrueckten Rand
und traegt die Dehnung -eps_c1d. Er ist noetig, weil beim vollstaendig
gedrueckten Querschnitt nicht mehr die Randfaser massgebend ist: reiner Druck
endet bei gleichmaessig -eps_c1d, nicht bei -eps_c2d. Ohne diesen Abschnitt
liefe die Linie an beiden Enden ueber die wahre Grenze hinaus und schnitte sich
selbst -- womit Punkt-in-Linie-Test und Schnittsuche unbrauchbar waeren.

Anfang (gleichmaessiger Zug bei eps_ud) und Ende (gleichmaessiger Druck bei
eps_c1d) sind beiden Faechern gemeinsam, sodass sich eine geschlossene Linie
ergibt.


## DIE GRENZEN SIND EXPLIZIT

`eps_c1d` und `eps_c2d` gibt der Aufrufer mit, `eps_ud` steht je Lage
dabei. Frueher las der Faecher sie aus dem Betongesetz -- ein Gesetz, das sie
nicht hat, etwa der Spannungsblock, haette keinen Faecher bekommen.


## VORZEICHEN

```
N > 0   Zug
M > 0   Zug an der Unterseite (Feldmoment)
```
`z` von der Oberkante nach unten.

## Inhalt

### Linienpunkt

```python
@dataclass(frozen=True)
class Linienpunkt
```

Ein Punkt der Resistenzlinie samt der Dehnungsebene, die ihn erzeugt.

- `N: float` – Normalkraft in N (Zug positiv).
- `M: float` – Moment in Nm (Zug unten positiv).
- `eps_oben: float`
- `eps_unten: float`
- `abschnitt: str = ''`

### faecher

```python
def faecher(h: float, staebe: Sequence[Tuple[float, float]], schritte: int, *, eps_c1d: float, eps_c2d: float) -> List[Tuple[str, Dehnungsebene]]
```

Die Folge der Dehnungsebenen auf dem Rand -- die eigentliche Prozedur.

`staebe` sind `(z, eps_ud)` je Lage. Beide Faecher laufen von
gleichmaessigem Zug bis zu gleichmaessigem Druck; zusammengesetzt ergeben
sie die geschlossene Resistenzlinie.

### grenzen

```python
def grenzen(h: float, staebe: Sequence[Tuple[float, float, str]], *, eps_c1d: float, eps_c2d: float) -> Tuple[List[Dehnungsgrenze], Tuple[str, ...]]
```

Dieselben Grenzen als Bedingungen an einzelne Stellen, samt Namen.

`staebe` sind `(z, eps_ud, Name)` je Lage. Der Beton an beiden
Raendern bis `-eps_c2d`; im Punkt C, im Abstand
`h·(1 - eps_c1d/eps_c2d)` vom gedrueckten Rand, bis `-eps_c1d` -- das
zaehlt erst, wenn der ganze Querschnitt gedrueckt ist, und so ist die
Bedingung auch gebaut: solange ein Rand nicht gedrueckt ist, haelt sie
von selbst; jede Stahllage bis `±eps_ud`. Der Arm gilt ab der halben
Hoehe, wie in [[opencivil.querschnitt.fasern]].


## Konstanten

- `SCHRITTE = 80` – Schritte je Faecherabschnitt. Die Linie nahe dem reinen Druck laeuft schnell und waere mit weniger sichtbar eckig. Die Zahlen im Bericht haengen nicht daran: die Resistenzlinie sucht jeden Widerstand zwischen zwei Schritten genau.
- `SCHRITTE_SUCHE = 20` – Schritte fuer die Bewehrungssuche, die kein Diagramm zeichnet. Ihre Zahlen sind dieselben (auf 1e-9): die Linie sucht jeden Widerstand und jede Spitze zwischen zwei Schritten genau, der Faecher grenzt nur ein. Ein Viertel der Ebenen, ein Viertel der Zeit.
- `FASERN = 200` – Fasern ueber die Hoehe fuer die Betonintegration.

## Braucht

- [[opencivil.querschnitt.fasern]]
- [[opencivil.querschnitt.werkstoffgesetz]]

## Gebraucht von

- [[opencivil.nachweis.biegung_normalkraft]]
- [[opencivil.nachweis.knicken]]
- [[opencivil.nachweis.resistenzlinie]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.spannungsanalyse]]
