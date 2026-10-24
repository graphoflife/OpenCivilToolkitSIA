---
erzeugt: f98b619bb383
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/aufbau/balkensystem.py
> ein Balkensystem wird Rechnung.
> Paket [[opencivil.projekt.aufbau]] · [Quelltext](../../opencivil/projekt/aufbau/balkensystem.py)

## VERANTWORTUNG

Aus einem [[opencivil.projekt.balkensystem#BalkensystemEintrag|BalkensystemEintrag]] das
Stabwerk mit aufgeloesten Materialien und Querschnitten ([[opencivil.projekt.aufbau.balkensystem#bauen|bauen]]). Ein
Material ist ein Beton des Projekts oder ein eigenes. Ein Querschnitt kann
eine Platte oder eine Querschnittsanalyse des Projekts nehmen; die muessen
dann schon gebaut sein -- darum kommt das Balkensystem in
[[opencivil.projekt.aufbau#Konstanten|BAUTEILE]] nach ihnen. Von dort kommt auch
das Material einer Linie «gemäss Querschnitt»: der Beton der Platte oder
der Analyse.

## Inhalt

### bauen

```python
def bauen(art: 'Bauteilart', eintrag: BalkensystemEintrag, aufbau: Aufbau) -> Bauteil
```

Ein Balkensystem: das Stabwerk der Beschreibung, seine Materialien und
Querschnitte aufgeloest. Hart scheitert nur ein Verweis, den es nicht
gibt -- ein Beton, eine Platte, eine Querschnittsanalyse --; was dem
System selbst fehlt, steht in seinen Meldungen, und der Rest des
Projekts rechnet.

### _stabquerschnitt

```python
def _stabquerschnitt(q: StabquerschnittEintrag, aufbau: Aufbau, wo: str) -> Stabquerschnitt
```

Woher A und I eines Querschnitts kommen -- die Platte oder Analyse dazu muss es geben.

### _paare

```python
def _paare(eintrag: BalkensystemEintrag, modell: Modell, aufbau: Aufbau, wo: str) -> Tuple[Dict[str, Tuple[str, Stabmaterial]], List[Meldung]]
```

Je tragenden Stab sein Querschnitt und sein Material, aufgeloest --
«gemäss Querschnitt» wird zum Beton der Platte oder Analyse. Traegt das
Material nicht, sagt es eine Meldung, und das System rechnet nicht.

### _beton

```python
def _beton(kennung: str, aufbau: Aufbau, wo: str) -> Baustoff
```

Ein Beton des Projekts -- einen Verweis ins Leere gibt es nicht.

### _stabmaterial

```python
def _stabmaterial(m: StabmaterialEintrag, aufbau: Aufbau, wo: str) -> Tuple[Optional[Stabmaterial], str]
```

Ein Material des Systems, aufgeloest: ein Beton des Projekts oder ein
eigenes. Traegt es nicht, ist es `None`, und der zweite Teil sagt
warum -- klein beginnend, er folgt auf ein «aber».

### _material_des_querschnitts

```python
def _material_des_querschnitts(q: StabquerschnittEintrag, aufbau: Aufbau) -> Tuple[Optional[Stabmaterial], str]
```

Das Material, das ein Querschnitt mitbringt: der Beton einer Platte, das
eine Material der Flaechen einer Analyse. Sonst `None`, und der zweite
Teil sagt, warum.


## Braucht

- [[opencivil.material.basis]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.balkensystem]]
- [[opencivil.projekt.lesen]]
- [[opencivil.spannungsanalyse.modul]]
- [[opencivil.stabwerk.rechnung]]
- [[opencivil.stabwerk.system]]

## Gebraucht von

- [[opencivil.projekt.aufbau]]
