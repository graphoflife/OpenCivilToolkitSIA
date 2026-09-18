# Was noch offen ist

Reihenfolge ungefähr nach Dringlichkeit. Erledigtes wandert raus — was dabei
gelernt wurde, steht in [ENTWICKLUNG.md](ENTWICKLUNG.md).

---

## Offen


- [ ] **Die Sortentabellen sind ungeprüft.** `BETONSORTEN` und `STAHLSORTEN` in
      `material/` stammen aus der Vorgängerfassung und sind nie gegen die
      gedruckte SIA 262 gehalten worden. Dasselbe gilt für sämtliche
      Normverweise. Vor ernsthaftem Gebrauch nachschlagen.
- [ ] Normstelle für den vereinfachten Spannungsblock (0.15·ε_c2d … f_cd) fehlt
      — bewusst leer gelassen, statt eine Ziffer zu erfinden.
- [ ] Der Riegel `k_g ≥ 1.20` ist nach Vorgabe eingebaut, aber nicht gegen die
      Norm geprüft. Bei D_max = 32 mm und C30/37 greift er (roh 1.00 → 1.20)
      und senkt den Querkraftwiderstand um gut 4 %.
- [ ] Keine Testumgebung für das JavaScript. `stabstellen`, `besterVersatz`,
      `naechsteStufe` und `beschriftungenEntzerren` sind rein und wären in
      wenigen Zeilen abgedeckt; geprüft wird bisher von Hand im Browser.
- [ ] Momente stehen in der Mitschrift als `kNm`, gemeint ist `kNm/m` (die
      Platte wird je Laufmeter gerechnet). In der Eingabemaske steht es
      richtig. Einheitlich ziehen.

## Offene Normfragen — deine Fragen, unbeantwortet

Diese Punkte sind **nicht** entschieden. Ich habe je eine Annahme eingebaut und
sie hier notiert; keine davon ist nachgeschlagen.

- [ ] **Wird bei den häufigen Lastfällen mit φ gerechnet?** Eingebaut: ja,
      `E_c,eff = E_cm/(1+φ)` mit demselben φ wie überall. Begründung: häufige
      Einwirkung ist Dauerlast, und Kriechen senkt den Hebelarm, liegt also auf
      der sicheren Seite. Aber die Norm sagt es an dieser Stelle nicht.
- [ ] **Charakteristische oder Bemessungs-Kennwerte für die Stahlspannung?**
      Eingebaut: `E_s` und `E_cm` als Mittelwerte (4.4.1.2 verlangt
      Mittelwerte), die Grenze dagegen aus `f_yd − 80 MPa` (Tabelle 17). Das
      mischt zwei Niveaus — nach Tabelle 17 steht dort aber ausdrücklich `f_yd`.
- [ ] **Zugfestigkeit des Betons in der Spannungsrechnung?** Eingebaut: nein,
      voll gerissen. Das ist konservativ (ohne Mitwirkung zwischen den Rissen),
      aber die Norm erlaubt in 4.4.1.2 die Mittelwerte — also womöglich auch
      `f_ctm`.
- [ ] **Unterscheidet die Norm inneren Zwang auf Normalkraft und auf Biegung?**
      Eingebaut: ja, als zwei getrennte Nachweise mit verschiedenem `k_t`
      (`h` gegen `h/3`). 4.4.1.3 stützt das («für Platten- und
      Rechteckquerschnitte unter Biegebeanspruchung gilt t = h/3»), nennt sie
      aber nicht als zwei Nachweise.
- [ ] **Unterscheidet die Norm sprödes Versagen auf Normalkraft und Biegung?**
      Eingebaut: die Rissnormalkraft steht unter *Mindestbewehrung* (4.4.2), das
      Rissmoment unter *sprödes Versagen* (4.4.1.3). Ob das die gemeinte
      Trennung ist, steht dahin.
- [ ] **Was macht der Eurocode?** Nicht verglichen. EC2 7.3.2 hat
      `A_s,min·σ_s = k_c·k·f_ct,eff·A_ct` — formal dieselbe Gestalt wie
      SIA 4.4.2, aber mit `k_c` und `k` statt `k_t`, und mit einer anderen
      Begründung für die wirksame Zugzone. Ein Vergleich würde zeigen, ob die
      Zahlen zusammenpassen.
