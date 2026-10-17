---
erzeugt: 80d5da004d7a
art: modul
tags: [modul]
---
> [!abstract] opencivil/material/basis.py
> Gemeinsames Geruest fuer Baustoffe.
> Paket [[opencivil.material]] · [Quelltext](../../opencivil/material/basis.py)

## VERANTWORTUNG

Ein Baustoff ist im Rechenwerk kein Sonderfall, sondern nur ein Namensraum
voller Werte und Berechnungen. Diese Datei stellt das Geruest bereit, mit dem
Beton und Betonstahl (und spaeter weitere) ihre Werte deklarieren.


## WARUM VORLAGEN UND EXEMPLARE GETRENNT SIND

Im alten Code war die Liste der Betonvariablen eine Liste veraenderlicher
Objekte auf Modulebene, die zugleich als Vorlage und als Rechenobjekt diente.
Zwei Betone im selben Projekt haetten sich gegenseitig ueberschrieben. Hier
sind Vorlagen unveraenderliche Beschreibungen; `erzeuge()` giesst daraus fuer
jedes Material ein eigenes Exemplar mit eigenem Namensraum.


## ALLES IST UEBERSCHREIBBAR

Jeder abgeleitete Kennwert ist eine gewoehnliche Berechnung. Wer ihn von Hand
setzen will, ruft `werk.setze(...)` -- die Berechnung wird dann uebersprungen,
und im Bericht steht der Wert als 'vom Benutzer überschrieben'.

## Inhalt

### mit_index

```python
def mit_index(symbol: str, index: str) -> str
```

Haengt einen Materialindex an ein Symbol an.

Sind mehrere Betone oder Staehle im Spiel, traegt sonst jeder dasselbe
Symbol: im Bericht staenden dann mehrere gleich aussehende Gleichungen mit
verschiedenen Zahlen. Mit Index wird daraus `f_{yd,\text{B500B}}`.

Ein vorhandener Tiefindex wird erweitert, ein Hochgestelltes bleibt aussen:

```
f_{yd}        -> f_{yd,\text{B500B}}
E_s           -> E_{s,\text{B500B}}
\gamma_s      -> \gamma_{s,\text{B500B}}
f_{yk}^{-}    -> f_{yk,\text{B500B}}^{-}
```

### Baustoffart

```python
class Baustoffart(Wahl)
```

- `BETON = 'beton'`
- `BETONSTAHL = 'betonstahl'`

#### Baustoffart.beschriftung

```python
@property
def beschriftung(self) -> str
```

### KennwertVorlage

```python
@dataclass(frozen=True)
class KennwertVorlage
```

Beschreibung eines Baustoffkennwerts -- unabhaengig vom konkreten Material.

Ist `funktion` gesetzt, wird der Kennwert gerechnet; sonst ist er eine
Eingabe, deren Zahlenwert aus der Sortenvorlage kommt.

- `kurzname: str`
- `symbol: str`
- `einheit: Einheit = EINHEITSLOS`
- `beschreibung: str = ''`
- `referenz: str = ''`
- `stellen: int = 2`
- `funktion: Optional[FormelFunktion] = None`
- `vorlage_latex: Optional[str] = None`
- `eingaben: Tuple[str, ...] = ()` – Kurznamen der Kennwerte desselben Baustoffs, die eingehen.
- `festwert: Optional[Groesse] = None` – Normvorgabe, die nicht aus der Sortentabelle kommt (z.B. gamma_c).
- `begruendung: str = ''`
- `name: str = ''` – Name der Formel im Notizbuch, wo die Beschreibung nicht taugt -- siehe `GleichungBlock.name`.

#### KennwertVorlage.ist_berechnet

```python
@property
def ist_berechnet(self) -> bool
```

#### KennwertVorlage.ist_festwert

```python
@property
def ist_festwert(self) -> bool
```

#### KennwertVorlage.definition

```python
def definition(self, praefix: str, symbol_index: str='') -> WertDef
```

### Baustoff

```python
@dataclass
class Baustoff
```

Ein konkretes Material im Modell: eigener Namensraum, eigene Berechnungen.

Beispiel:

```python
c30 = beton("C30/37")
werk.registriere(*c30.berechnungen)
werk.setze(c30.id_von("f_ck"), Groesse(32, MPA))   # abweichender Wert
loesung = werk.loese(c30.id_von("f_cd"))
```

