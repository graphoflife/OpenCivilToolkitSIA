---
erzeugt: b580b6239516
art: modul
tags: [modul]
---
> [!abstract] opencivil/spannungsanalyse/herleitung.py
> wie eine Linie entstand.
> Paket [[opencivil.spannungsanalyse]] · [Quelltext](../../opencivil/spannungsanalyse/herleitung.py)

## VERANTWORTUNG

Die Herleitung einer Linie und ihres Moduls, mit den Zahlen des Falls --
daraus bildet die Formelsammlung ihr Thema ([[opencivil.spannungsanalyse.herleitung#Konstanten|THEMA]]). Was nur die Art
des Bauteils weiss, schreibt das Paar ([[opencivil.spannungsanalyse.linie#Paar|Paar]]).

## Inhalt

### herleitung

```python
def herleitung(p: Protokoll, fall, paar: Paar, linie: Linie, werte: Mapping[str, 'Wert'], raum: str, modul: Optional[Modullinie]=None) -> None
```

Wie die Linie entstand -- mit den Zahlen dieses Falls, und ohne sie in der
Formelsammlung, die daraus «Spannung-Dehnung-Analyse» bildet. Mit
`modul` dazu, wie aus ihr der aequivalente E-Modul wird.

`paar` ist das Loeserpaar einer Platte oder eines gezeichneten
Querschnitts. Was nur die Art des Bauteils weiss -- die Tiefe, der Riss,
die Dehnung am Ende, der reine Betonquerschnitt --, schreibt es selbst
(`tiefe`, `herleitung_riss`, `herleitung_dehnung_am_ende`,
`herleitung_bezug`); der Rest ist derselbe Text.

### _herleitung_modul

```python
def _herleitung_modul(p: Protokoll, w: Zwischenwerte, modul: Modullinie, *, bezug: Callable[[], 'Wert'], bezugsort: str) -> None
```

Der aequivalente Modul: der reine Betonquerschnitt, die Formel und der
Modul an den Ecken der Linie -- jede Zeile mit Kraft und Verformung, also
von Hand nachzurechnen. `bezug` schreibt den reinen Betonquerschnitt
hin, wie ihn die Art des Bauteils kennt, und gibt ihn zurueck;
`bezugsort` sagt, wo die Mitteldehnung gilt.


## Konstanten

- `THEMA = 'Spannung-Dehnung-Analyse'` – Unter diesem Thema steht in der Formelsammlung, wie die Linien entstehen.

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.material.basis]]
- [[opencivil.material.betonstahl]]
- [[opencivil.querschnitt.gesetzwahl]]
- [[opencivil.querschnitt.werkstoffgesetz]]
- [[opencivil.spannungsanalyse.art]]
- [[opencivil.spannungsanalyse.linie]]
- [[opencivil.spannungsanalyse.modul]]

## Gebraucht von

- [[opencivil.spannungsanalyse]]
- [[opencivil.spannungsanalyse.analysen]]

## Formeln aus diesem Modul

- [[Äquivalenter E-Modul über dem Moment]] · `_herleitung_modul`
- [[Äquivalenter E-Modul über der Normalkraft]] · `_herleitung_modul`
- [[Fliessdehnung]] · `herleitung`
- [[Grenzdehnungen am Ende der Linie]] · `herleitung`
- [[Grösste Krümmung]] · `herleitung`
- [[Wirksamer Elastizitätsmodul]] · `herleitung`
