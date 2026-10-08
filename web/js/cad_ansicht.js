/**
 * cad_ansicht.js -- Massstab, Ausschnitt und Raster eines Zeichenfensters.
 *
 * Allgemein: kennt weder Beton noch Querschnitt, nur eine Ebene mit zwei
 * Achsen in Millimetern, die erste nach rechts, die zweite nach oben. Welche
 * Namen sie tragen, sagt die App (der Querschnitt «y» und «z», ein Grundriss
 * hätte «x» und «y»).
 *
 * Gerechnet wird im Bild in Pixeln: die viewBox des SVG ist so gross wie das
 * Bild selbst, und alles Umrechnen geschieht hier. So bleiben Striche und
 * Schrift beim Zoomen gleich dick.
 */

import { svgEl } from './dom.js';

/** Eine leere Ansicht: noch nie gemessen, noch nie eingepasst. */
export function ansichtNeu() {
  return { massstab: null, ursprung: [0, 0], breite: 0, hoehe: 0 };
}

/** Welt (mm) -> Bild (px). */
export const nachBild = (v, [a, b]) => [v.ursprung[0] + v.massstab * a, v.ursprung[1] - v.massstab * b];

/** Bild (px) -> Welt (mm). */
export const nachWelt = (v, [x, h]) => [(x - v.ursprung[0]) / v.massstab, (v.ursprung[1] - h) / v.massstab];

/** Zoomt um `faktor` und hält dabei den Weltpunkt unter `bild` fest. */
export function zoomen(v, faktor, bild) {
  const neu = Math.min(80, Math.max(1e-3, v.massstab * faktor));
  const f = neu / v.massstab;
  v.ursprung = [bild[0] - (bild[0] - v.ursprung[0]) * f, bild[1] - (bild[1] - v.ursprung[1]) * f];
  v.massstab = neu;
}

/**
 * Passt das Rechteck `[[a0, b0], [a1, b1]]` ins Bild -- mit Rand für
 * Masslinien. `frei` hält zusätzlich eine Ecke frei, unten rechts, wo das
 * schwebende Fenster steht.
 */
export function einpassen(v, [[a0, b0], [a1, b1]], { rand = 46, frei = [0, 0] } = {}) {
  if (!v.breite || !v.hoehe) return;
  const b = Math.max(a1 - a0, 1);
  const h = Math.max(b1 - b0, 1);
  const nutzbreite = Math.max(40, v.breite - 2 * rand - frei[0]);
  const nutzhoehe = Math.max(40, v.hoehe - 2 * rand - frei[1]);
  v.massstab = Math.max(1e-3, Math.min(nutzbreite / b, nutzhoehe / h));
  v.ursprung = [
    rand + nutzbreite / 2 - v.massstab * (a0 + a1) / 2,
    rand + nutzhoehe / 2 + v.massstab * (b0 + b1) / 2,
  ];
}

/** Ein Pfad durch Weltpunkte, als SVG-Anweisung. */
export function pfad(v, punkte, zu = true) {
  return punkte.map((p, i) => {
    const [x, y] = nachBild(v, p);
    return `${i ? 'L' : 'M'}${x.toFixed(1)} ${y.toFixed(1)}`;
  }).join(' ') + (zu && punkte.length > 2 ? ' Z' : '');
}

export function text(x, y, inhalt, klasse, anker = 'middle') {
  const t = svgEl('text', { x: x.toFixed(1), y: y.toFixed(1), 'text-anchor': anker, class: klasse });
  t.textContent = inhalt;
  return t;
}

/**
 * Wie weit zwei Rasterlinien im Bild auseinander stehen: das Raster mal 1,
 * 2, 5, 10, … -- so dicht, dass sie nicht verschwimmen.
 */
function rasterschritt(v, raster) {
  let schritt = raster;
  for (let i = 1; schritt * v.massstab < 14 && i < 30; i += 1) {
    schritt = raster * [1, 2, 5][i % 3] * 10 ** Math.floor(i / 3);
  }
  return schritt;
}

/** Raster und Achsen, über das ganze Bild. */
export function rasterZeichnen(v, raster, [achse1, achse2]) {
  const g = svgEl('g', { class: 'cad-raster' });
  const schritt = rasterschritt(v, raster);
  const [a0, b1] = nachWelt(v, [0, 0]);
  const [a1, b0] = nachWelt(v, [v.breite, v.hoehe]);
  const fuenf = schritt * 5;
  const grobe = (w) => Math.abs(w / fuenf - Math.round(w / fuenf)) < 1e-6;
  let fein = '';
  let grob = '';
  for (let a = Math.ceil(a0 / schritt) * schritt; a <= a1; a += schritt) {
    const d = `M${nachBild(v, [a, 0])[0].toFixed(1)} 0 V${v.hoehe}`;
    if (grobe(a)) grob += d; else fein += d;
  }
  for (let b = Math.ceil(b0 / schritt) * schritt; b <= b1; b += schritt) {
    const d = `M0 ${nachBild(v, [0, b])[1].toFixed(1)} H${v.breite}`;
    if (grobe(b)) grob += d; else fein += d;
  }
  const [nx, nh] = nachBild(v, [0, 0]);
  g.append(
    svgEl('path', { d: fein, class: 'cad-raster-fein' }),
    svgEl('path', { d: grob, class: 'cad-raster-grob' }),
    svgEl('path', { d: `M0 ${nh} H${v.breite} M${nx} 0 V${v.hoehe}`, class: 'cad-achse' }),
    text(v.breite - 6, nh - 5, achse1, 'cad-achstext', 'end'),
    text(nx + 6, 12, achse2, 'cad-achstext', 'start'),
  );
  return g;
}

/** Eine Zahl, wie sie im Fenster steht: höchstens `stellen` Nachkommastellen. */
export function zahlText(wert, stellen = 1) {
  return String(Number(Number(wert).toFixed(stellen)));
}
