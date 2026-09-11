# Entwicklungsprotokoll

Was gebaut wurde, und vor allem **warum es so gebaut ist**. Das Was steht im
Code; das Warum geht sonst verloren. Neueste Einträge oben.

Wer das Werkzeug bloss benutzen will, liest [README.md](README.md).

---

## Aufbau in einem Bild

```
                   ┌───────────────────────────────────┐
                   │  opencivil/  –  der Rechenkern    │
                   │  Einheiten · Rechenwerk · SIA     │
                   └──────────────┬────────────────────┘
                                  │
                   ┌──────────────▼────────────────────┐
                   │  opencivil/web/dienst.py          │
                   │  dict rein, dict raus.            │
                   │  Kein HTTP, keine Platte,         │
                   │  kein Unterprozess.               │
                   └────────┬─────────────────┬────────┘
                            │                 │
              ┌─────────────▼──────┐   ┌──────▼───────────────┐
              │ web/server.py      │   │ web/js/kern.js       │
              │ HTTP, CPython      │   │ Pyodide im Browser   │
              │ kann zusätzlich    │   │ lädt die .py-Dateien │
              │ PDF übersetzen     │   │ übers Netz nach      │
              └─────────────┬──────┘   └──────┬───────────────┘
                            │                 │
                   ┌────────▼─────────────────▼────────┐
                   │  web/js/api.js  –  wählt den Weg  │
                   └──────────────┬────────────────────┘
                                  │
                   ┌──────────────▼────────────────────┐
                   │  Oberfläche. Rechnet nichts.      │
                   └───────────────────────────────────┘
```

Der Knackpunkt ist die zweite Kiste. Alles darunter ist Transport, alles
darüber ist Darstellung. Gerechnet wird an genau einer Stelle.

---

## 2026-09-11 · Drei Befunde aus dem Code-Review

Eine strenge Durchsicht des eigenen Arbeitsstands. Alle drei Befunde waren
derselbe Fehler in drei Gewändern: **ein Begriff, mehrfach kodiert**.

### 1. Die Achse war vier Schreibweisen

Ob waagrecht (Momentenwiderstand bei festgehaltener Normalkraft) oder senkrecht
gemessen wird, stand vierfach da:

| Ort | Schreibweise |
| --- | --- |
| `linie.py` | zwei Funktionspaare `..._bei_N` / `..._bei_M` |
| `linie.py` | `positiv: bool` |
| `Auswertung` | `groesse: str` = `"M"` \| `"N"` |
| `Erfuellungsart` | `NORMALKRAFT_KONSTANT` \| `MOMENT_KONSTANT` |

Abgefragt an sechs Stellen. Wer eine dritte Messart hinzufügt, muss vier
Notationen treffen; eine vergessene ist stumm falsch.

Jetzt gibt es `linie.Achse` — sie kennt ihren Feldnamen (zugleich der Feldname
eines Punktes, daher kommt `von()` ohne Fallunterscheidung aus), ihre Einheit,
ihre Gegenachse und ihr Wort. Letzteres ausgeschrieben, weil die deutsche
Fugenform sich nicht anhängen lässt: *Momentenwiderstand*, nicht
*Momentswiderstand* — das hat prompt ein Test gefangen.

Der eigentliche Zug war, **die Einwirkung als Punkt derselben Ebene zu lesen**.
Damit wird aus zwei gespiegelten Methoden eine:

```python
ed = geo.Stelle(N=..., M=...)
fest = achse.gegen.von(ed)      # was festgehalten wird
gesucht = achse.von(ed)         # was verglichen wird
```

Netto 55 Zeilen weniger. Nebenbei fiel der doppelte Minus (`− −6000.0`) weg —
an *einer* Stelle statt zwei, weil es die zweite nicht mehr gibt.

### 2. Die präzise Linie sass in der falschen Klasse

Seit das Urteil über die Handrechnung fällt, ist die aus Dehnungsebenen
aufgebaute Linie kein Teil des Nachweises mehr — sie wird gerechnet, nicht
hergeleitet. Sie sass trotzdem mitten in `BiegungNormalkraft`:
Faserintegration, Fächeraufbau, `Linienpunkt`, 90 Zeilen stillgelegte
Mitschrift. Vier Zuständigkeiten in einer Klasse.

