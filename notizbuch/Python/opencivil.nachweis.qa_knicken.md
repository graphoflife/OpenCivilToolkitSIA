---
erzeugt: dff3a524600b
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/qa_knicken.py
> Knicken am gezeichneten Querschnitt.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/qa_knicken.py)

## VERANTWORTUNG

Der Knicknachweis der Platte am gezeichneten Querschnitt, je Knickfall in
einer Richtung: der Zugseite, zu der sich der Stab biegt -- unten, oben,
links oder rechts, wie bei den Spannung-Dehnung-Analysen
([[opencivil.querschnitt.zugseite#Zugseite|Zugseite]]). Das Verfahren ist
dasselbe ([[opencivil.nachweis.knicken#Knickverfahren|Knickverfahren]]: Ausmitten-
Iteration, Grenzkraft N_Rd); hier steht nur, woher der Stab kommt
([[opencivil.nachweis.knicken#Knickstab|Knickstab]]):

* die Verformung aus den Fasern in dieser Richtung, mit den Gesetzen der
  Wahl «Verformung» ([[opencivil.querschnitt.analyse#Querschnittsanalyse.querschnitt|querschnitt]]);
* der Widerstand aus dem Bruchzustand bei der Druckkraft in dieser Richtung,
  mit den Gesetzen der Wahl «Widerstand» -- das Moment in Biegerichtung;
* die statische Hoehe vom gedrueckten Rand bis zum entferntesten Stab in
  Zugrichtung, fuer die Mindestausmitte `d/30`.


## DIE NULLLINIE BLEIBT PARALLEL ZUR ACHSE

wie in der einachsigen Tragsicherheit und den Analysen. Das Moment um die
andere Achse, das ein unsymmetrischer Querschnitt dabei weckt, zaehlt nicht;
um beide Achsen zugleich knickt hier kein Stab -- je Richtung ein Fall.
Nach Vorgabe, nicht nachgeschlagen (`notizbuch/Notizen/TODO.md`).


## WAS ES KOSTET

Jede Probekraft der Suche nach N_Rd ist eine ganze Ausmitten-Iteration, jede
Iteration ein paar Ebenen. Gesucht werden sie mit Illinois, von der
zuletzt gefundenen Ebene aus ([[opencivil.core.suche#Konstanten|ILLINOIS]]), wie
das Knicken der Platte.


## EINHEITEN

SI-Basis; die Zeichnung in mm.

## Inhalt

### QAKnickfall

```python
@dataclass(frozen=True)
class QAKnickfall(Knickfall)
```

Ein Knickfall des gezeichneten Querschnitts -- mit der Seite, zu der er sich biegt.

- `richtung: Zugseite = Zugseite.UNTEN`

### knickstab

```python
def knickstab(verformung: Querschnitt, widerstand: Querschnitt, seite: Zugseite) -> Knickstab
```

Der Stab in einer Richtung: die Fasern des einen Querschnitts fuer die
Verformung, der Bruchzustand des anderen fuer den Widerstand.

### KnickenQA

```python
class KnickenQA(Knickverfahren)
```

Nachweis am verformten System, je Knickfall in seiner Richtung.

#### KnickenQA.pruefe

```python
def pruefe(self, e: Eingaben, p: Protokoll)
```


## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.suche]]
- [[opencivil.nachweis.knicken]]
- [[opencivil.nachweis.querschnittsloeser]]
- [[opencivil.nachweis.rechenwahl]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.gesetzwahl]]
- [[opencivil.querschnitt.interaktion]]
- [[opencivil.querschnitt.zugseite]]

## Gebraucht von

- [[opencivil.projekt.aufbau.querschnittsanalyse]]
