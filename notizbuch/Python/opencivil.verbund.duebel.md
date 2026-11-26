---
erzeugt: 807db41872a6
art: modul
tags: [modul]
---
> [!abstract] opencivil/verbund/duebel.py
> Kopfbolzenduebel nach SIA 264:2014, 6.1.
> Paket [[opencivil.verbund]] · [Quelltext](../../opencivil/verbund/duebel.py)

## VERANTWORTUNG

Was ein Kopfbolzenduebel traegt und wie viele es braucht, ohne Herleitung,
in N, mm und N/mm² -- die Herleitung schreiben die Kennzahlen
([[opencivil.nachweis.qa_verbund_kennzahlen]]) und die Nachweise je
Lastfall ([[opencivil.nachweis.qa_verbund]]):

* ob Stahl und Beton voll verduebelt angenommen sind oder mit Kopfbolzen-
  duebeln gerechnet wird ([[opencivil.verbund.duebel#Verduebelung|Verduebelung]]);
* der Duebel ([[opencivil.verbund.duebel#Kopfbolzen|Kopfbolzen]]): Schaftdurchmesser `d` von 16 bis
  25 mm, Laenge `h_D` ab `4 d` -- so ist er verformungsfaehig
  (6.1.1.3), und nur fuer ihn nennt 6.1.2.1 einen Widerstand --,
  Zugfestigkeit `f_u`; ihre Vorgabe 450 N/mm² ist die der
  Kopfbolzenduebel in SIA 263:2013, Tabelle 3. Die Grenzen weisen schon
  die Felder ab ([[opencivil.projekt.querschnittsanalyse#QuerschnittsanalyseEintrag|QuerschnittsanalyseEintrag]]);
* sein Schubwiderstand `P_Rd` (6.1.2.1): der kleinere aus der
  Betonstauchung (30) und dem Versagen des Duebels (31), mit `f_u`
  hoechstens 500 N/mm² und `γ_v = 1.25`;
* je Lastfall der Abschnitt bis zum Momentennullpunkt ([[opencivil.verbund.duebel#Abschnitt|Abschnitt]]):
  wie viele Duebel dort sitzen, `N`, und wie weit die Momentennullpunkte
  auseinander liegen, `L_e`;
* der kleinste Verduebelungsgrad ([[opencivil.verbund.duebel#eta_min|eta_min]], 6.1.1.6, (29)) -- und
  ob ein Lastfall im Bereich negativer Momente liegt, wo er eins ist
  ([[opencivil.verbund.duebel#negativ|negativ]]).


## DIE DUEBEL TRAGEN DIE KRAFT DES BETONS

Zwischen dem Schnitt und dem Momentennullpunkt tragen die `N` Duebel die
Kraft, die Beton und Betonstahl ausserhalb der Profile zusammen im Schnitt
haben -- Kammerbeton zaehlt zum Stahl
([[opencivil.verbund.querschnitt#Verbundquerschnitt.fuge|fuge]]); am
Momentennullpunkt haben sie keine (nach Vorgabe, nicht nachgeschlagen: mit
einer Normalkraft kann dort schon ein Teil im Beton stecken). Die volle
Verduebelung braucht `N_f = |N_c,f| / P_Rd` Duebel, `N_c,f` die Kraft
des Betons im plastischen Zustand bei voller Verduebelung; `η = N/N_f` ist
der Verduebelungsgrad.

γ_v BLEIBT:
Auch wo die Tragsicherheit charakteristische Werte waehlt, rechnet der
Duebel mit `γ_v = 1.25`: er ist kein Material des Projekts, das eine
eigene Wahl haette (nach Vorgabe, nicht nachgeschlagen).

(29) -- UND OHNE DOPPELTE SYMMETRIE:
Teilweise verduebelt sein darf ein Traeger nur im Bereich positiver Momente
(6.1.1.6), und dort nur, wenn `η` die Grenze von (29) haelt; (29) gilt
fuer doppelsymmetrische Stahlprofile, mit `f_y` des Profils. Fuer andere
nennt die Norm keine Grenze; das Werkzeug verlangt dort volle Verduebelung,
`η ≥ 1` (nach Vorgabe, nicht nachgeschlagen).


## DER BEREICH NEGATIVER MOMENTE

Im gezeichneten Querschnitt sagt das Vorzeichen eines Moments nicht, ob es
positiv ist: die Platte kann oben oder unten liegen. Das Werkzeug sieht den
Bereich negativer Momente, wo Beton und Betonstahl ausserhalb der Profile bei
voller Verduebelung
zusammen gezogen sind oder die plastische Nulllinie die Seite zieht, auf der
der Beton liegt ([[opencivil.verbund.duebel#negativ|negativ]]) -- so auch ueber Kammerbeton, der
gedrueckt mehr traegt als der gezogene Betonstahl der Platte (nach Vorgabe,
nicht nachgeschlagen).

## Inhalt

### Verduebelung

```python
class Verduebelung(Wahl)
```

Wie Stahl und Beton verbunden sind -- einmal fuer die ganze Analyse.

- `VOLL = 'voll'`
- `KOPFBOLZEN = 'kopfbolzen'`

#### Verduebelung.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Verduebelung.erklaerung

```python
@property
def erklaerung(self) -> str
```

### Kopfbolzen

```python
@dataclass(frozen=True)
class Kopfbolzen
```

Ein Kopfbolzenduebel -- siehe Dateikopf. `d` und `h` in mm, `f_u` in N/mm².

- `d: float`
- `h: float`
- `f_u: float`

#### Kopfbolzen.f_u_wirksam

```python
@property
def f_u_wirksam(self) -> float
```

`f_u`, hoechstens 500 N/mm² (6.1.2.1).

#### Kopfbolzen.betonstauchung

```python
def betonstauchung(self, f_ck: float, E_cm: float) -> float
```

(30): was der Beton um den Duebel traegt, in N -- `f_ck` und `E_cm` in N/mm².

#### Kopfbolzen.schaft

```python
def schaft(self) -> float
```

(31): was der Schaft traegt, in N.

### Abschnitt

```python
@dataclass(frozen=True)
class Abschnitt
```

Was ein Lastfall ueber die Duebel weiss: wie viele zwischen seinem
Schnitt und dem naechsten Momentennullpunkt sitzen, `N` in (29), und
wie weit die Momentennullpunkte auseinander liegen, `L_e` in m. Leer,
solange es nicht angegeben ist.

- `anzahl: Optional[int] = None`
- `L_e: Optional[float] = None`

### negativ

```python
def negativ(n: Tuple[float, float], zum_beton: Optional[Tuple[float, float]], N_c: float) -> bool
```

Ob ein Lastfall im Bereich negativer Momente liegt -- siehe Dateikopf:
`N_c` die Kraft in Beton und Betonstahl ausserhalb der Profile bei
voller Verduebelung, in N
(Zug positiv), `n` die Zugrichtung ihrer Nulllinie, `zum_beton` vom
Baustahl zum Beton (`None`, wo der Beton keine Seite hat).

### eta_min

```python
def eta_min(f_y: float, L_e: float) -> float
```

Der kleinste Verduebelungsgrad nach (29) fuer ein doppelsymmetrisches
Profil mit der Fliessgrenze `f_y` in N/mm², `L_e` in m.


## Konstanten

- `REFERENZ_P_RD = 'SIA 264:2014, 6.1.2.1, (30) und (31)'`
- `REFERENZ_GRAD = 'SIA 264:2014, 6.1.1.6, (29)'`
- `REFERENZ_VOLL = 'SIA 264:2014, 6.1.1.6'`
- `REFERENZ_LAENGE = 'SIA 264:2014, 6.1.1.3'`
- `REFERENZ_F_U = 'SIA 263:2013, 3.4.3, Tabelle 3'`
- `GAMMA_V = 1.25` – Der Widerstandsbeiwert der Verduebelung (6.1.2.1).
- `BETONSTAUCHUNG = 0.29` – Die Beiwerte von (30) und (31).
- `SCHAFT = 0.8`
- `LAENGE_IN_D = 4.0`
- `F_U_HOECHSTENS = 500.0` – Bis wohin `f_u` zaehlt, in N/mm² (6.1.2.1) -- und die Vorgabe aus SIA 263, Tabelle 3.
- `F_U_VORGABE = 450.0`
- `F_Y_BEZUG = 355.0` – (29): der Bezug der Fliessgrenze in N/mm², die Beiwerte, die Untergrenze und bis wohin `L_e` in m die Formel gilt -- darueber verlangt sie volle Verduebelung.
- `GRAD_AB = 0.4`
- `L_E_BIS = 25.0`

## Braucht

- [[opencivil.core.wahl]]

## Gebraucht von

- [[opencivil.nachweis.qa_verbund]]
- [[opencivil.nachweis.qa_verbund_kennzahlen]]
- [[opencivil.projekt.aufbau.querschnittsanalyse]]
- [[opencivil.projekt.beispiele]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.web.api]]
