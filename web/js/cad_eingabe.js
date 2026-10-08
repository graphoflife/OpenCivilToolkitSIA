/**
 * cad_eingabe.js -- wie ein Punkt entsteht. Für jeden Befehl dieselbe Mechanik.
 *
 * Ob ein Knoten gesetzt, eine Linie gezogen oder etwas verschoben wird: jeder
 * Punkt kommt auf denselben Wegen zustande.
 *
 *   Maus       fängt an Knoten □, Linienmitte △, Schnittpunkt ×, am Lot ⊥
 *              vom Bezugspunkt auf eine Linie, auf der Linie ◇, sonst am
 *              Raster +. Alt gedrückt: nicht fangen.
 *   R          setzt den Bezugspunkt auf den gefangenen Punkt. Nach jedem
 *              gesetzten Punkt springt er von selbst dorthin.
 *   Ziffern    gehen ins schwebende Fenster: relativ zum Bezugspunkt,
 *              absolut, oder Länge und Winkel. Enter setzt den Punkt genau
 *              dorthin -- getippte Werte werden nicht gefangen.
 *   Y / Z      binden an die Achse durch den Bezugspunkt (die Buchstaben
 *              kommen von der App). Getippt wird dann nur der Abstand.
 *   P / S      parallel oder senkrecht: danach eine Linie anklicken. Die
 *              Bindung läuft durch den Bezugspunkt; ein gefangener Punkt wird
 *              auf sie projiziert.
 *   M          die Mitte zweier Punkte. Mit einer Bindung: auf sie projiziert.
 *   Esc        nimmt zuerst das Warten zurück, dann die Bindung, dann das
 *              Getippte -- erst danach geht es an den Befehl.
 *
 * Gelesen wird die Taste selbst (`e.key`), nicht ihre Lage: auf der
 * Schweizer Tastatur liegen Y und Z vertauscht.
 *
 * Das ist Eingabehilfe, keine Rechnung: in die Rechnung geht nur der Punkt,
 * der am Ende dasteht.
 */

import { nachBild, nachWelt } from './cad_ansicht.js';
import {
  abstand, aufGerade, aufStrecke, rund, schnitt,
} from './cad_modell.js';
import { svgEl } from './dom.js';

/** Wie nah der Zeiger an etwas sein muss, um es zu fangen oder zu treffen -- px. */
export const NAEHE = 9;

export function eingabeNeu() {
  return {
    bezug: null,         // [a, b] -- Bezugspunkt für Getipptes und Bindungen
    bindung: null,       // {art: 'achse'|'parallel'|'senkrecht', r: [da, db], text}
    warten: null,        // 'parallel' | 'senkrecht' | {art: 'mitte', erster}
    modus: 'rel',        // 'rel' | 'abs' | 'polar'
    felder: ['', ''],    // was getippt ist
    runde: 0,            // zählt mit, wenn die Felder geleert werden -- dann neu bauen
  };
}

/** Leert die Felder -- auch die im schwebenden Fenster, das daran sieht, dass `runde` weiterzählt. */
export function felderLeeren(pe) {
  pe.felder = ['', ''];
  pe.runde += 1;
}

/** Alles Vorläufige weg -- etwa nach einem fertigen Befehl. Der Bezugspunkt bleibt. */
export function eingabeLeeren(pe) {
  pe.bindung = null;
  pe.warten = null;
  felderLeeren(pe);
}

// ===========================================================================
// Was es zu fangen gibt
// ===========================================================================

/**
 * Die Ziele des Fangens -- je Stand der Zeichnung einmal gesammelt:
 * Knoten, Strecken (Linien und Kanten der Flächen), deren Mitten und die
 * Schnittpunkte der Strecken.
 */
