---
erzeugt: 3e23b3c10151
art: modul
tags: [modul]
---
> [!abstract] opencivil/pfahl/quer.py
> der äussere Widerstand eines Pfahls quer zu seiner Achse.
> Paket [[opencivil.pfahl]] · [Quelltext](../../opencivil/pfahl/quer.py)

## VERANTWORTUNG

Der Nachweis [[opencivil.pfahl.quer#AeussererQuerwiderstand|AeussererQuerwiderstand]], je Kombination, die den Pfahl
quer belastet ([[opencivil.pfahl.pfahl#Pfahl.quer_belastet|quer_belastet]]):

* die Querkraft am Kopf gegen den Bemessungswert des äusseren Widerstands
  quer (SIA 267:2013, 9.4.4.2.2, 9.5.2.3):

```
R_tr,k   der kleinste Bruch aus dem Erdwiderstand p_E,k und dem
         Biegewiderstand M_R des Pfahls (:func:`~.erdwiderstand.brueche`)
R_tr,d = η_a,tr · R_tr,k / γ_M,a     wie (42), mit γ_M,a = 1.4 (49)
```

* in jeder Tiefe die Bettungskraft der Verläufe gegen den Erdwiderstand
  (9.5.4.5):

```python
q_d(z) = |p(z)| · D  ≤  p_E,d(z) = η_a,tr · p_E,k(z) / γ_M,a
```

Die Verläufe kommen aus der Steifigkeit ([[opencivil.pfahl.steifigkeit|.steifigkeit]]), der
Querschnitt aus dem inneren Widerstand ([[opencivil.pfahl.innen|.innen]]) -- beide als Befund.


## DER BIEGEWIDERSTAND IM BRUCH

η_i · M_R,k(N / η_i), mit f_ck und f_yk ([[opencivil.pfahl.innen#biegewiderstand|biegewiderstand]]).
Längs des Pfahls liegt N zwischen dem Wert am Kopf und dem am Fuss. Die
Fläche der Widerstände ist konvex, M_R also in N konkav: sein kleinster Wert
liegt an einem der beiden Enden, und mit ihm rechnen alle Gelenke.


## NACH VORGABE, NICHT NACHGESCHLAGEN (notizbuch/Notizen/TODO.md)

* γ_M,a = 1.4, nach (49) in der Regel der kleinste Wert; die Norm will R_tr,d
  je Objekt bestimmt haben.
* Der Biegewiderstand charakteristisch mal η_i: 9.4.4.2.2 nennt den
  charakteristischen inneren Widerstand, η_i steht bei (50).
* Die Bettungskraft gegen p_E,d, mit denselben Beiwerten wie R_tr,d.
* Ohne H_Ed kein R_tr: ein Moment allein prüft nur die Bettungskraft.


## EINHEITEN

SI-Basis.

## Inhalt

### Querfall

```python
@dataclass
class Querfall
```

Was eine Kombination quer ergab, in SI -- R_tr nur mit H_Ed.

- `grenze: List[float]` – In jeder Tiefe der Verläufe p_E,d / D: der Erdwiderstand als Druck, wie der Bettungsdruck.
- `R_trk: Optional[float] = None`
- `R_trd: Optional[float] = None`
- `bruch: Optional[Bruch] = None`

### Querbefund

```python
@dataclass
class Querbefund
```

Je Kombination, nach ihrem Namen, was sie quer ergab -- für das Bild.

- `faelle: Dict[str, Querfall] = field(default_factory=dict)`

### AeussererQuerwiderstand

```python
class AeussererQuerwiderstand(Nachweis)
```

Siehe Dateikopf.

- `THEMA = 'Äusserer Pfahlwiderstand quer'`
- `ART = 'R_tr'`

#### AeussererQuerwiderstand.pruefe

```python
def pruefe(self, e: Eingaben, p: Protokoll) -> Ausfuehrung
```

#### AeussererQuerwiderstand._erdwiderstand

```python
def _erdwiderstand(self, e: Eingaben, p: Protokoll, oben: float, unten: float) -> Erdwiderstand
```

p_E,k aus den Schichten -- die Erddrücke nur für die Arten, die am Pfahl vorkommen.

#### AeussererQuerwiderstand._tabelle

```python
def _tabelle(self, p: Protokoll, linien: Sequence[Linie]) -> None
```

p_E,k am Pfahl, je Stück oben und unten.

#### AeussererQuerwiderstand._brueche

```python
def _brueche(self, p: Protokoll) -> None
```

Die Brüche, die der Kopf zulässt.

#### AeussererQuerwiderstand._bettung

```python
def _bettung(self, e: Eingaben, p: Protokoll, werte: Zwischenwerte, k: Kombination, v: Verlauf, erd: Erdwiderstand, fall: Querfall) -> NachweisUrteil
```

In jeder Tiefe der Verläufe die Bettungskraft gegen p_E,d -- massgebend die knappste.


## Konstanten

- `GAMMA_M_QUER = 1.4` – Der Widerstandsbeiwert quer zur Achse -- der kleinste, den die Norm zulässt.
- `GAMMA_M_QUER_REFERENZ = 'SIA 267:2013, 9.5.2.3.1, (49)'`
- `WAHL_BRUCH = Rechenwahl(art=Rechenart.PARABEL, satz=Werkstoffsatz.CHARAKTERISTISCH)` – Womit der Pfahl im Bruch biegt: charakteristische Werte, der Beton als Parabel.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.nachweis]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.pfahl.buch]]
- [[opencivil.pfahl.erdwiderstand]]
- [[opencivil.pfahl.innen]]
- [[opencivil.pfahl.pfahl]]
- [[opencivil.pfahl.steifigkeit]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.gesetzwahl]]
- [[opencivil.querschnitt.interaktion]]

## Gebraucht von

- [[opencivil.projekt.aufbau.pfahl]]
- [[opencivil.web.pfahldaten]]

## Formeln aus diesem Modul

- [[Bemessungswert des äusseren Widerstands]] · `AeussererQuerwiderstand._querkraft`
- [[Bemessungswert des Erdwiderstands am Pfahl]] · `AeussererQuerwiderstand._bettung`
- [[Erddruck am Pfahl drainiert]] · `AeussererQuerwiderstand._erdwiderstand`
- [[Erddruck am Pfahl undrainiert]] · `AeussererQuerwiderstand._erdwiderstand`
- [[Erdwiderstand je Meter Pfahl]] · `AeussererQuerwiderstand._erdwiderstand`
- [[Hebel des Moments am Pfahlkopf]] · `AeussererQuerwiderstand._querkraft`
- [[Querbruch am eingespannten Kopf]] · `AeussererQuerwiderstand._brueche`
- [[Querbruch am frei drehbaren Kopf]] · `AeussererQuerwiderstand._brueche`
- [[Querbruch durch Verschieben]] · `AeussererQuerwiderstand._brueche`
