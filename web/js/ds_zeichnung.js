/**
 * ds_zeichnung.js -- das Zeichenfenster einer Durchstanzstelle: der Adapter.
 *
 * Gezeichnet werden Aussparungen und Plattenbereiche: Polygone im Grundriss,
 * in mm, x nach rechts, y nach oben, die Achse der Stütze im Ursprung -- wie
 * im Kern (opencivil/projekt/durchstanzen.py). Je ein Werkzeug zeichnet sie,
 * Ecke um Ecke oder als Rechteck aus zwei Ecken (G); ein drittes setzt
 * Hilfspunkte zum Fangen. Ein Plattenbereich hat seine Dicke und die Seite
 * seiner Stufe: für den nächsten stehen sie in der Seitenleiste, solange
 * sein Werkzeug läuft, für gewählte, wenn man sie wählt. Ecken und Knoten
 * verschiebt man wie im Querschnitt: wählen, dann V oder die Felder in der
 * Seitenleiste.
 *
 * Darunter liegt, was der Kern zuletzt gerechnet hat: Stütze oder Wand,
 * Plattenrand, Nachweisschnitt, die Schnitte an den Stufen und der Schnitt
 * durch verschiedene Dicken (ds_grundriss.js). Die Ecken der Stütze fangen den Zeiger. Ändert sich
 * eine Aussparung oder ein Bereich, rechnet die nächste Lösung die Schnitte
 * neu -- bis dahin stehen die alten da.
 *
 * WAS HIER GERECHNET WIRD -- UND WAS NICHT:
 * Nichts, was in die Rechnung geht. Ob eine Aussparung den Schnitt mindert,
 * wo die Schnitte an den Stufen liegen und ob alles gültig ist, sagt der Kern.
 */

import { mitBild, wahlSchalter } from './bausteine.js';
import {
  auswahlEigenschaften, cadApp, teilname, umrissVon, vorgabe, zahlfeldMitVar, zugleich,
} from './cad_app.js';
import { nachBild, nachWelt } from './cad_ansicht.js';
import { cadBereich } from './cad_fenster.js';
import { cadZeile, schalterzeile } from './cad_palette.js';
import { el } from './dom.js';
import {
  aussparungTeile, bereichTeile, grundrissTeile, grundrissUmfang,
} from './ds_grundriss.js';
import {
  eintragVon, feldangabe, katalog, zustand,
} from './zustand.js';

/** Welche Liste ein Werkzeug füllt. */
const LISTE_VON = { aussparung: 'aussparungen', plattenbereich: 'plattenbereiche' };

/** Wie ein Teil einer Liste heisst, einzeln und mehrere -- «Bereich B1» wie im Kern. */
const NAMEN = {
  aussparungen: ['Aussparung', 'Aussparungen'],
  plattenbereiche: ['Bereich', 'Plattenbereiche'],
};

/**
 * Die Arten: Aussparung und Plattenbereich, je eine Fläche aus Knoten, ihre
 * Vorsilben vom Kern (`VORSILBEN` in opencivil/projekt/durchstanzen.py).
 */
function arten() {
  const vorsilben = katalog('durchstanzen', 'vorsilben');
  return ['aussparungen', 'plattenbereiche'].map((liste, rang) => ({
    liste, form: 'flaeche', rang, vorsilbe: vorsilben[liste], heisst: NAMEN[liste][0],
    mehrzahl: NAMEN[liste][1],
  }));
}

/** In mm, wie der Querschnitt -- aber mit dem Raster eines Grundrisses. */
const EINSTELLUNG = {
  werkzeuge: [
    { name: 'aussparung', text: 'Aussparung', zeichen: 'cad-polygon', taste: 'a', form: 'polygon',
      titel: 'Aussparung: die Ecken der Reihe nach – Enter oder ein Klick auf die erste schliesst; '
        + 'G für ein Rechteck aus zwei Ecken' },
    { name: 'plattenbereich', text: 'Plattenbereich', zeichen: 'cad-plattenbereich', taste: 'b',
      form: 'polygon',
      titel: 'Plattenbereich mit eigener Dicke: die Ecken der Reihe nach – G für ein Rechteck aus '
        + 'zwei Ecken' },
    { name: 'hilfspunkt', text: 'Hilfspunkt', zeichen: 'cad-hilfspunkt', taste: 'k', form: 'knoten',
      titel: 'Hilfspunkt: ein Knoten ohne Aussparung, zum Fangen' },
  ],
  einheit: 'mm',
  raster: { stufen: [5, 10, 25, 50, 100, 250], vorgabe: 50 },
  stellen: 0,
  massstab: [0.01, 20],
};