Alles nach `dehnungsfaecher.py`. Der Nachweis hängt nur noch an einer Zeile:

```python
self.linie = dehnungsfaecher.aufbauen(h=…, b=…, lagen=…, beton=…)
```

844 → 600 Zeilen, und die Klasse handelt von einer Sache. Der stillgelegte
Block bleibt vollständig, jetzt aber neben dem Code, zu dem er gehört.

### 3. Fünf Filter für eine Frage

„Gehört das zum gewählten Bestandteil?" wurde in `bericht.js` fünfmal gefragt,
jede Sicht mit einem anderen Schlüssel — und nur eine benutzte
`raumDerAuswahl()`, den kanonischen Weg, den es längst gab.

Schlimmer: die Herleitung verglich über **Anzeigetexte**. Die Oberfläche baute
`Plattenanalyse: Decke über EG` nach und verglich es mit dem Titel. Das bräche,
sobald jemand eine Überschrift umformuliert, und zwar stumm.

Jetzt trägt der Abschnitt seinen Namensraum mit (`Abschnitt(titel, raum)` —
Titel für den Leser, Raum für die Oberfläche), und alle fünf Sichten fragen
`imRaum(eingrenzung(), id)`.

### Kleineres aus derselben Durchsicht

* `querkraft.py` hatte **zwei** `_statische_hoehe` mit gleichem Rumpf, eine
  davon unbenutzt; die Lagentiefen wurden über `self._tiefen` zwischen Methoden
  geschmuggelt. Jetzt eine freie Funktion und ein Parameter.
* `SCHWELLE_ZUG` / `SCHWELLE_DRUCK` standen mitten im Klassenkörper.

### Was die Durchsicht über die Arbeitsweise sagt

Alle drei Befunde entstanden beim *Hinzufügen*: jedes Mal war die zweite
Kodierung eines Begriffs billiger als das Zusammenführen. Das ist der Normalfall
und kein Versehen — aber es heisst, dass eine Durchsicht nach jeder grösseren
Runde nötig ist, nicht irgendwann.

Der Manifest-Wächter hat die neue Datei sofort gemeldet. Genau dafür ist er da.

---

## 2026-09-11 · Alles nachrechenbar, und der Bericht bekommt Abschnitte

**Anlass:** Durchsicht der ganzen Herleitung. Dabei kamen vier echte Fehler
zum Vorschein, und der Querkraftnachweis stellte sich als die einzige Stelle
heraus, an der eine Zahl nicht nachzurechnen war.

### Vier Fehler, die beim Lesen auffielen

| Fehler | Ursache |
| --- | --- |
| `M_Rd = 754·435·(264 − …) = −83.9` | Das Minus stand nur im Ergebnis, nicht in der Formel. Die geschriebene Gleichung stimmte nicht mit ihrem eigenen Resultat überein. |
| `π · 18 mm²/4` | Das Quadrat band an die Einheit statt an den Wert. |
| `− −1484.6` | Doppeltes Minus in der Interpolation. |
| `\text{M\_Rd(N=0) −}` | Eckpunktnamen als roher Text statt gesetzt. |

Der erste ist der schlimmste: eine Gleichung, die ihr eigenes Ergebnis nicht
liefert, ist schlechter als gar keine.

### Querkraft

Die Herleitung zeigte nur den Ansatz und eine Ergebnistabelle. Jetzt steht je
Kombination die vollständige Rechnung da — Einwirkung, statische Höhe,
wirksame Höhe, Dekompressionsmoment, Dehnung, `k_d`, Widerstand,
Erfüllungsgrad — jede Zeile analytisch **und** mit eingesetzten Zahlen.

Je Fall ein eigener Abschnitt, weil der Widerstand über `m_Ed` und `N_Ed` von
der Einwirkung abhängt. Ausgewiesen als `v_Rd(M_Ed = …, N_Ed = …)`; ein
blosses `v_Rd` läse sich wie ein Kennwert des Querschnitts, und das ist es
nicht.

