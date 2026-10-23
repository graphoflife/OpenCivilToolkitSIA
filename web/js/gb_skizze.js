/**
 * gb_skizze.js -- die Bausteine der Bilder im Grundbau: Grundbruch und Setzung.
 *
 * Linien, Pfeile, Masse, Winkelbögen, Text mit tiefgestellten Teilen und die
 * Schraffur unter dem Gelände -- in px, im Stil der Klassen `gb-…` im
 * Stilblatt («gb» für Grundbau). Bis 2026-10-23 standen sie in
 * gb_zeichnung.js; die Setzung (sz_zeichnung.js) zeichnet mit denselben.
 */

import { svgEl } from './dom.js';

/** Wie breit die Bilder gezeichnet werden, in px -- die Hülle skaliert sie. */
export const BREITE = 720;

/** Eine Zahl mit fester Stellenzahl, für die Beschriftung. */
export const zahl = (x, n) => Number(x).toFixed(n);

/** Eine Gruppe -- `svgEl` nimmt keine Kinder. Fehlende (null) bleiben weg. */
export function gruppe(klasse, kinder) {
  const g = svgEl('g', { class: klasse });
  g.append(...kinder.filter(Boolean));
  return g;
}

export function linie(punkte, klasse) {
  return svgEl('path', {
    d: punkte.map(([x, y], i) => `${i ? 'L' : 'M'}${x.toFixed(1)} ${y.toFixed(1)}`).join(' '),
    class: klasse,
  });
}

/** Ein Pfeil von `von` nach `bis`, die Spitze bei `bis`. */
export function pfeil(von, bis, klasse) {
  const [x1, y1] = von;
  const [x2, y2] = bis;
  const l = Math.hypot(x2 - x1, y2 - y1);
  if (l < 1) return null;
  const ux = (x2 - x1) / l;
  const uy = (y2 - y1) / l;
  const s = Math.min(9, l / 2);
  const spitze = [
    [x2, y2],
    [x2 - ux * s - uy * s * 0.45, y2 - uy * s + ux * s * 0.45],
    [x2 - ux * s + uy * s * 0.45, y2 - uy * s - ux * s * 0.45],
  ];
  return gruppe(klasse, [
    linie([von, [x2 - ux * s * 0.8, y2 - uy * s * 0.8]], 'gb-pfeil-schaft'),
    svgEl('path', { d: `M${spitze.map((q) => q.map((v) => v.toFixed(1)).join(' ')).join(' L')} Z`, class: 'gb-pfeil-spitze' }),
  ]);
}

/**
 * Text mit tiefgestellten Teilen: `teile` sind Zeichenketten und `{ unten }`
 * -- «δ», { unten: 'R' }, « = 7.1°». `drehung` dreht ihn um seinen Punkt,
 * in Grad im Gegenuhrzeigersinn -- längs eines geneigten Geländes.
 */
export function text(x, y, teile, { klasse = '', anker = 'start', drehung = 0 } = {}) {
  const t = svgEl('text', {
    x: x.toFixed(1), y: y.toFixed(1), class: `gb-text ${klasse}`, 'text-anchor': anker,
    transform: drehung ? `rotate(${-drehung} ${x.toFixed(1)} ${y.toFixed(1)})` : null,
  });
  let tief = false;
  for (const teil of [].concat(teile)) {
    const unten = typeof teil === 'object';
    const span = svgEl('tspan', {
      dy: unten === tief ? 0 : (unten ? 4 : -4),
      class: unten ? 'gb-index' : '',
    });
    span.textContent = unten ? teil.unten : teil;
    t.append(span);
    tief = unten;
  }
  return t;
}

/** Ein Winkelbogen um `mitte` von Richtung `a` nach `b` (Winkel in px-Lage, rad). */
export function bogen(mitte, r, a, b, klasse = 'gb-bogen') {
  let d = b - a;
  while (d <= -Math.PI) d += 2 * Math.PI;
  while (d > Math.PI) d -= 2 * Math.PI;
  const [cx, cy] = mitte;
  const p = (w) => [cx + r * Math.cos(w), cy + r * Math.sin(w)].map((v) => v.toFixed(1)).join(' ');
  return svgEl('path', { d: `M${p(a)} A${r} ${r} 0 0 ${d > 0 ? 1 : 0} ${p(a + d)}`, class: klasse });
}

/** Ein Mass: Linie mit Pfeilen an beiden Enden, die Schrift daneben. */
export function mass(von, bis, teile, { seite = 'rechts' } = {}) {
  const [x1, y1] = von;
  const [x2, y2] = bis;
  const mitte = [(x1 + x2) / 2, (y1 + y2) / 2];
  const senkrecht = Math.abs(x2 - x1) < Math.abs(y2 - y1);
  const lage = senkrecht
    ? { x: mitte[0] + (seite === 'rechts' ? 6 : -6), y: mitte[1] + 4, anker: seite === 'rechts' ? 'start' : 'end' }
    : { x: mitte[0], y: mitte[1] - 6, anker: 'middle' };
  return gruppe('gb-mass', [
    pfeil(mitte, von, 'gb-masspfeil'),
    pfeil(mitte, bis, 'gb-masspfeil'),
    text(lage.x, lage.y, teile, { anker: lage.anker, klasse: 'gb-masstext' }),
  ]);
}

/**
 * Die Schraffur unter dem Gelände: kurze Striche nach links unten, alle 11 px
 * längs jeder Strecke `[von, bis]` -- Punkte in px.
 */
export function schraffur(strecken) {
  const striche = [];
  for (const [a, e] of strecken) {
    const n = Math.floor(Math.hypot(e[0] - a[0], e[1] - a[1]) / 11);
    for (let i = 1; i < n; i += 1) {
      const [x, y] = [a[0] + (e[0] - a[0]) * i / n, a[1] + (e[1] - a[1]) * i / n];
      striche.push(`M${x.toFixed(1)} ${y.toFixed(1)} l-6 7`);
    }
  }
  return svgEl('path', { d: striche.join(' '), class: 'gb-schraffur' });
}
