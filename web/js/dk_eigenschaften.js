/**
 * dk_eigenschaften.js -- die Seitenleiste im Zeichenfenster einer Decke.
 *
 * Was ein Werkzeug als Nächstes anlegt (`neuEigenschaften`) und was gewählt
 * ist (`eigenschaften`): je Knoten -- mit seiner Stütze und Punktlast --,
 * Platte -- mit der Last auf ihr --, Linienlager, Träger, Zone oder Last
 * seine Felder; ein Schnitt hat keine, nur wo sein Bild zu holen ist. Sind mehrere derselben Art gewählt, ändert das Fenster alle
 * zugleich; was sie gemeinsam haben, steht da, sonst «Var» -- wie im
 * Balkensystem. Eine Stütze und eine Punktlast wählt man nicht für sich:
 * sie stehen im Fenster ihres Knotens, wie ein Lager im Balkensystem -- die
 * Punktlast wie in der Wand (`punktlastFelder` in lastfaelle.js). Die
 * Lasten gelten dem Lastfall, den das Fenster zeigt (lastfaelle.js). Was
 * nur die Streifenmethode liest -- die Richtungen einer Platte, die Stufe
 * eines Trägers, der Stützenbereich --, steht nur, wenn die Decke nach ihr
 * rechnet.
 *
 * Vom Zeichenfenster kennt es nur `a`: was die Werkzeuge vorgeben
 * (`a.dk.vorgaben`) und das Modell. Was jedes Fenster mit Zeichnung gleich
 * hat -- die Antwort des Kerns, die Auswahl nach Listen, Felder für mehrere,
 * die Lage der Knoten, die Meldungen --, steht in cad_app.js. Einheiten und
 * Grenzen der Felder sagt der Kern (`katalog.felder`). Gerechnet wird hier
 * nichts.
 */

import {
  VAR, gemeinsam, materialliste, mitVar, wahlBlock, wahlSchalter,
} from './bausteine.js';
import { zahlText } from './cad_ansicht.js';
import {
  auswahlEigenschaften, frischeAntwort, jaNein, laengenzeile, lagefelder, meldungszeilen, vorgabe, zahlfeldMitVar,
  zugleich,
} from './cad_app.js';
import { cadZeile, schalterzeile } from './cad_palette.js';
import { el } from './dom.js';
import {
  aktiverLastfall, gezeigterLastfall, lastfallText, lastfallWaehlen, lastfallZeile, punktlastFelder,
} from './lastfaelle.js';
import { eintragVon, feldangabe, materialien } from './zustand.js';

/**
 * Was der Kern in seiner Antwort meldet (cad_app.js): zur Decke, und zum
 * Lastfall, den das Fenster zeigt -- mit dessen Namen davor.
 */
export function deckenmeldungen(a, antwort) {
  const lf = gezeigterLastfall(a.dk);
  const fall = lf && (antwort.faelle || []).find((f) => f.name === lf.name);
  return [...antwort.meldungen, ...(fall?.meldungen || []).map((m) => ({ ...m, text: `«${lf.name}»: ${m.text}` }))];
}

/**
 * Der Beton, den eine neue Platte bekommt: der gewählte, sonst der erste des
 * Projekts. Bis 2026-11-19 blieb ein gelöschter Beton gewählt, und jede neue
 * Platte verwies ins Leere.
 */
export function vorgabeBeton(a) {
  const betone = materialien('beton');
  const gewaehlt = a.dk.vorgaben.platten.beton;
  return betone.some((m) => m.kennung === gewaehlt) ? gewaehlt : betone[0]?.kennung || '';
}

/**
 * Ein Zahlenfeld mit Beschriftung und der Einheit des Kerns. `klasse` ist
 * der Name der Einträge im Katalog (`deckenplatte`), `wert(feld)` das
 * Gemeinsame der gewählten, `setzen(feld)` schreibt. `neben` hält die
 * Zahlen der Felder, gegen die dieses prüft (`grenzeVerletzt` in dom.js).
 */
function feldzeile(klasse, feld, beschriftung, wert, setzen, { schritt = 1, titel, neben } = {}) {
  const angabe = feldangabe(klasse, feld);
  return cadZeile(beschriftung, zahlfeldMitVar({
    wert: wert(feld), schritt, angabe, titel, neben, beiAenderung: setzen(feld),
  }), angabe.einheit || '');
}

/**
 * Die Richtungen der Rechnung, je gewählte Platte (`von_selbst` ihrer
 * Antwort, in Grad) -- null, solange sie nicht da sind. Ohne Platte,
 * für die nächste, die das Werkzeug zeichnet: gar keine.
 */