Zwei Formeln berichtigt: `k_g = max(1.20; …)` — der Riegel fehlte — und
`m_Dd = |min(N_Ed; 0)|·h/6`, denn nur Druck entlastet.

**Zur Stellenzahl:** die Faktoren stehen mit vier Stellen da, damit die Zeile
beim Nachrechnen aufgeht: `0.8124 · 1.0954 · 264.0 = 234.93` gegen `234.95`
wahr. Mit zwei Stellen wäre `0.81 · 1.1 · 264 = 235.2` herausgekommen — eine
Zeile, die ihr eigenes Ergebnis verfehlt, ist genau das Problem von oben.

### Abschnitte im Bericht

Jede Berechnung trägt jetzt ihren Abschnitt (`Beton: C30/37`,
`Plattenanalyse: Decke über EG`); der Löser setzt die Überschrift, sobald die
erste Berechnung eines Abschnitts drankommt.

Von Hand ginge das nicht: **welche Berechnung eines Bauteils zuerst läuft,
entscheidet die Abhängigkeitsfolge**, nicht die Reihenfolge im Quelltext. Eine
Überschrift irgendwo hinzuschreiben hiesse, eine Reihenfolge anzunehmen, die
der Löser jederzeit ändern darf.

Der Nebeneffekt ist der eigentliche Gewinn: die Oberfläche kann die Herleitung
jetzt auf den gewählten Bestandteil zuschneiden. Über die Titelebene allein
ginge das nicht — Zwischenüberschriften stehen auf derselben. Deshalb markiert
der Kern, welcher Titel einen Abschnitt eröffnet.

### Lagentabelle statt fünf gleicher Formeln

Für jeden Bewehrungsposten stand eine eigene Flächenformel in der Herleitung —
fünf Lagen ergaben fünf gleich aussehende Blöcke, in denen sich nur die Zahlen
unterschieden. Die Formel steht jetzt einmal, die Ergebnisse in der Tabelle,
ergänzt um Teilung, Stahlsorte und Fläche.

Dafür rechnet `Lagenaufbau` jetzt auch die Flächen. Das ist die richtige
Zuständigkeit: eine Prozedur, die den Lagenaufbau bestimmt, kennt ohnehin alle
Durchmesser und Teilungen.

Ist die Menge gemischt angegeben, steht `s = 150` bzw. `n = 7` in der Zelle;
sind alle gleich, steht die Grösse in der Kopfzeile.

### Günstige und ungünstige Lage

Je Lage wählbar, wie Grundbewehrung und Zulage zueinander liegen:

* **günstig** — beide auf derselben Hülle, je um ihren eigenen Halbmesser
  eingerückt; die *äusseren* Kanten fluchten
* **ungünstig** (Vorgabe) — die *inneren* Kanten fluchten, der dünnere Stab
  rückt zur Plattenmitte und verliert Hebelarm

Die Vorgabe ist ungünstig, weil sich auf der Baustelle nicht steuern lässt,
welche Kante fluchtet.

**Eine Regel für alle vier Lagen.** Die Vorgabe lautete „gleiche Oberkante bei
Lage 1 und 2, gleiche Unterkante bei 3 und 4" — das klingt nach zwei Fällen,
ist aber einer: von der Plattenmitte aus gesehen fluchtet beide Male die
*innere* Kante. `rand = Hülle + ⌀_max − ⌀/2`, fertig. Ein Sonderfall weniger.

Wirkung am Beispiel: die Zulage der 1. Lage sitzt bei 258 statt 264 mm, und
der Querkraftnachweis rechnet mit `d = 261` statt `264` mm — massgebend ist
jetzt die Grundbewehrung.

### Zwei Angaben für die Ausführung

