/**
 * dk_eigenschaften.js -- das schwebende Fenster im Zeichenfenster einer Decke.
 *
 * Was ein Werkzeug als Nächstes anlegt (`neuEigenschaften`) und was gewählt
 * ist (`eigenschaften`): je Knoten -- mit seiner Stütze --, Platte,
 * Linienlager, Unterzug oder Zone seine Felder. Sind mehrere derselben Art
 * gewählt, ändert das Fenster alle zugleich; was sie gemeinsam haben, steht
 * da, sonst «Var» -- wie im Balkensystem. Eine Stütze wählt man nicht für
 * sich: sie steht im Fenster ihres Knotens, wie ein Lager im Balkensystem.
 *
 * Vom Zeichenfenster kennt es nur `a`: was die Werkzeuge vorgeben
 * (`a.dk.vorgaben`), die letzte Antwort des Kerns (`a.dk.daten`) und das
 * Modell. Einheiten und Grenzen der Felder sagt der Kern (`katalog.felder`).
 * Gerechnet wird hier nichts.
 */

import { wahlBlock, wahlSchalter } from './bausteine.js';
import { zahlText } from './cad_ansicht.js';
import {
  cadZeile, gemeinsam, jaNein, mitVar, schalterzeile, zahlfeldMitVar,
} from './cad_app.js';
import { abstand, auswahlTeil } from './cad_modell.js';
import { auswahl, el } from './dom.js';
import { feldangabe, materialien, zustand } from './zustand.js';

/** Die Antwort des Kerns, wenn sie zur Zeichnung gehört, wie sie jetzt ist -- sonst null. */
export function frischeAntwort(a) {
  const d = a.dk.daten;
  return d && d.fassung === zustand.fassung ? d : null;
}

/** Der Beton, den eine neue Platte bekommt: der gewählte, sonst der erste des Projekts. */
export function vorgabeBeton(a) {
  return a.dk.vorgaben.platten.beton || materialien('beton')[0]?.kennung || '';
}

/**
 * Ein Zahlenfeld mit Beschriftung und der Einheit des Kerns. `klasse` ist
 * der Name der Einträge im Katalog (`deckenplatte`), `wert(feld)` das
 * Gemeinsame der gewählten, `setzen(feld)` schreibt.
 */
function feldzeile(klasse, feld, beschriftung, wert, setzen, { schritt = 1, titel } = {}) {
  const angabe = feldangabe(klasse, feld);
  return cadZeile(beschriftung, zahlfeldMitVar({
    wert: wert(feld), schritt, angabe, titel, beiAenderung: setzen(feld),
  }), angabe.einheit || '');
}

/** Die Betone des Projekts -- eine Wahl aus dem Projekt, darum eine Liste. */
function betonWahl(gewaehlt, setzen) {
  const werte = materialien('beton').map((b) => ({ wert: b.kennung, beschriftung: b.name || b.sorte }));
  return auswahl({
    werte: werte.some((x) => x.wert === gewaehlt) ? mitVar(werte, gewaehlt)
      : [{ wert: gewaehlt, beschriftung: '– Beton wählen –' }, ...werte],
    gewaehlt, titel: 'E_cm und das Gewicht der Platte kommen von ihm', beiAenderung: setzen,
  });
}

/**
 * Die Felder je Art -- für die Vorgabe eines Werkzeugs wie für gewählte
 * Teile; `wert` und `setzen` wie bei `feldzeile`.
 */
