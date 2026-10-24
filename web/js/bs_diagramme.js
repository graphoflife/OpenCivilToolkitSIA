/**
 * bs_diagramme.js -- die Ergebnisse eines Balkensystems, rechts.
 *
 * Unter «Diagramme» je Zeile der Statik-Analyse ein Diagramm -- ihr Fall,
 * Lastfall oder Kombination, und ihre Grösse (Benutzer, 2026-10-23):
 *
 *   M, V, N       je Stab der Verlauf, quer zum Stab aufgetragen, positive
 *                 Werte auf der Seite der gestrichelten Faser -- das Moment
 *                 also auf der Zugseite;
 *   Verschiebung  das System verschoben, überhöht -- das unverformte blass;
 *   Verdrehung    je Stab die Verdrehung φ des Querschnitts, aufgetragen wie
 *                 ein Verlauf, im Gegenuhrzeigersinn positiv;
 *   Lagerkräfte   je Lager die Kräfte und das Moment auf das Tragwerk.
 *
 * Angeschrieben sind die Werte an den Enden und je Stab die grössten, an
 * ihrer Stelle ein Punkt, im Feld dazu die Stelle x -- bei der Verschiebung
 * die grösste Durchbiegung gegen die Sehne. Die Extremwerte rechnet der
 * Kern genau; sie stehen in seiner Übersicht, nicht in den Proben.
 *
 * Fahren mit der Maus -- auf dem Handy: Tippen -- über einen Knoten zeigt
 * seine Verschiebung und Drehung, oder «Verdrehung nicht bestimmbar, da keine
 * Steifigkeit»; über einem Stab den Wert an dieser Stelle.
 *
 * Unter «Zusammenfassung» je System eine Tabelle: je Fall die grössten und
 * kleinsten Schnittgrössen und Durchbiegungen und die Lagerkräfte -- aus der
 * Rechnung, die mit jeder Eingabe läuft.
 *
 * Die Verläufe kommen aus einer eigenen Anfrage (`balkensystem_verlauf`),
 * erst wenn jemand sie sehen will -- wie die Diagramme der
 * Querschnittsanalyse. Gerechnet wird hier nichts: die Werte kommen fertig
 * aus dem Kern, mit den Extremstellen; zwischen seinen dichten Proben wird
 * für die Anzeige beim Darüberfahren nur gerade verbunden.
 */

import { api } from './api.js';
import { karte } from './bausteine.js';
import { kraftpfeil, momentSymbol } from './bs_symbole.js';
import { abdruckVon } from './bs_zeichnung.js';
import { el, leerzustand, svgEl } from './dom.js';
import { aendern, zustand } from './zustand.js';

const BREITE = 640;
/** Wie weit die grösste Ordinate vom Stab absteht, in Bildpunkten. */
const AUSSCHLAG = 44;
/**
 * Platz rund um das System, in Bildpunkten: für die grösste Ordinate und
 * dahinter ihren Wert mit Stelle -- bis 2026-10-24 waren es 58, und der Wert
 * an einer äusseren Stütze war halb abgeschnitten.
 */
const RAND = AUSSCHLAG + 46;

/**
 * Die Verläufe: Feld in den Proben, Zeichen, Einheit, Stellen, Farbe -- der
 * Titel kommt aus dem Katalog.
 */
const GROESSEN = {
  N: { schluessel: 'N', zeichen: 'N', einheit: 'kN', stellen: 1, klasse: 'bs-d-n' },
  V: { schluessel: 'V', zeichen: 'V', einheit: 'kN', stellen: 1, klasse: 'bs-d-v' },
  M: { schluessel: 'M', zeichen: 'M', einheit: 'kNm', stellen: 1, klasse: 'bs-d-m' },
  verdrehung: { schluessel: 'phi', zeichen: 'φ', einheit: 'mrad', stellen: 2, klasse: 'bs-d-phi' },
};

/** «Kennung|Fall» -> {abdruck, fall, daten, alt, fehler, uhr}: die letzte Antwort je System und Fall. */
const vorrat = new Map();

