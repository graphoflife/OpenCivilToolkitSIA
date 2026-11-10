---
erzeugt: 04866cab6b11
art: modul
tags: [modul]
---
> [!abstract] opencivil/durchstanzen/flaeche.py
> die gestützte Fläche: was Lage und Form für den Nachweis heissen.
> Paket [[opencivil.durchstanzen]] · [Quelltext](../../opencivil/durchstanzen/flaeche.py)

## VERANTWORTUNG

Die Wahlen der Lage und der Form ([[opencivil.durchstanzen.flaeche#Lage|Lage]], [[opencivil.durchstanzen.flaeche#Stuetzenform|Stuetzenform]]) und
je Lage eine Art gestützter Fläche: [[opencivil.durchstanzen.flaeche#Innenstuetze|Innenstuetze]],
[[opencivil.durchstanzen.flaeche#Randstuetze|Randstuetze]] und [[opencivil.durchstanzen.flaeche#Eckstuetze|Eckstuetze]] mit ihrer Form,
[[opencivil.durchstanzen.flaeche#Wandende|Wandende]] und [[opencivil.durchstanzen.flaeche#Wandecke|Wandecke]]. Jede Art weiss, was der Nachweis
von ihr braucht -- ihre Masse, den Umriss, die Achse, die Plattenränder, die
Kandidaten des Nachweisschnitts, u_0 als Formel, wo es eine gibt, die
Näherung für k_e, die Gleichungen der Momente im Stützstreifen und ob das
Werkzeug Durchstanzbewehrung und Stahlpilze vorschlägt. Welche Art es ist,
entscheidet [[opencivil.durchstanzen.flaeche#Lage.flaeche|Lage.flaeche]] einmal. Bis 2026-11-10 fragten Stelle,
Nachweis, Bewehrung und Maske an 28 Stellen nach Lage und Form.


## KOORDINATEN

In der Ebene der Platte, in m. Eine Stütze steht mit ihrer Achse im
Ursprung; der Plattenrand einer Randstütze liegt unten (y negativ), bei der
Eckstütze liegt ein zweiter links (x negativ). Ein Wandende liegt im
Ursprung, die Wand läuft nach +x; eine Wandecke liegt mit ihrer äusseren
Ecke im Ursprung, die Wände laufen nach +x und +y, die Platte liegt aussen.


## EINHEITEN

SI-Basis.

## Inhalt

### Mass

```python
@dataclass(frozen=True)
class Mass
```

Ein Mass in einer Formel: sein Kurzname, sein Zeichen und sein Wert in m.

- `name: str`
- `zeichen: str`
- `wert: float`

### Umfangsformel

```python
@dataclass(frozen=True)
class Umfangsformel
```

u_0 in geschlossener Form: der Wert und wie die Herleitung ihn schreibt.

- `wert: float`
- `vorlage: str`
- `eingaben: Dict[str, Wert]`
- `titel: str`
- `referenz: str`
- `name: Optional[str] = None`

### Randbreite

```python
@dataclass(frozen=True)
class Randbreite
```

Was die Breite b_sr eines Stützstreifens am Plattenrand bestimmt
(Figur 25): b_sr = quer + 2 · (längs + a), mit den Abmessungen der Stütze
quer und längs zum Streifen und ihrem Abstand zum Rand.

- `quer: Mass`
- `laengs: Mass`
- `abstand: Mass`

### Momentengleichung

```python
@dataclass(frozen=True)
class Momentengleichung
```

Wie 4.3.6.4.7 das mittlere Moment im Stützstreifen einer Richtung rechnet:
m_sd = max[V_d · (1/8 + e_u / (teiler · b)); mindest · V_d]. Die Breite b
ist b_s, am Plattenrand b_sr nach `rand`.

- `nummer: str`
- `teiler: float`
- `mindest: float = 0.0`
- `rand: Optional[Randbreite] = None`

### Stuetzenform

```python
class Stuetzenform(Wahl)
```

Die Form einer Stütze im Grundriss. Die Ovalstütze ist ein Rechteck mit
halbrunden Enden, b_x × b_y über alles -- so heisst sie in der Software von
Leviat (DURA); der Name ist nicht aus der Norm.

- `RECHTECK = 'rechteck'`
- `RUND = 'rund'`
- `OVAL = 'oval'`

#### Stuetzenform.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Stuetzenform.masse

```python
@property
def masse(self) -> Tuple[str, ...]
```

#### Stuetzenform.kurz

```python
@property
def kurz(self) -> str
```

Wie die Liste die Stütze nennt -- mit den Kurznamen ihrer Masse, in mm.

#### Stuetzenform.flaeche

```python
def flaeche(self, masse: Masse) -> Stuetzenflaeche
```

Die Stütze aus ihren Massen, mit der Achse im Ursprung.

#### Stuetzenform.breite

```python
def breite(self, masse: Masse, achse: str) -> Mass
```

Die Abmessung in `achse` («x» oder «y») -- an der Rundstütze der Durchmesser.

#### Stuetzenform.umfang

```python
def umfang(self, e: Eingaben, d_v: Wert, wert: float) -> Umfangsformel
```

u_0 rundum, ohne Rand, Ecken und Aussparungen (Figur 22) -- `wert` aus dem Schnitt.

### Lage

```python
class Lage(Wahl)
```

Wo die gestützte Fläche in der Platte liegt -- [[opencivil.durchstanzen.flaeche#Lage.flaeche|flaeche]] macht daraus ihre Art.

- `INNEN = 'innen'`
- `RAND = 'rand'`
- `ECKE = 'ecke'`
- `WANDENDE = 'wandende'`
- `WANDECKE = 'wandecke'`

#### Lage.beschriftung

```python
@property
def beschriftung(self) -> str
```

#### Lage.mehrzahl

```python
@property
def mehrzahl(self) -> str
```

«Innenstützen», «Wandenden» -- wie die Näherung von 4.3.6.2.5 sie nennt.

#### Lage.flaeche

```python
def flaeche(self, form: Stuetzenform) -> 'GestuetzteFlaeche'
```

Die Art der gestützten Fläche; `form` gilt nur für Stützen.

### GestuetzteFlaeche

```python
class GestuetzteFlaeche(ABC)
```

Eine Art gestützter Fläche -- siehe Dateikopf.

- `lage: ClassVar[Lage]`
- `titel: ClassVar[str]` – Wie die Maske ihre Masse überschreibt: «Stütze» oder «Wand».
- `k_e: ClassVar[float]` – Die Näherung nach SIA 262:2025, 4.3.6.2.5.
- `hat_form: ClassVar[bool] = False`
- `momente: ClassVar[bool] = True` – Ob 4.3.6.4.7 Momente im Stützstreifen nennt -- für Wände nicht.
- `ecken_abziehen: ClassVar[bool] = True` – Ob neben Ecken etwas vom Schnitt abgeht -- an Wänden zählt u_0 nur 1.5·d_v entlang der Wand.
- `vorschlag: ClassVar[bool] = True` – Ob das Werkzeug Durchstanzbewehrung vorschlägt -- an Wänden noch nicht.
- `stahlpilz: ClassVar[bool] = False` – Ob ein ZEUS-Stahlpilz in Frage kommt: der Katalog hat sie nur für Innenstützen.
- `k_sys_erhoeht: ClassVar[bool] = False` – Ob das Gutachten von ancoPLUS 3·k_r zulässt: an Innenstützen und Wandenden.

#### GestuetzteFlaeche.masse

```python
@property
@abstractmethod
def masse(self) -> Tuple[str, ...]
```

Die Kurznamen der Masse, die für sie gelten.

#### GestuetzteFlaeche.kurz

```python
@property
@abstractmethod
def kurz(self) -> str
```

Wie die Liste sie nennt -- mit den Kurznamen ihrer Masse, in mm.

#### GestuetzteFlaeche.kandidaten

```python
@abstractmethod
def kandidaten(self, masse: Masse, abstand: float, d_v: float) -> List[Kandidat]
```

Die möglichen Nachweisschnitte im Abstand `abstand` -- siehe [[opencivil.durchstanzen.schnitt|.schnitt]].

#### GestuetzteFlaeche.umriss

```python
@abstractmethod
def umriss(self, masse: Masse, d_v: float) -> List[Punkt]
```

Der Umriss fürs Bild.

#### GestuetzteFlaeche.achse

```python
def achse(self, masse: Masse) -> Punkt
```

Die Achse -- von ihr gehen die Strahlen an Aussparungen vorbei.

#### GestuetzteFlaeche.raender

```python
def raender(self, masse: Masse) -> Tuple[Halbebene, ...]
```

Die Plattenränder.

#### GestuetzteFlaeche.umfang

```python
def umfang(self, e: Eingaben, d_v: Wert, a: Auswertung) -> Optional[Umfangsformel]
```

u_0 als Formel -- oder nichts, dann steht der Schnitt als Länge in der Platte.

#### GestuetzteFlaeche.k_e_naeherung

```python
def k_e_naeherung(self, a: Auswertung) -> Tuple[float, str]
```

Die Näherung für k_e und wie die Herleitung sie nennt.

#### GestuetzteFlaeche.momentengleichung

```python
def momentengleichung(self, r: Richtung, masse: Masse) -> Momentengleichung
```

Die Gleichung der Momente im Stützstreifen in `r` -- nur, wo [[opencivil.durchstanzen.flaeche#GestuetzteFlaeche|momente]] gilt.

### Stuetze

```python
@dataclass(frozen=True)
class Stuetze(GestuetzteFlaeche)
```

Eine Stütze mit ihrer Form; am Rand und an der Ecke mit dem Abstand zum Rand.

- `form: Stuetzenform`
- `titel: ClassVar[str] = 'Stütze'`
- `hat_form: ClassVar[bool] = True`
- `randmasse: ClassVar[Tuple[str, ...]] = ()`

#### Stuetze.masse

```python
@property
def masse(self) -> Tuple[str, ...]
```

#### Stuetze.kurz

```python
@property
def kurz(self) -> str
```

#### Stuetze.kandidaten

```python
def kandidaten(self, masse: Masse, abstand: float, d_v: float) -> List[Kandidat]
```

#### Stuetze.umriss

```python
def umriss(self, masse: Masse, d_v: float) -> List[Punkt]
```

#### Stuetze._randbreite

```python
def _randbreite(self, r: Richtung, masse: Masse) -> Randbreite
```

Der Streifen in `r` am Plattenrand: quer zu ihm die Stütze, längs ihr Abstand zum Rand.

### Innenstuetze

```python
@dataclass(frozen=True)
class Innenstuetze(Stuetze)
```

- `lage: ClassVar[Lage] = Lage.INNEN`
- `k_e: ClassVar[float] = 0.9`
- `stahlpilz: ClassVar[bool] = True`
- `k_sys_erhoeht: ClassVar[bool] = True`

#### Innenstuetze.umfang

```python
def umfang(self, e: Eingaben, d_v: Wert, a: Auswertung) -> Optional[Umfangsformel]
```

Rundum, wo nichts neben Ecken oder hinter Aussparungen abgeht, die Formel der Form.

#### Innenstuetze.k_e_naeherung

```python
def k_e_naeherung(self, a: Auswertung) -> Tuple[float, str]
```

Mit grossen Aussparungen in Stützennähe gilt 0.7 wie am Rand (4.3.6.2.5).

#### Innenstuetze.momentengleichung

```python
def momentengleichung(self, r: Richtung, masse: Masse) -> Momentengleichung
```

### Randstuetze

```python
@dataclass(frozen=True)
class Randstuetze(Stuetze)
```

- `lage: ClassVar[Lage] = Lage.RAND`
- `k_e: ClassVar[float] = 0.7`
- `randmasse: ClassVar[Tuple[str, ...]] = ('a_y',)`

#### Randstuetze.raender

```python
def raender(self, masse: Masse) -> Tuple[Halbebene, ...]
```

Der Rand unten.

#### Randstuetze.momentengleichung

```python
def momentengleichung(self, r: Richtung, masse: Masse) -> Momentengleichung
```

Parallel zum Rand (63), senkrecht zu ihm (64) mit b_sr.

### Eckstuetze

```python
@dataclass(frozen=True)
class Eckstuetze(Stuetze)
```

- `lage: ClassVar[Lage] = Lage.ECKE`
- `k_e: ClassVar[float] = 0.65`
- `randmasse: ClassVar[Tuple[str, ...]] = ('a_x', 'a_y')`

#### Eckstuetze.raender

```python
def raender(self, masse: Masse) -> Tuple[Halbebene, ...]
```

Der Rand unten und der links.

#### Eckstuetze.momentengleichung

```python
def momentengleichung(self, r: Richtung, masse: Masse) -> Momentengleichung
```

### Wand

```python
class Wand(GestuetzteFlaeche)
```

Das Ende oder die Ecke einer Wand mit der Dicke t. Entlang der Wand zählt
der Schnitt 1.5·d_v; was dahinter läuft, gehört nicht dazu (Figur 23b
und c).

- `titel: ClassVar[str] = 'Wand'`
- `k_e: ClassVar[float] = 0.75`
- `momente: ClassVar[bool] = False`
- `ecken_abziehen: ClassVar[bool] = False`
- `vorschlag: ClassVar[bool] = False`

#### Wand.masse

```python
@property
def masse(self) -> Tuple[str, ...]
```

#### Wand.kurz

```python
@property
def kurz(self) -> str
```

### Wandende

```python
class Wandende(Wand)
```

- `lage: ClassVar[Lage] = Lage.WANDENDE`
- `k_sys_erhoeht: ClassVar[bool] = True`

#### Wandende.kandidaten

```python
def kandidaten(self, masse: Masse, abstand: float, d_v: float) -> List[Kandidat]
```

#### Wandende.umriss

```python
def umriss(self, masse: Masse, d_v: float) -> List[Punkt]
```

Die Wand 4·d_v weit -- etwas über den Schnitt hinaus, der 3.5·d_v weit reicht.

#### Wandende.achse

```python
def achse(self, masse: Masse) -> Punkt
```

#### Wandende.umfang

```python
def umfang(self, e: Eingaben, d_v: Wert, a: Auswertung) -> Optional[Umfangsformel]
```

### Wandecke

```python
class Wandecke(Wand)
```

- `lage: ClassVar[Lage] = Lage.WANDECKE`

#### Wandecke.kandidaten

```python
def kandidaten(self, masse: Masse, abstand: float, d_v: float) -> List[Kandidat]
```

#### Wandecke.umriss

```python
def umriss(self, masse: Masse, d_v: float) -> List[Punkt]
```

Die beiden Wände je 4·d_v weit.

#### Wandecke.achse

```python
def achse(self, masse: Masse) -> Punkt
```

#### Wandecke.umfang

```python
def umfang(self, e: Eingaben, d_v: Wert, a: Auswertung) -> Optional[Umfangsformel]
```


## Konstanten

- `Masse = Dict[str, float]` – Die Masse einer Stelle in m, nach ihrem Kurznamen.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.wahl]]
- [[opencivil.core.wert]]
- [[opencivil.durchstanzen.schnitt]]
- [[opencivil.querschnitt.platte]]

## Gebraucht von

- [[opencivil.durchstanzen.nachweis]]
- [[opencivil.durchstanzen.stelle]]
- [[opencivil.projekt.durchstanzen]]
- [[opencivil.web.durchstanzdaten]]
