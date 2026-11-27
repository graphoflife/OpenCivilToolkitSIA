/**
 * qa_stabilitaet.js -- Knicken und Kippen eines Stabs mit dem gezeichneten Querschnitt.
 *
 * Eine Kachel je Bauweise: beim Stahl Knicken und Kippen nach SIA 263, je
 * Achse mit der Knickspannungskurve; beim Holz nach SIA 265, mit der
 * Dauer der Einwirkung je Fall; im Verbund die Verbundstütze nach
 * SIA 264, 5.3 -- davor die Kriechzahl des Betons, je Fall dazu der
 * ständige Anteil der Normalkraft und die Länge der Stütze statt der
 * Kipplänge. Die Fälle stehen in derselben Liste der Analyse
 * (`stabilitaetsfaelle`); welche Felder ein Fall zeigt, richtet sich nach
 * der Bauweise, die der Kern nennt.
 *
 * Gerechnet wird nichts: was einem Fall fehlt oder warum ein Querschnitt
 * keine Verbundstütze ist, sagt der Kern im Fall und in der Herleitung.
 */

import { feld, mitBild, wahlBlock, wahlSchalter } from './bausteine.js';
import { el, zahlfeld } from './dom.js';
import { anfuegenKnopf, fallkopf, fallzeile } from './faelle.js';
import { standOhne, zeilenstand } from './kapitel.js';
import { span } from './mathe.js';
import {
  HOLZ_RECHNET, ausHolz, biegungsWahl, dauerSchalter, imVerbund,
} from './qa_fallteile.js';
import { knickkurvenVon } from './qa_zeichnung.js';
import {
  ausVorlage, eintragAendern, feldangabe, katalog,
} from './zustand.js';

/** Was hinter den Fragezeichen steht -- je Bauweise. */
const HILFE = {
  stahl: {
    zeilen: [
      ['Klasse', 'im Fall aus c/t wie in der Tragsicherheit, bei N_Ed und den Momenten 1. Ordnung'],
      ['Knicken', 'je Achse χ_K aus der Schlankheit und der Kurve: N_K,Rd = χ_K · f_y · A / γ_M1 (7)'],
      ['Kippen', 'um die starke Achse, wo ein Moment um sie wirkt: M_cr nach Anhang B, η aus ψ; M_D,Rd = χ_D · W · f_y / γ_M1 (9)'],
      ['M-N', 'Klassen 1 bis 3 nach (50), ein I-Walzprofil auch nach (51) – es gilt die günstigere; Klasse 4 nach (62) und (63)'],
      ['L = 0', 'gehalten: um diese Achse knickt der Stab nicht, oder er kippt nicht'],
      ['ψ', 'Verhältnis der Endmomente, −1 bis 1: konstantes Moment 1; mit Querlast oder verschieblich ebenfalls 1'],
      ['α_eff', 'N_Ed bleibt, die Momente wachsen, bis die Gleichung aufgeht'],
    ],
    formel: 'N_Ed / N_K,Rd + Σ ω · M_Ed / ((1 − N_Ed / N_cr) · M_Rd) ≤ 1   (50)',
  },
  holz: {
    zeilen: [
      ['Knicken', 'je Achse k_c aus λ_rel = λ/π · √(f_c,0,k / E_0,05), (30) und (31)'],
      ['Kippen', 'nur ein Rechteck, wo ein Moment um die starke Achse wirkt: k_m aus σ_m,crit (39) bis (41)'],
      ['M-N', 'je Achse für sich: (29) mit Druck allein, (37) mit Druck und Biegung, (38) ohne Druck'],
      ['L = 0', 'gehalten: um diese Achse knickt der Stab nicht, oder er kippt nicht'],
      ['α_eff', 'N_Ed bleibt, die Momente wachsen, bis die Gleichung aufgeht'],
    ],
    formel: 'σ_c,0,d / (k_c · f_c,0,d) + σ_m,d / (k_m · f_m,d) ≤ 1   (37)',
  },
  verbund: {
    zeilen: [
      ['Art', 'ein I-Profil ganz einbetoniert oder kammerbetoniert, oder ein Rohr mit Beton gefüllt (Tabelle 7) – doppelsymmetrisch, 0.2 ≤ h/b ≤ 5 und 0.2 ≤ δ ≤ 0.9'],
      ['Knicken', 'die Achse ohne Moment: N_Ed ≤ χ_K · N_pl,Rd (15), λ̄ aus (EI)_eff mit 0.6 · E_c,eff (17), höchstens 2'],
      ['Biegung', 'die Achse mit Moment: M_Ed,II = k · M_Ed + k_0 · N_Ed · e_0, k nach (24), e_0 nach Tabelle 7 – gegen 0.9 · μ_d · M_pl,Rd (25), mit S420 und S460 0.8'],
      ['zweiachsig', 'beide Achsen linear zusammen (5.3.5): Σ M_Ed,II / (μ_d · M_pl,Rd) ≤ 0.9'],
      ['L', 'Länge der Stütze zwischen ihren seitlich unverschieblich gehaltenen Enden – für k und e_0'],
      ['φ', 'Kriechzahl des Betons: E_c,eff = E_cm / (1 + N_G,Ed/N_Ed · φ) (19)'],
      ['L_K = 0', 'gehalten: um diese Achse knickt die Stütze nicht, und ihr Moment wächst nicht'],
    ],
    formel: 'M_Ed,II / (μ_d · M_pl,Rd) ≤ 0.9   (25)',
  },
};

