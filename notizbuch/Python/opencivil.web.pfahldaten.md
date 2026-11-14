---
erzeugt: ae4fc014dca6
art: modul
tags: [modul]
---
> [!abstract] opencivil/web/pfahldaten.py
> was die Oberflaeche von einem Pfahl zeichnet.
> Paket [[opencivil.web]] · [Quelltext](../../opencivil/web/pfahldaten.py)

## VERANTWORTUNG

Je Pfahl die Zahlen der Situationszeichnung, in den Einheiten der Anzeige:
die Mantelreibung je Stück und der Spitzendruck, wie der äussere Widerstand
sie gerechnet hat. Dazu die Legende unter dem Bild
([[opencivil.web.anzeige]]): Mantel und Fuss, die Bemessungswerte beider
Nachweise auf Druck und auf Zug und der Fall, der entscheidet. Masse,
Schichten und Grundwasser liest die Oberflaeche aus dem Eintrag.

Und je Kombination die Verläufe über die Tiefe, wie die Steifigkeit sie
gerechnet hat ([[opencivil.web.pfahldaten#verlaeufe|verlaeufe]]), mit dem Satz, der unter ihnen steht.

Gerechnet wird hier nichts: alles steht in den Befunden.

## Inhalt

### situation

```python
def situation(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Dict[str, Any]
```

Was die Zeichnung eines Pfahls braucht. Ohne Kombination gibt es keinen
Nachweis und keinen Befund -- dann zeichnet sie nur den Pfahl im Boden.

### verlaeufe

```python
def verlaeufe(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Dict[str, Any]
```

Je Kombination Setzung, Normalkraft und -- wo quer gerechnet ist --
Verschiebung, Verdrehung, Moment, Querkraft und Bettungsdruck über die
Tiefe ab Terrain, dazu der Satz darunter. Leer ohne Steifigkeit.

### _legende

```python
def _legende(aussen: Aussenbefund, innen: Innenbefund, urteile: List[Any]) -> List[list]
```

Mantel und Fuss, die Bemessungswerte, der entscheidende Fall.


## Konstanten

- `VERLAEUFE = (('N', KN), ('w', MM), ('y', MM), ('theta', MRAD), ('M', KNM), ('V', …` – Die Verläufe über die Tiefe: Feld des Befunds und Einheit der Anzeige.

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.rechenwerk]]
- [[opencivil.pfahl.aussen]]
- [[opencivil.pfahl.innen]]
- [[opencivil.pfahl.steifigkeit]]
- [[opencivil.projekt]]
- [[opencivil.web.anzeige]]

## Gebraucht von

- [[opencivil.web.zeichendaten]]
