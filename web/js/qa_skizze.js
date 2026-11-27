/**
 * qa_skizze.js -- ein kleines Bild aus Teilen des Kerns, mit Masslinien.
 *
 * Die Teile einer Vorlage -- Polygone, Stäbe, Stablinien samt ihren Stäben,
 * Schubwände, die Linie eines Profilblechs und Masslinien -- baut der Kern
 * (`opencivil/querschnitt/vorlagen.py`, `Teile`); hier werden sie nur
 * gezeichnet: im Fenster der Vorlagen (qa_vorlagen.js) und als Rippe einer
 * gewählten Blechverbunddecke (qa_blechdecke.js). Bis 2026-11-27 stand das in
 * qa_vorlagen.js.
 */

import { pfad } from './cad_ansicht.js';
import { svgEl } from './dom.js';

/** Alle Punkte der Teile -- für den Rahmen der Skizze. */
function punkteVon(teile) {
  return [
    ...teile.polygone.flatMap((p) => p.punkte),
    ...teile.staebe.map((s) => s.lage),
  ];
}

/** Eine Masslinie neben dem Bauteil, auf der Seite, die der Kern nennt. */
function masslinie(g, m, nach) {
  const ab = 12;
  const [dx, dy] = { unten: [0, ab], oben: [0, -ab], links: [-ab, 0], rechts: [ab, 0] }[m.seite] || [0, ab];
  const [x0, y0] = nach(m.von);
  const [x1, y1] = nach(m.bis);
  const [p, q] = [[x0 + dx, y0 + dy], [x1 + dx, y1 + dy]];
  const kurz = (x, y) => (dx ? `M${x - 3} ${y} H${x + 3}` : `M${x} ${y - 3} V${y + 3}`);
  g.append(svgEl('path', {
    d: `M${x0} ${y0} L${p[0]} ${p[1]} M${x1} ${y1} L${q[0]} ${q[1]} M${p[0]} ${p[1]} L${q[0]} ${q[1]} `
      + `${kurz(...p)} ${kurz(...q)}`,
    class: 'cad-mass',
  }));
  const [mx, my] = [(p[0] + q[0]) / 2, (p[1] + q[1]) / 2];
  const t = svgEl('text', { class: 'cad-masstext', 'text-anchor': 'middle' });
  t.textContent = m.text;
  if (dx) {
    const x = mx + (dx < 0 ? -4 : 11);
    t.setAttribute('x', x);
    t.setAttribute('y', my);
    t.setAttribute('transform', `rotate(-90 ${x} ${my})`);
  } else {
    t.setAttribute('x', mx);
    t.setAttribute('y', my + (dy > 0 ? 11 : -4));
  }
  g.append(t);
}

/**
 * Die Teile als kleines Bild, `breite` × `hoehe` px -- mit Masslinien, wenn
 * `masse`, sonst als Bildchen für einen Knopf. Die Flächen haben die Klasse
 * `flaeche`: die ihres Materials. Ein Stück -- ein Stahlprofil -- ist ein
 * Pfad, sein Loch gerade-ungerade ausgespart; sonst ist ein Loch eine
 * Aussparung, wie in der Zeichnung. Ein Profilblech liegt als Linie über
 * den Flächen.
 */
export function skizze(teile, breite, hoehe, { masse = true, flaeche = 'cad-beton', einStueck = false } = {}) {
  const bild = svgEl('svg', {
    viewBox: `0 0 ${breite} ${hoehe}`, width: breite, height: hoehe, class: 'cad-skizze',
  });
  const punkte = punkteVon(teile);
  if (!punkte.length) return bild;
  const ys = punkte.map((p) => p[0]);
  const zs = punkte.map((p) => p[1]);
  const [y0, y1, z0, z1] = [Math.min(...ys), Math.max(...ys), Math.min(...zs), Math.max(...zs)];
  const rand = masse ? 30 : 3;
  const s = Math.min((breite - 2 * rand) / Math.max(y1 - y0, 1), (hoehe - 2 * rand) / Math.max(z1 - z0, 1));
  const ox = (breite - s * (y1 - y0)) / 2 - s * y0;
  const oy = (hoehe + s * (z1 - z0)) / 2 + s * z0;
  const v = { massstab: s, ursprung: [ox, oy] };
  const nach = (p) => [ox + s * p[0], oy - s * p[1]];
  const g = svgEl('g');
  if (einStueck) {
    g.append(svgEl('path', {
      d: teile.polygone.map((p) => pfad(v, p.punkte)).join(' '), class: flaeche, 'fill-rule': 'evenodd',
    }));
  }
  for (const p of einStueck ? [] : teile.polygone) {
    g.append(svgEl('path', { d: pfad(v, p.punkte), class: p.aussparung ? 'cad-loch' : flaeche }));
  }
  for (const b of teile.bleche || []) g.append(svgEl('path', { d: pfad(v, b.punkte, false), class: 'cad-profilblech' }));
  for (const w of teile.schubwaende) {
    g.append(svgEl('path', {
      d: pfad(v, [w.von, w.bis], false), class: 'cad-skizze-wand',
      'stroke-width': Math.max(1, w.dicke * s).toFixed(1),
    }));
  }
  for (const l of teile.stablinien) g.append(svgEl('path', { d: pfad(v, [l.von, l.bis], false), class: 'cad-linie' }));
  for (const st of [...teile.staebe, ...(teile.stabmitten || [])]) {
    const [x, y] = nach(st.lage);
    g.append(svgEl('circle', { cx: x, cy: y, r: Math.max(1.5, (st.durchmesser * s) / 2), class: 'cad-stab' }));
  }
  if (masse) for (const m of teile.masslinien) masslinie(g, m, nach);
  bild.append(g);
  return bild;
}
