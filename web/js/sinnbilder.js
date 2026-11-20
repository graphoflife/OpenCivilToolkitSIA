/**
 * sinnbilder.js -- die Zeichen auf den Knöpfen: die Kapitel eines Bauteils,
 * die Apps links, die Werkzeuge des Zeichenfensters, die Rechenarten und die
 * Stellungen der Schalter, wo Wörter allein nicht sagen, was gemeint ist.
 *
 * Einfache Linienbilder, 24 × 24, in der Farbe der Schrift: was das Kapitel
 * zeigt oder prüft, auf einen Blick -- die Interaktionslinie, der geknickte
 * Stab, die Druckzone, der Riss; bei den Apps, was sie bearbeiten; bei den
 * Werkzeugen, was sie zeichnen. Selbst gezeichnet; keine fremde Bibliothek
 * und keine Bilddatei.
 *
 * Jedes Zeichen ist eine Liste von Pfaden (`d`), Kreisen (`[cx, cy, r]`),
 * vollen Punkten (`voll`, ebenso) und vollen Flächen (`flaechen`, Pfade,
 * mit Loch nach der Regel evenodd) -- ein Stab ist ein voller Punkt, eine
 * Stütze im Grundriss eine volle Fläche, ein Rohr im Schnitt ein Ring.
 * Gestrichelt wird, was eine Grenze meint oder nicht mitrechnet.
 */

import { svgEl } from './dom.js';

const ACHSEN = 'M4 20h16 M4 20V4';

