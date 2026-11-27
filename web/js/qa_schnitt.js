/**
 * qa_schnitt.js -- der Schnitt im Zeichenfenster der Querschnittsanalyse.
 *
 * Ein Werkzeug «Schnitt» (Benutzer, 2026-11-27): eine Strecke quer durch
 * den Querschnitt, gezeichnet wie eine Linie. Ein Pfeil in ihrer Mitte zeigt
 * auf den Teil, den sie abtrennt -- was jenseits liegt und mit dem Rest nur
 * über die Strecke zusammenhängt. Der Teil ist getönt, an der Spitze des
 * Pfeils steht b_i, die Länge, auf der der Schnitt Material von Material
 * trennt. Gerechnet wird mit ihm nur der Schubfluss (Kachel «Schubfluss»,
 * qa_schubfluss.js).
 *
 * Der Pfeil zeigt zuerst nach links der Richtung, in der man zeichnet --
 * schon beim Zeichnen sieht man ihn. Gewählt dreht ihn der Schalter «Pfeil»
 * um; seine Stellungen nennen die Richtung im Bild, «nach oben» oder «nach
 * unten», vom Kern: links und rechts der Zeichenrichtung sieht man nicht
 * mehr. Trennt ein Schnitt nichts ab, steht er grau, und seine Meldung sagt
 * warum.
 *
 * WAS HIER GERECHNET WIRD -- UND WAS NICHT:
 * Nur das Bild des Pfeils. Was ein Schnitt abtrennt, b_i und A′ und wie die
 * Richtungen heissen, kommen mit der Antwort des Kerns zur Zeichnung
 * (`schnitte`).
 */

import { mitVar, wahlSchalter } from './bausteine.js';
import { nachBild, pfad, zahlText } from './cad_ansicht.js';
import { mitTitel } from './cad_app.js';
import { schalterzeile } from './cad_palette.js';
import { el, svgEl } from './dom.js';

/** Die Art der Elemente, für das allgemeine Fenster -- eine Linie wie die Hilfslinie. */
export const SCHNITT = { liste: 'schnitte', klasse: 'schnitt', form: 'linie', vorsilbe: 'L', rang: 3 };

/** Das Werkzeug, in der Leiste vor dem Hilfspunkt. */
export const SCHNITTWERKZEUG = {
  name: 'schnitt', text: 'Schnitt', zeichen: 'cad-schnitt', taste: 'x', form: 'linie',
  titel: 'Schnitt: eine Strecke quer durch den Querschnitt – der Pfeil zeigt auf den Teil, '
    + 'durch dessen Rand der Schubfluss geht',
};

/** Wie lang der Pfeil ist und seine Spitze, in px. */
const PFEIL = 22;
const SPITZE = 7;

/**
 * Wohin der Pfeil im Bild zeigt, ein Einheitsvektor in px (nach unten
 * positiv): links der Strecke von `p` nach `q`, in ihrer Richtung gesehen,
 * oder rechts -- wie im Kern (`abtrennen.py`). Ohne Länge null.
 */
function richtungImBild(p, q, seite) {
  const l = Math.hypot(q[0] - p[0], q[1] - p[1]);
  if (!l) return null;
  const s = seite === 'rechts' ? -1 : 1;
  // Links von (t_y, t_z) liegt (−t_z, t_y); im Bild zeigt z nach oben.
  return [(-(q[1] - p[1]) / l) * s, (-(q[0] - p[0]) / l) * s];
}

/** Strecke und Pfeil eines Schnitts, in der Klasse `klasse` -- auch als Vorschau beim Zeichnen. */
export function schnittBild(a, p, q, seite, klasse = '') {
  const g = svgEl('g', { class: `cad-schnittbild ${klasse}` });
  g.append(svgEl('path', { d: pfad(a.v, [p, q], false), class: 'cad-schnitt' }));
  const d = richtungImBild(p, q, seite);
  if (!d) return g;
  const [x, y] = nachBild(a.v, [(p[0] + q[0]) / 2, (p[1] + q[1]) / 2]);
  const [sx, sy] = [x + d[0] * PFEIL, y + d[1] * PFEIL];
  const [bx, by] = [sx - d[0] * SPITZE, sy - d[1] * SPITZE];
  const [qx, qy] = [-d[1] * (SPITZE / 2), d[0] * (SPITZE / 2)];
  g.append(
    svgEl('path', { d: `M${x.toFixed(1)} ${y.toFixed(1)}L${bx.toFixed(1)} ${by.toFixed(1)}`, class: 'cad-schnittpfeil' }),
    svgEl('path', {
      d: `M${sx.toFixed(1)} ${sy.toFixed(1)}L${(bx + qx).toFixed(1)} ${(by + qy).toFixed(1)}`
        + `L${(bx - qx).toFixed(1)} ${(by - qy).toFixed(1)}Z`,
      class: 'cad-schnittspitze',
    }),
  );
  return g;
}

