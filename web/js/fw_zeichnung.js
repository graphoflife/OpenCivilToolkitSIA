/**
 * fw_zeichnung.js -- das Zeichenfenster eines Fachwerkmodells: Adapter und Seitenleiste.
 *
 * Gezeichnet wird eine Scheibe in Metern, x nach rechts und y nach oben, wie
 * die Decke: Scheiben und Löcher als Umrisse, Lager und Lasten an Knoten.
 * Alles hängt an Knoten (`verbunden`): ein Lager an einer Ecke verschiebt
 * sich mit ihr. Lager und Last wählt man nicht für sich, sondern ihren
 * Knoten, wie eine Stütze der Decke: sein Fenster zeigt sie, je mit einem
 * Schalter, der sie an- und abstellt.
 *
 * WAS DER KERN SAGT:
 * Anfrage `fachwerk_zeichnung`: die Meldungen -- ein Lager neben der
 * Scheibe, eine Scheibe, die sich noch bewegen kann. Sie gelten nur,
 * solange die Zeichnung dieselbe ist, nach der gefragt wurde.
 *
 * Das Bild steht in `fw_bild.js`. Gerechnet wird hier nichts; Einheiten und
 * Grenzen der Felder sagt der Kern (`katalog.felder`).
 */

import { api } from './api.js';
import {
  gemeinsam, mitBild, mitVar, wahlBlock, wahlSchalter,
} from './bausteine.js';
import {
  auswahlEigenschaften, cadApp, cadBereichMitListe, jaNein, lagefelder, meldungenJe, meldungszeilen, teilname,
  umrissVon, vorgabe, zahlfeldMitVar, zugleich,
} from './cad_app.js';
import { cadZeile, schalterzeile } from './cad_palette.js';
import { el } from './dom.js';
import { scheibe } from './fw_bild.js';
import { eintragVon, feldangabe, katalog, zustand } from './zustand.js';

/** Was die Arten heissen, je Liste -- einzeln und mehrere. */
const NAMEN = {
  lager: ['Lager', 'Lager'], lasten: ['Last', 'Lasten'], loecher: ['Loch', 'Löcher'], scheiben: ['Scheibe', 'Scheiben'],
};

/**
 * Die Arten des Fachwerkmodells, ihre Vorsilben vom Kern (`VORSILBEN` in
 * opencivil/projekt/fachwerkmodell.py). Lager und Last vor allem: sie stehen
 * auf dem Knoten, an dem sonst eine Scheibe gewählt würde -- gewählt wird
 * aber ihr Knoten (`waehlbar`). Ein Loch vor der Scheibe: es liegt darauf.
 */
function arten() {
  const vorsilben = katalog('fachwerkmodell', 'vorsilben');
  return [['lager', 'punkt'], ['lasten', 'punkt'], ['loecher', 'flaeche'], ['scheiben', 'flaeche']]
    .map(([liste, form], rang) => ({
      liste, form, rang, vorsilbe: vorsilben[liste], heisst: NAMEN[liste][0], mehrzahl: NAMEN[liste][1],
    }));
}

/** Meter und ein Raster bis 2 m, wie die Decke -- das Modell hängt an seinen Knoten. */
const EINSTELLUNG = {
  werkzeuge: [
    { name: 'scheibe', text: 'Scheibe', zeichen: 'cad-scheibe', taste: 's', form: 'polygon',
      titel: 'Scheibe – ein Umriss aus Ecken; liegen mehrere da, ist Material, wo eine von ihnen ist' },
    { name: 'loch', text: 'Loch', zeichen: 'cad-loch', taste: 'o', form: 'polygon',
      titel: 'Loch – in seinem Innern ist kein Material, auf seinem Rand schon' },
    { name: 'lager', text: 'Lager', zeichen: 'halt-xy', taste: 'a', form: 'knoten',
      titel: 'Lager – an einen Knoten oder eine freie Stelle klicken, am Rand oder innen' },
    { name: 'last', text: 'Last', zeichen: 'cad-punktlast', taste: 'q', form: 'knoten',
      titel: 'Last – eine Punktlast an einen Knoten oder eine freie Stelle, in jeder Richtung' },
    { name: 'knoten', text: 'Knoten', zeichen: 'cad-knoten', taste: 'k', form: 'knoten' },
  ],
  einheit: 'm',
  raster: { stufen: [0.05, 0.1, 0.25, 0.5, 1, 2], vorgabe: 0.5 },
  stellen: 3,
  massstab: [0.2, 20000],
  verbunden: true,
};

