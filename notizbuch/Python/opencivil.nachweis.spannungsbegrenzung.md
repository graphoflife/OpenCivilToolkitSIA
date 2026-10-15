---
erzeugt: dfc85a441a87
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/spannungsbegrenzung.py
> Stahlspannung unter Gebrauchslasten.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/spannungsbegrenzung.py)

## VERANTWORTUNG

Bestimmt je Lastfall die Stahlspannung im gerissenen Querschnitt und haelt sie
gegen eine Grenze. Zwei Nachweise teilen sich diese Rechnung:

* **Gegen Fliessen**, unter *haeufiger* Einwirkung: ``sigma_s \<= f_yd - 80
  N/mm²`` (SIA 262:2025, Tabelle 17). Nur bei erhoehter und hoher
  Anforderung -- bei normaler steht in der Tabelle ein Strich.
* **Aus der Rissbreite**, unter *quasi-staendiger* Einwirkung:
  `sigma_s <= sigma_s,adm`, dieselbe zulaessige Spannung wie bei der
  Zwaengung -- `f_yk` bei normaler Anforderung, die Wurzelformel mit
  `w_nom` bei erhoehter und hoher. Immer gefuehrt.


## EINE KLASSE, ZWEI GRENZEN

Die Rechnung ist in beiden Faellen dieselbe: derselbe Loeser, dieselbe
Fallschleife, dieselbe groesste Zugdehnung. Verschieden ist allein die
Grenze -- ihre Zahl, die Eingaben, aus denen sie entsteht, und ihr Absatz in
der Herleitung. Die drei gehoeren zusammen und stehen darum in einem Objekt,
das dem Nachweis mitgegeben wird ([[opencivil.nachweis.spannungsbegrenzung#Spannungsgrenze|Spannungsgrenze]]). Zwei Klassen
mit kopiertem Kern waeren genau die Fehlerklasse, vor der `zustand2.py`
warnt: zwei Nachweise, die fuer denselben Querschnitt verschiedene sigma_s
melden.


## WIE DIE SPANNUNG ENTSTEHT

Ueber [[opencivil.nachweis.querschnittsloeser]]: gesucht wird die
Dehnungsebene, die `M_Ed` und `N_Ed` des Lastfalls im Gleichgewicht
haelt. Der Beton nimmt keinen Zug auf. Womit gerechnet wird, waehlt das
Kapitel ([[opencivil.nachweis.rechenwahl#Rechenwahl|Rechenwahl]]): die
Kriechzahl, den Wertesatz und die Rechenart. Die Vorgabe ist, wie bis
2026-10-09 fest: **elastisch** -- der Beton im Druck linear mit dem wirksamen
Modul `E_cm/(1+phi)` -- mit den **charakteristischen** Festigkeiten: der
Stahl fliesst bei `f_yk`, der Beton traegt hoechstens `f_ck`.

Die gedrueckte Bewehrung wirkt mit, wie im Querschnitt -- nur in der
Rechenart «Handrechnung» nicht. Gemessen wird an der am staerksten
gezogenen Lage. (Bis 2026-10-09 stand hier, nur gezogene Bewehrung zaehle;
gerechnet wurde aber schon damals mit beiden.)


## WENN DER STAHL FLIESST

Auf dem Plateau bleibt die Spannung bei `f_yk` stehen. Bei normaler
Anforderung ist aber gerade `f_yk` die Grenze -- ein fliessender Stahl
haette dann `sigma_s = sigma_s,adm` und stuende mit Erfuellungsgrad 1.00
als «erfuellt» in der Tabelle. Darum wird an der **Dehnung** gemessen:

```
alpha = sigma_s,adm / (E_s * eps_s)
```

Solange der Stahl elastisch bleibt, ist `E_s * eps_s` genau `sigma_s`, und
das ist der uebliche Spannungsvergleich, Bit fuer Bit. Fliesst er, waechst die
Dehnung weiter, waehrend die Spannung stehen bleibt: der Nachweis faellt
durch, und zwar um so deutlicher, je weiter die Bewehrung ueber die Grenze
gedehnt ist. Das braucht auch die Bewehrungssuche -- ein Erfuellungsgrad, der
auf dem Plateau festsitzt, zeigt ihr keine Richtung.


## WAS IN DER MITSCHRIFT STEHT

Der **Ablauf** der Suche (aus [[opencivil.nachweis.querschnittsloeser#protokoll_verfahren|querschnittsloeser.protokoll_verfahren]]),
die Festlegungen dahinter -- Kriechzahl, Werkstoffgesetze, Grenze --, dann je
Fall die gefundene Ebene und die **Probe**: mit diesem `eps_m` und `chi`
entstehen genau `N_Ed` und `M_Ed`. Die einzelnen Halbierungen stehen nicht
da; sie sind kein Rechenschritt, sondern der Weg zu einem, und belegt wird der
durch die Probe.

## Inhalt

### Gebrauchsfall

```python
@dataclass(frozen=True)
class Gebrauchsfall
```

Eine Schnittgroessenkombination unter Gebrauchslast.

Haeufig oder quasi-staendig -- das sagt nicht der Fall, sondern der
Nachweis, dem er mitgegeben wird.

- `name: str`
- `M_Ed: Groesse`
- `N_Ed: Groesse`

#### Gebrauchsfall.kennung

```python
@property
def kennung(self) -> str
```

### Vergleich

```python
@dataclass(frozen=True)
class Vergleich
```

Was in der Tabelle gegeneinander steht -- und wie es im Satz heisst.

Spannungen, solange der Stahl elastisch bleibt. Fliesst er, Dehnungen:
sonst stuende `f_yk` neben `f_yk` und daneben «nicht erfuellt» --
richtig gerechnet und doch nicht zu lesen. Entschieden wird das einmal,
in [[opencivil.nachweis.spannungsbegrenzung#Spannungsbegrenzung|Spannungsbegrenzung._einen_fall]]; Urteil und Begruendung lesen
es nur noch ab.

- `einwirkung: Wert`
- `widerstand: Wert`
- `satz: str`

### Fallergebnis

```python
@dataclass
class Fallergebnis
```

Was der Nachweis fuer einen Lastfall gefunden hat.

- `fall: Gebrauchsfall`
- `eps_m: float = 0.0`
- `chi: float = 0.0`
- `N_int: float = 0.0`
- `M_int: float = 0.0`
- `eps_s: float = 0.0` – Groesste Zugdehnung in der Bewehrung.
- `sigma_s: float = 0.0` – Die Spannung dazu, in Pa -- auf dem Plateau `f_yk`.
- `sigma_s_adm: float = 0.0`
- `eps_s_adm: float = 0.0` – `sigma_s_adm / E_s` -- dagegen wird gemessen, wenn der Stahl fliesst.
- `eps_y: float = 0.0` – Die Fliessdehnung `f_yk / E_s`.
- `stahl: Optional[Baustoff] = None` – Der Stahl der massgebenden Lage -- seine Grenze, sein `E_s` und seine Fliessdehnung gelten. Mit verschiedenen Staehlen unten und oben ist massgebend die gezogene Lage mit dem kleinsten Erfuellungsgrad, nicht die am staerksten gedehnte.
- `erfuellungsgrad: float = 0.0`
- `erfuellt: bool = False`
- `konvergiert: bool = True`
- `vergleich: Optional[Vergleich] = None` – Fehlt nur, wenn sich keine Gleichgewichtslage fand.
- `begruendung: str = ''`
- `hinweis: str = ''`

#### Fallergebnis.fliesst

```python
@property
def fliesst(self) -> bool
```

Ob die am staerksten gedehnte Lage auf dem Plateau liegt.

### Spannungsgrenze

```python
class Spannungsgrenze(ABC)
```

Wogegen ein Stahlspannungsnachweis haelt -- und alles, was nur dazugehoert.

Die Zahl, die Eingaben, aus denen sie entsteht, und die Absaetze, die sie
begruenden. Dazu die Woerter, unter denen der Nachweis ueberall erscheint:
Wert-ID, Symbol, Tabellenzeile, Ueberschrift. Zwei Grenzen mit gleichem
`langname` stuenden als zwei ununterscheidbare Zeilen in derselben
Tabelle.

Die Absaetze sind **nicht** zu einem Text mit Platzhaltern
zusammenzulegen: der eine argumentiert fuer `f_yd`, der andere fuer
`f_yk`. Ein Text, der beides behauptet, behauptet nichts.

- `idteil: str` – Teil der Wert-ID: `<querschnitt>.nachweis.<idteil>.<richtung>`.
- `symbolteil: str` – Index am Erfuellungsgrad.
- `art: str` – Kurzzeichen im Urteil.
- `langname: str` – Spalte «Nachweis» der Zusammenfassung.
- `thema: str` – Thema in der Formelsammlung, und wovon der Erfuellungsgrad spricht.
- `einwirkung: str` – «häufiger» / «quasi-ständiger» -- im Titel.
- `lastindex: str` – Index an M_Ed und N_Ed in der Herleitung.
- `fallwort: str` – Ueberschrift je Fall.
- `referenz: str`
- `einleitung: str` – Der erste Satz der Herleitung: wozu der Nachweis da ist.

#### Spannungsgrenze.id

```python
@property
def id(self) -> str
```

Die Kennung des Nachweises, zu dem die Grenze gehoert.

#### Spannungsgrenze.je_stahl

```python
def je_stahl(self, name: str, symbol: str, stahl: Baustoff) -> Tuple[str, str]
```

Name und Zeichen eines Werts, der zu einem Stahl gehoert -- mit dem
Stahl daran, sobald die Richtung mehr als einen hat.

#### Spannungsgrenze.spannung

```python
def spannung(self, sigma_adm: float, stahl: Baustoff) -> Wert
```

`sigma_s,adm` als Wert -- in Herleitung, Vergleich und Tabelle derselbe.

#### Spannungsgrenze.gilt_bei

```python
@classmethod
def gilt_bei(cls, anforderung: str) -> bool
```

Ob der Nachweis bei dieser Rissanforderung verlangt ist.

#### Spannungsgrenze.bezuege

```python
@abstractmethod
def bezuege(self) -> List[Eingabebezug]
```

Was nur diese Grenze braucht, zusaetzlich zur gemeinsamen Rechnung.

#### Spannungsgrenze.bestimmen

```python
@abstractmethod
def bestimmen(self, e: Eingaben, p: Protokoll) -> Dict[str, float]
```

Die zulaessige Stahlspannung in Pa, je Stahl unter seiner Kennung --
gerechnet und mitgeschrieben.

#### Spannungsgrenze.festlegung

```python
@classmethod
@abstractmethod
def festlegung(cls, p: Protokoll) -> None
```

Welche Werte die Grenze ansetzt, und warum -- ohne Platte, nur der Absatz.

### GrenzeGegenFliessen

```python
class GrenzeGegenFliessen(Spannungsgrenze)
```

`f_yd - 80 N/mm²` unter haeufiger Einwirkung -- das Fliessen verhindern.

Nur bei erhoehter und hoher Anforderung -- bei normaler steht in
Tabelle 17 ein Strich. Das sagt [[opencivil.nachweis.spannungsbegrenzung#GrenzeGegenFliessen.gilt_bei|gilt_bei]]; der Aufbau fragt, und
der Katalog der Oberflaeche auch.

- `idteil = 'spannung'`
- `symbolteil = '\\sigma'`
- `art = 'σ_s'`
- `langname = 'Risse: Häufige Lastfälle'`
- `thema = 'Stahlspannung gegen Fliessen'`
- `einwirkung = 'häufiger'`
- `lastindex = 'häufig'`
- `fallwort = 'Häufiger Lastfall'`
- `referenz = 'SIA 262:2025, Tabelle 17'`
- `einleitung = 'Unter häufiger Einwirkung darf die Bewehrung nicht fliessen – sonst …`

#### GrenzeGegenFliessen.gilt_bei

```python
@classmethod
def gilt_bei(cls, anforderung: str) -> bool
```

#### GrenzeGegenFliessen.bezuege

```python
def bezuege(self) -> List[Eingabebezug]
```

#### GrenzeGegenFliessen.bestimmen

```python
def bestimmen(self, e: Eingaben, p: Protokoll) -> Dict[str, float]
```

#### GrenzeGegenFliessen.festlegung

```python
@classmethod
def festlegung(cls, p: Protokoll) -> None
```

### GrenzeAusRissbreite

```python
class GrenzeAusRissbreite(Spannungsgrenze)
```

`sigma_s,adm` aus der Rissanforderung, unter quasi-staendiger Einwirkung.

Dieselbe zulaessige Spannung wie bei der Zwaengung -- dieselbe Funktion,
[[opencivil.nachweis.spannungsbegrenzung#GrenzeAusRissbreite|mindestbewehrung.zulaessige_stahlspannung]], und keine zweite
Fassung davon. Bei normaler Anforderung `f_yk`: die Bewehrung darf
unter Dauerlast nicht fliessen. Bei erhoehter und hoher zusaetzlich die
Wurzelformel mit `w_nom`.

**Massgebend ist der dickste Stab der Tragrichtung.** Anders als bei der
Rissnormalkraft, wo je Lage ein Urteil faellt und die Grenze zu *dieser*
Lage gehoert: hier kommt sigma_s aus dem Faserintegral ueber den ganzen
Querschnitt, und welche Lage die groesste Zugspannung traegt, wechselt mit
dem Lastfall -- bei einem Feldmoment die untere, bei einem Stuetzmoment
die obere. Der dickste Stab gibt die kleinste zulaessige Spannung; das
liegt fuer jede der beiden auf der sicheren Seite.

- `idteil = 'spannung_riss'`
- `symbolteil = '\\sigma,w'`
- `art = 'σ_s,w'`
- `langname = 'Risse: Quasi-ständige Lastfälle'`
- `thema = 'Stahlspannung aus Rissbreite'`
- `einwirkung = 'quasi-ständiger'`
- `lastindex = '\\text{quasi-ständig}'`
- `fallwort = 'Quasi-ständiger Lastfall'`
- `referenz = 'SIA 262:2025, 4.4.2'`
- `einleitung = 'Unter quasi-ständiger Einwirkung begrenzt die Stahlspannung die Riss…`

#### GrenzeAusRissbreite.bezuege

```python
def bezuege(self) -> List[Eingabebezug]
```

#### GrenzeAusRissbreite.bestimmen

```python
def bestimmen(self, e: Eingaben, p: Protokoll) -> Dict[str, float]
```

#### GrenzeAusRissbreite.festlegung

```python
@classmethod
def festlegung(cls, p: Protokoll) -> None
```

### protokoll_festlegungen

```python
def protokoll_festlegungen(p: Protokoll, wahl: Rechenwahl) -> None
```

Die ersten beiden der drei Festlegungen hinter jeder Stahlspannung:
Kriechen und Werkstoffgesetze. Die dritte, die Grenze, schreibt danach
die Grenze selbst ([[opencivil.nachweis.spannungsbegrenzung#Spannungsgrenze.festlegung|Spannungsgrenze.festlegung]]). Fuer die Platte
und den gezeichneten Querschnitt dieselben Absaetze.

### Spannungsbegrenzung

```python
class Spannungsbegrenzung(Nachweis)
```

Stahlspannung unter Gebrauchslast, je Tragrichtung, gegen eine Grenze.

Ein Urteil je Lastfall. Gerechnet wird am gerissenen Querschnitt, womit,
sagt `wahl`; wogegen gehalten wird, sagt `grenze`.

#### Spannungsbegrenzung.thema

```python
@property
def thema(self) -> str
```

Je Grenze eines: gegen Fliessen oder aus der Rissbreite.

#### Spannungsbegrenzung.langname

```python
@property
def langname(self) -> str
```

#### Spannungsbegrenzung.pruefe

```python
def pruefe(self, e: Eingaben, p: Protokoll)
```

#### Spannungsbegrenzung._vergleich

```python
def _vergleich(self, erg: Fallergebnis) -> Vergleich
```

Spannungen oder Dehnungen -- die eine Stelle, die das entscheidet.

#### Spannungsbegrenzung._urteil

```python
def _urteil(self, erg: Fallergebnis, *, still: bool=False) -> NachweisUrteil
```

Das Urteil eines Falls -- was gegeneinander steht, sagt der Vergleich.

#### Spannungsbegrenzung._protokoll_ansatz

```python
def _protokoll_ansatz(self, p: Protokoll, e: Eingaben, w: Betonkennwerte, loeser: Querschnittsloeser) -> Dict[str, float]
```

Was fuer alle Faelle gilt -- und die Grenzen, die dabei entstehen.

#### Spannungsbegrenzung._wertigkeiten

```python
def _wertigkeiten(self, w: Betonkennwerte, loeser: Querschnittsloeser) -> str
```

`n = E_s / E_c,eff` hinter dem wirksamen Modul -- einmal, solange
alle Staehle denselben Modul haben, sonst je Stahl.

#### Spannungsbegrenzung._protokoll_fliessen

```python
def _protokoll_fliessen(self, p: Protokoll, e: Eingaben, erg: Fallergebnis, werte: Zwischenwerte, wirkt: Wert, grenze: Wert) -> None
```

Der Fall, in dem die Spannung am Plateau stehen bleibt.


## Konstanten

- `FLIESSABSTAND = 80000000.0` – Abstand zur Bemessungsfliessgrenze, in Pa. SIA 262:2025, Tabelle 17.
- `_GEFORDERT = ('erhoeht', 'hoch')` – Anforderungen, bei denen der Nachweis gegen Fliessen gefuehrt wird. Bei *normal* steht in der Tabelle ein Strich. Von aussen fragt man [[opencivil.nachweis.spannungsbegrenzung#GrenzeGegenFliessen.gilt_bei|GrenzeGegenFliessen.gilt_bei]] -- die Liste gehoert der Grenze.
- `VORGABE = Rechenwahl(satz=Werkstoffsatz.CHARAKTERISTISCH, art=Rechenart.ELASTIS…` – Womit die Stahlspannungen rechnen, wenn das Kapitel nichts anderes waehlt: elastisch, mit charakteristischen Werten -- ein Gebrauchsnachweis fragt, was der Querschnitt tut, nicht was er darf.
- `VERGLEICH_BEIM_FLIESSEN = 'Fliesst die Bewehrung, bleibt ihre Spannung am Plateau stehen, währe…` – Was verglichen wird, wenn die Bewehrung fliesst -- siehe Dateikopf.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.material.basis]]
- [[opencivil.material.betonstahl]]
- [[opencivil.nachweis.mindestbewehrung]]
- [[opencivil.nachweis.querschnittsloeser]]
- [[opencivil.nachweis.rechenwahl]]
- [[opencivil.nachweis.zustand2]]
- [[opencivil.querschnitt.platte]]

## Gebraucht von

- [[opencivil.nachweis.qa_gebrauch]]
- [[opencivil.nachweis.stabgrenzen]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.web.api]]

## Formeln aus diesem Modul

- [[Fliessdehnung]] · `Spannungsbegrenzung._protokoll_fliessen`
- [[Zulässige Dehnung]] · `Spannungsbegrenzung._protokoll_fliessen`
- [[Zulässige Stahlspannung]] · `GrenzeGegenFliessen.bestimmen`
