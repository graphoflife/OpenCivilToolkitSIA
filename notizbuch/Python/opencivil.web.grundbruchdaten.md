---
erzeugt: 9f750c812387
art: modul
tags: [modul]
---
> [!abstract] opencivil/web/grundbruchdaten.py
> was die Oberflaeche von einem Grundbruch zeichnet.
> Paket [[opencivil.web]] · [Quelltext](../../opencivil/web/grundbruchdaten.py)

## VERANTWORTUNG

Je Fundament die Zahlen der Situationszeichnung, in den Einheiten der
Anzeige -- m, kN: wie tief und wie weit der Gleitkoerper reicht, sein
Umriss und je Kombination die Kraefte und die beiden Erfuellungsgrade. Dazu
die Legende unter dem Bild ([[opencivil.web.anzeige]]): je Kombination
ihre Zeile mit der Neigung der Last, darunter das Grundwasser, wie die
Rechnung es eingeordnet hat, der Gleitkoerper und die Laenge. Die
Abmessungen selbst liest die Oberflaeche aus dem Eintrag; was der Kern
daraus macht, kommt von hier.

Gerechnet wird hier nichts, was nicht der Kern schon weiss: der Umriss kommt
aus [[opencivil.geotechnik.grundbruch#gleitkoerper|opencivil.geotechnik.grundbruch.gleitkoerper]], mit denselben
Werten b und phi_eff wie die Formeln fuer L_Gl und H_Gl.

## Inhalt

### situation

```python
def situation(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Dict[str, Any]
```

Was die Zeichnung eines Fundaments braucht. Ohne eingeschaltete
Kombination gibt es keinen Nachweis und keinen Befund -- dann zeichnet
sie nur das Fundament, ohne Gleitkörper und ohne Kräfte.

### _legende

```python
def _legende(fundament: grundbruch.Fundament, befund: Optional[grundbruch.Grundbruchbefund], *, gezeichnet: bool) -> List[list]
```

Die Zeilen unter dem Bild, die fuer jede Kombination gelten: das
Grundwasser, der Gleitkoerper -- gezeichnet ist er ohne die Neigungen --
und die Laenge senkrecht zum Bild. Die Zeile der gezeigten Kombination
steht bei ihr.


## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.rechenwerk]]
- [[opencivil.geotechnik.grundbruch]]
- [[opencivil.projekt]]
- [[opencivil.web.anzeige]]

## Gebraucht von

- [[opencivil.web.zeichendaten]]
