---
erzeugt: 2505d9ed49a3
art: modul
tags: [modul]
---
> [!abstract] opencivil/material/fluessigkeit.py
> Fluessigkeiten: das Wasser und eigene.
> Paket [[opencivil.material]] · [Quelltext](../../opencivil/material/fluessigkeit.py)

## VERANTWORTUNG

Eine Fluessigkeit traegt nichts, sie wiegt nur. Ihr Kennwert ist die
Dichte `rho_fl`; daraus folgt ihre Raumlast `gamma_fl = rho_fl · g`,
eine gewoehnliche, einzeln ueberschreibbare Berechnung wie jeder Kennwert
([[opencivil.material.basis]]). Grundbruch und Pfahl nehmen aus ihr die
Raumlast des Grundwassers ([[opencivil.geotechnik.wasser]]); bis
2026-11-27 stand dort je ein Feld γ_w = 10 kN/m³.


## DIE SORTEN

Nur das Wasser, mit 1000 kg/m³ – nach Vorgabe, nicht nachgeschlagen. SIA
261:2020 rechnet den Wasserdruck mit der Raumlast des Wassers γ_w,k (4.4.2.1,
Gl. (8)), nennt dafuer aber keine Zahl; die fluessigen Stoffe in Anhang A,
Tabelle 30 sind Lagergueter, das Wasser steht nicht darunter. Eine andere
Fluessigkeit – eine Bentonitsuspension, Salzwasser – legt man als eigene
mit ihrer Dichte an.

g:
10 m/s² wie beim Eigengewicht ([[opencivil.material.basis#Konstanten|ERDBESCHLEUNIGUNG]]):
so wiegt das Wasser 10 kN/m³.

## Inhalt

### Fluessigkeitssorte

```python
@dataclass(frozen=True)
class Fluessigkeitssorte
```

Eine Fluessigkeit: ihre Dichte in kg/m³.

- `rho_fl: float`

### fluessigkeitssorten_zum_anlegen

```python
def fluessigkeitssorten_zum_anlegen() -> List[str]
```

Die Sorten in der Folge, in der neue angelegt werden: die erste, dann die uebrigen.

### fluessigkeit

```python
def fluessigkeit(sorte: str=ERSTE_FLUESSIGKEIT, *, name: Optional[str]=None, praefix: Optional[str]=None, abweichungen: Optional[Mapping[str, Groesse]]=None, symbol_index: str='') -> Baustoff
```

Erzeugt eine Fluessigkeit.

:param sorte: Bezeichnung aus [[opencivil.material.fluessigkeit#Konstanten|FLUESSIGKEITSSORTEN]], z.B. `'Wasser'`.
:param abweichungen: Zahlenwerte, die von der Sorte abweichen – bei einer
eigenen Fluessigkeit ihre Dichte.


## Konstanten

- `FLUESSIGKEITSSORTEN = {'Wasser': Fluessigkeitssorte(1000.0)}` – Die Fluessigkeiten, die das Werkzeug kennt – siehe Dateikopf.
- `ERSTE_FLUESSIGKEIT = 'Wasser'` – Womit eine neue Fluessigkeit anfaengt.
- `FLUESSIGKEIT_VORLAGEN = (KennwertVorlage(kurzname='rho_fl', symbol='\\rho_{fl}', einheit=KG_P…`

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.material.basis]]

## Gebraucht von

- [[opencivil.material.arten]]
- [[opencivil.projekt.frueher]]
- [[opencivil.projekt.projekt]]

## Formeln aus diesem Modul

- [[Raumlast der Flüssigkeit]]
