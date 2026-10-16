# Was noch offen ist

Reihenfolge ungefähr nach Dringlichkeit. Erledigtes wandert raus — was dabei
gelernt wurde, steht in [[Entwicklung]].

---

## Offen


- [ ] **Die Sortentabellen sind ungeprüft.** `BETONSORTEN` und `STAHLSORTEN` in
      `material/` stammen aus der Vorgängerfassung und sind nie gegen die
      gedruckte SIA 262 gehalten worden. Dasselbe gilt für sämtliche
      Normverweise. Vor ernsthaftem Gebrauch nachschlagen.
- [ ] Normstelle für den vereinfachten Spannungsblock (0.15·ε_c2d … f_cd) fehlt
      — bewusst leer gelassen, statt eine Ziffer zu erfinden. Er ist jetzt
      auch ein wählbares Gesetz der Querschnittsanalyse («Spannungsblock
      0.85·x»).
- [ ] Der Riegel `k_g ≥ 1.20` ist nach Vorgabe eingebaut, aber nicht gegen die
      Norm geprüft. Bei D_max = 32 mm und C30/37 greift er (roh 1.00 → 1.20)
      und senkt den Querkraftwiderstand um gut 4 %.
- [ ] Normstellen für 112 von 176 Formeln fehlen noch -- die Liste samt
      Stelle im Code steht auf der Übersicht der [[Formelsammlung]]. Sie
      kommen vom Benutzer und werden im Code eingetragen (`referenz=`).
- [ ] Verformung und «Plattendicke optimieren»: **entschieden, noch nicht
      umsetzen** (Benutzer, 2026-10-16). Bei der Dickensuche wird der
      Verformungsnachweis ignoriert, denn w hängt von der Plattendicke ab: es
      gehört zur eingegebenen Dicke und wächst bei gleicher Last mit 1/h³.
      Kein Umrechnen mit (h₀/h)³. Erst umsetzen, wenn der Benutzer es sagt;
      bis dahin hält die Suche w fest wie eine Einwirkung.
- [ ] Verformung der Platte: der Grenzwert w_max = L/350 und dass w mit der
      Steifigkeit E_cm ermittelt ist, sind nach Vorgabe eingebaut, nicht
      nachgeschlagen (`nachweis/verformung.py`, `GRENZE`). Die Normstelle dazu
      fehlt; die des Vergrösserungsfaktors (4.4.3.2.5) hat der Benutzer
      geliefert.
- [ ] **Grundbruch: die Quelle benennen.** Die Formeln stehen mit «Kap.
      9.2.x» am Code (`geotechnik/grundbruch.py`, `KAP_*`); der Titel des
      Buches fehlt. Er kommt vom Benutzer.
- [ ] Grundbruch, nach Vorgabe, nicht nachgeschlagen: b_γ mit tan φ wie
      Tabelle 9.2.18 (der Text schreibt tan α); Wasser unter der Sohle, aber
      im Gleitkörper, rechnet mit γ' statt der verlangten
      Stabilitätsberechnung; eine Klammer der Lastneigung unter null gilt
      null; δ*/φ als Eingabe mit Vorgabe 1; gerechnet wird mit den
      Teilsicherheiten auf φ und c, ein globaler Sicherheitsgrad wie F_stat
      des Kapitels kommt nicht dazu. Vom Benutzer bestätigen lassen.
- [ ] Grundbruch: keine Ausmitte der Last (wirksame Breite), kein
      Erdwiderstand vor dem Fundament. Der Gleitkörper im Bild gilt für
      waagrechte Sohle und waagrechtes Gelände.
- [ ] Der Dienst «bericht» und das PDF des lokalen Servers haben seit dem
      Wegfall des Knopfs «Bericht» keinen Weg mehr aus der Oberfläche.
      Entfernen, oder wieder erreichbar machen.
- [ ] Obsidian: einmal im Tresor prüfen, ob Seiten mit Punkt im Namen
      (`opencivil.core.protokoll`) sauber verlinken. Sonst die Namen ohne
      Punkt schreiben.
- [ ] Keine Testumgebung für das JavaScript. Eine erste Brücke steht:
      `tests/test_markdown_js.py` gibt ein Modul ohne Imports node als
      `data:`-Adresse. Für die übrigen fehlt sie noch: `stabstellen`, `besterVersatz`,
      `naechsteStufe` und `beschriftungenEntzerren` sind rein und wären in
      wenigen Zeilen abgedeckt; geprüft wird bisher von Hand im Browser.
      Dazu jetzt das Modell des Zeichenfensters (`cad_modell.js`: Knoten
      anlegen, löschen, kopieren, je Element verschieben, zusammenführen),
      das Fangen und welche Ecke ein Klick nimmt.
