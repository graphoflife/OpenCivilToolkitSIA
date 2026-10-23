---
erzeugt: 9569c8cedda0
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/setzung.py
> eine Setzungsberechnung, wie die Oberflaeche sie beschreibt.
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/setzung.py)

## VERANTWORTUNG

Der [[opencivil.projekt.setzung#SetzungEintrag|SetzungEintrag]]: Lastflaeche, Pressungen aus Wiederbelastung und
Erstbelastung, zulaessige Setzung, die Steifigkeit des Fundaments und die
Schichten des Baugrunds mit Dicke und M_E-Werten -- als speicherbare
Datenklasse. Gerechnet wird in [[opencivil.geotechnik.setzung]].

Die Vorgaben der Felder: B = L = 1 m wie beim Grundbruch; keine Pressung --
eine neue Berechnung bringt keine Einwirkung mit, wie ein neuer Lastfall
(Benutzer, 2026-10-19). Die zulaessige Setzung von 20 mm, die Dicke der
Teilschichten von 0.5 m und die Schicht, mit der eine neue Berechnung
beginnt -- 2 m mit M_E = 20 und M'_E = 60 MN/m² --, sind nicht vom Benutzer,
sondern gesetzt, damit sich gleich etwas rechnen laesst.

Die Namen der Schichten muessen nicht verschieden sein: sie beschriften nur,
die Werte tragen die Nummer der Schicht. Zwei Tonschichten, durch Sand
getrennt, heissen beide «Ton».

## Inhalt

### SchichtEintrag

```python
@dataclass
class SchichtEintrag(Beschreibung)
```

Eine Schicht des Baugrunds, von der Sohle an nach unten: Dicke und M_E-Werte.

- `name: str`
- `d: float = bereich(2.0, heisst='Dicke d', einheit=M, ueber=0.0)` – Dicke der Schicht in m.
- `M_E: float = bereich(20.0, heisst='M_E', einheit=MN_PRO_M2, ueber=0.0)` – M_E-Wert der Erstbelastung in MN/m².
- `M_E_strich: float = bereich(60.0, heisst="M'_E", einheit=MN_PRO_M2, ueber=0.0)` – M_E-Wert der Wiederbelastung, M'_E, in MN/m².

### SetzungEintrag

```python
@dataclass
class SetzungEintrag(Beschreibung)
```

Ein Flachfundament auf geschichtetem Baugrund, mit seinen Pressungen.

- `BEZEICHNUNG = 'Setzung'`
- `kennung: str`
- `name: str`
- `B: float = bereich(1.0, heisst='Breite B', einheit=M, ueber=0.0)` – Breite des Fundaments in m.
- `L: float = bereich(1.0, heisst='Länge L', einheit=M, ueber=0.0)` – Länge des Fundaments in m.
- `steifigkeit: Steifigkeit = Steifigkeit.STARR` – Starr: gerechnet wird im Punkt K; schlaff: unter der Mitte (Kap. 8.10).
- `q_W: float = bereich(0.0, heisst='Pressung aus Wiederbelastung q_W', einheit=KN_PR…` – Der Teil der Pressung in der Sohle, der den Boden nur wieder belastet, in kN/m².
- `q_E: float = bereich(0.0, heisst='Pressung aus Erstbelastung q_E', einheit=KN_PRO_…` – Der Teil, der darüber hinausgeht und den Boden zum ersten Mal belastet, in kN/m².
- `s_zul: float = bereich(20.0, heisst='Zulässige Setzung s_zul', einheit=MM, ueber=0.0)` – Die Setzung, die das Fundament höchstens erfahren darf, in mm.
- `dz: float = bereich(0.5, heisst='Dicke der Teilschichten Δz_max', einheit=M, uebe…` – Wie dick eine Teilschicht höchstens ist, in m -- jede Schicht wird so geteilt.
- `beschreibung: str = ''` – Freier Text -- geht in keine Rechnung ein.
- `schichten: List[SchichtEintrag] = field(default_factory=list)` – Von der Sohle an nach unten; darunter gilt der Baugrund als unzusammendrückbar.

#### SetzungEintrag.neu

```python
@classmethod
def neu(cls, kennung: str, name: str) -> 'SetzungEintrag'
```

Eine frische Berechnung, wie die Oberflaeche sie anlegt: mit einer Schicht.

#### SetzungEintrag.materialien

```python
def materialien(self) -> List[str]
```

Die Materialien, auf die das Fundament zeigt -- keine: der Boden steht im Eintrag.

#### SetzungEintrag.bezuege

```python
def bezuege(self) -> List[str]
```

Die Bauteile, deren Querschnitt das Fundament nimmt -- keine.

#### SetzungEintrag.schicht

```python
def schicht(self, name: str, *, d: float, M_E: float, M_E_strich: float) -> SchichtEintrag
```

Eine Schicht unten anfügen -- Dicke in m, M_E-Werte in MN/m².


## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.geotechnik.setzung]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.lesen]]

## Gebraucht von

- [[opencivil.projekt]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.aufbau.setzung]]
- [[opencivil.projekt.projekt]]
