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
- [ ] In den Tabellenspalten springt die Stellenzahl: `205` steht neben
      `224.5`, `1.6` neben `0.99`. `Groesse.formatiert()` streicht
      nachlaufende Nullen — im Fliesstext richtig, in einer Zahlenkolonne
      nicht. Die Spalte bräuchte die Rohzahl samt `stellen`; heute kommt sie
      fertig formatiert aus dem Kern.

## Erledigt zuletzt

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
