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
