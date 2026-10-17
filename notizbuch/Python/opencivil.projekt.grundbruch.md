---
erzeugt: d7dcd1280db0
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/grundbruch.py
> ein Grundbruchnachweis, wie die Oberflaeche ihn beschreibt.
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/grundbruch.py)

## VERANTWORTUNG

Der [[opencivil.projekt.grundbruch#GrundbruchEintrag|GrundbruchEintrag]]: Boden, Fundament, Gelaende und Grundwasser
als Zahlen, dazu die Einwirkungskombinationen -- als speicherbare
Datenklasse. Gerechnet wird in [[opencivil.geotechnik.grundbruch]].

Die Vorgaben der Felder hat der Benutzer genannt (2026-10-16): phi_k = 30°,
gamma_phi = 1.2, c = 0, gamma_c = 1.5, gamma = 21 und gamma_w = 10 kN/m³,
b = L = 1 m, t = t_1 = 0, N_Ed = 1000 kN, T_Ed = 200 kN, alpha = beta = 0.
delta*/phi = 1 ist dazugekommen, damit sich T_Rd rechnen laesst: das Kapitel
nennt fuer delta* «2/3 phi bis 1 · phi».

## Inhalt

### GrundbruchkombinationEintrag

```python
@dataclass
class GrundbruchkombinationEintrag(Beschreibung)
```

Eine Einwirkung auf das Fundament: N normal zur Sohle, T in ihrer Richtung, in kN.

- `name: str`
- `N_Ed: float = bereich(1000.0, heisst='Druckkraft N_Ed', einheit=KN, ueber=0.0)`
- `T_Ed: float = bereich(200.0, heisst='T_Ed, in Richtung von Bild 9.2.15,', einheit=K…`
- `aktiv: bool = True` – Ob die Kombination gerechnet wird. Ausgeschaltet bleibt sie stehen.

### GrundbruchEintrag

```python
@dataclass
class GrundbruchEintrag(Beschreibung)
```

Ein Flachfundament auf seinem Baugrund, mit seinen Einwirkungen.

- `BEZEICHNUNG = 'Grundbruch'`
- `kennung: str`
- `name: str`
- `phi_k: float = bereich(30.0, heisst='φ_k', einheit=GRAD, ab=0.0, unter=90.0)` – Reibungswinkel, charakteristisch, in Grad.
- `gamma_phi: float = bereich(1.2, heisst='Partialfaktor γ_φ', ueber=0.0)` – Partialfaktor des Reibungswinkels -- SIA 267:2013, 5.3.2.2.
- `c_k: float = bereich(0.0, heisst='Kohäsion c', einheit=KPA, ab=0.0)` – Kohäsion, charakteristisch, in kPa -- mit phi = 0 die undrainierte Scherfestigkeit.
- `gamma_c: float = bereich(1.5, heisst='Partialfaktor γ_c', ueber=0.0)` – Partialfaktor der Kohäsion.
- `gamma: float = bereich(21.0, heisst='Raumlast γ', einheit=KN_PRO_M3, ueber=0.0)` – Raumlast des Bodens in kN/m³.
- `gamma_w: float = bereich(10.0, heisst='γ_w', einheit=KN_PRO_M3, ab=0.0)` – Raumlast des Wassers in kN/m³.
- `q_Ed: float = bereich(0.0, heisst='Auflast q_Ed', einheit=KPA, ab=0.0)` – Bemessungslast neben dem Fundament in kPa.
- `b: float = bereich(1.0, heisst='Breite b', einheit=M, ueber=0.0)` – Breite des Fundaments in m -- die kürzere Seite.
- `L: float = bereich(1.0, heisst='Länge L', einheit=M, ueber=0.0)` – Länge des Fundaments in m.
- `t1: float = bereich(0.0, heisst='Tiefe t_1', einheit=M, ab=0.0)` – Tiefe des höchsten möglichen Grundwasserspiegels unter Terrain, in m.
- `t: float = bereich(0.0, heisst='Tiefe t', einheit=M, ab=0.0)` – Tiefe der Fundamentsohle unter Terrain, in m.
- `alpha: float = bereich(0.0, heisst='α', einheit=GRAD, ab=0.0, unter=90.0)` – Neigung der Sohle in Grad, positiv gegen T ansteigend (Bild 9.2.15).
- `beta: float = bereich(0.0, heisst='β', einheit=GRAD, ab=0.0, unter=90.0)` – Neigung des Geländes in Grad, positiv vom Fundament weg abfallend.
- `delta_faktor: float = bereich(1.0, heisst='δ*/φ', ueber=0.0)` – Sohlreibungswinkel im Verhältnis zum Reibungswinkel, delta*/phi.
- `beschreibung: str = ''` – Freier Text -- geht in keine Rechnung ein.
- `kombinationen: List[GrundbruchkombinationEintrag] = field(default_factory=list)`

#### GrundbruchEintrag.neu

```python
@classmethod
def neu(cls, kennung: str, name: str) -> 'GrundbruchEintrag'
```

Ein frischer Grundbruch, wie die Oberflaeche ihn anlegt: mit einer Kombination.

#### GrundbruchEintrag.materialien

```python
def materialien(self) -> List[str]
```

Die Materialien, auf die das Fundament zeigt -- keine: der Boden steht im Eintrag.

#### GrundbruchEintrag.bezuege

```python
def bezuege(self) -> List[str]
```

Die Bauteile, deren Querschnitt das Fundament nimmt -- keine.

#### GrundbruchEintrag.kombination

```python
def kombination(self, name: str, *, N_Ed: float, T_Ed: float=0.0) -> GrundbruchkombinationEintrag
```

Eine Kombination anfügen -- N normal zur Sohle, T in ihrer Richtung, in kN.

#### GrundbruchEintrag.regeln

```python
def regeln(self, wo: str) -> None
```

Haelt unmoegliche Zahlen und Namen auf, bevor daraus ein Widerstand
wird -- was mehrere Felder zusammen betrifft; wo jede Zahl fuer sich
liegt, steht an ihrem Feld. Vor dem Rechnen und nicht beim Oeffnen:
eine abgelegte Datei mit b = 0 oder zwei gleich benannten
Kombinationen soll sich oeffnen und korrigieren lassen.


## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.lesen]]

## Gebraucht von

- [[opencivil.projekt]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.aufbau.grundbruch]]
- [[opencivil.projekt.projekt]]