- [ ] Balkensystem im schmalen Fenster: das schwebende Fenster eines Knotens
      oder Stabs deckt die halbe Zeichnung. Zuklappen geht, aber bei Lasten
      mit vielen Feldern wird es lang.
- [ ] Keine Testumgebung für die Zeichenhilfen des Balkensystems
      (`bs_symbole.js`, die verbundene Zeichnung in `cad_modell.js`) --
      geprüft von Hand im Browser.

## Umbau: Befunde der Strukturdurchsicht (2026-10-12)

Neun Durchsichten haben je einen Bereich ganz gelesen; jeder Punkt ist am
Code nachgeprüft. Reihenfolge nach Empfehlung. Ziel jedes Punkts ist, dass
etwas wegfällt, nicht dass es umzieht. Behoben sind der dringendste
Befund, die gemischten Stahlsorten, dazu «Ergebnisse in den Rechenlauf»
und «Ein Steckbrief je Bauteilart» (siehe [[Entwicklung]]).

- [ ] **Ein Querschnittsmodell statt zweier.** Gerechnet wird mit den
      Closures in `querschnittsloeser.py` (`beton_nichtlinear`,
      `stahl_bilinear`, `stahl_nur_zug`), gedruckt mit den Klassen in
      `werkstoffgesetz.py` -- `rechenwahl.py` baut dafür ein
      Platzhalter-`Betongesetz(0.0, 1.0, 1.0, 0.0)` nur fürs LaTeX. Jenseits
      ε_c2d und beim gedrückten Stahl unterscheiden sie sich schon; k_σ steht
      dreimal. Der Dehnungsfächer steht zweimal (`dehnungsfaecher.faecher`
      von Hand, `interaktion.py` aus den Dehnungsgrenzen), Punkt C dreimal.
      Die Rechenart wird in sieben Modulen einzeln abgefragt, die Analyse
      vergleicht rohe Texte («block», «bemessung»). Besser: ein Gesetz ist
      ein Objekt mit `__call__` und `latex()` wie `Spannungsblock`, der Fächer
      kommt aus `Dehnungsgrenzen`, je Rechenart eine Tabellenzeile. Vorher
      die Geschwindigkeit der Closures messen.
- [ ] **Eine Grundlage für die Apps mit Zeichenfenster.** `bs_zeichnung.js`
      ist aus `qa_zeichnung.js` kopiert, rund 150 Zeilen wortgleich bis auf
      `a.qa`/`a.bs`, und läuft schon auseinander (Fehler des Kerns: kurze
      Meldung gegen Text unter der Zeichnung). Dazu vier selbstgebaute
      Zwischenspeicher für Nebenanfragen mit vier Fehlerregeln
      (`bs_diagramme.js`, `qa_diagramme.js`, `app.js`, `bericht.js`).
      Besser: `cadApp({…})` liefert Lesen, Schreiben, Fenster, Liste,
      Markierung und eine `kernAntwort`; `nachgefragt(schluessel, holen)`
      merkt sich Antworten bis zur nächsten Lösung.
- [ ] **Keine Rechnung und keine Norm in der Oberfläche.** Beim
      Darüberfahren verbindet `bs_diagramme.js` zwei Proben gerade, obwohl
      der Kern den Wert genau kennt; Grenzwerte und grösste Durchbiegung
      wählt das JS selbst (dieselbe Regel in `stabwerk/herleitung.py`).
      Hilfetexte wiederholen Regeln des Kerns -- «x/d ≤ 0.35»
      steht neben einem Feld bis 0.5 (`nachweise.js`) --, eine Normstelle
      steht in `editor.js`, Wert-IDs werden aus Text nachgebaut
      (`zustand.js` `namensraum`). Besser: eine `Fallauswertung` im
      Stabwerk für Herleitung und Bildschirm -- für die Lagerkräfte gibt es
      sie schon (`Systembefund.lagerkraefte`) --, Anzeige auf der nächsten
      Probe, Hilfetexte und Formeln aus denselben Konstanten über den
      Katalog.
