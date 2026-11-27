---
erzeugt: 267d78d24b81
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/erdbeben.py
> ein Gebaeude im Erdbeben, wie die Oberflaeche es beschreibt.
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/erdbeben.py)

## VERANTWORTUNG

Der [[opencivil.projekt.erdbeben#ErdbebenEintrag|ErdbebenEintrag]]: Standort und Bauwerksklasse, die
Verhaltensbeiwerte je Richtung, woher die Grundschwingzeit kommt, ob Grund-
und Aufriss regelmaessig sind – dazu die Geschosse
([[opencivil.projekt.erdbeben#GeschossEintrag|GeschossEintrag]], von unten), jedes mit seinem Kern: einer
Querschnittsanalyse des Projekts mit allen Waenden in x und in y (Benutzer,
2026-11-27). Gerechnet wird in [[opencivil.erdbeben.ersatzkraft]].

Die Vorgaben der Felder sind gesetzt, damit sich gleich etwas rechnen
laesst, und stehen in keiner Quelle: Zone Z1b, Baugrundklasse C,
Bauwerksklasse I, q = 1.5 – der kleinste Wert fuer Stahlbeton ohne
Duktilitaet (SIA 262:2025, Tabelle 14) –, Grund- und Aufriss regelmaessig,
ein Geschoss von 3 m ohne Last und ohne Kern. Ohne Last rechnet ein neues
Gebaeude nichts, wie ein neuer Lastfall. psi_2 = 0.3 gilt fuer Wohn- und
Bueroflaechen (SIA 260:2013, Anhang A, Tabelle 2), eta_EI = 0.5 ist nach
Vorgabe, nicht nachgeschlagen.

## Inhalt

### GeschossEintrag

```python
@dataclass
class GeschossEintrag(Beschreibung)
```

Ein Geschoss ueber der Einspannung, von unten gezaehlt: Hoehe, Lasten und sein Kern.

- `IM_ORT = 'Geschoss'`
- `name: str`
- `h: float = bereich(3.0, heisst='Höhe h', einheit=M, ueber=0.0)` – Hoehe des Geschosses in m, von Decke zu Decke – das unterste ab der Einspannung.
- `G_k: float = bereich(0.0, heisst='Ständige Last G_k', einheit=KN, ab=0.0)` – Die staendige Last, die mit der Decke des Geschosses schwingt, in kN.
- `Q_k: float = bereich(0.0, heisst='Nutzlast Q_k', einheit=KN, ab=0.0)` – Die Nutzlast des Geschosses in kN.
- `psi_2: float = bereich(0.3, heisst='ψ₂', ab=0.0, bis=1.0)` – Der Beiwert fuer den quasi-staendigen Anteil der Nutzlast.
- `kern: str = ''` – Die Kennung der Querschnittsanalyse seines Kerns – leer, solange keine gewaehlt ist. Sie zeigt alle Waende in x und in y, wie im Grundriss: y der Analyse liegt in x des Gebaeudes.
- `eta_EI: float = bereich(0.5, heisst='η_EI', ueber=0.0, bis=1.0)` – Der Anteil der ungerissenen Biegesteifigkeit seines Kerns, der gilt.

### ErdbebenEintrag

```python
@dataclass
class ErdbebenEintrag(BauteilEintrag)
```

Ein Gebaeude im Erdbeben, nach dem Ersatzkraftverfahren (SIA 261:2020, 16.5.2).

- `BEZEICHNUNG = 'Erdbeben'`
- `STAMM = 'Gebäude'`
- `kennung: str`
- `name: str`
- `zone: Erdbebenzone = Erdbebenzone.Z1B`
- `baugrund: Baugrundklasse = Baugrundklasse.C`
- `bauwerksklasse: Bauwerksklasse = Bauwerksklasse.I`
- `q_x: float = bereich(1.5, heisst='Verhaltensbeiwert q_x', ab=1.0)`
- `q_y: float = bereich(1.5, heisst='Verhaltensbeiwert q_y', ab=1.0)`
- `schwingzeit: Schwingzeit = Schwingzeit.KERN` – Aus dem Kern (40) oder von Hand.
- `T1_x: float = bereich(0.5, heisst='Grundschwingzeit T₁ in x', einheit=S, ueber=0.0)`
- `T1_y: float = bereich(0.5, heisst='Grundschwingzeit T₁ in y', einheit=S, ueber=0.0)` – Nur von Hand: die Grundschwingzeiten in s.
- `grundriss_regelmaessig: bool = True` – Ob der Grundriss die Kriterien von 16.5.1.3 erfuellt – das sagt der Benutzer.
- `aufriss_regelmaessig: bool = True` – Ob der Aufriss die Kriterien von 16.5.1.4 erfuellt; das Gewicht prueft der Kern dazu.
- `beschreibung: str = ''` – Freier Text – geht in keine Rechnung ein.
- `geschosse: List[GeschossEintrag] = field(default_factory=list)` – Von unten nach oben, ab der Einspannung.

#### ErdbebenEintrag.neu

```python
@classmethod
def neu(cls, kennung: str, name: str) -> 'ErdbebenEintrag'
```

Ein frisches Gebaeude, wie die Oberflaeche es anlegt: ein Geschoss ohne Kern.

#### ErdbebenEintrag.bezuege

```python
def bezuege(self) -> List[str]
```

Die Querschnittsanalysen, die ein Geschoss als Kern nimmt.

#### ErdbebenEintrag.geschoss

```python
def geschoss(self, name: str, *, h: float, G_k: float, Q_k: float=0.0, psi_2: float=0.3, kern: str='', eta_EI: float=0.5) -> GeschossEintrag
```

Ein Geschoss oben anfuegen – h in m, Lasten in kN, `kern` die
Kennung einer Querschnittsanalyse.


## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.erdbeben.ersatzkraft]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.lesen]]

## Gebraucht von

- [[opencivil.projekt]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.aufbau.erdbeben]]
- [[opencivil.projekt.projekt]]
- [[opencivil.web.api]]
