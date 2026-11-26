/**
 * decke.js -- Mittlere Tafel: Eingaben einer Stahlbetondecke, und was rechts von ihr steht.
 *
 * Von oben nach unten:
 *
 *     Decke       Bezeichnung, Zeichnung samt Liste, Beschreibung
 *     Eingaben    Knöpfe, je mit einem Fenster (`KAPITEL`): die Streifen --
 *                 wie breit, und wie die Last auf die zwei Richtungen geht --,
 *                 die Lastfälle und Lastkombinationen (lastfaelle.js), und
 *                 welche Ergebnisbilder rechts stehen -- über die ganze
 *                 Platte oder längs eines Schnitts
 *
 * Rechts im Reiter «Diagramme» der Grundriss mit der Aufteilung und einer
 * mit den Streifen, darunter je Zeile der Ergebnisse ein Bild der
 * Schnittkräfte oder Lager (dk_ergebnis.js); in der Zusammenfassung die
 * Streifen je Richtung, je Fall die Last und was die Lager tragen -- auch
 * je Lager --, und die Meldungen. Gerechnet wird nach der Streifenmethode,
 * im Kern (opencivil/decke); hier stehen nur seine Zahlen.
 */

import {
  beschreibung, bezeichnung, erklaerung, feld, karte, klappgruppe, panel, tabelle, wahlBlock,
  wahlSchalter,
} from './bausteine.js';
import { zahlText } from './cad_ansicht.js';
import { listengruppen, listenzeilen, meldungsliste } from './cad_app.js';
import { LASTLISTEN } from './dk_eigenschaften.js';
import { ergebnisKarten } from './dk_ergebnis.js';
import { anteilText, grundrissBild, legende } from './dk_grundriss.js';
import { zeichenbereich } from './dk_zeichnung.js';
import {
  auswahl, el, leerzustand, zahlfeld,
} from './dom.js';
import { kapitelFenster, kapitelPanel, zeilenstand } from './kapitel.js';
import { diagrammzeilen, lastenKapitel, lastfallWaehlen } from './lastfaelle.js';
import {
  eintragAendern, eintragVon, feldangabe, katalog, zustand,
} from './zustand.js';

