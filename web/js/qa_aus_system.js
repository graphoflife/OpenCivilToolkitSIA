/**
 * qa_aus_system.js -- die Kachel «Aus dem Balkensystem» der Querschnittsanalyse.
 *
 * Ein ebenes oder räumliches Balkensystem und seine Stäbe: alle, deren
 * Querschnitt diese Analyse ist, oder gewählte. Je Kombination nimmt der
 * Kern ihre massgebenden Stellen -- grösstes und kleinstes M_y, M_z und N,
 * grösstes |V_z|, |V_y| und |T|, je mit den übrigen Schnittgrössen dort --,
 * und jede ist ein Lastfall aller Nachweise der Analyse, neben den eigenen
 * (opencivil/projekt/aufbau/aus_system.py). Was sich wählen lässt, welche
 * Stäbe zählen und die Stellen sagt der Kern (`zeichendaten`); hier stehen
 * sie nur da, und nur, solange sie zum gewählten System gehören.
 */

import {
  bauteilliste, hakenSchalter, tabelle, wahlBlock, wahlSchalter,
} from './bausteine.js';
import { el } from './dom.js';
import { eintragAendern, istSandbox, katalog, zustand } from './zustand.js';

/** Die Systeme des Projekts zur Wahl, erst die ebenen, dann die räumlichen. */
function systeme() {
  const art = (liste, wort) => (zustand.projekt[liste] || [])
    .map((s) => ({ kennung: s.kennung, name: `${s.name} – ${wort}` }));
  return [...art('balkensysteme', 'eben'), ...art('balkensysteme3d', 'räumlich')];
}

/** Was der Kern dazu sagt -- nur, wenn es zum jetzigen System gehört: nach einer anderen Wahl gilt es nicht mehr. */
function befund(analyse) {
  const d = zustand.loesung?.zeichendaten?.[analyse.kennung]?.aus_system;
  return d && d.system === analyse.aus_system.system ? d : null;
}

/** Ändert die Wahl der Analyse. */
function setzen(analyse, veraenderer) {
  eintragAendern(analyse.kennung, (a) => veraenderer(a.aus_system));
}

/** Die Wahl der Stäbe: der Schalter, darunter, was die gewählte Stellung heisst. */
function stabwahl(analyse) {
  const werte = katalog('querschnittsanalyse', 'stabwahlen');
  const wahl = analyse.aus_system.stabwahl;
  return [
    wahlBlock('Stäbe', wahlSchalter({
      werte, gewaehlt: wahl, titel: 'Welche Stäbe des Systems ihre Stellen geben',
      setzen: (v) => setzen(analyse, (x) => { x.stabwahl = v; }),
    })),
    el('p.qa-erlaeuterung', { text: werte.find((w) => w.wert === wahl)?.titel || '' }),
  ];
}

/** Je Stab des Systems ein Schalter: zählt er oder nicht -- bei «gewählte». */
function stabschalter(analyse, d) {
  if (!d.kandidaten.length) return el('div.leer', { text: 'Das System hat noch keinen Stab.' });
  const gewaehlt = new Set(analyse.aus_system.staebe);
  return el('div.qa-stabwahl', {}, d.kandidaten.map((k) => el('span.qa-stab', {}, [
    hakenSchalter(gewaehlt.has(k.kennung), (an) => setzen(analyse, (x) => {
      x.staebe = an ? [...x.staebe, k.kennung] : x.staebe.filter((s) => s !== k.kennung);
    }), `Stab ${k.kennung}`),
    el('span', { text: k.querschnitt ? `${k.kennung} – ${k.querschnitt}` : k.kennung }),
  ])));
}

/** Die Spalten der Stellen: das Feld eines Lastfalls und sein Kopf. */
const SPALTEN = [
  ['N_Ed', 'N [kN]'], ['V_y_Ed', 'V_y [kN]'], ['V_z_Ed', 'V_z [kN]'],
  ['T_Ed', 'T [kNm]'], ['M_y_Ed', 'M_y [kNm]'], ['M_z_Ed', 'M_z [kNm]'],
];

