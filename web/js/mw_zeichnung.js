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
 * LASTEN:
 * Linien- und Punktlasten zeichnen die Werkzeuge in den Lastfall, der in der
 * Leiste gewählt ist (lastfaelle.js), wie in der Decke: das Fenster zeigt nur
 * dessen Lasten, und nur sie lassen sich wählen. Eine Linienlast liegt von
 * Knoten zu Knoten -- eine schräge meldet der Kern --, eine Punktlast steht
 * an ihrem Knoten und in dessen Fenster.
 *
 * WAS DER KERN SAGT:
 * Anfrage `mauerwerk_zeichnung`: die Meldungen, je Öffnung die Fläche ihres
 * Sturzes, die Pfeiler und je Pfeiler und Sturzauflager das Urteil, das an
 * ihm gilt. Sie gelten nur, solange die Zeichnung dieselbe ist, nach der
 * gefragt wurde; bis die nächste Antwort da ist, steht die letzte blass.
 *
 * Das Bild steht in `mw_bild.js`. Gerechnet wird hier nichts; Einheiten und
 * Grenzen der Felder sagt der Kern (`katalog.felder`).
 */

import { api } from './api.js';
import {
  mitBild, mitVar, wahlBlock, wahlSchalter,
} from './bausteine.js';
import {
  auswahlEigenschaften, cadApp, cadBereichMitListe, laengenzeile, lagefelder, meldungenJe, meldungszeilen,
  teilname, umrissVon, vorgabe, zahlfeldMitVar, zugleich,
} from './cad_app.js';
import { polygonBefehl } from './cad_befehle.js';
import { cadZeile } from './cad_palette.js';
import { el } from './dom.js';
import {
  aktiverLastfall, gezeigterLastfall, lastfallFuerNeue, lastfallLeiste, lastfallText, lastfallWaehlen,
  lastfallZeile, punktlastFelder, punktlastSetzen,
} from './lastfaelle.js';
import { PFEIL, wand } from './mw_bild.js';
import {
  eintragVon, feldangabe, katalog, zustand,
} from './zustand.js';

/** Was die Arten heissen, je Liste -- einzeln und mehrere. */
const NAMEN = {
  punktlasten: ['Punktlast', 'Punktlasten'],
  linienlasten: ['Linienlast', 'Linienlasten'],
  oeffnungen: ['Öffnung', 'Öffnungen'],
  waende: ['Wand', 'Wände'],
};

/** Je Liste der Lasten der Name ihrer Einträge im Katalog und das Zeichen ihres Werts. */
const LASTEN = { linienlasten: ['wandlinienlast', 'q'], punktlasten: ['wandpunktlast', 'Q'] };

/**
 * Die Arten der Wand, ihre Vorsilben vom Kern (`VORSILBEN` in
 * opencivil/projekt/mauerwerk.py). Eine Last vor dem, worauf sie liegt, und
 * eine Öffnung vor der Wand. Eine Punktlast wählt man an ihrem Knoten
 * (`waehlbar`), wie in der Decke.
 */
function arten() {
  const vorsilben = katalog('mauerwerk', 'vorsilben');
  return [['punktlasten', 'punkt'], ['linienlasten', 'linie'], ['oeffnungen', 'flaeche'], ['waende', 'flaeche']]
    .map(([liste, form], rang) => ({
      liste, form, rang, vorsilbe: vorsilben[liste], heisst: NAMEN[liste][0], mehrzahl: NAMEN[liste][1],
    }));
}

/** Eine Last braucht einen Lastfall -- ohne einen startet ihr Werkzeug nicht und sagt, wo er zu wählen ist. */
const lastBereit = (a) => Boolean(lastfallFuerNeue(a.mw));

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
    { name: 'linienlast', text: 'Linienlast', zeichen: 'cad-linienlast', taste: 'l', form: 'linie', bereit: lastBereit,
      titel: 'Linienlast – waagrecht von Punkt zu Punkt, im gewählten Lastfall, etwa eine Decke auf der Wand' },
    { name: 'punktlast', text: 'Punktlast', zeichen: 'cad-punktlast', taste: 'e', form: 'knoten', bereit: lastBereit,
      titel: 'Punktlast – an einen Knoten oder eine freie Stelle, im gewählten Lastfall, etwa ein Träger' },
    { name: 'knoten', text: 'Knoten', zeichen: 'cad-knoten', taste: 'k', form: 'knoten' },
  ],
  einheit: 'm',
  raster: { stufen: [0.05, 0.1, 0.25, 0.5, 1, 2], vorgabe: 0.1 },
  stellen: 3,
  massstab: [0.2, 20000],
  verbunden: true,
};

/** Welche Liste ein Werkzeug füllt -- der Knoten keine. */
const LISTE_VON = {
  wand: 'waende', oeffnung: 'oeffnungen', linienlast: 'linienlasten', punktlast: 'punktlasten',
};

// ===========================================================================
// Das Fenster einer Wand
// ===========================================================================

