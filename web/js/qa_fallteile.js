/**
 * qa_fallteile.js -- was Lastfälle und Stabilitätsfälle einer Querschnittsanalyse teilen.
 *
 * Die Bauweise, wie der Kern sie nennt (`bauweiseVon`), die Wahl der
 * Biegung, die der Analyse gehört, und beim Holz, wie es rechnet und ob
 * eine Einwirkung stossartig ist. Die Tragsicherheit (querschnittsanalyse.js)
 * und Knicken und Kippen (qa_stabilitaet.js) zeigen sie gleich.
 *
 * Gerechnet wird nichts.
 */

import { wahlBlock, wahlSchalter } from './bausteine.js';
import { bauweiseVon } from './qa_zeichnung.js';
import { eintragAendern, katalog } from './zustand.js';

/** Ob der Querschnitt aus Holz ist -- das sagt der Kern (`bauweiseVon`). */
export function ausHolz(analyse) {
  return bauweiseVon(analyse.kennung) === 'holz';
}

/** Ob der Querschnitt im Verbund ist -- das sagt der Kern (`bauweiseVon`). */
export function imVerbund(analyse) {
  return bauweiseVon(analyse.kennung) === 'verbund';
}

/** Ob der Querschnitt eine Blechverbunddecke ist -- das sagt der Kern (`bauweiseVon`). */
export function imBlechverbund(analyse) {
  return bauweiseVon(analyse.kennung) === 'blechverbund';
}

/** Was beim Holz an der Stelle der Rechenwahl steht: es rechnet immer gleich. */
export const HOLZ_RECHNET = 'Das Holz rechnet linear, mit den Bemessungswerten der Norm und dem '
  + 'η_w der Feuchteklasse – ein stossartiger Fall dazu mit η_t.';

/**
 * Beim Holz, je Fall: ob die Einwirkung stossartig ist -- dann hebt η_t
 * seine Bemessungswerte. Die Stellungen und was sie heissen, kommen aus dem
 * Kern. Er steht unter den Zahlen, über die ganze Breite: neben dem Namen
 * hat nur eine Zahlenspalte Platz, und dort ragte er aus dem Fenster.
 */
export function dauerSchalter(fall, aendern) {
  return wahlSchalter({
    werte: katalog('querschnittsanalyse', 'einwirkungsdauern'),
    gewaehlt: !!fall.stossartig,
    setzen: (wert) => aendern((x) => { x.stossartig = wert; }),
    titel: 'Dauer der Einwirkung – stossartig hebt die Bemessungswerte des Holzes',
  });
}

/**
 * Ob der Querschnitt nur um y gebogen wird oder um beide Achsen -- je
 * Stellung die Nulllinie im Bild, statt Häkchen und Satz (Benutzer,
 * 2026-11-19); was sonst noch gilt, steht im Titel der Stellung. Dieselbe
 * Wahl in der Tragsicherheit und bei Knicken und Kippen: sie gehört der
 * Analyse.
 */
export function biegungsWahl(analyse) {
  return wahlBlock('Biegung', wahlSchalter({
    werte: [
      { wert: true, beschriftung: 'einachsig', zeichen: 'biegung-einachsig',
        titel: 'Nur um y: die Nulllinie bleibt waagrecht; M_z und V_y zählen nicht' },
      { wert: false, beschriftung: 'zweiachsig', zeichen: 'biegung-zweiachsig',
        titel: 'N, M_y und M_z gleichzeitig: die Nulllinie liegt schief' },
    ],
    gewaehlt: !!analyse.einachsig,
    setzen: (wert) => eintragAendern(analyse.kennung, (a) => { a.einachsig = wert; }),
    titel: 'Nur um y gebogen oder um beide Achsen',
  }));
}
