---
erzeugt: e22c969f9e9b
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/querschnittsanalyse.py
> ein gezeichneter Querschnitt, wie die Oberflaeche ihn beschreibt.
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/querschnittsanalyse.py)

## VERANTWORTUNG

Der [[opencivil.projekt.querschnittsanalyse#QuerschnittsanalyseEintrag|QuerschnittsanalyseEintrag]]: Knoten, Polygone mit Material, Staebe
und Stablinien, Schubwaende, Hilfslinien, die Wahl der Werkstoffgesetze, die
Lastfaelle und die Schalter der Nachweise -- als eine speicherbare
Datenklasse, wie die Platte in [[opencivil.projekt.platte]]. Dazu die
Vorlage einer frischen Analyse und ein Baukasten, der ohne Oberflaeche
zeichnet ([[opencivil.projekt.querschnittsanalyse#QuerschnittsanalyseEintrag.polygon|QuerschnittsanalyseEintrag.polygon]] und folgende).


## KNOTEN

Die Elemente tragen keine eigenen Koordinaten, sie verweisen auf Knoten --
ein Polygon auf seine Ecken, ein Stab auf seine Lage, eine Linie auf Anfang
und Ende. Wer einen Knoten verschiebt, verschiebt alles, was an ihm haengt.
Jedes Element hat eine Kennung, die nie wiederkommt ([[opencivil.projekt.netz]]):
K fuer Knoten, F fuer Flaechen, S fuer Staebe, L fuer alle Linien.


## KOORDINATEN UND EINHEITEN

y nach rechts, z nach oben, alles in Millimetern -- so, wie gezeichnet und
eingetippt wird. Schnittgroessen in kN und kNm. Umgerechnet wird beim Bauen.


## VORZEICHEN DER LASTFAELLE

N > 0 Zug. Ein positives Moment zieht auf der negativen Seite seiner Achse:
M_y > 0 unten (wie bei der Platte), M_z > 0 links. V_y und V_z wirken in
Achsrichtung, T im Gegenuhrzeigersinn.


## WAS HIER NICHT GEPRUEFT WIRD

Ob die Polygone sich ueberlappen, ob ein Stab im Beton liegt: das prueft der
Aufbau. Eine abgelegte Analyse mit einem verunglueckten Polygon soll sich
oeffnen und korrigieren lassen -- dasselbe Vorgehen wie bei den Abmessungen
der Platte ([[opencivil.projekt.platte#QuerschnittEintrag.regeln|QuerschnittEintrag.regeln]]).

## Inhalt

### _punkt

```python
def _punkt(roh: Any, wo: str) -> List[float]
```

Ein Punkt `[y, z]` -- zwei Zahlen, sonst ein Satz, was fehlt.

### KnotenEintrag

```python
@dataclass
class KnotenEintrag(Beschreibung)
```

Ein Punkt der Zeichnung, in mm. Die Elemente verweisen mit seiner Kennung auf ihn.

- `kennung: str = ''`
- `y: float = 0.0`
- `z: float = 0.0`

### FlaecheEintrag

```python
@dataclass
class FlaecheEintrag(Beschreibung)
```

Ein Polygon des Querschnitts. Ohne Material ist es eine Aussparung.

- `kennung: str = ''`
- `knoten: List[str] = field(default_factory=list)` – Die Ecken als Knoten, der Reihe nach; die erste wird am Ende nicht wiederholt.
- `material: str = ''` – Kennung des Materials; leer heisst Aussparung.

#### FlaecheEintrag.ist_aussparung

```python
@property
def ist_aussparung(self) -> bool
```

### StabEintrag

```python
@dataclass
class StabEintrag(Beschreibung)
```

Ein einzelner Bewehrungsstab, an einem Knoten.

- `kennung: str = ''`
- `knoten: str = ''`
- `durchmesser: float = 16.0`
- `stahl: str = ''`

### StablinieEintrag

```python
@dataclass
class StablinieEintrag(Beschreibung)
```

Eine Linie von Staeben -- oder eine verschmierte Stahlflaeche.

Je Art ein eigenes Feld fuer die Menge: wer die Art wechselt und wieder
zurueck, findet seine Zahl noch vor. Welche gilt, sagt `art`.

- `kennung: str = ''`
- `von: str = ''`
- `bis: str = ''` – Anfang und Ende als Knoten.
- `art: Linienart = Linienart.TEILUNG`
- `durchmesser: float = 16.0` – Bei Anzahl und Teilung der Stabdurchmesser in mm.
- `flaeche: float = 1000.0` – Bei Art «Fläche» die ganze Stahlflaeche der Linie in mm².
- `anzahl: float = 5.0`
- `teilung: float = 150.0` – Bei Art «Teilung» der Wunschabstand in mm -- gerundet auf einen, der aufgeht.
- `starteisen: bool = True`
- `endeisen: bool = True`
- `stahl: str = ''`

### SchubwandEintrag

```python
@dataclass
class SchubwandEintrag(Beschreibung)
```

Eine Schubwand: eine Linie ueber dem Querschnitt, mit Dicke und Buegeln.

Ihre Laenge ist der Hebelarm des Fachwerks -- gezeichnet wird sie darum
von Gurt zu Gurt. Die Teilung `s` gilt in Laengsrichtung des Bauteils;
im Schnitt ist sie nicht zu sehen.

- `kennung: str = ''`
- `von: str = ''`
- `bis: str = ''` – Anfang und Ende als Knoten. Die Richtung zaehlt: sie gibt dem Schubfluss sein Vorzeichen.
- `dicke: float = 200.0` – `b_w` in mm.
- `durchmesser: float = 10.0` – Buegeldurchmesser in mm.
- `teilung: float = 150.0` – Buegelteilung in Laengsrichtung in mm.
- `schnitte: int = einer_von(SCHNITTE, 2)` – Wie viele Buegelschenkel die Wand kreuzen, 1 bis 8.
- `stahl: str = ''`

### HilfslinieEintrag

```python
@dataclass
class HilfslinieEintrag(Beschreibung)
```

Eine Linie, die nur der Konstruktion dient: an ihr fangen, an ihr messen.
Gerechnet wird mit ihr nicht. Geschlossene Hilfslinien lassen sich im
Zeichenfenster zu einer Flaeche machen.

- `kennung: str = ''`
- `von: str = ''`
- `bis: str = ''`

### QALastfallEintrag

```python
@dataclass
class QALastfallEintrag(Beschreibung)
```

Ein Lastfall der Querschnittsanalyse -- kN und kNm, Vorzeichen siehe oben.

- `name: str`
- `N_Ed: float = 0.0`
- `M_y_Ed: float = 0.0`
- `M_z_Ed: float = 0.0`
- `V_y_Ed: float = 0.0`
- `V_z_Ed: float = 0.0`
- `T_Ed: float = 0.0`
- `aktiv: bool = True`

### QAGebrauchsfallEintrag

```python
@dataclass
class QAGebrauchsfallEintrag(Beschreibung)
```

Ein Lastfall unter Gebrauchslast -- wie ein Lastfall der Tragsicherheit,
ohne Querkraft und Torsion: begrenzt wird die Stahlspannung, und dafuer
zaehlen N und die Momente. kN und kNm, Vorzeichen siehe oben.

- `name: str`
- `N_Ed: float = 0.0`
- `M_y_Ed: float = 0.0`
- `M_z_Ed: float = 0.0`
- `aktiv: bool = True`

### QAGebrauchswahl

```python
@dataclass
class QAGebrauchswahl(Gebrauchswahl)
```

Die Stahlspannungen am gezeichneten Querschnitt: ueber die Fasern oder elastisch -- ohne Handrechnung.

- `rechenart: Rechenart = einer_von(FASERSPANNUNGSARTEN, Rechenart.ELASTISCH)`

### QAGebrauchsliste

```python
@dataclass
class QAGebrauchsliste(Gebrauchsliste)
```

Die Lastfaelle einer Stahlspannung am gezeichneten Querschnitt: dieselbe
Liste wie bei der Platte, mit N, M_y und M_z je Fall, abgeleitet aus den
Lastfaellen der Tragsicherheit. Gerechnet wird ueber die Fasern -- eine
Handrechnung gibt es hier nicht.

- `FALL = QAGebrauchsfallEintrag`
- `BAUTEIL = 'Querschnitt'`
- `faelle: List[QAGebrauchsfallEintrag] = field(default_factory=list)`
- `wahl: QAGebrauchswahl = field(default_factory=QAGebrauchswahl)`

### QAKnickEintrag

```python
@dataclass
class QAKnickEintrag(KnickEintrag)
```

Ein Knicknachweis des gezeichneten Querschnitts -- wie bei der Platte,
dazu die Zugseite: die Seite, zu der sich der Stab biegt und die das
Moment 1. Ordnung zieht ([[opencivil.querschnitt.zugseite#Zugseite|Zugseite]]).

- `richtung: Zugseite = Zugseite.UNTEN`

### WerkstoffwahlEintrag

```python
@dataclass
class WerkstoffwahlEintrag(Beschreibung)
```

Mit welchen Werten ein Material in dieser Analyse rechnet.

`satz`: Bemessungs- oder charakteristische Werte -- das legt fest, wo
die Plateaus liegen (`f_cd` oder `f_ck`, `f_yd` oder `f_yk`).
`betongesetz`: beim Beton die Parabel-Rechteck-Beziehung oder der
vereinfachte Spannungsblock 0.85·x.

- `material: str`
- `satz: Werkstoffsatz = Werkstoffsatz.BEMESSUNG`
- `betongesetz: Rechenart = einer_von((Rechenart.PARABEL, Rechenart.BLOCK), Rechenart.PARABEL)` – Die beiden genauen Rechenarten -- die Parabel zuerst, sie ist die Vorgabe.

#### WerkstoffwahlEintrag.rechenwahl

```python
@property
def rechenwahl(self) -> Rechenwahl
```

Fuer die Rechnung: Wertesatz und Rechenart, ohne Kriechen -- der Bruchzustand.

### QASpannungsfallEintrag

```python
@dataclass
class QASpannungsfallEintrag(SpannungsfallEintrag)
```

Eine Spannung-Dehnung-Analyse des gezeichneten Querschnitts -- dieselben
Felder wie bei der Platte. Die Richtung ist hier die Zugseite: die Seite,
die ein positives Moment zieht ([[opencivil.querschnitt.zugseite#Zugseite|Zugseite]]).

- `richtung: Zugseite = Zugseite.UNTEN`

### Elemente

```python
@dataclass(frozen=True)
class Elemente
```

Die Elemente einer Analyse, so wie der Kern sie prueft und rechnet:
Koordinaten in mm, und je Element `name` und `kennung`.

Der Name zaehlt je Art ab 1 -- «Polygon 1», «Aussparung 2», «Stab 1»,
«Linie 1», «Wand 3» -- und steht so in Berichten und Meldungen. Die
Kennung ist die des Elements (`F1`, `L4`); an ihr erkennt die
Oberflaeche, welches gemeint ist. Die Namen werden hier vergeben und
nirgends sonst -- vorher entstanden sie an fuenf Stellen.

Ein Element, das auf einen Knoten verweist, den es nicht gibt, steht in
keiner Liste, sondern in `fehler`. Sein Name bleibt reserviert: die
Elemente danach heissen weiter so wie vorher.

- `polygone: List[dict]` – Je Polygon `punkte` und `material` (leer: Aussparung).
- `staebe: List[dict]` – Je Stab `lage`, `durchmesser` und `stahl`.
- `linien: List[dict]` – Je Stablinie die Felder der Beschreibung, `von` und `bis` als Punkte.
- `waende: List[dict]` – Je Schubwand die Felder der Beschreibung, `von` und `bis` als Punkte.
- `hilfslinien: List[dict] = field(default_factory=list)` – Je Hilfslinie `von` und `bis` -- gerechnet wird mit ihnen nichts.
- `fehler: List[dict] = field(default_factory=list)` – Was sich nicht aufloesen liess: `text` und `elemente` (Kennungen), wie eine Meldung.

### QuerschnittsanalyseEintrag

```python
@dataclass
class QuerschnittsanalyseEintrag(Beschreibung)
```

Ein gezeichneter Querschnitt mit Bewehrung, Schubwaenden und Lastfaellen.

- `BEZEICHNUNG = 'Querschnitt'`
- `kennung: str`
- `name: str`
- `knoten: List[KnotenEintrag] = field(default_factory=list)`
- `flaechen: List[FlaecheEintrag] = field(default_factory=list)`
- `staebe: List[StabEintrag] = field(default_factory=list)`
- `stablinien: List[StablinieEintrag] = field(default_factory=list)`
- `schubwaende: List[SchubwandEintrag] = field(default_factory=list)`
- `hilfslinien: List[HilfslinieEintrag] = field(default_factory=list)`
- `werkstoffwahl: List[WerkstoffwahlEintrag] = field(default_factory=list)` – Je Material eine Wahl; fehlt eine, gelten die Vorgaben.
- `lastfaelle: List[QALastfallEintrag] = field(default_factory=list)`
- `einachsig: bool = False` – Nur Biegung um y: die Nulllinie bleibt waagrecht, M_z und V_y zaehlen nicht, und Duktilitaet und sproedes Versagen gibt es nur in y. Torsion bleibt. Bei einem unsymmetrischen Querschnitt ist das eine Naeherung -- dasselbe, was die Platte immer tut.
- `alpha_min: int = neigung(ALPHA_MIN, 'α_min')`
- `alpha_max: int = neigung(ALPHA_MAX, 'α_max')`
- `k_c: float = druckfeld()` – Grenzen der Druckfeldneigung und Abminderung der Druckdiagonalen -- wie bei der Platte.
- `laengszugkraft: bool = False` – Ob die Laengszugkraft aus Querkraft und Torsion in den M-N-Nachweis eingeht: das Druckfeld jeder Schubwand braucht in Laengsrichtung Zug.
- `duktilitaet: bool = False`
- `x_d_max: float = x_d_grenze()`
- `sproede: bool = False`
- `rissanforderung: Rissanforderung = Rissanforderung.NORMAL` – Anforderung an die Rissbildung -- `normal`, `erhoeht` oder `hoch`, wie bei der Platte.
- `zwaengung: bool = False` – Ob die Zwaengung auf Normalkraft nachgewiesen wird -- am ganzen Querschnitt.
- `zwaengung_begrenzt: bool = False` – Ob die rissaktive Dicke dabei hoechstens 500 mm betraegt.
- `zwaengung_biegung: bool = False` – Ob die Zwaengung auf Biegung nachgewiesen wird -- je Richtung.
- `zwaengung_biegung_kriechzahl: float = bereich(0.0, heisst='Kriechzahl φ', ab=0.0)` – Die Kriechzahl φ der Zwaengung auf Biegung: der Beton mit `E_cm/(1+φ)`.
- `quasistaendig: QAGebrauchsliste = field(default_factory=lambda: QAGebrauchsliste(anteil=QUASISTAENDIG_A…` – Die quasi-staendigen Lastfaelle -- fuer die Rissbreite.
- `haeufig: QAGebrauchsliste = field(default_factory=lambda: QAGebrauchsliste(anteil=HAEUFIG_ANTEIL))` – Die haeufigen Lastfaelle -- gegen das Fliessen, bei erhoehter und hoher Anforderung.
- `knickfaelle: List[QAKnickEintrag] = field(default_factory=list)` – Knicknachweise, je in einer Richtung; leer heisst: keiner.
- `knicken_wahl_verformung: KnickVerformungswahl = field(default_factory=KnickVerformungswahl)`
- `knicken_wahl_widerstand: KnickWiderstandswahl = field(default_factory=KnickWiderstandswahl)` – Womit das Knicken die Ausmitte e_2d und den Widerstand rechnet -- wie bei der Platte: die Verformung immer praezise, der Widerstand mit 0.85·x oder praezise.
- `spannungsfaelle: List[QASpannungsfallEintrag] = field(default_factory=list)` – Die Spannung-Dehnung-Analysen -- kein Nachweis, ein Blick in den Querschnitt.
- `beschreibung: str = ''` – Freier Text -- geht in keine Rechnung ein, wie bei der Platte.

#### QuerschnittsanalyseEintrag.wahl

```python
def wahl(self, material: str) -> WerkstoffwahlEintrag
```

Die Wahl fuer dieses Material -- die Vorgaben, wenn keine dasteht.

#### QuerschnittsanalyseEintrag.materialien

```python
def materialien(self) -> List[str]
```

Jedes Material, auf das die Analyse zeigt, in der Reihenfolge des
ersten Auftretens. Jeder Verweis zaehlt, auch einer, der gerade nichts traegt: wer das
Material loescht, liesse ihn ins Leere zeigen, und spaetestens die
naechste Aenderung machte daraus einen Fehler beim Rechnen.

#### QuerschnittsanalyseEintrag.bezuege

```python
def bezuege(self) -> List[str]
```

Die Bauteile, deren Querschnitt die Analyse nimmt -- keine.

#### QuerschnittsanalyseEintrag.elemente

```python
def elemente(self) -> Elemente
```

Die Elemente mit Name und Kennung, Koordinaten in mm -- siehe [[opencivil.projekt.querschnittsanalyse#Elemente|Elemente]].

#### QuerschnittsanalyseEintrag.netz

```python
def netz(self) -> Netz
```

Die Knoten zum Weiterzeichnen: gleiche Koordinaten sind ein Knoten.

#### QuerschnittsanalyseEintrag._knoten

```python
def _knoten(self, netz: Netz, ort: Ort) -> str
```

Ein Knoten aus einem Punkt `[y, z]` -- oder die Kennung, wenn schon eine dasteht.

#### QuerschnittsanalyseEintrag._kennung

```python
def _kennung(self, vorsilbe: str) -> str
```

Die naechste Kennung -- alle Linien zaehlen gemeinsam, ob Bewehrung, Wand oder Hilfslinie.

#### QuerschnittsanalyseEintrag.polygon

```python
def polygon(self, punkte: Sequence[Ort], material: str='') -> FlaecheEintrag
```

Ein Polygon aus Ecken `[y, z]` in mm; ohne Material eine Aussparung.

#### QuerschnittsanalyseEintrag.stab

```python
def stab(self, y: float, z: float, **felder: Any) -> StabEintrag
```

Ein einzelner Stab bei `(y, z)` -- `durchmesser`, `stahl`.

#### QuerschnittsanalyseEintrag.stablinie

```python
def stablinie(self, von: Ort, bis: Ort, **felder: Any) -> StablinieEintrag
```

Eine Stablinie; die Felder wie [[opencivil.projekt.querschnittsanalyse#StablinieEintrag|StablinieEintrag]].

#### QuerschnittsanalyseEintrag.schubwand

```python
def schubwand(self, von: Ort, bis: Ort, **felder: Any) -> SchubwandEintrag
```

Eine Schubwand; die Felder wie [[opencivil.projekt.querschnittsanalyse#SchubwandEintrag|SchubwandEintrag]].

#### QuerschnittsanalyseEintrag.hilfslinie

```python
def hilfslinie(self, von: Ort, bis: Ort) -> HilfslinieEintrag
```

Eine Hilfslinie -- nur zum Konstruieren, gerechnet wird mit ihr nicht.

#### QuerschnittsanalyseEintrag.lage

```python
def lage(self, kennung: str) -> Optional[Tuple[float, float]]
```

Wo ein Knoten liegt, in mm -- `None`, wenn es ihn nicht gibt.

#### QuerschnittsanalyseEintrag.vorlage_einsetzen

```python
def vorlage_einsetzen(self, schluessel: str, *, beton: str, stahl: str, masse: Optional[Mapping[str, float]]=None, randabstand: float=50.0, bewehrung: bool=True, schubwaende: bool=True, ursprung: Tuple[float, float]=(0.0, 0.0)) -> List[str]
```

Setzt eine Vorlage ein ([[opencivil.querschnitt.vorlagen]]) -- dazu,
nicht anstatt: was schon gezeichnet ist, bleibt, und wo ein Punkt der
Vorlage genau auf einem Knoten liegt, haengt sie an ihm. `ursprung`
ist, wohin ihre Ecke unten links kommt; die Lagen auf einen
Millionstel Millimeter wie im Zeichenfenster, damit die Summe keinen
Rundungsrest behaelt. Gibt die Kennungen der neuen Elemente zurueck.
Passen die Masse nicht zueinander, ein `ValueError` mit dem Grund.

#### QuerschnittsanalyseEintrag.regeln

```python
def regeln(self, wo: str) -> None
```

Was erst das Rechnen braucht, wie bei der Platte
([[opencivil.projekt.querschnittsanalyse#QuerschnittsanalyseEintrag|QuerschnittEintrag.regeln]]): eine abgelegte Analyse
mit einer unmoeglichen Grenze soll sich oeffnen und korrigieren
lassen. Bis 2026-10-16 rechnete sie mit α_min > α_max, k_c \< 0 und
x/d = 0.9.

#### QuerschnittsanalyseEintrag.lastfall

```python
def lastfall(self, name: str, **werte: float) -> QALastfallEintrag
```

Einen Lastfall anfuegen, ohne Oberflaeche -- kN und kNm.

#### QuerschnittsanalyseEintrag.knickfall

```python
def knickfall(self, name: str, *, N_Ed: float, M_Ed_1: float=0.0, laenge: float=3.0, knicklaenge: Optional[float]=None, richtung: str=Zugseite.UNTEN.value) -> QAKnickEintrag
```

Ein Knicknachweis -- N_Ed in kN (Druck negativ), Längen in m, die Zugseite.

#### QuerschnittsanalyseEintrag.spannungsfall

```python
def spannungsfall(self, name: str, *, art: str='schnittgroessen', **felder: Any) -> QASpannungsfallEintrag
```

Eine Spannung-Dehnung-Analyse -- Felder wie bei der Platte, die
Richtung als Zugseite (`unten`, `oben`, `links`, `rechts`).
Gelesen wie aus einer Datei, also mit denselben Pruefungen.

#### QuerschnittsanalyseEintrag.neu

```python
@classmethod
def neu(cls, kennung: str, name: str, beton: str, stahl: str) -> 'QuerschnittsanalyseEintrag'
```

Eine frische Analyse, wie der Benutzer sie angelegt bekommt.

Ein Rechteck 300 × 600 mm, unten drei, oben zwei Staebe, und ein
Lastfall mit Feldmoment. Zum Anfangen, nicht als Vorgabe: gezeichnet
wird danach, was man braucht.


## Konstanten

- `SCHNITTE = range(1, 9)` – Schnitte eines Buegels durch eine Schubwand: so viele Schenkel kreuzen sie.
- `Ort = Union[str, Sequence[float]]` – Ein Punkt in mm -- oder die Kennung eines Knotens, der dort liegt.

## Braucht

- [[opencivil.nachweis.rechenwahl]]
- [[opencivil.nachweis.rissanforderung]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.lesen]]
- [[opencivil.projekt.netz]]
- [[opencivil.querschnitt.geometrie]]
- [[opencivil.querschnitt.gesetzwahl]]
- [[opencivil.querschnitt.platte]]
- [[opencivil.querschnitt.vorlagen]]
- [[opencivil.querschnitt.zugseite]]

## Gebraucht von

- [[opencivil.projekt]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.projekt]]
- [[opencivil.web.api]]
