---
erzeugt: b19b1210b990
art: modul
tags: [modul]
---
> [!abstract] opencivil/web/zeichengeometrie.py
> die Zeichnung einer Querschnittsanalyse, wie der Kern sie sieht.
> Paket [[opencivil.web]] · [Quelltext](../../opencivil/web/zeichengeometrie.py)

## VERANTWORTUNG

Was das Zeichenfenster einer Querschnittsanalyse vom Kern ueber ihre
Zeichnung erfaehrt (Anfrage `geometrie`): jede Meldung am Element, das sie
betrifft, die Staebe einer Linie mit ihrer tatsaechlichen Teilung, die
Lage in der Ueberdeckung, der Schwerpunkt, die Zellen der Schubwaende, je
Spannglied seine Werte, je Stahlprofil sein Umriss und je
Blechverbunddecke ihr Beton und ihr Blech. Gerechnet wird nur Geometrie –
und die Spannkraft, aus derselben Herleitung wie im Bericht.
Schnell genug fuer jede Aenderung.

Bis 2026-11-26 stand das in [[opencivil.web.api]]; mit den Spanngliedern
waere die Datei ueber tausend Zeilen gewachsen.


## EINHEITEN

Wie die Zeichnung: Lagen und Masse in mm, Flaechen in mm², Spannungen in
N/mm², die Vordehnung in Promille, Kraefte in kN.

## Inhalt

### geometrie

```python
def geometrie(eintrag, projekt) -> dict
```

Die Zeichnung einer Querschnittsanalyse, wie der Kern sie sieht – in mm.