const FELDER = {
  platten: (wert, setzen) => [
    feldzeile('deckenplatte', 'h', 'Dicke h', wert, setzen, { schritt: 10 }),
    cadZeile('Beton', betonWahl(wert('beton'), setzen('beton'))),
    feldzeile('deckenplatte', 'richtung_1', 'Richtung 1', wert, setzen, {
      schritt: 15, titel: 'In diese Richtung tragen die Streifen der Richtung 1 -- in Grad gegen x',
    }),
    feldzeile('deckenplatte', 'richtung_2', 'Richtung 2', wert, setzen, {
      schritt: 15, titel: 'Die zweite Richtung der Streifen -- in Grad gegen x, nicht gleich der ersten',
    }),
  ],
  linienlager: (wert, setzen) => [
    schalterzeile('vertikal', jaNein(wert('vertikal'), setzen('vertikal'),
      'Hält die Platte in der Höhe -- eine Wand, ein Träger')),
    schalterzeile('eingespannt', jaNein(wert('eingespannt'), setzen('eingespannt'),
      'Hält die Drehung -- ohne vertikalen Halt wie an einer Symmetrieachse')),
  ],
  unterzuege: (wert, setzen) => [
    feldzeile('unterzug', 'breite', 'Breite b', wert, setzen, {
      schritt: 0.1, titel: 'So breit trägt der Unterzug als Streifen in der Platte',
    }),
    feldzeile('unterzug', 'stufe', 'Stufe', wert, setzen, {
      titel: 'Ein Unterzug liegt auf denen höherer Stufe, die ihn kreuzen',
    }),
  ],
  zonen: (wert, setzen) => [
    feldzeile('zone', 'anteil', 'Richtung 1', wert, setzen, {
      schritt: 10, titel: 'Dieser Anteil der Last geht in Richtung 1 der Platte, der Rest in Richtung 2',
    }),
  ],
  stuetzen: (wert, setzen) => {
    const vonHand = wert('bereich_von_hand');
    return [
      feldzeile('stuetze', 'b_x', 'b_x', wert, setzen, { schritt: 50 }),
      feldzeile('stuetze', 'b_y', 'b_y', wert, setzen, { schritt: 50 }),
      wahlBlock('Stützenbereich', wahlSchalter({
        werte: mitVar([
          { wert: false, beschriftung: 'von selbst', titel: 'So gross wie die Stütze oder der breiteste Unterzug über ihr' },
          { wert: true, beschriftung: 'von Hand', titel: 'l_x × l_y von Hand' },
        ], vonHand),
        gewaehlt: vonHand, setzen: setzen('bereich_von_hand'),
        titel: 'Über diesen Bereich geben die Streifen ihre Last an die Stütze ab (Folie 39)',
      })),
      ...(vonHand === true ? [
        feldzeile('stuetze', 'l_x', 'l_x', wert, setzen, { schritt: 0.1 }),
        feldzeile('stuetze', 'l_y', 'l_y', wert, setzen, { schritt: 0.1 }),
      ] : []),
    ];
  },
};

/** Welche Liste ein Werkzeug füllt -- der Knoten keine. */
const LISTE_VON = {
  platte: 'platten', lager: 'linienlager', stuetze: 'stuetzen', unterzug: 'unterzuege', zone: 'zonen',
};

/** Die Felder für das, was ein Werkzeug als Nächstes anlegt. */
export function neuEigenschaften(a, werkzeug) {
  const liste = LISTE_VON[werkzeug];
  if (!liste) return { inhalt: [], schluessel: werkzeug };
  const v = a.dk.vorgaben[liste];
  const wert = (feld) => (feld === 'beton' ? vorgabeBeton(a) : v[feld]);
  const setzen = (feld) => (w) => { v[feld] = w; a.neuZeichnen(); };
  return {
    inhalt: [el('div.cad-neu-titel', { text: 'Neu' }), ...FELDER[liste](wert, setzen)],
    schluessel: JSON.stringify([werkzeug, v, vorgabeBeton(a)]),
  };
}

/** Was der Kern zu diesen Teilen meldet -- nur, wenn seine Antwort zur Zeichnung gehört. */
function meldungszeilen(a, kennungen) {
  return (frischeAntwort(a)?.meldungen || []).filter((m) => m.elemente.some((k) => kennungen.includes(k)))
    .map((m) => el(m.fehler ? 'p.cad-meldung' : 'p.cad-hinweis-klein', { text: m.text }));
}

export function eigenschaften(a) {
  const z = a.adapter.zeichnung();
  const verzeichnis = a.modell.verzeichnis(z);
  const kennungen = [...new Set([...a.auswahl].map((s) => auswahlTeil(s).kennung))]
    .filter((k) => verzeichnis.has(k));
  const listen = new Set(kennungen.map((k) => verzeichnis.get(k).art?.liste ?? 'knoten'));
  const schluessel = JSON.stringify([Boolean(frischeAntwort(a))]);
  if (!kennungen.length) return { titel: '', inhalt: [] };
  if (listen.size > 1) {
    return {
      titel: `${kennungen.length} gewählt`,
      inhalt: [el('p.cad-hinweis-klein', { text: 'Verschiedenes zugleich -- verschieben mit V, löschen mit Entf.' })],
      schluessel,
    };
  }
  const [liste] = listen;
  if (liste === 'knoten') return { ...knotenEigenschaften(a, z, kennungen), schluessel };
  return { ...teilEigenschaften(a, z, liste, kennungen), schluessel };
}

