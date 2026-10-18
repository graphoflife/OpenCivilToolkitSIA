/**
 * plattenkapitel.js -- was von einer Platte verlangt wird, Kapitel für Kapitel.
 *
 * Die Kapitel der Platte (`plattenKapitel`): ihre Tragsicherheit samt den
 * Angaben zur Querkraft, die Nachweise, die sie mit dem gezeichneten
 * Querschnitt teilt (`nachweise.js`), die Verformung, die sechs
 * Spannung-Dehnung-Analysen und das Werkzeug, das die Bewehrung sucht
 * (`bewehrungssuche.js`). Dazu ihr Ort `PLATTE`: was bei der Platte anders
 * ist als beim gezeichneten Querschnitt, und was hinter ihren Fragezeichen
 * steht.
 *
 * Eigenes Modul, weil die beiden Hälften wenig miteinander zu tun haben: in
 * `editor.js` steht, was die Platte *ist* -- Abmessungen, Material, Lagen
 * --, hier, was von ihr *verlangt* wird.
 *
 * Gerechnet wird hier nichts. Jede Zeile beschreibt eine Eingabe; die Zahlen
 * dazu bildet der Kern, sobald der Nachweis läuft.
 */

import {
  erklaerung, feld, richtungsWahl, zweiSchalter,
} from './bausteine.js';
import { SUCHE } from './bewehrungssuche.js';
import { el, zahlfeld } from './dom.js';
import { fallkopf, fallzeile } from './faelle.js';
import { zeilenstand } from './kapitel.js';
import { xLagen } from './lagen.js';
import { span } from './mathe.js';
import {
  analysenKapitel, anBauteil, anfuegenKnopf, nachweisKapitel, rechenwahlZeile,
} from './nachweise.js';
import { ausVorlage, feldangabe, naechsterName, projektAendern, zustand } from './zustand.js';

/**
 * Was hinter den Fragezeichen der Platte steht: Rechenweg, Werte (Bemessung
 * oder charakteristisch), φ -- als Stichworte, dazu die Bedingung. Alle an
 * einer Stelle, damit sie gleich gebaut sind. Die Begründungen stehen in der
 * Dokumentation, nicht hier.
 *
 * Knicken und die beiden Stahlspannungen rechnet der gezeichnete Querschnitt
 * gleich: dort steht hier nur, was bei der Platte dazukommt, das Übrige
 * steht bei den Kapiteln (`nachweisKapitel` in nachweise.js).
 */
const HILFE = {
  tragsicherheit: {
    zeilen: [
      ['M-N', 'Resistenzlinie nach Rechenwahl; Vorgabe Handrechnung: Block 0.85·x, Druckstahl weggelassen'],
      ['V', 'ohne Bügel k_d·τ_cd·d_v mit m_R aus derselben Linie, mit Bügeln Fachwerk bei günstigster Neigung'],
      ['Werte', 'M-N nach Rechenwahl: Bemessung (f_cd, f_yd → M_Rd) oder charakteristisch (f_ck, f_yk → M_Rk); V mit τ_cd, f_yd'],
      ['φ', 'nach Rechenwahl, nur präzise → E_c,eff = E_cm / (1 + φ)'],
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
      ['Weg', 'M_Rd bei N = 0 aus der Linie der Tragsicherheit gegen Rissmoment des ungerissenen Querschnitts'],
      ['Werte', 'M_Rd wie die Tragsicherheit (charakteristisch: M_Rk), M_Riss Mittelwert (f_ctm)'],
      ['φ', '–'],
    ],
    formel: 'M_Rd(N_Ed = 0) ≥ M_Riss = f_ct,eff · h²·b / 6',
  },
  zwang: {
    zeilen: [
      ['Weg', 'Risskraft des ungerissenen Querschnitts gegen A_s bei σ_s,adm'],
      ['Werte', 'f_ctm, f_yk; σ_s,adm nach Tab. 17 und Rissanforderung'],
      ['φ', 'Normalkraft: –; Biegung: eigenes φ → n = E_s/E_cm · (1 + φ)'],
    ],
    formel: 'σ_s,adm ≥ N_Riss / A_s    N_Riss = h_eff/2 · b · f_ct,eff',
  },
  quasistaendig: {
    zeilen: [
      ['Weg', 'Stahlspannung am gerissenen Querschnitt, an der am stärksten gezogenen Lage'],
      ['Grenze', 'σ_s,adm mit dem dicksten Stab der Tragrichtung'],
    ],
  },
  haeufig: {
    zeilen: [
      ['Weg', 'Stahlspannung am gerissenen Querschnitt, an der am stärksten gezogenen Lage'],
    ],
  },
  verformung: {
    zeilen: [
      ['Weg', 'w mit E_cm ermittelt, mal Vergrösserungsfaktor ω_w der gezogenen Seite'],
      ['ω_w', 'SIA 262:2025, 4.4.3.2.5 – je Platte und gezogene Seite einmal gerechnet'],
      ['Grenze', 'w_max = L/350 – nach Vorgabe, nicht nachgeschlagen'],
      ['φ', 'oben im Fenster, für alle Fälle der Platte; Vorgabe 2'],
    ],
    formel: 'w_eff = ω_w · w ≤ w_max = L/350',
  },
  knicken: {
    zeilen: [
      ['Richtung', 'nur Tragrichtung x'],
      ['Linie', 'Widerstand gleich gewählt wie die Tragsicherheit: deren Linie'],
    ],
  },
};

