/**
 * nachweise.js -- die untere Hälfte der Plattentafel: was nachgewiesen wird.
 *
 * Vier Kapitel in der Reihenfolge, in der auch der Bericht sie führt:
 * Tragsicherheit (samt Knicken), Duktilität, sprödes Versagen und die
 * Rissbreitenbegrenzung. Dazu das Werkzeug, das die Bewehrung sucht.
 *
 * Eigenes Modul, weil `editor.js` sonst über tausend Zeilen läge und die
 * beiden Hälften wenig miteinander zu tun haben: oben steht, was die Platte
 * *ist* -- Abmessungen, Material, Lagen --, hier steht, was von ihr
 * *verlangt* wird. Geteilt wird nur der Schalter und die Feldzeile, und die
 * stehen in `bausteine.js`.
 *
 * Gerechnet wird hier nichts. Jede Zeile beschreibt eine Eingabe; die Zahlen
 * dazu bildet der Kern, sobald der Nachweis läuft.
 */

import { api } from './api.js';
import { feld, hakenSchalter, lagenwahl, richtungVon, richtungsWahl } from './bausteine.js';
import { auswahl, el, zahlfeld } from './dom.js';
import { aendern, projektAendern, zustand } from './zustand.js';

/**
 * Was die letzte Bewehrungssuche je Platte gemeldet hat.
 *
 * Ausserhalb des Baums: das Ergebnis übernehmen heisst, das Projekt zu
 * ändern, und das zeichnet die Tafel neu. Stünde die Meldung im DOM, wäre
 * sie genau in dem Augenblick weg, in dem sie etwas zu sagen hat. Ins
 * Projekt gehört sie auch nicht -- sie beschreibt einen Vorgang, keine
 * Eigenschaft der Platte, und niemand will sie in der abgelegten Datei.
 */
const automatikMeldungen = new Map();

/** Die Nachweiskapitel einer Platte, von der Tragsicherheit bis zum Riss. */
export function nachweiseBlock(querschnitt) {
  const aendernAn = (veraenderer) => projektAendern((p) => {
    veraenderer(p.querschnitte.find((x) => x.kennung === querschnitt.kennung));
  });
  return el('div.feldgruppe', {}, [
    el('h3', { text: 'Nachweise' }),
    el('div.unterkapitel', {}, [
      el('div.unterkapitel-kopf', {}, [
        el('span', { text: 'Tragsicherheitsnachweise' }),
        el('button.knopf.knopf-zart', {
          text: '+ Einwirkung',
          on: {
            click: () => aendernAn((q) => q.kombinationen.push({
              name: `Fall ${q.kombinationen.length + 1}`,
              M_Ed: 100, N_Ed: 0, V_Ed: 0,
              art: 'automatisch', richtung: 'x',
            })),
          },
        }),
      ]),
      querschnitt.kombinationen.length
        ? el('div.einwirkung.ist-kopf', {}, [
          el('span'),
          el('span', { text: 'Bezeichnung' }),
          el('span', { text: 'M_Ed [kNm]' }),
          el('span', { text: 'N_Ed [kN]' }),
          el('span', { text: 'V_Ed [kN/m]' }),
          el('span', { text: 'Ri.' }),
          el('span'),
        ])
        : null,
      ...(querschnitt.kombinationen.length
        ? querschnitt.kombinationen.map((_, i) => einwirkungZeile(querschnitt, i))
        : [el('div.leer', { text: 'Ohne Einwirkung kein Nachweis.' })]),
    ]),

    el('div.unterkapitel', {}, [
      el('div.unterkapitel-kopf', {}, [
        el('span', { text: 'Duktilitätsnachweise' }),
        el('span.kurvenhinweis', { text: 'x / d ≤ 0.35 bei M_Ed = 0' }),
      ]),
      ...[1, 2, 3, 4].map((nummer) => duktilitaetZeile(querschnitt, nummer)),
    ]),

    lagenkapitel(querschnitt, {
      titel: 'Nachweise gegen sprödes Versagen',
      feld: 'sproede_lagen',
      hinweis: 'M_Rd(N_Ed = 0) ≥ M_Riss',
      beschriftung: (n) => `Rissmoment ${n}. Lage`,
      was: 'Nachweis',
    }),

    mindestbewehrungsBlock(querschnitt),
    knickBlock(querschnitt),
  ]);
}

