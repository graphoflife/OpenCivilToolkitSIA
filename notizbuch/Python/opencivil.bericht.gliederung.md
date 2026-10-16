---
erzeugt: 91e6a45eb26f
art: modul
tags: [modul]
---
> [!abstract] opencivil/bericht/gliederung.py
> der ganze Bericht als Bloecke.
> Paket [[opencivil.bericht]] · [Quelltext](../../opencivil/bericht/gliederung.py)

## VERANTWORTUNG

Legt fest, was im Bericht steht und in welcher Folge: die Herleitung, die
Formelsammlung, die Nachweise je Platte, die Werte, die fehlenden Eingaben. Als
[[opencivil.core.protokoll#Protokoll|Protokoll]], aus denselben Bloecken, aus denen schon die Herleitung
besteht. Konsole und LaTeX-Dokument setzen nur noch dieses eine Protokoll,
jede mit ihrer Tafel.


## WARUM

Vorher baute jede Darstellung ihre Abschnitte selbst, und sie liefen
auseinander: die Konsole listete die Werte nach Kennung, das Dokument nach
Bezeichnung; die Konsole stellte die Werte vor die Nachweise, das Dokument
dahinter; und beide fassten die Nachweise flach zusammen, ohne Platten und
mit anderen Spalten als der Bildschirm. Ein Bericht in einem weiteren Format
haette eine weitere Kopie gebraucht.


## EIGENSTAENDIG NUTZBAR


```python
from opencivil.bericht.gliederung import bericht
from opencivil.bericht.konsole import protokoll_zeilen
print("\n".join(protokoll_zeilen(bericht(loesung, titel="Decke"))))
```

## Inhalt

### bericht

```python
def bericht(loesung: Loesung, *, titel: str='Berechnung', aufbau: Optional['Aufbau']=None) -> Protokoll
```

Der vollstaendige Bericht einer Loesung; `titel` wird sein Kopftitel.

Mit `aufbau` stehen die Nachweise je Platte da, samt Angaben und
Bewehrung -- wie auf dem Bildschirm. Ohne (ein Rechenwerk, das keine
Platten kennt) in einer Tabelle ohne Plattenueberschrift.

### _abschnitt

```python
def _abschnitt(p: Protokoll, titel: str) -> None
```

Ein Abschnitt des Berichts, als oberste Ueberschrift.

Mit eigenem Namensraum: jede Darstellung ordnet die Bloecke nach
Abschnitten ([[opencivil.core.protokoll#Protokoll.nach_abschnitten|Protokoll.nach_abschnitten]]), und ein Titel ohne
Namensraum gehoerte zum letzten Bauteil der Herleitung -- die Werte
stuenden dann mitten in dessen Abschnitt, sobald es darin zweimal
vorkommt.

### _nachweise

```python
def _nachweise(p: Protokoll, zusammenfassung: Zusammenfassung, aufbau: Optional['Aufbau'], loesung: Loesung) -> None
```

Je Platte dasselbe wie auf dem Bildschirm: Angaben, Bewehrung,
Nachweistabelle, darunter Hinweise und stille Maengel, zuletzt die
Kennzahlen -- die auch ohne Lastfall.

Eines kommt dazu. Auf dem Bildschirm ist ein nicht erfuellter Nachweis
rot hinterlegt und traegt seine Begruendung im Tooltip -- auf Papier
gibt es beides nicht. Darum steht jeder unter der Tabelle mit seiner
Begruendung, sofern ihn nicht schon ein gebuendelter Hinweis erklaert.


## Braucht

- [[opencivil.bericht.formelsammlung]]
- [[opencivil.bericht.zusammenfassung]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.rechenwerk]]
- [[opencivil.projekt]]

## Gebraucht von

- [[opencivil.bericht.konsole]]
- [[opencivil.bericht.latex_dokument]]
- [[opencivil.bericht.markdown]]
