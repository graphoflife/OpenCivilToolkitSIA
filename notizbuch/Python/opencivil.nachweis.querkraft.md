---
erzeugt: 6f9193648b22
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/querkraft.py
> Querkraftnachweis, was beide Ansaetze teilen.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/querkraft.py)

## VERANTWORTUNG

Bestimmt den Querkraftwiderstand einer Platte je Tragrichtung und prueft ihn
gegen die angegebenen Querkraefte.


## ZWEI ANSAETZE, EINER DAVON GILT

Ob die Platte eine Querkraftbewehrung traegt, entscheidet allein, welcher der
beiden laeuft -- je einer eine Klasse in seinem Modul:

* ohne Buegel ([[opencivil.nachweis.querkraft_ohne_buegel|querkraft_ohne_buegel]]):
  `V_Rd = k_d * tau_cd * d_v`, abhaengig von Moment und Normalkraft;
* mit Buegeln ([[opencivil.nachweis.querkraft_buegel|querkraft_buegel]]): das
  Fachwerkmodell mit veraenderlicher Neigung der Druckdiagonalen.

Beides zu addieren waere ein drittes Modell -- und dieses Werkzeug rechnet
nur, was es auch herleitet. Hier steht, was beide teilen: die Faelle, die
statische Hoehe der gezogenen Bewehrung, die Ausgaben, das Urteil und die
letzte Zeile der Herleitung.

Bis 2026-10-25 steckten beide Ansaetze in einer Klasse hinter einem
`buegel is None`, und ihr Befund trug beide Haelften als «vielleicht leer».


## STATISCHE HOEHE

`d` ist die statische Hoehe der *gezogenen* Bewehrung und haengt damit vom
Vorzeichen des Moments ab: bei positivem Moment liegt der Zug unten, bei
negativem oben.

## Inhalt

### _statische_hoehe

```python
def _statische_hoehe(lagen: Sequence[Tuple[float, bool]], h: float, moment_positiv: bool) -> Optional[float]
```

Statische Hoehe der gezogenen Bewehrung, in m ab der gedrueckten Kante.

`lagen` ist eine Folge von `(z ab Oberkante, liegt unten)`.

Bei positivem Moment liegt der Zug unten: gemessen wird von der Oberkante
zur aeussersten unteren Lage. Bei negativem Moment umgekehrt. **Nur die
Lagen der gezogenen Seite zaehlen.** Wer alle nimmt, bekommt bei
einseitiger Bewehrung eine Zahl, die gar keine statische Hoehe ist: eine
Platte nur mit unterer Bewehrung lieferte fuers negative Moment
`h - 261 = 39 mm` -- den Abstand der Unterkante zur *unteren* Lage.

`None`, wenn auf der gezogenen Seite nichts liegt. Dann gibt es kein
`d`, und ohne `d` keinen Querkraftwiderstand.

### lagen_von

```python
def lagen_von(e: Eingaben, posten) -> Tuple[Tuple[float, bool], ...]
```

Je Posten die Tiefe und auf welcher Seite er liegt, `(z, liegt unten)`
-- ohne das laesst sich die gezogene Bewehrung nicht von der gedrueckten
trennen. Fuer den Nachweis und die Kennzahlen.

### zuglage

```python
def zuglage(lagen: Sequence[Tuple[float, bool]], moment_positiv: bool) -> Optional[int]
```

Die aeusserste Lage der gezogenen Seite, als Index in `lagen`.

### _hoch

```python
def _hoch(kurz: str, symbol: str, zeichen: str) -> Tuple[str, str]
```

Kurzname und Zeichen, mit `zeichen` hochgestellt: `d_+` und `d^{+}`.

### protokoll_hoehen

```python
def protokoll_hoehen(p: Protokoll, werte: Zwischenwerte, e: Eingaben, posten, zuglage: int, d: float, d_v: Optional[float]=None, *, seite: Zugseite, zeichen: str='') -> Tuple[Wert, Optional[Wert]]
```

