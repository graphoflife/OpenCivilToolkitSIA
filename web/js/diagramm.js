/**
 * diagramm.js -- M-N-Interaktionsdiagramm als SVG.
 *
 * Zeichnet die vom Rechenkern gelieferte Resistenzlinie und trägt die
 * Bemessungspunkte ein. Zu jedem Punkt wird die Strecke zum massgebenden
 * Punkt der Linie gezeigt -- also genau der Weg, in dem der Erfüllungsgrad
 * gemessen wurde. Bei "Normalkraft konstant" ist das eine Waagrechte, bei
 * "Moment konstant" eine Senkrechte, beim kürzesten Abstand die Schräge.
 *
 * Es wird nichts nachgerechnet: sämtliche Koordinaten kommen aus der Lösung.
 */

import { el } from './dom.js';

const NR = 'http://www.w3.org/2000/svg';
const BREITE = 720;
const HOEHE = 520;
const RAND = { oben: 22, rechts: 22, unten: 46, links: 74 };

function svgEl(name, attribute = {}) {
  const knoten = document.createElementNS(NR, name);
  for (const [k, v] of Object.entries(attribute)) {
    if (v !== null && v !== undefined) knoten.setAttribute(k, String(v));
  }
  return knoten;
}

/** Sucht einen runden Schrittabstand für die Achsenteilung. */
function schrittweite(spanne, zielAnzahl = 8) {
  const roh = spanne / zielAnzahl;
  const groesse = 10 ** Math.floor(Math.log10(Math.abs(roh) || 1));
  const rest = roh / groesse;
  const gewaehlt = rest >= 5 ? 10 : rest >= 2 ? 5 : rest >= 1 ? 2 : 1;
  return gewaehlt * groesse;
}

/**
 * Zeichnet den Plattenquerschnitt mit seinen vier Bewehrungslagen.
 *
 * Gezeigt wird ein Schnitt senkrecht zur x-Achse: Stäbe in x-Richtung sind
 * angeschnitten (Kreise), Stäbe in y-Richtung laufen in der Schnittebene
 * (Balken). Sämtliche Höhenlagen stammen aus der Lösung -- hier wird nichts
 * nachgerechnet.
 */
export function querschnittZeichnen(eintrag, werte) {
  const zahl = (id) => (werte[id] ? werte[id].zahl : null);
  const h = zahl(eintrag.werte.h);
  const b = zahl(eintrag.werte.b);
  if (!h || !b) return el('div.leer', { text: 'Geometrie noch nicht gerechnet.' });

  const BREITE = 640;
  const RAND = { oben: 26, unten: 40, links: 62, rechts: 130 };
  const zeichenBreite = BREITE - RAND.links - RAND.rechts;
  // Massstab so, dass die Platte gut sichtbar bleibt, ohne die Höhe zu verzerren.
  const massstab = zeichenBreite / b;
  const zeichenHoehe = h * massstab;
  const HOEHE = zeichenHoehe + RAND.oben + RAND.unten;

  const x = (mm) => RAND.links + mm * massstab;
  const y = (mm) => RAND.oben + mm * massstab;

  const svg = svgEl('svg', {
    class: 'qs', viewBox: `0 0 ${BREITE} ${HOEHE}`, xmlns: NR,
    role: 'img', 'aria-label': 'Plattenquerschnitt',
  });

  svg.append(svgEl('rect', {
    x: x(0), y: y(0), width: b * massstab, height: zeichenHoehe,
    fill: '#eceff4', stroke: '#7b8794', 'stroke-width': 1.6,
  }));

  const farbe = { x: '#1f6feb', y: '#b8622a' };
  for (const bew of eintrag.bewehrung) {
    const z = zahl(bew.z_id);
    const phi = zahl(eintrag.werte[`lage.${bew.lage}${bew.art === 'grund' ? 'g' : 'z'}.phi`]);
    if (z === null) continue;
    const r = Math.max((phi || 12) * massstab / 2, 2.2);
    const anzahl = 9;
    for (let i = 0; i < anzahl; i++) {
      const px = x(b * (i + 0.5) / anzahl);
      if (bew.richtung === 'x') {
        svg.append(svgEl('circle', {
          cx: px, cy: y(z), r,
          fill: farbe.x, opacity: bew.art === 'zulage' ? 0.55 : 1,
        }));
      } else {
        svg.append(svgEl('rect', {
          x: px - r * 1.6, y: y(z) - r, width: r * 3.2, height: r * 2, rx: r,
          fill: farbe.y, opacity: bew.art === 'zulage' ? 0.55 : 1,
        }));
      }
    }
    const beschriftung = svgEl('text', {
      x: BREITE - RAND.rechts + 10, y: y(z) + 4,
      'font-size': 10.5, fill: farbe[bew.richtung],
    });
    beschriftung.textContent =
      `${bew.lage}. ${bew.art === 'grund' ? 'Grund' : 'Zulage'} ${bew.menge} (${bew.richtung})`;
    svg.append(beschriftung);
  }

  // Höhenmass links
  svg.append(svgEl('line', {
    x1: RAND.links - 16, y1: y(0), x2: RAND.links - 16, y2: y(h),
    stroke: '#56657a', 'stroke-width': 1,
  }));
  for (const [wert, text] of [[0, 'OK'], [h, 'UK']]) {
    svg.append(svgEl('line', {
      x1: RAND.links - 21, y1: y(wert), x2: RAND.links - 11, y2: y(wert),
      stroke: '#56657a', 'stroke-width': 1,
    }));
    const m = svgEl('text', {
      x: RAND.links - 25, y: y(wert) + 4, 'text-anchor': 'end',
      'font-size': 10.5, fill: '#56657a',
    });
    m.textContent = text;
    svg.append(m);
  }
  const masstext = svgEl('text', {
    x: 14, y: RAND.oben + zeichenHoehe / 2, 'font-size': 11, fill: '#16202c',
    'font-weight': 600, 'text-anchor': 'middle',
    transform: `rotate(-90 14 ${RAND.oben + zeichenHoehe / 2})`,
  });
  masstext.textContent = `h = ${h.toFixed(0)} mm`;
  svg.append(masstext);

  const breitentext = svgEl('text', {
    x: RAND.links + (b * massstab) / 2, y: HOEHE - 12,
    'text-anchor': 'middle', 'font-size': 11, fill: '#16202c', 'font-weight': 600,
  });
  breitentext.textContent = `b = ${b.toFixed(0)} mm`;
  svg.append(breitentext);

  return el('div.diagramm-huelle', {}, [
    svg,
    el('div.mn-legende', {}, [
      el('span', {}, [el('i', { style: { background: farbe.x } }), 'x-Richtung (angeschnitten)']),
      el('span', {}, [el('i', { style: { background: farbe.y, borderRadius: '2px' } }), 'y-Richtung (in der Schnittebene)']),
      el('span', { text: 'blasser = Zulage' }),
    ]),
  ]);
}

