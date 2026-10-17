---
erzeugt: 9bea252bb346
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/qa_gebrauch.py
> Gebrauchsnachweise des gezeichneten Querschnitts.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/qa_gebrauch.py)

## VERANTWORTUNG

Was die Platte unter Gebrauchslast nachweist, am gezeichneten Querschnitt:

* die Stahlspannung -- unter quasi-staendiger Einwirkung aus der Rissbreite
  begrenzt, unter haeufiger gegen das Fliessen: derselbe Nachweis wie bei
  der Platte ([[opencivil.nachweis.spannungsbegrenzung#Spannungsbegrenzung|Spannungsbegrenzung]]),
  hier mit den Staeben als Stellen ([[opencivil.nachweis.qa_gebrauch#AnalyseStellen|AnalyseStellen]]);
* die Zwaengung auf Normalkraft, am ganzen Querschnitt
  ([[opencivil.nachweis.qa_gebrauch#RissnormalkraftQA|RissnormalkraftQA]]), und auf Biegung, je Richtung
  ([[opencivil.nachweis.qa_gebrauch#ZwaengungBiegungQA|ZwaengungBiegungQA]]).

Die Grenzen sind die der Platte, aus denselben Funktionen
([[opencivil.nachweis.mindestbewehrung#zulaessige_stahlspannung|zulaessige_stahlspannung]],
`f_yd - 80 N/mm²`), und die Woerter, unter denen die Stahlspannungen
erscheinen, aus denselben Grenzen ([[opencivil.nachweis.spannungsbegrenzung|spannungsbegrenzung]]).
Anders ist, woran sie gemessen werden.


## JE STAB

Die Platte haelt je Lage den dicksten Stab gegen die Rissbreite. Hier haelt
jeder gezogene Stab gegen seine eigene Grenze, und massgebend ist der
kleinste Erfuellungsgrad (Benutzer, 2026-10-15) -- wie ein Stab zu seiner
Grenze kommt, steht in [[opencivil.nachweis.stabgrenzen]], wie die Ebene
unter Gebrauchslast gefunden wird, in [[opencivil.nachweis.gebrauchsebene]].


## ZWAENGUNG AUF NORMALKRAFT

Es reisst der ganze Querschnitt, und die Bewehrung muss aufnehmen, was der
Beton dabei abgibt (Benutzer, 2026-10-15):

```
t        = min(b; h)                  kleinere Abmessung des Betons,
                                      wahlweise hoechstens 500 mm
k_t      = 1 / (1 + 0.5 · t)
N_Riss   = Σ A_c · k_t · f_ctm        je Beton
N_s,adm  = Σ A_s,i · sigma_s,adm,i   >=  N_Riss
```

Bei der Platte nimmt jede Lage die Haelfte -- zusammen derselbe Gedanke.


## ZWAENGUNG AUF BIEGUNG

Je Richtung wie das sproede Versagen: dasselbe Rissmoment
([[opencivil.nachweis.rissgroessen#rissmoment|rissmoment]]), gehalten gegen
das Moment, bei dem der erste gezogene Stab sein `sigma_s,adm` erreicht --
am gerissenen Querschnitt, elastisch, ohne Normalkraft, mit eigenem φ
(Benutzer, 2026-10-15). Die Platte rechnet dasselbe von Hand, mit dem
Hebelarm `d - x/3` und ohne die gedrueckte Bewehrung; hier wirkt sie mit.


## NACH VORGABE, NICHT NACHGESCHLAGEN

Der ganze Querschnitt bei der Normalkraft, `t` als kleinere Abmessung, die
Grenze je Stab, der fiktive Durchmesser und das Moment am elastisch
gerissenen Querschnitt. Siehe `notizbuch/Notizen/TODO.md`.


## EINHEITEN

SI-Basis wie im ganzen Querschnittsmodul; die Zeichnung in mm.

## Inhalt

### _Analysezustand

```python
@dataclass(frozen=True)
class _Analysezustand(Stahlzustand)
```

Dazu der Querschnitt nach der Wahl und je Stab seine Angaben.

- `querschnitt: Querschnitt`
- `staebe: Tuple[Stabangabe, ...]`

### AnalyseStellen

```python
class AnalyseStellen(Stahlspannungsort)
```

Der gezeichnete Querschnitt fuer die Stahlspannung
([[opencivil.nachweis.spannungsbegrenzung#Spannungsbegrenzung|Spannungsbegrenzung]]):
Stellen sind seine Staebe, und jeder gezogene haelt gegen seine eigene
Grenze (siehe Dateikopf). Die Ebene eines Lastfalls traegt N, M_y und M_z
mit gedrehter Nulllinie ([[opencivil.nachweis.gebrauchsebene#gebrauchsebene|gebrauchsebene]]);
«einachsig» bleibt sie waagrecht.

- `messung = 'Gerechnet wird am gerissenen Querschnitt: der Beton nimmt keinen Zug…`
- `regel_der_rissbreite = GRENZE_JE_STAB`

#### AnalyseStellen.basis

```python
def basis(self, grenze: Type[Spannungsgrenze]) -> str
```

#### AnalyseStellen.bezuege

```python
def bezuege(self, wahl: Rechenwahl) -> List[Eingabebezug]
```

#### AnalyseStellen.zustand

```python
def zustand(self, e: Eingaben, wahl: Rechenwahl) -> _Analysezustand
```

#### AnalyseStellen.aus_rissbreite

```python
def aus_rissbreite(self, zustand: _Analysezustand, e: Eingaben, p: Protokoll, anforderung: Rissanforderung, basis: str) -> Grenzen
```

#### AnalyseStellen.ebene

```python
def ebene(self, zustand: _Analysezustand, fall: Lastfall) -> Gebrauchsebene
```

#### AnalyseStellen.keine_ebene

```python
def keine_ebene(self, fall: Lastfall) -> str
```

#### AnalyseStellen.begruendung

```python
def begruendung(self, zustand: _Analysezustand, erg: Fallergebnis) -> str
```

#### AnalyseStellen.dehnungsgrenze

```python
def dehnungsgrenze(self, basis: str, werte: Zwischenwerte, erg: Fallergebnis) -> Wert
```

#### AnalyseStellen.protokoll_gesetze

```python
def protokoll_gesetze(self, p: Protokoll, e: Eingaben, zustand: _Analysezustand, wahl: Rechenwahl, basis: str) -> None
```

#### AnalyseStellen.protokoll_verfahren

```python
def protokoll_verfahren(self, p: Protokoll, zustand: _Analysezustand, wahl: Rechenwahl) -> None
```

#### AnalyseStellen.protokoll_einwirkung

```python
def protokoll_einwirkung(self, p: Protokoll, fall: Lastfall, index: str) -> None
```

#### AnalyseStellen.protokoll_ebene

```python
def protokoll_ebene(self, p: Protokoll, werte: Zwischenwerte, zustand: _Analysezustand, grenzen: Grenzen, erg: Fallergebnis) -> None
```

### _tabelle_gezogen

```python
def _tabelle_gezogen(p: Protokoll, staebe: Sequence[Stabangabe], grenzen: Grenzen, ebene: Gebrauchsebene) -> None
```

Je Element mit gezogenen Staeben der unguenstigste: Dehnung, Spannung,
Grenze -- bei einer verschmierten Linie das Stueck, das seiner Grenze
am naechsten kommt.

### betonflaechen

```python
def betonflaechen(analyse: Querschnittsanalyse) -> List[Tuple[Baustoff, float]]
```

Die Flaeche jedes Betons, in m² -- ein Polygon zaehlt fuer seinen Beton
und wird dem abgezogen, in dem es liegt, wie in der Interaktion.

### RissnormalkraftQA

```python
class RissnormalkraftQA(Nachweis)
```

Der ganze Querschnitt reisst: seine Risskraft gegen alle Staebe zusammen.

- `THEMA = 'Zwängung auf Normalkraft'`
- `LANGNAME = 'Risse: Zwängung Normalkraft'`

#### RissnormalkraftQA.pruefe

```python
def pruefe(self, e: Eingaben, p: Protokoll)
```

#### RissnormalkraftQA._risskraft

```python
def _risskraft(self, p: Protokoll, e: Eingaben, werte: Zwischenwerte) -> Wert
```

Rissaktive Dicke, wirksame Zugfestigkeit je Beton und die Risskraft.

### ZwaengungBiegungQA

```python
class ZwaengungBiegungQA(Biegezwang)
```

Je Richtung das Rissmoment gegen das Moment, bei dem der erste gezogene
Stab sein `sigma_s,adm` erreicht.

#### ZwaengungBiegungQA.pruefe

```python
def pruefe(self, e: Eingaben, p: Protokoll)
```

#### ZwaengungBiegungQA._an_der_grenze

```python
def _an_der_grenze(self, q: Querschnitt, staebe: Sequence[Stabangabe], grenzen: Grenzen, M_y: float, M_z: float, M_start: float) -> Optional[Tuple[float, Gebrauchsebene, int]]
```

Das Moment ohne Normalkraft, bei dem der erste gezogene Stab seine
Grenze erreicht -- samt Ebene und Stab. `None`, wo auf der gezogenen
Seite des Schwerpunkts kein Stab liegt.

Bleibt alles linear, ist es ein Dreisatz: die Spannungen wachsen mit
dem Moment. Gerechnet wird darum bei `M_start` und beim
gedreisatzten Moment; stimmt es dort nicht, weil der Beton ueber
`f_ck` kommt, sucht Illinois weiter. Eine Ebene, die sich nicht
findet, liegt jenseits der Grenze: der Stahl fliesst dort laengst.


## Konstanten

- `GRENZ_SCHRANKE = 1e-07` – Wann das Moment der Zwaengung auf Biegung gefunden ist: wie nahe der erste gezogene Stab seiner Grenze kommen muss, als Teil von ihr.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.material.basis]]
- [[opencivil.nachweis.gebrauchsebene]]
- [[opencivil.nachweis.mindestbewehrung]]
- [[opencivil.nachweis.querschnittsloeser]]
- [[opencivil.nachweis.rechenwahl]]
- [[opencivil.nachweis.richtungsnachweise]]
- [[opencivil.nachweis.rissanforderung]]
- [[opencivil.nachweis.rissgroessen]]
- [[opencivil.nachweis.schiefe_biegung]]
- [[opencivil.nachweis.spannungsbegrenzung]]
- [[opencivil.nachweis.spannungsgrenzen]]
- [[opencivil.nachweis.stabgrenzen]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.geometrie]]
- [[opencivil.querschnitt.gesetzwahl]]
- [[opencivil.querschnitt.interaktion]]

## Gebraucht von

- [[opencivil.projekt.aufbau]]

## Formeln aus diesem Modul

- [[Aufnehmbare Risskraft]] · `RissnormalkraftQA.pruefe`
- [[Moment der Bewehrung bei zulässiger Stahlspannung]] · `ZwaengungBiegungQA._protokoll_ansatz`
- [[Rissaktive Dicke des gezeichneten Querschnitts]] · `RissnormalkraftQA._risskraft`
- [[Risskraft des ganzen Querschnitts]] · `RissnormalkraftQA._risskraft`