/** Was im Verbund über den Fällen steht: welche Querschnitte als Verbundstütze rechnen. */
const VERBUND_RECHNET = 'Als Verbundstütze rechnet ein einziges I-Profil oder Rohr der '
  + 'Profiltabelle: ganz einbetoniert, kammerbetoniert oder mit Beton gefüllt (Tabelle 7). Ihre '
  + 'Enden sind seitlich unverschieblich gehalten. Gerechnet wird mit den Rechenwerten der '
  + 'Tragsicherheit, der Beton im gefüllten Rohr mit 1.0 · f_cd.';

/**
 * Die Spalten eines Falls, in zwei Zeilen: oben die Druckkraft und die
 * Längen, unten die Momente mit ihrem ψ -- einachsig ohne M_z und ψ_z, beim
 * Holz ohne ψ (`ohneHolz`) und mit dem Titel `titelHolz`; im Verbund mit dem
 * ständigen Anteil und der Länge der Stütze (`nurVerbund`), ohne Kipplänge
 * (`ohneVerbund`). Eine Last, die man leert, ist keine Last; eine Länge, ein
 * Anteil oder ein ψ behält den bisherigen Wert, denn null heisst dort
 * etwas: gehalten, nichts ständig, ein dreieckiges Moment.
 */
const STABSPALTEN = [
  { feld: 'N_Ed', kopf: ['N_{Ed}', 'kN'], schritt: 50, leer: 0, titel: 'Normalkraft in kN – Druck negativ' },
  {
    feld: 'staendig', kopf: ['N_{G}/N', '%'], schritt: 10, nurVerbund: true,
    titel: 'Ständiger Anteil der Normalkraft N_G,Ed/N_Ed in % – er kriecht (SIA 264, (19))',
  },
  { feld: 'L_K_y', kopf: ['L_{K,y}', 'm'], schritt: 0.5, titel: 'Knicklänge um y in m – null: gehalten' },
  { feld: 'L_K_z', kopf: ['L_{K,z}', 'm'], schritt: 0.5, titel: 'Knicklänge um z in m – null: gehalten' },
  {
    feld: 'L_D', kopf: ['L_D', 'm'], schritt: 0.5, ohneVerbund: true,
    titel: 'Kipplänge in m: Abstand der Punkte, an denen der Druckgurt seitlich gehalten ist – null: gehalten',
    titelHolz: 'Kipplänge in m: Abstand der seitlichen Halterungen – null: gehalten',
  },
  {
    feld: 'L', kopf: ['L', 'm'], schritt: 0.5, nurVerbund: true,
    titel: 'Länge der Stütze in m, zwischen ihren seitlich gehaltenen Enden – für k (24) und die Imperfektion',
  },
  {
    feld: 'M_y_Ed', kopf: ['M_{y,Ed}', 'kNm'], schritt: 10, leer: 0,
    titel: 'Grösstes Moment 1. Ordnung um y im Stab, in kNm – positiv: Zug unten',
  },
  {
    feld: 'psi_y', kopf: [String.raw`\psi_y`], schritt: 0.25, ohneHolz: true,
    titel: 'Verhältnis der Endmomente um y, −1 bis 1 – konstantes Moment, Querlast oder verschieblich: 1',
  },
  {
    feld: 'M_z_Ed', kopf: ['M_{z,Ed}', 'kNm'], schritt: 10, leer: 0, zweiachsig: true,
    titel: 'Grösstes Moment 1. Ordnung um z im Stab, in kNm – positiv: Zug links',
  },
  {
    feld: 'psi_z', kopf: [String.raw`\psi_z`], schritt: 0.25, zweiachsig: true, ohneHolz: true,
    titel: 'Verhältnis der Endmomente um z, −1 bis 1 – konstantes Moment, Querlast oder verschieblich: 1',
  },
];

