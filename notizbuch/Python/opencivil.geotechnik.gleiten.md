---
erzeugt: da4aa720ec3f
art: modul
tags: [modul]
---
> [!abstract] opencivil/geotechnik/gleiten.py
> das Gleiten eines Flachfundaments in seiner Sohle.
> Paket [[opencivil.geotechnik]] · [Quelltext](../../opencivil/geotechnik/gleiten.py)

## VERANTWORTUNG

Der Nachweis [[opencivil.geotechnik.gleiten#Gleiten|Gleiten]]: je Einwirkungskombination der
Gleitwiderstand in der Sohle nach SIA 267:2013, 8.5.2.2 -- drainiert
T_Rd = N_Ed · tan delta_d, mit delta_k = min(k_delta · phi_k; 35°) nach
8.4.1.1 und tan delta_d = tan delta_k / gamma_phi; undrainiert
T_Rd = b · L · s_u,d, Gl. (32). Das Fundament und seine Bemessungswerte
stehen in [[opencivil.geotechnik.fundament|fundament]].


## EINHEITEN

Alles in SI-Basis; die Winkel als Groessen in Grad.

## Inhalt

### Gleiten

```python
class Gleiten(Fundamentnachweis)
```

Der Gleitwiderstand in der Sohle je Kombination nach SIA 267:2013,
8.5.2.2 -- drainiert aus der Reibung, undrainiert aus der Scherfestigkeit
--, ohne Erdwiderstand, wie im Buch für eine geneigte Sohle.

- `THEMA = 'Gleiten'`
- `ART = 'GL'`
- `FELD = 'gleiten'`
- `BODEN = {Verhalten.DRAINIERT: ('phi_k', 'gamma_phi', 'delta_faktor', 'c_eff')…`
- `MASSE = ('b', 'L')`

#### Gleiten.pruefe

```python
def pruefe(self, e: Eingaben, p: Protokoll) -> Ausfuehrung
```

#### Gleiten._sohlreibung

```python
def _sohlreibung(self, e: Eingaben, p: Protokoll) -> Wert
```

delta_k nach SIA 267:2013, 8.4.1.1, und daraus der Bemessungswert delta_d.

#### Gleiten._widerstand

```python
@staticmethod
def _widerstand(e: Eingaben, p: Protokoll, zw: Zwischenwerte, N: Wert, delta: Optional[Wert]) -> Wert
```

Drainiert die Reibung unter N, undrainiert die Scherfestigkeit auf der Sohlfläche.


## Konstanten

- `SOHLREIBUNG_GRENZE = 35.0` – Wie gross der Sohlreibungswinkel delta_k höchstens ist, in Grad -- SIA 267:2013, 8.4.1.1.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.nachweis]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.geotechnik.fundament]]
- [[opencivil.geotechnik.verhalten]]

## Gebraucht von

- [[opencivil.projekt.aufbau.grundbruch]]

## Formeln aus diesem Modul

- [[Bemessungswert des Sohlreibungswinkels]] · `Gleiten._sohlreibung`
- [[Gleitwiderstand]] · `Gleiten._widerstand`
- [[Reibungswinkel der Sohlfuge]] · `Gleiten._sohlreibung`