Unter jeder Tabelle der Zusammenfassung stehen Bewehrungsmass
(`A_s,tot · 7850 / (b·h)`, Beispiel 138.7 kg/m³) und Distanzhalterhöhe (OK der
inneren unteren bis UK der inneren oberen Lage, Beispiel 182 mm). Beide kommen
aus dem Kern und stehen damit auch in der Herleitung — in der Oberfläche
gerechnet wären sie die einzigen Zahlen ohne Herleitung gewesen.

### Eigene Pfeilknöpfe

Teilung springt auf Vielfache von 25, Durchmesser durch die lieferbare Reihe
(6 8 10 12 14 16 18 20 22 26 **30** 34 40), Stabzahl in Einerschritten. Das
Drehfeld des Browsers kann nur gleichmässige Schritte — die Reihe der
Durchmesser ist aber keine. Deshalb eigene Knöpfe.

---

## 2026-09-11 · Nachgewiesen wird, was von Hand nachrechenbar ist

**Anlass:** Die M-N-Interaktionslinie entstand aus hunderten Faserintegrationen.
Genau — aber niemand kann sie nachrechnen. Wer das Ergebnis prüfen will, kann es
nur glauben. Für ein Werkzeug, dessen ganzer Zweck „keine Black Box" ist, war
das der wunde Punkt.

### Jetzt zwei Linien

| | genau | Handrechnung |
| --- | --- | --- |
| Entsteht aus | Dehnungsebenen, 332 Punkte | 6 Eckpunkte |
| Beton | Parabel-Rechteck, 200 Fasern | Spannungsblock 0.85·x |
| Gedrückter Stahl | mitgerechnet | **vernachlässigt** |
| In der Herleitung | nein | ja, Formel für Formel |
| Im Diagramm | dünn gestrichelt, grau | gefüllt, kräftig |
| **Urteil** | — | **massgebend** |

Die genaue Linie wird weiterhin gerechnet. Sie steht als Vergleich daneben, und
zwar bewusst zurückhaltend gezeichnet: sie ist nicht das Ergebnis, sie ist der
Massstab dafür, wie viel die Vereinfachung kostet.

### Die sechs Eckpunkte

Je Momentenvorzeichen zwei, dazu zwei gemeinsame:

1. **M_Rd bei N = 0** — `x = A_s·f_yd / (0.85·b·f_cd)`, dann
   `M_Rd = A_s·f_yd·(d − 0.85x/2)`
2. **grösste Zugkraft** — beide Lagen fliessen. *Ein* Punkt für beide
   Vorzeichen, nicht zwei: der Dehnungszustand ist eindeutig, also auch das
   Moment. Bei symmetrischer Bewehrung hebt es sich auf.
3. **grösste Druckkraft** — `N = −b·h·f_cd`, ohne Stahl, `M = 0`
4. **x = h/2** — Nulllinie auf halber Höhe. Gilt nur, wenn die Zugbewehrung
   dort noch fliesst; sonst fällt der Punkt weg und das Polygon läuft
   geradlinig zum reinen Druck.

Punkt 4 gibt dem Polygon den Bauch, den die genaue Linie unter Druck hat.
Beispielplatte x-Richtung: N = −1485 kN, M = 339.2 kNm; genaue Linie −1959 kN,
374.6 kNm.

**Eine Lesart, die geklärt werden musste:** die Vorgabe lautete „0.85·x = h/2".
Wörtlich gelesen wäre x = h/1.7 = 176.5 mm — dann scheitert aber das
mitgegebene Fliesskriterium bei jedem realistischen Plattenquerschnitt
(ε_s = 1.70 ‰ < ε_yd = 2.17 ‰; erfüllt erst ab d/h > 0.95). Das Kriterium wäre
damit sinnlos gewesen. Gemeint war x = h/2, und dann geht es auf:
ε_s = 2.61 ‰ > 2.17 ‰.

**Und eine Vorzeichenfrage:** `M = A_s·f_yd·(d − h/2) − A_s'·f_yd·(d' − h/2)`
stimmt nur, wenn d' von der *Zug*randfaser aus gemessen wird. Misst man d' wie
üblich von der gedrückten Randfaser, muss dort ein Plus stehen — sonst zeigte
ein symmetrischer Querschnitt unter reinem Zug ein Moment, was nicht sein kann.
Umgesetzt ist die Summe der Kräfte mal Hebelarm um die halbe Höhe; das ist
dieselbe Formel, nur mit durchgehend einer Konvention.

