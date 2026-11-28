---
erzeugt: 6d7e210b1d9f
art: modul
tags: [modul]
---
> [!abstract] opencivil/mauerwerk/uebersicht.py
> was die Zusammenfassung einer Wand über ihren Nachweisen zeigt.
> Paket [[opencivil.mauerwerk]] · [Quelltext](../../opencivil/mauerwerk/uebersicht.py)

## VERANTWORTUNG

Die Angaben zur Wand – ihr Mauerwerk, wie es gemauert ist, ihre Dicke
([[opencivil.mauerwerk.uebersicht#angaben|angaben]]) – und die Tabelle ihrer Bemessungswerte: je Wert der
des Mauerwerks und der, mit dem die Wand rechnet, im Verband mit seinem
Faktor ([[opencivil.mauerwerk.uebersicht#wertetabelle|wertetabelle]]). Beides aus dem Befund der Wand
([[opencivil.mauerwerk.werk#Wandbefund|Wandbefund]]). Bis 2026-11-28 stellte die
Oberfläche diese Tabelle selbst zusammen; seit die Wand Nachweise führt,
steht sie wie bei jedem Bauteil über deren Tabelle, auch im Bericht.

## Inhalt

### angaben

```python
def angaben(befund: Wandbefund) -> GleichungBlock
```

Was über der Tabelle steht: Mauerwerk, wie gemauert – im Verband mit
seinem Faktor, den μ_d nicht trägt –, Stossfugen und Dicke.

### wertetabelle

```python
def wertetabelle(wand: Mauerwerkswand, befund: Wandbefund) -> TabellenBlock
```

Die Bemessungswerte des Mauerwerks und der Wand, mit Beschreibung und
Zeichen des Mauerwerks – vollfugig f_yd aus dessen f_yd,v.


## Konstanten

- `WERTE = (('f_xd', 2), ('f_yd', 2), ('E_xd', 0), ('G_d', 0), ('mu_d', 2))` – Welche Bemessungswerte die Tabelle zeigt, je mit seinen Stellen.

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.mauerwerk.kennwerte]]
- [[opencivil.mauerwerk.werk]]

## Gebraucht von

- [[opencivil.bericht.zusammenfassung]]
