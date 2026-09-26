/**
 * lagen.js -- die vier Lagen und ihre Paare.
 *
 * Gespeichert ist die Richtung der äusseren Lagen (1 und 4); die innere Lage
 * jeder Seite hat die Gegenrichtung. Diese Regel steht im Kern einmal
 * (`QuerschnittEintrag.richtung_von`) und hier einmal -- die Maske braucht
 * sie schon beim Tippen, bevor der Kern gerechnet hat. Vorher stand sie hier
 * dreimal: als Richtung, als Partnertafel und als Umrechnung beim Schalten.
 */

const GEGEN = { x: 'y', y: 'x' };
const aussen = (nummer) => nummer === 1 || nummer === 4;
const feldVon = (nummer) => (nummer <= 2 ? 'richtung_lage1' : 'richtung_lage4');

/** Die Lage derselben Seite: 1 ↔ 2, 3 ↔ 4. */
export function partnerVon(nummer) {
  return { 1: 2, 2: 1, 3: 4, 4: 3 }[nummer];
}

/** Tragrichtung der Lage 1..4, 'x' oder 'y'. */
export function richtungVon(querschnitt, nummer) {
  const gespeichert = querschnitt[feldVon(nummer)];
  return aussen(nummer) ? gespeichert : GEGEN[gespeichert];
}

/** Die Lage auf eine Richtung stellen -- ihr Partner bekommt die Gegenrichtung. */
export function richtungSetzen(querschnitt, nummer, richtung) {
  querschnitt[feldVon(nummer)] = aussen(nummer) ? richtung : GEGEN[richtung];
}

/** Welche der vier Lagen in x tragen -- in aller Regel die 2. und die 3. */
export function xLagen(querschnitt) {
  return [1, 2, 3, 4].filter((n) => richtungVon(querschnitt, n) === 'x');
}
