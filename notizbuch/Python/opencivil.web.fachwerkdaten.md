---
erzeugt: a7bd60975918
art: modul
tags: [modul]
---
> [!abstract] opencivil/web/fachwerkdaten.py
> was die Oberflaeche von einem Fachwerkmodell zeichnet.
> Paket [[opencivil.web]] · [Quelltext](../../opencivil/web/fachwerkdaten.py)

## VERANTWORTUNG

Aus dem Befund eines Fachwerkmodells die Daten seiner Zeichnung: seine
Meldungen, ob es bereit ist, ein Fachwerk zu suchen – keine Meldung des
Modells haelt es auf –, und das gefundene Fachwerk, nachgerechnet
([[opencivil.web.fachwerkdaten#uebersicht|uebersicht]]). Dazu eine Runde der Suche ([[opencivil.web.fachwerkdaten#suchen|suchen]]) und der
Teil des Katalogs, den nur das Fachwerkmodell braucht ([[opencivil.web.fachwerkdaten#katalog|katalog]]).
Scheiben, Lager und Lasten zeichnet die Oberflaeche nach dem Projekt.


## EIN FACHWERK, ZWEI WEGE

Was eine Runde gibt und was die Rechnung nachgerechnet hat, hat dieselbe
Form ([[opencivil.web.fachwerkdaten#_fachwerk|_fachwerk]]): Knoten `{x, y}` in m, Staebe ``{von, bis, N,
l}`` mit N in kN, Zug positiv, und l in m – so zeichnet die Seite beide
mit einem Bild, waehrend gesucht wird und danach.

## Inhalt

### zeichnung

```python
def zeichnung(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Dict[str, Any]
```

Was die Zeichnung eines Fachwerkmodells unter seine Teile legt – auch wenn es nicht rechnet.

### uebersicht

```python
def uebersicht(befund: Optional[Fachwerkbefund]) -> Dict[str, Any]
```

`bereit`; `meldungen` des Modells und `zum_fachwerk`, was zum
Fachwerk zu sagen ist, je `{text, elemente, fehler, unfertig}`;
`abdruck` von Modell und Verfahren und `stand` – `keines`,
`veraltet`, `unlesbar`, `gefunden` oder leer
([[opencivil.fachwerkmodell.werk#Fachwerkbefund|Fachwerkbefund]]); und `fachwerk`: nachgerechnet, mit `V`
in kNm, den Kraeften der Lager, den Runden und wie viele Staebe es gab
– oder `None`. Ohne Befund leer.

Am Abdruck erkennt die Seite, ob das Fachwerk, das eine Suche eben gab,
zum Modell der letzten Rechnung gehoert – und zeigt es, bis die
Rechnung es nachgerechnet hat.

### _fachwerk

```python
def _fachwerk(n: Nachrechnung) -> Dict[str, Any]
```

Siehe Dateikopf – dazu `V` in kNm und je Lager `{lager, R_x, R_y}` in kN.

### suchen

```python
def suchen(eintrag: FachwerkmodellEintrag, zustand: Optional[Mapping[str, Any]]) -> Dict[str, Any]
```

Eine Runde der Suche ([[opencivil.fachwerkmodell.suche#runde|runde]]):
der `zustand` der letzten hinein – `None` fuer die erste –, heraus

- `fertig`: ob die Suche zu Ende ist – auch, wenn sie nicht beginnen kann;
- `abdruck`: von Modell und Verfahren, wie in [[opencivil.web.fachwerkdaten#uebersicht|uebersicht]] –
  leer, wenn das Modell nicht bereit ist;
- `zustand`: fuer die naechste Runde;
- `gefunden`: was die Seite im Eintrag ablegt, wenn sie aufhoert
  ([[opencivil.projekt.fachwerkmodell#GefundenesFachwerk|GefundenesFachwerk]]);
- `fachwerk`: dasselbe zum Zeichnen, nachgerechnet ([[opencivil.web.fachwerkdaten#_fachwerk|_fachwerk]]);
- `stand`: Runde, Staebe im Modell, moegliche, wie viele dazukommen;
- `meldungen`: was dem Suchen im Weg steht oder offen bleibt.

### _ohne

```python
def _ohne(meldungen, abdruck_: str='') -> Dict[str, Any]
```

Die Antwort, wenn die Suche nicht beginnen kann: nur, warum.

### _zustand

```python
def _zustand(roh: Optional[Mapping[str, Any]]) -> Optional[Suchzustand]
```

Der Zustand, wie die Seite ihn zurueckschickt – streng gelesen: sie hat ihn so bekommen.

### katalog

```python
def katalog() -> Dict[str, Any]
```

Womit die Kennungen der Teile beginnen, je Liste, und wie ein Lager halten kann.


## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.rechenwerk]]
- [[opencivil.fachwerkmodell.grundstruktur]]
- [[opencivil.fachwerkmodell.modell]]
- [[opencivil.fachwerkmodell.nachrechnung]]
- [[opencivil.fachwerkmodell.pruefen]]
- [[opencivil.fachwerkmodell.suche]]
- [[opencivil.fachwerkmodell.werk]]
- [[opencivil.projekt]]
- [[opencivil.projekt.aufbau.fachwerkmodell]]
- [[opencivil.projekt.fachwerkmodell]]
- [[opencivil.projekt.lesen]]
- [[opencivil.stabwerk.system]]
- [[opencivil.web.anzeige]]

## Gebraucht von

- [[opencivil.web.api]]
- [[opencivil.web.dienst]]
- [[opencivil.web.zeichendaten]]
