---
erzeugt: 0a2294aca71c
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/querkraft.py
> Querkraftnachweis.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/querkraft.py)

## VERANTWORTUNG

Bestimmt den Querkraftwiderstand einer Platte je Tragrichtung und prueft ihn
gegen die angegebenen Querkraefte.


## ZWEI ANSAETZE, EINER DAVON GILT

Ob die Platte eine Querkraftbewehrung traegt, entscheidet allein, welcher der
beiden laeuft. Beides zu addieren waere ein drittes Modell -- und dieses
Werkzeug rechnet nur, was es auch herleitet.


## MIT BUEGELN

Fachwerkmodell, siehe [[opencivil.nachweis.querkraft#buegelwiderstand|buegelwiderstand]]:

```
V_Rd,s = A_(⌀,V)/(s_V,x * s_V,y) * 0.9 * d * f_yd * cot(alpha)
V_Rd,c = 0.9 * d * k_c * f_cd * sin(alpha) * cos(alpha)
V_Rd   = max ueber alpha von min(V_Rd,s; V_Rd,c)
```

Gesucht wird ganzgradig zwischen `alpha_min` und `alpha_max`. Bei
Normalzug steilt sich die Druckdiagonale auf -- beide Grenzen werden dann auf
mindestens `ALPHA_ZUG` gehoben.


## OHNE BUEGEL


```
V_Rd = k_d * tau_cd * d_v

k_d   = 1 / (1 + eps_v * d * k_g)
k_g   = 48 / (16 + D_max * min[1.0; (60/f_ck)^2])
m_Dd  = |N_Ed| * h / 6                      Dekompressionsmoment
eps_v = f_yd * (m_Ed - m_Dd) / (E_s * (m_Rd(N_Ed) - m_Dd))

d_v = d - Einlagenhoehe,  falls  h/6 < Einlagenhoehe < d
d_v = d                   sonst
```

`d` ist die statische Hoehe der *gezogenen* Bewehrung und haengt damit vom
Vorzeichen des Moments ab: bei positivem Moment liegt der Zug unten, bei
negativem oben.


## ZUG BRAUCHT KEINEN SONDERFALL

Das Dekompressionsmoment ist ueber `min(N_Ed; 0)` definiert und wird bei
einer Normalzugkraft von selbst null -- entlastend wirkt nur Druck. Der
Nachweis laeuft damit unveraendert weiter; frueher stand hier ein Sonderfall,
der `V_Rd = 0` setzte.


## EINHEITEN

Die Formeln der Norm sind dimensionell inhomogen -- `d` und `D_max` gehen
in Millimeter ein, `f_ck` in N/mm^2. `k_g` laeuft deshalb ueber
[[opencivil.core.einheiten#empirisch|opencivil.core.einheiten.empirisch]], das diese Voraussetzung erzwingt;
`k_d` rechnet `d` in Millimeter um, und die Herleitung sagt es dazu.
`V_Rd` ergibt sich in N/mm, also kN/m -- eine Querkraft je Laufmeter.

## Inhalt

### Kurvenbeiwerte

```python
@dataclass(frozen=True)
class Kurvenbeiwerte
```

Was ausser Moment und Normalkraft in den Widerstand eingeht.

Alles in SI-Basis. Steht nach dem Lauf am Nachweis bereit, damit sich die
Kurve zu jeder eingestellten Normalkraft neu rechnen laesst -- ohne dass
die Oberflaeche die Formel ein zweites Mal enthaelt.

- `h: float`
- `lagen: Tuple[Tuple[float, bool], ...]` – Je vorhandener Posten: `(z ab Oberkante, liegt unten)`.
- `einlage: float`
- `tau_cd: float`
- `f_yd: float`
- `E_s: float`
- `k_g: float`

#### Kurvenbeiwerte.hoehen

```python
def hoehen(self, moment_positiv: bool) -> Optional[Tuple[float, float]]
```

`(d, d_v)` fuer diese Momentenrichtung -- `None` ohne Zugbewehrung.

### Widerstandspunkt

```python
@dataclass(frozen=True)
class Widerstandspunkt
```

Was bei einem bestimmten Moment noch an Querkraft aufnehmbar ist.

Ein einzelner Punkt der Rechnung -- der Nachweis braucht ihn fuer seine
Faelle, die Kurve fuer ihre fuenfzig Stuetzstellen. Beide ueber dieselbe
Funktion, sonst zeigte das Diagramm etwas anderes als der Nachweis.

- `m_Dd: float`
- `eps_v: float`
- `k_d: float`
- `v_Rd: float` – in N/m.
- `plastisch: bool = False` – `m_Ed` liegt ueber dem Momentenwiderstand; die Bewehrung fliesst.
- `grund: str = ''` – Gesetzt, wenn sich kein Widerstand bestimmen liess.

### widerstand

```python
def widerstand(*, M_Ed: float, N_Ed: float, h: float, d: float, d_v: float, tau_cd: float, f_yd: float, E_s: float, k_g: float, m_Rd: float, index: str='Rd') -> Widerstandspunkt
```

Der Querkraftwiderstand bei diesem Moment und dieser Normalkraft.

Alles in SI-Basis; `tau_cd` in Pa, `m_Rd` in Nm, Rueckgabe in N/m.
`index` ist der des Momentenwiderstands, `Rd` oder `Rk` -- je nach
der Linie, aus der er kommt; er steht nur im Text.

**DREI AESTE**


* `|m_Ed| <= m_Dd` -- der Querschnitt bleibt ungerissen, `eps_v = 0`
  und `k_d` damit am groessten.
* `|m_Ed| <= m_Rd` -- der Regelfall der Norm.
* `|m_Ed| >  m_Rd` -- die Bewehrung fliesst. Die Dehnung folgt dann nicht
  mehr dem Moment, sondern ist **fest**: `eps_v = 1.5 * f_yd/E_s`. Der
  Widerstand faellt an dieser Stelle sprunghaft und bleibt danach
  unveraendert -- in der Kurve eine Waagrechte.

### Buegelpunkt

```python
@dataclass(frozen=True)
class Buegelpunkt
```

Was bei einer bestimmten Neigung der Druckdiagonalen aufnehmbar ist.

Beide Anteile in N/m, also je Laufmeter -- wie `V_Ed`.

- `alpha: int` – Neigung der Druckdiagonalen in Grad.
- `V_Rd_s: float` – Bügel: waechst, je flacher die Diagonale liegt.
- `V_Rd_c: float` – Druckdiagonale: groesst bei 45°, faellt nach beiden Seiten.

#### Buegelpunkt.V_Rd

```python
@property
def V_Rd(self) -> float
```

Massgebend ist der kleinere der beiden -- eines von beiden versagt.

### fachwerk

```python
def fachwerk(*, alpha: int, a_sw_s: float, z: float, b_w: float, f_yd: float, f_cd: float, k_c: float) -> Buegelpunkt
```

Fachwerkmodell mit veraenderlicher Neigung der Druckdiagonalen -- fuer die
Buegel einer Platte wie fuer eine Schubwand der Querschnittsanalyse.

Alles in SI-Basis: Flaechen in m^2, Laengen in m, Festigkeiten in Pa:

```
V_Rd,s = A_sw/s · z · f_yd · cot(alpha)
V_Rd,c = b_w · z · k_c · f_cd · sin(alpha) · cos(alpha)
```

`A_sw/s` ist der Bewehrungsgehalt je Laenge in Laengsrichtung, `z`
der Hebelarm der inneren Kraefte, `b_w` die Breite des Stegs.

### buegelwiderstand

```python
def buegelwiderstand(*, alpha: int, a_s: float, s_x: float, s_y: float, d: float, f_yd: float, f_cd: float, k_c: float) -> Buegelpunkt
```

Das Fachwerk der Platte, je Laufmeter (Rueckgabe in N/m):

```
V_Rd,s = A_(⌀,V)/(s_x · s_y) · 0.9 · d · f_yd · cot(alpha)
V_Rd,c = 0.9 · d · k_c · f_cd · sin(alpha) · cos(alpha)
```

`A_(⌀,V)/(s_x · s_y)` ist der Bewehrungsgehalt: ein Buegelschenkel je
Rasterfeld. Beide Groessen gelten **je Laufmeter** -- so wie `V_Ed` und
wie der Widerstand ohne Buegel. Darum ist die Stegbreite ein Meter, und der
Hebelarm `0.9 · d`.

### Buegelwerte

```python
@dataclass(frozen=True)
class Buegelwerte
```

Was ausser der Neigung und der statischen Hoehe in den Widerstand eingeht.

Alles in SI-Basis. Steht nach dem Lauf am Nachweis bereit, damit sich der
Verlauf ueber der Neigung zeichnen laesst -- ohne dass die Oberflaeche die
Formel ein zweites Mal enthaelt. Dasselbe Muster wie
[[opencivil.nachweis.querkraft#Kurvenbeiwerte|Kurvenbeiwerte]] beim Ansatz ohne Buegel.

- `a_s: float`
- `s_x: float`
- `s_y: float`
- `f_yd: float`
- `f_cd: float`
- `k_c: float`

### neigungen

```python
def neigungen(*, alpha_min: int, alpha_max: int, **werte: float) -> List[Buegelpunkt]
```

Je ganzes Grad im Bereich ein Punkt, einschliesslich der Grenzen.

### beste_neigung

```python
def beste_neigung(punkte: Sequence[Buegelpunkt]) -> Buegelpunkt
```

Die Neigung mit dem groessten Widerstand.

`V_Rd,s` waechst mit flacherer Diagonale, `V_Rd,c` faellt dabei --
das Kleinere von beiden hat sein Groesstes dort, wo sich die beiden
Aeste treffen. Gesucht wird ganzgradig; bei Gleichstand gilt die
steilere Neigung, weil sie die Druckdiagonale weniger beansprucht.

### _statische_hoehe

```python
def _statische_hoehe(lagen: Sequence[Tuple[float, bool]], h: float, moment_positiv: bool) -> Optional[float]
```

Statische Hoehe der gezogenen Bewehrung, in m ab der gedrueckten Kante.

`lagen` ist eine Folge von `(z ab Oberkante, liegt unten)`.

Bei positivem Moment liegt der Zug unten: gemessen wird von der Oberkante
zur aeussersten unteren Lage. Bei negativem Moment umgekehrt. **Nur die
Lagen der gezogenen Seite zaehlen.** Wer alle nimmt, bekommt bei
einseitiger Bewehrung eine Zahl, die gar keine statische Hoehe ist: eine
Platte nur mit unterer Bewehrung lieferte fuers negative Moment
`h - 261 = 39 mm` -- den Abstand der Unterkante zur *unteren* Lage.

`None`, wenn auf der gezogenen Seite nichts liegt. Dann gibt es kein
`d`, und ohne `d` keinen Querkraftwiderstand.

### _zuglage

```python
def _zuglage(lagen: Sequence[Tuple[float, bool]], moment_positiv: bool) -> Optional[int]
```

Die aeusserste Lage der gezogenen Seite, als Index in `lagen`.

### _ohne_zugbewehrung

```python
def _ohne_zugbewehrung(M_Ed: float) -> str
```

Die Begruendung, wenn die gezogene Seite keinen Stahl hat -- fuer beide Ansaetze.

### Querkraftfall

```python
@dataclass(frozen=True)
class Querkraftfall
```

Eine zu pruefende Kombination fuer den Querkraftnachweis.

- `name: str`
- `V_Ed: Groesse`
- `M_Ed: Groesse`
- `N_Ed: Groesse`

#### Querkraftfall.kennung

```python
@property
def kennung(self) -> str
```

### Querkraftergebnis

```python
@dataclass
class Querkraftergebnis
```

Alle Zwischenwerte eines Falls, damit die Herleitung vollstaendig ist.

- `fall: Querkraftfall`
- `zuglage: Optional[int] = None` – Die aeusserste gezogene Lage, als Index in den Posten -- aus ihr kommt `d`.
- `d: float = 0.0`
- `d_v: float = 0.0`
- `k_g: float = 0.0`
- `k_d: float = 0.0`
- `eps_v: float = 0.0`
- `m_Dd: float = 0.0`
- `m_Rd: float = 0.0` – Momentenwiderstand bei der wirkenden Normalkraft, in Nm.
- `v_Rd: float = 0.0` – in N/m.
- `plastisch: bool = False` – `m_Ed` liegt ueber dem Momentenwiderstand -- siehe [[opencivil.nachweis.querkraft#widerstand|widerstand]].
- `erfuellungsgrad: float = 0.0`
- `erfuellt: bool = False`
- `begruendung: str = ''`
- `hinweis: str = ''` – Gesetzt, wenn sich gar kein Widerstand bestimmen liess -- siehe [[opencivil.core.berechnung#NachweisUrteil|opencivil.core.berechnung.NachweisUrteil.hinweis]].
- `punkte: Tuple[Buegelpunkt, ...] = ()` – Der Widerstand je ganzem Grad zwischen den beiden Grenzwinkeln.
- `massgebend: Optional[Buegelpunkt] = None` – Der Punkt mit dem groessten Widerstand -- daraus stammt `v_Rd`.
- `alpha_min: int = 0`
- `alpha_max: int = 0` – Die tatsaechlich verwendeten Grenzen; bei Normalzug angehoben.
- `zug_hebt_alpha: bool = False` – Ob die Grenzen wegen einer Normalzugkraft angehoben wurden.

### Querkraft

```python
class Querkraft(Nachweis)
```

Querkraftwiderstand je Tragrichtung.

**ZWEI ANSAETZE, EINER DAVON GILT**


* **Ohne Buegel** -- `V_Rd = k_d · tau_cd · d_v`, der Widerstand des
  Betons allein. Er haengt ueber `eps_v` an `m_Ed` und `m_Rd(N_Ed)`
  und damit an der Einwirkung.
* **Mit Buegeln** -- das Fachwerkmodell aus [[opencivil.nachweis.querkraft#buegelwiderstand|buegelwiderstand]]. Der
  Betonanteil des ersten Ansatzes entfaellt dann vollstaendig; massgebend
  ist das Kleinere aus Buegel- und Druckdiagonalenwiderstand, gesucht
  ueber die guenstigste Neigung.

Welcher gilt, entscheidet allein, ob die Platte eine Querkraftbewehrung
traegt -- nicht eine Einstellung daneben.

- `THEMA = 'Querkraft'`

#### Querkraft.pruefe

```python
def pruefe(self, e: Eingaben, p: Protokoll)
```

#### Querkraft._eintragen

```python
def _eintragen(self, erg: Querkraftergebnis, ergebnis: Dict[str, Groesse], urteile: List[NachweisUrteil]) -> None
```

Ausgaben und Urteil eines Falls -- fuer beide Ansaetze dieselben.

Was ein Querkraftnachweis herausgibt, haengt nicht davon ab, wie der
Widerstand zustande kam. Zweimal geschrieben liefen die beiden Faelle
frueher oder spaeter auseinander.

#### Querkraft._einwirkung

```python
def _einwirkung(self, fall: Querkraftfall) -> Wert
```

Die Querkraft als Betrag -- fuer Urteil und Erfuellungsgrad dieselbe.

Das Vorzeichen spielt keine Rolle, verglichen wird der Betrag. Also
steht auch der Betrag da; sonst teilte der Leser den Widerstand durch
eine negative Zahl und bekaeme etwas anderes als den danebenstehenden
Erfuellungsgrad. Die Betragsstriche stehen trotzdem nicht am Symbol:
sie sagen nichts, was die Zahl daneben nicht schon zeigt.

#### Querkraft._widerstand

```python
def _widerstand(self, erg: Querkraftergebnis) -> Wert
```

Der Widerstand eines Falls -- fuer Urteil und Herleitung derselbe.

Er gilt nur unter genau dieser Einwirkung; das gehoert ins Symbol,
sonst liest sich V_Rd wie ein Kennwert des Querschnitts.

#### Querkraft._lagen

```python
def _lagen(self, e: Eingaben) -> List[Tuple[float, bool]]
```

Je Posten die Tiefe und auf welcher Seite er liegt -- ohne das laesst
sich die gezogene Bewehrung nicht von der gedrueckten trennen.

#### Querkraft._mit_buegeln

```python
def _mit_buegeln(self, e: Eingaben, p: Protokoll)
```

Fachwerkmodell: Bügel gegen Druckdiagonale, über die Neigung gesucht.

Der Betonanteil des bügellosen Ansatzes entfällt hier vollständig --
beides zu addieren wäre ein anderes Modell, und dieses Werkzeug rechnet
nur, was es auch herleitet.

#### Querkraft.kurve

```python
def kurve(self, N_Ed: float) -> dict
```

Der Querkraftwiderstand ueber dem Moment, bei festgehaltener Normalkraft.

**Ein** Diagramm je Tragrichtung, mit vorzeichenbehafteter Waagrechten:
rechts das positive Moment (Zug unten), links das negative (Zug oben).
Frueher waren das zwei Bilder; nebeneinander liessen sie sich schlecht
vergleichen, obwohl sie dieselbe Platte beschreiben.

Die beiden Aeste sind getrennte Linienzuege und treffen sich bei
`M_Ed = 0` nicht unbedingt: sie haben verschiedene statische Hoehen,
also auch verschiedene Widerstaende bei verschiedwindendem Moment. Das
ist kein Zeichenfehler, sondern die Platte.

Je Ast fuenfzig Stuetzstellen von null bis `m_Rd + 20 kNm`. Der
Bereich jenseits von `m_Rd` ist der eigentliche Zweck: dort faellt der
Widerstand, weil die Bewehrung fliesst (siehe [[opencivil.nachweis.querkraft#widerstand|widerstand]]).

Gerechnet wird mit derselben Funktion wie im Nachweis. Die Kurve kann
also nicht etwas anderes zeigen als die Punkte, die darauf liegen.

:param N_Ed: eingestellte Normalkraft in N, Zug positiv.

#### Querkraft._ast

```python
def _ast(self, N_Ed: float, moment_positiv: bool) -> Optional[dict]
```

Ein Ast der Kurve. `None`, wenn es ihn nicht gibt.

Es gibt ihn nicht, wenn auf der gezogenen Seite keine Bewehrung liegt
oder die Normalkraft ausserhalb der Resistenzlinie faellt -- in beiden
Faellen waere jeder gezeichnete Widerstand erfunden.

#### Querkraft.neigungsverlauf

```python
def neigungsverlauf(self, d: float, von: int, bis: int) -> List[Buegelpunkt]
```

Der Widerstand ueber der Neigung -- fuer das Diagramm.

Ueber dieselbe Funktion wie der Nachweis selbst, nur ueber einen
weiteren Bereich: gezeichnet wird auch ausserhalb der beiden Grenzen,
dort blass. Zwei Rechenwege fuer dieselbe Kurve liefen auseinander.

#### Querkraft._widerstandssymbol

```python
def _widerstandssymbol(self, fall: Querkraftfall) -> str
```

`V_Rd(M_Ed = 100 kNm, N_Ed = -300 kN)` -- der Widerstand ist bedingt.

#### Querkraft._protokoll_hoehe

```python
def _protokoll_hoehe(self, p: Protokoll, e: Eingaben, erg: Querkraftergebnis, werte: Zwischenwerte) -> Wert
```

Die statische Höhe der gezogenen Bewehrung -- geschrieben, und für die Formeln danach.

#### Querkraft._protokoll_grad

```python
def _protokoll_grad(self, p: Protokoll, erg: Querkraftergebnis) -> None
```

Die letzte Zeile jedes Falls -- für beide Ansätze dieselbe.

#### Querkraft._protokoll_fall

```python
def _protokoll_fall(self, p: Protokoll, e: Eingaben, erg: Querkraftergebnis, k_g: Wert) -> None
```

Die vollstaendige Rechnung eines Falls, mit Zahlen in jeder Zeile.

Frueher stand hier nur der Ansatz und eine Ergebnistabelle -- damit war
der Querkraftwiderstand die einzige Zahl im ganzen Werkzeug, die man
nicht nachrechnen konnte.


## Konstanten

- `K_G_MINDEST = 1.2` – Unterer Riegel fuer den Beiwert der Gesteinskoernung.
- `PLASTISCH = 1.5` – Vielfaches der Fliessdehnung, sobald `m_Ed` den Widerstand ueberschreitet. `eps_v = PLASTISCH * f_yd / E_s` -- fest, nicht vom Moment abhaengig.
- `OHNE_BUEGEL = 'Querkraftwiderstand ohne Querkraftbewehrung'` – Die Seiten der beiden Widerstaende im Notizbuch -- Ansatz und Rechnung stehen je auf derselben.
- `MIT_BUEGELN = 'Querkraftwiderstand mit Querkraftbewehrung'`
- `KURVENPUNKTE = 50` – Stuetzstellen der M_Ed-v_Rd-Kurve.
- `KURVENZUGABE = 20000.0` – Wie weit die Kurve ueber `m_Rd` hinaus gezeichnet wird, in Nm.
- `SPRUNGSCHRITT = 0.001` – Abstand der beiden Stellen, zwischen denen der Sprung bei `m_Rd` liegt, in Nm. Nur damit der Absatz senkrecht gezeichnet wird -- 1 mNm.
- `NUR_KURVE = Querkraftfall(name='ohne Einwirkung', V_Ed=Groesse(0.0, KN_PRO_M), M_…` – Der Fall eines Querkraftnachweises ohne Querkraft: er rechnet still, nur fuer das Diagramm -- die M-V-Kurve und der Verlauf ueber die Neigung brauchen die Beiwerte, die erst im Lauf entstehen. Ohne Einwirkung kein Urteil, kein Punkt im Bild und keine Zeile in der Werteliste; M = 0 misst d fuer das positive Moment.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.nachweis.biegung_normalkraft]]
- [[opencivil.querschnitt.platte]]

## Gebraucht von

- [[opencivil.projekt.aufbau]]
- [[opencivil.querschnitt.schubwaende]]
- [[opencivil.web.diagrammdaten]]

## Formeln aus diesem Modul

- [[Beiwert der Gesteinskörnung]] · `Querkraft._protokoll_k_g`
- [[Beiwert für die statische Höhe]] · `Querkraft._protokoll_fall`
- [[Dehnung auf halber Höhe]] · `Querkraft._protokoll_fall`
- [[Dekompressionsmoment]] · `Querkraft._protokoll_fall`
- [[Dekompressionsmoment und Dehnung]] · `Querkraft._protokoll_ansatz`
- [[Querkraftwiderstand mit Querkraftbewehrung]] · `Querkraft._protokoll_ansatz_buegel`
- [[Querkraftwiderstand mit Querkraftbewehrung]] · `Querkraft._protokoll_fall_buegel`
- [[Querkraftwiderstand ohne Querkraftbewehrung]] · `Querkraft._protokoll_ansatz`
- [[Querkraftwiderstand ohne Querkraftbewehrung]] · `Querkraft._protokoll_fall`
- [[Teilung in y aus der Stabzahl]] · `Querkraft._protokoll_ansatz_buegel`
- [[Widerstand der Bügel]] · `Querkraft._protokoll_fall_buegel`
- [[Widerstand der Druckdiagonalen]] · `Querkraft._protokoll_fall_buegel`
- [[Wirksame Höhe (Einlage nicht massgebend)]] · `Querkraft._protokoll_fall`
- [[Wirksame Höhe, um die Einlage vermindert]] · `Querkraft._protokoll_fall`