const fest = (x, n) => (Math.abs(x) < 0.5 * 10 ** -n ? 0 : x).toFixed(n);

// ===========================================================================
// Anfrage
// ===========================================================================

/** Fragt nach den Verläufen -- erst, wenn gerade nicht gerechnet wird: dann liegt das System im Speicher des Kerns. */
function anfordern(schluessel, kennung, eintrag, verzug = 500) {
  clearTimeout(eintrag.uhr);
  eintrag.uhr = setTimeout(() => {
    if (vorrat.get(schluessel) !== eintrag) return;
    if (zustand.rechnetGerade) {
      anfordern(schluessel, kennung, eintrag);
      return;
    }
    api.balkensystemVerlauf(zustand.projekt, kennung, eintrag.fall).then((antwort) => {
      if (vorrat.get(schluessel) !== eintrag) return;
      eintrag.daten = antwort;
      aendern({}, 'diagramm');
    }).catch((fehler) => {
      if (vorrat.get(schluessel) !== eintrag) return;
      eintrag.fehler = fehler.message;
      aendern({}, 'diagramm');
    });
  }, verzug);
}

/**
 * Die Antwort des Kerns zu einem Fall -- neu angefragt, wenn es keine gibt
 * oder sie nicht mehr zum Projekt passt. Bis die neue da ist, gilt die alte.
 * Zeigen zwei Diagramme denselben Fall, teilen sie sich die Antwort.
 */
function antwortZu(kennung, fall) {
  const schluessel = `${kennung}|${fall}`;
  const abdruck = abdruckVon(kennung);
  let eintrag = vorrat.get(schluessel);
  if (!eintrag || eintrag.abdruck !== abdruck) {
    const alt = eintrag?.daten || eintrag?.alt || null;
    eintrag = { abdruck, fall, daten: null, alt, fehler: null, uhr: null };
    vorrat.set(schluessel, eintrag);
    anfordern(schluessel, kennung, eintrag, alt ? 500 : 80);
  }
  return eintrag;
}

// ===========================================================================
// Rahmen: vom System ins Bild
// ===========================================================================

/** Massstab und Lage im Bild -- x nach rechts, z nach oben, ringsum Platz für die Ordinaten. */
function bildrahmen(staebe) {
  const punkte = Object.values(staebe).flatMap((s) => [[s.x_a, s.z_a], [s.x_a + s.c * s.L, s.z_a + s.s * s.L]]);
  const xs = punkte.map((p) => p[0]);
  const zs = punkte.map((p) => p[1]);
  const [x0, x1, z0, z1] = [Math.min(...xs), Math.max(...xs), Math.min(...zs), Math.max(...zs)];
  const breite = Math.max(x1 - x0, 1e-9);
  const hoehe = Math.max(z1 - z0, 1e-9);
  let m = (BREITE - 2 * RAND) / breite;
  m = Math.min(m, 380 / hoehe);
  if (!Number.isFinite(m) || m <= 0) m = 50;
  const hoeheBild = Math.round(hoehe * m + 2 * RAND);
  const ox = BREITE / 2 - m * (x0 + x1) / 2;
  const oy = hoeheBild / 2 + m * (z0 + z1) / 2;
  return {
    m, hoehe: hoeheBild, groesse: Math.max(breite, hoehe),
    bild: ([x, z]) => [ox + m * x, oy - m * z],
  };
}

/** Ein Punkt eines Stabs an der Stelle x, in der Zeichnung. */
const amStab = (s, x) => [s.x_a + s.c * x, s.z_a + s.s * x];

/** Die Seite der gestrichelten Faser, im Bild -- in der Zeichnung (s, −c). */
const faserseite = (s) => [s.s, s.c];

function linie(r, p, q, klasse) {
  const [a, b] = [r.bild(p), r.bild(q)];
  return svgEl('path', { d: `M${a[0].toFixed(1)} ${a[1].toFixed(1)} L${b[0].toFixed(1)} ${b[1].toFixed(1)}`, class: klasse });
}

