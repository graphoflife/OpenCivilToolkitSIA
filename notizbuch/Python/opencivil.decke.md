---
erzeugt: 725c645d310a
art: modul
tags: [modul]
---
> [!abstract] opencivil/decke/__init__.py
> Stahlbetondecken nach der Streifenmethode.
> Paket [[opencivil]] · [Quelltext](../../opencivil/decke/__init__.py)

Der Rechenkern der App «Decken»: Platten beliebiger Form und Dicke auf
Linienlagern und Stützen, mit Trägern, unter Flächen-,
Linien- und Einzellasten – gerechnet nicht mit finiten Elementen, sondern
nach der Streifenmethode von Hillerborg (Stahlbeton II, 7.2 Platten,
Folien 27 bis 39): jede Last geht in Streifen zweier Richtungen zu den
Lagern, Drillmomente werden nicht gebraucht. Das ist eine
Gleichgewichtslösung – ein unterer Grenzwert der Traglast.

* [[opencivil.decke.geometrie|geometrie]] – Vielecke: Schnitte, Dreiecke und die
  Breite eines Stücks quer zum Streifen.
* [[opencivil.decke.modell|modell]] – was gerechnet wird, in SI.
* [[opencivil.decke.durchlauftraeger|durchlauftraeger]] – ein Streifen als Durchlaufträger:
  elastisch gelöst, dann die Statik mit gleichmässiger Pressung der
  Flächenlager.
* [[opencivil.decke.streifen|streifen]] – die Decke in Streifen und Durchlaufträger
  zerlegt, und worauf jeder liegt.
* [[opencivil.decke.aufteilung|aufteilung]] – welcher Anteil der Last in welche
  Richtung geht.
* [[opencivil.decke.lasten|lasten]] – die Lasten eines Lastfalls auf den
  Streifen.
* [[opencivil.decke.rechnung|rechnung]] – je Fall alle Durchlaufträger, von den
  Feldstreifen über die Träger zu Stützen und Linienlagern.
* [[opencivil.decke.feld|feld]] – was an einer Stelle der Platte wirkt:
  `m_x`, `m_y`, `m_xy`, die Querkräfte, die Biegewiderstände und die
  Lastverteilelemente.

Nur die Standardbibliothek: das Werkzeug rechnet auch im Browser.

## Module

- [[opencivil.decke.aufteilung]] – welcher Teil der Last in welche Richtung geht.
- [[opencivil.decke.baender]] – die Bänder, die eine Decke selbst legt.
- [[opencivil.decke.durchlauftraeger]] – ein Streifen als Durchlaufträger.
- [[opencivil.decke.feld]] – die Schnittkräfte der Platte an einer Stelle.
- [[opencivil.decke.fem]] – die Decke nach der Methode der finiten Elemente.
- [[opencivil.decke.geometrie]] – Vielecke in der Ebene der Decke.
- [[opencivil.decke.herleitung]] – wie eine Decke ihre Rechnung aufschreibt.
- [[opencivil.decke.lasten]] – die Lasten eines Lastfalls auf den Streifen.
- [[opencivil.decke.modell]] – was gerechnet wird: die Decke in SI.
- [[opencivil.decke.rechnung]] – die Streifenmethode, Fall für Fall.
- [[opencivil.decke.richtungen]] – die zwei Richtungen, die eine Platte selbst wählt.
- [[opencivil.decke.schnitt]] – die Schnittkräfte längs eines Schnitts.
- [[opencivil.decke.streifen]] – die Decke in Streifen zerlegt.
- [[opencivil.decke.werk]] – die Decke im Rechenwerk.
