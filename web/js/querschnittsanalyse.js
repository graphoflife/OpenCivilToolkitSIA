/**
 * querschnittsanalyse.js -- Mittlere Tafel: Eingaben einer Querschnittsanalyse.
 *
 * Oben der Querschnitt: Bezeichnung, Zeichnung samt Liste, Beschreibung.
 * Darunter die Kapitel als Knöpfe, wie bei der Platte (`kapitel.js`); ein
 * Klick öffnet das Fenster mit den Eingaben. Ins Fenster der Tragsicherheit
 * gehört, womit sie rechnet: die Rechenwerte je Material, die Lastfälle und
 * die Angaben der Schubwände -- Duktilität und sprödes Versagen rechnen am
 * selben Querschnitt.
 *
 * Ein Querschnitt aus Stahl hat dazu Knicken und Kippen nach SIA 263, einer
 * aus Holz nach SIA 265, einer im Verbund die Verbundstütze nach SIA 264
 * (qa_stabilitaet.js). Einer aus Holz hat davor die Feuchteklasse, je Fall
 * dazu, ob die Einwirkung stossartig ist. Einer im Verbund hat davor die
 * Verdübelung, mit Kopfbolzendübeln je Lastfall dazu, wie viele bis zum
 * Momentennullpunkt sitzen. Eine Blechverbunddecke hat davor den
 * Längsschub (qa_laengsschub.js); ihre Lastfälle haben nur N, M_y und V_z,
 * denn sie trägt in einer Richtung.
 *
 * Wie bei der Platte steht oben, was der Querschnitt *ist*, und in den
 * Fenstern, was von ihm *verlangt* wird. Gerechnet wird nichts: jede Zeile
 * beschreibt eine Eingabe, die Zahlen dazu bildet der Kern.
 *
 * VORZEICHEN: N > 0 Zug. Ein positives Moment zieht auf der negativen Seite
 * seiner Achse -- M_y > 0 unten, M_z > 0 links. V_y und V_z wirken in
 * Achsrichtung, T im Gegenuhrzeigersinn. Das kleine Bild neben den
 * Lastfällen zeigt es.
 */

import {
  beschreibung, bezeichnung, erklaerung, feld, hakenSchalter, mitBild, panel, wahlBlock,
  wahlSchalter,
} from './bausteine.js';
import { el, svgEl, zahlfeld } from './dom.js';
import { anfuegenKnopf, fallkopf, fallzeile } from './faelle.js';
import {
  kapitelFenster, kapitelPanel, zeilenstand,
} from './kapitel.js';
import { span } from './mathe.js';
import {
  analysenKapitel, mitKopf, nachweisKapitel, werkstoffzeilen,
} from './nachweise.js';
import {
  HOLZ_RECHNET, ausHolz, biegungsWahl, dauerSchalter, imBlechverbund, imVerbund,
} from './qa_fallteile.js';
import { LAENGSSCHUB } from './qa_laengsschub.js';
import { AUS_SYSTEM, stellenVon } from './qa_aus_system.js';
import { SCHUBFLUSS } from './qa_schubfluss.js';
import { STABILITAET, STABILITAET_HOLZ, STABILITAET_VERBUND } from './qa_stabilitaet.js';
import { uebersicht } from './qa_uebersicht.js';
import {
  bauweiseVon, ohneAnalysenVon, ohneNachweiseVon, werkstoffeVon, zeichenbereich,
} from './qa_zeichnung.js';
import {
  ausVorlage, eintragAendern, feldangabe, katalog,
} from './zustand.js';

/**
 * Was hinter den Fragezeichen steht -- Stichworte wie bei der Platte.
 * Knicken und die beiden Stahlspannungen rechnet die Platte gleich: dort
 * steht hier nur, was beim gezeichneten Querschnitt dazukommt, das Übrige
 * steht bei den Kapiteln (`nachweisKapitel` in nachweise.js).
 */
