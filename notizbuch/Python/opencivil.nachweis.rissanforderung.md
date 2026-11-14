---
erzeugt: e973c410565f
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

Alles steht in SIA 262:2025, Tabelle 17: erhoeht 0.5 mm, hoch 0.2 mm,
normal keine Rissbreite, nur `f_yk`; gegen Fliessen bei normaler
Anforderung ein Strich (am 2026-11-14 gegen die gedruckte Tabelle geprueft).

## Inhalt

### Rissanforderung

```python
class Rissanforderung(Wahl)
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
der Rissbreite, dann gilt allein `f_yk`. SIA 262:2025, Tabelle 17.

#### Rissanforderung.gegen_fliessen

```python
@property
def gegen_fliessen(self) -> bool
```

Ob der Nachweis gegen Fliessen unter haeufiger Einwirkung verlangt ist (Tabelle 17).


## Braucht

- [[opencivil.core.wahl]]

## Gebraucht von

- [[opencivil.nachweis.mindestbewehrung]]
- [[opencivil.nachweis.qa_gebrauch]]
- [[opencivil.nachweis.spannungsbegrenzung]]
- [[opencivil.nachweis.spannungsgrenzen]]
- [[opencivil.nachweis.stabgrenzen]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.web.api]]
