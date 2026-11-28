/**
 * mw_bild.js -- eine Wand aus Mauerwerk, gezeichnet.
 *
 * Was eine Wand im Bild zeigt, im Zeichenfenster wie auf ihrer Karte im
 * Reiter «Diagramme»: die Wand hell mit kräftigem Rand, die Öffnungen
 * ausgespart, über jeder ihr Sturz -- wie weit er aufliegt, sagt der Kern
 * (`stuerze`, mauerwerkdaten.py) --, und an den Rändern, wie die Wand
 * gehalten ist. Beide Bilder rufen dieselbe Funktion, jedes mit seiner
 * Ansicht `v` (cad_ansicht.js).
 *
 * ZEICHEN DER RÄNDER, ausserhalb der Wand, um den Rahmen ihres Umrisses:
 *   eingespannt   Kopf oder Fuss: eine Kante mit Schraffur, an der die Wand sitzt
 *   gelenkig      dieselbe Kante, etwas abgerückt, dazwischen Gelenke
 *   gehalten      links oder rechts: eine Kante mit Gelenken -- eine Querwand
 *   frei          nichts
 *
 * DIE PFEILER, nur auf der Karte: unter der Wand je ein Mass von Öffnung zu
 * Öffnung, mit Name und Breite -- wie der Kern sie bestimmt (`pfeiler`).
 *
 * Gerechnet wird hier nichts: nur Lagen fürs Auge -- wo ein Zeichen steht,
 * wie weit die Gelenke auseinander.
 */

import {
  ansichtNeu, einpassen, nachBild, pfad, text, zahlText,
} from './cad_ansicht.js';
import { mitTitel, umrissVon } from './cad_app.js';
import { el, svgEl } from './dom.js';

/** So weit stehen Schraffur und Gelenke von der Wand ab, in px. */
const RAND = { gelenk: 2.6, abstand: 6, schraffur: 5, teilung: 7, gelenke: 24 };

/** Die Ecken eines Umrisses, in m -- null, wenn einer seiner Knoten fehlt. */
function eckenVon(lagen, knoten) {
  const punkte = knoten.map((k) => lagen.get(k));
  return punkte.some((p) => !p) || punkte.length < 3 ? null : punkte;
}

/** Der Rahmen um Punkte im Bild: links, rechts, oben, unten -- px. */
function rahmen(v, punkte) {
  const bild = punkte.map((p) => nachBild(v, p));
  const xs = bild.map((p) => p[0]);
  const ys = bild.map((p) => p[1]);
  return { l: Math.min(...xs), r: Math.max(...xs), o: Math.min(...ys), u: Math.max(...ys) };
}

/**
 * Eine gehaltene Kante von `p` nach `q` (px), aussen in der Richtung `n`:
 * eine Linie mit Schraffur dahinter -- gelenkig etwas abgerückt, mit
 * Gelenken zwischen ihr und der Wand.
 */
function kante(p, q, n, gelenkig) {
  const g = svgEl('g', { class: 'mw-rand' });
  const ab = gelenkig ? RAND.abstand : 0;
  const [a, b] = [p, q].map(([x, y]) => [x + n[0] * ab, y + n[1] * ab]);
  const laenge = Math.hypot(b[0] - a[0], b[1] - a[1]);
  if (laenge < 1) return g;
  const t = [(b[0] - a[0]) / laenge, (b[1] - a[1]) / laenge];
  const punkt = ([x, y]) => `${x.toFixed(1)} ${y.toFixed(1)}`;
  const d = [`M${punkt(a)} L${punkt(b)}`];
  for (let s = RAND.teilung / 2; s <= laenge; s += RAND.teilung) {
    const fuss = [a[0] + t[0] * s, a[1] + t[1] * s];
    const ende = [fuss[0] + n[0] * RAND.schraffur - t[0] * 4, fuss[1] + n[1] * RAND.schraffur - t[1] * 4];
    d.push(`M${punkt(fuss)} L${punkt(ende)}`);
  }
  g.append(svgEl('path', { d: d.join(' '), class: 'mw-rand-linie' }));
  if (gelenkig) {
    const anzahl = Math.max(2, Math.round(laenge / RAND.gelenke));
    for (let i = 0; i < anzahl; i += 1) {
      const s = ((i + 0.5) * laenge) / anzahl;
      g.append(svgEl('circle', {
        cx: (p[0] + t[0] * s + n[0] * (ab / 2)).toFixed(1), cy: (p[1] + t[1] * s + n[1] * (ab / 2)).toFixed(1),
        r: RAND.gelenk, class: 'mw-gelenk',
      }));
    }
  }
  return g;
}

