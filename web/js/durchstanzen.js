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
 * rechts in der Zusammenfassung, der Grundriss unter «Diagramme». Die Felder
 * mit Zeichen und Hinweisen kommen aus dem Kern, je Gruppe der Herleitung
 * (`katalog.vorgaben`, opencivil/durchstanzen/stelle.py); hier steht nur,
 * auf welcher Tafel eine Gruppe steht. Einheiten und Grenzen kommen aus dem
 * Katalog (`katalog.felder.durchstanz`), die Stellungen der Schalter ebenso
 * (`katalog.durchstanzen`) -- und mit ihnen, welche Felder der Kern je
 * Stellung liest: die Maske zeigt genau die. Bis 2026-11-20 standen die
 * Felder hier ein zweites Mal.
 */

import {
  bezeichnung, eingabegruppen, erklaerung, feld, karte, materialliste, mitBild, panel, wahlBlock,
  wahlSchalter,
} from './bausteine.js';
import { el } from './dom.js';
import { zeichenbereich } from './ds_zeichnung.js';
import { eintragAendern, katalog } from './zustand.js';

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
    formel: 'u_0 = 2·(b_x + b_y) + π·d_v;  u = k_e · u_red',
  },
  bewehrung: {
    zeilen: [
      ['Lage', 'die Biegebewehrung auf der Zugseite über der Stütze'],
      ['aussen', 'welche Richtung näher am Rand liegt – sie hat das grössere d'],
      ['d', 'das Mittel der beiden Lagen; d_v = d, solange die Stütze nicht in die Platte reicht'],
    ],
    formel: 'd = (d_x + d_y) / 2',
  },
  rotation: {
    zeilen: [
      ['Stufe 1', 'm_sd/m_Rd = 1, für regelmässige Flachdecken mit 0.5 ≤ l_x/l_y ≤ 2'],
      ['Stufe 2', 'die Momente im Stützstreifen aus V_d und e_u, Gleichungen (62) bis (65); '
        + 'ebenfalls nur mit 0.5 ≤ l_x/l_y ≤ 2'],
      ['Stufe 3', 'r_s und m_sd aus einer Berechnung nach der Elastizitätstheorie; '
        + 'in ψ steht 1.2 statt 1.5'],
      ['l', 'die grössere der angrenzenden Spannweiten; r_s = 0.22·l'],
    ],
    formel: 'ψ = 1.5 · r_s/d · f_yd/E_s · (m_sd/m_Rd)^1.5',
  },
  einwirkung: {
    zeilen: [
      ['V_d', 'der Bemessungswert der Auflagerkraft'],
      ['q_d', 'Flächenlast, die innerhalb des Nachweisschnitts abgezogen wird: bei der Decke '
        + 'Eigengewicht und Nutzlast, bei der Bodenplatte die Bodenpressung – je als '
        + 'Bemessungswert'],
      ['k_e', 'die Näherung gilt für regelmässige Flachdecken; sonst aus der Exzentrizität'],
      ['e', 'wie weit die Auflagerkraft neben der Stützenachse angreift'],
    ],
    formel: 'V_Rd,c = k_r · τ_cd · d_v · u',
  },
};

/** Die Gruppe der Vorgaben mit der Exzentrizität: eine eigene Karte, wo der Nachweis sie liest. */
const EXZENTRIZITAET = 'Exzentrizität der Auflagerkraft';

/** Die Lage der Stelle, wie der Katalog sie beschreibt. */
function lageVon(d) {
  return katalog('durchstanzen', 'lagen').find((l) => l.wert === d.lage);
}

/**
 * Was der Kern an dieser Stelle liest: die festen Felder, die Masse der Lage
 * in ihrer Form, die Felder der Näherungsstufe an dieser Lage und die von
 * k_e -- je aus dem Katalog.
 */
function gelesen(d) {
  const lage = lageVon(d);
  const ke = katalog('durchstanzen', 'ke').find((k) => k.wert === d.ke);
  return new Set([...katalog('durchstanzen', 'fest'), ...lage.masse[d.form],
    ...lage.stufen[d.stufe], ...ke.eingaben]);
}

/**
 * Die Stelle, deren Art eben zwischen Decke und Bodenplatte umgeschaltet
 * wurde: bis zur nächsten Änderung sagt der Schalter, welche Zahlen jetzt
 * für die andere Seite gelten (Benutzer, 2026-11-19).
 */
let umgeschaltet = null;

function aenderer(d) {
  return (veraenderer) => eintragAendern(d.kennung, (x) => {
    const vorher = x.plattenart;
    veraenderer(x);
    umgeschaltet = x.plattenart !== vorher ? x.kennung : null;
  });
}

/**
 * Ein Schalter mit den Stellungen aus dem Katalog. Mit `bild` zeigt jede ihr
 * Sinnbild `bild-wert` (sinnbilder.js) -- etwa, wo der Plattenrand liegt.
 */
