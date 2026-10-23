/**
 * setzung.js -- Mittlere Tafel: Eingaben einer Setzungsberechnung.
 *
 * Von oben nach unten:
 *
 *     Setzung Situation   Bezeichnung; Fundament, Pressung in der Sohle und
 *                         Nachweis je als Karte; Beschreibung
 *     Schichten           von der Sohle an nach unten: Dicke, M_E und M'_E
 *
 * Gerechnet wird nichts: die Setzung steht rechts in der Zusammenfassung und
 * im Bild der Situation unter «Diagramme». Einheiten und Grenzen kommen aus
 * dem Katalog (`katalog.felder`), wie beim Grundbruch.
 */

import {
  erklaerung, feld, karte, panel, wahlSchalter, zahlzeile,
} from './bausteine.js';
import { el, zahlfeld } from './dom.js';
import { fallkopf, fallzeile } from './faelle.js';
import { span } from './mathe.js';
import { ausVorlage, feldangabe, naechsterName, projektAendern, zustand } from './zustand.js';

const HILFE = {
  situation: {
    zeilen: [
      ['B, L', 'die Seiten der Lastfläche'],
      ['q_W', 'Pressung aus Wiederbelastung: bis zu der Spannung, die der Boden schon '
        + 'getragen hat -- etwa bis zum Gewicht des Aushubs'],
      ['q_E', 'Pressung aus Erstbelastung: was darüber hinausgeht'],
      ['starr', 'gerechnet im Punkt K, 0.13 L und 0.13 B von einer Ecke (Bild 8.15): die '
        + 'mittlere Setzung'],
      ['schlaff', 'gerechnet unter der Mitte: die grösste Setzung (Kap. 8.10)'],
      ['Δz_max', 'jede Schicht wird in gleich dicke Teilschichten geteilt, höchstens so dick'],
    ],
    formel: 's ≤ s_zul',
  },
  schichten: {
    zeilen: [
      ['Folge', 'von der Sohle an nach unten; unter der letzten gilt der Baugrund als '
        + 'unzusammendrückbar'],
      ['M_E', 'Modul der Erstbelastung -- rechnet mit q_E'],
      ["M'_E", 'Modul der Wiederbelastung -- rechnet mit q_W'],
    ],
    formel: "Δs = J·q_W·Δz / M'_E + J·q_E·Δz / M_E",
  },
};

/** Ändert die Setzung mit dieser Kennung -- der eine Weg, auf dem hier etwas geändert wird. */
function aendernAn(kennung, veraenderer) {
  projektAendern((p) => veraenderer(p.setzungen.find((s) => s.kennung === kennung)));
}

function situationPanel(s) {
  const aendern = (veraenderer) => aendernAn(s.kennung, veraenderer);
  const zahl = (schluessel, text, symbol, mehr = {}) =>
    zahlzeile('setzung', s, schluessel, text, symbol, { ...mehr, aendern });
  return panel({
    schluessel: 'setzung/Situation', titel: 'Setzung Situation',
    zusatz: erklaerung(HILFE.situation.zeilen, HILFE.situation.formel),
  }, [
    el('div.unterkapitel', {}, [
      feld('Bezeichnung', el('input', {
        type: 'text', value: s.name,
        on: { change: (e) => aendern((x) => { x.name = e.target.value; }) },
      })),
    ]),
    karte('Fundament', [
      zahl('B', 'Breite', 'B', { schritt: 0.1 }),
      zahl('L', 'Länge', 'L', { schritt: 0.1 }),
      feld('Steifigkeit', wahlSchalter({
        werte: (zustand.katalog?.setzung?.steifigkeiten || []).map((x) => ({
          wert: x.wert, beschriftung: x.wert, titel: x.beschriftung,
        })),
        gewaehlt: s.steifigkeit,
        setzen: (w) => aendern((x) => { x.steifigkeit = w; }),
        titel: 'Starr: im Punkt K, die mittlere Setzung -- schlaff: unter der Mitte, die grösste',
      }), ''),
    ]),
    karte('Pressung in der Sohle', [
      zahl('q_W', 'Wiederbelastung', 'q_W', {
        schritt: 5, titel: 'Bis zu der Spannung, die der Boden schon getragen hat',
      }),
      zahl('q_E', 'Erstbelastung', 'q_E', {
        schritt: 5, titel: 'Was darüber hinausgeht und den Boden zum ersten Mal belastet',
      }),
    ]),
    karte('Nachweis', [
      zahl('s_zul', 'Zulässige Setzung', 's_{zul}'),
      zahl('dz', 'Teilschichten höchstens', String.raw`\Delta z_{max}`, {
        schritt: 0.1, titel: 'Jede Schicht wird in gleich dicke Teilschichten geteilt',
      }),
    ]),
    el('div.unterkapitel', {}, [
      el('div.beschreibung', {}, [
        el('label', { text: 'Beschreibung' }),
        el('textarea', {
          rows: 2, value: s.beschreibung || '',
          on: { change: (e) => aendern((x) => { x.beschreibung = e.target.value; }) },
        }),
      ]),
    ]),
  ]);
}

function schichtZeile(s, i) {
  const schicht = s.schichten[i];
  const aendern = (veraenderer) => aendernAn(s.kennung, (x) => veraenderer(x.schichten[i]));
  const zahl = (schluessel, schritt, titel) => zahlfeld({
    wert: schicht[schluessel], schritt, angabe: feldangabe('schicht', schluessel), titel,
    beiAenderung: (v) => aendern((x) => { x[schluessel] = v; }),
  });
  return fallzeile({
    fall: schicht, aendern, nameTitel: 'Bezeichnung der Schicht',
    vorn: el('span.schicht-nummer', { text: String(i + 1), title: `${i + 1}. Schicht unter der Sohle` }),
    zahlen: [zahl('d', 0.5, 'Dicke der Schicht'),
      zahl('M_E', 1, 'M_E-Wert der Erstbelastung'),
      zahl('M_E_strich', 1, 'M_E-Wert der Wiederbelastung')],
    entfernenTitel: 'Schicht entfernen',
    entfernen: () => aendernAn(s.kennung, (x) => { x.schichten.splice(i, 1); }),
  });
}

/** Ein Spaltenkopf mit Formelzeichen und der Einheit des Kerns: «M'_E [MN/m²]». */
function kopf(schluessel, symbol) {
  return el('span', {}, [span(symbol), ` [${feldangabe('schicht', schluessel).einheit || ''}]`]);
}

function schichtenPanel(s) {
  const neu = () => aendernAn(s.kennung, (x) => {
    x.schichten.push(ausVorlage('schicht', { name: naechsterName('Schicht', x.schichten) }));
  });
  return panel({
    schluessel: 'setzung/Schichten', titel: 'Schichten',
    zusatz: erklaerung(HILFE.schichten.zeilen, HILFE.schichten.formel),
  }, [
    el('div.unterkapitel', {}, [
      s.schichten.length
        ? fallkopf([kopf('d', 'd'), kopf('M_E', 'M_E'), kopf('M_E_strich', "M'_E")])
        : el('div.leer', { text: 'Ohne Schicht keine Setzung.' }),
      ...s.schichten.map((_, i) => schichtZeile(s, i)),
      el('button.knopf-anfuegen', { type: 'button', text: '+ Schicht', on: { click: neu } }),
    ]),
  ]);
}

export function setzungEditor(s) {
  return [situationPanel(s), schichtenPanel(s)];
}
