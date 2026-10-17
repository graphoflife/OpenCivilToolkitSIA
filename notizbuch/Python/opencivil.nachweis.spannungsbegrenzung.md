---
erzeugt: e643c3360c8f
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
der Herleitung. Die drei gehoeren zusammen und stehen darum in einer Klasse,
die dem Nachweis mitgegeben wird
([[opencivil.nachweis.spannungsgrenzen#Spannungsgrenze|Spannungsgrenze]], mit den
Stellen in ihrem eigenen Modul). Zwei Klassen mit kopiertem Kern waeren genau
die Fehlerklasse, vor der `zustand2.py` warnt: zwei Nachweise, die fuer
denselben Querschnitt verschiedene sigma_s melden.


## EINE KLASSE, ZWEI GEOMETRIEN

Dasselbe gilt fuer die Platte und den gezeichneten Querschnitt. Gemessen
wird an **Stellen** -- bei der Platte an ihren Lagen, beim gezeichneten
Querschnitt an jedem Stab --, und was der Nachweis von der Geometrie wissen
muss, sagt ihm ein schmaler Anschluss ([[opencivil.nachweis.spannungsbegrenzung#Stahlspannungsort|Stahlspannungsort]]): die
Ebene je Fall, die Stellen, die Grenze aus der Rissbreite und die Absaetze,
die nur die Geometrie schreiben kann. Welche Stelle massgebend ist, wie
verglichen und geurteilt wird, steht einmal, hier. Bis 2026-10-17 stand der
gezeichnete Querschnitt in einer Abschrift dieser Klasse daneben, mit
kopiertem Urteil und kopiertem Vergleich.


## WIE DIE SPANNUNG ENTSTEHT

Ueber [[opencivil.nachweis.querschnittsloeser]]: gesucht wird die
Dehnungsebene, die `M_Ed` und `N_Ed` des Lastfalls im Gleichgewicht
haelt -- am gezeichneten Querschnitt mit gedrehter Nulllinie
([[opencivil.nachweis.gebrauchsebene]]). Der Beton nimmt keinen Zug auf.
Womit gerechnet wird, waehlt das Kapitel
([[opencivil.querschnitt.gesetzwahl#Rechenwahl|Rechenwahl]]): die Kriechzahl, den
Wertesatz und die Rechenart. Die Vorgabe ist, wie bis 2026-10-09 fest:
**elastisch** -- der Beton im Druck linear mit dem wirksamen Modul
`E_cm/(1+phi)` -- mit den **charakteristischen** Festigkeiten: der Stahl
fliesst bei `f_yk`, der Beton traegt hoechstens `f_ck`.

Die gedrueckte Bewehrung wirkt mit, wie im Querschnitt -- nur in der
Rechenart «Handrechnung» nicht. Gemessen wird an der am staerksten
gezogenen Stelle. (Bis 2026-10-09 stand hier, nur gezogene Bewehrung zaehle;
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

Eine Schnittgroessenkombination unter Gebrauchslast -- an der Platte.

Haeufig oder quasi-staendig -- das sagt nicht der Fall, sondern der
Nachweis, dem er mitgegeben wird. Der gezeichnete Querschnitt nimmt
seinen [[opencivil.querschnitt.analyse#Lastfall|Lastfall]].

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

### protokoll_festlegungen

```python
def protokoll_festlegungen(p: Protokoll, wahl: Rechenwahl) -> None
```

Die ersten beiden der drei Festlegungen hinter jeder Stahlspannung:
Kriechen und Werkstoffgesetze. Die dritte, die Grenze, schreibt danach
die Grenze selbst ([[opencivil.nachweis.spannungsgrenzen#Spannungsgrenze.festlegung|Spannungsgrenze.festlegung]]). Fuer die Platte
und den gezeichneten Querschnitt dieselben Absaetze.

### Stahlebene

```python
class Stahlebene(Protocol)
```

Was der Nachweis von der Ebene eines Falls liest -- je Stelle Dehnung und Spannung.

- `konvergiert: bool`
- `verfehlt: bool`
- `eps_s: Tuple[float, ...]`
- `sigma_s: Tuple[float, ...]`

### Stahlspannungsort

```python
class Stahlspannungsort(ABC)
```

Was [[opencivil.nachweis.spannungsbegrenzung#Spannungsbegrenzung|Spannungsbegrenzung]] von seiner Geometrie wissen muss -- und
nicht mehr: die Platte je Tragrichtung ([[opencivil.nachweis.spannungsbegrenzung#PlattenStellen|PlattenStellen]]), der
gezeichnete Querschnitt
([[opencivil.nachweis.qa_gebrauch#AnalyseStellen|AnalyseStellen]]).

Je Rechnung bereitet der Ort seinen Zustand vor ([[opencivil.nachweis.spannungsbegrenzung#Stahlspannungsort.zustand|zustand]]): die
Stellen, an denen gemessen wird, und was er sonst braucht. Je Fall findet
er die Ebene ([[opencivil.nachweis.spannungsbegrenzung#Stahlspannungsort.ebene|ebene]]). Die Grenze aus der Rissbreite gehoert ihm
([[opencivil.nachweis.spannungsbegrenzung#Stahlspannungsort.aus_rissbreite|aus_rissbreite]]), und die Absaetze, die nur er schreiben kann.

Was in Kennungen, Zeichen und Titeln anders heisst, sagen die Woerter
unten -- so blieben Bericht und Kennungen beider Geometrien, wie sie vor
der Zusammenlegung waren (2026-10-17).

- `name: str`
- `abschnitt: Abschnitt`
- `richtung: Optional[Richtung] = None` – Die Tragrichtung, wo es eine gibt -- sie steht im Namen jedes Urteils.
- `zeichen: str = ''` – Im Index des Erfuellungsgrads nach der Grenze -- bei der Platte «,x».
- `beschriftung: str = ''` – Im Titel des Nachweises nach «Einwirkung» -- bei der Platte « in x-Richtung».
- `titelzusatz: str = ''` – Im Titel der Herleitung -- bei der Platte « – in x-Richtung».
- `stahlindex: str = 's'` – Der Index an ε_s und σ_s -- bei der Platte «{s,x}».
- `messung: str = ''` – Woran gemessen wird: der zweite Satz der Herleitung.
- `regel_der_rissbreite: str = ''` – Mit welchem Durchmesser die Grenze aus der Rissbreite gilt, als Satz.

#### Stahlspannungsort.basis

```python
@abstractmethod
def basis(self, grenze: Type[Spannungsgrenze]) -> str
```

Die Kennung des Nachweises mit dieser Grenze.

#### Stahlspannungsort.bezuege

```python
@abstractmethod
def bezuege(self, wahl: Rechenwahl) -> List[Eingabebezug]
```

Was die Rechnung liest, mit jeder Grenze.

#### Stahlspannungsort.stahlbezuege

```python
def stahlbezuege(self, kennwerte: Sequence[str]) -> List[Eingabebezug]
```

Diese Kennwerte je Stahl -- wo sie nicht schon in [[opencivil.nachweis.spannungsbegrenzung#Stahlspannungsort.bezuege|bezuege]] stehen.

#### Stahlspannungsort.rissbreitenbezuege

```python
def rissbreitenbezuege(self) -> List[Eingabebezug]
```

Was die Grenze aus der Rissbreite liest, ueber [[opencivil.nachweis.spannungsbegrenzung#Stahlspannungsort.bezuege|bezuege]] hinaus.

#### Stahlspannungsort.zustand

```python
@abstractmethod
def zustand(self, e: Eingaben, wahl: Rechenwahl) -> Stahlzustand
```

Was eine Rechnung braucht, aus ihren Eingaben.

#### Stahlspannungsort.aus_rissbreite

```python
@abstractmethod
def aus_rissbreite(self, zustand: Stahlzustand, e: Eingaben, p: Protokoll, anforderung: Rissanforderung, basis: str) -> Grenzen
```

`sigma_s,adm` jeder Stelle aus der Rissbreite -- gerechnet und hergeleitet.

#### Stahlspannungsort.ebene

```python
@abstractmethod
def ebene(self, zustand: Stahlzustand, fall) -> Stahlebene
```

Die Dehnungsebene, die den Fall traegt -- auch eine ohne Gleichgewicht.

#### Stahlspannungsort.keine_ebene

```python
@abstractmethod
def keine_ebene(self, fall) -> str
```

Was dasteht, wo sich zum Fall keine Ebene findet.

#### Stahlspannungsort.begruendung

```python
@abstractmethod
def begruendung(self, zustand: Stahlzustand, erg: 'Fallergebnis') -> str
```

Die Begruendung des Urteils -- mit dem Satz des Vergleichs.

#### Stahlspannungsort.dehnungsgrenze

```python
@abstractmethod
def dehnungsgrenze(self, basis: str, werte: Zwischenwerte, erg: 'Fallergebnis') -> Wert
```

`eps_s,adm` als Wert, fuer den Vergleich, wenn der Stahl fliesst.

#### Stahlspannungsort.protokoll_vor_den_grenzen

```python
def protokoll_vor_den_grenzen(self, p: Protokoll, e: Eingaben, zustand: Stahlzustand, wahl: Rechenwahl, phi: Wert, basis: str) -> None
```

Was vor der Grenze steht -- bei der Platte der wirksame Modul.

#### Stahlspannungsort.protokoll_gesetze

```python
@abstractmethod
def protokoll_gesetze(self, p: Protokoll, e: Eingaben, zustand: Stahlzustand, wahl: Rechenwahl, basis: str) -> None
```

Die Werkstoffgesetze, wie gerechnet wird.

#### Stahlspannungsort.protokoll_verfahren

```python
@abstractmethod
def protokoll_verfahren(self, p: Protokoll, zustand: Stahlzustand, wahl: Rechenwahl) -> None
```

Wie die Dehnungsebene gefunden wird.

#### Stahlspannungsort.protokoll_einwirkung

```python
@abstractmethod
def protokoll_einwirkung(self, p: Protokoll, fall, index: str) -> None
```

Die Schnittgroessen des Falls.

#### Stahlspannungsort.protokoll_ebene

```python
@abstractmethod
def protokoll_ebene(self, p: Protokoll, werte: Zwischenwerte, zustand: Stahlzustand, grenzen: Grenzen, erg: 'Fallergebnis') -> None
```

Die gefundene Ebene, ihre Probe und was der Ort dazu sagt.

### Fallergebnis

```python
@dataclass
class Fallergebnis
```

Was der Nachweis fuer einen Lastfall gefunden hat.

- `fall: object` – Bei der Platte ein [[opencivil.nachweis.spannungsbegrenzung#Gebrauchsfall|Gebrauchsfall]], am gezeichneten Querschnitt ein Lastfall.
- `ebene: Optional[Stahlebene] = None` – Die Ebene, die der Ort fand -- fehlt nur ohne Bewehrung.
- `stelle: int = 0` – Die massgebende Stelle: die gezogene mit dem kleinsten Erfuellungsgrad.
- `eps_s: float = 0.0` – Ihre Dehnung -- die groesste Zugdehnung, wo nur ein Stahl liegt.
- `sigma_s: float = 0.0` – Die Spannung dazu, in Pa -- auf dem Plateau `f_yk`.
- `E_s: float = 0.0`
- `sigma_s_adm: float = 0.0`
- `eps_s_adm: float = 0.0` – `sigma_s_adm / E_s` -- dagegen wird gemessen, wenn der Stahl fliesst.
- `eps_y: float = 0.0` – Die Fliessdehnung `f_s / E_s`.
- `stahl: Optional[Baustoff] = None` – Der Stahl der massgebenden Stelle -- seine Grenze, sein `E_s` und seine Fliessdehnung gelten. Mit verschiedenen Staehlen ist massgebend die gezogene Stelle mit dem kleinsten Erfuellungsgrad, nicht die am staerksten gedehnte.
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

Ob die massgebende Stelle auf dem Plateau liegt.

### _Plattenzustand

```python
@dataclass(frozen=True)
class _Plattenzustand(Stahlzustand)
```

Dazu der Loeser der Tragrichtung und die Kennwerte des Betons.

- `loeser: Querschnittsloeser`
- `w: Betonkennwerte`

### PlattenStellen

```python
class PlattenStellen(Stahlspannungsort)
```

Die Platte in einer Tragrichtung: Stellen sind ihre Lagen -- in der
Handrechnung je Seite eine. Die Grenze aus der Rissbreite gilt mit dem
dicksten Stab der Tragrichtung, fuer jede Lage dieselbe.

**Massgebend ist der dickste Stab der Tragrichtung.** Anders als bei der
Rissnormalkraft, wo je Lage ein Urteil faellt und die Grenze zu *dieser*
Lage gehoert: hier kommt sigma_s aus dem Faserintegral ueber den ganzen
Querschnitt, und welche Lage die groesste Zugspannung traegt, wechselt mit
dem Lastfall -- bei einem Feldmoment die untere, bei einem Stuetzmoment
die obere. Der dickste Stab gibt die kleinste zulaessige Spannung; das
liegt fuer jede der beiden auf der sicheren Seite.

- `regel_der_rissbreite = 'Massgebend ist der dickste Stab der Tragrichtung. Welche Lage die gr…`

#### PlattenStellen.basis

```python
def basis(self, grenze: Type[Spannungsgrenze]) -> str
```

#### PlattenStellen.bezuege

```python
def bezuege(self, wahl: Rechenwahl) -> List[Eingabebezug]
```

#### PlattenStellen.stahlbezuege

```python
def stahlbezuege(self, kennwerte: Sequence[str]) -> List[Eingabebezug]
```

#### PlattenStellen.rissbreitenbezuege

```python
def rissbreitenbezuege(self) -> List[Eingabebezug]
```

#### PlattenStellen.zustand

```python
def zustand(self, e: Eingaben, wahl: Rechenwahl) -> _Plattenzustand
```

#### PlattenStellen.aus_rissbreite

```python
def aus_rissbreite(self, zustand: Stahlzustand, e: Eingaben, p: Protokoll, anforderung: Rissanforderung, basis: str) -> Grenzen
```

#### PlattenStellen.ebene

```python
def ebene(self, zustand: _Plattenzustand, fall: Gebrauchsfall) -> Ebene
```

#### PlattenStellen.keine_ebene

```python
def keine_ebene(self, fall: Gebrauchsfall) -> str
```

#### PlattenStellen.begruendung

```python
def begruendung(self, zustand: Stahlzustand, erg: Fallergebnis) -> str
```

#### PlattenStellen.dehnungsgrenze

```python
def dehnungsgrenze(self, basis: str, werte: Zwischenwerte, erg: Fallergebnis) -> Wert
```

#### PlattenStellen.protokoll_vor_den_grenzen

```python
def protokoll_vor_den_grenzen(self, p: Protokoll, e: Eingaben, zustand: _Plattenzustand, wahl: Rechenwahl, phi: Wert, basis: str) -> None
```

#### PlattenStellen._wertigkeiten

```python
def _wertigkeiten(self, zustand: _Plattenzustand, wahl: Rechenwahl, basis: str) -> str
```

`n = E_s / E_c,eff` hinter dem wirksamen Modul -- einmal, solange
alle Staehle denselben Modul haben, sonst je Stahl.

#### PlattenStellen.protokoll_gesetze

```python
def protokoll_gesetze(self, p: Protokoll, e: Eingaben, zustand: Stahlzustand, wahl: Rechenwahl, basis: str) -> None
```

#### PlattenStellen.protokoll_verfahren

```python
def protokoll_verfahren(self, p: Protokoll, zustand: _Plattenzustand, wahl: Rechenwahl) -> None
```

#### PlattenStellen.protokoll_einwirkung

```python
def protokoll_einwirkung(self, p: Protokoll, fall: Gebrauchsfall, index: str) -> None
```

#### PlattenStellen.protokoll_ebene

```python
def protokoll_ebene(self, p: Protokoll, werte: Zwischenwerte, zustand: Stahlzustand, grenzen: Grenzen, erg: Fallergebnis) -> None
```

### Spannungsbegrenzung

```python
class Spannungsbegrenzung(Nachweis)
```

Stahlspannung unter Gebrauchslast gegen eine Grenze -- an der Platte je
Tragrichtung, am gezeichneten Querschnitt; wo, sagt `ort`.

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
def _vergleich(self, erg: Fallergebnis, grenzen: Grenzen) -> Vergleich
```

Spannungen oder Dehnungen -- die eine Stelle, die das entscheidet.

#### Spannungsbegrenzung._urteil

```python
def _urteil(self, erg: Fallergebnis, *, still: bool=False) -> NachweisUrteil
```

Das Urteil eines Falls -- was gegeneinander steht, sagt der Vergleich.

#### Spannungsbegrenzung._protokoll_ansatz

```python
def _protokoll_ansatz(self, p: Protokoll, e: Eingaben, zustand: Stahlzustand) -> Grenzen
```

Was fuer alle Faelle gilt -- und die Grenzen, die dabei entstehen.

#### Spannungsbegrenzung._protokoll_fliessen

```python
def _protokoll_fliessen(self, p: Protokoll, e: Eingaben, erg: Fallergebnis, grenzen: Grenzen, werte: Zwischenwerte, wirkt: Wert, grenze: Wert) -> None
```

Der Fall, in dem die Spannung am Plateau stehen bleibt.


## Konstanten

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
- [[opencivil.nachweis.rissanforderung]]
- [[opencivil.nachweis.spannungsgrenzen]]
- [[opencivil.nachweis.zustand2]]
- [[opencivil.querschnitt.gesetzwahl]]
- [[opencivil.querschnitt.platte]]

## Gebraucht von

- [[opencivil.nachweis.qa_gebrauch]]
- [[opencivil.nachweis.spannungsgrenzen]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.aufbau.platte]]

## Formeln aus diesem Modul

- [[Fliessdehnung]] · `Spannungsbegrenzung._protokoll_fliessen`
- [[Zulässige Dehnung]] · `Spannungsbegrenzung._protokoll_fliessen`
