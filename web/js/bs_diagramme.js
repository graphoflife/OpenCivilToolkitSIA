/**
 * bs_diagramme.js -- die Ergebnisse eines Balkensystems, rechts.
 *
 * Unter «Diagramme» je Zeile der Statik-Analyse ein Diagramm -- ihr Fall,
 * Lastfall oder Kombination, und ihre Grösse (Benutzer, 2026-10-23):
 *
 *   Schnittgrösse  je Stab der Verlauf, quer zum Stab aufgetragen, positive
 *                  Werte zu der Achse des Stabs, die der Katalog nennt: in
 *                  der Ebene zur gestrichelten Faser -- das Moment also auf
 *                  der Zugseite --, im Raum M_y und V_z zu z, M_z und V_y
 *                  zu y. N und T haben keine Seite: sie stehen zu der Achse
 *                  quer zum Stab, die man im Bild länger sieht;
 *   Verschiebung   das System verschoben, überhöht -- das unverformte blass;
 *   Verdrehung     (in der Ebene) je Stab die Verdrehung φ des Querschnitts,
 *                  aufgetragen wie ein Verlauf, im Gegenuhrzeigersinn positiv;
 *   Lagerkräfte    je Lager die Kräfte und Momente auf das Tragwerk.
 *
 * Angeschrieben sind die Werte an den Enden und je Stab die grössten, an
 * ihrer Stelle ein Punkt, im Feld dazu die Stelle x -- bei der Verschiebung
 * die grössten Durchbiegungen gegen die Sehne. Deckte eine Zahl eine
 * frühere, rückt sie weiter (`freistellen`). Die Extremwerte rechnet der
 * Kern genau; sie stehen in seiner Übersicht, nicht in den Proben. Welche
 * Grössen es gibt, wie sie heissen und welche Einheit sie haben, sagt der
 * Katalog der Art (`ergebnisse`) -- eben und im Raum zeichnet derselbe Code.
 *
 * IM RAUM:
 * Ein System im Raum sieht man parallel projiziert wie im Zeichenfenster
 * (cad_raum.js); über jedem Diagramm wählt ein Schalter die Ansicht: schräg
 * von oben, Grundriss x-y, Ansicht x-z, Ansicht y-z. Ein Verlauf liegt in
 * der Ebene aus dem Stab und seiner Achse und erscheint verkürzt wie sie --
 * sieht man die Achse von vorne, sieht man den Verlauf von der Seite. Die
 * Ansicht ist Darstellung: sie gilt, bis das Projekt neu geladen wird, und
 * wird nicht abgelegt.
 *
 * Fahren mit der Maus -- auf dem Handy: Tippen -- über einen Knoten zeigt
 * seine Verschiebung und Drehung, oder «Verdrehung nicht bestimmbar, da keine
 * Steifigkeit»; über einem Stab den Wert an dieser Stelle.
 *
 * Unter «Zusammenfassung» je System eine Tabelle: je Fall die grössten und
 * kleinsten Schnittgrössen und die massgebenden Durchbiegungen über alle
 * Stäbe und die Lagerkräfte -- aus der Rechnung, die mit jeder Eingabe läuft.
 *
 * Die Beschriftung (`anschreiben`) und das Fahren mit der Maus
 * (`zeigerEinrichten`) teilt das Bild längs eines Schnitts durch eine Decke
 * (dk_schnitt.js): es zeigt seine Grösse wie an einem Balken.
 *
 * Die Verläufe kommen aus einer eigenen Anfrage (`balkensystem_verlauf`),
 * erst wenn jemand sie sehen will (fallantwort.js) -- wie die Diagramme der
 * Querschnittsanalyse. Gerechnet wird hier nichts: die Werte kommen fertig
 * aus dem Kern, mit den Extremstellen, den Grenzwerten über alle Stäbe und
 * der grössten Verschiebung; zwischen seinen dichten Proben wird für die
 * Anzeige beim Darüberfahren nur gerade verbunden.
 */

import { api } from './api.js';
import { karte, wahlSchalter } from './bausteine.js';
import { imBild, kraft, moment } from './bs_symbole.js';
import { systemart, systemkatalog } from './bs_teile.js';
import { nachBild } from './cad_ansicht.js';
import { skalar } from './cad_modell.js';
import { ANSICHTEN, achsenkreuz, basisAus } from './cad_raum.js';
import { el, leerzustand, svgEl } from './dom.js';
import { antwortZu } from './fallantwort.js';
import { fallname } from './lastfaelle.js';
import { aendern, eintragVon, zustand } from './zustand.js';