/**
 * Die Kapitel der Platte in ihren Gruppen: die Nachweise, die Analysen und
 * das Werkzeug, das die Bewehrung sucht.
 */
export function plattenKapitel() {
  return [
    { titel: 'Nachweise', kapitel: [TRAGSICHERHEIT, ...nachweisKapitel(PLATTE), VERFORMUNG] },
    { titel: 'Spannung-Dehnung-Analysen', kapitel: analysenKapitel(PLATTE) },
    { titel: 'Werkzeug', kapitel: [SUCHE] },
  ];
}

/** Die Tragsicherheit der Platte -- mit der Querkraft, und die gilt je Meter. */
const TRAGSICHERHEIT = {
  schluessel: 'tragsicherheit',
  name: 'Trag\u00adsicherheit', titel: 'Tragsicherheitsnachweise',
  bezug: (q) => `${jeB(q)} · V je m`,
  hilfe: HILFE.tragsicherheit,
  inhalt: tragsicherheitInhalt,
  stand: (q) => zeilenstand(q.kombinationen, 'Einwirkung', 'Einwirkungen', 'keine Einwirkung'),
};

const VERFORMUNG = {
  schluessel: 'verformung',
  name: 'Verformung', titel: 'Begrenzung der Durchbiegung',
  bezug: () => 'w in mm · L in m · nur x',
  hilfe: HILFE.verformung,
  inhalt: verformungInhalt,
  stand: (q) => zeilenstand(q.verformung?.faelle, 'Fall', 'Fälle', 'kein Fall'),
};

/**
 * Wo die Kapitel eines Bauteils stehen und was bei ihm anders ist: die
 * Liste im Projekt, die Vorlage einer neuen Analyse und ihre Richtung -- bei
 * der Platte die Tragrichtung x oder y. Der gezeichnete Querschnitt hat seinen
 * eigenen Ort (`querschnittsanalyse.js`): dort ist die Richtung die Zugseite.
 * `raender(k)` sagt, wie die beiden Ränder einer Analyse heissen -- der
 * gedrückte und der gezogene.
 *
 * Für die Kapitel (`nachweisKapitel`, `analysenKapitel`): `bezug(e)` steht
 * unter dem Titel eines Fensters, `hilfe` hinter seinem Fragezeichen.
 * `marke()` und `hinweis(e, feld)` stehen vor und hinter den Zeilen mit
 * einem Schalter, `rechenwerte` unter Duktilität und sprödem Versagen.
 * `gebrauch` und `knick` sind, was die Stahlspannungen und das Knicken beim
 * Bauteil anders zeigen.
 */
