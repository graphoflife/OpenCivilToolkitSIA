/**
 * mauerwerk.js -- Mittlere Tafel: Eingaben einer Wand aus Mauerwerk, und was rechts von ihr steht.
 *
 * Oben die Wand: Bezeichnung, Zeichnung samt Liste, Beschreibung. Darunter
 * zwei Kacheln:
 *
 *     Mauerwerk   das Material und die Dicke -- mit den üblichen Dicken
 *                 seiner Sorte als Schalter (`katalog.mauerwerk.dicken`) --,
 *                 wie die Wand über die Dicke gemauert ist und wie die
 *                 Stossfugen, je mit Bild; darunter, was der Kern zu
 *                 Mauerwerk und Dicke sagt
 *     Ränder      Kopf und Fuss gelenkig oder eingespannt, links und rechts
 *                 frei oder gehalten, je mit Bild
 *
 * Die Dicke ist eine Vorgabe der Rechnung: Feld, Zeichen und Kachel kommen
 * aus dem Kern (`katalog.vorgaben.mauerwerk`, opencivil/mauerwerk/werk.py).
 *
 * Rechts im Reiter «Diagramme» die Ansicht der Wand mit Öffnungen, Stürzen,
 * Rändern und Pfeilern; in der Zusammenfassung die Bemessungswerte, die
 * Öffnungen und die Pfeiler. Gerechnet wird im Kern (opencivil/mauerwerk);
 * hier stehen nur seine Zahlen. Lasten und Nachweise kommen mit den
 * nächsten Schritten.
 */

import {
  beschreibung, bezeichnung, eingabegruppen, erklaerung, feld, fehlendesMaterial, karte, materialliste,
  meldungshinweise, mitBild, panel, tabelle, wahlBlock, wahlSchalter,
} from './bausteine.js';
import { zahlText } from './cad_ansicht.js';
import { listengruppen, listenzeilen, meldungsliste } from './cad_app.js';
import { el, leerzustand } from './dom.js';
import { gruppenkapitel, kapitelFenster, kapitelPanel } from './kapitel.js';
import { wandBild, wandLegende } from './mw_bild.js';
import { zeichenbereich } from './mw_zeichnung.js';
import {
  eintragAendern, eintragVon, katalog, zustand,
} from './zustand.js';

const HILFE = {
  zeilen: [
    ['Achsen', 'die Wand in der Ansicht: x nach rechts, y nach oben, in m'],
    ['Wand', 'ihr Umriss, ein Rechteck aus zwei Ecken – eine schräge Krone, etwa die eines Giebels, rechnet das Werkzeug noch nicht'],
    ['Öffnung', 'eine Türe oder ein Fenster, ebenso ein Rechteck; über jeder liegt ein Sturz, so breit wie sie und auf jeder Seite um a länger'],
    ['Pfeiler', 'das Mauerwerk zwischen zwei Öffnungen und zwischen einer Öffnung und dem Ende der Wand – Öffnungen übereinander bilden zusammen eine Lücke'],
    ['Lasten', 'kommen mit den Nachweisen'],
  ],
};

/** Was die letzte Rechnung zu einer Wand zeichnet -- oder null. */
const zeichendaten = (kennung) => zustand.loesung?.zeichendaten?.[kennung] || null;

/** Die Stellungen eines Schalters der Wand, wie der Kern sie nennt: «mauerung», «halterung» … */
const stellungen = (liste) => katalog('mauerwerk', liste);

/**
 * Die Hilfe einer Kachel: `zeilen`, dann je Stellung ihrer Schalter `listen`
 * ihr Wort und was der Kern dazu sagt -- so steht jede Regel nur dort.
 */
const hilfeMit = (zeilen, listen) => () => ({
  zeilen: [...zeilen, ...listen.flatMap((liste) => stellungen(liste).map((s) => [s.beschriftung, s.titel]))],
});

const HILFE_MAUERWERK = hilfeMit([
  ['Mauerwerk', 'ein Standardmauerwerk der SIA 266 oder ein eigenes, etwa ein deklariertes – angelegt unter «Materialien»'],
  ['Dicke', 'meist so dick, wie die Steine der Sorte sind; eine andere Dicke geht auch, ein grauer Hinweis sagt es'],
], ['mauerung', 'stossfugen']);

const HILFE_RAENDER = hilfeMit([
  ['Kopf und Fuss', 'gelenkig oder eingespannt'],
  ['Links und rechts', 'frei oder gehalten – gehaltene Ränder tragen nur Querlast ab'],
], ['halterung', 'seitenrand']);

/** Das Wort einer Stellung, wie der Kern es nennt: «Verbandmauerwerk». */
const wortVon = (liste, wert) => stellungen(liste).find((s) => s.wert === wert)?.beschriftung ?? wert;

/** Das Material der Wand, wie es im Projekt steht -- oder undefined. */
const materialVon = (w) => zustand.projekt.materialien.find((m) => m.kennung === w.material && m.art === 'mauerwerk');

