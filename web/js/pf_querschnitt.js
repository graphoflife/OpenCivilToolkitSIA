/**
 * pf_querschnitt.js -- der Querschnitt eines Pfahls als Bild, massstäblich.
 *
 * Beim Bohrpfahl der Kreis D aus Beton, darin die Wendel ⌀_w mit der
 * Überdeckung c und die n Längsstäbe ⌀_l auf dem Radius r_s. Beim
 * Mikropfahl der Verpresskörper D und in seiner Mitte das Tragglied, ein
 * Rohr d_a mit der Wanddicke t oder ein Vollstab; gestrichelt der
 * Durchmesser nach der Abrostung Δt, mit dem der Nachweis rechnet. Der
 * Stahl dunkel, Beton und Verpresskörper grau, wie in der Situation
 * (pf_zeichnung.js).
 *
 * Alle Zahlen kommen aus dem Kern (opencivil/web/pfahldaten.py), in mm,
 * auch r_s und der Durchmesser nach der Abrostung: so, wie der Nachweis
 * sie rechnet. Hier wird nur gezeichnet.
 */

import { karte } from './bausteine.js';
import { el, svgEl } from './dom.js';
import {
  BREITE, gruppe, legende, linie, mass, pfeil, text, zahl,
} from './gb_skizze.js';

/** So gross steht der Kreis D im Bild, in px. */
const DURCHMESSER = 270;
/** Die Mitte des Kreises, in px; rechts davon die Beschriftungen. */
const MITTE = [215, 170];
/** Wie hoch das Bild ist, in px: oben Platz für r_s, unten für das Mass D. */
const HOEHE = 370;
/** Wo die Beschriftungen beginnen, in px von links. */
const ZETTEL = MITTE[0] + DURCHMESSER / 2 + 70;

/** Eine Zahl in mm, so genau wie eingegeben -- höchstens eine Nachkommastelle. */
const mm = (x) => `${Number(zahl(x, 1))} mm`;

function kreis([x, y], r, klasse) {
  return svgEl('circle', {
    cx: x.toFixed(1), cy: y.toFixed(1), r: Math.max(r, 0.6).toFixed(1), class: klasse,
  });
}

/** Ein Ring zwischen den Radien `aussen` und `innen` -- ein Pfad mit Loch. */
function ring([x, y], aussen, innen, klasse) {
  const rund = (r) => `M${(x - r).toFixed(1)} ${y.toFixed(1)} `
    + `a${r.toFixed(1)} ${r.toFixed(1)} 0 1 0 ${(2 * r).toFixed(1)} 0 `
    + `a${r.toFixed(1)} ${r.toFixed(1)} 0 1 0 ${(-2 * r).toFixed(1)} 0 Z`;
  return svgEl('path', { d: rund(aussen) + rund(innen), class: klasse, 'fill-rule': 'evenodd' });
}

/** Ein Punkt auf dem Kreis um die Mitte, `w` im Gegenuhrzeigersinn ab rechts, in px. */
function aufKreis(r, w) {
  return [MITTE[0] + r * Math.cos(w), MITTE[1] - r * Math.sin(w)];
}

/** Eine Beschriftung rechts, auf Höhe `y`, mit einem Strich zu `punkt`. */
function zettel(punkt, y, zeilen) {
  return gruppe('', [
    linie([punkt, [ZETTEL - 8, y]], 'gb-masshilfe'),
    ...zeilen.map((teile, i) => text(ZETTEL, y + 4 + 16 * i, teile, { klasse: 'gb-masstext' })),
  ]);
}

/** Eine Beschriftung längs der Strecke von `a` nach `b`, mittig darüber, von links lesbar. */
function entlang(a, b, teile) {
  let w = Math.atan2(b[1] - a[1], b[0] - a[0]);
  if (w > Math.PI / 2) w -= Math.PI;
  if (w <= -Math.PI / 2) w += Math.PI;
  const x = (a[0] + b[0]) / 2 + 6 * Math.sin(w);
  const y = (a[1] + b[1]) / 2 - 6 * Math.cos(w);
  return text(x, y, teile, { klasse: 'gb-masstext', anker: 'middle', drehung: (-w * 180) / Math.PI });
}

/** Das Mass D unter dem Kreis, mit Hilfslinien bis zu seinem Rand. */
function durchmesser(R, teile) {
  const [x, y] = MITTE;
  const unten = y + R + 26;
  return gruppe('', [
    linie([[x - R, y], [x - R, unten + 4]], 'gb-masshilfe'),
    linie([[x + R, y], [x + R, unten + 4]], 'gb-masshilfe'),
    mass([x - R, unten], [x + R, unten], teile),
  ]);
}

