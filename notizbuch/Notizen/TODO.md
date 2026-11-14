# Was noch offen ist

Reihenfolge ungefähr nach Dringlichkeit. Erledigtes wandert raus — was dabei
gelernt wurde, steht in [[Entwicklung]].

---

## Offen


- [ ] **Decken: die App fertig bauen.** Rechenkern, Zeichenfenster,
      Lasten und Lastfälle sowie die Ergebnisbilder samt Lagerkräften stehen
      (siehe [[Entwicklung]], 2026-11-13 und 2026-11-14). Es fehlt der
      Bericht mit Herleitung.
- [ ] Decken: das Moment eines eingespannten Linienlagers steht im Bild
      der Lager nur als Betrag. Sein Vorzeichen um die Achse des Lagers
      hängt an der Richtung, in der es gezeichnet ist, und sagt darum
      niemandem etwas. Prüfen, ob es mit dem Vorzeichen der Platte
      dastehen soll -- negativ, wo es oben zieht.
- [ ] Decken: die Knoten der Lasten anderer Lastfälle bleiben in der
      Zeichnung als Punkte stehen, ohne ihre Last. Prüfen, ob sie mit ihr
      verschwinden sollen.
- [ ] Decken: eine schräge Richtung heisst nach ihrem Winkel, ihre
      Streifen «71.57° 1 … 71.57° 8», und der Bericht nennt den Winkel
      daneben noch einmal. Mit den Ergebnisbildern besser benennen --
      der Benutzer spricht von m_η.
- [ ] Decken: «Knoten einfügen» auf einer Kante, die zwei Platten
      teilen, setzt den Knoten nur in die gewählte Platte; die andere
      behält ihre Kante ohne ihn. Prüfen, ob beide ihn bekommen sollen.
- [ ] Zeichenfenster: während eines Befehls heissen P und S «parallel»
      und «senkrecht», nicht Platte und Stütze. Erst Esc, dann die Taste.
- [ ] Decken, nach Vorgabe (`opencivil/decke/`): die automatische
      Aufteilung, wo Folie 31 nichts sagt (die Spannweite eines Kragarms
      zählt doppelt, gleich lange Spannweiten innerhalb 1 % je zur Hälfte,
      entschieden wird im Schwerpunkt jeder Zelle); die Grösse des
      Stützenbereichs, wenn sie fehlt (ein Quadrat, so breit wie die Stütze
      oder der breiteste Unterzug über ihr -- Folie 39 lässt sie offen);
      Streifen in zwei Richtungen, die nicht rechtwinklig aufeinander stehen;
      die Linienlast als Band von 1 mm, die Einzellast über 1 × 1 m verteilt.
      Die Norm sagt zu keinem etwas (geprüft am 2026-11-14): nach der
      statischen Methode gilt jede Aufteilung, die im Gleichgewicht ist
      (SIA 262:2025, 4.1.4.2.2), wenn das Verformungsvermögen gesichert ist
      (4.1.4.2.4); quer braucht es trotzdem mindestens 20 % der
      Hauptbewehrung (5.5.3.2). Die Einzellast selbst steht nach SIA 261:2020,
      Tabelle 8 auf 50 × 50 mm. Bei schiefen Richtungen ist die
      Fliessbedingung (34) nur eine grobe Näherung (4.3.2.5, 4.3.2.6): bei
      45° ist m_xy = m/2. Vom Benutzer bestätigen lassen; Vorschlag: bei
      schiefen Richtungen ein Hinweis im Bericht.
- [ ] **Decken: die Kombination GZG.** Jede neue Decke bekommt GZT und GZG,
      beide nach der Streifenmethode. Die ist eine Methode der
      Plastizitätstheorie und gilt für die Tragsicherheit (SIA 262:2025,
      4.1.4.2.1); Schnittgrössen im Gebrauch rechnet man in der Regel
      elastisch, mit Mittelwerten (4.4.1.2). Vorschlag: bei der Decke keine
      GZG vorgeben, oder ihr Ergebnis als Gleichgewichtslösung kennzeichnen,
      nicht als Gebrauchsnachweis. Entscheid des Benutzers.
- [ ] **Günstige ständige Last in den Vorgaben.** Die Vorgabe-Kombination
      GZT nimmt Eigengewicht und Auflast mit 1.35 und die Nutzlast mit 1.5,
      im Balkensystem wie in der Decke. SIA 260:2013, Tabelle 1 kennt für
      eine günstig wirkende ständige Last 0.80; massgebend ist sie etwa beim
      Kragarm mit Nachbarfeld, beim Abheben eines Lagers oder beim Gleiten.
      Vorschlag: eine zweite Vorgabe-Kombination mit 0.80 auf den ständigen
      Lasten, oder ein Hinweis in der Herleitung. Entscheid des Benutzers.
- [ ] Decken: B-B des Kolloquiums 4 weicht von der Musterlösung ab
      (−60.1 statt −58.5 kNm/m, Stützen 115.0/276.4 statt 115.5/275.1 kN),
      weil die App die Last aus C-C dort ablegt, wo sie aufliegt, statt mit
      dem Faktor 8.0 über die ganze Länge. Dem Benutzer so vorlegen.
- [ ] **«Stahl II» ist keine Sorte von SIA 262:2025.** Geprüft am
      2026-11-14: die neun Betonsorten stimmen mit Tabelle 3, B500A, B500B,
      B500C und B700B mit den Tabellen 5 und 9. «Stahl II» (f_yk = 345 N/mm²,
      Dehnungen wie B500B) steht in keiner Tabelle der Norm, wird aber als
      Normsorte «nach SIA 262:2025» angeboten. Vorschlag: aus den Normsorten
      nehmen; wer ihn braucht, legt ihn als eigenes Material an. Oder seine
      Quelle nennen, etwa eine ältere Norm. Entscheid des Benutzers.
- [ ] **Tabelle 8 rundet, das Werkzeug rechnet genau.** f_cd und τ_cd kommen
      aus den Gleichungen (2) und (3); Tabelle 8 nennt gerundete Werte, bis
      1.6 % daneben (C16/20: 10.67 statt 10.5 N/mm²). Vorschlag: bei der
      Formel bleiben, die Tabelle verweist selbst auf sie. Entscheid des
      Benutzers.
- [ ] **Vorgabe der Überdeckung.** c_nom = 30 mm liegt unter dem Grösstkorn
      D_max = 32 mm, und SIA 262:2025, 5.2.2.2 will bei stark beanspruchten
      Bauteilen mehr; Tabelle 18 verlangt schon für XC2 und XC3 35 mm.
      Vorschlag: Vorgabe 35 mm, oder ein Hinweis im Bericht, wenn c_nom
      kleiner ist als D_max oder der Stab. Entscheid des Benutzers.
- [ ] **Konstruktive Regeln der Bewehrungssuche.** Die Suche kennt nicht:
      Stäbe über ⌀30 nur ausnahmsweise (SIA 262:2025, 5.2.1); den lichten
      Abstand von mindestens D_max, dem Nachbarstab und 20 mm (5.2.3.2); die
      grösste Teilung 1.2·h und 300 mm (5.5.3.1); die Querbewehrung von
      mindestens 20 % der Hauptbewehrung (5.5.3.2); die Mindestbügel nach
      (116) (5.5.2.2, 5.5.3.4). Beispiel: h = 200 mm mit Teilung 250 mm --
      erlaubt wären 240 mm. Vorschlag: (116), 1.2·h und 300 mm als
      Bedingung, 5.2.1 und die 20 % als Meldung. Entscheid des Benutzers.
- [ ] **Dichten aus SIA 261.** 2400 und 2500 kg/m³ für Beton und Stahlbeton,
      7850 kg/m³ für Stahl stehen so in SIA 261:2020, Anhang A, Tabelle 28
      (mit g = 10 m/s²); SIA 262 nennt keine. Ob der Verweis eingetragen wird,
      entscheidet der Benutzer -- bis dahin «nach Vorgabe».
- [ ] **Kriechzahl bei hoher Spannung.** Über 0.4·f_cm kriecht der Beton
      stärker, und die Norm erhöht φ (SIA 262:2025, 3.1.2.6.3, (14)). φ ist
      eine Eingabe; das Werkzeug prüft das nicht. Zur Kenntnis.
- [ ] Verformung und «Plattendicke optimieren»: **entschieden, noch nicht
      umsetzen** (Benutzer, 2026-10-16). Bei der Dickensuche wird der
      Verformungsnachweis ignoriert, denn w hängt von der Plattendicke ab: es
      gehört zur eingegebenen Dicke und wächst bei gleicher Last mit 1/h³.
      Kein Umrechnen mit (h₀/h)³. Erst umsetzen, wenn der Benutzer es sagt;
      bis dahin hält die Suche w fest wie eine Einwirkung.
