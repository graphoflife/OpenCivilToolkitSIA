---
erzeugt: 08743d44b0bb
art: modul
tags: [modul]
---
> [!abstract] opencivil/core/protokoll.py
> Mitschrift einer Berechnung.
> Paket [[opencivil.core]] · [Quelltext](../../opencivil/core/protokoll.py)

## VERANTWORTUNG

Eine Berechnung schreibt waehrend des Rechnens in ein Protokoll. Rechenschritt
und seine Darstellung entstehen dadurch am selben Ort und koennen nicht
auseinanderlaufen -- man kann nicht das eine rechnen und das andere aufschreiben.

Genau das braucht eine Prozedur: eine Iteration soll nicht nur ihr Resultat
liefern, sondern auch ihren Ablauf zeigen -- Startwerte, Zwischenschritte in
einer Tabelle, Abbruchkriterium. Ein Leser muss die Rechnung von Hand
nachvollziehen koennen.

Das Protokoll ist reine Datenstruktur. Ob daraus Konsolentext, ein LaTeX-
Dokument oder HTML wird, entscheidet erst der Bericht -- jede Darstellung mit
einer Tafel, die fuer jede Blockart sagt, wie sie gesetzt wird (siehe
[[opencivil.core.protokoll#darstellen|darstellen]]).


## STILLES PROTOKOLL

In heissen Schleifen (z.B. beim punktweisen Aufbau einer M-N-Interaktionslinie
mit hunderten Dehnungsebenen) will man nichts mitschreiben. Dafuer gibt es
[[opencivil.core.protokoll#StillesProtokoll|StillesProtokoll]] -- dieselbe Schnittstelle, verwirft aber alles.

## Inhalt

### HinweisArt

```python
class HinweisArt(str, Enum)
```

- `INFO = 'info'`
- `WARNUNG = 'warnung'`
- `ANNAHME = 'annahme'`

#### HinweisArt.beschriftung

```python
@property
def beschriftung(self) -> str
```

### Block

```python
@dataclass
class Block
```

Basis aller Protokollbausteine.

### Abschnitt

```python
@dataclass(frozen=True)
class Abschnitt
```

Ueberschrift eines Bauteils oder Baustoffs samt seinem Namensraum.

Beides gehoert zusammen: der Titel ist fuer den Leser, der Namensraum fuer
die Oberflaeche, die danach filtert.

- `titel: str`
- `raum: str`
- `thema: str = ''` – Unter welchem Thema die Formeln des Abschnitts in der Formelsammlung stehen, sofern die Berechnung keines mitbringt -- «Beton», «Querschnitt».

### TitelBlock

```python
@dataclass
class TitelBlock(Block)
```

- `text: str`
- `ebene: int = 2`
- `raum: str = ''` – Namensraum des Abschnitts, den dieser Titel eroeffnet -- leer, wenn er keinen eroeffnet. Die Oberflaeche grenzt die Herleitung damit auf den gewaehlten Bestandteil ein. Ueber den Anzeigetext ginge das auch, aber ein Vergleich ueber Beschriftungen ist immer eine Falle: er bricht, sobald jemand den Text aendert, und er bricht stumm.

#### TitelBlock.abschnitt

```python
@property
def abschnitt(self) -> bool
```

### TextBlock

```python
@dataclass
class TextBlock(Block)
```

Fliesstext zwischen den Formeln.

- `text: str`
- `erklaerung: bool = False` – Ob der Text erklaert, statt ein Ergebnis zu nennen -- das 'Warum'. Erklaerungen stehen nicht in der Herleitung (siehe [[opencivil.core.protokoll#darstellen|darstellen]]), sondern in der Formelsammlung unter den Formeln ihres Themas. Die Herleitung zeigt Formeln, Zahlen und Stichworte.
- `thema: str = ''` – Thema der Berechnung, die den Block schrieb -- vom Rechenwerk gestempelt.

### GleichungBlock

```python
@dataclass
class GleichungBlock(Block)
```

Eine gesetzte Formel.

- `latex: str`
- `titel: str = ''`
- `referenz: str = ''`
- `wert_id: str = ''` – ID des erzeugten Wertes, falls die Gleichung einen Wert liefert.
- `gruppe: str = ''` – Name eines Kastens, in dem mehrere Angaben zusammenstehen sollen. Vier Zeilen der Form `h = 300 mm` untereinander sind kein Nachweis, sondern eine Liste. Zusammengelegt liest sie sich besser -- aber nur fuer die Darstellung: jede Angabe bleibt ihr eigener Block mit eigener `wert_id`. Das ist der Punkt. Wer die vier zu *einem* Block verschmelzen wollte, verloere die Rueckverfolgung: wird nur `h` gebraucht, laeuft auch nur dessen Vorgabe, und im Kasten steht dann eben nur `h`. Ein verschmolzener Block wuesste nichts davon und zeigte alle vier.
- `formelzeile: Optional[tex.Formelzeile] = None` – Strukturierte Fassung, sofern vorhanden -- erlaubt spaeteren Umbruch.
- `ansatz: bool = False` – Ob die Gleichung rein symbolisch ist -- ein Ansatz ohne Zahlen, etwa das Werkstoffgesetz oder die Formel, nach der gleich gerechnet wird. Die Formelsammlung nimmt sie so, wie sie dasteht.
- `thema: str = ''` – Thema der Berechnung, die den Block schrieb -- vom Rechenwerk gestempelt.
- `name: str = field(default='', compare=False)` – Name der Formel im Notizbuch -- nie Fall, Sorte, Lage oder Richtung. Leer heisst: ihr Titel ohne Zahlenangabe (siehe [[opencivil.bericht.formelsammlung#formelname|opencivil.bericht.formelsammlung.formelname]]). Gesetzt wird er, wo der Titel je nach Fall wechselt oder fuer sich nichts sagt («Ansatz»).
- `codestelle: str = field(default='', compare=False)` – Wo im Code die Gleichung geschrieben wird, als `modul:Funktion` -- das Notizbuch verlinkt damit Formel und Modul. Selbst ermittelt (siehe [[opencivil.core.protokoll#codestelle_aus|codestelle_aus]]), nur die allgemeine Formel gibt sie mit.

### TabellenBlock

```python
@dataclass
class TabellenBlock(Block)
```

Tabelle, typischerweise ein Iterationsprotokoll.

Jede Zelle ist Text (`str`) oder [[opencivil.core.protokoll#TabellenBlock|latex.Mathe]] -- die
Darstellung entscheidet, wie sie beides setzt.

- `kopf: Sequence[tex.Zelle]`
- `zeilen: Sequence[Sequence[tex.Zelle]]`
- `titel: str = ''`
- `ausrichtung: Optional[str] = None`

#### TabellenBlock.als_latex

```python
def als_latex(self) -> str
```

### HinweisBlock

```python
@dataclass
class HinweisBlock(Block)
```

- `text: str`
- `art: HinweisArt = HinweisArt.INFO`

### Protokoll

```python
class Protokoll
```

Sammelt die Bloecke einer Berechnung in der Reihenfolge ihres Entstehens.

Beispiel:

```python
p.titel("Bemessungswert der Betondruckfestigkeit")
p.formel(f_cd, r"\frac{@eta_fc \cdot @f_ck}{@gamma_c}",
         {"eta_fc": eta, "f_ck": fck, "gamma_c": gamma})
p.hinweis("Massgebend ist der abgeminderte Wert.")
```

#### Protokoll.anfuegen

```python
def anfuegen(self, *bloecke: Block) -> None
```

Fertige Bloecke uebernehmen -- etwa die Tabelle einer Zusammenfassung.

#### Protokoll.titel

```python
def titel(self, text: str, ebene: int=2, raum: str='') -> None
```

#### Protokoll.text

```python
def text(self, text: str) -> None
```

Ein Ergebnis in Worten -- knapp, es steht in der Herleitung.

#### Protokoll.erklaerung

```python
def erklaerung(self, text: str) -> None
```

Das Warum -- steht in der Formelsammlung, nicht in der Herleitung.

#### Protokoll.gleichung

```python
def gleichung(self, latex: str, titel: str='', referenz: str='') -> None
```

Setzt beliebiges, bereits fertiges LaTeX.

#### Protokoll.ansatz

```python
def ansatz(self, latex: str, titel: str='', referenz: str='', *, name: str='') -> None
```

Eine Gleichung ohne Zahlen -- sie kommt auch in die Formelsammlung.

#### Protokoll.formel

```python
def formel(self, ergebnis: Wert, vorlage: str, eingaben: Mapping[str, Wert], titel: str='', referenz: Optional[str]=None, *, empirisch: Optional[Mapping[str, Einheit]]=None, nachsatz: str='', name: str='', codestelle: str='') -> None
```

Der Regelfall: `Symbol = analytische Formel = Formel mit Zahlen = Resultat`.

Von Hand geschrieben wird nur `vorlage` (die analytische Form mit
`@name`-Platzhaltern). Die Fassung mit Zahlen und Einheiten entsteht
automatisch aus `eingaben`. Zwischenergebnisse, die keine Werte des
Rechenwerks sind, legt [[opencivil.core.protokoll#Zwischenwerte|Zwischenwerte]] an.

`empirisch` nennt die Eingaben einer dimensionell inhomogenen
Normformel mit der Einheit, in der sie als blanke Zahl eingehen
([[opencivil.core.protokoll#Protokoll|latex.einsetzen_numerisch]]). `nachsatz` steht hinter dem
Resultat, etwa ein Vergleich ([[opencivil.core.protokoll#Protokoll|latex.vergleich]]).

`name` und `codestelle` sind fuer das Notizbuch (siehe
[[opencivil.core.protokoll#GleichungBlock|GleichungBlock]]); die Codestelle ermittelt sich selbst.

#### Protokoll.wert

```python
def wert(self, ergebnis: Wert, titel: str='', referenz: Optional[str]=None, gruppe: str='', *, name: str='', codestelle: str='') -> None
```

Schlichte Form `Symbol = Wert` -- fuer Eingaben und Vorgaben.

#### Protokoll.tabelle

```python
def tabelle(self, kopf: Sequence[tex.Zelle], zeilen: Iterable[Sequence[tex.Zelle]], titel: str='', ausrichtung: Optional[str]=None) -> None
```

#### Protokoll.hinweis

```python
def hinweis(self, text: str) -> None
```

#### Protokoll.warnung

```python
def warnung(self, text: str) -> None
```

#### Protokoll.annahme

```python
def annahme(self, text: str) -> None
```

Haelt eine getroffene Annahme fest.

Dafuer gedacht, dass empirische Normformeln ihre Einheiten-Konvention
offenlegen (siehe `einheiten.empirisch`).

#### Protokoll.herkunft_stempeln

```python
def herkunft_stempeln(self, thema: str, ab: int=0) -> None
```

Das Thema auf die Bloecke ab `ab`.

Das Rechenwerk ruft das nach jeder Berechnung fuer das, was sie
geschrieben hat. Die Formelsammlung ordnet danach; die Berechnung
selbst muss nichts davon wissen. (Den Raum braucht es nicht: er
steht am Titel des Abschnitts.)

#### Protokoll.ist_leer

```python
@property
def ist_leer(self) -> bool
```

#### Protokoll.alle_bloecke

```python
def alle_bloecke(self) -> List[Block]
```

Alle Bloecke -- als Liste.

Als Liste und nicht als Generator: der Name verspricht eine Sammlung,
und wer eine Sammlung zweimal durchlaeuft, erwartet zweimal dasselbe.
Ein Generator gab beim zweiten Mal nichts zurueck, lautlos -- eine
Pruefung, die danach «nicht gefunden» meldete, obwohl es dastand.
Die Blockzahl ist die eines Berichts; sie in eine Liste zu legen
kostet nichts.

#### Protokoll.nach_abschnitten

```python
def nach_abschnitten(self) -> List[Block]
```

Dieselben Bloecke, aber je Abschnitt an einem Stueck.

Gerechnet wird in Abhaengigkeitsreihenfolge, und die springt zwischen
den Bauteilen hin und her: der Querkraftnachweis einer Platte braucht
ihren Momentenwiderstand, kommt also erst, wenn *alle* M-N-Nachweise
durch sind. Im Protokoll stand die Ueberschrift einer Platte darum
zweimal, mit der anderen Platte dazwischen.

Wer liest, erwartet alles zu einem Bauteil beieinander. Die Reihenfolge
der Abschnitte bleibt die ihres ersten Auftretens, innerhalb eines
Abschnitts bleibt die Rechenreihenfolge unangetastet -- verschoben wird
also nur, was ohnehin nur der Darstellung dient.

Eroeffnet wird ein Abschnitt von einem Titel mit Namensraum; alles
davor (und jeder Titel ohne Namensraum) gehoert zum laufenden.

#### Protokoll.gleichungen

```python
def gleichungen(self) -> List[GleichungBlock]
```

#### Protokoll.warnungen

```python
def warnungen(self) -> List[HinweisBlock]
```

### codestelle_aus

```python
def codestelle_aus(modul: str, qualname: str) -> str
```

`modul:Klasse.methode` -- so nennt das Notizbuch eine Stelle im Code.

Ohne das, was nur in einer Funktion lebt (`<locals>`, `<lambda>`):
gemeint ist die Funktion, in der es steht. Eine Lambda auf Modulebene
heisst schlicht wie ihr Modul.

### _codestelle

```python
def _codestelle() -> str
```

Die Codestelle dessen, der gerade ins Protokoll schreibt: der erste
Aufrufer ausserhalb dieses Moduls.

Gefragt wird den Aufrufstapel und nicht die Berechnung, die laeuft: viele
Formeln schreibt eine Hilfsfunktion in einem anderen Modul, und die
Spannung-Dehnung-Analyse laeuft ganz ohne Rechenwerk. Das stille Protokoll
fragt gar nicht -- es schreibt ja nichts.

### StillesProtokoll

```python
class StillesProtokoll(Protokoll)
```

Verwirft alles. Fuer Laeufe, deren Herleitung niemand liest.

Die Schnittstelle bleibt identisch, damit derselbe Rechencode einmal
protokollierend und einmal still laufen kann -- ohne Verzweigung im Code
und ohne dass die beiden Pfade auseinanderlaufen koennen.

Gebaut wird gar nichts, nicht erst gebaut und dann verworfen: eine Formel
setzt ihre Vorlage zweimal ein und misst ihre Breite, und die
Bewehrungssuche rechnet hundertfach, ohne je eine Zeile zu zeigen.

#### StillesProtokoll.titel

```python
def titel(self, *_, **__) -> None
```

#### StillesProtokoll.text

```python
def text(self, *_, **__) -> None
```

#### StillesProtokoll.erklaerung

```python
def erklaerung(self, *_, **__) -> None
```

#### StillesProtokoll.gleichung

```python
def gleichung(self, *_, **__) -> None
```

#### StillesProtokoll.ansatz

```python
def ansatz(self, *_, **__) -> None
```

#### StillesProtokoll.formel

```python
def formel(self, *_, **__) -> None
```

#### StillesProtokoll.wert

```python
def wert(self, *_, **__) -> None
```

#### StillesProtokoll.tabelle

```python
def tabelle(self, *_, **__) -> None
```

#### StillesProtokoll.ist_leer

```python
@property
def ist_leer(self) -> bool
```

### Zwischenwerte

```python
class Zwischenwerte
```

Benannte Zwischenwerte fuer [[opencivil.core.protokoll#Protokoll.formel|Protokoll.formel]].

Eine Vorlage wird zweimal eingesetzt, mit Symbolen und mit Zahlen samt
Einheit. Dafuer braucht jede Groesse ein Symbol, eine Einheit und eine
Stellenzahl -- auch ein Zwischenergebnis, das kein Wert des Rechenwerks
ist. Hier entstehen solche Werte, mit festen Gewohnheiten je Groessenart:
Laengen in mm auf eine Stelle, Flaechen in mm² und Spannungen in N/mm²
ganz, Kraefte in kN und Momente in kNm auf eine Stelle, Dehnungen in
Promille auf zwei, Kruemmungen in 1/m auf fuenf; wo eine Groesse mehr verlangt (die Zugfestigkeit des
Betons auf zwei Stellen), sagt es `stellen`. Jede Stelle, die das von
Hand tat, rechnete dafuer selbst um und schrieb die Einheit selbst dazu.

Die Kennung ist `{basis}.{name}`: eindeutig in der Mitschrift, aber nie
im Rechenwerk angemeldet -- diese Werte zeigen eine Rechnung, sie gehen in
keine ein.

#### Zwischenwerte.wert

```python
def wert(self, name: str, symbol: str, groesse: Groesse, stellen: int=1, beschreibung: str='') -> Wert
```

Ein Zwischenwert in der Einheit, in der `groesse` angezeigt wird.

#### Zwischenwerte.laenge

```python
def laenge(self, name: str, symbol: str, si: float, beschreibung: str='', *, stellen: int=1) -> Wert
```

#### Zwischenwerte.flaeche

```python
def flaeche(self, name: str, symbol: str, si: float, beschreibung: str='', *, stellen: int=0) -> Wert
```

#### Zwischenwerte.spannung

```python
def spannung(self, name: str, symbol: str, si: float, beschreibung: str='', *, stellen: int=0) -> Wert
```

#### Zwischenwerte.kraft

```python
def kraft(self, name: str, symbol: str, si: float, beschreibung: str='', *, stellen: int=1) -> Wert
```

#### Zwischenwerte.moment

```python
def moment(self, name: str, symbol: str, si: float, beschreibung: str='', *, stellen: int=1) -> Wert
```

#### Zwischenwerte.dehnung

```python
def dehnung(self, name: str, symbol: str, si: float, beschreibung: str='', *, stellen: int=2) -> Wert
```

#### Zwischenwerte.kruemmung

```python
def kruemmung(self, name: str, symbol: str, si: float, beschreibung: str='', *, stellen: int=5) -> Wert
```

#### Zwischenwerte.zahl

```python
def zahl(self, name: str, symbol: str, zahl: float, beschreibung: str='', *, stellen: int=3) -> Wert
```

### darstellen

```python
def darstellen(protokoll: Protokoll, tafel: Tafel[T]) -> List[T]
```

Setzt jeden Block eines Protokolls mit der Funktion seiner Art.

Ein Durchlauf fuer alle Darstellungen. Vorher unterschied jede die
Blockarten mit einer eigenen `if/elif`-Kette, und die der Oberflaeche
liess eine unbekannte Art stillschweigend weg. Jetzt wirft eine Blockart
ohne Eintrag: eine neue fehlt nicht still in der Darstellung, die sie
noch nicht kennt.

Gesucht wird die genaue Art, nicht eine Oberklasse -- auch eine
abgeleitete Blockart braucht ihren eigenen Eintrag.

Erklaerungen ([[opencivil.core.protokoll#TextBlock|TextBlock.erklaerung]]) laesst jede Darstellung weg:
sie stehen in der Formelsammlung. Hier, an der einen Stelle, durch die
Oberflaeche und alle Berichte gehen.


## Konstanten

- `T = TypeVar('T')`
- `Tafel = Mapping[Type[Block], Callable[[Any], T]]` – Wie eine Darstellung die Bloecke setzt: je Blockart eine Funktion, die den Block bekommt. Bis 2026-10-25 bekam sie auch seine Tiefe -- die Zahl der eingeschachtelten Mitschriften, in denen er stand; die schrieb da keine Rechnung mehr.

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.wert]]

## Gebraucht von

- [[opencivil.bericht.formelsammlung]]
- [[opencivil.bericht.gliederung]]
- [[opencivil.bericht.konsole]]
- [[opencivil.bericht.latex_dokument]]
- [[opencivil.bericht.markdown]]
- [[opencivil.bericht.zusammenfassung]]
- [[opencivil.core.berechnung]]
- [[opencivil.core.rechenwerk]]
- [[opencivil.geotechnik.grundbruch]]
- [[opencivil.geotechnik.setzung]]
- [[opencivil.material.basis]]
- [[opencivil.nachweis.biegung_normalkraft]]
- [[opencivil.nachweis.duktilitaet]]
- [[opencivil.nachweis.fehlende_bewehrung]]
- [[opencivil.nachweis.gebrauchsebene]]
- [[opencivil.nachweis.handrechnung]]
- [[opencivil.nachweis.kennzahlen]]
- [[opencivil.nachweis.knicken]]
- [[opencivil.nachweis.mindestbewehrung]]
- [[opencivil.nachweis.qa_gebrauch]]
- [[opencivil.nachweis.qa_kennzahlen]]
- [[opencivil.nachweis.qa_knicken]]
- [[opencivil.nachweis.querkraft]]
- [[opencivil.nachweis.querkraft_buegel]]
- [[opencivil.nachweis.querkraft_ohne_buegel]]
- [[opencivil.nachweis.querschnittsloeser]]
- [[opencivil.nachweis.rechenwahl]]
- [[opencivil.nachweis.resistenzlinie]]
- [[opencivil.nachweis.richtungsnachweise]]
- [[opencivil.nachweis.rissgroessen]]
- [[opencivil.nachweis.schiefe_biegung]]
- [[opencivil.nachweis.schubwandnachweis]]
- [[opencivil.nachweis.spannungsbegrenzung]]
- [[opencivil.nachweis.spannungsgrenzen]]
- [[opencivil.nachweis.sproedes_versagen]]
- [[opencivil.nachweis.stabgrenzen]]
- [[opencivil.nachweis.verformung]]
- [[opencivil.notizbuch.formelseiten]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.lagenaufbau]]
- [[opencivil.querschnitt.platte]]
- [[opencivil.querschnitt.werkstoffgesetz]]
- [[opencivil.spannungsanalyse.analysen]]
- [[opencivil.spannungsanalyse.herleitung]]
- [[opencivil.spannungsanalyse.linie]]
- [[opencivil.spannungsanalyse.modul]]
- [[opencivil.spannungsanalyse.platte]]
- [[opencivil.spannungsanalyse.schnitt]]
- [[opencivil.stabwerk.herleitung]]
- [[opencivil.stabwerk.rechnung]]
- [[opencivil.stabwerk.stabquerschnitt]]
- [[opencivil.web.api]]
