"""
opencivil/stahlprofile -- die Stahlprofile: ihre Formen, welche es gibt, wie eines im Querschnitt liegt.

Das Balkensystem rechnet mit ihren Kennwerten, die Querschnittsanalyse mit
ihrem Umriss -- darum stehen sie in keinem der beiden Pakete (seit
2026-11-26; bis dahin in :mod:`opencivil.stabwerk`).

* :mod:`~opencivil.stahlprofile.formen` -- je Form die Masse, die Formeln
  fuer ``A``, ``I_y``, ``I_z`` und ``I_T`` und der Umriss. Die Formen sind
  Vorlagen von Stabquerschnitten (:class:`opencivil.stabwerk.querschnitte.Stabvorlage`).
* :mod:`~opencivil.stahlprofile.tabelle` -- welche Profile es gibt, je
  Reihe mit ihren Massen.
* :mod:`~opencivil.stahlprofile.lage` -- ein Profil im gezeichneten
  Querschnitt: an seiner Mitte, gedreht und gespiegelt.
"""