- [ ] **Balkensystem: Kennung statt Name.** Ein Fall wird an seinem Namen
      erkannt, gleiche Namen sind darum verboten -- seit 2026-10-15 als
      Meldung am System, nicht mehr als Fehler des ganzen Projekts. «Fest»
      reist als `math.inf` und wird in
      `system.py` an 17 Stellen zurückübersetzt; Stäbe und Lasten werden in
      vier Durchgängen aufgelöst, mit einem Schalter `melden`; die
      Querschnittsart wird in drei Schichten verzweigt. Besser: LF1/LK1 als
      Identität, `Halt(fest, feder)`, Lasten einmal je Fall auflösen,
      `_stabquerschnitt` liefert Eingaben und Formeln.
- [ ] **Varianten im Kern -- deine Entscheidung.** `prioritaet`,
      `bedingung`, `anwendbar`, `verworfene_varianten` benutzt ausserhalb des
      Kerns niemand. Wer zwei Berechnungen für denselben Wert anmeldet
      (kopierter Namensraum), bekommt keinen Fehler, sondern still eine
      Variante; die zuerst angemeldete gewinnt. Empfehlung: ein Erzeuger je
      Wert, `registriere` wirft beim zweiten. War eine Gründungsentscheidung.
- [ ] **Dateien über 1000 Zeilen**, je entlang einer Naht, die schon da ist:
      `cad_fenster.js` (Bedienung, Rückgängig, Punkteingabe auslagern; die
      Befehle stehen in vier Listen, Knöpfe täuschen Tastendrücke vor),
      `querkraft.py` (zwei Nachweise hinter `if self.buegel is not None`:
      Fachwerk, ohne Bügel, mit Bügeln; die Regel für d_v steht in Kurve und
      Nachweis je einmal), `nachweise.js` (die Fenster für Riss und
      Verformung in ein eigenes Modul), `spannungsanalyse.py`, `aufbau.py`
      und `querschnittsloeser.py` (entlang ihrer Abschnittsmarken), `stil.css`
      (ein Blatt je App). Stand 2026-10-16: stil.css 2248 Zeilen, die übrigen
      1066 bis 1330.
- [ ] **Der Posten als `Postenbezug` statt als 5-Tupel.** Ein
      Bewehrungsposten reist als `(Lage, Art, Posten, ID von A_s, ID von z)`
      und wird rund zwanzigmal nach Position zerlegt; die Marke
      `f"{lage.nummer}{art.kuerzel}"` wird an neun Stellen neu gebaut, obwohl
      `Postenbezug` daneben schon entsteht (`platte.py`, `_aufbauen`). Rest von
      Befund 1 -- der Stahl je Lage ist behoben, die Gestalt des Postens nicht.
- [ ] **Kleineres:** die Regel für einachsige Biegung steht in drei Modulen
      und ist auseinandergelaufen (`M_y > 0` in `richtungsnachweise.py`,
      `M_y >= 0` in `schiefe_biegung.py`) · `print(ergebnis)` hat eine
      dritte, abweichende Zusammenfassung (`konsole.py`) · die Herleitung am
      Bildschirm lässt unbekannte Blockarten still weg (`bericht.js`) ·
      `Unterprotokoll` ruft keine Rechnung auf, sein `tiefe` läuft durch 24
      Darstellungsfunktionen · `BEREICHE.get(…, "")` legt eine neue Art
      still unter «Weitere» · neun Nachweise bauen ihr Urteil je selbst und
      nennen jeden Erfüllungsgrad zweimal · der Schalter `schnell` bündelt
      vier Verhalten für zwei Nutzer.

## Offene Normfragen — deine Fragen, unbeantwortet

Diese Punkte sind **nicht** entschieden. Ich habe je eine Annahme eingebaut und
sie hier notiert; keine davon ist nachgeschlagen.

- [ ] **Die Grenze des Nachweises gegen Fliessen.** Eingebaut `f_yd − 80 MPa`,
      weil Tabelle 17 ausdrücklich `f_yd` nennt — mit charakteristischen
      Werten in der Rechnung mischt das zwei Niveaus, ist aber die strengere
      Seite. Womit die Stahlspannung rechnet (φ, Werte, Rechenart), wählt
      jedes Kapitel; Vorgabe elastisch, charakteristisch, φ = 0.
- [ ] **Welcher Durchmesser bestimmt `σ_s,adm` unter quasi-ständiger Last?**
      Eingebaut: der dickste Stab der Tragrichtung. Die Spannung kommt aus dem
      ganzen Querschnitt, und welche Lage am stärksten gezogen ist, wechselt
      mit dem Lastfall; der dickste Stab gibt die kleinste Grenze. Denkbar
      wäre auch der Stab der jeweils am stärksten gezogenen Lage.