function schrift(x, y, inhalt, klasse = 'bs-d-text', anker = 'middle') {
  const t = svgEl('text', { x: x.toFixed(1), y: y.toFixed(1), 'text-anchor': anker, class: klasse });
  t.textContent = inhalt;
  return t;
}

function systemlinien(r, staebe) {
  const g = svgEl('g');
  for (const s of Object.values(staebe)) g.append(linie(r, amStab(s, 0), amStab(s, s.L), 'bs-d-system'));
  return g;
}

// ===========================================================================
// Die Bilder
// ===========================================================================

/** Ob zwei Stellen eines Stabs dieselbe sind -- auf ein Tausendstel seiner Länge. */
const gleicheStelle = (s, a, b) => Math.abs(a - b) <= 1e-3 * s.L;

/**
 * Ein Wert im Bild: die Zahl neben dem Punkt `p`, auf der Seite `n` -- mit
 * einem Punkt, wenn er ein Extremwert ist, und im Feld darunter seiner
 * Stelle.
 */
function anschreiben(svg, p, n, text, { punkt = false, stelle = null, klasse = '' } = {}) {
  if (punkt) svg.append(svgEl('circle', { cx: p[0].toFixed(1), cy: p[1].toFixed(1), r: 3.2, class: `bs-d-extrem ${klasse}` }));
  const [x, y] = [p[0] + n[0] * 11, p[1] + n[1] * 11 + 4];
  svg.append(schrift(x, y, text));
  if (stelle !== null) svg.append(schrift(x, y + 12, `x = ${fest(stelle, 2)} m`, 'bs-d-text bs-d-stelle'));
}

/**
 * Ein Verlauf: je Stab die Fläche zwischen Stab und Ordinate. Angeschrieben
 * die Werte an den Enden und der grösste und der kleinste -- `extreme` vom
 * Kern, je Stab `{kleinst: [x, v], groesst: [x, v]}`.
 */
