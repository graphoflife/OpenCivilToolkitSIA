/**
 * ds_grundriss.js -- der Grundriss einer Durchstanzstelle als Bild.
 *
 * Von oben gesehen, x nach rechts, y nach oben, in mm: die Stütze oder Wand,
 * die Plattenränder -- was jenseits liegt, grau --, die Aussparungen mit
 * einem Kreuz und der Nachweisschnitt im Abstand d_v/2. Was von ihm zählt,
 * ist ausgezogen, was nicht zählt, gestrichelt: neben den Ecken grosser
 * Stützen und im Schatten der Aussparungen. Braucht es Durchstanzbewehrung,
 * stehen ihre Leisten mit den Ankern da und der äussere Schnitt um sie.
 *
 * Alles kommt aus der Lösung, wie der Kern es gerechnet hat
 * (opencivil/web/durchstanzdaten.py) -- auch der Umriss der Stütze. Steht im
 * Bild etwas anderes als in den Eingaben, ist die Rechnung noch nicht
 * zurück. Zwei Bilder zeichnen damit: die Karte im Reiter «Diagramme» und
 * das Zeichenfenster, in dem die Aussparungen entstehen (ds_zeichnung.js) --
 * beide über `grundrissTeile`; das Zeichenfenster gibt ihm die Aussparungen,
 * wie sie gerade gezeichnet sind.
 */

import { karte } from './bausteine.js';
import { el, svgEl } from './dom.js';
import { BREITE, linie, text, zahl } from './gb_skizze.js';
import { zustand } from './zustand.js';

/** So hoch wird das Bild höchstens und mindestens, in px. */
const HOEHE = [260, 520];
const RAND = 18;

/** `[x, y]` -> «M… L…», geschlossen oder offen. */
function pfadVon(punkte, zu) {
  const d = punkte.map(([x, y], i) => `${i ? 'L' : 'M'}${x.toFixed(1)} ${y.toFixed(1)}`).join(' ');
  return zu ? `${d} Z` : d;
}

/**
 * Was vom Rechteck `sicht` jenseits eines Plattenrands liegt: das Rechteck,
 * an der Geraden des Rands abgeschnitten. Nur fürs Bild -- welcher Teil des
 * Schnitts in der Platte liegt, sagt der Kern.
 */
function jenseits([[x0, y0], [x1, y1]], { punkt, richtung }) {
  const n = [Math.cos(richtung), Math.sin(richtung)];
  const seite = (p) => (p[0] - punkt[0]) * n[0] + (p[1] - punkt[1]) * n[1];
  const ecken = [[x0, y0], [x1, y0], [x1, y1], [x0, y1]];
  const aussen = [];
  ecken.forEach((p, i) => {
    const q = ecken[(i + 1) % 4];
    const [sp, sq] = [seite(p), seite(q)];
    if (sp <= 0) aussen.push(p);
    if ((sp < 0 && sq > 0) || (sp > 0 && sq < 0)) {
      const t = sp / (sp - sq);
      aussen.push([p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])]);
    }
  });
  return aussen;
}

/**
 * Die Teile des Grundrisses als SVG, für ein Bild mit der Abbildung `bild`
 * (mm -> px) und dem sichtbaren Ausschnitt `sicht` in mm -- bis dorthin
 * reichen die Plattenränder. `aussparungen` in mm, unter Stütze und Schnitt:
 * die der Lösung, oder im Zeichenfenster die, wie sie gerade gezeichnet sind.
 */
export function grundrissTeile(s, bild, sicht, aussparungen = s.aussparungen) {
  const px = (punkte) => punkte.map(bild);
  const teile = [];
  for (const r of s.raender) {
    const aussen = jenseits(sicht, r);
    if (aussen.length >= 3) teile.push(svgEl('path', { d: pfadVon(px(aussen), true), class: 'ds-jenseits' }));
  }
  for (const r of s.raender) {
    const t = [-Math.sin(r.richtung), Math.cos(r.richtung)];
    const weit = Math.hypot(sicht[1][0] - sicht[0][0], sicht[1][1] - sicht[0][1]) * 2;
    teile.push(linie(px([
      [r.punkt[0] - weit * t[0], r.punkt[1] - weit * t[1]],
      [r.punkt[0] + weit * t[0], r.punkt[1] + weit * t[1]],
    ]), 'ds-rand'));
  }
  for (const a of aussparungen) teile.push(...aussparungTeile(px(a)));
  teile.push(svgEl('path', { d: pfadVon(px(s.umriss), true), class: 'ds-stuetze' }));
  if (s.bewehrung) teile.push(...bewehrungTeile(s.bewehrung, px));
  for (const l of s.schnitt) {
    teile.push(linie(px(l.punkte), l.zaehlt ? 'ds-schnitt' : 'ds-schnitt-nicht'));
  }
  return teile;
}

