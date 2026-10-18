---
erzeugt: 0f483e3370ff
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
- `zugstahl: Mapping[bool, Tuple[float, float]]` – Je Momentenrichtung (`True`: Zug unten) `(f_yd, E_s)` des Stahls der gezogenen Seite -- unten und oben duerfen verschiedene Staehle liegen. Fehlt eine Richtung, liegt auf ihrer Zugseite keine Bewehrung.
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

### zuglage

```python
def zuglage(lagen: Sequence[Tuple[float, bool]], moment_positiv: bool) -> Optional[int]
```

Die aeusserste Lage der gezogenen Seite, als Index in `lagen`.

### beiwert_k_g

```python
def beiwert_k_g(p: Protokoll, basis: str, D_max: Wert, f_ck: Wert) -> Wert
```

Der Beiwert der Gesteinskoernung, samt seiner Zeile in der Herleitung --
fuer den Querkraftnachweis und die Kennzahlen der Platte, eine Formel.
Empirisch: `D_max` in mm, `f_ck` in N/mm^2.

### buegelteilung_y

```python
def buegelteilung_y(buegel, b: float, menge_y: float) -> float
```

Die Buegelteilung in y, in m: angegeben -- oder aus der Stabzahl ueber die
betrachtete Breite `b`. Die Formel kennt nur Teilungen.

### _hoch

```python
def _hoch(kurz: str, symbol: str, zeichen: str) -> Tuple[str, str]
```

Kurzname und Zeichen, mit `zeichen` hochgestellt: `d_+` und `d^{+}`.

### protokoll_hoehen

```python
def protokoll_hoehen(p: Protokoll, werte: Zwischenwerte, e: Eingaben, posten, zuglage: int, d: float, d_v: Optional[float]=None, *, positiv: bool, zeichen: str='') -> Tuple[Wert, Optional[Wert]]
```