export function ziele(a) {
  if (a.zielcache?.version === a.version) return a.zielcache;
  const z = a.adapter.zeichnung();
  const m = a.modell;
  const lagen = m.lagen(z);
  const knoten = (z.knoten || []).map((k) => ({ kennung: k.kennung, p: m.lage(k) }));
  const strecken = [];
  for (const { art, e } of m.elemente(z)) {
    if (art.form === 'linie') {
      const s = lagen.get(e.von);
      const t = lagen.get(e.bis);
      if (s && t) strecken.push({ s, e: t, quelle: e.kennung, art });
    } else if (art.form === 'flaeche') {
      const punkte = e.knoten.map((k) => lagen.get(k));
      if (punkte.some((p) => !p)) continue;
      punkte.forEach((p, i) => strecken.push({
        s: p, e: punkte[(i + 1) % punkte.length], quelle: e.kennung, kante: i, art,
      }));
    }
  }
  const mitten = strecken.map((st) => ({ p: [(st.s[0] + st.e[0]) / 2, (st.s[1] + st.e[1]) / 2], st }));
  const schnitte = [];
  for (let i = 0; i < strecken.length; i += 1) {
    for (let j = i + 1; j < strecken.length; j += 1) {
      const p = schnitt([strecken[i].s, strecken[i].e], [strecken[j].s, strecken[j].e]);
      // Gemeinsame Enden sind Knoten, keine Schnittpunkte.
      if (p && ![strecken[i].s, strecken[i].e].some((q) => abstand(p, q) < 1e-6)) {
        schnitte.push({ p });
      }
    }
  }
  a.zielcache = {
    version: a.version, knoten, strecken, mitten, schnitte,
    extra: a.adapter.fangpunkte?.(a) || [],
  };
  return a.zielcache;
}

// ===========================================================================
// Fangen
// ===========================================================================

const ras = (w, r) => Math.round(w / r) * r;

/** Die Gerade der Bindung: durch den Bezugspunkt, in ihrer Richtung. */
function bindungsgerade(pe) {
  if (!pe.bindung) return null;
  return { durch: pe.bezug || [0, 0], r: pe.bindung.r };
}

/**
 * Wohin der Zeiger fängt -- `{p, art, knoten?}`. Mit einer Bindung liegt
 * das Ergebnis immer auf ihr: ein gefangener Punkt wird auf sie projiziert,
 * sonst der Abstand ab dem Bezugspunkt ans Raster gerundet.
 */
export function fangen(a, bild, { frei = false, gerade = false } = {}) {
  const v = a.v;
  const pe = a.eingabe;
  let welt = nachWelt(v, bild);
  const weit = NAEHE / v.massstab;
  const ohneFang = frei || !a.fang;
  let linie = bindungsgerade(pe);

  // Shift: waagrecht oder senkrecht zum Bezugspunkt, solange gedrückt.
  if (!linie && gerade && pe.bezug) {
    const waagrecht = Math.abs(welt[0] - pe.bezug[0]) >= Math.abs(welt[1] - pe.bezug[1]);
    linie = { durch: pe.bezug, r: waagrecht ? [1, 0] : [0, 1] };
  }

  const z = ohneFang ? null : ziele(a);
  const naechster = (liste, art) => {
    let bester = null;
    for (const x of liste) {
      const d = abstand(welt, x.p);
      if (d <= weit && (!bester || d < bester.d)) bester = { ...x, d, art };
    }
    return bester;
  };

  if (linie) {
    // Was in der Nähe gefangen wird, wandert auf die Bindung.
    const punkt = z && (naechster(z.knoten, 'knoten')
      || naechster([...z.mitten, ...z.schnitte, ...z.extra], 'punkt'));
    if (punkt) return { p: aufGerade(punkt.p, linie.durch, linie.r), art: 'projiziert', von: punkt.p };
    const fuss = aufGerade(welt, linie.durch, linie.r);
    if (ohneFang) return { p: fuss, art: 'frei' };
    // Der Abstand ab dem Bezugspunkt aufs Raster.
    const l = Math.hypot(linie.r[0], linie.r[1]) || 1;
    const t = ((fuss[0] - linie.durch[0]) * linie.r[0] + (fuss[1] - linie.durch[1]) * linie.r[1]) / l;
    const tr = ras(t, a.raster);
    return { p: [linie.durch[0] + (tr * linie.r[0]) / l, linie.durch[1] + (tr * linie.r[1]) / l], art: 'raster' };
  }

  if (ohneFang) return { p: welt, art: 'frei' };

  const knoten = naechster(z.knoten, 'knoten');
  if (knoten) return { p: knoten.p, art: 'knoten', knoten: knoten.kennung };
  const punkt = naechster([...z.schnitte.map((x) => ({ ...x, art2: 'schnitt' })),
    ...z.mitten.map((x) => ({ ...x, art2: 'mitte' })), ...z.extra.map((x) => ({ ...x, art2: 'punkt' }))], 'punkt');
  if (punkt) return { p: punkt.p, art: punkt.art2 };

  // Das Lot vom Bezugspunkt auf eine Strecke -- nur, wo sein Fuss auf ihr liegt.
  if (pe.bezug) {
    let lot = null;
    for (const st of z.strecken) {
      const r = [st.e[0] - st.s[0], st.e[1] - st.s[1]];
      const l2 = r[0] * r[0] + r[1] * r[1];
      if (!l2) continue;
      const t = ((pe.bezug[0] - st.s[0]) * r[0] + (pe.bezug[1] - st.s[1]) * r[1]) / l2;
      if (t <= 1e-9 || t >= 1 - 1e-9) continue;
      const fuss = [st.s[0] + t * r[0], st.s[1] + t * r[1]];
      const d = abstand(welt, fuss);
      if (d <= weit && abstand(fuss, pe.bezug) > 1e-9 && (!lot || d < lot.d)) lot = { p: fuss, d };
    }
    if (lot) return { p: lot.p, art: 'lot' };
  }

  let bester = null;
  for (const st of z.strecken) {
    const { q } = aufStrecke(welt, st.s, st.e);
    const d = abstand(welt, q);
    if (d > weit * 0.8 || (bester && d >= bester.d)) continue;
    // Auf einer waagrechten oder senkrechten Strecke darf die freie Richtung
    // ans Raster -- der Punkt bleibt trotzdem genau auf ihr.
    let p = q;
    if (Math.abs(st.e[1] - st.s[1]) < 1e-9) p = [ras(q[0], a.raster), st.s[1]];
    else if (Math.abs(st.e[0] - st.s[0]) < 1e-9) p = [st.s[0], ras(q[1], a.raster)];
    if (abstand(aufStrecke(p, st.s, st.e).q, p) > 1e-9) p = q;
    bester = { p, d, art: 'linie' };
  }
  if (bester) return { p: bester.p, art: 'linie' };
  welt = [ras(welt[0], a.raster), ras(welt[1], a.raster)];
  return { p: welt, art: 'raster' };
}

