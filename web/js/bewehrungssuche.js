/**
 * bewehrungssuche.js -- das Werkzeug, das die Bewehrung einer Platte sucht.
 *
 * Ein Kapitel der Platte (`SUCHE`, eingereiht in `plattenkapitel.js`): der
 * Modus, Teilungen und Durchmesser, die Obergrenze je Lage und der Knopf,
 * der einmal sucht und das Ergebnis in die Lagen schreibt. Gesucht wird im
 * Kern (`api.bewehrungSuchen`); hier stehen die Maske und, ob gerade
 * gesucht wird.
 */

import { api } from './api.js';
import { feld, hakenSchalter } from './bausteine.js';
import { auswahl, el, melden, zahlfeld } from './dom.js';
import { aendern, projektAendern, zustand } from './zustand.js';

/**
 * Welche Platte gerade durchsucht wird.
 *
 * Nur das: der Knopf soll währenddessen «sucht …» heissen und nicht zweimal
 * auslösen. Das Ergebnis steht danach in den Lagen und in der
 * Zusammenfassung -- dort sieht man, ob es aufgeht. Ein Satz daneben, grün
 * oder rot, sagte dasselbe ein zweites Mal und blieb stehen, bis man etwas
 * anderes tat.
 *
 * Ausserhalb des Projekts: das ist ein Vorgang und keine Eigenschaft der
 * Platte, und niemand will ihn in der abgelegten Datei.
 */
const laufendeSuche = new Set();

/** Das Kapitel der Suche -- solange sie läuft, heisst sein Knopf «sucht …». */
export const SUCHE = {
  schluessel: 'automatik',
  name: 'Bewehrung suchen', titel: 'Automatische Bewehrung',
  inhalt: automatikInhalt,
  stand: (q) => (laufendeSuche.has(q.kennung) ? { an: true, text: 'sucht …' }
    : { an: false, text: q.automatik_dicke ? 'mit Dicke' : '' }),
};

/**
 * «Automatische Bewehrung» -- die Bewehrung suchen lassen, statt sie zu setzen.
 *
 * Ein einzelner Knopf, kein Automatismus im Hintergrund: was hier
 * herauskommt, wird in die Lagen geschrieben und steht dann da wie eine
 * Eingabe von Hand -- man sieht es, kann es ändern und kann es lassen.
 * Eine Bewehrung, die sich bei jeder Zahl neu setzt, wäre keine Eingabe mehr.
 *
 * Gesucht wird gegen die Nachweise, die eingeschaltet sind. Die Schalter
 * weiter unten steuern damit unmittelbar, wonach gesucht wird.
 */
function automatikInhalt(querschnitt) {
  const aendern = (veraenderer) => projektAendern((p) => {
    veraenderer(p.querschnitte.find((x) => x.kennung === querschnitt.kennung));
  });
  const quer = querschnitt.automatik_querkraft === true;
  const dicke = querschnitt.automatik_dicke === true;

  // Die Teilungen als Text: «100, 150» liest und tippt sich schneller als
  // eine Liste aus Zahlenfeldern mit Plus- und Minusknöpfen.
  const teilungsfeld = (feld, titel) => el('input', {
    type: 'text', value: (querschnitt[feld] || []).join(', '), title: titel,
    on: {
      change: (e) => aendern((q) => {
        q[feld] = e.target.value.split(/[^0-9.]+/)
          .map(Number).filter((x) => x > 0);
      }),
    },
  });
  const hakenzeile = (an, setzen, text) => el('div.duktilitaetszeile.ist-breit', {}, [
    hakenSchalter(an, setzen, text),
    el('span.postenname', { text }),
    el('span'),
  ]);

  // Die Modi kommen aus dem Kern: ihre Namen stehen dort, wo sie gesucht
  // werden, und nicht ein zweites Mal hier. Die Wahl über die ganze Breite
  // und ohne Beschriftung davor -- der längste Modus braucht die Zeile.
  return [el('div.automatik', {}, [
    auswahl({
      werte: zustand.katalog?.suchmodi || [],
      gewaehlt: querschnitt.automatik_modus,
      titel: 'Modus. Ohne Kräfte: Duktilität, sprödes Versagen, Riss unter Zwang',
      beiAenderung: (v) => aendern((q) => { q.automatik_modus = v; }),
    }),
    // Ein Schalter neben dem Modus: je Dicke sucht das Werkzeug im gewählten
    // Modus. Die Mindestdicke gehört dazu und steht nur dann da.
    hakenzeile(dicke, (wert) => aendern((q) => {
      q.automatik_dicke = wert;
    }), 'Plattendicke optimieren'),
    ...(dicke ? [feld('Mindestdicke', zahlfeld({
      wert: querschnitt.automatik_mindestdicke, schritt: 10, min: 10,
      titel: 'Dünner sucht die Dickenoptimierung keine Platte',
      beiAenderung: (v) => aendern((q) => { q.automatik_mindestdicke = v; }),
    }), 'mm')] : []),
    feld('Teilungen', teilungsfeld('automatik_teilungen',
      'mm, durch Komma getrennt. Grund und Zulage einer Lage: gleiche Teilung'), 'mm'),
    // Leer heisst: kein Mindestdurchmesser -- dann darf eine Lage leer
    // bleiben. Die Null zeigt das Feld darum als leer, und die Pfeile gehen
    // wie bei der Obergrenze durch die Durchmesser: von leer aus auf 2 mm
    // hiesse einen Stab, den es nicht gibt.
    feld('Mindestdurchmesser', zahlfeld({
      wert: querschnitt.automatik_mindestdurchmesser || null,
      stufen: zustand.katalog.durchmesser, min: 0,
      titel: 'Grundbew. jeder Lage mindestens mit diesem ⌀; leer: Lage darf leer bleiben',
      leer: 0,
      beiAenderung: (v) => aendern((q) => { q.automatik_mindestdurchmesser = v; }),
    }), 'mm'),
    ...obergrenze(querschnitt, aendern),
    hakenzeile(querschnitt.automatik_y_wie_x === true, (wert) => aendern((q) => {
      q.automatik_y_wie_x = wert;
    }), 'y-Grundbew. wie x'),
    hakenzeile(quer, (wert) => aendern((q) => {
      q.automatik_querkraft = wert;
    }), 'Bügel mitsuchen'),
    ...(quer ? [feld('Bügelteilungen',
      teilungsfeld('automatik_querkraft_teilungen', 'mm, Raster quadratisch: s_x = s_y'),
      'mm')] : []),
    automatikLeiste(querschnitt),
  ])];
}