const HILFE = {
  decke: {
    zeilen: [
      ['Achsen', 'x nach rechts, y nach oben, in m; Dicken und Stützen in mm'],
      ['Platte', 'ein Umriss mit Dicke und Beton – E_cm und Gewicht vom Beton, mit g = 10 m/s²; ihre Streifen tragen in Richtung 1 und 2, in Grad gegen x'],
      ['Linienlager', 'eine Wand oder ein Rand: vertikal gehalten, eingespannt oder beides – eingespannt allein wie eine Symmetrieachse'],
      ['Stütze', 'an einem Knoten, b_x × b_y; die Streifen geben ihre Last über den Stützenbereich ab'],
      ['Unterzug', 'versteckt in der Platte, ein starker Streifen der Breite b – er liegt auf Lagern, Stützen und Unterzügen höherer Stufe. Sein M und V unter «Ergebnisse»'],
      ['Zone', 'dort geht ihr Anteil der Last in Richtung 1, der Rest in Richtung 2'],
      ['Schnitt', 'eine Linie, längs der ein Ergebnisbild die Schnittkraft wie an einem Balken zeigt – er rechnet nicht mit'],
    ],
    formel: 'Streifenmethode: jede Last in Streifen zweier Richtungen; die Streifen tragen ohne Drillmoment, schiefe Richtungen geben in x, y ein m_xy',
  },
  streifen: {
    zeilen: [
      ['Breite', 'höchstens so breit; geteilt wird zudem an jeder Ecke, jedem Rand eines Unterzugs und Stützenbereichs und jedem Ende eines Linienlagers'],
      ['automatisch', 'je Stelle die Richtung, die Lager hat – trägt keine, fällt die Last dort aus; tragen beide, nahe einem Rand (ein Viertel der kürzeren Spannweite) zu ihm, in den Ecken je zur Hälfte, sonst mehr in die kürzere Spannweite – je ungleicher die Spannweiten, desto mehr; Folie 31, verallgemeinert nach Vorgabe'],
      ['fest', 'überall derselbe Anteil in Richtung 1'],
      ['Zonen', 'gehen beidem vor: dort gilt ihr Anteil – zu zeichnen im Fenster mit «Zone»'],
    ],
    formel: 'q₁ = α · q   q₂ = (1 − α) · q',
  },
  ergebnisse: {
    zeilen: [
      ['Fall', 'ein Lastfall oder eine Kombination – gerechnet wird jeder Fall'],
      ['Wo', 'über die ganze Platte, längs eines Schnitts oder in einem Unterzug – längs wie an einem Balken, positive Werte unten, die Stelle s ab seinem Anfang. Ein Schnitt zeigt die Lager, die er kreuzt, und die Unterzüge als Band'],
      ['M, V', 'Moment und Querkraft eines Unterzugs über seine ganze Breite, in kNm und kN – wie er als Träger gerechnet ist, auf seinen Lagern'],
      ['m_x, m_y', 'die Momente je Meter in x und y, positiv mit Zug unten – bei schiefen Streifen aus m_η umgerechnet'],
      ['m_xy', 'das Drillmoment je Meter: nur, wo ein Streifen schief zu x und y trägt'],
      ['v_x, v_y, v_0', 'die Querkräfte je Meter und die Hauptquerkraft v_0 = √(v_x² + v_y²)'],
      ['Lager', 'je Linienlager der Verlauf seiner Kraft über die Länge; darunter je Lager die Summe, eingespannt auch sein Moment, negativ, wo es oben zieht'],
      ['Farben', 'in jeder Zelle ein Verlauf – längs eines Streifens glatt, quer springen die Werte an den Grenzen der Streifen, weil jeder seinen Teil der Last trägt'],
      ['Angeschrieben', 'der grösste und der kleinste Wert, mit Punkt an seiner Stelle; über einer Zelle der Wert in ihrer Mitte'],
    ],
  },
};

// ===========================================================================
// Unter der Zeichnung
// ===========================================================================

/**
 * Meldungen des Kerns -- zur Decke und zum gezeigten Lastfall -- und je Teil
 * eine Zeile (cad_app.js): ein Klick wählt im Fenster, eine Stütze oder
 * Punktlast über ihren Knoten; bei einer Last zeigt die Zeichnung dann
 * ihren Lastfall.
 */
