# OpenCivilToolkit

Nachvollziehbare Bemessung nach SIA – ohne Black Box.

Jeder Rechenschritt ist ein Objekt, das weiss, welche Werte es braucht, welche es
liefert, wie gerechnet wird und wie das Ergebnis aufzuschreiben ist. Aus dieser
einen Quelle entstehen Zahlenwert *und* LaTeX-Herleitung – sie können nicht
auseinanderlaufen.

## Im Browser, ohne Installation

**<https://graphoflife.github.io/OpenCivilToolkitSIA/>**

Dort rechnet **Python**, nicht JavaScript: die Seite startet Pyodide und lädt
genau die `.py`-Dateien aus `opencivil/`, die auf dem Rechner auch laufen. Keine
Formel ist in JavaScript nachgebaut — das wäre ein zweiter Rechenweg, der
irgendwann vom ersten abweicht, und dann wüsste niemand mehr, welcher stimmt.

Der erste Aufruf lädt einmalig ≈13 MB Python-Laufzeit; danach liegt sie im
Zwischenspeicher des Browsers. Ein Durchgang des Beispielprojekts braucht in
CPython rund 25 ms; im Browser ist es etwa das Anderthalbfache.

## Auf dem eigenen Rechner

```bash
python3 start_ui.py          # Oberfläche auf http://127.0.0.1:8080
python3 demo_material.py     # Kern allein: Kennwerte, Rückverfolgung, Überschreiben
python3 demo_nachweis.py     # Kern allein: Querschnitt, M-N-Nachweis, Bericht
python3 -m unittest discover -s tests -t .
```

Der lokale Server startet ohne Ladezeit und kann den Bericht mit einer
TeX-Maschine zu PDF übersetzen. Sonst ist er dasselbe: beide Wege rufen
`opencivil/web/dienst.py` auf. Welcher gerade gilt, steht unten links im Fenster.

Kein Fremdpaket, nirgends — es genügt ein `python3`. KaTeX und Pyodide liegen
unter `web/vendor/` bei, damit die Seite ohne fremden Dienst auskommt.

## Speichern

Jede Eingabe liegt sofort im Browser; ein geschlossenes Fenster kostet nichts.
*Speichern* legt das Projekt als `.json` auf die Platte, *Öffnen* liest es
zurück. Gelesen wird die Datei im Kern, mit denselben Prüfungen wie alles andere.

## Stand

Fertig und getestet (569 Tests):

| Baustein | Inhalt |
|---|---|
| `core/einheiten` | `Groesse` mit Dimensionsprüfung, Einheitenkatalog, `empirisch()` |
| `core/wert` | Trennung von Definition und Belegung, Quelle eines Wertes |
| `core/berechnung` | `Formel`, `Vorgabe`, `Prozedur`, `Nachweis` |
| `core/latex` | Platzhalter-Einsetzung, `Formelzeile`, Tabellen, Fallunterscheidung |
| `core/protokoll` | Mitschrift als Datenstruktur, `StillesProtokoll` |
| `core/rechenwerk` | Rückwärtsauflösung, Variantenwahl, fehlende Eingaben, Zyklen |
| `material/` | Beton und Betonstahl nach SIA 262:2025 |
| `querschnitt/` | Plattenquerschnitt, Lagenaufbau, Werkstoffgesetze |
| `nachweis/linie` | Geometrie einer M-N-Linie, `Achse` als Wert |
| `nachweis/handrechnung` | die von Hand nachrechenbaren Eckpunkte |
| `nachweis/dehnungsfaecher` | die präzise Linie -- nur für das Diagramm |
| `nachweis/querschnittsloeser` | Dehnungsebene aus N und M, zwei Bisektionen |
| `nachweis/` | M-N, Querkraft (mit Bügeln), Duktilität, sprödes Versagen, Zwängung auf Normalkraft und auf Biegung, Stahlspannung unter häufiger (gegen Fliessen) und quasi-ständiger Last (aus der Rissbreite), Knicken am verformten System |
| `spannungsanalyse.py` | drei Bilder am Querschnitt — kein Nachweis |
| `bewehrungssuche.py` | die kleinste Bewehrung suchen, die alle Nachweise erfüllt |
| `bericht/` | Konsole und LaTeX-Dokument (PDF, sobald eine TeX-Maschine da ist) |
| `projekt.py` | speicherbare Projektbeschreibung, baut daraus ein Rechenwerk |
| `web/speicher.py` | Ergebnisse je Bauteil, damit nur Geändertes neu rechnet |
| `web/dienst.py` | der Rechendienst, unabhängig vom Transportweg |
| `web/server.py` | HTTP-Hülle darum (nur Standardbibliothek) |
| `web/js/kern.js` | Pyodide-Hülle darum, für die Seite ohne Server |
| `web/js/` | Oberfläche in reinem JavaScript, ohne Bauschritt |