/** Welche Liste ein Werkzeug füllt -- der Knoten keine. */
const LISTE_VON = { scheibe: 'scheiben', loch: 'loecher', lager: 'lager', last: 'lasten' };

// ===========================================================================
// Das Fenster eines Fachwerkmodells
// ===========================================================================

/** Die Zeichenfenster der Fachwerkmodelle, je Kennung eines (cad_app.js); ihr Zustand hängt als `a.fw` daran. */
const fensterVon = cadApp('fw', adapter, (a) => { a.fw = a.adapter.fw; });

/** Das Zeichenfenster eines Fachwerkmodells, samt der Liste darunter. Die Tafel ruft das bei jedem Neubau. */
export function zeichenbereich(modell, listeBauen) {
  return cadBereichMitListe(fensterVon(modell.kennung), listeBauen);
}

/** Was die Werkzeuge als Nächstes anlegen, je Liste: die Vorlage des Kerns. */
function vorgabenNeu() {
  const vorlage = (klasse) => structuredClone(katalog('vorlagen', klasse));
  return {
    scheiben: vorlage('scheibe'), loecher: vorlage('loch'), lager: vorlage('scheibenlager'),
    lasten: vorlage('scheibenlast'),
  };
}

/**
 * Was der Adapter eines Fachwerkmodells über die gemeinsame Grundlage
 * hinaus weiss (cad_app.js). Den Kern fragt er nach der Zeichnung (Anfrage
 * `fachwerk_zeichnung`).
 */
function adapter(kennung) {
  const fw = { kennung, vorgaben: vorgabenNeu(), vorsilben: katalog('fachwerkmodell', 'vorsilben') };
  return {
    fw,
    einstellung: EINSTELLUNG,
    achsen: ['x', 'y'],
    arten: arten(),
    name: teilname,
    neuText: (a, werkzeug) => EINSTELLUNG.werkzeuge.find((w) => w.name === werkzeug)?.text || '',
    punktAnlegen,
    flaecheAnlegen,
    zeichnen,
    waehlbar: (art) => !['lager', 'lasten'].includes(art.liste),
    umriss: () => umrissVon((eintragVon(kennung)?.knoten || []).map((k) => [k.x, k.y]), [[0, 0], [6, 3]]),
    fragen: () => api.fachwerkZeichnung(zustand.projekt, kennung),
    nehmen: (_, antwort) => antwort.uebersicht,
    eigenschaften,
    neuEigenschaften,
  };
}

/**
 * Setzt an einen Knoten ein Lager oder eine Last nach der Vorgabe ihres
 * Werkzeugs -- oder nimmt sie weg. Je Knoten eines und eine.
 */
function anKnoten(a, z, liste, knoten, an) {
  const da = z[liste].some((e) => e.knoten === knoten);
  if (!an) z[liste] = z[liste].filter((e) => e.knoten !== knoten);
  else if (!da) {
    z[liste].push({
      ...structuredClone(a.fw.vorgaben[liste]), kennung: a.modell.naechsteKennung(z, a.fw.vorsilben[liste]), knoten,
    });
  }
}

/** Ein Lager oder eine Last an den Knoten -- gewählt bleibt der Knoten, sein Fenster zeigt sie. */
function punktAnlegen(a, z, knoten, werkzeug) {
  if (LISTE_VON[werkzeug]) anKnoten(a, z, LISTE_VON[werkzeug], knoten, true);
  return null;
}

function flaecheAnlegen(a, z, knoten, werkzeug) {
  const liste = LISTE_VON[werkzeug] || 'scheiben';
  const kennung = a.modell.naechsteKennung(z, a.fw.vorsilben[liste]);
  z[liste].push({ ...structuredClone(a.fw.vorgaben[liste]), kennung, knoten });
  return kennung;
}

/** Das Modell, darüber rot, was der Kern an einem Teil beanstandet. */
function zeichnen(a, g) {
  const z = eintragVon(a.fw.kennung);
  if (!z) return;
  g.append(scheibe(a.v, z, meldungenJe(a)));
}

// ===========================================================================
// Die Seitenleiste
// ===========================================================================

/**
 * Ein Zahlenfeld mit Beschriftung und der Einheit des Kerns -- `klasse` ist
 * der Name der Einträge im Katalog, `wert(feld)` das Gemeinsame der
 * gewählten, `setzen(feld)` schreibt.
 */
