/**
 * nachweise.js -- was von einer Platte verlangt wird, Kapitel für Kapitel.
 *
 * Jedes Kapitel öffnet sich in einem eigenen Fenster (`kapitel.js`):
 * Tragsicherheit samt den Angaben zur Querkraft, Knicken, Duktilität,
 * sprödes Versagen, Rissbreite bei Zwang, die beiden Stahlspannungen und
 * die sechs Spannung-Dehnung-Analysen; dazu das Werkzeug, das die Bewehrung
 * sucht. Hier steht, was in den Fenstern steht -- `…Inhalt(q)` liefert die
 * Knoten.
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
  erklaerung, feld, hakenSchalter, richtungsWahl,
} from './bausteine.js';
import { auswahl, el, melden, zahlfeld } from './dom.js';
import { xLagen } from './lagen.js';
import { span } from './mathe.js';
import {
  aendern, ausVorlage, naechsterName, projektAendern, zustand,
} from './zustand.js';

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
 * Dokumentation, nicht hier.
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
      ['Werte', 'nach Rechenwahl; Vorgabe charakteristisch (f_ck, f_yk), elastisch'],
      ['φ', 'nach Rechenwahl → E_c,eff = E_cm / (1 + φ), präzise und elastisch'],
    ],
    formel: 'σ_s ≤ σ_s,adm (Tab. 17)',
  },
  haeufig: {
    zeilen: [
      ['Weg', 'Stahlspannung am gerissenen Querschnitt, an der am stärksten gezogenen Lage'],
      ['Werte', 'nach Rechenwahl; Vorgabe charakteristisch (f_ck, f_yk), elastisch; Grenze aus f_yd'],
      ['φ', 'nach Rechenwahl → E_c,eff = E_cm / (1 + φ), präzise und elastisch'],
    ],
    formel: 'σ_s ≤ f_yd − 80 N/mm²',
  },
  knicken: {
    zeilen: [
      ['Weg', 'verformtes System: e_0d + e_1d + e_2d, iteriert über die Krümmung'],
      ['N_Rd', 'grösste Druckkraft mit Gleichgewichtslage'],
      ['Verformung', 'e_2d immer präzise; φ und Werte nach Wahl, Vorgabe Bemessung (f_cd, f_yd)'],
      ['Widerstand', 'Rechenwahl für N_Rd(M_Ed = N_Ed·e_tot), ohne Handrechnung; Vorgabe 0.85·x, Bemessung; gleich wie die Tragsicherheit gewählt: deren Linie'],
      ['φ', 'je Wahl, nur präzise → E_c,eff = E_cm / (1 + φ)'],
    ],
    formel: 'α_eff = N_Rd / |N_Ed|',
  },
};

/**
 * Das Fragezeichen im Kopf eines Fensters -- null, wo es nichts zu erklären
 * gibt: die Analysen und die Suche haben keines.
 */
