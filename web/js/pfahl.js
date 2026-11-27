/**
 * pfahl.js -- Mittlere Tafel: Eingaben eines Pfahls.
 *
 * Von oben nach unten:
 *
 *     Pfahl      Bezeichnung, Bohr- oder Mikropfahl, Beschreibung
 *     Eingaben   je eine Kachel mit Sinnbild und dem Wichtigsten
 *                (Benutzer, 2026-11-25), ein Klick öffnet ihr Fenster: je
 *                Gruppe der Vorgaben eine -- Masse, Querschnitt,
 *                Grundwasser, äusserer Widerstand, Fuss, Querlast --, dazu
 *                die Schichten vom Terrain an nach unten, je eine Karte
 *                (Dicke, Raumlast, drainiert oder undrainiert, die
 *                Mantelreibung gerechnet oder eingegeben, der
 *                Verformungsmodul), und die Einwirkungen: N_Ed am Kopf,
 *                Druck positiv, H_Ed und -- am frei drehbaren Kopf -- M_Ed
 *
 * Kacheln, Felder, Zeichen und Hinweise kommen aus dem Kern, wie beim
 * Grundbruch (`katalog.vorgaben`, opencivil/pfahl/pfahl.py): nur die Felder,
 * die er mit den gewählten Stellungen liest, beim Umrechnungsfaktor η_a mit
 * dem Grenzwert seiner Grundlage. Hier stehen nur die Schalter und die
 * Materialien, je bei ihrer Gruppe -- das Wasser seit 2026-11-27 beim
 * Grundwasser, statt der Zahl γ_w. Bis 2026-11-20 standen die Felder hier
 * ein zweites Mal. Gerechnet wird nichts: die Widerstände und die Federn am
 * Kopf stehen rechts in der Zusammenfassung, die Situation und die Verläufe
 * über die Tiefe unter «Diagramme». Einheiten und Grenzen kommen aus dem
 * Katalog (`katalog.felder`), die Stellungen der Schalter ebenso
 * (`katalog.pfahl`).
 */

import {
  beschreibung, bezeichnung, eingabegruppen, eingabezeilen, feld, fehlendesMaterial, karte,
  materialliste, mitBild, namensfeld, panel, verhaltenSchalter, wahlBlock, wahlSchalter,
} from './bausteine.js';
import { el, zahlfeld } from './dom.js';
import { anfuegenKnopf, fallkopf, fallzeile } from './faelle.js';
import {
  gruppenkapitel, kapitelFenster, kapitelPanel, zeilenstand,
} from './kapitel.js';
import {
  ausVorlage, eintragAendern, feldangabe, katalog,
} from './zustand.js';

