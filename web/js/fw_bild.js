/**
 * fw_bild.js -- ein Fachwerkmodell, gezeichnet.
 *
 * Was ein Fachwerkmodell im Bild zeigt, im Zeichenfenster wie auf seiner
 * Karte im Reiter «Diagramme»: die Scheiben hell mit kräftigem Rand, die
 * Löcher ausgespart und gestrichelt, die Lager mit ihrem Zeichen und die
 * Lasten als Pfeile. Beide Bilder rufen dieselbe Funktion, jedes mit
 * seiner Ansicht `v` (cad_ansicht.js).
 *
 * ZEICHEN DER LAGER, unter dem Punkt, den sie halten:
 *   fest in x und y    ein Dreieck auf schraffiertem Grund
 *   nur in y           ein Dreieck auf Rollen über dem Grund -- in x verschieblich
 *   nur in x           dasselbe um 90° gedreht, links vom Punkt
 *
 * ZEICHEN DER LASTEN:
 * Ein Pfeil, der im Punkt endet, in der Richtung der Kraft, daneben Name und
 * Betrag; beim Darüberfahren beide Teile, F_h nach rechts und F_v nach
 * unten.
 *
 * DAS FACHWERK, nur auf der Karte, über der Scheibe und unter Lagern und
 * Lasten: Zug rot und durchgezogen, Druck blau und gestrichelt, wie in
 * Fachwerkmodellen üblich, jeder Stab so dick, wie seine Kraft gross ist --
 * bezogen auf die grösste. Beim Darüberfahren Kraft und Länge.
 *
 * DIE FORM des Verfahrens SIMP, ebenso nur auf der Karte, auf der Scheibe
 * unter dem Fachwerk: je Element ein graues Quadrat, so dunkel, wie es
 * voll ist -- unter einem Fachwerk heller.
 *
 * Gerechnet wird hier nichts: nur Lagen fürs Auge -- wie lang ein Pfeil im
 * Bild ist, wo ein Name steht, wie dick ein Stab.
 */

import {
  ansichtNeu, einpassen, nachBild, pfad, zahlText,
} from './cad_ansicht.js';
import { mitTitel, umrissVon } from './cad_app.js';
import { el, svgEl } from './dom.js';

/** So lang ist ein Lastpfeil im Bild, in px -- gleich, wie gross die Kraft ist. */
const PFEIL = 38;

/** Wie ein Lager hält, in Worten -- für den Titel beim Darüberfahren. */
const HAELT = { xy: 'fest in x und y', x: 'fest nur in x', y: 'fest nur in y' };

function text(p, inhalt, klasse) {
  const t = svgEl('text', { x: p[0].toFixed(1), y: p[1].toFixed(1), class: klasse });
  t.textContent = inhalt;
  return t;
}

/** Der Betrag einer Last in kN, aus ihren beiden Teilen. */
export const betrag = (f) => Math.hypot(f.F_h, f.F_v);

/**
 * Das Zeichen eines Lagers bei `[x, y]` (Bildpunkte), wie unter dem Punkt
 * gezeichnet -- fest nur in x um 90° gedreht, nach links.
 */
function lagerzeichen(x, y, halt) {
  const g = svgEl('g', halt === 'x' ? { transform: `rotate(90 ${x.toFixed(1)} ${y.toFixed(1)})` } : {});
  const p = (dx, dy) => `${(x + dx).toFixed(1)} ${(y + dy).toFixed(1)}`;
  const dreieck = halt === 'xy' ? 11 : 9;
  // Der Grund, schraffiert, `dy` unter dem Punkt.
  const grund = (dy) => {
    const d = [`M${p(-11, dy)} L${p(11, dy)}`];
    for (let s = -9; s <= 9; s += 6) d.push(`M${p(s, dy)} L${p(s - 4, dy + 5)}`);
    return svgEl('path', { d: d.join(' '), class: 'fw-grund' });
  };
  g.append(svgEl('path', { d: `M${p(0, 0)} L${p(-7, dreieck)} L${p(7, dreieck)} Z`, class: 'fw-lager' }));
  if (halt === 'xy') g.append(grund(11));
  else {
    for (const s of [-4, 4]) g.append(svgEl('circle', { cx: x + s, cy: y + 11.2, r: 2.2, class: 'fw-rolle' }));
    g.append(grund(13.8));
  }
  return g;
}

