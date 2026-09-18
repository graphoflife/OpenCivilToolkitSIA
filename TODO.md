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

## Erledigt zuletzt

Das Gradzeichen hatte keine Basis (`\,^{\circ}`) — KaTeX brach daran ab und
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