Wie das zusammenhängt und warum es so gebaut ist, steht in
[ENTWICKLUNG.md](ENTWICKLUNG.md).

## Oberfläche

Drei Tafeln: links die Bestandteile des Projekts, in der Mitte die Eingaben zum
ausgewählten Bestandteil, rechts das Ergebnis. Unter 900 px Fensterbreite steht
eine Tafel allein und ein Umschalter am unteren Rand wechselt zwischen ihnen --
dieselbe Aufteilung, nur nacheinander.

Die Oberfläche rechnet nichts. Sie schickt die Projektbeschreibung an den Kern
und stellt dar, was zurückkommt -- fertige Zahlen und fertige LaTeX-Zeichen­ketten.
Deshalb kann am Bildschirm gar nichts anderes stehen als im Bericht.

**Rechte Tafel:**

* *Zusammenfassung* -- je Platte eine Tabelle: Widerstand, Einwirkung und
  Erfüllungsgrad. Darunter, in gedämpftem Rot, die ausgeschalteten Nachweise,
  die mit der vorliegenden Bewehrung *nicht* aufgehen würden
* *Diagramme* -- Plattenquerschnitt, M-N-Resistenzlinie mit den
  Bemessungspunkten (die gestrichelte Strecke zeigt den Weg, in dem der
  Erfüllungsgrad gemessen wurde), Querkraftkurven, Spannungs-Dehnungs-Bilder
* *Herleitung* -- die Mitschrift, Formel für Formel, mit Normstelle
* *Werte* -- alle Grössen mit ihrer Herkunft (Eingabe, Vorgabe, berechnet,
  überschrieben); dort lässt sich auch ein Ziel wählen: der Kern löst rückwärts
  auf, rechnet nur das Nötige und zeigt die Kette der erforderlichen Schritte

**Formel nach Word:** jede Formel hat zwei Knöpfe. *Word* legt sie als MathML in
die Zwischenablage -- Word fügt daraus eine richtige, weiter bearbeitbare
Gleichung ein, kein Bild. *TeX* legt den LaTeX-Quelltext ab, für Overleaf oder
den Formeleditor von Word 365.

**Überschreiben:** bei jedem gerechneten Kennwert steht ein Haken. Wird er
gesetzt, gilt der eingetippte Wert, und der ganze Zweig dahinter entfällt --
sichtbar daran, dass die zugehörigen Formeln aus der Herleitung verschwinden.

## Die vier tragenden Entscheide

**1. Einheiten werden geprüft, nicht angenommen.**
Eine `Groesse` trägt ihre Dimension mit sich; `mm + MPa` wirft sofort. Intern
wird alles in SI-Basis gehalten, die Anzeige-Einheit ist reine Darstellung.

Dimensionell inhomogene Normformeln – etwa `tau_cd = 0.3·√f_ck / gamma_c` –
laufen über `empirisch()`. Dort muss man angeben, in welcher Einheit jeder Wert
einzusetzen ist und welche Einheit das Resultat trägt. Die stillschweigende
Konvention der Norm steht damit im Code statt in jemandes Kopf. Im Bericht
erscheint sie nicht -- dort sagt die Normreferenz an der Gleichung, woher sie kommt.