/**
 * Ein Lastpfeil, der bei `[x, y]` (Bildpunkte) endet -- in der Richtung von
 * `F_h` nach rechts und `F_v` nach unten. Zurück der Pfeil und wo sein
 * Ende liegt, für die Beschriftung.
 */
function lastpfeil(x, y, f) {
  const n = betrag(f);
  const u = n > 0 ? [f.F_h / n, f.F_v / n] : [0, 1];
  const ende = [x - u[0] * PFEIL, y - u[1] * PFEIL];
  const spitze = (seite) => [x - u[0] * 9 + seite * u[1] * 4, y - u[1] * 9 - seite * u[0] * 4];
  const [l, r] = [spitze(1), spitze(-1)];
  const d = `M${ende[0].toFixed(1)} ${ende[1].toFixed(1)} L${(x - u[0] * 8).toFixed(1)} ${(y - u[1] * 8).toFixed(1)} `
    + `M${x.toFixed(1)} ${y.toFixed(1)} L${l[0].toFixed(1)} ${l[1].toFixed(1)} L${r[0].toFixed(1)} ${r[1].toFixed(1)} Z`;
  return { d, ende, u };
}

/** So dick ist ein Stab im Bild, in px: der dünnste und der mit der grössten Kraft. */
const STAB = [1.2, 6];

/**
 * Das Fachwerk (fw_suche.js, `gezeigtesFachwerk`): je Stab eine Linie von
 * Knoten zu Knoten, dazu die Knoten, an denen Stäbe enden.
 */
function fachwerkLinien(v, fachwerk) {
  const g = svgEl('g', { class: 'fw-fachwerk' });
  const groesste = Math.max(0, ...fachwerk.staebe.map((s) => Math.abs(s.N)));
  const bild = (k) => nachBild(v, [fachwerk.knoten[k].x, fachwerk.knoten[k].y]);
  const enden = new Set();
  fachwerk.staebe.forEach((s, i) => {
    const [[x1, y1], [x2, y2]] = [bild(s.von), bild(s.bis)];
    const dicke = STAB[0] + (STAB[1] - STAB[0]) * (groesste > 0 ? Math.abs(s.N) / groesste : 0);
    const zug = s.N > 0;
    g.append(mitTitel(svgEl('line', {
      x1: x1.toFixed(1), y1: y1.toFixed(1), x2: x2.toFixed(1), y2: y2.toFixed(1),
      class: zug ? 'fw-stab ist-zug' : 'fw-stab ist-druck', 'stroke-width': dicke.toFixed(2),
    }), [`Stab ${i + 1}: ${zug ? 'Zug' : 'Druck'}, N = ${zahlText(s.N, 1)} kN, l = ${zahlText(s.l, 2)} m`]));
    enden.add(s.von).add(s.bis);
  });
  for (const k of enden) {
    const [x, y] = bild(k);
    g.append(svgEl('circle', { cx: x.toFixed(1), cy: y.toFixed(1), r: 2.2, class: 'fw-knoten' }));
  }
  return g;
}

/**
 * Die Form des Verfahrens SIMP (fachwerkdaten.py, `_formbild`): je Zeile die
 * Stücke gleicher Dichte als ein Rechteck, so dunkel, wie sie voll sind --
 * leere und Felder ohne Element bleiben frei.
 */