- `id: str` – Namensraum, z.B. `beton.C30_37`.
- `name: str` – Anzeigename, z.B. `C30/37`.
- `art: Baustoffart`
- `sorte: str = ''`
- `symbol_index: str = ''` – Index, der an die Symbole dieses Baustoffs gehaengt wird -- leer, solange es nur einen seiner Art gibt. Steht hier, damit auch die Nachweise ihn erreichen. Sie bauen Symbole wie `f_{cd}` selbst, und ohne den Index waere bei zwei Betonen nicht zu sehen, welcher gemeint ist. Vergeben wird er beim Aufbau des Projekts, wo sich zaehlen laesst, wie viele Baustoffe einer Art vorkommen.
- `definitionen: Dict[str, WertDef] = field(default_factory=dict)`
- `berechnungen: List[Berechnung] = field(default_factory=list)`
- `eingabewerte: Dict[str, Groesse] = field(default_factory=dict)` – Zahlenwerte aus der Sortenvorlage, nach Kurzname.

#### Baustoff.id_von

```python
def id_von(self, kurzname: str) -> str
```

Globale Wert-ID zu einem Kurznamen, z.B. `f_cd` -> `beton.C30_37.f_cd`.

#### Baustoff.definition

```python
def definition(self, kurzname: str) -> WertDef
```

#### Baustoff.kurzname_pruefen

```python
def kurzname_pruefen(self, kurzname: str) -> str
```

#### Baustoff.kennwerte

```python
@property
def kennwerte(self) -> Tuple[str, ...]
```

#### Baustoff.ins_rechenwerk

```python
def ins_rechenwerk(self, werk) -> 'Baustoff'
```

Meldet Berechnungen und Sortenwerte beim Rechenwerk an.

Die Sortenwerte werden als [[opencivil.core.berechnung#Vorgabe|Vorgabe]]-Berechnungen registriert und
nicht als gesetzte Eingaben -- so bleiben sie normale Knoten im Graphen
und der Benutzer kann sie mit `werk.setze(...)` ueberschreiben.

Mehrfaches Anmelden ist ausdruecklich erlaubt und wirkungslos: derselbe
Beton wird von jedem Querschnitt gebraucht, der ihn verwendet, und keiner
von ihnen kann wissen, ob ein anderer ihn schon angemeldet hat.

#### Baustoff.ist_angemeldet

```python
def ist_angemeldet(self, werk) -> bool
```

Prueft, ob dieser Baustoff im Rechenwerk schon bekannt ist.

### erzeuge

```python
def erzeuge(*, art: Baustoffart, name: str, sorte: str, vorlagen: Sequence[KennwertVorlage], werte: Mapping[str, Groesse], praefix: Optional[str]=None, symbol_index: str='') -> Baustoff
```

Giesst aus den Vorlagen ein Material mit eigenem Namensraum.

:param werte: Zahlenwerte der Eingabekennwerte, nach Kurzname
(typischerweise aus der Sortentabelle).


## Konstanten

- `_SYMBOL = re.compile('^(?P<basis>.+?)(?:_\\{(?P<tief_lang>[^{}]*)\\}|_(?P<tief_…` – Symbol mit optionalem Index und optionalem Hochgestellten, z.B. `f_{yk}^{-}`.
- `text_maskieren = text_latex` – Maskierung fuer `\text{...}`. Liegt in core.latex, weil es nichts mit Baustoffen zu tun hat -- der Name bleibt hier als gewohnter Zugang stehen.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wahl]]
- [[opencivil.core.wert]]

## Gebraucht von

- [[opencivil.material.beton]]
- [[opencivil.material.betonstahl]]
- [[opencivil.nachweis.duktilitaet]]
- [[opencivil.nachweis.handrechnung]]
- [[opencivil.nachweis.qa_gebrauch]]
- [[opencivil.nachweis.rechenwahl]]
- [[opencivil.nachweis.richtungsnachweise]]
- [[opencivil.nachweis.spannungsbegrenzung]]
- [[opencivil.nachweis.stabgrenzen]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.platte]]
- [[opencivil.spannungsanalyse.herleitung]]
- [[opencivil.spannungsanalyse.schnitt]]
- [[opencivil.stabwerk.rechnung]]