const HILFE = {
  tragsicherheit: {
    zeilen: [
      ['M-N', 'Dehnungsebene über Fasern; schief: die Nulllinie dreht, bis M_Rd in Richtung M_Ed zeigt'],
      ['V+T', 'elastisch auf die Schubwände verteilt (Federn b_w·l), Zellen nach Bredt; je Wand Fachwerk'],
      ['Werte', 'je Material nach Wahl, oben in diesem Fenster'],
    ],
    formel: 'α_eff = Widerstand / Einwirkung ≥ 1',
  },
  tragsicherheitStahl: {
    zeilen: [
      ['Klasse', 'je Blech jedes Profils aus c/t, im Lastfall; frei gezeichnet und gedrückt höchstens 3'],
      ['M-N', 'Klasse 1 und 2 plastisch, die Nulllinie dreht, bis M_Rd in Richtung M_Ed zeigt; 3 elastisch (54); 4 am wirksamen Querschnitt (60)'],
      ['V', 'je Richtung gegen V_Rd der Profile; über der Hälfte von V_Rd tragen die Bleche, in denen sie steht, für M-N nur noch 1 − (V/V_Rd)²'],
      ['T', 'nicht nachgewiesen – SIA 263 nennt keinen Torsionswiderstand des Querschnitts'],
      ['Werte', 'je Baustahl nach Wahl, oben in diesem Fenster'],
    ],
    formel: 'α_eff = Widerstand / Einwirkung ≥ 1',
  },
  tragsicherheitVerbund: {
    zeilen: [
      ['Klasse', 'je Blech jedes Profils aus c/t an der plastischen Nulllinie des Lastfalls; über Klasse 2 rechnet der Verbund noch nicht'],
      ['Kammerbeton', 'deckt Beton im I-Profil den Flansch innen oder den Steg beidseits, gelten die Grenzen der Tabelle 3 und von 5.2.1.3'],
      ['M-N', 'plastisch: der Beton mit 0.85 · f_cd und nur auf Druck; die Nulllinie dreht, bis M_Rd in Richtung M_Ed zeigt'],
      ['Dübel', 'mit Kopfbolzendübeln je Lastfall: η = N · P_Rd / |N_c,f| gegen η_min (29); reichen sie nicht für die volle Verdübelung, rechnet M-N mit Teilverdübelung (6.1.1.6)'],
      ['β', 'Baustahl S420 und S460: M_pl,Rd mal β, wenn x_p/h über 0.15 liegt (Figur 1)'],
      ['Betonstahl', 'zieht ihn ein Moment, rechnet es plastisch nur mit Klasse B oder C (5.1.2.3)'],
      ['V', 'der Stahl allein, je Richtung gegen V_Rd der Profile; über der Hälfte von V_Rd tragen die Bleche, in denen sie steht, für M-N nur noch 1 − (V/V_Rd)²'],
      ['T', 'nicht nachgewiesen'],
      ['Werte', 'je Material nach Wahl, oben in diesem Fenster'],
    ],
    formel: 'α_eff = Widerstand / Einwirkung ≥ 1',
  },
  tragsicherheitBlech: {
    zeilen: [
      ['Richtung', 'die Decke trägt in Richtung ihrer Rippen: N, M_y und V_z über die ganze Breite b (5.4.1.1)'],
      ['M-N', 'plastisch wie der Verbundträger: der Beton mit 0.85 · f_cd nur gedrückt, Blech und Betonstahl gezogen; bei negativem Moment ohne das Blech (5.4.3.2)'],
      ['V', 'V_Rd = k_d · τ_cd · d_p · b_0 / b_s je Breite, mit k_d = 0.8 bis d_p = 150 mm (26) – darüber grau'],
      ['Längsschub', 'V_L,Rd nach der m-k-Methode (28) – was er braucht, steht in der Kachel «Längsschub»'],
      ['Werte', 'je Material nach Wahl, oben in diesem Fenster'],
    ],
    formel: 'α_eff = Widerstand / Einwirkung ≥ 1',
  },
  tragsicherheitHolz: {
    zeilen: [
      ['σ', 'linear am Bruttoquerschnitt: N/A, je Achse M/W an der weitesten Faser'],
      ['M-N', 'Zug (6), Druck (10), Biegung (14), Biegung mit Zug (21) oder mit Druck (22)'],
      ['V+T', 'τ = V·S/(I·b) nach Jourawski; Torsion nur am Rechteck – (23), (24), (25)'],
      ['k_h', 'Brettschichtholz unter 600 mm Höhe: f_m,d um y mal k_h (5)'],
      ['η', 'η_w der Feuchteklasse, mal η_t = 1.4 in einem stossartigen Fall (2.2.6)'],
    ],
    formel: 'α_eff = Widerstand / Einwirkung ≥ 1',
  },
  verduebelung: {
    zeilen: [
      ['voll', 'Stahl und Beton tragen zusammen, ohne Schlupf (5.1.2.1); ob Dübel dafür reichen, prüft das Werkzeug dann nicht'],
      ['P_Rd', 'je Kopfbolzendübel der kleinere aus Betonstauchung (30) und Versagen des Dübels (31), mit γ_v = 1.25'],
      ['N', 'je Lastfall: die Dübel zwischen seinem Schnitt und dem nächsten Momentennullpunkt'],
      ['η', 'N · P_Rd gegen die Kraft im Beton bei voller Verdübelung: η = N / N_f'],
      ['η_min', 'positives Moment und ein doppelsymmetrisches Profil: (29) mit L_e, dem Abstand der Momentennullpunkte; sonst 1 – negativ ist ein Moment, das die Seite des Betons zieht'],
      ['teilweise', 'unter der vollen Verdübelung trägt der Beton nur N · P_Rd: Beton und Stahl je mit ihrer Nulllinie (6.1.1.6)'],
    ],
    formel: 'P_Rd = min(0.29 · d² · √(f_ck · E_cm); 0.8 · f_u · π · d²/4) / γ_v',
  },
  feuchteklasse: {
    zeilen: [
      ['Klasse', 'wie feucht das Holz im Bauwerk im Mittel ist – SIA 265, Tabelle 3'],
      ['η_w', 'mindert jeden Bemessungswert des Holzes: 1.0, 0.8, 0.6 – Tabelle 4'],
      ['Analysen', 'die Spannung-Dehnung-Analysen rechnen ohne η_w'],
    ],
  },
  duktilitaet: {
    zeilen: [
      ['Weg', 'reine Biegung (N = 0) je Richtung: Zug unten, oben, links, rechts'],
      ['x, d', 'senkrecht zur Nulllinie, ab dem gedrücktesten Betonpunkt; d bis zum Schwerpunkt der gezogenen Stäbe'],
      ['einachsig', 'nur Zug unten und oben'],
    ],
    formel: 'x/d ≤ k·435/f_yd',
  },
  sproede: {
    zeilen: [
      ['Weg', 'M_Rd bei N = 0 je Richtung gegen das Rissmoment des Bruttoquerschnitts'],
      ['Werte', 'M_Rd nach Werkstoffwahl, M_Riss mit f_ct,eff = k_t·f_ctm'],
    ],
    formel: 'M_Rd(N = 0) ≥ M_Riss = f_ct,eff · W',
  },
  knicken: {
    zeilen: [
      ['Richtung', 'je Fall zur gewählten Zugseite'],
      ['d', 'vom gedrückten Rand bis zum entferntesten Stab in Zugrichtung'],
    ],
  },
  zwang: {
    zeilen: [
      ['Normalkraft', 'der ganze Querschnitt reisst: Σ A_c·k_t·f_ctm, t = kleinere Abmessung; gegen alle Stäbe'],
      ['500 mm', 'nur massige Bauteile: Beton bis 250 mm vom Rand, k_t für 500 mm (SIA 262:2025, 4.4.2.3.7)'],
      ['Biegung', 'je Richtung M_Riss wie beim spröden Versagen, gegen das Moment, bei dem der erste gezogene Stab σ_s,adm erreicht – gerissen, präzise, eigenes φ'],
      ['σ_s,adm', 'je Stab nach Tab. 17 mit seinem ⌀; verschmiert: fiktiver ⌀ bei 150 mm Teilung'],
    ],
    formel: 'Σ A_s·σ_s,adm ≥ N_Riss    M_s,adm ≥ M_Riss',
  },
  quasistaendig: {
    zeilen: [
      ['Weg', 'Ebene am gerissenen Querschnitt; schief dreht die Nulllinie, bis N, M_y und M_z stimmen'],
      ['Grenze', 'je gezogenem Stab aus der Rissbreite, mit seinem ⌀; massgebend der kleinste Erfüllungsgrad'],
    ],
  },
  haeufig: {
    zeilen: [
      ['Weg', 'Ebene am gerissenen Querschnitt, wie quasi-ständig'],
    ],
  },
  schubwaende: {
    zeilen: [
      ['Wand', 'eine Linie über dem Querschnitt, Länge = Hebelarm'],
      ['α', 'ganzgradig zwischen α_min und α_max; bei Normalzug α_min mindestens 40°'],
      ['Längszug', 'ΔN = |V|·cot α je Wand, in der Wandmitte; geht in M-N ein'],
    ],
    formel: 'V_Rd = min(A_sw/s·l·f_yd·cot α ; b_w·l·k_c·f_cd·sin α·cos α)',
  },
};

