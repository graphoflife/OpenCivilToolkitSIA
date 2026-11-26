---
erzeugt: f4bd6d5df43f
art: modul
tags: [modul]
---
> [!abstract] opencivil/web/erdbebendaten.py
> was die Oberflaeche von einem Gebaeude im Erdbeben zeichnet.
> Paket [[opencivil.web]] · [Quelltext](../../opencivil/web/erdbebendaten.py)

## VERANTWORTUNG

Je Gebaeude die Zahlen der Ansicht, in den Einheiten der Anzeige -- m, kN
und kNm: Hoehe und Gewicht jedes Geschosses, je Richtung die Kraefte
F_d,i, Querkraft und Moment unter jedem Geschoss und was jede Wand am Fuss
traegt. Dazu je Wand, warum sie nicht rechnet, oder ihr Umriss im
Grundriss, in mm um ihren Schwerpunkt und gedreht nach ihrer Lage; die
Meldungen -- rot, was falsch ist, grau, was fehlt oder hier nicht gerechnet
wird -- und die Legenden unter den Bildern ([[opencivil.web.anzeige]]).
Namen und Hoehen der Geschosse liest die Oberflaeche aus dem Eintrag; was
der Kern daraus macht, kommt von hier.

Gerechnet wird hier nichts, was nicht der Kern schon weiss: Querkraefte und
Momente kommen aus [[opencivil.erdbeben.ersatzkraft#querkraefte|opencivil.erdbeben.ersatzkraft.querkraefte]] und
[[opencivil.erdbeben.ersatzkraft#momente|momente]], wie in der Tabelle der
Herleitung, der Grund einer Wand aus
[[opencivil.projekt.aufbau.erdbeben#wandquerschnitt|opencivil.projekt.aufbau.erdbeben.wandquerschnitt]], wie beim Bauen,
und ihr Umriss aus derselben Zeichnung wie das Bild ihrer Analyse
([[opencivil.web.diagrammdaten#zeichnung|opencivil.web.diagrammdaten.zeichnung]]).

## Inhalt

### ansicht

```python
def ansicht(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Dict[str, Any]
```

Was die Ansicht eines Gebaeudes braucht. Ohne Nachweis -- es fehlt ein
Geschoss, eine Wand oder ihr Querschnitt -- nur, was fehlt.

### _grundriss

```python
def _grundriss(nummer: int, wand: TragwandEintrag, analyse: Any) -> Dict[str, Any]
```

Eine Wand im Grundriss, in mm: die Flaechen ihrer Analyse um deren
Schwerpunkt, gedreht nach ihrer Lage -- x nach rechts, y nach oben.
`nummer` ist ihr Platz in der Liste, ab 1, wie in der Herleitung.

### _verlaufslegende

```python
def _verlaufslegende(grundrisse: List[Optional[dict]], befund: Erdbebenbefund) -> List[list]
```

Was das Bild der Waende, Querkraefte und Momente zeigt -- die Waende mit Namen.

### _richtung

```python
def _richtung(b: Richtungsbefund, z: Sequence[float]) -> Dict[str, Any]
```

Eine Richtung in den Einheiten der Anzeige: Kraefte, Querkraefte und
Momente von unten, die Waende. `z` sind die Hoehen der Decken, m.

### _legende

```python
def _legende(b: Richtungsbefund, nachweis, loesung: Loesung) -> List[list]
```

Je Richtung: T_1 gegen 4 T_C mit dem Urteil (39), dann F_d und M_0 -- mit q und mit q = 1.


## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.nachweis]]
- [[opencivil.core.rechenwerk]]
- [[opencivil.erdbeben.ersatzkraft]]
- [[opencivil.projekt]]
- [[opencivil.projekt.aufbau.erdbeben]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.erdbeben]]
- [[opencivil.web.anzeige]]
- [[opencivil.web.diagrammdaten]]

## Gebraucht von

- [[opencivil.web.zeichendaten]]
