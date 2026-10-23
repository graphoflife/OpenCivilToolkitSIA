/**
 * bs_diagramme.js -- die Ergebnisse eines Balkensystems, rechts.
 *
 * Unter «Diagramme» je System und gewählter Kombination -- ein Lastfall
 * allein bekommt keine Bilder:
 *
 *   Verformung    das System verschoben, überhöht -- das unverformte blass;
 *   N, V, M       je Stab der Verlauf, quer zum Stab aufgetragen, positive
 *                 Werte auf der Seite der gestrichelten Faser -- das Moment
 *                 also auf der Zugseite --, mit den Werten an den Enden und
 *                 am grössten Wert;
 *   Lagerkräfte   je Lager die Kräfte und das Moment auf das Tragwerk.
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
import {
  auswahl, el, leerzustand, svgEl,
} from './dom.js';
import { aendern, zustand } from './zustand.js';

const BREITE = 640;
/** Platz rund um das System -- für die Ordinaten und die Beschriftung, in Bildpunkten. */
const RAND = 58;
/** Wie weit die grösste Ordinate vom Stab absteht, in Bildpunkten. */
const AUSSCHLAG = 44;

/** Die Grössen der Bilder: Titel, Feld in den Proben, Einheit, Stellen. */
const GROESSEN = [
  { schluessel: 'N', titel: 'Normalkraft N', einheit: 'kN', stellen: 1, klasse: 'bs-d-n' },
  { schluessel: 'V', titel: 'Querkraft V', einheit: 'kN', stellen: 1, klasse: 'bs-d-v' },
  { schluessel: 'M', titel: 'Moment M', einheit: 'kNm', stellen: 1, klasse: 'bs-d-m' },
];

/** Kennung -> {abdruck, fall, daten, alt, fehler, uhr}: die letzte Antwort je System. */
const vorrat = new Map();

/** Kennung -> Name des gezeigten Falls. Ansichtssache, nicht Teil des Projekts. */
const gezeigt = new Map();

const fest = (x, n) => (Math.abs(x) < 0.5 * 10 ** -n ? 0 : x).toFixed(n);

// ===========================================================================
// Anfrage
// ===========================================================================

/** Fragt nach den Verläufen -- erst, wenn gerade nicht gerechnet wird: dann liegt das System im Speicher des Kerns. */
function anfordern(kennung, eintrag, verzug = 500) {
  clearTimeout(eintrag.uhr);
  eintrag.uhr = setTimeout(() => {
    if (vorrat.get(kennung) !== eintrag) return;
    if (zustand.rechnetGerade) {
      anfordern(kennung, eintrag);
      return;
    }
    api.balkensystemVerlauf(zustand.projekt, kennung, eintrag.fall).then((antwort) => {
      if (vorrat.get(kennung) !== eintrag) return;
      eintrag.daten = antwort;
      aendern({}, 'diagramm');
    }).catch((fehler) => {
      if (vorrat.get(kennung) !== eintrag) return;
      eintrag.fehler = fehler.message;
      aendern({}, 'diagramm');
    });
  }, verzug);
}

/**
 * Die Fälle, für die es Bilder gibt: die Kombinationen, wie die letzte
 * Rechnung sie kennt -- ein Lastfall allein bekommt keine (Benutzer,
 * 2026-10-23).
 */