function formFelder(v, form, mitFachwerk) {
  const g = svgEl('g', { class: mitFachwerk ? 'fw-form mit-fachwerk' : 'fw-form' });
  const { x0, y0, h, spalten, zeilen, werte } = form;
  for (let j = 0; j < zeilen; j += 1) {
    for (let i = 0; i < spalten;) {
      const zeichen = werte[j * spalten + i];
      let k = i + 1;
      while (k < spalten && werte[j * spalten + k] === zeichen) k += 1;
      const stufe = zeichen === '-' ? 0 : parseInt(zeichen, 16);
      if (stufe > 0) {
        const [xa, ya] = nachBild(v, [x0 + i * h, y0 + (j + 1) * h]);
        const [xb, yb] = nachBild(v, [x0 + k * h, y0 + j * h]);
        g.append(svgEl('rect', {
          x: xa.toFixed(1), y: ya.toFixed(1), width: (xb - xa).toFixed(1), height: (yb - ya).toFixed(1),
          'fill-opacity': (stufe / 15).toFixed(2),
        }));
      }
      i = k;
    }
  }
  return g;
}

/** Was die Linien des Fachwerks heissen und, gibt es eine, was die Form -- unter dem Bild. */
export function fachwerkLegende(fachwerk, form) {
  const probe = (klasse, text) => {
    const svg = svgEl('svg', { viewBox: '0 0 26 8', width: 26, height: 8, 'aria-hidden': 'true' });
    svg.append(svgEl('line', { x1: 1, y1: 4, x2: 25, y2: 4, class: klasse, 'stroke-width': 2.4 }));
    return el('span.dk-legende-eintrag', {}, [svg, text]);
  };
  const formProbe = () => {
    const svg = svgEl('svg', { viewBox: '0 0 26 8', width: 26, height: 8, 'aria-hidden': 'true' });
    const g = svgEl('g', { class: 'fw-form' });
    g.append(svgEl('rect', { x: 1, y: 0, width: 24, height: 8 }));
    svg.append(g);
    return el('span.dk-legende-eintrag', {}, [svg, 'die Form: je dunkler, desto voller']);
  };
  return el('div.dk-legende', {}, [
    ...(fachwerk ? [probe('fw-stab ist-zug', 'Zug'), probe('fw-stab ist-druck', 'Druck'),
      el('span.dk-legende-eintrag', { text: 'je dicker, desto grösser die Kraft' })] : []),
    form ? formProbe() : null,
  ].filter(Boolean));
}

/**
 * Das ganze Modell: die Flächen der Scheiben, die Form, wenn eine da ist,
 * die Löcher, die Umrisse, das Fachwerk, wenn eines da ist, die Lager, die
 * Lasten und die Namen. `fehler(kennung)` und `texte(kennung)` sagen, was
 * der Kern an einem Teil meldet -- rot, und als Titel beim Darüberfahren.
 */
