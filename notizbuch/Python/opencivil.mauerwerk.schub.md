---
erzeugt: 146b29bc72ac
art: modul
tags: [modul]
---
> [!abstract] opencivil/mauerwerk/schub.py
> die Nachweise des Schubs in der Ebene einer Wand.
> Paket [[opencivil.mauerwerk]] · [Quelltext](../../opencivil/mauerwerk/schub.py)

## VERANTWORTUNG

Je Pfeiler und Kombination die beiden Bedingungen des einfachen Nachweises
nach SIA 266:2015, 4.3.2.2: die geneigte Druckstrebe ([[opencivil.mauerwerk.schub#Schub|Schub]],
Gl. (13)) und das Gleiten in der Lagerfuge ([[opencivil.mauerwerk.schub#Gleiten|Gleiten]], Gl. (14)).
Querkraft, Normalkraft und Moment am Fuss kommen aus dem Abtrag der Wand
([[opencivil.mauerwerk.lasten|lasten]], [[opencivil.mauerwerk.scheibe|scheibe]]);
ohne Querkraft gibt es keinen Nachweis. Wie bei der Normalkraft lässt sich
keiner führen, wo der Pfeiler nicht gedrückt ist (4.1.2).


## DIE DRUCKSTREBE

(Gl. (13))
Die Resultierende aus N_xd und V_d geht als Strebe durch den Pfeiler,
geneigt um tan α = V_d / N_xd. Geneigt trägt das Mauerwerk nur f_yd
(Figur 7), am Fuss auf der gedrückten Länge l_2 = l_w − 2 · M_z2d / N_xd:
N_xd ≤ f_yd · l_2 · t · cos² α. Steht die Normalkraft quer zur Wand
ausmittig, gilt 4.3.3.1: die Strebe trägt nur auf der Dicke
t_nom = t_w − 2 · e_z, mit e_z der grössten Ausmitte der verformten Wand
unter N_xd auf der Länge l_2 (4.3.1.3, [[opencivil.mauerwerk.knicken|knicken]]);
findet die Wand dort kein Gleichgewicht, gilt vereinfacht
t_nom = 0.25 · t_w. Die Norm verlangt mit t_nom den Nachweis nach Figur 9
(Gl. (18)); das Werkzeug rechnet ihn mit dem einfachen der Gl. (13), denn
der erweiterte nach 4.3.2.3 legt der Strebe nur Druck zu (Gl. (15)) – nach
Vorgabe, nicht nachgeschlagen, auf der sicheren Seite.


## DAS GLEITEN

(Gl. (14))
Steiler als arctan μ_d kann die Strebe nicht stehen: V_d / N_xd ≤ μ_d,
nach V_d aufgelöst V_d ≤ V_Rd = μ_d · N_xd.


## EINHEITEN

SI-Basis.

## Inhalt

### Schubnachweis

```python
class Schubnachweis(Wandnachweis)
```

Was beide teilen: Querkraft und Normalkraft am Fuss – ohne Querkraft
kein Nachweis, ohne Druck keiner, der sich führen lässt.

#### Schubnachweis.stelle

```python
def stelle(self, p: Protokoll, befund: 'Wandbefund', s: Stelle) -> Stellenausgang
```

#### Schubnachweis.gedrueckt

```python
def gedrueckt(self, p: Protokoll, befund: 'Wandbefund', s: Stelle, pf: Pfeiler, a: Abtrag, zw: Zwischenwerte, V: Wert, N: Wert) -> Stellenausgang
```

Der Nachweis eines gedrückten Pfeilers mit Querkraft.

### Schub

```python
class Schub(Schubnachweis)
```

Die geneigte Druckstrebe – siehe Dateikopf.

- `LANGNAME = 'Schub'`
- `ART = 'V'`
- `FELD = 'schub'`

#### Schub.ansatz

```python
def ansatz(self, p: Protokoll, befund: 'Wandbefund') -> None
```

#### Schub.gedrueckt

```python
def gedrueckt(self, p: Protokoll, befund: 'Wandbefund', s: Stelle, pf: Pfeiler, a: Abtrag, zw: Zwischenwerte, V: Wert, N: Wert) -> Stellenausgang
```

#### Schub._dicke

```python
@staticmethod
def _dicke(p: Protokoll, zw: Zwischenwerte, befund: 'Wandbefund', a: Abtrag, pf: Pfeiler, N: Wert, l_2: Wert) -> Wert
```

t_nom: auf dieser Dicke trägt die Strebe – t_w, wo die Normalkraft mittig steht.

### Gleiten

```python
class Gleiten(Schubnachweis)
```

Das Gleiten in der Lagerfuge – siehe Dateikopf.

- `LANGNAME = 'Gleiten'`
- `ART = 'G'`
- `FELD = 'gleiten'`

#### Gleiten.ansatz

```python
def ansatz(self, p: Protokoll, befund: 'Wandbefund') -> None
```

#### Gleiten.gedrueckt

```python
def gedrueckt(self, p: Protokoll, befund: 'Wandbefund', s: Stelle, pf: Pfeiler, a: Abtrag, zw: Zwischenwerte, V: Wert, N: Wert) -> Stellenausgang
```


## Konstanten

- `REFERENZ_GL_13 = 'SIA 266:2015, 4.3.2.2, Gl. (13), Figur 7 und 8'` – Wo die Regeln stehen.
- `REFERENZ_GL_14 = 'SIA 266:2015, 4.3.2.2, Gl. (14)'`
- `REFERENZ_T_NOM = 'SIA 266:2015, 4.3.3.1'`
- `T_NOM_MIN = 0.25` – So dünn rechnet eine Wand mit ausmittiger Normalkraft höchstens, in Dicken – 4.3.3.1.

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.nachweis]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.mauerwerk.knicken]]
- [[opencivil.mauerwerk.lasten]]
- [[opencivil.mauerwerk.modell]]
- [[opencivil.mauerwerk.nachweise]]
- [[opencivil.mauerwerk.werk]]

## Gebraucht von

- [[opencivil.projekt.aufbau.mauerwerk]]

## Formeln aus diesem Modul

- [[Dicke einer Schubwand mit ausmittiger Normalkraft]] · `Schub._dicke`
- [[Neigung der Druckstrebe in einem Pfeiler]] · `Schub.gedrueckt`
- [[Widerstand der Druckstrebe in einem Pfeiler]] · `Schub.gedrueckt`
- [[Widerstand eines Pfeilers gegen Gleiten]] · `Gleiten.gedrueckt`
