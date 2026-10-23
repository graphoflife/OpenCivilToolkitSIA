/**
 * gb_zeichnung.js -- die Situation eines Grundbruchs als Bild.
 *
 * Wie Bild 9.2.15 des Kapitels: links die Seite, zu der T zeigt und auf der
 * das Gelände um β abfällt; die Sohle steigt um α nach links an, N steht
 * normal zu ihr, R ist um δ_R gegen N geneigt. Dazu wie in Bild 9.2.10 der
 * höchste Grundwasserspiegel in der Tiefe t₁ unter Terrain und, gestrichelt,
 * der Gleitkörper mit seiner Tiefe H unter der Sohle.
 *
 * Die Masse kommen aus dem Eintrag, wie sie eingegeben sind; was der Kern
 * daraus macht -- der Umriss des Gleitkörpers, die Neigung der Last, die
 * Lage des Grundwassers --, aus der Lösung (opencivil/web/grundbruchdaten.py).
 * Die Kräfte stehen im Verhältnis zueinander, nicht im Massstab der Längen:
 * die grösste ist immer gleich lang.
 */

import { karte } from './bausteine.js';
import { auswahl, el, svgEl } from './dom.js';
import {
  BREITE, bogen, linie, mass, pfeil, schraffur, text, zahl,
} from './gb_skizze.js';
import { aendern, zustand } from './zustand.js';

const RAND = 36;
/** Wie lang die Resultierende gezeichnet wird, in px. */
const PFEIL = 120;
const GRAD = Math.PI / 180;

/** Welche Kombination je Grundbruch gezeigt wird -- ohne Wahl die massgebende. */
const gezeigt = new Map();

/**
 * Der Umriss des Gleitkörpers, soweit er im Boden liegt. Er ist für
 * waagrechtes Gelände gerechnet; fällt das Gelände ab, tritt er früher aus
 * -- dort endet er im Bild. `gekappt` sagt, ob das geschah.
 */
function imBoden(umriss, tanB) {
  const ueber = ([X, Y]) => Y - Math.min(X, 0) * tanB;
  for (let i = 1; i < umriss.length; i += 1) {
    const [a, e] = [umriss[i - 1], umriss[i]];
    if (e[0] <= 0 && ueber(e) > 1e-9) {
      const anteil = ueber(a) / (ueber(a) - ueber(e));
      return {
        zug: [...umriss.slice(0, i), [a[0] + anteil * (e[0] - a[0]), a[1] + anteil * (e[1] - a[1])]],
        gekappt: true,
      };
    }
  }
  return { zug: umriss, gekappt: false };
}

// ===========================================================================
// Das Bild
// ===========================================================================

/**
 * Die Situation: Gelände, Fundament, Grundwasser, Gleitkörper und die
 * Kräfte des Falls `fall` (aus der Lösung) -- ohne Fall ohne Kräfte.
 */