/** Die Zeichenfenster der Wände, je Kennung eines (cad_app.js); ihr Zustand hängt als `a.mw` an. */
const fensterVon = cadApp('mw', adapter, (a) => { a.mw = a.adapter.mw; });

/** Das Zeichenfenster einer Wand, samt der Liste darunter. Die Tafel ruft das bei jedem Neubau. */
export function zeichenbereich(eintrag, listeBauen) {
  const a = fensterVon(eintrag.kennung);
  const bereich = cadBereichMitListe(a, listeBauen);
  lastfallLeiste(a, a.mw, a.mw.lastfallHuelle);
  return bereich;
}

/** Was die Werkzeuge als Nächstes anlegen, je Liste: die Vorlage des Kerns. */
function vorgabenNeu() {
  const vorlage = (klasse) => structuredClone(katalog('vorlagen', klasse));
  return {
    waende: vorlage('wand'),
    oeffnungen: vorlage('oeffnung'),
    linienlasten: vorlage(LASTEN.linienlasten[0]),
    punktlasten: vorlage(LASTEN.punktlasten[0]),
  };
}

/**
 * Was der Adapter einer Wand über die gemeinsame Grundlage hinaus weiss
 * (cad_app.js). Den Kern fragt er nach der Zeichnung (Anfrage
 * `mauerwerk_zeichnung`).
 */
