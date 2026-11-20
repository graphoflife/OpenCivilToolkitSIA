---
erzeugt: 4233fdd613b6
art: modul
tags: [modul]
---
> [!abstract] opencivil/web/bruecke.py
> Welche Dateien der Browser laden muss.
> Paket [[opencivil.web]] · [Quelltext](../../opencivil/web/bruecke.py)

## VERANTWORTUNG

Fuehrt Buch darueber, aus welchen Quelldateien der Rechenkern besteht, und
schreibt diese Liste nach `web/kern/dateien.json` -- dazu alle Dateien in
einem Stueck nach `web/kern/quellen.json`. Der Faden in
`web/js/kern_arbeiter.js` holt das Paket und legt jede Datei darin ins
Dateisystem von Pyodide -- danach ist `import opencivil` im Browser
dasselbe wie auf dem Rechner.


## EIN PAKET STATT 214 DATEIEN

Bis 2026-11-20 holte der Browser jede Datei fuer sich, nach der Liste. Auf
GitHub Pages kostet jede Anfrage ihre Zeit, und ein paar hundert laufen
nicht alle zugleich; jetzt ist es eine. Das Paket ist ein zweites, erzeugtes
Abbild des Quellcodes im Repo -- und damit etwas, das unbemerkt veralten
kann: [[opencivil.web.bruecke#quellen_stimmen|quellen_stimmen]] prueft im Test, dass es zu den vorhandenen
Dateien passt. Veraltet es, schlaegt der Test an, nicht erst die
veroeffentlichte Seite. Es ist Text und kein Archiv, JSON von Pfad zu
Inhalt: Git speichert davon nur, was sich aendert, und GitHub komprimiert
es beim Senden. Im Diff zeigt Git es nicht (`.gitattributes`) -- was sich
darin aendert, steht schon im Diff der Quelle.


## JE DATEI EINE MARKE

Neben jedem Pfad steht in der Liste seine Marke, die ersten zwoelf Zeichen
von SHA-256 ueber den Inhalt: ihr Diff zeigt, welche Kerndatei sich
aenderte, und der Test merkt, wenn das Neuschreiben vergessen ging. Das
Paket hat seine eigene Marke, in der Importtafel der Seite (unten): ein
geaenderter Kern hat damit eine neue Adresse, und aus dem Zwischenspeicher
kommt kein alter mehr. Ein schlichter statischer Server ohne Cache-Angabe
laesst den Browser nach Gefuehl zwischenspeichern -- so kam einmal
`blatt.py` nach einer Aenderung noch alt.


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
unter `web/js/`, fuer das Paket und fuer das Verzeichnis des Notizbuchs
die Adresse mit Marke, dazu die Stilblaetter mit Marke. Die Module selbst bleiben, wie sie sind
-- `import './dom.js'` fuehrt ueber die Tafel auf `./dom.js?v=Marke`.
So haengt alles an der Seite: wer sie neu laedt, bekommt den Rest im selben
Stand. Ohne Marke bleiben nur die Fremdbibliotheken unter `web/vendor/`;
die aendern sich nur, wenn jemand bewusst eine neue Fassung einlegt.


## UND OHNE NETZ

Der Service Worker `sw.js` legt in einen Speicher des Browsers, was die
Seite zum Starten braucht; danach geht sie auch ohne Netz auf. Er liegt im
Wurzelverzeichnis, damit er auch die Wurzel abdeckt, die veroeffentlichte
Adresse. Was in den Speicher gehoert, schreibt die Bruecke in ihn hinein wie
die Marken in die Seite ([[opencivil.web.bruecke#vorrat|vorrat]]): alles mit Marke, und je Ordner
unter `web/vendor/` dessen Dateien, mit einer Marke ueber den ganzen
Ordner ([[opencivil.web.bruecke#fremdmarke|fremdmarke]]). Aendert sich etwas, aendert sich `sw.js`,
und der Browser installiert ihn neu. Ohne diese Liste muesste er raten, was
die Seite gleich braucht -- und ohne Netz fehlte, was er beim ersten Besuch
nicht gesehen hat.


## UND DIE FREMDPAKETE

Im Manifest steht auch, welche Fremdpakete unter `web/vendor/pyodide/`
beiliegen ([[opencivil.web.bruecke#mitgelieferte_pakete|mitgelieferte_pakete]]): Importname -> Paketname, gelesen aus
den Dateien, die dort liegen, und aus `pyodide-lock.json`. Die App «Python»
laedt nur diese ([[opencivil.konsole.pakete]]). Eine zweite, von Hand
gefuehrte Liste gibt es nicht: was `werkzeug/pyodide_holen.py` hinlegt,
steht nach dem naechsten Lauf der Bruecke im Manifest. Darum liegt das
Manifest auch im Paket, an seinem Platz neben `opencivil/`: die Konsole
liest es im Browser wie auf dem Rechner.


## WARUM ALLE DATEIEN UND NICHT NUR DIE GEBRAUCHTEN

Man koennte die Liste auf das beschraenken, was [[opencivil.web.dienst]]
einbindet. Dann muesste die Regel aber bei jeder neuen Einbindung nachgezogen
werden, und wer das vergisst, merkt es erst im Browser. Ein paar Dutzend
Kilobyte sind der bessere Handel.


## AUFRUF


```
python3 -m opencivil.web.bruecke    # schreibt web/kern/, die Marken in web/index.html und sw.js
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

### quellen

```python
def quellen() -> dict
```

Das Paket fuer den Browser: Pfad -> Inhalt, fuer jede Datei von
[[opencivil.web.bruecke#kerndateien|kerndateien]] und fuer das Manifest -- was der Faden ins
Dateisystem von Pyodide legt, so wie es im Repo liegt.

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

### quellen_stimmen

```python
def quellen_stimmen() -> bool
```

Ob das abgelegte Paket den vorhandenen Dateien entspricht, Zeichen fuer Zeichen.

### quellen_schreiben

```python
def quellen_schreiben(pfad: Path | None=None) -> Path
```

Schreibt das Paket -- nach dem Manifest, das darin liegt.

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

### stilblaetter

```python
def stilblaetter() -> List[Path]
```

Die Blaetter des Stils in der Reihenfolge ihrer Nummern -- so bindet die
Seite sie ein, und so gelten sie: bei gleicher Spezifitaet gewinnt die
Regel im spaeteren Blatt.

### tafeldateien

```python
def tafeldateien() -> List[Path]
```

Was ueber die Importtafel der Seite geht: jedes Modul der Oberflaeche, das
Paket des Kerns und das Verzeichnis des Notizbuchs.

### versionsmarken

```python
def versionsmarken() -> str
```

Was in der Seite zwischen [[opencivil.web.bruecke#Konstanten|ANFANG]] und [[opencivil.web.bruecke#Konstanten|ENDE]] steht: die
Stilblaetter und die Importtafel, jede Adresse mit der Marke ihrer Datei.

### _adresse

```python
def _adresse(pfad: Path, *, mit_marke: bool=False, von: Path | None=None) -> str
```

Die Adresse einer Datei von der Seite aus, auf Wunsch mit ihrer Marke --
oder mit `von` vom Service Worker aus, ohne `./`.

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

### vorrat

```python
def vorrat() -> dict
```

Was der Service Worker in seinen Speicher legt, damit die Seite auch ohne
Netz startet -- Pfade von der Wurzel aus:

- `seiten`: [[opencivil.web.bruecke#Konstanten|SEITEN]], die er zuerst aus dem Netz holt;
- `dateien`: die Stilblaetter und alles ueber die Importtafel, mit Marke;
- `fremd`: je Ordner unter `web/vendor/` seine Marke und seine
  Dateien -- ohne die Pakete der Konsole (`.whl`): numpy und pandas
  holt er erst, wenn ein Skript sie braucht.

### fremdmarke

```python
def fremdmarke(ordner: Path) -> str
```

Die Marke eines Ordners unter `web/vendor/`: die ersten zwoelf Zeichen
von SHA-256 ueber Namen und Inhalt jeder Datei darin, ausser den
Erlaeuterungen. Eine neue Fassung von Pyodide gibt eine neue Marke, also
einen neuen Speicher; eine Veroeffentlichung, die ihn nicht anruehrt,
laesst die 13 MB liegen.

### vorrat_marken

```python
def vorrat_marken() -> str
```

Was im Service Worker zwischen [[opencivil.web.bruecke#Konstanten|SW_ANFANG]] und [[opencivil.web.bruecke#Konstanten|SW_ENDE]] steht.

### vorrat_stimmt

```python
def vorrat_stimmt() -> bool
```

Ob der Vorrat im Service Worker zu den Dateien passt.

### vorrat_schreiben

```python
def vorrat_schreiben(datei: Path | None=None) -> Path
```

Ersetzt den Vorrat im Service Worker; alles ausserhalb der beiden Kommentare bleibt.

### _zerlegen

```python
def _zerlegen(datei: Path, anfang: str, ende: str) -> Tuple[str, str, str]
```

Die Datei in drei Stuecke: bis und mit dem Anfangskommentar, die Marken,
ab dem Endkommentar. Fehlt ein Kommentar, bricht es ab -- still nichts zu
schreiben hiesse, die alten Marken blieben stehen.


## Konstanten

- `WURZEL = Path(__file__).resolve().parents[2]`
- `PAKET = WURZEL / 'opencivil'`
- `MANIFEST = WURZEL / 'web' / 'kern' / 'dateien.json'`
- `QUELLEN = WURZEL / 'web' / 'kern' / 'quellen.json'`
- `PYODIDE = WURZEL / 'web' / 'vendor' / 'pyodide'`
- `NOTIZBUCH = WURZEL / 'notizbuch'`
- `VERZEICHNIS = WURZEL / 'web' / 'kern' / 'notizbuch.json'`
- `SEITE = WURZEL / 'web' / 'index.html'`
- `STIL = WURZEL / 'web' / 'css'`
- `SW = WURZEL / 'sw.js'`
- `FREMD = WURZEL / 'web' / 'vendor'`
- `SEITEN = ('./', 'web/', 'web/manifest.webmanifest', 'web/favicon.svg')` – Was der Service Worker zuerst aus dem Netz holt und nur ohne Netz aus seinem Speicher: die Seiten, in denen die Marken stehen, und was keine traegt. Der Rest des Vorrats kommt aus [[opencivil.web.bruecke#vorrat|vorrat]].
- `ERLAEUTERUNGEN = ('.md', '.txt')` – Was unter `web/vendor/` nur erlaeutert: nicht im Speicher, nicht in der Marke.
- `_MARKEN = 'Versionsmarken: geschrieben von «python3 -m opencivil.web.bruecke», …`
- `ANFANG = f'<!-- {_MARKEN} -->'`
- `ENDE = '<!-- Ende der Versionsmarken -->'`
- `SW_ANFANG = f'// {_MARKEN}'`
- `SW_ENDE = '// Ende der Versionsmarken'`
- `HINWEIS = "Erzeugt von opencivil/web/bruecke.py. Nicht von Hand ändern -- nach …` – Was in der Liste und im Paket obenan steht.

## Braucht

- [[opencivil.notizbuch.erzeugen]]
- [[opencivil.notizbuch.tresor]]
