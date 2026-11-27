---
erzeugt: 15926225845c
art: modul
tags: [modul]
---
> [!abstract] opencivil/stahlbau/stabilitaet.py
> Knicken und Kippen eines Stabs aus Baustahl.
> Paket [[opencivil.stahlbau]] · [Quelltext](../../opencivil/stahlbau/stabilitaet.py)

## VERANTWORTUNG

Was die Stabilitaet eines Stahlstabs nach SIA 263:2013 braucht, ohne
Rechenwerk und ohne Herleitung, in N, mm und N/mm² ([[opencivil.stahlbau.stabilitaet#rechnen|rechnen]]). Die
Herleitung schreibt [[opencivil.nachweis.qa_stahl_stabilitaet]]. Der Stab
hat den gezeichneten Querschnitt; ein Fall gibt ihm die Druckkraft, die
groessten Momente 1. Ordnung, die Verhaeltnisse ψ seiner Endmomente und die
Knick- und Kipplaengen ([[opencivil.stahlbau.stabilitaet#Stabfall|Stabfall]]).


## DIE WIDERSTAENDE NACH DER KLASSE

Die Klasse im Fall wie in der Tragsicherheit
([[opencivil.stahlbau.widerstand#rechnen|rechnen]]), bei `N_Ed` und den
Momenten 1. Ordnung. Dann je Achse plastisch in den Klassen 1 und 2,
elastisch in Klasse 3 (5.2.9) und am wirksamen Querschnitt in Klasse 4 --
je einmal mit der Festigkeit, mit der gerechnet wird, und einmal mit
`f_y` fuer die Schlankheiten.


## KNICKEN (4.5.1, 5.3.8)

Je Achse `N_cr = π² E I/L_K²`, `λ̄_K = √(f_y A/N_cr)` -- mit einem
Baustahl genau `√(f_y/σ_cr,K)` -- und `χ_K` nach (8) mit der Kurve aus
Figur 7 ([[opencivil.stahlbau.stabilitaet#kurve|kurve]]): `N_K,Rd = χ_K f_y A/γ_M1` (7). In Klasse 4 mit
`A_eff` statt `A`, `N_cr` am ganzen Querschnitt (5.3.8). Eine
Knicklaenge null heisst: gehalten, `N_cr` unendlich.


## KIPPEN (4.5.2, ANHANG B)

Um die starke Achse, wo ein Moment um sie wirkt und eine Kipplaenge
`L_D` da ist: `σ_cr,D = √(σ_Dv² + σ_Dw²)` nach (91) bis (93), mit `η`
nach (94) und dem Druckgurt nach Figur 40 ([[opencivil.stahlbau.stabilitaet#druckgurt|druckgurt]]);
`M_cr = W_el σ_cr,D` (90), `λ̄_D = √(W f_y/M_cr)` und `χ_D` nach (10)
mit `α_D = 0.21` der Walzprofile; `M_D,Rd = χ_D W f_y/γ_M1` (9), `W`
nach der Klasse. In Klasse 4 ohne den Anteil nach Saint-Venant (B.4). Wo
gekippt wird, gilt (9) immer auch allein.


## DAS ZUSAMMENWIRKEN

* Klassen 1 bis 3: (50), in Klasse 3 mit elastischen Widerstaenden (5.2.9).
* Klassen 1 und 2, I-Walzprofil, Knicken aus der Ebene und Kippen nicht
  verhindert: auch (51) (5.1.10.2, 5.1.10.4).
* Klasse 4: (62) und (63), mit den Ersatzimperfektionen der Spalte EE von
  Figur 3 -- ohne Moment und ohne Versatz des wirksamen Schwerpunkts nur
  5.3.8.


## DER ERFUELLUNGSGRAD

wie in der Tragsicherheit
([[opencivil.stahlbau.widerstand]]): die Normalkraft bleibt, die Momente
wachsen in ihrer Richtung, bis die Gleichung aufgeht. (50) ist in den
Momenten linear, `α = (1 - N_Ed/N_K,Rd)/Σ m`; (51) mit der Potenz β,
`α = (a^β + b^β)^(-1/β)`. Ohne Moment `N_K,Rd/|N_Ed|`. Wo schon die
Normalkraft allein nicht traegt, misst `α` sie ([[opencivil.stahlbau.stabilitaet#Ergebnis|Ergebnis.alpha_N]]).
Wo zwei Gleichungen gelten duerfen -- (50) und (51) --, zaehlt die
guenstigere; wo beide gelten muessen -- (62) und (63), oder das
Zusammenwirken und (9) --, die unguenstigere.


## WAS DAS WERKZEUG NICHT KANN

der Fall sagt es grau ([[opencivil.stahlbau.stabilitaet#Ergebnis|Ergebnis.fehlt]])
* Kurve und Druckgurt kennt es nur fuer einen Querschnitt aus einem einzigen
  Profil. Fuer jeden anderen waehlt der Benutzer die Kurve je Achse; kippen
  laesst es ihn nicht.
* Anhang B gilt fuer doppelsymmetrische Querschnitte (B.3): das I und das
  Rechteckrohr. Ein U mit Kipplaenge und Moment um die starke Achse ist
  nicht fuehrbar.
* Biegedrillknicken (4.5.1.2), die Vergroesserung ξ (5.1.9.2) und die
  kritischen Kipplaengen der Tabelle 6 rechnet es nicht.


## NACH VORGABE, NICHT NACHGESCHLAGEN

* Das Rundrohr gilt als warmgefertigt, Kurve a -- wie in den Excel-Dateien
  des Benutzers. Fuer ein kaltgefertigtes waehlt er c.
* Unter ψ = -0.5 bleibt η bei 2.35, dem Wert bei -0.5: (94) gilt erst ab
  dort, und darunter waere η groesser.
* Der Druckgurt ohne Ausrundungen, die gedrueckte Steghoehe die Haelfte der
  Hoehe zwischen den Flanschen -- unter Biegung allein; beim Rechteckrohr
  mit beiden Stegen: Figur 40 zeigt nur das I.
* Rohre kippen mit dem `α_D` der Walzprofile.
* Mit mehreren Baustaehlen `λ̄_K = √(Σ f_y A/N_cr)`.
* `w_0` nach Figur 3 mit der Knicklaenge als Stablaenge.
* In Klasse 4 mindert `χ_D` in (62) und (63) den Widerstand um die starke
  Achse: (67) nennt das Kippen nur fuer die Biegung allein.
* ψ gilt fuer `ω` und fuer `η` -- dieselben Endmomente.


## AUF DER SICHEREN SEITE

In Klasse 4 zaehlt der ganze Druckgurt, obwohl B.5 und 5.6.2.3 nur die
mitwirkenden Teile zulassen. Ohne die uebrigen waere sein
Traegheitsradius groesser: im Flansch eines I-Walzprofils wirkt alles mit,
und was fehlte -- ein Stegstreifen, die Mitte des Flanschs eines
Rechteckrohrs --, liegt nahe seiner Achse.

## Inhalt

### Knickkurve

```python
class Knickkurve(Wahl)
```

Die Knickspannungskurve einer Achse: die des Profils nach Figur 7 oder eine gewaehlte.

- `PROFIL = 'profil'`
- `A = 'a'`
- `B = 'b'`
- `C = 'c'`
- `D = 'd'`

#### Knickkurve.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Knickkurve.erklaerung

```python
@property
def erklaerung(self) -> str
```

### abminderung

```python
def abminderung(lam: float, alpha: float, lam_0: float) -> Tuple[float, float]
```

`Φ` und `χ` nach (8) mit `λ̄_0 = 0.2` oder (10) mit 0.4 -- `χ` hoechstens eins.

### eta

```python
def eta(psi: float) -> float
```

`η` nach (94); unter ψ = -0.5 der Wert dort (Dateikopf).

### omega

```python
def omega(psi: float) -> float
```

`ω` nach 5.1.9.1, mindestens 0.4.

### kurve

```python
def kurve(profil: tabelle.Profil, stark: bool) -> Tuple[str, str]
```

Die Kurve eines Profils nach Figur 7 fuer das Knicken um seine starke oder
schwache Achse -- und in Worten, warum.

### Druckgurt

```python
@dataclass(frozen=True)
class Druckgurt
```

Der Druckgurt nach Figur 40, in mm: der Flansch `b × t_f` und je Steg
ein Drittel seiner gedrueckten Hoehe `h_c` -- beim Rechteckrohr zwei
Stege im Abstand `e` von der Mitte.

- `b: float`
- `t_f: float`
- `t_w: float`
- `h_c: float`
- `stege: int`
- `e: float`

#### Druckgurt.A

```python
@property
def A(self) -> float
```

#### Druckgurt.I

```python
@property
def I(self) -> float
```

Um die Achse in der Mitte des Flanschs, quer zu ihm.

#### Druckgurt.i

```python
@property
def i(self) -> float
```

### druckgurt

```python
def druckgurt(profil: tabelle.Profil) -> Optional[Druckgurt]
```

Der Druckgurt eines doppelsymmetrischen Profils mit starker Achse: beim
I und beim Rechteckrohr -- sonst `None`. Die gedrueckte Steghoehe ist
bei reiner Biegung die Haelfte der Hoehe zwischen den Flanschen.

### einzelprofil

```python
def einzelprofil(teile: Iterable[Tuple[str, Optional[Profillage]]]) -> Optional[tabelle.Profil]
```

Das Profil, wenn der Querschnitt nur aus ihm besteht -- mit seinen
Loechern, die seine Kennung tragen, ohne jede andere Flaeche; sonst
`None`. `teile` je Flaeche ihre Kennung und, beim Umriss eines
Profils, seine Lage: aus der Analyse wie aus der Zeichnung
([[opencivil.web.zeichengeometrie]]) -- eine Regel fuer beide.

### starke_achse

```python
def starke_achse(I: Mapping[str, float]) -> Optional[str]
```

Die Achse mit dem groesseren Traegheitsmoment -- `None`, wo beide gleich sind.

### kurven_des_profils

```python
def kurven_des_profils(profil: tabelle.Profil, I: Mapping[str, float]) -> Dict[str, Tuple[str, str]]
```

Je Achse die Kurve, die Figur 7 dem Profil zuweist, und warum -- `I` je Achse.

### rechenkurven

```python
def rechenkurven(wahl: Mapping[str, Knickkurve], profil: Optional[tabelle.Profil], I: Mapping[str, float]) -> Dict[str, Optional[Tuple[str, str]]]
```

Je Achse die Kurve, mit der gerechnet wird, und warum: die gewaehlte, sonst
die des einzigen Profils ([[opencivil.stahlbau.stabilitaet#einzelprofil|einzelprofil]]) -- `None`, wo es keines
gibt.

### fehlende_kurven

```python
def fehlende_kurven(kurven: Mapping[str, Optional[Tuple[str, str]]], faelle: Iterable[Stabfall]) -> str
```

Welche Kurve den `faelle` fehlt, als Satz: um eine Achse, um die einer
von ihnen knickt, ohne Kurve ([[opencivil.stahlbau.stabilitaet#rechenkurven|rechenkurven]]) -- leer, wo keine
fehlt. Eine Regel fuer den Fall und die Kachel davor
([[opencivil.web.zeichengeometrie]]).

### seite_von

```python
def seite_von(achse: str, M: float) -> Zugseite
```

Die Seite, die ein Moment um `achse` zieht: `M_y ≥ 0` unten, `M_z ≥ 0` links.

### quer

```python
def quer(achse: str) -> str
```

### Stab

```python
@dataclass(frozen=True)
class Stab
```

Was jeder Fall vom Querschnitt braucht -- in mm, mm⁴ und N/mm².

- `stahl: Stahlquerschnitt`
- `f: Sequence[float]` – Je Gruppe die Fliessgrenze, mit der gerechnet wird -- `f_y/γ_M1` oder `f_y`.
- `f_k: Sequence[float]` – Je Gruppe `f_y` -- fuer die Schlankheiten.
- `eps: Sequence[float]`
- `E: float`
- `G: float`
- `I: Dict[str, float]`
- `I_T: float`
- `bezug: Punkt` – Der Schwerpunkt -- um ihn wirken die Momente.
- `biegung: Biegung`
- `kurven: Dict[str, Knickkurve]`
- `profil: Optional[tabelle.Profil]` – Das einzige Profil des Querschnitts -- `None`, wo er mehr hat ([[opencivil.stahlbau.stabilitaet#einzelprofil|einzelprofil]]).

#### Stab.stark

```python
@property
def stark(self) -> Optional[str]
```

#### Stab.A

```python
@property
def A(self) -> float
```

#### Stab.i

```python
def i(self, achse: str) -> float
```

#### Stab.kurve

```python
def kurve(self, achse: str) -> Optional[Tuple[str, str]]
```

Die Kurve um `achse` und warum -- `None`, wo sie fehlt ([[opencivil.stahlbau.stabilitaet#rechenkurven|rechenkurven]]).

### Stabfall

```python
@dataclass(frozen=True)
class Stabfall
```

Ein Fall des Stabs, in SI wie ein Lastfall der Analyse: `N` in N,
negativ Druck, die Momente in Nm um den Schwerpunkt, die Laengen in m --
eine Laenge null heisst gehalten. Nur im Verbund zaehlen `staendig`
und `L` ([[opencivil.verbund.stuetze]]).

- `name: str`
- `N: float = 0.0`
- `M_y: float = 0.0`
- `M_z: float = 0.0`
- `psi_y: float = 1.0`
- `psi_z: float = 1.0`
- `L_K_y: float = 0.0`
- `L_K_z: float = 0.0`
- `L_D: float = 0.0`
- `staendig: float = 1.0` – Der staendige Anteil der Normalkraft, `N_G,Ed/N_Ed`: er kriecht.
- `L: float = 0.0` – Die Laenge der Stuetze, fuer `k` (24) und die Ersatzimperfektion.

#### Stabfall.kennung

```python
@property
def kennung(self) -> str
```

#### Stabfall.psi

```python
def psi(self, achse: str) -> float
```

#### Stabfall.knicklaenge

```python
def knicklaenge(self, achse: str) -> float
```

In mm.

### Knicken

```python
@dataclass(frozen=True)
class Knicken
```

Das Knicken um eine Achse, in N und mm -- ohne Kurve, wo der Stab gehalten ist.

- `achse: str`
- `L_K: float`
- `N_cr: float` – `math.inf`, wo der Stab gehalten ist.
- `lam: float`
- `kurve: str`
- `grund: str`
- `phi: float`
- `chi: float`
- `N_K_Rd: float`
- `schlankheit: float` – `λ_K = L_K/i` nach 4.5.1.7.

#### Knicken.gehalten

```python
@property
def gehalten(self) -> bool
```

#### Knicken.rest

```python
def rest(self, N: float) -> float
```

`1 - |N|/N_cr`.

### Kippen

```python
@dataclass(frozen=True)
class Kippen
```

Das Kippen um die starke Achse, in N, mm und N/mm².

- `achse: str`
- `seite: Zugseite`
- `eta: float`
- `gurt: Druckgurt`
- `L_K: float` – `L_D/√η`, die Knicklaenge des Druckgurts.
- `sigma_Dv: float`
- `sigma_Dw: float`
- `sigma_cr: float`
- `W_el: float`
- `M_cr: float`
- `M_Rk: float`
- `lam: float`
- `phi: float`
- `chi: float`
- `M_D_Rd: float`

### Glied50

```python
@dataclass(frozen=True)
class Glied50
```

Ein Moment in (50): `ω/(1 - N/N_cr) · |M_Ed|/M_Rd`.

- `achse: str`
- `omega: float`
- `rest: float` – `1 - |N_Ed|/N_cr`.
- `M_Ed: float`
- `M_Rd: float`
- `kippen: bool` – Ob `M_Rd` hier `M_D,Rd` ist.

#### Glied50.m

```python
@property
def m(self) -> float
```

### Gleichung51

```python
@dataclass(frozen=True)
class Gleichung51
```

(51) mit ihren Teilen, in N und N·mm -- `s` die starke Achse, `w` die schwache.

- `s: str`
- `w: str`
- `beta: float`
- `b: float`
- `h: float`
- `t_f: float`
- `M_D_Rd_min: float` – Mit `η = 1` bei zweiachsiger Biegung, sonst wie `M_D,Rd`.
- `M_s_red: float`
- `M_w_red: float`
- `begrenzt: bool` – Ob `ω_s M_D,Rd` `M_s,red,Rd` begrenzt.
- `a: float` – `ω_s |M_s,Ed|/M_s,red,Rd`.
- `c: float` – `ω_w |M_w,Ed|/M_w,red,Rd`.

#### Gleichung51.alpha

```python
@property
def alpha(self) -> float
```

### Gleichung62

```python
@dataclass(frozen=True)
class Gleichung62
```

(62) oder (63): `n = |N_Ed|/(f_y A_eff)` und die Glieder des wirksamen
Querschnitts, das der Achse `verstaerkt` mit `1/(1 - N/N_cr)` --
leer, wo schon `N_cr` erreicht ist.

- `verstaerkt: str`
- `n: float`
- `glieder: List[wd.Glied]`
- `alpha: Optional[float]` – Der Faktor auf die Momente -- ohne Moment auf die Normalkraft; `None`, wo schon die Normalkraft nicht traegt: dann [[opencivil.stahlbau.stabilitaet#Gleichung62|alpha_N]].
- `alpha_N: Optional[float]`

### Ergebnis

```python
@dataclass
class Ergebnis
```

Was ein Fall am Stab ergibt -- siehe Dateikopf. Kraefte in N, Momente in N·mm.

- `fall: Stabfall`
- `N: float`
- `M: Dict[str, float]`
- `x: wd.Fall` – Der Fall am Querschnitt: seine Klasse und die Bleche.
- `fehlt: str = ''` – Warum der Fall nicht fuehrbar ist -- leer, wo er es ist.
- `rd: Optional[wd.Widerstaende] = None`
- `rk: Optional[wd.Widerstaende] = None` – Dieselben Widerstaende mit `f_y` -- fuer die Schlankheiten.
- `wirksam: Optional[wd.Wirksame] = None` – In Klasse 4 der wirksame Querschnitt, mit dem gerechnet wird.
- `knicken: Dict[str, Knicken] = field(default_factory=dict)`
- `kippen: Optional[Kippen] = None`
- `kippen_min: Optional[Kippen] = None` – Mit `η = 1` -- fuer (51) bei zweiachsiger Biegung, wo `η` nicht schon eins ist.
- `glieder: List[Glied50] = field(default_factory=list)`
- `alpha_50: Optional[float] = None`
- `g51: Optional[Gleichung51] = None`
- `alpha_9: Optional[float] = None`
- `g62: List[Gleichung62] = field(default_factory=list)`
- `w_0: Dict[str, float] = field(default_factory=dict)`
- `alpha: float = math.inf`
- `alpha_N: Optional[float] = None` – Wo schon die Normalkraft allein nicht traegt: um welchen Faktor sie kleiner sein muesste.

#### Ergebnis.klasse

```python
@property
def klasse(self) -> int
```

#### Ergebnis.mit_moment

```python
@property
def mit_moment(self) -> bool
```

#### Ergebnis.N_K_Rd

```python
@property
def N_K_Rd(self) -> float
```

#### Ergebnis.n

```python
@property
def n(self) -> float
```

`|N_Ed|/N_K,Rd`.

#### Ergebnis.versatz

```python
@property
def versatz(self) -> Tuple[float, float]
```

Wie weit der wirksame Schwerpunkt bei Druck neben dem ganzen liegt, in mm.

#### Ergebnis.mit_versatz

```python
@property
def mit_versatz(self) -> bool
```

### rechnen

```python
def rechnen(stab: Stab, fall: Stabfall) -> Ergebnis
```

Ein Fall am Stab -- siehe Dateikopf.

### _widerstaende

```python
def _widerstaende(stab: Stab, e: Ergebnis) -> None
```

Die Widerstaende nach der Klasse des Falls: mit der Festigkeit der Rechnung, mit `f_y`.

### _M_Rd

```python
def _M_Rd(e: Ergebnis, achse: str, kippen: Optional[Kippen]) -> float
```

Der Biegewiderstand um `achse` zur Seite des Moments -- um die starke mit dem Kippen.

### _gleichung_50

```python
def _gleichung_50(e: Ergebnis) -> None
```

(50): `N_Ed/N_K,Rd + Σ ω/(1 - N_Ed/N_cr) · M_Ed/M_Rd ≤ 1`.

### _mit_51

```python
def _mit_51(stab: Stab, e: Ergebnis) -> bool
```

Ob (51) gelten darf: Klasse 1 oder 2, ein I-Walzprofil, ein Moment, und
weder das Knicken aus der Ebene noch das Kippen verhindert.

### _gleichung_51

```python
def _gleichung_51(stab: Stab, e: Ergebnis) -> None
```

(51) mit den Achsen des Profils -- die starke heisst dort y.

### _gleichungen_62

```python
def _gleichungen_62(e: Ergebnis) -> None
```

(62) und (63) am wirksamen Querschnitt, je mit einem verstaerkten Glied.

### _faktor

```python
def _faktor(nutzung: Callable[[float], float]) -> float
```

Das `μ` mit `nutzung(μ) = 1` -- die linke Seite waechst mit `μ` und
ist bei null kleiner als eins. Durch Halbieren, bis auf 1e-12 genau.


## Konstanten

- `REFERENZ_KNICKEN = 'SIA 263:2013, 4.5.1.3, (7); 4.5.1.4, (8); Tabelle 8'`
- `REFERENZ_KURVE = 'SIA 263:2013, 4.5.1.5; 4.5.1.6; Figur 7'`
- `REFERENZ_KLASSE_4 = 'SIA 263:2013, 4.5.1.3; 5.3.8'`
- `REFERENZ_SCHLANKHEIT = 'SIA 263:2013, 4.5.1.7'`
- `REFERENZ_KIPPEN = 'SIA 263:2013, 4.5.2.2, (9); 4.5.2.3, (10)'`
- `REFERENZ_DRUCKGURT = 'SIA 263:2013, Anhang B.5, (93); Figur 40'`
- `REFERENZ_ETA = 'SIA 263:2013, Anhang B.6, (94); Figur 41'`
- `REFERENZ_OMEGA = 'SIA 263:2013, 5.1.9.1; 5.1.10.3'`
- `REFERENZ_50 = 'SIA 263:2013, 5.1.10.1, (50); 5.2.9'`
- `REFERENZ_51 = 'SIA 263:2013, 5.1.10.2, (51); 5.1.10.4'`
- `REFERENZ_62 = 'SIA 263:2013, 5.3.9, (62), (63); 4.2.3.2, Figur 3'`
- `ALPHA_K = {'a': 0.21, 'b': 0.34, 'c': 0.49, 'd': 0.76}` – Tabelle 8: der Imperfektionsbeiwert je Kurve.
- `LAMBDA_0_KNICKEN = 0.2` – Bis wohin nichts gemindert wird: λ̄_0 in (8) und in (10).
- `LAMBDA_0_KIPPEN = 0.4`
- `ALPHA_D_GEWALZT = 0.21` – 4.5.2.3: α_D der Walzprofile -- geschweisste haben 0.49, die kippen hier nicht.
- `SCHLANKHEIT = 200.0` – 4.5.1.7: die Schlankheit, die ein Haupttragelement in der Regel nicht ueberschreitet.
- `W0_NENNER = {'a': 300.0, 'b': 250.0, 'c': 200.0, 'd': 150.0}` – Figur 3, Spalte EE: `w_0 = L/Nenner` je Kurve.
- `OMEGA_MIN = 0.4` – 5.1.9.1: das kleinste ω.
- `PSI_ETA_MIN = -0.5` – Ab wo (94) gilt -- darunter bleibt η beim Wert dort (Dateikopf).
- `STARK = 1.0 + 1e-06` – Um so viel muss ein Traegheitsmoment groesser sein, damit seine Achse die starke ist.
- `VERSATZ = 1e-06` – Ab welchem Versatz in mm der wirksame Schwerpunkt neben dem ganzen liegt.
- `_KURVE_DER_REIHE = {'ROR': ('a', 'warmgefertigtes Hohlprofil'), 'RRW': ('a', 'warmgefert…` – Figur 7 ohne die I-Walzprofile: je Reihe die Kurve um beide Achsen und warum -- nach der Reihe, nicht nach der Form: RRK und RRW haben dieselbe Form, das eine kalt-, das andere warmgefertigt.
- `KURVE_FEHLT = '{was}: Figur 7 kennt das Werkzeug nur für einen Querschnitt aus eine…` – Was fehlt -- Saetze fuer die Herleitung und die Zusammenfassung.
- `KIPPEN_FEHLT = 'Kippen rechnet das Werkzeug nur für einen Querschnitt aus einem einz…`

## Braucht

- [[opencivil.core.wahl]]
- [[opencivil.core.wert]]
- [[opencivil.querschnitt.biegung]]
- [[opencivil.querschnitt.geometrie]]
- [[opencivil.querschnitt.zugseite]]
- [[opencivil.stahlbau.querschnitt]]
- [[opencivil.stahlbau.widerstand]]
- [[opencivil.stahlprofile.formen]]
- [[opencivil.stahlprofile.lage]]
- [[opencivil.stahlprofile.tabelle]]

## Gebraucht von

- [[opencivil.nachweis.qa_holz_stabilitaet]]
- [[opencivil.nachweis.qa_stahl_stabilitaet]]
- [[opencivil.nachweis.qa_verbund_stuetze]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.projekt.stabilitaet]]
- [[opencivil.verbund.stuetze]]
- [[opencivil.web.api]]
- [[opencivil.web.zeichengeometrie]]
