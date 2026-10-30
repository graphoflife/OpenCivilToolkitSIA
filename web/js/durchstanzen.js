/**
 * durchstanzen.js -- Mittlere Tafel: Eingaben eines Durchstanznachweises.
 *
 * Von oben nach unten:
 *
 *     Durchstanzstelle   Bezeichnung; Decke oder Bodenplatte; Lage der
 *                        gestützten Fläche, Form und Masse, Randabstände
 *     Grundriss          das Zeichenfenster: Aussparungen (ds_zeichnung.js)
 *     Platte             Dicke, Überdeckung, Grösstkorn, Beton und Stahl
 *     Biegebewehrung     ⌀ und Abstand je Richtung, welche Lage aussen liegt
 *     Plattenrotation    Näherungsstufe; Spannweiten oder r_s und m_sd
 *     Einwirkung         V_d, die Flächenlast im Schnitt, k_e
 *
 * Gerechnet wird nichts: Nachweisschnitt, Rotation und Widerstand stehen
 * rechts in der Zusammenfassung, der Grundriss unter «Diagramme». Einheiten
 * und Grenzen kommen aus dem Katalog (`katalog.felder.durchstanz`), die
 * Stellungen der Schalter ebenso (`katalog.durchstanzen`).
 */

import {
  erklaerung, feld, karte, panel, wahlBlock, wahlSchalter, zahlzeile as feldzeile,
} from './bausteine.js';
import { auswahl, el } from './dom.js';
import { zeichenbereich } from './ds_zeichnung.js';
import { eintragAendern, materialien, zustand } from './zustand.js';

const HILFE = {
  stelle: {
    zeilen: [
      ['Decke', 'die Zugbewehrung liegt über der Stütze oben'],
      ['Bodenplatte', 'die Bodenpressung drückt von unten: die Zugbewehrung liegt unten'],
      ['Rand, Ecke', 'der Plattenrand liegt unten, an der Ecke auch links; a ist der Abstand '
        + 'von der Stütze zum Rand'],
      ['Wandende', 'die Wand läuft nach rechts weiter; gezählt werden 1.5·d_v entlang der Wand'],
      ['Wandecke', 'die äussere Ecke zweier Wände, die nach rechts und oben laufen'],
    ],
    formel: 'u = 2·(b_x + b_y) + π·d_v',
  },
  bewehrung: {
    zeilen: [
      ['Lage', 'die Biegebewehrung auf der Zugseite über der Stütze'],
      ['aussen', 'welche Richtung näher am Rand liegt -- sie hat das grössere d'],
      ['d', 'das Mittel der beiden Lagen; d_v = d, solange die Stütze nicht in die Platte reicht'],
    ],
    formel: 'd = (d_x + d_y) / 2',
  },
  rotation: {
    zeilen: [
      ['Stufe 1', 'm_sd/m_Rd = 1, für regelmässige Flachdecken mit 0.5 ≤ l_x/l_y ≤ 2'],
      ['Stufe 2', 'die Momente im Stützstreifen aus V_d und e_u, Gleichungen (62) bis (65)'],
      ['Stufe 3', 'r_s und m_sd aus einer Berechnung nach der Elastizitätstheorie'],
      ['l', 'die grössere der angrenzenden Spannweiten; r_s = 0.22·l'],
    ],
    formel: 'ψ = 1.5 · r_s/d · f_yd/E_s · (m_sd/m_Rd)^1.5',
  },
  einwirkung: {
    zeilen: [
      ['V_d', 'der Bemessungswert der Auflagerkraft'],
      ['q_d', 'Flächenlast, die innerhalb des Nachweisschnitts abgezogen wird: bei der Decke '
        + 'Eigengewicht und Nutzlast, bei der Bodenplatte die Bodenpressung -- je als '
        + 'Bemessungswert'],
      ['k_e', 'die Näherung gilt für regelmässige Flachdecken; sonst aus der Exzentrizität'],
      ['e', 'wie weit die Auflagerkraft neben der Stützenachse angreift'],
    ],
    formel: 'V_Rd,c = k_r · τ_cd · d_v · u',
  },
};

function aenderer(d) {
  return (veraenderer) => eintragAendern('durchstanzstellen', d.kennung, veraenderer);
}

/** Eine Zahl des Eintrags als Feld: Beschriftung mit Symbol, Einheit aus dem Katalog. */
function zahlzeile(d, schluessel, text, symbol, { schritt = 1, titel } = {}) {
  return feldzeile('durchstanz', d, schluessel, text, symbol, {
    schritt, titel, aendern: aenderer(d),
  });
}