function einwirkungZeile(querschnitt, index) {
  const k = querschnitt.kombinationen[index];
  const aendern = (veraenderer) => projektAendern((p) => {
    veraenderer(p.querschnitte.find((x) => x.kennung === querschnitt.kennung).kombinationen[index]);
  });

  const zahl = (feld, titel, schritt = 10) => zahlfeld({
    wert: k[feld], schritt, titel,
    beiAenderung: (v) => aendern((x) => { x[feld] = v ?? 0; }),
  });

  const an = k.aktiv !== false;
  return el('div.einwirkung', { class: an ? '' : 'ist-aus' }, [
    hakenSchalter(an, (wert) => aendern((x) => { x.aktiv = wert; }), 'Lastfall'),
    el('input.ew-name', {
      type: 'text', value: k.name, title: 'Bezeichnung der Einwirkung',
      on: { change: (e) => aendern((x) => { x.name = e.target.value; }) },
    }),
    zahl('M_Ed', 'Bemessungsmoment in kNm'),
    zahl('N_Ed', 'Normalkraft in kN – Zug positiv, Druck negativ'),
    zahl('V_Ed', 'Querkraft in kN/m – 0 heisst: kein Querkraftnachweis'),
    richtungsWahl(k.richtung || 'beide',
      (wert) => aendern((x) => { x.richtung = wert; })),
    el('button.knopf.knopf-zart.knopf-gefahr', {
      text: '×', title: 'Einwirkung entfernen',
      on: {
        click: () => projektAendern((p) => {
          p.querschnitte.find((x) => x.kennung === querschnitt.kennung)
            .kombinationen.splice(index, 1);
        }),
      },
    }),
  ]);
}

/**
 * Ein Kapitel mit vier Lagenschaltern -- dieselbe Gestalt wie die Duktilität.
 *
 * Drei Nachweise sind so gebaut (Duktilität, sprödes Versagen, Zwängung auf
 * Biegung); dreimal dieselben zwanzig Zeilen wären dreimal dieselbe Gelegenheit
 * auseinanderzulaufen.
 */
function lagenkapitel(querschnitt, { titel, feld, hinweis, beschriftung, was }) {
  const vorgabe = [true, false, false, false];
  const wahl = lagenwahl(querschnitt[feld], vorgabe);

  const setzen = (nummer, wert) => projektAendern((p) => {
    const q = p.querschnitte.find((x) => x.kennung === querschnitt.kennung);
    q[feld] = lagenwahl(q[feld], vorgabe);
    q[feld][nummer - 1] = wert;
  });

  return el('div.unterkapitel', {}, [
    el('div.unterkapitel-kopf', {}, [
      el('span', { text: titel }),
      hinweis ? el('span.kurvenhinweis', { text: hinweis }) : null,
    ]),
    ...[1, 2, 3, 4].map((nummer) => {
      const lage = querschnitt.lagen[nummer - 1];
      const leer = !(lage.grund.durchmesser > 0 || lage.zulage.durchmesser > 0);
      const richtung = richtungVon(querschnitt, nummer);
      return el('div.duktilitaetszeile', {}, [
        el('span.postenname', { text: beschriftung(nummer) }),
        el('span.richtung', {
          text: richtung, class: `lage-${richtung}`,
          title: `Tragrichtung der ${nummer}. Lage`,
        }),
        hakenSchalter(wahl[nummer - 1], (wert) => setzen(nummer, wert), was),
        el('span.kurvenhinweis', {
          text: (wahl[nummer - 1] && leer) ? 'Lage nicht definiert' : '',
        }),
      ]);
    }),
  ]);
}

/**
 * Knicken -- Druckkraft, Moment 1. Ordnung, Länge und Knicklänge je Fall.
 *
 * Nur in x-Richtung: eine Knicklänge gehört zu einer Tragrichtung, und in y
 * wäre die Breite der Platte die Länge.
 */
