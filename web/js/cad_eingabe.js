/**
 * cad_eingabe.js -- wie ein Punkt entsteht. Für jeden Befehl dieselbe Mechanik.
 *
 * Ob ein Knoten gesetzt, eine Linie gezogen oder etwas verschoben wird: jeder
 * Punkt kommt auf denselben Wegen zustande.
 *
 *   Maus       fängt an Knoten □, Linienmitte △, Schnittpunkt ×, am Lot ⊥
 *              vom Bezugspunkt auf eine Linie, auf der Linie ◇, sonst am
 *              Raster +. Die Punkte, die der Befehl schon gesetzt hat -- die
 *              Ecken eines offenen Polygons --, fangen wie Knoten. Alt
 *              gedrückt: nicht fangen.
 *   R          setzt den Bezugspunkt auf den gefangenen Punkt. Nach jedem
 *              gesetzten Punkt springt er von selbst dorthin.
 *   Ziffern    gehen ins schwebende Fenster: relativ zum Bezugspunkt,
 *              absolut, oder Länge und Winkel. Enter setzt den Punkt genau
 *              dorthin -- getippte Werte werden nicht gefangen.
 *   Y / Z      binden an die Achse durch den Bezugspunkt (die Buchstaben
 *              kommen von der App, im Raum X, Y und Z). Getippt wird dann
 *              nur der Abstand. Ein Punkt unter dem Zeiger wird gefangen
 *              und auf die Achse projiziert: das Fangzeichen steht an ihm,
 *              eine gestrichelte Spur führt zum Punkt auf der Achse.
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
 * IM BILD:
 * Was nah ist, misst sich im Bild, in Bildpunkten -- auch im Raum, wo ein
 * Knoten weit hinten neben einem vorne liegen kann. Ein Punkt auf einer
 * Strecke oder Geraden entsteht aus dem Anteil, bei dem er im Bild liegt;
 * die Projektion ist parallel, also liegt er in der Zeichnung beim selben.
 * Im Raum ohne einen Knoten oder eine Linie unter dem Zeiger: der Punkt der
 * Arbeitsebene, den man dort sieht (cad_ansicht.js).
 *
 * Das ist Eingabehilfe, keine Rechnung: in die Rechnung geht nur der Punkt,
 * der am Ende dasteht.
 */

import { nachBild, nachWelt, richtungImBild } from './cad_ansicht.js';
import {
  abstand, aufGerade, aufStrecke, entlang, kreuzung, minus, mitte, rund, skalar,
} from './cad_modell.js';
import { svgEl } from './dom.js';

/** Wie nah der Zeiger an etwas sein muss, um es zu fangen oder zu treffen -- px. */
export const NAEHE = 9;

/**
 * Wie nah er an einem Punkt sein muss -- einem Knoten, einer Mitte, einem
 * Schnittpunkt --, um ihn zu fangen: weiter als an einer Linie, denn einen
 * Punkt trifft man schwerer (Benutzer, 2026-10-23: «in der Nähe clippt man
 * zu dem»). Punkte gehen Linien vor.
 */
export const FANGWEITE = 12;

/** Eine leere Eingabe, für eine Zeichnung mit `achsen` Achsen. */
export function eingabeNeu(achsen = 2) {
  return {
    bezug: null,         // ein Punkt -- Bezugspunkt für Getipptes und Bindungen
    bindung: null,       // {art: 'achse'|'parallel'|'senkrecht', r: Richtung, achse?: Index, text}
    warten: null,        // 'parallel' | 'senkrecht' | {art: 'mitte', erster}
    modus: 'rel',        // 'rel' | 'abs' | 'polar'
    felder: Array(achsen).fill(''), // was getippt ist, je Achse ein Feld
    runde: 0,            // zählt mit, wenn die Felder geleert werden -- dann neu bauen
  };
}

