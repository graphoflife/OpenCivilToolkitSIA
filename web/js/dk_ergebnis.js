/**
 * dk_ergebnis.js -- die Ergebnisbilder einer Decke, rechts.
 *
 * Unter «Diagramme» je Zeile der Ergebnisse ein Bild: ihr Fall, Lastfall
 * oder Kombination, und ihre Grösse --
 *
 *   m_x, m_y, m_xy   die Momente je Meter in den Achsen x und y, auch wo
 *                    ein Streifen schief trägt (Benutzer, 2026-11-13);
 *   v_x, v_y, v_0    die Querkräfte je Meter und die Hauptquerkraft;
 *   Lager            je Linienlager der Verlauf seiner Kraft über die
 *                    Länge; darunter je Lager die Summe, eingespannt auch
 *                    das grösste Moment.
 *
 * Die Schnittkräfte liegen in Farbe über dem Grundriss: positiv rot,
 * negativ blau, weiss bei null -- je kräftiger, desto näher am grössten
 * Betrag. Eine Zelle hat den Wert an ihrem Schwerpunkt; in einem Streifen
 * ist er über die Breite gleich. Angeschrieben sind der grösste und der
 * kleinste Wert, mit Punkt an ihrer Stelle; über einer Zelle steht ihr Wert.
 *
 * Im Bild der Lager stehen nur ihre Namen, die Zahlen in der Tabelle
 * darunter: neben den Lagern deckten sie einander, wo zwei Lager nahe
 * beisammen liegen, und am Rand liefen sie aus dem Bild.
 *
 * Die Bilder kommen aus einer eigenen Anfrage (`decke_ergebnis`), erst wenn
 * jemand sie sehen will (fallantwort.js). Gerechnet wird hier nichts: Werte,
 * Extremstellen und Lagerkräfte kommen fertig aus dem Kern
 * (opencivil/web/deckendaten.py); hier stehen nur Lagen fürs Auge -- auf
 * welcher Seite eines Lagers sein Verlauf steht, wo eine Zahl.
 */

import { api } from './api.js';
import { karte, tabelle } from './bausteine.js';
import { nachBild, pfad, zahlText } from './cad_ansicht.js';
import { mitTitel } from './cad_app.js';
import { innen } from './cad_modell.js';
import { grundrissBild } from './dk_grundriss.js';
import { el, leerzustand, svgEl } from './dom.js';
import { antwortZu } from './fallantwort.js';
import { fallname } from './lastfaelle.js';
import { katalog, zustand } from './zustand.js';

/** Stellen der angeschriebenen Werte. */
const STELLEN = 1;
/** So weit steht der grösste Verlauf eines Linienlagers von ihm ab, in Bildpunkten. */
const AUSSCHLAG = 28;
/** Platz um die Decke, in Bildpunkten: für Zahlen am Rand -- beim Bild der Lager für die Verläufe und Namen. */
const RAND = { feld: 34, lager: AUSSCHLAG + 34 };

function text([x, y], inhalt, klasse, anker = 'start') {
  const t = svgEl('text', { x: x.toFixed(1), y: y.toFixed(1), class: klasse, 'text-anchor': anker });
  t.textContent = inhalt;
  return t;
}

/** Steht ein Wert als «0» da, wird er nicht angeschrieben. */
const nennbar = (wert) => zahlText(Math.abs(wert), STELLEN) !== '0';

// ===========================================================================
// Schnittkräfte
// ===========================================================================

/**
 * Die Farbskala eines Bilds: symmetrisch um null, so weit wie der grösste
 * Betrag -- nur positiv von weiss nach rot, nur negativ von blau nach weiss.
 * Die Extremwerte zählen mit: über einer Stütze liegen sie zwischen den
 * Schwerpunkten der Zellen.
 */
function skala(werte, extrem) {
  const alle = [...werte, ...(extrem ? [extrem.groesst.wert, extrem.kleinst.wert] : [])];
  const hoch = Math.max(0, ...alle);
  const tief = Math.min(0, ...alle);
  return { hoch, tief, weit: Math.max(hoch, -tief) };
}

/** Die Farbe eines Werts in der Skala. */
function farbe(wert, { weit }) {
  const t = weit > 0 ? Math.max(-1, Math.min(1, wert / weit)) : 0;
  return `color-mix(in srgb, var(${t < 0 ? '--feld-minus' : '--feld-plus'}) ${(100 * Math.abs(t)).toFixed(1)}%, var(--feld-null))`;
}

/** Die Zellen in ihrer Farbe -- über jeder ihr Wert. */
function zellen(v, ergebnis, groesse, s, zeichen, einheit) {
  const g = svgEl('g', { class: 'dk-zellen' });
  ergebnis.zellen.forEach((ecken, i) => {
    const wert = ergebnis.werte[groesse][i];
    const f = farbe(wert, s);
    g.append(mitTitel(svgEl('path', { d: pfad(v, ecken), class: 'dk-zelle', style: `fill: ${f}; stroke: ${f}` }),
      [`${zeichen} = ${zahlText(wert, STELLEN)} ${einheit}`]));
  });
  return g;
}