Geprueft von [[opencivil.querschnitt.analyse#Zeichnung|Zeichnung]], denselben
Pruefungen, die das Bauteil vor dem Rechnen macht; hier aber alle
Meldungen auf einmal statt nur der ersten. Die Wahl der Materialien kommt
dazu, nach derselben Regel wie beim Bauen ([[opencivil.projekt.aufbau.kern#materialgrund|materialgrund]]) – das
kann nur das Projekt wissen. Ebenso ein Verweis auf einen Knoten, den es
nicht gibt, und ein Spannglied, dessen Durchmesser es in seiner Sorte
nicht gibt. `fehler` sagt je Meldung, ob etwas nicht stimmt oder nur
fehlt: ein geloeschter Stahl ist zu ersetzen, kein Widerspruch. Sind die
Materialien zusammen keine Bauweise ([[opencivil.querschnitt.bauweise#bauweise|bauweise]]), sagt es eine
Meldung ohne Element, grau.

`bauweise` ist die Bauweise ([[opencivil.querschnitt.bauweise#Bauweise|Bauweise]]),
leer ohne. `ohne_nachweise` ist der Satz, warum ein Querschnitt dieser
Bauweise keinen Nachweis hat – leer beim Stahlbeton, beim Stahl und ohne
Bauweise –, `ohne_analysen` derselbe fuer die
Spannung-Dehnung-Analysen, leer ausser im Verbund und in der
Blechverbunddecke. Danach zeigt die
Analyse ihre Kacheln ([[opencivil.projekt.aufbau.querschnittsanalyse#ohne_nachweise|ohne_nachweise]], [[opencivil.projekt.aufbau.querschnittsanalyse#ohne_analysen|ohne_analysen]]).
`knickkurven` sagt je Achse die Knickspannungskurve, die Figur 7 dem
einzigen Profil des Querschnitts zuweist, `knickkurven_fehlen`, welche
einem Stabilitaetsnachweis fehlt ([[opencivil.web.zeichengeometrie#_knickkurven|_knickkurven]]).
`laengsschub_fehlt` sagt fuer die Kachel «Längsschub» einer
Blechverbunddecke, was ihm noch fehlt, «m und k fehlen» – leer, wo
nichts fehlt oder keine Decke gezeichnet ist
([[opencivil.verbund.blechdecke#Laengsschub.fehlt_kurz|fehlt_kurz]]).

`gueltig` heisst: die Zeichnung rechnet. Eine Spannung ueber der
Grenze der Norm steht rot am Glied, haelt die Rechnung aber nicht an –
gerechnet wird mit den Zahlen des Benutzers.

### _knickkurven

```python
def _knickkurven(eintrag, flaechen: Sequence[Mapping], brutto) -> Dict[str, Any]
```

`knickkurven`: je Achse die Knickspannungskurve des einzigen Profils,
`kurve` und `grund` – `None`, wo der Querschnitt nicht aus einem
einzigen Profil besteht ([[opencivil.stahlbau.stabilitaet#einzelprofil|einzelprofil]]):
dann waehlt der Benutzer sie. `knickkurven_fehlen`: der Satz, welche
Kurve den Faellen von Knicken und Kippen dann fehlt – derselbe wie im
Fall ([[opencivil.stahlbau.stabilitaet#fehlende_kurven|fehlende_kurven]]), leer,
wo keine fehlt.

### _tiefen

```python
def _tiefen(eltern: Optional[Sequence[Optional[int]]], kennungen: Sequence[str]) -> Dict[str, int]
```

Wie tief jedes Element verschachtelt ist, je Kennung – 0 fuer eines, das
in keinem liegt: so zeichnet das Fenster die aeusseren zuerst. Ein Profil
zaehlt mit seinem Umriss, nicht mit seinem Loch. Ohne gueltige
Verschachtelung alle 0.

### _profil

```python
def _profil(p: Mapping, tiefe: int) -> dict
```

Ein Stahlprofil, wie das Fenster es zeichnet: seine Umrisse und die Mitte,
zu der sie gehoeren – haengt sie an einem Knoten, der eben verschoben
wird, schiebt das Fenster das Bild mit, bis die naechste Antwort da ist.
Dazu, was es ist, seine Flaeche aus dem Umriss, die Masse von aussen und
die Punkte zum Fangen; ob Drehen und Spiegeln es aendern, sagt, ob das
Fenster die Schalter dafuer zeigt.

### _blechdecke

```python
def _blechdecke(d: Mapping, tiefe: int) -> dict
```

Eine Blechverbunddecke, wie das Fenster sie zeichnet: der Umriss ihres
Betons und die Linie ihres Blechs zur Ecke links unten, an der sie haengt
– wie beim Profil schiebt das Fenster beides mit dem Knoten mit, bis die
naechste Antwort da ist. Gefangen wird an jeder Ecke des Betons. Dazu,
was aus den Massen folgt, aus derselben Form wie in der Herleitung
([[opencivil.querschnitt.profilblech#Blechform|Blechform]]): die Breite `b`,
die Dicke `t` des Blechs, sein Schwerpunkt `e` ueber der Unterkante,
`d_p`, `b_0` und die Flaeche `A` des Blechs ueber die ganze Breite.
Und eine Rippe mit ihren Massen als Bild: es sagt im Fenster, was die
Zeichen der Felder meinen ([[opencivil.querschnitt.profilblech#rippenskizze|rippenskizze]]).

### _als_satz

```python
def _als_satz(teil: str) -> str
```

Ein Satzteil als Satz: gross beginnend, mit Punkt – leer bleibt leer.

### _Glieder

```python
class _Glieder(NamedTuple)
```

Was die Zeichnung von ihren Spanngliedern weiss – siehe [[opencivil.web.zeichengeometrie#_spannglieder|_spannglieder]].

- `gebaut: Dict[str, Spannglied]`
- `werte: Dict[str, dict]`
- `fehlt: List[dict]` – Grau: das Erzeugnis fehlt noch – die Zeichnung rechnet nicht.
- `grenzen: List[dict]` – Rot: eine Spannung jenseits der Grenze der Norm – gerechnet wird trotzdem.

### _spannglieder

```python
def _spannglieder(roh: Sequence[Mapping], projekt) -> _Glieder
```

Die Glieder, die rechnen, je Kennung – und ihre Werte aus derselben
Herleitung wie im Bericht ([[opencivil.querschnitt.spannglieder#Spannglieder|Spannglieder]]), mit den Saetzen dazu,
was an ihren Spannungen die Norm verletzt ([[opencivil.querschnitt.spannglieder#grenzen_verletzt|grenzen_verletzt]]).
Dazu die Meldungen zu denen, deren Erzeugnis oder Art es in der Sorte
nicht gibt: grau, wie beim Bauen ([[opencivil.querschnitt.spannglieder#was_fehlt|was_fehlt]]). Ein falsches oder
fehlendes Material meldet schon [[opencivil.projekt.aufbau.kern#materialgrund|materialgrund]]; ein Material, das
selbst nicht rechnet, sagt es in seinem Fenster.


## Braucht

- [[opencivil.core.protokoll]]
- [[opencivil.core.rechenwerk]]
- [[opencivil.material.basis]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.aufbau.querschnittsanalyse]]
- [[opencivil.projekt.blechdecken]]
- [[opencivil.projekt.lesen]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.projekt.spannglieder]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.bauweise]]
- [[opencivil.querschnitt.geometrie]]
- [[opencivil.querschnitt.profilblech]]
- [[opencivil.querschnitt.spannglieder]]
- [[opencivil.stahlbau.stabilitaet]]
- [[opencivil.stahlprofile.lage]]

## Gebraucht von

- [[opencivil.web.dienst]]
