/**
 * mw_zeichnung.js -- das Zeichenfenster einer Wand aus Mauerwerk: Adapter und Seitenleiste.
 *
 * Gezeichnet wird die Wand in der Ansicht, in Metern, x nach rechts und y
 * nach oben, wie die Decke: ihr Umriss und ihre Öffnungen -- Türen und
 * Fenster. Beide sind Rechtecke, darum zeichnen ihre Werkzeuge gleich ein
 * Rechteck aus zwei Ecken; mit G geht es Ecke um Ecke, wie in jedem
 * Zeichenfenster. Alles hängt an Knoten (`verbunden`): wer die Ecke einer
 * Türe auf den Fuss der Wand setzt, verschiebt beide zusammen.
 *
 * WAS DER KERN SAGT:
 * Anfrage `mauerwerk_zeichnung`: die Meldungen und je Öffnung die Fläche
 * ihres Sturzes. Sie gelten nur, solange die Zeichnung dieselbe ist, nach
 * der gefragt wurde; bis die nächste Antwort da ist, stehen die Stürze der
 * letzten blass.
 *
 * Das Bild steht in `mw_bild.js`. Gerechnet wird hier nichts; Einheiten und
 * Grenzen der Felder sagt der Kern (`katalog.felder`).
 */

import { api } from './api.js';
import {
  mitBild, mitVar, wahlBlock, wahlSchalter,
} from './bausteine.js';
import {
  auswahlEigenschaften, cadApp, cadBereichMitListe, meldungenJe, meldungszeilen, teilname, umrissVon, vorgabe,
  zahlfeldMitVar, zugleich,
} from './cad_app.js';
import { polygonBefehl } from './cad_befehle.js';
import { cadZeile } from './cad_palette.js';
import { el } from './dom.js';
import { wand } from './mw_bild.js';
import {
  eintragVon, feldangabe, katalog, zustand,
} from './zustand.js';

/** Was die Arten heissen, je Liste -- einzeln und mehrere. */
const NAMEN = { oeffnungen: ['Öffnung', 'Öffnungen'], waende: ['Wand', 'Wände'] };

/**
 * Die Arten der Wand, ihre Vorsilben vom Kern (`VORSILBEN` in
 * opencivil/projekt/mauerwerk.py). Eine Öffnung vor der Wand: sie liegt darauf.
 */
function arten() {
  const vorsilben = katalog('mauerwerk', 'vorsilben');
  return [['oeffnungen', 'flaeche'], ['waende', 'flaeche']].map(([liste, form], rang) => ({
    liste, form, rang, vorsilbe: vorsilben[liste], heisst: NAMEN[liste][0], mehrzahl: NAMEN[liste][1],
  }));
}

/** Ein Umriss, der als Rechteck aus zwei Ecken beginnt -- G wechselt zu Ecke um Ecke (cad_befehle.js). */
const rechteckBefehl = (werkzeug) => () => ({
  ...polygonBefehl(werkzeug), rechteck: true,
  hinweis: 'Esc oder Rücktaste nimmt den letzten Punkt zurück · G wechselt zwischen Rechteck und Ecke um Ecke',
});

/** Meter und ein Raster bis 2 m, wie die Decke -- Türen und Fenster liegen meist auf 10 cm. */
const EINSTELLUNG = {
  werkzeuge: [
    { name: 'wand', text: 'Wand', zeichen: 'cad-mauer', taste: 'w', form: 'polygon', befehl: rechteckBefehl('wand'),
      titel: 'Wand – ihr Umriss in der Ansicht, ein Rechteck aus zwei Ecken' },
    { name: 'oeffnung', text: 'Öffnung', zeichen: 'cad-oeffnung', taste: 'o', form: 'polygon',
      befehl: rechteckBefehl('oeffnung'),
      titel: 'Öffnung – eine Türe oder ein Fenster, ein Rechteck aus zwei Ecken; darüber liegt ihr Sturz' },
    { name: 'knoten', text: 'Knoten', zeichen: 'cad-knoten', taste: 'k', form: 'knoten' },
  ],
  einheit: 'm',
  raster: { stufen: [0.05, 0.1, 0.25, 0.5, 1, 2], vorgabe: 0.1 },
  stellen: 3,
  massstab: [0.2, 20000],
  verbunden: true,
};

/** Welche Liste ein Werkzeug füllt -- der Knoten keine. */
const LISTE_VON = { wand: 'waende', oeffnung: 'oeffnungen' };

// ===========================================================================
// Das Fenster einer Wand
// ===========================================================================

/** Die Zeichenfenster der Wände, je Kennung eines (cad_app.js); ihr Zustand hängt als `a.mw` an. */
const fensterVon = cadApp('mw', adapter, (a) => { a.mw = a.adapter.mw; });

/** Das Zeichenfenster einer Wand, samt der Liste darunter. Die Tafel ruft das bei jedem Neubau. */
export function zeichenbereich(eintrag, listeBauen) {
  return cadBereichMitListe(fensterVon(eintrag.kennung), listeBauen);
}

/** Was die Werkzeuge als Nächstes anlegen, je Liste: die Vorlage des Kerns. */
function vorgabenNeu() {
  return {
    waende: structuredClone(katalog('vorlagen', 'wand')),
    oeffnungen: structuredClone(katalog('vorlagen', 'oeffnung')),
  };
}

