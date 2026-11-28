---
erzeugt: 6acfd036b922
art: modul
tags: [modul]
---
> [!abstract] opencivil/web/zeichendaten.py
> was die Oberflaeche je Bauteil zeichnet, nach seiner Art.
> Paket [[opencivil.web]] · [Quelltext](../../opencivil/web/zeichendaten.py)

## VERANTWORTUNG

Je Bauteilart ([[opencivil.projekt.aufbau#Konstanten|BAUTEILE]]) die Funktion,
die aus Aufbau und Loesung die Zeichendaten eines Eintrags macht – oder
keine, wo die Bilder anders kommen: bei der Platte aus den Linien und
Kurven der Antwort und aus eigenen Anfragen, ebenso bei der
Querschnittsanalyse – sie bekommt hier nur, was sie aus einem
Balkensystem nimmt. Die
Schnittstelle legt sie unter einem Schluessel ab, `zeichendaten[kennung]`
([[opencivil.web.zeichendaten#zeichendaten|zeichendaten]]). Fehlt hier eine Art, meldet sich das beim Laden –
nicht erst als leeres Bild. Bis 2026-11-10 stand je Art ein eigener
Schluessel in der Antwort.

## Inhalt

### _balkensystem

```python
def _balkensystem(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Dict[str, Any]
```

Eben wie im Raum: die knappe Uebersicht, je Querschnitt sein Umriss und
die Achse, um die sich sein Profil biegt, und je Linie ihre Achsen, die
die Oberflaeche nicht selbst legt – auch wenn das System nicht rechnet.

### _analyse

```python
def _analyse(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Dict[str, Any]
```

Was die Kachel «Aus dem Balkensystem» vom Kern braucht – `None` ohne
System: welches gerechnet ist (die Oberflaeche zeigt es nur, solange es
das gewaehlte ist), welche Staebe sich waehlen lassen und welche zaehlen,
die Saetze, die grau dastehen, und je Stelle ihr Name, wofuer sie
massgebend ist und ihre Werte als Lastfall, in kN und kNm
([[opencivil.projekt.aufbau.aus_system|aus_system]]). Ihre Bilder holt die
Analyse anders.

### zeichendaten

```python
def zeichendaten(aufbau: Aufbau, loesung: Loesung) -> Dict[str, Any]
```

Je Bauteil, nach Kennung, seine Zeichendaten – nur fuer die Arten, die welche haben.


## Konstanten

- `ZEICHENDATEN = {PLATTE.name: None, ANALYSE.name: _analyse, BALKENSYSTEM.name: _balke…` – Je Bauteilart, nach ihrem Namen, was die Oberflaeche von einem Eintrag zeichnet – `None`: ihre Bilder kommen anders.

## Braucht

- [[opencivil.core.rechenwerk]]
- [[opencivil.projekt]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.web.balkendaten]]
- [[opencivil.web.deckendaten]]
- [[opencivil.web.durchstanzdaten]]
- [[opencivil.web.erdbebendaten]]
- [[opencivil.web.fachwerkdaten]]
- [[opencivil.web.grundbruchdaten]]
- [[opencivil.web.mauerwerkdaten]]
- [[opencivil.web.pfahldaten]]
- [[opencivil.web.setzungsdaten]]

## Gebraucht von

- [[opencivil.web.api]]
- [[opencivil.web.dienst]]