/** «1.00 × 2.10 m»: Breite und Höhe dessen, was gezeichnet ist -- nur fürs Auge, gerechnet wird im Kern. */
function masse(eintrag, knoten) {
  const punkte = knoten.map((k) => eintrag.knoten.find((x) => x.kennung === k)).filter(Boolean);
  if (punkte.length < 3) return '';
  const spanne = (achse) => Math.max(...punkte.map((p) => p[achse])) - Math.min(...punkte.map((p) => p[achse]));
  return `${zahlText(spanne('x'), 2)} × ${zahlText(spanne('y'), 2)} m`;
}

// ===========================================================================
// Unter der Zeichnung
// ===========================================================================

/** Meldungen des Kerns und je Teil eine Zeile (cad_app.js): ein Klick wählt im Fenster. */
function liste(a) {
  const w = eintragVon(a.mw.kennung);
  if (!w) return [];
  const zeile = listenzeilen(a);
  return [
    meldungsliste(a),
    ...listengruppen(a, [
      ['Wand', w.waende.map((u) => zeile({ kennung: u.kennung, was: masse(w, u.knoten) }))],
      ['Öffnungen', w.oeffnungen.map((o) => zeile({
        kennung: o.kennung, was: masse(w, o.knoten), wert: wortVon('sturz', o.sturz),
      }))],
    ]),
  ];
}

// ===========================================================================
// Die Wand
// ===========================================================================

function wandGruppe(w) {
  const aendern = (veraenderer) => eintragAendern(w.kennung, veraenderer);
  return panel({
    schluessel: 'mauerwerk/Wand', titel: 'Wand', zusatz: 'in der Ansicht, x nach rechts, y nach oben, m', breit: true,
  }, [
    bezeichnung(w, aendern, erklaerung(HILFE.zeilen)),
    zeichenbereich(w, liste),
    el('div.unterkapitel', {}, [beschreibung(w, aendern)]),
  ]);
}

// ===========================================================================
// Die Kacheln
// ===========================================================================

/** Ein Schalter der Wand mit den Stellungen des Kerns, je mit Bild `liste-wert` (sinnbilder_mauerwerk.js). */
function schalter(w, feldname, liste, titel) {
  return wahlSchalter({
    werte: mitBild(stellungen(liste), liste), gewaehlt: w[feldname], titel,
    setzen: (wert) => eintragAendern(w.kennung, (x) => { x[feldname] = wert; }),
  });
}

/**
 * Die üblichen Dicken der Sorte des Mauerwerks als Schalter -- eine andere
 * Zahl im Feld darüber geht auch, dann ist keine Stellung an. Ohne
 * Mauerwerk keine.
 */
function dickenWahl(w) {
  const sorte = materialVon(w)?.sorte;
  const dicken = sorte ? katalog('mauerwerk', 'dicken')[sorte] : null;
  if (!dicken?.length) return null;
  return wahlBlock(`Übliche Dicken, ${sorte}`, wahlSchalter({
    werte: dicken.map((d) => ({ wert: d, beschriftung: String(d), titel: `t_w = ${d} mm` })),
    gewaehlt: w.t, titel: `So dick sind die Steine der Sorte ${sorte} meist, in mm`,
    setzen: (d) => eintragAendern(w.kennung, (x) => { x.t = d; }),
  }));
}

/** Die Kachel «Ränder»: wie die Wand an ihren vier Rändern gehalten ist. */
function raenderKapitel(w) {
  return {
    schluessel: 'mw-raender', name: 'Ränder', titel: 'Ränder', hilfe: HILFE_RAENDER,
    inhalt: () => [karte('', [
      wahlBlock('Kopf', schalter(w, 'kopf', 'halterung', 'Wie die Wand oben gehalten ist')),
      wahlBlock('Fuss', schalter(w, 'fuss', 'halterung', 'Wie die Wand unten gehalten ist')),
      wahlBlock('Links', schalter(w, 'links', 'seitenrand', 'Ob eine Querwand den linken Rand hält')),
      wahlBlock('Rechts', schalter(w, 'rechts', 'seitenrand', 'Ob eine Querwand den rechten Rand hält')),
      el('p.karte-hinweis', {
        text: 'Gehaltene Ränder links und rechts tragen nur Querlast ab, über ein waagrechtes Gewölbe.',
      }),
    ])],
    stand: () => ({
      an: true,
      text: `Kopf ${wortVon('halterung', w.kopf)}, Fuss ${wortVon('halterung', w.fuss)}; `
        + `links ${wortVon('seitenrand', w.links)}, rechts ${wortVon('seitenrand', w.rechts)}`,
    }),
  };
}

/**
 * Die Kacheln: «Mauerwerk» aus der Gruppe der Vorgaben des Kerns, mit
 * Material und Schaltern um die Dicke herum, und «Ränder».
 */