/** Der grösste und der kleinste Wert, je mit Punkt -- was als «0» dastünde, nicht. */
function extremwerte(v, ergebnis, groesse, einheit) {
  const e = ergebnis.extreme[groesse];
  if (!e) return [];
  const heraus = [];
  for (const [art, klasse] of [['groesst', 'ist-plus'], ['kleinst', 'ist-minus']]) {
    const { wert, ort } = e[art];
    if (!nennbar(wert) || (klasse === 'ist-plus' ? wert < 0 : wert > 0)) continue;
    const [x, y] = nachBild(v, ort);
    const links = x > v.breite - 90;
    heraus.push(
      svgEl('circle', { cx: x.toFixed(1), cy: y.toFixed(1), r: 3.5, class: `dk-extrem ${klasse}` }),
      text([x + (links ? -7 : 7), y - 7], `${zahlText(wert, STELLEN)} ${einheit}`, 'dk-extremtext',
        links ? 'end' : 'start'),
    );
  }
  return heraus;
}

/** Unter dem Bild, was die Farben heissen: von der kleinsten bis zur grössten Zahl der Skala. */
function farblegende(s, einheit) {
  const von = s.hoch > 0 && s.tief >= 0 ? 0 : -s.weit;
  const bis = s.tief < 0 && s.hoch <= 0 ? 0 : s.weit;
  const farben = [von < 0 ? 'var(--feld-minus)' : null, 'var(--feld-null)', bis > 0 ? 'var(--feld-plus)' : null]
    .filter(Boolean);
  return el('div.dk-farblegende', {}, [
    el('span', { text: zahlText(von, STELLEN) }),
    el('span.dk-farbbalken', { style: { background: `linear-gradient(to right, ${farben.join(', ')})` } }),
    el('span', { text: `${zahlText(bis, STELLEN)} ${einheit}` }),
  ]);
}

function feldInhalt(decke, daten, ergebnis, groesse) {
  const einheit = ergebnis.einheiten[groesse];
  const zeichen = katalog('decke', 'diagrammgroessen').find((g) => g.wert === groesse)?.beschriftung || groesse;
  const s = skala(ergebnis.werte[groesse], ergebnis.extreme[groesse]);
  const bild = grundrissBild(decke, daten, 'nichts', {
    rand: RAND.feld,
    unter: (v) => zellen(v, ergebnis, groesse, s, zeichen, einheit),
    oben: (v) => extremwerte(v, ergebnis, groesse, einheit),
  });
  return [el('div.gb-bildhuelle', {}, [bild]), farblegende(s, einheit)];
}

// ===========================================================================
// Lager
// ===========================================================================

/**
 * Auf welcher Seite eines Linienlagers sein Verlauf steht -- als Normale in
 * m: links von a → b, ausser dort liegt Platte und rechts nicht.
 */
function seite(decke, a, b) {
  const L = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1;
  const n = [-(b[1] - a[1]) / L, (b[0] - a[0]) / L];
  const mitte = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
  const lagen = new Map(decke.knoten.map((k) => [k.kennung, [k.x, k.y]]));
  const platten = decke.platten.map((p) => p.knoten.map((k) => lagen.get(k))).filter((p) => p.every(Boolean));
  const auf = (d) => platten.some((p) => innen([mitte[0] + d * n[0], mitte[1] + d * n[1]], p));
  return auf(0.05 * L) && !auf(-0.05 * L) ? [-n[0], -n[1]] : n;
}

/** Je Linienlager der Verlauf seiner Kraft und dahinter sein Name. */
function linienlager(v, decke, ergebnis) {
  const groesst = Math.max(0, ...ergebnis.linienlager.flatMap((l) => l.stufen.map((s) => Math.abs(s[2]))));
  const k = groesst > 0 ? AUSSCHLAG / groesst : 0;
  const heraus = [];
  for (const l of ergebnis.linienlager) {
    const L = Math.hypot(l.b[0] - l.a[0], l.b[1] - l.a[1]) || 1;
    const e = [(l.b[0] - l.a[0]) / L, (l.b[1] - l.a[1]) / L];
    const n = seite(decke, l.a, l.b);
    // Im Bild zeigt y nach unten: die Normale dort mit umgekehrtem y.
    const nb = [n[0], -n[1]];
    const am = (u, r) => {
      const [x, y] = nachBild(v, [l.a[0] + u * e[0], l.a[1] + u * e[1]]);
      return [x + r * k * nb[0], y + r * k * nb[1]];
    };
    const punkte = [am(0, 0), ...l.stufen.flatMap(([ua, ub, r]) => [am(ua, r), am(ub, r)]), am(L, 0)];
    const titel = l.stufen.filter((s) => s[1] > s[0]).map(([ua, ub, r, m]) => `${zahlText(ua, 2)} bis ${zahlText(ub, 2)} m: `
      + `r = ${zahlText(r, STELLEN)} kN/m${l.eingespannt ? `, m = ${zahlText(m, STELLEN)} kNm/m` : ''}`);
    heraus.push(mitTitel(svgEl('path', {
      d: `${punkte.map(([x, y], i) => `${i ? 'L' : 'M'}${x.toFixed(1)} ${y.toFixed(1)}`).join(' ')} Z`,
      class: 'dk-lagerverlauf',
    }), [`Linienlager ${l.name}`, ...titel]));
    // Hinter dem Verlauf, in der Mitte des Lagers: so weit draussen, wie er höchstens absteht.
    const [x, y] = am(L / 2, 0);
    const weg = AUSSCHLAG + 10;
    const anker = Math.abs(nb[0]) < 0.3 ? 'middle' : (nb[0] > 0 ? 'start' : 'end');
    heraus.push(text([x + weg * nb[0], y + weg * nb[1] + 4], l.name, 'dk-lagertext', anker));
  }
  return heraus;
}

