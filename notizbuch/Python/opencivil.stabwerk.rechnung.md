---
erzeugt: 2f83d646498b
art: modul
tags: [modul]
---
> [!abstract] opencivil/stabwerk/rechnung.py
> das Balkensystem im Rechenwerk.
> Paket [[opencivil.stabwerk]] · [Quelltext](../../opencivil/stabwerk/rechnung.py)

## VERANTWORTUNG

Was ein Balkensystem im Rechenwerk anmeldet: je Querschnitt die Flaeche
`A` und das Traegheitsmoment `I`, je Paar aus Querschnitt und Material
die Dehn- und die Biegesteifigkeit `EA` und `EI`, und eine Prozedur, die
das System nach der Steifigkeitsmethode rechnet
([[opencivil.stabwerk.system|system]]) und ihre Herleitung schreibt
([[opencivil.stabwerk.herleitung|herleitung]]).


## EBEN UND IM RAUM

Das 3D-Balkensystem ([[opencivil.stabwerk3d.rechnung]]) tut dasselbe mit
mehr Kennwerten und Steifigkeiten -- `I_y`, `I_z` und `I_T`, `EI_y`,
`EI_z` und `GI_T` -- und rechnet im Raum. Was beide gleich tun, steht in
[[opencivil.stabwerk.rechnung#Stabwerksrechnung|Stabwerksrechnung]]: welche Kennwerte, Steifigkeiten und
Materialkennwerte, sagt je System eine Liste, ob eben oder im Raum seine
Art ([[opencivil.stabwerk.art#Konstanten|EBENE]],
[[opencivil.stabwerk.art#Konstanten|RAUM]]) -- gerechnet wird mit demselben
Kern --, wie es sein Eigengewicht ansetzt und seine Herleitung schreibt,
eine Methode.


## WOHER A UND I KOMMEN

sagt jeder Querschnitt selbst ([[opencivil.stabwerk.stabquerschnitt|stabquerschnitt]]):
nach Vorlage, von Hand, aus einer Platte oder aus einer
Querschnittsanalyse.


## MATERIALIEN

Ein Material der Staebe ([[opencivil.stabwerk.rechnung#Stabmaterial|Stabmaterial]]) ist ein Beton oder Baustahl
des Projekts oder ein eigenes mit E und Dichte von Hand (Benutzer,
2026-10-24). Ein Stab
kann auch das Material seines Querschnitts nehmen, den Beton einer Platte
oder Querschnittsanalyse.


## STEIFIGKEIT -- NACH VORGABE, NICHT NACHGESCHLAGEN

`E_cm` eines Betons, `E_a` eines Baustahls ([[opencivil.stabwerk.rechnung#Konstanten|E_MODUL]]) oder
E von Hand -- und bei
einem Stab mit dem Material seiner Querschnittsanalyse auf Wunsch deren
E_eq bei N und M (Benutzer, 2026-10-23) --, am ungerissenen
Bruttoquerschnitt, ohne Schubverformung, Gleichgewicht am unverformten
System. Die Herleitung sagt es, das TODO fuehrt es. Findet die Suche nach
E_eq keinen Modul, sagt es eine Meldung, und das System rechnet nicht.


## EIGENGEWICHT -- NACH VORGABE DES BENUTZERS (2026-10-23)

Je Paar aus Querschnitt und Material `g_k = rho · g · A` in kN/m, mit
`g = 10 m/s²` und beim Beton der Dichte des Stahlbetons -- ohne den Stahl
noch dazu --, beim Baustahl mit `rho_a`. Es kommt als Last senkrecht je Meter Stab in den Lastfall, den
die Beschreibung dafuer nennt.


## DAS ERGEBNIS

kommt als Befund in die Loesung ([[opencivil.stabwerk.rechnung#Systembefund|Systembefund]]); Zusammenfassung,
Bilder und Zwischenspeicher lesen es dort. Einen Wert liefert die Prozedur
nicht: sie ist Ziel unter ihrer ID. Ein bewegliches System ist ein Ergebnis
mit Meldung und keine Ausnahme: der Rest des Projekts rechnet weiter.

## Inhalt

### Materialkennwert

```python
@dataclass(frozen=True)
class Materialkennwert
```

Ein Kennwert, den ein Stab von seinem Material nimmt: je Art des
Baustoffs, welcher es ist, und wie er bei einem eigenen Material von
Hand heisst -- `kurzname` ist auch sein Feld dort.

- `kurzname: str`
- `symbol: str`
- `einheit: Einheit`
- `beschreibung: str`
- `je_stoff: Mapping[Baustoffart, str]`

### _traegheit

```python
def _traegheit(si: float) -> str
```

Ein Traegheitsmoment in Worten: «1.06·10⁶ mm⁴».

### stoffkennwerte

```python
def stoffkennwerte(kennwerte: Sequence[Materialkennwert]) -> Dict[Baustoffart, Dict[str, str]]
```

Je Art des Baustoffs, welche seiner Kennwerte ein Stab nimmt: `{BETON: {"E": "E_cm"}}`.

### Steifigkeitsformel

```python
@dataclass(frozen=True)
class Steifigkeitsformel
```

Eine Steifigkeit eines Stabs: ein Modul seines Materials mal ein
Kennwert seines Querschnitts. `kurzname` heisst auch das Feld des
Stabs im Rechenkern, `beschreibung` auch die Formel.

- `kurzname: str`
- `einheit: Einheit`
- `beschreibung: str`
- `modul: str` – `E` oder `G` -- ein [[opencivil.stabwerk.rechnung#Materialkennwert|Materialkennwert]].
- `kennwert: str` – Ein Kennwert des Querschnitts: `A`, `I`, `I_T` ...

### Stabmaterial

```python
@dataclass(frozen=True)
class Stabmaterial
```

Ein Material der Staebe, aufgeloest: ein Beton oder Baustahl -- seine
Kennwerte von ihm -- oder ein eigenes mit Kennwerten von Hand.

- `kennung: str` – Im System, `M1` -- bei einem Stab mit dem Material seines Querschnitts dessen Zeichen.
- `name: str`
- `stoff: Optional[Baustoff] = None` – Der Beton oder Baustahl -- `None` bei einem eigenen Material.
- `werte: Mapping[str, float] = field(default_factory=dict)` – Von Hand, je [[opencivil.stabwerk.rechnung#Materialkennwert|Materialkennwert]] in seiner Einheit -- nur ohne `stoff`.
- `vom_querschnitt: bool = False` – Das Material des Querschnitts: dann gilt dessen E_eq, wenn er eines hat.

### Steifigkeit

```python
@dataclass(frozen=True)
class Steifigkeit
```

Ein Paar aus Querschnitt und Material und die Wert-IDs seiner Steifigkeiten.

- `querschnitt: str`
- `material: str` – Die Kennung des [[opencivil.stabwerk.rechnung#Stabmaterial|Stabmaterial]].
- `werte: Mapping[str, str]` – Je [[opencivil.stabwerk.rechnung#Steifigkeitsformel|Steifigkeitsformel]] die Wert-ID: `{"EA": ..., "EI": ...}`.
- `g_k: str = ''` – Das Eigengewicht je Meter -- leer, wenn kein Lastfall es bekommt.
- `mit_eq: bool = False` – Ob E das E_eq des Querschnitts ist -- dann fehlen die Steifigkeiten, wo die Suche keines fand.

### Lagerkraft

```python
@dataclass(frozen=True)
class Lagerkraft
```

Eine Zeile der Lagerkraefte eines Falls, auf das Tragwerk wirkend -- in
Herleitung und Bildschirm dieselbe.

- `wo: str` – «A1 (K1)», «L2 bei 1.500 m», «L2: Bettung, Summe».
- `werte: Tuple[float, ...]` – Wie der Rechenkern sie gibt: `(R_x, R_z, M)` in der Ebene, sechs im Raum -- in N und Nm.
- `knoten: str = ''` – Der Knoten, an dem sie angreift -- leer auf einem Stab und bei einer Summe.
- `summe: bool = False` – Die Summe ueber einen Stab, mit dem Moment um den Ursprung (siehe `SUMMEN`).

### Systembefund

```python
@dataclass
class Systembefund
```

Was die Steifigkeitsmethode im Lauf fand: das System mit seinen
Steifigkeiten, wie es gerechnet wurde, und sein Ergebnis -- Meldungen,
Faelle mit Verschiebungen und Lagerkraeften, in SI. Die Verlaeufe eines
Falls rechnet [[opencivil.stabwerk.rechnung#Systembefund.verlaeufe|verlaeufe]] einmal, wenn jemand sie braucht.

- `gerechnet: System`
- `ergebnis: Ergebnis`
- `eigengewicht: Dict[str, float] = field(default_factory=dict)` – Je tragenden Stab sein Eigengewicht in N/m -- leer, wenn kein Lastfall es bekommt.
- `_verlaeufe: Dict[str, Dict[str, Stabverlauf]] = field(default_factory=dict, repr=False)`

#### Systembefund.verlaeufe

```python
def verlaeufe(self, fall: str) -> Dict[str, Stabverlauf]
```

Je Stab der Verlauf der Schnittgroessen und der Biegelinie in einem Fall -- einmal gerechnet.

#### Systembefund.lagerkraefte

```python
def lagerkraefte(self, fall: Fall) -> List[Lagerkraft]
```

Die Lagerkraefte eines Falls, Zeile fuer Zeile: die Lager an Knoten,
gehaltene Stellen auf Staeben und je Stab die Summe dessen, was ein
festes Linienlager und die Bettung aufnehmen. Zusammen halten sie den
Lasten das Gleichgewicht -- darum fehlt keine davon, weder in der
Herleitung noch am Bildschirm.

### SteifigkeitsmethodeProzedur

```python
class SteifigkeitsmethodeProzedur(Prozedur)
```

Das ganze System, gerechnet und aufgeschrieben.

- `THEMA = STEIFIGKEITSMETHODE`

#### SteifigkeitsmethodeProzedur.rechne

```python
def rechne(self, e: Eingaben, p: Protokoll) -> Ausfuehrung
```

### Stabwerksrechnung

```python
class Stabwerksrechnung(Rechenobjekt)
```

Ein Balkensystem, fertig fuer das Rechenwerk -- was die Ebene und der
Raum gleich tun, siehe Dateikopf. Je System sagen die Klassenattribute,
welche Kennwerte, Steifigkeiten und Materialkennwerte es hat und wie es
rechnet, und die Methoden `_eigenlast` und `_schreiben`, wie sein
Eigengewicht als Last aussieht und wie es seine Herleitung schreibt.

- `KENNWERTE: Tuple[Kennwert, ...]` – Was ein Querschnitt liefert ([[opencivil.stabwerk.stabquerschnitt|stabquerschnitt]]).
- `STEIFIGKEITEN: Tuple[Steifigkeitsformel, ...]`
- `MATERIALKENNWERTE: Tuple[Materialkennwert, ...]`
- `ART: Art` – Eben oder im Raum ([[opencivil.stabwerk.art|art]]).

#### Stabwerksrechnung.abschnitt

```python
def abschnitt(self, thema: str=STEIFIGKEITSMETHODE) -> Abschnitt
```

Ein Abschnitt fuer alles -- das Thema sagt nur, wo die Formeln gesammelt stehen.

#### Stabwerksrechnung.bezuege

```python
@property
def bezuege(self) -> List[str]
```

Die Platten und Analysen, deren Werte das System liest.

#### Stabwerksrechnung._kennwerte

```python
def _kennwerte(self, m: Stabmaterial) -> Dict[str, str]
```

Die Wert-IDs der [[opencivil.stabwerk.rechnung#Stabwerksrechnung|MATERIALKENNWERTE]] eines Materials: die
seines Baustoffs -- oder bei einem eigenen Vorgaben von Hand, einmal
je Material.

#### Stabwerksrechnung._erdbeschleunigung

```python
def _erdbeschleunigung(self) -> str
```

`g` als Vorgabe des Systems -- seine Wert-ID.

#### Stabwerksrechnung._steifigkeit

```python
def _steifigkeit(self, q: str, m: Stabmaterial, index: str, g: Optional[str]=None) -> Steifigkeit
```

Die [[opencivil.stabwerk.rechnung#Stabwerksrechnung|STEIFIGKEITEN]] eines Paars aus Querschnitt und Material --
mit `g` dazu sein Eigengewicht. Module und Dichte kommen vom
Material; nimmt der Stab das Material seines Querschnitts und hat der
ein E_eq, gilt dieses.

#### Stabwerksrechnung._eigengewicht

```python
def _eigengewicht(self, e: Eingaben) -> Dict[str, float]
```

Je tragenden Stab `g_k` in N/m -- es kommt senkrecht ueber seine
ganze Laenge in den Lastfall des Eigengewichts, je Meter Stab und
nicht je Meter Projektion. Leer ohne diesen Lastfall.

#### Stabwerksrechnung.baustoffe

```python
@property
def baustoffe(self) -> List[Baustoff]
```

Die Betone der Stäbe, jeder einmal -- eigene Materialien bringen ihre Werte selbst.

#### Stabwerksrechnung.ziele

```python
def ziele(self) -> List[str]
```

Was ein Lauf rechnen muss: jeder Querschnitt -- auch einer, den kein
Stab nimmt -- und das System. Von einem E_eq die Suche, nicht E: das
fehlt, wo sie keinen Modul fand.

#### Stabwerksrechnung.rechnen_und_schreiben

```python
def rechnen_und_schreiben(self, e: Eingaben, p: Protokoll) -> Ausfuehrung
```

Die Steifigkeiten in die Staebe, das System gerechnet, die Herleitung
geschrieben. Haelt eine Meldung der Beschreibung die Rechnung auf --
oder ein E_eq, das es nicht gibt --, bleibt es bei ihr.

#### Stabwerksrechnung._ohne_modul

```python
def _ohne_modul(self, e: Eingaben) -> List[Meldung]
```

Je Querschnitt, dessen Suche kein E_eq fand und den ein Stab mit
seinem Material nimmt, eine Meldung.

#### Stabwerksrechnung._keine_hauptachsen

```python
def _keine_hauptachsen(self, e: Eingaben) -> List[Meldung]
```

Je Querschnitt mit `I_yz`, den ein Stab nimmt und dessen y und z
merklich keine Hauptachsen sind ([[opencivil.stabwerk.stabquerschnitt#Konstanten|KOPPLUNG]]), ein Hinweis --
er haelt die Rechnung nicht auf.

#### Stabwerksrechnung._eigenlast

```python
def _eigenlast(self, stab: str, g: float) -> Any
```

Das Eigengewicht eines Stabs als Last seines Systems: senkrecht, `g` in N/m.

#### Stabwerksrechnung._schreiben

```python
def _schreiben(self, p: Protokoll, befund: Systembefund) -> None
```

Die Herleitung.

### Balkensystem

```python
class Balkensystem(Stabwerksrechnung)
```

Ein ebenes Balkensystem, fertig fuer das Rechenwerk.

- `WAS = 'Balkensystem'`
- `KENNWERTE = EBEN`
- `STEIFIGKEITEN = (DEHNSTEIFIGKEIT, Steifigkeitsformel('EI', KNM2, 'Biegesteifigkeit', …`
- `MATERIALKENNWERTE = (E_MODUL, DICHTE)`
- `ART = EBENE`

### _gewicht_je_meter

```python
def _gewicht_je_meter(rho: Groesse, g: Groesse, A: Groesse) -> Groesse
```

Das Eigengewicht eines Stabs je Meter: Dichte mal g mal Flaeche.

### _modul_mal_kennwert

```python
def _modul_mal_kennwert(**faktoren: Groesse) -> Groesse
```

Modul mal Kennwert ([[opencivil.stabwerk.rechnung#Steifigkeitsformel|Steifigkeitsformel]]).


## Konstanten

- `E_MODUL = Materialkennwert('E', 'E', N_PRO_MM2, 'E-Modul', {Baustoffart.BETON: …` – Beim Beton `E_cm` -- die Analyse rechnet in der Regel ungerissen (SIA 262:2025, 4.1.4.1.3), mit dem Mittelwert --, beim Baustahl `E_a`.
- `DICHTE = Materialkennwert('rho', '\\rho', KG_PRO_M3, 'Dichte', {Baustoffart.BE…` – Fuer das Eigengewicht: beim Beton die Dichte des Stahlbetons (Benutzer, 2026-10-23).
- `SCHUBMODUL = Materialkennwert('G', 'G', N_PRO_MM2, 'Schubmodul', {Baustoffart.BETO…` – Fuer die Torsion, nur im Raum: `G_cm` des Betons, `G_a` des Baustahls.
- `STABKENNWERTE = stoffkennwerte((E_MODUL, DICHTE))` – Welche Kennwerte eines Baustoffs ein Stab in der Ebene aus ihm nimmt.
- `ERDBESCHLEUNIGUNG = Groesse(10.0, M_PRO_S2)` – Die Erdbeschleunigung des Eigengewichts -- 10 m/s² nach Vorgabe des Benutzers (2026-10-23): so wiegt Stahlbeton 25 kN/m³.
- `QUERSCHNITTE = 'Stabquerschnitte'` – Die Themen der Formelsammlung: was am Querschnitt haengt, und die Rechnung.
- `STEIFIGKEITSMETHODE = 'Steifigkeitsmethode'`
- `DEHNSTEIFIGKEIT = Steifigkeitsformel('EA', MN, 'Dehnsteifigkeit', 'E', 'A')`

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.rechenobjekt]]
- [[opencivil.core.wert]]
- [[opencivil.material.basis]]
- [[opencivil.stabwerk.art]]
- [[opencivil.stabwerk.herleitung]]
- [[opencivil.stabwerk.modell]]
- [[opencivil.stabwerk.stabquerschnitt]]
- [[opencivil.stabwerk.system]]
- [[opencivil.stabwerk.verlauf]]

## Gebraucht von

- [[opencivil.decke.werk]]
- [[opencivil.ergebnis]]
- [[opencivil.projekt.aufbau.balkensystem]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.balkensystem]]
- [[opencivil.stabwerk.herleitung]]
- [[opencivil.stabwerk3d.herleitung]]
- [[opencivil.stabwerk3d.rechnung]]
- [[opencivil.web.api]]
- [[opencivil.web.balkendaten]]
- [[opencivil.web.systemkatalog]]

## Formeln aus diesem Modul

- [[Biegesteifigkeit]] · `_modul_mal_kennwert`
- [[Biegesteifigkeit um y]] · `_modul_mal_kennwert`
- [[Biegesteifigkeit um z]] · `_modul_mal_kennwert`
- [[Dehnsteifigkeit]] · `_modul_mal_kennwert`
- [[Eigengewicht eines Stabs]] · `_gewicht_je_meter`
- [[Torsionssteifigkeit]] · `_modul_mal_kennwert`
