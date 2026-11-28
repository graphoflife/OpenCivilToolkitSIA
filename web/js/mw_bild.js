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
 * DIE URTEILE: jeder Pfeiler getönt in der Farbe des Urteils, das an ihm
 * gilt, mit Name und Erfüllungsgrad an seinem Fuss; unter jedem Auflager
 * eines Sturzes ein Strich in der Farbe des seinen -- grün erfüllt, rot
 * nicht, grau, wo sich der Nachweis nicht führen liess oder nichts
 * einwirkt (`urteile`, mauerwerkdaten.py).
 *
 * DIE LASTEN, nur im Zeichenfenster: die des gezeigten Lastfalls, eine
 * Linienlast als Pfeile über ihrer Linie, eine Punktlast als Pfeil auf ihren
 * Knoten, beide mit Wert und Ausmitte -- wie im Balkensystem (bs_symbole.js).
 * Schiebt eine Punktlast waagrecht, kommt ein Pfeil von der Seite dazu, mit H;
 * den lotrechten zeigt sie dann nur, wenn auch Q nicht null ist. Eine
 * Querlast wirkt quer zur Wand, man sieht sie von vorne: Kreise über die
 * ganze Wand, ausser auf Öffnungen und Stürzen -- mit Punkt, wo sie zum
 * Betrachter drückt, mit Kreuz, wo von ihm weg, wechselnd, wo sie in beiden
 * Richtungen wirkt wie die des Erdbebens. Ihre Werte stehen unter der Wand,
 * je Querlast eine Zeile, p_E vom Kern (`ersatzkraefte`): in der Wand
 * stünden sie auf den Graden der Stürze.
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

import { blickSymbol, kraftpfeil, streckenlast } from './bs_symbole.js';
import {
  ansichtNeu, einpassen, nachBild, pfad, text, zahlText,
} from './cad_ansicht.js';
import { mitTitel, umrissVon } from './cad_app.js';
import { el, svgEl } from './dom.js';

/** So weit stehen Schraffur und Gelenke von der Wand ab, in px. */
const RAND = { gelenk: 2.6, abstand: 6, schraffur: 5, teilung: 7, gelenke: 24 };

/**
 * So lang sind die Pfeile der Lasten, px -- länger als die Schraffur am Kopf,
 * die einer Punktlast so viel länger, dass ihre Beschriftung über der einer
 * Linienlast steht, nicht darin.
 */
export const PFEIL = { linie: 26, punkt: 52 };

/**
 * Wie die Querlasten stehen, px: die Kreise etwa `abstand` auseinander, in
 * jeder Richtung höchstens `je` -- weg von Öffnungen und Stürzen um `frei`;
 * ihre Zeilen ab `unten` unter dem Fuss, `zeile` hoch.
 */
const QUER = { abstand: 64, je: [12, 8], frei: 9, unten: 30, zeile: 18 };

/** So breit ist ein Zeichen der Urteile im Bild, px -- 11 px Schrift mit fester Breite. */
const ZEICHEN = 6.6;

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

/** Wert und Ausmitte einer Last, wie sie am Pfeil stehen: «q = 40 kN/m, e = 20 mm». */
function lasttext(zeichen, einheit, e) {
  return `${zeichen} = ${zahlText(e.wert, 1)} ${einheit}${e.e ? `, e = ${zahlText(e.e, 0)} mm` : ''}`;
}

/**
 * Die Lasten des Lastfalls `lastfall`, in m an den Knoten `lagen`: Pfeile
 * nach unten, für H zur Seite -- rot, was der Kern an einer beanstandet.
 */
function lasten(v, modell, lagen, lastfall, { fehler, texte }) {
  const g = svgEl('g', { class: 'mw-lasten' });
  const klasse = (kennung) => (fehler(kennung) ? 'bs-last ist-fehler' : 'bs-last');
  for (const e of (modell.linienlasten || []).filter((x) => x.lastfall === lastfall)) {
    const [p, q] = [lagen.get(e.von), lagen.get(e.bis)];
    if (!p || !q) continue;
    g.append(mitTitel(streckenlast(nachBild(v, p), nachBild(v, q), [0, 1], PFEIL.linie, PFEIL.linie,
      lasttext('q', 'kN/m', e), klasse(e.kennung)), [`Linienlast ${e.kennung}`, ...texte(e.kennung)]));
  }
  for (const e of (modell.punktlasten || []).filter((x) => x.lastfall === lastfall)) {
    const p = lagen.get(e.knoten);
    if (!p) continue;
    const [q, titel] = [nachBild(v, p), [`Punktlast ${e.kennung}`, ...texte(e.kennung)]];
    if (e.wert || !e.H) {
      g.append(mitTitel(kraftpfeil(q, [0, 1], PFEIL.punkt, lasttext('Q', 'kN', e), klasse(e.kennung)), titel));
    }
    if (e.H) {
      g.append(mitTitel(kraftpfeil(q, [Math.sign(e.H), 0], PFEIL.punkt, `H = ${zahlText(e.H, 1)} kN`,
        klasse(e.kennung)), titel));
    }
  }
  return g;
}