function situationsbild(g, s, fall) {
  const b = Math.max(g.b, 1e-3);
  const { t, t1 } = g;
  const tanA = Math.tan(g.alpha * GRAD);
  const tanB = Math.tan(g.beta * GRAD);
  // Modell in m: X nach rechts, Y nach oben, null am Terrain an der linken
  // Kante des Fundaments -- dort, wo in Bild 9.2.15 t gemessen wird.
  const sohleL = [0, -t];
  const sohleR = [b, -t - b * tanA];
  const kopf = Math.max(0.3 * b, 0.25);
  const umriss = (s?.umriss || []).map(([x, z]) => [-x, -t - z]);
  const reichweite = s?.L_gl ?? b;
  const tiefe = s?.H_gl ?? 0.7 * b;
  const links = -Math.max(reichweite + 0.25 * b + 0.2, 1.4 * b + 0.4);
  const rechts = b + Math.max(1.5 * b, 1.5);
  const k = (BREITE - 2 * RAND) / (rechts - links);

  // Unten: Sohle, Gleitkörper -- und das Grundwasser, solange es nicht
  // weit darunter liegt; dann steht es am unteren Rand mit seiner Tiefe.
  const sohleTief = Math.min(sohleL[1], sohleR[1]);
  const grenze = Math.min(sohleTief - tiefe, sohleTief - 0.6 * b) - Math.max(0.6 * b, 0.6);
  const gwTiefer = -t1 < grenze;
  const gwY = gwTiefer ? grenze : -t1;
  const unten = Math.min(grenze, gwY) - 0.25 * b - 0.15;

  // Die Kräfte: tief bei der Mitte der Sohle, N normal zu ihr nach unten, T
  // in ihr nach links, R die Summe. Ihre Länge in px, nicht in m.
  const mitte = [b / 2, (sohleL[1] + sohleR[1]) / 2];
  const cosA = Math.cos(g.alpha * GRAD);
  const sinA = Math.sin(g.alpha * GRAD);
  let kraefte = null;
  if (fall) {
    const R = Math.hypot(fall.N_Ed, fall.T_Ed) || 1;
    const nl = (fall.N_Ed / R) * PFEIL / k;
    const tl = (fall.T_Ed / R) * PFEIL / k;
    // In m: die Sohlnormale nach unten (-sinA, -cosA), die Sohle nach links (-cosA, sinA).
    const nVon = [mitte[0] + sinA * nl, mitte[1] + cosA * nl];
    const tVon = [mitte[0] + cosA * tl, mitte[1] - sinA * tl];
    const rVon = [nVon[0] + cosA * tl, nVon[1] - sinA * tl];
    kraefte = { nVon, tVon, rVon };
  }
  // Oben die Masslinie von b, über dem Fundament und den Kräften; Abstände
  // für Schrift in px, damit sie in jedem Massstab Platz hat.
  const inM = (pixel) => pixel / k;
  const spitzen = kraefte ? Math.max(kraefte.nVon[1], kraefte.rVon[1]) : kopf;
  const massB = Math.max(kopf, spitzen) + inM(24);
  const oben = massB + inM(22);

  const px = ([X, Y]) => [RAND + (X - links) * k, RAND + (oben - Y) * k];
  const hoehe = Math.round(2 * RAND + (oben - unten) * k);
  const svg = svgEl('svg', {
    viewBox: `0 0 ${BREITE} ${hoehe}`, class: 'gb-bild', role: 'img',
    'aria-label': `Situation des Grundbruchs ${g.name}`,
  });
  // Ein zu kurzer Pfeil ist null -- und `append(null)` schriebe «null» ins Bild.
  const zeichne = (...teile) => svg.append(...teile.filter(Boolean));

  // -- Boden: Gelände links geneigt, rechts waagrecht, darunter schraffiert --
  const gelaendeLinks = [[links, links * tanB], [0, 0]];
  const gelaendeRechts = [[b, 0], [rechts, 0]];
  zeichne(
    schraffur([gelaendeLinks.map(px), gelaendeRechts.map(px)]),
    linie(gelaendeLinks.map(px), 'gb-gelaende'),
    linie(gelaendeRechts.map(px), 'gb-gelaende'),
  );

  // -- Grundwasser: unter dem Gelände, mit dem Zeichen rechts ---------------
  const gwStart = tanB > 0 ? Math.max(links, gwY / tanB) : links;
  if (gwY <= 0) {
    zeichne(linie([[gwStart, gwY], [rechts, gwY]].map(px), 'gb-wasser'));
    const [zx, zy] = px([b + 0.62 * (rechts - b), gwY]);
    zeichne(
      svgEl('path', { d: `M${zx - 7} ${zy - 9} h14 l-7 9 z`, class: 'gb-wasserzeichen' }),
      linie([[zx - 6, zy + 4], [zx + 6, zy + 4]], 'gb-wasser-kurz'),
      linie([[zx - 3, zy + 8], [zx + 3, zy + 8]], 'gb-wasser-kurz'),
      text(zx + 12, zy - 2, gwTiefer ? ['GW tiefer'] : ['GW'], { klasse: 'gb-wassertext' }),
    );
  }

  // -- Gleitkörper, gestrichelt, bis er aus dem Gelände tritt --------------
  if (umriss.length) {
    const { zug, gekappt } = imBoden(umriss, tanB);
    zeichne(linie(zug.map(px), 'gb-gleitkoerper'));
    const tiefster = umriss.reduce((a, p) => (p[1] < a[1] ? p : a), umriss[0]);
    zeichne(mass(px([tiefster[0], sohleL[1]]), px(tiefster), ['H = ', zahl(tiefe, 2), ' m'],
      { seite: 'links' }));
    // L gilt auf Höhe der Sohle -- gekappt endet der Zug nicht dort.
    if (!gekappt) {
      const ende = px(zug[zug.length - 1]);
      zeichne(text(ende[0], ende[1] + 16, ['L = ', zahl(reichweite, 2), ' m'],
        { anker: 'middle', klasse: 'gb-zart' }));
    }
  }

  // -- Fundament ------------------------------------------------------------
  zeichne(svgEl('path', {
    d: `M${[[0, kopf], [b, kopf], sohleR, sohleL].map(px).map((p) => p.map((v) => v.toFixed(1)).join(' ')).join(' L')} Z`,
    class: 'gb-fundament',
  }));

  // -- Masse: b über allem, t links am Fundament, t₁ rechts -----------------
  zeichne(
    linie([px([0, kopf]), px([0, massB + inM(5)])], 'gb-masshilfe'),
    linie([px([b, kopf]), px([b, massB + inM(5)])], 'gb-masshilfe'),
    mass(px([0, massB]), px([b, massB]), ['b = ', zahl(g.b, 2), ' m']),
  );
  if (t > 0) {
    zeichne(mass(px([-inM(12), 0]), px([-inM(12), sohleL[1]]), ['t = ', zahl(t, 2), ' m'],
      { seite: 'links' }));
  }
  if (t1 > 0) {
    const x = b + 0.3 * (rechts - b);
    zeichne(mass(px([x, 0]), px([x, gwY]), ['t', { unten: '1' }, ' = ', zahl(t1, 2), ' m']));
  }

  // -- Winkel: β am Gelände, α an der Sohle -----------------------------------
  if (g.beta > 0) {
    const ecke = px([0, 0]);
    const r = Math.min(70, 0.8 * (0 - links) * k);
    zeichne(
      linie([ecke, px([-(r / k) * 1.25, 0])], 'gb-hilfslinie'),
      bogen(ecke, r, Math.PI, Math.PI - g.beta * GRAD),
      text(ecke[0] - r - 4, ecke[1] + 12, ['β = ', zahl(g.beta, 1), '°'], { anker: 'end' }),
    );
  }
  if (g.alpha > 0) {
    const ecke = px(sohleR);
    const r = Math.min(0.45 * b * k, 60);
    zeichne(
      linie([ecke, [ecke[0] - r * 1.3, ecke[1]]], 'gb-hilfslinie'),
      bogen(ecke, r, Math.PI, Math.PI + g.alpha * GRAD),
      text(ecke[0] - r - 4, ecke[1] + 14, ['α = ', zahl(g.alpha, 1), '°'], { anker: 'end' }),
    );
  }

  // -- Auflast neben dem Fundament ------------------------------------------
  if (g.q_Ed > 0) {
    const reihe = (von, bis) => {
      const [a, e] = [px(von), px(bis)];
      const n = Math.max(2, Math.floor(Math.abs(e[0] - a[0]) / 26));
      return Array.from({ length: n }, (_, i) => {
        const x = a[0] + (e[0] - a[0]) * (i + 0.5) / n;
        const y = a[1] + (e[1] - a[1]) * (i + 0.5) / n;
        return pfeil([x, y - 16], [x, y - 1], 'gb-auflast');
      });
    };
    zeichne(
      ...reihe([links + 0.1 * b, (links + 0.1 * b) * tanB], [-0.08 * b, -0.08 * b * tanB]),
      ...reihe([b + 0.08 * b, 0], [rechts - 0.1 * b, 0]),
    );
    // Angeschrieben über dem Gelände links, längs des Hangs: rechts stehen
    // die Kräfte.
    const [x, y] = px([links + 0.1 * b, (links + 0.1 * b) * tanB]);
    const s = Math.sin(g.beta * GRAD);
    const c = Math.cos(g.beta * GRAD);
    zeichne(text(x - 22 * s, y - 22 * c, ['q', { unten: 'Ed' }, ' = ', zahl(g.q_Ed, 1), ' kPa'],
      { klasse: 'gb-lasttext', drehung: g.beta }));
  }

  // -- Kräfte --------------------------------------------------------------
  if (kraefte) {
    const p = px(mitte);
    const [n, tv, r] = [px(kraefte.nVon), px(kraefte.tVon), px(kraefte.rVon)];
    if (fall.T_Ed > 0) {
      zeichne(linie([n, r, tv], 'gb-hilfslinie'));
    }
    zeichne(pfeil(n, p, 'gb-kraft'), text(n[0] - 6, n[1] + 4, ['N'], { anker: 'end', klasse: 'gb-krafttext' }));
    if (fall.T_Ed > 0) {
      zeichne(
        pfeil(tv, p, 'gb-kraft'),
        text(tv[0] + 4, tv[1] + 16, ['T'], { klasse: 'gb-krafttext' }),
        pfeil(r, p, 'gb-kraft gb-resultierende'),
        text(r[0] + 6, r[1] + 4, ['R'], { klasse: 'gb-krafttext' }),
      );
      // δ_R zwischen N und R, angeschrieben rechts vom Bogen.
      const winkel = (q) => Math.atan2(q[1] - p[1], q[0] - p[0]);
      const rb = 0.6 * PFEIL;
      const wr = winkel(r);
      zeichne(
        bogen(p, rb, winkel(n), wr),
        text(p[0] + rb * Math.cos(wr) + 7, p[1] + rb * Math.sin(wr) + 4,
          ['δ', { unten: 'R' }], { klasse: 'gb-krafttext' }),
      );
    }
  }
  return svg;
}