// -- Knoten und ihre Stützen -------------------------------------------------

/** Setzt an einen Knoten eine Stütze nach der Vorgabe des Werkzeugs -- oder nimmt sie weg. */
export function stuetzeSetzen(a, z, knoten, an) {
  const da = z.stuetzen.some((s) => s.knoten === knoten);
  if (!an) z.stuetzen = z.stuetzen.filter((s) => s.knoten !== knoten);
  else if (!da) {
    z.stuetzen.push({
      ...structuredClone(a.dk.vorgaben.stuetzen), kennung: a.modell.naechsteKennung(z, a.dk.vorsilben.stuetzen), knoten,
    });
  }
}

function stuetzeFelder(a, z, knoten) {
  const stuetzen = knoten.map((k) => z.stuetzen.find((s) => s.knoten === k) || null);
  const zeilen = [schalterzeile('Stütze', jaNein(gemeinsam(stuetzen.map(Boolean)), (w) => a.aendern((zz) => {
    for (const k of knoten) stuetzeSetzen(a, zz, k, w);
  }), 'Eine Stütze unter diesem Knoten'))];
  // Ihre Felder nur, wenn jeder gewählte Knoten eine hat -- sonst stünde
  // da, was nur für einige gilt.
  if (stuetzen.some((s) => !s)) return zeilen;
  const wert = (feld) => gemeinsam(stuetzen.map((s) => s[feld]));
  const setzen = (feld) => (w) => a.aendern((zz) => {
    for (const s of zz.stuetzen) if (knoten.includes(s.knoten)) s[feld] = w;
  });
  return [...zeilen, ...FELDER.stuetzen(wert, setzen), ...meldungszeilen(a, stuetzen.map((s) => s.kennung))];
}

function knotenEigenschaften(a, z, knoten) {
  const gewaehlt = z.knoten.filter((x) => knoten.includes(x.kennung));
  // Eine getippte Lage gilt für alle gewählten -- so stehen sie danach in einer Flucht.
  const lageSetzen = (feld) => (w) => a.aendern((zz) => {
    for (const kennung of knoten) {
      const da = zz.knoten.find((x) => x.kennung === kennung);
      if (da) a.modell.verschieben(zz, new Set([kennung]), feld === 'x' ? [w - da.x, 0] : [0, w - da.y]);
    }
  });
  return {
    titel: knoten.length === 1 ? `Knoten ${knoten[0]}` : `${knoten.length} Knoten`,
    inhalt: [
      ...['x', 'y'].map((feld) => cadZeile(feld, zahlfeldMitVar({
        wert: gemeinsam(gewaehlt.map((k) => k[feld])), schritt: a.raster, beiAenderung: lageSetzen(feld),
      }), a.einstellung.einheit)),
      ...stuetzeFelder(a, z, knoten),
      ...meldungszeilen(a, knoten),
    ],
  };
}

// -- Platten, Linienlager, Unterzüge, Zonen -----------------------------------

function teilEigenschaften(a, z, liste, kennungen) {
  const gewaehlt = z[liste].filter((x) => kennungen.includes(x.kennung));
  const wert = (feld) => gemeinsam(gewaehlt.map((e) => e[feld]));
  const setzen = (feld) => (w) => a.aendern((zz) => {
    for (const e of zz[liste]) if (kennungen.includes(e.kennung)) e[feld] = w;
  });
  const inhalt = [...FELDER[liste](wert, setzen)];
  const art = a.adapter.arten.find((x) => x.liste === liste);
  if (gewaehlt.length === 1 && art.form === 'linie') {
    const [e] = gewaehlt;
    const lagen = a.modell.lagen(z);
    const [p, q] = [lagen.get(e.von), lagen.get(e.bis)];
    if (p && q) inhalt.push(el('p.cad-info', { text: `L = ${zahlText(abstand(p, q), 3)} m · ${e.von} → ${e.bis}` }));
  }
  inhalt.push(...meldungszeilen(a, kennungen));
  return {
    titel: gewaehlt.length === 1 ? a.adapter.name(a, gewaehlt[0].kennung) : `${gewaehlt.length} ${art.mehrzahl}`,
    inhalt,
  };
}