function schalter(d, schluessel, liste, titel = '', bild = null) {
  const werte = katalog('durchstanzen', liste).map((w) => ({
    wert: w.wert, beschriftung: w.beschriftung, titel: w.beschriftung,
  }));
  return wahlSchalter({
    werte: bild ? mitBild(werte, bild) : werte,
    gewaehlt: d[schluessel],
    setzen: (w) => aenderer(d)((x) => { x[schluessel] = w; }),
    titel,
  });
}

/** Die Wahl eines Materials: eine Auswahlliste, wie bei der Platte. */
function materialfeld(d, schluessel, art, text) {
  return feld(text, materialliste({
    art, gewaehlt: d[schluessel], titel: text,
    setzen: (k) => aenderer(d)((x) => { x[schluessel] = k; }),
  }), '');
}

function stellePanel(d, vorgaben) {
  const lage = lageVon(d);
  return panel({
    schluessel: 'durchstanzen/Stelle', titel: 'Durchstanzstelle',
    zusatz: erklaerung(HILFE.stelle.zeilen, HILFE.stelle.formel),
  }, [
    el('div.unterkapitel', {}, [
      bezeichnung(d, aenderer(d)),
      feld('Platte', schalter(d, 'plattenart', 'plattenarten',
        'Decke: Zug oben – Bodenplatte: Zug unten, gegen die Bodenpressung'), ''),
      umgeschaltet === d.kennung ? el('p.hinweis', {
        text: katalog('durchstanzen', 'plattenarten').find((w) => w.wert === d.plattenart).umgeschaltet,
      }) : null,
    ]),
    wahlBlock('Lage', schalter(d, 'lage', 'lagen', 'Wo die gestützte Fläche in der Platte liegt', 'lage')),
    karte(lage.titel, [
      lage.hat_form ? feld('Form', schalter(d, 'form', 'formen', 'Die Form der Stütze im Grundriss',
        'stuetzenform'), '') : null,
      ...vorgaben.zeilen('Gestützte Fläche'),
    ]),
  ]);
}

/** Das Zeichenfenster: Aussparungen zeichnen, darunter Stütze, Rand und Schnitt der letzten Rechnung. */
function grundrissPanel(d) {
  return panel({
    schluessel: 'durchstanzen/Grundriss', titel: 'Grundriss und Aussparungen',
    zusatz: 'x nach rechts, y nach oben, mm', breit: true,
  }, [zeichenbereich(d)]);
}

function plattenPanel(d, vorgaben) {
  return panel({ schluessel: 'durchstanzen/Platte', titel: 'Platte' }, [
    karte('', [
      ...vorgaben.zeilen('Platte'),
      materialfeld(d, 'beton', 'beton', 'Beton'),
      materialfeld(d, 'stahl', 'betonstahl', 'Betonstahl'),
    ]),
  ]);
}

function bewehrungPanel(d, vorgaben) {
  return panel({
    schluessel: 'durchstanzen/Bewehrung',
    titel: d.plattenart === 'bodenplatte' ? 'Biegebewehrung unten' : 'Biegebewehrung oben',
    zusatz: erklaerung(HILFE.bewehrung.zeilen, HILFE.bewehrung.formel),
  }, [
    karte('', [...vorgaben.zeilen('Biegebewehrung'), feld('Aussen liegt', wahlSchalter({
      werte: [{ wert: 'x', beschriftung: 'x' }, { wert: 'y', beschriftung: 'y' }],
      gewaehlt: d.aussen,
      setzen: (w) => aenderer(d)((x) => { x.aussen = w; }),
      titel: 'Welche Lage näher am Rand liegt',
    }), '')]),
  ]);
}

function rotationPanel(d, vorgaben) {
  return panel({
    schluessel: 'durchstanzen/Rotation', titel: 'Plattenrotation',
    zusatz: erklaerung(HILFE.rotation.zeilen, HILFE.rotation.formel),
  }, [
    wahlBlock('Näherungsstufe', schalter(d, 'stufe', 'stufen', 'SIA 262:2025, 4.3.6.4.2')),
    karte('', vorgaben.zeilen('Plattenrotation')),
  ]);
}

function einwirkungPanel(d, vorgaben) {
  const exzentrizitaet = vorgaben.zeilen(EXZENTRIZITAET);
  return panel({
    schluessel: 'durchstanzen/Einwirkung', titel: 'Einwirkung',
    zusatz: erklaerung(HILFE.einwirkung.zeilen, HILFE.einwirkung.formel),
  }, [
    karte('', vorgaben.zeilen('Einwirkung')),
    wahlBlock('k_e', schalter(d, 'ke', 'ke', 'SIA 262:2025, 4.3.6.2.4 und 4.3.6.2.5')),
    exzentrizitaet.length ? karte(EXZENTRIZITAET, exzentrizitaet) : null,
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
  // Je Gruppe der Vorgaben eine Tafel; welche Felder sie zeigt, sagt der Kern.
  const vorgaben = eingabegruppen('durchstanz', d, aenderer(d), { gelesen: gelesen(d) });
  const tafeln = [stellePanel(d, vorgaben), grundrissPanel(d), plattenPanel(d, vorgaben),
    bewehrungPanel(d, vorgaben), rotationPanel(d, vorgaben), einwirkungPanel(d, vorgaben)];
  vorgaben.vollstaendig();
  return tafeln;
}
