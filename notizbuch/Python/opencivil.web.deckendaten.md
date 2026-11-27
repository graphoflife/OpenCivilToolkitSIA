---
erzeugt: 92844383ac39
art: modul
tags: [modul]
---
> [!abstract] opencivil/web/deckendaten.py
> was die Oberflaeche von einer Decke zeichnet.
> Paket [[opencivil.web]] · [Quelltext](../../opencivil/web/deckendaten.py)

## VERANTWORTUNG

Aus dem Befund einer Decke die Daten ihrer Bilder, in m. In der
Streifenmethode: wie die Last auf die zwei Richtungen geht – je Zelle der
automatischen Aufteilung, je Platte bei fester, und in den Zonen –, wo die
Grenzen der Streifen verlaufen, die Flaechen der Traeger und die
Stuetzenbereiche. In der FEM: das Netz und die Flaechen der Traeger. In
beiden die Meldungen – die der Decke und je Lastfall und Kombination die
eigenen, samt Last und Lagerkraft, auch je Lager.

Auf Anfrage die Bilder eines Falls ([[opencivil.web.deckendaten#ergebnis|ergebnis]]): die Momente und
Querkraefte – in der FEM auch die Durchbiegung – in Zellen ueber die
Platten, je Zelle mit ihrem Gefaelle, ihre groessten Werte mit Ort, die
Kraft jeder Stuetze, der Verlauf laengs jedes Linienlagers, der laengs
jedes Schnitts und der jedes Traegers – dieser ganz, nicht je Meter. Die
Zellen sind gross; mit jeder Rechnung mitgeliefert, machten sie jede
Eingabe langsamer – dasselbe wie beim Verlauf des Balkensystems.

Was in eine Rechnung eingeht, rechnet hier niemand: Zellen, Werte und
groesste Werte kommen je Verfahren ([[opencivil.web.deckendaten#Konstanten|_BILDER]]) von derselben Stelle,
an der auch der Bericht sie holt – in der Streifenmethode aus
[[opencivil.decke.feld]] und [[opencivil.decke.schnitt]], in der FEM
aus [[opencivil.decke.fem.auswertung]].

## Inhalt

### zeichnung

```python
def zeichnung(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Dict[str, Any]
```

Was die Zeichnung einer Decke unter ihre Teile legt – auch wenn sie nicht rechnet.

### uebersicht

```python
def uebersicht(befund: Optional[Deckenbefund]) -> Dict[str, Any]
```

`gerechnet` und `meldungen` (`{text, elemente, fehler}`) immer,
mit einem Befund auch das `verfahren`, nach dem er rechnete. Was die
Decke je Verfahren dazu zeichnet, sagen [[opencivil.web.deckendaten#_streifen|_streifen]] und
[[opencivil.web.deckendaten#_fem|_fem]]; wenn sie rechnete, in beiden `faelle`: je Lastfall und
Kombination `name`, die Last `summe`, was davon `daneben` liegt
und `nicht_getragen` wird, und was die `lager` tragen, in kN, auch
`je_lager` ([[opencivil.web.deckendaten#_je_lager|_je_lager]]) – und seine `meldungen`;
`fallmeldungen` sind dieselben, jede einmal, vorn ihre Faelle
([[opencivil.decke.rechnung#Faelle.fallmeldungen|fallmeldungen]]). Die Zonen und
Lasten zeichnet die Oberflaeche nach dem Projekt.

### _streifen

```python
def _streifen(e: Ergebnis) -> Dict[str, Any]
```

In der Streifenmethode `von_selbst`: je Platte, die ihre Richtungen
selbst wählt, die zwei in Grad gegen x; wenn die Decke in Streifen
zerfiel, `gerechnet` und dazu `richtungen`, `anteile` (Vieleck und
Anteil in Richtung 1, in % – `None`, wo keine Richtung trägt),
`grenzen` (je Grenze zweier Streifen eine Strecke), `traeger` – die
des Benutzers –, `baender` – die die Rechnung selbst legte, mit
`achse`, `art` und `breite` in m – und `stuetzenbereiche`.

### _fem

```python
def _fem(e: Femergebnis) -> Dict[str, Any]
```

In der FEM, wenn ein Netz entstand, `gerechnet` und dazu das `netz`
– seine `weite` und seine `knoten` in m, seine `dreiecke`, je
drei Nummern von Knoten – und die `traeger`, je die Flaeche ihrer
Breite.

### verfahren_von

```python
def verfahren_von(groesse: str) -> List[str]
```

Die Verfahren, deren Bilder `groesse` zeigen: eine Groesse der Platte
die, die sie rechnen – die Lagerkraefte, M und V jedes.

### faelle

```python
def faelle(befund: Optional[Deckenbefund]) -> List[str]
```

Die Namen der gerechneten Faelle, Lastfaelle zuerst – leer, wenn die Decke nicht rechnet.

### _je_lager

```python
def _je_lager(e: Faelle, f: Fall) -> List[Dict[str, Any]]
```

Was jedes Lager traegt, in kN: jede Stuetze, jedes Linienlager – auch, was nichts traegt.

### ergebnis

```python
def ergebnis(befund: Deckenbefund, name: str, schnitte: Sequence[Tuple[str, Punkt, Punkt]]=()) -> Dict[str, Any]
```

Die Bilder des Falls `name`, Lastfall oder Kombination, nach dem
Verfahren der Decke ([[opencivil.web.deckendaten#Konstanten|_BILDER]]): `zellen`, je Zelle ihre Ecken,
`mitten`, je Zelle ihr Schwerpunkt, und `werte`, je Groesse des
Verfahrens der Wert dort; `gefaelle`, je Groesse und Zelle
`[∂/∂x, ∂/∂y]` in ihrer Einheit je m – damit verlaeuft die Farbe ueber
die Zelle; `extreme`, je Groesse der groesste und der kleinste Wert mit
seinem Ort – gesucht an den Proben des Bilds
([[opencivil.decke.feld#Bild|Bild]]). Dazu je Stuetze ihre Kraft `F`,
je Linienlager, was [[opencivil.web.deckendaten#_linienlager|_linienlager]] sagt, je der `schnitte` –
`(Kennung, a, b)` – und je Traeger, was [[opencivil.web.deckendaten#_verlauf|_verlauf]] sagt.
Momente in kNm/m, Querkraefte und `r` in kN/m, die Durchbiegung in
mm, Kraefte in kN, die eines Traegers in kNm und kN – wie
`einheiten` sagt.

### _Verfahren

```python
@dataclass(frozen=True)
class _Verfahren
```

Woher die Bilder eines Verfahrens kommen: welche `groessen` sie
zeigen, was die Uebersicht zeichnet, das Bild der Platte in einem Fall,
der Verlauf laengs eines Schnitts und je Traeger ``(Name, a, b,
Verlauf)``.

- `groessen: Sequence[str]`
- `uebersicht: Callable[[Any], Dict[str, Any]]`
- `bild: Callable[[Any, Any], feld.Bild]`
- `verlauf: Callable[[Any, Any, Punkt, Punkt], schnitt.Verlauf]`
- `traeger: Callable[[Any, Any], List[Tuple[str, Punkt, Punkt, schnitt.Verlauf]]]`

### _verlauf

```python
def _verlauf(v: schnitt.Verlauf, kennung: str, a: Punkt, b: Punkt, groessen: Sequence[str]) -> Dict[str, Any]
```

Ein Schnitt oder ein Traeger im Bild eines Falls, alles in m ab `a`:
seine Enden `a` und `b`, seine Laenge `L`, wo er in einer Platte
liegt (`stuecke`), die `stellen`, an denen er hinsieht, und je der
`groessen` die `werte` dort und die `extreme` mit Stelle `u`;
die `lager`, die er kreuzt oder auf denen er liegt, und die
`traeger`. Zwei Stellen eines Sprungs fallen in der Rundung
zusammen – im Bild steht er senkrecht.

### _linienlager

```python
def _linienlager(lager: Linienlager, fall: Fall) -> Dict[str, Any]
```

Ein Linienlager im Bild eines Falls: seine Summe `F`, seine Stufen
`[u_a, u_b, r, m]` ([[opencivil.decke.rechnung#Fall|lagerstufen]]),
`r_max` und `m_max` ([[opencivil.decke.rechnung#spitzen|spitzen]]).

### _extreme

```python
def _extreme(proben: Sequence[feld.Probe], groesse: str) -> Dict[str, Any]
```

Der groesste und der kleinste Wert einer Groesse unter den Proben, je mit Ort.

### _anteile

```python
def _anteile(e: Ergebnis) -> List[Tuple[Sequence[Tuple[float, float]], Optional[float]]]
```

Automatisch die Zellen der Aufteilung, fest jede Platte mit dem Anteil der Decke.

### _grenzen

```python
def _grenzen(e: Ergebnis) -> List[Dict[str, Any]]
```

Je Richtung jeder Platte die Grenzen ihrer Feldstreifen, als Strecken
in der Platte – in einem L zwei, wo die Grenze die Ecke quert.


## Konstanten

- `STELLEN = 4` – Auf einen Zehntelmillimeter – fuers Bild genug, und die Antwort bleibt klein.
- `EINHEITEN = {**{g: KNM_PRO_M if g.startswith('m') else KN_PRO_M for g in feld.GRO…` – Die Einheit der Anzeige je Groesse: Momente der Platte in kNm/m, Querkraefte in kN/m, die Durchbiegung in mm – die eines ganzen Trägers in kNm und kN.
- `_BILDER = {Verfahren.STREIFEN: _Verfahren(tuple(feld.GROESSEN), _streifen, feld…` – Je Verfahren der Decke, woher ihre Bilder kommen – einmal gewaehlt, je Anfrage.

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.rechenwerk]]
- [[opencivil.decke.baender]]
- [[opencivil.decke.feld]]
- [[opencivil.decke.fem.auswertung]]
- [[opencivil.decke.fem.rechnung]]
- [[opencivil.decke.geometrie]]
- [[opencivil.decke.modell]]
- [[opencivil.decke.rechnung]]
- [[opencivil.decke.schnitt]]
- [[opencivil.decke.werk]]
- [[opencivil.projekt]]
- [[opencivil.stabwerk.system]]
- [[opencivil.web.anzeige]]

## Gebraucht von

- [[opencivil.web.api]]
- [[opencivil.web.dienst]]
- [[opencivil.web.zeichendaten]]
