/**
 * eb_verlauf.js -- der Kern je Geschoss, Querkraft und Moment über die Höhe.
 *
 * Ein Bild in der Höhe der Ansicht (eb_zeichnung.js): links in jedem
 * Geschoss sein Kern im Grundriss, x nach rechts und y nach oben, alle im
 * selben Massstab -- man sieht, wo er dünner wird oder ein Geschoss einen
 * anderen hat (Benutzer, 2026-11-27; bis dahin standen die Wände
 * nebeneinander, über die ganze Höhe dieselben). Im untersten stehen die
 * Nummern seiner getrennten Teile, wo er aus mehreren besteht: so heissen
 * sie in der Tabelle am Fuss und in der Herleitung. Daneben je Richtung,
 * die der Kern gerechnet hat, die Querkraft V als Treppe und das Moment M
 * des Kragarms, unten eingespannt: beide Richtungen im selben Massstab je
 * Grösse, in den Farben von V und M wie in allen Verläufen. Angeschrieben
 * ist je Geschoss der Wert unter ihm, wo Platz ist, sonst nur der am Fuss.
 *
 * Umrisse, Teile, Querkräfte und Momente kommen fertig aus dem Kern
 * (opencivil/web/erdbebendaten.py), die Umrisse um den Schwerpunkt ihrer
 * Analyse, wie gezeichnet. Hier wird nur gezeichnet.
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
/** Die Spalten in px: die Namen der Geschosse, der Kern, die Lücke zwischen zwei Streifen. */
const NAMEN = 84;
const KERN = 170;
const LUECKE = 14;
/** So breit steht ein Streifen höchstens da, in px -- und so weit reicht sein grösster Wert. */
const STREIFEN = 140;
const REICHWEITE = 0.8;
/** So viel Platz bleibt in einem Geschoss über und unter dem Kern, in px. */
const LUFT = 6;
/** Ab dieser Höhe eines Geschosses steht sein Wert im Streifen, in px. */
const MIT_WERT = 24;

/** Eine geschlossene Fläche durch `punkte` in px. */
function flaeche(punkte, klasse) {
  const d = punkte.map(([x, y], i) => `${i ? 'L' : 'M'}${x.toFixed(1)} ${y.toFixed(1)}`).join(' ');
  return svgEl('path', { d: `${d} Z`, class: klasse });
}

/** Die Grenzen eines Umrisses, in mm: [x links, x rechts, y unten, y oben]. */
function grenzen(kern) {
  const punkte = kern.polygone.flatMap((p) => p.punkte);
  const xs = punkte.map((p) => p[0]);
  const ys = punkte.map((p) => p[1]);
  return [Math.min(...xs), Math.max(...xs), Math.min(...ys), Math.max(...ys)];
}

/**
 * Der Kern jedes Geschosses in seinem Band, in der Spalte ab `x0` und alle
 * im selben Massstab -- so gross, wie der grösste Kern, das niedrigste
 * Geschoss mit Kern und die Spalte es zulassen. `kerne` sind je Geschoss
 * sein Grundriss aus dem Kern der Software oder nichts, `baender` je
 * Geschoss [oben, unten] in px. Im untersten stehen die Nummern der Teile.
 */
function kernbilder(kerne, baender, x0) {
  const mit = kerne.map((k, i) => [k, i]).filter(([k]) => k);
  const rahmen = new Map(mit.map(([k]) => [k, grenzen(k)]));
  const breit = Math.max(...[...rahmen.values()].map(([a, b]) => b - a));
  const hoch = Math.max(...[...rahmen.values()].map(([, , c, d]) => d - c));
  const niedrig = Math.min(...mit.map(([, i]) => baender[i][1] - baender[i][0]));
  const s = Math.min((niedrig - 2 * LUFT) / (hoch || 1), KERN / (breit || 1));
  if (!(s > 0)) return [];
  return mit.flatMap(([kern, i]) => {
    const [a, b, c, d] = rahmen.get(kern);
    const [oben, unten] = baender[i];
    const [mx, my] = [x0 + KERN / 2, (oben + unten) / 2];
    const punkt = ([X, Y]) => [mx + (X - (a + b) / 2) * s, my - (Y - (c + d) / 2) * s];
    const flaechen = [...kern.polygone].sort((p, q) => p.tiefe - q.tiefe).map((p) => mitTitel(
      flaeche(p.punkte.map(punkt), p.material ? `cad-${p.material}` : 'cad-loch'),
      [`${kern.name}: ${p.stoff || 'Aussparung'}`],
    ));
    const nummern = i === 0 ? kern.teile.map((t) => {
      const [x, y] = punkt(t.mitte);
      return text(x, y + 4, [String(t.nummer)], { anker: 'middle', klasse: 'eb-teilnummer' });
    }) : [];
    return [...flaechen, ...nummern];
  });
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
 * Die Karte «Kern, Querkraft und Moment» eines Gebäudes -- oder nichts,
 * solange es nichts zu zeigen gibt. `d` ist, was der Kern zeichnet, `a`
 * der Aufriss der Ansicht: dieselben Höhen im selben Massstab. Den Kern
 * eines Geschosses nennt der Eintrag, seinen Grundriss der Kern der
 * Software -- nur, wo er rechnet.
 */
export function verlaufKarte(h, d, a) {
  const kerne = h.geschosse.map((g) => d?.grundrisse?.[g.kern] || null);
  const mitKern = kerne.some(Boolean);
  const richtungen = d?.richtungen || [];
  if (!h.geschosse.length || (!mitKern && !richtungen.length)) return null;
  const { z, m, hoch } = a;
  const fuss = RAND + OBEN + hoch;
  const y = (hoehe) => fuss - hoehe * m;
  const baender = z.map((zi, i) => [y(zi), y(i ? z[i - 1] : 0)]);
  const xKern = RAND + NAMEN;
  const xStreifen = xKern + (mitKern ? KERN + 2 * LUECKE : 0);
  const anzahl = 2 * richtungen.length;
  const breite = Math.min(STREIFEN, (BREITE - RAND - xStreifen - LUECKE * (anzahl - 1)) / (anzahl || 1));
  const svg = svgEl('svg', {
    viewBox: `0 0 ${BREITE} ${fuss + UNTEN + RAND}`, class: 'gb-bild', role: 'img',
    'aria-label': `Kern, Querkraft und Moment des Gebäudes ${h.name}`,
  });
  const rechtsAussen = xStreifen + anzahl * (breite + LUECKE);
  // Die Decken als zarte Linien über alles: ein Geschoss liest sich quer.
  svg.append(...z.map((zi) => linie([[xKern, y(zi)], [rechtsAussen, y(zi)]], 'gb-hilfslinie')));
  h.geschosse.forEach((g, i) => {
    const [oben, unten] = baender[i];
    svg.append(text(RAND, (oben + unten) / 2 + 4, [g.name], { klasse: 'eb-name' }));
  });
  if (mitKern) {
    svg.append(text(xKern, RAND + 12, ['Kern'], { klasse: 'eb-titel' }),
      ...kernbilder(kerne, baender, xKern));
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
    schraffur([[[xKern, fuss + 1], [rechtsAussen, fuss + 1]]]),
    linie([[xKern, fuss], [rechtsAussen, fuss]], 'gb-gelaende'),
  );
  return karte('Kern, Querkraft und Moment', [
    el('div.gb-bildhuelle', {}, [svg]),
    legende(d.verlaufslegende || []),
  ], { bild: svg, klasse: 'ist-breit' });
}
