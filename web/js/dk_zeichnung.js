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
 * LASTEN:
 * Flächen-, Linien- und Punktlasten zeichnen die Werkzeuge in den Lastfall,
 * der in der Leiste gewählt ist (lastfaelle.js), wie im Balkensystem. Das
 * Fenster zeigt nur dessen Lasten, und nur sie lassen sich wählen. Eine
 * Punktlast steht wie eine Stütze an ihrem Knoten, die Last auf einer ganzen
 * Platte im Fenster der Platte.
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
  LASTLISTEN, eigenschaften, frischeAntwort, kernmeldungen, neuEigenschaften, punktlastSetzen, stuetzeSetzen,
  vorgabeBeton,
} from './dk_eigenschaften.js';
import { anteilText, grundriss } from './dk_grundriss.js';
import { el } from './dom.js';
import { aktiverLastfall, lastfallFuerNeue, lastfallLeiste } from './lastfaelle.js';
import { eintragVon, katalog, zustand } from './zustand.js';

/** Was die Arten heissen, je Liste -- einzeln und mehrere. */
const NAMEN = {
  stuetzen: ['Stütze', 'Stützen'],
  punktlasten: ['Punktlast', 'Punktlasten'],
  linienlasten: ['Linienlast', 'Linienlasten'],
  linienlager: ['Linienlager', 'Linienlager'],
  unterzuege: ['Unterzug', 'Unterzüge'],
  flaechenlasten: ['Flächenlast', 'Flächenlasten'],
  zonen: ['Zone', 'Zonen'],
  platten: ['Platte', 'Platten'],
};

/**
 * Die Arten der Decke, ihre Vorsilben vom Kern (`VORSILBEN` in
 * opencivil/projekt/decke.py). Eine Stütze und eine Punktlast vor allem:
 * sie stehen auf dem Knoten, an dem sonst eine Platte gewählt würde --
 * gewählt wird aber ihr Knoten (`waehlbar`). Eine Last vor dem, worauf sie
 * liegt, und eine Zone vor ihrer Platte: sie liegen darauf.
 */
function arten() {
  const vorsilben = katalog('decke', 'vorsilben');
  return [
    ['stuetzen', 'punkt'], ['punktlasten', 'punkt'], ['linienlasten', 'linie'], ['linienlager', 'linie'],
    ['unterzuege', 'linie'], ['flaechenlasten', 'flaeche'], ['zonen', 'flaeche'], ['platten', 'flaeche'],
  ].map(([liste, form], rang) => ({
    liste, form, rang, vorsilbe: vorsilben[liste], heisst: NAMEN[liste][0], mehrzahl: NAMEN[liste][1],
  }));
}

/** Eine Last braucht einen Lastfall -- ohne einen startet ihr Werkzeug nicht und sagt, wo er zu wählen ist. */
function lastBereit(a) {
  return Boolean(lastfallFuerNeue(a.dk));
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
    { name: 'flaechenlast', text: 'Flächenlast', zeichen: 'cad-flaechenlast', taste: 'q', form: 'polygon',
      bereit: lastBereit,
      titel: 'Flächenlast -- ein Umriss im gewählten Lastfall; auf einer ganzen Platte im Fenster der Platte' },
    { name: 'linienlast', text: 'Linienlast', zeichen: 'cad-linienlast', taste: 'l', form: 'linie',
      bereit: lastBereit, titel: 'Linienlast -- von Punkt zu Punkt, im gewählten Lastfall' },
    { name: 'punktlast', text: 'Punktlast', zeichen: 'cad-punktlast', taste: 'e', form: 'knoten',
      bereit: lastBereit, titel: 'Punktlast -- an einen Knoten oder eine freie Stelle, im gewählten Lastfall' },
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
  lastfallLeiste(a, a.dk, a.dk.lastfallHuelle);
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
    flaechenlasten: vorlage('flaechenlast'),
    linienlasten: vorlage('linienlast'),
    punktlasten: vorlage('punktlast'),
  };
}