function stabspalten(analyse) {
  const holz = ausHolz(analyse);
  const verbund = imVerbund(analyse);
  return STABSPALTEN
    .filter((s) => !(analyse.einachsig && s.zweiachsig) && !(holz && s.ohneHolz)
      && !(verbund ? s.ohneVerbund : s.nurVerbund))
    .map((s) => (holz && s.titelHolz ? { ...s, titel: s.titelHolz } : s));
}

/** Wie viele Spalten die obere Zeile hat: die Druckkraft und die Längen, bis zu den Momenten. */
function obenSpalten(analyse) {
  return stabspalten(analyse).findIndex((s) => s.feld === 'M_y_Ed');
}

/**
 * Knicken und Kippen: die Wahl der Biegung wie in der Tragsicherheit, beim
 * Stahl je Achse die Knickspannungskurve, darunter die Fälle. Was einem Fall
 * noch fehlt, sagt der Kern mit demselben Satz wie in der Herleitung
 * (`knickkurvenVon`). Das Holz knickt nach einer festen Kurve: dort steht
 * statt der Kurven, wie es rechnet. Die Verbundstütze nimmt ihre Kurven aus
 * Tabelle 7: dort steht die Kriechzahl und welche Querschnitte sie rechnet.
 */
function stabilitaetsAngaben(analyse) {
  const aendern = (veraenderer) => eintragAendern(analyse.kennung, veraenderer);
  const faelle = analyse.stabilitaetsfaelle || [];
  const holz = ausHolz(analyse);
  const verbund = imVerbund(analyse);
  const stahl = !holz && !verbund;
  const { eigene, fehlen } = knickkurvenVon(analyse.kennung);
  const spalten = obenSpalten(analyse);
  return [
    biegungsWahl(analyse),
    ...(stahl ? ['y', 'z'].map((achse) => kurvenwahl(analyse, achse, eigene)) : []),
    fehlen && stahl ? el('p.hinweis', { text: fehlen }) : null,
    verbund ? kriechzahl(analyse) : null,
    el('p.qa-erlaeuterung', {
      text: (holz && HOLZ_RECHNET) || (verbund && VERBUND_RECHNET)
        || 'Gerechnet mit den Rechenwerten der Tragsicherheit.',
    }),
    faelle.length ? fallkopf(stabspalten(analyse).map((s) => s.kopf), { spalten }) : null,
    ...(faelle.length
      ? faelle.map((_, i) => stabilitaetsZeile(analyse, i, spalten))
      : [el('div.leer', { text: 'Ohne Fall kein Nachweis.' })]),
    anfuegenKnopf('Stabilitätsnachweis', (name) => aendern((a) => {
      a.stabilitaetsfaelle = a.stabilitaetsfaelle || [];
      a.stabilitaetsfaelle.push(ausVorlage('qastabilitaet', { name: name(a.stabilitaetsfaelle) }));
    })),
  ];
}

/**
 * Die Knickspannungskurve um eine Achse: ein Schalter, je Stellung ihr
 * Bild. Darunter klein, welche Kurve das Profil hat und warum -- oder dass
 * es keines gibt, wo die Kurve aus ihm kommen soll.
 */
