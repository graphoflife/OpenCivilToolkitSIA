---
erzeugt: 484ea3a2274f
art: modul
tags: [modul]
---
> [!abstract] opencivil/web/zeichendaten.py
> was die Oberflaeche je Bauteil zeichnet, nach seiner Art.
> Paket [[opencivil.web]] · [Quelltext](../../opencivil/web/zeichendaten.py)

## VERANTWORTUNG

Je Bauteilart ([[opencivil.projekt.aufbau#Konstanten|BAUTEILE]]) die Funktion,
die aus Aufbau und Loesung die Zeichendaten eines Eintrags macht -- oder
keine, wo die Bilder anders kommen: bei Platte und Querschnittsanalyse aus
den Linien und Kurven der Antwort und aus eigenen Anfragen. Die
Schnittstelle legt sie unter einem Schluessel ab, `zeichendaten[kennung]`
([[opencivil.web.zeichendaten#zeichendaten|zeichendaten]]). Fehlt hier eine Art, meldet sich das beim Laden --
nicht erst als leeres Bild. Bis 2026-11-10 stand je Art ein eigener
Schluessel in der Antwort.

## Inhalt

### _balkensystem

```python
def _balkensystem(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Dict[str, Any]
```

Die knappe Uebersicht und je Querschnitt sein Umriss -- auch wenn das System nicht rechnet.

### zeichendaten

```python
def zeichendaten(aufbau: Aufbau, loesung: Loesung) -> Dict[str, Any]
```

Je Bauteil, nach Kennung, seine Zeichendaten -- nur fuer die Arten, die welche haben.


## Konstanten

- `ZEICHENDATEN = {PLATTE.name: None, ANALYSE.name: None, BALKENSYSTEM.name: _balkensys…` – Je Bauteilart, nach ihrem Namen, was die Oberflaeche von einem Eintrag zeichnet -- `None`: ihre Bilder kommen anders.

## Braucht

- [[opencivil.core.rechenwerk]]
- [[opencivil.projekt]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.web.balkendaten]]
- [[opencivil.web.durchstanzdaten]]
- [[opencivil.web.grundbruchdaten]]
- [[opencivil.web.setzungsdaten]]

## Gebraucht von

- [[opencivil.web.api]]
