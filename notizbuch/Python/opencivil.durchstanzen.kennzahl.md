---
erzeugt: b6f33384e581
art: modul
tags: [modul]
---
> [!abstract] opencivil/durchstanzen/kennzahl.py
> was eine Durchstanzstelle ohne Durchstanzbewehrung trägt.
> Paket [[opencivil.durchstanzen]] · [Quelltext](../../opencivil/durchstanzen/kennzahl.py)

## VERANTWORTUNG

Die Kennzahl einer Durchstanzstelle ([[opencivil.durchstanzen.kennzahl#Durchstanzkennzahl|Durchstanzkennzahl]]): der
Durchstanzwiderstand V_Rd,c am Schnittpunkt – dort, wo die Querkraft im
Schnitt um die Stütze so gross ist wie der Widerstand, den sie selbst
zulässt. Gerechnet immer, auch ohne Einwirkung (Benutzer, 2026-11-27); der
Nachweis ([[opencivil.durchstanzen.nachweis|.nachweis]]) bleibt, wie er ist. Ohne Stahlpilz und ohne
Durchstanzbewehrung.


## DER SCHNITTPUNKT

In Näherungsstufe 2 wachsen die Momente im Stützstreifen mit der Stützenkraft
V_d (4.3.6.4.7), mit ihnen ψ (60), und k_r (59) sinkt. Bei V_d = 0 wären ψ = 0
und k_r = 2: ein Widerstand, der nur ohne Last gilt – im Beispiel mit C30/37
866.7 kN statt 503.6 kN. Gesucht ist darum V_d mit:

```
V_d − ΔV = V_Rd,c(ψ(V_d))
```

ΔV ist die Flächenlast im Schnitt (4.3.6.2.6). Die linke Seite wächst mit
V_d, die rechte sinkt nie: es gibt genau einen Schnittpunkt, zwischen 0 und
V_Rd,c(ψ = 0) + ΔV. Gesucht wird er durch Halbieren, gerechnet still mit
denselben Schritten wie der Nachweis ([[opencivil.durchstanzen.nachweis#Stuetzenrechnung|Stuetzenrechnung]]);
geschrieben wird nur der letzte. Darum gilt: liegt die Querkraft eines
Nachweises bei der Kennzahl oder darunter, geht er ohne Durchstanzbewehrung
auf, sonst nicht.

In den Stufen 1 und 3 hängt ψ nicht von V_d ab, V_Rd,c gilt für jede
Stützenkraft. Gesucht wird gleich: so steht in der Herleitung auch dort, bis
zu welcher Stützenkraft es ohne Durchstanzbewehrung geht.


## MIT PLATTENBEREICHEN (4.3.6.2.7)

Derselbe Schnittpunkt an jedem Schnitt, um die Stütze, an jeder Stufe
([[opencivil.durchstanzen.stufen|.stufen]]) und durch verschiedene Dicken ([[opencivil.durchstanzen.weg|.weg]]), je mit seinem
ΔV; es gilt der kleinste. Der Schnitt durch verschiedene Dicken wird bei
jeder Stützenkraft neu gesucht, mit ihrem ψ – wie im Nachweis. Die
Kennzahl ist die Querkraft im Schnitt um die Stütze bei dieser Stützenkraft
– so bleibt sie mit der Querkraft eines Nachweises vergleichbar. Liegt der
Schnittpunkt an einem anderen Schnitt, ist sie kleiner als V_Rd,c um die
Stütze.


## EINHEITEN

SI-Basis.

## Inhalt

### Durchstanzkennzahl

```python
class Durchstanzkennzahl(Stuetzenrechnung, Kennzahlprozedur)
```

Die Kennzahl einer Durchstanzstelle – siehe Dateikopf.

- `THEMA = 'Durchstanzen'`

#### Durchstanzkennzahl.rechne

```python
def rechne(self, e: Eingaben, p: Protokoll) -> Dict[str, Groesse]
```

#### Durchstanzkennzahl._schnittpunkt

```python
def _schnittpunkt(self, e: Eingaben, w: Zwischenwerte, g: Stuetzenschnitt) -> Tuple[float, Schnittort]
```

Die grösste Stützenkraft in N, bei der jeder Schnitt hält, und wo
ihr Schnittpunkt liegt. Je Schnitt still mit den Schritten des
Nachweises; der Schnitt durch verschiedene Dicken zuletzt, nur bis
zur kleinsten Kraft der anderen.

### _beiwerte

```python
def _beiwerte(r: Widerstand) -> Tuple[float, float, float]
```

ψ, k_g und τ_cd an der Stütze – was jeder Schnitt für seinen Widerstand braucht.

### _halbieren

```python
def _halbieren(rest: Callable[[float], float], oben: Optional[float]=None) -> float
```

Die Stützenkraft in N, bei der `rest(V)` null wird – der Widerstand
eines Schnitts und ΔV, weniger V –, durch Halbieren zwischen 0 und
`oben`. Ohne `oben` bis zum Rest bei V = 0: dort ist er sicher
aufgebraucht, denn der Widerstand sinkt nie mit V (Dateikopf).


## Konstanten

- `GENAUIGKEIT = 1.0` – Wie genau die Stützenkraft am Schnittpunkt feststeht, in N.
- `NUR_IM_NACHWEIS = ('V_d',)` – Was nur der Nachweis liest: die Stützenkraft sucht die Kennzahl selbst.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.sprache]]
- [[opencivil.durchstanzen.herleitung]]
- [[opencivil.durchstanzen.nachweis]]
- [[opencivil.durchstanzen.stelle]]
- [[opencivil.durchstanzen.stufen]]
- [[opencivil.durchstanzen.weg]]

## Gebraucht von

- [[opencivil.projekt.aufbau.durchstanzen]]
