---
erzeugt: 6b39e86f5344
art: modul
tags: [modul]
---
> [!abstract] opencivil/material/baustahl.py
> Baustahl nach SIA 263:2013.
> Paket [[opencivil.material]] · [Quelltext](../../opencivil/material/baustahl.py)

## VERANTWORTUNG

Sortentabelle und Kennwerte fuer Baustahl, aufgebaut wie Beton und
Betonstahl ([[opencivil.material.basis]]): jeder Kennwert ist eine eigene,
einzeln ueberschreibbare Berechnung.


## DIE SORTENTABELLE

SIA 263:2013, 3.2.2.3, Tabelle 1 nennt fuer S235, S275, S355 und S460 die
Streckgrenze, die Fliessschubspannung und die Zugfestigkeit, je fuer Dicken
bis 40 mm und fuer 40 mm \< t ≤ 100 mm. Beide Spalten stehen als Kennwerte da;
welche gilt, haengt an der Dicke des Erzeugnisses, nicht am Material. Am
2026-11-15 gegen die gedruckte Tabelle geprueft.


## DIE NORMVORGABEN

Dichte, Elastizitaetsmodul, Schubmodul und Querdehnungszahl stehen in
3.2.2.1, die Widerstandsbeiwerte in 4.1.3. Die Waermedehnzahl (3.2.2.2) fehlt
noch: das Werkzeug kennt keine Temperatur als Einheit, und keine Rechnung
braucht sie.


## DAS GESETZ

Fuer die Spannung-Dehnung-Linie ([[opencivil.querschnitt.werkstoffgesetz#Baustahlgesetz|Baustahlgesetz]])
kommen der Bemessungswert der Streckgrenze `f_yd = f_y / gamma_M1` (4.1.1,
Gleichung (1), mit 4.1.3) und eine Grenzdehnung dazu. Die Norm nennt keine
Linie und keine Grenzdehnung; nach Vorgabe, nicht nachgeschlagen, endet sie
bei [[opencivil.material.baustahl#Konstanten|DUKTILITAET]] mal der Fliessdehnung – so viel verlangt 3.2.2.4
mindestens, wo plastisch gerechnet wird, und die Sorten der Tabelle 1
erfuellen es.


## EIGENSTAENDIG NUTZBAR


```python
from opencivil.core.rechenwerk import Rechenwerk
from opencivil.material.baustahl import baustahl

werk = Rechenwerk()
s355 = baustahl("S355").ins_rechenwerk(werk)
print(werk.loese(s355.id_von("eps_y")).wert(s355.id_von("eps_y")))
```

## Inhalt

### Baustahlsorte

```python
@dataclass(frozen=True)
class Baustahlsorte
```

Eine Zeile von Tabelle 1, in N/mm² – links bis 40 mm Dicke, rechts darueber.

- `f_y: float`
- `tau_y: float`
- `f_u: float`
- `f_y_dick: float`
- `tau_y_dick: float`
- `f_u_dick: float`

### baustahlsorten_zum_anlegen

```python
def baustahlsorten_zum_anlegen() -> List[str]
```

Die Sorten in der Reihenfolge, in der neue angelegt werden – wie in Tabelle 1.

### baustahl

```python
def baustahl(sorte: str=ERSTER_BAUSTAHL, *, name: Optional[str]=None, praefix: Optional[str]=None, abweichungen: Optional[Mapping[str, Groesse]]=None, symbol_index: str='') -> Baustoff
```

Erzeugt einen Baustahl aus der Sortentabelle.

:param sorte: Bezeichnung aus [[opencivil.material.baustahl#Konstanten|BAUSTAHLSORTEN]], z.B. `'S355'`.
:param abweichungen: Zahlenwerte, die von der Tabelle abweichen.


## Konstanten

- `TABELLE_1 = 'SIA 263:2013, 3.2.2.3, Tabelle 1'` – Wo die Sortentabelle steht – jeder Wert aus ihr nennt diese Stelle.
- `BAUSTAHLSORTEN = {'S235': Baustahlsorte(235.0, 135.0, 360.0, 215.0, 124.0, 340.0), 'S2…` – Baustahlsorten nach SIA 263:2013, Tabelle 1.
- `ERSTER_BAUSTAHL = 'S235'` – Womit ein neuer Baustahl anfaengt: die Folge der Tabelle.
- `DICK = 'für 40 mm < t ≤ 100 mm'` – Was ueber 40 mm Dicke gilt, steht unter demselben Zeichen mit `t>40` oben.
- `DUKTILITAET = 15.0` – Wie viele Fliessdehnungen weit die Linie reicht: das Verhaeltnis von Bruch- zu Fliessdehnung, das SIA 263:2013, 3.2.2.4 fuer die plastischen Verfahren mindestens verlangt – als Grenzdehnung nach Vorgabe, nicht nachgeschlagen.
- `BAUSTAHL_VORLAGEN = (_tabellenwert('f_y', 'f_y', 'Streckgrenze'), _tabellenwert('tau_y', …`

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.material.basis]]
- [[opencivil.material.betonstahl]]

## Gebraucht von

- [[opencivil.material.arten]]
- [[opencivil.material.profilblech]]
- [[opencivil.projekt.projekt]]

## Formeln aus diesem Modul

- [[Bemessungswert der Streckgrenze]]
- [[Fliessdehnung]]
- [[Grenzdehnung des Baustahls]]
