/**
 * pf_verlauf.js -- die Verläufe eines Pfahls über die Tiefe.
 *
 * Je Kombination eine Karte: nebeneinander die Normalkraft N und die
 * Setzung w, und wo eine Last quer wirkt, die Verschiebung y, die
 * Verdrehung θ, das Moment M, die Querkraft V und der Bettungsdruck p --
 * je über der Tiefe ab Terrain, die Tiefe nach unten wie im Bild der
 * Situation. Angeschrieben ist der Wert mit dem grössten Betrag, mit
 * Punkt; was überall null ist, fehlt. Neben dem Bettungsdruck gestrichelt
 * der Erdwiderstand, den er nicht übersteigen darf -- so weit er ins Bild
 * fällt: bis zum Doppelten des grössten Drucks.
 *
 * Gerechnet wird nichts: die Werte kommen fertig aus dem Kern
 * (opencivil/web/pfahldaten.py), mit dem Bemessungswert des
 * Verformungsmoduls, wie die Legende sagt.
 */

import { achsenkreuz } from './achsen.js';
import { karte } from './bausteine.js';
import { el, svgEl } from './dom.js';
import { legende, zahl } from './gb_skizze.js';

/** Die Verläufe: Feld der Daten, Achsentitel, Stellen der Beschriftung, Farbe, Feld der Grenze. */
const GROESSEN = [
  { feld: 'N', titel: 'N [kN]', stellen: 0, klasse: 'bs-d-n' },
  { feld: 'w', titel: 'w [mm]', stellen: 2, klasse: 'pf-d-w' },
  { feld: 'y', titel: 'y [mm]', stellen: 2, klasse: 'pf-d-w' },
  { feld: 'theta', titel: 'θ [mrad]', stellen: 2, klasse: 'bs-d-phi' },
  { feld: 'M', titel: 'M [kNm]', stellen: 1, klasse: 'bs-d-m' },
  { feld: 'V', titel: 'V [kN]', stellen: 1, klasse: 'bs-d-v' },
  { feld: 'p', titel: 'p [kN/m²]', stellen: 0, klasse: 'pf-d-p', grenze: 'p_grenze' },
];

/** So weit, gemessen am grössten Wert, reicht das Bild für die Grenze. */
const GRENZE_IM_BILD = 2;

const BREITE = 168;
const HOEHE = 380;
const RAND = { oben: 12, rechts: 14, unten: 34, links: 40 };

/** Der Index des Werts mit dem grössten Betrag. */
function groesster(werte) {
  return werte.reduce((best, v, i) => (Math.abs(v) > Math.abs(werte[best]) ? i : best), 0);
}

/**
 * Die Stücke der Linie (w über z), die nicht über `oben` hinausgehen -- an
 * dieser Grenze geschnitten, damit nichts über das Bild hinaus zeichnet.
 */
function bisZu(z, w, oben) {
  const stuecke = [];
  let stueck = [];
  for (let k = 0; k < z.length; k += 1) {
    if (k > 0 && (w[k - 1] - oben) * (w[k] - oben) < 0) {
      const t = (oben - w[k - 1]) / (w[k] - w[k - 1]);
      stueck.push([oben, z[k - 1] + t * (z[k] - z[k - 1])]);
      if (w[k] > oben) {
        stuecke.push(stueck);
        stueck = [];
      }
    }
    if (w[k] <= oben) stueck.push([w[k], z[k]]);
  }
  stuecke.push(stueck);
  return stuecke.filter((s) => s.length > 1);
}

/**
 * Ein Verlauf über die Tiefe: die Fläche zwischen null und der Kurve, der
 * grösste Wert -- und, wo es eine gibt, die Grenze beidseits gestrichelt.
 */
function verlaufsbild(z, werte, { titel, stellen, klasse }, grenze) {
  const i = groesster(werte);
  const spitze = Math.abs(werte[i]);
  let [von, bis] = [Math.min(0, ...werte), Math.max(0, ...werte)];
  const weit = grenze ? Math.min(Math.max(...grenze), GRENZE_IM_BILD * spitze) : 0;
  [von, bis] = [Math.min(von, -weit), Math.max(bis, weit)];
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
  if (grenze) {
    for (const seite of [1, -1]) {
      for (const stueck of bisZu(z, grenze, seite > 0 ? bis : -von)) {
        bild.daten.append(svgEl('path', {
          d: pfad(stueck.map(([w, zi]) => [bild.x(seite * w), bild.y(zi)])),
          class: `pf-d-grenze ${klasse}`,
        }));
      }
    }
  }
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
      .map((g) => verlaufsbild(v.z, v[g.feld], g, g.grenze && v[g.grenze]))),
    legende(d.verlaufslegende || []),
  ], { klasse: 'ist-breit' }));
}
