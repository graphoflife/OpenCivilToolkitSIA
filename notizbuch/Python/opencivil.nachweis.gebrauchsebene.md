---
erzeugt: 6ee73fa111e1
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/gebrauchsebene.py
> die Dehnungsebene des gezeichneten Querschnitts unter Gebrauchslast.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/gebrauchsebene.py)

## VERANTWORTUNG

Ein Lastfall traegt N, M_y und M_z; gesucht ist die Ebene, die alle drei
haelt -- am Querschnitt mit den Gesetzen einer Rechenwahl, fuer die
Stahlspannungen und die Zwaengung auf Biegung
([[opencivil.nachweis.qa_gebrauch]]).


## DIE SUCHE

Zu einer Neigung ψ der Zugrichtung ist es die Aufgabe der Platte: N und das
Moment in Zugrichtung bestimmen `eps_m` und `chi`
([[opencivil.nachweis.querschnittsloeser#FaserloeserIllinois|FaserloeserIllinois]]).
Uebrig bleibt das Moment entlang der Nulllinie, und ψ wird gedreht, bis auch
es stimmt ([[opencivil.nachweis.gebrauchsebene#gebrauchsebene|gebrauchsebene]]): der Sekante nach, dann Illinois, und wo
die Sekante wegliefe, mit wachsenden Schritten nach beiden Seiten
eingegrenzt. Bei einem symmetrischen Querschnitt trifft schon die Neigung,
die zum Moment gehoert. Einachsig bleibt die Nulllinie waagrecht, und M_z
zaehlt nicht -- wie in der Tragsicherheit.


## WAS ES KOSTET

Jede Neigung ist eine ganze Suche ueber die Fasern. Halbiert brauchte die
schiefe Biegung am Unterzug des Beispiels zwanzig Neigungen zu je 85 ms;
mit Sekante und Illinois sind es eine Handvoll zu je wenigen ms.


## EINHEITEN

SI-Basis.

## Inhalt

### Gebrauchsebene

```python
@dataclass(frozen=True)
class Gebrauchsebene
```

Die Dehnungsebene zu einem Lastfall -- und was sie erzeugt.

- `psi: float` – Neigung der Zugrichtung, wie [[opencivil.querschnitt.interaktion#Querschnitt|Querschnitt]] sie nimmt.
- `eps_m: float` – Dehnung im Schwerpunkt.
- `chi: float` – Kruemmung in Zugrichtung, 1/m.
- `N: float`
- `M_y: float`
- `M_z: float` – Was die Ebene erzeugt -- die Probe.
- `eps_s: Tuple[float, ...]`
- `sigma_s: Tuple[float, ...]` – Dehnung und Spannung je Bewehrung des Querschnitts.
- `konvergiert: bool = True`

### _bei_neigung

```python
def _bei_neigung(q: Querschnitt, psi: float, N: float, M_y: float, M_z: float) -> Optional[Tuple[Gebrauchsebene, float]]
```

Die Ebene bei dieser Neigung, die N und das Moment in Zugrichtung traegt
-- und was ihr am Moment entlang der Nulllinie noch fehlt. Mit
`M = -(n_z·M_y + n_y·M_z)` und `M_quer = -(n_y·M_y - n_z·M_z)`, den
Umkehrungen von [[opencivil.querschnitt.interaktion#Richtung.momente|momente]].

### gebrauchsebene

```python
def gebrauchsebene(q: Querschnitt, *, N: float, M_y: float, M_z: float, einachsig: bool, start: Optional[float]=None) -> Gebrauchsebene
```

Die Dehnungsebene, die `N`, `M_y` und `M_z` im Gleichgewicht haelt.

Einachsig mit waagrechter Nulllinie, `M_z` zaehlt nicht. Sonst wird die
Neigung gesucht, bei der auch das Moment entlang der Nulllinie stimmt --
von `start` aus oder von der, die bei Symmetrie gaelte; bei einem
symmetrischen Querschnitt trifft schon sie. Sonst der Sekante nach, bis
die Abweichung das Vorzeichen wechselt, dann Illinois. Laeuft die Sekante
weg, wird nach beiden Seiten mit wachsenden Schritten eingegrenzt
([[opencivil.nachweis.gebrauchsebene#Konstanten|NEIGUNGSSCHRITTE]]), wie beim Widerstand in einer Momentenrichtung
([[opencivil.querschnitt.interaktion#Querschnitt.in_richtung|in_richtung]]).

### protokoll_ebene

```python
def protokoll_ebene(p: Protokoll, werte: Zwischenwerte, ebene: Gebrauchsebene, einachsig: bool) -> None
```

Die gefundene Ebene und ihre Probe.


## Konstanten

- `NEIGUNGSSCHRITTE = (2.0, 5.0, 10.0, 20.0, 35.0, 55.0, 75.0, 90.0)` – Wie weit sich die Neigung ψ der Ebene unter Gebrauchslast von der entfernen darf, die bei Symmetrie gaelte -- nach jeder Seite, in Grad. Weiter als 90° laege die Gegenrichtung, und die gehoert zur negativen Kruemmung.
- `QUER_SCHRANKE = 1e-07` – Wann das Moment entlang der Nulllinie als getroffen gilt, als Teil der groessten Schnittgroesse -- N mit einem Hebel von einem Meter gezaehlt.
- `KEINE = Gebrauchsebene(psi=0.0, eps_m=0.0, chi=0.0, N=0.0, M_y=0.0, M_z=0.0, …` – Wenn sich keine Ebene findet.
- `SUCHE_DER_EBENE = 'Gesucht wird die Ebene, die N, M_y und M_z zugleich trägt. Zu einer …` – Wie die Ebene unter Gebrauchslast gefunden wird -- bei schiefer Biegung.
- `EINACHSIG = 'Einachsig bleibt die Nulllinie waagrecht, und M_z zählt nicht – wie …` – Dasselbe, einachsig.

## Braucht

- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.nachweis.querschnittsloeser]]
- [[opencivil.querschnitt.interaktion]]

## Gebraucht von

- [[opencivil.nachweis.qa_gebrauch]]