function kapitel(w) {
  const aendern = (veraenderer) => eintragAendern(w.kennung, veraenderer);
  const vorgaben = eingabegruppen('mauerwerk', w, aendern);
  const daten = zeichendaten(w.kennung);
  const material = materialVon(w);
  const kacheln = [
    gruppenkapitel(vorgaben, 'Mauerwerk', {
      zeichen: 'mw-wand', hilfe: HILFE_MAUERWERK, werte: ['t'], wort: material ? material.name || material.sorte : '',
      vor: [feld('Mauerwerk', materialliste({
        art: 'mauerwerk', gewaehlt: w.material, titel: 'Woraus die Wand gemauert ist',
        setzen: (k) => aendern((x) => { x.material = k; }),
      }), '')],
      nach: [
        dickenWahl(w),
        ...meldungshinweise(daten?.zum_mauerwerk),
        wahlBlock('Gemauert', schalter(w, 'mauerung', 'mauerung', 'Wie die Wand über ihre Dicke gemauert ist')),
        wahlBlock('Stossfugen', schalter(w, 'stossfugen', 'stossfugen', 'Ob auch die Stossfugen ganz mit Mörtel gefüllt sind')),
      ],
      fehlt: fehlendesMaterial('mauerwerk', w.material),
    }),
    raenderKapitel(w),
  ];
  vorgaben.vollstaendig();
  return [{ titel: '', kapitel: kacheln.filter(Boolean) }];
}

export function mauerwerkEditor(w) {
  return [wandGruppe(w), kapitelPanel(w, kapitel(w), { schluessel: 'mauerwerk/Eingaben', titel: 'Eingaben' })];
}

/** Das offene Fenster einer Wand -- oder null. */
export function mauerwerkFenster(w, schluessel) {
  return kapitelFenster(w, kapitel(w), schluessel);
}

// ===========================================================================
// Rechts: Diagramme und Zusammenfassung
// ===========================================================================

/** Eine frische Wand, in Diagrammen und Zusammenfassung gleich. */
function ohneWand() {
  return karte(null, [leerzustand('Noch keine Wand.', 'Zeichnen im Fenster mit «Wand».')]);
}

/**
 * Die Karte einer Wand im Reiter «Diagramme»: die Ansicht mit Öffnungen,
 * Stürzen, Rändern und den Massen der Pfeiler -- darüber, was der Kern
 * meldet. Das Panel darum baut bericht.js.
 */
export function mauerwerkKarten(kennung) {
  const w = eintragVon(kennung);
  if (!w?.waende.length) return [ohneWand()];
  const daten = zeichendaten(kennung);
  const bild = wandBild(w, daten, katalog('mauerwerk'));
  return [karte('Ansicht', [
    ...meldungshinweise(daten?.meldungen), el('div.gb-bildhuelle', {}, [bild]), wandLegende(katalog('mauerwerk')),
  ], { bild, klasse: 'ist-breit' })];
}

/** Die Bemessungswerte des Mauerwerks und die der Wand -- im Verband mit dem Faktor. */
function werteKarte(werte) {
  const verband = werte.faktor !== 1;
  return karte('Bemessungswerte', [
    tabelle(['', `${werte.mauerwerk} [N/mm²]`, 'Wand [N/mm²]'], werte.zeilen.map((z) => [
      z.zeichen, zahlText(z.mauerwerk, z.stellen), zahlText(z.wand, z.stellen)])),
    el('p.karte-hinweis', {
      text: verband ? `Im Verband gelten die Werte des Mauerwerks mal ${zahlText(werte.faktor, 2)} – μ_d ohne Einheit und ohne Faktor.`
        : 'μ_d ohne Einheit.',
    }),
  ]);
}

/** Die Öffnungen, wie sie gezeichnet sind, mit dem Sturz über jeder. */
function oeffnungenKarte(w) {
  return karte('Öffnungen', [tabelle(['Öffnung', 'b × h', 'Sturz', 'h_St [mm]', 'a [mm]'],
    w.oeffnungen.map((o) => [o.kennung, masse(w, o.knoten), wortVon('sturz', o.sturz), zahlText(o.h_St, 0),
      zahlText(o.a, 0)]))]);
}

/** Die Pfeiler, wie der Kern sie bestimmt: wo sie stehen und wie breit sie sind. */
function pfeilerKarte(pfeiler) {
  return karte('Pfeiler', [tabelle(['Pfeiler', 'links – rechts [m]', 'b [m]'],
    pfeiler.map((e) => [e.name, `${zahlText(e.x0, 2)} – ${zahlText(e.x1, 2)}`, zahlText(e.b, 2)]))]);
}

/**
 * Die Zusammenfassung einer Wand: was der Kern meldet, die Bemessungswerte,
 * die Öffnungen und die Pfeiler. Das Panel darum baut bericht.js.
 */
export function mauerwerkZusammenfassung(kennung) {
  const w = eintragVon(kennung);
  const daten = zeichendaten(kennung);
  if (!w?.waende.length) return [ohneWand()];
  if (!daten) return [karte(null, [leerzustand('Noch nicht gerechnet.')])];
  const meldungen = meldungshinweise(daten.meldungen);
  return [
    meldungen.length ? karte('Wand', meldungen) : null,
    daten.werte ? werteKarte(daten.werte) : null,
    w.oeffnungen.length ? oeffnungenKarte(w) : null,
    daten.pfeiler.length ? pfeilerKarte(daten.pfeiler) : null,
  ].filter(Boolean);
}
