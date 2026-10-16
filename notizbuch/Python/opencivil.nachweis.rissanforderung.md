---
erzeugt: 864aba6a98b4
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/rissanforderung.py
> die Anforderung an die Rissbildung.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/rissanforderung.py)

## VERANTWORTUNG

Die drei Stufen und was jede verlangt, an einer Stelle: wie sie heisst,
welche nominelle Rissbreite sie begrenzt und ob sie den Nachweis gegen
Fliessen unter haeufiger Einwirkung verlangt.

Vorher stand das in vier Tabellen -- die Rissbreite in der Mindestbewehrung,
der Fliessnachweis in der Spannungsbegrenzung, die Beschriftung im Leser,
die Liste fuer die Maske daraus gebaut --, und eine unbekannte Stufe wurde
an zwei Stellen ueber `.get` zur mildesten. Jetzt ist eine unbekannte
Stufe ein Fehler, wo immer sie auftaucht.

Die Rissbreiten 0.5 und 0.2 mm sind nach Vorgabe eingebaut, nicht
nachgeschlagen; dass bei normaler Anforderung kein Nachweis gegen Fliessen
gefuehrt wird, steht in SIA 262:2025, Tabelle 17 (ein Strich).

## Inhalt

### Rissanforderung

```python
class Rissanforderung(str, Enum)
```

Normal, erhoeht oder hoch -- wie die Maske und die Datei sie schreiben.

- `NORMAL = 'normal'`
- `ERHOEHT = 'erhoeht'`
- `HOCH = 'hoch'`

#### Rissanforderung.beschriftung

```python
@property
def beschriftung(self) -> str
```

Wie sie an der Maske heisst.

#### Rissanforderung.rissbreite

```python
@property
def rissbreite(self) -> Optional[float]
```

Die nominelle Rissbreite w_nom in m -- `None` heisst: keine Grenze aus
der Rissbreite, dann gilt allein `f_yk`. Nach Vorgabe, nicht
nachgeschlagen.

#### Rissanforderung.gegen_fliessen

```python
@property
def gegen_fliessen(self) -> bool
```

Ob der Nachweis gegen Fliessen unter haeufiger Einwirkung verlangt ist (Tabelle 17).


## Konstanten

- `RISSANFORDERUNGEN = tuple((a.value for a in Rissanforderung))` – Die Stufen, wie sie in der Datei stehen -- fuer die Wahl am Feld.

## Gebraucht von

- [[opencivil.nachweis.mindestbewehrung]]
- [[opencivil.nachweis.qa_gebrauch]]
- [[opencivil.nachweis.spannungsbegrenzung]]
- [[opencivil.nachweis.stabgrenzen]]
- [[opencivil.projekt.platte]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.web.api]]