/** Leert die Felder -- auch die im schwebenden Fenster, das daran sieht, dass `runde` weiterzählt. */
export function felderLeeren(pe) {
  pe.felder = pe.felder.map(() => '');
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
  const mitten = strecken.map((st) => ({ p: mitte(st.s, st.e), st }));
  const schnitte = [];
  for (let i = 0; i < strecken.length; i += 1) {
    for (let j = i + 1; j < strecken.length; j += 1) {
      const p = kreuzung([strecken[i].s, strecken[i].e], [strecken[j].s, strecken[j].e]);
      // Gemeinsame Enden sind Knoten, keine Schnittpunkte.
      if (p && ![strecken[i].s, strecken[i].e].some((q) => abstand(p, q) < 1e-6)) {
        schnitte.push({ p });
      }
    }
  }
  a.zielcache = {
    version: a.version, knoten, strecken, mitten, schnitte,
  };
  return a.zielcache;
}

// ===========================================================================
// Fangen
// ===========================================================================

const ras = (w, r) => Math.round(w / r) * r;

/** Die Gerade der Bindung: durch den Bezugspunkt, in ihrer Richtung. */
function bindungsgerade(a) {
  const pe = a.eingabe;
  if (!pe.bindung) return null;
  return { durch: pe.bezug || pe.felder.map(() => 0), r: pe.bindung.r };
}

/** Die Richtung einer Achse -- 1 in ihr, 0 in den anderen. */
export function achsrichtung(n, i) {
  return Array.from({ length: n }, (_, j) => (j === i ? 1 : 0));
}

/**
 * Die Stelle auf einer Geraden, die der Bildpunkt trifft: der Abstand ab
 * `durch` in Einheiten der Zeichnung, entlang der Richtung `r` (Länge 1).
 * Zeigt die Gerade genau auf den Betrachter, ist es null.
 */
function stelleAufGerade(a, bild, { durch, r }) {
  const d = richtungImBild(a.v, r);
  const l2 = d[0] * d[0] + d[1] * d[1];
  if (l2 < 1e-12) return 0;
  const p = nachBild(a.v, durch);
  return ((bild[0] - p[0]) * d[0] + (bild[1] - p[1]) * d[1]) / l2;
}

/** Eine Richtung auf die Länge 1. */
function einheit(r) {
  const l = Math.hypot(...r) || 1;
  return r.map((x) => x / l);
}

/**
 * Shift: die Achse durch den Bezugspunkt, die im Bild am ehesten dorthin
 * zeigt, wo der Zeiger steht -- in der Ebene waagrecht oder senkrecht.
 */
function geradeRichtung(a, bild) {
  const p = nachBild(a.v, a.eingabe.bezug);
  const zum = [bild[0] - p[0], bild[1] - p[1]];
  const n = a.eingabe.bezug.length;
  let beste = null;
  for (let i = 0; i < n; i += 1) {
    const d = richtungImBild(a.v, achsrichtung(n, i));
    const l = Math.hypot(...d);
    const passt = l > 1e-9 ? Math.abs(zum[0] * d[0] + zum[1] * d[1]) / l : -1;
    if (!beste || passt > beste.passt) beste = { i, passt };
  }
  return achsrichtung(n, beste.i);
}

/** Der Punkt aufs Raster -- im Raum nur in der Arbeitsebene; ihre Lage bleibt, wie sie ist. */
function aufsRaster(a, p) {
  const ebene = a.v.ebene;
  return p.map((w, i) => (ebene && i === ebene.achse ? ebene.lage : ras(w, a.raster)));
}

/** In welcher Achse allein sich eine Strecke ändert -- oder -1. */
function achsparallel(s, e) {
  const d = minus(e, s);
  const frei = d.map((x, i) => (Math.abs(x) < 1e-9 ? -1 : i)).filter((i) => i >= 0);
  return frei.length === 1 ? frei[0] : -1;
}

/**
 * Wohin der Zeiger fängt -- `{p, art, knoten?}`. Mit einer Bindung liegt
 * das Ergebnis immer auf ihr: ein gefangener Punkt wird auf sie projiziert,
 * sonst der Abstand ab dem Bezugspunkt ans Raster gerundet.
 */