export function hilfe(schluessel) {
  const eintrag = HILFE[schluessel];
  return eintrag ? erklaerung(eintrag.zeilen, eintrag.formel) : null;
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
 * Worauf sich M und N beziehen: auf den Streifen b, nicht auf den Meter --
 * bei b = 500 mm heisst M_Ed = 50 kNm also 100 kNm/m. V gilt je Meter.
 */
export function jeB(querschnitt) {
  return `M, N je b = ${querschnitt.b} mm`;
}

/**
 * Ändert das Bauteil im Projekt -- für die Fenster, die an ihm schreiben.
 * `ort.liste` sagt, in welcher Liste des Projekts es steht.
 */
function anBauteil(eintrag, ort) {
  return (veraenderer) => projektAendern((p) => {
    veraenderer(p[ort.liste].find((x) => x.kennung === eintrag.kennung));
  });
}

/** Dasselbe für die Platte. */
function anPlatte(querschnitt) {
  return anBauteil(querschnitt, PLATTE);
}

/**
 * Tragsicherheit: Rechenwahl, die Einwirkungen und die Angaben, die allein
 * die Querkraft braucht.
 */
export function tragsicherheitInhalt(querschnitt) {
  const aendernAn = anPlatte(querschnitt);
  return [
    rechenwahlZeile('Rechenwahl', querschnitt.tragsicherheit_wahl,
      (veraenderer) => aendernAn((q) => veraenderer(q.tragsicherheit_wahl))),
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
    feld(['Neigung ', span(String.raw`\alpha_{min}`)], zahlfeld({
      wert: buegel.alpha_min, schritt: 1, min: 1, max: 89,
      titel: 'Kleinste Neigung der Druckdiagonalen, ganze °',
      beiAenderung: (v) => aendernBuegel((x) => { x.alpha_min = Math.round(v); }),
    }), '°'),
    feld(['Neigung ', span(String.raw`\alpha_{max}`)], zahlfeld({
      wert: buegel.alpha_max, schritt: 1, min: 1, max: 89,
      titel: 'Grösste Neigung der Druckdiagonalen, ganze °',
      beiAenderung: (v) => aendernBuegel((x) => { x.alpha_max = Math.round(v); }),
    }), '°'),
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
 * Die Zeile eines Nachweises mit *einem* Schalter.
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
function schalterZeile(querschnitt, { feld, name, zusatz = null }) {
  const an = !!querschnitt[feld];
  const leer = !xLagen(querschnitt).some(
    (n) => querschnitt.lagen[n - 1].grund.durchmesser > 0
        || querschnitt.lagen[n - 1].zulage.durchmesser > 0);

  return el(`div.duktilitaetszeile${zusatz ? '.mit-feld' : ''}`, {}, [
    hakenSchalter(an, (wert) => anPlatte(querschnitt)((q) => { q[feld] = wert; }), 'Nachweis'),
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
  ]);
}

/** Duktilität: ein Schalter und die Grenze x/d. */
export function duktilitaetInhalt(querschnitt) {
  return [schalterZeile(querschnitt, {
    feld: 'duktilitaet', name: 'Max. x/d',
    // Vorgabe und Höchstwert der Grenze kennt der Kern. Leer gelassen
    // bleibt der bisherige Wert -- eine Grenze von null gäbe es nicht.
    zusatz: zahlfeld({
      wert: querschnitt.x_d_max, schritt: 0.05, min: 0.05,
      max: zustand.katalog?.duktilitaet?.hoechstens,
      titel: `Grenze der Druckzonenhöhe x/d; höchstens ${
        zustand.katalog?.duktilitaet?.hoechstens ?? '–'}`,
      beiAenderung: (v) => anPlatte(querschnitt)((q) => { q.x_d_max = v; }),
    }),
  })];
}

/** Sprödes Versagen: ein Schalter. */
export function sproedeInhalt(querschnitt) {
  return [schalterZeile(querschnitt, { feld: 'sproede', name: 'Rissmoment' })];
}

/**
 * Knicken -- Druckkraft, Moment 1. Ordnung, Länge und Knicklänge je Fall.
 *
 * Bei der Platte nur in x-Richtung: eine Knicklänge gehört zu einer
 * Tragrichtung, und in y wäre die Breite der Platte die Länge. Der
 * gezeichnete Querschnitt wählt je Fall die Zugseite, zu der sich der Stab
 * biegt -- `ort.knick.richtung` baut die Auswahl; sie steht oben neben dem
 * Namen, die vier Zahlen bleiben darunter. `ort.knick` sagt auch die Köpfe
 * und Titel der Spalten.
 */
export function knickInhalt(eintrag, ort = PLATTE) {
  const faelle = eintrag.knickfaelle || [];
  const aendern = anBauteil(eintrag, ort);
  const knick = ort.knick;

  return [
    // Zwei Wahlen: womit die Verformung gerechnet wird und womit der
    // Querschnitt widersteht. Ohne Handrechnung: beim Knicken zählt die
    // Normalkraft genau. Die Verformung nur präzise -- mit dem
    // Spannungsblock wäre die Ausmitte nahe der Grenzkraft nicht eindeutig.
    rechenwahlZeile('Verformung (e_2d)', eintrag.knicken_wahl_verformung,
      (veraenderer) => aendern((q) => veraenderer(q.knicken_wahl_verformung)),
      { arten: 'verformungsarten' }),
    rechenwahlZeile('Widerstand (N_Rd)', eintrag.knicken_wahl_widerstand,
      (veraenderer) => aendern((q) => veraenderer(q.knicken_wahl_widerstand)),
      { arten: 'faserarten' }),
    faelle.length
      ? el('div.einwirkung.ist-knick.ist-kopf', {}, [
        el('span'),
        el('span', { text: 'Bezeichnung' }),
        ...knick.kopf.map((text) => el('span', { text })),
        el('span'),
      ])
      : null,
    ...(faelle.length
      ? faelle.map((_, i) => knickZeile(eintrag, ort, i))
      : [el('div.leer', { text: knick.leer })]),
    anfuegenKnopf('Knicknachweis', () => aendern((q) => {
      q.knickfaelle = q.knickfaelle || [];
      q.knickfaelle.push(
        ausVorlage(knick.vorlage, { name: naechsterName('Knicken', q.knickfaelle) }));
    })),
  ];
}

function knickZeile(eintrag, ort, index) {
  const k = (eintrag.knickfaelle || [])[index];
  const aendern = (veraenderer) => anBauteil(eintrag, ort)((e) => veraenderer(e.knickfaelle[index]));
  const titel = ort.knick.titel;
  // Eine Länge null gibt es nicht -- geleert bleibt der bisherige Wert.
  const zahl = (feld, schritt) => zahlfeld({
    wert: k[feld], schritt, titel: titel[feld],
    beiAenderung: (v) => aendern((x) => { x[feld] = v; }),
  });

  const aktiv = k.aktiv !== false;
  const richtung = ort.knick.richtung;
  return el(`div.einwirkung.ist-knick${richtung ? '.mit-zugseite' : ''}`, {
    class: aktiv ? '' : 'ist-aus',
  }, [
    hakenSchalter(aktiv, (wert) => aendern((x) => { x.aktiv = wert; }), 'Knicknachweis'),
    el('input.ew-name', {
      type: 'text', value: k.name, title: 'Bezeichnung des Knicknachweises',
      on: { change: (e) => aendern((x) => { x.name = e.target.value; }) },
    }),
    zahl('N_Ed', 50),
    zahl('M_Ed_1', 10),
    zahl('laenge', 0.5),
    zahl('knicklaenge', 0.5),
    richtung ? richtung(k, (wert) => aendern((x) => { x.richtung = wert; })) : null,
    el('button.weg', {
      text: '×', title: 'Knicknachweis entfernen',
      on: {
        click: () => anBauteil(eintrag, ort)((e) => { e.knickfaelle.splice(index, 1); }),
      },
    }),
  ]);
}

/**
 * Die Rissanforderung als erste Zeile der drei Rissnachweise -- Zwang,
 * quasi-ständig, häufig. Sie gehört dem Bauteil, nicht dem Nachweis: in
 * einem der drei Fenster gewählt, gilt sie in allen. Vorher stand sie oben
 * bei der Platte, weit weg von den Nachweisen, die sie brauchen (Benutzer,
 * 2026-10-16).
 */
function rissanforderungZeile(eintrag, ort) {
  return feld('Rissanforderung', auswahl({
    werte: (zustand.katalog?.rissanforderungen || []).map((r) => ({
      wert: r.wert, beschriftung: r.beschriftung,
    })),
    gewaehlt: eintrag.rissanforderung || 'normal',
    titel: 'Bestimmt σ_s,adm (Tab. 17)',
    beiAenderung: (v) => anBauteil(eintrag, ort)((e) => { e.rissanforderung = v; }),
  }), erklaerung([
    ['Gilt für', 'alle Rissnachweise: Riss bei Zwang, Stahlspannung quasi-ständig '
      + 'und Fliessen häufig. Hier geändert, ändert sie sich in allen dreien.'],
    ['Bestimmt', 'σ_s,adm nach Tab. 17 und ob «Fliessen häufig» gefordert ist'],
  ]));
}

/** Die gewählte Rissanforderung aus dem Katalog -- oder nichts, wenn er fehlt. */
function anforderung(querschnitt) {
  return (zustand.katalog?.rissanforderungen || [])
    .find((r) => r.wert === (querschnitt.rissanforderung || 'normal'));
}

/** Ob der Nachweis gegen Fliessen gefordert ist -- das weiss der Kern über den Katalog. */
export function fliessenGefordert(querschnitt) {
  return anforderung(querschnitt)?.fliessnachweis !== false;
}

/**
 * Rissbreite bei Zwang: Normalkraft, Biegung mit ihrem eigenen φ, und die
 * Begrenzung der rissaktiven Dicke. Eine Annahme über das Tragwerk, nicht
 * über das Bauteil -- darum ausgeschaltet, bis jemand sie trifft.
 *
 * `ort.zwang(e)` sagt, was beim Bauteil anders ist: bei der Platte steht die
 * Marke der Tragrichtung x vor den Zeilen, beim gezeichneten Querschnitt
 * dahinter, worüber nachgewiesen wird.
 */
export function zwangInhalt(eintrag, ort = PLATTE) {
  const aendern = anBauteil(eintrag, ort);
  const { marke, hinweise, phiTitel } = ort.zwang(eintrag);

  // Der Zeilentitel sagt schon, was der Schalter tut. Die Spalte rechts
  // wiederholte das in einem ganzen Satz und machte die Tafel breit.
  // Mit Richtungsmarke wie die Lagenzeilen: dieselbe Angabe soll überall
  // gleich aussehen, sonst liest man sie zweimal verschieden.
  const zwaengung = (feld, beschriftung, { mitMarke = false, zusatz = null } = {}) => {
    const vorne = mitMarke && marke ? marke() : null;
    const art = vorne ? (zusatz ? '.mit-feld' : '') : (zusatz ? '.mit-grenze' : '.ist-breit');
    return el(`div.duktilitaetszeile${art}`, {}, [
      hakenSchalter(!!eintrag[feld], (wert) => aendern((q) => { q[feld] = wert; }), 'Zwängung'),
      vorne,
      el('span.postenname', { text: beschriftung }),
      zusatz,
      el('span.kurvenhinweis', { text: hinweise[feld] || '' }),
    ]);
  };

  return [
    rissanforderungZeile(eintrag, ort),
    zwaengung('zwaengung', 'Zwängung auf Normalkraft', { mitMarke: true }),
    // Die Zwängung auf Biegung rechnet am gerissenen Querschnitt -- mit
    // ihrem eigenen φ, nicht dem der Platte.
    zwaengung('zwaengung_biegung', 'Zwängung auf Biegung', {
      mitMarke: true,
      zusatz: el('span.zeilenfeld', {}, [
        el('span.zeichen', { text: 'φ' }),
        zahlfeld({
          wert: eintrag.zwaengung_biegung_kriechzahl ?? 0, schritt: 0.1, min: 0, leer: 0,
          titel: phiTitel,
          beiAenderung: (v) => aendern((q) => { q.zwaengung_biegung_kriechzahl = v; }),
        }),
      ]),
    }),
    zwaengung('zwaengung_begrenzt', 'Begrenzung auf 500 mm'),
  ];
}

/** Die Stahlspannung unter quasi-ständigen Lastfällen -- begrenzt aus der Rissbreite. */
export function quasistaendigInhalt(eintrag, ort = PLATTE) {
  return gebrauchsKapitel(eintrag, ort, {
    feld: 'quasistaendig', wort: 'quasi-ständig', neu: 'Quasi-ständig',
  });
}

/** Das Fliessen unter häufigen Lastfällen -- gefordert nur bei erhöhter und hoher Anforderung. */
export function haeufigInhalt(eintrag, ort = PLATTE) {
  return gebrauchsKapitel(eintrag, ort, {
    feld: 'haeufig', wort: 'häufig', neu: 'Häufig',
    // Bei normaler Anforderung steht in Tabelle 17 ein Strich: der
    // Nachweis entfällt, und damit auch alles, was unten eingetragen wird.
    // Ohne diesen Satz nimmt die Maske Lastfälle entgegen und rechnet sie
    // stillschweigend nicht -- man sucht das Ergebnis in der
    // Zusammenfassung und findet nichts. Was gefordert ist, sagt der Kern
    // über den Katalog; hier steht keine zweite Fassung der Norm. Nur
    // dieses Kapitel: das quasi-ständige läuft immer.
    hinweis: fliessenGefordert(eintrag) ? null
      : `Rissanforderung «${anforderung(eintrag)?.beschriftung ?? '–'}» → `
        + 'Tab. 17: kein Nachweis. Für den Nachweis oben «Erhöht» oder «Hoch» wählen.',
  });
}

/**
 * Ein Stahlspannungsnachweis unter Gebrauchslast: Rechenwahl, der Anteil
 * der Tragsicherheitseinwirkungen und die eigenen Lastfälle.
 *
 * Zweimal gebraucht -- quasi-ständig gegen die Rissbreite, häufig gegen das
 * Fliessen. Im Kern sind beide dieselbe Rechnung mit anderer Grenze, hier
 * dieselbe Maske mit anderen Feldern. Eine Kopie davon stünde in der
 * Oberfläche genau so, wie sie im Kern vermieden wurde.
 *
 * `feld` ist die Gebrauchsliste des Bauteils -- `haeufig` oder
 * `quasistaendig`, je mit `anteil`, `aus_tragsicherheit` und `faelle`. Was
 * ein Fall trägt und welche Rechenarten gelten, sagt `ort.gebrauch`: bei der
 * Platte M und N, beim gezeichneten Querschnitt N, M_y und M_z.
 *
 * Der Anteil steht in der Schalterzeile und nicht darunter: «[✓] [60] % der
 * Tragsicherheitseinwirkungen» liest sich als ein Satz, und man sieht beim
 * Einschalten, womit gerechnet wird. Seine Vorgabe kommt aus dem Kern -- die
 * Datei läuft beim Laden durch ihn und bringt den Wert immer mit.
 */
function gebrauchsKapitel(eintrag, ort, {
  feld, wort, neu, hinweis,
}) {
  const liste = eintrag[feld];
  const abgeleitet = !!liste.aus_tragsicherheit;
  const faelle = liste.faelle;
  const aendern = (veraenderer) => anBauteil(eintrag, ort)((e) => veraenderer(e[feld]));
  const spalten = ort.gebrauch.spalten(eintrag);

  return [
    rissanforderungZeile(eintrag, ort),
    hinweis ? el('p.hinweis.hinweis-annahme', { text: hinweis }) : null,
    rechenwahlZeile('Rechenwahl', liste.wahl,
      (veraenderer) => aendern((l) => veraenderer(l.wahl)), { arten: ort.gebrauch.arten }),

    el('div.duktilitaetszeile.ist-anteil', {}, [
      hakenSchalter(abgeleitet, (wert) => aendern((l) => {
        l.aus_tragsicherheit = wert;
      }), 'Ableitung'),
      zahlfeld({
        wert: liste.anteil, schritt: 5, min: 5, max: 100,
        titel: `Anteil der Tragsicherheitseinwirkungen als ${wort}, in %`,
        // Leer gelassen bleibt der bisherige Wert -- eine Null wäre kein
        // Anteil, und der Kern wiese sie ohnehin zurück.
        beiAenderung: (v) => aendern((l) => { l.anteil = v; }),
      }),
      el('span.postenname', { text: '% der Tragsicherheitseinwirkungen' }),
      el('span.kurvenhinweis', { text: '' }),
    ]),

    // Die abgeleiteten Fälle und eigene schliessen sich nicht aus: wer den
    // Anteil nimmt, kann trotzdem einen Fall von Hand dazustellen, den keine
    // Tragsicherheitskombination abbildet.
    faelle.length
      ? el('div.einwirkung.ist-kopf', { style: { '--felder': spalten.length } }, [
        el('span'),
        el('span', { text: 'Bezeichnung' }),
        ...spalten.map((s) => el('span', { text: s.kopf })),
        el('span'),
      ])
      : null,
    ...(faelle.length
      ? faelle.map((_, i) => gebrauchsfallZeile(eintrag, ort, spalten, feld, wort, i))
      : [el('div.leer', {
        text: abgeleitet
          ? 'Nur die abgeleiteten Fälle.'
          : `Noch kein ${wort}er Lastfall.`,
      })]),
    anfuegenKnopf('Lastfall', () => aendern((l) => {
      l.faelle.push(ausVorlage(ort.gebrauch.vorlage, { name: naechsterName(neu, l.faelle) }));
    })),
  ];
}

/** Ein Lastfall unter Gebrauchslast auf einer Zeile -- wie eine Einwirkung, ohne Querkraft. */
function gebrauchsfallZeile(eintrag, ort, spalten, feld, wort, index) {
  const k = eintrag[feld].faelle[index];
  const aendern = (veraenderer) => anBauteil(eintrag, ort)((e) => veraenderer(e[feld].faelle[index]));

  const aktiv = k.aktiv !== false;
  return el('div.einwirkung', {
    class: aktiv ? '' : 'ist-aus', style: { '--felder': spalten.length },
  }, [
    hakenSchalter(aktiv, (wert) => aendern((x) => { x.aktiv = wert; }), 'Lastfall'),
    el('input.ew-name', {
      type: 'text', value: k.name, title: `Bezeichnung des ${wort}en Lastfalls`,
      on: { change: (e) => aendern((x) => { x.name = e.target.value; }) },
    }),
    ...spalten.map((s) => zahlfeld({
      wert: k[s.feld], schritt: s.schritt, titel: s.titel(wort), leer: 0,
      beiAenderung: (v) => aendern((x) => { x[s.feld] = v; }),
    })),
    el('button.weg', {
      text: '×', title: `${wort[0].toUpperCase()}${wort.slice(1)}en Lastfall entfernen`,
      on: {
        click: () => anBauteil(eintrag, ort)((e) => { e[feld].faelle.splice(index, 1); }),
      },
    }),
  ]);
}

/**
 * «Automatische Bewehrung» -- die Bewehrung suchen lassen, statt sie zu setzen.
 *
 * Ein einzelner Knopf, kein Automatismus im Hintergrund: was hier
 * herauskommt, wird in die Lagen geschrieben und steht dann da wie eine
 * Eingabe von Hand -- man sieht es, kann es ändern und kann es lassen.
 * Eine Bewehrung, die sich bei jeder Zahl neu setzt, wäre keine Eingabe mehr.
 *
 * Gesucht wird gegen die Nachweise, die eingeschaltet sind. Die Schalter
 * weiter unten steuern damit unmittelbar, wonach gesucht wird.
 */
export function automatikInhalt(querschnitt) {
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
  return [el('div.automatik', {}, [
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
      wert: querschnitt.automatik_mindestdicke, schritt: 10, min: 10,
      titel: 'Dünner sucht die Dickenoptimierung keine Platte',
      beiAenderung: (v) => aendern((q) => { q.automatik_mindestdicke = v; }),
    }), 'mm')] : []),
    feld('Teilungen', teilungsfeld('automatik_teilungen',
      'mm, durch Komma getrennt. Grund und Zulage einer Lage: gleiche Teilung'), 'mm'),
    // Leer heisst: kein Mindestdurchmesser -- dann darf eine Lage leer
    // bleiben. Die Null zeigt das Feld darum als leer, und die Pfeile gehen
    // wie bei der Obergrenze durch die Durchmesser: von leer aus auf 2 mm
    // hiesse einen Stab, den es nicht gibt.
    feld('Mindestdurchmesser', zahlfeld({
      wert: querschnitt.automatik_mindestdurchmesser || null,
      stufen: zustand.katalog.durchmesser, min: 0,
      titel: 'Grundbew. jeder Lage mindestens mit diesem ⌀; leer: Lage darf leer bleiben',
      leer: 0,
      beiAenderung: (v) => aendern((q) => { q.automatik_mindestdurchmesser = v; }),
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
  ])];
}

/** Ob für diese Platte gerade gesucht wird -- der Knopf im Panel sagt es dann. */
export function sucheLaeuft(kennung) {
  return laufendeSuche.has(kennung);
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
        wert: posten.durchmesser || null, stufen: zustand.katalog.durchmesser, min: 0,
        titel: '⌀ in mm; Grund und Zulage leer: keine Obergrenze',
        leer: 0,
        beiAenderung: (v) => setzen('durchmesser', v),
      }),
      el('span.zeichen', { text: '@' }),
      zahlfeld({
        wert: posten.abstand, schritt: 25, min: 25, titel: 'Teilung in mm',
        beiAenderung: (v) => setzen('abstand', v),
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

/**
 * Einmal suchen und das Ergebnis in die Lagen schreiben.
 *
 * Die Lagen bleiben stehen, bis das Ergebnis da ist; dass gesucht wird,
 * zeigt der Laufbalken. Früher wurden sie zuerst geleert -- dafür musste
 * die Oberfläche wissen, welche Posten der Kern sucht, und wusste es bald
 * nicht mehr (die Anhebung der y-Lagen kam dort nie an). Was herauskam,
 * sagt jetzt die Meldung, auch wenn dieselben Durchmesser zurückkommen.
 */
async function bewehrungErmitteln(kennung) {
  laufendeSuche.add(kennung);
  aendern({}, 'bewehrungssuche-start');
  try {
    const antwort = await api.bewehrungSuchen(zustand.projekt, kennung);
    if (antwort.gefunden) {
      // Der Kern gibt das fertige Projekt zurück; übernommen wird die eine
      // gesuchte Platte, damit die anderen unberührt bleiben -- mit der
      // neuen Dicke, wenn sie gesucht wurde.
      projektAendern((p) => {
        const alt = p.querschnitte.findIndex((x) => x.kennung === kennung);
        const neu = antwort.projekt?.querschnitte?.find((x) => x.kennung === kennung);
        if (alt >= 0 && neu) p.querschnitte[alt] = neu;
      });
    }
    melden(antwort.begruendung, !antwort.gefunden);
  } catch (fehler) {
    melden(String(fehler.message || fehler), true);
  } finally {
    // Zuletzt und immer. Hing das Neuzeichnen am Zweig, blieb der Knopf auf
    // «sucht …» stehen, und man musste ein zweites Mal drücken.
    laufendeSuche.delete(kennung);
    aendern({}, 'bewehrungssuche-ende');
  }
}

/**
 * Wo die Kapitel eines Bauteils stehen und was bei ihm anders ist: die
 * Liste im Projekt, die Vorlage einer neuen Analyse und ihre Richtung -- bei
 * der Platte die Tragrichtung x oder y. Der gezeichnete Querschnitt hat seinen
 * eigenen Ort (`querschnittsanalyse.js`): dort ist die Richtung die Zugseite.
 * `raender(k)` sagt, wie die beiden Ränder einer Analyse heissen -- der
 * gedrückte und der gezogene. `zwang(e)`, `gebrauch` und `knick` sind, was
 * die Zwängung, die Stahlspannungen und das Knicken beim Bauteil anders
 * zeigen.
 */
export const PLATTE = {
  liste: 'querschnitte',
  vorlage: 'analyse',
  richtung: (k, setzen) => richtungsWahl(k.richtung || 'x', setzen, ['x', 'y']),
  raender: () => ['oben', 'unten'],
  // Die Zwängung: nur in Tragrichtung x.
  zwang: () => ({
    marke: () => el('span.richtung', {
      text: 'x', class: 'lage-x', title: 'Nur Tragrichtung x',
    }),
    hinweise: {},
    phiTitel: 'Kriechzahl φ der Zwängung auf Biegung: n = E_s/E_cm · (1 + φ)',
  }),
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

/**
 * Eine Art der Spannung-Dehnung-Analyse: die Bilder dieser Art, und ein
 * Knopf für ein weiteres.
 *
 * Kein Nachweis -- es wird nichts gegen etwas gehalten. Darum auch keine
 * Erfüllungsgrade in der Zusammenfassung; die Bilder stehen im eigenen
 * Reiter. Jede Art hat ihr Fenster, und was eine Zeile fragt, hängt an der
 * Art: eine Zeile, die nach N und M fragt, soll nicht daneben zwei
 * Dehnungsfelder zeigen, die sie nicht liest. Die Bilder aller Arten
 * stehen in einer Liste der Platte; jede Zeile behält ihre Stelle darin.
 */
export function analyseInhalt(eintrag, art, ort = PLATTE) {
  const stellen = (eintrag.spannungsfaelle || [])
    .map((k, i) => (k.art === art ? i : -1))
    .filter((i) => i >= 0);

  return [
    ...(stellen.length
      ? stellen.map((i) => spannungsZeile(eintrag, i, ort))
      : [el('div.leer', { text: 'Noch kein Bild.' })]),
    anfuegenKnopf('Bild', () => projektAendern((p) => {
      const e = p[ort.liste].find((x) => x.kennung === eintrag.kennung);
      e.spannungsfaelle = e.spannungsfaelle || [];
      e.spannungsfaelle.push(
        ausVorlage(ort.vorlage, { name: naechsterName('Bild', e.spannungsfaelle), art }));
    })),
  ];
}

/** Ein Feld mit seiner Beschriftung darüber -- eine Formel bleibt klein geschrieben. */
export function mitKopf(kopf, eingabe, formel = false) {
  return el('div.mit-kopf', {}, [
    el('span.spaltenkopf', { text: kopf, class: formel ? 'ist-formel' : '' }), eingabe,
  ]);
}

/**
 * Die Felder einer Rechenwahl: Kriechzahl φ, Werte und Rechenart -- in jedem
 * Kapitel und in jeder Analyse dieselben drei. `ziel` trägt die Felder
 * `kriechzahl`, `werkstoffsatz` und `rechenart`, `aendern` ändert es im
 * Projekt. `arten` sagt, welche Rechenarten gelten: `rechenarten`, bei den
 * Stahlspannungen `spannungsarten`, beim Knicken und in den Analysen
 * `faserarten` (ohne Handrechnung), bei der Verformung des Knickens
 * `verformungsarten` (nur präzise). Wirkt φ bei der gewählten Art
 * nicht, steht das Feld blass da -- es bleibt aber stehen, damit die Zahl
 * nicht verloren geht, wenn man die Art wieder wechselt. `phiImmer`: in den
 * Analysen rechnet der ungerissene Teil immer mit E_cm/(1+φ), dort wirkt φ
 * bei jeder Art.
 */
function rechenwahlFelder(ziel, aendern, { arten = 'rechenarten', phiImmer = false } = {}) {
  const katalog = zustand.katalog?.rechenwahl || {};
  const liste = katalog[arten] || [];
  const art = liste.find((a) => a.wert === ziel.rechenart);
  // In schmalen Zeilen stehen die kurzen Namen; der lange steht im Titel.
  const kurz = (l) => (l || []).map((e) => ({ wert: e.wert, beschriftung: e.kurz }));
  const phi = mitKopf('φ', zahlfeld({
    wert: ziel.kriechzahl ?? 0, schritt: 0.1, min: 0, leer: 0,
    titel: phiImmer
      ? 'Kriechzahl φ – wirkt auf den ungerissenen Teil, präzise auch auf den gerissenen'
      : 'Kriechzahl φ – wirkt präzise und elastisch',
    beiAenderung: (v) => aendern((x) => { x.kriechzahl = v; }),
  }), true);
  if (art && !art.mit_kriechzahl && !phiImmer) phi.classList.add('ist-ohne-wirkung');
  return [
    phi,
    mitKopf('Werte', auswahl({
      werte: kurz(katalog.werkstoffsaetze),
      gewaehlt: ziel.werkstoffsatz,
      titel: 'Bemessungswerte (f_cd, f_yd) oder charakteristische (f_ck, f_yk)',
      beiAenderung: (v) => aendern((x) => { x.werkstoffsatz = v; }),
    })),
    mitKopf('Rechenart', auswahl({
      werte: kurz(liste),
      gewaehlt: ziel.rechenart,
      titel: liste.map((a) => a.beschriftung).join(' · '),
      beiAenderung: (v) => aendern((x) => { x.rechenart = v; }),
    })),
  ];
}

/**
 * Eine Zeile «Rechenwahl» unter einem Kapitelkopf: ein kleiner Titel, darunter
 * die drei Felder. Beim Knicken stehen zwei solche Zeilen, mit «Verformung»
 * und «Widerstand» als Titel. `aendern` bekommt eine Funktion, die die Wahl
 * selbst ändert.
 */
function rechenwahlZeile(titel, ziel, aendern, optionen) {
  return el('div.rechenwahl', {}, [
    el('span.rechenwahl-titel', { text: titel }),
    ...rechenwahlFelder(ziel, aendern, optionen),
  ]);
}

/**
 * Eine Analyse als kleine Karte: oben der Name, darunter ihre Zahlen, φ und
 * die Richtung, zuunterst Werte und Rechenart. Die Zahlenfelder richten sich
 * nach der Art -- die steht über dem Fenster und wird hier nicht gewählt.
 */
function spannungsZeile(eintrag, index, ort) {
  const k = (eintrag.spannungsfaelle || [])[index];
  const liste = (p) => p[ort.liste].find((x) => x.kennung === eintrag.kennung).spannungsfaelle;
  const aendern = (veraenderer) => projektAendern((p) => veraenderer(liste(p)[index]));
  const [oben, unten] = ort.raender(k);
  const zahl = (feld, titel, schritt) => zahlfeld({
    wert: k[feld], schritt, titel, leer: 0,
    beiAenderung: (v) => aendern((x) => { x[feld] = v; }),
  });
  const aktiv = k.aktiv !== false;

  // Je Art andere Felder -- und immer zwei, damit die Zeilen untereinander
  // dieselbe Gestalt behalten.
  // Je Art andere Felder -- und andere Beschriftungen darüber. Ohne sie
  // stünden dort zwei namenlose Zahlen, und ob die erste eine Kraft oder
  // eine Dehnung ist, sähe man erst am Ergebnis.
  const kruemmung = {
    kopf: ['N_Ed [kN]', ''],
    felder: () => [
      zahl('N_Ed', 'Normalkraft in kN – Zug positiv', 50),
      el('span.kurvenhinweis', { text: '0 … M_Rd' }),
    ],
  };
  const dehnung = {
    kopf: ['M_Ed [kNm]', ''],
    felder: () => [
      zahl('M_Ed', 'Moment in kNm, festgehalten', 10),
      el('span.kurvenhinweis', { text: '0 … N_Rd' }),
    ],
  };
  const bauplan = {
    schnittgroessen: {
      kopf: ['N_Ed [kN]', 'M_Ed [kNm]'],
      felder: () => [
        zahl('N_Ed', 'Normalkraft in kN – Zug positiv', 50),
        zahl('M_Ed', 'Moment in kNm', 10),
      ],
    },
    dehnungen: {
      kopf: [`ε ${oben} [‰]`, `ε ${unten} [‰]`],
      felder: () => [
        zahl('eps_oben', `Randdehnung ${oben} in ‰ – Zug positiv`, 0.5),
        zahl('eps_unten', `Randdehnung ${unten} in ‰ – Zug positiv`, 0.5),
      ],
    },
    // Der äquivalente Modul läuft auf denselben Linien: dieselben Felder.
    moment_kruemmung: kruemmung,
    moment_emodul: kruemmung,
    normalkraft_dehnung: dehnung,
    normalkraft_emodul: dehnung,
  }[k.art];
  // Womit gerechnet wird -- je Analyse, wie in den Kapiteln, aber ohne
  // Handrechnung: eine Linie rechnet die Normalkraft genau.
  const [phi, werte, rechenart] = rechenwahlFelder(
    k, aendern, { arten: 'faserarten', phiImmer: true });

  return el('div.einwirkung.ist-spannung', { class: aktiv ? '' : 'ist-aus' }, [
    hakenSchalter(aktiv, (wert) => aendern((x) => { x.aktiv = wert; }), 'Analyse'),
    el('input.ew-name', {
      type: 'text', value: k.name, title: 'Bezeichnung der Analyse',
      on: { change: (e) => aendern((x) => { x.name = e.target.value; }) },
    }),
    // Beschriftung über dem Feld, nicht daneben: so bleibt das Raster der
    // Zeile dasselbe, gleich welche Art es ist.
    ...bauplan.felder().map((eingabe, i) => mitKopf(bauplan.kopf[i] || '', eingabe)),
    phi,
    ort.richtung(k, (wert) => aendern((x) => { x.richtung = wert; })),
    werte,
    rechenart,
    el('button.weg', {
      text: '×', title: 'Analyse entfernen',
      on: { click: () => projektAendern((p) => { liste(p).splice(index, 1); }) },
    }),
  ]);
}
