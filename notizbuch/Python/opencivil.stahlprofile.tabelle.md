---
erzeugt: 42c98bf73d11
art: modul
tags: [modul]
---
> [!abstract] opencivil/stahlprofile/tabelle.py
> welche Stahlprofile es gibt, mit ihren Massen.
> Paket [[opencivil.stahlprofile]] · [Quelltext](../../opencivil/stahlprofile/tabelle.py)

## VERANTWORTUNG

Die Reihen der Walzprofile, Rohre und des Vollstahls und je Groesse ihre
Masse in mm. Was daraus gerechnet wird, sagt die Form der Reihe
([[opencivil.stahlprofile.formen]]); gesucht wird ein Profil nach seinem
Namen ([[opencivil.stahlprofile.tabelle#profil|profil]]).


## VOLLSTAHL – MASSE FREI (Benutzer, 2026-11-27)

Vierkant-, Rund- und Flachstahl haben keine Tabelle: ihr Name sagt ihre
Masse in mm, «VKT 40», «RND 25», «FL 100 x 10» – die Reihe, dann die
Zahlen mit « x » dazwischen, wie bei den Rohren ([[opencivil.stahlprofile.tabelle#_name|_name]]).
[[opencivil.stahlprofile.tabelle#profil|profil]] liest sie daraus; welche es sind und wie weit sie gehen,
sagt die Reihe ([[opencivil.stahlprofile.tabelle#Profilreihe|Profilreihe.frei]]). Jede Zahl steht so kurz, wie
sie genau bleibt: «FL 100 x 10», nicht «FL 100.0 x 10». Ein Flachstahl
liegt: `b` ist seine Breite, `h` seine Dicke.


## QUELLE

Die Tabelle des Benutzers, «Festigkeitsnachweise I-Standardprofile Stahl» vom
2019-04-15, Blatt «Querschnitte» – dieselben Groessen in derselben Folge
(Benutzer, 2026-11-15). Die warmgefertigten Rechteckrohre (RRW) hat sie
nicht: ihre Groessen kommen aus dem Katalog «Hollow Structural Sections» von
ArcelorMittal Tubular Products Europe, 2024, Rohre nach EN 10210 – jede
Wanddicke, die er fuer ein Mass h × b als lieferbar zeigt (geholt am
2026-11-27 mit Erlaubnis des Benutzers). L, INP, T und HEAA hat der Benutzer
am 2026-11-27 zurueckgestellt; sie stehen im Notizbuch unter TODO.


## NACH VORGABE, NICHT NACHGESCHLAGEN

* RRK: die Radien aus der Wanddicke, wie in der Tabelle – bis t = 6 mm
  r_o = 2t und r_i = t, bis 10 mm 2.5t und 1.5t, darueber 3t und 2t.
* RRW: r_o = 1.5t und r_i = t, wie ueblich fuer warmgefertigte Rohre – der
  Katalog nennt keine Radien, und EN 10210-2 liegt nicht vor. Damit hat das
  RRW 200 x 100 x 8 A = 44.75 cm² und I_y = 2234 cm⁴.
* UNP: bis h = 300 mm sind die Flansche um 8 % geneigt, und t_f gilt bei
  b/2; darueber 5 %, und t_f gilt in der Mitte des Flanschs, (b + t_w)/2.
  Damit trifft die Rechnung die Werte der Tabelle, die keine Formeln hat.

## Inhalt

### Profil

```python
@dataclass(frozen=True)
class Profil
```

Eine Groesse einer Reihe: ihr Name und die Masse ihrer Form.

- `name: str`
- `reihe: str`
- `masse: Mapping[str, float]`

#### Profil.form

```python
@property
def form(self) -> Stabvorlage
```

### Profilreihe

```python
@dataclass(frozen=True)
class Profilreihe
```

- `kurz: str` – Wie die Reihe heisst und womit jeder ihrer Namen beginnt: «IPE».
- `beschreibung: str`
- `form: Stabvorlage`
- `profile: Tuple[Profil, ...]` – Die Groessen der Tabelle – bei Vollstahl nur die eine, mit der die Reihe beginnt.
- `frei: Tuple[Mass, ...] = ()` – Bei Vollstahl die Masse, die man frei eingibt, in der Folge des Namens (Dateikopf) – leer bei einer Reihe der Tabelle.
- `zur_form: Callable[..., Dict[str, float]] = dict` – Aus den freien Massen die der Form – beim Vierkant `b` und `h` aus `a`.

### _z

```python
def _z(zahl: Union[str, float]) -> str
```

Eine Zahl, wie sie im Namen steht: 21.3, 400 – so kurz, wie sie genau
bleibt, wie `String` in JavaScript (profilwahl.js).

### _name

```python
def _name(kurz: str, *zahlen: Union[str, float]) -> str
```

Ein Name: die Reihe, dann die Zahlen mit « x » dazwischen – «RRK 200 x 100 x 8».

### _unp

```python
def _unp(h: float, b: float, t_w: float, t_f: float, r_1: float, r_2: float) -> Dict[str, float]
```

Die Masse eines UNP – Neigung p in % und die Stelle c von t_f nach der Hoehe.

### _rrk

```python
def _rrk(h: float, b: float, t: float) -> Dict[str, float]
```

Die Masse eines RRK – die Radien aus der Wanddicke.

### _rrw

```python
def _rrw(text: str) -> Tuple[Profil, ...]
```

Die RRW einer Zeile «h b t t t» nach der anderen – die Radien aus der Wanddicke.

### _benannt

```python
def _benannt(kurz: str, text: str, masse: Callable[..., Dict[str, float]]) -> Tuple[Profil, ...]
```

Die Zeilen einer Reihe, deren Name vorne steht: «IPE 80  80  46 ...».

### _vollstahl

```python
def _vollstahl(kurz: str, beschreibung: str, form: Stabvorlage, frei: Tuple[Mass, ...], zur_form: Callable[..., Dict[str, float]]=dict) -> Profilreihe
```

Eine Reihe aus Vollstahl – ihr eines Profil aus den Vorgaben ihrer Masse (Dateikopf).

### reihe

```python
def reihe(kurz: str) -> Profilreihe
```

### profil

```python
def profil(name: str) -> Profil
```

Das Profil dieses Namens: aus der Tabelle oder, bei Vollstahl, aus den
Zahlen im Namen (Dateikopf). Was nicht geht, sagt ein `KeyError` mit
dem Grund, als Satz.

### _aus_vollstahl

```python
def _aus_vollstahl(r: Profilreihe, name: str, teile: Sequence[str]) -> Profil
```

Ein Profil aus Vollstahl aus den Zahlen seines Namens, `teile` – siehe [[opencivil.stahlprofile.tabelle#profil|profil]].


## Konstanten

- `_I_PROFILE = '\nIPE 80 80 46 3.8 5.2 5\nIPE 100 100 55 4.1 5.7 7\nIPE 120 120 64 4…` – I-Profile: Name, h, b, t_w, t_f, r.
- `_UPE = '\nUPE 80 80 50 4 7 10\nUPE 100 100 55 4.5 7.5 10\nUPE 120 120 60 5 8…` – UPE: Name, h, b, t_w, t_f, r.
- `_UNP = '\nUNP 65 65 42 5.5 7.5 7.5 4\nUNP 80 80 45 6 8 8 4\nUNP 100 100 50 6…` – UNP: Name, h, b, t_w, t_f, r_1, r_2.
- `_RRK = '\n 20 20 2\n 25 25 2\n 25 25 2.5\n 25 25 3\n 30 30 2\n 30 30 2.5\n 3…` – RRK: h, b, t – erst die quadratischen, dann die rechteckigen.
- `_RRW = '\n 80 80 5 6 6.3 7.1 8 10 12 12.5\n 90 90 5 6 6.3 7.1 8 10 12 12.5\n…` – RRW: h, b und dahinter jede lieferbare Wanddicke t – je Zeile, wie im Katalog: erst die quadratischen, dann die rechteckigen.
- `_ROR = '\n 21.3 2.3\n 21.3 2.6\n 21.3 3.2\n 26.9 2.3\n 26.9 2.6\n 26.9 3.2\n…` – ROR: D, t.
- `PROFILREIHEN = (Profilreihe('IPE', 'I-Träger, schmale Flansche', I_PROFIL, _benannt(…`
- `PROFILE = {p.name: p for r in PROFILREIHEN for p in r.profile}` – Jedes Profil nach seinem Namen – «HEB 300», «RRK 200 x 100 x 8».
- `_REIHEN = {r.kurz: r for r in PROFILREIHEN}`
- `_ZAHL = re.compile('\\d+(\\.\\d+)?')` – Eine Zahl im Namen eines Profils aus Vollstahl: ohne Vorzeichen und Exponent, 12 oder 12.5.

## Braucht

- [[opencivil.querschnitt.vorlagen]]
- [[opencivil.stabwerk.querschnitte]]
- [[opencivil.stahlprofile.formen]]

## Gebraucht von

- [[opencivil.projekt.aufbau.balkensystem]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.projekt.staebe]]
- [[opencivil.stahlbau.schub]]
- [[opencivil.stahlbau.stabilitaet]]
- [[opencivil.stahlprofile.bleche]]
- [[opencivil.stahlprofile.lage]]
- [[opencivil.verbund.querschnitt]]
- [[opencivil.verbund.stuetze]]
- [[opencivil.web.api]]
