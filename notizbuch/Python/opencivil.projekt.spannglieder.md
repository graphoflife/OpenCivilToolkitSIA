---
erzeugt: 4057c2179d71
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/spannglieder.py
> ein Spannglied, wie die Oberflaeche es beschreibt.
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/spannglieder.py)

## VERANTWORTUNG

Der [[opencivil.projekt.spannglieder#SpanngliedEintrag|SpanngliedEintrag]] einer Querschnittsanalyse
([[opencivil.projekt.querschnittsanalyse#QuerschnittsanalyseEintrag|QuerschnittsanalyseEintrag]]):
an einem Knoten, aus einem Spannstahl des Projekts, mit allem, was es
ausmacht -- Erzeugnis und Anzahl, Wirkung, Spannungen, Verbund. Alles
steht am Glied selbst, wie Durchmesser und Material beim Stab (Benutzer,
2026-11-25). Was daraus folgt, rechnet
[[opencivil.querschnitt.spannglieder]].


## DAS ERZEUGNIS

Keine freie Zahl: der Durchmesser waehlt einen Draht, eine Litze oder
einen Stab, den Tabelle 7 fuer die Sorte des Spannstahls nennt, und die
Flaeche kommt aus der Tabelle. Passt der Durchmesser nicht zur Sorte --
etwa nach dem Wechsel von Y1860 zu Y1030, das es nur in Staeben gibt --,
fehlt die Wahl noch: das Glied rechnet nicht und sagt es grau.


## DIE SPANNUNGEN

Leer gelassen, gilt die Vorgabe ([[opencivil.querschnitt.spannglieder#vorspannung|vorspannung]]):
`sigma_p0 = 0.70 f_pk`, `sigma_pinf = 0.85 sigma_p0`. Die Zahlen des
Benutzers werden nie umgedeutet; was die Norm begrenzt, sagt ein roter
Hinweis am Glied, gerechnet wird trotzdem mit ihnen.


## DIE NEIGUNG

`beta_p` in Grad, positiv, wo die lotrechte Kraft des Glieds wie ein
positives `V_z` wirkt; sie zaehlt nur mit Vordehnung. Was daraus folgt,
steht im Kopf von [[opencivil.querschnitt.spannglieder]]; dort auch,
warum sie hoechstens `GRENZE_NEIGUNG` steil sein darf.

## Inhalt

### SpanngliedEintrag

```python
@dataclass
class SpanngliedEintrag(Beschreibung)
```

Ein Spannglied an einem Knoten -- siehe Dateikopf.

- `IM_ORT = 'Spannglied'`
- `kennung: str = ''`
- `knoten: str = ''`
- `stahl: str = materialfeld('spannstahl')` – Kennung des Spannstahls.
- `durchmesser: float = bereich(DURCHMESSER, heisst='Durchmesser', einheit=MM, ueber=0.0)` – Welches Erzeugnis der Sorte -- an seinem Durchmesser erkannt (Tabelle 7).
- `anzahl: int = bereich(1, heisst='Anzahl', ab=1)` – Wie viele Draehte, Litzen oder Staebe das Glied hat.
- `wirkung: Spannwirkung = Spannwirkung.VORDEHNUNG` – Mit Vordehnung im Widerstand -- oder schlaff, weil die Vorspannung schon als Einwirkung zaehlt.
- `sigma_p0: Optional[float] = bereich(None, heisst='σ_p0', einheit=N_PRO_MM2, ueber=0.0)` – Die Spannung nach dem Spannen in N/mm² -- leer: 0.70 f_pk.
- `sigma_pinf: Optional[float] = bereich(None, heisst='σ_p∞', einheit=N_PRO_MM2, ueber=0.0, bis_feld='…` – Die Spannung nach allen Verlusten in N/mm² -- leer: 0.85 sigma_p0.
- `verbund: Verbund = Verbund.MIT`
- `neigung: float = bereich(0.0, heisst='β_p', einheit=GRAD, ab=-GRENZE_NEIGUNG, bis=GREN…` – Die Neigung gegen die Stabachse in Grad -- siehe Dateikopf.


## Konstanten

- `DURCHMESSER = 15.7` – Womit ein neues Glied beginnt: eine Litze 15.7 mm -- die verbreitetste, die Tabelle 7 fuer Y1860 nennt.

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.lesen]]
- [[opencivil.querschnitt.spannglieder]]

## Gebraucht von

- [[opencivil.projekt.aufbau.querschnittsanalyse]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.web.zeichengeometrie]]