/**
 * Was der Adapter einer Wand über die gemeinsame Grundlage hinaus weiss
 * (cad_app.js). Den Kern fragt er nach der Zeichnung (Anfrage
 * `mauerwerk_zeichnung`).
 */
function adapter(kennung) {
  const mw = { kennung, vorgaben: vorgabenNeu(), vorsilben: katalog('mauerwerk', 'vorsilben') };
  return {
    mw,
    einstellung: EINSTELLUNG,
    achsen: ['x', 'y'],
    arten: arten(),
    name: teilname,
    neuText: (a, werkzeug) => EINSTELLUNG.werkzeuge.find((w) => w.name === werkzeug)?.text || '',
    // Der Knoten ist er selbst -- sonst setzt kein Werkzeug einen Punkt.
    punktAnlegen: () => null,
    flaecheAnlegen,
    zeichnen,
    umriss: () => umrissVon(
      (eintragVon(kennung)?.knoten || []).map((k) => [k.x, k.y]), [[0, 0], [6, 3]]),
    fragen: () => api.mauerwerkZeichnung(zustand.projekt, kennung),
    nehmen: (_, antwort) => antwort.uebersicht,
    eigenschaften,
    neuEigenschaften,
  };
}

function flaecheAnlegen(a, z, knoten, werkzeug) {
  const liste = LISTE_VON[werkzeug];
  const kennung = a.modell.naechsteKennung(z, a.mw.vorsilben[liste]);
  z[liste].push({ ...structuredClone(a.mw.vorgaben[liste]), kennung, knoten });
  return kennung;
}

/**
 * Die Wand, darüber rot, was der Kern an einem Teil beanstandet -- mit den
 * Stürzen seiner letzten Antwort, blass, solange sie zu einer früheren
 * Zeichnung gehört.
 */
function zeichnen(a, g) {
  const z = eintragVon(a.mw.kennung);
  if (!z) return;
  const { antwort } = a.adapter.kern;
  g.append(wand(a.v, z, {
    ...meldungenJe(a), stuerze: antwort?.stuerze || [], alt: antwort?.fassung !== zustand.fassung,
    stellungen: katalog('mauerwerk'),
  }));
}

// ===========================================================================
// Die Seitenleiste
// ===========================================================================

/**
 * Ein Zahlenfeld einer Öffnung mit Beschriftung und Einheit des Kerns --
 * `wert(feld)` das Gemeinsame der gewählten, `setzen(feld)` schreibt.
 */
function feldzeile(feld, wert, setzen, titel) {
  const angabe = feldangabe('oeffnung', feld);
  return cadZeile(angabe.heisst, zahlfeldMitVar({
    wert: wert(feld), schritt: 10, angabe, titel, beiAenderung: setzen(feld),
  }), angabe.einheit || '');
}

/** Die Felder einer Öffnung, für die Vorgabe des Werkzeugs wie für gewählte: der Sturz über ihr. */
function oeffnungFelder(wert, setzen) {
  return [
    wahlBlock('Sturz', wahlSchalter({
      werte: mitVar(mitBild(katalog('mauerwerk', 'sturz'), 'sturz'), wert('sturz')),
      gewaehlt: wert('sturz'), setzen: setzen('sturz'), titel: 'Was über der Öffnung trägt',
    })),
    feldzeile('h_St', wert, setzen, 'Wie hoch der Sturz ist'),
    feldzeile('a', wert, setzen, 'Wie weit der Sturz auf jeder Seite auf dem Mauerwerk liegt'),
  ];
}

/** Die Felder für das, was ein Werkzeug als Nächstes anlegt -- nur die Öffnung hat welche. */
function neuEigenschaften(a, werkzeug) {
  if (werkzeug !== 'oeffnung') return { inhalt: [], schluessel: werkzeug };
  const v = a.mw.vorgaben.oeffnungen;
  const { wert, setzen } = vorgabe(a, v);
  return { inhalt: oeffnungFelder(wert, setzen), schluessel: JSON.stringify([werkzeug, v]) };
}

/** Was gewählt ist (cad_app.js): Knoten, Öffnungen mit ihrem Sturz -- oder der Umriss der Wand. */
function eigenschaften(a) {
  return auswahlEigenschaften(a, { oeffnungen: oeffnungEigenschaften, waende: wandEigenschaften });
}

function oeffnungEigenschaften(a, z, kennungen) {
  const { wert, setzen } = zugleich(a, z, 'oeffnungen', kennungen);
  return {
    titel: kennungen.length === 1
      ? a.adapter.name(a, kennungen[0]) : `${kennungen.length} Öffnungen`,
    inhalt: [...oeffnungFelder(wert, setzen), ...meldungszeilen(a, kennungen)],
  };
}

/** Der Umriss der Wand, ohne Felder: was sie ausmacht, steht in den Kacheln unter der Zeichnung. */
function wandEigenschaften(a, z, kennungen) {
  const meldungen = meldungszeilen(a, kennungen);
  return {
    titel: kennungen.length === 1 ? a.adapter.name(a, kennungen[0]) : `${kennungen.length} Wände`,
    inhalt: meldungen.length ? meldungen : [el('p.cad-hinweis-klein', {
      text: 'Ihre Ecken verschiebt man mit V. Mauerwerk, Dicke und Ränder stehen in den Kacheln '
        + 'unter der Zeichnung.',
    })],
  };
}
