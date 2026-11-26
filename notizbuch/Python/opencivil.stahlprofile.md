---
erzeugt: a36d87d8eaf2
art: modul
tags: [modul]
---
> [!abstract] opencivil/stahlprofile/__init__.py
> die Stahlprofile: ihre Formen, welche es gibt, wie eines im Querschnitt liegt.
> Paket [[opencivil]] · [Quelltext](../../opencivil/stahlprofile/__init__.py)

Das Balkensystem rechnet mit ihren Kennwerten, die Querschnittsanalyse mit
ihrem Umriss -- darum stehen sie in keinem der beiden Pakete (seit
2026-11-26; bis dahin in [[opencivil.stabwerk]]).

* [[opencivil.stahlprofile.formen|formen]] -- je Form die Masse, die Formeln
  fuer `A`, `I_y`, `I_z` und `I_T` und der Umriss. Die Formen sind
  Vorlagen von Stabquerschnitten ([[opencivil.stabwerk.querschnitte#Stabvorlage|opencivil.stabwerk.querschnitte.Stabvorlage]]).
* [[opencivil.stahlprofile.tabelle|tabelle]] -- welche Profile es gibt, je
  Reihe mit ihren Massen.
* [[opencivil.stahlprofile.lage|lage]] -- ein Profil im gezeichneten
  Querschnitt: an seiner Mitte, gedreht und gespiegelt.

## Module

- [[opencivil.stahlprofile.bleche]] – die Bleche eines Stahlprofils, fuer seine Querschnittsklasse.
- [[opencivil.stahlprofile.formen]] – die Formen der Stahlprofile, mit ihren Formeln.
- [[opencivil.stahlprofile.lage]] – ein Stahlprofil im gezeichneten Querschnitt.
- [[opencivil.stahlprofile.tabelle]] – welche Stahlprofile es gibt, mit ihren Massen.