- [ ] **Grenzwert der Durchbiegung wählbar?** L/350 steht in SIA 260:2013,
      Anhang A, Tabelle 3: häufige Last, Funktionstüchtigkeit und Komfort.
      Dieselbe Tabelle nennt L/500 (seltene Last, spröde Einbauten) und
      L/300 (quasi-ständige Last, Aussehen); welches Kriterium gilt, legt das
      Projekt fest (SIA 262:2025, 4.4.3.2.1). Die Tabelle meint je Zeile nur
      einen Teil der Durchbiegung -- was nach dem Einbau dazukommt, was die
      veränderlichen Lasten bewirken, oder alles abzüglich Überhöhung; das
      Werkzeug hält die ganze samt Kriechen gegen L/350, strenger als jede
      Zeile ausser L/500. Vorschlag: ein Schalter 500 / 350 / 300, Vorgabe
      350. Entscheid des Benutzers.
- [ ] **Grundbruch: ein Widerstandsbeiwert γ_R?** SIA 267:2013 teilt
      Grundbruch- und Gleitwiderstand durch γ_R, in der Regel 1.0 bis 1.2,
      1.0 nur bei bewährten, zuverlässigen Verfahren (8.5.2.1, (29), (30)).
      Das Werkzeug setzt 1.0, und der Bericht sagt es; das Buch nennt die
      Tragfähigkeitsformel selbst eine Näherung (Kap. 9.2.9), sein N_γ liegt
      eher hoch (9.2.6). Mit γ_R = 1.2 sinken N_Rd und T_Rd um 17 %.
      Empfehlung: ein Feld γ_R, Vorgabe 1.0. Entscheid des Benutzers.
- [ ] **Grundbruch: die Raumlast unter Wasser.** Das Buch bildet γ' aus
      der gesättigten Raumlast, γ' = γ_g − γ_w (Kap. 1.4); das Werkzeug hat
      nur ein γ und nimmt es auch unter dem Wasser. Mit γ = 21 statt
      γ_g = 22 kN/m³ wird γ' 11 statt 12, gut 8 % kleiner -- sicher, denn
      γ' hält den Gleitkörper nieder; die Hilfe sagt es. Empfehlung: ein
      eigenes Feld γ_g für den Boden unter dem Wasser, Vorgabe 22 kN/m³.
      Entscheid des Benutzers.
- [ ] **Grundbruch: φ_k über 45°?** Das Feld nimmt bis unter 90°; die
      Tabellen des Buches enden bei 45°, eine Grenze nennt es nicht.
      Empfehlung: ab 45° ein Hinweis «ausserhalb der Tabellen des Buches»,
      keine Sperre. Entscheid des Benutzers.
- [ ] Grundbruch, ohne Stelle in der Quelle: Liegt das Grundwasser im
      Gleitkörper (T < H), verlangt das Buch eine Stabilitätsberechnung
      (Kap. 9.2.8, 9.2.10); gerechnet wird mit γ' wie in Lage 2. Bei
      ruhendem Wasser liegt das sicher, eine Strömung fehlt (SIA 267:2013,
      8.4.4.4 verlangt sie). Eine Klammer der Lastneigung unter null gilt
      null; das wird erst ab δ_R > 55° wirksam, wo das Gleiten längst nicht
      mehr erfüllt ist. Bestätigt sind dagegen: b_γ mit tan φ (Tabelle
      9.2.18 lässt sich nur so nachrechnen) und die Partialfaktoren statt
      F_stat (SIA 267:2013, 5.3.2.1, 5.3.2.2, Tabelle 1).
- [ ] **Grundbruch und Gleiten, nicht gebaut** -- SIA 267:2013 verlangt
      es, wo massgebend: die Ausmitte der Last mit der wirksamen Fläche
      A' = a'·b' (8.4.4.4, Figur 4; im Buch Kap. 9.2.11), bis dahin sagt
      die Hilfe, b und L als wirksame Masse einzugeben; das Kippen
      (8.5.3.6, (38)–(40)) und im Gebrauch die Ausmitte bis zur einfachen
      Kernweite (8.5.4.7); der Erdwiderstand vor dem Fundament (8.4.3,
      8.5.2.3, γ_M = 1.4) -- ihn wegzulassen ist sicher; der Geländebruch
      (8.5.3.3, Kap. 14 der Norm); benachbarte Fundamente (8.4.4.3).
      Der Gleitkörper im Bild gilt für waagrechte Sohle und waagrechtes
      Gelände, wie die Formeln für L_Gl und H_Gl.
- [ ] **Setzung: die Startwerte einer neuen Berechnung.** Keine steht in
      einer Quelle. s_zul = 20 mm: die zulässige Setzung ist je Bauwerk
      festzulegen (SIA 267:2013, 8.5.4.1; Kap. 8.12), das Beispiel in
      Kap. 8.8 nimmt 2 cm. Δz_max = 0.5 m: das Buch schweigt, sein
      Beispiel teilt in 1 m. M'_E = 60 MN/m² bei M_E = 20: das Buch nimmt
      grob M'_E ≈ 8 bis 10 · M_E an (Kap. 5.3) -- 3 · M_E ist weicher als
      jede Angabe. Wirkt nur, solange q_W > 0. Empfehlung: M'_E = 160
      (8 · M_E). Bestätigt: MN/m² statt kN/m² (nur die Anzeige, Tabelle
      8.4 trifft) und «starr» als Vorgabe (das Beispiel in Kap. 8.3 rechnet
      so). Entscheid des Benutzers.
- [ ] Setzung, nicht gebaut: Setzungsdifferenzen und Verkippung
      (Kap. 8.11 bis 8.13; SIA 267:2013, 8.5.1.2, 8.5.4.4), der zeitliche
      Verlauf (Konsolidation; 8.5.4.3), die Einflusstiefe als Abbruch
      (Kap. 8.4) -- gerechnet wird bis zur untersten Schicht, und unter der
      Tabelle steht, wie viel J dort noch ist. Liegen darunter weichere
      Schichten, mahnt das Buch zur Vorsicht.
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

## Umbau: Befunde der Strukturdurchsicht vom 2026-11-09

Vier Durchsichten über das ganze Repo (Rechenkern; Projekt, Dienst und
Fachmodule; Oberfläche; Durchstanzen), jeder Punkt am Code nachgeprüft.
Urteil: gutheissen mit Änderungen. Im Kern ist nichts verheddert, und die
Schichten sind sauber. Vor der nächsten Bauteilart und vor dem nächsten
Schritt beim Durchstanzen braucht es aber einen Umbau: drei Muster stehen
schon dreifach da. 1 und 2 sind am 2026-11-09 erledigt, 3 bis 12 am
2026-11-10 (siehe [[Entwicklung]]). Offen ist nur, was darunter steht.

**Im übrigen Repo, neu gefunden:**

- [ ] **cad_fenster.js hat 1138 Zeilen** -- die einzige Datei über
      tausend, schon vor der Durchsicht (bei Punkt 11 übersehen). Nähte an
      den Abschnitten: Ändern und Rückgängig, Befehle, Zeichnen,
      schwebendes Fenster mit Knöpfen, Bedienen, Aufbau.

**Stand der früheren Befunde:** fast alle offen. Teilweise behoben: die
Grenze x/d kommt aus dem Katalog (nachweise.js), editor.js nennt keine
Normstelle mehr, Meldungen nennen das Feld, `print(ergebnis)` nutzt
`zusammenfassen`. Behoben: die d_v-Regel steht einmal
(`Kurvenbeiwerte.hoehen`). Gewachsen: die Halbierungen (dazu dicke.py und
qa_gebrauch.py), die Materiallisten im JS (dazu durchstanzen.js), die
Grundlage der Zeichenfenster (siehe 3) und das Kern-Wissen im JS (dazu
durchstanzen.js).

## Umbau: Befunde der Strukturdurchsicht vom 2026-10-25

Vier Durchsichten über das ganze Repo, jeder Punkt am Code nachgeprüft.
Die Punkte im Rechenkern sind am 2026-10-25 behoben, siehe [[Entwicklung]]
-- bis auf zwei, die auch die Oberfläche betreffen: die Stablinie vor dem
Bauen und die Einheiten am Feld. Offen sind sonst die Punkte der
Oberfläche. Was in den Abschnitten darunter schon steht, steht hier nicht
noch einmal: die Grundlage der Apps mit Zeichenfenster, die
`Fallauswertung`, die Dateien über 1000 Zeilen.

- [ ] **Sechs eigene Zwischenspeicher für Nebenanfragen** (`qa_zeichnung.js`,
      `bs_zeichnung.js`, `qa_diagramme.js`, `bs_diagramme.js`, `app.js`,
      `bericht.js`) mit drei Regeln für Fehler: ohne Antwort des Kerns
      bleibt die Querschnittsanalyse still ohne Geometrie, das
      Balkensystem zeigt den Fehler. Besser `nachgefragt(schluessel,
      abdruck, holen)` mit `{daten, alt, fehler}` -- gehört zur Grundlage
      der Apps mit Zeichenfenster unten.
- [ ] **Der Adapter des Zeichenfensters ist ein Sammelsurium:** 32 Glieder,
      14 davon braucht nur eine App. Das Fenster gibt den Namen des
      Werkzeugs weiter, und die App verzweigt danach erneut. Besser: das
      Verhalten an die Tabellen der Werkzeuge und Arten hängen, die das
      Fenster ohnehin durchläuft; ebenfalls Teil von `cadApp`.
