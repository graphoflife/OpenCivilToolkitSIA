/**
 * decke.js -- Mittlere Tafel: Eingaben einer Stahlbetondecke, und was rechts von ihr steht.
 *
 * Von oben nach unten:
 *
 *     Decke       Bezeichnung, Zeichnung samt Liste, Beschreibung
 *     Eingaben    Knöpfe, je mit einem Fenster (`KAPITEL`): die Streifen --
 *                 wie breit, und wie die Last auf die zwei Richtungen geht --,
 *                 die Lastfälle und Lastkombinationen (lastfaelle.js)
 *
 * Rechts im Reiter «Diagramme» der Grundriss mit der Aufteilung und einer
 * mit den Streifen, in der Zusammenfassung die Streifen je Richtung, je Fall
 * die Last und was die Lager tragen, und die Meldungen. Gerechnet wird nach
 * der Streifenmethode, im Kern (opencivil/decke); hier stehen nur seine
 * Zahlen.
 */

import {
  erklaerung, feld, karte, klappgruppe, panel, wahlBlock, wahlSchalter,
} from './bausteine.js';
import { ansichtNeu, einpassen, zahlText } from './cad_ansicht.js';
import { umrissVon } from './cad_app.js';
import { LASTLISTEN, kernmeldungen } from './dk_eigenschaften.js';
import { anteilText, grundriss, legende } from './dk_grundriss.js';
import { waehlen, zeichenbereich } from './dk_zeichnung.js';
import {
  el, leerzustand, svgEl, zahlfeld,
} from './dom.js';
import { kapitelFenster, kapitelPanel } from './kapitel.js';
import { lastenKapitel, lastfallWaehlen } from './lastfaelle.js';
import {
  eintragAendern, eintragVon, feldangabe, katalog, zustand,
} from './zustand.js';

const HILFE = {
  decke: {
    zeilen: [
      ['Achsen', 'x nach rechts, y nach oben, in m; Dicken und Stützen in mm'],
      ['Platte', 'ein Umriss mit Dicke und Beton -- E_cm und Gewicht vom Beton, mit g = 10 m/s²; ihre Streifen tragen in Richtung 1 und 2, in Grad gegen x'],
      ['Linienlager', 'eine Wand oder ein Rand: vertikal gehalten, eingespannt oder beides -- eingespannt allein wie eine Symmetrieachse'],
      ['Stütze', 'an einem Knoten, b_x × b_y; die Streifen geben ihre Last über den Stützenbereich ab'],
      ['Unterzug', 'versteckt in der Platte, ein starker Streifen der Breite b -- er liegt auf Lagern, Stützen und Unterzügen höherer Stufe'],
      ['Zone', 'dort geht ihr Anteil der Last in Richtung 1, der Rest in Richtung 2'],
    ],
    formel: 'Streifenmethode: jede Last in Streifen zweier Richtungen, ohne Drillmomente',
  },
  streifen: {
    zeilen: [
      ['Breite', 'höchstens so breit; geteilt wird zudem an jeder Ecke, jedem Rand eines Unterzugs und Stützenbereichs und jedem Ende eines Linienlagers'],
      ['automatisch', 'je Stelle die Richtung, die Lager hat; tragen beide, nahe einem Rand (ein Viertel der kürzeren Spannweite) zu ihm, sonst in die kürzere Spannweite, in den Ecken je zur Hälfte -- Folie 31, verallgemeinert nach Vorgabe'],
      ['fest', 'überall derselbe Anteil in Richtung 1'],
      ['Zonen', 'gehen beidem vor: dort gilt ihr Anteil -- zu zeichnen im Fenster mit «Zone»'],
    ],
    formel: 'q₁ = α · q   q₂ = (1 − α) · q',
  },
};

// ===========================================================================
// Unter der Zeichnung
// ===========================================================================

