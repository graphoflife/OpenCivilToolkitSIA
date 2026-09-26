/**
 * nachweise.js -- die untere Hälfte der Plattentafel: was nachgewiesen wird.
 *
 * Vier Kapitel in der Reihenfolge, in der auch der Bericht sie führt:
 * Tragsicherheit (samt Knicken), Duktilität, sprödes Versagen und die
 * Rissbreitenbegrenzung. Dazu das Werkzeug, das die Bewehrung sucht.
 *
 * Eigenes Modul, weil `editor.js` sonst über tausend Zeilen läge und die
 * beiden Hälften wenig miteinander zu tun haben: oben steht, was die Platte
 * *ist* -- Abmessungen, Material, Lagen --, hier steht, was von ihr
 * *verlangt* wird. Geteilt wird nur der Schalter und die Feldzeile, und die
 * stehen in `bausteine.js`.
 *
 * Gerechnet wird hier nichts. Jede Zeile beschreibt eine Eingabe; die Zahlen
 * dazu bildet der Kern, sobald der Nachweis läuft.
 */

import { api } from './api.js';
import {
  DURCHMESSER, erklaerung, feld, hakenSchalter, richtungVon, richtungsWahl,
} from './bausteine.js';
import { auswahl, el, melden, zahlfeld } from './dom.js';
import { aendern, naechsterName, projektAendern, zustand } from './zustand.js';

/**
 * Welche Platte gerade durchsucht wird.
 *
 * Nur das: der Knopf soll währenddessen «sucht …» heissen und nicht zweimal
 * auslösen. Das Ergebnis steht danach in den Lagen und in der
 * Zusammenfassung -- dort sieht man, ob es aufgeht. Ein Satz daneben, grün
 * oder rot, sagte dasselbe ein zweites Mal und blieb stehen, bis man etwas
 * anderes tat.
 *
 * Ausserhalb des Projekts: das ist ein Vorgang und keine Eigenschaft der
 * Platte, und niemand will ihn in der abgelegten Datei.
 */
const laufendeSuche = new Set();

/**
 * Was hinter jedem Fragezeichen steht: Rechenweg, Werte (Bemessung oder
 * charakteristisch), φ -- als Stichworte, dazu die Bedingung. Alle an einer
 * Stelle, damit sie gleich gebaut sind. Die Begründungen stehen in der
 * Formelsammlung, nicht hier.
 */
const HILFE = {
  tragsicherheit: {
    zeilen: [
      ['M-N', 'Resistenzlinie von Hand, Block 0.85·x mit f_cd, Druckstahl weggelassen'],
      ['V', 'ohne Bügel k_d·τ_cd·d_v, mit Bügeln Fachwerk bei günstigster Neigung'],
      ['Werte', 'Bemessung (f_cd, f_yd, τ_cd)'],
      ['φ', '–'],
    ],
    formel: 'α_eff = Widerstand / Einwirkung ≥ 1',
  },
  duktilitaet: {
    zeilen: [
      ['Weg', 'Druckzone aus Kräftegleichgewicht bei M_Ed = 0; beide x-Lagen, gezeigt die ungünstigere'],
      ['Werte', 'Bemessung (f_cd, f_yd)'],
      ['φ', '–'],
    ],
    formel: '0.85·x·b·f_cd = A_s·f_yd    x/d ≤ 0.35',
  },
  sproede: {
    zeilen: [
      ['Weg', 'M_Rd bei N = 0 gegen Rissmoment des ungerissenen Querschnitts'],
      ['Werte', 'M_Rd Bemessung (f_cd, f_yd), M_Riss Mittelwert (f_ctm)'],
      ['φ', '–'],
    ],
    formel: 'M_Rd(N_Ed = 0) ≥ M_Riss = f_ct,eff · h²·b / 6',
  },
  zwang: {
    zeilen: [
      ['Weg', 'Risskraft des ungerissenen Querschnitts gegen A_s bei σ_s,adm'],
      ['Werte', 'f_ctm, f_yk; σ_s,adm nach Tab. 17 und Rissanforderung'],
      ['φ', '–'],
    ],
    formel: 'σ_s,adm ≥ N_Riss / A_s    N_Riss = h_eff/2 · b · f_ct,eff',
  },
  quasistaendig: {
    zeilen: [
      ['Weg', 'Stahlspannung am gerissenen Querschnitt, nur gezogene Bewehrung'],
      ['Werte', 'charakteristisch (f_ck, f_yk)'],
      ['φ', 'aus Eingabe → E_c,eff = E_cm / (1 + φ)'],
    ],
    formel: 'σ_s ≤ σ_s,adm (Tab. 17)',
  },
  haeufig: {
    zeilen: [
      ['Weg', 'Stahlspannung am gerissenen Querschnitt, nur gezogene Bewehrung'],
      ['Werte', 'charakteristisch (f_ck, f_yk), Grenze aus f_yd'],
      ['φ', 'aus Eingabe → E_c,eff = E_cm / (1 + φ)'],
    ],
    formel: 'σ_s ≤ f_yd − 80 N/mm²',
  },
  knicken: {
    zeilen: [
      ['Weg', 'verformtes System: e_0d + e_1d + e_2d, iteriert über die Krümmung'],
      ['N_Rd', 'grösste Druckkraft mit Gleichgewichtslage'],
      ['Werte', 'Bemessung (f_cd, f_yd)'],
      ['φ', 'aus Eingabe → E_c,eff = E_cm / (1 + φ)'],
    ],
    formel: 'α_eff = N_Rd / |N_Ed|',
  },
};