/** Was der Kern zuletzt zu dieser Stelle gerechnet hat -- oder null. */
function situationVon(kennung) {
  return zustand.loesung?.zeichendaten?.[kennung] || null;
}

/** Das Zeichenfenster einer Stelle, samt einer Zeile darunter. Die Tafel ruft das bei jedem Neubau. */
export function zeichenbereich(stelle) {
  return cadBereich(fensterVon(stelle.kennung), [el('p.cad-hinweis-klein', {
    text: 'Ausgezogen, was von den Schnitten zählt; gestrichelt, was nicht zählt. '
      + 'Die Schnitte kommen aus der letzten Rechnung.',
  })]);
}

/**
 * Was der Adapter einer Stelle über die gemeinsame Grundlage hinaus weiss
 * (cad_app.js) -- dazu, was das Werkzeug als Nächstes anlegt (`ds.vorgabe`,
 * die Vorlage des Kerns).
 */
function adapter(kennung) {
  const ds = { kennung, vorgabe: structuredClone(katalog('vorlagen', 'plattenbereich')) };
  const alle = arten();
  return {
    ds,
    einstellung: EINSTELLUNG,
    achsen: ['x', 'y'],
    arten: alle,
    name: teilname,
    neuText: (a, werkzeug) => ({
      aussparung: 'Aussparung', plattenbereich: `Plattenbereich, h = ${ds.vorgabe.h} mm`,
    }[werkzeug] || 'Hilfspunkt'),
    // Ein Hilfspunkt ist der Knoten selbst und legt nichts an.
    punktAnlegen: () => null,
    flaecheAnlegen: (a, z, knoten, werkzeug) => {
      const liste = LISTE_VON[werkzeug];
      const neu = a.modell.naechsteKennung(z, alle.find((x) => x.liste === liste).vorsilbe);
      z[liste] = z[liste] || [];
      z[liste].push(liste === 'plattenbereiche'
        ? { ...structuredClone(ds.vorgabe), kennung: neu, knoten } : { kennung: neu, knoten });
      return neu;
    },
    zeichnen: (a, g) => zeichnen(a, g, kennung),
    fangpunkte: () => (situationVon(kennung)?.umriss || []).map((p) => ({ p })),
    umriss: () => umriss(kennung),
    eigenschaften,
    neuEigenschaften,
  };
}

/** Die Zeichenfenster der Durchstanzstellen, je Kennung eines. */
const fensterVon = cadApp('ds', adapter, (a) => { a.ds = a.adapter.ds; });

/** Die Ecken der Polygone einer Liste, wie sie gerade gezeichnet sind -- mit dem Eintrag dazu. */
function polygone(a, z, liste) {
  const lagen = a.modell.lagen(z);
  return (z[liste] || []).map((e) => ({ e, punkte: e.knoten.map((k) => lagen.get(k)) }))
    .filter(({ punkte }) => punkte.length >= 2 && punkte.every(Boolean));
}

/**
 * Unten der Grundriss aus der letzten Lösung, darin die Aussparungen und
 * Plattenbereiche, wie sie gerade gezeichnet sind -- auch die, die der Kern
 * noch nicht kennt.
 */
function zeichnen(a, g, kennung) {
  const z = eintragVon(kennung);
  const aussparungen = polygone(a, z, 'aussparungen').map((x) => x.punkte);
  const bereiche = polygone(a, z, 'plattenbereiche')
    .map(({ e, punkte }) => ({ name: e.kennung, h: e.h, punkte }));
  const bild = (p) => nachBild(a.v, p);
  const s = situationVon(kennung);
  if (s) {
    const sicht = [nachWelt(a.v, [0, a.v.hoehe]), nachWelt(a.v, [a.v.breite, 0])];
    g.append(...grundrissTeile(s, bild, sicht, aussparungen, bereiche));
  } else {
    for (const b of bereiche) g.append(...bereichTeile(b, bild));
    for (const punkte of aussparungen) g.append(...aussparungTeile(punkte.map(bild)));
  }
}

