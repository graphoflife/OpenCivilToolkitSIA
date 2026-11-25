---
erzeugt: ae902a960953
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/eintraege.py
> die Teile einer Projektbeschreibung.
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/eintraege.py)

## VERANTWORTUNG

Material, Lastfaelle, Rechenwahlen und was Platte und gezeichneter
Querschnitt gleich angeben -- jedes als Datenklasse, die sich als JSON
speichern und wieder einlesen laesst. Gelesen und geprueft wird jeder Eintrag
ueber seine Felder: was eines annehmen darf, steht an ihm
([[opencivil.projekt.lesen]]).

Was nur die Platte hat -- Posten, Lagen, Buegel --, steht bei ihr in
[[opencivil.projekt.platte]]; bis 2026-11-20 stand es hier. Das ganze
Projekt steht in [[opencivil.projekt.projekt]].

## Inhalt

### _feldnamen

```python
@functools.lru_cache(maxsize=None)
def _feldnamen(klasse: type) -> frozenset
```

Die Namen der Felder einer Beschreibungsklasse -- je Klasse einmal gesucht.

### Beschreibung

```python
@dataclass
class Beschreibung
```

Gemeinsamer Boden aller Beschreibungsteile.

Der Weg nach draussen sind die Felder der Datenklasse, nicht mehr. Von
Hand geschrieben war `als_dict` ein Spiegel, der nur stimmt, solange
jemand ihn nachfuehrt -- neun Stueck, zusammen gut hundert Zeilen, deren
ganze Aufgabe war, identisch zu etwas zu sein, das die Standardbibliothek
schon kann.

Seit der Zwischenspeicher ([[opencivil.web.speicher]]) seinen Abdruck
daraus bildet, waere ein vergessenes Feld auch nicht mehr bloss eine
unvollstaendige Datei: die Aenderung faende sich im Abdruck nicht wieder,
das Bauteil gaelte als unveraendert, und die Oberflaeche zeigte eine alte
Zahl. Von allen Fehlern der schlimmste -- und mit dieser Zeile gibt es ihn
nicht.