**2. Die Formel steht einmal da.**
Von Hand geschrieben wird nur die *analytische* Form mit `@name`-Platzhaltern.
Die Fassung mit Zahlen und Einheiten entsteht daraus automatisch:

```python
Formel(
    id="beton.C30_37.f_cd",
    ausgabe=f_cd_def,
    eingaben={"eta_fc": "...eta_fc", "f_ck": "...f_ck", "gamma_c": "...gamma_c"},
    vorlage=r"\frac{@eta_fc \cdot @f_ck}{@gamma_c}",
    funktion=lambda eta_fc, f_ck, gamma_c: eta_fc * f_ck / gamma_c,
)
```

ergibt

```latex
f_{cd} = \frac{\eta_{fc} \cdot f_{ck}}{\gamma_c}
       = \frac{1 \cdot 30\,\mathrm{N}/\mathrm{mm}^{2}}{1.5}
       = 20\,\mathrm{N}/\mathrm{mm}^{2}
```

**3. Welche Formel gilt, entscheidet sich zur Laufzeit.**
Mehrere Berechnungen dürfen denselben Wert liefern. Der Löser wählt in zwei
Stufen: erst, ob die Eingaben überhaupt beschaffbar sind, dann über
`anwendbar()`, das zusätzlich von den Zahlenwerten abhängen darf. Die Begründung
der Wahl landet im Protokoll.

```python
Formel(..., prioritaet=10, bedingung=lambda e: (
    (True, "f_ck ≤ 50 N/mm², Normalbeton") if e.g("f_ck") <= Groesse(50, MPA)
    else (False, "gilt nur bis C50/60")))
```

**4. Rechnen und Aufschreiben geschehen gemeinsam.**
Eine Berechnung schreibt während des Rechnens ins `Protokoll`. Eine Iteration
liefert damit nicht nur ihr Resultat, sondern auch ihren Ablauf – Ansatz,
Zwischenschritte als Tabelle, Abbruchkriterium.

## Rückverfolgung

```python
loesung = werk.loese("querschnitt.decke.nachweis.mn.Feld.ausnutzung")

loesung.kette(ziel)             # nötige Rechenschritte, in Reihenfolge
loesung.benoetigte_werte(ziel)  # alle eingegangenen Werte
loesung.fehlende                # was der Benutzer noch angeben muss
```

Fehlende Eingaben werden bis zur Wurzel verfolgt: gemeldet wird nicht
„`f_yd` fehlt", sondern „`f_yk` und `gamma_s` fehlen, gebraucht für `f_yd`".

Berechnet wird nur, was das Ziel braucht. Wird ein Wert von Hand gesetzt
(`werk.setze(...)`), gilt er als überschrieben und der ganze Zweig dahinter
entfällt.

## Nachgewiesen wird x

Eine Platte trägt in zwei Richtungen, nachgewiesen wird hier nur eine: **x**.
Die y-Lagen werden trotzdem eingegeben, und zwar aus zwei Gründen. Sie zählen
zum Bewehrungsgehalt, und sie liegen aussen -- ihr Durchmesser bestimmt, wieviel
statische Höhe der x-Bewehrung bleibt. Wer sie weglässt, rechnet x mit einer
Höhe, die es auf der Baustelle nicht gibt.

Vorgegeben tragen darum die **2. und die 3. Lage** in x: die Querrichtung läuft
unten und oben durch, die Tragrichtung liegt dazwischen. Wer anders verlegt,
stellt die Richtung der 1. und der 4. Lage um; die beiden inneren bekommen
zwingend die Gegenrichtung.

Die Bewehrungssuche fasst die y-Lagen nicht an. In y wird nichts nachgewiesen,
also gäbe es dort kein Mass, an dem sich ein Durchmesser bemessen liesse -- sie
zöge ihn auf null, und genau das wäre falsch. Was in y liegt, sagt der Benutzer.