const HILFE = {
  pfahl: {
    zeilen: [
      ['Tiefen', 'ab Oberkante Terrain nach unten: der Kopf in t_K, der Fuss in t_K + L, das Grundwasser in t_w'],
      ['D', 'beim Bohrpfahl verrohrt aussen an der Verrohrung, unverrohrt der des Bohrwerkzeugs (SIA 267:2013, 9.5.2.4.7); beim Mikropfahl der des Verpresskörpers'],
    ],
  },
  querschnitt: {
    zeilen: [
      ['η_i', 'Umrechnungsfaktor des inneren Widerstands, in der Regel höchstens 0.8, mit verlässlicher Prüfung der Integrität bis 0.9 (SIA 267:2013, 9.5.2.4.4, 9.5.2.4.9)'],
      ['Mikropfahl', 'es trägt nur das Tragglied aus Stahl, aussen um die Abrostung Δt verkleinert'],
      ['M im Pfahl', 'in jeder Tiefe |M| ≤ η_i·M_Rd(N/η_i), mit der Normalkraft dort; im Bohrpfahl um die Längszugkraft aus der Querkraft vermindert, F_tVd = |V|·cot α (SIA 262:2025, 4.3.3.4.11)'],
      ['V im Pfahl', 'Bohrpfahl: Fachwerk mit z = 0.9·d, die Wendel zu 70 % von Bügeln (SIA 262:2025, 4.3.3.4.4), α 30° bis 45°, unter Zug ab 40°; Mikropfahl: A_v·f_yd/√3 mit A_v = 2·A/π (SIA 263:2013, 5.1.4.1) – beides mal η_i'],
    ],
    formel: 'R_i,d = η_i·R_mat,d',
  },
  grundwasser: {
    zeilen: [
      ['t_w', 'ab Oberkante Terrain bis zum höchsten Grundwasserspiegel; darunter zählt in den Schichten γ − γ_w'],
      ['Wasser', 'eine Flüssigkeit aus den Materialien; γ_w ist ihre Raumlast, beim Wasser 10 kN/m³'],
    ],
  },
  aussen: {
    zeilen: [
      ['η_a', 'Umrechnungsfaktor des äusseren Widerstands, höchstens 0.7 aus einer Berechnung, 0.9 aus Erfahrung oder einem dynamischen Versuch, 1.0 aus einem statischen Versuch (SIA 267:2013, 9.5.2.2.5); kleiner, wo die Zuverlässigkeit nicht hoch ist (9.5.2.2.6)'],
      ['γ_M,a', '1.3 auf Druck, 1.6 auf Zug (SIA 267:2013, 9.5.2.2.4) – fest, keine Eingabe'],
    ],
    formel: 'R_a,d = η_a·(R_b,k + R_s,k)/γ_M,a',
  },
  fuss: {
    zeilen: [
      ['Fuss', 'drainiert (c·N_c + σ\'_v·N_q)·X mit X aus Bild 12.4, undrainiert s_u·N_c mit N_c ≤ 9 aus Bild 12.5 (Kap. 12.5); örtliches Abscheren mit 2/3 von φ\'_k und c\'_k (Kap. 9.2.7)'],
    ],
  },
  querlast: {
    zeilen: [
      ['Kopf', 'frei drehbar: ein Moment am Kopf ist Einwirkung; eingespannt, etwa in einer steifen Pfahlkopfplatte: der Kopf dreht sich nicht, das Moment dort ist Reaktion'],
      ['t_red', 'bis in diese Tiefe unter Terrain wächst die Bettung quer linear von null an – die Norm verlangt nur, sie nahe der Oberfläche abzumindern (SIA 267:2013, 9.5.4.5)'],
      ['R_tr,k', 'Widerstand quer: der kleinste Bruch – der ganze Pfahl gedreht oder verschoben, oder ein Gelenk, wo das Moment den Biegewiderstand erreicht (SIA 267:2013, 9.4.4.2.2); der Biegewiderstand mit f_ck und f_yk, mal η_i'],
      ['η_a,tr', 'Umrechnungsfaktor quer: R_tr,k wird immer gerechnet, also höchstens 0.7 (SIA 267:2013, 9.5.2.3.2, 9.5.2.2.5)'],
      ['γ_M,a quer', '1.4, der kleinste Wert der Norm (SIA 267:2013, 9.5.2.3.1, (49)) – fest, keine Eingabe'],
      ['Bettung', 'in keiner Tiefe darf die Bettungskraft der Verläufe den Erdwiderstand p_E,d = η_a,tr·p_E,k/1.4 übersteigen (SIA 267:2013, 9.5.4.5)'],
    ],
    formel: 'R_tr,d = η_a,tr·R_tr,k/γ_M,a',
  },
  schichten: {
    zeilen: [
      ['Folge', 'vom Terrain an nach unten; unter dem Fuss muss noch Boden sein'],
      ['γ', 'eine Raumlast über und unter dem Wasser; darunter zählt γ − γ_w'],
      ['drainiert', 'q_s,k = K·σ\'_v·tan δ, mit δ = k_δ·φ\'_k; rau δ ≈ φ\'_k, K an einem Bohrpfahl höchstens etwa K₀ = 1 − sin φ\'_k (Kap. 12.5)'],
      ['undrainiert', 'q_s,k = α·s_u,k; am Bohrpfahl α ≈ 0.6 in weichem, 0.9 in steifem Ton (Kap. 12.5)'],
      ['eingegeben', 'q_s,k, etwa aus dem geotechnischen Bericht; eine Schicht, die nicht trägt, mit null – sie hat dann auch längs keine Feder'],
      ['E_s,k', 'Verformungsmodul: am Mantel die Feder 0.42·E_s,k, am Fuss 4.5·E_s,k (Cassan, Kap. 12.8), quer k_s = E_s,k/D (SIA 267:2013, 9.5.4.5, (53)); in der Tragsicherheit E_s,k/1.5 (5.3.2.5)'],
      ['quer', 'Erdwiderstand p_E,k: vorne passiv, hinten aktiv, nach Rankine ohne Reibung am Pfahl – drainiert mit φ\'_k und c\'_k (Kap. 9.3.5), undrainiert mit s_u,k (Kap. 9.3.6) –, beides auf der Breite 3·D (Kap. 10.8)'],
    ],
    formel: 'R_s,k = π·D·Σ h·q_s,k',
  },
  einwirkungen: {
    zeilen: [
      ['N_Ed', 'Normalkraft am Pfahlkopf, Druck positiv, Zug negativ'],
      ['H_Ed', 'Querkraft am Pfahlkopf'],
      ['M_Ed', 'Moment am frei drehbaren Kopf, positiv, wenn es dreht wie H_Ed über dem Kopf; am eingespannten Kopf ist das Moment Reaktion'],
      ['Druck', 'N_Ed ≤ R_a,d und N_Ed ≤ R_i,d'],
      ['Zug', 'Z_Ed = −N_Ed ≤ R_a,d,Z (nur der Mantel) und ≤ R_i,d,Z (nur der Stahl)'],
      ['Quer', '|H_Ed| ≤ R_tr,d, dazu in jeder Tiefe die Bettungskraft ≤ p_E,d; ein Moment ohne Querkraft prüft nur die Bettungskraft'],
    ],
    formel: 'E_d ≤ R_d (SIA 267:2013, 9.5.3.1, (52))',
  },
};

