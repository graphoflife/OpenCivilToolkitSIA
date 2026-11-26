---
erzeugt: 53f10cdff803
art: modul
tags: [modul]
---
> [!abstract] opencivil/web/pfahldaten.py
> was die Oberflaeche von einem Pfahl zeichnet.
> Paket [[opencivil.web]] · [Quelltext](../../opencivil/web/pfahldaten.py)

## VERANTWORTUNG

Je Pfahl die Zahlen der Situationszeichnung, in den Einheiten der Anzeige:
die Mantelreibung je Stück und der Spitzendruck, wie der äussere Widerstand
sie gerechnet hat, mit ihren Grössen ([[opencivil.web.pfahldaten#Konstanten|SITUATION]]). Dazu die Legende unter dem Bild
([[opencivil.web.anzeige]]): Mantel und Fuss, die Bemessungswerte beider
Nachweise auf Druck und auf Zug, quer je Kombination, und der Fall, der
entscheidet. Masse, Schichten und Grundwasser liest die Oberflaeche aus dem
Eintrag.

Dazu das Bild des Querschnitts ([[opencivil.web.pfahldaten#querschnitt|querschnitt]]), auch ohne
Kombination: seine Masse in mm, mit r_s und dem Durchmesser nach der
Abrostung aus denselben Funktionen wie im Nachweis.

Und je Kombination die Verläufe über die Tiefe, wie die Steifigkeit sie
gerechnet hat ([[opencivil.web.pfahldaten#verlaeufe|verlaeufe]]), mit dem Satz, der unter ihnen steht --
neben Moment und Querkraft der Widerstand des Pfahls, neben dem
Bettungsdruck der Erdwiderstand: die Grenzen, die sie nicht übersteigen
dürfen. Jede Grösse bringt Zeichen, Einheit und Stellen mit
([[opencivil.web.pfahldaten#Konstanten|VERLAEUFE]]); das Bild schreibt keine davon selbst.

Gerechnet wird hier nichts: alles steht in den Befunden.

## Inhalt

### situation

```python
def situation(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Dict[str, Any]
```

Was die Zeichnung eines Pfahls braucht. Ohne Kombination gibt es keinen
Nachweis und keinen Befund -- dann zeichnet sie nur den Pfahl im Boden.

### querschnitt

```python
def querschnitt(pfahl: Pfahl) -> Dict[str, Any]
```

Was das Bild des Querschnitts braucht, in mm: beim Bohrpfahl
Durchmesser, Laengsstaebe, Wendel und der Radius r_s ihrer Mitten, beim
Mikropfahl Verpresskoerper und Tragglied -- `t` `None` beim
Vollstab -- mit dem Durchmesser nach der Abrostung. Dazu die Legende.

### _befund

```python
def _befund(aufbau: Aufbau, kennung: str, loesung: Loesung, feld: str) -> Optional[Any]
```

Der Befund des Nachweises in `feld` -- `None`, wo es ihn nicht gibt.

### verlaeufe

```python
def verlaeufe(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Dict[str, Any]
```

Je Kombination Setzung, Normalkraft und -- wo quer gerechnet ist --
Verschiebung, Verdrehung, Moment, Querkraft und Bettungsdruck über die
Tiefe ab Terrain, dazu der Satz darunter. Leer ohne Steifigkeit.

### _verlauf

```python
def _verlauf(v: Verlauf, aussen: Optional[Querbefund], innen: Optional[Innenquerbefund]) -> Dict[str, Any]
```

Eine Kombination: die Tiefen und je gerechnete Grösse ihre Werte, mit der
Grenze, wo es eine gibt (sonst `None`).

### _grenzen

```python
def _grenzen(name: str, aussen: Optional[Querbefund], innen: Optional[Innenquerbefund]) -> Dict[str, List[float]]
```

Die Grenzen einer Kombination neben M, V und p, in SI -- leer, wo sie nicht quer belastet.

### _legende

```python
def _legende(aussen: Aussenbefund, innen: Innenbefund, quer: Optional[Querbefund], urteile: List[Any]) -> List[list]
```

Mantel und Fuss, die Bemessungswerte, quer je Kombination, der entscheidende Fall.


## Konstanten

- `VERLAEUFE = (('N', Anzeigegroesse('N', KN, stellen=0)), ('w', Anzeigegroesse('w',…` – Die Verläufe über die Tiefe, in der Folge der Bilder: Feld des Befunds und Grösse der Anzeige. Eine Grenze steht in derselben Einheit wie ihr Verlauf.
- `SITUATION = {'q_s': Anzeigegroesse('q_s,k', KPA, 'q_{s,k}'), 'q_b': Anzeigegroess…` – Was die Situationszeichnung aus der Lösung anschreibt.

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.rechenwerk]]
- [[opencivil.pfahl.aussen]]
- [[opencivil.pfahl.innen]]
- [[opencivil.pfahl.innen_quer]]
- [[opencivil.pfahl.pfahl]]
- [[opencivil.pfahl.quer]]
- [[opencivil.pfahl.steifigkeit]]
- [[opencivil.projekt]]
- [[opencivil.web.anzeige]]

## Gebraucht von

- [[opencivil.web.zeichendaten]]
