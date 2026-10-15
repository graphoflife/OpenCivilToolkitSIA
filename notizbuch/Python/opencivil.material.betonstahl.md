---
erzeugt: a1ae240778ec
art: modul
tags: [modul]
---
> [!abstract] opencivil/material/betonstahl.py
> Betonstahl nach SIA 262:2025.
> Paket [[opencivil.material]] · [Quelltext](../../opencivil/material/betonstahl.py)

## VERANTWORTUNG

Sortentabelle und Kennwertherleitung fuer Betonstahl. Aufbau wie bei
[[opencivil.material.beton]]: jeder abgeleitete Kennwert ist eine eigene,
einzeln nachvollziehbare und einzeln ueberschreibbare Berechnung.

Alle Formeln hier sind einheitenrein -- es gibt keine empirischen Sonderfaelle.


## EIGENSTAENDIG NUTZBAR


```python
from opencivil.core.rechenwerk import Rechenwerk
from opencivil.material.betonstahl import betonstahl

werk = Rechenwerk()
b500b = betonstahl("B500B").ins_rechenwerk(werk)
print(werk.loese(b500b.id_von("f_yd")).wert(b500b.id_von("f_yd")))
```

## Inhalt

### Stahlsorte

```python
@dataclass(frozen=True)
class Stahlsorte
```

Zeile der Sortentabelle.

- `f_yk: float` – Charakteristische Fliessgrenze in N/mm^2.
- `f_yk_druck: float` – Charakteristische Fliessgrenze auf Druck in N/mm^2.
- `eps_uk: float` – Dehnung bei Hoechstlast in %.
- `eps_ud: float` – Bemessungswert der Dehnung bei Hoechstlast in %.

### stahlsorten_zum_anlegen

```python
def stahlsorten_zum_anlegen() -> List[str]
```

Die Stahlsorten in der Reihenfolge, in der neue angelegt werden -- siehe [[opencivil.material.betonstahl#Konstanten|ERSTER_STAHL]].

### betonstahl

```python
def betonstahl(sorte: str='B500B', *, name: Optional[str]=None, praefix: Optional[str]=None, abweichungen: Optional[Mapping[str, Groesse]]=None, symbol_index: str='') -> Baustoff
```

Erzeugt einen Betonstahl aus der Sortentabelle.

:param sorte: Bezeichnung aus [[opencivil.material.betonstahl#Konstanten|STAHLSORTEN]], z.B. `'B500B'`.
:param abweichungen: Zahlenwerte, die von der Tabelle abweichen.

### betonstahl_frei

```python
def betonstahl_frei(name: str, werte: Mapping[str, Groesse], *, praefix: Optional[str]=None) -> Baustoff
```

Erzeugt einen frei definierten Betonstahl ohne Sortentabelle.


## Konstanten

- `FLIESSDEHNUNG = 'Fliessdehnung'` – Die Seite im Notizbuch fuer die Dehnung, bei der der Stahl zu fliessen beginnt -- mit Bemessungswert oder charakteristisch, wo immer sie steht.
- `STAHLSORTEN = {'B500A': Stahlsorte(f_yk=500.0, f_yk_druck=500.0, eps_uk=2.5, eps_ud…` – Betonstahlsorten nach SIA 262:2025, Tabelle 3.2.2.3. Uebernommen aus der Vorgaengerfassung des Werkzeugs. Vor dem produktiven Einsatz gegen die gedruckte Norm pruefen.
- `ERSTER_STAHL = 'B500B'` – Womit ein neuer Betonstahl anfängt, wenn man in der Oberfläche einen anlegt: B500B, danach die übrigen der Reihe nach (Benutzer, 2026-10-15).
- `STAHL_VORLAGEN = (KennwertVorlage(kurzname='f_yk', symbol='f_{yk}', einheit=N_PRO_MM2,…`

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.material.basis]]

## Gebraucht von

- [[opencivil.nachweis.qa_gebrauch]]
- [[opencivil.nachweis.spannungsbegrenzung]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.lesen]]
- [[opencivil.spannungsanalyse]]
- [[opencivil.web.api]]

## Formeln aus diesem Modul

- [[Bemessungswert der Fliessgrenze]]
- [[Bemessungswert der Fliessgrenze auf Druck]]
- [[Fliessdehnung]]