export const PLATTE = {
  liste: 'querschnitte',
  vorlage: 'analyse',
  richtung: (k, setzen) => richtungsWahl(k.richtung || 'x', setzen, ['x', 'y']),
  raender: () => ['oben', 'unten'],
  bezug: jeB,
  hilfe: HILFE,
  // Nachgewiesen wird nur x: vor jedem Schalter die Marke der Tragrichtung,
  // wie in den Lagenzeilen -- dieselbe Angabe soll überall gleich aussehen,
  // sonst liest man sie zweimal verschieden.
  marke: () => el('span.richtung', {
    text: 'x', class: 'lage-x', title: 'Nur Tragrichtung x; es zählt die ungünstigere x-Lage',
  }),
  // Ein eingeschalteter Nachweis ohne Bewehrung ist kein Fehler der
  // Eingabe -- er wird geführt und meldet selbst, dass er nicht geht. Hier
  // steht es trotzdem, damit man es beim Einschalten sieht.
  hinweis: (q, feld) => (q[feld] && !xBewehrt(q) ? 'keine x-Bewehrung' : ''),
  // Womit Duktilität und sprödes Versagen rechnen, steht im Fragezeichen:
  // die beiden rechnen hier verschieden.
  rechenwerte: null,
  // Das Knicken: nur in x.
  knick: {
    vorlage: 'knickfall',
    kopf: ['N_Ed,x [kN]', 'M_Ed,1,x [kNm]', 'l [m]', 'l_cr [m]'],
    titel: {
      N_Ed: 'Druckkraft in kN – negativ, in x-Richtung',
      M_Ed_1: 'Moment 1. Ordnung in kNm, um die y-Achse (Tragrichtung x)',
      laenge: 'Systemlänge in m – geht in die Schiefstellung ein',
      knicklaenge: 'Knicklänge in m',
    },
    richtung: null,
    leer: 'Kein Knicknachweis (nur x).',
  },
  // Die Lastfälle unter Gebrauchslast: Moment und Normalkraft je b.
  gebrauch: {
    vorlage: 'gebrauchsfall',
    arten: 'spannungsarten',
    spalten: () => [
      {
        feld: 'M_Ed', kopf: 'M_Ed [kNm]', schritt: 10,
        titel: (wort) => `Moment unter ${wort}er Einwirkung, in kNm`,
      },
      {
        feld: 'N_Ed', kopf: 'N_Ed [kN]', schritt: 10,
        titel: (wort) => `Normalkraft unter ${wort}er Einwirkung, in kN – Zug positiv`,
      },
    ],
  },
};

/** Ob in x Bewehrung liegt -- Grund oder Zulage einer x-Lage. */
function xBewehrt(querschnitt) {
  return xLagen(querschnitt).some((n) => querschnitt.lagen[n - 1].grund.durchmesser > 0
    || querschnitt.lagen[n - 1].zulage.durchmesser > 0);
}

/**
 * Worauf sich M und N beziehen: auf den Streifen b, nicht auf den Meter --
 * bei b = 500 mm heisst M_Ed = 50 kNm also 100 kNm/m. V gilt je Meter.
 */
function jeB(querschnitt) {
  return `M, N je b = ${querschnitt.b} mm`;
}

/** Dasselbe für die Platte. */
function anPlatte(querschnitt) {
  return anBauteil(querschnitt, PLATTE);
}

/**
 * Tragsicherheit: Rechenwahl, die Einwirkungen und die Angaben, die allein
 * die Querkraft braucht.
 */
function tragsicherheitInhalt(querschnitt) {
  const aendernAn = anPlatte(querschnitt);
  return [
    rechenwahlZeile('Rechenwahl', querschnitt.tragsicherheit_wahl,
      (veraenderer) => aendernAn((q) => veraenderer(q.tragsicherheit_wahl))),
    querschnitt.kombinationen.length
      ? fallkopf(['M_Ed [kNm]', 'N_Ed [kN]', 'V_Ed [kN/m]'])
      : null,
    ...(querschnitt.kombinationen.length
      ? querschnitt.kombinationen.map((_, i) => einwirkungZeile(querschnitt, i))
      : [el('div.leer', { text: 'Ohne Einwirkung kein Nachweis.' })]),
    anfuegenKnopf('Einwirkung', () => aendernAn((q) => q.kombinationen.push(
      ausVorlage('einwirkung', { name: naechsterName('Tragsicherheit', q.kombinationen) }),
    ))),
    querkraftAngaben(querschnitt),
  ];
}

