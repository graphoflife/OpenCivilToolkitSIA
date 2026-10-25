---
erzeugt: bb777b7668ce
art: modul
tags: [modul]
---
> [!abstract] opencivil/spannungsanalyse/schnitt.py
> das Paar eines gezeichneten Querschnitts.
> Paket [[opencivil.spannungsanalyse]] · [Quelltext](../../opencivil/spannungsanalyse/schnitt.py)

## VERANTWORTUNG

Wie ein gezeichneter Querschnitt zu den sechs Fragen kommt: das Loeserpaar
je Zugseite ([[opencivil.spannungsanalyse.schnitt#Schnittpaar|Schnittpaar]], ein
[[opencivil.spannungsanalyse.linie#Paar|Paar]]), seine Ebenen mit kippender
Nulllinie ([[opencivil.spannungsanalyse.schnitt#KippendeNulllinie|KippendeNulllinie]]) und was seine Herleitung anders
schreibt als die Platte. Bis 2026-10-17 stand es in
`opencivil/querschnitt/schnittanalyse.py` -- im Querschnitt, aber auf der
Analyse gebaut, die es ihrerseits erst in einer Funktion laden konnte.


## JE ZUGSEITE

Eine Analyse waehlt die Seite, die ein positives Moment zieht: unten, oben,
links oder rechts ([[opencivil.querschnitt.zugseite#Zugseite|Zugseite]]). Das
Moment wirkt um die Achse der Biegung, um die andere wirkt keines: reine
Biegung. Ein unsymmetrischer Querschnitt kippt dafuer seine Nulllinie, und
jede Ebene der Analyse sucht ihre Neigung ([[opencivil.spannungsanalyse.schnitt#KippendeNulllinie|KippendeNulllinie]]), wie
die Gebrauchsnachweise es tun -- so hat es der Benutzer am 2026-10-17
entschieden. Bis dahin blieb die Nulllinie parallel zur Achse, und das Moment
um die andere Achse, das ein L dabei weckte, zaehlte nicht: an einem L mit
Steg 200×800 und Flansch 600×200 hiess das ein Rissmoment von 132 statt
64 kNm. «Einachsig» bleibt es so, wie in der Tragsicherheit
([[opencivil.spannungsanalyse.linie#FesteNulllinie|FesteNulllinie]]); die Platte
rechnet immer so.

`eps_m` ist die Dehnung im Schwerpunkt des Bruttoquerschnitts, und die
Momente beziehen sich auf ihn, wie in den Lastfaellen. «Oben» heisst der
Rand gegenueber der Zugseite, «unten» der auf ihr: bei Zug links ist oben
der rechte Rand. Kippt die Nulllinie, gelten oben und unten senkrecht zu ihr.


## WOMIT GERECHNET WIRD

Je Analyse eine Rechenwahl wie bei der Platte -- Kriechzahl, Wertesatz,
Rechenart --, fuer jeden Werkstoff des Querschnitts dieselbe. Die
Werkstoffwahl der Tragsicherheit gilt hier nicht. Staebe in derselben Tiefe,
aus demselben Stahl, werden zu einer Lage: sie haben dieselbe Dehnung.
Zerlegt wird in so viele Streifen wie die Platte in Fasern
([[opencivil.querschnitt.fasern#Konstanten|FASERN]]), dazu die Grenzen an jeder
Ecke: eine Linie rechnet viele Ebenen, und mit den 200 Streifen der
Tragsicherheit dauerte sie dreimal so lang -- fuer ein M_Rd, das sich um
zwei Zehntelpromille aendert.


## DER RISS

Am ungerissenen Bruttoquerschnitt, ohne Stahl, wie beim sproeden Versagen
([[opencivil.nachweis.rissgroessen]]):

```python
M_Riss(N) = (f_ct,eff - N/A) · W        W zur Ecke, die unter reiner Biegung zuerst reisst
N_Riss(M) = (f_ct,eff,t - σ_M) · A      σ_M aus M, an der Ecke, die zuerst reisst
```

Unter reiner Biegung mit dem Deviationsmoment `I_yz`, «einachsig» mit
`W = I/v`. `f_ct,eff` mit `k_t` fuer ein Drittel der Tiefe, unter Zug
fuer die rissaktive Dicke `min(h; b)` -- die Regeln der Platte,
uebertragen; der Beton der Ecke gibt `f_ctm`. Nach Vorgabe, nicht
nachgeschlagen (`notizbuch/Notizen/TODO.md`). Bei der Platte ist
`W/A = h/6` -- dieselbe Formel.


## DER AEQUIVALENTE MODUL

Bezogen auf den Bruttoquerschnitt: `I` um die Achse der Biegung bzw.
`A`. Kippt die Nulllinie, kippt sie auch beim reinen Betonquerschnitt,
mit dem der Modul sich vergleicht: unter reiner Biegung kruemmt er sich wie
einer mit `I_y - I_yz²/I_z` (um y). Sonst zeigte ein ungerissener L schon
seiner Form wegen weniger als `E_c,eff` -- am L oben 0.79·E_cm statt 1.07.
So vom Benutzer bestaetigt am 2026-10-17. Bei der Platte sind es `b·h³/12`
und `b·h`.


## EINHEITEN

SI-Basis wie im ganzen Querschnittsmodul.

## Inhalt

### _betonspannung

```python
def _betonspannung(r, gesetze: Mapping[int, Callable[[float], float]]) -> Callable[[float, float], float]
```

Die Spannung des Betons an einer Stelle, fuer das Bild: in jedem Streifen
der Beton mit der groessten Breite dort. Liegen zwei Betone in derselben
Tiefe, zeigt das Bild den, der dort ueberwiegt.

### _loeser

```python
def _loeser(q: Querschnitt, psi: float, herkunft: Sequence[Bewehrungselement], staehle: Mapping[int, Stahlgesetz], namen: Mapping[int, str], *, suche: Suche) -> Faserloeser
```

Der Querschnitt in der Zugrichtung `psi` als [[opencivil.nachweis.querschnittsloeser#Faserloeser|Faserloeser]].
Staebe in derselben Tiefe, aus demselben Stahl und im selben Beton werden
eine Lage -- sie haben dieselbe Dehnung, und das Bild zeigt sie als eine.
Ihr Arm entlang der Nulllinie ist der Schwerpunkt ihrer Flaechen: mit ihm
stimmt das Moment um die andere Achse, nach dem die kippende Nulllinie
sucht. Bis 2026-10-17 fiel er weg, und die Suche fand an einem L Ebenen
mit einem Moment um die andere Achse. `suche` sagt, wie der Loeser
sucht ([[opencivil.spannungsanalyse.schnitt#_Zerlegung.in_richtung|_Zerlegung.in_richtung]]).

### _Zerlegung

```python
@dataclass(frozen=True)
class _Zerlegung
```

Ein Zustand des gezeichneten Querschnitts -- in jeder Zugrichtung zu haben.

- `querschnitt: Querschnitt`
- `herkunft: Tuple[Bewehrungselement, ...]` – Je Bewehrung das Element, aus dem sie stammt -- fuer die Namen der Lagen.
- `staehle: Mapping[int, Stahlgesetz]`
- `namen: Mapping[int, str]`

#### _Zerlegung.in_richtung

```python
def in_richtung(self, psi: float, *, suche: Suche=SUCHE_DER_ANALYSEN) -> FesteNulllinie
```

Der Zustand in der Zugrichtung `psi`, mit fester Nulllinie --
gesucht wie in allen Analysen. Nur die gekippten Richtungen der
kippenden Nulllinie suchen je Frage frisch ([[opencivil.spannungsanalyse.schnitt#Konstanten|_JE_FRAGE]]).

### KippendeNulllinie

```python
class KippendeNulllinie
```

Die Ebenen eines Zustands des gezeichneten Querschnitts unter reiner
Biegung: die Nulllinie kippt, bis kein Moment um die andere Achse bleibt.

Bei einer Neigung ϑ gegen die Zugseite ist es die Aufgabe einer festen
Richtung ([[opencivil.spannungsanalyse.linie#FesteNulllinie|FesteNulllinie]]): die
Ebene traegt dort den Anteil `M·cos ϑ` des Moments, das zu ihr gehoert,
bzw. ihre Kruemmung hat senkrecht zur Achse der Biegung den verlangten
Anteil. Uebrig bleibt das Moment um die andere Achse, und gedreht wird,
bis es null ist -- mit der Suche der Gebrauchsnachweise
([[opencivil.nachweis.gebrauchsebene#neigung_suchen|neigung_suchen]]), von der
Neigung aus, die zuletzt gefunden wurde: die Ebenen einer Linie folgen
sich in kleinen Schritten. Findet sie von dort nichts, sucht sie noch
einmal bei der Zugseite selbst: die Ebene ohne Moment, mit der eine Linie
unter Druck beginnt, kippt an einem L um +29°, ihre gebogenen Ebenen um
-48° -- zu weit fuer eine Suche, die hoechstens 90° nach jeder Seite
geht. Bei einem symmetrischen Querschnitt trifft schon die Zugseite, und
es bleibt bei der Ebene, die die feste Nulllinie faende.

Gesucht wird in jeder gekippten Richtung mit Illinois ([[opencivil.spannungsanalyse.schnitt#Konstanten|_JE_FRAGE]]),
wie unter Gebrauchslast: halbiert kostete eine Linie am L des Dateikopfs
viermal so lang. Ihre Loeser entstehen je Frage frisch, ohne Gedaechtnis
-- so haengt keine Ebene an der Reihenfolge der Fragen, und Illinois darf
auch beim Spannungsblock suchen: halbiert brauchte die N-ε-Linie des
Kastentraegers im Pruefprojekt damit 9 s. Die Zugseite selbst sucht wie
der Loeser des Paars -- so bleibt ein symmetrischer Querschnitt genau bei
der Ebene der festen Nulllinie.

Was am Moment um die andere Achse fehlt, misst jede Frage selbst: zu
einer Kruemmung das Moment selbst; wo die gekippte Ebene `M·cos ϑ`
traegt -- zu N und M, zu einer Dehnung --, dasselbe geteilt durch
`cos ϑ`, `M·sin ϑ + M_quer,ϑ` ([[opencivil.spannungsanalyse.schnitt#_rest_beim_moment|_rest_beim_moment]]). Sonst waere
bei 90° alles null, das Moment um die andere Achse mit, ohne dass die
Ebene reine Biegung waere. Ohne Moment aber ist 90° eine Loesung: unter
Druck kruemmt sich der Unterzug des Beispiels, oben breiter als unten, nur
senkrecht -- bei Zug links um 90° gekippt. Jenseits von 90° laege die
Gegenrichtung.

Jede Antwort bleibt gemerkt. Eine Linie fragt dieselbe Stelle mehrmals --
ihr Ende beim Suchen, fuer den Bruch, fuer das Fliessen --, und von einer
anderen Neigung aus faende die Suche am Rand des Gleichgewichts keine
Ebene mehr: dort gibt es sie nur bei genau einer Neigung. Am L des
Dateikopfs fehlte so der Fliessbeginn.

Was die Suche zu N und M findet, ohne das Moment um die andere Achse zu
treffen -- an einem Sprung des Spannungsblocks --, ist verfehlt
([[opencivil.spannungsanalyse.linie#Dehnungsebene|verfehlt]]). Zu
einer Kruemmung oder einer Dehnung gibt es dann keine Ebene: dort laeuft
eine Linie ueber die Verformung, und eine verfehlte Ebene truege sie ueber
ihr Ende hinaus.

#### KippendeNulllinie._gekippt

```python
def _gekippt(self, aufgabe: Callable[[FesteNulllinie, float], Optional[Dehnungsebene]], rest: Callable[[Dehnungsebene], float]) -> Optional[Dehnungsebene]
```

Die Ebene ohne Moment um die andere Achse. `aufgabe(fest, ϑ)` loest
die Aufgabe in der Richtung, die um ϑ gegen die Zugseite gekippt ist;
`rest(ebene)` sagt, was ihr am Moment um die andere Achse noch fehlt.

#### KippendeNulllinie._gemerkt

```python
def _gemerkt(self, frage: Tuple[str, float, float], aufgabe: Callable[[FesteNulllinie, float], Optional[Dehnungsebene]], rest: Callable[[Dehnungsebene], float]) -> Optional[Dehnungsebene]
```

Die Antwort auf `frage` -- gesucht beim ersten Mal, danach gemerkt.

#### KippendeNulllinie.zu_kraeften

```python
def zu_kraeften(self, N: float, M: float) -> Optional[Dehnungsebene]
```

#### KippendeNulllinie.zur_kruemmung

```python
def zur_kruemmung(self, chi: float, N: float) -> Optional[Dehnungsebene]
```

#### KippendeNulllinie.zur_dehnung

```python
def zur_dehnung(self, eps_m: float, M: float) -> Optional[Dehnungsebene]
```

### _rest_beim_moment

```python
def _rest_beim_moment(M: float) -> Callable[[Dehnungsebene], float]
```

Was einer gekippten Ebene am Moment um die andere Achse fehlt, wenn sie in
ihrer Richtung `M·cos ϑ` traegt: `M·sin ϑ + M_quer,ϑ`, das Moment um
die andere Achse geteilt durch `cos ϑ` -- ohne die Null, die der Faktor
bei 90° braechte.

### _getroffen

```python
def _getroffen(ebene: Optional[Dehnungsebene]) -> Optional[Dehnungsebene]
```

Die Ebene, wenn sie das Moment um die andere Achse trifft -- sonst keine.

### _massstab

```python
def _massstab(ebene: Dehnungsebene) -> float
```

Woran das Moment um die andere Achse gemessen wird: das groessere von M
und N mit einem Hebel von einem Meter, wie unter Gebrauchslast -- so gilt
eine Schranke fuer jede Stelle einer Linie.

### Schnittpaar

```python
@dataclass(frozen=True)
class Schnittpaar
```

Die beiden Loeser eines gezeichneten Querschnitts in einer Zugrichtung --
gerissen und ungerissen, wie das [[opencivil.spannungsanalyse.platte#Loeserpaar|Loeserpaar]]
der Platte --, dazu beide Zustaende in jeder anderen Richtung, fuer die
kippende Nulllinie. Dazu der Riss am Bruttoquerschnitt und was die
Herleitung braucht.

- `gerissen: Faserloeser`
- `ungerissen: Faserloeser`
- `seite: Zugseite`
- `wahl: Rechenwahl`
- `querschnitt: Querschnitt` – Der gerissene Querschnitt im Bruchzustand -- derselbe, aus dem `gerissen` stammt.
- `zerlegungen: Tuple[_Zerlegung, _Zerlegung]` – Gerissen und ungerissen, in jeder Richtung -- fuer die kippende Nulllinie.
- `A: float` – Flaeche des Bruttoquerschnitts, m².
- `I: float` – Traegheitsmoment um die Achse der Biegung, m⁴.
- `brutto: Bruttoquerschnitt`
- `riss: Rissmoment` – Das Rissmoment unter reiner Biegung, ohne Normalkraft -- und die Ecke, die zuerst reisst.
- `k_t_zug: float` – Fuer die Rissnormalkraft: `k_t` fuer die rissaktive Dicke unter Zug, die kleinere Abmessung `min(h; b)` (Benutzer, 2026-10-17). Bis dahin die ganze Tiefe in Zugrichtung, auch wo der Querschnitt quer dazu schmaler ist.
- `breite: float` – Die Ausdehnung des Betons quer zur Zugrichtung, m.
- `t_zug: float` – Die rissaktive Dicke unter Zug, `min(h; b)`, m.
- `E_cm: float` – Der Modul des Betons der Ecke, die zuerst reisst -- Massstab des aequivalenten Moduls.
- `staehle: Tuple[Baustoff, ...] = ()`
- `ids: Mapping[str, str] = field(default_factory=dict)` – Kurzname -> Wert-ID der Eingaben, fuer die Herleitung: der Beton der Ecke, die zuerst reisst, und A, I -- dazu die Zugfestigkeit jedes Betons unter ihrer eigenen ID, denn welche Ecke unter Zug zuerst reisst, haengt am Moment.
- `bezugsort = 'im Schwerpunkt'` – Wo die Mitteldehnung gilt -- dort greift N an.

#### Schnittpaar.einachsig

```python
@property
def einachsig(self) -> bool
```

Ob die Nulllinie parallel zur Achse der Biegung bleibt, statt zu kippen -- wie die Analyse.

#### Schnittpaar.ebenen

```python
def ebenen(self) -> Zustaende
```

Die Ebenen beider Zustaende: kippend, «einachsig» mit fester Nulllinie.

#### Schnittpaar.W

```python
@property
def W(self) -> float
```

Das Widerstandsmoment zur Ecke, die unter reiner Biegung zuerst reisst, m³.

#### Schnittpaar.M_Riss

```python
@property
def M_Riss(self) -> float
```

Das Rissmoment ohne Normalkraft.

#### Schnittpaar.rissmoment_bei

```python
def rissmoment_bei(self, N: float) -> float
```

`M_Riss(N) = (f_ct,eff - N/A)·W` -- Druck hebt es, Zug senkt es.

#### Schnittpaar.rissnormalkraft

```python
def rissnormalkraft(self, M: float) -> Rissnormalkraft
```

Die Rissnormalkraft beim Moment `M` -- an der Ecke, die zuerst reisst.

#### Schnittpaar.rissnormalkraft_bei

```python
def rissnormalkraft_bei(self, M: float) -> float
```

`N_Riss(M) = (f_ct,eff,t - σ_M)·A` -- ein Moment senkt sie, gleich in welche Richtung.

#### Schnittpaar.I_c

```python
@property
def I_c(self) -> float
```

Der reine Betonquerschnitt fuer den aequivalenten Modul: `I` -- kippt
die Nulllinie, `I - I_yz²/I_quer`, siehe Dateikopf.

#### Schnittpaar.A_c

```python
@property
def A_c(self) -> float
```

#### Schnittpaar.tiefe

```python
def tiefe(self, w: Zwischenwerte, ein: Callable[[str], 'Wert']) -> 'Wert'
```

Die Ausdehnung des Betons in Zugrichtung -- aus der Zeichnung, kein Wert des Rechenwerks.

#### Schnittpaar.herleitung_riss

```python
def herleitung_riss(self, p: Protokoll, w: Zwischenwerte, linie: Linie, ein: Callable[[str], 'Wert'], h: 'Wert') -> None
```

Der Riss am Bruttoquerschnitt: Widerstandsmoment, Zugfestigkeit, Risskraft.

#### Schnittpaar.herleitung_dehnung_am_ende

```python
def herleitung_dehnung_am_ende(self, p: Protokoll, w: Zwischenwerte, bruch: Grenzzustand, oben: 'Wert', unten: 'Wert', h: 'Wert') -> None
```

Die Dehnung im Schwerpunkt am Ende -- dort greift N an; `h` senkrecht zur Nulllinie.

#### Schnittpaar.herleitung_bezug

```python
def herleitung_bezug(self, p: Protokoll, w: Zwischenwerte, momente: bool, ein: Callable[[str], 'Wert'], h: 'Wert') -> 'Wert'
```

Der reine Betonquerschnitt des aequivalenten Moduls: der Bruttoquerschnitt.

### schnittpaar

```python
def schnittpaar(analyse: Querschnittsanalyse, seite: Zugseite, wert: Callable[[str], float], wahl: Rechenwahl) -> Optional[Schnittpaar]
```

Das Loeserpaar eines gezeichneten Querschnitts in einer Zugrichtung --
`None` ohne Bewehrung. `wert` liefert zu einer Wert-ID die Zahl in SI,
aus einer Loesung.


## Konstanten

- `_JE_FRAGE = Illinois(auch_bei_sprung=True)` – Wie eine gekippte Richtung sucht: mit Illinois, auch beim Spannungsblock -- ihr Loeser lebt fuer eine Frage, ein Gedaechtnis ueber Fragen hinweg hat er nicht.
- `KIPPGRENZE = 1e-06` – Unter diesem `cos ϑ` gibt es zu einer Kruemmung keine Neigung mehr: die gekippte Ebene braeuchte `chi/cos ϑ`.

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.suche]]
- [[opencivil.core.wert]]
- [[opencivil.material.basis]]
- [[opencivil.nachweis.gebrauchsebene]]
- [[opencivil.nachweis.querschnittsloeser]]
- [[opencivil.nachweis.rissgroessen]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.bewehrungselemente]]
- [[opencivil.querschnitt.fasern]]
- [[opencivil.querschnitt.gesetzwahl]]
- [[opencivil.querschnitt.interaktion]]
- [[opencivil.querschnitt.werkstoffgesetz]]
- [[opencivil.querschnitt.zugseite]]
- [[opencivil.spannungsanalyse.art]]
- [[opencivil.spannungsanalyse.linie]]

## Gebraucht von

- [[opencivil.spannungsanalyse]]
- [[opencivil.spannungsanalyse.analysen]]
- [[opencivil.spannungsanalyse.modul]]

## Formeln aus diesem Modul

- [[Grösste Dehnung im Schwerpunkt]] · `Schnittpaar.herleitung_dehnung_am_ende`
- [[Rissaktive Dicke des gezeichneten Querschnitts]] · `Schnittpaar.herleitung_riss`
- [[Rissmoment bei der Normalkraft]] · `Schnittpaar.herleitung_riss`
- [[Rissnormalkraft beim Moment]] · `Schnittpaar.herleitung_riss`
- [[Spannung aus dem Moment an der Ecke, die zuerst reisst]] · `Schnittpaar.herleitung_riss`
- [[Widerstandsmoment zum gezogenen Rand]] · `Schnittpaar.herleitung_riss`