export function scheibe(v, modell, {
  fehler = () => false, texte = () => [], fachwerk = null, form = null,
} = {}) {
  const g = svgEl('g', { class: 'fw-modell' });
  const lagen = new Map((modell.knoten || []).map((k) => [k.kennung, [k.x, k.y]]));
  const orte = (knoten) => {
    const punkte = knoten.map((k) => lagen.get(k));
    return punkte.some((p) => !p) ? null : punkte;
  };
  const klasse = (grund, kennung) => (fehler(kennung) ? `${grund} ist-fehler` : grund);
  const flaechen = svgEl('g');
  const umrisse = svgEl('g');
  const namen = svgEl('g', { class: 'dk-namen' });
  for (const [liste, grund, was] of [['scheiben', 'fw-scheibe', 'Scheibe'], ['loecher', 'fw-loch', 'Loch']]) {
    for (const s of modell[liste] || []) {
      const punkte = orte(s.knoten);
      if (!punkte || punkte.length < 3) continue;
      flaechen.append(svgEl('path', { d: pfad(v, punkte), class: `${grund}-flaeche` }));
      umrisse.append(mitTitel(svgEl('path', { d: pfad(v, punkte), class: klasse(grund, s.kennung) }),
        [`${was} ${s.kennung}`, ...texte(s.kennung)]));
      const oben = punkte.reduce((a, b) => (nachBild(v, b)[1] < nachBild(v, a)[1] ? b : a));
      const [x, y] = nachBild(v, oben);
      namen.append(text([x + 4, y + 11], s.kennung, 'dk-name ist-klein'));
    }
  }
  const lager = svgEl('g');
  for (const a of modell.lager || []) {
    const ort = lagen.get(a.knoten);
    if (!ort) continue;
    const [x, y] = nachBild(v, ort);
    const gruppe = svgEl('g', { class: klasse('fw-lagergruppe', a.kennung) });
    gruppe.append(lagerzeichen(x, y, a.halt));
    lager.append(mitTitel(gruppe, [`Lager ${a.kennung}: ${HAELT[a.halt] || a.halt}`, ...texte(a.kennung)]));
    namen.append(text(a.halt === 'x' ? [x - 26, y - 9] : [x + 13, y + 6], a.kennung, 'dk-name ist-klein'));
  }
  const lasten = svgEl('g');
  for (const f of modell.lasten || []) {
    const ort = lagen.get(f.knoten);
    if (!ort) continue;
    const [x, y] = nachBild(v, ort);
    const { d, ende, u } = lastpfeil(x, y, f);
    lasten.append(mitTitel(svgEl('path', { d, class: klasse('fw-last', f.kennung) }),
      [`Last ${f.kennung}: F_h = ${zahlText(f.F_h, 1)} kN nach rechts, F_v = ${zahlText(f.F_v, 1)} kN nach unten`,
        ...texte(f.kennung)]));
    // Der Name hinter dem Ende des Pfeils: neben einem waagrechten, über oder unter einem senkrechten.
    const waagrecht = Math.abs(u[0]) > Math.abs(u[1]);
    const lage = waagrecht ? [ende[0] - Math.sign(u[0]) * 4, ende[1]] : [ende[0] + 4, ende[1] - Math.sign(u[1]) * 8];
    namen.append(text(lage, `${f.kennung} · ${zahlText(betrag(f), 1)} kN`,
      `dk-name ist-klein ist-last${waagrecht && u[0] > 0 ? ' ist-links' : ''}`));
  }
  g.append(flaechen);
  if (form) g.append(formFelder(v, form, Boolean(fachwerk)));
  g.append(umrisse);
  if (fachwerk) g.append(fachwerkLinien(v, fachwerk));
  g.append(lager, lasten, namen);
  return g;
}

/** So breit ist ein Bild auf seiner Karte, und so hoch höchstens und mindestens -- px. */
const BILD = { breite: 720, hoehe: [240, 520], rand: 48 };

/**
 * Das Modell als Bild, fest im Massstab -- mit Rand für Lager und Pfeile,
 * darin das `fachwerk` und die `form`, wenn sie da sind.
 */
export function scheibeBild(modell, fachwerk = null, form = null) {
  const umriss = umrissVon((modell.knoten || []).map((k) => [k.x, k.y]), [[0, 0], [6, 3]]);
  const [[x0, y0], [x1, y1]] = umriss;
  const breit = Math.max(x1 - x0, 1);
  const hoch = Math.max(y1 - y0, 1);
  const hoehe = Math.min(BILD.hoehe[1], Math.max(BILD.hoehe[0],
    (hoch / breit) * (BILD.breite - 2 * BILD.rand) + 2 * BILD.rand));
  const v = ansichtNeu([1e-3, 1e5]);
  Object.assign(v, { breite: BILD.breite, hoehe });
  einpassen(v, umriss, { rand: BILD.rand });
  const svg = svgEl('svg', { viewBox: `0 0 ${BILD.breite} ${hoehe.toFixed(0)}`, class: 'gb-bild fw-bild' });
  svg.append(scheibe(v, modell, { fachwerk, form }));
  return svg;
}
