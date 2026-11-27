---
erzeugt: 337a4207c298
art: modul
tags: [modul]
---
> [!abstract] opencivil/querschnitt/profilblech.py
> das Profilblech einer Blechverbunddecke.
> Paket [[opencivil.querschnitt]] · [Quelltext](../../opencivil/querschnitt/profilblech.py)

## VERANTWORTUNG

Die Form eines Profilblechs aus den Massen seines Datenblatts
([[opencivil.querschnitt.profilblech#Blechform|Blechform]]): seine Linie, der Beton darueber, wie dick es ist und
wo sein Schwerpunkt liegt. Dazu das Blech als Bewehrungselement der
Querschnittsanalyse ([[opencivil.querschnitt.profilblech#Profilblech|Profilblech]]). Die Nachweise der Decke stehen
in [[opencivil.nachweis.qa_blechverbund]], ihr Eintrag in
[[opencivil.projekt.blechdecken]].


## DIE FORM (SIA 264:2014, Figur 18)

`n` Rippen im Abstand `b_s`. Eine Rippe – der Beton zwischen zwei
Stegen des Blechs – ist oben `b_o` breit, unten `b_u` und `h_p`
hoch; ist sie oben schmaler als unten, ist das Blech hinterschnitten. Ueber
den Rippen liegt der Beton `h_c = h − h_p`. Die Decke liegt mit ihrer
Ecke links unten – der Unterkante der Rippen, dem linken Rand – auf ihrem
Punkt.

`b_0`, die Breite einer Rippe fuer die Querkraft, ist bei einem offenen
Blech die mittlere, `(b_o + b_u)/2`, bei einem hinterschnittenen die
Oeffnung oben, `b_o`.


## DIE DICKE (nach Vorgabe, nicht nachgeschlagen)

Das Datenblatt nennt die Flaeche `A_p` je Meter Breite. Das Werkzeug
verteilt sie gleichmaessig ueber die Abwicklung einer Rippe, ``s = b_s −
b_o + 2·L_w + b_u` mit der Laenge `L_w` eines Stegs: `t = A_p·b_s/s``.
Sicken und Ausrundungen laesst es weg. Damit liegt der Schwerpunkt des
Blechs `e` ueber der Unterkante, und die statische Hoehe ist ``d_p = h −
e`` (Figur 18).


## IM QUERSCHNITT

Das Blech liegt am Rand des Betons, nicht in ihm: es verdraengt keinen.
Jede gerade Strecke geht wie eine verschmierte Linie in den Querschnitt ein
([[opencivil.querschnitt.interaktion#linie_als_bewehrung|linie_als_bewehrung]]), mit ihrem
Teil der Flaeche.


## IM FENSTER DER VORLAGEN

Die Decke kommt wie ein Stahlprofil als ein Element in die Zeichnung, nicht
als Flaechen ([[opencivil.querschnitt.profilblech#Konstanten|VORLAGE]]). Ihre Skizze zeigt die ganze Decke mit ihren
Massen von aussen ([[opencivil.querschnitt.profilblech#skizze|skizze]]), dazu eine Rippe mit ihren eigenen
([[opencivil.querschnitt.profilblech#rippenskizze|rippenskizze]]): bei tausend Millimetern Breite waeren `b_o`,
`b_u` und `h_p` in der ganzen Decke nicht zu lesen.

## Inhalt

### Blechform

```python
@dataclass(frozen=True)
class Blechform
```

Die Masse eines Profilblechs nach seinem Datenblatt, in mm – siehe Dateikopf.

- `ursprung: Punkt` – Die Ecke links unten: die Unterkante der Rippen, der linke Rand.
- `rippen: int`
- `h: float` – Die Dicke der ganzen Decke.
- `h_p: float`
- `b_s: float`
- `b_o: float`
- `b_u: float`
- `A_p: float` – Die Flaeche des Blechs je Meter Breite, in mm²/m.

#### Blechform.breite

```python
@property
def breite(self) -> float
```

#### Blechform.h_c

```python
@property
def h_c(self) -> float
```

Der Beton ueber den Rippen.

#### Blechform.hinterschnitten

```python
@property
def hinterschnitten(self) -> bool
```

#### Blechform.b_0

```python
@property
def b_0(self) -> float
```

Die Breite einer Rippe fuer die Querkraft (Figur 18).

#### Blechform.L_w

```python
@property
def L_w(self) -> float
```

Die Laenge eines Stegs.

#### Blechform.s

```python
@property
def s(self) -> float
```

Die Abwicklung des Blechs je Rippe.

#### Blechform.t

```python
@property
def t(self) -> float
```

Die Dicke des Blechs, gleich ueber die Abwicklung – siehe Dateikopf.

#### Blechform.e

```python
@property
def e(self) -> float
```

Wie hoch der Schwerpunkt des Blechs ueber der Unterkante liegt.

#### Blechform.d_p

```python
@property
def d_p(self) -> float
```

Die statische Hoehe: von der Oberkante zum Schwerpunkt des Blechs (Figur 18).

#### Blechform.flaeche

```python
@property
def flaeche(self) -> float
```

Die Flaeche des Blechs ueber die ganze Breite, in mm².

#### Blechform.linie

```python
@property
def linie(self) -> Tuple[Punkt, ...]
```

Das Blech von links nach rechts: oben, in jede Rippe hinunter und wieder hinauf.

#### Blechform.strecken

```python
@property
def strecken(self) -> Tuple[Strecke, ...]
```

#### Blechform.beton

```python
@property
def beton(self) -> Tuple[Punkt, ...]
```

Der Beton ueber dem Blech, gegen den Uhrzeigersinn.

### Profilblech

```python
@dataclass(frozen=True)
class Profilblech(Bewehrungselement)
```

Das Blech einer Blechverbunddecke – `von` und `bis` sind die Enden
seiner Linie, `flaeche` die des Blechs ueber die ganze Breite.

- `form: Blechform`
- `verschmiert = True`

#### Profilblech.strecken

```python
@property
def strecken(self) -> Tuple[Strecke, ...]
```

#### Profilblech.menge

```python
@property
def menge(self) -> Zelle
```

#### Profilblech.kurzmenge

```python
@property
def kurzmenge(self) -> Zelle
```

#### Profilblech.rissdurchmesser

```python
@property
def rissdurchmesser(self) -> float
```

#### Profilblech.als_bewehrung

```python
def als_bewehrung(self, stahl: int, verdraengt: Verdraengt) -> List[Bewehrung]
```

Je Strecke ihr Teil der Flaeche, ohne den Beton zu verdraengen – siehe Dateikopf.

#### Profilblech.stahlflaechen

```python
def stahlflaechen(self) -> Flaechen
```

### skizze

```python
def skizze(form: Blechform) -> Teile
```

Die Decke fuer das Fenster der Vorlagen: ihr Beton, die Linie ihres
Blechs und ihre zwei Masse von aussen – die Breite unten, «5 × 200 =
1000», die Dicke links. Die Ecke links unten liegt im Ursprung der Form:
sie kommt an den Einsetzpunkt, wie bei den Flaechen.

### rippenskizze

```python
def rippenskizze(form: Blechform) -> Teile
```

Eine Rippe der Decke mit ihren Massen, fuer das Fenster der Vorlagen:
der Abstand `b_s` ueber der Decke, `b_o` ueber der Oeffnung der
Rippe, `b_u` unter ihr, `h_p` rechts und `h` links.

### aus_form

```python
def aus_form(name: str, kennung: str, stahl: Baustoff, form: Blechform) -> Profilblech
```

Das Blech einer Decke mit dieser Form, aus dem Baustoff `stahl`.


## Konstanten

- `VORLAGE = 'blechdecke'` – Unter welchem Schluessel das Fenster der Vorlagen die Decke fuehrt – neben den Flaechen ([[opencivil.querschnitt.vorlagen]]) und dem Stahlprofil.
- `GLEICH = 1e-09` – Wie nah zwei Punkte der Linie liegen duerfen, in mm, ehe sie einer sind: bei `b_o = b_s` stossen die Rippen oben aneinander.

## Braucht

- [[opencivil.core.latex]]
- [[opencivil.material.basis]]
- [[opencivil.querschnitt.bewehrungselemente]]
- [[opencivil.querschnitt.geometrie]]
- [[opencivil.querschnitt.interaktion]]
- [[opencivil.querschnitt.vorlagen]]

## Gebraucht von

- [[opencivil.nachweis.qa_blechverbund]]
- [[opencivil.projekt.aufbau.querschnittsanalyse]]
- [[opencivil.projekt.blechdecken]]
- [[opencivil.web.api]]
- [[opencivil.web.dienst]]
- [[opencivil.web.zeichengeometrie]]
