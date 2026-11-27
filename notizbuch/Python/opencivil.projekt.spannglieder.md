---
erzeugt: 7ba72a62daac
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
ausmacht – Erzeugnis und Anzahl oder Flaeche und Art, Wirkung, die
Faktoren der Spannungen, Verbund. Alles steht am Glied selbst, wie
Durchmesser und Material beim Stab (Benutzer, 2026-11-25). Was daraus
folgt, rechnet [[opencivil.querschnitt.spannglieder]].


## DIE FLAECHE (Benutzer, 2026-11-27)

Ein Schalter waehlt, woher sie kommt (`flaechenangabe`). Aus einem
Erzeugnis: der Durchmesser waehlt einen Draht, eine Litze oder einen Stab,
den Tabelle 7 fuer die Sorte des Spannstahls nennt, und die Flaeche kommt
aus der Tabelle, mal `anzahl`. Eingegeben: `flaeche` in mm², dazu nur
die Art, an der E_p haengt. Passt der Durchmesser oder die Art nicht zur
Sorte – etwa nach dem Wechsel von Y1860 zu Y1030, das es nur in Staeben
gibt –, fehlt die Wahl noch: das Glied rechnet nicht und sagt es grau.
Was nicht gewaehlt ist, bleibt stehen, fuer den Weg zurueck.


## DIE SPANNUNGEN (Benutzer, 2026-11-27)

Eingegeben sind Faktoren, je hoechstens 1: `sigma_p0 = anteil_p0 · f_pk`
und `sigma_pinf = anteil_pinf · sigma_p0`, Vorgabe 0.70 und 0.85. Die
Spannungen selbst stehen gerechnet daneben. Was die Norm begrenzt, sagt ein
roter Hinweis am Glied; gerechnet wird trotzdem mit den Faktoren. Bis
2026-11-27 waren `sigma_p0` und `sigma_pinf` die Felder, in N/mm².


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

Ein Spannglied an einem Knoten – siehe Dateikopf.

- `IM_ORT = 'Spannglied'`
- `kennung: str = ''`
- `knoten: str = ''`
- `stahl: str = materialfeld('spannstahl')` – Kennung des Spannstahls.
- `flaechenangabe: Flaechenangabe = Flaechenangabe.ERZEUGNIS` – Woher die Flaeche kommt – siehe Dateikopf.
- `durchmesser: float = bereich(DURCHMESSER, heisst='Durchmesser', einheit=MM, ueber=0.0)` – Welches Erzeugnis der Sorte – an seinem Durchmesser erkannt (Tabelle 7).
- `anzahl: int = bereich(1, heisst='Anzahl', ab=1)` – Wie viele Draehte, Litzen oder Staebe das Glied hat.
- `flaeche: float = bereich(FLAECHE, heisst='Fläche A_p', einheit=MM2, ueber=0.0, zeichen…` – Die Flaeche des ganzen Glieds in mm², wo sie eingegeben ist.
- `art: Erzeugnisart = Erzeugnisart.LITZE` – Draht, Litze oder Stab, wo die Flaeche eingegeben ist: daran haengt E_p.
- `wirkung: Spannwirkung = Spannwirkung.VORDEHNUNG` – Mit Vordehnung im Widerstand – oder schlaff, weil die Vorspannung schon als Einwirkung zaehlt.
- `anteil_p0: float = bereich(ANTEIL_SPANNEN, heisst='σ_p0/f_pk', ueber=0.0, bis=1.0)` – `sigma_p0 = anteil_p0 · f_pk`.
- `anteil_pinf: float = bereich(ANTEIL_NACH_VERLUSTEN, heisst='σ_p∞/σ_p0', ueber=0.0, bis=1.0)` – `sigma_pinf = anteil_pinf · sigma_p0`.
- `verbund: Verbund = Verbund.MIT`
- `neigung: float = bereich(0.0, heisst='β_p', einheit=GRAD, ab=-GRENZE_NEIGUNG, bis=GREN…` – Die Neigung gegen die Stabachse in Grad – siehe Dateikopf.


## Konstanten

- `DURCHMESSER = 15.7` – Womit ein neues Glied beginnt: eine Litze 15.7 mm – die verbreitetste, die Tabelle 7 fuer Y1860 nennt.
- `FLAECHE = erzeugnis(ERSTER_SPANNSTAHL, DURCHMESSER).flaeche` – Womit die eingegebene Flaeche beginnt: die eines Stuecks der Vorgabe, 150 mm² – wer umschaltet, sieht dasselbe Glied.

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.material.spannstahl]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.lesen]]
- [[opencivil.querschnitt.spannglieder]]

## Gebraucht von

- [[opencivil.projekt.aufbau.querschnittsanalyse]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.web.zeichengeometrie]]
