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
python3 demo_nachweis.py     # Kern allein: Platte beschreiben, rechnen, Bericht
python3 -m unittest discover -s tests -t .
```

Der lokale Server startet ohne Ladezeit. Sonst ist er dasselbe: beide Wege rufen
`opencivil/web/dienst.py` auf. Welcher gerade gilt, steht unten links im Fenster.

Kein Fremdpaket, nirgends — es genügt ein `python3`. KaTeX, MathLive, Pyodide
und die Schrift JetBrains Mono liegen unter `web/vendor/` bei, damit die Seite
ohne fremden Dienst auskommt.

## In Python, ohne Oberfläche

```python
from opencivil import Projekt

p = Projekt("Decke über EG")
p.beton("C30/37")
p.stahl("B500B")

# Masse in mm; je Richtung zwei Durchmesser, unten und oben.
# x liegt innen (2. und 3. Lage), y aussen.
q = p.platte("Decke", h=300, x=[18, 12], x_zulage=[12, 0], y=[12, 12],
             teilung=150, rissanforderung="erhoeht")
q.einwirkung("Feld", M_Ed=150, V_Ed=80)       # kNm, kN, kN/m; Zug positiv
q.quasistaendig.lastfall("Dauerlast", M_Ed=80)
q.duktilitaet = True                          # alles Weitere am Eintrag selbst
q.spannungsfall("Biegung", art="moment_kruemmung", N_Ed=0)          # M-χ-Linie
q.spannungsfall("Zug", art="normalkraft_dehnung", M_Ed=20,          # N-ε-Linie,
                kriechzahl=1.0, rechenart="block")                  # eigene Wahl
q.spannungsfall("Steifigkeit", art="moment_emodul",                 # E_eq über M
                werkstoffsatz="charakteristisch")

# Jedes Kapitel wählt, womit es rechnet: Kriechzahl, Werte, Rechenart.
from opencivil.projekt import RechenwahlEintrag
q.tragsicherheit_wahl = RechenwahlEintrag(rechenart="parabel")      # genaue Linie
q.quasistaendig.wahl.kriechzahl = 2.0                               # φ der Stahlspannung
q.knicken_wahl_widerstand = RechenwahlEintrag(werkstoffsatz="charakteristisch",
                                               rechenart="parabel")
q.kriechzahl = 2.0                            # φ der Platte: nur für w/w_c

ergebnis = p.rechnen()
print(ergebnis.zusammenfassung())             # je Platte eine Tabelle
ergebnis.erfuellt                             # True / False
ergebnis.bericht()                            # der ganze Bericht mit Herleitung
ergebnis.latex("ausgabe/decke")               # .tex, mit pdf=True auch PDF
ergebnis.markdown("ausgabe/decke")            # .md, Formeln als LaTeX-Mathe
ergebnis.analysen()                           # Spannungsbilder, M-χ- und N-ε-Linien
p.speichern("decke.json")                     # lässt sich in der Oberfläche öffnen
```

Ein gezeichneter Querschnitt geht genauso -- Masse in mm, y nach rechts, z
nach oben:

```python
u = p.analyse("Unterzug")                     # Rechteck 300 × 600, 3 ⌀20 unten, 2 ⌀12 oben
ecken = [[50, 50], [250, 50], [250, 550], [50, 550]]
for i in range(4):                            # vier Wände: eine Zelle, sie trägt Torsion
    u.schubwand(ecken[i], ecken[(i + 1) % 4], dicke=100, durchmesser=10,
                teilung=150, schnitte=1, stahl="s1")
