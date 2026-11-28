---
erzeugt: e5c740f60092
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/aufbau/aus_system.py
> die Lastfaelle einer Querschnittsanalyse aus einem Balkensystem.
> Paket [[opencivil.projekt.aufbau]] · [Quelltext](../../opencivil/projekt/aufbau/aus_system.py)

## VERANTWORTUNG

Was eine Analyse aus ihrem Balkensystem nimmt
([[opencivil.projekt.aus_system#AusSystemEintrag|AusSystemEintrag]]), wird hier zu
Lastfaellen ([[opencivil.projekt.aufbau.aus_system#aus_dem_system|aus_dem_system]]): das System gerechnet, je Kombination
die massgebenden Stellen ihrer Staebe
([[opencivil.stabwerk.stellen#massgebende_stellen|massgebende_stellen]]), jede als
Lastfall der Analyse, dazu die Herleitung. Das geht erst, wenn alle
Balkensysteme gebaut sind – darum baut die Analyse ihre Nachweise im
zweiten Gang des Aufbaus ([[opencivil.projekt.aufbau#Bauteilart|danach]]).


## KEIN KREIS

Das System liest die Werte der Analyse – Flaeche und Traegheitsmomente,
auch wenn seine Staebe genau diese Analyse als Querschnitt haben –, die
Nachweise der Analyse lesen die Stellen des Systems. Die Werte haengen an
der Zeichnung, nicht an den Lastfaellen: erst rechnet das System mit den
Werten, dann laufen die Nachweise.


## OHNE STELLEN

Gibt es das System nicht mehr, rechnet es nicht, hat es keine Kombination
oder keinen der Staebe, sagt es ein grauer Satz an der Analyse
([[opencivil.projekt.aufbau.aus_system#AusDemSystem|AusDemSystem.ohne]]) – sie rechnet mit ihren eigenen Lastfaellen
weiter. Ein unfertiger Zustand ist kein Fehler (Benutzer, 2026-11-19).
Ebenso ein gewaehlter Stab, der im System keiner mehr ist
([[opencivil.projekt.aufbau.aus_system#AusDemSystem|AusDemSystem.fehlen]]): wer auf eine geloeschte Kennung zeigt, sagt
es am Ort (Benutzer, 2026-11-19).

## Inhalt

### AusDemSystem

```python
@dataclass
class AusDemSystem
```

Was eine Analyse aus ihrem Balkensystem nahm – oder warum nichts.

- `system: str` – Sein Name – wie ihn die Liste der Balkensysteme zeigt; leer, wenn es das System nicht mehr gibt.
- `wahl: Stabwahl`
- `staebe: List[str] = field(default_factory=list)` – Die Kennungen der Linien, die zaehlen, in der Folge des Systems.
- `fehlen: List[str] = field(default_factory=list)` – Gewaehlte Linien, die im System kein Stab mehr sind – geloescht oder ohne Querschnitt.
- `kandidaten: List[Tuple[str, str]] = field(default_factory=list)` – Was sich im System waehlen laesst: je Stab seine Kennung und der Name seines Querschnitts.
- `stellen: List[Tuple[str, Stelle]] = field(default_factory=list)` – Je Stelle ihr Name als Lastfall – eindeutig in der Analyse.
- `ohne: str = ''` – Warum es keine Stelle gibt, ein Satz – leer, wenn es welche gibt.

#### AusDemSystem.hinweise

```python
@property
def hinweise(self) -> List[str]
```

Was grau an der Analyse steht, je ein Satz: warum es keine Stelle gibt, was fehlt.

#### AusDemSystem.lastfaelle

```python
@property
def lastfaelle(self) -> List[QALastfallEintrag]
```

Die Stellen als Lastfaelle der Analyse, in kN und kNm.

#### AusDemSystem.herleitung

```python
def herleitung(self, id: str, schwerpunkt: Tuple[str, str], **angaben: Any) -> Stellenherleitung
```

Ihre Herleitung, als Prozedur ohne Ausgabe
([[opencivil.stabwerk.stellen#Stellenherleitung|Stellenherleitung]]) – `schwerpunkt`
die Wert-IDs von `y_S` und `z_S` der Analyse.

### aus_dem_system

```python
def aus_dem_system(eintrag: QuerschnittsanalyseEintrag, aufbau: Aufbau) -> Optional[AusDemSystem]
```

Was die Analyse `eintrag` aus ihrem Balkensystem nimmt – `None`
ohne System. Siehe Dateikopf.

### _staebe

```python
def _staebe(eintrag: QuerschnittsanalyseEintrag, system: Any) -> Tuple[List[str], List[str]]
```

Die Staebe, die zaehlen, in der Folge des Systems – und gewaehlte, die
es dort nicht mehr gibt oder die keinen Querschnitt haben, in der Folge
der Wahl.

### _benannt

```python
def _benannt(stellen: List[Stelle], vergeben: List[str]) -> List[Tuple[str, Stelle]]
```

Je Stelle ihr Name als Lastfall. Die Nachweise fuehren einen Lastfall
unter der Kennung seines Namens ([[opencivil.core.wert#kennung_aus|kennung_aus]]);
gaebe es die schon, bekommt er eine Nummer dazu.


## Konstanten

- `_WAHL = {Stabwahl.MIT_QUERSCHNITT: 'die Stäbe mit dieser Querschnittsanalyse …` – Wie die Herleitung die Wahl der Staebe nennt.

## Braucht

- [[opencivil.core.sprache]]
- [[opencivil.core.wert]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.aus_system]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.projekt.staebe]]
- [[opencivil.stabwerk.stellen]]

## Gebraucht von

- [[opencivil.projekt.aufbau.querschnittsanalyse]]