export function fangen(a, bild, { frei = false, gerade = false } = {}) {
  const v = a.v;
  const pe = a.eingabe;
  const welt = nachWelt(v, bild);
  const imBild = (p) => nachBild(v, p);
  const ohneFang = frei || !a.fang;
  let linie = bindungsgerade(a);

  // Shift: entlang einer Achse durch den Bezugspunkt, solange gedrückt.
  if (!linie && gerade && pe.bezug) linie = { durch: pe.bezug, r: geradeRichtung(a, bild) };

  const z = ohneFang ? null : ziele(a);
  // Was die App dazu fangen lässt (der Schwerpunkt), je Mal neu: es kommt
  // oft erst nach der Zeichnung an, aus einer Antwort des Kerns.
  const extra = ohneFang ? [] : a.adapter.fangpunkte?.(a) || [];
  // Was der Befehl schon gesetzt hat -- die Ecken eines Polygons, das noch
  // offen ist (Benutzer, 2026-10-23). Sie fangen wie Knoten.
  const gesetzt = ohneFang ? [] : a.befehl?.fangpunkte?.() || [];
  const naechster = (liste) => {
    let bester = null;
    for (const x of liste) {
      const d = abstand(bild, imBild(x.p));
      if (d <= FANGWEITE && (!bester || d < bester.d)) bester = { ...x, d };
    }
    return bester;
  };
  // Ein Punkt unter dem Zeiger: zuerst ein Knoten, dann Schnittpunkte,
  // Mitten und was die App dazugibt -- je mit seinem Fangzeichen.
  const punkt = z && (naechster([...z.knoten.map((k) => ({ p: k.p, art: 'knoten', knoten: k.kennung })),
    ...gesetzt.map((x) => ({ p: x.p, art: 'knoten', knoten: x.knoten }))])
    || naechster([...z.schnitte.map((x) => ({ p: x.p, art: 'schnitt' })),
      ...z.mitten.map((x) => ({ p: x.p, art: 'mitte' })),
      ...extra.map((x) => ({ p: x.p, art: 'punkt' }))]));

  if (linie) {
    // Was in der Nähe gefangen wird, wandert auf die Bindung -- `von` sagt,
    // welcher Punkt es war, damit man ihn gefangen sieht.
    if (punkt) {
      return { p: aufGerade(punkt.p, linie.durch, linie.r), art: 'projiziert',
        von: { p: punkt.p, art: punkt.art } };
    }
    const r = einheit(linie.r);
    const t = stelleAufGerade(a, bild, { durch: linie.durch, r });
    if (ohneFang) return { p: entlang(linie.durch, r, t), art: 'frei' };
    // Der Abstand ab dem Bezugspunkt aufs Raster.
    return { p: entlang(linie.durch, r, ras(t, a.raster)), art: 'raster' };
  }

  if (ohneFang) return { p: welt, art: 'frei' };

  if (punkt) return { p: punkt.p, art: punkt.art, knoten: punkt.knoten };

  // Das Lot vom Bezugspunkt auf eine Strecke -- nur, wo sein Fuss auf ihr liegt.
  if (pe.bezug) {
    let lot = null;
    for (const st of z.strecken) {
      const r = minus(st.e, st.s);
      const l2 = skalar(r, r);
      if (!l2) continue;
      const t = skalar(minus(pe.bezug, st.s), r) / l2;
      if (t <= 1e-9 || t >= 1 - 1e-9) continue;
      const fuss = entlang(st.s, r, t);
      const d = abstand(bild, imBild(fuss));
      if (d <= NAEHE && abstand(fuss, pe.bezug) > 1e-9 && (!lot || d < lot.d)) lot = { p: fuss, d };
    }
    if (lot) return { p: lot.p, art: 'lot' };
  }

  let bester = null;
  for (const st of z.strecken) {
    const { t } = aufStrecke(bild, imBild(st.s), imBild(st.e));
    const q = entlang(st.s, minus(st.e, st.s), t);
    const d = abstand(bild, imBild(q));
    if (d > NAEHE * 0.8 || (bester && d >= bester.d)) continue;
    // Auf einer Strecke entlang einer Achse darf die freie Richtung ans
    // Raster -- der Punkt bleibt trotzdem genau auf ihr.
    let p = q;
    const i = achsparallel(st.s, st.e);
    if (i >= 0) p = st.s.map((w, j) => (j === i ? ras(q[i], a.raster) : w));
    if (abstand(aufStrecke(p, st.s, st.e).q, p) > 1e-9) p = q;
    bester = { p, d, art: 'linie' };
  }
  if (bester) return { p: bester.p, art: 'linie' };
  return { p: aufsRaster(a, welt), art: 'raster' };
}

