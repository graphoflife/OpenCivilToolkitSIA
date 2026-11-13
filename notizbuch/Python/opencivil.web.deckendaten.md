---
erzeugt: 9354989b7e96
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
samt Last und Lagerkraft. Was in eine Rechnung eingeht, rechnet hier
niemand; geschnitten wird nur fuers Bild.

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
`lager` tragen, in kN -- und seine `meldungen`. Die Zonen und
Lasten zeichnet die Oberflaeche nach dem Projekt.

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

## Braucht

- [[opencivil.core.rechenwerk]]
- [[opencivil.decke.geometrie]]
- [[opencivil.decke.modell]]
- [[opencivil.decke.rechnung]]
- [[opencivil.decke.werk]]
- [[opencivil.projekt]]
- [[opencivil.stabwerk.system]]

## Gebraucht von

- [[opencivil.web.dienst]]
- [[opencivil.web.zeichendaten]]