/** Die Strecke unter dem Zeiger -- für P und S, und um eine Kante zu treffen. */
function streckeAn(a, bild) {
  const welt = nachWelt(a.v, bild);
  const weit = NAEHE / a.v.massstab;
  let bester = null;
  for (const st of ziele(a).strecken) {
    const d = abstand(welt, aufStrecke(welt, st.s, st.e).q);
    if (d <= weit && (!bester || d < bester.d)) bester = { ...st, d };
  }
  return bester;
}

// ===========================================================================
// Der Punkt, den ein Klick oder Enter liefert
// ===========================================================================

/**
 * Ein Klick: der gefangene Punkt -- oder ein Schritt der Hilfen (eine Linie
 * für P/S, ein Punkt der Mitte). Gibt den fertigen Punkt zurück, sonst null.
 */
export function klickPunkt(a, bild, e) {
  const pe = a.eingabe;
  if (pe.warten === 'parallel' || pe.warten === 'senkrecht') {
    const st = streckeAn(a, bild);
    if (!st) return null;
    let r = [st.e[0] - st.s[0], st.e[1] - st.s[1]];
    if (pe.warten === 'senkrecht') r = [-r[1], r[0]];
    pe.bindung = {
      art: pe.warten, r,
      text: `${pe.warten === 'parallel' ? '∥' : '⊥'} ${a.adapter.name(a, st.quelle) || st.quelle}`,
    };
    pe.warten = null;
    return null;
  }
  const f = fangen(a, bild, { frei: e.altKey, gerade: e.shiftKey });
  if (pe.warten?.art === 'mitte') {
    if (!pe.warten.erster) {
      pe.warten.erster = f.p;
      return null;
    }
    const q = pe.warten.erster;
    let m = [(q[0] + f.p[0]) / 2, (q[1] + f.p[1]) / 2];
    const g = bindungsgerade(pe);
    if (g) m = aufGerade(m, g.durch, g.r);
    pe.warten = null;
    return { p: m.map(rund), art: 'mitte' };
  }
  return { p: f.p.map(rund), art: f.art, knoten: f.knoten };
}