export function diagrammZeichnen(linie) {
  const punkte = linie.punkte;
  if (!punkte?.length) return el('div.leer', { text: 'Keine Resistenzlinie vorhanden.' });

  const alleM = punkte.map((p) => p.M);
  const alleN = punkte.map((p) => p.N);
  for (const k of linie.kombinationen) { alleM.push(k.M_Ed); alleN.push(k.N_Ed); }

  const spielraum = 0.08;
  const mSpanne = (Math.max(...alleM) - Math.min(...alleM)) || 1;
  const nSpanne = (Math.max(...alleN) - Math.min(...alleN)) || 1;
  const mMin = Math.min(...alleM) - mSpanne * spielraum;
  const mMax = Math.max(...alleM) + mSpanne * spielraum;
  const nMin = Math.min(...alleN) - nSpanne * spielraum;
  const nMax = Math.max(...alleN) + nSpanne * spielraum;

  const zeichenBreite = BREITE - RAND.links - RAND.rechts;
  const zeichenHoehe = HOEHE - RAND.oben - RAND.unten;
  const x = (m) => RAND.links + ((m - mMin) / (mMax - mMin)) * zeichenBreite;
  const y = (n) => RAND.oben + (1 - (n - nMin) / (nMax - nMin)) * zeichenHoehe;

  const svg = svgEl('svg', {
    class: 'mn', viewBox: `0 0 ${BREITE} ${HOEHE}`,
    xmlns: NR, role: 'img',
    'aria-label': 'M-N-Interaktionsdiagramm',
  });

  // -- Gitter und Achsen --------------------------------------------------
  const gitter = svgEl('g');
  const mSchritt = schrittweite(mMax - mMin);
  const nSchritt = schrittweite(nMax - nMin);

  for (let m = Math.ceil(mMin / mSchritt) * mSchritt; m <= mMax; m += mSchritt) {
    gitter.append(svgEl('line', {
      x1: x(m), y1: RAND.oben, x2: x(m), y2: HOEHE - RAND.unten,
      stroke: '#e6e9ee', 'stroke-width': 1,
    }));
    const beschriftung = svgEl('text', {
      x: x(m), y: HOEHE - RAND.unten + 16, 'text-anchor': 'middle',
      'font-size': 11, fill: '#5c6773',
    });
    beschriftung.textContent = Math.round(m);
    gitter.append(beschriftung);
  }
  for (let n = Math.ceil(nMin / nSchritt) * nSchritt; n <= nMax; n += nSchritt) {
    gitter.append(svgEl('line', {
      x1: RAND.links, y1: y(n), x2: BREITE - RAND.rechts, y2: y(n),
      stroke: '#e6e9ee', 'stroke-width': 1,
    }));
    const beschriftung = svgEl('text', {
      x: RAND.links - 8, y: y(n) + 4, 'text-anchor': 'end',
      'font-size': 11, fill: '#5c6773',
    });
    beschriftung.textContent = Math.round(n);
    gitter.append(beschriftung);
  }
  svg.append(gitter);

  // Nulllinien kräftiger, damit Zug und Druck auf einen Blick trennbar sind.
  if (nMin < 0 && nMax > 0) {
    svg.append(svgEl('line', {
      x1: RAND.links, y1: y(0), x2: BREITE - RAND.rechts, y2: y(0),
      stroke: '#b8c0cc', 'stroke-width': 1.5,
    }));
  }
  if (mMin < 0 && mMax > 0) {
    svg.append(svgEl('line', {
      x1: x(0), y1: RAND.oben, x2: x(0), y2: HOEHE - RAND.unten,
      stroke: '#b8c0cc', 'stroke-width': 1.5,
    }));
  }

  // -- Resistenzlinie ------------------------------------------------------
  svg.append(svgEl('polygon', {
    points: punkte.map((p) => `${x(p.M).toFixed(2)},${y(p.N).toFixed(2)}`).join(' '),
    fill: 'rgba(31,95,168,.07)', stroke: '#1f5fa8', 'stroke-width': 2,
    'stroke-linejoin': 'round',
  }));

  // -- Bemessungspunkte ----------------------------------------------------
  for (const k of linie.kombinationen) {
    const farbe = k.innerhalb ? '#1a7f45' : '#b3261e';

    if (k.widerstand) {
      svg.append(svgEl('line', {
        x1: x(k.M_Ed), y1: y(k.N_Ed), x2: x(k.widerstand.M), y2: y(k.widerstand.N),
        stroke: farbe, 'stroke-width': 1.4, 'stroke-dasharray': '5 3', opacity: .75,
      }));
      svg.append(svgEl('circle', {
        cx: x(k.widerstand.M), cy: y(k.widerstand.N), r: 3.5,
        fill: '#fff', stroke: farbe, 'stroke-width': 1.6,
      }));
    }

    const punkt = svgEl('circle', {
      cx: x(k.M_Ed), cy: y(k.N_Ed), r: 6,
      fill: farbe, stroke: '#fff', 'stroke-width': 2,
    });
    const titel = svgEl('title');
    titel.textContent =
      `${k.name}\nM_Ed = ${k.M_Ed.toFixed(1)} kNm, N_Ed = ${k.N_Ed.toFixed(1)} kN`
      + `\nAusnutzung ${Number.isFinite(k.ausnutzung) ? k.ausnutzung.toFixed(3) : '∞'}`
      + ` (${k.art_text})\n${k.innerhalb ? 'erfüllt' : 'NICHT erfüllt'}`;
    punkt.append(titel);
    svg.append(punkt);

    const beschriftung = svgEl('text', {
      x: x(k.M_Ed) + 9, y: y(k.N_Ed) - 8,
      'font-size': 11, 'font-weight': 600, fill: farbe,
    });
    beschriftung.textContent = k.name;
    svg.append(beschriftung);
  }

  // -- Achsenbeschriftung --------------------------------------------------
  const xTitel = svgEl('text', {
    x: RAND.links + zeichenBreite / 2, y: HOEHE - 8,
    'text-anchor': 'middle', 'font-size': 12, fill: '#1a1f27', 'font-weight': 600,
  });
  xTitel.textContent = 'M [kNm]';
  svg.append(xTitel);

  const yTitel = svgEl('text', {
    x: 16, y: RAND.oben + zeichenHoehe / 2,
    'text-anchor': 'middle', 'font-size': 12, fill: '#1a1f27', 'font-weight': 600,
    transform: `rotate(-90 16 ${RAND.oben + zeichenHoehe / 2})`,
  });
  yTitel.textContent = 'N [kN]   (Zug positiv)';
  svg.append(yTitel);

  return el('div.diagramm-huelle', {}, [
    svg,
    el('div.mn-legende', {}, [
      el('span', {}, [el('i', { style: { background: '#1f5fa8' } }), 'Resistenzlinie']),
      el('span', {}, [el('i', { style: { background: '#1a7f45' } }), 'erfüllt']),
      el('span', {}, [el('i', { style: { background: '#b3261e' } }), 'nicht erfüllt']),
      el('span', { text: '– – –  gemessener Weg zur Linie' }),
    ]),
  ]);
}