- [ ] **60 % und 70 % sind Abschätzungen, keine Normwerte.** Beide sind je
      Platte einstellbar; wer die echten ψ-Kombinationen kennt, trägt sie als
      eigene Lastfälle ein.
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
- [ ] **k_σ der Parabel aus `E_cm/(1+φ)`.** Die Parabel rechnet überall --
      Tragsicherheit, Knicken, Stahlspannung, Analyse -- mit
      `k_σ = max(1; E_c,eff/(400·f_c))`, `E_c,eff = E_cm/(1+φ)` und `f_c` des
      Wertesatzes. Der Beton hat daneben sein `k_σ = E_cd/(400·f_cd)`
      (4.2.1.6); mit `γ_cE = 1` ist das bei φ = 0 dieselbe Zahl. Ob für
      die Tragsicherheit `E_cd` und für das Kriechen der Modul der richtige
      Ort ist, ist nach Vorgabe, nicht nachgeschlagen.
- [ ] **Die Handrechnung als Rechenart im Löser.** Bei der Stahlspannung
      rechnet «Handrechnung» wie die Resistenzlinie aus Handrechnung
      (Knicken und Analysen bieten sie seit 2026-10-12 nicht mehr an):
      Spannungsblock, gedrückter Stahl weggelassen, je Seite eine Lage im
      Schwerpunkt, der Beton auch dort gezählt, wo der Stahl liegt. Ein
      Modell, keine Normregel — nach Vorgabe. Dazu bekommt der Stahl im Löser das Druckplateau `f_y,druck`
      wie die genaue Linie; bei den Normsorten ist es gleich `f_y`.
- [ ] **Querkraft mit `m_Rk`.** Rechnet die Tragsicherheit charakteristisch,
      nimmt die Querkraft ohne Bügel ihr `m_Rk(N_Ed)` aus derselben Linie, ihr
      eigenes `τ_cd` und `f_yd` bleiben aber Bemessungswerte. Das mischt zwei
      Niveaus — nach Vorgabe, nicht nachgeschlagen.
- [ ] **Der Vergrösserungsfaktor w/w_c** (SIA 262:2025, 4.4.3.2.5, Formel von
      dir): `d′` reicht vom gezogenen Rand bis zur Gegenlage (deine
      Festlegung), also ist `ρ′` das `ρ` der Gegenseite; ohne Gegenlage ist
      `ρ′ = 0`. Gezählt wird nur die x-Bewehrung, Grund und Zulage einer Seite
      im Schwerpunkt. Der Gültigkeitsbereich ist nicht geprüft — etwa
      `1 − 20·ρ′ ≤ 0` ab `ρ′ = 5 %` gäbe einen negativen Faktor.
- [ ] **Der äquivalente E-Modul** (Spannung-Dehnung-Analyse, M–E_eq und
      N–E_eq) zählt die Verformung ab dem Zustand ohne laufende Kraft (deine
      Wahl, 2026-10-11): `E_eq = M/(I_c·(χ − χ_0))`. Ein Modell mit dem
      ungerissenen Betonquerschnitt gibt damit die Verformung aus der
      laufenden Kraft wieder, nicht, was die feste allein verformt. Er gilt
      für den Querschnitt, ohne Zugversteifung -- für eine Durchbiegung liegt
      er damit tief (sicher), für Zwangkräfte nicht. Keine Normstelle.
- [ ] **Der kürzeste Abstand bei der genauen Linie** misst zum gezeichneten
      Polygon des Fächers (80 Schritte je Abschnitt), nicht zum genau
      gesuchten Rand wie Normalkraft und Moment konstant.

### Querschnittsanalyse

Je eine Annahme eingebaut, im Code mit «nach Vorgabe, nicht nachgeschlagen».

- [ ] **C-Punkt bei beliebiger Form.** Eingebaut: ganz gedrückt darf der
      Beton am Punkt im Abstand `(1 − ε_c1d/ε_c2d)·h` vom gedrücktesten Rand
      nicht über `ε_c1d` gestaucht werden, mit `h` als Ausdehnung des Betons
      senkrecht zur Nulllinie. Bei der Platte ist das die bekannte Regel; ob
      sie für L, T oder Kasten so gilt, steht dahin.
- [ ] **Federmodell und Bredt.** Eingebaut: die Querkraft verteilt sich nach
      der Steifigkeit `k = b_w·l` (reine Verschiebung), das Versatzmoment
      tragen die Zellen nach Bredt, mehrzellig mit gleicher Verdrillung. Ohne
      Zelle tragen die Federn die Torsion mit Drehung. Ein Modell, keine
      Normregel.