/**
 * Meldungen des Kerns -- zur Decke und zum gezeigten Lastfall -- und je Teil
 * eine Zeile: ein Klick wählt im Fenster, bei einer Stütze oder Punktlast
 * ihren Knoten; bei einer Last zeigt die Zeichnung dann ihren Lastfall.
 */
function liste(a) {
  const z = eintragVon(a.dk.kennung);
  if (!z) return [];
  const teile = [];
  if (a.dk.unterlage === 'aufteilung') teile.push(legende());
  if (a.dk.daten?.fehler) teile.push(el('div.qa-meldungen', {}, [el('div.qa-meldung', { text: a.dk.daten.fehler })]));
  const knotenVon = new Map([...z.stuetzen, ...z.punktlasten].map((s) => [s.kennung, s.knoten]));
  const meldungen = kernmeldungen(a);
  if (meldungen.length) {
    teile.push(el('div.qa-meldungen', {}, meldungen.map((m) => el('button.qa-meldung', {
      type: 'button', text: m.text, class: m.fehler ? '' : 'ist-hinweis',
      title: 'Wählt die Teile, die die Meldung nennt',
      on: { click: () => waehlen(a.dk.kennung, m.elemente.map((k) => knotenVon.get(k) || k)) },
    }))));
  }
  const zeile = (kennung, links, rechts, waehlbar = kennung, lastfall = undefined) => el('div.bs-element', {
    dataset: { kennung: waehlbar },
    on: {
      click: () => {
        if (lastfall !== undefined) lastfallWaehlen(a, a.dk, lastfall);
        waehlen(a.dk.kennung, [waehlbar]);
      },
    },
  }, [el('span.bs-element-name', { text: kennung }), el('span', { text: links }),
    el('span.bs-element-zusatz', { text: rechts })]);
  const fall = (lf) => z.lastfaelle.find((x) => x.kennung === lf)?.name || 'kein Lastfall';
  const flaeche = (w) => `q = ${zahlText(w, 2)} kN/m²`;
  const beton = (k) => {
    const m = eintragVon(k);
    return m ? (m.name || m.sorte) : 'kein Beton';
  };
  const halt = (l) => [l.vertikal ? 'vertikal' : '', l.eingespannt ? 'eingespannt' : ''].filter(Boolean).join(', ')
    || 'hält nichts';
  const gruppen = [
    ['Platten', z.platten.map((p) => zeile(p.kennung, `${zahlText(p.h, 0)} mm`,
      `${beton(p.beton)} · ${p.knoten.length} Ecken · Richtungen ${zahlText(p.richtung_1, 1)}°, ${zahlText(p.richtung_2, 1)}°`))],
    ['Linienlager', z.linienlager.map((l) => zeile(l.kennung, `${l.von} → ${l.bis}`, halt(l)))],
    ['Stützen', z.stuetzen.map((s) => zeile(s.kennung, `an ${s.knoten}`,
      `${zahlText(s.b_x, 0)} × ${zahlText(s.b_y, 0)} mm${s.bereich_von_hand ? ` · Bereich ${zahlText(s.l_x, 2)} × ${zahlText(s.l_y, 2)} m` : ''}`,
      s.knoten))],
    ['Unterzüge', z.unterzuege.map((u) => zeile(u.kennung, `${u.von} → ${u.bis}`,
      `b = ${zahlText(u.breite, 2)} m · Stufe ${u.stufe}`))],
    ['Zonen', z.zonen.map((x) => zeile(x.kennung, anteilText(x.anteil), `${x.knoten.length} Ecken`))],
    ['Lasten', [
      ...z.platten.flatMap((p) => p.lasten.map((q) => zeile(p.kennung, 'ganze Platte',
        `${flaeche(q.wert)} · ${fall(q.lastfall)}`, p.kennung, q.lastfall))),
      ...z.flaechenlasten.map((f) => zeile(f.kennung, `${f.knoten.length} Ecken`,
        `${flaeche(f.wert)} · ${fall(f.lastfall)}`, f.kennung, f.lastfall)),
      ...z.linienlasten.map((l) => zeile(l.kennung, `${l.von} → ${l.bis}`,
        `q = ${zahlText(l.wert, 2)} kN/m · ${fall(l.lastfall)}`, l.kennung, l.lastfall)),
      ...z.punktlasten.map((e) => zeile(e.kennung, `an ${e.knoten}`,
        `Q = ${zahlText(e.wert, 1)} kN über ${zahlText(e.l_x, 2)} × ${zahlText(e.l_y, 2)} m · ${fall(e.lastfall)}`,
        e.knoten, e.lastfall)),
    ]],
  ];
  // Jede Gruppe klappt auf und zu, zu Beginn zu -- wie im Balkensystem.
  const offen = a.dk.aufgeklappt || (a.dk.aufgeklappt = new Set());
  for (const [titel, zeilen] of gruppen) {
    if (zeilen.length) teile.push(klappgruppe(titel, zeilen, offen, 'bs-elemente'));
  }
  return teile;
}