const aenderer = (t) => (veraenderer) => eintragAendern(t.kennung, veraenderer);

/**
 * Ein Schalter aus den Stellungen des Katalogs: das Wort auf dem Knopf, die
 * Erklärung darüber. Mit `bild` zeigt jede Stellung ihr Sinnbild `bild-wert`.
 */
function schalter(gewaehlt, liste, setzen, titel = '', bild = null) {
  const werte = katalog('pfahl', liste);
  return wahlSchalter({ werte: bild ? mitBild(werte, bild) : werte, gewaehlt, setzen, titel });
}

/** Ob R_a,k aus einem Versuch kommt: dann gehen die Schichten nicht in ihn ein. */
function ausVersuch(t) {
  return katalog('pfahl', 'grundlagen').find((g) => g.wert === t.grundlage)?.versuch;
}

/** Das Wort einer Stellung, wie der Katalog es nennt: «gerechnet», «frei drehbar». */
function wortVon(liste, wert) {
  return katalog('pfahl', liste).find((w) => w.wert === wert)?.beschriftung || '';
}

function kopfPanel(t) {
  const aendern = aenderer(t);
  return panel({ schluessel: 'pfahl/Situation', titel: 'Pfahl' }, [
    el('div.unterkapitel', {}, [
      bezeichnung(t, aendern),
      feld('Pfahl', schalter(t.art, 'arten', (w) => aendern((x) => { x.art = w; }),
        'Bohrpfahl aus Stahlbeton oder Mikropfahl mit einem Tragglied aus Stahl'), ''),
      beschreibung(t, aendern),
    ]),
  ]);
}

/**
 * Eine Schicht als Karte: nur die Zahlen, die ihre Stellungen lesen
 * (`katalog.vorgaben`), die Schalter vor den Zahlen, nach denen sie fragen.
 */
function schichtKarte(t, i) {
  const s = t.schichten[i];
  const aendern = (veraenderer) => eintragAendern(t.kennung, (x) => veraenderer(x.schichten[i]));
  const weg = el('button.weg', {
    text: '×', title: 'Schicht entfernen',
    on: { click: () => eintragAendern(t.kennung, (x) => { x.schichten.splice(i, 1); }) },
  });
  return karte(`Schicht ${i + 1}`, [
    feld('Bezeichnung', namensfeld({
      wert: s.name, setzen: (name) => aendern((x) => { x.name = name; }),
    })),
    ...eingabezeilen('pfahlschicht', s, aendern, {
      dazu: {
        Festigkeit: {
          vor: [feld('Verhalten', verhaltenSchalter(s.verhalten,
            (w) => aendern((x) => { x.verhalten = w; })), '')],
        },
        Mantelreibung: {
          vor: [feld('Mantelreibung', schalter(s.mantel, 'mantel',
            (w) => aendern((x) => { x.mantel = w; }), 'Gerechnet aus der Schicht oder eingegeben'),
          '')],
        },
      },
    }),
  ], { zusatz: weg });
}