Die statische Hoehe der gezogenen Bewehrung und, ohne Buegel, die
wirksame -- geschrieben, und fuer die Formeln danach. `zuglage` ist der
Posten der aeussersten gezogenen Lage ([[opencivil.nachweis.querkraft#zuglage|zuglage]]), `positiv`, ob
der Zug unten liegt. `zeichen` hebt die Groessen hoch, wo zwei Seiten
nebeneinander stehen: `d^{+}` (die Kennzahlen).

Mit Buegeln gibt es kein `d_v`: bis 2026-10-18 schrieben die Kennzahlen
dort ein «d_v = d (Einlage nicht massgebend)», weil sie die Hoehen ohne
Buegel mit einer Einlage null mitbenutzten.

### protokoll_ohne_buegel

```python
def protokoll_ohne_buegel(p: Protokoll, werte: Zwischenwerte, widerstand: Wert, *, k_d: float, eps_v: Wert, d: Wert, d_v: Wert, k_g: Wert, tau_cd: Wert, titel: str='Querkraftwiderstand', zeichen: str='') -> None
```

Der Widerstand ohne Buegel aus der Dehnung `eps_v`, die schon dasteht:
`k_d` und `V_Rd = k_d · tau_cd · d_v`. `widerstand` ist der Wert,
der dabei herauskommt, mit seinem Zeichen.

### protokoll_mit_buegeln

```python
def protokoll_mit_buegeln(p: Protokoll, werte: Zwischenwerte, widerstand: Wert, q: Buegelpunkt, *, e: Eingaben, s_y: Wert, d: Wert, alpha_min: int, alpha_max: int, seite: str='', zeichen: str='') -> None
```

Der Widerstand mit Buegeln bei der guenstigsten Neigung `q`: welche es
ist, die Buegel, die Druckdiagonale und das Kleinere beider.
`widerstand` ist der Wert, der dabei herauskommt; `seite` steht in
den Titeln, wo zwei Seiten nebeneinander stehen.

### _ohne_zugbewehrung

```python
def _ohne_zugbewehrung(M_Ed: float) -> str
```

Die Begruendung, wenn die gezogene Seite keinen Stahl hat -- fuer beide Ansaetze.

### Querkraftbefund

```python
@dataclass
class Querkraftbefund
```

Was der Querkraftnachweis festhaelt: je Fall die Zwischenwerte, dazu die
geloesten Eingaenge seines Ansatzes. Daraus zeichnet sich die Kurve ueber
dem Moment (ohne Buegel) oder ueber der Neigung (mit Buegeln), ohne dass
die Oberflaeche die Formel ein zweites Mal enthaelt. Steht nach dem Lauf
in der Loesung, nicht am Nachweis.

- `ergebnisse: List['Querkraftergebnis'] = field(default_factory=list)`
- `beiwerte: Optional[Kurvenbeiwerte] = None` – Die geloesten Eingaenge ohne Buegel -- fuer [[opencivil.nachweis.querkraft#Querkraftbefund.kurve|kurve]].
- `buegelwerte: Optional[Buegelwerte] = None` – Die geloesten Eingaenge des Buegelansatzes -- fuer [[opencivil.nachweis.querkraft#Querkraftbefund.neigungsverlauf|neigungsverlauf]].
- `mn: Optional[MNBefund] = None` – Der Befund des M-N-Nachweises: aus seiner Linie kommt `m_Rd(N_Ed)` der Kurve.
- `index: str = 'Rd'` – Wie der Momentenwiderstand heisst -- `Rd`, oder `Rk` mit charakteristischen Werten.
- `ohne_einwirkung: Optional['Querkraftergebnis'] = None` – Mit Buegeln und ohne Lastfall: der Ast ueber der Neigung bei M = 0 und N = 0, damit das Bild auch ohne Fall dasteht. Kein Fall des Nachweises -- ohne Ausgabe, Urteil und Herleitung.

#### Querkraftbefund.kurve

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

#### Querkraftbefund._ast

```python
def _ast(self, N_Ed: float, moment_positiv: bool) -> Optional[dict]
```

Ein Ast der Kurve. `None`, wenn es ihn nicht gibt.

Es gibt ihn nicht, wenn auf der gezogenen Seite keine Bewehrung liegt
oder die Normalkraft ausserhalb der Resistenzlinie faellt -- in beiden
Faellen waere jeder gezeichnete Widerstand erfunden.

#### Querkraftbefund.neigungsverlauf

```python
def neigungsverlauf(self, d: float, von: int, bis: int) -> List[Buegelpunkt]
```

Der Widerstand ueber der Neigung -- fuer das Diagramm.

Ueber dieselbe Funktion wie der Nachweis selbst, nur ueber einen
weiteren Bereich: gezeichnet wird auch ausserhalb der beiden Grenzen,
dort blass. Zwei Rechenwege fuer dieselbe Kurve liefen auseinander.

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

#### Querkraft._widerstandssymbol

```python
def _widerstandssymbol(self, fall: Querkraftfall) -> str
```

`V_Rd(M_Ed = 100 kNm, N_Ed = -300 kN)` -- der Widerstand ist bedingt.

#### Querkraft._protokoll_grad

```python
def _protokoll_grad(self, p: Protokoll, erg: Querkraftergebnis) -> None
```

Die letzte Zeile jedes Falls -- für beide Ansätze dieselbe.

#### Querkraft._protokoll_fall

```python
def _protokoll_fall(self, p: Protokoll, e: Eingaben, erg: Querkraftergebnis, k_g: Wert, mn: MNBefund) -> None
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
- `OHNE_EINWIRKUNG = Querkraftfall(name='ohne Einwirkung', V_Ed=Groesse(0.0, KN_PRO_M), M_…` – Was der Nachweis mit Buegeln ohne Lastfall rechnet, nur fuer sein Bild (siehe [[opencivil.nachweis.querkraft#Querkraftbefund|Querkraftbefund.ohne_einwirkung]]).

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.nachweis.biegung_normalkraft]]
- [[opencivil.nachweis.rechenwahl]]
- [[opencivil.querschnitt.fachwerk]]
- [[opencivil.querschnitt.platte]]

## Gebraucht von

- [[opencivil.nachweis.kennzahlen]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.aufbau.platte]]

## Formeln aus diesem Modul

- [[Beiwert der Gesteinskörnung]] · `beiwert_k_g`
- [[Beiwert für die statische Höhe]] · `protokoll_ohne_buegel`
- [[Dehnung auf halber Höhe]] · `Querkraft._protokoll_fall`
- [[Dekompressionsmoment]] · `Querkraft._protokoll_fall`
- [[Dekompressionsmoment und Dehnung]] · `Querkraft._protokoll_ansatz`
- [[Querkraftwiderstand mit Querkraftbewehrung]] · `Querkraft._protokoll_ansatz_buegel`
- [[Querkraftwiderstand mit Querkraftbewehrung]] · `protokoll_mit_buegeln`
- [[Querkraftwiderstand ohne Querkraftbewehrung]] · `Querkraft._protokoll_ansatz`
- [[Querkraftwiderstand ohne Querkraftbewehrung]] · `protokoll_ohne_buegel`
- [[Teilung in y aus der Stabzahl]] · `Querkraft._protokoll_ansatz_buegel`
- [[Widerstand der Bügel]] · `protokoll_mit_buegeln`
- [[Widerstand der Druckdiagonalen]] · `protokoll_mit_buegeln`
- [[Wirksame Höhe (Einlage nicht massgebend)]] · `protokoll_hoehen`
- [[Wirksame Höhe, um die Einlage vermindert]] · `protokoll_hoehen`