// ===========================================================================
// Decke
// ===========================================================================

function deckeGruppe(decke) {
  const aendern = (veraenderer) => eintragAendern(decke.kennung, veraenderer);
  return panel({
    schluessel: 'decke/Decke', titel: 'Decke', zusatz: 'x nach rechts, y nach oben, m', breit: true,
  }, [
    feld('Bezeichnung', el('input', {
      type: 'text', value: decke.name,
      on: { change: (e) => aendern((d) => { d.name = e.target.value; }) },
    }), erklaerung(HILFE.decke.zeilen, HILFE.decke.formel)),
    zeichenbereich(decke, liste),
    el('div.unterkapitel', {}, [
      el('div.beschreibung', {}, [
        el('label', { text: 'Beschreibung' }),
        el('textarea', {
          rows: 2, value: decke.beschreibung || '',
          on: { change: (e) => aendern((d) => { d.beschreibung = e.target.value; }) },
        }),
      ]),
    ]),
  ]);
}

// ===========================================================================
// Streifen
// ===========================================================================

/** Wie die Aufteilung im Schalter heisst -- vom Kern. */
const AUFTEILUNGEN = () => katalog('decke', 'aufteilungen');

/**
 * Wie breit die Streifen höchstens sind und wie die Last auf die zwei
 * Richtungen geht: automatisch oder überall derselbe Anteil -- in einer
 * Zone deren.
 */
function streifenInhalt(decke) {
  const aendern = (veraenderer) => eintragAendern(decke.kennung, veraenderer);
  return [
    feld('Streifenbreite', zahlfeld({
      wert: decke.streifenbreite, schritt: 0.05, angabe: feldangabe('decke', 'streifenbreite'),
      titel: 'So breit sind die Streifen höchstens -- schmaler, wo eine Ecke oder ein Lager sie teilt',
      beiAenderung: (w) => aendern((d) => { d.streifenbreite = w; }),
    }), feldangabe('decke', 'streifenbreite').einheit),
    wahlBlock('Aufteilung', wahlSchalter({
      werte: AUFTEILUNGEN().map((x) => ({ wert: x.wert, beschriftung: x.beschriftung, titel: x.titel })),
      gewaehlt: decke.aufteilung, titel: 'Wie die Last ausserhalb der Zonen auf die zwei Richtungen geht',
      setzen: (w) => aendern((d) => { d.aufteilung = w; }),
    })),
    decke.aufteilung === 'fest' ? feld('Anteil in Richtung 1', zahlfeld({
      wert: decke.anteil, schritt: 10, angabe: feldangabe('decke', 'anteil'),
      titel: 'Dieser Anteil der Last geht in Richtung 1, der Rest in Richtung 2',
      beiAenderung: (w) => aendern((d) => { d.anteil = w; }),
    }), feldangabe('decke', 'anteil').einheit) : null,
    el('p.karte-hinweis', { text: 'In einer Zone gilt ihr eigener Anteil -- gezeichnet im Fenster mit «Zone».' }),
  ].filter(Boolean);
}