const BREITE = 640;
/** Wie weit die grösste Ordinate vom Stab absteht, in Bildpunkten. */
const AUSSCHLAG = 44;
/**
 * Platz rund um das System, in Bildpunkten: für die grösste Ordinate und
 * dahinter ihren Wert mit Stelle -- bis 2026-10-24 waren es 58, und der Wert
 * an einer äusseren Stütze war halb abgeschnitten.
 */
const RAND = AUSSCHLAG + 46;

/** Die Farbe eines Verlaufs nach seiner Familie: N; V, V_y, V_z; M, M_y, M_z; T; φ. */
const FARBEN = { N: 'bs-d-n', V: 'bs-d-v', M: 'bs-d-m', T: 'bs-d-t', phi: 'bs-d-phi' };

const fest = (x, n) => (Math.abs(x) < 0.5 * 10 ** -n ? 0 : x).toFixed(n);

/** «M = 12.5 kNm» -- ein Wert mit Zeichen und Einheit einer Grösse des Katalogs. */
const wertText = (g, wert) => `${g.zeichen} = ${fest(wert, g.stellen)} ${g.einheit}`;

// ===========================================================================
// Rahmen: vom System ins Bild
// ===========================================================================

/** Ein Punkt eines Stabs an der Stelle x, in der Zeichnung. */
const amStab = (s, x) => s.anfang.map((w, i) => w + x * s.achsen.x[i]);

/**
 * Massstab und Lage im Bild, ringsum Platz für die Ordinaten: eine Ansicht
 * wie die des Zeichenfensters (cad_ansicht.js) -- in der Ebene x nach rechts
 * und z nach oben, im Raum aus der Richtung `basis` (cad_raum.js). Dazu die
 * Achsen des Systems und seine Grösse, nach der die Verschiebung überhöht
 * wird -- in jeder Ansicht dieselbe.
 */
function bildrahmen(staebe, basis, achsen) {
  const ecken = Object.values(staebe).flatMap((s) => [s.anfang, amStab(s, s.L)]);
  const einheit = { basis, massstab: 1, ursprung: [0, 0] };
  const bilder = ecken.map((p) => nachBild(einheit, p));
  const spanne = (werte) => [Math.min(...werte), Math.max(...werte)];
  const [x0, x1] = spanne(bilder.map((p) => p[0]));
  const [y0, y1] = spanne(bilder.map((p) => p[1]));
  const breite = Math.max(x1 - x0, 1e-9);
  const hoehe = Math.max(y1 - y0, 1e-9);
  let m = Math.min((BREITE - 2 * RAND) / breite, 380 / hoehe);
  if (!Number.isFinite(m) || m <= 0) m = 50;
  const hoeheBild = Math.round(hoehe * m + 2 * RAND);
  const v = {
    basis, massstab: m, breite: BREITE, hoehe: hoeheBild,
    ursprung: [BREITE / 2 - (m * (x0 + x1)) / 2, hoeheBild / 2 - (m * (y0 + y1)) / 2],
  };
  const spannen = achsen.map((_, i) => {
    const [klein, gross] = spanne(ecken.map((p) => p[i]));
    return gross - klein;
  });
  return { v, achsen, hoehe: hoeheBild, groesse: Math.max(1e-9, ...spannen), bild: (p) => nachBild(v, p) };
}

/**
 * Wohin die Ordinaten eines Stabs im Bild zeigen: zu seiner Achse `achse`,
 * verkürzt wie sie (`d`, je Bildpunkt Ausschlag) -- ohne Achse (N, T) zu
 * der quer zum Stab, die man länger sieht; in der Ebene gibt es nur z.
 * `seite` ist die Richtung, in der die Zahlen stehen: die der Achse, oder,
 * sieht man sie fast von vorne, quer zum Stab im Bild.
 */
function auftrag(r, s, achse) {
  const quer = Object.fromEntries(['y', 'z'].filter((x) => s.achsen[x]).map((x) => [x, imBild(r.v, s.achsen[x])]));
  const a = quer[achse || (quer.y?.f > quer.z.f ? 'y' : 'z')];
  const d = [a.r[0] * a.f, a.r[1] * a.f];
  if (a.f > 0.2) return { d, seite: a.r };
  const t = imBild(r.v, s.achsen.x).r;
  const n = [-t[1], t[0]];
  return { d, seite: skalar(n, a.r) < 0 ? [-n[0], -n[1]] : n };
}

function linie(r, p, q, klasse) {
  const [a, b] = [r.bild(p), r.bild(q)];
  return svgEl('path', { d: `M${a[0].toFixed(1)} ${a[1].toFixed(1)} L${b[0].toFixed(1)} ${b[1].toFixed(1)}`, class: klasse });
}

