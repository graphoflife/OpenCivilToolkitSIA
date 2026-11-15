/**
 * cad_ansicht.js -- Massstab, Ausschnitt und Raster eines Zeichenfensters.
 *
 * Allgemein: kennt weder Beton noch Querschnitt, nur eine Ebene mit zwei
 * Achsen, die erste nach rechts, die zweite nach oben. Welche Namen sie
 * tragen und in welcher Einheit gezeichnet wird, sagt die App (der
 * Querschnitt «y» und «z» in mm, das Balkensystem «x» und «z» in m).
 *
 * Gerechnet wird im Bild in Pixeln: die viewBox des SVG ist so gross wie das
 * Bild selbst, und alles Umrechnen geschieht hier. So bleiben Striche und
 * Schrift beim Zoomen gleich dick.
 *
 * IM RAUM:
 * Eine Zeichnung mit drei Achsen sieht man parallel projiziert, von einer
 * Richtung, die sich drehen lässt (cad_raum.js). Die Ansicht trägt dann ihre
 * `basis`: die Richtungen in der Zeichnung, die im Bild nach rechts und
 * nach oben zeigen. In der Ebene fehlt sie -- es gilt die erste Achse nach
 * rechts, die zweite nach oben. Ein Punkt im Bild ist im Raum eine Gerade;
 * wo der Zeiger hinzeigt, sagt erst die Arbeitsebene (`ebene`): die Achse,
 * die auf ihr senkrecht steht, und ihre Lage auf dieser Achse. Weil die
 * Projektion parallel ist, bleibt eine Gerade im Bild eine Gerade, und eine
 * Stelle auf einer Strecke liegt im Bild beim selben Anteil wie in der
 * Zeichnung -- darum trifft und fängt das Fenster im Bild.
 */

import { skalar } from './cad_modell.js';
import { svgEl } from './dom.js';

/**
 * Eine leere Ansicht: noch nie gemessen, noch nie eingepasst. `grenzen`:
 * kleinster und grösster Massstab, in Bildpunkten je Einheit der Zeichnung.
 */
export function ansichtNeu(grenzen = [1e-3, 80]) {
  return { massstab: null, ursprung: [0, 0], breite: 0, hoehe: 0, grenzen, basis: null, ebene: null };
}

/** Die Richtungen nach rechts und nach oben, wo die Ansicht keine eigenen hat: die Ebene. */
const EBEN = [[1, 0], [0, 1]];

/** Welt -> Bild (px). */
export function nachBild(v, p) {
  const [rechts, oben] = v.basis || EBEN;
  return [v.ursprung[0] + v.massstab * skalar(p, rechts), v.ursprung[1] - v.massstab * skalar(p, oben)];
}

/**
 * Bild (px) -> Welt: in der Ebene der Punkt selbst, im Raum der Punkt auf
 * der Arbeitsebene, den man dort sieht. Sieht man sie genau von der Seite,
 * trifft die Gerade sie nicht -- dann der Punkt senkrecht auf sie.
 */
export function nachWelt(v, [x, h]) {
  const a = (x - v.ursprung[0]) / v.massstab;
  const b = (v.ursprung[1] - h) / v.massstab;
  if (!v.basis) return [a, b];
  const [rechts, oben] = v.basis;
  const p = rechts.map((r, i) => a * r + b * oben[i]);
  if (!v.ebene) return p;
  const { achse, lage } = v.ebene;
  const blick = blickrichtung(v);
  if (Math.abs(blick[achse]) < 1e-9) {
    p[achse] = lage;
    return p;
  }
  const t = (lage - p[achse]) / blick[achse];
  return p.map((w, i) => w + t * blick[i]);
}

/** Die Richtung, aus der man in den Raum blickt -- senkrecht auf das Bild, zum Betrachter. */
export function blickrichtung(v) {
  const [[a1, a2, a3], [b1, b2, b3]] = v.basis;
  return [a2 * b3 - a3 * b2, a3 * b1 - a1 * b3, a1 * b2 - a2 * b1];
}

/** Eine Richtung der Zeichnung im Bild, in px je Einheit -- y nach unten. */
export function richtungImBild(v, r) {
  const [rechts, oben] = v.basis || EBEN;
  return [v.massstab * skalar(r, rechts), -v.massstab * skalar(r, oben)];
}

/** Zoomt um `faktor` und hält dabei den Weltpunkt unter `bild` fest. */
export function zoomen(v, faktor, bild) {
  const neu = Math.min(v.grenzen[1], Math.max(v.grenzen[0], v.massstab * faktor));
  const f = neu / v.massstab;
  v.ursprung = [bild[0] - (bild[0] - v.ursprung[0]) * f, bild[1] - (bild[1] - v.ursprung[1]) * f];
  v.massstab = neu;
}

/**
 * Der Umriss `[[kleinste...], [grösste...]]` der Zeichnung, wie er im Bild
 * liegt: das Rechteck um die Bilder seiner Ecken, in Einheiten der
 * Zeichnung -- nach rechts und nach oben.
 */
function imBildUmriss(v, [klein, gross]) {
  if (!v.basis) return [klein, gross];
  const ecken = klein.reduce((liste, _, i) => liste.flatMap((e) => [[...e, klein[i]], [...e, gross[i]]]), [[]]);
  const [rechts, oben] = v.basis;
  const as = ecken.map((p) => skalar(p, rechts));
  const bs = ecken.map((p) => skalar(p, oben));
  return [[Math.min(...as), Math.min(...bs)], [Math.max(...as), Math.max(...bs)]];
}

/**
 * Passt den Umriss `[[kleinste...], [grösste...]]` ins Bild -- mit Rand für
 * Masslinien. `frei` hält zusätzlich einen Streifen frei, in px: `rechts`,
 * `oben` oder `unten`, dort, wo das schwebende Fenster steht.
 */
export function einpassen(v, umriss, { rand = 46, frei = {} } = {}) {
  if (!v.breite || !v.hoehe) return;
  const [[a0, b0], [a1, b1]] = imBildUmriss(v, umriss);
  const { rechts = 0, oben = 0, unten = 0 } = frei;
  const b = Math.max(a1 - a0, 1);
  const h = Math.max(b1 - b0, 1);
  const nutzbreite = Math.max(40, v.breite - 2 * rand - rechts);
  const nutzhoehe = Math.max(40, v.hoehe - 2 * rand - oben - unten);
  v.massstab = Math.min(v.grenzen[1], Math.max(v.grenzen[0], Math.min(nutzbreite / b, nutzhoehe / h)));
  v.ursprung = [
    rand + nutzbreite / 2 - v.massstab * (a0 + a1) / 2,
    oben + rand + nutzhoehe / 2 + v.massstab * (b0 + b1) / 2,
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
 * Wie weit zwei Rasterlinien auseinander stehen: das Raster mal 1, 2, 5,
 * 10, … -- so weit, dass sie im Bild nicht verschwimmen. `jeEinheit`: wie
 * viele Bildpunkte eine Einheit der Zeichnung dort lang ist.
 */
export function rasterschritt(raster, jeEinheit) {
  let schritt = raster;
  for (let i = 1; schritt * jeEinheit < 14 && i < 30; i += 1) {
    schritt = raster * [1, 2, 5][i % 3] * 10 ** Math.floor(i / 3);
  }
  return schritt;
}

/** Raster und Achsen, über das ganze Bild. */
export function rasterZeichnen(v, raster, [achse1, achse2]) {
  const g = svgEl('g', { class: 'cad-raster' });
  const schritt = rasterschritt(raster, v.massstab);
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
