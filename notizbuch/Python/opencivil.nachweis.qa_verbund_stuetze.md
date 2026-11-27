---
erzeugt: c43bb1f7e676
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/qa_verbund_stuetze.py
> eine Verbundstuetze nach SIA 264:2014, 5.3.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/qa_verbund_stuetze.py)

## VERANTWORTUNG

Je Stabilitaetsfall der Querschnittsanalyse ein Nachweis mit seiner
Herleitung; gerechnet wird in [[opencivil.verbund.stuetze]]. Vorweg,
einmal fuer alle Faelle, der Querschnitt als Stuetze ([[opencivil.nachweis.qa_verbund_stuetze#_Querschnitt|_Querschnitt]]):
seine Art nach Tabelle 7, was 5.3.1 und 5.3.2 von ihm verlangen, je
Werkstoff Flaeche, Festigkeit und Traegheitsmomente, `N_pl,Rd`, `δ` und
`N_pl,Rk`. Dann je Fall ([[opencivil.nachweis.qa_verbund_stuetze#_Fall|_Fall]]) `E_c,eff`, die Achse ohne
Moment nach (15), die mit Moment nach (25) – zweiachsig linear.


## DER ERFUELLUNGSGRAD

Je Nachweis der Widerstand durch die Einwirkung, massgebend der kleinste:
(15) `χ_K N_pl,Rd/|N_Ed|`, (25) `0.9 μ_d M_pl,Rd/M_Ed,II`, zweiachsig
`0.9/Σ`. Wo `|N_Ed|` `N_cr,eff` erreicht, knickt die Stuetze aus:
`N_cr,eff/|N_Ed|`.


## WAS FEHLT – GRAU

Ein Querschnitt, den Tabelle 7 nicht kennt, und was
[[opencivil.verbund.stuetze#Stuetze.fehlt|fehlt]] und
[[opencivil.verbund.stuetze#Ergebnis|fehlt]] nennen.


## VORZEICHEN

N \< 0 Druck; M_y > 0 zieht unten, M_z > 0 links.

## Inhalt

### _nulllinie

```python
def _nulllinie(lage: Optional[float]) -> str
```

Wo die Nulllinie liegt, in Worten – von der Mitte zur gezogenen oder gedrueckten Seite.

### VerbundStuetzeQA

```python
class VerbundStuetzeQA(Nachweis)
```

Eine Verbundstuetze, je Fall – siehe Dateikopf. `kriechzahl` ist `φ(t,t_0)`.

- `THEMA = 'Verbundstütze'`
- `ART = 'Stab'`

#### VerbundStuetzeQA.pruefe

```python
def pruefe(self, e: Eingaben, p: Protokoll)
```

#### VerbundStuetzeQA._grau

```python
def _grau(self, p: Protokoll, grund: str) -> Ausfuehrung
```

Jeder Fall grau, mit demselben Grund: er liegt am Querschnitt.

### _einwirkung

```python
def _einwirkung(p: Protokoll, biegung: Biegung, fall: st.Stabfall) -> None
```

Die Einwirkung und die Stuetze als Tabelle – einachsig ohne M_z.

### _Querschnitt

```python
class _Querschnitt
```

Der Querschnitt als Stuetze, vorweg fuer alle Faelle – mit den Werten, die sie lesen.

#### _Querschnitt.steifigkeit

```python
def steifigkeit(self, achse: str, E_c: Dict[int, Wert], beton: float) -> Tuple[str, Dict[str, Wert]]
```

`Σ E I` um `achse` als Vorlage mit ihren Werten – der Beton mit
`beton · E_c,eff`, der Betonstahl mit seinem Anteil (5.3.2.2).

### _Fall

```python
class _Fall
```

Die Herleitung eines Falls – je Achse, mit den Vergleichen, die er fuehrt.

#### _Fall._kriechen

```python
def _kriechen(self, kriechzahl: float) -> Dict[int, Wert]
```

(19) je Beton.

#### _Fall._steifigkeit

```python
def _steifigkeit(self, kennung: str, symbol: str, si: float) -> Wert
```

Eine Biegesteifigkeit, `si` in N mm².

#### _Fall._biegung

```python
def _biegung(self, b: vs.Biegeachse) -> Optional[Tuple[Wert, Wert, Wert]]
```

Die Achse mit Moment, bis `M_Ed,II`, `μ_d` und `M_pl,Rd` – die
gibt sie zurueck, oder `None`, wo die Stuetze ausknickt.

#### _Fall._zweite_ordnung

```python
def _zweite_ordnung(self, b: vs.Biegeachse, M: Wert, M_II: Wert) -> bool
```

(22) bis (24) und die Imperfektion – falsch, wo die Stuetze ausknickt.

#### _Fall._interaktion

```python
def _interaktion(self, b: vs.Biegeachse) -> Tuple[Wert, Wert]
```

`M_pl,Rd`, `M_pl,N,Rd` und `μ_d` (Figur 7) – zurueck gibt es
`μ_d` und `M_pl,Rd`.

#### _Fall._zweiachsig

```python
def _zweiachsig(self, teile: Dict[str, Tuple[Wert, Wert, Wert]]) -> None
```

5.3.5: beide Achsen linear – gegen die Grenze von (25).


## Konstanten

- `REFERENZ = 'SIA 264:2014, 5.3'`
- `ERKLAERUNG = 'Die Stütze hat den gezeichneten Querschnitt und ist an ihren Enden s…`
- `ANNAHME = f'Doppelsymmetrisch heisst: je Werkstoff liegt der Schwerpunkt höchst…`
- `ANSATZ_ROHR = 'N_{pl,Rd} = A_a\\, f_{yd} + A_c\\, 1.0\\, f_{cd} + A_s\\, f_{sd}'` – (14) im gefuellten Rohr, mit 1.0 statt 0.85 (5.3.2.5) – eine eigene Formel.
- `NAME_ROHR = 'Plastischer Normalkraftwiderstand eines gefüllten Rohrs'`
- `NICHT_GEDRUECKT = 'Nicht gedrückt: die Stütze knickt nicht. Biegung allein weist die Tr…` – Was ein Fall ohne Druck sagt.
- `_KUERZEL = {Baustoffart.BAUSTAHL: 'a', Baustoffart.BETON: 'c', Baustoffart.BETON…` – Das Kuerzel je Art, an den Zeichen der Gruppen: A_a, I_c, E_s.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.nachweis]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.material.basis]]
- [[opencivil.nachweis.qa_stahl_stabilitaet]]
- [[opencivil.nachweis.qa_verbund_kennzahlen]]
- [[opencivil.nachweis.qa_verbund_werte]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.biegung]]
- [[opencivil.stahlbau.stabilitaet]]
- [[opencivil.verbund.stuetze]]

## Gebraucht von

- [[opencivil.projekt.aufbau.querschnittsanalyse]]

## Formeln aus diesem Modul

- [[Abminderungsfaktor beim Knicken und Kippen]] · `_Fall._knicken`
- [[Beiwert μ_d einer Verbundstütze]] · `_Fall._interaktion`
- [[Beiwert Φ beim Knicken]] · `_Fall._knicken`
- [[Beiwert ω der Momentenverteilung]] · `_Fall._zweite_ordnung`
- [[Bemessungssteifigkeit einer Verbundstütze]] · `_Fall._zweite_ordnung`
- [[Bezogene Schlankheit einer Verbundstütze]] · `_Fall._knicken`
- [[Biegesteifigkeit einer Verbundstütze für die Schlankheit]] · `_Fall._knicken`
- [[Ersatzimperfektion einer Verbundstütze]] · `_Fall._zweite_ordnung`
- [[Knickwiderstand einer Verbundstütze]] · `_Fall._knicken`
- [[Kritische Normalkraft einer Verbundstütze]] · `_Fall._knicken`
- [[Kritische Normalkraft einer Verbundstütze]] · `_Fall._zweite_ordnung`
- [[Moment 2. Ordnung einer Verbundstütze]] · `_Fall._zweite_ordnung`
- [[Plastischer Normalkraftwiderstand eines gefüllten Rohrs]] · `_Querschnitt._normalkraft`
- [[Plastischer Normalkraftwiderstand im Verbund]] · `_Querschnitt._normalkraft`
- [[Querschnittsparameter einer Verbundstütze]] · `_Querschnitt._normalkraft`
- [[Vergrösserungsfaktor der Imperfektion einer Verbundstütze]] · `_Fall._zweite_ordnung`
- [[Vergrösserungsfaktor einer Verbundstütze]] · `_Fall._zweite_ordnung`
- [[Widerstand einer Verbundstütze nach (25)]] · `_Fall._biegung`
- [[Wirksamer Elastizitätsmodul des Betons einer Verbundstütze]] · `_Fall._kriechen`
- [[Zweiachsige Biegung einer Verbundstütze]] · `_Fall._zweiachsig`
