---
erzeugt: 7d93e06354ee
art: modul
tags: [modul]
---
> [!abstract] opencivil/web/api.py
> Uebersetzung der Rechenergebnisse nach JSON.
> Paket [[opencivil.web]] · [Quelltext](../../opencivil/web/api.py)

## VERANTWORTUNG

Bildet [[opencivil.core.rechenwerk#Loesung|Loesung]], Protokoll, Zusammenfassung und Katalogdaten auf
schlichte JSON-Strukturen ab. Zusammen mit [[opencivil.web.diagrammdaten]],
das die Punktfolgen der Diagramme liefert, ist das die einzige Stelle, die
beide Welten kennt.

Wichtig: hier wird nichts gerechnet und nichts formatiert, was der Rechenkern
nicht schon bestimmt hat. Die Oberflaeche bekommt fertige LaTeX-Zeichenketten
und fertig formatierte Zahlen -- sie soll die Darstellung nicht ein zweites Mal
erfinden, sonst laufen Bericht und Bildschirm auseinander.

## Inhalt

### _rechenarten

```python
def _rechenarten(arten) -> list
```

Die Rechenarten mit Beschriftung -- und ob die Kriechzahl bei ihnen wirkt.

### katalog

```python
def katalog() -> dict
```

Alles, was die Oberflaeche zum Aufbau ihrer Auswahlfelder braucht.

### obergrenzen

```python
def obergrenzen(projekt) -> Dict[str, str]
```

Je Platte die Obergrenze der automatischen Bewehrung, fertig als Text --
«4712 mm²/m» oder «keine». Die Oberflaeche zeigt sie neben den Eingaben,
ohne selbst zu rechnen.

### wert_dict

```python
def wert_dict(wert: Wert) -> dict
```

### zelle_dict

```python
def zelle_dict(zelle: Zelle) -> dict
```

Eine Tabellenzelle fuer die Oberflaeche: `{"text": ...}` oder
`{"mathe": ...}`. Die Oberflaeche setzt nur Formeln mit KaTeX -- Text
aus LaTeX zurueckzulesen, wie sie es frueher musste, entfaellt.

### protokoll_liste

```python
def protokoll_liste(protokoll: Protokoll) -> List[dict]
```

### loesung_dict

```python
def loesung_dict(loesung: Loesung, aufbau: Optional[Aufbau]=None) -> dict
```

Vollstaendige Abbildung eines Rechenlaufs.

### zusammenfassungen

```python
def zusammenfassungen(loesung: Loesung, aufbau: Aufbau) -> dict
```

Je Platte die Nachweistabelle -- Zeilen **und** ihr LaTeX.

Was darin steht, darueber und darunter, baut
[[opencivil.bericht.zusammenfassung]] -- dieselben Stuecke, die auch
im Bericht stehen. Hier werden sie nur abgebildet; die Oberflaeche faerbt
ein, was `erfuellt` sagt, und haengt die Begruendung als Tooltip an die
Zeile.

### geometrie

```python
def geometrie(eintrag, projekt) -> dict
```

Die Zeichnung einer Querschnittsanalyse, wie der Kern sie sieht -- in mm.

Geprueft von [[opencivil.querschnitt.analyse#Zeichnung|Zeichnung]], denselben
Pruefungen, die das Bauteil vor dem Rechnen macht; hier aber alle
Meldungen auf einmal statt nur der ersten. Ein Material, das es nicht
gibt, oder ein Stahl als Polygon kommt dazu -- das kann nur das Projekt
wissen. Ebenso ein Verweis auf einen Knoten, den es nicht gibt.

### zuordnung

```python
def zuordnung(aufbau: Aufbau) -> dict
```

Verbindet die Kennungen der Oberflaeche mit den Wert-IDs des Rechenwerks.


## Konstanten

- `_WERKSTOFFSAETZE = [{'wert': s.value, 'beschriftung': s.beschriftung, 'kurz': s.kurz} fo…` – Die Wertesaetze und Betongesetze mit Beschriftung -- dieselben in der Querschnittsanalyse und in jeder Spannung-Dehnung-Analyse. `kurz` fuer die Karte einer Analyse, in der die lange nicht Platz hat. Die Woerter stehen beim Wertesatz selbst.
- `_BETONGESETZE = [{'wert': a.value, 'beschriftung': a.beschriftung, 'kurz': a.kurz} fo…` – Die Betongesetze heissen wie die Rechenarten, deren Werte sie sind; welche es gibt, steht am Feld der Werkstoffwahl.
- `TAFEL = {TitelBlock: _titel_dict, TextBlock: _text_dict, GleichungBlock: _gle…` – Je Blockart, wie die Oberflaeche sie bekommt -- jede als JSON-Objekt.

## Braucht

- [[opencivil.bericht.formelsammlung]]
- [[opencivil.bericht.markdown]]
- [[opencivil.bericht.zusammenfassung]]
- [[opencivil.bewehrungssuche]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.rechenwerk]]
- [[opencivil.core.wert]]
- [[opencivil.material.beton]]
- [[opencivil.material.betonstahl]]
- [[opencivil.nachweis.biegung_normalkraft]]
- [[opencivil.nachweis.duktilitaet]]
- [[opencivil.nachweis.querschnittsloeser]]
- [[opencivil.nachweis.rechenwahl]]
- [[opencivil.nachweis.rissanforderung]]
- [[opencivil.nachweis.verformung]]
- [[opencivil.projekt]]
- [[opencivil.projekt.balkensystem]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.lesen]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.geometrie]]
- [[opencivil.querschnitt.vorlagen]]
- [[opencivil.querschnitt.zugseite]]
- [[opencivil.spannungsanalyse]]
- [[opencivil.stabwerk.modell]]
- [[opencivil.stabwerk.querschnitte]]
- [[opencivil.web.balkendaten]]
- [[opencivil.web.diagrammdaten]]
- [[opencivil.web.grundbruchdaten]]
- [[opencivil.web.umschlag]]

## Gebraucht von

- [[opencivil.web.dienst]]
