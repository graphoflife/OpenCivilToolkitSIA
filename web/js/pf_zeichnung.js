/**
 * pf_zeichnung.js -- die Situation eines Pfahls als Bild.
 *
 * Ein Schnitt längs der Achse: die Schichten vom Terrain an nach unten, mit
 * Namen und Kennwerten, links die Tiefen, gestrichelt das Grundwasser. Darin
 * der Pfahl vom Kopf bis zum Fuss, beim Mikropfahl das Tragglied in der
 * Mitte des Verpresskörpers. Rechts vom Pfahl, je Stück des Mantels, die
 * Mantelreibung als Balken, unter dem Fuss der Spitzendruck -- wie sie in
 * den äusseren Widerstand eingehen.
 *
 * Masse und Schichten kommen aus dem Eintrag, wie sie eingegeben sind; die
 * Mantelreibung je Stück, der Spitzendruck und die Legende aus der Lösung
 * (opencivil/web/pfahldaten.py). Die Tiefen sind massstäblich; der Pfahl
 * ist es in der Breite nur, solange er so weder verschwindet noch die
 * Schichten verdeckt -- sonst sagt es die Legende.
 */

import { karte } from './bausteine.js';
import { el, svgEl } from './dom.js';
import {
  BREITE, legende, linie, mass, pfeil, text, textzeile, wasserzeichen, zahl,
} from './gb_skizze.js';
import { verlaufKarten } from './pf_verlauf.js';
import { eintragVon, zustand } from './zustand.js';

const RAND = 16;
/** Links Platz für die Tiefen, oben für den Durchmesser, unten für den Spitzendruck, in px. */
const LINKS = 58;
const OBEN = 30;
const UNTEN = 40;
/** So hoch wird der Baugrund gezeichnet, in px. */
const HOEHE = 460;
/** Die Achse des Pfahls, in px von links -- links davon ist Platz für die Schichten. */
const ACHSE = 370;
/** So breit wird der Pfahl mindestens und höchstens gezeichnet, in px. */
const BREITE_PFAHL = [12, 48];
/** So lang wird der Balken der grössten Mantelreibung, in px. */
const BALKEN = 130;

/** Wo die Schichten liegen, wie eingegeben: je Schicht Ober- und Unterkante ab Terrain, in m. */
function lagen(schichten) {
  let oben = 0;
  return schichten.map((schicht) => {
    const lage = { schicht, z_o: oben, z_u: oben + Math.max(schicht.d, 0) };
    oben = lage.z_u;
    return lage;
  });
}

/** Tiefe, Massstab und die Breite, in der der Pfahl gezeichnet wird. */
function massstab(t) {
  const schichten = lagen(t.schichten);
  const fuss = Math.max(t.t_K, 0) + Math.max(t.L, 0);
  const tiefe = Math.max(schichten.length ? schichten[schichten.length - 1].z_u : 0, fuss, 1e-3);
  const k = HOEHE / tiefe;
  const echt = (t.D / 1000) * k;
  const breite = Math.min(Math.max(echt, BREITE_PFAHL[0]), BREITE_PFAHL[1]);
  return { schichten, tiefe, fuss, k, breite, verzerrt: Math.abs(breite - echt) > 0.05 * echt };
}

/** Die Kennwerte einer Schicht, mit denen sie trägt -- drainiert oder undrainiert. */
function festigkeit(s) {
  return s.verhalten === 'drainiert'
    ? ["φ'", { unten: 'k' }, ` = ${zahl(s.phi_k, 1)}°, c'`, { unten: 'k' }, ` = ${zahl(s.c_k, 1)} kN/m²`]
    : ['s', { unten: 'u,k' }, ` = ${zahl(s.s_u, 1)} kN/m²`];
}

/**
 * Der Schnitt: Schichten, Grundwasser, Pfahl, Mantelreibung und
 * Spitzendruck. `d` ist, was der Kern dazu sagt, oder nichts, solange nicht
 * gerechnet ist.
 */
