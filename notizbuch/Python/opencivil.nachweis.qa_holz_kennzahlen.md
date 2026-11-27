---
erzeugt: 0c578f21d5de
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/qa_holz_kennzahlen.py
> was ein Holzquerschnitt aufnimmt, ohne Einwirkung.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/qa_holz_kennzahlen.py)

## VERANTWORTUNG

Die Kennzahlen eines Querschnitts aus Holz nach SIA 265:2012, wie die des
Stahls ([[opencivil.nachweis.qa_stahl_kennzahlen]]) – gerechnet immer, ob
es Lastfaelle gibt oder nicht. Je Beanspruchung allein, linear (4.1.2), mit
den Bemessungswerten der Tabellen 6 und 7 und dem Beiwert η_w der
Feuchteklasse der Analyse:

* der Zugwiderstand nach (6), der Druckwiderstand nach (10) ohne Knicken;
* je Achse der Biegewiderstand nach (14), beim Brettschichtholz um y mit
  `k_h`;
* je Richtung der Querkraftwiderstand nach (23), aus der Schubflaeche;
* beim Rechteck der Torsionswiderstand nach (24).

Die Werte des Querschnitts – `W`, `k_h`, `A_V`, `W_T` – rechnet
[[opencivil.nachweis.qa_holz_werte#HolzwerteQA|HolzwerteQA]]; hier stehen nur die
Widerstaende. Stossartig ist hier nichts: `η_t` gehoert dem Lastfall.

## Inhalt

### KennzahlenHolzQA

```python
class KennzahlenHolzQA(Kennzahlprozedur)
```

Die Kennzahlen eines Holzquerschnitts – siehe Dateikopf.

- `THEMA = 'Kennzahlen'`

#### KennzahlenHolzQA._mit_k_h

```python
def _mit_k_h(self, achse: str) -> bool
```

Ob die Biegung um `achse` `k_h` hat: beim Brettschichtholz um y.

#### KennzahlenHolzQA.rechne

```python
def rechne(self, e: Eingaben, p: Protokoll) -> Dict[str, Groesse]
```


## Konstanten

- `BIEGUNG = ('@eta \\cdot @f_m \\cdot @W', 'Biegewiderstand eines Holzquerschnitt…` – Die Biegung, je mit und ohne k_h – eine Vorlage, ein Name.
- `BIEGUNG_K_H = ('@eta \\cdot @k_h \\cdot @f_m \\cdot @W', 'Biegewiderstand des Brett…`

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.holzbau.gleichungen]]
- [[opencivil.material.holz]]
- [[opencivil.nachweis.qa_holz_werte]]
- [[opencivil.querschnitt.analyse]]

## Gebraucht von

- [[opencivil.projekt.aufbau.querschnittsanalyse]]

## Formeln aus diesem Modul

- [[Biegewiderstand des Brettschichtholzes]] · `KennzahlenHolzQA.rechne`
- [[Biegewiderstand eines Holzquerschnitts]] · `KennzahlenHolzQA.rechne`
- [[Druckwiderstand eines Holzquerschnitts]] · `KennzahlenHolzQA.rechne`
- [[Querkraftwiderstand eines Holzquerschnitts]] · `KennzahlenHolzQA.rechne`
- [[Torsionswiderstand eines Rechtecks aus Holz]] · `KennzahlenHolzQA.rechne`
- [[Zugwiderstand eines Holzquerschnitts]] · `KennzahlenHolzQA.rechne`