/** Eine getippte Zahl -- leer heisst null, Komma gilt als Punkt. */
function zahl(text) {
  const t = String(text ?? '').trim().replace(',', '.');
  if (t === '' || t === '-') return null;
  const w = Number(t);
  return Number.isFinite(w) ? w : NaN;
}

/**
 * Der getippte Punkt -- oder null, wenn nichts dasteht. Leere Felder sind
 * null, absolut: wie der Bezugspunkt. Ein Feld, das keine Zahl ist, ergibt
 * `{fehler}`.
 */
export function getipptPunkt(a) {
  const pe = a.eingabe;
  const [u, w] = pe.felder.map(zahl);
  if (u === null && w === null) return null;
  if (Number.isNaN(u) || Number.isNaN(w)) return { fehler: 'Das ist keine Zahl.' };
  const bezug = pe.bezug || [0, 0];
  const g = bindungsgerade(pe);
  if (g) {
    // Mit einer Bindung gibt es nur den Abstand entlang.
    const l = Math.hypot(g.r[0], g.r[1]) || 1;
    const t = u ?? 0;
    return { p: [bezug[0] + (t * g.r[0]) / l, bezug[1] + (t * g.r[1]) / l].map(rund), art: 'getippt' };
  }
  if (pe.modus === 'abs') return { p: [u ?? bezug[0], w ?? bezug[1]].map(rund), art: 'getippt' };
  if (pe.modus === 'polar') {
    const l = u ?? 0;
    const winkel = ((w ?? 0) * Math.PI) / 180;
    return { p: [bezug[0] + l * Math.cos(winkel), bezug[1] + l * Math.sin(winkel)].map(rund), art: 'getippt' };
  }
  return { p: [bezug[0] + (u ?? 0), bezug[1] + (w ?? 0)].map(rund), art: 'getippt' };
}

/** Was die Felder gerade heissen -- je nach Modus und Bindung. */
export function feldnamen(a) {
  const [x, y] = a.adapter.achsen;
  if (a.eingabe.bindung) return ['Abstand', null];
  return {
    rel: [`Δ${x}`, `Δ${y}`], abs: [x, y], polar: ['L', 'α°'],
  }[a.eingabe.modus];
}

// ===========================================================================
// Tasten
// ===========================================================================

/**
 * Eine Taste während einer Punkteingabe. Gibt zurück, ob sie hier etwas
 * bewirkt hat -- sonst gehört sie dem Befehl oder dem Fenster.
 */
export function taste(a, e) {
  const pe = a.eingabe;
  const k = e.key.length === 1 ? e.key.toLowerCase() : e.key;
  const [achse1, achse2] = a.adapter.achsen.map((x) => x.toLowerCase());
  const anBezug = () => {
    if (!pe.bezug && a.zeiger?.fang) pe.bezug = a.zeiger.fang.p.map(rund);
  };
  switch (k) {
    case 'r':
      if (!a.zeiger?.fang) return false;
      pe.bezug = a.zeiger.fang.p.map(rund);
      return true;
    case 'm':
      pe.warten = { art: 'mitte', erster: null };
      return true;
    case achse1:
    case achse2: {
      const r = k === achse1 ? [1, 0] : [0, 1];
      if (pe.bindung?.art === 'achse' && pe.bindung.r[0] === r[0]) {
        pe.bindung = null;
      } else {
        anBezug();
        pe.bindung = { art: 'achse', r, text: `entlang ${k === achse1 ? a.adapter.achsen[0] : a.adapter.achsen[1]}` };
      }
      felderLeeren(pe);
      return true;
    }
    case 'p':
    case 's':
      anBezug();
      pe.warten = k === 'p' ? 'parallel' : 'senkrecht';
      return true;
    case 'Escape':
      if (pe.warten) { pe.warten = null; return true; }
      if (pe.bindung) { pe.bindung = null; return true; }
      if (pe.felder.some((x) => x !== '')) { felderLeeren(pe); return true; }
      return false;
    default:
      return false;
  }
}

/** Was die Hilfen gerade sagen -- für die Frage im schwebenden Fenster. */
export function hilfstext(a) {
  const w = a.eingabe.warten;
  if (w === 'parallel') return 'Linie anklicken, zu der parallel.';
  if (w === 'senkrecht') return 'Linie anklicken, zu der senkrecht.';
  if (w?.art === 'mitte') return w.erster ? 'Zweiten Punkt der Mitte klicken.' : 'Ersten Punkt der Mitte klicken.';
  return '';
}

