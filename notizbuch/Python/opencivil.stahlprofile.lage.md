---
erzeugt: 9539eda0a040
art: modul
tags: [modul]
---
> [!abstract] opencivil/stahlprofile/lage.py
> ein Stahlprofil im gezeichneten Querschnitt.
> Paket [[opencivil.stahlprofile]] · [Quelltext](../../opencivil/stahlprofile/lage.py)

## VERANTWORTUNG

Wo ein Profil der Tabelle oder aus Vollstahl in einer Querschnittsanalyse liegt
([[opencivil.stahlprofile.lage#Profillage|Profillage]]): aus seiner Mitte, seiner Drehung und ob es gespiegelt
ist, seine Umrisse in der Zeichnung und wie es in Bericht und Meldungen
heisst; ob Drehen oder Spiegeln es ueberhaupt aendert ([[opencivil.stahlprofile.lage#drehbar|drehbar]],
[[opencivil.stahlprofile.lage#spiegelbar|spiegelbar]]); woran der Zeiger faengt ([[opencivil.stahlprofile.lage#fangpunkte|fangpunkte]]); und seine
Skizze fuer das Fenster der Vorlagen ([[opencivil.stahlprofile.lage#skizze|skizze]]). Wohin seine Bleche
kommen, rechnet dieselbe Lage ([[opencivil.stahlprofile.bleche|bleche]]).


## DIE MITTE

Die Mitte des umschreibenden Rechtecks, in mm – nicht der Schwerpunkt, der
beim U neben ihr liegt. An ihr haengt das Profil in der Zeichnung (ein
Knoten), um sie dreht es sich. Ungedreht steht es wie in der Tabelle
([[opencivil.stahlprofile.formen|formen]]): der Steg senkrecht, beim U der
Ruecken links.


## DREHEN UND SPIEGELN

Erst gespiegelt, an der senkrechten Achse durch die Mitte – beim U ist der
Ruecken dann rechts –, danach gedreht um 0, 90, 180 oder 270 Grad gegen den
Uhrzeigersinn, mit y nach rechts und z nach oben. Ein U um 90 Grad ist
nach oben offen, ein I um 90 Grad liegt: der Steg waagrecht.


## GERECHNET WIRD MIT DEM UMRISS

Die Querschnittsanalyse rechnet mit dem Vieleck, nicht mit den Formeln der
Tabelle: Fasern, Schwerpunkt und Traegheitsmomente kommen aus ihm, wie bei
jeder gezeichneten Flaeche. Wie genau es die Tabelle trifft, steht bei
[[opencivil.stahlprofile.formen#Konstanten|BOGENECKEN]].

## Inhalt

### _lokal

```python
@lru_cache(maxsize=_GEMERKT)
def _lokal(name: str) -> Tuple[Tuple[Punkt, ...], ...]
```

Die Umrisse, wie die Form sie zeichnet – einmal je Profil: sein Name sagt seine Masse.

### _mitte_lokal

```python
@lru_cache(maxsize=_GEMERKT)
def _mitte_lokal(name: str) -> Punkt
```

Die Mitte des umschreibenden Rechtecks, wie die Form das Profil zeichnet.

### Profillage

```python
@dataclass(frozen=True)
class Profillage
```

Ein Profil, wie es im Querschnitt liegt: sein Name, seine Mitte in mm,
seine Drehung und ob es gespiegelt ist – siehe Dateikopf. Einen Namen,
der nicht geht, sagt ein `KeyError`, sobald etwas gerechnet wird
([[opencivil.stahlprofile.tabelle#profil|profil]]).

- `name: str`
- `mitte: Punkt = (0.0, 0.0)`
- `drehung: int = 0`
- `gespiegelt: bool = False`

#### Profillage.setzen

```python
def setzen(self, p: Punkt) -> Punkt
```

Ein Punkt, wie die Form das Profil zeichnet, an seiner Stelle in der Zeichnung.

#### Profillage.richtung

```python
def richtung(self, wort: str) -> str
```

Wohin «oben», «unten», «links» oder «rechts» der Form in der Zeichnung zeigt.

#### Profillage.umrisse

```python
@property
def umrisse(self) -> List[List[Punkt]]
```

Die Umrisse in der Zeichnung, in mm: der erste aussen, die weiteren Loecher – beim Rohr eines.

#### Profillage.beschreibung

```python
@property
def beschreibung(self) -> str
```

Was das Profil ist, fuer Bericht und Liste: «UPE 200, gespiegelt, um
90° gedreht» – nur, was etwas aendert: ein gespiegeltes I heisst wie
jedes.

### _gleich

```python
def _gleich(a: Sequence[Sequence[Punkt]], b: Sequence[Sequence[Punkt]]) -> bool
```

Ob zwei Umrisse dieselben Ecken haben, auf einen Hundertstel Millimeter – gleich in welcher Folge.

### drehbar

```python
@lru_cache(maxsize=_GEMERKT)
def drehbar(name: str) -> bool
```

Ob eine Drehung um 90 Grad das Profil aendert – beim Rundrohr nicht, beim quadratischen Rohr auch nicht.

### spiegelbar

```python
@lru_cache(maxsize=_GEMERKT)
def spiegelbar(name: str) -> bool
```

Ob das Spiegeln das Profil aendert – nur, wenn es zur senkrechten Achse nicht symmetrisch ist, wie das U.

### fangpunkte

```python
def fangpunkte(teile: Sequence[Sequence[Punkt]]) -> List[Punkt]
```

Woran der Zeiger am Profil faengt: die Ecken des umschreibenden
Rechtecks und die Mitten seiner Seiten – beim I die Spitzen und Mitten
der Flansche, so legt sich eine Platte auf den Obergurt.

### _aussen

```python
def _aussen(profil: tabelle.Profil) -> Tuple[str, ...]
```

Welche Masse die Skizze zeigt: bei Vollstahl die frei eingegebenen –
beim Vierkant nur `a` –, beim Rundrohr `D`, sonst `b` und `h`.

### skizze

```python
def skizze(name: str, drehung: int=0, gespiegelt: bool=False) -> Teile
```

Das Profil fuer das Fenster der Vorlagen: seine Umrisse um seine Mitte
– nicht von unten links wie die Teile der anderen Vorlagen: die Mitte
kommt an den Einsetzpunkt – und die Masse, die es von aussen hat
([[opencivil.stahlprofile.lage#_aussen|_aussen]]), Breite unten, Hoehe links, nach der Drehung; ein
einziges steht unten.


## Konstanten

- `IM_BERICHT = 'Ein Stahlprofil zählt mit seinem Umriss: die Ausrundungen als Vielec…` – Was der Bericht zu einem Profil sagt, unter dem Satz zu den Polygonen ([[opencivil.querschnitt.analyse#Querschnittsanalyse.aufbau_protokollieren|aufbau_protokollieren]]). Ein halbes Prozent gegen die Formeln der Formen: so weit liegt das UNP mit I_z daneben (0.44 %), die anderen Reihen trifft der Umriss auf 0.33 % ([[opencivil.stahlprofile.formen#Konstanten|BOGENECKEN]]). Gegen die Werte der Tabelle des Benutzers ist es beim UNP bis 0.9 %: dort sind sie von Hand eingetippt, mit drei Stellen (tests/test_stahlprofile.py).
- `VORLAGE = 'stahlprofil'` – Unter diesem Schluessel steht das Profil bei den Vorlagen des Zeichenfensters: es setzt ein Profil ein, keine Flaeche (Plan vom 2026-11-25, Schritt 11).
- `DREHUNGEN = (0, 90, 180, 270)` – Um so viele Grad gegen den Uhrzeigersinn laesst sich ein Profil drehen.
- `_DREHUNG = {0: (1, 0), 90: (0, 1), 180: (-1, 0), 270: (0, -1)}` – cos und sin je Drehung – genau, ohne Rundungsrest der Winkelfunktionen.
- `_RICHTUNGEN = {'oben': (0, 1), 'unten': (0, -1), 'links': (-1, 0), 'rechts': (1, 0)}` – Die vier Richtungen der Zeichnung, als Einheitsvektor – so heisst ein Blech nach seiner Lage, auch am gedrehten Profil ([[opencivil.stahlprofile.lage#Profillage.richtung|Profillage.richtung]]).
- `_STELLEN = 6` – Auf so viele Stellen nach dem Komma in mm liegen die Ecken – wie beim Einsetzen einer Vorlage, damit die Summe keinen Rundungsrest behaelt.
- `_GEMERKT = 4096` – So viele Profile behaelt jeder Speicher unten – die der Tabelle alle, dazu die frei eingegebenen aus Vollstahl, deren Zahl offen ist.

## Braucht

- [[opencivil.querschnitt.vorlagen]]
- [[opencivil.stahlprofile.tabelle]]

## Gebraucht von

- [[opencivil.projekt.profile]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.stahlbau.schub]]
- [[opencivil.stahlbau.stabilitaet]]
- [[opencivil.stahlprofile.bleche]]
- [[opencivil.web.api]]
- [[opencivil.web.dienst]]
- [[opencivil.web.zeichengeometrie]]