/**
 * Die Eingaben, die nicht im Zeichenfenster stehen -- als Knöpfe, jeder mit
 * seinem Fenster, wie im Balkensystem. Unter dem Namen klein, was gilt.
 */
const KAPITEL = [
  {
    titel: 'Tragwerk',
    kapitel: [
      {
        schluessel: 'streifen', name: 'Streifen', titel: 'Streifen und Aufteilung', hilfe: HILFE.streifen,
        inhalt: streifenInhalt,
        stand: (d) => ({
          an: true,
          text: `${zahlText(d.streifenbreite, 2)} m · ${d.aufteilung === 'fest' ? anteilText(d.anteil)
            : AUFTEILUNGEN().find((x) => x.wert === d.aufteilung)?.beschriftung || d.aufteilung}`,
        }),
      },
    ],
  },
  lastenKapitel({
    lastenVon: (d, lf) => d.platten.reduce((n, p) => n + p.lasten.filter((x) => x.lastfall === lf).length, 0)
      + LASTLISTEN.reduce((n, liste) => n + d[liste].filter((x) => x.lastfall === lf).length, 0),
    eigengewicht: {
      text: 'ρ · g · h',
      titel: 'Je Platte die Dichte des Stahlbetons mal g = 10 m/s² mal ihre Dicke',
    },
  }),
];

/** Die Fenster der Decke, nach ihrem Schlüssel: die Kapitel. */
export function deckeFenster(decke, schluessel) {
  return kapitelFenster(decke, KAPITEL, schluessel);
}

export function deckeEditor(decke) {
  return [deckeGruppe(decke), kapitelPanel(decke, KAPITEL, { schluessel: 'decke/Eingaben', titel: 'Eingaben' })];
}

// ===========================================================================
// Rechts: Diagramme und Zusammenfassung
// ===========================================================================

/** So breit ist ein Grundriss auf seiner Karte, und so hoch höchstens und mindestens -- px. */
const BILD = { breite: 720, hoehe: [260, 560], rand: 24 };

/**
 * Ein Grundriss als Bild, fest im Massstab: die Decke, wie sie im Projekt
 * steht, und darunter, was die letzte Rechnung zu ihr sagt.
 */
function grundrissBild(decke, daten, was) {
  const umriss = umrissVon(decke.knoten.map((k) => [k.x, k.y]), [[0, 0], [10, 8]]);
  const [[x0, y0], [x1, y1]] = umriss;
  const breit = Math.max(x1 - x0, 1);
  const hoch = Math.max(y1 - y0, 1);
  const hoehe = Math.min(BILD.hoehe[1], Math.max(BILD.hoehe[0],
    (hoch / breit) * (BILD.breite - 2 * BILD.rand) + 2 * BILD.rand));
  const v = ansichtNeu([1e-3, 1e5]);
  Object.assign(v, { breite: BILD.breite, hoehe });
  einpassen(v, umriss, { rand: BILD.rand });
  const svg = svgEl('svg', { viewBox: `0 0 ${BILD.breite} ${hoehe.toFixed(0)}`, class: 'gb-bild dk-bild' });
  svg.append(grundriss(v, decke, daten, { was }));
  return svg;
}

/** Was die letzte Rechnung zu einer Decke zeichnet -- oder null. */
const zeichendaten = (kennung) => zustand.loesung?.zeichendaten?.[kennung] || null;

/** Die Meldungen des Kerns als Hinweise -- die der Beschreibung zuerst, wie er sie schreibt. */
function meldungszeilen(daten) {
  return (daten?.meldungen || []).map((m) => el('p', {
    class: m.fehler ? 'hinweis hinweis-warnung' : 'hinweis', text: m.text,
  }));
}

/**
 * Die Karten einer Decke im Reiter «Diagramme»: der Grundriss mit der
 * Aufteilung und einer mit den Streifen. Das Panel darum baut bericht.js.
 */