/**
 * Die Spalten eines Lastfalls. `zweiachsig`: nur bei schiefer Biegung --
 * einachsig zählen M_z und V_y nicht, also stehen sie auch nicht da.
 * `torsion`: was eine Blechverbunddecke nicht trägt, wie M_z und V_y.
 */
const SPALTEN = [
  { feld: 'N_Ed', symbol: 'N', schritt: 50, titel: 'Normalkraft in kN – Zug positiv' },
  { feld: 'M_y_Ed', symbol: 'M_y', schritt: 10, titel: 'Moment um y in kNm – positiv: Zug unten' },
  {
    feld: 'M_z_Ed', symbol: 'M_z', schritt: 10, zweiachsig: true,
    titel: 'Moment um z in kNm – positiv: Zug links',
  },
  {
    feld: 'V_y_Ed', symbol: 'V_y', schritt: 10, zweiachsig: true,
    titel: 'Querkraft in y in kN – positiv nach rechts',
  },
  { feld: 'V_z_Ed', symbol: 'V_z', schritt: 10, titel: 'Querkraft in z in kN – positiv nach oben' },
  {
    feld: 'T_Ed', symbol: 'T', schritt: 5, torsion: true,
    titel: 'Torsion in kNm – positiv im Gegenuhrzeigersinn',
  },
];

/**
 * Die Spalten der Lastfälle einer Analyse. Eine Blechverbunddecke trägt
 * nur N, M_y und V_z (5.4.1.1): M_z, V_y und T stehen bei ihr nur da,
 * solange ein Lastfall dort noch eine Zahl hat -- der Kern meldet sie gelb,
 * und hier lässt sie sich löschen.
 */
function spalten(analyse) {
  if (imBlechverbund(analyse)) {
    return SPALTEN.filter((s) => !(s.zweiachsig || s.torsion)
      || analyse.lastfaelle.some((fall) => fall[s.feld]));
  }
  return SPALTEN.filter((s) => !(analyse.einachsig && s.zweiachsig));
}

/** Was im Verbund unter den Werten je Material steht: der Beton rechnet immer gleich. */
const VERBUND_RECHNET = 'Im Verbund rechnet der Querschnitt plastisch: der Beton mit 0.85 · f_cd '
  + 'über die ganze Druckzone und ohne Zug, Baustahl und Betonstahl mit ihrer Fliessgrenze '
  + '(SIA 264, 5.1.2.1). Eine Rechenart des Betons gibt es darum hier nicht.';

/** Dasselbe in einer Blechverbunddecke -- mit dem Blech. */
const BLECH_RECHNET = 'Die Blechverbunddecke rechnet plastisch wie der Verbundträger: der Beton '
  + 'mit 0.85 · f_cd über die ganze Druckzone und ohne Zug, Betonstahl und Blech mit ihrer '
  + 'Fliessgrenze – das Blech nur gezogen und bei negativem Moment gar nicht (SIA 264, 5.4.3.2). '
  + 'Eine Rechenart des Betons gibt es darum hier nicht.';

/** Wo der Beton immer plastisch rechnet, je Bauweise: was dann unter den Werten steht. */
const PLASTISCH = { verbund: VERBUND_RECHNET, blechverbund: BLECH_RECHNET };

/** Ob im Verbund mit Kopfbolzendübeln gerechnet wird -- sonst gilt die Verdübelung als voll. */
function mitDuebeln(analyse) {
  return imVerbund(analyse) && analyse.verduebelung === 'kopfbolzen';
}

/**
 * Im Verbund mit Kopfbolzendübeln, je Lastfall: wie viele Dübel zwischen
 * seinem Schnitt und dem nächsten Momentennullpunkt sitzen -- N in (29) --
 * und wie weit die Momentennullpunkte auseinander liegen, L_e. Leer,
 * solange nichts angegeben ist: dann sagt der Nachweis grau, was fehlt --
 * nur wo er es braucht, ohne Moment etwa nicht.
 */