function knickBlock(querschnitt) {
  const faelle = querschnitt.knickfaelle || [];
  const aendern = (veraenderer) => projektAendern((p) => {
    veraenderer(p.querschnitte.find((x) => x.kennung === querschnitt.kennung));
  });

  return el('div.unterkapitel', {}, [
    el('div.unterkapitel-kopf', {}, [
      el('span', { text: 'Knicken' }),
      el('button.knopf.knopf-zart', {
        text: '+ Knicknachweis',
        on: {
          click: () => aendern((q) => {
            q.knickfaelle = q.knickfaelle || [];
            q.knickfaelle.push({
              name: `Stütze ${q.knickfaelle.length + 1}`,
              N_Ed: -500, M_Ed_1: 20, laenge: 3, knicklaenge: 3, aktiv: true,
            });
          }),
        },
      }),
    ]),
    faelle.length
      ? el('div.einwirkung.ist-knick.ist-kopf', {}, [
        el('span'),
        el('span', { text: 'Bezeichnung' }),
        el('span', { text: 'N_Ed [kN]' }),
        el('span', { text: 'M_Ed,1 [kNm]' }),
        el('span', { text: 'l [m]' }),
        el('span', { text: 'l_cr [m]' }),
        el('span'),
      ])
      : null,
    ...(faelle.length
      ? faelle.map((_, i) => knickZeile(querschnitt, i))
      : [el('div.leer', { text: 'Kein Knicknachweis – nur in x-Richtung möglich.' })]),
  ]);
}

function knickZeile(querschnitt, index) {
  const k = (querschnitt.knickfaelle || [])[index];
  const aendern = (veraenderer) => projektAendern((p) => {
    veraenderer(p.querschnitte.find((x) => x.kennung === querschnitt.kennung)
      .knickfaelle[index]);
  });
  const zahl = (feld, titel, schritt) => zahlfeld({
    wert: k[feld], schritt, titel,
    beiAenderung: (v) => aendern((x) => { x[feld] = v ?? 0; }),
  });

  const aktiv = k.aktiv !== false;
  return el('div.einwirkung.ist-knick', { class: aktiv ? '' : 'ist-aus' }, [
    hakenSchalter(aktiv, (wert) => aendern((x) => { x.aktiv = wert; }), 'Knicknachweis'),
    el('input.ew-name', {
      type: 'text', value: k.name, title: 'Bezeichnung des Knicknachweises',
      on: { change: (e) => aendern((x) => { x.name = e.target.value; }) },
    }),
    zahl('N_Ed', 'Druckkraft in kN – negativ', 50),
    zahl('M_Ed_1', 'Moment 1. Ordnung in kNm', 10),
    zahl('laenge', 'Systemlänge in m – geht in die Schiefstellung ein', 0.5),
    zahl('knicklaenge', 'Knicklänge in m', 0.5),
    el('button.knopf.knopf-zart.knopf-gefahr', {
      text: '×', title: 'Knicknachweis entfernen',
      on: {
        click: () => projektAendern((p) => {
          p.querschnitte.find((x) => x.kennung === querschnitt.kennung)
            .knickfaelle.splice(index, 1);
        }),
      },
    }),
  ]);
}

/**
 * Mindestbewehrung: was angesetzt wird und wogegen.
 *
 * Zwei Teile. Oben die Zwängung -- eine Annahme über das Tragwerk, nicht über
 * die Platte, darum ausgeschaltet, bis jemand sie trifft. Unten die häufigen
 * Lastfälle, gegen die später die Stahlspannung begrenzt wird.
 *
 * Gerechnet wird hier nichts: die 70-%-Regel steht als Satz da, die Zahlen
 * dazu bildet der Kern, sobald der Nachweis läuft.
 */
