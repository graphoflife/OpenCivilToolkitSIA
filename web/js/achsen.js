/**
 * achsen.js -- ein Achsenkreuz für alle Diagramme.
 *
 * Massstab, Gitter mit Teilung, Nulllinien, Rahmen und Achsentitel: was jedes
 * Diagramm braucht und vorher jedes selbst baute, sechsmal fast gleich und mit
 * kleinen Abweichungen, die niemand gewollt hatte. Die Diagramme zeichnen nur
 * noch ihre Daten hinein.
 *
 * Die Reihenfolge im Bild ist fest: Gitter und Nulllinien zuunterst, darüber
 * die Daten (`daten`), zuoberst die Achsentitel.
 */

import { svgEl } from './dom.js';

export const NR = 'http://www.w3.org/2000/svg';

const GITTER = '#e6e9ee';
const NULLLINIE = '#b8c0cc';
const TEILUNG = '#5c6773';
const TITEL = '#1a1f27';
const RAHMEN = '#8895a8';

/** Sucht einen runden Schrittabstand für die Achsenteilung. */
export function schrittweite(spanne, zielAnzahl = 8) {
  const roh = spanne / zielAnzahl;
  const groesse = 10 ** Math.floor(Math.log10(Math.abs(roh) || 1));
  const rest = roh / groesse;
  const gewaehlt = rest >= 5 ? 10 : rest >= 2 ? 5 : rest >= 1 ? 2 : 1;
  return gewaehlt * groesse;
}

/** Die Striche einer Teilung: runde Vielfache im Bereich, aufsteigend. */
function striche([a, b], { ziel = 8, schritt } = {}) {
  const von = Math.min(a, b);
  const bis = Math.max(a, b);
  const s = schritt ?? schrittweite(bis - von, ziel);
  const heraus = [];
  for (let v = Math.ceil(von / s) * s; v <= bis; v += s) heraus.push(v);
  return heraus;
}

function text(inhalt, attribute) {
  const knoten = svgEl('text', attribute);
  knoten.textContent = inhalt;
  return knoten;
}

/**
 * Ein leeres Diagramm.
 *
 * @param {object} o
 * @param {number} o.breite   Breite des Bildes (viewBox)
 * @param {number} o.hoehe    Höhe des Bildes
 * @param {{oben: number, rechts: number, unten: number, links: number}} o.rand
 *   Platz um das Feld, für Teilung und Titel
 * @param {object} o.x   die waagrechte Achse, `o.y` die senkrechte, je mit
 *   - `bereich: [a, b]` -- a liegt links bzw. unten. Umgekehrt angegeben läuft
 *     die Achse andersherum, etwa die Höhe eines Schnitts nach unten.
 *   - `teilung` -- Gitter mit beschrifteten Strichen: `{ziel, schritt,
 *     format}`. `schritt` fest, sonst ein runder aus `ziel` Strichen. Ohne
 *     `teilung` kein Gitter.
 *   - `null` -- die Nulllinie betonen, sofern sie im Bereich liegt
 *   - `titel` -- der Achsentitel
 * @param {object} [o.attribute]  Attribute des svg-Elements
 * @param {boolean} [o.rahmen]    das Feld umrahmen
 * @param {{teilung: number, titel: number}} [o.schrift]  Schriftgrössen
 * @param {number} [o.titelLinks]  Abstand des senkrechten Titels vom Rand
 * @returns {{svg, daten, x: Function, y: Function, feld: object}}
 *   `daten` ist die Gruppe, in die das Diagramm zeichnet.
 */
export function achsenkreuz({
  breite, hoehe, rand, x: xAchse, y: yAchse, attribute = {},
  rahmen = false, schrift = { teilung: 11, titel: 12 }, titelLinks = 16,
}) {
  const feld = {
    links: rand.links, rechts: breite - rand.rechts,
    oben: rand.oben, unten: hoehe - rand.unten,
  };
  const feldBreite = feld.rechts - feld.links;
  const feldHoehe = feld.unten - feld.oben;
  const [x0, x1] = xAchse.bereich;
  const [y0, y1] = yAchse.bereich;
  // Ein Bereich ohne Ausdehnung zeichnete sonst alles ins Unendliche.
  const x = (v) => feld.links + ((v - x0) / ((x1 - x0) || 1)) * feldBreite;
  const y = (v) => feld.oben + (1 - (v - y0) / ((y1 - y0) || 1)) * feldHoehe;

  const svg = svgEl('svg', { ...attribute, viewBox: `0 0 ${breite} ${hoehe}` });

  if (rahmen) {
    svg.append(svgEl('rect', {
      x: feld.links, y: feld.oben, width: feldBreite, height: feldHoehe,
      fill: 'none', stroke: RAHMEN, 'stroke-width': 1,
    }));
  }

  if (xAchse.teilung || yAchse.teilung) {
    const gitter = svgEl('g');
    const format = (teilung) => teilung.format || ((v) => Math.round(v));
    if (xAchse.teilung) {
      for (const v of striche(xAchse.bereich, xAchse.teilung)) {
        gitter.append(svgEl('line', {
          x1: x(v), y1: feld.oben, x2: x(v), y2: feld.unten,
          stroke: GITTER, 'stroke-width': 1,
        }));
        gitter.append(text(format(xAchse.teilung)(v), {
          x: x(v), y: feld.unten + schrift.teilung + 5, 'text-anchor': 'middle',
          'font-size': schrift.teilung, fill: TEILUNG,
        }));
      }
    }
    if (yAchse.teilung) {
      for (const v of striche(yAchse.bereich, yAchse.teilung)) {
        gitter.append(svgEl('line', {
          x1: feld.links, y1: y(v), x2: feld.rechts, y2: y(v),
          stroke: GITTER, 'stroke-width': 1,
        }));
        gitter.append(text(format(yAchse.teilung)(v), {
          x: feld.links - 8, y: y(v) + 4, 'text-anchor': 'end',
          'font-size': schrift.teilung, fill: TEILUNG,
        }));
      }
    }
    svg.append(gitter);
  }

  // Nulllinien kräftiger, damit Zug und Druck auf einen Blick trennbar sind.
  const umfasstNull = ([a, b]) => Math.min(a, b) < 0 && Math.max(a, b) > 0;
  if (yAchse.null && umfasstNull(yAchse.bereich)) {
    svg.append(svgEl('line', {
      x1: feld.links, y1: y(0), x2: feld.rechts, y2: y(0),
      stroke: NULLLINIE, 'stroke-width': 1.5,
    }));
  }
  if (xAchse.null && umfasstNull(xAchse.bereich)) {
    svg.append(svgEl('line', {
      x1: x(0), y1: feld.oben, x2: x(0), y2: feld.unten,
      stroke: NULLLINIE, 'stroke-width': 1.5,
    }));
  }

  const daten = svgEl('g');
  svg.append(daten);

  const titel = { 'text-anchor': 'middle', 'font-size': schrift.titel, fill: TITEL, 'font-weight': 600 };
  if (xAchse.titel) {
    svg.append(text(xAchse.titel, { ...titel, x: feld.links + feldBreite / 2, y: hoehe - 8 }));
  }
  if (yAchse.titel) {
    const mitte = feld.oben + feldHoehe / 2;
    svg.append(text(yAchse.titel, {
      ...titel, x: titelLinks, y: mitte, transform: `rotate(-90 ${titelLinks} ${mitte})`,
    }));
  }

  return { svg, daten, x, y, feld };
}