u.stab(150, 300, durchmesser=16, stahl="s1")  # ein Einzelstab bei y = 150, z = 300
u.lastfall("Feld", M_y_Ed=150, V_z_Ed=150, T_Ed=15)   # kN, kNm
u.einachsig = False                           # N, M_y, M_z zusammen, Nulllinie schräg
```

Gezeichnet wird mit Knoten: gleiche Koordinaten sind ein Knoten, und die
Wände oben teilen ihre Ecken mit der Bewehrungslinie unten. Dasselbe tut
das Zeichenfenster -- verschoben wird dort aber nur, was gewählt ist: Wer
die Bewehrungslinie verschiebt, nimmt die Wände nicht mit. Ein Klick wählt
eine Ecke, wo mehrere aufeinander liegen, ein Rahmen alle. Eine Vorlage
kommt dazu, wo man will:
`u.vorlage_einsetzen("kreis", beton="b1", stahl="s1", masse={"D": 400},
ursprung=(600, 0))` -- Rechteck, T-Balken, Hohlkasten oder Kreis.

Ein ebener Rahmen ebenso -- Koordinaten in m, x nach rechts, z nach oben:

```python
r = p.balkensystem("Rahmen")                  # leer; gezeichnet wird wie beim Querschnitt
stuetze = r.querschnitt("Stütze", "rechteck", b=300, h=300)   # Masse in mm
riegel = r.querschnitt_aus("Unterzug", "analyse", u)          # A und I_y der Analyse
links = r.linie((0, 0), (0, 4), querschnitt=stuetze, material="b1")
balken = r.linie((0, 4), (6, 4), querschnitt=riegel, material="b1")
r.linie((6, 4), (6, 0), querschnitt=stuetze, material="b1", gelenk_anfang=True)
r.lager_an((0, 0), "eingespannt")             # gelenkig, verschieblich oder je Richtung
r.lager_an((6, 0), "gelenkig")
g = r.lastfall("Eigengewicht")
w = r.lastfall("Wind")
r.stablast(g, balken, wert=25.0)              # kN/m, senkrecht nach unten positiv
r.stablast(w, links, wert=3.0, richtung="waagrecht")
r.knotenlast(w, (0, 4), 10.0, richtung="waagrecht")          # kN
r.kombination("Tragsicherheit", (g, 1.35), (w, 1.5))

