# Entwicklungsprotokoll

Was gebaut wurde, und vor allem **warum es so gebaut ist**. Das Was steht im
Code; das Warum geht sonst verloren. Neueste Einträge oben.

Wer das Werkzeug bloss benutzen will, liest [README.md](../../README.md).

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
              │ HTTP, CPython      │   │ Pyodide im Browser,  │
              │ kann zusätzlich    │   │ in eigenem Faden;    │
              │ PDF übersetzen     │   │ lädt die .py-Dateien │
              │                    │   │ übers Netz nach      │
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

## 2026-10-25 · Aufgeräumt: Doppeltes im Balkensystem, ein Weg zum Ändern

Befund 1.2 der Strukturdurchsicht vom 2026-10-25: Reste aus den Tagen davor.

- **`AUS_BAUTEIL`** statt `E_EQ_ARTEN` und `MIT_MATERIAL`: zwei Namen für
  dasselbe Tupel. Ein Querschnitt aus einer Platte oder Analyse bringt ein
  Material mit und hat ein E_eq -- beides, weil er ein Bauteil mit Bewehrung
  nimmt.
- **Kein Umweg mehr über den Adapter:** `aktiverLastfall`, `lastfallWaehlen`
  und `passendeUebersicht` nehmen das Zeichenfenster `a` statt der Kennung
  und stehen mit `eintragVon` und `abdruckVon` in `bs_teile.js`. Das
  schwebende Fenster liest sie dort wie das Zeichenfenster; die drei Glieder
  des Adapters, die nur dafür da waren, sind weg.
- **`eintragAendern(liste, kennung, veraenderer)`** in `zustand.js`: dieselbe
  Funktion stand siebenmal da, als `aendernAn` oder `schreiben`, je App und
  im Balkensystem zweimal. Gibt es den Eintrag nicht mehr, ändert sich
  nichts -- das tat bisher nur die Kopie in `python.js`, deren Speichern
  verzögert kommt.

---

## 2026-10-25 · Eine Zuweisung an ein Feld, das es nicht gibt, scheitert laut

Befund 1.1 der Strukturdurchsicht vom 2026-10-25: `Beschreibung.__setattr__`
nahm jeden Namen an. Eine Zuweisung an ein Feld, das es nicht gibt, legte
still ein neues Attribut an.

- **Gefunden hat es drei Tests, die nichts mehr prüften oder Totes
  setzten:** `richtung` an einer Kombination (in den Hilfen von
  `test_querkraft`, `test_schnittstelle`, `test_bewehrungssuche`), `stahl`
  an den Bügeln (das Feld fiel am 2026-10-24 weg) und `kriechzahl` an der
  Platte -- «das φ der Platte spielt keine Rolle» prüfte seit dem
  Verformungsnachweis nichts. Er prüft jetzt, dass das φ der Tragsicherheit
  und das der Verformung die Zwängung nicht ändern.
- **Jetzt:** ein Name, der kein Feld ist, wirft `ProjektFehler` mit dem
  ähnlichsten Feld, mit demselben Satz wie beim Lesen einer Datei
  (`unbekanntes_feld` in `lesen.py`, beide nehmen ihn). Ein Tippfehler im
  Baukasten (`q.knicklange = 4`) bleibt nicht mehr ohne Wirkung.

---

## 2026-10-24 · Balkensystem: auch die Statik-Analyse ein Knopf

Wunsch des Benutzers: die Statik-Analyse soll ebenfalls ein Knopf sein.

- Ein fünftes Kapitel in eigener Gruppe «Analyse», mit dem Zeichen eines
  Trägers auf zwei Lagern und seinem Moment; darunter klein «4 Diagramme».
  Das Fenster zeigt die Zeilen, die vorher im Panel standen, samt «+
  Diagramm».
- Unter den Eingaben steht damit kein Panel mehr, nur die Knöpfe -- anders
  als noch beim Eintrag «vier Knöpfe mit Fenstern», wo die Statik-Analyse
  bewusst ein Panel blieb.

---

## 2026-10-24 · Aufgeräumt: das Zeichenfenster des Balkensystems in drei Dateien

Auftrag des Benutzers, nach dem Vorschlag im Bericht: `bs_zeichnung.js` war
über 1100 Zeilen lang.

- **`bs_eigenschaften.js`** (rund 460 Zeilen): das schwebende Fenster --
  was ein Werkzeug als Nächstes anlegt, die Felder von Knoten, Linien und
  Lasten, mehrere zugleich mit «Var».
- **`bs_teile.js`** (50 Zeilen): was Zeichnung, Fenster und Panels gemeinsam
  brauchen -- Katalog, Lastart, die Last zu einer Kennung, die Zugseite
  einer Linie, der Name eines Materials.
- **`bs_zeichnung.js`** (rund 680 Zeilen): Fenster, Adapter, Lasten anlegen
  und treffen, Kern, Zeichnen.
- **Keine Abhängigkeit im Kreis:** das schwebende Fenster kennt vom
  Zeichenfenster nur `a`; was es vom System braucht -- die Zeichnung, den
  Lastfall, die Übersicht des Kerns, das Umkehren --, gibt ihm der Adapter.
  `umkehren` nimmt dafür, was danach gewählt bleibt.
- Für den Benutzer ändert sich nichts; im Browser geprüft: Fenster eines
  Stabs, zweier Stäbe mit «Var» und Zugseite, eines Knotens, einer Last, die
  Vorgaben der Werkzeuge Linie und Last.

---

## 2026-10-24 · Platte: auch die Bügel aus dem Stahl der Platte

Entscheid des Benutzers: der Bügelstahl ist derselbe wie der übrige Stahl;
rückwärts verträglich muss es nicht sein.

- `QuerkraftbewehrungEintrag` hat keinen Stahl mehr; der Aufbau gibt den
  Bügeln den der Platte. Die Auswahl neben den Bügeln ist weg, die Platte
  zeigt nur noch auf Beton und Stahl (`materialien`).
- Eine ältere Datei mit `querkraftbewehrung.stahl` öffnet sich nicht mehr --
  wie gewünscht.

---

## 2026-10-24 · Listen unter der Zeichnung zu Beginn zugeklappt

Wunsch des Benutzers: im Balkensystem die Liste der Linien und Lager zu
Beginn zugeklappt -- in der Querschnittsanalyse ebenso die Flächen und die
Bewehrung unter der Zeichnung.

- **Eine Stelle:** `klappgruppe` in `bausteine.js` baut die Gruppe beider
  Listen; offen bleibt, was man aufgeklappt hat (`aufgeklappt` am Fenster,
  Ansichtssache). Vorher merkte sich das Balkensystem die zugeklappten,
  und die Analyse klappte gar nicht.
- **Analyse:** Flächen, Stäbe, Bewehrung, Schubwände und Hilfslinien klappen
  je für sich, mit ihrer Zahl im Titel; Meldungen und Querschnittswerte
  bleiben offen.

---

## 2026-10-24 · Balkensystem: vier Knöpfe mit Fenstern

Wunsch des Benutzers: im Balkensystem vier schöne Knöpfe -- Material,
Querschnitt, Lastfälle, Lastkombinationen --, die je ein Fenster öffnen,
wie bei der Querschnittsanalyse.

- **Dieselben Kacheln:** `kapitelPanel` und `kapitelFenster` aus
  `kapitel.js`, wie Platte und Analyse; je Knopf sein Zeichen, sein Name und
  darunter klein, wie viele es gibt («2 Querschnitte»). Zwei Gruppen:
  Tragwerk (Material, Querschnitte) und Lasten (Lastfälle,
  Lastkombinationen). Neue Zeichen: ein Walzprofil, ein Balken mit drei
  Lasten, das Summenzeichen.
- **Die Inhalte** der bisherigen Panels sind die der Fenster
  (`materialienInhalt` ...); Lastfälle und Kombinationen sind zwei.
- **Ein Querschnitt** öffnet sein Fenster wie bisher; darin führt «← alle
  Querschnitte» zurück -- es gibt nur ein Fenster zugleich.
- Die Statik-Analyse bleibt ein Panel: sie sagt, welche Diagramme rechts
  stehen, und man ändert sie im Blick auf sie.

---

## 2026-10-24 · Balkensystem: mehrere zugleich ändern, mit «Var»

Wunsch des Benutzers: sind mehrere Elemente gewählt, ändert das Fenster
alle zugleich; was sie gemeinsam haben, steht da, sonst «Var» -- auch bei
den Gelenken; eine Änderung gilt dann für alle.

- **Eine Regel:** `gemeinsam(werte)` gibt den gemeinsamen Wert oder `VAR`;
  `mitVar` setzt «Var» vor die Stellungen eines Schalters oder einer Liste,
  `zahlfeldMitVar` lässt das Feld leer mit «Var» darin. Gesetzt wurde schon
  vorher für alle -- nur zeigte das Fenster die Werte des ersten.
- **Linien:** Querschnitt, Material, Zugseite, Gelenke, Bettung. «gemäss
  Querschnitt» steht nur, wenn jeder Querschnitt der gewählten Stäbe eines
  mitbringt.
- **Knoten:** x und z -- eine getippte Lage gilt für alle, sie stehen
  danach in einer Flucht --, das Lager und je Richtung sein Halt; die
  Richtungen nur, wenn alle ein Lager haben.
- **Lasten:** der Lastfall immer, die Felder, wenn alle von derselben Art
  sind (bisher: «einzeln bearbeiten»).
- **Gelenke und «projiziert»** sind Schalter «ja | nein» statt Haken --
  ein Haken hätte kein «Var» zeigen können.

---

## 2026-10-24 · Platte: ein Stahl für alle Lagen

Wunsch des Benutzers: den Stahl nicht je Lage wählen, sondern einen für alle
Lagen, oben im Panel der Platte unter dem Beton.

- **Beschreibung:** `QuerschnittEintrag.stahl`; `LageEintrag` hat keinen
  Stahl mehr. Die Bügel behalten ihren eigenen -- sie sind keine Lage.
- **Rechnung unverändert:** der Aufbau gibt jeder `Bewehrungslage` den Stahl
  der Platte; die Nachweise rechnen weiter je Lage mit ihrem Stahl, es ist
  nur immer derselbe. Ohne Stahl scheitert die Platte mit einer Meldung --
  vorher bekam eine leere Lage still den ersten Stahl des Projekts.
- **Tests:** der Index bei zwei Stählen kommt jetzt aus einer zweiten Platte
  mit dem zweiten Stahl. Die Prüfungen, dass in einer Platte mit B700B unten
  und B500B oben jede Lage mit ihrem Stahl rechnet (2026-10-12), sind weg --
  eine solche Platte lässt sich nicht mehr beschreiben. Geblieben ist die
  des Lösers, der je Seite den Stahl ihrer Lagen behält.

---

## 2026-10-24 · Balkensystem: E_eq auch aus einer Platte

Entscheid des Benutzers: E_eq gibt es auch für einen Querschnitt aus einer
Platte -- immer in x-Richtung, Zug unten.

- **Eine Suche, zwei Quellen:** die Frage nach E_eq (`Modulfrage`) hat eine
  Quelle: `ModulAusAnalyse` -- das Paar der Analyse zur Zugseite des
  Moments, wie bisher -- oder `ModulAusPlatte`, das Paar der Platte in x
  (`loeserpaar`). Jede Quelle sagt, was sie liest (die Bezüge im
  Rechenwerk) und welches Paar gilt; Suche, Herleitung und E aus dem
  Befund sind dieselben.
- **Negatives Moment:** bei der Platte zieht es unten, nach Vorgabe; ein
  negatives M hat darum kein E_eq, und das System sagt es -- still mit |M|
  zu rechnen, hiesse die Zahl umzudeuten.
- **Prüfprojekt:** der Deckenstreifen bekommt ein E_eq bei 20 kNm, ohne
  Stab -- gesucht und hergeleitet wird es trotzdem, keine Zahl des Systems
  ändert sich.

---

## 2026-10-24 · Balkensystem: Querschnitte als Zeilen mit Bild und Fenster

Wunsch des Benutzers: jeder Querschnitt eine kompakte Zeile, links eine
Vorschau, A und I in der Zeile; ein neuer und ein Klick auf die Vorschau
öffnen ein Fenster, in dem man wählt, woher der Querschnitt kommt; die
Vorlage als Auswahlliste mit kleiner Vorschau.

- **Umriss vom Kern:** `balkendaten.umrisse` gibt je Querschnitt seine
  Polygone in mm -- die Vorlage mit ihren Massen (`Stabvorlage.umriss`), den
  Streifen b × h einer Platte mit ihren gerechneten Werten, die Polygone
  einer Analyse samt Aussparungen; Kennwerte von Hand und ein Querschnitt,
  der nicht geht, keine. Die Antwort `rechnen` trägt sie als `stabumrisse`,
  auch wenn das System nicht rechnet. Die Oberfläche passt sie nur ins
  Bild; gezeichnet wird gerade-ungerade, so bleiben Löcher Löcher.
- **Zeile:** Bild (ein Knopf), Name, A und I vom Kern -- ohne sie die
  Meldung des Kerns zum Querschnitt --, Herkunft mit Massen, «trägt».
- **Fenster:** das Fenster über der mittleren Spalte, wie bei den Kapiteln
  einer Platte (`fenster.js`, Schlüssel `querschnitt:Q1`); es wird mit dem
  Editor neu gezeichnet und zeigt darum immer den Stand. Darin die Felder,
  die vorher im Panel standen, die Vorlage als Auswahlliste mit Bild -- auf
  Wunsch des Benutzers, in [[Arbeitsweise]] als Ausnahme vermerkt -- und
  das E der Stäbe gemäss Querschnitt.
- **Nebenbei behoben:** wer «A und I aus» auf Kennwerte stellte, behielt
  die Masse der Vorlage, und der Kern meldete «einen Kennwert «b» gibt es
  nicht». Jetzt bekommt eine Vorlage ihre Vorgaben, Kennwerte beginnen leer.

---

## 2026-10-24 · Balkensystem: eigene Materialien als Tabelle

Wunsch des Benutzers: im Panel «Materialien» zuerst Materialien anlegen,
je Zeile eines -- ein Beton des Projekts, dessen E und Dichte man nicht
ändern kann, oder ein Material mit E und Dichte von Hand; an der Linie nur
diese und «gemäss Querschnitt»; am Querschnitt kein E mehr, nur noch die
Wahl E₀ oder E_eq, wenn eine Linie sein Material nimmt.

- **Beschreibung:** das System hat `stabmaterialien`
  (`StabmaterialEintrag`, Kennung «M1»: `beton` mit Verweis auf einen Beton
  des Projekts oder `eigen` mit `E` und `rho`). Eine Linie zeigt auf eines
  davon oder auf «gemäss Querschnitt». `materialien()` -- die Liste, die das
  Löschen im Projekt prüft -- nennt die Betone, auf die ein Material zeigt.
- **Kein E am Querschnitt:** `E` und die Stellung «Zahl» sind weg; ein E von
  Hand hat jetzt ein eigenes Material. `e_modul` heisst `e0` oder `e_eq` und
  gilt nur für einen Stab mit dem Material des Querschnitts -- mit einem
  Material des Systems nimmt er dessen E, auch bei einer Analyse.
- **Rechnung:** der Aufbau löst jedes Material zu einem `Stabmaterial` auf
  (Beton oder Zahlen von Hand); `Balkensystem` braucht keine Baustoffe mehr
  daneben. Ein eigenes Material schreibt E und ρ als Eingaben in die
  Herleitung, einmal je Material. Das Material des Querschnitts trägt im
  Zeichen keinen Index: es kann wie ein Material des Systems heissen.
- **Meldungen:** ein Material ohne Beton, eines, das auf Betonstahl zeigt,
  und eine Linie mit einem Material, das es nicht gibt, halten das System
  auf; ein Verweis auf einen Beton, den es nicht gibt, das Projekt -- wie
  bisher bei Platte und Analyse.
- **Oberfläche:** die Tabelle mit Kopf (Material, Art, E, ρ, trägt); E und ρ
  eines Betons grau vom Kern. An der Linie die Materialien des Systems und
  «gemäss Querschnitt», wenn der Querschnitt eines mitbringt -- und
  umgekehrt bei «gemäss Querschnitt» nur solche Querschnitte. Ein neues
  System bekommt den ersten Beton des Projekts; eine neue Linie das erste
  Material.
- **Beispiele:** im Prüfprojekt sind Stahl (E_s, ρ_s) und der weichere
  Fundamentbeton (E = 15000) eigene Materialien -- jede Zahl des Berichts
  bleibt, nur die Namen wechseln.

---

## 2026-10-24 · Balkensystem: die Zugseite je Stab

Wunsch des Benutzers: je Stab festlegen, welche Seite die Zugseite ist;
von selbst unten, bei einer senkrechten Linie links, und umzuschalten.

- **Kein neues Feld:** die Zugseite ist die gestrichelte Faser, und die
  liegt schon immer rechts der Laufrichtung; «Umkehren» legte sie auf die
  andere Seite. Ein eigenes Feld hätte die Laufrichtung bedeutungslos
  gemacht, und jede Stelle, die die Faser zeichnet oder rechnet -- Lasten
  quer, Linienlager, Diagramme, Herleitung --, hätte es kennen müssen.
- **Von selbst:** eine neu gezeichnete Linie läuft nach rechts, eine
  senkrechte nach unten -- wie herum man sie auch zeichnet
  (`linieAnlegen`). Die Beispiele behalten ihre Richtung: im Rahmen liegt
  die Faser innen.
- **Schalter:** «Zugseite» im Fenster eines Stabs, mit den Stellungen unten
  | oben, bei einem senkrechten links | rechts. Er kehrt die Linie im Kern
  um, wie «Umkehren»: die Lasten bleiben, wo sie wirken -- eine Last quer
  zum Stab wechselt dabei ihr Vorzeichen --, die Gelenke an ihren Knoten.
  Bei mehreren gewählten Linien steht er, solange alle senkrecht oder alle
  nicht senkrecht liegen.

---

## 2026-10-24 · Balkensystem: Verdrehung in der Statik-Analyse

Wunsch des Benutzers: neben der Verschiebung auch die Verdrehung.

- **Kern:** der Verlauf eines Stabs gibt je Stelle `phi`, die Verdrehung des
  Querschnitts -- die Ableitung der Biegelinie, im Gegenuhrzeigersinn
  positiv, für jeden Stab gleich, wie er auch liegt. Die grössten Werte je
  Stab sucht `extrem("phi")` wie bei M: an den Enden und wo sich die
  Verdrehung nicht ändert.
- **Diagramm:** die Stellung «Verdrehung» im Schalter jeder Zeile; das Bild
  trägt φ in mrad auf wie einen Verlauf, bernsteinfarben, mit den Werten an
  den Enden und den grössten je Stab.
- **Geprüft:** am Einfeldträger unter q an den Lagern ±qL³/24EI, in der
  Mitte null.
- **Nebenbei:** der Rand um jedes Diagramm war für die grösste Ordinate
  und ihren Wert zu knapp -- an einer äusseren Stütze stand «.67» statt
  «-1.67». Jetzt reicht er für beides, mit Stelle (`RAND` in
  `bs_diagramme.js`).

---

## 2026-10-24 · Balkensystem: der Lastfall in der Leiste

Wunsch des Benutzers: im Zeichenfenster neben «Last» den Lastfall wählen,
auch «– kein Lastfall –»; zu Beginn das Eigengewicht.

- Das Zeichenfenster hat einen Platz gleich neben den Werkzeugen
  (`adapter.leisteZusatz`); die Leiste wird einmal gebaut, das
  Balkensystem füllt ihn bei jedem Neubau der Tafel neu (`lastfallLeiste`),
  damit er jeden Lastfall kennt.
- «– kein Lastfall –» ist `''` im Zustand des Fensters; ohne Wahl gilt der
  Lastfall mit dem Eigengewicht, sonst der erste (`aktiverLastfall`).
- Die Liste «Lastfall» über der Zeichnung und im Fenster des Werkzeugs ist
  weg; eine gewählte Last wechselt ihren Lastfall weiter in ihrem Fenster.

---

## 2026-10-24 · Balkensystem: Kleinigkeiten der Oberfläche

Wünsche des Benutzers, je eine Zeile:

- **Kombinationen:** die Zahlenfelder so schmal, dass 999.99 gerade Platz
  hat -- in em gemessen (sechs Zeichen JetBrains Mono zu 0.6 em); «6ch»
  löste sich im Rahmen schmaler auf als im Feld.
- **Lastfälle:** die Namen gleich breit untereinander -- die Spalte daneben
  hat eine feste Breite, auch beim längeren Satz des Eigengewichts.
- **Liste unter der Zeichnung:** Linien, Lager und Lasten klappen je auf und
  zu; zu bleibt, was man zugeklappt hat (Ansicht, nicht Projekt).
- **Lagerkräfte lesbar:** die Regel `.bs-reaktion` färbte auch den weissen
  Rand der Zahlen grün; jetzt nur noch die Striche, und im Diagramm stehen
  die Zahlen so gross wie dessen übrige.

---

## 2026-10-24 · Querschnitt: verschmierte Linie aus ⌀, Teilung und Länge

Wunsch des Benutzers: bei verschmierter Bewehrung entweder die Stahlfläche
eingeben oder Durchmesser, Teilung und Länge -- daraus L/s · π⌀²/4, und die
Fläche steht grau darunter.

- **Beschreibung:** an der Stablinie `verschmiert` (`flaeche` | `staebe`,
  `VERSCHMIERT` in `querschnitt/geometrie.py`) und `laenge` (leer: die der
  Linie). ⌀ und s sind die Felder, die die Linie nach Teilung auch hat --
  wer die Art wechselt, findet seine Zahlen noch vor.
- **Eine Stelle:** `linienflaeche` in der Geometrie bestimmt die Fläche jeder
  Stablinie. Vorher stand die Regel zweimal, in der Analyse und in der
  Antwort für das Zeichenfenster (`api.geometrie`). Die graue Zahl im
  Fenster ist die Fläche dieser Antwort.
- **Herleitung:** in der Tabelle «Bewehrung» «verschmiert: ⌀10 @ 200 auf
  300», darüber der Ansatz A_s = L/s · π⌀²/4 (Formelsammlung «Verschmierte
  Stahlfläche aus Stäben»).
- **Mit ihrem ⌀** (Benutzer, Rückfrage 2026-10-24): die Grenze der
  Stahlspannung je Stab und «Überdeckung beachten» nehmen bei einer Linie
  aus ⌀ und Teilung deren ⌀; fiktiv (Stäbe alle 150 mm) bleibt nur die mit
  der Fläche von Hand (`Stabangabe.fiktiv`).
- **Nebenbei behoben:** die Normalkraft-Dehnungs-Linie stürzte ab, wenn die
  Suche nach dem Fliessbeginn auf eine Stelle ohne Gleichgewicht fiel -- sie
  hielt «keine Ebene» für «fliesst noch nicht» (`linie.py`). Getroffen hat
  es der Kastenträger des Prüfprojekts mit der neuen Linie; ohne sie ändert
  die Korrektur keine Zahl.

---

## 2026-10-24 · Querschnitt: Materialien pastell

Wunsch des Benutzers: im gezeichneten Querschnitt Beton pastellgrün,
Betonstahl pastellrot, Schubwände pastellgelb, Baustahl pastellblau -- den
es noch nicht gibt.

- Eigene Farbmarken je Material, eine helle Fläche und eine kräftigere
  Linie (`--mat-beton`, `--mat-stahl`, `--mat-wand`, `--mat-baustahl`, je
  mit `-linie`). `--beton` und `--stahl` bleiben: sie färben auch die Köpfe
  der Tafeln, und die sollen nicht grün und rot werden.
- Gilt für Zeichnung und Vorlagen des Querschnitts, die Schraffur der
  Zellen (gelb wie die Wände) und die Zeilen «Rechenwerte je Material» --
  dort steht dasselbe Material in derselben Farbe.

---

## 2026-10-24 · Balkensystem: E_eq der Querschnittsanalyse bei N und M

Letzte Etappe des neuen Balkensystems. Entschieden (Rückfrage): E₀ ist E_cm
-- das gibt «vom Material» schon, eine eigene Stellung braucht es nicht;
N und M stehen am Querschnitt; ein E für EA und EI.

- **Beschreibung:** dritte Stellung `e_eq` am Querschnitt, nur bei einer
  Analyse (`E_EQ_ARTEN`); dazu `eq` mit N, M und den Rechenwerten einer
  Spannung-Dehnung-Analyse (φ, Werte, Rechenart).
- **Gerechnet im Rechenwerk**, nicht in der Auswertung danach -- es geht in
  die Rechnung ein. `modul_bei` in `spannungsanalyse/modul.py` nimmt das Paar
  der Analyse (`schnittpaar`) und dieselbe Regel wie die Linie M–E_eq:
  ungerissen bis M_Riss(N), darüber gerissen, gezählt ab χ₀; die Formel
  selbst ist die der `Modullinie`. Ein Test hält es gegen die Linie: am
  Anfang gleich, bei 80 kNm zwischen ihren beiden Punkten daneben.
- **Scheitern ohne das Projekt aufzuhalten:** die Suche (`ModulProzedur`)
  hat keine Ausgabe, nur einen Befund. E kommt aus ihm (`ModulAusBefund`)
  und ist nur anwendbar, wo sie einen Modul fand; sonst fehlen E, EA und EI,
  die Rechnung des Systems liest den Befund und meldet «kein E_eq – …».
  Wie ein bewegliches System: das System rechnet nicht, der Rest schon.
- **Generisch geblieben:** das Stabwerk kennt die Analyse nicht. Der Aufbau
  hängt eine `Modulfrage` an den Querschnitt, sie baut ihre Berechnungen
  selbst ein (`einbauen`).

---

## 2026-10-23 · Balkensystem: Statik-Analyse mit «+ Diagramm»

Wunsch des Benutzers: wie in der Spannung-Dehnung-Analyse eine
Statik-Analyse, in der man Diagramme anlegt -- je Zeile ein Lastfall oder
eine Kombination (Auswahlliste) und M, V, N oder die Verschiebungen. In den
Diagrammen die grössten Werte angeschrieben, und wo sie liegen. Der Knopf
heisst «+ Diagramm», nicht «+ Bild» -- auch in der Spannung-Dehnung-Analyse
von Platte und Querschnitt (eigener Commit).

- **Beschreibung:** `diagramme` am System, je Eintrag `fall` (Kennung von
  Lastfall oder Kombination) und `groesse` (`DIAGRAMMGROESSEN`). Gerechnet
  wird damit nichts -- das System rechnet jeden Fall; die Liste sagt nur,
  welche Diagramme rechts stehen. Ein neues System bringt M, V, N der GZT
  und die Verschiebung der GZG mit. Die Bilder nur je Kombination (vorige
  Etappe) sind damit wieder offen: die Zeile wählt.
- **Lager dazu:** die Lagerkräfte hatten ein eigenes Bild; sie sind eine
  fünfte Stellung des Schalters, damit nichts verloren geht. Der Benutzer
  nannte nur M, V, N und Verschiebung -- fällt die Stellung weg, ist es eine
  Zeile in `DIAGRAMMGROESSEN`.
- **Angeschrieben:** die Werte an den Enden und je Stab der grösste und der
  kleinste, mit einem Punkt; im Feld darunter die Stelle «x = …». Die
  Extremwerte kommen genau vom Kern (`uebersicht.faelle[].staebe`), nicht
  aus den 24 Proben je Stab. Bei der Verschiebung je Stab die grösste
  Durchbiegung gegen die Sehne -- ein Stab, der sich nur mitbewegt, bleibt
  ohne Zahl.
- **Anfragen:** je System und Fall eine Antwort (`antwortZu`); zwei
  Diagramme desselben Falls teilen sie sich.

---

## 2026-10-23 · Balkensystem: Materialien unter der Zeichnung, E-Modul je Querschnitt

Vierte Etappe des neuen Balkensystems. Wünsche des Benutzers: unter der
Zeichnung eine Liste der Materialien und Querschnitte, deren wichtige
Eigenschaften sich ändern lassen; der E-Modul auch als Zahl, unabhängig vom
Material; das Material einer Linie getrennt vom Querschnitt, wahlweise
«gemäss Querschnitt».

- **Materialien:** ein Panel zwischen Zeichnung und Querschnitten, je
  Material des Projekts E-Modul und Dichte -- die Kennwerte, mit denen ein
  Stab rechnet. Welche das sind, sagt der Katalog (`kennwerte`, aus
  `E_MODUL` und `DICHTE` in `stabwerk/rechnung.py`). Die Zeilen sind die der
  App «Materialien» (`kennwertZeile` aus `material.js`): bei einer Normsorte
  gesperrt, bei einem eigenen Material hier wie dort zu ändern -- eine Regel,
  zwei Orte, ein Code. Welche Stäbe ein Material trägt, sagt der Kern
  (`zuordnung.balkensysteme.materialien`), samt denen «gemäss Querschnitt».
- **E-Modul je Querschnitt:** Schalter «vom Material | Zahl» (`e_modul`,
  `E` in N/mm²). Die Zahl gilt für jeden Stab mit dem Querschnitt, aus
  welchem Material auch immer; die Dichte kommt weiter vom Material. In der
  Herleitung eine Vorgabe «E-Modul, «…» (von Hand)», die Steifigkeiten
  heissen dann «mit E von Hand».
- **Material gemäss Querschnitt:** das Zeichen `MATERIAL_DES_QUERSCHNITTS`
  an der Linie. Aufgelöst wird es beim Aufbau: der Beton einer Platte, das
  eine Material der Flächen einer Analyse. Bringt der Querschnitt keines
  mit -- nach Vorlage, von Hand, eine leere Analyse, zwei Betone --, sagt es
  eine Meldung am System, und es rechnet nicht. Welche Arten eines
  mitbringen, steht einmal (`MIT_MATERIAL`); die Oberfläche bietet die Wahl
  nur dort an und liest es aus dem Katalog (`bringt_material`).

---

## 2026-10-23 · Balkensystem: Eigengewicht von selbst, GZT und GZG

Dritte Etappe des neuen Balkensystems. Wünsche des Benutzers: das
Eigengewicht als eigener Lastfall, von selbst aus der Dichte; Bilder nur für
die Kombinationen. Entschieden (Rückfrage): ein neues System bringt die
Lastfälle Eigengewicht, Auflast und Nutzlast mit, dazu die Kombinationen GZT
(1.35 / 1.35 / 1.5) und GZG (1.0 / 1.0 / 1.0); g = 10 m/s².

- **Welcher Lastfall:** einer trägt das Zeichen `eigengewicht`, höchstens
  einer -- zwei sind eine Meldung am System. Er lässt sich umbenennen, nicht
  löschen; eigene Lasten darf er zusätzlich haben.
- **Gerechnet im Kern:** je Paar aus Querschnitt und Material eine Formel
  `g_k = ρ · g · A` (Formelsammlung «Eigengewicht eines Stabs»), beim Beton
  mit ρ_sb, ohne den Stahl noch dazu. Vor dem Lösen kommt je tragenden Stab
  eine Linienlast senkrecht über die ganze Länge in den Lastfall, je Meter
  Stab, nicht projiziert. So steht sie in der Herleitung wie jede andere Last,
  und Kombinationen nehmen sie mit ihrem Faktor.
- **Gezeigt:** der Befund gibt das Eigengewicht je Stab mit
  (`Systembefund.eigengewicht`), die Übersicht in kN/m. Das Zeichenfenster
  zeichnet es grau im Lastfall, der es bekommt -- nicht zu wählen, nicht zu
  löschen. Die Übersicht fragt neu, wenn sich ein Material oder eine
  genommene Platte oder Analyse ändert, nicht nur die Zeichnung: sonst
  stünde nach einer neuen Dichte das alte g_k da. Wovon eine Antwort des
  Kerns abhängt, steht einmal (`abdruckVon` in `bs_zeichnung.js`) und gilt
  für Zeichenfenster und Diagramme -- vorher hatte jedes seine eigene Regel,
  die des Fensters enger. Gefragt wird bei jedem Neubau der Tafel; ist der
  Abdruck derselbe, bleibt es bei der letzten Antwort.
- **Bilder nur je Kombination:** die Wahl über den Bildern zeigt nur
  Kombinationen; ohne eine sagt ein Satz, wo man sie anlegt. Gerechnet
  werden die Lastfälle weiter -- die Kombinationen setzen sich aus ihnen
  zusammen, und die Herleitung zeigt sie.

---

## 2026-10-23 · Balkensystem: Lasten für sich, Linie und Knoten aufgeräumt

Zweite Etappe des neuen Balkensystems. Wünsche des Benutzers: im Fenster
einer Linie und eines Knotens zu viel; Lasten für sich wählen und löschen,
auf einer Linie oder an einem Knoten, eine Einzellast auch irgendwo auf der
Linie, in % zwischen ihren Knoten. Entschieden (Rückfrage): Gelenke bleiben
an der Linie, die Bettung eingeklappt; eine verteilte Last liegt immer auf
der ganzen Linie, mit Anfangs- und Endwert.

- **Beschreibung:** Jede Last hat eine Kennung (P1 …), Stab- und Knotenlasten
  zählen zusammen. Eine Stablast hat `stelle` in % statt `von`/`bis` in m.
  Das Feld `stab` der Linie ist weg: sie trägt, sobald sie einen Querschnitt
  hat (`stab` bleibt als abgeleitete Eigenschaft). Teilen verteilt eine
  verteilte Last auf beide Hälften, mit dem Wert am Schnitt, die zweite mit
  neuer Kennung; Umkehren spiegelt die Stelle. Alte Speicherstände mit
  Balkensystem öffnen sich nicht mehr -- das Programm legt sie beiseite.
- **Gespeichert an der Linie:** die Lasten bleiben in `linie.lasten`. So
  gehen sie mit ihr beim Kopieren, Teilen, Löschen und Rückgängig -- wie
  bisher, ohne Pflege an zwei Stellen.
- **Anhänge im Zeichenfenster:** was eine App an Elemente hängt und selbst
  zeichnet, lässt sich wählen und löschen (`adapter.anhaenge`: `treffer`,
  `hat`, `loeschen`, `rahmen`), aber nicht verschieben oder kopieren -- eine
  Last am Knoten nähme sonst den Knoten mit. Ein Werkzeug der Form «anhang»
  legt an, wo geklickt wird (`anhangBefehl`, `anhangAnlegen`).
- **Treffen:** jedes Lastzeichen trägt seine Formen mit (`formen` in
  `bs_symbole.js`): das Band einer verteilten Last ohne den Streifen an der
  Linie, den Schaft eines Pfeils ohne die Spitze, den Bogen eines Moments,
  dazu die Zahl. So trifft ein Klick auf den Balken den Balken.
- **Fenster:** Linie -- Querschnitt («– kein Stab –»), Material, Gelenke,
  «▸ Bettung». Knoten -- Lage und Lager. Last -- Lastfall, Richtung, Wert,
  Stelle, projiziert. Werkzeug «Last» Q -- dazu die Art als Schalter. Unter
  der Zeichnung eine Liste der Lasten; ein Klick wählt die Last und zeigt
  ihren Lastfall.

---

## 2026-10-23 · Dichte bei Beton und Stahl

Erste Etappe des neuen Balkensystems (Wunsch des Benutzers): das
Eigengewicht soll aus der Dichte des Materials kommen. Neue Kennwerte mit
Vorgabe, wie γ_c -- keine Normstelle, die Zahlen hat der Benutzer genannt:

- Beton: ρ_c = 2400 kg/m³ (unbewehrt) und ρ_sb = 2500 kg/m³ (Stahlbeton).
  Gerechnet wird mit ρ_sb: ein Stab aus Beton trägt seine Bewehrung, und die
  steckt in den 2500 kg/m³, ohne dass ihr Stahl noch dazukäme.
- Betonstahl: ρ_s = 7850 kg/m³. Dieselbe Zahl gab bisher das Bewehrungsmass
  als eigene Konstante in `querschnitt/platte.py`; sie steht jetzt als
  `STAHLDICHTE` beim Betonstahl, und beide lesen sie dort.

Wie jeder Kennwert: bei einer Normsorte gesperrt, bei einem eigenen Material
änderbar.

---

## 2026-10-23 · Kennzahlen auch beim gezeichneten Querschnitt

Wunsch des Benutzers: die Tabelle «Kennzahlen» der Platte auch in der
Zusammenfassung der Querschnittsanalyse. `nachweis/qa_kennzahlen.py`
rechnet sie, immer, auch ohne Lastfall:

- **Bewehrungsmass** μ_s = A_s,tot · 7850 kg/m³ / A -- Längsbewehrung ohne
  Bügel, wie bei der Platte.
- **Je Zugseite M_Rd bei N_Ed = 0** -- unten, oben, links, rechts, einachsig
  nur unten und oben; Zug oben und rechts negativ wie M_Rd⁻ der Platte.
  Derselbe Bruchzustand wie bei Duktilität und sprödem Versagen
  (`bei_reiner_biegung`), mit der Rechenwahl der Tragsicherheit -- die
  Platte nimmt dafür immer die Handrechnung mit Bemessungswerten.
- **N_Rd⁺ und N_Rd⁻ bei gleichmässiger Dehnung**: die Grenzen, gegen die der
  M-N-Nachweis reine Normalkraft hält. Bei der Platte heissen sie «bei
  M_Ed = 0»; an einem unsymmetrischen Querschnitt ist das nicht dasselbe.
- **x/d je Zugseite mit Bewehrung**, wie im Nachweis der Duktilität. Ob eine
  Seite Bewehrung hat, entscheidet die Zeichnung (Stäbe jenseits des
  Schwerpunkts) -- welche Kennzahlen es gibt, muss vor dem Rechnen
  feststehen.
- **Mit Schubwänden V_z,Rd, V_y,Rd und T_Rd**, je allein und ohne
  Normalkraft: die Verteilung ist linear, also trägt jede Wand v_Rd/q₁ der
  Last, wenn q₁ ihr Fluss je Einheitslast ist; massgebend die kleinste. Was
  die Wände nicht tragen können -- V_y bei lauter senkrechten Wänden, T ohne
  Zelle --, steht nicht da. Ein Test hält V_z,Rd und T_Rd gegen den Nachweis
  der Schubwände: mit ihnen als Last ist er gerade erfüllt.
- **Nicht übernommen:** Distanzhalter und Vergrösserungsfaktor gehören den
  Lagen und dem Verformungsnachweis der Platte; der Querkraftwiderstand ohne
  Bügel ihrer Rechnung je Meter.

Aufgeräumt dabei: die Festigkeiten einer Wand und die Neigungsgrenzen
stehen jetzt in der Analyse (`schubwaende_mit`, `neigungsgrenzen`) statt im
Nachweis der Schubwände -- die Kennzahlen brauchen sie auch. Und der
Durchmesser einer verschmierten Linie bei s = 150 mm stand nach dem Einbau
der Überdeckung zweimal da: in `stabgrenzen.py` (fiktiver Durchmesser der
Stahlspannung, seit 2026-10-15) und in `geometrie.py`. Jetzt nur noch in
`geometrie.aequivalenter_durchmesser`; `fiktiver_durchmesser` ruft sie.

---

## 2026-10-23 · Überdeckung: ein Hilfspolygon und «Überdeckung beachten»

Wunsch des Benutzers: beim Polygon eine Überdeckung in mm eingeben können,
Vorgabe 0. Darüber erscheint ein Hilfspolygon, so weit nach innen gerückt,
an dessen Ecken man fängt -- um Bewehrung einfach zu zeichnen. Und gewählte
Bewehrung soll sich auf Knopfdruck so verschieben, dass sie mit ihrem eigenen
Radius gerade ganz in diesem Polygon liegt; eine verschmierte Linie gilt
dafür als Stäbe mit dem äquivalenten Durchmesser bei s = 150 mm.

- **Gerechnet im Kern**, nicht in der Oberfläche: die Stablagen gehen in die
  Rechnung. `geometrie.py` rückt ein Polygon (`versetzt`: jede Kante um c,
  Ecken, wo sich die gerückten Kanten schneiden -- auch an einer
  einspringenden Ecke spitz; eine Kante, die sich umkehrt, fällt weg) und
  sagt, wohin ein Stab oder die Enden einer Linie müssen
  (`stab_in_ueberdeckung`, `linie_in_ueberdeckung`). Die Antwort `geometrie`
  trägt je Polygon das Hilfspolygon und je Stab und Linie die Lage
  `ueberdeckt`; der Knopf übernimmt sie nur.
- **Wohin:** auf den nächsten Punkt, an dem der Stab gerade ganz innen liegt
  -- ein ⌀20 aus der Ecke des Rechtecks mit c = 30 nach (40, 40); was schon
  innen liegt, bleibt. Jedes Ende einer Linie für sich; sind zwei Ränder
  gleich nah (an einer einspringenden Ecke), quer zur Linie.
- **Welches Polygon:** eines mit Beton nur für das, was in ihm liegt;
  sonst das nächste. Eine Aussparung mit c rückt nach aussen und schiebt
  Bewehrung aus sich hinaus -- so hat ein Hohlkasten auch innen seine
  Überdeckung. Gerückt wird jede Kante, auch die Fuge zu einem Nachbarn: wer
  einen Querschnitt aus mehreren Polygonen zeichnet, gibt c dem, an dessen
  Rand sie gilt.
- **Verschmiert:** der Durchmesser hängt an der Länge, und die ändert sich
  beim Verschieben. Gerechnet wird, bis beide zueinander passen -- ein
  zweiter Klick verschiebt nichts mehr.
- Was am selben Knoten hängt -- eine Polygonecke unter dem Ende einer
  Linie --, bleibt liegen (`verschieben` je Ecke).

---

## 2026-10-23 · Das offene Polygon fängt an seinen eigenen Ecken

Wunsch des Benutzers: beim Zeichnen eines Polygons sollen nicht nur die
Knoten fangen, die es schon gibt, sondern auch die Ecken, die das Polygon
selbst schon hat. Bis jetzt waren sie keine Knoten der Zeichnung -- das
werden sie erst beim Schliessen -- und fingen darum nicht.

Ein Befehl kann jetzt `fangpunkte()` haben: was er schon gesetzt hat. Das
Fangen (`cad_eingabe.js`) nimmt diese Punkte wie Knoten, mit demselben
Quadrat; auf eine Bindung (Y, Z, P, S) werden sie projiziert wie jeder
Punkt. Das Polygon gibt seine Ecken -- die erste gefangen schliesst es wie
bisher.

---

## 2026-10-23 · Einheit neben den Koordinaten, Fenster hält die Oberkante

Zwei Wünsche des Benutzers zum schwebenden Fenster:

- **Rechts neben jedem Koordinatenfeld die Einheit** -- im Querschnitt mm,
  im Balkensystem m, denn dessen Koordinaten sind Meter; beim Winkel °. Sie
  kommt aus `feldeinheiten` neben `feldnamen` (`cad_eingabe.js`), aus der
  Einheit der App. Das Winkelfeld heisst darum nur noch «α». Auch die Lage
  des Zeigers in der Ruhe trägt die Einheit. Die Felder sind dafür 7 statt 8
  Zeichen breit, sonst passte die Zeile nicht ins Fenster.
- **Die Oberkante bleibt stehen**, wenn der Inhalt wechselt -- etwa beim
  Umschalten der Bewehrung zwischen Linie und Punkt. Bisher hing das Fenster
  an seiner Unterkante. Gemerkt wird jetzt der Abstand von oben rechts, und
  es steht anfangs oben rechts. Reicht es über den unteren Rand, rückt es
  hinauf, bis es ganz zu sehen ist, und kehrt zurück, wenn es schrumpft.
  «Alles zeigen» hält darum oben oder unten frei, je nachdem, wo es steht
  (`einpassen` nimmt `frei` als `{rechts, oben, unten}`).

---

## 2026-10-23 · Die übrigen festen Listen werden Schalter

Wunsch des Benutzers, nach der Empfehlung: jede feste Wahl als Schalter. Eine
Wahl aus dem eigenen Projekt -- Lastfall, Querschnitt, Platte oder Analyse,
Fall der Diagramme, Kombination des Grundbruchs -- bleibt eine Liste wie die
Materialwahl: ihre Zahl wächst mit dem Projekt, als Knöpfe würde sie zu breit.

- **Nachweise:** Rissanforderung; Werte und Rechenart der Rechenwahl stehen
  jetzt untereinander -- nebeneinander fanden «Bemessung | charakteristisch»
  und vier Rechenarten keinen Platz. In der Zeile einer Analyse ebenso.
- **Querschnittsanalyse:** Werkstoffsatz und Betongesetz je Material, der
  Beton mit dem Gesetz in einer zweiten Zeile. Die Zugseite als Pfeile
  ↓ ↑ ← → (`Zugseite.pfeil` im Kern), «Zug unten» im Titel: vier Wörter
  passten nicht in die 80 px der Analysezeile. Die Achsen des
  Interaktionsdiagramms; der Modus der Bewehrungssuche untereinander.
- **Balkensystem:** «A und I aus» mit kurzen Namen (`kurz` im Katalog) unter
  dem Namen des Querschnitts, die Vorlage mit Umbruch; im schwebenden Fenster
  Lager, Halt je Richtung, Linienlager und Lastrichtung. Haben gewählte
  Knoten verschiedene Lager, steht keine Stellung an -- vorher hiess das
  «verschieden».

Neu dafür in `bausteine.js`: `wahlBlock` -- ein Schalter unter seiner
Beschriftung, als `div`. In einem `label` löste ein Klick auf die Beschriftung
die erste Stellung aus; darum stehen Schalter auch im Zeichenfenster nicht
mehr in `label.cad-zeile`. In `stil.css` die Spielarten `ist-wortlaut`
(Stellungen, wie sie geschrieben sind: 0.85·x, M_y), `ist-umbruch`,
`ist-senkrecht` und `ist-pfeile`.

---

## 2026-10-23 · Linien ohne Kette, Schalter statt Auswahllisten

Drei Wünsche des Benutzers:

- **Eine Linie, dann ein neuer Anfang.** Bis jetzt war das Ende einer Linie
  gleich der Anfang der nächsten, eine Kette. Jetzt wartet das Werkzeug nach
  dem zweiten Punkt wieder auf einen Anfangspunkt; der Bezugspunkt für
  Getipptes bleibt am Ende. Für beide Apps, weil die Linie dem Zeichenfenster
  gehört -- im Balkensystem zeichnet man einen Rahmen damit Stab für Stab.
- **Esc wie die Rücktaste**, auch bei der Linie: ein gesetzter Anfangspunkt
  geht zurück, erst ohne ihn endet das Werkzeug.
- **Keine Auswahllisten ausser für die Materialwahl** -- als Grundsatz in
  [[Arbeitsweise]]. Im Zeichenfenster sind die Verteilung der Bewehrung
  (verschmiert, Anzahl, Teilung) und das Raster nun Schalter, die Schnitte
  einer Schubwand ein Zahlenfeld; die Steifigkeit der Setzung ein Schalter.
  Dafür gibt es `wahlSchalter` in `bausteine.js`. Die übrigen Listen stehen
  im [[TODO]], dazu die Frage, ob eine Wahl aus dem eigenen Projekt -- ein
  Lastfall, ein Querschnitt -- eine Liste bleiben darf wie die Materialwahl.

Beim Prüfen fiel auf: das schwebende Fenster der Bewehrung ist mit allen
Feldern fast 400 px hoch und deckt im schmalen Panel die halbe Zeichnung --
ein Klick dorthin setzt keinen Punkt. Zuklappen geht (–), verschieben am Kopf.

---

## 2026-10-23 · Fangen sichtbar, Esc im Polygon

Zwei Meldungen des Benutzers:

- **«Das Fangen von Punkten scheint nicht mehr zu gehen»** -- etwa beim
  Verschieben entlang y über einen Punkt fahren, und der Zielpunkt soll seine
  Projektion auf die y-Linie sein. Gerechnet hat das Fenster das richtig;
  nur sah man es nicht: das Fangzeichen stand allein auf der Achse, oft weit
  weg vom Zeiger oder unter dem schwebenden Fenster, am angefahrenen Punkt
  nichts. Jetzt steht das Zeichen des Punktes an ihm selbst (□ Knoten, △
  Mitte, × Schnitt), eine gestrichelte Spur führt zur Stelle auf der Achse.
  Dazu fängt ein Punkt schon 12 px daneben statt 9 (`FANGWEITE`), Linien
  weiter bei 9: ein Punkt ist schwerer zu treffen als eine Linie.
- **Esc im Polygon** nimmt wie die Rücktaste den letzten Punkt zurück, statt
  alle zu verwerfen; erst ohne Punkt endet das Werkzeug.

---

## 2026-10-23 · Zeichenfenster des Querschnitts: ein Knopf je Art

Wunsch des Benutzers: im Querschnitt nicht «Linie» und «Knoten» wie im
Balkensystem, sondern je Art ein eigener Knopf mit Zeichen -- Bewehrung (als
Linie oder als Punkt), Schubwand, Hilfspunkt, Hilfslinie --, und in einem
Fenster immer nur eine Art, ohne Auswahlfeld zwischen Bewehrung, Schubwand
und Hilfslinie.

- **Die Werkzeuge gehören der App.** Das Zeichenfenster hatte drei feste
  Werkzeuge (Polygon, Linie, Knoten); welche Art eine Linie wurde, sagte das
  Feld «Art» im Fenster. Jetzt bringt jede App ihre Werkzeuge mit, je mit
  Namen, Zeichen, Taste und der Form, die es zeichnet (`einstellung.werkzeuge`).
  Die Befehle Knoten, Linie und Polygon tragen den Namen des Werkzeugs, das sie
  gestartet hat, und reichen ihn an den Adapter: eine Linie des Werkzeugs
  «schubwand» ist eine Schubwand. Das Balkensystem behält Linie und Knoten.
- **Querschnitt:** Polygon P, Bewehrung B, Schubwand W, Hilfspunkt K,
  Hilfslinie H, dazu Vorlage T. Die Bewehrung zeichnet als Linie oder als
  Punkt -- ihre Form ist eine Funktion des Werkzeugs, und der Schalter «Linie
  | Punkt» in ihrem Fenster startet es mit der anderen Form neu.
- **Ein Fenster, eine Art.** Die Felder «Art» beim Neuen und beim Gewählten
  sind weg, mit ihnen der Wechsel einer gezeichneten Linie in eine andere Art
  samt dem Gedächtnis dafür. Die Titel sagen, was es ist: «Linie 1 ·
  Linienbewehrung», «Stab 1 · Punktbewehrung».
- **Zeichen statt Schriftzeichen.** Die Knöpfe tragen Sinnbilder
  (sinnbilder.js), die Werkzeuge das Zeichen über dem Wort. Rückgängig,
  Wiederholen, Alles zeigen und Vollbild stehen klein zu zweit übereinander,
  nur als Zeichen -- so passt die Leiste in eine Zeile, auch im 500 px
  schmalen Panel.

---

## 2026-10-23 · Die App «Setzung»

Wunsch des Benutzers: eine Setzungsberechnung im Stil des Grundbruchs, mit
Bild der Situation -- Breite und Länge des Fundaments, Pressung aus
Wiederbelastung und aus Erstbelastung, beliebig viele Schichten mit Dicke,
M_E und M'_E; nachgewiesen wird, dass die Setzung unter einer zulässigen
bleibt. Die Theorie ist das Kapitel 8 «Setzungsberechnung», das er
mitgeschickt hat.

- **Gerechnet in Tabellenform, wie Kap. 8.3.** Jede Schicht in gleich dicke
  Teilschichten von höchstens Δz_max; je Teilschicht J an Ober- und
  Unterkante, gemittelt (die Spalte «J_K mittel» der Tabelle 8.4), und
  Δs = J·q_W·Δz/M'_E + J·q_E·Δz/M_E (Kap. 8.5). Die beiden Pressungen gibt
  der Benutzer getrennt an; aus Aushub und Gebäudegewicht rechnet die App
  sie nicht selbst. Unter der untersten Schicht gilt der Baugrund als
  unzusammendrückbar; wie viel J dort noch ankommt, steht unter der Tabelle.
- **Wo gerechnet wird, sagt die Steifigkeit** (Kap. 8.10): starr im
  kennzeichnenden Punkt K (0.13 L, 0.13 B, Bild 8.15), schlaff unter der
  Mitte. «Die maximale Setzung» des Wunsches ist damit beides: beim starren
  Fundament setzt sich alles gleich, beim schlaffen ist die Mitte am tiefsten.
- **J nach Boussinesq, die Eckformel und vier Rechtecke.** Die Formel steht
  nicht im gelieferten Kapitel (es verweist auf Kapitel 3). Sie trifft die
  Werte J_K der Tabelle 8.4 auf die gedruckte Stelle (428, 378, 336, 302,
  272 ‰) und die Grenztiefen der Tabelle 8.5, und das Beispiel der Tabelle
  ergibt 20.5 mm aus dem Ton -- das Kapitel nennt 2.1 cm. Steht im
  [[TODO]].
- **Wie der Grundbruch gebaut:** `geotechnik/setzung.py` (Fundament als
  Vorgaben, Nachweis, Befund), `projekt/setzung.py` (Eintrag, Schichten),
  `projekt/aufbau/setzung.py`, eine neue Bauteilart `SETZUNG` mit Vorsilbe
  `w` -- `s` tragen die Betonstähle. Die Oberfläche: `setzung.js` und
  `sz_zeichnung.js`. Die Bausteine des Bildes (Pfeile, Masse, Text,
  Schraffur) standen in `gb_zeichnung.js`; sie stehen jetzt in
  `gb_skizze.js` und gelten für beide. Das Bild des Grundbruchs ist dabei
  Zeichen für Zeichen gleich geblieben, an allen sechs Fundamenten der
  beiden Prüfprojekte verglichen. Die Zahlzeile der Maske
  (`bausteine.zahlzeile`) teilen sich Grundbruch und Setzung ebenso.
- **Das Bild:** ein Schnitt quer durch das Fundament durch den Punkt, die
  Schichten als Bänder mit Namen, Dicke, M_E-Werten und ihrem Beitrag zur
  Setzung, darin J über die Tiefe wie die Kurve E in Bild 8.1, oben rechts
  der Grundriss mit dem Punkt. Im selben Massstab, ausser der Baugrund wäre
  flacher als 200 px -- dann überhöht, und die Legende sagt, wie stark.
- **Eine Schicht hat keinen Schalter.** Ausgeschaltet hätten die Schichten
  darunter nach oben rücken müssen; die Zeile trägt statt des Schalters ihre
  Nummer (`fallzeile({vorn})`). Die Namen müssen nicht verschieden sein --
  zwei Tonschichten heissen beide «Ton»; die Werte tragen die Nummer.
- **Gesetzt, nicht vom Benutzer** (im [[TODO]] zum Bestätigen): s_zul = 20
  mm, Δz_max = 0.5 m, die Startschicht 2 m mit M_E = 20 und M'_E = 60
  MN/m², «starr», und die M_E-Werte in MN/m² statt kN/m² wie im Kapitel.
  Keine Pressung in einer neuen Berechnung, wie bei neuen Lastfällen
  (2026-10-19).
- **Im Beispiel** hat das Fundament der Stütze nun auch seine Setzung, 9.9
  mm gegen 25 mm; im Prüfprojekt das Beispiel der Tabelle 8.4 (geht mit 20
  mm nicht auf), ein schlaffer Damm mit Wiederbelastung und eine Setzung
  ohne Schicht.

---

## 2026-10-19 · Leere Vorlagen, Lastfälle ohne Einwirkung, Kopieren

Drei Wünsche des Benutzers:

- **Neue Lastfälle bringen keine Einwirkung mit.** In jeder Liste der Platte
  und des gezeichneten Querschnitts -- Tragsicherheit, Rissnachweise,
  Knicken, dazu Verformung und Analysen -- sind Kräfte, Momente und die
  Durchbiegung einer neuen Zeile null. Die Einträge gaben das schon vor; die
  Startwerte im Katalog setzten 30 kNm, 100 kNm, −500 kN, w = 2 mm darüber.
- **Neue Querschnittsanalysen und Balkensysteme sind leer.** `neu()` gibt
  beide leer zurück; das Rechteck bleibt Vorlage im Zeichenfenster, und die
  Python-Schnittstelle setzt es für ihre Analyse ausdrücklich ein. Eine
  Analyse ohne tragendes Element (`leer`) wird kein Bauteil: bis dahin hielt
  sie die ganze Rechnung an («Es gibt kein Polygon mit Material»). Jetzt
  steht eine Warnung da; ein Balkensystem, das sie als Querschnitt nimmt,
  meldet es weich und rechnet nicht (`Aufbau.leere_analysen`).
- **Kopieren.** Jeder Eintrag links hat neben «×» ein «⧉»: die Kopie steht
  gleich hinter dem Original, heisst «… (Kopie)» und ist gewählt. Die Kopie
  eines Materials ist immer ein eigenes -- BE2, S3 … nach der Sorte des
  Originals und mit seinen Abweichungen --, denn eine Normsorte gibt es im
  Projekt nur einmal.

---

## 2026-10-19 · Eine Lage ohne Stahl wird nicht nachgewiesen

Wunsch des Benutzers: Sind bei einer Platte etwa die oberen Lagen leer,
sollen sprödes Versagen (der Schalter «Rissmoment»), Duktilität und Zwängung
auf Biegung die leere Lage einfach weglassen.

Vorher bekam jede leere x-Lage in diesen drei Nachweisen ein Urteil «ohne
Bewehrung → kein Nachweis» mit Erfüllungsgrad 0, das als nicht erfüllt
zählte: eine Platte nur mit unterer Bewehrung galt als nicht erfüllt, und in
der Tabelle stand die leere Lage statt der bewehrten. Jetzt gibt die Platte
diesen Nachweisen nur die Lagen mit Stahl (`_lagennachweise` in
`projekt/aufbau/platte.py`, eine Stelle für alle drei). Der gezeichnete
Querschnitt machte es schon so: eine Seite ohne Stahl kommt dort nicht vor.

Die Zwängung auf Normalkraft wählt ihre Lagen selbst und meldet eine leere
weiter -- der Benutzer hat sie nicht genannt; offen, ob sie folgen soll.

---

## 2026-10-18 · Analysen aus dem Speicher; das Suchfenster steht einmal

Zwei Punkte aus der Durchsicht, auf Wunsch des Benutzers.

**Analysen aus dem Speicher.** Jede Rechnung rechnete alle
Spannung-Dehnung-Analysen neu, auch die unveränderter Bauteile; die
Nachweise kamen schon aus dem Zwischenspeicher. Jetzt liegen auch die
Zeichendaten der Analysen dort, in einem zweiten Speicher derselben Art
(`dienst.ANALYSEN`), je Bauteil unter demselben Abdruck wie seine Lösung.
Am Prüfprojekt «jeder Nachweis» (Server): dieselbe Rechnung nochmals 3,17 s
→ 0,04 s, nach einer Änderung an einer Platte ohne Analyse 3,20 s → 0,10 s.
In Pyodide eine neue Analyse 167 ms, danach 54 ms.

**Das Suchfenster steht einmal.** Ein Bild aus Randdehnungen mit −1 ‰ oben
und 48 ‰ unten meldete «ausserhalb dessen, wofür die Werkstoffgesetze
gelten», obwohl die unterste Lage bei 39.7 ‰ lag: Die Meldung mass beide
Ränder an `eps_druck`/`eps_zug`, einem zweiten, groberen Fenster neben den
Grenzen, in denen der Löser sucht.

- Jede `Dehnungsgrenze` trägt ihren Namen; die parallelen `grenznamen`
  fallen weg.
- `Dehnungsgrenzen.verletzt` sagt, welche Grenze eine Ebene verlässt, und
  der Hinweis nennt sie: «Stahl der 2. Lage bei 49.6 ‰, gilt bis 45.0 ‰».
- `eps_druck`/`eps_zug` fallen am Löser weg, dazu das Ersatzfenster, das nur
  noch Tests nutzten. Die Herleitung nennt ε_c2d aus den Kennwerten des
  Betons; ihr Text bleibt gleich.

Alle Zahlen beider Prüfprojekte bis aufs letzte Bit gleich.

---

## 2026-10-18 · Durchsicht der Phasen 4 und 5: Regeln, die zweimal standen

Vier Durchsichten über die Arbeit seit 300d19a (Wiederverwendung,
Vereinfachung, Effizienz, Wurzel). Behoben, je ein Commit, alle Zahlen beider
Prüfprojekte bis aufs letzte Bit gleich:

- Die Analyse rechnete N_Ed, M_Ed und die Randdehnungen mit eigenen Faktoren
  um, obwohl die Felder ihre Einheit tragen; jetzt `fall.si(feld)`.
- A_s, Schwerpunkt und d einer Lage rechneten drei Nachweise je für sich;
  jetzt `lage_aus_posten` und `statische_hoehe` neben `protokoll_lage`.
- Die Gebrauchsebene nannte ihre Suche für die Mitschrift ein zweites Mal;
  jetzt liest die Mitschrift sie vom Löser.
- Kleine Doppel: Erfüllungsgrade je Seite, τ_cd und die Lagen der Querkraft,
  die Einheit der Kennzahlentabelle, ungelesene Wahllisten im Katalog.
- Die Fallzeile nimmt den Fall statt vier Angaben aus ihm.

Dabei gefunden, ein Fehler aus 2b56a9c: Kam anderswo ein Material dazu,
wartete die Werkstoffwahl der Zeichnung auf eine Antwort, die nie kam. Jetzt
fragt `passendeGeometrie` selbst, wenn die Antwort nicht mehr passt.

Was liegen blieb, steht im [[TODO]].

---

## 2026-10-18 · Ein Klick in ein Feld markiert seinen Inhalt

Wunsch des Benutzers: wer in ein Text- oder Zahlenfeld klickt, soll gleich
tippen können. Vorher setzte der Klick nur den Cursor: wer hinter die 300
klickte und 250 tippte, bekam 300250. Jetzt ist 300 markiert und wird
ersetzt. Ein zweiter Klick setzt den Cursor wie gewohnt.

- Eine Stelle für die ganze Seite: `inhaltMarkieren` in `dom.js`, beim Start
  einmal eingerichtet. Markiert wird beim Fokus, also auch, wenn das
  CAD-Fenster eine Ziffer ins erste Feld schickt -- sie ersetzt dann, was
  dort stand -- und wenn die Seite nach dem Neuzeichnen den Fokus zurückgibt.
  Ein Textfeld bekommt dort gleich danach seinen Cursor zurück; ein
  Zahlenfeld hat keinen und bleibt markiert, etwa nach Enter.
- Der Browser hebt die Markierung beim Loslassen der Maus wieder auf; dieses
  eine Loslassen wird abgefangen.
- Mehrzeilige Felder (Beschreibung, Python-Skript) bleiben aussen vor: dort
  ersetzte ein Tastendruck den ganzen Text.

---

## 2026-10-18 · Die Oberfläche fragt den Kern

Phase 5 des Umbaus aus der Durchsicht vom 2026-10-16, in neun Commits.
Keine Zahl ändert sich; geändert hat sich die Datei (Teilung und Stabzahl)
und, wo Kern-Wissen im JS stand, wer es weiss.

- **Eine Zugseite** (`querschnitt/zugseite.py`). Dieselbe Seite stand in
  sechs Formen da: Enum, Tupel der Richtungen, Text der Verformung,
  `pos`/`neg`, `+`/`-` und drei Winkelausdrücke. Jetzt sagt die
  `Zugseite` selbst, was die anderen ausrechneten: Gegenseite, Vorzeichen,
  Zeichen, Marke in Kennungen; die Seiten der Platte sind `UM_Y`, und jede
  Lage kennt ihre (`Bewehrungslage.seite`).
- **«einachsig» gehört der Analyse.** Die fünf Nachweise des gezeichneten
  Querschnitts lesen `analyse.einachsig`, ihre Seiten sind
  `analyse.zugseiten`, und der Bruttoquerschnitt trägt den Schalter weiter
  -- vorher lief er durch elf Signaturen.
- **Eine Zeile je App** (`apps.js`). Material und Python liefen als
  Sonderwege durch Baum, Editor, Zustand und rechte Tafel; je Bauteilart
  standen ihre Teile in sieben Tabellen. Die fünf Anleger nach der Vorlage
  des Kerns sind einer (`nachVorlage`); der Editor des Materials und der
  der Platte haben eigene Module (`material.js`, `platte.js`).
- **Der Katalog nennt je Feld Einheit, Grenzen, «ganz» und Wahl**
  (`lesen.feldangaben`, `katalog.felder`). Die Einheiten des Grundbruchs
  standen dreimal; jetzt am Feld, das Bauen nimmt sie dort
  (`lesen.als_groesse`). Das Zahlenfeld nimmt die Angabe des Kerns
  (`zahlfeld({angabe})`): Grenzen für die Pfeile, und ein ganzzahliges
  Feld lehnt eine Kommazahl sichtbar ab -- vorher rundete die Oberfläche
  37.5° still auf 38°.
- **Teilung und Stabzahl bleiben beide stehen**, `art` sagt, welche gilt --
  wie bei der Stablinie. Umschalten setzt nur noch die Art; die Vorgaben
  (5 Stäbe, 150 und 200 mm) stehen im Kern statt im JS. Ein Stand von
  vorher öffnet sich nicht mehr (null gibt es dort nicht mehr); die Seite
  bewahrt ihn auf, wie für alte Stände entschieden.
- **Analysearten, Einheiten und E_eq/E_cm aus dem Kern.** Die Daten einer
  Linie bringen Zeichen und Einheiten mit, aus der Tabelle, die auch
  skaliert (`diagrammdaten._LINIENGROESSEN`); der Modul sein Vielfaches
  von E_cm. Welche Felder eine Frage braucht, sagt `Analyseart.eingaben`.
- **Eine Fallzeile** (`faelle.js`): sieben Zeilenbauer und sechzehn Regeln
  mit `:nth-child` werden eine Zeile, deren Zellen ihre Klasse tragen; die
  Zahlen übernehmen die Spalten der Zeile (`subgrid`). Unterwegs: `el()`
  setzte `--felder` nie, die Gebrauchsfälle der Platte standen still in
  drei statt zwei Spalten.
- **Die Werkstoffwahl** der Analyse nimmt die Materialien aus der Antwort
  des Kerns zur Zeichnung -- die letzte JS-Kopie von «wer braucht welches
  Material».

## 2026-10-18 · Löser und Kennzahlen

Phase 4 des Umbaus aus der Durchsicht vom 2026-10-16, in zehn Commits.
Zahlen bewegen sich nur, wo der Benutzer es entschieden hat -- beim
Suchfenster und bei der Suche der Analysen, beide erst ab der siebten
Stelle; jeder andere Schritt ist mit dem Werteabdruck belegt.

- **Die Suche ist ein Gegenstand** (`core/suche.py`). Halbieren und
  Illinois waren Unterklassen des Lösers (`FaserloeserIllinois`,
  `QuerschnittsloeserIllinois`, `klasse=`), die sich an vier Stellen mit
  `if self.halbiert` wieder abschalteten; Illinois stand zweimal, das
  Eingrenzen fünfmal. Jetzt bekommt der Löser seine Suche
  (`Faserloeser(…, suche=ILLINOIS)`), und sie sagt zweierlei von sich: ob
  sie bei der zuletzt gefundenen Stelle anfängt (`vom_letzten`) und ob sie
  taugt, wo ein Gesetz springt (`auch_bei_sprung`). Springt eines, halbiert
  der Löser trotzdem (`wirksame_suche`). Die Herleitung nennt die Suche mit
  deren eigenem Text; der falsche Satz «zwei geschachtelte Halbierungen»
  ist weg.
- **Ein Suchfenster aus den Gesetzen** (`Gesetze.grenzen`, Benutzer
  2026-10-18). Jeder Löser der Platte sucht in den Grenzen des
  Dehnungsfächers: der Beton an den Rändern bis −ε_c2d, im Punkt C bis
  −ε_c1d, jeder Stahl an seiner Lage bis ±ε_ud. Vorher suchte die
  Stahlspannung den Beton fest bis 3 ‰ -- bei einem Beton mit ε_c2d unter
  3 ‰ jenseits seines Gesetzes. 111 Werte bewegen sich, höchstens um
  7·10⁻⁷ relativ.
- **Die Analysen schneller** (`SUCHE_DER_ANALYSEN`, Benutzer 2026-10-18).
  Ihre Löser suchen mit Illinois, jede Frage im ganzen Fenster; wo der
  Spannungsblock springt, wird weiter halbiert. Alle Analysen des
  Prüfprojekts rechnen in 4.0 statt 5.2 s, die der Platte etwa fünfmal
  schneller; 674 Werte bewegen sich, höchstens um 2·10⁻⁶ relativ. Nicht
  geholfen hat, die Löser je Neigung mit der zuletzt gefundenen Ebene
  vorzubelegen: es machte sie langsamer.
- **Die Querkraft schreibt ihre Herleitung selbst** (`protokoll_hoehen`,
  `protokoll_ohne_buegel`, `protokoll_mit_buegeln`). Die Kennzahlen
  schrieben V_Rd,c, V_Rd,s und d_v ein zweites Mal, samt einem erzwungenen
  «d_v = d (Einlage nicht massgebend)» im Bügelteil.
- **Kennzahlen: jeder Erzeuger nennt seine** (`core.wert.Kennzahl`,
  `Bauteil.kennzahlen`). Die Handliste der Beschriftungen in der
  Zusammenfassung fällt weg. Was fehlt, fehlt: ein x/d gibt es nur für
  eine Seite mit Zugbewehrung, statt «(x/d)⁻ = 0».
- **Ein Fehler unterwegs** (`linie._schnittpunkte`). Eine Platte nur mit
  oberer x-Bewehrung zeigte als Druckwiderstand 0 statt −5000 kN: ihre
  Linie berührt M = 0 nur, entlang einer Kante, und die Schnittsuche
  zählte nur Kreuzungen. Jetzt zählt jeder Eckpunkt auf der Geraden.
- **Dieselbe Höhe, ein Name.** Der Vergrösserungsfaktor schreibt seine
  Lagen mit `protokoll_lage`: 248.1 mm heissen d_{2,x} wie in der Zwängung,
  nicht mehr d_u.

## 2026-10-17 · Platte und gezeichneter Querschnitt: ein Nachweis, zwei Geometrien

Phase 3 des Umbaus aus der Durchsicht vom 2026-10-16, in fünfzehn Commits.
Zahlen ändern sich nur, wo der Benutzer es entschieden hat -- bei den
Rissgrössen und der kippenden Nulllinie; jeder andere Schritt ist mit dem
Werteabdruck bis auf die letzte Stelle belegt.

- **Ein Gesetz schreibt sich selbst** (`Gesetz.protokoll`). Fünf Stellen
  schrieben die Werkstoffgesetze in die Herleitung, jede mit eigener Weiche
  (`isinstance`, `art is ELASTISCH`, `mit_block`); jetzt schreibt jedes
  Gesetz seine Formel und seine Werte. Der Schalter `gemittelt` fällt weg:
  ob ein Gesetz springt, sagt es selbst (`mittel`).
- **Schichten.** Rechenwahl, Rechenart, Wertesatz und Betongesetz gehören
  dem Querschnitt (`querschnitt/gesetzwahl.py`), die Zugseite hat ein
  eigenes Modul, das Fachwerk zieht nach `querschnitt/fachwerk.py`;
  `tests/test_schichten.py` hält fest, dass der Querschnitt nichts von oben
  importiert. Die Spannung-Dehnung-Analyse ist ein Paket
  (`spannungsanalyse/`), mit einem Protokoll `Paar` statt `Any`.
  «Ungerissen» gibt es nur noch auf einem Weg (`betongesetz(…,
  ungerissen=True)`).
- **Die Rissgrössen an einer Stelle** (`nachweis/rissgroessen.py`). Sie
  standen viermal da und sagten schon Verschiedenes: das Rissmoment der
  Analyse ohne I_yz, das des Nachweises mit, und für die rissaktive Dicke
  unter Zug vier Regeln. Jetzt, wie der Benutzer am 2026-10-17 entschieden
  hat: das Rissmoment unter reiner Biegung, wo f_ct,eff zuerst erreicht
  wird, «einachsig» mit W = I/v; k_t unter Biegung mit h/3, unter Zug mit
  min(h; b), wahlweise höchstens 500 mm.
- **Die Nulllinie der Analyse kippt** (`spannungsanalyse/schnitt.py`,
  `KippendeNulllinie`). Jede Ebene sucht die Neigung, bei der kein Moment
  um die andere Achse bleibt, mit der Suche der Gebrauchsnachweise
  (`gebrauchsebene.neigung_suchen`); «einachsig» bleibt sie waagrecht. Der
  äquivalente Modul vergleicht dann mit I_y − I_yz²/I_z. An einem L (Steg
  200 × 800, Flansch 600 × 200) sinkt das Rissmoment von 116.0 auf
  56.9 kNm, und die Linie endet genau beim Widerstand der Tragsicherheit.
  Der Preis: eine gekippte Linie dauert etwa dreimal so lang -- angenommen,
  schneller in Phase 4. Unterwegs behoben: Stäbe gleicher Tiefe verloren
  als Lage ihren Arm entlang der Nulllinie, und `illinois` rechnete mit
  `nan` weiter.
- **Ein Nachweis, zwei Anschlüsse.** Die Stahlspannung misst an Stellen --
  Lagen oder Stäbe --, was die Geometrie beiträgt, sagt ein schmaler
  Anschluss (`Stahlspannungsort`: `PlattenStellen`, `AnalyseStellen`);
  `SpannungsbegrenzungQA` mit seinem kopierten Urteil fällt weg. Bei der
  Zwängung auf Biegung teilen beide nur Name, Thema und Einleitung
  (`Biegezwang`): die Platte rechnet von Hand mit d − x/3, der gezeichnete
  Querschnitt sucht -- ein gemeinsamer Nachweis hätte fast nur
  weitergereicht (Benutzer, 2026-10-17).
- **Die Beschreibung und die Maske einmal.** Zwölf Felder, die beide gleich
  angeben, stehen in `Querschnittsangaben`. Die Oberfläche baut die sechs
  gemeinsamen Kapitel mit `nachweisKapitel(ort)`: eine Schalterzeile, die
  Fragezeichen am Kapitel, das Gemeinsame der Hilfe einmal. Was das
  Bauteil anders zeigt, sagt sein Ort (`PLATTE`, `ORT`).
- **Dateien.** `projekt/aufbau.py` wird ein Paket -- ein Kern und je
  Bauteilart ein Modul --, `nachweise.js` teilt sich nach Abnehmern
  (`nachweise.js` für beide, `plattenkapitel.js`, `bewehrungssuche.js`),
  und `TestVorgabenAnEinerStelle` fällt weg: seit dem neuen Leser prüfte er
  nur noch, was die Bauart garantiert.

## 2026-10-17 · Prüfen nach Regel, Wahlfelder als Wahl

Phase 2 des Umbaus aus der Durchsicht vom 2026-10-16, in elf Commits. Keine
Zahl ändert sich (Werteabdruck nach jedem Schritt), und die Dateien bleiben
Zeichen für Zeichen gleich.

- **Ein Wahlfeld hält sein Mitglied** (`core/wahl.py`,
  `lesen.wahl_aus_text`). Zwölf Wahlen erben von `Wahl`, einem `StrEnum`,
  das sich als sein Text ausgibt und einen unbekannten Text mit den
  möglichen nennt. Text in einem Wahlfeld wird beim Lesen, im Konstruktor
  und bei jeder Zuweisung zum Mitglied (`Beschreibung.__setattr__`);
  `json.dumps` schreibt den Wert. Warum: rund dreissig Stellen verwandelten
  den Text zurück (`Rissanforderung(…)` elfmal, `Rechenwahl.aus` viermal),
  und neun Tupel hielten die Werte ein zweites Mal. Welche Rechenarten ein
  Kapitel anbietet, steht am Feld seiner Unterklasse (`Gebrauchswahl`,
  `KnickVerformungswahl` …) statt in fünf Aufrufen von `pruefen(wo, arten)`.
- **Die Fassade liest wie eine Datei.** Was als Stichwort an
  `Projekt.platte`, `analyse`, `balkensystem` und `grundbruch` geht, liest
  `lesen` mit dem frischen Eintrag als Grundlage; ein Teil darf als Eintrag
  oder als seine Felder kommen. Die zweite Fassung von «Gemeint ist
  vielleicht …» fällt weg.
- **Form beim Lesen, Inhalt vor dem Rechnen** (`lesen.bereich`,
  `lesen.inhalt_pruefen`). Beim Öffnen zählt die Form: Typ, Wahl, Pflicht,
  eine Kennung je Eintrag, die Sorte eines Materials. Wo eine Zahl liegen
  muss, steht an ihrem Feld -- `bereich(300.0, heisst="Dicke h",
  einheit=MM, ueber=0.0)`; was mehrere Felder betrifft, in `regeln(wo)` des
  Eintrags. Beides prüft `inhalt_pruefen` vor jedem Rechnen über das ganze
  Projekt, mit dem Ort am Feld. Warum: geprüft wurde zu drei Zeitpunkten
  ohne Regel -- ein Anteil null hielt das Öffnen auf, eine Dicke null erst
  das Rechnen, eine negative Kriechzahl das Lesen, eine negative Überdeckung
  das Bauen --, dazu in fünf Formen von `pruefen`. Ein abgelegter Stand mit
  einem Fehler im Inhalt soll sich öffnen und korrigieren lassen; seit 1d
  galt das schon für gleiche Namen.
- **Dabei neu gemeldet:** k_c und α der Platte gelten auch ohne Bügel; ein
  negativer Bügeldurchmesser hiess still «keine Bügel»; die Posten der
  Obergrenze der Suche werden vor jedem Rechnen geprüft. Die Felder, die
  Platte und gezeichneter Querschnitt teilen, stehen einmal (`neigung`,
  `druckfeld`, `x_d_grenze`).
- **Die Suche prüft vorab** (`bewehrungssuche.vorab_pruefen`). Eine
  unmögliche Platte endete in der Bewertung als «nicht gefunden», weil dort
  jede Ausnahme ein Nein wird. Gebaut wird vorab nicht: eine Platte ohne
  Bewehrung darf gesucht werden.

## 2026-10-17 · Vier Fehler aus der Durchsicht behoben

Die Durchsicht vom 2026-10-16 fand vier Fehler mit sichtbarer Folge. Jeder
steckte in einer Doppelung, und behoben ist er dort, wo die Doppelung
wegfällt.

- **Ein unlesbarer Stand im Browser bleibt erhalten** (`web/js/ablage.js`).
  Liess sich der abgelegte Stand nicht öffnen, startete die Seite mit dem
  Beispiel und meldete «Nicht gelöscht» -- die erste Änderung überschrieb
  ihn doch. Jetzt wird der Rohtext vorher unter `opencivil.projekt.unlesbar`
  aufbewahrt; ein bleibender Hinweis oben rechts bietet ihn zum
  Herunterladen an, bis er verworfen ist.
- **Ein Umschlag für alle Antworten** (`opencivil/web/umschlag.py`). Die
  Konsole baute ihre JSON-Antwort selbst, ohne den Riegel gegen NaN, und
  hing bei `plt.plot(…, lw=float("nan"))`. Dazu weist `kern.js` eine
  unlesbare Antwort zurück, statt die Anfrage offen zu lassen, und
  `zeichnen.py` prüft Breite, Grösse und Deckung.
- **Wer worauf zeigt, sagt der Kern** (`Projekt.verweise`, Dienst
  `verweise`). Der Löschschutz im Baum hielt eine eigene Liste, die den
  Bügelstahl nicht kannte.
- **Gleiche Namen erst beim Rechnen, in allen Listen** (`eindeutig`). Die
  Prüfung «Wand A»/«Wand-A» stand nur bei drei von neun Listen; und weil
  gleiche Namen schon das Öffnen aufhielten, waren sie ein Auslöser des
  ersten Fehlers.

Dazu ein Werkzeug für die Umbauten der nächsten Phasen:
`werkzeug/werteabdruck.py` legt jede Zahl der Prüfprojekte ab und
vergleicht genau. Nach Phase 1: alle gleich.

## 2026-10-16 · Ein Modell der Werkstoffgesetze

C2 der Durchsicht vom 2026-10-12, in drei Commits. Keine Zahl im Bericht
ändert sich; die Schnappschüsse bewegen sich nur in Formelzeilen.

- **Ein Gesetz rechnet und schreibt sich selbst**
  (`querschnitt/werkstoffgesetz.py`). Vorher rechnete der Löser mit
  Funktionen (`beton_nichtlinear`, `stahl_bilinear`, `stahl_nur_zug`), und
  gedruckt wurden Klassen, eine davon als Platzhalter nur fürs LaTeX.
  Jenseits von ε_c2d und beim gedrückten Stahl stand in der Herleitung
  etwas anderes, als gerechnet wurde. Jetzt baut jedes Gesetz einmal seine
  Funktion (gemessen gleich schnell, rund 14 µs je Kräfteintegral) und
  schreibt seine Formel aus denselben Ästen -- samt «0 jenseits der
  Bruchstauchung». Neu die Formelseite «Beton linear, ohne Zug».
- **Jenseits der Grenze null, auf ihr um eine Rundung** (`RUNDUNG`,
  1e-12). Der Löser hielt die Grenze hart, die genaue Resistenzlinie gar
  nicht (Schalter `bricht`): eine Lage genau auf ε_ud kippte an der letzten
  Stelle auf null. Jetzt eine Formel je Gesetz.
- **Die Querschnittsanalyse baut ihren Beton wie die Platte**
  (`rechenwahl.betongesetz`). Der Beiwert der Parabel kommt aus E_cm statt
  aus dem E_cd des Materials -- bei γ_cE = 1 dieselbe Zahl -- und steht
  jetzt auch mit Bemessungswerten in ihrer Herleitung. Weil keine Rechnung
  mehr γ_cE, E_cd und das k_σ des Materials liest, fallen die drei aus dem
  Bericht; in der Materialtabelle stehen sie weiter (siehe [[TODO]]). Die
  Wahl je Material ist eine `Rechenwahl` statt zweier Texte («bemessung»,
  «block»), und Bruchzustand wie Spannungen und Knicken bauen ihre
  Werkstoffe an einer Stelle (`Querschnittsanalyse.werkstoffe`) statt an
  zweien. Das Materialbild zeigt dieselbe Parabel.
- **Punkt C an einer Stelle** (`anteil_punkt_c`), vorher dreimal: im Fächer
  der Platte, in ihren Grenzen und in der Interaktion.
- **Der Hinweis zu Randdehnungen** misst Druck und Zug je an ihrer Grenze.
  Vorher galt das Grössere der beiden: −5 ‰ blieb ohne Hinweis, weil der
  Stahl bis 45 ‰ reicht, obwohl der Beton dort nichts mehr trägt.

Offen bleibt der eigene Dehnungsfächer der Platte neben dem allgemeinen
(siehe [[TODO]]).

## 2026-10-16 · Was still einen Ersatz nahm, meldet sich

Zweiter Teil von C1. Mit dem strengen Leser kommt nichts Unbekanntes mehr ins
Projekt; was danach beim Rechnen still einen Ersatz nahm, ist jetzt ein
Fehler mit Ort.

- **Die Rissanforderung an einer Stelle** (`nachweis/rissanforderung.py`):
  Stufe, Beschriftung, Rissbreite und ob gegen Fliessen nachgewiesen wird.
  Vorher vier Tabellen und zwei `.get`, die eine unbekannte Stufe zur
  mildesten machten; jetzt ist sie überall ein Fehler.
- **Kein «erstes im Projekt» mehr** (`aufbau._stoff`): Stäbe, Linien und
  Wände einer Analyse und Bügel ohne Stahl bekamen still den ersten. Ein
  Material muss es geben, und es muss von seiner Art sein -- ein Stahl ist
  kein Beton. Nur eine leere Lage behält den Ersatz: sie trägt nichts.
- **Zahlen, die erst das Rechnen braucht** (`zahlen_pruefen`, vorher
  `masse_pruefen`): ein Posten mit Durchmesser braucht eine Teilung oder
  Stabzahl grösser null, eine Knicklänge grösser null; die Analyse prüft
  α, k_c und x/d wie die Platte, über dieselben Funktionen
  (`neigungen_pruefen`, `druckfeld_pruefen`, `x_d_max_pruefen`).
- **Kennungen eindeutig** -- im Projekt über alle Arten (ein zweites `b1`
  ersetzte still das erste), im Balkensystem je Teil als Meldung (eine Last
  fiel in zwei Lastfälle), je Analyse eine Werkstoffwahl.
- **Was es nicht gibt:** ein Kennwert `fck` (fiel weg), ein Mass `B` am
  Stabquerschnitt (gerechnet wurde mit b = 300), eine leere Teilungsliste
  der Suche (wurde 150 mm).
- **Die Fassade meldet an der Zeile:** Stichworte gehen über den Leser, ein
  vertipptes heisst «Gemeint ist vielleicht 'richtung'?» statt Pythons
  englischer Meldung, ein falscher Wert fällt beim Anlegen auf.

---

## 2026-10-16 · Ein Leser und eine Prüfung für jedes Feld

Wunsch des Benutzers (TODO C1): Eingaben an einer Stelle prüfen. Vorher las
jede Klasse ihre Datei von Hand -- 39 Leser, jeder mit eigenen Vorgaben,
Prüfungen und alten Formaten --, und die Fassade ging an ihnen vorbei. Ein
`quer="festt"` aus Python wurde still zur Bettung; eine Rissanforderung mit
Tippfehler zur mildesten Stufe, ohne x-Bewehrung ganz ohne Meldung.

- **Ein Leser** (`lesen.lesen`) für alle Einträge, aus den Feldern der
  Datenklassen. Streng: ein Feld, das es nicht gibt, meldet sich mit dem
  ähnlichsten («Gemeint ist vielleicht 'rissanforderung'?»), ein Text ist
  keine Zahl, `"false"` kein Schalter, 35.7 keine ganze Zahl -- abgeschnitten
  wird nichts. Was fehlt, bekommt die Vorgabe: bei einem Eintrag in einem
  Eintrag die eines frischen an dieser Stelle, so rechnet eine teilweise
  angegebene Rechenwahl des Knickens wie ihr Kapitel.
- **Eine Prüfung** (`lesen.felder_pruefen`) für jedes Feld, aus dem, was an
  ihm steht: Typ, Wahl (`einer_von`), Untergrenze (`nicht_negativ`), Pflicht
  -- ein Text ohne Vorgabe darf nicht leer sein. Sie läuft beim Lesen und
  vor jedem Rechnen über das ganze Projekt (`Projekt.pruefen`): was in
  Python gebaut wurde, geht durch dieselbe Tür wie eine Datei.
- **Der Ort steht in jeder Meldung** so, wie die Oberfläche ihn nennt:
  «Platte 'Decke', lagen 2, grund: 'abstand' muss eine Zahl sein». Bauteile
  und Materialien tragen dafür eine `BEZEICHNUNG`.
- **Alte Formate weg** -- seit 2026-10-11 erlaubt: vier Lagen aus
  `lagen_unten`, flache Gebrauchslisten, Schalterlisten je Lage, `richtung`
  an Lastfällen, `betongesetz`, die Kriechzahl der Platte für jedes Kapitel,
  Analysen mit eigenen Koordinaten, die Kette `ERSATZ_ALTER_WAHL`. Mit der
  Kriechzahl der Platte ging ein stiller Fehler: fehlte in einer Platte ein
  φ, galt 2.0 statt 0. Der Schnappschuss «altformat» ist weg, seine drei
  Querschnitte stehen in den beiden anderen.
- Am 2026-09-26 blieben die Leser von Hand, weil Altformate und Prüfungen
  darin standen («ein Wächter statt eines generischen Lesers»). Die
  Altformate sind weg, die Prüfungen stehen an den Feldern -- der Grund ist
  entfallen. Der Wächter bleibt: ein Test prüft je Eintragsklasse, dass ein
  Wörterbuch mit nur den Pflichtfeldern die Vorgaben ergibt.
- Was erst das Rechnen braucht (h > 0, das Material einer Platte), prüft
  weiter der Aufbau: eine abgelegte Platte mit h = 0 soll sich öffnen und
  korrigieren lassen.

---

## 2026-10-16 · Eigener Betonstahl heisst S1

Der Benutzer hat die Festlegungen der Kennzahlen bestätigt und eine
geändert: eigener Betonstahl heisst S1, S2 … statt BS1 (`EIGENE_VORSILBE`).
Eigener Beton heisst weiter BE1, BE2 …. Bezüge laufen über die Kennung
(`s1`, `s2` …), angezeigt wird der Name; die beiden müssen nicht
übereinstimmen -- ein eigener Stahl neben B500B hat die Kennung `s2` und
heisst S1.

---

## 2026-10-16 · Bewehrung mit Höhe ab Unterkante

Wunsch des Benutzers: in der Tabelle «Bewehrung von oben nach unten» eine
Spalte mit der Höhe jeder Lage über der Unterkante, in mm.

- Die Zahl ist `h - z` der Stabachse, mit z aus dem Lagenaufbau. Sie wechselt
  nur den Bezug einer hergeleiteten Grösse und geht in keine Rechnung ein;
  darum steht sie nur in der Übersicht, nicht als eigene Formel.
- Liegen Grund und Zulage verschieden hoch, stehen beide, getrennt durch «/».
  Beispiel: unten ⌀18 + ⌀12 in der 2. Lage ergibt «51 / 54».
- `bewehrungsuebersicht` bekommt dafür die Werte der Lösung. Ihr Typ war
  falsch angeschrieben (`QuerschnittEintrag` statt `Plattenquerschnitt`).

---

## 2026-10-16 · Kennzahlen der Platte, immer gerechnet

Wunsch des Benutzers: unter der Zusammenfassung jeder Platte Kennzahlen,
gleich ob Nachweise gewählt sind -- ω_w und ω_w', M_Rd± bei N_Ed = 0, N_Rd±
bei M_Ed = 0, x/d aus der Handrechnung, V_Rd,max und V_Rd,min ohne Bügel
(je das Kleinere beider Seiten) und V_Rd(α_opt) mit Bügeln.

- **`Plattenkennzahlen`** (`nachweis/kennzahlen.py`), eine Prozedur je
  Platte mit x-Bewehrung, Rechenziel der Platte nach ihren Nachweisen.
  Rechnet die Tragsicherheit von Hand mit Bemessungswerten, liest sie deren
  Linie aus dem Befund -- dasselbe Muster wie das Knicken --, sonst eine
  eigene mit Herleitung. N_Rd bei M = 0 sucht `kante` auf der Linie;
  `protokoll_treffer` nimmt dafür jetzt den Wert mit, unter dem das Ergebnis
  weitergeht, statt eines allgemeinen N_Rd.
- **Querkraft:** k_g und die Teilung in y sind Funktionen
  (`beiwert_k_g`, `buegelteilung_y`), die Nachweis und Kennzahlen teilen;
  der Widerstand kommt aus `widerstand` und `neigungen`. Bei M_Ed = M_Rd ist
  ε_v = f_yd/E_s, gleich wie gross M_Rd ist -- die «Fliessdehnung».
- **Vergrösserungsfaktor:** ω_w war Teil des Verformungsnachweises und
  rechnete nur für Seiten, die ein Fall zog. Jetzt ist er eine eigene
  Prozedur der Platte (`Vergroesserungsfaktor`), immer und für beide Seiten;
  der Nachweis liest ihn. Die Zeichen heissen ω_w und ω_w' wie beim Benutzer.
- **Eine Liste, zwei Darstellungen:** `zusammenfassung.kennzahlen` baut die
  Zeilen; die Oberfläche zeigt sie (`loesung.kennzahlen`), der Bericht als
  Tabelle unter jeder Platte. Bewehrungsmass und Distanzhalter gehören dazu;
  der Lagenaufbau rechnet dafür auch bei einer Platte ohne Nachweis.
- **x/d:** die Handrechnung hält am Punkt N = 0 ihr x und d fest
  (`Eckpunkt.x`, `.d`).

---

## 2026-10-16 · Rechte Tafel weiss, Diagramme einzeln gross, Normsorten gesperrt

Wünsche des Benutzers, je ein Commit:

- **Rechte Tafel wie die mittlere:** weisser Grund, die Köpfe aller drei
  Tafeln gleich hoch (`--tafelkopf`) und ohne Umbruch. Ist die rechte
  Tafel schmal, fällt ihr Titel weg und die Reiter rücken zusammen; auf dem
  Telefon bricht der Kopf weiter um.
- **Diagramme:** statt «nebeneinander 1, 2, 3» eine Leiste mit einer
  Vorschau je Diagramm, darunter das gewählte gross. Die Vorschau ist eine
  verkleinerte Kopie des Bildes, kein eigenes Bild -- ein zweiter Weg, die
  Diagramme zu zeichnen, liefe auseinander. Ein Diagramm ist jede Karte mit
  einem Bild; die übrigen Karten eines Bauteils (Wahl des Falls, Hinweise)
  stehen über dem gewählten.
- **Materialien:** «+» öffnet ein Fenster: Normsorte nach SIA oder eigenes
  Material mit einer Sorte als Vorlage. Eine Normsorte bleibt, wie sie ist
  -- «Material modifizieren» und die Wahl der Sorte sind weg; links trägt
  sie ein rotes «SIA» statt des Schlosses. Ein eigenes Material heisst BE1,
  BE2 … bzw. BS1 … (`EIGENE_VORSILBE`) und darf nicht wie eine Normsorte
  heissen. In Python: `p.eigener_beton("C30/37")`, `p.eigener_stahl()`;
  `material_loesen` ist weg.

---

## 2026-10-16 · Neue App «Grundbruch»: Grundbruch und Gleiten eines Flachfundaments

Wunsch des Benutzers, mit dem Kapitel 9.2 «Tragfähigkeit» als Vorlage (Text,
Tabellen 9.2.8 bis 9.2.18, Bilder 9.2.10 und 9.2.15) und den Vorgaben der
Felder: φ_k = 30°, γ_φ = 1.2, c = 0, γ_c = 1.5, γ = 21 und γ_w = 10 kN/m³,
q_Ed = 0, b = L = 1 m, t = t_1 = 0, N_Ed = 1000 kN, T_Ed = 200 kN, α = β = 0.

- **Kern:** `opencivil/geotechnik/grundbruch.py`. Das `Fundament` legt die
  Eingaben als Vorgaben ins Rechenwerk und rechnet φ_eff = arctan(tan φ_k /
  γ_φ) (SIA 267:2013, 5.3.2.1), c_eff = c_k / γ_c und γ'. Zwei Nachweise je
  Kombination: `Grundbruch` nach der erweiterten Tragfähigkeitsformel, für
  φ = 0 nach der undrainierten (9.2.17), und `Gleiten`, T_Rd = N_Ed · tan δ*.
  Die Faktoren, die nicht an der Last hängen, rechnen einmal; i je
  Kombination. Der Befund trägt die Faktoren für die Tabelle der
  Zusammenfassung und L, H des Gleitkörpers für das Bild.
- **Steckbrief:** `GRUNDBRUCH` in `BAUTEILE`, Vorsilbe `g`. Lesen, Kennungen,
  Zwischenspeicher, Formelsammlung und Erkennen einer Datei kamen damit von
  selbst; dazu der Eintrag in `arten.js`.
- **Zusammenfassung:** über den Nachweisen die Angaben in zwei Zeilen und die
  Tabelle der Faktoren wie im Bild des Benutzers -- drei Spaltenpaare
  Kohäsion, seitliche Auflast, Gewicht Gleitkörper; Zeilen N, s, d, i (je
  Kombination), g, b'. `angaben()` braucht dafür die Lösung: die Faktoren
  stehen erst nach dem Rechnen fest.
- **Bild der Situation** (Reiter Diagramme): wie Bild 9.2.15, die Bruchseite
  links. Die Masse kommen aus dem Eintrag, der Umriss des Gleitkörpers aus dem
  Kern (`gleitkoerper()`, Prandtl: Keil, Spirale, Keil -- trifft L und H der
  Formeln). Er ist für waagrechtes Gelände gerechnet und endet im Bild, wo er
  aus einem geneigten Gelände tritt. Die Kräfte stehen im Verhältnis
  zueinander, die grösste immer gleich lang; gezeigt wird die massgebende
  Kombination oder die gewählte.
- **Formelsammlung:** eine Seite sammelt jetzt jede Normstelle, unter der
  ihre Formel vorkommt, nicht nur die der ersten Fassung -- σ_v0 = γ t + q
  steht beim Grundwasser (9.2.8) und in der undrainierten Formel (9.2.17).
- **Prüfprojekt:** Hang (Wasser im Gleitkörper, α, β, q, Kohäsion, eine
  Last so schräg, dass i null wird), Ufer (Lage 1), Kai (Lage 2), Seeton
  (undrainiert, einmal ohne Widerstand), Schacht (tief eingebunden). Das
  Beispiel hat ein grünes Einzelfundament.
- **Tests** gegen jede Tabelle des Kapitels und gegen die Tabelle des
  Benutzers. Das Buch rundet nicht einheitlich: d_c bei t/b = 4 ist 1.532,
  die Tabelle sagt 1.52; H/b bei 25° ist 1.35, sie sagt 1.4. Dort ist die
  Toleranz eine Stelle weiter, die Abweichung steht beim Test.

Entschieden, ohne Rückfrage, und so im [[TODO]]:

- b_γ rechnet mit tan φ wie Tabelle 9.2.18; im Text steht tan α.
- Liegt das Wasser unter der Sohle, aber höher als H, verlangt das Kapitel
  eine Stabilitätsberechnung -- gerechnet wird mit γ' wie in Lage 2.
- Eine Klammer eines Lastneigungsfaktors unter null gilt null; i_c bleibt,
  wie die Formel es ergibt (auch negativ, wie in der Tabelle des Benutzers).
- δ*/φ ist ein eigenes Feld, Vorgabe 1 -- das Kapitel nennt 2/3 φ bis φ.
- L ≥ b wird verlangt: b ist die kürzere Seite.
- Kein globaler Sicherheitsfaktor F wie im Kapitel: die Sicherheit steckt in
  γ_φ und γ_c.

---

## 2026-10-16 · Rechte Tafel wie die mittlere; Spannung-Dehnung als Diagramme

Die rechte Tafel sieht jetzt aus wie die mittlere (Benutzer): je Bauteil ein
graues Panel, darin weisse Karten mit blauer Kante -- dieselben `panel` und
`karte` aus `bausteine.js`, also auch derselbe Kopf zum Zuklappen.

- **Zusammenfassung:** je Bauteil ein Panel mit den Karten Angaben,
  Bewehrung, Nachweise, Kennzahlen. Die Tabelle der Nachweise ist immer
  660 px breit (`--tabellenbreite`), sie skaliert nicht mehr mit der Tafel;
  breiter wird sie nur, wo ihr Inhalt es verlangt. Das Panel ist so breit,
  dass sie hineinpasst (`--berichtbreite`, 704 px) -- in der Tafel von 750 px,
  die ein Bildschirm von 1536 px ergibt, ohne Rollen. Dafür wurde sie etwas
  kleiner gesetzt (12.5 statt 13 px, knappere Zellen).
- **Diagramme:** je Bauteil ein Panel, je Diagramm eine Karte; die Wahl
  «nebeneinander» stellt die Karten im Panel nebeneinander, statt ganzer
  Blätter. Die Werkstoffgesetze stehen zusammen in einem Panel.
- **Herleitung:** je Bestandteil ein Panel, je Kapitel -- Titel der Ebene 2
  -- eine Karte.
- **Spannung-Dehnung-Analysen** sind keine kleinen Bilder mehr, sondern
  Diagramme wie die M-N-Linie: 720 × 520, Gitter und Teilung an beiden
  Achsen, Legende darunter, Werte über den Punkten beim Darüberfahren. Die
  zwei Bilder «Dehnung» und «Spannung» über die Höhe sind ein Diagramm mit
  zwei Feldern an derselben Höhenachse (Benutzer); die Nulllinie läuft durch
  beide. Zwei Felder statt zweier Achsen in einem: die Einheiten sind
  verschieden, übereinander läse man die eine Kurve an der Achse der anderen.
- `min-width: max-content` an der Tabelle machte sie in Chrome fünfmal so
  breit; es braucht ihn nicht, weil die Zeilen ohnehin nicht umbrechen.

## 2026-10-16 · Verformungsnachweis der Platte

Die Kriechzahl φ steht nicht mehr bei der Platte. Dafür gibt es neben
«Fliessen häufig» den Nachweis «Verformung» (Benutzer): zuoberst φ, Vorgabe 2,
darunter Verformungsfälle wie Lastfälle, je Fall die Durchbiegung w in mm und
die Spannweite L in m. Gehalten wird w_eff = ω_w · w gegen w_max = L/350; der
Hinweis im Fenster sagt, dass w mit der Steifigkeit E_cm zu ermitteln ist.

- **ω_w ist die Formel, die schon da war** -- w/w_c nach SIA 262:2025,
  4.4.3.2.5, mit ρ der gezogenen und ρ′ der Gegenseite. Sie stand bei den
  Bewehrungslagen und rechnete mit dem φ der Platte; jetzt gehört sie dem
  Nachweis (`nachweis/verformung.py`), und die Zahlen sind dieselben (4.00
  unten, 7.52 oben im Beispiel).
- **Je Fall eine Zugseite**, Vorgabe unten. Der Faktor hängt an der Seite,
  die gezogen wird; ein Kragarm zieht oben. Gerechnet wird er je Seite, die
  ein Fall verlangt, einmal für die Platte -- nicht je Fall. Der Benutzer hat
  die Frage nach der Seite mit der Formel beantwortet; die Zugseite je Fall
  ist meine Folgerung daraus (ρ ist das der gezogenen Seite). Ohne x-Bewehrung
  auf der gezogenen Seite gibt es keinen Faktor: der Fall steht mit Grad null
  und dem Grund in der Tabelle.
- **Nach Vorgabe, nicht nachgeschlagen:** L/350 und «w mit E_cm» (siehe
  [[TODO]]). Die Herleitung sagt es als Annahme.
- **Eine alte Datei** bringt ihr φ der Platte als φ der Verformung mit. w und
  L prüft erst das Rechnen, wie die Masse der Platte: eine abgelegte Platte
  mit L = 0 lässt sich öffnen und korrigieren.
- Unter der Tabelle steht ω_w je gezogene Seite, wie vorher w/w_c -- jetzt
  nur, wo der Nachweis rechnet. Beispiel und Prüfprojekt haben Fälle: unten
  und oben, erfüllt und nicht, ein eigenes φ, eine Platte ohne x-Bewehrung.

## 2026-10-16 · Schalter, Fenster, Apps, Rissanforderung

Mehrere kleine Wünsche des Benutzers an die Oberfläche, je ein Commit:

- **Schalter mit zwei Stellungen** sind ein einziger Knopf (`zweiSchalter` in
  `bausteine.js`): ein Klick irgendwo schaltet um. So hoch wie die
  Eingabefelder daneben; die gewählte Stellung ist eine abgerundete farbige
  Fläche bis an den Rand, die andere bleibt blass auf grauem Grund. Gilt für
  Haken/Kreuz, x/y, «Aktuelle Seite/Gesamt»; «günstig/ungünstig» ist ein
  Knopf mit Text und bekam nur die Höhe.
- **Fenster** erscheinen senkrecht in der Mitte; ein langes beginnt oben und
  rollt wie bisher. Auf dem Telefon steht die Anzeige «Kern: …» über der
  Reiterleiste statt dahinter.
- **Apps merken sich ihre Auswahl** (`zuletzt` in `zustand.js`): beim Wechsel
  ist der zuletzt gewählte Eintrag der App wieder gewählt, sonst der erste.
  Ihr Zeichen ist blau, sobald sie einen Eintrag hat.
- **Die Rissanforderung** steht in den Fenstern «Riss bei Zwang»,
  «Stahlspannung quasi-ständig» und «Fliessen häufig» statt oben bei Platte
  und Querschnitt, mit einem «?»: sie gehört weiter dem Bauteil und gilt für
  alle drei.
- **Die Bezeichnung der Platte** beginnt bündig über der Beton-Auswahl; eine
  Auswahl mit kurzen Namen ist mindestens so breit wie ein Zahlenfeld.

## 2026-10-15 · Neue Materialien: C25/30 und B500B zuerst

«+» bei Beton legt zuerst C25/30 an, gibt es den schon, C30/37, und so
weiter aufwärts; nach C50/60 kommen die schwächeren von unten. Beim Stahl
zuerst B500B, danach die übrigen der Reihe nach (Benutzer). Vorher nahm
«+» die erste freie Sorte der Tabelle, also C12/15 und B500A.

Die Reihenfolge steht im Kern neben den Sortentabellen
(`betonsorten_zum_anlegen`, `stahlsorten_zum_anlegen`) und kommt über den
Katalog (`anlegen`) in die Oberfläche; die nimmt die erste Sorte, die es im
Projekt noch nicht gibt.

## 2026-10-15 · Die App «Python»

An die Stelle der analytischen Gleichungen tritt eine App, in der Python
läuft (Benutzer): Skripte, gespeichert mit dem Projekt; in der Mitte Code
und Konsole, rechts statt der Berechnung die Variablen -- wie in Spyder. Die
Entscheide des Benutzers: reines Python, ohne das offene Projekt im
Namensraum (`import opencivil` geht trotzdem); mehrere Skripte, eine Sitzung
für alle; die Variablen rechts; numpy und pandas dazu, Diagramme mit einem
eigenen Modul statt matplotlib.

- **Immer im Browser.** Der Code läuft in einem eigenen Faden mit Pyodide,
  auch wenn der lokale Server rechnet: über ihn könnte sonst jede Webseite
  Code auf dem Rechner ausführen. Derselbe Faden wie beim Rechenkern
  (`kern_arbeiter.js`), mit einem anderen Dienst (`opencivil.konsole.dienst`)
  und für sich: eine Endlosschleife hält weder die Seite noch den Kern an, und
  «Abbrechen» beendet ihn einfach -- unterbrechen liesse sich Python im Faden
  nur mit Kopfzeilen, die GitHub Pages nicht setzt. Er startet erst beim
  ersten Lauf; am Rechner war das Skript nach rund 5 s fertig.
- **Die Sitzung** (`konsole/sitzung.py`) sammelt, was ein Lauf ergibt, der
  Reihe nach: Ausgabe, Fehlerausgabe, den Wert der letzten Zeile (nur in der
  Konsole), Fehler mit Skriptname und Zeile -- ohne die eigenen Rahmen --,
  Bilder. Ein fehlendes Paket sagt, was beiliegt. `input()` meldet, dass es
  hier keine Tastatur gibt, die wartet.
- **Pakete** lädt die Konsole erst, wenn ein Skript sie mit `import`
  einbindet (`konsole/pakete.py`); welche beiliegen, steht im
  Kernverzeichnis, das der Faden dafür neben `opencivil/` einhängt.
- **Diagramme** (`konsole/zeichnen.py`): die gängigen Befehle von
  matplotlib.pyplot unter denselben Namen; ein Bild ist eine Beschreibung,
  die Oberfläche zeichnet sie mit dem Achsenkreuz aller Diagramme
  (`web/js/zeichnen.js`), mit Legende und dem Wert beim Darüberfahren. `show()`
  stellt es zwischen die Ausgaben, was offen bleibt, kommt am Ende des Laufs.
- **Der Code wird nicht neu gezeichnet**, solange dasselbe Skript gewählt
  ist -- sonst spränge der Cursor. Gespeichert wird kurz nach dem Tippen und
  vor jedem Lauf, als Anlass «skript»: das rechnet nichts neu.
- Das Beispielprojekt hat ein Skript mit einem Diagramm, ohne Download.

## 2026-10-15 · numpy und pandas liegen bei

Für die App «Python», die als Nächstes kommt, liegen numpy und pandas samt
dem, was pandas braucht, unter `web/vendor/pyodide/` (5 Dateien, 7.85 MB).
Der Benutzer hat sie Datei für Datei freigegeben; SciPy (14 MB) und
matplotlib (9.6 MB) wollte er nicht -- Diagramme macht ein eigenes Modul.
Seaborn wäre keine leichtere Wahl gewesen, es baut auf matplotlib; Plotly
gehört nicht zur Pyodide-Verteilung und wäre mit plotly.js grösser.

- `werkzeug/pyodide_holen.py --pakete` holt sie aus der vollen Verteilung
  derselben Fassung und hält jede Datei gegen ihre Prüfsumme in
  `pyodide-lock.json`; beim Wechsel der Fassung kommen sie mit.
- Welche beiliegen, schreibt die Brücke aus den Dateien ins Kernverzeichnis
  (`pakete` in `web/kern/dateien.json`) -- keine zweite Liste.
- Geladen wird ein Rad erst, wenn ein Skript es einbindet: wer die Seite nur
  zum Rechnen öffnet, lädt nichts davon.

## 2026-10-15 · Links Knöpfe je App

Die linke Tafel zeigt die Apps als Knöpfe mit Zeichen, wie die Kapitel einer
Platte in der Mitte (Benutzer): Materialien, Stahlbeton-Platten,
Querschnittsanalyse, 2D Balkensysteme. Unter den Knöpfen steht nur die Liste
der gewählten App, mit «+» darüber; bei den Materialien je eine für Beton und
Betonstahl. Der Name des Projekts ist aus der Kopfleiste zuoberst in diese
Tafel gezogen.

- Welche App gewählt ist, steht in `zustand.app`; wer einen Eintrag wählt,
  wählt seine App mit (`waehlen`). Das Zuklappen der Kapitel (`offen`) gibt
  es nicht mehr -- es gibt nur noch eine Liste.
- Auf dem Knopf steht nur die Anzahl: «1 Querschnittsanalyse» passte nicht
  in die schmale Spalte.
- Die Knöpfe rollen nicht mit, nur die Liste darunter.

## 2026-10-15 · Analytische Gleichungen entfernt

Die App «Analytische Gleichungen» ist weg (Benutzer): an ihre Stelle kommt
eine App, in der Python läuft, mit Konsole und Variablen. Mit ihr gingen der
Leser der LaTeX-Zeilen (`opencivil/gleichungen/`), die Beschreibung der
Blätter (`projekt/gleichungen.py`), ihr Editor (`web/js/gleichungen.js`) und
MathLive (840 KB unter `web/vendor/`), das nur sie brauchte. Das Prüfprojekt
«Jeder Nachweis» hat kein Blatt «Vorbemessung» mehr; sonst ändert sich am
Bericht nichts.

Eine alte Datei mit Blättern öffnet sich weiter: die Blätter fallen beim
Lesen weg, ohne Hinweis (Benutzer: «Einfach löschen»). Alte Stände müssen
ohnehin nicht weiter funktionieren (2026-10-11).

## 2026-10-15 · Die Suche prüft ihre Ebene selbst

Mit dem Spannungsblock -- Handrechnung und 0.85·x -- gibt es bei viel Druck
und wenig Moment keine Dehnungsebene: der Block liegt immer ganz an einem
Rand und gibt mehr Moment, als einwirkt. Die Suche endete dann an einem
Sprung, meldete «gefunden», und die Mitschrift hakte die Probe ab. An einer
Platte h = 250, ⌀12 oben und unten, quasi-ständig N = -600 kN, M = 14.5 kNm
stand «N_int = -170.1 kN ✓, M_int = 1.4 kNm ✓»; das Bild «N, M» der Analyse
zeigte eine Ebene mit -2490 kN. Präzise gibt es die Ebene. Gefunden bei der
Durchsicht nach dem Knicken (siehe darunter), der Benutzer wählte die
Abhilfe: die Suche prüft sich selbst.

- **Eine Stelle:** `Faserloeser._mit_probe` hält N_int und M_int gegen das
  Ziel. Die Schranke hängt am Querschnitt, nicht an der Last
  (`probenschranken`): ein Millionstel der Druckkraft des ganzen
  Querschnitts bei seiner Grenzstauchung, das Moment mal seiner Höhe. An
  beiden Prüfprojekten bleiben 1684 gefundene Ebenen unter 0.4 % davon; eine
  verfehlte liegt um Hunderte Kilonewton daneben. Trifft sie nicht, ist die
  Ebene verfehlt (`Ebene.verfehlt`), nicht gefunden.
- **Was dasteht:** `Rechenart.ohne_ebene` -- «Mit der 0.85·x-Vereinfachung
  gibt es zu dieser Einwirkung keine Dehnungsebene – präzise rechnen.», bei
  der Handrechnung entsprechend. Die Stahlspannungen der Platte und des
  gezeichneten Querschnitts schreiben es statt der Probe, der Fall ist nicht
  erfüllt; das Bild «N, M» sagt dasselbe. Die schiefe Biegung prüft am Ende
  auch ihre Neigung, an M_y und M_z.
- **Die Linien bleiben, wie sie waren:** eine M-χ-Linie fragt nur, bei
  welcher Krümmung das Moment seinen Wert durchläuft -- am Sprung ist das
  seine Stelle (`spannungsanalyse._durchlaufen`). Ihre Zahlen sind
  unverändert.

## 2026-10-15 · Verformung beim Knicken nur noch präzise

Die Verformung beim Knicken -- die Ausmitte e_2d -- rechnet nur noch präzise,
mit der Parabel; Kriechzahl und Werte bleiben wählbar (Benutzer). Den
Spannungsblock gibt es dort nicht mehr: mit ihm hat das Moment über der
Krümmung flache Stücke, auf denen jede Krümmung dasselbe Moment trägt, und
nahe der Grenzkraft hing N_Rd davon ab, wie gesucht wurde (siehe den Eintrag
darunter). Der Widerstand beim Knicken bleibt bei 0.85·x oder präzise.

Was erlaubt ist, steht einmal: `VERFORMUNGSARTEN` in `nachweis/rechenwahl.py`,
gelesen von Platte, Querschnittsanalyse und Katalog. Eine alte Datei mit 0.85·x
oder Handrechnung für die Verformung liest sich als präzise:
`ERSATZ_ALTER_WAHL` ist dafür eine Kette geworden -- Handrechnung → 0.85·x →
präzise --, und gelesen wird, bis es die Wahl gibt. Im Widerstand wird die
Handrechnung damit weiter 0.85·x, in der Verformung präzise. Die Platte
«Parabel» des Prüfprojekts knickt jetzt präzise mit charakteristischen
Werten; ihre Grenzkraft ändert sich damit, sonst keine Zahl.

## 2026-10-15 · Knicken der Platte mit Illinois und Warmstart

Das Knicken der Platte sucht seine Ebenen jetzt wie das am gezeichneten
Querschnitt (Benutzer): mit Illinois, von der zuletzt gefundenen Krümmung
und Dehnung aus (`QuerschnittsloeserIllinois`, die Fasern der Platte mit der
Suche von `FaserloeserIllinois`). Die drei Knicknachweise des Prüfprojekts
brauchten 1 768 883 Faserdurchläufe, beinahe die ganze Rechenzeit; jetzt sind
es 518 917, und jede Grenzkraft ist auf 0.01 kN dieselbe.

**Wo ein Gesetz springt, wird halbiert.** Der erste Versuch machte überall
den Warmstart, und die Stütze q3 -- ihre Verformung rechnet absichtlich mit
dem Spannungsblock -- kam auf 4200 statt 4099.5 kN. Mit dem Block hat das
Moment über der Krümmung flache Stücke: dort trägt jede Krümmung dasselbe
Moment, und welche gefunden wird, hängt am Weg der Suche. Beide Löser sagten
bei 4200 kN «trägt nicht», wenn sie frisch anfingen; mit dem Gedächtnis der
vorigen Probekräfte fand der neue eine Ebene. Ein Ergebnis, das an der
Reihenfolge der Rechnungen hängt, ist keines. Springt ein Gesetz, sucht der
Löser darum wie jeder `Faserloeser`, halbiert und von vorn
(`FaserloeserIllinois.halbiert`); das gilt auch am gezeichneten Querschnitt.
Parabel und elastisch haben flache Stücke erst am vollplastischen
Querschnitt -- dort blieb an beiden Prüfprojekten jede Zahl, wie sie war, und
ein Test hält eine ganze Knickfolge gegen das Halbieren.

**Die Mitschrift sagt, wie gesucht wurde.** Der Löser beschreibt seine
Suche selbst (`Faserloeser.suche`); das Knicken schreibt damit «Illinois,
von der letzten Ebene aus» oder, beim Block, die Halbierungen.

## 2026-10-15 · Knicken am gezeichneten Querschnitt

Knicken gibt es jetzt auch für den gezeichneten Querschnitt, je Fall zu der
Zugseite, zu der sich der Stab biegt -- unten, oben, links, rechts.

**Ein Verfahren, zwei Stäbe.** Die Ausmitten-Iteration und die Suche nach
N_Rd brauchen vom Stab nur dreierlei: die Ebene zu N und M, den
Momentenwiderstand bei N und die statische Höhe (`Knickstab`). Das Verfahren
steht darum in `Knickverfahren`; die Platte (`Knicken`) gibt ihren Löser,
ihre Resistenzlinie und die Höhe ihrer untersten x-Lage, der gezeichnete
Querschnitt (`KnickenQA`) seine Fasern in der Richtung, den Bruchzustand bei
N und das d vom gedrückten Rand bis zum entferntesten Stab. Am Rechteck 400 ×
400 mit je drei ⌀20 geben beide dieselbe Grenzkraft, 3069.2 kN.

**Warmstart.** Jede Probekraft der Suche nach N_Rd ist eine ganze
Iteration, jede Iteration ein paar Ebenen mit wenig verschiedenen
Schnittgrössen. Der Illinois-Löser fängt darum bei der Krümmung und der
Dehnung an, die er zuletzt gefunden hat, statt von der grössten Krümmung
her einzugrenzen: 111 072 statt 390 801 Faserdurchläufe für dieselben sechs
Fälle, dieselben Zahlen auf 0.001 kN. Gemessen an der Zahl der Durchläufe,
nicht an der Zeit -- die schwankte auf dem ausgelasteten Rechner um das
Doppelte.

## 2026-10-15 · Gebrauchsnachweise am gezeichneten Querschnitt

Was die Platte unter Gebrauchslast nachweist, gibt es jetzt auch für den
gezeichneten Querschnitt: Rissbreite bei Zwang (Normalkraft und Biegung),
Stahlspannung quasi-ständig und Fliessen häufig. Drei neue Knöpfe unter
«Nachweise», dazu die Rissanforderung im Panel des Querschnitts.

**Je Stab statt je Lage.** Die Platte hält den dicksten Stab einer Lage gegen
die Rissbreite. Der gezeichnete Querschnitt kennt jeden Stab: jeder hat seine
eigene Grenze, mit seinem Durchmesser und dem `f_ctm` seines Betons, und
massgebend ist der kleinste Erfüllungsgrad (Benutzer). Eine verschmierte
Linie hat keinen Durchmesser; sie bekommt einen fiktiven, als lägen ihre
Stäbe 150 mm auseinander (Annahme des Benutzers). Stäbe mit derselben Grenze
werden einmal hergeleitet (`nachweis/stabgrenzen.py`).

**Zwang auf Normalkraft am ganzen Querschnitt** (Benutzer): der ganze Beton
reisst, `N_Riss = Σ A_c·k_t·f_ctm` mit `t` als kleinerer Abmessung, gegen
`Σ A_s·σ_s,adm` aller Stäbe. Bei der Platte nimmt jede Lage die Hälfte --
zusammen derselbe Gedanke. **Zwang auf Biegung je Richtung** (Benutzer):
dasselbe Rissmoment wie beim spröden Versagen -- es steht dafür jetzt einmal
als Funktion da (`richtungsnachweise.rissmoment`) --, gegen das Moment, bei
dem der erste gezogene Stab seine Grenze erreicht: gerissen, elastisch, mit
eigenem φ. Linear ist das ein Dreisatz; kommt der Beton über `f_ck`, sucht
Illinois weiter. An einem Rechteck mit Stäben nur unten trifft es die
Handrechnung der Platte, `σ_s,adm·A_s·(d − x/3)`, auf 0.03 %.

**Die Ebene bei schiefer Biegung** (`nachweis/gebrauchsebene.py`): zu einer
Neigung ψ ist es die Aufgabe der Platte; ψ dreht, bis auch das Moment entlang
der Nulllinie stimmt. Erst halbiert brauchte das am Unterzug 2.7 s für alle
vier Nachweise. Zwei Dinge holten das auf 0.15 s, bei gleichen Zahlen: ψ
folgt der Sekante statt fester Schritte, und der Löser sucht seine Ebene mit
Illinois statt durch Halbieren. Dafür hat `Faserloeser` eine Methode
`_suchen` bekommen, die eine Unterklasse ersetzt (`FaserloeserIllinois`);
die Platte halbiert weiter, ihre Berichte sind Zeichen für Zeichen gleich.

**Nichts doppelt.** Die Texte der Stahlspannung -- Kriechen,
Werkstoffgesetze, was beim Fliessen verglichen wird -- stehen einmal
(`spannungsbegrenzung.protokoll_festlegungen`), die Gebrauchsliste ist
dieselbe Klasse mit anderem Fall (`QAGebrauchsliste`: N, M_y, M_z), und die
Fenster der Oberfläche sind die der Platte mit einem anderen Ort
(`ort.zwang`, `ort.gebrauch` in `nachweise.js`).

## 2026-10-15 · Spannung-Dehnung-Analysen am gezeichneten Querschnitt

Die sechs Analysen der Platte gibt es jetzt auch für den gezeichneten
Querschnitt, je Zugseite -- unten, oben, links, rechts. Gerechnet wird mit
denselben Funktionen; neu ist nur, wie der Querschnitt zu ihnen kommt.

**Ein Löser für jeden Faserquerschnitt.** `Querschnittsloeser` baute seine
Fasern aus Höhe, Breite und Lagen und suchte darin die Ebene. Die Suche
braucht davon nichts als die Fasern und die Dehnungsgrenzen. Sie steht jetzt
in `Faserloeser`; die Platte baut ihn wie bisher, der gezeichnete Querschnitt
aus `Querschnitt.richtung(psi)` -- den Fasern, mit denen schon seine
Tragsicherheit rechnet. Bilder und Linien lesen vom Löser die Ränder (`oben`,
`unten`), die Lagen und die Spannung des Betons an einer Stelle; das sagt
jeder Querschnitt selbst. Bei der Platte liegt die Mitteldehnung auf halber
Höhe, beim gezeichneten Querschnitt im Schwerpunkt, wo N angreift.

**Ein Paar je Art.** Das Löserpaar der Platte (`Loeserpaar`) und das des
gezeichneten Querschnitts (`Schnittpaar`) haben dieselben Glieder: gerissen,
ungerissen, Riss, Bezugsfläche des Moduls. Was nur eine Art weiss -- wie
sie reisst, woran sich der Modul misst, wo die Mitteldehnung gilt --,
schreibt jedes Paar in die Herleitung selbst; der übrige Text ist derselbe.
Bei der Platte ist `W/A = h/6`, also derselbe Riss wie bisher.

**Annahmen**, im Code «nach Vorgabe, nicht nachgeschlagen», in [[TODO]]: die
Nulllinie bleibt parallel zur Achse; der Riss am Bruttoquerschnitt mit `k_t`
wie bei der Platte, `f_ctm` vom Beton am gezogenen Rand; der äquivalente
Modul am Bruttoquerschnitt.

**Dabei:** Stäbe in derselben Tiefe, aus demselben Stahl, sind im Bild eine
Lage -- sie haben dieselbe Dehnung, und dreissig Punkte übereinander liest
niemand. Die Analysen zerlegen in 60 Streifen statt der 200 der
Tragsicherheit: eine Linie rechnet viele Ebenen, und M_Rd ändert sich dabei um
zwei Zehntelpromille. Jede Dehnungsgrenze trägt jetzt ihren Namen mit Seite
(«Beton C30/37, Rand oben»), damit «massgebend» sagt, wo.

## 2026-10-15 · Querschnittsanalyse: Kapitel als Knöpfe

Wie bei der Platte: oben der Querschnitt mit dem Zeichenfenster, darunter je
Kapitel ein Knopf, die Eingaben im Fenster. Die drei Panels Werkstoffe,
Schubwände und Nachweise sind weg. Die Rechenwerte je Material und die
Angaben der Schubwände stehen im Fenster der Tragsicherheit: die Werkstoffwahl
ist ihre Rechenwahl -- Duktilität und sprödes Versagen rechnen am selben
Querschnitt, ihre Fenster sagen es --, und Neigung, k_c und Längszugkraft
braucht allein die Querkraft mit Torsion.

`kapitel.js` ist dafür allgemein geworden: Knopf, Panel und Fenster für
jedes Bauteil. Welche Kapitel eine Art hat, steht bei ihrem Editor -- die der
Platte in `editor.js`, die der Analyse in `querschnittsanalyse.js`.

## 2026-10-15 · Zeichenfenster: der Vektor beginnt am angeklickten Knoten

Verschieben und Kopieren fragten zuerst nach einem Basispunkt, dann nach dem
Ziel -- zwei Klicks, auch wenn man den Knoten gerade angeklickt hatte, um
ihn zu wählen. Jetzt merkt sich das Fenster den zuletzt angeklickten Knoten
(`a.anker`): eine Ecke, ein Stab, ein freier Knoten. Mit V oder C beginnt der
Vektor dort, und der Knoten ist zugleich Bezugspunkt -- getippte Δy und Δz
sind die Verschiebung selbst. D wählt einen anderen Startpunkt; Esc kehrt von
dort zum angeklickten zurück und beendet beim zweiten Mal. Ein Rahmen und das
Abwählen vergessen den Knoten; dann fragt der Befehl wie bisher zuerst nach
dem Startpunkt.

Dafür kann ein Befehl jetzt eigene Tasten haben (`tasten`), die zugleich als
Knopf im schwebenden Fenster stehen, und beim Start etwas tun (`start`). Das
Zeichenfenster ist dasselbe für Querschnittsanalyse und Balkensystem; beide
haben es.

## 2026-10-15 · Oberfläche: Kapitel als Knöpfe, kompakte Bewehrung

Auf Wunsch übersichtlicher, in drei Schritten. Gerechnet wird dasselbe.

**Graue Panels, schlichter Baum.** Ein Panel ist eine graue Fläche mit Rand:
man sieht, wo eines aufhört. Die Karten darin -- Lagen, Einwirkungen --
bleiben weiss. Der Baum links trägt keine Zeichen und keine farbigen Kanten
mehr.

**Die Bewehrung braucht gut die Hälfte der Höhe.** Eine Lage ist so hoch wie
ihre zwei Zeilen Grund und Zulage, 68 statt rund 110 px: Nummer und Richtung
stehen links daneben statt in einer eigenen Kopfzeile, der Stahl am Ende der
Grundzeile, «ungünstig/günstig» als ein Knopf am Ende der Zulage. Ob die
Zahl eine Teilung oder eine Stabzahl ist, schaltet die Einheit selbst
(«mm» ↔ «Stk») -- ein eigener Knopf kostete jede Zeile eine Spalte. Die
Zahlenfelder der Lagen sind auf vier Ziffern bemessen statt auf acht. Die
Bügel sind gebaut wie eine Lage.

**Die Kapitel sind Knöpfe, ihre Eingaben stehen in einem Fenster.** Unter der
Bewehrung stand bisher alles offen untereinander -- sieben Nachweise, die
Analysen, die Suche --, und wer die Bewehrung neben einer Einwirkung sehen
wollte, rollte weit. Jetzt steht jedes Kapitel als Knopf da, mit Zeichen und
einer kleinen Zeile, was eingestellt ist; ein Klick öffnet die Eingaben in
einem Fenster über der mittleren Tafel. Baum und Ergebnis bleiben sichtbar,
damit man sieht, was eine Eingabe bewirkt. Jede der sechs Analysearten hat
ihren Knopf; im Fenster wird die Art darum nicht mehr gewählt, ein neues
Bild bekommt sie mit. Jedes Kapitel steht einmal in `kapitel.js`, was in
den Fenstern steht, liefert `nachweise.js`.

Welches Fenster offen ist, ist Ansichtssache (`zustand.fenster`) wie die
offenen Kapitel im Baum. Es gehört zum gewählten Bauteil: wer ein anderes
wählt, schliesst es -- alle Wahlen gehen dafür durch `waehlen`. Gezeichnet
wird es mit dem Editor neu. Der graue Grund darunter bleibt dabei stehen und
ist der Knoten, der rollt; so retten Bildlauf und Fokus wie bei den Tafeln.

**Was nur die Querkraft braucht, steht bei ihr.** Grösstkorn und
Einlagenhöhe (ohne Bügel), k_c und die Grenzen der Neigung (mit Bügeln) gehen
in keinen anderen Nachweis ein. Sie standen bei der Platte und bei den Bügeln
und stehen jetzt im Fenster der Tragsicherheit.

**Die Zeichen** sind eigene Linienbilder (`sinnbilder.js`), im Stil wie bei
Fagus, aber nicht von dort übernommen.

## 2026-10-15 · Bügelteilung, gleiche Fallnamen, Lagerkräfte am Bildschirm

Vier Punkte, die man sieht -- drei behoben, einer bestätigt.

**Eine Bügelteilung von null wird gemeldet.** Beim Lesen wurde sie still zu
200 mm (`wahl(...) or 200`): die Maske zeigte 0, gerechnet wurde mit 200. Eine
Null in y liess die Bügel sogar ganz verschwinden. Jetzt sagt allein der
Durchmesser, ob Bügel liegen; mit Bügeln müssen die Teilungen und die
Stabzahl grösser als null sein, sonst steht es als Satz da. Geprüft wird
beim Bauen, nicht beim Öffnen: eine Datei mit 0 lässt sich so öffnen und
korrigieren. In y gilt wie in der Maske: steht eine Teilung da, ist es die
Teilung, sonst die Stabzahl.

**Gleiche Fallnamen halten nur ihr System auf.** Heissen zwei Lastfälle,
zwei Kombinationen oder ein Lastfall und eine Kombination gleich, wären die
Fälle nicht zu unterscheiden -- sie werden am Namen erkannt. Bisher fiel das
in `pruefen` auf, und das ganze Projekt rechnete nicht, auch keine Platte.
Jetzt ist es eine Meldung des Systems: es rechnet nicht und sagt warum, der
Rest rechnet weiter.

**Lagerkräfte: dieselben Zeilen in Herleitung und Bildschirm.** Der
Bildschirm zeigte nur die Lager an Knoten. Beim gebetteten Balken fehlte
damit die Bettung, und die Kräfte gingen nicht auf: Einfeld mit 10 kN/m auf
6 m, ein Lager und Bettung -- am Bildschirm 11.7 kN, in der Herleitung
11.7 + 48.3 = 60 kN. Jetzt stellt `Systembefund.lagerkraefte` die Zeilen
an einer Stelle zusammen: Lager an Knoten, gehaltene Stellen auf Stäben,
die Summen von Linienlager und Bettung. Die Tabelle zeigt alle; unter dem
Bild steht, was keinen Pfeil hat.

**«kNm» in der Herleitung der Platte ist richtig.** Der TODO-Eintrag
«gemeint ist kNm/m» stammte vom 11.09.; seit dem 26.09. gelten M und N
bewusst je Streifen b (siehe [[Arbeitsweise]], «Entschieden»).

## 2026-10-14 · Umbau: Ergebnisse im Rechenlauf, ein Steckbrief je Bauteilart

Zwei Befunde der Strukturdurchsicht (siehe [[TODO]], «Umbau»). Kein Ergebnis
hat sich geändert; im Bericht fehlt einzig die Zeile «Anzahl der
Unbekannten» in der Werteliste -- die Zahl steht weiter in der Herleitung.

**Ergebnisse stehen in der Lösung, nicht am Objekt.** Bisher legten die
Nachweise, das Balkensystem und das Gleichungsblatt beim Rechnen auf sich
selbst ab, was sie fanden -- Interaktionslinie, Werte je Lage und Fall,
Wände und Schubfluss, das Systemergebnis --, und jeder Lauf überschrieb es.
Wer las, musste wissen, welcher Lauf zuletzt war. Der Zwischenspeicher
hängte darum ganze Objekte zwischen zwei Aufbauten um (`TEILEFELDER`,
`teile_von`, `teile_setzen`) und bildete die Felder der Lösung in
`Teilergebnis` von Hand nach. Jetzt gibt `rechne()` eine `Ausfuehrung`
zurück: Ausgaben, Urteile und einen Befund. Die Lösung hält
`befunde[berechnung_id]`; Diagramme, Zusammenfassung und Fassade lesen
dort. Wer den Befund einer anderen Berechnung braucht -- Knicken und
Querkraft die Linie der Tragsicherheit --, meldet einen `Befundbezug` an,
und der Löser rechnet sie zuerst. Der Speicher legt je Bauteil seine Lösung
ab (`Loesung.anhaengen`).

Das ersetzt «Das Ergebnis bleibt darum am Objekt» aus dem Eintrag zu den
Balkensystemen: `p.rechnen().balkensystem("Rahmen")` liefert jetzt den
`Systembefund`, mit `ergebnis` und `verlaeufe()` wie vorher.

**Ein Ziel darf eine Berechnung sein.** Wer eine Berechnung rechnen wollte,
musste einen ihrer Werte als Ziel nennen. Darum gab es Werte, die niemand
las: die Zahl der Unbekannten, die Zeilenzahl eines Blatts und den
Querkraftfall «ohne Einwirkung» mit sieben Weichen und `nur_ziel`. Jetzt ist
die ID einer Berechnung selbst ein Ziel; sie läuft einmal, auch ohne
Ausgabe. Nachweise, Systeme und Blätter sind Ziele unter ihrer ID. Ein
Querkraftnachweis ohne Lastfall rechnet so still für sein Bild; mit Bügeln
hält sein Befund den Ast bei M = 0 und N = 0 (`ohne_einwirkung`), damit das
Bild auch ohne Fall dasteht.

**Ein Steckbrief je Bauteilart.** Platte, Querschnittsanalyse und
Balkensystem standen an rund dreissig Stellen einzeln, und viele schwiegen,
wenn man eine vergass: ein Eintrag ging beim Öffnen verloren, ein Nachweis
wurde nie gerechnet, eine Kennung kam doppelt vor. Jetzt hat jede Art ihre
`Bauteilart` in `BAUTEILE` (`projekt/aufbau.py`): Liste in der Datei, Klasse
der Einträge, Vorsilbe, Namensraum, Abschnitt der Formelsammlung,
Baufunktion. Gebaut wird je Eintrag ein `Bauteil`, bei dem seine Nachweise
angemeldet werden (`Aufbau.eintragen`); Ziele, Urteile und Bezüge kommen von
dort, und niemand liest mehr aus «q1.x» zurück, wem ein Nachweis gehört. In
der Oberfläche steht dasselbe in `ARTEN` (`web/js/arten.js`): Baum, Editor,
Zusammenfassung und Diagramme gehen sie durch. Liste, Vorsilbe und
Namensraum stehen an beiden Orten; ein Test hält sie gleich
(`tests/test_arten_js.py`).

**Dabei gefunden:** Die Bewehrungssuche behielt in ihrer Arbeitskopie alle
Querschnittsanalysen und Balkensysteme. Im Beispiel zählte sie deren Urteile
mit; im Prüfprojekt scheiterte die Bewertung an einem System, das eine
andere Platte nimmt. Jetzt rechnet sie nur ihr Bauteil (`Projekt.nur`).

## 2026-10-12 · Gemischte Stahlsorten: jede Lage rechnet mit ihrem Stahl

Gefunden in der Strukturdurchsicht (siehe [[TODO]], «Umbau»), nachgerechnet:
Der Editor lässt je Seite einen eigenen Stahl wählen, aber Stahlspannung,
Knicken, Querkraft ohne Bügel und die Spannung-Dehnung-Analyse nahmen den
Stahl der ersten Lage für alle Lagen (`posten[0][0].stahl`). Unten B700B und
oben B500B: die Stahlspannung rechnete die obere Lage mit f_yd = 609 statt
435 N/mm², die Querkraft las nur B500B. Nur die Tragsicherheit rechnete je
Sorte -- sie baute ihre Lagen auf einem zweiten Weg.

**Die Lage trägt ihren Stahl.** `Stahllage` hat jetzt ein Feld `stahl`
(ein `Stahlgesetz` mit den Festigkeiten des Wertesatzes) und `sorte`.
Gebaut wird sie an einer Stelle, `rechenwahl.stahllagen()`, angemeldet über
`lagenbezuege()` unter `{kennwert}__{sorte}` -- genau so, wie die M-N-Linie
es schon tat. Ihr Tupel `(a_s, z, Gesetz, Text)` und
`dehnungsfaecher.lagen_aus_eingaben` sind weg: Löser, genaue Linie,
Handrechnung und Analyse sehen eine Lage jetzt in derselben Gestalt. Der
Löser bekommt keinen Stahl mehr, sondern macht aus dem Stahl jeder Lage ihr
Gesetz (`bilinear`, in der Handrechnung nur auf Zug).

**Wo es auf die Seite ankommt, entscheidet die Seite:**

- Stahlspannung: je Stahl eine Grenze (`f_yd − 80`, bzw. aus der
  Rissbreite mit `f_yk` und `E_s` der Sorte). Massgebend ist die gezogene
  Lage mit dem kleinsten Erfüllungsgrad -- bei einem Stahl dieselbe wie
  bisher, die am stärksten gedehnte.
- Querkraft: `ε_v` mit `f_yd` und `E_s` der gezogenen Seite, je Fall und
  in der M-V-Kurve je Momentenrichtung.
- Analyse: Fliessbeginn, wo die erste Lage die Fliessdehnung *ihres*
  Stahls erreicht; die Grenzen des Fächers je Lage mit ihrem `ε_ud`; in der
  Herleitung `ε_y` je Stahl.
- Knicken: das Suchfenster reicht im Zug bis zur kleinsten Bruchdehnung der
  Lagen, an beiden Rändern. Das ist die vorsichtige Lesart des Fensters
  am Rand, das schon vorher eine Vereinfachung war -- ob Knicken die
  Grenzen des Fächers bekommt, steht im TODO beim Querschnittsmodell.

**Mit einem Stahl ändert sich nichts** -- auch nicht im Bericht: gleiche
Zeichen, gleiche Zahlen, gleiche Sätze. Neue Sätze und Indizes erscheinen
nur, wo eine Richtung zwei Stähle hat. Einzige Ausnahme in der Sache: die
Stahlspannungen rechneten fest mit `ε_ud = 4.5 %` statt mit dem der Sorte;
bei B500B ist das dasselbe, bei B500A und B500C gilt jetzt die Sorte.

## 2026-10-12 · 2D Balkensysteme: ein ebener Rahmen nach der Steifigkeitsmethode

Wunsch des Benutzers: unter der Querschnittsanalyse eine App für ebene
Balkensysteme -- gezeichnet wie der Querschnitt, Stäbe mit Querschnitt und
Material, Lager und Federn, Gelenke, Lastfälle und Kombinationen, gerechnet
nach der Steifigkeitsmethode. Er wählte den ebenen Rahmen: Normalkraft statt
Torsion.

**Ein eigener Rechenkern, `opencivil/stabwerk/`, ohne Projekt und ohne
Rechenwerk.** Gleichungslöser, Stab, System, Verläufe und Querschnitte
kennen nur Zahlen in SI. So lassen sie sich gegen Handrechnungen prüfen --
Einfeldträger, Kragarm, Zweifeldträger, Dreigelenkrahmen, Fachwerk, Bettung
nach Hetényi --, bevor irgendetwas anderes daran hängt. Erst
`stabwerk/rechnung.py` meldet ein System im Rechenwerk an.

**Gelöst wird im Profil, nicht dicht.** LDLᵀ mit umgekehrter
Cuthill-McKee-Nummerierung: ein gebetteter Stab wird in bis zu 64 Stücke
geteilt, und mit hunderten Unbekannten wäre eine dichte Matrix in Pyodide
spürbar. Ein Pivot unter 1e-10 · K_ii heisst beweglich; dann wird die
Unbekannte festgehalten, zu Ende zerlegt und die freie Bewegung gelöst -- so
kann die Meldung sagen, *was* sich bewegt, statt nur «singulär».

**Eine Drehung ohne Steifigkeit wird gestrichen, erkannt an der Verbindung.**
Hängt ein Knoten nur an Gelenken, wäre seine Zeile in K null. Statt sie mit
einer kleinen Feder zu verstecken, fällt sie weg, ist null und heisst
«Verdrehung nicht bestimmbar, da keine Steifigkeit» -- so verlangt es der
Benutzer, und eine erfundene Feder wäre eine Zahl, die niemand eingegeben hat.

**Ein Gelenk ist eine eigene Drehung des Stabendes.** Die Alternative, die
Stabmatrix zu kondensieren, hätte für jede Gelenkkombination eine eigene
Matrix gebraucht und die Drehung des Endes verloren, die die Biegelinie
braucht.

**Ein festes Linienlager ist exakt, nicht steif.** Liegt ein Stab quer fest
auf, biegt er sich nicht, und seine Last geht geradewegs ins Lager. Eine sehr
steife Bettung hätte dasselbe genähert und die Matrix verdorben.

**Nichts Unmögliches wirft.** Ein bewegliches System, ein Stab ohne
Querschnitt, eine Last hinter dem Stabende sind Meldungen am Ergebnis: der
Rest des Projekts rechnet weiter. Hart scheitert nur ein Verweis auf ein
Material, eine Platte oder Analyse, die es nicht gibt -- und das verhindert
schon der Baum, der nichts löschen lässt, was ein System braucht.

**Die Prozedur liefert nur die Zahl der Unbekannten.** Das Rechenwerk will
für jede Ausgabe einen Wert, auch wenn das System beweglich ist. Extremwerte
je Fall gäbe es dann nicht. Das Ergebnis bleibt darum am Objekt, und
Zusammenfassung, Bilder und Zwischenspeicher lesen es dort; der Abdruck im
Speicher zählt die Platten und Analysen mit, aus denen ein System liest.

**Lasten stehen an ihrer Linie, Lager und Knotenlasten neben den Knoten.**
So gehen Stablasten mit, wenn eine Linie kopiert, gelöscht oder rückgängig
gemacht wird. Ein Lager als Feld am Knoten ginge verloren, sobald das
Zeichenfenster zwei Knoten zusammenführt.

**Teilen und Umkehren rechnet der Kern.** Dabei entstehen Lastwerte -- der
Wert einer Trapezlast am Schnitt, gespiegelte Stellen, ein umgekehrtes
Vorzeichen bei quer und längs. Das wäre Rechnung in der Oberfläche. Ein Test
hält fest, dass beides die Lagerkräfte nicht ändert.

**Das Zeichenfenster kann «verbunden».** In der Querschnittsanalyse gehört
eine Ecke ihrem Element; ein Rahmen hängt an seinen Knoten. Statt die
Mechanik zu kopieren, stellt der Adapter das ein, dazu Einheit, Raster,
Werkzeuge und Zoomgrenzen -- die Querschnittsanalyse bleibt, wie sie war.

**Die Bilder kommen aus einer eigenen Anfrage**, wie die Diagramme der
Querschnittsanalyse: Verläufe sind gross, und die Rechnung bei jeder Eingabe
soll sie nicht mitschleppen. Die Oberfläche zeichnet nur, und zwischen den
dichten Proben des Kerns verbindet sie für die Anzeige gerade.

**Steifigkeit nach Vorgabe, nicht nachgeschlagen:** E_cm für Beton, E_s für
Stahl, am ungerissenen Bruttoquerschnitt, ohne Schubverformung, Theorie
1. Ordnung. Die Herleitung sagt es, das [[TODO]] führt es.

Die Rechteckformeln der Spannung-Dehnung-Analyse und der Stabquerschnitte
sind dieselbe Formel und heissen jetzt gleich -- «Fläche eines Rechtecks»,
«Flächenträgheitsmoment eines Rechtecks»; ihre Theorie ist dorthin gezogen.

---

## 2026-10-12 · Platte: M_Rd im M-χ-Bild, Rechenarten, Linie I bis zum Riss

Frage des Benutzers: Die M_Rd im M-χ-Bild stimmen nicht immer mit dem M_Rd
des Tragwiderstands überein. Die ganze Prüfung mit Zahlen steht in
[[Prüfung M_Rd der Platte]]; hier, was daraus folgte und warum.

**Der Name war falsch, nicht die Zahl.** Das Bild nannte den Fliessbeginn
«M_Rd» und das Ende «M_Rd,u». Wer den Widerstand suchte, fand den
Fliessbeginn, präzise bei N = 0 228.1 statt 235.7 kNm. Das Ende der Linie
und der Tragwiderstand stimmen bei gleicher Rechenwahl auf 0.05 %; ein Test
hält das für 0.85·x und präzise, φ 0 und 2 und beide Wertesätze fest. Jetzt
heisst der Fliessbeginn M_y, wie seine Krümmung χ_y, und das Ende M_Rd.

**Handrechnung nur, wo ein Polygon Sinn ergibt.** Der Tragwiderstand mit
Handrechnung ist ein Polygon durch vier Eckpunkte, dazwischen gerade -- unter
Druck bis 18 % unter der genauen Linie desselben Modells. Die M-χ-Linie und
das Knicken rechnen die Normalkraft aber Ebene für Ebene genau; dort war die
«Handrechnung» nur ein Spannungsblock ohne Druckstahl, also eine schlechtere
0.85·x-Vereinfachung. Sie fällt dort weg (`FASERARTEN`). Eine alte Datei
liest sich als 0.85·x (`ERSATZ_ALTER_WAHL`); die Zahlen steigen dann leicht,
weil die Druckbewehrung mitzählt -- im Prüfprojekt N_Rd,K 3900.6 → 4496.7 kN.
Die eigene Linie des Knickens rechnet schnell mit den Schritten der Suche,
sonst zahlte die Bewehrungssuche jetzt öfter eine ganze genaue Linie.

**Namen nach Wunsch.** «Handrechnung», «0.85·x-Vereinfachung», «Präzise ohne
Vereinfachung» -- an einer Stelle (`Rechenart.beschriftung`, `kurz`,
`latex`), auch für die Betongesetze der Querschnittsanalyse.

**Zugfestigkeit nur für den Riss.** Die gestrichelte Vergleichslinie
«ungerissen» lief über den Riss hinaus bis zum Bruch -- dort mit Betonzug
ohne Grenze. Sie endet jetzt beim Riss. Kein Betongesetz und kein Widerstand
zählt die Zugfestigkeit; sie steckt in M_Riss und N_Riss und in den
Nachweisen, die vom Reissen handeln.

**φ in der Analyse.** Der ungerissene Teil rechnet immer mit E_cm/(1+φ),
auch bei 0.85·x -- das Feld war dort grau, obwohl φ wirkte. Es ist in den
Analysen jetzt immer aktiv, und bei 0.85·x sagt ein Hinweis, dass φ nur auf
den ungerissenen Teil wirkt. Die 0.85·x-Vereinfachung bleibt in den Analysen
wählbar (Benutzer), mit dem Hinweis, dass die Linie im Gebrauchsbereich zu
weich ist.

**E_eq-Bild.** Jede Ecke trägt ihren Modul und das Vielfache von E_cm: am
Anfang, vor und nach dem Riss, beim Fliessbeginn, am Ende.

## 2026-10-11 · Das Notizbuch: Dokumentation in Obsidian und auf der Seite

Wunsch: alle Notizen als Markdown, das Obsidian und die Seite lesen; die
Formelsammlung als verlinktes Notizheft, jede Formel eine Seite mit Theorie
und SIA-Verweis; global einsehbar über einen Knopf neben «Rechnen»; dazu,
wie die Python-Bibliothek funktioniert -- und ein Notizbuch für Claude.

**Ein Ordner, kein Plugin.** Obsidian liest einen gewöhnlichen Ordner als
Tresor: `notizbuch/`. Darin [[Start]], die Formelsammlung (111 Formel-, 18
Themenseiten, eine Übersicht), je Modul eine Python-Seite (80) und die
Notizen -- [[Arbeitsweise]] (die Regeln, die vorher privat lagen),
Entwicklung und TODO, mit `git mv` hierher verschoben. `CLAUDE.md` lädt die
Arbeitsweise in jede Sitzung; `.obsidian/app.json` stellt strenge
Zeilenumbrüche und Wikilinks ein.

**Eine Seite je Formelname.** Gleich benannte Formeln sind Fassungen einer
Seite (131 Formeln, 111 Seiten). Der Name ist der Titel ohne Zahlen, oder
`GleichungBlock.name`, wo der Titel je nach Fall wechselt oder nichts sagt
(«Ansatz», «C30/37: …», «Duktilität» wie das Thema). Er hängt nur an der
Formel, nie an Reihenfolge oder Zähler -- sonst stünde die Theorie beim
nächsten Lauf an der falschen Formel. Tests über die ganze Sammlung halten
das: eine Formel ein Name, eine Seite eine Grösse, kein Name wie ein Thema,
keine Sorte, jeder Name im Tresor einmal.

**Oben erzeugt, unten von Hand.** Die Brücke schreibt den oberen Teil jeder
Seite neu; unter der Linie `<!-- Ab hier von Hand … -->` bleibt die Theorie
Zeichen für Zeichen. Die Prüfsumme `erzeugt:` verrät Handänderungen oben --
dann schreibt die Brücke nichts und nennt die Datei. Notizen ohne
`erzeugt:` fasst sie nie an; eine verwaiste Seite mit Theorie bleibt mit
Hinweis stehen, ein Test ist rot, bis der Text umgezogen ist.

**Woher eine Grösse kommt** sagt die Rechnung selbst: je Lauf merkt sich der
Generator, welche Formel einen Wert zuletzt schrieb. Dafür trägt die
Formelzeile ihre Eingänge (`Formelzeile.eingaben`) und jede Gleichung ihre
Codestelle -- gefunden über den Aufrufstapel, weil viele Formeln von
Hilfsfunktionen in anderen Modulen geschrieben werden. Gekostet hat das
nichts Messbares.

**Die Python-Seiten** liest `bibliothek.py` mit `ast`, ohne Import: Docstring,
Klassen und Funktionen mit Signatur, Konstanten, Importe, Formeln. Zeilen in
GROSSBUCHSTABEN werden Überschriften, Eingerücktes Code, Rollen wie
`:class:` Links -- auch ohne vollen Namen, über die eigene Klasse und die
Importe. Keine Rolle bleibt offen (Test). Die leeren Pakete bekamen einen
Docstring, `opencivil` einen Abschnitt RECHENWEG.

**Auf der Seite** öffnet «Dokumentation» die Ansicht -- auf dem Telefon die
vierte Wahl «Doku» unten, weil die Kopfleiste voll ist. Den Markdown zerlegt
ein eigenes Modul ohne fremde Bibliothek (`markdown.js`, rein, mit node
über das ganze Notizbuch geprüft); `notizbuch_seite.js` baut daraus die Seite,
nie über `innerHTML`. Die Adresse `#notizbuch/<Name>#<Abschnitt>` trägt
Links, Zurück-Knopf und Lesezeichen. Seiten kommen ohne Zwischenspeicher:
eine in Obsidian geänderte Notiz steht nach dem Hochladen gleich da; eine
neue erst, wenn die Brücke sie ins Verzeichnis `web/kern/notizbuch.json`
geschrieben hat.

**Was wegfiel.** Der rechte Reiter «Formelsammlung» samt
`formelsammlung.json` -- an jeder Gleichung der Herleitung führt jetzt
«Formel» zur Seite. Und auf Wunsch der Knopf «Bericht» oben rechts.

**Theorie** steht unter jeder Seite, von Claude geschrieben, ohne erfundene
Normstelle: ein Test verlangt, dass jede «SIA 262 …»-Angabe darin auch im
Code steht. Annahmen heissen «nach Vorgabe, nicht nachgeschlagen». 80 von
111 Formeln haben noch keine Normstelle -- die Liste steht auf der Übersicht
der Formelsammlung.

**Unterwegs gefunden.** Der lokale Server dekodierte Adressen nicht: jede
Datei mit Umlaut oder Leerzeichen gab 404. Und der Docstring von `tresor.py`
zeigte die Trennlinie wörtlich -- auf seiner Modulseite hielt der Generator
sie für die echte und meldete «von Hand geändert». Eine ganz erzeugte Seite
darf die Linie jetzt nicht enthalten.

## 2026-10-11 · Spannung-Dehnung-Analyse: äquivalenter E-Modul über M und über N

Wunsch: zwei weitere Arten neben M–χ und N–ε. Auf der y-Achse der
äquivalente E-Modul -- der, den man einem reinen Betonquerschnitt geben
müsste (ungerissen, ohne Stahl, elastisch) --, auf der x-Achse das Moment
bei fester Normalkraft bis M_Rd,u, und ebenso die Normalkraft bei festem
Moment.

**Die Formel.** Aus M = E·I·χ und N = E·A·ε, mit dem reinen
Betonquerschnitt eingesetzt und der echten Verformung des bewehrten:

```
E_eq = M / (I_c · (χ − χ_0))       I_c = b·h³/12
E_eq = N / (A_c · (ε_m − ε_0))     A_c = b·h,  ε_m auf halber Höhe
```

χ und ε_m sind die Zahlen der M–χ- bzw. N–ε-Linie; gerechnet wird nichts
Neues, jeder Punkt wird umgerechnet (`Modullinie` in `spannungsanalyse.py`).

**Ab dem Zustand ohne laufende Kraft** -- deine Wahl. Was die feste Kraft
allein verformt, kann ein gerader, ungerissener Betonquerschnitt nicht
abbilden: bei unsymmetrischer Bewehrung krümmt schon eine Normalkraft, und
gerissen dehnt schon das Moment die halbe Höhe. Ab null gezählt, ergäbe das
nahe null Ausreisser:

```
N–E_eq bei M = 30 kNm, N = 16 kN
ab null gezählt           99 510 N/mm²   (fast 3·E_cm)
ab dem Zustand mit M      35 370 N/mm²   (wie bei M = 0)
```

Ist die feste Kraft null, sind beide gleich.

**Am Beispiel** (Decke über EG, charakteristisch, Parabel, φ = 0, N = 0):

| M | Zustand | E_eq | E_eq/E_cm |
|---|---|---|---|
| 0 … 41.4 kNm | ungerissen | 35 903 N/mm² | 1.07 |
| 41.4 kNm | gleich nach dem Riss | 8 925 N/mm² | 0.27 |
| 267.7 kNm | Stahl fliesst | 8 271 N/mm² | 0.25 |
| 278.3 kNm | Ende | 1 714 N/mm² | 0.05 |

Ungerissen von Hand: der ideelle Querschnitt mit (n − 1)·A_s gegen den
reinen Beton, E_c·I_id/I_c = 35 912 N/mm² -- 0.03 % darüber, das ist die
Teilung in 60 Fasern. Über N greift die Kraft auf halber Höhe an, der
ideelle Schwerpunkt liegt tiefer: E_c/(A_c·(1/A_id + v²/I_id)) = 35 366 N/mm²,
auf sechs Stellen wie die Linie.

**Die Beschriftung.** Fliessbeginn und Ende liegen über M nur wenige kNm
auseinander, ihre Namen fanden neben den Punkten keinen freien Platz und
lagen übereinander. Ein Name rückt jetzt, wenn alles am Punkt besetzt ist,
schrittweise höher und bekommt einen feinen Strich zum Punkt. Die neuen
Lagen kommen nach den alten an die Reihe; was vorher Platz fand, steht wo
es stand.

## 2026-10-09 · Rechenwahl je Kapitel, genaue Resistenzlinie, Vergrösserungsfaktor w/w_c

Wünsche:
* Tragsicherheit, Stahlspannung quasi-ständig, Fliessen häufig und Knicken
  wählen je selbst: die Kriechzahl φ, die Werte (Bemessung → M_Rd,
  charakteristisch → M_Rk) und die Rechenart -- Handrechnung Block 0.85·x,
  Block 0.85·x genau (mit Druckstahl) oder Parabel.
* Das Knicken zweimal: für die Verformung (e_2d) und für den Widerstand
  N_Rd(M_Ed = N_Ed·e_tot).
* Die Spannung-Dehnung-Analyse bekommt die Handrechnung als Rechenart.
* Das φ der Platte bleibt, gilt aber nur für den Vergrösserungsfaktor w/w_c
  nach SIA 262:2025, 4.4.3.2.5 -- in x, für Zug unten und Zug oben, auf zwei
  Stellen, in der Zusammenfassung neben Bewehrungsmass und Distanzhalter.
* Entschieden: jedes Kapitel hat sein eigenes φ, Vorgabe 0; «elastisch»
  bleibt bei den Stahlspannungen als vierte Art und Vorgabe; Querkraft und
  sprödes Versagen folgen der Tragsicherheit; ρ′ = A_s′/(b·d′) mit d′ vom
  gezogenen Rand bis zur Gegenlage.
* Nachgereicht: alte Speicherstände sind im Prototyp nicht wichtig.

**Eine Stelle für die Gesetze.** `nachweis/rechenwahl.py` hat die
`Rechenwahl` (φ, Wertesatz, Rechenart) und baut daraus Beton, Stahl, Lagen
und Löser. Vorher baute jedes Kapitel seine Gesetze selbst, und die Parabel
stand dreimal da. Die Rechenarten im Löser:

| Rechenart | Beton | Stahl | Lagen |
|---|---|---|---|
| Handrechnung | Block, auch wo der Stahl liegt | nur Zug | je Seite eine, im Schwerpunkt |
| Block genau | Block, über jede Faser gemittelt | Zug und Druck | jede für sich |
| Parabel | k_σ aus E_cm/(1+φ), nie unter 1 | Zug und Druck | jede für sich |
| elastisch | E_cm/(1+φ), höchstens f_c | Zug und Druck | jede für sich |

Mit «Handrechnung» endet die M-χ-Linie der Analyse genau beim M_Rd der
Handrechnung (am Beispiel auf 0.1 %, auch mit Druckbewehrung) -- das ist die
Probe, dass Löser und Linie dasselbe Modell meinen.

**Zwei Linien hinter einer Schnittstelle.** `nachweis/resistenzlinie.py`:
die `Handlinie` (das Polygon der Handrechnung) und die `Ebenenlinie` (der
Rand des Dehnungsfächers). Beide können dasselbe -- `innerhalb`, `kante`,
`moment_bei`, `eckwerte`, `protokoll_treffer` --, und der M-N-Nachweis,
die Querkraft, das spröde Versagen und das Knicken fragen nur noch die
Schnittstelle. Die Linie entsteht in einer Funktion (`resistenzlinie`), die
Tragsicherheit und Knicken teilen.

**Genau statt auf der Sehne.** Die Ebenenlinie sucht ihren Widerstand bei
N_Ed nicht auf der Geraden zwischen zwei Punkten des Fächers, sondern auf
dem Fächer selbst: zwischen den beiden Ebenen, deren Punkte ihn
einschliessen, mit dem Illinois-Verfahren. Zwei benachbarte Punkte liegen im
selben Abschnitt, also ist jede Ebene dazwischen eine des Fächers. Damit
hängt keine Zahl im Bericht an der Schrittweite der Zeichnung:

```
M_R bei N = −2000 … +300 kN, mit 20 und mit 160 Schritten gezeichnet:  Abweichung < 1e-9
```

Das Urteil fällt an denselben Rändern: drin ist, was bei dieser Normalkraft
zwischen dem linken und dem rechten Rand liegt. So kann es dem
Erfüllungsgrad nicht widersprechen. In die Herleitung kommt nicht die Suche,
sondern ihre Probe: die Ebene, die Kraft jedes Teils (der Stahl mit voller
Spannung, der Beton als Resultierende ohne die Fläche des Stahls), die
Summen und welche Grenzdehnung erreicht ist. Am Beispiel, Feld, Parabel mit φ = 2,
charakteristisch: ΣF = −1162.6 + 848.2 + 377.0 − 62.7 ≈ 0 kN,
ΣF·(z − h/2) = 277.2 kNm, massgebend der Beton am oberen Rand.

**Auch die Spitzen liegen zwischen den Ebenen.** Das grösste Moment sowieso
-- aber auch die grösste Druckkraft liegt nicht beim gleichmässigen −ε_c1d:
kippt die Ebene ein wenig um den Punkt C, fliesst die gedrückte Bewehrung und
trägt mehr. Beide werden mit dem Goldenen Schnitt zwischen den Nachbarn des
grössten Punkts gesucht.

**Der Stahl der Linie fällt jenseits von ε_ud nicht auf null.** Die unterste
Lage liegt im Fächer genau auf ε_ud. Ein Gesetz, das dort abbricht, kippte an
der Rundung -- 1e-19 zu viel, und die halbe Zugkraft wäre weg.

**Was die Wahl am Beispiel ändert** (Decke über EG, M_R bei N_Ed in kNm):

| Fall | Handrechnung | Block genau | Parabel |
|---|---|---|---|
| Feld (N = 0) | 235.9 | 236.2 | 235.7 |
| Feld mit Druck (N = −300 kN) | 253.8 | 265.3 | 264.5 |
| Stütze (N = 0, Zug oben) | 79.9 | 90.1 | 90.0 |

Block und Parabel liegen beisammen. Die Hand liegt an der Stütze 11 % tiefer,
weil sie die 2450 mm² gedrückter Bewehrung unten weglässt. Höher als die
genaue Linie liegt sie nur knapp: reisst der Stahl bei ε_ud, bevor der Beton
ε_c2d erreicht, ist die Druckzone weniger voll als ihr Block (Feld, 235.9 gegen
235.7).

**Charakteristisch heisst R_k, die Kennungen bleiben.** M_Rk, N_Rk, m_Rk in
der Querkraft, M_Rk(N_Ed = 0) im spröden Versagen, N_Rk,K beim Knicken. Die
Wert-IDs heissen weiter `…M_Rd…`: wer sie liest, soll nicht je nach Wahl
anders fragen müssen.

**Das Knicken teilt die Linie, wenn es darf.** Gleiche Wahl für den
Widerstand wie die Tragsicherheit -- die Kriechzahl zählt nur, wo sie wirkt --,
dann ist es deren Linie, einmal gerechnet und einmal hergeleitet. Sonst baut
es eine eigene, mit Herleitung, und im M-N-Diagramm steht sie gestrichelt
neben der massgebenden; die Knickpunkte liegen auf ihr. Nebenbei korrigiert:
die Herleitung nannte als Suchfenster −3.0 ‰, gerechnet wurde mit
ε_c2d = −3.5 ‰.

**w/w_c im Lagenaufbau.** Dort entstehen schon Flächen und Tiefen jeder
Lage, Bewehrungsmass und Distanzhalter -- der Faktor steht in der Herleitung
gleich daneben und braucht keine eigenen Rechenziele. d′ ist die statische
Höhe der Gegenlage, also ist ρ′ das ρ der Gegenseite. Am Beispiel:

```
Zug unten  ρ = 2450/(1000·248.1) = 0.00988   ρ′ = 0.00299   w/w_c = 4.00
Zug oben   ρ = 754/(1000·252)    = 0.00299   ρ′ = 0.00988   w/w_c = 7.52
```

**Alte Dateien.** Bis zur Nachricht, dass sie im Prototyp nicht zählen, hielt
ein Test eine Datei von vor der Rechenwahl Zahl für Zahl fest; jedes Kapitel
übernahm beim Öffnen das φ der Platte. Das Übernehmen bleibt, der Test ist
weg: er verlangte bei jedem Umbau Ausnahmen für Werte, die niemand mehr
braucht.

## 2026-10-09 · Spannung-Dehnung-Analyse: Wahl je Analyse, M-χ bis zur Grenze, N-ε-Linie

Wünsche:
* Im Dehnungsbild steht die Krümmung als χ, nicht als x.
* Jede Analyse wählt selbst: die Kriechzahl φ, Bemessungs- oder
  charakteristische Werte, Parabel oder Spannungsblock für den Beton.
* Die M-χ-Linie: M_Rd steht scheinbar am falschen Ort. Das oberste M heisst
  M_Rd,u. An allen Eckpunkten stehen die Krümmungen. Die Formelsammlung
  erklärt die Linie und die grösste Krümmung.
* Neu eine N-ε-Linie auf Zug, mit N_Riss, N_Rd und der grössten Dehnung,
  bei einstellbarem M_Ed.
* Nachgereicht: Der Fliessbeginn heisst im Bild M_Rd, nicht M_y.
* Nachgereicht: N_Riss mit k_t für die ganze Dicke, `k_t = 1/(1 + 0.5·t)`
  mit `t = h`.

**χ sah aus wie x.** JetBrains Mono zeichnet χ fast wie x. Griechische
Buchstaben in Bildern und Achsentiteln setzt jetzt `formelText` (in
`achsen.js`) in die kursive Formelschrift von KaTeX, `_y` und `_{Rd,u}`
tiefgestellt; das gilt für alle Diagramme. Die Zahlenzeile über den Bildern
setzt KaTeX. In der Auswahl «M–χ» kommen nur die griechischen Buchstaben aus
der Formelschrift (`@font-face` mit `unicode-range`).

**Wahl je Analyse.** Drei neue Felder am `SpannungsfallEintrag`:

| Feld | leer / Vorgabe | sonst |
|---|---|---|
| `kriechzahl` | die der Platte | eine eigene Zahl ≥ 0 |
| `werkstoffsatz` | `bemessung` (f_cd, f_yd) | `charakteristisch` (f_ck, f_yk) |
| `betongesetz` | `parabel` | `block` (0.85·x) |

Eine alte Datei hat die Felder nicht und rechnet darum mit den Vorgaben wie
bisher. Moduln und Grenzdehnungen sind in beiden Wertesätzen dieselben, wie
überall im Werkzeug.

**Das Ende der M-χ-Linie war falsch.** Am Beispiel, Decke über EG, x, N = 0:

```
vorher   Ende bei χ = 0.040 1/m, M = 234.6 kNm, Beton oben −2.7 ‰
nachher  Ende bei χ = 0.057 1/m, M = 235.4 kNm, Beton oben −3.5 ‰ = −ε_c2d
```

Die Linie endete dort, wo die Suche des Lösers aufgab, nicht dort, wo der
Querschnitt versagt (siehe unten). Jetzt rechnet sie den gerissenen Teil über
die Krümmung, nicht über das Moment. Sie endet bei der grössten Krümmung, zu
der es noch ein Gleichgewicht gibt. Das ist die erste erreichte Grenzdehnung,
dieselbe wie im Dehnungsfächer der genauen M-N-Linie:
* der Beton am Rand bei −ε_c2d;
* jede Stahllage bei ±ε_ud (vorher galt ε_ud am Betonrand);
* im Punkt C bei −ε_c1d.

Welche Grenze massgebend ist, steht am Ende der Linie.

**Fliessbeginn und Ende.** Der Stahl fliesst bei 224.6 kNm
(χ_y = 0.015 1/m). Danach wächst das Moment noch um 5 %: Die Druckzone wird
kleiner, und der Beton füllt sein Gesetz. Die Linie zeigt beide Punkte. Im
Bild heisst der Fliessbeginn, wie gewünscht, M_Rd und das Ende M_Rd,u:

```
zuerst   M_y  = 224.6 kNm   …   M_Rd,u = 235.4 kNm
jetzt    M_Rd = 224.6 kNm   …   M_Rd,u = 235.4 kNm
```

Mit charakteristischen Werten heissen sie M_Rk und M_Rk,u, bei der N-ε-Linie
N_Rd und N_Rd,u. Die Krümmung beim Fliessen behält ihr y. Das M_Rd des
M-N-Nachweises ist ein anderes: Es rechnet den Bruch, nicht den
Fliessbeginn, und entspricht darum M_Rd,u.

**Warum M_Rd,u nicht genau das M_Rd des Nachweises ist.** Der Nachweis
rechnet von Hand: Spannungsblock 0.85·x, ohne gedrückten Stahl, die Lagen je
Seite zu einer zusammengefasst. Die Linie integriert genau, mit
Druckbewehrung, und mit der kriechweichen Parabel (k_σ = 1.4 statt 4.2):

```
Handrechnung (Nachweis)                     235.9 kNm
Linie, Bemessung + Block                    236.2 kNm   (Druckbewehrung trägt mit)
Linie, Bemessung + Parabel                  235.4 kNm
Platte ohne Druckbewehrung, Block           170.0 kNm, Handrechnung 170.1 kNm (−0.03 %)
```

**Die N-ε-Linie.** M_Ed bleibt fest, N wächst auf Zug, gezeichnet über ε_m,
die Dehnung auf halber Höhe. Der Ablauf:
* ungerissen bis N_Riss = f_ct,eff·b·h − 6·|M|/h, am Bruttoquerschnitt;
* dort der Sprung;
* gerissen bis zum Bruch, mit dem Fliessbeginn N_Rd.

Wo sie endet, hängt an der Bewehrung. Symmetrisch bewehrt und ohne Moment
trägt am Ende der ganze Stahl, N_Rd = Σ A_s·f_yd, und die Lagen stehen auf
ε_ud. Das Beispiel ist unten stärker bewehrt (2450 mm²) als oben (754 mm²).
Dort endet die Linie bei 20 kNm im Beton:

```
M_Ed = 20 kNm    N_Rd,u = 1030 kN   Beton am unteren Rand bei −3.5 ‰
M_Ed = 71.5 kNm  N_Rd,u = 1390 kN   Stahl bei 45 ‰  (≈ Σ A_s·f_yd = 1393 kN)
```

Σ A_s·f_yd erreicht nur, wer das Moment des Stahlschwerpunkts mitbringt, hier
rund 71 kNm. Bei kleinerem Moment muss der Beton unten drücken.

**k_t für die ganze Dicke.** Zuerst rechnete N_Riss mit dem f_ct,eff des
Rissmoments, also mit k_t für ein Drittel der Dicke. Unter Zug reisst aber
der ganze Querschnitt. Jetzt gilt nach Vorgabe `k_t = 1/(1 + 0.5·t)` mit
`t = h`, wie bei der Zwängung auf Normalkraft (`beiwert_dicke`,
`protokoll_zugfestigkeit` mit `teiler=1`). Am Beispiel, h = 300 mm,
f_ctm = 2.9 N/mm²:

```
                 k_t     f_ct,eff      N_Riss(0)   N_Riss(20 kNm)
zuerst (h/3)     0.95    2.76 N/mm²    828.6 kN    428.6 kN
jetzt  (h)       0.87    2.52 N/mm²    756.5 kN    356.5 kN
```

Das Rissmoment der M-χ-Linie bleibt nach Vorgabe bei h/3, auch unter Zug:
Biegung reisst über ein Drittel der Dicke. Beim selben N und M reissen die
beiden Linien darum nicht mehr am selben Punkt:

```
M-χ-Linie bei N = 300 kN     reisst bei M = 26.4 kNm
N-ε-Linie bei M = 26.4 kNm   reisst bei N = 228 kN
```

**Die Karte.** Die Zeile einer Analyse ist eine kleine Karte. Sie hat drei
Zeilen:
1. Name und Richtung.
2. Art, ihre Zahlen und φ. Das Feld φ zeigt leer blass die Kriechzahl der
   Platte.
3. Werte und Beton, mit kurzen Namen. In einer Spalte fehlten «charakteristisch»
   80 px. Am Telefon stehen beide je auf einer eigenen Zeile.

**Formelsammlung.** Die Linien schreiben ihre Herleitung selbst, wie jede
Rechnung hier, unter dem Thema «Spannung-Dehnung-Analyse». Sie enthält:
* E_c,eff und die beiden Betongesetze;
* Zustand I und II;
* M_Riss(N) und N_Riss(M);
* den Fliessbeginn;
* die Grenzdehnungen, χ_u und ε_m,u.

`Projekt.jeder_nachweis()` führt dafür je eine M-χ- und eine N-ε-Analyse.
Die Berichte bleiben zeichengleich, denn Analysen stehen nicht im Bericht.

**Nebenbei: ein Fehler im gemeinsamen Löser.** `Querschnittsloeser.loese`
meldete nahe am Widerstand «keine Gleichgewichtslage», obwohl es eine gab.
Die Suche halbierte von der grössten Krümmung aus (0.16, 0.08, 0.04 1/m) und
sah zwischen 0.04 und 0.08 nie nach:

```
vorher   M = 234.9 kNm → keine Gleichgewichtslage
nachher  M = 234.9 kNm → χ = 0.046 1/m;  erst über 235.3 kNm wirklich keine
```

Jetzt sucht sie zuerst die grösste Krümmung mit Gleichgewicht und darunter
die Lösung. Den Löser nutzen auch der Knicknachweis und «Aus N und M». An
allen 41 Urteilen beider Prüfprojekte ändert sich nichts.

---

## 2026-10-09 · Eine Ecke gehört ihrem Element

Wunsch: Liegen Punkte aufeinander, soll ein Klick genau einen wählen. Eine
Bewehrungslinie, deren Anfang auf einer Polygonecke liegt, soll sich
verschieben lassen, ohne die Ecke mitzunehmen. Wer gezielt wählen will,
wählt zuerst das Polygon oder die Linie und dann die Ecke, mit Shift auch
mehrere. Ohne Auswahl gilt: zuerst die zuletzt gesetzte Bewehrung, dann das
zuletzt gezeichnete Polygon. Ein Rahmen wählt alle Punkte darin.

Vorher: Ein Knoten gehörte allen Elementen, die an ihm hingen. Der Klick
wählte den Knoten, und V verschob Polygon, Linie und Wände mit:

```
Linie von K1 gezeichnet, gewählt, V, 20 nach unten
vorher:   Polygonecke (0, 0) -> (0, -20), das Polygon verzogen
nachher:  Polygonecke bleibt bei (0, 0), nur die Linie wandert
```

Jetzt wählt man **Ecken von Elementen** («F1#2»: die dritte Ecke von F1):
* **Ein Klick nimmt genau eine Ecke.** Wo mehrere aufeinander liegen, gilt:
  1. die Ecke eines Elements, um das es gerade geht (es ist gewählt, oder
     eine seiner Ecken);
  2. sonst nach Art: Bewehrung (Linien, dann Stäbe), Schubwände,
     Hilfslinien, zuletzt Flächen;
  3. innerhalb einer Art das zuletzt gezeichnete, also die höchste Nummer.

  Ein zweiter Klick an derselben Stelle nimmt die nächste Ecke. Der Zeiger
  zeigt vorher, welche es wird: ein Quadrat und gestrichelt das Element, dem
  sie gehört. Schubwände und Hilfslinien hattest du nicht genannt; sie
  stehen als Linien vor den Flächen.
* **Shift nimmt dazu.** Polygon wählen, eine Ecke klicken, die zweite mit
  Shift: Es sind die zwei Ecken dieses Polygons, auch wo ein anderes
  Polygon sie teilt.
* **Ein Rahmen nach rechts** wählt, was ganz drin liegt, und jede Ecke im
  Rahmen, auch die aufeinanderliegenden. So bleibt verbunden, was man
  zusammen verschiebt.
* **Verschoben wird, was gewählt ist.** Hängt an einem Knoten auch etwas,
  das nicht mitkommt, bekommen die bewegten Ecken einen eigenen Knoten
  (`verschieben` in `cad_modell.js`). Danach ist, was genau aufeinander
  liegt, wieder ein Knoten: Das ist Ablage, keine Bedeutung. Kern und
  Dateiformat bleiben darum, wie sie sind.
* **«Lösen» ist weg.** Es tat von Hand, was jetzt jedes Verschieben tut.
* **Eine gewählte Ecke** zeigt im schwebenden Fenster ihre Lage, etwa
  «Linie 1 · Anfang». Geändert wird nur sie. Entf nimmt sie aus ihrem
  Umriss, solange drei Ecken bleiben; eine Linie ohne ihr Ende geht ganz.
  Kopieren gibt es nur für ganze Elemente.

Nachgespielt im Browser, am Unterzug:
* Linie von K1 nach (180, 120), gewählt, V, `0`, `-20`: Die Linie beginnt
  bei (0, −20), die Polygonecke bleibt bei (0, 0).
* Ohne Auswahl auf (0, 0): «Linie 3 · Anfang». Ein zweiter Klick: «Polygon 1
  · Ecke 1».
* Polygon, dann (0, 0), dann (300, 0) mit Shift, V um 30 nach unten: Nur die
  beiden Polygonecken wandern, die Linie bleibt.
* Rahmen um (0, 0): «2 Ecken». V verschiebt beide, und sie teilen danach
  wieder einen Knoten.
* Auf K5 klicken: «Linie 1 · Anfang». z = 40 im schwebenden Fenster: Nur die
  Bewehrung rückt, die Wände bleiben.

## 2026-10-09 · Der Griff zwischen Eingaben und Berechnung ist zurück

Wunsch: Die Panels behalten ihre feste Breite, aber ein Griff stellt ein, wie
breit die mittlere und die rechte Tafel sind. In der mittleren stehen die
Panels dann in der Mitte.

* **Zwei Griffe:** Der linke verstellt den Baum, der rechte die Eingaben. Was
  eine der beiden gewinnt, gibt die Berechnung her.
* **Die Panels bleiben 420 px** und stehen in der Mitte der Tafel. Am
  2026-10-08 war der rechte Griff weggefallen, weil die Panels links standen:
  breiter gab nur leeren Platz am rechten Rand.
* **Die Zeichnung der Querschnittsanalyse füllt die Tafel aus,** sobald man
  am Griff gezogen hat. Bis dahin ist sie wie vorher halb so breit wie der
  Platz rechts vom Baum.
* **Grenzen:** Schmaler als ein Panel lässt sich die mittlere Tafel nicht
  ziehen, es würde abgeschnitten. Die Berechnung bleibt mindestens 280 px
  breit.
* **Die Breite gilt bis zum Neuladen,** wie beim linken Griff.

Nachgemessen bei 1600 px Fenster:
* Ohne Ziehen sind die Eingaben 476 px breit, wie vorher.
* 300 px nach rechts: 776 px. Die Panels stehen 150 px vom Rand, also in der
  Mitte.
* Ganz nach links: 476 px, nichts abgeschnitten. Ganz nach rechts: Die
  Berechnung hat noch 280 px.
* In der Analyse: Die Zeichnung ist 754 px breit, die übrigen Panels 420 px,
  in der Mitte.

## 2026-10-08 · Querschnittsanalyse: ein CAD aus Knoten, Linien und Flächen

Wunsch: das Koordinatenfenster als kleines schwebendes Fenster, ein CAD wie
Fagus oder AxisVM mit wenigen Knöpfen, allgemein genug für einen Grundriss.
Linien verbinden Knoten, eine Schubwand ist auch nur eine Linie, bearbeitet
wird über Auswahl und Menü statt durch Ziehen. Dieser Eintrag ist der
Umstieg (Schritt 5 des Plans); Vorlagen und das breitere Panel folgen.

### Im Kern: Knoten statt Koordinaten

Vorher trug jedes Element seine Punkte selbst. Wo Wand und Bewehrungslinie
zusammentreffen, standen dieselben Zahlen zweimal da -- wer eine Ecke
verschob, musste beide treffen.

Jetzt gibt es `knoten` mit Kennung und Lage, und die Elemente verweisen
darauf:

```
vorher:  schubwaende: [{von: [50, 50], bis: [250, 50], …}]
nachher: knoten:      [{kennung: "K5", y: 50, z: 50}, {kennung: "K6", …}]
         schubwaende: [{kennung: "L3", von: "K5", bis: "K6", …}]
```

* **Kennungen** (`F1`, `S1`, `L1`, `K1`) kommen nie wieder: die nächste ist
  die grösste plus eins. Die Linien zählen gemeinsam, weil eine Linie ihre
  Art wechseln kann und ihre Kennung dabei behält.
* **Namen in Berichten** bleiben, wie sie waren: «Polygon 1», «Wand 2», nur
  vom Kern vergeben. Neu nennt er auch die Hilfslinien; vorher hätte die
  Oberfläche sie selbst nummeriert.
* **Alte Projekte** werden beim Öffnen umgewandelt; gleiche Koordinaten
  werden ein Knoten. Die drei eingefrorenen Analysen geben dieselben
  Erfüllungsgrade, und alle drei Berichte sind Zeichen für Zeichen gleich.
* **Ein Verweis ins Leere** (ein Knoten, den es nicht gibt) wird eine
  Meldung am Element, wie ein Geometriefehler. Rechnen lässt sich so nicht;
  öffnen schon.
* **Gebaut wird mit dem Baukasten** (`u.polygon`, `u.stab`, `u.stablinie`,
  `u.schubwand`, `u.hilfslinie`). Er führt gleiche Knoten zusammen; `neu()`,
  das Beispiel und die Tests benutzen ihn.

### In der Oberfläche: ein allgemeines Fenster und ein Adapter

Die beiden alten Dateien (`zeichenfenster.js`, `koordinaten.js`, zusammen
rund 2300 Zeilen) sind weg. An ihrer Stelle:

* **`cad_*.js`, allgemein.** Sie kennen nur Knoten und Elemente in drei
  Formen -- Punkt, Linie, Fläche -- und wissen nichts von Beton. Ansicht,
  Modell, Punkteingabe, Befehle, Auswahl, schwebendes Fenster, Rahmen.
* **`qa_zeichnung.js`, der Adapter.** Er sagt, was die Formen im Querschnitt
  sind, wie sie aussehen und welche Eigenschaften sie haben.
* **`qa_uebersicht.js`, die Liste darunter.** Nur zum Lesen: Meldungen,
  Querschnittswerte in zwei Spalten, je Element eine Zeile. Ein Klick wählt.

So bedient es sich:
* **Oben nur Polygon P, Linie L, Knoten K,** dazu Rückgängig, Wiederholen,
  Alles zeigen F, Vollbild. Wählen ist der Grundzustand; Esc führt dorthin.
* **Jeder Punkt entsteht gleich:** Fang an Knoten, Mitten, Schnittpunkten und
  Raster; R setzt den Bezugspunkt; Ziffern gehen ins schwebende Fenster
  (relativ, absolut oder Länge und Winkel); Y/Z binden an eine Achse, P/S an
  eine Linie; M nimmt die Mitte zweier Punkte, auf die Bindung projiziert.
  Gelesen wird die Taste selbst, darum stimmen Y und Z auch auf der
  Schweizer Tastatur.
* **Neben der Auswahl** steht eine kleine Leiste: Verschieben V, Kopieren C,
  Löschen, und «Fläche bilden», wenn die gewählten Hilfslinien einen
  geschlossenen Umriss bilden. Von selbst wird keine Fläche daraus: die vier
  Wände des Unterzugs umschliessen eine Zelle, die kein Beton werden soll.
* **Ein Rahmen nach rechts** wählt, was ganz drin liegt, nach links auch, was
  er schneidet. Er nimmt auch Knoten mit: wer die zwei Knoten der rechten
  Kante wählt und um 100 verschiebt, macht den Balken 100 breiter.
* **Jede Aktion ist ein Schritt für Rückgängig,** nie ein Zwischenpunkt.
* **Bearbeiten neben der Auswahl** (Schritt 7):
  * *Teilen* halbiert eine Linie, *Knoten* fügt einen in eine Kante ein,
    wo man klickt.
  * *Umkehren* tauscht Anfang und Ende.
  * *Lösen* gibt der Auswahl eigene Knoten, wo sie einen mit anderem teilt:
    So verschiebt man die untere Bewehrung um 10 mm, ohne dass die Wände
    mitgehen.
  * Eine Bewehrung lässt sich **nicht teilen**: Bei zwei Hälften wären es
    andere Stäbe als beim Ganzen, also n Stäbe je Hälfte oder ein doppelter
    Stab in der Mitte. Beim Umkehren tauschen Start- und Endeisen mit, damit
    die Stäbe bleiben, wo sie sind.
* **Das Lot ⊥** (Schritt 6) fängt den Fusspunkt vom Bezugspunkt auf eine
  Linie, wenn er auf ihr liegt.
* **Vorlagen im Kern** (Schritt 8, `opencivil/querschnitt/vorlagen.py`):
  Rechteck, T-Balken, Hohlkasten, Kreis. T öffnet ein Fenster mit kleinen
  Bildern, den Massen als Felder und einer Skizze mit Masslinien, die sich
  beim Tippen ändert (Anfrage `vorlage`, unter Pyodide rund 1 ms).
  «Einsetzen» fragt nach dem Punkt für die Ecke unten links; Enter ohne
  Zahlen heisst Ursprung. Eingesetzt wird mit dem Baukasten des Kerns
  (`vorlage_einsetzen`), und die Vorlage kommt **dazu** -- vorher ersetzte
  sie die ganze Zeichnung. Wo sie genau auf einen Knoten trifft, hängt sie
  an ihm. `neu()` baut die frische Analyse aus dem Rechteck ohne Schubwand:
  dieselben Knoten, Linien und Zahlen wie vorher. Vorher stand das Rechteck
  zweimal da, in Python und in JS.
* **Verschmolzen wird nur, was bewegt wurde:** Landet ein verschobener Knoten
  genau auf einem anderen, wird er eins mit ihm. Zwei gelöste Knoten anderswo
  bleiben zwei.

Nachgespielt im Browser, mit Server und mit Pyodide:
* Stab 150 rechts von K3 (K, über K3, R, `150` Tab `0` Enter): Knoten genau
  bei (450, 600).
* Linie von K1, dann Y, M, K5, K8: Ende genau bei (150, 0).
* Linie von K1, P, die obere Bewehrung anklicken, über K8 klicken: Ende bei
  (250, 0), K8 auf die Parallele projiziert.
* Rahmen um die rechte Kante, V, `100` Tab `0`: der Balken ist 400 breit.
* Je Änderung genau eine Anfrage `geometrie`.

### Nebenbei

* **Der Baum las noch die alten Eckpunkte** und brach beim Start ab. Er
  misst jetzt die Ecken der Flächen über ihre Knoten.
* **Das Panel der Zeichnung wächst mit** (Schritt 9): Es ist etwa halb so
  breit wie der Platz rechts vom Baum und nie schmaler als 420 px. Bei
  1280 px Fenster sind das 448 px, bei 2560 px 1088 px; alle anderen Panels
  und die Zahlenfelder bleiben gleich. Die Höhe zieht man am Griff unter der
  Zeichnung, und der Browser merkt sie sich.
* **Statt der Palette weicht die Zeichnung aus:** «Alles zeigen» lässt die
  Ecke des schwebenden Fensters frei. Daneben oder darüber, je nachdem, was
  weniger Massstab kostet.
  * Geplant war, dass das Fenster dem Zeiger ausweicht. Ein Fenster, das vor
    der Maus flieht, lässt sich aber mit der Maus nicht mehr bedienen, und
    während eines Befehls stehen darin die Eigenschaften des Neuen.
* **Getippte Zahlen gingen verloren, wenn das schwebende Fenster zu war.**
  Die erste Ziffer klappt es jetzt auf.
* **Die Seite war 1800 statt 768 px hoch.** Der unsichtbare MathML-Teil jeder
  Formel ist bei KaTeX absolut gesetzt und lag ohne Bezug auf der Seite
  statt in der Tafel. Bekam ein Feld weit unten den Fokus, rollte die ganze
  Seite mit, samt Kopfleiste. `.katex { position: relative }` hält ihn in der
  Formel. Der Fehler ist älter als das CAD; aufgefallen ist er beim Testen.

## 2026-10-08 · Zahlenfelder: eine Breite für «99999.99»

Wunsch: Zahlenfelder nicht zu gross. Wenn «99999.99» ganz sichtbar ist,
ist das als Daumenregel genug gross.

Vorher hatte jede Zeile ihre eigene Breite:
* die Felder der Platte 112 px;
* die Lastfälle 80 px;
* die Lagen 64 px, die Bügel 56 px;
* die Koordinaten rund 137 px;
* die Lastfälle der Analyse 49 px — von «-1500» sah man die Hälfte.

Jetzt gibt es **eine** Grösse, `--zahlbreite = 8ch + Pfeile + Rand`, am
Rahmen um Feld und Pfeile. `ch` ist ein Zeichen der Schrift des Feldes. In
JetBrains Mono ist jede Ziffer und der Punkt genau eines, also passen acht
Zeichen genau hinein. Bei 14 px sind das 86 px, auf dem Telefon bei 16 px
und ohne Pfeile 80 px.

Was das in den Zeilen heisst:
* **Die Raster nehmen die Breite des Feldes** (`auto`) statt einer festen
  Zahl. Wo ein Kopf über den Spalten steht, nehmen sie `--zahlbreite`
  selbst; die Zeile steht dann in der Schrift der Felder, klein gesetzt sind
  erst die Beschriftungen. Sonst rechnete der Kopf in kleineren Zeichen und
  stünde schief.
* **Zahlen stehen überall rechtsbündig,** damit die Stellen untereinander
  stehen.
* **Die Lastfälle der Analyse** stehen in Zeilen zu drei Zahlen: N, M_y, M_z,
  darunter V_y, V_z, T.
* **Die Bügelzeile** hat drei Felder und den Umschalter. Oben steht der
  Durchmesser, darunter die beiden Teilungen.
* **Auf dem Telefon** steht der Umschalter «Teilung» unter den Feldern statt
  über den Rand hinaus.
* **Wo vier Felder in einer Karte stehen** (Knicken, Spannungsanalyse), werden
  sie etwas schmaler. Die Werte darin sind kurz.

Aufgeräumt nebenbei: Die einzeilige Form der Lastfälle für breite Tafeln ist
weg. Seit die Panels fest 420 px breit sind, kam sie nie mehr zum Zug.

Nachgeprüft im Browser:
* Jedes sichtbare Zahlenfeld der Platte, der Materialien, der Analyse und der
  Diagramme zeigt «99999.99» ganz, am Schreibtisch und auf dem Telefon.
* Keine Zeile ragt über ihre Karte hinaus.

---

## 2026-10-08 · Panels untereinander, fest breit, einklappbar

Wünsche, für alle Apps (Material, Platte, Querschnittsanalyse, Gleichungsblatt):
* Die Panels der Eingaben sollen nicht mehr mit dem Fenster breiter werden,
  sondern gerade so gross sein, dass alles sichtbar ist.
* Die Bewehrung steht nicht mehr neben der Platte. Alles steht untereinander,
  schlank und kompakt.
* Jedes Panel lässt sich einklappen.

**Eine Breite für alle Panels: 420 px** (`--panelbreite`). Streng nach dem
Inhalt wären die Panels verschieden breit geworden: beim Material rund 580 px
wegen der langen Beschreibungen, bei der Querschnittsanalyse über 900 px, weil
die Zeichenfläche keine natürliche Breite hat. Darum ist alles auf eine
schlanke Breite ausgelegt:
* Die Beschreibungen der Kennwerte brechen um, statt abgeschnitten zu werden.
* Die Lastfälle stehen in zwei Zeilen: der Name oben, die Zahlen darunter.
* Die mittlere Spalte ist so breit wie die Panels. Ein breiteres Fenster gibt
  der Berechnung rechts Platz, nicht den Eingaben.
* Auf dem Telefon werden die Panels schmaler, wo das Fenster nicht reicht.

```
Fenster 1280 px  vorher  Baum 300 · Eingaben 440 · Berechnung 530
                 jetzt   Baum 300 · Eingaben 476 · Berechnung 499
Fenster  800 px  vorher  Platte und Bewehrung nebeneinander, je rund 380 px
                 jetzt   untereinander, je 420 px, rechts davon frei
```

**Die Umbrüche richten sich nach dem Panel, nicht mehr nach der Tafel.**
Jedes Panel ist selbst der Bezug für die Container-Abfragen darin. Vorher war
das die Tafel: ein breiteres Fenster stellte die Lastfälle auf eine Zeile um,
und die Panels wurden breiter.

**Einklappen:** Ein Klick auf den Kopf eines Panels klappt es zu oder auf.
Der Browser merkt sich das je App und Panel, für alle Platten gleich und auch
über ein Neuladen hinweg. Pfeil und Titel sind ein Knopf, damit auch die
Tastatur ihn erreicht. Neu gezeichnet wird dafür nichts.

**Ein Griff weniger:** Der Griff zwischen Eingaben und Berechnung ist weg.
Breiter gäbe er nur leeren Platz, schmaler schnitte er die Panels ab. Der
Griff links verstellt nur noch den Baum; was der Baum gewinnt, gibt die
Berechnung her.

Nachgeprüft im Browser:
* **Alle vier Apps:** jedes Panel 420 px breit. Die mittlere Spalte bleibt
  beim Wechseln gleich breit, und nichts wird neu abgeschnitten.
* **Einklappen und Aufklappen,** auch nach dem Neuladen. Die Zeichenfläche
  zeichnet nach dem Aufklappen richtig, und das Vollbild deckt weiterhin das
  ganze Fenster.
* **Schmales Fenster (800 px):** die Panels untereinander, 420 px breit.
* **Telefon (375 px):** 351 px breit, nichts ragt hinaus.
* **Der Griff links:** Baum 300 → 250 px, Eingaben bleiben 476 px, Berechnung
  219 → 269 px.

---

## 2026-10-08 · Die ganze Seite in JetBrains Mono

Wunsch: Die Seite soll aussehen wie ein Code-Editor, mit gleich breiten
Zeichen. Die Gleichungen sollen trotzdem schön bleiben.

* **Die Schrift:** JetBrains Mono, mitgeliefert unter
  `web/vendor/jetbrains-mono/`, wie KaTeX und Pyodide. So sieht die Seite auch
  offline gleich aus. Es ist eine Datei mit 111 KB für alle Stärken. Von
  Google Fonts geladen, meldete jeder Aufruf die Adresse des Besuchers an
  Google.
* **Die Gleichungen bleiben, wie sie sind.** KaTeX und der Formeleditor setzen
  sie mit ihren eigenen Schriften.
* **Eine Zeile gegen die Breite:** Bei gleicher Schriftgrösse wäre der Text ein
  Fünftel breiter und wirkte grösser, denn die Mittellänge ist 0.55 statt 0.50
  der Schriftgrösse. `font-size-adjust: 0.5` gleicht die Mittellänge an die
  frühere Schrift an. Der Text wirkt so gross wie vorher und wird nur noch
  etwa ein Zehntel breiter. Die 127 einzelnen Schriftgrössen im Stilblatt
  bleiben unverändert. KaTeX und der Formeleditor sind davon ausgenommen,
  sonst erbten sie die Angleichung und würden grösser.

  ```
  «Biegung und Normalkraft», 14 px:
    frühere Schrift   160 px
    JetBrains Mono    193 px
    angeglichen       175 px
  ```

* **Was nicht mehr passte:** Der Name «Decke über EG» ragte 5 Pixel über sein
  Feld von 112 Pixeln hinaus. Ein Feld ohne Einheit bekommt jetzt deren Platz
  dazu.

Nachgeprüft:
* **Jede Ansicht**, mit alter und neuer Schrift verglichen, auf Text, der nicht
  mehr in seinen Kasten passt: Platte, Querschnittsanalyse, Materialien,
  Gleichungsblatt, alle Tafeln, «Gesamt», das Menü «Speichern» und der
  Bericht. Neu sind nur zwei Kleinigkeiten:
  - Eine Tabelle in der Herleitung der Querschnittsanalyse ist 4 Pixel zu
    breit und rollt darum seitlich. Breite Tabellen rollen dort schon heute.
  - In den Kennwerten des Betonstahls wird «ε_uk Dehnung bei Höchstlast»
    gekürzt. Der ganze Text steht im Hinweis beim Darüberfahren.
* **Die Zeichen:** JetBrains Mono hat die griechischen Buchstaben, ‰, ≤ ≥,
  ✓ ✗ und die meisten Pfeile. Es fehlen ⌀ und einige Werkzeugzeichen der
  Zeichenfläche. Die kommen aus einer Ersatzschrift des Systems, wie schon
  vorher.
* **Die Diagramme:** Keine Beschriftung überdeckt neu eine andere.

---

## 2026-10-06 · Spannung-Dehnung-Analyse: Zahlen am Bild, Sprung beim Riss

Wünsche:
* In den Bildern Dehnung und Spannung stehen die Zahlen: an jeder
  Stahllage und am Beton zuoberst und zuunterst.
* Die Momenten-Krümmungs-Linie springt beim Rissmoment waagrecht nach
  rechts.
* Das Rissmoment und M_Rd stehen an der Linie.

**Die Zahlen** stehen neben dem Punkt, auf der Seite ihres Vorzeichens.
Zwei Lagen wenige Millimeter übereinander, etwa 246 und 249 mm, kämen
aufeinander zu liegen. Darum rückt eine weg, und ein kurzer Strich zeigt,
wohin sie gehört. Damit neben dem grössten Wert Platz für seine Zahl bleibt,
reicht der Bereich jetzt 40 % über ihn hinaus statt 15 %; die Verläufe sind
etwas schmaler.

**Der Sprung.** Die alte Linie war kein Rechenfehler, sondern ein anderes
Modell. Sie mischte Zustand I und II mit Zugversteifung:
`χ = (1 − ζ)·χ_I + ζ·χ_II` mit `ζ = 1 − (M_Riss/M)²`. Beim Rissmoment ist
ζ = 0, darum lief sie dort ohne Sprung weiter. Der Querschnitt selbst
springt aber: beim selben Moment von χ_I auf χ_II. Jetzt zeigt die Linie den
Querschnitt – ungerissen bis M_Riss, beim Rissmoment zwei Punkte, darüber
gerissen. Am Beispiel, Decke über EG, x-Richtung, N = 0:

```
vorher   M = 41.4 kNm   χ = 0.00134 1/m, danach ohne Knick weiter
nachher  M = 41.4 kNm   χ = 0.00134 → 0.00263 1/m, knapp das Doppelte
```

Die Zugversteifung ist damit draussen. Ihr Beiwert war ohnehin offen; ob
und mit welcher Regel eine Linie des Bauteils dazukommt, steht jetzt so in
TODO.md.

**Dabei gefunden: das Rissmoment hing nicht an N.** Die Linie nahm immer das
Rissmoment ohne Normalkraft, auch mit Druck. Jetzt gilt
`M_Riss(N) = M_Riss(0) − N·h/6`, am Bruttoquerschnitt wie beim spröden
Versagen (Annahme, in TODO.md).

```
N = −200 kN   vorher M_Riss = 41.4 kNm   nachher 51.4 kNm
```

Ein Test prüft das an der Bedeutung, nicht an der Formel. Beim Rissmoment
steht der gezogene Rand des ungerissenen Querschnitts bei jeder Normalkraft
fast gleich: 2.14 N/mm² bei N = 0, 2.17 bei 200 kN Druck. Mit dem alten
Rissmoment wären es bei 200 kN Druck 1.65 gewesen.

Zwei Randfälle sagen, was sie sind:
* Liegt das Rissmoment über M_Rd, bleibt die Linie bis M_Rd ungerissen.
* Reisst schon die Zugkraft den Querschnitt, ist sie ganz gerissen.

Nachgeprüft:
* **Tests:** unter M_Riss ungerissen, darüber gerissen, zwei Punkte beim
  Rissmoment; Moment und Krümmung fallen nirgends zurück; das Rissmoment
  mit N; die beiden Randfälle. Die Schnappschüsse sind unverändert, denn die
  Analyse steht in keinem Bericht.
* **Im Browser:** Zahlen an allen Lagen, der Sprung sichtbar, Marken an
  M_Riss und M_Rd.

---

## 2026-10-02 · Nur noch ein Interaktionsdiagramm

Wunsch: es soll nur ein Interaktionsdiagramm sichtbar sein.

Vorher standen bei einer Analyse drei Bilder derselben Art:
- das Interaktionsdiagramm mit wählbaren Achsen;
- je Lastfall die M-N-Linie in seiner Ebene;
- je Lastfall die M_y-M_z-Kurve bei N_Ed.

Die beiden je Lastfall sind weg. Was nur sie zeigten -- wo der Nachweis
seinen Widerstand misst --, steht jetzt im einen Diagramm:
* **Der Widerstand reist mit.** Jeder Lastfall bringt den Bruchzustand
  seines Nachweises mit, mit N, M_y und M_z. Liegen Einwirkung und
  Widerstand beide in der gewählten Ebene, führt ein gestrichelter Weg vom
  einen zum anderen. Am Unterzug, M_y über N bei M_z = 0: von «Feld»
  (150 kNm) waagrecht zu 211.8 kNm auf der Linie.
* **Ein Klick legt den Schnitt durch einen Lastfall.** Bei einem schiefen
  Fall misst der Nachweis bei N_Ed; ein Klick in der Ansicht M_y über M_z
  setzt N auf sein N_Ed, und der Weg erscheint. Kein Abtippen von Werten
  mit Längszugkraft.

Bruchzustand und Schubfluss sind keine Interaktionsdiagramme und bleiben.

Nachgeprüft:
* **Tests:** Der Widerstand liegt auf dem Diagramm. Bei N = N_Ed ergibt der
  Schnitt rundum dasselbe M_y wie der Nachweis. Je Lastfall gibt es keine
  eigene Linie mehr.
* **Im Browser:** Weg sichtbar; ein Klick auf einen blassen Fall legt den
  Schnitt durch ihn.

---

## 2026-10-02 · Interaktionsdiagramm mit wählbaren Achsen

Wunsch: ein M-N-Interaktionsdiagramm auch für die Querschnittsanalyse, mit
wählbaren Achsen. Auf x und y steht je eine von N, M_y und M_z; die dritte
bekommt ihren Wert in einem Zahlenfeld.

### Vorher und nachher

| | vorher | nachher |
| --- | --- | --- |
| Interaktionsdiagramm | je Lastfall nur die Linie in seiner Ebene | eines je Analyse, Achsen frei wählbar |
| Lastfälle im Bild | nur der eine Fall | alle; die in der Ebene kräftig, die übrigen blass |
| Linie bei starker Druckkraft | eine gerade Sehne über ein Drittel der N-Spanne | durchgehend glatt, höchstens 0.14 % neben der genauen Suche |

Beispiel am Unterzug:
- x = M_y, y = N, M_z = 0: die bekannte M-N-Linie, «Feld» liegt darin, grün.
- x = M_y, y = M_z, N = 0: der Umriss bei N = 0.
- Mit x = M_z und M_y = 150 kNm steht «Feld» ebenfalls kräftig da, weil sein
  M_y genau 150 ist.

### Wie es gebaut ist

* **Ein Schnitt durch die Fläche aller Bruchzustände**
  (`Querschnitt.schnitt` in `opencivil/querschnitt/interaktion.py`). Im
  Raum (N, M_y, M_z) bilden alle Bruchzustände eine geschlossene Fläche;
  jeder Fächer ist eine Linie darauf.
  * Bei festem N: je Neigung der Punkt mit diesem N, mit derselben Suche wie
    im Nachweis.
  * Bei festem Moment: die Fächer von 72 Neigungen, je auf 120 Stufen in N
    gelesen. Auf jeder Stufe schneidet die Gerade des festen Moments den
    Umriss in zwei Punkten. Gegen einen genauen Umriss aus 360 Neigungen
    liegt das höchstens 0.4 % daneben.
* **Die Fläche wird einmal je Querschnitt gerechnet** und bleibt an ihm.
  Weil der Kern den Querschnitt nach einer Rechnung im Zwischenspeicher
  hält, kostet erst der erste Schnitt etwas.
  * Pyodide: 579 ms für den ersten Schnitt, danach 26–67 ms je Wert.
* **Die Oberfläche wählt nur.** Die Punkte kommen mit allen drei Grössen; die
  Oberfläche legt zwei davon auf die Achsen. Zwei Momente bekommen denselben
  Massstab. Wird auf einer Achse gewählt, was schon auf der anderen steht,
  tauschen die beiden.
* **Einachsig** gibt es nur M_y über N, wie im Nachweis: die Nulllinie bleibt
  waagrecht, M_z zählt nicht.

### Nebenbei, ausserhalb des Wunsches

* **Der Fächer hatte eine Sehne.** Seine Stützstellen lagen gleichmässig in
  der Krümmung. Wo die Nulllinie den Rand erreicht, sprang N zwischen zwei
  Stellen von −1762 auf −3267 kN, und die M-N-Linie war dort gerade. Jetzt
  wird halbiert, bis die Mitte zweier Stützstellen auf ihrer Sehne liegt. Die
  Nachweise waren nicht betroffen: sie suchen genau.
* **Der Spannungsblock traf N_Ed nicht** (eigener Commit davor). Er springt
  bei 0.15·ε_c2d von null auf f_cd; in der Fasermitte gelesen, sprang N mit.
  Beim Kastenträger stand in der Probe 638.7 kN statt 664.0 kN. Jetzt wird
  über die Faser gemittelt. Feld ging von 0.64 auf 0.62; Parabel-Rechteck,
  Stahl und Platte rechnen wie vorher.

### Nachgeprüft

* **Tests:** 796. Neu sind der Schnitt gegen die genaue Suche (bei festem N
  gleich, bei M_z = 0 und M_z = 40 kNm auf 0.3 bzw. 0.5 %), der Fächer ohne
  Sehne, die Wahl in der Anfrage und der Spannungsblock: jede Normalkraft
  wird getroffen. Ohne die Behebung verfehlt N bis 22 kN.
* **Im Browser:** Achsen gewechselt und getauscht, Werte getippt, kräftig und
  blass geprüft, einachsig und zurück; mit Server und mit Pyodide.

---

## 2026-10-02 · Querschnittsanalyse: gezeichnete Querschnitte

Wunsch: unter den Stahlbeton-Platten eine zweite «App». Statt ein paar Masse
einzugeben, zeichnet man den Querschnitt: Polygone mit Material, Bewehrung als
Einzelstäbe oder Linien wie bei Fagus, Schubwände mit Bügeln. Nachgewiesen
wird wie bei der Platte, aber in beide Richtungen: N, M_y und M_z gleichzeitig,
dazu V_y, V_z und Torsion. Wahlweise nur einachsig.

### Vorher und nachher

| | Platte | Querschnittsanalyse |
| --- | --- | --- |
| Eingabe | h, b, vier Lagen | gezeichnet: Polygone, Aussparungen, Stäbe, Linien, Wände |
| Biegung | M um y, Handrechnung gegen das Polygon | N, M_y, M_z zusammen, Nulllinie schräg, gegen den Dehnungsfächer |
| Querkraft | je Laufmeter, eine Bügelschar | auf die Wände verteilt, mit Torsion und Zellen |
| Werte | Bemessung | je Material Bemessung oder charakteristisch, Beton Parabel-Rechteck oder Block 0.85·x |

Beispiel: der Unterzug im Beispielprojekt, 300 × 600 mm, vier Schubwände auf
der Bügelachse. Für M_y = 150 kNm, V_z = 150 kN und T = 15 kNm steht in der
Zusammenfassung Biegung 1.41 (M_Rd = 211.8 kNm) und Querkraft mit Torsion
1.75. Die rechte Wand trägt 150 kN/m aus der Querkraft und 75 kN/m aus der
Torsion, zusammen 225 kN/m gegen v_Rd = 394.3 kN/m.

### Wie es gebaut ist

* **Fünf neue Teile im Kern** unter `opencivil/querschnitt/`:
  * `geometrie` -- Polygone (Fläche, Schwerpunkt, Trägheit nach Gauss),
    Verschachtelung (ein Polygon in einem anderen ersetzt es dort), Stablinien,
    Prüfungen.
  * `fasern` -- Fasern und Dehnungsgrenzen. Der Löser der Platte rechnet jetzt
    darüber; ihr Bericht ist Zeichen für Zeichen gleich geblieben.
  * `interaktion` -- die zulässigen Dehnungsebenen als konvexes Vieleck. Sein
    Rand ist der Dehnungsfächer, für jede Form ohne Sonderfälle. Je Neigung ψ
    wird N = N_Ed gesucht, und ψ so, dass das Moment in Richtung der
    Einwirkung zeigt.
  * `schubwaende` -- Federn b_w·l für die Querkraft, das Versatzmoment, die
    Zellen als Flächen des Wandgraphen, Bredt mehrzellig, Fachwerk je Wand,
    die Längszugkraft.
  * `analyse` -- das Bauteil: die Zeichnung mit allen Meldungen, die Werte,
    die Werkstoffwahl.
* **Vier Nachweise:** `schiefe_biegung`, `schubwandnachweis` und in
  `richtungsnachweise` Duktilität und sprödes Versagen je Richtung.
* **Aufbau je Bauteil statt je Platte.** Zwischenspeicher, Zusammenfassung und
  Bericht gehen über `Aufbau.bauteile()`: erst die Platten, dann die Analysen.
* **Die Oberfläche** (`web/js/`):
  * `zeichenfenster.js` -- das Zeichenfenster. Es entsteht einmal je Analyse
    und übersteht jeden Neubau der Tafel; ein halb gezeichnetes Polygon, der
    Massstab und der Verlauf für «Rückgängig» bleiben, wenn nebenher eine
    Rechnung fertig wird.
  * `koordinaten.js` -- das Koordinatenfenster, absolut oder relativ.
  * `querschnittsanalyse.js` -- die übrige Eingabe.
  * `qa_diagramme.js` -- die Diagramme.
* **Was gezeichnet wird, entscheidet der Kern.** Die Anfrage `geometrie`
  liefert in ein paar Millisekunden die Stäbe der Linien mit tatsächlicher
  Teilung, den Schwerpunkt, die Zellen und jede Meldung am Element. Die
  Oberfläche rechnet nur Eingabehilfen: Raster, Fang, Zoom, Masslinien.
* **Diagramme auf Nachfrage.** Die M_y-M_z-Kurven brauchen siebzig
  Bruchzustände, die kein Nachweis braucht. Sie kommen aus einer eigenen
  Anfrage (`analysediagramme`), erst wenn der Reiter offen ist und die
  Rechnung durch ist.

### Nebenbei, ausserhalb des Wunsches

* **Die rechte Tafel sagt, wenn die letzte Eingabe nicht rechnet.** Vorher
  blieb das Ergebnis von davor kommentarlos stehen; beim Zeichnen kommt eine
  unfertige Eingabe oft vor.
* **Werte in den Werkstofftabellen mit Einheit:** «ε_c1d = 2 ‰» statt «2».
* **Zellen im Fenster in Metern gesucht**, wie im Nachweis. In Millimetern
  hätte dieselbe Toleranz etwas anderes bedeutet, und ein Wandende 0.4 µm neben
  der Ecke hätte im Bild keine Zelle gezeigt, im Nachweis aber eine.

### Annahmen, nicht nachgeschlagen

Stehen im Code als «nach Vorgabe, nicht nachgeschlagen» und in
[[TODO]]: die C-Punkt-Regel bei beliebiger Form, das Federmodell
b_w·l mit Bredt, die Längszugkraft in der Wandmitte, k_t aus der Höhe in
Biegerichtung, x/d senkrecht zur Nulllinie, die Normstelle des
Spannungsblocks.

### Nachgeprüft

* **Tests:** 784, darunter die Fächer der Analyse gegen den der Platte (zwei
  unabhängige Wege), Bredt am Kasten, zwei Zellen mit Mittelwand, das
  Gleichgewicht der Wandflüsse und die Diagramme gegen die Nachweise.
* **Schnappschüsse:** nach Durchsicht übernommen. Im Beispiel kommt der
  Unterzug dazu, im vollen Bericht nur die Einheiten.
* **Im eingebauten Browser**, mit Server und mit Pyodide:
  * gezeichnet, verschoben, rückgängig gemacht;
  * Koordinaten absolut und relativ getippt;
  * Stab ausserhalb mit Meldung;
  * Vorlage Hohlkasten mit Zelle;
  * einachsig und schief, Längszugkraft;
  * Vollbild und Telefonbreite ohne waagrechtes Rollen.
* **Rechenzeit in Pyodide:** eine Analyse mit vier Lastfällen braucht
  84–177 ms, mit allen Nachweisen 110 ms, ihre Diagramme 317 ms. Ziel war
  unter einer Sekunde.

---

## 2026-10-02 · Nachtrag zum Umbau: der Zeilenname ohne Rückfall

Der letzte Rest aus Schritt 9 des Umbaus. Eine Zeile der Zusammenfassung
hiess bisher «Langname, sonst Kürzel, sonst Name»
(`Zeile.aus` in `opencivil/bericht/zusammenfassung.py`). Jetzt heisst sie nur
noch nach dem Langnamen.

Die Rückfälle kamen nie zum Zug. Am Beispiel und am Projekt mit jedem
Nachweis hatten alle 33 Urteile einen Langnamen; `Nachweis.rechne` stempelt
ihn auf, aus `LANGNAME` oder dem Thema. Der Bericht bleibt Zeichen für
Zeichen gleich.

Ohne Rückfall stünde ein künftiger Nachweis ohne beides mit leerer Zeile da.
Das meldet jetzt `TestJedesUrteilHatEinenLangnamen`. Gegenprobe: ohne
Langnamen schlägt er an.

Das Kürzel `art` am Urteil bleibt, wie beim Umbau entschieden: es ist der
feste Schlüssel, nach dem die Tests filtern.

---

## 2026-09-26 · Versionsmarken auch für JavaScript und CSS

Wunsch: Nach einer Änderung soll der Browser nie mehr alte und neue Teile der
Oberfläche mischen.

### Vorher und nachher

Die `.py`-Dateien des Kerns hatten schon Marken (`…py?v=Marke`). Die Module
der Oberfläche, das Stilblatt und die beiden Verzeichnisse unter `web/kern/`
nicht. Ein Server ohne Cache-Angabe lässt den Browser selbst schätzen, wie
lange er eine Datei behält. So lief beim Prüfen einmal ein altes
`nachweise.js` mit dem neuen Kern. Neu laden half nicht sicher: Chrome prüft
dabei nur die Seite selbst beim Server nach. Die eingebundenen Dateien nimmt
es weiter aus dem Speicher.

| | vorher | nachher |
| --- | --- | --- |
| Modul geändert, Seite neu geladen | das Modul kann alt bleiben | neue Marke, neue Adresse: sicher neu |
| Stilblatt | ohne Marke | mit Marke |
| `dateien.json`, `formelsammlung.json` | ohne Marke | mit Marke |

Im eingebauten Browser nachgespielt: `nachweise.js` probehalber geändert, die
Brücke laufen lassen, neu geladen. Geholt wurde `nachweise.js?v=a1c47523be1e`
statt `?v=44617ce23c2b`, mit dem neuen Inhalt.

### Wie es gebaut ist

* **Eine Importtafel in `web/index.html`.** `python3 -m opencivil.web.bruecke`
  schreibt sie zwischen zwei Kommentare: je Modul unter `web/js/` und je
  Verzeichnis unter `web/kern/` die Adresse mit Marke, dazu das Stilblatt mit
  Marke. Die Module selbst bleiben, wie sie sind: `import './dom.js'` führt
  über die Tafel auf `./dom.js?v=Marke`.
* **`app.js` wird im Seitenkopf eingebunden statt mit `src` geladen.** Ein
  `src`-Attribut liest die Tafel nicht.
* **Formelsammlung und Faden holen ihre Adressen mit `import.meta.resolve`**,
  also ebenfalls über die Tafel.
* **Im Faden gilt die Tafel nicht.** Darum schickt `kern.js` ihm als erste
  Nachricht die Adresse des Kernverzeichnisses, samt Marke. Der Faden bindet
  keine eigenen Module ein; die kämen ohne Marke.
* **Ein Test meldet, wenn die Brücke vergessen ging**
  (`test_versionsmarken_sind_auf_dem_stand`), wie schon beim Kern. Sie muss
  jetzt auch nach jeder Änderung unter `web/js/` oder `web/css/` laufen.

### Was bleibt

* **Die Seite selbst** kann noch aus dem Speicher kommen, auf GitHub Pages
  bis zu zehn Minuten. Dann ist aber alles gleich alt, und Neuladen holt alles
  neu. Beim Prüfen kam genau das vor: der eingebaute Browser nahm beim
  Navigieren die alte Seite, erst Neuladen brachte die neue.
* **Die Fremdbibliotheken** unter `web/vendor/` (KaTeX, MathLive, Pyodide)
  bleiben ohne Marke. Sie ändern sich nur, wenn jemand bewusst eine neue
  Fassung einlegt.

### Nachgeprüft

666 Tests. In einem frischen Chrome, ohne Server (Pyodide) und mit Server:
alle eigenen Dateien kommen mit Marke, der Kern läuft, die Formelsammlung
lädt, die Konsole bleibt ohne Fehler. Das Protokoll des statischen Servers
zeigt `dateien.json?v=3288a407ae8a`, geholt vom Faden.

---

## 2026-09-26 · Umbau nach dem strengen Review: jede Regel an einer Stelle

Anlass: ein Review, das nicht nach Fehlern fragt, sondern nach Form. Es fand
zwei Blocker und einen echten Fehler. Umgesetzt in neun Schritten, jeder für
sich getestet und gepusht. Die Hauptprobe war jedes Mal dieselbe: **Der
Bericht bleibt Zeichen für Zeichen gleich**, und die Suche findet in 65
Vergleichsfällen dieselben Lagen und Dicken. Gerechnet wurden das Beispiel,
«y wie x», eine dünne y-Lage und jeder Nachweis, in allen Modi, mit
Mindestdurchmesser 0, 10 und 16.

### Der Fehler

`bewehrung_suchen` las Einstellungen als `rumpf.get(...) or eintrag...`. Das
`or` hält eine 0 für «nicht angegeben». Ein Mindestdurchmesser 0, also «kein
Minimum», wurde darum still zur Vorgabe der Platte. Jetzt kommen die
Einstellungen nur von der Platte. Die Oberfläche hatte die Übersteuerungen
ohnehin nie benutzt.

### Vorher und nachher

| | vorher | nachher |
| --- | --- | --- |
| `bewehrungssuche` | eine Datei, 1009 Zeilen | Paket aus 4 Teilen, das grösste 554 Zeilen |
| Ergebnis der Suche | Wörterbuch aus Marken (`'2g'`, `'3z'`) | die Lagen selbst |
| Regeln für die y-Lagen | an 3 Stellen, dazu eine Liste «gehoben» | eine Funktion `_y_ableiten` |
| Start der Grundbewehrung | Index `grund_ab` durch 4 Funktionen | eine Stufenliste je Art (`Stufen`) |
| «Plattendicke optimieren» | 2 von 5 Modi, zwei Eigenschaften trennten sie wieder | eigener Schalter `automatik_dicke` |
| eine Vorgabe wie `h = 300` | im Feld, im Leser und in der Oberfläche | nur im Feld |
| `?? Zahl` in der Oberfläche | 30 Stellen | 1 (der Haken beim Materialwert) |
| Durchmesserliste | im Kern und in der Oberfläche, schon verschieden (⌀6) | nur im Kern, über den Katalog |
| Kopplung der Lagenpaare in JS | dreifach | ein Modul `lagen.js` |
| Urteilsnamen | 9 eigene f-Strings, jeder anders | gestempelt aus Langname, Richtung, Fall |

Unterm Strich ist der Code gleich lang (+1337/−1333 Zeilen), denn die neuen
Module haben Kopfkommentare bekommen. Kürzer geworden ist die Logik: rund
fünfzehn Begriffe fallen weg, von `_vollstaendig` bis `buegelVon`.

### Was sich für dich ändert

* **Ein geleertes Zahlenfeld behält seinen Wert.** Vorher sprang «h» auf 300,
  eine Zahl, die die Oberfläche selbst kannte. Nur wo leer etwas heisst,
  sagt das Feld es: «keins» bei Durchmesser, Lasten, Einlagenhöhe und
  Mindestdurchmesser, «zurück zum Normwert» beim Materialkennwert
  (`zahlfeld({leer})`).
* **«Plattendicke optimieren» ist ein Schalter** unter der Moduswahl. Alte
  Dateien mit den Dickenmodi lesen sich richtig.
* **Die Suche leert die Lagen nicht mehr.** Das Leeren sollte zeigen, dass
  etwas passiert. Dafür musste die Oberfläche wissen, welche Posten der
  Kern sucht, und die Anhebung der y-Lagen kam dort nie an. Jetzt zeigt es
  der Laufbalken, und danach meldet die Suche ihr Ergebnis.
* **⌀6 bieten die Pfeile nicht mehr an.** Eintippen geht weiter; die Suche
  kannte ihn nie.
* **Die gemeldete Stahlfläche zählt alle Lagen,** auch die unberührten
  y-Lagen (Beispiel 3079 statt 1571 mm²). Welche Teilung gewinnt, ändert
  sich dadurch nicht.
* **Formelsammlung:** Der Schalter «Aktuelle Seite | Gesamt» war dort noch
  ausgeblendet («zeigt immer alles»). Seit sie je Bestandteil filtert, kam
  man so nicht mehr zu «Gesamt». Er steht jetzt wieder da. Das war ein
  Fehler aus dem vorigen Auftrag.

### Bewusst stehen gelassen

* **Das Kürzel `art` der Urteile.** Das Review nannte es einen blossen
  Rückfall. Es ist aber der feste Schlüssel der Nachweisart, an dem Tests
  filtern. Ein Anzeigename ändert sich, wie die Umbenennung zu «Risse: …»
  gezeigt hat.
* **Ein Wächter statt eines generischen Lesers:** Die Leser bleiben von Hand
  geschrieben, weil darin Altformate und Prüfungen stehen. Neu nehmen sie
  ihre Vorgaben aber von der Klasse (`cls.h`, `vorgabe(cls, feld)`), und ein
  Test prüft je Eintragsklasse, dass ein Wörterbuch mit nur den
  Pflichtfeldern genau die Vorgaben ergibt.

### Offen, nicht gewählt

`stil.css` (über 1200 Zeilen) und `querkraft.py` (über 1100) aufteilen, die
Querschnittszeichnung zerlegen, die acht `automatik_`-Felder als eigene
Gruppe, `masse_pruefen` richtig benennen, `rechnetImBrowser` ohne Aufrufer.

---

## 2026-09-26 · Orange und Gelb, Bügel im Querschnitt, Formeln je Bestandteil

Wunsch: neue Farben für die Richtungen und die Ja/Nein-Schalter, die Bügel
im Querschnittsbild, die Formelsammlung je Bestandteil, die Stahlwahl nur an
den x-Lagen.

### Farben

| | vorher | nachher |
| --- | --- | --- |
| x-Lagen | saftgrün | kräftig orange |
| y-Lagen | hellrot | kräftig gelb, auf Weiss noch sichtbar |
| Bügel und «beide» | sanftes Violett | leuchtendes Violett |
| Ja/Nein-Schalter | weiches Grün und Rot | das Grün und Rot, das vorher x und y trugen |

* **Gelb trägt keine Schrift.** Auf dem gelben Schalter steht dunkle Schrift,
  und die Beschriftungen im Querschnittsbild stehen in der tiefen Fassung
  der Farbe.
* **«ungünstig | günstig» ist jetzt blau.** Er war gold, damit man ihn nicht
  mit x|y verwechselt, als x noch blau war. Neben dem Gelb der y-Lagen wäre
  Gold genau diese Verwechslung.

### Bügel im Querschnittsbild

* **Senkrechte violette Striche** in Stabdicke, von der Unterkante der 1.
  bis zur Oberkante der 4. Lage.
* **Abstand wie die Teilung in y** (oder die Anzahl über die Breite). Die
  Werte kommen aus der Lösung (`querkraft.s_y`, `querkraft.n_y`). Der
  Schnitt läuft in y, darum zählt diese Teilung.
* **Kein Strich schneidet einen x-Stab.** Die Reihe wird als Ganzes
  verschoben wie eine Zulage (`besterVersatz`), damit die Teilung ablesbar
  bleibt. Trifft danach noch ein Strich, rückt er allein neben den Stab.
  Beispiel ⌀10@200: fünf Striche im Abstand 200 mm, keiner berührt einen
  Kreis. Ein erster Versuch rückte jeden Strich einzeln; die Abstände wurden
  dabei ungleich (116, 216, 191, 193 mm).

### Formelsammlung je Bestandteil

* Beton gewählt: nur «Beton». Betonstahl: nur «Betonstahl». Platte: ihre
  zehn Themen. «Gesamt»: alle zwölf.
* **Zu welchem Bestandteil ein Thema gehört, sagt der Kern** (`Thema.art`):
  der Namensraum des Abschnitts, unter dem es zum ersten Mal steht, etwa
  `beton.b1`.

### Stahl nur an den x-Lagen

* An einer y-Lage steht keine Stahlwahl mehr. Die Wahl an der x-Lage gilt für
  beide Lagen dieser Seite. So kann eine verborgene y-Wahl nicht unbemerkt
  vom Rest abweichen.

---

## 2026-09-26 · Schalter an jeder Lage, eine eigene Grenze x/d

Wunsch: x|y-Schalter auch an der 2. und 3. Lage, ein Feld «Max. x/d» beim
Duktilitätsnachweis, «Rissmoment» beim spröden Versagen.

* **Jede Lage hat ihren x|y-Schalter.** Gespeichert bleibt die Richtung der
  äusseren Lage (1 und 4). Wer an der inneren schaltet, stellt die äussere
  auf das Gegenteil. Beispiel: 2. Lage auf y → 1. Lage wird x.
* **Max. x/d je Platte** (`QuerschnittEintrag.x_d_max`): Vorgabe 0.35,
  höchstens 0.5. Die Zahlen stehen beim Nachweis (`duktilitaet.GRENZE`,
  `HOECHSTENS`), die Oberfläche holt den Höchstwert über den Katalog.
  - Ausserhalb von (0, 0.5] meldet der Kern beim Bauen: «max. x/d muss
    grösser als null und höchstens 0.5 sein». Geprüft wird nicht beim
    Öffnen, damit sich eine abgelegte Platte korrigieren lässt.
  - Weicht die Grenze von 0.35 ab, sagt es die Herleitung: «Grenze
    eingegeben: (x/d)_max = 0.45 statt der Vorgabe 0.35.» Eine andere
    Grenze ist eine Annahme, die man im Bericht finden muss.
  - Beispiel: ⌀26@150 + ⌀10@150 unten gibt x/d = 0.43. Bei 0.35 nicht
    erfüllt, bei 0.5 erfüllt.
* **Sprödes Versagen:** Die Zeile heisst «Rissmoment». «Ungünstigere
  x-Lage» steht jetzt im Tooltip der x-Marke.
* **Nebenbei:** Die Pfeile an Feldern mit Kommaschritt runden auf die
  Stellen des Schritts. Vorher gab 0.35 − 0.05 im Feld 0.30000000000000004;
  das betraf auch k_c und die Kriechzahl.

---

## 2026-09-26 · Der Mindestdurchmesser gilt für jede Lage

Wunsch: Ist bei der automatischen Bewehrung ein Mindestdurchmesser gegeben,
bekommt jede Lage mindestens ihn als Grundbewehrung.

### Vorher und nachher

Am Beispiel, Mindestdurchmesser ⌀10, Teilung 150:

| Modus | vorher | nachher |
| --- | --- | --- |
| Grundbew. ohne Kräfte, Zulage mit Kräften | 2. Lage nur Zulage ⌀14, 3. Lage nur Zulage ⌀10 | 2. Lage ⌀10 + Zulage ⌀10, 3. Lage ⌀10 |
| Grundbew. ohne Kräfte | beide x-Lagen leer | beide x-Lagen ⌀10 |
| Grundbew. mit Kräften | ⌀14 und ⌀10 | unverändert |

Vorher galt der Mindestdurchmesser nur für Stäbe, die die Suche überhaupt
einbaute. Eine Lage, die kein Nachweis verlangte, blieb leer. Im Modus
«ohne Kräfte» war das bei einer Platte ohne Zwängung jede x-Lage.

### Wie es gebaut ist

* **x-Lagen:** Die Grundbewehrung beginnt in der Suche beim
  Mindestdurchmesser statt bei null. Beim Zurücknehmen geht sie nicht unter
  ihn. Die Zulage beginnt weiter bei null und darf fehlen.
* **y-Lagen:** Folgt y der x-Grundbewehrung, hat sie ihn damit schon. Sonst
  hebt die Suche eine y-Lage, die dünner ist oder leer, auf den
  Mindestdurchmesser mit der gesuchten Teilung (`_y_mindestens`). Eine
  dickere y-Lage bleibt, wie sie ist. Gehoben wird vor dem Suchen, denn
  liegt y aussen, kostet ihr Durchmesser x die statische Höhe.
* **Leer heisst: kein Mindestdurchmesser.** Dann darf eine Lage leer
  bleiben, wie bisher. Das Feld zeigt die Null als leer, und seine Pfeile
  gehen durch die Durchmesser statt in 2-mm-Schritten.
* **Obergrenze:** Liegt schon die Grundbewehrung mit Mindestdurchmesser
  darüber, sagt die Suche das, statt erfolglos zu suchen.

---

## 2026-09-26 · «Risse: …», Farben für die Tragrichtungen, kürzere Lastfallzeilen

Wunsch: andere Namen in der Zusammenfassung, dunklere Ränder, neue Farben
für x und y, Überdeckung und Platte als Karten, Lastfallzeilen nicht über
die ganze Breite.

### Namen in der Zusammenfassung

| vorher | nachher |
| --- | --- |
| Stahlspannung aus Rissbreite | Risse: Quasi-ständige Lastfälle |
| Stahlspannung gegen Fliessen | Risse: Häufige Lastfälle |
| Zwängung auf Biegung | Risse: Zwängung Biegung |
| Zwängung auf Normalkraft | Risse: Zwängung Normalkraft |

* **Nur in der Zusammenfassung** und in den Hinweisen darunter, in der
  Oberfläche wie im Bericht. Formelsammlung, Herleitung und die Schalter der
  Eingabe heissen weiter wie bisher.
* **Dafür hat jeder Nachweis einen eigenen Namen für die Zusammenfassung**
  (`Nachweis.LANGNAME`, leer: sein Thema). Vorher war der Name das Thema
  der Formelsammlung. Beide ordnen aber anders: die Formelsammlung nach dem,
  was gerechnet wird, die Zusammenfassung nach der Frage, die beantwortet
  wird.
* «Quasi-ständige» mit kleinem s nach dem Bindestrich, wie sonst überall in
  der Oberfläche.

### Farben

* **x saftgrün, y hellrot, Bügel violett** (wie «beide»). Vorher war x blau
  und y kupfer. Kupfer ist aber auch die Farbe des Betonstahls. Jetzt trägt
  jede Farbe nur eine Bedeutung.
* **Heller und gelblicher als Grün und Rot der Urteile.** Eine y-Lage soll
  nicht wie ein verfehlter Nachweis aussehen.
* **Einmal festgelegt**, in `stil.css`. Das Querschnittsbild liest sie dort
  (`stilfarbe`); vorher stand das Blau der x-Lagen ein zweites Mal im
  JavaScript.

### Ränder und Karten

* **Eingaberand dunkler:** Zahlen- und Namensfelder, Auswahllisten,
  Textkasten, Formelfelder und Schalter haben einen gemeinsamen Rand
  (`--eingabe-rand`). Der Kontrast zu Weiss steigt von 1.7 auf 3.1; die
  Richtlinie für barrierefreie Bedienelemente (WCAG) verlangt 3.
* **Überdeckung:** eine weisse Karte mit blauer Kante wie die Lagen. Vorher
  war sie grau und gestrichelt und ging zwischen den Lagen unter.
* **Platte:** Die Angaben stehen in einer Karte mit blauer Kante wie die
  Nachweiskapitel.

### Lastfallzeilen

* **Die Zeile steht links**, der Name ist höchstens drei Zahlenfelder breit
  (240 px). Vorher füllte der Name die ganze Breite, und Name und Zahlen
  standen weit auseinander.
* In der schmalen Tafel bleiben die Felder 80 px breit. Der Name darüber ist
  so breit wie die Felder unter ihm.
* **Spaltenköpfe dunkler** (wie die Kapitelköpfe), «Bezeichnung»
  linksbündig über dem Namen.

---

## 2026-09-26 · Python in einem eigenen Faden

Wunsch: Die Seite soll nicht mehr stillstehen, während der Browser rechnet.

### Vorher und nachher

Ohne Server rechnet Pyodide im Browser. Bisher tat es das im selben Faden wie
die Oberfläche. Solange Python rechnete, ging nichts: kein Scrollen, kein
Klick, kein Laufbalken. Jetzt rechnet es in einem Web Worker.

Gemessen an der Dickensuche des Beispiels (sechs Suchen, 0.8 s). Gezählt
wurden die Bilder, die die Seite in dieser Zeit zeichnet
(`requestAnimationFrame`):

| | längste Pause zwischen zwei Bildern |
| --- | --- |
| vorher, im Hauptfaden | ≈ 800 ms: die Seite steht die ganze Suche lang |
| jetzt, im Web Worker | 22 ms: 62 Bilder je Sekunde, flüssig |

Mit allen Nachweisen dauert eine Dickensuche bis zu einer halben Minute. So
lange stand die Seite vorher still.

### Wie es gebaut ist

* **`web/js/kern_arbeiter.js` ist der Faden.** Er lädt Pyodide, hängt die
  Quelldateien samt Versionsmarken ein und bindet `opencivil.web.dienst` ein.
  Dann beantwortet er eine Nachricht nach der anderen mit `bearbeite_json`.
  Das Einhängen ist unverändert aus `kern.js` herübergezogen.
* **`web/js/kern.js` vermittelt nur noch.** Jede Anfrage bekommt eine Nummer.
  Die Antwort mit derselben Nummer löst ihr Versprechen ein. Hinein und heraus
  geht JSON als Zeichenkette, wie über HTTP.
* **`api.js` sieht keinen Unterschied mehr.** Server und Browser antworten
  beide mit einem Versprechen.
* **Fehler kommen an wie bisher.** Wirft Python, erscheint die Meldung des
  Kerns als `KernFehler`. Stirbt der Faden selbst, bekommt jede wartende
  Anfrage einen Fehler. Keine wartet ewig.
* **Der Ladeschirm meldet dasselbe:** «Python wird geladen …», dann
  «Rechenkern wird eingelesen …».

### Warum erst jetzt

Beim Umzug in den Browser (2026-09-11) brauchte ein ganzer Durchgang 73 ms.
Ein Worker lohnte damals nicht. Mit der Dickensuche rechnet ein Knopfdruck ein
Vielfaches davon.

### Nachgeprüft

Im Browser ohne Server geprüft: Eingabe und Rechnen, das Auge, der Bericht und
die Dickensuche. Ein absichtlicher Fehler kommt mit der Meldung des Kerns an.
Die Konsole bleibt ohne Fehler. Mit Server ändert sich nichts, dort rechnet
CPython ohnehin in einem anderen Prozess.

---

## 2026-09-26 · Eine Obergrenze der Bewehrung, und die dünnste Platte

Wunsch: eine Obergrenze der Bewehrung und zwei Modi, die die Plattendicke
optimieren -- dazu eine Mindestdicke.

### Die Obergrenze

* **Eingegeben wie eine Lage:** Grund ⌀@s plus Zulage ⌀@s
  (`ObergrenzeEintrag`, zwei gewöhnliche `PostenEintrag`), Vorgabe ⌀30@150
  = 4712 mm²/m. Beide leer heisst: keine Grenze.
* **Es zählt die Summe je x-Lage** (auf Entscheid). Wie die Suche sie auf
  Grund und Zulage verteilt, ist frei. Geprüft wird jede Lage für sich.
* **Sie gilt in allen Modi** (auf Entscheid). Einen Schritt über die Grenze
  rechnet die Suche gar nicht erst. Reicht es darunter nicht, meldet sie
  «Obergrenze … mm²/m je Lage erreicht».
* **Grössere Durchmesser:** Damit ⌀30@150 überhaupt erreichbar ist, kennt die
  Längsbewehrung jetzt auch ⌀30, ⌀34 und ⌀40; die Grenze hält die Suche im
  Zaum. Bügel bleiben bei höchstens ⌀26.
* **Die Summe in mm²/m rechnet der Kern** (`api.obergrenzen`), mit derselben
  Fläche je Posten wie die Lagen (`PostenEintrag.je_meter` über
  `Bewehrungsposten.flaeche`). Die Oberfläche zeigt sie nur.

### Die dünnste Platte

* **So sucht `dicke_suchen`:** Je Dicke läuft die gewöhnliche
  Bewehrungssuche.
  - Von der eingegebenen Dicke aus wird halbiert, solange es geht, aber nie
    unter die Mindestdicke (Vorgabe 150 mm). Geht es nicht, wird verdoppelt,
    höchstens bis 2 m.
  - Dazwischen läuft eine Bisektion auf dem Zentimeter. Das Ergebnis ist die
    kleinste Dicke dieses Rasters, also auf den nächsten cm aufgerundet.
  - Übernommen werden Dicke und Bewehrung.
* **«Geht» heisst:** Die Suche findet eine Lösung unter der Obergrenze, und
  die Duktilität geht auf, wenn sie eingeschaltet ist. Die Bewehrungssuche
  selbst weicht der Duktilität aus, weil mehr Stahl sie verschlechtert. Bei
  der Dicke ist sie dagegen gerade das Kriterium, das eine dickere Platte
  verlangt.
* **Beispiel:** Von 300 mm und von 120 mm aus ergibt sich dieselbe Dicke,
  170 mm: 300 ✓, 150 ✗, 220 ✓, 180 ✓, 160 ✗, 170 ✓. Das sind sechs Suchen in
  0.4 s, unter Pyodide 0.8 s.
* **Bewusst begrenzt:** Dicker ist nicht immer leichter, denn die
  Mindestbewehrung wächst mit der Dicke. Bei der Decke aus «voll» sind es
  2723 mm² bei 300 mm und 7079 mm² bei 2400 mm. Mit einer Obergrenze kann
  eine sehr dicke Platte also wieder durchfallen.
  - Darum hört das Verdoppeln bei 2 m auf und meldet «keine Dicke».
  - Die Bisektion setzt voraus, dass es innerhalb einer Verdopplung nur
    einmal von «geht nicht» zu «geht» wechselt.

### Offen

* **Die blockierte Seite:** Im Browser ohne Server steht die Seite während
  der Suche still. Mit allen Nachweisen braucht eine einzelne Suche 2–3 s, die
  Dickensuche also bis zu einer halben Minute. Der nächste Schritt wäre ein
  Web Worker für Pyodide. **Erledigt** im Eintrag darüber: Python rechnet
  jetzt in einem eigenen Faden.

---

## 2026-09-26 · Aufgeräumte Oberfläche, eine Formelsammlung und ein Blatt wie Mathcad

Eine Liste mit fünfzehn Punkten, abgearbeitet in vierzehn Schritten, jeder
ein Commit. Die Tests kamen zuerst, weil jeder spätere Schritt die Suite
laufen lässt: 132 s → 28 s, ohne Abdeckung zu verlieren. Gestrichen wurde
nur Doppeltes; mit den Tests der neuen Teile sind es jetzt 637 statt 656.

### Die Zeit steckte in wenigen Rechnungen

Drei Viertel der Laufzeit gingen auf eine Handvoll Rechnungen: dieselben
Knickfälle in jedem Test neu, ein zwölf Meter langer Stab mit fünf Sekunden
je Grenzkraftsuche, ein Knickfall im Standardprojekt, der jeden kalten Lauf
zwei Sekunden kostete. Jetzt rechnet jede Klasse sie einmal, und der instabile
Fall ist −8000 kN auf 3 m. Erst danach wurde gestrichen, und nur, was ein
anderer Test schon prüft.

### Zwei Rechenfragen

* **Die Breite b rechnete richtig.** Bei b = 500 halbieren sich A_s, M_Rd,
  N_Rd und das Rissmoment, und alle Grade bleiben gleich. Nur die Darstellung
  verschwieg den Bezug: Die Lagentabelle mischte «je b» und «je 1000 mm».
  Jetzt bekommt sie eine Spalte b, sobald x und y verschieden breit sind.
  Die Maske schreibt «M, N je b = … mm · V je m». Ein Test halbiert b, M und
  N und erwartet jeden Grad unverändert.
* **Der Eckpunkt x = h/2 fiel weg**, sobald die Zugbewehrung dort nicht
  fliesst, und mit ihm der ganze Bauch des Polygons. Liegt die x-Bewehrung
  tief, ergab das bei N = −2000 kN von Hand 81 kNm; genau gerechnet sind es
  282 kNm. Jetzt trägt der Stahl, was seine Dehnung hergibt,
  σ_sd = min(E_s·ε_s; f_yd). Das ergibt 246 kNm, innerhalb der genauen
  Linie. Querkraft und Knicken erben das Polygon und damit die Korrektur.

### Oberfläche

* **Neue Einträge nehmen die kleinste freie Nummer.** Bisher war es
  «Anzahl + 1», was nach dem Löschen einen doppelten Namen ergab. Den wies
  der Kern ab.
* **Die automatische Bewehrung steht im Bewehrungs-Panel**, also dort, wohin
  sie schreibt. Ihre Moduswörter kommen aus dem Kern
  (`Suchmodus.beschriftung`) statt aus einer JS-Kopie. «y-Grundbew. wie x»
  wirkt schon in jeder Rechnung der Suche, denn eine aussen liegende y-Lage
  kostet die x-Richtung statische Höhe.
* **Die Zusammenfassung hat höchstens zwei Zeilen je Zelle.** Welche Spalten
  übereinander stehen, sagt der Kern (`stapel_spalten`), wie schon bei der
  Grad-Spalte.
* **Ein Auge statt des Reiters «Werte».** Es startet einen Teillauf neben
  der Gesamtlösung, nicht an ihrer Stelle, damit Zusammenfassung, Diagramme
  und Bericht vollständig bleiben. Sein Ziel ist `NachweisUrteil.ziel`, die
  Wert-ID des Erfüllungsgrads.
* **Das Querkraft-Diagramm steht immer da.** Ohne V_Ed läuft der Nachweis
  still mit einem Nullfall, weil die Beiwerte der Kurve erst im Lauf
  entstehen. Er fällt kein Urteil, meldet keinen Mangel und schreibt keine
  Herleitung.
* **Fragezeichen und Texte:** Alle Hilfetexte stehen in einer Tafel (`HILFE`)
  mit den Stichworten Rechenweg · Werte · φ. Sichtbare Texte sind knapp;
  längere Texte gibt es nur in der Formelsammlung.

### Die Formelsammlung

Die erklärenden Absätze standen in der Herleitung mitten zwischen den Zahlen.
Jetzt heissen sie `p.erklaerung(…)`. `darstellen()` lässt sie aus, und diese
eine Stelle gilt für die Oberfläche und alle Berichte. Die Sammlung nimmt sie
auf, ebenso die rein symbolischen Ansätze (`p.ansatz(…)`). Nach jeder
Berechnung stempelt das Rechenwerk das Thema auf ihre Blöcke; das spart jeder
Berechnung, es selbst durchzureichen. Entdoppelt wird über den ganzen Lauf,
nach der Vorlage ohne führendes Minus und nach dem Grundzeichen des
Ergebnisses. So bleibt M_Rd,x = … und M_Rd,y = … eine einzige Formel. (Was
die Oberfläche davon zeigt, hat sich danach noch geändert: siehe «Die
Formelsammlung zeigt alles».)

### Analytische Gleichungen

* **Kein `eval`.** Ein rekursiver Abstieg liest die LaTeX-Teilmenge, die
  MathLive liefert, und rechnet mit `Groesse`. Einheiten prüft er also wie
  überall im Kern.
* **Getipptes LaTeX erreicht KaTeX nie.** Die Anzeige entsteht aus dem
  Syntaxbaum als Vorlage und geht durch dieselbe `Formelzeile` wie jede
  Herleitung: Symbol = Formel = Zahlen = Ergebnis. `\href`, `\htmlClass`
  und ähnliche Befehle weist schon der Leser ab.
* **Jede Zeile steht für sich.** Ein Fehler bleibt bei seiner Zeile und bei
  den Zeilen, die ihr Ergebnis brauchen («y: Fehler in Zeile 7»). Er bricht
  weder das Blatt noch die Platten ab. Eine Neudefinition gilt ab ihrer
  Zeile, wie beim Lesen von oben nach unten.
* **Projektwerte sind Eingabebezüge.** Das Rechenwerk rechnet darum die
  Platte vorher. Ein verschwundener Wert ist ein Fehler seiner Zeile und
  kein Abbruch.
* **MathLive liegt im Repo** (840 KB) und wird erst geladen, wenn ein Blatt
  offen ist. Seine Schriften sind byte-gleich mit denen von KaTeX und werden
  von dort genommen.
* **Die Ansicht bleibt stehen.** Neu gezeichnet verlöre ein Formelfeld mitten
  im Tippen Fokus und Cursor. Die Ansicht behält darum ihre Knoten, solange
  die Zeilen dieselben bleiben. Kommt eine Zeile dazu, wird sie neu gebaut.
  Vorher lässt sie den Fokus los: MathLive merkt sich das fokussierte Feld,
  und verschwindet es ohne Blur, wirft der nächste Fokus.

### Beim Durchsehen gefunden

Drei Fehler, jeder mit eigenem Commit und Test:

* **Das Auge bei Knicken.** Das Knicken las das M-N-Polygon direkt vom
  Nachweisobjekt, meldete es dem Rechenwerk aber nicht als Eingang. Im
  Gesamtlauf fiel das nicht auf, weil M-N vorher rechnet. Der Teillauf des
  Auges brach dagegen ab, und die Oberfläche zeigte still die ganze
  Herleitung. Jetzt ist N_Rd⁻ ein Eingang, wie m_Rd bei der Querkraft. Die
  Lücke bestand seit dem 18.9.; sichtbar wurde sie erst mit dem Auge.
* **Querkraft ohne V_Ed.** Der stille Nullfall für das Diagramm gab ein
  Urteil ab. Ohne Zugbewehrung ist V_Rd = 0, und die Zusammenfassung meldete
  «Querkraft – ohne Einwirkung: nicht erfüllt, ausgeschaltet» bei einer
  Platte ganz ohne Querkraft. Jetzt gibt der Nullfall kein Urteil ab. Das
  Diagramm lässt ihn nach dem Fall weg, nicht nach dem Schalter «still»:
  der heisst «ausgeschaltet», nicht «nur für das Bild».
* **Bewehrung suchen.** Die Suche leert die gesuchten Lagen zuerst, als
  Zeichen, dass gesucht wird, und zwar im gespeicherten Projekt. Fand sie
  nichts, blieben die Lagen leer, obwohl der Kommentar das Gegenteil sagte.
  Jetzt kommen die alten Durchmesser zurück, wo das Feld noch leer ist.

### Vereinfacht

Wieder vier Durchsichten des Diffs: Wiederverwendung, Vereinfachung,
Effizienz, Ebene der Lösung. Der Bericht blieb dabei unverändert.

* **Eine Stelle statt mehrerer:**
  - Der Langname eines Urteils wird gestempelt wie der Raum, statt achtmal
    mitgegeben.
  - «n. Lage ohne Bewehrung» und «Zugseite ohne Bewehrung» stehen je einmal
    da.
  - Sekunde, Minute, Stunde, m³ und kN/m³ stehen im Einheitenkatalog statt im
    Leser. Eine getippte Einheit kommt zuerst von dort: «N/mm2» wird N/mm²,
    «1/m» wird überhaupt erst lesbar.
  - Der «Name im Index» (Sorte, Fall) gilt für Formelsammlung und Blatt
    gleich.
* **Die Oberfläche fragt den Kern:**
  - Leere Gleichungszeile, Einheiten für die Tipp-Kürzel und
    Namensvorschlag eines Projektwerts kommen aus dem Kern.
  - Den Vorschlag macht der Leser selbst. Vorher schlug die Oberfläche
    ⌀_{1,y,g} vor, das der Leser ablehnt, und k_σ nicht, das er annimmt.
* **Kein Raum auf jedem Formelblock:** zwei Antworten auf dieselbe Frage
  -- der Abschnittstitel trägt ihn schon -- sind eine zu viel. (Seit die
  Formelsammlung alles zeigt, braucht sie gar keinen Raum mehr.) Die
  Oberfläche zeichnet die Sammlung mit dem gemeinsamen Blockzeichner.
* **Das Auge ist schneller:**
  - Vorher zeichnete der Klick erst die ganze Herleitung und warf sie gleich
    wieder weg. Unter Pyodide kostete das bei drei Platten eine halbe
    Sekunde.
  - Nach einer Eingabe kommen Haupt- und Teillauf in einem Zeichnen an.
  - Der Teillauf rechnet nur, wenn die Herleitung zu sehen ist.

Bewusst nicht:

* **Die Rechenfolge** Baustoffe → Platten → Blätter steht sowohl in
  `alle_ziele` als auch in `_stromabwaerts`. Eine gemeinsame Liste schickte
  die Baustoffe durch den Verschmelzungsweg des Zwischenspeichers, und das
  kann die Herleitung verschieben.
* **Eine schlanke Antwort für Teilläufe** sparte etwa ein Zehntel und
  änderte die Form der Schnittstelle.
* **Diese Umbauten** wären grösser, als der Nutzen rechtfertigt:
  - Zeilen des Blatts einzeln nachführen statt neu bauen (31 ms bei 12
    Zeilen unter Pyodide).
  - Die M-V-Kurve zwischenspeichern (2–4 %).
  - Die Suche als Ansichtszustand führen, statt die Lagen im Projekt zu
    leeren. Die Rückgabe der alten Werte behebt den Verlust schon.

### Kerndateien mit Versionsmarke

Beim Prüfen mit Pyodide kam `blatt.py` nach einer Änderung noch alt, während
die Oberfläche schon neu war. Ein schlichter statischer Server sagt nichts
übers Zwischenspeichern, und der Browser schätzt dann selbst.

* **Jetzt steht im Manifest neben jedem Pfad eine Marke:** die ersten zwölf
  Zeichen von SHA-256 über den Inhalt. `kern.js` holt `…py?v=Marke`, eine
  geänderte Datei hat also eine neue Adresse. Geprüft: nach einer Änderung
  kam genau sie frisch, die übrigen 54 aus dem Zwischenspeicher.
* **Das Manifest selbst geht bewusst nicht an jedem Speicher vorbei.** Es
  soll so alt sein wie die Oberfläche, die es liest; GitHub Pages speichert
  beide zehn Minuten. Frisch geholt träfe nach einer Veröffentlichung eine
  noch gespeicherte alte Oberfläche auf den neuen Kern.
* **Das Manifest ändert sich jetzt mit jeder Änderung am Kern.** Der Test
  in `test_dienst` meldet, wenn `python3 -m opencivil.web.bruecke` vergessen
  ging.

### Ergebnisse statt Rechenziele in der Werteliste

In der Werteliste des Berichts stand vom Blatt nur sein Ziel: «Zeilen ohne
Fehler – Vorbemessung, n = 5». Die Zeilenwerte selbst fehlten.

* **Warum das Ziel bleibt:** Das Rechenwerk verlangt vorab erklärte
  Ausgaben. Welche Zeilen aufgehen und in welcher Einheit, steht aber erst
  nach dem Rechnen fest. Ein Ziel, das immer entsteht, braucht das Blatt
  trotzdem, auch eines nur mit Text will in die Herleitung.
* **Die Zeilen:** Das Blatt gibt nach dem Rechnen zusätzlich zurück, was
  seine Zeilen ergeben haben (`Gleichungsblatt.ausfuehren`), und das
  Rechenwerk legt es ab wie jede Ausgabe.
  - Die Beschreibung «Vorbemessung, Zeile 4» bekommen die Werte erst dort.
    In der Herleitung stünde sie sonst als Titel über jeder Zeile.
  - Ein Projektwert behält die Herkunft des Originals: h bleibt Eingabe.
  - Die Kennungen sind dreistellig (`z004`), sonst sortierte die Liste
    Zeile 10 vor Zeile 2.
* **Das Ziel:** Es trägt das neue Kennzeichen `WertDef.nur_ziel` und steht
  in keiner Werteliste mehr.
* **Der Nullfall der Querkraft** (Diagramm ohne V_Ed) gehört zur selben Art:
  V_Rd und Erfüllungsgrad «ohne Einwirkung» sind nur Ziel, damit die Kurve
  entsteht. Sie tragen dasselbe Kennzeichen; aus der Werteliste von
  «beispiel» fielen damit zwei Zeilen.

### Die Formelsammlung zeigt alles

Die Formelsammlung entstand aus dem Lauf des offenen Projekts. Sie zeigte
darum nur, was dort gerechnet wurde; im Beispiel waren das 30 Formeln zu vier
Themen, kein Knicken, keine Querkraft. Gemeint war sie aber zum Nachschlagen,
unabhängig vom Projekt. Jetzt zeigt sie jede Formel des Werkzeugs: 81 Formeln
und 32 Erklärungen zu zwölf Themen.

* **Woher die Formeln kommen:** aus zwei Projekten, die zusammen jeden
  Nachweis laut führen. Das sind dieselben wie im Schnappschuss, und ein
  Test wacht darüber.
  - Das zweite, «voll», stand bisher im Test. Jetzt steht es als
    `Projekt.jeder_nachweis()` im Kern, eine Stelle für beide Zwecke.
  - Gerechnet wird mit allen Kennwerten der Baustoffe (`alle_ziele`), sonst
    fehlte ε_yd.
  - Gerechnet wird im schnellen Aufbau: 0.3 s statt 2.6 s, bei derselben
    Sammlung, Zeichen für Zeichen.
* **Vorab erzeugt:** Unter Pyodide dauerte das Rechnen beim ersten Blick in
  den Reiter mehrere Sekunden. Darum schreibt `python3 -m
  opencivil.web.bruecke` die Sammlung als `web/kern/formelsammlung.json`,
  und die Oberfläche liest sie nur noch. Ein Test meldet, wenn sie nicht
  mehr zum Kern passt.
  - Die Antwort jeder Rechnung trägt sie nicht mehr mit.
  - Den Schalter «Aktuelle Seite / Gesamt» gibt es in diesem Reiter nicht
    mehr, denn es gibt nichts einzugrenzen.
* **Dieselbe Formel, zweimal geschrieben:** Summe und Schwerpunkt einer Lage
  schreiben Handrechnung und Lagennachweise mit anderen Platzhalternamen.
  - In der ganzen Sammlung standen sie darum doppelt, gleich gesetzt.
  - Jetzt gilt zusätzlich: was gesetzt gleich aussieht, ist dieselbe Formel.
  - Die Platzhalter einfach gleichzumachen wäre zu grob: dann fielen etwa
    σ = N/A und σ = M/W zusammen.
* **Im Bericht bleiben die Formeln des Laufs.** Ein Bericht erklärt, was er
  rechnet, nicht alles. Der Abschnitt heisst darum jetzt «Verwendete
  Formeln»; zwei verschiedene Dinge unter dem Namen «Formelsammlung» wären
  eines zu viel.

---

## 2026-09-25 · Jede Formel aus einer Vorlage -- und danach vereinfacht

Der Pilot der letzten Runde (Duktilität) hatte gezeigt, dass Vorlagen tragen.
Jetzt stehen alle Herleitungen so da: die Formel einmal mit Symbolen, Zahlen
und Einheiten setzt das Programm aus den gerechneten Werten ein. Von Hand
gesetzte Einheiten in den Nachweisen und Querschnitten: vorher 179, jetzt 13
-- Tabellenköpfe und die Stahldichte 7850 kg/m³. Jeder Schritt wurde am
Schnappschuss gemessen; geändert hat sich die Darstellung, keine gerechnete
Zahl. Damit das auch dort galt, wo bisher kein Projekt hinkam, ist «voll»
zuerst um Querkraft ohne Bügel, Bügel mit Stabzahl in y und die begrenzte
rissaktive Dicke erweitert worden.

### Zuerst die beiden Befunde des Piloten

* **Kein «1.00» neben «nicht erfüllt».** Die Herleitung rundete den Grad
  selbst. Jetzt kennt ein Wert, ob er ein Erfüllungsgrad ist (`grad_def`),
  und setzt sich überall nach `grad_als_text` -- auch in der Werttabelle,
  die dasselbe an ihr vorbei tat: dort stand 0.996 als «1». Die Obergrenze
  1e9, die acht Nachweise einzeln setzten, fällt weg; ein unendlicher Grad
  steht als ∞ da, JSON bekommt `null` (das konnte `endlich()` längst).
* **Umbruch nach dem, was man sieht.** `sichtbare_breite` zählt einen Bruch
  so breit wie seinen breiteren Teil, `\left` und `\,\mathrm{mm}` fast gar
  nicht. Zwischen 52 und 68 sichtbaren Zeichen lag im Projekt keine Formel;
  die Grenze steht bei 60.

### Empirische Formeln

Wo die Norm eine Einheit voraussetzt, steht die Zahl blank in dieser Einheit,
dahinter der Hinweis: `k_t = 1/(1 + 0.5 · 0.3/3) = 0.952 (h in m)`. So bei
E_cm, τ_cd, k_t (dreimal), α_i, k_g und k_d. Die Stellen wandern mit der
Einheit -- 300 mm stehen als 0.3 m da, nicht als 0. Vorher stand bei E_cm
`∛(38 N/mm²)`, bei k_d ein von Hand gesetztes `· 10⁻³`.

### Was beim Umstellen auffiel

* **Querkraft, fliessende Bewehrung:** Liegt m_Ed über m_Rd, ist ε_v fest,
  1.5 · f_yd/E_s. Die Herleitung zeigte trotzdem die Formel mit m_Ed und
  m_Rd -- mit Zahlen, die ein anderes ε_v ergeben (4.79 statt 3.26 ‰).
* **A_s,tot** stand mit zwei Nachkommastellen da: eine von Hand gebaute
  WertDef gab die Stellenzahl als Normverweis weiter.
* **Eine auf null gerundete Zahl** stand als «-0».
* **f_cd in der Handrechnung** ohne Nachkommastelle: bei C25/30 «17» statt
  16.7, die Druckkraft ging von Hand um 2 % daneben.
* Grössen der ganzen Lage tragen deren Index (σ_s,adm,3,x), wie Widerstand
  und Grad in der Tabelle; die statische Höhe sagt, aus welcher Lage sie
  kommt (`d = h − z_{3,x,g}`).

### Vereinfacht

Vier Durchsichten des Diffs -- Wiederverwendung, Vereinfachung, Effizienz,
Ebene der Lösung --, jeder Befund ein Commit, der Bericht dabei unverändert:

* **Ohne Leser keine Herleitung.** Bewehrungssuche, ausgeschaltete Nachweise
  und Querkraftkurven bauten jede Formel -- zweimal eingesetzt, Breite
  gemessen -- und warfen sie weg. Die Suche an der Decke von «voll» brauchte
  91 ms statt 42 ms vor der Umstellung. Das stille Protokoll baut jetzt gar
  nichts; `loese(…, ohne_herleitung=True)`. Dieselbe Suche: 33 ms.
* **Was mehrere Nachweise gleich herleiten, steht einmal da:** k_t mit
  f_ct,eff und das Rissmoment (`protokoll_rissmoment`), die zulässige
  Stahlspannung, Summe, Schwerpunkt und statische Höhe einer Lage
  (`protokoll_lage`), der wirksame Modul, die Grad-Zeile (`grad_formel` nimmt
  Widerstand und Einwirkung), das Gegenzeichen eines Vergleichs (`vergleich`
  bekommt das Sollzeichen).
* Einwirkung und Widerstand für Tabelle und Herleitung über `Zwischenwerte`
  statt je vier Zeilen WertDef. Die Spannungsbegrenzung nimmt Platte und
  Richtung von ihrer Grenze, statt beides doppelt zu bekommen und zu prüfen.
* Gestrichen: `annahmen_text/_latex`, die JSON-Felder `einzeilig`/`mehrzeilig`
  (las niemand), Symbolfelder, deren Eingabe ihr Symbol mitbringt, tote
  Parameter und Importe.

Bewusst nicht: Der Umgebungszweig in `sichtbare_breite` bleibt, obwohl ihn
heute keine Formel erreicht -- ohne ihn wäre die Messung für eine
Fallunterscheidung falsch. k_d, k_t und α_i rechnen nicht über `empirisch()`;
ihre Einheit steht neben der Vorlage, und die Kurve rechnet k_d fünfzigmal.
Vorlagen zwischenzuspeichern brächte ein Prozent.

### Danach, auf Entscheid

* **Die Tiefe einer Lage heisst `z`.** Die Platte führte sie unter `d`: für
  eine obere Lage stand in der Tabelle d = 48 mm, im Nachweis darunter
  d = 252 mm. Jetzt heisst sie an der Quelle z (Tabelle «Randabstände,
  Tiefen ab Oberkante», Werttabelle, Handrechnung), und die statische Höhe
  steht überall in einer eigenen Zeile, `d = z` unten, `d = h − z` oben.
  Den Schwerpunkt einer Seite schrieb die Handrechnung nach Kräften
  gewichtet, gerechnet wurde nach Flächen -- jetzt steht dasselbe da.
* **M-N, «nächster Punkt»:** Der Grad ist ein Verhältnis von Längen im
  normierten Diagramm, (Ē_d ± a)/Ē_d. Herleitung und Zusammenfassung zeigten
  das Moment des nächsten Punkts gegen M_Ed (175.1/150, wo der Grad 1.40
  war). Jetzt stehen N_ref, M_ref, Ē_d, der Punkt P, a und R̄_d da, und die
  Zusammenfassung zeigt dasselbe Paar. «voll» führt einen solchen Fall mit.
* **Ohne Einwirkung keine Dehnung:** Für M = N = 0 fand der Löser die
  Nullebene nur bis auf seine Schranke; der Rest gab einen Grad von 3 · 10⁸
  statt ∞. Der Löser gibt die Nullebene jetzt exakt zurück.

### Offen

* **Lagen mit einem Posten** heissen je nach Stelle `3,x` oder `3,x,g`; die
  Handrechnung schreibt A_s,3,x, die Nachweise A_s,3,x,g. Dahinter steht
  `posten_ids` als Tupel ohne Marke und Index.

---

## 2026-09-25 · LaTeX für Formeln, Text für Text: der Bericht aus Blöcken, in drei Formaten

Anlass war die Frage, ob LaTeX die richtige Entscheidung war, und ob Formeln
und Tabellen nicht auch in Markdown gingen. Die Antwort und eine zweite
strenge Durchsicht des ganzen Codes führten zu elf Schritten, jeder am
Schnappschuss des Berichts gemessen -- der dafür zuerst auf ein zweites
Projekt verbreitert wurde, das jeden Nachweis einmal laut führt.

### LaTeX ja -- aber nur, wo Mathematik steht

Markdown hat keine eigene Formelsprache. Wer Formeln darstellt -- GitHub,
Obsidian, Jupyter, Pandoc --, liest LaTeX-Mathe zwischen `$…$` und `$$…$$`;
Word 365 versteht LaTeX-Mathe im Formeleditor und MathML aus der
Zwischenablage. Für Formeln war LaTeX also richtig.

Falsch war es als Träger von Text und Tabellen. Jede Tabellenzelle war LaTeX,
Text stand als `\text{…}` darin: die Konsole druckte das so ab, der
Word-Knopf einer Tabelle lieferte eine Formelmatrix statt einer Tabelle, und
die Oberfläche las den Text per regulärem Ausdruck zurück. Jetzt sagt eine
Zelle, was sie ist: ein `str` oder `Mathe(latex)`. Auch jede Zahl ist Mathe --
ihr Minus ist ein Minuszeichen und kein Bindestrich; beim ersten Umbau waren
Zahlen kurz Text, und im `.tex` stand `-6000.0` mit Bindestrich. Im Dokument
sind Tabellen jetzt `tabular` bzw. `longtable`, nicht mehr eine Formel.

### Der Bericht besteht aus Blöcken

Konsole und LaTeX-Dokument bauten ihre Abschnitte je selbst und liefen
auseinander: die Werte vor oder hinter den Nachweisen, nach Kennung oder nach
Bezeichnung; und beide fassten die Nachweise flach zusammen, ohne Platten --
zwei Kombinationen «Feld» zweier Platten sahen gleich aus. Ein
Markdown-Bericht hätte eine dritte Kopie gebraucht.

Jetzt legt `bericht/gliederung.py` den ganzen Bericht als `Protokoll` an, aus
denselben sechs Blockarten wie die Herleitung. Jede Darstellung ist eine Tafel
`{Blockart: Funktion}`, ein Durchlauf setzt sie; eine Blockart ohne Eintrag
wirft, statt still zu fehlen (vorher gab die Oberfläche für Unbekanntes `None`
zurück, und das wurde weggefiltert). Die Nachweise stehen je Platte mit
derselben Tabelle wie am Bildschirm, aus denselben Stücken
(`bericht/zusammenfassung.py`). Eines kommt im Bericht dazu: auf Papier gibt
es weder rote Zeilen noch Tooltips, darum steht jeder nicht erfüllte Nachweis
mit seiner Begründung unter der Tabelle.

Tabellen dürfen jetzt eine Spalte als umbrechbar auszeichnen (`L`). Im
Dokument nimmt eine solche Tabelle die Zeilenbreite ein und bricht nur diese
Spalten um (`xltabular`); sonst liefe die Nachweistabelle mit zwei Formeln
nebeneinander über den Rand.

### Markdown und drei Knöpfe

Der Markdown-Bericht ist die dritte Tafel. An jeder Formel und jeder Tabelle
stehen jetzt *Word*, *TeX* und *MD*. Das Markdown eines Blocks kommt aus
derselben Tafel wie das Dokument, damit Knopf und Dokument dasselbe liefern.
Eine Tabelle geht als HTML-Tabelle nach Word, Formelzellen darin als MathML.
Ob Word sie so einfügt, wie es soll, ist hier nicht prüfbar -- die
Zwischenablage enthält, was sie soll.

### Der Pilot: Herleitung aus Vorlagen

Die Handrechnung schrieb ihre Formeln schon als Vorlage, `p.formel` setzte
Zahlen und Einheiten ein. Die übrigen Nachweise schreiben Symbol- und
Zahlenzeile von Hand, mit eigener Umrechnung. Probeweise umgestellt ist die
Duktilität: im Modul von 10 handgesetzten Einheiten auf 0, von 13
Umrechnungen auf 2 (beide im Begründungssatz), und Querschnitt und
Schwerpunkt einer Lage aus zwei Posten stehen jetzt mit Zahlen da statt nur
mit dem Resultat. Dafür wurden die Zwischenwerte der Handrechnung zu
`Zwischenwerte` neben `Protokoll.formel`.

Was der Pilot zeigte:

* **Jeder Nachweis rundet seinen Erfüllungsgrad selbst**, sieben Stellen mit
  `f"{grad:.2f}"`. Ein knapp verfehlter steht in der Herleitung damit als
  «1.00» neben «nicht erfüllt» -- genau das, was `grad_als_text` verhindert,
  aber die Herleitung geht an ihr vorbei. Über `p.formel(…, ergebnis_latex=…)`
  folgt die Duktilität jetzt der Regel; die übrigen täten es mit der
  Umstellung.
* **Der Umbruch zählt Quelltext**, nicht was man sieht: `darstellen()` setzt
  mehrzeilig ab 90 Zeichen LaTeX, und `\left`, `\,\mathrm{mm}` zählen mit.
  Von 45 mehrzeilig gesetzten Formeln im Projekt «voll» sind 30 sichtbar
  kürzer als 70 Zeichen. Das gilt schon für die Baustoffe und die
  Handrechnung; vor einer Umstellung der übrigen wäre das zu klären.
* **Die Postenhöhe heisst `d`, ist aber `z`**: gemessen ab Oberkante. Von
  Hand fiel das nicht auf, in einer Vorlage steht dann `d = h - d`. Die
  Duktilität setzt darum ein eigenes `z`.

Offen und zu entscheiden: rund 80 Gleichungen in acht Modulen, mit 124 von
Hand gesetzten Einheiten.

### Nebenbei

* Sechs Diagramme bauten Massstab, Gitter und Titel je selbst. `achsen.js`
  macht das einmal; verglichen wurde das SVG jedes Diagramms vorher und
  nachher, 8 von 10 gleich, die Werkstoffgesetze absichtlich angeglichen.
* Die Spannung-Dehnung-Analyse baute ihre Löser in der Schnittstelle -- ohne
  Oberfläche war sie nicht zu haben, und ihr Test prüfte eine eigene Kopie
  des Aufbaus. Jetzt `spannungsanalyse.analysen()` und `Ergebnis.analysen()`.
* Die Punktfolgen der Diagramme stehen in `web/diagrammdaten.py`; dabei fiel
  eine zweite Kopie von `BLOCKANTEIL = 0.85` weg. Die Webtests sind nach
  Thema geteilt.
* Eine Regel für Fallkennungen statt elf Kopien, eine Liste der
  Rissanforderungen statt zwei; `eintragen()` lehnt ein Nachweisfeld ab, das
  nicht in `NACHWEISFELDER` steht.
* Im LaTeX-Fliesstext stehen griechische Buchstaben und `≥` als Unicode. Unter
  pdflatex bricht das ab -- älter als diese Runde und als eigene Aufgabe
  vermerkt. Eine TeX-Maschine gibt es hier nicht; übersetzt wurde nichts.

---

## 2026-09-25 · Stahlspannung unter Dauerlast, und was ein strenges Review daran verschob

Neu ist ein Nachweis: die Stahlspannung unter quasi-ständiger Einwirkung,
gehalten gegen dieselbe zulässige Spannung wie bei der Zwängung -- `f_yk` bei
normaler Anforderung, die Wurzelformel mit `w_nom` bei erhöhter und hoher.
Gerechnet wird mit 60 % der Tragsicherheitseinwirkungen, beim bestehenden
Nachweis gegen Fliessen mit 70 %; beide Anteile sind je Platte einstellbar.
Das Was steht im Code. Hier steht, warum er so aussieht -- und was eine
zweite, strenge Durchsicht danach noch verschoben hat.

### Das Plateau gehört zu f_yk

Die Gebrauchsnachweise rechneten mit dem Fliessplateau bei `f_yd`. Für den
neuen Nachweis wäre das tödlich gewesen: bei normaler Anforderung ist die
Grenze `f_yk = 500`, das Plateau kappte die Spannung aber bei 435 -- ein
Nachweis, der per Konstruktion nie durchfällt. Der Teilsicherheitsbeiwert
gehört in die Tragsicherheit; im Gebrauchszustand wird gefragt, was der
Querschnitt *tut*, und Stahl fliesst bei `f_yk`.

Welche Werte ein Nachweis ansetzt, ist seither ein Name und keine Zahl an der
Aufrufstelle: `Werkstoffsatz.BEMESSUNG` oder `CHARAKTERISTISCH`. Zuerst hatte
der Satz nur einen Nutzer, und die anderen schrieben weiter `"f_yd"` von Hand --
eine Abstraktion, die zur Hälfte eingeführt ist, ist schlechter als keine. Jetzt
nennt jeder Nutzer des Lösers seine Wahl.

### Gemessen wird an der Dehnung, wenn der Stahl fliesst

Bei normaler Anforderung fallen Grenze und Plateau zusammen. Ein fliessender
Stahl hätte dann `σ_s = σ_s,adm` und stünde mit 1.00 als erfüllt da -- dieselbe
Falle wie das «1.00 neben nicht erfüllt», die schon einmal behoben wurde, nur
von der anderen Seite. Darum `α = σ_s,adm / (E_s · ε_s)`: elastisch ist das Bit
für Bit der Spannungsvergleich, auf dem Plateau wächst die Dehnung weiter, und
der Nachweis fällt um so deutlicher durch, je weiter der Stahl gedehnt ist. Das
braucht auch die Bewehrungssuche -- ein Grad, der auf dem Plateau festsitzt,
zeigt ihr keine Richtung.

### Eine Klasse, zwei Grenzen

Beide Stahlspannungsnachweise sind dieselbe Rechnung: derselbe Löser, dieselbe
Fallschleife. Verschieden ist die Grenze -- ihre Zahl, ihre Eingaben, ihr
Absatz in der Herleitung. Also eine Klasse, und die Grenze als Objekt, das
diese drei zusammenhält. Zwei Klassen mit kopiertem Kern wären genau das, wovor
`zustand2.py` warnt: zwei Nachweise, die für denselben Querschnitt verschiedene
σ_s melden.

Die Durchsicht fand daran noch zweierlei. Die Grenzen legten beim Anmelden
Zustand ab, den sie später lasen -- eine Reihenfolge, die nur ein Docstring
sicherte. Und *wann* eine Grenze gilt, stand draussen, im Aufbau und im Katalog
der Oberfläche. Jetzt werden beide Grenzen gleich gebaut und sagen selbst, bei
welcher Anforderung sie gelten; im Aufbau sind die zwei Blöcke eine Schleife.

### Ein Konzept, ein Typ

Die Gebrauchslastfälle waren sechs flache Felder an der Platte, und fünf Stellen
setzten die drei zusammengehörigen über ihre Namen wieder zusammen. Jetzt ist
es eine `Gebrauchsliste` mit Anteil, Schalter und Fällen, die sich selbst
prüft. Das Dateiformat war erst eine Runde alt -- billiger wurde die Umstellung
nicht mehr. Alte Dateien werden gelesen und neu geschrieben.

Dieselbe Frage stellte sich an kleinerer Stelle mehrmals: was zu einer Platte
gehört, gehört an die Platte. Ihre Namensprüfung stand am Projekt, ihre
Massprüfung im Aufbau, die Aufzählung ihrer Lastfalllisten in der Suche. Jetzt
hat `QuerschnittEintrag` `pruefen()`, `masse_pruefen()` und `ohne_lastfaelle()`
-- und die Massprüfung bewusst *nicht* in `pruefen()`, weil das auch beim
Öffnen läuft: eine gespeicherte Platte mit `h = 0` liesse sich sonst nicht mehr
öffnen und korrigieren.

### Warum die Suche lange brauchte

Nicht zu viele Nachweise, sondern einer, der ein Bild malt: der M-N-Nachweis
baute bei jeder Bewertung die genaue Resistenzlinie, 97 000 Auswertungen des
Werkstoffgesetzes, für ein Diagramm, das während der Suche niemand ansieht.
Ohne sie: 289 → 56 ms je Bewertung. Dazu entstehen im schnellen Aufbau ganz
stille Nachweise nicht mehr -- exakt und nicht genähert, denn die Suche zählt
stille Urteile ohnehin nicht. Und ein `max()` im Betongesetz kostete, bei
siebzigtausend Aufrufen je Fall, allein 28 ms.

### Ohne Oberfläche, aber nicht daneben

`p.beton()`, `p.platte()`, `p.rechnen()` legen dieselben Einträge an, die die
Maske anlegen würde -- kein zweites Objektmodell, das mit dem ersten gleich
bleiben müsste. `Projekt.beispiel()` ist selbst so gebaut, damit prüft der
Schnappschuss die Fassade mit. Und die Zusammenfassung gibt es seit der
Durchsicht einmal, als Zeilenmodell, das Oberfläche und Konsole je auf ihre
Art setzen. Vorher baute jede ihre Zeilen selbst, und sie waren schon
auseinandergelaufen, bevor es jemand merkte.

### Der Schnappschuss

Vor allem anderen kam ein Test, der den ganzen Bericht des Beispiels Byte für
Byte vergleicht. Der Anlass war eine Zahl, die einmal von 261 auf 249 mm
gewandert war, ohne dass ein Einzeltest darauf zeigte. Seither ist jede Runde
daran gemessen: ob sich nur bewegt hat, was sich bewegen sollte. Die Durchsicht
hat in keinem ihrer sieben Schritte eine Zahl im Bericht geändert.

### Nebenbei

* Fallnamen standen roh als Wert-ID in den Formelzeichen. Aus «Feld (60 %)»
  wurde `Feld__60___`, ein doppelter Index, an dem KaTeX abbrach -- sichtbar,
  sobald der neue Nachweis immer lief. Jedes Symbol wird jetzt geprüft.
* Ein knapp verfehlter Grad hiess in beiden Berichten «1». Die Regel dagegen
  stand nur in der Schnittstelle; jetzt steht sie im Kern.
* Ein Test-Helfer setzte Felder mit `setattr`. Nach der Umstellung auf die
  Gebrauchsliste gab es die alten Namen nicht mehr -- `setattr` legte sie still
  neu an, und fünf Tests prüften nichts. Ein Helfer, der nach Namen setzt,
  muss unbekannte Namen ablehnen; dieser tut es jetzt.

---

## 2026-09-24 · Eine Tragrichtung, und ein Schalter je Nachweis

Bis heute rechnete das Werkzeug jeden Nachweis in beiden Tragrichtungen. Das
klang vollständig und war es nicht: für y hatte niemand Schnittgrössen, die
Toggles standen dort auf aus, und in der Zusammenfassung stand trotzdem die
halbe Tabelle voll Zeilen, die nichts aussagten. Nachgewiesen wird jetzt nur
noch x.

Die y-Lagen bleiben trotzdem. Sie sind keine Zierde: sie zählen zum
Bewehrungsgehalt, und vor allem liegen sie aussen und drücken die x-Bewehrung
nach innen. Wer sie weglässt, rechnet mit einer statischen Höhe, die es auf der
Baustelle nicht gibt -- im Beispiel sind das 261 statt 249 mm, also 5 % zuviel.
Darum ist die Vorgabe neu **x auf der 2. und 3. Lage**: die Querrichtung läuft
unten und oben durch, die Tragrichtung liegt dazwischen. Der häufigere Fall,
und der ungünstigere.

Die Suche fasst die y-Lagen nicht an. Das war eine Entscheidung mit zwei
möglichen Antworten, und die falsche wäre teuer gewesen: sucht man y gegen
dieselben Nachweise wie x, bekommt y auch dann Eisen, wenn niemand etwas
nachweisen will -- und sucht man es gegen die *eingeschalteten* Nachweise, bleibt
y bei den Vorgaben (alles aus) leer, und die statische Höhe von x ist wieder
optimistisch. Beides schlecht. Also gar nicht: der y-Durchmesser ist eine
Eingabe, und die Suche rechnet mit ihm.

### Vier Haken werden einer

Duktilität, sprödes Versagen, Zwängung auf Biegung und Zwängung auf Normalkraft
hatten je einen Schalter pro Lage. Vier Haken für eine Frage, und drei davon
betrafen Lagen, die niemand nachweist. Jetzt ist es einer. Gerechnet werden
beide x-Lagen -- die untere trägt das Feld-, die obere das Stützmoment --, in
der Zusammenfassung steht die ungünstigere, und die Herleitung zeigt beide samt
einem Satz, welche entschieden hat.

### Wo gesammelt wird, und wo nicht

Der erste Anlauf liess die Nachweise nur noch das schlechteste Urteil
zurückgeben. Das war die naheliegende Stelle und die falsche: damit war die
Ebene zurück, an der die Bewehrungssuche vor ein paar Runden schon einmal
stehengeblieben ist. Halten zwei Lagen gemeinsam das Minimum, hebt es kein
einzelner Schritt -- die Suche sieht eine Ebene und gibt auf, obwohl der
nächste Durchmesser offensichtlich hilft. Genau dafür zählt sie die *Summe*
der Rückstände, und die braucht jede Lage einzeln.

Der Test von damals hat es sofort gemeldet. Gesammelt wird jetzt in
`Loesung.gefuehrte_urteile`, also dort, wo ohnehin entschieden wird, was in
eine Tabelle gehört. Die Urteile tragen dafür ein `sammel`-Kennzeichen: vier
Lagen sind vier Antworten auf dieselbe Frage, drei Lastfälle sind drei
verschiedene Fragen, und welches von beidem vorliegt, weiß nur der Nachweis.

Die Regel dahinter ist älter als dieser Fall: **was gerechnet wird, und was man
davon sieht, sind zwei Fragen.** Das Stillstellen ausgeschalteter Nachweise
folgt derselben; beide gehören in die Darstellung, keine in die Prüfung.

### Was beim Einlesen passiert

Alte Dateien bringen die Listen noch mit. War irgendein Haken gesetzt, gilt der
Nachweis als eingeschaltet -- die Lesart, die nichts wegnimmt, was jemand
verlangt hat. Ein Lastfall dagegen, der nur in y galt, wird **gemeldet** statt
umgedeutet: ihn auf x zu legen hiesse, eine Zahl an einem anderen Querschnitt
anzusetzen als der Benutzer gemeint hat. Eine stillschweigende Milderung ist
genau das, was ein Nachweiswerkzeug nicht tun darf -- die Regel steht seit der
Rissanforderung im Code und gilt auch hier.

### Nebenbei

`Protokoll.alle_bloecke()` war ein Generator. Ein Test lief zweimal darüber:
beim zweiten Mal kam nichts, lautlos, und die Prüfung meldete «nicht
gefunden», obwohl es dastand. Ein Name, der eine Sammlung verspricht, muss
zweimal dasselbe liefern -- jetzt ist es eine Liste.

---

## 2026-09-21 · Die Abkürzung, die die Suche zweimal fand

Die Bewehrungssuche darf jetzt leere Lagen bewehren -- vorher blieb, was auf
null stand, auf null. Das war zu vorsichtig: wer die Bewehrung ermitteln
lässt, will wissen, *wo* welche hingehört. Dazu ein Mindestdurchmesser, damit
kein Stab dünner wird als das, was man verlegen will; null bleibt erlaubt,
denn eine Lage ganz wegzulassen ist eine gültige Antwort.

Damit kam ein Fallstrick, und zwar ein hübscher: **die Menge der Nachweise
hängt an der Bewehrung.** Nimmt man allen Stahl weg, gibt es keine Lage mehr,
der ein Nachweis gälte -- und kein Nachweis heisst Rückstand null. Die Suche
hat das sofort gefunden und mir stolz eine Platte ohne jede Bewehrung als
«alle Nachweise erfüllt» zurückgegeben.

Der erste Anlauf war eine Schranke beim Annehmen: weniger Urteile als die voll
bewehrte Platte, also kein Ergebnis. Das reichte nicht, denn gesucht wird ja
auch *unterwegs*: der nächste Schritt geht dorthin, wo der Rückstand am
kleinsten ist, und das war wieder der Zustand mit den wenigsten Nachweisen.
Jetzt gibt es eine einzige Zahl, an der sich alles ausrichtet: Rückstand plus
ein voller Punkt für jeden Nachweis, den es gar nicht gibt. Ein Nachweis, der
sich nicht einmal aufstellen lässt, ist so schlecht wie einer, der bei null
steht.

Zwei weitere Unstimmigkeiten fielen dabei auf. Erstens hat die Suche nie
wieder hinunter gerechnet: der Aufstieg nimmt in jeder Runde den Schritt, der
am meisten bringt, und der kann über das Ziel hinausgehen. «Die kleinste
Bewehrung» war damit eine Zusage, die das Werkzeug nicht hielt. Jetzt folgt
ein Abstieg, Stufe um Stufe, solange alles aufgeht.

Zweitens räumte die Arbeitskopie die Platte leer -- richtig, denn das Werkzeug
*ermittelt* die Bewehrung und legt nicht zu dem dazu, was zufällig dasteht --,
aber `uebernehmen` schrieb nur die gesuchten Posten zurück. Bei einer Platte
mit vorhandener Zulage blieb die stehen: gerechnet war die Grundbewehrung
ohne sie, eingebaut war sie mit. Die Lösung enthält jetzt jeden Posten, die
nicht gesuchten ausdrücklich mit null.

Dazu eine Reihe kleinerer Sachen an der Oberfläche: der Reiter
Spannung-Dehnung ist weg, seine Bilder stehen bei den Diagrammen, und dort
lässt sich einstellen, wie viele Blätter nebeneinander stehen. Die
Plus-Knöpfe sind unter ihre Listen gewandert und sehen aus wie Knöpfe. Die
Analysezeilen beschriften ihre Zahlenfelder je nach Art. Und der Knicknachweis
zeigt im M-N-Diagramm drei Punkte statt zwei: Einwirkung 1. Ordnung, am
verformten System, und den Widerstand bei N_Rd -- der liegt auf der
Resistenzlinie, denn dort steht der Stab an seiner Grenze.

## 2026-09-21 · Luft, und ein Umbruch, der auf die falsche Zahl sah

Aufräumen an der Oberfläche: mehr Abstand zwischen den Tafeln, mehr zwischen
den Kapiteln, und Kapitel, die überall gleich aussehen.

Der Abstand zwischen zwei Tafeln entsteht nicht am Griff, sondern in den
Tafeln selbst -- jede gibt auf der Seite nach, an der eine andere steht. So
bleibt der Griff schmal und greifbar, und der Inhalt hat trotzdem Luft.

Bei den Kapiteln fiel auf, dass «Platte» keine Linie links hatte und
«Nachweise» schon: die Linie hing an `.unterkapitel`, und die Platte hat
keines. Statt sieben Aufrufstellen um einen Körper-Container zu erweitern,
sitzt die Linie jetzt an der Gruppe selbst, und die Überschrift holt sich die
Einrückung mit einem negativen Rand zurück. Eine Regel statt sieben Eingriffe.
Die Unterkapitel wurden dafür zu Karten wie die Bewehrungslagen -- bei fünf
Nachweiskapiteln untereinander sah man vorher nicht, wo eines aufhört.

Das Padding hat dann etwas ans Licht geholt, das schon länger schief lag: der
Editor klappt in zwei Spalten auf, und der Umbruch hing an einer
`@media`-Abfrage -- also an der **Fensterbreite**. Das ist die falsche Zahl.
Die Tafeln sind in der Breite verstellbar; ein breites Fenster sagt nichts
darüber, wie viel Platz eine einzelne Tafel hat. Bei 1600 px Fenster und
420 px Tafel klappte der Editor zweispaltig auf und lief um 200 Pixel über.
Jetzt entscheidet eine `@container`-Abfrage, und sie sieht die Tafel.

Danach blieben 15 Pixel übrig, und auch die hatten einen Grund: die
Einwirkungszeilen standen auf `1fr` für den Namen. Ohne `minmax(0, 1fr)` nimmt
ein Gitter die Mindestbreite des Inhalts, und die Zeile wächst über die Karte
hinaus, statt den Namen zu kürzen.

Der Knopf «Bewehrung ermitteln» hat seine Meldung verloren. Das Ergebnis steht
danach in den Lagen und in der Zusammenfassung -- ein Satz daneben sagte
dasselbe ein zweites Mal und blieb stehen, bis man etwas anderes tat. Geht es
nicht auf, meldet es die Zeile oben rechts, dort, wo auch sonst steht, was
schiefging. Aus der Map mit Meldungen wurde ein Set mit Kennungen: der Knopf
muss nur noch wissen, ob er gerade läuft.

Dabei fiel eine Unstimmigkeit auf: eine neue Platte zeigte ein leeres
Teilungsfeld, während der Kern mit 150 mm rechnete. Was man sieht, muss
laufen -- die Vorgaben stehen jetzt auch in der neu angelegten Platte.

## 2026-09-21 · Den Querschnitt ansehen, ohne ihn nachzuweisen

Die Spannung-Dehnung-Analyse ist das erste Stück in diesem Werkzeug, das
nichts nachweist. Es gibt keinen Erfüllungsgrad und kein Urteil — gefragt
wird, was im Querschnitt eigentlich geschieht. Darum läuft sie auch nicht im
Rechenwerk: sie hat kein Ziel, das jemand anderes brauchen könnte, und nichts
hängt von ihr ab.

Drei Fragen an dasselbe Faserintegral. Aus N und M die Dehnungsebene — das
ist der Löser, wie ihn die Nachweise benutzen. Aus den Randdehnungen die
Kräfte — das ist die Umkehrung und braucht gar keine Suche, denn die Ebene
steht ja schon da. Und die Momenten-Krümmungs-Linie bei festgehaltener
Normalkraft.

Die dritte war die interessante. Unterhalb des Rissmoments ist der
Querschnitt ungerissen und deutlich steifer, als die Nachweise ihn rechnen —
dort wird der Beton auf Zug grundsätzlich nicht angesetzt. Für eine
Verformungsbetrachtung wäre das falsch herum: man bekäme eine Krümmung, die
es bei kleinen Momenten gar nicht gibt.

Der naheliegende Weg wäre eine zweite Formel gewesen, `χ_I = M/(E·I)` mit dem
Trägheitsmoment des ideellen Querschnitts. Stattdessen läuft derselbe Löser
ein zweites Mal, und es wechselt genau ein Stück: das Betongesetz. Zustand I
nimmt Zug linear auf, Zustand II gar nicht; alles andere — Höhe, Breite,
Lagen, Stahlgesetz, Suchfenster — ist dasselbe Objekt. Eine zweite Formel
wäre eine zweite Wahrheit über denselben Querschnitt gewesen, und sie hätte
ihre eigenen Annahmen über die Mitwirkung des Stahls mitgebracht.

Beim Zeichnen stolperte ich über die Höhenachse. Der Löser rechnet mit einem
`z`, das ich für «von der Unterkante» gehalten hatte — bis die 1. Lage bei
z = 261 mm auftauchte und die 4. bei 36. Es ist der Abstand von der
*gedrückten* Randfaser, also von oben. Ein Bild mit der anderen Annahme wäre
nicht falsch gewesen, sondern auf dem Kopf, und hätte neben dem Nachweis
gestanden wie ein Widerspruch. Jetzt prüft ein Test die Richtung: positives
Moment heisst unten gezogen, und die 1. Lage liegt unten.

Die Zusage der Tests ist nicht, dass eine Zahl stimmt — die kommt aus
demselben Integral wie die Nachweise und ist dort geprüft. Geprüft wird, dass
die drei zueinander passen: aus N und M eine Ebene, aus deren Randdehnungen
wieder N und M. Und dass die eigenständig gesuchte Grenze der Linie dasselbe
`M_Rd` ist, das im M-N-Nachweis steht.

## 2026-09-20 · Der Knopf, den man zweimal drücken musste

Ein Druck auf «Bewehrung ermitteln» tat nichts, der zweite zeigte das
Ergebnis des ersten. Die Suche lief also -- nur sah man sie nicht.

Der Zustand der Meldung liegt ausserhalb des Projekts, in einer Map neben der
Tafel: sie beschreibt einen Vorgang und keine Eigenschaft der Platte. Damit
sie sichtbar wird, muss nach dem Eintragen jemand neu zeichnen, und das hing
am Zweig: bei Erfolg tat es `projektAendern`, bei Misserfolg ein eigener
Aufruf. Der Erfolgszweig zeichnete aber schon *vor* dem Eintragen der Meldung
-- übernommen wurde das Projekt, und das löst für sich ein Neuzeichnen aus.
Danach stand die Meldung im Speicher und niemand fragte mehr danach. Erst der
nächste Druck zeichnete neu, und zwar als Erstes: also sah man das alte
Ergebnis.

Jetzt steht das Neuzeichnen in einem `finally`. Zuletzt und immer, egal
welcher Zweig gelaufen ist. Das ist die Art Stelle, an der eine
Fallunterscheidung sich rächt, die es gar nicht hätte geben müssen.

Dazu drei Dinge am Bild. Die Schalter stehen jetzt in jedem Kapitel ganz
links, wie bei den Tragsicherheitsnachweisen -- das Auge sucht die Spalte
einmal und findet sie danach wieder. Zwischen den Nachweiskapiteln ist Luft;
innerhalb bleibt es eng. Und das Werkzeug steht unter der Platte statt neben
ihr: es liest deren Angaben und schreibt in die Spalte daneben.

Beim Umstellen fiel auf, dass es die Lagenzeile dreimal gab -- einmal für die
Duktilität, einmal für das spröde Versagen, einmal für die Zwängung auf
Biegung. Dieselben zwanzig Zeilen, nur mit anderer Vorgabe. Jetzt baut
`lagenkapitel` alle drei; die Vorgabe ist ein Beiwert. Die Umstellung war
danach eine Stelle statt drei.

## 2026-09-20 · Zwei Fehler in einer Suche

Das Bewehrungswerkzeug fand für eine frische Platte mit h = 300 mm nichts. Es
steckten zwei Fehler darin, und keiner war der, den ich vermutet hatte.

**Der erste war die Zielgrösse.** Gemessen habe ich den Fortschritt am
*schlechtesten* Erfüllungsgrad: nimm den Schritt, der ihn am weitesten hebt.
Das klingt vernünftig und hat eine Lücke. Halten zwei Nachweise das Minimum
gleichzeitig — sprödes Versagen in der 1. und in der 4. Lage, gleich bewehrt,
also gleich weit daneben —, dann hebt kein einzelner Schritt es, weil der
jeweils andere stehen bleibt. Die Suche sah eine Ebene und gab auf, obwohl der
nächste Durchmesser offensichtlich geholfen hätte. Gemessen wird jetzt die
Summe der Fehlbeträge, `Σ max(0, 1 − α)`. Die kennt keine Ebene: sie fällt,
sobald irgendein unerfüllter Nachweis besser wird, und ist null genau dann,
wenn alle aufgehen. Eine Zeile, und die ganze Kategorie ist weg.

**Der zweite war schlimmer und in den Tests unsichtbar.** Bewertet wurde das
*ganze Projekt*. Stand neben der gesuchten Platte eine andere, die aus eigenen
Gründen nicht aufging, trug deren Rückstand mit — und die gesuchte Platte
bekam die Schuld. In den Tests gab es immer nur eine Platte; in der
Oberfläche legt man eine zweite an, und schon findet die Suche nie wieder
etwas. Die Arbeitskopie enthält jetzt nur noch die eine Platte. Das ist
zugleich schneller, denn die anderen wurden bei jedem Schritt mitgerechnet.

Dazu die Entscheidung, die du getroffen hast: **die Duktilität bleibt
draussen.** Sie ist der einzige Nachweis, der durch mehr Bewehrung schlechter
wird — er begrenzt die Druckzonenhöhe, und die wächst mit der Stahlfläche.
Eine Suche, die von unten aufsteigt, hat gegen ihn kein Mittel ausser
aufzugeben. Abgeschaltet wird er nicht beim Bewerten, sondern in der
Arbeitskopie, gleich neben den Lastfällen: gebaut wird nur, was eingeschaltet
ist, und gezählt wird, was gebaut wurde. An dieser Regel soll die Suche nichts
vorbeischmuggeln. Verschwiegen wird er trotzdem nicht — nach dem Fund läuft
er einmal mit, und das Ergebnis sagt, ob er aufgeht.

Und ein Nein soll sagen, warum. «Mehr Stahl bringt nichts» ist richtig und
hilft niemandem, wenn es in der Richtung gar keinen Stahl gibt, den man
vergrössern könnte. Ist eine ganze Tragrichtung unbewehrt, steht das jetzt
dabei.

## 2026-09-20 · Was vom letzten Lauf noch gilt

Bisher rechnete jede geänderte Zahl alles neu: Materialien, alle Platten, das
ganze Protokoll. Bei einer Platte sind das dreissig Millisekunden und es fällt
niemandem auf. Bei vier Platten hundertzwanzig, bei einer Platte mit
Knicknachweis anderthalb Sekunden — und dann fällt es auf.

Gemessen zuerst, und die Messung war eindeutig: `Projekt.aufbauen()` kostet
0.4 ms, das Lösen 30 ms. Bauen ist gratis, Lösen ist alles, und es skaliert
linear mit der Zahl der Platten. Also muss man nicht den Aufbau
zwischenspeichern, sondern das Ergebnis.

Das Rechenwerk konnte das nicht selbst. Innerhalb eines Laufs ist es längst
sparsam — es rechnet nur, was die Ziele brauchen, und jeden Wert einmal. Was
ihm fehlt, ist das Gedächtnis *zwischen* zwei Läufen, und das kann es sich
nicht geben: es sieht einen fertigen Graphen und weiss nicht, welche Eingabe
jemand angefasst hat. Das weiss nur, wer die Beschreibung entgegennimmt.

Gebraucht wurde dafür genau ein neues Mittel: `loese(*ziele, bekannt=…)`.
Mitgebrachte Werte stehen im Zwischenspeicher, als wären sie eben gerechnet
worden — der Lauf geht über sie hinweg, ohne Rechnung und ohne
Protokollblock. Damit lassen sich mehrere Läufe aneinanderhängen: erst die
Baustoffe, dann Platte für Platte, und die Herleitung liest sich am Ende wie
aus einem Guss.

Die eigentliche Frage war die Körnung. Verlockend wäre je Nachweis gewesen:
einen Duktilitätsschalter umlegen und den Knicknachweis stehen lassen. Das
geht nicht, und der Grund ist unangenehm konkret — die Nachweise tragen ihre
Lastfälle im Bauch, nicht in ihren Bezügen. Ein Knickfall mit geänderter
Normalkraft hat denselben Bezugsgraphen und dieselben Ausgabekennungen wie
vorher. Ein feiner Abdruck sähe keinen Unterschied und gäbe ein falsches
Ergebnis heraus, ohne dass irgendwo etwas auffiele.

Also grob: der Abdruck einer Platte ist ihr ganzer JSON-Eintrag plus *alle*
Materialien. Nicht nur die verwendeten — ein Vergleich, der erst auflösen
müsste, welche Kennung wohin zeigt, wäre genau die Stelle, an der man eines
vergisst. Die Regel dahinter: lieber zu viel verwerfen als zu wenig. Ein
Abdruck, der eine Änderung übersieht, liefert falsche Zahlen; einer, der zu
oft verwirft, kostet Zeit. Von beiden Fehlern ist nur einer hinnehmbar.

Eine Überraschung gab es doch. Ein übernommenes Bauteil besteht nicht nur aus
Zahlen: die Nachweise merken sich beim Rechnen einiges, was die Schnittstelle
später ausliest — Interaktionslinien, Fallergebnisse, Iterationsschritte.
Hätte man nur die Werte aufbewahrt, stünde die Zusammenfassung da und das
Diagramm wäre leer. Also wandern die Nachweis*objekte* mit.

Die Zusage ist nicht «schneller», sondern «gleich». Der Haupttest fährt acht
Änderungen durch — Dicke, Moment, Betonsorte, Stabdurchmesser, ein Schalter,
eine Knicknormalkraft, eine gelöschte Platte — und hält jedes Mal die Antwort
mit warmem Speicher gegen die aus dem Kalten. Zeichen für Zeichen dieselbe.
Ein Werkzeug, das je nach Vorgeschichte verschiedene Zahlen zeigt, wäre
schlimmer als ein langsames.

Vier Platten, gemessen: erster Lauf 131 ms, unverändert 6 ms, eine von vier
geändert 38 ms.

## 2026-09-20 · Suchen statt setzen

Das automatische Bewehrungswerkzeug war das letzte offene Stück, und es fing
mit einer Frage an: lässt sich die Bewehrung nicht einfach ausrechnen?

Für einen einzelnen Nachweis ja. Für alle zusammen nicht, und der Grund ist
der Duktilitätsnachweis: er wird durch *mehr* Stahl schlechter, alle anderen
besser. Zwischen beiden liegt ein Fenster, und ob es offen ist, weiss man
erst, wenn man hineingeschaut hat. Also wird gesucht.

Gestiegen wird von unten. Alle Posten auf den kleinsten Durchmesser, dann
Runde für Runde: jeden Posten einzeln einen Schritt grösser probieren und den
nehmen, der den schlechtesten Erfüllungsgrad am weitesten hebt. Der Schritt
wird ausprobiert und nicht geraten — eine Regel der Art „bei einem
Momentenversagen die Zuglage verstärken" liefe beim Duktilitätsnachweis
genau verkehrt. Bei dreissig Millisekunden je Rechnung ist Ausprobieren der
günstigere Handel.

Welche Nachweise zählen, musste nirgends aufgeschrieben werden: gebaut wird
nur, was eingeschaltet ist, und gezählt wird, was gebaut wurde. Die Schalter
in der Maske steuern die Suche damit unmittelbar. Eine zweite Liste hätte es
hier nur gegeben, um mit der ersten auseinanderzulaufen.

Der Knicknachweis stellte sich quer. Er kostet je Rechnung Sekunden statt
Millisekunden, weil er N_Rd durch Halbieren sucht und jede Probekraft eine
eigene Ausmitten-Iteration nach sich zieht. Ein Suchlauf mit einer Stütze
brauchte Minuten. Die Abkürzung: während der Suche entfällt die Halbierung.
Erfüllt oder nicht kommt gleich heraus — N_Rd ≥ |N_Ed| gilt genau dann, wenn
der Querschnitt bei N_Ed das Moment zweiter Ordnung aufnimmt. Nur die Zahl
daneben ist eine andere. Dafür gibt es einen Test, der beides gegeneinander
hält.

Beim Knicken selbst hat sich vorher schon etwas Grundsätzliches geändert.
Verglichen wurden M_Rd und M_Ed,II, und das geht nur, solange es ein
Gleichgewicht gibt. Beim Knicken fehlt gerade das: ein kippender Stab hatte
kein Moment und darum kein Urteil, sondern einen Satz. Jetzt ist der
Erfüllungsgrad N_Rd/|N_Ed| — die Normalkraft hat immer einen Grenzwert.

Die Ausmitten-Iteration steht seither vollständig in der Herleitung. Das ist
der Unterschied zur Nullstellensuche im Faserlöser: dort ist die Halbierung
ein Weg zu einem Rechenschritt, hier ist die Folge der Rechenschritt selbst.
Dass sie einläuft, *ist* die Aussage des Nachweises — und das sieht man nur,
wenn man die Folge sieht.

## 2026-09-18 · Was `b` eigentlich bedeutet

Eine Platte hatte bisher eine Breite, und die galt für alles. Das ist so lange
richtig, wie sie 1000 mm ist — und das ist sie fast immer, weshalb der Fehler
lange keiner war.

Er wird einer, sobald jemand 2000 mm einträgt. Die Angabe `b` beschreibt einen
Streifen in x-Richtung: so breit ist das Stück Platte, über das die x-Bewehrung
gezählt wird. Die y-Bewehrung liegt quer dazu. Ihre Teilung ist auf den
Laufmeter bezogen und hat von `b` nie etwas mitbekommen. Wer trotzdem mit `b`
rechnet, bekommt in y aus derselben Bewehrung den doppelten Widerstand.

Also gibt es jetzt zwei Breiten. `b` ist die Eingabe, `b_y` ist festgelegt auf
1000 mm — und steht trotzdem als Vorgabe im Protokoll, neben `b` im selben
Kasten. Eine stille Festlegung wäre genau die Art Zahl, die man später in
keiner Herleitung wiederfindet und dann für einen Rechenfehler hält.

`Plattenquerschnitt.id_breite(richtung)` gibt die passende Kennung heraus, und
jeder richtungsbehaftete Nachweis fragt dort nach statt bei `id_von("b")`. Der
Lagenaufbau wählt je Posten, aus welcher Breite die Fläche kommt. Beim
Duktilitätsnachweis war es zuerst nicht offensichtlich, dass er das überhaupt
braucht: `x/d` ist von der Breite unabhängig, weil `x = A_s·f_sd/(b·f_cd)` sie
herauskürzt. Unabhängig ist es aber nur, wenn `A_s` und `b` aus *derselben*
Richtung stammen. Genau darauf prüft einer der neuen Tests.

Das Bewehrungsmass war der einzige Ort, an dem beide Richtungen zusammenlaufen.
Es rechnet jetzt jede Lage über `b/b_q` auf denselben Streifen um. Bei gleicher
Breite ist das die schlichte Summe wie bisher — die Zahl für den Regelfall
ändert sich nicht.

Acht Tests in `tests/test_breite_je_richtung.py`, alle als Verhalten formuliert:
`b` verdoppeln, und dann muss in x alles mitgehen und in y nichts. Absolute
Zahlen stehen dort keine; sie wären nur eine zweite Stelle, an der dieselbe
Formel steht.

## 2026-09-18 · Ein Löser für Dehnungsebenen, und was darauf steht

Vier Nachweise in einem Zug — und der Grund, warum sie zusammengehören: sie
brauchen alle dieselbe Frage beantwortet. *Welche Dehnungsebene hält diesen
Querschnitt unter (N, M) im Gleichgewicht?*

### Sprödes Versagen war der falsche Nachweis

Der Nachweis mit `σ_s,adm` gab vor, gegen sprödes Versagen zu schützen, tat
aber etwas anderes: er begrenzt die Stahlspannung aus einer aufgezwungenen
Krümmung. Und er war nicht einmal konservativ — bei normaler Anforderung liegt
`M_s,adm` rund 10 % **über** `M_Rd`, weil `f_yk/f_yd = 1.15` den kleineren
Hebelarm des gerissenen Querschnitts mehr als aufwiegt.

Jetzt sind es zwei Nachweise:

* **Sprödes Versagen**: `M_Rd(N_Ed = 0) ≥ M_Riss` — trägt der bewehrte
  Querschnitt mehr als der unbewehrte im Augenblick des Risses?
* **Zwängung auf Biegung**: `σ_s ≤ σ_s,adm` — hält die Bewehrung die Spannung
  aus, die eine aufgezwungene Krümmung erzeugt?

Dafür läuft der M-N-Nachweis jetzt für jede bewehrte Richtung, auch ohne
Schnittgrössen: seine Eckwerte gehören dem Querschnitt, nicht der Einwirkung.

### Der Querschnittslöser

Mit Normalkraft gibt es keine geschlossene Lösung. Zwei Unbekannte, zwei
Gleichgewichtsbedingungen, nichtlineares Betongesetz. `scipy.optimize.fsolve`
kam nicht in Frage — das Werkzeug läuft auch im Browser über Pyodide.

Zwei geschachtelte **Bisektionen**: bei festem `χ` wächst `N(ε_m)` monoton,
also ist `ε_m` eindeutig bestimmbar; damit wird `M` eine Funktion von `χ`
allein, und die äussere Bisektion sucht darin die Krümmung. Kein Startwert kann
danebenliegen, kein Newton-Schritt davonlaufen.

**Der Fehler, der mich aufgehalten hat:** ich suchte zuerst über `ε ∈ [−0.5,
0.5]`. Jenseits der Bruchdehnung geben beide Werkstoffgesetze null zurück —
dort ist nichts mehr monoton, und die Bisektion sah bei `ε = −0.5` dieselbe
Normalkraft wie bei 0. Nichts konvergierte. Das Suchfenster für `ε_m` hängt
jetzt von `χ` ab und bleibt im gültigen Bereich beider Gesetze.

Gemessen an der geschlossenen Lösung des Zustands II trifft der Löser die
Stahlspannung auf 0.01 % (183.60 gegen 183.58 N/mm²).

### Was in die Mitschrift gehört

Nicht die Suche, sondern die **Probe**: die gefundene Ebene und der Nachweis,
dass mit ihr `N_int = N_Ed` und `M_int = M_Ed` herauskommt. Wer das nachrechnen
will, integriert zwei Mal über die Höhe — das geht von Hand. Den Weg dorthin
muss er nicht nachvollziehen. Dasselbe Vorgehen wie bei der Neigungssuche des
Querkraftnachweises.

### Spannungsbegrenzung und Knicken

**Spannungsbegrenzung**: je häufigem Lastfall die Stahlspannung im gerissenen
Querschnitt gegen `f_yd − 80 MPa` (Tabelle 17). Nur bei erhöhter und hoher
Anforderung — bei normaler steht dort ein Strich. Gezählt wird nur gezogene
Bewehrung.

**Knicken**: die Ausmitten-Iteration am verformten System. Läuft die Folge ein,
gibt es eine Gleichgewichtslage; wächst sie, knickt das System. Das ist die
eigentliche Aussage: nicht erfüllt heisst hier **nicht** «eine Spannung ist
überschritten», sondern «es gibt gar kein Gleichgewicht». Danach muss der
Querschnitt das Moment zweiter Ordnung noch aufnehmen.

Nur in x-Richtung: eine Knicklänge gehört zu einer Tragrichtung, und in y wäre
die Breite der Platte die Länge.

### Maske

Vier Kapitel statt zwei, jedes mit Lagenschaltern im selben Stil — dreimal
dieselben zwanzig Zeilen wären dreimal dieselbe Gelegenheit auseinanderzulaufen,
darum baut `lagenkapitel()` sie alle. Jeder Tragsicherheitsfall hat einen
Ein/Aus-Schalter; ausgeschaltet bleibt er blass stehen, statt gelöscht zu
werden. Dazu das Panel *Spannung-Dehnung* — leer, mit einem Satz dazu, was
dorthin gehört.

---

## 2026-09-18 · Sprödes Versagen unter Biegung, und der gerissene Querschnitt

```
k_t      = 1/(1 + 0.5·h/3)                 h in Metern, immer die ganze Dicke
M_Riss   = k_t·f_ctm · h²·b/6              ungerissener Bruttoquerschnitt
M_s,adm  = σ_s,adm · A_s · z  ≥  M_Riss    gerissener Querschnitt
```

**Zwei verschiedene Querschnitte in einem Nachweis** — und das ist kein
Versehen, sondern die Frage selbst: das Rissmoment gehört dem Zustand *vor*
dem Riss, der Widerstand dem Augenblick *danach*. Reicht die Bewehrung für
das, was der Beton abgibt? Die Stelle ist in der Herleitung mit einem Satz
erklärt, weil man dort sonst stolpert.

### Der Hebelarm kam nicht aus einem plastischen Ansatz

Naheliegend wäre `A_s·f_yk = x·b·f_cd/2`, dann `M = σ_s,adm·A_s·z`. Das mischt
aber drei Sicherheitsniveaus (f_yk, f_cd, σ_s,adm), und das `x` gehört zu einer
Spannung, die gar nicht herrscht. Unmittelbar nach dem Riss ist der Querschnitt
im **Zustand II**: gerissen, beide Baustoffe elastisch, Gebrauchsspannungen.

Dort hängt `x` überhaupt nicht von der Last ab — alles ist linear, die
Nulllinie ist eine reine Querschnittseigenschaft:

```
ρ = n·A_s/b
x = √(ρ² + 2·d·ρ) − ρ
z = d − x/3
```

Das `x/3` ist die Stelle, an der man sich vertut: die Betondruckspannung
verläuft dreieckig mit dem Maximum an der gedrückten Kante, ihre Resultierende
liegt also bei `x/3` **von dieser Kante**, nicht bei `2x/3`.

### Kriechen ist immer konservativ — bewiesen, nicht vermutet

`n = (E_s/E_cm)·(1+φ)`; die Klammer ist wesentlich, `E_s/(E_cm·(1+φ))` wäre das
Gegenteil. Ob ein grösseres φ nun günstig oder ungünstig ist, lässt sich
ausrechnen statt raten:

```
dx/dρ = (ρ+d)/√(ρ²+2dρ) − 1 > 0,  denn (ρ+d)² − (ρ²+2dρ) = d² > 0
```

Grösseres n gibt also immer grösseres x, kleineres z, kleineres `M_s,adm` — für
**jede** Geometrie. Ein Test rechnet das über drei Bewehrungsgrade und drei
statische Höhen nach, damit die Aussage nicht an einem Zahlenbeispiel hängt.
Damit braucht es keine Fallunterscheidung: gerechnet wird mit dem eingegebenen
φ, Vorgabe 2.0.

### Zustand II als eigener Baustein

`nachweis/zustand2.py` — 80 Zeilen, zwei Funktionen. Der Grund steht im Kopf
der Datei: die Spannungsbegrenzung unter häufiger Einwirkung braucht dieselbe
Nulllinie, und zwei Rechenwege für dieselbe Grösse laufen auseinander. Das ist
in diesem Werkzeug schon zweimal passiert.

### E_cm gab es längst

Ich hatte angefangen, eine Spalte `E_cm` in die Sortentabelle zu schreiben — und
dabei den bestehenden Kennwert überschrieben. Er wird schon hergeleitet, aus
`k_e · f_cm^(1/3)`, und steht damit in der Mitschrift. Für C30/37 gibt das
33 620 N/mm². Die Tabellenspalte ist wieder weg.

### Der Nachweis läuft ohne Schalter

Anders als Duktilität und Zwängung: sprödes Versagen unter Biegung geht jede
Platte an, unabhängig von Einwirkung und Zwang. Damit gibt es keinen Zustand
mehr, in dem die Zusammenfassung leer bleibt — vier Zeilen je Platte kommen
immer.

---

## 2026-09-18 · Sprödes Versagen unter Zwängung

Der erste der Mindestbewehrungsnachweise. Er fragt nicht nach Tragfähigkeit,
sondern danach, ob sich das Versagen ankündigt: ein zu schwach bewehrter
Querschnitt reisst und bricht im selben Augenblick.

```
h_eff    = min(500 mm; h)  falls begrenzt, sonst h
k_t      = 1/(1 + 0.5·h_eff)               h_eff in Metern
f_ct,eff = k_t · f_ctm
N_Riss   = h_eff/2 · b · f_ct,eff
N_s,adm  = A_s · σ_s,adm  ≥  N_Riss
```

Zwei Urteile je Tragrichtung — die untere **und** die obere Lage. Ein Zwang
kennt keine Zugseite; er beansprucht den Querschnitt über die ganze Höhe.

### f_yk, nicht f_yd

Die zulässige Stahlspannung geht von der **charakteristischen** Fliessgrenze
aus. Das ist kein Versehen: nachgewiesen wird nicht die Tragfähigkeit, sondern
dass die Bewehrung den Riss überlebt. Bei erhöhter und hoher Anforderung
begrenzt zusätzlich die nominelle Rissbreite:

```
σ_s,adm = min[ √(9·E_s·f_ctm·w_nom / ⌀) ; f_yk ]
```

Dimensionell stimmig: `E_s·f_ctm` gibt Pa², `w_nom/⌀` ist dimensionslos, die
Wurzel also eine Spannung. Massgebend ist der **dickste** Stab der Lage — er
verteilt den Riss auf die wenigsten Stäbe und bekommt damit die grösste
Spannung.

### Eine leere Lage fällt nicht durch, sie meldet sich

Ohne Bewehrung wäre `⌀ = 0` und die Wurzel undefiniert. Statt dort eine Null zu
erfinden, gibt es ein Urteil ohne Einwirkung und Widerstand plus den Grund —
dasselbe Muster wie beim Duktilitätsnachweis und bei der unbewehrten
Tragrichtung.

---

## 2026-09-18 · Die Übersicht liest sich jetzt wie ein Schnitt

Die Bewehrungsübersicht lief von unten nach oben — untere Überdeckung, 1. bis
4. Lage, obere Überdeckung. Die Eingabemaske stapelt umgekehrt, wie man die
Platte im Schnitt sieht. Zwei Folgen für dieselbe Sache nebeneinander: jetzt
läuft auch die Tabelle von oben nach unten, die Bügel bleiben als eigene Zeile
am Ende.

Die Bügelzeile trug ausserdem die ganze Herleitung mit sich:

```
⌀_V = 6 mm   s_V,x = 200 mm   s_V,y = 200 mm   A_⌀,V = 28.3 mm²
```

In einer Übersicht ist das Ballast — und der Bügelquerschnitt steht ohnehin in
der Herleitung, wo er auch hergeleitet wird. Jetzt dieselbe Kurzform wie bei
den Lagen: `⌀6@200@200`, Durchmesser und die beiden Teilungen. Damit fällt auch
die letzte Stelle weg, an der `A_⌀,V` ein zweites Mal aus der Lösung geholt
wurde; `_bewehrungsuebersicht` braucht die Lösung gar nicht mehr.

---

## 2026-09-18 · Ein Gradzeichen ohne Basis, und eine Richtung ohne Zeile

### `\,^{\circ}` bringt KaTeX zu Fall

Die Einheit *Grad* trug das LaTeX `^{\circ}`, und `Einheit.als_latex()` setzt
allem einen schmalen Abstand voran. Heraus kam `30\,^{\circ}` — ein Exponent
**ohne Basis**. KaTeX bricht daran ab und zeigt statt der Formel den rohen
Quelltext, und zwar für den ganzen Kasten:

```
s_{V,x} = 300\,\mathrm{mm} \qquad \alpha_{min} = 30\,^{\circ} \qquad …
```

Die leere Gruppe ist die fehlende Basis: `{}^{\circ}`. Dazu hat `Einheit` jetzt
ein Feld `klebt` — das Gradzeichen gehört an die Zahl, nicht hinter einen
schmalen Abstand. `30°`, nicht `30 °`.

### Der Kasten war zerrissen

Im gemeldeten Text fehlte `⌀_V`. Der Grund: **die Reihenfolge der Eingänge ist
die Reihenfolge der Blöcke.** Der Querkraftnachweis forderte `A_{⌀,V}` vor den
übrigen Bügelangaben an; der Löser beschaffte dafür zuerst den Durchmesser,
schrieb dann die Flächenformel — und die stand mitten zwischen den fünf
Vorgaben, die in *einem* Kasten stehen sollen. `gruppenBilden` legt nur
aneinandergrenzende Blöcke zusammen, also wurden es zwei.

Behoben, indem `a_s_V` in der Bezugsliste ans Ende wandert. Das ist eine
stille Abhängigkeit — die Bezugsreihenfolge sah bisher wie eine Geschmacksfrage
aus — und steht jetzt als Kommentar an der Stelle.

### Eine unbewehrte Tragrichtung stand gar nicht da

Wer eine Einwirkung in y-Richtung angab, ohne dort Bewehrung zu haben, fand sie
in der Zusammenfassung nirgends wieder: `richtungen_mit_bewehrung` liess die
Richtung aus, und damit entfiel der Nachweis stillschweigend. Ein leerer Platz
liest sich aber wie *geprüft und in Ordnung*.

Ohne Stahl ist der Momentenwiderstand der Handrechnung **null** — nicht das,
was der Beton allein noch aufnähme (siehe den Eintrag zur präzisen
Resistenzlinie: der Unterschied ist erheblich). Der neue Baustein
`FehlendeBewehrung` rechnet darum nichts, sondern meldet: Widerstand null,
Erfüllungsgrad null, nicht erfüllt, mit Grund. Dass er nichts rechnet, ist
Absicht — ein Baustein, der hier eine Zahl herleitete, käme früher oder später
auf die Betondruckfestigkeit und damit auf einen Widerstand aus dem Nichts.

Der Querkraftnachweis fällt aus demselben Grund aus und bekommt dieselbe
Behandlung: ohne Bewehrung keine statische Höhe, also kein `V_Rd`. Nur die
M-N-Zeile zu zeigen hiesse, die Lücke halb zu schliessen.

Nebenbei: gleiche Gründe stehen unter der Tabelle jetzt in **einer** Zeile
zusammengefasst. Bei einer ganzen unbewehrten Richtung standen sonst sechsmal
derselbe Satz untereinander — das ist keine Erklärung mehr, sondern eine Wand.

---

## 2026-09-18 · Duktilität

Ein dritter Nachweis, und der erste, der nicht an einer Tragrichtung hängt,
sondern an einer **einzelnen Bewehrungslage**:

```
0.85 · x · b · f_cd = A_s · f_sd        (Kräftegleichgewicht, M_Ed = 0)
x / d ≤ 0.35
```

Eine flache Druckzone heisst: der Stahl fliesst lange, bevor der Beton versagt
— der Querschnitt kündigt sein Versagen an. Nachgewiesen wird darum kein
Widerstand, sondern ein Verhältnis. Als Erfüllungsgrad steht `0.35/(x/d)` da,
also wieder Widerstand/Einwirkung; damit passt er in dieselbe Spalte wie alles
andere.

### Das d muss man wählen

`d` gilt ab der **gedrückten** Randfaser. Bei den unteren Lagen ist das die
Oberkante (`d = z`), bei den oberen die Unterkante (`d = h − z`). Wer hier
stumpf `z` stehen liesse, bekäme bei den oberen Lagen eine Zahl, die keine
statische Höhe ist — genau der Fehler, der beim Querkraftnachweis einmal
`d = 39 mm` lieferte.

Grundbewehrung und Zulage liegen auf leicht verschiedenen Höhen, gehören aber
zur selben Lage: gerechnet wird mit ihrem gemeinsamen Schwerpunkt, und der steht
in der Herleitung.

### Eine eingeschaltete, aber leere Lage

Das ist kein Fehler der Beschreibung — es kann beim Umbewehren jederzeit
passieren. Der Nachweis läuft, fällt nicht durch mit einer erfundenen Null,
sondern liefert ein Urteil **ohne** Einwirkung und Widerstand (in der Tabelle
zwei Striche) und dazu den Satz, warum. Schon in der Maske steht «Lage nicht
definiert» neben dem Schalter.

### Der Hinweis ist jetzt ein Feld, keine Vermutung

Dafür habe ich zurückgenommen, was ich in der Runde davor gebaut hatte: die
Schnittstelle schloss aus «Widerstand = 0» darauf, dass etwas zu melden sei.
Das war geraten. `NachweisUrteil` hat jetzt ein Feld `hinweis`, das nur setzt,
wer etwas zu melden hat — die Prüfung weiss es ohnehin. Beim Duktilitätsnachweis
ist der Widerstand nämlich 0.35 und nicht null, die alte Regel hätte ihn
übersehen.

### Maske

Vier Zeilen unter den Tragsicherheitsnachweisen, je ein Schalter ✓/✗ im Stil der
x/y-Wahl, dazu die Tragrichtung der Lage in ihrer Farbe. Vorgabe sind die beiden
äusseren Lagen.

Nebenbei zwei Kleinigkeiten: die Kreuze an den Bewehrungsposten sind runde
Knöpfe mit hellrotem Grund geworden — als blosses Zeichen waren sie kaum zu
sehen und sahen nicht nach etwas Drückbarem aus. Und die Tragrichtung einer
Einwirkung ist kein Auswahlfeld mehr, sondern ein Schalter wie die übrigen: x
blau, y kupfer wie bei den Lagen, `x+y` in einem sanften Violett — der Mischung
aus beiden.

---

## 2026-09-18 · Querkraftbewehrung

Bis hierher konnte eine Platte nur ohne Bügel nachgewiesen werden. Jetzt trägt
sie ein Bügelraster: ein Durchmesser, eine Teilung in x, eine in y, ein eigener
Stahl, dazu die beiden Grenzwinkel der Druckdiagonalen und `k_c`.

### Zwei Ansätze, einer davon gilt

```
V_Rd,s = A_(⌀,V)/(s_V,x · s_V,y) · 0.9 · d · f_yd · cot α
V_Rd,c = 0.9 · d · k_c · f_cd · sin α · cos α
V_Rd   = max über α von min(V_Rd,s; V_Rd,c)
```

`V_Rd,s` wächst mit flacherer Diagonale, `V_Rd,c` fällt dabei — das Kleinere
von beiden hat sein Grösstes dort, wo sich die Äste treffen. Gesucht wird
ganzgradig zwischen `α_min` und `α_max`; Zwischenwerte wären eine Genauigkeit,
die das Fachwerkmodell nicht hergibt.

Ob dieser Ansatz läuft oder der bisherige, entscheidet **allein**, ob eine
Querkraftbewehrung da ist. Beides zu addieren wäre ein drittes Modell, und
dieses Werkzeug rechnet nur, was es auch herleitet. Mit Bügeln fordert der
Nachweis `m_Rd(N_Ed)` gar nicht mehr an — sonst hinge eine Interpolation in der
Herleitung, die dort nichts erklärt.

### Die Breite gehört nicht in die Formel

Vorgegeben war `V_Rd,c = b · 0.9 · d · k_c · f_cd · sin α · cos α`. Mit `b` darin
ist das eine **Kraft**, `V_Rd,s` dagegen eine Kraft **je Laufmeter** — die
beiden liessen sich nicht vergleichen. Bei den üblichen `b = 1000 mm` fällt es
nicht auf, weil der Faktor 1 ist; bei `b = 500 mm` wäre `V_Rd,c` um das Doppelte
zu gross. `b` steht deshalb in keiner der beiden Formeln: es ist der Bezug, auf
den sich alle Schnittgrössen ohnehin schon beziehen.

### Eine Stabzahl in y schliesst die y-Richtung aus

In y darf statt der Teilung eine Stabzahl über `b` stehen; daraus wird
`s_V,y = b/n`. In x-Richtung ergibt das eine saubere Teilung. Für einen Nachweis
**in** y-Richtung liefe die Breite längs der Traglinie mit, und die Formel hätte
keinen Bezug mehr — dort steht dann `V_Rd = 0` und der Grund dabei.

Daraus wurde eine allgemeine Regel: **ein Widerstand von null erklärt sich nicht
von selbst.** Steht in der Zusammenfassung `0.0 kN/m`, steht der Grund jetzt
sichtbar unter der Tabelle statt nur im Tooltip. Das betrifft auch den älteren
Fall «auf der gezogenen Seite liegt keine Bewehrung».

### Das Diagramm

Mit Bügeln hängt der Widerstand nicht mehr am Moment — die M-V-Kurve entfällt
und an ihre Stelle tritt der Verlauf über der Neigung: V_Rd,c orange, V_Rd,s
blau, darunter das massgebende Kleinere. Gezeichnet wird von 25° bis 45°, blass
ausserhalb der Grenzen; ein dort abgeschnittener Ast liesse offen, ob die Kurve
endet oder der Bereich. Bei Normalzug wächst die Achse mit, denn `α_min` springt
dann auf 40° und `α_max` notfalls hinterher.

**Ein Bild je statischer Höhe und Neigungsbereich.** Beides hängt am einzelnen
Fall: `d` am Vorzeichen des Moments, der Bereich am Vorzeichen der Normalkraft.
Fälle, die darin übereinstimmen, liegen auf derselben Kurve.

### Die Maske

Der Bügelblock steht unter den Lagen und hat einen grünen Akzent — die Bügel
tragen quer zu beiden Tragrichtungen, also weder blau noch kupfer. Die Zeile hat
eine Zahl mehr als eine Lagenzeile; damit sie in dieselbe Spaltenbreite passt,
fehlt ihr die Namensspalte. Ohne das lief die mittlere Tafel um 28 Bildpunkte
über.

Eine Beschreibung aus der Zeit vor den Bügeln kennt die Felder nicht. Die Maske
füllt sie deshalb beim ersten Anfassen mit genau den Werten, die der Kern
einsetzen würde — sonst stünde dort ein leeres Feld, während gerechnet wird.
Dieselbe Falle wie damals bei `h = 0`.

---

## 2026-09-18 · Nicht rechnen, was schon dasteht

Zwei Stellen, an denen die Mitschrift Arbeit vortäuschte, und eine, an der sie
sich auf eine Faustregel verliess.

### Der Bruch, der immer null war

Bei `N_Ed = 0` stand in der Herleitung:

```
M_Rd = M_1 + (N_Ed - N_1)/(N_2 - N_1) · (M_2 - M_1)
     = 142.5 + (0.0 - 0.0)/(910.6 - 0.0) · (27.9 - 142.5) = 142.5 kNm
```

Der Zähler ist null, weil `N_Ed` **genau** auf dem Eckpunkt liegt. Zu
interpolieren gibt es da nichts; die Zeile sieht nur so aus, als wäre etwas
gerechnet worden. Jetzt steht der Eckpunkt selbst da:

```
M_Rd = M_Rd(N_Ed=0)^+ = 248.7 kNm
```

Geprüft wird nicht auf `N_Ed == 0`, sondern darauf, ob die festgehaltene Grösse
einen Stützpunkt trifft. Damit fällt derselbe Fall auf der anderen Achse
gleich mit weg: bei `M_Ed = 0` und Normaldruck steht jetzt
`N_Rd = N_Rd^- = -6000.0 kN` statt einer Interpolation über eine Kante, auf der
sich nichts ändert. Mitgeprüft wird auch der Zielwert — bei einer Kante längs
der festgehaltenen Achse träfen sonst beide Stützpunkte zu, und nur einer davon
ist der Widerstand.

### Die Schwelle, die den günstigeren Wert stehen lassen konnte

Ob der Erfüllungsgrad am Momentenwiderstand (bei festgehaltener Normalkraft)
oder am Normalkraftwiderstand (bei festgehaltenem Moment) gemessen wird,
entschied eine Faustregel: ab 25 % der Grenzzugkraft bzw. 60 % der
Grenzdruckkraft senkrecht, sonst waagrecht. Zwei Zahlen, die niemand herleiten
konnte — und in der Nähe der Schwelle konnte die Regel den **grösseren** der
beiden Erfüllungsgrade auswählen, also den günstigeren.

Gerechnet werden jetzt beide, und es gilt der kleinere. Das ist kein
Rechenschritt, sondern die Festlegung, in welcher Richtung gemessen wird —
deshalb steht der Vergleich nicht in der Mitschrift, wohl aber vollständig,
was dann gerechnet wurde. Wer den Massstab selbst vorgibt, bekommt ihn
unverändert; sonst liesse sich ein Zwischenwert nicht mehr gezielt nachrechnen.

### Die Zusammenfassung sagte alles zweimal

Die Spalte *Urteil* schrieb «erfüllt» neben einen Erfüllungsgrad von 2.49. Sie
ist weg; hinterlegt wird stattdessen die Zahl selbst, weich grün oder weich
rot. Welche Spalte das ist, sagt der Kern (`grad_spalte`) — die Oberfläche soll
es nicht aus der Kopfzeile erraten.

Der Nachweis heisst jetzt `M-N: Feld` statt `M-N-Nachweis x – Feld`. Die
Richtung fehlt mit Absicht: sie steht im Symbol des Widerstands (`M_{Rd,x}`).
Zusammengesetzt wird der kurze Name aus zwei neuen Feldern des Urteils
(`art`, `fall`) und nicht aus dem langen herausgeschnitten — aus Anzeigetext
auf Bedeutung zu schliessen hat die Nachweise mehrerer Platten schon einmal in
dieselbe Tabelle gepackt.

Über der Tabelle stehen jetzt Beton, Dicke und Breite sowie die Bewehrung von
unten nach oben gelesen: untere Überdeckung, 1. bis 4. Lage, obere Überdeckung.
Beide kommen fertig aus dem Kern und sind in der Oberfläche eine gewöhnliche
Gleichung und eine gewöhnliche Tabelle — dieselbe Gestalt, dieselben
Kopierknöpfe wie alles andere.

`v_Rd` ist durchgehend `V_Rd` geworden, auch in der Herleitung. Gross in der
Tabelle und klein in der Formel wäre genau die Art Abweichung, die dieses
Werkzeug vermeiden will. Die Betragsstriche an `V_Ed` sind weg: die Zahl
daneben ist ohnehin der Betrag.

### Maske

Zahlenfelder tragen einen leichten blauen Akzent — sie sind das, was man
anfasst; Namensfelder und Auswahllisten bleiben unbunt. Vor jedem
Bewehrungsposten steht ein ×, das den Durchmesser auf null setzt; es ist nur
rot, solange es etwas zu entfernen gibt, bleibt aber auch sonst stehen, damit
die Zeile nicht bei jeder Eingabe um seine Breite springt.

Eine neue Platte bringt `D_max = 32 mm` mit — ohne Vorgabe stand das Feld leer
und der Querkraftnachweis meldete eine fehlende Eingabe. Bewehrt ist sie nur
noch aussen (1. und 4. Lage, ⌀12@150): was man nicht braucht, soll man
wegnehmen müssen und nicht wegnehmen dürfen. `D_max` steht in der Maske jetzt
mit echtem Index, dafür nimmt `feld()` neben Klartext auch Knoten entgegen.

---

## 2026-09-18 · Eine Änderung fiel unter den Tisch

Gemeldet: manchmal eine Zahl ändern, oben rechts steht «geändert …» — und es
geschieht nichts.

Der Riegel gegen doppeltes Rechnen warf den zweiten Wunsch weg:

```js
if (zustand.rechnetGerade) return;     // und damit war er fort
```

Das ist ein Riegel ohne Gedächtnis. Solange Pyodide rechnet, fällt er nie auf:
Python läuft im Hauptfaden, ein Durchgang ist ein einziger Arbeitsschritt, und
während dessen kann niemand tippen. Über den lokalen Server aber liegt ein
`await fetch` dazwischen — die Oberfläche bleibt bedienbar, und wer in diesen
gut 40 ms etwas ändert, dessen Änderung verschwindet. Nachgemessen im laufenden
Betrieb: zwei Änderungen, **ein** Rechengang, und angezeigt wurde danach das
Urteil zur *vorherigen* Zahl. Nicht bloss «es passiert nichts» — es stand eine
Antwort da, die nicht zur Eingabe gehörte.

Jetzt wird der jüngste Wunsch aufbewahrt und im Anschluss ausgeführt. Ältere
dürfen verfallen: gerechnet wird ohnehin immer mit der Beschreibung, wie sie
im Augenblick des Durchgangs aussieht.

```js
let auftrag = { ziele };
while (auftrag) {
  nachgereicht = null;
  await einDurchgang(auftrag.ziele);
  auftrag = nachgereicht;     // während des Rechnens dazugekommen
}
```

### Der Riegel gehörte in den Schutz von `finally`

Gesetzt wurde er vor dem `try`, und gesetzt wird er von `aendern()` — das
zeichnet alle drei Tafeln neu. Wäre dabei je ein Fehler gefallen, stünde der
Riegel für immer, und **jede** weitere Rechnung wäre gesperrt gewesen, auch die
von Hand angestossene. Ein Fehler beim Zeichnen hätte das Werkzeug stumm
gemacht. Er steht jetzt im `try`.

### «geändert …» sagte nicht die Wahrheit

Der verzögerte Durchgang lief `stillschweigend`, hat also die Anzeige nicht
angerührt — während gerechnet wurde, stand weiter «geändert …» da. Genau der
Eindruck, der gemeldet wurde. Das Kennzeichen ist ersatzlos weg; die Anzeige
geht jetzt «geändert …» → «rechnet …» → Urteil.

### Dieselbe Art Fehler unter dem Diagramm

Wer die Normalkraft zweimal kurz hintereinander weiterstellt, hat zwei
Anfragen unterwegs. Kommt die ältere zuletzt zurück, überschreibt sie die
jüngere: unter der Kurve steht die eine Zahl, gezeichnet ist die andere.
`normalkraftWaehlen` verwirft eine Antwort jetzt, wenn inzwischen weitergestellt
wurde. Nachgestellt, indem die erste Antwort künstlich 1500 ms verzögert wurde
und die zweite 100 — die Anzeige bleibt auf dem zuletzt Gewählten.

---

## 2026-09-12 · Ein Kasten, der sich nicht als Kasten zu erkennen gibt

Die zusammengelegten Angaben hatten eine eigene Gestalt bekommen: eigener
Rahmen, eigene Überschriftzeile, keine Kopierknöpfe. Damit war es **ein zweites
Konzept für dieselbe Sache** — und man sah es sofort.

Jetzt ist der zusammengelegte Kasten eine **gewöhnliche Gleichung**: dieselbe
Hülle, dieselbe Kopfzeile, dieselben Word- und TeX-Knöpfe. Die Mehrzahl der
Werte steckt allein darin, dass der Block mehrere `wert_ids` trägt statt einer:

```js
const ids = block.wert_ids || (block.wert_id ? [block.wert_id] : []);
const hervorgehoben = ids.some((id) => zustand.hervorgehoben.has(id));
```

Zusammengelegt wird der Inhalt mit `\qquad` — genau so, wie die Mitschrift es
an anderen Stellen ohnehin schon tut (`M_Ed = … \qquad N_Ed = …`). Die
Rückverfolgung bleibt Wert für Wert auflösbar, weil im Kern weiterhin je
Vorgabe ein Block entsteht und nur die tatsächlich gelaufenen zusammenkommen.

### Tabellen bekommen dieselben Knöpfe

Eine Tabelle ist eine Aussage wie eine Gleichung; dass sie sich nicht
kopieren liess, war eine Lücke. `werkzeugleiste()` steht jetzt einmal da und
hängt an beidem.

### Die Zusammenfassungstabelle kam zweimal vor

Für den Kopierknopf brauchte sie LaTeX. Die Oberfläche hätte es selbst bauen
können — dann gäbe es die Tabelle zweimal, einmal als HTML fürs Auge und
einmal als LaTeX für die Zwischenablage, und die beiden liefen auseinander.

Also baut sie der Kern: `api.zusammenfassungen()` liefert Kopf, Zeilen **und**
LaTeX, letzteres über dieselbe Funktion wie jede Tabelle der Mitschrift. Die
Oberfläche setzt die Zellen und färbt ein, was `erfuellt` sagt. Nebenbei sind
damit die Zahlen der Tabelle auf feste Stellen gebracht, ohne dafür eine eigene
Hilfsfunktion im Browser zu brauchen.

---

## 2026-09-12 · Zwei Kästen statt vier Zeilen — ohne die Rückverfolgung zu verlieren

Plattendicke, Breite und die beiden Überdeckungen standen als vier einzelne
Blöcke untereinander. Das ist kein Nachweis, das ist eine Liste. Jetzt stehen
sie in zwei Kästen: **Abmessungen – Beton C30/37** und **Überdeckungen**.

Die naheliegende Umsetzung wäre gewesen, im Kern einen Block zu schreiben, der
alle vier enthält. Die hätte einen stillen Schaden angerichtet: bei einer
Rückverfolgung läuft nur, was gebraucht wird. Wird allein `h` verlangt, läuft
auch nur dessen Vorgabe — ein verschmolzener Block wüsste davon nichts und
zeigte trotzdem alle vier Werte, davon drei, die gar nicht gerechnet wurden.

Darum bleibt **jede Angabe ihr eigener Block** mit eigener `wert_id`. Sie trägt
nur zusätzlich einen Gruppennamen, und die Oberfläche legt aufeinanderfolgende
Blöcke derselben Gruppe in einen Kasten. Das Verhalten fällt damit von selbst
richtig aus:

| Rückverfolgtes Ziel | Kasten |
|---|---|
| `querschnitt.q1.h` | Abmessungen → nur Plattendicke |
| `querschnitt.q1.c_nom_unten` | Überdeckungen → nur Überdeckung unten |
| `querschnitt.q1.bewehrungsmass` | beide Kästen, alle vier |
| `beton.b1.f_cd` | gar keiner |

Und weil die Blöcke einzeln bleiben, lässt sich im Kasten auch weiterhin jede
Angabe für sich hervorheben.

### Die Betonsorte steht im Kastennamen

Sie ist keine gerechnete Grösse und hat darum keine Kette, an der sie hängen
könnte — filterbar wie die vier Zahlen ist sie nicht. Als Aufschrift des
Kastens gilt sie dagegen immer, denn eine Platte hat genau einen Beton.

Die Zeile in der Zusammenfassung ist damit wieder weg; sie stand ohnehin an
der falschen Stelle.

---

## 2026-09-12 · Die Sorte gehört an das Symbol

Bei zwei Betonen stand in den Plattennachweisen zweimal `f_cd` mit
verschiedenen Zahlen. Der Mechanismus dafür gibt es längst — die Baustoffe
hängen ihren Namen an, sobald mehrere ihrer Art vorkommen. Die Nachweise
gingen daran vorbei: sie schrieben `f_{cd}` selbst hin.

Behoben, indem der Baustoff seinen Index **behält** (`Baustoff.symbol_index`)
statt ihn beim Erzeugen zu verbrauchen. Damit erreichen ihn auch Handrechnung
und Querkraftnachweis, und beide bilden ihre Symbole über dieselbe Funktion
`mit_index()` wie die Materialien selbst — eine Regel, nicht zwei.

Betroffen sind `f_cd`, `f_ck`, `τ_cd`, `ε_c2d` (Beton) sowie `f_yd`, `f_sd`,
`E_s` (Stahl). Der Index richtet sich je Lage nach der **massgebenden** Sorte,
also der mit dem kleinsten `f_yd` — sonst stünde ein fremder Name an der Zahl.

Eine Stelle bleibt ohne: der Spaltenkopf `f_yd [N/mm²]` der Tabelle
«Zusammengefasste Bewehrung». Ein Kopf kann keine zwei Indizes tragen. Dort
kommt stattdessen eine Stahlspalte dazu — aber nur, wenn es mehrere Sorten
gibt, nach derselben Regel wie der Index selbst.

### Was die Platte ist, steht jetzt über ihrer Tabelle

Abmessungen, Überdeckungen und Betonsorte in einer Zeile über der
Nachweistabelle:

```
Beton C30/37   ·   h = 400 mm   ·   b = 1000 mm   ·   c_nom,u = 30 mm   ·   c_nom,o = 30 mm
```

In der Herleitung bleiben sie als eigene Blöcke stehen — dort wird mit ihnen
gerechnet, und eine Herleitung ohne ihre Eingangswerte wäre nicht
nachvollziehbar. Hier geht es um etwas anderes: die Zahlen darunter einordnen
zu können, ohne den Reiter zu wechseln.

---

## 2026-09-12 · Durchsicht nach der M-V-Kurve

Ein Durchgang über alles, was seit der letzten Durchsicht dazugekommen ist.

### Ein roher Fehler kam wieder durch

Die neue Anfrage `querkraftkurven` nahm ihre Normalkraft mit `float(v)` entgegen
— und ein Wort statt einer Zahl endete als `ValueError` mit Status 500 beim
Benutzer. Dieselbe Klasse, die beim letzten Mal in `_zahl()` behoben wurde; der
neue Weg ging daran vorbei.

Bemerkenswert daran: die Anfrage stammt aus der eigenen Oberfläche, wo nur
Zahlenfelder hineinschreiben. Das ist trotzdem keine Zusicherung — sie steht
offen im Netz. Jetzt Status 400 mit Kennung und Wert im Satz.

### Der Schalter günstig/ungünstig

Stand unter den beiden Postenzeilen, gehört aber in den Lagenkopf: die Lage der
Stäbe zueinander ist Geometrie der Lage, nicht Eigenschaft des Werkstoffs.
Jetzt links vom Stahlfeld, dort wo er gesucht wird.

### Was geprüft wurde und hielt

Acht Randfälle der neuen Anfrage; das Polygon in vier Bewehrungsanordnungen —
keine Selbstkreuzung, die Handlinie bleibt überall auf der sicheren Seite der
präzisen; der Bericht (52 646 Zeichen LaTeX, keine übrigen `@`-Platzhalter,
keine doppelten Minus); die Rückverfolgung eines Querkraftziels über 39
Berechnungen; alle vier Reiter; der Umfangsschalter mit Materialauswahl; der
Berichtsdialog; Speichern samt dem Punkt am Knopf. Keine Konsolenfehler, keine
KaTeX-Fehlschläge, keine sich überdeckenden Marken im neuen Diagramm.

---

## 2026-09-12 · Das Polygon kreuzte sich selbst

Der Eckpunkt `x = h/2` liegt gewöhnlich im Druck. Bei einer dünnen, stark
bewehrten Platte aber nicht: sobald `A_s·f_yd` die Blockdruckkraft
`0.85·b·f_cd·h/2` übersteigt, wird sein `N` positiv.

Die Reihenfolge der Eckpunkte war fest verdrahtet — erst `x = h/2`, dann
`M_Rd(N_Ed=0)`. Rutscht der erste in den Zug, läuft die Linie hinauf, wieder
hinunter und erneut hinauf: sie kreuzt sich selbst.

**Und dann ist sie keine Resistenzlinie mehr.** Weder der Punkt-in-Fläche-Test
noch die Schnittsuche liefern auf einem sich kreuzenden Polygon etwas
Brauchbares — und beide tragen jedes Urteil dieses Nachweises.

Jetzt wird jede Seite nach der Normalkraft geordnet: hinauf zur Zugspitze,
wieder hinunter zum Druck. Damit stimmt die Reihenfolge in beiden Fällen, ohne
Sonderbehandlung.

Nachgestellt an h = 150 mm mit ⌀20@100 beidseitig: `A_s·f_yd = 1367 kN` gegen
`1275 kN` Blockdruck, also `N = +90.9 kN` bei `x = h/2`. Vorher sechs
Richtungswechsel in N — jetzt zwei, wie es sein muss.

Den Punkt wegzulassen wäre die andere Möglichkeit gewesen. Ordnen ist besser:
er ist ein gerechneter Widerstand, und ihn zu streichen hiesse, Tragfähigkeit
zu verschenken.

---

## 2026-09-12 · Ein Widerstand aus dem Nichts

Gemeldet: eine Platte nur mit unterer Bewehrung weist trotzdem ein negatives
Moment nach. Nachgestellt und bestätigt — das Polygon hatte einen Eckpunkt bei

```
x = h/2 −     N = −2550 kN,  M = −219.9 kNm
```

**ohne jede obere Bewehrung.** Der Punkt kommt aus dem Kräftegleichgewicht mit
dem Betondruckblock; steht auf der gezogenen Seite kein Stahl, bleibt der Block
allein da und liefert ein Moment, das aus nichts stammt. Die Mitschrift sagte
daneben sogar «die Zugbewehrung fliesst» — über eine Bewehrung, die es nicht
gibt. Der Punkt setzt fliessenden Stahl voraus; ohne Stahl fliesst nichts.

### Dieselbe Lücke beim Querkraftnachweis

`_statische_hoehe` nahm **alle** Lagen der Richtung, ohne auf die Seite zu
achten:

```python
return max(tiefen) if moment_positiv else h - min(tiefen)
```

Bei einseitiger Bewehrung ist das keine statische Höhe mehr. Eine Platte nur
mit unterer Bewehrung lieferte fürs negative Moment `h − 261 = 39 mm` — den
Abstand der Unterkante zur *unteren* Lage. Daraus wurde ein Querkraftwiderstand
gerechnet.

Jetzt zählen nur die Lagen der gezogenen Seite. Gibt es dort keine, gibt es
kein `d` — und ohne `d` keinen Widerstand: `v_Rd = 0`, mit einem Satz, der sagt
warum.

Der Nachweis wird trotzdem geführt und fällt durch. Ihn wegzulassen wäre das
Gefährlichere: eine Einwirkung ohne roten Eintrag liest sich wie Zustimmung.

---

## 2026-09-12 · Die M-V-Kurve

Ein Diagramm je Tragrichtung — höchstens zwei pro Platte, und nur dort, wo auch
ein Querkraftnachweis geführt wurde. Die Waagrechte ist vorzeichenbehaftet:
rechts das positive Moment (Zug unten), links das negative (Zug oben). Je Ast
fünfzig Stützstellen von null bis `m_Rd + 20 kNm`.

Beide Äste im selben Bild, weil sie dieselbe Platte beschreiben. Sie treffen
sich bei `M_Ed = 0` nicht unbedingt: jeder misst mit seiner eigenen statischen
Höhe — im Beispiel 261 mm unten gegen 264 mm oben, also 285.9 gegen
289.2 kN/m. Kein Zeichenfehler, sondern die Platte.

Einen Ast gibt es nur, wo auf der gezogenen Seite Bewehrung liegt.

**In die Herleitung kommt davon nichts.** Die Kurve ist eine Ansicht, keine
Rechenschaft: fünfzig Stützstellen niederzuschreiben hiesse, den Bericht mit
Zahlen zu füllen, die niemand einzeln nachrechnet.

### Eine Funktion, zwei Aufrufer

Die Kurve könnte leicht neben ihren eigenen Punkten herlaufen — und das wäre
schlimmer als gar keine Kurve, weil sie wie eine Bestätigung aussähe. Darum
ging die Rechnung zuerst aus `_einen_fall` heraus in eine freie Funktion
`widerstand(...)`. Nachweis und Kurve rufen dieselbe; ein Test rechnet den
Bemessungspunkt direkt nach und vergleicht ihn mit dem Urteil.

### Jenseits von m_Rd

Der eigentliche Grund, 20 kNm weiterzuzeichnen. Dort fliesst die Bewehrung,
die elastische Beziehung gilt nicht mehr, und die Dehnung folgt nicht mehr dem
Moment, sondern ist **fest**:

```
ε_v = 1.5 · f_yd/E_s          (konstant)
```

Der Widerstand fällt damit einmal und läuft danach waagrecht. Im Beispiel von
170.1 auf 141.4 kN/m — ein Sprung von 17 %. Gezeichnet wird der Ast
gestrichelt, damit der Absatz nicht wie ein Rechenfehler aussieht.

Angeschrieben sind drei Stellen: der Höchstwert bei M_Ed = 0, der Wert genau
bei M_Ed = m_Rd und die Waagrechte danach. Die mittlere brauchte eine eigene
Stützstelle: die fünfzig gleichmässigen treffen m_Rd nur zufällig, und die
Marke hätte sonst den Wert des Nachbarpunkts gezeigt (170.6 statt 170.1) --
und der Absatz wäre schräg statt senkrecht.

### Die Normalkraft gehört unter das Diagramm

`v_Rd` hängt über `m_Rd(N_Ed)` von der Normalkraft ab. Eine Kurve gilt also
immer nur für eine; welche, steht in einem Feld darunter.

Wird sie verstellt, **rechnet der Kern neu** — eine eigene Anfrage
`querkraftkurven`. Die naheliegende Abkürzung wäre gewesen, das Polygon in den
Browser zu geben und dort zu interpolieren; dann stünde die Formel ein zweites
Mal im Werkzeug, in einer anderen Sprache. Ein Umlauf kostet in Pyodide rund
70 ms.

Bemessungspunkte, deren Normalkraft nicht die eingestellte ist, werden blass
gezeichnet statt weggelassen — sie sind ja vorhanden, nur eben auf einer
anderen Kurve. Der Mauszeiger sagt dann, zu welcher.

Die eingestellte Normalkraft steht in der Ansicht, nicht im Projekt: sie sagt
nichts über das Bauwerk, sondern nur, welchen Schnitt man gerade sehen will.

---

## 2026-09-12 · Eingaben wurden auf Treu und Glauben genommen

Eine Durchsicht mit Randwerten statt mit dem Beispiel. Die Verweise waren
sauber geprüft — fehlendes Material, unbekannte Sorte, doppelter Name, alles
mit einem verständlichen Satz. **Zahlen dagegen wurden gar nicht geprüft.**

### Eine eingegebene Null verschwand

```python
h=float(d.get("h") or 300.0)
```

`0 or 300.0` ist `300.0`. Der Ausdruck kann eine eingegebene Null nicht von
einem fehlenden Feld unterscheiden — und dieselbe Zeile gab es für `b`, beide
Überdeckungen und `D_max`.

Durchgespielt in der Oberfläche: ins Feld *Dicke h* eine `0` getippt. Das Feld
zeigt 0, der Browserspeicher enthält 0, gerechnet wird mit **300 mm**, die
Herleitung schreibt 300 mm hin — und oben rechts steht **«alle Nachweise
erfüllt»**. Eine Platte ohne Dicke, und das Werkzeug beruhigt.

Das ist der schlimmste Fehlerfall, den dieses Programm haben kann: nicht eine
falsche Zahl, sondern eine falsche Zahl mit einem grünen Haken daneben.

Jetzt gibt es `_zahl(d, feld, vorgabe)` — die Vorgabe greift nur, wenn nichts
dasteht. Und `_pflichtfeld()` für die, die keine Vorgabe haben dürfen.

### Unmögliche Abmessungen liefen durch

`h = -300` wurde gerechnet. Eine Platte mit 400 mm Überdeckung in 300 mm Dicke
auch. Heraus kamen Zahlen, die aussahen wie ein Ergebnis.

`_masse_pruefen()` hält auf, was geometrisch unmöglich ist — und nur das. Ob
20 mm Überdeckung für die Expositionsklasse genügen, entscheidet der Ingenieur;
das Werkzeug hat dazu nichts zu sagen. Null Überdeckung bleibt darum erlaubt.

### Rohe Python-Fehler kamen beim Benutzer an

| Eingabe | Vorher |
|---|---|
| eigenes Material, `γ_c = 0` | `ZeroDivisionError: float division by zero` |
| eigenes Material, `f_ck = -30` | `TypeError: … not 'complex'` |
| Datei ohne `kennung` | `KeyError: 'kennung'` |

Alle drei mit HTTP 500. Jeder Kennwert dieser beiden Baustoffe ist seiner Natur
nach positiv — Festigkeiten, Moduln, Dehnungen, Teilsicherheitsbeiwerte. Eine
Null liefert dort keine falsche Zahl, sondern gar keine. Das wird jetzt vorher
gesagt, mit Sorte und Kurzname im Satz.

### Nachgemessen

Fünfzehn Randfälle, vorher vier Abstürze und vier stille Ersetzungen — jetzt
durchgehend Status 400 mit einem deutschen Satz, und die zulässigen Fälle
rechnen unverändert. Was gut war, blieb gut: fremdes JSON, doppelte Namen,
gelöschtes Material, leeres Projekt, Rundreise durch `pruefen` (byte-gleich),
nur eine Seite bewehrt, Stabzahl statt Teilung, gemischte Angabe.

---

## 2026-09-12 · Zwei Arten von Überschrift, und nur zwei

Die Mitschrift sah flach aus, wo sie es nicht ist: «Plattenanalyse: Decke über
EG» und «Querkraft – x-Richtung» trugen dieselbe Schrift, denselben blauen
Akzent, dieselbe Linie. Das eine beginnt einen Bestandteil, das andere
gliedert innerhalb — zu sehen war das nicht.

Die Ursache war eine altbekannte: **die Oberfläche entschied nach der
Schriftebene.**

```js
el(`div.b-titel${block.ebene >= 3 ? '.b-titel-3' : ''}`, …)
```

`ebene` ist eine Grössenangabe, keine Aussage über den Rang. Ein Abschnitt und
eine Zwischenüberschrift stehen beide auf 2, also sahen sie gleich aus. Die
Aussage steht längst im Block: trägt er einen Namensraum, beginnt hier etwas
Neues. Genau danach wird jetzt entschieden — dasselbe `raum`, das schon den
Umfangsschalter und die Abschnittsgruppierung trägt.

Damit gibt es zwei Arten:

| | Schrift | Akzent | Linie |
|---|---|---|---|
| `.b-titel` (neuer Bestandteil) | 700, 16 px | blau, 4 px | ja |
| `.b-untertitel` (gliedert innerhalb) | 500, 14 px | gedämpft, 3 px | nein |

Die Ebene bleibt, aber nur noch für die Tiefe *innerhalb* eines Abschnitts:
eine Stufe tiefer wird eingerückt und einen Punkt kleiner, nicht neu
eingefärbt. Eine dritte Farbe hätte eine Bedeutung behauptet, die es nicht
gibt.

Der Akzent der Zwischenüberschriften bekam eine eigene Variable
(`--unterakzent`). Die Farben darüber tragen je eine Bedeutung — Beton grau,
Betonstahl kupfer, Platte blau —; eine davon hier zu borgen hiesse, etwas
auszusagen, was nicht gemeint ist.

---

## 2026-09-12 · m_Rd(N_Ed) wird auch beim Querkraftnachweis hergeleitet

Der Querkraftwiderstand hängt über ε_v vom Momentenwiderstand ab, und der
wiederum von der wirkenden Normalkraft. In der Mitschrift stand dafür bisher
eine blanke Zahl — nachrechenbar nur, wenn man sie im M-N-Nachweis suchen ging.

Jetzt steht die Interpolation dort, wo mit ihr gerechnet wird:

```
M_Rd = M_1 + (N_Ed − N_1)/(N_2 − N_1) · (M_2 − M_1)
     = 337.2 + (−300.0 − (−1484.6))/(0.0 − (−1484.6)) · (248.7 − 337.2)
     = 266.6 kNm
```

samt der Tabelle der beiden Stützpunkte.

**Nicht nachgebaut, sondern geteilt.** `protokoll_interpolation` war eine
Methode von `BiegungNormalkraft` und ist jetzt eine freie Funktion; beide
Nachweise rufen dieselbe. Eine zweite Fassung im Querkraftmodul liefe früher
oder später auseinander — und zwar unbemerkt, weil beide plausible Zahlen
lieferten.

Was der Querkraftnachweis dafür braucht, ist die Auswertung hinter
`M_Rd(N_Ed)`. Der M-N-Nachweis rechnet sie ohnehin (sie ist die Quelle von
`d_m_rd`) und reicht sie über `widerstand_bei_n()` heraus — ein benannter
Übergabepunkt statt eines Griffs in fremde Zwischenstände. Dass sie zum
Zeitpunkt des Zugriffs vorliegt, steht nicht in einer Annahme: der
Querkraftnachweis führt `d_m_rd` als Eingang, also sichert der Graph die
Reihenfolge.

### Dabei aufgefallen

Bei negativem Moment zeigte die Interpolation `−83.9` und die Dehnungsformel
darunter `83.9` — zwei Zahlen für dieselbe Grösse. Gerechnet wird mit dem
Betrag, also trägt die Formel ihn jetzt auch:

```
ε_v = f_yd · (|m_Ed| − m_Dd) / (E_s · (|m_Rd(N_Ed)| − m_Dd))
```

Dasselbe Prinzip wie beim negativen Moment in der Handrechnung: die
geschriebene Gleichung muss ihr eigenes Ergebnis liefern.

---

## 2026-09-12 · Sieben Meldungen

### Zug schliesst den Querkraftnachweis nicht mehr aus

Bei einer Normalzugkraft wurde `v_Rd = 0` gesetzt. Nötig war das nie: das
Dekompressionsmoment ist über `min(N_Ed; 0)` definiert und wird bei Zug von
selbst null — entlastend wirkt nur Druck. Der Sonderfall stand also neben einer
Formel, die dasselbe schon sagte, und übertönte sie. Weg damit; der Nachweis
läuft durch, und der kleinere Momentenwiderstand bei Zug senkt `v_Rd` ohnehin.

Der Test dazu ging vorher über die Formel statt über den Nachweis, weil der
Sonderfall verhinderte, dass sie je erreicht wurde. Jetzt prüft er den Weg.

### Eine Vorgabe darf schweigen

Vierzehn Zeilen der Form `∅ = 12 mm` und `s = 150 mm` standen untereinander in
der Herleitung — dieselben Zahlen wie in der Lagentabelle, nur schlechter zu
vergleichen. `Vorgabe(stumm=True)` schreibt keinen eigenen Block, bleibt aber
ein vollwertiger Knoten im Rechengraph: in der Werteliste, überschreibbar,
rückverfolgbar.

Dasselbe für Grösstkorn und Einlagenhöhe — die stehen jetzt beim
Querkraftnachweis, der sie als einziger braucht, statt verwaist zwischen
Plattendicke und Bewehrung.

Der Solver setzt für eine stumme Berechnung auch keine Abschnittsüberschrift;
sonst stünde ein Titel ohne alles darunter.

### Die Nachweise erbten ihren Abschnitt vom Zufall

Beim Aufräumen aufgefallen: weder `BiegungNormalkraft` noch `Querkraft` gab
einen `abschnitt` an. Beide schrieben ihre Überschrift einfach dorthin, wo sie
gerade landeten — und das entscheidet die Abhängigkeitsfolge. In einer
Reihenfolge stand der Querkraftnachweis der Platte unter **Beton: C30/37**.
Jetzt trägt jeder Nachweis den Abschnitt seiner Platte.

### Feste Stellenzahl in den Tabellenspalten

`205` neben `224.5`, `1.6` neben `0.99` — die Kommas fluchteten nicht.
`formatiert()` streicht nachlaufende Nullen, und das bleibt so: im Fliesstext
ist es richtig. Die Tabelle bekommt daneben die Rohzahl und die Stellenzahl und
setzt sie selbst. In einer Spalte steht immer dieselbe Grösse, also passt auch
immer dieselbe Stellenzahl.

### Die Griffe zwischen den Tafeln

Der linke Griff zog nur `--breite-links` nach. Die mittlere Tafel behielt ihre
Pixelbreite und rutschte mit, also ging die Änderung zu Lasten der rechten —
die als `1fr` schlicht den Rest bekommt. Wer die rechte schmaler wollte, musste
am linken Griff ziehen.

Jetzt nimmt jeder Griff der einen Tafel, was er der anderen gibt; die dritte
bleibt, wo sie ist. Die Breiten werden gemessen statt gerechnet — zwischen den
Tafeln liegen noch die Griffe selbst, und die rechte hat gar keine Variable.

### Ziffern unter den Pfeilen

`.zahlfeld > input` hielt rechts 16 px frei, `.postenzeile input[type=number]`
setzte `padding: 3px 5px` — und gewann, weil ein Attributselektor spezifischer
ist. Die Ziffern liefen unter die Pfeile. Die Spurbreite steht jetzt einmal als
`--pfeilspur`, und die Regel hat dieselbe Form wie die überschreibende.

### Pfeiltasten hielten bei null

`naechsteStufe` hatte ein `Math.max(0, …)` eingebaut. Für Durchmesser und
Teilung stimmt das, für ein Moment nicht. Die Grenze sagt jetzt jedes Feld für
sich über `min` — die Schnittgrössen ohne, die Baustoffkennwerte mit.

### Nebenbei

Der Schliessen-Knopf des Berichtsdialogs war weiss auf weiss: der Dialogkopf
setzt `color: #fff`, und `.knopf` bringt eine helle Fläche mit. Jetzt ein ×
mit eigenem Stil. Und die Seite hat ein Zeichen — `web/favicon.svg`, OCT in
Weiss und dem Blau der Wortmarke. Gezeichnet, nicht gesetzt: ein `<text>` im
Favicon hinge davon ab, welche Schrift der Browser gerade findet.

---

## 2026-09-12 · Durchsicht der laufenden Seite

Vier Befunde, drei davon im Kern.

### Die Stahlflächen der Handrechnung hatten einen leeren Index

In der Herleitung stand `A_{s,}` — Komma, dann nichts. Beide Lagen trugen
dasselbe Symbol, obwohl verschiedene Zahlen darunter standen, und `d` hatte gar
keinen Index. Genau das, was mit den eindeutigen Indizes behoben worden war.

Die Ursache lag eine Schicht tiefer: `lagen_zusammenfassen` bekam blanke Tupel

```python
(a_s, z, f_yd, E_s, text, von_unten)     # sechs von acht Feldern
```

obwohl es `Posten` mit genau diesen Feldern **plus** `index` und der Herkunft
gibt. Das Tupel war die verlustbehaftete Zwischenform; was es nicht trug, war
weg. Und weil `Lage.teile` damit immer leer blieb, lief

```python
if len(lage.teile) > 1:
    self._schwerpunkt(p, lage)
```

**nie** — die Herleitung von `d` aus Grundbewehrung und Zulage, ausdrücklich
gewünscht und vollständig geschrieben, war toter Code. Ein stiller Ausfall:
keine Fehlermeldung, nur eine fehlende Formel.

Behoben, indem `Posten` selbst durchgereicht wird. Der Index entsteht jetzt in
`platte.posten_index()` statt an zwei Stellen mit derselben Formel.

Der erste Test dazu fand sofort einen Fall, den ich übersehen hatte: eine
unbewehrte Seite hat gar keine Lagennummer, also auch keinen Index — und
schrieb weiter `A_{s,}`. Darum bildet die Lage ihr Symbol nun selbst
(`symbol_flaeche`, `symbol_d`) und fällt ohne Index auf schlichtes `A_s`
zurück, statt ein leeres Tiefstellen zu erzeugen.

### Einheiten in zwei Schreibweisen

Die Diagramme beschrifteten `σ [N/mm²]`, die Herleitung setzte `N/mm²` — und
die Werteliste, die Kennzahlen und die Felder der Eingabemaske zeigten
`N/mm^2`, `mm^2`, `kg/m^3`, `promille`. Dieselbe Einheit, drei Zentimeter
auseinander, verschieden geschrieben.

Der `name` einer `Einheit` ist ihr Schlüssel im Katalog und muss ASCII
bleiben. Neben `latex` steht darum jetzt `beschriftung` — die lesbare Form für
alles, was als blanker Text neben einer Zahl erscheint. Die Potenzen entstehen
mechanisch, `‰` gibt `PROMILLE` selbst an, denn aus `promille` liesse es sich
nicht ableiten. Zusammengesetzte Einheiten erben sie wie das LaTeX.

### Jede Überschrift stand mehrfach

Bei zwei Platten mit Querkraft zählte das Protokoll **acht** Abschnittstitel
für vier Abschnitte: `q1` dreimal, `beton` zweimal. Der Querkraftnachweis
einer Platte braucht ihren Momentenwiderstand und kommt darum erst, wenn alle
M-N-Nachweise durch sind — die Rechenreihenfolge springt zwischen den Bauteilen
hin und her, und das Protokoll bildete sie ab.

`Protokoll.nach_abschnitten()` legt jeden Abschnitt wieder an ein Stück.
Innerhalb eines Abschnitts bleibt die Rechenreihenfolge unangetastet, die
Abschnitte selbst stehen in der Reihenfolge ihres ersten Auftretens. Es ist
eine Frage der Darstellung, also rufen es alle drei Ausgaben auf — Oberfläche,
LaTeX und Konsole — statt dass eine davon es für sich löst.

### Kleineres

`2 Nachweis(e) nicht erfüllt` schreibt sich jetzt aus. Und wo `einheit.name`
in menschenlesbarem Text stand, steht `beschriftung`; wo es als LaTeX diente,
`latex` — die dritte, handgeschriebene Fassung `\mathrm{{...}}` ist weg.

### Was offen bleibt

In den Tabellenspalten springt die Stellenzahl: `205` neben `224.5`, `1.6`
neben `0.99`. `formatiert()` streicht nachlaufende Nullen, und das ist im
Fliesstext richtig — in einer Zahlenkolonne nicht. Steht in `TODO.md`.

---

## 2026-09-12 · Zwei gemeldete Fehler

### Alle Nachweise landeten in der Tabelle der ersten Platte

Gemeldet: bei zwei Platten stehen die Nachweise beider in derselben Tabelle.

Die Ursache war derselbe Fehler, den der dritte Befund der letzten Durchsicht
schon einmal gefunden hatte — ich hatte ihn nur an einer Stelle übersehen. Die
Zusammenfassung musste einem Urteil ansehen, zu welcher Platte es gehört, und
tat das über den **Anzeigetext**:

```js
// so war es
if (Object.keys(eintrag.nachweise || {}).some((r) =>
  urteil.name.includes(` ${r} –`))) return kennung;
```

`r` ist die Tragrichtung, also `x` oder `y`. Jede Platte hat beide. Also passte
jedes Urteil auf die erste Platte, und die Schleife brach dort ab: zwölf Zeilen
in der ersten Tabelle, «kein Nachweis gerechnet» in der zweiten. Bei nur einer
Platte fiel das nie auf — die Antwort war zufällig richtig.

Die Behebung verlegt die Zuordnung dorthin, wo sie bekannt ist. Ein Urteil
trägt jetzt den Namensraum seines Nachweises, und **gestempelt wird er in der
Oberklasse**, nicht von den Unterklassen:

```python
def rechne(self, e, p):
    groessen, urteile = self.pruefe(e, p)
    self.urteile = [replace(u, raum=self.id) for u in urteile]
    return groessen
```

Das ist der eigentliche Punkt. Hätte `NachweisUrteil` ein Pflichtfeld `raum`
bekommen, müsste jede Nachweisklasse daran denken und könnte sich vertun. So
gibt es die Angabe genau einmal, und sie kann nicht falsch sein. In der
Oberfläche fällt damit die letzte Sonderbehandlung weg — es gilt dasselbe
Prädikat wie in den anderen vier Sichten:

```js
const urteile = (loesung.urteile || []).filter(
  (u) => imRaum(eintrag.namensraum, u.raum));
```

Geprüft mit einem Projekt aus zwei gleich bewehrten Platten: der Test verlangt,
dass jedes Urteil auf **genau einen** Namensraum passt, und hält daneben fest,
dass die Namen allein es nicht entschieden hätten — sie sind identisch.

### Die leere Zulage stand auf «Anzahl»

Zwei Felder beschreiben dieselbe Sache, und genau eines davon ist gesetzt:
Teilung **oder** Stabzahl. War keines gesetzt — der Normalfall bei einer noch
leeren Zulage —, las die Oberfläche das als «Stabzahl», weil sie nur auf
`abstand !== null` prüft. Bei einer Platte ist die Teilung aber der Regelfall.

Die Regel steht jetzt in `PostenEintrag.aus_dict`, also an der Stelle, durch
die **alle drei** Wege laufen (Beispiel, Ablage im Browser, Datei von der
Platte — `projektHolen()` schickt auch den abgelegten Stand durch `pruefen`).
Damit richtet sich auch ein schon gespeichertes Projekt beim nächsten Öffnen.
Eine ausdrücklich gewählte Stabzahl bleibt selbstverständlich eine Stabzahl.

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
