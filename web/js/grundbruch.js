/**
 * grundbruch.js -- Mittlere Tafel: Eingaben eines Grundbruchs.
 *
 * Von oben nach unten:
 *
 *     Grundbruch Situation   Bezeichnung; Boden, Fundament, Gelände und
 *                            Grundwasser, Sohlreibung je als Karte;
 *                            Beschreibung
 *     Einwirkungen           die Kombinationen: N_Ed normal zur Sohle, T_Ed
 *                            in ihrer Richtung, je mit Schalter
 *
 * Gerechnet wird nichts: φ_eff, c_eff und γ' unter den Feldern des Bodens
 * kommen aus der Lösung, die Widerstände rechts ebenso.
 *
 * WINKEL wie in Bild 9.2.15 des Kapitels: T zeigt zur Seite, auf der das
 * Gelände um β abfällt, und die Sohle steigt um α in Richtung von T an. Das
 * Bild der Situation rechts unter «Diagramme» zeigt beides.
 *
 * EINHEITEN UND GRENZEN kommen aus dem Katalog (`katalog.felder`): in
 * welcher Einheit der Kern eine Zahl meint, steht an ihrem Feld im Kern und
 * nur dort. Bis 2026-10-18 stand sie auch hier -- wich sie ab, galt eine
 * Zahl still um 10³ anders, als die Maske sagte.
 */

import {
  erklaerung, feld, karte, panel, zahlzeile as feldzeile,
} from './bausteine.js';
import { el, zahlfeld } from './dom.js';
import { fallkopf, fallzeile } from './faelle.js';
import { span } from './mathe.js';
import { ausVorlage, eintragAendern, feldangabe, naechsterName, zustand } from './zustand.js';

const HILFE = {
  situation: {
    zeilen: [
      ['φ_eff', 'arctan(tan φ_k / γ_φ) nach SIA 267:2013, 5.3.2.1; γ_φ nach 5.3.2.2'],
      ['c_eff', 'c_k / γ_c -- mit φ = 0 rechnet c als undrainierte Scherfestigkeit s_u'],
      ['t, t₁', 'ab Oberkante Terrain: bis zur Sohle, bis zum höchsten Grundwasserspiegel'],
      ['α', 'Neigung der Sohle, positiv, wenn sie in Richtung von T ansteigt (Bild 9.2.15)'],
      ['β', 'Neigung des Geländes, positiv, wenn es auf der Seite von T abfällt'],
      ['b, L', 'b ist die kürzere Seite; ein Streifenfundament ist ein sehr langes'],
    ],
    formel: "γ' = γ − γ_w",
  },
  einwirkungen: {
    zeilen: [
      ['N_Ed', 'normal zur Sohle, Druck positiv'],
      ['T_Ed', 'in der Sohle, zur Seite, auf der das Gelände abfällt'],
      ['Grundbruch', 'N_Ed ≤ N_Rd = σ_f · b · L'],
      ['Gleiten', 'T_Ed ≤ T_Rd = N_Ed · tan δ*'],
    ],
    formel: 'δ_R = arctan(T_Ed / N_Ed)',
  },
};

/** Eine Zahl des Eintrags als Feld: Beschriftung mit Symbol, Einheit, Schrittweite. */
function zahlzeile(g, schluessel, text, symbol, { schritt = 1, titel } = {}) {
  return feldzeile('grundbruch', g, schluessel, text, symbol, {
    schritt, titel, aendern: (veraenderer) => eintragAendern('grundbrueche', g.kennung, veraenderer),
  });
}

/** Die Bemessungswerte des Bodens, wie der Kern sie gerechnet hat -- oder nichts. */
function bemessungswerte(g) {
  const ids = zustand.loesung?.zuordnung?.grundbrueche?.[g.kennung]?.werte;
  const werte = zustand.loesung?.werte || {};
  const gerechnet = ['phi_eff', 'c_eff', 'gamma_auftrieb'].map((k) => werte[ids?.[k]]).filter(Boolean);
  if (!gerechnet.length) return null;
  return el('p.gb-bemessung', {}, gerechnet.flatMap((w, i) => [
    i ? el('span.gb-trenner', { text: '·' }) : null,
    span(`${w.symbol} = ${w.latex}`),
  ]));
}

