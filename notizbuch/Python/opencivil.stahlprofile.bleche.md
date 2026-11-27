---
erzeugt: 9156a38841d7
art: modul
tags: [modul]
---
> [!abstract] opencivil/stahlprofile/bleche.py
> die Bleche eines Stahlprofils, fuer seine Querschnittsklasse.
> Paket [[opencivil.stahlprofile]] · [Quelltext](../../opencivil/stahlprofile/bleche.py)

## VERANTWORTUNG

Je Form die ebenen Teile eines Profils, an denen SIA 263:2013 die
Schlankheit misst (Tabellen 5a und 5b) und die mitwirkende Breite rechnet
(4.5.3): die Flansche und der Steg des I und des U, die vier Waende des
Rechteckrohrs -- und das Rundrohr als Ganzes, dessen Grenze D/t heisst. Jedes
Blech liegt, wo das Profil in der Zeichnung liegt
([[opencivil.stahlprofile.lage#Profillage|Profillage]]), und heisst nach seiner
Lage dort: «Flansch oben, links», auch am gedrehten Profil.


## ZWEI BREITEN AUF EINER GERADEN

Die theoretische Breite `b` laeuft auf der Mittelebene des Blechs zwischen
den Mittellinien der Bleche, an denen es haengt -- beim einseitig gehaltenen
von der Mittellinie des Stegs bis zum freien Rand. Mit ihr rechnet die
mitwirkende Breite: 4.5.3.3 misst von den theoretischen Scheibenschnittlinien
aus. Die Schlankheit misst die Breite `c`, die die Bilder der Tabellen 5a
und 5b zeigen: beim gewalzten Profil ohne die Ausrundungen, beim
Rechteckrohr ohne 1.5 t je Seite, ob kalt- oder warmgefertigt -- Tabelle 5a
unterscheidet nicht. Sie liegt auf derselben Geraden, `vor` nach dem
Anfang der theoretischen.


## DAS UNP

nach Vorgabe, nicht nachgeschlagen
Seine Flansche sind geneigt. Gerechnet wird mit der Flanschdicke `t_f` der
Tabelle, die in der Mitte des Flanschs gilt, und mit `r_1` wie beim UPE
mit `r`: der Steg bis zur Ausrundung misst so `h - 2 t_f - 2 r_1`, etwas
mehr als zwischen den dickeren Wurzeln der Flansche -- auf der sicheren
Seite.


## DER KASTEN

Die Waende eines Rechteckrohrs mindern nach dem genaueren Faktor fuer
Kastentraeger ([[opencivil.stahlbau.klasse#abminderung_kasten|abminderung_kasten]]); das
weiss jedes seiner Bleche ([[opencivil.stahlprofile.bleche#Blech|Blech.kasten]]).

## Inhalt

### Halterung

```python
class Halterung(Wahl)
```

Wie ein Blech gehalten ist -- danach waehlt die Norm ihre Tabelle.

- `BEIDSEITIG = 'beidseitig'`
- `EINSEITIG = 'einseitig'`
- `ROHR = 'Rundrohr'`

#### Halterung.tabelle

```python
@property
def tabelle(self) -> str
```

Wo seine Grenzen stehen: Tabelle 5a fuer beidseitig gestuetzte Scheiben und Rohre, sonst 5b.

### Blech

```python
@dataclass(frozen=True)
class Blech
```

Ein Blech eines Profils, in mm in der Zeichnung -- siehe Dateikopf.
`von` und `bis` sind die Enden der theoretischen Breite, beim
einseitig gehaltenen `von` am gehaltenen Rand und `bis` am freien.
Beim Rundrohr liegen beide in seiner Mitte, und `c` ist `D`.

- `name: str`
- `halterung: Halterung`
- `von: Punkt`
- `bis: Punkt`
- `t: float`
- `c: float`
- `vor: float = 0.0`
- `kasten: bool = False` – Ob es eine Wand eines Kastens ist -- siehe Dateikopf.

#### Blech.b

```python
@property
def b(self) -> float
```

Die theoretische Breite.

#### Blech.punkt

```python
def punkt(self, a: float) -> Punkt
```

Der Punkt auf der Mittelebene, `a` von `von` entfernt.

#### Blech.lichte_enden

```python
@property
def lichte_enden(self) -> Tuple[Punkt, Punkt]
```

Die Enden der Breite `c`, an der die Schlankheit gemessen wird.

#### Blech.streifen

```python
def streifen(self, von: float, bis: float) -> Tuple[Punkt, ...]
```

Das Rechteck des Blechs zwischen `von` und `bis`, ab seinem Anfang gemessen, so dick wie es.

### _u

```python
def _u(m: Mapping[str, float], r: float) -> List[_Roh]
```

Ein U, der Ruecken links: zwei Flansche, je von der Mittellinie des Stegs bis zur Spitze.

### _steg

```python
def _steg(y: float, h: float, t_f: float, t_w: float, r: float) -> _Roh
```

Der Steg zwischen den Mittellinien der Flansche, `c` bis zu den Ausrundungen.

### _rechteckrohr

```python
def _rechteckrohr(m: Mapping[str, float]) -> List[_Roh]
```

Vier Waende zwischen den Mittellinien der anderen; `c` ohne 1.5 t je Seite (Tabelle 5a).

### bleche

```python
def bleche(lage: Profillage) -> List[Blech]
```

Die Bleche des Profils, wo es in der Zeichnung liegt -- siehe Dateikopf.


## Konstanten

- `_Roh = Tuple[Tuple[str, ...], Halterung, Punkt, Punkt, float, float, float]` – Ein Blech, wie die Form es zeichnet: sein Name aus Woertern -- die Richtungen darin dreht und spiegelt die Lage mit --, die Halterung, die Enden der theoretischen Breite, die Dicke, `c` und `vor`.
- `_RICHTUNGEN = ('oben', 'unten', 'links', 'rechts')`
- `_KASTEN = {'rechteckrohr_gerundet'}` – Die Formen, die ein Kasten sind -- siehe Dateikopf.
- `_BLECHE = {'i_profil': _i, 'u_parallel': lambda m: _u(m, m['r']), 'u_geneigt': …` – Je Form, welche Bleche sie hat -- nach dem Schluessel ihrer Vorlage.

## Braucht

- [[opencivil.core.wahl]]
- [[opencivil.stahlprofile.lage]]
- [[opencivil.stahlprofile.tabelle]]

## Gebraucht von

- [[opencivil.nachweis.qa_stahl_kennzahlen]]
- [[opencivil.nachweis.qa_stahl_werte]]
- [[opencivil.nachweis.qa_verbund_werte]]
- [[opencivil.stahlbau.klasse]]
- [[opencivil.stahlbau.querschnitt]]
- [[opencivil.stahlbau.schub]]
- [[opencivil.verbund.querschnitt]]
