---
erzeugt: fd9c623fe469
art: modul
tags: [modul]
---
> [!abstract] opencivil/notizbuch/erzeugen.py
> alle Seiten, die aus dem Code entstehen.
> Paket [[opencivil.notizbuch]] · [Quelltext](../../opencivil/notizbuch/erzeugen.py)

## VERANTWORTUNG

Fuehrt Formelsammlung und Python-Doku zusammen: die Formelseiten verlinken
die Stelle im Code auf die Seite ihres Moduls, und die Modulseiten nennen die
Formeln, die das Modul schreibt. Die Bruecke schreibt, was hier herauskommt
([[opencivil.web.bruecke#notizbuch_schreiben|opencivil.web.bruecke.notizbuch_schreiben]]).

Ein eigenes Modul, weil beide Seiten voneinander wissen muessen -- und weil
`opencivil.notizbuch` beim Import nichts laden darf: die Formelsammlung
braucht daraus die Namensregel.

## Inhalt

### seiten

```python
def seiten() -> List[Seite]
```

Formel-, Themen- und Uebersichtsseiten, dazu je Modul und Paket eine.


## Braucht

- [[opencivil.notizbuch.bibliothek]]
- [[opencivil.notizbuch.formelseiten]]
- [[opencivil.notizbuch.tresor]]

## Gebraucht von

- [[opencivil.web.bruecke]]