function duebelzeile(fall, aendern) {
  const zahl = (feld, titel) => zahlfeld({
    wert: fall[feld], leer: null, titel,
    angabe: feldangabe('qalastfall', feld),
    beiAenderung: (v) => aendern((x) => { x[feld] = v; }),
  });
  return el('div.qa-duebelzeile', {}, [
    el('span.postenname', { text: 'Dübel bis zum Momentennullpunkt' }),
    zahl('duebelzahl', 'Kopfbolzendübel zwischen diesem Schnitt und dem nächsten '
      + 'Momentennullpunkt – N in (29)'),
    el('span'),
    el('span.postenname', {}, ['Abstand der Momentennullpunkte ', span('L_e')]),
    zahl('L_e', 'Abstand der Momentennullpunkte – im positiven Moment bestimmt er den kleinsten '
      + 'Verdübelungsgrad (29)'),
    el('span.einheit', { text: feldangabe('qalastfall', 'L_e').einheit }),
  ]);
}

// ===========================================================================
// Querschnitt
// ===========================================================================

function querschnittGruppe(analyse) {
  const aendern = (veraenderer) => eintragAendern(analyse.kennung, veraenderer);
  return panel({
    schluessel: 'analyse/Querschnitt', titel: 'Querschnitt', zusatz: 'y nach rechts, z nach oben, mm',
    breit: true,
  }, [
    bezeichnung(analyse, aendern),
    zeichenbereich(analyse, uebersicht),
    el('div.unterkapitel', {}, [
      // Freier Text, der in keine Rechnung eingeht -- wie bei der Platte.
      beschreibung(analyse, aendern, { stil: { marginTop: 0 } }),
    ]),
  ]);
}

// ===========================================================================
// Tragsicherheit
// ===========================================================================

/**
 * Womit die Tragsicherheit rechnet: je Material im Querschnitt seine Werte,
 * beim Beton dazu seine Rechenart -- dieselben Zeilen wie die Rechenwahl
 * jedes Moduls (`werkstoffzeilen`), ohne Kriechzahl: der Bruch rechnet ohne
 * Kriechen. Duktilität und sprödes Versagen rechnen am selben Querschnitt.
 * Im Verbund und in der Blechverbunddecke rechnet der Beton immer
 * plastisch: dort steht statt seiner Rechenart, wie (`PLASTISCH`).
 */
function rechenwahl(analyse) {
  const plastisch = PLASTISCH[bauweiseVon(analyse.kennung)];
  return el('div.rechenwahl', {}, [
    el('span.rechenwahl-titel', { text: 'Rechenwahl' }),
    werkstoffzeilen(analyse, (veraenderer) => eintragAendern(analyse.kennung, veraenderer), {
      ...werkstoffeVon(analyse.kennung), klasse: 'querschnittsanalyse', mitRechenart: !plastisch,
    }),
    plastisch ? el('p.qa-erlaeuterung', { text: plastisch }) : null,
  ]);
}

/**
 * Was allein Querkraft und Torsion brauchen -- die Schubwände rechnen damit,
 * und mit ihnen die Längszugkraft, wenn sie zählt.
 */
function schubwandAngaben(analyse) {
  const aendern = (veraenderer) => eintragAendern(analyse.kennung, veraenderer);
  return el('div.unterkapitel', {}, [
    el('div.unterkapitel-kopf', {}, [el('span', { text: 'Querkraft und Torsion: Fachwerk je Wand' }),
      erklaerung(HILFE.schubwaende.zeilen, HILFE.schubwaende.formel)]),
    el('div.neigungszeile', {}, [
      el('span.postenname', { text: 'Neigung' }),
      ...[['alpha_min', String.raw`\alpha_{min}`,
        'Kleinste Neigung der Druckdiagonalen, ganze °; bei Normalzug mindestens 40°'],
      ['alpha_max', String.raw`\alpha_{max}`, 'Grösste Neigung der Druckdiagonalen, ganze °'],
      ].flatMap(([schluessel, symbol, titel]) => {
        const angabe = feldangabe('querschnittsanalyse', schluessel);
        return [
          span(symbol),
          zahlfeld({
            wert: analyse[schluessel], angabe, neben: analyse, titel,
            beiAenderung: (v) => aendern((a) => { a[schluessel] = v; }),
          }),
          el('span.einheit', { text: angabe.einheit }),
        ];
      }),
    ]),
    feld(['Druckdiagonale ', span('k_c')], zahlfeld({
      wert: analyse.k_c, schritt: 0.05, angabe: feldangabe('querschnittsanalyse', 'k_c'),
      titel: 'Abminderung f_cd in der Druckdiagonalen',
      beiAenderung: (v) => aendern((a) => { a.k_c = v; }),
    }), '', 'Abminderung f_cd in der Druckdiagonalen'),
    el('div.duktilitaetszeile.ist-breit', {}, [
      hakenSchalter(!!analyse.laengszugkraft,
        (wert) => aendern((a) => { a.laengszugkraft = wert; }), 'Längszugkraft'),
      el('span.postenname', { text: 'Längszugkraft aus Querkraft und Torsion berücksichtigen' }),
      el('span'),
    ]),
  ]);
}

/**
 * Tragsicherheit: womit gerechnet wird und die Lastfälle -- beim Stahlbeton
 * dazu, was Querkraft und Torsion brauchen (`schubwandAngaben`). Das Holz
 * hat keine Wahl, wie es rechnet; dort steht, wie. Stahl und Verbund wählen
 * die Werte je Material. Eine Blechverbunddecke trägt in einer Richtung:
 * statt der Wahl der Biegung steht, was sie trägt -- vom Kern --, und das
 * Bild der Vorzeichen hat weder M_z noch V_y noch T.
 */
