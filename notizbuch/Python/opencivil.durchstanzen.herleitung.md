---
erzeugt: 371fc7c1c0fb
art: modul
tags: [modul]
---
> [!abstract] opencivil/durchstanzen/herleitung.py
> wie ein Nachweisschnitt in der Herleitung steht.
> Paket [[opencivil.durchstanzen]] · [Quelltext](../../opencivil/durchstanzen/herleitung.py)

## VERANTWORTUNG

Die Schritte, die jeder Schnitt durchläuft -- was von ihm nicht zählt, k_e
nach (57), der wirksame Umfang, die Querkraft und der Widerstand (58) --, einmal
geschrieben: für den Schnitt um die Stütze ([[opencivil.durchstanzen.nachweis|.nachweis]]), um die
äussersten Anker und um einen Stahlpilz ([[opencivil.durchstanzen.mit_bewehrung|.mit_bewehrung]]). Die Zahlen
kommen aus der [[opencivil.durchstanzen.pruefung#Schnittpruefung|Schnittpruefung]], sie werden hier nicht
gerechnet. Weil es dieselben Formeln sind, hat jede in der Formelsammlung
eine Seite, gleich an welchem Schnitt sie steht.


## DIE ZEICHEN ([[opencivil.durchstanzen.herleitung#Index|Index]])

Um die Stütze u_0, u_red, u, V_{d,red} und V_{Rd,c}; aussen um die Anker mit
«out», um den Pilz mit «P», der Index zuletzt: u_{red,out}, V_{d,P} ...


## EINHEITEN

SI-Basis.

## Inhalt

### Index

```python
@dataclass(frozen=True)
class Index
```

Wie die Werte eines Schnitts heissen: `zeichen` hängt am Symbol -- leer um
die Stütze, «out» aussen um die Anker, «P» um den Pilz --, `vorsilbe` an
den Namen der Zwischenwerte, damit die Leisten um die Stütze und um den
Pilz nebeneinander stehen können.

- `zeichen: str = ''`
- `vorsilbe: str = ''`

#### Index.name

```python
def name(self, grund: str) -> str
```

#### Index.unten

```python
def unten(self, *teile: str) -> str
```

Der Index eines Symbols, der eigene zuletzt: `unten("red")` -- «red» oder «red,out».

#### Index.symbol

```python
def symbol(self, grund: str, *teile: str) -> str
```

`symbol("V", "d")` -- «V_{d,out}»; ohne Index «V_d», «u».

### rand

```python
def rand(p: Protokoll, w: Zwischenwerte, a: Auswertung, *, ix: Index, titel: str, referenz: str) -> Wert
```

u_0: der Schnitt, soweit er in der Platte liegt.

### abzuege

```python
def abzuege(p: Protokoll, w: Zwischenwerte, a: Auswertung, u_0: Wert, *, ix: Index, ecken_text: str, ecken_referenz: str, ecken: bool=True) -> Wert
```

Was vom Schnitt nicht zählt -- neben den Ecken und hinter Aussparungen
(Figur 23) -- und was bleibt, u_red. `ecken` falsch, wo u_0 die Ecken
schon nicht mitzählt (die Formeln um Wandende und Wandecke). Die Zahl ist
die der Auswertung, mit der auch die Prüfung rechnet.

### k_e

```python
def k_e(p: Protokoll, w: Zwischenwerte, a: Auswertung, e_u: Tuple[float, float], *, ix: Index) -> Wert
```

k_e nach (57): b aus der Fläche im Schnitt, e_u von seinem Schwerpunkt
zur Resultierenden der Auflagerkraft -- je Komponente, in m.

### wirksam

```python
def wirksam(p: Protokoll, w: Zwischenwerte, k_e: Wert, u_red: Wert, *, ix: Index, titel: str) -> Wert
```

Der wirksame Umfang u = k_e · u_red.

### querkraft

```python
def querkraft(p: Protokoll, w: Zwischenwerte, e: Eingaben, s: Schnittpruefung, *, ix: Index, titel_last: str, titel: str) -> Wert
```

Die Querkraft, die den Schnitt kreuzt: V_d ohne die Flächenlast darin
(4.3.6.2.6). `titel_last` sagt, was die Flächenlast ist.

### widerstand

```python
def widerstand(p: Protokoll, w: Zwischenwerte, s: Schnittpruefung, *, ix: Index, k_r: Wert, tau_cd: Wert, d_v: Wert, u: Wert, titel: str, referenz: str) -> Wert
```

V_Rd,c nach (58) an diesem Schnitt.


## Konstanten

- `STUETZE = Index()`

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.durchstanzen.pruefung]]
- [[opencivil.durchstanzen.schnitt]]

## Gebraucht von

- [[opencivil.durchstanzen.mit_bewehrung]]
- [[opencivil.durchstanzen.nachweis]]

## Formeln aus diesem Modul

- [[Beiwert der Momentenübertragung]] · `k_e`
- [[Bemessungswert der Querkraft im Nachweisschnitt]] · `querkraft`
- [[Durchmesser des flächengleichen Kreises]] · `k_e`
- [[Durchstanzwiderstand ohne Durchstanzbewehrung]] · `widerstand`
- [[Flächenlast innerhalb des Nachweisschnitts]] · `querkraft`
- [[Nachweisschnitt ohne das, was nicht zählt]] · `abzuege`
- [[Wirksamer Umfang des Nachweisschnitts]] · `wirksam`
