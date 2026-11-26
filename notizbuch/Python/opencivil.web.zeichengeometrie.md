---
erzeugt: 03cb4bcffaa4
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
Spannglied seine Werte und je Stahlprofil sein Umriss. Gerechnet wird nur
Geometrie -- und die Spannkraft, aus derselben Herleitung wie im Bericht.
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

Die Zeichnung einer Querschnittsanalyse, wie der Kern sie sieht -- in mm.

Geprueft von [[opencivil.querschnitt.analyse#Zeichnung|Zeichnung]], denselben
Pruefungen, die das Bauteil vor dem Rechnen macht; hier aber alle
Meldungen auf einmal statt nur der ersten. Die Wahl der Materialien kommt
dazu, nach derselben Regel wie beim Bauen ([[opencivil.projekt.aufbau.kern#materialgrund|materialgrund]]) -- das
kann nur das Projekt wissen. Ebenso ein Verweis auf einen Knoten, den es
nicht gibt, und ein Spannglied, dessen Durchmesser es in seiner Sorte
nicht gibt. `fehler` sagt je Meldung, ob etwas nicht stimmt oder nur
fehlt: ein geloeschter Stahl ist zu ersetzen, kein Widerspruch. Sind die
Materialien zusammen keine Bauweise ([[opencivil.querschnitt.bauweise#bauweise|bauweise]]), sagt es eine
Meldung ohne Element, grau.

`bauweise` ist die Bauweise ([[opencivil.querschnitt.bauweise#Bauweise|Bauweise]]),
leer ohne. `ohne_nachweise` ist der Satz, warum ein Querschnitt dieser
Bauweise keinen Nachweis hat -- leer beim Stahlbeton, beim Stahl und ohne
Bauweise --, `ohne_analysen` derselbe fuer die
Spannung-Dehnung-Analysen, leer ausser im Verbund. Danach zeigt die
Analyse ihre Kacheln ([[opencivil.projekt.aufbau.querschnittsanalyse#ohne_nachweise|ohne_nachweise]], [[opencivil.projekt.aufbau.querschnittsanalyse#ohne_analysen|ohne_analysen]]).

`gueltig` heisst: die Zeichnung rechnet. Eine Spannung ueber der
Grenze der Norm steht rot am Glied, haelt die Rechnung aber nicht an --
gerechnet wird mit den Zahlen des Benutzers.

### _tiefen

```python
def _tiefen(eltern: Optional[Sequence[Optional[int]]], kennungen: Sequence[str]) -> Dict[str, int]
```

Wie tief jedes Element verschachtelt ist, je Kennung -- 0 fuer eines, das
in keinem liegt: so zeichnet das Fenster die aeusseren zuerst. Ein Profil
zaehlt mit seinem Umriss, nicht mit seinem Loch. Ohne gueltige
Verschachtelung alle 0.

### _profil

```python
def _profil(p: Mapping, tiefe: int) -> dict
```

Ein Stahlprofil, wie das Fenster es zeichnet: seine Umrisse und die Mitte,
zu der sie gehoeren -- haengt sie an einem Knoten, der eben verschoben
wird, schiebt das Fenster das Bild mit, bis die naechste Antwort da ist.
Dazu, was es ist, seine Flaeche aus dem Umriss, die Masse von aussen und
die Punkte zum Fangen; ob Drehen und Spiegeln es aendern, sagt, ob das
Fenster die Schalter dafuer zeigt.

### _als_satz

```python
def _als_satz(teil: str) -> str
```

Ein Satzteil als Satz: gross beginnend, mit Punkt -- leer bleibt leer.

### _Glieder

```python
class _Glieder(NamedTuple)
```

Was die Zeichnung von ihren Spanngliedern weiss -- siehe [[opencivil.web.zeichengeometrie#_spannglieder|_spannglieder]].

- `gebaut: Dict[str, Spannglied]`
- `werte: Dict[str, dict]`
- `fehlt: List[dict]` – Grau: das Erzeugnis fehlt noch -- die Zeichnung rechnet nicht.
- `grenzen: List[dict]` – Rot: eine Spannung jenseits der Grenze der Norm -- gerechnet wird trotzdem.

### _spannglieder

```python
def _spannglieder(roh: Sequence[Mapping], projekt) -> _Glieder
```

Die Glieder, die rechnen, je Kennung -- und ihre Werte aus derselben
Herleitung wie im Bericht ([[opencivil.querschnitt.spannglieder#Spannglieder|Spannglieder]]), mit den Saetzen dazu,
was an ihren Spannungen die Norm verletzt ([[opencivil.querschnitt.spannglieder#grenzen_verletzt|grenzen_verletzt]]).
Dazu die Meldungen zu denen, deren Durchmesser es in der Sorte nicht
gibt: grau, wie beim Bauen ([[opencivil.projekt.aufbau.querschnittsanalyse#erzeugnis_grund|erzeugnis_grund]]). Ein falsches oder
fehlendes Material meldet schon [[opencivil.projekt.aufbau.kern#materialgrund|materialgrund]]; ein Material, das
selbst nicht rechnet, sagt es in seinem Fenster.


## Braucht

- [[opencivil.core.protokoll]]
- [[opencivil.core.rechenwerk]]
- [[opencivil.material.basis]]
- [[opencivil.material.spannstahl]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.aufbau.querschnittsanalyse]]
- [[opencivil.projekt.lesen]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.projekt.spannglieder]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.bauweise]]
- [[opencivil.querschnitt.geometrie]]
- [[opencivil.querschnitt.spannglieder]]
- [[opencivil.stahlprofile.lage]]

## Gebraucht von

- [[opencivil.web.dienst]]