/** Das Fragezeichen zu einem Eintrag der Tafel oben. */
function hilfe(schluessel) {
  const { zeilen, formel } = HILFE[schluessel];
  return erklaerung(zeilen, formel);
}

/**
 * Der Knopf, der eine Liste verlängert.
 *
 * Steht unter der Liste und nicht in der Überschrift: dort ist die Stelle,
 * an der die nächste Zeile erscheint, und ein Knopf gehört dorthin, wo seine
 * Wirkung sichtbar wird. Über die ganze Breite und mit gestricheltem Rand --
 * man sieht, dass dort noch etwas hinkommt.
 */
function anfuegenKnopf(text, tun) {
  return el('button.knopf-anfuegen', { text: `+ ${text}`, on: { click: tun } });
}

/**
 * Was am Querschnitt ausgewertet wird, ohne dass es ein Nachweis waere.
 *
 * Eigenes Kapitel, weil hier nichts gegen etwas gehalten wird: kein
 * Erfüllungsgrad, kein Urteil. Unter den Nachweisen zu stehen hiesse, den
 * Unterschied zu verwischen, um den es dabei geht.
 */
export function analysenBlock(querschnitt) {
  return el('div.feldgruppe', {}, [
    el('h3', {}, [el('span', { text: 'Weitere Analysen' }),
      el('span', { text: `kein Nachweis · ${jeB(querschnitt)}` })]),
    spannungsBlock(querschnitt),
  ]);
}

/**
 * Worauf sich M und N beziehen: auf den Streifen b, nicht auf den Meter --
 * bei b = 500 mm heisst M_Ed = 50 kNm also 100 kNm/m. V gilt je Meter.
 */
function jeB(querschnitt) {
  return `M, N je b = ${querschnitt.b} mm`;
}

/** Die Nachweiskapitel einer Platte, von der Tragsicherheit bis zum Riss. */
export function nachweiseBlock(querschnitt) {
  const aendernAn = (veraenderer) => projektAendern((p) => {
    veraenderer(p.querschnitte.find((x) => x.kennung === querschnitt.kennung));
  });
  return el('div.feldgruppe', {}, [
    el('h3', {}, [el('span', { text: 'Nachweise' }),
      el('span', { text: `${jeB(querschnitt)} · V je m` })]),
    el('div.unterkapitel', {}, [
      el('div.unterkapitel-kopf', {}, [
        el('span', { text: 'Tragsicherheitsnachweise' }),
        hilfe('tragsicherheit'),
      ]),
      querschnitt.kombinationen.length
        ? el('div.einwirkung.ist-kopf', {}, [
          el('span'),
          el('span', { text: 'Bezeichnung' }),
          el('span', { text: 'M_Ed [kNm]' }),
          el('span', { text: 'N_Ed [kN]' }),
          el('span', { text: 'V_Ed [kN/m]' }),
          el('span'),
        ])
        : null,
      ...(querschnitt.kombinationen.length
        ? querschnitt.kombinationen.map((_, i) => einwirkungZeile(querschnitt, i))
        : [el('div.leer', { text: 'Ohne Einwirkung kein Nachweis.' })]),
      anfuegenKnopf('Einwirkung', () => aendernAn((q) => q.kombinationen.push({
        name: naechsterName('Tragsicherheit', q.kombinationen),
        M_Ed: 30, N_Ed: 0, V_Ed: 0, art: 'automatisch',
      }))),
    ]),

    nachweiskapitel(querschnitt, {
      titel: 'Duktilitätsnachweis', feld: 'duktilitaet', name: 'Max. x/d',
      // Vorgabe und Höchstwert der Grenze kennt der Kern. Leer gelassen
      // bleibt der bisherige Wert -- eine Grenze von null gäbe es nicht.
      zusatz: zahlfeld({
        wert: querschnitt.x_d_max, schritt: 0.05, min: 0.05,
        max: zustand.katalog?.duktilitaet?.hoechstens,
        titel: `Grenze der Druckzonenhöhe x/d; höchstens ${
          zustand.katalog?.duktilitaet?.hoechstens ?? '–'}`,
        beiAenderung: (v) => aendernAn((q) => { if (v !== null) q.x_d_max = v; }),
      }),
    }),
    nachweiskapitel(querschnitt, {
      titel: 'Nachweis gegen sprödes Versagen', feld: 'sproede', name: 'Rissmoment',
    }),

    mindestbewehrungsBlock(querschnitt),
    knickBlock(querschnitt),
  ]);
}

function einwirkungZeile(querschnitt, index) {
  const k = querschnitt.kombinationen[index];
  const aendern = (veraenderer) => projektAendern((p) => {
    veraenderer(p.querschnitte.find((x) => x.kennung === querschnitt.kennung).kombinationen[index]);
  });

  const zahl = (feld, titel, schritt = 10) => zahlfeld({
    wert: k[feld], schritt, titel,
    beiAenderung: (v) => aendern((x) => { x[feld] = v ?? 0; }),
  });

  const an = k.aktiv !== false;
  return el('div.einwirkung', { class: an ? '' : 'ist-aus' }, [
    hakenSchalter(an, (wert) => aendern((x) => { x.aktiv = wert; }), 'Lastfall'),
    el('input.ew-name', {
      type: 'text', value: k.name, title: 'Bezeichnung der Einwirkung',
      on: { change: (e) => aendern((x) => { x.name = e.target.value; }) },
    }),
    zahl('M_Ed', 'Bemessungsmoment in kNm'),
    zahl('N_Ed', 'Normalkraft in kN – Zug positiv, Druck negativ'),
    zahl('V_Ed', 'Querkraft in kN/m – 0 heisst: kein Querkraftnachweis'),
    el('button.weg', {
      text: '×', title: 'Einwirkung entfernen',
      on: {
        click: () => projektAendern((p) => {
          p.querschnitte.find((x) => x.kennung === querschnitt.kennung)
            .kombinationen.splice(index, 1);
        }),
      },
    }),
  ]);
}