const ZEICHEN = {
  // M-N-Interaktionslinie: Achsen, die geschlossene Linie, ein Punkt darin.
  tragsicherheit: {
    pfade: ['M3 12h18 M12 3v18',
      'M12 4.5c4.6.6 7 3.8 7 7.5s-2.4 6.9-7 7.5c-4.6-.6-7-3.8-7-7.5s2.4-6.9 7-7.5z'],
    kreise: [[14.5, 10, 1.3]],
  },
  // Ein Stab unter Druck, der ausweicht.
  knicken: {
    pfade: ['M12 2v4 M10 4.2l2 1.8 2-1.8', 'M12 7c4 3.5 4 9.5 0 13', 'M8 21h8'],
    strich: ['M12 7v13'],
  },
  // Querschnitt mit Druckzone oben und ihrer Höhe x daneben.
  duktilitaet: {
    pfade: ['M6 3h11v18H6z', 'M6 8.5h11', 'M7.5 8.5l3-5.5 M11.5 8.5l3-5.5 M15.5 8.5l1.5-2.8',
      'M20 3v5.5 M19 3h2 M19 8.5h2'],
  },
  // Querschnitt, von unten gerissen.
  sproede: {
    pfade: ['M6 3h12v18H6z', 'M12 21l-1.6-3.2 2.2-2.6-1.8-3.2 1.4-2.6'],
  },
  // Ein Träger auf zwei Lagern, gestrichelt seine Biegelinie, dazu der Pfeil w.
  verformung: {
    pfade: ['M3 8h18', 'M4.5 8l-1.6 2.8h3.2z', 'M19.5 8l-1.6 2.8h3.2z',
      'M12 9.5v4.5 M10.8 12.8l1.2 1.2 1.2-1.2'],
    strich: ['M4.5 8Q12 22 19.5 8'],
  },
  // Ein Stab zwischen zwei Wänden, in der Mitte gerissen.
  zwang: {
    pfade: ['M4 5v14 M20 5v14', 'M2 7l2-2 M2 11l2-2 M2 15l2-2 M2 19l2-2',
      'M20 9l2-2 M20 13l2-2 M20 17l2-2 M20 21l2-2',
      'M4 10h7 M13 10h7 M4 14h7 M13 14h7', 'M11.2 9l1.6 2.4-1.6 2.6'],
  },
  // Ein Balken mit Rissen über der Bewehrung.
  quasistaendig: {
    pfade: ['M3 7h18v10H3z', 'M7 17v-3.5 M12 17v-4.5 M17 17v-3.5'],
    strich: ['M3 14.5h18'],
  },
  // Spannung über Dehnung: gerade, dann das Fliessplateau -- und die Grenze.
  haeufig: {
    pfade: [ACHSEN, 'M4 20l6-11h10'],
    strich: ['M4 12.5h16'],
  },
  // Querschnitt und daneben die Spannung aus N und M.
  schnittgroessen: {
    pfade: ['M4 4h5v16H4z', 'M13 4v16', 'M13 4h7l-7 11'],
  },
  // Querschnitt und daneben die Dehnung, gegeben am Rand.
  dehnungen: {
    pfade: ['M4 4h5v16H4z', 'M14 4v16', 'M14 4h5 M14 20h-3', 'M19 4L11 20'],
  },
  // Moment über Krümmung: steil, dann flacher.
  moment_kruemmung: {
    pfade: [ACHSEN, 'M4 20c2-6 4-8.5 7-9.5s6-1.2 9-1.2'],
  },
  // Normalkraft über Dehnung: gerade, dann geknickt.
  normalkraft_dehnung: {
    pfade: [ACHSEN, 'M4 20l4-9 3.5-3H20'],
  },
  // E-Modul über dem Moment: oben flach, dann fallend.
  moment_emodul: {
    pfade: [ACHSEN, 'M4 6h3c3 0 4 3 5 6s3 4 8 4'],
  },
  // E-Modul über der Normalkraft: ein Sprung beim Riss.
  normalkraft_emodul: {
    pfade: [ACHSEN, 'M4 6h6v8h10'],
  },
  // Eine Lupe über zwei Stäben.
  automatik: {
    pfade: ['M14.6 14.6L20.5 20.5'],
    kreise: [[10, 10, 6.2], [8, 11, 1.2], [12, 11, 1.2]],
  },

  // -- Die Apps links ------------------------------------------------------

  // Ein Würfel Beton mit Kies darin.
  material: {
    pfade: ['M12 3l8 4.5v9L12 21l-8-4.5v-9z', 'M4 7.5l8 4.5 8-4.5 M12 12v9'],
    kreise: [[7.5, 13.5, 0.8], [9, 16.5, 0.8], [15.5, 15, 0.8]],
  },
  // Eine Platte im Schnitt, die Bewehrung unten.
  platte: {
    pfade: ['M3 8.5h18v7H3z'],
    kreise: [[6.5, 13, 0.9], [10.5, 13, 0.9], [14.5, 13, 0.9], [18.5, 13, 0.9]],
  },
  // Ein gezeichneter Querschnitt: ein T mit Stäben.
  analyse: {
    pfade: ['M4 4h16v5h-5v11H9V9H4z'],
    kreise: [[11, 17.5, 0.9], [13, 17.5, 0.9], [6.5, 6.5, 0.9], [17.5, 6.5, 0.9]],
  },
  // Ein Rahmen, links eingespannt, rechts gelenkig.
  balkensystem: {
    pfade: ['M6 18V6h12v12', 'M3.5 18h5 M3.5 20l1-2 M5.5 20l1-2 M7.5 20l1-2',
      'M18 18l-2 3h4z'],
  },
  // Ein Rahmen im Raum, schräg von oben: vier Stützen, oben ein Rost --
  // gestrichelt die Stütze hinten links, die hinter dem Rahmen steht.
  balkensystem3d: {
    pfade: ['M3.5 20V10h11v10', 'M3.5 10l6-5h11l-6 5', 'M20.5 5v10'],
    strich: ['M9.5 5v10'],
  },
  // Eine Decke im Grundriss: ein L, gestrichelt geteilt in Streifen beider Richtungen.
  decke: {
    pfade: ['M3.5 3.5h17v8h-8v9h-9z'],
    strich: ['M8 3.5v17 M3.5 8h17 M3.5 16h9'],
  },
  // Eine Platte auf einer Stütze, darin gestrichelt der Kegel, der durchstanzt.
  durchstanzen: {
    pfade: ['M2.5 7h19v5h-19z', 'M10 12h4v9h-4z'],
    strich: ['M6 7l4 5 M18 7l-4 5'],
  },
  // Ein Fundament im Boden, darauf die Last, darunter gestrichelt der
  // Gleitkörper bis ins Gelände daneben.
  grundbruch: {
    pfade: ['M9.5 6h6v6.5h-6z', 'M12.5 1.5v3.2 M11 3.4l1.5 1.5 1.5-1.5', 'M2.5 9.5h7 M15.5 9.5h6'],
    strich: ['M15.5 12.5C14.5 20 6 19.5 3 9.5'],
  },
  // Ein Fundament auf zwei Schichten, darunter gestrichelt, wie es sich setzt.
  setzung: {
    pfade: ['M8 3.5h8v4.5H8z', 'M2.5 8h19 M2.5 13.5h19 M2.5 19h19'],
    strich: ['M5 10.5Q12 16.5 19 10.5'],
  },
  // Ein Pfahl durch zwei Schichten, gestrichelt ihre Grenze, darauf die Last.
  pfahl: {
    pfade: ['M10 6h4v15.5h-4z', 'M12 1v3.6 M10.5 3.2l1.5 1.5 1.5-1.5', 'M2.5 8h7.5 M14 8h7.5'],
    strich: ['M2.5 14.5h7.5 M14 14.5h7.5'],
  },
  // Eine Konsole: die Aufforderung und eine Zeile dahinter.
  python: {
    pfade: ['M3 4.5h18v15H3z', 'M6.5 9l3 3-3 3', 'M11.5 15.5h5'],
  },

  // -- Die Knöpfe des Balkensystems -------------------------------------------

  // Ein Walzprofil im Schnitt.
  querschnitte: {
    pfade: ['M5 4h14v3.2h-5.4v9.6H19V20H5v-3.2h5.4V7.2H5z'],
  },
  // Ein Balken, darauf drei Lasten.
  lastfaelle: {
    pfade: ['M3 17h18', 'M6 4v9 M4.5 11.2L6 13l1.5-1.8', 'M12 4v9 M10.5 11.2L12 13l1.5-1.8',
      'M18 4v9 M16.5 11.2L18 13l1.5-1.8'],
  },
  // Das Summenzeichen: Lastfälle mal Beiwert, zusammengezählt.
  kombinationen: {
    pfade: ['M17.5 5H7l5.5 7L7 19h10.5'],
  },
  // Ein Träger auf zwei Lagern, darunter sein Moment.
  statik: {
    pfade: ['M3 7h18', 'M3 7l-1.6 2.6h3.2z M21 7l-1.6 2.6h3.2z', 'M3 7Q12 25 21 7'],
  },

  // -- Die Knöpfe der Decke ---------------------------------------------------

  // Die Streifen: eine Platte, gestrichelt in beide Richtungen geteilt.
  streifen: {
    pfade: ['M3.5 3.5h17v17h-17z'],
    strich: ['M9 3.5v17 M15 3.5v17 M3.5 9h17 M3.5 15h17'],
  },
  // Die Ergebnisse: die Platte, gestrichelt ein Schnitt durch sie und
  // darüber der Verlauf längs ihm -- wie beim Werkzeug, das ihn zeichnet.
  ergebnisse: {
    pfade: ['M3.5 3.5h17v17h-17z', 'M3.5 16C7 5 17 5 20.5 16'],
    strich: ['M3.5 16h17'],
  },

  // -- Die Werkzeuge des Zeichenfensters -----------------------------------

  // Ein Umriss mit seinen Ecken.
  'cad-polygon': {
    pfade: ['M5 19L3.5 7.5l9-4 8 6.5-4.5 9z'],
  },
  // Ein Balken im Schnitt, unten seine Stäbe.
  'cad-bewehrung': {
    pfade: ['M6 3h12v18H6z'],
    voll: [[9.2, 16.6, 1.6], [14.8, 16.6, 1.6], [9.2, 7.4, 1.2], [14.8, 7.4, 1.2]],
  },
  // Stäbe auf einer Linie -- eine Linienbewehrung.
  'cad-linienbewehrung': {
    pfade: ['M3 12h18'],
    voll: [[6, 12, 2], [12, 12, 2], [18, 12, 2]],
  },
  // Ein einzelner Stab.
  'cad-punktbewehrung': {
    pfade: ['M12 3.5v3.5 M12 17v3.5 M3.5 12H7 M17 12h3.5'],
    voll: [[12, 12, 3]],
  },
  // Eine Wand als Band, gestrichelt ihre Achse -- wie in der Zeichnung.
  'cad-schubwand': {
    pfade: ['M3 7.5h18v9H3z'],
    strich: ['M5 12h14'],
  },
  // Ein Punkt zum Konstruieren: klein, gestrichelt umkreist -- er rechnet nicht mit.
  'cad-hilfspunkt': {
    strich: ['M12 5a7 7 0 1 1 0 14a7 7 0 1 1 0-14'],
    voll: [[12, 12, 2]],
  },
  // Eine Linie, die nicht mitrechnet: gestrichelt, mit ihren Enden.
  'cad-hilfslinie': {
    strich: ['M5.5 18.5l13-13'],
    kreise: [[4.5, 19.5, 1.6], [19.5, 4.5, 1.6]],
  },
  // Eine Vorlage: ein Blatt mit einem T-Balken.
  'cad-vorlage': {
    pfade: ['M4 3.5h16v17H4z', 'M7.5 8h9 M12 8v8.5'],
  },
  // Ein Stab des Rahmens zwischen zwei Knoten.
  'cad-linie': {
    pfade: ['M6 18L18 6'],
    voll: [[5, 19, 2], [19, 5, 2]],
  },
  // Ein Knoten.
  'cad-knoten': {
    kreise: [[12, 12, 6]],
    voll: [[12, 12, 2.2]],
  },
  // Eine Wand unter der Platte: eine Linie, auf der einen Seite schraffiert.
  'cad-wand': {
    pfade: ['M3 9h18', 'M5 9l-2 3 M9 9l-2 3 M13 9l-2 3 M17 9l-2 3 M21 9l-2 3'],
    voll: [[3, 9, 1.6], [21, 9, 1.6]],
  },
  // Ein versteckter Unterzug: ein breites Band, gestrichelt seine Achse.
  'cad-unterzug': {
    pfade: ['M3 8.5h18 M3 15.5h18'],
    strich: ['M3 12h18'],
  },
  // Ein Schnitt: oben die Linie, gestrichelt, mit ihren Enden -- darunter der Verlauf längs ihr.
  'cad-schnitt': {
    strich: ['M5 5h14'],
    pfade: ['M3 3v4 M21 3v4', 'M3 12h18', 'M3 12c3.5 9.5 14.5 9.5 18 0'],
  },
  // Eine Stütze im Grundriss: ein Quadrat mit Kreuz.
  'cad-stuetze': {
    pfade: ['M7 7h10v10H7z', 'M7 7l10 10 M17 7L7 17'],
  },
  // Eine Zone: ein Umriss, darin die Last zu Teilen in die zwei Richtungen.
  'cad-zone': {
    pfade: ['M4 4.5h16v15H4z', 'M8 12h8 M14 10l2 2-2 2', 'M12 8v8 M10 14l2 2 2-2'],
  },
  // Eine Flächenlast: ein gestrichelter Umriss, darin Pfeile nach unten.
  'cad-flaechenlast': {
    strich: ['M3.5 4.5h17v15h-17z'],
    pfade: ['M8 8v7 M6.3 13.3L8 15l1.7-1.7', 'M12 8v7 M10.3 13.3L12 15l1.7-1.7',
      'M16 8v7 M14.3 13.3L16 15l1.7-1.7'],
  },
  // Eine Linienlast: Pfeile auf eine kräftige Linie.
  'cad-linienlast': {
    pfade: ['M3 18.5h18', 'M3 17.5h18', 'M6 4v10 M4.3 12.3L6 14l1.7-1.7', 'M12 4v10 M10.3 12.3L12 14l1.7-1.7',
      'M18 4v10 M16.3 12.3L18 14l1.7-1.7'],
  },
  // Eine Punktlast: ein Pfeil auf einen Punkt.
  'cad-punktlast': {
    pfade: ['M12 3v13 M8.5 12.5L12 16l3.5-3.5'],
    voll: [[12, 19.5, 2]],
  },
  // Eine Last: drei Pfeile auf einen Stab.
  'cad-last': {
    pfade: ['M3 19.5h18', 'M5 4.5h14',
      'M6 4.5v10 M3.8 12.3L6 14.5l2.2-2.2', 'M12 4.5v10 M9.8 12.3L12 14.5l2.2-2.2',
      'M18 4.5v10 M15.8 12.3L18 14.5l2.2-2.2'],
  },
  'cad-rueckgaengig': {
    pfade: ['M8.5 5.5L4 10l4.5 4.5', 'M4 10h11a5 5 0 0 1 0 10h-4'],
  },
  'cad-wiederholen': {
    pfade: ['M15.5 5.5L20 10l-4.5 4.5', 'M20 10H9a5 5 0 0 0 0 10h4'],
  },
  // Alles ins Bild: vier Ecken um ein Stück Zeichnung.
  'cad-alles': {
    pfade: ['M4 9V4h5 M15 4h5v5 M20 15v5h-5 M9 20H4v-5', 'M9 9h6v6H9z'],
  },
  'cad-vollbild': {
    pfade: ['M14 4h6v6 M20 4l-6 6 M10 20H4v-6 M4 20l6-6'],
  },

  // -- Die Rechenarten --------------------------------------------------------
  // Wie eine Rechenart den Beton rechnet: Spannung über Dehnung auf Druck,
  // die Dehnung nach rechts (Benutzer, 2026-11-18: die Wörter allein sagen
  // es nicht). Die Gesetze in querschnitt/werkstoffgesetz.py; das Bild
  // zeichnet sie nach, mit ε_c1d = 2 ‰ und ε_c2d = 3 ‰ an der Achse.

  // Der Spannungsblock: keine Spannung bis 0.15 · ε_c2d, dann f_cd bis ε_c2d.
  'rechenart-block': {
    pfade: [ACHSEN, 'M4 20H6.1V8H18'],
  },
  // Parabel bis ε_c1d, dann waagrecht bis ε_c2d.
  'rechenart-parabel': {
    pfade: [ACHSEN, 'M4 20Q8.67 8 13.33 8H18'],
  },
  // Gerade bis f_c, dann waagrecht -- ohne Ende.
  'rechenart-elastisch': {
    pfade: [ACHSEN, 'M4 20L15 6.5H20'],
  },
  // Die Handrechnung: eine Hand, die eine Formel hält. Sie rechnet mit dem
  // Block, aber in geschlossenen Formeln.
  'rechenart-handrechnung': {
    pfade: ['M2.5 13h2.5v8.5H2.5z', 'M5 14h5.5a1.8 1.8 0 0 1 0 3.6H8',
      'M5 20.5h8.5l6.3-3.6a1.5 1.5 0 0 0-1.5-2.6l-4.6 2.6',
      'M7.5 3.5l3.5 5 M11 3.5l-3.5 5', 'M13.5 5h4 M13.5 7h4'],
  },

  // -- Die Stellungen der Schalter ---------------------------------------------
  // Je Stellung ihr Bild, `art-wert` (Benutzer, 2026-11-19: die Bedienung
  // erklärt sich selbst). Jede Stellung des Katalogs hat ihres -- das prüft
  // tests/test_bauteilarten.py.

  // Wo die Stütze in der Platte steht, von oben: gestrichelt läuft die Platte
  // weiter, ausgezogen ist ihr Rand -- wie im Kern unten (y negativ), bei der
  // Ecke dazu links. Die Wand läuft nach rechts, die Wandecke nach rechts und
  // oben (durchstanzen/flaeche.py).
  'lage-innen': {
    strich: ['M3 3h18v18H3z'],
    flaechen: ['M9 9h6v6H9z'],
  },
  'lage-rand': {
    strich: ['M3 21V3h18v18'],
    pfade: ['M3 21h18'],
    flaechen: ['M9 11h6v6H9z'],
  },
  'lage-ecke': {
    strich: ['M3 3h18v18'],
    pfade: ['M3 3v18h18'],
    flaechen: ['M7 11h6v6H7z'],
  },
  'lage-wandende': {
    strich: ['M3 3h18v18H3z'],
    flaechen: ['M21 10.5H10v3h11z'],
  },
  'lage-wandecke': {
    strich: ['M3 3h18v18H3z'],
    flaechen: ['M21 15H9V3h3v9h9z'],
  },
  // Die Form der Stütze im Grundriss; das Oval ist ein Rechteck mit halbrunden Enden.
  'stuetzenform-rechteck': {
    pfade: ['M6 8h12v8H6z'],
  },
  'stuetzenform-rund': {
    kreise: [[12, 12, 6]],
  },
  'stuetzenform-oval': {
    pfade: ['M10 8h4a4 4 0 0 1 0 8h-4a4 4 0 0 1 0-8z'],
  },
  // Der Kopf eines Pfahls: frei drehbar auf einem Gelenk, eingespannt in einer
  // Platte -- gestrichelt, wie weit er in ihr steckt.
  'kopf-frei': {
    pfade: ['M10 7.5v14h4v-14'],
    kreise: [[12, 5, 2.5]],
  },
  'kopf-eingespannt': {
    pfade: ['M3 3h18v6H3z', 'M10 9v12.5h4V9'],
    strich: ['M10 9V5 M14 9V5'],
  },
  // Das Tragglied im Schnitt: das Rohr ein Ring, der Vollstab eine Scheibe.
  'tragglied-rohr': {
    flaechen: ['M4.5 12a7.5 7.5 0 1 0 15 0a7.5 7.5 0 1 0-15 0z M7.5 12a4.5 4.5 0 1 0 9 0a4.5 4.5 0 1 0-9 0z'],
  },
  'tragglied-stab': {
    voll: [[12, 12, 7.5]],
  },
  // Das Fundament im Grundriss und wo die Setzung gilt: starr im Punkt K,
  // 0.13 L und 0.13 B von einer Ecke (gestrichelt die Abstände, hier
  // grösser, damit man sie sieht), schlaff in der Mitte.
  'setzung-starr': {
    pfade: ['M3 6h18v12H3z'],
    strich: ['M3 14.5h3.5 M7 18v-3'],
    voll: [[7.2, 14.4, 1.9]],
  },
  'setzung-schlaff': {
    pfade: ['M3 6h18v12H3z'],
    voll: [[12, 12, 1.9]],
  },
  // Grund und Zulage einer Lage im Schnitt: ausgezogen die Seite der Platte,
  // gestrichelt die Kante, an der beide Stäbe bündig liegen. Ungünstig rückt
  // der dünnere von der Seite weg, günstig liegen beide an der Überdeckung.
  'zulage-unten-unguenstig': {
    pfade: ['M2 21h20'], strich: ['M2 7h20'], voll: [[8, 11, 4], [16.5, 9.2, 2.2]],
  },
  'zulage-unten-guenstig': {
    pfade: ['M2 21h20'], strich: ['M2 15h20'], voll: [[8, 11, 4], [16.5, 12.8, 2.2]],
  },
  'zulage-oben-unguenstig': {
    pfade: ['M2 3h20'], strich: ['M2 17h20'], voll: [[8, 13, 4], [16.5, 14.8, 2.2]],
  },
  'zulage-oben-guenstig': {
    pfade: ['M2 3h20'], strich: ['M2 9h20'], voll: [[8, 13, 4], [16.5, 11.2, 2.2]],
  },
  // Eine Einlage in der Platte, im Schnitt, darüber ihr grösstes Mass.
  einlage: {
    pfade: ['M2 4h20 M2 20h20', 'M7 12.5h10v4.5H7z', 'M7 6.5v3 M17 6.5v3 M7 8h10'],
  },
  // Wie die Stäbe auf einer Linie liegen: verschmiert ein Band; n Stäbe
  // gleich verteilt, das Mass über die ganze Linie; im Abstand s, das Mass
  // zwischen zweien.
  'linie-flaeche': {
    flaechen: ['M3 10.5h18v3H3z'],
  },
  'linie-anzahl': {
    pfade: ['M4 13.5h16', 'M4 7.5h16 M4 6v3 M20 6v3'],
    voll: [[4, 13.5, 1.8], [9.33, 13.5, 1.8], [14.67, 13.5, 1.8], [20, 13.5, 1.8]],
  },
  'linie-teilung': {
    pfade: ['M4 13.5h16', 'M9.33 7.5h5.34 M9.33 6v3 M14.67 6v3'],
    voll: [[4, 13.5, 1.8], [9.33, 13.5, 1.8], [14.67, 13.5, 1.8], [20, 13.5, 1.8]],
  },
  // Die Linie mit ihren Enden: ein Stab genau am Anfang, das Ende frei -- und
  // umgekehrt. Der Strich steht nur am freien Ende; mit einem an beiden Enden
  // sahen sich die zwei Bilder in 18 px zu ähnlich.
  'linie-starteisen': {
    pfade: ['M4 12h16', 'M20 8v8'],
    voll: [[4, 12, 2.3], [9.33, 12, 1.6], [14.67, 12, 1.6]],
  },
  'linie-endeisen': {
    pfade: ['M4 12h16', 'M4 8v8'],
    voll: [[9.33, 12, 1.6], [14.67, 12, 1.6], [20, 12, 2.3]],
  },
  // Der Querschnitt mit seiner Druckzone, voll: über einer waagrechten
  // Nulllinie, wenn er nur um y gebogen wird, sonst über einer schiefen.
  'biegung-einachsig': {
    pfade: ['M7 3h10v18H7z', 'M3 10h18'],
    flaechen: ['M7 3h10v7H7z'],
  },
  'biegung-zweiachsig': {
    pfade: ['M7 3h10v18H7z', 'M3 14L21 6'],
    flaechen: ['M7 3h10v4.78L7 12.22z'],
  },
};

