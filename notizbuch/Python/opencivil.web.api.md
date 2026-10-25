---
erzeugt: 056740861bc5
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
def loesung_dict(loesung: Loesung, aufbau: Optional[Aufbau]=None, *, spannungsanalysen: Optional[dict]=None) -> dict
```

Vollstaendige Abbildung eines Rechenlaufs. `spannungsanalysen` sind die
Zeichendaten der Analysen, wo der Aufrufer sie schon hat -- aus dem
Zwischenspeicher ([[opencivil.web.dienst#rechnen|opencivil.web.dienst.rechnen]]); sonst werden sie
hier gerechnet.

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

Verbindet die Kennungen der Oberflaeche mit den Wert-IDs des Rechenwerks:
die Materialien und je Bauteilart unter ihrer Liste die Bauteile -- je
Namensraum, Name und was [[opencivil.web.api#Konstanten|_ZUORDNUNG]] fuer ihre Art sagt.

### _werte

```python
def _werte(teil) -> dict
```

Wo die Werte eines Bauteils stehen, nach Kurzname.

### _systemzuordnung

```python
def _systemzuordnung(teil) -> dict
```

Je Querschnitt eines Systems, wo A und I stehen -- und je Paar aus Querschnitt und Material EA und EI.


## Konstanten

- `_WERKSTOFFSAETZE = [{'wert': s.value, 'beschriftung': s.beschriftung, 'kurz': s.kurz} fo…` – Die Wertesaetze und Betongesetze mit Beschriftung -- dieselben in der Querschnittsanalyse und in jeder Spannung-Dehnung-Analyse. `kurz` fuer die Karte einer Analyse, in der die lange nicht Platz hat. Die Woerter stehen beim Wertesatz selbst.
- `_VERSCHMIERUNGEN = {'flaeche': ('Stahlfläche', 'Die Stahlfläche der ganzen Linie, von Ha…` – Wie die Angaben einer verschmierten Stablinie heissen: kurz im Schalter, lang in seinem Titel -- je Angabe, die die Beschreibung kennt.
- `_DIAGRAMMGROESSEN = {'M': ('M', 'Moment M'), 'V': ('V', 'Querkraft V'), 'N': ('N', 'Norma…` – Wie die Diagramme der Statik-Analyse heissen: kurz im Schalter, lang ueber dem Diagramm -- je Groesse, die die Beschreibung kennt.
- `_BETONGESETZE = [{'wert': a.value, 'beschriftung': a.beschriftung, 'kurz': a.kurz} fo…` – Die Betongesetze heissen wie die Rechenarten, deren Werte sie sind; welche es gibt, steht am Feld der Werkstoffwahl.
- `TAFEL = {TitelBlock: _titel_dict, TextBlock: _text_dict, GleichungBlock: _gle…` – Je Blockart, wie die Oberflaeche sie bekommt -- jede als JSON-Objekt.
- `_ZUORDNUNG = {'platte': _plattenzuordnung, 'balkensystem': _systemzuordnung}` – Was eine Bauteilart in der Zuordnung mehr hat als Namensraum und Name -- ohne Eintrag ihre Werte ([[opencivil.web.api#_werte|_werte]]). Bis 2026-10-25 stand die Zuordnung je Art von Hand da, zwei Bloecke wortgleich.

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
- [[opencivil.geotechnik.setzung]]
- [[opencivil.material.beton]]
- [[opencivil.material.betonstahl]]
- [[opencivil.nachweis.biegung_normalkraft]]
- [[opencivil.nachweis.duktilitaet]]
- [[opencivil.nachweis.rechenwahl]]
- [[opencivil.nachweis.rissanforderung]]
- [[opencivil.projekt]]
- [[opencivil.projekt.balkensystem]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.lesen]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.geometrie]]
- [[opencivil.querschnitt.gesetzwahl]]
- [[opencivil.querschnitt.vorlagen]]
- [[opencivil.querschnitt.zugseite]]
- [[opencivil.spannungsanalyse]]
- [[opencivil.stabwerk.modell]]
- [[opencivil.stabwerk.querschnitte]]
- [[opencivil.stabwerk.rechnung]]
- [[opencivil.web.balkendaten]]
- [[opencivil.web.diagrammdaten]]
- [[opencivil.web.grundbruchdaten]]
- [[opencivil.web.setzungsdaten]]
- [[opencivil.web.umschlag]]

## Gebraucht von

- [[opencivil.web.dienst]]