/** Was der Kern sagt: die Sätze grau, welche Stäbe zählen und die Stellen als Lastfälle. */
function ergebnis(analyse, d) {
  if (!d) {
    const da = zustand.loesung?.zeichendaten?.[analyse.kennung];
    return [el('p.hinweis', {
      text: da ? 'Wird gerechnet …' : 'Die Stellen stehen da, sobald die Analyse rechnet.',
    })];
  }
  return [
    ...d.hinweise.map((text) => el('p.hinweis', { text })),
    d.staebe.length ? el('p.qa-erlaeuterung', { text: `Gerechnet: ${d.staebe.join(', ')}.` }) : null,
    d.stellen.length ? tabelle(['Lastfall', 'massgebend für', ...SPALTEN.map(([, kopf]) => kopf)],
      d.stellen.map((s) => [s.name, s.gruende, ...SPALTEN.map(([feld]) => s[feld].toFixed(1))]),
      { textspalten: 2 }) : null,
  ];
}

/** Das Fenster: was es tut, das System, die Stäbe und was daraus wird. */
function inhalt(analyse) {
  const wahl = analyse.aus_system;
  const d = befund(analyse);
  return [
    el('p.qa-erlaeuterung', {
      text: 'Je Kombination des Systems die massgebenden Stellen der Stäbe: grösstes und '
        + 'kleinstes M_y, M_z und N, grösstes |V_z|, |V_y| und |T|, je mit den übrigen '
        + 'Schnittgrössen dort. Jede ist ein Lastfall aller Nachweise dieser Analyse, neben '
        + 'den eigenen.',
    }),
    wahlBlock('Balkensystem', bauteilliste({
      alle: systeme(), gewaehlt: wahl.system, inSandbox: istSandbox(analyse.kennung),
      titel: 'Das System, dessen Stellen Lastfälle dieser Analyse sind – leer: keines',
      setzen: (v) => setzen(analyse, (x) => { x.system = v; }),
    })),
    ...(wahl.system ? [
      ...stabwahl(analyse),
      wahl.stabwahl === 'gewaehlt' && d ? stabschalter(analyse, d) : null,
      ...ergebnis(analyse, d),
    ] : [el('div.leer', {
      text: systeme().length ? 'Kein System gewählt – die Analyse rechnet nur ihre eigenen Lastfälle.'
        : 'Noch kein Balkensystem im Projekt.',
    })]),
  ].filter(Boolean);
}

/** Was auf der Kachel steht: wie viele Stellen -- grau, was fehlt. */
function stand(analyse) {
  if (!analyse.aus_system.system) return { an: false, text: 'kein System' };
  const d = befund(analyse);
  if (!d) return { an: false, text: 'wird gerechnet' };
  const n = d.stellen.length;
  return n ? { an: true, text: `${n} ${n === 1 ? 'Stelle' : 'Stellen'}` }
    : { an: false, text: 'keine Stelle' };
}

/** Die Kachel, für jede Bauweise mit Nachweisen dieselbe. */
export const AUS_SYSTEM = {
  schluessel: 'aus_system',
  name: 'Aus dem Balken­system',
  titel: 'Lastfälle aus dem Balkensystem',
  breit: 6,
  bezug: () => 'N, V in kN · M, T in kNm',
  hilfe: {
    zeilen: [
      ['Stäbe', 'alle mit dieser Analyse als Querschnitt – auch einer, der später dazukommt – oder gewählte, mit welchem Querschnitt auch immer'],
      ['Stellen', 'je Kombination über die Stäbe zusammen; was überall null ist, gibt keine, und eine Stelle, die mehreres zugleich ist, steht einmal da'],
      ['Sprung', 'wo eine Schnittgrösse springt, sagt der Name die Seite: links zum Anfang des Stabs hin, rechts zu seinem Ende; gilt der Extremwert auf beiden Seiten, zählen beide'],
      ['Vorzeichen', 'der Querschnitt vom Anfang des Stabs her gesehen, unten auf der gestrichelten Faser: M_z und V_y kehren sich um'],
      ['Lastfälle', 'nur die Kombinationen des Systems, nicht seine einzelnen Lastfälle'],
    ],
  },
  inhalt,
  stand,
};

/**
 * Die Stellen, die zur Analyse gehören -- je mit ihrem Namen: für den
 * Stand der Gebrauchsnachweise, die auch aus ihnen ableiten.
 */
export function stellenVon(analyse) {
  return befund(analyse)?.stellen || [];
}
