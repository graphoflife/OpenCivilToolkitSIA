/**
 * grundbruch.js -- Mittlere Tafel: Eingaben eines Grundbruchs.
 *
 * Von oben nach unten:
 *
 *     Grundbruch Situation   Bezeichnung; Boden – drainiert oder undrainiert –,
 *                            Fundament, Gelände und Grundwasser, drainiert
 *                            die Sohlreibung, je als Karte; Beschreibung
 *     Einwirkungen           die Kombinationen: N_Ed normal zur Sohle, T_Ed
 *                            in ihrer Richtung, je mit Schalter
 *
 * Gerechnet wird nichts: φ_eff, c_eff und γ' – undrainiert s_u,d – unter den
 * Feldern des Bodens kommen aus der Lösung, die Widerstände rechts ebenso.
 *
 * WINKEL wie in Bild 9.2.15 des Kapitels: T zeigt zur Seite, auf der das
 * Gelände um β abfällt, und die Sohle steigt um α in Richtung von T an. Das
 * Bild der Situation rechts unter «Diagramme» zeigt beides.
 *
 * EINHEITEN UND GRENZEN kommen aus dem Katalog (`katalog.felder`): in
 * welcher Einheit der Kern eine Zahl meint, steht an ihrem Feld im Kern und
 * nur dort. Bis 2026-10-18 stand sie auch hier -- wich sie ab, galt eine
 * Zahl still um 10³ anders, als die Maske sagte. Die Karten mit ihren
 * Feldern, Zeichen und Hinweisen sind die Gruppen der Herleitung
 * (`katalog.vorgaben`, opencivil/geotechnik/fundament.py); bis 2026-11-20
 * standen sie hier ein zweites Mal.
 */

import {
  eingabekarten, erklaerung, feld, namensfeld, panel, verhaltenSchalter,
} from './bausteine.js';
import { el, zahlfeld } from './dom.js';
import { fallkopf, fallzeile } from './faelle.js';
import { span } from './mathe.js';
import { ausVorlage, eintragAendern, feldangabe, naechsterName, zustand } from './zustand.js';

const HILFE = {
  situation: {
    zeilen: [
      ['φ_eff', 'arctan(tan φ_k / γ_φ) nach SIA 267:2013, 5.3.2.1; γ_φ nach 5.3.2.2, Tabelle 1'],
      ['c_eff', 'c_k / γ_c – die Kohäsion nur, wo sie dauerhaft wirkt (SIA 267:2013, 8.5.1.6)'],
      ['s_u,d', 's_u,k / γ_cu, undrainiert; γ_cu nach SIA 267:2013, 5.3.2.2, Tabelle 1'],
      ['Feinkörnig', 'kurzzeitig undrainiert, langfristig drainiert: je ein Grundbruch für beide (SIA 267:2013, 8.5.1.5, 8.5.1.6)'],
      ['γ', 'eine Raumlast über und unter dem Wasser; das Buch nimmt unter ihm die gesättigte (Kap. 1.4), mit der feuchten wird γ\' etwas kleiner, auf der sicheren Seite'],
      ['t, t₁', 'ab Oberkante Terrain: bis zur Sohle, bis zum höchsten Grundwasserspiegel'],
      ['α', 'Neigung der Sohle, positiv, wenn sie in Richtung von T ansteigt (Bild 9.2.15)'],
      ['β', 'Neigung des Geländes, positiv, wenn es auf der Seite von T abfällt'],
      ['b, L', 'b ist die kürzere Seite; ein Streifenfundament ist ein sehr langes. Eine Ausmitte rechnet das Werkzeug nicht: bei ausmittiger Last die wirksamen Masse b − 2e und L − 2e eingeben (Kap. 9.2.11; SIA 267:2013, Figur 4)'],
    ],
    formel: "γ' = γ − γ_w",
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
  const gerechnet = ['phi_eff', 'c_eff', 's_u_d', 'gamma_auftrieb'].map((k) => werte[ids?.[k]]).filter(Boolean);
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

function situationPanel(g) {
  const aendern = (veraenderer) => eintragAendern(g.kennung, veraenderer);
  return panel({
    schluessel: 'grundbruch/Situation', titel: 'Grundbruch Situation',
    zusatz: erklaerung(HILFE.situation.zeilen, HILFE.situation.formel),
  }, [
    el('div.unterkapitel', {}, [
      feld('Bezeichnung', namensfeld({
        wert: g.name, setzen: (name) => aendern((x) => { x.name = name; }),
      })),
    ]),
    // Welche Felder das Verhalten liest, sagt der Kern (Benutzer, 2026-11-19:
    // was nicht gilt, steht nicht da) -- bis dahin hiess φ = 0 undrainiert.
    ...eingabekarten('grundbruch', g, aendern, {
      dazu: {
        Boden: {
          vor: [feld('Verhalten', verhaltenSchalter(g.verhalten,
            (w) => aendern((x) => { x.verhalten = w; })), '')],
          nach: [bemessungswerte(g)],
        },
      },
    }),
    el('div.unterkapitel', {}, [
      el('div.beschreibung', {}, [
        el('label', { text: 'Beschreibung' }),
        el('textarea', {
          rows: 2, value: g.beschreibung || '',
          on: { change: (e) => aendern((x) => { x.beschreibung = e.target.value; }) },
        }),
      ]),
    ]),
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

function einwirkungenPanel(g) {
  const neu = () => eintragAendern(g.kennung, (x) => {
    x.kombinationen.push(ausVorlage('grundbruchkombination',
      { name: naechsterName('Kombination', x.kombinationen) }));
  });
  return panel({
    schluessel: 'grundbruch/Einwirkungen', titel: 'Einwirkungen',
    zusatz: erklaerung(HILFE.einwirkungen.zeilen, HILFE.einwirkungen.formel),
  }, [
    el('div.unterkapitel', {}, [
      g.kombinationen.length
        ? fallkopf([['N_{Ed}', 'N_Ed'], ['T_{Ed}', 'T_Ed']].map(
          ([zeichen, s]) => [zeichen, feldangabe('grundbruchkombination', s).einheit]))
        : el('div.leer', { text: 'Ohne Kombination kein Nachweis.' }),
      ...g.kombinationen.map((_, i) => kombinationZeile(g, i)),
      el('button.knopf-anfuegen', { type: 'button', text: '+ Kombination', on: { click: neu } }),
    ]),
  ]);
}

export function grundbruchEditor(g) {
  return [situationPanel(g), einwirkungenPanel(g)];
}