function lastfallAngaben(analyse) {
  const aendern = (veraenderer) => eintragAendern(analyse.kennung, veraenderer);
  const faelle = analyse.lastfaelle;
  const decke = imBlechverbund(analyse);
  return [
    ausHolz(analyse) ? el('p.qa-erlaeuterung', { text: HOLZ_RECHNET }) : rechenwahl(analyse),
    el('div.qa-kopfzeile', {}, [
      el('div.qa-schalter', {}, [decke
        ? el('p.qa-erlaeuterung', { text: katalog('querschnittsanalyse', 'blechdecke').richtung })
        : biegungsWahl(analyse)]),
      vorzeichenbild(analyse.einachsig || decke, { torsion: !decke }),
    ]),
    faelle.length ? lastfallKopf(analyse) : null,
    ...(faelle.length
      ? faelle.map((_, i) => lastfallZeile(analyse, i))
      : [el('div.leer', { text: 'Ohne Lastfall kein Nachweis.' })]),
    anfuegenKnopf('Lastfall', (name) => aendern((a) => a.lastfaelle.push(
      ausVorlage('qalastfall', { name: name(a.lastfaelle) })))),
  ];
}

/** In welchen Richtungen Duktilität, sprödes Versagen und Zwängung auf Biegung geführt werden. */
function richtungstext(analyse) {
  return analyse.einachsig ? 'Zug unten und oben' : 'Zug unten, oben, links, rechts';
}

/**
 * Ein Lastfall: Schalter, Name, die Schnittgrössen, Entfernen. Alle sechs
 * stehen auf einer Zeile, N bis T; das Fenster ist dafür breit (Benutzer,
 * 2026-11-20 -- bis dahin drei je Zeile). Reicht der Platz nicht, brechen sie
 * nach drei um (`schmal`). Der Kopf trägt nur ihre Symbole; die Einheiten
 * stehen in der Überschrift des Kapitels.
 */
function lastfallKopf(analyse) {
  return fallkopf(spalten(analyse).map((s) => span(s.symbol)), { schmal: 3 });
}

function lastfallZeile(analyse, index) {
  const fall = analyse.lastfaelle[index];
  const aendern = (veraenderer) => eintragAendern(analyse.kennung, (a) => veraenderer(a.lastfaelle[index]));
  return fallzeile({
    fall, aendern, was: 'Lastfall', nameTitel: 'Bezeichnung des Lastfalls',
    liste: { kennung: analyse.kennung, pfad: 'lastfaelle', index },
    unten: (ausHolz(analyse) && [dauerSchalter(fall, aendern)])
      || (mitDuebeln(analyse) && [duebelzeile(fall, aendern)]) || null,
    zahlen: spalten(analyse).map((s) => zahlfeld({
      // Eine Last, die man leert, ist keine Last.
      wert: fall[s.feld], schritt: s.schritt, titel: s.titel, leer: 0,
      beiAenderung: (v) => aendern((x) => { x[s.feld] = v; }),
    })),
    schmal: 3,
    entfernenTitel: 'Lastfall entfernen',
    entfernen: () => eintragAendern(analyse.kennung, (a) => {
      a.lastfaelle.splice(index, 1);
    }),
  });
}

/**
 * Das kleine Bild der Vorzeichen: Achsen mit V_y und V_z, der Drehsinn von
 * T, und dick die Kanten, die ein positives Moment zieht. Einachsig ohne
 * M_z und V_y, ohne `torsion` auch ohne T.
 */
function vorzeichenbild(einachsig, { torsion = true } = {}) {
  const teile = ['N > 0 Zug', 'M_y > 0 Zug unten', ...(einachsig ? [] : ['M_z > 0 Zug links', 'V_y nach rechts']),
    'V_z nach oben', ...(torsion ? ['T im Gegenuhrzeigersinn'] : [])];
  const bild = svgEl('svg', {
    viewBox: '0 0 168 120', width: 168, height: 120, class: 'vorzeichenbild',
    role: 'img', 'aria-label': `Vorzeichen: ${teile.join(', ')}`,
  });
  const text = (x, y, inhalt, klasse = '', anker = 'middle') => {
    const t = svgEl('text', { x, y, 'text-anchor': anker, class: klasse });
    t.textContent = inhalt;
    return t;
  };
  const pfeil = (x1, y1, x2, y2, klasse) => {
    const g = svgEl('g', { class: klasse });
    const winkel = Math.atan2(y2 - y1, x2 - x1);
    const spitze = (w) => `${x2 - 7 * Math.cos(winkel + w)},${y2 - 7 * Math.sin(winkel + w)}`;
    g.append(
      svgEl('line', { x1, y1, x2, y2 }),
      svgEl('polygon', { points: `${x2},${y2} ${spitze(0.42)} ${spitze(-0.42)}` }),
    );
    return g;
  };

  // Der Querschnitt, der Schwerpunkt S in seiner Mitte.
  const [l, o, r, u] = [52, 26, 112, 96];
  const [sx, sy] = [(l + r) / 2, (o + u) / 2];
  bild.append(svgEl('rect', {
    x: l, y: o, width: r - l, height: u - o, class: 'vz-flaeche',
  }));

  // Gezogene Kanten bei positivem Moment.
  bild.append(svgEl('line', { x1: l, y1: u, x2: r, y2: u, class: 'vz-zug' }));
  bild.append(text(sx, u + 15, 'Zug: M_y > 0', 'vz-zugtext'));
  if (!einachsig) {
    bild.append(svgEl('line', { x1: l, y1: o, x2: l, y2: u, class: 'vz-zug' }));
    const t = text(l - 8, sy, 'Zug: M_z > 0', 'vz-zugtext');
    t.setAttribute('transform', `rotate(-90 ${l - 8} ${sy})`);
    bild.append(t);
  }

  // Achsen in Richtung der positiven Querkräfte.
  bild.append(pfeil(sx, sy, r + 20, sy, 'vz-achse'));
  bild.append(text(r + 23, sy + 4, einachsig ? 'y' : 'y, V_y', 'vz-achstext', 'start'));
  bild.append(pfeil(sx, sy, sx, 6, 'vz-achse'));
  bild.append(text(sx + 6, 12, 'z, V_z', 'vz-achstext', 'start'));

  bild.append(svgEl('circle', { cx: sx, cy: sy, r: 2.2, class: 'vz-schwerpunkt' }));
  if (torsion) bild.append(...drehsinn(sx, sy, text));
  return el('div.vorzeichen', { title: 'N > 0: Zug. Bezugspunkt: Schwerpunkt S' }, [bild]);
}