- [ ] **Längszugkraft in der Wandmitte.** Eingebaut: `ΔN = |q|·l·cot α` je
      Stück einer Wand, angreifend in seiner Mitte; daraus `ΔN`, `ΔM_y`,
      `ΔM_z`. Gleichwertig mit `V·cot α / 2` in jedem Gurt, aber nicht
      nachgeschlagen.
- [ ] **k_t bei beliebiger Form.** Eingebaut: wie bei der Platte mit `h/3`,
      wobei `h` die Ausdehnung des Betons in Biegerichtung ist (z für M_y,
      y für M_z).
- [ ] **Duktilität in beliebiger Richtung.** Eingebaut: x und d senkrecht zur
      Nulllinie, x ab dem gedrücktesten Betonpunkt, d bis zum entferntesten
      gezogenen Stab -- in den Richtungen Zug unten, oben, links, rechts.
- [ ] **Wanddicke im vollen Querschnitt.** Wie dick eine Schubwand in einem
      Rechteck anzusetzen ist, sagt das Werkzeug nicht -- das gibt der
      Benutzer ein. Das Beispiel nimmt 100 mm auf der Bügelachse; eine Regel
      dafür ist nicht nachgeschlagen.
- [ ] **Spannung-Dehnung-Analyse je Zugseite.** Eingebaut
      (`querschnitt/schnittanalyse.py`): die Nulllinie bleibt parallel zur
      Achse, wie einachsig -- das Moment um die andere Achse, das ein
      unsymmetrischer Querschnitt dabei weckt, zählt nicht. Der Riss am
      ungerissenen Bruttoquerschnitt, `M_Riss(N) = (f_ct,eff − N/A)·W` und
      `N_Riss(M) = (f_ct,eff,t − M·v/I)·A`, mit `k_t` für ein Drittel der
      Tiefe bzw. die ganze, wie bei der Platte; `f_ctm` und `E_cm` vom Beton
      am gezogenen Rand. Der äquivalente Modul am Bruttoquerschnitt (`I`, `A`).
- [ ] **Gebrauchsnachweise.** Eingebaut (`nachweis/qa_gebrauch.py`), je auf
      Vorgabe des Benutzers vom 2026-10-15: die Zwängung auf Normalkraft am
      ganzen Querschnitt, `N_Riss = Σ A_c·k_t·f_ctm` mit `t` als kleinerer
      Abmessung des Betons (umschreibendes Rechteck, wahlweise ≤ 500 mm),
      gegen `Σ A_s·σ_s,adm` aller Stäbe; die Zwängung auf Biegung je
      Richtung mit dem Rissmoment des spröden Versagens gegen das Moment, bei
      dem der erste gezogene Stab `σ_s,adm` erreicht -- gerissen, elastisch,
      ohne N, mit eigenem φ, die gedrückte Bewehrung wirkt mit (die Platte
      lässt sie weg). `σ_s,adm` je Stab mit seinem Durchmesser und dem
      `f_ctm` seines Betons; eine verschmierte Linie mit einem fiktiven
      Durchmesser bei 150 mm Teilung (`nachweis/stabgrenzen.py`).
- [ ] **Knicken je Richtung.** Eingebaut (`nachweis/qa_knicken.py`): je Fall
      zu einer Zugseite, die Nulllinie parallel zur Achse wie einachsig --
      ein unsymmetrischer Querschnitt, der um beide Achsen zugleich knickt,
      wird nicht erfasst. `d` für die Mindestausmitte `d/30` vom gedrückten
      Rand bis zum entferntesten Stab in Zugrichtung. Die Regeln der Platte,
      übertragen; nach Vorgabe, nicht nachgeschlagen.

### Balkensysteme

Im Code mit «nach Vorgabe, nicht nachgeschlagen».

- [ ] **Welche Steifigkeit?** Eingebaut: E_cm für Beton, E_s für Betonstahl,
      am ungerissenen Bruttoquerschnitt, ohne Schubverformung, Theorie
      1. Ordnung (`stabwerk/rechnung.py`, `E_MODUL`). Für Verformungen im
      Gebrauch ist ein gerissener Stahlbetonbalken weicher, unter Dauerlast
      kriecht er; die Schnittgrössen eines unbestimmten Systems hängen daran.
- [ ] **Platte als Stabquerschnitt.** Eingebaut: ein Streifen b × h mit den
      Formeln des Rechtecks, ohne Bewehrung -- b ist die betrachtete Breite
      der Platte.

## Noch nicht gebaut