/**
 * Was allein der Querkraftnachweis braucht -- darum hier und nicht bei der
 * Platte: ohne Bügel Grösstkorn und Einlagenhöhe, mit Bügeln die
 * Abminderung k_c und die Grenzen der Neigung. In keinem anderen Nachweis
 * spielen sie eine Rolle.
 */
function querkraftAngaben(querschnitt) {
  const aendernAn = anPlatte(querschnitt);
  const buegel = querschnitt.querkraftbewehrung;
  const aendernBuegel = (veraenderer) => aendernAn((q) => veraenderer(q.querkraftbewehrung));
  return el('div.unterkapitel', {}, [
    el('div.unterkapitel-kopf', {}, [el('span', { text: 'Querkraft ohne Bügel' })]),
    feld(['Grösstkorn ', span('D_{max}')], zahlfeld({
      wert: querschnitt.d_max, schritt: 4, min: 1,
      titel: 'Für k_g, Querkraft ohne Bügel',
      beiAenderung: (v) => aendernAn((q) => { q.d_max = v; }),
    }), 'mm', 'Grösstkorn → k_g, Querkraft ohne Bügel'),
    feld('Einlagenhöhe', zahlfeld({
      wert: querschnitt.einlagenhoehe, schritt: 5, min: 0,
      titel: 'Verringert d_v, falls h/6 < e < d',
      leer: 0,
      beiAenderung: (v) => aendernAn((q) => { q.einlagenhoehe = v; }),
    }), 'mm'),
    el('div.unterkapitel-kopf', { style: { marginTop: '8px' } }, [
      el('span', { text: 'Querkraft mit Bügeln' }),
    ]),
    feld(['Druckdiagonale ', span('k_c')], zahlfeld({
      wert: querschnitt.k_c, schritt: 0.05, min: 0,
      titel: 'Abminderung f_cd in der Druckdiagonalen; nur mit Bügeln',
      beiAenderung: (v) => aendernAn((q) => { q.k_c = v; }),
    }), '', 'Abminderung f_cd in der Druckdiagonalen'),
    ...[['alpha_min', String.raw`\alpha_{min}`, 'Kleinste'],
      ['alpha_max', String.raw`\alpha_{max}`, 'Grösste']].map(([schluessel, symbol, welche]) => {
      const angabe = feldangabe('querkraftbewehrung', schluessel);
      return feld(['Neigung ', span(symbol)], zahlfeld({
        wert: buegel[schluessel], angabe,
        titel: `${welche} Neigung der Druckdiagonalen, ganze °`,
        beiAenderung: (v) => aendernBuegel((x) => { x[schluessel] = v; }),
      }), angabe.einheit);
    }),
  ]);
}

function einwirkungZeile(querschnitt, index) {
  const k = querschnitt.kombinationen[index];
  const aendern = (veraenderer) => projektAendern((p) => {
    veraenderer(p.querschnitte.find((x) => x.kennung === querschnitt.kennung).kombinationen[index]);
  });

  // Eine Last, die man leert, ist keine Last.
  const zahl = (feld, titel, schritt = 10) => zahlfeld({
    wert: k[feld], schritt, titel, leer: 0,
    beiAenderung: (v) => aendern((x) => { x[feld] = v; }),
  });

  return fallzeile({
    an: k.aktiv !== false, umschalten: (wert) => aendern((x) => { x.aktiv = wert; }),
    was: 'Lastfall', name: k.name, nameTitel: 'Bezeichnung der Einwirkung',
    umbenennen: (name) => aendern((x) => { x.name = name; }),
    zahlen: [
      zahl('M_Ed', 'Bemessungsmoment in kNm'),
      zahl('N_Ed', 'Normalkraft in kN – Zug positiv, Druck negativ'),
      zahl('V_Ed', 'Querkraft in kN/m – 0 heisst: kein Querkraftnachweis'),
    ],
    entfernenTitel: 'Einwirkung entfernen',
    entfernen: () => projektAendern((p) => {
      p.querschnitte.find((x) => x.kennung === querschnitt.kennung)
        .kombinationen.splice(index, 1);
    }),
  });
}

