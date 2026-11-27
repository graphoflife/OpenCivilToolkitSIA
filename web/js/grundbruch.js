/**
 * grundbruch.js -- Mittlere Tafel: Eingaben eines Grundbruchs.
 *
 * Von oben nach unten:
 *
 *     Grundbruch   Bezeichnung und Beschreibung
 *     Eingaben     je eine Kachel mit Sinnbild und dem Wichtigsten
 *                  (Benutzer, 2026-11-25), ein Klick öffnet ihr Fenster:
 *                  Boden – drainiert oder undrainiert –, Fundament,
 *                  Gelände und Grundwasser, drainiert die Sohlreibung,
 *                  die Einwirkungen: N_Ed normal zur Sohle, T_Ed in ihrer
 *                  Richtung, je Kombination mit Schalter
 *
 * Gerechnet wird nichts: φ_eff, c_eff, γ_w und γ' – undrainiert s_u,d – unter
 * den Feldern des Bodens kommen aus der Lösung, die Widerstände rechts ebenso.
 *
 * DAS WASSER ist seit 2026-11-27 ein Material des Projekts, eine Flüssigkeit:
 * drainiert wählt der Boden sie aus der Liste, γ_w ist ihre Raumlast. Bis
 * dahin stand γ_w = 10 kN/m³ als Zahl unter den Feldern.
 *
 * WINKEL wie in Bild 9.2.15 des Kapitels: T zeigt zur Seite, auf der das
 * Gelände um β abfällt, und die Sohle steigt um α in Richtung von T an. Das
 * Bild der Situation rechts unter «Diagramme» zeigt beides.
 *
 * EINHEITEN UND GRENZEN kommen aus dem Katalog (`katalog.felder`): in
 * welcher Einheit der Kern eine Zahl meint, steht an ihrem Feld im Kern und
 * nur dort. Bis 2026-10-18 stand sie auch hier -- wich sie ab, galt eine
 * Zahl still um 10³ anders, als die Maske sagte. Die Kacheln mit ihren
 * Feldern, Zeichen und Hinweisen sind die Gruppen der Herleitung
 * (`katalog.vorgaben`, opencivil/geotechnik/fundament.py); bis 2026-11-20
 * standen sie hier ein zweites Mal.
 */

import {
  beschreibung, bezeichnung, eingabegruppen, feld, fehlendesMaterial, materialliste, panel,
  verhaltenSchalter,
} from './bausteine.js';
import { el, zahlfeld } from './dom.js';
import { anfuegenKnopf, fallkopf, fallzeile } from './faelle.js';
import {
  gruppenkapitel, kapitelFenster, kapitelPanel, zeilenstand,
} from './kapitel.js';
import { span } from './mathe.js';
import { ausVorlage, eintragAendern, feldangabe, zustand } from './zustand.js';

