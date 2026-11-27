---
erzeugt: 3b4a10dfabaa
art: modul
tags: [modul]
---
> [!abstract] opencivil/stabwerk/querschnitte.py
> die Querschnitte der Staebe, nach Vorlage.
> Paket [[opencivil.stabwerk]] · [Quelltext](../../opencivil/stabwerk/querschnitte.py)

## VERANTWORTUNG

Was ein Stab von seinem Querschnitt braucht: die Flaeche `A`, die
Flaechentraegheitsmomente `I_y` um die waagrechte und `I_z` um die
senkrechte Achse durch den Schwerpunkt und das Torsionstraegheitsmoment
`I_T`. Je Vorlage stehen die Formeln hier – als Vorlage in Zeichen und als
Rechnung –, und aus ihnen entstehen im Rechenwerk die Formeln mit Zahlen
([[opencivil.stabwerk.rechnung]]). Der ebene Rahmen nimmt davon `A` und
`I_y`, das Stabwerk im Raum alle vier; gerechnet wird nur, was einer
braucht.


## DIE VORLAGEN

Rechteck, Kreis, Kreisring, Rechteckrohr, T-Querschnitt (Flansch oben),
Doppel-T und Trapez. Jede ist symmetrisch zur senkrechten Achse `z`;
`h` ist die Hoehe, entlang `z`, `b` die Breite, entlang `y`. Die
Seiten der Formeln heissen wie bei den Stahlprofilen
([[opencivil.stahlprofile.formen]]) – nur die von `I_y` ohne «um y»:
so hiessen sie, bevor es `I_z` gab.

Daneben: Kennwerte von Hand, der Streifen einer Platte (`b × h`, mit den
Formeln des Rechtecks) und der Bruttoquerschnitt einer Querschnittsanalyse
(`A` und `I_y`). Das waehlt die Beschreibung
([[opencivil.projekt.balkensystem]]), je Art eine Klasse rechnet es
([[opencivil.stabwerk.stabquerschnitt]]); hier stehen nur die Formeln.


## TORSION – NACH VORGABE, NICHT NACHGESCHLAGEN

Kreis und Kreisring haben `I_T = 2 · I_y`, wie jeder Kreisquerschnitt.
Das Rechteckrohr rechnet als duenne Wand: offen und nach Bredt geschlossen,
dieselbe Formel wie beim Rohr mit runden Ecken. Rechteck, T und Doppel-T
zerfallen in Rechtecke, und jedes traegt ``s · t³ · (1/3 - 0.21 · t/s ·
(1 - t⁴/(12 · s⁴)))` bei, mit `t` der kuerzeren und `s`` der laengeren
Seite – die Naeherung von Roark, beim Rechteck auf weniger als ein Prozent
genau; die Verbindung von Steg und Flansch zaehlt dabei nicht. Das Trapez
rechnet als Rechteck seiner mittleren Breite. Die Norm regelt nichts davon;
das TODO fuehrt es.


## EINHEITEN

Masse in mm, `A` in mm², die Traegheitsmomente in 10⁶ mm⁴ – wie in der
Querschnittsanalyse.