function situationPanel(g) {
  const aendern = (veraenderer) => eintragAendern('grundbrueche', g.kennung, veraenderer);
  return panel({
    schluessel: 'grundbruch/Situation', titel: 'Grundbruch Situation',
    zusatz: erklaerung(HILFE.situation.zeilen, HILFE.situation.formel),
  }, [
    el('div.unterkapitel', {}, [
      feld('Bezeichnung', el('input', {
        type: 'text', value: g.name,
        on: { change: (e) => aendern((x) => { x.name = e.target.value; }) },
      })),
    ]),
    karte('Boden', [
      zahlzeile(g, 'phi_k', 'Reibungswinkel', String.raw`\varphi_k`,
        { titel: 'Reibungswinkel, charakteristisch' }),
      zahlzeile(g, 'gamma_phi', 'Partialfaktor', String.raw`\gamma_{\varphi}`,
        { schritt: 0.05, titel: 'Partialfaktor des Reibungswinkels, SIA 267:2013, 5.3.2.2' }),
      zahlzeile(g, 'c_k', 'Kohäsion', 'c_k',
        { titel: 'Kohäsion, charakteristisch -- mit φ = 0 die undrainierte Scherfestigkeit' }),
      zahlzeile(g, 'gamma_c', 'Partialfaktor', String.raw`\gamma_c`,
        { schritt: 0.05, titel: 'Partialfaktor der Kohäsion' }),
      zahlzeile(g, 'gamma', 'Raumlast Boden', String.raw`\gamma`, { schritt: 0.5 }),
      zahlzeile(g, 'gamma_w', 'Raumlast Wasser', String.raw`\gamma_w`, { schritt: 0.5 }),
      bemessungswerte(g),
    ]),
    karte('Fundament', [
      zahlzeile(g, 'b', 'Breite', 'b', { schritt: 0.1, titel: 'Die kürzere Seite' }),
      zahlzeile(g, 'L', 'Länge', 'L', { schritt: 0.1 }),
      zahlzeile(g, 't', 'Tiefe der Sohle', 't',
        { schritt: 0.1, titel: 'Oberkante Terrain bis Unterkante Fundament' }),
      zahlzeile(g, 'alpha', 'Sohlneigung', String.raw`\alpha`,
        { titel: 'Positiv, wenn die Sohle in Richtung von T ansteigt' }),
    ]),
    karte('Gelände und Grundwasser', [
      zahlzeile(g, 'beta', 'Geländeneigung', String.raw`\beta`,
        { titel: 'Positiv, wenn das Gelände auf der Seite von T abfällt' }),
      zahlzeile(g, 't1', 'Grundwasser', 't_1',
        { schritt: 0.1, titel: 'Oberkante Terrain bis zum höchsten möglichen Grundwasserspiegel' }),
      zahlzeile(g, 'q_Ed', 'Auflast neben dem Fundament', 'q_{Ed}',
        { titel: 'Bemessungslast auf dem Gelände neben dem Fundament' }),
    ]),
    karte('Sohlreibung', [
      zahlzeile(g, 'delta_faktor', 'Reibung der Sohle', String.raw`\delta^{*}/\varphi`,
        { schritt: 0.05, titel: 'δ* im Verhältnis zu φ -- meist zwischen 2/3 und 1' }),
    ]),
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
  const aendern = (veraenderer) => eintragAendern('grundbrueche', g.kennung,
    (x) => veraenderer(x.kombinationen[i]));
  const zahl = (schluessel, titel) => zahlfeld({
    wert: k[schluessel], schritt: 10, angabe: feldangabe('grundbruchkombination', schluessel),
    titel, leer: 0, beiAenderung: (v) => aendern((x) => { x[schluessel] = v; }),
  });
  return fallzeile({
    fall: k, aendern, was: 'Kombination', nameTitel: 'Bezeichnung der Kombination',
    zahlen: [zahl('N_Ed', 'Normal zur Sohle, Druck positiv'),
      zahl('T_Ed', 'In der Sohle, zur Seite, auf der das Gelände abfällt')],
    entfernenTitel: 'Kombination entfernen',
    entfernen: () => eintragAendern('grundbrueche', g.kennung, (x) => { x.kombinationen.splice(i, 1); }),
  });
}

function einwirkungenPanel(g) {
  const neu = () => eintragAendern('grundbrueche', g.kennung, (x) => {
    x.kombinationen.push(ausVorlage('grundbruchkombination',
      { name: naechsterName('Kombination', x.kombinationen) }));
  });
  return panel({
    schluessel: 'grundbruch/Einwirkungen', titel: 'Einwirkungen',
    zusatz: erklaerung(HILFE.einwirkungen.zeilen, HILFE.einwirkungen.formel),
  }, [
    el('div.unterkapitel', {}, [
      g.kombinationen.length
        ? fallkopf(['N_Ed', 'T_Ed'].map(
          (s) => `${s} [${feldangabe('grundbruchkombination', s).einheit}]`))
        : el('div.leer', { text: 'Ohne Kombination kein Nachweis.' }),
      ...g.kombinationen.map((_, i) => kombinationZeile(g, i)),
      el('button.knopf-anfuegen', { type: 'button', text: '+ Kombination', on: { click: neu } }),
    ]),
  ]);
}

export function grundbruchEditor(g) {
  return [situationPanel(g), einwirkungenPanel(g)];
}
