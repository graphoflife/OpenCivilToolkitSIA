---
erzeugt: 5252e1825659
art: modul
tags: [modul]
---
> [!abstract] opencivil/erdbeben/__init__.py
> Erdbeben nach SIA 261:2020, Kapitel 16.
> Paket [[opencivil]] · [Quelltext](../../opencivil/erdbeben/__init__.py)

```
ersatzkraft.py   das Ersatzkraftverfahren (16.5.2): ein Gebaeude mit
                 Geschossen, jedes mit seinem Kern, je Hauptrichtung die
                 Grundschwingzeit, die Ersatzkraft und ihre Verteilung
                 auf die Geschosse und die Teile des Kerns
kern.py          der Kern eines Geschosses: seine getrennten Teile, je
                 um ihren Schwerpunkt, und ihre Traegheitsmomente
kragarm.py       der Kern als Kragarm: Querkraft, Moment und, Geschoss
                 fuer Geschoss, die Auslenkung des Dachs
```

## Module

- [[opencivil.erdbeben.ersatzkraft]] – das Ersatzkraftverfahren nach SIA 261:2020, 16.5.2.
- [[opencivil.erdbeben.kern]] – der Kern eines Geschosses: seine Teile, je um ihren Schwerpunkt.
- [[opencivil.erdbeben.kragarm]] – der Kern als Kragarm: Querkraft, Moment und Auslenkung.
