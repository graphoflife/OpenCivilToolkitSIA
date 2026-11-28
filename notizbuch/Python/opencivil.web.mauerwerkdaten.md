---
erzeugt: c18cd1c9b428
art: modul
tags: [modul]
---
> [!abstract] opencivil/web/mauerwerkdaten.py
> was die Oberflaeche von einer Wand aus Mauerwerk zeichnet.
> Paket [[opencivil.web]] · [Quelltext](../../opencivil/web/mauerwerkdaten.py)

## VERANTWORTUNG

Aus dem Befund einer Wand die Daten ihrer Zeichnung ([[opencivil.web.mauerwerkdaten#uebersicht|uebersicht]]):
ihre Meldungen – die zu Mauerwerk und Dicke auch fuer sich, fuer die
Kachel der Maske –, ob sie rechnet, ihre Pfeiler und je Oeffnung die
Flaeche ihres Sturzes – der Kern weiss, wie weit er aufliegt; die Seite zeichnet
ihn nur. Dazu je Pfeiler und Sturzauflager das Urteil, das an ihm gilt
([[opencivil.web.mauerwerkdaten#urteile|urteile]]), fuer die Farbe im Bild, und der Teil des Katalogs, den
nur die Wand braucht ([[opencivil.web.mauerwerkdaten#katalog|katalog]]). Umriss, Oeffnungen und Lasten
zeichnet die Oberflaeche nach dem Projekt; die Bemessungswerte stehen in
der Zusammenfassung ueber den Nachweisen ([[opencivil.mauerwerk.uebersicht]]).


## EINHEITEN

In m, wie im Zeichenfenster; die ueblichen Dicken in mm, wie das Feld.

## Inhalt

### zeichnung

```python
def zeichnung(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Dict[str, Any]
```

Was die Zeichnung einer Wand unter ihre Teile legt – auch wenn sie
nicht rechnet: [[opencivil.web.mauerwerkdaten#uebersicht|uebersicht]] und die Urteile ([[opencivil.web.mauerwerkdaten#urteile|urteile]]).

### urteile

```python
def urteile(nachweise: Sequence[Nachweis], alle: Sequence[NachweisUrteil]) -> Dict[str, Dict[str, str]]
```

Je Pfeiler und Sturzauflager («O1 links») das Urteil, das an ihm gilt:
das ungünstigste über seine Nachweise und Kombinationen – ein
verfehltes vor einem offenen, ein offenes vor dem kleinsten Grad. Je Ort
`{zustand, grad, titel}`: `zustand` ist `verfehlt`, `offen`,
`erfuellt` oder `ohne` – keine Kombination wirkt dort ein –,
`titel` sagt in Worten, welcher Nachweis in welcher Kombination.

### _massgebend

```python
def _massgebend(liste: Sequence[Tuple[NachweisUrteil, Stelle]]) -> Dict[str, str]
```

Das Urteil, das an einem Ort gilt – siehe [[opencivil.web.mauerwerkdaten#urteile|urteile]].

### uebersicht

```python
def uebersicht(befund: Optional[Wandbefund]) -> Dict[str, Any]
```

`bereit`: ob die Wand rechnet; `meldungen` alle je ``{text,
elemente, fehler, unfertig}`, `zum_mauerwerk`` die zu Mauerwerk und
Dicke darunter noch einmal; `pfeiler` je `{name, x0, x1, y0, y1, b}`
und `stuerze` je `{oeffnung, sturz, x0, y0, x1, y1}` in m – leer,
solange die Zeichnung nicht rechnet. Ohne Befund ist alles leer.

### unfertig

```python
def unfertig(grund: str) -> Dict[str, Any]
```

Die Uebersicht einer Wand, die nicht rechnet, weil ihr etwas fehlt –
`grund` ein Satzteil ohne Punkt: grau, kein Fehler (Benutzer, 2026-11-19).

### katalog

```python
def katalog() -> Dict[str, Any]
```

Womit die Kennungen der Teile beginnen, je Liste, die Stellungen der
Schalter – wie gemauert, die Stossfugen, Kopf und Fuss, die Ränder links
und rechts, die Art eines Sturzes – und je Sorte die üblichen Dicken in mm.


## Braucht

- [[opencivil.core.nachweis]]
- [[opencivil.core.rechenwerk]]
- [[opencivil.core.sprache]]
- [[opencivil.mauerwerk.modell]]
- [[opencivil.mauerwerk.nachweise]]
- [[opencivil.mauerwerk.pruefen]]
- [[opencivil.mauerwerk.werk]]
- [[opencivil.projekt]]
- [[opencivil.projekt.mauerwerk]]
- [[opencivil.stabwerk.system]]

## Gebraucht von

- [[opencivil.web.api]]
- [[opencivil.web.dienst]]
- [[opencivil.web.zeichendaten]]