- [ ] **Balkensysteme, nächste Schritte:** Eigengewicht aus Querschnitt und
      Wichte, Umhüllende der Kombinationen, Theorie 2. Ordnung,
      Schubverformung, schiefe Lager, und die Schnittgrössen eines Stabs als
      Einwirkung einer Platte oder Querschnittsanalyse.

- [ ] **Querschnittsanalyse, nächste Schritte** (je ein eigener Plan):
      Baustahl (Sortentabelle, Gesetz, Verbundquerschnitt, Stahlwände mit
      eigenem G), Holz (wie spröd Zug und Druck sind, legen wir vorher fest),
      weitere Nachweise (Wände ohne Bügel).
- [ ] **Die genaue Linie der Platte über den neuen Fächer.** Die Platte hat
      noch ihren eigenen `dehnungsfaecher`; der Fächer der Analyse kann
      dasselbe für jede Form. Seit beide ihren Widerstand genau suchen, liegen
      sie unter 0.01 % beisammen (`tests/test_interaktion.py`) -- umstellen
      ginge, die Fasern legen sie verschieden.
- [ ] **Kriechzahl φ an den Flächen der Querschnittsanalyse.** Die
      Stahlspannungen und die Zwängung auf Biegung rechnen mit dem φ ihres
      Kapitels, wie bei der Platte -- für jeden Beton dasselbe. Ein φ je
      Fläche bräuchte es erst, wenn zwei Betone verschieden kriechen sollen.
      Die Eigenschaften einer Fläche stehen im schwebenden Fenster; φ käme
      dort ohne Umbau dazu.
- [ ] **Ein Kreis ist ein 48-Eck.** Die Ecken liegen auf dem Kreis, die
      Fläche ist darum 0.3 % kleiner als π·D²/4. Steht so in der Zeichnung;
      wer es genauer will, zeichnet mehr Ecken.

- [ ] **Neu gerechnet wird je Bauteil, nicht je Wert.** Eine Platte, deren
      Beschreibung sich nicht geändert hat, kommt aus dem Zwischenspeicher --
      das war das Ziel und es steht. Innerhalb einer Platte wird aber weiter
      alles gerechnet: ein umgelegter Duktilitätsschalter rechnet den
      Knicknachweis derselben Platte mit, obwohl der nichts davon weiss. Feiner
      ginge es erst, wenn die Nachweise ihre Lastfälle nicht mehr im Bauch
      trügen, sondern über Bezüge -- heute hätte ein Knickfall mit geänderter
      Normalkraft denselben Bezugsgraphen wie vorher, und ein feiner Abdruck
      sähe den Unterschied nicht. Das wäre ein Umbau an jedem Nachweis, und der
      Fehlerfall wäre eine stillschweigend falsche Zahl.
- [ ] **Die M-χ- und die N-ε-Linie zeigen den Querschnitt, ohne
      Zugversteifung.** Ungerissen bis zum Riss, dort der Sprung, darüber
      gerissen. Für die Durchbiegung eines Bauteils fehlt die
      Mitwirkung des Betons zwischen den Rissen. Bis 2026-10-06 stand sie als
      `ζ = 1 − β·(M_Riss/M)²` mit β = 1.0 drin (üblich: 1.0 kurzzeitig, 0.5
      dauernd oder wiederholt) -- dafür war der Sprung nicht zu sehen. Ob eine
      Linie des Bauteils dazukommt, mit welcher Regel und welchem Beiwert nach
      SIA 262, ist nicht nachgeschlagen. Für eine Durchbiegung ist der
      kleinere Beiwert (weicher) der ungünstige, für eine Zwängung der
      grössere.
- [ ] **Das Rissmoment der Momenten-Krümmungs-Linie** gilt am
      Bruttoquerschnitt ohne Stahl, `M_Riss(N) = M_Riss(0) − N·h/6` (Zug
      positiv) -- Annahme, nicht nachgeschlagen. Sein f_ct,eff hat k_t für
      `t = h/3`, auch unter Zug: Biegung bleibt bei h/3, nach Vorgabe
      (2026-10-09). Der ungerissene Zustand
      daneben rechnet mit Stahl und Kriechzahl und ist steifer: am Beispiel
      steht sein gezogener Rand beim Rissmoment bei 2.14 statt
      f_ct,eff = 2.76 N/mm². Ob für die Linie der ideelle Querschnitt gelten
      soll, ist offen.
