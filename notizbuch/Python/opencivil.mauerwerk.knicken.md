---
erzeugt: e0ebe6257617
art: modul
tags: [modul]
---
> [!abstract] opencivil/mauerwerk/knicken.py
> ein Pfeiler unter Normalkraft nach Theorie 2. Ordnung.
> Paket [[opencivil.mauerwerk]] · [Quelltext](../../opencivil/mauerwerk/knicken.py)

## VERANTWORTUNG

Der Beiwert k_N eines Pfeilers (SIA 266:2015, 4.3.1.3, Gl. (11)): die
grösste Normalkraft, bezogen auf l_w · t_w · f_xd, unter der die verformte
Wand im Gleichgewicht steht (4.3.1.1) und ihre Ausmitte nirgends die Grenze
der Figur 4 überschreitet ([[opencivil.mauerwerk.knicken#k_N|k_N]]). Dazu der Zustand unter der
Normalkraft der Bemessung: wie weit die Wand ausweicht und wo. Und unter
einer festen Normalkraft die grösste Querlast, die die Wand so trägt – das
lotrechte Druckgewölbe (4.3.4.2, Figur 11, [[opencivil.mauerwerk.knicken#querlast|querlast]]).


## DAS MODELL

Ein Streifen der Wand von Fuss bis Kopf, beide waagrecht gehalten (4.3), die
Normalkraft über die ganze Höhe gleich. Gelenkig gehalten greift sie dort mit
ihrer Ausmitte an; eingespannt dreht sich die Wand dort nicht, und die
Ausmitte ergibt sich – wie in den Fällen der Tabelle 9 und des Anhangs A.
Die Ausmitte in der Höhe x ist e(x) = e_u + (e_o − e_u) · x/h + w(x), w die
Auslenkung der Wand. Ihre Krümmung -w'' folgt aus der Ausmitte nach Figur 3:

```
χ · h_Ed² / t = 4.1 · tan(2.4 e/t) · [1 + tan²(2.4 e/t)],
h_Ed = π √(B_yd / N_xd)                      (Figur 19)
```

bis e = 0.375 t; dort ist das Moment am Ende (Figur 3), und mehr Ausmitte
lässt Figur 4 nicht zu: höchstens 0.375 t und nach Gl. (6) höchstens
(1 − N_xd/(l_w t_w f_xd)) · t/2.

Eine Querlast q, gleichmässig über die Höhe, gibt dazu das Moment eines
einfachen Balkens, q · x · (h − x)/2 je Meter, also die Ausmitte
q · x · (h − x)/(2 N) je Meter Wand. Ein eingespannter Rand nimmt sein
Moment wie ohne Querlast über seine Ausmitte auf, die das Gleichgewicht
bestimmt.

B_yd = E_xd · I_y, wie in Gl. (8) – nach Vorgabe, nicht nachgeschlagen:
4.3.1.3 nennt B_yd, ohne es festzulegen. So sind auch die Kurven der Figur 5
gerechnet: die Rechnung hier trifft sie bis e/t = 0.30 auf etwa 0.006
(tests/test_mauerwerk_nachweise.py), mit dem Faktor √(1 − N/(2 A f)) der
Figur 3 lägen sie bis 20 % tiefer. Die Kurve e/t = 0.35 der Figur 5 liegt
dagegen fast doppelt so hoch, wie Figur 3 und 4 es zulassen; die Kurven der
Figur 19 stimmen mit beiden überein. Gerechnet wird nach Figur 3 und 4.


## GERECHNET WIRD IN TEILEN DER DICKE

Alle Längen durch t_w, die Normalkraft als n = N/(l_w t_w f_xd). Dann hängt
alles nur noch an h_w/t_w, den Ausmitten in t_w und E_xd/f_xd, für
Standardmauerwerk 1000 (4.2.1.4) – k_N ist für jeden Pfeiler derselbe
Beiwert, wie breit er auch ist. Die Querlast heisst dort
λ = q · h_w²/(t_w² · f_xd), q je m² Wand; ihre Ausmitte in Dicken ist
λ · ξ · (1 − ξ)/(2 n), ξ = x/h_w.


## DIE SUCHE (nach Vorgabe, nicht nachgeschlagen)

Die Wand in [[opencivil.mauerwerk.knicken#Konstanten|TEILE]] Stücke geteilt, je Knoten das Gleichgewicht w'' =
−χ(e) als finite Differenz, gelöst nach Newton. n wächst in Schritten, jedes
Gleichgewicht vom vorigen aus. Eine Stufe gilt, wenn das Gleichgewicht
besteht, nicht gekippt ist – die Determinante der Ableitung behält das
Vorzeichen, das sie bei kleiner Last hat – und die Ausmitte nirgends über
der Grenze liegt. Hält eine Stufe nicht, wird der Schritt halbiert, bis er
kleiner ist als [[opencivil.mauerwerk.knicken#Konstanten|GENAU]]. Erreicht die Ausmitte 0.375 t, endet die
Rechnung dort: ein Gelenk, das sich bei kleiner Normalkraft weiter drehen
dürfte (4.3.1.1), zählt sie nicht – auf der sicheren Seite.

Die Querlast sucht [[opencivil.mauerwerk.knicken#querlast|querlast]] ebenso: erst die Normalkraft bis n wie
bei k_N, dann wächst λ in Schritten, die sich halbieren, bis die Wand kein
Gleichgewicht mehr findet oder ihre Ausmitte die Grenze erreicht. Die
Schritte messen sich an λ_1 = 8 · n · Grenze(n), der Querlast, die eine
mittig belastete, gelenkig gehaltene Wand nach Theorie 1. Ordnung trägt.

## Inhalt

### g

```python
def g(u: float) -> float
```

χ · h_Ed²/t zu einer Ausmitte von `u` Dicken – Figur 3, ungerade fortgesetzt.

### _dg

```python
def _dg(u: float) -> float
```

Die Ableitung von [[opencivil.mauerwerk.knicken#g|g]] nach u.

### grenze

```python
def grenze(n: float) -> float
```

Die grösste Ausmitte in Dicken unter n: Figur 4 0.375, Gl. (6) höchstens (1 − n)/2.

### Zustand

```python
@dataclass(frozen=True)
class Zustand
```

Ein Gleichgewicht der Wand: unter n die Ausmitte je Knoten, von unten nach oben.

- `n: float`
- `e: Tuple[float, ...]`

#### Zustand.stelle

```python
@property
def stelle(self) -> int
```

Der Knoten mit der grössten Ausmitte.

#### Zustand.e_max

```python
@property
def e_max(self) -> float
```

Die grösste Ausmitte, mit Vorzeichen.

#### Zustand.hoehe

```python
@property
def hoehe(self) -> float
```

Wo sie liegt: der Anteil der Höhe ab dem Fuss, 0 bis 1.

#### Zustand.e_u

```python
@property
def e_u(self) -> float
```

#### Zustand.e_o

```python
@property
def e_o(self) -> float
```

### Knickergebnis

```python
@dataclass(frozen=True)
class Knickergebnis
```

Was die Rechnung findet – `bei_n_d` der Zustand unter n_d, `None` darüber.

- `k_N: float`
- `grund: str` – [[opencivil.mauerwerk.knicken#Konstanten|DRUCK]], [[opencivil.mauerwerk.knicken#Konstanten|AUSMITTE]] oder [[opencivil.mauerwerk.knicken#Konstanten|STABILITAET]].
- `grenzzustand: Optional[Zustand]` – Der letzte Zustand, der hielt – `None`, wenn schon keine Last hält.
- `bei_n_d: Optional[Zustand] = None`

### Querergebnis

```python
@dataclass(frozen=True)
class Querergebnis
```

Was die Suche nach der Querlast findet – siehe [[opencivil.mauerwerk.knicken#querlast|querlast]].

- `lam: float` – Die grösste Querlast als λ = q · h_w²/(t_w² · f_xd), null, wenn schon n allein nicht hält.
- `grund: str` – [[opencivil.mauerwerk.knicken#Konstanten|AUSMITTE]] oder [[opencivil.mauerwerk.knicken#Konstanten|STABILITAET]]: was über ihr nicht mehr hielt.
- `grenzzustand: Optional[Zustand]` – Der letzte Zustand, der hielt – `None`, wenn schon n allein nicht hält.

### _Wand

```python
class _Wand
```

Die Gleichungen einer Wand in Dicken: Höhe `ht`, Ränder unten und oben.

#### _Wand.ausmitten

```python
def ausmitten(self, w: Sequence[float], p_u: float, p_o: float, quer: float=0.0) -> List[float]
```

Je Knoten die Ausmitte – `quer` ist λ/(2 n), die Querlast (Dateikopf).

#### _Wand.loesen

```python
def loesen(self, n: float, start: Optional[Tuple[List[float], float, float]], quer: float=0.0) -> Optional[Tuple[List[float], float, float, int]]
```

Das Gleichgewicht unter n nach Newton, von `start` aus – ``(w, p_u,
p_o, Vorzeichen der Determinante)` oder `None``, wenn es keines findet.
`quer` wie bei [[opencivil.mauerwerk.knicken#_Wand.ausmitten|ausmitten]]: es hängt nicht an w, die Ableitung
bleibt dieselbe.

### k_N

```python
def k_N(ht: float, e_u: Optional[float], e_o: Optional[float], E_f: float=1000.0, n_d: Optional[float]=None) -> Knickergebnis
```

Der Beiwert k_N einer Wand von `ht` Dicken Höhe – Ausmitten `e_u` am
Fuss und `e_o` am Kopf in Dicken, `None` für einen eingespannten
Rand; `E_f` = E_xd/f_xd. Mit `n_d` auch der Zustand unter dieser
Last, wenn sie hält. Siehe Dateikopf.

### _k_N

```python
@lru_cache(maxsize=512)
def _k_N(ht: float, e_u: Optional[float], e_o: Optional[float], E_f: float, n_d: Optional[float]) -> Knickergebnis
```

Die Rechnung hinter [[opencivil.mauerwerk.knicken#k_N|k_N]], je Fall einmal: die Zeichnung fragt nach jeder Eingabe.

### querlast

```python
def querlast(ht: float, e_u: Optional[float], e_o: Optional[float], E_f: float, n: float, richtung: int) -> Querergebnis
```

Die grösste Querlast der Wand von `ht` Dicken Höhe unter der festen
Normalkraft `n` – Ausmitten und `E_f` wie bei [[opencivil.mauerwerk.knicken#k_N|k_N]],
`richtung` +1, wenn die Querlast zur Seite positiver Ausmitten drückt,
sonst −1. Siehe Dateikopf.

### _querlast

```python
@lru_cache(maxsize=512)
def _querlast(ht: float, e_u: Optional[float], e_o: Optional[float], E_f: float, n: float, richtung: int) -> Querergebnis
```

Die Rechnung hinter [[opencivil.mauerwerk.knicken#querlast|querlast]], je Fall einmal.


## Konstanten

- `TEILE = 40` – In so viele gleiche Stücke ist die Höhe geteilt.
- `PLATEAU = 0.375` – Die grösste Ausmitte in Teilen der Dicke: dort ist das Moment am Ende (Figur 3, Figur 4).
- `FORMELGRENZE = 0.6` – Bis zu dieser Ausmitte gilt die Formel der Figur 3 in der Rechnung – darüber bricht ein Schritt ab, statt dem Tangens nahe π/2 zu folgen.
- `SCHRITT = 0.02` – Der erste Schritt in n, und wie genau k_N am Ende ist.
- `GENAU = 2e-05`
- `QUER_SCHRITT = 0.1` – Der erste Schritt der Querlast und wie genau sie am Ende ist, beide in λ_1; weiter als bis zum Vielfachen [[opencivil.mauerwerk.knicken#Konstanten|QUER_HOECHSTENS]] sucht sie nicht.
- `QUER_GENAU = 0.0001`
- `QUER_HOECHSTENS = 20.0`
- `REFERENZ_FIGUR_3 = 'SIA 266:2015, 4.3.1.1, Figur 3'` – Wo die Regeln stehen.
- `REFERENZ_GRENZE = 'SIA 266:2015, 4.3.1.1, Gl. (6), Figur 4'`
- `REFERENZ_K_N = 'SIA 266:2015, 4.3.1.3, Gl. (11)'`
- `REFERENZ_GEWOELBE = 'SIA 266:2015, 4.3.4.2, Figur 11'`
- `DRUCK = 'druck'` – Was k_N begrenzt.
- `AUSMITTE = 'ausmitte'`
- `STABILITAET = 'stabilitaet'`

## Gebraucht von

- [[opencivil.mauerwerk.nachweise]]
- [[opencivil.mauerwerk.querlast]]
- [[opencivil.mauerwerk.schub]]
