---
erzeugt: e7d1285316ad
art: modul
tags: [modul]
---
> [!abstract] opencivil/bewehrungssuche/__init__.py
> die Bewehrung suchen statt sie zu setzen.
> Paket [[opencivil]] · [Quelltext](../../opencivil/bewehrungssuche/__init__.py)

Vier Teile, jeder mit einer Frage:

* [[opencivil.bewehrungssuche.bewertung|.bewertung]] -- wie weit ist eine Bewehrung vom Ziel, und gegen
  welche Platte wird gesucht?
* [[opencivil.bewehrungssuche.laengs|.laengs]] -- die kleinste Laengsbewehrung, die alles erfuellt.
* [[opencivil.bewehrungssuche.dicke|.dicke]] -- die duennste Platte, bei der die Laengssuche aufgeht.
* [[opencivil.bewehrungssuche.buegel|.buegel]] -- die duennsten Buegel fuer den Querkraftnachweis.

Nach aussen gilt, was hier steht; die Teile duerfen sich innen umbauen.

## Module

- [[opencivil.bewehrungssuche.bewertung]] – wie weit eine Bewehrung vom Ziel ist.
- [[opencivil.bewehrungssuche.buegel]] – die Querkraftbewehrung suchen.
- [[opencivil.bewehrungssuche.dicke]] – die duennste Platte suchen.
- [[opencivil.bewehrungssuche.laengs]] – die Laengsbewehrung suchen.

## Braucht

- [[opencivil.bewehrungssuche.bewertung]]
- [[opencivil.bewehrungssuche.buegel]]
- [[opencivil.bewehrungssuche.dicke]]
- [[opencivil.bewehrungssuche.laengs]]

## Gebraucht von

- [[opencivil.web.api]]
- [[opencivil.web.dienst]]