// ===========================================================================
// Zeichnen: Fangzeichen, Bezugspunkt, Bindung
// ===========================================================================

const ZEICHEN = {
  knoten: (x, y) => svgEl('rect', { x: x - 5, y: y - 5, width: 10, height: 10, class: 'cad-fang' }),
  mitte: (x, y) => svgEl('path', { d: `M${x} ${y - 6} L${x + 6} ${y + 5} L${x - 6} ${y + 5} Z`, class: 'cad-fang' }),
  schnitt: (x, y) => svgEl('path', { d: `M${x - 5} ${y - 5} L${x + 5} ${y + 5} M${x + 5} ${y - 5} L${x - 5} ${y + 5}`, class: 'cad-fang' }),
  linie: (x, y) => svgEl('path', { d: `M${x} ${y - 6} L${x + 6} ${y} L${x} ${y + 6} L${x - 6} ${y} Z`, class: 'cad-fang' }),
  lot: (x, y) => svgEl('path', { d: `M${x - 6} ${y + 5} H${x + 6} M${x} ${y + 5} V${y - 6}`, class: 'cad-fang' }),
  projiziert: (x, y) => svgEl('path', { d: `M${x - 6} ${y} H${x + 6} M${x} ${y - 6} V${y} M${x - 6} ${y - 6} V${y}`, class: 'cad-fang' }),
  punkt: (x, y) => svgEl('circle', { cx: x, cy: y, r: 5, class: 'cad-fang' }),
  raster: (x, y) => svgEl('path', { d: `M${x - 5} ${y} H${x + 5} M${x} ${y - 5} V${y + 5}`, class: 'cad-fang' }),
};

/** Die Hilfen ins obere Bild: Fangzeichen, Bezugspunkt, Bindung, Mitte. */
export function hilfenZeichnen(a, g) {
  const v = a.v;
  const pe = a.eingabe;
  if (pe.bindung) {
    const durch = nachBild(v, pe.bezug || [0, 0]);
    const r = pe.bindung.r;
    const l = Math.hypot(r[0], -r[1]) || 1;
    const lang = Math.hypot(v.breite, v.hoehe);
    const [dx, dy] = [(r[0] / l) * lang, (-r[1] / l) * lang];
    g.append(svgEl('path', {
      d: `M${durch[0] - dx} ${durch[1] - dy} L${durch[0] + dx} ${durch[1] + dy}`, class: 'cad-bindung',
    }));
  }
  if (pe.bezug && a.befehl) {
    const [x, y] = nachBild(v, pe.bezug);
    g.append(svgEl('path', { d: `M${x - 7} ${y - 7} L${x + 7} ${y + 7} M${x + 7} ${y - 7} L${x - 7} ${y + 7}`, class: 'cad-bezug' }));
  }
  if (pe.warten?.art === 'mitte' && pe.warten.erster) {
    const [x, y] = nachBild(v, pe.warten.erster);
    g.append(svgEl('circle', { cx: x, cy: y, r: 4, class: 'cad-mittepunkt' }));
    const f = a.zeiger?.fang;
    if (f) {
      const [x2, y2] = nachBild(v, f.p);
      g.append(
        svgEl('path', { d: `M${x} ${y} L${x2} ${y2}`, class: 'cad-mittelinie' }),
        svgEl('circle', { cx: (x + x2) / 2, cy: (y + y2) / 2, r: 3.5, class: 'cad-mittepunkt' }),
      );
    }
  }
  const f = a.zeiger?.fang;
  if (f && a.befehl) {
    const [x, y] = nachBild(v, f.p);
    g.append((ZEICHEN[f.art] || ZEICHEN.raster)(x, y));
  }
  if (pe.warten === 'parallel' || pe.warten === 'senkrecht') {
    const st = a.zeiger?.bild && streckeAn(a, a.zeiger.bild);
    if (st) {
      const [x0, y0] = nachBild(v, st.s);
      const [x1, y1] = nachBild(v, st.e);
      g.append(svgEl('path', { d: `M${x0} ${y0} L${x1} ${y1}`, class: 'cad-streckenwahl' }));
    }
  }
}