/** Ein Schalter mit den Stellungen aus dem Katalog. */
function schalter(d, schluessel, liste, titel = '') {
  return wahlSchalter({
    werte: (zustand.katalog?.durchstanzen?.[liste] || []).map((w) => ({
      wert: w.wert, beschriftung: w.beschriftung, titel: w.beschriftung,
    })),
    gewaehlt: d[schluessel],
    setzen: (w) => aenderer(d)((x) => { x[schluessel] = w; }),
    titel,
  });
}

/** Die Wahl eines Materials: eine Auswahlliste, wie bei der Platte. */
function materialfeld(d, schluessel, art, text) {
  const stoffe = materialien(art);
  return feld(text, auswahl({
    werte: stoffe.map((m) => ({ wert: m.kennung, beschriftung: m.name || m.sorte })),
    gewaehlt: d[schluessel],
    titel: text,
    beiAenderung: (k) => aenderer(d)((x) => { x[schluessel] = k; }),
  }), '');
}

function stellePanel(d) {
  const wand = d.lage === 'wandende' || d.lage === 'wandecke';
  const masse = [];
  if (wand) {
    masse.push(zahlzeile(d, 't', 'Wanddicke', 't', { schritt: 10 }));
  } else {
    masse.push(feld('Form', schalter(d, 'form', 'formen', 'Die Form der Stütze im Grundriss'), ''));
    if (d.form === 'rund') {
      masse.push(zahlzeile(d, 'D', 'Durchmesser', 'D', { schritt: 10 }));
    } else {
      masse.push(zahlzeile(d, 'b_x', 'Abmessung in x', 'b_x', { schritt: 10 }),
        zahlzeile(d, 'b_y', 'Abmessung in y', 'b_y', { schritt: 10 }));
    }
    if (d.lage === 'ecke') {
      masse.push(zahlzeile(d, 'a_x', 'Abstand zum linken Rand', 'a_x', { schritt: 10 }));
    }
    if (d.lage === 'rand' || d.lage === 'ecke') {
      masse.push(zahlzeile(d, 'a_y', 'Abstand zum unteren Rand', 'a_y', { schritt: 10 }));
    }
  }
  return panel({
    schluessel: 'durchstanzen/Stelle', titel: 'Durchstanzstelle',
    zusatz: erklaerung(HILFE.stelle.zeilen, HILFE.stelle.formel),
  }, [
    el('div.unterkapitel', {}, [
      feld('Bezeichnung', el('input', {
        type: 'text', value: d.name,
        on: { change: (e) => aenderer(d)((x) => { x.name = e.target.value; }) },
      })),
      feld('Platte', schalter(d, 'plattenart', 'plattenarten',
        'Decke: Zug oben -- Bodenplatte: Zug unten, gegen die Bodenpressung'), ''),
    ]),
    wahlBlock('Lage', schalter(d, 'lage', 'lagen', 'Wo die gestützte Fläche in der Platte liegt')),
    karte(wand ? 'Wand' : 'Stütze', masse),
  ]);
}

/** Das Zeichenfenster: Aussparungen zeichnen, darunter Stütze, Rand und Schnitt der letzten Rechnung. */
function grundrissPanel(d) {
  return panel({
    schluessel: 'durchstanzen/Grundriss', titel: 'Grundriss und Aussparungen',
    zusatz: 'x nach rechts, y nach oben, mm', breit: true,
  }, [zeichenbereich(d)]);
}

function plattenPanel(d) {
  const bodenplatte = d.plattenart === 'bodenplatte';
  return panel({ schluessel: 'durchstanzen/Platte', titel: 'Platte' }, [
    karte('', [
      zahlzeile(d, 'h', 'Plattendicke', 'h', { schritt: 10 }),
      zahlzeile(d, 'c', bodenplatte ? 'Überdeckung unten' : 'Überdeckung oben', 'c_{nom}', {
        schritt: 5, titel: 'Die Überdeckung der Zugbewehrung',
      }),
      zahlzeile(d, 'D_max', 'Grösstkorn', 'D_{max}', { schritt: 1 }),
      materialfeld(d, 'beton', 'beton', 'Beton'),
      materialfeld(d, 'stahl', 'betonstahl', 'Betonstahl'),
    ]),
  ]);
}