- [ ] **Arten als Text oder Schalter statt als eigener Typ** (die Art des
      Stabquerschnitts, die Querkraft, «einachsig», die Bewehrung der
      Querschnittsanalyse und M–χ oder N–ε sind seit 2026-10-25 behoben):
      Die Beschreibung einer Stablinie fragen vor dem Bauen noch die Prüfung
      der Zeichnung, `geometrie.linienflaeche` und die Liste unter der
      Zeichnung (`api.geometrie`) je nach Art ab -- dort ist der Stahl noch
      eine Kennung, kein Baustoff.
- [ ] **Die Oberfläche wiederholt Kern-Wissen, neu dazugekommen** (zum
      Punkt «Keine Rechnung und keine Norm in der Oberfläche» unten):
      `bs_zeichnung.js` kopiert die Lastrichtungen aus dem Kern; Einheiten
      und Stellen der Diagramme stehen in `bs_diagramme.js` neben
      `balkendaten.py`; `plattenkapitel.js` wiederholt «x/d ≤ 0.35», «L/350»
      und eine Normstelle.
- [ ] **Eine fehlende Bauteilart fällt in der Oberfläche still weg**
      (`bericht.js`). Im Kern führt der Aufbau seit 2026-10-25 nur noch
      die Bauteile; Objekte und Nachweise je Art und Feld sind Sichten
      darauf, und Zuordnung und Angaben laufen über die Bauteile.
- [ ] **Einheiten nicht an jedem Feld.** Der Katalog bringt seit 2026-10-25
      die Feldangaben jeder Klasse von Einträgen, aus einem Durchgang über
      den Baum der Beschreibung. Viele Felder tragen ihre Einheit aber
      nicht -- `KombinationEintrag.M_Ed` und Co. --, und die Oberfläche
      schreibt sie darum selbst («M_Ed [kNm]» in `plattenkapitel.js`).
      Besser: die Einheit ans Feld (`bereich(einheit=…)`), dann liest die
      Maske sie aus dem Katalog -- zusammen mit «Einheiten der Platte beim
      Bauen ein zweites Mal» unten.
- [ ] **Kleineres:** sieben Helfer bauen SVG-Pfade, und die Diagramme
      kennen zwei Regime für Farben.

## Umbau: liegen geblieben bei der Durchsicht vom 2026-10-18

Vier Durchsichten (Wiederverwendung, Vereinfachung, Effizienz, Wurzel) über
die Phasen 4 und 5; was sich ohne Umbau ausserhalb dieser Arbeit beheben
liess, ist behoben (siehe [[Entwicklung]]). Liegen blieb:

- [ ] **Einheiten der Platte beim Bauen ein zweites Mal:** `Groesse(eintrag.h,
      MM)` und Co. für h, b, Überdeckungen, D_max, Einlagenhöhe, w, L und die
      Knicklängen, obwohl die Felder ihre Einheit tragen. Besser
      `eintrag.si(…)` wie die Analyse. Die Masken von Verformung und Knicken
      schreiben ihre Einheiten und `min: 0` noch selbst; der Katalog hätte
      sie (`feldangaben(VerformungsfallEintrag)`, `KnickEintrag`).
- [ ] **Der Rand des Gleichgewichts wird viermal von Hand halbiert**
      (`linie._grenze`, N_Rd beim Knicken, `gebrauchsebene._rand`,
      `Faserloeser._rand`), mit vier Abbruchregeln; `core/suche.py` kennt
      diese Suchform nicht.
- [ ] **Teilung oder Stabzahl** steht als `art`/`abstand`/`anzahl` und als
      `art_y`/`abstand_y`/`anzahl_y` da; die Rechenobjekte wandeln es zurück
      in «eine Zahl ist None». Besser ein gemeinsamer Eintrag für beide.
- [ ] **Die Grössen einer Linie** (Zeichen, Einheit, Stellen) stehen in den
      Diagrammdaten (`_LINIENGROESSEN`) und in der Herleitung je für sich;
      das JS zerlegt die Zeichen mit einem regulären Ausdruck (`mitIndex`).
- [ ] **Material in der Oberfläche:** «Name oder Sorte» steht 14-mal im JS,
      im Kern als `anzeigename`; `materialwahl` ist privat in
      `qa_zeichnung.js`, die Platte baut ihre Auswahl selbst; «Beton» und
      «Betonstahl» stehen in drei JS-Tabellen neben `Baustoffart.beschriftung`.
- [ ] **Kleineres:** Welche Seite x-Bewehrung hat, fragen Kennzahlen,
      Verformung und Querkraft je für sich · `Aufbau.kennzahlen` lesen nur
      noch Tests · `protokoll_mit_buegeln` nimmt `seite` als Text an und
      bekommt eine Zugseite · zwei kleine Einsparungen im Löser (−4 % der
      Faserdurchläufe, Zeit im Rauschen) sind nicht gemacht.

## Umbau: Befunde der Durchsicht vom 2026-10-16

Sechs Durchsichten über die Arbeit vom 15. und 16. Oktober (42 Commits);
jeder Punkt ist am Code nachgeprüft. Umgesetzt ist der ganze Plan: die vier
Fehler mit Folge, Phase 2, Prüfen und Wahlfelder, Phase 3, Platte und
Querschnitt als ein Nachweis (beide 2026-10-17), Phase 4, Löser und
Kennzahlen, und Phase 5, die Oberfläche (beide 2026-10-18, siehe
[[Entwicklung]]). Hier steht, was dabei liegen blieb oder neu auffiel.

- [ ] **Die Karten des Berichts je Bauteilart** stehen noch neben den Zeilen
      von `apps.js`: `UEBERSICHTEN` und `DIAGRAMME` in `bericht.js`. In die
      Zeilen ziehen sie erst, wenn `plattenkarten` und `spannungskarten` aus
      `bericht.js` ausziehen -- sonst importierten sich `apps.js` und
      `bericht.js` gegenseitig.
- [ ] **Kern-Wissen im JS, neu dazugekommen:**
      - Das Querschnittsbild einer Analyse (Punkt aus N und M oder aus
        Randdehnungen) beschriftet seine Zahlen selbst mit kN, kNm, ‰, 1/m
        und mm -- wie seine Zeichendaten sie liefern (`_bild_dict`). Die
        Linien bringen ihre Grössen seit 2026-10-18 mit.
      - Die Situationszeichnung des Grundbruchs (`gb_zeichnung.js`)
        beschriftet b, t, t₁, α, β und q_Ed selbst mit m, ° und kPa; ihre
        Geometrie rechnet ohnehin in m und Grad. Ganz aus dem JS gehen diese
        Einheiten erst mit Situationsdaten des Kerns in SI.

      Besser: Der Katalog liefert je Feld Einheit, Bereich und Wahl
      (`katalog.felder`, seit 2026-10-18 beim Grundbruch und bei den
      Neigungen); die übrigen Masken folgen. Das Zeichen bleibt in der Maske:
      im Kern steht es an der Rechnung, nicht am Feld.
- [ ] **Kleineres:**
      - Aus dem früheren Punkt C2 ist «je Rechenart eine Tabellenzeile»
        nicht gemacht.
      - Grundbruch: Das Nachweisgerüst steht zweimal, und im Zweig «zu
        schräg» steht im Befund N_Rd = 0 aus den Vorgaben der Datenklasse
        (das Urteil zeigt dort seit 2026-10-25 Striche und den Hinweis).
      - Die Summe von Grundbewehrung und Zulage hat zwei Formelseiten:
        [[Bewehrung der Lage]] (`protokoll_lage`, auch die Verformung) und
        [[Bewehrungsquerschnitt der zusammengefassten Lage]] (Handrechnung).
        Zusammenlegen hiesse, eine Seite umzubenennen.
      - Die leere Lage bekommt still den ersten Stahl.
      - Die Pakete laden über vier Schichten, obwohl Pyodide es selbst kann
        (`loadPackagesFromImports`). Das ändert eine mitgelieferte Datei.
      - Eine Meldung nennt ihren Ort mit den Feldern der Datei («Platte
        'Decke', lagen 2, grund: …»), nicht mit den Wörtern der Maske
        («2. Lage, Grundbewehrung»). Gehen könnte das mit einer Bezeichnung
        je Feld, wie sie der Katalog in Phase 5 ohnehin bekommt.

## Umbau: Befunde der Strukturdurchsicht (2026-10-12)

Neun Durchsichten haben je einen Bereich ganz gelesen; jeder Punkt ist am
Code nachgeprüft. Reihenfolge nach Empfehlung. Ziel jedes Punkts ist, dass
etwas wegfällt, nicht dass es umzieht. Behoben sind der dringendste
Befund, die gemischten Stahlsorten, dazu «Ergebnisse in den Rechenlauf»,
«Ein Steckbrief je Bauteilart», «Eingaben an einer Stelle prüfen» und
«Ein Modell der Werkstoffgesetze» (siehe [[Entwicklung]]).

