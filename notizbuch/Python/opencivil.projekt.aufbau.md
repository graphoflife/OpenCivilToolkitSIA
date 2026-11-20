---
erzeugt: 726e1605d2e0
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

Platte, Querschnittsanalyse, 2D- und 3D-Balkensystem, Decke, Durchstanzen, Grundbruch,
Setzung und Pfahl haben je einen Steckbrief
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
[[opencivil.projekt.aufbau.balkensystem3d|balkensystem3d]],
[[opencivil.projekt.aufbau.decke|decke]],
[[opencivil.projekt.aufbau.durchstanzen|durchstanzen]],
[[opencivil.projekt.aufbau.grundbruch|grundbruch]],
[[opencivil.projekt.aufbau.setzung|setzung]],
[[opencivil.projekt.aufbau.pfahl|pfahl]]); was mehr als eine braucht, im
Kern ([[opencivil.projekt.aufbau.kern|kern]]): der Aufbau, das Bauteil, die
Baustoffe, die Stahlspannungen und der Knickfall. Bis 2026-10-17 stand alles
in einer Datei von ueber tausend Zeilen.

## Module

- [[opencivil.projekt.aufbau.balkensystem]] – ein Balkensystem wird Rechnung.
- [[opencivil.projekt.aufbau.balkensystem3d]] – ein 3D-Balkensystem wird Rechnung.
- [[opencivil.projekt.aufbau.decke]] – eine Decke wird Rechnung.
- [[opencivil.projekt.aufbau.durchstanzen]] – eine Durchstanzstelle wird Rechnung.
- [[opencivil.projekt.aufbau.faelle]] – was Balkensystem und Decke an Faellen gleich pruefen.
- [[opencivil.projekt.aufbau.grundbruch]] – ein Fundament wird Rechnung.
- [[opencivil.projekt.aufbau.kern]] – was alle Bauteilarten beim Bauen teilen.
- [[opencivil.projekt.aufbau.pfahl]] – ein Pfahl wird Rechnung.
- [[opencivil.projekt.aufbau.platte]] – eine Platte wird Rechnung.
- [[opencivil.projekt.aufbau.querschnittsanalyse]] – ein gezeichneter Querschnitt wird Rechnung.
- [[opencivil.projekt.aufbau.setzung]] – eine Setzungsberechnung wird Rechnung.

## Inhalt

### aufbauen

```python
def aufbauen(projekt: 'Projekt', *, schnell: bool=False) -> Aufbau
```

Baut aus der Beschreibung ein vollstaendiges Rechenwerk.