/**
 * Ein Zeichen als SVG -- `name` aus der Liste oben. Einen unbekannten Namen
 * meldet es laut: bis 2026-11-20 stand dann ein leerer Knopf da, und keiner
 * merkte es (die Kachel «Ergebnisse» der Decke).
 */
export function sinnbild(name) {
  const z = ZEICHEN[name];
  if (!z) throw new Error(`sinnbilder.js: kein Zeichen «${name}».`);
  const svg = svgEl('svg', {
    viewBox: '0 0 24 24', class: 'sinnbild', 'aria-hidden': 'true',
    fill: 'none', stroke: 'currentColor', 'stroke-width': 1.6,
    'stroke-linecap': 'round', 'stroke-linejoin': 'round',
  });
  for (const d of z.pfade || []) svg.append(svgEl('path', { d }));
  for (const d of z.strich || []) svg.append(svgEl('path', { d, 'stroke-dasharray': '2 2' }));
  for (const [cx, cy, r] of z.kreise || []) svg.append(svgEl('circle', { cx, cy, r }));
  for (const [cx, cy, r] of z.voll || []) {
    svg.append(svgEl('circle', { cx, cy, r, fill: 'currentColor', stroke: 'none' }));
  }
  for (const d of z.flaechen || []) {
    svg.append(svgEl('path', { d, fill: 'currentColor', 'fill-rule': 'evenodd' }));
  }
  return svg;
}
