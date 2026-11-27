---
erzeugt: 0852ec159c81
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/blechdecken.py
> eine Blechverbunddecke, wie die Oberflaeche sie beschreibt.
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/blechdecken.py)

## VERANTWORTUNG

Der [[opencivil.projekt.blechdecken#BlechdeckeEintrag|BlechdeckeEintrag]] einer Querschnittsanalyse
([[opencivil.projekt.querschnittsanalyse#QuerschnittsanalyseEintrag|QuerschnittsanalyseEintrag]]):
ein Streifen Blechverbunddecke an einem Knoten -- ihr Beton und ihr
Profilblech aus Materialien des Projekts, dazu die Masse des Blechs aus
seinem Datenblatt (Plan vom 2026-11-25: einen Katalog der Bleche gibt es
nicht). Was daraus folgt -- die Linie des Blechs, seine Dicke, `d_p` --,
rechnet [[opencivil.querschnitt.profilblech]].


## DER BETON GEHOERT ZUR DECKE (2026-11-27)

Die Decke ist ein Element mit ihrem Beton, nicht ein Blech unter einem
gezeichneten Polygon: so passen Beton und Blech immer zueinander, und eine
andere Rippe aendert beide. Bewehrung zeichnet man in den Beton der Decke
wie in jedes Polygon aus Beton.


## DIE GRENZEN

Die Rippe ist niedriger als die Decke (`h_p < h`), oben nicht breiter als
ihr Abstand und unten schmaler -- sonst stiessen die Rippen unten
aneinander, und der Beton beruehrte sich selbst. Das weisen schon die
Felder ab. Ob die Rippe oben oder unten breiter ist, ist frei: unten
breiter ist das Blech hinterschnitten.


## DIE VORGABEN

Ein Blech mittlerer Groesse, kein Erzeugnis: fuenf Rippen im Abstand von
200 mm, 60 mm hoch, oben 120 mm und unten 70 mm breit, 1100 mm² je Meter,
unter einer Decke von 140 mm.

## Inhalt

### BlechdeckeEintrag

```python
@dataclass
class BlechdeckeEintrag(Beschreibung)
```

Eine Blechverbunddecke an einem Knoten -- siehe Dateikopf.

- `IM_ORT = 'Blechverbunddecke'`
- `kennung: str = ''`
- `knoten: str = ''` – Die Ecke links unten: die Unterkante der Rippen, der linke Rand.
- `beton: str = materialfeld('beton')`
- `blech: str = materialfeld('profilblech')` – Kennung des Profilblechstahls.
- `h: float = bereich(140.0, heisst='Dicke h', zeichen='h', einheit=MM, ueber=0.0)`
- `rippen: int = bereich(5, heisst='Rippen n', zeichen='n', ab=1, bis=RIPPEN_BIS)`
- `h_p: float = bereich(60.0, heisst='Höhe der Rippe h_p', zeichen='h_p', einheit=MM,…`
- `b_s: float = bereich(200.0, heisst='Rippenabstand b_s', zeichen='b_s', einheit=MM,…`
- `b_o: float = bereich(120.0, heisst='Rippe oben b_o', zeichen='b_o', einheit=MM, ue…`
- `b_u: float = bereich(70.0, heisst='Rippe unten b_u', zeichen='b_u', einheit=MM, ue…`
- `A_p: float = bereich(1100.0, heisst='Blech A_p je Meter Breite', zeichen='A_p', ei…` – Die Flaeche des Blechs je Meter Breite, aus dem Datenblatt.

#### BlechdeckeEintrag.form

```python
def form(self, ursprung: Tuple[float, float]) -> Blechform
```

Die Form des Blechs mit der Ecke links unten bei `ursprung`, in mm.


## Konstanten

- `RIPPEN_BIS = 100` – Wie viele Rippen eine Decke hoechstens hat -- 20 m bei 200 mm Abstand; so zeichnet ein Tippfehler keine tausend (nach Vorgabe, nicht nachgeschlagen).

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.lesen]]
- [[opencivil.querschnitt.profilblech]]

## Gebraucht von

- [[opencivil.projekt.aufbau.querschnittsanalyse]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.web.api]]
- [[opencivil.web.dienst]]
- [[opencivil.web.zeichengeometrie]]