/**
 * Ein Nachweiskapitel mit *einem* Schalter.
 *
 * Duktilität, sprödes Versagen und Zwängung auf Biegung sind gleich gebaut:
 * gerechnet werden die beiden x-Lagen, in der Zusammenfassung steht die
 * ungünstigere. Vorher stand hier ein Schalter je Lage -- vier Haken für eine
 * Frage, und drei davon betrafen Lagen, die niemand nachweist.
 *
 * Nachgewiesen wird nur x. Die y-Lagen stehen im Querschnitt, weil sie die
 * statische Höhe von x bestimmen; ein Nachweis fragt nicht nach ihnen.
 *
 * `name` sagt, woran gemessen wird; `zusatz` ist ein Feld dahinter, etwa die
 * Grenze x/d der Duktilität.
 */
function nachweiskapitel(querschnitt, {
  titel, feld, name, zusatz = null,
}) {
  const an = !!querschnitt[feld];
  const leer = !xLagen(querschnitt).some(
    (n) => querschnitt.lagen[n - 1].grund.durchmesser > 0
        || querschnitt.lagen[n - 1].zulage.durchmesser > 0);

  return el('div.unterkapitel', {}, [
    el('div.unterkapitel-kopf', {}, [
      el('span', { text: titel }),
      hilfe(feld),
    ]),
    el(`div.duktilitaetszeile${zusatz ? '.mit-feld' : ''}`, {}, [
      hakenSchalter(an, (wert) => projektAendern((p) => {
        p.querschnitte.find((x) => x.kennung === querschnitt.kennung)[feld] = wert;
      }), 'Nachweis'),
      el('span.richtung', {
        text: 'x', class: 'lage-x',
        title: 'Nur Tragrichtung x; es zählt die ungünstigere x-Lage',
      }),
      el('span.postenname', { text: name }),
      zusatz,
      // Ein eingeschalteter Nachweis ohne Bewehrung ist kein Fehler der
      // Eingabe -- er wird geführt und meldet selbst, dass er nicht geht.
      // Hier steht es trotzdem, damit man es beim Einschalten sieht.
      el('span.kurvenhinweis', { text: (an && leer) ? 'keine x-Bewehrung' : '' }),
    ]),
  ]);
}

/** Welche der vier Lagen in x tragen -- in aller Regel die 2. und die 3. */
function xLagen(querschnitt) {
  return [1, 2, 3, 4].filter((n) => richtungVon(querschnitt, n) === 'x');
}

/**
 * Knicken -- Druckkraft, Moment 1. Ordnung, Länge und Knicklänge je Fall.
 *
 * Nur in x-Richtung: eine Knicklänge gehört zu einer Tragrichtung, und in y
 * wäre die Breite der Platte die Länge.
 */
function knickBlock(querschnitt) {
  const faelle = querschnitt.knickfaelle || [];
  const aendern = (veraenderer) => projektAendern((p) => {
    veraenderer(p.querschnitte.find((x) => x.kennung === querschnitt.kennung));
  });

  return el('div.unterkapitel', {}, [
    el('div.unterkapitel-kopf', {}, [el('span', { text: 'Knicken' }), hilfe('knicken')]),
    faelle.length
      ? el('div.einwirkung.ist-knick.ist-kopf', {}, [
        el('span'),
        el('span', { text: 'Bezeichnung' }),
        el('span', { text: 'N_Ed,x [kN]' }),
        el('span', { text: 'M_Ed,1,x [kNm]' }),
        el('span', { text: 'l [m]' }),
        el('span', { text: 'l_cr [m]' }),
        el('span'),
      ])
      : null,
    ...(faelle.length
      ? faelle.map((_, i) => knickZeile(querschnitt, i))
      : [el('div.leer', { text: 'Kein Knicknachweis (nur x).' })]),
    anfuegenKnopf('Knicknachweis', () => aendern((q) => {
      q.knickfaelle = q.knickfaelle || [];
      q.knickfaelle.push({
        name: naechsterName('Knicken', q.knickfaelle),
        N_Ed: -500, M_Ed_1: 20, laenge: 3, knicklaenge: 3, aktiv: true,
      });
    })),
  ]);
}