function verlaufsbild(r, daten, groesse, extreme) {
  const svg = svgEl('svg', { viewBox: `0 0 ${BREITE} ${r.hoehe}`, class: 'bs-diagramm' });
  svg.append(systemlinien(r, daten.staebe));
  const feld = groesse.schluessel;
  const alle = Object.values(daten.staebe).flatMap((s) => s.proben.map((p) => Math.abs(p[feld])));
  const groesste = Math.max(0, ...alle);
  const k = groesste > 1e-9 ? AUSSCHLAG / groesste : 0;
  for (const [name, s] of Object.entries(daten.staebe)) {
    const n = faserseite(s);
    const ordinate = (x, v) => {
      const [bx, by] = r.bild(amStab(s, x));
      return [bx + n[0] * k * v, by + n[1] * k * v];
    };
    const basis = s.proben.map((p) => r.bild(amStab(s, p.x)));
    const kurve = s.proben.map((p) => ordinate(p.x, p[feld]));
    const flaeche = [...kurve, ...basis.reverse()];
    svg.append(svgEl('path', {
      d: `${flaeche.map((p, i) => `${i ? 'L' : 'M'}${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(' ')} Z`,
      class: `bs-d-flaeche ${groesse.klasse}`,
    }));
    svg.append(svgEl('path', {
      d: kurve.map((p, i) => `${i ? 'L' : 'M'}${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(' '),
      class: `bs-d-kurve ${groesse.klasse}`,
    }));
    const e = extreme[name]?.[feld];
    const spitzen = e ? [e.groesst, e.kleinst] : [];
    const zaehlt = (v) => Math.abs(v) >= groesste * 0.01;
    const seite = (v) => (v >= 0 ? n : [-n[0], -n[1]]);
    const enden = [[0, s.proben[0][feld]], [s.L, s.proben[s.proben.length - 1][feld]]];
    for (const [x, v] of enden) {
      if (!zaehlt(v)) continue;
      const istSpitze = spitzen.some(([xs, vs]) => gleicheStelle(s, xs, x) && vs === v);
      anschreiben(svg, ordinate(x, v), seite(v), fest(v, groesse.stellen),
        { punkt: istSpitze, klasse: groesse.klasse });
    }
    // Ein Extremwert im Feld bekommt seinen Punkt und seine Stelle; einer
    // an einem Ende steht schon dort.
    const gezeigt = [];
    for (const [x, v] of spitzen) {
      if (!zaehlt(v) || enden.some(([xe]) => gleicheStelle(s, xe, x))) continue;
      if (gezeigt.some((xg) => gleicheStelle(s, xg, x))) continue;
      gezeigt.push(x);
      anschreiben(svg, ordinate(x, v), seite(v), fest(v, groesse.stellen),
        { punkt: true, stelle: x, klasse: groesse.klasse });
    }
  }
  return svg;
}

/**
 * Die Verschiebung: das System verschoben, überhöht -- das unverformte blass
 * darunter. Je Stab angeschrieben die grösste Durchbiegung gegen die Sehne,
 * mit Punkt und Stelle -- `extreme` vom Kern, wie beim Verlauf.
 */
function verformungsbild(r, daten, extreme) {
  const svg = svgEl('svg', { viewBox: `0 0 ${BREITE} ${r.hoehe}`, class: 'bs-diagramm' });
  svg.append(systemlinien(r, daten.staebe));
  const groesste = Math.max(0, ...Object.values(daten.staebe)
    .flatMap((s) => s.proben.map((p) => Math.hypot(p.ux, p.uz))));
  // Überhöht, bis die grösste Verschiebung ein Zwölftel des Systems ist.
  const faktor = groesste > 1e-12 ? (r.groesse / 12) / (groesste / 1000) : 0;
  const verschoben = (s, x) => {
    const [px, pz] = amStab(s, x);
    return r.bild([px + faktor * zwischen(s.proben, x, 'ux') / 1000,
      pz + faktor * zwischen(s.proben, x, 'uz') / 1000]);
  };
  const durchbiegungen = Object.entries(daten.staebe).map(([name, s]) => {
    const w = extreme[name]?.w;
    if (!w) return null;
    const [x, v] = Math.abs(w.groesst[1]) >= Math.abs(w.kleinst[1]) ? w.groesst : w.kleinst;
    return { s, x, v };
  }).filter(Boolean);
  const groessteW = Math.max(0, ...durchbiegungen.map((d) => Math.abs(d.v)));
  for (const s of Object.values(daten.staebe)) {
    const punkte = s.proben.map((p) => verschoben(s, p.x));
    svg.append(svgEl('path', {
      d: punkte.map((p, i) => `${i ? 'L' : 'M'}${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(' '),
      class: 'bs-d-verformt',
    }));
  }
  // Nur, was zählt: ein Stab, der sich bloss mitbewegt, biegt sich kaum.
  for (const { s, x, v } of durchbiegungen) {
    if (Math.abs(v) < Math.max(1e-3, groessteW * 0.05)) continue;
    // w > 0 biegt zur gestrichelten Faser -- die Zahl steht aussen davor.
    const n = faserseite(s);
    const seite = v >= 0 ? n : [-n[0], -n[1]];
    anschreiben(svg, verschoben(s, x), seite, `w = ${fest(v, 2)} mm`,
      { punkt: true, stelle: x, klasse: 'bs-d-w' });
  }
  for (const w of Object.values(daten.knoten)) {
    const [x, y] = r.bild([w.x + faktor * w.ux / 1000, w.z + faktor * w.uz / 1000]);
    svg.append(svgEl('circle', { cx: x.toFixed(1), cy: y.toFixed(1), r: 2.5, class: w.unbestimmt ? 'bs-d-knoten ist-unbestimmt' : 'bs-d-knoten' }));
  }
  svg.append(schrift(BREITE - 8, r.hoehe - 8,
    faktor ? `grösste Verschiebung ${fest(groesste, 2)} mm · überhöht ${Math.round(faktor)}-fach` : 'keine Verschiebung',
    'bs-d-text bs-d-zusatz', 'end'));
  return svg;
}

/** Die Lagerkräfte: je Lager Pfeile und Moment, auf das Tragwerk. */
function lagerbild(r, daten, lagerkraefte) {
  const svg = svgEl('svg', { viewBox: `0 0 ${BREITE} ${r.hoehe}`, class: 'bs-diagramm' });
  svg.append(systemlinien(r, daten.staebe));
  for (const l of lagerkraefte) {
    if (!l.knoten) continue;
    const w = daten.knoten[l.knoten];
    if (!w) continue;
    const p = r.bild([w.x, w.z]);
    if (Math.abs(l.R_z) > 1e-6) {
      svg.append(kraftpfeil(p, [0, l.R_z > 0 ? -1 : 1], 34, `${fest(Math.abs(l.R_z), 1)} kN`, 'bs-last bs-reaktion'));
    }
    if (Math.abs(l.R_x) > 1e-6) {
      svg.append(kraftpfeil(p, [l.R_x > 0 ? 1 : -1, 0], 34, `${fest(Math.abs(l.R_x), 1)} kN`, 'bs-last bs-reaktion'));
    }
    if (Math.abs(l.M) > 1e-6) svg.append(momentSymbol(p, l.M, `${fest(l.M, 1)} kNm`, 'bs-last bs-reaktion'));
  }
  return svg;
}

// ===========================================================================
// Fahren mit der Maus
// ===========================================================================

/** Ein Wert an der Stelle x eines Stabs -- zwischen zwei Proben gerade verbunden. */
function zwischen(proben, x, feld) {
  for (let i = 1; i < proben.length; i += 1) {
    const [a, b] = [proben[i - 1], proben[i]];
    if (x >= a.x && x <= b.x) {
      const t = b.x > a.x ? (x - a.x) / (b.x - a.x) : 0;
      return a[feld] + (b[feld] - a[feld]) * t;
    }
  }
  return proben[proben.length - 1][feld];
}

/**
 * Was unter dem Zeiger liegt: ein Knoten -- seine Verschiebung --, sonst die
 * nächste Stelle eines Stabs und ihr Wert. `zeilen(stab, x)` sagt, was an
 * einer Stelle steht.
 */
function finden(r, daten, punkt, zeilen) {
  for (const [k, w] of Object.entries(daten.knoten)) {
    const [x, y] = r.bild([w.x, w.z]);
    if (Math.hypot(punkt[0] - x, punkt[1] - y) <= 10) {
      return {
        ort: [x, y],
        text: [`Knoten ${k}`, `u_x = ${fest(w.ux, 2)} mm   u_z = ${fest(w.uz, 2)} mm`,
          w.unbestimmt ? daten.unbestimmt_text : `φ = ${fest(w.phi, 3)} mrad`],
      };
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

/** Hängt das Fahren mit der Maus an ein Bild: ein Zettel und ein Punkt an der Stelle. */
function zeigerEinrichten(huelle, svg, r, daten, zeilen) {
  const zettel = el('div.bs-zettel', { hidden: true });
  const marke = svgEl('circle', { r: 4, class: 'bs-d-marke', visibility: 'hidden' });
  svg.append(marke);
  huelle.append(zettel);
  const zeigen = (e) => {
    const rahmen = svg.getBoundingClientRect();
    if (!rahmen.width) return;
    const f = BREITE / rahmen.width;
    const punkt = [(e.clientX - rahmen.left) * f, (e.clientY - rahmen.top) * f];
    const treffer = finden(r, daten, punkt, zeilen);
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

/** Der Name eines Falls -- Lastfall oder Kombination -- aus seiner Kennung; `null`, wenn es ihn nicht gibt. */
function fallname(system, kennung) {
  return [...system.lastfaelle, ...system.kombinationen].find((f) => f.kennung === kennung)?.name ?? null;
}

/**
 * Ein Diagramm der Statik-Analyse als Karte: der Fall der Zeile, die Grösse
 * der Zeile. Über dem Diagramm sein Titel und der Fall.
 */
function diagrammKarte(kennung, system, zeile) {
  const titel = (zustand.katalog?.balkensystem?.diagrammgroessen || [])
    .find((g) => g.wert === zeile.groesse)?.titel || zeile.groesse;
  const fall = fallname(system, zeile.fall);
  if (fall === null) {
    return karte(titel, [leerzustand('Kein Fall gewählt.',
      'Unter «Statik-Analyse» einen Lastfall oder eine Kombination wählen.')]);
  }
  const eintrag = antwortZu(kennung, fall);
  if (eintrag.fehler) return karte(`${titel} – ${fall}`, [el('p.hinweis.hinweis-warnung', { text: eintrag.fehler })]);
  const antwort = eintrag.daten || eintrag.alt;
  const daten = antwort?.verlauf;
  if (!daten) return karte(`${titel} – ${fall}`, [leerzustand('Diagramm wird gerechnet …')]);
  const r = bildrahmen(daten.staebe);
  const uebersicht = (antwort.uebersicht?.faelle || []).find((f) => f.name === daten.fall);
  const extreme = uebersicht?.staebe || {};
  const verschiebung = (s, x) => [
    `u_x = ${fest(zwischen(s.proben, x, 'ux'), 2)} mm   u_z = ${fest(zwischen(s.proben, x, 'uz'), 2)} mm`,
    `w = ${fest(zwischen(s.proben, x, 'w'), 2)} mm gegen die Sehne`,
  ];
  let svg;
  let zeilen = verschiebung;
  const unten = [];
  if (zeile.groesse === 'verschiebung') {
    svg = verformungsbild(r, daten, extreme);
  } else if (zeile.groesse === 'lagerkraefte') {
    const lager = uebersicht?.lagerkraefte || [];
    svg = lagerbild(r, daten, lager);
    // Was keinen Knoten hat -- eine Stelle auf einem Stab, die Summe von
    // Linienlager oder Bettung --, steht unter dem Bild. Ohne sie ginge das
    // Gleichgewicht am Bildschirm nicht auf.
    unten.push(...lager.filter((l) => !l.knoten).map((l) => el('p.bs-einheiten', {
      text: `${l.wo}: R_x = ${fest(l.R_x, 1)} kN · R_z = ${fest(l.R_z, 1)} kN · M = ${fest(l.M, 1)} kNm`,
    })));
    if (lager.some((l) => l.summe)) unten.push(el('p.bs-einheiten', { text: antwort.uebersicht.summen_text }));
  } else {
    const g = GROESSEN[zeile.groesse];
    svg = verlaufsbild(r, daten, g, extreme);
    zeilen = (s, x) => [`${g.zeichen} = ${fest(zwischen(s.proben, x, g.schluessel), g.stellen)} ${g.einheit}`];
  }
  const huelle = el('div.bs-diagramm-huelle', {}, [svg]);
  zeigerEinrichten(huelle, svg, r, daten, zeilen);
  return karte(`${titel} – ${daten.fall}`, [huelle, ...unten],
    { klasse: eintrag.daten ? '' : 'ist-veraltet' });
}

/**
 * Die Diagramme eines Systems -- je Zeile der Statik-Analyse eine Karte. Das
 * Panel darum baut bericht.js.
 */
export function systemKarten(kennung) {
  const system = zustand.projekt.balkensysteme?.find((s) => s.kennung === kennung);
  const uebersicht = zustand.loesung?.balkensysteme?.[kennung];
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

/** Der grösste und der kleinste Wert einer Grösse über alle Stäbe -- mit Stab und Stelle. */
function grenzen(staebe, groesse) {
  let klein = null;
  let gross = null;
  for (const [name, e] of Object.entries(staebe)) {
    const [xk, vk] = e[groesse].kleinst;
    const [xg, vg] = e[groesse].groesst;
    if (!klein || vk < klein.v) klein = { v: vk, name, x: xk };
    if (!gross || vg > gross.v) gross = { v: vg, name, x: xg };
  }
  return { klein, gross };
}

function wertzelle(w, stellen) {
  if (!w) return el('td', { text: '–' });
  return el('td.bs-zahl', { title: `${w.name} bei x = ${fest(w.x, 2)} m` }, [
    fest(w.v, stellen), el('span.bs-wo', { text: ` ${w.name}` })]);
}

/**
 * Die Zusammenfassung eines Systems als Karten: Meldungen, je Fall die
 * Grenzwerte, die Lagerkräfte. Das Panel darum baut bericht.js.
 */
export function systemZusammenfassung(kennung) {
  const u = zustand.loesung?.balkensysteme?.[kennung];
  if (!u?.gerechnet) return [karte(null, [leerzustand('Noch nicht gerechnet.')])];
  const meldungen = (u.meldungen || []).map((m) => el('p', {
    class: m.fehler ? 'hinweis hinweis-warnung' : 'hinweis', text: m.text,
  }));
  if (!u.gueltig || !u.faelle.length) {
    return [karte(null, [...meldungen, u.faelle.length ? null : leerzustand('Kein Lastfall.')])];
  }
  const kopf = ['Fall', 'N_min', 'N_max', 'V_min', 'V_max', 'M_min', 'M_max', 'w_max']
    .map((t) => el('th', { text: t }));
  const zeilen = u.faelle.map((f) => {
    const n = grenzen(f.staebe, 'N');
    const v = grenzen(f.staebe, 'V');
    const m = grenzen(f.staebe, 'M');
    const w = grenzen(f.staebe, 'w');
    const wmax = Math.abs(w.gross?.v ?? 0) >= Math.abs(w.klein?.v ?? 0) ? w.gross : w.klein;
    return el('tr', {}, [
      el('td', { text: f.name + (f.kombination ? ' (Kombination)' : '') }),
      wertzelle(n.klein, 1), wertzelle(n.gross, 1), wertzelle(v.klein, 1), wertzelle(v.gross, 1),
      wertzelle(m.klein, 1), wertzelle(m.gross, 1), wertzelle(wmax, 2),
    ]);
  });
  // Alle Zeilen, wie in der Herleitung -- auch die Summen von Linienlager
  // und Bettung. Mit den Knoten allein gingen die Kräfte nicht auf.
  const lagerzeilen = u.faelle.flatMap((f) => f.lagerkraefte.map((l) => el('tr', {}, [
    el('td', { text: f.name }), el('td', { text: l.wo }),
    el('td.bs-zahl', { text: fest(l.R_x, 1) }), el('td.bs-zahl', { text: fest(l.R_z, 1) }),
    el('td.bs-zahl', { text: fest(l.M, 1) }),
  ])));
  const summen = u.faelle.some((f) => f.lagerkraefte.some((l) => l.summe));
  return [
    karte('Grenzwerte je Fall', [
      ...meldungen,
      el('p.bs-einheiten', { text: 'N, V in kN · M in kNm · w in mm gegen die Sehne · der Stab mit dem Wert steht klein daneben' }),
      el('div.tabelle-huelle', {}, [el('table.bs-tabelle', {}, [el('thead', {}, [el('tr', {}, kopf)]), el('tbody', {}, zeilen)])]),
    ]),
    lagerzeilen.length ? karte('Lagerkräfte auf das Tragwerk', [
      el('div.tabelle-huelle', {}, [el('table.bs-tabelle', {}, [
        el('thead', {}, [el('tr', {}, ['Fall', 'Lager', 'R_x [kN]', 'R_z [kN]', 'M [kNm]'].map((t) => el('th', { text: t })))]),
        el('tbody', {}, lagerzeilen),
      ])]),
      summen ? el('p.bs-einheiten', { text: u.summen_text }) : null,
    ]) : null,
  ];
}