### Die Massstabswahl

Vorher: beide Richtungen rechnen, die ungünstigere nehmen. Jetzt eine feste
Regel — waagrecht (M_Rd bei festgehaltenem N_Ed), ausser nahe den Spitzen:

* Zug mit |N_Ed| > N_Rd⁺/2 → senkrecht
* Druck mit |N_Ed| > 3/4·|N_Rd⁻| → senkrecht

Die verschiedenen Schwellen sind kein Versehen: die Linie ist nicht symmetrisch,
auf der Druckseite bleibt sie viel länger brauchbar waagrecht.

Diese Wahl erscheint **nicht** in der Mitschrift. Sie ist kein Rechenschritt,
sondern die Festlegung, in welcher Richtung gemessen wird. Was dann gerechnet
wird — die lineare Interpolation zwischen zwei Eckpunkten — steht vollständig
da, mit Stützpunkten.

### Was dabei auffiel

**Die Handrechnung liegt nicht durchgehend auf der sicheren Seite.** Sie
vernachlässigt den gedrückten Stahl (das drückt den Widerstand), setzt aber
einen Block der Höhe 0.85·x an, dessen Resultierende über der
Parabel-Rechteck-Beziehung liegt (das hebt ihn). Welcher Einfluss überwiegt,
hängt vom Querschnitt ab. Bei der einfachen Testplatte liegt das Polygon 0.15 %
*über* der genauen Linie. Der Test prüft deshalb eine Toleranz und keine
Richtung.

**Ein Gruppierungsfehler, der still gewesen wäre:** Grundbewehrung und Zulage
einer Lage liegen auf leicht verschiedenen Höhen, weil ihre Durchmesser
verschieden sind. Wer die Bewehrung nach z gruppiert, bekommt drei Gruppen
statt zwei und verliert eine davon — im Beispiel 1696 mm² von 2450 mm².
Gruppiert wird nach der Lagenzugehörigkeit aus dem Modell.

### Nebenbei

* Liniengeometrie nach `linie.py` herausgezogen. Beide Linien werden auf
  dieselbe Art ausgewertet; läge die Geometrie bei einer von beiden, müsste die
  andere sie einbinden (Ring) oder nachbauen (Drift).
* Betondiagramm zeigt zusätzlich den Spannungsblock in grün, umschaltbar — man
  sieht, was man beim Handrechnen aufgibt.
* Bewehrungsbeschriftungen im Querschnittsbild werden auseinandergeschoben,
  mit Anschlussstrich auf die wahre Höhe.
* Das kleine α des Erfüllungsgrads wurde von `text-transform: uppercase` zu
  einem grossen Α gemacht. KaTeX ist davon jetzt ausgenommen.

---

## 2026-09-11 · Die Seite läuft ohne Server

**Anlass:** Die veröffentlichte Seite sollte funktionieren, ohne dass irgendwo
ein Python läuft — und ohne dass die Formeln dafür in JavaScript nachgebaut
werden.

### Was entschieden wurde

| Frage | Entscheidung | Warum |
| --- | --- | --- |
| Python im Browser | **Pyodide**, ins Repo gelegt | Kein fremder Dienst, offline lauffähig, in fünf Jahren noch dasselbe. Kostet ≈13 MB. |
| Rechnen in JavaScript | **nein, nirgends** | Zwei Rechenwege driften auseinander, und dann ist die Frage „welcher stimmt?" nicht mehr zu beantworten. |
| Lokaler Server | **bleibt** | Startet ohne Ladezeit und kann den Bericht zu PDF übersetzen. Beides kann der Browser nicht. |
| Projektablage | **Browser + Datei** | Laufend im localStorage als Netz darunter; Speichern und Öffnen über `.json`. |
| Bauschritt | **keiner** | Die Seite ist, was im Repo liegt. Nichts wird erzeugt, nichts kann veralten. |

