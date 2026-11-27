"""
opencivil/erdbeben -- Erdbeben nach SIA 261:2020, Kapitel 16.

    ersatzkraft.py   das Ersatzkraftverfahren (16.5.2): ein Gebaeude mit
                     Geschossen, jedes mit seinem Kern, je Hauptrichtung die
                     Grundschwingzeit, die Ersatzkraft und ihre Verteilung
                     auf die Geschosse und die Teile des Kerns
    kern.py          der Kern eines Geschosses: seine getrennten Teile, je
                     um ihren Schwerpunkt, und ihre Traegheitsmomente
    kragarm.py       der Kern als Kragarm: Querkraft, Moment und, Geschoss
                     fuer Geschoss, die Auslenkung des Dachs
"""
