---
erzeugt: b074893574b3
art: modul
tags: [modul]
---
> [!abstract] opencivil/web/erdbebendaten.py
> was die Oberflaeche von einem Gebaeude im Erdbeben zeichnet.
> Paket [[opencivil.web]] · [Quelltext](../../opencivil/web/erdbebendaten.py)

## VERANTWORTUNG

Je Gebaeude die Zahlen der Ansicht, in den Einheiten der Anzeige -- m, kN
und kNm: Hoehe und Gewicht jedes Geschosses, je Richtung die Kraefte
F_d,i, die Querkraft unter jedem Geschoss und was jede Wand am Fuss
traegt. Dazu je Wand, warum sie nicht rechnet, die Meldungen -- rot, was
falsch ist, grau, was fehlt oder hier nicht gerechnet wird -- und die
Legende unter dem Bild ([[opencivil.web.anzeige]]). Namen und Hoehen der
Geschosse liest die Oberflaeche aus dem Eintrag; was der Kern daraus
macht, kommt von hier.

Gerechnet wird hier nichts, was nicht der Kern schon weiss: die Querkraefte
kommen aus [[opencivil.erdbeben.ersatzkraft#querkraefte|opencivil.erdbeben.ersatzkraft.querkraefte]], wie in der
Tabelle der Herleitung, und der Grund einer Wand aus
[[opencivil.projekt.aufbau.erdbeben#wandquerschnitt|opencivil.projekt.aufbau.erdbeben.wandquerschnitt]], wie beim Bauen.

## Inhalt

### ansicht

```python
def ansicht(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Dict[str, Any]
```

Was die Ansicht eines Gebaeudes braucht. Ohne Nachweis -- es fehlt ein
Geschoss, eine Wand oder ihr Querschnitt -- nur, was fehlt.

### _richtung

```python
def _richtung(b: Richtungsbefund) -> Dict[str, Any]
```

Eine Richtung in den Einheiten der Anzeige: Kraefte und Querkraefte von unten, die Waende.

### _legende

```python
def _legende(b: Richtungsbefund, nachweis, loesung: Loesung) -> List[list]
```

Je Richtung: T_1 gegen 4 T_C mit dem Urteil (39), dann F_d und M_0 -- mit q und mit q = 1.


## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.nachweis]]
- [[opencivil.core.rechenwerk]]
- [[opencivil.erdbeben.ersatzkraft]]
- [[opencivil.projekt]]
- [[opencivil.projekt.aufbau.erdbeben]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.web.anzeige]]

## Gebraucht von

- [[opencivil.web.zeichendaten]]