/** Wie die Ränder heissen, in Worten des Kerns -- für den Titel beim Darüberfahren. */
const wortVon = (stellungen, wert) => stellungen?.find((s) => s.wert === wert)?.beschriftung ?? wert;

/**
 * Die Ränder um den Rahmen `r` (px): Kopf und Fuss gehalten, gelenkig oder
 * eingespannt, links und rechts nur, wenn sie gehalten sind.
 */
function raender(r, wand, stellungen) {
  const g = svgEl('g', { class: 'mw-raender' });
  const halt = (name, p, q, n, gelenkig) => g.append(mitTitel(kante(p, q, n, gelenkig), [name]));
  for (const [seite, y, n] of [['kopf', r.o, [0, -1]], ['fuss', r.u, [0, 1]]]) {
    halt(`${seite === 'kopf' ? 'Kopf' : 'Fuss'} ${wortVon(stellungen.halterung, wand[seite])}`,
      [r.l, y], [r.r, y], n, wand[seite] !== 'eingespannt');
  }
  for (const [seite, x, n] of [['links', r.l, [-1, 0]], ['rechts', r.r, [1, 0]]]) {
    if (wand[seite] === 'gehalten') {
      halt(`${seite === 'links' ? 'Links' : 'Rechts'} ${wortVon(stellungen.seitenrand, 'gehalten')}`,
        [x, r.o], [x, r.u], n, true);
    }
  }
  return g;
}

/**
 * Je Pfeiler ein Mass unter der Wand, `y` px unter ihrem Fuss: von Rand zu
 * Rand, dazu Name und Breite.
 */
function pfeilermasse(v, pfeiler, y) {
  const g = svgEl('g', { class: 'mw-pfeiler' });
  for (const e of pfeiler) {
    const [x0] = nachBild(v, [e.x0, 0]);
    const [x1] = nachBild(v, [e.x1, 0]);
    g.append(mitTitel(svgEl('path', {
      d: `M${x0.toFixed(1)} ${y.toFixed(1)} H${x1.toFixed(1)} M${x0.toFixed(1)} ${(y - 4).toFixed(1)} v8 `
        + `M${x1.toFixed(1)} ${(y - 4).toFixed(1)} v8`,
      class: 'mw-mass',
    }), [`Pfeiler ${e.name}: b = ${zahlText(e.b, 2)} m`]));
    g.append(text((x0 + x1) / 2, y + 12, `${e.name} · ${zahlText(e.b, 2)} m`, 'dk-name ist-pfeiler'));
  }
  return g;
}

/**
 * Die ganze Wand: ihre Fläche, die Öffnungen ausgespart, die Stürze, die
 * Umrisse, die Ränder und die Namen -- auf der Karte auch die Pfeiler.
 * `fehler(kennung)` und `texte(kennung)` sagen, was der Kern an einem Teil
 * meldet -- rot, und als Titel beim Darüberfahren. `stuerze` und `pfeiler`
 * sind die des Kerns; `alt`, wenn sie zu einer früheren Zeichnung gehören --
 * dann stehen sie blass. `stellungen` sind die Wörter der Schalter
 * (`katalog.mauerwerk`).
 */