- [ ] **Steifigkeit beim Knicken: charakteristisch oder Bemessung?** Eingebaut:
      Bemessung (`f_cd`, `f_yd`) mit `E_cm/(1+φ)`. Du vermutest dasselbe. Ob φ
      dabei überhaupt gilt und ob `eps_c2d = 3‰` oder der Wert der Norm (3.5‰)
      zu nehmen ist, ist offen — eingebaut sind die Werte des Betons aus dem
      Katalog.
- [ ] Alle diese Schalter sollen laut deiner Anmerkung **wählbar** sein
      (φ ja/nein, charakteristisch/Bemessung). Eingebaut ist je eine feste
      Annahme; die Schalter fehlen noch.

## Noch nicht gebaut

- [ ] **Automatisches Bewehrungstool.** Nicht angefangen — die Zeit ging für
      Löser, Spannungsbegrenzung und Knicken drauf. Das Gerüst steht aber:
      `Projekt.aufbauen()` liefert alle Urteile, und eine Suche über
      Durchmesser × Teilung müsste nur wiederholt aufbauen und die Urteile
      abfragen. Offen ist vor allem, wonach optimiert wird (kleinste
      Stahlmenge? wenigste Durchmesser?) und welche Nachweise mitzählen.
- [ ] **Spannung-Dehnung-Analyse**: das Panel steht leer da. Der Löser liefert
      zu jedem Fall ε_m und χ; was gezeigt werden soll, ist noch nicht
      festgelegt.

## Offen (neu)

- [ ] Die rechte Tafel läuft waagrecht über, sobald sie schmal wird (bei rund
      350 px um 63 Bildpunkte). Formeln und Tabellen haben je einen eigenen
      Rollbalken; ein Inhalt entkommt ihnen. Besteht schon länger, nicht neu.
- [ ] Die Normstelle für das Fachwerkmodell mit Bügeln (`SIA 262:2025, 4.3.3.4`)
      ist eingetragen, aber wie alle anderen Verweise nicht nachgeschlagen.
      Dasselbe gilt für die Vorgaben `α_min = 30°`, `α_max = 45°`, `k_c = 0.55`
      und die Regel, dass Normalzug beide Grenzen auf 40° hebt — alle nach
      Vorgabe eingebaut, keine geprüft.
- [ ] Ebenso der Duktilitätsnachweis: die Grenze `x/d ≤ 0.35` und der Verweis
      `SIA 262:2025, 4.1.4.2.5` stehen nach Vorgabe da, nachgeschlagen ist
      keines von beiden.

- [ ] Die Zahlen der Rissnachweise sind ungeprüft wie alle anderen: beide `k_t`,
      die 500-mm-Grenze, `h/3`, `w_nom = 0.5/0.2 mm` und die Wurzelformel für
      `σ_s,adm` stehen nach Vorgabe da, nachgeschlagen ist keines davon.

## Erledigt zuletzt

Querschnittslöser für Dehnungsebenen (zwei geschachtelte Bisektionen, ohne
fremde Pakete) · Sprödes Versagen und Zwängung auf Biegung als zwei getrennte
Nachweise, je Lage einschaltbar · Stahlspannung unter häufiger Einwirkung gegen
`f_yd − 80 MPa` · Knicknachweis am verformten System (nur x-Richtung) ·
Ein/Aus-Schalter an jedem Tragsicherheitsfall · Panel «Spannung-Dehnung»
(leer) ·

Sprödes Versagen unter Biegung: `M_s,adm = σ_s,adm·A_s·z ≥ M_Riss`, der
Hebelarm aus dem gerissenen Querschnitt (Zustand II) statt aus einem
plastischen Ansatz — dort hängt `x` nicht von der Last ab, ist also eine reine
Querschnittseigenschaft. Kriechen über `n = (E_s/E_cm)·(1+φ)` mit φ als
Eingabe; dass ein grösseres φ immer konservativ ist, ist bewiesen und nicht
vermutet · Der gerissene Querschnitt als eigener Baustein
(`nachweis/zustand2.py`), damit die spätere Spannungsbegrenzung dieselbe
Nulllinie benutzt ·

