/**
 * dk_zeichnung.js -- das Zeichenfenster einer Decke: der Adapter.
 *
 * Gezeichnet wird ein Grundriss in Metern, x nach rechts und y nach oben
 * (Benutzer, 2026-10-23): Platten und Zonen als Umrisse, Linienlager und
 * versteckte Unterzüge als Linien, Stützen an einem Knoten. Alles hängt an
 * Knoten (`verbunden`): wo zwei Platten sich eine Ecke teilen oder eine Wand
 * an einer Platte entlangläuft, verschiebt man sie zusammen. Eine Stütze ist
 * ein eigener Eintrag an ihrem Knoten, gewählt wird aber der Knoten -- wie
 * ein Lager im Balkensystem; sein Fenster zeigt die Stütze.
 *
 * WAS DARUNTER LIEGT:
 * Was der Kern zur Zeichnung sagt (Anfrage `decke_zeichnung`): wie die Last
 * auf die zwei Richtungen geht, oder wo die Streifen laufen -- umzuschalten
 * in der Leiste. Bis die Antwort auf die letzte Änderung da ist, bleibt die
 * vorige blass stehen, statt bei jedem Strich zu flackern. Die Meldungen
 * gelten nur, solange die Zeichnung dieselbe ist, nach der gefragt wurde.
 *
 * Das schwebende Fenster steht in `dk_eigenschaften.js`, das Bild in
 * `dk_grundriss.js`. Gerechnet wird hier nichts.
 */

import { api } from './api.js';
import { wahlSchalter } from './bausteine.js';
import { cadApp, cadBereichMitListe, listeZeichnen, umrissVon } from './cad_app.js';
import { knotenname } from './cad_modell.js';
import {
  eigenschaften, frischeAntwort, neuEigenschaften, stuetzeSetzen, vorgabeBeton,
} from './dk_eigenschaften.js';
import { anteilText, grundriss } from './dk_grundriss.js';
import { el } from './dom.js';
import { eintragVon, katalog, zustand } from './zustand.js';

/** Was die Arten heissen, je Liste -- einzeln und mehrere. */
const NAMEN = {
  stuetzen: ['Stütze', 'Stützen'],
  linienlager: ['Linienlager', 'Linienlager'],
  unterzuege: ['Unterzug', 'Unterzüge'],
  zonen: ['Zone', 'Zonen'],
  platten: ['Platte', 'Platten'],
};

/**
 * Die Arten der Decke, ihre Vorsilben vom Kern (`VORSILBEN` in
 * opencivil/projekt/decke.py). Eine Stütze vor allem: sie steht auf dem
 * Knoten, an dem sonst eine Platte gewählt würde -- gewählt wird aber ihr
 * Knoten (`waehlbar`). Eine Zone vor ihrer Platte: sie liegt in ihr.
 */
function arten() {
  const vorsilben = katalog('decke', 'vorsilben');
  return [
    ['stuetzen', 'punkt'], ['linienlager', 'linie'], ['unterzuege', 'linie'], ['zonen', 'flaeche'],
    ['platten', 'flaeche'],
  ].map(([liste, form], rang) => ({
    liste, form, rang, vorsilbe: vorsilben[liste], heisst: NAMEN[liste][0], mehrzahl: NAMEN[liste][1],
  }));
}

/** Meter, ein Raster bis 2 m und die Werkzeuge der Decke -- sie hängt an ihren Knoten. */
const EINSTELLUNG = {
  werkzeuge: [
    { name: 'platte', text: 'Platte', zeichen: 'cad-polygon', taste: 'p', form: 'polygon',
      titel: 'Platte -- ein Umriss aus Ecken, mit Dicke und Beton' },
    { name: 'lager', text: 'Linienlager', zeichen: 'cad-wand', taste: 'w', form: 'linie',
      titel: 'Linienlager -- eine Wand oder ein Rand: vertikal gehalten, eingespannt oder beides' },
    { name: 'stuetze', text: 'Stütze', zeichen: 'cad-stuetze', taste: 's', form: 'knoten',
      titel: 'Stütze -- an einen Knoten oder eine freie Stelle klicken' },
    { name: 'unterzug', text: 'Unterzug', zeichen: 'cad-unterzug', taste: 'u', form: 'linie',
      titel: 'Versteckter Unterzug -- ein starker Streifen in der Platte' },
    { name: 'zone', text: 'Zone', zeichen: 'cad-zone', taste: 'z', form: 'polygon',
      titel: 'Zone -- dort geht ein eigener Anteil der Last in Richtung 1' },
    { name: 'knoten', text: 'Knoten', zeichen: 'cad-knoten', taste: 'k', form: 'knoten' },
  ],
  einheit: 'm',
  raster: { stufen: [0.05, 0.1, 0.25, 0.5, 1, 2], vorgabe: 0.5 },
  stellen: 3,
  massstab: [0.2, 20000],
  verbunden: true,
};