function richtungenVonSelbst(a, platten) {
  const von = frischeAntwort(a)?.von_selbst || {};
  return platten.map((p) => von[p.kennung] || null);
}

/** Was die Rechnung als Richtungen wählt, unter dem Schalter «automatisch». */
function gewaehlteRichtungen(richtungen) {
  const hinweis = (text) => el('p.cad-hinweis-klein', { text });
  if (!richtungen) return hinweis('Die Rechnung legt sie entlang der Ränder der Platte.');
  if (richtungen.includes(null)) {
    return hinweis('Entlang der Ränder – die Richtungen stehen da, sobald die Decke rechnet.');
  }
  const gemeinsame = gemeinsam(richtungen.map((r) => JSON.stringify(r)));
  if (gemeinsame === VAR) return hinweis('Je Platte entlang ihrer Ränder – sie unterscheiden sich.');
  const [r1, r2] = JSON.parse(gemeinsame);
  return hinweis(`Entlang der Ränder: Richtung 1 ${zahlText(r1, 1)}°, Richtung 2 ${zahlText(r2, 1)}°.`);
}

/**
 * Die Felder je Art -- für die Vorgabe eines Werkzeugs wie für gewählte
 * Teile; `wert` und `setzen` wie bei `feldzeile`, `streifen`, ob die Decke
 * nach der Streifenmethode rechnet.
 */
