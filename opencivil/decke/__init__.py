"""
opencivil/decke -- Stahlbetondecken nach der Streifenmethode.

Der Rechenkern der App «Decken»: Platten beliebiger Form und Dicke auf
Linienlagern und Stützen, mit versteckten Unterzügen, unter Flächen-,
Linien- und Einzellasten -- gerechnet nicht mit finiten Elementen, sondern
nach der Streifenmethode von Hillerborg (Stahlbeton II, 7.2 Platten,
Folien 27 bis 39): jede Last geht in Streifen zweier Richtungen zu den
Lagern, Drillmomente werden nicht gebraucht. Das ist eine
Gleichgewichtslösung -- ein unterer Grenzwert der Traglast.

* :mod:`~opencivil.decke.geometrie` -- Vielecke: Schnitte, Dreiecke und die
  Breite eines Stücks quer zum Streifen.
* :mod:`~opencivil.decke.modell` -- was gerechnet wird, in SI.
* :mod:`~opencivil.decke.traeger` -- ein Streifen als Durchlaufträger:
  elastisch gelöst, dann die Statik mit gleichmässiger Pressung der
  Flächenlager.
* :mod:`~opencivil.decke.streifen` -- die Decke in Streifen und Träger
  zerlegt, und worauf jeder liegt.
* :mod:`~opencivil.decke.aufteilung` -- welcher Anteil der Last in welche
  Richtung geht.
* :mod:`~opencivil.decke.lasten` -- die Lasten eines Lastfalls auf den
  Streifen.
* :mod:`~opencivil.decke.rechnung` -- je Fall alle Träger, von den
  Feldstreifen über die Unterzüge zu Stützen und Linienlagern.
* :mod:`~opencivil.decke.feld` -- was an einer Stelle der Platte wirkt:
  ``m_x``, ``m_y``, ``m_xy``, die Querkräfte, die Biegewiderstände und die
  Lastverteilelemente.

Nur die Standardbibliothek: das Werkzeug rechnet auch im Browser.
"""