function liste(a) {
  const z = eintragVon(a.dk.kennung);
  if (!z) return [];
  const zeile = (kennung, was, wert, lastfall = undefined) => listenzeilen(a)({
    kennung, was, wert, vorher: lastfall === undefined ? undefined : () => lastfallWaehlen(a, a.dk, lastfall),
  });
  const fall = (lf) => z.lastfaelle.find((x) => x.kennung === lf)?.name || 'kein Lastfall';
  const flaeche = (w) => `q = ${zahlText(w, 2)} kN/m²`;
  const beton = (k) => {
    const m = eintragVon(k);
    return m ? (m.name || m.sorte) : 'kein Beton';
  };
  // Von selbst die Richtungen der letzten Antwort -- auch einer alten, wie das Bild darunter.
  const vonSelbst = a.adapter.kern.antwort?.von_selbst || {};
  const richtungen = (p) => {
    const [r1, r2] = p.richtungen_von_hand ? [p.richtung_1, p.richtung_2] : vonSelbst[p.kennung] || [];
    const winkel = r1 === undefined ? '' : ` ${zahlText(r1, 1)}°, ${zahlText(r2, 1)}°`;
    return `Richtungen${winkel}${p.richtungen_von_hand ? ' von Hand' : ' automatisch'}`;
  };
  const halt = (l) => [l.vertikal ? 'vertikal' : '', l.eingespannt ? 'eingespannt' : ''].filter(Boolean).join(', ')
    || 'hält nichts';
  const gruppen = [
    ['Platten', z.platten.map((p) => zeile(p.kennung, `${zahlText(p.h, 0)} mm`,
      `${beton(p.beton)} · ${p.knoten.length} Ecken · ${richtungen(p)}`))],
    ['Linienlager', z.linienlager.map((l) => zeile(l.kennung, `${l.von} → ${l.bis}`, halt(l)))],
    ['Stützen', z.stuetzen.map((s) => zeile(s.kennung, `an ${s.knoten}`,
      `${zahlText(s.b_x, 0)} × ${zahlText(s.b_y, 0)} mm${s.bereich_von_hand ? ` · Bereich ${zahlText(s.l_x, 2)} × ${zahlText(s.l_y, 2)} m` : ''}`))],
    ['Unterzüge', z.unterzuege.map((u) => zeile(u.kennung, `${u.von} → ${u.bis}`,
      `b = ${zahlText(u.breite, 2)} m · Stufe ${u.stufe}`))],
    ['Zonen', z.zonen.map((x) => zeile(x.kennung, anteilText(x.anteil), `${x.knoten.length} Ecken`))],
    ['Lasten', [
      ...z.platten.flatMap((p) => p.lasten.map((q) => zeile(p.kennung, 'ganze Platte',
        `${flaeche(q.wert)} · ${fall(q.lastfall)}`, q.lastfall))),
      ...z.flaechenlasten.map((f) => zeile(f.kennung, `${f.knoten.length} Ecken`,
        `${flaeche(f.wert)} · ${fall(f.lastfall)}`, f.lastfall)),
      ...z.linienlasten.map((l) => zeile(l.kennung, `${l.von} → ${l.bis}`,
        `q = ${zahlText(l.wert, 2)} kN/m · ${fall(l.lastfall)}`, l.lastfall)),
      ...z.punktlasten.map((e) => zeile(e.kennung, `an ${e.knoten}`,
        `Q = ${zahlText(e.wert, 1)} kN über ${zahlText(e.l_x, 2)} × ${zahlText(e.l_y, 2)} m · ${fall(e.lastfall)}`,
        e.lastfall)),
    ]],
  ];
  return [
    a.dk.unterlage === 'aufteilung' ? legende(a.adapter.kern.antwort) : null,
    meldungsliste(a),
    ...listengruppen(a, gruppen),
  ];
}

// ===========================================================================
// Decke
// ===========================================================================

