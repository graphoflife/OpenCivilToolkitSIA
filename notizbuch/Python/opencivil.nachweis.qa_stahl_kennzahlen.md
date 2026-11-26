---
erzeugt: 6abd81a569a2
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/qa_stahl_kennzahlen.py
> was ein gezeichneter Stahlquerschnitt aufnimmt, ohne Einwirkung.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/qa_stahl_kennzahlen.py)

## VERANTWORTUNG

Die Kennzahlen eines Querschnitts aus Baustahl nach SIA 263:2013, wie die des
Stahlbetons ([[opencivil.nachweis.qa_kennzahlen]]) -- gerechnet immer, ob
es Lastfaelle gibt oder nicht:

* die Querschnittsklasse bei Druck und je Zugseite bei Biegung: je Blech
  jedes Profils nach den Tabellen 5a und 5b, massgebend das unguenstigste
  (4.3.1.3);
* der Zug- und der Druckwiderstand nach (38), in Klasse 4 nach (55) mit der
  wirksamen Flaeche;
* je Zugseite der Momentenwiderstand: plastisch nach (40) in den Klassen 1
  und 2, elastisch nach (52) in Klasse 3, nach (56) mit dem wirksamen
  Querschnitt in Klasse 4;
* mit Profilen der Querkraftwiderstand in z und, wo auch um z gebogen wird,
  in y -- je Profil allein ([[opencivil.stahlbau.schub]]), zusammen.

Knicken und Kippen gehoeren dem Stab: hier stehen die Widerstaende des
Querschnitts. Die Rechnung selbst steht in [[opencivil.stahlbau]]; hier
nur, was sie in die Herleitung schreibt. Mit mehreren Staehlen oder Dicken
rechnet jede Gruppe mit ihrer Fliessgrenze; eine Tabelle zeigt sie, statt
einer Formel. Mit Bemessungswerten oder charakteristischen, wie die
Tragsicherheit waehlt ([[opencivil.nachweis.qa_stahl_werte]]).


## WAS FEHLT -- GRAU IN DER HERLEITUNG

* Frei gezeichnete Flaechen: ihr Beulen ist nicht geprueft, Querkraft tragen
  sie nicht ([[opencivil.stahlbau.querschnitt]]). Ohne Profil gibt es
  darum keinen Querkraftwiderstand.
* Ein Rundrohr der Klasse 4: SIA 263 nennt dafuer keine mitwirkende Breite;
  der Widerstand dieser Beanspruchung steht auf null, und ein Satz sagt,
  warum.
* Der Nettoquerschnitt (39): gerechnet wird der gezeichnete Querschnitt nach
  (38). Ein Loch zeichnet man als Aussparung; dass dort die Zugfestigkeit
  nach (39) massgebend werden kann, prueft das Werkzeug nicht (nach Vorgabe,
  nicht nachgeschlagen).
* Sind y und z keine Hauptachsen, sagt es der Satz des Balkensystems
  ([[opencivil.stabwerk.stabquerschnitt#keine_hauptachsen|keine_hauptachsen]]).

## Inhalt

### _ohne_klammern

```python
def _ohne_klammern(symbol: str) -> str
```

Ein Symbol als Teil einer Kennung: «W_{pl}» wird «W_pl».

### _achse

```python
def _achse(seite: Zugseite) -> str
```

Um welche Achse ein Moment diese Seite zieht.

### KennzahlenStahlQA

```python
class KennzahlenStahlQA(Kennzahlprozedur)
```

Die Kennzahlen eines Stahlquerschnitts -- siehe Dateikopf.

- `THEMA = 'Kennzahlen'`

#### KennzahlenStahlQA.rechne

```python
def rechne(self, e: Eingaben, p: Protokoll) -> Dict[str, Groesse]
```

#### KennzahlenStahlQA._summe

```python
def _summe(self, p: Protokoll, sw: Stahlwerte, werte: Zwischenwerte, ergebnis: Dict[str, Groesse], kurz: str, groessen: Sequence[float], symbol: str, *, vorzeichen: float=1.0, titel: str, referenz: str) -> None
```

`Σ f_y X/γ_M1` -- `groessen` je Gruppe `X`: Flaechen in mm²,
Widerstandsmomente in mm³, nach dem Symbol (`A` oder `W`). Mit
einer Gruppe als Formel, sonst als Tabelle.

#### KennzahlenStahlQA._klasse

```python
def _klasse(self, p: Protokoll, ergebnis: Dict[str, Groesse], kurz: str, zustaende: Sequence[Blechzustand], freie: Sequence[Teil], titel: str) -> int
```

Die Klasse je Blech, als Tabelle -- und die des Querschnitts: die unguenstigste.

#### KennzahlenStahlQA._elastisch

```python
def _elastisch(self, p: Protokoll, sw: Stahlwerte, werte: Zwischenwerte, ergebnis: Dict[str, Groesse], kurz: str, el: Elastisch, I: Wert, seite: Zugseite, symbol: str, titel: str, referenz: str) -> None
```

Bis die erste Faser fliesst: je Gruppe `W = I/z` bis zu ihrer
weitesten Faser, massgebend das kleinste `f_y W/γ_M1`.


## Konstanten

- `REFERENZ_38 = 'SIA 263:2013, 5.1.2.1, (38)'`
- `REFERENZ_40 = 'SIA 263:2013, 5.1.3, (40)'`
- `REFERENZ_52 = 'SIA 263:2013, 5.2.3, (52)'`
- `REFERENZ_55 = 'SIA 263:2013, 5.3.2, (55); 4.5.3'`
- `REFERENZ_56 = 'SIA 263:2013, 5.3.3, (56); 4.5.3'`
- `REFERENZ_KLASSE = 'SIA 263:2013, 4.3.1.3; Tabellen 5a und 5b'`
- `_BEDEUTUNG = {'A': 'Fläche aus Baustahl', 'A_{eff}': 'Wirksame Fläche', 'W_{pl}': …` – Was die Querschnittswerte bedeuten, nach ihrem Symbol.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.nachweis.qa_stahl_werte]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.zugseite]]
- [[opencivil.stabwerk.stabquerschnitt]]
- [[opencivil.stahlbau.klasse]]
- [[opencivil.stahlbau.querschnitt]]
- [[opencivil.stahlbau.schub]]
- [[opencivil.stahlprofile.bleche]]

## Gebraucht von

- [[opencivil.nachweis.qa_stahl]]
- [[opencivil.projekt.aufbau.querschnittsanalyse]]

## Formeln aus diesem Modul

- [[Beiwert ε der Grenzschlankheiten]] · `KennzahlenStahlQA._teile`
- [[Normalkraftwiderstand eines Stahlquerschnitts]] · `KennzahlenStahlQA._summe`
- [[Plastischer Biegewiderstand eines Stahlquerschnitts]] · `KennzahlenStahlQA._summe`
- [[Querkraftwiderstand eines Stahlprofils]] · `KennzahlenStahlQA._schub`
- [[Schubbeulen des Blechs, ohne Quersteifen]] · `KennzahlenStahlQA._schub`
- [[Steg ohne Schubbeulen]] · `KennzahlenStahlQA._schub`