Die statische Hoehe der gezogenen Bewehrung und, ohne Buegel, die
wirksame -- geschrieben, und fuer die Formeln danach. `zuglage` ist der
Posten der aeussersten gezogenen Lage ([[opencivil.nachweis.querkraft#zuglage|zuglage]]), `seite` die
gezogene. `zeichen` hebt die Groessen hoch, wo zwei Seiten
nebeneinander stehen: `d^{+}` (die Kennzahlen).

Mit Buegeln gibt es kein `d_v`: bis 2026-10-18 schrieben die Kennzahlen
dort ein «d_v = d (Einlage nicht massgebend)», weil sie die Hoehen ohne
Buegel mit einer Einlage null mitbenutzten.

### _ohne_zugbewehrung

```python
def _ohne_zugbewehrung(M_Ed: float) -> str
```

Die Begruendung, wenn die gezogene Seite keinen Stahl hat -- fuer beide Ansaetze.

### Querkraftfall

```python
@dataclass(frozen=True)
class Querkraftfall
```

Eine zu pruefende Kombination fuer den Querkraftnachweis.

- `name: str`
- `V_Ed: Groesse`
- `M_Ed: Groesse`
- `N_Ed: Groesse`

#### Querkraftfall.kennung

```python
@property
def kennung(self) -> str
```

### Querkraftergebnis

```python
@dataclass
class Querkraftergebnis(Fallausgang)
```

Was ein Fall ergibt, in beiden Ansaetzen -- ihre eigenen Zwischenwerte
tragen [[opencivil.nachweis.querkraft_ohne_buegel#ErgebnisOhneBuegel|ErgebnisOhneBuegel]]
und [[opencivil.nachweis.querkraft_buegel#ErgebnisMitBuegeln|ErgebnisMitBuegeln]].

- `fall: Querkraftfall`
- `zuglage: Optional[int] = None` – Die aeusserste gezogene Lage, als Index in den Posten -- aus ihr kommt `d`.
- `d: float = 0.0`
- `v_Rd: float = 0.0` – in N/m.
- `ausgang: Ausgang = NICHT_FUEHRBAR` – \|V_Ed\| gegen v_Rd -- nicht fuehrbar, wo sich kein Widerstand bestimmen liess.
- `begruendung: str = ''`

### Querkraft

```python
class Querkraft(Nachweis)
```

Der Querkraftnachweis einer Platte in einer Tragrichtung -- was beide
Ansaetze teilen. Welcher gilt, entscheidet allein, ob die Platte Buegel
traegt: [[opencivil.nachweis.querkraft_ohne_buegel#QuerkraftOhneBuegel|QuerkraftOhneBuegel]]
oder [[opencivil.nachweis.querkraft_buegel#QuerkraftMitBuegeln|QuerkraftMitBuegeln]].

- `THEMA = 'Querkraft'`
- `ART = 'V'`
- `buegel = None` – Die Buegel der Platte -- nur der Ansatz mit Buegeln hat welche.

#### Querkraft._ansatzbezuege

```python
@abstractmethod
def _ansatzbezuege(self) -> List[Eingabebezug]
```

Was der Ansatz ausser der Hoehe und den Lagen der Bewehrung liest.

#### Querkraft._befunde

```python
def _befunde(self) -> List[Befundbezug]
```

Wessen Befund der Ansatz liest -- ohne Buegel den des M-N-Nachweises.

#### Querkraft._eintragen

```python
def _eintragen(self, erg: Querkraftergebnis, ergebnis: Dict[str, Groesse], urteile: List[NachweisUrteil]) -> None
```

Ausgaben und Urteil eines Falls -- fuer beide Ansaetze dieselben.

Was ein Querkraftnachweis herausgibt, haengt nicht davon ab, wie der
Widerstand zustande kam. Zweimal geschrieben liefen die beiden Faelle
frueher oder spaeter auseinander.

#### Querkraft._einwirkung

```python
def _einwirkung(self, fall: Querkraftfall) -> Wert
```

Die Querkraft als Betrag -- fuer Urteil und Erfuellungsgrad dieselbe.

Das Vorzeichen spielt keine Rolle, verglichen wird der Betrag. Also
steht auch der Betrag da; sonst teilte der Leser den Widerstand durch
eine negative Zahl und bekaeme etwas anderes als den danebenstehenden
Erfuellungsgrad. Die Betragsstriche stehen trotzdem nicht am Symbol:
sie sagen nichts, was die Zahl daneben nicht schon zeigt.

#### Querkraft._widerstand

```python
def _widerstand(self, erg: Querkraftergebnis) -> Wert
```

Der Widerstand eines Falls -- fuer Urteil und Herleitung derselbe.

Er gilt nur unter genau dieser Einwirkung; das gehoert ins Symbol,
sonst liest sich V_Rd wie ein Kennwert des Querschnitts.

#### Querkraft._widerstandssymbol

```python
def _widerstandssymbol(self, fall: Querkraftfall) -> str
```

`V_Rd(M_Ed = 100 kNm, N_Ed = -300 kN)` -- der Widerstand ist bedingt.

#### Querkraft._protokoll_grad

```python
def _protokoll_grad(self, p: Protokoll, erg: Querkraftergebnis) -> None
```

Die letzte Zeile jedes Falls -- für beide Ansätze dieselbe. Der
Widerstand steht hier kurz: seine Bedingung steht in der Zeile, die ihn
herleitet.


## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.querschnitt.lagenaufbau]]
- [[opencivil.querschnitt.platte]]
- [[opencivil.querschnitt.zugseite]]

## Gebraucht von

- [[opencivil.nachweis.kennzahlen]]
- [[opencivil.nachweis.querkraft_buegel]]
- [[opencivil.nachweis.querkraft_ohne_buegel]]
- [[opencivil.projekt.aufbau.platte]]

## Formeln aus diesem Modul

- [[Wirksame Höhe (Einlage nicht massgebend)]] · `protokoll_hoehen`
- [[Wirksame Höhe, um die Einlage vermindert]] · `protokoll_hoehen`
