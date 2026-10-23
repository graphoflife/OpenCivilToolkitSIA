---
erzeugt: a75fe6fdc13f
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/aufbau/balkensystem.py
> ein Balkensystem wird Rechnung.
> Paket [[opencivil.projekt.aufbau]] · [Quelltext](../../opencivil/projekt/aufbau/balkensystem.py)

## VERANTWORTUNG

Aus einem [[opencivil.projekt.balkensystem#BalkensystemEintrag|BalkensystemEintrag]] das
Stabwerk mit aufgeloesten Querschnitten ([[opencivil.projekt.aufbau.balkensystem#bauen|bauen]]). Ein Querschnitt kann
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

Ein Balkensystem: das Stabwerk der Beschreibung, seine Querschnitte
aufgeloest. Hart scheitert nur ein Verweis, den es nicht gibt -- ein
Material, eine Platte, eine Querschnittsanalyse --; was dem System selbst
fehlt, steht in seinen Meldungen, und der Rest des Projekts rechnet.

### _stabquerschnitt

```python
def _stabquerschnitt(q: StabquerschnittEintrag, aufbau: Aufbau, wo: str) -> Stabquerschnitt
```

Woher A und I eines Querschnitts kommen -- die Platte oder Analyse dazu muss es geben.

### _paare

```python
def _paare(eintrag: BalkensystemEintrag, modell: Modell, aufbau: Aufbau) -> Tuple[Dict[str, Tuple[str, str]], List[Meldung]]
```

Je tragenden Stab Querschnitt und Material -- «gemäss Querschnitt» wird
zum Material der Platte oder Analyse. Bringt der Querschnitt keines mit,
sagt es eine Meldung, und das System rechnet nicht.

### _material_des_querschnitts

```python
def _material_des_querschnitts(q: StabquerschnittEintrag, aufbau: Aufbau) -> Tuple[str, str]
```

Die Kennung des Materials, das ein Querschnitt mitbringt: der Beton einer
Platte, das eine Material der Flaechen einer Analyse. Sonst leer, und
der zweite Teil sagt, warum.


## Braucht

- [[opencivil.material.basis]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.balkensystem]]
- [[opencivil.projekt.lesen]]
- [[opencivil.stabwerk.rechnung]]
- [[opencivil.stabwerk.system]]

## Gebraucht von

- [[opencivil.projekt.aufbau]]
