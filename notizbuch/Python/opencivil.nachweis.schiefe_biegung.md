---
erzeugt: c2c070f0eeb1
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/schiefe_biegung.py
> Biegung und Normalkraft am gezeichneten Querschnitt.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/schiefe_biegung.py)

## VERANTWORTUNG

Prueft je Lastfall `(N_Ed, M_y,Ed, M_z,Ed)` gegen den Bruchzustand des
gezeichneten Querschnitts -- schief, oder auf Wunsch nur um y.


## WOGEGEN NACHGEWIESEN WIRD

Bei der Platte gegen eine Handrechnung, die sich mit wenigen Zeilen
nachvollziehen laesst. Fuer ein beliebiges Polygon gibt es keine solche:
nachgewiesen wird darum gegen den Dehnungsfaecher selbst
([[opencivil.querschnitt.interaktion]]). Was in der Herleitung steht, ist
nicht die Suche, sondern ihre **Probe**: die gefundene Dehnungsebene, die
Kraefte jedes Teils mit ihrem Angriffspunkt, und die drei Summen `N`,
`M_y` und `M_z`. Wer nachrechnen will, rechnet diese Summen -- das geht
von Hand. Dasselbe Vorgehen wie beim Querschnittsloeser der Platte.


## DER MASSSTAB

Normalkraft fest, Richtung des Moments fest: `α_eff = M_Rd / M_Ed` in der
Richtung von `(M_y,Ed, M_z,Ed)`. Ohne Moment `N_Rd / N_Ed`.


## LAENGSZUGKRAFT

Ist sie zugeschaltet, kommt das, was das Druckfeld der Schubwaende in
Laengsrichtung braucht, zu N und den Momenten dazu -- siehe
[[opencivil.querschnitt.schubwaende]]. Die Werte liefert der Nachweis der
Schubwaende; dieser hier liest sie ueber das Rechenwerk.


## VORZEICHEN

N > 0 Zug; M_y > 0 zieht unten, M_z > 0 links.

## Inhalt

### Fallergebnis

```python
@dataclass
class Fallergebnis
```

Was ein Lastfall ergab -- fuer die Diagramme nach dem Lauf.

- `fall: Lastfall`
- `N: float`
- `M_y: float`
- `M_z: float` – Die Einwirkung, wie nachgewiesen -- mit Laengszugkraft, wo zugeschaltet.
- `punkt: Optional[Bruchpunkt]`
- `erfuellungsgrad: float`

### SchiefeBiegung

```python
class SchiefeBiegung(Nachweis)
```

Biegung und Normalkraft, je Lastfall gegen den Dehnungsfaecher.

- `THEMA = 'Schiefe Biegung'` – In der Formelsammlung ein eigenes Thema: gerechnet wird anders als bei der Platte, gegen den Dehnungsfaecher statt gegen eine Handrechnung. In der Zusammenfassung heisst er wie dort.
- `LANGNAME = 'Biegung und Normalkraft'`

#### SchiefeBiegung.pruefe

```python
def pruefe(self, e: Eingaben, p: Protokoll)
```


## Konstanten

- `KEIN_MOMENT = 1e-06` – Ab welchem Moment ein Lastfall als Biegung gilt, in Nm. Darunter ist es reine Normalkraft -- eine Richtung des Moments gibt es dann nicht.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.interaktion]]

## Gebraucht von

- [[opencivil.projekt.aufbau]]

## Formeln aus diesem Modul

- [[Dehnungsebene und innere Kräfte]] · `SchiefeBiegung._protokoll_ansatz`
- [[Erfüllungsgrad bei fester Normalkraft und fester Richtung]] · `SchiefeBiegung._protokoll_ansatz`
- [[Probe – Moment um y]] · `SchiefeBiegung._protokoll_bruchzustand`
- [[Probe – Moment um z]] · `SchiefeBiegung._protokoll_bruchzustand`
- [[Probe – Normalkraft]] · `SchiefeBiegung._protokoll_bruchzustand`
- [[Widerstand in der Richtung der Einwirkung]] · `SchiefeBiegung._ein_fall`