function bewehrungPanel(d) {
  return panel({
    schluessel: 'durchstanzen/Bewehrung',
    titel: d.plattenart === 'bodenplatte' ? 'Biegebewehrung unten' : 'Biegebewehrung oben',
    zusatz: erklaerung(HILFE.bewehrung.zeilen, HILFE.bewehrung.formel),
  }, [
    karte('In x', [
      zahlzeile(d, 'phi_x', 'Durchmesser', String.raw`\varnothing_x`, { schritt: 2 }),
      zahlzeile(d, 's_x', 'Abstand', 's_x', { schritt: 10 }),
    ]),
    karte('In y', [
      zahlzeile(d, 'phi_y', 'Durchmesser', String.raw`\varnothing_y`, { schritt: 2 }),
      zahlzeile(d, 's_y', 'Abstand', 's_y', { schritt: 10 }),
    ]),
    karte('', [feld('Aussen liegt', wahlSchalter({
      werte: [{ wert: 'x', beschriftung: 'x' }, { wert: 'y', beschriftung: 'y' }],
      gewaehlt: d.aussen,
      setzen: (w) => aenderer(d)((x) => { x.aussen = w; }),
      titel: 'Welche Lage näher am Rand liegt',
    }), '')]),
  ]);
}

function rotationPanel(d) {
  const inhalt = d.stufe === '3' ? [
    zahlzeile(d, 'r_sx', 'Abstand zum Momentennullpunkt in x', 'r_{sx}', { schritt: 0.1 }),
    zahlzeile(d, 'r_sy', 'Abstand zum Momentennullpunkt in y', 'r_{sy}', { schritt: 0.1 }),
    zahlzeile(d, 'm_sdx', 'Moment im Stützstreifen in x', 'm_{sd,x}', { schritt: 5 }),
    zahlzeile(d, 'm_sdy', 'Moment im Stützstreifen in y', 'm_{sd,y}', { schritt: 5 }),
  ] : [
    zahlzeile(d, 'l_x', 'Spannweite in x', 'l_x', { schritt: 0.1 }),
    zahlzeile(d, 'l_y', 'Spannweite in y', 'l_y', { schritt: 0.1 }),
  ];
  return panel({
    schluessel: 'durchstanzen/Rotation', titel: 'Plattenrotation',
    zusatz: erklaerung(HILFE.rotation.zeilen, HILFE.rotation.formel),
  }, [
    wahlBlock('Näherungsstufe', schalter(d, 'stufe', 'stufen', 'SIA 262:2025, 4.3.6.4.2')),
    karte('', inhalt),
  ]);
}

function einwirkungPanel(d) {
  const bodenplatte = d.plattenart === 'bodenplatte';
  // Wann der Kern e_x und e_y liest, sagt `Durchstanzstelle.eingaben`: für
  // k_e aus der Exzentrizität und für die Momente in Stufe 2, ausser an Wänden.
  const wand = d.lage === 'wandende' || d.lage === 'wandecke';
  const exzentrisch = d.ke === 'exzentrizitaet' || (d.stufe === '2' && !wand);
  return panel({
    schluessel: 'durchstanzen/Einwirkung', titel: 'Einwirkung',
    zusatz: erklaerung(HILFE.einwirkung.zeilen, HILFE.einwirkung.formel),
  }, [
    karte('', [
      zahlzeile(d, 'V_d', 'Auflagerkraft', 'V_d', { schritt: 10 }),
      zahlzeile(d, 'q_d', bodenplatte ? 'Bodenpressung' : 'Eigengewicht und Nutzlast', 'q_d', {
        schritt: 1, titel: 'Bemessungswert der Flächenlast, abgezogen innerhalb des Nachweisschnitts',
      }),
    ]),
    wahlBlock('k_e', schalter(d, 'ke', 'ke', 'SIA 262:2025, 4.3.6.2.4 und 4.3.6.2.5')),
    exzentrisch ? karte('Exzentrizität der Auflagerkraft', [
      zahlzeile(d, 'e_x', 'in x', 'e_x', { schritt: 10 }),
      zahlzeile(d, 'e_y', 'in y', 'e_y', { schritt: 10 }),
    ]) : null,
    el('div.unterkapitel', {}, [
      el('div.beschreibung', {}, [
        el('label', { text: 'Beschreibung' }),
        el('textarea', {
          rows: 2, value: d.beschreibung || '',
          on: { change: (e) => aenderer(d)((x) => { x.beschreibung = e.target.value; }) },
        }),
      ]),
    ]),
  ]);
}

export function durchstanzEditor(d) {
  return [stellePanel(d), grundrissPanel(d), plattenPanel(d), bewehrungPanel(d), rotationPanel(d),
    einwirkungPanel(d)];
}
