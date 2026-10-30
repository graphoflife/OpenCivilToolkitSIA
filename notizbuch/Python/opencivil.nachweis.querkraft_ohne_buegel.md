---
erzeugt: a99c8d583a8b
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/querkraft_ohne_buegel.py
> Querkraft ohne Querkraftbewehrung.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/querkraft_ohne_buegel.py)

## VERANTWORTUNG

Der Querkraftnachweis einer Platte ohne Buegel ([[opencivil.nachweis.querkraft_ohne_buegel#QuerkraftOhneBuegel|QuerkraftOhneBuegel]]),
samt der Kurve seines Widerstands ueber dem Moment. Was er mit dem Ansatz mit
Buegeln teilt, steht in [[opencivil.nachweis.querkraft]].


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

### beiwert_k_g

```python
def beiwert_k_g(p: Protokoll, basis: str, D_max: Wert, f_ck: Wert) -> Wert
```

Der Beiwert der Gesteinskoernung, samt seiner Zeile in der Herleitung --
fuer den Querkraftnachweis und die Kennzahlen der Platte, eine Formel.
Empirisch: `D_max` in mm, `f_ck` in N/mm^2.

### tau_cd_wert

```python
def tau_cd_wert(werte: Zwischenwerte, e: Eingaben) -> Wert
```

tau_cd fuer die Herleitung, mit vier Stellen: in der Baustofftabelle steht
es auf zwei (1.1), und mit so wenigen ginge die Nachrechnung um ein halbes
Prozent daneben. Fuer den Nachweis und die Kennzahlen.

### protokoll_ohne_buegel

```python
def protokoll_ohne_buegel(p: Protokoll, werte: Zwischenwerte, widerstand: Wert, *, k_d: float, eps_v: Wert, d: Wert, d_v: Wert, k_g: Wert, tau_cd: Wert, titel: str='Querkraftwiderstand', zeichen: str='') -> None
```

Der Widerstand ohne Buegel aus der Dehnung `eps_v`, die schon dasteht:
`k_d` und `V_Rd = k_d · tau_cd · d_v`. `widerstand` ist der Wert,
der dabei herauskommt, mit seinem Zeichen.

### BefundOhneBuegel

```python
@dataclass
class BefundOhneBuegel
```

Was der Nachweis ohne Buegel festhaelt: je Fall die Zwischenwerte, dazu
die geloesten Eingaenge des Ansatzes. Daraus zeichnet sich die Kurve
ueber dem Moment, ohne dass die Oberflaeche die Formel ein zweites Mal
enthaelt. Steht nach dem Lauf in der Loesung, nicht am Nachweis.

- `beiwerte: Kurvenbeiwerte` – Die geloesten Eingaenge -- fuer [[opencivil.nachweis.querkraft_ohne_buegel#BefundOhneBuegel.kurve|kurve]].
- `mn: MNBefund` – Der Befund des M-N-Nachweises: aus seiner Linie kommt `m_Rd(N_Ed)` der Kurve.
- `index: str = 'Rd'` – Wie der Momentenwiderstand heisst -- `Rd`, oder `Rk` mit charakteristischen Werten.
- `ergebnisse: List['ErgebnisOhneBuegel'] = field(default_factory=list)`

#### BefundOhneBuegel.kurve

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
Widerstand, weil die Bewehrung fliesst (siehe [[opencivil.nachweis.querkraft_ohne_buegel#widerstand|widerstand]]).

Gerechnet wird mit derselben Funktion wie im Nachweis. Die Kurve kann
also nicht etwas anderes zeigen als die Punkte, die darauf liegen.

:param N_Ed: eingestellte Normalkraft in N, Zug positiv.

#### BefundOhneBuegel._ast

```python
def _ast(self, N_Ed: float, moment_positiv: bool) -> Optional[dict]
```

Ein Ast der Kurve. `None`, wenn es ihn nicht gibt.

Es gibt ihn nicht, wenn auf der gezogenen Seite keine Bewehrung liegt
oder die Normalkraft ausserhalb der Resistenzlinie faellt -- in beiden
Faellen waere jeder gezeichnete Widerstand erfunden.

### ErgebnisOhneBuegel

```python
@dataclass
class ErgebnisOhneBuegel(Querkraftergebnis)
```

Alle Zwischenwerte eines Falls ohne Buegel, damit die Herleitung vollstaendig ist.

- `d_v: float = 0.0`
- `k_d: float = 0.0`
- `eps_v: float = 0.0`
- `m_Dd: float = 0.0`
- `m_Rd: float = 0.0` – Momentenwiderstand bei der wirkenden Normalkraft, in Nm.
- `plastisch: bool = False` – `m_Ed` liegt ueber dem Momentenwiderstand -- siehe [[opencivil.nachweis.querkraft_ohne_buegel#widerstand|widerstand]].

### QuerkraftOhneBuegel

```python
class QuerkraftOhneBuegel(Querkraft)
```

Der Querkraftnachweis einer Platte ohne Buegel -- siehe Dateikopf.

#### QuerkraftOhneBuegel.pruefe

```python
def pruefe(self, e: Eingaben, p: Protokoll)
```

#### QuerkraftOhneBuegel._protokoll_fall

```python
def _protokoll_fall(self, p: Protokoll, e: Eingaben, erg: ErgebnisOhneBuegel, k_g: Wert, mn: MNBefund) -> None
```

Die vollstaendige Rechnung eines Falls, mit Zahlen in jeder Zeile.

Frueher stand hier nur der Ansatz und eine Ergebnistabelle -- damit war
der Querkraftwiderstand die einzige Zahl im ganzen Werkzeug, die man
nicht nachrechnen konnte.


## Konstanten

- `K_G_MINDEST = 1.2` – Unterer Riegel fuer den Beiwert der Gesteinskoernung.
- `PLASTISCH = 1.5` – Vielfaches der Fliessdehnung, sobald `m_Ed` den Widerstand ueberschreitet. `eps_v = PLASTISCH * f_yd / E_s` -- fest, nicht vom Moment abhaengig.
- `OHNE_BUEGEL = 'Querkraftwiderstand ohne Querkraftbewehrung'` – Die Seite des Widerstands im Notizbuch -- Ansatz und Rechnung stehen darauf.
- `KURVENPUNKTE = 50` – Stuetzstellen der M_Ed-v_Rd-Kurve.
- `KURVENZUGABE = 20000.0` – Wie weit die Kurve ueber `m_Rd` hinaus gezeichnet wird, in Nm.
- `SPRUNGSCHRITT = 0.001` – Abstand der beiden Stellen, zwischen denen der Sprung bei `m_Rd` liegt, in Nm. Nur damit der Absatz senkrecht gezeichnet wird -- 1 mNm.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.nachweis.biegung_normalkraft]]
- [[opencivil.nachweis.querkraft]]
- [[opencivil.nachweis.rechenwahl]]
- [[opencivil.querschnitt.zugseite]]

## Gebraucht von

- [[opencivil.durchstanzen.nachweis]]
- [[opencivil.nachweis.kennzahlen]]
- [[opencivil.projekt.aufbau.platte]]

## Formeln aus diesem Modul

- [[Beiwert der Gesteinskörnung]] · `beiwert_k_g`
- [[Beiwert für die statische Höhe]] · `protokoll_ohne_buegel`
- [[Dehnung auf halber Höhe]] · `QuerkraftOhneBuegel._protokoll_fall`
- [[Dekompressionsmoment]] · `QuerkraftOhneBuegel._protokoll_fall`
- [[Dekompressionsmoment und Dehnung]] · `QuerkraftOhneBuegel._protokoll_ansatz`
- [[Querkraftwiderstand ohne Querkraftbewehrung]] · `QuerkraftOhneBuegel._protokoll_ansatz`
- [[Querkraftwiderstand ohne Querkraftbewehrung]] · `protokoll_ohne_buegel`