/** Der Drehsinn von T im Bild der Vorzeichen -- ein Bogen um S mit Spitze am Ende, und sein Name. */
function drehsinn(sx, sy, text) {
  const rad = 13;
  const punkt = (w) => [sx + rad * Math.cos(w), sy - rad * Math.sin(w)];
  const [ax, ay] = punkt(-0.6);
  const [ex, ey] = punkt(3.6);
  const tangente = 3.6 + Math.PI / 2;
  const spitze = (w) => `${ex - 6 * Math.cos(tangente + w)},${ey + 6 * Math.sin(tangente + w)}`;
  return [
    svgEl('path', { d: `M ${ax} ${ay} A ${rad} ${rad} 0 1 0 ${ex} ${ey}`, class: 'vz-drehung' }),
    svgEl('polygon', { points: `${ex},${ey} ${spitze(0.5)} ${spitze(-0.5)}`, class: 'vz-drehspitze' }),
    text(sx + rad + 4, sy + rad + 4, 'T', 'vz-achstext', 'start'),
  ];
}

// ===========================================================================
// Die Kapitel -- je ein Knopf, die Eingaben im Fenster (kapitel.js)
// ===========================================================================

/**
 * Die Tragsicherheit des gezeichneten Querschnitts, mit Querkraft und
 * Torsion. Die übrigen Nachweise führt er wie die Platte
 * (`nachweisKapitel`).
 */
const TRAGSICHERHEIT = {
  schluessel: 'tragsicherheit',
  name: 'Trag\u00adsicherheit', titel: 'Tragsicherheitsnachweise',
  breit: 6,
  bezug: () => 'N, V in kN · M, T in kNm',
  hilfe: HILFE.tragsicherheit,
  inhalt: (analyse) => [...lastfallAngaben(analyse), schubwandAngaben(analyse)],
  stand: (a) => zeilenstand(a.lastfaelle, 'Lastfall', 'Lastfälle', 'kein Lastfall'),
};

/**
 * Dieselbe Kachel für einen Querschnitt aus Stahl, nach SIA 263: ohne
 * Schubwände -- die Querkraft tragen die Profile.
 */
const TRAGSICHERHEIT_STAHL = {
  ...TRAGSICHERHEIT, hilfe: HILFE.tragsicherheitStahl, inhalt: lastfallAngaben,
};

/**
 * Dieselbe Kachel für einen Querschnitt im Verbund, nach SIA 264: auch
 * ohne Schubwände -- die Querkraft trägt der Stahl allein (4.3.2.2).
 */
const TRAGSICHERHEIT_VERBUND = {
  ...TRAGSICHERHEIT, hilfe: HILFE.tragsicherheitVerbund, inhalt: lastfallAngaben,
};

/** Dieselbe Kachel für einen Querschnitt aus Holz, nach SIA 265. */
const TRAGSICHERHEIT_HOLZ = { ...TRAGSICHERHEIT_STAHL, hilfe: HILFE.tragsicherheitHolz };

/**
 * Dieselbe Kachel für eine Blechverbunddecke, nach SIA 264, 5.4: ohne
 * Schubwände -- die Querkraft trägt die Decke nach (26).
 */
const TRAGSICHERHEIT_BLECH = {
  ...TRAGSICHERHEIT, hilfe: HILFE.tragsicherheitBlech, inhalt: lastfallAngaben,
};

/** Die Feuchteklasse der Analyse -- oder die des Kerns, solange keine gewählt ist. */
function feuchteklasse(analyse) {
  return analyse.feuchteklasse ?? feldangabe('querschnittsanalyse', 'feuchteklasse').vorgabe;
}

/** Die gewählte Feuchteklasse aus dem Katalog: Beschriftung, was sie heisst, ihr Stand. */
function feuchteVon(analyse) {
  const gewaehlt = feuchteklasse(analyse);
  return katalog('querschnittsanalyse', 'feuchteklassen').find((k) => k.wert === gewaehlt);
}

/**
 * Wie feucht das Holz im Bauwerk ist -- einmal für die Analyse, je Klasse
 * ein Bild, darunter, was die gewählte heisst. Ihr η_w mindert jeden
 * Nachweis.
 */
const FEUCHTEKLASSE = {
  schluessel: 'feuchteklasse',
  name: 'Feuchte\u00adklasse', titel: 'Feuchteklasse nach SIA 265',
  hilfe: HILFE.feuchteklasse,
  inhalt: (analyse) => [
    wahlBlock('Feuchteklasse', wahlSchalter({
      werte: mitBild(katalog('querschnittsanalyse', 'feuchteklassen'), 'feuchteklasse'),
      gewaehlt: feuchteklasse(analyse),
      setzen: (wert) => eintragAendern(analyse.kennung, (a) => { a.feuchteklasse = wert; }),
      titel: 'Wie feucht das Holz im Bauwerk im Mittel ist',
    })),
    el('p.qa-erlaeuterung', { text: feuchteVon(analyse)?.titel || '' }),
  ],
  stand: (a) => ({ an: true, text: feuchteVon(a)?.stand || '' }),
};