- [ ] **Eine Grundlage für die Nebenanfragen.** Die Zeichenfenster haben
      seit 2026-11-10 eine (`cadApp` in `cad_app.js`: Lesen, Schreiben,
      Fenster, Liste, Markierung, Vergessen). Offen ist der zweite Teil:
      selbstgebaute Zwischenspeicher für Nebenanfragen mit eigenen
      Fehlerregeln (`bs_diagramme.js`, `qa_diagramme.js`, `app.js`,
      `bericht.js`). Die beiden Diagramme hängen seit 2026-11-10 an der
      Fassung des Projekts und an `ansichtVon`, ihre Anfrage mit Uhr und
      Verzug steht aber noch zweimal da; die Geometrie der Analyse und die
      Übersicht des Systems fragen je auf ihre Art. Besser:
      `nachgefragt(schluessel, holen)` merkt sich Antworten bis zur
      nächsten Fassung.
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
      Meldung am System, nicht mehr als Fehler des ganzen Projekts. Stäbe
      und Lasten werden in vier Durchgängen aufgelöst, mit einem Schalter
      `melden`. Besser: LF1/LK1 als Identität, Lasten einmal je Fall
      auflösen. («Fest» als `math.inf` ist seit 2026-10-25 ein `Halt`.)
- [ ] **Varianten im Kern -- deine Entscheidung.** `prioritaet`,
      `bedingung`, `anwendbar`, `verworfene_varianten` benutzt ausserhalb des
      Kerns niemand. Wer zwei Berechnungen für denselben Wert anmeldet
      (kopierter Namensraum), bekommt keinen Fehler, sondern still eine
      Variante; die zuerst angemeldete gewinnt. Empfehlung: ein Erzeuger je
      Wert, `registriere` wirft beim zweiten. War eine Gründungsentscheidung.
- [ ] **Dateien über 1000 Zeilen**, je entlang einer Naht, die schon da ist:
      `cad_fenster.js` (Bedienung, Rückgängig, Punkteingabe auslagern; die
      Befehle stehen in vier Listen, Knöpfe täuschen Tastendrücke vor),
      `stil.css` (ein Blatt je App). Stand 2026-10-25: stil.css 2348 Zeilen,
      cad_fenster.js 1138. `querkraft.py` und `querschnitt/platte.py` sind
      geteilt (2026-10-25); die Regel für d_v steht in Kurve und Nachweis
      ohne Bügel noch je einmal.
      `nachweise.js`, `spannungsanalyse.py` und `aufbau.py` sind geteilt,
      `querschnittsloeser.py` liegt bei 914.
- [ ] **Kleineres:** `print(ergebnis)` hat eine
      dritte, abweichende Zusammenfassung (`konsole.py`) · die Herleitung am
      Bildschirm lässt unbekannte Blockarten still weg (`bericht.js`) ·
      `BEREICHE.get(…, "")` legt eine neue Art
      still unter «Weitere» · der Schalter `schnell` bündelt vier Verhalten
      für zwei Nutzer.

## Offene Normfragen — deine Fragen, unbeantwortet

Diese Punkte sind **nicht** entschieden. Eingebaut ist je eine Annahme; wo die
Prüfung vom 2026-11-14 den Bereich schon erreicht hat, steht dabei, was die
Norm dazu sagt.

- [ ] **Pfähle, nach Vorgabe eingebaut** (`opencivil/pfahl/`). Beim
      örtlichen Abscheren gelten η_a und γ_M,a trotzdem, obwohl das Buch
      danach keine weitere Sicherheit vorsieht (Kap. 12.5); X wird dabei mit
      φ'_k abgelesen, nicht mit 2/3 davon. Ausserhalb der Bilder 12.4 und
      12.5 gilt der Wert am Rand. Der Fuss im undrainierten Ton rechnet ohne
      die Überlagerung, das Gewicht des Pfahls steht ebenso wenig in der
      Einwirkung. Auf Zug dieselbe Mantelreibung wie auf Druck. δ/φ'_k und α
      höchstens 1. Der Mörtel im Rohr eines Mikropfahls zählt nicht, obwohl
      SIA 267:2013, 9.5.2.4.8 ihn zuliesse -- nach SIA 262 endete der ganze
      Querschnitt sonst bei −ε_c1d. Das Tragglied rechnet als Betonstahl nach
      SIA 262 mit γ_s; SIA 263:2013 liegt im Ordner der Normen und ist nur
      für die Querkraft eingearbeitet. Vorschlag: so lassen, jede Annahme steht in der
      Herleitung. Entscheid des Benutzers.
- [ ] **Pfähle, Steifigkeit nach Vorgabe eingebaut**
      (`opencivil/pfahl/steifigkeit.py`). Die Bettung quer wächst vom
      Terrain linear bis t_red, vorgegeben 2 m -- 9.5.4.5 verlangt nur, sie
      nahe der Oberfläche abzumindern. Der Mikropfahl rechnet mit Cassans
      Federn für Bohrpfähle. Der Querschnitt ungerissen und ohne Bewehrung,
      beim Bohrpfahl mit E_cm, beim Mikropfahl nur das Tragglied. γ_E = 1.5,
      der kleinste Wert nach 5.3.2.5. Längs und quer getrennt, ohne Theorie
      zweiter Ordnung (9.5.3.4.3 verlangt dafür eine eigene Untersuchung).
      Keine Feder am Mantel, wo q_s,k null eingegeben ist; eine Feder am
      Fuss, wo R_a,k aus einem Versuch kommt. Vorgabe für E_s,k: 30 MN/m²,
      das Beispiel des Buches. Vorschlag: so lassen, jede Annahme steht in
      der Herleitung. Entscheid des Benutzers.
- [ ] **Pfähle, Widerstand quer nach Vorgabe eingebaut**
      (`opencivil/pfahl/quer.py`, `erdwiderstand.py`). Die Norm verlangt
      R_tr,k aus Erdwiderstand und innerem Widerstand (9.4.4.2.2), sagt aber
      nicht wie. Eingebaut: Rankine ohne Wandreibung (Kap. 9.3.5, 9.3.6),
      vorne passiv und hinten aktiv, beide auf der Breite 3·D (das Buch nennt
      die dreifache Breite nur für vorne, Kap. 10.8). Die Brüche als Familie
      von Mechanismen: frei drehbar Drehung, ein Gelenk oder Verschiebung,
      eingespannt Gelenk am Kopf mit Drehung, zwei Gelenke oder
      Verschiebung. Der Biegewiderstand mit f_ck und f_yk mal η_i, der
      kleinere an Kopf und Fuss. γ_M,a = 1.4, nach (49) in der Regel der
      kleinste Wert. Die Bettungskraft gegen η_a,tr · p_E,k / γ_M,a, mit
      denselben Beiwerten wie R_tr (9.5.4.5 nennt keine). Nur ein Moment am
      Kopf, ohne Querkraft, gibt keinen Nachweis R_tr -- geprüft wird dann nur die
      Bettungskraft. Vorschlag: so lassen, jede Annahme steht in der
      Herleitung. Entscheid des Benutzers.
- [ ] **Pfähle, innerer Widerstand quer nach Vorgabe eingebaut**
      (`opencivil/pfahl/innen_quer.py`). Bohrpfahl: d reicht bis zum
      Schwerpunkt der halben Bewehrung, als ob die Stäbe gleichmässig auf dem
      Kreis lägen; b_w ist die Sehne auf der Höhe des Druckgurts -- für den
      Kreis nennt SIA 262:2025 keine Breite; α_min = 30° auch unter Druck, wo
      4.3.3.3.3 bei bedeutendem Druck 25° zuliesse; die Wendel ist aus dem
      Stahl der Längsbewehrung; die Längszugkraft F_tVd (4.3.3.4.11) wirkt in
      der Achse statt je zur Hälfte an den Gurten, auf der sicheren Seite;
      die Querkraft zählt auch nahe dem Kopf, wo 4.3.3.4.1 sie im Abstand
      z · cot α nähme. Mikropfahl: A_v = 2·A/π für Rohr und Vollstab --
      SIA 263:2013, 5.1.4.1 verweist für runde Querschnitte auf
      SN EN 1993-1-1, die nicht vorliegt; f_yd nach SIA 262 (γ_s = 1.15) statt
      f_y/γ_M1 (1.05, SIA 263:2013, 4.1.3); dass die Querkraft über der
      Hälfte ihres Widerstands den Biegewiderstand mindert (5.1.5.1), steht
      nur als Hinweis. Vorschlag: so lassen, jede Annahme steht in der
      Herleitung. Entscheid des Benutzers.
- [ ] **Pfähle quer: die dreifache Breite.** Das Buch nennt sie eine grobe
      Näherung (Kap. 10.8) und daneben den Weg nach Weissenbach: ein
      räumlicher Gleitkeil, die resultierende Kraft bis in die Tiefe t aus
      Tabelle 10.21 (mit δ = 27.5°), und eine Abminderung, wo die Fläche
      schmaler ist als etwa 0.3 · t. Die eingebaute Näherung -- Rankine ohne
      Wandreibung, hinten aktiv abgezogen -- bleibt darunter: ⌀ 900 mm in
      Kies mit φ' = 35°, bis 3 m Tiefe 60 %, bis 6 m 43 % der Kraft nach
      Weissenbach. Nur sehr nahe am Terrain und bei kleinem φ' kommt sie an
      die Tabelle heran. Die Abminderung gehört zum Weg nach Weissenbach und
      ist nicht eingebaut. Vorschlag: so lassen. Entscheid des Benutzers.