function knickZeile(querschnitt, index) {
  const k = (querschnitt.knickfaelle || [])[index];
  const aendern = (veraenderer) => projektAendern((p) => {
    veraenderer(p.querschnitte.find((x) => x.kennung === querschnitt.kennung)
      .knickfaelle[index]);
  });
  const zahl = (feld, titel, schritt) => zahlfeld({
    wert: k[feld], schritt, titel,
    beiAenderung: (v) => aendern((x) => { x[feld] = v ?? 0; }),
  });

  const aktiv = k.aktiv !== false;
  return el('div.einwirkung.ist-knick', { class: aktiv ? '' : 'ist-aus' }, [
    hakenSchalter(aktiv, (wert) => aendern((x) => { x.aktiv = wert; }), 'Knicknachweis'),
    el('input.ew-name', {
      type: 'text', value: k.name, title: 'Bezeichnung des Knicknachweises',
      on: { change: (e) => aendern((x) => { x.name = e.target.value; }) },
    }),
    zahl('N_Ed', 'Druckkraft in kN – negativ, in x-Richtung', 50),
    zahl('M_Ed_1', 'Moment 1. Ordnung in kNm, um die y-Achse (Tragrichtung x)', 10),
    zahl('laenge', 'Systemlänge in m – geht in die Schiefstellung ein', 0.5),
    zahl('knicklaenge', 'Knicklänge in m', 0.5),
    el('button.weg', {
      text: '×', title: 'Knicknachweis entfernen',
      on: {
        click: () => projektAendern((p) => {
          p.querschnitte.find((x) => x.kennung === querschnitt.kennung)
            .knickfaelle.splice(index, 1);
        }),
      },
    }),
  ]);
}

/**
 * Mindestbewehrung: was angesetzt wird und wogegen.
 *
 * Zwei Teile. Oben die Zwängung -- eine Annahme über das Tragwerk, nicht über
 * die Platte, darum ausgeschaltet, bis jemand sie trifft. Unten die häufigen
 * Lastfälle, gegen die später die Stahlspannung begrenzt wird.
 *
 * Gerechnet wird hier nichts: die 70-%-Regel steht als Satz da, die Zahlen
 * dazu bildet der Kern, sobald der Nachweis läuft.
 */
/** Die gewählte Rissanforderung aus dem Katalog -- oder nichts, wenn er fehlt. */
function anforderung(querschnitt) {
  return (zustand.katalog?.rissanforderungen || [])
    .find((r) => r.wert === (querschnitt.rissanforderung || 'normal'));
}

function mindestbewehrungsBlock(querschnitt) {
  // Ob der Nachweis gegen Fliessen überhaupt gefordert ist, weiss der Kern.
  const gefordert = anforderung(querschnitt)?.fliessnachweis !== false;

  const aendern = (veraenderer) => projektAendern((p) => {
    veraenderer(p.querschnitte.find((x) => x.kennung === querschnitt.kennung));
  });

  // Der Zeilentitel sagt schon, was der Schalter tut. Die Spalte rechts
  // wiederholte das in einem ganzen Satz und machte die Tafel breit.
  // Mit Richtungsmarke wie die Lagenzeilen: dieselbe Angabe soll überall
  // gleich aussehen, sonst liest man sie zweimal verschieden.
  const zwaengung = (feld, beschriftung, richtung = null) => el(
    `div.duktilitaetszeile${richtung ? '' : '.ist-breit'}`, {}, [
      hakenSchalter(!!querschnitt[feld],
        (wert) => aendern((q) => { q[feld] = wert; }), 'Zwängung'),
      richtung
        ? el('span.richtung', {
          text: richtung, class: `lage-${richtung}`,
          title: 'Nur Tragrichtung x',
        })
        : null,
      el('span.postenname', { text: beschriftung }),
      el('span.kurvenhinweis', { text: '' }),
    ]);

  return el('div.unterkapitel', {}, [
    el('div.unterkapitel-kopf', {}, [
      el('span', { text: 'Nachweise der Rissbreitenbegrenzung' }),
    ]),

    el('div.unterkapitel-kopf', { style: { marginTop: '8px' } }, [
      el('span', { text: 'Rissbreitenbegrenzung bei Zwang' }),
      hilfe('zwang'),
    ]),
    zwaengung('zwaengung', 'Zwängung auf Normalkraft', 'x'),
    zwaengung('zwaengung_biegung', 'Zwängung auf Biegung', 'x'),
    zwaengung('zwaengung_begrenzt', 'Begrenzung auf 500 mm'),

    gebrauchsKapitel(querschnitt, {
      titel: 'Stahlspannungsbegrenzung bei quasi-ständigen Lastfällen',
      feld: 'quasistaendig',
      wort: 'quasi-ständig',
      neu: 'Quasi-ständig',
    }),

    gebrauchsKapitel(querschnitt, {
      titel: 'Verhindern des Fliessens für häufige Lastfälle',
      feld: 'haeufig',
      wort: 'häufig',
      neu: 'Häufig',
      // Bei normaler Anforderung steht in Tabelle 17 ein Strich: der
      // Nachweis entfällt, und damit auch alles, was unten eingetragen wird.
      // Ohne diesen Satz nimmt die Maske Lastfälle entgegen und rechnet sie
      // stillschweigend nicht -- man sucht das Ergebnis in der
      // Zusammenfassung und findet nichts. Was gefordert ist, sagt der Kern
      // über den Katalog; hier steht keine zweite Fassung der Norm. Nur
      // dieses Kapitel: das quasi-ständige darüber läuft immer.
      hinweis: gefordert ? null
        : `Rissanforderung «${anforderung(querschnitt)?.beschriftung ?? '–'}» → `
          + 'Tab. 17: kein Nachweis. Für Nachweis: «Erhöht» oder «Hoch».',
    }),
  ]);
}