/**
 * Die Durchstanzbewehrung: der Stahlpilz mit seinen Stegen und dem Schnitt um
 * ihn, je Leiste eine Linie vom Rand der gestützten Fläche bis zum letzten
 * Anker, die Anker als Punkte, und der äussere Schnitt um sie (Figur 26) --
 * was nicht zählt, gestrichelt.
 */
function bewehrungTeile(b, px) {
  const teile = [];
  if (b.pilz) {
    teile.push(svgEl('path', { d: pfadVon(px(b.pilz.umriss), true), class: 'ds-pilzflaeche' }));
    for (const steg of b.pilz.stege) teile.push(linie(px(steg), 'ds-steg'));
    for (const l of b.pilz.schnitt) {
      teile.push(linie(px(l.punkte), l.zaehlt ? 'ds-pilzschnitt' : 'ds-pilzschnitt-nicht'));
    }
  }
  for (const l of b.aussen) teile.push(linie(px(l.punkte), l.zaehlt ? 'ds-aussen' : 'ds-aussen-nicht'));
  for (const l of b.leisten) {
    const punkte = px([l.wurzel, ...l.anker]);
    teile.push(linie(punkte, 'ds-leiste'));
    for (const [x, y] of punkte.slice(1)) {
      teile.push(svgEl('circle', { cx: x.toFixed(1), cy: y.toFixed(1), r: 2.6, class: 'ds-anker' }));
    }
  }
  return teile;
}

/** Eine Aussparung: der Umriss und ein Kreuz zwischen den äussersten Ecken, wie im Plan. */
export function aussparungTeile(punkte, klasse = '') {
  const xs = punkte.map((p) => p[0]);
  const ys = punkte.map((p) => p[1]);
  const [x0, x1, y0, y1] = [Math.min(...xs), Math.max(...xs), Math.min(...ys), Math.max(...ys)];
  return [
    svgEl('path', { d: pfadVon(punkte, true), class: `ds-aussparung ${klasse}` }),
    svgEl('path', {
      d: `M${x0.toFixed(1)} ${y0.toFixed(1)} L${x1.toFixed(1)} ${y1.toFixed(1)} `
        + `M${x0.toFixed(1)} ${y1.toFixed(1)} L${x1.toFixed(1)} ${y0.toFixed(1)}`,
      class: 'ds-aussparung-kreuz',
    }),
  ];
}

/** Was im Bild sein soll, in mm: Stütze, Schnitte, Bewehrung, Pilz und Aussparungen, mit Rand. */
export function grundrissUmfang(s) {
  const punkte = [...s.umriss, ...s.schnitt.flatMap((l) => l.punkte), ...s.aussparungen.flat(),
    ...(s.bewehrung?.aussen || []).flatMap((l) => l.punkte),
    ...(s.bewehrung?.pilz?.schnitt || []).flatMap((l) => l.punkte)];
  const xs = punkte.map((p) => p[0]);
  const ys = punkte.map((p) => p[1]);
  const rand = Math.max(s.d_v, 0.08 * Math.max(Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys)));
  return [[Math.min(...xs) - rand, Math.min(...ys) - rand], [Math.max(...xs) + rand, Math.max(...ys) + rand]];
}

/** Das Bild für den Reiter «Diagramme»: fest im Massstab, so breit wie die Bilder des Grundbaus. */
function grundrissBild(s) {
  const sicht = grundrissUmfang(s);
  const [[x0, y0], [x1, y1]] = sicht;
  const k0 = (BREITE - 2 * RAND) / (x1 - x0);
  const hoehe = Math.min(HOEHE[1], Math.max(HOEHE[0], (y1 - y0) * k0 + 2 * RAND));
  const k = Math.min(k0, (hoehe - 2 * RAND) / (y1 - y0));
  const links = (BREITE - (x1 - x0) * k) / 2;
  const oben = (hoehe - (y1 - y0) * k) / 2;
  const bild = ([x, y]) => [links + (x - x0) * k, oben + (y1 - y) * k];
  const welt = ([u, v]) => [x0 + (u - links) / k, y1 - (v - oben) / k];
  const svg = svgEl('svg', { viewBox: `0 0 ${BREITE} ${hoehe.toFixed(0)}`, class: 'gb-bild' });
  // Jenseits des Rands grau bis an den Bildrand, nicht nur bis an den Umfang.
  svg.append(...grundrissTeile(s, bild, [welt([0, hoehe]), welt([BREITE, 0])]));
  // Die Achsen unten links: x nach rechts, y nach oben.
  const [ax, ay] = [RAND + 4, hoehe - RAND];
  svg.append(
    linie([[ax, ay], [ax + 34, ay]], 'ds-achse'), linie([[ax, ay], [ax, ay - 34]], 'ds-achse'),
    text(ax + 38, ay + 4, ['x'], { klasse: 'gb-zart' }), text(ax - 3, ay - 38, ['y'], { klasse: 'gb-zart' }),
  );
  return svg;
}

