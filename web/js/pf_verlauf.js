/**
 * pf_verlauf.js -- die Verläufe eines Pfahls über die Tiefe.
 *
 * Je Kombination eine Karte: nebeneinander die Normalkraft N und die
 * Setzung w, und wo eine Last quer wirkt, die Verschiebung y, die
 * Verdrehung θ, das Moment M, die Querkraft V und der Bettungsdruck p --
 * je über der Tiefe ab Terrain, die Tiefe nach unten wie im Bild der
 * Situation. Angeschrieben ist der Wert mit dem grössten Betrag, mit
 * Punkt; was überall null ist, fehlt.
 *
 * Gerechnet wird nichts: die Werte kommen fertig aus dem Kern
 * (opencivil/web/pfahldaten.py), mit dem Bemessungswert des
 * Verformungsmoduls, wie die Legende sagt.
 */

import { achsenkreuz } from './achsen.js';
import { karte } from './bausteine.js';
import { el, svgEl } from './dom.js';
import { legende, zahl } from './gb_skizze.js';

/** Die Verläufe: Feld der Daten, Achsentitel, Stellen der Beschriftung, Farbe. */
const GROESSEN = [
  { feld: 'N', titel: 'N [kN]', stellen: 0, klasse: 'bs-d-n' },
  { feld: 'w', titel: 'w [mm]', stellen: 2, klasse: 'pf-d-w' },
  { feld: 'y', titel: 'y [mm]', stellen: 2, klasse: 'pf-d-w' },
  { feld: 'theta', titel: 'θ [mrad]', stellen: 2, klasse: 'bs-d-phi' },
  { feld: 'M', titel: 'M [kNm]', stellen: 1, klasse: 'bs-d-m' },
  { feld: 'V', titel: 'V [kN]', stellen: 1, klasse: 'bs-d-v' },
  { feld: 'p', titel: 'p [kN/m²]', stellen: 0, klasse: 'pf-d-p' },
];

const BREITE = 168;
const HOEHE = 380;
const RAND = { oben: 12, rechts: 14, unten: 34, links: 40 };

/** Der Index des Werts mit dem grössten Betrag. */
function groesster(werte) {
  return werte.reduce((best, v, i) => (Math.abs(v) > Math.abs(werte[best]) ? i : best), 0);
}

/** Ein Verlauf über die Tiefe: die Fläche zwischen null und der Kurve, der grösste Wert. */
function verlaufsbild(z, werte, { titel, stellen, klasse }) {
  const i = groesster(werte);
  const spitze = Math.abs(werte[i]);
  const [von, bis] = [Math.min(0, ...werte), Math.max(0, ...werte)];
  const luft = 0.08 * (bis - von || 1);
  const bild = achsenkreuz({
    breite: BREITE, hoehe: HOEHE, rand: RAND,
    attribute: { class: 'pf-verlauf', role: 'img', 'aria-label': titel },
    x: { bereich: [von - (von < 0 ? luft : 0), bis + (bis > 0 ? luft : 0)],
      teilung: { ziel: 3 }, null: true, titel },
    y: { bereich: [z[z.length - 1], z[0]], teilung: { ziel: 8 } },
  });
  const punkte = z.map((zi, k) => [bild.x(werte[k]), bild.y(zi)]);
  const pfad = (p) => p.map(([x, y], k) => `${k ? 'L' : 'M'}${x.toFixed(1)} ${y.toFixed(1)}`).join(' ');
  const null0 = bild.x(0);
  bild.daten.append(
    svgEl('path', {
      d: `${pfad([[null0, punkte[0][1]], ...punkte, [null0, punkte[punkte.length - 1][1]]])} Z`,
      class: `bs-d-flaeche ${klasse}`,
    }),
    svgEl('path', { d: pfad(punkte), class: `bs-d-kurve ${klasse}` }),
  );
  if (spitze > 0) {
    const [x, y] = punkte[i];
    const rechts = x < (bild.feld.links + bild.feld.rechts) / 2;
    const schrift = svgEl('text', {
      x: (x + (rechts ? 6 : -6)).toFixed(1), y: Math.max(y - 6, bild.feld.oben + 10).toFixed(1),
      'text-anchor': rechts ? 'start' : 'end', class: 'bs-d-text',
    });
    schrift.textContent = zahl(werte[i], stellen);
    bild.daten.append(
      svgEl('circle', { cx: x.toFixed(1), cy: y.toFixed(1), r: 3.2, class: `bs-d-extrem ${klasse}` }),
      schrift,
    );
  }
  return bild.svg;
}

/**
 * Die Karten der Verläufe, je Kombination eine -- `d` ist, was der Kern
 * zum Pfahl zeichnet. Ohne Steifigkeit keine.
 */
export function verlaufKarten(d) {
  return (d?.verlaeufe || []).map((v) => karte(`Verläufe – ${v.name}`, [
    el('div.pf-verlaeufe', {}, GROESSEN
      .filter((g) => v[g.feld] && v[g.feld].some((x) => Math.abs(x) > 1e-9))
      .map((g) => verlaufsbild(v.z, v[g.feld], g))),
    legende(d.verlaufslegende || []),
  ], { klasse: 'ist-breit' }));
}