/** «b_i = 200 mm» hinter der Spitze des Pfeils, das i tiefgestellt. */
function breitentext(a, p, q, seite, breite) {
  const d = richtungImBild(p, q, seite);
  const [x, y] = nachBild(a.v, [(p[0] + q[0]) / 2, (p[1] + q[1]) / 2]);
  const weit = PFEIL + 6;
  let anker = 'middle';
  if (d[0] > 0.35) anker = 'start';
  else if (d[0] < -0.35) anker = 'end';
  const t = svgEl('text', {
    x: (x + d[0] * weit).toFixed(1), y: (y + d[1] * weit + (d[1] > 0.35 ? 10 : 4)).toFixed(1),
    'text-anchor': anker, class: 'cad-beschriftung cad-schnitttext',
  });
  const index = svgEl('tspan', { 'baseline-shift': 'sub', 'font-size': '8px' });
  index.textContent = 'i';
  t.append('b', index, ` = ${zahlText(breite, 0)} mm`);
  return t;
}

/**
 * Die Schnitte: was jeder abtrennt, getönt, darüber Strecke und Pfeil und
 * an dessen Spitze b_i. `info` ist, was der Kern zu den Schnitten weiss,
 * nach Kennung -- ohne Antwort nur Strecke und Pfeil. Einer, der nichts
 * abtrennt, steht grau; `texte` gibt ihm seine Meldung als Titel.
 */
export function schnitteZeichnen(a, g, schnitte, ort, info, klassen, texte) {
  for (const s of schnitte || []) {
    const [p, q] = [ort(s.von), ort(s.bis)];
    if (!p || !q) continue;
    const i = info.get(s.kennung);
    if (i?.stuecke.length) {
      g.append(svgEl('path', { d: i.stuecke.map((t) => pfad(a.v, t)).join(' '), class: 'cad-abgetrennt' }));
    }
    const ohne = i && !i.stuecke.length ? 'ist-ohne' : '';
    g.append(mitTitel(schnittBild(a, p, q, s.seite, klassen(s.kennung, ohne)), texte(s.kennung)));
    if (i?.stuecke.length) g.append(breitentext(a, p, q, s.seite, i.breite));
  }
}

/**
 * Der Schalter «Pfeil»: links oder rechts der Strecke, in ihrer Richtung
 * gesehen. Ein gewählter Schnitt nennt die Richtung im Bild, vom Kern
 * (`info.pfeile`); beim Zeichnen und bei mehreren gibt es sie nicht -- dann
 * heissen die Stellungen nach der Zeichenrichtung.
 */
export function schnittFelder(wert, setzen, info = null) {
  const seite = wert('seite');
  const zeichenrichtung = { links: 'links der Zeichenrichtung', rechts: 'rechts der Zeichenrichtung' };
  const werte = ['links', 'rechts'].map((w) => ({
    wert: w, beschriftung: info?.pfeile?.[w] || w, titel: `Der Pfeil zeigt ${zeichenrichtung[w]}`,
  }));
  return [schalterzeile('Pfeil', wahlSchalter({
    werte: mitVar(werte, seite), gewaehlt: seite, setzen: setzen('seite'),
    titel: 'Wohin der Pfeil zeigt: auf den Teil, den der Schnitt abtrennt', klasse: '.cad-wahl',
  }))];
}

/** Was der Kern zu einem gewählten Schnitt weiss: b_i und die Fläche des abgetrennten Teils. */
export function schnittInfo(info) {
  if (!info?.stuecke?.length) return [];
  return [el('p.cad-info', {
    text: `b_i = ${zahlText(info.breite, 0)} mm · A′ = ${zahlText(info.flaeche, 0)} mm² abgetrennt`,
  })];
}

/** Was in der Seitenleiste steht, während das Werkzeug zeichnet. */
export function schnittHinweis() {
  return el('p.cad-hinweis-klein', {
    text: 'Eine Strecke quer durch den Querschnitt. Der Pfeil zeigt auf den Teil, den sie '
      + 'abtrennt – zuerst links der Zeichenrichtung; gewählt dreht ihn der Schalter um. '
      + 'Gerechnet wird mit ihm der Schubfluss, in der Kachel «Schubfluss».',
  });
}
