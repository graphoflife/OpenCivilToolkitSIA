---
erzeugt: eb387f5393c7
art: modul
tags: [modul]
---
> [!abstract] opencivil/core/einheiten.py
> Dimensionen, Einheiten und Groessen.
> Paket [[opencivil.core]] · [Quelltext](../../opencivil/core/einheiten.py)

## VERANTWORTUNG

Stellt den physikalischen Zahlentyp des gesamten Toolkits bereit. Eine
`Groesse` traegt immer ihren Wert *und* ihre Dimension mit sich. Rechnen mit
inkompatiblen Groessen (z.B. `mm + MPa`) wirft sofort einen Fehler, statt
still eine falsche Zahl zu liefern.

Intern wird jede Groesse in SI-Basiseinheiten (m, kg, s, K) gespeichert. Die
Anzeige-Einheit ist reine Darstellung und beeinflusst das Resultat nie.


## EMPIRISCHE NORMFORMELN

Viele SIA-Formeln sind dimensionell inhomogen, z.B.

```
tau_cd = 0.3 * sqrt(f_ck) / gamma_c        (SIA 262:2025, 2.4.2.4)
```

Hier ist stillschweigend vorausgesetzt, dass `f_ck` in N/mm^2 eingesetzt wird
und das Resultat in N/mm^2 herauskommt. Solche Formeln duerfen nicht ueber die
normale Arithmetik laufen. Dafuer gibt es [[opencivil.core.einheiten#empirisch|empirisch]]: dort muss man
explizit deklarieren, in welcher Einheit jeder Eingabewert einzusetzen ist und
welche Einheit das Resultat traegt. Damit wird die implizite Einheiten-Konvention
der Norm sichtbar, pruefbar und im Bericht darstellbar.


## EIGENSTAENDIG NUTZBAR


```python
from opencivil.core.einheiten import Groesse, MM, MPA, KN
h = Groesse(300, MM)
print(h.formatiert(0))            # '300'
print((h * h).in_einheit(MM**2))  # 90000.0
```

## Inhalt

### Dimension

```python
@dataclass(frozen=True)
class Dimension
```

Physikalische Dimension als Exponentenvektor ueber den SI-Basisgroessen.

Die Exponenten sind `Fraction`, damit auch Wurzeln darstellbar bleiben
(z.B. `sqrt(Kraft/Flaeche)`). Das ist noetig, damit empirische Formeln
nicht schon beim Zwischenschritt abstuerzen.

- `laenge: Fraction = Fraction(0)`
- `masse: Fraction = Fraction(0)`
- `zeit: Fraction = Fraction(0)`
- `temperatur: Fraction = Fraction(0)`

#### Dimension.ist_dimensionslos

```python
@property
def ist_dimensionslos(self) -> bool
```

### Einheit

```python
@dataclass(frozen=True)
class Einheit
```

Eine benannte Einheit: Dimension plus Umrechnungsfaktor auf SI-Basis.

`faktor` ist so definiert, dass gilt:

```
wert_in_SI = wert_in_dieser_Einheit * faktor
```

Einheiten lassen sich multiplizieren, dividieren und potenzieren, sodass
zusammengesetzte Einheiten wie `KN / M` direkt entstehen. Zusammengesetzte
Einheiten bekommen einen mechanisch erzeugten Namen; wo ein bestimmter Name
gewuenscht ist (z.B. `kNm/m`), wird die Einheit unten explizit definiert.

- `name: str` – Maschinenlesbarer Name, zugleich Schluessel im Katalog: `N/mm^2`.
- `dimension: Dimension`
- `faktor: float = 1.0`
- `latex: Optional[str] = None`
- `klebt: bool = False` – Ob das Zeichen unmittelbar an der Zahl haengt, ohne schmalen Abstand. Der Regelfall ist der Abstand: `30\,\mathrm{mm}`. Das Gradzeichen gehoert dagegen an die Zahl -- `30°`, nicht `30 °`.
- `beschriftung: Optional[str] = None` – Lesbare Schreibweise fuer die Oberflaeche: `N/mm²`. Der `name` bleibt ASCII, weil er als Schluessel dient und in IDs vorkommt. Wo eine Zahl ohne LaTeX-Satz neben ihrer Einheit steht -- in der Werteliste, an den Eingabefeldern --, gehoert die lesbare Form hin. Andernfalls stuende dort `N/mm^2`, waehrend die Herleitung daneben `N/mm²` setzt.

#### Einheit.als_latex

```python
def als_latex(self) -> str
```

LaTeX-Fragment der Einheit, mit vorangestelltem schmalem Abstand.

### _name_zu_latex

```python
def _name_zu_latex(name: str) -> str
```

Baut aus einem einfachen Einheitennamen ein aufrechtes LaTeX-Fragment.

### _name_zu_text

```python
def _name_zu_text(name: str) -> str
```

Macht aus dem ASCII-Namen die lesbare Schreibweise: `mm^2` -> `mm²`.

Nur die Potenzen, und nur solange jede Ziffer ein hochgestelltes Zeichen
hat. Fuer alles Weitere -- `‰` etwa -- gibt die Einheit ihre
`beschriftung` selbst an; mechanisch ableiten liesse sich das nicht.

### einheit

```python
def einheit(name: str) -> Einheit
```

Sucht eine benannte Einheit im Katalog.

### EinheitenFehler

```python
class EinheitenFehler(Exception)
```

Basisklasse fuer alle Einheiten- und Dimensionsfehler.

### DimensionsFehler

```python
class DimensionsFehler(EinheitenFehler)
```

Zwei Groessen mit unvertraeglichen Dimensionen wurden verknuepft.

### UnbekannteEinheitFehler

```python
class UnbekannteEinheitFehler(EinheitenFehler)
```

Eine Einheit wurde ueber einen unbekannten Namen angefordert.

### Groesse

```python
class Groesse
```

Ein physikalischer Zahlenwert mit Dimension.

Der Wert wird intern immer in SI-Basiseinheiten gehalten ([[opencivil.core.einheiten#Groesse|si]]).
`anzeige` merkt sich lediglich, in welcher Einheit die Groesse dargestellt
werden soll -- das Rechenergebnis haengt nie davon ab.

Beispiele:

```python
h = Groesse(300, MM)
b = Groesse(1.0, M)
flaeche = h * b                    # Dimension L^2
print(flaeche.in_einheit(MM2))     # 300000.0

h + Groesse(30, MPA)               # -> DimensionsFehler
```

#### Groesse.aus_si

```python
@classmethod
def aus_si(cls, si_wert: Zahl, anzeige: Einheit) -> 'Groesse'
```

Baut eine Groesse aus einem bereits in SI-Basis vorliegenden Wert.

#### Groesse.dimension

```python
@property
def dimension(self) -> Dimension
```

#### Groesse.in_einheit

```python
def in_einheit(self, ziel: Einheit) -> float
```

Gibt den Zahlenwert in der gewuenschten Einheit zurueck.

#### Groesse.zahl

```python
@property
def zahl(self) -> float
```

Zahlenwert in der aktuellen Anzeige-Einheit.

#### Groesse.als

```python
def als(self, ziel: Einheit) -> 'Groesse'
```

Gleiche physikalische Groesse, andere Anzeige-Einheit.

#### Groesse.wurzel

```python
def wurzel(self) -> 'Groesse'
```

Quadratwurzel. Halbiert die Dimensionsexponenten.

#### Groesse.nahe

```python
def nahe(self, andere: 'Groesse', rel: float=1e-09, abs_: float=0.0) -> bool
```

Toleranter Vergleich -- fuer Tests und Iterationsabbrueche.

#### Groesse.formatiert

```python
def formatiert(self, stellen: int=2, einheit_: Optional[Einheit]=None) -> str
```

Formatiert den Zahlenwert (ohne Einheit) mit fester Nachkommastellenzahl.

Nachlaufende Nullen werden entfernt, damit `18.70` als `18.7`
erscheint -- so wie es im Bericht gelesen werden soll.

#### Groesse.als_latex

```python
def als_latex(self, stellen: int=2, einheit_: Optional[Einheit]=None) -> str
```

Formatierter Zahlenwert samt Einheit als LaTeX-Fragment.

#### Groesse._pruefe_dimension

```python
def _pruefe_dimension(self, andere: Dimension, aktion: str) -> None
```

Strenge Dimensionspruefung -- fuer Vergleiche und Umrechnungen.

#### Groesse._vertraegliche_anzeige

```python
def _vertraegliche_anzeige(self, andere: 'Groesse', aktion: str) -> Einheit
```

Prueft Addierbarkeit und waehlt die Anzeige-Einheit des Resultats.

Eine dimensionslose Null gilt als neutrales Element und darf zu jeder
Groesse addiert werden -- sonst waere `summe([])` oder das Aufsummieren
einer anfangs leeren Liste unnoetig umstaendlich. Die Anzeige-Einheit
kommt dann vom dimensionsbehafteten Operanden.

### null

```python
def null(anzeige: Einheit=EINHEITSLOS) -> Groesse
```

Nullgroesse in der gewuenschten Einheit.

### summe

```python
def summe(groessen: Iterable[Groesse], anzeige: Optional[Einheit]=None) -> Groesse
```

Summiert Groessen und liefert bei leerer Eingabe eine passende Null.

`sum()` von Python startet bei `0` und funktioniert deshalb nicht
zuverlaessig mit Groessen.

### EmpirischeEinsetzung

```python
@dataclass(frozen=True)
class EmpirischeEinsetzung
```

Protokolliert, in welcher Einheit ein Wert in eine Normformel einging.

- `name: str`
- `groesse: Groesse`
- `erwartete_einheit: Einheit`

#### EmpirischeEinsetzung.zahlenwert

```python
@property
def zahlenwert(self) -> float
```

### EmpirischesErgebnis

```python
@dataclass(frozen=True)
class EmpirischesErgebnis
```

Resultat einer empirischen Formel samt der getroffenen Annahmen.

- `wert: Groesse`
- `einsetzungen: Tuple[EmpirischeEinsetzung, ...]`
- `ergebnis_einheit: Einheit`

#### EmpirischesErgebnis.einheiten

```python
@property
def einheiten(self) -> Dict[str, Einheit]
```

Je Eingabe die Einheit, in der sie als blanke Zahl einging.

### empirisch

```python
def empirisch(funktion: Callable[..., float], *, ergebnis: Einheit, **eingaben: Tuple[Groesse, Einheit]) -> EmpirischesErgebnis
```

Wertet eine dimensionell inhomogene Normformel kontrolliert aus.

Jede Eingabe wird als Paar `(Groesse, erwartete Einheit)` uebergeben. Die
Groesse wird in genau diese Einheit umgerechnet (mit Dimensionspruefung!),
als blanke Zahl in `funktion` eingesetzt, und das Resultat bekommt die
deklarierte Ergebnis-Einheit.

So bleibt die Einheiten-Konvention der Norm explizit und nachvollziehbar,
statt als unsichtbare Annahme im Code zu verschwinden.

Beispiel -- SIA 262:2025, 2.4.2.4:

```python
erg = empirisch(
    lambda f_ck, gamma_c: 0.3 * math.sqrt(f_ck) / gamma_c,
    ergebnis=N_PRO_MM2,
    f_ck=(f_ck_groesse, N_PRO_MM2),
    gamma_c=(gamma_c_groesse, EINHEITSLOS),
)
print(erg.wert)            # z.B. '1.0 N/mm^2'
print(erg.einheiten)       # {'f_ck': N/mm^2, 'gamma_c': -}
```


## Konstanten

- `DIMENSIONSLOS = Dimension()`
- `LAENGE = Dimension(laenge=1)`
- `MASSE = Dimension(masse=1)`
- `ZEIT = Dimension(zeit=1)`
- `TEMPERATUR = Dimension(temperatur=1)`
- `FLAECHE = LAENGE ** 2`
- `VOLUMEN = LAENGE ** 3`
- `KRAFT = MASSE * LAENGE / ZEIT ** 2`
- `SPANNUNG = KRAFT / FLAECHE`
- `MOMENT = KRAFT * LAENGE`
- `KRAFT_PRO_LAENGE = KRAFT / LAENGE`
- `MOMENT_PRO_LAENGE = MOMENT / LAENGE`
- `DICHTE = MASSE / VOLUMEN`
- `FLAECHE_PRO_LAENGE = FLAECHE / LAENGE`
- `KRUEMMUNG = DIMENSIONSLOS / LAENGE`
- `_HOCHGESTELLT = {'1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵', '6': '⁶', '7': '⁷'…` – Hochgestellte Ziffern, soweit es sie als eigenes Zeichen gibt.
- `EINHEITSLOS = Einheit('-', DIMENSIONSLOS, 1.0, latex='')`
- `PROZENT = Einheit('%', DIMENSIONSLOS, 0.01, latex='\\%')`
- `PROMILLE = Einheit('promille', DIMENSIONSLOS, 0.001, latex='\\text{‰}', beschrif…`
- `M = Einheit('m', LAENGE, 1.0)`
- `DM = Einheit('dm', LAENGE, 0.1)`
- `CM = Einheit('cm', LAENGE, 0.01)`
- `MM = Einheit('mm', LAENGE, 0.001)`
- `KM = Einheit('km', LAENGE, 1000.0)`
- `M2 = Einheit('m^2', FLAECHE, 1.0)`
- `CM2 = Einheit('cm^2', FLAECHE, 0.0001)`
- `MM2 = Einheit('mm^2', FLAECHE, 1e-06)`
- `M3 = Einheit('m^3', VOLUMEN, 1.0)`
- `MIO_MM3 = Einheit('10^6 mm^3', LAENGE ** 3, 0.001, latex='\\cdot 10^{6}\\,\\mat…` – Widerstandsmoment in Millionen mm^3 -- aus demselben Grund wie darunter.
- `MIO_MM4 = Einheit('10^6 mm^4', LAENGE ** 4, 1e-06, latex='\\cdot 10^{6}\\,\\mat…` – Flaechenmoment zweiten Grades in Millionen mm^4. Bei Betonquerschnitten stuende in mm^4 eine zehnstellige Zahl; so heisst es «5400 · 10⁶ mm⁴».
- `N = Einheit('N', KRAFT, 1.0)`
- `KN = Einheit('kN', KRAFT, 1000.0)`
- `MN = Einheit('MN', KRAFT, 1000000.0)`
- `PA = Einheit('Pa', SPANNUNG, 1.0)`
- `KPA = Einheit('kPa', SPANNUNG, 1000.0)`
- `MPA = Einheit('MPa', SPANNUNG, 1000000.0)`
- `GPA = Einheit('GPa', SPANNUNG, 1000000000.0)`
- `N_PRO_MM2 = Einheit('N/mm^2', SPANNUNG, 1000000.0, latex='\\mathrm{N}/\\mathrm{mm…`
- `KN_PRO_M2 = Einheit('kN/m^2', SPANNUNG, 1000.0, latex='\\mathrm{kN}/\\mathrm{m}^{…`
- `NM = Einheit('Nm', MOMENT, 1.0)`
- `KNM = Einheit('kNm', MOMENT, 1000.0)`
- `MNM = Einheit('MNm', MOMENT, 1000000.0)`
- `KN_PRO_M = Einheit('kN/m', KRAFT_PRO_LAENGE, 1000.0, latex='\\mathrm{kN}/\\mathr…`
- `KNM_PRO_M = Einheit('kNm/m', MOMENT_PRO_LAENGE, 1000.0, latex='\\mathrm{kNm}/\\ma…`
- `MM2_PRO_M = Einheit('mm^2/m', FLAECHE_PRO_LAENGE, 1e-06, latex='\\mathrm{mm}^{2}/…`
- `PRO_M = Einheit('1/m', KRUEMMUNG, 1.0, latex='\\mathrm{m}^{-1}', beschriftung…`
- `KNM2 = Einheit('kNm^2', MOMENT * LAENGE, 1000.0, latex='\\mathrm{kNm}^{2}', …`
- `KNM_PRO_RAD = Einheit('kNm/rad', MOMENT, 1000.0, latex='\\mathrm{kNm}/\\mathrm{rad}…`
- `KG = Einheit('kg', MASSE, 1.0)`
- `T = Einheit('t', MASSE, 1000.0)`
- `KG_PRO_M3 = Einheit('kg/m^3', DICHTE, 1.0, latex='\\mathrm{kg}/\\mathrm{m}^{3}')`
- `KN_PRO_M3 = Einheit('kN/m^3', KRAFT / VOLUMEN, 1000.0, latex='\\mathrm{kN}/\\math…`
- `S = Einheit('s', ZEIT, 1.0)`
- `MIN = Einheit('min', ZEIT, 60.0)`
- `H = Einheit('h', ZEIT, 3600.0)`
- `RAD = Einheit('rad', DIMENSIONSLOS, 1.0)`
- `GRAD = Einheit('Grad', DIMENSIONSLOS, math.pi / 180.0, latex='{}^{\\circ}', …`
- `MRAD = Einheit('mrad', DIMENSIONSLOS, 0.001)` – Tausendstel Radiant -- die Drehungen eines Stabwerks.
- `EINHEITEN = {e.name: e for e in (EINHEITSLOS, PROZENT, PROMILLE, M, DM, CM, MM, K…` – Alle benannten Einheiten, nach Namen auffindbar.

## Gebraucht von

- [[opencivil.bericht.zusammenfassung]]
- [[opencivil.core.berechnung]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.rechenwerk]]
- [[opencivil.core.wert]]
- [[opencivil.geotechnik.grundbruch]]
- [[opencivil.material.basis]]
- [[opencivil.material.beton]]
- [[opencivil.material.betonstahl]]
- [[opencivil.nachweis.biegung_normalkraft]]
- [[opencivil.nachweis.duktilitaet]]
- [[opencivil.nachweis.fehlende_bewehrung]]
- [[opencivil.nachweis.kennzahlen]]
- [[opencivil.nachweis.knicken]]
- [[opencivil.nachweis.linie]]
- [[opencivil.nachweis.mindestbewehrung]]
- [[opencivil.nachweis.qa_gebrauch]]
- [[opencivil.nachweis.qa_knicken]]
- [[opencivil.nachweis.querkraft]]
- [[opencivil.nachweis.resistenzlinie]]
- [[opencivil.nachweis.richtungsnachweise]]
- [[opencivil.nachweis.rissgroessen]]
- [[opencivil.nachweis.schiefe_biegung]]
- [[opencivil.nachweis.schubwandnachweis]]
- [[opencivil.nachweis.spannungsbegrenzung]]
- [[opencivil.nachweis.spannungsgrenzen]]
- [[opencivil.nachweis.sproedes_versagen]]
- [[opencivil.nachweis.verformung]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.balkensystem]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.grundbruch]]
- [[opencivil.projekt.lesen]]
- [[opencivil.projekt.platte]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.platte]]
- [[opencivil.spannungsanalyse.herleitung]]
- [[opencivil.spannungsanalyse.platte]]
- [[opencivil.spannungsanalyse.schnitt]]
- [[opencivil.stabwerk.querschnitte]]
- [[opencivil.stabwerk.rechnung]]
- [[opencivil.web.api]]
- [[opencivil.web.diagrammdaten]]