const HILFE = {
  boden: {
    zeilen: [
      ['φ_eff', 'arctan(tan φ_k / γ_φ) nach SIA 267:2013, 5.3.2.1; γ_φ nach 5.3.2.2, Tabelle 1'],
      ['c_eff', 'c_k / γ_c – die Kohäsion nur, wo sie dauerhaft wirkt (SIA 267:2013, 8.5.1.6)'],
      ['s_u,d', 's_u,k / γ_cu, undrainiert; γ_cu nach SIA 267:2013, 5.3.2.2, Tabelle 1'],
      ['Feinkörnig', 'kurzzeitig undrainiert, langfristig drainiert: je ein Grundbruch für beide (SIA 267:2013, 8.5.1.5, 8.5.1.6)'],
      ['γ', 'eine Raumlast über und unter dem Wasser; das Buch nimmt unter ihm die gesättigte (Kap. 1.4), mit der feuchten wird γ\' etwas kleiner, auf der sicheren Seite'],
      ['Wasser', 'drainiert: das Grundwasser, eine Flüssigkeit aus den Materialien; γ_w ist ihre Raumlast, beim Wasser 10 kN/m³'],
    ],
    formel: "γ' = γ − γ_w",
  },
  fundament: {
    zeilen: [
      ['b, L', 'b ist die kürzere Seite; ein Streifenfundament ist ein sehr langes. Eine Ausmitte rechnet das Werkzeug nicht: bei ausmittiger Last die wirksamen Masse b − 2e und L − 2e eingeben (Kap. 9.2.11; SIA 267:2013, Figur 4)'],
      ['t', 'ab Oberkante Terrain bis zur Sohle'],
      ['α', 'Neigung der Sohle, positiv, wenn sie in Richtung von T ansteigt (Bild 9.2.15)'],
    ],
  },
  gelaende: {
    zeilen: [
      ['t₁', 'ab Oberkante Terrain bis zum höchsten Grundwasserspiegel'],
      ['β', 'Neigung des Geländes, positiv, wenn es auf der Seite von T abfällt'],
    ],
  },
  sohlreibung: {
    zeilen: [
      ['δ_k', 'k_δ · φ_k, höchstens 35° (SIA 267:2013, 8.4.1.1)'],
      ['undrainiert', 'gleitet das Fundament im Boden: T_Rd = b · L · s_u,d, Gl. (32) – ohne Sohlreibung'],
    ],
    formel: 'tan δ_d = tan δ_k / γ_φ',
  },
  einwirkungen: {
    zeilen: [
      ['N_Ed', 'normal zur Sohle, Druck positiv; das günstige Eigengewicht von Fundament und Hinterfüllung mit γ_G,inf = 1.0 (SIA 267:2013, 8.5.2.4)'],
      ['T_Ed', 'in der Sohle, zur Seite, auf der das Gelände abfällt'],
      ['Grundbruch', 'N_Ed ≤ N_Rd = σ_f · b · L'],
      ['Gleiten', 'T_Ed ≤ T_Rd = N_Ed · tan δ_d, undrainiert b · L · s_u,d (SIA 267:2013, 8.5.2.2)'],
    ],
    formel: 'δ_R = arctan(T_Ed / N_Ed)',
  },
};

/**
 * Die Bemessungswerte des Bodens, wie der Kern sie gerechnet hat -- oder
 * nichts. Ging die letzte Rechnung nicht, gehören sie zur Eingabe davor:
 * dann stehen sie blass und sagen es (bis 2026-11-19 ohne Kennzeichen).
 */
function bemessungswerte(g) {
  const ids = zustand.loesung?.zuordnung?.grundbrueche?.[g.kennung]?.werte;
  const werte = zustand.loesung?.werte || {};
  const gerechnet = ['phi_eff', 'c_eff', 's_u_d', 'gamma_w', 'gamma_auftrieb']
    .map((k) => werte[ids?.[k]]).filter(Boolean);
  if (!gerechnet.length) return null;
  const alt = Boolean(zustand.rechenfehler);
  return el(alt ? 'p.gb-bemessung.ist-ohne-wirkung' : 'p.gb-bemessung', {}, [
    ...gerechnet.flatMap((w, i) => [
      i ? el('span.gb-trenner', { text: '·' }) : null,
      span(`${w.symbol} = ${w.latex}`),
    ]),
    alt ? el('span.gb-trenner', { text: '· aus der Rechnung davor' }) : null,
  ]);
}

function kopfPanel(g) {
  const aendern = (veraenderer) => eintragAendern(g.kennung, veraenderer);
  return panel({ schluessel: 'grundbruch/Situation', titel: 'Grundbruch' }, [
    el('div.unterkapitel', {}, [bezeichnung(g, aendern), beschreibung(g, aendern)]),
  ]);
}

function kombinationZeile(g, i) {
  const k = g.kombinationen[i];
  const aendern = (veraenderer) => eintragAendern(g.kennung, (x) => veraenderer(x.kombinationen[i]));
  const zahl = (schluessel, titel) => zahlfeld({
    wert: k[schluessel], schritt: 10, angabe: feldangabe('grundbruchkombination', schluessel),
    titel, leer: 0, beiAenderung: (v) => aendern((x) => { x[schluessel] = v; }),
  });
  return fallzeile({
    fall: k, aendern, was: 'Kombination', nameTitel: 'Bezeichnung der Kombination',
    liste: { kennung: g.kennung, pfad: 'kombinationen', index: i },
    zahlen: [zahl('N_Ed', 'Normal zur Sohle, Druck positiv'),
      zahl('T_Ed', 'In der Sohle, zur Seite, auf der das Gelände abfällt')],
    entfernenTitel: 'Kombination entfernen',
    entfernen: () => eintragAendern(g.kennung, (x) => { x.kombinationen.splice(i, 1); }),
  });
}

