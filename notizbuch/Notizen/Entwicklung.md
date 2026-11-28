# Entwicklungsprotokoll

Was gebaut wurde, und vor allem **warum es so gebaut ist**. Das Was steht im
Code; das Warum geht sonst verloren. Neueste Einträge oben.

Wer das Werkzeug bloss benutzen will, liest [README.md](../../README.md).

---

## 2026-11-28 · Fachwerkmodell: kein Stab unter der Türe

Beim Lesen der SIMP-Form (Schritt 11d) fiel auf: Die Ground Structure
legte Stäbe längs der Schwelle einer Türe, die auf dem Rand der Scheibe
liegt – im Beispiel ein Zugband von (6, 0) nach (1, 0) mit 135 kN, quer
durch die Türe. Ein Punkt auf dem Rand eines Lochs zählt als Material,
und so galt auch die Schwelle, obwohl dort auf keiner Seite Material ist.

- Neu braucht ein Stück eines Stabs auf einem Rand Material auf einer
  Seite, 10⁻⁵ m daneben gesucht – hundertmal die Rundung der Geometrie.
  Längs der Türe, über ihr und an den Rändern der Scheibe bleibt jeder
  Stab möglich (Test).
- Die Wandscheibe mit Türe trägt nun ohne das Band: bei h = 1 m 22 statt
  27 Stäbe, V = 7109.6 statt 3734.0 kNm; bei 0.5 m 58 statt 36 Stäbe,
  V = 6818.9 statt 3662.5 kNm.
- Mit «Zug nur waagrecht und senkrecht» geht sie im Raster von 1 m nicht
  mehr auf: bei (6, 0) bleiben 158.3 kN offen, genau die Kraft des Bands,
  rot gemeldet. Im Prüfprojekt steht sie darum mit 0.5 m: 67 Stäbe,
  V = 10175.0 kNm.
- Das Beispiel für das Halbieren der Schwelle N_min ist neu die Wand bei
  0.4 m: ohne die Stäbe unter 1 % und 0.5 % bleiben 0.8 % der grössten
  Last offen, ohne die unter 0.25 % nicht – 74 statt 89 Stäbe, gleich
  leicht. Bei 0.55 m geht es jetzt ohne Halbieren auf.

## 2026-11-28 · Fachwerkmodell: Zug nur waagrecht und senkrecht

Schritt 11c des Plans vom 2026-11-27. Im Fenster «Verfahren» steht unter
den drei Zahlen der Schalter «Zug nur waagrecht und senkrecht» [ja | nein],
Vorgabe nein. Mit ja tragen geneigte Stäbe nur Druck; den Zug nehmen
waagrechte und senkrechte auf, wie eine Bewehrung in x und y. Beispiel
Konsole 1 × 2 m, links oben und unten gehalten, 100 kN an der rechten
Kante: ohne den Schalter ein Zugstab schräg zum oberen Lager, V = 200 kNm;
mit ihm geht der Zug senkrecht hinauf und waagrecht zum Lager, V = 400 kNm
im Raster von 1 m – von Hand mit virtuellen Verschiebungen bestätigt –,
375 kNm bei 0.5 m. Die Wandscheibe mit Türe: 15 statt 27 Stäbe,
V = 3954.2 statt 3734.0 kNm; sie steht so ein zweites Mal im Prüfprojekt.

- In der Optimierung hat ein geneigter Stab keine Unbekannte für Zug,
  seine Kraft kann nur Druck sein: `optimieren` nimmt `None` statt der
  Kosten des Zugs. Die Unbekannten stehen dazu in einer Folge q⁺ (nur wo
  Zug geht), q⁻, r⁺, r⁻. Eine Schranke statt hoher Kosten, weil hohe Kosten
  nur fast null geben und, wo kein Fachwerk aufgeht, Zug statt einer
  ehrlichen Meldung.
- Die Suche fügt einen geneigten Stab nur dazu, wo er gestaucht würde; sie
  kommt Runde um Runde dorthin, wo die Optimierung über alle Stäbe ist
  (Test).
- Waagrecht oder senkrecht heisst bis auf 10⁻⁹ der Länge – nur Rundung;
  ein Stab mit 1 mm Gefälle auf 3 m ist geneigt.
- Geht so kein Fachwerk auf, nennt die rote Meldung an der Last den
  Schalter: «Die Last F1 lässt sich mit Zug nur waagrecht und senkrecht
  nicht ganz zu den Lagern tragen: 10.0 kN bleiben offen.» Die Suche sagt
  «Fertig nach 1 Runde: kein Fachwerk trägt die Lasten.», ohne leere
  Stabtabelle; die Herleitung sagt es in einem Satz. Vorher blieben dort
  Stäbe ohne Kraft stehen: was ein Stab mindestens tragen muss, galt gegen
  die grösste Stabkraft, die selbst fast null war – jetzt gegen die
  grösste Last.
- Die Rechnung prüft auch das abgelegte Fachwerk: ein geneigter Stab auf
  Zug steht rot. Die Suche gibt keinen; nur eine von Hand geänderte Datei
  kann es.
- Im feinen Raster verteilt sich der Zug oft auf viele Bänder – Konsole
  bei 0.25 m: 39 Stäbe, V = 372.5 kNm. Das ist das Optimum; ohne seine
  dünnen Stäbe ginge das Gleichgewicht nicht auf, auch mit N_min = 20 %
  bleiben alle 39 (Frage im [[TODO]]).

## 2026-11-28 · Fachwerkmodell: Ground Structure live

Schritt 11b des Plans vom 2026-11-27. Die Kachel «Verfahren» hat die
Rasterweite h, das Gewicht w_Z des Zugs gegenüber dem Druck und die
kleinste Stabkraft N_min; ihr Fenster den Knopf «Fachwerk suchen». Vorher
stand dort «Noch ohne Verfahren»; jetzt zeigt das Bild nach jeder Runde das
Fachwerk, Zug rot, Druck blau gestrichelt, je dicker, desto grösser die
Kraft, bis keine Stäbe mehr dazukommen oder man anhält. Beispiel
«Wandscheibe mit Türe»: bei h = 1 m 188 mögliche Stäbe, 16 Runden,
27 Stäbe, V = 3734.0 kNm; bei 0.5 m 1528 mögliche, 20 Runden, 36 Stäbe,
V = 3662.5 kNm, 2 % leichter.

- Das Verfahren nach He, Gilbert & Song (2019), Abschnitt 3: eine lineare
  Optimierung über die Stabkräfte, selbst geschrieben als primal-duales
  Innere-Punkte-Verfahren nach Mehrotra, mit dem Gleichungslöser der
  Stabwerke (Profilmatrix, Reverse-Cuthill-McKee). Die erste Runde kennt
  nur die Stäbe bis 1.5 h; danach kommen je Runde die dazu, die das
  Fachwerk noch leichter machten (Gl. (7), α = β = 0.05). Ein Rest je
  Knoten mit hoher Strafe hält jede Runde lösbar – geht das Gleichgewicht
  nicht auf, sagt die Nachrechnung rot, welche Last offen bleibt.
- Die Seite rechnet nichts: sie schickt den Zustand der letzten Runde
  zurück – welche Stäbe im Modell sind, mit dem Abdruck von Modell und
  Verfahren –, der Kern gibt die nächste Runde und das Fachwerk zum
  Zeichnen. Ändert man das Modell während der Suche, passt der Abdruck
  nicht mehr, und sie beginnt von vorn. Wird das Modell gelöscht oder ein
  anderes Projekt gewählt, hört sie auf und legt nichts ab.
- Am Ende legt die Seite das Fachwerk im Eintrag ab; von da an ist es eine
  Eingabe wie jede andere. Die Rechnung rechnet sein Gleichgewicht nach
  und erkennt am Abdruck, ob es noch zum Modell passt – sonst grau «gehört
  zu einem früheren Stand». Auch die Seite vergleicht den Abdruck: ohne das
  stünde zwischen dem Ende der Suche und der nächsten Rechnung einen
  Augenblick «Noch kein Fachwerk gesucht».
- Die Meldungen sind zweierlei: was das Modell meldet und was zum Fachwerk
  zu sagen ist (`zum_fachwerk`) – noch keines, veraltet, angehalten, offen.
- Das Innere-Punkte-Verfahren endet bei mehreren gleich leichten
  Fachwerken in ihrer Mitte, mit vielen kleinen Stäben. Die Nachbearbeitung
  lässt die unter N_min der grössten Kraft weg und sucht das Gleichgewicht
  ohne sie neu; geht es nicht auf, halbiert sie die Schwelle. Bei 0.55 m:
  49 statt 102 Stäbe, gleich leicht. Gründlich, mit bis zu 30 Versuchen,
  nur in der letzten Runde – sonst dauerte die Suche bei 0.5 m 5 statt
  2 s. Zuletzt werden zwei Stäbe in einer Flucht durch einen freien Knoten
  einer.
- Zeit für die Wandscheibe: in CPython 0.3 s bei 1 m und 2 s bei 0.5 m;
  auf der Seite (Pyodide, 150 bis 170 ms je Runde) 4.5 s bei 0.55 m und
  40 s bei 0.25 m. Darum sucht sie auf Knopfdruck (Frage im [[TODO]]).
- Das Prüfprojekt hat das Fachwerk, das die Suche bei 1 m findet
  (`FachwerkmodellEintrag.suchen`, je Lauf einmal gesucht): der Bericht
  zeigt die Stäbe, V, die Lagerkräfte und die Formel «Leichtestes
  Fachwerk». Gegen die Handrechnung prüft eine Konsole 1 × 2 m, links
  oben und unten gehalten, 100 kN nach unten an der rechten Kante auf
  halber Höhe: zwei Stäbe mit ±70.7 kN, V = 200 kNm, mit w_Z = 2
  300 kNm.

## 2026-11-27 · Fachwerkmodell: Scheibe, Lager und Lasten zeichnen

Schritt 11a des Plans vom 2026-11-27: eine neue App «Fachwerkmodelle»,
eben. Gezeichnet wird im Zeichenfenster wie bei der Decke, in Metern:
Scheiben als Umrisse, Löcher, Lager und Punktlasten, alles an Knoten.
Gesucht wird noch kein Fachwerk; das kommt mit den Verfahren in 11b bis
11d. Beispiel «Wandscheibe mit Türe»: 6 × 3 m, eine Türe 1 × 2.2 m,
links fest, rechts verschieblich in x, oben 300 kN und 50 → / 200 ↓ kN.

- Ohne Material und ohne Dicke, ein Satz Lasten je Modell (Entscheid 11
  des Plans): ohne Bemessung hängen Fachwerk und Kräfte nur von Form,
  Lagern und Lasten ab.
- Material ist, wo eine Scheibe ist und kein Loch – der Rand eines Lochs
  zählt noch dazu (`Modell.im_material`, neu `geometrie.auf_rand`). So
  darf eine Last auf dem Sturz einer Türe stehen.
- Ob die Lager die Scheibe halten, prüft der Kern als starrer Körper:
  jede Richtung, in der ein Lager hält, ist eine Gleichung in
  Verschiebung und Drehung; drei unabhängige halten sie. Sonst nennt die
  graue Meldung die Bewegung, die bleibt – «sie kann sich in x
  verschieben», «… um das Lager A2 drehen», «… um den Punkt (0.00, 3.00)
  drehen». Warum vor jedem Verfahren: über einem beweglichen Modell gibt
  es kein Gleichgewicht, und die Optimierung in 11b fände nur eine
  singuläre Matrix statt eines Grundes.
- Was nur fehlt, steht grau (keine Scheibe, kein Lager, «Keine Last → kein
  Fachwerk.»), was falsch ist, rot (eine Last neben der Scheibe oder im
  Loch, ein Umriss ohne Fläche); ein Loch neben jeder Scheibe ist bloss ein
  Hinweis. Solange nichts anhält, sagt ein Hinweis «Noch ohne Verfahren» –
  im Kern als Meldung, so stehen Bericht und Seite gleich.
- Lager und Last hängen am Knoten wie die Stütze der Decke: gewählt wird
  der Knoten, seine Seitenleiste hat je einen Schalter «Lager» und
  «Last». Das Lager hat drei Stellungen mit Bild, fest in x und y, nur in
  x (gedreht gezeichnet, links vom Punkt) und nur in y.
- Wie ein Teil heisst («Lager A1»), steht jetzt einmal in `cad_app.js`
  (`teilname`), für Decke und Fachwerkmodell; die Meldungen als Hinweise
  auf einer Karte in `bausteine.js` (`meldungshinweise`) – vier ältere
  Kopien davon stehen noch in Balkensystem und Decke (TODO).

## 2026-11-27 · Decke: FEM als zweites Verfahren

Schritt 10b des Plans vom 2026-11-27. Die erste Kachel einer Decke heisst
«Verfahren» und hat einen Schalter [Streifenmethode | FEM], je mit Bild;
mit FEM steht darunter die Netzweite, Vorgabe 0.5 m. Die FEM rechnet die
ganze Platte linear elastisch und ungerissen, mit E_cm und ν_c = 0.2 ihres
Betons (SIA 262:2025, 3.1.2.3.5), als dünne Platte nach Kirchhoff aus
Dreiecken DKT. Die Ergebnisse sind dieselben wie in der Streifenmethode –
m_x bis v_0, die Lagerkräfte, Schnitte, M und V der Träger, die nötigen
Biegewiderstände –, dazu die Durchbiegung w. Neues Beispiel «Kolloquium 4
nach FEM»: die Decke von Kolloquium 4 mit einem Träger T4 von
h_T = 300 mm; von 920.7 kN tragen S1 122.9, S2 260.4, S3 123.0 und L1
414.3 kN, w ist höchstens 3.9 mm, T4 hat über S2 M = −94.3 kNm.

- Das Paket `decke/fem/` schreibt alles selbst, ohne fremde Pakete: das
  Netz (eine eigene Delaunay-Triangulierung, die den Rändern, Lagern,
  Trägern und Linienlasten folgt, jede Stütze ein Knoten), das Dreieck DKT,
  das System mit dem Löser der Stabwerke (Profil, Cuthill-McKee), die
  Lasten auf den Knoten, das Glätten und die Auswertung.
- Warum DKT: es hat je Ecke nur w und die zwei Neigungen, kommt ohne
  Schubverformung aus und gibt eine gleichmässige Krümmung genau wieder
  (Patch-Test im Test).
- Geglättet wird je Sektor: an einem Lager, Träger, einer Linienlast oder
  Fuge behält jede Seite ihre Momente; nur wo die Platte durchläuft, gilt
  das Mittel der Dreiecke um einen Knoten. Die Querkräfte kommen aus dem
  Gefälle der geglätteten Momente.
- Ein Träger hat neu eine Höhe h_T (0 heisst in der Platte). In der FEM
  ist er ein Balken in der Mittelebene mit
  EI = E_cm·b·((h + h_T)³ − h³)/12, ohne Torsion; M und V sind die des
  Balkens und der Platte über b (Entscheid 10 des Plans). Sein Steg wiegt
  in beiden Verfahren mit. Liegt er auf der Fuge zweier Platten, nimmt er
  h der ersten – wie das Gewicht des Stegs.
- Was nur ein Verfahren kennt, zeigt nur dieses: Richtungen, Stufe,
  Streifenbreite, Bänder und Zonen die Streifenmethode, w die FEM. Ein
  Diagramm der anderen sagt grau «gibt es nur in der …».
- Beide Verfahren geben ihre Fälle in derselben Form (`Faelle`, `Fall` in
  `decke/rechnung.py`) und ihr Bild als `feld.Bild`; welches gilt, steht
  einmal fest (`werk.VERFAHREN`, `deckendaten._BILDER`). Bilder und Bericht
  lesen beide gleich.
- Geprüft gegen Navier (6 × 4 m, 0.25 m: w −0.6 %, m −0.1 %), die
  eingespannte Quadratplatte nach Timoshenko, die Kragplatte, einen
  Träger und Σ Lagerkräfte = Σ Lasten (`tests/test_decke_fem.py`).
- Gemessen auf der Seite: Kolloquium 4 je Rechnung 0.3 s bei 0.5 m; eine
  Decke 20 × 15 m 3 s bei 0.5 m, 0.4 s bei 1 m. Bei 1 m biegt sich die
  Navier-Platte um 10 % zu wenig. Darum bleibt 0.5 m die Vorgabe; die
  Frage steht in [[TODO]].

## 2026-11-27 · Decke: Unterzug heisst Träger

Schritt 10a des Plans vom 2026-11-27. Was in der Decke «Unterzug» hiess,
heisst jetzt «Träger» – in Oberfläche, Meldungen, Bericht und Code –, denn
er kann auch ein Überzug sein (Benutzer). Die Streifenmethode rechnet wie
bisher; im Bericht ändern nur Namen, keine Zahl.

- Damit es nicht zweierlei Träger gibt, heissen die Stücke, in die die
  Rechnung jeden Streifen zwischen seinen Lagern teilt, «Durchlaufträger»:
  `decke/traeger.py` heisst `decke/durchlauftraeger.py`, die Klasse
  `Durchlauftraeger`. Im Bericht steht «Durchlaufträger, je Meter ihrer
  Breite», die Tabelle der gezeichneten heisst «Träger» statt «Versteckte
  Unterzüge».
- Kennungen T1, T2 … statt U1, U2 …; das Werkzeug hat die Taste T statt U.
- Alte Dateien öffnen weiter: `frueher.traeger_umbenennen` macht beim Lesen
  aus der Liste `unterzuege` die Liste `traeger`, aus U1 T1 – auch dort, wo
  ein Diagramm den Träger nennt – und aus dem Zähler U den Zähler T, so dass
  keine Kennung zweimal vergeben wird. Wäre ein T1 schon vergeben, behält
  der Träger sein U1.
- Das Beispiel «Unterzug» der Querschnittsanalyse heisst weiter so: dort ist
  es die Form eines Querschnitts, kein Bauteil der Decke.

## 2026-11-27 · Bericht: Kennzahlen auch ohne Nachweis

Gefunden beim Schubfluss. Eine Querschnittsanalyse aus Stahl oder Holz ohne
Lastfall hat keinen Nachweis, aber Kennzahlen – ein IPE 300 aus S355 etwa
N_Rd = 1820 kN und M_y,Rd = 212.5 kNm. Auf dem Bildschirm standen sie, im
Bericht fehlte die Analyse ganz: die Zusammenfassung nahm nur Bauteile mit
Nachweisen. Jetzt hat jedes Bauteil eine Gruppe, das Nachweise, Kennzahlen
oder einen Schubfluss hat; der Bericht sagt «Kein Nachweis geführt.» und
zeigt darunter die Kennzahlen.

## 2026-11-27 · Querschnittsanalyse: Schubfluss in Schnitten

Schritt 9 des Plans vom 2026-11-27. Neu ist im Zeichenfenster der
Querschnittsanalyse das Werkzeug «Schnitt» (Taste X): eine Strecke quer
durch den Querschnitt, ein Pfeil zeigt auf den Teil, den sie abtrennt. Dazu
die Kachel «Schubfluss» mit eigenen Lastfällen N, V_z und M_y, einachsig um
y, je mit der Rechenwahl einer Spannung-Dehnung-Analyse. In der
Zusammenfassung steht je Schnitt und Fall der Schubfluss v und τ = v/b_i.
Beispiel Plattenbalken, Flansch 1600 × 200, Steg 400, 4 ⌀26, C30/37,
V = 400 kN, M = 500 kNm: ein Schnitt am Steg trennt 600 mm Flansch ab, 3/8
der Druckkraft, v = 210.9 kN/m, τ = 1.05 N/mm² über b_i = 200 mm. Nur die
Einwirkung, ohne Widerstand (Benutzer).

- Die Regel: v = |F′(M + ΔM) − F′(M)|/Δx mit ΔM = V·Δx und Δx = 10 mm
  (`nachweis/qa_schubfluss.py`). F′ kommt aus zwei Dehnungsebenen des
  ganzen Querschnitts, vom Faserlöser der Spannung-Dehnung-Analysen,
  gerissen. Elastisch gibt das V·S′/I (Test am I-Profil und am
  Verbundträger über der Stütze), gerissen mit festem Hebelarm β·V/z.
  Warum nicht β·V/z selbst: das braucht einen Hebelarm und gilt nur ohne
  Normalkraft; zwei Zustände des ganzen Querschnitts brauchen beides nicht.
- Was ein Schnitt abtrennt (`querschnitt/abtrennen.py`): die Flächen werden
  an der Strecke geteilt; abgetrennt ist, was auf der Seite des Pfeils
  liegt und mit dem Rest nur über die Strecke zusammenhängt. Stäbe und
  Spannglieder zählen mit ihrer Mitte, verschmierte Linien mit ihren
  Stücken. Trennt ein Schnitt nichts ab – zu kurz, neben dem Querschnitt,
  ein Kasten durch nur eine Wand –, steht er grau, die Meldung sagt warum,
  und die anderen rechnen.
- Der abgetrennte Teil rechnet auf den Streifen des ganzen Querschnitts,
  geteilt an seinen eigenen Ecken (`Querschnitt(raster=…)`). Mit eigenen
  Streifen gaben die Fuge einer Aufdopplung und ein Schnitt über dem Stahl,
  die dieselbe Druckzone abtrennen, um 0.26 % verschiedene v; jetzt
  dieselbe Zahl.
- Nimmt der Querschnitt N und M nicht auf, gibt es kein v: die Tabelle
  zeigt «–», darunter steht der Grund. Eine Grösse ohne Zahl zeigt dafür
  überall «–» statt «nan» (`Groesse.formatiert`, `als_latex`), und der
  Bericht lässt sie in der Liste der Werte weg.
- Im Bericht steht der Schubfluss unter den Kennzahlen, auch bei einer
  Analyse ohne Nachweise.
- Der Pfeil zeigt zuerst links der Zeichenrichtung; der Schalter «Pfeil»
  nennt die Richtung im Bild, «nach oben | nach unten», vom Kern.
- Im Prüfprojekt «Jeder Nachweis» hat der Träger mit Dübeln zwei Schnitte:
  einen längs der Oberkante des Profils – v ist, was die Dübel je Meter
  tragen, 706.8 kN/m im Feld – und einen in der Platte, der nichts
  abtrennt. Dazu drei Fälle, einer jenseits des Widerstands.

## 2026-11-27 · Erdbeben: ein Kern je Geschoss, Massen im Bild

Schritt 8 des Plans vom 2026-11-27. Vorher wählte man unter «Wände» jede
Wand mit ihrer eigenen Querschnittsanalyse, dazu Anzahl n, Lage 0° oder 90°
und η_EI, und jede galt über die ganze Höhe. Jetzt heisst die Kachel
«Kern»: je Geschoss eine Querschnittsanalyse mit dem ganzen Kern, allen
Wänden in x und in y, gezeichnet, wie er im Grundriss liegt (y der Analyse
ist x des Gebäudes), dazu η_EI, Vorgabe 0.5. So darf der Kern oben dünner
werden: im Turm des Prüfprojekts trägt die Winkelwand unten 250 mm, ab dem
5. OG 200 mm, und EI sinkt in x von 32 400 auf 26 400 MNm².

- Getrennte Teile eines Kerns zählen je um ihren eigenen Schwerpunkt, ohne
  Steiner-Anteil zwischen ihnen; innerhalb eines Teils bleibt er
  (`erdbeben/kern.py`, eigene Prozedur mit Herleitung). Zusammen hängt, was
  ein Stück Kante teilt (`geometrie.beruehren`); eine Ecke allein genügt
  nicht. Am Fuss trägt jeder Teil nach seinem Anteil an I, wie früher jede
  Wand. Das Wohnhaus des Beispiels steht jetzt auf einem Kern aus vier
  getrennten Wänden, jede an beiden Seiten mit ⌀12 alle 150 mm wie die
  alte Wand, und rechnet dieselben Zahlen wie vorher: T₁ = 0.356 s,
  F_d = 1975.9 kN, je Richtung tragen zwei Wände 49.9 %.
- T₁ nimmt die Auslenkung des Dachs aus dem Arbeitssatz, Geschoss für
  Geschoss mit dessen EI, genau (`erdbeben/kragarm.py`). Mit einem EI über
  die ganze Höhe gibt das die alte Formel Σ W·z²·(3H − z)/(6EI) (Test).
  Querkräfte und Momente sind mit nach `kragarm.py` umgezogen; sonst wäre
  `ersatzkraft.py` über 1000 Zeilen gewachsen.
- Auf jeder Decke sitzt ihre Masse als Kreis, die Fläche so gross wie sie,
  daneben «EG 274 t» – aus W = 2500 + 0.3 · 800 = 2740 kN. Die Massen
  stehen schon da, wenn das Gebäude noch nicht rechnet, etwa ohne Kern:
  dieselbe Regel W = G_k + ψ₂·Q_k gibt sie (`ersatzkraft.gewicht`).
- Das Bild daneben zeigt in jedem Geschoss seinen Kern, alle im selben
  Massstab, im untersten mit den Nummern der Teile; die Tabelle darunter
  nennt je Teil Anteil, V und M am Fuss – nur, wo es mehr als einen gibt.
- Die Geschosse stehen von oben nach unten wie das Gebäude, gezählt weiter
  ab der Einspannung; «+ Geschoss» steht über der Liste, wo das neue
  erscheint, und übernimmt Kern und η_EI des obersten.
- Hat ein Geschoss einen Kern, braucht jedes einen; ohne Kern in allen
  rechnet das Gebäude nur mit T₁ von Hand, wie früher ohne Wand.
- Die Einheit m⁴ ist neu: so steht der Kern in der Herleitung, 2.6042 m⁴
  statt 2 604 167 · 10⁶ mm⁴.
- Eine Datei von früher öffnet sich weiter (`projekt/frueher.py`): ihre
  Wände werden ein Kern, eine neue Analyse «Kern Wohnhaus» mit jeder Wand
  n-mal, die in 90° gedreht, nebeneinander und 1 m auseinander – getrennte
  Teile, also dieselben Zahlen; «aus den Wänden» wird «aus dem Kern».
  Ohne das hätte sich das Projekt des Benutzers im Browser nicht mehr
  geöffnet: sein Wohnhaus trug noch die Wände des alten Beispiels. Wände
  ohne Analyse fallen weg; verschiedene η_EI oder eine gelöschte Analyse
  gehen nicht ohne Rückfrage in einen Kern, die Datei meldet sich dann.
- Nebenbei: die Querkraft V steht jetzt mitten im Geschoss. Vorher stand
  sie 14 px tiefer und lag bei Geschossen um 33 px Höhe, etwa im Turm mit
  neun Geschossen, auf dem Namen der Decke darunter.

## 2026-11-27 · Durchstanzen: der Widerstand am Schnittpunkt als Kennzahl

Schritt 7 des Plans vom 2026-11-27. Vorher stand bei V_d = 0 in den Angaben
V_Rd,c = 866.7 kN (C30/37, B500B, Vorgaben, Näherungsstufe 2): mit ψ = 0 und
k_r = 2, ein Widerstand, der nur ohne Last gilt. Jetzt hat jede
Durchstanzstelle die Kennzahl «Durchstanzwiderstand am Schnittpunkt»,
im Beispiel V_Rd,c = 503.6 kN: die grösste Querkraft im Nachweisschnitt ohne
Durchstanzbewehrung, mit ψ aus derselben Stützenkraft. Sie steht in der
Karte «Kennzahlen» unter der Zusammenfassung, mit Auge und Kopierknöpfen,
auch mit Einwirkung. Der Nachweis bleibt, wie er ist; er zeigt daneben sein
eigenes V_Rd,c, mit ψ aus der eingegebenen Kraft -- darum heisst die
Kennzahl «am Schnittpunkt».

- Gesucht wird V_d mit V_d − ΔV = V_Rd,c(ψ(V_d)), durch Halbieren auf 1 N
  genau (`durchstanzen/kennzahl.py`). Links wächst mit V_d, rechts sinkt:
  es gibt genau einen Schnittpunkt. Die Herleitung zeigt V_d, m_sd, ψ, k_r
  und V_Rd,c an dieser Stelle und darunter V_d,red, gleich gross. Mit
  q_d = 10 kN/m²: V_d = 505.1 kN, ΔV = 2.7 kN, V_Rd,c = 502.5 kN.
- Geht V_d,red eines Nachweises nicht über die Kennzahl, braucht er keine
  Durchstanzbewehrung, sonst schon (Test).
- Gerechnet wird mit den Schritten des Nachweises: Schnitt, Plattenrotation
  und Widerstand stehen jetzt in `Stuetzenrechnung` (`durchstanzen/nachweis.py`),
  und die Kennzahl ruft sie bei jedem Halbieren still (`StillesProtokoll`);
  geschrieben wird nur der letzte. So können Nachweis und Kennzahl nicht
  auseinanderlaufen.
- In den Stufen 1 und 3 hängt ψ nicht von V_d ab; die Kennzahl ist dort das
  V_Rd,c des Nachweises, und die Herleitung sagt es.
- Ohne Last zeigt die Tabelle «Durchstanzen» in den Angaben nur noch d_v, u
  und k_e: ψ = 0, k_r = 2 und 866.7 kN fallen weg.
- Kennzahlen meldet ein Weg an, `Aufbau.kennzahlen_eintragen`; bis dahin
  schrieben Querschnittsanalyse und Pfahl dieselben drei Zeilen je selbst.

## 2026-11-27 · Durchstanzen ohne Last: der Grundriss sagt es auch

Aufräumen A2 des Plans vom 2026-11-27. Die Zusammenfassung sagte ohne
Stützenkraft schon seit dem 2026-11-19 «Keine Einwirkung → kein Nachweis.»;
unter dem Grundriss stand noch «V_d = 0 ≤ V_Rd,c = 866.7 kN – erfüllt,
α = ∞». Jetzt steht dort derselbe Satz.

Ob die Stütze nichts trägt, sagt der Befund (`ohne_einwirkung` in
`durchstanzen/nachweis.py`); Nachweis und Legende fragen beide ihn, damit die
Regel an einer Stelle steht.

## 2026-11-27 · Pfahl: η_a aus der Grundlage, Spitzendruck eingegeben

Schritt 6 des Plans vom 2026-11-27.

**η_a.** Vorher setzte die Grundlage nur die Obergrenze von η_a; das Feld
blieb auf 0.7, auch nach einem statischen Versuch, wo 1.0 erlaubt ist.
Jetzt wählt unter der Grundlage ein Schalter [aus der Grundlage | von Hand]:

- Aus der Grundlage ist η_a ihr Grenzwert und steht grau im Feld:
  Berechnung 0.7, Erfahrung 0.9, dynamischer Versuch 0.9, statischer
  Versuch 1.0 (SIA 267:2013, 9.5.2.2.5, (45)–(48), am Scan S. 64
  geprüft). Die Herleitung sagt in einer Annahme, dass der Grenzwert nur
  gilt, wenn R_a,k sehr zuverlässig bestimmt ist, sonst ist η_a kleiner
  (9.5.2.2.6); grau unter dem Schalter steht dasselbe.
- Von Hand ist das Feld offen und weist eine Zahl über dem Grenzwert ab:
  «η_a ist für «Berechnung» höchstens 0.7 (SIA 267:2013, 9.5.2.2.5, (48)):
  0.8 ist nicht übernommen.» Wer danach auf eine strengere Grundlage
  wechselt, sieht die Meldung von vorher: η_a = 0.95 liegt über 0.7.
- Dafür kann ein Feld der Vorgaben (`core/vorgaben.py`) nach den Wahlen
  enger begrenzt sein (`bis`, `bis_satz`) oder festgelegt (`fest`). Die
  Regel steht so an einer Stelle, `_aussen` in `pfahl/pfahl.py`: die Maske
  zeigt, was sie sagt, und die Herleitung rechnet mit derselben Zahl.
- Alte Dateien rechnen wie zuvor: ein Pfahl ohne den Schalter behält eine
  Zahl, die vom Grenzwert abweicht, von Hand (`umrechnung_setzen` in
  `projekt/frueher.py`); sonst kommt sie aus der Grundlage.

**Spitzendruck.** Ein neuer Pfahl hat den Spitzendruck eingegeben,
q_b,k = 2000 kPa, statt gerechnet. Beispiel D = 900 mm:
R_b,k = π/4 · 0.9² · 2000 = 1272 kN. Das Startbeispiel und die Pfähle von
«Jeder Nachweis» setzen «gerechnet» ausdrücklich und behalten ihre Zahlen;
ebenso die Handrechnungen der Tests.

---

## 2026-11-27 · Vorlagen: Trapez, Doppel-T, Platte mit Aufbeton, Bewehrung je Lage

Schritt 5 des Plans vom 2026-11-27.

**Bewehrung je Lage.** Vorher setzte jede Vorlage feste Stäbe, das
Rechteck etwa drei ⌀20 unten und zwei ⌀12 oben, jede Achse 50 mm vom Rand
(«Achsabstand»). Jetzt hat jede Lage einen Durchmesser und eine Teilung,
der Kreis Durchmesser und Anzahl. Statt des Achsabstands steht die
Überdeckung c_nom, Vorgabe 35 mm.

- c_nom misst bis zum äussersten Stab: mit Schubwänden bis zum Bügel, ohne
  bis zum Längsstab. Darum haben auch die Bügel ⌀ und s, Vorgabe ⌀10 und
  150 mm wie bei einer neuen Wand.
- Die Teilung ist ein Wunsch wie beim Zeichnen einer Stablinie: gerundet
  auf den nächsten Abstand, der aufgeht. Jede Lage wird eine Stablinie mit
  Teilung.
- Beispiel Rechteck b = 300 mm, c_nom = 35, Bügel ⌀10, unten ⌀20 mit
  s = 100: die Achsen liegen 35 + 10 + 10 = 55 mm vom Rand, dazwischen
  bleiben 190 mm. Unter der Lage steht «→ 3 Stäbe, Abstand 95 mm»; die
  Zahl kommt aus dem Kern, aus derselben Rundung wie die Stablinie.
- Ist «Bewehrung» aus, sind ihre Felder grau und gesperrt, ebenso die der
  Bügel ohne Schubwände, c_nom erst, wenn beides aus ist. Vorher blieben
  sie offen, ohne etwas zu bewirken.
- Passt eine Lage nicht, sagt es die Meldung mit ihrem Namen: «Die Stäbe
  unten passen nicht in den Querschnitt – Überdeckung, Bügel oder
  Durchmesser sind zu gross.» Im Kreis prüft der Kern auch, dass die Stäbe
  nicht ineinander liegen: bei D = 100 mm wären es acht ⌀16 im Abstand von
  5 mm.
- Die Schubwände enden auf der Höhe der Stabachsen, auch ohne Bewehrung.

**Drei neue Vorlagen.**

- Trapez: b oben, b unten, h. Die Lagen halten c_nom quer zur schrägen
  Kante. Die Wand ist so dick wie die engste Stelle zwischen den Lagen –
  nach Vorgabe, im [[TODO]].
- Doppel-T: Obergurt b_o und h_o, Steg b_w, Untergurt b_u und h_u, Höhe h.
  Die Wand reicht wie beim T von den Stäben unten bis in die Mitte des
  Obergurts. Eingesetzt mit den Vorgaben: unten 5 ⌀20 im Abstand 97.5 mm
  (gewünscht 100), oben 6 ⌀12 im Abstand 139.6 mm (gewünscht 150).
- Platte mit Aufbeton: b, Dicke unten h_u, oben h_o und ein zweiter Beton
  für den Aufbeton; die Platte darunter ist aus dem Material der Vorlage.
  Ohne Schubwände, wie eine Platte.

**Das Rechteck der Skripte.** `Projekt.querschnittsanalyse` und viele
Tests bauen auf dem alten Rechteck auf: 300 × 600 mm, 3 ⌀20 und 2 ⌀12, je
50 mm vom Rand. Es steht jetzt für sich, `rechteck_der_skripte` in
`querschnitt/vorlagen.py`; seine Zahlen bleiben, kein Test änderte sich.

**Woher die Felder kommen.** Masse, Lagen, Bügel und die Wahl des zweiten
Betons stehen im Katalog des Kerns; die Seitenleiste baut daraus ihre
Zeilen.

---

## 2026-11-27 · Spannglied: Erzeugnis oder Fläche, Faktoren statt Spannungen

Schritt 4 des Plans vom 2026-11-27.

**Wie viel Stahl.** Ein Schalter «Menge» [Erzeugnis | Fläche A_p].

- Erzeugnis wie bisher: Draht, Litze oder Stab mit einem Durchmesser aus
  Tabelle 7, dazu die Anzahl.
- Fläche: A_p frei in mm², dazu nur die Art, denn an ihr hängt E_p:
  195 000 N/mm² für Litzen, 200 000 für Drähte und Stäbe (SIA 262:2025,
  3.3.2.4). Zur Wahl stehen nur die Arten, die es von der Sorte gibt –
  Y1860 als Draht und Litze, Y1030 nur als Stab. Passt die Art nicht, steht
  grau am Ort «Y1030 gibt es nicht als Litze (Tabelle 7) – eine Art
  wählen.»; die Zahlen neben den Faktoren bleiben dann leer.
- Was an einem Glied fehlt, sagt eine Funktion, `was_fehlt` in
  `querschnitt/spannglieder.py`, für Aufbau und Zeichnung zugleich. Vorher
  hatten beide ihre eigene Prüfung des Durchmessers.
- A_p beginnt mit 150 mm², einer Litze ⌀15.7 wie das Erzeugnis der
  Vorgabe. Jede Stellung behält ihre Zahl; wer hin und her schaltet,
  verliert nichts (Frage im [[TODO]]).

**Faktoren statt Spannungen.** σ_p0 und σ_p∞ sind keine Felder mehr.
Eingestellt werden k_p0 = σ_p0/f_pk und k_p∞ = σ_p∞/σ_p0, je über null und
höchstens 1; das Feld weist 1.2 schon bei der Eingabe ab. Die Spannung steht
daneben, gerechnet im Kern: Y1860 mit den Vorgaben 0.70 · 1860 = 1302 N/mm²,
dann 0.85 · 1302 = 1107 N/mm².

- Die Regel «σ_p∞ höchstens σ_p0» fiel weg: k_p∞ ≤ 1 sagt dasselbe.
- Gl. (22) bleibt ein roter Hinweis. Mit der Vorgabe 0.70 schlägt er beim
  Y1030 an, 721 über 706 N/mm²; der Punkt im [[TODO]] ist auf die Faktoren
  umgeschrieben.
- Die Herleitung zeigt k_p0 und k_p∞ mit ihren Stellen, 0.725 bleibt
  0.725. Steht k_p∞ auf der Vorgabe, sagt eine Annahme, dass die Verluste
  am Bauwerk hängen (4.1.5.3) und die Vorgabe ihre Rechnung nicht ersetzt.
- Die Formel heisst «Spannung im Spannglied» statt «… nach Vorgabe»; ihre
  Theorie zog mit.

**Alte Dateien** öffnen sich weiter und rechnen wie zuvor:
`spannungen_als_faktoren` in `projekt/frueher.py` teilt σ_p0 durch f_pk
des gewählten Stahls, mit seinen Abweichungen und Überschreibungen, und
σ_p∞ durch σ_p0. Eine leere Spannung nimmt die Vorgabe wie damals. Ohne
Stahl bleibt das Glied unverändert und meldet das unbekannte Feld.

**Beispiel.** Das zweite Glied des Spannbetons hat jetzt eine eingegebene
Fläche, 280 mm² wie zwei Litzen ⌀15.3, und die Faktoren 0.73 und 0.81 statt
der Spannungen 1350 und 1100 N/mm². Damit σ_p0,2 = 1358 N/mm²,
P∞,2 = 307.9 statt 308 kN und M_Rd = 879.4 statt 879.5 kNm.

---

## 2026-11-27 · Test: ein Spannglied verdrängt den Beton

Aufräumen A3 des Plans vom 2026-11-27. Dass ein Stab den Beton an seiner
Stelle ersetzt, prüften Tests schon; für das Spannglied fehlte einer. Am
Rechteck 300 × 600 mm aus C30/37 mit vier Litzen (A_p = 600 mm²), im reinen
Druck, gleichmässig gedehnt:

- ohne Glied: N_Rd^- = −20 · 180 000 = −3600 kN;
- schlaff und ohne Verbund, das Glied trägt nichts: −20 · 179 400 =
  −3588 kN, mit dem Spannungsblock wie mit der Parabel;
- mit Vordehnung ohne Verbund zieht es P∞ = 664.02 kN dazu: −2923.98 kN.

Rechnet das Glied ohne Verdrängung, stehen −3600 kN da, und alle drei
Fälle schlagen an (`TestVerdraengt` in `tests/test_spannglieder.py`). Am
Code änderte sich nichts: das Glied gibt seine Stelle schon mit
(`Spannglied.als_bewehrung`).

---

## 2026-11-27 · Materialien: Flüssigkeit, das Wasser, ein volles neues Projekt

Schritt 3 des Plans vom 2026-11-27.

**Flüssigkeit.** Eine neue Materialart mit nur einem Kennwert, der Dichte
ρ_fl; die Raumlast γ_fl = ρ_fl · g ist ein gewöhnlicher, überschreibbarer
Kennwert. Die feste Sorte «Wasser» hat 1000 kg/m³, mit g = 10 m/s² also
10 kN/m³ – nach Vorgabe, nicht nachgeschlagen: SIA 261:2020 nennt für γ_w,k
keine Zahl (Frage im [[TODO]]). Eigene heissen FL1, FL2 …

- g steht jetzt an einer Stelle, `ERDBESCHLEUNIGUNG` in `material/basis.py`;
  Eigengewicht der Stäbe, Erdbeben und Decke nehmen es von dort.
- Das Register der Arten sagt neu, ob eine Art einen Wertesatz hat
  (`mit_satz`), ob ihre festen Sorten aus einer Norm stammen (`aus_norm`)
  und ihr Geschlecht (`geschlecht`: «Neue Flüssigkeit», «keine
  Flüssigkeit»). Vorher nahmen zwei Stellen das Holz von Hand aus, und
  «saechlich» kannte nur zwei Geschlechter.
- Das Wasser steht in keiner Norm: in der Oberfläche heisst es «Feste
  Sorte» mit der Marke «fest», nicht «Normsorte nach SIA» mit «SIA»
  (`festeSorte` in `material.js`). Sonst hätte das Werkzeug eine Normstelle
  erfunden.
- «kein …» für mehrere Arten kommt aus einer Regel, `keines` in
  `material/arten.py` und gleich in `bausteine.js`: verschiedene
  Geschlechter je mit dem eigenen Wort. Gefunden beim Bauen: der rote Satz
  hiess ««C30/37» ist kein Flüssigkeit».

**Grundbruch und Pfahl.** Statt der Zahl γ_w = 10 kN/m³ wählen sie ihr
Wasser aus den Materialien: der Grundbruch im Fenster «Boden», nur
drainiert, der Pfahl im Fenster «Grundwasser». Die Herleitung hat dafür
eine Zeile «Raumlast des Grundwassers, «Wasser»: γ_w = γ_fl = 10 kN/m³»
(`geotechnik/wasser.py`); so rechnet auch ein überschriebenes γ_fl mit.

- Dass der Boden schwerer sein muss als sein Wasser, prüfte bisher der
  Eintrag gegen seine Zahl. Jetzt prüft es der Aufbau mit dem Kennwert,
  wie das Projekt ihn rechnet (`kennwert`, `schwerer_als_wasser` in
  `aufbau/kern.py`). Dafür stehen die Materialien samt Überschreibungen
  jetzt vor den Bauteilen im Rechenwerk. Der Schnappschuss zeigt, dass
  sich dadurch sonst nichts verschiebt.
- Ein undrainierter Grundbruch braucht kein Wasser, auch nicht beim
  Löschen eines Materials (`materialien()`).

**Dateien von früher.** Alte Speicherstände müssen nicht weiter gehen
(2026-10-11), aber hier geht es ohne Rückfrage: `projekt/frueher.py` nimmt
die Zahl γ_w vor dem strengen Lesen heraus und setzt danach ein Wasser ein,
mit denselben Methoden wie in Python. Aus 10 kN/m³ wird das Wasser, aus
einer anderen Zahl eine eigene Flüssigkeit mit der Dichte dazu; gleiche
Zahlen teilen sich eine. Das Projekt «OCT Projekt» im Browser des Benutzers
bekam so sein Wasser und rechnet wie vorher.

**Neues Projekt.** Es hat von jeder Art eine Sorte: C25/30, B500B, S235,
Y1860, GL24h, SE 350 G und das Wasser. Vorher nur C25/30 und B500B.

## 2026-11-27 · Zeichenfenster: Seitenleiste, eigene Knöpfe für Profil, Blechdecke, Vorlage

Schritt 2 des Plans vom 2026-11-27.

**Seitenleiste.** Vorher lagen die Felder eines Werkzeugs in einem
schwebenden Kästchen von 224 px in der Zeichnung, das man ziehen und
zuklappen konnte; die Vorlagen hatten ein eigenes Fenster von 300 px.
Nachher stehen sie in einer Leiste rechts neben der Zeichnung, so hoch wie
sie und 280 bis 360 px breit – in allen Zeichenfenstern, auch im
Balkensystem, in der Decke und beim Durchstanzen.

- Ob die Leiste neben oder unter der Zeichnung steht, entscheidet die
  Breite des Zeichenfensters selbst, nicht die des Bildschirms: `.cad` ist
  ein Container, ab 640 px wird `.cad-mitte` ein Raster aus Zeichnung und
  Leiste. Darunter steht sie unter der Zeichnung, auf dem Handy ohnehin.
  Bei 1366 px Bildschirmbreite ist das Fenster 465 px breit, die Leiste
  also darunter; daneben im Vollbild oder ab etwa 1715 px. Die Frage
  dazu steht im [[TODO]].
- Neben der Zeichnung bekommt die Leiste `contain: size`: sie ist so hoch
  wie die Zeichnung und rollt, statt sie zu strecken.
- Heisst «Seitenleiste», nicht «Leiste»: «Leiste» sind schon die Knöpfe
  oben und die kleine Leiste neben einer Auswahl.
- Was fällt: Ziehen, Zuklappen, die gemerkte Lage (`opencivil.cad.palette`
  bleibt ungenutzt im Browser liegen), das Fenster «Vorlage» und
  `einpassen(…, frei)`, das beim Einpassen Platz für das Kästchen liess.
- `setzen(titel, bauen, schluessel)` baut den Inhalt nur, wenn sich der
  Schlüssel ändert. Vorher wurde er bei jedem Zeichnen gebaut und gleich
  wieder verworfen; dabei wanderten die zwischengespeicherten Felder einer
  Vorlage in ein Element, das nie angezeigt wurde, und fehlten nach dem
  Vollbild in der Leiste.

**Eigene Knöpfe.** «Polygon» heisst «Querschnitt zeichnen», mit einem
T-Träger mit offenem Umriss als Bild (`cad-querschnitt`; `cad-polygon`
bleibt, Decke und Durchstanzen brauchen es). Neben «Bewehrung» stehen
«Stahlprofil» (I) und «Blechverbunddecke» (D); vorher steckten beide im
Fenster «Vorlage». «Vorlage» (T) ist jetzt ein Werkzeug wie die anderen.

- Alle drei setzen an einem Punkt ein: die Masse und die Skizze stehen in
  der Leiste, der Zeiger zeigt die Teile, ein Klick setzt sie, Enter ohne
  Zahlen am Ursprung. Ein Werkzeug bringt dafür seinen Befehl selbst mit
  (`befehl(a)` neben `form`).
- Tippen ändert nur die Skizze; die Felder bleiben, der Cursor bleibt im
  Feld. Erst eine andere Wahl baut die Leiste neu.
- Der Katalog sagt für Profil und Blechdecke nur noch den Schlüssel ihrer
  Vorlage; Name und Skizze des Fensters fallen weg.

## 2026-11-27 · Oberfläche: kleinere App-Kacheln, kompakte Tabellen, das Handy

Schritt 1 des Plans vom 2026-11-27: die Seite soll kleiner und kompakter
werden, auch auf dem Handy.

**App-Kacheln.** Vorher standen drei Kacheln in einer Reihe, vier Reihen,
zusammen 396 px hoch. Nachher sind es vier je Reihe mit kleinerem Bild und
der Zahl der Einträge in der Ecke, zusammen 202 px. Eine Kachel ist nur gut
60 px breit; lange Namen brechen darum an weichen Trennstellen um
(«Quer-schnitts-analyse», «Stahl-beton-Platten», «Grund-bruch»,
«Mate-rialien»), und eine Reihe ist nur so hoch wie ihr längster Name.

- Die Regeln stehen unter `.app-wahl`: `.kachel` aus `30-eingaben.css`
  hat dieselbe Spezifität, wird später geladen und gewann sonst.
- Nur die Kacheln der Apps werden kleiner. Die Kacheln in einer App, etwa
  «Schichten» im Pfahl, zeigen einen Wert und bleiben, wie sie sind.

**Handy.** Vorher rollte nur die Liste unter den Kacheln. Die Kacheln
füllten den Bildschirm, und an die Liste kam man kaum. Nachher rollt die
ganze linke Tafel samt Kacheln; `overscroll-behavior: contain` hält die
Seite dahinter still. Das Auge der Nachweise bekommt auf dem Handy 34 px
als Fingerziel wie die anderen kleinen Knöpfe.

**Tabellen.** Nachweise und Kennzahlen teilen eine Tabelle. Vorher war eine
Zeile 38 px hoch, mit Widerstand über Einwirkung 50 px. Nachher sind es 27
und 41 px: Zeilenabstand 1.35, weniger Polsterung, das Auge 20 statt
26 px. Die Striche sind hell (`--linie`, neu in `10-grundlage.css`), der
Kopf hat 1 statt 2 px. Die Tabellen der Angaben (`table.gitter`) folgen.
Ein dunkles Thema hat die Seite nicht; es gibt also nur eine Linienfarbe.

## 2026-11-27 · Knicken und Kippen: eine Zeile je Fall, ein Bild zu ψ

Drei Wünsche des Benutzers zur Kachel «Knicken und Kippen nach SIA 263».

**Eine Zeile.** Vorher standen die Zahlen eines Falls in zwei Zeilen: oben
N und die Längen, unten die Momente mit ψ. Nachher stehen alle acht auf
einer Zeile, wie die sechs Lasten der Tragsicherheit. Dafür ist das
Fenster breiter, 712 statt 628 px: jedes Feld bleibt knapp 6 Zeichen breit,
«-10000» passt. Bei 628 px wäre schon «-1000» angeschnitten gewesen. Die
Mitte wird nur so breit, wenn der rechten Tafel 300 px bleiben, also ab
einem Bildschirm von 1366 px; sonst, im schmalen Fenster und auf dem Handy
bricht der Fall wie bisher vor den Momenten um.

- Wie viele Zahlen ein breites Fenster trägt, sagt die Kachel (`breit: 6`
  oder `breit: 8`); das Stilblatt hat je Zahl eine Breite. Die Lastfälle
  bleiben bei 628 px und rücken schon ab 1282 px auf eine Zeile.
- Den Umbruch im schmalen Fenster haben jetzt beide Listen gemeinsam
  (`schmal` in `fallzeile` und `fallkopf`). Vorher hatte nur die Lastreihe
  eine eigene Regel, mit fest drei Spalten.
- Holz hat sechs Zahlen und das Fenster der Lasten. Im Verbund sind es
  zweiachsig neun: die passen auch in 712 px nicht, dort bleibt der Umbruch
  (5 + 4). Einachsig sind es sieben, sie stehen auf einer Zeile.

**Ein Bild zu ψ.** Über den Fällen zeigt ein Bild, was ψ heisst: ein Stab
mit den Endmomenten ψ·M und M, dazu ψ = 1, 0 und −1. Daneben steht in
Worten: das kleinere Endmoment durch das grössere, mit Vorzeichen. Beim
Holz fehlt es, denn dort gibt es kein ψ.

**Eine sichere Vorgabe.** ψ = 1 war schon die Vorgabe und ist der
ungünstigste Wert: ω (49) ist damit am grössten, η (94) am kleinsten, und
im Verbund ist k (24) am grössten. Das steht jetzt im Bild, im Titel des
Felds und in der Hilfe.

---

## 2026-11-27 · Startbeispiel mit 35 mm Überdeckung

Eine Frage aus dem TODO, vom Benutzer am 2026-11-27 beantwortet: das
Startbeispiel auf 35 mm, wie jede neue Platte.

Vorher hatte die Platte des Beispiels oben und unten c_nom = 30 mm – als
einzige, damit Bericht, Formelsammlung und Handrechnungen der Tests ihre
Zahlen behielten. Nachher nimmt sie die Vorgabe von 35 mm. Jede Lage liegt
5 mm weiter innen, die untere x-Lage in d = 243.1 statt 248.1 mm. Damit
sinkt M_Rd bei N = 0 von 235.9 auf 230.6 kNm, und der Erfüllungsgrad im
Feld von 2.36 auf 2.31. Kein Urteil kippt; das Beispiel startet grün.

- Rund dreissig Handrechnungen der Tests sind nachgerechnet, jede mit
  ihrer eigenen Formel, nicht aus dem Programm abgeschrieben.
- Ein Satz stimmte nicht mehr: dass der obere Stahl im Beispiel mehr
  Widerstand bringt. Gedrückter Stahl hilft nur, wo er höher liegt, als
  der Spannungsblock ohne ihn reicht – hier 53 mm. Seit 35 mm liegt die
  obere x-Lage selbst in 53 mm: 230.5 statt 230.6 kNm. Der Test zeigt die
  Wirkung jetzt an einer Platte mit 20 mm Überdeckung oben, 232.2 statt
  230.6 kNm.
- Eine absichtlich zu dünne Platte der Bewehrungssuche war 70 mm dick.
  Zwischen zwei Überdeckungen von 35 mm bliebe da kein Platz, und sie
  wäre ungültig statt nur zu schwach. Jetzt ist sie 80 mm dick.

---

## 2026-11-27 · Alle Tests in knapp zwei Minuten

Dem Benutzer war die Wartezeit vor jedem Commit zu lang: alle Tests
nacheinander brauchten rund sechs Minuten. Weniger Tests je Commit wollte
er nicht – jeder Push veröffentlicht die Seite, und die Commits sind sein
Rückfallnetz.

Vorher lief `unittest discover` auf einem der acht Kerne. Nachher
verteilt `python3 -m tests.alle` die 111 Testdateien auf alle acht, jede
in einem eigenen Prozess, die längste zuerst: 2633 Tests in 102 statt
355 s, mit vier Prozessen 135 s. Viel schneller wird es nicht. Unter
Last brauchen alle Dateien zusammen 748 s Rechenzeit, gut 90 s je Kern;
die Hälfte der Kerne ist sparsam und langsamer, und die längste Datei
allein braucht 67 s.

- Kein fremdes Paket: `subprocess` und ein Pool von Fäden, die je auf
  einen Prozess warten.
- Wie lange eine Datei zuletzt brauchte, merkt sich `tests/.dauern.json`,
  nicht im Repo – nur für die Reihenfolge.
- Ein Test prüft, dass das Programm einen Fehlschlag, einen Absturz beim
  Import und einen Lauf ohne Tests nie als «OK» liest.

---

## 2026-11-27 · Erdbeben: rechnet neu, wenn sich eine Wand ändert

Ein Fehler, gefunden beim Planen der Wünsche vom 2026-11-27.

Vorher: Kürzte man im Haus der Tests die Analyse seiner beiden Wände von
5 m auf 2.5 m, stand beim Gebäude weiter F_d = 2970.5 kN in x statt
1050.2 kN – bis sich am Gebäude selbst etwas änderte oder die Seite neu
lud. Der Zwischenspeicher
entscheidet nach einem Abdruck, ob ein Ergebnis noch gilt: der Eintrag
selbst, alle Materialien und die Einträge, deren Werte er liest. Diese
Bezüge setzte jede App beim Bauen selbst; das Balkensystem tat es, das
Erdbeben vergass es.

Nachher nimmt jedes Bauteil seine Bezüge aus seinem Eintrag – derselben
Liste, die schon beim Löschen sagt, wer auf eine Analyse zeigt. Eine neue
App kann sie nicht mehr vergessen. Ein Test ändert die Länge einer Wand
und vergleicht das Ergebnis aus dem Speicher mit einem frisch gerechneten.

---

## 2026-11-27 · Neue Systeme und Decken: auch «GZT günstig»

Eine Frage aus dem TODO, vom Benutzer am 2026-11-27 beantwortet: eine
zweite Kombination mit 0.8 auf den ständigen Lasten, «aber dann konsequent
auch ohne Nutzlast».

Vorher bekam ein neues Balkensystem – eben wie räumlich – die Kombinationen
GZT (Eigengewicht und Auflast mit 1.35, Nutzlast mit 1.5) und GZG, eine
neue Decke nur die GZT. Wo die ständige Last entlastet – am Kragarm neben
einem Feld, gegen das Abheben eines Lagers –, fehlte der Fall mit der
kleinen ständigen Last. Nachher steht gleich nach der GZT «GZT günstig»:
Eigengewicht und Auflast mit 0.80, ohne Nutzlast. Ein Beispiel aus den
Tests, Eigengewicht 135 kN, Auflast 34 kN, Nutzlast 32 kN: die GZT trägt
1.35 · 169 + 1.5 · 32 = 276.2 kN, «GZT günstig» 0.80 · 169 = 135.2 kN.

- Die Beiwerte sind die des Typs 2 nach SIA 260:2013, 4.4.3.4,
  Tabelle 1: γ_G,sup = 1.35, γ_G,inf = 0.80. Nach der Fussnote 1 nimmt die
  ganze ständige Last den einen oder den anderen Beiwert; darum gilt 0.80
  für Eigengewicht und Auflast zusammen.
- Bestehende Systeme und Decken behalten ihre Kombinationen. Bilder zeigt
  die neue Kombination von selbst keine; man wählt sie wie jede andere.

---

## 2026-11-27 · Überdeckung: neu 35 mm

Eine Frage aus dem TODO, vom Benutzer am 2026-11-27 beantwortet: «Vorgabe
35 mm».

Vorher begannen Platte und Durchstanzen mit c_nom = 30 mm, oben wie unten –
weniger als das Grösstkorn D_max = 32 mm der Vorgabe, und weniger, als
SIA 262:2025, Tabelle 18, schon für Betonstahl in XC2 und XC3 verlangt.
Nachher beginnt jede neue Platte und jede neue Durchstanzstelle mit 35 mm.
Ein Beispiel aus dem Prüfprojekt: die Decke mit h = 300 mm und ⌀18 + ⌀12 in
der 2. Lage verliert 5 mm statische Höhe, ihr M_Rd sinkt von 235.9 auf
230.6 kNm.

- Die Zahl steht an einer Stelle, `UEBERDECKUNG` in
  `querschnitt/platte.py`; Platte und Durchstanzen lesen sie dort.
- Gespeicherte Projekte behalten ihre Zahl. Das Startbeispiel auch: es
  setzt 30 mm ausdrücklich, denn an seinen Zahlen hängen Bericht,
  Formelsammlung und viele Handrechnungen der Tests. Ebenso rechnen die
  Handrechnungen des Durchstanzens in den Tests mit 30 mm.
- Im Prüfprojekt «Jeder Nachweis» gilt die neue Vorgabe. Kein Urteil
  kippt; der Stahlpilz der zweiten Innenstütze wird grösser, 850 statt
  730 mm.

---

## 2026-11-27 · Stahl II aus SIA 269/2; f_cd bleibt gerechnet

Zwei Fragen aus dem TODO, vom Benutzer am 2026-11-27 beantwortet.

**Stahl II.** Vorher hiess er eine Sorte nach SIA 262:2025, und die
Herleitung nannte für f_yk = 345 N/mm² deren Tabelle 5 – dort steht er
nicht. Der Benutzer hat die Quelle genannt: SIA 269/2:2011, Tabelle 8
(S. 38), die Betonstähle früherer Normen. Dort stehen die Sorten II a und
II b der SIA 162 von 1956 mit f_sk = 345 N/mm², f_sd = 300 N/mm² und der
Duktilitätsklasse B; Dehnungen nennt die Tabelle für sie keine. Nachher:

- Die Herleitung nennt für f_yk «SIA 269/2:2011, 3.3.1, Tabelle 8», für
  ε_uk und ε_ud die Klasse B nach SIA 262:2025, Tabellen 5 und 9. Die
  Zahlen bleiben 5.0 % und 4.5 %, und f_yd = 345/1.15 = 300 N/mm² trifft
  f_sd der Tabelle.
- Am Material und im Fenster «Neues Material» steht die Norm, und dass
  ihre Werte nur gelten, wenn bekannt ist, wann der Stahl hergestellt
  wurde, die Sorte an ihren Rippen erkannt und der Stahl unbeschädigt ist
  (3.3.1). Das Fenster nennt die Grundlage der gewählten Sorte, nicht mehr
  eine für alle.
- Er hat die Duktilitätsklasse B, wie die Tabelle sagt; bisher hatte er
  keine. An den Nachweisen ändert das nichts.

**Festigkeiten des Betons.** f_cd und τ_cd kommen weiter genau aus den
Gleichungen (2) und (3) der SIA 262:2025. Ihre Tabelle 8 rundet, bis 1.6 %
daneben: bei C16/20 nennt sie 10.5 statt 10.67 N/mm². Der Benutzer hat das
Rechnen bestätigt.

## 2026-11-27 · Balkensystem: keine Achse, wo sie nichts ändert

Der Benutzer hat es am 2026-11-27 gewählt; gesehen am 2026-11-26.

**Vorher und nachher.** Ein Stab aus einem Rundrohr ROR 168.3 × 8 im
ebenen Balkensystem. Vorher stand im Fenster des Querschnitts der Schalter
«Biegung: um y – stark | um z – schwach», die Zeile hiess «ROR 168.3 x 8 ·
um y», und der Bericht schrieb «ROR 168.3 x 8, um y, die starke Achse».
Ein Rundrohr hat keine starke Achse, und der Schalter änderte nichts.
Nachher steht dort kein Schalter, die Zeile heisst «ROR 168.3 x 8», und der
Bericht nennt keine Achse. Ebenso beim quadratischen Rechteckrohr, beim
Vierkant- und beim Rundstahl.

**Eine Stelle.** Ob die Achse etwas ändert, sagt dieselbe Regel, die in
der Querschnittsanalyse die Drehung weglässt: sieht ein Profil um 90°
gedreht gleich aus, ist I_y gleich I_z (`drehbar` in
`stahlprofile/lage.py`). Der Querschnitt des Balkensystems fragt sie
(`biegeachse`). Die Rechnung nimmt dann I_y, und die Oberfläche bekommt die
Achse mit den Zeichendaten, nur dort, wo sie etwas ändert. Die gespeicherte
Wahl bleibt: wer zurück auf ein HEB wechselt, findet sie wieder.

**So bleibt es (Benutzer, 2026-11-27).** Drei Fragen aus dem TODO hat der
Benutzer am selben Tag beantwortet:

- Ein Stahlprofil in der Querschnittsanalyse hängt an der Mitte seines
  umschreibenden Rechtecks, nicht am Schwerpunkt.
- Ein Rechteckrohr ist ein Kasten: Gleichung (70) der SIA 263 gilt für
  jede seiner Wände, nicht nur für den Druckflansch. Ein RRK 200 × 200 × 5
  aus S355 trägt damit unter Druck 1133.1 kN statt 1296.6 kN.
- Liegt ein Stab der Querschnittsanalyse nicht ganz im Beton, steht die
  Meldung weiter zweimal da: über der Zeichnung und rot an ihr, wo ein
  Klick den Stab wählt.

## 2026-11-27 · Flachstahl: Kippen und kleine Kennwerte

Aus der Durchsicht nach HALFEN HDB; der Benutzer hat es am 2026-11-27
gewählt.

**Kippen.** Ein Flachstahl unter Biegung um die starke Achse, nicht
seitlich gehalten: das Werkzeug rechnet kein Kippen. Vorher stand als
Grund, Anhang B gelte für doppelsymmetrische Querschnitte – das las sich,
als wäre der Flachstahl keiner. Nachher sagt der Satz, wie es ist: er ist
doppelsymmetrisch, aber das Werkzeug nimmt den Wölbanteil (93) aus dem
Druckgurt nach Figur 40 (SIA 263, S. 85), und den kennt es nur bei
I-Profilen und Rechteckrohren. Für U-Profile und Querschnitte aus mehreren
Teilen bleibt der alte Satz; er stimmt dort.

**Kleine Kennwerte.** Ein Flachstahl 20 × 3 mm hat I_y = 0.0045 cm⁴. Mit
zwei Stellen stand vorher «0 cm⁴» da. Nachher haben die Momente von Flach-,
Vierkant- und Rundstahl vier Stellen; seine Masse sind frei, und ein
dünner Stahl soll nicht als null erscheinen. Die Flächen behalten zwei,
die Profile aus Tabellen auch.

## 2026-11-27 · Nachweise, die sich nicht führen lassen: grau statt rot

Aus der Durchsicht nach HALFEN HDB; der Benutzer hat es am 2026-11-27
gewählt.

**Vorher und nachher.** Platte 180 mm, Innenstütze 300 × 300 mm,
V_d = 400 kN, System HALFEN HDB: kein Anker passt in die Platte. Vorher
standen die vier Nachweise mit Durchstanzbewehrung rot mit 0.00 in der
Zusammenfassung, oben stand «4 Nachweise nicht erfüllt», und die Legende
unter dem Grundriss sagte «nicht erfüllt, α = 0.00». Nachher stehen sie
grau mit «–», oben steht «4 Nachweise nicht geführt», ohne Rot, und die
Legende nennt den Grund: «Kein HALFEN HDB passt in diese Platte. Die
Nachweise mit Durchstanzbewehrung sind darum nicht geführt.»

**Was «nicht geführt» heisst.** Damit der Nachweis überhaupt geht, fehlt
etwas: Bewehrung auf der gezogenen Seite, ein Produkt, das passt, eine
Wand in einer Richtung, ein Verfahren, das das Werkzeug rechnet. Falsch
ist dabei nichts – darum grau, nach der Regel «was nur fehlt, steht
grau». Ein Nachweis, der gerechnet wurde und nicht aufgeht, bleibt rot.

**Nachgewiesen ist es trotzdem nicht.** «Alle Nachweise erfüllt» bleibt
streng: ein nicht geführter Nachweis zählt nicht als erfüllt. Der Satz
unter den Nachweisen im Bericht unterscheidet die Fälle: «Mindestens ein
Nachweis ist nicht erfüllt.», «Nicht alle Nachweise liessen sich führen;
die übrigen sind erfüllt.» und «Kein Nachweis liess sich führen.» Die
Konsole schreibt denselben Satz.

**Eine Stelle.** Ob ein Urteil offen ist, setzt der Kern selbst: wo nichts
gegeneinander steht und der Nachweis nicht aufgeht (`NICHT_FUEHRBAR`).
Das Wort dazu – «erfüllt», «nicht erfüllt», «nicht geführt» – und der Satz
über alle stehen in `opencivil/core/nachweis.py`; Tabelle, Bericht,
Konsole, MCP und die Anzeige oben lesen sie nur. Für ausgeschaltete
Nachweise schrieb die Konsole bisher «Nicht geführt, geht aber nicht auf»;
das heisst nun «Ausgeschaltet, …», damit ein Wort nicht zwei Dinge sagt.

**Wo es sich zeigt.** Überall, wo ein Nachweis bisher als nicht führbar
endete: eine Platte ohne Bewehrung in einer Richtung, Duktilität mit
Stahl der Klasse A, ein Rundrohr der Klasse 4, Kippen und Torsion von Holz
ausserhalb des Rechtecks, Verbund ohne Zahl der Dübel oder über Figur 1,
eine Verbundstütze über λ̄ = 2, Schubwände, die eine Richtung nicht
halten, Durchstanzen ohne passendes Produkt – und das Erdbeben, wenn das
Bauwerk nicht regelmässig ist: dort gilt das Ersatzkraftverfahren nicht,
ein anderes rechnet das Werkzeug nicht. Dass die Regelmässigkeit dort grau
steht und nicht rot, hat der Benutzer am 2026-11-27 bestätigt. Im
Schnappschuss werden darum 13 Zellen von «0.00» zu «–».

## 2026-11-27 · Durchstanzen: HALFEN HDB

Aus dem Plan vom 2026-11-25, Schritt 8, letzter Teil. Der Benutzer hat am
2026-11-27 erlaubt, die Unterlage von Leviat zu holen: die
«Produktinformation Technik» zur Durchstanzbewehrung (09/2026, 12 Seiten).

**Vorher und nachher.** Innenstütze 400 × 400 mm, Platte 280 mm aus
C30/37, V_d = 800 kN. Vorher gab es zur Wahl ancoPLUS oder Bügel. Nachher
steht im Schalter [ancoPLUS | HALFEN HDB | Bügel]. Mit HDB schlägt das
Werkzeug 16 Leisten mit je 4 Ankern ⌀12 vor, 85 / 145 / 175 / 175 mm vom
Rand der Stütze, h_A = 220 mm – angeordnet wie die Bügel, aber mit Ankern.
Alle Nachweise sind erfüllt; die Druckdiagonale hält mit 2·k_r:
V_Rd,max = 867 kN.

**Was die Unterlage hergibt.** Wenig: Doppelkopfanker aus B500, die
Durchmesser 12, 14, 16, 20 und 25 mm, und den Faktor 3.5 anstelle der 2
in Gleichung (70), nach einem Gutachten von A. Kenel. Abstände, Höhen und
Regeln für die Anordnung nennt sie nicht.

**Warum die 2 und nicht 3.5.** Einen grösseren Faktor als die 2 lässt
SIA 262:2025, 4.3.6.5.9, nur zu, wo Versuche die Sicherheit zeigen – meist
mit strengeren Regeln für die Anordnung, als die Norm sie stellt. Diese
Regeln stünden im Gutachten, und es liegt nicht vor. Mit 3.5 und den
Abständen der Norm rechnete das Werkzeug womöglich zu günstig. Darum stehen
die Anker nach den Regeln der Norm (5.5.3.8, 5.5.3.9, 5.5.3.12, Tabelle
21), und es gilt die 2; die Herleitung sagt, warum. Liegen die Regeln des
Herstellers vor, ist das eine kleine Änderung (TODO).

**Bügel und HDB teilen ihre Regeln.** Was die Norm vorgibt – die
Abstände, die Grenze des Durchmessers, die 2 in (70) –, steht einmal, in
`NachNorm` (`opencivil/durchstanzen/systeme.py`). Bügel und HDB
unterscheiden sich in den Durchmessern, der Höhe, den Wörtern und dem Bild.
Die Höhe der Anker ist der Platz zwischen den Überdeckungen, auf 5 mm
abgerundet (nach Vorgabe, nicht nachgeschlagen).

**Das Bild im Schalter.** Zwei Anker mit ihren Köpfen wie bei ancoPLUS,
dazu die Montageleiste unter den Köpfen – so steht HDB auf der Schalung.

## 2026-11-27 · Vollstahl: Vierkant, Rund und Flach mit freien Massen

Aus dem Plan vom 2026-11-25, Schritt 11d, zweiter Teil. Der Benutzer hat am
selben Tag entschieden: Vierkant-, Rund- und Flachstahl bekommen keine
Tabelle, man gibt ihre Masse frei ein.

**Vorher und nachher.** Vorher kannte die Profilwahl nur Walzprofile und
Rohre aus Tabellen. Nachher stehen im Schalter der Reihen auch VKT, RND und
FL. Wer FL wählt, sieht statt einer Liste zwei Zahlenfelder, Breite und
Dicke, mit 100 und 10 mm zu Beginn; aus ihnen wird der Name «FL 100 x 10».
Ein FL 200 x 20 aus S355 trägt in der Querschnittsanalyse plastisch
M_Rd = 6.76 kNm und V_Rd = 781 kN. Als frei gezeichnetes Blech derselben
Masse waren es elastisch 4.51 kNm und keine Querkraft.

**Der Name trägt die Masse.** Ein Profil heisst wie bisher nach Reihe und
Zahlen, mit « x » dazwischen wie bei den Rohren. Der Kern liest die Zahlen
aus dem Namen und prüft sie wie ein Feld: «VKT 0» geht nicht, weil die
Seite grösser als null sein muss, und «VKT 40.0» heisst «VKT 40». Jede
Zahl steht so kurz, wie sie genau bleibt – so schreibt sie auch
JavaScript, und die Oberfläche braucht keine eigene Regel. Die Felder mit
ihren Grenzen schickt der Kern im Katalog mit. Ein falscher Name meldet
nun seinen Grund – am Profil, im Balkensystem und in der Skizze –, statt
nur «gibt es in der Tabelle nicht».

**Die Formen der Vorlagen.** Vollstahl rechnet mit dem Rechteck und dem
Kreis der Stabquerschnitte, nur in cm² und cm⁴; es gelten dieselben
Formelseiten. Der Vierkant gibt seine Seite a als b und h weiter.

**Was er rechnet, nach Vorgabe.** Vollstahl hat keine Bleche, die beulen:
er zählt in Klasse 1. Die Querkraft trägt der ganze Querschnitt, A_v = A;
SIA 263 verweist dafür auf eine Norm, die nicht vorliegt. Der Rundstahl
trägt wie das Rundrohr die Resultierende von V_y und V_z. Die Knickkurve
ist c, wie Figur 7 sie für Vollquerschnitte zeigt. Kippen rechnet der
Flachstahl nicht: den Druckgurt nach Figur 40 kennt das Werkzeug nur beim
I und beim Rechteckrohr, und die Meldung sagt das grau.

**Pfeile in Millimetern.** Ein Mass einer Vorlage kann nun sagen, um wie
viel seine Pfeile springen; beim Vollstahl um 1 mm statt um 10.

## 2026-11-27 · Warmgefertigte Rechteckrohre (RRW)

Aus dem Plan vom 2026-11-25, Schritt 11d. Der Benutzer hat am selben Tag
entschieden: den Rohrkatalog von ArcelorMittal holen, das Verkaufsprogramm
für L, INP, T und HEAA nicht – diese Reihen bleiben weg.

**Vorher und nachher.** Vorher gab es nur das kaltgefertigte Rechteckrohr
RRK. Nachher steht daneben die Reihe RRW, 481 Grössen von RRW 80 x 80 x 5
bis RRW 500 x 300 x 16. Das RRW 200 x 100 x 8 hat A = 44.75 cm² und knickt
nach Kurve a; das RRK derselben Masse hat 43.24 cm² – seine Ecken sind
runder – und knickt nach Kurve c. Bei λ̄_K = 1.0 ist χ_K damit 0.67 statt
0.54.

**Woher die Grössen.** Der Katalog «Hollow Structural Sections» von
ArcelorMittal Tubular Products Europe (2024) zeigt je Mass h × b, welche
Wanddicken lieferbar sind: als farbige Felder einer Tabelle. Zeile und
Spalte kommen aus der Textschicht, die Farbe aus der Mitte jeder Zelle im
Bild; Stichproben im Bild stimmen. Die hellen Felder sind nur die Streifen
leerer Spalten, keine zweite Art von Lieferbarkeit. Radien nennt der
Katalog keine.

**Eine Form für beide Rohre.** RRK und RRW unterscheiden sich nur in den
Radien. Die Form heisst darum neu «Rechteckrohr mit runden Ecken», und die
Reihe bringt ihre Radien mit: das RRK die der Tabelle des Benutzers, das
RRW 1.5 t und t (nach Vorgabe, nicht nachgeschlagen: EN 10210-2 liegt nicht
vor). Was ein Rohr ist – Wände, Kasten, Schubfläche, gefülltes Rohr im
Verbund –, gilt so für beide, ohne eine Stelle mehr. Die drei Formelseiten
heissen nun «… eines Rechteckrohrs mit runden Ecken»; ihre Theorie zog mit.
Im Stabwerk heisst die Form `RECHTECKROHR_GERUNDET`, weil die Vorlage mit
scharfen Ecken dort schon `RECHTECKROHR` heisst.

**Die Knickkurve kommt von der Reihe.** Figur 7 von SIA 263 trennt
warmgefertigte Hohlprofile (Kurve a) von kaltgefertigten (Kurve c). Weil
beide dieselbe Form haben, steht die Kurve nun je Reihe statt je Form; ein
Test verlangt sie für jede Reihe, die kein I-Profil ist. Die Schlankheit
der Wände misst Tabelle 5a bei jedem Rechteckrohr ohne 1.5 t je Seite, ob
kalt oder warm – dort ändert sich nichts.

**Was offen bleibt.** VKT, RND und FL mit frei eingegebenen Massen, wie
der Benutzer am 2026-11-27 gewählt hat – der nächste Schritt.

## 2026-11-27 · Blechverbunddecken nach SIA 264

Aus dem Plan vom 2026-11-25, Schritt 14d, zweiter Teil: die
Blechverbunddecke nach SIA 264:2014, 5.4, als Element der
Querschnittsanalyse.

**Vorher und nachher.** Vorher liess sich kein Profilblech zeichnen.
Nachher gibt es die Vorlage «Blechverbunddecke»: Rippen, Abstand, Höhe,
die zwei Breiten der Rippe, die Fläche des Blechs je Meter und die Dicke
der Decke; daneben zeigt eine Rippe, was jedes Zeichen meint. Eingesetzt
wird die Decke mit ihrem Beton und ihrem Blech. Fünf Rippen 60 mm hoch,
oben 120 und unten 70 mm breit, im Abstand von 200 mm, 1100 mm² je
Meter, unter 140 mm C25/30 aus SE 350 G haben d_p = 108.9 mm. Sie tragen
M_Rd = 35.2 kNm und V_Rd = 41.4 kN; mit m = 150 und k = 0.1 N/mm² über
ein Einfeld von 3 m V_L,Rd = 27.9 kN. L/d_p = 27.5 liegt über 26: ein
Hinweis sagt, dass die Durchbiegung zu rechnen wäre.

**Die Decke ist ein Element mit ihrem Beton**, nicht ein Blech unter
einem gezeichneten Polygon: so passen Beton und Blech immer zueinander,
und eine andere Rippe ändert beide. Bewehrung zeichnet man in ihren Beton
wie in jedes Polygon. Verschoben wird sie wie ein Profil, geändert im
schwebenden Fenster. Eine Analyse rechnet eine Decke; eine zweite meldet
die Zeichnung rot.

**Eine Richtung.** Die Decke trägt entlang ihrer Rippen (5.4.1.1):
gerechnet wird einachsig, mit N, M_y und V_z über die ganze gezeichnete
Breite. Die Tragsicherheit hat darum keinen Schalter «einachsig | schief»,
sondern sagt es in einem Satz. Die Spalten M_z, V_y und T stehen nur,
solange ein Lastfall dort eine Zahl hat; ein solcher Fall sagt gelb, dass
sie nicht nachgewiesen werden.

**Der Längsschub hat eine eigene Kachel.** m und k aus dem Datenblatt,
das Feld – Einfeld, Endfeld mit 0.9 L, Innenfeld mit 0.8 L – und die
Last – gleichmässig mit L_s = L/4, zwei Einzellasten mit ihrem Abstand
a – als Schalter mit Bild, darunter die Spannweite. Was fehlt, sagt die
Kachel grau, «m, k und L fehlen»; der Rest der Decke rechnet weiter.

**Unter negativem Moment zählt das Blech nicht** (5.4.3.2). Ohne
Betonstahl trägt über der Stütze nichts Zug: der Erfüllungsgrad ist null,
rot, mit dem Grund. Eine Decke von 200 mm auf hinterschnittenen Rippen
mit ⌀10 @ 150 oben trägt dort 37.0 kNm.

**Die Oberfläche.** Stahlprofil und Decke sind beide Elemente mit einem
Umriss vom Kern. Was sie teilen, steht in `qa_umriss.js`, je Art eine
Beschreibung in `UMRISSE`. Die Knöpfe neben der Auswahl – Bewehrung in
die Überdeckung, Hilfslinien als Fläche – zogen nach `qa_aktionen.js`,
damit `qa_zeichnung.js` unter 1000 Zeilen bleibt; die Beispiele des
Verbunds zogen nach `beispiele_verbund.py`.

**Formelsammlung.** Neun neue Seiten mit Theorie, verlinkt in den Themen
«Blechverbunddecke» und «Profilblechstahl»: das Prüfprojekt hat jetzt
einen Profilblechstahl, die «Blechverbunddecke» und die «Hinterschnittene
Blechdecke». Was nach Vorgabe eingebaut ist und was
noch fehlt, steht im [[TODO]].

---

## 2026-11-27 · Profilblechstahl als Material

Aus dem Plan vom 2026-11-25, Schritt 14d, erster Teil: der Stahl der
Profilbleche einer Blechverbunddecke ist ein Material wie Baustahl und
Holz. Das Blech selbst – Rippen, Fläche, m und k aus dem Datenblatt –
kommt als Element der Querschnittsanalyse.

**Vorher und nachher.** Vorher gab es unter «Materialien» keinen Stahl
für Profilbleche. Nachher gibt es «+ Profilblechstahl» mit den sechs
Sorten der SIA 264:2014, Tabelle 1, SE 220 G bis SE 550 G. SE 350 G steht
zuerst: f_yp = 350 N/mm², f_ypd = 350/1.05 = 333 N/mm². Das Bild zeigt
die Linie elastisch – ideal plastisch, wie beim Baustahl.

**Was die Norm nicht nennt.** E_a kommt über 3.1.1 aus der SIA 263, also
210 000 N/mm². Eine Grenzdehnung nennt keine der beiden Normen: die Linie
endet wie beim Baustahl bei 15 Fliessdehnungen, nach Vorgabe. Welche der
beiden üblichen Sorten, SE 320 G oder SE 350 G, zuerst steht, ist auch
eine Vorgabe.

---

## 2026-11-27 · Verbund nach SIA 264, Verbundstützen

Aus dem Plan vom 2026-11-25, Schritt 14c: die Verbundstütze nach SIA
264:2014, 5.3 – Knicken, Druck mit Biegung nach Theorie 2. Ordnung und
zweiachsige Biegung.

**Vorher und nachher.** Vorher hatte ein Querschnitt aus Baustahl und
Beton keinen Nachweis als Stab. Nachher hat er die Kachel
«Verbundstütze», wie «Knicken und Kippen» beim Stahl: die Kriechzahl φ für
die ganze Analyse, je Fall N_Ed, die Momente, ψ, die Knicklängen, den
ständigen Anteil der Normalkraft und die Länge der Stütze. Ein HEB 300
aus S355, ganz einbetoniert in 500 × 500 mm aus C30/37 mit vier ⌀20, 6 m
lang, unter N_Ed = −6000 kN, davon 60 % ständig, φ = 2, und
M_y,Ed = 200 kNm: um z knickt sie mit N_K,Rd = 6557.5 kN; um y wächst das
Moment mit k = 1.32 und der Ersatzimperfektion L/200 auf 501.4 kNm, gegen
0.9 · 0.686 · 863.9 = 533.1 kNm – Erfüllungsgrad 1.06.

**Die Art liest das Werkzeug an der Zeichnung.** Tabelle 7 kennt drei
Arten, und an der Art hängen Knickkurve, Ersatzimperfektion, die Grenzen
gegen das Beulen und der Faktor des Betons. Statt sie wählen zu lassen,
erkennt das Werkzeug sie am Querschnitt: ein einziges Profil, ganz
einbetoniert, kammerbetoniert oder als Rohr gefüllt, ohne Beton daneben.
So kann keine Wahl der Zeichnung widersprechen. Ein Verbundträger unter
seiner Platte ist keine der drei; sein Fall sagt grau, dass Tabelle 7 ihn
nicht kennt.

**Unfertig ist kein Fehler.** Ist eine Knicklänge um eine Achse mit
Moment länger als die Stütze, bittet der Fall grau um die Länge der
Stütze; liegt λ̄ über 2, sagt er grau, dass dort das vereinfachte
Verfahren endet. Ohne Druck ist er kein Fall der Stütze. Erreicht N_Ed
N_cr,eff, knickt sie aus: rot.

**Das gefüllte Rohr** rechnet seinen Beton hier mit 1.0 statt 0.85
(5.3.2.5, 5.3.4.4), unter eigenem Namen in der Formelsammlung; die
Kennzahlen bleiben bei 0.85.

**Beton auf der Wand eines Profils ist ein Fehler am Ort.** In der
Zeichnung gilt das innerste Polygon. Ein Kreis aus Beton mit dem
Aussendurchmesser eines ROR 219.1 x 8 lag darum im Umriss des Rohrs,
ersetzte seinen Stahl bis auf 81 mm² und blieb im Loch leer – ohne
Meldung. Nachher meldet die Zeichnung rot, dass das Polygon auf dem Stahl
des Profils liegt; Beton, der ein Rohr füllt, liegt ganz in seinem Loch.
Ist ein Rohr innen leer, sagt die Verbundstütze genau das, statt nur, dass
Tabelle 7 den Querschnitt nicht kennt.

**Die Oberfläche.** Mit der neuen Kachel wäre `querschnittsanalyse.js`
über 900 Zeilen gewachsen: die Fälle von Knicken und Kippen zogen nach
`qa_stabilitaet.js`, die Schalter der Fälle nach `qa_fallteile.js`.
Ständiger Anteil und Länge der Stütze stehen nur beim Verbund, die
Kipplänge dort nicht.

**Formelsammlung.** 16 neue Seiten mit Theorie, verlinkt im Thema
«Verbundstütze». Das Prüfprojekt hat dafür die «Verbundstütze» mit acht
Fällen und das «Gefüllte Rohr»; der «Verbundträger mit Dübeln» hat einen
Fall «Als Stütze», der grau sagt, dass Tabelle 7 ihn nicht kennt. Was nach
Vorgabe eingebaut ist und was noch fehlt, steht im [[TODO]].

## 2026-11-27 · Verbund nach SIA 264, Verdübelung

Aus dem Plan vom 2026-11-25, Schritt 14b: Kopfbolzendübel nach SIA
264:2014, 6.1 – ihr Schubwiderstand, der Verdübelungsgrad und die
Teilverdübelung.

**Vorher und nachher.** Vorher rechnete ein Verbundquerschnitt immer mit
voller Verdübelung, und die Herleitung sagte, dass das Werkzeug die Dübel
nicht prüft. Nachher hat er die Kachel «Verdübelung» mit dem Schalter
[voll angenommen | Kopfbolzendübel]. Mit Dübeln stehen dort ihr
Durchmesser, ihre Länge und f_u, und je Lastfall die Zahl N der Dübel bis
zum Momentennullpunkt und der Abstand L_e der Momentennullpunkte. Ein
IPE 400 aus S355 unter einer Platte 2000 × 150 mm aus C30/37, mit
Kopfbolzen ⌀19 × 125 mm: ein Dübel trägt 81.7 kN, volle Verdübelung
bräuchte 35 Dübel. Mit 25 ist η = 0.71, verlangt sind bei L_e = 12 m
0.61 – erfüllt, und der Biegewiderstand sinkt von 889.3 auf 817.4 kNm.
Mit 15 Dübeln ist η = 0.43: rot, nicht erfüllt.

**Die Dübel tragen nur den Beton ausserhalb der Profile.** Beton zwischen
den Flanschen eines Profils hängt am Steg (5.2.1.2), nicht an den Dübeln.
Das Werkzeug schneidet ihn an der konvexen Hülle des Profils ab und zählt
ihn zum Stahl, mit dem Betonstahl darin. Ohne das sah es über der Stütze
eines Profils mit Kammerbeton fast keine Kraft in der Fuge: der gedrückte
Kammerbeton hob den gezogenen Betonstahl der Platte beinahe auf.

**Wo volle Verdübelung verlangt ist.** Im Bereich negativer Momente lässt
6.1.1.6 keine Teilverdübelung zu, und (29) gilt nur für doppelsymmetrische
Profile. Ob ein Moment negativ ist, sagt im gezeichneten Querschnitt sein
Vorzeichen nicht – die Platte kann oben oder unten liegen. Das Werkzeug
sieht es daran, dass Beton und Betonstahl ausserhalb der Profile zusammen
gezogen sind oder das Moment die Seite des Betons zieht. Über der Stütze
des Beispiels verlangt es darum η ≥ 1; mit 12 Dübeln ist η = 4.10.

**Unfertig ist kein Fehler.** Fehlt einem Lastfall die Zahl der Dübel,
rechnet er mit voller Verdübelung und sagt grau, was fehlt; fehlt nur
L_e, rechnet er die Teilverdübelung und sagt grau, dass (29) L_e braucht.
Ohne Moment prüft er keine Dübel. Was nach Vorgabe eingebaut ist und was
noch fehlt – Durchbildung, Längsschub in der Platte, Zug in den Dübeln –,
steht im [[TODO]].

**Formelsammlung.** Acht neue Seiten mit Theorie, verlinkt im Thema
«Verbundquerschnitt». Das Prüfprojekt hat dafür den «Verbundträger mit
Dübeln» mit sieben Lastfällen. Nebenbei: die Angaben zum Querschnitt
schreiben y_S = 0.0 mm statt −0.0 mm.

## 2026-11-26 · Verbund nach SIA 264, Querschnitt

Aus dem Plan vom 2026-11-25, Schritt 14a: die Tragsicherheit eines
gezeichneten Querschnitts aus Baustahl und Beton nach SIA 264:2014, 5.1
und 5.2 – plastischer Biegewiderstand, Querkraft und ihr Zusammenwirken.

**Vorher und nachher.** Vorher sagte ein Querschnitt aus Baustahl und
Beton nur grau, dass das Werkzeug ihn nach SIA 264 noch nicht nachweist.
Nachher hat er die Kachel «Tragsicherheit». Ein IPE 300 aus S355 unter
einer Platte 1500 × 120 mm aus C30/37 trägt plastisch 426.5 kNm, die
Nulllinie 71.4 mm unter der Oberkante, in der Platte; mit M_Ed = 300 kNm
ist α = 1.42.

**Plastisch, mit voller Verdübelung.** Baustahl und Betonstahl fliessen
ganz, der Beton trägt nur gedrückt, mit 0.85·f_cd über die ganze
Druckzone (5.1.2.1, 4.3.2.1). Die Rechenart des Betons gilt hier nicht;
die Kachel sagt es an ihrer Stelle. Die Rechnung ist dieselbe wie beim
Stahl: Stahl und Verbund teilen sich die starr-plastische Rechnung, neu in
`opencivil/querschnitt/plastisch.py`, je Gruppe mit ihrer Zug- und
Druckfestigkeit; der Beton hat eine Zugfestigkeit von null.

**Die Klasse** misst jedes Blech an der plastischen Nulllinie des
Lastfalls. Plastisch rechnet der Verbund nur in den Klassen 1 und 2;
darüber steht der Fall grau, denn elastisch nach 5.1.2.4 rechnet das
Werkzeug ihn noch nicht. Deckt Beton im I-Profil den Flansch innen, gelten
die Grenzen der Tabelle 3, deckt er den Steg beidseits, 5.2.1.3 – die
Tabelle der Bleche nennt dann diese Stelle. Mit S420 und S460 mindert β
nach Figur 1, und gezogener Betonstahl muss in Klasse B oder C sein
(5.1.2.3). Die Querkraft trägt der Stahl allein, wie im Stahl, und über
der Hälfte von V_Rd mindert sie die Bleche, in denen sie steht (4.3.2.2).

**Was nicht in der Norm steht**, steht im [[TODO]] und in der Herleitung.
Verdübelung, Verbundstützen und Blechverbunddecken folgen als Schritte
14b bis 14d.

**Formelsammlung.** Vier neue Seiten mit Theorie und das Thema
«Verbundquerschnitt». Das Prüfprojekt hat dafür einen Verbundträger aus
S460 und damit einen zweiten Baustahl: die Beispiele der Stahlformeln
nennen jetzt den Stahl, etwa f_yd,S355.

## 2026-11-26 · Holz nach SIA 265

Aus dem Plan vom 2026-11-25, Schritt 13: die Nachweise eines gezeichneten
Holzquerschnitts nach SIA 265:2012, 4.2, mit Knicken und Kippen.

**Vorher und nachher.** Vorher sagte ein Querschnitt aus Holz nur, dass
das Werkzeug ihn noch nicht nachweist. Nachher hat er drei Kacheln:
«Feuchteklasse», «Tragsicherheit» und «Knicken und Kippen». Ein Träger
160 × 400 mm aus GL24h in Feuchteklasse 2 mit M_y = 40 kNm hat α = 1.42
nach (14); ist die Einwirkung stossartig, 1.99.

**Linear, mit den Bemessungswerten der Tabellen.** Die Nachweise rechnen
mit den elastischen Spannungen des gezeichneten Querschnitts – so verlangt
es 4.1.2 –, die Spannung-Dehnung-Analysen weiter mit dem Gesetz des Holzes,
auf Wunsch elastisch-plastisch im Druck. Die Tabellen 6 und 7 nennen
Bemessungswerte für Feuchteklasse 1 und η_t = 1; jeder Nachweis
multipliziert sie mit η = η_w·η_t (3.3.2, 3.4.2.2).

**Die Feuchteklasse gilt einmal je Analyse**, in einer eigenen Kachel mit
drei Bildern: ein geschlossenes Haus, ein Dach im Regen, Wasser. **«Stossartig»** ist ein
Schalter am Lastfall und am Fall des Stabs, «normal | stossartig», denn
η_t = 1.4 nach 2.2.6 gilt nur für Anprall, Erdbeben oder dynamische Lasten
aus dem Strassenverkehr. Die Kennzahlen rechnen ohne.

**Welche Gleichung**, sagt der Lastfall selbst: Zug (6), Druck (10),
Biegung (14), Biegung mit Zug (21), mit Druck (22); Querkraft (23),
Torsion (24), beide (25). Beim Stab je Achse (29), (37) oder (38), mit k_c
nach (30) und (31) und k_m nach (39) bis (41). Wie beim Stahl bleibt die
Normalkraft fest, und die Momente wachsen um λ, bis die Gleichung aufgeht;
in (25) wachsen Querkraft und Torsion zusammen, λ·t + λ²·v² = 1.

**Was nicht in der Norm steht**, steht im [[TODO]] und in der Herleitung:
die weiteste Faser, die Lamellen parallel zu y für k_h, τ_d als
Resultierende, Torsion und Kippen nur im Rechteck – sonst grau –, und dass
mehrere Hölzer in einem Querschnitt keinen Nachweis haben.

**Formelsammlung.** 40 neue Seiten mit Theorie, dazu die Themen
«Holzquerschnitt» und «Knicken und Kippen eines Holzstabs». Der
Trägheitsradius des Druckgurts beim Stahl und der des Holzquerschnitts
sind dieselbe Formel und darum eine Seite, «Trägheitsradius».

## 2026-11-26 · Knicken und Kippen eines Stahlstabs

Aus dem Plan vom 2026-11-25, Schritte 12c und 12d: ein Stab mit dem
gezeichneten Querschnitt, nach SIA 263:2013, 4.5, 5.1.10, 5.3.9 und
Anhang B.

**Vorher und nachher.** Vorher hatte ein Querschnitt aus Stahl nur die
Kachel «Tragsicherheit». Nachher steht daneben «Knicken und Kippen». Ein
HEM 180 aus S355 mit N_Ed = −1385 kN, M_y = −57 kNm, M_z = 7.53 kNm und
3.63 m Knick- und Kipplänge hat dort α = 1.35, massgebend (51); die linke
Seite von (51) ist 0.582, die Excel-Datei «Stabilitätsnachweise» des
Benutzers sagt 0.583.

**Ein Fall** hat die Druckkraft, die grössten Momente 1. Ordnung im Stab –
so verlangen es (50) und (51) –, je Achse das Verhältnis ψ der Endmomente
und drei Längen: L_K,y, L_K,z und L_D. Eine Länge null heisst gehalten; so
bleibt jede Länge eine Zahl, und kein Schalter steht neben ihr. ψ gilt für
ω und für η, dieselben Endmomente.

**Die Knickspannungskurve gehört zum Querschnitt**, nicht zum Fall: je
Achse eine Wahl an der Analyse, «aus dem Profil» oder a bis d, je mit dem
Bild ihrer Kurve. Aus dem Profil heisst nach Figur 7 – beim HEB 300 b um y
und c um z –, und das geht nur, wo der Querschnitt ein einziges Profil
ist (`einzelprofil`, eine Regel für Rechnung und Zeichnung). Sonst fehlt
die Kurve, und das steht grau auf der Kachel und im Fenster, mit demselben
Satz wie im Fall: `fehlende_kurven` sagt es an einer Stelle, der Kern
schickt es mit der Antwort zur Zeichnung.

**Die Rechnung** (`stahlbau/stabilitaet.py`): die Klasse im Fall wie im
Lastfall, die Widerstände nach ihr; je Achse N_cr, λ̄_K und χ_K; um die
starke Achse M_cr nach Anhang B mit η aus ψ, λ̄_D und χ_D; dann (50), beim
I-Walzprofil auch (51) – die günstigere gilt –, in Klasse 4 (62) und (63),
und wo gekippt wird immer auch (9). Wie in der Tragsicherheit bleibt die
Normalkraft, und die Momente wachsen, bis die Gleichung aufgeht.

**Was nicht in der Norm steht oder vereinfacht ist**, steht im [[TODO]]
und in der Herleitung. In Klasse 4 zählt der ganze Druckgurt, obwohl B.5
nur die mitwirkenden Teile zulässt: ohne die übrigen wäre sein
Trägheitsradius grösser, die Vereinfachung liegt also auf der sicheren
Seite. Die Begriffe der Formeln folgen der Norm: ideelle Kippspannung,
Saint-Venant- und Wölbanteil, reduzierte Kipplänge.

**Oberfläche.** Die Kachel zeigt ein I, das seitlich ausweicht und sich
verdreht. Im Fenster steht oben dieselbe Wahl «Biegung einachsig |
zweiachsig» wie in der Tragsicherheit – sie gehört der Analyse –, dann die
beiden Kurven, dann die Fälle in zwei Zeilen: oben N und die drei Längen,
unten die Momente mit ihrem ψ. Einachsig fallen M_z und ψ_z weg.

## 2026-11-26 · Tragsicherheit des Stahlquerschnitts je Lastfall

Aus dem Plan vom 2026-11-25, Schritt 12b: N, M_y, M_z, V_y, V_z und T eines
Lastfalls am gezeichneten Stahlquerschnitt, nach SIA 263:2013, 5.1 bis 5.3.

**Vorher und nachher.** Vorher rechnete ein HEB 300 aus S355 mit dem
Lastfall N_Ed = −1000 kN, M_y = 200 kNm, M_z = 50 kNm, V_z = 600 kN nur
seine Kennzahlen, und die Zusammenfassung sagte, dass das Werkzeug die
Lastfälle noch nicht nachweist. Nachher stehen je Lastfall zwei Nachweise
da: Biegung und Normalkraft mit α = 2.32 – M_Rd = 477.7 gegen
M_Ed = 206.2 kNm, der Steg wegen der Querkraft um ρ = 0.42 gemindert –
und Querkraft mit α = 1.55, 600 gegen 927.2 kN.

**Die Klasse im Lastfall.** Die Kennzahlen kennen die Klasse bei reinem
Druck und reiner Biegung; ein Lastfall liegt dazwischen. Gezählt werden die
Bleche im Zustand, in dem der Querschnitt versagt: α an der plastischen
Nulllinie bei N_Ed, ψ an den elastischen Spannungen, bei denen (54) gerade
aufgeht. Ein IPE 600 ist so bei N = −1000 kN mit M = 300 kNm in Klasse 2
(der Steg mit α = 0.74), bei N = −3000 kN mit M = 100 kNm in Klasse 3, bei
reinem Druck von 4000 kN in Klasse 4. Welche Laststufe gilt, sagt die Norm
nicht – nach Vorgabe, in [[TODO]].

**Nach der Klasse der Widerstand** (`stahlbau/widerstand.py`). Die
Normalkraft bleibt, das Moment wächst in seiner Richtung, bis es nicht mehr
geht – wie beim Stahlbeton.
- Klasse 1 und 2: genau plastisch, jeder Teil ganz gezogen oder ganz
  gedrückt an einer geraden Nulllinie (5.1.1.2, 5.1.8). Die Nulllinie dreht,
  bis das Moment in die Richtung der Einwirkung zeigt; die Suche dafür
  stand in der Interaktion des Stahlbetons und steht jetzt für beide in
  `core/suche.py` (`winkel_suchen`). Die Herleitung zeigt die Probe: je Teil
  und Zone die Kraft mit ihrem Angriffspunkt, die Summen N, M_y und M_z.
  Die Excel-Dateien des Benutzers rechnen mit (44), das auf der sicheren
  Seite liegt: beim HEB 300 bei N = −1000 kN 506.7 statt 565.6 kNm, bei
  −3000 kN 256.0 statt 296.1 kNm – das Werkzeug gibt 12 bis 16 % mehr.
- Klasse 3: (54) als Widerstand, λ auf das Moment, bis die Summe 1 ist.
- Klasse 4: (60) ebenso, mit A_eff und der Verschiebung e_N seines
  Schwerpunkts bei Druck und W_eff zur Seite, die das Moment zieht.
- Trägt schon die Normalkraft allein nicht, sagt α, um welchen Faktor sie
  kleiner sein müsste.

**Querkraft.** Je Richtung V_Ed gegen V_Rd der Kennzahlen; in einem
Querschnitt aus Rundrohren die Resultierende, wie in den Excel-Dateien.
Über der Hälfte von V_Rd tragen die Bleche, in denen die Querkraft steht,
für Normalkraft und Biegung nur noch 1 − (V_Ed/V_Rd)². Beim HEB 300 mit
V_z = 700 kN ist das genau die Minderung von (43): 36.4 kNm. In den
Tabellen der Herleitung steht der weggenommene Teil als eigene Zeile mit
negativer Kraft.

**Was fehlt, steht grau:** Torsion – SIA 263 nennt in 5.1 bis 5.3 keinen
Torsionswiderstand des Querschnitts –, Querkraft ohne Profil, ein Rundrohr
der Klasse 4 und das Interaktionsdiagramm. Knicken und Kippen kommen mit
Schritt 12c und 12d.

**Die Oberfläche.** Ein Stahlquerschnitt zeigt unter «Nachweise» nur die
Kachel «Tragsicherheit», ohne die Schubwände des Betons; welche Bauweise
er hat, sagt der Kern mit der Zeichnung. Die Werte je Baustahl
[Bemessung | charakteristisch] stehen wie beim Beton oben im Fenster.

**Daneben.** Was Kennzahlen und Nachweise des Stahls teilen – die Kennwerte
je Baustahl, die Tabellen der Klassen und der mitwirkenden Breiten – steht
einmal, in `nachweis/qa_stahl_werte.py`. Die Herleitung von I_T hat ihre
eigene Überschrift; vorher stand sie unter dem Nachweis, der zuletzt
gerechnet wurde. Die Formelsammlung hat zwölf neue Seiten zum Stahl, mit
Theorie; was Kennzahlen und Nachweis gleich rechnen, steht auf einer Seite,
gleich in welcher Klasse.

**Die Zeichnung.** Ein Querschnitt nur aus Profilen öffnete stark
vergrössert auf seinem Schwerpunkt: die Masse eines Profils kennt nur der
Kern, und «Alles zeigen» lief vor seiner Antwort, mit einem einzigen
Knoten. Jetzt passt das Fenster nach der Antwort noch einmal ein, wenn bis
dahin niemand die Ansicht bewegt hat (`umrissVollstaendig`).

**Gegen die Hand** (`tests/test_stahl_tragsicherheit.py`): der Steg in der
plastischen Nulllinie (das Moment verliert N²/(4 t_w f)), die Minderung
durch Querkraft, (54) am HEA 300, (55) und (60) am IPE 600, die
Resultierende im Rundrohr, einachsig, charakteristisch und das freie Blech
unter dem HEB 300 – je auf vier Stellen.

## 2026-11-26 · Kennzahlen des Stahlquerschnitts nach SIA 263

Aus dem Plan vom 2026-11-25, Schritt 12a: die Querschnittsklasse je Blech
und was der Querschnitt danach trägt.

**Vorher und nachher.** Vorher rechnete ein HEB 300 aus S355 in der
Querschnittsanalyse nur A, I_y und I_z, und die Zusammenfassung sagte,
dass das Werkzeug einen Stahlquerschnitt noch nicht nachweist. Nachher
stehen unter den Kennzahlen: Querschnittsklasse 1 bei Druck und je
Zugseite, N_Rd = ±5042 kN, M_y,Rd = 632.1 kNm, M_z,Rd = 294.2 kNm,
V_z,Rd = 927.2 kN und V_y,Rd = 2225.7 kN – jede mit dem Auge auf ihre
Herleitung. Die Lastfälle weist er noch nicht nach (Schritt 12b).

**Die Klasse je Blech, aus der Zeichnung.** Jede Form nennt ihre Bleche
(`stahlprofile/bleche.py`): Flansche und Steg, die vier Wände des
Rechteckrohrs, das Rundrohr als Ganzes – mit c und t für die Schlankheit
und der theoretischen Breite für die mitwirkende. Der Querschnitt
(`stahlbau/querschnitt.py`) legt je Beanspruchung die Nulllinie, plastisch
und elastisch, und liest an den Enden von c ab, welcher Teil eines Blechs
gedrückt ist: daraus α und ψ und die Grenzen der Tabellen 5a und 5b
(`stahlbau/klasse.py`). Massgebend ist das ungünstigste gedrückte Blech;
die Herleitung zeigt alle in einer Tabelle. So gilt auch ein gedrehtes
oder gespiegeltes Profil, und ein Profil neben einem anderen.

**Nach der Klasse der Widerstand.** Klasse 1 und 2 rechnen plastisch, mit
W_pl am Umriss; Klasse 3 elastisch bis zur weitesten Faser; Klasse 4 mit
dem wirksamen Querschnitt: je Blech fällt ein Streifen der gedrückten Zone
weg, wie Tabelle 10 ihn legt. Ein IPE 600 aus S355 ist bei Druck in
Klasse 4 – sein Steg hat c/t = 42.8 > 34.2 –, behält 499 von 581 mm und
trägt 4943 statt 5276 kN. Mehrere Stähle oder Dicken rechnen je mit ihrer
Fliessgrenze; die Herleitung zeigt sie in einer Tabelle statt einer
Formel.

**Was die Norm nicht regelt** (alles «nach Vorgabe» in [[TODO]]): die
Dicke, nach der Tabelle 1 wählt; die Schubflächen ausser (41a), wie in
den Excel-Dateien des Benutzers; das Rechteckrohr als Kasten mit (70);
ein Rundrohr der Klasse 4 ohne Widerstand; frei gezeichnete Flächen
höchstens in Klasse 3 und ohne Querkraft.

**Gegen die Excel-Datei des Benutzers**, HEB 800 aus S235: N_Rd 7481
gegen 7479 kN, M_Rd 2289.9 gegen 2289 kNm, A_v 16 183 gegen 16 175 mm².
V_Rd 2080.7 gegen etwa 2090 kN: die Datei rechnet τ_y = 235/√3 = 135.68,
das Werkzeug 135 N/mm² aus Tabelle 1.

## 2026-11-26 · Stahlprofile in der Querschnittsanalyse

Aus dem Plan vom 2026-11-25, Schritt 11c. Der Benutzer: ein Stahlprofil
bleibt ein Profil – man wählt Reihe und Grösse, verschiebt und dreht es;
freie Bleche zeichnet man als Fläche aus Baustahl.

**Vorher und nachher.** Vorher kannte die Querschnittsanalyse kein Profil;
ein HEB 300 hätte man als Polygon mit seinen Ausrundungen von Hand zeichnen
müssen. Nachher wählt man unter den Vorlagen «Stahlprofil», dort Reihe,
Grösse, Baustahl, Drehung und Spiegeln, und klickt den Punkt, an den seine
Mitte kommt. Ein HEB 300 aus S355 hat dann A = 14 914 mm² (die Tabelle
des Benutzers: 14 908) und rechnet wie jede Fläche.

**Ein Profil ist ein Punkt mit Fläche.** Es hängt an einem Knoten, seiner
Mitte: der Mitte des umschreibenden Rechtecks, nicht dem Schwerpunkt, der
beim U daneben liegt (zu prüfen, TODO). Seinen Umriss, samt dem Loch eines
Rohrs, schickt der Kern mit der Antwort zur Zeichnung (`profile`); die
Oberfläche schiebt ihn nur mit, wenn der Knoten wandert, bis die nächste
Antwort da ist. Das allgemeine Zeichenfenster kennt dafür Punkte mit
Fläche (`punktUmriss` des Adapters): ein Klick trifft ein Rohr in seinem
Stahl, nicht in seinem Loch; ein Rahmen wählt es wie die Ecke eines
Polygons, und die Vorschau beim Verschieben zeigt seinen Umriss.

**Gerechnet wird mit dem Umriss** (`stahlprofile/lage.py`). Die
Ausrundungen sind Vielecke mit 12 Ecken je Viertelkreis, das Rundrohr hat
96. Gegen die Formeln, mit denen das Balkensystem dasselbe Profil rechnet,
weichen A, I_y und I_z höchstens 0.44 % ab (UNP, I_z), die anderen Reihen
höchstens 0.33 %. Gegen die Werte der Tabelle des Benutzers sind es beim
UNP bis 0.9 %: dort sind sie von Hand mit drei Stellen eingetippt. Ein
Satz im Bericht sagt, wie genau der Umriss ist.

**Drehen und Spiegeln nur, wo es etwas ändert**, das sagt der Kern: ein
Rundrohr und ein quadratisches Rohr drehen sich nicht, nur das U spiegelt
sich. Erst gespiegelt, dann gedreht, gegen den Uhrzeigersinn; ein
ungespiegeltes U um 90° ist nach oben offen. Im schwebenden Fenster
stehen die vier Drehungen unter ihrem Namen, wie jede Wahl mit mehr als
zwei Stellungen dort.

**Ein Paket für beide** (`opencivil/stahlprofile/`): Formen, Tabelle und
Lage, gebraucht vom Balkensystem und von der Querschnittsanalyse. Die Wahl
ist in beiden dieselbe (`profilwahl.js`): die Reihen als Schalter mit dem
Bild ihres mittleren Profils, die Grösse als Liste. Im Balkensystem hat
der Schalter damit Bilder bekommen.

**Grau, was fehlt; rot, was falsch ist.** Ohne Baustahl steht «Profil 1:
noch kein Material gewählt.» Ein Beton als Material eines Profils ist rot,
ein Name, den die Tabelle nicht kennt, auch – mit einem Punkt an seiner
Mitte, damit man es findet.

**Am Rand.** Die Antwort zur Zeichnung sagt je Fläche ihre Tiefe statt
ihrer Eltern: ein Profil im Beton liegt über ihm, ein Beton im Rohr über
dem Rohr. Die Übersicht unter der Zeichnung hat eine Gruppe
«Stahlprofile», die Liste der Analysen nennt sie («2 × HEB 300»). Eine
lange Liste in einer Zeile des schwebenden Fensters kürzt sich, statt das
Fenster breiter zu drücken.

**Was offen bleibt.** Die Bleche je Form für die Querschnittsklasse kommen
mit Schritt 12, wenn ein Nachweis sie braucht. Die neuen Reihen (L, RRW,
HEAA, T, INP, VKT, RND, FL) brauchen eine Quelle und die Erlaubnis des
Benutzers, sie zu holen (Schritt 11d).

## 2026-11-26 · Spannung-Dehnung-Analysen für Holz und Stahl

Aus dem Plan vom 2026-11-25, Schritt 11b: ein Querschnitt aus Holz oder
aus Baustahl hat die sechs Spannung-Dehnung-Analysen wie einer aus
Stahlbeton. Seine Nachweise stehen weiter grau, darunter die Kacheln der
Analysen. Der Verbund wartet auf Schritt 14: sein Riss braucht den
ideellen Querschnitt, mit E_a/E_cm gewichtet; bis dahin sagt es ein grauer
Satz an der Stelle der Kacheln.

**Ohne Beton reisst er nicht** (`spannungsanalyse/rissfrei.py`). Ein
solcher Querschnitt hat einen Zustand: seine Linie läuft ohne Sprung und
ohne die gestrichelten Zustände I und II von null bis dorthin, wo eine
Faser ihre Grenzdehnung erreicht. Faserintegral und Suche der Ebene sind
dieselben wie beim Stahlbeton; was beide am gezeichneten Querschnitt
gemeinsam haben – die feste oder kippende Nulllinie, die Dehnung am Ende –,
steht einmal (`AmSchnitt` in `schnitt.py`).

**Vorher und nachher.** Ein Rechteck 200 × 400 mm aus C24: vorher stand
statt aller Kacheln ein grauer Satz. Nachher ist die M-χ-Linie ohne
Normalkraft eine Gerade bis 8 · W = 42.7 kNm, wo der gezogene Rand bricht.
Mit N = −300 kN und «elastisch-plastisch» fliesst der gedrückte Rand bei
44.0 kNm, und die Linie trägt weiter bis 59.4 kNm – von Hand nachgerechnet
im Test. Aus S355 fliesst er bei f_yd · W = 1803 kNm und endet bei der
Grenzdehnung kurz vor M_pl = 2705 kNm.

**Holz: linear oder auf Druck elastisch-plastisch.** Unter dem Holz steht
nur dieser Schalter, und nur in den Analysen (SIA 265:2012, 3.1.2.2); die
Nachweise rechnen linear (4.1.2). Einen Wertesatz hat das Holz nicht: die
Norm nennt Bemessungswerte, und so sagt es auch die Herleitung.

**Der äquivalente Modul misst sich am Modul des Materials:** E_0,mean beim
Holz, E_a beim Baustahl, beim Stahlbeton weiter E_cm. Solange keine Faser
fliesst, ist er dieser Modul – bis auf 0.03 %: das Faserintegral liest
jeden Streifen in seiner Mitte, und so fehlt I der Anteil 1/n² (10 997
statt 11 000 N/mm²). Hat der Querschnitt zwei Sorten derselben Art, gilt
der Modul der grössten Fläche (nach Vorgabe, im TODO).

**Wo eine Fläche fliesst, sagt ihr Gesetz** (`Gesetz.fliessbereich`):
der Baustahl bei ±f/E, das Holz plastisch bei −f_c,0,d/E. Die Grenzen
heissen nach dem Material: «Holz C24, Rand unten» – bis heute hiess jede
Fläche ausser dem Beton «Stahl». Das Bild über die Höhe läuft über die
Flächen jedes Werkstoffs, nicht mehr nur über den Beton.

**Oberfläche.** Die Legende sagt «Druck im Holz» und «Querschnitt aus
Baustahl – ohne Beton reisst er nicht», und sie nennt nur, was im Bild
steht: Riss und Fliessbeginn nur, wo die Linie einen hat, die
Bewehrungslage nur mit Bewehrung. Über dem Bild fehlt φ, wo nichts kriecht.
Den Titel des Schalters unter einem Material schreibt der Kern: beim
Baustahl «f_yd oder f_y», beim Spannstahl «f_pd oder f_p0.1k» – bis heute
hiess jeder Stahl «f_yd oder f_yk». Die Zeilen je Material haben die Farbe
ihrer Art, und ihre Überschrift heisst «Je Material» statt «Werte je
Material»: unter dem Holz steht kein Wert, sondern wie es rechnet.

**Was offen bleibt.** Ein E_eq im Balkensystem gibt es weiter nur beim
Stahlbeton. Die Linie des Holzes endet beim Bruch der Zugfaser; der
Nachweis der Biegung nach SIA 265 rechnet mit f_m,d und gäbe beim Rechteck
oben 14 · W = 74.7 kNm statt 42.7 – zu entscheiden mit Schritt 13 (TODO).

## 2026-11-26 · Flächen aus Holz und Baustahl, die Bauweise

Aus dem Plan vom 2026-11-25, Schritt 11a: eine Fläche der
Querschnittsanalyse ist aus Beton, Baustahl oder Holz. Die Liste des
Materials gliedert sie nach Art; die Zeichnung färbt Holz hellbraun und
Baustahl hellblau.

**Woraus der Querschnitt ist, sagt der Kern** (`querschnitt/bauweise.py`),
nach der Tabelle des Benutzers: Beton mit oder ohne Betonstahl und
Spannstahl ist Stahlbeton, nur Baustahl Stahl, Baustahl mit Beton Verbund,
nur Holz Holz. Eine andere Mischung rechnet nicht und sagt grau, mit den
Namen: «Einen Querschnitt aus Beton («C30/37») und Holz («C24») rechnet das
Werkzeug nicht.»

**Vorher und nachher.** Ein Rechteck 200 × 400 mm aus C24: vorher liess
die Liste nur Beton zu. Nachher rechnet es A = 80 000 mm² und
I_y = 1 066.67 · 10⁶ mm⁴, ein Stab im Balkensystem nimmt sie mit
E_0,mean, und statt der Kacheln des Stahlbetons steht grau: «Einen
Holzquerschnitt weist das Werkzeug nach SIA 265:2012 noch nicht nach.» Die
Nachweise kommen mit den Schritten 12 bis 14, die Spannung-Dehnung-Analysen
für jede Bauweise mit 11b; was in den Kacheln eingestellt ist, bleibt.
Unter «Diagramme» steht das Bild des Querschnitts in der Farbe des Holzes,
und statt «Kein Interaktionsdiagramm.» sagt derselbe Satz, warum es keines
gibt.

**Bewehrung liegt nur im Beton** – Stab, Linie, Schubwand und Spannglied
(`BEWEHRT`). Ein Stab im Holz ist rot, wie einer neben dem Querschnitt. Für
die Hilfe «Überdeckung beachten» ist eine Fläche aus Baustahl wie eine
Aussparung: hat sie eine Überdeckung, hält die Bewehrung so viel Abstand
von ihr – im Verbund vom Blech. Eine Vorlage aus Holz oder Baustahl kommt
ohne Bewehrung; ihr Fenster zeigt neu das Material, aus dem sie ist.

**Welche Arten ein Feld nimmt, steht an ihm** (`materialfeld`): der Aufbau,
die Prüfung der Zeichnung, die Liste der Oberfläche und der Zugang für
Claude lesen es dort. Bis heute stand «beton» an drei Stellen fest.

**Was andere Bauteile nehmen.** Ein E_eq gibt es bisher nur beim
Stahlbeton – es kommt aus dem gerissenen Querschnitt; bei einem aus Holz
sagt es der Querschnitt im Balkensystem. Eine Wand des Erdbebens rechnet
mit E_cm und ist aus Stahlbeton; eine aus Holz ist rot.

Eine neue Analyse verlangt ein Material für ihre Flächen, nicht mehr Beton
und Betonstahl: «Zuerst Beton, Baustahl oder Holz anlegen.»

## 2026-11-26 · Holz als Material

Aus dem Plan vom 2026-11-25, Schritt 10: unter «Materialien» gibt es Holz
nach SIA 265:2012 – Vollholz C16, C24, C30 und D30 (Tabelle 6),
Brettschichtholz GL24k bis GL36h (Tabelle 7). Ein neues Holz beginnt bei
C24, der Sorte, die Tabelle 6 hervorhebt; Kennungen h1 …, eigene H1 ….

**Bemessungswerte aus der Tabelle, nicht gerechnet.** Die Norm nennt sie
selbst, für Feuchteklasse 1 und ohne stossartige Einwirkung; der Beiwert
γ_M/η_M (Tabelle 1) steckt darin und steht nur zur Auskunft dabei.
Gerechnet aus f_m,k kämen sie nicht heraus, denn die Tabellen runden: D30
hätte 17.6 statt 17 N/mm². Was erst ein Nachweis braucht – Feuchteklasse,
«stossartig», Querdruck mit Vorholz, k_h –, kommt mit den Nachweisen
(Schritt 13) und steht im TODO.

**Die Dichte für das Eigengewicht** ist nicht die Rohdichte der Tabellen
(das 5%-Fraktil, für Verbindungen), sondern die mittlere Raumlast nach
SIA 261:2020, Tabelle 28: Nadelholz 5, Laubholz 7.5 kN/m³, mit g = 10 m/s²
500 und 750 kg/m³. So nimmt sie auch ein Stab im Balkensystem, mit
E_0,mean und im Raum G_mean.

**Das Gesetz** ist linear bis zum Bruch, auf Zug wie auf Druck. Das Bild
im Material zeigt als zweite Linie den Druck elastisch-plastisch
(3.1.2.2), bis 3·ε_c,0,d – nach Vorgabe, im TODO. Die zweite Linie war
bis heute der Spannungsblock des Betons und hiess im Code «vereinfacht»;
sie heisst jetzt «zweite», denn beim Holz ist sie keine Vereinfachung.

**«Neues Holz», nicht «Neuer Holz».** Wie ein Satz eine Art nennt, steht
neu im Register (`saechlich`): das Fenster heisst «Neues Holz», die Karte
«Eigenes Holz», das Balkensystem sagt «kein Holz» und «ein Holz des
Projekts». Bis heute stand «Neuer», «Eigener» und «keinen» fest im Text.

## 2026-11-26 · Geneigte Spannglieder in der Querkraft

Aus dem Plan vom 2026-11-25, Schritt 9c: ein Spannglied mit Vordehnung hat
eine Neigung β_p, und ihr lotrechter Anteil zählt in der Querkraft.

**Vorher und nachher.** Rechteck 300 × 600 mm, eine Schubwand in der
Mitte, V_z = 300 kN, vier Litzen ⌀15.7 aus Y1860 mit P∞ = 664 kN. Vorher
trug die Wand 300 kN, ob das Glied geneigt war oder nicht. Nachher, um 5°
geneigt: das Glied trägt 664 · sin 5° = 57.9 kN, die Wand 242.1 kN. Um −5°
geneigt wirkt es entgegen, mit seiner grössten Kraft: 300 + 834.8 · sin 5°
= 372.8 kN.

**Das Vorzeichen.** β_p > 0 heisst: die lotrechte Kraft wirkt wie ein
positives V_z. Gleich gerichtet wie das V_z eines Lastfalls trägt sie mit
P∞ mit (Gl. 50), entgegen mit der grössten Kraft im Glied (4.3.3.4.9) –
dasselbe Glied je Lastfall verschieden, wenn die Querkraft das Vorzeichen
wechselt. Ein Glied neben dem Schwerpunkt dreht dazu: das Moment seiner
lotrechten Kraft fehlt den Wänden in der Torsion.

**Warum die Einwirkung gemindert wird.** Gl. (50) legt den Anteil zum
Widerstand. Bei mehreren Wänden weiss aber keine, wie viel davon ihr
gehört; zieht man ihn von V_z ab, bevor verteilt wird, findet er seinen
Platz von selbst. An der Grenze dasselbe; der Erfüllungsgrad ist
V_Rd/(V_Ed − V_p). Im TODO zum Bestätigen, ebenso die grösste Kraft
(mit Verbund A_p·f_pd, ohne A_p·σ_p0) und die Grenze von ±20°, bis zu der
ein Glied im Biegewiderstand als längs gilt.

**Schlaff zählt die Neigung nicht** (Benutzer, 2026-11-25): dort steht die
Vorspannung samt Neigung schon in den Lastfällen. Das Zeichenfenster zeigt
das Feld β_p darum nur mit Vordehnung und sagt sonst in einer Zeile,
warum es fehlt; die Zahl bleibt am Glied für den Weg zurück.

**Was sonst dazukam.** Eine negative Zahl hinter einer Winkelfunktion steht
in der Herleitung in Klammern, «sin(−5°)» statt «sin −5°» – die Regel in
`opencivil/core/latex.py` gilt für jede Formel. Das Bild des Schubflusses
nennt den Anteil der Glieder, die Liste im Zeichenfenster ihre lotrechte
Kraft. Der Träger «Spannbeton» des Prüfprojekts hat einen Kasten aus
Schubwänden und einen Lastfall «Auflager»: ein Glied trägt mit, eines wirkt
entgegen und dreht, das schlaffe zählt nicht – zusammen V_p = 31.5 kN.

---

## 2026-11-26 · Spannglieder in der Querschnittsanalyse

Aus dem Plan vom 2026-11-25, Schritt 9, zweiter Teil: neben «Bewehrung»
setzt ein Werkzeug «Spannstahl» Spannglieder in den Querschnitt, und jede
Rechnung über die Fasern nimmt sie mit – Tragsicherheit, Gebrauch, Knicken,
Kennzahlen und die Spannung-Dehnung-Analysen.

- Vorher kannte ein gezeichneter Querschnitt nur Betonstahl. Nachher setzt
  ein Klick ein Glied, und an ihm steht alles, wie beim Stab: der
  Spannstahl, das Erzeugnis (je Art eine Zeile mit den Durchmessern aus
  Tabelle 7), die Anzahl, die Wirkung [Vordehnung | schlaff] mit Bild,
  σ_p0 und σ_p∞ (leer gilt die Vorgabe, ihre Zahl steht grau im Feld) und
  der Verbund [mit | ohne]. Gezeichnet wird ein Kreis mit der Fläche des
  Glieds; die Liste unter dem Fenster nennt P∞, das Bild des Querschnitts
  und das Bruchbild zeigen die Glieder.
- Das Beispiel von Hand (`tests/test_spannglieder.py`): Rechteck
  300 × 600 mm aus C30/37 ohne Betonstahl, vier Litzen Y1860 ⌀15.7 bei
  d = 500 mm, gerechnet mit dem Spannungsblock. A_p = 600 mm²,
  σ_p∞ = 0.85 · 0.70 · 1860 = 1106.7 N/mm², ε_p = 5.68 ‰, P∞ = 664 kN.
  M_Rd mit Vordehnung 359.3 kNm, schlaff 83.0 kNm, ohne Verbund 295.3 kNm,
  schlaff ohne Verbund null. Das Rissmoment steigt mit der Vorspannung von
  47.5 auf 246.7 kNm.
- Drei Gesetze (`opencivil/querschnitt/spannglieder.py`): mit Vordehnung
  und Verbund das Gesetz der Figur 17, um ε_p verschoben (4.1.5.1.5);
  schlaff mit Restfestigkeit dasselbe, um σ_p∞ gesenkt (4.1.5.5.2); ohne
  Verbund die feste Spannung σ_p∞ (4.1.5.1.6), schlaff null. Jedes Glied
  bekommt im Faserlöser einen eigenen Werkstoff; seine Dehnungsgrenze heisst
  wie das Glied.
- Die Werte eines Glieds leitet eine Prozedur `Spannglieder` her, und die
  Nachweise lesen sie aus dem Rechenwerk. Das Zeichenfenster bekommt
  dieselben Zahlen: die Antwort zur Zeichnung steht jetzt in
  `opencivil/web/zeichengeometrie.py` (aus `api.py` gezogen, das sonst an
  tausend Zeilen gekommen wäre) und rechnet die Prozedur in einem kleinen
  Rechenwerk. Ein fehlendes Erzeugnis ist grau; σ_p0 über Gleichung (22)
  oder σ_p∞ unter 0.45·f_pk (4.1.5.2.3) ist rot, gerechnet wird trotzdem.
- Die Nachweise: die Duktilität führt mit Spannstahl in der Zugzone keinen
  Nachweis über x/d (4.1.4.2.5). Sprödes Versagen, Zwängung auf Biegung
  und die Spannung-Dehnung-Analysen nehmen das Rissmoment mit der
  Vorspannung (4.3.1.2; 4.4.3.2.4); es reisst die Ecke, an der am wenigsten
  Druck aufzuheben ist. Die Zwängung auf Normalkraft zählt die Glieder noch
  nicht, ein Hinweis sagt es. Die Stahlspannungen im Gebrauch gelten nur
  dem Betonstahl; ohne ihn steht «Ohne Betonstahl → kein Nachweis.» –
  vorher «Ohne Bewehrung …», auch bei der Platte.
- Ohne Last ist ein vorgespannter Querschnitt nicht spannungslos: der
  Faserlöser nimmt die Ebene null nur noch, wenn sie im Gleichgewicht ist,
  und die Linien der Spannung-Dehnung-Analysen beginnen bei der Krümmung,
  die die Vorspannung allein weckt.
- Das Prüfprojekt «Jeder Nachweis» hat eine dritte Analyse, «Spannbeton»,
  mit je einem Glied in jedem Gesetz; daraus stammen die neuen Seiten der
  Formelsammlung, eine je Grösse.
- Nebenbei im Zeichenfenster: ein leeres Nachbarfeld begrenzte ein Feld wie
  eine Null – mit leerem σ_p0 wies σ_p∞ jede Zahl ab. `grenzeVerletzt`
  (`web/js/dom.js`) überspringt es jetzt.
- Gespeicherte Analysen bekommen beim Öffnen eine leere Liste
  `spannglieder`.
- Offen ([[TODO]]): die Vorgabe bei Y1100 und Y1030, die schon über
  Gleichung (22) liegt; die Vordehnung ohne die Stauchung des Betons; die
  Zwängung auf Normalkraft; der Spannungszuwachs nach 4.4.2.3.10; die
  Neigung β_p (Schritt 9c) und das Hüllrohr nach Gleichung (44).

## 2026-11-26 · Spannstahl als Material

Aus dem Plan vom 2026-11-25, Schritt 9, erster Teil: unter «Materialien»
gibt es neben Beton, Betonstahl und Baustahl den Spannstahl.

- Vorher: kein Spannstahl. Nachher: «Spannstahl hinzufügen» bietet Y1860,
  Y1770, Y1670, Y1570, Y1230, Y1100, Y1050 und Y1030 an, in der Folge der
  Tabelle 10; Normsorten heissen sp1 …, eigene SP1 ….
- Kennwerte: f_pk und f_p0.1k aus Tabelle 7, E_p = 200 GPa für Drähte und
  Stäbe und 195 GPa für Litzen (3.3.2.4), γ_s = 1.15, ε_ud = 2 %
  (Tabelle 10), f_pd = f_p0.1k/γ_s nach Gleichung (5) – ungerundet, für
  Y1860 1391 statt der 1390 der Tabelle, wie f_yd beim Betonstahl.
- Die Erzeugnisse je Sorte stehen im Material unter «Erzeugnisse»: Drähte,
  Litzen und Stäbe mit Durchmesser, Fläche und Bezeichnung, etwa Litze
  15.7 mm, 150 mm², Y1860S7-15.7. Daraus wählt ein Spannglied, der zweite
  Teil des Schritts; die Fläche kommt aus der Tabelle, nicht aus π·d²/4.
- Das Bild: Figur 17, nur Zug, ideal plastisch (4.2.3.5) – für Y1860 bis
  1391 N/mm² bei 6.96 ‰, dann waagrecht bis 20 ‰. Gezeichnet mit dem Modul
  der Drähte und Stäbe; wo eine Sorte auch Litzen hat, sagt ein Hinweis,
  dass sie flacher ansteigen und ab 7.13 ‰ fliessen. Gedrückt trägt der
  Spannstahl nichts, nach Vorgabe (TODO).
- Die Linien der Materialien stehen jetzt in `opencivil/web/werkstoffkurven.py`
  statt in `diagrammdaten.py`, das sonst an tausend Zeilen gekommen wäre.
  Die Liste der Bereiche im Notizbuch (`formelseiten.BEREICHE`) nimmt die
  Materialarten aus `material/arten.py`, statt sie von Hand zu nennen.

## 2026-11-26 · Durchstanzen: Bügel und die Leiste im Bild

Aus dem Plan vom 2026-11-25, Schritt 8: die Durchstanzbewehrung hat eine
eigene Kachel mit der Wahl des Systems, [ancoPLUS | Bügel], und unter
«Diagramme» steht neben dem Grundriss eine Leiste in der Ansicht.

- Vorher gab es nur ancoPLUS, und c_v stand in der Kachel «Platte». Nachher
  wählt die Kachel «Durchstanzbewehrung» das System; c_v steht dort und
  heisst nach System und Platte «Ankerköpfe von unten» oder «Bügel von oben».
- Beispiel, Innenstütze 400 × 400 mm, h = 280 mm, C30/37, V_d = 800 kN: mit
  ancoPLUS 16 × DX4-0215, Anker ⌀10 bei 85/140/140/175 mm; mit Bügeln
  16 Linien zu 4 Schenkeln ⌀8 bei 85/145/175/175 mm, 220 mm hoch. Beide
  erfüllen alle vier Nachweise. Bei 1000 kN hält ancoPLUS um einen
  ZEUS-Pilz, mit dem Faktor seines Gutachtens bis 3·k_r; die Bügel nicht:
  für sie gilt in (70) die 2 der Norm (4.3.6.5.9), und der Hinweis sagt es.
- Die Regeln je System stehen in `opencivil/durchstanzen/systeme.py`: welche
  Durchmesser, wie hoch, welche Abstände, k_sys, der Stahl und die Wörter
  der Herleitung. Die Bemessung (`bewehrung.bemessen`) und der Nachweis
  laufen über das gewählte System; die Anordnung um die Stütze ist für alle
  dieselbe. Was bei den Bügeln nach Vorgabe gewählt ist, steht im TODO.
- Das Bild (`web/js/ds_ansicht.js`): die Leiste mit den meisten Elementen,
  längs geschnitten und massstäblich – Platte, Zugbewehrung, Stütze (bei
  der Bodenplatte oben), ein Pilz, die Anker mit Köpfen oder die Bügel mit
  ihren Biegungen; hinterlegt der Bereich 0.35·d_v bis d_v, in dem sie
  zählen; bemasst die Abstände, c_v, h_A, c und h. Alle Masse kommen aus
  dem Kern (`durchstanzdaten._ansicht`), die Lagen der Zugbewehrung aus dem
  Befund des Nachweises.
- HALFEN HDB fehlt noch: die Unterlage von Leviat hole ich erst nach deinem
  Ja.

## 2026-11-26 · Baustahl: Gesetz und Bild

Aus dem Plan vom 2026-11-25, Schritt 7: der Baustahl hat eine
Spannung-Dehnung-Linie, elastisch – ideal plastisch, in Zug und Druck
gleich (`Baustahlgesetz` in `opencivil/querschnitt/werkstoffgesetz.py`).

- Vorher zeigte «Diagramme → Werkstoffe» für einen Baustahl nichts. Die
  Stelle kannte nur Beton und «sonst Betonstahl»; dem Baustahl fehlten
  dessen Kennwerte, und der Fehler wurde still übergangen.
- Nachher, für S355: f_yd = 355/1.05 = 338 N/mm² (SIA 263:2013, 4.1.1
  mit γ_M1 nach 4.1.3), ε_yd = 1.61 ‰, die Linie endet bei ε_ud = 25.4 ‰.
  Beide Werte stehen auch unter den Kennwerten des Materials.
- Die Grenzdehnung ist nach Vorgabe, nicht nachgeschlagen (im TODO): die
  Norm nennt keine. Gewählt sind 15 Fliessdehnungen – so viel verlangt
  3.2.2.4 mindestens für die plastischen Verfahren, gegen das Seitenbild
  geprüft.
- Welche Linie ein Material hat, sagt jetzt seine Art an einer Stelle
  (`KURVEN` in `opencivil/web/diagrammdaten.py`); ein Test verlangt eine
  Linie für jede Art. Spannstahl und Holz kommen dort dazu.
- Noch rechnet keine Querschnittsanalyse mit Baustahl; das Gesetz wartet
  auf Schritt 11.

## 2026-11-26 · Decke: Bänder von selbst

Aus dem Plan vom 2026-11-25: bei automatischer Aufteilung legt die
Rechnung selbst Bänder – versteckte Unterzüge, so breit wie das neue Feld
«Breite der Bänder» der Decke, Vorgabe 1 m (`opencivil/decke/baender.py`).

- Vorher, ein Feld 6 × 5 m auf Wänden unten, rechts und links, oben frei:
  alles spannte 6 m in x, und die untere Wand trug 0 kN. Nachher liegt
  innen am freien Rand ein Band von Wand zu Wand; die Streifen in y liegen
  auf ihm, und die untere Wand trägt 90 von 300 kN.
- Vorher, eine Flachdecke 8 × 8 m auf vier Eckstützen: 86 % der Last
  fielen aus. Nachher liegen vier Bänder innen an den Rändern, von Stütze
  zu Stütze, und jede Stütze trägt 160 kN, ein Viertel.
- Wo: durch jede Stütze in den zwei Richtungen ihrer Platte, über weitere
  Stützen hinweg bis zur nächsten Wand oder zum nächsten Unterzug quer
  dazu – steht die Stütze am Rand, rückt das Band nach innen, bis es ganz
  in der Platte liegt; und innen an jedem offenen Rand – frei, an einem
  Loch, an einer Platte mit anderen Richtungen –, beidseits bis zum
  nächsten Lager.
- Abweichungen vom Plan, damit die Rechnung nicht schlechter trägt als
  ohne Band:
  - Ein Band am Rand nur, wo die Streifen quer zum Rand schon ein Lager
    haben. Eine Platte 4 × 2 m zwischen zwei Wänden bekäme sonst oben und
    unten ein Band, und die zwei nähmen ihr die ganze Last ab.
  - Nie als Kragarm: ein Band liegt auf zwei Lagern oder mehr, die die
    Höhe halten. Auf einer eingespannten Wand trägt die Platte selbst.
  - Die Bänder liegen unter jedem Unterzug des Benutzers: ein Band liegt
    auf einem Unterzug, nie trägt es einen. Vorher hätte ein Band über
    einer Stütze (Stufe 2) einen Unterzug der Stufe 1 getragen.
  - Nie längs über einer Wand: dort endet das Band, wo die Wand beginnt.
    In «Jede Wahl» liefe das Band über S1 sonst 3 m auf der Wand L4.
- Die Herleitung nennt die Bänder in einer eigenen Tabelle «Bänder, von
  der Rechnung gelegt», mit der Regel; im Grundriss stehen sie fein
  gestrichelt. Was an einer Stelle bleibt, wie über Eck auf zwei Wänden,
  sagt weiter die Meldung, wie bisher.
- Lage, Breite und Rang der Bänder sind nach Vorgabe, nicht nachgeschlagen
  (im TODO): die Norm lässt jede Aufteilung zu, die im Gleichgewicht ist
  (SIA 262:2025, 4.1.4.2.2).

## 2026-11-26 · Decke: ein Streifen knapp neben seinem Lager

Beim Prüfen der Richtungen gefunden, ein Fehler von früher.

- Vorher hielt die ganze Decke an mit «Der Träger steht nicht im
  Gleichgewicht», wenn ein Streifen nur ganz wenig über sein erstes oder
  letztes Lager ragte. Zwei Beispiele: ein Rechteck, dessen eine Ecke bei
  x = 6.00001 statt 6 m liegt, oder eine um 30° gedrehte Platte mit
  Koordinaten, auf 0.1 mm gerundet. Es fehlten 48 N oder 5.5 kN.
- Der Grund: jedes freie Ende war ein eigenes Element des Balkens, auch
  eines von einem Mikrometer. So kurz ist es fast starr; die Zerlegung
  hielt seinen Knoten darum still fest, wie ein Lager, das es nicht gibt,
  und die Lagerkräfte stimmten nicht mehr. Ebenso zwei Wechsel der
  Steifigkeit 1 mm nebeneinander.
- Nachher ist ein freies Ende statisch bestimmt: seine Last geht als Kraft
  und Moment an das erste oder letzte Lager (`traeger._resultante`). Ein
  Wechsel der Steifigkeit näher als 1 cm an einem Lager oder einem anderen
  Wechsel gilt dort (`WECHSEL`, nach Vorgabe, im TODO). Beide Beispiele
  rechnen, und die Lager tragen die ganze Last.
- Im vollen Beispiel des Berichts ändert sich nur eine Rundung: das
  grösste Moment von U2 liegt genau bei 2.475 m und steht nun als 2.48
  statt 2.47.

## 2026-11-26 · Decke: Richtungen von selbst

Aus dem Plan vom 2026-11-25: jede Platte wählt ihre zwei Richtungen selbst,
entlang ihrer Ränder, mit einem Schalter je Platte [automatisch | von Hand].

- Vorher hatte jede Platte 0° und 90°, bis der Benutzer andere Winkel
  tippte. Eine um 30° gedrehte Platte trug damit in x und y, schief zu
  allen Rändern. Nachher trägt sie von selbst in 30° und 120°, und das
  Fenster der Platte sagt unter «automatisch»: «Entlang der Ränder:
  Richtung 1 30°, Richtung 2 120°.»
- Die Regel (`opencivil/decke/richtungen.py`): Richtung 1 läuft parallel
  zu den meisten Metern Rand, ein Rand quer dazu zählt mit. Platten, die
  aneinanderstossen, wählen gemeinsam, damit die Streifen über die Fuge
  laufen; die Fuge selbst zählt nicht. Eine Platte von Hand ändert nichts
  an denen daneben – sonst änderte der Schalter an einer Platte still
  die Rechnung der anderen.
- Abweichung vom Plan: geplant war der nach Länge gewichtete Mittelwert
  der Randrichtungen. Ein Trapez, unten 6 m, oben 4 m, 5 m hoch, läge
  damit auf −4.9°, schief zu jedem Rand; nach den meisten Metern trägt es
  in x und y.
- «von Hand» beginnt mit den Richtungen, die die Rechnung gewählt hatte:
  der Schalter allein ändert nichts.
- Zwei Richtungen von Hand, weniger als 5° auseinander – auch 0° und 178°
  –, weist schon das Feld ab, mit demselben Satz wie die Prüfung vor dem
  Rechnen (`Bereich.quer_zu`). Bis heute hielt erst die Zerlegung die
  Rechnung an.
- Dateien von früher: eine Platte ohne den Schalter und mit 0° und 90° –
  der alten Vorgabe – wählt nun selbst; mit anderen Winkeln bleiben sie
  von Hand (`DeckenplatteEintrag.ergaenzt`, aus `lesen` gerufen). Ebenso
  ohne Maske: wer einen anderen Winkel angibt, meint ihn.
- Die Herleitung sagt nach der Tabelle der Platten, welche ihre Richtungen
  selbst wählen und nach welcher Regel. Keine Zahl der Beispiele ändert
  sich: ihre Platten liegen in x und y, die schiefe in «Jede Wahl» bleibt
  von Hand.

## 2026-11-26 · Decke: «trägt nicht», und warum

Aus dem Plan vom 2026-11-25: was auch mit Bändern nicht trägt, sagt die
Decke grau am Ort, und der Rest rechnet.

- Vorher zeigte die Lastaufteilung eine Platte nur auf zwei Wänden über
  Eck als «je zur Hälfte», und rot stand «Platte P1: an 480 Stellen trägt
  keine der beiden Richtungen – dort fehlt ein Lager oder ein Unterzug.»
  Nachher ist sie grau, die Legende sagt «trägt nicht – es fehlt ein
  Lager», und grau an der Platte: «Platte P1: auf 30.00 m² trägt keine
  Richtung – in x liegt sie nur auf «L2», und nichts hält ihre Drehung; in
  y liegt sie nur auf «L1», und nichts hält ihre Drehung. Dort fällt die
  Last aus; es fehlt ein Lager oder ein Unterzug.» Fläche statt Zahl der
  Zellen: die sagt dem Benutzer etwas.
- Fest und Zonen bleiben, wie eingegeben. Gibt eine davon Last in eine
  Richtung, die nicht trägt, sagt es die Meldung: «auf 8.00 m² gibt die
  feste Aufteilung 70 % der Last in y, aber in y liegt sie auf nichts –
  dieser Teil fällt aus.» Eine Zone gilt dafür in den Zellen, deren
  Schwerpunkt in ihr liegt – wie die automatische Aufteilung je Zelle
  entscheidet.
- Die Last solcher Stellen geht weiter je zur Hälfte in die Streifen und
  fällt dort aus; die Probe zählt sie als nicht getragen, wie bisher.
- Auch «… Streifen tragen nicht – … fallen aus.» je Fall ist jetzt grau:
  es fehlt ein Lager, nichts ist falsch (Arbeitsweise, 2026-11-19).
- Warum ein Träger nicht trägt, steht einmal, in `Traeger.warum_nicht`
  (vorher `rechnung._warum`), in drei Wendungen: für einen Streifen, für
  mehrere und für die Platte. Die Aufteilung rechnet dafür zuerst alle
  Zellen mit der Lage ihres Schwerpunkts (`Zelle`), in beiden Arten der
  Aufteilung.

## 2026-11-26 · Decke: die Mitte eines Felds teilt fliessend

Vom Benutzer entschieden (2026-11-25), der erste Teil des Lastabtrags von
selbst.

- Vorher ging die Mitte eines Felds ganz in die kürzere Spannweite, und
  nur wenn beide innerhalb 1 % gleich lang waren, je zur Hälfte. Ein Feld
  5 × 5.04 m teilte also halb-halb, eines 5 × 5.06 m alles in die 5 m:
  ein Sprung um die halbe Last für 2 cm. Nachher teilt sie geradlinig, je
  zur Hälfte bei gleichen Spannweiten, ganz in die kürzere ab dem
  Verhältnis 1.5: 5 × 5.04 m gibt 50.8 % in die 5 m, 5 × 5.06 m 51.2 %,
  4 × 5 m 75 %.
- Am Rand bleibt alles wie auf Folie 31: näher als ein Viertel der
  kürzeren Spannweite an einem Lager geht die Last zu ihm, in den Ecken je
  zur Hälfte. Folie 31 selbst (8 × 4 m, Verhältnis 2) gibt dieselben
  Momente wie vorher.
- Die Regel steht in `aufteilung.in_der_mitte`, das Verhältnis als
  `GANZ_AB`; die Herleitung schreibt sie als Gleichung mit derselben Zahl.
  `GLEICHE_SPANNWEITE` fällt weg.
- In der Beispieldecke «Jede Wahl» spannt die Mitte von P1 6 m in x und
  7 m in y: dort gehen jetzt 2/3 in x statt alles, und die eingespannte
  Wand L2 trägt im Eigengewicht 59.2 statt 61.8 kN/m. Kolloquium 4 teilt
  fest und bleibt gleich.

## 2026-11-26 · Erdbeben: Bild «Wände, Querkraft und Moment»

Vom Benutzer gewünscht (2026-11-25): je Geschoss der Kern, dazu V und M
über die Höhe.

- Vorher zeigte das Erdbeben unter «Diagramme» nur die Ansicht mit den
  Kräften je Geschoss und die Querkraft als Zahl daneben; das Moment gab es
  nur am Fuss (M_0). Nachher steht darunter ein zweites Bild in derselben
  Höhe: links je Geschoss die Wände im Grundriss, daneben je Richtung die
  Querkraft V als Treppe und das Moment M des Kragarms, im Beispiel des
  Wohnhauses unten 1976 kN und 17 065 kNm, unter dem Dach 647 kN und
  1940 kNm (= 647 kN · 3 m). Die Tabelle «Kräfte je Geschoss» der
  Herleitung hat dafür die Spalte M.
- M unter einem Geschoss rechnet `ersatzkraft.momente`, neben
  `querkraefte`: die Kräfte darüber, je mal ihr Abstand zur Decke darunter.
  Das Kippmoment M_0 ist jetzt dessen erster Wert, nicht mehr eine eigene
  Summe – eine Regel, eine Stelle; der Test prüft beides.
- Die Wände haben keinen Ort im Grundriss (entschieden im Plan vom
  2026-11-25): sie stehen nebeneinander, alle im selben Massstab, in jedem
  Geschoss gleich, denn sie gehen über die ganze Höhe. Gedreht nach ihrer
  Lage: bei 90° liegt y der Analyse in y des Gebäudes
  (`Wandlage.im_grundriss`, neben `traegheit`, wo dieselbe Regel für die
  Steifigkeit steht). Ihr Umriss kommt aus derselben Zeichnung wie das Bild
  «Querschnitt» ihrer Analyse (`diagrammdaten.zeichnung`, vorher
  `_zeichnung`), in derselben Farbe.
- Beide Richtungen stehen je Grösse im selben Massstab, wie die Pfeile der
  Ansicht. Ohne Gewicht zeigt das Bild nur die Wände; ohne Wand mit
  Querschnitt und ohne Kräfte fehlt es.

## 2026-11-26 · Pfahl: Bild «Querschnitt»

Vom Benutzer gewünscht (2026-11-25).

- Vorher zeigte ein Pfahl unter «Diagramme» die Situation und die Verläufe;
  wie er im Schnitt aussieht, stand nur in Zahlen. Nachher steht zwischen
  beiden das Bild «Querschnitt», massstäblich und auch ohne Kombination.
  Beim Bohrpfahl der Betonkreis D, die Wendel, die n Längsstäbe und der
  Radius ihrer Mitten, im Beispiel «r_s = 355 mm» längs des Pfeils, dazu
  Überdeckung und Ganghöhe. Beim Mikropfahl der Verpresskörper und das
  Tragglied, Rohr oder Vollstab; mit einer Abrostung gestrichelt der
  Durchmesser, mit dem der Nachweis rechnet, etwa «gerechnet mit d_a =
  106.3 mm» bei 114.3 mm und Δt = 4 mm.
- r_s und der Durchmesser nach der Abrostung kommen aus denselben zwei
  Funktionen wie im Nachweis (`innen.bewehrungsradius`,
  `innen.nach_abrostung`): Bild und Rechnung können nicht auseinanderlaufen.
  Die Masse schickt `pfahldaten.querschnitt` in mm; gezeichnet wird in
  `pf_querschnitt.js` mit den Helfern der Grundbau-Skizzen.
- Die Legende sagt beim Mikropfahl wie die Herleitung, dass nur das
  Tragglied trägt; die Abrostung nennt sie nur, wo es eine gibt.

## 2026-11-26 · Querschnittsanalyse: Bild «Querschnitt» zuerst unter den Diagrammen

Vom Benutzer gewünscht (2026-11-25).

- Vorher zeigte der Reiter «Diagramme» einer Querschnittsanalyse zuerst
  das Interaktionsdiagramm; den Querschnitt sah man nur im Zeichenfenster.
  Nachher ist «Querschnitt» das erste Bild, wie bei der Platte, und steht
  auch ohne Lastfall da: die Flächen in der Farbe ihres Baustoffs,
  Aussparungen gestrichelt, die Stäbe und verschmierten Linien, unten und
  links die Aussenmasse dessen, was Material hat, und der Schwerpunkt S
  mit den Achsen y und z, um die die Momente drehen. Die Legende nennt die
  Betone, den Stahl der Stäbe und die Lage von S, im Beispiel «S: y =
  150 mm, z = 300 mm».
- Dieselben Stile wie im Zeichenfenster (`cad-beton`, `cad-stab`,
  `cad-mass`, `cad-schwerpunkt`): beide sehen gleich aus. Auch
  Bruchzustand und Schubfluss zeichnen S jetzt so.
- Der Kern schickt dazu je Polygon die Art und den Namen seines Baustoffs,
  je Stab und verschmierte Linie Namen und Stahl
  (`diagrammdaten.zeichnung`). Eine Fläche aus Holz oder Baustahl
  (Schritt 11) bekommt ihre Farbe dann über die Klasse `cad-<art>`;
  Profile und Spannglieder kommen mit den Schritten 9 und 11 ins Bild.

## 2026-11-26 · Kacheln für Durchstanzen, Grundbruch, Setzung, Pfähle und Erdbeben

Vom Benutzer gewünscht (2026-11-25).

- Vorher hatten diese fünf Apps eine lange Spalte mit allen Karten
  untereinander. Nachher steht oben ein Kopf mit Bezeichnung, der Wahl der
  Art (Decke oder Bodenplatte, die Art des Pfahls) und der Beschreibung,
  darunter die Kacheln «Eingaben» wie bei Platte und Querschnittsanalyse:
  je Kachel ein Bild, der Name und das Wichtigste, etwa «Boden – φ_k =
  30°, c_k = 0 kN/m²». Ein Klick öffnet ihr Fenster mit genau diesen
  Feldern.
  - Durchstanzen: Gestützte Fläche, Platte, Biegebewehrung,
    Plattenrotation, Einwirkung. Der Grundriss bleibt offen über den
    Kacheln.
  - Grundbruch: Boden, Fundament, Gelände und Grundwasser, Sohlreibung,
    Einwirkungen.
  - Setzung: Fundament, Pressung in der Sohle, Schichten, Nachweis.
  - Pfahl: Pfahl, Querschnitt, Schichten, Grundwasser, Äusserer
    Widerstand, Fuss, Querlast, Einwirkungen.
  - Erdbeben: Standort und Bauwerk, Verhaltensbeiwert, Grundschwingzeit,
    Regelmässigkeit, Geschosse, Wände.
- Je Gruppe der Vorgaben des Kerns eine Kachel (`gruppenkapitel` in
  `kapitel.js`): Felder, Zeichen und Einheiten kommen weiter aus dem Kern,
  und `vollstaendig()` meldet eine Gruppe, die keine Kachel hat. Eine
  Gruppe, die in der gewählten Stellung kein Feld hat, gibt keine Kachel:
  undrainiert die Sohlreibung; am Pfahl der Fuss, wenn der äussere
  Widerstand aus einem Versuch kommt – der Versuch hat den Fuss schon
  mitbelastet.
- Was fehlt, steht grau auf der Kachel: «kein Beton», «keine
  Kombination», «keine Schicht», bei den Wänden der Grund der ersten, die
  nicht rechnet.
- Abweichung vom Plan: Bild und Kurzstand einer Kachel stehen in der
  Maske, nicht an der `Gruppe` des Kerns. Sie sagen nichts über die
  Rechnung; die Felder, die der Kurzstand zeigt, nennt die Maske mit ihren
  Kurznamen, Zeichen und Einheit holt sie vom Kern.
- Die Beschreibung ist ein Baustein für alle Apps (`beschreibung` in
  `bausteine.js`); `eingabekarten` ist weg. 21 neue Bilder stehen in
  `sinnbilder.js` unter «Die Kacheln der Eingaben».
- Keine Zahl einer Rechnung ändert sich; der Bericht bleibt gleich.

## 2026-11-26 · Platte: Betonstahl einmal oben, A_s je Lage; Kennzahlen mit Auge und Kopierknöpfen

Vom Benutzer gewünscht (2026-11-25).

- Angaben zur Platte: Vorher stand «Beton C30/37, h = 300 mm, b_x =
  1000 mm» darüber, und jede Zeile der Bewehrung nannte «B500B». Nachher
  steht «Beton C30/37, Betonstahl B500B, h = 300 mm, b_x = 1000 mm». Die
  Platte hat einen Betonstahl für alle Lagen und die Bügel; hält der
  Rechenkern verschiedene, nennt die Zeile alle.
- Die Spalte «Stahl» heisst jetzt «A_s [mm²]»: der Querschnitt der Lage
  über die Breite ihres Streifens – b_x für eine Lage in x, b_y für eine
  in y –, Grund und Zulage zusammen, aus dem Lagenaufbau. Im
  Beispiel steht die 1. Lage als «Ø12@150 | 754», die 2. als «Ø18@150 +
  Ø12@150 | 2450». Die Bügel haben dort einen Strich; ihr Querschnitt
  steht in der Herleitung.
- Kennzahlen: Vorher eine Liste ohne Knöpfe. Nachher eine Tabelle wie die
  der Nachweise: je Zeile ein Auge, das genau diesen Wert in der Herleitung
  zeigt, darunter Word | TeX | MD. Der Kern schickt die Tabelle fertig
  (`api.kennzahltabellen`, dieselbe wie im Bericht), je Zeile mit ihrem
  Wert als Ziel; ein Bauteil ohne Kennzahlen fehlt darin.
- In der Oberfläche teilen sich Nachweise und Kennzahlen `augenblock` und
  `augentabelle` (bericht.js), die CSS-Klasse heisst `augen-tabelle`. Nur
  eine Zeile mit Urteil bekommt die Farbe von erfüllt oder nicht.
- Der Bericht ändert sich in diesen zwei Tabellen; keine Zahl einer
  Rechnung ändert sich.

## 2026-11-26 · Durchstanzen gegen das Skript geprüft: m_sd aus der ganzen Auflagerkraft

Vom Benutzer gewünscht (2026-11-25): das Durchstanzen gegen das Skript
«Stahlbeton II, 7.4 Platten» (Kaufmann, FS 2026) prüfen, besonders welches
V_d in m_sd gilt – mit oder ohne Abzug der Last im Nachweisschnitt.

- Die Formeln des Moduls stimmen mit SIA 262:2025, 4.3.6 überein:
  Nachweisschnitt, k_e, Abzug im Schnitt, (58) bis (61), b_sr, (62) bis
  (65), r_s am Rand in Stufe 3, (66) bis (70) und der äussere Schnitt.
- Offen war, welches V_d in (62) bis (65) gilt. Die Norm sagt es nicht
  ausdrücklich; der Abzug nach 4.3.6.2.6 ist erlaubt, nicht verlangt. Das
  Skript verknüpft m_sd mit der Stützenreaktion (Folie 28). Entscheid des
  Benutzers (2026-11-26): m_sd kommt aus der ganzen Auflagerkraft. Den
  Abzug behält die Querkraft im Nachweis, in (66), (67) und am äusseren
  Schnitt.
  - Vorher, Bodenplatte mit Stütze 400 × 400 mm, h = 600 mm, V_d =
    2000 kN, Bodenpressung 150 kN/m², Stufe 2: m_sd = 234.9 kNm/m und
    V_Rd,c = 1995 kN. Nachher: m_sd = 250.0 kNm/m und V_Rd,c = 1906 kN
    (−4.4 %).
  - Bei einer Decke ändert sich V_Rd,c um weniger als 1 %. In Stufe 1 und 3
    ändert sich nichts.
- Das Skript weicht an zwei Stellen von der Norm 2025 ab; das Werkzeug
  folgt der Norm (siehe [[TODO]]): k_g nach (37) und f_ctm in (69).
- Neu steht in jeder Herleitung grau, dass Einzellasten über 0.2·V_d nahe
  am Nachweisschnitt nicht geprüft sind (4.3.6.2.3). Ohne Einwirkung fehlt
  der Satz.

## 2026-11-25 · Die Rechenart je Beton, in jedem Modul

Vom Benutzer gewünscht (2026-11-25): Die Rechenart soll überall unter dem
Schalter «Bemessung | charakteristisch» des Betons stehen, wie schon in der
Tragsicherheit der Querschnittsanalyse. Das ersetzt den Entscheid vom
2026-11-20, die Rechenart bleibe je Modul.

- Vorher standen bei «Stahlspannung quasi-ständig» die Kriechzahl, eine
  Rechenart für das ganze Modul und darunter die Werte je Material. Nachher
  stehen dort die Kriechzahl, «C30/37 [Bemessung | charakteristisch]» und
  darunter «[Hand | 0.85·x | präzise]», dann «B500B [Bemessung |
  charakteristisch]». Bei mehreren Betonen hat jeder seine Art.
- Im Kern hält `Rechenwahl` die Arten wie die Wertesätze: `Rechenarten`
  führt je Beton seine Art, auf derselben Grundlage `JeBaustoff` wie
  `Wertesaetze`. Haben alle Betone dieselbe Art, ist es dieselbe Wahl wie
  eine für alle; zwei gleiche Wahlen teilen sich also weiter eine Linie.
  `Rechenwahl.art` gibt es nur, wo alle Betone gleich rechnen, etwa in der
  Platte mit ihrem einen Beton. Wer mehrere Betone rechnet, fragt
  `art_von(beton)` oder `arten.mit_kriechzahl` und `arten.mit_block`.
- Damit fällt die Sonderform der Querschnittsanalyse weg:
  - ihre Wahl je Baustoff, ein Wörterbuch aus `Rechenwahl`;
  - das Feld `betongesetze`;
  - der Rückruf `wahl(stoff)` in `Querschnittsanalyse.werkstoffe`.

  Die Analyse hat jetzt eine Wahl wie jedes Kapitel.
- Im Projekt heisst das Feld überall `rechenarten`. Es hält je Kennung
  eines Betons seine Art, wie `werkstoffsaetze` je Material; ein Stahl hat
  keine. Welche Arten ein Kapitel anbietet, steht weiter am Feld. Der
  Katalog schickt sie mit (`felder`, `wahl`), und die Oberfläche zeigt nur
  diese Stellungen. Gibt es nur eine Art, wie bei der Verformung beim
  Knicken, steht kein Schalter. Im Katalog bleibt nur `rechenarten`;
  `faserarten`, `verformungsarten` und `betongesetze` sind weg.
- Über dem Bild einer Spannung-Dehnung-Analyse steht die Art in Worten,
  bei verschiedenen Arten je Beton: «C30/37 0.85·x, C50/60 präzise». Die
  Herleitung zeigt das Gesetz des Betons, der zuerst reisst, und sagt,
  dass die anderen mit ihrer eigenen Art rechnen. Das Feld φ steht blass,
  wenn φ bei keinem der gewählten Betone wirkt.
- Keine Zahl ändert sich, der Bericht des Beispiels bleibt gleich. Ein
  gespeicherter Stand mit `rechenart` oder `betongesetze` öffnet sich nicht
  mehr und nennt das Feld; die Seite bewahrt ihn auf (Prototyp, Benutzer,
  2026-10-11).
- Neue Tests prüfen zwei Betone mit verschiedenen Arten: im Kern und an
  einem Plattenbalken aus C30/37 und C50/60.

## 2026-11-25 · Die Rechenart «elastisch» ist gestrichen

Vom Benutzer gewünscht (2026-11-25): Er fragte, worin sich «elastisch» und
«präzise» unterscheiden, in Wirklichkeit gebe es doch keinen Unterschied –
und wählte, «elastisch» zu entfernen.

- «elastisch» rechnete den Beton linear mit E_cm/(1+φ), ohne Zug und
  höchstens f_c; «präzise» rechnet die Parabel mit demselben Modul. Unter
  Gebrauchslast ist die Parabel beinahe eine Gerade. An einer Platte 250 mm,
  Ø12/150, C30/37 mit M = 50 kNm gab elastisch σ_s = 330.5 N/mm², präzise
  330.4; mit φ = 2 waren es 344 und 340. Nulllinie und Betonspannung lagen
  weiter auseinander, bis etwa 12 %; dort ist die Parabel die genauere.
- Übrig bleiben Handrechnung, 0.85·x und präzise. Die Stahlspannungen der
  Platte und des gezeichneten Querschnitts rechnen neu als Vorgabe präzise,
  ebenso die Zwängung auf Biegung des gezeichneten Querschnitts, die bisher
  fest elastisch rechnete. SIA 262:2025, 4.1.4.1.4 verlangt für den
  gerissenen Zustand nur, dass der Beton im Riss keinen Zug überträgt; das
  gilt mit der Parabel ebenso. Weil die Parabel bei null mit 1.25·E_c,eff
  ansteigt, ist sie dort steifer als die Gerade: der Stahl im Testfall
  «Fliessen» fliesst erst ab etwa 261 kNm statt schon bei 258, und zwei Tests
  gegen die geschlossene Formel d − x/3 treffen nur noch auf ein halbes
  Prozent.
- Die Listen `SPANNUNGSARTEN` und `FASERSPANNUNGSARTEN` gleichen damit
  `RECHENARTEN` und `FASERARTEN` und sind weg, im Kern wie im Katalog der
  Oberfläche. Das Gesetz `BetonElastisch` ist als `BetonOhneZug` in
  `test_querschnittsloeser.py` gezogen: dort prüft es den Löser gegen die
  geschlossene Lösung des Zustands II, die es nur linear gibt.
- Die Formelseite «Beton linear, ohne Zug» fällt weg; was ihre Theorie
  sagte, steht in kurzen Worten bei der Parabel-Rechteck-Beziehung.
- Gespeicherte Stände tragen die Rechenart der Stahlspannungen mit, auch
  die Vorgabe. Einer mit «elastisch» öffnet sich nicht mehr; die Seite
  bewahrt ihn auf (Prototyp, Benutzer, 2026-10-11).

## 2026-11-22 · Die Anleitung «KI-Agenten»

Vom Benutzer gewünscht (2026-11-22): eine Anleitung Schritt für Schritt, wie
man eine KI mit dem Werkzeug arbeiten lässt, und oben neben «Dokumentation»
ein Knopf dazu. Gewählt hat er eine Seite im Notizbuch, für Claude Code, die
Claude-App und andere MCP-Programme, und den Namen «KI-Agenten».

- Die Seite ist `Anleitungen/KI-Agenten.md`, eine Notiz von Hand. Der neue
  Ordner steht im Inhalt gleich nach dem Anfang (`ORDNER` in `tresor.py`).
- Sie beginnt mit dem Weg der Daten: KI und Seite teilen keinen Speicher,
  die Projektdatei trägt die Projekte hin und her – «Speichern», die KI
  arbeitet, «Öffnen». Ohne diesen Satz wartete man in der Seite auf
  Änderungen, die nie von selbst kommen.
- Die Probe in Schritt 2 schickt eine einzige Nachricht, `ping`: von Hand
  gestartet, wartet der Server sonst still, und das sieht aus wie ein Fehler.
- Für die Claude-App stehen der volle Pfad von Python und `PYTHONPATH` im
  Eintrag: die App startet den Server in einem Ordner, den man nicht kennt,
  und findet nicht unbedingt das Python des Terminals.
- Der Knopf trägt den Namen seiner Seite (`data-seite` in `index.html`); das
  Notizbuch öffnet sie und stellt den Knopf gedrückt, solange sie offen ist
  (`zeigtSeinZiel`). Ein Test prüft, dass es die Seite gibt.
- Auf dem Telefon fehlt der Knopf wie «Dokumentation»: die Anleitung steht im
  Inhalt, und eine KI braucht ohnehin einen Rechner mit Python.

## 2026-11-22 · Das Zahnrad: alles zurücksetzen

Vom Benutzer gewünscht (2026-11-22): ein Knopf, der alles zurücksetzt –
nicht offen in der Kopfleiste, sondern hinter einem Zahnrad oben rechts.
Gewählt hat er «alles im Browser».

- Das Zahnrad öffnet das Fenster «Einstellungen» (`einstellungen.js`). Es
  sagt, was weggeht, mit den Namen der Projekte und der Zahl aufbewahrter
  Stände; daneben stehen «Alle Projekte speichern» – dieselbe Funktion wie
  «Speichern» – und «Alles zurücksetzen …», das noch einmal nachfragt.
- Weg geht jeder Schlüssel der Seite im Browser (`opencivil.…`): die
  Projekte mit ihren Sandboxen, aufbewahrte Stände, die Lage der Werkzeuge
  im Zeichenfenster und zugeklappte Bereiche. Danach lädt die Seite neu und
  beginnt mit dem Beispiel, wie beim ersten Besuch (`allesZuruecksetzen`).
  Bis dahin legt sie nichts mehr ab, sonst brächte die nächste Änderung den
  alten Stand zurück.
- Was die Seite für den Betrieb ohne Netz geladen hat, bleibt: es ist das
  Programm, nicht die Arbeit.
- Dass jeder Schlüssel die Vorsilbe trägt, prüft `test_ablage_js.py`; ein
  Schlüssel ohne sie überlebte das Zurücksetzen still.
- Das Fenster braucht den Kern nicht. Es geht auch auf, wenn der Kern nicht
  startet – gerade dann kann ein Neubeginn helfen.
- Auf dem Telefon steht das Zahnrad ganz rechts in der Zeile der Knöpfe.
  Unter der Anzeige machte es die Kopfleiste höher, als sie ist, und schob
  den Namen oben hinaus.

## 2026-11-21 · Die Platte reisst wie der gezeichnete Querschnitt

Vom Benutzer gewählt (2026-11-21): eine Rechnung für beide. Die
Spannung-Dehnung-Analyse der Platte rechnete ihren Riss selbst, in b und h,
die des gezeichneten Querschnitts am Bruttoquerschnitt – dieselben Zahlen,
zwei Rechnungen und zwei Herleitungen. Jetzt steht der Riss einmal da
(`spannungsanalyse/riss.py`, `Bruttoriss`), und die Platte gibt ihm ihr
Rechteck b×h als Bruttoquerschnitt (`bruttoquerschnitt_rechteck`).

- **Vorher** stand in der Herleitung der Platte
  `M_Riss(N) = M_Riss − N·h/6 = 41.4 kNm − (−200 kN)·0.3 m/6 = 51.4 kNm`, und
  `M_Riss` selbst stand ohne Herleitung da.
- **Nachher** schreibt sie, was auch der gezeichnete Querschnitt schreibt:
  `A = b·h`, `I = b·h³/12`, `W = I/v_z`, `k_t` und `f_ct,eff`, dann
  `M_Riss(N) = (f_ct,eff − N/A)·W` – am Beispiel wieder 51.4 kNm. Unter Zug
  `N_Riss(M) = (f_ct,eff − M·v/I)·A` statt `f_ct,eff·b·h − 6·|M|/h`.
- Was nur die Platte weiss, sagt sie selbst: A und I kommen aus b und h,
  und unter Zug reisst ihre ganze Dicke, t = h – ihr Streifen b ist keine
  Abmessung der Platte. Am gezeichneten Querschnitt bleibt t = min(h; b).
- Der reine Betonquerschnitt des äquivalenten Moduls verweist bei beiden
  auf den Bruttoquerschnitt (`I_c = I`, `A_c = A`); sonst stünden b·h³/12
  und b·h zweimal in derselben Herleitung.

Die Zahlen sind dieselben, bis auf die letzte Rechenstelle; die Herleitung
des gezeichneten Querschnitts steht Wort für Wort wie vorher.

## 2026-11-21 · Was nur fehlt, steht auch als Hinweis grau

Vom Benutzer gewählt (2026-11-21), nach der Prüfung im Browser gefunden.
Ein leerer Eintrag zeigte über der Eingabe und rechts in der
Zusammenfassung «Nichts zu rechnen: noch nichts gezeichnet.» gelb
hinterlegt, wie eine Warnung; ebenso stand «Noch keine Einwirkung – so
rechnet kein Fall.» über den Fällen. Beides sagt nur, was fehlt, und steht
jetzt grau, wie die Meldungen der Zeichenfenster, denen nur etwas fehlt
(`unfertigHinweis`, `fehltHinweis`). Gelb bleiben Fehler und Warnungen.

## 2026-11-21 · Ein Urteil je Teil

Ein Umbau ohne neue Zahl, vom Benutzer gewählt (2026-11-21):

- **Ausgang und Begründung eines Falls stehen einmal da.** Zehn
  Fallergebnisse (je Lage, je Fall, je Kombination) führten je ein Feld
  `ausgang` mit der Vorgabe «nicht führbar» und ein Feld `begruendung`.
  Jetzt führt sie `Fallausgang` selbst, als Datenklasse, deren beide
  Felder man mit Namen setzt; was ein Ausgang je Nachweis gegeneinander
  stellt, steht im Kopf seiner Klasse. Die schiefe Biegung gab den
  Ausgang, die Biegung mit Normalkraft die Begründung nach der Stelle
  mit; jetzt beide mit Namen.
- **Die Schleife über die Teile steht einmal da.** Lagennachweise, beide
  Knicknachweise, Spannungsbegrenzung, Verformung und beide
  Querkraftnachweise schrieben je dieselbe Schleife: je Teil rechnen und
  herleiten, das Ergebnis in den Befund, die Ausgaben sammeln, das Urteil
  aus Ausgang und Begründung. Jetzt tut das `Teilnachweis.je_teil`; ein
  Nachweis sagt nur, wie er einen Teil rechnet, und wo nötig, wie der Teil
  heisst, welcher Grad ihn trägt und was er sonst ausgibt.
- **Je Seite des gezeichneten Querschnitts dasselbe.** Duktilität,
  sprödes Versagen und Zwängung auf Biegung schrieben je Seite den
  Titel, auf einer Seite ohne Bewehrung den Satz «Keine Bewehrung auf der
  gezogenen Seite → kein Nachweis.» und am Ende die massgebende Seite –
  dreimal von Hand. Das tut jetzt `Richtungsnachweis`; ebenso führt das
  Gleiten seine Kombinationen über `je_teil`, und der Grundbruch baut
  seine Urteile wie alle anderen.
- Eigene Schleifen behalten mit Absicht: Biegung mit Normalkraft, schiefe
  Biegung, Schubwand, Pfahl quer und innen quer, Erdbeben und fehlende
  Bewehrung – warum, steht in [[TODO]].

## 2026-11-21 · Platte und Querschnittsanalyse teilen, was gleich ist

Ein Umbau ohne neue Zahl, vom Benutzer gewählt (2026-11-21). Was die
Platte und der gezeichnete Querschnitt gleich tun, schrieb jeder von Hand
ab; jetzt steht es einmal da:

- **Der Anfang der Knicknachweise.** Beide prüften, dass es Fälle gibt,
  liessen die Verformung mit E_cd rechnen und legten je Fall einen
  Erfüllungsgrad «Knicken – Fall» an, mit Titel und Normstelle. Das tut
  jetzt `Knickverfahren.__init__`; die Platte gibt nur noch ihre
  Bezüge und ihre Resistenzlinie dazu, der gezeichnete Querschnitt seine
  Bezüge. Die Normstelle 4.3.7 steht einmal (`knicken.REFERENZ`).
- **Thema und Namen der Zwängung auf Normalkraft.** Der gezeichnete
  Querschnitt schrieb Thema, Langnamen, Art, das Kürzel «NR», den Namen
  «Rissnormalkraft» und den ersten Satz der Herleitung von der Platte ab.
  Jetzt teilen beide `Normalzwang`, wie bei der Biegung schon
  `Biegezwang`; der hat dazu sein Kürzel «ZB» bekommen, das der
  gezeichnete Querschnitt ebenfalls abschrieb.
- **Das Anlegen und Belegen der Kennzahlen.** Die Platte, der gezeichnete
  Querschnitt und der Pfahl (seine Federn) führten je zwei Listen, ein
  `dazu` und ein `_belegen`, Zeile für Zeile gleich. Jetzt erben alle drei
  von `Kennzahlprozedur` (`core/berechnung.py`): `anlegen(basis)` gibt das
  `dazu`, `_belegen` steht dort, und die Ausgaben sind genau die
  angelegten Kennzahlen. Die Platte nennt ihre Erklärung «Handrechnung mit
  Bemessungswerten» jetzt bei jeder Kennzahl selbst, statt sie als
  stille Vorgabe im `dazu` zu tragen.

## 2026-11-21 · Das Fachwerk an einer Stelle

Ein Umbau ohne neue Zahl, vom Benutzer gewählt (2026-11-21):

- Die Regeln der Druckdiagonalen standen in `querschnitt/platte.py`: die
  Grenzen der Neigung (30° und 45°), ihre Hebung auf 40° bei Normalzug
  (`druckfeldgrenzen`) und `k_c` = 0.55. Sieben Module holten sie dort,
  auch der Pfahl, der mit der Platte nichts zu tun hat. Und die Suche nach
  der günstigsten Neigung stand dreimal da: bei den Bügeln der Platte, bei
  den Schubwänden und bei der Wendel des Pfahls, jedes Mal dieselben vier
  Zeilen.
- Jetzt besitzt `querschnitt/fachwerk.py` beides: die Regeln und
  `guenstigste(punkt, alpha_min=, alpha_max=, zugkraft=)`. Jeder Nutzer
  gibt nur noch sein Fachwerk bei einer Neigung (`punkt`) – die Bügel je
  Laufmeter, die Wand mit ihrer Länge als Hebelarm, die Wendel mit 70 %.
- `Wandwiderstand` war Feld für Feld ein `Buegelpunkt` und ist weg; eine
  Wand gibt den `Buegelpunkt` ihrer günstigsten Neigung.
- Die Bügel der Platte haben `Buegelwerte.punkt`; die Kurve fürs Bild
  (`neigungen`) und die Suche rechnen jeden Punkt damit.

## 2026-11-21 · m_Rd mit Einheit, die Zahl der Tests

- Die M-V-Kurve der Platte schrieb an ihre senkrechte Linie «m_Rd = 235.9»,
  ohne Einheit. Jetzt «m_Rd = 235.9 kNm»: mit Einheit und Stellen, die der
  Kern der Achse gibt (`masszahl`), wie die Marken daneben.
- Im README stand «Fertig und getestet (1229 Tests)». Es sind 2145; die
  Zahl steht jetzt mit ihrem Datum da, weil sie weiter wächst.

## 2026-11-21 · Nichts doppelt, kein ∞ in der Werteliste

Zwei Stellen aus der Durchsicht, die der Benutzer weghaben wollte
(2026-11-21):

- **Eine leere Querschnittsanalyse sagte zweimal, dass nichts gezeichnet
  ist**: über der Zeichnung «Nichts zu rechnen: noch nichts gezeichnet.»,
  unter ihr «Noch nichts gezeichnet: Polygon P, Bewehrung B, … – oder eine
  Vorlage T.». Jetzt steht nur der Satz unter der Zeichnung; er sagt auch,
  womit man beginnt. Der Hinweis darüber schweigt, solange die Zeichnung
  ganz leer ist: `leer` eines Bauteils in `apps.js`, für die Analyse
  `nichtsGezeichnet` aus `cad_app.js` – dieselbe Regel, nach der der Satz
  unter der Zeichnung steht. Steht schon ein Hilfspunkt da, fehlt der Satz
  darunter, und der Hinweis sagt es wieder. Rechts in der Zusammenfassung
  bleibt «Nichts zu rechnen: noch nichts gezeichnet.».
- **Ein unbeschränkter Erfüllungsgrad stand als «∞» in der Werteliste des
  Berichts**, beim regelmässigen Gebäude «Erfüllungsgrad Regelmässigkeit
  ∞»: ein Grad, den kein Urteil trägt, weil sein Fall nicht vorkam –
  `Nachweis.rechne` setzt ihn auf ∞, damit weitergerechnet werden kann. Im
  vollen Bericht waren es 31 Zeilen, etwa beim Durchstanzen ohne
  Bewehrung. Die Werteliste lässt jeden Erfüllungsgrad ∞ weg
  (`_ohne_aussage` in `bericht/gliederung.py`): was er sagt, steht bei den
  Nachweisen in Worten («Keine Einwirkung → kein Nachweis.»).

Nicht geändert: die Tabellen der Schubwände in der Herleitung zeigen
V_Rd/V_1 = ∞ für eine Wand, die in einer Richtung nichts trägt. Dort ist ∞
eine Zahl der Rechnung, kein Urteil.

## 2026-11-21 · Eine Meldung nennt ein Feld wie die Maske

Eine Meldung nannte ihren Ort zum Teil mit den Feldern der Datei: «Platte
'Decke', Lage 2, grund: Teilung muss grösser als null sein»,
«querkraftbewehrung: α_max …», «Grundbruch 'F', kombinationen 'K': …». Der
Benutzer will die Wörter des Fensters (2026-11-21). Jetzt heisst es «Lage
2, Grund», «Bügel: α_max …», «Kombination 'K'».

- Ein Eintrag im Eintrag trägt sein Wort am Feld, `teil(…, heisst=…)` in
  `projekt/lesen.py`: «Grund», «Zulage», «Bügel», «Tragsicherheit,
  Rechenwahl», «Knicken, Verformung (e_2d)», «Fliessen häufig»,
  «Stahlspannung quasi-ständig», «Bewehrung suchen, Obergrenze», «E_eq» –
  die Wörter der Kapitel und Zeilen der Maske.
- Ein Element einer Liste nennt das Wort seiner Klasse (`IM_ORT`), wie
  schon Lage, Wand und Geschoss: «Einwirkung 'GZT'», «Knicknachweis
  'Wand'», «Schicht 'Kies'», «Diagramm 2». Ein Element der Zeichnung ohne
  Namen bleibt bei seiner Kennung, «L3», wie sie im Bild steht.
- Die Python-Schnittstelle des Balkensystems baute den Ort eines neuen
  Elements von Hand aus seiner Liste, «linien»; jetzt nach derselben Regel
  wie das Lesen (`element_ort`).
- Ein Test wacht, dass jeder Teil eines Eintrags ein Wort hat: ohne stünde
  still wieder das Feld der Datei in der Meldung.

Geblieben ist das Feld der Datei, wo eine Meldung die Form der Datei
betrifft – «'alpha_min' muss eine ganze Zahl sein», «ein Feld 'hh' gibt es
nicht»: sie richtet sich an wer die Datei oder das Skript schreibt, und der
braucht den Namen, den er tippt. Die Wörter der Knöpfe («+ Schicht») stehen
weiter in der Oberfläche.

## 2026-11-21 · Eine Lastnummer kommt nie wieder

Eine neue Last im Balkensystem nahm in der Zeichnung die grösste
vorhandene Nummer plus eins: wer P5 als letzte löschte, bekam mit der
nächsten wieder ein P5 – und eine Meldung oder Auswahl, die noch auf die
alte zeigte, traf die neue. Knoten, Linien und der Kern zählten schon nach
der Regel «eine Kennung kommt nie wieder» (Benutzer, 2026-11-19), nur die
Lasten in `bs_zeichnung.js` nicht; ihr Kommentar behauptete «wie im Kern».
Jetzt nimmt `naechsteLast` dieselbe `neueKennung` wie Knoten und Linien.
Gefunden bei der Durchsicht vom 2026-11-20.

## 2026-11-21 · η_EI statt κ

Der Anteil der ungerissenen Steifigkeit einer Tragwand hiess κ. Dasselbe
Zeichen ist in der Querschnittsanalyse die Krümmung, und SIA 262:2025 nennt
so die Vergrösserung der Querkraft duktiler Tragwände für höhere
Eigenformen (4.3.9.4.4, (97)) – wer beides liest, hätte zwei κ vor sich.
Der Benutzer hat η_EI gewählt (2026-11-21): in der Maske, der Herleitung
(«EI = Σ n·η_EI·E_cm·I»), der Datei (`eta_EI`) und in Python
(`h.wand(…, eta_EI=0.5)`). Die Zahlen bleiben; eine Datei mit `kappa` weist
der Kern laut ab, wie jedes Feld, das es nicht gibt.

## 2026-11-20 · Grosse Dateien geteilt

Punkt 8 der Durchsicht vom 2026-11-19: Dateien nahe an 1000 Zeilen werden
geteilt, nach dem, was zusammengehört.

- `projekt/eintraege.py` (910 Zeilen) gab Posten, Lage, die Obergrenze der
  Bewehrungssuche und die Bügel an `projekt/platte.py` ab: nur die Platte
  hat sie. Übrig bleibt, was mehrere Bauteile teilen – Material,
  Lastfälle, Rechenwahlen und die Angaben, die Platte und gezeichneter
  Querschnitt gleich machen (750 Zeilen).
- `querschnitt/interaktion.py` (922 Zeilen) gab die Fläche der Widerstände
  ab, den Schnitt durch alle Bruchzustände, den nur das
  Interaktionsdiagramm der Querschnittsanalyse liest:
  `querschnitt/widerstandsflaeche.py`. Ihre Stufen merkt sich das neue
  Modul je Querschnitt, solange es ihn gibt; vorher trug der Querschnitt
  sie selbst. Die Tests der Fläche stehen in `test_widerstandsflaeche.py`.
- `web/js/platte_bilder.js` (936 Zeilen) zeichnete den Bemessungspunkt
  dreimal selbst, die Querschnittsanalyse ein viertes Mal, jedes mit
  eigener Grösse für den Widerstand. Das Grün und Rot der Urteile stand in
  vier Bildern als eigene Zahl, etwas anders als in den Tabellen. Jetzt
  stehen `bemessungspunkt`, `urteilsfarbe` und die Legende mit ihren Proben
  (`strich`, `punkt`, `flaeche`, bisher nur in `spannungsbild.js`) in
  `achsen.js` (873 Zeilen bleiben). Sichtbar: eine Linie steht in der
  Legende als Strich mit ihrem Muster statt als Punkt, der Widerstand ist
  überall gleich gross, und die Punkte haben die Farben der Tabellen.
- `web/css/stil.css` (2597 Zeilen) steht in neun Blättern nach Bausteinen:
  Grundlage, Seite, Eingaben, Berechnung, schmale Geräte, Zeichenfenster,
  Notizbuch, Skizzen, Python. Geschnitten an den Abschnitten, die es schon
  gab, damit keine Regel ihren Platz wechselt: bei gleicher Spezifität
  gewinnt die spätere, und die Brücke bindet die Blätter in der Reihenfolge
  ihrer Nummern ein (`stilblaetter`). Im Browser verglichen: jedes Element
  der Platte, des Balkensystems, des Pfahls mit seinen Verläufen, der
  Setzung, des Erdbebens und von Python hat mit den neuen Blättern
  denselben Stil wie mit der alten Datei. Dabei weggefallen: fünf Regeln
  `[hidden]` (eine für alle, mit `!important`), 25 Farbregeln der Verläufe
  (eine Variable `--verlauf` je Grösse) und fünf Klassen für eine leere
  Liste (`.leer-zeile`; im Baum, unter der Zeichnung, bei Lastfällen und
  Querschnitten, in der Suche und in der Konsole). Sichtbar ist nur, dass
  eine leere Liste unter der Zeichnung 4 px mehr Luft hat und die bei den
  Lastfällen etwas weniger.
- `tests/test_querschnittsanalyse.py` (1076 Zeilen) gab die Tests der
  Vorlagen, der leeren Analyse und der verschmierten Stäbe an
  `test_qa_vorlagen.py` ab (819 Zeilen bleiben, 89 Tests wie vorher).

Warum: Wer die Platte liest, fand ihre Teile in einer anderen Datei, und
wer die gemeinsamen Teile suchte, las an den Lagen der Platte vorbei. Wer
den Bruchzustand liest, muss nicht mehr am Bild vorbei. Und ein
Bemessungspunkt sah in jedem Bild ein wenig anders aus, ohne dass es
jemand so gewollt hatte.

## 2026-11-20 · Die Platte rechnet als Rechteck mit Stäben

Die Platte rechnete ihren Querschnitt ein zweites Mal (Punkt 4 der
Durchsicht vom 2026-11-19): mit eigenen Fasern (`plattenfasern`), eigenem
Fächer und eigenen Grenzen (`dehnungsfaecher.py`), in einem eigenen Löser
(`Querschnittsloeser`). Jetzt baut sie einen `interaktion.Querschnitt` wie
der gezeichnete Querschnitt und der Pfahl: ein Rechteck b·h um die halbe
Höhe, je Lage ein Stab (`Gesetze.querschnitt`).

- Die Löser nehmen 60 Streifen wie beim gezeichneten Querschnitt
  (`FASERN`), die genaue Resistenzlinie 200 (`STREIFEN`). Die Linie läuft
  den Fächer der Interaktion ab, für Zug unten und für Zug oben
  (`faecherebenen`, dafür jetzt öffentlich).
- Eine Lage ist ein Band über die ganze Breite: wo das Gesetz springt,
  wird der Beton, den sie verdrängt, über die Dicke a_s/b gemittelt
  (`Bewehrung.dicke`). Ohne Angabe bleibt es ein Quadrat gleicher Fläche.
- Die Grenzen heissen wie beim gezeichneten Querschnitt, mit dem Namen des
  Baustoffs: «Beton C30/37, Rand oben» statt «Beton am oberen Rand»,
  «Beton C30/37, Punkt C» statt «Beton im Punkt C», «Stahl B500B,
  äusserste Lage unten» statt «Stahl der 1. Lage». So steht es im Bericht
  («Massgebend: …») und in den Hinweisen der Spannungsanalyse.
- Nebenbei behoben, auch am gezeichneten Querschnitt: lag ein Stahl an
  einer einzigen Stelle – eine Lage nur unten –, hiess seine Grenze bei
  Zug unten «oben». Jetzt sagt seine Lage zum Bezugspunkt die Seite.

Die Zahlen bleiben: alle 1518 Werte der beiden Beispielprojekte wie
vorher, auf 1e-9 genau. Im Bericht kippt eine Rundung: ein Moment des
Balkensystems liegt genau auf −20.25 kNm, und mit 1e-14 Unterschied im
Modul E_eq steht dort −20.2 statt −20.3.

Geblieben ist das `Loeserpaar` der Platte neben dem `Schnittpaar` des
gezeichneten Querschnitts. Seine Löser kommen aus demselben Bau, aber den
Riss rechnet es weiter am Rechteck in b und h, mit der rissaktiven Dicke
t = h. Beide zusammenzulegen ändert die Herleitung der Platte; das steht
in [[TODO]].

Warum: Dieselbe Grenzregel stand zweimal da, in `dehnungsfaecher.grenzen`
und `interaktion._grenzen`, mit verschiedenen Namen für dieselbe Grenze;
jede Änderung daran war zweimal zu machen. Der Vergleich zwischen Platte
und Querschnittsanalyse in `test_interaktion.py` trifft sich jetzt auf
1e-9 statt auf ein Zehntausendstel.

## 2026-11-20 · Eine Form für «welche Seite zieht»

Welche Seite ein Moment zieht, stand in fünf Formen da (Punkt 3 der
Durchsicht vom 2026-11-19): als `Zugseite`, als `von_unten` an den Lagen,
als `moment_positiv` in der Querkraft, als `True` und `False` in
Wörterbüchern und als Vorzeichen von M_Ed. Jetzt ist es überall die
`Zugseite`.

- Die Lage der Platte sagt ihre Seite an einer Stelle,
  `Bewehrungslage.seite`: Lagen 1 und 2 unten. `von_unten` ist weg. Die
  Stahllage trägt ihre Seite, und `je_seite` fasst nach ihr zusammen.
- Die Querkraft fragt je Zugseite: `zugposten`, `statische_hoehen`, die
  Kurvenbeiwerte, der Fall mit Bügeln. «Ein positives Moment zieht unten»
  steht nur noch in `Zugseite.aus_moment`; vorher auch im Modul der
  Spannungsanalyse und dreimal als `M_Ed >= 0` in der Querkraft.
- Ein Ast der M-V-Kurve nennt seine Seite, «unten» oder «oben», statt
  eines Ja/Nein.
- `Zugseite.vorzeichen` ersetzt viermal «+1 oder −1» von Hand.

Bewusst geblieben ist `positiv` an der Resistenzlinie (`kante`,
`moment_bei`): ein Vorzeichen auf einer Achse – auch auf der der
Normalkraft –, keine Seite.

Warum: Ein Ja/Nein kann «links» nicht sagen. Was auf `je_seite` aufbaut,
die Handrechnung, hing darum an der Platte. Die Seite als einzige Form ist
auch die Vorbedingung für Punkt 4, die Platte als `interaktion.Querschnitt`.

## 2026-11-20 · Die Apps mit Zeichenfenster antworten gleich

Querschnittsanalyse, Balkensystem und Decke hatten dasselbe dreimal
geschrieben (Punkt 5 der Durchsicht vom 2026-11-19): die Frage an den Kern,
die Liste unter der Zeichnung, die Meldungen und das schwebende Fenster zur
Auswahl. Das steht jetzt einmal in `cad_app.js`; die Apps geben nur dazu,
was sie selbst wissen. Das Durchstanzen nutzt dasselbe Fenster, ohne Liste.

- **Die Antwort des Kerns.** `kernFragen` fragt einmal je Fassung des
  Projekts; was gefragt wird und was von der Antwort bleibt, sagt der
  Adapter (`fragen`, `nehmen`, `meldungen`). Scheitert die Frage, steht ihr
  Grund unter der Zeichnung, «Die Zeichnung ist nicht geprüft: …» – das
  hatte bisher nur die Querschnittsanalyse –, und keine alte Antwort bleibt
  stehen. Das Durchstanzen fragt nicht: es liest seinen Grundriss aus der
  letzten Lösung.
- **Was ein Klick wählt.** `waehlbarVon` ist die eine Regel für Zeilen und
  Meldungen: ein Lager, eine Stütze, eine Punktlast über ihren Knoten, eine
  Last des Balkensystems selbst. Bisher stand sie siebenmal da; im
  Balkensystem wählte eine Meldung zu einer Last nichts, und eine Lagerzeile
  war nie markiert, wenn ihr Knoten gewählt war.
- **Die Liste.** Je Teil eine Zeile: der Name, was es ist, rechts eine Zahl;
  die Spalten einer Gruppe stehen untereinander (`subgrid`). Vorher sah sie
  in jeder App anders aus. Ist nichts gezeichnet, nennt sie die Werkzeuge
  mit ihren Tasten. Die zugeklappten Meldungen der Decke im Ergebnis haben
  eine eigene Form (`.meldungsgruppe`), statt die der Liste zu borgen.
- **Das schwebende Fenster.** `auswahlEigenschaften` sortiert die Auswahl
  nach Listen. Knoten und Ecken zeigen ihre Lage, auch mehrere zugleich
  mit «Var» – die Querschnittsanalyse zeigte bei mehreren nichts, das
  Durchstanzen nur einen Hinweis. `zugleich` gibt jedem Feld mehrerer
  Einträge den gemeinsamen Wert oder «Var». «Neu» über den Vorgaben eines
  Werkzeugs setzt die Palette, und nur, wenn es Vorgaben gibt: das Werkzeug
  «Knoten» zeigte ein einsames «Neu».

Warum: Die Bedienung soll sich selbst erklären (Benutzer, 2026-11-19), und
das geht nur, wenn alle Apps gleich antworten. Dreimal geschrieben, kam
jede Verbesserung nur in einer App an. `qa_zeichnung.js` ist dabei von 959
auf 820 Zeilen geschrumpft.

## 2026-11-20 · Tests aufgeräumt

Elf Tests prüften nichts, was nicht schon ein anderer prüft. Der Benutzer
wollte sie weg und getrennt davon aufgeräumt (2026-11-20). Gelöscht sind:

- fünf mit demselben Fall «ein Feld, das es nicht mehr gibt, wird
  abgewiesen»: `richtung` am Lastfall, `gleichungen`, das φ an der Platte,
  die flachen Felder des Knickens, der alte Dickenmodus. Das prüft
  `test_lesen` an einer Stelle; als Beispiel am ganzen Projekt bleibt
  `test_vier_lagen_statt_lagen_unten`;
- zwei, die den Code abschrieben: das «‰» der Promille und die Vorlagen der
  Listen im Katalog;
- einer, der nur prüfte, dass zwei geerbte Methoden aufrufbar sind;
- einer, der gegen ein von Hand geschriebenes `als_dict` wachte – das
  schreibt heute jede Klasse aus ihren Feldern selbst;
- einer, der mit `json.dumps` prüfte, ob eine Antwort JSON ist. Das lässt
  NaN durch; die echte Prüfung steht in `test_dienst` und
  `test_schnittstelle`;
- einer, der die Wahlwerte des Pfahlkopfs abschrieb.

Das Aufräumen daneben:

- Neun Dateien riefen `unittest.main()` mitten in der Datei auf. Wer eine
  davon direkt startete, übersprang still alles danach: die Datei der
  Querschnittsanalyse lief mit 14 Tests und 3 Fehlern, jetzt laufen alle
  89. `main()` steht jetzt am Ende jeder Datei.
- `test_schnittstelle` rechnet das Beispiel einmal für die vier Tests, die
  es lesen, statt in jedem neu.
- Die Decke prüfte in zwei Tests, dass Zeichnung und Bilder nur einer Decke
  gelten; das ist jetzt einer.

## 2026-11-20 · Erdbeben: das Ersatzkraftverfahren

Eine neue App nach SIA 261:2020, 16.5.2, auf Wunsch des Benutzers
(2026-11-20): die Kräfte je Geschoss und je Wand, ohne Verbindung ins
Balkensystem. Je Geschoss G_k, Q_k und ψ₂; jede Wand nimmt ihren
Querschnitt aus einer Querschnittsanalyse des Projekts, ungerissen mal κ
– so hat er es gewählt.

**Das Modell.** Die Wände einer Richtung stehen als ein Kragarm da,
eingespannt am Fuss; die Gewichte der Geschosse wirken waagrecht auf der
Höhe ihrer Decke. Daraus die Auslenkung des Dachs u und T₁ = 2·√u (40),
dann S_d (31) bis (34), F_d (41), die Kräfte je Geschoss (42) und das
Kippmoment, dasselbe mit q = 1.0 (16.5.1.9). Jede Wand trägt nach ihrem
Anteil an EI. Bei 0° liegt y der Analyse in x des Gebäudes: eine Kraft in
x biegt die Wand um z. Die Annahmen, die die Norm nicht regelt, stehen in
[[TODO]].

**Wann das Verfahren gilt.** Die Norm verlangt (39) in beiden Richtungen.
Darum ist T₁ ≤ 4·T_C je Richtung ein Urteil mit Erfüllungsgrad, und wer
verfehlt, nennt im Hinweis jeden Grund, auch die der anderen Richtung.
Grund- und Aufriss bejaht der Benutzer mit je einem Schalter, die
Kriterien in eigenen Worten darunter; dass das Gewicht nach oben zunimmt,
sieht die Rechnung selbst. Erst wo etwas davon fehlt, steht ein eigenes
Urteil «Regelmässigkeit», rot. Ein erster Entwurf gab jeder Richtung den Grad 0,
sobald der Grundriss unregelmässig war – das verbarg, wie weit (39) aufgeht. Die
Zahlen bleiben in jedem Fall stehen. Die Grenze heisst T_1,max = 4·T_C, wie
w_max bei der Verformung; mit «4·T_C» als Zeichen stand auf ihrer Seite der
Formelsammlung «4·T_C = 4·T_C».

**Duktile Wände.** Über q = 2.0 ist das Tragwerk duktil bemessen (SIA
262:2025, Tabellen 14 und 15), und für schlanke Tragwände gelten eigene
Bemessungswerte (4.3.9.4): das Moment linear über die Höhe, die Querkraft
vergrössert (95). Die Rechnung kennt sie nicht und sagt es grau – sonst
sähen die Kräfte je Wand nach Bemessung aus. Gefunden beim Nachschlagen
der Werte für q; dort heisst die Vergrösserung für höhere Eigenformen κ
(97), wie hier der Anteil der Steifigkeit (siehe [[TODO]]).

**Eine Wand, die nicht rechnet, hält das Gebäude an.** Ohne sie stimmten
Schwingzeit und Verteilung nicht und sähen doch richtig aus. Was ihr fehlt,
steht grau an ihr (`wandquerschnitt`, für Rechnung und Bild dieselbe
Regel): keine Analyse gewählt, eine gelöschte, eine, die nicht rechnet,
eine mit zwei Betonen – E_cm gilt nur für einen. Eine Analyse ohne Beton
gibt es nicht: rechnen kann nur eine mit Polygon, und jedes ist aus Beton.
Sind y und z keine Hauptachsen, sagt es derselbe Satz wie im Raum
(`keine_hauptachsen`), je Analyse einmal.

**Die Oberfläche.** Drei Tafeln: das Gebäude mit Standort, q, T₁ und der
Regelmässigkeit; die Geschosse von unten; die Wände mit Analyse, Lage als
Bild, n und κ. Unter «Diagramme» je Richtung die Ansicht mit den Kräften
als Pfeilen und der Querkraft je Geschoss, darunter was jede Wand am Fuss
trägt. Die Wahl einer Analyse und die eines Querschnitts im Balkensystem
sind eine Liste (`bauteilliste`); sie sagt jetzt in beiden «– gelöscht,
neu wählen –», wo der Eintrag fehlt. Meldungen nennen ein Geschoss und eine
Wand wie die Maske, «Wand 'W1'» statt «waende 'W1'»: das Wort der Klasse
(`IM_ORT`) gilt jetzt auch für Elemente mit Namen. Ohne Gewicht sagt das
Bild «Keine Einwirkung → kein Nachweis.» wie jeder Nachweis; es ist nur so
hoch, wie das Gebäude es braucht – ein Haus von einem Geschoss steht nicht
als Turm da –, und über der Tabelle der Wände steht, dass sie je eine der
n gleichen gilt.

**Beispiele.** Das Beispiel hat ein Wohnhaus auf je zwei Wänden in x und y,
grün; «Jeder Nachweis» ein Lager mit T₁ von Hand, unregelmässig und oben
schwerer, einen Turm auf einer Winkelwand, duktil bemessen mit q = 3.0, und
ein Gebäude ohne Wandquerschnitt – zusammen jeder Ast des Spektrums und
jeder graue Satz. Von Hand nachgerechnet
in `tests/test_erdbeben.py`: vier Geschosse auf zwei Wänden, T₁ = 0.4035 s,
F_d = 2970.5 kN.

## 2026-11-20 · Der MCP-Zugang

Der Benutzer wünschte sich, dass eine KI mit dem Werkzeug arbeiten kann,
mit Projektdateien (2026-11-20). `python3 -m opencivil.mcp` startet einen
Server, der das Model Context Protocol über stdin und stdout spricht –
JSON-RPC 2.0, eine Nachricht je Zeile, nur mit der Standardbibliothek. Er
kennt `initialize`, `ping`, `tools/list` und `tools/call`; Claude Code
findet ihn über `.mcp.json`.

**Ein Rechenweg.** Geöffnet und gerechnet wird über `dienst.bearbeite`, wie
in der Seite; angelegt, kopiert und gelöscht mit Methoden des Projekts
(`eintrag_anlegen`, `eintrag_kopieren`, `eintrag_loeschen`,
`material_anlegen`). Was die Seite dabei in JavaScript tut, ohne auf den
Kern zu warten, folgt ihm: der Stamm eines neuen Namens – «Platte» in
«Platte 1» – stand bis dahin in `arten.js` und steht jetzt an der Klasse
(`STAMM`), die Seite liest ihn aus dem Katalog (`staemme`), und ein Test
hält die Namen beider gleich, auch die der Kopien.

**Eine Tür für jede Änderung.** Jedes Werkzeug ändert eine Kopie des
Projekts; erst wenn der Kern sie geprüft hat, ersetzt sie das Projekt.
Abgewiesen wird, was er nicht lesen kann – «ein Feld 'hh' gibt es nicht.
Gemeint ist vielleicht 'h'?» – und was das ganze Projekt anhielte, wo es
vorher rechnete, etwa zwei Materialien mit einem Namen. Was nur den Eintrag
anhält, gilt: der Rest rechnet weiter, wie seit 2026-11-19 überall, und die
Antwort sagt gleich, was fehlt, in den Worten des Kerns. Anders als ein Feld
der Seite nimmt der Zugang darum auch eine Dicke von −5 mm an – und meldet
sie im selben Satz, der sonst beim Rechnen käme. Mehrere Änderungen in einem
Aufruf gelten zusammen oder keine.

**Kennungen, die jemand selbst schreibt.** Mit `eintrag_setzen` und
`eintrag_aendern` schreibt eine KI die Elemente eines Bauteils selbst, mit
ihren Kennungen. Eine gelöschte darf dabei nicht wiederkommen
(`netz.von_hand`, Regel 1 der Kennungen): sonst träfe ein Diagramm, das noch
auf einen gelöschten Lastfall zeigt, einen neuen. Die Meldung nennt die
nächste freie.

**Die Herleitung eines Bauteils.** `herleitung` holt den Bericht mit `nur`;
`Projekt.nur` behält dafür die Bauteile, deren Querschnitt das Bauteil
nimmt – ein Stab, dessen Querschnitt eine Analyse ist, rechnete ohne sie
nicht. Die Bewehrungssuche, die `nur` auch braucht, rechnet Platten, und die
nehmen keinen.

**Bewusst nicht.** Skripte der App «Python» führt der Zugang nicht aus –
die Konsole führt beliebigen Code aus. Und `rechnen` gibt nicht die ganze
Antwort des Dienstes zurück, beim Beispiel rund 870 kB, sondern je Bauteil
die Tabelle seiner Nachweise aus der Zusammenfassung, mit dem, was der Kern
dazu sagt. Eine Datei, die es schon gibt, überschreibt der Zugang nur mit
`ueberschreiben`, und wer ungespeicherte Änderungen hat, muss sie zum
Öffnen einer anderen Datei ausdrücklich verwerfen.

## 2026-11-20 · Schneller Start

Der Benutzer fragte, warum der Start auf GitHub so lange dauert
(2026-11-20). Gemessen wird jetzt bei jedem Laden: nach der ersten Rechnung
schreibt die Seite in die Konsole, wann jeder Schritt fertig war, ab dem
Aufruf der Seite («Start: Server gesucht 0.06 s · Oberfläche geladen 0.09 s
· Quellen geholt 0.10 s · Python geladen 2.48 s · …»). Jeder Schritt setzt
seine Marke selbst (`performance.mark`); der Faden des Kerns schickt die
seinen mit «bereit», und `api.js` rechnet sie auf die Uhr der Seite um.

**Wie gemessen wird.** Lokal ist alles sofort da, und die Zeiten schwanken
von einem Laden zum nächsten um bis zu 0.5 s: zwei Fassungen lassen sich nur
abwechselnd vergleichen, mehrmals. Was das Netz kostet, zeigt ein
Dateiserver, der eine Leitung nachahmt – 20 ms Laufzeit, 100 Mbit/s für
alle Anfragen zusammen, gzip wie GitHub; ein Werkzeug zum Messen, nicht im
Repo. Er spricht HTTP/1.1, GitHub HTTP/2: dort kosten viele kleine Anfragen
weniger als hier.

Bis dahin lief alles nacheinander: erst die Oberfläche, dann die Suche nach
einem Server, dann Python, dann die 214 Dateien des Kerns, dann das
Einlesen. Beim ersten Besuch, über die nachgeahmte Leitung: Oberfläche
0.96 s, Python 4.0 s, Quellen 6.3 s, eingelesen 7.7 s, erste Rechnung
8.5–8.7 s.

**Der Kern startet sofort.** Ein kleines Modul in `index.html` stösst ihn
an, bevor die Oberfläche geladen ist – mit `async`, damit es nicht auf sie
wartet. `kernBereitstellen` startet nur beim ersten Aufruf; wer später
fragt, bekommt dasselbe Versprechen, und die Anzeige des Ladeschirms
bekommt nachgereicht, was vorher gemeldet wurde. Im Faden kommen die
Quellen, während Python lädt.

**Ein Paket statt 214 Dateien.** Die Brücke schreibt alle Quellen
zusätzlich in ein Stück, `web/kern/quellen.json` (3 MB, gepackt 0.8 MB).
Der Faden holt es mit einer Anfrage und legt jede Datei darin in sein
Dateisystem, auch das Verzeichnis `dateien.json`: die Konsole liest dort,
welche Fremdpakete beiliegen. Ein Test wacht darüber, dass das Paket zu den
Dateien passt (`quellen_stimmen`). Im Diff zeigt Git es nicht
(`.gitattributes`) – was sich darin ändert, steht schon im Diff der Quelle.

Danach, beim ersten Besuch: Server gesucht 0.2 s, Quellen 1.3 s, Python
3.9 s, eingelesen 5.3–5.5 s, erste Rechnung 6.2–6.3 s. Beim erneuten
Besuch, aus dem Zwischenspeicher des Browsers, ändert sich nichts: vorher
wie nachher 4.4–4.5 s. Ob die Quellen neben Python kommen oder nach ihm,
macht dort keinen Unterschied (abwechselnd gemessen); neben ihm spart es auf
einer langsamen Leitung die Zeit für das Paket.

**Ohne Netz, und schneller beim erneuten Besuch.** Ein Service Worker,
`sw.js`, legt in einen Speicher des Browsers, was die Seite zum Starten
braucht, rund 18 MB; danach geht sie auch ohne Netz auf. Er liegt im
Wurzelverzeichnis und nicht unter `web/`: er gilt nur für Seiten unter
seinem Ordner, und auch die Wurzel soll ohne Netz aufgehen – sie ist die
veröffentlichte Adresse. Was eine Marke trägt, kommt aus dem Speicher, ohne
zu fragen. Die Ordner unter `web/vendor/` haben je einen Speicher, benannt
nach einer Marke über ihren Inhalt: eine Veröffentlichung ohne neues Pyodide
lässt dessen 13 MB liegen. Die Seiten selbst kommen zuerst aus dem Netz und
nur ohne Netz aus dem Speicher; so bringt eine Veröffentlichung die neuen
Marken. Was in den Speicher gehört, schreibt die Brücke in `sw.js`
(`vorrat`); jede Änderung ändert ihn, und der Browser installiert ihn neu.
numpy und pandas kommen erst hinein, wenn ein Skript sie braucht, eine
Seite des Notizbuchs, sobald man sie einmal geöffnet hat.

Angemeldet wird er erst, wenn der Kern bereit ist – sonst holte er beim
ersten Besuch dieselben 18 MB ein zweites Mal, gleichzeitig mit der Seite –,
und nur, wo im Browser gerechnet wird: mit `python3 start_ui.py` stünde er
beim Entwickeln im Weg, und eine Anmeldung von früher meldet die Seite dort
ab. Aufräumen darf er nur seine eigenen Speicher (`opencivil-…`): auf
github.io teilen sich alle Seiten eines Kontos einen Ursprung.

Über die nachgeahmte Leitung, beim erneuten Besuch: die erste Rechnung nach
3.5–4.0 s statt nach 4.5 s, und übers Netz geht nur noch die Seite selbst.
Auch Python lädt so schneller, 1.6–1.9 s statt 2.5 s. Mit angehaltenem
Server, von der Wurzel aus: die Seite geht auf und rechnet, erste Rechnung
nach 3.3 s. Mit `web/manifest.webmanifest` lässt sie sich als App
installieren, mit eigenem Fenster; als Zeichen dient `favicon.svg`.

**Vorladen der Module: gemessen, nicht eingebaut.** Geplant war
`<link rel="modulepreload">` für alle Module, damit der Browser sie auf
einmal holt statt Stufe um Stufe. Seit der Kern sofort startet, wartet aber
nichts mehr auf die Oberfläche: sie ist nach 1 s fertig, der Kern nach 5 s,
und dazwischen steht der Ladeschirm. Auch mit dem lokalen Server, wo die
Oberfläche auf dem Weg liegt, brachte es nichts: «Oberfläche geladen» nach
0.60–0.62 s mit, 0.62–0.63 s ohne. Die Suche nach dem Server kam damit
sogar später, hinter den 80 Anfragen (0.6 statt 0.16 s).

**Übersetzt vom letzten Besuch.** Das Einlesen des Kerns war danach der
grösste Brocken nach Python selbst: beim Einbinden übersetzt Python jede
Datei. Vorübersetzt mitliefern ginge nur aus demselben Python wie in
Pyodide, 3.14; auf dem Rechner läuft 3.12. Also übersetzt Pyodide selbst
und merkt es sich: der Faden lässt Python die `.pyc`-Dateien schreiben,
packt sie 3 s nach dem Start in ein Stück (4.2 MB) und legt es in einen
eigenen Speicher des Browsers, `opencivil-uebersetzt`, je Dienst eines –
Kern und Konsole binden Verschiedenes ein. Beim nächsten Besuch kommen sie
vor dem Einbinden an ihren Ort (`opencivil/web/uebersetzt.py`); neu
abgelegt wird nur, was sich geändert hat.

Python prüft jedes `.pyc` dabei am Inhalt seiner Quelle (hash-basiert, PEP
552), nicht wie sonst an Zeit und Grösse. Der erste Versuch setzte allen
Quellen eine feste Zeit; nach einer geänderten Ziffer – gleich gross –
wäre still der alte Code gelaufen. Ein Test zeigt genau diesen Fall
(`test_uebersetzt`). Über die nachgeahmte Leitung, abwechselnd gemessen:
eingelesen in 0.68–0.71 s statt 1.41–1.47 s, die erste Rechnung nach
3.2 s statt 3.9–4.0 s.

Was übrig bleibt, ist Python selbst: 1.6–1.8 s, auch aus dem Speicher.

## 2026-11-20 · Sandbox je App

Der Benutzer wollte in jeder App einen Eintrag zum schnellen Ausprobieren
(2026-11-20): zuoberst, leicht golden, «Sandbox» genannt, kopierbar, aber
nicht zu löschen – statt × trägt er ↺. Gespeichert wird er mit, nach jedem
Laden der Seite beginnt er neu. Er steht in jedem Projekt und in jeder App
ausser den Materialien, Python eingeschlossen.

Die Sandbox ist ein gewöhnlicher Eintrag ihrer Liste; `Projekt.sandboxen`
sagt je Liste, welcher. So zeichnen, rechnen und zeigen alle Apps sie, ohne
von ihr zu wissen, und die Regel steht an einer Stelle statt in jeder
Eintragsklasse. ↺ (`sandbox_zuruecksetzen`) baut sie neu und behält Kennung,
Namen und Platz: wer auf sie zeigt, zeigt weiter auf sie. Fehlt sie oder
heisst sie anders, weist `pruefen` die Datei ab – das geht nur von Hand,
die Oberfläche bietet beides nicht an. Eine Kopie (⧉) ist ein gewöhnlicher
Eintrag und heisst wie ein neuer, «Platte 2», nicht «Sandbox (Kopie)».

Neu angelegt wird sie wie mit «+»: `Beschreibung.frisch` baut den Eintrag
nach seiner Vorlage, und `ERSTE_MATERIALIEN` sagt je Klasse, welches Feld
das erste Material welcher Art bekommt. Der Katalog gibt der Oberfläche
dieselbe Tafel (`erste_materialien`); bis dahin hatte jede App in `apps.js`
ihr eigenes `einrichten`. Das neue Balkensystem bringt sein Material M1, einen
Beton, darum jetzt aus dem Kern mit; `beton()` in Python füllt es.

Nicht im Bericht, nicht unter «Gesamt» und nicht im Stand oben rechts: was
dort ausprobiert wird, ist nicht das Projekt. Unter «Aktuelle Seite» steht
sie wie jeder Eintrag, und die Herleitung eines verfolgten Nachweises zeigt
alles – verfolgen lässt sich auch einer der Sandbox. Auch die Zahl auf dem
Knopf einer App und über ihrer Liste zählt sie nicht, und ihretwegen wird
kein Zeichen blau; sonst sagte jede App «hier gibt es etwas». Wer eine App
wählt, bekommt den ersten Eintrag des Projekts, die Sandbox nur, wenn es
keinen gibt.

Dafür trägt jede Warnung jetzt den Namensraum ihres Eintrags
(`kern.Warnung`): über der Herleitung stehen nur die des gewählten, unter
«Gesamt» alle ausser denen der Sandboxen. Bis dahin standen alle über jeder
Herleitung – mit der Sandbox auch das «noch nichts gezeichnet» der leeren
Analyse, in jedem Projekt.

Sie hält nichts fest (`verweise`): sonst liesse sich der einzige Beton nicht
löschen, weil die Sandbox der Platten ihn nimmt. Zeigt sie danach ins Leere,
sagt sie es am Ort, mit Namen: «der Querschnitt «Unterzug» nimmt eine
Querschnittsanalyse, die es nicht mehr gibt – eine andere wählen.» Bis dahin
nannte der Satz die Kennung. Eine Platte ohne Beton hielt bis dahin das ganze
Projekt an («'beton' darf nicht leer sein»); jetzt rechnet nur sie nicht.

Den Querschnitt einer Sandbox darf nur eine Sandbox nehmen: sie beginnt
nach jedem Laden neu, und ein gewöhnliches Balkensystem rechnete dann still
mit anderem. Die Auswahl bietet sie darum nicht an; die Kopie eines
Sandbox-Systems, die ihn noch nimmt, rechnet nicht und sagt, warum.

Anfragen: `mappe_oeffnen` ersetzt `mappe_pruefen` und legt fehlende
Sandboxen an, mit `frisch` beginnen alle neu (Laden der Seite);
`sandbox_zuruecksetzen` für ↺. Das Beispiel und der Katalog (`neu.projekte`)
kommen mit Sandboxen, `Projekt.neu()` in Python ohne. Die frischen
Sandboxen rechnen mit: beim Beispiel kostet die erste Rechnung rund 0.06 s
mehr.

## 2026-11-20 · Mehrere Projekte in einer Datei

Der Benutzer wollte mehrere Projekte nebeneinander (2026-11-20). Oben in
der linken Spalte steht je Projekt ein Reiter, dazu «+»; darunter stehen
nur die Einträge des gewählten.

Im Kern hält `Mappe` (`projekt/mappe.py`) die Projekte. Gerechnet wird
weiter je Projekt; die Mappe prüft nur, was zwischen ihnen gilt: jedes hat
einen Namen, keine zwei denselben, und es gibt mindestens eines. Am Namen
wählt man ein Projekt – ohne ihn stünde ein leerer Reiter da, mit einem
doppelten zwei gleiche. Eine Meldung aus einem Projekt nennt es vorn:
«Projekt 'Halle', Platte 'Decke über EG': …», denn in jedem Projekt kann
eine Platte so heissen. Eine Datei mit einem einzelnen Projekt, wie sie
bis 2026-11-20 geschrieben wurde, ist eine Mappe mit diesem einen, und ihre
Meldungen bleiben, wie sie waren.

Der Ergebnisspeicher (`web/speicher.py`) legt nach Projekt und Kennung ab.
Richtig wäre es auch ohne – der Stempel ist der Inhalt –, aber jedes
Projekt räumte beim Rechnen die Ergebnisse des anderen weg, und der Wechsel
zurück rechnete alles neu. Gemessen beim Beispiel: 0.02 s statt 0.2 s.

Die Oberfläche hält die Mappe in `zustand.mappe`; `zustand.projekt` bleibt
das gezeigte, und alles Bisherige rechnet und zeichnet weiter daran. Ein
Wechsel geht über `projektSetzen`: es räumt Lösung, Auswahl und offene
Fenster ab und meldet «neu», worauf die Seite rechnet. Kehrt man zurück,
stehen App und Auswahl wieder, wie man sie verlassen hat – bis die Seite
neu lädt. Bis die erste Rechnung da ist, sagt die rechte Spalte «rechnet …».

Im Browser liegt die ganze Mappe unter `opencivil.mappe`, mit dem gewählten
Projekt. Was unter `opencivil.projekt` lag, wird beim ersten Laden das
einzige Projekt der Mappe; der alte Schlüssel verschwindet beim ersten
Ablegen.

«Speichern» schreibt alle Projekte in eine Datei. Mit einem Projekt heisst
sie wie das Projekt, wie bisher; mit mehreren «Projekte 2026-11-20», denn
kein Projektname steht für alle. «Öffnen» fragt, ob die Datei ersetzt oder
dazukommt (Benutzer, 2026-11-20). Kommt sie dazu, bekommt ein Name, den es
schon gibt, eine Nummer: «Halle» wird «Halle 2». Die Frage stellt
`rueckfrage` (fenster.js) im selben Dialogfenster wie die Wahl eines
Materials.

Ein neues Projekt baut der Kern, `Projekt.neu`: mit C25/30 und B500B, ohne
Bauteile – so rechnet die erste Platte gleich. × steht nur am gezeigten
Reiter und nie am letzten: ohne Projekt gäbe es nichts zu zeigen.

## 2026-11-20 · Rechenwerte je Material, in jedem Modul

Bis dahin wählte nur die Tragsicherheit der Querschnittsanalyse ihre Werte
je Material. Jedes andere Modul hatte einen Wertesatz für alle: die
Tragsicherheit, das Knicken, die Stahlspannungen und die
Spannung-Dehnung-Analysen der Platte, dieselben Kapitel der Analyse und
E_eq im Balkensystem. Der Benutzer wollte die Darstellung der
Querschnittsanalyse überall (2026-11-20).

Ein Modell im Kern: `Wertesaetze` in `querschnitt/gesetzwahl.py`, je
Baustoff sein Satz, unveränderlich und vergleichbar – eine Wahl ist
Schlüssel von Zwischenspeichern, und zwei gleiche Wahlen teilen sich eine
Linie. Haben alle Baustoffe denselben Satz, ist es dieselbe Wahl wie ein
Satz für alle (`Wertesaetze.je`). Ohne das rechneten die Kennzahlen, die
fest mit Bemessungswerten wählen, eine zweite Linie neben der gleichen der
Tragsicherheit, und der Bericht hatte einen Abschnitt mehr.

Im Projekt hält jedes Modul `werkstoffsaetze`, je Kennung eines Materials
seinen Satz (`je_material` in `projekt/lesen.py`). Eine Zuordnung, keine
Liste: zwei Wahlen für dasselbe Material gibt es so nicht, und die Prüfung
dafür fiel weg, mit ihr `WerkstoffwahlEintrag`. Was ein Material ohne
eigene Wahl nimmt, steht am Feld – Bemessungswerte, im Gebrauch
charakteristische – und geht als `vorgabe` in den Katalog. Die
Querschnittsanalyse hält dazu `betongesetze`, je Beton Parabel oder Block.

Gemischt heisst ein Widerstand R, weder Rd noch Rk (nach Vorgabe, nicht
nachgeschlagen), und die Rechenwahl der Herleitung nennt jeden Baustoff:
«C30/37: charakteristisch f_ck, B500B: Bemessungswerte f_yd». Mit einem
Satz für alle bleibt die Zeile, wie sie war; der Bericht des Beispiels ist
Zeichen für Zeichen gleich. «Jeder Nachweis» hat dafür eine Platte
«Gemischt».

Die Rechenart bleibt je Modul. Nur die Tragsicherheit der Analyse wählt das
Gesetz je Beton, wie bisher: eine Platte hat ohnehin einen Beton, und im
Gebrauch und beim Knicken gehören Handrechnung und elastisch zum ganzen
Querschnitt, nicht zu einem Baustoff. (Ersetzt am 2026-11-25: die Rechenart
steht jetzt in jedem Modul je Beton, siehe dort.)

In der Oberfläche baut `werkstoffzeilen` (nachweise.js) die Zeilen für
alle Module: Name, Schalter «Bemessung | charakteristisch», in der
Tragsicherheit der Analyse beim Beton das Gesetz darunter. Welche
Materialien es sind, sagt der Ort: die Platte ihre beiden Felder, die
Analyse der Kern mit ihrer Zeichnung, E_eq die Platte oder Analyse, aus
der sein Querschnitt kommt. Kommt die Antwort zu einer Zeichnung, zeichnet
jedes offene Fenster neu – auch der Querschnitt eines Balkensystems wartet
auf sie. Eine Wahl schreibt nur die Materialien, die das Bauteil jetzt hat:
sonst kehrte die Wahl eines ausgewechselten Materials still zurück, sobald
man es wieder wählt.

## 2026-11-20 · Die Decke sagt jede Meldung einmal

Die Decke meldete je Fall: bei vier Lastfällen und drei Kombinationen stand
derselbe Satz siebenmal da, und ein Streifen ohne Platte gab je Fall eine
eigene Zeile (Benutzer, 2026-11-20).

Jetzt sammelt der Kern (`Ergebnis.fallmeldungen` in `decke/rechnung.py`):
gleiche Sätze stehen einmal, vorn die Fälle, in denen sie stehen –
«In allen Fällen: …» oder ««g», «q»: …». Fällt aus demselben Grund in
mehreren Fällen etwas aus, steht der Grund einmal, die Kraft je Fall
dahinter: «12 Streifen tragen nicht – … Es fallen aus: «Eigengewicht»
30 kN, «Auflast» 9 kN, «GZT» 79.7 kN.» Dafür ist ein Ausfall eine eigene
`Meldung`, `Ausfall`, mit Grund und Kraft; im Fall selbst – für die
Zeichnung des gewählten Falls – bleibt der ganze Satz. Streifen mit
Last, die auf keiner Platte liegen, nennt eine Meldung je Fall, wie schon
die ausgefallenen Träger («Auf 3 Streifen liegt Last, aber sie liegen auf
keiner Platte.»). Die Herleitung und die Karte der Fälle nehmen dieselbe
Liste; mehr als drei Meldungen klappen in der Karte zusammen, mit ihrer
Anzahl, offen, solange eine ein Fehler ist. Eine Platte, die nur auf einer
Wand liegt, gab bei drei Lastfällen und einer Kombination acht Zeilen,
jetzt zwei.

Nebenbei: eine Kraft in einer Meldung der Decke stand ab 1000 kN mit
Exponent da, «1.5e+03 kN». Jetzt «1500 kN» (`lasten.kn`, drei gültige
Stellen wie bisher).

Die anderen Apps mit Lastfällen durchgesehen, dort wiederholt sich nichts:
das Balkensystem meldet für das ganze System; je Fall nur eine Last an
einem Ort ohne Stab, und eine Kombination meldet nicht noch einmal, was
ihre Lastfälle schon melden (`melden=not kombination` in
`stabwerk/system.py`). Platte, Querschnittsanalyse, Pfahl, Grundbruch und
Setzung melden je Nachweis, und die Hinweise unter der Nachweistabelle
stehen schon je Grund gebündelt (`hinweise` in
`bericht/zusammenfassung.py`).

## 2026-11-20 · Ein eigenes Material beginnt mit den Werten des ersten Betons

Ein eigenes Material im Balkensystem begann mit den Werten eines
Baustahls: E = 200 000 N/mm², ρ = 7850 kg/m³, im Raum G = 80 000 N/mm² –
als Zahlen im Code. Der Benutzer will die Werte eines Betons (2026-11-20).

Jetzt beginnt es mit denen des ersten Betons eines Projekts
(`ERSTER_BETON`, C25/30), aus seiner Vorlage gerechnet
(`beton.sortenwerte`) und gerundet wie im Bericht: E = E_cm = 32 075 N/mm²,
ρ = ρ_sb = 2500 kg/m³, G = G_cm = 13 365 N/mm². Welcher Kennwert des Betons
zu E, ρ und G gehört, sagen dieselben `Materialkennwert`e, mit denen ein
Stab aus Beton rechnet (`E_MODUL`, `DICHTE`, `SCHUBMODUL`);
`EIGENES_MATERIAL` in `projekt/balkensystem.py` hält die Zahlen.

## 2026-11-20 · Neues heisst wie sein Knopf

«+ Einwirkung» legte eine «Tragsicherheit 1» an, «+ Lastfall» der
Querschnittsanalyse ebenso, «+ Knicknachweis» ein «Knicken 1», und die
erste Schicht eines neuen Pfahls hiess «Kies». Der Benutzer will
generische Namen, die zum Knopf passen (2026-11-20).

Der Knopf `anfuegenKnopf` steht jetzt in `faelle.js`, bei der Zeile der
Fälle, und benennt, was er anlegt: `tun` bekommt `name(liste)`, «Wort» und
die kleinste freie Nummer. Setzung, Grundbruch, Pfahl und die
Querschnittsanalyse bauten ihren Knopf bis dahin selbst; sie nehmen ihn nun
auch. Neu heissen «Einwirkung 1» (auch die erste einer neuen Platte im
Kern), «Lastfall 1», «Knicknachweis 1», «Verformungsfall 1» und die erste
Pfahlschicht «Schicht 1». Wie der Benutzer es will, bleiben die
Standardfälle (Eigengewicht, Auflast, Nutzlast, GZT, GZG) und die
Gebrauchsfälle, die nach ihrer Art heissen («Häufig 1»).

## 2026-11-20 · Die rechte Tafel wird rötlich, solange sie nicht zur Eingabe passt

Nach einer Änderung stand rechts bis zur neuen Antwort das alte Ergebnis,
ohne dass man es ihm ansah; scheiterte die Rechnung, blieb es stehen. Der
Benutzer will die rechte Spalte rötlich, solange sie nicht zur Eingabe
passt (2026-11-20).

Die Seite merkt sich, zu welcher Eingabe die gezeigte Antwort gehört
(`geliefert` in `app.js`, der `rechenstand` beim Abschicken). Weicht die
Eingabe ab, trägt `#tafel-bericht` `ist-ueberholt`: ein hellroter Grund
(`--schlecht-hell`), erst nach 0.3 s, damit eine schnelle Rechnung nicht
aufblitzt. Er bleibt, wenn die Rechnung scheitert, und gilt nicht, wo die
App rechts selbst etwas zeigt (Python). `gerechnet` taugte dafür nicht: es
gilt schon, wenn die Anfrage abgeht. Im Browser-Fenster der Prüfung lief der
Übergang nicht, weil es keine Bilder zeichnete (`requestAnimationFrame`
stand still); ohne Übergang und im Bildschirmfoto stimmt die Farbe.

## 2026-11-20 · «Kriechzahl φ» heisst überall gleich

Die Kriechzahl stand an vier Stellen dreimal anders da: über dem Feld der
Rechenwahl ein φ allein, bei der Zwängung auf Biegung ein φ in anderer
Schrift, nur bei der Verformung «Kriechzahl φ». Der Benutzer will überall
dasselbe und das φ schöner (2026-11-20).

Jetzt steht überall «Kriechzahl φ», wie der Kern das Feld nennt
(`feldangabe(...).heisst`) – `kriechzahlName` in `nachweise.js`. Das φ
setzt `mitFormelzeichen` (`mathe.js`) in die Formelschrift, so gross wie in
einer gesetzten Formel, und klein, wo ein Spaltenkopf gross schreibt. Die
Spalte der Kriechzahl in der Rechenwahl ist dafür so breit wie ein
Zahlenfeld (`--zahlbreite`): «KRIECHZAHL φ» braucht 63 px, vorher hatte
sie rund 60. `mitKopf` nimmt statt `formel` einen Knoten als Kopf.

## 2026-11-20 · Eine feine Linie trennt die Fälle einer Liste

Ein Fall mit Zahlen unter dem Namen ist zwei oder drei Zeilen hoch; in einer
Liste lief einer in den nächsten über, man sah nicht, welche Zahlen zu
welchem Namen gehören (Benutzer, 2026-11-20). Jetzt trennt eine feine Linie
(`--rand`) jeden Fall vom vorigen – eine Regel im Stilblatt für alle
Listen aus `fallzeile` und für die Lastfälle von Balkensystem und Decke
(`.bs-fall`). Der erste Fall unter dem Kopf hat keine.

## 2026-11-20 · Die sechs Lasten eines Lastfalls stehen auf einer Zeile

In der Tragsicherheit der Querschnittsanalyse standen N, M_y, M_z und
darunter V_y, V_z, T – drei je Zeile, weil sechs Zahlenfelder nicht in ein
Panel passen. Der Benutzer will alle sechs auf einer Zeile und das Fenster
breiter (2026-11-20).

Ein Kapitel kann jetzt `breit` sein. Sein Fenster (`.fenster.ist-breit`) ist
dann bis 628 px breit, und die mittlere Tafel wird, solange es offen ist,
672 px breit – mit Platz für die Rollleiste. Ganz oder gar nicht: blieben
der rechten Tafel so keine 300 px, bleibt die Mitte, wie sie ist
(`round(down, …)` im Stilblatt), und die Felder brechen wie bisher nach
drei um (Containerabfrage unter 600 px). Eine von Hand gezogene Mitte
bleibt ebenso. Gemessen: bei 1600 px Fensterbreite sechs auf einer Zeile,
bei 1200 px drei. `fallkopf` nimmt dafür eine `klasse` wie `fallzeile`;
`JE_ZEILE` fällt weg.

## 2026-11-20 · «mm | Stk» ist ein Schalter wie alle anderen

Hinter der Teilung einer Lage und der Bügel in y stand die Einheit selbst
als Umschalter – blau, gestrichelt unterstrichen, nur die geltende Stellung
zu sehen; so sparte sie 2026-10 eine Spalte. Der Benutzer will ihn wie alle
anderen Schalter (2026-11-20): jetzt `zweiSchalter` mit den Stellungen
«mm | Stk», knapp (`ist-knapp`), in der Spalte, die der Knopf «günstig» bis
dahin belegte.

## 2026-11-20 · Die Zulage liegt auf einer eigenen Zeile

Der Knopf «ungünstig/günstig» einer Lage stand am Ende der Zeile der
Zulage, in einer Spalte, die schmaler war als er – er ragte über «mm».
Jetzt steht er unter den beiden Posten, als Schalter «ungünstig | günstig»
wie jeder andere, je Stellung mit dem Bild der zwei Stäbe im Schnitt; der
Titel einer Stellung sagt, welche Kante bündig liegt. Auf der eigenen Zeile
hat das Paar den Platz, den es am 2026-11-19 neben den Zahlen nicht hatte
(Benutzer, 2026-11-20). Die Zeile der Posten hat damit eine Spalte weniger.

## 2026-11-20 · Die Bilder nehmen ihre Einheiten aus den Daten

Drei Bilder schrieben Zeichen und Einheiten selbst: die Verläufe des Pfahls
(`GROESSEN` in `pf_verlauf.js`, ein Spiegel von `pfahldaten.VERLAEUFE` samt
Schlüsseln der Grenzen), die Diagramme der Platte (rund 35 Einheiten in
`platte_bilder.js`) und die Pfahlskizze. Benennt der Kern eine Grösse um,
verschwand ihr Bild still; die Skizze sagte schon kN/m², wo die Maske kPa
zeigt.

Jetzt bringen die Daten ihre Grössen mit (`Anzeigegroesse`): je Verlauf des
Pfahls Zeichen, Einheit, Stellen, Werte und Grenze; je Diagramm der Platte
`groessen` (`diagrammdaten.MN`, `MV`, `NEIGUNG`), mit denen der Kern auch
umrechnet – Einheit der Zahl und Einheit daneben können nicht mehr
auseinanderlaufen. Die Bilder setzen sie mit `achsentitel` und `masszahl`
(`achsen.js`) zusammen. Die Pfahlskizze schreibt die Kennwerte der
Schichten in der Einheit ihres Felds (`feldangabe`) – dafür sagt der
Katalog jetzt auch, ob eine Einheit an der Zahl klebt (`klebt`, «30°»).
Masse, die eine Skizze massstäblich zeichnet, schreibt sie weiter selbst
an: ihr Massstab hängt ohnehin an der Einheit.

Sichtbar anders: in der Pfahlskizze kPa statt kN/m² bei c'_k, s_u,k, q_s,k
und q_b,k, unter den Verläufen «p [kPa]». Sonst steht da dasselbe wie
vorher. Ein Verlauf ohne Farbe meldet sich laut, statt unsichtbar zu sein.

## 2026-11-20 · Das Durchstanzen holt seine Maske aus dem Kern

Der letzte der vier: die Tafel steht in `opencivil/durchstanzen/stelle.py`
(`VORGABEN`), die Maske hatte sie in `MASSE`, `ROTATION` und zwanzig Zeilen
von Hand. Welche Felder eine Stelle liest, sagt weiter `eingaben_fuer`; der
Katalog gibt dazu die festen Felder (`fest`), so ist die Menge der Maske
jetzt genau die des Nachweises. Anders als die andern verteilt das
Durchstanzen seine Gruppen auf mehrere Tafeln, mit dem Grundriss dazwischen:
`eingabegruppen` gibt die Zeilen je Gruppe, und eine Gruppe des Kerns, die
keine Tafel nimmt, meldet sich laut, statt still zu fehlen.

Sichtbar anders:

- Die Biegebewehrung steht in einer Karte: «Stabdurchmesser in x ∅_x»,
  «Stababstand in x s_x» und so fort, statt der Karten «In x» und «In y».
- a_x und a_y heissen in der Herleitung «Abstand vom linken» und «vom
  unteren Plattenrand» statt «vom Plattenrand in x/y», in der Maske «Abstand
  vom linken/unteren Rand». Vorher hatte a_x drei Namen.
- Die Exzentrizität hat in der Herleitung einen eigenen Kasten, wie in der
  Maske ihre eigene Karte.
- r_s heisst in der Maske kurz «Momentennullpunkt in x»; die lange
  Beschriftung war abgeschnitten.
- Die Titel über den Feldern sind die Beschreibung der Herleitung mit
  Hinweis.

## 2026-11-20 · Der Pfahl holt seine Maske aus dem Kern

Der dritte nach Grundbruch und Setzung: die Tafel der Vorgaben steht in
`opencivil/pfahl/pfahl.py` (`VORGABEN`, `JE_SCHICHT`) statt zweimal – im
Kern als Tupel, in `pfahl.js` als Karten. Welche Felder gelten, sagen dort
die Wahlen: Art und Tragglied den Querschnitt, die Grundlage den äusseren
Widerstand, Verhalten und Mantel die Felder einer Schicht. Die Maske setzt
nur noch Schalter und Materialien zu ihrer Gruppe. Eine Schicht hat vier
Gruppen in einer Karte (`eingabezeilen`); deren Titel sagen nur, wo die
Schalter für Verhalten und Mantel stehen.

Sichtbar anders:

- Die Karten folgen der Herleitung: Pfahl, Grundwasser, Äusserer
  Widerstand, Fuss, Querschnitt, Querlast – vorher stand der Querschnitt vor
  dem äusseren Widerstand.
- Der Fuss hat eine eigene Karte: der Schalter heisst dort «Spitzendruck»
  (gerechnet, eingegeben, trägt nicht), darunter q_b,k oder das Abscheren.
  Vorher stand er in der Karte des äusseren Widerstands. In der Herleitung
  steht q_b,k im Kasten «Fuss» statt «Äusserer Widerstand».
- Beim Mikropfahl heisst die Karte «Querschnitt» wie in der Herleitung,
  nicht mehr «Tragglied».
- Die Wandreibung heisst k_δ wie in der Herleitung, nicht mehr δ/φ'_k.
- Der Titel über jedem Feld ist die Beschreibung der Herleitung mit Hinweis
  und Normstelle; beim Umrechnungsfaktor η_a etwa «Umrechnungsfaktor des
  äusseren Widerstands – höchstens 0.7 (SIA 267:2013, 9.5.2.2.5, (48))».

## 2026-11-20 · Die Setzung holt ihre Maske aus dem Kern

Wie beim Grundbruch: die Tafel der Vorgaben steht einmal, in
`opencivil/geotechnik/setzung.py` – `VORGABEN` für Fundament, Pressung und
Nachweis, `JE_SCHICHT` für die Felder jeder Schicht. Die Herleitung zeigt je
Schicht einen Kasten mit nummerierten Zeichen (d₁, M_E,1), die Maske je
Schicht eine Zeile; «#» in der Beschreibung steht für die Schicht
(`Feld.nummeriert`). Auch die Spalten der Schichtentabelle, ihre Köpfe und
Schrittweiten kommen jetzt aus dem Kern. Der Schalter starr/schlaff ist keine
Zahl und bleibt in der Maske, hinter Breite und Länge.

Sichtbar anders sind nur die Titel über den Feldern: die Beschreibung der
Herleitung mit Hinweis und Normstelle. Über der Spalte M_E etwa
«M_E-Wert der Schicht, Erstbelastung (Kap. 5.3, 8.5; SIA 267:2013,
5.3.2.8)» statt «M_E-Wert der Erstbelastung».

## 2026-11-20 · Der Grundbruch holt seine Maske aus dem Kern

Die Maske des Grundbruchs schrieb die Tafel der Herleitung ab: Gruppen,
Felder, Zeichen und Hinweise. Ein neues Feld des Kerns wäre dort nie
erschienen, und die Zeichen liefen schon auseinander.

Jetzt steht die Tafel einmal im Kern (`VORGABEN` in
`opencivil/geotechnik/fundament.py`, die Bausteine in
`opencivil/core/vorgaben.py`), mit der kurzen Beschriftung der Maske neben
der Beschreibung der Herleitung – die Maske schneidet lange Beschriftungen
ab, samt Zeichen. Die Maske baut ihre Karten daraus (`eingabekarten` in
`bausteine.js`); ein Test prüft, dass Maske und Herleitung dieselben Felder
in derselben Folge zeigen. Die Herleitung bleibt, wie sie war.

Wo Kern und Maske verschieden schrieben, gilt jetzt der Kern:

- «Gelände und Grundwasser»: zuerst die Tiefe des Grundwassers t₁, dann die
  Geländeneigung β – vorher umgekehrt.
- Sohlreibung: das Zeichen ist k_δ wie in der Herleitung, nicht mehr
  δ_k/φ_k; das Verhältnis steht im Titel über dem Feld.
- Der Titel über jedem Feld ist die Beschreibung der Herleitung mit dem
  Hinweis der Maske und der Normstelle. Beim Grundwasser etwa «Tiefe des
  höchsten Grundwasserspiegels unter Terrain (SIA 267:2013, 4.2.2.3)» statt
  «Oberkante Terrain bis zum höchsten möglichen Grundwasserspiegel».

## 2026-11-20 · Eine Last an einem Knoten hat keine Stelle

Das Fenster einer Last an einem Knoten zeigte das Feld «Stelle» in % der
Linie, wie eine Einzellast auf einem Stab. Eine Zahl darin hielt das ganze
System an: eine Knotenlast hat kein solches Feld. Jetzt fragt das Fenster
nur bei einer Last auf einer Linie nach der Stelle; wo die Last liegt, sagt
ein einziger Wert statt zweier Schalter, die sich widersprechen konnten.

## 2026-11-20 · Kraft oder Moment an einem Knoten sagt der Kern

Ob eine Last an einem Knoten eine Kraft oder ein Moment ist und ob sie in
kN oder kNm steht, schrieb die Oberfläche an vier Stellen von Hand: im Feld,
in der Liste, im Titel und in der Zeichnung. Eine Art, die es nicht gibt,
war im Feld ein Moment, in Liste und Zeichnung eine Kraft.

Jetzt ist die Art eine Wahl im Kern (`Knotenlastart`), mit der Einheit
derselben Last auf einem Stab: eine Kraft an einem Knoten steht in kN wie
eine Einzellast, ein Moment in kNm wie ein Einzelmoment. Der Katalog gibt
die Arten wie die der Stablasten, und alle vier Stellen lesen dort. Am
Bildschirm ändert sich nichts.

## 2026-11-20 · Ein Mass prüft sich wie ein Feld

Die Masse der Vorlagen – in der Querschnittsanalyse und bei den
Stabquerschnitten des Balkensystems – und die Kennwerte von Hand hatten
keine Beschreibung wie ein Feld. Zwei Klassen `Mass` prüften selbst, mit
eigenen Sätzen, und die Fenster setzten eigene Mindestwerte: 1 in der
Querschnittsanalyse, 0 im Balkensystem, wo eine 0 erst beim Rechnen
auffiel. Die Kennwerte von Hand sagten «A, I_y, I_z und I_T müssen grösser
als null sein.», ohne zu sagen, welcher.

Jetzt beschreibt jedes Mass und jeder Kennwert seine Grenze wie ein Feld,
mit demselben Baustein im Kern (`opencivil/core/bereich.py`). Die Maske
weist eine 0 sofort ab, mit dem Satz des Kerns («Breite b muss grösser als
null sein: 0 ist nicht übernommen.»), und die Einheit kommt mit. Der
Achsabstand der Stäbe im Vorlagenfenster ist ein Mass wie die anderen;
seine Vorgabe von 50 mm stand vorher an vier Stellen.

Nimmt das Vorlagenfenster eine Zahl nicht, zeigt es wieder die zuletzt
übernommene – nicht die, mit der es aufging.

## 2026-11-20 · Dieselbe Grenze nur noch am Feld

Drei Stellen prüften eine Zahl ein zweites Mal, die ihr Feld schon prüft,
mit eigenen Sätzen:

- die Decke acht Grenzen – Dicke, Streifenbreite, Grösse der Stützen,
  Breite und Stufe der Unterzüge, die Anteile. Sie griffen nie: das Feld
  hielt die Zahl vorher auf.
- der Dienst der Bewehrungssuche die Teilungen, bevor die Suche sie mit dem
  Feld prüfte. Eine Teilung 0 hiess dort «Eine Teilung muss grösser als
  null sein, angegeben sind 0 mm.», überall sonst «Teilung muss grösser als
  null sein, angegeben ist 0 mm.».
- der Katalog Vorgabe und Höchstwert des Beiwerts k der Duktilität, neben
  dem Feld, das beides schon trägt.

Jetzt prüft nur das Feld. Was kein Feld sagen kann, bleibt, wo es war: wie
die Teile der Decke liegen, der Elastizitätsmodul aus dem Beton. Eine Liste
von Zahlen – die Teilungen der Suche – ist nie leer; das sagt jetzt ihr
Feld («Teilung: noch keine Zahl – es braucht mindestens eine.») und nicht
mehr die Suche.

## 2026-11-20 · Jedes Zahlenfeld kennt seine Grenzen

66 Zahlenfelder hatten im Kern keine Grenze – darunter Teilung und
Stabzahl der Bewehrung, die Bügel, die Federn und die Zahlen der Zeichnung.
Die Oberfläche setzte eigene Mindestwerte, die nur die Pfeile bremsten:
eine getippte Teilung 0 nahm das Feld an, und erst die ganze Platte
rechnete nicht mehr.

Jetzt hat jedes Zahlenfeld seinen Bereich, und die Maske weist ab, was
ausserhalb liegt, mit dem Satz des Kerns: «Teilung muss grösser als null
sein: 0 ist nicht übernommen.» Ein Test wacht, dass jedes neue Zahlenfeld
einen bekommt. Die Einheiten der Federn stehen am Feld statt in einer
eigenen Tabelle; Platte, Knicken und Querschnittsanalyse lesen ihre
Einheiten ebenso vom Feld. Eine Teilung von null weist das Feld auch ohne
Bügel ab: es kennt den Durchmesser nicht, und null ist nie eine Teilung.

Kommt eine falsche Zahl doch an – aus einer Datei oder einem Skript –,
nennt die Meldung das Element jetzt wie die Maske: «Lage 2» statt «lagen
2», «Linie 3» wie in der Zeichnung der Querschnittsanalyse statt
«stablinien 3», «A1» wie im Balkensystem statt «lager 1».

## 2026-11-20 · Zwei Testdateien geteilt

`tests/test_balkensystem.py` hatte 1146 Zeilen, `tests/test_nachweis_mn.py`
1006 – über der Grenze, ab der man eine Datei nicht mehr liest, sondern
durchsucht. Die Querschnitte und Materialien der Balkensysteme stehen jetzt
in `test_balkensystem_querschnitte.py`, der Plattenquerschnitt in
`test_plattenquerschnitt.py`; was beide Hälften brauchen, der Träger und
die Platten der Tests, in `tests/traeger.py` und `tests/platten.py`. Die
Tests selbst sind dieselben.

## 2026-11-20 · Jede Art eines Stabquerschnitts hat ihre Felder

Ein Querschnitt im Balkensystem kommt aus einer Vorlage, einem Stahlprofil,
Kennwerten von Hand, einer Platte oder einer Querschnittsanalyse. Die Arten
teilten sich zwei Felder: die Masse hiessen je nach Art Abmessungen oder A
und I, der Bezug Platte oder Analyse. Darum räumte die Oberfläche beim
Umschalten ab, was der Kern sonst abwies – dreimal nachgebessert, zuletzt
für die Wahl E₀ oder E_eq. Wer zurückschaltete, fand leere Felder.

Jetzt hat jede Art ihr eigenes Feld, und umschalten setzt nur die Art. Wer
etwa A = 1000 mm² von Hand eingibt, auf «Vorlage» und wieder zurück
schaltet, findet die 1000 wieder (Benutzer, 2026-11-19). Ebenso die Wahl
E_eq: bei einer Vorlage gilt sie nicht und wartet, statt dass der
Querschnitt nicht rechnet.

## 2026-11-20 · Ein Fehler trägt Ort und Grund getrennt

Was einem Bauteil noch fehlt, sagt ein Hinweis an seiner Stelle («Nichts zu
rechnen: noch keine Bewehrung.»), und der Rest rechnet weiter. Der Hinweis
entstand auf zwei Wegen: drei Baufunktionen gaben «unfertig» selbst zurück,
die anderen warfen einen Fehler, den der Aufbau fing. Der Fehler trug den
Ort nur im Text, «Platte 'Decke': …», und der Aufbau schnitt ihn wieder
heraus, damit am Ort nur der Grund stand. Je nach Weg hiess der Ort zudem
anders: eine leere Querschnittsanalyse «Querschnittsanalyse 'A'», eine mit
einem falschen Wert «Querschnitt 'A'».

Jetzt trägt der Fehler Grund und Ort getrennt, und jede Baufunktion wirft,
auch was nur fehlt. Am Ort steht der Grund ohne den Ort, tiefer gelegene
mit dem Rest davor («Schicht 2: …» beim Pfahl). Was dem Pfahl an Boden
fehlt, prüfen seine Regeln mit den übrigen. Eine Querschnittsanalyse heisst
in jeder Meldung «Querschnittsanalyse 'A'», wie an der Oberfläche. Sonst
lauten die Meldungen wie vorher.

## 2026-11-20 · Die Normalkraft der M-V-Kurve gehört zur Platte

Unter dem Bild «Querkraft über Moment» stellt man ein, für welche
Normalkraft die Kurve gilt. Die Zahl lebte bisher in der Oberfläche neben
dem Projekt und hatte zwei Wege in den Kern: sie ging bei jedem Rechnen mit,
und eine eigene Anfrage baute für die Kurve das ganze Projekt neu. Nach dem
Neuladen galt still wieder die Normalkraft des ersten Falls.

Jetzt ist sie ein Feld der Platte und wird mit dem Projekt gespeichert. Wer
sie ändert, ändert das Projekt, und es wird gerechnet wie nach jeder
Eingabe. Leer gilt die des ersten Falls; das Feld zeigt sie blass, und der
Satz daneben nennt den Fall, aus dem sie kommt. Das Bild findet die Platte über das gebaute Bauteil, das jetzt seinen Eintrag
kennt (`Bauteil.eintrag`; Kennung und Name kommen von dort).

## 2026-11-20 · Eine Stelle entscheidet, ob die Linie geteilt wird

Das Knicken und die Kennzahlen brauchen eine Resistenzlinie. Wählen sie wie
die Tragsicherheit, nehmen sie deren Linie, sonst bauen sie eine eigene.
Das entschieden beide je selbst, an sechs Stellen: für die Eingänge, den
Befund und die Linie. Der Vergleich der Wahlen übersah zudem den
Elastizitätsmodul – eine Parabel mit E_cd hätte die Linie einer mit E_cm
bekommen. Heute kommt das nicht vor, weil kein Kapitel den Modul seiner
Linie anders setzt.

Jetzt entscheidet die `Linienquelle` neben `resistenzlinie`, einmal: sie
gibt die Eingänge, den Befund und die Linie. Die Gleichheit ist eine Methode
der Rechenwahl und vergleicht Kriechzahl und Modul, wo ein Gesetz am Modul
hängt. Zahlen und Bericht bleiben gleich.

## 2026-11-20 · Die Decke rechnet ihre Träger wie Stäbe

Ein Streifen der Decke ist ein Durchlaufträger. Seine Lagerkräfte kamen
schon aus den Elementen des Stabwerks, Querkraft und Moment aber integrierte
die Decke ein zweites Mal selbst, mit eigener Regel für gleiche
Extremwerte. Jetzt rechnet sie wie ein ebener Stab, starr
(`ebener_verlauf` mit `EI = ∞`); ihre Stücke sind die des Stabwerks.

Die Regel für gleiche Extremwerte gilt nun auch für die Stäbe: was sich nur
in der Rundung unterscheidet, ist gleich, und es gilt die vorderste Stelle.
Bisher lag bei einem Stab, der sich nirgends biegt, der grösste Wert dort,
wo das Rauschen der Rechnung am grössten war – ein schiefer, längs
gedrückter Kragarm nannte für seine Durchbiegung «0.00 mm bei x = 2.10 m».
Jetzt steht dort x = 0. Die grösste Verschiebung wird am Betrag verglichen,
nicht an seinem Quadrat, damit die Rundung in m zählt.

Über alle Stäbe gilt dieselbe Regel: bei gleichem Wert der erste Stab, beim
massgebenden Wert bei gleichem Betrag der positive (`massgebender` statt des
Schlüssels `nach_betrag`). In den Beispielberichten rücken so nur Stellen in
den Tabellen der Extremwerte nach vorn, kein Wert ändert sich – ein Moment
von −1.2 kNm über den ganzen Stab stand bei «kleinst x = 0.00, grösst
x = 4.00», jetzt bei beiden x = 0.00.

## 2026-11-20 · Die Kennzahlen rechnen die Querkraft mit ihrem Nachweis

Unter jeder Platte steht ihr Querkraftwiderstand ohne Einwirkung. Gerechnet
haben ihn die Kennzahlen selbst: sie lasen die Eingänge des Nachweises,
stellten Beiwerte und Stahl eigens zusammen, für die Höhen sogar einen Satz
Beiwerte voller Nullen, und riefen die Formel mit eigener Liste. Eine neue
Grösse der Bügel, nur im Nachweis eingeführt, hätte den Widerstand unter der
Platte still abweichen lassen.

Jetzt löst der Nachweis seine Eingänge selbst – ohne Bügel zu
`Kurvenbeiwerte`, mit Bügeln zu `Buegelwerte` – und rechnet daran je
Zugseite: `Kurvenbeiwerte.widerstand` und `Buegelwerte.suche`. Fall, Kurve,
Bild über der Neigung und Kennzahl rufen dieselbe Rechnung. Was die
Kennzahlen lesen, sagt der Nachweis (`bezuege_ohne_faelle`); bisher nahmen
sie alle seine Eingänge und filterten die der Fälle über den Namen weg.
Welcher Ansatz gilt, entscheidet sich einmal. Die Zahlen und der Bericht
bleiben gleich.

## 2026-11-20 · `plt.grid` wirkt

Ein Bild aus der App «Python» bekam immer ein Gitter: `zeichnen.js` sagte
dem Achsenkreuz «nur Striche», wenn kein `plt.grid()` gerufen war, aber das
Achsenkreuz las es nie. Jetzt steht ohne `plt.grid()` kein Gitter über dem
Feld, nur kurze Striche am Rand, auf beiden Achsen – wie bei matplotlib. Mit
`plt.grid()` bleibt es, wie es war; die Vorlage eines neuen Skripts ruft es.

## 2026-11-20 · Wann gerechnet wird, steht an einer Stelle

Jede Änderung trug einen «Anlass», einen freien Text wie 'diagramm' oder
'skript'. Gewirkt haben davon drei: zwei zeichneten nur die Mitte neu, einer
rechnete. So rechneten Kopieren und Löschen eines Skripts neu, Anlegen,
Umbenennen und eine Änderung am Code nicht – und ein Zeichenfenster, das
einer Eingabe den sprechenden Anlass 'zeichnung' mitgegeben hätte, hätte
nichts gerechnet und rechts alte Zahlen stehen lassen.

Jetzt gibt es drei Wege: `aendern` zeichnet alles neu, `mitteAendern` nur
die Mitte, `projektAendern` ändert die Eingaben. Danach rechnet die Seite,
wenn sich geändert hat, was in die Rechnung eingeht: das Projekt ohne das,
was den Apps gehört, deren Zeile `rechnet: false` sagt – den Skripten, ihrer
Liste und ihren vergebenen Kennungen.

Für den Benutzer: ein neuer Name des Projekts rechnet jetzt neu; eine
Änderung an einem Skript rechnet nie neu, auch Kopieren und Löschen nicht.

## 2026-11-20 · Ein Diagramm nennt sein Bild

Der Reiter «Diagramme» im Bericht hielt jede Karte mit irgendeinem SVG für
ein Diagramm und nahm das erste als Vorschau. Ein Schalter mit Sinnbild im
Kopf einer Karte – die Ansicht des Rahmens im Raum – oder ein Zeichen in
einer Meldung über dem Bild wäre so zur Vorschau geworden. Jetzt sagt jede
Karte, die ein Diagramm zeigt, wo ihr Bild steht (`bild`); der Bericht liest
es dort (`bildDer`) und nirgends sonst – wie den Titel, den die Karte bekam
(`titelDer`), statt ihn aus ihrem Kopf zu lesen.

Was als Diagramm zählt, ist gleich geblieben: eine Karte, an deren Bildstelle
ein Bild gezeichnet ist. Ein Leerzustand an dieser Stelle – «Kein
Bruchzustand.» – macht sie zum Hinweis über den Diagrammen ihres Bauteils,
wie bisher.

## 2026-11-20 · Das Urteil steht hinter dem Grad

Wo «⇒ erfüllt» in einer Herleitung steht, entschieden zwei Schalter mit
entgegengesetzter Vorgabe: die Zeile des Erfüllungsgrads schrieb es nur auf
Wunsch, die Bedingung davor von selbst. Die meisten Nachweise setzten den
Schalter, einige nicht – in «Sprödes Versagen je Richtung» stand darum gar
kein Urteil. Jetzt steht es immer in der Zeile des Grads, und der Schalter
ist weg (entschieden vom Benutzer am 2026-11-19).

Für den Leser: wo das Urteil bisher in der Bedingung stand – Rissnormalkraft,
Duktilität, Spannungsbegrenzung, Mindestbewehrung, sprödes Versagen –, rückt
es eine Zeile tiefer, hinter den Grad.

## 2026-11-20 · Ein fehlendes Bild meldet sich

`sinnbild` zeichnete für einen Namen, den es nicht kennt, ein leeres Bild.
So standen die Kachel «Ergebnisse» der Decke und der Kopf ihres Fensters
ohne Bild da, und kein Test merkte es: er suchte die Namen nur in zwei
Schreibweisen, und ein Kapitel heisst wie sein Bild, ohne es zu nennen.
Jetzt wirft `sinnbild` wie der Katalog, «Ergebnisse» zeigt die Platte mit
einem Schnitt und dem Verlauf längs ihm, und der Test findet auch die
Kapitel und die Knöpfe des Zeichenfensters – und Namen mit Ziffern wie
`balkensystem3d`.

## 2026-11-20 · Durchstanzen: k_e nach einer Regel

Ob k_e aus der Näherung (4.3.6.2.5) oder aus (57) kommt, entschied das
Durchstanzen an vier Stellen: am Schnitt um die Stütze, stumm und laut an
den Schnitten um die Anker und den Pilz, und in der raschen Auslese der
Pilze. Die Eingänge von (57) – b und e_u – stellten die stille Suche und
die Herleitung je selbst zusammen. Wer eine dritte Art ergänzt und eine
Stelle vergisst, hätte aussen mit einem anderen k_e gerechnet, als die
Herleitung zeigt.

Jetzt wird die Regel einmal gebaut, im Nachweis an der Stütze:
`KeNaeherung` – ein Wert der gestützten Fläche, an jedem ihrer Schnitte –
oder `KeExzentrizitaet` mit dem Punkt, an dem die Auflagerkraft angreift.
Jede `Schnittpruefung` hält die Regel und fragt sie nach ihrem k_e; die
Herleitung schreibt, was sie gibt, und die Auslese der Pilze fragt nach
dem grössten k_e der Regel. Die Herleitung bleibt Wort für Wort dieselbe.

## 2026-11-19 · Grundbruch: Zahl und Formel aus derselben Spalte

Die Tragfähigkeitsformel stand in vier Formen: ein Wörterbuch der Werte,
Listen von Namen für das Produkt, die Vorlage der Herleitung und eine
Klasse mit den Zahlen für die Tabelle. d_γ = 1 stand darin als «1», als 1.0
und im Produkt gar nicht – wer dort einen Faktor ergänzt und eine Liste
vergisst, hätte ihn gezeigt und ohne ihn gerechnet. Jetzt hält eine
`Spalte` je Teil der Formel ihre Faktoren N, s, d, g und b' als Werte; aus
ihr kommen die Zahl (`produkt`), die Vorlage der Herleitung (`vorlage`) und
die Tabelle der Zusammenfassung.

Für den Leser: d_γ = 1 steht in der Herleitung jetzt als eigene Zeile mit
Kap. 9.2.13 statt als Satz, und in der Formel für σ_f steht d_γ, wo vorher
eine «1» stand. Die Zahlen bleiben dieselben.

## 2026-11-19 · Grundbruch in vier Dateien

`opencivil/geotechnik/grundbruch.py` stand bei 996 Zeilen; der Umbau der
Tragfähigkeitsformel hätte die Grenze von 1000 überschritten. Jetzt:

- `fundament.py`: das Fundament mit seinen Bemessungswerten, die
  Kombination und was Grundbruch und Gleiten teilen – der
  `Fundamentnachweis` mit dem Erfüllungsgrad je Kombination, den Eingängen
  je Verhalten und dem Vergleich von Einwirkung und Widerstand samt dem Satz
  für die Tabelle. Vorbild ist der Achsnachweis des Pfahls. Dazu die
  Angaben über der Tabelle der Zusammenfassung.
- `grundbruch.py`: der Grundbruch, 639 Zeilen.
- `gleiten.py`: das Gleiten.
- `tragfaehigkeit.py`: N_q und N_c, die auch der Fuss eines Pfahls braucht –
  der Pfahl hängt damit nicht mehr am Grundbruch.

Weggefallen ist der Verweis «Kap. 9.2.18», den keine Formel brauchte. Die
Rechnung ist dieselbe; der Schnappschuss der Berichte bleibt.

## 2026-11-19 · Bilder an den Schaltern: Querschnittsanalyse

Die letzte Gruppe. Die Art einer Bewehrungslinie zeigt je Stellung, wie die
Stäbe liegen: verschmiert ein Band, «Anzahl» das Mass über die ganze Linie,
«Teilung» das Mass zwischen zwei Stäben. Im kleinen Fenster des
Zeichenbereichs stehen die drei Bilder über dem Wort, wie bei den
Werkzeugen – nebeneinander waren sie breiter als das Fenster. Hinter
Start- und Endeisen steht die Linie mit dem Stab am Anfang oder am Ende;
der Strich markiert das freie Ende, denn mit einem Strich an beiden Enden
sahen sich die zwei Bilder zu ähnlich.

«Nur einachsig» war ein Häkchen mit einem Satz darunter; jetzt ist es der
Schalter «Biegung: einachsig / zweiachsig», je mit dem Querschnitt und
seiner Druckzone über einer waagrechten oder einer schiefen Nulllinie. Was
sonst noch gilt – M_z und V_y zählen einachsig nicht –, steht im Titel der
Stellung.

## 2026-11-19 · Bilder an den Schaltern: Setzung und Platte

Die Steifigkeit der Setzung zeigt das Fundament im Grundriss, mit dem Punkt,
für den die Setzung gilt: starr im Punkt K nahe einer Ecke, schlaff in der
Mitte. Der Knopf «ungünstig / günstig» einer Lage mit Grund und Zulage zeigt
die zwei Stäbe im Schnitt mit der Seite der Platte – ungünstig hängen beide
an derselben Kante weg von der Seite, günstig liegen beide an der
Überdeckung, unten wie oben gespiegelt. Der Zug eines Verformungsfalls trägt
den Pfeil, wie die Zugseite der Querschnittsanalyse («↓ unten», «↑ oben»);
den Pfeil liefert der Kern mit. Vor «Einlage, grösstes Mass» steht die
Einlage im Schnitt der Platte, mit ihrem Mass darüber.

## 2026-11-19 · Bilder an den Schaltern: Pfahl

Wie beim Durchstanzen, nach dem Entscheid des Benutzers. Der Kopf des
Pfahls zeigt «frei drehbar» als Pfahl auf einem Gelenk, «eingespannt» als
Pfahl in einer Platte; das Tragglied des Mikropfahls im Schnitt das Rohr
als Ring, den Vollstab als Scheibe. Volle Flächen dürfen dafür ein Loch
haben (Regel evenodd).

Dass ein Bild `art-wert` heisst, steht jetzt an einer Stelle, `mitBild` in
bausteine.js – Durchstanzen, Pfahl und die Rechenarten, die das bis dahin
selbst zusammensetzten, nehmen es von dort.

## 2026-11-19 · Bilder an den Schaltern: Durchstanzen

Entscheid des Benutzers: wo Wörter nicht reichen, zeigt jede Stellung ein
Bild. Beim Durchstanzen stand «Randstütze», ohne zu sagen, wo der Rand
liegt – das sagte erst die Hilfe. Jetzt zeigt jede Lage die Stütze von oben
im Ausschnitt der Platte: gestrichelt läuft die Platte weiter, ausgezogen
ist ihr Rand, unten bei der Randstütze, unten und links bei der Eckstütze –
wie die Koordinaten des Kerns und das Feld «Abstand zum unteren Rand».
Wandende und Wandecke zeigen die Wand, die Form Rechteck, Kreis und das
Oval mit halbrunden Enden.

Die Bilder heissen `art-wert` (`lage-rand`, `stuetzenform-oval`), wie schon
die Rechenarten; ein Test prüft, dass jede Stellung des Katalogs ihres hat,
auch eine neue. `sinnbild` kennt dazu volle Flächen (`flaechen`): in
Schaltergrösse, 23 Bildpunkte, verschwamm das Kreuz in der Stütze zu einem
Fleck. Die fünf Lagen mit Bild waren breiter als ihr Block; die Stellungen
eines Wahlblocks brechen jetzt um, wie es sein Kommentar schon versprach.

## 2026-11-19 · Grundbruch: drainiert oder undrainiert als Schalter

Entscheid des Benutzers. Bis dahin hiess im Grundbruch φ = 0 undrainiert,
und die Kohäsion c galt dann als s_u; im Pfahl wählt ein Schalter, je
Schicht. Jetzt hat der Grundbruch denselben Schalter im Kasten «Boden»:
«drainiert» zeigt φ_k, γ_φ, c_k, γ_c und die Sohlreibung, «undrainiert»
s_u,k und γ_cu. Beispiel: der Seeton der Beispiele hiess φ_k = 0,
c_k = 40 kPa, jetzt «undrainiert», s_u,k = 40 kPa. Herleitung und Bericht
zeigen dann s_u,k, γ_cu und s_u,d = s_u,k / γ_cu statt φ_k, c_k und c_eff;
die Zahlen bleiben dieselben.

γ_cu ist neu: SIA 267:2013, 5.3.2.2, Tabelle 1, führt für die undrainierte
Scherfestigkeit einen eigenen Partialfaktor, 1.5 wie γ_c; bis dahin galt
γ_c auch für s_u. Drainiert verlangt φ_k über null, undrainiert s_u,k über
null, wie beim Pfahl. Was nicht gilt, steht weder in der Maske noch in der
Herleitung; die Zahlen bleiben gespeichert und stehen nach dem
Zurückschalten wieder da. Das gilt auch für γ_w: es wirkt nur über γ', und
undrainiert gelten totale Spannungen – darum hält dort auch γ ≤ γ_w die
Rechnung nicht mehr an. Unter dem Bild heisst es «Undrainiert: kein
Gleitkörper gezeichnet.», ohne das φ = 0 von früher.

`Verhalten` steht jetzt in `opencivil/geotechnik/verhalten.py`, unter
Pfahl und Grundbruch; der Katalog führt die Stellungen unter `verhalten`,
und beide Fenster bauen den Schalter mit `verhaltenSchalter`
(bausteine.js). Die Erklärungen der Stellungen nennen keine Zeichen mehr:
der Pfahl schreibt φ'_k, der Grundbruch φ_k. Die Typen `Drainiert(φ, c)`
und `Undrainiert(s_u)` aus dem Umbauvorschlag bleiben offen.

## 2026-11-19 · Bügel und Längsbewehrung in einem Zug

Entscheid des Benutzers. Mit «Bügel mitsuchen» suchte die Platte erst die
Längsbewehrung, mit den alten Bügeln, dann die Bügel. Bei V_Ed = 400 kN/m
und ⌀10@200 scheiterte die Längssuche an der Querkraft, die Bügelsuche fand
⌀12@200, und erst ein zweiter Klick fand die Längsbewehrung – ohne Bügel
vorher ebenso. Jetzt prüft die Längssuche mit «Bügel mitsuchen» die
Querkraft nicht, die Bügelsuche danach schon, zuerst ohne Bügel: ein Klick
findet beides.

Auch ohne Bügel vorher nicht: so hängt das Ergebnis nicht daran, ob vorher
welche lagen, und es genügt immer ein Klick. Die Folge: wo etwas mehr
Längsbewehrung die Bügel erspart hätte, kommen Bügel dazu (h = 300 mm,
V_Ed = 200 kN/m: 3896 mm² und ⌀8@200 statt 4419 mm² ohne Bügel). Wer das
nicht will, schaltet «Bügel mitsuchen» aus; das «?» neben dem Schalter sagt
beides. Ob die Suche stattdessen zuerst ohne Bügel versuchen soll, steht
in [[TODO]].

Im Dienst (`bewehrung_suchen`), wo die beiden Suchen nacheinander laufen;
die Querkraft nimmt `QuerschnittEintrag.ohne_querkraft` aus der Kopie der
Längssuche.

## 2026-11-19 · Eine zu dünne Platte rechnet nicht

Entscheid des Benutzers. Vorher prüfte die Platte nur, dass die
Überdeckungen zusammen kleiner sind als h. Bei h = 80 mm und ⌀12 in jeder
Lage kreuzten sich die oberen und unteren Lagen, dastand «Höhe der
Distanzhalter −28 mm», und M_Rd wurde gerechnet. Jetzt sagt die Platte
«Nichts zu rechnen: Überdeckungen und Lagen ergeben zusammen 108 mm – mehr
als die Dicke h = 80 mm; die oberen und unteren Lagen kreuzten sich.» Wo sie
sich gerade berühren (h = 108 mm), rechnet sie.

Geprüft beim Bauen (`_querschnitt` in `aufbau/platte.py`, mit
`stapelhoehe` neben `Bewehrungslage`), nicht in den Regeln der Platte: die
Bewehrungssuche prüft vorab nur die Regeln (`vorab_pruefen` baut nicht) und
kann so eine zu dicke Bewehrung ersetzen; ein Kandidat, der nicht passt,
ist für sie ein Nein.

## 2026-11-19 · Ein leerer Name hält nur sein Bauteil an

Entscheid des Benutzers. Die Oberfläche nimmt keinen leeren Namen an; aus
einer bearbeiteten Datei aber liess ein leerer Fallname das ganze Projekt
nicht mehr öffnen («Platte 'Decke über EG', kombinationen 1: 'name' darf
nicht leer sein.»). Jetzt öffnet sich die Datei, und nur die Platte sagt
«Nichts zu rechnen: kombinationen 1: noch kein Name.»; der Rest rechnet.

Der Name ist das eine Pflichtfeld, das nicht schon das Lesen prüft, sondern
`inhalt_pruefen` vor dem Rechnen (`_ist_name` in `lesen.py`), und dort wie
am Namensfeld: nur Leerzeichen sind auch kein Name. Andere Pflichttexte
bleiben beim Lesen. Dass der Ort «kombinationen 1» heisst und nicht
«Einwirkung 1», steht schon in [[TODO]] (die Wörter der Maske im Ort).

## 2026-11-19 · Ein doppelter Fallname weist schon das Feld ab

Entscheid des Benutzers. Vorher nahm das Namensfeld jeden Namen, und erst
das Bauteil sagte oben im Fenster, dass er doppelt ist. Die sechs Fenster
der Spannung-Dehnung-Analysen teilen sich aber eine Liste: der andere stand
oft in einem Fenster, das nicht offen war. Jetzt sagt das Feld ««Feld» ist
als Tragsicherheitseinwirkung schon vergeben: «Stütze» bleibt.», bei einer
Analyse dazu «im Fenster «Momenten-Krümmungs-Linie»», bei einem eigenen
Gebrauchsfall «aus der Tragsicherheit abgeleitet».

Die Regel steht einmal, in `opencivil/projekt/fallnamen.py`: jedes Bauteil
nennt seine Listen (`fallnamen()`, ohne eigene keine), und dieselbe
`Fallnamen` prüft vor dem Rechnen (`pruefen`, für eine Datei) und fürs Feld
(`grund`). Das Feld fragt den Kern (`fallname` im Dienst), denn ob zwei
Namen zusammenfallen, sagt erst die Kennung (`kennung_aus`): «Wand A» und
«Wand-A» fallen zusammen. Antwortet der Kern nicht, gilt der Name – vor dem
Rechnen fragt er ohnehin. `eindeutig` und `namen_pruefen` sind weg; die
Meldung vor dem Rechnen heisst nun gleich wie am Feld.

Ein Test liest die Pfade aus web/js und verlangt, dass ein Bauteil jede
Liste kennt – sonst fragte ein Feld ins Leere und nähme jeden Namen.

## 2026-11-19 · α_min über α_max weist schon das Feld ab

Entscheid des Benutzers. Vorher nahm das Feld α_min = 50° bei α_max = 40°
an, und erst die Rechnung hielt Platte oder Analyse an. Jetzt sagt das Feld
«α_min darf nicht grösser sein als α_max: 50 ist nicht übernommen.» und
behält 30°; ebenso α_max unter α_min. Die Pfeile halten am anderen Wert.

Die Regel steht einmal, am Feld des Kerns: `bereich(..., bis_feld=
"alpha_max")` bei α_min (`kleinste_neigung`). Daraus macht der Katalog
`bis_feld` bei α_min und `ab_feld` bei α_max, mit dem Satz des Kerns, und
`inhalt_pruefen` hält eine Datei mit denselben Worten auf.
`neigungen_ordnen` ist weg. Die Zahl des anderen Feldes kennt erst die
Maske: `zahlfeld({..., neben: eintrag})`.

## 2026-11-19 · Eine Kennung kommt nie wieder

Entscheid des Benutzers. Vorher war die nächste Kennung die grösste
vorhandene plus eins, bei den Bauteilen und Materialien des Projekts sogar
die kleinste freie. Wer die letzte Kombination LK2 löschte und eine neue
anlegte, bekam wieder LK2 – und die Diagrammzeile, die auf die gelöschte
gezeigt hatte, zeigte still die neue. Jetzt merken sich das Projekt und
jedes Bauteil je Vorsilbe die höchste je vergebene Nummer (`vergeben`, in
der Datei gespeichert); die neue heisst LK3.

Die Regel steht je Sprache einmal: `neue_kennung` in
`opencivil/projekt/netz.py` (auch für die Knoten des `Netz`, das dafür sein
Bauteil bekommt statt nur dessen Liste) und `neueKennung` in
`web/js/zustand.js`, das auch das Zeichenfenster nimmt. Die vorhandenen
Kennungen zählen weiter mit: eine Datei ohne Zählung hat nur sie.

Wer auf etwas Gelöschtes zeigt, sagt es am Ort. Löschen lässt die
Oberfläche fast nichts, was noch benutzt wird – ein Material, einen
Querschnitt, einen Lastfall mit Lasten weist sie ab. Was bleibt, ist die
Diagrammzeile: sie zeigt «– gelöscht, einen Fall wählen –», ihre Karte
«Der gewählte Fall ist gelöscht.»; in der Decke ein gelöschter Schnitt
«– gelöscht, neu wählen –». Der Hinweis zu einem Beiwert ohne Lastfall
nennt dessen Kennung nicht mehr.

Dass ein neuer Eintrag nichts von einer früheren Ansicht zeigt, braucht
kein Vergessen beim Anlegen mehr: seine Kennung gab es nie.

## 2026-11-19 · Schalter statt Häkchen

Entscheid des Benutzers: auch eine Wahl ja/nein ist ein Schalter. Vier
Häkchen waren übrig:

- «überschreiben» bei einem abgeleiteten Kennwert eines eigenen Materials.
  Jetzt steht unter der Bezeichnung «gerechnet | von Hand» neben der Zahl
  – der Schalter sagt, woher die Zahl kommt. In einer Zeile neben der
  Bezeichnung fand er keinen Platz (155 px in einer Zeile von 394 px), und
  ✓/✗ hätte jede Zeile mit einem roten Kreuz gezeigt, obwohl nichts falsch
  ist. Ohne gerechneten Wert ist er ausgegraut (`zweiSchalter` kann jetzt
  `aus`); eine Normsorte hat keinen, an ihr ist nichts zu wählen. Die
  leere erste Spalte der Kennwertzeile ist weg.
- «mit Bewehrung», «mit Schubwänden» in der Vorlage der
  Querschnittsanalyse: «Bewehrung ✓|✗», «Schubwände ✓|✗» in der Reihe der
  Masse, wie die Ja/Nein-Wahlen in den Eigenschaften der Zeichnung. Das
  Fenster baut sich beim Umschalten nicht neu, nur die Skizze; darum
  ersetzt sich die Zeile selbst.
- «Fang» in der Palette jeder Zeichnung: «Fang ✓|✗» neben «Raster in m».
- Die vereinfachte Kurve im Betondiagramm: ✓|✗ vor ihrem Eintrag in der
  Legende.

Übrig ist nur das Kästchen einer Aufgabe im Notizbuch: es zeigt, ob eine
Aufgabe erledigt ist, und lässt sich nicht anklicken.

## 2026-11-19 · Durchstanzen: nach dem Umschalten der Platte ein Hinweis

Entscheid des Benutzers. Wer beim Durchstanzen von Decke auf Bodenplatte
schaltet, behält seine Zahlen: Decke und Bodenplatte haben dieselben
Vorgaben, eine «Vorgabe der neuen Art» gibt es nicht. Vorher wechselte nur
still die Beschriftung, und q_d = 10 kN/m² «Eigengewicht und Auflast» hiess
auf einmal Bodenpressung. Jetzt steht unter dem Schalter grau «c, c_v, q_d
und die Biegebewehrung gelten jetzt für die Bodenplatte – prüfen.», bis zur
nächsten Änderung der Stelle.

Der Satz kommt aus dem Kern (`Plattenart.umgeschaltet`), über den Katalog;
die Maske merkt sich nur, welche Stelle eben umgeschaltet wurde.

## 2026-11-19 · Ohne Last kein Nachweis, auch beim Durchstanzen und der Setzung

Entscheid des Benutzers. Vorher stand ein frisches Durchstanzen (V_d = 0)
und eine Setzung ohne Pressung in der Zusammenfassung als «erfüllt» mit dem
Grad ∞. Jetzt steht dort, wie schon in der Querschnittsanalyse, «Keine
Einwirkung → kein Nachweis.», in der Herleitung und unter der Tabelle.

Der Satz steht einmal, als `OHNE_EINWIRKUNG` in `opencivil/core/nachweis.py`,
neben `UNBESCHRAENKT`, mit dem er geht. Beim Durchstanzen bekommt der
Grundriss seinen Schnitt trotzdem; bei der Setzung genügt eine der beiden
Pressungen, q_W oder q_E, damit gerechnet wird.

## 2026-11-19 · Ein fehlendes Material steht grau, ohne Kennung

Zwei Entscheide des Benutzers. Vorher stand ein gelöschter Beton an einer
Platte der Decke oder an einem Stab des Balkensystems rot da, als wäre das
Projekt falsch, und nannte eine Kennung, die man nirgends sieht: «Platte
P3: Beton: das Material 'b9' gibt es nicht mehr – eines wählen.» Die
Querschnittsanalyse zeigte denselben Fall grau. Jetzt steht es überall
grau, «Platte P3: Beton: das gewählte Material gibt es nicht mehr – eines
wählen.»; rot bleibt die falsche Art, etwa ein Stahl, wo ein Beton
hingehört. Im Balkensystem heisst das Material wie in seiner Liste, «L1
nimmt «C30/37», aber …», und ohne Stoff «einen Beton des Projekts» –
vorher «das Material M1».

Gerechnet wird trotzdem nicht: ohne Material fehlen Steifigkeit und
Gewicht. Darum trennt die Meldung jetzt «hält an» von «ist falsch»:
`fehler` steht rot und hält an, `unfertig` steht grau und hält auch an,
sonst ist sie ein Hinweis (`Meldung.haelt_an`). Warum eine Wahl nicht
rechnet, sagt ein `Grund` mit `falsch`; für Materialien steht die Regel
einmal, in `materialgrund`, auch für die Zeichnung der
Querschnittsanalyse. Ebenso grau: ein Stab, der noch kein Material hat,
und «gemäss Querschnitt» bei einer Platte oder Analyse, die noch nicht
rechnet. Rot: «gemäss Querschnitt» bei einem Querschnitt nach Vorlage oder
einer Analyse aus zwei Betonen – dort widerspricht sich die Wahl.

## 2026-11-19 · Ein Gedankenstrich statt zwei Bindestrichen

Entscheid des Benutzers: in allem, was er in der Software liest, steht
«–». Vorher schrieben Meldungen, Hinweise, Titel und Bericht teils
«noch keine Kombination – unter «Einwirkungen» eine anlegen», teils mit
«–». Umgestellt sind 236 Stellen, nur in Zeichenketten – Kommentare und
Docstrings dürfen «--» behalten, und wo «--» etwas bedeutet, blieb es:
die Linienstile der Konsole («--» heisst gestrichelt), CSS-Variablen
(`--blau`) und der Kopf eines Moduls, den das Notizbuch am «--» zerlegt.
Die Tests, die einen Satz der Software erwarten, gingen mit; Meldungen
der Tests an Entwickler blieben.

## 2026-11-19 · Schalter in normaler Schrift

Entscheid des Benutzers: Schalter ohne Grossbuchstaben. Vorher stand jede
Stellung gross da, «DECKE | BODENPLATTE», und wo ein Formelzeichen darin
stand, hob eine eigene Klasse das wieder auf (`ist-wortlaut`, an 14
Schaltern) – sonst wurde aus E_cm «E_CM». Wer einen neuen Schalter mit
Formelzeichen baute und die Klasse vergass, hatte den Fehler wieder; so war
es beim Schalter «E-Modul». Jetzt steht jede Stellung, wie sie geschrieben
ist, 12 px halbfett, und die Klasse samt ihren fünf Ausnahmen im Stilblatt
ist weg. Überschriften von Gruppen und Spalten bleiben gross: dort ist es
Gestaltung, kein Inhalt.

## 2026-11-19 · Querschnittsanalyse: die Karte «Schubfluss» sagt, warum sie leer ist

Nachtrag zur Durchsicht. Unter «Diagramme» fehlte die Karte «Schubfluss»
ohne ein Wort, sobald ein Lastfall keine Querkraft und keine Torsion hatte
– die Karte «Bruchzustand» darüber sagt seit dem zehnten Schritt, warum
sie leer ist. Jetzt sagt es auch diese:

- Schubwände, aber weder Querkraft noch Torsion: «Keine Querkraft und
  keine Torsion → kein Schubfluss.»
- Querkraft, aber keine Schubwand: der Satz des Nachweises, «Es gibt keine
  Schubwand, die Querkraft oder Torsion aufnehmen könnte.» Ebenso, wenn
  die Wände nicht tragen: dann der Grund dafür.
- Weder Schubwand noch Querkraft: keine Karte. Schub ist dann kein Thema
  der Analyse, und ein Satz darüber wäre Lärm.

Der Satz kommt aus dem Kern (`_ohne_schub` in den Diagrammdaten); der
Nachweis legt seinen Grund je Lastfall im Befund ab (`Schubbefund.ohne`),
damit Urteil und Diagramm denselben Satz sagen.

Ebenso nachgetragen: die Spaltenköpfe der Kombinationen bei Grundbruch und
Pfahl standen als Text da und wurden gross geschrieben, «N_ED [KN]». Jetzt
Formeln wie bei Platte, Setzung und Querschnittsanalyse: N_Ed [kN].

## 2026-11-19 · Grundbruch, Setzung, Pfahl: die Zusammenfassung sagt, was fehlt

Dreizehnter und letzter Schritt der Durchsicht, die Bereiche Grundbruch
bis Python.

- **Ohne Kombination oder Schicht** stand in der Zusammenfassung nur «Kein
  Nachweis gerechnet.»; den Grund gab es nur als Warnung in der
  Herleitung. Jetzt steht er dort: «Kein Nachweis: noch keine Kombination
  – unter «Einwirkungen» eine anlegen.», bei ausgeschalteten «jede
  Kombination ist ausgeschaltet», bei der Setzung «noch keine Schicht –
  unter «Schichten» eine anlegen». Der Satz steht einmal, am Bauteil
  (`Aufbau.ohne_nachweis`, wie `unfertig`), und geht von dort in
  Zusammenfassung und Warnung.
- **Die Bemessungswerte des Grundbruchs** (φ_eff, c_eff, γ') blieben nach
  einer Rechnung, die nicht ging, ohne Kennzeichen neben der neuen
  Eingabe stehen. Jetzt blass, mit «aus der Rechnung davor».
- Ein geleerter Name: Pfahl, Schicht, Setzung, Grundbruch und Python nehmen
  alle das gemeinsame Namensfeld; es weist einen leeren Namen ab und lässt
  den alten stehen. Nichts mehr zu tun.

## 2026-11-19 · Decke: eine Zeile je Grund, eine frische Decke ohne Fehler

Zwölfter Schritt der Durchsicht.

- **Eine Platte ohne Lager** gab je Fall vierzig gleiche rote Zeilen, «Der
  Streifen «x1» trägt nicht – er liegt auf nichts. 4.5 kN fallen aus.»,
  in der Zusammenfassung rund 160. Jetzt eine je Grund und Fall: «40
  Streifen tragen nicht – sie liegen auf nichts. 120 kN fallen aus.» Ein
  einzelner Streifen heisst wie bisher. Ebenso im Balkensystem: ein
  Material, das nicht trägt, nennt alle Stäbe in einer Meldung, «L1, L2
  und L3 nehmen das Material M1, aber …», statt einer je Stab.
- **Eine frische Decke** zeigte «Die Decke hat keine Platte.» als roten
  Fehler und in der Zusammenfassung «Nicht gerechnet.». Jetzt grau «Noch
  keine Platte – mit «Platte» zeichnen.», und die Zusammenfassung sagt
  dasselbe wie die Diagramme. Gerechnet wird weiter nichts: ohne Streifen
  hält die Rechnung an, nicht mehr nur bei einem Fehler. Sonst hiesse die
  leere Decke gerechnet, mit null Last in jedem Fall.
- **Ohne Lastfall** fehlten im Fenster einer Platte «q überall» und im
  Fenster eines Knotens die Punktlast ohne ein Wort. Jetzt steht dort, was
  fehlt: «Für Lasten zuerst unter «Lastfälle» einen Lastfall anlegen.»
  (derselbe Satz wie an einer gewählten Last) oder, gibt es Lastfälle,
  «Kein Lastfall gewählt – oben in der Leiste einen wählen.» Das Fenster
  baut sich neu, wenn der erste Lastfall dazukommt.

## 2026-11-19 · Materiallisten: überall dieselbe, und ein gelöschtes Material steht am Ort

Elfter Schritt der Durchsicht, der erste der Bereiche Decke bis Python.

- **Eine Liste statt fünf:** Die Wahl eines Materials des Projekts stand in
  Querschnittsanalyse, Decke, Durchstanzen, Pfahl und Balkensystem je
  anders da. Jetzt baut sie überall `materialliste` in `bausteine.js`, mit
  allem, was eine davon schon konnte:
  - ein gelöschtes Material: «– Beton wählen –». Pfahl und Durchstanzen
    zeigten bis jetzt still den ersten Beton der Liste, als wäre er gewählt;
  - noch keines im Projekt: «– noch kein Beton im Projekt –» statt einer
    leeren Liste;
  - mehrere gewählte mit verschiedenem Beton: «Var». Die Decke zeigte dann
    «– Beton wählen –», als hätte keine Platte einen.

  `VAR`, `gemeinsam` und `mitVar` sind dafür von `cad_app.js` nach
  `bausteine.js` gezogen; die Liste braucht sie auch ausserhalb der
  Zeichenfenster.
- **Ein gelöschter Beton in der Decke:** hielt die ganze Decke an, mit
  «das Material 'b9' gibt es im Projekt nicht», ohne die Platte zu nennen,
  und das Zeichenfenster bekam nur einen Fehler. Jetzt steht an der Platte
  «Platte P3: Beton: das Material 'b9' gibt es nicht mehr – eines
  wählen.», nach derselben Regel wie bei jedem Bauteil (`materialgrund`),
  und die Zeichnung bleibt stehen. Ebenso im Balkensystem, am Stab. Ein
  neuer Beton für neue Platten fällt auf den ersten des Projekts zurück,
  wenn der vorgegebene gelöscht ist; bis jetzt bekam jede neue Platte den
  gelöschten.

## 2026-11-19 · Querschnittsanalyse: Diagramme und Spannungsbild sagen, was sie zeigen

Zehnter Schritt der Durchsicht, der zweite Teil der Querschnittsanalyse.

- **Das Spannungsbild bei Zug oben, links oder rechts:** An der Höhenachse
  stand immer «z [mm] (ab Oberkante)», an den Rändern «Oberkante» und
  «Unterkante». Bei Zug links läuft das Bild aber vom rechten Rand zum
  linken. Jetzt: «z [mm] (ab Rand rechts)», «Beton am Rand rechts:
  −17.6 N/mm²» – dieselben Namen wie die Felder «ε rechts» und «ε links»
  darüber. Auch die Herleitung der M-χ-Linie schreibt ε_rechts statt
  ε_oben. Die Namen kommen aus dem Kern (`Analyse.raender`). Bei der Platte
  heisst es jetzt «ab Rand oben» statt «ab Oberkante».
- **Ein Lastfall ohne Last** (etwa ein neuer, alles 0): fehlte in der
  Zusammenfassung ohne ein Wort, und im Interaktionsdiagramm stand «α_eff =
  ∞ – erfüllt». Jetzt steht er in der Zusammenfassung mit «Keine Einwirkung
  → kein Nachweis.», wie ein Knickfall ohne Druck, und im Diagramm grau mit
  demselben Satz.
- **Die Karte «Bruchzustand»:** fehlte bei einem Lastfall ohne Moment ohne
  ein Wort. Jetzt steht sie da und sagt warum: «Ohne Moment gibt es keinen
  Bruchzustand im Schnitt: nachgewiesen wird die Normalkraft gegen die
  gleichmässige Dehnung.» Ebenso bei einer Normalkraft jenseits der
  Tragfähigkeit. Die Sätze stehen einmal, im Nachweis, für Herleitung,
  Zusammenfassung und Diagramm.
- **Achsen des Interaktionsdiagramms gewechselt:** Bis die Antwort kam,
  stand blass die alte Fläche in den neuen Achsen, mit der Legende «bei M_z
  = 0». Jetzt steht dort «Der Schnitt für die neuen Achsen wird gerechnet
  …». Bleibt die feste Grösse dieselbe, bleibt das alte Bild blass stehen
  wie bisher.
- **Wenn der Kern die Zeichnung nicht prüfen kann:** im Fenster
  Tragsicherheit stand dauerhaft «Der Kern liest die Zeichnung …». Jetzt
  steht dort derselbe Grund wie unter der Zeichnung.
- **«Begrenzung auf 500 mm»** steht ohne «Zwängung auf Normalkraft» blass
  da und sagt «wirkt nur mit der Zwängung auf Normalkraft».
- **Offen** ([[TODO]]): α_min über α_max weist erst die Rechnung ab, nicht
  das Feld.

## 2026-11-19 · Querschnittsanalyse: was noch fehlt, ist kein Fehler

Neunter Schritt der Durchsicht, der erste Teil der Querschnittsanalyse: die
Zeichnung.

- **Mehrere gewählt:** Wer zwei Bewehrungslinien wählte, 3 ⌀20 und 2 ⌀12,
  sah im Fenster «n 3, ⌀ 20», die Werte der ersten, und ein getipptes ⌀ 16
  galt unsichtbar für beide. Jetzt steht da, was sie gemeinsam haben, sonst
  «Var», wie im Balkensystem und in der Decke. Verteilen sie ihre Stäbe
  verschieden (Anzahl und Teilung), sagt das Fenster, dass erst eine Art zu
  wählen ist.
- **Ein Stahl, den es nicht mehr gibt:** Wer einen Betonstahl löschte,
  bevor er gezeichnet hatte, und einen neuen anlegte, zeichnete mit dem
  gelöschten weiter: das Werkzeug merkte ihn sich. Die Liste zeigte still
  «B500B», unter der Zeichnung stand nichts. Jetzt nimmt das Werkzeug den
  ersten Betonstahl des Projekts; und verweist ein Element (etwa aus einer
  bearbeiteten Datei) ins Leere, zeigt die Liste «– Betonstahl wählen –»,
  und unter der Zeichnung steht grau «Linie 1: das Material 's9' gibt es
  nicht mehr – eines wählen.» Grau, weil nur etwas fehlt; rot bleibt, was
  falsch ist, etwa ein Beton als Stahl. Die Regel steht einmal, im Kern
  (`materialgrund`), für das Rechnen und für die Zeichnung.
- **Eine neue, leere Analyse:** stand rot «Es gibt kein Polygon mit
  Material». Jetzt steht nur «Noch nichts gezeichnet …». Mit Bewehrung,
  aber ohne Polygon, steht der Satz grau da, und die Liste links sagt «ohne
  Polygon» statt «leer».
- **Wenn der Kern die Zeichnung nicht prüfen kann:** der Grund blitzte 6 s
  unten auf, danach fehlten still Schwerpunkt und Meldungen. Jetzt steht er
  unter der Zeichnung, bis die nächste Antwort kommt.
- **«Fläche bilden»** sagt, was entsteht: «Die geschlossenen Hilfslinien
  werden eine Fläche C30/37 – wie die Vorgabe des Werkzeugs Polygon».

## 2026-11-19 · Platten und Materialien: was der Kern abwiese, sagt schon das Feld

Achter Schritt der Durchsicht, der zweite Teil der Platten und Materialien.

- **Ein eigenes Material mit dem Namen einer Normsorte:** BE1 liess sich in
  «C35/45» umbenennen, danach rechnete kein Bauteil mit BE1 mehr. Jetzt
  weist das Feld den Namen ab: «Den Namen «C35/45» trägt eine Normsorte:
  «BE1» bleibt.»
- **Die Kennwerte eines eigenen Materials:** die Pfeile führten bis 0
  (ν_c 0.2 → 0.1 → 0), und das Material rechnete nicht mehr. Jetzt halten
  sie an der Grenze des Kerns, über null, und eine getippte 0 meldet sich am
  Feld: «Querdehnungszahl des Betons muss grösser als null sein: 0 ist nicht
  übernommen.» Die Grenze steht einmal, im Kern (`kennwertbereich`); seine
  Meldung nennt den Kennwert jetzt wie das Fenster, «Teilsicherheitsbeiwert
  für Beton» statt «gamma_c».
- **«überschreiben» ohne gerechneten Wert:** der Haken setzte eine 0. Jetzt
  ist er gesperrt, bis es einen Wert gibt, und sagt das.
- **Die Teilungen der Bewehrungssuche:** aus «-150» wurde still 150, aus
  «abc» nichts. Jetzt: «Teilung muss grösser als null sein: «150» bleibt.»
  oder ««abc» ist keine Zahl: «150» bleibt.» Die Grenze steht am Feld der
  Platte im Kern.
- **Die Normalkraft unter der M-V-Kurve:** sprang nach jeder anderen Eingabe
  auf 0 zurück, weil das Rechnen sie nicht mitgab. Jetzt bleibt sie, bis
  man ein anderes Projekt öffnet.
- **Spaltenköpfe:** standen als Text da und wurden gross geschrieben:
  «M_ED [KNM]», «L_CR [M]», und aus «ε oben» wurde «Ε OBEN». Jetzt als
  Formelzeichen mit Einheit – M_Ed [kNm], l_cr [m], ε oben [‰] –, in der
  Platte und in der Querschnittsanalyse.
- **Kleineres:**
  - die Bügel «Stk» versprachen «dann nur Nachweise in x» – nachgewiesen
    wird ohnehin nur x; der Satz ist weg;
  - ein Haken-Schalter sagte «Bügel mitsuchen wird nicht geführt»; jetzt
    «Bügel mitsuchen: aus – Klicken schaltet ein», bei jedem dieser
    Schalter;
  - die Suche meldete «kleinste Stahlfläche von 1 Lösungen», jetzt «die
    einzige Lösung».
- **Offen** ([[TODO]]): eine zu dünne Platte, in der sich obere und untere
  Lagen kreuzen, und doppelte Namen von Fällen schon am Feld.

## 2026-11-19 · Platten: was die Fenster zeigen, stimmt wieder

Siebter Schritt der Durchsicht, der erste Teil der Platten.

- **Der Bezug einer Analyse in y:** im Fensterkopf stand «M, N je b =
  500 mm», gerechnet wird in y aber je Meter. Wer in einer Zeile «y» 20 kNm
  eintrug und 40 kNm/m meinte, bekam die Spannungen für die Hälfte. Jetzt:
  «M, N je b = 500 mm in x, je 1000 mm in y». Bei b = 1000 mm bleibt es
  beim alten Kopf.
- **Die Bewehrungssuche sagt alles, was sie gefunden hat:**
  - «Bügel mitsuchen» bei kleiner Querkraft: die Suche nahm die Bügel ⌀10
    weg und meldete nur die Teilung. Jetzt dazu «Bügel: Ohne Bügel
    erfüllt.» und «Duktilität erfüllt.» – ist sie nicht erfüllt, in Rot.
  - Grosse Querkraft: die Längssuche scheiterte, die Bügelsuche fand ⌀12@200
    – und das wurde verworfen, ein zweiter Klick half nicht. Jetzt nimmt
    die Platte die Bügel, die Meldung nennt sie, und der zweite Klick findet
    die Längsbewehrung. Dass die Suche nicht beides in einem Zug findet,
    liegt an ihrer Reihenfolge im Kern (siehe [[TODO]]).
- **Knicken und Verformung ohne x-Bewehrung:** der Knopf zeigte «1 Fall»
  in Blau, das Fenster schwieg, gerechnet wurde nichts. Jetzt steht auf dem
  Knopf «keine x-Bewehrung» und im Fenster «Noch keine x-Bewehrung – so
  rechnet kein Fall.»
- **Gebrauchsfälle «aus der Tragsicherheit» ohne eingeschaltete
  Einwirkung:** der Knopf zeigte «60 %» in Blau, das Fenster «Nur die
  abgeleiteten Fälle.» Jetzt «keine Einwirkung» und im Fenster, dass nichts
  abgeleitet wird, solange keine Einwirkung eingeschaltet ist. In der
  Querschnittsanalyse ebenso, dort mit den Lastfällen.
- **Welcher Querkraftblock gilt:** «ohne Bügel» (D_max, Einlage) und «mit
  Bügeln» (k_c, α) standen gleich da, obwohl je nach Bügeln nur einer
  wirkt. Jetzt ist der andere blass und sagt, warum: «gilt nicht: es liegen
  Bügel» oder «gilt erst mit Bügeln».

## 2026-11-19 · Balkensysteme: Lager, Profile und Hinweise

Sechster Schritt der Durchsicht, der zweite Teil der Balkensysteme.

- **Meldungen eines Lagers:** standen nur unter der Zeichnung, nicht im
  Fenster des Knotens, wo man das k tippt; ein Klick auf eine solche Meldung
  hob die Wahl sogar auf. Jetzt steht «A1: eine Feder braucht eine
  Steifigkeit grösser als null.» auch beim Knoten, und der Klick wählt ihn.
- **«je Richtung» beim Lager:** war ein Knopf, der nichts Sichtbares tat –
  ohne Lager legte er ein gelenkiges an, mit Lager blieb alles, wie es war.
  Jetzt steht «je Richtung» nur da, wenn die Richtungen darunter zu keiner
  Vorwahl passen, und leuchtet dann.
- **Ein Profil «um z»** stand im Bild hoch wie «um y», gerechnet aber mit
  I_z. Jetzt liegt es: ein IPE 300 ist im Bild 300 breit und 150 hoch.
- **Die Diagramme in 2D:** die Schalter lauteten «M V N …», im Raum «N V_y
  V_z T M_y M_z …». Jetzt beide mit N zuerst, wie die Tabelle der
  Grenzwerte.
- **Hinweise, wo vorher nichts stand:**
  - nimmt eine Linie das Material «gemäss Querschnitt», fehlen in ihrer
    Liste die Vorlagen, Profile und Kennwerte – jetzt sagt ein Satz, warum;
  - im Fenster eines Querschnitts aus Platte oder Analyse steht, dass man
    E₀ oder E_eq wählt, sobald ein Stab «gemäss Querschnitt» nimmt;
  - im Fenster «Material» steht sichtbar, warum «+ Baustahl» gesperrt ist:
    «Im Projekt gibt es keinen Baustahl – anlegen in der App
    «Materialien».» Vorher nur im Tooltip, den es auf dem Tablet nicht gibt.

## 2026-11-19 · Balkensysteme: was die Fenster zeigen, stimmt wieder

Fünfter Schritt der Durchsicht, der erste Teil der Balkensysteme.

- **Das Material in der Liste unter der Zeichnung:** stand bei jedem Stab
  «–», weil es unter den Materialien des Projekts gesucht wurde statt unter
  denen des Systems. Jetzt: «L1 K1 → K2 · Stütze 300×300 · C30/37».
- **E_eq beim Umschalten der Querschnittsart:** blieb stehen. Wer einen
  Querschnitt aus einer Platte mit E_eq auf «Vorlage» umstellte, hatte einen
  Querschnitt, der nicht rechnete («ein E_eq gibt es nur …»), und solange
  kein Stab «gemäss Querschnitt» nahm, keinen Schalter, um es abzuwählen.
  Jetzt bekommt er das E eines neuen Querschnitts zurück, E₀.
- **Was das Werkzeug «Linie» vorgibt:** galt, was beim Öffnen der erste
  Querschnitt war. Ein neues System zeichnete darum auch nach dem ersten
  Querschnitt jede Linie als «kein Stab», und ein gelöschter Querschnitt
  blieb die Vorgabe – die Linie bekam ihn trotzdem, und das System rechnete
  nicht. Jetzt gilt der gewählte, solange es ihn gibt, sonst der erste;
  «– kein Stab –» nur, wenn man es wählt. Ebenso beim Material.
- **Eine Last «quer» oder «längs zum Stab» auf einem Knoten:** wurde still
  «senkrecht». Jetzt kommt sie auf den Stab, an sein Ende, und behält ihre
  Richtung. Ein Moment in der Ebene hat keine Richtung und geht weiter an
  den Knoten.
- **«Kein Lastfall.»** stand bei jedem System, das nicht rechnet, auch mit
  drei Lastfällen. Jetzt nur, wenn es keinen gibt; sonst sagt die Meldung,
  was fehlt.
- **Leere Listen sagen es:** «– kein Stab: noch kein Querschnitt –», «– noch
  kein Material im System –».

## 2026-11-19 · Ein Name kann nicht leer sein

Vierter Schritt der Durchsicht.

- **Vorher:** ein geleertes Namensfeld galt, und niemand sagte etwas. Bei
  einer Platte, einer Querschnittsanalyse, einem Balkensystem, einem
  Grundbruch, einer Setzung oder einem Pfahl hielt das dann das ganze
  Projekt an: «Platte q1: 'name' darf nicht leer sein.» Ein Lastfall ohne
  Namen liess sein Diagramm «wird gerechnet» sagen, ohne je fertig zu
  werden; das Python-Skript behielt still den alten Namen.
- **Jetzt:** jedes Namensfeld weist einen leeren Namen gleich ab und behält
  den bisherigen: «Ein Name kann nicht leer sein: «Decke über EG» bleibt.»
  So bei allen Bauteilen, Lastfällen und Kombinationen, Schichten, den
  Querschnitten und Materialien eines Balkensystems, den Fällen und den
  Skripten.
- Das Feld eines eigenen Materials wies schon vorher ab, aber knapp («Name
  leer.»). Es geht jetzt durch dasselbe Feld und sagt beim Namen eines
  anderen Materials: «Den Namen «C30/37» trägt schon ein anderes Material:
  «BE1» bleibt.» Leerzeichen am Rand schnitt es still weg; jetzt gilt, was
  getippt ist.
- Der Baustein ist `namensfeld` in `bausteine.js`. Gleiche Namen von
  Bauteilen meldet weiter der Kern beim Eintrag, der sie hat.

## 2026-11-19 · Ein Zahlenfeld nimmt nur, was der Kern nähme

Dritter Schritt der Durchsicht: was fehlt, soll man am Ort sehen – bei einer
Zahl ist das ihr Feld.

- **Vorher:** die Pfeile hielten sich an die Grenzen des Kerns, Getipptes
  nicht. Eine Stelle von 150 %, eine Dicke von −5 mm oder k_c = 0 kam in
  die Rechnung und hielt dort ihr Bauteil an – man sah es erst danach,
  und nicht am Feld.
- **Jetzt:** das Feld weist die Zahl gleich ab, mit dem Satz des Kerns, und
  behält seinen Wert: «Dicke h muss grösser als null sein: -5 ist nicht
  übernommen.» Ebenso ein geleertes Feld, das als 0 zählt, wo 0 nicht
  geht (die Druckkraft N_Ed des Grundbruchs).
- Der Satz steht einmal, im Kern: `feldangaben` gibt zu den Grenzen eines
  Bereichs `heisst` und `verlangt` mit, `zahlfeld` setzt sie zusammen. Ein
  Test hält fest, dass es derselbe Satz ist, den das Rechnen sagt.
- Rund zwanzig Felder bekamen die Grenzen des Kerns erst jetzt – vorher
  hatten sie eigene `min`/`max` der Oberfläche oder keine: Dicke, Breite,
  Überdeckungen, Grösstkorn, Einlage und k_c der Platte, die Durchmesser
  von Lagen und Bügeln, die Kriechzahlen, k der Grenze x/d, die Anteile
  der Gebrauchslisten, die Längen beim Knicken und bei der Verformung, k_c
  der Querschnittsanalyse, die Stelle einer Einzellast im Balkensystem.
  Bei k_c liess die Oberfläche 0 zu, der Kern nicht.
- Was mehrere Felder zusammen betrifft – α_min nicht über α_max, eine
  Teilung, sobald ein Durchmesser da ist –, prüft weiter das Rechnen;
  dann sagt es das Bauteil.

## 2026-11-19 · Eine Eingabe, die der Kern abweist, hält nur ihr Bauteil an

Zweiter Schritt der Durchsicht. Der erste liess hart, «was eigentlich nur
eine verdorbene Datei erzeugt» – aber die Durchsicht fand Wege dorthin über
die Bedienung, und die Regel des Benutzers sagt: der Rest rechnet weiter.

- **Vorher:** k_c = 0 bei einer Platte, eine Kriechzahl unter null, zwei
  Lastfälle gleichen Namens, eine Normsorte mit eigenem Namen, ein
  gelöschter Beton, den ein Pfahl noch wählt: oben «Fehler», und jedes
  Bauteil zeigte das Ergebnis zur Eingabe davor.
- **Jetzt:** nur das Material oder Bauteil, das es betrifft, rechnet nicht
  und sagt über seinen Eingaben, warum – «Nichts zu rechnen: k_c muss
  grösser als null sein, angegeben ist 0.» Wer ein Material nimmt, das
  nicht rechnet, sagt «das Material «Mein Beton» rechnet nicht – warum,
  steht bei ihm.» Oben rechts «alle Nachweise erfüllt · 4 Bauteilen und
  einem Material fehlt noch etwas».
- Ein Material, das ein Bauteil wählt, heisst in der Meldung nach seinem
  Feld: «Beton: das Material 'b1' gibt es nicht mehr – eines wählen.»,
  «Stahl: noch kein Material gewählt.» Vorher stand der Name des Bauteils
  doppelt, sobald die Meldung am Bauteil stand («Platte 'Decke': Platte
  'Decke' verweist auf …»). Dafür gibt `ort_von` dem gelesenen Eintrag
  denselben Ort wie die Prüfung der Datei.
- Im Kern prüft `aufbauen` das Projekt ohne seine Listen. Jedes Material
  und jedes Bauteil prüft und baut sich dann für sich, und was dabei
  scheitert (`ProjektFehler`), wird `Aufbau.unfertig` – mit seinem Ort,
  damit es im Bericht lautet wie vorher (`Unfertiges.meldung`).
- Hart bleibt, was alle betrifft: die Form der Datei, zwei gleiche
  Kennungen, zwei Materialien desselben Namens. Die Bewehrungssuche nimmt
  ein unfertiges Bauteil als Nein, wie vorher den Fehler.
- Rund hundert Tests erwarteten den Fehler; sie prüfen jetzt die Meldung
  des unfertigen Eintrags (`tests/unfertig.py`).

## 2026-11-19 · Ein unfertiges Bauteil hält nur sich auf

Der Benutzer bat um beides: den Schalter «E-Modul» (unten) und eine
Durchsicht aller Fenster nach der neuen Regel, ein Bereich nach dem
anderen. Vier Durchsichten liefen nebeneinander; was zuerst auffiel,
betrifft alle Bereiche: ein Bauteil, dem noch etwas fehlte, liess das
ganze Projekt scheitern.

- **Vorher:** eine Platte ohne Bewehrung, ein Pfahl ohne Schicht oder
  ohne Boden unter dem Fuss und eine Querschnittsanalyse mit halbfertiger
  Zeichnung – etwa ein Stab, noch kein Polygon – hielten alles an: oben
  «Fehler», rechts das Ergebnis zur Eingabe davor.
- **Jetzt:** nur dieses Bauteil rechnet nicht. Über seinen Eingaben, in
  der Zusammenfassung und bei den Diagrammen steht «Nichts zu rechnen:
  noch keine Bewehrung.», oben rechts «alle Nachweise erfüllt · einem
  Bauteil fehlt noch etwas» – nicht grün, denn die Platte ohne Bewehrung
  ist nicht nachgewiesen. Ein Stab, der ihren Querschnitt nimmt, sagt
  «die Platte «Decke» rechnet nicht (noch keine Bewehrung).»
- Im Kern merkt sich `Aufbau.unfertig` Art, Name und Grund
  (`Aufbau.unfertige`); es ersetzt `leere_analysen`, das nur die leere
  Analyse kannte. Die Seite bekommt sie unter ihrer Liste wie die
  Zuordnung, und Zusammenfassung und Diagramme gehen die Bauteile jetzt in
  der Reihenfolge des Projekts durch (`bauteileDer`), gerechnete und
  unfertige zusammen.
- Hart bleibt, was eigentlich nur eine verdorbene Datei erzeugt: ein
  Verweis ins Leere, eine Zahl ausserhalb ihres Bereichs. Die Durchsicht
  fand aber Wege dorthin über die Bedienung – ein Material, das gelöscht
  wird, während es verborgen noch gewählt ist; ein Schalter, der eine
  erlaubte Zahl unerlaubt macht. Die folgen bereichsweise.
- Der Schalter «Biegung» eines Profils schreibt «um y – stark» wie
  geschrieben, nicht gross, wie der Schalter «E-Modul».

---

## 2026-11-19 · Empfehlungen umgesetzt, Bedienung erklärt sich selbst

Der Benutzer nahm die Empfehlungen des Vortags an und bat, die vier
Aufräumpunkte auch zu machen: «generell sollte einfach die bedienung
selbsterklärend sein». Das steht jetzt als Regel in [[Arbeitsweise]].

- **Grundbruch:** ein negatives σ_f gibt keinen Widerstand. Die Zeile
  zeigt es jetzt, statt dass die Zahlen nicht aufgehen: vorher
  −9 kPa · 1.6 m · 4 m = 0 kN, jetzt max[0; −9 kPa] · 1.6 m · 4 m = 0 kN,
  davor ein Satz, dass das nach Vorgabe ist – das Buch sagt dazu nichts.
- **Hauptachsen im Raum:** ein Querschnitt aus einer Analyse bringt im Raum
  I_yz mit, und ab 5 % von min(I_y; I_z) sagt ein Hinweis, dass y und z
  keine Hauptachsen sind. Er hält die Rechnung nicht auf und steht unter
  der Zeichnung, im Fenster des Querschnitts und im Bericht. Warum dieses
  Mass und nicht der Winkel der Hauptachsen: bei einem schlanken
  Querschnitt verbiegt schon ein Drittel Grad den Stab merklich zur Seite,
  bei einem fast quadratischen ist ein grosser Winkel harmlos. |I_yz| /
  min(I_y; I_z) ist genau das Verhältnis der Krümmung quer zur Krümmung
  um die steifere Achse.
- **Noch ohne Platte oder Analyse:** wer auf «Platte» oder «QS Analyse»
  umschaltete, liess bis heute das ganze Projekt scheitern, und das
  Fenster zeigte weiter die Werte von vorher. Zwei Gründe: die leere Wahl
  galt als Verweis auf etwas, das es nicht gibt, und beim Umschalten blieb
  die alte Wahl stehen – eine Analyse galt dann als «Platte» (im Browser
  gefunden). Jetzt beginnt jede Art mit leerer Wahl; solange sie leer ist,
  rechnet nur dieser Querschnitt nicht, die Meldung sagt «noch keine
  Querschnittsanalyse gewählt», und eine leere Liste sagt «noch keine im
  Projekt». Ein Verweis auf etwas, das es nicht gibt, scheitert weiter
  hart.
- Das Fenster eines Querschnitts zeigt die Meldungen des Kerns zu ihm; das
  Bild von Kennwerten von Hand nennt im Raum A, I_y, I_z und I_T statt
  «A, I»; die Hilfe der Ebene kennt «Kennwerte» und sagt nicht mehr, E_eq
  gebe es nur bei einer Analyse; der Schalter Linie/Punkt der Bewehrung ist
  ein gewöhnlicher `wahlSchalter`.
- Danach, auf Wunsch: der Schalter «E-Modul» schreibt E_cm und E_eq, wie
  sie heissen – gross geschrieben stand dort E_CM und E_EQ, andere
  Grössen. Die 5 % des Hinweises bleiben (Benutzer: «5 % lassen»).

---

## 2026-11-18 · 3D-Balkensystem: Querschnitt aus einer Querschnittsanalyse

Jetzt kann ein Stab im Raum seinen Querschnitt auch aus einer
Querschnittsanalyse nehmen – der letzte Unterschied zur Ebene bei der Wahl
des Querschnitts (Benutzer, selber Tag: «genau gleich, einfach einmal in
3d»). Dafür fehlte ein I_T: die Analyse kannte A, I_y und I_z, aber für ein
beliebiges Polygon gibt es keine Formel der Torsion. Jetzt rechnet sie es
selbst, numerisch, und zwar nur, wenn ein Stab im Raum es braucht – das
Rechenwerk rechnet nur, was ein Ziel verlangt, und die Ebene verlangt es
nie. Beispiel: das Rechteck 300 × 600 mm einer frischen Analyse hat
I_T = 3704.7 · 10⁶ mm⁴, die Reihe von St. Venant gibt 3704.6 · 10⁶ mm⁴;
gerechnet in 0.1 s.

- `querschnitt/torsion.py`: die Spannungsfunktion von Prandtl auf einem
  Gitter durch die achsparallelen Kanten, schräge Kanten genau
  geschnitten, jeder Hohlraum ein einziger Knoten, gelöst mit konjugierten
  Gradienten; dazu ein zweites Gitter, halb so gross, und Richardson.
  Warum zwei Gitter: eine dünne Wand mit n Zellen rechnet um 2/n² zu steif,
  bei vier Zellen also 12 %; extrapoliert bleibt davon nichts. Liegen die
  beiden über 5 % auseinander, wird feiner gerechnet – das braucht nur eine
  dünne schräge Wand.
- Getrennte Teile tragen je für sich, eine Insel im Hohlraum zählt zu
  seiner Fläche, eine Aussparung am Rand ist kein Hohlraum. Ohne fremde
  Pakete, wie alles hier; Formeln und Theorie in der Formelsammlung.
- Die Herleitung zeigt beide Gitter und I_T mit Zahlen. Im Raum gelten y
  und z als Hauptachsen, I_yz bleibt aussen vor – das sagt die Herleitung,
  und [[TODO]] hat den Punkt mit einem Vorschlag.
- Das Prüfprojekt hat im Raumrahmen je einen Stab aus Platte und Analyse.

---

## 2026-11-18 · 3D-Balkensystem: Querschnitt aus einer Platte

Im 3D-Balkensystem kann ein Querschnitt jetzt aus einer Platte kommen, wie
in der Ebene (Benutzer, selber Tag: «Es soll eigentlich genau gleich
funktionieren, einfach einmal in 3d»). Vorher standen dort nur Vorlage,
Profil und Kennwerte von Hand; jetzt auch «Platte», mit dem Material
«gemäss Querschnitt» an der Linie und auf Wunsch E_eq. Im Beispiel, Platte
C30/37 mit h = 250 mm und einem Streifen von 1000 mm, rechnet ein Kragarm
mit A = 250 000 mm², I_y = 1302 · 10⁶ mm⁴, I_z = 20 833 · 10⁶ mm⁴ und
I_T = 4388 · 10⁶ mm⁴ – den Formeln des Rechtecks –, E_cm und G_cm.

- Was Ebene und Raum am Querschnitt teilen, steht jetzt einmal
  (`projekt/staebe.py`): Bezug, E-Modul und die Frage nach E_eq beim
  Eintrag, das Auflösen der Art beim Bauen (`stabquerschnitt_von`).
  Der Raum fügt nur hinzu, dass ein Profil sich um beide Achsen biegt.
- Der Streifen liegt mit b waagrecht, solange β null ist, wie eine Platte.
- Ein E_eq gilt für EA, EI_y und EI_z; GI_T rechnet mit G_cm (nach
  Vorgabe, in [[TODO]]). Die Herleitung sagt es.
- «QS Analyse» fehlte im Raum noch: die Querschnittsanalyse rechnete
  kein I_T (siehe den Eintrag darüber).

---

## 2026-11-18 · Rechenart mit Bild

Wo man die Rechenart wählt – Hand, 0.85·x, präzise, elastisch –, steht
vor dem Wort jetzt ein kleines Bild: wie die Art den Beton rechnet,
Spannung über Dehnung (Benutzer, selber Tag: die Wörter allein seien
verwirrend). 0.85·x ist eine Stufe, präzise eine Parabel mit waagrechtem
Ende, elastisch eine Gerade; die Handrechnung eine Hand, die die Formel
«x =» hält – sie rechnet mit dem Block, aber in geschlossenen Formeln.
Vorher stand dort nur «Hand | 0.85·x | präzise».

- Die Bilder stehen bei den anderen Sinnbildern (`sinnbilder.js`,
  `rechenart-…`), gezeichnet nach den Gesetzen in `werkstoffgesetz.py`: der
  Block springt bei 0.15 · ε_c2d auf f_cd, die Parabel wird bei ε_c1d
  waagrecht.
- Ein Schalter trägt auf Wunsch zu jeder Stellung ein Bild (`wahlSchalter`,
  `zeichen`); die Rechenarten bekommen es an einer Stelle
  (`rechenartStellungen`) – im Kapitel, in den Karten der Analysen und beim
  Betongesetz je Material der Querschnittsanalyse.
- Mit vier Bildern war die Rechenart einen Pixel zu breit für ihr Fenster;
  sie nimmt jetzt die ganze Zeile, unter φ hindurch.

---

## 2026-11-18 · Pfahl: Kurzform der Querkraft

Das Auge zeigt die Querkraft im Bohrpfahl jetzt auch kurz, in drei Zeilen:
der Widerstand der Wendel, der der Druckdiagonalen und der Erfüllungsgrad
mit dem Minimum darin, im Beispiel «Jeder Nachweis einmal» beim ersten Pfahl
η_i · min[335.9 kN; 1374.8 kN] / 150 kN = 1.79. Vorher stand dort nur die
lange Herleitung. Der Benutzer hatte die Wahl der Empfehlung überlassen; es
ist der Kandidat, den [[TODO]] nannte. Der Mikropfahl bleibt ohne Kurzform:
sein Widerstand ist schon die Schubfläche und eine Zeile mit f_yd / √3.

---

## 2026-11-18 · Balkensystem: «QS Analyse» statt «Aus QS Analyse»

Der Schalter steht unter «A und I aus», und dort las man «A und I aus …
Aus QS Analyse». Jetzt heisst die Stellung «QS Analyse», ebenso die Zeile
in der Hilfe. Der Benutzer hatte die Wahl der Empfehlung überlassen.

---

## 2026-11-18 · Querschnittsanalyse: jede Schubwand für sich

Eine gezeichnete Wand ist dort geteilt, wo eine andere auf ihr endet oder
sie kreuzt, und jedes Teil ist eine eigene Schubwand mit eigener Kraft und
eigenem Widerstand (Benutzer, selber Tag: «jede Schubwand separat … die
Einwirkung präzise verteilen»). Ein Deckel über zwei Zellen ist so zwei
Wände, «Wand 1.1» und «Wand 1.2». Mit einer Mittelwand im Unterzug
zerfällt der Boden, Wand 1, in Wand 1.1 (70 mm) mit 5.1 kN gegen 27.6 kN und
Wand 1.2 (130 mm) mit 11.4 kN gegen 51.3 kN; vorher zählte er als eine Wand
mit dem stärkeren Fluss über seine ganze Länge. In der Zusammenfassung steht
die massgebende Wand.

- Geteilt wird einmal, an der Grenze (`schubwaende.einzeln`, gerufen von
  `zellen`): das Modell hält die geteilten Wände, und Verteilung, Kraft,
  Längszug, Nachweis, Kennzahlen und Bild rechnen ohne den Umweg über
  «Stücke einer Wand». Die Klasse `Stueck` ist weg.
- Die Federn ändert das Teilen nicht: Teile auf einer Linie verschieben und
  drehen sich gleich, ihr Fluss ist der der ganzen Wand – ein Test zeichnet
  denselben Kasten einmal mit ganzem, einmal mit geteiltem Deckel.
- Das Bild «Schubfluss» zeichnet jede geteilte Wand mit Band, Pfeil und
  Farbe; rot wird nur das Teil, das nicht hält. Es liest dafür nicht mehr
  die gezeichneten Wände, sondern die des Nachweises.
- Die Formel heisst jetzt V_Ed = |q|·l, «Kraft einer Wand: ihr Schubfluss
  über ihre Länge»; die Regel «der stärkste Fluss über die ganze Länge» und
  ihr Eintrag in [[TODO]] sind weg. In den Beispielen ist keine Wand geteilt,
  ihre Zahlen bleiben.

---

## 2026-11-18 · Querschnittsanalyse: Schubwände mit ganzer Kraft

Der Nachweis «Querkraft und Torsion» der Querschnittsanalyse rechnet je
Schubwand mit ihrer ganzen Kraft statt je Meter (Benutzer, selber Tag). Im
Beispiel «Unterzug», Lastfall Feld, stand für Wand 2 |q_Ed| = 225 kN/m
gegen v_Rd = 394.3 kN/m; jetzt V_Ed = 112.5 kN gegen V_Rd = 197.2 kN. Der
Erfüllungsgrad bleibt 1.75 – jeder bleibt, wie er war.

Warum so:

- Die Norm rechnet selbst so: (55) gibt die Torsion einer Zelle als Kraft
  je Wand, V_d,i = T_d/(2·A_k)·z_i mit der Länge z_i der Wand, und 4.3.5.5
  zählt sie mit der Querkraft zusammen (SIA 262:2025, S. 59, nachgeschlagen).
  Der Widerstand ist das Fachwerk (45), (47) mit z = l.
- Eine Regel an einer Stelle: `schubwaende.wandkraefte` gibt je Wand
  V_Ed = max|q|·l, `widerstand` das Fachwerk mit z = l. Nachweis,
  Kennzahlen und das Bild «Schubfluss» lesen beide. Vorher suchten Nachweis
  und Kennzahlen das stärkste Stück je für sich, mit verschiedenen Schwellen
  für das Rundungsrauschen.
- Trägt eine Wand zwischen zwei Zellen stückweise verschiedene Flüsse,
  zählt der stärkste über die ganze Länge: nach Vorgabe, auf der sicheren
  Seite und mit demselben Grad wie je Meter. Steht in [[TODO]] bei
  «Federmodell und Bredt».
- Die Kennzahlen V_z,Rd, V_y,Rd und T_Rd zeigen je Wand ebenso V_1 und V_Rd
  in kN; ihre Werte bleiben.
- Bei Gleichstand heisst die erste Wand massgebend (`schwaechste`): mit der
  Länge multipliziert wichen gleiche Werte in der letzten Stelle ab, und
  unter Torsion hiess sonst Wand 2 statt Wand 1 massgebend.
- Die Pfeile im Bild «Schubfluss» bleiben ein Fluss in kN/m – das Bild
  zeigt, wie er sich verteilt. Seine Legende nennt je Wand V_Ed, V_Rd und
  α_eff.

## 2026-11-16 · Kurzform eines Nachweises

Wer in der Zusammenfassung das Auge eines Nachweises anklickt, sieht über
der Herleitung die Karte «Kurzform»: den Nachweis in zwei, drei Formeln,
mit Word, TeX und MD im Kopf, um alle auf einmal zu kopieren (Benutzer,
selber Tag). Die Biegung der Platte bei N = 0 steht dort als

    M_Rd = A_s · f_yd · (d − A_s · f_yd / (2 · b · f_cd)) = 235.9 kNm
    α = M_Rd / M_Ed = 1.57

statt in den Zeilen der Handrechnung (x, Hebelarm, Moment). Die
Plattenquerkraft steht als ε_v, V_Rd = τ_cd · d_v / (1 + ε_v · d · k_g)
und α; die Querkraft mit Bügeln als V_Rd,s, V_Rd,c und
α = min[V_Rd,s; V_Rd,c] / V_Ed.

Warum so:

- Die Kurzform rechnet nichts Neues, sie schreibt die Mitschrift kürzer
  auf (`core/kurzform.py`). Vom Erfüllungsgrad aus sucht sie rückwärts je
  Platzhalter die Zeile, die seinen Wert rechnet, und setzt deren Formel
  ein. Was eine Zeile dabei ist, sagt die Berechnung, die sie schreibt:
  `kurz=Kurz.EINSETZEN` geht ein, `Kurz.ZEILE` steht als eigene Zeile
  davor, alles andere bleibt ein Symbol mit seiner Zahl. Eine Liste von
  Hand, welcher Nachweis wie aussieht, gibt es so nicht.
- Eingesetzt wird nur, solange die Formel schmal bleibt (`KURZBREITE`,
  40 Zeichen) und kein Bruch dabei in Zähler oder Nenner eines anderen
  gerät: dort setzt die Anzeige ihn klein, mit Einheiten in der
  Zahlenzeile kaum lesbar. Die Plattenquerkraft am Rand (elastisch) stand
  zuerst als eine Zeile mit Bruch im Bruch im Nenner; jetzt steht ε_v
  davor, wie bei der plastischen.
- Jede eingesetzte Formel wird nachgerechnet. Gibt sie nicht genau das
  Ergebnis ihrer Zeile, bleibt es bei den Zeilen. Dafür liest ein kleiner
  Formelbaum (`core/formelbaum.py`) das LaTeX der Vorlagen, setzt ein,
  kürzt gleiche Faktoren (die 0.85 des Spannungsblocks steht in x und in
  M_Rd) und schreibt die Formel wieder. sympy kam als fremdes Paket nicht
  in Frage. Was der Baum nicht liest, bleibt eine eigene Zeile.
- Eine Grösse, die als blanke Zahl in fester Einheit eingeht (d in mm bei
  k_d), wird nie ersetzt; «(d in mm)» steht hinter der Formel.
- Eine Zeile, die einen Wert nur weitergibt (M_Rd = M_Rd(N_Ed = 0)), wird
  übersprungen. Damit die Resistenzlinie an einem Eckpunkt dorthin findet,
  kennt `Eckpunkt.werte` die Werte der Handrechnung; nebenbei zeigt die
  Formelsammlung dort jetzt «Gebraucht von».
- Eine eingesetzte Formel hat keine Vorlage mehr und steht darum nicht in
  der Formelsammlung. Ihre Normstellen sind die aller Zeilen, die in ihr
  aufgingen, die Norm einmal genannt.
- Gekennzeichnet ist heute nur die Platte: Biegung bei N = 0, Querkraft
  mit und ohne Bügel. Wo nichts gekennzeichnet ist oder zwischen zwei
  Eckpunkten interpoliert wird, fehlt die Karte.

## 2026-11-16 · Decken: M und V eines Unterzugs

Ein Ergebnisbild zeigt auch einen Unterzug selbst: sein Moment M und seine
Querkraft V über die ganze Breite, in kNm und kN statt je Meter
(Benutzer, selber Tag). Im Kolloquium 4 etwa liegt U4 auf U1, U2 und U3:
über U2 ist M = −60.1 kNm, im Feld 47.9 kNm.

Warum so:

- Ein Unterzug ist im Kern ein Streifen mit eigenen Trägern; ihre Polynome
  für M und V gelten für die ganze Breite. Das Bild nimmt sie unverändert,
  statt das Feld der Platte über die Breite zu integrieren – das gäbe
  dasselbe nur ungenauer. Ein Bild der Platte teilt sie durch die Breite:
  m = M/b (geprüft in `tests/test_decke_schnitt.py`).
- Gewählt wird er wie ein Schnitt, in derselben Liste unter «Ergebnisse»:
  «ganze Platte», «längs Schnitt SN1», «Unterzug U1». Der Schalter daneben
  zeigt dann M und V statt m_x … v_0; wer zwischen Platte und Unterzug
  wechselt, bekommt dort die erste Grösse. Das Feld der Zeile heisst weiter
  `schnitt`: ein neuer Name hätte die heutigen Speicherstände unlesbar
  gemacht, weil das Lesen unbekannte Felder abweist.
- Das Bild ist das eines Schnitts (dk_schnitt.js), ohne Bänder: die Lager
  sind die seiner Träger – Linienlager, Stützen und Unterzüge höherer
  Stufe. Die Stelle s läuft ab dem ersten Knoten des Unterzugs; zeigt die
  Richtung seines Streifens anders herum, kehrt V das Vorzeichen, damit im
  Bild V = dM/ds gilt.
- Rechnet ein Fall einen Träger nicht – er trägt keine Last, oder er trägt
  nicht, und eine Meldung sagt es –, zeigt das Bild dort null.
- Passen Grösse und Ort nicht zusammen, etwa M über die ganze Platte, sagt
  die Karte es, statt etwas anderes zu zeigen. Das kommt nur aus einer von
  Hand geänderten Datei vor; die Bedienung lässt es nicht zu.

## 2026-11-16 · 3D-Balkensystem: drehen mit Alt

Im 3D-Fenster dreht auch die linke Maustaste die Ansicht, wenn dabei Alt
gedrückt ist, nicht nur die rechte (Benutzer, selber Tag).

Warum so:

- Alt hiess im Zeichenfenster schon «nicht fangen». Beides geht zusammen,
  weil das eine ein Ziehen ist und das andere ein Klick: mit Alt gezogen
  dreht die Ansicht, mit Alt geklickt entsteht wie bisher ein Punkt ohne
  Fangen. Es entscheidet, ob der Zeiger über die Zitterschwelle wandert.
- Manche Linux-Oberflächen verschieben mit Alt und Ziehen das ganze
  Fenster; dann kommt der Zug nie im Browser an. Die rechte Maustaste dreht
  darum weiter.

## 2026-11-16 · Decken: Schnitte

Im Grundriss einer Decke lassen sich Schnitte zeichnen, SN1, SN2 …; längs
eines Schnitts zeigt ein Ergebnisbild eine Grösse der Platte wie an einem
Balken des Balkensystems, mit den Lagern und Unterzügen, die er kreuzt
(Benutzer, selber Tag).

Warum so:

- Ein Schnitt ist eine Linie zwischen zwei Knoten, gezeichnet wie ein
  Linienlager (Werkzeug «Schnitt», Taste N). Welches Bild längs welchem
  Schnitt, sagt die Zeile unter «Ergebnisse»: neben der Grösse die Wahl
  «ganze Platte» oder «längs Schnitt SN1». Eine Auswahlliste, weil ihre
  Einträge mit dem Projekt wachsen; sie erscheint erst, wenn es Schnitte
  gibt. Die Lagerkräfte zeigen immer die ganze Platte.
- Der Kern tastet den Schnitt mit derselben Funktion ab, die die Zellen des
  ganzen Bildes füllt (`an_stelle`), nie genau auf einer Grenze: auf dem
  Rand eines Unterzugs zählten Streifen und Unterzug beide, ein schräger
  Schnitt zeigte dort einmal einen Ausreisser. Die Grenzen der Streifen, die
  Ränder der Unterzüge und die Enden der Trägerstücke teilen den Schnitt;
  abgetastet wird je Teil 10⁻⁶ m innen, dazwischen auf einem Raster von
  L/120 und wo V oder die Last null wird, dort liegen die Spitzen. An einem
  Sprung stehen so zwei Werte an derselben Stelle, und der Verlauf steht
  dort senkrecht.
- Lager im Bild: ein Linienlager, das der Schnitt kreuzt – eines, das er
  entlang läuft, nicht; eine Stütze nur, wenn er durch ihren Querschnitt
  geht, an der Stelle nächst ihrer Mitte. Ein Unterzug ist ein Band über
  der Achse; läuft der Schnitt in einem und kreuzt andere, stehen ihre
  Namen in Zeilen übereinander.
- Positive Werte unten, wie im Balkensystem das Moment auf der Zugseite.
  Beschriftung und Zeiger teilt das Bild mit dem Balkensystem
  (`anschreiben`, `zeigerEinrichten` in `bs_diagramme.js`).
- Je Schnitt wächst die Antwort um etwa 9.5 kB. Im Kolloquium 4 längs U4:
  m_x −60.1 kNm/m über S2, 47.9 kNm/m bei s = 2.04 m; längs U2 m_y
  123.7 kNm/m bei s = 2.475 m.

## 2026-11-16 · Decken: glatte Ergebnisbilder

Die Bilder der Momente und Querkräfte einer Decke sind nicht mehr gekachelt:
in jeder Zelle verläuft die Farbe (Benutzer, selber Tag). Er fragte, warum
das Bild gestuft sei, wo doch dahinter eine Parabel stehe.

Warum so:

- Gerechnet wird nach der Streifenmethode: längs eines Streifens ist m ein
  Polynom, quer gilt im ganzen Streifen derselbe Wert. Gestuft war das Bild,
  weil jede Zelle nur den Wert in ihrer Mitte zeigte. Jetzt gibt der Kern je
  Zelle und Grösse dazu ein Gefälle (`feld.gefaelle`): das der Ebene durch
  den Wert in der Mitte, die die Werte an den Ecken – 0.1 mm innen – nach
  den kleinsten Quadraten am besten trifft. Die Oberfläche zeichnet daraus
  einen linearen Verlauf, mit einem Halt bei null, wo die Farbe von blau
  nach rot knickt.
- Eine Zelle liegt in genau einem Streifen jeder Richtung, und Unterzüge,
  Lagerenden und Stützenbereiche liegen auf ihren Rändern, weil die
  Streifen dort geteilt werden. In einer Zelle ist darum jede Grösse ausser
  v_0 eine Summe von Polynomen längs der Streifen. Auf einem Rechteck hat
  die Ebene das Gefälle der Sehne – bei einer Parabel die Ableitung in der
  Mitte, das prüft ein Test –, und Nachbarn im selben Streifen treffen sich
  an der gemeinsamen Kante. Quer zu den Streifen bleiben die Sprünge: die
  rechnet die Streifenmethode wirklich.
- Gefälle aus den Ecken statt feinerer Zellen: feinere wären wieder
  gestuft, nur feiner, und die Antwort wüchse mit dem Quadrat. Mit den
  Gefällen wächst sie im Kolloquium 4 von 68 auf 131 kB, und die Anfrage
  dauert 0.22 statt 0.14 s. Ein SVG kann keine Farben zwischen den Ecken
  eines Vielecks mischen; ein linearer Verlauf je Zelle ist, was es kann.

## 2026-11-16 · Querschnittsanalyse: wie viele Stäbe im Kreis

Die runde Vorlage fragt neben dem Durchmesser nach der Zahl der Stäbe n
(Benutzer, selber Tag); bisher waren es immer acht ⌀16.

Warum so:

- Eine Anzahl ist ein Mass der Vorlage wie eine Länge, nur ganzzahlig
  (`Mass.ganzzahlig`): dieselbe Prüfung auf grösser als null, dazu eine auf
  ganze Zahlen – 7.5 Stäbe geben eine Meldung, keine stille Rundung. Einheit
  und Schritt des Feldes sagt der Katalog; das Fenster schreibt nicht mehr
  hinter jedes Mass «mm».
- Die Stäbe liegen gleich verteilt wie die Ecken des Kreises, der erste
  rechts: beide kommen aus `kreispunkte`, das jetzt die Zahl der Punkte
  nimmt. Bei n = 8 liegen sie genau wie bisher.
- Ob sich die Stäbe bei grossem n überlappen, prüft die Vorlage nicht; die
  Analyse prüft es auch bei einer Stablinie nicht. Man sieht es in der
  Skizze.

## 2026-11-15 · Der Pfahl rechnet mit dem Verlauf des Balkensystems

Der gebettete Pfahl integriert seine Schnittkräfte nicht mehr selbst (Punkt
2 der Strukturdurchsicht vom selben Tag). Am Bildschirm und im Bericht des
Pfahls ändert sich keine Zahl; im Balkensystem werden gebettete Stäbe
feiner geteilt, im vollen Beispiel der Tests 75 statt 42 Unbekannte, und
drei Werte rücken in der letzten Stelle zur genauen Lösung hin (ein Lager
46.5 statt 46.6 kN, genau 46.549).

Warum so:

- N, M und V jedes Pfahlelements kommen aus `ebener_verlauf`, genau mit
  Polynomen aus den Kräften an seinen Enden – dasselbe, womit das
  Balkensystem seine Stäbe auswertet. Dafür kennt `ebener_verlauf` jetzt
  eine Bettung, die vom Anfang zum Ende linear wächst, wie die Abminderung
  am Terrain. Weg sind die Beiwerte der kubischen Form in
  `_schnittkraefte`, N nach der Trapezregel und das Moment, das am
  eingespannten Kopf nachgeschoben wurde. Ein Test prüft, dass ein solches
  Stück am Ende genau die Kräfte und die Biegelinie seines Endes trifft.
- Eine Regel, wie fein ein gebetteter Stab geteilt wird, für beide
  (`stab.schritt`): Stücke höchstens 1/(5β). Das ist die bisherige des
  Pfahls; das Balkensystem teilte nach 1/(2β). Genau genug wären beide –
  die Lösung weicht bei 1/(2β) um 0.2 ‰ ab –, aber der Pfahl liest seine
  Nachweise an den Knoten ab: beim Mikropfahl des Beispiels wären die
  Elemente 8.5 statt 3.4 cm lang geworden, und zwei Nachweise wären um
  1 % günstiger ausgefallen, weil das grösste Moment zwischen den Knoten
  liegt. Die feinere Regel kostet das ganze Beispiel rund 15 % Rechenzeit.
  Wie viele Stücke ein Stab höchstens bekommt, folgt aus der Regel, damit
  der Hinweis auf eine zu steife Bettung wie bisher erst ab β·L = 32 kommt.
- Damit der Pfahl nicht langsamer rechnet, wertet er jedes Element ab
  seinem oberen Ende aus, ohne die Polynome zu verschieben, und die
  Biegelinie aus den Enden ist direkt nach Potenzen geschrieben. Das
  Beispiel rechnet so schnell wie vorher.

## 2026-11-15 · Die Seite der Faser legt nur der Kern

Wo die gestrichelte Faser einer Linie liegt – und damit, wo ein positives
Moment zieht –, legt jetzt auch in der Ebene allein der Kern (Punkt 3b der
Strukturdurchsicht vom selben Tag). Am Bildschirm bleibt alles, wie es war:
die Faser rechts der Laufrichtung, eine neue Linie mit der Faser unten, eine
senkrechte mit ihr links, der Schalter «Zugseite» wie bisher – im Browser
nachgeprüft.

Warum so:

- Der Kern schickt je Linie ihre Achsen, eben wie im Raum (`stabachsen` in
  `web/balkendaten.py`), in den Koordinaten der Zeichnung. Die Oberfläche
  zeichnet die Faser und die Lasten quer danach und nennt die Zugseite
  danach, wohin z zeigt. Bisher rechnete sie die Achsen der Ebene selbst
  aus, nach einer zweiten Regel, die mit der des Kerns übereinstimmen
  musste – sonst stand die Faser am Bildschirm auf der falschen Seite, und
  jedes Moment hätte falsch herum gelesen.
- Wohin eine neue Linie läuft, ist eine Angabe des Systems
  (`LAUFRICHTUNGEN`): in der Ebene nach rechts, steht sie senkrecht, nach
  unten; im Raum keine, sie läuft, wie sie gezeichnet ist. Ein Test prüft
  mit den Achsen des Kerns, dass die Faser dann unten bzw. links liegt;
  ändert sich eines von beiden, schlägt er an.
- Bis die Antwort des Kerns da ist, fehlen einer neuen Linie die Faser und
  die Lasten quer – wie im Raum schon. Die Antwort kommt mit jeder
  Änderung.

## 2026-11-15 · Grenzwerte und grösste Verschiebung aus dem Kern

Drei Ergebnisse suchte der Bildschirm der Balkensysteme bisher selbst: die
Grenzwerte über alle Stäbe in der Zusammenfassung, die massgebende
Durchbiegung je Stab im Verschiebungsbild und die grösste Verschiebung, auf
die dieses Bild überhöht. Jetzt liefert sie der Kern, je Fall (Punkt 3a der
Strukturdurchsicht vom selben Tag). Am Bildschirm stehen dieselben Zahlen,
nachgeprüft am Rahmen der Beispiele.

Warum so:

- «Massgebend» heisst an genau einer Stelle, was es heisst (`nach_betrag`
  in `stabwerk/verlauf.py`): der grösste Betrag, bei gleichem der positive
  Wert. Die Tabelle am Bildschirm nahm bei gleichem Betrag schon den
  positiven, der Bericht den zuerst gefundenen, oft den negativen. Jetzt
  nennen beide denselben; in den Beispielen ändert das keinen Satz.
- Über alle Stäbe fasst `grenzwerte` zusammen, mit Stab und Stelle; bei
  gleichem Wert gilt der erste Stab, wie vorher am Bildschirm.
- Die grösste Verschiebung kam aus den Proben des Bilds und lag knapp
  daneben, wenn sie zwischen zwei Proben fiel. Ihr Quadrat u² + v² + w² ist
  je Stück ein Polynom; sein grösster Wert steht dort, wo die Ableitung null
  wird, oder an einer Grenze – gesucht wie jeder andere Extremwert
  (`Stabverlauf.groesste_verschiebung`).

## 2026-11-15 · Ein Rechenkern für Ebene und Raum

Die 2D- und die 3D-Balkensysteme rechnen mit demselben Kern (Punkt 1 der
Strukturdurchsicht vom selben Tag). Am Bildschirm und im Bericht bleibt
alles gleich: dieselben Zahlen, nachgeprüft an jedem Balkensystem der
Beispiele, alt gegen neu. Nur wo die Durchbiegung eines Stabs überall null
ist, steht ihr Extremwert an einer anderen Stelle x – bei null ist jede
gleich richtig (TODO, Punkt 10).

Warum so:

- Ein ebenes System rechnet der Kern als System im Raum, das in seiner
  x-z-Ebene liegt. Was die Ebene anders macht, steht einmal, in ihrer Art
  (`stabwerk/art.py`): Ein Ort verschiebt sich nur in x und z und dreht
  sich nur um −y; ein Stab biegt sich nur in seiner x-z-Ebene, trägt keine
  Torsion und braucht nur EA und EI. Was aus der Ebene hinausführte, wird
  gar nicht erst eine Unbekannte. Darum bleiben Unbekannte, Gesamtmatrix,
  Lastvektor und Lösung der Ebene die alten, und die Herleitung zeigt
  weiter die Matrix 6 × 6 eines ebenen Stabs (`eben_matrix`).
- Die Achsen eines ebenen Stabs: y ist −y des Systems, z = x × y zeigt zur
  gestrichelten Faser (`achsen_eben` in `stabwerk3d/stab.py`). So sind N,
  V_z und M_y genau N, V und M von Hand, und die Drehung um y ist die im
  Gegenuhrzeigersinn. Bildschirm und Bericht der Ebene heissen weiter N, V,
  M, w und φ; welches Feld des Verlaufs dahinter steht, sagt eine Stelle
  (`IN_DER_EBENE` in `stabwerk/verlauf.py`).
- Kräfte und Gleichgewicht rechnet der Kern im Raum und gibt sie in den
  Achsen der Art ab: eben (u_x, u_z, φ) und (R_x, R_z, M), im Raum je sechs.
- Ein ebener Teil des Verlaufs nimmt EA nur, wo er sich dehnt, und EI nur,
  wo er sich biegt: der ebene Stab hat EI_z und GI_T null. Vorher standen
  dort Platzhalter 1.0.
- Welche Darstellung der Bildschirm nimmt, sagt die Art der Rechnung, nicht
  mehr die Klasse des Befunds; die Lage eines Stabs im Bild steht einmal.
- Weggefallen, rund 830 Zeilen: der ebene Kern und sein `Stabverlauf`,
  `stabwerk3d/system.py` und `stabwerk3d/verlauf.py`, der Befund des Raums,
  drei der fünf Weichen in `rechnung.py` (geblieben sind das Eigengewicht
  und die Herleitung), `_lage_eben`, `Lastrichtung.vektor`, `drehung` und
  `transponiert_mal`.

## 2026-11-15 · 3D-Balkensysteme: die App

Neben den 2D-Balkensystemen gibt es die App «3D Balkensysteme» (Benutzer,
2026-11-15): dieselbe Eingabe und dieselben Ergebnisse für einen Rahmen im
Raum. Gezeichnet wird schräg von oben oder in den Ansichten x-y, x-z und
y-z; die rechte Maustaste dreht, ein Klick trifft die Arbeitsebene, und die
Taste E legt sie durch den Punkt unter dem Zeiger. Die Diagramme zeigen N,
V_y, V_z, T, M_y, M_z, die Verschiebung und die Lagerkräfte, je aus einer
Ansicht, die ein Schalter über dem Diagramm wählt.

Warum so:

- Eine Oberfläche für beide Arten. `balkensystem.js`, `bs_diagramme.js`,
  `bs_zeichnung.js` und das schwebende Fenster lesen aus dem Katalog ihrer
  Art, was sie hat (`systemkatalog(art, …)` in `bs_teile.js`, im Kern
  `web/systemkatalog.py`): Achsen, Richtungen, Lager, Kennwerte, die Grössen
  der Ergebnisse. Beide Kataloge haben dieselben Schlüssel; ein Test liest
  jeden festen Pfad aus dem Quelltext und schlägt ihn in beiden nach. Was
  sich nur in Worten unterscheidet – die Hilfe, das Bild der Vorzeichen –,
  steht in `bs_texte.js`.
- Was nur der Raum braucht, steht in `cad_raum.js`: die vier Ansichten, das
  Drehen um die Mitte der Zeichnung, die Arbeitsebene und ihr Raster.
  `cad_fenster.js` ruft es an wenigen Stellen; in der Ebene ist `a.raum`
  leer, und alles bleibt, wie es war. Gedreht wird mit der rechten
  Maustaste, weil die linke wählt und zeichnet und die mittlere schiebt.
- Wie eine Richtung im Bild erscheint, entscheidet eine Stelle (`imBild`,
  `kraft`, `moment` in `bs_symbole.js`), für die Zeichnung wie für die
  Diagramme: eine Kraft, die man fast von vorne sieht, wird ein Kreis mit
  Punkt oder Kreuz, ein Moment ein Pfeil mit zwei Spitzen oder, von vorne,
  ein Bogen.
- Ein Verlauf liegt in der Ebene aus dem Stab und der Achse, die der
  Katalog nennt – M_y und V_z zu z, M_z und V_y zu y – und erscheint
  verkürzt wie sie; N und T stehen zu der Achse, die man länger sieht. Die
  Ansicht eines Diagramms ist Darstellung und wird nicht gespeichert.
- Zahlen weichen einander aus (`freistellen` in `bs_diagramme.js`): eine,
  die eine frühere deckt, rückt in halben Zeilen weiter. Im Raum enden an
  einer Ecke oft drei Stäbe, und f_y und f_z eines Stabs liegen nahe
  beieinander. Das gilt auch in der Ebene, wo vorher an einer Ecke zwei
  Zahlen übereinander standen.
- Die Schalter der Ansicht, der Ebene und der Diagramme schreiben ihre
  Stellungen, wie sie heissen: in Grossbuchstaben würde aus M_y ein M_Y.
  Darum stehen auch in der Ebene die Grössen der Statik-Analyse jetzt
  gemischt («Verschiebung» statt «VERSCHIEBUNG»), in den Decken ebenso.

## 2026-11-15 · Zeichenfenster: im Bild treffen, mit jeder Zahl von Achsen

Vorbereitung für das 3D-Balkensystem; in den bestehenden Apps ändert sich
nichts. Ein Knoten hat so viele Koordinaten, wie die App Achsen nennt, und
alles im Zeichenfenster rechnet mit allen: Verschieben, Kopieren,
Zusammenführen, Teilen, die Punkteingabe mit einem Feld und einer Taste je
Achse. Die Ansicht kann die Zeichnung über zwei Richtungen ins Bild legen
und einen Klick auf eine Arbeitsebene zurückführen.

Warum so:

- Treffen, Fangen und Wählen rechnen im Bild, in Bildpunkten, nicht mehr in
  der Zeichnung. Im Raum gibt es nur so eine Antwort auf «was liegt unter
  dem Zeiger»: was man dort sieht, vorne wie hinten. In der Ebene ist es
  dasselbe wie vorher – das Bild ist die Zeichnung, nur vergrössert und
  verschoben, und wie weit ein Punkt entlang einer Strecke liegt, ist in
  beiden gleich.
- Zwei Strecken schneiden sich im Raum nur, wo sie sich wirklich treffen
  (`kreuzung`); meist gehen sie aneinander vorbei. Im Bild gekreuzte Stäbe
  bieten darum keinen Schnittpunkt zum Fangen an.
- `cad_fenster.js` hatte 1137 Zeilen; mit dem Raum wäre es weiter
  gewachsen. Ändern und Rückgängig stehen jetzt in `cad_verlauf.js`, der
  Inhalt des schwebenden Fensters samt seinen Zeilen (`cadZeile`,
  `schalterzeile`) in `cad_palette.js`, das Hervorheben der Auswahl in
  `cad_auswahl.js`.

## 2026-11-15 · 3D-Balkensysteme: Beschreibung, Aufbau und Rechnung

Ein 3D-Balkensystem lässt sich im Projekt beschreiben und rechnen, mit
seiner Herleitung im Bericht – noch ohne Oberfläche und noch nicht in der
Liste der Bauteile. Es hat Knoten mit x, y und z, Linien mit einem
Drehwinkel β, Lager in sechs Richtungen, Linienlager quer in y und z und
längs, Lasten in jede Richtung des Systems oder des Stabs und Querschnitte
nach Vorlage, als Stahlprofil oder mit A, I_y, I_z und I_T von Hand. Ein
ebener Rahmen gibt darin dieselben Momente, Querkräfte und Durchbiegungen
wie im 2D-Balkensystem. Dort ändert sich nichts; sein Bericht ist Zeichen
für Zeichen derselbe.

Warum so:

- Beide Balkensysteme teilen, was gleich ist: zeichnen, teilen und
  umkehren ohne Oberfläche (`projekt/staebe.py`), das Übersetzen in das
  Stabwerk (`Uebersetzung` in `projekt/aufbau/balkensystem.py`) und die
  Rechnung mit Steifigkeiten und Eigengewicht (`Stabwerksrechnung` in
  `stabwerk/rechnung.py`). Was der Raum anders macht, steht in je einer
  kleinen Datei daneben: drei Koordinaten, sechs Lagerrichtungen, EI_y,
  EI_z und GI_T statt EI, der Drehwinkel.
- Welche Steifigkeiten ein Stab bekommt, sagt eine Liste je System: EA und
  EI in der Ebene, EA, EI_y, EI_z und GI_T im Raum. Jede schreibt ihre
  Formel in die Herleitung, die Torsionssteifigkeit mit G. Die Namen
  stimmen mit den Feldern des Rechenkerns überein; so braucht es keine
  Übersetzungstabelle, die man nachführen müsste.
- Kehrt man eine Linie im Raum um, bleiben ihre Lasten, wo sie sind:
  Lasten quer in y und längs wechseln das Vorzeichen, weil die Achsen des
  Stabs mitdrehen, und der Drehwinkel β wird −β, bei einem lotrechten Stab
  180° − β. So liegt der Querschnitt danach gleich im Raum.
- Die Bauteilart kommt erst mit der Oberfläche in die Liste: Die Seite
  liest die Liste beim Laden und verlangte sonst eine App, die es noch
  nicht gibt. Bis dahin prüfen die Tests das System mit einer eigenen
  Bauteilart (`tests/test_balkensystem3d.py`).
- Die Formelsammlung verweist über den Namen auf die Funktion einer
  Formel. Die Hilfsfunktionen der Steifigkeit heissen darum
  `_modul_mal_kennwert` und `_gewicht_je_meter`: gleichnamige Methoden
  verdeckten sie.

## 2026-11-15 · Material: Schubmodul des Betons

Ein Beton hat jetzt die Querdehnungszahl ν_c = 0.20 (SIA 262:2025,
3.1.2.3.5) und daraus den Schubmodul G_cm = E_cm / (2 · (1 + ν_c)) =
E_cm / 2.4, beim C30/37 also 14 008 N/mm². Das Stabwerk im Raum braucht ihn
für die Torsionssteifigkeit der Betonstäbe; der Baustahl hatte G_a schon.

Warum so:

- Den Schubmodul nennt die Norm nicht, nur die Querdehnungszahl für den
  elastischen Bereich. G folgt daraus, wenn der Beton sich in alle
  Richtungen gleich verhält – die übliche Annahme.
- Beide stehen beim Beton, wie E_cm: so lässt sich ν_c bei einem eigenen
  Beton überschreiben, und jedes Bauteil liest denselben Wert.

## 2026-11-15 · Stabquerschnitte: I_z und I_T für jede Vorlage

Jede Vorlage eines Stabquerschnitts rechnet jetzt auch das
Trägheitsmoment um die senkrechte Achse (I_z) und das
Torsionsträgheitsmoment (I_T), wie die Stahlprofile schon. Das Stabwerk im
Raum braucht beide. Ein Rechteck 300 × 600 hat I_y = 5400·10⁶ mm⁴,
I_z = 1350·10⁶ mm⁴ und I_T = 3708·10⁶ mm⁴. Im 2D-Balkensystem ändert sich
keine Zahl, nur ein Zeichen: Was bisher «I = b·h³/12» hiess, heisst jetzt
«I_y = b·h³/12», mit dem Titel «Flächenträgheitsmoment um y».

Warum so:

- Mit I_z daneben wäre ein blosses «I» zweideutig. Die Stahlprofile hiessen
  schon I_y und I_z. Die Seiten in der Formelsammlung behalten ihren Namen,
  damit die Theorie dort stehen bleibt; neu dazu kommen die Seiten «… um z».
- Wie viel jeder Querschnitt dem Stab gibt, sagt jetzt das System: der
  ebene Rahmen fragt nach A und I, der räumliche nach A, I_y, I_z und I_T
  (`stabwerk/stabquerschnitt.py`). Gerechnet wird nur, was gefragt ist.
- I_T ist nach Vorgabe (TODO). Rechteck, T und Doppel-T zerfallen in
  Rechtecke mit der Näherung von Roark, die beim Rechteck die Tafel von
  Timoshenko auf ein Prozent trifft. Die kürzere und die längere Seite
  stehen als eigene Zeile in der Herleitung, mit min und max: so stimmt die
  Formel auch für ein liegendes Rechteck.
- Rechteckrohr und RRK rechnen I_T mit derselben Formel, nach Bredt, nur
  mit anderem p_m und A_m. Das Rundrohr (ROR) ist ein Kreisring und nimmt
  dessen Formeln, in cm⁴; die Seite «Flächenträgheitsmoment eines Rundrohrs
  um z» heisst darum jetzt «… eines Kreisrings um z».

## 2026-11-15 · 3D-Balkensysteme: der Rechenkern

Ein Stabwerk im Raum lässt sich rechnen, noch ohne Oberfläche: Knoten mit
x, y und z, Stäbe mit EA, EI_y, EI_z, GI_T und einem Drehwinkel, Lager
und Federn in allen sechs Richtungen, Gelenke, Bettung und feste
Linienlager quer in y und z und längs. Heraus kommen N, V_y, V_z, T, M_y
und M_z längs jedes Stabs, die Biegelinie und die Lagerkräfte. Ein Kragarm
um die Ecke, 3 m in x und 2 m in y mit 20 kN am Ende, senkt sich um die
Biegung beider Arme und um die Verdrillung des ersten: Mit EI = 50 000 kNm²
und GI_T = 10 000 kNm² sind es 28.67 mm, davon 24.00 mm aus der Torsion.

Warum so:

- Ein gerader Stab im Raum besteht aus drei ebenen Stäben, die nichts
  voneinander wissen: Biegung in x-z samt Längskraft, Biegung in x-y und
  Torsion – die verhält sich wie die Längskraft, mit GI_T statt EA.
  Steifigkeit, Lasten, Bettung und Verlauf kommen darum aus dem ebenen
  Rechenkern (`stabwerk3d/stab.py`); dafür ist der Verlauf eines ebenen
  Stücks dort als eigene Funktion herausgelöst (`ebener_verlauf`). Ein
  ebener Rahmen, im Raum gerechnet, gibt auf 10⁻⁸ die Zahlen des
  2D-Balkensystems (`tests/test_stabwerk3d_system.py`).
- Die z-Achse eines Stabs zeigt nach unten, gleich in welche Richtung er
  läuft. So hat ein Feldmoment unter Schwerelast immer das gleiche
  Vorzeichen. Im 2D-Balkensystem hängt die gestrichelte Faser an der
  Richtung: Bei einem Stab nach links liegt sie oben.
- Ein Gelenk löst alle drei Momente (TODO): Sonst wäre ein Fachwerk aus
  Gelenkstäben beweglich, seine Knoten drehten sich ohne Widerstand. Wo
  ein Knoten um eine Achse keine Steifigkeit hat, ist seine Drehung
  gestrichen, wie in der Ebene, erkannt an der Verbindung.
- Was die Torsion allein nicht hält, ist ein Mechanismus und wird
  gemeldet: Ein Balken auf zwei Gelenklagern dreht sich ohne Gabel um
  seine Achse. Die Meldung sagt dann, dass sich nichts verschiebt.
- Die Geometrie im Raum hat eine eigene Datei (`stabwerk3d/raum.py`).
  Damit bleibt die Rechnung unter 1000 Zeilen.
- In der Ebene ist die Kombination jetzt eine Funktion (`kombiniert`), die
  beide Rechenkerne brauchen, ebenso der Bereich einer Last
  (`lastbereich`).

## 2026-11-15 · Balkensysteme: Stahlprofile aus der Tabelle

Ein Querschnitt kann ein Stahlprofil sein: im Fenster «Querschnitt» die Art
«Profil», dann die Reihe – IPE, HEA, HEB, HEM, UPE, UNP, RRK oder ROR –,
die Grösse aus der Liste und die Achse. Ein HEB 300 um y hat
A = 149.08 cm² und I = 25 165.66 cm⁴; vorher brauchte es dafür ein
Doppel-T ohne Ausrundungen (I = 24 187 cm⁴, 4 % zu wenig) oder Kennwerte
von Hand. Es sind alle 666 Profile der Tabelle des Benutzers, mit ihren
Massen.

Warum so:

- Je Form eine Vorlage mit Formeln (`stabwerk/profilformen.py`), je Grösse
  nur die Masse (`stabwerk/profiltabelle.py`): parametrisch, wie der
  Benutzer es wollte, und jede Zahl im Bericht hergeleitet. Die Formeln
  sind die seiner Tabelle; gegen sie prüft ein Test jedes Profil, I, UPE
  und ROR auf alle Stellen, RRK auf 2·10⁻⁵ (dort rundet das Werkzeug die
  Beiwerte der Zwickel).
- Das UNP hat in der Tabelle keine Formeln. Gerechnet wird es mit
  geneigten Flanschen als Trapezen; Neigung und Stelle von t_f sind so
  gewählt, dass die Werte der Tabelle auf 1.4 % getroffen werden (TODO).
- Jede Form rechnet A, I_y, I_z und I_T, das räumliche Balkensystem
  braucht sie alle. Das ebene nimmt I_y oder I_z, je nach Achse; weil das
  Rechenwerk nur rechnet, was ein Ziel braucht, steht von den anderen
  nichts im Bericht.
- A in cm², I in cm⁴, wie in jeder Stahlbautabelle – so lässt sich
  vergleichen. Die Masse bleiben in mm.
- Ein unbekannter Profilname ist ein Fehler des Projekts wie eine
  fehlende Platte, kein Wahlfeld: dessen Meldung zählte alle 666 auf.

## 2026-11-15 · Balkensysteme: Stäbe aus Baustahl

Ein Material der Stäbe kann neben einem Beton auch ein Baustahl des Projekts
sein: in der Tabelle der Materialien steht dazu «+ Baustahl». Ein Stab aus
ihm nimmt E_a und für das Eigengewicht ρ_a. Ein HEB 300 aus S355 wiegt so
7850 · 10 · 0.0149 = 1.17 kN/m; vorher brauchte es dafür ein eigenes
Material mit E und ρ von Hand. Im Prüfprojekt «Jeder Nachweis» sind die
Stahlstäbe von «Alles einmal» jetzt aus S355 statt aus einem eigenen
«Stahl» mit E = 200 000.

Warum so:

- Das Material zeigt mit `stoff` auf den Baustoff des Projekts, gleich
  welcher Art; vorher hiess das Feld `beton`. Ein alter Stand mit einem
  Balkensystem öffnet sich darum nicht mehr (Prototyp, Benutzer,
  2026-10-11) – die Seite bewahrt ihn auf.
- Welche Kennwerte ein Stab aus welchem Baustoff nimmt, steht an einer
  Stelle (`STABKENNWERTE` in `stabwerk/rechnung.py`); die Arten der Tabelle,
  die Decke und die Oberfläche lesen von dort.
- Die Art bleibt am Material (Beton, Baustahl, eigenes), nicht nur am
  Baustoff: so bietet die Auswahl nur Baustoffe dieser Art an, und ein
  Verweis auf die falsche Art meldet sich (««C30/37» ist kein Baustahl»).

## 2026-11-15 · Material: Baustahl nach SIA 263

Neben Beton und Betonstahl gibt es Baustahl (Benutzer, 2026-11-15): die
Sorten S235, S275, S355 und S460 nach SIA 263:2013, Tabelle 1, mit
Streckgrenze f_y, Fliessschubspannung τ_y und Zugfestigkeit f_u – je bis
40 mm Dicke und darüber bis 100 mm –, dazu E_a = 210 000, G_a = 81 000,
ν_a = 0.3 und ρ_a = 7850 (3.2.2.1), γ_M1 = 1.05 und γ_M2 = 1.25 (4.1.3)
und die Fliessdehnung ε_y = f_y/E_a. Eine Normsorte heisst wie die Sorte und
hat die Kennung st1, ein eigener Baustahl heisst ST1.

Warum so:

- Beide Spalten der Tabelle stehen als Kennwerte da (f_y und f_y^{t>40}):
  welche gilt, hängt an der Dicke des Blechs oder Profils, nicht am
  Material. Wer sie braucht, wählt sie dort.
- Die Wärmedehnzahl (3.2.2.2) fehlt: es gibt keine Temperatur als Einheit,
  und keine Rechnung braucht sie (TODO).
- Was das Werkzeug über eine Materialart weiss – Sorten, Kennwerte, wie ein
  Material entsteht, die Vorsilben b/s/st und BE/S/ST, worauf die Kennwerte
  stehen –, steht jetzt in einer Liste (`opencivil/material/arten.py`).
  Vorher war es an sieben Stellen von Hand als «beton» und «betonstahl»
  aufgezählt, in Python und im JS; die Oberfläche liest die Arten aus dem
  Katalog (`materialarten`).
- Die Fliessdehnung des Baustahls steht auf derselben Seite wie die des
  Betonstahls: es ist dieselbe Grösse, Fliessgrenze durch E-Modul.

## 2026-11-14 · Decken: ein Hinweis bei schiefen Platten

Trägt eine Platte schief zu x und y, steht im Bericht unter der
linearisierten Fliessbedingung ein Hinweis (Benutzer, 2026-11-14): ihre
Streifen geben Drillmomente, und die Bedingung gilt nur näherungsweise und
bei mässigen Drillmomenten (SIA 262:2025, 4.3.2.6); wo die Hauptmomente
deutlich schräg zur Bewehrung stehen, gehört das eigens in die Bemessung
(4.3.2.5). Im Beispiel «Jede Wahl» trägt P3 in 0° und 71.6°.

Warum so:

- Die Bedingung (34) nimmt eine Bewehrung in x und y an und lässt nur
  mässige Drillmomente zu. Ein schiefer Streifen hat aber in x und y ein
  Drillmoment, bei 45° halb so gross wie sein Moment – und mehr
  Biegewiderstand wird dann in beiden Richtungen verlangt.
- Der Hinweis steht einmal, bei der Bedingung selbst, nicht in jedem Fall:
  er hängt an den Richtungen der Platten, nicht an den Lasten.
- Schief heisst: eine Richtung der Platte ist weder x noch y
  (`Richtung.schief`). Zwei rechtwinklige Richtungen, gedreht gegen x,
  zählen auch – die Bewehrung, die (34) annimmt, liegt in x und y.

## 2026-11-14 · Decken: das Einspannmoment mit dem Vorzeichen der Platte

Das Moment eines eingespannten Linienlagers steht in Bild und Bericht jetzt
mit dem Vorzeichen der Platte: negativ, wo es oben zieht (Benutzer,
2026-11-14). Vorher stand nur sein Betrag da. Im Beispiel «Jede Wahl»
zeigt der eingespannte Rand L2 −24.8 kNm/m, L5 dagegen, der nur die Drehung
hält, +102.6 – dort hängt das Feld durch, und es zieht unten.

Warum so:

- Vorher zählte das Moment um die Achse des Lagers, rechtsdrehend um a → b.
  Sein Vorzeichen hing daran, wie herum jemand das Lager gezeichnet hatte,
  und sagte darum niemandem etwas. Das Vorzeichen der Platte hängt nur an
  der Seite, auf der die Platte liegt.
- Dafür gibt jeder Träger dem Lager sein Moment knapp vor und knapp nach
  ihm mit (`Wandkraft.vor`, `nach`), statt des Einspannmoments allein. Am
  Rand ist eines davon null, und das andere ist das Moment der Platte dort.
- Liegt Platte zu beiden Seiten – eine eingespannte Wand zwischen zwei
  Feldern –, hält das Lager nur den Unterschied ihrer Momente. Das
  Vorzeichen hat dann keine Seite von selbst; es gilt die Seite, die
  stärker zieht (`rechnung._gehalten`). Zwischen Feldern von 4 und 6 m
  zieht die Platte links mit −q · 4²/8 = −2 q an der Wand, rechts mit
  −q · 6²/8 = −4.5 q; die Wand hält −2.5 q, mit dem Vorzeichen der
  rechten Seite.
- Ein schiefer Träger gibt quer zum Lager cos² seines Winkels weiter, wie
  die Platte – das blieb.
- Ein Lager, das die Drehung nicht hält, bekommt kein Moment: dort stünde
  sonst Rauschen aus der Rechnung statt einer Null.

## 2026-11-14 · Decken: neu ohne GZG

Eine neue Decke bringt die Lastfälle des Balkensystems mit – Eigengewicht,
Auflast, Nutzlast –, aber nur noch die Kombination GZT (Benutzer,
2026-11-14). Vorher bekam sie auch die GZG mit je 1.0, und der Bericht
rechnete für sie Biegewiderstände.

Warum so:

- Die Streifenmethode ist eine Methode der Plastizitätstheorie und gilt für
  die Tragsicherheit (SIA 262:2025, 4.1.4.2.1); Schnittgrössen im Gebrauch
  rechnet man in der Regel elastisch, mit Mittelwerten (4.4.1.2). Eine GZG
  nach der Streifenmethode sähe aus wie ein Gebrauchsnachweis und wäre
  keiner. Wer sie trotzdem will, legt sie unter «Lastfälle» selbst an.
- Die Vorgabe ist geteilt: `standardfaelle` legt die Lastfälle und die GZT
  an, `gebrauchskombination` die GZG. Das Balkensystem nimmt beide, die
  Decke nur die erste – die Beiwerte stehen weiter an einer Stelle.
- Das Beispiel «Jede Wahl» ist angelegt wie eine neue Decke und hat darum
  auch keine GZG mehr.

## 2026-11-14 · Decken: Bericht mit Herleitung

Die Herleitung einer Decke geht jetzt bis zu den Ergebnissen. Nach den
Fällen stehen einmal die Ansätze – vom Streifen zur Platte, die Pressung
eines Flächenlagers, die linearisierte Fliessbedingung (SIA 262:2025,
4.3.2.6, (34)) und das Lastverteilelement –, dann je Lastfall und
Kombination: jeder Träger mit Breite, Länge, Last, Lagerkräften und seinem
kleinsten und grössten Moment samt Stelle; was jedes Lager trägt; die
grössten Schnittkräfte der Platte mit Ort; die Biegewiderstände, die sie
verlangen; und je Stütze und Einzellast, was ihr Lastverteilelement
zusätzlich braucht. Die vier Ansätze haben Formelseiten unter dem neuen
Thema [[Streifenmethode]]. Damit ist die App Decken fertig.

Warum so:

- Alles je Meter, auch die Träger: Last und Lagerkräfte in kN/m, Momente in
  kNm/m. So steht eine Zeile der Trägertabelle neben dem Bild, ohne dass
  jemand durch die Breite teilt.
- Gleiche Feldstreifen in einer Zeile: im Kolloquium 4 tragen alle 18 in x
  dasselbe, «x1 … x18». Zusammen kommen nur Nachbarn derselben Richtung mit
  denselben Zahlen, auch derselben Stelle des grössten Moments; ein Träger
  ohne Last fehlt und trennt seine Nachbarn. Von geteilten Streifen erst
  alle ersten Stücke, dann alle zweiten (`herleitung._reihe`): so steht
  x1.2 neben x2.2 statt hinter x1.1.
- Bei gleichen Werten an zwei Stellen gilt die vordere
  (`traeger.vorderste_extreme`): sonst entschied in einem symmetrischen
  Träger die Rundung, welche Stelle dasteht, und gleiche Nachbarn fanden
  sich nicht mehr.
- Die grössten Werte der Platte an denselben Stellen wie in den Bildern:
  Zellen und Proben stehen jetzt in `feld` (`zellen_von`, `proben`,
  `extrem`), Bild und Bericht holen sie dort – ebenso Spitze und grösstes
  Moment eines Linienlagers (`rechnung.spitzen`). Ein Wert, der als 0.0
  dasteht, hat keinen Ort: er liegt an vielen Stellen.
- Die Proben kosten mehr als die Rechnung selbst. Das Zeichenfenster fragt
  nach jeder Eingabe, braucht aber nur Zahlen und Bilder: was der Dienst
  nur dafür rechnet, rechnet ohne Herleitung (`dienst._bauteil_rechnen`),
  und die Herleitung der Decke fragt, ob jemand mitliest
  (`Protokoll.still`) – nichts von ihr geht in die Rechnung ein. Dazu
  sucht die Zerlegung die Feldstreifen einer Richtung nur noch einmal,
  nicht für jede Stelle neu. Im Kolloquium 4 braucht die Decke nach einer
  Eingabe so 19 ms; mit Bericht wären es 70 ms.

## 2026-11-14 · Decken: Ergebnisbilder samt Lagerkräften

Unter «Ergebnisse» legt man Bilder an, je Zeile ein Fall und eine Grösse:
m_x, m_y, m_xy, v_x, v_y, v_0 oder die Lager – wie die Diagramme des
Balkensystems. Die Schnittkräfte liegen in Farbe über dem Grundriss, positiv
rot, negativ blau; der grösste und der kleinste Wert stehen mit Punkt an
ihrer Stelle. Das Bild der Lager zeigt je Linienlager den Verlauf seiner
Kraft über die Länge, darunter je Lager die Summe F, die Spitze r_max und,
eingespannt, das grösste Moment. Die Zusammenfassung hat neu die Tabelle
«Lagerkräfte», je Lager und Fall. Eine neue Decke zeigt für GZT m_x, m_y,
v_0 und die Lager.

Warum so:

- Die Zellen der Bilder sind die Feldstreifen beider Richtungen, gekreuzt:
  so liegt jede in genau einem Streifen jeder Richtung, und der Wert an
  ihrem Schwerpunkt gilt für sie ganz. Breite Streifen werden quer geteilt,
  keine Zelle breiter als ein Vierundzwanzigstel der Decke
  (`feld.ZELLEN`). Mit 40 waren es im Kolloquium 4 3168 Zellen und
  330 kB je Antwort, mit 24 sind es 792 und 79 kB.
- Die grössten Werte nicht nur an den Schwerpunkten gesucht, sondern auch
  an den Enden jedes Trägerstücks, knapp innen, und wo seine Querkraft oder
  Last null wird (`feld.stellen`). Wo nur ein Streifen trägt, liegt das
  Extremum dort genau: im Kolloquium 4 m_x = −60.1 kNm/m über der mittleren
  Stütze, wie die Handrechnung von B-B – an den Schwerpunkten wären es
  −58.7 gewesen.
- Die Farben symmetrisch um null, so weit wie der grösste Betrag samt den
  Extremwerten: sonst endete die Legende bei −58.7, und daneben stand −60.1.
- Längs eines Linienlagers Stufen: jeder Streifen gibt seine Kraft
  gleichmässig über seine Breite ab, und wo zwei dasselbe Stück tragen,
  zählen beide (`rechnung.lagerverlauf`). Das Moment eines eingespannten
  Lagers um dessen Achse, damit sich Streifen verschiedener Richtung
  zusammenzählen lassen; sein Vorzeichen hängt dann an der Richtung, in der
  das Lager gezeichnet ist – darum steht nur der Betrag da (siehe [[TODO]]).
- Im Bild der Lager nur ihre Namen, die Zahlen in der Tabelle darunter: mit
  Zahlen neben jedem Lager deckten sich in «Jede Wahl» die Beschriftungen
  nahe beisammen liegender Lager, und am linken Rand liefen sie aus dem
  Bild. Spitze und grösstes Moment rechnet der Kern, nicht die Oberfläche –
  der Bericht braucht sie auch.
- Die Bilder eines Falls kommen mit einer eigenen Anfrage
  (`decke_ergebnis`), wie die Verläufe des Balkensystems: sie sind gross
  und nur gebraucht, wenn jemand hinsieht. Wie man nach ihnen fragt und
  die Antwort je Fall behält, steht jetzt einmal für beide
  (`web/js/fallantwort.js`), ebenso die Zeilen mit «+ Diagramm»
  (`diagrammzeilen` in `web/js/lastfaelle.js`).

## 2026-11-14 · Pfähle IV: innerer Widerstand quer

Je Kombination, die den Pfahl quer belastet, jetzt auch Moment und Querkraft
der Verläufe gegen den Querschnitt, in jeder Tiefe und beide mal η_i
(SIA 267:2013, 9.5.2.4.1, (50)). Neu beim Bohrpfahl die Ganghöhe der Wendel
s_w, vorgegeben 150 mm. In den Bildern von M und V steht der Widerstand
gestrichelt daneben, wie der Erdwiderstand neben p.

Warum so:

- Das Moment mit der Normalkraft in derselben Tiefe, nicht mit N_Ed am Kopf:
  längs des Pfahls nimmt N ab, und unter mässigem Druck trägt der
  Querschnitt mit weniger Normalkraft weniger Moment.
- M_Rd an sieben Normalkräften, dazwischen linear: jede Tiefe einzeln wäre
  ein Schnitt der Interaktion je Knoten, in Pyodide spürbar. M_R(N) ist
  konkav, die Gerade liegt also darunter; in den Proben weniger als 1 %
  (`tests/test_pfahl_innen_quer.py`).
- Im Bohrpfahl mindert die Längszugkraft aus der Querkraft (SIA 262:2025,
  4.3.3.4.11, (51)) die Normalkraft, mit der der Querschnitt biegt: am
  eingespannten Kopf ⌀ 900 mit N = 1000 kN und H = 100 kN von 742 auf
  699 kNm. Als Zug in der Achse statt je zur Hälfte an den Gurten: einfacher,
  und weil der Druckgurt weiter von der Achse liegt als der Zuggurt, auf der
  sicheren Seite.
- Die Querkraft im Bohrpfahl wie in einem Steg: das Fachwerk der Platte
  (`querschnitt/fachwerk.py`) mit der Wendel zu 70 % (4.3.3.4.4), d bis zum
  Schwerpunkt der gezogenen Hälfte der Stäbe, b_w als Sehne am Druckgurt.
  Im Beispiel trägt die Wendel ⌀ 10 alle 150 mm im ⌀ 900 rund ein Viertel
  dessen, was die Druckdiagonalen tragen.
- Unter Zug α ab 40°. Am Fuss eines Zugpfahls ist N null, dort gilt 30° –
  ein Zugpfahl zeigt darum beide Bereiche. Was dort als Millionstel Newton
  übrig bleibt, ist Rauschen und kein Zug (`innen_quer.RAUSCHEN`).
- Im Mikropfahl SIA 263:2013, soweit die Querkraft es braucht:
  V_Rd = A_v·f_yd/√3 (5.1.4.1, (41)), A_v = 2·A/π aus Ringen gleichen
  Schubflusses. f_yd bleibt der Wert nach SIA 262, wie längs.
- Die Ganghöhe ist die grösste längs des Pfahls; über 0.40 m ein Hinweis
  (SIA 267:2013, 9.6.3.2.4).

## 2026-11-14 · Pfähle III: äusserer Widerstand quer und Bettungskraft

Je Kombination mit H_Ed jetzt auch der Widerstand quer zur Achse, nach SIA
267:2013, 9.4.4.2.2 und 9.5.2.3: R_tr,k aus dem Erdwiderstand und dem
Biegewiderstand des Pfahls, R_tr,d = η_a,tr · R_tr,k / 1.4. Dazu in jeder
Kombination die Bettungskraft der Verläufe gegen den Erdwiderstand
(9.5.4.5). Die Karte «Querlast» trägt den Kopf, t_red und η_a,tr; im Bild
des Bettungsdrucks steht p_E,d / D gestrichelt daneben, die Legende der
Situation nennt R_tr,d je Kombination mit dem massgebenden Bruch.

Der Erdwiderstand nach dem Buch: Rankine drainiert und undrainiert
(Kap. 9.3.5, 9.3.6), vorne passiv weniger hinten aktiv, auf der dreifachen
Breite (Kap. 10.8).

Warum so:

- Mechanismen statt der Diagramme von Broms: die gelten für gleichförmigen
  oder linear wachsenden Boden. Mit Schichten und Grundwasser geht der
  Mechanismus über jedes Profil; je Lage Arbeit gleich Arbeit, die Lagen
  höchstens 1 cm auseinander, die Integrale je Stück genau. Geprüft gegen
  die geschlossenen Lösungen: gleichförmig √(2·M_R·c), 2·√(M_R·c) und
  (√2 − 1)·c·L, linear wachsend s³ = 3·M_R/a
  (`tests/test_pfahl_quer.py`).
- Die Linien des Erdwiderstands enden an Schichtgrenzen, am Wasserspiegel
  und wo e_a null wird: so ist p_E je Stück linear und das Integral genau.
  An einer Schichtgrenze gilt der kleinere Wert.
- Der Biegewiderstand charakteristisch, mit f_ck und f_yk, mal η_i: R_tr,k
  ist ein charakteristischer Wert, und der Pfahl ist im Boden nicht so
  sicher wie im Plan (9.5.2.4.4). M_R(N) ist konkav, weil der
  Interaktionsbereich konvex ist; zwischen Kopf und Fuss ist der kleinere
  der beiden Endwerte also der kleinste. Bei wenigen Stäben zählt die
  schwächere von zwei Lagen.
- Die Bettungskraft mit denselben Beiwerten wie R_tr, weil 9.5.4.5 keine
  nennt. η_a,tr / γ_M,a = 0.5 ist zugleich der Faktor 2, den das Buch auf
  dem passiven Druck verlangt, damit die Verformung klein bleibt.
- Nur ein Moment am Kopf gibt keinen Nachweis R_tr, aber den der
  Bettungskraft. Eingespannt zählt M_Ed weiterhin nicht.
- Der Erdwiderstand liest Schichten und Wasser aus demselben Profil wie der
  äussere Widerstand längs (`Pfahl.profil`).
- Der Mikropfahl mit Vollstab im Beispiel trägt quer nicht: M_R ≈ 2.6 kNm,
  und am Terrain drückt die Bettung stärker, als der Kies hält. Er bleibt
  so – ein Beispiel, das zeigt, wie ein Nachweis scheitert.
- Ohne Boden unter dem Fuss kein Widerstand quer; die Warnung sagt es jetzt.

## 2026-11-14 · Pfähle II: die Steifigkeit als gebetteter Stab

Der Pfahl steht jetzt auch als Stab auf Federn im Boden. Daraus zweierlei:

- Die Federn am Kopf, mit E_s,k: längs auf Druck und auf Zug, quer mit frei
  drehbarem Kopf, dazu die Steifigkeitsmatrix des eingespannten Kopfs
  (K_HH, K_HM, K_MM) für ein Modell des Tragwerks darüber. Sie hängen an
  keiner Kombination und stehen als Kennzahlen in der Zusammenfassung.
- Je Kombination die Verläufe über die Tiefe mit E_s,k/1.5: Normalkraft,
  Setzung, Verschiebung, Verdrehung, Moment, Querkraft und Bettungsdruck,
  als Bilder unter «Diagramme». Die Kombination hat dafür H_Ed und, am frei
  drehbaren Kopf, M_Ed.

Die Federn des Bodens: am Mantel 0.42·E_s und am Fuss 4.5·E_s nach Cassan
(Kap. 12.8), quer k_s = E_s/D (SIA 267:2013, 9.5.4.5, (53)), vom Terrain
bis t_red linear abgemindert. Jede Schicht hat dafür ihr E_s,k.

Warum so:

- Ein kleiner Löser für den Pfahl (`pfahl/bettung.py`) mit den Elementen
  des Stabwerks: Steifigkeit und Bettungsmatrix stehen nur in
  `stabwerk/stab.py`, gelöst wird mit dessen Profillöser. Das ganze
  Stabwerk wäre zu viel: es kennt Lastfälle, Lager und Teilstäbe, der Pfahl
  ist ein gerader Stab mit einer Last am Kopf.
- Die Bettungsmatrix des Stabwerks darf quer linear wachsen. Mit Stufen von
  gleicher Bettung zeigte der Bettungsdruck unter dem Kopf Sägezähne; so
  steht die Abminderung genau im Modell, und die Knoten richten sich nur
  nach den Schichtgrenzen und nach t_red.
- N, M und V aus dem Gleichgewicht der Bettungskräfte, für den Ansatz genau
  integriert, nicht aus der Krümmung eines Elements: eine Ordnung genauer,
  und am Fuss schliesst das Gleichgewicht auf Rundungsfehler.
- Die Federn am Kopf aus einer Probelast von 1 MN – das System ist linear.
  K_MM folgt ohne dritte Rechnung aus k_h = K_HH − K_HM²/K_MM.
- Geprüft gegen die geschlossenen Lösungen: längs Cassan, quer der lange
  Balken frei, mit Moment und eingespannt, je auf fünf Stellen
  (`tests/test_pfahl_steifigkeit.py`). Als Vergleich für die lineare
  Bettung dienen 100 Stufen zu 2 cm; 400 zu 5 mm machten das System schon
  so schlecht konditioniert, dass die Rundung 1e-4 erreichte.
- Das Moment am Kopf dreht wie H über dem Kopf (M_0 = H·e). So verrichten H
  an y und M_0 an θ Arbeit, und K_HM ist negativ.
- Am eingespannten Kopf zählt M_Ed nicht, das Moment dort ist Reaktion; die
  Oberfläche blendet das Feld aus, die Herleitung meldet ein eingegebenes.
- Ohne Boden unter dem Fuss keine Steifigkeit, nur eine Warnung.
- Nebenbei: die Achsen aller Diagramme schreiben ohne eigene Schrift so
  viele Nachkommastellen, wie ihr Schritt verlangt. Vorher stand bei 0.5
  eine 1 – etwa bei der Verdrehung in mrad.

## 2026-11-14 · Pfähle I: äusserer und innerer Widerstand

Eine neue App für den Einzelpfahl nach SIA 267:2013, Kapitel 9, gerechnet
nach Kapitel 12 des Buches von Lang, Huder, Amann und Puzrin: ein Bohrpfahl
aus Stahlbeton oder ein Mikropfahl mit Rohr oder Vollstab. Zwei Nachweise
längs der Achse, je Kombination auf Druck oder, bei negativem N_Ed, auf Zug:

- Äusserer Widerstand: Mantel und Fuss aus den Schichten – drainiert
  K·σ'_v·tan δ und (c'·N_c + σ'_v·N_q)·X, undrainiert α·s_u und s_u·N_c –
  oder R_a,k aus Versuchen. η_a richtet sich nach der Grundlage (0.7 bis
  1.0), γ_M,a ist 1.3 auf Druck und 1.6 auf Zug. Auf Zug trägt nur der
  Mantel.
- Innerer Widerstand: der Querschnitt nach SIA 262, ganz gedrückt oder ganz
  gezogen, mal η_i (0.8, mit Prüfung der Integrität 0.9). Beim Mikropfahl
  nur das Tragglied, um die Abrostung verkleinert.

Warum so:

- Die Stücke des Mantels enden an jeder Schichtgrenze und am Wasserspiegel.
  Darin verläuft σ'_v linear, der Wert in der Mitte ist also genau das
  Mittel. Das Buch nimmt die halbe Einbindetiefe – dasselbe, solange kein
  Wasser die Schicht teilt. Sein Beispiel 17.15 geht damit auf ein Prozent
  auf: 310 kN am Mantel, 4529 kN am Fuss (`tests/test_pfahl.py`).
- Der Querschnitt läuft durch dieselbe Interaktion wie die
  Querschnittsanalyse, nicht durch eine eigene Formel. So gilt dieselbe
  Grenze −ε_c1d, und der Stahl steht ganz gedrückt bei 400 statt 435 N/mm².
  Der Kreis ist ein 48-Eck mit derselben Fläche.
- Beide Nachweise teilen ihre Fälle (`pfahl/achse.py`): ob Druck oder Zug
  und gegen welchen Widerstand verglichen wird, steht an einer Stelle.
- Die Wahlen tragen ein Wort für den Knopf und eine Erklärung darüber, wie
  die Verschmierungen der Querschnittsanalyse.
- Das Beispielprojekt hat einen Bohrpfahl, das Prüfprojekt vier Pfähle:
  drainiert und undrainiert, aus dem Versuch, mit Rohr und Vollstab. Einer
  geht absichtlich nicht auf.
- Was weder Norm noch Buch sagen, steht als Annahme in der Herleitung und in
  [[TODO]].

## 2026-11-14 · Normprüfung VII: Durchstanzen

Geprüft gegen SIA 262:2025, 4.3.6 und 5.5.3. Was sich ändert:

- Die Anker rechnen mit ihrem eigenen Stahl B500B (4.3.6.5.4). Vorher mit dem
  der Platte: mit B700B f_yd 609 statt 435 N/mm², 40 % zu günstig.
- Liegt die Verankerung tiefer als d_v/6, tragen (68) und (70) 30 % weniger
  (5.5.3.11). Beispiel: h = 220 mm, d_v = 174 mm, c_v = 30 > 29 mm.
- k_e gilt je Schnitt (4.3.6.5.10 → 4.3.6.2.3): an einer Randstütze mit (57)
  aussen 0.746 statt 0.815 von innen.
- Der Randstreifen an der Eckstütze reicht nur bis zum zweiten Rand
  (Figur 25): 300 × 300 in der Ecke 600 statt 900 mm.
- Stufe 3 an Rand- und Eckstützen: r_s ≥ 2/3·b_sr (4.3.6.4.8).
- Leisten beim zweiten Anker höchstens 1.5·d_v auseinander (5.5.3.9), um den
  Stahlpilz also dichter.
- Ein Hinweis, wo das Produkt Tabelle 21 überschreitet; die Grenze selbst ist
  offen ([[TODO]]).
- Das Prüfprojekt hat eine Eckstütze in Stufe 2 und eine Randstütze in
  Stufe 3, damit die drei neuen Formeln im Notizbuch stehen.
- Bestätigt und aus der [[TODO]]: an Wandende und Wandecke rechnet Stufe 2
  wie Stufe 1 – 4.3.6.4.7 nennt für Wände keine Momente, und m_sd/m_Rd = 1
  liegt sicher. Ebenso die Normstellen, die noch fehlten: übrig sind 85 von
  227 Formeln, Geometrie und Mechanik ohne Normbezug und zwei Festlegungen,
  deren Entscheid offen steht (Rissbeginn, Raumlast unter Auftrieb).

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

## 2026-11-14 · Normprüfung VI: Grundbruch, Gleiten und Setzung

Sechster Bereich, an den Seiten bestätigt: SIA 267:2013, S. 30, 35–36,
53–57; Lang, Huder, Amann, Puzrin, *Bodenmechanik und Grundbau*, 8. Aufl.
2007, Kap. 1.4, 3.7, 5.3, 8.3–8.12, 9.2.5–9.2.18 und Anhang, Tabelle A1.

- **Gleiten nach SIA 267** (8.4.1.1, 8.5.2.2): δ_k = min(k_δ · φ_k; 35°),
  dann tan δ_d = tan δ_k / γ_φ. Vorher δ* = k_δ · φ_eff, ohne Grenze –
  das Buch nennt keine, die Norm schon. φ_k = 40°, γ_φ = 1.2,
  N_Ed = 1000 kN: T_Rd vorher 699 kN, jetzt 584 kN. Mit k_δ = ⅔ und
  φ_k = 30° lag es 1.6 % zu hoch, mit k_δ = 1 und φ_k ≤ 35° bleibt alles
  gleich. Der Feldtitel nennt die Regel der Norm statt «meist ⅔ bis 1».
- **Gleiten undrainiert** (8.5.2.2, (32)): T_Rd = b · L · c_eff statt
  null. b = L = 2 m, s_u = 30 kPa, γ_cu = 1.5: 80 kN; vorher war jede
  Kombination mit T > 0 «nicht erfüllt». Der Satz, nach dem Buch zähle
  keine Haftung, stand dort nicht.
- **γ_R = 1.0 steht im Bericht** (8.5.2.1, (29), (30)); vorher fehlte er
  ganz. Ob ein Feld dazukommt, entscheidet der Benutzer.
- **Der Einflussfaktor J ist nachgeschlagen:** die Eckformel steht im
  Anhang des Buches zu Tabelle A1, die Überlagerung in Kap. 3.7, Bild 3.15.
  Die Rechnung trifft die Tabellen A1 und A2; «nicht nachgeschlagen» ist
  fort.
- **Verweise:** N_Rd Kap. 9.2.11 und SIA 267:2013, 8.5.3.5; s = s_W + s_E
  Kap. 8.2, 8.5; der Punkt K Kap. 8.10, Bild 8.15; c_eff 5.3.2.1, (5); γ_c
  und γ Tabelle 1; t₁ 4.2.2.3; q_Ed Kap. 9.2.5; k_δ 8.4.1.1; s_zul 8.5.4.1;
  Δz_max Kap. 8.3; q_W, q_E Kap. 8.5; M_E Kap. 5.3, 8.5 und 5.3.2.8 (im
  Gebrauch ohne Partialfaktor). Der Titel des Buches steht im Code.
- **Hinweise:** die Auflast zählt nur dauernd und beidseitig über L_Gl
  (Kap. 9.2.5); c' neben φ' nur bei dauerhafter Wirkung, feinkörnige Böden
  kurz- und langfristig (8.5.1.5, 8.5.1.6); günstiges Eigengewicht mit
  γ_G,inf = 1.0 (8.5.2.4); bei Ausmitte die wirksamen Masse eingeben; der
  Boden einheitlich bis H_Gl (Kap. 9.2.10; 8.4.4.1); γ' aus der feuchten
  Raumlast liegt sicher.
- **Formelseiten:** «die Summe liegt auf der sicheren Seite» bei der
  erweiterten Tragfähigkeitsformel stand nicht im Buch – es nennt sie eine
  Näherung (9.2.9). Der Satz von Caquot ist als Herleitung ausserhalb des
  Buches gekennzeichnet.
- **Offen für den Benutzer** ([[TODO]]): ein Feld γ_R; ein Feld γ_g für
  den Boden unter Wasser; φ_k über 45°; die Startwerte der Setzung, vor
  allem M'_E = 3 · M_E statt 8 bis 10 · M_E.

## 2026-11-14 · Normprüfung V: Decke und Balkensystem

Fünfter Bereich, an den Normseiten bestätigt (SIA 262:2025, S. 43–45, 54,
66, 78; SIA 260:2013, S. 17 und 33; SIA 261:2020, S. 37).

- **Die Durchbiegung im Balkensystem sagt, was sie ist.** Jeder Stab misst
  w gegen die Gerade zwischen seinen Enden; die Norm misst gegenüber den
  Auflagern (4.4.3.1.1), beim Kragarm über die doppelte Länge. Das ist
  dasselbe nur, wo ein Stab von Lager zu Lager reicht. Einfeldträger 6 m,
  EI = 22 693 kNm², q = 10 kN/m: gegenüber den Auflagern 7.44 mm; mit einem
  Knoten in Feldmitte zeigte der Bericht 1.60 mm und L/w = 1875 statt 807.
  Kragarm 2 m: 0.14 statt 0.88 mm. Der Bericht sagt das jetzt, und L/w ist
  fort – es sah aus wie ein Nachweis. Dazu: w gilt kurzzeitig und
  ungerissen, die untere Grenze (4.4.3.2.2).
- **Die Annahmen des Balkensystems mit Ziffern:** E_eq ist eine
  Sekantensteifigkeit (4.1.4.1.2), gerechnet wird ungerissen wie in der
  Regel vorgesehen (4.1.4.1.3), aber ohne Bewehrung; Theorie 1. Ordnung,
  solange die Wirkungen 2. Ordnung klein bleiben (4.1.3.2.2), schlanke
  Druckglieder nach 4.3.7, eine Schiefstellung nach (17) als waagrechte
  Last. Vorher stand dort «nach Vorgabe, nicht nachgeschlagen».
- **Die Annahmen der Decke mit Ziffern:** die Streifenmethode ist eine
  Lösung nach der statischen Methode, ein unterer Grenzwert für die
  Tragsicherheit (4.1.4.2.1, 4.1.4.2.2), und nur, wenn das
  Verformungsvermögen gesichert ist (4.1.4.2.4). Jede Aufteilung im
  Gleichgewicht ist zulässig; die automatische bleibt eine Vorgabe. Die
  Fliessbedingung der Platte ist (34) der Norm, eine Näherung für
  Bewehrung in x und y (4.3.2.5, 4.3.2.6). Eine Punktlast stellt
  SIA 261:2020, Tabelle 8 selbst auf 50 × 50 mm.
- **Hilfetexte und Formelseiten** nennen dieselben Grenzen: E_eq für EA
  ist eine Näherung, schiefe Streifen geben in x, y ein m_xy, b_eff hängt
  vom Abstand der Momentennullpunkte ab und ist über Stützen schmaler.
- **Offen für den Benutzer** ([[TODO]]): die Durchbiegung je Feld; die
  Gebrauchskombination der Decke; γ_G,inf = 0.80 für günstige ständige
  Last; die Vorgaben der Decke; die Dichten aus SIA 261.

## 2026-11-14 · Normprüfung IV: Gebrauchstauglichkeit

Vierter Bereich, an den Normseiten bestätigt (SIA 262:2025, S. 45, 51, 53,
75–78; SIA 260:2013, Tabellen 1 bis 3).

- **Massige Bauteile im gezeichneten Querschnitt** (4.4.2.3.7): mit dem
  Schalter «500 mm» zählt bei der Zwängung auf Normalkraft nur der Beton
  bis 250 mm vom Rand, und k_t gilt für 500 mm. Vorher begrenzte der
  Schalter nur t, und das machte den Nachweis strenger statt milder. Wand
  1000 × 2000 mm, C30/37: ohne Schalter N_Riss = 3867 kN, mit Schalter
  vorher 4640 kN, jetzt 2900 kN (1.25 m² Randzone · 0.8 · 2.9 N/mm²). Unter
  zentrischem Zug sind alle Ränder gezogen, auch die einer Aussparung; wo
  zwei Betone aneinanderstossen, ist kein Rand. Die Fläche rechnet ein
  eigenes Modul (`querschnitt/randzone.py`) auf waagrechten Linien: bei
  Rechtecken genau, an einer einspringenden Ecke unter einem Promille
  daneben.
- **ρ′ mit dem d der gezogenen Seite** (4.4.3.2.5): beide Gehalte beziehen
  sich auf die statische Höhe des Bauteils. Vorher nahm ρ′ das d der
  Gegenseite. Im Beispiel wird ω_w′ = 7.55 statt 7.52. Ab ρ′ = 5 % gäbe
  (104) einen negativen Faktor; dort steht jetzt «kein Nachweis».
- **Die Zwängung heisst nach dem, was sie rechnet.** «Sprödes Versagen
  unter Zwängung» war die Begrenzung der Rissbreite bei Zwang (Tabelle 17,
  Zeile 2) und heisst jetzt «Zwängung auf Normalkraft». Sprödes Versagen
  ist 4.3.1.2 und rechnet mit dem Widerstand.
- **Ziffern:** σ_s,adm 4.4.2.3.4, (102) mit Tabelle 17 statt 4.4.2, bei
  normaler Anforderung Tabelle 17; die Risskräfte und das aufnehmbare
  Moment Tabelle 17; das Rissmoment 4.3.1.2 beim spröden Versagen, Tabelle
  17 bei der Zwängung; die rissaktive Dicke 4.4.2.3.7; ω_w und die Gehalte
  (104); die Kriechzahl 3.1.2.6; die Wertigkeit 3.1.2.6.1, (12).
- **L/350 stammt aus SIA 260:2013, Anhang A, Tabelle 3** (häufige Last,
  Funktionstüchtigkeit und Komfort), und w mit E_cm heisst γ_cE = 1.0
  (4.2.1.16). Beides stand als Vorgabe da. Die Tabelle meint dort nur einen
  Teil der Durchbiegung; gehalten wird die ganze samt Kriechen, das liegt
  sicher, und der Bericht sagt es.
- **Texte:** Tabelle 17 nennt für das Fliessen ausdrücklich f_yd − 80 N/mm²,
  für B500 355 N/mm² – der Satz, die Norm lasse f_yd oder f_yk offen, ist
  fort. Die Spannungsrechnung begründet ihre Werte mit 4.4.1.2
  (Mittelwerte); f_ck statt f_cm liegt dort auf der sicheren Seite. Wo eine
  Rissbreite verlangt ist, sagt ein Hinweis, dass (102) nur für den
  Augenblick des Risses gilt (Tabelle 17, Fussnote 1).
- **Offen für den Benutzer** ([[TODO]]): k_t bei Steg, Flansch und
  Hohlkasten; drei Nachweise mit charakteristischen Werten; sprödes
  Versagen unter Zug; die Fussnote je Fall; der Rissbeginn der
  Spannung-Dehnung-Analyse; f_ctk0.95 nach (101); (103) oder (104) und die
  Normalkraft in der Durchbiegung; ein Schalter für L/500, L/350, L/300;
  die Anteile 60 und 70 %; Mittelwerte im Gebrauch; der dickste Stab und
  der fiktive Durchmesser; der äquivalente Modul.

## 2026-11-14 · Normprüfung III: Baustoffe

Dritter Bereich, an den Normseiten bestätigt (S. 21, 28–30, 34–35, 48–49,
80–81, 89).

- **f_cd mit η_t** (2.4.2.3, (2); 4.2.1.3): der Beiwert für die Dauer der
  Einwirkung steht jetzt als Kennwert in der Formel, Vorgabe 1.0. Keine Zahl
  ändert sich, aber der Bericht zeigt die Annahme. Mit η_t = 0.85 – wenn f_ck
  später als nach 28 Tagen bestimmt ist oder früh viel Last wirkt – hätte
  C30/37 17.0 statt 20.0 N/mm². Eine Normsorte bleibt bei 1.0; wer abweicht,
  legt ein eigenes Material an.
- **Die Sortentabellen sind geprüft:** die neun Betone stimmen mit Tabelle 3,
  B500A, B500B, B500C und B700B mit den Tabellen 5 und 9. Der Hinweis «vor
  dem produktiven Einsatz prüfen» ist fort. «Stahl II» steht in keiner
  Tabelle – offen für den Benutzer.
- **Ziffern:** f_ck und f_ctm 3.1.2.2.1 und 3.1.2.2.4 mit Tabelle 3 statt
  3.1.2.2.7, der Ziffer des Leichtbetons; η_fc 4.2.1.2, (26) statt 2.4.2.3;
  f_yk 3.2.2.2 und ε_uk 3.2.2.3, je mit Tabelle 5; die Fliessgrenze auf Druck
  4.2.2.2, Figur 16 – die Norm setzt sie gleich der auf Zug; A_s und der
  Bügelschenkel 4.2.2.4 statt 5.5.2; der Lagenaufbau ohne Verweis statt
  5.2.2, dafür die Überdeckung mit 5.2.2.1 und Tabelle 18; der wirksame
  Modul E_cm/(1+φ) mit 3.1.2.6.1, (12). Gleichungsnummern an f_cm, E_cm,
  τ_cd und f_yd.
- **k_E statt k_e**, wie in der Norm; der Kurzname bleibt k_e, damit
  gespeicherte Projekte laden. 10 000 liegt im Band der Norm für Kies und
  Kalk.
- **Die Diagramme lesen den Verweis vom Werkstoffgesetz**, statt ihn ein
  zweites Mal zu schreiben – beim Stahl fehlte dort 4.2.2.5.
- **Offen für den Benutzer** ([[TODO]]): «Stahl II», die Rundung von
  Tabelle 8, die Vorgabe c_nom = 30 mm, die konstruktiven Regeln der
  Bewehrungssuche, der Verweis der Dichten auf SIA 261.

## 2026-11-14 · Normprüfung II: Querkraft und Torsion

Zweiter Bereich, jede Änderung an der Normseite bestätigt (S. 49, 54–59).

- **Eine Einlage zählt ab d/6, mit ihrem grössten Mass** (4.3.3.2.9).
  Vorher ab h/6, nur mit ihrer Höhe und nur, solange sie kleiner als d war.
  Bei h = 300 und d = 248 mm vermindert ein Rohr ⌀45 d_v jetzt auf 203 mm;
  vorher blieb es unter h/6 = 50 mm unbeachtet. Reicht eine Einlage über d,
  bleibt ohne Bügel kein Widerstand – vorher fiel sie dort ganz weg. Das
  Feld heisst weiter `einlagenhoehe`, damit gespeicherte Projekte laden.
- **Zug zählt im Dekompressionsmoment** (4.3.3.2.6): m_Dd = −N_Ed·h/6, Zug
  positiv. Vorher setzte eine Zugkraft m_Dd auf null; bei h = 300 mm und
  N_Ed = +200 kN ist es jetzt −10 kNm, die Dehnung grösser und der
  Widerstand kleiner. h/6 ist Mechanik des Rechtecks, kein Normtext.
- **Unter Normalzug ist die Neigung der Druckdiagonalen mindestens 40°**
  (4.3.3.3.3). Vorher wurde α_min auf genau 40° gesetzt, ein eingegebenes
  42° also gesenkt.
- **d der Querkraft reicht bis zum Schwerpunkt aller gezogenen Lagen**
  (4.3.3.2.2 verlangt für k_d alle Lagen der Richtung). Vorher bis zur
  äussersten, 1 bis 3 mm zu viel: im Beispiel 249 statt 248.1 mm.
- **Namen wie in der Norm:** ε_v heisst «nominelle Dehnung der
  Zugbewehrung», nicht «Dehnung auf halber Höhe»; k_d «Beiwert für den
  Querkraftwiderstand» statt «für die statische Höhe». Bügel und Schubwände
  schreiben f_yd statt f_sd, dem Zeichen der Ausgabe 2013. V_Rd,min der
  Kennzahlen ist der kleinste Widerstand bei elastischer Bewehrung; darf
  sie plastisch werden, gilt (41), und er liegt tiefer.
- **Ziffern:** ohne Bügel 4.3.3.2.1 mit (35), (36), (37), die Dehnung
  4.3.3.2.2 mit (38), (39) und 4.3.3.2.3, (41); mit Bügeln 4.3.3.4.3, (45)
  und 4.3.3.4.6, (47) statt 4.3.3.2; die Grenzen der Neigung 4.3.3.3.2,
  (42) und 4.3.3.3.3, k_c 4.2.1.7; Bredt 4.3.5.2, (55), Figur 20, mit
  Querkraft zusammen 4.3.5.5; der Bügelschenkel 4.2.2.4 statt 5.5.2.
- **In der Norm nicht gefunden** und so markiert: das Federmodell der
  Schubwände, die Aufteilung der Torsion auf mehrere Zellen, die Torsion
  ohne Zelle.
- **Offen für den Benutzer** ([[TODO]]): m_Rk bei charakteristischer
  Rechenwahl, die Längszugkraft, die Eingabegrenzen von α und k_c, die
  Schubwände charakteristisch, die Wanddicke im Beispiel «Unterzug» und
  die Regeln, die das Werkzeug nicht prüft.

## 2026-11-14 · Normprüfung I: Biegung, Duktilität, Knicken

Erster Bereich der Prüfung aller Apps gegen SIA 262:2025, jede Änderung an
der Normseite bestätigt (S. 43–59, 75). Der Benutzer hat die Norm vorgelegt
und verlangt, dass kein Normtext wörtlich in die Software kommt.

- **Die Duktilitätsgrenze hängt am Stahl.** 4.1.4.2.5 setzt
  x/d ≤ k·435 N/mm²/f_yd mit k = 0.35: bei B500 0.35, bei B700B 0.25 –
  bis heute stand 0.35 fest. Mehr als k = 0.5 lässt das Werkzeug nicht zu
  (4.1.4.2.6). Ohne Nachweis des Verformungsvermögens gilt die Bedingung
  nur mit Stahl der Klasse B oder C (Tabelle 5) und Beton bis C50/60;
  sonst heisst der Nachweis «nicht führbar» statt eines Erfüllungsgrads.
  Das Feld heisst weiter `x_d_max`, damit gespeicherte Projekte laden; es
  hält jetzt k.
- **d im gezeichneten Querschnitt reicht bis zum Schwerpunkt der gezogenen
  Stäbe** – bei mehreren Lagen die mittlere statische Höhe, wie das
  Zeichenverzeichnis sie bestimmt. Vorher bis zum entferntesten Stab; x/d
  war damit zu klein.
- **Knicken verformt mit E_cd = E_cm/1.2** (4.2.1.17). Vorher mit E_cm: der
  Stab war 20 % zu steif, e_2d zu klein. Die Rechenwahl trägt dafür ihren
  Modul (`Rechenwahl.modul`); nur die Verformung beim Knicken wählt E_cd,
  alle anderen Rechnungen bleiben bei E_cm – γ_cE = 1.0 wie in 4.2.1.16.
- **k_t trägt seinen Verweis selbst** (4.4.1.3, (99), (100)). Vorher erbte
  er ihn von sieben Aufrufern, mal als 4.4.1.3, mal als 4.4.2.
- **Ziffern berichtigt:** Querschnittsanalyse 4.1.4 → 4.3.2.3; Stahlgesetz
  4.2.2.4 → 4.2.2.2 mit Figur 16; Parabel 4.2.1.5 mit Figur 12 und 4.2.1.6,
  (27); Schiefstellung 4.1.3.2.3, (17); ungewollte Ausmitte 4.3.7.5, (75);
  sprödes Versagen 4.4.1.3 → 4.3.1.2. Die Länge beim Knicken heisst wie in
  4.1.3.2.3 «Höhe des Druckglieds», nicht mehr «Systemlänge». Die Hilfe der
  Platte sagt, dass Drillmomente selbst zum Moment zu zählen sind (4.3.2.6).
- **Offen für den Benutzer:** das Kriechen beim Knicken – die Vorgabe
  φ = 0 liegt unsicher ([[TODO]]).

## 2026-11-13 · Decken: Lasten und Lastfälle

Dritter Schritt der App «Decken»: Flächen-, Linien- und Punktlasten, getrennt
nach Lastfällen, und Kombinationen mit Beiwerten. Ergebnisbilder und Bericht
folgen.

- **Lastfälle und Kombinationen gelten wie im Balkensystem.** Ihre Regeln
  – gleiche Namen, Beiwerte, eine Last ohne Lastfall – stehen jetzt einmal
  in `opencivil/projekt/aufbau/faelle.py`, ihre beiden Fenster einmal in
  `web/js/lastfaelle.js`. Vorher lag beides im Balkensystem; eine zweite
  Fassung für die Decke hätte jede Regel doppelt geführt. Eine neue Decke
  bekommt dieselben Fälle wie ein neues Balkensystem: Eigengewicht,
  Auflast, Nutzlast, dazu GZT und GZG.
- **Das Eigengewicht kommt von selbst**, je Platte ρ · g · h mit
  g = 10 m/s².
- **Gezeichnet wird in den Lastfall, der oben in der Leiste steht**; nur
  dessen Lasten sind zu sehen und zu wählen. Ein Klick auf eine Last in der
  Liste wechselt in ihren Lastfall. Ohne Lastfall lehnt ein Lastwerkzeug
  ab, bevor es beginnt: dafür kennt das Zeichenfenster jetzt `bereit(a)` je
  Werkzeug. Lehnte erst das Anlegen ab, blieben die schon gesetzten Knoten
  liegen.
- **Die Last auf einer ganzen Platte gehört zur Platte**: im Fenster der
  Platte «q überall», je Lastfall höchstens eine. So folgt sie jeder
  Änderung des Umrisses, ohne dass ein zweites Vieleck nachgeführt werden
  muss.
- **Eine Punktlast ist, wie die Stütze, eine Eigenschaft ihres Knotens**:
  Q und die Fläche l_x × l_y, über die sie sich verteilt.
- **Eine Last ohne Lastfall ist ein Hinweis, kein Fehler**: sie bleibt weg,
  der Rest rechnet – in der Decke wie im Balkensystem.
- **Die Probe je Fall**: Zusammenfassung und Bericht zeigen je Lastfall und
  Kombination die Last und was die Lager davon tragen. Was neben den
  Platten liegt oder auf einem Streifen, der nicht trägt, zeigt die
  Zusammenfassung nur, wo es das gibt; der Bericht immer, damit die Summe
  aufgeht. Die Meldungen eines Falls tragen seinen Namen.
- **Der Bericht** listet die Lasten in einer Tabelle (Lastfall, Last, wo,
  Wert) und schreibt jede Kombination als Summe aus.
- **Das Beispiel «Jede Wahl»** hat in jedem Lastfall Lasten, so dass jede
  Art einmal gerechnet wird; sie liegen so, dass keine Beschriftung auf
  einer anderen steht.

## 2026-11-13 · Decken: die App mit dem Zeichenfenster

Zweiter Schritt der App «Decken»: die Zeile in der Liste der Apps und das
Zeichenfenster. Lasten, Ergebnisbilder und Bericht folgen.

- **Dasselbe Zeichenfenster wie Querschnitt und Balkensystem**
  (`cadApp`), so verlangt: Platte (P), Linienlager (W), Stütze (S),
  Unterzug (U), Zone (Z) und Knoten (K), in Metern auf einem Raster von
  0.5 m. Die Teile hängen an gemeinsamen Knoten; wer einen verschiebt,
  verschiebt jede Platte und jedes Lager daran mit.
- **Eine Stütze ist kein eigenes Teil, sondern eine Eigenschaft ihres
  Knotens.** Wer den Knoten wählt, sieht «Stütze ja/nein» und ihre Masse.
  So lässt sie sich nicht von ihrem Ort trennen, und es gibt keine zweite
  Stütze am selben Punkt.
- **Unter der Zeichnung, was der Kern sagt**: die Aufteilung der Last
  (orange ganz in Richtung 1, gelb ganz in Richtung 2, dazwischen
  gemischt), die Streifen samt Stützenbereichen, oder nichts. Der Kern
  rechnet nach jeder Änderung neu (Anfrage `decke_zeichnung`, nur die eine
  Decke); bis die Antwort da ist, steht die alte blass. So sieht der
  Benutzer die «intelligent definierte» Aufteilung schon beim Zeichnen,
  und die Oberfläche rechnet nichts selbst.
- **Die Meldungen des Kerns stehen neben der Zeichnung**; ein Klick wählt
  die Teile, die sie nennt, und diese sind rot. Die Meldung «trägt keine
  der beiden Richtungen» nennt jetzt nur noch die Platte, der ein Lager
  fehlt – vorher alle Platten, die mit ihr dieselben Richtungen teilen.
- **Die Hilfen der Mehrfachwahl** (`schalterzeile`, `gemeinsam`, `mitVar`,
  `zahlfeldMitVar`, `jaNein`) stehen jetzt in `cad_app.js` statt im
  Balkensystem: das schwebende Fenster der Decke braucht sie auch.
- **Namen im Bild**: ein Unterzug heisst bei einem Viertel seiner Länge –
  in der Mitte stünde er oft auf dem Namen der Platte, am Ende auf dem
  einer Stütze.

## 2026-11-13 · Decken: der Rechenkern der Streifenmethode

Erster Schritt der neuen App «Decken» (Wunsch des Benutzers, 2026-11-13):
ganze Stahlbetondecken aus mehreren Platten verschiedener Dicke, auch nicht
rechtwinklig, auf Linienlagern (mit oder ohne Einspannung, mit oder ohne
vertikale Halterung) und Stützen, mit versteckten Unterzügen, unter Flächen-,
Linien- und Einzellasten je Lastfall, mit Kombinationen. Gerechnet nach der
Streifenmethode, nicht mit finiten Elementen – so verlangt. Quellen sind die
Vorlesung Stahlbeton II, 7.2 Platten, und die Musterlösung des Kolloquiums 4,
beide vom Benutzer. Der Kern steht in `opencivil/decke/`; die Oberfläche
folgt in eigenen Schritten: Zeichnen, Lasten und Lastfälle, Ergebnisbilder,
Bericht mit Herleitung.

Warum es so gebaut ist:

- **Elastisch gelöste Streifen.** Der Benutzer hat für statisch unbestimmte
  Streifen die elastische Rechnung gewählt. Jeder Streifen ist ein
  Durchlaufträger; seine Steifigkeit folgt der Platte, über die er gerade
  läuft. Darum läuft ein Streifen über die Grenze zweier Platten durch, und
  die dickere zieht mehr Moment an.
- **Unterzüge als Flächenlager** (Folie 33). Erst elastisch mit Punktlagern
  lösen, dann die Statik mit gleichmässiger Pressung über die Breite des
  Unterzugs – wie die Musterlösung, die so über der Mitte von −10.9 auf
  −7.3 kNm/m kommt. Ein Unterzug liegt auf denen höherer Stufe, die
  Feldstreifen haben Stufe null; gerechnet wird von unten nach oben, und was
  ein Träger an Lagerkraft abgibt, ist die Last des nächsten.
- **Wer trägt, wenn zwei Lager am selben Ort sind:** das Linienlager vor dem
  Unterzug, der höhere Unterzug vor dem tieferen, der Unterzug vor der
  Stütze. Sonst trüge eine Last doppelt.
- **Die Aufteilung** ist fest (ein Anteil für die ganze Decke) oder
  automatisch: Folie 31 verallgemeinert. Je Zelle zweier Streifen trägt die
  Richtung, die überhaupt Lager hat; haben beide, geht eine randnahe Last
  (näher als ein Viertel der kürzeren Spannweite) zum nahen Rand, sonst zur
  kürzeren Spannweite; nahe zweier Ränder und bei gleicher Spannweite je die
  Hälfte. Das trifft die Momente der Folie genau. Gezeichnete Zonen mit
  eigenem Anteil gehen vor; der Benutzer wollte beides.
- **Lasten genau integriert.** Jedes Vieleck zerfällt in Dreiecke, wird mit
  dem Band eines Streifens geschnitten, und seine Breite quer zum Streifen
  ist stückweise linear: daraus werden Streckenlasten, ohne Raster. Eine
  Linienlast ist ein Band von 1 mm, eine Einzellast eine Fläche
  l_x × l_y (Vorgabe 1 × 1 m) – so braucht es nur eine Art, Lasten zu
  verteilen, und auf einer Streifengrenze teilt sich eine Linienlast von
  selbst zur Hälfte.
- **Schiefe Platten** tragen in den Richtungen ihrer Ränder. Ein schiefer
  Streifen trägt `m_η`; ausgegeben werden `m_x`, `m_y` und `m_xy` (die
  Transformation der Folie 14 rückwärts), daraus die Biegewiderstände nach
  der linearisierten Fliessbedingung (Folien 9 und 10). Das hatte der
  Benutzer ausdrücklich verlangt.
- **Lagerkräfte** («Es sollen auch Lager Kräfte ersichtlich sein», Benutzer):
  je Stütze die Kraft, je Linienlager der Verlauf in kN/m samt
  Einspannmoment, je Streifen seine Lagerkräfte. Jeder Fall prüft das
  Gleichgewicht: Last = Lagerkräfte + was neben den Platten liegt + was ein
  Streifen ohne Lager fallen lässt. Beides wird gemeldet, nichts still
  verworfen.
- **Lastverteilelemente** (Folie 38) über jeder Stütze und unter jeder
  Einzellast: was der Bereich zusätzlich braucht, damit die Kraft als Punkt
  hineinpasst.

Gegen das Kolloquium 4: A-A und C-C kommen wie in der Musterlösung heraus.
B-B rechnet die Musterlösung mit dem Faktor 8.0, als läge die Last aus C-C
über die ganze Länge des Unterzugs; die App legt sie dorthin, wo C-C
wirklich aufliegt, also nicht über die Unterzüge in y. Daher über der Mitte
−60.1 statt −58.5 kNm/m und die Stützen 115.0 und 276.4 statt 115.5 und
275.1 kN. Die Tests prüfen die App gegen die Handrechnung mit dieser Last und
die Musterlösung daneben mit ihrer Rundung (`tests/test_decke_rechnung.py`).

## 2026-11-11 · Die Vorgängerfassung aus dem Repo

`_Old by Gemini/`, der alte Prototyp (32 Dateien), ist weg, auf Wunsch des
Benutzers. Nichts im Werkzeug brauchte ihn, aber er war das Einzige im Repo
mit fremden Paketen (FastAPI, Uvicorn, Pydantic, SymPy) – wer fragte, ob
das Repo für sich steht, musste ihn ausnehmen. Seine Dateien stehen noch in
der git-Geschichte, zuletzt im Commit `673dc33`; dort liegt auch die alte
Wunschliste `TODOs.txt` des Benutzers. In die TODO-Notiz kommt sie nicht
(Benutzer, 2026-11-11). Den Vergleich mit damals führt das README weiter.

## 2026-11-10 · Verträge, die in einer Klasse stehen

Aus der Strukturdurchsicht vom 2026-11-09, Punkt 12, zweiter Teil. Für den
Benutzer ändert sich nichts; Berichte und Zahlen sind dieselben.

- **Der Stahl nur auf Zug ist eine eigene Art** (`StahlNurZug`). Bis dahin
  war er ein Schalter `nur_zug` am `Stahlgesetz`, nach dem sechs Stellen
  fragten – Seite, Wort, Normstelle, Rollen, Formel und Funktion. Jetzt
  stehen die vier Namen als Klassenwerte da, und die Eigenschaften des
  `Gesetz`, die sie nur durchreichten, sind weg. Die Handrechnung nimmt
  `StahlNurZug.aus(stahl)`.
- **Eine Grundlage der Rechenobjekte** (`core/rechenobjekt.py`): die Kennung
  eines Werts nach Kurzname (`id_von`) und das Anmelden im Rechenwerk, nach
  den Baustoffen (`ins_rechenwerk`, `baustoffe`). Sieben Klassen schrieben
  beides von Hand; zwei nannten bei einem unbekannten Kurznamen die
  bekannten, die übrigen nicht. Der Baustoff behält sein eigenes Anmelden,
  das zweimal Anmelden verträgt.
- **Der Vertrag der Bauteile** (`BauteilEintrag`): worauf ein Bauteil zeigt,
  Materialien und Querschnitte. Danach fragt das Projekt vor dem Löschen.
  Bis dahin schrieb ihn jede Art selbst, viermal `return []`, und eine neue
  Art, die ihn vergass, fiel erst beim Löschen auf. Ein Test prüft jetzt
  jede Art und jedes gebaute Objekt.

## 2026-11-10 · Aufgeräumt: Totes und doppelt Gefangenes

Aus der Strukturdurchsicht vom 2026-11-09, Punkt 12, erster Teil. Für den
Benutzer ändert sich nichts.

- **Tot oder nur geschrieben, jetzt weg:** `Rechenwerk.erzeuger`,
  `Protokoll.warnungen`, `Knickergebnis.halbierungen` und `.durchlaeufe`,
  `Baustoff.eingabewerte`; im JS `rechnetImBrowser` und der Haken
  `anhangVorschau`, den kein Zeichenfenster anbot; im Stilblatt die Regeln
  des alten Lastblocks im Balkensystem, `.marke-gut`/`-schlecht`,
  `.abstand-oben` und die y-Marke der Duktilitätszeile, die nur x kennt.
  `Durchstanzbefund.rotationen` bleibt: ein Test prüft die Rotation daran.
- **Der Dienst fängt nicht doppelt.** Vier Anfragen fingen einen
  `ProjektFehler` und warfen ihn als 400 weiter – genau das tut
  `bearbeite` für alle. Jetzt steht es dort, mit einem Satz dazu.

## 2026-11-10 · Die Anzeige: Einheiten an einer Stelle, Legenden aus dem Kern

Aus der Strukturdurchsicht vom 2026-11-09, Punkt 10.

**Für den Benutzer:** Unter den Bildern von Grundbruch, Setzung und
Durchstanzen stehen die Zeichen jetzt als Formeln, wie in der Herleitung –
vorher «N_Ed = 500.0 kN» als Text, jetzt N mit tiefgestelltem Ed und
«500 kN», die Zahlen gerundet wie im Bericht. Der Gleitkörper heisst H_Gl
und L_Gl wie in der Herleitung, nicht mehr H und L wie das Fundament. Beim
Setzungsbild steht die Länge des Fundaments vor «Tiefen überhöht».

**Die Legenden kommen aus dem Kern.** Bis dahin baute das JS sie aus den
Zahlen der Zeichendaten, samt Vergleich, Urteil und Literaturstelle
(«Kap. 8.10», «Bild 8.15»). Jetzt schreiben `grundbruchdaten`,
`setzungsdaten` und `durchstanzdaten` die Zeilen, als Zellen aus Text und
Formeln – dieselben wie in den Tabellen der Herleitung –, und
`gb_skizze.legende` setzt sie nur. In der Oberfläche bleibt, was nur sie
weiss: dass noch nichts gerechnet ist, welche Kombination gezeigt wird und
wie stark das Bild überhöht. Zahlen, die nur der Legende dienten, fallen
aus den Zeichendaten weg.

**Die Einheiten der Anzeige an einer Stelle** (`web/anzeige.py`): `zahl`
rechnet von SI in eine Einheit des Kerns, `si` zurück; die Linien der
Diagramme tragen ihre `Anzeigegroesse`. Bis dahin stand das auf drei Wegen
da – als Grösse nur für die Linien, sonst als nackte Faktoren `* 1e3`
und `/ 1e6`, und `kN = 1e-3` in den Bildern hiess das Gegenteil von
`kN = 1e3` beim Bauen. Wo der Kern selbst umrechnet, heisst der Faktor
jetzt nach der Einheit (`KN.faktor`, `MM.faktor`).

## 2026-11-10 · Je Seite eine Lage: eine Regel für Löser und Handrechnung

Aus der Strukturdurchsicht vom 2026-11-09, Punkt 9. An den Zahlen ändert
sich nichts.

Die Rechenart «Handrechnung» verspricht im Löser denselben Querschnitt wie
die Resistenzlinie aus Handrechnung: je Seite eine Lage im Schwerpunkt.
Gerechnet wurde das zweimal, und die Antworten gingen auseinander – ohne
Angabe der Seite entschied im Löser die Tiefe, in der Handrechnung nie; bei
zwei Stählen auf einer Seite meldete der Löser einen Fehler, die
Handrechnung nahm den schwächeren; eine leere Seite fiel im Löser weg und
stand in der Handrechnung mit ihrer Höhe. Den Schwerpunkt mehrerer Flächen
rechnete dazu `lage_aus_posten` ein drittes Mal.

Jetzt fasst `querschnittsloeser.je_seite` zusammen, und beide fragen dort:

- **Die Seite sagt die Lage**, nicht die Tiefe – eine Lage ohne Seite ist
  ein Fehler. Gebaut werden die Lagen ohnehin nur in `stahllagen`, und die
  kennt die Seite immer.
- **Je Seite ein Stahl**, sonst ein Fehler. Seit eine Platte einen Stahl für
  alle Lagen hat (Benutzer, 2026-10-24), kann es zwei gar nicht geben; die
  Regel «der schwächere zählt» lief nie.
- **Eine Seite ohne Stahl fehlt.** Die Handrechnung setzt sie mit null
  Fläche ein, damit ihre Formeln gelten; der Löser lässt sie weg.
- **Die zusammengefasste Lage behält ihre Teile**, ihren Index und einen
  Namen aus den Teilen. Ihre eigenen Posten (`handrechnung.Posten`)
  braucht die Handrechnung darum nicht mehr.

Den Schwerpunkt mehrerer Flächen rechnet `lagenaufbau.schwerpunkt`, für die
Posten einer Lage wie für die Lagen einer Seite.

## 2026-11-10 · Die Nachweise je Lage auf einer Schablone

Aus der Strukturdurchsicht vom 2026-11-09, Punkt 8. Für den Benutzer ändert
sich nichts; Kennungen, Zeichen, Texte und Herleitungen sind dieselben.

Duktilität, sprödes Versagen und die beiden Zwängungen der Platte prüfen je
Lage. Jeder der vier wählte seine Lagen selbst, entdoppelte die Stähle,
baute die Kennung seiner Grade und lief seine eigene Schleife über die
Lagen; der allgemeine `Nachweis` trug für sie `ohne_bewehrung` mit. Jetzt
steht das einmal, in `nachweis/lagennachweis.py`, und jeder Nachweis sagt
nur noch, was bei ihm anders ist: was alle Lagen brauchen (`ansatz`), die
eine Lage (`eine_lage`) und ihre Herleitung (`protokoll_lage`).

- **Eine leere Lage meldet sich.** Drei der vier lassen sie weg (Benutzer,
  2026-10-19), der Aufbau gibt sie ihnen gar nicht. Ihr Zweig «ohne
  Bewehrung → kein Nachweis» lief darum nie. Er ist weg; bekommt einer
  doch eine leere Lage, ist das ein Fehler des Aufbaus und kein Urteil, das
  still als nicht erfüllt zählte (`NUR_MIT_STAHL`). Nur die Zwängung auf
  Normalkraft prüft jede Lage, auch die leere.
- **Die Zwängung auf Biegung erbt zweimal:** vom `Biegezwang`, den sie mit
  dem gezeichneten Querschnitt teilt (Name, Normstelle, Einleitung), und von
  der Schablone.

## 2026-11-10 · Eine Bauteilart: wo sie steht und dass sie überall steht

Aus der Strukturdurchsicht vom 2026-11-09, Punkt 5. Für den Benutzer ändert
sich nichts.

Der Steckbrief einer Bauteilart versprach «nirgends sonst», tatsächlich
stand sie an rund fünfzehn Stellen, und sieben schwiegen, wenn sie fehlte.
Der Kern kennt Bericht und Oberfläche nicht; was die je Art brauchen,
steht darum in ihren Schichten – aber je an einer Stelle, und vollständig:

- **Zeichendaten.** Statt eines Schlüssels je Art (`balkensysteme`,
  `stabumrisse`, `grundbrueche`, `setzungen`, `durchstanzstellen`) liefert
  die Antwort `zeichendaten[kennung]`, und `web/zeichendaten.py` sagt je
  Art, wie sie entstehen – auch, dass Platte und Analyse keine haben.
  Fehlt eine Art, scheitert das Laden.
- **Kennzahlen** für jedes Bauteil; welche es hat, sagt das Bauteil.
- **Was über der Nachweistabelle steht** (`ANGABEN`) nennt jede Art,
  das Balkensystem mit `None`; der Test prüft es, beim Laden geht es
  wegen der Reihenfolge der Module nicht.
- **Vorlagen des Katalogs.** Sie entstehen im selben Durchgang wie die
  Feldangaben, je Klasse unter demselben Namen – aus «einwirkung» wurde
  «kombination», wie ihre Felder schon hiessen. Ein neuer Eintrag nimmt
  die Vorlage seiner Liste (`katalog.neu`), die je Bauteilart von selbst
  entsteht. Alle dreissig Vorlagen sind Zeichen für Zeichen dieselben.
- **`objekte("…")`** meldet einen Namen, den keine Art trägt.
- **In der Oberfläche** sind die Karten im Reiter «Diagramme» und die
  Übersicht einer Art ohne Nachweise Felder ihrer Zeile in apps.js; fehlt
  eines, scheitert das Laden. bericht.js kennt keine Art mehr selbst.
- **Sinnbilder:** ein Test findet jedes Zeichen, das die Oberfläche nennt.

`tests/test_bauteilarten.py` hält die Verzeichnisse beisammen.

---

## 2026-11-10 · Dateien unter tausend Zeilen

Aus der Strukturdurchsicht vom 2026-11-09, Punkt 11. Für den Benutzer
ändert sich nichts; der Bericht ist derselbe.

- **core/berechnung.py** (1095 Zeilen): der Nachweis mit Vergleich, Urteil,
  `grad_def` und `Fallbefund` steht in `core/nachweis.py`; berechnung.py
  behält, was eine Berechnung allgemein ist (594).
- **projekt/projekt.py** (897): das Beispiel und «Jeder Nachweis» stehen in
  `projekt/beispiele.py`. `Projekt.beispiel()` und
  `Projekt.jeder_nachweis()` bleiben als Zugang – die Anleitung nennt sie.
- **projekt/balkensystem.py** (906): wie der Eintrag zum Stabwerk in SI
  wird, mit seinen Meldungen, steht beim Aufbau
  (`aufbau/balkensystem.modell_von`). Der Eintrag beschreibt, der Aufbau
  übersetzt – wie bei jeder anderen Bauteilart.
- **diagramm.js** (959): die Bilder der Platte – Querschnitt,
  M-N-Interaktionsdiagramm, M-V- und Neigungskurven – und ihre Karten aus
  bericht.js stehen in `platte_bilder.js`. diagramm.js behält die Kurve
  eines Werkstoffgesetzes und das Entzerren von Beschriftungen;
  `spannungskarten` steht bei den Spannung-Dehnung-Bildern
  (spannungsbild.js). Damit ist die Vorbedingung von Punkt 5 erfüllt:
  bericht.js kennt keine Bilder einer Bauteilart mehr selbst.

Übersehen hatte die Durchsicht cad_fenster.js mit 1138 Zeilen; das steht
in [[TODO]].

---

## 2026-11-10 · Oberfläche: eine Grundlage für die Zeichenfenster

Aus der Strukturdurchsicht vom 2026-11-09, Punkt 3. Für den Benutzer ändert
sich nichts.

Querschnittsanalyse, Balkensystem und Durchstanzen haben je ein
Zeichenfenster, und jedes trug denselben Adapter: das Fenster je Kennung
und sein Vergessen, ob es noch gilt, Lesen und Schreiben des Eintrags, das
Wählen von aussen, die Liste unter dem Fenster mit ihrer Markierung, den
Titel mit den Meldungen des Kerns, die Lagefelder eines Punktes, den Umriss
für «Alles zeigen» und den Namen eines Knotens. Das steht jetzt einmal in
`cad_app.js` (`cadApp`, `cadBereichMitListe`, `cadZeile`, `lagefelder`,
`umrissVon`, `mitTitel`) und in `cad_modell.js` (`knotenname`); die Apps
geben nur dazu, was sie selbst wissen. Ein Zeichenfenster vergisst seine
Kennung jetzt mit `ansichtVergessen` – die drei Haken `vergessen` in
apps.js sind weg. Zwischen den Adaptern der Analyse und des Systems sind
statt rund 150 nur noch Abschnittsüberschriften gleich.

---

## 2026-11-10 · Oberfläche: Katalog, Fassung und Ansichten

Aus der Strukturdurchsicht vom 2026-11-09, Punkt 7.

- **Der Katalog.** Die Oberfläche las ihn, als könnte er fehlen
  (`zustand.katalog?.a?.b || []`, an 35 Stellen): ein umbenannter
  Schlüssel im Kern ergab still einen leeren Schalter. Er kommt aber beim
  Start mit dem Projekt. Jetzt liest jede Stelle über `katalog('a', 'b')`
  (zustand.js), und ein fehlender Schlüssel meldet sich mit seinem Pfad.
  `test_katalog_js.py` liest die Aufrufe aus dem Quelltext und schlägt jeden
  Pfad im Katalog des Kerns nach – ein umbenannter Schlüssel fällt im Test
  auf, nicht beim Klicken. Die eigenen Zugriffe in bs_teile.js und
  qa_vorlagen.js mit ihren Ersatzwerten sind weg.
- **Was veraltet ist.** Ob eine Antwort des Kerns noch zur Eingabe passt,
  entschieden drei Abdrücke von Hand (Geometrie der Querschnittsanalyse,
  ihre Diagramme, Übersicht und Verläufe des Balkensystems), jeder mit
  seiner eigenen Liste dessen, wovon er abhängt. Jetzt zählt
  `projektAendern` eine Fassung des Projekts hoch, und eine Antwort gilt
  für die Fassung, zu der gefragt wurde. Das fragt öfter: nach einer
  Änderung an der Platte auch nach den Diagrammen der Analyse. Ob sich für
  sie etwas geändert hat, entscheidet der Kern mit dem Abdruck, den er
  schon hatte (speicher.py, mit den Bezügen des Bauteils); die Diagramme
  einer Analyse merkt er sich jetzt darunter (`dienst.DIAGRAMME`). Im
  Browser: 16 ms statt 429 ms für die zweite Frage.
- **Was sich die Ansichten merken.** Gezeigter Fall, Schnitt des
  Interaktionsdiagramms und letzte Antwort lagen in drei Wörterbüchern je
  Kennung, die nie vergassen: wer a1 löschte und neu anlegte, sah kurz die
  alten Diagramme. Jetzt liegt das in `ansichtVon(kennung)`, geleert beim
  Anlegen, Kopieren und Löschen; ein neues Projekt (`projektSetzen`, beim
  Start und beim Öffnen) leert alles. Die Zeichenfenster haben noch ihr
  eigenes Gedächtnis – das gehört zu Punkt 3.

---

## 2026-11-10 · Oberfläche: Einträge über ihre Kennung

Aus der Strukturdurchsicht vom 2026-11-09, Punkt 6. Für den Benutzer ändert
sich nichts.

Die Oberfläche suchte einen Eintrag an rund 70 Stellen über den Namen
seiner Liste (`eintragAendern('querschnitte', k, …)`, `p.materialien.find(…)`),
mit zwei Regeln für einen falschen Namen: `eintragAendern` tat still nichts,
legte aber ab und rechnete; die Fassungen von Hand warfen. Kennungen sind im
Projekt eindeutig, darum genügt jetzt die Kennung: `eintragVon(kennung)`
findet den Eintrag in jeder Liste, `eintragAendern(kennung, v)` ändert ihn,
und gibt es ihn nicht mehr, geschieht nichts – weder abgelegt noch
gerechnet. Weg sind das Listenargument, `anBauteil` mit dem Feld `liste` der
Orte und acht eigene Leser in den Zeichenfenstern und Diagrammen. Listen
nennen nur noch, wer eine Liste braucht: Anlegen, Kopieren, Löschen.

---

## 2026-11-10 · Durchstanzen: die gestützte Fläche als Art

Aus der Strukturdurchsicht vom 2026-11-09, Punkt 4. Für den Benutzer ändert
sich nichts; der Bericht ist Zeichen für Zeichen derselbe.

- Lage und Form waren Textwahlen, nach denen Stelle, Nachweis, Bewehrung
  und Maske an 28 Stellen fragten. Jetzt macht `Lage.flaeche(form)` daraus
  einmal eine Art – Innen-, Rand- und Eckstütze mit ihrer Form, Wandende,
  Wandecke (`flaeche.py`) –, und die weiss, was der Nachweis von ihr
  braucht: Masse, Umriss, Achse, Ränder, die Kandidaten des Schnitts, u_0
  als Formel, die Näherung für k_e, die Gleichungen (62) bis (65) und ob es
  Durchstanzbewehrung und Stahlpilze gibt.
- Welche Felder der Nachweis liest, steht einmal
  (`stelle.eingaben_fuer`). Der Katalog gibt der Maske dieselben Teile je
  Wahl – die Masse je Lage und Form, die Felder je Näherungsstufe an
  dieser Lage, die von k_e –, und die Maske zeigt ihre Vereinigung.
  Bisher baute sie die Regel nach: welche Masse, wann r_s und m_sd, wann
  e_x und e_y. Auch den Kurztext der Liste («⌀450 mm», «Wand 250 mm») gibt
  der Katalog, als Vorlage mit den Namen der Masse.
- Ein Test hält Maske und Kern für alle 90 Wahlen gleich.

---

## 2026-11-09 · Durchstanzen: ein Schnittnachweis für alle drei Schnitte

Aus der Strukturdurchsicht vom selben Tag, Punkte 1 und 2. Für den Benutzer
ändern sich keine Zahlen.

- Um die Stütze, aussen um die Anker und um einen Stahlpilz läuft dieselbe
  Folge: der Schnitt, was von ihm nicht zählt, k_e, V_d − q_d·A und
  V_Rd,c nach (58). Sie stand dreimal da, mit drei Werkzeugen, und die
  Suche nach Leisten und Pilz prüfte (66), (67) und den äusseren Schnitt
  stumm, die Herleitung noch einmal laut. Änderte sich eine Bedingung an
  einer Stelle, wich der Vorschlag still vom Nachweis ab. Jetzt rechnet
  `pruefung.py` jede Bedingung einmal (`Schnittpruefung`,
  `Leistenpruefung`, `Pilzbefund`), ohne Herleitung; die Suche fragt ihr
  Ergebnis, die Herleitung schreibt dieselben Zahlen, für alle drei
  Schnitte mit denselben Schritten (`herleitung.py`).
- Damit sind die Formeln an allen drei Schnitten dieselben: sieben Seiten
  der Formelsammlung («Äusserer Nachweisschnitt ohne das, was nicht zählt»,
  «Querkraft im Schnitt um den Stahlpilz» …) gingen in die fünf Seiten des
  Schnitts um die Stütze auf, ihr Theorietext steht jetzt dort. Die
  Zeichen tragen den Index des Schnitts zuletzt: u_{red,out}, u_{0,P}. Die
  Flächenlast aussen und um den Pilz ist ein eigener Schritt,
  ΔV_{d,out} = q_d·A_{q,out}, wie um die Stütze.
- Ein Erfüllungsgrad, den kein Urteil trägt, ist unbeschränkt: das setzt
  jetzt `Nachweis.rechne` für jeden Nachweis. Bis dahin schrieb jeder
  Nachweis ∞ selbst, auf drei Arten – vier Nachweise im Kern, das
  Durchstanzen mit Wörterbüchern voller 0 und ∞. Sichtbar wird es an
  Wandende und Wandecke, wo das Werkzeug noch keine Bewehrung vorschlägt:
  die vier Grade mit Bewehrung stehen in der Wertetabelle als ∞ statt 0,
  denn gerechnet wurden sie nicht. Das Urteil «nicht erfüllt» kommt wie
  bisher aus dem Nachweis ohne Bewehrung.
- Der Befund trägt Leisten und Pilz getrennt (`leisten`, `pilz`), jedes mit
  seinen eigenen Zahlen, statt eines Befunds mit Platzhaltern
  (`V_Rd_max = ∞`, `k_sys = 0`) und einem `V_d_out`, das je nach Fall
  aussen um die Leisten oder um den Pilz hiess. Tabelle, Zeichendaten und
  Legende fragen sie ohne Weichen; die Kennwerttabelle zeigt beim Pilz
  jetzt auch Querkraft und Widerstand um ihn.

---

## 2026-11-09 · Durchstanzen: Leisten an Aussparungen

Gemeldet vom Benutzer: eine Leiste lief durch eine Aussparung, solange
keiner ihrer Anker darin lag. Geprüft wurden nur die Anker, nicht der Stahl
dazwischen. Jetzt gilt (`bewehrung.setzen`):

- Eine Leiste ist Stahl vom Rand der gestützten Fläche bis zum letzten
  Anker. Sie läuft weder über den Plattenrand noch durch eine Aussparung
  und hält zu beiden die Überdeckung c_nom. Stösst sie an, endet sie mit
  dem Anker davor; behält sie die angerechneten Anker nicht, fällt sie weg.
  Verschieden lange Leisten sind verschiedene Typen: «14 × DX5 + 2 × DX3».
- Im Schatten einer Aussparung, die näher als 5·d_v am Nachweisschnitt
  liegt, zählt der Schnitt nicht (Figur 23d). Dort liegt auch keine Leiste:
  Bewehrung, die diesen Teil des Schnitts quert, trägt nichts zur Stütze.
  Welche Aussparungen einen Schatten werfen, steht jetzt an einer Stelle
  (`schnitt.schatten_am_schnitt`), für den Schnitt und für die Leisten.

Im Prüfprojekt verliert die Ovalstütze neben ihrer Aussparung eine Leiste.

---

## 2026-10-30 · Durchstanzen: Stahlpilze ZEUS

Bricht an einer Innenstütze die erste Betondruckdiagonale (70), wählt das
Werkzeug den kleinsten ZEUS von AncoTech (Kreuz, Doppelkreuz, H-Kreuz;
Preisliste 12.2018), der zwischen die Überdeckungen passt (unten 20 mm,
oben 50 mm) und mit dem die Platte ausserhalb hält (4.3.6.6.2): ohne Leisten,
sonst mit ancoPLUS um den Pilz – dieselben vier Nachweise, mit dem Pilz als
gestützter Fläche bis an die Enden der Stege. d_v um den Pilz ist d − 20 mm
(gelesen). Den Widerstand des Pilzes selbst bestätigt der Hersteller; seine
Profile sind nicht veröffentlicht. Die Suche verwirft einen Pilz schon an
einer oberen Schranke seines Umfangs, bevor sie den Schnitt rechnet.

---

## 2026-10-30 · Durchstanzen: Durchstanzbewehrung mit ancoPLUS

Reicht der Beton allein nicht, schlägt das Werkzeug jetzt eine
Durchstanzbewehrung vor und weist sie nach. Das Produkt ist ancoPLUS von
AncoTech: Doppelkopfanker auf Leisten mit 2 bis 9 Ankern, ⌀10 bis 28 mm,
Höhen 125–455 mm. Die Typen «D» haben ungleiche Abstände: 0.375·d bis zum
ersten Anker, bis zum dritten 0.60·d, danach 0.75·d. So wünschte es der
Benutzer («Abstand zwischen 1. und 2. und 3. Eisen nicht konstant»). Die
Regeln stammen aus dem Gutachten Muttoni / Fernández Ruiz 2007 und der
Preisliste; das neuere Gutachten zu SIA 262:2025 war nicht lesbar.
Recherchiert sind ausserdem DURA-Körbe und S-Elemente (Leviat), HDB, FIDECA
und Peikko. Vorerst eingebaut ist nur ancoPLUS.

Die Suche (`durchstanzen/bewehrung.py`) stellt die Leisten senkrecht auf den
Rand der gestützten Fläche, an Ecken und Rundungen radial, beim zweiten
Anker höchstens 1.5·d auseinander. Sie nimmt den kleinsten Durchmesser, der
die Bewehrung (66) und das Verformungsvermögen (67) erfüllt, und dazu die
kleinste Zahl Anker je Leiste, mit der der äussere Schnitt nach Figur 26
aufgeht. Erst wenn kein Durchmesser reicht, stehen die Leisten dichter.
Nachgewiesen wird viermal (`durchstanzen/mit_bewehrung.py`, 4.3.6.5.1):
Bewehrung, Verformungsvermögen, erste Betondruckdiagonale (70) mit dem Faktor
des Gutachtens, und ausserhalb der Bewehrung. Das Urteil ohne Bewehrung
fällt dann nicht mehr; sein Grad steht als Wert in der Herleitung.

Der äussere Schnitt ist der Schnitt um eine «Stütze», deren Kern die Hülle
der äussersten Anker ist: von jeder Geraden zwischen zwei Ankern zählen
1.5·d_v,out von jedem Ende. Das ist dieselbe Regel wie an den Ecken grosser
Stützen (Figur 23a), also derselbe Code.

Neu ist eine Eingabe: die Überdeckung c_v der Anker auf der Druckseite. Sie
bestimmt d_v,out = d − c_v und den Faktor k_sys des Gutachtens.

Für Wandende und Wandecke gibt es noch keinen Vorschlag; die Herleitung
sagt es. Ebenso fehlen noch die Stahlpilze.

---

## 2026-10-30 · Durchstanzen: Aussparungen im Zeichenfenster

Die Aussparungen einer Durchstanzstelle entstehen jetzt in einem
Zeichenfenster unter «Durchstanzstelle», wie die Flächen der
Querschnittsanalyse: das Werkzeug «Aussparung» zeichnet ein Polygon, ein
«Hilfspunkt» setzt einen Knoten zum Fangen; Ecken und Knoten verschiebt man
mit V oder in den Feldern des schwebenden Fensters. Darunter liegt, was der
Kern zuletzt gerechnet hat: Stütze oder Wand, Plattenrand und
Nachweisschnitt, gezeichnet von derselben Funktion wie das Bild im Reiter
«Diagramme» (`ds_grundriss.js`). Die Ecken der Stütze fangen den Zeiger.

---

## 2026-10-30 · Durchstanzen: die App, noch ohne Durchstanzbewehrung

Die neue App «Durchstanzen» (Kennungen d1, d2 …): Decke oder Bodenplatte,
Innen-, Rand- und Eckstütze, Wandende und Wandecke; Rechteck-, Rund- und
Ovalstütze; Plattendicke, Überdeckung der Zugbewehrung, Grösstkorn, Beton
und Betonstahl; die Biegebewehrung je Richtung mit der Lage, die aussen
liegt; die Plattenrotation in den Näherungsstufen 1 bis 3; die Auflagerkraft,
die Flächenlast im Schnitt und k_e aus der Näherung oder aus der
Exzentrizität. Gerechnet wird der Widerstand ohne Durchstanzbewehrung
(`durchstanzen/nachweis.py`, Gleichungen (57) bis (65)), mit Herleitung,
Zusammenfassung und einem Grundriss im Reiter «Diagramme»: Stütze,
Plattenrand, Aussparungen und der Schnitt – was nicht zählt, gestrichelt.

Die **Ovalstütze** ist ein Rechteck mit halbrunden Enden, b_x × b_y über
alles. So heisst sie in der Software von Leviat; der Benutzer sprach von
«halbrunden Stützen mit speziellem Namen». Der Kern einer Stütze ist ohnehin
ein konvexer Kern mit Radius, die Ovalstütze ist also eine Strecke mit Radius.
Ihre geraden Seiten zählen wie die einer Rechteckstütze 1.5·d_v von jedem
Ende her.

**Decke und Bodenplatte** rechnen gleich. Verschieden ist nur, was im
Schnitt abgezogen wird (4.3.6.2.6): Eigengewicht und Nutzlast bzw. die
Bodenpressung, beide als Bemessungswert q_d. Ausserdem wechselt die
Zugbewehrung ihre Seite (oben bzw. unten), und mit ihr die Überdeckung.

Die **Aussparungen** verweisen auf Knoten im Grundriss, wie die Flächen der
Querschnittsanalyse. Gezeichnet werden sie im nächsten Schritt in einem
Zeichenfenster. Danach kommen die Durchstanzbewehrung (Produkte von
AncoTech und Leviat) und die Stahlpilze.

Gelesen, wo die Norm es offen lässt (in [[TODO]]): die Breite b_sr nach
Figur 25; Stufe 2 an Wänden rechnet wie Stufe 1, weil 4.3.6.4.7 dort keine
Momente nennt; jede Aussparung im Schatten gilt als «gross» für k_e = 0.7.

Nebenbei: die Linien des Schnitts für das Bild wurden zu grob gekürzt – es
wurde nur mit dem nächsten Punkt verglichen, und ein Bogen wurde zum
Vieleck. Jetzt nach Douglas und Peucker.

---

## 2026-10-30 · Durchstanzen, erster Baustein: der Nachweisschnitt

Wunsch des Benutzers: eine App für den Durchstanznachweis nach SIA 262:2025,
4.3.6, im Stil der AncoTech-Software. Die Normstellen 4.3.6.1 bis 4.3.6.7
(S. 60–66) hat er als PDF geliefert.

Der erste Baustein ist die Geometrie (`durchstanzen/schnitt.py`): der
Nachweisschnitt im Abstand d_v/2 um die gestützte Fläche (Figur 22) und was
von ihm nicht zählt (Figur 23, kumulativ) – an grossen Stützen die geraden
Stücke weiter als 1.5·d_v von einer Ecke, jenseits des Plattenrands, und
hinter einer Aussparung, die näher als 5·d_v liegt. Am Rand werden der
geschlossene Schnitt und die zum Rand gerechnet; es gilt der kürzere
(Figur 22d). Eine Stütze ist ein konvexer Kern mit einem Radius (Rechteck,
Rundstütze); Wandende und Wandecke haben ihren eigenen Schnitt (Figur 23b
und c). Gerechnet wird mit Teilstücken von 1 mm, die je zählen oder nicht;
so braucht kein Zusammentreffen von Rand, Ecke und Aussparung eine eigene
Formel. Die Tests prüfen die Fälle der Figuren gegen ihre Formeln von Hand.

Gelesen, wo die Norm es offen lässt (nicht nachgeschlagen, in [[TODO]]):
eine Strecke, die von einer Ecke zum freien Plattenrand läuft, zählt ganz
– die Begrenzung auf 1.5·d_v gilt zwischen zwei Ecken und entlang einer
Wand.

---

## 2026-10-25 · Aufbau: die Nachweise nur noch beim Bauteil

Aus der Strukturdurchsicht, der Rest: jeder Nachweis stand zweimal im
Aufbau – beim Bauteil und in einem von 23 Wörterbüchern je Nachweisfeld
(`aufbau.querkraft`, `aufbau.knicken` …), die fast nur die Tests lasen.
Jetzt steht er nur beim Bauteil, mit Feld und Schlüssel, und
`aufbau.feld("knicken")` ist die Sicht darauf. Die rund 90 Lesestellen
fragen so. Für den Benutzer ändert sich nichts.

---

## 2026-10-25 · Aufbau: die Objekte je Art nur noch im Bauteil

Aus der Strukturdurchsicht: jede Baufunktion legte ihr Objekt zweimal
ab – im Bauteil und in einem Wörterbuch ihrer Art (`querschnitte`,
`querschnittsanalysen`, `balkensysteme`, `grundbrueche`, `setzungen`).
Jetzt steht es nur im Bauteil, und die fünf Wörterbücher sind Sichten
darauf (`Aufbau.objekte`). Wer sie liest, merkt nichts. Für den Benutzer
ändert sich nichts.

---

## 2026-10-25 · Katalog: die Feldangaben jeder Klasse von Einträgen

Aus der Strukturdurchsicht: welche Einheit, Grenzen und Ganzzahligkeit ein
Feld hat, gab der Katalog der Oberfläche für elf Klassen von Einträgen, von
Hand aufgezählt. Jetzt geht er den Baum der Beschreibung ab, auf dem Weg,
auf dem auch das Lesen einer Datei ihn abläuft (`lesen.eintragsklassen`),
und bringt alle 49, je unter ihrem Namen ohne «Eintrag». Die elf alten
Angaben sind unverändert. Für den Benutzer ändert sich nichts; die
Einheiten, die noch nicht am Feld stehen, stehen in [[TODO]].

---

## 2026-10-25 · Bauteilarten: Zuordnung und Angaben über die Bauteile

Aus der Strukturdurchsicht: die Zuordnung der Kennungen der Oberfläche zu
den Wert-IDs (`api.zuordnung`) stand je Bauteilart von Hand da, Grundbruch
und Setzung wortgleich; was über einer Nachweistabelle steht
(`zusammenfassung.angaben`), fand die Art durch Probieren, ein Register
nach dem anderen. Jetzt gehen beide über die Bauteile: die Zuordnung gibt
jedem Namensraum, Name und seine Werte, und was eine Art mehr hat, steht
in `_ZUORDNUNG`; die Angaben stehen je Art in `ANGABEN`. Eine neue Art
bekommt die Zuordnung von selbst, und ohne Angaben meldet sie sich laut.
Für den Benutzer ändert sich nichts.

---

## 2026-10-25 · Balkensystem: frei, fest oder Feder als ein Wert

Aus der Strukturdurchsicht: wie ein Lager oder ein Linienlager eine
Richtung hält, reiste als Zahl – «fest» als unendliche Federzahl, «frei»
als `None` –, und das System übersetzte beides an 17 Stellen zurück, etwa
`wert not in (None, FEST)`. Jetzt ist es ein `Halt` mit `fest` und
`feder` (`FREI`, `FEST`, `feder(k)` in `stabwerk/modell.py`), und das
System liest nur noch `halt.fest` und `halt.feder`. Für den Benutzer
ändert sich nichts.

---

## 2026-10-25 · Spannung-Dehnung-Analyse: Moment oder Normalkraft ohne Schalter

Aus der Strukturdurchsicht: ob eine Linie über dem Moment läuft (M–χ und
der Modul darüber) oder über der Normalkraft, reisten die Herleitungen als
Ja/Nein `momente` weiter, bis in das Paar der Platte und des gezeichneten
Querschnitts, das den reinen Betonquerschnitt je nach Schalter als I_c
oder A_c schrieb. Jetzt hat das Paar dafür zwei Methoden
(`herleitung_traegheit`, `herleitung_flaeche`), und wer fragt, fragt die
Art der Analyse (`Analyseart.ueber_moment`) statt sie mit einer Konstanten
zu vergleichen. Für den Benutzer ändert sich nichts.

---

## 2026-10-25 · Vorlagen: Rechteck, T und Kreis einmal gezeichnet

Aus der Strukturdurchsicht: die Vorlagen der Querschnittsanalyse
(`querschnitt/vorlagen.py`) und die der Stabquerschnitte im Balkensystem
(`stabwerk/querschnitte.py`) zeichneten Rechteck, T und Kreis je für sich,
und ein Steg so breit wie der Flansch galt im einen als T, im anderen
nicht. Die Umrisse und die Prüfung des T stehen jetzt einmal, in
`querschnitt/vorlagen.py`; das Balkensystem nimmt sie von dort.

Die beiden Kataloge bleiben getrennt: der eine baut die Teile einer
Zeichnung mit Bewehrung und Schubwänden, der andere Formeln für A und I
samt Herleitung.

Für den Benutzer: ein T im Balkensystem mit b_w = b gilt nicht mehr –
«Der Steg b_w muss schmaler sein als der Flansch b.» Dafür gibt es das
Rechteck. Die Meldungen des T lauten in beiden Apps gleich.

---

## 2026-10-25 · Aufgeräumt: der Name eines Kennwerts an einer Stelle

Aus der Strukturdurchsicht: unter welchem Namen ein Nachweis einen
Kennwert eines Baustoffs liest, etwa «f_yk__B500B», bauten `stahlname` in
`rechenwahl.py`, `Querschnittsanalyse._name` und zwei Nachweise von Hand je
für sich. Jetzt sagt es der Baustoff selbst (`Baustoff.eingabename`, die
Eingabe dazu `Baustoff.bezug`). Für den Benutzer ändert sich nichts.

---

## 2026-10-25 · Querschnittsanalyse: drei Arten Bewehrung

Aus der Strukturdurchsicht: ein Bewehrungselement der Querschnittsanalyse
war ein Datensatz mit der Art als Text («stab», «flaeche», «anzahl»,
«teilung»), und ein Dutzend Weichen in fünf Modulen fragten sie ab – für
die Tabellen der Herleitung, die Angaben über den Nachweisen, die Fasern
des Querschnitts, den Durchmesser der Rissbreite und die Bilder. Jetzt ist
es ein `Einzelstab`, eine `Stabreihe` oder eine `VerschmierteLinie`
(`querschnitt/bewehrungselemente.py`), und jede Art sagt selbst, wo ihre
Stäbe liegen, wie sie in den Tabellen steht, wie sie in den Querschnitt
eingeht und welcher Durchmesser ihre Rissbreite bestimmt. Welche Art eine
Beschreibung ist, wird einmal entschieden, beim Bauen. Für den Benutzer
ändert sich nichts.

---

## 2026-10-25 · Platte: ein Bewehrungsposten in einer Gestalt

Rest von Befund 1 der Strukturdurchsicht: Ein Bewehrungsposten der Platte
reiste als Tupel `(Lage, Art, Posten, ID von A_s, ID von z)` und wurde rund
zwanzigmal nach Stelle zerlegt. Seine Marke «1g» entstand an neun Stellen
neu, die Breite je Richtung (b oder b_y) an drei, die Bezeichnung «1. Lage
Grundbewehrung» an drei. Jetzt reist er als `Postenbezug`, mit Marke,
Index, Bezeichnung und seinen Werten; unter welchem Namen ein Nachweis
diese liest, sagt er selbst (`name`, `bezuege`). Die Breite je Richtung
sagt `Richtung.breite`, den Index einer Lage `Bewehrungslage.index`.

Der Lagenaufbau und die Helfer für die Posten einer Lage zogen dafür in
ein eigenes Modul, `querschnitt/lagenaufbau.py`; `platte.py` sinkt von
1003 auf 661 Zeilen. Für den Benutzer ändert sich nichts.

---

## 2026-10-25 · Schubwand: der Bügelgehalt an einer Stelle

Aus der Strukturdurchsicht: den Bügelquerschnitt einer Schubwand je Länge,
n · π⌀²/4 / s, rechneten der Nachweis (`Wandangabe.a_sw_s`) und die Liste
unter der Zeichnung (`api.py`) je für sich. Jetzt steht die Formel einmal,
`geometrie.buegelgehalt`; die Liste rechnet nur noch in mm²/m um. Für den
Benutzer ändert sich nichts.

---

## 2026-10-25 · Aufgeräumt: die eingeschachtelte Mitschrift entfällt

Befund 6 der Strukturdurchsicht: `Protokoll.unterprotokoll` öffnete eine
eingeschachtelte Mitschrift. Keine Rechnung rief es mehr auf, und doch nahm
jede Darstellung – Konsole, LaTeX, Markdown, Oberfläche – je Block eine
«Tiefe» mit, durch 28 Funktionen. Beides ist weg: eine Darstellung bekommt
nur noch den Block. Für den Benutzer ändert sich nichts.

---

## 2026-10-25 · Querschnittsanalyse: die Biegung als eigene Wahl

Befund 3 der Strukturdurchsicht, dritter Teil: Ob der gezeichnete
Querschnitt «einachsig» rechnet, fragten 17 Dateien als Ja/Nein ab, 80-mal.
Die Regel für den Bruchzustand zu einer Einwirkung stand dreimal da, der
Betrag des Moments viermal, «V_y zählt einachsig nicht» dreimal.

- **`Biegung`** (`querschnitt/biegung.py`) mit zwei Stellungen, `SCHIEF` und
  `EINACHSIG`. Sie sagt je einmal, welche Momente und Querkräfte zählen, wie
  gross das Moment ist, welche Seiten ein Nachweis ziehen lässt, ob die
  Zugrichtung feststeht und welcher Bruchzustand zu einer Einwirkung gehört.
  Der Aufbau wählt sie einmal, aus dem Schalter der Beschreibung.
- **Die Herleitungen** schreiben je Moment, das zählt, eine Zeile – statt
  an sechs Stellen «wenn nicht einachsig, auch M_z». Wo eine Herleitung je
  Art ganz anders lautet (die Spannung am ungerissenen Querschnitt, der Riss
  der Spannung-Dehnung-Analyse), fragt sie `biegung.einachsig`, je an einer
  Stelle.
- Für den Benutzer ändert sich nichts.

---

## 2026-10-25 · Querkraft: zwei Nachweise, zwei Klassen

Befund 3 der Strukturdurchsicht, zweiter Teil, und die längste Datei des
Kerns: `querkraft.py` hatte 1188 Zeilen, und darin steckten zwei Nachweise
hinter einem `buegel is None` – der Ansatz ohne Bügel und das
Fachwerkmodell. Ihr Befund trug beide Hälften als «vielleicht leer», das
Fallergebnis die Zwischenwerte beider Ansätze.

- **Drei Module:** `querkraft.py` hält, was beide teilen – die Fälle, die
  statische Höhe der gezogenen Bewehrung, die Ausgaben, das Urteil, die
  letzte Zeile der Herleitung (335 Zeilen). `querkraft_ohne_buegel.py` hat
  `QuerkraftOhneBuegel` mit der Kurve über dem Moment,
  `querkraft_buegel.py` hat `QuerkraftMitBuegeln` mit dem Verlauf über der
  Neigung – je mit eigenem Befund und Fallergebnis.
- **Gewählt wird im Aufbau der Platte**, einmal: Bügel oder nicht. Was ein
  Ansatz liest, sagt er selbst (`_ansatzbezuege`); der Code ist sonst
  wortgleich umgezogen.
- Für den Benutzer ändert sich nichts.

---

## 2026-10-25 · Die Art eines Stabquerschnitts als eigene Klasse

Befund 3 der Strukturdurchsicht, erster Teil: Woher A und I eines Stabs
kommen, war ein Text («vorlage», «kennwerte», «platte», «analyse»), und vier
Schichten fragten ihn je für sich ab – die Beschreibung, der Aufbau, das
Rechenwerk (dort zwei fast gleiche Zweige) und das Bildchen einer Zeile.
«Platte oder Analyse» stand zweimal als Tupel da und einmal wörtlich.

- **`Querschnittsart`** ist eine Wahl wie die Rechenart: Name, kurzer Name
  und `aus_bauteil` – nur ein Querschnitt aus einer Platte oder Analyse
  bringt ein Material mit und hat ein E_eq. Der Katalog liest das aus ihr,
  statt die Arten von Hand zu listen.
- **Je Art eine Klasse** (`stabwerk/stabquerschnitt.py`): `NachVorlage`,
  `VonHand`, `AusPlatte`, `AusAnalyse`. Jede meldet ihre Berechnungen für A
  und I selbst an und kennt ihren Umriss; was Platte und Analyse gemeinsam
  haben, das Bauteil und das E_eq, steht in `AusBauteil`. Der Aufbau löst
  die Art einmal auf, Rechenwerk und Bildchen fragen sie nicht mehr.
- Für den Benutzer ändert sich nichts. Im JavaScript bleiben die Masken je
  Art – sie sind verschieden, weil die Eingaben verschieden sind.

---

## 2026-10-25 · Das Urteil der Nachweise aus einer Hand

Befund 2.1 der Strukturdurchsicht: Erfüllungsgrad, «erfüllt», die Regel für
«unbeschränkt» und das Urteil baute jeder Nachweis selbst (22-mal
`NachweisUrteil(`), und das war auseinandergelaufen.

- **`Vergleich`** im Kern (`core/berechnung.py`): Einwirkung gegen
  Widerstand. Er besitzt die Regeln: Grad = R/E; wirkt nichts in der
  Richtung, die der Widerstand begrenzt – E ist null oder wirkt ihr
  entgegen, etwa ein gedrückter Stahl –, ist er ∞; erfüllt ab eins. Dazu
  seine Zeilen der Herleitung (`zeile`, `bedingung`). Biegung mit
  Normalkraft gibt ihr Urteil selbst vor (`entscheid`): dort entscheidet, ob
  die Einwirkung innerhalb der Resistenzlinie liegt, wie es ihr Dateikopf
  seit jeher sagt – der Grad misst nur, wie weit.
- **Ohne Vergleich** zwei feste Ausgänge: `NICHT_FUEHRBAR` (Grad 0, nicht
  erfüllt, etwa eine Lage ohne Bewehrung) und `UNBESCHRAENKT` (∞, erfüllt,
  etwa ohne Druck beim Knicken).
- **`Nachweis.urteil(ziel, fall, ausgang, begruendung)`** baut das Urteil;
  ohne Vergleich kommt der Grund als Hinweis in die Zusammenfassung. Den
  Grad als Ausgabe stempelt `Nachweis.rechne` aus dem Urteil – vorher
  nannte jeder Nachweis ihn zweimal. Das Kurzzeichen steht als `ART` an der
  Klasse.
- **Die Fallergebnisse** (elf Klassen) tragen ihren `ausgang` statt
  `erfuellt` und `erfuellungsgrad` und lesen beides daraus ab
  (`Fallausgang`). Die `_urteil`-Methoden sind weg, ebenso der eigene
  `Vergleich` der Spannungsbegrenzung.
- **Was sich zeigt:**
  - Die Duktilität je Richtung und die Schubwände der Querschnittsanalyse
    zeigen ∞ statt «1000000000.00».
  - Bei Biegung mit Normalkraft zeigt die Herleitung jetzt wie die Tabelle
    das Vorzeichen: ein eingegebenes M_Ed = −50 kNm steht nirgends als
    50 kNm. Ein Betrag hätte die Zahl des Benutzers still umgedeutet. Die
    Zeichen in der Herleitung bleiben kurz, die Tabelle zeigt den Widerstand
    mit seiner Bedingung (`Vergleich.benannt`: dieselben Zahlen, andere
    Zeichen).
  - «Nicht führbar» steht überall gleich da: Striche statt Zahlen und der
    Grund als Hinweis – jetzt auch bei der Querkraft, beim Grundbruch «zu
    schräg» und bei Biegung mit Normalkraft ohne Schnitt mit der Linie (dort
    stand M_Ed = 0 statt der Einwirkung). Nur «ohne Bewehrung» zeigt weiter
    die Einwirkung neben dem Widerstand null.
  - Die Tabelle der Schubwände setzt den Grad wie überall
    (`grad_als_text`), und das Diagramm liest ihn aus dem Befund, statt ihn
    nachzurechnen.

---

## 2026-10-25 · Eine gewählte Last auf einer Linie bleibt beim Ändern gewählt

Gefunden beim Prüfen des Eintrags darunter: Wer im schwebenden Fenster den
Wert einer Last auf einer Linie änderte, verlor danach ihre Auswahl – das
Fenster ging nach jeder Eingabe zu.

- Nach jeder Änderung räumt das Zeichenfenster die Auswahl auf und fragte
  dafür nur sein Modell, ob es das Gewählte noch gibt. Eine Last auf einer
  Linie ist aber kein Element des Modells, sondern ein Anhang der App (seit
  2026-10-23); eine Last an einem Knoten ist beides und war darum nicht
  betroffen.
- Jetzt fragt es bei einem Anhang die App (`istAnhang`), wie es das beim
  Löschen und Verschieben schon tat.

---

## 2026-10-25 · Aufgeräumt: Doppeltes im Balkensystem, ein Weg zum Ändern

Befund 1.2 der Strukturdurchsicht vom 2026-10-25: Reste aus den Tagen davor.

- **`AUS_BAUTEIL`** statt `E_EQ_ARTEN` und `MIT_MATERIAL`: zwei Namen für
  dasselbe Tupel. Ein Querschnitt aus einer Platte oder Analyse bringt ein
  Material mit und hat ein E_eq – beides, weil er ein Bauteil mit Bewehrung
  nimmt.
- **Kein Umweg mehr über den Adapter:** `aktiverLastfall`, `lastfallWaehlen`
  und `passendeUebersicht` nehmen das Zeichenfenster `a` statt der Kennung
  und stehen mit `eintragVon` und `abdruckVon` in `bs_teile.js`. Das
  schwebende Fenster liest sie dort wie das Zeichenfenster; die drei Glieder
  des Adapters, die nur dafür da waren, sind weg.
- **`eintragAendern(liste, kennung, veraenderer)`** in `zustand.js`: dieselbe
  Funktion stand siebenmal da, als `aendernAn` oder `schreiben`, je App und
  im Balkensystem zweimal. Gibt es den Eintrag nicht mehr, ändert sich
  nichts – das tat bisher nur die Kopie in `python.js`, deren Speichern
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
  Platte – «das φ der Platte spielt keine Rolle» prüfte seit dem
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
- Unter den Eingaben steht damit kein Panel mehr, nur die Knöpfe – anders
  als noch beim Eintrag «vier Knöpfe mit Fenstern», wo die Statik-Analyse
  bewusst ein Panel blieb.

---

## 2026-10-24 · Aufgeräumt: das Zeichenfenster des Balkensystems in drei Dateien

Auftrag des Benutzers, nach dem Vorschlag im Bericht: `bs_zeichnung.js` war
über 1100 Zeilen lang.

- **`bs_eigenschaften.js`** (rund 460 Zeilen): das schwebende Fenster –
  was ein Werkzeug als Nächstes anlegt, die Felder von Knoten, Linien und
  Lasten, mehrere zugleich mit «Var».
- **`bs_teile.js`** (50 Zeilen): was Zeichnung, Fenster und Panels gemeinsam
  brauchen – Katalog, Lastart, die Last zu einer Kennung, die Zugseite
  einer Linie, der Name eines Materials.
- **`bs_zeichnung.js`** (rund 680 Zeilen): Fenster, Adapter, Lasten anlegen
  und treffen, Kern, Zeichnen.
- **Keine Abhängigkeit im Kreis:** das schwebende Fenster kennt vom
  Zeichenfenster nur `a`; was es vom System braucht – die Zeichnung, den
  Lastfall, die Übersicht des Kerns, das Umkehren –, gibt ihm der Adapter.
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
- Eine ältere Datei mit `querkraftbewehrung.stahl` öffnet sich nicht mehr –
  wie gewünscht.

---

## 2026-10-24 · Listen unter der Zeichnung zu Beginn zugeklappt

Wunsch des Benutzers: im Balkensystem die Liste der Linien und Lager zu
Beginn zugeklappt – in der Querschnittsanalyse ebenso die Flächen und die
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

Wunsch des Benutzers: im Balkensystem vier schöne Knöpfe – Material,
Querschnitt, Lastfälle, Lastkombinationen –, die je ein Fenster öffnen,
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
  Querschnitte» zurück – es gibt nur ein Fenster zugleich.
- Die Statik-Analyse bleibt ein Panel: sie sagt, welche Diagramme rechts
  stehen, und man ändert sie im Blick auf sie.

---

## 2026-10-24 · Balkensystem: mehrere zugleich ändern, mit «Var»

Wunsch des Benutzers: sind mehrere Elemente gewählt, ändert das Fenster
alle zugleich; was sie gemeinsam haben, steht da, sonst «Var» – auch bei
den Gelenken; eine Änderung gilt dann für alle.

- **Eine Regel:** `gemeinsam(werte)` gibt den gemeinsamen Wert oder `VAR`;
  `mitVar` setzt «Var» vor die Stellungen eines Schalters oder einer Liste,
  `zahlfeldMitVar` lässt das Feld leer mit «Var» darin. Gesetzt wurde schon
  vorher für alle – nur zeigte das Fenster die Werte des ersten.
- **Linien:** Querschnitt, Material, Zugseite, Gelenke, Bettung. «gemäss
  Querschnitt» steht nur, wenn jeder Querschnitt der gewählten Stäbe eines
  mitbringt.
- **Knoten:** x und z – eine getippte Lage gilt für alle, sie stehen
  danach in einer Flucht –, das Lager und je Richtung sein Halt; die
  Richtungen nur, wenn alle ein Lager haben.
- **Lasten:** der Lastfall immer, die Felder, wenn alle von derselben Art
  sind (bisher: «einzeln bearbeiten»).
- **Gelenke und «projiziert»** sind Schalter «ja | nein» statt Haken –
  ein Haken hätte kein «Var» zeigen können.

---

## 2026-10-24 · Platte: ein Stahl für alle Lagen

Wunsch des Benutzers: den Stahl nicht je Lage wählen, sondern einen für alle
Lagen, oben im Panel der Platte unter dem Beton.

- **Beschreibung:** `QuerschnittEintrag.stahl`; `LageEintrag` hat keinen
  Stahl mehr. Die Bügel behalten ihren eigenen – sie sind keine Lage.
- **Rechnung unverändert:** der Aufbau gibt jeder `Bewehrungslage` den Stahl
  der Platte; die Nachweise rechnen weiter je Lage mit ihrem Stahl, es ist
  nur immer derselbe. Ohne Stahl scheitert die Platte mit einer Meldung –
  vorher bekam eine leere Lage still den ersten Stahl des Projekts.
- **Tests:** der Index bei zwei Stählen kommt jetzt aus einer zweiten Platte
  mit dem zweiten Stahl. Die Prüfungen, dass in einer Platte mit B700B unten
  und B500B oben jede Lage mit ihrem Stahl rechnet (2026-10-12), sind weg –
  eine solche Platte lässt sich nicht mehr beschreiben. Geblieben ist die
  des Lösers, der je Seite den Stahl ihrer Lagen behält.

---

## 2026-10-24 · Balkensystem: E_eq auch aus einer Platte

Entscheid des Benutzers: E_eq gibt es auch für einen Querschnitt aus einer
Platte – immer in x-Richtung, Zug unten.

- **Eine Suche, zwei Quellen:** die Frage nach E_eq (`Modulfrage`) hat eine
  Quelle: `ModulAusAnalyse` – das Paar der Analyse zur Zugseite des
  Moments, wie bisher – oder `ModulAusPlatte`, das Paar der Platte in x
  (`loeserpaar`). Jede Quelle sagt, was sie liest (die Bezüge im
  Rechenwerk) und welches Paar gilt; Suche, Herleitung und E aus dem
  Befund sind dieselben.
- **Negatives Moment:** bei der Platte zieht es unten, nach Vorgabe; ein
  negatives M hat darum kein E_eq, und das System sagt es – still mit |M|
  zu rechnen, hiesse die Zahl umzudeuten.
- **Prüfprojekt:** der Deckenstreifen bekommt ein E_eq bei 20 kNm, ohne
  Stab – gesucht und hergeleitet wird es trotzdem, keine Zahl des Systems
  ändert sich.

---

## 2026-10-24 · Balkensystem: Querschnitte als Zeilen mit Bild und Fenster

Wunsch des Benutzers: jeder Querschnitt eine kompakte Zeile, links eine
Vorschau, A und I in der Zeile; ein neuer und ein Klick auf die Vorschau
öffnen ein Fenster, in dem man wählt, woher der Querschnitt kommt; die
Vorlage als Auswahlliste mit kleiner Vorschau.

- **Umriss vom Kern:** `balkendaten.umrisse` gibt je Querschnitt seine
  Polygone in mm – die Vorlage mit ihren Massen (`Stabvorlage.umriss`), den
  Streifen b × h einer Platte mit ihren gerechneten Werten, die Polygone
  einer Analyse samt Aussparungen; Kennwerte von Hand und ein Querschnitt,
  der nicht geht, keine. Die Antwort `rechnen` trägt sie als `stabumrisse`,
  auch wenn das System nicht rechnet. Die Oberfläche passt sie nur ins
  Bild; gezeichnet wird gerade-ungerade, so bleiben Löcher Löcher.
- **Zeile:** Bild (ein Knopf), Name, A und I vom Kern – ohne sie die
  Meldung des Kerns zum Querschnitt –, Herkunft mit Massen, «trägt».
- **Fenster:** das Fenster über der mittleren Spalte, wie bei den Kapiteln
  einer Platte (`fenster.js`, Schlüssel `querschnitt:Q1`); es wird mit dem
  Editor neu gezeichnet und zeigt darum immer den Stand. Darin die Felder,
  die vorher im Panel standen, die Vorlage als Auswahlliste mit Bild – auf
  Wunsch des Benutzers, in [[Arbeitsweise]] als Ausnahme vermerkt – und
  das E der Stäbe gemäss Querschnitt.
- **Nebenbei behoben:** wer «A und I aus» auf Kennwerte stellte, behielt
  die Masse der Vorlage, und der Kern meldete «einen Kennwert «b» gibt es
  nicht». Jetzt bekommt eine Vorlage ihre Vorgaben, Kennwerte beginnen leer.

---

## 2026-10-24 · Balkensystem: eigene Materialien als Tabelle

Wunsch des Benutzers: im Panel «Materialien» zuerst Materialien anlegen,
je Zeile eines – ein Beton des Projekts, dessen E und Dichte man nicht
ändern kann, oder ein Material mit E und Dichte von Hand; an der Linie nur
diese und «gemäss Querschnitt»; am Querschnitt kein E mehr, nur noch die
Wahl E₀ oder E_eq, wenn eine Linie sein Material nimmt.

- **Beschreibung:** das System hat `stabmaterialien`
  (`StabmaterialEintrag`, Kennung «M1»: `beton` mit Verweis auf einen Beton
  des Projekts oder `eigen` mit `E` und `rho`). Eine Linie zeigt auf eines
  davon oder auf «gemäss Querschnitt». `materialien()` – die Liste, die das
  Löschen im Projekt prüft – nennt die Betone, auf die ein Material zeigt.
- **Kein E am Querschnitt:** `E` und die Stellung «Zahl» sind weg; ein E von
  Hand hat jetzt ein eigenes Material. `e_modul` heisst `e0` oder `e_eq` und
  gilt nur für einen Stab mit dem Material des Querschnitts – mit einem
  Material des Systems nimmt er dessen E, auch bei einer Analyse.
- **Rechnung:** der Aufbau löst jedes Material zu einem `Stabmaterial` auf
  (Beton oder Zahlen von Hand); `Balkensystem` braucht keine Baustoffe mehr
  daneben. Ein eigenes Material schreibt E und ρ als Eingaben in die
  Herleitung, einmal je Material. Das Material des Querschnitts trägt im
  Zeichen keinen Index: es kann wie ein Material des Systems heissen.
- **Meldungen:** ein Material ohne Beton, eines, das auf Betonstahl zeigt,
  und eine Linie mit einem Material, das es nicht gibt, halten das System
  auf; ein Verweis auf einen Beton, den es nicht gibt, das Projekt – wie
  bisher bei Platte und Analyse.
- **Oberfläche:** die Tabelle mit Kopf (Material, Art, E, ρ, trägt); E und ρ
  eines Betons grau vom Kern. An der Linie die Materialien des Systems und
  «gemäss Querschnitt», wenn der Querschnitt eines mitbringt – und
  umgekehrt bei «gemäss Querschnitt» nur solche Querschnitte. Ein neues
  System bekommt den ersten Beton des Projekts; eine neue Linie das erste
  Material.
- **Beispiele:** im Prüfprojekt sind Stahl (E_s, ρ_s) und der weichere
  Fundamentbeton (E = 15000) eigene Materialien – jede Zahl des Berichts
  bleibt, nur die Namen wechseln.

---

## 2026-10-24 · Balkensystem: die Zugseite je Stab

Wunsch des Benutzers: je Stab festlegen, welche Seite die Zugseite ist;
von selbst unten, bei einer senkrechten Linie links, und umzuschalten.

- **Kein neues Feld:** die Zugseite ist die gestrichelte Faser, und die
  liegt schon immer rechts der Laufrichtung; «Umkehren» legte sie auf die
  andere Seite. Ein eigenes Feld hätte die Laufrichtung bedeutungslos
  gemacht, und jede Stelle, die die Faser zeichnet oder rechnet – Lasten
  quer, Linienlager, Diagramme, Herleitung –, hätte es kennen müssen.
- **Von selbst:** eine neu gezeichnete Linie läuft nach rechts, eine
  senkrechte nach unten – wie herum man sie auch zeichnet
  (`linieAnlegen`). Die Beispiele behalten ihre Richtung: im Rahmen liegt
  die Faser innen.
- **Schalter:** «Zugseite» im Fenster eines Stabs, mit den Stellungen unten
  | oben, bei einem senkrechten links | rechts. Er kehrt die Linie im Kern
  um, wie «Umkehren»: die Lasten bleiben, wo sie wirken – eine Last quer
  zum Stab wechselt dabei ihr Vorzeichen –, die Gelenke an ihren Knoten.
  Bei mehreren gewählten Linien steht er, solange alle senkrecht oder alle
  nicht senkrecht liegen.

---

## 2026-10-24 · Balkensystem: Verdrehung in der Statik-Analyse

Wunsch des Benutzers: neben der Verschiebung auch die Verdrehung.

- **Kern:** der Verlauf eines Stabs gibt je Stelle `phi`, die Verdrehung des
  Querschnitts – die Ableitung der Biegelinie, im Gegenuhrzeigersinn
  positiv, für jeden Stab gleich, wie er auch liegt. Die grössten Werte je
  Stab sucht `extrem("phi")` wie bei M: an den Enden und wo sich die
  Verdrehung nicht ändert.
- **Diagramm:** die Stellung «Verdrehung» im Schalter jeder Zeile; das Bild
  trägt φ in mrad auf wie einen Verlauf, bernsteinfarben, mit den Werten an
  den Enden und den grössten je Stab.
- **Geprüft:** am Einfeldträger unter q an den Lagern ±qL³/24EI, in der
  Mitte null.
- **Nebenbei:** der Rand um jedes Diagramm war für die grösste Ordinate
  und ihren Wert zu knapp – an einer äusseren Stütze stand «.67» statt
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
  hat – in em gemessen (sechs Zeichen JetBrains Mono zu 0.6 em); «6ch»
  löste sich im Rahmen schmaler auf als im Feld.
- **Lastfälle:** die Namen gleich breit untereinander – die Spalte daneben
  hat eine feste Breite, auch beim längeren Satz des Eigengewichts.
- **Liste unter der Zeichnung:** Linien, Lager und Lasten klappen je auf und
  zu; zu bleibt, was man zugeklappt hat (Ansicht, nicht Projekt).
- **Lagerkräfte lesbar:** die Regel `.bs-reaktion` färbte auch den weissen
  Rand der Zahlen grün; jetzt nur noch die Striche, und im Diagramm stehen
  die Zahlen so gross wie dessen übrige.

---

## 2026-10-24 · Querschnitt: verschmierte Linie aus ⌀, Teilung und Länge

Wunsch des Benutzers: bei verschmierter Bewehrung entweder die Stahlfläche
eingeben oder Durchmesser, Teilung und Länge – daraus L/s · π⌀²/4, und die
Fläche steht grau darunter.

- **Beschreibung:** an der Stablinie `verschmiert` (`flaeche` | `staebe`,
  `VERSCHMIERT` in `querschnitt/geometrie.py`) und `laenge` (leer: die der
  Linie). ⌀ und s sind die Felder, die die Linie nach Teilung auch hat –
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
  Suche nach dem Fliessbeginn auf eine Stelle ohne Gleichgewicht fiel – sie
  hielt «keine Ebene» für «fliesst noch nicht» (`linie.py`). Getroffen hat
  es der Kastenträger des Prüfprojekts mit der neuen Linie; ohne sie ändert
  die Korrektur keine Zahl.

---

## 2026-10-24 · Querschnitt: Materialien pastell

Wunsch des Benutzers: im gezeichneten Querschnitt Beton pastellgrün,
Betonstahl pastellrot, Schubwände pastellgelb, Baustahl pastellblau – den
es noch nicht gibt.

- Eigene Farbmarken je Material, eine helle Fläche und eine kräftigere
  Linie (`--mat-beton`, `--mat-stahl`, `--mat-wand`, `--mat-baustahl`, je
  mit `-linie`). `--beton` und `--stahl` bleiben: sie färben auch die Köpfe
  der Tafeln, und die sollen nicht grün und rot werden.
- Gilt für Zeichnung und Vorlagen des Querschnitts, die Schraffur der
  Zellen (gelb wie die Wände) und die Zeilen «Rechenwerte je Material» –
  dort steht dasselbe Material in derselben Farbe.

---

## 2026-10-24 · Balkensystem: E_eq der Querschnittsanalyse bei N und M

Letzte Etappe des neuen Balkensystems. Entschieden (Rückfrage): E₀ ist E_cm
– das gibt «vom Material» schon, eine eigene Stellung braucht es nicht;
N und M stehen am Querschnitt; ein E für EA und EI.

- **Beschreibung:** dritte Stellung `e_eq` am Querschnitt, nur bei einer
  Analyse (`E_EQ_ARTEN`); dazu `eq` mit N, M und den Rechenwerten einer
  Spannung-Dehnung-Analyse (φ, Werte, Rechenart).
- **Gerechnet im Rechenwerk**, nicht in der Auswertung danach – es geht in
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
Statik-Analyse, in der man Diagramme anlegt – je Zeile ein Lastfall oder
eine Kombination (Auswahlliste) und M, V, N oder die Verschiebungen. In den
Diagrammen die grössten Werte angeschrieben, und wo sie liegen. Der Knopf
heisst «+ Diagramm», nicht «+ Bild» – auch in der Spannung-Dehnung-Analyse
von Platte und Querschnitt (eigener Commit).

- **Beschreibung:** `diagramme` am System, je Eintrag `fall` (Kennung von
  Lastfall oder Kombination) und `groesse` (`DIAGRAMMGROESSEN`). Gerechnet
  wird damit nichts – das System rechnet jeden Fall; die Liste sagt nur,
  welche Diagramme rechts stehen. Ein neues System bringt M, V, N der GZT
  und die Verschiebung der GZG mit. Die Bilder nur je Kombination (vorige
  Etappe) sind damit wieder offen: die Zeile wählt.
- **Lager dazu:** die Lagerkräfte hatten ein eigenes Bild; sie sind eine
  fünfte Stellung des Schalters, damit nichts verloren geht. Der Benutzer
  nannte nur M, V, N und Verschiebung – fällt die Stellung weg, ist es eine
  Zeile in `DIAGRAMMGROESSEN`.
- **Angeschrieben:** die Werte an den Enden und je Stab der grösste und der
  kleinste, mit einem Punkt; im Feld darunter die Stelle «x = …». Die
  Extremwerte kommen genau vom Kern (`uebersicht.faelle[].staebe`), nicht
  aus den 24 Proben je Stab. Bei der Verschiebung je Stab die grösste
  Durchbiegung gegen die Sehne – ein Stab, der sich nur mitbewegt, bleibt
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
  Material des Projekts E-Modul und Dichte – die Kennwerte, mit denen ein
  Stab rechnet. Welche das sind, sagt der Katalog (`kennwerte`, aus
  `E_MODUL` und `DICHTE` in `stabwerk/rechnung.py`). Die Zeilen sind die der
  App «Materialien» (`kennwertZeile` aus `material.js`): bei einer Normsorte
  gesperrt, bei einem eigenen Material hier wie dort zu ändern – eine Regel,
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
  mit – nach Vorlage, von Hand, eine leere Analyse, zwei Betone –, sagt es
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
  einer – zwei sind eine Meldung am System. Er lässt sich umbenennen, nicht
  löschen; eigene Lasten darf er zusätzlich haben.
- **Gerechnet im Kern:** je Paar aus Querschnitt und Material eine Formel
  `g_k = ρ · g · A` (Formelsammlung «Eigengewicht eines Stabs»), beim Beton
  mit ρ_sb, ohne den Stahl noch dazu. Vor dem Lösen kommt je tragenden Stab
  eine Linienlast senkrecht über die ganze Länge in den Lastfall, je Meter
  Stab, nicht projiziert. So steht sie in der Herleitung wie jede andere Last,
  und Kombinationen nehmen sie mit ihrem Faktor.
- **Gezeigt:** der Befund gibt das Eigengewicht je Stab mit
  (`Systembefund.eigengewicht`), die Übersicht in kN/m. Das Zeichenfenster
  zeichnet es grau im Lastfall, der es bekommt – nicht zu wählen, nicht zu
  löschen. Die Übersicht fragt neu, wenn sich ein Material oder eine
  genommene Platte oder Analyse ändert, nicht nur die Zeichnung: sonst
  stünde nach einer neuen Dichte das alte g_k da. Wovon eine Antwort des
  Kerns abhängt, steht einmal (`abdruckVon` in `bs_zeichnung.js`) und gilt
  für Zeichenfenster und Diagramme – vorher hatte jedes seine eigene Regel,
  die des Fensters enger. Gefragt wird bei jedem Neubau der Tafel; ist der
  Abdruck derselbe, bleibt es bei der letzten Antwort.
- **Bilder nur je Kombination:** die Wahl über den Bildern zeigt nur
  Kombinationen; ohne eine sagt ein Satz, wo man sie anlegt. Gerechnet
  werden die Lastfälle weiter – die Kombinationen setzen sich aus ihnen
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
  Balkensystem öffnen sich nicht mehr – das Programm legt sie beiseite.
- **Gespeichert an der Linie:** die Lasten bleiben in `linie.lasten`. So
  gehen sie mit ihr beim Kopieren, Teilen, Löschen und Rückgängig – wie
  bisher, ohne Pflege an zwei Stellen.
- **Anhänge im Zeichenfenster:** was eine App an Elemente hängt und selbst
  zeichnet, lässt sich wählen und löschen (`adapter.anhaenge`: `treffer`,
  `hat`, `loeschen`, `rahmen`), aber nicht verschieben oder kopieren – eine
  Last am Knoten nähme sonst den Knoten mit. Ein Werkzeug der Form «anhang»
  legt an, wo geklickt wird (`anhangBefehl`, `anhangAnlegen`).
- **Treffen:** jedes Lastzeichen trägt seine Formen mit (`formen` in
  `bs_symbole.js`): das Band einer verteilten Last ohne den Streifen an der
  Linie, den Schaft eines Pfeils ohne die Spitze, den Bogen eines Moments,
  dazu die Zahl. So trifft ein Klick auf den Balken den Balken.
- **Fenster:** Linie – Querschnitt («– kein Stab –»), Material, Gelenke,
  «▸ Bettung». Knoten – Lage und Lager. Last – Lastfall, Richtung, Wert,
  Stelle, projiziert. Werkzeug «Last» Q – dazu die Art als Schalter. Unter
  der Zeichnung eine Liste der Lasten; ein Klick wählt die Last und zeigt
  ihren Lastfall.

---

## 2026-10-23 · Dichte bei Beton und Stahl

Erste Etappe des neuen Balkensystems (Wunsch des Benutzers): das
Eigengewicht soll aus der Dichte des Materials kommen. Neue Kennwerte mit
Vorgabe, wie γ_c – keine Normstelle, die Zahlen hat der Benutzer genannt:

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

- **Bewehrungsmass** μ_s = A_s,tot · 7850 kg/m³ / A – Längsbewehrung ohne
  Bügel, wie bei der Platte.
- **Je Zugseite M_Rd bei N_Ed = 0** – unten, oben, links, rechts, einachsig
  nur unten und oben; Zug oben und rechts negativ wie M_Rd⁻ der Platte.
  Derselbe Bruchzustand wie bei Duktilität und sprödem Versagen
  (`bei_reiner_biegung`), mit der Rechenwahl der Tragsicherheit – die
  Platte nimmt dafür immer die Handrechnung mit Bemessungswerten.
- **N_Rd⁺ und N_Rd⁻ bei gleichmässiger Dehnung**: die Grenzen, gegen die der
  M-N-Nachweis reine Normalkraft hält. Bei der Platte heissen sie «bei
  M_Ed = 0»; an einem unsymmetrischen Querschnitt ist das nicht dasselbe.
- **x/d je Zugseite mit Bewehrung**, wie im Nachweis der Duktilität. Ob eine
  Seite Bewehrung hat, entscheidet die Zeichnung (Stäbe jenseits des
  Schwerpunkts) – welche Kennzahlen es gibt, muss vor dem Rechnen
  feststehen.
- **Mit Schubwänden V_z,Rd, V_y,Rd und T_Rd**, je allein und ohne
  Normalkraft: die Verteilung ist linear, also trägt jede Wand v_Rd/q₁ der
  Last, wenn q₁ ihr Fluss je Einheitslast ist; massgebend die kleinste. Was
  die Wände nicht tragen können – V_y bei lauter senkrechten Wänden, T ohne
  Zelle –, steht nicht da. Ein Test hält V_z,Rd und T_Rd gegen den Nachweis
  der Schubwände: mit ihnen als Last ist er gerade erfüllt.
- **Nicht übernommen:** Distanzhalter und Vergrösserungsfaktor gehören den
  Lagen und dem Verformungsnachweis der Platte; der Querkraftwiderstand ohne
  Bügel ihrer Rechnung je Meter.

Aufgeräumt dabei: die Festigkeiten einer Wand und die Neigungsgrenzen
stehen jetzt in der Analyse (`schubwaende_mit`, `neigungsgrenzen`) statt im
Nachweis der Schubwände – die Kennzahlen brauchen sie auch. Und der
Durchmesser einer verschmierten Linie bei s = 150 mm stand nach dem Einbau
der Überdeckung zweimal da: in `stabgrenzen.py` (fiktiver Durchmesser der
Stahlspannung, seit 2026-10-15) und in `geometrie.py`. Jetzt nur noch in
`geometrie.aequivalenter_durchmesser`; `fiktiver_durchmesser` ruft sie.

---

## 2026-10-23 · Überdeckung: ein Hilfspolygon und «Überdeckung beachten»

Wunsch des Benutzers: beim Polygon eine Überdeckung in mm eingeben können,
Vorgabe 0. Darüber erscheint ein Hilfspolygon, so weit nach innen gerückt,
an dessen Ecken man fängt – um Bewehrung einfach zu zeichnen. Und gewählte
Bewehrung soll sich auf Knopfdruck so verschieben, dass sie mit ihrem eigenen
Radius gerade ganz in diesem Polygon liegt; eine verschmierte Linie gilt
dafür als Stäbe mit dem äquivalenten Durchmesser bei s = 150 mm.

- **Gerechnet im Kern**, nicht in der Oberfläche: die Stablagen gehen in die
  Rechnung. `geometrie.py` rückt ein Polygon (`versetzt`: jede Kante um c,
  Ecken, wo sich die gerückten Kanten schneiden – auch an einer
  einspringenden Ecke spitz; eine Kante, die sich umkehrt, fällt weg) und
  sagt, wohin ein Stab oder die Enden einer Linie müssen
  (`stab_in_ueberdeckung`, `linie_in_ueberdeckung`). Die Antwort `geometrie`
  trägt je Polygon das Hilfspolygon und je Stab und Linie die Lage
  `ueberdeckt`; der Knopf übernimmt sie nur.
- **Wohin:** auf den nächsten Punkt, an dem der Stab gerade ganz innen liegt
  – ein ⌀20 aus der Ecke des Rechtecks mit c = 30 nach (40, 40); was schon
  innen liegt, bleibt. Jedes Ende einer Linie für sich; sind zwei Ränder
  gleich nah (an einer einspringenden Ecke), quer zur Linie.
- **Welches Polygon:** eines mit Beton nur für das, was in ihm liegt;
  sonst das nächste. Eine Aussparung mit c rückt nach aussen und schiebt
  Bewehrung aus sich hinaus – so hat ein Hohlkasten auch innen seine
  Überdeckung. Gerückt wird jede Kante, auch die Fuge zu einem Nachbarn: wer
  einen Querschnitt aus mehreren Polygonen zeichnet, gibt c dem, an dessen
  Rand sie gilt.
- **Verschmiert:** der Durchmesser hängt an der Länge, und die ändert sich
  beim Verschieben. Gerechnet wird, bis beide zueinander passen – ein
  zweiter Klick verschiebt nichts mehr.
- Was am selben Knoten hängt – eine Polygonecke unter dem Ende einer
  Linie –, bleibt liegen (`verschieben` je Ecke).

---

## 2026-10-23 · Das offene Polygon fängt an seinen eigenen Ecken

Wunsch des Benutzers: beim Zeichnen eines Polygons sollen nicht nur die
Knoten fangen, die es schon gibt, sondern auch die Ecken, die das Polygon
selbst schon hat. Bis jetzt waren sie keine Knoten der Zeichnung – das
werden sie erst beim Schliessen – und fingen darum nicht.

Ein Befehl kann jetzt `fangpunkte()` haben: was er schon gesetzt hat. Das
Fangen (`cad_eingabe.js`) nimmt diese Punkte wie Knoten, mit demselben
Quadrat; auf eine Bindung (Y, Z, P, S) werden sie projiziert wie jeder
Punkt. Das Polygon gibt seine Ecken – die erste gefangen schliesst es wie
bisher.

---

## 2026-10-23 · Einheit neben den Koordinaten, Fenster hält die Oberkante

Zwei Wünsche des Benutzers zum schwebenden Fenster:

- **Rechts neben jedem Koordinatenfeld die Einheit** – im Querschnitt mm,
  im Balkensystem m, denn dessen Koordinaten sind Meter; beim Winkel °. Sie
  kommt aus `feldeinheiten` neben `feldnamen` (`cad_eingabe.js`), aus der
  Einheit der App. Das Winkelfeld heisst darum nur noch «α». Auch die Lage
  des Zeigers in der Ruhe trägt die Einheit. Die Felder sind dafür 7 statt 8
  Zeichen breit, sonst passte die Zeile nicht ins Fenster.
- **Die Oberkante bleibt stehen**, wenn der Inhalt wechselt – etwa beim
  Umschalten der Bewehrung zwischen Linie und Punkt. Bisher hing das Fenster
  an seiner Unterkante. Gemerkt wird jetzt der Abstand von oben rechts, und
  es steht anfangs oben rechts. Reicht es über den unteren Rand, rückt es
  hinauf, bis es ganz zu sehen ist, und kehrt zurück, wenn es schrumpft.
  «Alles zeigen» hält darum oben oder unten frei, je nachdem, wo es steht
  (`einpassen` nimmt `frei` als `{rechts, oben, unten}`).

---

## 2026-10-23 · Die übrigen festen Listen werden Schalter

Wunsch des Benutzers, nach der Empfehlung: jede feste Wahl als Schalter. Eine
Wahl aus dem eigenen Projekt – Lastfall, Querschnitt, Platte oder Analyse,
Fall der Diagramme, Kombination des Grundbruchs – bleibt eine Liste wie die
Materialwahl: ihre Zahl wächst mit dem Projekt, als Knöpfe würde sie zu breit.

- **Nachweise:** Rissanforderung; Werte und Rechenart der Rechenwahl stehen
  jetzt untereinander – nebeneinander fanden «Bemessung | charakteristisch»
  und vier Rechenarten keinen Platz. In der Zeile einer Analyse ebenso.
- **Querschnittsanalyse:** Werkstoffsatz und Betongesetz je Material, der
  Beton mit dem Gesetz in einer zweiten Zeile. Die Zugseite als Pfeile
  ↓ ↑ ← → (`Zugseite.pfeil` im Kern), «Zug unten» im Titel: vier Wörter
  passten nicht in die 80 px der Analysezeile. Die Achsen des
  Interaktionsdiagramms; der Modus der Bewehrungssuche untereinander.
- **Balkensystem:** «A und I aus» mit kurzen Namen (`kurz` im Katalog) unter
  dem Namen des Querschnitts, die Vorlage mit Umbruch; im schwebenden Fenster
  Lager, Halt je Richtung, Linienlager und Lastrichtung. Haben gewählte
  Knoten verschiedene Lager, steht keine Stellung an – vorher hiess das
  «verschieden».

Neu dafür in `bausteine.js`: `wahlBlock` – ein Schalter unter seiner
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
  gehört – im Balkensystem zeichnet man einen Rahmen damit Stab für Stab.
- **Esc wie die Rücktaste**, auch bei der Linie: ein gesetzter Anfangspunkt
  geht zurück, erst ohne ihn endet das Werkzeug.
- **Keine Auswahllisten ausser für die Materialwahl** – als Grundsatz in
  [[Arbeitsweise]]. Im Zeichenfenster sind die Verteilung der Bewehrung
  (verschmiert, Anzahl, Teilung) und das Raster nun Schalter, die Schnitte
  einer Schubwand ein Zahlenfeld; die Steifigkeit der Setzung ein Schalter.
  Dafür gibt es `wahlSchalter` in `bausteine.js`. Die übrigen Listen stehen
  im [[TODO]], dazu die Frage, ob eine Wahl aus dem eigenen Projekt – ein
  Lastfall, ein Querschnitt – eine Liste bleiben darf wie die Materialwahl.

Beim Prüfen fiel auf: das schwebende Fenster der Bewehrung ist mit allen
Feldern fast 400 px hoch und deckt im schmalen Panel die halbe Zeichnung –
ein Klick dorthin setzt keinen Punkt. Zuklappen geht (–), verschieben am Kopf.

---

## 2026-10-23 · Fangen sichtbar, Esc im Polygon

Zwei Meldungen des Benutzers:

- **«Das Fangen von Punkten scheint nicht mehr zu gehen»** – etwa beim
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
Balkensystem, sondern je Art ein eigener Knopf mit Zeichen – Bewehrung (als
Linie oder als Punkt), Schubwand, Hilfspunkt, Hilfslinie –, und in einem
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
  Punkt – ihre Form ist eine Funktion des Werkzeugs, und der Schalter «Linie
  | Punkt» in ihrem Fenster startet es mit der anderen Form neu.
- **Ein Fenster, eine Art.** Die Felder «Art» beim Neuen und beim Gewählten
  sind weg, mit ihnen der Wechsel einer gezeichneten Linie in eine andere Art
  samt dem Gedächtnis dafür. Die Titel sagen, was es ist: «Linie 1 ·
  Linienbewehrung», «Stab 1 · Punktbewehrung».
- **Zeichen statt Schriftzeichen.** Die Knöpfe tragen Sinnbilder
  (sinnbilder.js), die Werkzeuge das Zeichen über dem Wort. Rückgängig,
  Wiederholen, Alles zeigen und Vollbild stehen klein zu zweit übereinander,
  nur als Zeichen – so passt die Leiste in eine Zeile, auch im 500 px
  schmalen Panel.

---

## 2026-10-23 · Die App «Setzung»

Wunsch des Benutzers: eine Setzungsberechnung im Stil des Grundbruchs, mit
Bild der Situation – Breite und Länge des Fundaments, Pressung aus
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
  ergibt 20.5 mm aus dem Ton – das Kapitel nennt 2.1 cm. Steht im
  [[TODO]].
- **Wie der Grundbruch gebaut:** `geotechnik/setzung.py` (Fundament als
  Vorgaben, Nachweis, Befund), `projekt/setzung.py` (Eintrag, Schichten),
  `projekt/aufbau/setzung.py`, eine neue Bauteilart `SETZUNG` mit Vorsilbe
  `w` – `s` tragen die Betonstähle. Die Oberfläche: `setzung.js` und
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
  flacher als 200 px – dann überhöht, und die Legende sagt, wie stark.
- **Eine Schicht hat keinen Schalter.** Ausgeschaltet hätten die Schichten
  darunter nach oben rücken müssen; die Zeile trägt statt des Schalters ihre
  Nummer (`fallzeile({vorn})`). Die Namen müssen nicht verschieden sein –
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
  und des gezeichneten Querschnitts – Tragsicherheit, Rissnachweise,
  Knicken, dazu Verformung und Analysen – sind Kräfte, Momente und die
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
  eines Materials ist immer ein eigenes – BE2, S3 … nach der Sorte des
  Originals und mit seinen Abweichungen –, denn eine Normsorte gibt es im
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
weiter – der Benutzer hat sie nicht genannt; offen, ob sie folgen soll.

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
  CAD-Fenster eine Ziffer ins erste Feld schickt – sie ersetzt dann, was
  dort stand – und wenn die Seite nach dem Neuzeichnen den Fokus zurückgibt.
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
  – vorher lief er durch elf Signaturen.
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
  Feld lehnt eine Kommazahl sichtbar ab – vorher rundete die Oberfläche
  37.5° still auf 38°.
- **Teilung und Stabzahl bleiben beide stehen**, `art` sagt, welche gilt –
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
  des Kerns zur Zeichnung – die letzte JS-Kopie von «wer braucht welches
  Material».

## 2026-10-18 · Löser und Kennzahlen

Phase 4 des Umbaus aus der Durchsicht vom 2026-10-16, in zehn Commits.
Zahlen bewegen sich nur, wo der Benutzer es entschieden hat – beim
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
  Stahlspannung den Beton fest bis 3 ‰ – bei einem Beton mit ε_c2d unter
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
Zahlen ändern sich nur, wo der Benutzer es entschieden hat – bei den
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
  Der Preis: eine gekippte Linie dauert etwa dreimal so lang – angenommen,
  schneller in Phase 4. Unterwegs behoben: Stäbe gleicher Tiefe verloren
  als Lage ihren Arm entlang der Nulllinie, und `illinois` rechnete mit
  `nan` weiter.
- **Ein Nachweis, zwei Anschlüsse.** Die Stahlspannung misst an Stellen –
  Lagen oder Stäbe –, was die Geometrie beiträgt, sagt ein schmaler
  Anschluss (`Stahlspannungsort`: `PlattenStellen`, `AnalyseStellen`);
  `SpannungsbegrenzungQA` mit seinem kopierten Urteil fällt weg. Bei der
  Zwängung auf Biegung teilen beide nur Name, Thema und Einleitung
  (`Biegezwang`): die Platte rechnet von Hand mit d − x/3, der gezeichnete
  Querschnitt sucht – ein gemeinsamer Nachweis hätte fast nur
  weitergereicht (Benutzer, 2026-10-17).
- **Die Beschreibung und die Maske einmal.** Zwölf Felder, die beide gleich
  angeben, stehen in `Querschnittsangaben`. Die Oberfläche baut die sechs
  gemeinsamen Kapitel mit `nachweisKapitel(ort)`: eine Schalterzeile, die
  Fragezeichen am Kapitel, das Gemeinsame der Hilfe einmal. Was das
  Bauteil anders zeigt, sagt sein Ort (`PLATTE`, `ORT`).
- **Dateien.** `projekt/aufbau.py` wird ein Paket – ein Kern und je
  Bauteilart ein Modul –, `nachweise.js` teilt sich nach Abnehmern
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
  muss, steht an ihrem Feld – `bereich(300.0, heisst="Dicke h",
  einheit=MM, ueber=0.0)`; was mehrere Felder betrifft, in `regeln(wo)` des
  Eintrags. Beides prüft `inhalt_pruefen` vor jedem Rechnen über das ganze
  Projekt, mit dem Ort am Feld. Warum: geprüft wurde zu drei Zeitpunkten
  ohne Regel – ein Anteil null hielt das Öffnen auf, eine Dicke null erst
  das Rechnen, eine negative Kriechzahl das Lesen, eine negative Überdeckung
  das Bauen –, dazu in fünf Formen von `pruefen`. Ein abgelegter Stand mit
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
  Beispiel und meldete «Nicht gelöscht» – die erste Änderung überschrieb
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
  schreibt seine Formel aus denselben Ästen – samt «0 jenseits der
  Bruchstauchung». Neu die Formelseite «Beton linear, ohne Zug».
- **Jenseits der Grenze null, auf ihr um eine Rundung** (`RUNDUNG`,
  1e-12). Der Löser hielt die Grenze hart, die genaue Resistenzlinie gar
  nicht (Schalter `bricht`): eine Lage genau auf ε_ud kippte an der letzten
  Stelle auf null. Jetzt eine Formel je Gesetz.
- **Die Querschnittsanalyse baut ihren Beton wie die Platte**
  (`rechenwahl.betongesetz`). Der Beiwert der Parabel kommt aus E_cm statt
  aus dem E_cd des Materials – bei γ_cE = 1 dieselbe Zahl – und steht
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
  Material muss es geben, und es muss von seiner Art sein – ein Stahl ist
  kein Beton. Nur eine leere Lage behält den Ersatz: sie trägt nichts.
- **Zahlen, die erst das Rechnen braucht** (`zahlen_pruefen`, vorher
  `masse_pruefen`): ein Posten mit Durchmesser braucht eine Teilung oder
  Stabzahl grösser null, eine Knicklänge grösser null; die Analyse prüft
  α, k_c und x/d wie die Platte, über dieselben Funktionen
  (`neigungen_pruefen`, `druckfeld_pruefen`, `x_d_max_pruefen`).
- **Kennungen eindeutig** – im Projekt über alle Arten (ein zweites `b1`
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
jede Klasse ihre Datei von Hand – 39 Leser, jeder mit eigenen Vorgaben,
Prüfungen und alten Formaten –, und die Fassade ging an ihnen vorbei. Ein
`quer="festt"` aus Python wurde still zur Bettung; eine Rissanforderung mit
Tippfehler zur mildesten Stufe, ohne x-Bewehrung ganz ohne Meldung.

- **Ein Leser** (`lesen.lesen`) für alle Einträge, aus den Feldern der
  Datenklassen. Streng: ein Feld, das es nicht gibt, meldet sich mit dem
  ähnlichsten («Gemeint ist vielleicht 'rissanforderung'?»), ein Text ist
  keine Zahl, `"false"` kein Schalter, 35.7 keine ganze Zahl – abgeschnitten
  wird nichts. Was fehlt, bekommt die Vorgabe: bei einem Eintrag in einem
  Eintrag die eines frischen an dieser Stelle, so rechnet eine teilweise
  angegebene Rechenwahl des Knickens wie ihr Kapitel.
- **Eine Prüfung** (`lesen.felder_pruefen`) für jedes Feld, aus dem, was an
  ihm steht: Typ, Wahl (`einer_von`), Untergrenze (`nicht_negativ`), Pflicht
  – ein Text ohne Vorgabe darf nicht leer sein. Sie läuft beim Lesen und
  vor jedem Rechnen über das ganze Projekt (`Projekt.pruefen`): was in
  Python gebaut wurde, geht durch dieselbe Tür wie eine Datei.
- **Der Ort steht in jeder Meldung** so, wie die Oberfläche ihn nennt:
  «Platte 'Decke', lagen 2, grund: 'abstand' muss eine Zahl sein». Bauteile
  und Materialien tragen dafür eine `BEZEICHNUNG`.
- **Alte Formate weg** – seit 2026-10-11 erlaubt: vier Lagen aus
  `lagen_unten`, flache Gebrauchslisten, Schalterlisten je Lage, `richtung`
  an Lastfällen, `betongesetz`, die Kriechzahl der Platte für jedes Kapitel,
  Analysen mit eigenen Koordinaten, die Kette `ERSATZ_ALTER_WAHL`. Mit der
  Kriechzahl der Platte ging ein stiller Fehler: fehlte in einer Platte ein
  φ, galt 2.0 statt 0. Der Schnappschuss «altformat» ist weg, seine drei
  Querschnitte stehen in den beiden anderen.
- Am 2026-09-26 blieben die Leser von Hand, weil Altformate und Prüfungen
  darin standen («ein Wächter statt eines generischen Lesers»). Die
  Altformate sind weg, die Prüfungen stehen an den Feldern – der Grund ist
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
übereinstimmen – ein eigener Stahl neben B500B hat die Kennung `s2` und
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
gleich ob Nachweise gewählt sind – ω_w und ω_w', M_Rd± bei N_Ed = 0, N_Rd±
bei M_Ed = 0, x/d aus der Handrechnung, V_Rd,max und V_Rd,min ohne Bügel
(je das Kleinere beider Seiten) und V_Rd(α_opt) mit Bügeln.

- **`Plattenkennzahlen`** (`nachweis/kennzahlen.py`), eine Prozedur je
  Platte mit x-Bewehrung, Rechenziel der Platte nach ihren Nachweisen.
  Rechnet die Tragsicherheit von Hand mit Bemessungswerten, liest sie deren
  Linie aus dem Befund – dasselbe Muster wie das Knicken –, sonst eine
  eigene mit Herleitung. N_Rd bei M = 0 sucht `kante` auf der Linie;
  `protokoll_treffer` nimmt dafür jetzt den Wert mit, unter dem das Ergebnis
  weitergeht, statt eines allgemeinen N_Rd.
- **Querkraft:** k_g und die Teilung in y sind Funktionen
  (`beiwert_k_g`, `buegelteilung_y`), die Nachweis und Kennzahlen teilen;
  der Widerstand kommt aus `widerstand` und `neigungen`. Bei M_Ed = M_Rd ist
  ε_v = f_yd/E_s, gleich wie gross M_Rd ist – die «Fliessdehnung».
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
  verkleinerte Kopie des Bildes, kein eigenes Bild – ein zweiter Weg, die
  Diagramme zu zeichnen, liefe auseinander. Ein Diagramm ist jede Karte mit
  einem Bild; die übrigen Karten eines Bauteils (Wahl des Falls, Hinweise)
  stehen über dem gewählten.
- **Materialien:** «+» öffnet ein Fenster: Normsorte nach SIA oder eigenes
  Material mit einer Sorte als Vorlage. Eine Normsorte bleibt, wie sie ist
  – «Material modifizieren» und die Wahl der Sorte sind weg; links trägt
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
  Tabelle der Faktoren wie im Bild des Benutzers – drei Spaltenpaare
  Kohäsion, seitliche Auflast, Gewicht Gleitkörper; Zeilen N, s, d, i (je
  Kombination), g, b'. `angaben()` braucht dafür die Lösung: die Faktoren
  stehen erst nach dem Rechnen fest.
- **Bild der Situation** (Reiter Diagramme): wie Bild 9.2.15, die Bruchseite
  links. Die Masse kommen aus dem Eintrag, der Umriss des Gleitkörpers aus dem
  Kern (`gleitkoerper()`, Prandtl: Keil, Spirale, Keil – trifft L und H der
  Formeln). Er ist für waagrechtes Gelände gerechnet und endet im Bild, wo er
  aus einem geneigten Gelände tritt. Die Kräfte stehen im Verhältnis
  zueinander, die grösste immer gleich lang; gezeigt wird die massgebende
  Kombination oder die gewählte.
- **Formelsammlung:** eine Seite sammelt jetzt jede Normstelle, unter der
  ihre Formel vorkommt, nicht nur die der ersten Fassung – σ_v0 = γ t + q
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
  eine Stabilitätsberechnung – gerechnet wird mit γ' wie in Lage 2.
- Eine Klammer eines Lastneigungsfaktors unter null gilt null; i_c bleibt,
  wie die Formel es ergibt (auch negativ, wie in der Tabelle des Benutzers).
- δ*/φ ist ein eigenes Feld, Vorgabe 1 – das Kapitel nennt 2/3 φ bis φ.
- L ≥ b wird verlangt: b ist die kürzere Seite.
- Kein globaler Sicherheitsfaktor F wie im Kapitel: die Sicherheit steckt in
  γ_φ und γ_c.

---

## 2026-10-16 · Rechte Tafel wie die mittlere; Spannung-Dehnung als Diagramme

Die rechte Tafel sieht jetzt aus wie die mittlere (Benutzer): je Bauteil ein
graues Panel, darin weisse Karten mit blauer Kante – dieselben `panel` und
`karte` aus `bausteine.js`, also auch derselbe Kopf zum Zuklappen.

- **Zusammenfassung:** je Bauteil ein Panel mit den Karten Angaben,
  Bewehrung, Nachweise, Kennzahlen. Die Tabelle der Nachweise ist immer
  660 px breit (`--tabellenbreite`), sie skaliert nicht mehr mit der Tafel;
  breiter wird sie nur, wo ihr Inhalt es verlangt. Das Panel ist so breit,
  dass sie hineinpasst (`--berichtbreite`, 704 px) – in der Tafel von 750 px,
  die ein Bildschirm von 1536 px ergibt, ohne Rollen. Dafür wurde sie etwas
  kleiner gesetzt (12.5 statt 13 px, knappere Zellen).
- **Diagramme:** je Bauteil ein Panel, je Diagramm eine Karte; die Wahl
  «nebeneinander» stellt die Karten im Panel nebeneinander, statt ganzer
  Blätter. Die Werkstoffgesetze stehen zusammen in einem Panel.
- **Herleitung:** je Bestandteil ein Panel, je Kapitel – Titel der Ebene 2
  – eine Karte.
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

- **ω_w ist die Formel, die schon da war** – w/w_c nach SIA 262:2025,
  4.4.3.2.5, mit ρ der gezogenen und ρ′ der Gegenseite. Sie stand bei den
  Bewehrungslagen und rechnete mit dem φ der Platte; jetzt gehört sie dem
  Nachweis (`nachweis/verformung.py`), und die Zahlen sind dieselben (4.00
  unten, 7.52 oben im Beispiel).
- **Je Fall eine Zugseite**, Vorgabe unten. Der Faktor hängt an der Seite,
  die gezogen wird; ein Kragarm zieht oben. Gerechnet wird er je Seite, die
  ein Fall verlangt, einmal für die Platte – nicht je Fall. Der Benutzer hat
  die Frage nach der Seite mit der Formel beantwortet; die Zugseite je Fall
  ist meine Folgerung daraus (ρ ist das der gezogenen Seite). Ohne x-Bewehrung
  auf der gezogenen Seite gibt es keinen Faktor: der Fall steht mit Grad null
  und dem Grund in der Tabelle.
- **Nach Vorgabe, nicht nachgeschlagen:** L/350 und «w mit E_cm» (siehe
  [[TODO]]). Die Herleitung sagt es als Annahme.
- **Eine alte Datei** bringt ihr φ der Platte als φ der Verformung mit. w und
  L prüft erst das Rechnen, wie die Masse der Platte: eine abgelegte Platte
  mit L = 0 lässt sich öffnen und korrigieren.
- Unter der Tabelle steht ω_w je gezogene Seite, wie vorher w/w_c – jetzt
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
und Konsole, rechts statt der Berechnung die Variablen – wie in Spyder. Die
Entscheide des Benutzers: reines Python, ohne das offene Projekt im
Namensraum (`import opencivil` geht trotzdem); mehrere Skripte, eine Sitzung
für alle; die Variablen rechts; numpy und pandas dazu, Diagramme mit einem
eigenen Modul statt matplotlib.

- **Immer im Browser.** Der Code läuft in einem eigenen Faden mit Pyodide,
  auch wenn der lokale Server rechnet: über ihn könnte sonst jede Webseite
  Code auf dem Rechner ausführen. Derselbe Faden wie beim Rechenkern
  (`kern_arbeiter.js`), mit einem anderen Dienst (`opencivil.konsole.dienst`)
  und für sich: eine Endlosschleife hält weder die Seite noch den Kern an, und
  «Abbrechen» beendet ihn einfach – unterbrechen liesse sich Python im Faden
  nur mit Kopfzeilen, die GitHub Pages nicht setzt. Er startet erst beim
  ersten Lauf; am Rechner war das Skript nach rund 5 s fertig.
- **Die Sitzung** (`konsole/sitzung.py`) sammelt, was ein Lauf ergibt, der
  Reihe nach: Ausgabe, Fehlerausgabe, den Wert der letzten Zeile (nur in der
  Konsole), Fehler mit Skriptname und Zeile – ohne die eigenen Rahmen –,
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
  ist – sonst spränge der Cursor. Gespeichert wird kurz nach dem Tippen und
  vor jedem Lauf, als Anlass «skript»: das rechnet nichts neu.
- Das Beispielprojekt hat ein Skript mit einem Diagramm, ohne Download.

## 2026-10-15 · numpy und pandas liegen bei

Für die App «Python», die als Nächstes kommt, liegen numpy und pandas samt
dem, was pandas braucht, unter `web/vendor/pyodide/` (5 Dateien, 7.85 MB).
Der Benutzer hat sie Datei für Datei freigegeben; SciPy (14 MB) und
matplotlib (9.6 MB) wollte er nicht – Diagramme macht ein eigenes Modul.
Seaborn wäre keine leichtere Wahl gewesen, es baut auf matplotlib; Plotly
gehört nicht zur Pyodide-Verteilung und wäre mit plotly.js grösser.

- `werkzeug/pyodide_holen.py --pakete` holt sie aus der vollen Verteilung
  derselben Fassung und hält jede Datei gegen ihre Prüfsumme in
  `pyodide-lock.json`; beim Wechsel der Fassung kommen sie mit.
- Welche beiliegen, schreibt die Brücke aus den Dateien ins Kernverzeichnis
  (`pakete` in `web/kern/dateien.json`) – keine zweite Liste.
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
  es nicht mehr – es gibt nur noch eine Liste.
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

Mit dem Spannungsblock – Handrechnung und 0.85·x – gibt es bei viel Druck
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
- **Was dasteht:** `Rechenart.ohne_ebene` – «Mit der 0.85·x-Vereinfachung
  gibt es zu dieser Einwirkung keine Dehnungsebene – präzise rechnen.», bei
  der Handrechnung entsprechend. Die Stahlspannungen der Platte und des
  gezeichneten Querschnitts schreiben es statt der Probe, der Fall ist nicht
  erfüllt; das Bild «N, M» sagt dasselbe. Die schiefe Biegung prüft am Ende
  auch ihre Neigung, an M_y und M_z.
- **Die Linien bleiben, wie sie waren:** eine M-χ-Linie fragt nur, bei
  welcher Krümmung das Moment seinen Wert durchläuft – am Sprung ist das
  seine Stelle (`spannungsanalyse._durchlaufen`). Ihre Zahlen sind
  unverändert.

## 2026-10-15 · Verformung beim Knicken nur noch präzise

Die Verformung beim Knicken – die Ausmitte e_2d – rechnet nur noch präzise,
mit der Parabel; Kriechzahl und Werte bleiben wählbar (Benutzer). Den
Spannungsblock gibt es dort nicht mehr: mit ihm hat das Moment über der
Krümmung flache Stücke, auf denen jede Krümmung dasselbe Moment trägt, und
nahe der Grenzkraft hing N_Rd davon ab, wie gesucht wurde (siehe den Eintrag
darunter). Der Widerstand beim Knicken bleibt bei 0.85·x oder präzise.

Was erlaubt ist, steht einmal: `VERFORMUNGSARTEN` in `nachweis/rechenwahl.py`,
gelesen von Platte, Querschnittsanalyse und Katalog. Eine alte Datei mit 0.85·x
oder Handrechnung für die Verformung liest sich als präzise:
`ERSATZ_ALTER_WAHL` ist dafür eine Kette geworden – Handrechnung → 0.85·x →
präzise –, und gelesen wird, bis es die Wahl gibt. Im Widerstand wird die
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
den Warmstart, und die Stütze q3 – ihre Verformung rechnet absichtlich mit
dem Spannungsblock – kam auf 4200 statt 4099.5 kN. Mit dem Block hat das
Moment über der Krümmung flache Stücke: dort trägt jede Krümmung dasselbe
Moment, und welche gefunden wird, hängt am Weg der Suche. Beide Löser sagten
bei 4200 kN «trägt nicht», wenn sie frisch anfingen; mit dem Gedächtnis der
vorigen Probekräfte fand der neue eine Ebene. Ein Ergebnis, das an der
Reihenfolge der Rechnungen hängt, ist keines. Springt ein Gesetz, sucht der
Löser darum wie jeder `Faserloeser`, halbiert und von vorn
(`FaserloeserIllinois.halbiert`); das gilt auch am gezeichneten Querschnitt.
Parabel und elastisch haben flache Stücke erst am vollplastischen
Querschnitt – dort blieb an beiden Prüfprojekten jede Zahl, wie sie war, und
ein Test hält eine ganze Knickfolge gegen das Halbieren.

**Die Mitschrift sagt, wie gesucht wurde.** Der Löser beschreibt seine
Suche selbst (`Faserloeser.suche`); das Knicken schreibt damit «Illinois,
von der letzten Ebene aus» oder, beim Block, die Halbierungen.

## 2026-10-15 · Knicken am gezeichneten Querschnitt

Knicken gibt es jetzt auch für den gezeichneten Querschnitt, je Fall zu der
Zugseite, zu der sich der Stab biegt – unten, oben, links, rechts.

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
nicht an der Zeit – die schwankte auf dem ausgelasteten Rechner um das
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
`Σ A_s·σ_s,adm` aller Stäbe. Bei der Platte nimmt jede Lage die Hälfte –
zusammen derselbe Gedanke. **Zwang auf Biegung je Richtung** (Benutzer):
dasselbe Rissmoment wie beim spröden Versagen – es steht dafür jetzt einmal
als Funktion da (`richtungsnachweise.rissmoment`) –, gegen das Moment, bei
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

**Nichts doppelt.** Die Texte der Stahlspannung – Kriechen,
Werkstoffgesetze, was beim Fliessen verglichen wird – stehen einmal
(`spannungsbegrenzung.protokoll_festlegungen`), die Gebrauchsliste ist
dieselbe Klasse mit anderem Fall (`QAGebrauchsliste`: N, M_y, M_z), und die
Fenster der Oberfläche sind die der Platte mit einem anderen Ort
(`ort.zwang`, `ort.gebrauch` in `nachweise.js`).

## 2026-10-15 · Spannung-Dehnung-Analysen am gezeichneten Querschnitt

Die sechs Analysen der Platte gibt es jetzt auch für den gezeichneten
Querschnitt, je Zugseite – unten, oben, links, rechts. Gerechnet wird mit
denselben Funktionen; neu ist nur, wie der Querschnitt zu ihnen kommt.

**Ein Löser für jeden Faserquerschnitt.** `Querschnittsloeser` baute seine
Fasern aus Höhe, Breite und Lagen und suchte darin die Ebene. Die Suche
braucht davon nichts als die Fasern und die Dehnungsgrenzen. Sie steht jetzt
in `Faserloeser`; die Platte baut ihn wie bisher, der gezeichnete Querschnitt
aus `Querschnitt.richtung(psi)` – den Fasern, mit denen schon seine
Tragsicherheit rechnet. Bilder und Linien lesen vom Löser die Ränder (`oben`,
`unten`), die Lagen und die Spannung des Betons an einer Stelle; das sagt
jeder Querschnitt selbst. Bei der Platte liegt die Mitteldehnung auf halber
Höhe, beim gezeichneten Querschnitt im Schwerpunkt, wo N angreift.

**Ein Paar je Art.** Das Löserpaar der Platte (`Loeserpaar`) und das des
gezeichneten Querschnitts (`Schnittpaar`) haben dieselben Glieder: gerissen,
ungerissen, Riss, Bezugsfläche des Moduls. Was nur eine Art weiss – wie
sie reisst, woran sich der Modul misst, wo die Mitteldehnung gilt –,
schreibt jedes Paar in die Herleitung selbst; der übrige Text ist derselbe.
Bei der Platte ist `W/A = h/6`, also derselbe Riss wie bisher.

**Annahmen**, im Code «nach Vorgabe, nicht nachgeschlagen», in [[TODO]]: die
Nulllinie bleibt parallel zur Achse; der Riss am Bruttoquerschnitt mit `k_t`
wie bei der Platte, `f_ctm` vom Beton am gezogenen Rand; der äquivalente
Modul am Bruttoquerschnitt.

**Dabei:** Stäbe in derselben Tiefe, aus demselben Stahl, sind im Bild eine
Lage – sie haben dieselbe Dehnung, und dreissig Punkte übereinander liest
niemand. Die Analysen zerlegen in 60 Streifen statt der 200 der
Tragsicherheit: eine Linie rechnet viele Ebenen, und M_Rd ändert sich dabei um
zwei Zehntelpromille. Jede Dehnungsgrenze trägt jetzt ihren Namen mit Seite
(«Beton C30/37, Rand oben»), damit «massgebend» sagt, wo.

## 2026-10-15 · Querschnittsanalyse: Kapitel als Knöpfe

Wie bei der Platte: oben der Querschnitt mit dem Zeichenfenster, darunter je
Kapitel ein Knopf, die Eingaben im Fenster. Die drei Panels Werkstoffe,
Schubwände und Nachweise sind weg. Die Rechenwerte je Material und die
Angaben der Schubwände stehen im Fenster der Tragsicherheit: die Werkstoffwahl
ist ihre Rechenwahl – Duktilität und sprödes Versagen rechnen am selben
Querschnitt, ihre Fenster sagen es –, und Neigung, k_c und Längszugkraft
braucht allein die Querkraft mit Torsion.

`kapitel.js` ist dafür allgemein geworden: Knopf, Panel und Fenster für
jedes Bauteil. Welche Kapitel eine Art hat, steht bei ihrem Editor – die der
Platte in `editor.js`, die der Analyse in `querschnittsanalyse.js`.

## 2026-10-15 · Zeichenfenster: der Vektor beginnt am angeklickten Knoten

Verschieben und Kopieren fragten zuerst nach einem Basispunkt, dann nach dem
Ziel – zwei Klicks, auch wenn man den Knoten gerade angeklickt hatte, um
ihn zu wählen. Jetzt merkt sich das Fenster den zuletzt angeklickten Knoten
(`a.anker`): eine Ecke, ein Stab, ein freier Knoten. Mit V oder C beginnt der
Vektor dort, und der Knoten ist zugleich Bezugspunkt – getippte Δy und Δz
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
man sieht, wo eines aufhört. Die Karten darin – Lagen, Einwirkungen –
bleiben weiss. Der Baum links trägt keine Zeichen und keine farbigen Kanten
mehr.

**Die Bewehrung braucht gut die Hälfte der Höhe.** Eine Lage ist so hoch wie
ihre zwei Zeilen Grund und Zulage, 68 statt rund 110 px: Nummer und Richtung
stehen links daneben statt in einer eigenen Kopfzeile, der Stahl am Ende der
Grundzeile, «ungünstig/günstig» als ein Knopf am Ende der Zulage. Ob die
Zahl eine Teilung oder eine Stabzahl ist, schaltet die Einheit selbst
(«mm» ↔ «Stk») – ein eigener Knopf kostete jede Zeile eine Spalte. Die
Zahlenfelder der Lagen sind auf vier Ziffern bemessen statt auf acht. Die
Bügel sind gebaut wie eine Lage.

**Die Kapitel sind Knöpfe, ihre Eingaben stehen in einem Fenster.** Unter der
Bewehrung stand bisher alles offen untereinander – sieben Nachweise, die
Analysen, die Suche –, und wer die Bewehrung neben einer Einwirkung sehen
wollte, rollte weit. Jetzt steht jedes Kapitel als Knopf da, mit Zeichen und
einer kleinen Zeile, was eingestellt ist; ein Klick öffnet die Eingaben in
einem Fenster über der mittleren Tafel. Baum und Ergebnis bleiben sichtbar,
damit man sieht, was eine Eingabe bewirkt. Jede der sechs Analysearten hat
ihren Knopf; im Fenster wird die Art darum nicht mehr gewählt, ein neues
Bild bekommt sie mit. Jedes Kapitel steht einmal in `kapitel.js`, was in
den Fenstern steht, liefert `nachweise.js`.

Welches Fenster offen ist, ist Ansichtssache (`zustand.fenster`) wie die
offenen Kapitel im Baum. Es gehört zum gewählten Bauteil: wer ein anderes
wählt, schliesst es – alle Wahlen gehen dafür durch `waehlen`. Gezeichnet
wird es mit dem Editor neu. Der graue Grund darunter bleibt dabei stehen und
ist der Knoten, der rollt; so retten Bildlauf und Fokus wie bei den Tafeln.

**Was nur die Querkraft braucht, steht bei ihr.** Grösstkorn und
Einlagenhöhe (ohne Bügel), k_c und die Grenzen der Neigung (mit Bügeln) gehen
in keinen anderen Nachweis ein. Sie standen bei der Platte und bei den Bügeln
und stehen jetzt im Fenster der Tragsicherheit.

**Die Zeichen** sind eigene Linienbilder (`sinnbilder.js`), im Stil wie bei
Fagus, aber nicht von dort übernommen.

## 2026-10-15 · Bügelteilung, gleiche Fallnamen, Lagerkräfte am Bildschirm

Vier Punkte, die man sieht – drei behoben, einer bestätigt.

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
Fälle nicht zu unterscheiden – sie werden am Namen erkannt. Bisher fiel das
in `pruefen` auf, und das ganze Projekt rechnete nicht, auch keine Platte.
Jetzt ist es eine Meldung des Systems: es rechnet nicht und sagt warum, der
Rest rechnet weiter.

**Lagerkräfte: dieselben Zeilen in Herleitung und Bildschirm.** Der
Bildschirm zeigte nur die Lager an Knoten. Beim gebetteten Balken fehlte
damit die Bettung, und die Kräfte gingen nicht auf: Einfeld mit 10 kN/m auf
6 m, ein Lager und Bettung – am Bildschirm 11.7 kN, in der Herleitung
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
Unbekannten» in der Werteliste – die Zahl steht weiter in der Herleitung.

**Ergebnisse stehen in der Lösung, nicht am Objekt.** Bisher legten die
Nachweise, das Balkensystem und das Gleichungsblatt beim Rechnen auf sich
selbst ab, was sie fanden – Interaktionslinie, Werte je Lage und Fall,
Wände und Schubfluss, das Systemergebnis –, und jeder Lauf überschrieb es.
Wer las, musste wissen, welcher Lauf zuletzt war. Der Zwischenspeicher
hängte darum ganze Objekte zwischen zwei Aufbauten um (`TEILEFELDER`,
`teile_von`, `teile_setzen`) und bildete die Felder der Lösung in
`Teilergebnis` von Hand nach. Jetzt gibt `rechne()` eine `Ausfuehrung`
zurück: Ausgaben, Urteile und einen Befund. Die Lösung hält
`befunde[berechnung_id]`; Diagramme, Zusammenfassung und Fassade lesen
dort. Wer den Befund einer anderen Berechnung braucht – Knicken und
Querkraft die Linie der Tragsicherheit –, meldet einen `Befundbezug` an,
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
Sorte – sie baute ihre Lagen auf einem zweiten Weg.

**Die Lage trägt ihren Stahl.** `Stahllage` hat jetzt ein Feld `stahl`
(ein `Stahlgesetz` mit den Festigkeiten des Wertesatzes) und `sorte`.
Gebaut wird sie an einer Stelle, `rechenwahl.stahllagen()`, angemeldet über
`lagenbezuege()` unter `{kennwert}__{sorte}` – genau so, wie die M-N-Linie
es schon tat. Ihr Tupel `(a_s, z, Gesetz, Text)` und
`dehnungsfaecher.lagen_aus_eingaben` sind weg: Löser, genaue Linie,
Handrechnung und Analyse sehen eine Lage jetzt in derselben Gestalt. Der
Löser bekommt keinen Stahl mehr, sondern macht aus dem Stahl jeder Lage ihr
Gesetz (`bilinear`, in der Handrechnung nur auf Zug).

**Wo es auf die Seite ankommt, entscheidet die Seite:**

- Stahlspannung: je Stahl eine Grenze (`f_yd − 80`, bzw. aus der
  Rissbreite mit `f_yk` und `E_s` der Sorte). Massgebend ist die gezogene
  Lage mit dem kleinsten Erfüllungsgrad – bei einem Stahl dieselbe wie
  bisher, die am stärksten gedehnte.
- Querkraft: `ε_v` mit `f_yd` und `E_s` der gezogenen Seite, je Fall und
  in der M-V-Kurve je Momentenrichtung.
- Analyse: Fliessbeginn, wo die erste Lage die Fliessdehnung *ihres*
  Stahls erreicht; die Grenzen des Fächers je Lage mit ihrem `ε_ud`; in der
  Herleitung `ε_y` je Stahl.
- Knicken: das Suchfenster reicht im Zug bis zur kleinsten Bruchdehnung der
  Lagen, an beiden Rändern. Das ist die vorsichtige Lesart des Fensters
  am Rand, das schon vorher eine Vereinfachung war – ob Knicken die
  Grenzen des Fächers bekommt, steht im TODO beim Querschnittsmodell.

**Mit einem Stahl ändert sich nichts** – auch nicht im Bericht: gleiche
Zeichen, gleiche Zahlen, gleiche Sätze. Neue Sätze und Indizes erscheinen
nur, wo eine Richtung zwei Stähle hat. Einzige Ausnahme in der Sache: die
Stahlspannungen rechneten fest mit `ε_ud = 4.5 %` statt mit dem der Sorte;
bei B500B ist das dasselbe, bei B500A und B500C gilt jetzt die Sorte.

## 2026-10-12 · 2D Balkensysteme: ein ebener Rahmen nach der Steifigkeitsmethode

Wunsch des Benutzers: unter der Querschnittsanalyse eine App für ebene
Balkensysteme – gezeichnet wie der Querschnitt, Stäbe mit Querschnitt und
Material, Lager und Federn, Gelenke, Lastfälle und Kombinationen, gerechnet
nach der Steifigkeitsmethode. Er wählte den ebenen Rahmen: Normalkraft statt
Torsion.

**Ein eigener Rechenkern, `opencivil/stabwerk/`, ohne Projekt und ohne
Rechenwerk.** Gleichungslöser, Stab, System, Verläufe und Querschnitte
kennen nur Zahlen in SI. So lassen sie sich gegen Handrechnungen prüfen –
Einfeldträger, Kragarm, Zweifeldträger, Dreigelenkrahmen, Fachwerk, Bettung
nach Hetényi –, bevor irgendetwas anderes daran hängt. Erst
`stabwerk/rechnung.py` meldet ein System im Rechenwerk an.

**Gelöst wird im Profil, nicht dicht.** LDLᵀ mit umgekehrter
Cuthill-McKee-Nummerierung: ein gebetteter Stab wird in bis zu 64 Stücke
geteilt, und mit hunderten Unbekannten wäre eine dichte Matrix in Pyodide
spürbar. Ein Pivot unter 1e-10 · K_ii heisst beweglich; dann wird die
Unbekannte festgehalten, zu Ende zerlegt und die freie Bewegung gelöst – so
kann die Meldung sagen, *was* sich bewegt, statt nur «singulär».

**Eine Drehung ohne Steifigkeit wird gestrichen, erkannt an der Verbindung.**
Hängt ein Knoten nur an Gelenken, wäre seine Zeile in K null. Statt sie mit
einer kleinen Feder zu verstecken, fällt sie weg, ist null und heisst
«Verdrehung nicht bestimmbar, da keine Steifigkeit» – so verlangt es der
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
Material, eine Platte oder Analyse, die es nicht gibt – und das verhindert
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

**Teilen und Umkehren rechnet der Kern.** Dabei entstehen Lastwerte – der
Wert einer Trapezlast am Schnitt, gespiegelte Stellen, ein umgekehrtes
Vorzeichen bei quer und längs. Das wäre Rechnung in der Oberfläche. Ein Test
hält fest, dass beides die Lagerkräfte nicht ändert.

**Das Zeichenfenster kann «verbunden».** In der Querschnittsanalyse gehört
eine Ecke ihrem Element; ein Rahmen hängt an seinen Knoten. Statt die
Mechanik zu kopieren, stellt der Adapter das ein, dazu Einheit, Raster,
Werkzeuge und Zoomgrenzen – die Querschnittsanalyse bleibt, wie sie war.

**Die Bilder kommen aus einer eigenen Anfrage**, wie die Diagramme der
Querschnittsanalyse: Verläufe sind gross, und die Rechnung bei jeder Eingabe
soll sie nicht mitschleppen. Die Oberfläche zeichnet nur, und zwischen den
dichten Proben des Kerns verbindet sie für die Anzeige gerade.

**Steifigkeit nach Vorgabe, nicht nachgeschlagen:** E_cm für Beton, E_s für
Stahl, am ungerissenen Bruttoquerschnitt, ohne Schubverformung, Theorie
1. Ordnung. Die Herleitung sagt es, das [[TODO]] führt es.

Die Rechteckformeln der Spannung-Dehnung-Analyse und der Stabquerschnitte
sind dieselbe Formel und heissen jetzt gleich – «Fläche eines Rechtecks»,
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
Handrechnung ist ein Polygon durch vier Eckpunkte, dazwischen gerade – unter
Druck bis 18 % unter der genauen Linie desselben Modells. Die M-χ-Linie und
das Knicken rechnen die Normalkraft aber Ebene für Ebene genau; dort war die
«Handrechnung» nur ein Spannungsblock ohne Druckstahl, also eine schlechtere
0.85·x-Vereinfachung. Sie fällt dort weg (`FASERARTEN`). Eine alte Datei
liest sich als 0.85·x (`ERSATZ_ALTER_WAHL`); die Zahlen steigen dann leicht,
weil die Druckbewehrung mitzählt – im Prüfprojekt N_Rd,K 3900.6 → 4496.7 kN.
Die eigene Linie des Knickens rechnet schnell mit den Schritten der Suche,
sonst zahlte die Bewehrungssuche jetzt öfter eine ganze genaue Linie.

**Namen nach Wunsch.** «Handrechnung», «0.85·x-Vereinfachung», «Präzise ohne
Vereinfachung» – an einer Stelle (`Rechenart.beschriftung`, `kurz`,
`latex`), auch für die Betongesetze der Querschnittsanalyse.

**Zugfestigkeit nur für den Riss.** Die gestrichelte Vergleichslinie
«ungerissen» lief über den Riss hinaus bis zum Bruch – dort mit Betonzug
ohne Grenze. Sie endet jetzt beim Riss. Kein Betongesetz und kein Widerstand
zählt die Zugfestigkeit; sie steckt in M_Riss und N_Riss und in den
Nachweisen, die vom Reissen handeln.

**φ in der Analyse.** Der ungerissene Teil rechnet immer mit E_cm/(1+φ),
auch bei 0.85·x – das Feld war dort grau, obwohl φ wirkte. Es ist in den
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
wie die Python-Bibliothek funktioniert – und ein Notizbuch für Claude.

**Ein Ordner, kein Plugin.** Obsidian liest einen gewöhnlichen Ordner als
Tresor: `notizbuch/`. Darin [[Start]], die Formelsammlung (111 Formel-, 18
Themenseiten, eine Übersicht), je Modul eine Python-Seite (80) und die
Notizen – [[Arbeitsweise]] (die Regeln, die vorher privat lagen),
Entwicklung und TODO, mit `git mv` hierher verschoben. `CLAUDE.md` lädt die
Arbeitsweise in jede Sitzung; `.obsidian/app.json` stellt strenge
Zeilenumbrüche und Wikilinks ein.

**Eine Seite je Formelname.** Gleich benannte Formeln sind Fassungen einer
Seite (131 Formeln, 111 Seiten). Der Name ist der Titel ohne Zahlen, oder
`GleichungBlock.name`, wo der Titel je nach Fall wechselt oder nichts sagt
(«Ansatz», «C30/37: …», «Duktilität» wie das Thema). Er hängt nur an der
Formel, nie an Reihenfolge oder Zähler – sonst stünde die Theorie beim
nächsten Lauf an der falschen Formel. Tests über die ganze Sammlung halten
das: eine Formel ein Name, eine Seite eine Grösse, kein Name wie ein Thema,
keine Sorte, jeder Name im Tresor einmal.

**Oben erzeugt, unten von Hand.** Die Brücke schreibt den oberen Teil jeder
Seite neu; unter der Linie `<!-- Ab hier von Hand … -->` bleibt die Theorie
Zeichen für Zeichen. Die Prüfsumme `erzeugt:` verrät Handänderungen oben –
dann schreibt die Brücke nichts und nennt die Datei. Notizen ohne
`erzeugt:` fasst sie nie an; eine verwaiste Seite mit Theorie bleibt mit
Hinweis stehen, ein Test ist rot, bis der Text umgezogen ist.

**Woher eine Grösse kommt** sagt die Rechnung selbst: je Lauf merkt sich der
Generator, welche Formel einen Wert zuletzt schrieb. Dafür trägt die
Formelzeile ihre Eingänge (`Formelzeile.eingaben`) und jede Gleichung ihre
Codestelle – gefunden über den Aufrufstapel, weil viele Formeln von
Hilfsfunktionen in anderen Modulen geschrieben werden. Gekostet hat das
nichts Messbares.

**Die Python-Seiten** liest `bibliothek.py` mit `ast`, ohne Import: Docstring,
Klassen und Funktionen mit Signatur, Konstanten, Importe, Formeln. Zeilen in
GROSSBUCHSTABEN werden Überschriften, Eingerücktes Code, Rollen wie
`:class:` Links – auch ohne vollen Namen, über die eigene Klasse und die
Importe. Keine Rolle bleibt offen (Test). Die leeren Pakete bekamen einen
Docstring, `opencivil` einen Abschnitt RECHENWEG.

**Auf der Seite** öffnet «Dokumentation» die Ansicht – auf dem Telefon die
vierte Wahl «Doku» unten, weil die Kopfleiste voll ist. Den Markdown zerlegt
ein eigenes Modul ohne fremde Bibliothek (`markdown.js`, rein, mit node
über das ganze Notizbuch geprüft); `notizbuch_seite.js` baut daraus die Seite,
nie über `innerHTML`. Die Adresse `#notizbuch/<Name>#<Abschnitt>` trägt
Links, Zurück-Knopf und Lesezeichen. Seiten kommen ohne Zwischenspeicher:
eine in Obsidian geänderte Notiz steht nach dem Hochladen gleich da; eine
neue erst, wenn die Brücke sie ins Verzeichnis `web/kern/notizbuch.json`
geschrieben hat.

**Was wegfiel.** Der rechte Reiter «Formelsammlung» samt
`formelsammlung.json` – an jeder Gleichung der Herleitung führt jetzt
«Formel» zur Seite. Und auf Wunsch der Knopf «Bericht» oben rechts.

**Theorie** steht unter jeder Seite, von Claude geschrieben, ohne erfundene
Normstelle: ein Test verlangt, dass jede «SIA 262 …»-Angabe darin auch im
Code steht. Annahmen heissen «nach Vorgabe, nicht nachgeschlagen». 80 von
111 Formeln haben noch keine Normstelle – die Liste steht auf der Übersicht
der Formelsammlung.

**Unterwegs gefunden.** Der lokale Server dekodierte Adressen nicht: jede
Datei mit Umlaut oder Leerzeichen gab 404. Und der Docstring von `tresor.py`
zeigte die Trennlinie wörtlich – auf seiner Modulseite hielt der Generator
sie für die echte und meldete «von Hand geändert». Eine ganz erzeugte Seite
darf die Linie jetzt nicht enthalten.

## 2026-10-11 · Spannung-Dehnung-Analyse: äquivalenter E-Modul über M und über N

Wunsch: zwei weitere Arten neben M–χ und N–ε. Auf der y-Achse der
äquivalente E-Modul – der, den man einem reinen Betonquerschnitt geben
müsste (ungerissen, ohne Stahl, elastisch) –, auf der x-Achse das Moment
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

**Ab dem Zustand ohne laufende Kraft** – deine Wahl. Was die feste Kraft
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
reinen Beton, E_c·I_id/I_c = 35 912 N/mm² – 0.03 % darüber, das ist die
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
  charakteristisch → M_Rk) und die Rechenart – Handrechnung Block 0.85·x,
  Block 0.85·x genau (mit Druckstahl) oder Parabel.
* Das Knicken zweimal: für die Verformung (e_2d) und für den Widerstand
  N_Rd(M_Ed = N_Ed·e_tot).
* Die Spannung-Dehnung-Analyse bekommt die Handrechnung als Rechenart.
* Das φ der Platte bleibt, gilt aber nur für den Vergrösserungsfaktor w/w_c
  nach SIA 262:2025, 4.4.3.2.5 – in x, für Zug unten und Zug oben, auf zwei
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
Handrechnung (am Beispiel auf 0.1 %, auch mit Druckbewehrung) – das ist die
Probe, dass Löser und Linie dasselbe Modell meinen.

**Zwei Linien hinter einer Schnittstelle.** `nachweis/resistenzlinie.py`:
die `Handlinie` (das Polygon der Handrechnung) und die `Ebenenlinie` (der
Rand des Dehnungsfächers). Beide können dasselbe – `innerhalb`, `kante`,
`moment_bei`, `eckwerte`, `protokoll_treffer` –, und der M-N-Nachweis,
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
– aber auch die grösste Druckkraft liegt nicht beim gleichmässigen −ε_c1d:
kippt die Ebene ein wenig um den Punkt C, fliesst die gedrückte Bewehrung und
trägt mehr. Beide werden mit dem Goldenen Schnitt zwischen den Nachbarn des
grössten Punkts gesucht.

**Der Stahl der Linie fällt jenseits von ε_ud nicht auf null.** Die unterste
Lage liegt im Fächer genau auf ε_ud. Ein Gesetz, das dort abbricht, kippte an
der Rundung – 1e-19 zu viel, und die halbe Zugkraft wäre weg.

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
Widerstand wie die Tragsicherheit – die Kriechzahl zählt nur, wo sie wirkt –,
dann ist es deren Linie, einmal gerechnet und einmal hergeleitet. Sonst baut
es eine eigene, mit Herleitung, und im M-N-Diagramm steht sie gestrichelt
neben der massgebenden; die Knickpunkte liegen auf ihr. Nebenbei korrigiert:
die Herleitung nannte als Suchfenster −3.0 ‰, gerechnet wurde mit
ε_c2d = −3.5 ‰.

**w/w_c im Lagenaufbau.** Dort entstehen schon Flächen und Tiefen jeder
Lage, Bewehrungsmass und Distanzhalter – der Faktor steht in der Herleitung
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
zusammentreffen, standen dieselben Zahlen zweimal da – wer eine Ecke
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
  Formen – Punkt, Linie, Fläche – und wissen nichts von Beton. Ansicht,
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
  (`vorlage_einsetzen`), und die Vorlage kommt **dazu** – vorher ersetzte
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

Die beiden je Lastfall sind weg. Was nur sie zeigten – wo der Nachweis
seinen Widerstand misst –, steht jetzt im einen Diagramm:
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
  * `geometrie` – Polygone (Fläche, Schwerpunkt, Trägheit nach Gauss),
    Verschachtelung (ein Polygon in einem anderen ersetzt es dort), Stablinien,
    Prüfungen.
  * `fasern` – Fasern und Dehnungsgrenzen. Der Löser der Platte rechnet jetzt
    darüber; ihr Bericht ist Zeichen für Zeichen gleich geblieben.
  * `interaktion` – die zulässigen Dehnungsebenen als konvexes Vieleck. Sein
    Rand ist der Dehnungsfächer, für jede Form ohne Sonderfälle. Je Neigung ψ
    wird N = N_Ed gesucht, und ψ so, dass das Moment in Richtung der
    Einwirkung zeigt.
  * `schubwaende` – Federn b_w·l für die Querkraft, das Versatzmoment, die
    Zellen als Flächen des Wandgraphen, Bredt mehrzellig, Fachwerk je Wand,
    die Längszugkraft.
  * `analyse` – das Bauteil: die Zeichnung mit allen Meldungen, die Werte,
    die Werkstoffwahl.
* **Vier Nachweise:** `schiefe_biegung`, `schubwandnachweis` und in
  `richtungsnachweise` Duktilität und sprödes Versagen je Richtung.
* **Aufbau je Bauteil statt je Platte.** Zwischenspeicher, Zusammenfassung und
  Bericht gehen über `Aufbau.bauteile()`: erst die Platten, dann die Analysen.
* **Die Oberfläche** (`web/js/`):
  * `zeichenfenster.js` – das Zeichenfenster. Es entsteht einmal je Analyse
    und übersteht jeden Neubau der Tafel; ein halb gezeichnetes Polygon, der
    Massstab und der Verlauf für «Rückgängig» bleiben, wenn nebenher eine
    Rechnung fertig wird.
  * `koordinaten.js` – das Koordinatenfenster, absolut oder relativ.
  * `querschnittsanalyse.js` – die übrige Eingabe.
  * `qa_diagramme.js` – die Diagramme.
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
optimieren – dazu eine Mindestdicke.

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
  – der Abschnittstitel trägt ihn schon – sind eine zu viel. (Seit die
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

## 2026-09-25 · Jede Formel aus einer Vorlage – und danach vereinfacht

Der Pilot der letzten Runde (Duktilität) hatte gezeigt, dass Vorlagen tragen.
Jetzt stehen alle Herleitungen so da: die Formel einmal mit Symbolen, Zahlen
und Einheiten setzt das Programm aus den gerechneten Werten ein. Von Hand
gesetzte Einheiten in den Nachweisen und Querschnitten: vorher 179, jetzt 13
– Tabellenköpfe und die Stahldichte 7850 kg/m³. Jeder Schritt wurde am
Schnappschuss gemessen; geändert hat sich die Darstellung, keine gerechnete
Zahl. Damit das auch dort galt, wo bisher kein Projekt hinkam, ist «voll»
zuerst um Querkraft ohne Bügel, Bügel mit Stabzahl in y und die begrenzte
rissaktive Dicke erweitert worden.

### Zuerst die beiden Befunde des Piloten

* **Kein «1.00» neben «nicht erfüllt».** Die Herleitung rundete den Grad
  selbst. Jetzt kennt ein Wert, ob er ein Erfüllungsgrad ist (`grad_def`),
  und setzt sich überall nach `grad_als_text` – auch in der Werttabelle,
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
Einheit – 300 mm stehen als 0.3 m da, nicht als 0. Vorher stand bei E_cm
`∛(38 N/mm²)`, bei k_d ein von Hand gesetztes `· 10⁻³`.

### Was beim Umstellen auffiel

* **Querkraft, fliessende Bewehrung:** Liegt m_Ed über m_Rd, ist ε_v fest,
  1.5 · f_yd/E_s. Die Herleitung zeigte trotzdem die Formel mit m_Ed und
  m_Rd – mit Zahlen, die ein anderes ε_v ergeben (4.79 statt 3.26 ‰).
* **A_s,tot** stand mit zwei Nachkommastellen da: eine von Hand gebaute
  WertDef gab die Stellenzahl als Normverweis weiter.
* **Eine auf null gerundete Zahl** stand als «-0».
* **f_cd in der Handrechnung** ohne Nachkommastelle: bei C25/30 «17» statt
  16.7, die Druckkraft ging von Hand um 2 % daneben.
* Grössen der ganzen Lage tragen deren Index (σ_s,adm,3,x), wie Widerstand
  und Grad in der Tabelle; die statische Höhe sagt, aus welcher Lage sie
  kommt (`d = h − z_{3,x,g}`).

### Vereinfacht

Vier Durchsichten des Diffs – Wiederverwendung, Vereinfachung, Effizienz,
Ebene der Lösung –, jeder Befund ein Commit, der Bericht dabei unverändert:

* **Ohne Leser keine Herleitung.** Bewehrungssuche, ausgeschaltete Nachweise
  und Querkraftkurven bauten jede Formel – zweimal eingesetzt, Breite
  gemessen – und warfen sie weg. Die Suche an der Decke von «voll» brauchte
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
heute keine Formel erreicht – ohne ihn wäre die Messung für eine
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
  gewichtet, gerechnet wurde nach Flächen – jetzt steht dasselbe da.
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
Schnappschuss des Berichts gemessen – der dafür zuerst auf ein zweites
Projekt verbreitert wurde, das jeden Nachweis einmal laut führt.

### LaTeX ja – aber nur, wo Mathematik steht

Markdown hat keine eigene Formelsprache. Wer Formeln darstellt – GitHub,
Obsidian, Jupyter, Pandoc –, liest LaTeX-Mathe zwischen `$…$` und `$$…$$`;
Word 365 versteht LaTeX-Mathe im Formeleditor und MathML aus der
Zwischenablage. Für Formeln war LaTeX also richtig.

Falsch war es als Träger von Text und Tabellen. Jede Tabellenzelle war LaTeX,
Text stand als `\text{…}` darin: die Konsole druckte das so ab, der
Word-Knopf einer Tabelle lieferte eine Formelmatrix statt einer Tabelle, und
die Oberfläche las den Text per regulärem Ausdruck zurück. Jetzt sagt eine
Zelle, was sie ist: ein `str` oder `Mathe(latex)`. Auch jede Zahl ist Mathe –
ihr Minus ist ein Minuszeichen und kein Bindestrich; beim ersten Umbau waren
Zahlen kurz Text, und im `.tex` stand `-6000.0` mit Bindestrich. Im Dokument
sind Tabellen jetzt `tabular` bzw. `longtable`, nicht mehr eine Formel.

### Der Bericht besteht aus Blöcken

Konsole und LaTeX-Dokument bauten ihre Abschnitte je selbst und liefen
auseinander: die Werte vor oder hinter den Nachweisen, nach Kennung oder nach
Bezeichnung; und beide fassten die Nachweise flach zusammen, ohne Platten –
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
Ob Word sie so einfügt, wie es soll, ist hier nicht prüfbar – die
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
  «1.00» neben «nicht erfüllt» – genau das, was `grad_als_text` verhindert,
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
* Die Spannung-Dehnung-Analyse baute ihre Löser in der Schnittstelle – ohne
  Oberfläche war sie nicht zu haben, und ihr Test prüfte eine eigene Kopie
  des Aufbaus. Jetzt `spannungsanalyse.analysen()` und `Ergebnis.analysen()`.
* Die Punktfolgen der Diagramme stehen in `web/diagrammdaten.py`; dabei fiel
  eine zweite Kopie von `BLOCKANTEIL = 0.85` weg. Die Webtests sind nach
  Thema geteilt.
* Eine Regel für Fallkennungen statt elf Kopien, eine Liste der
  Rissanforderungen statt zwei; `eintragen()` lehnt ein Nachweisfeld ab, das
  nicht in `NACHWEISFELDER` steht.
* Im LaTeX-Fliesstext stehen griechische Buchstaben und `≥` als Unicode. Unter
  pdflatex bricht das ab – älter als diese Runde und als eigene Aufgabe
  vermerkt. Eine TeX-Maschine gibt es hier nicht; übersetzt wurde nichts.

---

## 2026-09-25 · Stahlspannung unter Dauerlast, und was ein strenges Review daran verschob

Neu ist ein Nachweis: die Stahlspannung unter quasi-ständiger Einwirkung,
gehalten gegen dieselbe zulässige Spannung wie bei der Zwängung – `f_yk` bei
normaler Anforderung, die Wurzelformel mit `w_nom` bei erhöhter und hoher.
Gerechnet wird mit 60 % der Tragsicherheitseinwirkungen, beim bestehenden
Nachweis gegen Fliessen mit 70 %; beide Anteile sind je Platte einstellbar.
Das Was steht im Code. Hier steht, warum er so aussieht – und was eine
zweite, strenge Durchsicht danach noch verschoben hat.

### Das Plateau gehört zu f_yk

Die Gebrauchsnachweise rechneten mit dem Fliessplateau bei `f_yd`. Für den
neuen Nachweis wäre das tödlich gewesen: bei normaler Anforderung ist die
Grenze `f_yk = 500`, das Plateau kappte die Spannung aber bei 435 – ein
Nachweis, der per Konstruktion nie durchfällt. Der Teilsicherheitsbeiwert
gehört in die Tragsicherheit; im Gebrauchszustand wird gefragt, was der
Querschnitt *tut*, und Stahl fliesst bei `f_yk`.

Welche Werte ein Nachweis ansetzt, ist seither ein Name und keine Zahl an der
Aufrufstelle: `Werkstoffsatz.BEMESSUNG` oder `CHARAKTERISTISCH`. Zuerst hatte
der Satz nur einen Nutzer, und die anderen schrieben weiter `"f_yd"` von Hand –
eine Abstraktion, die zur Hälfte eingeführt ist, ist schlechter als keine. Jetzt
nennt jeder Nutzer des Lösers seine Wahl.

### Gemessen wird an der Dehnung, wenn der Stahl fliesst

Bei normaler Anforderung fallen Grenze und Plateau zusammen. Ein fliessender
Stahl hätte dann `σ_s = σ_s,adm` und stünde mit 1.00 als erfüllt da – dieselbe
Falle wie das «1.00 neben nicht erfüllt», die schon einmal behoben wurde, nur
von der anderen Seite. Darum `α = σ_s,adm / (E_s · ε_s)`: elastisch ist das Bit
für Bit der Spannungsvergleich, auf dem Plateau wächst die Dehnung weiter, und
der Nachweis fällt um so deutlicher durch, je weiter der Stahl gedehnt ist. Das
braucht auch die Bewehrungssuche – ein Grad, der auf dem Plateau festsitzt,
zeigt ihr keine Richtung.

### Eine Klasse, zwei Grenzen

Beide Stahlspannungsnachweise sind dieselbe Rechnung: derselbe Löser, dieselbe
Fallschleife. Verschieden ist die Grenze – ihre Zahl, ihre Eingaben, ihr
Absatz in der Herleitung. Also eine Klasse, und die Grenze als Objekt, das
diese drei zusammenhält. Zwei Klassen mit kopiertem Kern wären genau das, wovor
`zustand2.py` warnt: zwei Nachweise, die für denselben Querschnitt verschiedene
σ_s melden.

Die Durchsicht fand daran noch zweierlei. Die Grenzen legten beim Anmelden
Zustand ab, den sie später lasen – eine Reihenfolge, die nur ein Docstring
sicherte. Und *wann* eine Grenze gilt, stand draussen, im Aufbau und im Katalog
der Oberfläche. Jetzt werden beide Grenzen gleich gebaut und sagen selbst, bei
welcher Anforderung sie gelten; im Aufbau sind die zwei Blöcke eine Schleife.

### Ein Konzept, ein Typ

Die Gebrauchslastfälle waren sechs flache Felder an der Platte, und fünf Stellen
setzten die drei zusammengehörigen über ihre Namen wieder zusammen. Jetzt ist
es eine `Gebrauchsliste` mit Anteil, Schalter und Fällen, die sich selbst
prüft. Das Dateiformat war erst eine Runde alt – billiger wurde die Umstellung
nicht mehr. Alte Dateien werden gelesen und neu geschrieben.

Dieselbe Frage stellte sich an kleinerer Stelle mehrmals: was zu einer Platte
gehört, gehört an die Platte. Ihre Namensprüfung stand am Projekt, ihre
Massprüfung im Aufbau, die Aufzählung ihrer Lastfalllisten in der Suche. Jetzt
hat `QuerschnittEintrag` `pruefen()`, `masse_pruefen()` und `ohne_lastfaelle()`
– und die Massprüfung bewusst *nicht* in `pruefen()`, weil das auch beim
Öffnen läuft: eine gespeicherte Platte mit `h = 0` liesse sich sonst nicht mehr
öffnen und korrigieren.

### Warum die Suche lange brauchte

Nicht zu viele Nachweise, sondern einer, der ein Bild malt: der M-N-Nachweis
baute bei jeder Bewertung die genaue Resistenzlinie, 97 000 Auswertungen des
Werkstoffgesetzes, für ein Diagramm, das während der Suche niemand ansieht.
Ohne sie: 289 → 56 ms je Bewertung. Dazu entstehen im schnellen Aufbau ganz
stille Nachweise nicht mehr – exakt und nicht genähert, denn die Suche zählt
stille Urteile ohnehin nicht. Und ein `max()` im Betongesetz kostete, bei
siebzigtausend Aufrufen je Fall, allein 28 ms.

### Ohne Oberfläche, aber nicht daneben

`p.beton()`, `p.platte()`, `p.rechnen()` legen dieselben Einträge an, die die
Maske anlegen würde – kein zweites Objektmodell, das mit dem ersten gleich
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
  wurde `Feld__60___`, ein doppelter Index, an dem KaTeX abbrach – sichtbar,
  sobald der neue Nachweis immer lief. Jedes Symbol wird jetzt geprüft.
* Ein knapp verfehlter Grad hiess in beiden Berichten «1». Die Regel dagegen
  stand nur in der Schnittstelle; jetzt steht sie im Kern.
* Ein Test-Helfer setzte Felder mit `setattr`. Nach der Umstellung auf die
  Gebrauchsliste gab es die alten Namen nicht mehr – `setattr` legte sie still
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
Baustelle nicht gibt – im Beispiel sind das 261 statt 249 mm, also 5 % zuviel.
Darum ist die Vorgabe neu **x auf der 2. und 3. Lage**: die Querrichtung läuft
unten und oben durch, die Tragrichtung liegt dazwischen. Der häufigere Fall,
und der ungünstigere.

Die Suche fasst die y-Lagen nicht an. Das war eine Entscheidung mit zwei
möglichen Antworten, und die falsche wäre teuer gewesen: sucht man y gegen
dieselben Nachweise wie x, bekommt y auch dann Eisen, wenn niemand etwas
nachweisen will – und sucht man es gegen die *eingeschalteten* Nachweise, bleibt
y bei den Vorgaben (alles aus) leer, und die statische Höhe von x ist wieder
optimistisch. Beides schlecht. Also gar nicht: der y-Durchmesser ist eine
Eingabe, und die Suche rechnet mit ihm.

### Vier Haken werden einer

Duktilität, sprödes Versagen, Zwängung auf Biegung und Zwängung auf Normalkraft
hatten je einen Schalter pro Lage. Vier Haken für eine Frage, und drei davon
betrafen Lagen, die niemand nachweist. Jetzt ist es einer. Gerechnet werden
beide x-Lagen – die untere trägt das Feld-, die obere das Stützmoment –, in
der Zusammenfassung steht die ungünstigere, und die Herleitung zeigt beide samt
einem Satz, welche entschieden hat.

### Wo gesammelt wird, und wo nicht

Der erste Anlauf liess die Nachweise nur noch das schlechteste Urteil
zurückgeben. Das war die naheliegende Stelle und die falsche: damit war die
Ebene zurück, an der die Bewehrungssuche vor ein paar Runden schon einmal
stehengeblieben ist. Halten zwei Lagen gemeinsam das Minimum, hebt es kein
einzelner Schritt – die Suche sieht eine Ebene und gibt auf, obwohl der
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
Nachweis als eingeschaltet – die Lesart, die nichts wegnimmt, was jemand
verlangt hat. Ein Lastfall dagegen, der nur in y galt, wird **gemeldet** statt
umgedeutet: ihn auf x zu legen hiesse, eine Zahl an einem anderen Querschnitt
anzusetzen als der Benutzer gemeint hat. Eine stillschweigende Milderung ist
genau das, was ein Nachweiswerkzeug nicht tun darf – die Regel steht seit der
Rissanforderung im Code und gilt auch hier.

### Nebenbei

`Protokoll.alle_bloecke()` war ein Generator. Ein Test lief zweimal darüber:
beim zweiten Mal kam nichts, lautlos, und die Prüfung meldete «nicht
gefunden», obwohl es dastand. Ein Name, der eine Sammlung verspricht, muss
zweimal dasselbe liefern – jetzt ist es eine Liste.

---

## 2026-09-21 · Die Abkürzung, die die Suche zweimal fand

Die Bewehrungssuche darf jetzt leere Lagen bewehren – vorher blieb, was auf
null stand, auf null. Das war zu vorsichtig: wer die Bewehrung ermitteln
lässt, will wissen, *wo* welche hingehört. Dazu ein Mindestdurchmesser, damit
kein Stab dünner wird als das, was man verlegen will; null bleibt erlaubt,
denn eine Lage ganz wegzulassen ist eine gültige Antwort.

Damit kam ein Fallstrick, und zwar ein hübscher: **die Menge der Nachweise
hängt an der Bewehrung.** Nimmt man allen Stahl weg, gibt es keine Lage mehr,
der ein Nachweis gälte – und kein Nachweis heisst Rückstand null. Die Suche
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

Zweitens räumte die Arbeitskopie die Platte leer – richtig, denn das Werkzeug
*ermittelt* die Bewehrung und legt nicht zu dem dazu, was zufällig dasteht –,
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
verformten System, und den Widerstand bei N_Rd – der liegt auf der
Resistenzlinie, denn dort steht der Stab an seiner Grenze.

## 2026-09-21 · Luft, und ein Umbruch, der auf die falsche Zahl sah

Aufräumen an der Oberfläche: mehr Abstand zwischen den Tafeln, mehr zwischen
den Kapiteln, und Kapitel, die überall gleich aussehen.

Der Abstand zwischen zwei Tafeln entsteht nicht am Griff, sondern in den
Tafeln selbst – jede gibt auf der Seite nach, an der eine andere steht. So
bleibt der Griff schmal und greifbar, und der Inhalt hat trotzdem Luft.

Bei den Kapiteln fiel auf, dass «Platte» keine Linie links hatte und
«Nachweise» schon: die Linie hing an `.unterkapitel`, und die Platte hat
keines. Statt sieben Aufrufstellen um einen Körper-Container zu erweitern,
sitzt die Linie jetzt an der Gruppe selbst, und die Überschrift holt sich die
Einrückung mit einem negativen Rand zurück. Eine Regel statt sieben Eingriffe.
Die Unterkapitel wurden dafür zu Karten wie die Bewehrungslagen – bei fünf
Nachweiskapiteln untereinander sah man vorher nicht, wo eines aufhört.

Das Padding hat dann etwas ans Licht geholt, das schon länger schief lag: der
Editor klappt in zwei Spalten auf, und der Umbruch hing an einer
`@media`-Abfrage – also an der **Fensterbreite**. Das ist die falsche Zahl.
Die Tafeln sind in der Breite verstellbar; ein breites Fenster sagt nichts
darüber, wie viel Platz eine einzelne Tafel hat. Bei 1600 px Fenster und
420 px Tafel klappte der Editor zweispaltig auf und lief um 200 Pixel über.
Jetzt entscheidet eine `@container`-Abfrage, und sie sieht die Tafel.

Danach blieben 15 Pixel übrig, und auch die hatten einen Grund: die
Einwirkungszeilen standen auf `1fr` für den Namen. Ohne `minmax(0, 1fr)` nimmt
ein Gitter die Mindestbreite des Inhalts, und die Zeile wächst über die Karte
hinaus, statt den Namen zu kürzen.

Der Knopf «Bewehrung ermitteln» hat seine Meldung verloren. Das Ergebnis steht
danach in den Lagen und in der Zusammenfassung – ein Satz daneben sagte
dasselbe ein zweites Mal und blieb stehen, bis man etwas anderes tat. Geht es
nicht auf, meldet es die Zeile oben rechts, dort, wo auch sonst steht, was
schiefging. Aus der Map mit Meldungen wurde ein Set mit Kennungen: der Knopf
muss nur noch wissen, ob er gerade läuft.

Dabei fiel eine Unstimmigkeit auf: eine neue Platte zeigte ein leeres
Teilungsfeld, während der Kern mit 150 mm rechnete. Was man sieht, muss
laufen – die Vorgaben stehen jetzt auch in der neu angelegten Platte.

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
Ergebnis des ersten. Die Suche lief also – nur sah man sie nicht.

Der Zustand der Meldung liegt ausserhalb des Projekts, in einer Map neben der
Tafel: sie beschreibt einen Vorgang und keine Eigenschaft der Platte. Damit
sie sichtbar wird, muss nach dem Eintragen jemand neu zeichnen, und das hing
am Zweig: bei Erfolg tat es `projektAendern`, bei Misserfolg ein eigener
Aufruf. Der Erfolgszweig zeichnete aber schon *vor* dem Eintragen der Meldung
– übernommen wurde das Projekt, und das löst für sich ein Neuzeichnen aus.
Danach stand die Meldung im Speicher und niemand fragte mehr danach. Erst der
nächste Druck zeichnete neu, und zwar als Erstes: also sah man das alte
Ergebnis.

Jetzt steht das Neuzeichnen in einem `finally`. Zuletzt und immer, egal
welcher Zweig gelaufen ist. Das ist die Art Stelle, an der eine
Fallunterscheidung sich rächt, die es gar nicht hätte geben müssen.

Dazu drei Dinge am Bild. Die Schalter stehen jetzt in jedem Kapitel ganz
links, wie bei den Tragsicherheitsnachweisen – das Auge sucht die Spalte
einmal und findet sie danach wieder. Zwischen den Nachweiskapiteln ist Luft;
innerhalb bleibt es eng. Und das Werkzeug steht unter der Platte statt neben
ihr: es liest deren Angaben und schreibt in die Spalte daneben.

Beim Umstellen fiel auf, dass es die Lagenzeile dreimal gab – einmal für die
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
Marke hätte sonst den Wert des Nachbarpunkts gezeigt (170.6 statt 170.1) –
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
