---
erzeugt: bdd07d454086
art: modul
tags: [modul]
---
> [!abstract] opencivil/web/fachwerkdaten.py
> was die Oberflaeche von einem Fachwerkmodell zeichnet.
> Paket [[opencivil.web]] · [Quelltext](../../opencivil/web/fachwerkdaten.py)

## VERANTWORTUNG

Aus dem Befund eines Fachwerkmodells die Daten seiner Zeichnung: seine
Meldungen und ob es bereit ist, ein Fachwerk zu suchen – keine Meldung
haelt es auf ([[opencivil.web.fachwerkdaten#uebersicht|uebersicht]]). Dazu der Teil des Katalogs, den nur das
Fachwerkmodell braucht ([[opencivil.web.fachwerkdaten#katalog|katalog]]): die Vorsilben seiner Teile und
die Stellungen eines Lagers. Scheiben, Lager und Lasten zeichnet die
Oberflaeche nach dem Projekt.

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

`bereit` und `meldungen` (`{text, elemente, fehler, unfertig}`) – ohne Befund leer.

### katalog

```python
def katalog() -> Dict[str, Any]
```

Womit die Kennungen der Teile beginnen, je Liste, und wie ein Lager halten kann.


## Braucht

- [[opencivil.core.rechenwerk]]
- [[opencivil.fachwerkmodell.modell]]
- [[opencivil.fachwerkmodell.werk]]
- [[opencivil.projekt]]
- [[opencivil.projekt.fachwerkmodell]]

## Gebraucht von

- [[opencivil.web.api]]
- [[opencivil.web.dienst]]
- [[opencivil.web.zeichendaten]]