- [ ] **Pfähle quer: undrainiert 12 · s_u · D.** Aus Rankine auf 3·D folgt
      in der Tiefe 12 · s_u · D je Meter. In der Literatur (Broms; das Buch
      nennt ihn nur im Literaturverzeichnis) ist 9 · s_u · D üblich, in den
      obersten 1.5·D null. Das Werkzeug gibt im Ton also bis ein Drittel
      mehr Widerstand. Vorschlag: so lassen, solange keine Quelle vorliegt,
      die man nachschlagen kann. Entscheid des Benutzers.
- [ ] **Pfähle, nicht nachgewiesen:** die konstruktiven Regeln des
      Bohrpfahls (SIA 267:2013, 9.6.3.2.3 bis 9.6.3.2.6: Mindestbewehrung,
      Zahl und Abstand der Stäbe, Überdeckung), der Kopf auf 1.2·R_i,k
      (9.6.1.2.3) und das Knicken (9.5.1.1, nur ein Hinweis). Negative
      Mantelreibung und Gruppenwirkung (9.4.3.1, 9.4.4.1.7) fehlen ganz.

- [ ] **Durchstanzen, Begrenzung auf 1.5·d_v (Figur 23a bis c).** Eingebaut:
      eine gerade Strecke des Nachweisschnitts zählt 1.5·d_v von jeder Ecke
      der gestützten Fläche und entlang einer Wand von ihrem Ende her; eine
      Strecke, die von einer Ecke zum freien Plattenrand läuft (Figur 22d),
      zählt ganz. Geprüft (2026-11-14): Ecken und Wände wie 4.3.6.2.3 und
      Figur 23a bis c. Zur Strecke bis zum freien Rand sagt die Norm nichts;
      vorsichtiger wäre, auch dort nur 1.5·d_v ab der Ecke zu zählen.
      Entscheid des Benutzers.
- [ ] **Durchstanzen, l_min in (61).** Das Werkzeug nimmt die kleinere der
      beiden eingegebenen Spannweiten, je die grössere der angrenzenden
      (4.3.6.4.4); gemeint ist in (61) die kleinste Spannweite. Selten
      massgebend, weil b_s = 1.5·0.22·l ≈ 0.33·l meist kleiner ist; in Stufe 3
      mit grossem r_s möglich, und die Herleitung sagt es, wo l_min greift.
      Vorschlag: ein eigenes Feld für die kleinste Spannweite, oder so lassen.
      Entscheid des Benutzers.
- [ ] **Durchstanzen, Rundstütze am Rand (Figur 25).** b_sr rechnet mit dem
      Durchmesser für beide Abmessungen der Stütze; die Figur zeigt nur
      Rechtecke, die Norm sagt nichts. Vorsichtiger wäre das einbeschriebene
      Quadrat, Seite D/√2. Entscheid des Benutzers.
- [ ] **Durchstanzen, «grosse Aussparungen» für k_e = 0.7 (4.3.6.2.5).**
      Eingebaut: eine Innenstütze bekommt 0.7, sobald eine Aussparung den
      Nachweisschnitt mindert (Figur 23d) -- wie gross sie ist, zählt nicht.
      Geprüft (2026-11-14): die Norm nennt keine Grösse; die Annahme ist
      strenger als nötig, nicht falsch.
- [ ] **Durchstanzen, Ovalstütze.** Eingebaut: ihre geraden Seiten zählen wie
      die einer Rechteckstütze 1.5·d_v von jedem Ende her. Der Name kommt aus
      der Software von Leviat. Die Norm kennt die Form nicht (Figur 22 zeigt
      Kreis und Rechteck); die Regel für gerade Abschnitte (Figur 23a) ist
      folgerichtig übertragen. Offen: ob du diese Form gemeint hast.
- [ ] **Durchstanzbewehrung: die Regeln von ancoPLUS.** Eingebaut nach dem
      Gutachten Muttoni / Fernández Ruiz 2007 (zu SIA 262:2003):
      Abstände 0.375·d / 0.60·d bis zum dritten Anker / danach 0.75·d,
      ⌀ je nach d (Tabelle 1), k_sys = 3.0 bei c_v ≤ d/10 und 2.0 bei
      c_v ≥ d/6 (dazwischen linear) für Innenstützen und Wandenden, 2.0 am
      Rand und an der Ecke, Obergrenze 3.5. Die Höhe h_A = h − c_nom − c_v
      auf …5 mm abgerundet stammt aus der Zulassung ETA-13/0196 und zwei
      Beispielen. Nach der Norm geprüft (2026-11-14): Leisten beim zweiten
      Anker höchstens 1.5·d_v auseinander (5.5.3.9), Anker aus B500B mit
      eigenem f_yd (4.3.6.5.4), −30 % auf (68) und (70) bei c_v > d_v/6
      (5.5.3.11). **Zu entscheiden:** Tabelle 21 (5.5.3.12) lässt bei
      d ≤ 180 mm und d > 340 mm engere Reihen zu, als das Produkt stellt
      (bei d = 404 mm 267 statt 300 mm). Heute steht nur ein Hinweis in der
      Herleitung. Empfehlung: auf Tabelle 21 begrenzen, ausser das Gutachten
      deckt die Abstände (4.3.6.5.6).
- [ ] **Durchstanzbewehrung an Aussparungen.** Eingebaut: eine Leiste hält
      zur Aussparung die Überdeckung c_nom, wie zum Plattenrand (nach Vorgabe,
      nicht nachgeschlagen), und im Schatten einer Aussparung nach Figur 23d
      liegt keine Leiste (gelesen: dort zählt der Schnitt nicht, also auch
      keine Bewehrung, die ihn quert). Geprüft (2026-11-14): 4.3.6 und 5.5.3
      sagen zu beidem nichts; die Leiste im Schatten folgt Figur 23d.
- [ ] **Stahlpilz: die Masse des Herstellers.** Geprüft (2026-11-14): die
      gestützte Fläche reicht bis an die äussersten Stege, ausserhalb gilt
      4.3.6.3 bis 4.3.6.5 (4.3.6.6.2), den Widerstand des Pilzes bestätigt der
      Hersteller (4.3.6.6.1), und d_v reicht bis zur Höhe der gestützten
      Fläche (Figur 21). Nach Vorgabe von AncoTech, die Norm sagt nichts:
      20 mm Beton unter und 50 mm über dem Pilz, 50 mm Überstand über die
      Stütze. Wo an den Stegen gemessen wird, zeigt Figur 21 nicht.
- [ ] **Durchstanzen: was das Werkzeug nicht abbildet** (zur Kenntnis):
      Einzellasten über 0.2·V_d näher als 3·d_v am Schnitt (4.3.6.2.3);
      einbetonierte Leitungen (Figur 23e); Verstärkungen und Schwächungen der
      Platte (4.3.6.2.7, Figur 24); Vorspannung (4.3.6.4.3); an Rand- und
      Eckstützen die untere Bewehrung als gezogene (4.3.6.4.7); die
      Verankerung der Biegebewehrung (5.5.3.7); ein Schnitt, der an einer
      Aussparung nahe der Stütze endet (4.3.6.2.2). Die Bedingung
      0.5 ≤ l_x/l_y ≤ 2 für Stufe 1 und 2 (4.3.6.4.2) prüft das Werkzeug nicht,
      die Sicherung gegen Totaleinsturz (4.3.6.7) steht nur als Hinweis.
- [ ] **Sprödes Versagen unter Zug fehlt.** Wo ein Querschnitt für die
      Tragsicherheit zählt, muss sein Widerstand die Rissbeanspruchung
      übertreffen, auch die auf Normalkraft (SIA 262:2025, 4.3.1.2, mit
      `f_ct,eff` nach 4.4.1.3; ebenso 4.1.4.2.4). Geführt wird nur das
      Rissmoment gegen `M_Rd`; die Rissnormalkraft hält das Werkzeug allein
      gegen die zulässige Stahlspannung der Zwängung, und die liegt bei
      normaler Anforderung bei `f_yk`, bei erhöhter für ⌀10 und ⌀12 ebenfalls
      über `f_yd`. Beispiel: Platte h = 250 mm, C30/37, normale Anforderung,
      `N_Riss` = 322 kN je Lage und Meter -- heute genügen 644 mm²/m, mit
      `A_s·f_yd ≥ N_Riss` brauchte es 741 mm²/m (+15 %). Vorschlag: die
      Bedingung als eigenen Nachweis führen. Entscheid des Benutzers.
- [ ] **Gebrauch mit Mittelwerten.** Gebrauchsnachweise rechnen mit den
      Mittelwerten der Baustoffe (SIA 262:2025, 4.4.1.2). Die Stahlspannung
      nimmt als Grenze des Betons `f_ck` statt `f_cm = f_ck + 8 N/mm²`
      (C30/37: 30 statt 38 N/mm²); im elastischen Bereich zählen nur `E_s`
      und `E_cm`, die schon Mittelwerte sind. Einen Mittelwert der
      Fliessgrenze kennt die Norm nicht, beim Stahl bleibt `f_yk`. Die Grenze
      gegen Fliessen ist `f_yd − 80 N/mm²`, so nennt sie Tabelle 17.
      Empfehlung: lassen -- `f_ck` liegt auf der sicheren Seite. Entscheid
      des Benutzers.
