/**
 * bs_symbole.js -- die Zeichen eines Balkensystems im Bild.
 *
 * Lager und Federn, Gelenke, Linienlager, die gestrichelte Faser und die
 * Lasten. Gezeichnet wird in Bildpunkten: ein Lager ist gleich gross, wie
 * weit man auch zoomt -- nur seine Lage kommt aus der Zeichnung. Die Länge
 * eines Lastpfeils folgt seinem Wert, im Verhältnis zur grössten Last
 * derselben Art im Bild; das ist Darstellung und geht in keine Rechnung ein.
 *
 * RICHTUNGEN IM BILD:
 * Das Bild hat y nach unten, die Zeichnung z nach oben: eine Richtung
 * (dx, dz) der Zeichnung ist im Bild (dx, −dz) -- `imBild`. Die gestrichelte
 * Faser liegt rechts der Laufrichtung eines Stabs: in der Zeichnung bei
 * (s, −c), im Bild bei (−t_y, t_x) für seine Laufrichtung t im Bild. Dorthin
 * zeigt auch eine Last «quer», und dort liegt ein Linienlager.
 *
 * TREFFEN:
 * Ein Lastzeichen trägt seine Formen im Bild mit (`formen` an der Gruppe):
 * das Band einer verteilten Last, den Schaft eines Pfeils, den Bogen eines
 * Moments. Daran wählt das Zeichenfenster eine Last -- die Formen stehen
 * dort, wo das Zeichen entsteht, und nicht ein zweites Mal im Adapter.
 */

import { text } from './cad_ansicht.js';
import { svgEl } from './dom.js';

/** Wie gross die Zeichen sind, in Bildpunkten. */
export const GROESSE = {
  lager: 13,        // Höhe des Dreiecks
  gelenk: 3.6,      // Radius des Gelenkkreises
  gelenkAbstand: 9, // wie weit vom Knoten entlang des Stabs
  faser: 4,         // Abstand der gestrichelten Faser vom Stab
  pfeil: 44,        // Länge des längsten Lastpfeils
  moment: 13,       // Radius eines Momentbogens
};

/** Eine Richtung der Zeichnung (x nach rechts, z nach oben) im Bild. */
export const imBild = ([dx, dz]) => [dx, -dz];

function linie(p, q, klasse) {
  return svgEl('path', { d: `M${p[0].toFixed(1)} ${p[1].toFixed(1)} L${q[0].toFixed(1)} ${q[1].toFixed(1)}`, class: klasse });
}

