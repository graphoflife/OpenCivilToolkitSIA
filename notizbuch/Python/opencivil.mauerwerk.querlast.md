---
erzeugt: 74705fecf09f
art: modul
tags: [modul]
---
> [!abstract] opencivil/mauerwerk/querlast.py
> eine Wand quer zu ihrer Ebene belastet, auch im Erdbeben.
> Paket [[opencivil.mauerwerk]] · [Quelltext](../../opencivil/mauerwerk/querlast.py)

## VERANTWORTUNG

Die Ersatzkraft des Erdbebens quer zur Wand ([[opencivil.mauerwerk.querlast#p_E|p_E]], SIA 261:2020,
16.7.2, Gl. (49)) samt ihrer Herleitung ([[opencivil.mauerwerk.querlast#erdbeben_schreiben|erdbeben_schreiben]]), was
zum Erdbeben am Mauerwerk zu sagen ist ([[opencivil.mauerwerk.querlast#erdbebenhinweise|erdbebenhinweise]], SIA
266:2015, 4.7.1.4 und 4.7.1.5), und je Pfeiler und Kombination zwei
Nachweise: die Querlast über die Druckgewölbe ([[opencivil.mauerwerk.querlast#Querlastnachweis|Querlastnachweis]],
4.3.4) und, wo das Gebäude mit q = 2.0 rechnet, das Normalkraftniveau nach
Gl. (27) ([[opencivil.mauerwerk.querlast#Normalkraftniveau|Normalkraftniveau]]).


## DIE ERSATZKRAFT

(Gl. (49))
Im Schwerpunkt der Wand wirkt quer zu ihr F_a, aus ihrem Eigengewicht G_a;
je m² Wand ist G_a das Eigengewicht g_k. Mit der Schwingzeit der Wand gleich
der des Gebäudes, T_a = T_1, ist die Klammer der Gl. (49) am grössten:
p_E = γ_f · a_gd · S · g_k / (g · q_a) · [3 · (1 + z_a/h) − 0.5] – nach
Vorgabe, nicht nachgeschlagen, die ungünstigste Annahme, auch für eine
tragende Wand (Benutzer, 2026-11-27). Die untere Grenze der Gl. (49) gilt
damit nie. q_a = 1.5 (16.7.3). p_E wirkt in beiden Richtungen.


## DIE QUERLAST (4.3.4)

Quer zur Wand trägt unbewehrtes Mauerwerk über Druckgewölbe (4.3.4.2,
Figur 11), mit der Druckfestigkeit nach 4.3.2.1 (4.3.4.4):

- lotrecht zwischen Kopf und Fuss mit der Normalkraft: die verformte Wand
  nach Theorie 2. Ordnung wie beim Knicken, die Querlast dazu
  ([[opencivil.mauerwerk.knicken#querlast|querlast]]). Gerechnet wird immer
  nach Theorie 2. Ordnung; Gl. (19) und (20) erlaubten sonst, sie zu
  vernachlässigen – so liegt die Rechnung auf der sicheren Seite.
- waagrecht zwischen den Rändern, wenn beide gehalten sind, die Wand keine
  Öffnung hat und die Stossfugen vollfugig sind (4.3.4.3): ein Bogen mit
  drei Gelenken, an jedem über t_w/2 mit f_yd gedrückt, also
  p_Rd,h = 2 · f_yd · t_w² / L². Effekte 2. Ordnung vernachlässigt er,
  darum nur, wo Gl. (19) und (20) mit L statt h_w gelten; w_d ist dabei die
  Durchbiegung des waagrechten Streifens, elastisch, ungerissen, mit E_xd.

Nach Vorgabe, nicht nachgeschlagen: die Normalkraft des lotrechten Gewölbes
ist die in halber Höhe, N_m = N_Ld + (N_xd − N_Ld)/2, über die ganze Höhe;
ein Pfeiler bekommt die Querlast bis zur Mitte der Öffnungen neben ihm,
am Ende der Wand bis zu diesem; es gilt das stärkere der beiden Gewölbe,
nicht ihre Summe.


## DAS NORMALKRAFTNIVEAU

(Gl. (27))
Rechnet das Gebäude mit q = 2.0, muss jede Wand N_xd/(l_w · t_w · f_xd) ≤
0.20 erfüllen (4.7.1.5) – in den Kombinationen mit diesem Erdbeben.


## EINHEITEN

SI-Basis; Querlasten in N/m².

## Inhalt

### klammer

```python
def klammer(z_a: float, h: float) -> float
```

Die Klammer der Gl. (49) mit T_a = T_1: 3 · (1 + z_a/h) − 0.5 – siehe Dateikopf.

### p_E

```python
def p_E(g_k: float, g: float, q: Querlast) -> float
```

Die Ersatzkraft des Erdbebens je m² Wand, in N/m² – `g_k` ihr
Eigengewicht je m² in N/m², `g` in m/s². Siehe Dateikopf.

### erdbeben_schreiben

```python
def erdbeben_schreiben(p: Protokoll, zw: Zwischenwerte, q: Querlast, g_k: Wert, g: Wert) -> None
```

Die Ersatzkraft einer Querlast aus dem Erdbeben, nach Gl. (49) hergeleitet.

### erdbebenhinweise

```python
def erdbebenhinweise(wand: Wand) -> List[Meldung]
```

Was zum Erdbeben am Mauerwerk zu sagen ist, grau, je Querlast des
Erdbebens: wo es ein erhöhtes Verformungsvermögen braucht – in
Bauwerksklasse III, in II in den Zonen Z3a und Z3b (4.7.1.4) –, und
dass q = 2.5 es durch Versuche nachweisen muss (4.7.2). Beides prüft
das Werkzeug nicht.

### _Richtung

```python
@dataclass(frozen=True)
class _Richtung
```

Eine Richtung, in der die Querlast wirkt: `p_d` mit Vorzeichen, und was die Wand trägt.

- `p_d: float`
- `lotrecht: knicken.Querergebnis`
- `p_Rd_v: float`
- `p_Rd_h: Optional[float]` – `None`, wo das waagrechte Gewölbe nicht trägt.

#### _Richtung.p_Rd

```python
@property
def p_Rd(self) -> float
```

#### _Richtung.grad

```python
@property
def grad(self) -> float
```

### einwirkungen

```python
def einwirkungen(a: Abtrag) -> List[float]
```

Die Querlasten der Kombination je Richtung, mit Vorzeichen: p ± p_E
mit dem Erdbeben, sonst p allein – leer ohne Querlast.

### einzugsbreite

```python
def einzugsbreite(befund: 'Wandbefund', pf: Pfeiler) -> Tuple[float, float]
```

Von wo bis wo ein Pfeiler Querlast bekommt, in m: bis zur Mitte der
Öffnungen neben ihm, am Ende der Wand bis zu diesem (Dateikopf).

### waagrechtes_gewoelbe

```python
def waagrechtes_gewoelbe(befund: 'Wandbefund') -> Optional[str]
```

Warum die Wand kein waagrechtes Gewölbe hat, als Satz – `None`, wenn
sie eines haben kann: ohne Öffnung, beide Ränder gehalten, vollfugig.
Gl. (19) und (20) prüft [[opencivil.mauerwerk.querlast#Querlastnachweis|Querlastnachweis]].

### Querlastnachweis

```python
class Querlastnachweis(Wandnachweis)
```

Die Querlast über die Druckgewölbe – siehe Dateikopf.

- `LANGNAME = 'Querlast'`
- `ART = 'Q'`
- `FELD = 'querlast'`

#### Querlastnachweis.ansatz

```python
def ansatz(self, p: Protokoll, befund: 'Wandbefund') -> None
```

#### Querlastnachweis.stelle

```python
def stelle(self, p: Protokoll, befund: 'Wandbefund', s: Stelle) -> Stellenausgang
```

#### Querlastnachweis._normalkraft

```python
@staticmethod
def _normalkraft(p: Protokoll, zw: Zwischenwerte, a: Abtrag, pf: Pfeiler) -> Wert
```

N_m: die Normalkraft in halber Höhe des Pfeilers – die des lotrechten Gewölbes.

#### Querlastnachweis._richtung

```python
@staticmethod
def _richtung(befund: 'Wandbefund', pf: Pfeiler, n: float, e_o: Optional[Wert], e_u: Optional[Wert], p_d: float, b_q: float, grund_h: Optional[str]) -> _Richtung
```

Was die Wand in der Richtung von `p_d` trägt – noch ohne Herleitung.

#### Querlastnachweis._beide

```python
@staticmethod
def _beide(p: Protokoll, zw: Zwischenwerte, a: Abtrag, richtungen: List[_Richtung], r: _Richtung) -> None
```

Mit dem Erdbeben: beide Richtungen in einem Satz, die massgebende zuerst.

#### Querlastnachweis._lotrecht

```python
@staticmethod
def _lotrecht(p: Protokoll, zw: Zwischenwerte, r: _Richtung, N_m: Wert, h: float, t: float) -> Wert
```

Das lotrechte Gewölbe: was die Rechnung nach Theorie 2. Ordnung fand.

#### Querlastnachweis._waagrecht

```python
@staticmethod
def _waagrecht(p: Protokoll, zw: Zwischenwerte, befund: 'Wandbefund', pf: Pfeiler, r: _Richtung, p_d: Wert) -> Optional[Wert]
```

Das waagrechte Gewölbe einer Wand ohne Öffnung zwischen gehaltenen
Rändern: Gl. (19) und (20) mit L, dann sein Widerstand – `None`,
wo eine der beiden nicht gilt.

### _gewoelbe_haelt

```python
def _gewoelbe_haelt(befund: 'Wandbefund', L: float, p_d: float) -> bool
```

Ob Gl. (19) und (20) mit der Spannweite `L` statt h_w gelten – siehe Dateikopf.

### _durchbiegung

```python
def _durchbiegung(befund: 'Wandbefund', L: float, p_d: float) -> float
```

w_d des waagrechten Streifens, elastisch, ungerissen, mit E_xd: 5 p L⁴ / (384 E t³/12).

### _seite

```python
def _seite(p_d: float) -> str
```

Wohin eine Querlast drückt, in Worten.

### _wo

```python
def _wo(hoehe: float, h: float) -> str
```

Wo in der Wand – `hoehe` als Anteil ab dem Fuss.

### Normalkraftniveau

```python
class Normalkraftniveau(Wandnachweis)
```

Gl. (27), wo das Gebäude mit q = 2.0 rechnet – siehe Dateikopf.

- `LANGNAME = 'Normalkraftniveau'`
- `ART = 'n'`
- `FELD = 'normalkraftniveau'`

#### Normalkraftniveau.ansatz

```python
def ansatz(self, p: Protokoll, befund: 'Wandbefund') -> None
```

#### Normalkraftniveau.stelle

```python
def stelle(self, p: Protokoll, befund: 'Wandbefund', s: Stelle) -> Stellenausgang
```


## Konstanten

- `REFERENZ_GL_49 = 'SIA 261:2020, 16.7.2, Gl. (49)'` – Wo die Regeln stehen.
- `REFERENZ_Q_A = 'SIA 261:2020, 16.7.3'`
- `REFERENZ_GL_19 = 'SIA 266:2015, 4.3.4.1, Gl. (19)'`
- `REFERENZ_GL_20 = 'SIA 266:2015, 4.3.4.1, Gl. (20)'`
- `REFERENZ_VOLLFUGIG = 'SIA 266:2015, 4.3.4.3'`
- `REFERENZ_GL_27 = 'SIA 266:2015, 4.7.1.5, Gl. (27)'`
- `REFERENZ_VERFORMUNG = 'SIA 266:2015, 4.7.1.4'`
- `Q_A = 1.5` – Der Verhaltensbeiwert einer Wand als sekundäres Bauteil (16.7.3).
- `SCHLANKHEIT = 15.0` – Wie schlank das waagrechte Gewölbe höchstens ist, und wie weit es sich biegt – Gl. (19), (20).
- `DURCHBIEGUNG = 0.002`
- `NIVEAU = 0.2` – Wie stark ein Pfeiler höchstens gedrückt ist, wenn das Gebäude mit q = 2.0 rechnet – Gl. (27).

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.sprache]]
- [[opencivil.core.wert]]
- [[opencivil.erdbeben.ersatzkraft]]
- [[opencivil.mauerwerk.knicken]]
- [[opencivil.mauerwerk.lasten]]
- [[opencivil.mauerwerk.modell]]
- [[opencivil.mauerwerk.nachweise]]
- [[opencivil.mauerwerk.werk]]
- [[opencivil.stabwerk.system]]

## Gebraucht von

- [[opencivil.mauerwerk.herleitung]]
- [[opencivil.mauerwerk.werk]]
- [[opencivil.projekt.aufbau.mauerwerk]]

## Formeln aus diesem Modul

- [[Ausmitte einer Wand unter Querlast]] · `Querlastnachweis.ansatz`
- [[Durchbiegung einer Wand als waagrechter Streifen]] · `Querlastnachweis._waagrecht`
- [[Ersatzkraft des Erdbebens quer zu einer Wand]] · `erdbeben_schreiben`
- [[Normalkraft eines Pfeilers in halber Höhe]] · `Querlastnachweis._normalkraft`
- [[Normalkraftniveau eines Pfeilers]] · `Normalkraftniveau.stelle`
- [[Querlastwiderstand einer Wand aus Mauerwerk]] · `Querlastnachweis.stelle`
- [[Widerstand des waagrechten Druckgewölbes einer Wand]] · `Querlastnachweis._waagrecht`