/**
 * Ein Stahlspannungsnachweis unter Gebrauchslast: Überschrift, der Anteil
 * der Tragsicherheitseinwirkungen und die eigenen Lastfälle.
 *
 * Zweimal gebraucht -- quasi-ständig gegen die Rissbreite, häufig gegen das
 * Fliessen. Im Kern sind beide dieselbe Rechnung mit anderer Grenze, hier
 * dieselbe Maske mit anderen Feldern. Eine Kopie davon stünde in der
 * Oberfläche genau so, wie sie im Kern vermieden wurde.
 *
 * `feld` ist die Gebrauchsliste der Platte -- `haeufig` oder `quasistaendig`,
 * je mit `anteil`, `aus_tragsicherheit` und `faelle`. Vorher waren das drei
 * Feldnamen je Kapitel, die hier wieder zusammengesetzt wurden.
 *
 * Der Anteil steht in der Schalterzeile und nicht darunter: «[✓] [60] % der
 * Tragsicherheitseinwirkungen» liest sich als ein Satz, und man sieht beim
 * Einschalten, womit gerechnet wird. Seine Vorgabe kommt aus dem Kern -- die
 * Datei läuft beim Laden durch ihn und bringt den Wert immer mit.
 */
function gebrauchsKapitel(querschnitt, {
  titel, feld, wort, neu, hinweis,
}) {
  const liste = querschnitt[feld];
  const abgeleitet = !!liste.aus_tragsicherheit;
  const faelle = liste.faelle;
  const aendern = (veraenderer) => projektAendern((p) => {
    veraenderer(p.querschnitte.find((x) => x.kennung === querschnitt.kennung)[feld]);
  });

  return el('div', {}, [
    el('div.unterkapitel-kopf', { style: { marginTop: '8px' } }, [
      el('span', { text: titel }),
      hilfe(feld),
    ]),
    hinweis ? el('p.hinweis.hinweis-annahme', { text: hinweis }) : null,

    el('div.duktilitaetszeile.ist-anteil', {}, [
      hakenSchalter(abgeleitet, (wert) => aendern((l) => {
        l.aus_tragsicherheit = wert;
      }), 'Ableitung'),
      zahlfeld({
        wert: liste.anteil, schritt: 5, min: 5, max: 100,
        titel: `Anteil der Tragsicherheitseinwirkungen als ${wort}, in %`,
        // Leer gelassen bleibt der bisherige Wert -- eine Null wäre kein
        // Anteil, und der Kern wiese sie ohnehin zurück.
        beiAenderung: (v) => aendern((l) => { if (v !== null) l.anteil = v; }),
      }),
      el('span.postenname', { text: '% der Tragsicherheitseinwirkungen' }),
      el('span.kurvenhinweis', { text: '' }),
    ]),

    // Die abgeleiteten Fälle und eigene schliessen sich nicht aus: wer den
    // Anteil nimmt, kann trotzdem einen Fall von Hand dazustellen, den keine
    // Tragsicherheitskombination abbildet.
    faelle.length
      ? el('div.einwirkung.ist-kopf.ist-gebrauch', {}, [
        el('span'),
        el('span', { text: 'Bezeichnung' }),
        el('span', { text: 'M_Ed [kNm]' }),
        el('span', { text: 'N_Ed [kN]' }),
        el('span'),
      ])
      : null,
    ...(faelle.length
      ? faelle.map((_, i) => gebrauchsfallZeile(querschnitt, feld, wort, i))
      : [el('div.leer', {
        text: abgeleitet
          ? 'Nur die abgeleiteten Fälle.'
          : `Noch kein ${wort}er Lastfall.`,
      })]),
    anfuegenKnopf('Lastfall', () => aendern((l) => {
      l.faelle.push({
        name: naechsterName(neu, l.faelle),
        M_Ed: 0, N_Ed: 0, aktiv: true,
      });
    })),
  ]);
}

/** Ein Lastfall unter Gebrauchslast auf einer Zeile -- wie eine Einwirkung, ohne Querkraft. */
function gebrauchsfallZeile(querschnitt, feld, wort, index) {
  const k = querschnitt[feld].faelle[index];
  const aendern = (veraenderer) => projektAendern((p) => {
    veraenderer(p.querschnitte.find((x) => x.kennung === querschnitt.kennung)
      [feld].faelle[index]);
  });

  const aktiv = k.aktiv !== false;
  return el('div.einwirkung.ist-gebrauch', { class: aktiv ? '' : 'ist-aus' }, [
    hakenSchalter(aktiv, (wert) => aendern((x) => { x.aktiv = wert; }), 'Lastfall'),
    el('input.ew-name', {
      type: 'text', value: k.name, title: `Bezeichnung des ${wort}en Lastfalls`,
      on: { change: (e) => aendern((x) => { x.name = e.target.value; }) },
    }),
    zahlfeld({
      wert: k.M_Ed, schritt: 10, titel: `Moment unter ${wort}er Einwirkung, in kNm`,
      beiAenderung: (v) => aendern((x) => { x.M_Ed = v ?? 0; }),
    }),
    zahlfeld({
      wert: k.N_Ed, schritt: 10,
      titel: `Normalkraft unter ${wort}er Einwirkung, in kN – Zug positiv`,
      beiAenderung: (v) => aendern((x) => { x.N_Ed = v ?? 0; }),
    }),
    el('button.weg', {
      text: '×', title: `${wort[0].toUpperCase()}${wort.slice(1)}en Lastfall entfernen`,
      on: {
        click: () => projektAendern((p) => {
          p.querschnitte.find((x) => x.kennung === querschnitt.kennung)
            [feld].faelle.splice(index, 1);
        }),
      },
    }),
  ]);
}



