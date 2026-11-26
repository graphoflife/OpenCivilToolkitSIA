/**
 * eb_verlauf.js -- die Wände je Geschoss, Querkraft und Moment über die Höhe.
 *
 * Ein Bild in der Höhe der Ansicht (eb_zeichnung.js): links je Geschoss die
 * Wände im Grundriss, nebeneinander und alle im selben Massstab -- sie haben
 * keinen Ort im Grundriss, und sie gehen über die ganze Höhe. Daneben je
 * Richtung, die der Kern gerechnet hat, die Querkraft V als Treppe und das
 * Moment M des Kragarms, unten eingespannt: beide Richtungen im selben
 * Massstab je Grösse, in den Farben von V und M wie in allen Verläufen.
 * Angeschrieben ist je Geschoss der Wert unter ihm, wo Platz ist, sonst nur
 * der am Fuss.
 *
 * Umrisse, Querkräfte und Momente kommen fertig aus dem Kern
 * (opencivil/web/erdbebendaten.py), die Umrisse schon gedreht nach der Lage
 * der Wand. Hier wird nur gezeichnet.
 */

import { karte } from './bausteine.js';
import { mitTitel } from './cad_app.js';
import { el, svgEl } from './dom.js';
import {
  BREITE, legende, linie, schraffur, text, zahl,
} from './gb_skizze.js';

const RAND = 16;
/** Oben Platz für die Titel der Spalten, unten für die Schraffur, in px. */
const OBEN = 40;
const UNTEN = 22;
/** Die Spalten in px: die Namen der Geschosse, die Wände, die Lücke zwischen zwei Streifen. */
const NAMEN = 84;
const WAENDE = 170;
const LUECKE = 14;
/** So breit steht ein Streifen höchstens da, in px -- und so weit reicht sein grösster Wert. */
const STREIFEN = 140;
const REICHWEITE = 0.8;
/** So viel Platz bleibt in einem Geschoss über und unter den Wänden, in px. */
const LUFT = 6;
/** Ab dieser Höhe eines Geschosses steht sein Wert im Streifen, in px. */
const MIT_WERT = 24;

/** Eine geschlossene Fläche durch `punkte` in px. */
function flaeche(punkte, klasse) {
  const d = punkte.map(([x, y], i) => `${i ? 'L' : 'M'}${x.toFixed(1)} ${y.toFixed(1)}`).join(' ');
  return svgEl('path', { d: `${d} Z`, class: klasse });
}

/** Die Grenzen eines Umrisses, in mm: [x links, x rechts, y unten, y oben]. */
function grenzen(wand) {
  const punkte = wand.polygone.flatMap((p) => p.punkte);
  const xs = punkte.map((p) => p[0]);
  const ys = punkte.map((p) => p[1]);
  return [Math.min(...xs), Math.max(...xs), Math.min(...ys), Math.max(...ys)];
}

/**
 * Die Wände in jedem Geschoss, nebeneinander ab `x0` und alle im selben
 * Massstab -- so gross, wie das niedrigste Geschoss und die Spalte es
 * zulassen. `baender` sind je Geschoss [oben, unten] in px. Dazu die Mitte
 * jeder Wand, für ihre Nummer über der Spalte.
 */
function waende(grundrisse, baender, x0) {
  const rahmen = grundrisse.map(grenzen);
  const breit = rahmen.reduce((summe, [a, b]) => summe + (b - a), 0);
  const hoch = Math.max(...rahmen.map(([, , c, d]) => d - c));
  const niedrig = Math.min(...baender.map(([oben, unten]) => unten - oben));
  const luecken = LUECKE * (grundrisse.length - 1);
  const s = Math.min((niedrig - 2 * LUFT) / (hoch || 1), (WAENDE - luecken) / (breit || 1));
  if (!(s > 0)) return { teile: [], mitten: [] };
  let x = x0 + (WAENDE - breit * s - luecken) / 2;
  const mitten = rahmen.map(([a, b]) => {
    const mitte = x + ((b - a) * s) / 2;
    x += (b - a) * s + LUECKE;
    return mitte;
  });
  const teile = baender.flatMap(([oben, unten]) => grundrisse.flatMap((wand, k) => {
    const [a, b, c, d] = rahmen[k];
    const [mx, my] = [mitten[k], (oben + unten) / 2];
    const punkt = ([X, Y]) => [mx + (X - (a + b) / 2) * s, my - (Y - (c + d) / 2) * s];
    const name = `${wand.name}${wand.n > 1 ? ` (${wand.n}×)` : ''}`;
    return [...wand.polygone].sort((p, q) => p.tiefe - q.tiefe).map((p) => mitTitel(
      flaeche(p.punkte.map(punkt), p.material ? `cad-${p.material}` : 'cad-loch'),
      [`${name}: ${p.stoff || 'Aussparung'}`],
    ));
  }));
  return { teile, mitten };
}

/**
 * Ein Streifen ab `x0`: die Werte unter jedem Geschoss über der Höhe, als
 * Fläche von der Nulllinie bis zur Kurve. Mit `treppe` bleibt der Wert im
 * Geschoss gleich -- die Querkraft --, sonst läuft er gerade von Decke zu
 * Decke bis null am Dach -- das Moment. `y` bildet die Höhe auf px ab, `k`
 * ist der Massstab, px je Einheit.
 */