Die Umrisse von Rechteck, T und Kreis, was an einem T nicht geht, und das
[[opencivil.querschnitt.vorlagen#Mass|Mass]] mit seiner Grenze teilen sich
die Vorlagen hier mit denen der Querschnittsanalyse
([[opencivil.querschnitt.vorlagen]]).

## Inhalt

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
- `formeln: Tuple[Kennformel, ...]` – In der Reihenfolge, in der gerechnet wird – darunter `A`, `I_y`, `I_z` und `I_T`, bei einer Vorlage wie bei einem Stahlprofil ([[opencivil.stahlprofile.formen]]).
- `pruefung: Callable[[Masse], Optional[str]]`
- `umriss: Callable[[Masse], List[List[Tuple[float, float]]]]` – Die Umrisse fuer das Bild, in mm – der erste aussen, die weiteren Loecher.

#### Stabvorlage.vorgaben

```python
def vorgaben(self) -> Dict[str, float]
```

#### Stabvorlage.pruefen

```python
def pruefen(self, masse: Masse) -> Optional[str]
```

Was an den Massen nicht geht – `None`, wenn alles geht.

#### Stabvorlage.kennwerte

```python
def kennwerte(self, masse: Masse) -> Dict[str, Groesse]
```

Alle Kennwerte, der Reihe nach gerechnet – ohne Herleitung.

### rechtecktorsion

```python
def rechtecktorsion(t: Groesse, s: Groesse) -> Groesse
```

[[opencivil.stabwerk.querschnitte#Konstanten|RECHTECKTORSION]] als Rechnung.

### _seiten

```python
def _seiten(name: str, teil: str, nummer: str, a: Seite, b: Seite) -> Tuple[Kennformel, ...]
```

Die kuerzere Seite `t` und die laengere `s` eines Rechtecks mit den
Seiten `a` und `b` – je in Zeichen (mit `@`) und als Rechnung aus
den Werten. `teil` sagt, welches Rechteck: «des Flanschs»; `nummer`
haengt am Zeichen.

### _torsion

```python
def _torsion(name: str, teile: Tuple[Tuple[int, str], ...]) -> Kennformel
```

`I_T` aus Rechtecken, je mit `t` und `s` und der Nummer daran –
`(2, "_1")` heisst zweimal das Rechteck mit `t_1` und `s_1`.

### _wie_um_y

```python
def _wie_um_y(name: str) -> Tuple[Kennformel, Kennformel]
```

`I_z` und `I_T` eines Kreisquerschnitts: um jede Achse dasselbe, polar das Doppelte.

### vorlage

```python
def vorlage(schluessel: str) -> Stabvorlage
```


## Konstanten

- `EINS = Groesse(1.0, EINHEITSLOS)` – Eins ohne Einheit – fuer `1 - x` mit Groessen.
- `RECHTECKTORSION = '@s \\cdot \\left(@t\\right)^{3} \\cdot \\left(\\frac{1}{3} - 0.21 \\…` – Was ein Rechteck zum Torsionstraegheitsmoment beitraegt, mit der kuerzeren Seite `t` und der laengeren `s` – die Naeherung von Roark (Dateikopf).
- `ROHRTORSION = ('\\frac{\\left(@t\\right)^{3} \\cdot @p_m}{3} + \\frac{4 \\cdot \\le…` – Das Torsionstraegheitsmoment eines Rechteckrohrs: offen und geschlossen (Bredt), mit dem Umfang `p_m` und der umschlossenen Flaeche `A_m` der Mittellinie – auch beim Rohr mit runden Ecken ([[opencivil.stahlprofile.formen|formen]]).
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

- [[opencivil.projekt.staebe]]
- [[opencivil.stabwerk.stabquerschnitt]]
- [[opencivil.stahlprofile.formen]]
- [[opencivil.stahlprofile.tabelle]]
- [[opencivil.web.systemkatalog]]

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
- [[Flächenträgheitsmoment eines Kreisrings um z]] · `_wie_um_y`
- [[Flächenträgheitsmoment eines Rechteckrohrs]]
- [[Flächenträgheitsmoment eines Rechtecks]]
- [[Flächenträgheitsmoment eines Rechtecks um z]]
- [[Flächenträgheitsmoment eines T-Querschnitts]]
- [[Flächenträgheitsmoment eines Trapezes]]
- [[Kürzere Seite eines Rechtecks]] · `_seiten`
- [[Längere Seite eines Rechtecks]] · `_seiten`
- [[Schwerpunkt eines T-Querschnitts]]
- [[Torsionsträgheitsmoment eines Kreisrings]] · `_wie_um_y`
- [[Torsionsträgheitsmoment eines Rechtecks]] · `_torsion`