/**
 * Die Verformung: zuoberst die Kriechzahl φ des Vergrösserungsfaktors ω_w,
 * darunter die Verformungsfälle -- je Fall w, die Spannweite L und die
 * Seite, die er zieht.
 *
 * φ gilt für die ganze Platte, nicht je Fall: ω_w hängt nur an der Platte
 * und an der gezogenen Seite und wird je Seite einmal gerechnet (Benutzer,
 * 2026-10-16). Vorher stand φ oben bei der Platte, nur für diesen Faktor.
 */
function verformungInhalt(querschnitt) {
  const aendern = (veraenderer) => anPlatte(querschnitt)((q) => veraenderer(q.verformung));
  const { kriechzahl, faelle } = querschnitt.verformung;
  return [
    feld(['Kriechzahl ', span(String.raw`\varphi`)], zahlfeld({
      wert: kriechzahl, schritt: 0.1, min: 0,
      titel: 'Kriechzahl φ im Vergrösserungsfaktor ω_w',
      beiAenderung: (v) => aendern((l) => { l.kriechzahl = v; }),
    }), erklaerung([
      ['Wofür', 'den Vergrösserungsfaktor ω_w (SIA 262:2025, 4.4.3.2.5)'],
      ['Gilt für', 'alle Verformungsfälle dieser Platte: ω_w wird je gezogene Seite einmal gerechnet'],
    ], 'ω_w = (1 − 20ρ′)/(10ρ^0.7) · (0.75 + 0.1φ) · (h/d)³')),
    el('p.hinweis.hinweis-annahme', { text: 'w mit der Steifigkeit E_cm ermitteln.' }),
    faelle.length ? fallkopf(['w [mm]', 'L [m]', 'Zug']) : null,
    ...(faelle.length
      ? faelle.map((_, i) => verformungsZeile(querschnitt, i))
      : [el('div.leer', { text: 'Noch kein Verformungsfall (nur x).' })]),
    anfuegenKnopf('Verformungsfall', () => aendern((l) => {
      l.faelle.push(ausVorlage('verformungsfall', { name: naechsterName('Verformung', l.faelle) }));
    })),
  ];
}

/** Ein Verformungsfall auf einer Zeile: w, L und die gezogene Seite. */
function verformungsZeile(querschnitt, index) {
  const k = querschnitt.verformung.faelle[index];
  const aendern = (veraenderer) => anPlatte(querschnitt)((q) => {
    veraenderer(q.verformung.faelle[index]);
  });
  const seiten = zustand.katalog?.verformung?.zugseiten || [];
  return fallzeile({
    an: k.aktiv !== false, umschalten: (wert) => aendern((x) => { x.aktiv = wert; }),
    was: 'Verformungsfall', name: k.name, nameTitel: 'Bezeichnung des Verformungsfalls',
    umbenennen: (name) => aendern((x) => { x.name = name; }),
    zahlen: [
      zahlfeld({
        wert: k.w, schritt: 1, min: 0, leer: 0,
        titel: 'Durchbiegung w in mm, mit der Steifigkeit E_cm ermittelt',
        beiAenderung: (v) => aendern((x) => { x.w = v; }),
      }),
      // Eine Spannweite null gibt es nicht -- geleert bleibt der bisherige Wert.
      zahlfeld({
        wert: k.laenge, schritt: 0.5,
        titel: 'Spannweite L in m – der Grenzwert ist L/350',
        beiAenderung: (v) => aendern((x) => { x.laenge = v; }),
      }),
      seiten.length === 2
        ? zweiSchalter({
          stellungen: seiten.map((s) => [s.wert, s.beschriftung]),
          gewaehlt: k.zugseite, klasse: '.schalter-richtung',
          setzen: (wert) => aendern((x) => { x.zugseite = wert; }),
          titel: `Zug ${k.zugseite}: danach richtet sich ω_w -- Klicken schaltet um`,
        })
        : el('span'),
    ],
    entfernenTitel: 'Verformungsfall entfernen',
    entfernen: () => anPlatte(querschnitt)((q) => { q.verformung.faelle.splice(index, 1); }),
  });
}