function mindestbewehrungsBlock(querschnitt) {
  const aus70 = querschnitt.haeufige_aus_tragsicherheit !== false;
  const faelle = querschnitt.haeufige || [];

  const aendern = (veraenderer) => projektAendern((p) => {
    veraenderer(p.querschnitte.find((x) => x.kennung === querschnitt.kennung));
  });

  // Der Zeilentitel sagt schon, was der Schalter tut. Die Spalte rechts
  // wiederholte das in einem ganzen Satz und machte die Tafel breit.
  const zwaengung = (feld, beschriftung) => el('div.duktilitaetszeile.ist-breit', {}, [
    el('span.postenname', { text: beschriftung }),
    hakenSchalter(!!querschnitt[feld],
      (wert) => aendern((q) => { q[feld] = wert; }), 'Zwängung'),
    el('span.kurvenhinweis', { text: '' }),
  ]);

  return el('div.unterkapitel', {}, [
    el('div.unterkapitel-kopf', {}, [
      el('span', { text: 'Nachweise der Rissbreitenbegrenzung' }),
    ]),

    el('div.unterkapitel-kopf', { style: { marginTop: '8px' } }, [
      el('span', { text: 'Begrenzung der Rissbreiten unter aufgezwungenen '
        + 'Verformungen' }),
    ]),
    zwaengung('zwaengung_x', 'Zwängung auf Normalkraft x'),
    zwaengung('zwaengung_y', 'Zwängung auf Normalkraft y'),
    zwaengung('zwaengung_begrenzt', 'Begrenzung auf 500 mm'),

    // Ohne eigene Überschrift: die vier Zeilen schreiben ihren Nachweis selbst
    // aus und stehen unter derselben Aufschrift wie die Normalkraft-Zwängung.
    ...[1, 2, 3, 4].map((nummer) => zwaengungBiegungZeile(querschnitt, nummer)),

    el('div.unterkapitel-kopf', { style: { marginTop: '8px' } }, [
      el('span', { text: 'Verhindern des Fliessens für häufige Lastfälle' }),
      el('button.knopf.knopf-zart', {
        text: '+ Lastfall',
        on: {
          click: () => aendern((q) => {
            q.haeufige = q.haeufige || [];
            q.haeufige.push({
              name: `Häufig ${q.haeufige.length + 1}`,
              M_Ed: 0, N_Ed: 0, richtung: 'beide', aktiv: true,
            });
          }),
        },
      }),
    ]),

    el('div.duktilitaetszeile.ist-breit', {}, [
      el('span.postenname', { text: '70 % der Tragsicherheitseinwirkungen' }),
      hakenSchalter(aus70, (wert) => aendern((q) => {
        q.haeufige_aus_tragsicherheit = wert;
      }), 'Ableitung'),
      el('span.kurvenhinweis', { text: '' }),
    ]),

    // Die abgeleiteten Fälle und eigene schliessen sich nicht aus: wer die
    // 70 % nimmt, kann trotzdem einen Fall von Hand dazustellen, den keine
    // Tragsicherheitskombination abbildet.
    ...[
      faelle.length
        ? el('div.einwirkung.ist-kopf.ist-haeufig', {}, [
          el('span'),
          el('span', { text: 'Bezeichnung' }),
          el('span', { text: 'M_Ed [kNm]' }),
          el('span', { text: 'N_Ed [kN]' }),
          el('span', { text: 'Ri.' }),
          el('span'),
        ])
        : null,
      ...(faelle.length
        ? faelle.map((_, i) => haeufigZeile(querschnitt, i))
        : [el('div.leer', {
          text: aus70
            ? 'Nur die abgeleiteten Fälle.'
            : 'Noch kein häufiger Lastfall.',
        })]),
    ],
  ]);
}

/** Eine Lagenzeile der Zwängung auf Biegung. */
function zwaengungBiegungZeile(querschnitt, nummer) {
  const vorgabe = [true, false, false, false];
  const wahl = lagenwahl(querschnitt.zwaengung_biegung_lagen, vorgabe);
  const richtung = richtungVon(querschnitt, nummer);
  const setzen = (wert) => projektAendern((p) => {
    const q = p.querschnitte.find((x) => x.kennung === querschnitt.kennung);
    q.zwaengung_biegung_lagen = lagenwahl(q.zwaengung_biegung_lagen, vorgabe);
    q.zwaengung_biegung_lagen[nummer - 1] = wert;
  });
  return el('div.duktilitaetszeile', {}, [
    el('span.postenname', { text: `Zwängung auf Biegung ${nummer}. Lage` }),
    el('span.richtung', {
      text: richtung, class: `lage-${richtung}`,
      title: `Tragrichtung der ${nummer}. Lage`,
    }),
    hakenSchalter(wahl[nummer - 1], setzen, 'Nachweis'),
    el('span.kurvenhinweis', { text: '' }),
  ]);
}