function faelleVon(kennung) {
  return (zustand.loesung?.balkensysteme?.[kennung]?.faelle || [])
    .filter((f) => f.kombination).map((f) => f.name);
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

/** Ein Verlauf: je Stab die Fläche zwischen Stab und Ordinate, und die Werte an Enden und Extremwert. */
function verlaufsbild(r, daten, groesse) {
  const svg = svgEl('svg', { viewBox: `0 0 ${BREITE} ${r.hoehe}`, class: 'bs-diagramm' });
  svg.append(systemlinien(r, daten.staebe));
  const alle = Object.values(daten.staebe).flatMap((s) => s.proben.map((p) => Math.abs(p[groesse.schluessel])));
  const groesste = Math.max(0, ...alle);
  const k = groesste > 1e-9 ? AUSSCHLAG / groesste : 0;
  for (const s of Object.values(daten.staebe)) {
    const n = faserseite(s);
    const ordinate = (p) => {
      const [x, y] = r.bild(amStab(s, p.x));
      const v = p[groesse.schluessel];
      return [x + n[0] * k * v, y + n[1] * k * v];
    };
    const basis = s.proben.map((p) => r.bild(amStab(s, p.x)));
    const kurve = s.proben.map(ordinate);
    const flaeche = [...kurve, ...basis.reverse()];
    svg.append(svgEl('path', {
      d: `${flaeche.map((p, i) => `${i ? 'L' : 'M'}${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(' ')} Z`,
      class: `bs-d-flaeche ${groesse.klasse}`,
    }));
    svg.append(svgEl('path', {
      d: kurve.map((p, i) => `${i ? 'L' : 'M'}${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(' '),
      class: `bs-d-kurve ${groesse.klasse}`,
    }));
    // Beschriftet: die Enden und der grösste Betrag dazwischen.
    const marken = [s.proben[0], s.proben[s.proben.length - 1]];
    const innen = s.proben.slice(1, -1).reduce((b, p) => (Math.abs(p[groesse.schluessel]) > Math.abs(b?.[groesse.schluessel] ?? 0) ? p : b), null);
    if (innen && Math.abs(innen[groesse.schluessel]) > Math.max(...marken.map((p) => Math.abs(p[groesse.schluessel]))) * 1.02) marken.push(innen);
    for (const p of marken) {
      const v = p[groesse.schluessel];
      if (Math.abs(v) < groesste * 0.01) continue;
      const [x, y] = ordinate(p);
      const versatz = v >= 0 ? 1 : -1;
      svg.append(schrift(x + n[0] * 10 * versatz, y + n[1] * 10 * versatz + 4, fest(v, groesse.stellen)));
    }
  }
  return svg;
}

/** Die Verformung: das System verschoben, überhöht -- das unverformte blass darunter. */
function verformungsbild(r, daten) {
  const svg = svgEl('svg', { viewBox: `0 0 ${BREITE} ${r.hoehe}`, class: 'bs-diagramm' });
  svg.append(systemlinien(r, daten.staebe));
  const groesste = Math.max(0, ...Object.values(daten.staebe)
    .flatMap((s) => s.proben.map((p) => Math.hypot(p.ux, p.uz))));
  // Überhöht, bis die grösste Verschiebung ein Zwölftel des Systems ist.
  const faktor = groesste > 1e-12 ? (r.groesse / 12) / (groesste / 1000) : 0;
  for (const s of Object.values(daten.staebe)) {
    const punkte = s.proben.map((p) => {
      const [x, z] = amStab(s, p.x);
      return r.bild([x + faktor * p.ux / 1000, z + faktor * p.uz / 1000]);
    });
    svg.append(svgEl('path', {
      d: punkte.map((p, i) => `${i ? 'L' : 'M'}${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(' '),
      class: 'bs-d-verformt',
    }));
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

function fallwahl(kennung, faelle, gewaehlt) {
  return auswahl({
    werte: faelle.map((f) => ({ wert: f, beschriftung: f })),
    gewaehlt,
    titel: 'Welche Kombination gezeigt wird',
    beiAenderung: (w) => {
      gezeigt.set(kennung, w);
      aendern({}, 'diagramm');
    },
  });
}

/**
 * Die Diagramme eines Systems -- je Bild eine Karte, darüber die Wahl des
 * Falls. Das Panel darum baut bericht.js.
 */
export function systemKarten(kennung) {
  const faelle = faelleVon(kennung);
  const uebersicht = zustand.loesung?.balkensysteme?.[kennung];
  if (uebersicht && !uebersicht.gueltig) {
    return [karte(null, (uebersicht.meldungen || []).filter((m) => m.fehler)
      .map((m) => el('p.hinweis.hinweis-warnung', { text: m.text })))];
  }
  if (!faelle.length) {
    return [karte(null, [leerzustand('Keine Lastkombination.',
      'Bilder gibt es je Kombination; anlegen unter «Lastfälle und Kombinationen».')])];
  }
  const fall = faelle.includes(gezeigt.get(kennung)) ? gezeigt.get(kennung) : faelle[0];
  const abdruck = `${abdruckVon(kennung)}|${fall}`;
  let eintrag = vorrat.get(kennung);
  if (!eintrag || eintrag.abdruck !== abdruck) {
    const alt = eintrag?.daten || eintrag?.alt || null;
    eintrag = { abdruck, fall, daten: null, alt, fehler: null, uhr: null };
    vorrat.set(kennung, eintrag);
    anfordern(kennung, eintrag, alt?.verlauf?.fall === fall ? 500 : 80);
  }
  const antwort = eintrag.daten || eintrag.alt;
  // Die Wahl des Falls gilt für alle Bilder darunter -- über die ganze Breite.
  const kopf = karte('Fall', [
    el('div.qa-fallkopf', {}, [
      fallwahl(kennung, faelle, fall),
      !eintrag.daten ? el('span.qa-nachfuehren', { text: 'wird nachgeführt …' }) : null,
    ]),
  ], { klasse: 'ist-breit' });
  if (eintrag.fehler) return [kopf, karte(null, [el('p.hinweis.hinweis-warnung', { text: eintrag.fehler })])];
  const daten = antwort?.verlauf;
  if (!daten) return [kopf, karte(null, [leerzustand('Diagramme werden gerechnet …')])];
  const r = bildrahmen(daten.staebe);
  const veraltet = !eintrag.daten;
  const blatt = (t, svg, zeilen, unten = []) => {
    const huelle = el('div.bs-diagramm-huelle', {}, [svg]);
    zeigerEinrichten(huelle, svg, r, daten, zeilen);
    return karte(`${t} – ${daten.fall}`, [huelle, ...unten],
      { klasse: veraltet ? 'ist-veraltet' : '' });
  };
  const verschiebung = (s, x) => [
    `u_x = ${fest(zwischen(s.proben, x, 'ux'), 2)} mm   u_z = ${fest(zwischen(s.proben, x, 'uz'), 2)} mm`,
    `w = ${fest(zwischen(s.proben, x, 'w'), 2)} mm gegen die Sehne`,
  ];
  const lager = (antwort.uebersicht?.faelle || []).find((f) => f.name === daten.fall)?.lagerkraefte || [];
  // Was keinen Knoten hat -- eine Stelle auf einem Stab, die Summe von
  // Linienlager oder Bettung --, steht unter dem Bild. Ohne sie ginge das
  // Gleichgewicht am Bildschirm nicht auf.
  const ohneKnoten = lager.filter((l) => !l.knoten).map((l) => el('p.bs-einheiten', {
    text: `${l.wo}: R_x = ${fest(l.R_x, 1)} kN · R_z = ${fest(l.R_z, 1)} kN · M = ${fest(l.M, 1)} kNm`,
  }));
  if (lager.some((l) => l.summe)) {
    ohneKnoten.push(el('p.bs-einheiten', { text: antwort.uebersicht.summen_text }));
  }
  return [
    kopf,
    blatt('Verformung', verformungsbild(r, daten), verschiebung),
    ...GROESSEN.map((g) => blatt(g.titel, verlaufsbild(r, daten, g), (s, x) => [
      `${g.schluessel} = ${fest(zwischen(s.proben, x, g.schluessel), g.stellen)} ${g.einheit}`])),
    blatt('Lagerkräfte', lagerbild(r, daten, lager), verschiebung, ohneKnoten),
  ];
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
