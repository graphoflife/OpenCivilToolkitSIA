---
erzeugt: 955f494f2a66
art: modul
tags: [modul]
---
> [!abstract] opencivil/material/beton.py
> Beton nach SIA 262:2025.
> Paket [[opencivil.material]] · [Quelltext](../../opencivil/material/beton.py)

## VERANTWORTUNG

Sortentabelle und Kennwertherleitung fuer Beton. Jeder abgeleitete Kennwert ist
eine eigene Berechnung im Rechenwerk und damit einzeln nachvollziehbar und
einzeln ueberschreibbar.


## ZU DEN EMPIRISCHEN FORMELN

`tau_cd` und `E_cm` sind dimensionell inhomogen -- die Norm setzt dort
stillschweigend voraus, dass in N/mm^2 gerechnet wird. Sie laufen deshalb ueber
[[opencivil.core.einheiten#empirisch|opencivil.core.einheiten.empirisch]], das diese Voraussetzung erzwingt und
die Einheitenkonvention erzwingt. Alle uebrigen Formeln sind einheitenrein und
werden ganz normal gerechnet.


## EIGENSTAENDIG NUTZBAR


```python
from opencivil.core.rechenwerk import Rechenwerk
from opencivil.material.beton import beton

werk = Rechenwerk()
c30 = beton("C30/37").ins_rechenwerk(werk)
loesung = werk.loese(c30.id_von("f_cd"))
print(loesung.wert(c30.id_von("f_cd")))
```

## Inhalt

### betonsorten_zum_anlegen

```python
def betonsorten_zum_anlegen() -> List[str]
```

Die Betonsorten in der Reihenfolge, in der neue angelegt werden -- siehe [[opencivil.material.beton#Konstanten|ERSTER_BETON]].

### _tau_cd

```python
def _tau_cd(f_ck: Groesse, gamma_c: Groesse)
```

SIA 262:2025, 2.4.2.4 -- empirisch, f_ck in N/mm^2.

### _e_cm

```python
def _e_cm(k_e: Groesse, f_cm: Groesse)
```

SIA 262:2025, 3.1.2.3.3 -- empirisch, f_cm in N/mm^2.

### _eta_fc

```python
def _eta_fc(f_ck: Groesse) -> Groesse
```

SIA 262:2025, 2.4.2.3 -- einheitenrein, da nur ein Verhaeltnis eingeht.

### beton

```python
def beton(sorte: str='C30/37', *, name: Optional[str]=None, praefix: Optional[str]=None, abweichungen: Optional[Mapping[str, Groesse]]=None, symbol_index: str='') -> Baustoff
```

Erzeugt einen Beton aus der Sortentabelle.

:param sorte: Bezeichnung aus [[opencivil.material.beton#Konstanten|BETONSORTEN]], z.B. `'C30/37'`.
:param name: abweichender Anzeigename, sonst die Sorte.
:param praefix: eigener Namensraum, falls mehrere Betone derselben Sorte
im Modell vorkommen sollen.
:param abweichungen: Zahlenwerte, die von der Sortentabelle abweichen --
fuer selbst definierte Materialien.

### beton_frei

```python
def beton_frei(name: str, werte: Mapping[str, Groesse], *, praefix: Optional[str]=None) -> Baustoff
```

Erzeugt einen frei definierten Beton ohne Sortentabelle.

Erwartet mindestens `f_ck` und `f_ctm`; alles Weitere kann angegeben
werden, um Normvorgaben zu ersetzen.


## Konstanten

- `BETONSORTEN = {'C12/15': (12.0, 1.6), 'C16/20': (16.0, 1.9), 'C20/25': (20.0, 2.2),…` – Betonsorten nach SIA 262:2025, Tabelle 3.1.2.2.7 -- (f_ck, f_ctm) in N/mm^2. Uebernommen aus der Vorgaengerfassung des Werkzeugs. Vor dem produktiven Einsatz gegen die gedruckte Norm pruefen.
- `ERSTER_BETON = 'C25/30'` – Womit ein neuer Beton anfängt, wenn man in der Oberfläche einen anlegt: C25/30; gibt es den schon, der nächstfestere, und so weiter (Benutzer, 2026-10-15). Nach dem festesten kommen die schwächeren, von unten.
- `BETON_VORLAGEN = (KennwertVorlage(kurzname='f_ck', symbol='f_{ck}', einheit=N_PRO_MM2,…` – Alle Betonkennwerte in der Reihenfolge, in der sie im Bericht erscheinen.

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.material.basis]]

## Gebraucht von

- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.lesen]]
- [[opencivil.web.api]]

## Formeln aus diesem Modul

- [[Beiwert zur Berücksichtigung der Festigkeitsminderung]] · `_eta_fc`
- [[Bemessungswert der Betondruckfestigkeit]]
- [[Bemessungswert der Schubspannungsgrenze]] · `_tau_cd`
- [[Bemessungswert des Elastizitätsmoduls]]
- [[Krümmungsbeiwert der Spannungs-Dehnungs-Beziehung]]
- [[Mittelwert der Zylinderdruckfestigkeit]]
- [[Mittelwert des Elastizitätsmoduls]] · `_e_cm`