Der Weg hinein ebenso: [[opencivil.projekt.lesen#lesen|lesen]] liest
jeden Eintrag aus seinen Feldern, streng, und prueft ihn mit
[[opencivil.projekt.lesen#felder_pruefen|felder_pruefen]] -- was ein Feld annehmen
darf, steht an ihm. Von Hand waren es 39 Leser, jeder mit eigenen
Vorgaben, Pruefungen und alten Formaten, und die Fassade ging an ihnen
vorbei: ein «festt» aus Python wurde still zur Feder (2026-10-16).

`BEZEICHNUNG`, wo es sie gibt, nennt den Eintrag in Meldungen so wie
die Oberflaeche: «Platte 'Decke'». `IM_ORT` nennt ein Element einer
Liste mit dem Wort der Maske: mit Namen «Wand 'W1'», ohne mit seiner
Nummer, «Lage 2».

Ein Wahlfeld haelt das Mitglied seiner Wahl; wer Text zuweist -- die
Datei, der Konstruktor, die Fassade --, bekommt hier das Mitglied
([[opencivil.projekt.lesen#wahl_aus_text|wahl_aus_text]]).

Was ueber mehrere Felder gilt, steht in [[opencivil.projekt.eintraege#Beschreibung.regeln|regeln]] -- geprueft vor
dem Rechnen, nach den Bereichen der Felder
([[opencivil.projekt.lesen#inhalt_pruefen|inhalt_pruefen]]).

- `ERSTE_MATERIALIEN: ClassVar[Mapping[str, str]] = {}` – Was ein neuer Eintrag vom Projekt nimmt ([[opencivil.projekt.eintraege#Beschreibung.frisch|frisch]]): je Feld, als Pfad wie `stabmaterialien/0/stoff`, die Art des Materials, von der er das erste bekommt. «+» in der Oberflaeche liest es aus dem Katalog, damit die Regel an einer Stelle steht. Ohne eigene keines.
- `STAMM: ClassVar[str] = ''` – Wie ein neuer Eintrag einer App heisst, vor seiner Nummer: «Platte» in «Platte 1» ([[opencivil.projekt.projekt#naechster_name|naechster_name]]). Nur die Klassen der Apps haben einen ([[opencivil.projekt.projekt#Konstanten|APPLISTEN]]), und das Projekt: «Projekt 2». Die Oberflaeche liest ihn aus dem Katalog.

#### Beschreibung.regeln

```python
def regeln(self, wo: str) -> None
```

Die Regeln ueber mehrere Felder -- ohne eigene keine. `wo` nennt den Eintrag.

#### Beschreibung.fallnamen

```python
def fallnamen(self) -> List[Fallnamen]
```

Die Listen von Faellen, deren Namen sich unterscheiden muessen
([[opencivil.projekt.fallnamen|fallnamen]]) -- ohne eigene keine. Geprueft
vor den Regeln ([[opencivil.projekt.lesen#inhalt_pruefen|inhalt_pruefen]]) und
vom Namensfeld, bevor es einen Namen uebernimmt.

#### Beschreibung.si

```python
def si(self, feld: str) -> float
```

Die Zahl eines Feldes in SI, mit der Einheit seines Bereichs
([[opencivil.projekt.lesen#als_groesse|als_groesse]]) -- der, in der die
Maske sie zeigt. Wer rechnet, nimmt sie so, statt die Einheit noch
einmal anzuschreiben.

#### Beschreibung.als_dict

```python
def als_dict(self) -> dict
```

#### Beschreibung.frisch

```python
@classmethod
def frisch(cls, materialien: Iterable[Any]=()) -> Any
```

Ein frischer Eintrag dieser Klasse, wie die Oberflaeche ihn anlegt:
ueber `neu`, wo die Klasse eines hat -- eine Platte mit ihren
Lagen, ein Grundbruch mit einer Kombination --, sonst mit ihren
Vorgaben. Aus `materialien` bekommt jedes Feld in
[[opencivil.projekt.eintraege#Beschreibung|ERSTE_MATERIALIEN]] das erste seiner Art. Kennung und Name
bleiben leer: sie setzt, wer anlegt.

#### Beschreibung.aus_dict

```python
@classmethod
def aus_dict(cls, roh: Mapping[str, Any], wo: Optional[str]=None) -> Any
```

Ein Eintrag aus der Datei -- gelesen und geprueft, siehe [[opencivil.projekt.lesen]].

### BauteilEintrag

```python
@dataclass
class BauteilEintrag(Beschreibung)
```

Was jedes Bauteil eines Projekts sagt -- eine Platte, eine Analyse, ein
Fundament --: worauf es zeigt. Danach fragt das Projekt, bevor etwas
geloescht wird ([[opencivil.projekt.projekt#Projekt.verweise|verweise]]).
Ohne eigene Angabe zeigt es auf nichts.

Bis 2026-11-10 stand dieser Vertrag in keiner Klasse: jede Art schrieb
beide Methoden selbst, viermal `return []`, und eine neue Art, die sie
vergass, fiel erst beim Loeschen eines Materials auf.

- `_: KW_ONLY`
- `vergeben: Dict[str, int] = field(default_factory=dict)` – Je Vorsilbe die hoechste Nummer, die das Bauteil je vergeben hat -- an seine Knoten, Linien, Lastfaelle: eine Kennung kommt nie wieder ([[opencivil.projekt.netz#neue_kennung|neue_kennung]]).

#### BauteilEintrag.materialien

```python
def materialien(self) -> List[str]
```

Die Kennungen der Materialien, auf die das Bauteil zeigt.

#### BauteilEintrag.bezuege

```python
def bezuege(self) -> List[str]
```

Die Kennungen der Bauteile, deren Querschnitt es nimmt.

### MaterialEintrag

```python
@dataclass
class MaterialEintrag(Beschreibung)
```

Ein Baustoff, wie ihn die Oberflaeche beschreibt: eine Normsorte nach SIA,
die bleibt, wie sie ist, oder ein eigenes Material mit einer Sorte als
Vorlage.

- `BEZEICHNUNG = 'Material'`
- `kennung: str`
- `art: Baustoffart`
- `sorte: str` – Die Normsorte -- bei einem eigenen Material die Vorlage seiner Kennwerte.
- `name: str = ''`
- `eigenstaendig: bool = False` – False = Normsorte, Kennwerte gesperrt, Name = Sorte -- nie aenderbar. True = eigenes Material, aenderbar, mit eigenem Namen (BE1, S1 ...).
- `abweichungen: Dict[str, float] = field(default_factory=dict)`
- `ueberschreibungen: Dict[str, float] = field(default_factory=dict)`

#### MaterialEintrag.anzeigename

```python
@property
def anzeigename(self) -> str
```

#### MaterialEintrag.ist_normsorte

```python
@property
def ist_normsorte(self) -> bool
```

#### MaterialEintrag.sorte_pruefen

```python
def sorte_pruefen(self) -> None
```

Die Sorte -- schon beim Oeffnen: aus ihr kommen die Kennwerte, ohne
sie laesst sich das Material nicht einmal zeigen. Die Materialart
prueft ihr Feld.

#### MaterialEintrag.regeln

```python
def regeln(self, wo: str) -> None
```

Was eine Normsorte bleibt und wie ein eigenes Material heissen darf --
vor dem Rechnen, nicht beim Oeffnen: ein abgelegtes Material mit
falschem Namen soll sich oeffnen und umbenennen lassen.

### kleinste_neigung

```python
def kleinste_neigung() -> Any
```

α_min, die kleinste Neigung der Druckdiagonalen -- und nicht ueber α_max:
bei den Buegeln der Platte wie am gezeichneten Querschnitt. Eine
groessere weist schon das Feld ab ([[opencivil.core.bereich#Bereich|bis_feld]]).

### groesste_neigung

```python
def groesste_neigung() -> Any
```

α_max, die groesste -- eine unter α_min weist ihr Feld ebenso ab.

### _neigung

```python
def _neigung(vorgabe: int, heisst: str, bis_feld: Optional[str]=None) -> Any
```

Eine Grenze der Druckfeldneigung -- in ganzen Grad, 1° bis 89°.

### druckfeld

```python
def druckfeld() -> Any
```

Die Abminderung k_c der Druckdiagonalen -- eine Festigkeit mal k_c, also groesser als null.

### x_d_grenze

```python
def x_d_grenze() -> Any
```

Der Beiwert k der Grenze `x/d <= k * 435 N/mm^2 / f_yd` im
Duktilitaetsnachweis -- Vorgabe und Hoechstwert stehen beim Nachweis
(`duktilitaet.BEIWERT`, `duktilitaet.HOECHSTENS`).

### KnickEintrag

```python
@dataclass
class KnickEintrag(Beschreibung)
```

Ein Knicknachweis: Druckkraft, Moment 1. Ordnung, Laenge, Knicklaenge.

Nur in x-Richtung -- eine Knicklaenge gehoert zu einer Tragrichtung, und
in y waere die Breite der Platte die Laenge.

- `IM_ORT = 'Knicknachweis'`
- `name: str`
- `N_Ed: float = bereich(0.0, heisst='Normalkraft N_Ed', einheit=KN)` – Druck negativ.
- `M_Ed_1: float = bereich(0.0, heisst='Moment 1. Ordnung M_Ed,1', einheit=KNM)`
- `laenge: float = bereich(3.0, heisst='Höhe des Druckglieds', einheit=M, ueber=0.0)` – Hoehe des Druckglieds in m, bei mehreren uebereinander ihre ganze Hoehe (SIA 262:2025, 4.1.3.2.3) -- sie bestimmt die Schiefstellung. Bis 2026-11-14 hiess sie Systemlaenge; bis 2026-10-16 rechnete eine Laenge von null und hiess «erfuellt».
- `knicklaenge: float = bereich(3.0, heisst='Knicklänge', einheit=M, ueber=0.0)` – Knicklaenge in m.
- `aktiv: bool = True` – Ob der Fall gerechnet wird. Ausgeschaltet bleibt er stehen -- eine geloeschte Zeile muesste man neu eintippen, um sie wieder anzusehen.

### VerformungsfallEintrag

```python
@dataclass
class VerformungsfallEintrag(Beschreibung)
```

Ein Verformungsfall: die Durchbiegung, mit der Steifigkeit E_cm
ermittelt, ihre Spannweite und die Seite, die er zieht.

Wie ein Knickfall nur in x-Richtung.

- `IM_ORT = 'Verformungsfall'`
- `name: str`
- `w: float = bereich(0.0, heisst='Durchbiegung w', einheit=MM, ab=0.0)` – Durchbiegung in mm, mit E_cm ermittelt -- ein Betrag.
- `laenge: float = bereich(5.0, heisst='Spannweite L', einheit=M, ueber=0.0)` – Spannweite L in m -- der Grenzwert ist L/350.
- `zugseite: Zugseite = einer_von(UM_Y, Zugseite.UNTEN)` – `unten` im Feld, `oben` am Kragarm -- welches rho gilt.
- `aktiv: bool = True` – Ob der Fall gerechnet wird. Ausgeschaltet bleibt er stehen.

### VerformungEintrag

```python
@dataclass
class VerformungEintrag(Beschreibung)
```

Der Verformungsnachweis einer Platte: die Kriechzahl seines
Vergroesserungsfaktors und die Faelle.

phi gilt fuer die Platte und nicht je Fall -- der Faktor wird je Seite
einmal gerechnet ([[opencivil.nachweis.verformung]]).

- `kriechzahl: float = bereich(VERFORMUNG_KRIECHZAHL, heisst='Kriechzahl φ', ab=0.0)` – phi im Vergroesserungsfaktor omega_w, Vorgabe 2.
- `faelle: List[VerformungsfallEintrag] = field(default_factory=list)`

#### VerformungEintrag.fall

```python
def fall(self, name: str, *, w: float, laenge: float, zugseite: Zugseite=VerformungsfallEintrag.zugseite) -> VerformungsfallEintrag
```

Einen Fall anfuegen -- w in mm, die Spannweite in m.

### abgeleiteter_fallname

```python
def abgeleiteter_fallname(name: str, anteil: float) -> str
```

Wie ein aus der Tragsicherheit abgeleiteter Lastfall heisst.

Die eine Stelle dafuer: der Aufbau benennt die Faelle so, und die
Namenspruefung muss genau denselben Namen bilden, um einen gleichlautenden
eigenen Fall zu erkennen. `70.0` wird zu «70 %», `62.5` zu «62.5 %».

### JeMaterial

```python
class JeMaterial
```

Was je Material waehlt ([[opencivil.projekt.lesen#je_material|je_material]]):
im Feld `werkstoffsaetze` je Kennung eines Materials sein Wertesatz
(Benutzer, 2026-11-20), im Feld `rechenarten` je Beton seine
Rechenart (Benutzer, 2026-11-25). Ein Material ohne eigene Wahl rechnet
mit der Vorgabe des Feldes -- die Stahlspannungen etwa charakteristisch
und praezise. Fuer die Rechnung wird daraus die Wahl an einem Bauteil
([[opencivil.projekt.eintraege#JeMaterial.wahl|wahl]]), mit der `kriechzahl` des Eintrags. Bis 2026-11-20
waehlte nur die Querschnittsanalyse je Material, jedes andere Kapitel
einen Wertesatz fuer alle; bis 2026-11-25 galt ausser in ihrer
Tragsicherheit eine Rechenart fuer alle Betone.

#### JeMaterial.von

```python
def von(self, feld: str, material: str) -> Any
```

Die Wahl eines Materials in diesem Feld -- die Vorgabe des Feldes, wenn es keine eigene hat.

#### JeMaterial.wahl

```python
def wahl(self, stoffe: Mapping[str, Baustoff]) -> Rechenwahl
```

Womit an einem Bauteil aus diesen Baustoffen gerechnet wird --
`stoffe` nach ihrer Kennung im Projekt: je Baustoff sein Wertesatz,
je Beton seine Rechenart; ein Stahl hat keine.

### SpannungsfallEintrag

```python
@dataclass
class SpannungsfallEintrag(Beschreibung, JeMaterial)
```

Eine Auswertung am Querschnitt -- kein Nachweis.

Es wird nichts gegen etwas gehalten: kein Erfuellungsgrad, kein Urteil.
Gefragt wird, was im Querschnitt geschieht, und je nach [[opencivil.projekt.eintraege#SpannungsfallEintrag|art]] von
der einen oder der anderen Seite -- aus Schnittgroessen, aus Dehnungen,
als Momenten-Kruemmungs- oder als Normalkraft-Dehnungs-Linie.

Womit gerechnet wird, waehlt jede Analyse fuer sich: die Kriechzahl, je
Material den Wertesatz und je Beton die Rechenart ([[opencivil.projekt.eintraege#JeMaterial|JeMaterial]],
[[opencivil.querschnitt.gesetzwahl#Rechenwahl|Rechenwahl]]).

- `IM_ORT = 'Diagramm'`
- `name: str`
- `art: Analyseart = Analyseart.SCHNITTGROESSEN` – Was gefragt wird -- siehe [[opencivil.spannungsanalyse.art#Analyseart|Analyseart]].
- `richtung: Richtung = Richtung.X` – Welche Bewehrung zaehlt. Hier keine Wahl `beide`: ein Bild zeigt einen Querschnitt, und der liegt in einer Richtung.
- `N_Ed: float = bereich(0.0, heisst='N_Ed', einheit=KN)` – Zug positiv. Welche Frage welches Feld braucht, sagt [[opencivil.spannungsanalyse.art#Analyseart.eingaben|Analyseart.eingaben]].
- `M_Ed: float = bereich(0.0, heisst='M_Ed', einheit=KNM)`
- `eps_oben: float = bereich(-1.0, heisst='ε oben', einheit=PROMILLE)`
- `eps_unten: float = bereich(2.0, heisst='ε unten', einheit=PROMILLE)` – Die Randdehnungen.
- `kriechzahl: float = bereich(0.0, heisst='Kriechzahl φ', ab=0.0)` – Die Kriechzahl φ dieser Analyse.
- `werkstoffsaetze: Dict[str, Werkstoffsatz] = je_material(Werkstoffsatz.BEMESSUNG)` – Je Material `bemessung` (f_cd, f_yd) oder `charakteristisch` (f_ck, f_yk).
- `rechenarten: Dict[str, Rechenart] = je_material(Rechenart.PARABEL, FASERARTEN)` – Je Beton `block` oder `parabel` -- siehe [[opencivil.querschnitt.gesetzwahl#Rechenart|Rechenart]]. Die Handrechnung gibt es hier nicht ([[opencivil.nachweis.rechenwahl#Konstanten|FASERARTEN]]).
- `aktiv: bool = True`

### spannungsfallnamen

```python
def spannungsfallnamen(faelle: Iterable[SpannungsfallEintrag]) -> Fallnamen
```

Die Namen der Spannung-Dehnung-Analysen, bei der Platte wie am
gezeichneten Querschnitt -- eine Liste fuer sechs Fenster, darum sagt die
Meldung, in welchem der andere steht.

### GebrauchsfallEintrag

```python
@dataclass
class GebrauchsfallEintrag(Beschreibung)
```

Eine Schnittgroessenkombination unter Gebrauchslast.

Wie [[opencivil.projekt.eintraege#KombinationEintrag|KombinationEintrag]], aber ohne Querkraft: begrenzt wird die
Stahlspannung, und dafuer zaehlen Moment und Normalkraft. Ob der Fall
haeufig oder quasi-staendig ist, sagt die Liste, in der er steht.

- `IM_ORT = 'Lastfall'`
- `name: str`
- `M_Ed: float = bereich(0.0, heisst='Moment M_Ed', einheit=KNM)`
- `N_Ed: float = bereich(0.0, heisst='Normalkraft N_Ed', einheit=KN)`
- `aktiv: bool = True` – Ob dieser Lastfall gerechnet wird. Ausgeschaltet bleibt er stehen.

### RechenwahlEintrag

```python
@dataclass
class RechenwahlEintrag(Beschreibung, JeMaterial)
```

Womit ein Nachweis-Kapitel rechnet: Kriechzahl, je Material der
Wertesatz und je Beton die Rechenart ([[opencivil.projekt.eintraege#JeMaterial|JeMaterial]]) -- siehe
[[opencivil.querschnitt.gesetzwahl#Rechenwahl|Rechenwahl]]. So steht sie in
der Tragsicherheit.

Jedes andere Kapitel hat seine Unterklasse, und welche Rechenarten es
anbietet, steht an deren Feld: der Leser prueft es wie jede Wahl. Bis
2026-10-17 prueften fuenf Aufrufer je mit ihrer Liste nach dem Lesen.
Die Kriechzahl des Vergroesserungsfaktors gehoert dem Verformungsnachweis
([[opencivil.projekt.eintraege#VerformungEintrag|VerformungEintrag]]).

- `kriechzahl: float = bereich(0.0, heisst='Kriechzahl φ', ab=0.0)`
- `werkstoffsaetze: Dict[str, Werkstoffsatz] = je_material(Werkstoffsatz.BEMESSUNG)`
- `rechenarten: Dict[str, Rechenart] = je_material(Rechenart.HANDRECHNUNG, RECHENARTEN)`

### Gebrauchswahl

```python
@dataclass
class Gebrauchswahl(RechenwahlEintrag)
```

Die Stahlspannungen: praezise, mit charakteristischen Werten -- die Rechenarten der Tragsicherheit.

- `werkstoffsaetze: Dict[str, Werkstoffsatz] = je_material(Werkstoffsatz.CHARAKTERISTISCH)`
- `rechenarten: Dict[str, Rechenart] = je_material(Rechenart.PARABEL, RECHENARTEN)`

### KnickVerformungswahl

```python
@dataclass
class KnickVerformungswahl(RechenwahlEintrag)
```

Die Ausmitte e_2d beim Knicken: nur praezise ohne Vereinfachung.

- `rechenarten: Dict[str, Rechenart] = je_material(Rechenart.PARABEL, VERFORMUNGSARTEN)`

### KnickWiderstandswahl

```python
@dataclass
class KnickWiderstandswahl(RechenwahlEintrag)
```

Der Widerstand beim Knicken: ueber die Fasern, vorgegeben die
0.85·x-Vereinfachung. Bis 2026-10-12 war es die Handrechnung, die es
dort nicht mehr gibt; die Vereinfachung kommt ihr am naechsten.

- `rechenarten: Dict[str, Rechenart] = je_material(Rechenart.BLOCK, FASERARTEN)`

### Gebrauchsliste

```python
@dataclass
class Gebrauchsliste(Beschreibung)
```

Die Lastfaelle eines Stahlspannungsnachweises: eigene und abgeleitete.

Eine Platte hat zwei davon, eine haeufige und eine quasi-staendige. Beide
werden gleich gebildet -- die eigenen Faelle, dazu die
Tragsicherheitseinwirkungen mal `anteil` Prozent -- und unterscheiden
sich nur darin, wogegen der Nachweis sie haelt.

Frueher waren das sechs flache Felder an der Platte, und jede Stelle, die
damit arbeitete, setzte die drei zusammengehoerigen wieder ueber ihre
Namen zusammen. Welche Liste haeufig und welche quasi-staendig ist, sagt
das Feld der Platte, in dem sie steht; die Liste selbst weiss es nicht.

Der gezeichnete Querschnitt hat dieselbe Liste mit anderen Faellen
([[opencivil.projekt.querschnittsanalyse#QAGebrauchsliste|QAGebrauchsliste]]): was
darin steht ([[opencivil.projekt.eintraege#Gebrauchsliste|FALL]]), welche Rechenarten sie anbietet (der Typ
ihres Feldes [[opencivil.projekt.eintraege#JeMaterial.wahl|wahl]]) und wie ihr Bauteil heisst, wo ein Fall ohne
Bauteil gelesen wird ([[opencivil.projekt.eintraege#Gebrauchsliste|BAUTEIL]]).

- `FALL = GebrauchsfallEintrag`
- `BAUTEIL = 'Platte'`
- `anteil: float = bereich(heisst='Anteil aus der Tragsicherheit', einheit=PROZENT, uebe…` – Welcher Anteil der Tragsicherheitseinwirkungen abgeleitet wird, in %. Null ergaebe Lastfaelle ohne Last -- ein Nachweis, der immer aufgeht und nichts sagt. Ueber hundert waere keine Gebrauchslast mehr. Gemeldet statt begrenzt: wer 700 statt 70 tippt, soll es erfahren und nicht mit 100 weiterrechnen.
- `aus_tragsicherheit: bool = False` – Ob die abgeleiteten Faelle *gefuehrt* werden. Gebildet werden sie immer; ausgeschaltet rechnen sie still mit. Der Anteil ist eine bequeme Abschaetzung und keine Norm, darum stehen die Faelle nur auf Verlangen in der Tabelle.
- `faelle: List[GebrauchsfallEintrag] = field(default_factory=list)` – Eigene Lastfaelle -- neben den abgeleiteten, nicht statt ihrer.
- `wahl: Gebrauchswahl = teil(Gebrauchswahl, heisst='Rechenwahl')` – Womit die Stahlspannung gerechnet wird -- Vorgabe praezise, charakteristisch.

#### Gebrauchsliste.lastfall

```python
def lastfall(self, name: str, **werte: float)
```

Einen eigenen Lastfall anfuegen -- kNm und kN, Zug positiv.

#### Gebrauchsliste.namensliste

```python
def namensliste(self, feld: str, kombinationen: List[Any], wort: str) -> Fallnamen
```

Die Namen dieser Liste ([[opencivil.projekt.fallnamen#Fallnamen|Fallnamen]]),
unter `feld` im Bauteil. Je Liste fuer sich: die beiden Listen
landen in getrennten Nachweisen und damit in getrennten ID-Raeumen,
ein Fall «Dauer» darf in beiden stehen. Schon vergeben sind die aus
den `kombinationen` der Tragsicherheit abgeleiteten: sie tragen den
Namen ihrer Kombination mit angehaengtem Anteil, und wer einen eigenen
Fall genau so nennt, traefe denselben Schluessel.

### Querschnittsangaben

```python
@dataclass
class Querschnittsangaben(BauteilEintrag)
```

Was die Platte ([[opencivil.projekt.platte#QuerschnittEintrag|QuerschnittEintrag]]) und
der gezeichnete Querschnitt
([[opencivil.projekt.querschnittsanalyse#QuerschnittsanalyseEintrag|QuerschnittsanalyseEintrag]])
gleich angeben: die Rissanforderung, die Schalter der Zwaengungen, des
sproeden Versagens und der Duktilitaet mit ihren Werten, womit das Knicken
rechnet, die Abminderung im Druckfeld und den freien Text. Bis 2026-10-17
stand jedes dieser Felder zweimal da, je mit eigener Beschreibung.

Wo nachgewiesen wird, sagt die Geometrie: die Platte je x-Lage, der
gezeichnete Querschnitt je Richtung oder am ganzen Querschnitt. Die Felder
hier sind nur mit Namen anzugeben (`KW_ONLY`): so duerfen die Felder der
Geometrie ohne Vorgabe dahinter folgen -- der Beton der Platte.

- `kennung: str`
- `name: str`
- `_: KW_ONLY`
- `rissanforderung: Rissanforderung = Rissanforderung.NORMAL` – Anforderung an die Rissbildung -- `normal`, `erhoeht` oder `hoch`.
- `zwaengung: bool = False` – Ob die Zwaengung auf Normalkraft nachgewiesen wird -- an der Platte je x-Lage, am gezeichneten Querschnitt am ganzen Querschnitt. Vorgabe aus: eine Zwaengung ist eine Annahme ueber das Tragwerk, keine Eigenschaft des Querschnitts. Wer sie braucht, schaltet sie ein. An der Platte ein Schalter, nicht zwei: nachgewiesen wird nur die Tragrichtung x. Die y-Lagen stehen im Querschnitt, weil sie die statische Hoehe von x bestimmen und zum Bewehrungsgehalt zaehlen -- nachgewiesen werden sie nicht.
- `zwaengung_begrenzt: bool = False` – Ob die rissaktive Dicke der Zwaengung auf Normalkraft hoechstens 500 mm betraegt.
- `zwaengung_biegung: bool = False` – Ob die Zwaengung auf Biegung nachgewiesen wird -- an der Platte je x-Lage, am gezeichneten Querschnitt je Richtung.
- `zwaengung_biegung_kriechzahl: float = bereich(0.0, heisst='Kriechzahl φ', ab=0.0)` – Die Kriechzahl φ der Zwaengung auf Biegung: der Beton mit `E_cm/(1+φ)`, an der Platte als Wertigkeit `n = (E_s/E_cm)·(1+φ)`.
- `sproede: bool = False` – Ob der Nachweis gegen sproedes Versagen gefuehrt wird.
- `duktilitaet: bool = False` – Ob der Duktilitaetsnachweis gefuehrt wird. Ein Schalter fuer das Bauteil und nicht einer je Lage. An der Platte werden beide x-Lagen gerechnet -- die obere traegt das Stuetz-, die untere das Feldmoment --, und in der Zusammenfassung steht die unguenstigere. Vier Schalter fuer einen Nachweis waren vier Gelegenheiten, den falschen zu vergessen; die Frage ist ohnehin, ob der Querschnitt sein Versagen ankuendigt, und die beantwortet die schlechtere Lage.
- `x_d_max: float = x_d_grenze()` – Der Beiwert k der Grenze `x/d <= k * 435 N/mm^2 / f_yd` im Duktilitaetsnachweis. Bis 2026-11-14 war er selbst die Grenze; bei B500 sind beide gleich, darum heisst das Feld weiter so, und alte Dateien lesen sich ohne Umweg.
- `knicken_wahl_verformung: KnickVerformungswahl = teil(KnickVerformungswahl, heisst='Knicken, Verformung (e_2d)')` – Womit die Ausmitte e_2d gerechnet wird -- immer praezise ohne Vereinfachung ([[opencivil.nachweis.rechenwahl#Konstanten|VERFORMUNGSARTEN]]), Vorgabe Bemessungswerte.
- `knicken_wahl_widerstand: KnickWiderstandswahl = teil(KnickWiderstandswahl, heisst='Knicken, Widerstand (N_Rd)')` – Womit N_Rd(M_Ed = N_Ed·e_tot) gerechnet wird -- Vorgabe die 0.85·x-Vereinfachung, ohne Handrechnung. Mit derselben Wahl wie die Tragsicherheit ist es deren Linie.
- `k_c: float = druckfeld()` – Abminderung der Betondruckfestigkeit in der Druckdiagonalen.
- `beschreibung: str = ''` – Freier Text zum Bauteil -- was sonst nirgends hinpasst. Wo es liegt, woher die Schnittgroessen stammen, was noch zu klaeren ist. Geht in keine Rechnung ein und steht in keinem Nachweis; er wird gespeichert und wieder angezeigt, mehr nicht. Genau dafuer gibt es ihn: ohne ein solches Feld landen solche Saetze im Namen.

### KombinationEintrag

```python
@dataclass
class KombinationEintrag(Beschreibung)
```

Eine zu pruefende Schnittgroessenkombination.

- `IM_ORT = 'Einwirkung'`
- `name: str`
- `M_Ed: float = bereich(0.0, heisst='Moment M_Ed', einheit=KNM)`
- `N_Ed: float = bereich(0.0, heisst='Normalkraft N_Ed', einheit=KN)`
- `V_Ed: float = bereich(0.0, heisst='Querkraft V_Ed', einheit=KN_PRO_M)` – Je Meter, nicht je Streifen b -- für den Querkraftnachweis.
- `art: Erfuellungsart = Erfuellungsart.AUTOMATISCH`
- `aktiv: bool = True` – Ob dieser Lastfall gerechnet wird. Ausgeschaltet bleibt er stehen.


## Konstanten

- `HAEUFIG_ANTEIL = 70.0` – Anteil der Tragsicherheitseinwirkungen, der als haeufiger Lastfall gilt -- in Prozent, wie die Maske ihn zeigt. Eine Vorgabe, einstellbar je Platte.
- `QUASISTAENDIG_ANTEIL = 60.0` – Dasselbe fuer die quasi-staendigen Lastfaelle.

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.material.arten]]
- [[opencivil.material.basis]]
- [[opencivil.nachweis.biegung_normalkraft]]
- [[opencivil.nachweis.duktilitaet]]
- [[opencivil.nachweis.rechenwahl]]
- [[opencivil.nachweis.rissanforderung]]
- [[opencivil.nachweis.verformung]]
- [[opencivil.projekt.fallnamen]]
- [[opencivil.projekt.lesen]]
- [[opencivil.querschnitt.fachwerk]]
- [[opencivil.querschnitt.gesetzwahl]]
- [[opencivil.querschnitt.platte]]
- [[opencivil.querschnitt.zugseite]]
- [[opencivil.spannungsanalyse]]

## Gebraucht von

- [[opencivil.mcp.ausgabe]]
- [[opencivil.mcp.sitzung]]
- [[opencivil.projekt]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.aufbau.platte]]
- [[opencivil.projekt.balkensystem]]
- [[opencivil.projekt.balkensystem3d]]
- [[opencivil.projekt.beispiele]]
- [[opencivil.projekt.decke]]
- [[opencivil.projekt.durchstanzen]]
- [[opencivil.projekt.erdbeben]]
- [[opencivil.projekt.faelle]]
- [[opencivil.projekt.grundbruch]]
- [[opencivil.projekt.pfahl]]
- [[opencivil.projekt.platte]]
- [[opencivil.projekt.projekt]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.projekt.setzung]]
- [[opencivil.projekt.skript]]
- [[opencivil.projekt.staebe]]