function pfadAus(punkte, klasse, zu = false) {
  const d = punkte.map((p, i) => `${i ? 'L' : 'M'}${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(' ') + (zu ? ' Z' : '');
  return svgEl('path', { d, class: klasse });
}

/** Eine Schraffur unter einer Grundlinie von p nach q, auf der Seite `n` (Einheitsvektor im Bild). */
function schraffur(g, p, q, n, klasse = 'bs-boden') {
  g.append(linie(p, q, klasse));
  const l = Math.hypot(q[0] - p[0], q[1] - p[1]) || 1;
  const t = [(q[0] - p[0]) / l, (q[1] - p[1]) / l];
  for (let s = 3; s < l; s += 5) {
    const a = [p[0] + t[0] * s, p[1] + t[1] * s];
    const b = [a[0] + n[0] * 5 - t[0] * 4, a[1] + n[1] * 5 - t[1] * 4];
    g.append(linie(a, b, 'bs-schraffur'));
  }
}

/** Eine Feder von p nach q, als Zickzack. */
function feder(p, q, klasse = 'bs-feder') {
  const l = Math.hypot(q[0] - p[0], q[1] - p[1]) || 1;
  const t = [(q[0] - p[0]) / l, (q[1] - p[1]) / l];
  const n = [-t[1], t[0]];
  const punkte = [p, [p[0] + t[0] * 3, p[1] + t[1] * 3]];
  const zacken = 6;
  for (let i = 0; i < zacken; i += 1) {
    const s = 3 + ((l - 6) * (i + 0.5)) / zacken;
    const seite = i % 2 ? -1 : 1;
    punkte.push([p[0] + t[0] * s + n[0] * 3.5 * seite, p[1] + t[1] * s + n[1] * 3.5 * seite]);
  }
  punkte.push([q[0] - t[0] * 3, q[1] - t[1] * 3], q);
  return pfadAus(punkte, klasse);
}

/**
 * Ein Lager am Bildpunkt `p`: je Richtung frei, fest oder Feder (`halt`
 * = {x, z, phi} mit 'frei' | 'fest' | 'feder'). Fest in x und z ein
 * Dreieck auf schraffiertem Grund, nur in z ein Dreieck auf Rollen, nur in
 * x dasselbe von der Seite; eingespannt ein Balken mit Schraffur. Eine
 * Feder statt fest zeichnet die Feder in ihrer Richtung, eine Drehfeder
 * einen Bogen.
 */
export function lagerSymbol(p, halt, klasse = '') {
  const g = svgEl('g', { class: `bs-lager ${klasse}` });
  const h = GROESSE.lager;
  const [x, y] = p;
  const fest = (r) => halt[r] === 'fest';
  const federnd = (r) => halt[r] === 'feder';
  if (fest('x') && fest('z') && fest('phi')) {
    schraffur(g, [x - h, y], [x + h, y], [0, 1]);
    g.append(linie([x - h, y], [x + h, y], 'bs-einspannung'));
    return g;
  }
  // Das Dreieck steht unter dem Knoten, wenn z hält -- sonst seitlich.
  const unten = fest('z') || federnd('z') || !(fest('x') || federnd('x'));
  if (unten) {
    const basis = y + h;
    g.append(pfadAus([[x, y], [x - h * 0.7, basis], [x + h * 0.7, basis]], 'bs-dreieck', true));
    if (federnd('z')) {
      g.append(feder([x, basis], [x, basis + 14]));
      schraffur(g, [x - h * 0.7, basis + 14], [x + h * 0.7, basis + 14], [0, 1]);
    } else if (fest('x')) {
      schraffur(g, [x - h, basis], [x + h, basis], [0, 1]);
    } else {
      // Verschieblich: auf Rollen, eine zweite Linie darunter.
      g.append(linie([x - h, basis + 3], [x + h, basis + 3], 'bs-boden'));
      schraffur(g, [x - h, basis + 3], [x + h, basis + 3], [0, 1]);
    }
    if (federnd('x')) g.append(feder([x - h - 16, y], [x, y]), linie([x - h - 16, y - 6], [x - h - 16, y + 6], 'bs-boden'));
  } else {
    // Hält nur in x: das Dreieck liegt links, die Rollen senkrecht.
    const basis = x - h;
    g.append(pfadAus([[x, y], [basis, y - h * 0.7], [basis, y + h * 0.7]], 'bs-dreieck', true));
    if (federnd('x')) {
      g.append(feder([basis, y], [basis - 14, y]));
      schraffur(g, [basis - 14, y - h * 0.7], [basis - 14, y + h * 0.7], [-1, 0]);
    } else {
      g.append(linie([basis - 3, y - h], [basis - 3, y + h], 'bs-boden'));
      schraffur(g, [basis - 3, y - h], [basis - 3, y + h], [-1, 0]);
    }
  }
  if (fest('phi')) {
    // Eingespannt gegen Drehen, aber verschieblich: ein Riegel über dem Dreieck.
    g.append(linie([x - h * 0.8, y - 4], [x + h * 0.8, y - 4], 'bs-einspannung'));
  } else if (federnd('phi')) {
    const r = 9;
    g.append(svgEl('path', { d: `M${x + r} ${y} A${r} ${r} 0 1 1 ${x} ${y - r}`, class: 'bs-feder' }));
  }
  return g;
}

/** Ein Gelenk am Stabende: ein offener Kreis kurz vor dem Knoten, in Richtung `t` (Einheitsvektor im Bild, vom Knoten weg). */
export function gelenkSymbol(p, t, klasse = '') {
  const a = GROESSE.gelenkAbstand;
  return svgEl('circle', {
    cx: (p[0] + t[0] * a).toFixed(1), cy: (p[1] + t[1] * a).toFixed(1),
    r: GROESSE.gelenk, class: `bs-gelenk ${klasse}`,
  });
}

/** Die gestrichelte Faser: rechts der Laufrichtung, knapp neben dem Stab. */
export function faserSymbol(p, q, klasse = '') {
  const l = Math.hypot(q[0] - p[0], q[1] - p[1]);
  if (l < 24) return null;
  const t = [(q[0] - p[0]) / l, (q[1] - p[1]) / l];
  // Im Bild ist y unten: rechts der Laufrichtung ist (−t_y, t_x).
  const n = [-t[1], t[0]];
  const f = GROESSE.faser;
  const rand = Math.min(14, l * 0.15);
  return linie(
    [p[0] + t[0] * rand + n[0] * f, p[1] + t[1] * rand + n[1] * f],
    [q[0] - t[0] * rand + n[0] * f, q[1] - t[1] * rand + n[1] * f], `bs-faser ${klasse}`);
}

/**
 * Ein Linienlager neben dem Stab: quer fest eine schraffierte Linie auf der
 * Seite der gestrichelten Faser, quer federnd ein Band aus Federn (Bettung);
 * längs fest kurze Querstriche an der Linie, längs federnd kleine Federn.
 */
export function linienlagerSymbol(p, q, quer, laengs, klasse = '') {
  const g = svgEl('g', { class: `bs-linienlager ${klasse}` });
  const l = Math.hypot(q[0] - p[0], q[1] - p[1]);
  if (l < 8) return g;
  const t = [(q[0] - p[0]) / l, (q[1] - p[1]) / l];
  const n = [-t[1], t[0]];
  const ab = 9;
  if (quer === 'fest') {
    schraffur(g, [p[0] + n[0] * ab, p[1] + n[1] * ab], [q[0] + n[0] * ab, q[1] + n[1] * ab], n);
  } else if (quer === 'feder') {
    const anzahl = Math.max(2, Math.min(24, Math.round(l / 22)));
    for (let i = 0; i < anzahl; i += 1) {
      const s = ((i + 0.5) * l) / anzahl;
      const a = [p[0] + t[0] * s, p[1] + t[1] * s];
      g.append(feder([a[0] + n[0] * 2, a[1] + n[1] * 2], [a[0] + n[0] * 16, a[1] + n[1] * 16]));
    }
    g.append(linie([p[0] + n[0] * 16, p[1] + n[1] * 16], [q[0] + n[0] * 16, q[1] + n[1] * 16], 'bs-boden'));
  }
  if (laengs === 'fest' || laengs === 'feder') {
    const anzahl = Math.max(2, Math.min(16, Math.round(l / 30)));
    for (let i = 0; i < anzahl; i += 1) {
      const s = ((i + 0.5) * l) / anzahl;
      const a = [p[0] + t[0] * s - n[0] * 3, p[1] + t[1] * s - n[1] * 3];
      if (laengs === 'fest') g.append(linie([a[0] - t[0] * 4, a[1] - t[1] * 4], [a[0] + t[0] * 4, a[1] + t[1] * 4], 'bs-laengslager'));
      else g.append(feder([a[0] - t[0] * 6, a[1] - t[1] * 6], [a[0] + t[0] * 6, a[1] + t[1] * 6], 'bs-feder bs-laengslager'));
    }
  }
  return g;
}

/** Eine Pfeilspitze an `q`, aus Richtung `t` kommend. */
function spitze(q, t, klasse) {
  const n = [-t[1], t[0]];
  const a = [q[0] - t[0] * 7 + n[0] * 3.5, q[1] - t[1] * 7 + n[1] * 3.5];
  const b = [q[0] - t[0] * 7 - n[0] * 3.5, q[1] - t[1] * 7 - n[1] * 3.5];
  return pfadAus([q, a, b], `${klasse} bs-spitze`, true);
}

/**
 * Eine Kraft, die an `p` angreift: ein Pfeil in Richtung `r` (Einheitsvektor
 * im Bild), dessen Spitze `p` berührt, `laenge` Bildpunkte lang -- mit dem
 * Wert am Schaft.
 */
export function kraftpfeil(p, r, laenge, beschriftung, klasse = 'bs-last') {
  const g = svgEl('g');
  const anfang = [p[0] - r[0] * laenge, p[1] - r[1] * laenge];
  g.append(linie(anfang, p, klasse), spitze(p, r, klasse));
  // Getroffen wird der Schaft, nicht die Spitze: dort liegt der Knoten oder Stab.
  g.formen = [{ art: 'strecke', von: anfang, bis: [p[0] - r[0] * 7, p[1] - r[1] * 7] }];
  if (beschriftung) {
    g.append(text(anfang[0] - r[0] * 4 + (Math.abs(r[0]) < 0.5 ? 6 : 0),
      anfang[1] - r[1] * 4 + (Math.abs(r[1]) < 0.5 ? -5 : 4), beschriftung,
      `bs-lasttext ${klasse}`, Math.abs(r[0]) < 0.5 ? 'start' : (r[0] > 0 ? 'end' : 'start')));
  }
  return g;
}

/**
 * Ein Moment an `p`: ein Bogen um den Punkt, die Spitze im Drehsinn --
 * positiv im Gegenuhrzeigersinn, wie in der Zeichnung.
 */
export function momentSymbol(p, wert, beschriftung, klasse = 'bs-last') {
  const g = svgEl('g');
  const r = GROESSE.moment;
  const [x, y] = p;
  // Von rechts unten über oben nach links unten -- im Bild y nach unten.
  const a0 = (-30 * Math.PI) / 180;
  const a1 = (210 * Math.PI) / 180;
  const punkt = (w) => [x + r * Math.cos(w), y - r * Math.sin(w)];
  const [s, e] = wert >= 0 ? [punkt(a0), punkt(a1)] : [punkt(a1), punkt(a0)];
  g.append(svgEl('path', {
    d: `M${s[0].toFixed(1)} ${s[1].toFixed(1)} A${r} ${r} 0 1 ${wert >= 0 ? 0 : 1} ${e[0].toFixed(1)} ${e[1].toFixed(1)}`,
    class: `${klasse} bs-bogen`,
  }));
  // Die Spitze tangential am Ende des Bogens.
  const w = wert >= 0 ? a1 : a0;
  const tangente = wert >= 0 ? [Math.sin(w), Math.cos(w)] : [-Math.sin(w), -Math.cos(w)];
  g.append(spitze(e, tangente, klasse));
  if (beschriftung) g.append(text(x, y - r - 5, beschriftung, `bs-lasttext ${klasse}`));
  g.formen = [{ art: 'bogen', mitte: p, r }];
  return g;
}

/**
 * Eine verteilte Last zwischen den Bildpunkten `a` und `b`: Pfeile in
 * Richtung `r`, deren Spitzen die Linie berühren, und die Umrisslinie über
 * ihren Enden. `la` und `lb` sind die Pfeillängen an beiden Enden -- mit
 * Vorzeichen: negativ zeigt der Pfeil entgegen `r`.
 */
export function streckenlast(a, b, r, la, lb, beschriftung, klasse = 'bs-last') {
  const g = svgEl('g');
  const l = Math.hypot(b[0] - a[0], b[1] - a[1]);
  const anzahl = Math.max(2, Math.min(18, Math.round(l / 18)));
  const ende = (p, laenge) => [p[0] - r[0] * laenge, p[1] - r[1] * laenge];
  const umriss = [];
  for (let i = 0; i <= anzahl; i += 1) {
    const s = i / anzahl;
    const p = [a[0] + (b[0] - a[0]) * s, a[1] + (b[1] - a[1]) * s];
    const laenge = la + (lb - la) * s;
    umriss.push(ende(p, laenge));
    if (Math.abs(laenge) < 6) continue;
    const richtung = laenge > 0 ? r : [-r[0], -r[1]];
    g.append(linie(ende(p, laenge), p, `${klasse} bs-lastpfeil`), spitze(p, richtung, klasse));
  }
  g.append(pfadAus(umriss, `${klasse} bs-umriss`));
  g.append(linie(a, umriss[0], `${klasse} bs-lastpfeil`), linie(b, umriss[umriss.length - 1], `${klasse} bs-lastpfeil`));
  // Getroffen wird das Band zwischen der Linie und den Enden der Pfeile.
  g.formen = [{ art: 'band', linie: [a, b], punkte: [a, b, umriss[umriss.length - 1], umriss[0]] }];
  if (beschriftung) {
    const mitte = umriss[Math.floor(umriss.length / 2)];
    g.append(text(mitte[0] - r[0] * 6, mitte[1] - r[1] * 6 + (Math.abs(r[1]) > 0.5 ? (r[1] > 0 ? -2 : 10) : 4),
      beschriftung, `bs-lasttext ${klasse}`));
  }
  return g;
}

/** Ein verteiltes Moment: kleine Bögen entlang der Strecke. */
export function streckenmoment(a, b, wert, beschriftung, klasse = 'bs-last') {
  const g = svgEl('g');
  const l = Math.hypot(b[0] - a[0], b[1] - a[1]);
  const anzahl = Math.max(1, Math.min(8, Math.round(l / 40)));
  const boegen = [];
  for (let i = 0; i < anzahl; i += 1) {
    const s = (i + 0.5) / anzahl;
    boegen.push(momentSymbol([a[0] + (b[0] - a[0]) * s, a[1] + (b[1] - a[1]) * s], wert,
      i === Math.floor(anzahl / 2) ? beschriftung : '', `${klasse} bs-klein`));
  }
  g.append(...boegen);
  g.formen = boegen.flatMap((x) => x.formen);
  return g;
}

/** Ein Knoten, dessen Drehung keine Steifigkeit hat: ein Ring mit Fragezeichen. */
export function unbestimmtSymbol(p, titel) {
  const g = svgEl('g', { class: 'bs-unbestimmt' });
  g.append(svgEl('circle', { cx: p[0], cy: p[1], r: 7 }), text(p[0] + 10, p[1] - 8, '?', 'bs-unbestimmt-text', 'start'));
  const t = svgEl('title');
  t.textContent = titel;
  g.append(t);
  return g;
}
