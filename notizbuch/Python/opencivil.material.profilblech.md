---
erzeugt: 43da2431403a
art: modul
tags: [modul]
---
> [!abstract] opencivil/material/profilblech.py
> Profilblechstahl nach SIA 264:2014.
> Paket [[opencivil.material]] · [Quelltext](../../opencivil/material/profilblech.py)

## VERANTWORTUNG

Sortentabelle und Kennwerte des Stahls, aus dem die Profilbleche einer
Blechverbunddecke sind, aufgebaut wie der Baustahl
([[opencivil.material.baustahl]]): jeder Kennwert ist eine eigene, einzeln
ueberschreibbare Berechnung. Das Blech selbst -- seine Rippen und seine
Flaeche aus dem Datenblatt -- gehoert zur Blechverbunddecke, einem Element
der Querschnittsanalyse ([[opencivil.projekt.blechdecken]]); seine Form
rechnet [[opencivil.querschnitt.profilblech]], und `m` und `k` des
Laengsschubs stehen an der Analyse. Nichts davon gehoert zum Material.


## DIE SORTENTABELLE

SIA 264:2014, 3.3.1, Tabelle 1 nennt fuer die Sorten SE 220 G bis SE 550 G
nach SN EN 10346 die Streckgrenze `f_yp` und die Zugfestigkeit `f_u`,
fuer Dicken bis 3 mm. Die Bruchdehnung der Tabelle braucht keine Rechnung;
sie fehlt hier. Am 2026-11-27 gegen die gedruckte Tabelle geprueft.


## DIE NORMVORGABEN

Den Elastizitaetsmodul nennt SIA 264 nicht selbst: nach 3.1.1 gelten die
Eigenschaften der SIA 263, also `E_a` aus 3.2.2.1. Der
Widerstandsbeiwert `γ_ap = 1.05` steht in 4.1.5, der Bemessungswert
`f_yp/γ_ap` in 4.1.3, Gleichung (1).


## DIE ERSTE SORTE

SE 350 G -- nach 3.3.1 sind SE 320 G und SE 350 G ueblich (nach Vorgabe,
nicht nachgeschlagen, welche von beiden zuerst steht).


## DAS GESETZ

Wie beim Baustahl elastisch -- ideal plastisch, in Zug und Druck gleich
([[opencivil.querschnitt.werkstoffgesetz#Profilblechgesetz|Profilblechgesetz]]). Die Norm
nennt keine Linie und keine Grenzdehnung; nach Vorgabe, nicht
nachgeschlagen, endet sie wie beim Baustahl bei
[[opencivil.material.baustahl#Konstanten|DUKTILITAET]] mal der Fliessdehnung.

## Inhalt

### Profilblechsorte

```python
@dataclass(frozen=True)
class Profilblechsorte
```

Eine Zeile von Tabelle 1, in N/mm².

- `f_yp: float`
- `f_u: float`

### profilblechsorten_zum_anlegen

```python
def profilblechsorten_zum_anlegen() -> List[str]
```

Die Sorten in der Folge, in der neue angelegt werden: die erste, dann die Tabelle.

### profilblech

```python
def profilblech(sorte: str=ERSTES_PROFILBLECH, *, name: Optional[str]=None, praefix: Optional[str]=None, abweichungen: Optional[Mapping[str, Groesse]]=None, symbol_index: str='') -> Baustoff
```

Erzeugt einen Profilblechstahl aus der Sortentabelle.

:param sorte: Bezeichnung aus [[opencivil.material.profilblech#Konstanten|PROFILBLECHSORTEN]], z.B. `'SE 350 G'`.
:param abweichungen: Zahlenwerte, die von der Tabelle abweichen.


## Konstanten

- `TABELLE_1 = 'SIA 264:2014, 3.3.1, Tabelle 1'` – Wo die Sortentabelle steht -- jeder Wert aus ihr nennt diese Stelle.
- `PROFILBLECHSORTEN = {'SE 220 G': Profilblechsorte(220.0, 300.0), 'SE 250 G': Profilblechs…` – Profilblechstahl nach SIA 264:2014, Tabelle 1 -- in ihrer Folge.
- `ERSTES_PROFILBLECH = 'SE 350 G'` – Womit ein neuer Profilblechstahl anfaengt -- siehe Dateikopf.
- `PROFILBLECH_VORLAGEN = (KennwertVorlage(kurzname='f_yp', symbol='f_{yp}', einheit=N_PRO_MM2,…`

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.material.basis]]
- [[opencivil.material.baustahl]]
- [[opencivil.material.betonstahl]]

## Gebraucht von

- [[opencivil.material.arten]]

## Formeln aus diesem Modul

- [[Bemessungswert der Streckgrenze]]
- [[Fliessdehnung]]
- [[Grenzdehnung des Profilblechstahls]]