function deckeGruppe(decke) {
  const aendern = (veraenderer) => eintragAendern(decke.kennung, veraenderer);
  return panel({
    schluessel: 'decke/Decke', titel: 'Decke', zusatz: 'x nach rechts, y nach oben, m', breit: true,
  }, [
    bezeichnung(decke, aendern, erklaerung(HILFE.decke.zeilen, HILFE.decke.formel)),
    zeichenbereich(decke, liste),
    el('div.unterkapitel', {}, [beschreibung(decke, aendern)]),
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
      titel: 'So breit sind die Streifen höchstens – schmaler, wo eine Ecke oder ein Lager sie teilt',
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
    el('p.karte-hinweis', { text: 'In einer Zone gilt ihr eigener Anteil – gezeichnet im Fenster mit «Zone».' }),
  ].filter(Boolean);
}

/** Ob die Zeile das Bild eines Unterzugs zeigt -- dann gelten M und V statt der Grössen der Platte. */
const imUnterzug = (decke, zeile) => decke.unterzuege.some((u) => u.kennung === zeile.schnitt);

/** Die Grössen, die eine Zeile zeigen kann: die eines Unterzugs oder die der Platte. */
const groessenDer = (decke, zeile) => katalog('decke', 'diagrammgroessen')
  .filter((g) => g.unterzug === imUnterzug(decke, zeile));

/**
 * Wo ein Ergebnisbild hinsieht: über die ganze Platte, längs eines Schnitts
 * oder in einem Unterzug -- eine Wahl aus dem Projekt, darum eine Liste.
 * Nur, wenn es Schnitte oder Unterzüge gibt; die Lagerkräfte zeigen immer
 * die ganze Decke. Was es nicht mehr gibt, steht als «– gelöscht, neu wählen –» da. Wer
 * zwischen Platte und Unterzug wechselt, bekommt dort die erste Grösse:
 * m_x hat ein Unterzug nicht, M die Platte nicht.
 */
function ortWahl(decke, zeile, aendern) {
  if (zeile.groesse === 'lager' || !(decke.schnitte.length || decke.unterzuege.length || zeile.schnitt)) return null;
  const werte = [{ wert: '', beschriftung: 'ganze Platte' },
    ...decke.schnitte.map((s) => ({ wert: s.kennung, beschriftung: `längs Schnitt ${s.kennung}` })),
    ...decke.unterzuege.map((u) => ({ wert: u.kennung, beschriftung: `Unterzug ${u.kennung}` }))];
  return auswahl({
    werte: werte.some((x) => x.wert === zeile.schnitt) ? werte
      : [{ wert: zeile.schnitt, beschriftung: '– gelöscht, neu wählen –' }, ...werte],
    gewaehlt: zeile.schnitt,
    titel: 'Über die ganze Platte, längs eines Schnitts – zu zeichnen im Fenster mit «Schnitt» – '
      + 'oder in einem Unterzug: M und V über seine ganze Breite',
    beiAenderung: (w) => aendern((z) => {
      z.schnitt = w;
      const moeglich = groessenDer(decke, z);
      if (!moeglich.some((g) => g.wert === z.groesse)) z.groesse = moeglich[0].wert;
    }),
  });
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
  {
    titel: 'Analyse',
    kapitel: [
      {
        schluessel: 'ergebnisse', name: 'Ergebnisse', titel: 'Ergebnisse', hilfe: HILFE.ergebnisse,
        inhalt: (d) => diagrammzeilen(d, {
          groessen: (zeile) => groessenDer(d, zeile), vorlage: 'deckendiagramm',
          zusatz: (zeile, aendern) => ortWahl(d, zeile, aendern),
        }),
        stand: (d) => zeilenstand(d.diagramme, 'Diagramm', 'Diagramme', 'kein Diagramm'),
      },
    ],
  },
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

/** Was die letzte Rechnung zu einer Decke zeichnet -- oder null. */
const zeichendaten = (kennung) => zustand.loesung?.zeichendaten?.[kennung] || null;

/** Die Meldungen des Kerns als Hinweise -- die der Beschreibung zuerst, wie er sie schreibt. */
function meldungszeilen(daten) {
  return (daten?.meldungen || []).map((m) => el('p', {
    class: m.fehler ? 'hinweis hinweis-warnung' : 'hinweis', text: m.text,
  }));
}

/**
 * Eine frische Decke, in Diagrammen und Zusammenfassung gleich. Die
 * Zusammenfassung sagte bis 2026-11-19 «Nicht gerechnet.» unter einem
 * roten Fehler.
 */
function ohnePlatte() {
  return karte(null, [leerzustand('Noch keine Platte.', 'Zeichnen im Fenster mit «Platte».')]);
}

/**
 * Die Karten einer Decke im Reiter «Diagramme»: der Grundriss mit der
 * Aufteilung, einer mit den Streifen und die Ergebnisbilder. Das Panel
 * darum baut bericht.js.
 */
export function deckenKarten(kennung) {
  const decke = eintragVon(kennung);
  const daten = zeichendaten(kennung);
  if (!decke?.platten.length) return [ohnePlatte()];
  if (!daten?.gerechnet) {
    return [karte(null, [...meldungszeilen(daten), leerzustand('Noch nicht gerechnet.')])];
  }
  const aufteilung = grundrissBild(decke, daten, 'aufteilung');
  const streifen = grundrissBild(decke, daten, 'streifen');
  return [
    karte('Lastaufteilung', [
      ...meldungszeilen(daten),
      el('div.gb-bildhuelle', {}, [aufteilung]), legende(daten),
    ], { bild: aufteilung, klasse: 'ist-breit' }),
    karte('Streifen', [
      el('div.gb-bildhuelle', {}, [streifen]),
      el('p.karte-hinweis', {
        text: 'Gestrichelt die Stützenbereiche: über sie geben die Streifen ihre Last an die Stützen ab.',
      }),
    ], { bild: streifen, klasse: 'ist-breit' }),
    ...ergebnisKarten(kennung, decke, daten),
  ];
}

/** Welche zugeklappten Meldungen offen sind -- Ansichtssache, nicht Teil des Projekts. */
const MELDUNGEN_OFFEN = new Set();

/**
 * Was der Kern zu den Fällen meldet, jede Meldung einmal, vorn ihre Fälle
 * (`fallmeldungen`). Mehr als drei klappen zusammen, mit ihrer Anzahl --
 * offen, solange eine davon ein Fehler ist (Benutzer, 2026-11-20).
 */
function fallmeldungen(daten) {
  const meldungen = daten.fallmeldungen || [];
  const zeilen = meldungen.map((m) => el('p', {
    class: m.fehler ? 'hinweis hinweis-warnung' : 'hinweis', text: m.text,
  }));
  if (zeilen.length <= 3) return zeilen;
  const titel = 'Meldungen zu den Fällen';
  if (meldungen.some((m) => m.fehler)) MELDUNGEN_OFFEN.add(titel);
  return [klappgruppe(titel, zeilen, MELDUNGEN_OFFEN, 'meldungsgruppe')];
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
    ...fallmeldungen(daten),
    el('p.karte-hinweis', {
      text: 'Die Lager tragen die ganze Last ausser dem, was neben den Platten liegt oder auf einem Streifen, der nicht trägt.',
    }),
  ]);
}