const FELDER = {
  // `richtungen`: was die Rechnung je gewählte Platte als Richtungen wählt (`richtungenVonSelbst`).
  platten: (wert, setzen, { streifen, richtungen = null }) => {
    const vonHand = wert('richtungen_von_hand');
    const stoff = feldzeile('deckenplatte', 'h', 'Dicke h', wert, setzen, { schritt: 10 });
    const beton = cadZeile('Beton', materialliste({
      art: 'beton', gewaehlt: wert('beton'), setzen: setzen('beton'),
      titel: streifen ? 'E_cm und das Gewicht der Platte kommen von ihm'
        : 'E_cm, ν_c und das Gewicht der Platte kommen von ihm',
    }));
    if (!streifen) return [stoff, beton];
    const neben = { richtung_1: wert('richtung_1'), richtung_2: wert('richtung_2') };
    return [
      stoff,
      beton,
      wahlBlock('Richtungen', wahlSchalter({
        werte: mitVar([
          {
            wert: false, beschriftung: 'automatisch',
            titel: 'Entlang der Ränder – Platten, die aneinanderstossen, gleich, damit die Streifen über die Fuge laufen',
          },
          { wert: true, beschriftung: 'von Hand', titel: 'Richtung 1 und 2 in Grad gegen x' },
        ], vonHand),
        gewaehlt: vonHand, setzen: setzen('richtungen_von_hand'),
        titel: 'In diesen zwei Richtungen tragen die Streifen der Platte',
      })),
      ...(vonHand === true ? [
        feldzeile('deckenplatte', 'richtung_1', 'Richtung 1', wert, setzen, {
          schritt: 15, neben, titel: 'In diese Richtung tragen die Streifen der Richtung 1 – in Grad gegen x',
        }),
        feldzeile('deckenplatte', 'richtung_2', 'Richtung 2', wert, setzen, {
          schritt: 15, neben, titel: 'Die zweite Richtung der Streifen – in Grad gegen x, mindestens 5° neben der ersten',
        }),
      ] : []),
      ...(vonHand === false ? [gewaehlteRichtungen(richtungen)] : []),
    ];
  },
  linienlager: (wert, setzen) => [
    schalterzeile('vertikal', jaNein(wert('vertikal'), setzen('vertikal'),
      'Hält die Platte in der Höhe – eine Wand, ein Träger')),
    schalterzeile('eingespannt', jaNein(wert('eingespannt'), setzen('eingespannt'),
      'Hält die Drehung – ohne vertikalen Halt wie an einer Symmetrieachse')),
  ],
  traeger: (wert, setzen, { streifen }) => [
    feldzeile('traeger', 'breite', 'Breite b', wert, setzen, {
      schritt: 0.1, titel: streifen ? 'So breit trägt der Träger als Streifen in der Platte'
        : 'So breit ist der Träger: so breit zählen Balken und Platte zu seinem M und V',
    }),
    feldzeile('traeger', 'h_T', 'Höhe h_T', wert, setzen, {
      schritt: 50, titel: 'So weit reicht der Träger über oder unter die Platte – 0: er steckt in ihr. '
        + 'Sein Steg wiegt mit; in der FEM ist er ein Balken in der Platte',
    }),
    streifen ? feldzeile('traeger', 'stufe', 'Stufe', wert, setzen, {
      titel: 'Ein Träger liegt auf denen höherer Stufe, die ihn kreuzen',
    }) : null,
    el('p.cad-hinweis-klein', {
      text: 'Sein M und V: unter «Ergebnisse» mit «+ Diagramm», dann statt «ganze Platte» den Träger wählen.',
    }),
  ].filter(Boolean),
  zonen: (wert, setzen) => [
    feldzeile('zone', 'anteil', 'Richtung 1', wert, setzen, {
      schritt: 10, titel: 'Dieser Anteil der Last geht in Richtung 1 der Platte, der Rest in Richtung 2',
    }),
  ],
  flaechenlasten: (wert, setzen) => [
    feldzeile('flaechenlast', 'wert', 'q', wert, setzen, { schritt: 0.5, titel: 'Nach unten positiv' }),
  ],
  linienlasten: (wert, setzen) => [
    feldzeile('linienlast', 'wert', 'q', wert, setzen, { schritt: 1, titel: 'Je Meter Linie, nach unten positiv' }),
  ],
  punktlasten: (wert, setzen) => [
    feldzeile('punktlast', 'wert', 'Q', wert, setzen, { schritt: 5, titel: 'Nach unten positiv' }),
    feldzeile('punktlast', 'l_x', 'l_x', wert, setzen, {
      schritt: 0.1, titel: 'Über l_x × l_y verteilt trägt die Platte die Last',
    }),
    feldzeile('punktlast', 'l_y', 'l_y', wert, setzen, { schritt: 0.1 }),
  ],
  schnitte: () => [el('p.cad-hinweis-klein', {
    text: 'Sein Bild: unter «Ergebnisse» mit «+ Diagramm», dann statt «ganze Platte» den Schnitt wählen.',
  })],
  stuetzen: (wert, setzen, { streifen }) => {
    const vonHand = wert('bereich_von_hand');
    const masse = [feldzeile('stuetze', 'b_x', 'b_x', wert, setzen, { schritt: 50 }),
      feldzeile('stuetze', 'b_y', 'b_y', wert, setzen, { schritt: 50 })];
    if (!streifen) {
      return [...masse, el('p.cad-hinweis-klein', {
        text: 'In der FEM hält die Stütze die Platte als Punkt – b_x und b_y rechnen nicht mit.',
      })];
    }
    return [
      ...masse,
      wahlBlock('Stützenbereich', wahlSchalter({
        werte: mitVar([
          { wert: false, beschriftung: 'von selbst', titel: 'So gross wie die Stütze oder der breiteste Träger über ihr' },
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
  platte: 'platten', lager: 'linienlager', stuetze: 'stuetzen', traeger: 'traeger', zone: 'zonen',
  flaechenlast: 'flaechenlasten', linienlast: 'linienlasten', punktlast: 'punktlasten', schnitt: 'schnitte',
};

/** Die Listen der gezeichneten Lasten -- jede in einem Lastfall. */
export const LASTLISTEN = ['flaechenlasten', 'linienlasten', 'punktlasten'];

/**
 * Was ausser der Auswahl die Felder ändert: am Lastfall, welcher gezeigt
 * ist, wie er heisst, ob es einen gibt -- und das Verfahren der Decke.
 */
function felderStand(a) {
  const z = eintragVon(a.dk.kennung);
  return [aktiverLastfall(a.dk), gezeigterLastfall(a.dk)?.name ?? null, Boolean(z?.lastfaelle.length),
    z?.verfahren ?? null];
}

/** Ob die Decke des Fensters nach der Streifenmethode rechnet -- dann zählen auch ihre eigenen Felder. */
const nachStreifen = (a) => eintragVon(a.dk.kennung)?.verfahren !== 'fem';

/** Die Felder für das, was ein Werkzeug als Nächstes anlegt. */
export function neuEigenschaften(a, werkzeug) {
  const liste = LISTE_VON[werkzeug];
  if (!liste) return { inhalt: [], schluessel: werkzeug };
  const v = a.dk.vorgaben[liste];
  const { setzen } = vorgabe(a, v);
  const wert = (feld) => (feld === 'beton' ? vorgabeBeton(a) : v[feld]);
  return {
    inhalt: [...(LASTLISTEN.includes(liste) ? [lastfallText(a.dk)] : []),
      ...FELDER[liste](wert, setzen, { streifen: nachStreifen(a) })],
    schluessel: JSON.stringify([werkzeug, v, vorgabeBeton(a), felderStand(a)]),
  };
}

/** Was gewählt ist (cad_app.js): Knoten oder Teile einer Liste -- neu auch, wenn der gezeigte Lastfall wechselt. */
export function eigenschaften(a) {
  return auswahlEigenschaften(a, { knoten: knotenEigenschaften, sonst: teilEigenschaften }, felderStand(a));
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
  const kennungen = stuetzen.map((s) => s.kennung);
  const { wert, setzen } = zugleich(a, z, 'stuetzen', kennungen);
  return [...zeilen, ...FELDER.stuetzen(wert, setzen, { streifen: nachStreifen(a) }), ...meldungszeilen(a, kennungen)];
}

/** Gewählte Knoten: ihre Lage (cad_app.js), ihre Stütze und ihre Punktlast im gezeigten Lastfall. */
function knotenEigenschaften(a, z, knoten) {
  return {
    titel: knoten.length === 1 ? `Knoten ${knoten[0]}` : `${knoten.length} Knoten`,
    inhalt: [
      ...lagefelder(a, z, knoten),
      ...stuetzeFelder(a, z, knoten),
      ...punktlastFelder(a, a.dk, z, knoten, (wert, setzen) => FELDER.punktlasten(wert, setzen, {})),
      ...meldungszeilen(a, knoten),
    ],
  };
}

// -- Platten, Linienlager, Träger, Zonen, Lasten ---------------------------

/**
 * Die Last auf den ganzen gewählten Platten im gezeigten Lastfall -- leer
 * heisst keine. Je Platte und Lastfall eine, wie im Kern.
 */
function plattenlastFelder(a, platten) {
  const lf = gezeigterLastfall(a.dk);
  if (!lf) return [lastfallText(a.dk)];
  const kennungen = platten.map((p) => p.kennung);
  const angabe = feldangabe('plattenlast', 'wert');
  const setzen = (w) => a.aendern((zz) => {
    for (const p of zz.platten) {
      if (!kennungen.includes(p.kennung)) continue;
      p.lasten = p.lasten.filter((x) => x.lastfall !== lf.kennung);
      if (w !== null) p.lasten.push({ lastfall: lf.kennung, wert: w });
    }
  });
  return [lastfallText(a.dk), cadZeile('q überall', zahlfeldMitVar({
    wert: gemeinsam(platten.map((p) => p.lasten.find((x) => x.lastfall === lf.kennung)?.wert ?? null)),
    schritt: 0.5, angabe, leer: null, platzhalter: 'keine', beiAenderung: setzen,
    titel: `Flächenlast auf der ganzen Platte im Lastfall «${lf.name}», nach unten positiv – leer: keine`,
  }), angabe.einheit)];
}

/**
 * Wer eine Platte auf «von Hand» stellt, beginnt mit den Richtungen, die
 * die Rechnung gewählt hatte -- so ändert der Schalter allein nichts.
 */
function vonHandAb(a) {
  const von = frischeAntwort(a)?.von_selbst || {};
  return (e, feld) => {
    if (feld === 'richtungen_von_hand' && e.richtungen_von_hand && von[e.kennung]) {
      [e.richtung_1, e.richtung_2] = von[e.kennung];
    }
  };
}

function teilEigenschaften(a, z, kennungen, liste) {
  const platten = liste === 'platten';
  const { gewaehlt, wert, setzen } = zugleich(a, z, liste, kennungen, platten ? vonHandAb(a) : undefined);
  // Ändert man den Lastfall einer Last, zeigt das Fenster danach dessen Lasten -- sonst verschwände sie.
  const inhalt = [
    ...(LASTLISTEN.includes(liste) ? [lastfallZeile(z, wert('lastfall'), (w) => {
      setzen('lastfall')(w);
      lastfallWaehlen(a, a.dk, w);
    }, 'Zu welchem Lastfall die Lasten gehören')] : []),
    ...FELDER[liste](wert, setzen, {
      streifen: nachStreifen(a), richtungen: platten ? richtungenVonSelbst(a, gewaehlt) : null,
    }),
    ...(platten ? plattenlastFelder(a, gewaehlt) : []),
  ];
  const art = a.adapter.arten.find((x) => x.liste === liste);
  if (gewaehlt.length === 1 && art.form === 'linie') inhalt.push(laengenzeile(a, z, gewaehlt[0]));
  inhalt.push(...meldungszeilen(a, kennungen));
  return {
    titel: gewaehlt.length === 1 ? a.adapter.name(a, gewaehlt[0].kennung) : `${gewaehlt.length} ${art.mehrzahl}`,
    inhalt: inhalt.filter(Boolean),
  };
}