/** Was «Alles zeigen» ins Bild nimmt: der Grundriss der letzten Lösung und alle Knoten. */
function umriss(kennung) {
  const s = situationVon(kennung);
  const punkte = (eintragVon(kennung)?.knoten || []).map((k) => [k.x, k.y]);
  if (s) punkte.push(...grundrissUmfang(s));
  return umrissVon(punkte, [[-1000, -1000], [1000, 1000]]);
}

// ===========================================================================
// Die Seitenleiste
// ===========================================================================

/**
 * Dicke und Seite der Stufe eines Plattenbereichs -- `wert(feld)` ist, was
 * gilt, `setzen(feld)` schreibt: in die gewählten oder in die Vorgabe für
 * den nächsten. Das Bild der Seite steht bei einer Bodenplatte auf dem Kopf:
 * dort steht die Stütze oben.
 */
function bereichFelder(a, wert, setzen) {
  const angabe = feldangabe('plattenbereich', 'h');
  const boden = eintragVon(a.ds.kennung)?.plattenart === 'bodenplatte';
  return [
    cadZeile('Dicke h', zahlfeldMitVar({
      wert: wert('h'), angabe, titel: 'Die Dicke der Platte im Bereich', beiAenderung: setzen('h'),
    }), angabe.einheit || ''),
    schalterzeile('Stufe', wahlSchalter({
      werte: mitBild(katalog('durchstanzen', 'seiten'), 'seite'), gewaehlt: wert('seite'),
      setzen: setzen('seite'), titel: 'Auf welcher Seite der Platte die Stufe liegt',
      klasse: boden ? '.ds-seite-boden' : '',
    })),
  ];
}

/** Die Felder für das, was ein Werkzeug als Nächstes anlegt: beim Bereich Dicke und Seite. */
function neuEigenschaften(a, werkzeug) {
  if (werkzeug !== 'plattenbereich') return { inhalt: [], schluessel: werkzeug };
  const v = a.ds.vorgabe;
  const { wert, setzen } = vorgabe(a, v);
  return {
    inhalt: bereichFelder(a, wert, setzen),
    schluessel: JSON.stringify([werkzeug, v, eintragVon(a.ds.kennung)?.plattenart]),
  };
}

/**
 * Die Seitenleiste zur Auswahl (cad_app.js): Ecken und Knoten mit ihrer
 * Lage, Aussparungen mit dem, was man mit ihnen tun kann, Plattenbereiche
 * mit Dicke und Seite.
 */
function eigenschaften(a) {
  return auswahlEigenschaften(a, { sonst: teilEigenschaften },
    eintragVon(a.ds.kennung)?.plattenart ?? null);
}

/** Gewählte Aussparungen oder Plattenbereiche: ihre Felder und was man mit ihnen tun kann. */
function teilEigenschaften(a, z, kennungen, liste) {
  const einzeln = kennungen.length === 1;
  const art = a.adapter.arten.find((x) => x.liste === liste);
  const bereiche = liste === 'plattenbereiche';
  const inhalt = [];
  if (bereiche) {
    const { wert, setzen } = zugleich(a, z, liste, kennungen);
    inhalt.push(...bereichFelder(a, wert, setzen));
  }
  inhalt.push(el('p.cad-hinweis-klein', {
    text: einzeln ? 'Eine Ecke verschiebt man, indem man auf sie klickt; '
      + `${bereiche ? 'den ganzen Bereich' : 'die ganze Aussparung'} mit V. Entf löscht.`
      : 'Verschieben mit V, kopieren mit C, löschen mit Entf.',
  }));
  const titel = einzeln ? teilname(a, kennungen[0]) : `${kennungen.length} ${art.mehrzahl}`;
  return { titel, inhalt };
}