/**
 * Was der Zeiger gerade fängt -- während eines Befehls ist es schon
 * gefangen, in Ruhe erst hier. Null, wenn er nicht über der Zeichnung ist.
 */
export function zeigerFang(a) {
  return a.zeiger?.fang || (a.zeiger?.bild ? fangen(a, a.zeiger.bild) : null);
}

/** Die Strecke unter dem Zeiger -- für P und S, und um eine Kante zu treffen. */
function streckeAn(a, bild) {
  let bester = null;
  for (const st of ziele(a).strecken) {
    const [s, e] = [nachBild(a.v, st.s), nachBild(a.v, st.e)];
    const d = abstand(bild, aufStrecke(bild, s, e).q);
    if (d <= NAEHE && (!bester || d < bester.d)) bester = { ...st, d };
  }
  return bester;
}

/**
 * Senkrecht zur Richtung `r`: in der Ebene um 90° gedreht, im Raum in der
 * Arbeitsebene -- quer zu `r` und zu ihrer Normalen. Null, wenn `r` auf
 * der Arbeitsebene senkrecht steht.
 */
function senkrecht(a, r) {
  if (r.length === 2) return [-r[1], r[0]];
  const n = achsrichtung(3, a.v.ebene.achse);
  const s = [n[1] * r[2] - n[2] * r[1], n[2] * r[0] - n[0] * r[2], n[0] * r[1] - n[1] * r[0]];
  return Math.hypot(...s) > 1e-9 * Math.hypot(...r) ? s : null;
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
    let r = minus(st.e, st.s);
    if (pe.warten === 'senkrecht') r = senkrecht(a, r);
    if (!r) {
      pe.warten = null;
      return { fehler: 'Diese Linie steht senkrecht auf der Arbeitsebene – darin gibt es keine Senkrechte zu ihr.' };
    }
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
    let m = mitte(pe.warten.erster, f.p);
    const g = bindungsgerade(a);
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
  const werte = pe.felder.map(zahl);
  if (werte.every((w) => w === null)) return null;
  if (werte.some((w) => Number.isNaN(w))) return { fehler: 'Das ist keine Zahl.' };
  const bezug = pe.bezug || werte.map(() => 0);
  const g = bindungsgerade(a);
  if (g) {
    // Mit einer Bindung gibt es nur den Abstand entlang.
    return { p: entlang(bezug, einheit(g.r), werte[0] ?? 0).map(rund), art: 'getippt' };
  }
  if (pe.modus === 'abs') return { p: werte.map((w, i) => w ?? bezug[i]).map(rund), art: 'getippt' };
  if (pe.modus === 'polar') {
    // Länge und Winkel in der Ebene -- im Raum in der Arbeitsebene, ab ihrer ersten Achse.
    const [i, j] = ebenenachsen(a);
    const winkel = ((werte[1] ?? 0) * Math.PI) / 180;
    const p = [...bezug];
    p[i] += (werte[0] ?? 0) * Math.cos(winkel);
    p[j] += (werte[0] ?? 0) * Math.sin(winkel);
    return { p: p.map(rund), art: 'getippt' };
  }
  return { p: bezug.map((b, i) => b + (werte[i] ?? 0)).map(rund), art: 'getippt' };
}