/**
 * Je Lager eine Zeile: die Summe, beim Linienlager der Wert von r mit dem
 * grössten Betrag -- eingespannt auch das grösste Moment, als Betrag.
 */
function lagertabelle(ergebnis) {
  const eingespannt = ergebnis.linienlager.some((l) => l.eingespannt);
  const zahl = (wert) => zahlText(wert, STELLEN);
  const moment = (l) => (eingespannt ? [l?.eingespannt ? zahl(l.m_max) : '–'] : []);
  return tabelle(['Lager', 'F [kN]', 'r_max [kN/m]', ...(eingespannt ? ['|m|_max [kNm/m]'] : [])], [
    ...ergebnis.stuetzen.map((s) => [`${s.name} · Stütze`, zahl(s.F), '–', ...moment(null)]),
    ...ergebnis.linienlager.map((l) => [`${l.name} · Linienlager`, zahl(l.F), zahl(l.r_max), ...moment(l)]),
  ]);
}

function lagerInhalt(decke, daten, ergebnis) {
  const bild = grundrissBild(decke, daten, 'nichts', {
    rand: RAND.lager,
    oben: (v) => linienlager(v, decke, ergebnis),
  });
  return [
    el('div.gb-bildhuelle', {}, [bild]),
    lagertabelle(ergebnis),
    el('p.karte-hinweis', {
      text: 'Im Bild je Linienlager die Kraft r über seine Länge: was zwei Streifen auf dasselbe Stück geben, '
        + 'zählt zusammen. Das Moment eines eingespannten Rands steht nur als Betrag da.',
    }),
  ];
}

// ===========================================================================
// Karten
// ===========================================================================

/** Ein Bild der Ergebnisse als Karte: der Fall der Zeile, die Grösse der Zeile. */
function ergebnisKarte(kennung, decke, daten, zeile) {
  const titel = katalog('decke', 'diagrammgroessen').find((g) => g.wert === zeile.groesse)?.titel || zeile.groesse;
  const fall = fallname(decke, zeile.fall);
  if (fall === null) {
    return karte(titel, [leerzustand('Kein Fall gewählt.',
      'Unter «Ergebnisse» einen Lastfall oder eine Kombination wählen.')]);
  }
  const eintrag = antwortZu(kennung, fall, (f) => api.deckeErgebnis(zustand.projekt, kennung, f));
  if (eintrag.fehler) return karte(`${titel} – ${fall}`, [el('p.hinweis.hinweis-warnung', { text: eintrag.fehler })]);
  const ergebnis = (eintrag.daten || eintrag.alt)?.ergebnis;
  if (!ergebnis) return karte(`${titel} – ${fall}`, [leerzustand('Bild wird gerechnet …')]);
  const inhalt = zeile.groesse === 'lager' ? lagerInhalt(decke, daten, ergebnis)
    : feldInhalt(decke, daten, ergebnis, zeile.groesse);
  return karte(`${titel} – ${ergebnis.fall}`, inhalt,
    { klasse: eintrag.daten ? 'ist-breit' : 'ist-breit ist-veraltet' });
}

/**
 * Die Ergebnisbilder einer Decke -- je Zeile der Ergebnisse eine Karte.
 * `daten` ist, was der Kern mit jeder Rechnung zu ihr zeichnet: die Bänder
 * der Unterzüge kommen von dort.
 */
export function ergebnisKarten(kennung, decke, daten) {
  if (!decke.diagramme?.length) {
    return [karte(null, [leerzustand('Noch kein Ergebnisbild.', 'Anlegen unter «Ergebnisse» mit «+ Diagramm».')])];
  }
  return decke.diagramme.map((zeile) => ergebnisKarte(kennung, decke, daten, zeile));
}
