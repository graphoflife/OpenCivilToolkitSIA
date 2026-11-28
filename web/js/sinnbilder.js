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

// Was ein Stab ohne Imperfektion trüge, χ über λ̄ bis 2.5: eins bis λ̄ = 1,
// dann nach Euler 1/λ̄² -- die Grenze, unter der jede Knickspannungskurve liegt.
const EULER = 'M4 5L10.4 5L11.7 9.6L13 12.3L14.2 14.1L15.5 15.4L16.8 16.2L18.1 16.9L20 17.6';

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
  // Ein Stahlträger im Schnitt, der seitlich ausweicht und sich dabei
  // verdreht -- gestrichelt, wo er stand: Knicken und Kippen.
  stabilitaet: {
    pfade: ['M13.6 4.1L21.2 6.8 M8.8 17.2L16.4 19.9 M17.4 5.4L12.6 18.6'],
    strich: ['M4 5h8 M4 19h8 M8 5v14'],
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
  // Eine Wandscheibe, gestrichelt, darin ihr Fachwerk: zwei Streben, oben
  // der Druckgurt, unten das Zugband -- auf zwei Lagern.
  fachwerkmodell: {
    strich: ['M3 3.5h18v13H3z'],
    pfade: ['M5 16.5L9 7h6l4 9.5z', 'M5 16.5l-2 3.5h4z M19 16.5l-2 3.5h4z'],
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
  // Ein Gebäude mit drei Geschossen, links eine Kraft auf das oberste,
  // darunter der Boden, der bebt.
  erdbeben: {
    pfade: ['M9 4h9v14H9z', 'M9 8.7h9 M9 13.3h9', 'M2.5 6.3h4.5 M5.3 4.6l1.7 1.7-1.7 1.7',
      'M2.5 18h19', 'M3 21.3l2-1.6 2 1.6 2-1.6 2 1.6 2-1.6 2 1.6 2-1.6 2 1.6'],
  },
  // Eine Mappe: die Projekte einer Datei.
  projekte: {
    pfade: ['M3 6h6l2 2.5h10V19H3z', 'M3 11h18'],
  },
  // Eine Konsole: die Aufforderung und eine Zeile dahinter.
  python: {
    pfade: ['M3 4.5h18v15H3z', 'M6.5 9l3 3-3 3', 'M11.5 15.5h5'],
  },
  // Ein Zahnrad mit acht Zähnen: die Einstellungen oben rechts.
  einstellungen: {
    pfade: ['M10.1 5 10.6 2.5 13.4 2.5 13.9 5 15.6 5.8 17.7 4.3 19.7 6.3 18.2 8.4 19 10.1 '
      + '21.5 10.6 21.5 13.4 19 13.9 18.2 15.6 19.7 17.7 17.7 19.7 15.6 18.2 13.9 19 '
      + '13.4 21.5 10.6 21.5 10.1 19 8.4 18.2 6.3 19.7 4.3 17.7 5.8 15.6 5 13.9 2.5 13.4 '
      + '2.5 10.6 5 10.1 5.8 8.4 4.3 6.3 6.3 4.3 8.4 5.8z'],
    kreise: [[12, 12, 3]],
  },

  // -- Die Kacheln der Eingaben: Durchstanzen, Grundbruch, Setzung, Pfahl,
  //    Erdbeben. Was die Gruppe beschreibt, im Schnitt oder von oben. ------

  // Die Stütze von oben, gestrichelt um sie herum der Nachweisschnitt.
  stuetze: {
    flaechen: ['M9.5 9.5h5v5h-5z'],
    strich: ['M4.5 8.5a4 4 0 0 1 4-4h7a4 4 0 0 1 4 4v7a4 4 0 0 1-4 4h-7a4 4 0 0 1-4-4z'],
  },
  // Die Biegebewehrung von oben: Stäbe in beiden Richtungen.
  biegebewehrung: {
    pfade: ['M3 7h18 M3 12h18 M3 17h18', 'M7 3v18 M12 3v18 M17 3v18'],
  },
  // Die Platte dreht sich um die Stütze: gestrichelt, wo sie unverformt läge.
  rotation: {
    pfade: ['M10 12.5L2.5 15.5 M14 12.5l7.5 3', 'M10 12.5v9 M14 12.5v9'],
    strich: ['M2.5 12.5h19'],
  },
  // Die Auflagerkraft: eine Kraft auf die Platte über der Stütze.
  einwirkung: {
    pfade: ['M3 10.5h18v4H3z', 'M10 14.5v7 M14 14.5v7', 'M12 2.5v5.5 M10.3 6.3 12 8l1.7-1.7'],
  },
  // Die Platte im Schnitt über der Stütze, daneben zwei Anker mit ihren Köpfen.
  durchstanzbewehrung: {
    pfade: ['M2 4.5h20v9.5H2z', 'M12 7v4.5 M10.4 7h3.2 M10.4 11.5h3.2',
      'M17.5 7v4.5 M15.9 7h3.2 M15.9 11.5h3.2'],
    flaechen: ['M3 14h5v7.5H3z'],
  },
  // Woraus die Durchstanzbewehrung besteht: Doppelkopfanker -- bei HDB mit
  // der Montageleiste unter den Köpfen, wie er auf der Schalung steht --,
  // oder ein Bügel um vier Stäbe der Biegebewehrung, im Schnitt.
  'system-ancoplus': {
    pfade: ['M8 6v12 M16 6v12'],
    flaechen: ['M5 4h6v2.2H5z M5 17.8h6V20H5z M13 4h6v2.2h-6z M13 17.8h6V20h-6z'],
  },
  'system-hdb': {
    pfade: ['M8 5v11 M16 5v11'],
    flaechen: ['M5 3h6v2.2H5z M5 15.8h6V18H5z M13 3h6v2.2h-6z M13 15.8h6V18h-6z',
      'M2.5 18h19v2.2h-19z'],
  },
  'system-buegel': {
    pfade: ['M8.5 4h7a2.5 2.5 0 0 1 2.5 2.5v11a2.5 2.5 0 0 1-2.5 2.5h-7A2.5 2.5 0 0 1 6 17.5v-11A2.5 2.5 0 0 1 8.5 4z'],
    voll: [[9, 7, 1.5], [15, 7, 1.5], [9, 17, 1.5], [15, 17, 1.5]],
  },
  // Der Boden: Körner unter dem Gelände.
  boden: {
    pfade: ['M3 6h18'],
    kreise: [[6.5, 10.5, 1.6], [12, 10, 1.1], [17.5, 11, 1.8], [8.8, 15.8, 1.3],
      [14.6, 16, 1.6], [19.2, 18.6, 1], [4.6, 19.2, 1.1], [11.2, 20.2, 0.9]],
  },
  // Ein Fundament im Schnitt: die Stütze darauf, das Gelände daneben.
  fundament: {
    pfade: ['M10.5 3v8.5 M13.5 3v8.5', 'M5 11.5h14v5H5z', 'M2.5 8h8 M13.5 8h8'],
  },
  // Das Gelände, das abfällt, und tiefer der Spiegel des Grundwassers.
  gelaende: {
    pfade: ['M2.5 6.5h8l11 5', 'M6 13.8h3l-1.5 2.6z', 'M6.3 19.6h2.4 M6.9 21.2h1.2'],
    strich: ['M2.5 17.5h19'],
  },
  // Der Spiegel des Grundwassers: das Dreieck über der Linie.
  grundwasser: {
    pfade: ['M8 5.5h8l-4 6z', 'M2.5 12.5h19', 'M6 16h12 M8.5 19.5h7'],
  },
  // Ein Fundament, das in seiner Sohle gleitet: die Kraft T, darunter die Fuge.
  sohlreibung: {
    pfade: ['M8 6h11v7H8z', 'M2.5 13h19', 'M3.5 16l2.5-3 M8 16l2.5-3 M12.5 16l2.5-3 M17 16l2.5-3',
      'M2 9.5h5 M5.3 7.8 7 9.5l-1.7 1.7'],
  },
  // Die Pressung in der Sohle: der Boden drückt von unten gegen das Fundament.
  pressung: {
    pfade: ['M4 4.5h16v5H4z', 'M4 18.5h16', 'M7 18.5v-7 M5.6 12.9 7 11.5l1.4 1.4',
      'M12 18.5v-7 M10.6 12.9 12 11.5l1.4 1.4', 'M17 18.5v-7 M15.6 12.9 17 11.5l1.4 1.4'],
  },
  // Schichten übereinander: Sand, Silt, Kies.
  schichten: {
    pfade: ['M2.5 3.5h19 M2.5 9.5h19 M2.5 15.5h19 M2.5 21.5h19',
      'M4.5 14l3-3 M10 14l3-3 M15.5 14l3-3'],
    voll: [[6, 6.5, 0.8], [10, 6.5, 0.8], [14, 6.5, 0.8], [18, 6.5, 0.8]],
    kreise: [[6.5, 18.5, 1.4], [12, 18.5, 1.4], [17.5, 18.5, 1.4]],
  },
  // Der Pfahl im Schnitt: der Kreis, darin die Längsstäbe.
  pfahlquerschnitt: {
    kreise: [[12, 12, 9]],
    voll: [[18, 12, 1.2], [16.2, 16.2, 1.2], [12, 18, 1.2], [7.8, 16.2, 1.2], [6, 12, 1.2],
      [7.8, 7.8, 1.2], [12, 6, 1.2], [16.2, 7.8, 1.2]],
  },
  // Der äussere Widerstand: der Boden trägt den Pfahl am Mantel und am Fuss.
  widerstand: {
    pfade: ['M10 3h4v15h-4z', 'M2.5 5.5h7.5 M14 5.5h7.5', 'M6.5 16V9 M5.1 10.4 6.5 9l1.4 1.4',
      'M17.5 16V9 M16.1 10.4 17.5 9l1.4 1.4', 'M12 22.5v-3 M10.6 20.9 12 19.5l1.4 1.4'],
  },
  // Der Fuss des Pfahls: der Boden drückt von unten gegen ihn.
  pfahlfuss: {
    pfade: ['M9 2.5V13h6V2.5', 'M9 21.5V16 M7.6 17.4 9 16l1.4 1.4',
      'M12 21.5V16 M10.6 17.4 12 16l1.4 1.4', 'M15 21.5V16 M13.6 17.4 15 16l1.4 1.4'],
  },
  // Eine Kraft quer auf den Kopf des Pfahls.
  querlast: {
    pfade: ['M10.5 4h3v17.5h-3z', 'M2.5 10h8 M13.5 10h8', 'M2.5 6h6 M6.9 4.4 8.5 6l-1.6 1.6'],
  },
  // Der Standort: eine Marke auf der Karte.
  standort: {
    pfade: ['M12 21.5s6.5-6.4 6.5-11.5a6.5 6.5 0 0 0-13 0c0 5.1 6.5 11.5 6.5 11.5z'],
    kreise: [[12, 10, 2.3]],
  },
  // Kraft über Verschiebung: elastisch, dann plastisch -- gestrichelt, wie
  // weit es elastisch ginge.
  verhaltensbeiwert: {
    pfade: [ACHSEN, 'M4 20l5-9h11'],
    strich: ['M9 11l4-7'],
  },
  // Eine Schwingung über eine Periode, darunter ihre Dauer T.
  schwingzeit: {
    pfade: ['M3 11C5.5 3 9.5 3 12 11s6.5 8 9 0', 'M3 20.5h18 M3 19v3 M21 19v3'],
  },
  // Ein Gebäude in der Ansicht, gestrichelt seine Symmetrieachse.
  regelmaessigkeit: {
    pfade: ['M5 21V6h14v15', 'M5 11h14 M5 16h14', 'M2.5 21h19'],
    strich: ['M12 2.5v20'],
  },
  // Die Geschosse: Decken übereinander, von unten gezählt.
  geschosse: {
    pfade: ['M4 4.5h16 M4 10h16 M4 15.5h16', 'M6 4.5V21 M18 4.5V21', 'M2.5 21h19'],
  },
  // Ein Kern im Grundriss: ein U aus drei Wänden und daneben eine Wand für
  // sich -- ein Teil, der sich um seinen eigenen Schwerpunkt biegt.
  // Gestrichelt der Umriss des Geschosses.
  kern: {
    strich: ['M3 3h18v18H3z'],
    flaechen: ['M5.5 5.5h8v2.3H7.8v6.4h5.7v2.3h-8z', 'M16.5 9H19v10h-2.5z'],
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

  // Das Verfahren: eine Platte, links in Streifen geteilt (gestrichelt),
  // rechts in Dreiecke -- die zwei Wege, sie zu rechnen.
  verfahren: {
    pfade: ['M3.5 3.5h17v17h-17z', 'M12 3.5v17', 'M12 12h8.5 M12 3.5l8.5 8.5 M12 12l8.5 8.5'],
    strich: ['M7.75 3.5v17 M3.5 7.75h8.5 M3.5 16.25h8.5'],
  },
  // Die Stellungen des Schalters: die Streifenmethode -- die Platte
  // gestrichelt in beide Richtungen geteilt -- und die FEM, ein Netz aus
  // Dreiecken.
  'verfahren-streifen': {
    pfade: ['M3.5 3.5h17v17h-17z'],
    strich: ['M9 3.5v17 M15 3.5v17 M3.5 9h17 M3.5 15h17'],
  },
  'verfahren-fem': {
    pfade: ['M3.5 3.5h17v17h-17z', 'M12 3.5v17 M3.5 12h17',
      'M3.5 3.5L20.5 20.5 M12 3.5L20.5 12 M3.5 12L12 20.5'],
  },

  // -- Die Knöpfe des Fachwerkmodells -----------------------------------------

  // Das Verfahren: Knoten im Raster, gestrichelt Stäbe, die möglich sind,
  // kräftig die gewählten -- ein Bogen mit Zugband.
  'fw-verfahren': {
    strich: ['M4.5 5h15 M4.5 5l7.5 7 M19.5 5l-7.5 7 M4.5 12h15'],
    pfade: ['M4.5 19L12 5l7.5 14z'],
    voll: [[4.5, 5, 1.3], [12, 5, 1.3], [19.5, 5, 1.3], [4.5, 12, 1.3], [12, 12, 1.3],
      [19.5, 12, 1.3], [4.5, 19, 1.3], [12, 19, 1.3], [19.5, 19, 1.3]],
  },
  // Die Stellungen des Schalters: Ground Structure -- das Raster der Knoten,
  // gestrichelt, was möglich ist, kräftig der Bogen mit Zugband, den die
  // Optimierung wählt --, und SIMP: in der Scheibe, gestrichelt, voll die
  // Form, die das Material annimmt, ein Bogen auf einem Band.
  'fw-verfahren-ground_structure': {
    strich: ['M4.5 12h15 M4.5 5l15 14 M19.5 5l-15 14'],
    pfade: ['M4.5 19L12 5l7.5 14z'],
    voll: [[4.5, 5, 1.3], [12, 5, 1.3], [19.5, 5, 1.3], [4.5, 12, 1.3], [12, 12, 1.3],
      [19.5, 12, 1.3], [4.5, 19, 1.3], [12, 19, 1.3], [19.5, 19, 1.3]],
  },
  'fw-verfahren-simp': {
    strich: ['M3.5 4.5h17v15h-17z'],
    flaechen: ['M3.5 19.5Q12 -1.5 20.5 19.5h-4Q12 7.5 7.5 19.5z', 'M3.5 17h17v2.5h-17z'],
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
  // Ein T-Balken, dessen Umriss noch offen ist: der Querschnitt, wie man ihn
  // zeichnet -- Ecke um Ecke, der Stift unten rechts am Steg.
  'cad-querschnitt': {
    pfade: ['M9.5 20V9H3V4h18v5h-4.5v6'],
    voll: [[9.5, 20, 1.3], [16.5, 15, 1.7]],
  },
  // Ein Walzprofil im Schnitt -- ein I.
  'cad-stahlprofil': {
    pfade: ['M5.5 4h13v3h-5v10h5v3h-13v-3h5V7h-5z'],
  },
  // Eine Blechverbunddecke im Schnitt: der Beton über seinem Trapezblech.
  'cad-blechdecke': {
    pfade: ['M2.5 5.5h19 M2.5 5.5v12 M21.5 5.5v6',
      'M2.5 17.5h3l2.5-6h4l2.5 6h3l2.5-6h1.5'],
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
  // Ein Spannglied im Schnitt: das Hüllrohr mit seinen Litzen.
  'cad-spannglied': {
    kreise: [[12, 12, 7.5]],
    voll: [[12, 9.2, 2], [9.6, 13.6, 2], [14.4, 13.6, 2]],
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
  // Ein Schnitt: ein Querschnitt, strichpunktiert die Strecke quer durch ihn,
  // aus ihrer Mitte der Pfeil zum Teil, den sie abtrennt.
  'cad-schnitt': {
    pfade: ['M5 4h14v16H5z', 'M2.5 13h3 M7.5 13h2 M11.5 13h1 M14.5 13h2 M18.5 13h3',
      'M12 12V6.5 M10.3 8.2L12 6.5l1.7 1.7'],
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
  // Ein Träger: ein breites Band, gestrichelt seine Achse.
  'cad-traeger': {
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
  // Eine Scheibe: ein Umriss aus vier Ecken.
  'cad-scheibe': {
    pfade: ['M3.5 20V4h17v16z'],
    voll: [[3.5, 20, 1.5], [3.5, 4, 1.5], [20.5, 4, 1.5], [20.5, 20, 1.5]],
  },
  // Ein Loch in einer Scheibe: gestrichelt, mit seinen Ecken.
  'cad-loch': {
    pfade: ['M3.5 20V4h17v16z'],
    strich: ['M8.5 8.5h7v7h-7z'],
    voll: [[8.5, 8.5, 1.3], [15.5, 8.5, 1.3], [15.5, 15.5, 1.3], [8.5, 15.5, 1.3]],
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
  // Wie ein Lager eine Scheibe hält, im Punkt oben: fest in x und y ein
  // Dreieck auf schraffiertem Grund, nur in y auf Rollen, nur in x dasselbe
  // gedreht, links vom Punkt -- wie im Bild (fw_bild.js).
  'halt-xy': {
    pfade: ['M12 5l-5 9h10z', 'M4.5 14h15', 'M7 14l-2.5 4 M11 14l-2.5 4 M15 14l-2.5 4 M19 14l-2.5 4'],
    voll: [[12, 5, 1.6]],
  },
  'halt-y': {
    pfade: ['M12 4l-5 9h10z', 'M4.5 17.3h15', 'M7 17.3l-2.5 3.5 M11 17.3l-2.5 3.5 M15 17.3l-2.5 3.5 M19 17.3l-2.5 3.5'],
    kreise: [[9.5, 15.1, 2], [14.5, 15.1, 2]],
    voll: [[12, 4, 1.6]],
  },
  'halt-x': {
    pfade: ['M20 12l-9-5v10z', 'M6.7 4.5v15', 'M6.7 7l-3.5-2.5 M6.7 11l-3.5-2.5 M6.7 15l-3.5-2.5 M6.7 19l-3.5-2.5'],
    kreise: [[8.9, 9.5, 2], [8.9, 14.5, 2]],
    voll: [[20, 12, 1.6]],
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
  // Wie ein Spannglied zählt, als Spannung über der Dehnung des Betons an
  // seiner Stelle: mit Vordehnung trägt es schon bei null, der volle Punkt;
  // schlaff beginnt es bei null und bleibt um σ_p∞ tiefer -- gestrichelt,
  // was es mit Vordehnung trüge.
  'wirkung-vordehnung': {
    pfade: [ACHSEN, 'M4 11.5L8.5 6H20'],
    voll: [[4, 11.5, 1.8]],
  },
  'wirkung-restfestigkeit': {
    pfade: [ACHSEN, 'M4 20L8.5 14.5H20'],
    strich: ['M8.5 6H20'],
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
  // Die Knickspannungskurve: aus dem Profil das I, dessen Form nach Figur 7
  // die Kurve bestimmt; sonst χ über λ̄ nach (8), mit dem α_K der Kurve
  // gerechnet, unter der Grenze ohne Imperfektion (gestrichelt). Je
  // grösser α_K, desto tiefer die Kurve.
  'knickkurve-profil': {
    pfade: ['M5 4h14v3h-5.5v10H19v3H5v-3h5.5V7H5z'],
  },
  'knickkurve-a': {
    pfade: [ACHSEN, 'M4 5L5.3 5L6.6 5.7L7.8 6.7L9.1 8.1L10.4 10L11.7 12.1L13 13.7L14.2 15L15.5 15.9'
      + 'L16.8 16.7L18.1 17.2L19.4 17.6'],
    strich: [EULER],
  },
  'knickkurve-b': {
    pfade: [ACHSEN, 'M4 5L5.3 5L6.6 6.1L7.8 7.4L9.1 9.1L10.4 11L11.7 12.8L13 14.3L14.2 15.4L15.5 16.2'
      + 'L16.8 16.9L18.1 17.4L19.4 17.7'],
    strich: [EULER],
  },
  'knickkurve-c': {
    pfade: [ACHSEN, 'M4 5L5.3 5L6.6 6.5L7.8 8.2L9.1 10.1L10.4 11.9L11.7 13.5L13 14.8L14.2 15.7'
      + 'L15.5 16.5L16.8 17.1L18.1 17.5L19.4 17.9'],
    strich: [EULER],
  },
  'knickkurve-d': {
    pfade: [ACHSEN, 'M4 5L5.3 5L6.6 7.2L7.8 9.3L9.1 11.3L10.4 13L11.7 14.4L13 15.4L14.2 16.2'
      + 'L15.5 16.9L16.8 17.4L18.1 17.7L19.4 18'],
    strich: [EULER],
  },
  // Die Feuchteklasse des Holzes: auf der Kachel ein Tropfen. Je Klasse, wo
  // der Balken (voll) steht: im Haus; unter einem offenen Dach, der Regen
  // von der Seite; halb im Wasser.
  feuchteklasse: {
    pfade: ['M12 3.5C10 7 6.5 10.5 6.5 14.5a5.5 5.5 0 0 0 11 0C17.5 10.5 14 7 12 3.5z'],
  },
  'feuchteklasse-1': {
    pfade: ['M3 11L12 4l9 7', 'M5 9.5V20h14V9.5'],
    flaechen: ['M8.5 14h7v4h-7z'],
  },
  'feuchteklasse-2': {
    pfade: ['M2.5 9.5L11 4l8.5 5.5', 'M19.5 11.5l-2 3.5 M22.5 12.5l-2 3.5 M21 17.5l-2 3.5'],
    flaechen: ['M4.5 12.5h9v4h-9z'],
  },
  'feuchteklasse-3': {
    pfade: ['M3 13q2.25-1.8 4.5 0t4.5 0t4.5 0t4.5 0', 'M3 18q2.25-1.8 4.5 0t4.5 0t4.5 0t4.5 0'],
    flaechen: ['M7 7h10v7H7z'],
  },
  // Die Verdübelung im Verbund: auf der Kachel Platte und Träger in der
  // Ansicht, dazwischen die Kopfbolzendübel. Je Stellung der Querschnitt mit
  // seiner Dehnung daneben: voll verdübelt eine Gerade über Beton und Stahl;
  // mit Dübeln springt sie an der Fuge (gestrichelt, der Schlupf), und Beton
  // und Stahl haben je ihre Nulllinie.
  verduebelung: {
    pfade: ['M2 3.5h20v7H2z', 'M6 10.5V6.5 M4.8 6.5h2.4', 'M12 10.5V6.5 M10.8 6.5h2.4',
      'M18 10.5V6.5 M16.8 6.5h2.4', 'M2 13v5.5 M22 13v5.5'],
    flaechen: ['M2 10.5h20V13H2z', 'M2 18.5h20V21H2z'],
  },
  'verduebelung-voll': {
    pfade: ['M2 3.5h9v5H2z', 'M3.5 9.3h6 M6.5 9.3v10.4 M3.5 19.7h6', 'M16.5 3.5v16.2',
      'M19.5 3.5L13.5 19.7'],
  },
  'verduebelung-kopfbolzen': {
    pfade: ['M2 3.5h9v5H2z', 'M3.5 9.3h6 M6.5 9.3v10.4 M3.5 19.7h6', 'M6.5 8.5V5.8 M5.3 5.8h2.4',
      'M16.5 3.5v16.2', 'M19.5 3.5L15 8.9', 'M19 8.9L13.5 19.7'],
    strich: ['M15 8.9h4'],
  },
  // Aus dem Balkensystem: ein Träger auf zwei Lagern, darauf eine Stelle
  // -- ein Pfeil führt von ihr zum Querschnitt darunter.
  aus_system: {
    pfade: ['M3 6h18', 'M5 6l-2 3h4z M19 6l-2 3h4z', 'M12 8.5v5 M10.2 11.7l1.8 1.8 1.8-1.8',
      'M9 16h6v6H9z'],
    kreise: [[12, 6, 1.4]],
  },
  // Der Schubfluss: ein Plattenbalken im Schnitt, gestrichelt die Schnitte
  // am Steg, aus ihnen die Pfeile in die Flanschen, die sie abtrennen.
  schubfluss: {
    pfade: ['M2.5 4h19v5h-6.5v11h-5V9H2.5z', 'M8.5 6.5H4.6 M5.9 5.2L4.6 6.5l1.3 1.3',
      'M15.5 6.5h3.9 M18.1 5.2l1.3 1.3-1.3 1.3'],
    strich: ['M10 4v5 M14 4v5'],
  },
  // Der Längsschub der Blechverbunddecke: die Decke in der Ansicht, unten
  // voll ihr Blech -- darüber und darunter je ein Pfeil, wie Beton und Blech
  // gegeneinander gleiten wollen.
  laengsschub: {
    pfade: ['M3 7h18v8H3z', 'M6 4h10 M14 2.5l2 1.5-2 1.5', 'M18 19.5H8 M10 18l-2 1.5 2 1.5'],
    flaechen: ['M3 15h18v1.6H3z'],
  },
  // Wo das Feld der Decke liegt: ein Einfeld auf zwei Lagern; das End- und
  // ein Innenfeld einer durchlaufenden Decke, gestrichelt ihre Nachbarfelder.
  'blechfeld-einfeld': {
    pfade: ['M4 11h16', 'M4 11l-1.6 2.8h3.2z', 'M20 11l-1.6 2.8h3.2z'],
  },
  'blechfeld-endfeld': {
    pfade: ['M3 11h10', 'M3 11l-1.6 2.8h3.2z', 'M13 11l-1.6 2.8h3.2z', 'M21 11l-1.6 2.8h3.2z'],
    strich: ['M13 11h8'],
  },
  'blechfeld-innenfeld': {
    pfade: ['M8 11h8', 'M2.5 11l-1.6 2.8h3.2z', 'M8 11l-1.6 2.8h3.2z', 'M16 11l-1.6 2.8h3.2z',
      'M21.5 11l-1.6 2.8h3.2z'],
    strich: ['M2.5 11H8 M16 11h5.5'],
  },
  // Wie die Last auf dem Feld steht: gleichmässig verteilt, oder zwei
  // Einzellasten, je im Abstand a von ihrem Lager -- unten sein Mass.
  'blechlast-gleichmaessig': {
    pfade: ['M4 14h16', 'M4 14l-1.6 2.8h3.2z', 'M20 14l-1.6 2.8h3.2z', 'M4 5.5h16',
      'M6 5.5v6 M10 5.5v6 M14 5.5v6 M18 5.5v6',
      'M5 10.3l1 1.2 1-1.2 M9 10.3l1 1.2 1-1.2 M13 10.3l1 1.2 1-1.2 M17 10.3l1 1.2 1-1.2'],
  },
  'blechlast-einzellasten': {
    pfade: ['M4 14h16', 'M4 14l-1.6 2.8h3.2z', 'M20 14l-1.6 2.8h3.2z',
      'M9 4v8 M7.6 10.6L9 12l1.4-1.4', 'M15 4v8 M13.6 10.6L15 12l1.4-1.4',
      'M4 20h5 M4 18.8v2.4 M9 18.8v2.4'],
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
