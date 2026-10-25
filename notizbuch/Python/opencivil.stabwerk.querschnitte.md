---
erzeugt: d649c9e15cac
art: modul
tags: [modul]
---
> [!abstract] opencivil/stabwerk/querschnitte.py
> die Querschnitte der Staebe, nach Vorlage.
> Paket [[opencivil.stabwerk]] · [Quelltext](../../opencivil/stabwerk/querschnitte.py)

## VERANTWORTUNG

Was ein Stab des ebenen Rahmens von seinem Querschnitt braucht: die Flaeche
`A` und das Flaechentraegheitsmoment `I` um die Achse senkrecht zur
Ebene des Rahmens. Je Vorlage stehen die Formeln hier -- als Vorlage in
Zeichen und als Rechnung --, und aus ihnen entstehen im Rechenwerk die
Formeln mit Zahlen ([[opencivil.stabwerk.rechnung]]).


## DIE VORLAGEN

Rechteck, Kreis, Kreisring, Rechteckrohr, T-Querschnitt (Flansch oben),
Doppel-T und Trapez. Jede ist symmetrisch zur Ebene des Rahmens, damit die
Biegung in ihr bleibt. Gebogen wird um die waagrechte Achse durch den
Schwerpunkt; `h` ist die Hoehe in der Ebene des Rahmens.

Daneben: Kennwerte von Hand, der Streifen einer Platte (`b × h`, mit den
Formeln des Rechtecks) und der Bruttoquerschnitt einer Querschnittsanalyse
(`A` und `I_y`). Das waehlt die Beschreibung
([[opencivil.projekt.balkensystem]]), je Art eine Klasse rechnet es
([[opencivil.stabwerk.stabquerschnitt]]); hier stehen nur die Formeln.


## EINHEITEN

Masse in mm, `A` in mm², `I` in 10⁶ mm⁴ -- wie in der Querschnittsanalyse.

Die Umrisse von Rechteck, T und Kreis und was an einem T nicht geht, teilen
sich die Vorlagen hier mit denen der Querschnittsanalyse
([[opencivil.querschnitt.vorlagen]]).

## Inhalt

### Mass

```python
@dataclass(frozen=True)
class Mass
```

Ein Mass einer Vorlage -- in mm.

- `schluessel: str`
- `symbol: str`
- `beschriftung: str`
- `vorgabe: float`

### Kennformel

```python
@dataclass(frozen=True)
class Kennformel
```

Eine Formel einer Vorlage: was sie liefert, ihre Vorlage in Zeichen
(`@name` fuer ein Mass oder einen frueheren Kennwert) und die Rechnung
dazu, mit Groessen.

- `kurzname: str`
- `symbol: str`
- `einheit: Einheit`
- `stellen: int`
- `beschreibung: str`
- `vorlage: str`
- `funktion: Callable[..., Groesse]`
- `name: str` – Die Seite im Notizbuch.

### Stabvorlage

```python
@dataclass(frozen=True)
class Stabvorlage
```

- `schluessel: str`
- `name: str`
- `masse: Tuple[Mass, ...]`
- `formeln: Tuple[Kennformel, ...]` – In der Reihenfolge, in der gerechnet wird -- am Ende `A` und `I`.
- `pruefung: Callable[[Masse], Optional[str]]`
- `umriss: Callable[[Masse], List[List[Tuple[float, float]]]]` – Die Umrisse fuer das Bild, in mm -- der erste aussen, die weiteren Loecher.

#### Stabvorlage.vorgaben

```python
def vorgaben(self) -> Dict[str, float]
```

#### Stabvorlage.pruefen

```python
def pruefen(self, masse: Masse) -> Optional[str]
```

Was an den Massen nicht geht -- `None`, wenn alles geht.

#### Stabvorlage.kennwerte

```python
def kennwerte(self, masse: Masse) -> Dict[str, Groesse]
```

Alle Kennwerte, der Reihe nach gerechnet -- ohne Herleitung.

### vorlage

```python
def vorlage(schluessel: str) -> Stabvorlage
```


## Konstanten

- `RECHTECK = Stabvorlage(schluessel='rechteck', name='Rechteck', masse=(Mass('b', …` – Rechteck: b breit, h hoch.
- `KREIS = Stabvorlage(schluessel='kreis', name='Kreis', masse=(Mass('d', 'd', '…` – Kreis: Durchmesser d.
- `KREISRING = Stabvorlage(schluessel='kreisring', name='Kreisring', masse=(Mass('D'…` – Kreisring: aussen D, Wand t.
- `RECHTECKROHR = Stabvorlage(schluessel='rechteckrohr', name='Rechteckrohr', masse=(Ma…` – Rechteckrohr: b breit, h hoch, Wand t ringsum.
- `T_QUERSCHNITT = Stabvorlage(schluessel='t', name='T-Querschnitt', masse=(Mass('b', 'b…` – T-Querschnitt, Flansch oben: b breit, h hoch, Steg b_w, Flansch h_f.
- `DOPPEL_T = Stabvorlage(schluessel='doppel_t', name='Doppel-T', masse=(Mass('b', …` – Doppel-T, symmetrisch: b breit, h hoch, Flansche t_f, Steg t_w.
- `TRAPEZ = Stabvorlage(schluessel='trapez', name='Trapez', masse=(Mass('b_o', 'b…` – Trapez: oben b_o, unten b_u, h hoch.
- `VORLAGEN = (RECHTECK, KREIS, KREISRING, RECHTECKROHR, T_QUERSCHNITT, DOPPEL_T, T…`

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.querschnitt.vorlagen]]

## Gebraucht von

- [[opencivil.projekt.balkensystem]]
- [[opencivil.stabwerk.stabquerschnitt]]
- [[opencivil.web.api]]

## Formeln aus diesem Modul

- [[Fläche eines Doppel-T-Querschnitts]]
- [[Fläche eines Kreises]]
- [[Fläche eines Kreisrings]]
- [[Fläche eines Rechteckrohrs]]
- [[Fläche eines Rechtecks]]
- [[Fläche eines T-Querschnitts]]
- [[Fläche eines Trapezes]]
- [[Flächenträgheitsmoment eines Doppel-T-Querschnitts]]
- [[Flächenträgheitsmoment eines Kreises]]
- [[Flächenträgheitsmoment eines Kreisrings]]
- [[Flächenträgheitsmoment eines Rechteckrohrs]]
- [[Flächenträgheitsmoment eines Rechtecks]]
- [[Flächenträgheitsmoment eines T-Querschnitts]]
- [[Flächenträgheitsmoment eines Trapezes]]
- [[Schwerpunkt eines T-Querschnitts]]