// ===========================================================================
// Die Karte
// ===========================================================================

/** Die Zeilen unter dem Bild: Kräfte, Grundwasser, Gleitkörper. */
function legende(g, s, fall) {
  const zeilen = [];
  if (fall) {
    zeilen.push(`${fall.name}: N_Ed = ${zahl(fall.N_Ed, 1)} kN · T_Ed = ${zahl(fall.T_Ed, 1)} kN`
      + ` · δ_R = ${zahl(fall.delta_R, 1)}° – die Kräfte im Verhältnis zueinander, nicht im Massstab der Längen`);
  } else {
    zeilen.push(g.kombinationen.some((k) => k.aktiv !== false)
      ? 'Noch nicht gerechnet.' : 'Keine Kombination eingeschaltet – ohne Kräfte.');
  }
  if (s?.grundwasser) zeilen.push(s.grundwasser);
  if (s?.umriss?.length) {
    zeilen.push(`Gleitkörper nach Prandtl: H = ${zahl(s.H_gl, 2)} m unter der Sohle, L = `
      + `${zahl(s.L_gl, 2)} m neben ihr${g.alpha || g.beta ? ' – gezeichnet für α = β = 0' : ''}`);
  } else if (s?.undrainiert) {
    zeilen.push('Undrainiert, φ = 0: kein Gleitkörper gezeichnet.');
  }
  zeilen.push(`Länge des Fundaments L = ${zahl(g.L, 2)} m, senkrecht zum Bild.`);
  return el('div.gb-legende', {}, zeilen.map((z) => el('p', { text: z })));
}