/** Die Schichten: je eine Karte, vom Terrain an nach unten. */
const SCHICHTEN = {
  schluessel: 'schichten',
  name: 'Schichten', titel: 'Schichten',
  hilfe: HILFE.schichten,
  inhalt: (t) => [
    ausVersuch(t) ? el('div.leer', { text: 'R_a,k kommt aus dem Versuch: die Schichten gehen nicht in den äusseren Widerstand ein.' }) : null,
    t.schichten.length ? null : el('div.leer', { text: 'Ohne Schicht lässt sich R_a,k nicht rechnen.' }),
    ...t.schichten.map((_, i) => schichtKarte(t, i)),
    el('div.unterkapitel', {}, [
      anfuegenKnopf('Schicht', (name) => eintragAendern(t.kennung, (x) => {
        x.schichten.push(ausVorlage('pfahlschicht', { name: name(x.schichten) }));
      })),
    ]),
  ].filter(Boolean),
  stand: (t) => zeilenstand(t.schichten, 'Schicht', 'Schichten', 'keine Schicht'),
};

/** Die Kräfte am Kopf: N_Ed und H_Ed, M_Ed nur am frei drehbaren Kopf -- sonst ist es Reaktion. */
function kraefte(t) {
  return [
    ['N_Ed', 50, 'Am Pfahlkopf, Druck positiv, Zug negativ'],
    ['H_Ed', 10, 'Querkraft am Pfahlkopf'],
    t.kopf === 'frei' ? ['M_Ed', 10, 'Moment am Kopf, positiv, wenn es dreht wie H_Ed über dem Kopf'] : null,
  ].filter(Boolean);
}

function kombinationZeile(t, i) {
  const k = t.kombinationen[i];
  const aendern = (veraenderer) => eintragAendern(t.kennung, (x) => veraenderer(x.kombinationen[i]));
  return fallzeile({
    fall: k, aendern, was: 'Kombination', nameTitel: 'Bezeichnung der Kombination',
    liste: { kennung: t.kennung, pfad: 'kombinationen', index: i },
    zahlen: kraefte(t).map(([schluessel, schritt, titel]) => zahlfeld({
      wert: k[schluessel], schritt, angabe: feldangabe('pfahlkombination', schluessel), titel,
      leer: 0, beiAenderung: (v) => aendern((x) => { x[schluessel] = v; }),
    })),
    entfernenTitel: 'Kombination entfernen',
    entfernen: () => eintragAendern(t.kennung, (x) => { x.kombinationen.splice(i, 1); }),
  });
}

/** Die Kombinationen: je eine Zeile, darunter der Knopf für eine weitere. */
const EINWIRKUNGEN = {
  schluessel: 'kombinationen',
  name: 'Einwirkungen', titel: 'Einwirkungen',
  hilfe: HILFE.einwirkungen,
  inhalt: (t) => [el('div.unterkapitel', {}, [
    t.kombinationen.length
      ? fallkopf(kraefte(t).map(([schluessel]) => [schluessel.replace('_Ed', '_{Ed}'),
        feldangabe('pfahlkombination', schluessel).einheit]))
      : el('div.leer', { text: 'Ohne Kombination kein Nachweis.' }),
    ...t.kombinationen.map((_, i) => kombinationZeile(t, i)),
    anfuegenKnopf('Kombination', (name) => eintragAendern(t.kennung, (x) => {
      x.kombinationen.push(ausVorlage('pfahlkombination', { name: name(x.kombinationen) }));
    })),
  ])],
  stand: (t) => zeilenstand(t.kombinationen, 'Kombination', 'Kombinationen', 'keine Kombination'),
};

