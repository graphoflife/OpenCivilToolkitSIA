---
erzeugt: e4e8600aa13b
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/verformung.py
> die Durchbiegung der Platte.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/verformung.py)

## VERANTWORTUNG

Haelt je Verformungsfall die wirksame Durchbiegung gegen ihren Grenzwert:

```
omega_w = (1 - 20 rho') / (10 rho^0.7) · (0.75 + 0.1 phi) · (h/d)^3
w_eff   = omega_w · w
w_max   = L / 350
alpha   = w_max / w_eff
```

`w` gibt der Benutzer an, ermittelt mit der Steifigkeit E_cm. Der
Vergroesserungsfaktor omega_w -- in der Norm w/w_c, SIA 262:2025, 4.4.3.2.5
-- fuehrt sie auf die Durchbiegung der gerissenen Platte unter Dauerlast.


## EIN FAKTOR JE SEITE, NICHT JE FALL

`rho = A_s/(b·d)` gehoert zur gezogenen Seite, `rho'` zur Gegenseite, mit
`d'` vom gezogenen Rand bis zur Gegenlage -- das ist deren statische Hoehe:
`rho'` der einen Seite ist das `rho` der anderen. Der Faktor haengt also
nur an der Platte und an der gezogenen Seite: [[opencivil.nachweis.verformung#Vergroesserungsfaktor|Vergroesserungsfaktor]]
rechnet ihn je Seite mit x-Bewehrung, immer -- unten omega_w, oben omega_w'
--, denn die Zusammenfassung zeigt beide als Kennzahl (Benutzer,
2026-10-16). Der Nachweis liest ihn fuer jeden Fall seiner Seite. Die
x-Posten einer Seite zaehlen zusammen, in ihrem Schwerpunkt. Fehlt die
Gegenseite, ist `rho' = 0`; fehlt die gezogene, gibt es keinen Faktor, und
der Fall laesst sich nicht nachweisen.

Das phi gehoert der Verformung der Platte, Vorgabe 2.


## NACH VORGABE

Der Grenzwert L/350 und dass `w` mit E_cm ermittelt ist, stehen so, wie
der Benutzer sie vorgegeben hat -- nicht nachgeschlagen
(`notizbuch/Notizen/TODO.md`). Die Formel des Faktors und ihre Normstelle
hat er geliefert.


## EINHEITEN

Alles in SI-Basis; `w` in mm und `L` in m kommen als Groessen.

## Inhalt

### gegenseite

```python
def gegenseite(seite: str) -> str
```

### Verformungsfall

```python
@dataclass(frozen=True)
class Verformungsfall
```

Eine Durchbiegung, mit E_cm ermittelt, zu ihrer Spannweite.

- `name: str`
- `w: Groesse` – Die Durchbiegung mit der Steifigkeit E_cm -- ein Betrag.
- `laenge: Groesse` – Die Spannweite L.
- `zugseite: str = 'unten'` – Welche Seite der Fall zieht -- danach richten sich rho und rho'.

#### Verformungsfall.kennung

```python
@property
def kennung(self) -> str
```

### Fallergebnis

```python
@dataclass
class Fallergebnis
```

Was ein Fall ergibt -- fuer Urteil und Herleitung.

- `fall: Verformungsfall`
- `w_eff: Optional[Wert] = None`
- `w_max: Optional[Wert] = None`
- `erfuellungsgrad: float = 0.0`
- `erfuellt: bool = False`
- `begruendung: str = ''`
- `hinweis: str = ''`

### Vergroesserungsfaktor

```python
class Vergroesserungsfaktor(Prozedur)
```

Der Vergroesserungsfaktor der Durchbiegung in x, je gezogene Seite mit
x-Bewehrung: unten omega_w, oben omega_w'. Er gehoert der Platte und
rechnet immer -- als Kennzahl und fuer den Verformungsnachweis.

- `THEMA = 'Verformung'`

#### Vergroesserungsfaktor.rechne

```python
def rechne(self, e: Eingaben, p: Protokoll) -> Dict[str, Groesse]
```

#### Vergroesserungsfaktor._bewehrungsgehalte

```python
def _bewehrungsgehalte(self, p: Protokoll, e: Eingaben, werte: Zwischenwerte) -> Dict[str, Tuple[Wert, Wert]]
```

Je Seite mit x-Bewehrung der Bewehrungsgehalt und seine statische
Hoehe -- die gezogene Seite braucht beide, die Gegenseite ihren
Gehalt als rho'.

### Verformung

```python
class Verformung(Nachweis)
```

Die Durchbiegung je Verformungsfall, in x -- mit dem
Vergroesserungsfaktor der Seite, die der Fall zieht
([[opencivil.nachweis.verformung#Vergroesserungsfaktor|Vergroesserungsfaktor]]).

- `THEMA = 'Verformung'`

#### Verformung.pruefe

```python
def pruefe(self, e: Eingaben, p: Protokoll) -> Ausfuehrung
```


## Konstanten

- `KRIECHZAHL = 2.0` – Vorgabe der Kriechzahl phi im Vergroesserungsfaktor -- Klima und Belastungsalter, eine Annahme ueber das Bauwerk.
- `GRENZE = 350.0` – `w_max = L / GRENZE` -- nach Vorgabe des Benutzers (2026-10-16), nicht nachgeschlagen.
- `ZUGSEITEN = ('unten', 'oben')` – Die Seiten, die ein Verformungsfall ziehen kann: unten im Feld, oben am Kragarm oder ueber der Stuetze.
- `SYMBOL = {'unten': '\\omega_w', 'oben': "\\omega_w'"}` – Wie der Faktor einer Seite heisst: omega_w fuer Zug unten, omega_w' fuer Zug oben (Benutzer, 2026-10-16).

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.querschnitt.platte]]

## Gebraucht von

- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.aufbau.platte]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.web.api]]

## Formeln aus diesem Modul

- [[Bewehrungsgehalt]] · `Vergroesserungsfaktor._bewehrungsgehalte`
- [[Bewehrungsquerschnitt der zusammengefassten Lage]] · `Vergroesserungsfaktor._bewehrungsgehalte`
- [[Grenzwert der Durchbiegung]] · `Verformung._einen_fall`
- [[Schwerpunkt der zusammengefassten Lage]] · `Vergroesserungsfaktor._bewehrungsgehalte`
- [[Statische Höhe]] · `Vergroesserungsfaktor._bewehrungsgehalte`
- [[Vergrösserungsfaktor der Durchbiegung]] · `Vergroesserungsfaktor.rechne`
- [[Wirksame Durchbiegung]] · `Verformung._einen_fall`
