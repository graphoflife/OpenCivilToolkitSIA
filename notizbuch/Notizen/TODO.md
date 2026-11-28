# Was noch offen ist

Reihenfolge ungefähr nach Dringlichkeit. Erledigtes wandert raus — was dabei
gelernt wurde, steht in [[Entwicklung]].

---

## Fragen an den Benutzer – Plan vom 2026-11-27

Der Benutzer will den Plan vom 2026-11-27 ganz abgearbeitet haben und die
Fragen erst am Schluss mit Claude durchgehen (2026-11-27). Bis dahin
sammeln sie sich hier, je mit dem, was vorläufig gebaut ist.

- [ ] **Knicken und Kippen: die Spalten in den Kern?** Zeichen, Einheiten
      und Titel der Felder stehen noch in `qa_stabilitaet.js`. Das
      widerspricht «Felder, Gruppen und Zeichen einer Maske kommen aus dem
      Kern». Vorschlag: als eigener kleiner Schritt nach dem Plan; in
      Schritt 5 blieb es liegen, weil dort nur die Vorlagen umzogen.
      Vorläufig unverändert.
- [ ] **App-Kacheln: kürzere Namen?** In den kleineren Kacheln braucht
      «Querschnittsanalyse» drei Zeilen («Quer-schnitts-analyse»), die
      anderen höchstens zwei. Vorschlag: so lassen, die Reihe ist nur so
      hoch wie nötig. Sonst etwa «Querschnitt». Vorläufig mit Trennstellen.
- [ ] **Seitenleiste: ab welcher Breite neben der Zeichnung?** Die Felder
      eines Werkzeugs stehen rechts der Zeichnung, sobald das Zeichenfenster
      mindestens 640 px breit ist, sonst darunter. Bei einem Bildschirm von
      1366 px ist es in der Mitte nur 465 px breit: die Leiste steht unter
      der Zeichnung, man rollt zu ihr. Neben der Zeichnung steht sie ab
      etwa 1715 px Bildschirmbreite, im Vollbild (bei 1366 px: Zeichnung
      595, Leiste 360 px) oder wenn man die Mitte breiter zieht. Die
      andere Möglichkeit wäre die Regel des Fensters «Knicken und Kippen»:
      die Mitte wird breiter, solange der rechten Tafel 300 px bleiben –
      bei 1366 px stünde die Leiste dann neben der Zeichnung, aber der
      Bericht hätte nur noch 300 statt 519 px. Vorschlag: so lassen, für
      langes Zeichnen das Vollbild. Vorläufig: 640 px.
- [ ] **Wasser: «fest» statt «SIA»?** Das Wasser bleibt wie eine Normsorte,
      wie es ist, steht aber in keiner Norm. Es heisst darum «Feste Sorte»
      und trägt die Marke «fest», wo Normsorten «SIA» tragen. Vorschlag: so
      lassen. Sonst etwa «Vorgabe». Vorläufig: «fest».
- [ ] **Beim Umschalten die Zahl der anderen Stellung übernehmen?** Heute
      behält jede Stellung ihre Zahl. Vorschlag: so lassen, hin und her geht
      nichts verloren; sonst wäre eine früher eingegebene Zahl weg.
      Vorläufig: jede Stellung behält ihre Zahl. Zwei Stellen:
      - Spannglied: wer 4 Litzen ⌀15.7 hat (600 mm²) und auf «Fläche A_p»
        schaltet, sieht dort 150 mm², die Vorgabe, oder was er früher
        eingab – nicht 600 mm².
      - Pfahl (Schritt 6): wer nach einem statischen Versuch η_a «aus der
        Grundlage» hat (1.0) und auf «von Hand» schaltet, sieht dort 0.7,
        die Vorgabe, oder was er früher eingab – nicht 1.0.
- [ ] **Erdbeben: die Tabellen der Herleitung von unten nach oben?** Die
      Listen der Eingabe stehen jetzt von oben nach unten wie das Gebäude
      (Schritt 8), die Tabellen der Herleitung – Gewichte, Steifigkeit,
      Auslenkung, Kräfte – weiter von unten, «1: EG» zuerst. Vorschlag: so
      lassen; die Formeln zählen von unten (z_i = Σ h_j, j ≤ i), und die
      Summen lesen sich von der Einspannung her. Sonst umdrehen wie die
      Eingabe. Vorläufig: von unten.
- [ ] **Erdbeben: «+ Geschoss» über der Liste?** Ein neues Geschoss kommt
      oben dazu, mit Kern und η_EI des obersten; der Knopf steht darum über
      der Liste, wo es erscheint, nicht darunter wie in den anderen Listen.
      Vorschlag: so lassen. Vorläufig: oben.
- [ ] **Erdbeben: mit T₁ von Hand braucht jedes Geschoss einen Kern, sobald
      eines einen hat?** Hat ein Geschoss einen Kern, rechnet das Gebäude
      erst, wenn jedes einen hat – auch mit T₁ von Hand, wo nur der Kern am
      Fuss die Kräfte verteilt. Vorschlag: so lassen; ein Geschoss ohne Kern
      ist meist vergessen, und die Meldung sagt, welches. Sonst genügte mit
      T₁ von Hand der Kern am Fuss. Vorläufig: jedes braucht einen.
- [ ] **Schubfluss: Δx = 10 mm und das Vorzeichen von ΔM?** Gerechnet wird
      v = |F′(M + ΔM) − F′(M)|/Δx mit ΔM = |V|·Δx, im Vorzeichen von M – das
      Moment wächst im Betrag. Gibt es bei M + ΔM keine Gleichgewichtslage,
      gilt M − ΔM. Angegeben ist der Betrag von v. Beispiel Plattenbalken:
      ΔM = 400 kN · 10 mm = 4 kNm, v = 210.9 kN/m; mit Δx = 1 mm ändert
      sich v um weniger als 0.01 %, mit 100 mm um 0.2 %. Vorschlag: so
      lassen. Vorläufig: 10 mm, im Betrag wachsend.
- [ ] **Schubfluss: der Pfeil zeigt zuerst links der Zeichenrichtung?** Wer
      von links nach rechts zeichnet, bekommt den Pfeil nach oben; der
      Schalter «Pfeil» nennt die Richtung im Bild, «nach oben | nach
      unten». Für v spielt die Seite kaum eine Rolle: was der eine Teil
      gewinnt, verliert der andere – nur ein Stab genau auf dem Schnitt
      zählt nie zum abgetrennten Teil. Sie bestimmt, welcher Teil getönt
      ist und welche Fläche A′ dasteht. Vorschlag: so lassen. Vorläufig:
      links.
- [ ] **FEM: Netzweite 0.5 m als Vorgabe?** Gemessen auf der Seite
      (Python im Browser), je Rechnung der Decke: das Beispiel «Kolloquium 4
      nach FEM», 9 × 5.5 m, 0.3 s bei 0.5 m; eine Decke von 20 × 15 m 3 s
      bei 0.5 m (1394 Knoten) und 0.4 s bei 1 m. Nach jeder Änderung rechnet
      die Seite die Decke heute zwei- bis dreimal (Zeichnung,
      Zusammenfassung, Bilder), bei 20 × 15 m also 6 bis 10 s. Mit 1 m
      wird es ungenau: die gelenkige Platte 6 × 4 m biegt sich nach Navier
      um 10 % weniger als richtig (bei 0.5 m 2.6 %, bei 0.25 m 0.6 %), die
      Momente um 2 % (0.7 %). Vorschlag: 0.5 m lassen; für grosse Decken
      beim Zeichnen 1 m und für den Bericht 0.5 m. Vorläufig: 0.5 m. Die
      Grenze von 3000 Knoten (`KNOTEN_HOECHSTENS`, nach Vorgabe) heisst auf
      der Seite etwa 9 s je Rechnung.
- [ ] **FEM: schneller rechnen?** Zwei Wege, unabhängig vom Plan:
      (a) Zeichnung und Bilder fragen nacheinander nach derselben Decke, und
      jede rechnet sie neu (`_bauteil_rechnen` in `web/dienst.py` merkt
      sich nichts) – ein kleiner Speicher dafür spart eine der zwei oder drei
      Rechnungen, in jeder App. (b) Der Gleichungslöser
      (`stabwerk/matrix.py`) mit `math.sumprod` statt `sum(map(mul, …))`:
      die Zerlegung der Decke 20 × 15 m 0.48 statt 0.75 s, die Ergebnisse
      gleich bis auf 10⁻¹². Vorschlag: beides, je als eigener Commit.
      Vorläufig: nichts davon.
- [ ] **FEM: die Querkraft eines Trägers am Lager?** Der Balken hat je Stück
      zwischen zwei Knoten eine feste Querkraft; am Lager steht darum die
      des ersten Stücks, und die liegt zu tief: um 7 % bei 0.2 m, 12 % bei
      0.4 m (Träger 4 m, gleichmässige Last). Auch der Ort im Bericht ist
      der Anfang des Stücks: T4 im Beispiel hat V = −116.1 kN bei u = 4.00 m,
      die Stütze steht bei 4.50 m. Vorschlag: die Querkraft am Lager aus den
      zwei Stücken daneben linear bis zum Lager verlängern – bei
      gleichmässiger Last ist das genau. Vorläufig: das erste Stück.
- [ ] **FEM: die Stütze als Punkt?** Sie hält die Platte nur in ihrer Mitte;
      b_x und b_y rechnen nicht mit. Über ihr wachsen die Momente mit
      feinerem Netz ohne Grenze – der Bericht sagt es in einem Hinweis.
      Anders ginge es mit allen Knoten in b_x × b_y festgehalten; das braucht
      aber ein Netz, das feiner ist als die Stütze. Vorschlag: so lassen.
      Vorläufig: Punkt.
- [ ] **FEM: die nötigen Biegewiderstände auch als Bild?** Heute stehen sie
      in beiden Verfahren nur im Bericht, als grösster Wert mit Ort. Als
      Bild wären es vier mehr: m_xu, m_yu, m'_xu, m'_yu. Vorschlag: ja, als
      kleiner Schritt nach dem Plan. Vorläufig: nur im Bericht.
- [ ] **FEM: was nach Vorgabe gebaut ist, nicht nachgeschlagen.** Je mit dem
      Vorschlag «so lassen»:
      - eine Einzellast über l_x × l_y verteilt, wie in der Streifenmethode,
        statt im Punkt;
      - der Steg eines Trägers (b × h_T) wiegt mit, in beiden Verfahren,
        wenn der Lastfall das Eigengewicht hat;
      - eine Last geht an die Ecken ihres Dreiecks, als wäre w dort linear;
      - die Kraft längs eines Linienlagers mit den Nachbarn ausgeglichen
        (1-2-1), an Enden, Ecken und Stössen im Punkt;
      - ein Träger auf der Fuge zweier Platten nimmt h der ersten;
      - Zonen gelten nur in der Streifenmethode; in der FEM sagt es eine
        graue Meldung.
- [ ] **Fachwerkmodell: das Lagerzeichen immer unter dem Punkt?** Ein
      Lager fest in x und y oder nur in y steht mit seinem Dreieck unter
      dem Punkt, eines nur in x links davon – auch wo es oben an der
      Scheibe hängt; dann liegt das Zeichen auf ihr. Vorschlag: so lassen,
      später nach aussen drehen, wo kein Material ist. Vorläufig: unten,
      nur in x links.
- [ ] **Fachwerkmodell: die Suche von selbst starten?** Heute sucht sie nur
      auf Knopfdruck, «Fachwerk suchen» im Fenster «Verfahren»; nach einer
      Änderung sagt die Kachel grau «neu zu suchen». Auf der Seite dauerte
      die Suche für die Wandscheibe mit Türe am 2026-11-27 4.5 s bei
      h = 0.55 m und 40 s bei 0.25 m, seit dem 2026-11-28 eher weniger;
      von selbst liefe sie nach jedem Verschieben eines Knotens an.
      Vorschlag: so lassen. Vorläufig: auf Knopfdruck.
- [ ] **Fachwerkmodell: unter gleich leichten Fachwerken das mit den
      wenigsten Stäben?** Tragen zwei Wege gleich leicht – etwa zwei
      Diagonalen –, endet die Optimierung in ihrer Mitte: beide mit halber
      Kraft. Danach fallen die Stäbe unter N_min der grössten Kraft weg
      (Vorgabe 1 %), und das Gleichgewicht wird ohne sie neu gesucht; was
      darüber liegt, bleibt. Bei h = 0.4 m sind es so 74 statt 89 Stäbe,
      gleich leicht. Ein Schritt am Schluss, der unter den gleich leichten
      eines mit wenigen Stäben wählt, wäre eigene Arbeit. Ein höheres
      N_min hilft nur, wo das Gleichgewicht ohne die dünnen Stäbe aufgeht;
      sonst halbiert die Suche die Schwelle, bis es aufgeht, und ein grauer
      Hinweis sagt, dass dünne bleiben. Bei h = 0.4 m geben N_min = 1, 5
      und 10 % dieselben 74 Stäbe: ohne die Stäbe unter 0.5 % der grössten
      Kraft blieben 0.8 % der grössten Last offen. Vorschlag: so lassen.
      Vorläufig: so.
- [ ] **Fachwerkmodell: mit «Zug nur waagrecht und senkrecht» im feinen
      Raster viele Bänder?** Die Konsole 1 × 2 m hat mit dem Schalter im
      Raster von 1 m 7 Stäbe (V = 400 kNm), bei 0.5 m 14 (375 kNm), bei
      0.25 m 39 (372.5 kNm): der Zug verteilt sich auf viele dünne Bänder,
      wie eine verteilte Bewehrung. Das ist das Optimum dieser Aufgabe;
      ohne die dünnen Bänder geht das Gleichgewicht nicht auf, auch ein
      höheres N_min räumt nicht auf. Vorschlag: so lassen; für ein Modell
      zum Lesen das gröbere Raster. Vorläufig: so.
- [ ] **Fachwerkmodell: was nach Vorgabe gebaut ist, nicht nachgeschlagen.**
      Je mit dem Vorschlag «so lassen»:
      - die Rasterweite h = 0.5 m;
      - waagrecht oder senkrecht heisst bis auf 10⁻⁹ der Länge, also nur
        Rundung;
      - höchstens 600 Knoten; ein Raster mit mehr als 200 000 Punkten im
        Rechteck um die Scheibe wird gar nicht erst gelegt;
      - die erste Runde nur mit Stäben bis 1.5 h;
      - w_Z = 1, Zug zählt wie Druck, wählbar von 0.1 bis 10; N_min = 1 %
        der grössten Kraft, wählbar von 0 bis 50 %;
      - geht das Gleichgewicht ohne die dünnen Stäbe nicht auf, halbiert
        die Nachbearbeitung die Schwelle, höchstens 30-mal und nur in der
        letzten Runde – in jeder Runde dauerte die Suche bei 0.5 m 5 statt
        2 s;
      - zwei Stäbe in einer Flucht durch einen Knoten ohne Last und Lager
        werden einer;
      - die Optimierung: Genauigkeit 10⁻⁸, höchstens 100 Schritte, je
        Schritt 99.5 % des Wegs zum Rand; offen bleiben darf vom
        Gleichgewicht 10⁻⁶ der grössten Last, und ein Rest kostet das
        Tausendfache dessen, was die Last über die Diagonale der Scheibe zu
        tragen kostete.
- [ ] **SIMP: das Fachwerk schwerer als das der Ground Structure?** Die
      Wandscheibe mit Türe hat mit der Ground Structure V = 7110 kNm im
      Raster von 1 m und 6819 kNm bei 0.5 m. Aus der Form von SIMP kommen
      bei der Netzweite 0.1 m 7836 kNm (26 Stäbe), bei 0.2 m 8706 kNm
      (20 Stäbe) und bei 0.15 m 11970 kNm (22 Stäbe): dort bleibt an der
      Ecke über der Türe ein kleines Dreieck stehen. Die Form ist die
      steifste, nicht die mit dem kleinsten V; das Fachwerk folgt ihr und
      nimmt einen Stab neben ihr nur, wo es ohne nicht geht. Vorschlag: so
      lassen – SIMP zeigt, wie die steife Scheibe trägt, die Ground
      Structure das leichteste Fachwerk; wer beides sehen will, kopiert
      das Modell. Vorläufig: so.
- [ ] **SIMP: die Netzweite 0.2 m als Vorgabe?** Gemessen an der
      Wandscheibe mit Türe, 6 × 3 m:
      - bei 0.2 m 406 Elemente und 93 Schritte: auf der Seite 8 s, ohne
        Browser 3 s;
      - bei 0.1 m 1580 Elemente und 114 Schritte: auf der Seite 89 s, ohne
        Browser 36 s; auf einem Handy länger (nicht gemessen).
      Feiner wird das Fachwerk leichter, 7836 statt 8706 kNm (oben). Eine
      Wand von 10 × 5 m hätte bei 0.1 m 5000 Elemente, mehr als die 2500,
      die das Werkzeug rechnet; bei 0.2 m sind es 1250. Die Form wächst im
      Bild sichtbar, und «Anhalten» liest das Fachwerk jederzeit aus ihr.
      Vorschlag: 0.2 m; wer es feiner will, stellt 0.1 m. Vorläufig: 0.2 m.
- [ ] **SIMP: «Zug nur waagrecht und senkrecht» nur bei der Ground
      Structure?** Die Form kennt keine Richtung des Zugs. Bei SIMP fehlt
      der Schalter; war er an, sagt ein grauer Satz, dass er nur bei der
      Ground Structure gilt. Man könnte beim Fachwerk aus der Form die
      geneigten Stäbe auf Druck beschränken – nur folgen sie dann der Form
      nicht mehr, und oft ginge das Gleichgewicht nicht auf. Vorschlag: so
      lassen. Vorläufig: so.
- [ ] **SIMP: wie das Werkzeug die Form liest – anders als die Quelle.**
      Xia, Langelaar & Hendriks (2020) verbinden die Knoten längs der
      Mittellinien. Das allein war oft beweglich oder schwer: eine
      gebogene Strebe wurde eine Gerade quer durch die Scheibe. Darum:
      - eine Linie, die mehr als 1.5 Netzweiten von der Geraden abbiegt,
        bekommt dort einen Knoten (Douglas & Peucker);
      - Äste, die frei enden, fallen weg, ebenso, was an keinem Lager und
        keiner Last hängt;
      - ein Stab weniger als 10° schief zur Senkrechten oder Waagrechten
        durch ein Lager oder eine Last wird genau so gerückt;
      - jedes Paar von Knoten ist ein möglicher Stab, wenn er im Material
        liegt; neben der Form kostet er bis zum Zehnfachen.
      Vorschlag: so lassen. Vorläufig: so.
- [ ] **SIMP: was nach Vorgabe gebaut ist, nicht nachgeschlagen.** Aus der
      Quelle (Andreassen et al. 2011) sind E_min = 10⁻⁹, p = 3, der Filter
      bis 1.5 Netzweiten, die Änderung von höchstens 0.2 je Schritt, die
      Halbierung bis 10⁻³ und das Ende bei einer Änderung unter 0.01; aus
      Xia et al. (2020) die Schwelle 0.5 und die 5 %. Nach Vorgabe, je mit
      dem Vorschlag «so lassen»:
      - ν = 0.2 wie für Beton, die Quelle nimmt 0.3;
      - höchstens 200 Schritte und 2500 Elemente;
      - je Anfrage der Seite eine Sekunde Schritte;
      - ein Lager und eine Last gehen an die nächste Ecke eines Elements;
      - Netzweite 0.2 m und Anteil Material 30 %, wählbar von 5 bis 80 %;
      - beim Lesen der Form 1.5 Netzweiten, 10°, das Zehnfache, das
        Wegfallen freier Äste und die Paare (oben).
- [ ] **Aus dem Balkensystem: Kombinationen des Gebrauchs?** Eine
      Kombination des Systems hat keine Art. Jede wird Lastfall der
      Tragsicherheit, und die Analyse leitet daraus ihre häufigen und
      quasi-ständigen ab wie aus den eigenen – auch aus einer Kombination,
      die im System schon quasi-ständig gemeint ist. Vorschlag: so lassen;
      später bekommt eine Kombination des Systems eine Art [Tragsicherheit |
      häufig | quasi-ständig] und geht nur in ihre Nachweise. Vorläufig:
      jede als Tragsicherheit.