/**
 * Die Karten eines Grundbruchs im Reiter «Diagramme»: die Situation, über ihr
 * die Wahl der Kombination. Das Panel darum baut bericht.js.
 */
export function situationKarten(kennung) {
  const g = (zustand.projekt?.grundbrueche || []).find((x) => x.kennung === kennung);
  if (!g) return [];
  const s = zustand.loesung?.grundbrueche?.[kennung];
  const faelle = s?.faelle || [];
  const name = faelle.some((f) => f.name === gezeigt.get(kennung)) ? gezeigt.get(kennung) : s?.massgebend;
  const fall = faelle.find((f) => f.name === name) || null;
  const wahl = faelle.length > 1 ? auswahl({
    werte: faelle.map((f) => ({
      wert: f.name, beschriftung: f.name === s.massgebend ? `${f.name} (massgebend)` : f.name,
    })),
    gewaehlt: fall?.name,
    titel: 'Deren Kräfte zeigt das Bild',
    beiAenderung: (w) => {
      gezeigt.set(kennung, w);
      aendern({}, 'diagramm');
    },
  }) : null;
  return [karte('Situation', [
    el('div.gb-bildhuelle', {}, [situationsbild(g, s, fall)]),
    legende(g, s, fall),
  ], { zusatz: wahl, klasse: 'ist-breit' })];
}