/**
 * Je Lager, was es in jedem Fall trägt: jede Stütze ihre Kraft, jedes
 * Linienlager die Summe über seine Länge -- in kN.
 */
function lagerKarte(daten) {
  const faelle = daten.faelle || [];
  const lager = faelle[0]?.je_lager || [];
  if (!lager.length) return null;
  return karte('Lagerkräfte', [
    tabelle(['Lager', ...faelle.map((f) => `${f.name} [kN]`)], lager.map((l, i) => [
      `${l.name} · ${l.art === 'stuetze' ? 'Stütze' : 'Linienlager'}`,
      ...faelle.map((f) => zahlText(f.je_lager[i].F, 1)),
    ])),
    el('p.karte-hinweis', { text: 'Den Verlauf längs eines Linienlagers zeigt das Bild «Lager» unter «Diagramme».' }),
  ]);
}

/**
 * Die Zusammenfassung einer Decke: die Meldungen, je Richtung, wie viele
 * Feldstreifen sie hat, je Fall Last und Lagerkraft und je Lager, was es
 * trägt. Das Panel darum baut bericht.js.
 */
export function deckenZusammenfassung(kennung) {
  const daten = zeichendaten(kennung);
  if (!eintragVon(kennung)?.platten.length) return [ohnePlatte()];
  if (!daten) return [karte(null, [leerzustand('Noch nicht gerechnet.')])];
  if (!daten.gerechnet) return [karte(null, [...meldungszeilen(daten), leerzustand('Nicht gerechnet.')])];
  // Eine schräge Richtung heisst nach ihrem Winkel -- «71.57°» --, eine eigene Spalte dafür wiederholte ihn.
  return [
    karte('Streifen', [
      ...meldungszeilen(daten),
      tabelle(['Richtung', 'Feldstreifen'], daten.richtungen.map((r) => [r.name, String(r.streifen)])),
    ]),
    faelleKarte(daten),
    lagerKarte(daten),
  ].filter(Boolean);
}

