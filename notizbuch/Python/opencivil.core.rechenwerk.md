---
erzeugt: 7029c201dbeb
art: modul
tags: [modul]
---
> [!abstract] opencivil/core/rechenwerk.py
> Registrierung und Aufloesung von Berechnungen.
> Paket [[opencivil.core]] · [Quelltext](../../opencivil/core/rechenwerk.py)

## VERANTWORTUNG

Das Rechenwerk kennt alle Berechnungen und alle vom Benutzer gesetzten Werte.
Es beantwortet die beiden Fragen, um die es in diesem Werkzeug geht:

**Rueckwaerts** -- "Ich will diesen Wert. Was ist dafuer noetig?"
[[opencivil.core.rechenwerk#Rechenwerk.loese|Rechenwerk.loese]] verfolgt das Ziel rueckwaerts durch den Graphen,
fuehrt genau die noetigen Berechnungen aus (und nur die) und meldet jede
Eingabe, die dafuer fehlt -- samt der Kette, ueber die sie gebraucht wird.

**Vorwaerts** -- "Was laesst sich mit dem, was ich habe, ueberhaupt rechnen?"
[[opencivil.core.rechenwerk#Rechenwerk.loese_alles|Rechenwerk.loese_alles]] berechnet alles Erreichbare und listet fuer
den Rest auf, woran es scheitert.

Ein Ziel ist ein Wert -- oder eine Berechnung unter ihrer ID. Dann laeuft
sie, auch wenn sie keine Ausgabe hat: ein Nachweis ohne Lastfall, ein
Balkensystem. Was sie findet, steht in ihrem Befund.


## AUFLOESEN UND RECHNEN GESCHEHEN GEMEINSAM

Welche Formelvariante gilt, kann von den Zahlenwerten abhaengen (siehe
`Berechnung.anwendbar`). Ein rein struktureller Plan koennte das nicht
entscheiden. Darum wird waehrend des Aufloesens gerechnet: sobald die Eingaben
einer Variante vorliegen, wird geprueft, ob sie anwendbar ist; wenn nicht,
kommt die naechste an die Reihe.

Weil rekursiv in die Tiefe gearbeitet wird, steht im Protokoll jede Groesse vor
der, die sie braucht -- die Reihenfolge des Berichts stimmt also von selbst.


## EIGENSTAENDIG NUTZBAR


```python
werk = Rechenwerk()
werk.registriere(*beton_berechnungen("C30_37"))
loesung = werk.loese("beton.C30_37.f_cd")
print(loesung.wert("beton.C30_37.f_cd"))
for f in loesung.fehlende:
    print(f)
```

## Inhalt

### RechenwerkFehler

```python
class RechenwerkFehler(Exception)
```

Aufbau- oder Bedienfehler am Rechenwerk.

### ZyklusFehler

```python
class ZyklusFehler(RechenwerkFehler)
```

Im Abhaengigkeitsgraphen wurde ein Kreis entdeckt.

### Herkunft

```python
@dataclass
class Herkunft
```

Wie ein Wert zustande kam -- die Kante im Abhaengigkeitsgraphen.

- `wert_id: str`
- `berechnung_id: str`
- `eingaben: Tuple[str, ...]`

### NichtBerechenbar

```python
@dataclass
class NichtBerechenbar
```

Ein Ziel liess sich nicht aufloesen, mit Begruendung.

- `ziel: str`
- `fehlende: List[FehlendeEingabe] = field(default_factory=list)`
- `verworfene_varianten: List[Tuple[str, str]] = field(default_factory=list)` – Paare aus (Berechnungs-ID, Grund der Ablehnung).

### _gesammelt

```python
def _gesammelt(urteile: Sequence[NachweisUrteil]) -> List[NachweisUrteil]
```

Teilurteile derselben Frage auf das schlechteste zusammenziehen.

Gesammelt wird je Namensraum, also je Nachweis: die vier Lagen des
Duktilitaetsnachweises sind vier Antworten auf dieselbe Frage, die drei
Lastfaelle des M-N-Nachweises sind drei verschiedene Fragen. Welche von
beidem es ist, sagt das Urteil selbst -- nicht diese Stelle, die von den
Nachweisen nichts weiss.

Die Reihenfolge bleibt die des ersten Teilurteils: eine Tabelle, in der
Zeilen ihren Platz je nach Zahlenwert wechseln, laesst sich nicht
vergleichen.

### Loesung

```python
@dataclass
class Loesung
```

Ergebnis eines Rechenlaufs.

- `werte: Dict[str, Wert] = field(default_factory=dict)`
- `protokoll: Protokoll = field(default_factory=Protokoll)`
- `reihenfolge: List[str] = field(default_factory=list)` – IDs der ausgefuehrten Berechnungen, in Ausfuehrungsreihenfolge. Genau die Liste, die die Oberflaeche aktivieren soll, wenn der Benutzer einen Zielwert auswaehlt.
- `graph: Dict[str, Herkunft] = field(default_factory=dict)`
- `fehlende: List[FehlendeEingabe] = field(default_factory=list)`
- `nicht_berechenbar: Dict[str, NichtBerechenbar] = field(default_factory=dict)`
- `urteile: List[NachweisUrteil] = field(default_factory=list)`
- `befunde: Dict[str, Any] = field(default_factory=dict)` – Je Berechnung, was sie ueber ihre Ausgaben hinaus festgehalten hat -- Linien, Fallergebnisse, das Ergebnis eines Systems (siehe [[opencivil.core.berechnung#Ausfuehrung|Ausfuehrung]]). Nach Berechnungs-ID.

#### Loesung.anhaengen

```python
def anhaengen(self, teil: 'Loesung') -> None
```

Einen weiteren Lauf anhaengen, in dieser Reihenfolge -- so setzt der
Dienst die Bauteile zusammen, jedes aus seinem eigenen Lauf oder aus
dem Zwischenspeicher. `teil` bleibt dabei, wie es ist.

#### Loesung.befund

```python
def befund(self, berechnung: Union[str, Berechnung]) -> Any
```

Der Befund einer Berechnung -- nach ihrer ID oder ihr selbst.

#### Loesung.wert

```python
def wert(self, wert_id: str) -> Wert
```

#### Loesung.groesse

```python
def groesse(self, wert_id: str) -> Groesse
```

#### Loesung.hat

```python
def hat(self, wert_id: str) -> bool
```

#### Loesung.vollstaendig

```python
@property
def vollstaendig(self) -> bool
```

#### Loesung.gefuehrte_urteile

```python
@property
def gefuehrte_urteile(self) -> List[NachweisUrteil]
```

Die Urteile, die in eine Tabelle gehoeren.

Ohne die stillen: ein stiller Nachweis ist ausgeschaltet, er rechnet
mit, damit ein Hinweis stehen kann, wenn er nicht aufgeht -- gefuehrt
hat ihn niemand.

Und je Nachweis, der seine Faelle als Teile derselben Frage stempelt
(siehe [[opencivil.core.berechnung#NachweisUrteil|NachweisUrteil.sammel]]), nur das schlechteste. Vier
Zeilen fuer eine Frage waren drei zuviel; beantwortet wird sie von
der schlechtesten Lage.

#### Loesung.stille_maengel

```python
@property
def stille_maengel(self) -> List[NachweisUrteil]
```

Ausgeschaltete Nachweise, die nicht aufgehen -- nur als Hinweis.

#### Loesung.alle_nachweise_erfuellt

```python
@property
def alle_nachweise_erfuellt(self) -> bool
```

Ohne die stillen: sie sind ausgeschaltet und zaehlen nicht mit.

Sonst staende oben rechts «nicht erfuellt» wegen eines Nachweises,
den niemand fuehrt -- und man faende in der Tabelle nichts dazu.

#### Loesung.kette

```python
def kette(self, wert_id: str) -> List[str]
```

Alle Berechnungen, die zu diesem Wert gefuehrt haben, in Reihenfolge.

Das ist die Rueckverfolgung: welche Rechenschritte waren noetig?

#### Loesung.benoetigte_werte

```python
def benoetigte_werte(self, wert_id: str) -> List[str]
```

Alle Werte, die in die Berechnung dieses Wertes eingegangen sind.

### Rechenwerk

```python
class Rechenwerk
```

Sammelt Berechnungen und Eingabewerte und loest Ziele auf.

Ein Rechenwerk ist bewusst zustandsbehaftet, aber die Rechenlaeufe sind es
nicht: [[opencivil.core.rechenwerk#Rechenwerk.loese|loese]] liefert eine frische [[opencivil.core.rechenwerk#Loesung|Loesung]] und laesst das
Rechenwerk selbst unveraendert (abgesehen vom Zwischenspeicher).

#### Rechenwerk.definiere

```python
def definiere(self, *definitionen: WertDef) -> 'Rechenwerk'
```

Macht Wert-Definitionen bekannt, die keine Berechnung erzeugt.

#### Rechenwerk.kennt_berechnung

```python
def kennt_berechnung(self, berechnung_id: str) -> bool
```

#### Rechenwerk.registriere

```python
def registriere(self, *berechnungen: Berechnung) -> 'Rechenwerk'
```

Nimmt Berechnungen auf.

Mehrere Berechnungen duerfen denselben Wert liefern -- das sind die
Varianten, unter denen der Loeser spaeter waehlt. Dieselbe Berechnung
zweimal anzumelden ist dagegen ein Aufbaufehler und wird gemeldet;
wer nicht weiss, ob schon angemeldet wurde, fragt vorher mit
[[opencivil.core.rechenwerk#Rechenwerk.kennt_berechnung|kennt_berechnung]].

#### Rechenwerk.setze

```python
def setze(self, wert_id: str | WertDef, groesse: Groesse, quelle: Optional[Quelle]=None) -> 'Rechenwerk'
```

Setzt einen Wert von Hand.

Gibt es fuer den Wert eine Berechnung, gilt er als *ueberschrieben* und
die Berechnung wird uebersprungen -- genau das erlaubt es, berechnete
Materialkennwerte gezielt durch eigene zu ersetzen. Gibt es keine, ist
es eine gewoehnliche *Eingabe*.

#### Rechenwerk.loesche

```python
def loesche(self, wert_id: str) -> 'Rechenwerk'
```

Nimmt eine Ueberschreibung zurueck -- der Wert wird wieder gerechnet.

#### Rechenwerk.berechnungen

```python
@property
def berechnungen(self) -> Tuple[Berechnung, ...]
```

#### Rechenwerk.bekannte_werte

```python
@property
def bekannte_werte(self) -> Tuple[str, ...]
```

#### Rechenwerk.vorgegebene_werte

```python
@property
def vorgegebene_werte(self) -> Mapping[str, Wert]
```

#### Rechenwerk.definition

```python
def definition(self, wert_id: str) -> Optional[WertDef]
```

#### Rechenwerk.erzeuger

```python
def erzeuger(self, wert_id: str) -> Tuple[Berechnung, ...]
```

Alle Berechnungen, die diesen Wert liefern koennen (Varianten).

#### Rechenwerk.moegliche_ziele

```python
def moegliche_ziele(self) -> Tuple[str, ...]
```

Alle Werte, die ueberhaupt berechenbar waeren -- und die Berechnungen
ohne Ausgabe, nach denen sonst kein Wert fragte.

#### Rechenwerk.loese

```python
def loese(self, *ziele: str, bekannt: Optional[Mapping[str, Wert]]=None, ohne_herleitung: bool=False) -> Loesung
```

Berechnet die angegebenen Ziele und alles, was dafuer noetig ist.

Ein Ziel ist die ID eines Werts oder einer Berechnung. Eine Berechnung
laeuft dann als Ganzes, einmal -- auch ohne Ausgabe, wie ein Nachweis
ohne Lastfall. Eine Formel traegt die ID ihres Ergebnisses; dort ist
der Wert gemeint, was auf dasselbe hinauslaeuft.

Nicht mehr: Werte, die kein Ziel braucht, werden nicht angefasst.
Laesst sich ein Ziel nicht aufloesen, bricht der Lauf nicht ab -- das
Ziel landet in [[opencivil.core.rechenwerk#Loesung|Loesung.nicht_berechenbar]], und die fehlenden
Eingaben werden benannt.

`bekannt` sind Werte, die bereits vorliegen. Sie gelten als
gerechnet: der Lauf holt sie nicht noch einmal und schreibt sie auch
nicht noch einmal ins Protokoll. Damit lassen sich mehrere Laeufe
aneinanderhaengen, ohne dass die Baustoffe in jedem davon erneut
hergeleitet werden -- und damit laesst sich ein Bauteil auslassen,
dessen Ergebnis von einem frueheren Lauf noch gilt.

**Der Aufrufer haftet dafuer, dass die Werte noch gelten.** Das
Rechenwerk prueft es nicht; es kann es nicht, denn was eine Eingabe
wert ist, weiss nur, wer sie gesetzt hat.

`ohne_herleitung` rechnet dasselbe, schreibt aber nichts mit --
fuer Laeufe, die nur Werte und Urteile brauchen.

#### Rechenwerk.loese_alles

```python
def loese_alles(self) -> Loesung
```

Berechnet alles, was sich aus den vorhandenen Eingaben ergibt.

Was nicht geht, wird nicht erzwungen, sondern mit Begruendung in
[[opencivil.core.rechenwerk#Loesung|Loesung.nicht_berechenbar]] vermerkt.

### _Lauf

```python
class _Lauf
```

Fuehrt einen Aufloesungsvorgang durch.

Eigenes Objekt, damit ein Lauf seinen ganzen Zustand (Zwischenspeicher,
Rekursionsstapel, Protokoll) fuer sich hat und mehrere Laeufe sich nicht in
die Quere kommen.

#### _Lauf.ziel

```python
def ziel(self, ziel: str) -> None
```

Loest ein angefordertes Ziel auf -- Wert oder Berechnung -- und merkt es sich.

#### _Lauf.rechnen

```python
def rechnen(self, berechnung_id: str, pfad: Tuple[str, ...]) -> bool
```

Eine Berechnung als Ganzes, einmal je Lauf -- ob sie Ausgaben hat oder
nicht. `False`, wenn ihr Eingaben fehlen oder sie nicht anwendbar
ist; der Grund steht dann unter ihrer ID.

Brachte der Aufrufer ihre Ausgaben schon mit, lief sie in einem
frueheren Lauf: dann gilt sie als gerechnet, wie ein mitgebrachter
Wert.

#### _Lauf.aufloesen

```python
def aufloesen(self, ziel: str, pfad: Tuple[str, ...]) -> Optional[Wert]
```

Liefert den Wert oder None, wenn er nicht beschaffbar ist.

#### _Lauf._als_fehlend_vermerken

```python
def _als_fehlend_vermerken(self, ziel: str, pfad: Tuple[str, ...]) -> None
```

Ein Wert ohne jeden Erzeuger -- eine echte Eingabe, die fehlt.

#### _Lauf._bis_zur_wurzel

```python
def _bis_zur_wurzel(self, ziel: str, gesehen: Set[str]) -> List[FehlendeEingabe]
```

Faehrt die Fehlschlagkette hinunter bis zu den echten Eingabeluecken.

Dem Benutzer nuetzt die Meldung "f_cd nicht berechenbar" wenig -- er
will wissen, dass f_ck und gamma_c fehlen. Darum wird jede fehlende
Zwischengroesse weiter aufgeloest, bis nur noch Werte uebrig sind, fuer
die es ueberhaupt keinen Erzeuger gibt.

#### _Lauf.abschliessen

```python
def abschliessen(self) -> Loesung
```


## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]

## Gebraucht von

- [[opencivil.bericht.gliederung]]
- [[opencivil.bericht.konsole]]
- [[opencivil.bericht.latex_dokument]]
- [[opencivil.bericht.markdown]]
- [[opencivil.bericht.zusammenfassung]]
- [[opencivil.ergebnis]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.querschnitt.schnittanalyse]]
- [[opencivil.spannungsanalyse]]
- [[opencivil.web.api]]
- [[opencivil.web.diagrammdaten]]
- [[opencivil.web.dienst]]
- [[opencivil.web.speicher]]