export function deckenKarten(kennung) {
  const decke = eintragVon(kennung);
  const daten = zeichendaten(kennung);
  if (!decke?.platten.length) {
    return [karte(null, [leerzustand('Noch keine Platte.', 'Zeichnen im Fenster mit «Platte».')])];
  }
  if (!daten?.gerechnet) {
    return [karte(null, [...meldungszeilen(daten), leerzustand('Noch nicht gerechnet.')])];
  }
  return [
    karte('Lastaufteilung', [
      ...meldungszeilen(daten),
      el('div.gb-bildhuelle', {}, [grundrissBild(decke, daten, 'aufteilung')]), legende(),
    ], { klasse: 'ist-breit' }),
    karte('Streifen', [
      el('div.gb-bildhuelle', {}, [grundrissBild(decke, daten, 'streifen')]),
      el('p.karte-hinweis', {
        text: 'Gestrichelt die Stützenbereiche: über sie geben die Streifen ihre Last an die Stützen ab.',
      }),
    ], { klasse: 'ist-breit' }),
  ];
}

/** Eine Tabelle der Zusammenfassung: Kopf und Zeilen, je Zelle ein Text -- Zahlen rechtsbündig. */
function tabelle(kopf, zeilen) {
  return el('div.tabelle-huelle', {}, [el('table.bs-tabelle', {}, [
    el('thead', {}, [el('tr', {}, kopf.map((t) => el('th', { text: t })))]),
    el('tbody', {}, zeilen.map((z) => el('tr', {}, z.map((t, i) => el(i ? 'td.bs-zahl' : 'td', { text: t }))))),
  ])]);
}

/**
 * Je Lastfall und Kombination die Last und was die Lager davon tragen -- die
 * Probe des Kerns --, darunter, was er zu den Fällen meldet. Was neben den
 * Platten liegt oder nicht getragen wird, nur, wo es das gibt.
 */
function faelleKarte(daten) {
  const faelle = daten.faelle || [];
  if (!faelle.length) return karte('Lasten', [leerzustand('Kein Lastfall.', 'Anlegen unter «Lastfälle».')]);
  const spalten = [['Last', 'summe'], ['Lager', 'lager'], ['neben den Platten', 'daneben'],
    ['nicht getragen', 'nicht_getragen']]
    .filter(([, feld], i) => i < 2 || faelle.some((f) => Math.abs(f[feld]) >= 5e-4));
  return karte('Lasten und Lagerkräfte', [
    tabelle(['Fall', ...spalten.map(([t]) => `${t} [kN]`)],
      faelle.map((f) => [f.name, ...spalten.map(([, feld]) => zahlText(f[feld], 1))])),
    ...faelle.flatMap((f) => f.meldungen.map((m) => el('p', {
      class: m.fehler ? 'hinweis hinweis-warnung' : 'hinweis', text: `«${f.name}»: ${m.text}`,
    }))),
    el('p.karte-hinweis', {
      text: 'Die Lager tragen die ganze Last ausser dem, was neben den Platten liegt oder auf einem Streifen, der nicht trägt.',
    }),
  ]);
}

/**
 * Die Zusammenfassung einer Decke: die Meldungen, je Richtung, wie viele
 * Feldstreifen sie hat, und je Fall Last und Lagerkraft. Das Panel darum
 * baut bericht.js.
 */
export function deckenZusammenfassung(kennung) {
  const daten = zeichendaten(kennung);
  if (!daten) return [karte(null, [leerzustand('Noch nicht gerechnet.')])];
  if (!daten.gerechnet) return [karte(null, [...meldungszeilen(daten), leerzustand('Nicht gerechnet.')])];
  // Eine schräge Richtung heisst nach ihrem Winkel -- «71.57°» --, eine eigene Spalte dafür wiederholte ihn.
  return [
    karte('Streifen', [
      ...meldungszeilen(daten),
      tabelle(['Richtung', 'Feldstreifen'], daten.richtungen.map((r) => [r.name, String(r.streifen)])),
    ]),
    faelleKarte(daten),
  ];
}

