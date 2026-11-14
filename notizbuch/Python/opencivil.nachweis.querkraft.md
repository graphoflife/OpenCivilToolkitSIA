---
erzeugt: f72aeaafd466
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
negativem oben. Gemessen wird bis zum Schwerpunkt aller gezogenen Posten der
Richtung -- Grundbewehrung, Zulage, auch mehrere Lagen (SIA 262:2025,
4.3.3.2.2). Bis 2026-11-14 galt der aeusserste Posten; mit einer Zulage war
`d` damit 1 bis 3 mm zu gross.

## Inhalt

### zugposten

```python
def zugposten(posten: Sequence[Postenbezug], moment_positiv: bool) -> List[Postenbezug]
```

Die Posten der gezogenen Seite: bei positivem Moment die unteren, bei
negativem die oberen. **Nur sie zaehlen.** Wer alle nimmt, bekommt bei
einseitiger Bewehrung eine Zahl, die gar keine statische Hoehe ist: eine
Platte nur mit unterer Bewehrung lieferte fuers negative Moment
`h - 261 = 39 mm` -- den Abstand der Unterkante zur *unteren* Lage.

### statische_hoehen

```python
def statische_hoehen(e: Eingaben, posten: Sequence[Postenbezug]) -> Dict[bool, float]
```

Je Momentenrichtung (`True`: Zug unten) die statische Hoehe der
gezogenen Bewehrung, in m ab dem gedrueckten Rand -- im Schwerpunkt ihrer
Posten ([[opencivil.querschnitt.lagenaufbau#lage_aus_posten|lage_aus_posten]]). Fuer
den Nachweis und die Kennzahlen.

Fehlt eine Richtung, liegt auf ihrer Zugseite keine Bewehrung. Dann gibt
es kein `d`, und ohne `d` keinen Querkraftwiderstand.

### _hoch

```python
def _hoch(kurz: str, symbol: str, zeichen: str) -> Tuple[str, str]
```

Kurzname und Zeichen, mit `zeichen` hochgestellt: `d_+` und `d^{+}`.

### protokoll_hoehen

```python
def protokoll_hoehen(p: Protokoll, werte: Zwischenwerte, e: Eingaben, gezogen: Sequence[Postenbezug], d: float, d_v: Optional[float]=None, *, seite: Zugseite, zeichen: str='') -> Tuple[Wert, Optional[Wert]]
```

Die statische Hoehe der gezogenen Bewehrung und, ohne Buegel, die
wirksame -- geschrieben, und fuer die Formeln danach. `gezogen` sind die
Posten der gezogenen Seite ([[opencivil.nachweis.querkraft#zugposten|zugposten]]), `seite` die gezogene.
Liegen dort mehrere, steht zuerst ihr Schwerpunkt da. `zeichen` hebt die
Groessen hoch, wo zwei Seiten nebeneinander stehen: `d^{+}` (die
Kennzahlen).

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
- `zugposten: Tuple[Postenbezug, ...] = ()` – Die Posten der gezogenen Seite -- aus ihrem Schwerpunkt kommt `d`; leer ohne Zugbewehrung.
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
- `REFERENZ: str` – Wo der Widerstand des Ansatzes steht -- fuer Nachweis, Widerstand und Erfuellungsgrad.
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


## Konstanten

- `REFERENZ_EINLAGE = 'SIA 262:2025, 4.3.3.2.9'` – Wo die wirksame Hoehe und ihre Einlage stehen.

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

- [[opencivil.nachweis.kennzahlen]]
- [[opencivil.nachweis.querkraft_buegel]]
- [[opencivil.nachweis.querkraft_ohne_buegel]]
- [[opencivil.projekt.aufbau.platte]]

## Formeln aus diesem Modul

- [[Wirksame Höhe ohne Abzug]] · `protokoll_hoehen`
- [[Wirksame Höhe, um die Einlage vermindert]] · `protokoll_hoehen`
