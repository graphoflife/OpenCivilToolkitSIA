---
erzeugt: 799a57283b44
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/schubwandnachweis.py
> Querkraft und Torsion am gezeichneten Querschnitt.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/schubwandnachweis.py)

## VERANTWORTUNG

Je Lastfall `(V_y, V_z, T)` auf die Schubwaende verteilt und jede Wand mit
dem Fachwerk nachgewiesen. Die Verteilung – Federn nach `b_w · l`, Versatz,
Zellen nach Bredt – steht in [[opencivil.querschnitt.schubwaende]]; hier
wird sie aufgeschrieben und geurteilt.

Liefert zudem je Lastfall die Laengszugkraft `ΔN, ΔM_y, ΔM_z`, wenn sie
zugeschaltet ist: der Nachweis von Biegung und Normalkraft liest sie.


## DER MASSSTAB

Jede Schubwand fuer sich, mit ihrer ganzen Kraft, nicht je Meter (Benutzer,
2026-11-18): die gezeichneten Waende an ihren Knoten geteilt
([[opencivil.querschnitt.schubwaende#einzeln|einzeln]]), je Wand
`V_Ed = |q| · l` gegen das Fachwerk mit ihrer Laenge als Hebelarm
([[opencivil.querschnitt.schubwaende#wandkraefte|wandkraefte]],
[[opencivil.querschnitt.schubwaende#widerstand|widerstand]]). Massgebend ist die
schwaechste Wand; nur sie steht in der Zusammenfassung.


## GENEIGTE SPANNGLIEDER

Ein geneigtes Glied mit Vordehnung traegt mit seiner lotrechten Kraft
`F · sin beta_p` einen Teil von `V_z`
([[opencivil.querschnitt.spannglieder]]). Die Waende tragen den Rest:
`V_z - Σ F_i sin beta_p,i`, und in der Torsion fehlt ihnen das Moment
dieser Kraefte um den Schwerpunkt. Jede Wand vergleicht diesen Rest mit
ihrem Widerstand. Gleichung (50) schreibt den mitgetragenen Teil dem
Widerstand zu; an der Grenze ist das dasselbe, und nur so verteilt er sich
auf mehrere Waende – nach Vorgabe, nicht nachgeschlagen. `F` ist
`P_inf`, wo die lotrechte Kraft wie `V_z` wirkt (4.3.3.4.8); wirkt sie
entgegen, die groesste Kraft im Glied (4.3.3.4.9): mit Verbund `A_p`
mal die Fliessgrenze seines Wertesatzes – so weit kann es im Bruch
tragen –, ohne Verbund `A_p · sigma_p0`, die Kraft nach dem Spannen.
Welche Kraft die groesste ist, sagt die Norm nicht: nach Vorgabe, nicht
nachgeschlagen.

## Inhalt

### schub_belastet

```python
def schub_belastet(biegung: Biegung, fall: Lastfall) -> bool
```

Ob ein Lastfall die Schubwaende belastet – einachsig zaehlt `V_y`
nicht. Fuer den Nachweis und fuer den Aufbau, der fragt, ob es ihn
braucht.

### Schubbefund

```python
@dataclass
class Schubbefund
```

Was der Nachweis im Lauf fand: die Waende einzeln und ihre Zellen, je
Lastfall die Verteilung des Schubflusses und je Wand den Widerstand bei
der gewaehlten Neigung und ihren Vergleich – fuer die Diagramme. Ein
Lastfall ohne Verteilung (keine Last, keine Wand) fehlt in diesen dreien;
war er belastet, sagt `ohne` warum.

- `modell: sw.Zellenmodell`
- `verteilungen: Dict[str, sw.Verteilung] = field(default_factory=dict)`
- `widerstaende: Dict[str, List[Buegelpunkt]] = field(default_factory=dict)`
- `vergleiche: Dict[str, List[Vergleich]] = field(default_factory=dict)` – Je Wand ihre Kraft gegen ihren Widerstand, beide fuer die ganze Wand.
- `ohne: Dict[str, str] = field(default_factory=dict)` – Je belasteter Lastfall ohne Verteilung der Grund – es gibt keine Wand, oder die Waende tragen nicht. Derselbe Satz wie im Urteil.
- `glieder: Dict[str, float] = field(default_factory=dict)` – Je Lastfall, was die geneigten Spannglieder von `V_z` tragen, in N – ohne sie leer.

#### Schubbefund.waende

```python
@property
def waende(self) -> Tuple[sw.Wand, ...]
```

### GeneigtesGlied

```python
@dataclass(frozen=True)
class GeneigtesGlied
```

Ein geneigtes Glied, wie der Nachweis es liest: seine zwei Kraefte, seine Neigung, sein Hebel.

- `glied: Spannglied`
- `P_inf: Wert`
- `P_max: Wert`
- `beta: Wert`
- `hebel: Wert` – `y - y_S`: wie weit es neben dem Schwerpunkt liegt.

#### GeneigtesGlied.kraft

```python
def kraft(self, V_z: float) -> Wert
```

`P_inf`, wo es `V_z` mittraegt – sonst `P_max`.

#### GeneigtesGlied.lotrecht

```python
def lotrecht(self, V_z: float) -> float
```

Seine lotrechte Kraft im Lastfall mit `V_z`, in N.

### Schubwandnachweis

```python
class Schubwandnachweis(Nachweis)
```

Querkraft und Torsion, je Lastfall auf die Schubwaende verteilt.

- `THEMA = 'Querkraft und Torsion'`
- `ART = 'V+T'`

#### Schubwandnachweis.pruefe

```python
def pruefe(self, e: Eingaben, p: Protokoll)
```

#### Schubwandnachweis._protokoll_glieder

```python
def _protokoll_glieder(self, p: Protokoll, e: Eingaben, bezug) -> List[GeneigtesGlied]
```

Die Regel, und je geneigtes Glied seine grösste Kraft – ohne Glied nichts.

#### Schubwandnachweis._ohne_glieder

```python
def _ohne_glieder(self, p: Protokoll, werte: Zwischenwerte, befund: Schubbefund, fall: Lastfall, geneigte: Sequence[GeneigtesGlied]) -> Tuple[Wert, Wert]
```

`V_z` und `T`, die die Waende tragen: ohne die lotrechte Kraft der
geneigten Glieder und ihr Moment um den Schwerpunkt.


## Konstanten

- `GROESSTE_KRAFT = 'Grösste Kraft eines geneigten Spannglieds'` – Die Seiten im Notizbuch, je Groesse eine.
- `LOTRECHT = 'Lotrechte Kraft der geneigten Spannglieder'`
- `QUERKRAFT_DER_WAENDE = 'Querkraft der Wände neben geneigten Spanngliedern'`
- `MOMENT_DER_GLIEDER = 'Torsion aus der lotrechten Kraft der Spannglieder'`
- `TORSION_DER_WAENDE = 'Torsion der Wände neben geneigten Spanngliedern'`
- `REFERENZ_GLIEDER = f'{REFERENZ_GUENSTIG}; {REFERENZ_UNGUENSTIG}'` – Wo die lotrechte Kraft der Glieder steht: mittragend und entgegen.
- `OHNE_SCHUB = 'Keine Querkraft und keine Torsion → kein Schubfluss.'` – Warum ein Lastfall ohne Querkraft und Torsion keinen Schubfluss hat – das Diagramm zeigt den Satz an Stelle des Bildes.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.nachweis]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.biegung]]
- [[opencivil.querschnitt.fachwerk]]
- [[opencivil.querschnitt.schubwaende]]
- [[opencivil.querschnitt.spannglieder]]

## Gebraucht von

- [[opencivil.projekt.aufbau.querschnittsanalyse]]
- [[opencivil.web.diagrammdaten]]

## Formeln aus diesem Modul

- [[Grösste Kraft eines geneigten Spannglieds]] · `Schubwandnachweis._protokoll_glieder`
- [[Kraft einer Wand – ihr Schubfluss über ihre Länge]] · `Schubwandnachweis._protokoll_ansatz`
- [[Lotrechte Kraft der geneigten Spannglieder]] · `Schubwandnachweis._ohne_glieder`
- [[Lotrechte Kraft der geneigten Spannglieder]] · `Schubwandnachweis._protokoll_glieder`
- [[Querkraft der Wände neben geneigten Spanngliedern]] · `Schubwandnachweis._ohne_glieder`
- [[Querkraft der Wände neben geneigten Spanngliedern]] · `Schubwandnachweis._protokoll_glieder`
- [[Querkraft über die Federn der Wände]] · `Schubwandnachweis._protokoll_ansatz`
- [[Torsion aus der lotrechten Kraft der Spannglieder]] · `Schubwandnachweis._ohne_glieder`
- [[Torsion der Wände neben geneigten Spanngliedern]] · `Schubwandnachweis._ohne_glieder`
- [[Torsion in den Zellen (Bredt, mehrzellig)]] · `Schubwandnachweis._protokoll_ansatz`
- [[Versatz – Moment der Querkraftanteile um den Schwerpunkt]] · `Schubwandnachweis._ein_fall`
- [[Was die Zellen tragen]] · `Schubwandnachweis._ein_fall`
- [[Widerstand einer Wand (Fachwerk, ihre Länge l als Hebelarm)]] · `Schubwandnachweis._protokoll_ansatz`