/**
 * «Automatische Bewehrung» -- die Bewehrung suchen lassen, statt sie zu setzen.
 *
 * Unten im Kapitel «Bewehrung»: das Werkzeug schreibt in die Lagen darüber.
 *
 * Ein einzelner Knopf, kein Automatismus im Hintergrund: was hier
 * herauskommt, wird in die Lagen geschrieben und steht dann da wie eine
 * Eingabe von Hand -- man sieht es, kann es ändern und kann es lassen.
 * Eine Bewehrung, die sich bei jeder Zahl neu setzt, wäre keine Eingabe mehr.
 *
 * Gesucht wird gegen die Nachweise, die eingeschaltet sind. Die Schalter
 * weiter unten steuern damit unmittelbar, wonach gesucht wird.
 */
export function automatikBlock(querschnitt) {
  const aendern = (veraenderer) => projektAendern((p) => {
    veraenderer(p.querschnitte.find((x) => x.kennung === querschnitt.kennung));
  });
  const quer = querschnitt.automatik_querkraft === true;
  const dicke = querschnitt.automatik_dicke === true;

  // Die Teilungen als Text: «100, 150» liest und tippt sich schneller als
  // eine Liste aus Zahlenfeldern mit Plus- und Minusknöpfen.
  const teilungsfeld = (feld, titel) => el('input', {
    type: 'text', value: (querschnitt[feld] || []).join(', '), title: titel,
    on: {
      change: (e) => aendern((q) => {
        q[feld] = e.target.value.split(/[^0-9.]+/)
          .map(Number).filter((x) => x > 0);
      }),
    },
  });
  const hakenzeile = (an, setzen, text) => el('div.duktilitaetszeile.ist-breit', {}, [
    hakenSchalter(an, setzen, text),
    el('span.postenname', { text }),
    el('span'),
  ]);

  // Die Modi kommen aus dem Kern: ihre Namen stehen dort, wo sie gesucht
  // werden, und nicht ein zweites Mal hier. Die Wahl über die ganze Breite
  // und ohne Beschriftung davor -- der längste Modus braucht die Zeile.
  return el('div.unterkapitel.automatik', {}, [
    el('div.unterkapitel-kopf', {}, [el('span', { text: 'Automatische Bewehrung' })]),
    auswahl({
      werte: zustand.katalog?.suchmodi || [],
      gewaehlt: querschnitt.automatik_modus,
      titel: 'Modus. Ohne Kräfte: Duktilität, sprödes Versagen, Riss unter Zwang',
      beiAenderung: (v) => aendern((q) => { q.automatik_modus = v; }),
    }),
    // Ein Schalter neben dem Modus: je Dicke sucht das Werkzeug im gewählten
    // Modus. Die Mindestdicke gehört dazu und steht nur dann da.
    hakenzeile(dicke, (wert) => aendern((q) => {
      q.automatik_dicke = wert;
    }), 'Plattendicke optimieren'),
    ...(dicke ? [feld('Mindestdicke', zahlfeld({
      wert: querschnitt.automatik_mindestdicke ?? 150, schritt: 10, min: 10,
      titel: 'Dünner sucht die Dickenoptimierung keine Platte',
      beiAenderung: (v) => aendern((q) => { q.automatik_mindestdicke = v ?? 150; }),
    }), 'mm')] : []),
    feld('Teilungen', teilungsfeld('automatik_teilungen',
      'mm, durch Komma getrennt. Grund und Zulage einer Lage: gleiche Teilung'), 'mm'),
    // Leer heisst: kein Mindestdurchmesser -- dann darf eine Lage leer
    // bleiben. Die Null zeigt das Feld darum als leer, und die Pfeile gehen
    // wie bei der Obergrenze durch die Durchmesser: von leer aus auf 2 mm
    // hiesse einen Stab, den es nicht gibt.
    feld('Mindestdurchmesser', zahlfeld({
      wert: querschnitt.automatik_mindestdurchmesser || null, stufen: DURCHMESSER, min: 0,
      titel: 'Grundbew. jeder Lage mindestens mit diesem ⌀; leer: Lage darf leer bleiben',
      beiAenderung: (v) => aendern((q) => {
        q.automatik_mindestdurchmesser = v ?? 0;
      }),
    }), 'mm'),
    ...obergrenze(querschnitt, aendern),
    hakenzeile(querschnitt.automatik_y_wie_x === true, (wert) => aendern((q) => {
      q.automatik_y_wie_x = wert;
    }), 'y-Grundbew. wie x'),
    hakenzeile(quer, (wert) => aendern((q) => {
      q.automatik_querkraft = wert;
    }), 'Bügel mitsuchen'),
    ...(quer ? [feld('Bügelteilungen',
      teilungsfeld('automatik_querkraft_teilungen', 'mm, Raster quadratisch: s_x = s_y'),
      'mm')] : []),
    automatikLeiste(querschnitt),
  ]);
}

/**
 * Die Obergrenze je Lage: Grund und Zulage je als ⌀ @ Teilung, gebaut wie
 * die Lagenzeilen. Es zählt nur die Summe -- wie die Suche sie verteilt, ist
 * frei. Die Summe rechnet der Kern (`obergrenzen` der Lösung).
 */
