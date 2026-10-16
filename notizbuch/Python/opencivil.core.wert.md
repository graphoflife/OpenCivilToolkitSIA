---
erzeugt: dd5c2231d540
art: modul
tags: [modul]
---
> [!abstract] opencivil/core/wert.py
> Benannte Werte im Rechenmodell.
> Paket [[opencivil.core]] · [Quelltext](../../opencivil/core/wert.py)

## VERANTWORTUNG

Trennt sauber zwischen der *Definition* eines Wertes (Symbol, Einheit,
Beschreibung, Normreferenz -- statisch) und seiner *Belegung* (Zahlenwert,
Herkunft -- dynamisch). Diese Trennung ist bewusst: im alten Code waren
Definition und Instanz dasselbe veraenderliche Objekt, was zu global
mutierbaren Vorlagen und schwer nachvollziehbarem Zustand fuehrte.


## NAMENSRAEUME

Wert-IDs sind punktgetrennt und global eindeutig:

```
beton.C30_37.f_cd
stahl.B500B.f_yd
querschnitt.decke1.lage.3.a_s
querschnitt.decke1.M_Rd
```

Das erlaubt mehrere Materialien und Bauteile im selben Modell, ohne dass sich
Werte gegenseitig ueberschreiben.

## Inhalt

### kennung_aus

```python
def kennung_aus(text: str) -> str
```

Ein Name, wie er in einer Wert-ID stehen darf.

Alles ausser Buchstaben und Ziffern wird zum Unterstrich. Damit bilden
«Feld A» und «Feld-A» auf dieselbe Kennung ab -- wer Namen prueft, muss
darum auch die Kennungen pruefen, nicht nur die Namen.

Die eine Stelle fuer diese Regel. Sie stand einmal neunmal da, in jedem
Nachweis als eigene Kopie; eine davon anders zu aendern haette Wert-IDs
ergeben, die nicht mehr zu den Namen in der Pruefung passen.

### Quelle

```python
class Quelle(str, Enum)
```

Woher ein Wert stammt -- entscheidend fuer die Nachvollziehbarkeit.

- `EINGABE = 'eingabe'` – Direkt vom Benutzer eingegeben.
- `VORGABE = 'vorgabe'` – Normvorgabe oder Vorlagenwert (z.B. f_ck aus der Betonsorte).
- `BERECHNET = 'berechnet'` – Von einer Berechnung erzeugt.
- `UEBERSCHRIEBEN = 'ueberschrieben'` – Waere berechenbar, wurde aber vom Benutzer von Hand gesetzt.

#### Quelle.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Quelle.ist_vorgegeben

```python
@property
def ist_vorgegeben(self) -> bool
```

True, wenn der Wert nicht aus einer Berechnung stammt.

### grad_als_text

```python
def grad_als_text(grad: float, erfuellt: bool, *, latex: bool=False) -> str
```

Ein Erfuellungsgrad als Text -- knapp, aber nie gerundet bis zur Luege.

Zwei Stellen genuegen fast immer. Nur wo ein Nachweis knapp nicht
aufgeht, zeigen sie `1.00` und sagen damit das Gegenteil des Urteils
daneben. Dann kommt eine Stelle dazu, abgeschnitten statt gerundet: der
Grad soll kleiner als eins bleiben, weil er das ist.

Die eine Stelle fuer diese Regel. Zuerst stand sie nur in der
Schnittstelle, und Konsolenbericht, LaTeX-Dokument und die Tooltips der
Diagramme rundeten weiter selbst -- dort stand bei 0.9966 «1» neben
«nicht erfuellt».

`latex` sagt, in welcher Sprache die Unendlichkeit geschrieben wird:
`\infty` fuer eine Formel, `∞` fuer Fliesstext. Die Zahl selbst ist
in beiden dieselbe.

### WertDef

```python
@dataclass(frozen=True)
class WertDef
```

Statische Definition eines Wertes.

Enthaelt alles, was zur Darstellung noetig ist, aber keinen Zahlenwert.
Unveraenderlich, damit Definitionen gefahrlos geteilt werden koennen.

