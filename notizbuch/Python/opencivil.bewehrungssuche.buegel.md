---
erzeugt: 3adc9b80f5f7
art: modul
tags: [modul]
---
> [!abstract] opencivil/bewehrungssuche/buegel.py
> die Querkraftbewehrung suchen.
> Paket [[opencivil.bewehrungssuche]] · [Quelltext](../../opencivil/bewehrungssuche/buegel.py)

## VERANTWORTUNG

Die duennsten Buegel, mit denen der Querkraftnachweis aufgeht -- nach der
Laengsbewehrung, denn ohne statische Hoehe gibt es keinen
Querkraftwiderstand.

## Inhalt

### Buegelloesung

```python
@dataclass
class Buegelloesung
```

Was die Suche nach den Buegeln gefunden hat.

- `gefunden: bool = False`
- `durchmesser: float = 0.0`
- `teilung: float = 0.0` – Teilung in beiden Richtungen -- ein Buegelraster ist quadratisch.
- `stahlvolumen: float = 0.0` – Buegelquerschnitt je Flaecheneinheit, in mm²/m² -- das Mass, nach dem verglichen wird. Bei Buegeln zaehlt nicht die Flaeche je Streifen, sondern wie dicht sie stehen.
- `begruendung: str = ''`

### buegel_suchen

```python
def buegel_suchen(projekt, kennung: str, *, teilungen: Sequence[float]=TEILUNGEN, durchmesser: Sequence[float]=BUEGELDURCHMESSER) -> Buegelloesung
```

Die duennsten Buegel, mit denen der Querkraftnachweis aufgeht.

Gesucht wird ueber Durchmesser und Rasterweite; das Raster ist quadratisch
(`s_x = s_y`), weil eine Platte in beiden Richtungen gleich durchstanzt
wird. Verglichen wird ueber den Buegelquerschnitt je Flaecheneinheit --
ein dicker Stab weit auseinander kann weniger Stahl sein als ein duenner
eng, und teurer ist er trotzdem seltener.

Geht es ohne Buegel, kommt das heraus: Durchmesser null. Was an der
Platte nicht stimmen kann, meldet sich vorab ([[opencivil.bewehrungssuche.bewertung#vorab_pruefen|vorab_pruefen]]).

### buegel_uebernehmen

```python
def buegel_uebernehmen(projekt, kennung: str, loesung: Buegelloesung) -> None
```

Die gefundenen Buegel in die Platte schreiben.


## Konstanten

- `BUEGELDURCHMESSER = (8, 10, 12, 14, 16, 18, 20, 22, 26)` – Buegel dicker als ⌀26 biegt niemand -- die Buegelsuche bleibt darunter.

## Braucht

- [[opencivil.bewehrungssuche.bewertung]]
- [[opencivil.bewehrungssuche.laengs]]

## Gebraucht von

- [[opencivil.bewehrungssuche]]
