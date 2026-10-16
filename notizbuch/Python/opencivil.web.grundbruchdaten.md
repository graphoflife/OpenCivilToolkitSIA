---
erzeugt: 9ff10bb7e9ea
art: modul
tags: [modul]
---
> [!abstract] opencivil/web/grundbruchdaten.py
> was die Oberflaeche von einem Grundbruch zeichnet.
> Paket [[opencivil.web]] · [Quelltext](../../opencivil/web/grundbruchdaten.py)

## VERANTWORTUNG

Je Fundament die Zahlen der Situationszeichnung, in den Einheiten der
Anzeige -- m, kN, Grad: wie tief und wie weit der Gleitkoerper reicht, sein
Umriss, die Lage des Grundwassers, wie die Rechnung sie eingeordnet hat, und
je Kombination die Kraefte, die Neigung der Last und die beiden
Erfuellungsgrade. Die Abmessungen selbst liest die Oberflaeche aus dem
Eintrag; was der Kern daraus macht, kommt von hier.

Gerechnet wird hier nichts, was nicht der Kern schon weiss: der Umriss kommt
aus [[opencivil.geotechnik.grundbruch#gleitkoerper|opencivil.geotechnik.grundbruch.gleitkoerper]], mit denselben
Werten b und phi_eff wie die Formeln fuer L_Gl und H_Gl.

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

Was die Zeichnung eines Fundaments braucht. Ohne eingeschaltete
Kombination gibt es keinen Nachweis und keinen Befund -- dann zeichnet
sie nur das Fundament, ohne Gleitkörper und ohne Kräfte.


## Braucht

- [[opencivil.core.rechenwerk]]
- [[opencivil.geotechnik.grundbruch]]
- [[opencivil.projekt]]

## Gebraucht von

- [[opencivil.web.api]]
