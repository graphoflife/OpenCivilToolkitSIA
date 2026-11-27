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
 * Gerechnet wird hier nichts: nur Lagen fürs Auge -- wie lang ein Pfeil im
 * Bild ist, wo ein Name steht.
 */

import {
  ansichtNeu, einpassen, nachBild, pfad, zahlText,
} from './cad_ansicht.js';
import { mitTitel, umrissVon } from './cad_app.js';
import { svgEl } from './dom.js';

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

/**
 * Das ganze Modell: die Flächen der Scheiben, die Löcher, die Umrisse, die
 * Lager, die Lasten und die Namen. `fehler(kennung)` und `texte(kennung)`
 * sagen, was der Kern an einem Teil meldet -- rot, und als Titel beim
 * Darüberfahren.
 */
export function scheibe(v, modell, { fehler = () => false, texte = () => [] } = {}) {
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
  g.append(flaechen, umrisse, lager, lasten, namen);
  return g;
}

/** So breit ist ein Bild auf seiner Karte, und so hoch höchstens und mindestens -- px. */
const BILD = { breite: 720, hoehe: [240, 520], rand: 48 };

/** Das Modell als Bild, fest im Massstab -- mit Rand für Lager und Pfeile. */
export function scheibeBild(modell) {
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
  svg.append(scheibe(v, modell));
  return svg;
}
