---
erzeugt: 5350947cd223
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/qa_verbund_kennzahlen.py
> was ein Verbundquerschnitt aufnimmt, ohne Einwirkung.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/qa_verbund_kennzahlen.py)

## VERANTWORTUNG

Die Kennzahlen eines Querschnitts aus Baustahl und Beton nach SIA 264:2014,
wie die des Stahls ([[opencivil.nachweis.qa_stahl_kennzahlen]]) --
gerechnet immer, ob es Lastfaelle gibt oder nicht:

* die Festigkeiten je Werkstoff
  ([[opencivil.nachweis.qa_verbund_werte#festigkeiten|festigkeiten]]);
* der Zugwiderstand: Baustahl und Betonstahl, der Beton traegt keinen Zug
  (4.3.2.1);
* der Druckwiderstand ohne Knicken wie (14), wo jedes Blech bei Druck in
  Klasse 1 oder 2 liegt;
* je Zugseite der plastische Momentenwiderstand bei `N = 0` mit voller
  Verduebelung (5.1.2.1), mit `β` nach 5.1.2.2 -- gerechnet in
  [[opencivil.verbund.widerstand]];
* mit Profilen der Querkraftwiderstand: ihn traegt der Stahl allein
  (4.3.2.2), wie im Stahlquerschnitt;
* mit Kopfbolzenduebeln ihr Schubwiderstand `P_Rd` (6.1.2.1) -- gerechnet
  in [[opencivil.verbund.duebel]]. Mehrere Betone: (30) mit dem, der am
  wenigsten traegt (nach Vorgabe, nicht nachgeschlagen). Wie viele Duebel
  ein Lastfall braucht, sagt sein Nachweis.


## WAS FEHLT -- GRAU IN DER HERLEITUNG

Wo ein Widerstand plastisch nicht gilt -- ein Blech ueber Klasse 2,
gezogener Betonstahl ohne Duktilitaetsklasse B oder C, `x_p/h` ueber 0.4
--, steht er auf null, und ein Satz sagt, warum: elastisch nach 5.1.2.4
rechnet das Werkzeug noch nicht. Die Momentenwiderstaende gelten mit
voller Verduebelung; was die Duebel eines Lastfalls erlauben, rechnet sein
Nachweis. Knicken und Kippen gehoeren dem Traeger.

## Inhalt

### _achse

```python
def _achse(seite: Zugseite) -> str
```

Um welche Achse ein Moment diese Seite zieht.

### verbund_von

```python
def verbund_von(analyse: Querschnittsanalyse) -> Verbundquerschnitt
```

Der Verbundquerschnitt einer Analyse: ihre Flaechen und ihre Bewehrung.

### KennzahlenVerbundQA

```python
class KennzahlenVerbundQA(Kennzahlprozedur)
```

Die Kennzahlen eines Verbundquerschnitts -- siehe Dateikopf.

- `THEMA = 'Kennzahlen'`

#### KennzahlenVerbundQA.rechne

```python
def rechne(self, e: Eingaben, p: Protokoll) -> Dict[str, Groesse]
```

#### KennzahlenVerbundQA._duebel

```python
def _duebel(self, p: Protokoll, e: Eingaben, ergebnis: Dict[str, Groesse], k: vd.Kopfbolzen) -> None
```

`P_Rd` nach (30) und (31) -- siehe Dateikopf.

#### KennzahlenVerbundQA._summe

```python
def _summe(self, p: Protokoll, werte: Verbundwerte, ergebnis: Dict[str, Groesse], kurz: str, festigkeit: Sequence[float], *, vorzeichen: float, titel: str, referenz: str) -> None
```

`Σ f A` je Werkstoff als Tabelle, die Summe als Kennzahl.


## Konstanten

- `REFERENZ_ZUG = 'SIA 264:2014, 4.3.2.1; 5.1.2.1'`
- `REFERENZ_14 = 'SIA 264:2014, 5.3.2.4, (14)'`
- `ANSATZ_14 = 'N_{pl,Rd} = A_a\\, f_{yd} + A_c\\, 0.85\\, f_{cd} + A_s\\, f_{sd}'` – (14) als Ansatz und sein Name -- die Verbundstuetze schreibt ihn auch.
- `NAME_14 = 'Plastischer Normalkraftwiderstand im Verbund'`
- `AUF_NULL = 'Der Widerstand steht darum auf null.'` – Was in den Kennzahlen fehlt, wo ein Widerstand plastisch nicht gilt -- siehe Dateikopf.
- `VOLLE_VERDUEBELUNG = 'Gerechnet mit voller Verdübelung, wie 5.1.2.1 es annimmt: Stahl und …` – Die Annahme hinter den Momentenwiderstaenden der Kennzahlen -- und mit Duebeln der Satz dazu.
- `MIT_DUEBELN = 'Was die Dübel eines Lastfalls erlauben, rechnet sein Nachweis.'`

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.material.basis]]
- [[opencivil.nachweis.qa_stahl]]
- [[opencivil.nachweis.qa_stahl_kennzahlen]]
- [[opencivil.nachweis.qa_verbund_werte]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.plastisch]]
- [[opencivil.querschnitt.zugseite]]
- [[opencivil.stabwerk.stabquerschnitt]]
- [[opencivil.stahlbau.querschnitt]]
- [[opencivil.verbund.duebel]]
- [[opencivil.verbund.querschnitt]]
- [[opencivil.verbund.widerstand]]

## Gebraucht von

- [[opencivil.nachweis.qa_verbund]]
- [[opencivil.nachweis.qa_verbund_stuetze]]
- [[opencivil.projekt.aufbau.querschnittsanalyse]]

## Formeln aus diesem Modul

- [[Plastischer Biegewiderstand mit β]] · `KennzahlenVerbundQA._biegung`
- [[Plastischer Normalkraftwiderstand im Verbund]] · `KennzahlenVerbundQA._normalkraft`
- [[Probe – Moment um y]] · `KennzahlenVerbundQA._biegung`
- [[Probe – Moment um z]] · `KennzahlenVerbundQA._biegung`
- [[Schubwiderstand eines Kopfbolzendübels]] · `KennzahlenVerbundQA._duebel`
- [[Schubwiderstand eines Kopfbolzendübels – Betonstauchung]] · `KennzahlenVerbundQA._duebel`
- [[Schubwiderstand eines Kopfbolzendübels – Versagen des Dübels]] · `KennzahlenVerbundQA._duebel`
