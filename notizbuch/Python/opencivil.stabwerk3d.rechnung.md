---
erzeugt: 22911d0b604b
art: modul
tags: [modul]
---
> [!abstract] opencivil/stabwerk3d/rechnung.py
> das 3D-Balkensystem im Rechenwerk.
> Paket [[opencivil.stabwerk3d]] · [Quelltext](../../opencivil/stabwerk3d/rechnung.py)

## VERANTWORTUNG

Wie das ebene Balkensystem ([[opencivil.stabwerk.rechnung]]), im Raum:
je Querschnitt `A`, `I_y`, `I_z` und `I_T`, je Paar aus
Querschnitt und Material `EA`, `EI_y`, `EI_z` und `GI_T` und das
Eigengewicht, und eine Prozedur, die das System rechnet
([[opencivil.stabwerk3d.system|system]]) und ihre Herleitung schreibt
([[opencivil.stabwerk3d.herleitung|herleitung]]). Was beide gleich tun, steht in
[[opencivil.stabwerk.rechnung#Stabwerksrechnung|Stabwerksrechnung]].


## STEIFIGKEIT -- NACH VORGABE, NICHT NACHGESCHLAGEN

Wie in der Ebene, die Torsion mit `G_cm` des Betons, `G_a` des
Baustahls oder G von Hand -- am ungerissenen Querschnitt und nach St.
Venant, ohne Woelbkrafttorsion. Die Herleitung sagt es, das TODO fuehrt es.

## Inhalt

### Raumbefund

```python
class Raumbefund(Systembefund)
```

Was die Rechnung im Raum fand -- wie in der Ebene, mit den Verlaeufen des Raums.

### Balkensystem3d

```python
class Balkensystem3d(Stabwerksrechnung)
```

Ein 3D-Balkensystem, fertig fuer das Rechenwerk.

- `WAS = '3D-Balkensystem'`
- `KENNWERTE = RAEUMLICH`
- `STEIFIGKEITEN = (DEHNSTEIFIGKEIT, Steifigkeitsformel('EI_y', KNM2, 'Biegesteifigkeit …`
- `MATERIALKENNWERTE = (E_MODUL, DICHTE, SCHUBMODUL)`


## Konstanten

- `RAUMKENNWERTE = stoffkennwerte((E_MODUL, DICHTE, SCHUBMODUL))` – Welche Kennwerte eines Baustoffs ein Stab im Raum aus ihm nimmt.

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.protokoll]]
- [[opencivil.stabwerk.modell]]
- [[opencivil.stabwerk.rechnung]]
- [[opencivil.stabwerk.stabquerschnitt]]
- [[opencivil.stabwerk.system]]
- [[opencivil.stabwerk3d.herleitung]]
- [[opencivil.stabwerk3d.modell]]
- [[opencivil.stabwerk3d.system]]
- [[opencivil.stabwerk3d.verlauf]]

## Gebraucht von

- [[opencivil.projekt.aufbau.balkensystem3d]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.stabwerk3d.herleitung]]
- [[opencivil.web.api]]
- [[opencivil.web.balkendaten]]
