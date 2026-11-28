/**
 * mauerwerk.js -- Mittlere Tafel: Eingaben einer Wand aus Mauerwerk, und was rechts von ihr steht.
 *
 * Oben die Wand: Bezeichnung, Zeichnung samt Liste, Beschreibung. Darunter
 * die Kacheln:
 *
 *     Mauerwerk     das Material und die Dicke -- mit den üblichen Dicken
 *                   seiner Sorte als Schalter (`katalog.mauerwerk.dicken`) --,
 *                   wie die Wand über die Dicke gemauert ist und wie die
 *                   Stossfugen, je mit Bild; darunter, was der Kern zu
 *                   Mauerwerk und Dicke sagt
 *     Ränder        Kopf und Fuss gelenkig oder eingespannt -- ein gelenkiger
 *                   Fuss mit der Ausmitte e_u --, links und rechts frei oder
 *                   gehalten, je mit Bild
 *     Lastfälle,    wie in Balkensystem und Decke (lastfaelle.js); die Lasten
 *     Kombinationen zeichnet man im Zeichenfenster
 *     Querlasten    zwischen beiden: was quer zur Wand wirkt, von Hand oder aus
 *                   dem Erdbeben (mw_querlasten.js) -- man zeichnet sie nicht
 *
 * Dicke und Ausmitte sind Vorgaben der Rechnung: Felder, Zeichen und
 * Kacheln kommen aus dem Kern (`katalog.vorgaben.mauerwerk`,
 * opencivil/mauerwerk/werk.py).
 *
 * Rechts im Reiter «Diagramme» die Ansicht der Wand mit Öffnungen, Stürzen,
 * Rändern, Pfeilern und ihren Urteilen; die Zusammenfassung ist die jedes
 * Bauteils mit Nachweisen, mit Angaben und Bemessungswerten der Wand
 * darüber (opencivil/mauerwerk/uebersicht.py). Gerechnet wird im Kern
 * (opencivil/mauerwerk); hier stehen nur seine Zahlen.
 */

import {
  beschreibung, bezeichnung, eingabegruppen, erklaerung, feld, fehlendesMaterial, karte, materialliste,
  meldungshinweise, mitBild, panel, wahlBlock, wahlSchalter,
} from './bausteine.js';
import { zahlText } from './cad_ansicht.js';
import { listengruppen, listenzeilen, meldungsliste } from './cad_app.js';
import { el, leerzustand } from './dom.js';
import { gruppenkapitel, kapitelFenster, kapitelPanel } from './kapitel.js';
import { lastenKapitel, lastfallWaehlen } from './lastfaelle.js';
import { wandBild, wandLegende } from './mw_bild.js';
import { QUERLASTEN } from './mw_querlasten.js';
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
    ['Linienlast', 'waagrecht von Punkt zu Punkt, etwa eine Decke; mit ihrer Ausmitte e quer zur Wand'],
    ['Punktlast', 'an einem Knoten, etwa ein Träger; ebenso mit Ausmitte'],
    ['Querlast', 'quer zur Wand über ihre ganze Ansicht, angelegt unter «Querlasten» – im Bild Kreise auf der Wand: mit Punkt, wo sie zum Betrachter drückt, mit Kreuz, wo von ihm weg, beides im Wechsel beim Erdbeben; ihre Werte stehen unter der Wand'],
    ['Lastfall', 'die Lasten gehören zu dem, der in der Leiste über der Zeichnung gewählt ist – wie sie zu den Pfeilern kommen, sagt die Herleitung'],
    ['Farben', 'jeder Pfeiler und jedes Sturzauflager in der Farbe seines Urteils, mit dem Erfüllungsgrad der ungünstigsten Kombination'],
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
  ['e_u', 'nur bei gelenkigem Fuss: so weit neben der Mitte der Wand steht die Normalkraft an ihm'],
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

/**
 * Meldungen des Kerns und je Teil eine Zeile (cad_app.js): ein Klick wählt
 * im Fenster -- eine Last zeigt es dazu in ihrem Lastfall.
 */
