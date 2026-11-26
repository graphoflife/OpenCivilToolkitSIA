---
erzeugt: f64ab5308c6c
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/qa_stahl_stabilitaet.py
> Knicken und Kippen eines Stahlstabs nach SIA 263:2013.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/qa_stahl_stabilitaet.py)

## VERANTWORTUNG

Je Stabilitaetsfall der Querschnittsanalyse ein Nachweis mit seiner
Herleitung; gerechnet wird in [[opencivil.stahlbau.stabilitaet]]. Der
Reihe nach: die Klasse im Fall, die Widerstaende nach ihr, das Knicken je
Achse, das Kippen um die starke Achse, dann das Zusammenwirken -- (50) und
(51) in den Klassen 1 bis 3, (62) und (63) in Klasse 4 -- und der
Erfuellungsgrad wie in der Tragsicherheit: die Normalkraft bleibt, die
Momente wachsen. Ohne Moment steht die Normalkraft gegen den kleineren
Knickwiderstand.


## WAS FEHLT -- GRAU

Was [[opencivil.stahlbau.stabilitaet#Ergebnis|fehlt]] nennt: eine
Knickspannungskurve, wo der Querschnitt nicht aus einem einzigen Profil
besteht und keine gewaehlt ist; das Kippen eines Querschnitts, den Anhang B
nicht kennt; ein Rundrohr der Klasse 4.


## VORZEICHEN

N \< 0 Druck; M_y > 0 zieht unten, M_z > 0 links -- um den Schwerpunkt.

## Inhalt

### _seite_der

```python
def _seite_der(g: wd.Glied, faktor: float) -> Zugseite
```

Die Seite, die ein Glied bei `λ` zieht.

### StahlStabilitaetQA

```python
class StahlStabilitaetQA(Nachweis)
```

Knicken und Kippen eines Stahlstabs, je Fall -- siehe Dateikopf.

- `THEMA = 'Knicken und Kippen'`
- `ART = 'Stab'`

#### StahlStabilitaetQA.pruefe

```python
def pruefe(self, e: Eingaben, p: Protokoll)
```

#### StahlStabilitaetQA._urteil

```python
def _urteil(self, p: Protokoll, werte: Zwischenwerte, r: '_Herleitung', d_grad: WertDef, fall: st.Stabfall) -> NachweisUrteil
```

Der Vergleich: die Momente gegen ihren Widerstand -- ohne Moment die Normalkraft.

### _einwirkung

```python
def _einwirkung(p: Protokoll, biegung: Biegung, fall: st.Stabfall) -> None
```

Die Einwirkung und der Stab als Tabelle -- einachsig ohne M_z.

### _Herleitung

```python
class _Herleitung
```

Die Herleitung eines Falls -- Schritt fuer Schritt, mit den Werten, die sie teilen.

#### _Herleitung.seiten

```python
def seiten(self) -> List[Zugseite]
```

Die Seiten, deren Biegewiderstand eine Gleichung braucht.

#### _Herleitung.widerstaende

```python
def widerstaende(self) -> None
```

#### _Herleitung._biegung

```python
def _biegung(self, seite: Zugseite) -> None
```

Der Biegewiderstand zu einer Seite, nach der Klasse.

#### _Herleitung.knicken

```python
def knicken(self, achse: str) -> None
```

#### _Herleitung.kippen

```python
def kippen(self) -> None
```

#### _Herleitung._druckgurt

```python
def _druckgurt(self, gurt: st.Druckgurt) -> Wert
```

Der Druckgurt nach Figur 40 -- sein Traegheitsradius.

#### _Herleitung._omega

```python
def _omega(self, achse: str) -> Wert
```

`ω` um `achse` -- beim ersten Mal mit seiner Formel.

#### _Herleitung.gleichung_50

```python
def gleichung_50(self) -> None
```

#### _Herleitung.gleichung_51

```python
def gleichung_51(self) -> None
```

#### _Herleitung.kippen_allein

```python
def kippen_allein(self) -> None
```

#### _Herleitung.gleichungen_62

```python
def gleichungen_62(self) -> None
```


## Konstanten

- `ABMINDERUNG = 'Abminderungsfaktor beim Knicken und Kippen'` – Der Name der Formel, die Knicken und Kippen beide schreiben.
- `_WIE = {1: 'plastisch', 2: 'plastisch', 3: 'elastisch (5.2.9)', 4: 'am wirks…` – Wie die Klassen rechnen.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.nachweis]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.nachweis.qa_stahl]]
- [[opencivil.nachweis.qa_stahl_kennzahlen]]
- [[opencivil.nachweis.qa_stahl_werte]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.biegung]]
- [[opencivil.querschnitt.zugseite]]
- [[opencivil.stahlbau.querschnitt]]
- [[opencivil.stahlbau.stabilitaet]]
- [[opencivil.stahlbau.widerstand]]
- [[opencivil.stahlprofile.formen]]

