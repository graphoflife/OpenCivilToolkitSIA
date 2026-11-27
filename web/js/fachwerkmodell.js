/**
 * fachwerkmodell.js -- Mittlere Tafel: Eingaben eines Fachwerkmodells, und was rechts von ihm steht.
 *
 * Oben die Scheibe: Bezeichnung, Zeichnung samt Liste, Beschreibung. Ein
 * Verfahren, das darin ein Fachwerk sucht, kommt in den nächsten Schritten
 * dazu (Plan vom 2026-11-27, Schritt 11).
 *
 * Rechts im Reiter «Diagramme» das Modell als Bild mit den Meldungen des
 * Kerns, in der Zusammenfassung die Lager und die Lasten. Gerechnet wird im
 * Kern (opencivil/fachwerkmodell); hier stehen nur seine Zahlen.
 */

import {
  beschreibung, bezeichnung, erklaerung, karte, meldungshinweise, panel, tabelle,
} from './bausteine.js';
import { zahlText } from './cad_ansicht.js';
import { listengruppen, listenzeilen, meldungsliste } from './cad_app.js';
import { el, leerzustand } from './dom.js';
import { scheibeBild } from './fw_bild.js';
import { zeichenbereich } from './fw_zeichnung.js';
import {
  eintragAendern, eintragVon, katalog, zustand,
} from './zustand.js';

const HILFE = {
  zeilen: [
    ['Achsen', 'x nach rechts, y nach oben, in m; Lasten in kN'],
    ['Scheibe', 'ein Umriss aus Ecken – liegen mehrere da, ist Material, wo eine von ihnen ist'],
    ['Loch', 'in seinem Innern ist kein Material, auf seinem Rand schon'],
    ['Lager', 'an einem Knoten, am Rand oder innen: fest in x und y, nur in x oder nur in y – zusammen halten sie die Scheibe, so dass sie sich weder verschieben noch drehen kann'],
    ['Last', 'eine Punktlast an einem Knoten, in jeder Richtung: F_h nach rechts, F_v nach unten positiv'],
    ['Material', 'keines und keine Dicke: ohne Bemessung hängen Fachwerk und Kräfte nur von Form, Lagern und Lasten ab'],
  ],
};

/** Wie ein Lager hält, in Worten des Kerns: «x und y», «nur x». */
const haltText = (halt) => katalog('fachwerkmodell', 'halt').find((h) => h.wert === halt)?.beschriftung ?? halt;

/** Wo ein Knoten liegt, «(2.00, 3.00)» in m -- leer, wenn es ihn nicht gibt. */
function ortText(modell, knoten) {
  const k = modell.knoten.find((x) => x.kennung === knoten);
  return k ? `(${zahlText(k.x, 2)}, ${zahlText(k.y, 2)})` : '';
}

/** «F_h = 50.0 kN · F_v = 200.0 kN»: eine Last, wie sie eingegeben ist. */
const lastText = (f) => `F_h = ${zahlText(f.F_h, 1)} kN · F_v = ${zahlText(f.F_v, 1)} kN`;

// ===========================================================================
// Unter der Zeichnung
// ===========================================================================

/** Meldungen des Kerns und je Teil eine Zeile (cad_app.js): ein Klick wählt im Fenster, Lager und Last über ihren Knoten. */
function liste(a) {
  const z = eintragVon(a.fw.kennung);
  if (!z) return [];
  const zeile = (kennung, was, wert = '') => listenzeilen(a)({ kennung, was, wert });
  const ecken = (u) => `${u.knoten.length} Ecken`;
  return [
    meldungsliste(a),
    ...listengruppen(a, [
      ['Scheiben', z.scheiben.map((s) => zeile(s.kennung, ecken(s)))],
      ['Löcher', z.loecher.map((l) => zeile(l.kennung, ecken(l)))],
      ['Lager', z.lager.map((l) => zeile(l.kennung, `an ${l.knoten}`, `hält ${haltText(l.halt)}`))],
      ['Lasten', z.lasten.map((f) => zeile(f.kennung, `an ${f.knoten}`, lastText(f)))],
    ]),
  ];
}

// ===========================================================================
// Die Scheibe
// ===========================================================================

function scheibeGruppe(modell) {
  const aendern = (veraenderer) => eintragAendern(modell.kennung, veraenderer);
  return panel({
    schluessel: 'fachwerkmodell/Scheibe', titel: 'Scheibe', zusatz: 'x nach rechts, y nach oben, m', breit: true,
  }, [
    bezeichnung(modell, aendern, erklaerung(HILFE.zeilen)),
    zeichenbereich(modell, liste),
    el('div.unterkapitel', {}, [beschreibung(modell, aendern)]),
  ]);
}

export function fachwerkEditor(modell) {
  return [scheibeGruppe(modell)];
}

// ===========================================================================
// Rechts: Diagramme und Zusammenfassung
// ===========================================================================

/** Was die letzte Rechnung zu einem Fachwerkmodell zeichnet -- oder null. */
const zeichendaten = (kennung) => zustand.loesung?.zeichendaten?.[kennung] || null;

/** Ein frisches Modell, in Diagrammen und Zusammenfassung gleich. */
function ohneScheibe() {
  return karte(null, [leerzustand('Noch keine Scheibe.', 'Zeichnen im Fenster mit «Scheibe».')]);
}

/**
 * Die Karte eines Fachwerkmodells im Reiter «Diagramme»: das Modell als
 * Bild, darüber, was der Kern meldet. Das Panel darum baut bericht.js.
 */
export function fachwerkKarten(kennung) {
  const modell = eintragVon(kennung);
  if (!modell?.scheiben.length) return [ohneScheibe()];
  const bild = scheibeBild(modell);
  return [karte('Scheibe', [
    ...meldungshinweise(zeichendaten(kennung)?.meldungen), el('div.gb-bildhuelle', {}, [bild]),
  ], { bild, klasse: 'ist-breit' })];
}

/**
 * Die Zusammenfassung eines Fachwerkmodells: was der Kern meldet, die
 * Lager und die Lasten, wie sie eingegeben sind. Das Panel darum baut
 * bericht.js.
 */
export function fachwerkZusammenfassung(kennung) {
  const modell = eintragVon(kennung);
  const daten = zeichendaten(kennung);
  if (!modell?.scheiben.length) return [ohneScheibe()];
  if (!daten) return [karte(null, [leerzustand('Noch nicht gerechnet.')])];
  return [
    karte('Modell', meldungshinweise(daten.meldungen)),
    modell.lager.length ? karte('Lager', [tabelle(['Lager', 'Ort [m]', 'hält'],
      modell.lager.map((l) => [l.kennung, ortText(modell, l.knoten), haltText(l.halt)]))]) : null,
    modell.lasten.length ? karte('Lasten', [tabelle(['Last', 'Ort [m]', 'F_h [kN] →', 'F_v [kN] ↓'],
      modell.lasten.map((f) => [f.kennung, ortText(modell, f.knoten), zahlText(f.F_h, 1), zahlText(f.F_v, 1)]))])
      : null,
  ].filter(Boolean);
}