function obergrenze(querschnitt, aendern) {
  const zeile = (welcher, name) => {
    const posten = querschnitt.automatik_grenze[welcher];
    const setzen = (feldname, wert) => aendern((q) => {
      q.automatik_grenze[welcher][feldname] = wert;
    });
    return el('div.postenzeile', { class: posten.durchmesser > 0 ? '' : 'ist-leer' }, [
      el('span'),
      el('span.postenname', { text: name }),
      el('span.zeichen', { text: '⌀' }),
      zahlfeld({
        wert: posten.durchmesser || null, stufen: DURCHMESSER, min: 0,
        titel: '⌀ in mm; Grund und Zulage leer: keine Obergrenze',
        beiAenderung: (v) => setzen('durchmesser', v ?? 0),
      }),
      el('span.zeichen', { text: '@' }),
      zahlfeld({
        wert: posten.abstand, schritt: 25, min: 25, titel: 'Teilung in mm',
        beiAenderung: (v) => setzen('abstand', v ?? 150),
      }),
      el('span.einheit', { text: 'mm' }),
    ]);
  };
  return [
    feld('Obergrenze je Lage',
      el('span.obergrenze', { text: zustand.loesung?.obergrenzen?.[querschnitt.kennung] ?? '…' }),
      '', 'Grund + Zulage zusammen, in allen Modi; wie die Suche es verteilt, ist frei'),
    zeile('grund', 'Grund'),
    zeile('zulage', 'Zulage'),
  ];
}

function automatikLeiste(querschnitt) {
  const kennung = querschnitt.kennung;
  const laeuft = laufendeSuche.has(kennung);
  const dicke = querschnitt.automatik_dicke === true;
  return el('div.automatik-leiste', {}, [
    el('button.knopf.knopf-haupt', {
      class: laeuft ? 'ist-am-suchen' : '',
      title: dicke ? 'Dünnste Platte suchen, Dicke und Bewehrung übernehmen'
        : 'Einmal suchen, Ergebnis in die Lagen',
      disabled: laeuft,
      on: { click: () => bewehrungErmitteln(kennung) },
    }, laeuft
      // Ein Balken, der läuft: die Suche dauert je nach Platte ein paar
      // Zehntelsekunden bis zu Sekunden. Ein Knopf, der bloss grau wird,
      // sieht in dieser Zeit aus wie einer, der nichts getan hat.
      ? [el('span.laufbalken'), el('span', { text: 'sucht …' })]
      : [el('span', { text: dicke ? 'Dicke und Bewehrung suchen' : 'Bewehrung suchen' })]),
  ]);
}

/** Einmal suchen und das Ergebnis in die Lagen schreiben. */
async function bewehrungErmitteln(kennung) {
  laufendeSuche.add(kennung);
  // Die gesuchten Lagen zuerst leeren -- sichtbar, im selben Augenblick.
  //
  // Die Suche fängt ohnehin bei null an (sie *ermittelt* die Bewehrung, sie
  // legt nicht zu dem dazu, was dasteht). Vorher blieben die alten
  // Durchmesser stehen, bis das Ergebnis kam, und wer denselben Durchmesser
  // zurückbekam, sah nicht, ob überhaupt etwas passiert war.
  //
  // In y nur die Grundbewehrung, und nur, wenn sie x folgt -- sonst sucht
  // die y-Lagen niemand, und sie bleiben wie eingetragen.
  let vorher = null;
  projektAendern((p) => {
    const q = p.querschnitte.find((x) => x.kennung === kennung);
    if (!q) return;
    vorher = q.lagen.map((lage) => [lage.grund.durchmesser, lage.zulage.durchmesser]);
    q.lagen.forEach((lage, i) => {
      const x = richtungVon(q, i + 1) === 'x';
      if (x || q.automatik_y_wie_x) lage.grund.durchmesser = 0;
      if (x) lage.zulage.durchmesser = 0;
    });
  });
  let gefunden = false;
  try {
    const antwort = await api.bewehrungSuchen(zustand.projekt, kennung);
    gefunden = antwort.gefunden;
    if (gefunden) {
      // Der Kern gibt das fertige Projekt zurück; übernommen wird die eine
      // gesuchte Platte, damit die anderen unberührt bleiben -- mit der
      // neuen Dicke, wenn der Modus sie gesucht hat.
      projektAendern((p) => {
        const alt = p.querschnitte.findIndex((x) => x.kennung === kennung);
        const neu = antwort.projekt?.querschnitte?.find((x) => x.kennung === kennung);
        if (alt >= 0 && neu) p.querschnitte[alt] = neu;
      });
      // Welche Dicken geprüft wurden, sieht man sonst nirgends.
      if (antwort.dicke) melden(antwort.begruendung);
    } else {
      // Nichts gefunden heisst: die Lagen kommen zurück, wie sie waren (unten).
      // Das sieht man nicht von selbst, also sagt es die Meldungszeile oben --
      // dort, wo auch sonst steht, was schiefging.
      melden(antwort.begruendung, true);
    }
  } catch (fehler) {
    melden(String(fehler.message || fehler), true);
  } finally {
    // Geleert waren die Lagen nur als Zeichen, dass gesucht wird. Ohne
    // Ergebnis die Durchmesser von vorher -- wo das Feld noch leer ist; was
    // jemand inzwischen eingetragen hat, bleibt.
    if (!gefunden && vorher) {
      projektAendern((p) => {
        p.querschnitte.find((x) => x.kennung === kennung)?.lagen.forEach((lage, i) => {
          const [grund, zulage] = vorher[i];
          if (!lage.grund.durchmesser) lage.grund.durchmesser = grund;
          if (!lage.zulage.durchmesser) lage.zulage.durchmesser = zulage;
        });
      });
    }
    // Zuletzt und immer. Hing das Neuzeichnen am Zweig, blieb der Knopf auf
    // «sucht …» stehen, und man musste ein zweites Mal drücken.
    laufendeSuche.delete(kennung);
    aendern({}, 'bewehrungssuche-ende');
  }
}