/** Ein häufiger Lastfall auf einer Zeile -- wie eine Einwirkung, ohne Querkraft. */
function haeufigZeile(querschnitt, index) {
  const k = (querschnitt.haeufige || [])[index];
  const aendern = (veraenderer) => projektAendern((p) => {
    veraenderer(p.querschnitte.find((x) => x.kennung === querschnitt.kennung)
      .haeufige[index]);
  });

  const aktiv = k.aktiv !== false;
  return el('div.einwirkung.ist-haeufig', { class: aktiv ? '' : 'ist-aus' }, [
    hakenSchalter(aktiv, (wert) => aendern((x) => { x.aktiv = wert; }), 'Lastfall'),
    el('input.ew-name', {
      type: 'text', value: k.name, title: 'Bezeichnung des häufigen Lastfalls',
      on: { change: (e) => aendern((x) => { x.name = e.target.value; }) },
    }),
    zahlfeld({
      wert: k.M_Ed, schritt: 10, titel: 'Moment unter häufiger Einwirkung, in kNm',
      beiAenderung: (v) => aendern((x) => { x.M_Ed = v ?? 0; }),
    }),
    zahlfeld({
      wert: k.N_Ed, schritt: 10,
      titel: 'Normalkraft unter häufiger Einwirkung, in kN – Zug positiv',
      beiAenderung: (v) => aendern((x) => { x.N_Ed = v ?? 0; }),
    }),
    richtungsWahl(k.richtung || 'beide',
      (wert) => aendern((x) => { x.richtung = wert; })),
    el('button.knopf.knopf-zart.knopf-gefahr', {
      text: '×', title: 'Häufigen Lastfall entfernen',
      on: {
        click: () => projektAendern((p) => {
          p.querschnitte.find((x) => x.kennung === querschnitt.kennung)
            .haeufige.splice(index, 1);
        }),
      },
    }),
  ]);
}

/**
 * Ein Schalter je Lage: wird für sie der Duktilitätsnachweis geführt?
 *
 * Der Nachweis gilt einer einzelnen Bewehrungslage, nicht einer Tragrichtung --
 * darum vier Zeilen und nicht zwei. Üblich sind die beiden äusseren; die
 * inneren tragen selten das massgebende Moment.
 */
function duktilitaetZeile(querschnitt, nummer) {
  const an = duktilitaetVon(querschnitt)[nummer - 1];
  const richtung = richtungVon(querschnitt, nummer);
  const lage = querschnitt.lagen[nummer - 1];
  const leer = !(lage.grund.durchmesser > 0 || lage.zulage.durchmesser > 0);

  const setzen = (wert) => projektAendern((p) => {
    const q = p.querschnitte.find((x) => x.kennung === querschnitt.kennung);
    q.duktilitaet = duktilitaetVon(q);
    q.duktilitaet[nummer - 1] = wert;
  });

  return el('div.duktilitaetszeile', {}, [
    el('span.postenname', { text: `Duktilität ${nummer}. Lage` }),
    el('span.richtung', {
      text: richtung,
      class: `lage-${richtung}`,
      title: `Tragrichtung der ${nummer}. Lage`,
    }),
    hakenSchalter(an, setzen),
    // Ein eingeschalteter Nachweis an einer leeren Lage ist kein Fehler der
    // Eingabe -- er wird geführt und meldet selbst, dass er nicht geht. Hier
    // steht es trotzdem, damit man es beim Einschalten schon sieht.
    el('span.kurvenhinweis', {
      text: (an && leer) ? 'Lage nicht definiert' : '',
    }),
  ]);
}

/** Genau vier Schalter, auch wenn die Beschreibung älter ist als der Nachweis. */
function duktilitaetVon(querschnitt) {
  const vorgabe = [true, false, false, true];
  const vorhanden = Array.isArray(querschnitt.duktilitaet)
    ? querschnitt.duktilitaet : [];
  return vorgabe.map((v, i) => (i < vorhanden.length ? !!vorhanden[i] : v));
}

/**
 * Die Bewehrung suchen lassen, statt sie zu setzen.
 *
 * Ein einzelner Knopf, kein Automatismus im Hintergrund: was hier
 * herauskommt, wird in die Lagen darunter geschrieben und steht dann da wie
 * eine Eingabe von Hand -- man sieht es, kann es ändern und kann es lassen.
 * Eine Bewehrung, die sich bei jeder Zahl neu setzt, wäre keine Eingabe mehr.
 *
 * Gesucht wird gegen die Nachweise, die eingeschaltet sind. Die Schalter
 * weiter unten steuern damit unmittelbar, wonach gesucht wird.
 */