- [ ] **Die Rissnormalkraft der N-ε-Linie** ist dieselbe Bedingung nach N
      aufgelöst: `N_Riss(M) = f_ct,eff·b·h − 6·|M|/h`, am Bruttoquerschnitt
      ohne Stahl, mit `k_t = 1/(1 + 0.5·t)` für die ganze Dicke, `t = h` --
      nach Vorgabe (2026-10-09), nicht nachgeschlagen. Das Rissmoment der
      M-χ-Linie bleibt nach Vorgabe bei `t = h/3`. Beim selben N und M reissen die
      beiden Linien darum nicht am selben Punkt: am Beispiel reisst die M-χ-
      Linie bei N = 300 kN bei 26.4 kNm, die N-ε-Linie bei M = 26.4 kNm
      schon bei 228 kN.
- [ ] **k_σ der Parabel nie unter 1.** Mit dem kriechweichen Modul
      `E_cm/(1+φ)` und charakteristischen Werten wird `E_c/(400·f_c)` kleiner
      als 1 (C30/37, φ = 2: 0.93); dann hätte der Nenner der Parabel im
      ansteigenden Ast eine Nullstelle. Angesetzt wird `max(1; E_c/(400·f_c))`:
      der Beton ist dann bis f_c bei ε_c1d linear -- nach Vorgabe, nicht
      nachgeschlagen. Ob die Norm das Kriechen über den Modul oder über die
      Dehnungen (ε_c1d·(1+φ)) ansetzt, ist offen.
- [ ] **Das Ende der Linien** liegt an den Grenzen des Dehnungsfächers:
      Betonrand −ε_c2d, Stahllagen ±ε_ud, Punkt C −ε_c1d bei
      `z_C = h·(1 − ε_c1d/ε_c2d)`. Dieselben Grenzen wie in
      `nachweis/dehnungsfaecher.py`, nach Vorgabe, nicht nachgeschlagen.
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

Eingaben an einer Stelle geprüft (C1, 2026-10-16): ein Leser aus den Feldern
der Datenklassen, streng, und dieselbe Prüfung vor jedem Rechnen -- die
Fassade geht durch dieselbe Tür wie eine Datei · alte Formate weg · die
Rissanforderung in einer Tabelle statt in vier · was beim Rechnen still einen
Ersatz nahm, meldet sich: ein Posten ohne Teilung, eine Knicklänge null, Stäbe
und Bügel ohne Stahl, ein Kennwert «fck», zwei gleiche Kennungen, ein Mass
«B» am Stabquerschnitt, eine leere Teilungsliste der Suche ·

Vom Benutzer entschieden (2026-10-16): die Kennzahlen der Platte bleiben, wie
sie sind -- x/d je Seite, mit Bügeln das Kleinere beider Seiten, von Hand mit
Bemessungswerten · eigener Betonstahl heisst S1, S2 … statt BS1 ·

Vier sichtbare Punkte: eine Bügelteilung von null wird gemeldet statt still
zu 200 mm · gleiche Fallnamen im Balkensystem halten nur das System auf ·
die Lagerkräfte am Bildschirm mit den Summen von Linienlager und Bettung,
dieselben Zeilen wie in der Herleitung · «kNm» in der Herleitung der Platte
ist richtig, M und N gelten je Streifen b (siehe [[Arbeitsweise]]) ·

Ein Steckbrief je Bauteilart: `BAUTEILE` im Kern und `ARTEN` in der
Oberfläche, ein Test hält beide gleich · je Bauteil ein Datensatz mit
Nachweisen, Zielen und Bezügen statt Kennungen wie «q1.x» zu zerlegen ·
die Bewehrungssuche rechnet nur ihr Bauteil ·

Ergebnisse in den Rechenlauf: Urteile und Befunde kommen mit der Ausführung,
kein Nachweis legt mehr etwas auf sich ab · der Speicher legt je Bauteil
seine Lösung ab · ein Ziel darf eine Berechnung sein -- die Zahl der
Unbekannten, die Zeilenzahl des Blatts und der Querkraft-Nullfall sind fort ·

Gemischte Stahlsorten: Stahlspannung, Knicken, Querkraft und Analyse
nahmen den Stahl der ersten Lage für alle Lagen -- jetzt trägt jede Lage
ihren Stahl, gebaut an einer Stelle (`stahllagen`) · Stahlspannung je Stahl
mit eigener Grenze, massgebend der kleinste Erfüllungsgrad · Querkraft mit
dem Stahl der gezogenen Seite · Fliessbeginn der Analyse je Lage ·