/** Die beiden Achsen, in denen gezeichnet wird -- in der Ebene beide, im Raum die der Arbeitsebene. */
export function ebenenachsen(a) {
  const n = a.adapter.achsen.length;
  const quer = a.v.ebene ? a.v.ebene.achse : -1;
  return Array.from({ length: n }, (_, i) => i).filter((i) => i !== quer).slice(0, 2);
}

/**
 * Was die Felder gerade heissen -- je nach Modus und Bindung. Ein Feld, das
 * nicht gebraucht wird, heisst null.
 */
export function feldnamen(a) {
  const achsen = a.adapter.achsen;
  const ohne = (namen) => achsen.map((_, i) => namen[i] ?? null);
  if (a.eingabe.bindung) return ohne(['Abstand']);
  if (a.eingabe.modus === 'polar') return ohne(['L', 'α']);
  return a.eingabe.modus === 'rel' ? achsen.map((x) => `Δ${x}`) : [...achsen];
}

/**
 * In welcher Einheit die Felder gemeint sind: Längen in der Einheit der App
 * (mm im Querschnitt, m im Balkensystem), der Winkel in Grad. Sie steht
 * rechts neben jedem Feld (Benutzer, 2026-10-23).
 */
export function feldeinheiten(a) {
  const e = a.einstellung.einheit;
  const namen = feldnamen(a);
  if (a.eingabe.modus === 'polar' && !a.eingabe.bindung) return namen.map((n, i) => (n ? [e, '°'][i] : null));
  return namen.map((n) => (n ? e : null));
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
  const anBezug = () => {
    if (!pe.bezug && a.zeiger?.fang) pe.bezug = a.zeiger.fang.p.map(rund);
  };
  const achse = a.adapter.achsen.findIndex((x) => x.toLowerCase() === k);
  if (achse >= 0) {
    if (pe.bindung?.art === 'achse' && pe.bindung.achse === achse) {
      pe.bindung = null;
    } else {
      anBezug();
      pe.bindung = {
        art: 'achse', achse, r: achsrichtung(a.adapter.achsen.length, achse),
        text: `entlang ${a.adapter.achsen[achse]}`,
      };
    }
    felderLeeren(pe);
    return true;
  }
  switch (k) {
    case 'r':
      if (!a.zeiger?.fang) return false;
      pe.bezug = a.zeiger.fang.p.map(rund);
      return true;
    case 'm':
      pe.warten = { art: 'mitte', erster: null };
      return true;
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
  const gerade = bindungsgerade(a);
  if (gerade) {
    const durch = nachBild(v, gerade.durch);
    const r = richtungImBild(v, gerade.r);
    const l = Math.hypot(...r);
    const lang = Math.hypot(v.breite, v.hoehe);
    // Zeigt die Gerade auf den Betrachter, ist sie im Bild ein Punkt.
    if (l > 1e-9) {
      const [dx, dy] = [(r[0] / l) * lang, (r[1] / l) * lang];
      g.append(svgEl('path', {
        d: `M${durch[0] - dx} ${durch[1] - dy} L${durch[0] + dx} ${durch[1] + dy}`, class: 'cad-bindung',
      }));
    } else {
      g.append(svgEl('circle', { cx: durch[0], cy: durch[1], r: 6, class: 'cad-bindung' }));
    }
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
    // Ein projizierter Punkt: sein Zeichen dort, wo er gefangen wurde, und
    // eine Spur von dort zur Stelle auf der Bindung.
    if (f.von) {
      const [x0, y0] = nachBild(v, f.von.p);
      g.append(
        svgEl('path', { d: `M${x0} ${y0} L${x} ${y}`, class: 'cad-spur' }),
        (ZEICHEN[f.von.art] || ZEICHEN.punkt)(x0, y0),
      );
    }
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