/** Die gewählte Verdübelung aus dem Katalog: Beschriftung und was sie heisst. */
function verduebelungVon(analyse) {
  return katalog('querschnittsanalyse', 'verduebelungen')
    .find((v) => v.wert === analyse.verduebelung);
}

/** Die Masse und der Stahl eines Kopfbolzendübels: Feld, Beschriftung, Titel. */
const DUEBELFELDER = [
  ['duebel_d', ['Durchmesser ', span('d')], 1, 'Durchmesser des Schafts'],
  ['duebel_h', ['Länge ', span('h_D')], 5, 'Länge des Dübels, aufgeschweisst, mit dem Kopf'],
  ['duebel_f_u', ['Zugfestigkeit ', span('f_u')], 10,
    'Zugfestigkeit des Dübelstahls – Vorgabe nach SIA 263, Tabelle 3'],
];

/**
 * Der Kopfbolzendübel der Analyse, je Feld mit den Grenzen des Kerns --
 * dort steht auch, dass d höchstens ein Viertel von h_D ist. Darunter, wo
 * die Zahl der Dübel hingehört: sie gilt je Lastfall.
 */
function duebelAngaben(analyse) {
  const aendern = (veraenderer) => eintragAendern(analyse.kennung, veraenderer);
  return el('div.unterkapitel', {}, [
    el('div.unterkapitel-kopf', {}, [el('span', { text: 'Kopfbolzendübel' })]),
    ...DUEBELFELDER.map(([schluessel, beschriftung, schritt, titel]) => {
      const angabe = feldangabe('querschnittsanalyse', schluessel);
      return feld(beschriftung, zahlfeld({
        wert: analyse[schluessel], schritt, angabe, neben: analyse, titel,
        beiAenderung: (v) => aendern((a) => { a[schluessel] = v; }),
      }), angabe.einheit, titel);
    }),
    el('p.qa-erlaeuterung', {
      text: 'Wie viele Dübel bis zum Momentennullpunkt sitzen und wie weit die '
        + 'Momentennullpunkte auseinander liegen, steht je Lastfall in der Tragsicherheit.',
    }),
  ]);
}

/**
 * Wie Stahl und Beton verbunden sind -- einmal für die Analyse: voll
 * angenommen, wie 5.1.2.1, oder mit Kopfbolzendübeln. Je Stellung ein Bild,
 * die Dehnung über dem Querschnitt; darunter, was die gewählte heisst.
 */
const VERDUEBELUNG = {
  schluessel: 'verduebelung',
  name: 'Ver\u00addübelung', titel: 'Verdübelung nach SIA 264',
  hilfe: HILFE.verduebelung,
  inhalt: (analyse) => [
    wahlBlock('Verdübelung', wahlSchalter({
      werte: mitBild(katalog('querschnittsanalyse', 'verduebelungen'), 'verduebelung'),
      gewaehlt: analyse.verduebelung,
      setzen: (wert) => eintragAendern(analyse.kennung, (a) => { a.verduebelung = wert; }),
      titel: 'Stahl und Beton voll verdübelt angenommen oder mit Kopfbolzendübeln gerechnet',
    })),
    el('p.qa-erlaeuterung', { text: verduebelungVon(analyse)?.titel || '' }),
    mitDuebeln(analyse) ? duebelAngaben(analyse) : null,
  ],
  stand: (a) => ({
    an: true,
    text: mitDuebeln(a) ? `Kopfbolzen ⌀${a.duebel_d} × ${a.duebel_h} mm`
      : verduebelungVon(a)?.beschriftung || '',
  }),
};

/** Die Nachweise je Bauweise, wo sie nicht die des Stahlbetons sind. */
const EIGENE_NACHWEISE = {
  stahl: [TRAGSICHERHEIT_STAHL, STABILITAET],
  verbund: [VERDUEBELUNG, TRAGSICHERHEIT_VERBUND, STABILITAET_VERBUND],
  blechverbund: [LAENGSSCHUB, TRAGSICHERHEIT_BLECH],
  holz: [FEUCHTEKLASSE, TRAGSICHERHEIT_HOLZ, STABILITAET_HOLZ],
};

/** Die Zugseiten einer Analyse aus dem Katalog -- und wie dann ihre Ränder heissen. */
function zugseite(wert) {
  return katalog('querschnittsanalyse', 'zugseiten').find((z) => z.wert === wert);
}

/**
 * Die Wahl der Zugseite: ein Schalter mit je einem Pfeil, der auf die
 * gezogene Seite zeigt -- «Zug unten» steht im Titel. Vier Wörter passten in
 * die schmale Spalte der Analysen nicht (Benutzer, 2026-10-23: keine
 * Auswahllisten).
 */
function zugseitenWahl(gewaehlt, setzen, titel) {
  return wahlSchalter({
    werte: katalog('querschnittsanalyse', 'zugseiten')
      .map((z) => ({ wert: z.wert, beschriftung: z.pfeil, titel: z.beschriftung })),
    gewaehlt, titel, setzen, klasse: '.ist-pfeile',
  });
}

/**
 * Wo die Kapitel eines gezeichneten Querschnitts stehen und was bei ihm
 * anders ist (vgl. `PLATTE` in plattenkapitel.js): die Richtung ist die Zugseite,
 * die Seite, die ein positives Moment zieht. «oben» heisst dann der Rand
 * gegenüber.
 */