## Gebraucht von

- [[opencivil.projekt.aufbau.querschnittsanalyse]]

## Formeln aus diesem Modul

- [[Abgeminderter Biegewiderstand um die schwache Achse]] · `_Herleitung.gleichung_51`
- [[Abgeminderter Kippwiderstand im Stab]] · `_Herleitung.gleichung_51`
- [[Abminderungsfaktor beim Knicken und Kippen]] · `_Herleitung.kippen`
- [[Abminderungsfaktor beim Knicken und Kippen]] · `_Herleitung.knicken`
- [[Beiwert η der Momentenverteilung beim Kippen]] · `_Herleitung.kippen`
- [[Beiwert Φ beim Kippen]] · `_Herleitung.kippen`
- [[Beiwert Φ beim Knicken]] · `_Herleitung.knicken`
- [[Beiwert ω der Momentenverteilung]] · `_Herleitung._omega`
- [[Biegewiderstand bis zum ersten Fliessen]] · `_Herleitung._biegung`
- [[Druck und Biegung am wirksamen Querschnitt im Stab]] · `_Herleitung.gleichungen_62`
- [[Druck und zweiachsige Biegung im doppelsymmetrischen I-Stab]] · `_Herleitung.gleichung_51`
- [[Druck und zweiachsige Biegung im Stab]] · `_Herleitung.gleichung_50`
- [[Erfüllungsgrad bei fester Normalkraft und fester Richtung]] · `StahlStabilitaetQA.pruefe`
- [[Ersatzimperfektion des Stabs]] · `_Herleitung.gleichungen_62`
- [[Exponent β der Interaktion]] · `_Herleitung.gleichung_51`
- [[Ideelle Kippspannung]] · `_Herleitung.kippen`
- [[Ideelles Kippmoment]] · `_Herleitung.kippen`
- [[Kippwiderstand]] · `_Herleitung.kippen`
- [[Knicklast nach Euler]] · `_Herleitung.knicken`
- [[Knickwiderstand]] · `_Herleitung.knicken`
- [[Normalkraftwiderstand eines Stahlquerschnitts]] · `_Herleitung.widerstaende`
- [[Plastischer Biegewiderstand eines Stahlquerschnitts]] · `_Herleitung._biegung`
- [[Reduzierte Kipplänge]] · `_Herleitung.kippen`
- [[Saint-Venant-Anteil der Kippspannung]] · `_Herleitung.kippen`
- [[Schlankheit beim Kippen]] · `_Herleitung.kippen`
- [[Schlankheit beim Knicken]] · `_Herleitung.knicken`
- [[Trägheitsradius]] · `_Herleitung._druckgurt`
- [[Widerstand in der Richtung der Einwirkung]] · `StahlStabilitaetQA._urteil`
- [[Widerstandsmoment bis zur weitesten Faser]] · `_Herleitung._biegung`
- [[Wölbanteil der Kippspannung]] · `_Herleitung.kippen`