/** Was unter den Teilen liegen kann -- die Wahl in der Leiste. */
const UNTERLAGEN = [
  { wert: 'aufteilung', beschriftung: 'Aufteilung',
    titel: 'Wie die Last auf die zwei Richtungen geht: orange Richtung 1, gelb Richtung 2' },
  { wert: 'streifen', beschriftung: 'Streifen',
    titel: 'Die Grenzen der Streifen beider Richtungen und die Stützenbereiche' },
  { wert: 'nichts', beschriftung: 'nichts', titel: 'Nur die gezeichneten Teile' },
];

// ===========================================================================
// Das Fenster einer Decke
// ===========================================================================

/** Die Zeichenfenster der Decken, je Kennung eines (cad_app.js); ihr Zustand hängt als `a.dk` daran. */
const DECKEN = cadApp('dk', adapter, (a) => { a.dk = a.adapter.dk; });
const fensterVon = DECKEN.fensterVon;
export const waehlen = DECKEN.waehlen;

/**
 * Das Zeichenfenster einer Decke, samt der Liste darunter. Die Tafel ruft
 * das bei jedem Neubau -- dann fragt es auch den Kern, wenn sich nicht die
 * Zeichnung geändert hat, aber ein Beton.
 */
export function zeichenbereich(decke, listeBauen) {
  const a = fensterVon(decke.kennung);
  const bereich = cadBereichMitListe(a, listeBauen);
  zeichnungHolen(a);
  unterlageLeiste(a);
  return bereich;
}

/** Die Wahl, was unter den Teilen liegt -- neben den Werkzeugen. */
function unterlageLeiste(a) {
  a.dk.leiste?.replaceChildren(wahlSchalter({
    werte: UNTERLAGEN, gewaehlt: a.dk.unterlage, titel: 'Was unter den Teilen liegt',
    setzen: (w) => {
      a.dk.unterlage = w;
      unterlageLeiste(a);
      a.neuZeichnen();
      // Die Legende unter der Zeichnung gilt nur für die Aufteilung.
      listeZeichnen(a);
    },
  }));
}

// ===========================================================================
// Der Adapter
// ===========================================================================

/** Was die Werkzeuge als Nächstes anlegen, je Liste: die Vorlage des Kerns. Der Beton leer heisst der erste des Projekts. */
function vorgabenNeu() {
  const vorlage = (klasse) => structuredClone(katalog('vorlagen', klasse));
  return {
    platten: vorlage('deckenplatte'),
    linienlager: vorlage('linienlager'),
    stuetzen: vorlage('stuetze'),
    unterzuege: vorlage('unterzug'),
    zonen: vorlage('zone'),
  };
}

/** Was der Adapter einer Decke über die gemeinsame Grundlage hinaus weiss (cad_app.js). */
function adapter(kennung) {
  const dk = {
    kennung, vorgaben: vorgabenNeu(), vorsilben: katalog('decke', 'vorsilben'), daten: null, gefragt: null,
    unterlage: 'aufteilung', leiste: null,
  };
  return {
    dk,
    einstellung: EINSTELLUNG,
    achsen: ['x', 'y'],
    arten: arten(),
    leisteZusatz: () => {
      dk.leiste = el('span.dk-unterlagewahl');
      return dk.leiste;
    },
    name: elementname,
    neuText,
    punktAnlegen,
    linieAnlegen,
    flaecheAnlegen,
    zeichnen,
    waehlbar: (art) => art.liste !== 'stuetzen',
    umriss: () => umrissVon((eintragVon(kennung)?.knoten || []).map((k) => [k.x, k.y]), [[0, 0], [10, 8]]),
    geaendert: zeichnungHolen,
    eigenschaften,
    neuEigenschaften,
  };
}