function kurvenwahl(analyse, achse, eigene) {
  const feldname = `knickkurve_${achse}`;
  const gewaehlt = analyse[feldname] || 'profil';
  const block = wahlBlock(`Knickspannungskurve um ${achse}`, wahlSchalter({
    werte: mitBild(katalog('querschnittsanalyse', 'knickkurven'), 'knickkurve'),
    gewaehlt,
    setzen: (wert) => eintragAendern(analyse.kennung, (a) => { a[feldname] = wert; }),
    titel: `Knickspannungskurve um ${achse} nach Figur 7: aus dem Profil oder gewählt`,
  }));
  if (gewaehlt === 'profil') {
    const profil = eigene?.[achse];
    block.append(el('p.qa-erlaeuterung', {
      text: profil ? `Kurve ${profil.kurve}: ${profil.grund}`
        : 'Ohne einzelnes Profil gibt Figur 7 keine Kurve.',
    }));
  }
  return block;
}

/** Im Verbund: die Kriechzahl des Betons, einmal für alle Fälle der Stütze. */
function kriechzahl(analyse) {
  const angabe = feldangabe('querschnittsanalyse', 'stuetze_kriechzahl');
  const titel = 'Kriechzahl φ(t,t_0) des Betons für die Verbundstütze – null rechnet ohne '
    + 'Kriechen (SIA 264, (19))';
  return feld(['Kriechzahl ', span(String.raw`\varphi`)], zahlfeld({
    wert: analyse.stuetze_kriechzahl, schritt: 0.5, angabe, titel,
    beiAenderung: (v) => eintragAendern(analyse.kennung, (a) => { a.stuetze_kriechzahl = v; }),
  }), angabe.einheit, titel);
}

function stabilitaetsZeile(analyse, index, spalten) {
  const fall = analyse.stabilitaetsfaelle[index];
  const aendern = (veraenderer) => eintragAendern(analyse.kennung,
    (a) => veraenderer(a.stabilitaetsfaelle[index]));
  return fallzeile({
    fall, aendern, was: 'Stabilitätsnachweis', nameTitel: 'Bezeichnung des Falls',
    liste: { kennung: analyse.kennung, pfad: 'stabilitaetsfaelle', index },
    unten: ausHolz(analyse) ? [dauerSchalter(fall, aendern)] : null,
    zahlen: stabspalten(analyse).map((s) => zahlfeld({
      wert: fall[s.feld], schritt: s.schritt, titel: s.titel, leer: s.leer,
      angabe: feldangabe('qastabilitaet', s.feld),
      beiAenderung: (v) => aendern((x) => { x[s.feld] = v; }),
    })),
    spalten,
    entfernenTitel: 'Fall entfernen',
    entfernen: () => eintragAendern(analyse.kennung, (a) => {
      a.stabilitaetsfaelle.splice(index, 1);
    }),
  });
}

/** Wie viele Fälle die Kachel hat -- für ihren Kurzstand. */
function faellestand(analyse) {
  return zeilenstand(analyse.stabilitaetsfaelle, 'Fall', 'Fälle', 'kein Fall');
}

/**
 * Knicken und Kippen eines Stabs mit dem gezeichneten Querschnitt, nach
 * SIA 263. Der Kachel fehlt etwas, solange einem Fall eine Kurve fehlt.
 */
export const STABILITAET = {
  schluessel: 'stabilitaet',
  name: 'Knicken und Kippen', titel: 'Knicken und Kippen nach SIA 263',
  bezug: () => 'N negativ: Druck · eine Länge null heisst gehalten',
  hilfe: HILFE.stahl,
  inhalt: stabilitaetsAngaben,
  stand: (a) => standOhne(faellestand(a), knickkurvenVon(a.kennung).fehlen ? 'Knickkurve fehlt' : ''),
};

/** Dieselbe Kachel für einen Querschnitt aus Holz, nach SIA 265. */
export const STABILITAET_HOLZ = {
  ...STABILITAET, titel: 'Knicken und Kippen nach SIA 265', hilfe: HILFE.holz, stand: faellestand,
};

/** Dieselbe Kachel für einen Querschnitt im Verbund: die Verbundstütze nach SIA 264. */
export const STABILITAET_VERBUND = {
  ...STABILITAET, name: 'Verbundstütze', titel: 'Verbundstütze nach SIA 264',
  bezug: () => 'N negativ: Druck · eine Knicklänge null heisst gehalten',
  hilfe: HILFE.verbund, stand: faellestand,
};