- `id: str` – Global eindeutige, punktgetrennte Kennung, z.B. `beton.C30_37.f_cd`.
- `symbol: str` – LaTeX-Symbol ohne Mathematikumgebung, z.B. `f_{cd}`.
- `einheit: Einheit = EINHEITSLOS` – Anzeige-Einheit. Beeinflusst nie das Rechenergebnis.
- `beschreibung: str = ''` – Deutscher Klartext, z.B. 'Bemessungswert der Betondruckfestigkeit'.
- `referenz: str = ''` – Normstelle, z.B. 'SIA 262:2025, 2.4.2.3'.
- `stellen: int = 2` – Nachkommastellen fuer die Darstellung.
- `erfuellungsgrad: bool = False` – Ein Erfuellungsgrad: gesetzt nach [[opencivil.core.wert#grad_als_text|grad_als_text]] statt mit `stellen` -- in Herleitung, Werttabelle und Oberflaeche derselbe Text.

#### WertDef.kurzname

```python
@property
def kurzname(self) -> str
```

Letztes Segment der ID, z.B. 'f_cd' aus 'beton.C30_37.f_cd'.

#### WertDef.namensraum

```python
@property
def namensraum(self) -> str
```

Alles vor dem letzten Segment, z.B. 'beton.C30_37'.

#### WertDef.belegen

```python
def belegen(self, groesse: Groesse, quelle: Quelle=Quelle.BERECHNET, herkunft: Optional[str]=None) -> 'Wert'
```

Erzeugt einen belegten Wert zu dieser Definition.

#### WertDef.mit_praefix

```python
def mit_praefix(self, praefix: str) -> 'WertDef'
```

Kopie mit vorangestelltem Namensraum.

Erlaubt es, Wert-Vorlagen (z.B. alle Betoneigenschaften) einmal zu
definieren und pro Material zu instanziieren.

### Wert

```python
@dataclass(frozen=True)
class Wert
```

Eine Definition zusammen mit ihrem Zahlenwert.

- `definition: WertDef`
- `groesse: Groesse`
- `quelle: Quelle = Quelle.BERECHNET`
- `herkunft: Optional[str] = None` – ID der Berechnung, die diesen Wert erzeugt hat (None bei Eingaben).

#### Wert.id

```python
@property
def id(self) -> str
```

#### Wert.symbol

```python
@property
def symbol(self) -> str
```

#### Wert.einheit

```python
@property
def einheit(self) -> Einheit
```

#### Wert.stellen

```python
@property
def stellen(self) -> int
```

#### Wert.beschreibung

```python
@property
def beschreibung(self) -> str
```

#### Wert.referenz

```python
@property
def referenz(self) -> str
```

#### Wert.in_einheit

```python
def in_einheit(self, ziel: Einheit) -> float
```

#### Wert.formatiert

```python
def formatiert(self, latex: bool=False) -> str
```

Zahlenwert in der definierten Einheit und Genauigkeit.

Ein Erfuellungsgrad folgt [[opencivil.core.wert#grad_als_text|grad_als_text]]; ab eins gilt er als
erfuellt, so ist er definiert. `latex` sagt, wie seine
Unendlichkeit geschrieben wird.

#### Wert.zahl_latex

```python
def zahl_latex(self) -> str
```

Zahlenwert samt Einheit als LaTeX-Fragment, z.B. `18.7\,\mathrm{MPa}`.

### FehlendeEingabe

```python
@dataclass
class FehlendeEingabe
```

Eine Eingabe, die zur Berechnung eines Ziels noetig waere, aber fehlt.

Der Loeser sammelt diese, statt abzubrechen -- so kann die Oberflaeche dem
Benutzer genau sagen, was er noch angeben muss und wofuer.

- `id: str` – ID des fehlenden Wertes.
- `benoetigt_von: str` – ID der Berechnung, die ihn braucht.
- `pfad: tuple = field(default_factory=tuple)` – Kette der Ziele, ueber die man hierher kam -- fuer die Begruendung.
- `definition: Optional[WertDef] = None` – Definition, falls bekannt (dann kennt man Symbol, Einheit, Beschreibung).

#### FehlendeEingabe.beschreibung

```python
@property
def beschreibung(self) -> str
```


## Braucht

- [[opencivil.core.einheiten]]

## Gebraucht von

- [[opencivil.bericht.konsole]]
- [[opencivil.bericht.zusammenfassung]]
- [[opencivil.core.berechnung]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.rechenwerk]]
- [[opencivil.ergebnis]]
- [[opencivil.geotechnik.grundbruch]]
- [[opencivil.material.basis]]
- [[opencivil.nachweis.biegung_normalkraft]]
- [[opencivil.nachweis.duktilitaet]]
- [[opencivil.nachweis.fehlende_bewehrung]]
- [[opencivil.nachweis.handrechnung]]
- [[opencivil.nachweis.knicken]]
- [[opencivil.nachweis.mindestbewehrung]]
- [[opencivil.nachweis.qa_gebrauch]]
- [[opencivil.nachweis.querkraft]]
- [[opencivil.nachweis.rechenwahl]]
- [[opencivil.nachweis.resistenzlinie]]
- [[opencivil.nachweis.richtungsnachweise]]
- [[opencivil.nachweis.schiefe_biegung]]
- [[opencivil.nachweis.schubwandnachweis]]
- [[opencivil.nachweis.spannungsbegrenzung]]
- [[opencivil.nachweis.sproedes_versagen]]
- [[opencivil.nachweis.stabgrenzen]]
- [[opencivil.nachweis.verformung]]
- [[opencivil.notizbuch.formelseiten]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.grundbruch]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.platte]]
- [[opencivil.querschnitt.schnittanalyse]]
- [[opencivil.querschnitt.werkstoffgesetz]]
- [[opencivil.spannungsanalyse]]
- [[opencivil.stabwerk.rechnung]]
- [[opencivil.web.api]]
