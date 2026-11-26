---
erzeugt: 3a5b77d700b8
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/stabilitaet.py
> ein Fall von Knicken und Kippen, wie die Oberflaeche ihn beschreibt.
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/stabilitaet.py)

## VERANTWORTUNG

Der [[opencivil.projekt.stabilitaet#QAStabilitaetEintrag|QAStabilitaetEintrag]] einer Querschnittsanalyse aus Stahl
([[opencivil.projekt.querschnittsanalyse#QuerschnittsanalyseEintrag|QuerschnittsanalyseEintrag]]):
ein Stab mit dem gezeichneten Querschnitt, seine Druckkraft, die groessten
Momente 1. Ordnung in ihm, je Achse das Verhaeltnis ψ seiner Endmomente und
die Knick- und Kipplaengen. Gerechnet wird in
[[opencivil.stahlbau.stabilitaet]], die Herleitung schreibt
[[opencivil.nachweis.qa_stahl_stabilitaet]].

EINE LAENGE NULL heisst gehalten: um diese Achse knickt der Stab nicht, oder
er kippt nicht. So bleibt jede Laenge eine Zahl, und kein Schalter steht
neben ihr.

ψ gilt fuer `ω` (5.1.9.1) und fuer `η` beim Kippen (Anhang B.6) --
dieselben Endmomente. Mit Querlast oder bei einem verschieblichen Stab
gilt `ω = 1` (5.1.10.3): dann ist ψ eins.

## Inhalt

### _psi

```python
def _psi(achse: str) -> Any
```

Das Verhaeltnis der Endmomente um `achse`: -1 bis 1, Vorgabe 1 -- das konstante Moment.

### _laenge

```python
def _laenge(heisst: str) -> Any
```

Eine Knick- oder Kipplaenge in m, Vorgabe 3 m -- null heisst gehalten.

### QAStabilitaetEintrag

```python
@dataclass
class QAStabilitaetEintrag(Beschreibung)
```

Ein Fall von Knicken und Kippen -- siehe Dateikopf. kN, kNm und m.

- `IM_ORT = 'Stabilitätsnachweis'`
- `name: str`
- `N_Ed: float = bereich(0.0, heisst='Normalkraft N_Ed (Druck negativ)', einheit=KN, b…` – Druck negativ -- Zug traegt der Querschnitt, das prueft die Tragsicherheit.
- `M_y_Ed: float = bereich(0.0, heisst='Moment M_y,Ed', einheit=KNM)` – Das groesste Moment 1. Ordnung um y im Stab; positiv zieht es unten.
- `M_z_Ed: float = bereich(0.0, heisst='Moment M_z,Ed', einheit=KNM)` – Das groesste um z; positiv zieht es links.
- `psi_y: float = _psi('y')`
- `psi_z: float = _psi('z')`
- `L_K_y: float = _laenge('Knicklänge L_K,y')` – Fuer das Knicken um y.
- `L_K_z: float = _laenge('Knicklänge L_K,z')`
- `L_D: float = _laenge('Kipplänge L_D')` – Der Abstand der Punkte, an denen der Druckgurt seitlich gehalten ist.
- `aktiv: bool = True` – Ob der Fall gerechnet wird. Ausgeschaltet bleibt er stehen.

#### QAStabilitaetEintrag.stabfall

```python
def stabfall(self) -> Stabfall
```

Der Fall in SI, aus der Einheit seiner Felder.


## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.lesen]]
- [[opencivil.stahlbau.stabilitaet]]

## Gebraucht von

- [[opencivil.projekt.querschnittsanalyse]]