- [ ] **Welcher Durchmesser bestimmt `σ_s,adm` unter quasi-ständiger Last?**
      Eingebaut: der dickste Stab der Tragrichtung; er gibt die kleinste
      Grenze. Die Norm sagt dazu nichts, (102) kennt nur den Durchmesser
      eines Stabs (geprüft am 2026-11-14). Ebenso eigene Festlegung: der
      fiktive Durchmesser einer verschmierten Linie im gezeichneten
      Querschnitt bei 150 mm Teilung (`nachweis/stabgrenzen.py`). Beides
      bestätigen lassen.
- [ ] **60 % und 70 % liegen teils auf der unsicheren Seite.** Die Gebrauchs-
      fälle aus der Tragsicherheit nehmen 70 % (häufig) und 60 %
      (quasi-ständig) ihrer Last. Mit den Kombinationen nach SIA 260:2013,
      4.4.4.4, den Beiwerten ψ aus Anhang A, Tabelle 2, sowie γ_G = 1.35
      und γ_Q = 1.5 aus Tabelle 1 wären es (häufig / quasi-ständig):
      - Wohnen, g = 5 und q = 2 kN/m²: 62 % / 57 %
      - Wohnen, g = 8 und q = 2 kN/m²: 65 % / 62 %
      - Verkauf, g = 5 und q = 4 kN/m²: 61 % / 58 %
      - Lager, g = 5 und q = 4 kN/m²: 68 % / 64 %
      - nur Eigenlast: 74 % / 74 %

      Bei schwerer Eigenlast und bei Lagern sind 60 % zu wenig, bei
      überwiegender Eigenlast auch 70 %. Vorschlag: die Anteile im Bericht
      als Annahme ausweisen, oder die Kombination aus g, q und ψ anbieten.
      Entscheid des Benutzers.
- [ ] **Was macht der Eurocode?** Nicht verglichen. EC2 7.3.2 hat
      `A_s,min·σ_s = k_c·k·f_ct,eff·A_ct` — formal dieselbe Gestalt wie
      SIA 262:2025, Tabelle 17, aber mit `k_c` und `k` statt `k_t`, und mit
      einer anderen Begründung für die wirksame Zugzone. Ein Vergleich würde
      zeigen, ob die Zahlen zusammenpassen.
- [ ] **Kriechen beim Knicken – Entscheid des Benutzers.** Die Vorgabe φ = 0
      liegt auf der unsicheren Seite: SIA 262:2025, 4.3.7.2 verlangt beim
      Druckglied das Kriechen. Die Norm setzt es über die Krümmung an –
      (78) enthält es, sonst eine Vorkrümmung nach (80) –, das Werkzeug über
      den Modul der Parabel, `E_c/(1+φ)`. Wege: eine Vorgabe φ > 0 oder die
      Vorkrümmung.
- [ ] **Die Handrechnung als Rechenart im Löser.** Bei der Stahlspannung
      rechnet «Handrechnung» wie die Resistenzlinie aus Handrechnung
      (Knicken und Analysen bieten sie seit 2026-10-12 nicht mehr an):
      Spannungsblock, gedrückter Stahl weggelassen, je Seite eine Lage im
      Schwerpunkt, der Beton auch dort gezählt, wo der Stahl liegt. Nach
      Vorgabe: den Block lässt SIA 262:2025, 4.2.1.5 für den Bruch zu,
      Spannungen im Gebrauch rechnet 4.1.4.1.4 linear elastisch -- dort ist
      er ein Modell, keine Normregel. Das Druckplateau `f_y,druck` des Stahls
      im Löser deckt 4.2.2.2: Figur 16 gilt für Zug und Druck.
- [ ] **Rechnet die Tragsicherheit charakteristisch,** nehmen drei
      Nachweise charakteristische Werte, wo die Norm Bemessungswerte meint:
      - Sprödes Versagen hält `M_Rk` statt `M_Rd` gegen das Rissmoment; die
        Bedingung steht bei der Tragsicherheit (SIA 262:2025, 4.3.1.2). Es
        genügt damit rund 13 % weniger Bewehrung (`f_yk/f_yd` = 1.15).
      - Die Querkraft ohne Bügel nimmt ihr `m_Rk(N_Ed)` aus derselben Linie,
        ihr eigenes `τ_cd` und `f_yd` bleiben Bemessungswerte. Die Norm setzt
        in die Dehnung `m_Rd` (4.3.3.2.2, (39)); mit `m_Rk` wird sie um etwa
        1/1.15 zu klein und `v_Rd` im Beispiel um 3.4 % zu gross.
      - Die Schubwände der Querschnittsanalyse tragen mit `f_yk` und `f_ck`,
        heissen aber weiter `v_Rd`. Die Platte nimmt immer Bemessungswerte.

      Vorschlag: alle drei immer mit Bemessungswerten, gleich, wie der
      M-N-Nachweis rechnet. Entscheid des Benutzers.
- [ ] **Durchbiegung nach (103) oder (104)?** Gerechnet wird immer der
      gerissene Zustand, (104). Ungerissen gilt `w = w_c·(1 + φ)`, (103); die
      wahre Durchbiegung liegt dazwischen (SIA 262:2025, 4.4.3.2.4 bis
      4.4.3.2.6). Bei φ = 2, h/d = 1.2 und ohne Gegenbewehrung gibt (104) ab
      etwa ρ = 1.6 % weniger als (103). Und die Normalkraft fehlt: Druck
      verkleinert die Durchbiegung, Zug vergrössert sie (4.4.3.2.5).
      Vorschlag: das Grössere von (103) und (104), und ein Hinweis, wenn die
      Platte eine Normalkraft hat. Entscheid des Benutzers.
- [ ] **Fussnote 1 zu Tabelle 17 je Fall erkennen?** Liegt die
      quasi-ständige Beanspruchung über dem Rissniveau, reicht die Grenze aus
      (102) für die verlangte Rissbreite nicht, und wie viel mehr Stahl es
      braucht, sagt die Norm nicht. Seit 2026-11-14 steht dazu ein Hinweis bei
      jedem Nachweis mit verlangter Rissbreite. Vorschlag: je Fall
      vergleichen, ob das quasi-ständige Moment über `M_Riss` liegt, und den
      Hinweis nur dann geben. Ein Modell für die Rissbreite darüber wäre ein
      eigener Entscheid.
- [ ] **Hohe Zugfestigkeit, wo sie ungünstig wirkt.** Wo ein hohes `f_ct`
      oder der ungerissene Zustand den Nachbarn schadet, etwa an
      Diskontinuitäten, gilt `f_ct,eff = k_t·f_ctk0.95` = 1.3·`k_t·f_ctm`
      (SIA 262:2025, 4.4.1.4, (101); 4.4.2.3.9). Das Werkzeug rechnet die
      Zwängung immer mit `f_ctm`. Vorschlag: zur Kenntnis, oder ein Schalter
      an der Zwängung. Entscheid des Benutzers.
- [ ] **Wann reisst der Querschnitt in der Spannung-Dehnung-Analyse?**
      Eingebaut: sobald der Beton ohne Stahl `k_t·f_ctm` erreicht, mit `k_t`
      für `h/3` beim Moment und für `h` bei der Normalkraft. Die Norm nimmt
      `f_ctm` oder eine Fraktile, 0.7 oder 1.3·`f_ctm`, ohne `k_t`
      (SIA 262:2025, 4.2.1.14; 3.1.2.2.5, (7) und (8)), und rechnet den
      ungerissenen Querschnitt mit dem Stahl (4.1.4.1.4). Beispiel Platte
      h = 300 mm: das Rissmoment liegt 5 % tiefer als mit `f_ctm`, die
      Rissnormalkraft 13 %; ohne Stahl kommen bei ρ = 0.5 % je Seite rund
      5 % dazu. Für Durchbiegungen ist das die sichere Seite, für Zwangkräfte
      nicht. Wegen der zwei `k_t` reissen die M-χ- und die N-ε-Linie beim
      selben N und M auch nicht am selben Punkt: die M-χ-Linie bei
      N = 300 kN bei 26.4 kNm, die N-ε-Linie bei M = 26.4 kNm schon bei
      228 kN. Vorschlag: `f_ctm`, wahlweise 0.7·`f_ctm` oder 1.3·`f_ctm`, am
      Querschnitt mit Stahl -- dann reissen beide Linien am selben Punkt.
      Entscheid des Benutzers.
- [ ] **Der äquivalente E-Modul** (Spannung-Dehnung-Analyse, M–E_eq und
      N–E_eq) zählt die Verformung ab dem Zustand ohne laufende Kraft (deine
      Wahl, 2026-10-11): `E_eq = M/(I_c·(χ − χ_0))`. Ein Modell mit dem
      ungerissenen Betonquerschnitt gibt damit die Verformung aus der
      laufenden Kraft wieder, nicht, was die feste allein verformt. Er gilt
      für den Querschnitt, ohne Zugversteifung -- für eine Durchbiegung liegt
      er damit tief (sicher), für Zwangkräfte nicht. SIA 262:2025 kennt
      keinen solchen Modul (geprüft am 2026-11-14); bestätigen lassen.