- [ ] **Aus dem Balkensystem: System und Analyse lassen sich nicht
      löschen?** Nimmt eine Analyse die Stellen eines Systems, zeigt sie auf
      es; ist sie zugleich Querschnitt eines seiner Stäbe, zeigt auch das
      System auf sie. Dann lässt sich keines löschen, bis man eine
      Verbindung löst, etwa in der Kachel das System auf «– wählen –»
      zurückstellt. Vorschlag: so lassen; die Meldung beim Löschen sagt,
      wer zeigt («„Träger" wird gebraucht von: …»). Vorläufig: so.
- [ ] **Aus dem Balkensystem: was nach Vorgabe gebaut ist, nicht
      nachgeschlagen.** Je mit dem Vorschlag «so lassen»:
      - die Vorzeichen: der Querschnitt vom Anfang des Stabs her gesehen,
        M_z und V_y umgekehrt;
      - V_z und V_y je ein Kriterium, nicht die Resultierende;
      - unter 0.001 N oder Nm gilt eine Schnittgrösse als null;
      - nur die Kombinationen, nicht die einzelnen Lastfälle des Systems;
      - bei gleichen Werten die vorderste Stelle des ersten Stabs; ist der
        Extremwert an einem Sprung auf beiden Seiten, beide.
- [ ] **Plattenbereiche: die Eckenregel an den Stufen.** Von einem Schnitt
      an einer Stufe zählt nur, was höchstens 1.5·d_v von einer Ecke
      entfernt liegt, wie um eine grosse Stütze (Figur 23a): zur Stütze hin
      von den Ecken des Bereichs, auf der Gegenseite von den Ecken des
      Schnitts selbst. Auf der Gegenseite ist das streng. Beispiel: Stütze
      400 × 400 mm, Platte 240 mm, Bereich 1200 × 1200 mm mit 320 mm. Um die
      Stütze trägt sie 335.4 kN, an der Stufe 290.1 kN – die Stufe ist
      massgebend. Ohne die Regel zählte der ganze Schnitt innen, denn
      gestützt ist die Platte nur an der Stütze, und die Stütze wäre
      massgebend. Nach Vorgabe, nicht nachgeschlagen. Vorschlag: so lassen,
      es liegt auf der sicheren Seite. Vorläufig: so.
- [ ] **Plattenbereiche: wann an der Stütze d des Bereichs gilt.** Ist ein
      Bereich auf der Gegenseite dicker, gilt sein d an der Stütze nur, wenn
      er weiter als sein d_v über die Stütze hinausreicht. Sonst endete der
      Riss jenseits der Stufe, wo die Zugbewehrung höher liegt, und es gilt
      d der Platte. Beispiel: Stütze 400 × 400 mm, Bereich 800 × 800 mm mit
      320 mm in einer Platte von 240 mm – er reicht 200 mm über die Stütze
      hinaus, d_v im Bereich ist 274 mm: an der Stütze gilt d = 194 mm der
      Platte. Dieselbe Regel gilt an jeder Stufe zur Stütze hin. Nach
      Vorgabe, nicht nachgeschlagen. Vorschlag: so lassen. Vorläufig: so.
- [ ] **Plattenbereiche: ψ mit dem kleinsten d um die Stütze.** Gewählt
      war «ψ aus der Grundplatte, das Konservative». Gebaut ist: ψ rechnet
      mit der kleinsten statischen Höhe der Platte und der Bereiche, die die
      Stütze umschliessen. Meist ist das die Platte; ist ein Bereich um die
      Stütze dünner, ist es seine – mit ihr dreht sich die Platte mehr, das
      bleibt auf der sicheren Seite. Vorschlag: so lassen. Vorläufig: so.
- [ ] **Plattenbereiche: die Kennzahl, wenn eine Stufe massgebend ist.**
      Die Kennzahl «Durchstanzwiderstand am Schnittpunkt» ist die Querkraft
      im Schnitt um die Stütze bei der grössten Stützenkraft, bei der jeder
      Schnitt hält. Ist eine Stufe massgebend, ist sie kleiner als V_Rd,c um
      die Stütze, im Beispiel oben 290.1 statt 335.4 kN, und die Herleitung
      sagt, an welcher Stufe es liegt. So bleibt sie mit V_d eines Nachweises
      vergleichbar. Vorschlag: so lassen. Vorläufig: so.
- [ ] **Plattenbereiche: die Dicke eines neuen Bereichs.** Ein neuer
      Bereich hat h = 360 mm, gleich wie dick die Platte ist; die Seite
      zeigt es im Feld, bevor man zeichnet. Vorschlag: so lassen. Sonst
      etwa die Dicke der Platte plus 80 mm, die der Kern vorgäbe.
      Vorläufig: 360 mm.
- [ ] **Bereich neben der Stütze: wie der Schnitt durch verschiedene
      Dicken gesucht wird.** Die Norm verlangt, jeden möglichen Schnitt zu
      rechnen (4.3.6.2.7), sagt aber nicht, wie. Beispiel: Stütze
      400 × 400 mm, Platte 240 mm, 100 mm neben der Stütze ein Streifen mit
      180 mm – um die Stütze 275.4 kN, durch den Streifen 269.2 kN. Nach
      Vorgabe, nicht nachgeschlagen, je mit dem Vorschlag «so lassen»:
      - 72 Strahlen von der Stützenachse, je 5°, bis 4·d der Platte über
        die Stütze und die Bereiche um sie hinaus, abgetastet alle 0.1·d
        des dünnsten Teils; weiter draussen geht ein Bereich nicht ein, ein
        Hinweis sagt es;
      - der Schnitt hält an jeder Stelle 0.5·d_v ihres d von der Stütze und
        von jedem Bereich, der auf der Druckseite weiter vorsteht;
      - in einen dünneren Bereich darf er gleich an dessen Rand, wo dort
        schon das kleinere d zählt – das ist streng, an der Stufe in
        Schritt 13b lag der Schnitt 0.5·d_v daneben;
      - von der Stütze zählt nur, was höchstens 1.5·d_v ihres d von ihren
        Ecken liegt, mit d der Stelle; an Ecken der Bereiche zählt alles;
      - gesucht wird mit k_e der Stütze, der gefundene Schnitt rechnet mit
        seinem eigenen; die Schatten der Aussparungen nimmt die Suche vom
        Schnitt um die Stütze, die genaue Rechnung von ihm selbst;
      - ein Schnitt mit überall demselben d fällt weg, und ohne Last gibt
        es keinen (ψ hängt von ihr ab) – die Kennzahl sucht ihn trotzdem;
      - der Schnitt um die Stütze und die an den Stufen rechnen weiter mit
        einem d, auch wo ein Bereich daneben in sie reicht.
      Vorläufig: so.
- [ ] **Schnitt durch verschiedene Dicken: blau.** Im Grundriss steht er
      blau, nicht orange wie im Plan – orange ist schon der äussere Schnitt
      der Leisten. Vorschlag: so lassen. Vorläufig: blau.
- [ ] **Leisten im Stützenkopf: ψ in Gleichung (69).** Im Plan stand für
      (69) das ψ des Bereichs, je Formel das Ungünstigere. Gebaut ist:
      (69) rechnet mit demselben ψ wie V_Rd,c – ψ ist die Drehung der
      Platte um die Stütze, eine Zahl –, d ist das an der Stütze. Beispiel:
      Kopf 1200 × 1200 mm mit 320 mm in einer Platte von 240 mm,
      Spannweite 2.5 m, V_d = 800 kN: σ_sd = 364 N/mm²; mit ψ aus dem d
      des Kopfs wären es 258 N/mm². Bei 7 m Spannweite erreicht σ_sd mit
      beiden f_yd. Vorschlag: so lassen. Vorläufig: so.
- [ ] **Leisten mit Plattenbereichen: wo sie liegen.** Sie stehen im
      innersten Bereich um die Stütze, so hoch, wie er dick ist, und
      bleiben c_nom vor seiner Stufe; aus jedem anderen Bereich bleiben sie
      draussen, auch mit c_nom – wie bei einer Aussparung. Beispiel: im
      Kopf 1200 × 1200 mm mit 320 mm sind die Anker 255 mm hoch statt
      175 mm in der Platte; neben einem dünneren Streifen 100 mm vor der
      Stütze fällt die Leiste zum Streifen hin weg. Nach Vorgabe, nicht
      nachgeschlagen. Vorschlag: so lassen. Vorläufig: so.
- [ ] **Leisten im Stützenkopf: der äussere Schnitt.** Er rechnet mit
      d_v,out = d an der Stütze − c_v, auch wo er über die Stufe hinaus in
      die dünnere Platte reicht; dort prüft der Schnitt an der Stufe
      (Figur 24a) die Platte. Im Beispiel liegt er ganz im Kopf: Anker bis
      260 mm, der Schnitt 122 mm weiter, die Stufe bei 400 mm. Nach
      Vorgabe, nicht nachgeschlagen. Vorschlag: mit dem kleinsten d entlang
      des Schnitts rechnen, das liegt sicher. Vorläufig: d an der Stütze.
- [ ] **Mit Plattenbereichen kein Stahlpilz.** Reicht die erste
      Druckdiagonale mit Leisten nicht, sucht das Werkzeug mit Bereichen
      keinen Pilz; ein Hinweis sagt es. Der Pilz rechnet mit der Dicke der
      Platte und kennt keine Stufen. Vorschlag: so lassen, bis jemand
      einen Pilz in einem Stützenkopf braucht. Vorläufig: so.
- [ ] **Leisten an der Stufe: wie sie stehen.** Hält der Schnitt an der
      Stufe eines Kopfs nicht, setzen eigene Leisten am Rand des Bereichs
      an wie an einer Stütze: der Kopf ist ihre gestützte Fläche, sie sind
      so hoch, wie die Platte jenseits dick ist, und es gelten die Werte
      des Schnitts an der Stufe, ψ der Stütze und k_sys wie an der Stütze.
      Beispiel: Kopf 1200 × 1200 mm mit 320 mm, Platte 240 mm,
      V_d = 400 kN – 24 ancoPLUS DX3-0175 um den Kopf, 175 mm hoch. Nach
      Vorgabe, nicht nachgeschlagen. Vorschlag: so lassen. Vorläufig: so.
- [ ] **Leisten an langen Seiten zählen ganz.** In (68) zählen alle
      Leisten, auch die vor Teilen des inneren Schnitts, die nach Figur 23a
      nicht zählen, weiter als 1.5·d_v von einer Ecke. Am Kopf oben stehen
      16 der 24 Leisten vor zählenden Teilen; sie tragen 1475 kN, nötig
      sind 33.9 kN. Die Norm begrenzt ΣA_sw nur im Abstand, 0.35·d_v bis
      d_v (4.3.6.5.4); dasselbe gilt seit jeher an grossen Stützen.
      Vorschlag: nur Leisten vor zählenden Teilen anrechnen, die übrigen
      stehen trotzdem (5.5.3.9) – das liegt sicher. Vorläufig: alle zählen.
- [ ] **Keine eigenen Leisten auf der Gegenseite und durch verschiedene
      Dicken.** Dort liegt der Schnitt im Bereich oder läuft an keiner
      Stufe entlang, an der eine Leiste ansetzen könnte; ein Hinweis sagt,
      dass das Werkzeug dort keine vorschlägt. Vorschlag: so lassen, bis
      jemand es braucht. Vorläufig: so.
- [ ] **Aufräumen: eine Platte oder ein Bereich dünner als die
      Bewehrung tief liegt.** Gefunden beim Bau von Schritt 13c, nicht
      behoben. Heute nimmt das Werkzeug eine Platte mit h = 40 mm an,
      obwohl c und die Stäbe tiefer liegen: d wird −6 mm, und V_Rd,c ist
      negativ. Ebenso einen Bereich mit 40 mm in einer Platte von 240 mm –
      um die Stütze steht dann «erfüllt, ∞». Vorschlag: die Felder h der
      Platte und des Bereichs weisen eine Dicke ab, bei der d nicht über
      null liegt, rot und mit dem Namen. Vorläufig: nicht geprüft.
- [ ] **Mauerwerk: die Dichte je Sorte.** Für das Eigengewicht nimmt jede
      Sorte eine Zeile der SIA 261:2020, Anhang A, Tabelle 28 – die der
      gelochten Steine ihrer Art: Backstein 13, Zementstein und
      Kalksandstein 18, Porenbeton 7 (MP) und 6 kN/m³ (MPL).
      Leichtsteine haben dort keine eigene Zeile und nehmen die ihrer Art –
      ein Leichtbackstein wiegt also wie ein Backstein. Nach Vorgabe, nicht
      nachgeschlagen. Vorschlag: so lassen; wer es genauer weiss, legt ein
      eigenes Mauerwerk mit seiner Dichte an. Vorläufig: so.
- [ ] **Mauerwerk: Porenbeton kriecht wie Kalksandstein.** Tabelle 2 der
      SIA 266 nennt den Endkriechwert für gebrannte, zementgebundene und
      hydrothermisch gebundene Steine; Porenbeton steht nicht dabei. Er
      härtet im Dampf wie Kalksandstein und bekommt darum dessen φ = 1.5.
      Nach Vorgabe. Vorschlag: so lassen. Vorläufig: φ = 1.5.
- [ ] **Mauerwerk: die üblichen Dicken.** Der Schalter unter der Dicke
      bietet je Sorte die Masse an, in denen die Steine meist gehandelt
      werden, etwa Kalksandstein 100, 120, 150, 175, 200 und 250 mm;
      Porenbeton bis 365 mm. Eine andere Dicke rechnet gleich, ein grauer
      Hinweis sagt nur, dass sie unüblich ist – etwa 180 mm. Die Norm nennt
      keine solche Liste. Vorschlag: die Listen mit dem vergleichen, was du
      auf Baustellen siehst. Vorläufig: so.
- [ ] **Mauerwerk: nur rechteckige Wände.** Eine Wand mit schräger Krone,
      etwa ein Giebel, steht rot: «… rechnet das Werkzeug noch nicht». Ihre
      Pfeiler wären verschieden hoch. Vorschlag: so lassen, bis du einen
      Giebel brauchst. Vorläufig: nur Rechtecke.
- [ ] **Mauerwerk: «nicht vollfugig».** Der Schalter der Stossfugen heisst
      [nicht vollfugig | vollfugig]; Tabelle 7 nennt nur die zweite Zeile
      eigens. «Knirsch» wäre enger: ganz ohne Mörtel in der Stossfuge.
      Vorschlag: so lassen. Vorläufig: «nicht vollfugig».
- [ ] **Mauerwerk im neuen Projekt.** Ein neues Projekt hat neu auch das
      Mauerwerk MB, wie es je Materialart eine Sorte hat; so rechnet die
      erste Wand gleich. Vorschlag: so lassen. Vorläufig: mit MB.
- [ ] **Zur Kenntnis – der Plan war ungenau:** In MBL, MCL und MPL steht
      das L für Leichtsteine (SIA 266:2015, 3.1.1.1), nicht für
      Leichtmörtel, wie der Plan schrieb. Gebaut nach der Norm.

## Wünsche vom 2026-11-20

Sechzehn Wünsche des Benutzers, geplant am 2026-11-20: kleines Sichtbares
zuerst, ein Commit je Punkt. Seine Entscheidungen: Sandbox in jedem Projekt
und in jeder App ausser Materialien; «Öffnen» ersetzt alles oder fügt hinzu;
offline nach dem ersten Besuch; MCP mit Projektdateien; Erdbeben mit
Kräften je Geschoss und Wand, ohne Verbindung ins Balkensystem.

- [ ] Startzeiten auf GitHub Pages messen, sobald die Commits vom
      2026-11-20 veröffentlicht sind: erster und erneuter Besuch, ohne Netz.
      Dazu in Chrome prüfen, ob sich die Seite als App installieren lässt;
      verlangt Chrome ein PNG als Zeichen, schreibt ein kleines Skript ohne
      Fremdpakete die Bilder.

## Offen

- [ ] **Meldungen als Hinweise: vier Kopien.** Seit 2026-11-27 macht
      `meldungshinweise` in `web/js/bausteine.js` aus den Meldungen des
      Kerns die Hinweise einer Karte (das Fachwerkmodell nimmt es). Dieselben
      Zeilen stehen noch in `balkensystem.js`, `bs_diagramme.js` und zweimal
      in `decke.js` (`meldungszeilen`, `fallmeldungen`). Aufräumen: alle auf
      `meldungshinweise`.
- [ ] **Erdbeben: der Name eines neuen Geschosses.** «+ Geschoss» nennt es
      «Geschoss n» mit der ersten freien Zahl, wie einen Lastfall. Heissen
      die übrigen «1. OG» bis «8. OG», heisst das neunte darum
      «Geschoss 1». Besser die Zahl seiner Stelle, «Geschoss 9»
      (`aufstocken` in `web/js/erdbeben.js`). Gesehen am 2026-11-27.
- [ ] **Decke: «Der Durchlaufträger steht nicht im Gleichgewicht».** In der Konsole
      des Browsers stand am 2026-11-27 aus einem älteren Test ein Abbruch
      der Rechnung `decke.e2.rechnung`: am Ende eines Streifens blieben
      V = 6.0 N und M = 12.0 Nm übrig (`statik` in `decke/durchlauftraeger.py`,
      Schranke 10⁻⁶ der Lastsumme). Nicht nachgestellt; das Projekt des
      Benutzers rechnet fehlerfrei. Kommt es wieder: den Stand sichern und
      die Lasten am Ende des Streifens prüfen, etwa eine, die nur um die
      Rundung `GLEICH` neben dem Ende liegt.
- [ ] Kurzform hinter dem Auge: weitere Nachweise kennzeichnen. Heute die
      Platte – Biegung bei N = 0, Querkraft mit und ohne Bügel – und seit
      2026-11-18 die Querkraft im Bohrpfahl (Wendel, Druckdiagonalen, das
      Minimum im Erfüllungsgrad). Der Mikropfahl bleibt ohne: sein
      Widerstand ist schon zwei kurze Zeilen. Welche weiter, entscheidet der
      Benutzer.
- [ ] Decken: die Knoten der Lasten anderer Lastfälle bleiben in der
      Zeichnung als Punkte stehen, ohne ihre Last. Prüfen, ob sie mit ihr
      verschwinden sollen.
- [ ] Decken: eine schräge Richtung heisst nach ihrem Winkel, ihre
      Streifen «71.57° 1 … 71.57° 8», und der Bericht nennt den Winkel
      daneben noch einmal. Mit den Ergebnisbildern besser benennen –
      der Benutzer spricht von m_η.
- [ ] Decken: «Knoten einfügen» auf einer Kante, die zwei Platten
      teilen, setzt den Knoten nur in die gewählte Platte; die andere
      behält ihre Kante ohne ihn. Prüfen, ob beide ihn bekommen sollen.
- [ ] Decken: ein Klick auf «40 Streifen tragen nicht …» wählt nichts aus –
      Streifen sind keine Teile der Zeichnung. Die Platten darunter wären
      die Wahl; dafür müsste der Kern wissen, auf welcher Platte ein Träger
      liegt. Gefunden bei der Durchsicht vom 2026-11-19. Seit 2026-11-26
      steht daneben an jeder Platte, wo bei ihr Last ausfällt und warum –
      ein Klick darauf wählt sie; die Meldung je Fall wählt weiter nichts.
- [ ] Zeichenfenster: während eines Befehls heissen P und S «parallel»
      und «senkrecht», nicht Platte und Stütze. Erst Esc, dann die Taste.
- [ ] Decken, nach Vorgabe (`opencivil/decke/`): die automatische
      Aufteilung, wo Folie 31 nichts sagt (die Spannweite eines Kragarms
      zählt doppelt, entschieden wird im Schwerpunkt jeder Zelle; die Mitte
      eines Felds teilt geradlinig bis ganz in die kürzere Spannweite ab
      dem Verhältnis 1.5 – so gewählt vom Benutzer am 2026-11-25, statt
      «innerhalb 1 % je zur Hälfte, sonst ganz»); die Grösse des
      Stützenbereichs, wenn sie fehlt (ein Quadrat, so breit wie die Stütze
      oder der breiteste Träger über ihr – Folie 39 lässt sie offen);
      die Richtungen, die eine Platte selbst wählt (parallel zu den meisten
      Metern Rand, ein Rand quer dazu zählt mit; aneinanderstossende
      gemeinsam – seit 2026-11-26, `decke/richtungen.py`);
      Streifen in zwei Richtungen, die nicht rechtwinklig aufeinander stehen;
      die Linienlast als Band von 1 mm, die Einzellast über 1 × 1 m verteilt;
      ein Wechsel der Steifigkeit eines Streifens, näher als 1 cm an einem
      Lager oder einem anderen Wechsel, gilt dort (seit 2026-11-26,
      `decke/durchlauftraeger.py`, `WECHSEL`); die Bänder, die die Rechnung bei
      automatischer Aufteilung legt (seit 2026-11-26, `decke/baender.py`):
      durch jede Stütze in den Richtungen ihrer Platte, von Lager zu Lager,
      an einer Stütze am Rand ganz in der Platte,
      und innen an offenen Rändern, nur wo die Streifen quer dazu schon ein
      Lager haben; 1 m breit, als Vorgabe im Feld der Decke; auf zwei
      Lagern oder mehr, nie als Kragarm; nie längs über einer Wand; unter
      jedem Träger des Benutzers, die am Rand unter denen über Stützen;
      ein Rand bis 1e-3 rad neben einer Richtung der Platte legt das Band
      in diese Richtung.
      Die Norm sagt zu keinem etwas (geprüft am 2026-11-14): nach der
      statischen Methode gilt jede Aufteilung, die im Gleichgewicht ist
      (SIA 262:2025, 4.1.4.2.2), wenn das Verformungsvermögen gesichert ist
      (4.1.4.2.4); quer braucht es trotzdem mindestens 20 % der
      Hauptbewehrung (5.5.3.2). Die Einzellast selbst steht nach SIA 261:2020,
      Tabelle 8 auf 50 × 50 mm.
- [ ] Decken: B-B des Kolloquiums 4 weicht von der Musterlösung ab
      (−60.1 statt −58.5 kNm/m, Stützen 115.0/276.4 statt 115.5/275.1 kN),
      weil die App die Last aus C-C dort ablegt, wo sie aufliegt, statt mit
      dem Faktor 8.0 über die ganze Länge. Dem Benutzer so vorlegen.
- [ ] **Konstruktive Regeln der Bewehrungssuche.** Die Suche kennt nicht:
      Stäbe über ⌀30 nur ausnahmsweise (SIA 262:2025, 5.2.1); den lichten
      Abstand von mindestens D_max, dem Nachbarstab und 20 mm (5.2.3.2); die
      grösste Teilung 1.2·h und 300 mm (5.5.3.1); die Querbewehrung von
      mindestens 20 % der Hauptbewehrung (5.5.3.2); die Mindestbügel nach
      (116) (5.5.2.2, 5.5.3.4). Beispiel: h = 200 mm mit Teilung 250 mm –
      erlaubt wären 240 mm. Vorschlag: (116), 1.2·h und 300 mm als
      Bedingung, 5.2.1 und die 20 % als Meldung. Entscheid des Benutzers.
- [x] **Bügel und Längsbewehrung in einem Zug suchen.** Erledigt
      (2026-11-19), siehe [[Entwicklung]]. Vorher: mit «Bügel
      mitsuchen» sucht die Platte erst die Längsbewehrung, mit den alten
      Bügeln, dann die Bügel. Bei V_Ed = 400 kN/m und Bügeln ⌀10@200
      scheitert darum die Längssuche an der Querkraft, die Bügelsuche findet
      ⌀12@200, und erst ein zweiter Klick findet die Längsbewehrung (gesehen
      am 2026-11-19). Vorschlag: mit «Bügel mitsuchen» prüft die Längssuche
      die Querkraft mit Bügeln nicht, die Bügelsuche danach schon.
      Entschieden (Benutzer, 2026-11-19): so. Umgesetzt ohne jede Querkraft
      in der Längssuche, auch ohne Bügel vorher: sonst brauchte es dort
      weiter zwei Klicks (h = 300 mm, V_Ed = 250 kN/m).
- [ ] **Mehr Längsbewehrung statt Bügel?** Mit «Bügel mitsuchen» legt die
      Suche die kleinste Längsbewehrung und dann Bügel, wo nötig: bei
      h = 300 mm und V_Ed = 200 kN/m 3896 mm² und ⌀8@200. Mit 4419 mm² ginge
      es ohne Bügel – so sucht sie, wenn der Schalter aus ist. Möglich wäre,
      mit dem Schalter zuerst ohne Bügel zu suchen und nur, wo das nicht
      geht, mit; das kostet dann eine zweite Suche. Vorschlag: lassen, der
      Schalter sagt, wer die Querkraft trägt. Entscheid des Benutzers.
- [x] **Zu dünne Platte: obere und untere Lagen kreuzen sich.** Erledigt
      (2026-11-19), siehe [[Entwicklung]]. Vorher prüfte die Platte
      nur, dass die Überdeckungen zusammen kleiner sind als h
      (`QuerschnittEintrag.regeln`). Bei h = 80 mm und überall ⌀12 liegt die
      3. Lage 32 mm über der Unterkante, die 2. bei 48 mm: «Höhe der
      Distanzhalter −28 mm», und M_Rd wird gerechnet (Durchsicht vom
      2026-11-19). Vorschlag: sind Überdeckungen und Lagen zusammen höher als
      h, rechnet die Platte nicht und sagt es, wie heute bei den
      Überdeckungen; die Bewehrungssuche prüft vorab nur Dicke und
      Überdeckungen, damit sie eine zu dicke Bewehrung ersetzen kann.
      Entschieden (Benutzer, 2026-11-19): so.
- [x] **Doppelte Namen von Fällen schon am Feld abweisen.** Erledigt
      (2026-11-19): `opencivil/projekt/fallnamen.py`, siehe [[Entwicklung]].
      Vorher hielt ein doppelter Name nur seine Platte oder Analyse an, und
      sie sagte es oben im Fenster. Die sechs Fenster der Spannung-Dehnung-Analysen teilen sich
      aber eine Namensliste: der Doppelgänger kann in einem Fenster stehen,
      das man nicht offen hat. Vorschlag: das Namensfeld weist einen
      vergebenen Namen ab und sagt, wo er steht. Entschieden (Benutzer,
      2026-11-19): so.
      Strenger noch ein leerer Name: die Oberfläche lässt ihn nicht zu, aus
      einer bearbeiteten Datei aber hält er beim Lesen das ganze Projekt an
      («Platte 'Decke über EG', kombinationen 1: 'name' darf nicht leer
      sein.»), statt nur seine Platte (Durchsicht vom 2026-11-19).
      Entschieden (Benutzer, 2026-11-19): nur seine Platte oder Analyse
      rechnet nicht und sagt am Ort, was fehlt. Erledigt (2026-11-19),
      siehe [[Entwicklung]].
- [x] **α_min über α_max schon am Feld abweisen.** Erledigt (2026-11-19):
      `bereich(..., bis_feld="alpha_max")`, siehe [[Entwicklung]]. Vorher
      nahm das Feld α_min = 50° bei α_max = 40° an; die Analyse oder Platte
      hielt an und sagte es oben im Fenster (`neigungen_ordnen`). Ein Feld, dessen Grenze
      ein anderes Feld ist, kennt der Katalog nicht: `bereich` hat nur feste
      Grenzen. Vorschlag: `bereich(..., hoechstens="alpha_max")`, daraus die
      Regel im Kern und die Grenze am Feld, an einer Stelle (Durchsicht vom
      2026-11-19). Entschieden (Benutzer, 2026-11-19): so.
- [ ] **Dichten aus SIA 261.** 2400 und 2500 kg/m³ für Beton und Stahlbeton,
      7850 kg/m³ für Stahl stehen so in SIA 261:2020, Anhang A, Tabelle 28
      (mit g = 10 m/s²); SIA 262 nennt keine. Ob der Verweis eingetragen wird,
      entscheidet der Benutzer – bis dahin «nach Vorgabe».
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
      einen Teil der Durchbiegung – was nach dem Einbau dazukommt, was die
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
      γ_g = 22 kN/m³ wird γ' 11 statt 12, gut 8 % kleiner – sicher, denn
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
      mehr erfüllt ist. Ein negatives σ_f gibt N_Rd = 0, die Formel zeigt es
      mit max[0; σ_f] (seit 2026-11-19). Bestätigt sind dagegen: b_γ mit tan φ (Tabelle
      9.2.18 lässt sich nur so nachrechnen) und die Partialfaktoren statt
      F_stat (SIA 267:2013, 5.3.2.1, 5.3.2.2, Tabelle 1).
- [ ] **Grundbruch und Gleiten, nicht gebaut** – SIA 267:2013 verlangt
      es, wo massgebend: die Ausmitte der Last mit der wirksamen Fläche
      A' = a'·b' (8.4.4.4, Figur 4; im Buch Kap. 9.2.11), bis dahin sagt
      die Hilfe, b und L als wirksame Masse einzugeben; das Kippen
      (8.5.3.6, (38)–(40)) und im Gebrauch die Ausmitte bis zur einfachen
      Kernweite (8.5.4.7); der Erdwiderstand vor dem Fundament (8.4.3,
      8.5.2.3, γ_M = 1.4) – ihn wegzulassen ist sicher; der Geländebruch
      (8.5.3.3, Kap. 14 der Norm); benachbarte Fundamente (8.4.4.3).
      Der Gleitkörper im Bild gilt für waagrechte Sohle und waagrechtes
      Gelände, wie die Formeln für L_Gl und H_Gl.
- [ ] **Setzung: die Startwerte einer neuen Berechnung.** Keine steht in
      einer Quelle. s_zul = 20 mm: die zulässige Setzung ist je Bauwerk
      festzulegen (SIA 267:2013, 8.5.4.1; Kap. 8.12), das Beispiel in
      Kap. 8.8 nimmt 2 cm. Δz_max = 0.5 m: das Buch schweigt, sein
      Beispiel teilt in 1 m. M'_E = 60 MN/m² bei M_E = 20: das Buch nimmt
      grob M'_E ≈ 8 bis 10 · M_E an (Kap. 5.3) – 3 · M_E ist weicher als
      jede Angabe. Wirkt nur, solange q_W > 0. Empfehlung: M'_E = 160
      (8 · M_E). Bestätigt: MN/m² statt kN/m² (nur die Anzeige, Tabelle
      8.4 trifft) und «starr» als Vorgabe (das Beispiel in Kap. 8.3 rechnet
      so). Entscheid des Benutzers.
- [ ] Setzung, nicht gebaut: Setzungsdifferenzen und Verkippung
      (Kap. 8.11 bis 8.13; SIA 267:2013, 8.5.1.2, 8.5.4.4), der zeitliche
      Verlauf (Konsolidation; 8.5.4.3), die Einflusstiefe als Abbruch
      (Kap. 8.4) – gerechnet wird bis zur untersten Schicht, und unter der
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
- [ ] Keine Testumgebung für die Zeichenhilfen des Balkensystems
      (`bs_symbole.js`, die verbundene Zeichnung in `cad_modell.js`) –
      geprüft von Hand im Browser.

## Entschieden: Durchsicht der Fenster vom 2026-11-19

Was die Durchsicht «Die Bedienung erklärt sich selbst» gefunden, aber nicht
von sich aus entschieden hat. Der Benutzer hat am 2026-11-19 bei jedem Punkt
die Empfehlung gewählt, bei den Bildern alle Gruppen. Ein Punkt wird
abgehakt, wenn er gebaut ist. Was die Durchsicht selbst behoben hat, steht
in [[Entwicklung]] (Schritte 1 bis 13 und der Nachtrag zur Karte
«Schubfluss»).

- [x] **Ein fehlendes Material: grau oder rot?** Die Querschnittsanalyse
      zeigt «Linie 1: das Material … gibt es nicht mehr – eines wählen.»
      grau, weil nur etwas fehlt. Decke und Balkensystem zeigen denselben
      Satz rot, und die ganze Decke bzw. das ganze System rechnet nicht:
      dort hält eine Meldung die Rechnung nur an, wenn sie ein Fehler ist
      (`Meldung.fehler` heisst beides). Empfehlung: grau für ein fehlendes
      oder gelöschtes Material, rot nur für die falsche Art (ein Stahl als
      Beton); dafür «hält an» und «ist falsch» trennen.
- [x] **Die Meldung nennt die interne Kennung.** «das Material 'b9' gibt es
      nicht mehr»: 'b9' sieht der Benutzer nirgends, die Listen zeigen
      Namen. Empfehlung: «das gewählte Material gibt es nicht mehr – eines
      wählen.» Der Satz steht an einer Stelle (`materialgrund` in
      `opencivil/projekt/aufbau/kern.py`).
- [x] **«erfüllt, ∞» ohne Last.** Ein frisches Durchstanzen (V_d = 0) und
      eine frische Setzung (ohne Last, s = 0) stehen in der Zusammenfassung
      als «erfüllt» mit dem Grad ∞. Die Querschnittsanalyse sagt in
      derselben Lage «Keine Einwirkung → kein Nachweis.». Empfehlung:
      dasselbe hier; der Satz käme dann an eine
      Stelle für alle Nachweise (heute `OHNE_EINWIRKUNG` in
      `opencivil/nachweis/schiefe_biegung.py`).
- [x] **Durchstanzen: der Schalter Decke ↔ Bodenplatte lässt die Zahlen
      stehen.** c, c_v, q_d und die Biegebewehrung behalten ihren Wert, nur
      die Beschriftung wechselt: etwa q_d = 10 kN/m² «Eigengewicht und
      Nutzlast» heisst danach «Bodenpressung». Jede Zahl behält ihre Rolle im
      Nachweis, und 10 kN/m² als Bodenpressung liegt auf der sicheren
      Seite, ist aber kaum gemeint. Die Vorgaben sind für beide Arten
      dieselben, «die Vorgabe der neuen Art» gibt es also nicht. Empfehlung:
      die Zahlen lassen und nach dem Umschalten am Schalter sagen, was
      jetzt für die andere Seite gilt – «c, c_v, q_d und die
      Biegebewehrung gelten jetzt für die Bodenplatte: prüfen». Sonst: alles
      auf die Vorgaben zurück.
- [x] **Bilder an Schaltern**, wo Wörter nicht reichen (`wahlSchalter` kann
      Bilder zeigen), das stärkste zuerst. Entschieden (Benutzer,
      2026-11-19): alle. Erledigt am 2026-11-19, alle Gruppen, siehe
      [[Entwicklung]].
      - Durchstanzen «Lage» (`durchstanzen.js`): wo der Plattenrand liegt,
        steht heute erst in der Hilfe – je Stellung die Stütze mit dem Rand;
      - Pfahl «Kopf frei / eingespannt» und «Tragglied Rohr / Stab»;
      - Durchstanzen «Form»; Setzung «starr / schlaff» (Setzung im Punkt K
        oder in der Mitte);
      - Platte «ungünstig / günstig» (zwei Stäbe, oben bzw. unten bündig),
        «Zug oben / unten» im Verformungsfall, «Einlage, grösstes Mass»;
      - Querschnittsanalyse: die Linienart (verschmiert, Anzahl, Teilung),
        Start- und Endeisen; «nur einachsig» als Schalter mit zwei Bildern,
        Nulllinie waagrecht oder schief, statt Häkchen und Satz.
- [x] **Häkchen statt Schalter**: «überschreiben» beim eigenen Material
      (`material.js`) und «mit Bewehrung», «mit Schubwänden» in der Vorlage
      der Querschnittsanalyse (`qa_vorlagen.js`). Sonst ist jede feste Wahl
      ein Schalter. Empfehlung: Schalter.
- [x] **Zwei Striche in sichtbaren Texten**: Meldungen und Hinweise
      schreiben teils «--» («noch keine Kombination – unter «Einwirkungen»
      eine anlegen»), teils «–». Empfehlung: in allem, was der Benutzer
      liest, «–»; im Code darf «--» bleiben.

## Umbau: Befunde der Strukturdurchsicht vom 2026-11-19

Neun Durchsichten über das ganze Repo – Fundament und Ausgabe;
Querschnitt, Spannungsanalyse und Suche; Nachweise; Balkensystem und
Decke; Durchstanzen, Pfahl und Boden; Projekt und Dienst; die Apps mit
Zeichenfenster; die übrigen Fachfenster und Bilder; Rahmen und Stilblatt.
Die tragenden Punkte sind am Code nachgeprüft. Urteil: gutheissen mit
Änderungen. Das Fundament trägt (ein Rechenwerk, ein Weg zur Formel samt
Herleitung, `Art` im Balkensystem, `achsenkreuz`, der Steckbrief
`BAUTEILE` mit seinen Wächtern, kein Code mehr für alte Speicherstände).
Die Kosten liegen an drei Stellen, die durch alle Bereiche gehen: Zahl und
Herleitung kommen an einigen Stellen aus getrennten Rechnungen (1); die
Beschreibung eines Feldes steht nur halb im Katalog, den Rest schreibt die
Oberfläche ab (2); die Platte rechnet als Sonderfall neben dem gezeichneten
Querschnitt (3, 4). Empfohlene Reihenfolge: 1 und 6 (klein, still falsch
oder still leer), 7 (aus der Arbeit vom 2026-11-19), 2 vor der nächsten
Maske, 5 mit der Querschnittsanalyse in der Durchsicht der Fenster; 3 und
4 sind der grosse Umbau. Entschieden (Benutzer, 2026-11-19): alles, in der
empfohlenen Reihenfolge, 3 und 4 nach den kleinen.

- [x] **1. Zahl und Herleitung aus getrennten Rechnungen.** Erledigt
      (2026-11-20), alle fünf Stellen. Wo eine Zahl
      stumm gerechnet und daneben für die Herleitung ein zweites Mal
      zusammengestellt wird, kann der Bericht eine Rechnung zeigen, mit der
      nicht gerechnet ist.
      - Erledigt (2026-11-19): Grundbruch, die Formel in vier Formen. Jetzt
        `Spalte(N, s, d, g, b)` mit `produkt()` und `vorlage()`; `z`,
        `_produkt` und `Faktoren` sind weg, d_γ ist ein Wert.
      - Erledigt (2026-11-20): Durchstanzen, k_e. Die Wahl Näherung oder
        (57) stand viermal; jetzt `KeRegel` mit `KeNaeherung` und
        `KeExzentrizitaet` in `pruefung.py`, einmal gebaut in `pruefe`.
        `Schnittpruefung.k_e` fragt sie, `herleitung.k_e` schreibt nur.
      - Erledigt (2026-11-20): Kennzahlen der Platte. Der Querkraftnachweis
        löst seine Eingänge (`kurvenbeiwerte`, `buegelwerte`) und rechnet je
        Zugseite (`Kurvenbeiwerte.widerstand`, `Buegelwerte.suche`); Fall,
        Kurve, Bild und Kennzahl rufen dieselbe Rechnung. Die Kennzahlen lesen
        `bezuege_ohne_faelle` statt alle Eingänge mit einem Filter auf `m_Rd_`
        und wählen den Ansatz einmal.
      - Erledigt (2026-11-20): Decke. `traeger.statik` rechnet über
        `ebener_verlauf(…, EI=∞)`, ihre Stücke sind `EbenesIntervall`;
        `Stueck` und `traeger.extreme` sind weg. `vorderste_extreme` steht
        in `verlauf.py` und ist die Regel von `extremwerte`, für Stäbe und
        Decke, ebenso über alle Stäbe (`grenzwerte`, `massgebender` statt
        `nach_betrag`) – das erledigt Punkt 10 vom 2026-11-15.
      - Erledigt (2026-11-20): Knicken und Kennzahlen. Ob sie die Linie der
        Tragsicherheit teilen, entscheidet die `Linienquelle` neben
        `resistenzlinie`; Eingänge, Befund und Linie folgen ihr. Die
        Gleichheit ist `Rechenwahl.gleiche_linie` und vergleicht den Modul,
        wo ein Gesetz an ihm hängt.
- [ ] **2. Die Beschreibung eines Feldes steht nur halb im Katalog.**
      Wo ein Feld seinen `bereich` hat, ist der Katalog die eine Quelle für
      Einheit, Grenze und Satz. Daneben:
      - Erledigt (2026-11-20): jedes Zahlfeld hat seinen `bereich` oder ist
        eine Wahl, `TestJedesZahlfeld` wacht darüber; die Masken nehmen die
        Grenzen aus dem Katalog statt eigener `min`. Weg sind
        `PostenEintrag.regeln`, `QuerkraftbewehrungEintrag.regeln`, beide
        `EINHEIT_DER_FEDER` und `federeinheiten`; Platte, Knicken und
        Querschnittsanalyse nehmen die Einheit vom Feld (`als_groesse`).
        Ohne Einheit am Feld bleibt der Wert einer Last im Balkensystem:
        seine hängt an der Art (`EINHEIT_DER_LAST`). Die Masse der Vorlagen
        und die Kennwerte von Hand sind Zuordnungen, keine Felder – sie
        gehören zum letzten Punkt hier. Die Prüfungen in `Zeichnung._stab`,
        `_linie` und `_wand` bleiben: das Zeichenfenster liest die Elemente
        ohne die Prüfung der Felder, und eine Teilung null teilte dort
        durch null.
      - Vier Masken schreiben die Eingabetabellen des Kerns ab
        (`durchstanzen.js` `MASSE` und `ROTATION`, `grundbruch.js`,
        `setzung.js`, `pfahl.js`): Gruppen, Reihenfolge, Zeichen,
        Normstellen. `ROTATION.filter(([k]) => felder.has(k))` verschluckt
        ein neues Feld des Kerns still, bei Grundbruch und Setzung erscheint
        es nie. Die Zeichen laufen schon auseinander (k_δ im Kern, δ_k/φ_k in
        `grundbruch.js`), a_x hat drei Namen. Umbau: der Katalog liefert je
        Art die Gruppen `{titel, felder: [{feld, zeichen, beschreibung,
        referenz}]}` aus denselben Tabellen, ein Baustein
        `eingabekarten(art, eintrag, gelesen)` baut die Karten. Entschieden
        (Benutzer, 2026-11-19): die Masken holen Felder und Zeichen aus dem
        Kern; das ersetzt «Das Zeichen bleibt in der Maske» vom 2026-10-16.
        Wo Kern und Maske heute verschieden schreiben, bekommt der Benutzer
        die Liste. Erweitert Punkt 3c vom 2026-11-15. Erledigt für den
        Grundbruch (2026-11-20): die Tafel steht in `fundament.VORGABEN`
        (Bausteine `opencivil/core/vorgaben.py`), mit der kurzen Beschriftung
        der Maske neben der Beschreibung; `eingabekarten` baut die Karten,
        `tests/test_vorgaben.py` vergleicht Maske und Herleitung. Erledigt
        für die Setzung (2026-11-20): `setzung.VORGABEN` und `JE_SCHICHT`,
        die Schichten je mit ihrer Nummer (`Feld.nummeriert`); auch die
        Spalten der Schichten kommen aus dem Kern. Erledigt für den Pfahl
        (2026-11-20): `pfahl.VORGABEN` und `JE_SCHICHT`; der Spitzendruck hat
        eine eigene Gruppe «Fuss», damit sein Schalter vor ihm steht, und
        `Pfahlschicht.kurznamen` ist weg. Erledigt für das Durchstanzen
        (2026-11-20): `stelle.VORGABEN`; die Maske verteilt die Gruppen auf
        ihre Tafeln (`eingabegruppen`) und meldet eine, die keinen Platz hat.
        `MASSE` und `ROTATION` sind weg, a_x heisst überall «vom linken
        (Platten)rand». Damit erledigt. Seit 2026-11-26 wird jede Gruppe
        eine Kachel (`gruppenkapitel` in `kapitel.js`); `eingabekarten` ist
        weg.
      - Bilder tippen Einheiten: `GROESSEN` in `pf_verlauf.js` spiegelt
        `VERLAEUFE` samt Grenzschlüsseln (eine umbenannte Grösse
        verschwindet still), `platte_bilder.js` rund 35 Einheiten, die
        Pfahlskizze kN/m² neben kPa in der Maske. Umbau: die Grössen
        (`Anzeigegroesse`) kommen mit den Daten. Erledigt (2026-11-20):
        Verläufe, Diagramme der Platte und Pfahlskizze nehmen Zeichen,
        Einheit und Stellen aus den Daten (`achsentitel`, `masszahl` in
        `achsen.js`), die Skizze die Kennwerte der Schichten aus dem Feld.
        Noch selbst geschrieben, heute gleich wie im Kern: `GROESSE` in
        `qa_diagramme.js` (N, M_y, M_z), die Achsen von `spannungsbild.js`
        (ε, σ, z) und die Kennwerte in den Skizzen von Grundbruch und
        Setzung – derselbe Schritt, falls gewünscht. Der Hinweis «unter Zug
        mindestens 40°» unter der Neigungskurve steht als Text im JS.
      - Knotenlasten: Art und Einheit von Hand, mit widersprüchlichen
        Rückfällen (`lastFelder` kNm für alles ausser «kraft», Zeichnung
        und Liste kN für alles ausser «moment»). Erledigt (2026-11-20): die
        Art ist eine Wahl im Kern (`Knotenlastart`), mit der Einheit
        derselben Last auf einem Stab; der Katalog gibt `knotenlastarten`
        wie die Stablasten, und Feld, Liste, Titel und Zeichnung lesen dort.
      - Dieselbe Grenze hinter dem Feld noch einmal. Erledigt (2026-11-20):
        `streifen.pruefen` (acht Prüfungen, die nie griffen), die Teilungen
        im Dienst der Suche, `katalog.duktilitaet`; eine Liste von Zahlen
        mit Bereich ist nie leer, das sagt ihr Feld. Der `Bereich` steht
        jetzt im Kern (`opencivil/core/bereich.py`): ein `Mass` für beide
        Arten von Vorlagen samt Achsabstand, die Kennwerte von Hand und
        jedes Feld prüfen mit ihm und geben der Maske dieselbe Angabe.
- [x] **3. «Welche Seite zieht» in fünf Formen.** Erledigt (2026-11-20):
      `Zugseite` ist die einzige Form. Die Lage der Platte sagt ihre Seite
      an einer Stelle (`Bewehrungslage.seite`), die Stahllage trägt sie
      (`Stahllage.seite`), `je_seite`, `zugposten`, `statische_hoehen` und
      die Kurvenbeiwerte der Querkraft gehen nach ihr. «Ein positives
      Moment zieht unten» steht nur in `Zugseite.aus_moment`, das
      Vorzeichen in `Zugseite.vorzeichen`. Bewusst geblieben: `positiv` an
      der Resistenzlinie (`kante`, `moment_bei`) ist ein Vorzeichen auf
      einer Achse, auch der Normalkraft, keine Seite; die Bewehrungssuche
      fragt nach der Tragrichtung x oder y, nicht nach der Seite. Siehe
      [[Entwicklung]].
- [ ] **4. Die Platte rechnet sich als Rechteck ein zweites Mal.** Zum
      grössten Teil erledigt (2026-11-20).
      - Erledigt (2026-11-20): die Platte baut ihren Querschnitt als
        `interaktion.Querschnitt` (`Gesetze.querschnitt`: Rechteck b×h, je
        Lage ein Stab), ihre Löser und die genaue Linie rechnen damit, und
        ihre Grenzen heissen wie beim gezeichneten Querschnitt. Weg sind
        `dehnungsfaecher.py`, `plattenfasern` und `Querschnittsloeser`.
        Siehe [[Entwicklung]].
      - Erledigt (2026-11-21): der Riss der Spannung-Dehnung-Analyse an
        einer Stelle (`spannungsanalyse/riss.py`, `Bruttoriss`), vom
        Benutzer gewählt. Die Platte reisst am Rechteck b×h als
        Bruttoquerschnitt, wie der gezeichnete Querschnitt:
        `M_Riss(N) = (f_ct,eff − N/A)·W` statt `M_Riss − N·h/6`; unter Zug
        t = h, am gezeichneten Querschnitt t = min(h; b). Dieselben Zahlen
        (vorher und nachher verglichen), nur die Herleitung der Platte ist
        neu; die des gezeichneten Querschnitts steht Wort für Wort wie
        vorher. Siehe [[Entwicklung]].
      - Offen: die Nachweise der Platte (sprödes Versagen, Zwängung auf
        Biegung) rechnen ihr Rissmoment weiter mit `rissmoment_rechteck`,
        die des gezeichneten Querschnitts am Bruttoquerschnitt – dieselben
        Zahlen, zwei Herleitungen. Und es bleiben zwei Paare,
        `Loeserpaar` und `Schnittpaar`: sie unterscheiden sich noch in der
        Tiefe (bei der Platte ein Wert, beim gezeichneten Querschnitt aus
        der Zeichnung), in der Dehnung am Ende und darin, dass die
        Nulllinie der Platte nie kippt.
      - Offen, verwandt, je ein eigener Umbau:
        - Erledigt (2026-11-21): Platte und Analyse teilen, was gleich ist
          – den Anfang der Knicknachweise (`Knickverfahren.__init__`),
          Thema und Namen der Rissnormalkraft (`Normalzwang`), Anlegen und
          Belegen der Kennzahlen (`Kennzahlprozedur`, auch für den Pfahl).
          Siehe [[Entwicklung]].
        - Erledigt (2026-11-21): das Fachwerk an einer Stelle.
          `fachwerk.py` besitzt die Druckfeldregeln (`ALPHA_MIN`,
          `ALPHA_MAX`, `ALPHA_ZUG`, `K_C`, `druckfeldgrenzen`) und die
          Suche `guenstigste(…)`; die Bügel der Platte, die Schubwände und
          die Wendel des Pfahls rufen sie. `Wandwiderstand` ist weg, eine
          Wand gibt einen `Buegelpunkt`. Siehe [[Entwicklung]].
        - Erledigt (2026-11-21): ein Urteil je Teil. `Fallausgang` führt
          Ausgang und Begründung; `Teilnachweis.je_teil` hat die Schleife
          einmal – für die Lagen der Platte, die Seiten des gezeichneten
          Querschnitts (`Richtungsnachweis`), die Fälle von Knicken,
          Spannungsbegrenzung, Verformung und Querkraft und die
          Kombinationen des Fundaments. Eigene Schleifen behalten mit
          Absicht: die Biegung mit Normalkraft (ihr Befund sammelt
          Auswertungen und je Fall M_Rd), die schiefe Biegung und die
          Schubwand (auch ein übersprungener Fall gibt Werte aus), der
          Pfahl quer und innen quer und das Erdbeben (mehrere Urteile je
          Fall) und die fehlende Bewehrung (sie rechnet nichts, jedes
          Urteil hat seine eigene Art). Siehe [[Entwicklung]].
- [x] **5. Nach dem Klick baut jede App mit Zeichenfenster selbst.**
      Erledigt (2026-11-20): `cad_app.js` fragt den Kern, baut die Liste
      unter der Zeichnung und das schwebende Fenster zur Auswahl für alle
      vier Apps mit Zeichenfenster, das Durchstanzen eingeschlossen; was
      ein Klick wählt, sagt `waehlbarVon` an einer Stelle. Siehe
      [[Entwicklung]].
- [x] **6. Still leer statt laut.** Erledigt (2026-11-20), alle fünf
      Stellen.
      - Erledigt (2026-11-20): `sinnbild` wirft für einen unbekannten
        Namen; «Ergebnisse» der Decke hat sein Bild, und der Test findet
        auch die Kapitel und die Knöpfe des Zeichenfensters.
      - Erledigt (2026-11-20): «⇒ erfüllt» steht immer hinter dem Grad;
        der Schalter `mit_urteil` ist weg, «Sprödes Versagen je Richtung»
        hat sein Urteil.
      - Erledigt (2026-11-20): eine Diagrammkarte nennt ihr Bild
        (`karte(titel, inhalt, {bild})`, gelesen mit `bildDer`); der
        Bericht sucht kein SVG mehr in der ganzen Karte.
      - Erledigt (2026-11-20): kein «Anlass» mehr. Ob gerechnet wird, sagt
        `rechnet: false` in der Zeile der App (die Skripte); «nur die Mitte
        neu zeichnen» ist `mitteAendern`.
      - Erledigt (2026-11-20): `nurStriche` wirkt; ohne `plt.grid()` steht
        kein Gitter, nur Striche am Rand, wie bei matplotlib.
- [x] **7. Aus der Arbeit vom 2026-11-19.** Erledigt (2026-11-20), alle
      vier Punkte.
      - Erledigt (2026-11-20): die Normalkraft der M-V-Kurve ist ein Feld
        der Platte, `querkraftkurve_normalkraft`, gespeichert mit dem
        Projekt; das Bild liest es über `Bauteil.eintrag`. Weg sind `n_ed`,
        die Anfrage `querkraftkurven`, `_normalkraefte`,
        `kurvenNormalkraft` und der Wächter gegen überholte Antworten.
      - Erledigt (2026-11-20): «unfertig» entsteht auf einem Weg. Ein
        `ProjektFehler` trägt Grund und Ort getrennt (`wo=`), jede
        Baufunktion wirft, auch was nur fehlt, und `aufbauen` nimmt
        `fehler.grund_bei(wo)`. Weg sind `ohne_ort` und das `Optional` der
        Baufunktionen; was dem Pfahl an Boden fehlt, steht bei seinen
        Regeln. Eine Querschnittsanalyse heisst in jeder Meldung so, nie mehr
        «Querschnitt». Der Ort in den Worten der Maske, offen seit
        2026-10-16, ist erledigt (2026-11-20): ein Element ohne Namen heisst
        mit dem Wort seiner Klasse und seiner Nummer (`IM_ORT`: «Lage 2»,
        «Linie 3»), sonst mit seiner Kennung («A1»). Seit 2026-11-21 auch
        jedes Feld und jede Liste: «Lage 2, Grund» statt «Lage 2, grund»,
        «Kombination 'K'» statt «kombinationen 'K'», siehe [[Entwicklung]].
      - Erledigt (2026-11-20): der Stabquerschnitt hat je Art ein eigenes
        Feld – `masse`, `kennwerte`, `profil`, `platte`, `analyse` –, und
        umschalten ist `setzen('art')`. Nach dem Zurückschalten stehen die
        alten Zahlen wieder da (Benutzer, 2026-11-19), auch die Wahl E₀ oder
        E_eq: bei einer Form wartet sie, statt dass der Querschnitt nicht
        rechnet.
      - Erledigt (2026-11-20): `tests/test_balkensystem.py` (1146 Zeilen)
        ist geteilt – Querschnitte und Materialien stehen in
        `test_balkensystem_querschnitte.py` –, ebenso `test_nachweis_mn.py`
        (1006): der Plattenquerschnitt steht in `test_plattenquerschnitt.py`.
        Eine Naht Ebene/Raum gab es in beiden nicht. Den Träger und die
        Platten der Tests haben `tests/traeger.py` und `tests/platten.py`.
- [x] **8. Dateien nahe oder über 1000 Zeilen.** Erledigt (2026-11-20).
      - Erledigt (2026-11-20): `tests/test_querschnittsanalyse.py`, 1076
        Zeilen – die Vorlagen, die leere Analyse und die verschmierten
        Stäbe stehen in `test_qa_vorlagen.py`; 819 Zeilen bleiben.
      - Erledigt (2026-11-20): `stil.css`, 2597 Zeilen, steht in neun
        Blättern unter `web/css/`, nach Bausteinen statt je App (Grundlage,
        Seite, Eingaben, Berechnung, schmale Geräte, Zeichenfenster,
        Notizbuch, Skizzen, Python). Geschnitten an den Abschnitten, die es
        schon gab: keine Regel hat ihren Platz gewechselt, die Brücke bindet
        die Blätter in der Reihenfolge ihrer Nummern ein. Fünf Regeln
        `[hidden]` sind eine, die 25 Farbregeln der Verläufe eine Variable je
        Grösse (`--verlauf`), fünf Klassen für leere Listen eine
        (`.leer-zeile`); das «…» der Vorschau bleibt, es ist ein Platzhalter.
      - Erledigt (2026-11-19): `grundbruch.py`, 996 Zeilen, ist geteilt in
        `fundament.py` mit dem gemeinsamen `Fundamentnachweis`,
        `grundbruch.py` (639 Zeilen), `gleiten.py` und `tragfaehigkeit.py`.
      - Erledigt (2026-11-20): `platte_bilder.js`, 936 Zeilen – der
        Bemessungspunkt, das Farbpaar erfüllt/nicht erfüllt und die Legende
        stehen als `bemessungspunkt`, `urteilsfarbe` und `legende` in
        `achsen.js`, für alle Bilder; `platte_bilder.js` hat noch 873.
      - Erledigt (2026-11-20): `interaktion.py`, 922 Zeilen – die Fläche
        der Widerstände, die nur ein Bild liest, steht in
        `querschnitt/widerstandsflaeche.py`; `interaktion.py` hat noch 815.
      - Erledigt (2026-11-20): `eintraege.py`, 910 Zeilen – Posten, Lage,
        Obergrenze und Bügel, die nur die Platte braucht, stehen in
        `projekt/platte.py`; `eintraege.py` hat noch 750.
- [ ] **9. Kleiner.**
      - Drainiert und undrainiert: im Pfahl ein Schalter, zwölfmal
        abgefragt; im Grundbruch heisst φ = 0 undrainiert. Der Erdwiderstand
        vor dem Fundament bräuchte eine dritte Form. Umbau: `Drainiert(φ, c)`
        und `Undrainiert(s_u)` als Typen. Entschieden (Benutzer, 2026-11-19):
        der Grundbruch bekommt den Schalter des Pfahls, «drainiert» mit φ
        und c, «undrainiert» mit s_u. Erledigt (2026-11-19), siehe
        [[Entwicklung]]; die Typen bleiben offen.
      - Durchstanzen: der `Ort` der Leisten führt fünf Werte der Herleitung
        als `None`; `_leisten_schreiben` hat 150 Zeilen.
      - Der Bericht baut die Angaben der Platte selbst; die Schreibweise
        einer Lage steht dreimal (`menge_text`, `zusammenfassung.py`,
        `lagenaufbau.py`).
      - Was eine Art des Balkensystems zeigt (Achsen, Zeichen, Einheiten),
        steht in acht Tabellen der Herleitungen und in `EBEN`/`RAUM` von
        Hand. Welches I die Ebene nimmt, entscheiden drei Mechanismen.
      - Was auf null rundet, hat kein Vorzeichen – in `fest` und
        `einheiten.py`, nicht in `zusammenfassung._groesse` und
        `Kennzahl.text` («-0.0»). Zwei Markdown-Maskierungen
        (`bibliothek._maskieren`, `bericht/markdown.text_markdown`).
      - Schalter fünfmal gebaut (`richtungsWahl` hat einen Nutzer und eine
        tote Stellung «beide»); `zahlfeld` und `namensfeld` weisen mit zwei
        Wortlauten ab.
      - Versalien über Formelzeichen: 12-mal `uppercase`, 11-mal wieder
        aufgehoben, 14-mal `ist-wortlaut`. Entschieden (Benutzer,
        2026-11-19): Schalter ohne Versalien.
      - In den Zeilen von `apps.js` steht Ableitbares doppelt (`fehlt` neben
        `braucht`, `einrichten` dreimal gleich).
      - Ungenutzt: `betonstahl_frei`; nur in Tests: `beton_frei`,
        `formeln_sammeln` und `Formeleintrag`; der Alias `text_maskieren`.
      - Erledigt (2026-11-19): `naechsteKennung` vergab die
        grösste plus eins – LK3 löschen, die nächste hiess wieder LK3, und
        eine Diagrammzeile, die auf die gelöschte zeigte, zeigte still die
        neue. Dieselbe Regel in `cad_modell.js` 144. Entschieden (Benutzer,
        2026-11-19): eine Kennung wird nie wieder vergeben, und wer auf eine
        gelöschte zeigt, sagt es am Ort. Siehe [[Entwicklung]].

**Stand früherer Befunde:**
- Gewachsen: «Name oder Sorte» (18 Stellen, die Materialliste wird an 7
  Orten gebaut); Kern-Wissen in Hilfetexten; Proben gerade verbinden (neu
  `dk_schnitt.js` 127); der Adapter des Zeichenfensters (das Werkzeug
  «Schnitt» der Decke brauchte sieben Einträge in zwei Dateien); `schnell`
  (fünf Verhalten, zwei Nutzer); «Welche Seite x-Bewehrung hat» (siehe 3);
  «Teilung oder Stabzahl» (eine Kopie im Bericht); `systemart(` 13 Aufrufe.
- Geschrumpft oder erledigt: «Einheiten nicht an jedem Feld» (es bleiben
  Schnittgrössen, Lasten, Koordinaten, Federn); die Masken von Verformung
  und Knicken lesen `feldangabe`; Karten und Übersichten des Berichts hängen
  an der Zeile der App; eine fehlende Bauteilart meldet sich beim Laden;
  `querschnittsloeser.py` 914 → 827 Zeilen; `linie._grenze` ist weg (von
  Hand halbiert wird noch an vier Stellen); Punkt 4c vom 2026-11-15 («quer»
  am Knoten).
- Unverändert: 2, 3d, 4a, 4b (43 Stellen), 5, 6, 8, 9 und 10 vom
  2026-11-15; die Varianten im Kern; die dritte Zusammenfassung der
  Konsole; «Kennung statt Name»; `namensraum` und `mitIndex` im JS.

## Umbau: Befunde der Strukturdurchsicht vom 2026-11-15

Drei Durchsichten: der Rechenkern der Balkensysteme in 2D und 3D, die
Pfähle, die Oberfläche beider Balkensysteme – jeder Punkt am Code
nachgeprüft. Urteil: umbauen, bevor weiter darauf gebaut wird. Gerechnet
wird richtig, aber den gebetteten Stab lösen drei Programme, und Regeln des
Kerns stehen ein zweites Mal im JS. Empfohlene Reihenfolge: 1, dann 3a und
3b, dann 2 – vor Knicken oder 2. Ordnung am Pfahl; der Rest, wenn dort
ohnehin gearbeitet wird. Die Punkte 1, 3a und 3b und der kleine Umbau aus
Punkt 2 sind erledigt (unten unter «Erledigt zuletzt»); von Punkt 2 bleibt
der grosse.

- [ ] **2. Rest: der Pfahl liest am Raster ab und baut sein System
      selbst.** Seit dem kleinen Umbau rechnet er mit den Elementen und dem
      Verlauf des Balkensystems, nummeriert und baut aber selbst zusammen.
      Seine Nachweise lesen M, V und den Bodendruck an den Knoten ab; darum
      teilen Pfahl und Balkensystem gebettete Stäbe in Stücke von 1/(5β),
      wo für die Lösung 1/(2β) genügte. Kosten: Knicken oder 2. Ordnung am Pfahl zweimal
      zusammenbauen; rund 15 % Rechenzeit im Balkensystem. Umbau, gross:
      der Pfahl als lotrechter Stab eines ebenen Systems – dann fände er
      seine grössten Werte genau wie das Balkensystem, und beide könnten
      wieder gröber teilen.
- [ ] **3c. Die Eingabe der Pfähle entscheidet selbst, welche Felder
      gelten** – drainiert, Mantel eingegeben, Bohrpfahl, Kopf frei –,
      obwohl der Kern es weiss (`Pfahlschicht.kurznamen`, die Gruppen in
      `pfahl.py`); Durchstanzen und Spannungsanalyse holen das schon aus dem
      Kern. Die Texte laufen auseinander: «Durchmesser der Längsstäbe» im
      Kern, «Durchmesser der Stäbe» im JS. Umbau: `pfahldaten` liefert je
      Pfahl die Felder, die gelten.
- [ ] **3d. Von Hand abgeschrieben:** `HALT` in `bs_eigenschaften.js` (der
      Katalog schickt `halt`, und niemand liest es), die Vorgabe einer neuen
      Last (`vorgabenNeu`), die Vorsilben L, A und P, das Vorzeichenbild im
      Raum mit den Zahlen der Startansicht (`bs_texte.js` gegen `ANSICHTEN`
      in `cad_raum.js`).
- [ ] **4a. Die Pfahlart als Weiche:** rund 30 Abfragen im Kern, einige im
      JS; `Masse` hat Nullen als Vorgabe, «je Pfahlart ein Teil davon», und
      `innen.querschnitt` erkennt den Bohrpfahl an der Zahl der Werkstoffe.
      Umbau: ein Pfahlquerschnitt mit zwei Formen, einmal gebaut, mit EA,
      EI, Interaktion, Schub, Feldern und Bild.
- [ ] **4b. «Im Raum?» gut zwei Dutzend Mal gefragt,** in vier Formen
      (`a.bs.raum`, `a.raum`, `v.basis`, die Zahl der Achsen);
      `cad_fenster.js` hatte vor der 3D-App keine solche Frage, jetzt
      sechs. `systemart` sucht die Art zwölfmal in allen Listen, obwohl
      `apps.js` sie kennt. Umbau: je Art ein Objekt, einmal gebaut, an
      `a.bs`; die Ansicht als Objekt, eben in `cad_ansicht.js`, im Raum in
      `cad_raum.js`; die Ebene immer mit Basis statt `null`.
- [ ] **4c. Still umgedeutet:** eine Last «quer» aus der Palette wird an
      einem Knoten senkrecht (`bs_zeichnung.js` 281); die massgebende Tiefe
      quer fällt ohne Stelle auf den Kopf zurück (`pfahl/quer.py` 318).
- [ ] **5. Feste Zahlen in den Herleitungen der Pfähle.** 0.42, 4.5,
      γ_E = 1.5, b' = 3·D und γ_M,a = 1.4 stehen als Text in den Formeln
      (`steifigkeit.py` 318, 357, 433; `quer.py` 181, 236), obwohl es die
      Konstanten gibt; die Hilfe in `pfahl.js` wiederholt sie. Wird γ_E eine
      Eingabe, zeigte die Herleitung 1.5 und rechnete mit etwas anderem.
      Umbau: Platzhalter oder `fest()`, wie schon in `innen_quer.py`.
- [ ] **6. Doppelte Bausteine.** Die Schichten des Pfahls zweimal
      (`boden.Profil`, `steifigkeit.Baugrund`), `lagen` zeichengleich in
      `pf_zeichnung.js` und `sz_zeichnung.js`; `lagerSymbol` und
      `raumlagerSymbol` mit gleichen Teilen. Die Anbindung an den Kern steht
      seit 2026-11-20 einmal (`kernFragen` in `cad_app.js`).
- [ ] **7. `cad_fenster.js` hat 899 Zeilen**, 101 bis zur Grenze. Nähte:
      die Aktionen der Auswahl nach `cad_auswahl.js` – dann fällt der Haken
      `a.aktionen` weg –, die Bedienung im Raum in die Ansicht aus 4b, die
      Eingabe mit Maus und Tasten (rund 260 Zeilen) in eine eigene Datei.
- [ ] **8. Klein.** `stahlprofile/formen.py` schreibt `_flaeche`, `_iy`, `_iz`
      und `_it` aus `querschnitte.py` ab, nur in cm, obwohl `_in_cm` genau
      das tut. (`nur_drehung` und `transponiert_mal` sind mit Punkt 1
      weggefallen.)
- [ ] **9. Die Geometrie des Raums gehört jetzt beiden Arten.** Seit Punkt
      1 rechnet auch die Ebene mit `stabwerk3d/raum.py` und
      `stabwerk3d/stab.py`, und `stabwerk/stab.py` ist nur noch der ebene
      Teil, aus dem der Stab im Raum besteht. Die Pakete trennen damit nicht
      mehr Ebene und Raum. Umbau, wenn dort ohnehin gearbeitet wird: beide
      Dateien nach `stabwerk/`, `stabwerk3d/` behält Modell, Rechnung und
      Herleitung des 3D-Balkensystems.
- [x] **10. Extremwert null an zufälliger Stelle.** Erledigt
      (2026-11-20) mit Punkt 1 vom 2026-11-19: `extremwerte` nimmt bei
      gleichen Werten die vorderste Stelle. Ist die Durchbiegung
      eines Stabs überall null – etwa bei einem, der nur Normalkraft trägt –,
      nennt die Tabelle der Extremwerte für 0.00 mm eine Stelle x, die nur
      vom Rundungsrauschen abhängt; seit Punkt 1 an sechs Stellen der
      Beispiele eine andere als vorher. Umbau: Werte, die sich bis auf
      Rundung gleichen, nehmen die erste Stelle.

## Umbau: Befunde der Strukturdurchsicht vom 2026-11-09

Vier Durchsichten über das ganze Repo (Rechenkern; Projekt, Dienst und
Fachmodule; Oberfläche; Durchstanzen), jeder Punkt am Code nachgeprüft.
Urteil: gutheissen mit Änderungen. Im Kern ist nichts verheddert, und die
Schichten sind sauber. Vor der nächsten Bauteilart und vor dem nächsten
Schritt beim Durchstanzen braucht es aber einen Umbau: drei Muster stehen
schon dreifach da. 1 und 2 sind am 2026-11-09 erledigt, 3 bis 12 am
2026-11-10 (siehe [[Entwicklung]]). Offen ist nur, was darunter steht.

**Im übrigen Repo, neu gefunden:**

- **cad_fenster.js hatte 1138 Zeilen** – am 2026-11-15 entlang dieser
      Nähte geteilt, jetzt 899; was noch hinausgehört, steht in der
      Durchsicht vom 2026-11-15, Punkt 7.

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
– bis auf zwei, die auch die Oberfläche betreffen: die Stablinie vor dem
Bauen und die Einheiten am Feld. Offen sind sonst die Punkte der
Oberfläche. Was in den Abschnitten darunter schon steht, steht hier nicht
noch einmal: die Grundlage der Apps mit Zeichenfenster, die
`Fallauswertung`, die Dateien über 1000 Zeilen.

- [ ] **Sechs eigene Zwischenspeicher für Nebenanfragen** (`qa_zeichnung.js`,
      `bs_zeichnung.js`, `qa_diagramme.js`, `bs_diagramme.js`, `app.js`,
      `bericht.js`) mit drei Regeln für Fehler: ohne Antwort des Kerns
      bleibt die Querschnittsanalyse still ohne Geometrie, das
      Balkensystem zeigt den Fehler. Besser `nachgefragt(schluessel,
      abdruck, holen)` mit `{daten, alt, fehler}` – gehört zur Grundlage
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
      Zeichnung (`zeichengeometrie.geometrie`) je nach Art ab – dort ist
      der Stahl noch eine Kennung, kein Baustoff.
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
      nicht – `KombinationEintrag.M_Ed` und Co. –, und die Oberfläche
      schreibt sie darum selbst («M_Ed [kNm]» in `plattenkapitel.js`).
      Besser: die Einheit ans Feld (`bereich(einheit=…)`), dann liest die
      Maske sie aus dem Katalog – zusammen mit «Einheiten der Platte beim
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
      `bericht.js` ausziehen – sonst importierten sich `apps.js` und
      `bericht.js` gegenseitig.
- [ ] **Kern-Wissen im JS, neu dazugekommen:**
      - Das Querschnittsbild einer Analyse (Punkt aus N und M oder aus
        Randdehnungen) beschriftet seine Zahlen selbst mit kN, kNm, ‰, 1/m
        und mm – wie seine Zeichendaten sie liefern (`_bild_dict`). Die
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
      Hilfetexte wiederholen Regeln des Kerns – «x/d ≤ 0.35»
      steht neben einem Feld bis 0.5 (`nachweise.js`) –, eine Normstelle
      steht in `editor.js`, Wert-IDs werden aus Text nachgebaut
      (`zustand.js` `namensraum`). Besser: eine `Fallauswertung` im
      Stabwerk für Herleitung und Bildschirm – für die Lagerkräfte gibt es
      sie schon (`Systembefund.lagerkraefte`) –, Anzeige auf der nächsten
      Probe, Hilfetexte und Formeln aus denselben Konstanten über den
      Katalog.
- [ ] **Balkensystem: Kennung statt Name.** Ein Fall wird an seinem Namen
      erkannt, gleiche Namen sind darum verboten – seit 2026-10-15 als
      Meldung am System, nicht mehr als Fehler des ganzen Projekts. Stäbe
      und Lasten werden in vier Durchgängen aufgelöst, mit einem Schalter
      `melden`. Besser: LF1/LK1 als Identität, Lasten einmal je Fall
      auflösen. («Fest» als `math.inf` ist seit 2026-10-25 ein `Halt`.)
- [ ] **Varianten im Kern – deine Entscheidung.** `prioritaet`,
      `bedingung`, `anwendbar`, `verworfene_varianten` benutzt ausserhalb des
      Kerns niemand. Wer zwei Berechnungen für denselben Wert anmeldet
      (kopierter Namensraum), bekommt keinen Fehler, sondern still eine
      Variante; die zuerst angemeldete gewinnt. Empfehlung: ein Erzeuger je
      Wert, `registriere` wirft beim zweiten. War eine Gründungsentscheidung.
- [ ] **Dateien über 1000 Zeilen**, je entlang einer Naht, die schon da ist:
      `cad_fenster.js` (Bedienung, Rückgängig, Punkteingabe auslagern; die
      Befehle stehen in vier Listen, Knöpfe täuschen Tastendrücke vor),
      `stil.css` – geteilt am 2026-11-20, nach Bausteinen statt je App;
      `cad_fenster.js` 1138 – geteilt am 2026-11-15, jetzt 902.
      `querkraft.py` und `querschnitt/platte.py` sind
      geteilt (2026-10-25); die Regel für d_v steht in Kurve und Nachweis
      ohne Bügel noch je einmal.
      `nachweise.js`, `spannungsanalyse.py` und `aufbau.py` sind geteilt,
      `querschnittsloeser.py` liegt bei 743.
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

- [ ] **Vorlage Trapez: Dicke der Schubwand nach Vorgabe**
      (`opencivil/querschnitt/vorlagen.py`, `_trapez`, seit 2026-11-27).
      Die Vorlage gibt der Wand die engste Breite zwischen den beiden
      Stablagen: bei b oben 400 und b unten 300 mm die Breite auf der Höhe
      der unteren Stäbe, etwa 309 mm. Die kleinere Breite gibt den kleineren
      Widerstand der Druckstrebe (Gl. (47)); nicht nachgeschlagen, ob
      SIA 262:2025 für einen Steg mit veränderlicher Breite etwas sagt. Die
      Dicke lässt sich nach dem Einsetzen an der Wand ändern.
- [ ] **Spannstahl gedrückt** (`opencivil/querschnitt/werkstoffgesetz.py`,
      `Spannstahlgesetz`, seit 2026-11-26). Figur 17 der SIA 262:2025
      idealisiert nur den Zug (4.2.3.3); nach Vorgabe, nicht nachgeschlagen,
      trägt der Spannstahl gedrückt nichts. Ein vorgespanntes Glied kommt
      nie dorthin – seine Vordehnung ist grösser als jede Stauchung des
      Betons –, ein schlaffes ohne Vorspannung schon. Bestätigen oder sagen,
      ob er gedrückt wie der Betonstahl tragen soll.
- [ ] **Baustahl, Grenzdehnung nach Vorgabe**
      (`opencivil/material/baustahl.py`, `DUKTILITAET`). Die Linie des
      Baustahls endet bei ε_ud = 15·ε_y, für S355 bei 25.4 ‰. SIA 263:2013
      nennt keine Grenzdehnung; 15 ist das kleinste Verhältnis von Bruch-
      zu Fliessdehnung, das 3.2.2.4 für die plastischen Verfahren verlangt.
      Bestätigen oder eine andere Zahl nennen. Wirkt seit 2026-11-26 in den
      Spannung-Dehnung-Analysen: dort endet die Linie eines Stahlquerschnitts.
- [ ] **Wasser, 1000 kg/m³ nach Vorgabe** (`opencivil/material/fluessigkeit.py`,
      seit 2026-11-27). SIA 261:2020 rechnet den Wasserdruck mit der
      Raumlast γ_w,k (4.4.2.1, Gl. (8)), nennt aber keine Zahl; die
      Flüssigkeiten in Anhang A, Tabelle 30, sind Lagergüter, das Wasser
      steht nicht darunter. Mit g = 10 m/s² gibt das γ_w = 10 kN/m³, die
      Vorgabe des Feldes γ_w von früher. Bestätigen oder eine Normstelle
      nennen.
- [ ] **Profilblechstahl, nach Vorgabe** (`opencivil/material/profilblech.py`,
      seit 2026-11-27).
      - Die Linie endet wie beim Baustahl bei ε_ud = 15·ε_yp, für SE 350 G
        bei 25 ‰. Weder SIA 264 noch SIA 263 nennen eine Grenzdehnung.
      - Ein neuer Profilblechstahl beginnt mit SE 350 G; 3.3.1 nennt
        SE 320 G und SE 350 G als üblich, aber keine zuerst.

      Bestätigen oder eine andere Zahl und Sorte nennen.
- [ ] **Blechverbunddecke, nach Vorgabe eingebaut**
      (`opencivil/verbund/blechdecke.py`, `opencivil/nachweis/qa_blechverbund.py`,
      seit 2026-11-27). Jede Annahme steht auch in der Herleitung.
      - Das Blech ist gleich dick, seine Fläche gleichmässig über die
        Abwicklung verteilt; Sicken und Ausrundungen zählen nicht.
      - Gedrückt trägt das Blech nichts: es beult. Ohne Moment zählt es
        gezogen, unter negativem Moment nicht (5.4.3.2).
      - Mit zwei Einzellasten bleibt der Abstand a, wie eingegeben, auch im
        End- oder Innenfeld: die Norm sagt nicht, ob er im gleichwertigen
        Einfeld kürzer wird.
      - L/d_p rechnet mit der eingegebenen Spannweite, nicht mit der des
        gleichwertigen Einfelds.
      - τ_cd in (26) und γ_v = 1.25 in (28) bleiben, auch wo die
        Tragsicherheit charakteristisch rechnet.
      - Eine Analyse rechnet eine Decke; eine Decke hat höchstens 100 Rippen.
      - Wo bei einer Normalkraft selbst das grösste Moment dieser Zugseite
        in die Gegenrichtung zeigt, ist der Widerstand null.

      Vorschlag: so lassen. Entscheid des Benutzers.
- [ ] **Holz, Grenzstauchung nach Vorgabe** (`opencivil/material/holz.py`,
      `STAUCHBARKEIT`, seit 2026-11-26). Elastisch-plastisch geht der Druck
      bis ε_cu = 3·ε_c,0,d, bei C24 bis 3.27 ‰. SIA 265:2012, 3.1.2.2 lässt
      das Fliessen zu, wo ein Bauteil plastisch stauchen kann, und nennt
      keine Grenze. Bestätigen oder eine andere Zahl nennen. Wirkt seit
      2026-11-26 in den Spannung-Dehnung-Analysen, wo das Holz
      «elastisch-plastisch» rechnet.
- [ ] **Holz: wo die Linie der Biegung endet – zu entscheiden**
      (`opencivil/spannungsanalyse/rissfrei.py`, seit 2026-11-26). Das
      Gesetz des Holzes bricht auf Zug bei f_t,0,d; so endet die M-χ-Linie,
      wo der gezogene Rand f_t,0,d erreicht – beim Rechteck 200 × 400 mm aus
      C24 bei 8 · W = 42.7 kNm. Der Nachweis der Biegung nach SIA 265 rechnet
      mit f_m,d und gibt seit Schritt 13 in der Kachel «Tragsicherheit»
      14 · W = 74.7 kNm. Ein Gesetz kann nicht beides: mit f_m,d trüge der
      reine Zug zu viel. Empfehlung: so lassen – die Linie zeigt das
      Gesetz, die Tragsicherheit den Nachweis nach (14) und (21); die
      Legende sagt, dass eine Faser ihre Grenzdehnung erreicht.
- [ ] **Erdbeben, nach Vorgabe eingebaut** (`opencivil/erdbeben/ersatzkraft.py`,
      `kern.py`). Getrennte Teile eines Kerns – Polygone, die kein Stück
      Kante teilen – zählen je um ihren eigenen Schwerpunkt, ohne
      Steiner-Anteil zwischen ihnen (Benutzer, 2026-11-27), und tragen am
      Fuss nach ihrem Anteil an I; eine Aussparung trennt ein Polygon nie,
      auch wo sie es ganz durchschneidet. Verformt wird der Kern nur durch
      Biegung, weder durch Schub noch im Fundament; η_EI = 0.5 als Anteil
      der ungerissenen Steifigkeit –
      16.5.5.2 verlangt eine mittlere Steifigkeit bis zum Fliessbeginn;
      g = 10 m/s² wie beim Eigengewicht. Nicht gerechnet, und das Ergebnis
      sagt es grau: die Torsion (16.5.2.7), die vertikale Komponente
      (16.5.4), sekundäre Bauteile (16.7) und, wo q über 2.0 liegt, die
      Bemessungswerte duktiler Tragwände (SIA 262:2025, 4.3.9.4).
      Entschieden (Benutzer, 2026-11-21): der Anteil heisst η_EI, nicht κ –
      κ ist in der Querschnittsanalyse die Krümmung und in SIA 262:2025 die
      Vergrösserung der Querkraft für höhere Eigenformen (4.3.9.4.4, (97)).
- [ ] **Pfähle, nach Vorgabe eingebaut** (`opencivil/pfahl/`). Beim
      örtlichen Abscheren gelten η_a und γ_M,a trotzdem, obwohl das Buch
      danach keine weitere Sicherheit vorsieht (Kap. 12.5); X wird dabei mit
      φ'_k abgelesen, nicht mit 2/3 davon. Ausserhalb der Bilder 12.4 und
      12.5 gilt der Wert am Rand. Der Fuss im undrainierten Ton rechnet ohne
      die Überlagerung, das Gewicht des Pfahls steht ebenso wenig in der
      Einwirkung. Auf Zug dieselbe Mantelreibung wie auf Druck. δ/φ'_k und α
      höchstens 1. Der Mörtel im Rohr eines Mikropfahls zählt nicht, obwohl
      SIA 267:2013, 9.5.2.4.8 ihn zuliesse – nach SIA 262 endete der ganze
      Querschnitt sonst bei −ε_c1d. Das Tragglied rechnet als Betonstahl nach
      SIA 262 mit γ_s; SIA 263:2013 liegt im Ordner der Normen und ist nur
      für die Querkraft eingearbeitet. Vorschlag: so lassen, jede Annahme steht in der
      Herleitung. Entscheid des Benutzers.
- [ ] **Pfähle, Steifigkeit nach Vorgabe eingebaut**
      (`opencivil/pfahl/steifigkeit.py`). Die Bettung quer wächst vom
      Terrain linear bis t_red, vorgegeben 2 m – 9.5.4.5 verlangt nur, sie
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
      Kopf, ohne Querkraft, gibt keinen Nachweis R_tr – geprüft wird dann nur die
      Bettungskraft. Vorschlag: so lassen, jede Annahme steht in der
      Herleitung. Entscheid des Benutzers.
- [ ] **Pfähle, innerer Widerstand quer nach Vorgabe eingebaut**
      (`opencivil/pfahl/innen_quer.py`). Bohrpfahl: d reicht bis zum
      Schwerpunkt der halben Bewehrung, als ob die Stäbe gleichmässig auf dem
      Kreis lägen; b_w ist die Sehne auf der Höhe des Druckgurts – für den
      Kreis nennt SIA 262:2025 keine Breite; α_min = 30° auch unter Druck, wo
      4.3.3.3.3 bei bedeutendem Druck 25° zuliesse; die Wendel ist aus dem
      Stahl der Längsbewehrung; die Längszugkraft F_tVd (4.3.3.4.11) wirkt in
      der Achse statt je zur Hälfte an den Gurten, auf der sicheren Seite;
      die Querkraft zählt auch nahe dem Kopf, wo 4.3.3.4.1 sie im Abstand
      z · cot α nähme. Mikropfahl: A_v = 2·A/π für Rohr und Vollstab –
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
      schmaler ist als etwa 0.3 · t. Die eingebaute Näherung – Rankine ohne
      Wandreibung, hinten aktiv abgezogen – bleibt darunter: ⌀ 900 mm in
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

- [x] **Durchstanzen gegen das Skript geprüft (2026-11-26).** Jede Formel
      des Moduls gegen das Skript «Stahlbeton II, 7.4 Platten» (Kaufmann,
      FS 2026) und SIA 262:2025, 4.3.6 gelegt. Offen war nur, welches V_d in
      m_sd (62) bis (65) gilt: jetzt die ganze Auflagerkraft, wie im Modell
      des Skripts (Folie 28; Entscheid des Benutzers, 2026-11-26). Das Skript
      weicht an zwei Stellen von der Norm 2025 ab, das Werkzeug folgt der
      Norm: k_g nach (37) mit der Untergrenze 1.2 und D_max · (60/f_ck)²
      über 60 MPa (Skript: ohne Untergrenze, mit dem Exponenten 4 des neuen
      Eurocode 2); in (69) f_ctm, das die Norm als Bemessungswert der
      Verbundspannung bezeichnet (Skript: f_bd wie SIA 262:2013). Nicht
      abgebildet: Vorspannung (m_Dd, 4.3.6.4.3) und Leitungen (Figur 23e).
- [ ] **Durchstanzen, Einzellasten nahe am Nachweisschnitt (4.3.6.2.3).**
      Greifen Einzellasten über 0.2·V_d näher als 3·d_v am Schnitt an, ist
      die ungleichmässige Querkraft zu berücksichtigen. Das Werkzeug kennt
      solche Lasten nicht; jede Herleitung sagt es grau (Benutzer,
      2026-11-26). Offen: eine Eingabe dafür, falls gewünscht.
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
      Nachweisschnitt mindert (Figur 23d) – wie gross sie ist, zählt nicht.
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
- [ ] **Durchstanzbewehrung: die Regeln der Bügel (2026-11-26).** Nach der
      Norm: mindestens zwei Reihen zwischen 0.35·d_v und d_v, s_0 kleiner
      als s_1, s_1 und ⌀ höchstens nach Tabelle 21 (5.5.3.8, 5.5.3.12), beim
      zweiten Schenkel höchstens 1.5·d_v auseinander (5.5.3.9), in (70) die
      2 der Norm (4.3.6.5.9). Nach Vorgabe, nicht nachgeschlagen: der erste
      Schenkel 0.35·d_v vom Rand, auf 5 mm aufgerundet; der zweite bei d_v,
      abgerundet, höchstens s_1 weiter; danach s_1; ⌀8 bis ⌀26 (die Liste
      der Bügelsuche) bis zur Grenze der Tabelle 21, aus B500B; zwei bis neun
      Reihen; die Höhe h − c − c_v. Offen: c misst bis zur Biegebewehrung –
      umfasst ein Bügel sie, liegt er um seinen Durchmesser näher an der
      Oberfläche. Die Höhe geht in keinen Widerstand ein, nur in Text und
      Bild.
- [ ] **Durchstanzbewehrung HALFEN HDB: der Faktor 3.5.** Eingebaut am
      2026-11-27 nach der Produktinformation Technik von Leviat (09/2026):
      Doppelkopfanker aus B500, ⌀12, 14, 16, 20 und 25. Die Unterlage nennt
      in (70) den Faktor 3.5 anstelle der 2, nach einem Gutachten (Kenel),
      das nicht vorliegt; ohne dessen Regeln für die Anordnung lässt
      4.3.6.5.9 nicht mehr als die 2 zu. Nach Vorgabe, nicht nachgeschlagen:
      die Anker stehen wie die Bügel nach der Norm (0.35·d_v, d_v, danach
      s_1 nach Tabelle 21), die Durchmesser bis zur Grenze der Tabelle 21, in
      (70) die 2, die Höhe h − c − c_v auf 5 mm abgerundet, der Stahl B500B.
      Offen: das Gutachten oder eine technische Dokumentation mit Abständen
      und Faktor – dann gälte 3.5 mit den Regeln des Herstellers. Holen nur
      mit deinem Ja, Datei für Datei. Entschieden (Benutzer, 2026-11-27):
      bis diese Regeln vorliegen, bleibt die 2.
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
      einbetonierte Leitungen (Figur 23e); bei Plattenbereichen mit eigener
      Dicke (4.3.6.2.7, Figur 24) keine eigenen Leisten an Stufen der
      Gegenseite und am Schnitt durch verschiedene Dicken, kein Stahlpilz
      und keine Bereiche an Wänden; Vorspannung
      (4.3.6.4.3); an Rand- und Eckstützen die untere Bewehrung als
      gezogene (4.3.6.4.7); die Verankerung der Biegebewehrung (5.5.3.7);
      ein Schnitt, der an einer Aussparung nahe der Stütze endet
      (4.3.6.2.2). Die Bedingung 0.5 ≤ l_x/l_y ≤ 2 für Stufe 1 und 2
      (4.3.6.4.2) prüft das Werkzeug nicht, die Sicherung gegen
      Totaleinsturz (4.3.6.7) steht nur als Hinweis.
- [ ] **Sprödes Versagen unter Zug fehlt.** Wo ein Querschnitt für die
      Tragsicherheit zählt, muss sein Widerstand die Rissbeanspruchung
      übertreffen, auch die auf Normalkraft (SIA 262:2025, 4.3.1.2, mit
      `f_ct,eff` nach 4.4.1.3; ebenso 4.1.4.2.4). Geführt wird nur das
      Rissmoment gegen `M_Rd`; die Rissnormalkraft hält das Werkzeug allein
      gegen die zulässige Stahlspannung der Zwängung, und die liegt bei
      normaler Anforderung bei `f_yk`, bei erhöhter für ⌀10 und ⌀12 ebenfalls
      über `f_yd`. Beispiel: Platte h = 250 mm, C30/37, normale Anforderung,
      `N_Riss` = 322 kN je Lage und Meter – heute genügen 644 mm²/m, mit
      `A_s·f_yd ≥ N_Riss` brauchte es 741 mm²/m (+15 %). Vorschlag: die
      Bedingung als eigenen Nachweis führen. Entscheid des Benutzers.
- [ ] **Gebrauch mit Mittelwerten.** Gebrauchsnachweise rechnen mit den
      Mittelwerten der Baustoffe (SIA 262:2025, 4.4.1.2). Die Stahlspannung
      nimmt als Grenze des Betons `f_ck` statt `f_cm = f_ck + 8 N/mm²`
      (C30/37: 30 statt 38 N/mm²); im elastischen Bereich zählen nur `E_s`
      und `E_cm`, die schon Mittelwerte sind. Einen Mittelwert der
      Fliessgrenze kennt die Norm nicht, beim Stahl bleibt `f_yk`. Die Grenze
      gegen Fliessen ist `f_yd − 80 N/mm²`, so nennt sie Tabelle 17.
      Empfehlung: lassen – `f_ck` liegt auf der sicheren Seite. Entscheid
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
      Spannungen rechnet 4.1.4.1.4 ungerissen linear elastisch und gerissen
      ohne Zug im Beton – dort ist er ein Modell, keine Normregel. Das Druckplateau `f_y,druck` des Stahls
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
      M-N-Nachweis rechnet. Entscheid des Benutzers. Seit 2026-11-20 gilt
      dasselbe, wenn nur ein Baustoff charakteristisch rechnet.
- [ ] **Wie heisst ein Widerstand mit gemischten Werten?** Seit 2026-11-20
      wählt jedes Modul seine Werte je Material. Rechnet etwa der Beton
      charakteristisch und der Stahl mit Bemessungswerten, heisst der
      Widerstand R, weder Rd noch Rk (nach Vorgabe, nicht nachgeschlagen;
      `Wertesaetze.index`). Entscheid des Benutzers.
- [ ] Die Querschnittsanalyse nennt ihre Widerstände in vier Dateien fest
      «Rd», auch wenn sie charakteristisch oder gemischt rechnet:
      `schiefe_biegung.py`, `richtungsnachweise.py`, `qa_kennzahlen.py`,
      `schubwandnachweis.py`. Die Platte nennt sie nach der Wahl.
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
      Querschnitt mit Stahl – dann reissen beide Linien am selben Punkt.
      Entscheid des Benutzers.
- [ ] **Der äquivalente E-Modul** (Spannung-Dehnung-Analyse, M–E_eq und
      N–E_eq) zählt die Verformung ab dem Zustand ohne laufende Kraft (deine
      Wahl, 2026-10-11): `E_eq = M/(I_c·(χ − χ_0))`. Ein Modell mit dem
      ungerissenen Betonquerschnitt gibt damit die Verformung aus der
      laufenden Kraft wieder, nicht, was die feste allein verformt. Er gilt
      für den Querschnitt, ohne Zugversteifung – für eine Durchbiegung liegt
      er damit tief (sicher), für Zwangkräfte nicht. SIA 262:2025 kennt
      keinen solchen Modul (geprüft am 2026-11-14); bestätigen lassen.
- [ ] **Der kürzeste Abstand bei der genauen Linie** misst zum gezeichneten
      Polygon des Fächers (80 Schritte je Abschnitt), nicht zum genau
      gesuchten Rand wie Normalkraft und Moment konstant.

### Querschnittsanalyse

Je eine Annahme eingebaut, im Code mit «nach Vorgabe, nicht nachgeschlagen».

- [ ] **Schubfluss, nach Vorgabe eingebaut** (`opencivil/nachweis/qa_schubfluss.py`,
      seit 2026-11-27). Die SIA 262 nennt die einwirkende Kraft in einer
      Fuge nicht; der Eurocode nimmt β·V/z (EN 1992-1-1, 6.2.5 – liegt nicht
      vor, nicht nachgeschlagen). Eingebaut ist v = ΔF′/Δx aus zwei
      Dehnungsebenen des ganzen Querschnitts, gerissen, mit der Rechenwahl
      des Falls; elastisch gibt das V·S′/I, gerissen mit festem Hebelarm
      β·V/z. Dazu Δx = 10 mm, ΔM im Vorzeichen von M, ohne
      Gleichgewichtslage bei M + ΔM der Schritt zurück, und τ = v/b_i als
      Mittel über die Länge, auf der der Schnitt Material von Material
      trennt.

- [ ] **Stahlquerschnitt, nach Vorgabe eingebaut** (`opencivil/stahlbau/`,
      `opencivil/nachweis/qa_stahl_kennzahlen.py`, seit 2026-11-26). Jede
      Annahme steht auch in der Herleitung.
      - Die Dicke, nach der Tabelle 1 die Fliessgrenze wählt: ein Profil
        rechnet ganz mit der seines dicksten Blechs, eine frei gezeichnete
        Fläche mit ihrer kleinsten Breite. Über 100 mm gilt weiter die
        rechte Spalte, wo die Tabelle endet.
      - Die Schubflächen: (41a) gilt für das I in Stegrichtung; für die
        anderen verweist 5.1.4.1 auf SN EN 1993-1-1, die nicht vorliegt.
        Eingebaut wie in den Excel-Dateien des Benutzers: das U in
        Stegrichtung A − 2 b t_f + (t_w + r) t_f, I und U quer dazu
        2 b t_f, das Rundrohr 2 t (D − t), das Rechteckrohr je Wand nach
        (13) mit b = h − t.
      - Das Schubbeulen mit k_τ = 5.34, dem langen Feld ohne Quersteifen;
        Flansche und Rundrohre beulen nicht.
      - Beulwerte ausserhalb ihrer Formeln: unter ψ = −3 (k₁ und (70)),
        −1 (k₂) und −1.2 (beidseitig gestützt) gilt der Wert am Rand. Für
        die mitwirkende Breite eines einseitig gestützten Blechs k₁ oder
        k₂ der Tabelle 5b statt der drei Werte der Tabelle 9 (auf 1 %
        gleich).
      - Der wirksame Querschnitt in einem Schritt, aus den Spannungen des
        Bruttoquerschnitts. Beim einseitig gestützten Blech fällt der
        Streifen am freien Ende weg, auch unter einem Gefälle der
        Spannung; Tabelle 10 zeigt nur den gleichmässigen Druck.
      - Das UNP mit t_f in der Mitte des geneigten Flanschs und r_1 als
        Ausrundung.
      - Ein Rundrohr der Klasse 4 trägt nichts: SIA 263 nennt dafür keine
        mitwirkende Breite.
      - Den Nettoquerschnitt nach (39) prüft das Werkzeug nicht.
      - y und z gelten als Hauptachsen, wie im Balkensystem.
      - Frei gezeichnete Flächen: höchstens Klasse 3, ihr Beulen nicht
        geprüft, und sie tragen keine Querkraft.

      Vorschlag: so lassen. Entscheid des Benutzers.

- [ ] **Stahlquerschnitt je Lastfall, nach Vorgabe eingebaut**
      (`opencivil/stahlbau/widerstand.py`, `opencivil/nachweis/qa_stahl.py`,
      seit 2026-11-26). Jede Annahme steht auch in der Herleitung.
      - Die Klasse im Lastfall: α an der plastischen Nulllinie bei N_Ed, ψ
        an den elastischen Spannungen, bei denen (54) gerade aufgeht. Ein
        ROR 323.9 x 5 mit N = +500 kN und M = 30 kNm ist so in Klasse 4 und
        nicht nachweisbar, obwohl es unter der Einwirkung ganz gezogen ist:
        im Versagen ist ein Teil gedrückt.
      - Klasse 1 und 2 genau plastisch (5.1.1.2, 5.1.8) statt nach (44) wie
        die Excel-Dateien: beim HEB 300 aus S355 12 bis 16 % mehr.
      - Querkraft über 0.5 V_Rd: die Bleche, in denen sie steht, tragen mit
        1 − (V_Ed/V_Rd)² – für jedes Profil und jede Richtung, auch für die
        Normalkraft, und in den Klassen 3 und 4 statt der
        Vergleichsspannung. Zwei Richtungen im selben Blech zählen
        zusammen, höchstens bis zum ganzen Blech. Beim Rundrohr der ganze
        Ring mit A_v/A.
      - Im Rundrohr die Resultierende √(V_y² + V_z²), wie in den
        Excel-Dateien.
      - (54) und (60) mit e·N, wo der Schwerpunkt neben dem Bezugspunkt
        liegt; bei Zug zählt in (60) der ganze Querschnitt. Mit mehreren
        Baustählen zählt je Glied der, der zuerst fliesst.
      - Mit charakteristischen Werten heissen die Widerstände weiter «Rd»,
        wie beim Stahlbeton der Querschnittsanalyse.
      - Torsion nicht nachgewiesen: SIA 263 nennt in 5.1 bis 5.3 keinen
        Torsionswiderstand des Querschnitts. Ein grauer Hinweis nennt den
        Lastfall.
      - Für Stahl kein Interaktionsdiagramm.

      Vorschlag: so lassen. Entscheid des Benutzers.

- [ ] **Knicken und Kippen, nach Vorgabe eingebaut**
      (`opencivil/stahlbau/stabilitaet.py`,
      `opencivil/nachweis/qa_stahl_stabilitaet.py`, seit 2026-11-26). Jede
      Annahme steht auch in der Herleitung.
      - Das Rundrohr gilt als warmgefertigt, Kurve a – wie in den
        Excel-Dateien. Für ein kaltgefertigtes wählt man c.
      - Die Kurve gilt je Achse für alle Fälle der Analyse. Ohne einzelnes
        Profil kennt das Werkzeug sie nicht; dann wählt man sie.
      - Die Klasse im Fall bei N_Ed und den Momenten 1. Ordnung, nach
        derselben Regel wie im Lastfall der Tragsicherheit.
      - ψ gilt für ω (5.1.9.1) und für η (B.6). Mit Querlast oder
        verschieblich ψ = 1: ω = 1 verlangt 5.1.10.3, η = 1 liegt auf der
        sicheren Seite. Unter ψ = −0.5 bleibt η bei 2.35.
      - Der Druckgurt ohne Ausrundungen, als gedrückter Steg die Hälfte der
        Höhe zwischen den Flanschen (Biegung allein); im Rechteckrohr beide
        Stege. In Klasse 4 der ganze Druckgurt, obwohl B.5 und 5.6.2.3 nur
        die mitwirkenden Teile zulassen – auf der sicheren Seite.
      - σ_Dv = 0, sobald der Fall in Klasse 4 ist (B.4), auch wo die
        Klasse 4 aus dem Druck kommt – auf der sicheren Seite, bei einem
        geschlossenen Rohr sehr.
      - Rohre kippen mit α_D = 0.21 der Walzprofile.
      - Mit mehreren Baustählen λ̄_K = √(Σ f_y A/N_cr).
      - w_0 nach Figur 3 mit der Knicklänge als Stablänge; in Klasse 4
        mindert χ_D in (62) und (63) den Widerstand um die starke Achse.
      - (51) nur, wo L_D und die Knicklänge um die schwache Achse beide
        über null sind; es gilt die günstigere von (50) und (51). Wo
        gekippt wird, gilt (9) immer auch allein.
      - Eine Schlankheit über 200 (4.5.1.7) ist nur ein Hinweis.
      - Nicht gerechnet: Biegedrillknicken (4.5.1.2), die Vergrösserung ξ
        (5.1.9.2), die kritischen Kipplängen der Tabelle 6, das Kippen
        geschweisster I und frei gezeichneter Querschnitte, (51) für das
        gewalzte Rechteckrohr – die Reihe RRW fehlt noch.
      - Anders als die Excel-Datei «Stabilitätsnachweise»: sie vergrössert
        in (50) mit N_K,Rd statt mit N_cr, etwas auf der sicheren Seite;
        das Werkzeug folgt (50).

      Vorschlag: so lassen. Entscheid des Benutzers.

- [ ] **Holzquerschnitt, nach Vorgabe eingebaut** (`opencivil/holzbau/`,
      `opencivil/nachweis/qa_holz.py`, `qa_holz_stabilitaet.py`,
      `qa_holz_werte.py`, seit 2026-11-26). Jede Annahme steht auch in der
      Herleitung.
      - Die Biegespannung je Achse an der weitesten Faser, M/W mit
        W = I/e_max: beim Rechteck genau, bei einem T auf der sicheren
        Seite.
      - Brettschichtholz hat seine Lamellen parallel zu y: k_h nach (5)
        gilt für die Biegung um y, mit der Höhe in z, und auch in (37) und
        (38). Um z gilt es nicht.
      - Den Systembeiwert k_sys (5.7.2.2) nimmt das Werkzeug nicht.
      - Querkraft in y und in z: τ_d = √(τ_y² + τ_z²), als lägen beide
        grössten Schubspannungen an derselben Stelle – auf der sicheren
        Seite.
      - Torsion nur im Rechteck mit Seiten parallel zu y und z, mit
        W_T = k_2·h·b² nach Saint-Venant; Kippen nur im Rechteck, mit (41)
        und der Kipplänge L_D als Abstand der seitlichen Halterungen. Bei
        einem anderen Querschnitt steht der Fall grau.
      - Die relative Schlankheit beim Knicken und Kippen mit f_c,0,k,
        f_m,k und E_0,05 aus Anhang B, ohne η_w.
      - Die Feuchteklasse gilt für die ganze Analyse; die
        Spannung-Dehnung-Analysen rechnen ohne η_w.
      - «Stossartig» gilt für den ganzen Fall: η_t = 1.4 vergrössert alle
        Festigkeiten des Falls. Die Kennzahlen rechnen ohne.
      - Ein Querschnitt aus mehreren Hölzern hat keinen Nachweis (grau):
        er bräuchte einen nach den Steifigkeiten gewichteten Querschnitt.

      Vorschlag: so lassen. Entscheid des Benutzers.

- [ ] **Verbundquerschnitt, nach Vorgabe eingebaut** (`opencivil/verbund/`,
      `opencivil/nachweis/qa_verbund.py`, `qa_verbund_kennzahlen.py`,
      `qa_verbund_werte.py`, seit 2026-11-26). Jede Annahme steht auch in
      der Herleitung.
      - Voll verdübelt angenommen (5.1.2.1), wo die Kachel «Verdübelung»
        nicht Kopfbolzendübel wählt; mit Dübeln siehe den nächsten Punkt.
      - Ein Stab ist ein Quadrat seiner Fläche, eine verschmierte Linie ein
        Rechteck; beide verdrängen den Beton, in dem sie liegen.
      - Die Klasse an der plastischen Nulllinie des Lastfalls. Nur die
        Klassen 1 und 2 rechnen; darüber steht der Fall grau («über 2»),
        denn elastisch nach 5.1.2.4 und 5.1.2.5 rechnet das Werkzeug noch
        nicht.
      - Kammerbeton: erkannt an fünf Punkten einen Millimeter neben dem
        Blech – beim Flansch innen bis 0.4 b von der Mitte des Stegs, wie
        im Bild der Tabelle 3 mit b_c/b ≥ 0.8, beim Steg auf beiden Seiten.
        Breiterer Beton zählt mit. Der Steg rechnet nach 5.2.1.3 mit 42ε,
        der kleinsten Grenze der Klasse 3 (bei reinem Druck), als Grenze
        der Klasse 2 – auf der sicheren Seite, weil ψ elastisch nicht
        gerechnet wird. Die Verbindung von Steg und Kammerbeton (5.2.1.2)
        nimmt es an; dass die Dübel einen Druckflansch nach 4.2.2.3 in die
        Klasse 1 heben, prüft es nicht.
      - 5.1.2.3 für jedes Moment, das Betonstahl zieht, nicht nur über der
        Stütze: ist er nicht in der Duktilitätsklasse B oder C, steht der
        Fall grau.
      - β (5.1.2.2) für jeden Baustahl mit f_y ≥ 420 N/mm²; x_p senkrecht
        zur Nulllinie ab dem gedrücktesten Punkt des Betons, h quer zu ihr
        über den ganzen Querschnitt – auch bei schiefer Biegung und bei
        negativem Moment, wo der Kammerbeton gedrückt ist. Über
        x_p/h = 0.4, wo Figur 1 endet, steht der Fall grau. Beim HEA 300
        aus S460 unter einer Platte 1500 × 120 mm ist darum die Biegung
        um z grau: die Druckzone reicht über 0.4 der Breite.
      - Der Beton mit 0.85·f_cd überall, auch im gefüllten Rohr; nur die
        Verbundstütze rechnet ihn dort mit 1.0 (5.3.2.5, 5.3.4.4), seit
        2026-11-27. γ_a ist γ_M1 des Baustahls.
      - Ein Rohr im Verbundquerschnitt mit den Grenzen der SIA 263; die
        Tabelle 6 gilt der Verbundstütze, und dort prüft das Werkzeug sie.
      - Die Querkraft trägt der Stahl allein; einen Anteil des Betons nach
        5.2.2.2 rechnet das Werkzeug nicht.
      - Torsion nicht nachgewiesen; ein Hinweis nennt den Lastfall.
      - Nicht geprüft: f_ck zwischen 20 und 50 N/mm² (3.5.1).
      - Für den Verbund keine Spannung-Dehnung-Analysen und kein
        Interaktionsdiagramm.

      Vorschlag: so lassen. Entscheid des Benutzers.

- [ ] **Verdübelung, nach Vorgabe eingebaut** (`opencivil/verbund/duebel.py`,
      `opencivil/verbund/querschnitt.py`, `opencivil/nachweis/qa_verbund.py`,
      seit 2026-11-27). Jede Annahme steht auch in der Herleitung.
      - Die N Dübel zwischen dem Schnitt und dem Momentennullpunkt tragen
        die Kraft, die Beton und Betonstahl ausserhalb der Profile im
        Schnitt zusammen haben; am Momentennullpunkt ist sie null, auch mit
        einer Normalkraft. 6.1.1.2 verlangt, die Normalkräfte zwischen den
        kritischen Schnitten zu berücksichtigen.
      - Kammerbeton zählt zum Stahl: Beton und Betonstahl in der konvexen
        Hülle eines Profils hängen am Steg (5.2.1.2), nicht an den Dübeln.
        Eine Platte, die nur auf dem Profil aufliegt, zählt ganz zum Beton.
      - Den Bereich negativer Momente erkennt das Werkzeug am Querschnitt:
        Beton und Betonstahl ausserhalb der Profile sind bei voller
        Verdübelung zusammen gezogen, oder die plastische Nulllinie zieht
        die Seite, auf der der Beton liegt. Dort verlangt es volle
        Verdübelung (6.1.1.6).
      - (29) nur für ein einziges Profil mit zwei Symmetrieachsen, erkannt
        an seiner Form (I-Profil, Rohr); sonst verlangt das Werkzeug η ≥ 1.
      - (30) mit dem schwächsten Beton des Querschnitts.
      - γ_v = 1.25 auch, wo die Tragsicherheit charakteristisch rechnet.
      - Mit Teilverdübelung gelten die Klassen an der Nulllinie des
        Baustahls, 5.1.2.3 und β an der des Betons.
      - Ohne Moment prüft das Werkzeug die Dübel nicht.

      Vorschlag: so lassen. Entscheid des Benutzers.

- [ ] **Verdübelung, noch nicht nachgewiesen** (seit 2026-11-27):
      - die konstruktive Durchbildung (SIA 264, 7.1);
      - der Längsschub in der Platte mit ihrer Querbewehrung (5.1.4,
        (4) bis (12));
      - Dübel unter Zug (6.1.2.2) und das Abheben der Platte (6.1.1.5);
      - die Abminderung im Profilblech (6.1.3, (32) und (33)): die
        Blechverbunddecke gibt es seit 2026-11-27, einen Verbundträger mit
        Dübeln durch ihr Blech noch nicht;
      - wie die Dübel bis zum Momentennullpunkt verteilt sind: gleichmässig
        nur unter den Bedingungen von 6.1.2.3; das Werkzeug fragt nur ihre
        Zahl.

- [ ] **Verbundstütze, nach Vorgabe eingebaut** (`opencivil/verbund/stuetze.py`,
      `opencivil/nachweis/qa_verbund_stuetze.py`, seit 2026-11-27). Jede
      Annahme steht auch in der Herleitung.
      - Doppelsymmetrisch heisst: je Werkstoff liegt der Schwerpunkt
        höchstens 1 mm neben der Mitte des Profils, und |I_yz| erreicht
        höchstens 1 % von √(I_y I_z).
      - Die Art nach Tabelle 7 liest das Werkzeug an der Zeichnung: ganz
        einbetoniert, wenn acht Punkte 1 mm ausserhalb des umschreibenden
        Rechtecks des Profils – Ecken und Mitten der Seiten – im Beton
        liegen; kammerbetoniert, wenn Beton den Steg beidseits und jeden
        Flansch innen deckt und ausserhalb des Profils nichts liegt;
        gefüllt, wenn in der Mitte des Rohrs Beton liegt und ausserhalb
        nichts. Nur ein einziges Profil aus der Tabelle.
      - Der Betonstahl über 6 % der Betonfläche zählt in jedem Stab
        gleichmässig weniger, auch in M_pl und in der Steifigkeit; 5.3.2.2
        sagt es für den Widerstand.
      - Ein Rohr mit mehr als 6 % Betonstahl rechnet mit Kurve b: Tabelle 7
        endet bei 6 %.
      - Die Ersatzimperfektion wächst mit k_0 = 1/(1 − N_Ed/N_cr,eff), also
        mit ω = 1 wie unter einer Querlast; zweiachsig wirkt sie in beiden
        Achsen zugleich.
      - Zweiachsig: Σ M_Ed,II/(μ_d M_pl,Rd) ≤ 0.9, bei S420 und S460 0.8.
        5.3.5 nennt die lineare Interaktion, aber keine Grenze.
      - μ_d höchstens 1: ob das Moment aus der Normalkraft selbst entsteht,
        weiss das Werkzeug nicht (5.3.4.6).
      - Die Theorie 2. Ordnung immer, auch wo (21) sie erliesse.
      - Eine Achse mit Moment rechnet immer nach 5.3.4; 5.3.2.2 liesse den
        zentrischen Nachweis bis zu einer Endexzentrizität von 0.1 h zu.
      - Eine Knicklänge null heisst gehalten: um diese Achse knickt die
        Stütze nicht, und ein Moment um sie wächst nicht.
      - E_s ist der Wert des Betonstahls; 3.6.2 liesse vereinfacht
        210 kN/mm² zu.

      Vorschlag: so lassen. Entscheid des Benutzers.

- [ ] **Verbundstütze, noch nicht nachgewiesen** (seit 2026-11-27):
      - die Querkraft im Profil: ab V_a,Ed ≥ 0.5 V_pla,Rd mindert sie den
        Biegewiderstand (5.3.4.5);
      - die Einleitung der Lasten und der Schub zwischen Stahl und Beton
        (5.3.6);
      - die Steifigkeit aus Moment und Krümmung (18);
      - ein Querschnitt ausserhalb der Tabelle 7 (5.3.5 verweist dafür auf
        SN EN 1994-1-1).
      Idee: die Kachel könnte die Art des Querschnitts schon nennen, bevor
      ein Fall rechnet; heute steht sie in der Herleitung und, wo sie
      fehlt, grau am Fall.

- [ ] **Ein Rohr füllen – zu entscheiden** (seit 2026-11-27). Beton, der
      ein Rohr füllt, muss ganz in seinem Loch liegen; das Loch eines RRK
      hat runde Ecken, ein Rechteck mit den Innenmassen liegt darum auf dem
      Stahl, und die Zeichnung meldet es rot. Von Hand geht es nur mit einem
      Vieleck, das den Ecken ausweicht. Vorschlag: am Profil ein Feld
      «Füllung» mit dem Beton – das Loch wird dann selbst zur Fläche aus
      diesem Beton, genau, ohne Zeichnen. Entscheid des Benutzers.

- [ ] **Holz: C16 unter Zug – zu entscheiden** (`opencivil/material/holz.py`,
      `zugglied_grund`, seit 2026-11-26). SIA 265 lässt C16 nicht als
      Zugglied zu (Tabelle 6, Fussnote 2). Heute steht das als Hinweis in
      der Herleitung, und der Nachweis rechnet weiter: ein Rechteck aus C16
      unter Zug ist «erfüllt», wenn die Spannung reicht. Empfehlung: rot am
      Lastfall, als nicht erfüllt, mit dem Grund – das ist falsch, nicht
      bloss unfertig.

- [ ] **Der Bezug des äquivalenten Moduls ohne Beton**
      (`opencivil/spannungsanalyse/rissfrei.py`, seit 2026-11-26). Hat ein
      Querschnitt aus Holz oder Baustahl zwei Sorten derselben Art, misst
      sich E_eq am Modul der grössten Fläche. Bestätigen oder einen anderen
      Bezug nennen, etwa den nach Fläche gemittelten.

- [ ] **Spannglieder: die Vorgabe der Spannung bei Y1100 und Y1030 – zu
      entscheiden** (`opencivil/querschnitt/spannglieder.py`, `vorspannung`,
      seit 2026-11-26). Ein neues Glied beginnt mit den Faktoren 0.70 und
      0.85, σ_p0 = 0.70·f_pk und σ_p∞ = 0.85·σ_p0, so gewählt vom Benutzer am
      2026-11-25, nach Vorgabe, nicht nachgeschlagen: die Verluste hängen am
      Bauwerk (SIA 262:2025, 4.1.5.3). Bei den Stäben Y1100 und Y1030 liegt
      schon die Vorgabe über der Grenze nach Gleichung (22): 770 über 765 und
      721 über 705.5 N/mm²; dort steht sie rot am Glied, und ein kleinerer
      Faktor, etwa 0.65, hält sie. Bei allen anderen Sorten hält sie, bei
      Y1570 knapp (1099 unter 1105). Seit 2026-11-27 ist die Vorgabe ein
      Faktor am Glied, nicht an der Sorte: ihn beim Wechsel des Stahls von
      selbst zu senken, deutete die Zahl des Benutzers um. Empfehlung: so
      lassen.
- [ ] **Spannglieder: Vordehnung ohne die Stauchung des Betons.** Eingebaut:
      ε_p = σ_p∞/E_p. Die Stauchung, die die Vorspannung im Beton an der
      Stelle des Glieds weckt, fehlt; ohne Last trägt ein Glied darum etwas
      weniger als σ_p∞ – im Rechteck 300 × 600 mm des Tests 1055 statt
      1107 N/mm². Bestätigen oder die Stauchung dazunehmen.
- [ ] **Spannglieder: Duktilität.** Mit Spannstahl in der Zugzone führt die
      Duktilität keinen Nachweis über x/d: 4.1.4.2.5 nennt Betonstahl der
      Klassen B und C, und der Nachweis sagt es grau. Umlagern ginge nur mit
      einem Nachweis des Verformungsvermögens (4.1.4.2.6). Bestätigen.
- [ ] **Spannglieder: Zwängung auf Normalkraft.** N_Riss gilt ohne
      Vorspannung, N_s,adm nur mit dem Betonstahl; ein Hinweis sagt es. Den
      Spannstahl mitzuzählen liesse 4.4.2.3.10 zu. Sprödes Versagen und
      Zwängung auf Biegung zählen die Vorspannung im Rissmoment schon mit
      (4.3.1.2; 4.4.3.2.4). Entscheiden, ob die Normalkraft nachzieht.
- [ ] **Spannglieder: Spannungszuwachs im Gebrauch (4.4.2.3.10) ungeprüft.**
      Die Stahlspannungen im Gebrauch begrenzen nur den Betonstahl; ohne ihn
      steht «Ohne Betonstahl → kein Nachweis.».
- [ ] **Geneigte Spannglieder: die grösste Kraft bei ungünstiger Neigung.**
      4.3.3.4.9 verlangt dann die grösste Kraft im Spannstahl, ohne zu
      sagen, welche.
      Eingebaut (`opencivil/nachweis/schubwandnachweis.py`, seit
      2026-11-26): mit Verbund A_p mal die Fliessgrenze des Wertesatzes
      (f_pd), ohne Verbund A_p·σ_p0. Bei vier Litzen ⌀15.7 aus Y1860 834.8
      statt 664 kN. Bestätigen – oder etwa P0 = A_p·σ_p0 für alle.
- [ ] **Geneigte Spannglieder: der Anteil mindert die Einwirkung.** Gl. (50)
      legt P∞·sin β_p zum Widerstand; das Werkzeug zieht ihn von V_z ab,
      bevor die Kraft auf die Wände verteilt wird: nur so findet er bei
      mehreren Wänden seinen Platz. An der Grenze gleich, der Erfüllungsgrad
      aber V_Rd/(V_Ed − V_p) statt (V_Rd + V_p)/V_Ed – bei 300 kN, 57.9 kN
      und V_Rd = 394.3 kN 1.63 statt 1.51. Bestätigen.
- [ ] **Geneigte Spannglieder: längs, und höchstens 20°.** Im Biegewiderstand
      und im Gebrauch zählt ein geneigtes Glied, als läge es längs
      (cos β_p ≈ 1, bei 20° 0.94); das Feld lässt darum höchstens ±20° zu.
      Das Moment der lotrechten Kraft um den Schwerpunkt geht in die Torsion
      der Wände. Nur die Neigung in der lotrechten Ebene, für V_z. Bestätigen.

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
      Vollquerschnitt rechnet die Norm als Zelle (4.3.5.1). Seit 2026-11-18
      ist eine gezeichnete Wand an ihren Knoten geteilt, jedes Teil eine
      eigene Schubwand (Benutzer), und je Wand gilt die ganze Kraft,
      V_Ed = |q|·l, gegen V_Rd mit der Wandlänge als Hebelarm. Für eine
      Zelle ist das die Norm: (55) gibt die Torsion als Kraft je Wand,
      V_d,i = T_d·z_i/(2·A_k), und 4.3.5.5 zählt sie mit der Querkraft
      zusammen (nachgeschlagen, S. 59).
- [ ] **Längszugkraft aus Querkraft und Torsion.** Die Formel ist bestätigt
      (SIA 262:2025, 4.3.3.4.11, (51); 4.3.5.4): je Wand
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
      Norm zählt der Steg, t = 200 mm und `k_t` = 0.909 – Rissmoment und
      Mindestbewehrung rund 6 % zu klein. Unter Zug heute `k_t` = 0.769
      (t = 600 mm) statt 0.909. Vorschlag: `t` aus der Dicke des gezogenen
      Teils (Steg- oder Plattendicke); einfach und sicher wäre die dünnste
      Wand des Querschnitts. Entscheid des Benutzers.
- [ ] **Wanddicke im vollen Querschnitt.** Für die Torsion zählt eine Wand
      eines Vollquerschnitts höchstens `d_k/8` dick, `d_k` der grösste Kreis
      in `A_k` (SIA 262:2025, 4.3.5.3, (56)); für die Querkraft allein zählt
      die Stegbreite. Das Beispiel «Unterzug» 300 × 600 nimmt 100 mm, für die
      Torsion wären höchstens 25 mm erlaubt – es rechnet sie viermal zu
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
      kann, etwa nach der Streifenmethode (4.3.3.2.3, (41)) – das Werkzeug
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
      ungerissenen Bruttoquerschnitt (`nachweis/rissgroessen.py`, für die
      Analyse in `spannungsanalyse/riss.py`, seit 2026-11-21 auch für die
      Platte):
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
      für 500 mm (SIA 262:2025, 4.4.2.3.7) – seit 2026-11-14, vorher
      begrenzte der Schalter nur `t`. Die Zwängung auf Biegung je Richtung
      mit dem Rissmoment des spröden Versagens gegen das Moment, bei dem der
      erste gezogene Stab `σ_s,adm` erreicht – gerissen, ohne Zug im Beton
      wie in 4.1.4.1.4, präzise mit der Parabel (bis 2026-11-25 linear);
      ohne N, mit eigenem φ und mit der gedrückten Bewehrung (die
      Platte lässt sie weg), dazu sagt die Norm nichts. `σ_s,adm` je Stab mit
      seinem Durchmesser und dem `f_ctm` seines Betons, wie (102) es will;
      eine verschmierte Linie mit einem fiktiven Durchmesser (siehe «Welcher
      Durchmesser …»).
- [ ] **Knicken je Richtung.** Eingebaut (`nachweis/qa_knicken.py`): je Fall
      zu einer Zugseite, die Nulllinie parallel zur Achse wie einachsig –
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
      q = 10 kN/m: einfacher Balken 6 m, w = 7.44 mm (L/w = 807) – liegt ein
      Knoten in Feldmitte, zeigt die App 1.60 mm. Kragarm 2 m: die Spitze
      senkt sich 0.88 mm, die App zeigt 0.14 mm. Seit 2026-11-14 sagt der
      Bericht das, und L/w steht nicht mehr da. Vorschlag: w je Feld gegen
      die Verbindung seiner Auflager messen, mit L/w; ein Feld reicht über
      Knoten ohne Lager, an denen zwei Stäbe in einer Flucht stossen, und am
      Kragarm gilt die doppelte Länge. Offen bliebe der Abfangträger: eine
      Stütze, die auf ihm steht, sieht aus wie eine, die ihn trägt.
      Entscheid des Benutzers.

- [ ] **Stahlprofile nach Vorgabe, nicht nachgeschlagen.** Masse und
      Formeln kommen aus der Tabelle des Benutzers («Festigkeitsnachweise
      I-Standardprofile Stahl», 2019-04-15), mit den Beiwerten der Zwickel
      gerundet wie dort (0.2146, 0.2234, 0.00755). Die RRK-Radien aus der
      Wanddicke wie in der Tabelle (bis 6 mm 2t/t, bis 10 mm 2.5t/1.5t,
      darüber 3t/2t). Beim UNP hat die Tabelle keine Formeln: gerechnet mit
      8 % Neigung und t_f bei b/2 bis h = 300 mm, darüber 5 % und t_f in der
      Mitte des Flanschs – so gewählt, dass die Werte der Tabelle getroffen
      werden (A, I_y auf 0.6 %, e_y 1 %, I_z 1.4 %); I_T des UNP wie beim
      UPE, mit t_f und r_1. Gegen eine Profiltabelle prüfen, etwa die
      Stahlbautabellen des SZS.
      Die warmgefertigten Rechteckrohre (RRW, seit 2026-11-27): ihre Grössen
      aus dem Katalog von ArcelorMittal, Radien nennt er keine. Gerechnet
      mit r_o = 1.5 t und r_i = t, wie für warmgefertigte Rohre üblich – EN
      10210-2 liegt nicht vor. Das RRW 200 × 100 × 8 hat damit A = 44.75 cm²,
      I_y = 2234 cm⁴ und I_z = 739 cm⁴.
      Vollstahl (VKT, RND, FL, seit 2026-11-27): ohne Bleche in Klasse 1, und
      die Querkraft trägt der ganze Querschnitt, A_v = A – SIA 263 verweist
      für A_v auf SN EN 1993-1-1, die nicht vorliegt, und die Tabellen 5a
      und 5b kennen nur Bleche und Rohre. Elastisch wären es beim Rechteck
      zwei Drittel davon. Der Flachstahl liegt: FL 100 x 10 ist 100 mm breit
      und 10 mm dick; hochkant steht er um 90° gedreht oder, im
      Balkensystem, «um z» gebogen. Prüfen, ob A_v = A bleiben soll.

### 3D-Balkensysteme

- [ ] **Ein Gelenk löst im Raum alle drei Momente, nach Vorgabe**
      (`stabwerk3d/system.py`). Biegung um beide Achsen und Torsion, wie ein
      Kugelgelenk; ein Stab mit Gelenken an beiden Enden trägt darum keine
      Torsion, und ein Moment um seine Achse ist ein Fehler. So rechnet ein
      Fachwerk aus Gelenkstäben wie in der Ebene. Hielte das Gelenk die
      Torsion, wäre jedes solche Fachwerk beweglich: seine Knoten drehten
      sich ohne Widerstand. Ein Anschluss mit Fahnenblech hält die Torsion
      aber oft fest, er wirkt als Gabel. Dafür bräuchte es ein Gelenk, das
      nur die Biegung löst. Entscheid des Benutzers: so lassen, oder die Art
      je Gelenk wählbar machen.
- [ ] **Die Achsen des Stabs und das Vorzeichen von M_z, nach Vorgabe**
      (`stabwerk3d/stab.py`, `stabwerk3d/verlauf.py`). Die z-Achse des Stabs
      zeigt nach unten, in der lotrechten Ebene durch ihn; bei einem
      lotrechten Stab ist y die Achse -y des Systems. M_y und M_z ziehen
      beide an der positiven Seite ihrer Achse, wie das Moment des
      2D-Balkensystems an der gestrichelten Faser: σ = N/A + M_y·z/I_y +
      M_z·y/I_z. Nach der Rechtsschraube hätte M_z das andere Vorzeichen;
      manche Programme rechnen so. Prüfen, ob es so bleiben soll.
- [ ] **Torsion nur nach St. Venant, nach Vorgabe.** Die Wölbkrafttorsion
      fehlt (I_w), und der Schubmittelpunkt liegt auf der Stabachse. Beim
      U-Profil liegt er in Wirklichkeit neben dem Steg: eine Last durch den
      Schwerpunkt verdreht es. Gerechnet wird, als täte sie das nicht.
- [ ] **Ein Lager hält nur in den Achsen des Systems.** Ein einfacher
      Balken auf zwei gelenkigen Lagern braucht eine Gabel, ein Lager, das
      die Drehung um seine Achse festhält. Sonst ist er beweglich, und die
      Meldung sagt es. Liegt der Balken schief im Grundriss, hält eine Gabel
      um x oder y auch einen Teil seiner Biegung fest. Schiefe Lager fehlen,
      wie in der Ebene.
- [ ] **I_T der Querschnittsvorlagen, nach Vorgabe**
      (`stabwerk/querschnitte.py`). Rechteck, T und Doppel-T zerfallen in
      Rechtecke, je mit der Näherung von Roark: s · t³ · (1/3 − 0.21 · t/s ·
      (1 − t⁴/(12 · s⁴))), t die kürzere Seite. Beim Rechteck trifft das die
      Tafel von Timoshenko auf ein Prozent; bei T und Doppel-T fehlt der
      Knoten zwischen Steg und Flansch, der etwas dazugibt (die Walzprofile
      rechnen ihn mit d_K). Das Trapez rechnet als Rechteck seiner
      mittleren Breite, das Rechteckrohr als dünne Wand nach Bredt, Kreis
      und Kreisring mit 2 · I_y. Ein Betonquerschnitt reisst unter Torsion,
      und seine Torsionssteifigkeit fällt dann stark ab; gerechnet wird
      ungerissen. Die Norm erlaubt, die Steifigkeit für Risse und Kriechen
      abzumindern, und sagt dazu, dass das günstig oder ungünstig wirken
      kann (SIA 262:2025, 4.1.4.1.3). Prüfen, ob die Formeln so bleiben
      sollen.
- [ ] **Die Vorwahlen der Lager im Raum, nach Vorgabe**
      (`projekt/balkensystem3d.py`). «Gelenkig» hält die drei
      Verschiebungen, «verschieblich» nur die lotrechte, «eingespannt» alle
      sechs Richtungen. Danach lässt sich jede Richtung für sich frei, fest
      oder federnd stellen, wie in der Ebene.
- [ ] **Ein eigenes Material hat G = 80 000 N/mm², nach Vorgabe** – wie
      E = 200 000 N/mm² und ρ = 7850 kg/m³ ungefähr ein Stahl. Wer ein
      eigenes Material nimmt, gibt G selbst ein.
- [ ] **Im Raum fehlt ein Diagramm der Verdrehung.** Ein Knoten dreht sich
      dort um drei Achsen; welches Bild es zeigen soll, ist offen. Die
      Zahlen stehen in der Herleitung.
- [ ] **Lager, die im Bild aufeinanderfallen.** In den Ansichten x-z und
      y-z liegen zwei Lager, die sich nur in der Tiefe unterscheiden, auf
      demselben Punkt; ihre Lagerkräfte drängen sich dann, und die Zahlen
      können sich trotz `freistellen` decken. Schräg von oben stehen sie
      getrennt. Offen, ob es mehr braucht.
- [ ] **Ein Knoten, der sich um eine Achse frei dreht, zeigt keine
      Drehung.** Im Raum zählt ein Knoten als «nicht bestimmbar», sobald ihn
      um eine Achse nichts hält – etwa mit einer Drehfeder um eine Achse,
      wo sonst nur Gelenke hängen. Beim Darüberfahren steht dann der Satz
      statt aller drei Drehungen, auch der bestimmten; die Herleitung nennt
      den Knoten (`web/balkendaten.py`). Besser wäre je Achse.

## Noch nicht gebaut

- [ ] **Stahlprofile, was fehlt:** L, INP, T und HEAA – die Tabelle des
      Benutzers hat sie nicht. Das Verkaufsprogramm von ArcelorMittal dafür
      hat er am 2026-11-27 nicht holen lassen: «weglassen». Die RRW sind seit
      dem Tag drin, aus dem Rohrkatalog derselben Firma, dazu Vierkant-,
      Rund- und Flachstahl mit freien Massen. Ein Flachstahl kippt im
      Werkzeug nicht: den Druckgurt nach Figur 40 kennt es nur beim I und
      beim Rechteckrohr. Für das Kippen
      fehlt noch I_w (Schritt 12d); W_el, W_pl und A_v rechnet seit
      2026-11-26 die Querschnittsanalyse am Umriss, die Bleche für die
      Querschnittsklasse liefert jede Form (`stahlprofile/bleche.py`).

- [ ] **Holz, was nach Schritt 13 fehlt:** der Querdruck f_c,90,d, mit
      Vorholz oder am Endauflager samt den Klammerwerten der Tabellen 6 und
      7 – er braucht ein Auflager, das die Querschnittsanalyse nicht kennt;
      die Kriechzahlen (Tabelle 5); k_sys (5.7.2.2); ein Querschnitt aus
      mehreren Hölzern; Torsion und Kippen ausser im Rechteck; Nachweise
      für einen Holzstab im Balkensystem. Holzwerkstoffe nach SIA 265/1
      kennt das Werkzeug nicht.

- [ ] **Spannglieder, nächste Schritte:** das Hüllrohr Ø_H und die Minderung
      der Stegbreite nach Gleichung (44) (4.3.3.3.5); eine Neigung in der
      waagrechten Ebene, für V_y. Die Neigung in der lotrechten steht seit
      2026-11-26.

- [ ] **Durchstanzen, nächste Schritte:** Stahlpilze an Rand und Ecke
      (der Katalog hat nur ganze Pilze); Durchstanzbewehrung an Wandende und
      Wandecke; weitere Produkte (DURA-Körbe und S-Elemente, FIDECA – Bügel
      gibt es seit 2026-11-26, HALFEN HDB seit 2026-11-27);
      Sicherung gegen Totaleinsturz (4.3.6.7).

- [ ] **Balkensysteme, nächste Schritte:** Umhüllende der Kombinationen,
      Theorie 2. Ordnung, Schubverformung, schiefe Lager, und die
      Schnittgrössen eines Stabs als Einwirkung einer Platte oder
      Querschnittsanalyse.

- [ ] **Querschnittsanalyse, nächste Schritte:** Stahl (SIA 263) und Holz
      (SIA 265) haben seit 2026-11-26 ihre Nachweise, mit Knicken und
      Kippen, der Verbund (SIA 264) die Tragsicherheit des Querschnitts.
      Seit 2026-11-27 auch die Verdübelung (6.1) und die Verbundstützen
      (5.3), die Blechverbunddecken (5.4). Beim Verbund fehlen noch
      das Kippen (5.1.2.6), der elastische Widerstand der Klasse 3
      (5.1.2.4, 5.1.2.5) und die Spannung-Dehnung-Analysen: sein Riss
      braucht den ideellen Querschnitt. Ein E_eq im Balkensystem gibt es
      bis dahin nur beim Stahlbeton. Dazu weitere Nachweise (Wände ohne
      Bügel).
- [ ] **Blechverbunddecke, noch nicht nachgewiesen** (seit 2026-11-27; die
      Herleitung der Kennzahlen nennt das meiste):
      - das Durchstanzen unter Einzellasten (5.4.3.4, (27));
      - die Querkraft bei d_p über 150 mm nach SIA 262 – bis dahin steht das
        Urteil mit Erfüllungsgrad null und einem Hinweis da;
      - die Endverankerung (5.4.3.6) und, statt der m-k-Methode, die
        Teilverdübelung nach SN EN 1994-1-1;
      - andere Lasten als gleichmässig oder zwei symmetrische Einzellasten
        für die Schublänge (5.4.3.5);
      - die Durchbiegung, wo L/d_p über 26 liegt (5.4.4.2);
      - der Bauzustand (5.4.4.4) und die Schwingungen (5.4.4.7);
      - die Mindestbewehrung über den Stützen (5.4.4.6), mit der Kette von
        Einfeldern nach 5.4.2.3;
      - M_z, V_y und T: die Decke trägt in einer Richtung (5.4.1.1);
      - die Spannung-Dehnung-Analysen, wie beim Verbund.
- [ ] **Baustahl: die Wärmedehnzahl** α_T = 10·10⁻⁶/°C (SIA 263:2013,
      3.2.2.2) fehlt – es gibt keine Temperatur als Einheit, und keine
      Rechnung braucht sie. Kommt mit der ersten, die sie braucht.
- [ ] **Kriechzahl φ an den Flächen der Querschnittsanalyse.** Die
      Stahlspannungen und die Zwängung auf Biegung rechnen mit dem φ ihres
      Kapitels, wie bei der Platte – für jeden Beton dasselbe. Ein φ je
      Fläche bräuchte es erst, wenn zwei Betone verschieden kriechen sollen.
      Die Eigenschaften einer Fläche stehen in der Seitenleiste des
      Zeichenfensters; φ käme dort ohne Umbau dazu.
- [ ] **Ein Kreis ist ein 48-Eck.** Die Ecken liegen auf dem Kreis, die
      Fläche ist darum 0.3 % kleiner als π·D²/4. Steht so in der Zeichnung;
      wer es genauer will, zeichnet mehr Ecken.

- [ ] **Neu gerechnet wird je Bauteil, nicht je Wert.** Eine Platte, deren
      Beschreibung sich nicht geändert hat, kommt aus dem Zwischenspeicher –
      das war das Ziel und es steht. Innerhalb einer Platte wird aber weiter
      alles gerechnet: ein umgelegter Duktilitätsschalter rechnet den
      Knicknachweis derselben Platte mit, obwohl der nichts davon weiss. Feiner
      ginge es erst, wenn die Nachweise ihre Lastfälle nicht mehr im Bauch
      trügen, sondern über Bezüge – heute hätte ein Knickfall mit geänderter
      Normalkraft denselben Bezugsgraphen wie vorher, und ein feiner Abdruck
      sähe den Unterschied nicht. Das wäre ein Umbau an jedem Nachweis, und der
      Fehlerfall wäre eine stillschweigend falsche Zahl.
- [ ] **Die M-χ- und die N-ε-Linie zeigen den Querschnitt, ohne
      Zugversteifung.** Ungerissen bis zum Riss, dort der Sprung, darüber
      gerissen. Für die Durchbiegung eines Bauteils fehlt die
      Mitwirkung des Betons zwischen den Rissen. Bis 2026-10-06 stand sie als
      `ζ = 1 − β·(M_Riss/M)²` mit β = 1.0 drin (üblich: 1.0 kurzzeitig, 0.5
      dauernd oder wiederholt) – dafür war der Sprung nicht zu sehen. Ob eine
      Linie des Bauteils dazukommt, mit welcher Regel und welchem Beiwert nach
      SIA 262, ist nicht nachgeschlagen. Für eine Durchbiegung ist der
      kleinere Beiwert (weicher) der ungünstige, für eine Zwängung der
      grössere.
- [ ] **k_σ der Parabel nie unter 1.** Mit dem kriechweichen Modul
      `E_cm/(1+φ)` und charakteristischen Werten wird `E_c/(400·f_c)` kleiner
      als 1 (C30/37, φ = 2: 0.93); dann hätte der Nenner der Parabel im
      ansteigenden Ast eine Nullstelle. Angesetzt wird `max(1; E_c/(400·f_c))`:
      der Beton ist dann bis f_c bei ε_c1d linear – nach Vorgabe;
      SIA 262:2025, 4.2.1.6 nennt keine Untergrenze. Das Kriechen über den
      Modul der Parabel ist ebenfalls Vorgabe; beim Druckglied setzt es die
      Norm über die Krümmung an (siehe «Kriechen beim Knicken»).
- [ ] **Das Ende der Linien** liegt an den Grenzen des Dehnungsfächers:
      Betonrand −ε_c2d (Tabelle 8), Stahllagen ±ε_ud (Tabelle 9), Punkt C
      −ε_c1d bei `z_C = h·(1 − ε_c1d/ε_c2d)` – dieselben Grenzen wie
      überall, gezogen in `querschnitt/interaktion.py`; Punkt C nach Vorgabe
      (siehe oben).

## Erledigt zuletzt

Die genaue Linie der Platte läuft den Fächer der Interaktion ab, über
dieselben Streifen wie der gezeichnete Querschnitt (Punkt 4 der Durchsicht
vom 2026-11-19) · der Hinweis auf die Hauptachsen kommt weiter ab 5 % von
min(I_y; I_z) (Benutzer, 2026-11-19: «5 % lassen»; steht jetzt in
[[Arbeitsweise]]) ·
der Schalter «E-Modul» eines Querschnitts schreibt E_cm und E_eq, wie sie
heissen, statt E_CM und E_EQ ·

Aus der Strukturdurchsicht vom 2026-11-15, Punkt 2, der kleine Umbau: der
Pfahl rechnet N, M und V mit `ebener_verlauf`, das dafür linear wachsende
Bettung kennt · weg: `_schnittkraefte`, N nach der Trapezregel, das
nachgeschobene Kopfmoment · eine Teilungsregel für Balkensystem und Pfahl
(`stab.schritt`, `stab.stuecke`, `bettung.elementlaenge`), die feinere des
Pfahls · `SCHRITT_LAMBDA` ist weg ·

Aus der Strukturdurchsicht vom 2026-11-15, Punkt 3b: die Achsen jeder
Linie kommen eben wie im Raum aus dem Kern (`stabachsen`) · die Oberfläche
legt keine Faser mehr selbst: `linienachsen` und die Regel in `zugseite`
sind weg · wohin eine neue Linie läuft, sagt das System
(`LAUFRICHTUNGEN`), mit einem Test gegen die Achsen des Kerns ·

Aus der Strukturdurchsicht vom 2026-11-15, Punkt 3a: die Grenzwerte über
alle Stäbe, die massgebende Durchbiegung und die grösste Verschiebung kommen
aus dem Kern (`grenzwerte`, `Extrem.massgebend`,
`Stabverlauf.groesste_verschiebung`) · eine Regel für «massgebend» in
Bericht und Bildschirm (`nach_betrag`) · die grösste Verschiebung genau
statt aus den Proben des Bilds ·

Aus der Strukturdurchsicht vom 2026-11-15, Punkt 1: ein Rechenkern für
Ebene und Raum (`stabwerk/system.py`); was die Ebene anders macht, steht in
`stabwerk/art.py` · ein Verlauf längs der Stäbe für beide · eine Rechnung
mit zwei statt fünf Weichen · die Darstellung am Bildschirm nach der Art
der Rechnung, die Lage eines Stabs einmal · weg: `stabwerk3d/system.py`,
`stabwerk3d/verlauf.py`, der ebene Kern und sein Verlauf, der Befund des
Raums, `_lage_eben`, `Lastrichtung.vektor`, `drehung`, `transponiert_mal` ·

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
Lage der Platte auf einer Schablone (`Lagennachweis`) – Lagenwahl, Grade,
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
Apps mit Zeichenfenster (`cad_app.js`) – Lesen, Schreiben, Fenster je
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
gleich in welcher Liste – ohne Listennamen, ohne `anBauteil` und ohne
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
der Datenklassen, streng, und dieselbe Prüfung vor jedem Rechnen – die
Fassade geht durch dieselbe Tür wie eine Datei · alte Formate weg · die
Rissanforderung in einer Tabelle statt in vier · was beim Rechnen still einen
Ersatz nahm, meldet sich: ein Posten ohne Teilung, eine Knicklänge null, Stäbe
und Bügel ohne Stahl, ein Kennwert «fck», zwei gleiche Kennungen, ein Mass
«B» am Stabquerschnitt, eine leere Teilungsliste der Suche ·

Vom Benutzer entschieden (2026-10-16): die Kennzahlen der Platte bleiben, wie
sie sind – x/d je Seite, mit Bügeln das Kleinere beider Seiten, von Hand mit
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
seine Lösung ab · ein Ziel darf eine Berechnung sein – die Zahl der
Unbekannten, die Zeilenzahl des Blatts und der Querkraft-Nullfall sind fort ·

Gemischte Stahlsorten: Stahlspannung, Knicken, Querkraft und Analyse
nahmen den Stahl der ersten Lage für alle Lagen – jetzt trägt jede Lage
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
der beiden x-Lagen · Gesammelt wird in der Darstellung, nicht in der Prüfung –
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
