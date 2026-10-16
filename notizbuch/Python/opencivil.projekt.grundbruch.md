---
erzeugt: b4a5e01c5a5d
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
- `N_Ed: float = 1000.0`
- `T_Ed: float = 200.0`
- `aktiv: bool = True` – Ob die Kombination gerechnet wird. Ausgeschaltet bleibt sie stehen.

#### GrundbruchkombinationEintrag.aus_dict

```python
@classmethod
def aus_dict(cls, d: Mapping[str, Any]) -> 'GrundbruchkombinationEintrag'
```

### GrundbruchEintrag

```python
@dataclass
class GrundbruchEintrag(Beschreibung)
```

Ein Flachfundament auf seinem Baugrund, mit seinen Einwirkungen.

- `kennung: str`
- `name: str`
- `phi_k: float = 30.0` – Reibungswinkel, charakteristisch, in Grad.
- `gamma_phi: float = 1.2` – Partialfaktor des Reibungswinkels -- SIA 267:2013, 5.3.2.2.
- `c_k: float = 0.0` – Kohäsion, charakteristisch, in kPa -- mit phi = 0 die undrainierte Scherfestigkeit.
- `gamma_c: float = 1.5` – Partialfaktor der Kohäsion.
- `gamma: float = 21.0` – Raumlast des Bodens in kN/m³.
- `gamma_w: float = 10.0` – Raumlast des Wassers in kN/m³.
- `q_Ed: float = 0.0` – Bemessungslast neben dem Fundament in kPa.
- `b: float = 1.0` – Breite des Fundaments in m -- die kürzere Seite.
- `L: float = 1.0` – Länge des Fundaments in m.
- `t1: float = 0.0` – Tiefe des höchsten möglichen Grundwasserspiegels unter Terrain, in m.
- `t: float = 0.0` – Tiefe der Fundamentsohle unter Terrain, in m.
- `alpha: float = 0.0` – Neigung der Sohle in Grad, positiv gegen T ansteigend (Bild 9.2.15).
- `beta: float = 0.0` – Neigung des Geländes in Grad, positiv vom Fundament weg abfallend.
- `delta_faktor: float = 1.0` – Sohlreibungswinkel im Verhältnis zum Reibungswinkel, delta*/phi.
- `beschreibung: str = ''` – Freier Text -- geht in keine Rechnung ein.
- `kombinationen: List[GrundbruchkombinationEintrag] = field(default_factory=list)`

#### GrundbruchEintrag.neu

```python
@classmethod
def neu(cls, kennung: str, name: str) -> 'GrundbruchEintrag'
```

Ein frischer Grundbruch, wie die Oberflaeche ihn anlegt: mit einer Kombination.

#### GrundbruchEintrag.kombination

```python
def kombination(self, name: str, *, N_Ed: float, T_Ed: float=0.0) -> GrundbruchkombinationEintrag
```

Eine Kombination anfügen -- N normal zur Sohle, T in ihrer Richtung, in kN.

#### GrundbruchEintrag.pruefen

```python
def pruefen(self) -> None
```

Was beim Oeffnen nicht stimmen kann: Namen der Kombinationen
eindeutig, auch in der Kennung. Die Zahlen prueft erst das Rechnen
([[opencivil.projekt.grundbruch#GrundbruchEintrag.zahlen_pruefen|zahlen_pruefen]]) -- eine abgelegte Datei mit b = 0 soll sich
oeffnen und korrigieren lassen.

#### GrundbruchEintrag.zahlen_pruefen

```python
def zahlen_pruefen(self) -> None
```

Haelt unmoegliche Zahlen auf, bevor daraus ein Widerstand wird.

#### GrundbruchEintrag.aus_dict

```python
@classmethod
def aus_dict(cls, d: Mapping[str, Any]) -> 'GrundbruchEintrag'
```


## Braucht

- [[opencivil.core.wert]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.lesen]]

## Gebraucht von

- [[opencivil.projekt]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.projekt]]
