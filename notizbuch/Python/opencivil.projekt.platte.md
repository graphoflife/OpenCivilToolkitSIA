---
erzeugt: 732eaf2d7744
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/platte.py
> eine Platte, wie die Oberflaeche sie beschreibt.
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/platte.py)

## VERANTWORTUNG

Der [[opencivil.projekt.platte#QuerschnittEintrag|QuerschnittEintrag]]: Abmessungen, vier Bewehrungslagen, die
Schalter der Nachweise und die Lastfaelle -- alles, was zu einer Platte
gehoert, als eine speicherbare Datenklasse. Dazu die Vorlage einer frischen
Platte ([[opencivil.projekt.platte#QuerschnittEintrag.neu|QuerschnittEintrag.neu]]) und die Methoden, mit denen man ohne
Oberflaeche Lastfaelle anfuegt.

Was daraus gerechnet wird, steht in [[opencivil.projekt.aufbau]].

## Inhalt

### QuerschnittEintrag

```python
@dataclass
class QuerschnittEintrag(Querschnittsangaben)
```

Eine Stahlbeton-Platte mit genau vier Bewehrungslagen. Was sie mit dem
gezeichneten Querschnitt gleich angibt, steht in der Grundlage
([[opencivil.projekt.eintraege#Querschnittsangaben|Querschnittsangaben]]).

- `BEZEICHNUNG = 'Platte'`
- `beton: str`
- `h: float = bereich(300.0, heisst='Dicke h', einheit=MM, ueber=0.0)`
- `b: float = bereich(1000.0, heisst='Breite b', einheit=MM, ueber=0.0)`
- `ueberdeckung_unten: float = bereich(30.0, heisst='Überdeckung unten', einheit=MM, ab=0.0)`
- `ueberdeckung_oben: float = bereich(30.0, heisst='Überdeckung oben', einheit=MM, ab=0.0)`
- `d_max: float = bereich(32.0, heisst='Grösstkorn D_max', einheit=MM, ueber=0.0)` – Grösstkorndurchmesser in mm.
- `einlagenhoehe: float = bereich(0.0, heisst='Einlagenhöhe', einheit=MM, ab=0.0)` – Höhe einer Einlage in mm.
- `querkraftbewehrung: QuerkraftbewehrungEintrag = field(default_factory=QuerkraftbewehrungEintrag)` – Bügel; ohne Durchmesser heisst: keine.
- `haeufig: Gebrauchsliste = field(default_factory=lambda: Gebrauchsliste(anteil=HAEUFIG_ANTEIL))` – Die haeufigen Lastfaelle -- fuer den Nachweis gegen Fliessen.
- `quasistaendig: Gebrauchsliste = field(default_factory=lambda: Gebrauchsliste(anteil=QUASISTAENDIG_ANT…` – Die quasi-staendigen Lastfaelle -- fuer die Rissbreite.
- `verformung: VerformungEintrag = field(default_factory=VerformungEintrag)` – Die Verformungsfaelle und das phi ihres Vergroesserungsfaktors.
- `knickfaelle: List[KnickEintrag] = field(default_factory=list)` – Knicknachweise; leer heisst: keiner.
- `spannungsfaelle: List[SpannungsfallEintrag] = field(default_factory=list)` – Auswertungen am Querschnitt -- Bilder, keine Nachweise.
- `automatik_modus: Suchmodus = Suchmodus.GRUND_OHNE_ZULAGE_MIT` – Wonach das Bewehrungswerkzeug sucht -- siehe `bewehrungssuche.Suchmodus`.
- `automatik_dicke: bool = False` – Ob das Werkzeug dazu die duennste Plattendicke sucht («Plattendicke optimieren»). Ein Schalter neben dem Modus und nicht ein eigener Modus: je Dicke laeuft dieselbe Suche im gewaehlten Modus.
- `automatik_y_wie_x: bool = False` – Ob die y-Grundbewehrung jeder Seite der x-Grundbewehrung dieser Seite folgt -- gleicher Durchmesser, gleiche Teilung. Ein Netz, wie es verlegt wird. Die Suche rechnet schon waehrend des Suchens damit: liegt y aussen, kostet ihr Durchmesser x die statische Hoehe.
- `automatik_teilungen: List[float] = field(default_factory=lambda: [150.0])` – Teilungen, die es versucht. Grundbewehrung und Zulage teilen sich eine. Vorgabe ist die eine uebliche. Wer mehrere angibt, bekommt die mit der kleinsten Stahlflaeche -- das kostet aber je Teilung einen ganzen Suchlauf, und meistens steht die Teilung ohnehin fest.
- `automatik_mindestdurchmesser: float = 10.0` – Duennster Stab, den die Suche einbaut -- in mm. Die Grundbewehrung jeder Lage hat ihn mindestens, in x wie in y; die Zulage darf fehlen. Null heisst: kein Mindestdurchmesser, eine Lage darf auch leer bleiben.
- `automatik_grenze: ObergrenzeEintrag = field(default_factory=ObergrenzeEintrag)` – Mehr Querschnitt bekommt keine x-Lage von der Suche -- in allen Modi, auch beim Optimieren der Plattendicke. Vorgabe ⌀30@150, 4712 mm²/m.
- `automatik_mindestdicke: float = 150.0` – Duenner sucht die Dickenoptimierung keine Platte -- in mm.
- `automatik_querkraft: bool = False` – Ob auch die Buegel gesucht werden.
- `automatik_querkraft_teilungen: List[float] = field(default_factory=lambda: [100.0, 150.0, 200.0])`
- `lagen: List[LageEintrag] = field(default_factory=list)` – Genau vier, Index 0 = 1. Lage (unterste). Fehlen welche, sind sie leer.
- `richtung_lage1: Richtung = Richtung.Y` – Richtung der 1. Lage; die 2. bekommt die Gegenrichtung. Vorgabe y, damit x auf der 2. und 3. Lage liegt -- innen. Das ist der unguenstigere Fall und der haeufigere: die Tragrichtung liegt selten zu unterst, weil die Querrichtung darunter durchlaeuft. Wer es anders verlegt, stellt es um.
- `richtung_lage4: Richtung = Richtung.Y` – Richtung der 4. Lage; die 3. bekommt die Gegenrichtung.
- `kombinationen: List[KombinationEintrag] = field(default_factory=list)`
- `tragsicherheit_wahl: RechenwahlEintrag = field(default_factory=RechenwahlEintrag)` – Womit die Tragsicherheit rechnet -- Vorgabe die Handrechnung mit Bemessungswerten. Die Querkraft und das sproede Versagen lesen ihren Momentenwiderstand aus derselben Linie.

#### QuerschnittEintrag.richtung_von

```python
def richtung_von(self, nummer: int) -> Richtung
```

Richtung der Lage 1..4 -- die Paare (1,2) und (3,4) sind gekoppelt.

#### QuerschnittEintrag.materialien

```python
def materialien(self) -> List[str]
```

Jedes Material, auf das die Platte zeigt -- Beton, Stahl jeder Lage,
Buegelstahl --, je einmal. Jeder Verweis zaehlt, auch einer, der gerade nichts traegt: wer das
Material loescht, liesse ihn ins Leere zeigen, und spaetestens die
naechste Aenderung machte daraus einen Fehler beim Rechnen.
Bis 2026-10-17 kannte der Loeschschutz der Oberflaeche den Buegelstahl
nicht.

#### QuerschnittEintrag.bezuege

```python
def bezuege(self) -> List[str]
```

Die Bauteile, deren Querschnitt die Platte nimmt -- keine.

#### QuerschnittEintrag.regeln

```python
def regeln(self, wo: str) -> None
```

Haelt unmoegliche Abmessungen und Namen auf, bevor daraus ein
Widerstand wird -- was mehrere Felder zusammen betrifft; wo jede Zahl
fuer sich liegt, steht an ihrem Feld ([[opencivil.projekt.lesen#bereich|bereich]]).

Bis hierher lief jede Geometrie durch: eine Platte mit `h = -300` wurde
gerechnet, eine mit beidseitiger Ueberdeckung groesser als die Dicke auch.
Heraus kamen Zahlen, die aussahen wie ein Ergebnis. Ein Tragwerksnachweis
darf an so etwas nicht vorbeirechnen -- er muss sagen, was nicht stimmt.

Geprueft wird nur, was geometrisch unmoeglich ist, nicht was unueblich
waere. Ob 20 mm Ueberdeckung fuer die Expositionsklasse genuegen,
entscheidet der Ingenieur.

**Nicht beim Oeffnen.** Eine abgelegte Platte mit `h = 0` liesse sich
sonst nicht mehr oeffnen -- und damit nicht mehr korrigieren. Gefragt
wird vor dem Rechnen ([[opencivil.projekt.lesen#inhalt_pruefen|inhalt_pruefen]]).
Ebenso die Namen der Faelle ([[opencivil.projekt.eintraege#eindeutig|eindeutig]]),
die der Tragsicherheit zuerst: aus ihnen leiten sich die
Gebrauchslisten ab.

#### QuerschnittEintrag.ohne_lastfaelle

```python
def ohne_lastfaelle(self) -> None
```

Jede Lastfallliste leeren -- was bleibt, fragt nicht nach der Belastung.

Die Bewehrungssuche braucht das fuer ihre Modi ohne Kraefte. Die Regel
heisst «alle», ohne Ausnahme, und sie steht neben den Feldern: wer
eine Lastfallliste anfuegt, findet sie hier. Ein Test sucht die Listen
ueber die Typen der Felder und schlaegt an, wenn eine fehlt -- frueher
stand diese Aufzaehlung in der Suche, und die quasi-staendigen waeren
dort beinahe vergessen worden.

#### QuerschnittEintrag.einwirkung

```python
def einwirkung(self, name: str, *, M_Ed: float=0.0, N_Ed: float=0.0, V_Ed: float=0.0) -> KombinationEintrag
```

Eine Tragsicherheitseinwirkung -- kNm, kN und kN/m, Zug positiv.

#### QuerschnittEintrag.knickfall

```python
def knickfall(self, name: str, *, N_Ed: float, M_Ed_1: float=0.0, laenge: float=3.0, knicklaenge: Optional[float]=None) -> KnickEintrag
```

Ein Knicknachweis -- N_Ed in kN (Druck negativ), Laengen in m.

#### QuerschnittEintrag.verformungsfall

```python
def verformungsfall(self, name: str, *, w: float, laenge: float, zugseite: str='unten') -> VerformungsfallEintrag
```

Ein Verformungsfall -- w in mm, mit E_cm ermittelt; die Spannweite in m.

#### QuerschnittEintrag.spannungsfall

```python
def spannungsfall(self, name: str, *, art: str='schnittgroessen', **felder: Any) -> SpannungsfallEintrag
```

Eine Spannung-Dehnung-Analyse -- Felder wie im Eintrag, in kN, kNm und
Promille. Gelesen wie aus einer Datei, also mit denselben Pruefungen:
ein Feld, eine Art oder ein Betongesetz, das es nicht gibt, meldet
sich hier.

#### QuerschnittEintrag.neu

```python
@classmethod
def neu(cls, kennung: str, name: str, beton: str, stahl: str, durchmesser: float=12.0) -> 'QuerschnittEintrag'
```

Eine frische Platte, wie sie der Benutzer angelegt bekommt.

Steht hier und nicht in der Oberflaeche. Dort stand sie einmal -- ein
Wortschatz aus zwanzig Feldern, den jemand von Hand mit den Vorgaben
dieser Klasse gleichhalten musste. Beim ersten Mal, als sich die
Vorgaben aenderten, lief er auseinander: neue Platten brachten
Nachweise eingeschaltet mit, die ueberall sonst aus waren.

Was hier steht, sind Entscheidungen und keine Vorgaben: alle vier
Lagen bewehrt, ein Feldmoment zum Anfangen. Alles Uebrige kommt aus
den Vorgabewerten der Felder.


## Braucht

- [[opencivil.bewehrungssuche.laengs]]
- [[opencivil.core.einheiten]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.lesen]]
- [[opencivil.querschnitt.platte]]

## Gebraucht von

- [[opencivil.projekt]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.projekt]]
