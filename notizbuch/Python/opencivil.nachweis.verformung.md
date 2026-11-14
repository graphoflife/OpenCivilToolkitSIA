---
erzeugt: 46cfd8188e63
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

`rho = A_s/(b·d)` gehoert zur gezogenen Seite, `rho' = A_s'/(b·d)` zur
Gegenseite -- beide mit dem `d` der gezogenen Seite (SIA 262:2025,
4.4.3.2.5). Bis 2026-11-14 bezog sich `rho'` auf die statische Hoehe der
Gegenseite; im Beispiel aenderte das omega_w um ein Promille. Der Faktor
haengt nur an der Platte und an der gezogenen Seite:
[[opencivil.nachweis.verformung#Vergroesserungsfaktor|Vergroesserungsfaktor]] rechnet ihn je Seite mit x-Bewehrung, immer
-- unten omega_w, oben omega_w' --, denn die Zusammenfassung zeigt beide als
Kennzahl (Benutzer, 2026-10-16). Der Nachweis liest ihn fuer jeden Fall
seiner Seite. Die x-Posten einer Seite zaehlen zusammen, in ihrem
Schwerpunkt. Fehlt die Gegenseite, ist `rho' = 0`; fehlt die gezogene,
gibt es keinen Faktor, und der Fall laesst sich nicht nachweisen. Ab
`rho' = 5 %` waere der Faktor nicht mehr positiv: dann gibt es keinen
Nachweis.

Das phi gehoert der Verformung der Platte, Vorgabe 2; die Norm bestimmt es
nach 3.1.2.6.


## DIE NORM

`w` mit E_cm heisst mit `gamma_cE = 1.0` (4.2.1.16). Den Grenzwert gibt
SIA 262 an SIA 260 weiter (4.4.3.1.1): L/350 steht in SIA 260:2013,
Anhang A, Tabelle 3, unter haeufiger Last fuer Funktionstuechtigkeit und
Komfort; welches Kriterium gilt, legt das Projekt fest (4.4.3.2.1). Die
Tabelle meint dort nur einen Teil der Durchbiegung -- was nach dem Einbau
der Einbauten dazukommt, oder was die veraenderlichen Lasten bewirken.
Gehalten wird die ganze samt Kriechen; das liegt sicher.


## EINHEITEN

Alles in SI-Basis; `w` in mm und `L` in m kommen als Groessen.

## Inhalt

### Verformungsfall

```python
@dataclass(frozen=True)
class Verformungsfall
```

Eine Durchbiegung, mit E_cm ermittelt, zu ihrer Spannweite.

- `name: str`
- `w: Groesse` – Die Durchbiegung mit der Steifigkeit E_cm -- ein Betrag.
- `laenge: Groesse` – Die Spannweite L.
- `zugseite: Zugseite = Zugseite.UNTEN` – Welche Seite der Fall zieht -- danach richten sich rho und rho'.

#### Verformungsfall.kennung

```python
@property
def kennung(self) -> str
```

### Fallergebnis

```python
@dataclass
class Fallergebnis(Fallausgang)
```

Was ein Fall ergibt -- fuer Urteil und Herleitung: w_eff gegen w_max.

- `fall: Verformungsfall`
- `ausgang: Ausgang = NICHT_FUEHRBAR`
- `begruendung: str = ''`

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
def _bewehrungsgehalte(self, p: Protokoll, e: Eingaben, werte: Zwischenwerte) -> Dict[Zugseite, Tuple[Wert, Wert, Wert]]
```

Je Seite mit x-Bewehrung ihr Querschnitt, ihr Bewehrungsgehalt und
ihre statische Hoehe -- die gezogene Seite braucht Gehalt und Hoehe,
die Gegenseite ihren Querschnitt fuer rho'. Querschnitt, Schwerpunkt
und Hoehe der Lage schreibt
[[opencivil.querschnitt.lagenaufbau#protokoll_lage|protokoll_lage]], wie in den
Nachweisen der Lagen: dieselbe Hoehe heisst ueberall gleich, etwa
d_{2,x}. Bis 2026-10-18 hiess sie hier d_u.

### Verformung

```python
class Verformung(Nachweis)
```

Die Durchbiegung je Verformungsfall, in x -- mit dem
Vergroesserungsfaktor der Seite, die der Fall zieht
([[opencivil.nachweis.verformung#Vergroesserungsfaktor|Vergroesserungsfaktor]]).

- `THEMA = 'Verformung'`
- `ART = 'w'`

#### Verformung.pruefe

```python
def pruefe(self, e: Eingaben, p: Protokoll) -> Ausfuehrung
```


## Konstanten

- `KRIECHZAHL = 2.0` – Vorgabe der Kriechzahl phi im Vergroesserungsfaktor -- Klima und Belastungsalter, eine Annahme ueber das Bauwerk.
- `GRENZE = 350.0` – `w_max = L / GRENZE` -- SIA 260:2013, Anhang A, Tabelle 3 (siehe Dateikopf). Daneben stehen dort L/500 (selten, sproede Einbauten) und L/300 (quasi-staendig, Aussehen).
- `REFERENZ_FAKTOR = 'SIA 262:2025, 4.4.3.2.5, (104)'` – Woher Faktor und Grenzwert kommen.
- `REFERENZ_GRENZE = 'SIA 260:2013, Anhang A, Tabelle 3'`
- `SYMBOL = {Zugseite.UNTEN: '\\omega_w', Zugseite.OBEN: "\\omega_w'"}` – Wie der Faktor einer Seite heisst: omega_w fuer Zug unten, omega_w' fuer Zug oben (Benutzer, 2026-10-16). Ziehen kann ein Fall die Seiten der Platte, [[opencivil.querschnitt.zugseite#Konstanten|UM_Y]]: unten im Feld, oben am Kragarm oder ueber der Stuetze.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.nachweis]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.querschnitt.lagenaufbau]]
- [[opencivil.querschnitt.platte]]
- [[opencivil.querschnitt.zugseite]]

## Gebraucht von

- [[opencivil.projekt.aufbau.platte]]
- [[opencivil.projekt.eintraege]]

## Formeln aus diesem Modul

- [[Bewehrungsgehalt]] · `Vergroesserungsfaktor._bewehrungsgehalte`
- [[Bewehrungsgehalt der Gegenseite]] · `Vergroesserungsfaktor.rechne`
- [[Grenzwert der Durchbiegung]] · `Verformung._einen_fall`
- [[Vergrösserungsfaktor der Durchbiegung]] · `Vergroesserungsfaktor.rechne`
- [[Wirksame Durchbiegung]] · `Verformung._einen_fall`
