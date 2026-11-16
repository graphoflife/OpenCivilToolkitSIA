---
erzeugt: fefea81d63f3
art: modul
tags: [modul]
---
> [!abstract] opencivil/decke/schnitt.py
> die Schnittkräfte längs eines Schnitts.
> Paket [[opencivil.decke]] · [Quelltext](../../opencivil/decke/schnitt.py)

## VERANTWORTUNG

Ein Schnitt ist eine Strecke über die Decke, von `a` nach `b`. Längs ihr
zeigt ein Ergebnisbild eine Grösse der Platte als Verlauf, wie bei einem
Balken mit den Lagern, die er kreuzt (Benutzer, 2026-11-16). Gerechnet wird
damit nichts: die Werte kommen von [[opencivil.decke.feld#an_stelle|an_stelle]],
woher auch die Bilder der Platte und der Bericht sie nehmen.


## WO DER VERLAUF HINSIEHT

Zwischen zwei Stellen, an denen sich etwas ändert, ist jede Grösse längs
des Schnitts ein Polynom -- v_0 der Betrag zweier. Solche Stellen sind die
Grenzen der Feldstreifen, die Ränder der Unterzüge und der Platten und die
Enden der Trägerstücke, durch deren Streifen er läuft: ein Lager, eine
Last, die beginnt oder aufhört. Dort sieht der Verlauf zu beiden Seiten
hin, [[opencivil.decke.feld#Konstanten|INNEN]] daneben -- ein Sprung steht als
zwei Werte an fast derselben Stelle da. Auf eine solche Stelle selbst sieht
er nie: auf dem Rand eines Unterzugs zählten er und der Feldstreifen
daneben zugleich. Dazwischen in Schritten von höchstens einem
[[opencivil.decke.schnitt#Konstanten|SCHRITTE]]-tel der Länge und dort, wo ein Träger sein grösstes
Moment oder seine grösste Querkraft hat: wo seine Querkraft oder seine
Last null wird. So liegt der grösste Wert genau, wo ein Streifen allein
trägt -- wie in den Bildern der Platte ([[opencivil.decke.feld#stellen|stellen]]).


## WAS ER KREUZT

Linienlager als Lager, Stützen auch -- wenn er durch ihren Querschnitt geht
--, Unterzüge als Bereich. Alles in m ab `a`.

## Inhalt

### Lagerstelle

```python
@dataclass(frozen=True)
class Lagerstelle
```

Wo ein Schnitt ein Lager kreuzt: `u` in m ab seinem Anfang, und was das Lager hält.

- `u: float`
- `art: str` – `linienlager` oder `stuetze`.
- `name: str`
- `vertikal: bool = True`
- `eingespannt: bool = False`

### Verlauf

```python
@dataclass(frozen=True)
class Verlauf
```

Die Schnittkräfte längs eines Schnitts der Länge `L`, in m: wo er in
einer Platte liegt (`stuecke`, von -- bis ab seinem Anfang), seine
`proben` -- `(u, Schnittkräfte)`, aufsteigend --, die `lager`, die
er kreuzt, und die `unterzuege` als `(von, bis, Name)`.

- `L: float`
- `stuecke: List[Tuple[float, float]]`
- `proben: List[Tuple[float, Schnittkraefte]]`
- `lager: List[Lagerstelle]`
- `unterzuege: List[Tuple[float, float, str]]`

#### Verlauf.extreme

```python
def extreme(self, groesse: str) -> Tuple[Tuple[float, float], Tuple[float, float]]
```

`((u, kleinster), (u, grösster))` der Grösse unter den Proben -- bei gleichen Werten der vordere.

### verlauf

```python
def verlauf(ergebnis: Ergebnis, fall: Fallergebnis, a: Punkt, b: Punkt) -> Verlauf
```

Der Verlauf längs des Schnitts von `a` nach `b` im Fall `fall` -- ohne Länge leer.

### _stellen

```python
def _stellen(z: Zerlegung, fall: Fallergebnis, a: Punkt, e: Punkt) -> Tuple[List[float], List[float]]
```

Längs des Schnitts ab `a` in Richtung `e`, in m: wo sich etwas ändert
-- an den Grenzen der Feldstreifen und den Enden der Trägerstücke -- und
wo ein Träger seine grössten Werte hat. Ein Träger zählt nur, wo der
Schnitt durch seinen Streifen läuft; einer, der quer zum Schnitt trägt,
ändert sich längs ihm nicht.

### _im_streifen

```python
def _im_streifen(streifen: Streifen, a: Punkt, e: Punkt) -> Tuple[float, float]
```

Von wo bis wo der Schnitt quer im Streifen liegt, in m ab `a` -- `von > bis`, wenn nirgends.

### _gerastert

```python
def _gerastert(stellen: List[float]) -> List[float]
```

Aufsteigend, und was näher als [[opencivil.decke.geometrie#Konstanten|TOLERANZ]]
bei der vorigen liegt, nicht: der Rand eines Unterzugs ist auch die Grenze
zweier Feldstreifen, nur in der Rundung verschieden.

### _im_teil

```python
def _im_teil(p: float, q: float, schritt: float, spitzen: List[float]) -> List[float]
```

Die Stellen zwischen zwei Grenzen `p` und `q`: knapp innen an beiden
Enden, dazwischen höchstens `schritt` auseinander und an jeder Spitze
-- keine, wenn das Stück dafür zu kurz ist.

### _lager

```python
def _lager(decke: Decke, a: Punkt, b: Punkt, e: Punkt, L: float) -> List[Lagerstelle]
```

Die Lager, die der Schnitt kreuzt, nach ihrer Stelle: ein Linienlager,
wo er es schneidet -- wer längs eines Lagers schneidet, kreuzt es nicht
--, eine Stütze, wenn er durch ihren Querschnitt geht, dort, wo er ihrer
Mitte am nächsten ist.


## Konstanten

- `SCHRITTE = 120` – In so viele gleiche Schritte teilt der Verlauf einen Schnitt mindestens.
- `QUER = 1e-12` – Kleiner zählt eine Richtung als quer zum Schnitt -- ein Kosinus.

## Braucht

- [[opencivil.decke.feld]]
- [[opencivil.decke.geometrie]]
- [[opencivil.decke.modell]]
- [[opencivil.decke.rechnung]]
- [[opencivil.decke.streifen]]
- [[opencivil.decke.traeger]]

## Gebraucht von

- [[opencivil.web.deckendaten]]
