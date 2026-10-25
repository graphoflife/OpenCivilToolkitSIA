---
erzeugt: c9b35d1194c9
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/querkraft_buegel.py
> Querkraft mit Querkraftbewehrung.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/querkraft_buegel.py)

## VERANTWORTUNG

Der Querkraftnachweis einer Platte mit Buegeln ([[opencivil.nachweis.querkraft_buegel#QuerkraftMitBuegeln|QuerkraftMitBuegeln]]),
samt dem Verlauf seines Widerstands ueber der Neigung. Was er mit dem Ansatz
ohne Buegel teilt, steht in [[opencivil.nachweis.querkraft]].


## MIT BUEGELN

Fachwerkmodell, siehe [[opencivil.nachweis.querkraft_buegel#buegelwiderstand|buegelwiderstand]]:

```
V_Rd,s = A_(⌀,V)/(s_V,x * s_V,y) * 0.9 * d * f_yd * cot(alpha)
V_Rd,c = 0.9 * d * k_c * f_cd * sin(alpha) * cos(alpha)
V_Rd   = max ueber alpha von min(V_Rd,s; V_Rd,c)
```

Gesucht wird ganzgradig zwischen `alpha_min` und `alpha_max`. Bei
Normalzug steilt sich die Druckdiagonale auf -- beide Grenzen werden dann auf
mindestens `ALPHA_ZUG` gehoben. Der Betonanteil des Ansatzes ohne Buegel
geht nicht zusaetzlich ein.

## Inhalt

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
[[opencivil.nachweis.querkraft_buegel#Buegelwerte|Kurvenbeiwerte]] beim Ansatz ohne Buegel.

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

### buegelteilung_y

```python
def buegelteilung_y(buegel, b: float, menge_y: float) -> float
```

Die Buegelteilung in y, in m: angegeben -- oder aus der Stabzahl ueber die
betrachtete Breite `b`. Die Formel kennt nur Teilungen.

### protokoll_mit_buegeln

```python
def protokoll_mit_buegeln(p: Protokoll, werte: Zwischenwerte, widerstand: Wert, q: Buegelpunkt, *, e: Eingaben, s_y: Wert, d: Wert, alpha_min: int, alpha_max: int, seite: str='', zeichen: str='') -> None
```

Der Widerstand mit Buegeln bei der guenstigsten Neigung `q`: welche es
ist, die Buegel, die Druckdiagonale und das Kleinere beider.
`widerstand` ist der Wert, der dabei herauskommt; `seite` steht in
den Titeln, wo zwei Seiten nebeneinander stehen.

### BefundMitBuegeln

```python
@dataclass
class BefundMitBuegeln
```

Was der Nachweis mit Buegeln festhaelt: je Fall die Zwischenwerte, dazu
die geloesten Eingaenge des Ansatzes. Daraus zeichnet sich der Verlauf
ueber der Neigung, ohne dass die Oberflaeche die Formel ein zweites Mal
enthaelt. Steht nach dem Lauf in der Loesung, nicht am Nachweis.

- `buegelwerte: Buegelwerte` – Die geloesten Eingaenge -- fuer [[opencivil.nachweis.querkraft_buegel#BefundMitBuegeln.neigungsverlauf|neigungsverlauf]].
- `ergebnisse: List['ErgebnisMitBuegeln'] = field(default_factory=list)`
- `ohne_einwirkung: Optional['ErgebnisMitBuegeln'] = None` – Ohne Lastfall: der Ast ueber der Neigung bei M = 0 und N = 0, damit das Bild auch ohne Fall dasteht. Kein Fall des Nachweises -- ohne Ausgabe, Urteil und Herleitung.

#### BefundMitBuegeln.neigungsverlauf

```python
def neigungsverlauf(self, d: float, von: int, bis: int) -> List[Buegelpunkt]
```

Der Widerstand ueber der Neigung -- fuer das Diagramm.

Ueber dieselbe Funktion wie der Nachweis selbst, nur ueber einen
weiteren Bereich: gezeichnet wird auch ausserhalb der beiden Grenzen,
dort blass. Zwei Rechenwege fuer dieselbe Kurve liefen auseinander.

### ErgebnisMitBuegeln

```python
@dataclass
class ErgebnisMitBuegeln(Querkraftergebnis)
```

Alle Zwischenwerte eines Falls mit Buegeln, damit die Herleitung vollstaendig ist.

- `punkte: Tuple[Buegelpunkt, ...] = ()` – Der Widerstand je ganzem Grad zwischen den beiden Grenzwinkeln.
- `massgebend: Optional[Buegelpunkt] = None` – Der Punkt mit dem groessten Widerstand -- daraus stammt `v_Rd`.
- `alpha_min: int = 0`
- `alpha_max: int = 0` – Die tatsaechlich verwendeten Grenzen; bei Normalzug angehoben.
- `zug_hebt_alpha: bool = False` – Ob die Grenzen wegen einer Normalzugkraft angehoben wurden.

### QuerkraftMitBuegeln

```python
class QuerkraftMitBuegeln(Querkraft)
```

Der Querkraftnachweis einer Platte mit Buegeln -- siehe Dateikopf.

#### QuerkraftMitBuegeln.pruefe

```python
def pruefe(self, e: Eingaben, p: Protokoll)
```

Fachwerkmodell: Bügel gegen Druckdiagonale, über die Neigung gesucht.

Der Betonanteil des bügellosen Ansatzes entfällt hier vollständig --
beides zu addieren wäre ein anderes Modell, und dieses Werkzeug rechnet
nur, was es auch herleitet.


## Konstanten

- `MIT_BUEGELN = 'Querkraftwiderstand mit Querkraftbewehrung'`
- `OHNE_EINWIRKUNG = Querkraftfall(name='ohne Einwirkung', V_Ed=Groesse(0.0, KN_PRO_M), M_…` – Was der Nachweis mit Buegeln ohne Lastfall rechnet, nur fuer sein Bild (siehe [[opencivil.nachweis.querkraft_buegel#BefundMitBuegeln|BefundMitBuegeln.ohne_einwirkung]]).

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.nachweis.querkraft]]
- [[opencivil.querschnitt.fachwerk]]
- [[opencivil.querschnitt.platte]]
- [[opencivil.querschnitt.zugseite]]

## Gebraucht von

- [[opencivil.nachweis.kennzahlen]]
- [[opencivil.projekt.aufbau.platte]]

## Formeln aus diesem Modul

- [[Querkraftwiderstand mit Querkraftbewehrung]] · `QuerkraftMitBuegeln._protokoll_ansatz_buegel`
- [[Querkraftwiderstand mit Querkraftbewehrung]] · `protokoll_mit_buegeln`
- [[Teilung in y aus der Stabzahl]] · `QuerkraftMitBuegeln._protokoll_ansatz_buegel`
- [[Widerstand der Bügel]] · `protokoll_mit_buegeln`
- [[Widerstand der Druckdiagonalen]] · `protokoll_mit_buegeln`
