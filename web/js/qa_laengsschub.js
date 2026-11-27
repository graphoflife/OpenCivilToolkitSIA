/**
 * qa_laengsschub.js -- die Kachel «Längsschub» einer Blechverbunddecke.
 *
 * Was der Längsschub nach der m-k-Methode (SIA 264, (28)) ausser dem
 * Querschnitt braucht, einmal für die Analyse: m und k aus dem Datenblatt
 * des Blechs, wo das Feld liegt, wie die Last steht und die Spannweite L
 * -- mit zwei Einzellasten dazu ihr Abstand a vom Auflager. Feld und Last
 * sind Schalter mit Bild; darunter steht, was die gewählte Stellung heisst.
 * Die Spannweite braucht auch die Schlankheit L/d_p, mit Einzellasten
 * ebenso.
 *
 * Was noch fehlt, sagt der Kern (`laengsschubFehltVon`): grau auf der
 * Kachel und im Fenster -- der Rest der Decke rechnet weiter. Gerechnet
 * wird hier nichts.
 */

import {
  feld, mitBild, wahlBlock, wahlSchalter,
} from './bausteine.js';
import { el, zahlfeld } from './dom.js';
import { span } from './mathe.js';
import { laengsschubFehltVon } from './qa_zeichnung.js';
import { eintragAendern, feldangabe, katalog } from './zustand.js';

/** Was hinter dem Fragezeichen steht. */
const HILFE = {
  zeilen: [
    ['m, k', 'aus dem Datenblatt des Blechs, aus Versuchen ermittelt – k darf negativ sein'],
    ['L_s', 'gleichmässige Last: ein Viertel der Spannweite; zwei Einzellasten: ihr Abstand a vom Auflager'],
    ['Feld', 'durchlaufend gilt das Endfeld als Einfeld mit 0.9 L, ein Innenfeld mit 0.8 L (5.4.3.5)'],
    ['L/d_p', 'bis 26 muss die Durchbiegung nicht gerechnet werden (5.4.4.3)'],
  ],
  formel: 'V_L,Rd = b · d_p · (m · A_p / (b · L_s) + k) / γ_v',
};

/** Die Zahlen des Längsschubs: Feld, Beschriftung, Schritt der Pfeile, Titel. */
const ZAHLEN = [
  ['blech_m', ['Beiwert ', span('m')], 10, 'Beiwert m der m-k-Methode, aus dem Datenblatt des Blechs (28)'],
  ['blech_k', ['Beiwert ', span('k')], 0.01,
    'Beiwert k der m-k-Methode, aus dem Datenblatt des Blechs (28) – er darf negativ sein'],
  ['blech_L', ['Spannweite ', span('L')], 0.1,
    'Spannweite des Felds – für die Schublänge und die Schlankheit L/d_p'],
];

/** Mit zwei Einzellasten dazu ihr Abstand -- er ist dann die Schublänge. */
const ABSTAND = ['blech_a', ['Abstand ', span('a')], 0.1,
  'Abstand der beiden Einzellasten vom nächsten Auflager, höchstens L/2 – die Schublänge'];

/** Die gewählte Stellung eines Schalters aus dem Katalog: Beschriftung, was sie heisst. */
function gewaehlt(liste, wert) {
  return katalog('querschnittsanalyse', liste).find((x) => x.wert === wert);
}

/** Ein Schalter mit Bild je Stellung, darunter, was die gewählte heisst. */
function schalter(analyse, { beschriftung, liste, bild, feldname, titel }) {
  return [
    wahlBlock(beschriftung, wahlSchalter({
      werte: mitBild(katalog('querschnittsanalyse', liste), bild),
      gewaehlt: analyse[feldname],
      setzen: (wert) => eintragAendern(analyse.kennung, (a) => { a[feldname] = wert; }),
      titel,
    })),
    el('p.qa-erlaeuterung', { text: gewaehlt(liste, analyse[feldname])?.titel || '' }),
  ];
}

/** Eine Zahl -- leer heisst: noch keine, dann fehlt sie grau. */
function zahl(analyse, [schluessel, beschriftung, schritt, titel]) {
  const angabe = feldangabe('querschnittsanalyse', schluessel);
  return feld(beschriftung, zahlfeld({
    wert: analyse[schluessel], leer: null, schritt, angabe, neben: analyse, titel,
    beiAenderung: (v) => eintragAendern(analyse.kennung, (a) => { a[schluessel] = v; }),
  }), angabe.einheit, titel);
}

function inhalt(analyse) {
  const fehlt = laengsschubFehltVon(analyse.kennung);
  const mitAbstand = gewaehlt('blechlasten', analyse.blech_last)?.mit_abstand;
  return [
    ...schalter(analyse, {
      beschriftung: 'Feld', liste: 'blechfelder', bild: 'blechfeld', feldname: 'blech_feld',
      titel: 'Wo das Feld der Decke liegt – danach die Spannweite für den Längsschub',
    }),
    ...schalter(analyse, {
      beschriftung: 'Last', liste: 'blechlasten', bild: 'blechlast', feldname: 'blech_last',
      titel: 'Wie die Last auf dem Feld steht – danach die Schublänge',
    }),
    ...ZAHLEN.map((z) => zahl(analyse, z)),
    mitAbstand ? zahl(analyse, ABSTAND) : null,
    fehlt ? el('p.hinweis', { text: `${fehlt} – bis dahin wird der Längsschub nicht nachgewiesen.` }) : null,
  ];
}

/** Eine eingegebene Zahl, wie sie steht -- ohne eine ein Strich. */
function wie(wert) {
  return wert ?? '–';
}

/**
 * Die Kachel: was der Längsschub braucht. Auf ihr grau, was davon fehlt,
 * sonst m und k.
 */
export const LAENGSSCHUB = {
  schluessel: 'laengsschub',
  name: 'Längs­schub', titel: 'Längsschub nach SIA 264',
  hilfe: HILFE,
  inhalt,
  stand: (a) => {
    const fehlt = laengsschubFehltVon(a.kennung);
    return fehlt ? { an: false, text: fehlt }
      : { an: true, text: `m = ${wie(a.blech_m)}, k = ${wie(a.blech_k)} N/mm²` };
  },
};
