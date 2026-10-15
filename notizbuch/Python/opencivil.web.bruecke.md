---
erzeugt: 7d16a45d362c
art: modul
tags: [modul]
---
> [!abstract] opencivil/web/bruecke.py
> Welche Dateien der Browser laden muss.
> Paket [[opencivil.web]] · [Quelltext](../../opencivil/web/bruecke.py)

## VERANTWORTUNG

Fuehrt Buch darueber, aus welchen Quelldateien der Rechenkern besteht, und
schreibt diese Liste nach `web/kern/dateien.json`. Der Faden in
`web/js/kern_arbeiter.js` liest sie, holt die Dateien uebers Netz und legt
sie ins Dateisystem von Pyodide -- danach ist `import opencivil` im Browser
dasselbe wie auf dem Rechner.


## WARUM EINE LISTE UND KEIN ARCHIV

Ein Archiv waere ein zweites, erzeugtes Abbild des Quellcodes im Repo -- und
damit etwas, das unbemerkt veralten kann. Die Liste ist reiner Text, im Diff
lesbar, und [[opencivil.web.bruecke#stimmt_ueberein|stimmt_ueberein]] prueft im Test, dass sie zu den
tatsaechlich vorhandenen Dateien passt. Veraltet sie, schlaegt der Test an,
nicht erst die veroeffentlichte Seite.


## JE DATEI EINE MARKE

Neben jedem Pfad steht eine Marke, die ersten zwoelf Zeichen von SHA-256 ueber
den Inhalt. Der Browser holt die Datei als `...py?v=Marke`: eine geaenderte
Datei hat damit eine neue Adresse, und aus dem Zwischenspeicher kommt keine
alte Fassung mehr, waehrend die uebrigen schon neu sind. Ein schlichter
statischer Server ohne Cache-Angabe laesst den Browser nach Gefuehl
zwischenspeichern -- so kam einmal `blatt.py` nach einer Aenderung noch alt.
Das Manifest aendert sich darum mit jeder Aenderung am Kern; der Test merkt,
wenn das Neuschreiben vergessen ging.


## UND DAS NOTIZBUCH

Die ganze Formelsammlung ([[opencivil.bericht.formelsammlung#laeufe|opencivil.bericht.formelsammlung.laeufe]])
haengt an keinem Projekt -- rechnen muss man sie trotzdem: zwei Projekte, die
zusammen jeden Nachweis fuehren. Unter Pyodide dauerte das Sekunden. Darum
rechnet sie die Bruecke und legt sie fertig ab, als Seiten des Notizbuchs: je
Formel, je Thema, je Modul eine, im Ordner `notizbuch/` -- ohne
anzufassen, was dort von Hand steht ([[opencivil.notizbuch.tresor]]). Dazu das
Verzeichnis aller Seiten, `web/kern/notizbuch.json`: GitHub Pages zeigt
keinen Ordnerinhalt, die Oberflaeche erfaehrt nur so, welche Seiten es gibt.
Die Seiten selbst holt sie ohne Marke und ohne Zwischenspeicher -- eine in
Obsidian geaenderte Notiz steht damit nach dem Hochladen gleich da; eine neue
erst, wenn die Bruecke sie ins Verzeichnis geschrieben hat.


## MARKEN AUCH FUER DIE OBERFLAECHE

Dasselbe traf die Module der Oberflaeche: nach einer Aenderung kam einmal ein
altes `nachweise.js` zum neuen Kern. Darum schreibt die Bruecke in
`web/index.html` eine Importtafel (`<script type="importmap">`): je Modul
unter `web/js/` und je Verzeichnis unter `web/kern/` die Adresse mit
Marke, dazu das Stilblatt mit Marke. Die Module selbst bleiben, wie sie sind
-- `import './dom.js'` fuehrt ueber die Tafel auf `./dom.js?v=Marke`.
So haengt alles an der Seite: wer sie neu laedt, bekommt den Rest im selben
Stand. Ohne Marke bleiben nur die Fremdbibliotheken unter `web/vendor/`;
die aendern sich nur, wenn jemand bewusst eine neue Fassung einlegt.


## UND DIE FREMDPAKETE

Im Manifest steht auch, welche Fremdpakete unter `web/vendor/pyodide/`
beiliegen ([[opencivil.web.bruecke#mitgelieferte_pakete|mitgelieferte_pakete]]): Importname -> Paketname, gelesen aus
den Dateien, die dort liegen, und aus `pyodide-lock.json`. Die App «Python»
laedt nur diese ([[opencivil|opencivil.konsole.pakete]]). Eine zweite, von Hand
gefuehrte Liste gibt es nicht: was `werkzeug/pyodide_holen.py` hinlegt,
steht nach dem naechsten Lauf der Bruecke im Manifest.


## WARUM ALLE DATEIEN UND NICHT NUR DIE GEBRAUCHTEN

Man koennte die Liste auf das beschraenken, was [[opencivil.web.dienst]]
einbindet. Dann muesste die Regel aber bei jeder neuen Einbindung nachgezogen
werden, und wer das vergisst, merkt es erst im Browser. Ein paar Dutzend
Kilobyte sind der bessere Handel.


## AUFRUF


```
python3 -m opencivil.web.bruecke    # schreibt web/kern/ und die Marken in web/index.html
```

## Inhalt

### kerndateien

```python
def kerndateien() -> List[str]
```

Alle Quelldateien des Kerns, als Pfade vom Projektverzeichnis aus.

Sortiert, damit das Manifest bei gleichem Stand Zeichen fuer Zeichen gleich
herauskommt und im Diff nur echte Aenderungen auftauchen.

### marke

```python
def marke(pfad: Path) -> str
```

Die Versionsmarke einer Datei: die ersten zwoelf Zeichen von SHA-256 ueber
ihren Inhalt. Windows-Zeilenenden zaehlen nicht -- sonst stimmte das
Manifest nach einem Auschecken mit CRLF nicht mehr.

### manifest

```python
def manifest() -> dict
```

### mitgelieferte_pakete

```python
def mitgelieferte_pakete() -> Dict[str, str]
```

Importname -> Paketname, fuer jedes Fremdpaket, dessen Datei beiliegt --
`dateutil` -> `python-dateutil`. Sortiert, damit das Manifest bei
gleichem Stand gleich herauskommt.

### _mit_marken

```python
def _mit_marken() -> Dict[str, str]
```

Pfad -> Marke, in der Reihenfolge von [[opencivil.web.bruecke#kerndateien|kerndateien]].

### stimmt_ueberein

```python
def stimmt_ueberein() -> bool
```

Ob das abgelegte Manifest den vorhandenen Dateien entspricht -- samt Marken.

### schreiben

```python
def schreiben(pfad: Path | None=None) -> Path
```

### notizbuch_seiten

```python
@functools.lru_cache(maxsize=1)
def notizbuch_seiten() -> Tuple[tresor.Seite, ...]
```

Was der Code zum Notizbuch beitraegt -- einmal je Lauf gerechnet.

### notizbuch_plan

```python
def notizbuch_plan(wurzel: Optional[Path]=None) -> tresor.Plan
```

Was ein Lauf im Notizbuch schriebe, loeschte oder beanstandete.

### notizbuch_verzeichnis

```python
def notizbuch_verzeichnis(wurzel: Optional[Path]=None) -> dict
```

Das Verzeichnis aller Seiten, so wie die Oberflaeche es liest.

### notizbuch_schreiben

```python
def notizbuch_schreiben(wurzel: Optional[Path]=None, verzeichnis: Optional[Path]=None) -> tresor.Plan
```

Schreibt die erzeugten Seiten und das Verzeichnis. Beanstandet der Plan
etwas, bricht es ab, bevor eine Datei angefasst ist.

### notizbuch_stimmt

```python
def notizbuch_stimmt() -> bool
```

Ob Seiten und Verzeichnis dem entsprechen, was der Code heute ergibt.

### tafeldateien

```python
def tafeldateien() -> List[Path]
```

Was ueber die Importtafel der Seite geht: jedes Modul der Oberflaeche und
die Verzeichnisse unter `web/kern/`.

### versionsmarken

```python
def versionsmarken() -> str
```

Was in der Seite zwischen [[opencivil.web.bruecke#Konstanten|ANFANG]] und [[opencivil.web.bruecke#Konstanten|ENDE]] steht: das
Stilblatt und die Importtafel, jede Adresse mit der Marke ihrer Datei.

### _adresse

```python
def _adresse(pfad: Path, *, mit_marke: bool=False) -> str
```

Die Adresse einer Datei von der Seite aus, auf Wunsch mit ihrer Marke.

### versionsmarken_stimmen

```python
def versionsmarken_stimmen() -> bool
```

Ob die Marken in der Seite zu den Dateien passen, auf die sie zeigen.

### versionsmarken_schreiben

```python
def versionsmarken_schreiben(seite: Path | None=None) -> Path
```

Ersetzt die Marken in der Seite; alles ausserhalb der beiden Kommentare bleibt.

### _zerlegen

```python
def _zerlegen(seite: Path) -> Tuple[str, str, str]
```

Die Seite in drei Stuecke: bis und mit dem Anfangskommentar, die Marken,
ab dem Endkommentar. Fehlt ein Kommentar, bricht es ab -- still nichts zu
schreiben hiesse, die alten Marken blieben stehen.


## Konstanten

- `WURZEL = Path(__file__).resolve().parents[2]`
- `PAKET = WURZEL / 'opencivil'`
- `MANIFEST = WURZEL / 'web' / 'kern' / 'dateien.json'`
- `PYODIDE = WURZEL / 'web' / 'vendor' / 'pyodide'`
- `NOTIZBUCH = WURZEL / 'notizbuch'`
- `VERZEICHNIS = WURZEL / 'web' / 'kern' / 'notizbuch.json'`
- `SEITE = WURZEL / 'web' / 'index.html'`
- `STILBLATT = WURZEL / 'web' / 'css' / 'stil.css'`
- `ANFANG = '<!-- Versionsmarken: geschrieben von «python3 -m opencivil.web.bruec…`
- `ENDE = '<!-- Ende der Versionsmarken -->'`

## Braucht

- [[opencivil.notizbuch.erzeugen]]
- [[opencivil.notizbuch.tresor]]
