/**
 * bs_symbole.js -- die Zeichen eines Balkensystems im Bild.
 *
 * Lager und Federn, Gelenke, Linienlager, die gestrichelte Faser und die
 * Lasten -- eben und im Raum. Gezeichnet wird in Bildpunkten: ein Lager ist
 * gleich gross, wie weit man auch zoomt -- nur seine Lage kommt aus der
 * Zeichnung. Die Länge eines Lastpfeils folgt seinem Wert, im Verhältnis zur
 * grössten Last derselben Art im Bild; das ist Darstellung und geht in keine
 * Rechnung ein.
 *
 * RICHTUNGEN IM BILD:
 * Jedes Zeichen bekommt seine Richtungen schon im Bild, als Einheitsvektor
 * (y nach unten): die Seite der gestrichelten Faser, die eines
 * Linienlagers, die eines Pfeils. Wie eine Richtung der Zeichnung ins Bild
 * fällt, sagt die Ansicht (cad_ansicht.js) -- in der Ebene liegt die Faser
 * rechts der Laufrichtung, im Raum dort, wohin z des Stabs zeigt. Zeigt
 * eine Kraft fast auf den Betrachter zu oder von ihm weg, ist sie ein Kreis
 * mit Punkt oder Kreuz (`blickSymbol`); ein Moment im Raum ist ein Pfeil mit
 * zwei Spitzen (`momentpfeil`), von vorne gesehen ein Bogen. Welches Zeichen
 * eine Richtung bekommt, entscheiden `imBild`, `kraft` und `moment` -- für
 * das Zeichenfenster und die Diagramme dieselben.
 *
 * TREFFEN:
 * Ein Lastzeichen trägt seine Formen im Bild mit (`formen` an der Gruppe):
 * das Band einer verteilten Last, den Schaft eines Pfeils, den Bogen eines
 * Moments. Daran wählt das Zeichenfenster eine Last -- die Formen stehen
 * dort, wo das Zeichen entsteht, und nicht ein zweites Mal im Adapter.
 */

import { blickrichtung, richtungImBild, text } from './cad_ansicht.js';
import { skalar } from './cad_modell.js';
import { svgEl } from './dom.js';