const ORT = {
  klasse: 'querschnittsanalyse',
  vorlage: 'qaspannungsfall',
  // Welche Materialien es sind, zählt der Kern mit der Zeichnung.
  werkstoffe: (a) => werkstoffeVon(a.kennung),
  richtung: (k, setzen) => mitKopf('Zug', zugseitenWahl(
    k.richtung, setzen, 'Zugseite: die Seite, die ein positives Moment zieht')),
  raender: (k) => zugseite(k.richtung)?.raender || ['oben', 'unten'],
  bezug: () => 'N in kN · M in kNm',
  hilfe: HILFE,
  // Nachgewiesen wird in jeder Richtung: vor einem Schalter steht keine
  // Tragrichtung, dahinter steht, in welchen Richtungen -- die Zwängung auf
  // Normalkraft gilt dem ganzen Querschnitt.
  marke: () => null,
  hinweis: (a, feld) => (feld === 'zwaengung' ? 'ganzer Querschnitt' : richtungstext(a)),
  // Duktilität und sprödes Versagen rechnen am Querschnitt der Tragsicherheit.
  rechenwerte: 'Gerechnet mit den Rechenwerten der Tragsicherheit.',
  // Das Knicken je Fall zu seiner Zugseite -- sie steht neben dem Namen.
  knick: {
    vorlage: 'qaknick',
    kopf: [['N_{Ed}', 'kN'], ['M_{Ed,1}', 'kNm'], ['l', 'm'], ['l_{cr}', 'm']],
    titel: {
      N_Ed: 'Druckkraft in kN – negativ',
      M_Ed_1: 'Moment 1. Ordnung in kNm – es zieht die gewählte Seite',
      laenge: 'Höhe des Druckglieds in m, bei mehreren übereinander die ganze – bestimmt die Schiefstellung',
      knicklaenge: 'Knicklänge in m',
    },
    richtung: (k, setzen) => zugseitenWahl(
      k.richtung, setzen, 'Zugseite: die Seite, zu der sich der Stab biegt'),
    leer: 'Kein Knicknachweis.',
    // Gerechnet wird mit jeder Lage -- es fehlt keine Richtung.
    fehlt: () => '',
  },
  // Die Lastfälle unter Gebrauchslast: wie die der Tragsicherheit, ohne
  // Querkraft und Torsion.
  gebrauch: {
    liste: 'qagebrauchsliste',
    wahl: 'qagebrauchswahl',
    // Woraus «aus der Tragsicherheit» ableitet: die Lastfälle der Analyse,
    // auch die aus einem Balkensystem.
    aus: (a) => [...a.lastfaelle, ...stellenVon(a)],
    vorlage: 'qagebrauchsfall',
    spalten: (a) => spalten(a).filter((s) => ['N_Ed', 'M_y_Ed', 'M_z_Ed'].includes(s.feld))
      .map((s) => ({
        feld: s.feld, kopf: [s.symbol, s.feld === 'N_Ed' ? 'kN' : 'kNm'],
        schritt: s.schritt, titel: (wort) => `${s.titel}, unter ${wort}er Einwirkung`,
      })),
  },
};

/**
 * Die Kacheln der Analyse. Die Nachweise sind die des Stahlbetons, beim
 * Stahl die Tragsicherheit und Knicken und Kippen nach SIA 263, beim Holz
 * dazu davor die Feuchteklasse, nach SIA 265, im Verbund die
 * Verdübelung, die Tragsicherheit und die Verbundstütze nach SIA 264, in
 * einer Blechverbunddecke der Längsschub und die Tragsicherheit nach
 * SIA 264, 5.4 (`bauweiseVon`). Ein Querschnitt aus
 * mehreren Hölzern hat keine, statt ihrer steht grau, warum
 * (`ohneNachweiseVon`). Die Spannung-Dehnung-Analysen hat jeder ausser dem
 * Verbund und der Decke (`ohneAnalysenVon`), den Schubfluss in den Schnitten
 * jeder (qa_schubfluss.js). Was in den Kacheln eingestellt ist, bleibt.
 */
function kapitel(analyse) {
  const gruppe = (titel, ohne, kacheln) => (ohne ? { titel, hinweis: ohne, kapitel: [] }
    : { titel, kapitel: kacheln() });
  // Gleich nach den eigenen Lastfällen die aus einem Balkensystem.
  const mitSystem = (kacheln) => kacheln.flatMap((k) => (k.schluessel === TRAGSICHERHEIT.schluessel
    ? [k, AUS_SYSTEM] : [k]));
  return [
    gruppe('Nachweise', ohneNachweiseVon(analyse.kennung),
      () => mitSystem(EIGENE_NACHWEISE[bauweiseVon(analyse.kennung)]
        || [TRAGSICHERHEIT, ...nachweisKapitel(ORT)])),
    gruppe('Spannung-Dehnung-Analysen', ohneAnalysenVon(analyse.kennung),
      () => analysenKapitel(ORT)),
    gruppe('Schnitte', '', () => [SCHUBFLUSS]),
  ];
}

/** Die mittlere Tafel für eine Querschnittsanalyse: oben der Querschnitt, darunter die Knöpfe. */
export function analyseEditor(analyse) {
  return [
    querschnittGruppe(analyse),
    kapitelPanel(analyse, kapitel(analyse),
      { schluessel: 'analyse/Kapitel', titel: 'Nachweise und Analysen' }),
  ];
}

/** Das offene Fenster einer Querschnittsanalyse -- oder null. */
export function analyseFenster(analyse, schluessel) {
  return kapitelFenster(analyse, kapitel(analyse), schluessel);
}