/**
 * Wohin eine Querlast drückt: `true` zum Betrachter, `false` von ihm weg,
 * `null` in beide Richtungen -- die des Erdbebens.
 */
const richtung = (q) => (q.art === 'erdbeben' ? null : q.wert >= 0);

/**
 * Die Querlasten des Lastfalls `lastfall` auf der Wand im Rahmen `r` (px)
 * -- siehe Dateikopf. `frei` sind die Rahmen, auf denen kein Kreis steht:
 * Öffnungen und Stürze.
 */
function querlasten(r, modell, lastfall, { frei, ersatzkraefte }) {
  const liste = (modell.querlasten || []).filter((q) => q.lastfall === lastfall);
  const g = svgEl('g', { class: 'mw-querlasten' });
  if (!liste.length) return g;
  const richtungen = new Set(liste.map(richtung));
  const zuMir = richtungen.size === 1 ? [...richtungen][0] : null;
  const [nx, ny] = [r.r - r.l, r.u - r.o].map((l, i) => Math.max(1, Math.min(QUER.je[i], Math.round(l / QUER.abstand))));
  const aufFrei = (x, y) => frei.some((f) => x > f.l - QUER.frei && x < f.r + QUER.frei
    && y > f.o - QUER.frei && y < f.u + QUER.frei);
  const raster = svgEl('g');
  for (let i = 0; i < nx; i += 1) {
    for (let j = 0; j < ny; j += 1) {
      const p = [r.l + ((i + 0.5) * (r.r - r.l)) / nx, r.o + ((j + 0.5) * (r.u - r.o)) / ny];
      if (!aufFrei(...p)) raster.append(blickSymbol(p, zuMir ?? (i + j) % 2 === 0, ''));
    }
  }
  g.append(mitTitel(raster, liste.map((q) => `Querlast ${q.kennung}`)));
  liste.forEach((q, k) => {
    const y = r.u + QUER.unten + k * QUER.zeile;
    const p = q.art === 'erdbeben' ? ersatzkraefte[q.kennung] : q.wert;
    const wert = q.art !== 'erdbeben' ? `p = ${zahlText(p, 2)} kN/m²`
      : `Erdbeben${p === undefined ? '' : `, p_E = ±${zahlText(p, 2)} kN/m²`}`;
    const zeichen = richtung(q) === null ? [true, false] : [richtung(q)];
    zeichen.forEach((z, n) => g.append(blickSymbol([r.l + 6 + n * 15, y], z, '')));
    g.append(text(r.l + 6 + zeichen.length * 15, y + 4, `Querlast ${q.kennung}: ${wert}`, 'bs-lasttext', 'start'));
  });
  return g;
}

/**
 * Die Urteile des Kerns, je Ort (`urteile`): die Pfeiler getönt, mit Name und
 * Grad an ihrem Fuss, und unter den Auflagern der Stürze je ein Strich --
 * von seinem Ende bis zur Kante der Öffnung, mit dem Grad darunter.
 */
function urteilsbild(v, { pfeiler, stuerze, urteile, oeffnungen, lagen }) {
  const g = svgEl('g', { class: 'mw-urteile' });
  for (const e of pfeiler) {
    const u = urteile[e.name];
    if (!u) continue;
    const ecken = [[e.x0, e.y0], [e.x1, e.y0], [e.x1, e.y1], [e.x0, e.y1]];
    g.append(mitTitel(svgEl('path', { d: pfad(v, ecken), class: `mw-urteil ist-${u.zustand}` }),
      [`Pfeiler ${e.name}`, u.titel]));
    const [a, b] = [nachBild(v, [e.x0, e.y0]), nachBild(v, [e.x1, e.y0])];
    // Ein schmaler Pfeiler nennt nur seinen Grad, sonst liefe er in den Nachbarn: der Name steht im Titel.
    const voll = u.grad ? `${e.name} · ${u.grad}` : e.name;
    const passt = voll.length * ZEICHEN <= Math.abs(b[0] - a[0]) - 4;
    g.append(text((a[0] + b[0]) / 2, a[1] - 6, passt ? voll : (u.grad || e.name), `mw-urteil-text ist-${u.zustand}`));
  }
  for (const s of stuerze) {
    const o = oeffnungen.find((x) => x.kennung === s.oeffnung);
    const ecken = o && eckenVon(lagen, o.knoten);
    if (!ecken) continue;
    const xs = ecken.map((p) => p[0]);
    for (const [seite, von, bis] of [['links', s.x0, Math.min(...xs)], ['rechts', Math.max(...xs), s.x1]]) {
      const u = urteile[`${s.oeffnung} ${seite}`];
      if (!u) continue;
      const [a, b] = [nachBild(v, [von, s.y0]), nachBild(v, [bis, s.y0])];
      g.append(mitTitel(svgEl('path', {
        d: `M${a[0].toFixed(1)} ${a[1].toFixed(1)} H${b[0].toFixed(1)}`, class: `mw-auflager ist-${u.zustand}`,
      }), [`Auflager ${s.oeffnung} ${seite}`, u.titel]));
      // Der Grad über dem Auflager, auf dem Mauerwerk über dem Sturz: darunter
      // verdeckten ihn die Öffnung und ihr Name.
      const oben = nachBild(v, [von, s.y1])[1] - 3;
      if (u.grad) g.append(text((a[0] + b[0]) / 2, oben, u.grad, `mw-urteil-text ist-klein ist-${u.zustand}`));
    }
  }
  return g;
}