/** Die Kombinationen: je eine Zeile, darunter der Knopf für eine weitere. */
const EINWIRKUNGEN = {
  schluessel: 'kombinationen',
  name: 'Einwirkungen', titel: 'Einwirkungen',
  hilfe: HILFE.einwirkungen,
  inhalt: (g) => [el('div.unterkapitel', {}, [
    g.kombinationen.length
      ? fallkopf([['N_{Ed}', 'N_Ed'], ['T_{Ed}', 'T_Ed']].map(
        ([zeichen, s]) => [zeichen, feldangabe('grundbruchkombination', s).einheit]))
      : el('div.leer', { text: 'Ohne Kombination kein Nachweis.' }),
    ...g.kombinationen.map((_, i) => kombinationZeile(g, i)),
    anfuegenKnopf('Kombination', (name) => eintragAendern(g.kennung, (x) => {
      x.kombinationen.push(ausVorlage('grundbruchkombination', { name: name(x.kombinationen) }));
    })),
  ])],
  stand: (g) => zeilenstand(g.kombinationen, 'Kombination', 'Kombinationen', 'keine Kombination'),
};

/**
 * Die Kacheln: je Gruppe der Vorgaben eine, dazu die Einwirkungen. Welche
 * Felder das Verhalten liest, sagt der Kern (Benutzer, 2026-11-19: was
 * nicht gilt, steht nicht da) -- bis dahin hiess φ = 0 undrainiert.
 * Undrainiert hat die Sohlreibung nichts zu zeigen und keine Kachel, und
 * der Boden braucht kein Wasser: dort gelten totale Spannungen.
 */
function kapitel(g) {
  const aendern = (veraenderer) => eintragAendern(g.kennung, veraenderer);
  const vorgaben = eingabegruppen('grundbruch', g, aendern);
  const drainiert = g.verhalten === 'drainiert';
  const wasser = drainiert
    ? feld('Wasser', materialliste({
      art: 'fluessigkeit', gewaehlt: g.wasser, titel: 'Das Grundwasser: seine Raumlast ist γ_w',
      setzen: (w) => aendern((x) => { x.wasser = w; }),
    }), '')
    : null;
  const kacheln = [
    gruppenkapitel(vorgaben, 'Boden', {
      zeichen: 'boden', werte: ['phi_k', 'c_k', 's_u'], hilfe: HILFE.boden,
      vor: [feld('Verhalten', verhaltenSchalter(g.verhalten,
        (w) => aendern((x) => { x.verhalten = w; })), '')],
      nach: [wasser, bemessungswerte(g)],
      fehlt: drainiert ? fehlendesMaterial('fluessigkeit', g.wasser) : '',
    }),
    gruppenkapitel(vorgaben, 'Fundament', {
      zeichen: 'fundament', werte: ['b', 'L'], hilfe: HILFE.fundament,
    }),
    gruppenkapitel(vorgaben, 'Gelände und Grundwasser', {
      zeichen: 'gelaende', werte: ['t1', 'beta'], hilfe: HILFE.gelaende,
    }),
    gruppenkapitel(vorgaben, 'Sohlreibung', {
      zeichen: 'sohlreibung', werte: ['delta_faktor'], hilfe: HILFE.sohlreibung,
    }),
    EINWIRKUNGEN,
  ];
  vorgaben.vollstaendig();
  return [{ titel: '', kapitel: kacheln.filter(Boolean) }];
}

export function grundbruchEditor(g) {
  return [kopfPanel(g),
    kapitelPanel(g, kapitel(g), { schluessel: 'grundbruch/Kapitel', titel: 'Eingaben' })];
}

/** Das offene Fenster eines Grundbruchs -- oder null. */
export function grundbruchFenster(g, schluessel) {
  return kapitelFenster(g, kapitel(g), schluessel);
}
