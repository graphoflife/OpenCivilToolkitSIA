/**
 * eb_zeichnung.js -- ein Gebäude im Erdbeben als Bild.
 *
 * Je Hauptrichtung eine Ansicht: die Geschosse als Decken über der
 * Einspannung, die Wände als Kragarm, links an jeder Decke ihre Kraft F_d,i
 * als Pfeil, rechts in jedem Geschoss die Querkraft darunter, am Fuss die
 * Ersatzkraft und das Kippmoment. Beide Richtungen im selben Massstab der
 * Kräfte -- man sieht, wo das Beben stärker angreift. Darunter, was jede Wand
 * am Fuss trägt, die Meldungen des Kerns -- rot, was falsch ist, grau, was
 * fehlt oder nicht gerechnet wird -- und die Legende.
 *
 * Namen und Höhen der Geschosse kommen aus dem Eintrag, wie eingegeben; was
 * der Kern daraus macht -- Kräfte, Querkräfte, die Anteile der Wände --, aus
 * der Lösung (opencivil/web/erdbebendaten.py). Gerechnet wird hier nur, wo
 * etwas im Bild steht.
 *
 * Dazu in derselben Höhe die Wände je Geschoss mit Querkraft und Moment
 * (eb_verlauf.js).
 */

import { karte } from './bausteine.js';
import { el, svgEl } from './dom.js';
import { verlaufKarte } from './eb_verlauf.js';
import {
  BREITE, legende, linie, pfeil, schraffur, text, textzeile, zahl,
} from './gb_skizze.js';
import { eintragVon, zustand } from './zustand.js';

const RAND = 16;
/** Oben Platz für den Titel, unten für die Schraffur und die Werte am Fuss, in px. */
const OBEN = 34;
const UNTEN = 54;
/** So hoch steht das Gebäude höchstens da, in px -- und so lang ist der längste Pfeil. */
const HOEHE = 300;
const PFEIL = 130;
/** Höchstens so viele px je m: ein Haus von einem Geschoss steht nicht als Turm da. */
const JE_METER = 25;
/** Mindestens so viel Platz über dem Fuss, in px -- auch ohne Geschoss. */
const NIEDRIG = 60;
/** Wie breit das Gebäude gezeichnet wird, in px -- seine Breite ist keine Eingabe. */
const GEBAEUDE = 46;

/**
 * Wie das Gebäude dasteht: `z` die Höhe jeder Decke über der Einspannung,
 * wie eingegeben, in m; `m` der Massstab, px je m; `hoch` der Platz über dem
 * Fuss, den das Bild braucht, in px -- ein niedriges Haus braucht wenig.
 */
function aufriss(geschosse) {
  let H = 0;
  const z = geschosse.map((g) => { H += Math.max(g.h, 0); return H; });
  const m = H > 0 ? Math.min(HOEHE / H, JE_METER) : 0;
  return { z, m, hoch: Math.max(H * m, NIEDRIG) };
}

/**
 * Eine Ansicht: links ab `x0`, `breite` breit. `r` ist die Richtung aus dem
 * Kern oder nichts; `k` der Massstab der Kräfte, px je kN.
 */
function ansicht(h, { z, m, hoch }, r, x0, breite, k, titel) {
  const H = z.length ? z[z.length - 1] : 0;
  const fuss = RAND + OBEN + hoch;
  const links = x0 + breite - GEBAEUDE - 78;
  const rechts = links + GEBAEUDE;
  const y = (hoehe) => fuss - hoehe * m;
  const teile = [
    text(x0, RAND + 12, [titel], { klasse: 'eb-titel' }),
    svgEl('rect', {
      x: links.toFixed(1), y: y(H).toFixed(1), width: GEBAEUDE, height: (H * m).toFixed(1),
      class: 'eb-gebaeude',
    }),
  ];
  h.geschosse.forEach((g, i) => {
    teile.push(
      linie([[links, y(z[i])], [rechts, y(z[i])]], 'eb-decke'),
      text(rechts + 6, y(z[i]) + 4, [g.name], { klasse: 'eb-name' }),
    );
    if (!r) return;
    const F = r.kraefte[i];
    teile.push(
      pfeil([links - 4 - Math.max(F * k, 6), y(z[i])], [links - 2, y(z[i])], 'gb-kraft'),
      text(links - 8 - Math.max(F * k, 6), y(z[i]) + 4, [`${zahl(F, 0)} kN`],
        { anker: 'end', klasse: 'gb-krafttext' }),
    );
    // Die Querkraft unter der Decke, mitten im Geschoss -- wo Platz ist.
    const unten = i ? z[i - 1] : 0;
    if ((z[i] - unten) * m >= 30) {
      teile.push(text(rechts + 6, y((z[i] + unten) / 2) + 14, ['V = ', `${zahl(r.querkraefte[i], 0)} kN`],
        { klasse: 'gb-zart' }));
    }
  });
  teile.push(
    schraffur([[[x0, fuss + 1], [x0 + breite, fuss + 1]]]),
    linie([[x0, fuss], [x0 + breite, fuss]], 'gb-gelaende'),
  );
  if (r) {
    teile.push(text(x0, fuss + 30, ['F', { unten: 'd' }, ` = ${zahl(r.F_d, 0)} kN · M`, { unten: '0' },
      ` = ${zahl(r.M_0, 0)} kNm`], { klasse: 'eb-fuss' }));
  }
  return teile;
}