function streifen(x0, breite, werte, z, y, k, { treppe, klasse, stellen }) {
  const unten = [0, ...z.slice(0, -1)];
  const punkte = [[0, 0]];
  werte.forEach((w, i) => {
    punkte.push([w, unten[i]]);
    if (treppe) punkte.push([w, z[i]]);
  });
  punkte.push([0, z[z.length - 1]]);
  const xy = punkte.map(([w, h]) => [x0 + w * k, y(h)]);
  const teile = [
    flaeche(xy, `bs-d-flaeche ${klasse}`),
    linie([[x0, y(0)], [x0, y(z[z.length - 1])]], 'gb-masshilfe'),
    linie(xy.slice(1), `bs-d-kurve ${klasse}`),
    svgEl('circle', { cx: xy[1][0].toFixed(1), cy: xy[1][1].toFixed(1), r: 3.2,
      class: `bs-d-extrem ${klasse}` }),
  ];
  werte.forEach((w, i) => {
    // Am Fuss immer, darüber nur, wo das Geschoss hoch genug ist.
    if (i > 0 && y(unten[i]) - y(z[i]) < MIT_WERT) return;
    const x = x0 + w * k;
    const rechts = x < x0 + breite / 2;
    teile.push(text(x + (rechts ? 4 : -4), y(unten[i]) - 4, [zahl(w, stellen)],
      { anker: rechts ? 'start' : 'end', klasse: 'bs-d-text gb-index' }));
  });
  return teile;
}

/**
 * Die Karte «Wände, Querkraft und Moment» eines Gebäudes -- oder nichts,
 * solange es nichts zu zeigen gibt. `d` ist, was der Kern zeichnet, `a`
 * der Aufriss der Ansicht: dieselben Höhen im selben Massstab.
 */
export function verlaufKarte(h, d, a) {
  const grundrisse = (d?.grundrisse || []).filter(Boolean);
  const richtungen = d?.richtungen || [];
  if (!h.geschosse.length || (!grundrisse.length && !richtungen.length)) return null;
  const { z, m, hoch } = a;
  const fuss = RAND + OBEN + hoch;
  const y = (hoehe) => fuss - hoehe * m;
  const baender = z.map((zi, i) => [y(zi), y(i ? z[i - 1] : 0)]);
  const xWaende = RAND + NAMEN;
  const xStreifen = xWaende + (grundrisse.length ? WAENDE + 2 * LUECKE : 0);
  const anzahl = 2 * richtungen.length;
  const breite = Math.min(STREIFEN, (BREITE - RAND - xStreifen - LUECKE * (anzahl - 1)) / (anzahl || 1));
  const svg = svgEl('svg', {
    viewBox: `0 0 ${BREITE} ${fuss + UNTEN + RAND}`, class: 'gb-bild', role: 'img',
    'aria-label': `Wände, Querkraft und Moment des Gebäudes ${h.name}`,
  });
  const rechtsAussen = xStreifen + anzahl * (breite + LUECKE);
  // Die Decken als zarte Linien über alles: ein Geschoss liest sich quer.
  svg.append(...z.map((zi) => linie([[xWaende, y(zi)], [rechtsAussen, y(zi)]], 'gb-hilfslinie')));
  h.geschosse.forEach((g, i) => {
    const [oben, unten] = baender[i];
    svg.append(text(RAND, (oben + unten) / 2 + 4, [g.name], { klasse: 'eb-name' }));
  });
  if (grundrisse.length) {
    const { teile, mitten } = waende(grundrisse, baender, xWaende);
    svg.append(
      text(xWaende, RAND + 12, ['Wände'], { klasse: 'eb-titel' }),
      ...mitten.map((x, k) => text(x, RAND + OBEN - 8, [String(grundrisse[k].nummer)],
        { anker: 'middle', klasse: 'gb-masstext' })),
      ...teile,
    );
  }
  // Je Grösse ein Massstab für beide Richtungen: man sieht, wo das Beben stärker angreift.
  const k = (feld) => (REICHWEITE * breite) / Math.max(1e-9, ...richtungen.flatMap((r) => r[feld]));
  const [kV, kM] = [k('querkraefte'), k('momente')];
  richtungen.forEach((r, j) => {
    const xV = xStreifen + 2 * j * (breite + LUECKE);
    const xM = xV + breite + LUECKE;
    svg.append(
      text(xV, RAND + 12, ['V', { unten: r.richtung }, ' [kN]'], { klasse: 'eb-titel' }),
      ...streifen(xV, breite, r.querkraefte, z, y, kV, { treppe: true, klasse: 'bs-d-v', stellen: 0 }),
      text(xM, RAND + 12, ['M', { unten: r.richtung }, ' [kNm]'], { klasse: 'eb-titel' }),
      ...streifen(xM, breite, r.momente, z, y, kM, { treppe: false, klasse: 'bs-d-m', stellen: 0 }),
    );
  });
  svg.append(
    schraffur([[[xWaende, fuss + 1], [rechtsAussen, fuss + 1]]]),
    linie([[xWaende, fuss], [rechtsAussen, fuss]], 'gb-gelaende'),
  );
  return karte('Wände, Querkraft und Moment', [
    el('div.gb-bildhuelle', {}, [svg]),
    legende(d.verlaufslegende || []),
  ], { bild: svg, klasse: 'ist-breit' });
}
