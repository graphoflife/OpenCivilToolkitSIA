/**
 * sinnbilder.js -- die Zeichen auf den Knöpfen: die Kapitel eines Bauteils
 * und die Apps links.
 *
 * Einfache Linienbilder, 24 × 24, in der Farbe der Schrift: was das Kapitel
 * zeigt oder prüft, auf einen Blick -- die Interaktionslinie, der geknickte
 * Stab, die Druckzone, der Riss; bei den Apps, was sie bearbeiten. Selbst
 * gezeichnet; keine fremde Bibliothek und keine Bilddatei.
 *
 * Jedes Zeichen ist eine Liste von Pfaden (`d`) und Kreisen (`[cx, cy, r]`).
 * Gestrichelt wird, was eine Grenze meint.
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
  // Eine Konsole: die Aufforderung und eine Zeile dahinter.
  python: {
    pfade: ['M3 4.5h18v15H3z', 'M6.5 9l3 3-3 3', 'M11.5 15.5h5'],
  },
};

/** Ein Zeichen als SVG -- `name` aus der Liste oben. */
export function sinnbild(name) {
  const z = ZEICHEN[name];
  const svg = svgEl('svg', {
    viewBox: '0 0 24 24', class: 'sinnbild', 'aria-hidden': 'true',
    fill: 'none', stroke: 'currentColor', 'stroke-width': 1.6,
    'stroke-linecap': 'round', 'stroke-linejoin': 'round',
  });
  for (const d of z?.pfade || []) svg.append(svgEl('path', { d }));
  for (const d of z?.strich || []) svg.append(svgEl('path', { d, 'stroke-dasharray': '2 2' }));
  for (const [cx, cy, r] of z?.kreise || []) svg.append(svgEl('circle', { cx, cy, r }));
  return svg;
}