function situationsbild(t, d) {
  const { schichten, tiefe, fuss, k, breite } = massstab(t);
  const y0 = RAND + OBEN;
  const y = (z) => y0 + z * k;
  const rechts = BREITE - RAND;
  const hoehe = Math.round(y(tiefe) + UNTEN + RAND);
  const svg = svgEl('svg', {
    viewBox: `0 0 ${BREITE} ${hoehe}`, class: 'gb-bild', role: 'img',
    'aria-label': `Situation des Pfahls ${t.name}`,
  });
  const zeichne = (...teile) => svg.append(...teile.filter(Boolean));

  // -- Schichten: Bänder mit Namen und Kennwerten ---------------------------
  schichten.forEach(({ schicht, z_o, z_u }, i) => {
    const [oben, dicke] = [y(z_o), (z_u - z_o) * k];
    zeichne(svgEl('rect', {
      x: LINKS.toFixed(1), y: oben.toFixed(1), width: (rechts - LINKS).toFixed(1),
      height: dicke.toFixed(1), class: `sz-schicht sz-schicht-${i % 2}`,
    }));
    const zeilen = dicke >= 50
      ? [[schicht.name], [`d = ${zahl(schicht.d, 2)} m, γ = ${zahl(schicht.gamma, 1)} kN/m³`],
        festigkeit(schicht)]
      : dicke >= 36 ? [[schicht.name], festigkeit(schicht)] : dicke >= 16 ? [[schicht.name]] : [];
    zeilen.forEach((teile, j) => zeichne(text(LINKS + 6, oben + 17 + 15 * j, teile,
      { klasse: j ? 'gb-zart' : 'sz-name' })));
  });

  // -- Die Tiefen links: Grenzen der Schichten, Kopf und Fuss ---------------
  const tiefen = [...new Set([0, ...schichten.map((s) => s.z_u), Math.max(t.t_K, 0), fuss])]
    .sort((a, b) => a - b);
  let letzte = -Infinity;
  for (const z of tiefen) {
    if (y(z) - letzte < 13) continue;
    zeichne(
      linie([[LINKS - 5, y(z)], [LINKS, y(z)]], 'sz-strich'),
      text(LINKS - 8, y(z) + 4, [`${zahl(z, 2)} m`], { anker: 'end', klasse: 'gb-masstext' }),
    );
    letzte = y(z);
  }
  zeichne(linie([[LINKS, y0], [rechts, y0]], 'gb-gelaende'));

  // -- Grundwasser, gestrichelt, das Zeichen rechts --------------------------
  if (t.t_w >= 0 && t.t_w <= tiefe) {
    zeichne(
      linie([[LINKS, y(t.t_w)], [rechts, y(t.t_w)]], 'gb-wasser'),
      wasserzeichen([rechts - 34, y(t.t_w)], 'GW'),
    );
  }

  // -- Der Pfahl, beim Mikropfahl mit dem Tragglied --------------------------
  const [kopf, unten] = [y(Math.max(t.t_K, 0)), y(fuss)];
  const [l, r] = [ACHSE - breite / 2, ACHSE + breite / 2];
  const mikro = t.art === 'mikropfahl';
  zeichne(svgEl('rect', {
    x: l.toFixed(1), y: kopf.toFixed(1), width: breite.toFixed(1),
    height: (unten - kopf).toFixed(1), class: mikro ? 'pf-verpresskoerper' : 'gb-fundament',
  }));
  if (mikro) {
    const stab = Math.min(Math.max((t.d_a / 1000) * k, 3), breite - 4);
    zeichne(svgEl('rect', {
      x: (ACHSE - stab / 2).toFixed(1), y: kopf.toFixed(1), width: stab.toFixed(1),
      height: (unten - kopf).toFixed(1), class: 'pf-stahl',
    }));
  }
  zeichne(
    text(r + 6, kopf - 7, [`D = ${zahl(t.D, 0)} mm`], { klasse: 'gb-masstext' }),
    mass([l - 12, kopf], [l - 12, unten], [`L = ${zahl(t.L, 2)} m`], { seite: 'links' }),
  );

  // -- Mantelreibung je Stück, Spitzendruck unter dem Fuss -------------------
  const stuecke = d?.stuecke || [];
  const groesste = Math.max(...stuecke.map((s) => s.q_s), 0);
  for (const s of stuecke) {
    const [a, e] = [y(s.z_o), y(s.z_u)];
    const lang = groesste > 0 ? (s.q_s / groesste) * BALKEN : 0;
    zeichne(svgEl('rect', {
      x: (r + 3).toFixed(1), y: a.toFixed(1), width: lang.toFixed(1),
      height: (e - a).toFixed(1), class: 'pf-mantel',
    }));
    if (e - a >= 14) {
      zeichne(text(r + 9 + lang, (a + e) / 2 + 4, ['q', { unten: 's,k' }, ` = ${zahl(s.q_s, 1)} kN/m²`],
        { klasse: 'pf-widerstand' }));
    }
  }
  if (d?.q_b != null) {
    const xs = breite >= 30 ? [l + breite / 6, ACHSE, r - breite / 6] : [ACHSE];
    zeichne(
      ...xs.map((x) => pfeil([x, unten + 26], [x, unten + 1], 'pf-spitze')),
      text(r + 9, unten + 20, ['q', { unten: 'b,k' }, ` = ${zahl(d.q_b, 0)} kN/m²`],
        { klasse: 'pf-widerstand' }),
    );
  }
  return svg;
}

/**
 * Die Zeilen unter dem Bild aus dem Kern: Mantel und Fuss, die
 * Bemessungswerte, was massgebend ist. Dazu, was nur das Bild weiss: dass
 * der Pfahl nicht massstäblich breit ist.
 */
function legendeVon(t, d) {
  const zeilen = d ? [...d.legende] : [textzeile('Noch nicht gerechnet.')];
  if (massstab(t).verzerrt) zeilen.push(textzeile('Die Breite des Pfahls ist nicht massstäblich.'));
  return legende(zeilen);
}

/**
 * Die Karten eines Pfahls im Reiter «Diagramme»: die Situation, dann je
 * Kombination die Verläufe über die Tiefe (pf_verlauf.js). Das Panel darum
 * baut bericht.js.
 */
export function pfahlKarten(kennung) {
  const t = eintragVon(kennung);
  if (!t) return [];
  const d = zustand.loesung?.zeichendaten?.[kennung];
  return [karte('Situation', [
    el('div.gb-bildhuelle', {}, [situationsbild(t, d)]),
    legendeVon(t, d),
  ], { klasse: 'ist-breit' }), ...verlaufKarten(d)];
}
