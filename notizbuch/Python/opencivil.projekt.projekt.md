---
erzeugt: 3500fc4e36c4
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/projekt.py
> das Projekt als Ganzes.
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/projekt.py)

## VERANTWORTUNG

Das [[opencivil.projekt.projekt#Projekt|Projekt]] haelt Materialien und Platten zusammen und ist das, was
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
- `gleichungen: List[GleichungsblattEintrag] = field(default_factory=list)` – Blätter analytischer Gleichungen -- Zeile für Zeile, wie in Mathcad.
- `querschnittsanalysen: List[QuerschnittsanalyseEintrag] = field(default_factory=list)` – Gezeichnete Querschnitte: Polygone, Bewehrung, Schubwände.

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

#### Projekt.freie_kennung

```python
def freie_kennung(self, vorsilbe: str) -> str
```

#### Projekt.freier_name

```python
def freier_name(self, wunsch: str, ausser: str='') -> str
```

Haengt bei Bedarf _1, _2, ... an, bis der Name eindeutig ist.

#### Projekt.abgeleiteter_name

```python
def abgeleiteter_name(self, sorte: str, ausser: str='') -> str
```

Erster freier Name der Form `<Sorte>_1`, `<Sorte>_2`, ...

Nicht ueber [[opencivil.projekt.projekt#Projekt.freier_name|freier_name]] mit dem Wunsch `C30/37_1`, denn das
haengte bei Belegung nochmals an und ergaebe `C30/37_1_1`.

#### Projekt.material_loesen

```python
def material_loesen(self, kennung: str) -> MaterialEintrag
```

Macht aus einer Normsorte ein eigenstaendiges, aenderbares Material.

Der Name wird dabei zwingend geaendert -- die Sortenbezeichnung bleibt
der unveraenderten Norm vorbehalten.

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

Prueft die Beschreibung, bevor daraus gerechnet wird.

#### Projekt.aufbauen

```python
def aufbauen(self, *, schnell: bool=False) -> Aufbau
```

Baut aus der Beschreibung ein vollstaendiges Rechenwerk.

Die Arbeit steht in [[opencivil.projekt.aufbau#aufbauen|opencivil.projekt.aufbau.aufbauen]], neben
dem [[opencivil.projekt.aufbau#Aufbau|Aufbau]], der dabei herauskommt.

#### Projekt.aus_dict

```python
@classmethod
def aus_dict(cls, d: Mapping[str, Any]) -> 'Projekt'
```

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
mit Stabzahl in y, ein Knickfall; eine zweite Platte mit x aussen und
b = 500 mm, die im Feld nicht aufgeht und deren Stahl unter Dauerlast
fliesst, dazu Querkraft ohne Bügel -- einmal über m_Rd, einmal
darunter, mit Einlage; eine dritte ohne x-Bewehrung; eine vierte mit
Querkraft ohne Einlage, einer Einwirkung, die am kürzesten Abstand
gemessen wird, und ⌀40 in y unter der x-Bewehrung -- die fliesst bei
x = h/2 nicht. Dazu ein Blatt Gleichungen. Gebaut über die Fassade, wie
ein Benutzer es in Python täte.


## Braucht

- [[opencivil.ergebnis]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.gleichungen]]
- [[opencivil.projekt.lesen]]
- [[opencivil.projekt.platte]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.querschnitt.platte]]

## Gebraucht von

- [[opencivil.projekt]]
- [[opencivil.projekt.aufbau]]
