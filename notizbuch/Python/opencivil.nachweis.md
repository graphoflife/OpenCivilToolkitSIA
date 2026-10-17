---
erzeugt: 2afd88c4fce6
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/__init__.py
> die Nachweise der Platte und des gezeichneten Querschnitts.
> Paket [[opencivil]] · [Quelltext](../../opencivil/nachweis/__init__.py)

Jeder Nachweis ist eine Berechnung im Rechenwerk: er liest Werte, schreibt
seine Herleitung ins Protokoll und faellt je Fall ein Urteil mit
Erfuellungsgrad. Dazu die Bausteine, die mehrere teilen: der
Querschnittsloeser, die Resistenzlinien, der Dehnungsfaecher und die
Rechenwahl, mit der jedes Kapitel waehlt, womit es rechnet.

## Module

- [[opencivil.nachweis.biegung_normalkraft]] – Nachweis für Biegung mit Normalkraft.
- [[opencivil.nachweis.dehnungsfaecher]] – Die zulaessigen Dehnungsebenen einer Platte.
- [[opencivil.nachweis.duktilitaet]] – Duktilitaetsnachweis ueber die Druckzonenhoehe.
- [[opencivil.nachweis.fehlende_bewehrung]] – Nachweise, die mangels Bewehrung entfallen.
- [[opencivil.nachweis.gebrauchsebene]] – die Dehnungsebene des gezeichneten Querschnitts unter Gebrauchslast.
- [[opencivil.nachweis.handrechnung]] – Eckpunkte der Resistenzlinie von Hand.
- [[opencivil.nachweis.kennzahlen]] – was eine Platte aufnimmt, ohne Einwirkung.
- [[opencivil.nachweis.knicken]] – Nachweis am verformten System.
- [[opencivil.nachweis.linie]] – Geometrie einer geschlossenen M-N-Linie.
- [[opencivil.nachweis.mindestbewehrung]] – Nachweise gegen sprödes Versagen.
- [[opencivil.nachweis.qa_gebrauch]] – Gebrauchsnachweise des gezeichneten Querschnitts.
- [[opencivil.nachweis.qa_knicken]] – Knicken am gezeichneten Querschnitt.
- [[opencivil.nachweis.querkraft]] – Querkraftnachweis.
- [[opencivil.nachweis.querschnittsloeser]] – Dehnungsebene zu gegebenen Schnittgrössen.
- [[opencivil.nachweis.rechenwahl]] – womit ein Kapitel rechnet.
- [[opencivil.nachweis.resistenzlinie]] – die Linie, gegen die der M-N-Nachweis haelt.
- [[opencivil.nachweis.richtungsnachweise]] – Duktilitaet und sproedes Versagen des gezeichneten Querschnitts.
- [[opencivil.nachweis.rissanforderung]] – die Anforderung an die Rissbildung.
- [[opencivil.nachweis.rissgroessen]] – wann der Beton reisst.
- [[opencivil.nachweis.schiefe_biegung]] – Biegung und Normalkraft am gezeichneten Querschnitt.
- [[opencivil.nachweis.schubwandnachweis]] – Querkraft und Torsion am gezeichneten Querschnitt.
- [[opencivil.nachweis.spannungsbegrenzung]] – Stahlspannung unter Gebrauchslasten.
- [[opencivil.nachweis.sproedes_versagen]] – Mindestbewehrung gegen sprödes Versagen.
- [[opencivil.nachweis.stabgrenzen]] – die zulaessige Stahlspannung je Stab des gezeichneten Querschnitts.
- [[opencivil.nachweis.verformung]] – die Durchbiegung der Platte.
- [[opencivil.nachweis.zustand2]] – Der gerissene Querschnitt, linear elastisch.
