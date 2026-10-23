---
erzeugt: 4d56e714d2e4
art: modul
tags: [modul]
---
> [!abstract] opencivil/web/setzungsdaten.py
> was die Oberflaeche von einer Setzung zeichnet.
> Paket [[opencivil.web]] · [Quelltext](../../opencivil/web/setzungsdaten.py)

## VERANTWORTUNG

Je Fundament die Zahlen der Situationszeichnung, in den Einheiten der
Anzeige -- m und mm: wo gerechnet wurde, wie die Zusatzspannung mit der
Tiefe abnimmt, was jede Schicht zur Setzung beitraegt, die Setzung und die
zulaessige. Die Abmessungen selbst liest die Oberflaeche aus dem Eintrag;
was der Kern daraus macht, kommt von hier.

Gerechnet wird hier nichts, was nicht der Kern schon weiss: die Linie des
Einflussfaktors kommt aus [[opencivil.geotechnik.setzung#einflusslinie|opencivil.geotechnik.setzung.einflusslinie]],
mit denselben L, B und demselben Punkt wie die Tabelle der Teilschichten.

## Inhalt

### situationen

```python
def situationen(aufbau: Aufbau, loesung: Loesung) -> Dict[str, Any]
```

Je Fundament, nach Kennung, was die Zeichnung vom Kern braucht.

### situation

```python
def situation(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Dict[str, Any]
```

Was die Zeichnung eines Fundaments braucht. Ohne Schicht gibt es keinen
Nachweis und keinen Befund -- dann zeichnet sie nur das Fundament.


## Braucht

- [[opencivil.core.rechenwerk]]
- [[opencivil.geotechnik.setzung]]
- [[opencivil.projekt]]

## Gebraucht von

- [[opencivil.web.api]]