/**
 * Spannung-Dehnung-Analyse: drei Fragen an denselben Querschnitt.
 *
 * Kein Nachweis -- es wird nichts gegen etwas gehalten. Darum auch keine
 * Erfüllungsgrade in der Zusammenfassung; die Bilder stehen im eigenen
 * Reiter. Was jede Zeile braucht, hängt an ihrer Art, und die Felder
 * wechseln entsprechend: eine Zeile, die nach N und M fragt, soll nicht
 * daneben zwei Dehnungsfelder zeigen, die sie nicht liest.
 */
function spannungsBlock(querschnitt) {
  const faelle = querschnitt.spannungsfaelle || [];
  const aendern = (veraenderer) => projektAendern((p) => {
    veraenderer(p.querschnitte.find((x) => x.kennung === querschnitt.kennung));
  });

  return el('div.unterkapitel', {}, [
    el('div.unterkapitel-kopf', {}, [
      el('span', { text: 'Spannung-Dehnung-Analyse' }),
    ]),
    ...(faelle.length
      ? faelle.map((_, i) => spannungsZeile(querschnitt, i))
      : [el('div.leer', { text: 'Keine Analyse angelegt.' })]),
    anfuegenKnopf('Analyse', () => aendern((q) => {
      q.spannungsfaelle = q.spannungsfaelle || [];
      q.spannungsfaelle.push({
        name: naechsterName('Bild', q.spannungsfaelle),
        art: 'schnittgroessen', richtung: 'x',
        N_Ed: 0, M_Ed: 30, eps_oben: -1, eps_unten: 2, aktiv: true,
      });
    })),
  ]);
}

/** Eine Analysezeile. Die Zahlenfelder richten sich nach der gewählten Art. */
function spannungsZeile(querschnitt, index) {
  const k = (querschnitt.spannungsfaelle || [])[index];
  const aendern = (veraenderer) => projektAendern((p) => {
    veraenderer(p.querschnitte.find((x) => x.kennung === querschnitt.kennung)
      .spannungsfaelle[index]);
  });
  const zahl = (feld, titel, schritt) => zahlfeld({
    wert: k[feld], schritt, titel,
    beiAenderung: (v) => aendern((x) => { x[feld] = v ?? 0; }),
  });
  const aktiv = k.aktiv !== false;

  // Je Art andere Felder -- und immer zwei, damit die Zeilen untereinander
  // dieselbe Gestalt behalten.
  // Je Art andere Felder -- und andere Beschriftungen darüber. Ohne sie
  // stünden dort zwei namenlose Zahlen, und ob die erste eine Kraft oder
  // eine Dehnung ist, sähe man erst am Ergebnis.
  const bauplan = {
    schnittgroessen: {
      kopf: ['N_Ed [kN]', 'M_Ed [kNm]'],
      felder: () => [
        zahl('N_Ed', 'Normalkraft in kN – Zug positiv', 50),
        zahl('M_Ed', 'Moment in kNm', 10),
      ],
    },
    dehnungen: {
      kopf: ['ε oben [‰]', 'ε unten [‰]'],
      felder: () => [
        zahl('eps_oben', 'Randdehnung oben in ‰ – Zug positiv', 0.5),
        zahl('eps_unten', 'Randdehnung unten in ‰ – Zug positiv', 0.5),
      ],
    },
    moment_kruemmung: {
      kopf: ['N_Ed [kN]', ''],
      felder: () => [
        zahl('N_Ed', 'Normalkraft in kN – Zug positiv', 50),
        el('span.kurvenhinweis', { text: '0 … M_Rd' }),
      ],
    },
  }[k.art] || { kopf: ['', ''], felder: () => [el('span'), el('span')] };

  return el('div.einwirkung.ist-spannung', { class: aktiv ? '' : 'ist-aus' }, [
    hakenSchalter(aktiv, (wert) => aendern((x) => { x.aktiv = wert; }), 'Analyse'),
    el('input.ew-name', {
      type: 'text', value: k.name, title: 'Bezeichnung der Analyse',
      on: { change: (e) => aendern((x) => { x.name = e.target.value; }) },
    }),
    auswahl({
      werte: [
        { wert: 'schnittgroessen', beschriftung: 'N, M' },
        { wert: 'dehnungen', beschriftung: 'ε oben/unten' },
        { wert: 'moment_kruemmung', beschriftung: 'M–χ' },
      ],
      gewaehlt: k.art || 'schnittgroessen',
      titel: 'Eingabeart',
      beiAenderung: (v) => aendern((x) => { x.art = v; }),
    }),
    // Beschriftung über dem Feld, nicht daneben: so bleibt das Raster der
    // Zeile dasselbe, gleich welche Art gewählt ist.
    ...bauplan.felder().map((eingabe, i) => el('div.mit-kopf', {}, [
      el('span.spaltenkopf', { text: bauplan.kopf[i] || '' }),
      eingabe,
    ])),
    richtungsWahl(k.richtung || 'x', (wert) => aendern((x) => { x.richtung = wert; }),
      ['x', 'y']),
    el('button.weg', {
      text: '×', title: 'Analyse entfernen',
      on: {
        click: () => projektAendern((p) => {
          p.querschnitte.find((x) => x.kennung === querschnitt.kennung)
            .spannungsfaelle.splice(index, 1);
        }),
      },
    }),
  ]);
}