function liste(a) {
  const w = eintragVon(a.mw.kennung);
  if (!w) return [];
  const zeile = listenzeilen(a);
  const fall = (lf) => w.lastfaelle.find((x) => x.kennung === lf)?.name || 'kein Lastfall';
  const last = (e, was, wert) => zeile({
    kennung: e.kennung, was, wert: `${wert} · ${fall(e.lastfall)}`, vorher: () => lastfallWaehlen(a, a.mw, e.lastfall),
  });
  const ausmitte = (e) => (e.e ? `, e = ${zahlText(e.e, 0)} mm` : '');
  return [
    meldungsliste(a),
    ...listengruppen(a, [
      ['Wand', w.waende.map((u) => zeile({ kennung: u.kennung, was: masse(w, u.knoten) }))],
      ['Öffnungen', w.oeffnungen.map((o) => zeile({
        kennung: o.kennung, was: masse(w, o.knoten), wert: wortVon('sturz', o.sturz),
      }))],
      ['Lasten', [
        ...w.linienlasten.map((e) => last(e, `${e.von} → ${e.bis}`, `q = ${zahlText(e.wert, 1)} kN/m${ausmitte(e)}`)),
        ...w.punktlasten.map((e) => last(e, `an ${e.knoten}`, `Q = ${zahlText(e.wert, 1)} kN${ausmitte(e)}`)),
      ]],
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

/**
 * Die Kachel «Ränder» aus der Gruppe der Vorgaben des Kerns: wie die Wand an
 * ihren vier Rändern gehalten ist -- die Ausmitte am Fuss steht gleich unter
 * seinem Schalter, wo er gelenkig ist.
 */
function raenderKapitel(w, vorgaben) {
  return gruppenkapitel(vorgaben, 'Ränder', {
    zeichen: 'mw-raender', hilfe: HILFE_RAENDER, werte: ['e_u'],
    wort: `Kopf ${wortVon('halterung', w.kopf)}, Fuss ${wortVon('halterung', w.fuss)}; `
      + `links ${wortVon('seitenrand', w.links)}, rechts ${wortVon('seitenrand', w.rechts)}`,
    vor: [
      wahlBlock('Kopf', schalter(w, 'kopf', 'halterung', 'Wie die Wand oben gehalten ist')),
      wahlBlock('Fuss', schalter(w, 'fuss', 'halterung', 'Wie die Wand unten gehalten ist')),
    ],
    nach: [
      wahlBlock('Links', schalter(w, 'links', 'seitenrand', 'Ob eine Querwand den linken Rand hält')),
      wahlBlock('Rechts', schalter(w, 'rechts', 'seitenrand', 'Ob eine Querwand den rechten Rand hält')),
      el('p.karte-hinweis', {
        text: 'Gehaltene Ränder links und rechts tragen nur Querlast ab, über ein waagrechtes Gewölbe.',
      }),
    ],
  });
}

/**
 * Die Kacheln: «Mauerwerk» und «Ränder» aus den Gruppen der Vorgaben des
 * Kerns, mit Material und Schaltern um ihre Felder herum, dann Lastfälle,
 * Querlasten und Kombinationen.
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
    raenderKapitel(w, vorgaben),
  ];
  vorgaben.vollstaendig();
  return [{ titel: '', kapitel: kacheln.filter(Boolean) }, lastenKapitel({
    lastenVon: (x, lf) => [...x.linienlasten, ...x.punktlasten, ...x.querlasten].filter((e) => e.lastfall === lf).length,
    eigengewicht: { text: 'ρ · g · t_w', titel: 'Die Dichte des Mauerwerks mal g = 10 m/s² mal die Dicke der Wand, je m² Ansicht' },
    dazu: [QUERLASTEN],
  })];
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

/** Eine frische Wand, in den Diagrammen. */
function ohneWand() {
  return karte(null, [leerzustand('Noch keine Wand.', 'Zeichnen im Fenster mit «Wand».')]);
}

/**
 * Die Karte einer Wand im Reiter «Diagramme»: die Ansicht mit Öffnungen,
 * Stürzen, Rändern, den Massen der Pfeiler und den Urteilen -- darüber, was
 * der Kern meldet. Das Panel darum baut bericht.js.
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
