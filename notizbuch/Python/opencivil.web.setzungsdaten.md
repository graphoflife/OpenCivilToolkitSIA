---
erzeugt: 89f8a2273d56
art: modul
tags: [modul]
---
> [!abstract] opencivil/web/setzungsdaten.py
> was die Oberflaeche von einer Setzung zeichnet.
> Paket [[opencivil.web]] · [Quelltext](../../opencivil/web/setzungsdaten.py)

## VERANTWORTUNG

Je Fundament die Zahlen der Situationszeichnung, in den Einheiten der
Anzeige -- m und mm: wo gerechnet wurde, wie die Zusatzspannung mit der
Tiefe abnimmt und was jede Schicht zur Setzung beitraegt. Dazu die Legende
unter dem Bild ([[opencivil.web.anzeige]]): der Punkt, die Setzung gegen
die zulaessige mit dem Urteil, was die Linie zeigt, und die Laenge. Die
Abmessungen selbst liest die Oberflaeche aus dem Eintrag; was der Kern
daraus macht, kommt von hier.

Gerechnet wird hier nichts, was nicht der Kern schon weiss: die Linie des
Einflussfaktors kommt aus [[opencivil.geotechnik.setzung#einflusslinie|opencivil.geotechnik.setzung.einflusslinie]],
mit denselben L, B und demselben Punkt wie die Tabelle der Teilschichten.

## Inhalt

### situation

```python
def situation(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Dict[str, Any]
```

Was die Zeichnung eines Fundaments braucht. Ohne Schicht gibt es keinen
Nachweis und keinen Befund -- dann zeichnet sie nur das Fundament.

### _legende

```python
def _legende(fundament: setzung.Setzungsfundament, befund: setzung.Setzungsbefund, s_zul: float, gefunden) -> List[list]
```

Wo gerechnet wurde, die Setzung gegen die zulaessige, was die Linie zeigt.


## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.rechenwerk]]
- [[opencivil.geotechnik.setzung]]
- [[opencivil.projekt]]
- [[opencivil.web.anzeige]]

## Gebraucht von

- [[opencivil.web.zeichendaten]]
