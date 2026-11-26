---
erzeugt: 4a1d7e26d7cc
art: modul
tags: [modul]
---
> [!abstract] opencivil/web/systemkatalog.py
> was die Oberflaeche an einem Balkensystem waehlen laesst.
> Paket [[opencivil.web]] · [Quelltext](../../opencivil/web/systemkatalog.py)

## VERANTWORTUNG

Der Katalog eines Balkensystems, eben und im Raum aus derselben Funktion
([[opencivil.web.systemkatalog#katalog|katalog]]): Querschnitte -- Vorlagen, Stahlprofile, Arten --,
Materialien, Lasten und ihre Richtungen, Lager und Linienlager, die
Diagramme und wie die Ergebnisse heissen. Beide haben dieselben Schluessel;
was eine Art anders hat, sagen ihre Beschreibung -- Achsen, Lagerfelder,
Linienlager, die Wahl jedes Feldes, die Einheiten der Federn --, ihre
Rechnung -- die Kennwerte von Querschnitt und Material -- und die
Darstellung ihrer Ergebnisse ([[opencivil.web.balkendaten]]). Bis
2026-11-15 stand der Katalog des 2D-Balkensystems in [[opencivil.web.api]].

## Inhalt

### _zeichen

```python
def _zeichen(feld: str) -> str
```

Wie eine Richtung eines Lagers heisst: `x`, `φ`, `φ_y`.

### _lastart

```python
def _lastart(art: Lastart) -> Dict[str, Any]
```

Eine Art einer Last auf einem Stab: wie sie heisst, ob sie verteilt liegt, ob sie eine Kraft ist, ihre Einheit.

### katalog

```python
def katalog(eintrag: type, rechnung: type, darstellung: Darstellung) -> Dict[str, Any]
```

Der Katalog einer Art von Balkensystem: `eintrag` ihre Beschreibung
(eine [[opencivil.projekt.staebe#MitStaeben|MitStaeben]]), `rechnung` die
Klasse, die sie rechnet, `darstellung` wie ihre Ergebnisse gezeigt werden.


## Konstanten

- `_DIAGRAMME = {'M': ('M', 'Moment M', 'M', 'z'), 'V': ('V', 'Querkraft V', 'V', 'z'…` – Wie ein Diagramm heisst -- kurz im Schalter, lang ueber dem Diagramm --, welches Feld der Proben es zeigt und zu welcher Achse des Stabs ein positiver Wert aufgetragen wird: zur Faser, an der ein positives Moment zieht, die Querkraft wie ihr Moment. Ohne Achse die, die im Bild laenger ist -- bei N und T gibt es keine Seite.
- `_LINIENLAGER = {'quer': ('Lager quer', 'quer', '⊥', 'Quer zur Linie, auf der Seite d…` – Wie ein Linienlager heisst -- im Fenster, kurz in der Liste, als Zeichen seiner Bettung --, was sein Schalter erklaert und in welcher Achse des Stabs es haelt: quer in der Ebene zur gestrichelten Faser, in z.

## Braucht

- [[opencivil.projekt.balkensystem]]
- [[opencivil.projekt.lesen]]
- [[opencivil.projekt.staebe]]
- [[opencivil.stabwerk.modell]]
- [[opencivil.stabwerk.querschnitte]]
- [[opencivil.stabwerk.rechnung]]
- [[opencivil.web.balkendaten]]

## Gebraucht von

- [[opencivil.web.api]]
