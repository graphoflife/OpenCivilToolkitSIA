---
erzeugt: 33668191c858
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/projekt.py
> das Projekt als Ganzes.
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/projekt.py)

## VERANTWORTUNG

Das [[opencivil.projekt.projekt#Projekt|Projekt]] haelt Materialien und Bauteile zusammen und ist das, was
gespeichert, geoeffnet und gerechnet wird. Hier stehen der Zugriff auf die
Teile, die Methoden fuer das Rechnen ohne Oberflaeche, die Pruefungen ueber
mehrere Teile hinweg (eindeutige Namen, Anteile), Speichern und Laden -- und
das Beispiel, mit dem die Oberflaeche startet.

Gebaut wird in [[opencivil.projekt.aufbau]]; [[opencivil.projekt.projekt#Projekt.aufbauen|Projekt.aufbauen]]
reicht nur weiter.

## Inhalt

### Projekt

```python
@dataclass
class Projekt(Beschreibung)
```

Die vollstaendige, speicherbare Beschreibung eines Projekts.

- `name: str = 'Neues Projekt'`
- `materialien: List[MaterialEintrag] = field(default_factory=list)`
- `querschnitte: List[QuerschnittEintrag] = field(default_factory=list)`
- `querschnittsanalysen: List[QuerschnittsanalyseEintrag] = field(default_factory=list)` – Gezeichnete Querschnitte: Polygone, Bewehrung, Schubwände.
- `balkensysteme: List[BalkensystemEintrag] = field(default_factory=list)` – Ebene Rahmen: Knoten, Stäbe, Lager, Lasten, Lastfälle.
- `grundbrueche: List[GrundbruchEintrag] = field(default_factory=list)` – Flachfundamente mit Grundbruch und Gleiten.
- `skripte: List[SkriptEintrag] = field(default_factory=list)` – Die Python-Skripte der App «Python» -- gespeichert, nicht gerechnet.

#### Projekt.material

```python
def material(self, kennung: str) -> MaterialEintrag
```

#### Projekt.querschnitt

```python
def querschnitt(self, kennung: str) -> QuerschnittEintrag
```

#### Projekt.querschnittsanalyse

```python
def querschnittsanalyse(self, kennung: str) -> QuerschnittsanalyseEintrag
```

#### Projekt.bauteile

```python
def bauteile(self) -> List[Any]
```

Alle Bauteile in der Reihenfolge der Beschreibung -- siehe [[opencivil.projekt.aufbau#Konstanten|BAUTEILE]].

#### Projekt.nur

```python
def nur(self, kennung: str) -> 'Projekt'
```

Eine Kopie, in der von den Bauteilen nur dieses eine steht --
die Materialien bleiben. So rechnet die Bewehrungssuche: die
anderen Bauteile kann sie nicht beeinflussen, und ihre Urteile
zaehlten sonst mit.

#### Projekt.bauteil

```python
def bauteil(self, kennung: str) -> Any
```

Ein Bauteil gleich welcher Art -- eine Platte, eine Analyse, ein System.

#### Projekt.freie_kennung

```python
def freie_kennung(self, vorsilbe: str) -> str
```

#### Projekt.eigener_name

```python
def eigener_name(self, art: str) -> str
```

Der erste freie Name eines eigenen Materials: BE1, BE2 ... oder S1 ...

#### Projekt.beton

```python
def beton(self, sorte: str='C30/37') -> MaterialEintrag
```

Eine Betonsorte nach Norm -- Kennung `b1`, `b2` ...

#### Projekt.stahl

```python
def stahl(self, sorte: str='B500B') -> MaterialEintrag
```

Eine Betonstahlsorte nach Norm -- Kennung `s1`, `s2` ...

#### Projekt.eigener_beton

```python
def eigener_beton(self, vorlage: str='C30/37') -> MaterialEintrag
```

Ein eigener Beton, `BE1`, `BE2` ... -- mit den Kennwerten der Sorte
`vorlage`, abzuaendern ueber `abweichungen` und
`ueberschreibungen`. Eine Normsorte selbst bleibt, wie sie ist.

#### Projekt.eigener_stahl

```python
def eigener_stahl(self, vorlage: str='B500B') -> MaterialEintrag
```

Ein eigener Betonstahl, `S1`, `S2` ... -- siehe [[opencivil.projekt.projekt#Projekt.eigener_beton|eigener_beton]].

#### Projekt._normsorte

```python
def _normsorte(self, art: str, vorsilbe: str, sorte: str) -> MaterialEintrag
```

Legt eine Normsorte an und prueft sie sofort.

Sofort und nicht erst beim Rechnen: ein Tippfehler in der Sorte soll
an der Zeile auffallen, in der er steht.

#### Projekt.platte

```python
def platte(self, name: str, *, h: float=300.0, x: Sequence[float]=(12.0, 12.0), y: Sequence[float]=(12.0, 12.0), x_zulage: Sequence[float]=(0.0, 0.0), y_zulage: Sequence[float]=(0.0, 0.0), teilung: float=150.0, x_innen: bool=True, beton: Union[str, MaterialEintrag, None]=None, stahl: Union[str, MaterialEintrag, None]=None, **felder: Any) -> QuerschnittEintrag
```

Eine Platte -- Masse in mm, Bewehrung als Durchmesser je Richtung.

`x` und `y` sind je zwei Durchmesser, *unten* und *oben*;
`x_zulage` und `y_zulage` ebenso, null heisst keine. Alle Posten
liegen in derselben `teilung`. `x_innen` legt die Tragrichtung
auf die 2. und 3. Lage, wie die Vorgabe der Oberflaeche.

`beton` und `stahl` duerfen fehlen, solange das Projekt nur je
einen hat. Alles Weitere -- `b`, `rissanforderung`,
`duktilitaet` ... -- geht als Stichwort an den Eintrag; ein
unbekanntes Stichwort wird gemeldet, statt still zu verschwinden.

Gebaut wird ueber [[opencivil.projekt.platte#QuerschnittEintrag.neu|QuerschnittEintrag.neu]], dieselbe Vorlage wie
in der Oberflaeche, nur ohne deren Startlast: wer rechnet, gibt seine
Einwirkungen selbst an.

#### Projekt.analyse

```python
def analyse(self, name: str, *, beton: Union[str, MaterialEintrag, None]=None, stahl: Union[str, MaterialEintrag, None]=None, **felder: Any) -> QuerschnittsanalyseEintrag
```

Eine Querschnittsanalyse -- wie in der Oberflaeche ein Rechteck
300 × 600 mm mit drei Staeben unten und zwei oben, aber ohne
Startlast: wer rechnet, gibt seine Lastfaelle selbst an.

Gezeichnet wird danach mit dem Baukasten des Eintrags --
`polygon`, `stab`, `stablinie`, `schubwand`, `hilfslinie`,
Masse in mm. Wie bei [[opencivil.projekt.projekt#Projekt.platte|platte]] geht alles Weitere als Stichwort
an den Eintrag.

#### Projekt.balkensystem

```python
def balkensystem(self, name: str, **felder: Any) -> BalkensystemEintrag
```

Ein leeres Balkensystem, ein ebener Rahmen. Gezeichnet wird danach
mit dem Baukasten des Eintrags -- `querschnitt`, `linie`,
`lager_an`, `lastfall`, `stablast`, `knotenlast`,
`kombination` --, Koordinaten in m. Leer und nicht wie in der
Oberflaeche mit einem Einfeldtraeger: wer in Python zeichnet, zeichnet
sein eigenes System.

#### Projekt.grundbruch

```python
def grundbruch(self, name: str, **felder: Any) -> GrundbruchEintrag
```

Ein Grundbruchnachweis mit den Vorgaben der Oberflaeche, aber ohne
ihre Startkombination: wer rechnet, gibt seine Einwirkungen mit
`kombination` selbst an. Alles Weitere -- `phi_k`, `b`, `t` ...
-- geht als Stichwort an den Eintrag; Winkel in Grad, Masse in m,
Spannungen in kPa.

#### Projekt.skript

```python
def skript(self, name: str, code: str='') -> SkriptEintrag
```

Ein Python-Skript für die App «Python» -- Kennung `p1`, `p2` ...
Ausgeführt wird es in der Konsole der Oberfläche, nicht hier.

#### Projekt._einziges

```python
def _einziges(self, art: str, gewaehlt: Union[str, MaterialEintrag, None]) -> str
```

Die Kennung des gewaehlten Materials -- oder des einzigen dieser Art.

#### Projekt.rechnen

```python
def rechnen(self) -> Ergebnis
```

Alles rechnen, was die Oberflaeche auch rechnet -- ohne sie.

Dieselben Ziele in derselben Reihenfolge ([[opencivil.projekt.aufbau#Aufbau.alle_ziele|Aufbau.alle_ziele]]),
also derselbe Bericht. Ohne Zwischenspeicher: der lohnt sich erst,
wenn man dieselbe Platte hundertmal rechnet.

#### Projekt.pruefen

```python
def pruefen(self) -> None
```

Prueft die Beschreibung -- vor jedem Rechnen und beim Oeffnen einer
Datei.

Zuerst jedes Feld gegen das, was an ihm steht
([[opencivil.projekt.lesen#felder_pruefen|felder_pruefen]]): was in Python
gebaut wurde, geht so durch dieselbe Tuer wie eine Datei. Danach, was
mehrere Felder zusammen betrifft.

#### Projekt.aufbauen

```python
def aufbauen(self, *, schnell: bool=False) -> Aufbau
```

Baut aus der Beschreibung ein vollstaendiges Rechenwerk.

Die Arbeit steht in [[opencivil.projekt.aufbau#aufbauen|opencivil.projekt.aufbau.aufbauen]], neben
dem [[opencivil.projekt.aufbau#Aufbau|Aufbau]], der dabei herauskommt.

#### Projekt.speichern

```python
def speichern(self, pfad: str | Path) -> Path
```

#### Projekt.laden

```python
@classmethod
def laden(cls, pfad: str | Path) -> 'Projekt'
```

#### Projekt.beispiel

```python
@classmethod
def beispiel(cls) -> 'Projekt'
```

Ein lauffähiges Beispiel, damit die Oberfläche nicht leer startet.

Gebaut über dieselben Methoden, die man ohne Oberfläche benutzt. So
steht die Fassade an einer Stelle vorgeführt -- und der
Schnappschuss-Test prüft sie mit: baute sie etwas anderes als die
Einträge von Hand, die hier vorher standen, änderte sich der Bericht.

#### Projekt.jeder_nachweis

```python
@classmethod
def jeder_nachweis(cls) -> 'Projekt'
```

Jeder Nachweis einmal laut -- und die Fälle, die das Beispiel nie zeigt.

Zusammen mit [[opencivil.projekt.projekt#Projekt.beispiel|beispiel]] führt es jeden Nachweis einmal laut; ein
Test wacht darüber. Aus den beiden stammen der Schnappschuss des
Berichts und die Formelsammlung der Oberfläche -- darum steht es hier
und nicht bei den Tests.

Erhöhte Anforderung mit allen Schaltern und begrenzter rissaktiver
Dicke, häufige und quasi-ständige Lastfälle abgeleitet und eigene, Bügel
mit Stabzahl in y, ein Knickfall, die Verformung im Feld und am
Kragarm; eine zweite Platte mit x aussen und b = 500 mm, die im Feld
nicht aufgeht, auch nicht in der Durchbiegung, und deren Stahl unter
Dauerlast fliesst, dazu Querkraft ohne Bügel -- einmal über m_Rd,
einmal darunter, mit Einlage; eine dritte ohne x-Bewehrung; eine vierte mit
Querkraft ohne Einlage, einer Einwirkung, die am kürzesten Abstand
gemessen wird, und ⌀40 in y unter der x-Bewehrung -- die fliesst bei
x = h/2 nicht. Gebaut über die Fassade, wie ein Benutzer es in Python
täte.

#### Projekt._grundbrueche

```python
@staticmethod
def _grundbrueche(p: 'Projekt') -> None
```

Jede Lage des Grundwassers und beide Arten des Bodens: drainiert mit
Kohäsion, geneigter Sohle, geneigtem Gelände, Auflast und dem
Wasser im Gleitkörper, dazu eine Last, so schräg, dass die Klammer
eines Lastneigungsfaktors unter null fällt; das Wasser über der Sohle
und auf ihrer Höhe, dort ein langer Streifen; undrainiert flach und
tief eingebunden, einmal so schräg belastet, dass es keinen
Widerstand gibt.

#### Projekt._alles_einmal

```python
@staticmethod
def _alles_einmal(p: 'Projekt', decke: QuerschnittEintrag, analyse: QuerschnittsanalyseEintrag) -> None
```

Jede Vorlage, Kennwerte von Hand, Platte und Analyse als
Querschnitt; Beton und Stahl; Gelenke und ein Knoten, dessen Drehung
keine Steifigkeit hat; Federn am Lager, Bettung, feste Linienlager
mit und ohne Stab; jede Lastart, auch projiziert.

#### Projekt._beweglich

```python
@staticmethod
def _beweglich(p: 'Projekt') -> None
```

Ein Träger auf zwei Rollen: nichts hält ihn waagrecht -- eine Meldung statt einer Zahl.

### _felder_setzen

```python
def _felder_setzen(eintrag: Any, felder: Mapping[str, Any], wo: str) -> None
```

Die Stichworte einer Fassade an den Eintrag -- ein unbekanntes wird
gemeldet, mit dem aehnlichsten Feld, statt still zu verschwinden.


## Braucht

- [[opencivil.ergebnis]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.balkensystem]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.grundbruch]]
- [[opencivil.projekt.lesen]]
- [[opencivil.projekt.platte]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.projekt.skript]]
- [[opencivil.querschnitt.platte]]

## Gebraucht von

- [[opencivil.projekt]]
- [[opencivil.projekt.aufbau]]