function bohrpfahl(q) {
  const m = DURCHMESSER / q.D;
  const R = (q.D / 2) * m;
  // Die Wendel: aussen um c vom Rand, so dick wie ihr Stab.
  const wendel = (q.D / 2 - q.c - q.phi_w / 2) * m;
  const staebe = Array.from({ length: q.n }, (_, k) => aufKreis(q.r_s * m, (2 * Math.PI * k) / q.n));
  // r_s zu dem Stab, der am nächsten links oben liegt -- dort ist Platz.
  const ecke = [MITTE[0] - R, MITTE[1] - R];
  const naehe = (p) => Math.hypot(p[0] - ecke[0], p[1] - ecke[1]);
  const oben = staebe.reduce((a, b) => (naehe(b) < naehe(a) ? b : a), staebe[0]);
  return [
    kreis(MITTE, R, 'gb-fundament'),
    svgEl('circle', {
      cx: MITTE[0], cy: MITTE[1], r: wendel.toFixed(1), class: 'pf-wendel',
      'stroke-width': Math.max(q.phi_w * m, 1.2).toFixed(1),
    }),
    ...staebe.map((p) => kreis(p, Math.max((q.phi_l / 2) * m, 2.2), 'pf-stahl')),
    ...(oben ? [
      pfeil(MITTE, oben, 'gb-masspfeil'),
      entlang(MITTE, oben, ['r', { unten: 's' }, ` = ${mm(q.r_s)}`]),
      kreis(MITTE, 2.5, 'pf-stahl'),
      zettel(staebe[0], MITTE[1] - 40, [[`${q.n} ⌀`, { unten: 'l' }, ` = ${mm(q.phi_l)}`]]),
    ] : []),
    zettel(aufKreis(wendel, -Math.PI / 5), MITTE[1] + 30, [
      ['Wendel ⌀', { unten: 'w' }, ` = ${mm(q.phi_w)}`],
      ['Ganghöhe s', { unten: 'w' }, ` = ${mm(q.s_w)}`],
    ]),
    // Der Strich zeigt in die Mitte der Überdeckung, zwischen Rand und Wendel.
    zettel(aufKreis((q.D / 2 - q.c / 2) * m, -Math.PI / 2.6), MITTE[1] + 96,
      [[`Überdeckung c = ${mm(q.c)}`]]),
    durchmesser(R, [`D = ${mm(q.D)}`]),
  ];
}

function mikropfahl(q) {
  const m = DURCHMESSER / q.D;
  const R = (q.D / 2) * m;
  const ra = (q.d_a / 2) * m;
  const rohr = q.t !== null;
  const teile = [
    kreis(MITTE, R, 'pf-verpresskoerper'),
    rohr ? ring(MITTE, ra, Math.max(ra - q.t * m, 0), 'pf-stahl') : kreis(MITTE, ra, 'pf-stahl'),
  ];
  if (q.dt > 0) teile.push(kreis(MITTE, (q.d_rest / 2) * m, 'pf-abrostung'));
  teile.push(
    zettel(aufKreis(ra, Math.PI / 4), MITTE[1] - 60, rohr
      ? [[`Rohr d`, { unten: 'a' }, ` = ${mm(q.d_a)}`], [`Wanddicke t = ${mm(q.t)}`]]
      : [[`Vollstab ⌀ = ${mm(q.d_a)}`]]),
    q.dt > 0
      ? zettel(aufKreis((q.d_rest / 2) * m, -Math.PI / 4), MITTE[1] + 20, [
        [`Abrostung Δt = ${mm(q.dt)}`],
        ['gerechnet mit ', rohr ? 'd' : '⌀', rohr ? { unten: 'a' } : '', ` = ${mm(q.d_rest)}`],
      ].map((z) => z.filter((t) => t !== '')))
      : null,
    zettel(aufKreis(R, -Math.PI / 2.6), MITTE[1] + 96, [['Verpresskörper']]),
    durchmesser(R, [`D = ${mm(q.D)}`]),
  );
  return teile;
}

/**
 * Die Karte «Querschnitt» eines Pfahls -- oder nichts, solange der Kern
 * ihn nicht geschickt hat.
 */
export function querschnittKarte(q) {
  if (!(q?.D > 0)) return null;
  const svg = svgEl('svg', {
    viewBox: `0 0 ${BREITE} ${HOEHE}`, class: 'gb-bild', role: 'img',
    'aria-label': q.art === 'bohrpfahl' ? 'Querschnitt des Bohrpfahls' : 'Querschnitt des Mikropfahls',
  });
  svg.append(...(q.art === 'bohrpfahl' ? bohrpfahl(q) : mikropfahl(q)).filter(Boolean));
  return karte('Querschnitt', [
    el('div.gb-bildhuelle', {}, [svg]),
    legende(q.legende),
  ], { bild: svg });
}