- [ ] **Der kürzeste Abstand bei der genauen Linie** misst zum gezeichneten
      Polygon des Fächers (80 Schritte je Abschnitt), nicht zum genau
      gesuchten Rand wie Normalkraft und Moment konstant.

### Querschnittsanalyse

Je eine Annahme eingebaut, im Code mit «nach Vorgabe, nicht nachgeschlagen».

- [ ] **C-Punkt bei beliebiger Form.** Eingebaut: ganz gedrückt darf der
      Beton am Punkt im Abstand `(1 − ε_c1d/ε_c2d)·h` vom gedrücktesten Rand
      nicht über `ε_c1d` gestaucht werden, mit `h` als Ausdehnung des Betons
      senkrecht zur Nulllinie. SIA 262:2025 regelt den Punkt nicht, auch bei
      der Platte nicht (gesucht in 4.2.1, 4.3.2, 4.3.7); er ist strenger als
      die Norm und liegt damit sicher. Vom Benutzer bestätigen lassen.
- [ ] **Federmodell und Bredt.** Eingebaut: die Querkraft verteilt sich nach
      der Steifigkeit `k = b_w·l` (reine Verschiebung), das Versatzmoment
      tragen die Zellen nach Bredt, mehrzellig mit gleicher Verdrillung. Ohne
      Zelle tragen die Federn die Torsion mit Drehung. Bredt für eine Zelle
      steht in der Norm (SIA 262:2025, 4.3.5.2, (55), Figur 20), das
      Zusammenzählen mit der Querkraft deckt 4.3.5.5. Das Federmodell, die
      Aufteilung auf mehrere Zellen und die Torsion ohne Zelle stehen nicht
      darin: nach Vorgabe eingebaut, in SIA 262:2025 nicht gefunden. Einen
      Vollquerschnitt rechnet die Norm als Zelle (4.3.5.1). Vom Benutzer
      bestätigen lassen.
- [ ] **Längszugkraft aus Querkraft und Torsion.** Die Formel ist bestätigt
      (SIA 262:2025, 4.3.3.4.11, (51); 4.3.5.4): je Stück einer Wand
      `ΔN = |q|·l·cot α`, halb in jedem Gurt. Die Norm verlangt sie immer;
      das Werkzeug rechnet sie in der Querschnittsanalyse nur auf Wunsch
      (Vorgabe aus) und bei der Platte mit Bügeln gar nicht. Vorschlag: in
      der Analyse Vorgabe ein, bei der Platte im Bericht als nicht
      nachgewiesen ausweisen. Entscheid des Benutzers.
- [ ] **k_t bei beliebiger Form.** Eingebaut: beim Moment `t` = ein Drittel
      der Ausdehnung des Betons in Biegerichtung (z für M_y, y für M_z), unter
      Zug die kleinere Seite des umschreibenden Rechtecks. Die Norm nimmt die
      kleinste Abmessung des gezogenen Teils, ein Drittel der Höhe nur bei
      Biegung von Platten und Rechtecken (SIA 262:2025, 4.4.1.3). Bei Steg,
      Flansch oder Hohlkasten liegt `k_t` darum zu tief, auf der unsicheren
      Seite. Beispiel Plattenbalken, Steg 200 × 800 mm unter einer Platte
      600 × 200 mm, Zug unten: heute t = 333 mm und `k_t` = 0.857, nach der
      Norm zählt der Steg, t = 200 mm und `k_t` = 0.909 -- Rissmoment und
      Mindestbewehrung rund 6 % zu klein. Unter Zug heute `k_t` = 0.769
      (t = 600 mm) statt 0.909. Vorschlag: `t` aus der Dicke des gezogenen
      Teils (Steg- oder Plattendicke); einfach und sicher wäre die dünnste
      Wand des Querschnitts. Entscheid des Benutzers.
- [ ] **Wanddicke im vollen Querschnitt.** Für die Torsion zählt eine Wand
      eines Vollquerschnitts höchstens `d_k/8` dick, `d_k` der grösste Kreis
      in `A_k` (SIA 262:2025, 4.3.5.3, (56)); für die Querkraft allein zählt
      die Stegbreite. Das Beispiel «Unterzug» 300 × 600 nimmt 100 mm, für die
      Torsion wären höchstens 25 mm erlaubt -- es rechnet sie viermal zu
      dick. Vorschlag: Hinweis am Feld «Dicke» mit beiden Regeln, im
      Beispiel 25 mm oder Torsion und Querkraft getrennt. Entscheid des
      Benutzers.
- [ ] **Querkraft: Eingabegrenzen.** Die Neigung der Druckdiagonalen darf
      1° bis 89° sein, `k_c` beliebig gross. Die Norm erlaubt höchstens 45°
      (SIA 262:2025, 4.3.3.3.2, (42)), mit festem `k_c` mindestens 30°, bei
      bedeutendem Normaldruck 25° (4.3.3.3.3), und `k_c` höchstens 1
      (4.2.1.7). Vorschlag: Feldgrenzen 25° bis 45° und `k_c ≤ 1`, mit Hinweis
      auf 30°. Entscheid des Benutzers.
- [ ] **Querkraft: Regeln, die das Werkzeug nicht prüft.** Mindestbügel und
      grösster Bügelabstand (SIA 262:2025, 5.5.2.2, (116); 5.5.3.4); die
      feste Dehnung `1.5·f_yd/E_s`, wo die Biegebewehrung plastisch werden
      kann, etwa nach der Streifenmethode (4.3.3.2.3, (41)) -- das Werkzeug
      nimmt sie erst über `m_Rd`; dort auch `α_min = 40°` und `k_c = 0.4`
      (4.3.3.3.3, 4.2.1.7); abgestufte Längsbewehrung, schiefe Querkraft,
      Einzellast nahe am Auflager (4.3.3.2.4, 4.3.3.2.5, 4.3.3.2.8); wo der
      Schnitt für `V_Ed` liegt (4.3.3.2.1, 4.3.3.4.1). Zur Kenntnis; was
      davon das Werkzeug prüfen oder am Feld sagen soll, entscheidet der
      Benutzer.
- [ ] **Spannung-Dehnung-Analyse je Zugseite.** Eingebaut
      (`spannungsanalyse/schnitt.py`): unter reiner Biegung kippt die
      Nulllinie, bis kein Moment um die andere Achse bleibt, «einachsig»
      bleibt sie parallel zur Achse (Benutzer, 2026-10-17). Der Riss am
      ungerissenen Bruttoquerschnitt (`nachweis/rissgroessen.py`):
      `M_Riss(N) = (f_ct,eff − N/A)·W` mit W zur Ecke, die unter reiner
      Biegung zuerst reisst, und `N_Riss(M) = (f_ct,eff,t − σ_M)·A` an der
      Ecke, an der das am wenigsten Zug braucht; `k_t` für ein Drittel der
      Tiefe bzw. für `min(h; b)`, die Regeln der Platte, übertragen (siehe
      «k_t bei beliebiger Form» und «Wann reisst der Querschnitt …»); `f_ctm`
      vom Beton der Ecke. Der äquivalente Modul am Bruttoquerschnitt (`I`,
      `A`), gekippt mit `I_y − I_yz²/I_z`.
- [ ] **Gebrauchsnachweise.** Eingebaut (`nachweis/qa_gebrauch.py`), je auf
      Vorgabe des Benutzers vom 2026-10-15: die Zwängung auf Normalkraft am
      ganzen Querschnitt, `N_Riss = Σ A_c·k_t·f_ctm` mit `t` als kleinerer
      Seite des umschreibenden Rechtecks (siehe «k_t bei beliebiger Form»),
      gegen `Σ A_s·σ_s,adm` aller Stäbe. Mit dem Schalter «500 mm» zählt bei
      massigen Bauteilen nur der Beton bis 250 mm vom Rand, und `k_t` gilt
      für 500 mm (SIA 262:2025, 4.4.2.3.7) -- seit 2026-11-14, vorher
      begrenzte der Schalter nur `t`. Die Zwängung auf Biegung je Richtung
      mit dem Rissmoment des spröden Versagens gegen das Moment, bei dem der
      erste gezogene Stab `σ_s,adm` erreicht -- gerissen und elastisch wie in
      4.1.4.1.4; ohne N, mit eigenem φ und mit der gedrückten Bewehrung (die
      Platte lässt sie weg), dazu sagt die Norm nichts. `σ_s,adm` je Stab mit
      seinem Durchmesser und dem `f_ctm` seines Betons, wie (102) es will;
      eine verschmierte Linie mit einem fiktiven Durchmesser (siehe «Welcher
      Durchmesser …»).