export function wand(v, modell, {
  fehler = () => false, texte = () => [], stuerze = [], pfeiler = [], alt = false, stellungen = {},
} = {}) {
  const g = svgEl('g', { class: 'mw-modell' });
  const lagen = new Map((modell.knoten || []).map((k) => [k.kennung, [k.x, k.y]]));
  const klasse = (grund, kennung) => (fehler(kennung) ? `${grund} ist-fehler` : grund);
  const flaechen = svgEl('g');
  const umrisse = svgEl('g');
  const namen = svgEl('g', { class: 'dk-namen' });
  const name = (punkte, kennung) => {
    const oben = punkte.reduce((a, b) => (nachBild(v, b)[1] < nachBild(v, a)[1] ? b : a));
    const [x, y] = nachBild(v, oben);
    namen.append(text(x + 4, y + 11, kennung, 'dk-name ist-klein'));
  };
  const waende = (modell.waende || []).map((w) => [w, eckenVon(lagen, w.knoten)]).filter(([, p]) => p);
  for (const [w, punkte] of waende) {
    flaechen.append(svgEl('path', { d: pfad(v, punkte), class: 'mw-wand-flaeche' }));
    umrisse.append(mitTitel(svgEl('path', { d: pfad(v, punkte), class: klasse('mw-wand', w.kennung) }),
      [`Wand ${w.kennung}`, ...texte(w.kennung)]));
    name(punkte, w.kennung);
  }
  const oeffnungen = svgEl('g');
  for (const o of modell.oeffnungen || []) {
    const punkte = eckenVon(lagen, o.knoten);
    if (!punkte) continue;
    oeffnungen.append(svgEl('path', { d: pfad(v, punkte), class: 'mw-oeffnung-flaeche' }));
    umrisse.append(mitTitel(svgEl('path', { d: pfad(v, punkte), class: klasse('mw-oeffnung', o.kennung) }),
      [`Öffnung ${o.kennung}`, ...texte(o.kennung)]));
    name(punkte, o.kennung);
  }
  const stuerzeGruppe = svgEl('g', { class: alt ? 'mw-stuerze ist-alt' : 'mw-stuerze' });
  for (const s of stuerze) {
    const o = (modell.oeffnungen || []).find((x) => x.kennung === s.oeffnung);
    const ecken = [[s.x0, s.y0], [s.x1, s.y0], [s.x1, s.y1], [s.x0, s.y1]];
    stuerzeGruppe.append(mitTitel(svgEl('path', { d: pfad(v, ecken), class: `mw-sturz ist-${s.sturz}` }), [
      `Sturz über ${s.oeffnung}: ${wortVon(stellungen.sturz, s.sturz)}`
        + (o ? `, h_St = ${zahlText(o.h_St, 0)} mm, a = ${zahlText(o.a, 0)} mm` : ''),
    ]));
  }
  g.append(flaechen, oeffnungen, stuerzeGruppe, umrisse);
  if (waende.length === 1) {
    const r = rahmen(v, waende[0][1]);
    g.append(raender(r, modell, stellungen));
    if (pfeiler.length) g.append(pfeilermasse(v, pfeiler, r.u + 26));
  }
  g.append(namen);
  return g;
}

/** So breit ist ein Bild auf seiner Karte, und so hoch höchstens und mindestens -- px. */
const BILD = { breite: 720, hoehe: [240, 520], rand: 56 };

/** Die Wand als Bild, fest im Massstab -- mit Rand für die Ränder und die Masse der Pfeiler. */
export function wandBild(modell, daten, stellungen) {
  const umriss = umrissVon((modell.knoten || []).map((k) => [k.x, k.y]), [[0, 0], [6, 3]]);
  const [[x0, y0], [x1, y1]] = umriss;
  const breit = Math.max(x1 - x0, 1);
  const hoch = Math.max(y1 - y0, 1);
  const hoehe = Math.min(BILD.hoehe[1], Math.max(BILD.hoehe[0],
    (hoch / breit) * (BILD.breite - 2 * BILD.rand) + 2 * BILD.rand));
  const v = ansichtNeu([1e-3, 1e5]);
  Object.assign(v, { breite: BILD.breite, hoehe });
  einpassen(v, umriss, { rand: BILD.rand });
  const svg = svgEl('svg', { viewBox: `0 0 ${BILD.breite} ${hoehe.toFixed(0)}`, class: 'gb-bild mw-bild' });
  svg.append(wand(v, modell, { stuerze: daten?.stuerze || [], pfeiler: daten?.pfeiler || [], stellungen }));
  return svg;
}

/** Was die Stürze und die Ränder im Bild heissen -- unter ihm. */
export function wandLegende(stellungen) {
  const probe = (inhalt, wort) => {
    const svg = svgEl('svg', { viewBox: '0 0 26 14', width: 26, height: 14, 'aria-hidden': 'true' });
    svg.append(inhalt);
    return el('span.dk-legende-eintrag', {}, [svg, wort]);
  };
  const sturz = (art) => probe(svgEl('rect', { x: 1, y: 3, width: 24, height: 8, class: `mw-sturz ist-${art}` }),
    `Sturz: ${wortVon(stellungen.sturz, art)}`);
  return el('div.dk-legende', {}, [
    sturz('beton'), sturz('vorfabriziert'),
    probe(kante([1, 4], [25, 4], [0, 1], false), wortVon(stellungen.halterung, 'eingespannt')),
    probe(kante([1, 2], [25, 2], [0, 1], true),
      `${wortVon(stellungen.halterung, 'gelenkig')} oder ${wortVon(stellungen.seitenrand, 'gehalten')}`),
  ]);
}