/**
 * Die Kacheln: je Gruppe der Vorgaben eine, mit den Schaltern und
 * Materialien, nach denen sie fragt, dazu Schichten und Einwirkungen. Aus
 * einem Versuch trägt der Fuss mit -- der Versuch hat den ganzen Pfahl
 * belastet --, und er hat keine Kachel.
 */
function kapitel(t) {
  const aendern = aenderer(t);
  const vorgaben = eingabegruppen('pfahl', t, aendern);
  const setzen = (schluessel) => (w) => aendern((x) => { x[schluessel] = w; });
  // Die Wahl eines Materials: eine Auswahlliste, wie beim Durchstanzen.
  const material = (schluessel, art, text) => feld(text, materialliste({
    art, gewaehlt: t[schluessel], titel: text, setzen: setzen(schluessel),
  }), '');
  const bohrpfahl = t.art === 'bohrpfahl';
  const kacheln = [
    gruppenkapitel(vorgaben, 'Pfahl', { zeichen: 'pfahl', werte: ['D', 'L'], hilfe: HILFE.pfahl }),
    gruppenkapitel(vorgaben, 'Querschnitt', {
      zeichen: 'pfahlquerschnitt', werte: ['n', 'phi_l', 'd_a', 't_r'], hilfe: HILFE.querschnitt,
      vor: bohrpfahl
        ? [material('beton', 'beton', 'Beton'), material('stahl', 'betonstahl', 'Längsbewehrung')]
        : [material('stahl', 'betonstahl', 'Stahl'),
          feld('Tragglied', schalter(t.tragglied, 'tragglieder', setzen('tragglied'),
            'Ein Stahlrohr oder ein Vollstab', 'tragglied'), '')],
      fehlt: (bohrpfahl ? fehlendesMaterial('beton', t.beton) : '')
        || fehlendesMaterial('betonstahl', t.stahl),
    }),
    SCHICHTEN,
    gruppenkapitel(vorgaben, 'Grundwasser', {
      zeichen: 'grundwasser', werte: ['t_w'], hilfe: HILFE.grundwasser,
      nach: [material('wasser', 'fluessigkeit', 'Wasser')],
      fehlt: fehlendesMaterial('fluessigkeit', t.wasser),
    }),
    gruppenkapitel(vorgaben, 'Äusserer Widerstand', {
      zeichen: 'widerstand', wort: wortVon('grundlagen', t.grundlage), werte: ['eta_a'],
      hilfe: HILFE.aussen,
      vor: [wahlBlock('Grundlage', schalter(t.grundlage, 'grundlagen', setzen('grundlage'),
        'Worauf R_a,k beruht – danach richtet sich, wie gross η_a höchstens ist'))],
    }),
    gruppenkapitel(vorgaben, 'Fuss', ausVersuch(t) ? { zeichen: 'pfahlfuss' } : {
      zeichen: 'pfahlfuss', wort: wortVon('spitzen', t.spitze), werte: ['q_b'], hilfe: HILFE.fuss,
      vor: [wahlBlock('Spitzendruck', schalter(t.spitze, 'spitzen', setzen('spitze'),
        'Ob und wie der Fuss trägt'))],
      nach: t.spitze === 'rechnen'
        ? [feld('Abscheren', schalter(t.abscheren, 'abscheren', setzen('abscheren'),
          'Wie der Boden am Fuss bricht, wenn er drainiert trägt'), '')]
        : [],
    }),
    gruppenkapitel(vorgaben, 'Querlast', {
      zeichen: 'querlast', wort: wortVon('koepfe', t.kopf), hilfe: HILFE.querlast,
      vor: [feld('Kopf', schalter(t.kopf, 'koepfe', setzen('kopf'),
        'Wie der Pfahlkopf gehalten ist', 'kopf'), '')],
    }),
    EINWIRKUNGEN,
  ];
  vorgaben.vollstaendig();
  return [{ titel: '', kapitel: kacheln.filter(Boolean) }];
}

export function pfahlEditor(t) {
  return [kopfPanel(t),
    kapitelPanel(t, kapitel(t), { schluessel: 'pfahl/Kapitel', titel: 'Eingaben' })];
}

/** Das offene Fenster eines Pfahls -- oder null. */
export function pfahlFenster(t, schluessel) {
  return kapitelFenster(t, kapitel(t), schluessel);
}