function feldzeile(klasse, feld, beschriftung, wert, setzen, { schritt = 1, titel } = {}) {
  const angabe = feldangabe(klasse, feld);
  return cadZeile(beschriftung, zahlfeldMitVar({
    wert: wert(feld), schritt, angabe, titel, beiAenderung: setzen(feld),
  }), angabe.einheit || '');
}

/** Die Felder je Art, für die Vorgabe eines Werkzeugs wie für gewählte Teile. */
const FELDER = {
  lager: (wert, setzen) => [wahlBlock('Hält', wahlSchalter({
    werte: mitVar(mitBild(katalog('fachwerkmodell', 'halt'), 'halt'), wert('halt')),
    gewaehlt: wert('halt'), setzen: setzen('halt'), titel: 'In welchen Richtungen das Lager die Scheibe hält',
  }))],
  lasten: (wert, setzen) => [
    feldzeile('scheibenlast', 'F_h', 'F_h', wert, setzen, { schritt: 10, titel: 'Waagrecht, nach rechts positiv' }),
    feldzeile('scheibenlast', 'F_v', 'F_v', wert, setzen, { schritt: 10, titel: 'Senkrecht, nach unten positiv' }),
  ],
};

/** Die Felder für das, was ein Werkzeug als Nächstes anlegt -- eine Scheibe und ein Loch haben keine. */
function neuEigenschaften(a, werkzeug) {
  const liste = LISTE_VON[werkzeug];
  if (!FELDER[liste]) return { inhalt: [], schluessel: werkzeug };
  const v = a.fw.vorgaben[liste];
  const { wert, setzen } = vorgabe(a, v);
  return { inhalt: FELDER[liste](wert, setzen), schluessel: JSON.stringify([werkzeug, v]) };
}

/** Was gewählt ist (cad_app.js): Knoten -- mit Lager und Last -- oder Scheiben und Löcher. */
function eigenschaften(a) {
  return auswahlEigenschaften(a, { knoten: knotenEigenschaften, sonst: teilEigenschaften });
}

/**
 * Lager oder Last der gewählten Knoten: ein Schalter, dann ihre Felder --
 * nur, wenn jeder gewählte Knoten eines hat, sonst stünde da, was nur für
 * einige gilt.
 */
function anhangFelder(a, z, knoten, liste, titel) {
  const teile = knoten.map((k) => z[liste].find((e) => e.knoten === k) || null);
  const zeilen = [schalterzeile(NAMEN[liste][0], jaNein(gemeinsam(teile.map(Boolean)), (w) => a.aendern((zz) => {
    for (const k of knoten) anKnoten(a, zz, liste, k, w);
  }), titel))];
  if (teile.some((e) => !e)) return zeilen;
  const kennungen = teile.map((e) => e.kennung);
  const { wert, setzen } = zugleich(a, z, liste, kennungen);
  return [...zeilen, ...FELDER[liste](wert, setzen), ...meldungszeilen(a, kennungen)];
}

/** Gewählte Knoten: ihre Lage (cad_app.js), ihr Lager und ihre Last. */
function knotenEigenschaften(a, z, knoten) {
  return {
    titel: knoten.length === 1 ? `Knoten ${knoten[0]}` : `${knoten.length} Knoten`,
    inhalt: [
      ...lagefelder(a, z, knoten),
      ...anhangFelder(a, z, knoten, 'lager', 'Ein Lager an diesem Knoten'),
      ...anhangFelder(a, z, knoten, 'lasten', 'Eine Punktlast an diesem Knoten'),
      ...meldungszeilen(a, knoten),
    ],
  };
}

/** Gewählte Scheiben oder Löcher: ohne Felder, nur was der Kern zu ihnen sagt. */
function teilEigenschaften(a, z, kennungen, liste) {
  const art = a.adapter.arten.find((x) => x.liste === liste);
  const meldungen = meldungszeilen(a, kennungen);
  return {
    titel: kennungen.length === 1 ? a.adapter.name(a, kennungen[0]) : `${kennungen.length} ${art.mehrzahl}`,
    inhalt: meldungen.length ? meldungen : [el('p.cad-hinweis-klein', {
      text: liste === 'loecher' ? 'Ein Loch nimmt das Material in seinem Innern weg.'
        : 'Ihre Ecken verschiebt man mit V; ein Loch zeichnet man darüber.',
    })],
  };
}