function adapter(kennung) {
  const mw = {
    kennung, vorgaben: vorgabenNeu(), vorsilben: katalog('mauerwerk', 'vorsilben'), lastfall: null,
    lastfallHuelle: null,
  };
  return {
    mw,
    einstellung: EINSTELLUNG,
    achsen: ['x', 'y'],
    arten: arten(),
    // Der Lastfall gleich neben den Werkzeugen, wie in der Decke.
    leisteZusatz: () => {
      mw.lastfallHuelle = el('span.bs-lastfallwahl');
      return mw.lastfallHuelle;
    },
    name: teilname,
    neuText: (a, werkzeug) => EINSTELLUNG.werkzeuge.find((w) => w.name === werkzeug)?.text || '',
    punktAnlegen,
    linieAnlegen,
    flaecheAnlegen,
    zeichnen,
    // Eine Last nur in dem Lastfall, den das Fenster zeigt; eine Punktlast an ihrem Knoten.
    waehlbar: (art, e) => art.liste !== 'punktlasten' && (!LASTEN[art.liste] || e.lastfall === aktiverLastfall(mw)),
    // Eine Linienlast trifft auch ein Klick auf ihre Pfeile, nicht nur auf die Linie darunter.
    trefferradius: (a, art) => (art.liste === 'linienlasten' ? PFEIL.linie / a.v.massstab : 0),
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
 * Eine Punktlast an den Knoten, im gezeigten Lastfall -- gewählt bleibt der
 * Knoten, sein Fenster zeigt sie. Ist keiner mehr gewählt, seit das Werkzeug
 * lief, bleibt es beim Knoten.
 */
function punktAnlegen(a, z, knoten, werkzeug) {
  const lf = werkzeug === 'punktlast' && lastfallFuerNeue(a.mw);
  if (lf) punktlastSetzen(a, a.mw, z, knoten, true, lf);
  return null;
}

/** Eine Linienlast im gezeigten Lastfall -- ohne einen keine. */
function linieAnlegen(a, z, von, bis) {
  const lastfall = lastfallFuerNeue(a.mw);
  if (!lastfall) return null;
  const kennung = a.modell.naechsteKennung(z, a.mw.vorsilben.linienlasten);
  z.linienlasten.push({ ...structuredClone(a.mw.vorgaben.linienlasten), kennung, von, bis, lastfall });
  return kennung;
}

/**
 * Die Wand, darüber rot, was der Kern an einem Teil beanstandet, und die
 * Lasten des gezeigten Lastfalls -- mit Stürzen, Pfeilern und Urteilen der
 * letzten Antwort, blass, solange sie zu einer früheren Zeichnung gehört.
 */
function zeichnen(a, g) {
  const z = eintragVon(a.mw.kennung);
  if (!z) return;
  const { antwort } = a.adapter.kern;
  g.append(wand(a.v, z, {
    ...meldungenJe(a), stuerze: antwort?.stuerze || [], pfeiler: antwort?.pfeiler || [],
    urteile: antwort?.urteile || {}, alt: antwort?.fassung !== zustand.fassung,
    stellungen: katalog('mauerwerk'), lastfall: aktiverLastfall(a.mw),
  }));
}

// ===========================================================================
// Die Seitenleiste
// ===========================================================================

/**
 * Ein Zahlenfeld mit Beschriftung und Einheit des Kerns -- `klasse` ist der
 * Name der Einträge im Katalog (`oeffnung`), `wert(feld)` das Gemeinsame der
 * gewählten, `setzen(feld)` schreibt. Ohne `beschriftung` die des Kerns.
 */
function feldzeile(klasse, feld, wert, setzen, { beschriftung, schritt = 10, titel } = {}) {
  const angabe = feldangabe(klasse, feld);
  return cadZeile(beschriftung ?? angabe.heisst, zahlfeldMitVar({
    wert: wert(feld), schritt, angabe, titel, beiAenderung: setzen(feld),
  }), angabe.einheit || '');
}

/** Die Felder einer Öffnung, für die Vorgabe des Werkzeugs wie für gewählte: der Sturz über ihr. */
function oeffnungFelder(wert, setzen) {
  return [
    wahlBlock('Sturz', wahlSchalter({
      werte: mitVar(mitBild(katalog('mauerwerk', 'sturz'), 'sturz'), wert('sturz')),
      gewaehlt: wert('sturz'), setzen: setzen('sturz'), titel: 'Was über der Öffnung trägt',
    })),
    feldzeile('oeffnung', 'h_St', wert, setzen, { titel: 'Wie hoch der Sturz ist' }),
    feldzeile('oeffnung', 'a', wert, setzen, { titel: 'Wie weit der Sturz auf jeder Seite auf dem Mauerwerk liegt' }),
  ];
}

/** Die Felder einer Last der Liste `liste`: ihr Wert nach unten und ihre Ausmitte quer zur Wand. */
function lastFelder(liste, wert, setzen) {
  const [klasse, zeichen] = LASTEN[liste];
  return [
    feldzeile(klasse, 'wert', wert, setzen, {
      beschriftung: zeichen, schritt: 5,
      titel: liste === 'linienlasten' ? 'Je Meter Linie, nach unten positiv' : 'Nach unten positiv',
    }),
    feldzeile(klasse, 'e', wert, setzen, {
      beschriftung: 'e', schritt: 5,
      titel: 'Ausmitte quer zur Wand, positiv zur Seite, von der aus man die Ansicht sieht – sie wirkt am Kopf '
        + 'der Pfeiler, die die Last tragen',
    }),
  ];
}

/**
 * Was ausser der Auswahl die Felder ändert: welcher Lastfall gezeigt ist,
 * wie er heisst und ob es einen gibt.
 */
function felderStand(a) {
  return [aktiverLastfall(a.mw), gezeigterLastfall(a.mw)?.name ?? null,
    Boolean(eintragVon(a.mw.kennung)?.lastfaelle.length)];
}

/** Die Felder für das, was ein Werkzeug als Nächstes anlegt: eine Öffnung oder eine Last. */
function neuEigenschaften(a, werkzeug) {
  const liste = LISTE_VON[werkzeug];
  if (liste !== 'oeffnungen' && !LASTEN[liste]) return { inhalt: [], schluessel: werkzeug };
  const v = a.mw.vorgaben[liste];
  const { wert, setzen } = vorgabe(a, v);
  return {
    inhalt: LASTEN[liste] ? [lastfallText(a.mw), ...lastFelder(liste, wert, setzen)] : oeffnungFelder(wert, setzen),
    schluessel: JSON.stringify([werkzeug, v, felderStand(a)]),
  };
}

/**
 * Was gewählt ist (cad_app.js): Knoten mit ihrer Punktlast, Öffnungen mit
 * ihrem Sturz, Linienlasten -- oder der Umriss der Wand. Neu auch, wenn der
 * gezeigte Lastfall wechselt.
 */
function eigenschaften(a) {
  return auswahlEigenschaften(a, {
    knoten: knotenEigenschaften, oeffnungen: oeffnungEigenschaften, linienlasten: linienlastEigenschaften,
    waende: wandEigenschaften,
  }, felderStand(a));
}

/** Gewählte Knoten: ihre Lage und ihre Punktlast im gezeigten Lastfall. */
function knotenEigenschaften(a, z, knoten) {
  return {
    titel: knoten.length === 1 ? a.adapter.name(a, knoten[0]) : `${knoten.length} Knoten`,
    inhalt: [
      ...lagefelder(a, z, knoten),
      ...punktlastFelder(a, a.mw, z, knoten,
        (wert, setzen) => lastFelder('punktlasten', wert, setzen)),
      ...meldungszeilen(a, knoten),
    ],
  };
}

/** Gewählte Linienlasten: ihr Lastfall, q und e -- bei einer auch, wie lang sie ist. */
function linienlastEigenschaften(a, z, kennungen) {
  const { gewaehlt, wert, setzen } = zugleich(a, z, 'linienlasten', kennungen);
  return {
    titel: kennungen.length === 1 ? a.adapter.name(a, kennungen[0])
      : `${kennungen.length} Linienlasten`,
    inhalt: [
      // Ändert man den Lastfall, zeigt das Fenster danach dessen Lasten -- sonst verschwände sie.
      lastfallZeile(z, wert('lastfall'), (w) => {
        setzen('lastfall')(w);
        lastfallWaehlen(a, a.mw, w);
      }, 'Zu welchem Lastfall die Lasten gehören'),
      ...lastFelder('linienlasten', wert, setzen),
      gewaehlt.length === 1 ? laengenzeile(a, z, gewaehlt[0]) : null,
      ...meldungszeilen(a, kennungen),
    ].filter(Boolean),
  };
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