Sprödes Versagen unter Normalkraft-Zwängung: `N_s,adm = A_s·σ_s,adm ≥ N_Riss`,
je Tragrichtung für die untere und die obere Lage, mit `σ_s,adm` aus der
Rissanforderung (Normal/Erhöht/Hoch) · Eingaben für die Mindestbewehrung
(Rissanforderung, Zwängung, häufige Lastfälle, 70-%-Ableitung) · Der
Haken/Kreuz-Schalter steht nicht mehr schief ·

Die Bewehrungsübersicht läuft von oben nach unten, wie die Eingabemaske und wie
der Schnitt durch die Platte; die Bügelzeile zeigt nur noch `⌀6@200@200` statt
der halben Herleitung · Das Gradzeichen hatte keine Basis (`\,^{\circ}`) — KaTeX brach daran ab und
zeigte den rohen Quelltext des ganzen Kastens · Der Kasten der Bügelangaben war
zerrissen, weil die Flächenformel zwischen den Vorgaben lief: die Reihenfolge
der Eingänge ist die Reihenfolge der Blöcke · Eine Tragrichtung ohne Bewehrung
stand nicht mehr in der Zusammenfassung, obwohl Einwirkungen angegeben waren;
jetzt gibt es dort Zeilen mit Widerstand und Erfüllungsgrad null samt Grund,
für M-N wie für Querkraft ·

Duktilitätsnachweis je Bewehrungslage: `x/d ≤ 0.35` mit `x` aus dem
Kräftegleichgewicht bei reiner Biegung, `d` ab der gedrückten Randfaser, Lage
für Lage einschaltbar (Vorgabe: die beiden äusseren). Eine eingeschaltete, aber
unbewehrte Lage meldet sich mit einem Satz statt mit einer erfundenen Null —
dafür trägt das Urteil jetzt ein eigenes Feld `hinweis`, statt dass die
Schnittstelle es aus einem Widerstand von null errät · Kreuze an den
Bewehrungsposten als runde Knöpfe mit hellrotem Grund · Tragrichtung einer
Einwirkung als Schalter x/y/x+y in den Farben der Lagen ·

Querkraftbewehrung: Bügelraster mit eigenem Stahl, Teilung je Richtung (in y
wahlweise als Stabzahl), Grenzwinkel der Druckdiagonalen und `k_c`. Mit Bügeln
gilt das Fachwerkmodell statt des Betonanteils, gesucht über die günstigste
Neigung; an die Stelle der M-V-Kurve tritt der Verlauf über α. Ein Widerstand
von null trägt jetzt überall seinen Grund sichtbar in der Zusammenfassung ·