### `opencivil/web/dienst.py` — die Trennlinie

Die Endpunktfunktionen sassen vorher in `server.py` und waren mit HTTP,
Dateisystem und `subprocess` verwoben. Jetzt nehmen sie ein `dict` und geben
ein `dict` zurück, sonst nichts. `bearbeite(name, rumpf) -> Antwort` wirft
nicht: auch der Fehlerfall ist eine gewöhnliche Antwort mit Status. Dadurch
muss keine der beiden Hüllen sich überlegen, welche Ausnahme welchen Status
verdient.

Das ist der eigentliche Kniff der ganzen Änderung. Ohne diese Trennlinie hätte
die Browserfassung ihre eigene Ablaufsteuerung gebraucht — und damit die
Möglichkeit, sich anders zu verhalten.

Was eine Hülle beisteuern darf, ist, was ihre Umgebung eigen hat: der Server
das Übersetzen zu PDF, der Browser das Ablegen im localStorage. Nie das Rechnen.

### `web/js/kern.js` — die Brücke

1. Pyodide aus `web/vendor/pyodide/` starten.
2. `web/kern/dateien.json` lesen — darin stehen die 27 Quelldateien.
3. Alle nebeneinander holen und ins Dateisystem von Pyodide schreiben.
4. `sys.path` erweitern, `opencivil.web.dienst` einbinden.
5. `bearbeite_json(name, rumpf)` aufrufen. JSON rein, JSON raus.

Die Datei enthält keine einzige Formel und keine Prüfung. Sie schaufelt
Zeichenketten.

**Warum eine Liste und kein Archiv:** Ein `.zip` im Repo wäre ein zweites,
erzeugtes Abbild des Quellcodes — und damit etwas, das unbemerkt veralten kann.
Die Liste ist Text, im Diff lesbar, und ein Test wacht darüber, dass sie zu den
vorhandenen Dateien passt. Veraltet sie, schlägt der Test an und nicht erst die
veröffentlichte Seite.

**Warum alle Dateien und nicht nur die gebrauchten:** Man könnte die Liste auf
das beschränken, was `dienst.py` einbindet. Dann müsste sie bei jeder neuen
Einbindung nachgezogen werden, und wer das vergisst, merkt es erst im Browser.
275 KB sind der bessere Handel.

### Nachgemessen

Am Beispielprojekt, ein voller Durchgang mit beiden Interaktionslinien:

| | Zeit |
| --- | --- |
| CPython 3.13 | 57 ms |
| Pyodide 314.0.6 (Python 3.14.2) | **73 ms** |

Das war die Überraschung — ich hatte mit dem Drei- bis Fünffachen gerechnet und
deshalb einen Web Worker erwogen. Bei 73 ms hinter einer Verzögerung von 450 ms
lohnt der Aufwand nicht. Sollte ein Projekt einmal deutlich grösser werden,
wäre ein Worker der nächste Schritt.

Die eigentliche Wartezeit ist der erste Aufruf: ≈13 MB Pyodide. Danach liegt es
im Zwischenspeicher des Browsers. Dafür gibt es den Ladeschirm.

### Gegengeprüft: rechnen beide dasselbe?

Dieselbe Anfrage über beide Wege, Antworten kanonisiert (Schlüssel sortiert)
und gehasht:

```
ketten        gleich      protokoll     gleich
reihenfolge   gleich      zuordnung     gleich
linien        ungleich    urteile       ungleich
werte         ungleich    werkstoffg.   ungleich
```

Nach Normierung der Zahlenschreibweise blieben `linien`, `urteile` und `werte`
**Bit für Bit gleich**. Die textuellen Unterschiede kamen allein daher, dass
Python `1e-05` schreibt, wo JavaScript `0.00001` schreibt.

`werkstoffgesetze` wich auch dann noch ab. Ursache: `JSON.stringify(-0)` ergibt
in JavaScript `"0"` — das Vorzeichen der negativen Null überlebt die Wandlung
nicht. Die Dehnung am Nullpunkt ist `-0.0`. Ebenfalls reine Darstellung, kein
Rechenunterschied.

