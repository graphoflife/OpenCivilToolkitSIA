---
erzeugt: c821fbe92eff
art: modul
tags: [modul]
---
> [!abstract] opencivil/notizbuch/tresor.py
> erzeugte Seiten in den Ordner `notizbuch/`.
> Paket [[opencivil.notizbuch]] · [Quelltext](../../opencivil/notizbuch/tresor.py)

## VERANTWORTUNG

Schreibt die Seiten, die aus dem Code entstehen, in den Tresor -- so, dass
nichts verloren geht, was von Hand dazukam. Und fuehrt das Verzeichnis, aus
dem die Oberflaeche erfaehrt, welche Seiten es gibt.


## AUFBAU EINER ERZEUGTEN SEITE


```
---
erzeugt: 3f9a1c0b7d2e
art: formel
tags: [formel]
---
der erzeugte Teil
<!-- Ab hier von Hand: … -->            (die Linie, siehe LINIE)
der eigene Teil, von Hand
```

`erzeugt` ist die Pruefsumme ueber alles bis und mit der Linie, ohne die
eigene Zeile. Beim Neuerzeugen wird nur dieser Teil ersetzt; der eigene Teil
bleibt Zeichen fuer Zeichen. Seiten ohne eigenen Teil -- Modul- und
Verzeichnisseiten -- haben keine Linie: sie sind ganz erzeugt.


## WER WAS ANFASSEN DARF

Dem Generator gehoeren nur Dateien mit `erzeugt:`. Eine Notiz ohne, wo
immer sie liegt, bleibt unberuehrt. Hat jemand oben in einer erzeugten Seite
etwas geaendert -- getippt, oder in Obsidian umbenannt, das die Links
nachfuehrt --, stimmt die Pruefsumme nicht mehr: dann schreibt der Generator
gar nichts und nennt die Dateien. Raten, was davon bleiben soll, waere
schlimmer.


## ZWEI PHASEN

