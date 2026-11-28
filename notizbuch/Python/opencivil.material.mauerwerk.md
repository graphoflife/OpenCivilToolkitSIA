---
erzeugt: 1967d39b2637
art: modul
tags: [modul]
---
> [!abstract] opencivil/material/mauerwerk.py
> Mauerwerk nach SIA 266:2015.
> Paket [[opencivil.material]] · [Quelltext](../../opencivil/material/mauerwerk.py)

## VERANTWORTUNG

Sortentabelle und Kennwerte des Standardmauerwerks, aufgebaut wie die
anderen Baustoffe ([[opencivil.material.basis]]): jeder Kennwert ist
eine eigene, einzeln ueberschreibbare Berechnung. Deklariertes Mauerwerk
(3.1.2.2, mit dem Buchstaben D) legt man als eigenes Material an und setzt
die Werte seiner Deklaration – die Wand prueft dann die Mindestwerte nach
3.1.3.1 ([[opencivil.material.mauerwerk#Konstanten|MINDESTWERTE]]).


## DIE SORTEN

Je Art der Steine eine (3.1.1.1): Backsteine MB, Leichtbacksteine MBL,
Zementsteine MC, Leichtzementsteine MCL, Kalksandsteine MK,
Porenbetonsteine MP und Porenbetonleichtsteine MPL. Fuer Standardmauerwerk
nennt Tabelle 1 die Druckfestigkeit f_xk senkrecht zu den Lagerfugen und die
Biegezugfestigkeit f_txk, Tabelle 7 die Bemessungswerte mit γ_M = 2.0
(Gl. (3)) – auch f_yd senkrecht zu den Stossfugen, offen und vollfugig
vermauert, fuer das Tabelle 1 keinen kennzeichnenden Wert nennt. f_yk ist
darum γ_M · f_yd der Tabelle 7: so gibt Gl. (3) deren Zahl wieder. Am
2026-11-28 gegen die gedruckten Tabellen geprueft.


## DIE STEIFIGKEIT

E_xk = 1000 f_xk und G_k = 0.4 E_xk fuer Standardmauerwerk (3.1.4.1,
Gl. (2)), die Bemessungswerte durch γ_M (4.2.1.4, Gl. (5)) – G_d ebenso,
das gibt die Zahlen der Tabelle 7, die auf eine Stelle rundet. Der
Endkriechwert φ nach Tabelle 2, je nachdem, wie die Steine gebunden sind.
μ_d = 0.6 fuer die Reibung in den Lagerfugen (4.2.1.3).


## WAS DIE WAND WAEHLT, NICHT DAS MATERIAL

Ob das Mauerwerk im Verband steht – dann gelten alle Werte der Tabelle 7
mal 0.85 (4.2.1.1) – und ob die Stossfugen vollfugig vermauert sind: beides
ist eine Wahl der Wand ([[opencivil.mauerwerk]]), ihre Herleitung zeigt
die Werte, mit denen sie rechnet.


## NACH VORGABE, NICHT NACHGESCHLAGEN

- Porenbetonsteine gelten in Tabelle 2 als hydrothermisch gebunden, wie
  Kalksandsteine: beide haerten im Dampf.
- Die Dichte fuer das Eigengewicht: die Raumlast eines unverputzten
  Mauerwerks nach SIA 261:2020, Anhang A, Tabelle 28, durch g = 10 m/s² –
  je Sorte die Zeile der gelochten Steine ihrer Art. Leichtsteine haben
  dort keine eigene Zeile und nehmen die ihrer Art; Porenbeton die der
  Gasbetonsteine, MP die hochwertigen, MPL die normalen.


## EIGENSTAENDIG NUTZBAR


```python
from opencivil.core.rechenwerk import Rechenwerk
from opencivil.material.mauerwerk import mauerwerk

werk = Rechenwerk()
mb = mauerwerk("MB").ins_rechenwerk(werk)
print(werk.loese(mb.id_von("f_xd")).wert(mb.id_von("f_xd")))
```

## Inhalt

### Bindung

```python
class Bindung(Enum)
```

Wie die Steine gebunden sind – das sagt den Endkriechwert (Tabelle 2).

- `GEBRANNT = 'gebrannte Steine'`
- `ZEMENT = 'zementgebundene Steine'`
- `HYDROTHERMISCH = 'hydrothermisch gebundene Steine'`

#### Bindung.phi

```python
@property
def phi(self) -> float
```

Der Richtwert des Endkriechwerts – SIA 266:2015, Tabelle 2.

### Mauerwerkssorte

```python
@dataclass(frozen=True)
class Mauerwerkssorte
```

Ein Standardmauerwerk: Tabelle 1 und 7, die Bindung und die Raumlast.

- `steine: str` – Woraus es gemauert ist, in der Mehrzahl – «Backsteine».
- `f_xk: float`
- `f_txk: float`
- `f_yd: float` – Bemessungswert senkrecht zu den Stossfugen, offen vermauert – Tabelle 7.
- `f_yd_v: float` – Dasselbe, vollfugig vermauert – Tabelle 7.
- `bindung: Bindung`
- `raumlast: float` – kN/m³ – die Zeile in Tabelle 28 der SIA 261, siehe Dateikopf.

### mauerwerkssorten_zum_anlegen

```python
def mauerwerkssorten_zum_anlegen() -> List[str]
```

Die Sorten in der Folge von Tabelle 1 – die erste ist MB.

### _durch_gamma

```python
def _durch_gamma(kurzname: str, symbol: str, beschreibung: str, eingabe: str, referenz: str, stellen: int=2) -> KennwertVorlage
```

Ein Bemessungswert: der kennzeichnende durch γ_M. Das Rechenwerk gibt
die Eingaben mit ihren Kurznamen.

### mauerwerk

```python
def mauerwerk(sorte: str=ERSTES_MAUERWERK, *, name: Optional[str]=None, praefix: Optional[str]=None, abweichungen: Optional[Mapping[str, Groesse]]=None, symbol_index: str='') -> Baustoff
```

Erzeugt ein Mauerwerk aus der Sortentabelle.

:param sorte: Bezeichnung aus [[opencivil.material.mauerwerk#Konstanten|MAUERWERKSSORTEN]], z.B. `'MB'`.
:param abweichungen: Zahlenwerte, die von der Tabelle abweichen – bei
deklariertem Mauerwerk die Werte der Deklaration.


## Konstanten

- `TABELLE_1 = 'SIA 266:2015, 3.1.3.3, Tabelle 1'` – Wo die Werte des Standardmauerwerks stehen.
- `TABELLE_2 = 'SIA 266:2015, 3.1.4.2, Tabelle 2'`
- `TABELLE_7 = 'SIA 266:2015, 4.2.1.1, Tabelle 7'`
- `RAUMLASTEN = 'SIA 261:2020, Anhang A, Tabelle 28'` – Wo die mittleren Raumlasten stehen.
- `GAMMA_M = 2.0` – Der Widerstandsbeiwert – SIA 266:2015, 4.2.1.1 und 4.2.1.4.
- `VERBAND = 0.85` – Der Faktor auf alle Bemessungswerte, wenn das Mauerwerk im Verband steht (SIA 266:2015, 4.2.1.1, unter Tabelle 7).
- `MINDESTWERTE = (('f_xk', 'f_{xk}', 1.8), ('f_yk', 'f_{yk}', 0.5), ('E_xk', 'E_{xk}',…` – Was deklariertes Mauerwerk mindestens haben muss (SIA 266:2015, 3.1.3.1): je Kennwert die Zahl in N/mm².
- `REFERENZ_MINDESTWERTE = 'SIA 266:2015, 3.1.3.1'`
- `MAUERWERKSSORTEN = {'MB': Mauerwerkssorte('Backsteine', 7.0, 0.15, 1.1, 1.6, Bindung.GEB…`
- `ERSTES_MAUERWERK = 'MB'` – Womit ein neues Mauerwerk anfaengt.
- `MAUERWERK_VORLAGEN = (_tabellenwert('f_xk', 'f_{xk}', 'Druckfestigkeit senkrecht zu den La…`

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.material.basis]]

## Gebraucht von

- [[opencivil.material.arten]]
- [[opencivil.mauerwerk.kennwerte]]
- [[opencivil.mauerwerk.pruefen]]
- [[opencivil.projekt.projekt]]

## Formeln aus diesem Modul

- [[Bemessungswert der Druckfestigkeit senkrecht zu den Lagerfugen]] · `_durch_gamma`
- [[Bemessungswert der Druckfestigkeit senkrecht zu den Stossfugen]] · `_durch_gamma`
- [[Bemessungswert der Druckfestigkeit senkrecht zu den Stossfugen, vollfugig vermauert]] · `_durch_gamma`
- [[Bemessungswert des Elastizitätsmoduls senkrecht zu den Lagerfugen]] · `_durch_gamma`
- [[Bemessungswert des Schubmoduls]] · `_durch_gamma`
- [[Elastizitätsmodul senkrecht zu den Lagerfugen, kennzeichnend]]
- [[Schubmodul, kennzeichnend]]