/**
 * Die ganze Wand: ihre Fläche, die Öffnungen ausgespart, die Urteile, die
 * Stürze, die Umrisse, die Ränder, die Lasten und die Namen -- auf der Karte
 * auch die Masse der Pfeiler. `fehler(kennung)` und `texte(kennung)` sagen,
 * was der Kern an einem Teil meldet -- rot, und als Titel beim
 * Darüberfahren. `stuerze`, `pfeiler` und `urteile` sind die des Kerns;
 * `alt`, wenn sie zu einer früheren Zeichnung gehören -- dann stehen sie
 * blass. `stellungen` sind die Wörter der Schalter (`katalog.mauerwerk`),
 * `lastfall` der Lastfall, dessen Lasten zu sehen sind -- ohne einen keine;
 * `ersatzkraefte` je Querlast des Erdbebens ihr p_E vom Kern; `masse`, ob
 * unter der Wand die Masse der Pfeiler stehen.
 */
export function wand(v, modell, {
  fehler = () => false, texte = () => [], stuerze = [], pfeiler = [], urteile = {}, alt = false, stellungen = {},
  lastfall = null, ersatzkraefte = {}, masse = false,
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
  const urteilsgruppe = urteilsbild(v, { pfeiler, stuerze, urteile, oeffnungen: modell.oeffnungen || [], lagen });
  if (alt) urteilsgruppe.classList.add('ist-alt');
  g.append(flaechen, urteilsgruppe, oeffnungen, stuerzeGruppe, umrisse);
  if (waende.length === 1) {
    const r = rahmen(v, waende[0][1]);
    g.append(raender(r, modell, stellungen));
    if (masse && pfeiler.length) g.append(pfeilermasse(v, pfeiler, r.u + 26));
    if (lastfall) {
      const frei = [
        ...(modell.oeffnungen || []).map((o) => eckenVon(lagen, o.knoten)).filter(Boolean),
        ...stuerze.map((s) => [[s.x0, s.y0], [s.x1, s.y1]]),
      ].map((punkte) => rahmen(v, punkte));
      g.append(querlasten(r, modell, lastfall, { frei, ersatzkraefte }));
    }
  }
  if (lastfall) g.append(lasten(v, modell, lagen, lastfall, { fehler, texte }));
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
  svg.append(wand(v, modell, {
    stuerze: daten?.stuerze || [], pfeiler: daten?.pfeiler || [], urteile: daten?.urteile || {}, stellungen,
    masse: true,
  }));
  return svg;
}

/** Was die Stürze, die Farben der Urteile und die Ränder im Bild heissen -- unter ihm. */
export function wandLegende(stellungen) {
  const probe = (inhalt, wort) => {
    const svg = svgEl('svg', { viewBox: '0 0 26 14', width: 26, height: 14, 'aria-hidden': 'true' });
    svg.append(inhalt);
    return el('span.dk-legende-eintrag', {}, [svg, wort]);
  };
  const sturz = (art) => probe(svgEl('rect', { x: 1, y: 3, width: 24, height: 8, class: `mw-sturz ist-${art}` }),
    `Sturz: ${wortVon(stellungen.sturz, art)}`);
  const urteil = (zustand, wort) => probe(svgEl('rect', {
    x: 1, y: 2, width: 24, height: 10, class: `mw-urteil ist-${zustand}`,
  }), wort);
  return el('div.dk-legende', {}, [
    sturz('beton'), sturz('vorfabriziert'),
    urteil('erfuellt', 'erfüllt'), urteil('verfehlt', 'nicht erfüllt'),
    urteil('offen', 'nicht geführt oder ohne Einwirkung'),
    probe(kante([1, 4], [25, 4], [0, 1], false), wortVon(stellungen.halterung, 'eingespannt')),
    probe(kante([1, 2], [25, 2], [0, 1], true),
      `${wortVon(stellungen.halterung, 'gelenkig')} oder ${wortVon(stellungen.seitenrand, 'gehalten')}`),
  ]);
}
