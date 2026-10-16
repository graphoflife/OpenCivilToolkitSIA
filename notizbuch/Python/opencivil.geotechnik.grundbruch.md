---
erzeugt: 1d7a7bd4b74c
art: modul
tags: [modul]
---
> [!abstract] opencivil/geotechnik/grundbruch.py
> Grundbruch und Gleiten eines Flachfundaments.
> Paket [[opencivil.geotechnik]] · [Quelltext](../../opencivil/geotechnik/grundbruch.py)

## VERANTWORTUNG

Das [[opencivil.geotechnik.grundbruch#Fundament|Fundament]] -- Boden, Abmessungen, Gelände und Grundwasser als
Vorgaben, dazu die Bemessungswerte der Scherfestigkeit -- und je
Einwirkungskombination zwei Nachweise:

* [[opencivil.geotechnik.grundbruch#Grundbruch|Grundbruch]] -- der Grundbruchwiderstand nach der erweiterten
  Tragfähigkeitsformel (Kap. 9.2.10):

```
    sigma_f = c N_c s_c d_c i_c g_c b_c
            + (gamma t + q) N_q s_q d_q i_q g_q b_q
            + 1/2 gamma b N_gamma s_gamma d_gamma i_gamma g_gamma b_gamma
    N_Rd    = sigma_f · b · L

und für phi = 0, undrainiert (Kap. 9.2.17)::

    sigma_f = 5.1 s_u (1 + s_c + d_c - i_c - b_c - g_c) + (gamma t + q)
```

* [[opencivil.geotechnik.grundbruch#Gleiten|Gleiten]] -- der Gleitwiderstand in der Sohle,
  T_Rd = N_Ed · tan delta* (Kap. 9.2.18).

Gerechnet wird mit Bemessungswerten: phi_eff = arctan(tan phi_k / gamma_phi)
(SIA 267:2013, 5.3.2.1) und c_eff = c_k / gamma_c. Ein globaler
Sicherheitsgrad wie F_stat des Kapitels kommt nicht dazu.


## QUELLE

Die Formeln stammen aus dem Kapitel 9.2 «Tragfähigkeit», das der Benutzer
geliefert hat; der Abschnitt steht an jeder Formel. Wo der Text und seine
Tabellen auseinandergehen, steht es beim Faktor: b_gamma rechnet nach
Tabelle 9.2.18 mit tan phi, im Text steht tan alpha.


## WINKEL (Bild 9.2.15)

alpha ist die Neigung der Sohle, positiv, wenn sie gegen T ansteigt -- das
Abgleiten wird schwerer; beta die Neigung des Geländes, positiv, wenn es vom
Fundament weg abfällt; delta_R die Neigung der Last gegen die Sohlnormale.
N steht normal zur Sohle, T in ihrer Richtung. Alle drei Winkel gehen in Grad
in die Faktoren ein, wie das Kapitel sie schreibt («0.007 arctan t/b»).


## GRUNDWASSER (Bild 9.2.10)

t_1 ist die Tiefe des höchsten Grundwasserspiegels unter Terrain. Liegt er
über der Sohle oder auf ihr (Lage 1, 2), zählt unter ihm gamma'; liegt er um
mindestens die Tiefe H des Gleitkörpers tiefer (Lage 3), zählt gamma.
Dazwischen verlangt das Kapitel eine Stabilitätsberechnung; gerechnet wird
dann mit gamma' wie in Lage 2, auf der sicheren Seite -- eine Annahme, nicht
aus dem Kapitel (notizbuch/Notizen/TODO.md). Undrainiert zählen totale
Spannungen, das Wasser spielt dort keine Rolle.


## EINHEITEN

Alles in SI-Basis; die Winkel als Groessen in Grad.

## Inhalt

### grad

```python
def grad(winkel: Groesse) -> float
```

Ein Winkel in Grad -- so gehen alpha, beta und arctan(t/b) in die Faktoren ein.

### Fundament

```python
@dataclass
class Fundament
```

Ein Flachfundament auf seinem Baugrund: die Eingaben als Vorgaben im
Rechenwerk, dazu phi_eff, c_eff und gamma'.

`b` ist die Breite, die kürzere Seite, `L` die Länge; ein
Streifenfundament ist ein sehr langes.

- `name: str`
- `phi_k: Groesse`
- `gamma_phi: Groesse`
- `c_k: Groesse`
- `gamma_c: Groesse`
- `gamma: Groesse`
- `gamma_w: Groesse`
- `q_Ed: Groesse`
- `b: Groesse`
- `L: Groesse`
- `t1: Groesse`
- `t: Groesse`
- `alpha: Groesse`
- `beta: Groesse`
- `delta_faktor: Groesse`
- `praefix: str`
- `definitionen: Dict[str, WertDef] = field(default_factory=dict, init=False)`
- `berechnungen: List[Berechnung] = field(default_factory=list, init=False)`

#### Fundament.abschnitt

```python
@property
def abschnitt(self) -> Abschnitt
```

Ueberschrift, unter der das Fundament in der Herleitung steht.

#### Fundament.id_von

```python
def id_von(self, kurzname: str) -> str
```

#### Fundament.ins_rechenwerk

```python
def ins_rechenwerk(self, werk) -> 'Fundament'
```

### Kombination

```python
@dataclass(frozen=True)
class Kombination
```

Eine Einwirkung auf das Fundament: N normal zur Sohle, T in ihrer Richtung.

- `name: str`
- `N_Ed: Groesse`
- `T_Ed: Groesse`

#### Kombination.kennung

```python
@property
def kennung(self) -> str
```

### Faktoren

```python
@dataclass
class Faktoren
```

Eine Spalte der Tragfähigkeitsformel: N, s, d, g und b' -- i hängt am Fall.

- `N: float`
- `s: float`
- `d: float`
- `g: float`
- `b: float`

### Fallergebnis

```python
@dataclass
class Fallergebnis
```

Was der Grundbruch bei einer Kombination ergibt.

- `kombination: Kombination`
- `delta_R: float` – Die Neigung der Last gegen die Sohlnormale, in rad.
- `i: Dict[str, Optional[float]] = field(default_factory=dict)` – Die Lastneigungsfaktoren je Spalte -- `None`, wo es keinen gibt.
- `sigma_f: float = 0.0`
- `N_Rd: float = 0.0`
- `erfuellungsgrad: float = 0.0`
- `erfuellt: bool = False`
- `begruendung: str = ''`
- `hinweis: str = ''`

### Grundbruchbefund

```python
@dataclass
class Grundbruchbefund
```

Was ausser den Erfüllungsgraden bleibt -- für die Zusammenfassung und das Bild.

- `undrainiert: bool`
- `spalten: Dict[str, Faktoren]` – Je Spalte der Formel (`c`, `q`, `g`) ihre Faktoren; undrainiert nur `c`.
- `L_gl: Optional[float] = None` – Wie weit der Gleitkörper neben das Fundament reicht, in m -- drainiert.
- `H_gl: Optional[float] = None` – Wie tief er unter die Sohle reicht, in m -- drainiert.
- `grundwasser: str = ''`
- `ergebnisse: List[Fallergebnis] = field(default_factory=list)`

### Grundbruch

```python
class Grundbruch(Nachweis)
```

Der Grundbruchwiderstand N_Rd je Kombination, gegen N_Ed gehalten. Die
Faktoren, die nicht an der Last hängen, werden einmal gerechnet; die
Lastneigung je Kombination.

- `THEMA = 'Grundbruch'`
- `ART = 'GB'`

#### Grundbruch.pruefe

```python
def pruefe(self, e: Eingaben, p: Protokoll) -> Ausfuehrung
```

#### Grundbruch._grundwasser

```python
def _grundwasser(self, e: Eingaben, p: Protokoll, werte: Zwischenwerte, H_gl: Wert) -> Tuple[Wert, Wert, str]
```

Überlagerung auf Höhe der Sohle und Raumlast im Gleitkörper, je nach Wasser.

#### Grundbruch._einbindewinkel

```python
@staticmethod
def _einbindewinkel(p: Protokoll, werte: Zwischenwerte, t: Wert, b: Wert) -> Wert
```

arctan(t/b) in Grad -- so steht er in den Tiefenfaktoren.

### gleitkoerper

```python
def gleitkoerper(b: float, phi: float, schritte: int=24) -> List[Tuple[float, float]]
```

Der Umriss des Gleitkörpers nach Prandtl, für Sohle und Gelände waagrecht
-- so, wie die Formeln für L_Gl und H_Gl ihn messen. In m, gemessen von
der Sohlkante auf der Seite, zu der T zeigt: x von dort weg vom
Fundament, z nach unten; das Fundament liegt bei -b \< x \< 0.

Der Zug läuft von der anderen Sohlkante über die Spitze des Keils unter
dem Fundament (Neigung 45° + φ/2), die logarithmische Spirale um die
Kante (r = r_0 · e^{ψ tan φ}, um 90° gedreht) und den Keil daneben
(45° - φ/2) bis ins Gelände bei x = L_Gl. Seine tiefste Stelle liegt
bei H_Gl. `phi` in rad, grösser als null.

### _hoch5

```python
def _hoch5(klammer: float) -> float
```

Eine Klammer hoch fünf -- unter null gilt null (siehe Herleitung).

### Gleiten

```python
class Gleiten(Nachweis)
```

Der Gleitwiderstand in der Sohle je Kombination: T_Rd = N_Ed · tan delta*,
ohne Erdwiderstand -- wie im Kapitel für eine geneigte Sohle.

- `THEMA = 'Gleiten'`
- `ART = 'GL'`

#### Gleiten.pruefe

```python
def pruefe(self, e: Eingaben, p: Protokoll) -> Ausfuehrung
```

### angaben

```python
def angaben(fundament: Fundament, werte: Dict[str, Wert]) -> GleichungBlock
```

Die Angaben über der Tabelle, aus den Werten der Lösung, wie sie
gerechnet wurden: in der ersten Zeile der Boden mit seinen
Bemessungswerten, in der zweiten die Masse und das Grundwasser. In einer
Zeile wären es acht Angaben -- breiter als die Spalte.

### faktortabelle

```python
def faktortabelle(befund: Grundbruchbefund) -> TabellenBlock
```

Die Faktoren der Tragfähigkeitsformel in drei Spalten -- Kohäsion,
seitliche Auflast, Gewicht des Gleitkörpers --, wie der Benutzer sie
tabelliert. Die Lastneigung je Kombination eine Zeile; undrainiert nur
die Spalte der Kohäsion.


## Konstanten

- `N_C_UNDRAINIERT = 5.1` – Der Beiwert der undrainierten Tragfähigkeitsformel, Kap. 9.2.17 -- 5.1, wie das Kapitel ihn schreibt (pi + 2 = 5.14 gerundet).
- `KAP_FAKTOREN = 'Kap. 9.2.6'` – Die Abschnitte des gelieferten Kapitels, an den Formeln als Referenz.
- `KAP_GRUNDWASSER = 'Kap. 9.2.8'`
- `KAP_FORMEL = 'Kap. 9.2.10'`
- `KAP_FORM = 'Kap. 9.2.12'`
- `KAP_TIEFE = 'Kap. 9.2.13'`
- `KAP_LAST = 'Kap. 9.2.14'`
- `KAP_GELAENDE = 'Kap. 9.2.15'`
- `KAP_SOHLE = 'Kap. 9.2.16'`
- `KAP_UNDRAINIERT = 'Kap. 9.2.17'`
- `KAP_GLEITEN = 'Kap. 9.2.18'`
- `SPALTEN = (('c', 'Kohäsion'), ('q', 'Seitliche Auflast'), ('g', 'Gewicht Gleitk…` – Die Spalten der Tragfähigkeitsformel, wie die Zusammenfassung sie zeigt.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]

## Gebraucht von

- [[opencivil.bericht.zusammenfassung]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.web.grundbruchdaten]]

## Formeln aus diesem Modul

- [[Abstand des Grundwassers unter der Sohle]] · `Grundbruch._grundwasser`
- [[Bemessungswert der Kohäsion]] · `_c_eff`
- [[Bemessungswert des Reibungswinkels]] · `_phi_eff`
- [[Bruchspannung in der Sohle]] · `Grundbruch._drainierter_fall`
- [[Bruchspannung in der Sohle]] · `Grundbruch._undrainierter_fall`
- [[Erweiterte Tragfähigkeitsformel]] · `Grundbruch._drainiert`
- [[Formfaktor s_c]] · `Grundbruch._drainiert`
- [[Formfaktor s_c]] · `Grundbruch._undrainiert`
- [[Formfaktor s_q]] · `Grundbruch._drainiert`
- [[Formfaktor s_γ]] · `Grundbruch._drainiert`
- [[Geländeneigungsfaktor g_c]] · `Grundbruch._drainiert`
- [[Geländeneigungsfaktor g_c]] · `Grundbruch._undrainiert`
- [[Geländeneigungsfaktor g_q]] · `Grundbruch._drainiert`
- [[Gleitwiderstand]] · `Gleiten.pruefe`
- [[Grundbruchwiderstand]] · `Grundbruch._widerstand`
- [[Lastneigungsfaktor i_c]] · `Grundbruch._drainierter_fall`
- [[Lastneigungsfaktor i_c]] · `Grundbruch._undrainierter_fall`
- [[Lastneigungsfaktor i_q]] · `Grundbruch._drainierter_fall`
- [[Lastneigungsfaktor i_γ]] · `Grundbruch._drainierter_fall`
- [[Neigung der Last]] · `Grundbruch._drainierter_fall`
- [[Raumlast im Gleitkörper]] · `Grundbruch._grundwasser`
- [[Raumlast unter Auftrieb]] · `_gamma_auftrieb`
- [[Reibungswinkel der Sohlfuge]] · `Gleiten.pruefe`
- [[Reichweite des Gleitkörpers]] · `Grundbruch._drainiert`
- [[Sohlneigungsfaktor b_c]] · `Grundbruch._drainiert`
- [[Sohlneigungsfaktor b_c]] · `Grundbruch._undrainiert`
- [[Sohlneigungsfaktor b_q]] · `Grundbruch._drainiert`
- [[Sohlneigungsfaktor b_γ]] · `Grundbruch._drainiert`
- [[Tiefe des Gleitkörpers]] · `Grundbruch._drainiert`
- [[Tiefenfaktor d_c]] · `Grundbruch._drainiert`
- [[Tiefenfaktor d_c]] · `Grundbruch._undrainiert`
- [[Tiefenfaktor d_q]] · `Grundbruch._drainiert`
- [[Tragfähigkeitsfaktor N_c]] · `Grundbruch._drainiert`
- [[Tragfähigkeitsfaktor N_q]] · `Grundbruch._drainiert`
- [[Tragfähigkeitsfaktor N_γ]] · `Grundbruch._drainiert`
- [[Tragfähigkeitsformel undrainiert]] · `Grundbruch._undrainiert`
- [[Überlagerung auf Höhe der Sohle]] · `Grundbruch._grundwasser`
- [[Überlagerung auf Höhe der Sohle]] · `Grundbruch._undrainiert`
- [[Winkel der Einbindetiefe]] · `Grundbruch._einbindewinkel`