/** Wie ein Teil heisst: nach seiner Kennung, mit der Art davor -- «Platte P2». */
function elementname(a, kennung) {
  if (!kennung) return '';
  const art = a.adapter.arten.find((x) => new RegExp(`^${x.vorsilbe}\\d+$`).test(kennung));
  return knotenname(kennung) ?? (art ? `${art.heisst} ${kennung}` : kennung);
}

/** Was das Werkzeug als Nächstes anlegt, in Worten -- für die Frage im schwebenden Fenster. */
function neuText(a, werkzeug) {
  const v = a.dk.vorgaben;
  if (werkzeug === 'platte') return `Platte ${v.platten.h} mm`;
  if (werkzeug === 'zone') return `Zone ${anteilText(v.zonen.anteil)}`;
  return EINSTELLUNG.werkzeuge.find((w) => w.name === werkzeug)?.text || '';
}

/** Eine Stütze an den Knoten -- gewählt bleibt der Knoten, sein Fenster zeigt sie. */
function punktAnlegen(a, z, knoten, werkzeug) {
  if (werkzeug === 'stuetze') stuetzeSetzen(a, z, knoten, true);
  return null;
}

function linieAnlegen(a, z, von, bis, werkzeug) {
  const liste = werkzeug === 'unterzug' ? 'unterzuege' : 'linienlager';
  const kennung = a.modell.naechsteKennung(z, a.dk.vorsilben[liste]);
  z[liste].push({ ...structuredClone(a.dk.vorgaben[liste]), kennung, von, bis });
  return kennung;
}

function flaecheAnlegen(a, z, knoten, werkzeug) {
  const liste = werkzeug === 'zone' ? 'zonen' : 'platten';
  const kennung = a.modell.naechsteKennung(z, a.dk.vorsilben[liste]);
  z[liste].push({
    ...structuredClone(a.dk.vorgaben[liste]), kennung, knoten,
    ...(liste === 'platten' ? { beton: vorgabeBeton(a) } : {}),
  });
  return kennung;
}

// ===========================================================================
// Der Kern
// ===========================================================================

/**
 * Fragt den Kern nach der Decke, wenn sie sich seit der letzten Frage
 * geändert hat. Kommt eine Antwort zu spät -- es wurde inzwischen wieder
 * gefragt --, gilt sie nicht mehr.
 */
function zeichnungHolen(a) {
  if (!eintragVon(a.dk.kennung)) return;
  const jetzt = zustand.fassung;
  if (a.dk.gefragt === jetzt) return;
  a.dk.gefragt = jetzt;
  api.deckeZeichnung(zustand.projekt, a.dk.kennung).then((antwort) => {
    if (a.dk.gefragt !== jetzt) return;
    a.dk.daten = { ...antwort.uebersicht, fassung: jetzt };
    a.neuZeichnen();
    listeZeichnen(a);
  }).catch((fehler) => {
    if (a.dk.gefragt !== jetzt) return;
    // Ein Verweis, den es nicht gibt, hält das ganze Projekt auf -- dann
    // steht der Satz des Kerns unter der Zeichnung.
    a.dk.daten = { gerechnet: false, fehler: fehler.message, meldungen: [], fassung: jetzt };
    a.neuZeichnen();
    listeZeichnen(a);
  });
}

// ===========================================================================
// Zeichnen
// ===========================================================================

function zeichnen(a, g) {
  const z = eintragVon(a.dk.kennung);
  if (!z) return;
  const frisch = frischeAntwort(a);
  const je = new Map();
  for (const m of frisch?.meldungen || []) {
    for (const k of m.elemente) je.set(k, [...(je.get(k) || []), m]);
  }
  const daten = a.dk.daten && { ...a.dk.daten, veraltet: !frisch };
  g.append(grundriss(a.v, z, daten, {
    was: a.dk.unterlage,
    fehler: (k) => (je.get(k) || []).some((m) => m.fehler),
    texte: (k) => (je.get(k) || []).map((m) => m.text),
  }));
}