/** Die Zeilen unter dem Bild: der Schnitt, was nicht zählt, die Bewehrung, das Ergebnis. */
function legende(s) {
  const b = s.bewehrung;
  const zeilen = [
    `Nachweisschnitt im Abstand d_v/2 = ${zahl(s.d_v / 2, 0)} mm um die gestützte Fläche; `
      + `wirksam u = k_e · u_red = ${zahl(s.u, 0)} mm mit k_e = ${zahl(s.k_e, 2)}.`,
    'Gestrichelt, was nicht zählt: weiter als 1.5·d_v von den Ecken grosser Stützen und entlang '
      + 'von Wänden, und was hinter Aussparungen liegt.',
  ];
  if (!b) {
    zeilen.push(`V_d = ${zahl(s.V_d, 1)} kN ${s.erfuellt ? '≤' : '>'} V_Rd,c = ${zahl(s.V_Rd_c, 1)} kN – `
      + `${s.erfuellt ? 'erfüllt' : 'nicht erfüllt'}, α = ${s.grad}.`);
  } else {
    zeilen.push(`Ohne Bewehrung V_Rd,c = ${zahl(s.V_Rd_c, 1)} kN < V_d = ${zahl(s.V_d, 1)} kN.`);
    if (b.pilz) {
      zeilen.push(`Stahlpilz: ${b.pilz.name}. Seine gestützte Fläche reicht bis an die Enden der `
        + `Stege; der Schnitt um sie (violett) liegt d_v,P/2 = ${zahl(b.pilz.d_v / 2, 0)} mm weit `
        + 'aussen. Den Widerstand des Pilzes selbst bestätigt der Hersteller.');
    }
    if (b.leisten.length) {
      zeilen.push(
        `Durchstanzbewehrung: ${b.name}, Anker ⌀${zahl(b.durchmesser, 0)} im Abstand `
          + `${b.abstaende.map((a) => zahl(a, 0)).join(' / ')} mm vom Rand `
          + `${b.pilz ? 'des Pilzes' : 'der Stütze'}.`,
        `Äusserer Schnitt (orange) im Abstand 0.5·d_v,out = ${zahl(b.d_v_out / 2, 0)} mm um die `
          + `äussersten Anker: u_out = ${zahl(b.u_out, 0)} mm, V_d,out = ${zahl(b.V_d_out, 1)} kN, `
          + `V_Rd,c,out = ${zahl(b.V_Rd_c_out, 1)} kN.`,
        `V_Rd,s = ${zahl(b.V_Rd_s, 1)} kN, V_Rd,max = ${zahl(b.V_Rd_max, 1)} kN.`,
      );
    } else if (b.pilz) {
      zeilen.push(`Um den Pilz: V_d,P = ${zahl(b.V_d_out, 1)} kN ≤ V_Rd,c,P = ${zahl(b.V_Rd_c_out, 1)} kN `
        + '-- ohne Durchstanzbewehrung.');
    }
    zeilen.push(`${s.erfuellt ? 'Alle Nachweise erfüllt' : 'Nicht alle Nachweise erfüllt'}, `
      + `kleinstes α = ${s.grad}.`);
  }
  return el('div.gb-legende', {}, zeilen.map((z) => el('p', { text: z })));
}

/** Die Karte einer Durchstanzstelle im Reiter «Diagramme». Das Panel darum baut bericht.js. */
export function durchstanzKarten(kennung) {
  const s = zustand.loesung?.durchstanzstellen?.[kennung];
  if (!s) return [karte('Grundriss', [el('p.karte-hinweis', { text: 'Noch nicht gerechnet.' })])];
  return [karte('Grundriss', [el('div.gb-bildhuelle', {}, [grundrissBild(s)]), legende(s)],
    { klasse: 'ist-breit' })];
}
