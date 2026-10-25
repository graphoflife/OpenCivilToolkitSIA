---
erzeugt: 09d5a6a575dc
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/qa_kennzahlen.py
> was ein gezeichneter Querschnitt aufnimmt, ohne Einwirkung.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/qa_kennzahlen.py)

## VERANTWORTUNG

Die Kennzahlen des gezeichneten Querschnitts, wie die der Platte
([[opencivil.nachweis.kennzahlen]]) -- gerechnet immer, ob es Lastfaelle
gibt oder nicht (Benutzer, 2026-10-23):

* das Bewehrungsmass: die Laengsbewehrung je Kubikmeter Beton, wie bei der
  Platte ohne Buegel;
* je Zugseite der Momentenwiderstand bei `N = 0` -- unten, oben, links,
  rechts, einachsig nur unten und oben;
* der Zug- und der Druckwiderstand bei gleichmaessiger Dehnung: dieselben
  Grenzen, gegen die der M-N-Nachweis reine Normalkraft haelt;
* je Zugseite mit Bewehrung die bezogene Druckzonenhoehe `x/d` bei
  `N = 0`;
* mit Schubwaenden der Widerstand gegen `V_z`, `V_y` und `T` je
  allein: so weit laesst sich die Last steigern, bis die erste Wand ihren
  Widerstand erreicht. Was die Waende nicht tragen koennen, steht nicht da.


## WAS DIE PLATTE HAT UND DIESER NICHT

Die Hoehe der Distanzhalter und die Vergroesserungsfaktoren gehoeren den
Lagen der Platte und ihrem Verformungsnachweis; ein gezeichneter
Querschnitt hat weder Lagen noch einen Verformungsnachweis. Einen
Querkraftwiderstand ohne Buegel rechnet die Platte je Meter; hier traegt
Querkraft nur, was als Schubwand gezeichnet ist.


## NICHTS ZWEIMAL

Gerechnet wird mit der Rechenwahl der Tragsicherheit, am selben
Bruchzustand wie Duktilitaet und sproedes Versagen
([[opencivil.querschnitt.biegung#Biegung.bei_reiner_biegung|bei_reiner_biegung]]); x und d
misst [[opencivil.querschnitt.interaktion#Querschnitt.druckzone|druckzone]], die
Grenzen der Normalkraft
[[opencivil.querschnitt.interaktion#Querschnitt.normalkraft_grenzen|normalkraft_grenzen]].
Die Schubwaende verteilen und widerstehen wie im Nachweis
([[opencivil.querschnitt.schubwaende]]); die Verteilung ist linear in
der Last, darum genuegt je Richtung eine Einheitslast.

## Inhalt

### _achse

```python
def _achse(seite: Zugseite) -> str
```

Um welche Achse ein Moment diese Seite zieht: y fuer unten und oben, sonst z.

### _getragen

```python
def _getragen(analyse: Querschnittsanalyse) -> List[str]
```

Welche Lasten die Schubwaende tragen koennen -- das haengt allein an ihrer
Lage, nicht an den Festigkeiten: V_y bei lauter senkrechten Waenden
nicht, Torsion nicht ohne Zelle und ohne drei Waende, die sich nicht in
einem Punkt treffen. Einachsig zaehlt V_y nicht.

### _einheit

```python
def _einheit(last: str, biegung: Biegung) -> Dict[str, float]
```

Eine Einheitslast in dieser Richtung -- 1 N oder 1 Nm, die anderen null;
so, wie sie wirkt: einachsig ist `V_y` null.

### KennzahlenQA

```python
class KennzahlenQA(Prozedur)
```

Die Kennzahlen eines gezeichneten Querschnitts -- siehe Dateikopf.

- `THEMA = 'Kennzahlen'`

#### KennzahlenQA._bewehrt

```python
def _bewehrt(self, seite: Zugseite) -> bool
```

Ob auf der gezogenen Seite des Schwerpunkts Bewehrung liegt -- an der
Zeichnung entschieden, damit feststeht, welche Kennzahlen es gibt. Eine
verschmierte Linie zaehlt mit ihren Enden.

#### KennzahlenQA.rechne

```python
def rechne(self, e: Eingaben, p: Protokoll) -> Dict[str, Groesse]
```


## Konstanten

- `BRUCH = 'N_Ed = 0, Dehnungsfächer mit der Rechenwahl der Tragsicherheit'` – Woher die Widerstaende stammen -- ihre Erklaerung unter dem Querschnitt.
- `SCHUB = (('V_z_Rd', 'V_z', 'V_{z,Rd}', KN, 'Querkraftwiderstand in z'), ('V_y…` – Die Lasten, gegen die die Schubwaende einzeln widerstehen: Kurzname, Komponente der Verteilung, Zeichen, Einheit, Beschriftung.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.material.betonstahl]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.biegung]]
- [[opencivil.querschnitt.schubwaende]]
- [[opencivil.querschnitt.zugseite]]

## Gebraucht von

- [[opencivil.projekt.aufbau.querschnittsanalyse]]

## Formeln aus diesem Modul

- [[Bewehrungsmass des gezeichneten Querschnitts]] · `KennzahlenQA._bewehrungsmass`
- [[Bezogene Druckzonenhöhe]] · `KennzahlenQA._biegung`
