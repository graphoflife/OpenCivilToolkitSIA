---
erzeugt: 566f72125cb0
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/profile.py
> ein Stahlprofil, wie die Oberflaeche es beschreibt.
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/profile.py)

## VERANTWORTUNG

Der [[opencivil.projekt.profile#ProfilEintrag|ProfilEintrag]] einer Querschnittsanalyse
([[opencivil.projekt.querschnittsanalyse#QuerschnittsanalyseEintrag|QuerschnittsanalyseEintrag]]):
ein Walzprofil oder Rohr der Tabelle ([[opencivil.stahlprofile.tabelle]])
an einem Knoten, aus einem Baustahl des Projekts, gedreht und gespiegelt.
Ein Profil bleibt ein Profil (Benutzer, 2026-11-25): man waehlt Reihe und
Groesse, verschiebt und dreht es; freie Bleche zeichnet man als Flaeche aus
Baustahl. Wo es dann liegt, rechnet [[opencivil.stahlprofile.lage]].


## DER NAME

Kein Wahlfeld -- wie beim Stahlprofil des Balkensystems
([[opencivil.projekt.staebe|StabquerschnittEintrag]]), sonst zaehlte
die Meldung alle Profile auf: einen Namen, den die Tabelle nicht kennt,
meldet die Zeichnung am Profil.

## Inhalt

### ProfilEintrag

```python
@dataclass
class ProfilEintrag(Beschreibung)
```

Ein Stahlprofil an einem Knoten -- siehe Dateikopf.

- `IM_ORT = 'Profil'`
- `kennung: str = ''`
- `knoten: str = ''` – Die Mitte als Knoten: die Mitte des umschreibenden Rechtecks, nicht der Schwerpunkt.
- `profil: str = VORGABE` – Der Name in der Tabelle, «HEB 300» -- Reihe und Groesse in einem.
- `stahl: str = materialfeld('baustahl')` – Kennung des Baustahls.
- `drehung: int = einer_von(DREHUNGEN, 0)` – Um so viele Grad gegen den Uhrzeigersinn gedreht, um die Mitte -- nach dem Spiegeln.
- `gespiegelt: bool = False` – An der senkrechten Achse durch die Mitte gespiegelt: beim U der Ruecken rechts.


## Konstanten

- `VORGABE = 'IPE 300'` – Womit ein neues Profil beginnt -- dasselbe wie im Balkensystem.

## Braucht

- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.lesen]]
- [[opencivil.stahlprofile.lage]]

## Gebraucht von

- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.web.api]]
