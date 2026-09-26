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