- [ ] **Knicken je Richtung.** Eingebaut (`nachweis/qa_knicken.py`): je Fall
      zu einer Zugseite, die Nulllinie parallel zur Achse wie einachsig --
      ein unsymmetrischer Querschnitt, der um beide Achsen zugleich knickt,
      wird nicht erfasst; SIA 262:2025, 4.3.7 regelt das nicht. `d` für die
      Mindestausmitte `d/30` (4.3.7.5) reicht bis zum entferntesten Stab in
      Zugrichtung statt bis zum Schwerpunkt der Zugbewehrung: `e_0d` wird
      etwas grösser, das liegt sicher.

### Balkensysteme

- [ ] **Durchbiegung gegenüber den Auflagern.** Das Balkensystem misst w je
      Stab gegen die Gerade zwischen seinen Enden; die Norm misst gegenüber
      den Auflagern (SIA 262:2025, 4.4.3.1.1), beim Kragarm über die doppelte
      Länge (SIA 260:2013, 1.2.2). Beispiel mit EI = 22 693 kNm² und
      q = 10 kN/m: einfacher Balken 6 m, w = 7.44 mm (L/w = 807) -- liegt ein
      Knoten in Feldmitte, zeigt die App 1.60 mm. Kragarm 2 m: die Spitze
      senkt sich 0.88 mm, die App zeigt 0.14 mm. Seit 2026-11-14 sagt der
      Bericht das, und L/w steht nicht mehr da. Vorschlag: w je Feld gegen
      die Verbindung seiner Auflager messen, mit L/w; ein Feld reicht über
      Knoten ohne Lager, an denen zwei Stäbe in einer Flucht stossen, und am
      Kragarm gilt die doppelte Länge. Offen bliebe der Abfangträger: eine
      Stütze, die auf ihm steht, sieht aus wie eine, die ihn trägt.
      Entscheid des Benutzers.

## Noch nicht gebaut

- [ ] **Durchstanzen, nächste Schritte:** Stahlpilze an Rand und Ecke
      (der Katalog hat nur ganze Pilze); Durchstanzbewehrung an Wandende und
      Wandecke; weitere Produkte (DURA-Körbe und S-Elemente, HDB, FIDECA);
      Sicherung gegen Totaleinsturz (4.3.6.7).

- [ ] **Balkensysteme, nächste Schritte:** Umhüllende der Kombinationen,
      Theorie 2. Ordnung, Schubverformung, schiefe Lager, und die
      Schnittgrössen eines Stabs als Einwirkung einer Platte oder
      Querschnittsanalyse.

- [ ] **Querschnittsanalyse, nächste Schritte** (je ein eigener Plan):
      Baustahl (Sortentabelle, Gesetz, Verbundquerschnitt, Stahlwände mit
      eigenem G; in der Zeichnung pastellblau, `--mat-baustahl`), Holz (wie spröd Zug und Druck sind, legen wir vorher fest),
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
- [ ] **k_σ der Parabel nie unter 1.** Mit dem kriechweichen Modul
      `E_cm/(1+φ)` und charakteristischen Werten wird `E_c/(400·f_c)` kleiner
      als 1 (C30/37, φ = 2: 0.93); dann hätte der Nenner der Parabel im
      ansteigenden Ast eine Nullstelle. Angesetzt wird `max(1; E_c/(400·f_c))`:
      der Beton ist dann bis f_c bei ε_c1d linear -- nach Vorgabe;
      SIA 262:2025, 4.2.1.6 nennt keine Untergrenze. Das Kriechen über den
      Modul der Parabel ist ebenfalls Vorgabe; beim Druckglied setzt es die
      Norm über die Krümmung an (siehe «Kriechen beim Knicken»).
- [ ] **Das Ende der Linien** liegt an den Grenzen des Dehnungsfächers:
      Betonrand −ε_c2d (Tabelle 8), Stahllagen ±ε_ud (Tabelle 9), Punkt C
      −ε_c1d bei `z_C = h·(1 − ε_c1d/ε_c2d)` -- dieselben Grenzen wie in
      `nachweis/dehnungsfaecher.py`; Punkt C nach Vorgabe (siehe oben).

## Erledigt zuletzt

Aus der Strukturdurchsicht vom 2026-11-09, Punkt 12 zu Ende: der Stahl nur
auf Zug als eigene Art (`StahlNurZug`) · eine Grundlage der Rechenobjekte
(`Rechenobjekt`: `id_von`, `ins_rechenwerk`) · der Vertrag der Bauteile
(`BauteilEintrag`: `materialien`, `bezuege`), mit einem Test ·

Aus der Strukturdurchsicht vom 2026-11-09, Punkt 12 zum Teil: Totes und
nur Geschriebenes weg, im Kern, im JS und im Stilblatt · der Dienst fängt
nicht mehr, was `bearbeite` schon fängt ·

Aus der Strukturdurchsicht vom 2026-11-09, Punkt 10: die Einheiten der
Anzeige an einer Stelle (`web/anzeige.py`), mit den Einheiten des Kerns
statt nackter Faktoren · die Legenden der Situationsbilder von Grundbruch,
Setzung und Durchstanzen aus dem Kern, als Zeilen aus Text und Formeln ·

Aus der Strukturdurchsicht vom 2026-11-09, Punkt 9: je Seite eine Lage im
Schwerpunkt nach einer Regel (`je_seite`), für den Löser in der
Handrechnung und die Resistenzlinie aus Handrechnung · der Schwerpunkt
mehrerer Flächen an einer Stelle (`schwerpunkt`) ·

Aus der Strukturdurchsicht vom 2026-11-09, Punkt 8: die vier Nachweise je
Lage der Platte auf einer Schablone (`Lagennachweis`) -- Lagenwahl, Grade,
Bezüge und Schleife einmal; eine leere Lage, wo keine hingehört, meldet
sich ·

Aus der Strukturdurchsicht vom 2026-11-09, Punkt 5: die Zeichendaten aller
Bauteile unter einem Schlüssel, je Art an einer Stelle · Kennzahlen für
jedes Bauteil · die Vorlagen des Katalogs im selben Durchgang wie die
Feldangaben, unter denselben Namen, und je Liste die Vorlage eines neuen
Eintrags · die Karten und die Übersicht einer Art als Felder ihrer Zeile in
apps.js · ein Test, der jede Art in jedem Verzeichnis und jedes Sinnbild
findet ·

Aus der Strukturdurchsicht vom 2026-11-09, Punkt 11: der Nachweis in
core/nachweis.py · die Prüfprojekte in projekt/beispiele.py · das Modell
des Balkensystems in aufbau/balkensystem.py · die Bilder der Platte und
ihre Karten in platte_bilder.js ·

Aus der Strukturdurchsicht vom 2026-11-09, Punkt 3: eine Grundlage für die
Apps mit Zeichenfenster (`cad_app.js`) -- Lesen, Schreiben, Fenster je
Kennung, Wählen von aussen, Vergessen, die Liste darunter, Lagefelder,
Umriss, Knotennamen ·

Aus der Strukturdurchsicht vom 2026-11-09, Punkt 7: der Katalog über
`katalog(…)`, das einen fehlenden Schlüssel mit seinem Pfad meldet, und ein
Test, der jeden Pfad der Oberfläche im Kern nachschlägt · eine Fassung des
Projekts statt dreier Abdrücke von Hand, und der Kern merkt sich die
Diagramme einer Analyse unter ihrem Abdruck · ein Speicher der Ansichten je
Kennung, geleert beim Anlegen, Kopieren, Löschen und Öffnen ·

Aus der Strukturdurchsicht vom 2026-11-09, Punkt 6: ein Eintrag wird über
seine Kennung gefunden und geändert (`eintragVon`, `eintragAendern`),
gleich in welcher Liste -- ohne Listennamen, ohne `anBauteil` und ohne
acht eigene Leser ·

Aus der Strukturdurchsicht vom 2026-11-09, Punkt 4: Lage und Form der
gestützten Fläche als Art, die weiss, was der Nachweis braucht · die Maske
zeigt die Felder, die der Katalog je Wahl nennt ·

Aus der Strukturdurchsicht vom 2026-11-09, Punkte 1 und 2: ein
Schnittnachweis für Stütze, Anker und Pilz, jede Bedingung einmal gerechnet
und einmal geschrieben · ein Grad ohne Urteil ist unbeschränkt, das setzt
der Kern für jeden Nachweis · Leisten und Pilz getrennt im Befund, ohne
Platzhalter ·

Vier Fehler der Durchsicht (2026-10-17): ein unlesbarer Stand im Browser
bleibt erhalten · die Konsole hängt nicht mehr bei NaN, ein Umschlag für
alle Antworten · Löschen fragt den Kern, auch nach dem Bügelstahl · gleiche
und fast gleiche Namen melden sich vor dem Rechnen, in allen Listen ·
Werteabdruck als Netz für die Umbauten ·

Ein Modell der Werkstoffgesetze (C2, 2026-10-16): jedes Gesetz rechnet und
schreibt sich selbst, aus denselben Ästen · jenseits der Grenze null, auf
ihr um eine Rundung · die Querschnittsanalyse baut ihren Beton wie die
Platte und ihre Werkstoffe an einer Stelle · Punkt C an einer Stelle · der
Hinweis zu Randdehnungen misst Druck und Zug je für sich ·

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
