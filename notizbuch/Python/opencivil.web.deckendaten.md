---
erzeugt: c8a872aa5b42
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
Querkraefte in Zellen ueber die Platten, ihre groessten Werte mit Ort, die
Kraft jeder Stuetze und der Verlauf laengs jedes Linienlagers. Die Zellen
sind gross; mit jeder Rechnung mitgeliefert, machten sie jede Eingabe
langsamer -- dasselbe wie beim Verlauf des Balkensystems.

Was in eine Rechnung eingeht, rechnet hier niemand; geschnitten wird nur
fuers Bild, und die Werte an einer Stelle kommen aus
[[opencivil.decke.feld]].

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
def ergebnis(befund: Deckenbefund, name: str) -> Dict[str, Any]
```

Die Bilder des Falls `name`, Lastfall oder Kombination: `zellen`, je
Zelle ihre Ecken, und `werte`, je Groesse
([[opencivil.decke.feld#Konstanten|GROESSEN]]) der Wert am Schwerpunkt jeder
Zelle; `extreme`, je Groesse der groesste und der kleinste Wert mit
seinem Ort -- gesucht unter den Schwerpunkten und den Stellen, an denen
ein Traeger springt oder sein Extremum hat ([[opencivil.decke.feld#stellen|stellen]]).
Dazu je Stuetze ihre Kraft `F` und je Linienlager, was
[[opencivil.web.deckendaten#_linienlager|_linienlager]] sagt. Momente in kNm/m, Querkraefte und `r` in
kN/m, Kraefte in kN -- wie `einheiten` sagt.

### _linienlager

```python
def _linienlager(lager: Linienlager, fall: Fallergebnis) -> Dict[str, Any]
```

Ein Linienlager im Bild eines Falls: seine Summe `F`, seine Stufen
`[u_a, u_b, r, m]` ([[opencivil.decke.rechnung#lagerverlauf|lagerverlauf]]),
`r_max`, der Wert von r mit dem groessten Betrag, und `m_max`, der
groesste Betrag von m -- nur der Betrag: das Vorzeichen von m haengt an
der Richtung a -> b, die niemand sieht.

### _extreme

```python
def _extreme(proben: Sequence[Tuple[Punkt, feld.Schnittkraefte]], groesse: str) -> Dict[str, Any]
```

Der groesste und der kleinste Wert einer Groesse unter den Proben, je mit Ort.

### _zellen

```python
def _zellen(e: Ergebnis) -> List[List[Punkt]]
```

Die Zellen der Bilder: je Gruppe die Feldstreifen ihrer beiden
Richtungen, die breiten geteilt ([[opencivil.web.deckendaten#Konstanten|ZELLEN]]), gekreuzt und mit den
konvexen Stuecken ihrer Platten geschnitten. So liegt jede Zelle in
einem Streifen jeder Richtung, und ihr Wert gilt fuer sie ganz.

### _baender

```python
def _baender(streifen: Sequence[Any], weite: float) -> List[Tuple[float, float]]
```

Die Feldstreifen einer Richtung quer in Baender, keines breiter als `weite`.

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
- `ZELLEN = 24` – So viele Zellen hat ein Bild der Schnittkraefte ueber die laengere Seite der Decke mindestens -- breitere Streifen werden dafuer geteilt. Mehr machten die Antwort gross: bei 40 waren es fuer die Decke des Kolloquiums 4 (9 m, Streifen 0.25 m) 3168 Zellen und 330 kB.
- `EINHEITEN = {g: KNM_PRO_M if g.startswith('m') else KN_PRO_M for g in feld.GROESS…` – Die Einheit der Anzeige je Groesse: Momente in kNm/m, Querkraefte in kN/m.

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.rechenwerk]]
- [[opencivil.decke.feld]]
- [[opencivil.decke.geometrie]]
- [[opencivil.decke.modell]]
- [[opencivil.decke.rechnung]]
- [[opencivil.decke.werk]]
- [[opencivil.projekt]]
- [[opencivil.stabwerk.system]]
- [[opencivil.web.anzeige]]

## Gebraucht von

- [[opencivil.web.dienst]]
- [[opencivil.web.zeichendaten]]