**Ergebnis: die Zahlen sind identisch.** Kein Zufall, sondern die Folge davon,
dass es nur eine Implementierung gibt.

### Ablage

`web/js/ablage.js`, drei Wege mit derselben Beschreibung:

- **Browser** — nach jeder Änderung in den localStorage. Kein Speichern im
  eigentlichen Sinn, sondern das Netz darunter.
- **Auf die Platte** — `.json` zum Herunterladen, eingerückt, damit man sie
  lesen und vergleichen kann.
- **Von der Platte** — Dateiwähler, geprüft im Kern.

Im Ablagevermerk steht mit, ob der Stand schon als Datei auf der Platte liegt.
Ohne das sähe jeder frisch geöffnete Tab so aus, als wäre alles gesichert.

**Eine Falle, die auffiel:** `Projekt.aus_dict` ist mit Absicht nachsichtig —
es nimmt jedes `dict` und macht daraus notfalls ein leeres Projekt. Beim Laden
einer Beschreibung ist das richtig. Beim Öffnen einer Datei wäre es verheerend:
wer versehentlich eine beliebige JSON-Datei erwischt, bekäme wortlos ein leeres
Projekt und hätte seine Arbeit verloren. `dienst.pruefen` verlangt deshalb, dass
mindestens eines der Felder `name`, `materialien`, `querschnitte` vorkommt.

### Der Server liefert jetzt vom Projektverzeichnis aus

Vorher war `web/` die Wurzel. Auf GitHub Pages liegt aber das ganze Repo im
Netz, und die Brücke holt die `.py`-Dateien unter `/opencivil/…`. Mit
verschiedenen Wurzeln hätten die Adressen verschiedene Tiefe — genau die Art
Unterschied, die einem erst auf der veröffentlichten Seite auffällt.

Ausgeliefert wird nur, was in `OEFFENTLICH` steht (`web/`, `opencivil/`).
`daten/`, `.git/` und `tests/` bleiben draussen; ein Test prüft das.

### Änderungen an bestehenden Dateien

- `latex_dokument.py`: `uebersetze()` aus `schreibe()` gelöst. Nur das
  Übersetzen braucht einen Unterprozess, und den gibt es im Browser nicht.
- `zustand.js`: `projektAendern` ist der einzige Weg, auf dem sich Eingaben
  ändern — deshalb hängt dort das Ablegen im Browser.
- Die Endpunkte für `daten/projekt.json` sind weg. Der Browser hält das Projekt.

---

## Davor

Sieben Commits Vorgeschichte, vom Rechenkern bis zum Querkraftnachweis. Für die
Einzelheiten: `git log`. Die tragenden Entscheidungen:

- **Eigene `Groesse`-Klasse** statt einer Bibliothek. Einheiten werden intern in
  SI gehalten, die Anzeigeeinheit ist reine Darstellung. Rechenoperationen
  prüfen die Dimension.
- **Keine Fremdpakete.** Der ganze Kern kommt mit der Standardbibliothek aus —
  wodurch er überhaupt erst in Pyodide läuft.
- **LaTeX von Hand statt sympy.** Welche Formel gilt, hängt oft davon ab, welche
  Eingaben vorliegen; das lässt sich nicht aus einem Ausdrucksbaum ableiten.
- **Rückwärtsverkettung im `Rechenwerk`**, verschränkt mit dem Ausführen, damit
  `anwendbar()` von tatsächlichen Werten abhängen darf.
- **`empirisch()`** als Notausgang für dimensionell uneinheitliche
  SIA-Formeln — erzwingt, dass jede Einheit benannt wird, und schreibt die
  Annahme in den Bericht.
- **Erfüllungsgrad statt Ausnutzung**, durchgehend, auch im Kern.

### Offen

**Die Sortentabellen in `material/beton.py` und `material/betonstahl.py` sind
aus der Vorgängerfassung übernommen und nicht gegen die gedruckte Norm
geprüft.** Das gilt auch für die Normverweise. Vor ernsthaftem Gebrauch
nachschlagen.
