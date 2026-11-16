---
erzeugt: 1a9d393d126a
art: modul
tags: [modul]
---
> [!abstract] opencivil/web/deckendaten.py
> was die Oberflaeche von einer Decke zeichnet.
> Paket [[opencivil.web]] · [Quelltext](../../opencivil/web/deckendaten.py)

## VERANTWORTUNG

Aus dem Befund einer Decke die Daten ihrer Bilder, in m: wie die Last auf
die zwei Richtungen geht -- je Zelle der automatischen Aufteilung, je
Platte bei fester, und in den Zonen --, wo die Grenzen der Streifen
verlaufen, die Flaechen der Unterzuege und die Stuetzenbereiche, dazu die
Meldungen -- die der Decke und je Lastfall und Kombination die eigenen,
samt Last und Lagerkraft, auch je Lager.

Auf Anfrage die Bilder eines Falls ([[opencivil.web.deckendaten#ergebnis|ergebnis]]): die Momente und
Querkraefte in Zellen ueber die Platten, je Zelle mit ihrem Gefaelle, ihre
groessten Werte mit Ort, die Kraft jeder Stuetze, der Verlauf laengs
jedes Linienlagers, der laengs jedes Schnitts und der jedes Unterzugs --
dieser ganz, nicht je Meter. Die Zellen sind gross;
mit jeder Rechnung mitgeliefert, machten sie jede Eingabe langsamer --
dasselbe wie beim Verlauf des Balkensystems.

Was in eine Rechnung eingeht, rechnet hier niemand: Zellen, Werte und
groesste Werte kommen aus [[opencivil.decke.feld]], derselben Stelle, an
der auch der Bericht sie holt -- laengs eines Schnitts ueber
[[opencivil.decke.schnitt]].

## Inhalt

### zeichnung

```python
def zeichnung(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Dict[str, Any]
```

Was die Zeichnung einer Decke unter ihre Teile legt -- auch wenn sie nicht rechnet.

### uebersicht

```python
def uebersicht(befund: Optional[Deckenbefund]) -> Dict[str, Any]
```

`gerechnet` und `meldungen` (`{text, elemente, fehler}`) immer;
wenn die Decke in Streifen zerfiel, dazu `richtungen`, `anteile`
(Vieleck und Anteil in Richtung 1, in %), `grenzen` (je Grenze
zweier Streifen eine Strecke), `unterzuege`, `stuetzenbereiche` und
`faelle`: je Lastfall und Kombination `name`, die Last `summe`,
was davon `daneben` liegt und `nicht_getragen` wird, und was die
`lager` tragen, in kN, auch `je_lager` ([[opencivil.web.deckendaten#_je_lager|_je_lager]]) -- und
seine `meldungen`. Die Zonen und Lasten zeichnet die Oberflaeche nach
dem Projekt.

### faelle

```python
def faelle(befund: Optional[Deckenbefund]) -> List[str]
```

Die Namen der gerechneten Faelle, Lastfaelle zuerst -- leer, wenn die Decke nicht rechnet.

### _je_lager

```python
def _je_lager(e: Ergebnis, f: Fallergebnis) -> List[Dict[str, Any]]
```

Was jedes Lager traegt, in kN: jede Stuetze, jedes Linienlager -- auch, was nichts traegt.

### ergebnis

```python
def ergebnis(befund: Deckenbefund, name: str, schnitte: Sequence[Tuple[str, Punkt, Punkt]]=()) -> Dict[str, Any]
```

Die Bilder des Falls `name`, Lastfall oder Kombination: `zellen`, je
Zelle ihre Ecken, `mitten`, je Zelle ihr Schwerpunkt, und `werte`,
je Groesse ([[opencivil.decke.feld#Konstanten|GROESSEN]]) der Wert dort;
`gefaelle`, je Groesse und Zelle `[∂/∂x, ∂/∂y]` in ihrer Einheit je
m ([[opencivil.decke.feld#gefaelle|gefaelle]]) -- damit verlaeuft die Farbe
ueber die Zelle; `extreme`, je Groesse der groesste und der kleinste
Wert mit seinem Ort -- gesucht an den Proben des Falls
([[opencivil.decke.feld#proben|proben]]).
Dazu je Stuetze ihre Kraft `F`, je Linienlager, was
[[opencivil.web.deckendaten#_linienlager|_linienlager]] sagt, je der `schnitte` -- `(Kennung, a, b)` --
und je Unterzug, was [[opencivil.web.deckendaten#_verlauf|_verlauf]] sagt. Momente in kNm/m,
Querkraefte und `r` in kN/m, Kraefte in kN, die eines Unterzugs in kNm
und kN -- wie `einheiten` sagt.

### _verlauf

```python
def _verlauf(v: schnitt.Verlauf, kennung: str, a: Punkt, b: Punkt, groessen: Sequence[str]) -> Dict[str, Any]
```

Ein Schnitt oder ein Unterzug im Bild eines Falls, alles in m ab `a`:
seine Enden `a` und `b`, seine Laenge `L`, wo er in einer Platte
liegt (`stuecke`), die `stellen`, an denen er hinsieht, und je der
`groessen` die `werte` dort und die `extreme` mit Stelle `u`;
die `lager`, die er kreuzt oder auf denen er liegt, und die
`unterzuege`. Zwei Stellen eines Sprungs fallen in der Rundung
zusammen -- im Bild steht er senkrecht.

### _linienlager

```python
def _linienlager(lager: Linienlager, fall: Fallergebnis) -> Dict[str, Any]
```

Ein Linienlager im Bild eines Falls: seine Summe `F`, seine Stufen
`[u_a, u_b, r, m]` ([[opencivil.decke.rechnung#lagerverlauf|lagerverlauf]]),
`r_max` und `m_max` ([[opencivil.decke.rechnung#spitzen|spitzen]]).

### _extreme

```python
def _extreme(proben: Sequence[feld.Probe], groesse: str) -> Dict[str, Any]
```

Der groesste und der kleinste Wert einer Groesse unter den Proben, je mit Ort.

### _anteile

```python
def _anteile(e: Ergebnis) -> List[Tuple[Sequence[Tuple[float, float]], float]]
```

Automatisch die Zellen der Aufteilung, fest jede Platte mit dem Anteil der Decke.

### _grenzen

```python
def _grenzen(e: Ergebnis) -> List[Dict[str, Any]]
```

Je Richtung jeder Platte die Grenzen ihrer Feldstreifen, als Strecken
in der Platte -- in einem L zwei, wo die Grenze die Ecke quert.


## Konstanten

- `STELLEN = 4` – Auf einen Zehntelmillimeter -- fuers Bild genug, und die Antwort bleibt klein.
- `EINHEITEN = {**{g: KNM_PRO_M if g.startswith('m') else KN_PRO_M for g in feld.GRO…` – Die Einheit der Anzeige je Groesse: Momente der Platte in kNm/m, Querkraefte in kN/m -- die eines ganzen Unterzugs in kNm und kN.

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.rechenwerk]]
- [[opencivil.decke.feld]]
- [[opencivil.decke.geometrie]]
- [[opencivil.decke.modell]]
- [[opencivil.decke.rechnung]]
- [[opencivil.decke.schnitt]]
- [[opencivil.decke.werk]]
- [[opencivil.projekt]]
- [[opencivil.stabwerk.system]]
- [[opencivil.web.anzeige]]

## Gebraucht von

- [[opencivil.web.dienst]]
- [[opencivil.web.zeichendaten]]