/**
 * Die Obergrenze je Lage: Grund und Zulage je als ⌀ @ Teilung, gebaut wie
 * die Lagenzeilen. Es zählt nur die Summe -- wie die Suche sie verteilt, ist
 * frei. Die Summe rechnet der Kern (`obergrenzen` der Lösung).
 */
function obergrenze(querschnitt, aendern) {
  const zeile = (welcher, name) => {
    const posten = querschnitt.automatik_grenze[welcher];
    const setzen = (feldname, wert) => aendern((q) => {
      q.automatik_grenze[welcher][feldname] = wert;
    });
    return el('div.postenzeile', { class: posten.durchmesser > 0 ? '' : 'ist-leer' }, [
      el('span'),
      el('span.postenname', { text: name }),
      el('span.zeichen', { text: '⌀' }),
      zahlfeld({
        wert: posten.durchmesser || null, stufen: zustand.katalog.durchmesser, min: 0,
        titel: '⌀ in mm; Grund und Zulage leer: keine Obergrenze',
        leer: 0,
        beiAenderung: (v) => setzen('durchmesser', v),
      }),
      el('span.zeichen', { text: '@' }),
      zahlfeld({
        wert: posten.abstand, schritt: 25, min: 25, titel: 'Teilung in mm',
        beiAenderung: (v) => setzen('abstand', v),
      }),
      el('span.einheit', { text: 'mm' }),
    ]);
  };
  return [
    feld('Obergrenze je Lage',
      el('span.obergrenze', { text: zustand.loesung?.obergrenzen?.[querschnitt.kennung] ?? '…' }),
      '', 'Grund + Zulage zusammen, in allen Modi; wie die Suche es verteilt, ist frei'),
    zeile('grund', 'Grund'),
    zeile('zulage', 'Zulage'),
  ];
}

function automatikLeiste(querschnitt) {
  const kennung = querschnitt.kennung;
  const laeuft = laufendeSuche.has(kennung);
  const dicke = querschnitt.automatik_dicke === true;
  return el('div.automatik-leiste', {}, [
    el('button.knopf.knopf-haupt', {
      class: laeuft ? 'ist-am-suchen' : '',
      title: dicke ? 'Dünnste Platte suchen, Dicke und Bewehrung übernehmen'
        : 'Einmal suchen, Ergebnis in die Lagen',
      disabled: laeuft,
      on: { click: () => bewehrungErmitteln(kennung) },
    }, laeuft
      // Ein Balken, der läuft: die Suche dauert je nach Platte ein paar
      // Zehntelsekunden bis zu Sekunden. Ein Knopf, der bloss grau wird,
      // sieht in dieser Zeit aus wie einer, der nichts getan hat.
      ? [el('span.laufbalken'), el('span', { text: 'sucht …' })]
      : [el('span', { text: dicke ? 'Dicke und Bewehrung suchen' : 'Bewehrung suchen' })]),
  ]);
}

/**
 * Einmal suchen und das Ergebnis in die Lagen schreiben.
 *
 * Die Lagen bleiben stehen, bis das Ergebnis da ist; dass gesucht wird,
 * zeigt der Laufbalken. Früher wurden sie zuerst geleert -- dafür musste
 * die Oberfläche wissen, welche Posten der Kern sucht, und wusste es bald
 * nicht mehr (die Anhebung der y-Lagen kam dort nie an). Was herauskam,
 * sagt jetzt die Meldung, auch wenn dieselben Durchmesser zurückkommen.
 */
async function bewehrungErmitteln(kennung) {
  laufendeSuche.add(kennung);
  aendern({}, 'bewehrungssuche-start');
  try {
    const antwort = await api.bewehrungSuchen(zustand.projekt, kennung);
    if (antwort.gefunden) {
      // Der Kern gibt das fertige Projekt zurück; übernommen wird die eine
      // gesuchte Platte, damit die anderen unberührt bleiben -- mit der
      // neuen Dicke, wenn sie gesucht wurde.
      projektAendern((p) => {
        const alt = p.querschnitte.findIndex((x) => x.kennung === kennung);
        const neu = antwort.projekt?.querschnitte?.find((x) => x.kennung === kennung);
        if (alt >= 0 && neu) p.querschnitte[alt] = neu;
      });
    }
    melden(antwort.begruendung, !antwort.gefunden);
  } catch (fehler) {
    melden(String(fehler.message || fehler), true);
  } finally {
    // Zuletzt und immer. Hing das Neuzeichnen am Zweig, blieb der Knopf auf
    // «sucht …» stehen, und man musste ein zweites Mal drücken.
    laufendeSuche.delete(kennung);
    aendern({}, 'bewehrungssuche-ende');
  }
}