Wirft [[opencivil.projekt.lesen#ProjektFehler|ProjektFehler]], wenn die Form
der Beschreibung nicht stimmt oder was alle teilen -- zwei Materialien
mit demselben Namen. Was nur ein Material oder ein Bauteil betrifft,
haelt nur dieses an ([[opencivil.projekt.aufbau.kern#Aufbau.unfertig|Aufbau.unfertig]]): ein Wert, den der Kern
abweist, ein Verweis auf ein Material, das es nicht mehr gibt oder das
selbst nicht rechnet, alles, was beim Bauen eines Bauteils scheitert
(Benutzer, 2026-11-19: der Rest rechnet weiter).

Mit `schnell` lassen Nachweise teure Nebenrechnungen weg, die das
Urteil nicht aendern -- die Suche nach der Knickgrenzkraft und die
genaue Resistenzlinie --, und ganz stille Nachweise entstehen gar
nicht erst. Gedacht fuer das Bewehrungswerkzeug, das hundertfach
rechnet und nur wissen muss, ob es aufgeht. Fuer eine Herleitung ist
das nichts: dort soll die Zahl stehen, die auch in der Tabelle steht.

### _vorab_pruefen

```python
def _vorab_pruefen(eintrag: Any, wo: str, aufbau: Aufbau) -> None
```

Was ein Bauteil aufhaelt, bevor es gebaut wird: ein Material, das selbst
nicht rechnet, und ein Wert, den der Kern abweist
([[opencivil.projekt.lesen#inhalt_pruefen|inhalt_pruefen]]). Ein Verweis auf ein
Material, das es nicht mehr gibt, meldet sich beim Bauen, mit dem, was
darauf zeigt ([[opencivil.projekt.aufbau.kern#material|material]]).

Bis 2026-11-19 hielt jedes davon das ganze Projekt an -- auch einen
Verweis ins Leere erreichte die Bedienung: der Beton eines Pfahls, der
als Mikropfahl keinen braucht und darum loeschen liess.

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
- `bauen: Callable[['Bauteilart', Any, Aufbau], Bauteil]` – Aus dem Eintrag das Bauteil -- Objekt und Nachweise, angemeldet im Werk. Wo es nichts zu rechnen gibt, wirft sie einen [[opencivil.projekt.lesen#ProjektFehler|ProjektFehler]] mit dem Grund: eine Querschnittsanalyse, in der noch nichts gezeichnet ist. Bis 2026-11-20 gaben drei Baufunktionen dafuer `None` zurueck.


## Konstanten

- `PLATTE = Bauteilart('platte', 'querschnitte', QuerschnittEintrag, 'q', 'quersc…`
- `ANALYSE = Bauteilart('querschnittsanalyse', 'querschnittsanalysen', Querschnitt…`
- `BALKENSYSTEM = Bauteilart('balkensystem', 'balkensysteme', BalkensystemEintrag, 'r',…`
- `BALKENSYSTEM3D = Bauteilart('balkensystem3d', 'balkensysteme3d', Balkensystem3dEintrag…` – Die Kennungen u1, u2 ...: «r» tragen die Rahmen in der Ebene.
- `DECKE = Bauteilart('decke', 'decken', DeckeEintrag, 'e', 'decke', 'Decken', d…` – Die Kennungen e1, e2 ...: «d» tragen schon die Durchstanzstellen.
- `GRUNDBRUCH = Bauteilart('grundbruch', 'grundbrueche', GrundbruchEintrag, 'g', 'gru…`
- `SETZUNG = Bauteilart('setzung', 'setzungen', SetzungEintrag, 'w', 'setzung', 'S…` – Die Kennungen w1, w2 ...: «s» tragen schon die Betonstaehle.
- `DURCHSTANZEN = Bauteilart('durchstanzen', 'durchstanzstellen', DurchstanzEintrag, 'd…`
- `PFAHL = Bauteilart('pfahl', 'pfaehle', PfahlEintrag, 't', 'pfahl', 'Pfähle', …` – Die Kennungen t1, t2 ...: «p» tragen schon die Skripte.
- `BAUTEILE = (PLATTE, ANALYSE, BALKENSYSTEM, BALKENSYSTEM3D, DECKE, DURCHSTANZEN, …` – Die Bauteilarten, in der Reihenfolge von Baum, Bericht und Rechnung -- ein Balkensystem liest Werte der Platten und Analysen, also kommt es nach ihnen; Decke, Durchstanzen, Grundbruch, Setzung und Pfahl lesen nichts von den anderen. Wer alle Bauteile durchgeht (Lesen, Kennungen, Aufbau, Zwischenspeicher, Erkennen einer Datei), geht diese Liste durch.

## Braucht

- [[opencivil.core.rechenwerk]]
- [[opencivil.projekt.aufbau.balkensystem]]
- [[opencivil.projekt.aufbau.balkensystem3d]]
- [[opencivil.projekt.aufbau.decke]]
- [[opencivil.projekt.aufbau.durchstanzen]]
- [[opencivil.projekt.aufbau.grundbruch]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.aufbau.pfahl]]
- [[opencivil.projekt.aufbau.platte]]
- [[opencivil.projekt.aufbau.querschnittsanalyse]]
- [[opencivil.projekt.aufbau.setzung]]
- [[opencivil.projekt.balkensystem]]
- [[opencivil.projekt.balkensystem3d]]
- [[opencivil.projekt.decke]]
- [[opencivil.projekt.durchstanzen]]
- [[opencivil.projekt.grundbruch]]
- [[opencivil.projekt.lesen]]
- [[opencivil.projekt.pfahl]]
- [[opencivil.projekt.platte]]
- [[opencivil.projekt.projekt]]
- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.projekt.setzung]]

## Gebraucht von

- [[opencivil.notizbuch.formelseiten]]
- [[opencivil.projekt]]
- [[opencivil.projekt.aufbau.balkensystem]]
- [[opencivil.projekt.aufbau.balkensystem3d]]
- [[opencivil.projekt.aufbau.decke]]
- [[opencivil.projekt.aufbau.durchstanzen]]
- [[opencivil.projekt.aufbau.grundbruch]]
- [[opencivil.projekt.aufbau.kern]]
- [[opencivil.projekt.aufbau.pfahl]]
- [[opencivil.projekt.aufbau.platte]]
- [[opencivil.projekt.aufbau.querschnittsanalyse]]
- [[opencivil.projekt.aufbau.setzung]]
- [[opencivil.projekt.mappe]]
- [[opencivil.projekt.projekt]]
- [[opencivil.web.zeichendaten]]
