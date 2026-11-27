---
erzeugt: 7f7b7cae8ff7
art: modul
tags: [modul]
---
> [!abstract] opencivil/verbund/stuetze.py
> eine Verbundstuetze nach SIA 264:2014, 5.3.
> Paket [[opencivil.verbund]] · [Quelltext](../../opencivil/verbund/stuetze.py)

## VERANTWORTUNG

Was der Nachweis einer Verbundstuetze braucht, ohne Herleitung, in N, mm und
N/mm²; die Herleitung schreibt [[opencivil.nachweis.qa_verbund_stuetze]].
Der Stab hat den gezeichneten Querschnitt; ein Fall gibt ihm die Druckkraft
und ihren staendigen Anteil, die groessten Momente 1. Ordnung, die
Verhaeltnisse ψ der Endmomente, die Knicklaengen und die Laenge der Stuetze
([[opencivil.stahlbau.stabilitaet#Stabfall|Stabfall]]).


## DER QUERSCHNITT

einmal je Analyse ([[opencivil.verbund.stuetze#Stuetze|Stuetze]])
* Die Art nach Tabelle 7 ([[opencivil.verbund.stuetze#querschnittsart|querschnittsart]]): ein einziges I-Profil
  oder Rohr aus der Profiltabelle, ganz einbetoniert, kammerbetoniert oder
  mit Beton gefuellt (5.3.1.1). Andere -- ein Rohr mit einem Profil darin,
  zwei Profile, ein Traeger unter einer Platte -- kennt Tabelle 7 nicht.
* Doppelsymmetrisch und konstant (5.3.2.1), `0.2 ≤ h/b ≤ 5` (5.3.2.3)
  und die Grenzen der Tabelle 6 gegen das lokale Beulen (5.3.1.7) -- das
  ganz einbetonierte Profil braucht keine.
* Je Gruppe Flaeche und Traegheitsmomente um die Mitte des Profils
  ([[opencivil.verbund.stuetze#Werkstoff|Werkstoff]]); der Betonstahl zaehlt hoechstens mit 6 % der
  Betonflaeche (5.3.2.2).
* `N_pl,Rd` (14) -- im gefuellten Rohr mit 1.0 statt 0.85 (5.3.2.5) --,
  `N_pl,Rk` mit γ = 1 (16) und `δ` (13) zwischen 0.2 und 0.9 (5.3.1.2).


## JE FALL ([[opencivil.verbund.stuetze#rechnen|rechnen]])

* `E_c,eff` (19) mit dem staendigen Anteil der Normalkraft und der
  Kriechzahl der Analyse.
* Die Achse ohne Moment knickt ([[opencivil.verbund.stuetze#Knicken|Knicken]]): `(EI)_eff,λ` (17),
  `N_cr` (20), `λ̄` (16) hoechstens 2.0, `χ_K` nach SIA 263 (8) mit
  der Kurve der Tabelle 7, `N_Ed ≤ χ_K N_pl,Rd` (15) -- 5.3.4.2.
* Die Achse mit Moment ([[opencivil.verbund.stuetze#Biegeachse|Biegeachse]]): `(EI)_eff,d` (22),
  `N_cr,eff` (23) mit der Laenge der Stuetze, `k` (24) mit `ω` nach
  SIA 263, die Ersatzimperfektion `e_0` der Tabelle 7:
  `M_Ed,II = k |M_Ed| + k_0 |N_Ed| e_0`; `μ_d = M_pl,N,Rd/M_pl,Rd` aus
  rechteckigen Spannungsbloecken (Figur 7, 5.3.4.4) und (25) mit 0.9, fuer
  S420 und S460 0.8. Zweiachsig linear (5.3.5).


## NACH VORGABE, NICHT NACHGESCHLAGEN

* Doppelsymmetrisch heisst: je Gruppe liegt der Schwerpunkt keinen
  Millimeter neben der Mitte des Profils, und `|I_yz|` um sie erreicht
  kein Hundertstel von `√(I_y I_z)`.
* Ganz einbetoniert heisst: acht Punkte einen Millimeter ausserhalb des
  umschreibenden Rechtecks des Profils -- Ecken und Mitten der Seiten --
  liegen im Beton. Kammerbetoniert: Beton deckt den Steg beidseits und
  jeden Flansch innen
  ([[opencivil.verbund.querschnitt#Verbundquerschnitt.kammerbetoniert|kammerbetoniert]]),
  ausserhalb des Profils liegt nichts. Gefuellt: in der Mitte des Rohrs
  liegt Beton, ausserhalb nichts.
* Der Betonstahl ueber 6 % der Betonflaeche zaehlt in jedem Stab
  gleichmaessig weniger -- auch in `M_pl` und `EI`.
* Die Imperfektion waechst mit `k_0 = 1/(1 - N_Ed/N_cr,eff)`, also mit
  `ω = 1` wie unter einer Querlast; zweiachsig wirkt sie in beiden Achsen
  zugleich.
* Zweiachsig: `Σ M_Ed,II/(μ_d M_pl,Rd) ≤ 0.9` (0.8) -- 5.3.5 nennt die
  lineare Interaktion, aber keine Grenze; die von (25) liegt auf der
  sicheren Seite.
* `μ_d` hoechstens eins: ob das Moment aus der Normalkraft selbst
  entsteht, weiss das Werkzeug nicht (5.3.4.6).
* Ein Rohr mit mehr als 6 % Betonstahl rechnet mit Kurve b, wie bis 6 %:
  Tabelle 7 endet dort, und mehr zaehlt nach 5.3.2.2 nicht.
* Die Theorie 2. Ordnung rechnet es immer, auch wo (21) sie erliesse.
* Eine Knicklaenge null heisst gehalten: um diese Achse knickt die Stuetze
  nicht, und ein Moment um sie waechst nicht.


## VORZEICHEN

N \< 0 Druck; M_y > 0 zieht unten, M_z > 0 links -- um die Mitte des
Profils, die bei einer doppelsymmetrischen Stuetze der Schwerpunkt ist.

## Inhalt

### Art

```python
class Art(Enum)
```

Wie Profil und Beton nach Tabelle 7 zusammen liegen -- siehe Dateikopf.

- `EINBETONIERT = 'ganz einbetoniert'`
- `KAMMERBETONIERT = 'kammerbetoniert'`
- `ROHR = 'mit Beton gefüllt'`

### _art_bei

```python
def _art_bei(verbund: Verbundquerschnitt, p: Punkt) -> Optional[Baustoffart]
```

Die Art des Materials an `p` -- `None` in einer Aussparung oder daneben.

### _rundum

```python
def _rundum(teil: Teil) -> List[Punkt]
```

Acht Punkte `NEBEN` ausserhalb des umschreibenden Rechtecks -- Ecken und Seitenmitten.

### querschnittsart

```python
def querschnittsart(verbund: Verbundquerschnitt) -> Tuple[Optional[Art], str]
```

Die Art nach Tabelle 7 (siehe Dateikopf) -- oder `None` und warum
Tabelle 7 den Querschnitt nicht kennt.

### Werkstoff

```python
@dataclass(frozen=True)
class Werkstoff
```

Eine Gruppe als Teil der Stuetze, um die Mitte des Profils: Flaeche in
mm², wie weit ihr Schwerpunkt neben der Mitte liegt, in mm, und ihre
Traegheitsmomente in mm⁴.

- `gruppe: int`
- `name: str`
- `art: Baustoffart`
- `A: float`
- `versatz: float`
- `I_y: float`
- `I_z: float`
- `I_yz: float`

#### Werkstoff.I

```python
def I(self, achse: str) -> float
```

### _werkstoffe

```python
def _werkstoffe(verbund: Verbundquerschnitt, mitte: Punkt) -> Tuple[Werkstoff, ...]
```

Je Gruppe ihre Werte um `mitte` -- Beton ohne, was Stahl und Staebe verdraengen.

### Festigkeiten

```python
@dataclass(frozen=True)
class Festigkeiten
```

Je Gruppe in N/mm²: gezogen und gedrueckt mit der Wahl der
Tragsicherheit, gedrueckt charakteristisch -- der Beton beide Male mit
seinem Umrechnungsfaktor -- und der Elastizitaetsmodul: `E_a`,
`E_cm` oder `E_s`.

- `zug: Tuple[float, ...]`
- `druck: Tuple[float, ...]`
- `druck_k: Tuple[float, ...]`
- `E: Tuple[float, ...]`

### Stuetze

```python
class Stuetze
```

Der Querschnitt als Verbundstuetze -- siehe Dateikopf. `eps` ist `ε`
des Profils, `hochfest`, ob es S420 oder S460 ist.

#### Stuetze.der_art

```python
def der_art(self, art: Baustoffart) -> List[Werkstoff]
```

#### Stuetze.flaeche

```python
def flaeche(self, art: Baustoffart) -> float
```

#### Stuetze.rho_s

```python
@cached_property
def rho_s(self) -> float
```

`A_s/A_c`, wie gezeichnet.

#### Stuetze.anteil_s

```python
@cached_property
def anteil_s(self) -> float
```

Mit welchem Anteil der Betonstahl zaehlt: hoechstens 6 % der Betonflaeche (5.3.2.2).

#### Stuetze.zaehlt

```python
def zaehlt(self, w: Werkstoff) -> float
```

#### Stuetze.unsymmetrisch

```python
@cached_property
def unsymmetrisch(self) -> str
```

Warum die Stuetze nicht doppelsymmetrisch ist -- leer, wo sie es ist (Dateikopf).

#### Stuetze.masse

```python
@cached_property
def masse(self) -> Tuple[float, float]
```

Hoehe `h` in z und Breite `b` in y, ueber alles, in mm.

#### Stuetze.hb

```python
@property
def hb(self) -> float
```

#### Stuetze.beulen

```python
@cached_property
def beulen(self) -> Optional[Tuple[str, float, float, str]]
```

Tabelle 6: das Verhaeltnis, seine Zahl, seine Grenze und wie sie
steht -- `None` beim ganz einbetonierten Profil.

#### Stuetze.N_a

```python
@cached_property
def N_a(self) -> float
```

`A_a f_y/γ_a` in N.

#### Stuetze.N_pl

```python
def N_pl(self, charakteristisch: bool=False) -> float
```

`N_pl,Rd` (14) in N -- oder `N_pl,Rk` mit γ = 1 (16).

#### Stuetze.delta

```python
@property
def delta(self) -> float
```

(13).

#### Stuetze.fehlt

```python
@cached_property
def fehlt(self) -> str
```

Warum die Stuetze nicht nach 5.3 rechnet, der erste Grund -- leer,
wo sie es tut: die Symmetrie, `h/b`, Tabelle 6, `δ`.

#### Stuetze.stark

```python
@cached_property
def stark(self) -> Optional[str]
```

Die starke Achse des Profils -- `None` beim runden und beim quadratischen Rohr.

#### Stuetze.kurve

```python
def kurve(self, achse: str) -> Tuple[str, float, str]
```

Tabelle 7 um `achse`: die Kurve, der Nenner von `e_0 = L/Nenner` und warum.

#### Stuetze.EI

```python
def EI(self, achse: str, E_c: Mapping[int, float], beton: float) -> float
```

`Σ E I` um `achse` in N mm², der Beton mit `beton · E_c`, `E_c` je Gruppe.

#### Stuetze.E_c_eff

```python
def E_c_eff(self, staendig: float, kriechzahl: float) -> Dict[int, float]
```

(19) je Beton, in N/mm² -- `staendig` ist `N_G,Ed/N_Ed`.

#### Stuetze.starr

```python
@cached_property
def starr(self) -> Starrplastisch
```

Der Querschnitt in rechteckigen Spannungsbloecken -- der Betonstahl mit seinem Anteil.

#### Stuetze.M_pl

```python
def M_pl(self, achse: str, M: float, N: float) -> Tuple[float, Optional[float]]
```

Der plastische Biegewiderstand um `achse` bei `N` in N, zur
Seite, die `M` zieht: sein Betrag in N mm und wie weit die
Nulllinie von der Mitte zur gezogenen Seite liegt, in mm --
`(0, None)`, wo der Querschnitt `N` nicht traegt.

### Knicken

```python
@dataclass(frozen=True)
class Knicken
```

Die Achse ohne Moment, nach (15): in N und mm -- gehalten mit
`L_K = 0`, `N_cr` unendlich und `χ_K = 1`.

- `achse: str`
- `L_K: float`
- `EI: float`
- `N_cr: float`
- `lam: float`
- `kurve: str`
- `grund: str`
- `phi: float`
- `chi: float`
- `N_K_Rd: float`

#### Knicken.gehalten

```python
@property
def gehalten(self) -> bool
```

### Biegeachse

```python
@dataclass(frozen=True)
class Biegeachse
```

Die Achse mit Moment, nach (25): in N und mm. Gehalten, mit `L_K = 0`,
waechst das Moment nicht: `k = 1`, ohne Imperfektion.

- `achse: str`
- `gehalten: bool`
- `M: float` – `|M_Ed|` 1. Ordnung.
- `psi: float`
- `omega: float`
- `EI_d: float`
- `N_cr_eff: float` – `math.inf`, wo die Achse gehalten oder die Stuetze null lang ist.
- `k: float`
- `k_0: float`
- `nenner: float`
- `e_0: float`
- `M_II: float` – `math.inf`, wo `|N_Ed|` `N_cr,eff` erreicht: die Stuetze knickt aus.
- `M_pl: float`
- `M_pl_N: float`
- `lage: Tuple[Optional[float], Optional[float]]` – Wie weit die Nulllinie ohne und mit `N_Ed` von der Mitte zur gezogenen Seite liegt.
- `mu: float` – `μ_d`, hoechstens eins.

#### Biegeachse.knickt_aus

```python
@property
def knickt_aus(self) -> bool
```

#### Biegeachse.nutzung

```python
@property
def nutzung(self) -> float
```

`M_Ed,II/(μ_d M_pl,Rd)`.

### Ergebnis

```python
@dataclass(frozen=True)
class Ergebnis
```

Ein Fall der Stuetze -- in N und mm.

- `fall: st.Stabfall`
- `E_c: Dict[int, float]` – (19) je Beton.
- `knicken: Dict[str, Knicken]`
- `biegung: Dict[str, Biegeachse]`
- `alpha_M: float`
- `fehlt: str = ''`

#### Ergebnis.N

```python
@property
def N(self) -> float
```

#### Ergebnis.summe

```python
@property
def summe(self) -> float
```

Zweiachsig: `Σ M_Ed,II/(μ_d M_pl,Rd)` -- 5.3.5, siehe Dateikopf.

#### Ergebnis.grade

```python
@property
def grade(self) -> List[Tuple[str, float]]
```

Je Nachweis, was er sagt, und sein Erfuellungsgrad.

#### Ergebnis.massgebend

```python
@property
def massgebend(self) -> Tuple[str, float]
```

### rechnen

```python
def rechnen(stuetze: Stuetze, fall: st.Stabfall, kriechzahl: float, momente: Mapping[str, float]) -> Ergebnis
```

Ein Fall mit Druck -- `momente` je Achse in N mm, wie sie zaehlen
(einachsig ohne `M_z`), `kriechzahl` `φ(t,t_0)`.

### _zu_lang

```python
def _zu_lang(fall: st.Stabfall, achse: str) -> str
```

Warum die Knicklaenge um `achse` nicht zur Stuetze passt -- leer, wo sie passt.

### momente

```python
def momente(biegung_wirkt: Sequence[float]) -> Dict[str, float]
```

Die Momente eines Falls je Achse in N mm -- aus `Biegung.wirkt` in Nm.


## Konstanten

- `REFERENZ_ART = 'SIA 264:2014, 5.3.1.1; 5.3.2.1; Tabelle 7'`
- `REFERENZ_HB = 'SIA 264:2014, 5.3.2.3'`
- `REFERENZ_BEULEN = 'SIA 264:2014, 5.3.1.7, Tabelle 6'`
- `REFERENZ_BEWEHRUNG = 'SIA 264:2014, 5.3.2.2'`
- `REFERENZ_N_PL_ROHR = 'SIA 264:2014, 5.3.2.4, (14); 5.3.2.5'` – (14) im gefuellten Rohr -- ohne Rohr gilt `qa_verbund_kennzahlen.REFERENZ_14`.
- `REFERENZ_N_PL_K = 'SIA 264:2014, 5.3.2.7, (16)'`
- `REFERENZ_DELTA = 'SIA 264:2014, 5.3.1.2, (13)'`
- `REFERENZ_KURVE = 'SIA 264:2014, 5.3.2.6, Tabelle 7'`
- `REFERENZ_15 = 'SIA 264:2014, 5.3.2.6, (15); SIA 263:2013, 4.5.1.4, (8)'`
- `REFERENZ_LAMBDA = 'SIA 264:2014, 5.3.2.7, (16); 5.3.2.1'`
- `REFERENZ_EI = 'SIA 264:2014, 5.3.2.8, (17)'`
- `REFERENZ_E_C = 'SIA 264:2014, 5.3.2.9, (19)'`
- `REFERENZ_N_CR = 'SIA 264:2014, 5.3.2.10, (20)'`
- `REFERENZ_EI_D = 'SIA 264:2014, 5.3.3.2, (22)'`
- `REFERENZ_N_CR_EFF = 'SIA 264:2014, 5.3.3.3, (23); 5.3.4.1'`
- `REFERENZ_K = 'SIA 264:2014, 5.3.4.1, (24); SIA 263:2013, 5.1.9.1'`
- `REFERENZ_E_0 = 'SIA 264:2014, 5.3.1.4; Tabelle 7'`
- `REFERENZ_MU = 'SIA 264:2014, 5.3.4.3; 5.3.4.4; 5.3.4.6; Figur 7'`
- `REFERENZ_25 = 'SIA 264:2014, 5.3.4.6, (25)'`
- `REFERENZ_ZWEIACHSIG = 'SIA 264:2014, 5.3.5'`
- `LAMBDA_BIS = 2.0` – 5.3.2.1 und (16): die groesste bezogene Schlankheit.
- `BEWEHRUNG_BIS = 0.06` – 5.3.2.2: der Betonstahl zaehlt hoechstens mit diesem Anteil der Betonflaeche.
- `ROHR_FAKTOR = 1.0` – 5.3.2.5 und 5.3.4.4: der Umrechnungsfaktor der Betondruckfestigkeit im gefuellten Rohr.
- `BETON_LAMBDA = 0.6` – (17): wie der Beton in `(EI)_eff,λ` zaehlt; (22): wie in `(EI)_eff,d`, und der Beiwert davor.
- `ROHR_RHO = 0.03` – Tabelle 7: bis zu welchem `ρ_s` ein gefuelltes Rohr mit Kurve a rechnet.
- `SYMMETRIE_VERSATZ = 1.0` – Wie weit ein Schwerpunkt neben der Mitte liegen und welchen Teil von `√(I_y I_z)` `|I_yz|` erreichen darf, damit eine Gruppe als doppelsymmetrisch gilt -- siehe Dateikopf.
- `SYMMETRIE_I_YZ = 0.01`
- `AUSSEN_AB = 1.0` – Ab wie viel mm² Beton oder Betonstahl ausserhalb des Profils liegen.
- `NICHT_IN_TABELLE = 'Tabelle 7 kennt diesen Querschnitt nicht. Als Verbundstütze rechnet …` – Warum ein Querschnitt nicht als Verbundstuetze rechnet.
- `LEERES_ROHR = 'Das Rohr «{name}» ist innen leer. Als Verbundstütze rechnet ein gefü…` – Warum ein Rohr nicht als gefuellt rechnet: in seiner Mitte liegt kein Beton.

## Braucht

- [[opencivil.material.basis]]
- [[opencivil.querschnitt.geometrie]]
- [[opencivil.querschnitt.plastisch]]
- [[opencivil.stahlbau.querschnitt]]
- [[opencivil.stahlbau.stabilitaet]]
- [[opencivil.stahlprofile.formen]]
- [[opencivil.stahlprofile.tabelle]]
- [[opencivil.verbund.querschnitt]]

## Gebraucht von

- [[opencivil.nachweis.qa_verbund_stuetze]]