Nicht rechnen, was schon dasteht: bei `N_Ed = 0` stand ein Bruch mit null im
Zähler, jetzt steht der getroffene Eckpunkt da — dasselbe bei `M_Ed = 0` und
Normaldruck · Der Massstab des Erfüllungsgrads wird nicht mehr über eine
Schwelle geraten: beide Wege werden gerechnet, es gilt der kleinere · Die
Zusammenfassung ist schlanker (`M-N: Feld`, keine Spalte *Urteil*, der
Erfüllungsgrad weich hinterlegt) und trägt darüber Beton, Dicke, Breite sowie
die Bewehrung von unten nach oben · `v_Rd` durchgehend gross, `V_Ed` ohne
Betragsstriche · blauer Akzent an allen Zahlenfeldern · × vor jedem
Bewehrungsposten · neue Platten mit `D_max = 32 mm` und Bewehrung nur in der
1. und 4. Lage · Eine Änderung während des Rechnens fiel unter den Tisch: der Riegel gegen
doppeltes Rechnen verwarf den zweiten Wunsch, statt ihn aufzuheben — angezeigt
wurde danach das Urteil zur vorherigen Zahl. Dazu: der Riegel stand ausserhalb
von `finally` und hätte nach einem Zeichenfehler jede weitere Rechnung für
immer gesperrt; während des verzögerten Durchgangs stand weiter «geändert …»
statt «rechnet …»; und zwei rasch aufeinander gestellte Normalkräfte unter dem
Diagramm konnten einander überholen · Der zusammengelegte Kasten ist eine gewöhnliche Gleichung mit Word/TeX-Knöpfen; Tabellen haben dieselben Knöpfe, und die Zusammenfassungstabelle kommt samt LaTeX aus dem Kern statt zweimal gebaut zu werden · Plattenangaben in zwei Kästen statt vier Zeilen, je Angabe ein eigener Block — damit bleibt die Rückverfolgung Wert für Wert auflösbar · Sortenindex an den Symbolen der Plattennachweise (f_cd, τ_cd, f_yd …), sobald mehrere Betone oder Stähle vorkommen · Angaben zur Platte über der Nachweistabelle · Schalter günstig/ungünstig in den Lagenkopf, links vom Stahl · rohe ValueError aus `querkraftkurven` abgefangen · Das Handpolygon kreuzte sich selbst, sobald der Eckpunkt x = h/2 im Zug lag (dünne, stark bewehrte Platte) — die Eckpunkte werden jetzt je Seite nach der Normalkraft geordnet · Ein Widerstand aus dem Nichts: ohne obere Bewehrung wies das Polygon ein
negatives Moment von 220 kNm nach, und der Querkraftnachweis rechnete mit einer
statischen Höhe von 39 mm · M-V-Kurve je Tragrichtung, beide Momentenvorzeichen
in einem Bild, mit einstellbarer Normalkraft und drei Marken · Eingaben werden
geprüft: eine eingegebene Null wurde stillschweigend durch die
Vorgabe ersetzt (`h = 0` rechnete mit 300 mm und meldete «alle Nachweise
erfüllt»), unmögliche Abmessungen liefen durch, und `γ_c = 0` kam als
`ZeroDivisionError` beim Benutzer an · Überschriften der Herleitung: fett mit blauem Akzent nur noch dort, wo ein
Bestandteil beginnt; innerhalb Zwischenüberschriften mit gedämpftem Akzent.
Entschieden wird nach dem Namensraum des Blocks, nicht mehr nach der
Schriftebene · `m_Rd(N_Ed)` wird auch beim Querkraftnachweis hergeleitet — dieselbe
Interpolation wie beim M-N-Nachweis, geschrieben von derselben Funktion; dazu
die Betragsstriche in der Dehnungsformel, damit sie ihr eigenes Ergebnis
liefert · erklärende Vorrede zur Lagentabelle entfällt · feste Stellenzahl in
den Tabellenspalten · Querkraftnachweis auch bei
Normalzug (m_Dd wird über `min(N_Ed; 0)` von selbst null) · Durchmesser und
Teilung nicht mehr als eigene Blöcke in der Herleitung, Grösstkorn und
Einlagenhöhe dafür beim Querkraftnachweis · jeder Nachweis trägt den Abschnitt
seiner Platte, statt ihn von der Rechenreihenfolge zu erben · Spaltengriffe
bewegen je eine Grenze · Ziffern liefen unter die Pfeile der Zahlenfelder ·
Pfeiltasten hielten bei null, obwohl Schnittgrössen negativ sein dürfen ·
Schliessen-Knopf im Berichtsdialog war weiss auf weiss, jetzt ein × ·
Zeichen für den Browsertab (`web/favicon.svg`).

## Davor

Durchsicht der laufenden Seite: leerer Index bei den Stahlflächen der
Handrechnung (`A_{s,}`) samt der nie geschriebenen Schwerpunktformel für `d` ·
Einheiten als `N/mm^2` statt `N/mm²` in Werteliste, Kennzahlen und
Eingabemaske · jede Abschnittsüberschrift stand mehrfach, weil die
Rechenreihenfolge zwischen den Bauteilen springt · `Nachweis(e)`.

Davor, zwei gemeldete Fehler: die Zusammenfassung packte die Nachweise mehrerer
Platten in dieselbe Tabelle (sie schloss aus dem Anzeigetext auf die Platte —
jetzt trägt jedes Urteil den Namensraum seines Nachweises) · eine noch leere
Zulage stand auf «Anzahl» statt auf «Teilung».

## Erledigt in der Runde davor

Querkraft vollständig nachrechenbar, je Fall ein eigener Nachweis,
`V_Rd(M_Ed, N_Ed)`, `m_Dd = |min(N_Ed;0)|·h/6`, `k_g` mit Riegel · Abschnitte
in der Herleitung · Lagentabelle mit Teilung, Stahlsorte und Fläche statt fünf
gleicher Formeln · eindeutige Indizes · Zusammenfassung je Platte mit
Bewehrungsmass und Distanzhalterhöhe · Umfangsschalter steuert Zusammenfassung
und Herleitung · Schrittweiten der Pfeile · Schalter günstige/ungünstige Lage ·
y-Bewehrung im Querschnittsbild als Rechteck.