/**
 * Die Ansichten nebeneinander -- je Richtung, die der Kern gerechnet hat,
 * sonst das Gebäude allein. `a` ist der Aufriss.
 */
function bild(h, d, a) {
  const richtungen = d?.richtungen?.length ? d.richtungen : [null];
  const groesste = Math.max(1e-9, ...richtungen.flatMap((r) => r?.kraefte || []));
  const k = PFEIL / groesste;
  const breite = (BREITE - RAND * (richtungen.length + 1)) / richtungen.length;
  const hoehe = RAND + OBEN + a.hoch + UNTEN + RAND;
  const svg = svgEl('svg', {
    viewBox: `0 0 ${BREITE} ${hoehe}`, class: 'gb-bild', role: 'img',
    'aria-label': `Ersatzkräfte des Gebäudes ${h.name}`,
  });
  richtungen.forEach((r, i) => {
    const titel = r ? `Richtung ${r.richtung}` : 'Ansicht';
    svg.append(...ansicht(h, a, r, RAND + i * (breite + RAND), breite, k, titel).filter(Boolean));
  });
  return svg;
}

/**
 * Was jede Wand am Fuss trägt, je Richtung: Anteil an EI, Querkraft und
 * Moment -- je eine der n gleichen, wie im Kern (`Wandanteil`).
 */
function wandtabelle(d) {
  const richtungen = (d?.richtungen || []).filter((r) => r.waende.length);
  if (!richtungen.length) return null;
  const kopf = ['Wand', 'n', ...richtungen.flatMap((r) => [`Anteil ${r.richtung}`,
    `V_${r.richtung} [kN]`, `M_${r.richtung} [kNm]`])];
  return el('table.eb-waende', {}, [
    el('caption', { text: 'Am Fuss, je eine der n gleichen Wände: ihr Anteil an EI, Querkraft und Moment' }),
    el('thead', {}, [el('tr', {}, kopf.map((t) => el('th', { text: t })))]),
    el('tbody', {}, richtungen[0].waende.map((w, i) => el('tr', {}, [
      el('td', { text: w.name }), el('td', { text: String(w.n) }),
      ...richtungen.flatMap((r) => [
        el('td', { text: `${zahl(100 * r.waende[i].anteil, 1)} %` }),
        el('td', { text: zahl(r.waende[i].V, 0) }),
        el('td', { text: zahl(r.waende[i].M, 0) }),
      ]),
    ]))),
  ]);
}

/** Die Meldungen des Kerns: rot, was falsch ist, grau, was fehlt oder nicht gerechnet wird. */
function meldungen(d) {
  const liste = d?.meldungen || [];
  return liste.length ? el('div.qa-meldungen', {}, liste.map((m) => el('div.qa-meldung', {
    text: m.text, class: m.fehler ? '' : 'ist-hinweis',
  }))) : null;
}

/**
 * Die Karten eines Gebäudes im Reiter «Diagramme»: die Ersatzkräfte, dann
 * Wände, Querkraft und Moment. Das Panel darum baut bericht.js.
 */
export function erdbebenKarten(kennung) {
  const h = eintragVon(kennung);
  if (!h) return [];
  const roh = zustand.loesung?.zeichendaten?.[kennung];
  // Eine Antwort zu anderen Geschossen gilt nicht mehr -- bis die neue da ist.
  const d = roh && (roh.richtungen.every((r) => r.kraefte.length === h.geschosse.length)) ? roh : null;
  const a = aufriss(h.geschosse);
  const abbild = bild(h, d, a);
  return [karte('Ersatzkräfte', [
    el('div.gb-bildhuelle', {}, [abbild]),
    wandtabelle(d),
    meldungen(d),
    legende(d ? d.legende : [textzeile('Noch nicht gerechnet.')]),
  ].filter(Boolean), { bild: abbild, klasse: 'ist-breit' }), verlaufKarte(h, d, a)].filter(Boolean);
}