Schnittgrössen gehören damit immer zu x. Eine ältere Datei mit einem Lastfall
in y lässt sich nicht öffnen; sie meldet, was zu tun ist. Ihn stillschweigend
auf x umzudeuten hiesse, eine Zahl an einem anderen Querschnitt anzusetzen als
gemeint war.

## Ein Schalter je Nachweis

Duktilität, sprödes Versagen, Zwängung auf Biegung und Zwängung auf Normalkraft
haben je **einen** Haken. Gerechnet werden beide x-Lagen -- die untere trägt das
Feld-, die obere das Stützmoment --, in der Zusammenfassung steht die
ungünstigere, und die Herleitung zeigt beide samt einem Satz, welche entschieden
hat. Geht die schlechtere auf, gehen beide auf; vier Zeilen für eine Frage waren
drei zuviel.

Ausgeschaltet heisst dabei nicht weg: der Nachweis rechnet weiter mit, er steht
nur nicht in Tabelle und Herleitung. Geht er mit der vorliegenden Bewehrung
nicht auf, steht darüber ein Hinweis unter der Zusammenfassung. Ein Schalter
sagt «interessiert mich gerade nicht» und nicht «gilt nicht».

## Vorzeichen und Einheiten im Querschnitt

* `z` von der Oberkante nach unten, `0 ≤ z ≤ h`
* Dehnung und Spannung: `> 0` = Zug
* `N > 0` = Zug, `M > 0` = Zug an der Unterseite, bezogen auf `h/2`
* `N` und `M` gelten für die betrachtete Breite `b`; mit `b = 1 m` sind es die
  Werte pro Laufmeter

## Erfüllungsgrad beim M-N-Nachweis

Ob ein Punkt innerhalb der Resistenzlinie liegt, entscheidet immer derselbe
Test. Nur *wie weit* er entfernt ist, hängt vom gewählten Massstab ab:

| `Erfuellungsart` | Messung |
|---|---|
| `NORMALKRAFT_KONSTANT` *(Standard)* | waagrecht bis zur Momentengrenze, `η = \|M_Ed\| / \|M_Rd\|` |
| `MOMENT_KONSTANT` | senkrecht bis zur Normalkraftgrenze, `η = \|N_Ed\| / \|N_Rd\|` |
| `NAECHSTER_PUNKT` | kürzester Abstand im auf die Eckwerte normierten Diagramm |

> Bei `MOMENT_KONSTANT` fällt η klein aus, wenn der Fall vom Moment beherrscht
> wird – die Reserve wird dann in einer Richtung gemessen, in der viel Luft ist.
> Das ist kein Fehler, sondern liegt in der Natur dieses Massstabs.

## Noch offen

* **PDF**: sobald `tectonic`, `latexmk` oder `pdflatex` installiert ist, wird
  automatisch übersetzt. Bis dahin steht das `.tex` bereit (Overleaf-tauglich).
* **Weitere Nachweise**: Rotationskapazität. Querkraft, Mindestbewehrung,
  Rissbegrenzung und Knicken sind gebaut.
* **Schiefe Lagen** im Lagenaufbau (die alte Fassung konnte das). Zulagen gibt
  es.
* **Normwerte prüfen**: die Sortentabellen in `material/beton.py` und
  `material/betonstahl.py` sind aus der Vorgängerfassung übernommen und vor dem
  produktiven Einsatz gegen die gedruckte Norm abzugleichen.

## Verhältnis zur Vorgängerfassung

`_Old by Gemini/` bleibt als Referenz liegen. Neu gegenüber damals:

* Einheitensystem statt Einheiten als Zierde (dort: `/1e6`-Faktoren von Hand)
* Formel einmal statt bis zu dreimal (dort: `calc_fn`, `sympy_expr`,
  `formula_template` nebeneinander, ungeprüft)
* Rechengraph mit Rückwärtsauflösung (dort: gar nicht vorhanden)
* Prozeduren mit mehreren Ausgaben (dort: eine Formel = ein Skalar)
* Fehler schlagen durch (dort: `except` mit Warnung und altem Wert zurück)
* Backend ohne Darstellungswissen (dort: Farben und Panel-Angaben in der Engine)
