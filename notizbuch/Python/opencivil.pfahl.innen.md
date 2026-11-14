---
erzeugt: e8f25aca8899
art: modul
tags: [modul]
---
> [!abstract] opencivil/pfahl/innen.py
> der innere Widerstand eines Pfahls: sein Querschnitt.
> Paket [[opencivil.pfahl]] · [Quelltext](../../opencivil/pfahl/innen.py)

## VERANTWORTUNG

Der Nachweis [[opencivil.pfahl.innen#InnererWiderstand|InnererWiderstand]]: je Kombination die Normalkraft am
Kopf gegen den Bemessungswert des inneren Widerstands, auf Druck oder auf
Zug (SIA 267:2013, 9.5.2.4):

```
R_i,d = η_i · R_mat,d     (50)    η_i ≤ 0.8 in der Regel (51), bis 0.9 mit
                                  Prüfung der Integrität (9.5.2.4.9)
```

R_mat,d ist der Widerstand des Querschnitts nach SIA 262, gleichmässig
gestaucht oder gedehnt -- der Bruchzustand derselben Interaktion, mit der
die Querschnittsanalyse rechnet
([[opencivil.querschnitt.interaktion#Querschnitt.reine_normalkraft|reine_normalkraft]]),
mit denselben Werkstoffen ([[opencivil.querschnitt.analyse#werkstoff|werkstoff]]).
Ganz gedrückt endet der Beton dort bei −ε_c1d, und der Stahl mit ihm.


## DER QUERSCHNITT ([[opencivil.pfahl.innen#querschnitt|querschnitt]])

* Bohrpfahl -- ein Kreis aus Beton mit dem Durchmesser D, darin n Längsstäbe
  auf dem Kreis, den Überdeckung und Wendel frei lassen.
* Mikropfahl -- nur das Tragglied aus Stahl, um die Abrostung aussen
  verkleinert: ein Rohr oder ein Vollstab.
Kreise sind Vielecke derselben Fläche ([[opencivil.pfahl.innen#kreis|kreis]]).


## NACH VORGABE, NICHT NACHGESCHLAGEN (notizbuch/Notizen/TODO.md)

* Der Mörtel im Rohr des Mikropfahls zählt nicht, obwohl 9.5.2.4.8 den vom
  Stahl umschlossenen Beton zuliesse: nach SIA 262 gerechnet, endete mit ihm
  das Ganze bei −ε_c1d, und das Rohr flösse nicht mehr.
* Das Tragglied rechnet als Stahl der Liste nach SIA 262, mit dessen γ_s;
  SIA 263 ist nicht eingearbeitet.


## EINHEITEN

SI-Basis.

## Inhalt

### kreis

```python
def kreis(durchmesser: float) -> Tuple[Punkt, ...]
```

Ein Kreis um den Ursprung als Vieleck derselben Fläche, in m: die Ecken
liegen etwas ausserhalb des Kreises, damit A = π · d²/4 genau bleibt.

### Masse

```python
@dataclass(frozen=True)
class Masse
```

Was der Querschnitt aus den Eingaben braucht, in m -- je Pfahlart ein Teil davon.

- `D: float = 0.0` – Bohrpfahl: Durchmesser des Betons.
- `r_s: float = 0.0` – Bohrpfahl: Radius des Kreises, auf dem die Längsstäbe liegen.
- `n: int = 0`
- `phi_l: float = 0.0`
- `d_aussen: float = 0.0` – Mikropfahl: Aussendurchmesser des Tragglieds nach der Abrostung.
- `d_innen: float = 0.0` – Mikropfahl: Innendurchmesser des Rohrs -- null beim Vollstab.

### querschnitt

```python
def querschnitt(masse: Masse, werkstoffe: Sequence[Werkstoff]) -> Querschnitt
```

Der Querschnitt der Interaktion, um die Achse des Pfahls: mit Beton als
erstem Werkstoff und Stahl als zweitem der Bohrpfahl, sonst nur Stahl.

### biegewiderstand

```python
def biegewiderstand(q: Querschnitt, N: float, eta_i: float, staebe: int=0) -> float
```

Das Moment, das der Pfahl bei der Normalkraft N trägt, Druck positiv:
η_i · M_R(N / η_i) -- die Fläche der Widerstände um η_i verkleinert, wie
(50) den Widerstand. Von `staebe` Stäben gilt die Lage, die dem Moment
weniger nützt: ein Stab im gezogenen Rand oder zwei beidseits davon.
Null, wo N allein schon mehr ist, als der Querschnitt trägt.

### Innenbefund

```python
@dataclass
class Innenbefund
```

Was ausser den Erfüllungsgraden bleibt -- für Zusammenfassung und Bild, in SI.

- `masse: Masse`
- `A_s: float`
- `R_mat: float`
- `R_mat_zug: float`
- `R_id: float`
- `R_id_zug: float`

### InnererWiderstand

```python
class InnererWiderstand(Achsnachweis)
```

Siehe Dateikopf.

- `THEMA = 'Innerer Pfahlwiderstand'`
- `ART = 'R_i'`
- `INDEX = 'i'`
- `TITEL = 'Innerer Widerstand'`
- `WORT = 'innerer Widerstand'`

#### InnererWiderstand.pruefe

```python
def pruefe(self, e: Eingaben, p: Protokoll) -> Ausfuehrung
```

#### InnererWiderstand._normalkraft

```python
def _normalkraft(self, p: Protokoll, werte: Zwischenwerte, q: Querschnitt, werkstoffe: Sequence[Werkstoff], A_s: Wert, A_c: Optional[Wert], *, zug: bool) -> Wert
```

R_mat,d in einer Richtung: die Dehnung aus der Interaktion, die
Spannungen aus den Gesetzen, die Kraft als Summe -- Druck und Zug
als Beträge.

#### InnererWiderstand._bemessung

```python
def _bemessung(self, e: Eingaben, p: Protokoll, werte: Zwischenwerte, R_mat: Wert, *, zug: bool) -> Wert
```

R_i,d = η_i · R_mat,d (50).


## Konstanten

- `WAHL = Rechenwahl(art=Rechenart.PARABEL)` – Womit der Querschnitt rechnet: Bemessungswerte, der Beton als Parabel.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.pfahl.achse]]
- [[opencivil.pfahl.pfahl]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.gesetzwahl]]
- [[opencivil.querschnitt.interaktion]]
- [[opencivil.querschnitt.vorlagen]]

## Gebraucht von

- [[opencivil.pfahl.innen_quer]]
- [[opencivil.pfahl.quer]]
- [[opencivil.pfahl.uebersicht]]
- [[opencivil.projekt.aufbau.pfahl]]
- [[opencivil.web.pfahldaten]]

## Formeln aus diesem Modul

- [[Fläche der Längsbewehrung]] · `InnererWiderstand._bohrpfahl`
- [[Fläche des Pfahlquerschnitts]] · `InnererWiderstand._bohrpfahl`
- [[Fläche des Tragrohrs nach Abrostung]] · `InnererWiderstand._mikropfahl`
- [[Fläche des Tragstabs nach Abrostung]] · `InnererWiderstand._mikropfahl`
- [[Innerer Widerstand des Pfahls]] · `InnererWiderstand._bemessung`
- [[Materialwiderstand auf Druck]] · `InnererWiderstand._normalkraft`
- [[Materialwiderstand des Stahls]] · `InnererWiderstand._normalkraft`
- [[Radius des Bewehrungskreises]] · `InnererWiderstand._bohrpfahl`
