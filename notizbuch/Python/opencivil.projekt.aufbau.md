---
erzeugt: c2697c85d6ae
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/aufbau/__init__.py
> aus der Beschreibung ein Rechenwerk.
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/aufbau/__init__.py)

## VERANTWORTUNG

[[opencivil.projekt.aufbau#aufbauen|aufbauen]] macht aus einem [[opencivil.projekt.projekt#Projekt|Projekt]] Baustoffe, Querschnitte,
Nachweise, Balkensysteme und Decken und meldet sie in einem [[opencivil.core.rechenwerk#Rechenwerk|Rechenwerk]] an.
Heraus kommt ein [[opencivil.projekt.aufbau.kern#Aufbau|Aufbau]] -- das Werk samt allen Nachweisobjekten und
Systemen, nach Bauteil und Art abgelegt, damit Schnittstelle,
Zwischenspeicher und Bewehrungssuche sie wiederfinden.

Die Beschreibung selbst rechnet nichts; hier wird sie zum ersten Mal
Rechnung. Darum stehen auch die Pruefungen hier, die erst beim Bauen
auffallen koennen -- ein Verweis auf ein geloeschtes Material, eine Platte
ohne Bewehrung.


## DIE BAUTEILARTEN

Platte, Querschnittsanalyse, Balkensystem, Decke, Durchstanzen, Grundbruch und Setzung
haben je einen Steckbrief
([[opencivil.projekt.aufbau#Bauteilart|Bauteilart]]) in [[opencivil.projekt.aufbau#Konstanten|BAUTEILE]] -- Liste in der Datei, Klasse der
Eintraege, Vorsilbe der Kennungen, Namensraum, Baufunktion. Wer alle
Bauteile durchgeht, geht diese Liste durch. Gebaut wird je Eintrag ein
[[opencivil.projekt.aufbau.kern#Bauteil|Bauteil]], das seine Nachweise, Ziele und Bezuege selbst fuehrt.

Was Bericht und Oberflaeche je Art brauchen, kennt der Kern nicht; es steht
in ihren Schichten, je an einer Stelle: was ueber der Nachweistabelle steht
([[opencivil.bericht.zusammenfassung#Konstanten|ANGABEN]]), was gezeichnet wird
([[opencivil.web.zeichendaten#Konstanten|ZEICHENDATEN]]), in der Oberflaeche ihr
Eintrag in arten.js und ihre Zeile in apps.js mit Editor und Karten. Fehlt
eine neue Art dort, meldet es sich -- beim Laden oder in
tests/test_bauteilarten.py; ihre Vorlage im Katalog entsteht von selbst.


## WO WAS STEHT

Hier der Steckbrief, die Liste der Arten und [[opencivil.projekt.aufbau#aufbauen|aufbauen]], das sie
durchgeht. Je Art ein Modul mit ihrer Baufunktion `bauen`
([[opencivil.projekt.aufbau.platte|platte]],
[[opencivil.projekt.aufbau.querschnittsanalyse|querschnittsanalyse]],
[[opencivil.projekt.aufbau.balkensystem|balkensystem]],
[[opencivil.projekt.aufbau.decke|decke]],
[[opencivil.projekt.aufbau.durchstanzen|durchstanzen]],
[[opencivil.projekt.aufbau.grundbruch|grundbruch]],
[[opencivil.projekt.aufbau.setzung|setzung]]); was mehr als eine braucht, im
Kern ([[opencivil.projekt.aufbau.kern|kern]]): der Aufbau, das Bauteil, die
Baustoffe, die Stahlspannungen und der Knickfall. Bis 2026-10-17 stand alles
in einer Datei von ueber tausend Zeilen.

## Module

- [[opencivil.projekt.aufbau.balkensystem]] – ein Balkensystem wird Rechnung.
- [[opencivil.projekt.aufbau.decke]] – eine Decke wird Rechnung.
- [[opencivil.projekt.aufbau.durchstanzen]] – eine Durchstanzstelle wird Rechnung.
- [[opencivil.projekt.aufbau.faelle]] – was Balkensystem und Decke an Faellen gleich pruefen.
- [[opencivil.projekt.aufbau.grundbruch]] – ein Fundament wird Rechnung.
- [[opencivil.projekt.aufbau.kern]] – was alle Bauteilarten beim Bauen teilen.
- [[opencivil.projekt.aufbau.platte]] – eine Platte wird Rechnung.
- [[opencivil.projekt.aufbau.querschnittsanalyse]] – ein gezeichneter Querschnitt wird Rechnung.
- [[opencivil.projekt.aufbau.setzung]] – eine Setzungsberechnung wird Rechnung.

## Inhalt

### aufbauen

```python
def aufbauen(projekt: 'Projekt', *, schnell: bool=False) -> Aufbau
```

Baut aus der Beschreibung ein vollstaendiges Rechenwerk.

Wirft [[opencivil.projekt.lesen#ProjektFehler|ProjektFehler]], wenn die
Beschreibung nicht stimmig ist -- etwa wenn ein Querschnitt auf ein
geloeschtes Material verweist.

Mit `schnell` lassen Nachweise teure Nebenrechnungen weg, die das
Urteil nicht aendern -- die Suche nach der Knickgrenzkraft und die
genaue Resistenzlinie --, und ganz stille Nachweise entstehen gar
nicht erst. Gedacht fuer das Bewehrungswerkzeug, das hundertfach
rechnet und nur wissen muss, ob es aufgeht. Fuer eine Herleitung ist
das nichts: dort soll die Zahl stehen, die auch in der Tabelle steht.

### Bauteilart

```python
@dataclass(frozen=True)
class Bauteilart
```

Der Steckbrief einer Bauteilart: was der Kern ausserhalb ihres Eintrags
und ihrer Baufunktion von ihr wissen muss. Eine neue Art kommt in
[[opencivil.projekt.aufbau#Konstanten|BAUTEILE]] dazu -- und in die Verzeichnisse von Bericht und
Oberflaeche, siehe Dateikopf.

- `name: str` – Wie sie im Aufbau, im Bericht und in der Oberflaeche heisst: `platte`.
- `liste: str` – Ihre Liste im [[opencivil.projekt.projekt#Projekt|Projekt]] und in der Datei: `querschnitte`.
- `eintrag: type` – Die Klasse ihrer Eintraege -- sie liest einen Eintrag aus der Datei.
- `vorsilbe: str` – Womit ihre Kennungen beginnen: `q` fuer q1, q2 ...
- `raum: str` – Womit ihre Namensraeume beginnen: `querschnitt` fuer querschnitt.q1.
- `bereich: str` – Wie ihr Abschnitt in der Formelsammlung heisst.
- `bauen: Callable[['Bauteilart', Any, Aufbau], Optional[Bauteil]]` – Aus dem Eintrag das Bauteil -- Objekt und Nachweise, angemeldet im Werk. `None`, wo es nichts zu rechnen gibt: eine Querschnittsanalyse, in der noch nichts gezeichnet ist.


## Konstanten

- `PLATTE = Bauteilart('platte', 'querschnitte', QuerschnittEintrag, 'q', 'quersc…`
- `ANALYSE = Bauteilart('querschnittsanalyse', 'querschnittsanalysen', Querschnitt…`
- `BALKENSYSTEM = Bauteilart('balkensystem', 'balkensysteme', BalkensystemEintrag, 'r',…`
- `DECKE = Bauteilart('decke', 'decken', DeckeEintrag, 'e', 'decke', 'Decken', d…` – Die Kennungen e1, e2 ...: «d» tragen schon die Durchstanzstellen.
- `GRUNDBRUCH = Bauteilart('grundbruch', 'grundbrueche', GrundbruchEintrag, 'g', 'gru…`
- `SETZUNG = Bauteilart('setzung', 'setzungen', SetzungEintrag, 'w', 'setzung', 'S…` – Die Kennungen w1, w2 ...: «s» tragen schon die Betonstaehle.
- `DURCHSTANZEN = Bauteilart('durchstanzen', 'durchstanzstellen', DurchstanzEintrag, 'd…`
- `BAUTEILE = (PLATTE, ANALYSE, BALKENSYSTEM, DECKE, DURCHSTANZEN, GRUNDBRUCH, SETZ…` – Die Bauteilarten, in der Reihenfolge von Baum, Bericht und Rechnung -- ein Balkensystem liest Werte der Platten und Analysen, also kommt es nach ihnen; Decke, Durchstanzen, Grundbruch und Setzung lesen nichts von den anderen. Wer alle Bauteile durchgeht (Lesen, Kennungen, Aufbau, Zwischenspeicher, Erkennen einer Datei), geht diese Liste durch.

## Braucht

- [[opencivil.core.rechenwerk]]
- [[opencivil.projekt.aufbau.balkensystem]]
- [[opencivil.projekt.aufbau.decke]]
- [[opencivil.projekt.aufbau.durchstanzen]]
- [[opencivil.projekt.aufbau.grundbruch]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.aufbau.platte]]
- [[opencivil.projekt.aufbau.querschnittsanalyse]]
- [[opencivil.projekt.aufbau.setzung]]
- [[opencivil.projekt.balkensystem]]
- [[opencivil.projekt.decke]]
- [[opencivil.projekt.durchstanzen]]
- [[opencivil.projekt.grundbruch]]
- [[opencivil.projekt.platte]]
- [[opencivil.projekt.projekt]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.projekt.setzung]]

## Gebraucht von

- [[opencivil.notizbuch.formelseiten]]
- [[opencivil.projekt]]
- [[opencivil.projekt.aufbau.balkensystem]]
- [[opencivil.projekt.aufbau.decke]]
- [[opencivil.projekt.aufbau.durchstanzen]]
- [[opencivil.projekt.aufbau.grundbruch]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.aufbau.platte]]
- [[opencivil.projekt.aufbau.querschnittsanalyse]]
- [[opencivil.projekt.aufbau.setzung]]
- [[opencivil.projekt.projekt]]
- [[opencivil.web.zeichendaten]]
