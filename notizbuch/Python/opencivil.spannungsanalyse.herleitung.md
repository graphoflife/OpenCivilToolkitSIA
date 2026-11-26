---
erzeugt: 2ab59404358c
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
def herleitung(p: Protokoll, fall, paar: Paar, linie: Linie, werte: Mapping[str, 'Wert'], raum: str, modul: Optional[Modullinie]=None, raender: Tuple[str, str]=('oben', 'unten')) -> None
```

Wie die Linie entstand -- mit den Zahlen dieses Falls, und ohne sie in der
Formelsammlung, die daraus «Spannung-Dehnung-Analyse» bildet. Mit
`modul` dazu, wie aus ihr der aequivalente E-Modul wird. `raender`
nennt die Raender bei z = 0 und z = h, wie die Analyse sie nennt
([[opencivil.spannungsanalyse.analysen#Analyse|raender]]): bei Zug
links heisst die Randdehnung bei z = 0 «rechts», nicht «oben».

`paar` ist das Loeserpaar einer Platte oder eines gezeichneten
Querschnitts. Was vor dem Ende der Linie steht -- die Gesetze, den Riss,
das Fliessen, die Grenzdehnungen --, schreibt das Paar
(`herleitung_gesetze`): mit Beton alle gleich
([[opencivil.spannungsanalyse.riss#Bruttoriss|Bruttoriss]]), ohne Beton ohne
Riss ([[opencivil.spannungsanalyse.rissfrei#RissfreiesPaar|RissfreiesPaar]]).
Was nur die Art des Bauteils weiss -- die Dehnung am Ende, der Bezug des
Moduls --, schreibt es ebenso selbst. Der Rest ist derselbe Text.

### _herleitung_modul

```python
def _herleitung_modul(p: Protokoll, w: Zwischenwerte, modul: Modullinie, paar: Paar, A: 'Wert', I: 'Wert') -> None
```

Der aequivalente Modul: sein Bezug, die Formel und der Modul an den Ecken
der Linie -- jede Zeile mit Kraft und Verformung, also von Hand
nachzurechnen. Beim Stahlbeton ist der Bezug der reine Betonquerschnitt,
der Bruttoquerschnitt des Risses mit seinem `A` und `I`; ohne Beton
der Querschnitt selbst ([[opencivil.spannungsanalyse.linie#Paar.modulbezug|modulbezug]]).


## Konstanten

- `THEMA = 'Spannung-Dehnung-Analyse'` – Unter diesem Thema steht in der Formelsammlung, wie die Linien entstehen.

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.spannungsanalyse.linie]]
- [[opencivil.spannungsanalyse.modul]]

## Gebraucht von

- [[opencivil.spannungsanalyse]]
- [[opencivil.spannungsanalyse.analysen]]

## Formeln aus diesem Modul

- [[Äquivalenter E-Modul über dem Moment]] · `_herleitung_modul`
- [[Äquivalenter E-Modul über der Normalkraft]] · `_herleitung_modul`
- [[Grösste Krümmung]] · `herleitung`