Erst wird geplant und geprueft ([[opencivil.notizbuch.tresor#planen|planen]]), dann geschrieben
([[opencivil.notizbuch.tresor#ausfuehren|ausfuehren]]). Ein Fehler in der dritten Datei laesst so nicht zwei
neue und eine alte zurueck.


## VERWAIST

Gibt es eine Formel nicht mehr, gibt es ihre Seite nicht mehr -- es sei denn,
unter der Linie steht etwas. Dann bleibt die Seite stehen, oben mit einem
Hinweis, bis der Text an der richtigen Seite steht; ein Test haelt das fest.

## Inhalt

### TresorFehler

```python
class TresorFehler(Exception)
```

Der Generator wuerde etwas ueberschreiben, das ihm nicht gehoert.

### Seite

```python
@dataclass(frozen=True)
class Seite
```

Eine erzeugte Seite, bevor sie geschrieben ist.

- `pfad: str` – Im Tresor, mit `/` getrennt: `Formelsammlung/Formeln/Statische Höhe.md`.
- `art: str` – `formel`, `thema`, `verzeichnis` oder `modul`.
- `rumpf: str` – Der erzeugte Teil, ohne Kopf und ohne Linie.
- `eigenschaften: Tuple[Tuple[str, Any], ...] = ()` – Weitere Eintraege des Kopfs, in dieser Folge -- Text oder Liste von Texten.
- `eigener_teil: bool = False` – Ob unter einer Linie von Hand weitergeschrieben wird.
- `rang: int = 0` – Wo die Seite im Verzeichnis steht, innerhalb ihres Ordners.
- `verzeichnis: Tuple[Tuple[str, Any], ...] = ()` – Was das Verzeichnis zusaetzlich ueber die Seite weiss: Zeichen, Themen ...

#### Seite.name

```python
@property
def name(self) -> str
```

### Datei

```python
@dataclass
class Datei
```

Eine Seite, wie sie im Tresor liegt.

- `erzeugt: Optional[str]` – Die abgelegte Pruefsumme -- `None` bei einer Notiz von Hand.
- `stimmt: bool` – Ob die Pruefsumme zum Inhalt passt.
- `eigen: Optional[str]` – Alles nach der Linie, oder `None`, wenn es keine gibt.
- `eigenschaften: Dict[str, str] = field(default_factory=dict)`

### Plan

```python
@dataclass
class Plan
```

Was ein Lauf des Generators taete.

- `schreiben: Dict[str, str] = field(default_factory=dict)`
- `loeschen: List[str] = field(default_factory=list)`
- `verwaist: List[str] = field(default_factory=list)`
- `unveraendert: List[str] = field(default_factory=list)`
- `fehler: List[str] = field(default_factory=list)`

#### Plan.nichts_zu_tun

```python
@property
def nichts_zu_tun(self) -> bool
```

### pruefsumme

```python
def pruefsumme(text: str) -> str
```

Die ersten zwoelf Zeichen von SHA-256, Windows-Zeilenenden zaehlen nicht.

### _wert

```python
def _wert(wert: Any) -> str
```

Ein Eintrag im Kopf, wie Obsidian ihn als Eigenschaft liest. Text in
Anfuehrungszeichen, sobald er mehr als Buchstaben enthaelt: ein `:` mit
Leerzeichen danach oder ein `#` hiesse sonst etwas anderes.

### text_der_seite

```python
def text_der_seite(seite: Seite, eigen: str='') -> str
```

Die Datei, wie sie geschrieben wird -- mit dem eigenen Teil, wo es einen
gibt. Die Linie darf sonst nirgends stehen, auch nicht in einem
Codeblock: wer die Datei liest, hielte sie fuer die Grenze.

### zerlegen

```python
def zerlegen(text: str) -> Datei
```

Liest Kopf, Pruefsumme und eigenen Teil einer Datei aus dem Tresor.

### vorhandene

```python
def vorhandene(wurzel: Path) -> Dict[str, str]
```

Jede Markdown-Datei im Tresor, ohne die Arbeitsdateien von Obsidian.

### planen

```python
def planen(seiten: Sequence[Seite], wurzel: Path) -> Plan
```

Was zu schreiben, zu loeschen und zu beanstanden waere -- ohne etwas anzufassen.

### ausfuehren

```python
def ausfuehren(plan: Plan, wurzel: Path) -> None
```

Schreibt und loescht, was der Plan sagt -- nur, wenn er nichts beanstandet.

### verzeichnis

```python
def verzeichnis(seiten: Sequence[Seite], wurzel: Path) -> List[Dict[str, Any]]
```

Jede Seite des Tresors, erzeugt oder von Hand, in der Folge des Baums:
Start, Formelsammlung (Uebersicht, Themen in Rechenfolge, Formeln von A
bis Z), Python, Notizen, dann alles andere. Eine Ordnerseite -- sie heisst
wie ihr Ordner -- steht vor den uebrigen.

### anhaenge

```python
def anhaenge(wurzel: Path) -> List[str]
```

Was ausser Seiten im Tresor liegt -- Bilder, die eine Seite einbettet.


## Konstanten

- `LINIE = '<!-- Ab hier von Hand: bleibt beim Neuerzeugen erhalten -->'` – Die Linie zwischen erzeugtem und eigenem Teil -- in Obsidian und auf der Seite unsichtbar, im Quelltext unuebersehbar.
- `ORDNER = ('', 'Formelsammlung', 'Formelsammlung/Themen', 'Formelsammlung/Forme…` – Die Ordner in der Reihenfolge, in der das Verzeichnis sie fuehrt.
- `_VERBORGEN = re.compile('(^|/)\\.')` – Was im Tresor kein Inhalt ist: die Arbeitsdateien von Obsidian.

## Braucht

- [[opencivil.notizbuch.namen]]

## Gebraucht von

- [[opencivil.notizbuch.bibliothek]]
- [[opencivil.notizbuch.erzeugen]]
- [[opencivil.notizbuch.formelseiten]]
- [[opencivil.web.bruecke]]