export function automatikBlock(querschnitt) {
  const aendern = (veraenderer) => projektAendern((p) => {
    veraenderer(p.querschnitte.find((x) => x.kennung === querschnitt.kennung));
  });
  const moden = [
    { wert: 'grund_ohne', beschriftung: 'Grundbewehrung ohne Kräfte' },
    { wert: 'grund_mit', beschriftung: 'Grundbewehrung mit Kräften' },
    { wert: 'grund_ohne_zulage_mit',
      beschriftung: 'Grund ohne Kräfte, Zulage mit Kräften' },
  ];
  const quer = querschnitt.automatik_querkraft === true;

  // Die Teilungen als Text: «100, 150» liest und tippt sich schneller als
  // eine Liste aus Zahlenfeldern mit Plus- und Minusknöpfen.
  const teilungsfeld = (feld, titel) => el('input.ew-name', {
    type: 'text', value: (querschnitt[feld] || []).join(', '), title: titel,
    on: {
      change: (e) => aendern((q) => {
        q[feld] = e.target.value.split(/[^0-9.]+/)
          .map(Number).filter((x) => x > 0);
      }),
    },
  });

  return el('div.feldgruppe', {}, [
    el('h3', {}, [el('span', { text: 'Bewehrung ermitteln' }),
      el('span', { text: 'kleinste Stahlfläche' })]),
    el('div.unterkapitel', {}, [
      feld('Modus', auswahl({
        werte: moden, gewaehlt: querschnitt.automatik_modus || 'grund_ohne',
        titel: 'Ohne Kräfte bleiben Duktilität, sprödes Versagen und die '
          + 'Rissbreitenbegrenzung – das, was eine Platte unabhängig von der '
          + 'Belastung braucht.',
        beiAenderung: (v) => aendern((q) => { q.automatik_modus = v; }),
      })),
      feld('Teilungen', teilungsfeld('automatik_teilungen',
        'Liste in mm, durch Komma getrennt. Grundbewehrung und Zulage einer '
        + 'Lage bekommen dieselbe Teilung.'), 'mm'),
      el('div.duktilitaetszeile.ist-breit', {}, [
        el('span.postenname', { text: 'Querkraftbewehrung mitsuchen' }),
        hakenSchalter(quer, (wert) => aendern((q) => {
          q.automatik_querkraft = wert;
        }), 'Bügelsuche'),
        el('span.kurvenhinweis', { text: '' }),
      ]),
      ...(quer ? [feld('Bügelteilungen',
        teilungsfeld('automatik_querkraft_teilungen',
          'Liste in mm. Das Bügelraster ist quadratisch: s_x = s_y.'), 'mm')] : []),
      automatikLeiste(querschnitt.kennung),
    ]),
  ]);
}

function automatikLeiste(kennung) {
  const stand = automatikMeldungen.get(kennung);
  const laeuft = stand?.laeuft === true;
  return el('div.automatik-leiste', {}, [
    el('button.knopf.knopf-haupt', {
      text: laeuft ? 'sucht …' : 'Bewehrung ermitteln',
      title: 'Sucht einmalig und schreibt das Ergebnis in die Lagen',
      disabled: laeuft,
      on: { click: () => bewehrungErmitteln(kennung) },
    }),
    stand?.text
      ? el('span.automatik-meldung', {
        text: stand.text,
        class: stand.gut === null ? '' : (stand.gut ? 'ist-gut' : 'ist-schlecht'),
      })
      : null,
  ]);
}

/** Einmal suchen, das Ergebnis übernehmen, die Meldung stehen lassen. */
async function bewehrungErmitteln(kennung) {
  automatikMeldungen.set(kennung, { laeuft: true, text: '', gut: null });
  aendern({}, 'bewehrungssuche-start');
  try {
    const antwort = await api.bewehrungSuchen(zustand.projekt, kennung);
    const teile = [antwort.begruendung];
    if (antwort.buegel) teile.push(`Bügel: ${antwort.buegel.begruendung}`);
    automatikMeldungen.set(kennung, {
      laeuft: false, text: teile.join(' '), gut: antwort.gefunden,
    });
    if (antwort.gefunden) {
      // Der Kern gibt das fertige Projekt zurück -- übernommen wird es als
      // eine Änderung, damit ein Rückgängig sie als eine zurücknimmt.
      projektAendern((p) => {
        const alt = p.querschnitte.findIndex((x) => x.kennung === kennung);
        const neu = antwort.projekt.querschnitte.find((x) => x.kennung === kennung);
        if (alt >= 0 && neu) p.querschnitte[alt] = neu;
      });
    } else {
      aendern({}, 'bewehrungssuche-ende');
    }
  } catch (fehler) {
    automatikMeldungen.set(kennung, {
      laeuft: false, text: String(fehler.message || fehler), gut: false,
    });
    aendern({}, 'bewehrungssuche-fehler');
  }
}