export const pfad = (punkte) => punkte.map((p, i) => `${i ? 'L' : 'M'}${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(' ');

function schrift(x, y, inhalt, klasse = 'bs-d-text', anker = 'middle') {
  const t = svgEl('text', { x: x.toFixed(1), y: y.toFixed(1), 'text-anchor': anker, class: klasse });
  t.textContent = inhalt;
  return t;
}

/** Ein leeres Bild mit dem System -- im Raum unten links die Achsen, wie man sie sieht. */
function bildflaeche(r, staebe) {
  const svg = svgEl('svg', { viewBox: `0 0 ${BREITE} ${r.hoehe}`, class: 'bs-diagramm' });
  const g = svgEl('g');
  for (const s of Object.values(staebe)) g.append(linie(r, amStab(s, 0), amStab(s, s.L), 'bs-d-system'));
  svg.append(g);
  if (r.v.basis) svg.append(achsenkreuz(r.v, r.achsen));
  return svg;
}

// ===========================================================================
// Die Bilder
// ===========================================================================

/** Ob zwei Stellen eines Stabs dieselbe sind -- auf ein Tausendstel seiner Länge. */
const gleicheStelle = (s, a, b) => Math.abs(a - b) <= 1e-3 * s.L;

/**
 * Wie gross eine Zahl im Bild ist, nachgemessen -- JetBrains Mono zu 13 px
 * (stil.css): je Zeichen die Breite, dazu wie weit die Schrift über und
 * unter ihre Grundlinie reicht, mit der kleineren Stelle bis unter deren
 * Zeile.
 */
const ZEICHEN = 7.1;
const OBEN = 12;
const UNTEN = 4;
const UNTEN_MIT_STELLE = 16;

/** Je Bild die Kästen der Zahlen, die schon darin stehen: links, oben, rechts, unten. */
const belegt = new WeakMap();
/** Wie viel Fläche zwei Kästen gemeinsam haben. */
const deckung = (a, b) => Math.max(0, Math.min(a[2], b[2]) - Math.max(a[0], b[0]))
  * Math.max(0, Math.min(a[3], b[3]) - Math.max(a[1], b[1]));

/**
 * Rückt eine Beschriftung des Bilds `svg` -- ihre Zeilen, die erste die
 * Zahl --, senkrecht, bis sie keine frühere deckt: an einer Ecke, wo
 * zwei Stäbe enden, im Raum, wo f_y und f_z nahe beieinander liegen, an
 * einem Lager mit mehreren Kräften. Zuerst in halben Höhen in Richtung
 * `weg` (1 nach unten, -1 nach oben), höchstens dreimal ihre Höhe, dann in
 * die andere; sonst dorthin, wo sie am wenigsten deckt. Wie gross sie ist,
 * schätzt sie aus der Zahl ihrer Zeichen.
 */
function freistellen(svg, zeilen, weg = 1) {
  const [erste] = zeilen;
  const x = Number(erste.getAttribute('x'));
  const y0 = Number(erste.getAttribute('y'));
  // Ein Zeichen Luft je Seite: «-24.9» und «-2.8» dicht an dicht läsen sich als eine Zahl.
  const breite = (Math.max(...zeilen.map((t) => t.textContent.length)) + 2) * ZEICHEN;
  const anker = erste.getAttribute('text-anchor');
  const links = anker === 'middle' ? x - breite / 2 : (anker === 'end' ? x + ZEICHEN - breite : x - ZEICHEN);
  const tiefe = zeilen.length > 1 ? UNTEN_MIT_STELLE : UNTEN;
  const kasten = (y) => [links, y - OBEN, links + breite, y + tiefe];
  const kaesten = belegt.get(svg) || [];
  belegt.set(svg, kaesten);
  const gedeckt = (y) => kaesten.reduce((summe, k) => summe + deckung(k, kasten(y)), 0);
  const schritte = [1, 2, 3, 4, 5, 6];
  const y = [...schritte, ...schritte.map((i) => -i)].map((i) => y0 + (weg * i * (OBEN + tiefe)) / 2)
    .reduce((beste, yi) => (gedeckt(yi) < gedeckt(beste) ? yi : beste), y0);
  kaesten.push(kasten(y));
  for (const t of zeilen) t.setAttribute('y', (Number(t.getAttribute('y')) + y - y0).toFixed(1));
}

/**
 * Ein Wert im Bild: die Zahl neben dem Punkt `p`, auf der Seite `n` -- mit
 * einem Punkt, wenn er ein Extremwert ist, und im Feld darunter seiner
 * Stelle, «x = 2.00 m»; längs eines Schnitts heisst sie s (`buchstabe`).
 * Deckt sie eine frühere, rückt sie vom Punkt weg (`freistellen`).
 */
export function anschreiben(svg, p, n, text, {
  punkt = false, stelle = null, klasse = '', buchstabe = 'x',
} = {}) {
  if (punkt) svg.append(svgEl('circle', { cx: p[0].toFixed(1), cy: p[1].toFixed(1), r: 3.2, class: `bs-d-extrem ${klasse}` }));
  const [x, y] = [p[0] + n[0] * 11, p[1] + n[1] * 11 + 4];
  const zeilen = [schrift(x, y, text)];
  if (stelle !== null) zeilen.push(schrift(x, y + 12, `${buchstabe} = ${fest(stelle, 2)} m`, 'bs-d-text bs-d-stelle'));
  svg.append(...zeilen);
  // Steht die Zahl über dem Punkt, rückt sie nach oben, sonst nach unten.
  freistellen(svg, zeilen, n[1] < -0.1 ? -1 : 1);
}

/**
 * Ein Verlauf: je Stab die Fläche zwischen Stab und Ordinate. Angeschrieben
 * die Werte an den Enden und der grösste und der kleinste -- `extreme` vom
 * Kern, je Stab und Grösse `{kleinst: [x, v], groesst: [x, v], massgebend:
 * [x, v]}`. `g`: die Grösse aus dem Katalog mit ihrem Feld, ihrer Achse und
 * ihrer Farbe.
 */
function verlaufsbild(r, daten, g, extreme) {
  const svg = bildflaeche(r, daten.staebe);
  const alle = Object.values(daten.staebe).flatMap((s) => s.proben.map((p) => Math.abs(p[g.feld])));
  const groesste = Math.max(0, ...alle);
  const k = groesste > 1e-9 ? AUSSCHLAG / groesste : 0;
  for (const [name, s] of Object.entries(daten.staebe)) {
    const { d, seite: n } = auftrag(r, s, g.achse);
    const ordinate = (x, v) => {
      const [bx, by] = r.bild(amStab(s, x));
      return [bx + d[0] * k * v, by + d[1] * k * v];
    };
    const basis = s.proben.map((p) => r.bild(amStab(s, p.x)));
    const kurve = s.proben.map((p) => ordinate(p.x, p[g.feld]));
    svg.append(svgEl('path', { d: `${pfad([...kurve, ...basis.reverse()])} Z`, class: `bs-d-flaeche ${g.klasse}` }));
    svg.append(svgEl('path', { d: pfad(kurve), class: `bs-d-kurve ${g.klasse}` }));
    const e = extreme[name]?.[g.feld];
    const spitzen = e ? [e.groesst, e.kleinst] : [];
    const zaehlt = (v) => Math.abs(v) >= groesste * 0.01;
    const seite = (v) => (v >= 0 ? n : [-n[0], -n[1]]);
    const enden = [[0, s.proben[0][g.feld]], [s.L, s.proben[s.proben.length - 1][g.feld]]];
    for (const [x, v] of enden) {
      if (!zaehlt(v)) continue;
      const istSpitze = spitzen.some(([xs, vs]) => gleicheStelle(s, xs, x) && vs === v);
      anschreiben(svg, ordinate(x, v), seite(v), fest(v, g.stellen), { punkt: istSpitze, klasse: g.klasse });
    }
    // Ein Extremwert im Feld bekommt seinen Punkt und seine Stelle; einer
    // an einem Ende steht schon dort.
    const gezeigt = [];
    for (const [x, v] of spitzen) {
      if (!zaehlt(v) || enden.some(([xe]) => gleicheStelle(s, xe, x))) continue;
      if (gezeigt.some((xg) => gleicheStelle(s, xg, x))) continue;
      gezeigt.push(x);
      anschreiben(svg, ordinate(x, v), seite(v), fest(v, g.stellen), { punkt: true, stelle: x, klasse: g.klasse });
    }
  }
  return svg;
}

/**
 * Die Verschiebung: das System verschoben, überhöht -- das unverformte blass
 * darunter. Je Stab angeschrieben die massgebenden Durchbiegungen gegen die
 * Sehne, mit Punkt und Stelle -- `extreme` vom Kern, wie beim Verlauf; in
 * der Ebene w, im Raum f_y und f_z, die nicht verschwinden. Die grösste
 * Verschiebung, auf die überhöht wird, kommt auch vom Kern.
 */
function verformungsbild(r, daten, extreme, e) {
  const svg = bildflaeche(r, daten.staebe);
  const groesste = daten.groesste_verschiebung;
  // Überhöht, bis die grösste Verschiebung ein Zwölftel des Systems ist.
  const faktor = groesste > 1e-12 ? (r.groesse / 12) / (groesste / 1000) : 0;
  const verschoben = (lage, u) => r.bild(lage.map((w, i) => w + (faktor * u[i]) / 1000));
  const durchbiegungen = Object.entries(daten.staebe).flatMap(([name, s]) => e.durchbiegungen.map(({ feld, achse }) => {
    const w = extreme[name]?.[feld];
    if (!w) return null;
    const [x, v] = w.massgebend;
    return { s, x, v, g: e.groessen[feld], achse };
  })).filter(Boolean);
  const groessteW = Math.max(0, ...durchbiegungen.map((d) => Math.abs(d.v)));
  // Der Massstab unten rechts steht zuerst fest -- die Zahlen weichen ihm
  // aus --, gezeichnet wird er zuletzt, über allem.
  const massstab = schrift(BREITE - 8, r.hoehe - 8,
    faktor ? `grösste Verschiebung ${fest(groesste, 2)} mm · überhöht ${Math.round(faktor)}-fach` : 'keine Verschiebung',
    'bs-d-text bs-d-zusatz', 'end');
  freistellen(svg, [massstab]);
  for (const s of Object.values(daten.staebe)) {
    svg.append(svgEl('path', { d: pfad(s.proben.map((p) => verschoben(amStab(s, p.x), p.u))), class: 'bs-d-verformt' }));
  }
  // Nur, was zählt: ein Stab, der sich bloss mitbewegt, biegt sich kaum.
  for (const { s, x, v, g, achse } of durchbiegungen) {
    if (Math.abs(v) < Math.max(1e-3, groessteW * 0.05)) continue;
    // Ein positiver Wert biegt zur Achse -- die Zahl steht aussen davor.
    const { seite: n } = auftrag(r, s, achse);
    anschreiben(svg, verschoben(amStab(s, x), verschiebungBei(s, x)), v >= 0 ? n : [-n[0], -n[1]],
      wertText(g, v), { punkt: true, stelle: x, klasse: 'bs-d-w' });
  }
  for (const w of Object.values(daten.knoten)) {
    const [x, y] = verschoben(w.lage, w.u);
    svg.append(svgEl('circle', { cx: x.toFixed(1), cy: y.toFixed(1), r: 2.5, class: w.unbestimmt ? 'bs-d-knoten ist-unbestimmt' : 'bs-d-knoten' }));
  }
  svg.append(massstab);
  return svg;
}

/**
 * Die Lagerkräfte: je Lager seine Kräfte und Momente auf das Tragwerk, wie
 * der Katalog sie nennt -- eine Kraft als Pfeil in ihrer Achse, ein Moment
 * um seine; was man von vorne sieht, als Kreis oder Bogen (bs_symbole.js).
 */
function lagerbild(r, daten, lagerkraefte, e) {
  const svg = bildflaeche(r, daten.staebe);
  const richtung = (achse) => e.achsen.map((a) => (a === achse ? 1 : 0));
  for (const l of lagerkraefte) {
    const w = l.knoten && daten.knoten[l.knoten];
    if (!w) continue;
    const p = r.bild(w.lage);
    for (const g of e.lagerkraefte) {
      const wert = l[g.zeichen];
      if (Math.abs(wert) <= 1e-6) continue;
      const achse = g.achse && richtung(g.achse);
      const zeichen = g.moment
        ? moment(r.v, p, achse, wert, `${fest(wert, g.stellen)} ${g.einheit}`, 'bs-last bs-reaktion')
        : kraft(p, imBild(r.v, achse), wert, 34, `${fest(Math.abs(wert), g.stellen)} ${g.einheit}`, 'bs-last bs-reaktion');
      svg.append(zeichen);
      freistellen(svg, [zeichen.querySelector('text')]);
    }
  }
  return svg;
}

// ===========================================================================
// Fahren mit der Maus
// ===========================================================================

/** Ein Wert an der Stelle x eines Stabs -- zwischen zwei Proben gerade verbunden; `wert(probe)` liest ihn. */
function zwischen(proben, x, wert) {
  for (let i = 1; i < proben.length; i += 1) {
    const [a, b] = [proben[i - 1], proben[i]];
    if (x >= a.x && x <= b.x) {
      const t = b.x > a.x ? (x - a.x) / (b.x - a.x) : 0;
      return wert(a) + (wert(b) - wert(a)) * t;
    }
  }
  return wert(proben[proben.length - 1]);
}

/** Die Verschiebung an der Stelle x eines Stabs, in mm je Achse des Systems. */
const verschiebungBei = (s, x) => s.proben[0].u.map((_, i) => zwischen(s.proben, x, (p) => p.u[i]));

/** «u_x = 1.20 mm   u_z = −3.40 mm» */
const verschiebungText = (e, u) => e.achsen.map((a, i) => `u_${a} = ${fest(u[i], 2)} mm`).join('   ');

/**
 * Was unter dem Zeiger liegt: ein Knoten -- seine Verschiebung und Drehung
 * --, sonst die nächste Stelle eines Stabs und ihr Wert. `zeilen(stab, x)`
 * sagt, was an einer Stelle steht.
 */
function finden(r, daten, e, punkt, zeilen) {
  for (const [k, w] of Object.entries(daten.knoten)) {
    const [x, y] = r.bild(w.lage);
    if (Math.hypot(punkt[0] - x, punkt[1] - y) <= 10) {
      const drehung = w.unbestimmt ? daten.unbestimmt_text
        : e.drehungen.map((z, i) => `${z} = ${fest(w.phi[i], 3)} mrad`).join('   ');
      return { ort: [x, y], text: [`Knoten ${k}`, verschiebungText(e, w.u), drehung] };
    }
  }
  let beste = null;
  for (const [name, s] of Object.entries(daten.staebe)) {
    const [ax, ay] = r.bild(amStab(s, 0));
    const [bx, by] = r.bild(amStab(s, s.L));
    const l2 = (bx - ax) ** 2 + (by - ay) ** 2 || 1;
    const t = Math.max(0, Math.min(1, ((punkt[0] - ax) * (bx - ax) + (punkt[1] - ay) * (by - ay)) / l2));
    const q = [ax + t * (bx - ax), ay + t * (by - ay)];
    const d = Math.hypot(punkt[0] - q[0], punkt[1] - q[1]);
    if (d <= AUSSCHLAG + 6 && (!beste || d < beste.d)) beste = { d, name, s, x: t * s.L, q };
  }
  if (!beste) return null;
  return { ort: beste.q, text: [`${beste.name} bei x = ${fest(beste.x, 2)} m`, ...zeilen(beste.s, beste.x)] };
}

/**
 * Hängt das Fahren mit der Maus an ein Bild: ein Zettel und ein Punkt an
 * der Stelle. `finden(punkt)` sagt, was unter dem Zeiger liegt -- `{ort,
 * text}` in Bildpunkten und Zeilen, oder null.
 */
export function zeigerEinrichten(huelle, svg, finden) {
  const zettel = el('div.bs-zettel', { hidden: true });
  const marke = svgEl('circle', { r: 4, class: 'bs-d-marke', visibility: 'hidden' });
  svg.append(marke);
  huelle.append(zettel);
  const zeigen = (ereignis) => {
    const rahmen = svg.getBoundingClientRect();
    if (!rahmen.width) return;
    const f = svg.viewBox.baseVal.width / rahmen.width;
    const punkt = [(ereignis.clientX - rahmen.left) * f, (ereignis.clientY - rahmen.top) * f];
    const treffer = finden(punkt);
    if (!treffer) {
      zettel.hidden = true;
      marke.setAttribute('visibility', 'hidden');
      return;
    }
    zettel.replaceChildren(...treffer.text.map((t) => el('div', { text: t })));
    zettel.hidden = false;
    marke.setAttribute('cx', treffer.ort[0].toFixed(1));
    marke.setAttribute('cy', treffer.ort[1].toFixed(1));
    marke.setAttribute('visibility', 'visible');
    const links = (treffer.ort[0] / f) + 12;
    zettel.style.left = `${Math.min(links, rahmen.width - 190)}px`;
    zettel.style.top = `${treffer.ort[1] / f + 12}px`;
  };
  svg.addEventListener('pointermove', zeigen);
  svg.addEventListener('pointerdown', zeigen);
  svg.addEventListener('pointerleave', () => {
    zettel.hidden = true;
    marke.setAttribute('visibility', 'hidden');
  });
}

// ===========================================================================
// Blätter
// ===========================================================================

/** Je Diagramm im Raum seine Ansicht -- am Eintrag der Zeile, nicht im Projekt. */
const ansichten = new WeakMap();

/** Der Schalter über einem Diagramm im Raum: aus welcher Richtung es das System zeigt. */
function ansichtsschalter(zeile, gewaehlt) {
  return wahlSchalter({
    werte: ANSICHTEN.map((x) => ({ wert: x.name, beschriftung: x.text, titel: x.titel })),
    gewaehlt, titel: 'Aus welcher Richtung das Diagramm das System zeigt',
    setzen: (name) => { ansichten.set(zeile, name); aendern({}, 'diagramm'); },
    klasse: '.bs-d-ansicht',
  });
}

/**
 * Ein Diagramm der Statik-Analyse als Karte: der Fall der Zeile, die Grösse
 * der Zeile. Über dem Diagramm sein Titel und der Fall, im Raum dazu die
 * Wahl der Ansicht.
 */
function diagrammKarte(kennung, system, zeile) {
  const art = systemart(kennung);
  const e = systemkatalog(art, 'ergebnisse');
  const groesse = systemkatalog(art, 'diagrammgroessen').find((g) => g.wert === zeile.groesse);
  const titel = groesse?.titel || zeile.groesse;
  const fall = fallname(system, zeile.fall);
  if (fall === null) {
    return karte(titel, [leerzustand('Kein Fall gewählt.',
      'Unter «Statik-Analyse» einen Lastfall oder eine Kombination wählen.')]);
  }
  const eintrag = antwortZu(kennung, fall,
    (f) => api.balkensystemVerlauf(zustand.projekt, kennung, f));
  if (eintrag.fehler) return karte(`${titel} – ${fall}`, [el('p.hinweis.hinweis-warnung', { text: eintrag.fehler })]);
  const antwort = eintrag.daten || eintrag.alt;
  const daten = antwort?.verlauf;
  if (!daten) return karte(`${titel} – ${fall}`, [leerzustand('Diagramm wird gerechnet …')]);
  const raum = e.achsen.length === 3;
  const ansicht = ANSICHTEN.find((x) => x.name === ansichten.get(zeile)) || ANSICHTEN[0];
  const r = bildrahmen(daten.staebe, raum ? basisAus(ansicht) : null, e.achsen);
  const uebersicht = (antwort.uebersicht?.faelle || []).find((f) => f.name === daten.fall);
  const extreme = uebersicht?.staebe || {};
  let svg;
  let zeilen = (s, x) => [verschiebungText(e, verschiebungBei(s, x)),
    `${e.durchbiegungen.map(({ feld }) => wertText(e.groessen[feld], zwischen(s.proben, x, (p) => p[feld]))).join('   ')} gegen die Sehne`];
  const unten = [];
  if (zeile.groesse === 'verschiebung') {
    svg = verformungsbild(r, daten, extreme, e);
  } else if (zeile.groesse === 'lagerkraefte') {
    const lager = uebersicht?.lagerkraefte || [];
    svg = lagerbild(r, daten, lager, e);
    // Was keinen Knoten hat -- eine Stelle auf einem Stab, die Summe von
    // Linienlager oder Bettung --, steht unter dem Bild. Ohne sie ginge das
    // Gleichgewicht am Bildschirm nicht auf.
    unten.push(...lager.filter((l) => !l.knoten).map((l) => el('p.bs-einheiten', {
      text: `${l.wo}: ${e.lagerkraefte.map((g) => wertText(g, l[g.zeichen])).join(' · ')}`,
    })));
    if (lager.some((l) => l.summe)) unten.push(el('p.bs-einheiten', { text: antwort.uebersicht.summen_text }));
  } else {
    const g = { ...e.groessen[groesse.feld], feld: groesse.feld, achse: groesse.achse, klasse: FARBEN[groesse.feld.split('_')[0]] };
    svg = verlaufsbild(r, daten, g, extreme);
    zeilen = (s, x) => [wertText(g, zwischen(s.proben, x, (p) => p[g.feld]))];
  }
  const huelle = el('div.bs-diagramm-huelle', {}, [svg]);
  zeigerEinrichten(huelle, svg, (punkt) => finden(r, daten, e, punkt, zeilen));
  return karte(`${titel} – ${daten.fall}`, [huelle, ...unten], {
    klasse: eintrag.daten ? '' : 'ist-veraltet', zusatz: raum ? ansichtsschalter(zeile, ansicht.name) : null,
  });
}

/**
 * Die Diagramme eines Systems -- je Zeile der Statik-Analyse eine Karte. Das
 * Panel darum baut bericht.js.
 */
export function systemKarten(kennung) {
  const system = eintragVon(kennung);
  const uebersicht = zustand.loesung?.zeichendaten?.[kennung]?.uebersicht;
  if (uebersicht && !uebersicht.gueltig) {
    return [karte(null, (uebersicht.meldungen || []).filter((m) => m.fehler)
      .map((m) => el('p.hinweis.hinweis-warnung', { text: m.text })))];
  }
  if (!system?.diagramme?.length) {
    return [karte(null, [leerzustand('Noch kein Diagramm.',
      'Anlegen unter «Statik-Analyse» mit «+ Diagramm».')])];
  }
  return system.diagramme.map((zeile) => diagrammKarte(kennung, system, zeile));
}

// ===========================================================================
// Zusammenfassung
// ===========================================================================

/** Ein Grenzwert über alle Stäbe vom Kern, `{stab, x, wert}` -- mit Stab und Stelle. */
function wertzelle(w, stellen) {
  return el('td.bs-zahl', { title: `${w.stab} bei x = ${fest(w.x, 2)} m` }, [
    fest(w.wert, stellen), el('span.bs-wo', { text: ` ${w.stab}` })]);
}

/** «N_min», «M_y,max» -- ein Grenzwert im Kopf der Tabelle. */
const grenzname = (zeichen, wo) => (zeichen.includes('_') ? `${zeichen},${wo}` : `${zeichen}_${wo}`);

/**
 * Welche Einheiten die Tabelle hat, je Einheit ihre Grössen: «N, V in kN ·
 * M in kNm · w in mm gegen die Sehne · …».
 */
function einheitenText(e) {
  const gruppen = new Map();
  for (const feld of e.schnittgroessen) {
    const g = e.groessen[feld];
    gruppen.set(g.einheit, [...(gruppen.get(g.einheit) || []), g.zeichen]);
  }
  const biegung = e.durchbiegungen.map(({ feld }) => e.groessen[feld]);
  return [
    ...[...gruppen].map(([einheit, zeichen]) => `${zeichen.join(', ')} in ${einheit}`),
    `${biegung.map((g) => g.zeichen).join(', ')} in ${biegung[0].einheit} gegen die Sehne`,
    'der Stab mit dem Wert steht klein daneben',
  ].join(' · ');
}

/**
 * Die Zusammenfassung eines Systems als Karten: Meldungen, je Fall die
 * Grenzwerte, die Lagerkräfte. Das Panel darum baut bericht.js.
 */
export function systemZusammenfassung(kennung) {
  const u = zustand.loesung?.zeichendaten?.[kennung]?.uebersicht;
  if (!u?.gerechnet) return [karte(null, [leerzustand('Noch nicht gerechnet.')])];
  const meldungen = (u.meldungen || []).map((m) => el('p', {
    class: m.fehler ? 'hinweis hinweis-warnung' : 'hinweis', text: m.text,
  }));
  // Ein System, das nicht rechnet, hat keine Fälle -- auch mit Lastfällen:
  // dann sagen es seine Meldungen, nicht «Kein Lastfall.».
  if (!u.gueltig) return [karte(null, meldungen)];
  if (!u.faelle.length) return [karte(null, [...meldungen, leerzustand('Kein Lastfall.')])];
  const e = systemkatalog(systemart(kennung), 'ergebnisse');
  const schnitt = e.schnittgroessen.map((feld) => ({ feld, ...e.groessen[feld] }));
  const biegung = e.durchbiegungen.map(({ feld }) => ({ feld, ...e.groessen[feld] }));
  const kopf = ['Fall', ...schnitt.flatMap((g) => [grenzname(g.zeichen, 'min'), grenzname(g.zeichen, 'max')]),
    ...biegung.map((g) => grenzname(g.zeichen, 'max'))].map((t) => el('th', { text: t }));
  const zeilen = u.faelle.map((f) => el('tr', {}, [
    el('td', { text: f.name + (f.kombination ? ' (Kombination)' : '') }),
    ...schnitt.flatMap((g) => [wertzelle(f.grenzen[g.feld].kleinst, g.stellen),
      wertzelle(f.grenzen[g.feld].groesst, g.stellen)]),
    ...biegung.map((g) => wertzelle(f.grenzen[g.feld].massgebend, g.stellen)),
  ]));
  // Alle Zeilen, wie in der Herleitung -- auch die Summen von Linienlager
  // und Bettung. Mit den Knoten allein gingen die Kräfte nicht auf.
  const lagerzeilen = u.faelle.flatMap((f) => f.lagerkraefte.map((l) => el('tr', {}, [
    el('td', { text: f.name }), el('td', { text: l.wo }),
    ...e.lagerkraefte.map((g) => el('td.bs-zahl', { text: fest(l[g.zeichen], g.stellen) })),
  ])));
  const summen = u.faelle.some((f) => f.lagerkraefte.some((l) => l.summe));
  return [
    karte('Grenzwerte je Fall', [
      ...meldungen,
      el('p.bs-einheiten', { text: einheitenText(e) }),
      el('div.tabelle-huelle', {}, [el('table.bs-tabelle', {}, [el('thead', {}, [el('tr', {}, kopf)]), el('tbody', {}, zeilen)])]),
    ]),
    lagerzeilen.length ? karte('Lagerkräfte auf das Tragwerk', [
      el('div.tabelle-huelle', {}, [el('table.bs-tabelle', {}, [
        el('thead', {}, [el('tr', {}, ['Fall', 'Lager', ...e.lagerkraefte.map((g) => `${g.zeichen} [${g.einheit}]`)]
          .map((t) => el('th', { text: t })))]),
        el('tbody', {}, lagerzeilen),
      ])]),
      summen ? el('p.bs-einheiten', { text: u.summen_text }) : null,
    ]) : null,
  ];
}