system = p.rechnen().balkensystem("Rahmen")
system.ergebnis.meldungen                     # leer -- oder warum nicht gerechnet wird
system.verlaeufe("Tragsicherheit")["L2"].extrem("M")         # in SI: Stelle, Wert
```

Linien- und Dreieckslasten (`wert_b`), Einzellasten, Momente und verteilte
Momente gehen mit `art=`; Federn, Bettung und feste Linienlager mit den
Feldern der Linie (`quer`, `k_quer`, `laengs`, `k_laengs`). `r.teilen("L2",
2.5)` teilt eine Linie samt ihren Lasten, `r.umkehren("L2")` kehrt sie um.

Es ist dieselbe Beschreibung, die die Oberfläche speichert, und dieselbe
Rechnung: `p.rechnen()` liefert dieselben Urteile wie die Maske, und
`Projekt.beispiel()` ist selbst so gebaut. Ein vertipptes Feld
(`riss_anforderung=...`) wird gemeldet, nicht still übergangen.

## Speichern

Jede Eingabe liegt sofort im Browser; ein geschlossenes Fenster kostet nichts.
*Speichern* legt das Projekt als `.json` auf die Platte, *Öffnen* liest es
zurück. Gelesen wird die Datei im Kern, mit denselben Prüfungen wie alles andere.

## Notizbuch und Obsidian

Wie gerechnet wird, wie die Bibliothek gebaut ist und was beim Bauen gelernt
wurde, steht als Markdown im Ordner [`notizbuch/`](notizbuch/Start.md):
die [Entwicklung](notizbuch/Notizen/Entwicklung.md), was noch
[offen](notizbuch/Notizen/TODO.md) ist, und die
[Arbeitsweise](notizbuch/Notizen/Arbeitsweise.md) von Claude. Der Ordner ist
ein Obsidian-Tresor: in Obsidian «Ordner als Tresor öffnen» und `notizbuch`
wählen – ohne Plugin. Auf der Seite zeigt ihn der Knopf *Dokumentation*
neben *Rechnen*, auf dem Telefon die Wahl *Doku* unten.

Jede Formel steht dort auf einer eigenen Seite – mit Normstelle, Grössen,
Zahlenbeispiel, der Stelle im Code und der Theorie. Diese Seiten schreibt
`python3 -m opencivil.web.bruecke` aus dem Code; was unter ihrer Linie von
Hand steht, bleibt dabei erhalten.

## Stand

Fertig und getestet (1091 Tests):

| Baustein | Inhalt |
|---|---|
| `core/einheiten` | `Groesse` mit Dimensionsprüfung, Einheitenkatalog, `empirisch()` |
| `core/wert` | Trennung von Definition und Belegung, Quelle eines Wertes |
| `core/berechnung` | `Formel`, `Vorgabe`, `Prozedur`, `Nachweis` |
| `core/latex` | Platzhalter-Einsetzung, `Formelzeile`, Tabellen aus Text- und Formelzellen, Fallunterscheidung |
| `core/protokoll` | Mitschrift als Datenstruktur, `Zwischenwerte` für Vorlagen, ein Durchlauf mit einer Tafel je Darstellung, `StillesProtokoll` |
| `core/rechenwerk` | Rückwärtsauflösung, Variantenwahl, fehlende Eingaben, Zyklen |
| `material/` | Beton und Betonstahl nach SIA 262:2025 |
| `querschnitt/` | Plattenquerschnitt, Lagenaufbau, Werkstoffgesetze (dazu der Spannungsblock als Gesetz) |
| `querschnitt/geometrie` | Polygone, Verschachtelung, Stablinien, Prüfungen der Zeichnung |
| `querschnitt/fasern` | Fasern und Dehnungsgrenzen -- auch der Löser der Platte rechnet darüber |
| `querschnitt/interaktion` | der Dehnungsfächer für jede Form, schiefe Biegung, Widerstand in Momentenrichtung |
| `querschnitt/schubwaende` | Querkraft und Torsion auf die Wände: Federn, Zellen, Bredt, Fachwerk, Längszugkraft |
| `querschnitt/analyse` | die Querschnittsanalyse als Bauteil: Zeichnung, Werte, Werkstoffwahl |
| `querschnitt/vorlagen` | Rechteck, T-Balken, Hohlkasten, Kreis zum Anfangen |
| `stabwerk/matrix` | Gleichungslöser im Profil (LDLᵀ), Nummerierung nach Cuthill-McKee, die freie Bewegung eines beweglichen Systems |
| `stabwerk/stab`, `modell` | der ebene Stab: Steifigkeit, Drehung, Bettung, arbeitsgleiche Lasten; das Stabwerk in SI |
| `stabwerk/system` | das ganze System: Unbekannte, Gelenke, Federn, Linienlager, Knoten auf Stäben, Kombinationen, Lagerkräfte, Gleichgewichtsprobe |
| `stabwerk/verlauf` | N, V, M und Biegelinie längs der Stäbe als Polynome, mit Extremwerten |
| `stabwerk/querschnitte` | die Querschnitte der Stäbe nach Vorlage, mit ihren Formeln |
| `stabwerk/rechnung`, `herleitung` | das Balkensystem im Rechenwerk und wie es seine Rechnung aufschreibt |
| `nachweis/linie` | Geometrie einer M-N-Linie, `Achse` als Wert |
| `nachweis/handrechnung` | die von Hand nachrechenbaren Eckpunkte |
| `nachweis/dehnungsfaecher` | die Grenzen des Dehnungsfächers: als Ebenen für die genaue Linie, als Bedingungen für die Analyse |
| `nachweis/resistenzlinie` | Handlinie und Ebenenlinie hinter einer Schnittstelle: Urteil, Widerstand bei N_Ed, Eckwerte, Probe |
| `nachweis/rechenwahl` | Kriechzahl, Werte, Rechenart -- die eine Stelle, die daraus Gesetze und Löser baut |
| `nachweis/querschnittsloeser` | Dehnungsebene aus N und M, zwei Bisektionen |
| `nachweis/` | M-N, Querkraft (mit Bügeln), Duktilität, sprödes Versagen, Zwängung auf Normalkraft und auf Biegung, Stahlspannung unter häufiger (gegen Fliessen) und quasi-ständiger Last (aus der Rissbreite), Knicken am verformten System |
| `nachweis/schiefe_biegung`, `schubwandnachweis`, `richtungsnachweise` | die Nachweise der Querschnittsanalyse: N mit M_y und M_z, Querkraft mit Torsion, Duktilität und sprödes Versagen je Richtung |
| `spannungsanalyse.py` | sechs Fragen an den Querschnitt: Bild aus N und M oder aus Dehnungen, M-χ- und N-ε-Linie, äquivalenter E-Modul über M und über N — kein Nachweis |
| `bewehrungssuche/` | die kleinste Bewehrung suchen, die alle Nachweise erfüllt – Längsbewehrung, dünnste Platte, Bügel |
| `bericht/` | der Bericht als Blöcke (`gliederung`), gesetzt als Konsolentext, LaTeX-Dokument (PDF, sobald eine TeX-Maschine da ist) und Markdown; die Zusammenfassung je Platte |
| `projekt/` | speicherbare Projektbeschreibung (`eintraege`, `platte`, `querschnittsanalyse`, `balkensystem`, `projekt`) und was daraus gebaut wird (`aufbau`) |
| `ergebnis.py` | ein gerechnetes Projekt: Zusammenfassung, Bericht, LaTeX, Markdown, Analysen |
| `notizbuch/` | das Notizbuch: Formel-, Themen- und Python-Seiten für Obsidian und die Dokumentation der Seite (`formelseiten`, `bibliothek`), geschrieben ohne Handgeschriebenes anzufassen (`tresor`) |
| `web/bruecke.py` | was der Browser lädt: das Verzeichnis des Kerns, die Seiten des Notizbuchs, die Versionsmarken |
| `web/api.py` | Lösung, Mitschrift und Zusammenfassung als JSON |
| `web/diagrammdaten.py` | die Punktfolgen der Diagramme als JSON |
| `web/balkendaten.py` | was die Oberfläche von einem Balkensystem zeigt: Übersicht und Verläufe |
| `web/speicher.py` | Ergebnisse je Bauteil, damit nur Geändertes neu rechnet |
| `web/dienst.py` | der Rechendienst, unabhängig vom Transportweg |
| `web/server.py` | HTTP-Hülle darum (nur Standardbibliothek) |
| `web/js/kern.js`, `kern_arbeiter.js` | Pyodide-Hülle darum, in einem eigenen Faden, für die Seite ohne Server |
| `web/js/` | Oberfläche in reinem JavaScript, ohne Bauschritt |
| `web/js/cad_*.js` | das Zeichenfenster, allgemein: Ansicht, Knoten und Elemente, Punkteingabe, Befehle, Auswahl, schwebendes Fenster |
| `web/js/qa_zeichnung.js`, `qa_uebersicht.js`, `qa_vorlagen.js` | was es in der Querschnittsanalyse zeichnet, die Liste darunter und die Vorlagen |
| `web/js/querschnittsanalyse.js`, `qa_diagramme.js` | ihre übrige Eingabe und ihre Diagramme |
| `web/js/bs_zeichnung.js`, `bs_symbole.js` | was es im Balkensystem zeichnet: Stäbe, Lager, Federn, Gelenke, Lasten |
| `web/js/balkensystem.js`, `bs_diagramme.js` | die übrige Eingabe des Balkensystems und seine Ergebnisse |

Wie das zusammenhängt und warum es so gebaut ist, steht in
[Entwicklung](notizbuch/Notizen/Entwicklung.md).

## Oberfläche

Drei Tafeln: links die Bestandteile des Projekts, in der Mitte die Eingaben zum
ausgewählten Bestandteil, rechts das Ergebnis. Unter 900 px Fensterbreite steht
eine Tafel allein und ein Umschalter am unteren Rand wechselt zwischen ihnen --
dieselbe Aufteilung, nur nacheinander.

Die Oberfläche rechnet nichts. Sie schickt die Projektbeschreibung an den Kern
und stellt dar, was zurückkommt -- fertige Zahlen und fertige LaTeX-Zeichen­ketten.
Deshalb kann am Bildschirm gar nichts anderes stehen als im Bericht.

**Spannung-Dehnung-Analyse:** bei jeder Platte unter «Weitere Analysen».
Kein Nachweis, sondern die Frage, was im Querschnitt geschieht:
* *N, M* oder *ε oben/unten* -- Dehnung und Spannung über die Höhe;
* *M–χ* -- die Momenten-Krümmungs-Linie bei fester Normalkraft;
* *N–ε* -- die Normalkraft-Dehnungs-Linie auf Zug bei festem Moment;
* *M–E_eq* und *N–E_eq* -- dieselben Linien, umgerechnet in den
  äquivalenten E-Modul: den Modul, den ein reiner Betonquerschnitt b·h
  (ungerissen, ohne Stahl, elastisch) bräuchte, um sich gleich stark zu
  krümmen bzw. zu dehnen -- `E_eq = M/(I_c·(χ − χ_0))` mit `I_c = b·h³/12`,
  `E_eq = N/(A_c·(ε_m − ε_0))` mit `A_c = b·h`, gezählt ab dem Zustand ohne
  laufende Kraft. Ein Wert, den man in ein Modell mit ungerissenem Beton
  eingeben kann.

Eine Linie ist ungerissen bis zum Riss, springt dort und ist darüber gerissen.
Sie endet bei der ersten Grenzdehnung, wie im Dehnungsfächer. An den Ecken
stehen Riss, Fliessbeginn (M_y, N_y) und Ende (M_Rd, N_Rd), je mit Kraft und
Verformung, am Ende auch die massgebende Grenze; im E_eq-Bild an jeder Ecke
der Modul und sein Vielfaches von E_cm. Das Ende ist der Widerstand: bei
derselben Rechenwahl dieselbe Zahl wie in der Tragsicherheit. Gestrichelt
stehen zum Vergleich der ungerissene Zustand, nur bis zum Riss, und der
gerissene. Die Zugfestigkeit des Betons zählt nur für den Riss. Jede Analyse
wählt selbst, wie die Nachweiskapitel (unten), aber ohne Handrechnung; φ
wirkt dort immer auf den ungerissenen Teil.

**Rechenwahl:** Unter dem Kopf der Tragsicherheit, der beiden
Stahlspannungskapitel und des Knickens steht eine Zeile «Rechenwahl», beim
Knicken zwei -- «Verformung (e_2d)» und «Widerstand (N_Rd)». Gewählt werden:
* die Kriechzahl φ, Vorgabe 0 -- sie wirkt nur präzise und elastisch,
  sonst ist das Feld blass;
* die Werte: Bemessung (f_cd, f_yd → M_Rd) oder charakteristisch
  (f_ck, f_yk → M_Rk);
* die Rechenart: *Handrechnung* (Spannungsblock 0.85·x, Druckstahl
  weggelassen, je Seite eine Lage), *0.85·x-Vereinfachung* (derselbe Block,
  mit Druckstahl, über die Fasern gerechnet) oder *Präzise ohne
  Vereinfachung* (Parabel-Rechteck); bei den Stahlspannungen dazu
  *elastisch*, ihre Vorgabe. Das Knicken und die Analysen bieten keine
  Handrechnung an: dort wird die Normalkraft Ebene für Ebene genau
  gerechnet. Der Widerstand beim Knicken rechnet darum, wenn nichts anderes
  gewählt ist, mit der 0.85·x-Vereinfachung.

Mit 0.85·x oder präzise hält die Tragsicherheit gegen den Rand des
Dehnungsfächers; den Widerstand bei N_Ed sucht sie genau, und die Herleitung
zeigt die Probe des Bruchzustands. Querkraft und sprödes Versagen lesen ihr
m_R aus derselben Linie. Wählt das Knicken für den Widerstand dasselbe wie die
Tragsicherheit, nimmt es deren Linie, sonst eine eigene. Die Kriechzahl der
Platte dient nur noch dem Vergrösserungsfaktor w/w_c (SIA 262:2025,
4.4.3.2.5); er steht je gezogene Seite in der Zusammenfassung.

**Querschnittsanalyse:** unter den Platten ein zweites Kapitel. Der
Querschnitt wird gezeichnet wie in einem kleinen CAD, aus Knoten, Linien und
Flächen:
* eine Fläche ist Beton oder eine Aussparung;
* ein Knoten ist ein Punkt oder ein Stab;
* eine Linie ist eine Bewehrung (nach Anzahl, Teilung oder verschmiert),
  eine Schubwand mit Bügeln oder eine Hilfslinie.

Gewählt wird per Klick oder Rahmen; verschoben und kopiert mit Basispunkt
und Ziel. Jeder Punkt fängt an Knoten, Mitten, Schnittpunkten und am Raster.
Genau setzen lässt er sich mit R (Bezugspunkt), Y/Z (Achse), P/S (parallel,
senkrecht) und M (Mitte), die Zahlen getippt. Alle Eigenschaften stehen im
schwebenden Fenster in der Zeichnung. Mit T kommt eine Vorlage dazu --
Rechteck, T-Balken, Hohlkasten oder Kreis, die Skizze ändert sich beim
Tippen der Masse. Rückgängig mit Strg+Z, Vollbild.
Darunter eine Liste: Meldungen, Querschnittswerte, je Element eine Zeile.
Was die Rechnung braucht -- die Stäbe einer Linie samt tatsächlicher
Teilung, Schwerpunkt, Zellen, Meldungen am Element -- kommt vom Kern. Darunter
je Material Bemessungs- oder charakteristische Werte und beim Beton das
Gesetz, die Lastfälle mit N, M_y, M_z, V_y, V_z und T, der Schalter «nur
einachsig» und die Nachweisschalter.

**2D Balkensysteme:** unter der Querschnittsanalyse ein drittes Kapitel,
ein ebener Rahmen nach der Steifigkeitsmethode. Gezeichnet wird mit
demselben Fenster, in Metern: Linien werden Stäbe mit Querschnitt und
Material, Knoten bekommen ein Lager (gelenkig, verschieblich, eingespannt
oder je Richtung frei, fest, Feder), Stabenden ein Gelenk, Linien ein
Linienlager oder eine Bettung. Die Lasten des Lastfalls, der über der
Zeichnung gewählt ist, stehen in der Zeichnung und im schwebenden Fenster.
Anders als im Querschnitt hängt ein Rahmen an seinen Knoten: ein Klick an
einem Knoten wählt ihn, ein verschobener Stab nimmt seine Knoten mit.
Teilen und Umkehren rechnet der Kern -- dabei entstehen Lastwerte. Ist das
System beweglich, sagt es eine Meldung und markiert, was sich bewegt; eine
Drehung ohne Steifigkeit, an einem Knoten, an dem nur Gelenke hängen, ist
gestrichen und trägt ein Fragezeichen. Die Querschnitte kommen aus einer
Vorlage, von Hand, aus einer Platte oder aus einer Querschnittsanalyse; die
Steifigkeit nach Vorgabe, nicht nachgeschlagen: E_cm bzw. E_s am
ungerissenen Bruttoquerschnitt, ohne Schubverformung, Theorie 1. Ordnung.

**Rechte Tafel:**

* *Zusammenfassung* -- je Platte eine Tabelle: Widerstand, Einwirkung und
  Erfüllungsgrad. Darunter, in gedämpftem Rot, die ausgeschalteten Nachweise,
  die mit der vorliegenden Bewehrung *nicht* aufgehen würden. Das Auge am
  Ende jeder Zeile zeigt genau diesen Nachweis: der Kern löst rückwärts auf,
  rechnet nur das Nötige, und die Herleitung zeigt nur diese Schritte
* *Diagramme* -- Plattenquerschnitt, M-N-Resistenzlinie mit den
  Bemessungspunkten (die gestrichelte Strecke zeigt den Weg, in dem der
  Erfüllungsgrad gemessen wurde) -- massgebend die Linie der Rechenwahl,
  daneben zum Vergleich präzise oder die Handrechnung, und eine eigene
  Linie des Knickens --, Querkraftkurven, Spannungs-Dehnungs-Bilder;
  bei einer Querschnittsanalyse ein einziges Interaktionsdiagramm mit
  wählbaren Achsen (zwei von N, M_y, M_z, die dritte mit festem Wert; ein
  Klick auf einen Lastfall legt den Schnitt durch ihn), dazu je Lastfall der
  Bruchzustand im Schnitt und der Schubfluss in den Wänden; bei einem
  Balkensystem je Fall Verformung, N, V, M und Lagerkräfte -- mit der Maus
  darüber (auf dem Telefon: tippen) der Wert an der Stelle, an einem Knoten
  seine Verschiebung
* *Herleitung* -- die Mitschrift, Formel für Formel, mit Normstelle

**Kopieren nach Word, LaTeX und Markdown:** jede Formel und jede Tabelle hat
drei Knöpfe. *Word* legt eine Formel als MathML in die Zwischenablage -- Word
fügt daraus eine richtige, weiter bearbeitbare Gleichung ein, kein Bild --
und eine Tabelle als echte Tabelle, deren Formelzellen Gleichungen sind. *TeX*
legt den LaTeX-Quelltext ab, für Overleaf oder den Formeleditor von Word 365.
*MD* legt den Block so ab, wie er im Markdown-Bericht steht.

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
stellt die Richtung einer Lage um; die andere Lage derselben Seite bekommt
zwingend die Gegenrichtung.

Die Bewehrungssuche bemisst die y-Lagen nicht. In y wird nichts nachgewiesen,
also gäbe es dort kein Mass, an dem sich ein Durchmesser bemessen liesse -- sie
zöge ihn auf null, und genau das wäre falsch. Was in y liegt, sagt der Benutzer,
oder die y-Grundbewehrung folgt der x-Grundbewehrung («y-Grundbew. wie x»).
Dünner als der Mindestdurchmesser bleibt sie aber nicht: die Grundbewehrung
jeder Lage hat ihn mindestens.

Mehr als die **Obergrenze** bekommt keine x-Lage: eingegeben wie eine Lage,
Grund ⌀@s plus Zulage ⌀@s (Vorgabe ⌀30@150 = 4712 mm²/m), und es zählt die
Summe je Lage. Mit dem Schalter «Plattendicke optimieren» sucht sie dazu die
**dünnste Platte**: halbieren oder verdoppeln, dann Bisektion auf den
Zentimeter -- nie unter die Mindestdicke (Vorgabe 150 mm) und nicht über 2 m.

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

In der Querschnittsanalyse:

* `y` nach rechts, `z` nach oben, Bezugspunkt der Schwerpunkt des
  Bruttoquerschnitts
* `N > 0` = Zug. Ein positives Moment zieht auf der negativen Seite seiner
  Achse: `M_y > 0` unten (wie bei der Platte), `M_z > 0` links
* `V_y`, `V_z` in Achsrichtung, `T > 0` im Gegenuhrzeigersinn

Im Balkensystem:

* `x` nach rechts, `z` nach oben, in m; Verschiebungen und Lagerkräfte
  positiv entlang der Achsen, eine Lagerkraft nach oben also positiv
* Drehungen und Momentlasten im Gegenuhrzeigersinn positiv
* Kraftlasten positiv in Pfeilrichtung: *senkrecht* nach unten, *waagrecht*
  nach rechts, *quer* zur gestrichelten Faser, *längs* vom Anfang zum Ende
* Schnittgrössen nach Baustatik: `N > 0` Zug, `M > 0` zieht an der
  gestrichelten Faser -- rechts der Laufrichtung, bei einem Stab von links
  nach rechts also unten --, `dM/dx = V − m`
* Querschnittsmasse in mm, Lasten in kN, kN/m, kNm, kNm/m; Federn in kN/m und
  kNm/rad, Bettung in kN/m²

## Erfüllungsgrad beim M-N-Nachweis

Ob ein Punkt innerhalb der Resistenzlinie liegt, entscheidet die massgebende
Linie der Rechenwahl -- bei 0.85·x und präzise an ihren genau gesuchten Rändern
bei dieser Normalkraft. Nur *wie weit* er entfernt ist, hängt vom gewählten
Massstab ab:

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
* **Balkensysteme**: Eigengewicht aus dem Querschnitt, Umhüllende der
  Kombinationen, Theorie 2. Ordnung, Schubverformung, schiefe Lager und die
  Übergabe der Schnittgrössen an die Querschnittsnachweise fehlen noch.
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
