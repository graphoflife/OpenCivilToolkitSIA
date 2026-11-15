---
erzeugt: 519119823c2b
art: modul
tags: [modul]
---
> [!abstract] opencivil/stabwerk/profiltabelle.py
> welche Stahlprofile es gibt, mit ihren Massen.
> Paket [[opencivil.stabwerk]] · [Quelltext](../../opencivil/stabwerk/profiltabelle.py)

## VERANTWORTUNG

Die Reihen der Walzprofile und Rohre und je Groesse ihre Masse in mm. Was
daraus gerechnet wird, sagt die Form der Reihe
([[opencivil.stabwerk.profilformen]]); gesucht wird ein Profil nach seinem
Namen ([[opencivil.stabwerk.profiltabelle#profil|profil]]).


## QUELLE

Die Tabelle des Benutzers, «Festigkeitsnachweise I-Standardprofile Stahl» vom
2019-04-15, Blatt «Querschnitte» -- dieselben Groessen in derselben Folge
(Benutzer, 2026-11-15). Was noch fehlt -- L, INP, T, HEAA und die
warmgefertigten Rechteckrohre --, steht im Notizbuch unter TODO.


## NACH VORGABE, NICHT NACHGESCHLAGEN

* RRK: die Radien aus der Wanddicke, wie in der Tabelle -- bis t = 6 mm
  r_o = 2t und r_i = t, bis 10 mm 2.5t und 1.5t, darueber 3t und 2t.
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
- `profile: Tuple[Profil, ...]`

### _z

```python
def _z(text: str) -> str
```

Eine Zahl, wie sie im Namen steht: 21.3, 400.

### _unp

```python
def _unp(h: float, b: float, t_w: float, t_f: float, r_1: float, r_2: float) -> Dict[str, float]
```

Die Masse eines UNP -- Neigung p in % und die Stelle c von t_f nach der Hoehe.

### _rrk

```python
def _rrk(h: float, b: float, t: float) -> Dict[str, float]
```

Die Masse eines RRK -- die Radien aus der Wanddicke.

### _benannt

```python
def _benannt(kurz: str, text: str, masse: Callable[..., Dict[str, float]]) -> Tuple[Profil, ...]
```

Die Zeilen einer Reihe, deren Name vorne steht: «IPE 80  80  46 ...».

### reihe

```python
def reihe(kurz: str) -> Profilreihe
```

### profil

```python
def profil(name: str) -> Profil
```

Das Profil dieses Namens -- ein unbekannter ist ein `KeyError`, der es sagt.


## Konstanten

- `_I_PROFILE = '\nIPE 80 80 46 3.8 5.2 5\nIPE 100 100 55 4.1 5.7 7\nIPE 120 120 64 4…` – I-Profile: Name, h, b, t_w, t_f, r.
- `_UPE = '\nUPE 80 80 50 4 7 10\nUPE 100 100 55 4.5 7.5 10\nUPE 120 120 60 5 8…` – UPE: Name, h, b, t_w, t_f, r.
- `_UNP = '\nUNP 65 65 42 5.5 7.5 7.5 4\nUNP 80 80 45 6 8 8 4\nUNP 100 100 50 6…` – UNP: Name, h, b, t_w, t_f, r_1, r_2.
- `_RRK = '\n 20 20 2\n 25 25 2\n 25 25 2.5\n 25 25 3\n 30 30 2\n 30 30 2.5\n 3…` – RRK: h, b, t -- erst die quadratischen, dann die rechteckigen.
- `_ROR = '\n 21.3 2.3\n 21.3 2.6\n 21.3 3.2\n 26.9 2.3\n 26.9 2.6\n 26.9 3.2\n…` – ROR: D, t.
- `PROFILREIHEN = (Profilreihe('IPE', 'I-Träger, schmale Flansche', I_PROFIL, _benannt(…`
- `PROFILE = {p.name: p for r in PROFILREIHEN for p in r.profile}` – Jedes Profil nach seinem Namen -- «HEB 300», «RRK 200 x 100 x 8».
- `_REIHEN = {r.kurz: r for r in PROFILREIHEN}`

## Braucht

- [[opencivil.stabwerk.profilformen]]
- [[opencivil.stabwerk.querschnitte]]

## Gebraucht von

- [[opencivil.projekt.aufbau.balkensystem]]
- [[opencivil.projekt.balkensystem]]
- [[opencivil.web.api]]