/** Was der Adapter einer Decke über die gemeinsame Grundlage hinaus weiss (cad_app.js). */
function adapter(kennung) {
  const dk = {
    kennung, vorgaben: vorgabenNeu(), vorsilben: katalog('decke', 'vorsilben'), daten: null, gefragt: null,
    unterlage: 'aufteilung', leiste: null, lastfall: null, lastfallHuelle: null,
  };
  return {
    dk,
    einstellung: EINSTELLUNG,
    achsen: ['x', 'y'],
    arten: arten(),
    // Der Lastfall gleich neben den Werkzeugen, wie im Balkensystem -- dann die Unterlage.
    leisteZusatz: () => {
      dk.lastfallHuelle = el('span.bs-lastfallwahl');
      dk.leiste = el('span.dk-unterlagewahl');
      return el('span.dk-leistenzusatz', {}, [dk.lastfallHuelle, dk.leiste]);
    },
    name: elementname,
    neuText,
    punktAnlegen,
    linieAnlegen,
    flaecheAnlegen,
    zeichnen,
    // Eine Last nur in dem Lastfall, den das Fenster zeigt -- die anderen sind nicht zu sehen.
    waehlbar: (art, e) => !['stuetzen', 'punktlasten'].includes(art.liste)
      && (!LASTLISTEN.includes(art.liste) || e.lastfall === aktiverLastfall(dk)),
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

/**
 * Eine Stütze oder Punktlast an den Knoten -- gewählt bleibt der Knoten,
 * sein Fenster zeigt sie. Eine Last geht in den gezeigten Lastfall; ist
 * keiner mehr gewählt, seit das Werkzeug lief, bleibt es beim Knoten.
 */
function punktAnlegen(a, z, knoten, werkzeug) {
  if (werkzeug === 'stuetze') stuetzeSetzen(a, z, knoten, true);
  const lf = werkzeug === 'punktlast' && lastfallFuerNeue(a.dk);
  if (lf) punktlastSetzen(a, z, knoten, true, lf);
  return null;
}

/** Ein neuer Eintrag der Liste nach der Vorgabe ihres Werkzeugs -- eine Last im gezeigten Lastfall, sonst keiner. */
function anlegen(a, z, liste, felder) {
  const zusatz = {};
  if (LASTLISTEN.includes(liste)) {
    zusatz.lastfall = lastfallFuerNeue(a.dk);
    if (!zusatz.lastfall) return null;
  }
  const kennung = a.modell.naechsteKennung(z, a.dk.vorsilben[liste]);
  z[liste].push({ ...structuredClone(a.dk.vorgaben[liste]), kennung, ...felder, ...zusatz });
  return kennung;
}

function linieAnlegen(a, z, von, bis, werkzeug) {
  const liste = { unterzug: 'unterzuege', linienlast: 'linienlasten' }[werkzeug] || 'linienlager';
  return anlegen(a, z, liste, { von, bis });
}

function flaecheAnlegen(a, z, knoten, werkzeug) {
  const liste = { zone: 'zonen', flaechenlast: 'flaechenlasten' }[werkzeug] || 'platten';
  return anlegen(a, z, liste, { knoten, ...(liste === 'platten' ? { beton: vorgabeBeton(a) } : {}) });
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
  const je = new Map();
  for (const m of kernmeldungen(a)) {
    for (const k of m.elemente) je.set(k, [...(je.get(k) || []), m]);
  }
  const daten = a.dk.daten && { ...a.dk.daten, veraltet: !frischeAntwort(a) };
  g.append(grundriss(a.v, z, daten, {
    was: a.dk.unterlage,
    fehler: (k) => (je.get(k) || []).some((m) => m.fehler),
    texte: (k) => (je.get(k) || []).map((m) => m.text),
    lastfall: aktiverLastfall(a.dk),
  }));
}