/** Wie gross die Zeichen sind, in Bildpunkten. */
export const GROESSE = {
  lager: 13,        // Höhe des Dreiecks
  gelenk: 3.6,      // Radius des Gelenkkreises
  gelenkAbstand: 9, // wie weit vom Knoten entlang des Stabs
  faser: 4,         // Abstand der gestrichelten Faser vom Stab
  pfeil: 44,        // Länge des längsten Lastpfeils
  moment: 13,       // Radius eines Momentbogens
  momentpfeil: 30,  // Länge eines Momentpfeils im Raum
  blick: 6,         // Radius einer Kraft, die man von vorne sieht
};

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
 * Ein Lager in der Ebene am Bildpunkt `p`: je Richtung frei, fest oder Feder (`halt`
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

/**
 * Ein Lager im Raum am Bildpunkt `p`: ein Dreieck unter dem Knoten -- in
 * Richtung `unten`, der Richtung −z im Bild (Einheitsvektor). Hält jede
 * Verschiebung, steht es auf schraffiertem Grund, ist eine frei, auf Rollen,
 * federt eine, auf einer Feder. Hält eine Drehung, liegt ein Riegel darüber,
 * federt eine, ein Bogen; hält alles, ist es eingespannt: ein Balken mit
 * Schraffur. `halt` = {schieben, drehen}, je eine Liste mit 'frei' | 'fest'
 * | 'feder'. Was je Richtung gilt, sagt der Titel des Zeichens.
 */
export function raumlagerSymbol(p, { schieben, drehen }, unten, klasse = '') {
  const g = svgEl('g', { class: `bs-lager ${klasse}` });
  const h = GROESSE.lager;
  const quer = [-unten[1], unten[0]];
  const auf = (s, t = 0) => [p[0] + unten[0] * s + quer[0] * t, p[1] + unten[1] * s + quer[1] * t];
  const alle = (liste, wert) => liste.every((x) => x === wert);
  if (alle([...schieben, ...drehen], 'fest')) {
    schraffur(g, auf(0, -h), auf(0, h), unten);
    g.append(linie(auf(0, -h), auf(0, h), 'bs-einspannung'));
    return g;
  }
  g.append(pfadAus([p, auf(h, -h * 0.7), auf(h, h * 0.7)], 'bs-dreieck', true));
  if (alle(schieben, 'fest')) {
    schraffur(g, auf(h, -h), auf(h, h), unten);
  } else if (schieben.includes('feder')) {
    g.append(feder(auf(h), auf(h + 14)));
    schraffur(g, auf(h + 14, -h * 0.7), auf(h + 14, h * 0.7), unten);
  } else {
    g.append(linie(auf(h + 3, -h), auf(h + 3, h), 'bs-boden'));
    schraffur(g, auf(h + 3, -h), auf(h + 3, h), unten);
  }
  if (drehen.includes('fest')) {
    g.append(linie(auf(-4, -h * 0.8), auf(-4, h * 0.8), 'bs-einspannung'));
  } else if (drehen.includes('feder')) {
    const r = 9;
    const [a, b] = [auf(0, r), auf(-r)];
    g.append(svgEl('path', { d: `M${a[0].toFixed(1)} ${a[1].toFixed(1)} A${r} ${r} 0 1 1 ${b[0].toFixed(1)} ${b[1].toFixed(1)}`, class: 'bs-feder' }));
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

/** Die gestrichelte Faser: knapp neben dem Stab, auf der Seite `n` (Einheitsvektor im Bild). */
export function faserSymbol(p, q, n, klasse = '') {
  const l = Math.hypot(q[0] - p[0], q[1] - p[1]);
  if (l < 24) return null;
  const t = [(q[0] - p[0]) / l, (q[1] - p[1]) / l];
  const f = GROESSE.faser;
  const rand = Math.min(14, l * 0.15);
  return linie(
    [p[0] + t[0] * rand + n[0] * f, p[1] + t[1] * rand + n[1] * f],
    [q[0] - t[0] * rand + n[0] * f, q[1] - t[1] * rand + n[1] * f], `bs-faser ${klasse}`);
}

/**
 * Ein Linienlager neben dem Stab: quer fest eine schraffierte Linie auf
 * seiner Seite, quer federnd ein Band aus Federn (Bettung); längs fest
 * kurze Querstriche an der Linie, längs federnd kleine Federn. `quer` ist
 * eine Liste `{halt, n}`: je Richtung quer, wie sie hält, und ihre Seite im
 * Bild (Einheitsvektor) -- in der Ebene eine, zur gestrichelten Faser, im
 * Raum zwei, in y und z des Stabs.
 */
export function linienlagerSymbol(p, q, quer, laengs, klasse = '') {
  const g = svgEl('g', { class: `bs-linienlager ${klasse}` });
  const l = Math.hypot(q[0] - p[0], q[1] - p[1]);
  if (l < 8) return g;
  const t = [(q[0] - p[0]) / l, (q[1] - p[1]) / l];
  const ab = 9;
  for (const { halt, n } of quer) {
    if (halt === 'fest') {
      schraffur(g, [p[0] + n[0] * ab, p[1] + n[1] * ab], [q[0] + n[0] * ab, q[1] + n[1] * ab], n);
    } else if (halt === 'feder') {
      const anzahl = Math.max(2, Math.min(24, Math.round(l / 22)));
      for (let i = 0; i < anzahl; i += 1) {
        const s = ((i + 0.5) * l) / anzahl;
        const a = [p[0] + t[0] * s, p[1] + t[1] * s];
        g.append(feder([a[0] + n[0] * 2, a[1] + n[1] * 2], [a[0] + n[0] * 16, a[1] + n[1] * 16]));
      }
      g.append(linie([p[0] + n[0] * 16, p[1] + n[1] * 16], [q[0] + n[0] * 16, q[1] + n[1] * 16], 'bs-boden'));
    }
  }
  if (laengs === 'fest' || laengs === 'feder') {
    // Auf der Seite gegenüber der ersten Richtung quer.
    const n = quer[0]?.n || [-t[1], t[0]];
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

/**
 * Ein Moment im Raum an `p`: ein Pfeil mit zwei Spitzen in Richtung `r`
 * (Einheitsvektor im Bild), vom Punkt weg -- es dreht im Rechtssinn um ihn.
 */
export function momentpfeil(p, r, beschriftung, klasse = 'bs-last') {
  const g = svgEl('g');
  const l = GROESSE.momentpfeil;
  const ende = [p[0] + r[0] * l, p[1] + r[1] * l];
  const zweite = [ende[0] - r[0] * 6, ende[1] - r[1] * 6];
  g.append(linie(p, ende, `${klasse} bs-momentpfeil`), spitze(ende, r, klasse), spitze(zweite, r, klasse));
  // Getroffen wird der Schaft ab etwas Abstand vom Punkt: dort liegt der Knoten oder Stab.
  g.formen = [{ art: 'strecke', von: [p[0] + r[0] * 9, p[1] + r[1] * 9], bis: ende }];
  if (beschriftung) {
    g.append(text(ende[0] + r[0] * 5 + (Math.abs(r[0]) < 0.5 ? 6 : 0),
      ende[1] + r[1] * 5 + (Math.abs(r[1]) < 0.5 ? -5 : 4), beschriftung,
      `bs-lasttext ${klasse}`, Math.abs(r[0]) < 0.5 ? 'start' : (r[0] > 0 ? 'start' : 'end')));
  }
  return g;
}

/**
 * Eine Kraft, die man von vorne sieht: ein Kreis um `p`, mit einem Punkt,
 * wenn sie auf den Betrachter zu zeigt, mit einem Kreuz, wenn von ihm weg.
 */
export function blickSymbol(p, zuMir, beschriftung, klasse = 'bs-last') {
  const g = svgEl('g');
  const r = GROESSE.blick;
  const [x, y] = p;
  g.append(svgEl('circle', { cx: x.toFixed(1), cy: y.toFixed(1), r, class: `${klasse} bs-blick` }));
  if (zuMir) {
    g.append(svgEl('circle', { cx: x.toFixed(1), cy: y.toFixed(1), r: 1.6, class: `${klasse} bs-spitze` }));
  } else {
    const k = r * 0.62;
    g.append(svgEl('path', {
      d: `M${(x - k).toFixed(1)} ${(y - k).toFixed(1)} L${(x + k).toFixed(1)} ${(y + k).toFixed(1)} M${(x - k).toFixed(1)} ${(y + k).toFixed(1)} L${(x + k).toFixed(1)} ${(y - k).toFixed(1)}`,
      class: `${klasse} bs-lastpfeil`,
    }));
  }
  if (beschriftung) g.append(text(x + r + 4, y - r - 2, beschriftung, `bs-lasttext ${klasse}`, 'start'));
  g.formen = [{ art: 'bogen', mitte: p, r: r / 2 }];
  return g;
}

/**
 * Eine Reihe gleicher Zeichen entlang der Strecke von `a` nach `b`, etwa
 * alle `abstand` Bildpunkte, höchstens `hoechstens`: ein verteiltes
 * Moment, eine verteilte Last, die man von vorne sieht. `zeichen(p,
 * beschriftung)` baut eines; die Beschriftung trägt das mittlere.
 */
export function reihe(a, b, abstand, zeichen, beschriftung, hoechstens = 8) {
  const g = svgEl('g');
  const l = Math.hypot(b[0] - a[0], b[1] - a[1]);
  const anzahl = Math.max(1, Math.min(hoechstens, Math.round(l / abstand)));
  const teile = [];
  for (let i = 0; i < anzahl; i += 1) {
    const s = (i + 0.5) / anzahl;
    teile.push(zeichen([a[0] + (b[0] - a[0]) * s, a[1] + (b[1] - a[1]) * s],
      i === Math.floor(anzahl / 2) ? beschriftung : ''));
  }
  g.append(...teile);
  g.formen = teile.flatMap((x) => x.formen);
  return g;
}

/** Ein verteiltes Moment: kleine Bögen entlang der Strecke. */
export function streckenmoment(a, b, wert, beschriftung, klasse = 'bs-last') {
  return reihe(a, b, 40, (p, t) => momentSymbol(p, wert, t, `${klasse} bs-klein`), beschriftung);
}

// ===========================================================================
// Richtungen der Zeichnung im Bild
// ===========================================================================

/** Ab welchem Anteil ihrer Länge eine Richtung im Bild ein Pfeil ist -- darunter sieht man sie von vorne. */
const SICHTBAR = 0.35;

/** In der Ebene dreht ein Moment um die Achse, die auf den Betrachter zeigt -- im Bild ein Bogen. */
const ZUM_BETRACHTER = { f: 0, zuMir: true };

/**
 * Eine Richtung der Zeichnung im Bild der Ansicht `v` (cad_ansicht.js): als
 * Einheitsvektor (`r`), wie lang sie dort erscheint, 0 bis 1 (`f`), und ob
 * sie auf den Betrachter zu zeigt (`zuMir`). In der Ebene liegt jede
 * Richtung ganz im Bild. Das Zeichenfenster und die Diagramme zeichnen
 * damit ihre Kräfte und Momente.
 */
export function imBild(v, richtung) {
  const [x, y] = richtungImBild(v, richtung).map((w) => w / v.massstab);
  const f = Math.hypot(x, y);
  return {
    r: f > 1e-9 ? [x / f, y / f] : [0, 1], f,
    zuMir: Boolean(v.basis) && skalar(richtung, blickrichtung(v)) > 0,
  };
}

/**
 * Eine Kraft an `p`: ein Pfeil in ihrer Richtung `d` (wie `imBild`), dessen
 * Spitze `p` berührt -- ein negativer Wert zeigt entgegen --, oder, sieht
 * man sie von vorne, ein Kreis.
 */
export function kraft(p, d, wert, laenge, beschriftung, klasse) {
  if (d.f < SICHTBAR) return blickSymbol(p, (wert >= 0) === d.zuMir, beschriftung, klasse);
  return kraftpfeil(p, wert >= 0 ? d.r : [-d.r[0], -d.r[1]], laenge, beschriftung, klasse);
}

/** Eine verteilte Kraft von `p` nach `q`: ein Pfeilband -- oder, von vorne, eine Reihe Kreise. */
export function kraftband(p, q, d, la, lb, beschriftung, klasse) {
  if (d.f < SICHTBAR) {
    return reihe(p, q, 26, (o, t) => blickSymbol(o, (la + lb >= 0) === d.zuMir, t, klasse), beschriftung, 12);
  }
  return streckenlast(p, q, d.r, la, lb, beschriftung, klasse);
}

/**
 * Ein Moment an `p` um die Achse `achse` der Ansicht `v` (in der Ebene
 * null): ein Pfeil mit zwei Spitzen -- sieht man die Achse von vorne, ein
 * Bogen, im Drehsinn, den man sieht.
 */
export function moment(v, p, achse, wert, beschriftung, klasse) {
  const d = achse ? imBild(v, achse) : ZUM_BETRACHTER;
  if (d.f < SICHTBAR) return momentSymbol(p, d.zuMir ? wert : -wert, beschriftung, klasse);
  return momentpfeil(p, wert >= 0 ? d.r : [-d.r[0], -d.r[1]], beschriftung, klasse);
}

/** Ein verteiltes Moment von `p` nach `q`, wie `moment` je Zeichen. */
export function momentband(v, p, q, achse, wert, beschriftung, klasse = 'bs-last') {
  const d = achse ? imBild(v, achse) : ZUM_BETRACHTER;
  if (d.f < SICHTBAR) return streckenmoment(p, q, d.zuMir ? wert : -wert, beschriftung, klasse);
  const r = wert >= 0 ? d.r : [-d.r[0], -d.r[1]];
  return reihe(p, q, 40, (o, t) => momentpfeil(o, r, t, `${klasse} bs-klein`), beschriftung);
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
