---
erzeugt: d1723c079d96
art: modul
tags: [modul]
---
> [!abstract] opencivil/gleichungen/__init__.py
> Analytische Gleichungen, Zeile fuer Zeile.
> Paket [[opencivil]] · [Quelltext](../../opencivil/gleichungen/__init__.py)

Ein Blatt wie in Mathcad: jede Zeile eine Definition (`b = 2a + 1\,\mathrm{m}`),
eine Auswertung (`a \cdot b =`), ein Projektwert (`f_{cd}` aus einem
Baustoff) oder ein Text. Gerechnet wird mit Einheiten ([[opencivil.core.einheiten#Groesse|Groesse]]),
dargestellt wie jede Herleitung: Symbol, Formel, Zahlen, Ergebnis.

* [[opencivil.gleichungen.ausdruck|.ausdruck]] -- Zerlegen, Auswerten und Darstellen einer Zeile.
* [[opencivil.gleichungen.blatt|.blatt]]    -- das Blatt als Berechnung im Rechenwerk.

## Module

- [[opencivil.gleichungen.ausdruck]] – eine Zeile LaTeX: zerlegen, rechnen, setzen.
- [[opencivil.gleichungen.blatt]] – ein Blatt Gleichungen als Berechnung.
