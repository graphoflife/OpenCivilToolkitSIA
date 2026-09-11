# Was noch offen ist

Reihenfolge ungefähr nach Dringlichkeit. Erledigtes wandert raus — was dabei
gelernt wurde, steht in [ENTWICKLUNG.md](ENTWICKLUNG.md).

---

## Fehler

- [ ] **Querkraftnachweis zeigt nur analytische Formeln, keine Zahlen.**
      Damit ist er nicht nachrechenbar — der einzige Zweck des Werkzeugs.

## Querkraft

- [ ] Je Kombination ein eigenständiger Nachweis. Der Widerstand hängt von der
      Einwirkung ab, also gibt es kein gemeinsames `v_Rd`.
- [ ] Ausweisen als `V_Rd(M_Ed = …, N_Ed = …)` — in der Zusammenfassung **und**
      in der Herleitung.
- [ ] `m_Dd = |min(N_Ed; 0)| · h / 6` — nur Druck zählt, Zug wird ignoriert.
- [ ] `k_g = max(1.20; 48 / (16 + D_max · min[1.0; (60/f_ck)²]))` — der untere
      Riegel bei 1.20 fehlt bisher.

## Mittleres Feld (Eingaben)

- [ ] Der Abschnitt unter *Nachweise* heisst **Tragsicherheitsnachweise**,
      nicht *Einwirkungen*.
- [ ] Schrittweiten der Pfeiltasten:
      - Teilung → nächster Vielfacher von **25**
      - Durchmesser → nächster aus **6, 8, 10, 12, 14, 16, 18, 20, 22, 26, 30, 34, 40**
      - Stabzahl → **1**
- [ ] Schalter **Ungünstige Lage / Günstige Lage** für alle vier Lagen, im Stil
      der x|y-Schalter, aber in anderer Farbe. Vorgabe: *ungünstig*.
      - *günstig* = heutiges Verhalten (beide Eisen auf derselben Hülle, je um
        ihren Halbmesser eingerückt)
      - *ungünstig*, Lage 1 und 2: das **dünnere** Eisen von Grund/Zulage wird
        nach oben geschoben, sodass beide dieselbe **Oberkante** haben
      - *ungünstig*, Lage 3 und 4: umgekehrt — gleiche **Unterkante**, das
        dickere Eisen ist massgebend

## Rechte Tafel

- [ ] Reiter *Nachweise* heisst **Zusammenfassung**.
- [ ] Dort **eine Tabelle je Plattenquerschnitt**.
- [ ] Der Schalter *Gesamt / Aktuelle Seite* steuert **Zusammenfassung und
      Herleitung**: entweder alle Platten oder nur die gewählte. Ist ein
      Material gewählt und *Aktuelle Seite* aktiv, bleibt die Zusammenfassung
      leer.
- [ ] Unter jeder Tabelle zwei Angaben zur Platte:
      - **Bewehrungsmass** in kg pro m³ Beton (Stahldichte 7850 kg/m³)
      - **Höhe der Distanzhalter**: liegen 2. und 3. Lage auf derselben Höhe,
        von OK 2. Lage bis UK 3. Lage; sonst von OK 1. Lage bis UK 3. Lage.
        Massgebend ist je das dickere Eisen aus Grundbewehrung und Zulage.

## Offen aus früheren Runden

- [ ] **Die Sortentabellen sind ungeprüft.** `BETONSORTEN` und `STAHLSORTEN` in
      `material/` stammen aus der Vorgängerfassung und sind nie gegen die
      gedruckte SIA 262 gehalten worden. Dasselbe gilt für sämtliche
      Normverweise. Vor ernsthaftem Gebrauch nachschlagen.
- [ ] Keine Testumgebung für das JavaScript. `stabstellen`, `besterVersatz` und
      `beschriftungenEntzerren` sind rein und wären in wenigen Zeilen abgedeckt;
      geprüft wird bisher von Hand im Browser.
- [ ] Normstelle für den vereinfachten Spannungsblock (0.15·ε_c2d … f_cd) fehlt
      — bewusst leer gelassen, statt eine Ziffer zu erfinden.