2D Balkensysteme: ebener Rahmen nach der Steifigkeitsmethode im eigenen
Kern `stabwerk/` · Gelenke, Federn, Bettung, feste Linienlager, Knoten auf
Stäben, Kombinationen · bewegliches System als Meldung, gestrichene
Drehung ohne Steifigkeit · Querschnitte nach Vorlage, von Hand, aus Platte
oder Analyse · Herleitung mit Matrizen und Gleichgewichtsprobe ·
Zeichenfenster verbunden, Teilen und Umkehren im Kern · Bilder mit Werten
beim Darüberfahren ·


Platte geprüft ([[Prüfung M_Rd der Platte]]): im M-χ-Bild heisst der
Fliessbeginn M_y und das Ende M_Rd, wie der Tragwiderstand · Rechenarten
heissen Handrechnung, 0.85·x-Vereinfachung und Präzise ohne Vereinfachung ·
Handrechnung nur noch in Tragsicherheit und Stahlspannungen · Linie
«ungerissen» nur bis zum Riss · E_eq-Ecken mit Vielfachem von E_cm ·

Rechenwahl je Kapitel: Tragsicherheit, beide Stahlspannungen, Knicken
(Verformung und Widerstand), Zwängung auf Biegung und jede Analyse wählen φ,
Werte und Rechenart selbst, φ = 0 als Vorgabe · Die Tragsicherheit hält mit
Block oder Parabel gegen den Rand des Dehnungsfächers, den Widerstand bei N_Ed
genau gesucht, mit der Probe in der Herleitung; charakteristisch heissen die
Widerstände M_Rk und N_Rk · Querkraft und sprödes Versagen lesen aus
derselben Linie · Das Knicken teilt sie bei gleicher Wahl, sonst baut es eine
eigene, die im Diagramm daneben steht · Der Vergrösserungsfaktor w/w_c je
gezogene Seite, mit dem φ der Platte · k_σ nie unter 1 · Das Fenster des
Knickens stand als −3.0 ‰ da, gerechnet wird mit −3.5 ‰ ·

Stahlspannung unter quasi-ständiger Einwirkung: dieselbe Rechnung wie gegen
Fliessen, mit 60 % statt 70 % und gegen `σ_s,adm` aus der Rissanforderung
(`f_yk` bei normaler, die Wurzelformel mit `w_nom` bei erhöhter und hoher) —
geführt bei jeder Anforderung · Eine Klasse, zwei Grenzen
(`GrenzeGegenFliessen`, `GrenzeAusRissbreite`) statt eines kopierten Kerns ·
Beide Anteile je Platte einstellbar, 60 und 70 als Vorgabe · Die
Werkstoffgesetze im Gebrauchszustand charakteristisch: Plateau bei `f_yk`
statt `f_yd`, Beton gedeckelt bei `f_ck` (`Werkstoffsatz` im Löser) ·
Fliesst der Stahl, wird an der Dehnung gemessen — sonst stünde bei normaler
Anforderung `f_yk` gegen `f_yk` mit «erfüllt» da · Im schnellen Aufbau der
Suche entstehen ganz stille Nachweise nicht: 29 → 2.5 ms je Bewertung bei
erhöhter Anforderung · Fallnamen stehen als `\text{…}` in den Symbolen —
`Feld__60___` war ein doppelter Index, und KaTeX brach daran ab ·
Fallnamen, die auf dieselbe Wert-ID fallen («Feld A», «Feld-A»), werden
gemeldet ·

Nachgewiesen wird nur noch die Tragrichtung x; die y-Lagen bleiben im
Querschnitt, weil sie die statische Höhe von x bestimmen und zum
Bewehrungsgehalt zählen · Vorgabe ist x auf der 2. und 3. Lage, also innen ·
Ein Schalter je Nachweis statt einer je Lage, angezeigt wird die ungünstigere
der beiden x-Lagen · Gesammelt wird in der Darstellung, nicht in der Prüfung --
die Suche zählt weiterhin jede Lage, sonst wäre die Ebene zurück, an der sie
einmal stehenblieb ·

Schmale Fenster: unter 900 px steht eine Tafel allein, ein Umschalter am
unteren Rand wechselt · Fingerziele ab 34 px, Erklärungen auf Tipp statt nur
auf Hover, `100dvh` gegen die Adressleiste · `.feld` und `.zweispaltig` auf
`minmax(0, 1fr)`, sonst nimmt ein Gitter die Mindestbreite seines Inhalts ·

Ausgeschaltete Nachweise rechnen still mit und melden sich unter der
Zusammenfassung, wenn sie nicht aufgehen · Die Plattenvorlage steht im Kern
(`QuerschnittEintrag.neu()`), nicht mehr in der Oberfläche · Doppelte
Lastfallnamen werden gemeldet, statt sich still zu überschreiben ·

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
