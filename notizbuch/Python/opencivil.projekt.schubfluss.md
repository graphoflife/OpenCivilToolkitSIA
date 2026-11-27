---
erzeugt: 707206429686
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/schubfluss.py
> Schnitte und Lastfaelle des Schubflusses, wie beschrieben.
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/schubfluss.py)

## VERANTWORTUNG

Was eine Querschnittsanalyse
([[opencivil.projekt.querschnittsanalyse#QuerschnittsanalyseEintrag|QuerschnittsanalyseEintrag]])
fuer den Schubfluss braucht (Benutzer, 2026-11-27): die Schnitte
([[opencivil.projekt.schubfluss#SchnittEintrag|SchnittEintrag]]), je eine Strecke quer durch den gezeichneten
Querschnitt mit einem Pfeil zum Teil, den sie abtrennt
([[opencivil.querschnitt.abtrennen]]), und die Lastfaelle
([[opencivil.projekt.schubfluss#SchubflussfallEintrag|SchubflussfallEintrag]]), je mit N, V_z und M_y und ihrer
Rechenwahl. Gerechnet wird in [[opencivil.nachweis.qa_schubfluss]].

EINACHSIG UM y:
Ein Fall hat nur die Querkraft in z und das Moment um y, wie ein
Plattenbalken, eine Aufdopplung oder ein Verbundtraeger sie tragen. Die
Nulllinie bleibt waagrecht, wie in der Tragsicherheit «einachsig».


## KOORDINATEN UND EINHEITEN

Wie die Querschnittsanalyse: die Enden eines Schnitts als Knoten in mm,
Schnittgroessen in kN und kNm, N > 0 Zug, M_y > 0 zieht unten.

## Inhalt

### Pfeilseite

```python
class Pfeilseite(Wahl)
```

Zu welcher Seite der Strecke der Pfeil zeigt – von ihrem Anfang zu ihrem Ende gesehen.

- `LINKS = 'links'`
- `RECHTS = 'rechts'`

### SchnittEintrag

```python
@dataclass
class SchnittEintrag(Beschreibung)
```

Ein Schnitt: eine Strecke zwischen zwei Knoten, der Pfeil zeigt auf den
Teil, den sie abtrennt. Gerechnet wird mit ihm nur der Schubfluss.

- `IM_ORT = 'Schnitt'`
- `kennung: str = ''`
- `von: str = ''`
- `bis: str = ''` – Anfang und Ende als Knoten.
- `seite: Pfeilseite = Pfeilseite.LINKS`

### SchubflussfallEintrag

```python
@dataclass
class SchubflussfallEintrag(Beschreibung, JeMaterial)
```

Ein Lastfall des Schubflusses – kN und kNm. Womit gerechnet wird, waehlt
er fuer sich wie eine Spannung-Dehnung-Analyse: die Kriechzahl, je
Material den Wertesatz, je Beton die Rechenart und je Holz, wie es
rechnet ([[opencivil.projekt.eintraege#JeMaterial|JeMaterial]]).

- `IM_ORT = 'Schubfluss'`
- `name: str`
- `N_Ed: float = bereich(0.0, heisst='Normalkraft N_Ed', einheit=KN)`
- `V_z_Ed: float = bereich(0.0, heisst='Querkraft V_z,Ed', einheit=KN)`
- `M_y_Ed: float = bereich(0.0, heisst='Moment M_y,Ed', einheit=KNM)`
- `kriechzahl: float = bereich(0.0, heisst='Kriechzahl φ', ab=0.0)`
- `werkstoffsaetze: Dict[str, Werkstoffsatz] = je_material(Werkstoffsatz.BEMESSUNG)`
- `rechenarten: Dict[str, Rechenart] = je_material(Rechenart.PARABEL, FASERARTEN)`
- `holzrechnungen: Dict[str, Holzrechnung] = je_material(Holzrechnung.LINEAR)`
- `aktiv: bool = True`


## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.wahl]]
- [[opencivil.nachweis.rechenwahl]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.lesen]]
- [[opencivil.querschnitt.gesetzwahl]]

## Gebraucht von

- [[opencivil.projekt.querschnittsanalyse]]
