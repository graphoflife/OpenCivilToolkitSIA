---
erzeugt: 0af1a57bfc13
art: modul
tags: [modul]
---
> [!abstract] opencivil/notizbuch/namen.py
> aus einem Namen wird ein Seitenname.
> Paket [[opencivil.notizbuch]] · [Quelltext](../../opencivil/notizbuch/namen.py)

## VERANTWORTUNG

Eine Seite des Notizbuchs heisst wie ihre Datei, und Obsidian verlinkt ueber
den Dateinamen: `[[Bemessungswert der Betondruckfestigkeit]]`. Was eine
Formel oder ein Thema heisst, muss darum auch als Dateiname taugen -- auf
jedem System und in jedem Link. Die Regel dafuer steht hier und nur hier;
Formelsammlung, Bruecke und api fragen sie ab.


## WAS ERSETZT WIRD

Ein Doppelpunkt wird zum Gedankenstrich (`Probe: Moment` -> ``Probe –
Moment``), der Schraegstrich zum Divisionsstrich ∕, die uebrigen Zeichen, die
ein System oder ein Link nicht vertraegt, zu einem aehnlichen; `?`, `#`
und `^` fallen weg. Geschrieben wird in NFC: dieselben Buchstaben, gleich
codiert, wo immer die Datei entstand.


## NIE STILL KUERZEN

Ein zu langer Name ist ein Fehler. Abgeschnitten fielen zwei Namen mit
gleichem Anfang zusammen -- und eine Seite verschwaende hinter der anderen.

Dieses Modul importiert nichts aus `opencivil`: die api laedt es auch in
Pyodide, wo jedes Modul beim Start mitkommt.

## Inhalt

### NamensFehler

```python
class NamensFehler(ValueError)
```

Aus diesem Text wird kein brauchbarer Seitenname.

### seitenname

```python
def seitenname(text: str) -> str
```

Der Name, unter dem eine Seite im Notizbuch steht -- zugleich ihr
Dateiname ohne `.md`.

Einmal angewandt, aendert eine zweite Anwendung nichts mehr.

### vergleichsname

```python
def vergleichsname(name: str) -> str
```

Woran zwei Namen als derselbe gelten: Obsidian und manches Dateisystem
unterscheiden gross und klein nicht.

### sortierschluessel

```python
def sortierschluessel(name: str) -> str
```

Deutsch sortiert, und auf jedem Rechner gleich: ä wie a, ß wie ss --
ohne die Spracheinstellung des Systems zu fragen.


## Konstanten

- `ERSATZ = {'/': '∕', '\\': '∕', '|': '¦', '*': '·', '"': "'", '<': '‹', '>': '›…` – Was in einem Dateinamen oder einem Link nicht stehen darf, und wofuer es steht. `:` hat eine eigene Regel (siehe [[opencivil.notizbuch.namen#seitenname|seitenname]]).
- `WEG = '?#^'` – Zeichen, die ersatzlos wegfallen: `#` und `^` meinen in einem Obsidian-Link Ueberschrift und Absatz.
- `HOECHSTENS = 100` – Laenger wird kein Name -- sonst ist er keiner mehr, sondern ein Satz.

## Gebraucht von

- [[opencivil.bericht.formelsammlung]]
- [[opencivil.notizbuch.bibliothek]]
- [[opencivil.notizbuch.formelseiten]]
- [[opencivil.notizbuch.tresor]]
