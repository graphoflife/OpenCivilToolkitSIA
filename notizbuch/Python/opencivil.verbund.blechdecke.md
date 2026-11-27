---
erzeugt: fcb0378d3aca
art: modul
tags: [modul]
---
> [!abstract] opencivil/verbund/blechdecke.py
> Blechverbunddecken nach SIA 264:2014, 5.4.
> Paket [[opencivil.verbund]] · [Quelltext](../../opencivil/verbund/blechdecke.py)

## VERANTWORTUNG

Was eine Blechverbunddecke traegt, ohne Rechenwerk und ohne Herleitung, in N,
mm und N/mm² -- die Herleitung schreiben ihre Kennzahlen und Nachweise
([[opencivil.nachweis.qa_blechverbund]]), die Form des Blechs kennt
[[opencivil.querschnitt.profilblech]]:

* die Biegung plastisch wie im Verbundtraeger (5.4.3.2; 5.1.2.1), unter
  negativem Moment ohne das Blech ([[opencivil.verbund.blechdecke#plastisch|plastisch]]);
* die Querkraft (5.4.3.3, (26)): `v_Rd = k_d·τ_cd·d_p·b_0/b_s` je Breite,
  mit `k_d = 0.8` bis `d_p = 150 mm` ([[opencivil.verbund.blechdecke#querkraft|querkraft]]). Darueber
  verweist die Norm auf SIA 262; das rechnet das Werkzeug fuer die Decke
  nicht, und die Zeile bleibt grau;
* der Laengsschub nach der m-k-Methode (5.4.3.5, (28)) mit seinen Angaben
  ([[opencivil.verbund.blechdecke#Laengsschub|Laengsschub]], [[opencivil.verbund.blechdecke#laengsschub|laengsschub]]): die Beiwerte `m` und `k`
  aus Versuchen -- dem Datenblatt des Blechs --, die Spannweite `L`, ob
  das Feld ein Einfeld, ein End- oder ein Innenfeld ist, und wie die Last
  steht;
* die Schlankheit `L/d_p`: bis 26 muss die Durchbiegung nicht gerechnet
  werden (5.4.4.3).


## DIE SCHUBLAENGE (5.4.3.5)

Bei gleichmaessiger Last ueber die ganze Spannweite `L/4`; bei zwei
gleichen Einzellasten, symmetrisch im Feld, der Abstand `a` der Last vom
naechsten Auflager. In einer durchlaufenden Decke gilt fuer `L` die
Spannweite des gleichwertigen Einfelds: `0.9 L` im Endfeld, `0.8 L` im
Innenfeld. Der Abstand `a` bleibt, wie eingegeben (nach Vorgabe, nicht
nachgeschlagen: die Norm sagt nicht, ob er im Ersatzfeld kuerzer wird).
Andere Lasten verlangen Versuche oder Naeherungen; das Werkzeug kennt nur
die beiden.

γ_v BLEIBT:
Wie beim Kopfbolzenduebel rechnet (28) auch mit charakteristischen Werten
mit `γ_v = 1.25` ([[opencivil.verbund.duebel#Konstanten|GAMMA_V]]; nach
Vorgabe, nicht nachgeschlagen).


## DIE BREITE

Der Querschnitt ist so breit, wie die Decke gezeichnet ist: `b = n·b_s`.
Die Schnittgroessen eines Lastfalls gelten fuer diese Breite, wie jede
Einwirkung der Querschnittsanalyse.

## Inhalt

### Feld

```python
class Feld(Wahl)
```

Wo das Feld der Decke liegt -- danach die Spannweite fuer den Laengsschub.

- `EINFELD = 'einfeld'`
- `ENDFELD = 'endfeld'`
- `INNENFELD = 'innenfeld'`

#### Feld.faktor

```python
@property
def faktor(self) -> float
```

Die Spannweite des gleichwertigen Einfelds, als Teil von `L` (5.4.3.5).

#### Feld.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Feld.erklaerung

```python
@property
def erklaerung(self) -> str
```

### Belastung

```python
class Belastung(Wahl)
```

Wie die Last auf dem Feld steht -- danach die Schublaenge `L_s`.

- `GLEICHMAESSIG = 'gleichmaessig'`
- `EINZELLASTEN = 'einzellasten'`

#### Belastung.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Belastung.mit_abstand

```python
@property
def mit_abstand(self) -> bool
```

Ob die Schublaenge der Abstand `a` der Last ist -- sonst kommt sie aus `L`.

#### Belastung.erklaerung

```python
@property
def erklaerung(self) -> str
```

### Laengsschub

```python
@dataclass(frozen=True)
class Laengsschub
```

Was (28) ausser dem Querschnitt braucht -- siehe Dateikopf. `m` und
`k` in N/mm², `L` und `a` in m, wie eingegeben; `None`, solange
eine Angabe fehlt.

- `m: Optional[float]`
- `k: Optional[float]`
- `L: Optional[float]`
- `feld: Feld = Feld.EINFELD`
- `last: Belastung = Belastung.GLEICHMAESSIG`
- `a: Optional[float] = None`

#### Laengsschub.L_ersatz

```python
@property
def L_ersatz(self) -> Optional[float]
```

Die Spannweite des gleichwertigen Einfelds in m -- `None` ohne `L`.

#### Laengsschub.L_s

```python
@property
def L_s(self) -> Optional[float]
```

Die Schublaenge in mm -- `None`, solange fehlt, woraus sie kommt.

#### Laengsschub.fehlt

```python
@property
def fehlt(self) -> List[str]
```

Die Zeichen dessen, was (28) noch fehlt, «m», «L» -- leer, wenn er rechnen kann.

#### Laengsschub.fehlt_in_worten

```python
@property
def fehlt_in_worten(self) -> str
```

Dasselbe im Satz: «der Beiwert m und die Spannweite L» -- leer, wenn nichts fehlt.

#### Laengsschub.fehlt_kurz

```python
@property
def fehlt_kurz(self) -> str
```

Dasselbe fuer die Kachel: «m und k fehlen», «L fehlt» -- leer, wenn nichts fehlt.

### plastisch

```python
def plastisch(verbund: Verbundquerschnitt, zug: Sequence[float], druck: Sequence[float], N: float, M_y: float, bezug: Punkt) -> Tuple[Starrplastisch, Optional[Zustand]]
```

Die Decke starr-plastisch bei `N` in N und `M_y` in N·mm, einachsig um
y (5.4.1.1): je Gruppe mit `zug` und `druck` -- unter negativem
Moment zaehlt das Blech auch gezogen nicht (5.4.3.2). Dazu der Zustand,
dessen Moment die Seite von `M_y` zieht; `None`, wo `N` jenseits
dessen liegt, was die Decke ganz gezogen oder ganz gedrueckt traegt.

### querkraft

```python
def querkraft(tau_cd: float, d_p: float, b_0: float, b_s: float) -> float
```

(26): was die Decke je mm Breite an Querkraft traegt, in N/mm -- `τ_cd` in N/mm².

### laengsschub

```python
def laengsschub(b: float, d_p: float, A_p: float, L_s: float, m: float, k: float) -> float
```

(28): der Laengsschubwiderstand in N -- `A_p` die Flaeche des Blechs ueber `b`.


## Konstanten

- `REFERENZ_FORM = 'SIA 264:2014, Figur 18'`
- `REFERENZ_STATISCHE_HOEHE = 'SIA 264:2014, 5.4.3.3; Figur 9'` – `d_p` reicht in Figur 9 von der Oberkante bis zur Achse des Blechs.
- `REFERENZ_BIEGUNG = 'SIA 264:2014, 5.4.3.2; 5.1.2.1'`
- `REFERENZ_QUERKRAFT = 'SIA 264:2014, 5.4.3.3, (26); Figur 18'`
- `REFERENZ_LAENGSSCHUB = 'SIA 264:2014, 5.4.3.5, (28)'`
- `REFERENZ_SCHUBLAENGE = 'SIA 264:2014, 5.4.3.5'`
- `REFERENZ_SCHLANKHEIT = 'SIA 264:2014, 5.4.4.3'`
- `REFERENZ_EINACHSIG = 'SIA 264:2014, 5.4.1.1'`
- `K_D = 0.8` – Der Beiwert von (26) -- und bis zu welcher statischen Hoehe in mm er gilt.
- `D_P_BIS = 150.0`
- `SCHLANKHEIT = 26.0` – Bis zu welchem `L/d_p` die Durchbiegung nicht gerechnet werden muss (5.4.4.3).
- `ANGABEN = {'m': 'der Beiwert m', 'k': 'der Beiwert k', 'L': 'die Spannweite L',…` – Was (28) ausser dem Querschnitt braucht, je Zeichen in Worten -- fuer die Saetze, die sagen, was davon fehlt ([[opencivil.verbund.blechdecke#Laengsschub.fehlt|Laengsschub.fehlt]]).

## Braucht

- [[opencivil.core.sprache]]
- [[opencivil.core.wahl]]
- [[opencivil.material.basis]]
- [[opencivil.querschnitt.biegung]]
- [[opencivil.querschnitt.geometrie]]
- [[opencivil.querschnitt.plastisch]]
- [[opencivil.verbund.duebel]]
- [[opencivil.verbund.querschnitt]]

## Gebraucht von

- [[opencivil.nachweis.qa_blechverbund]]
- [[opencivil.projekt.beispiele_verbund]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.web.api]]
