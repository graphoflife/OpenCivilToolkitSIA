/**
 * pfahl.js -- Mittlere Tafel: Eingaben eines Pfahls.
 *
 * Von oben nach unten:
 *
 *     Pfahl Situation   Bezeichnung; Bohr- oder Mikropfahl; Masse,
 *                       Grundwasser, Querschnitt, äusserer Widerstand und
 *                       Querlast je als Karte; Beschreibung
 *     Schichten         vom Terrain an nach unten, je eine Karte: Dicke,
 *                       Raumlast, drainiert oder undrainiert, die
 *                       Mantelreibung gerechnet oder eingegeben, der
 *                       Verformungsmodul
 *     Einwirkungen      die Kombinationen: N_Ed am Kopf, Druck positiv,
 *                       H_Ed und -- am frei drehbaren Kopf -- M_Ed
 *
 * Gezeigt werden nur die Felder, die der Kern mit den gewählten Stellungen
 * liest. Gerechnet wird nichts: die Widerstände und die Federn am Kopf
 * stehen rechts in der Zusammenfassung, die Situation und die Verläufe über
 * die Tiefe unter «Diagramme». Einheiten
 * und Grenzen kommen aus dem Katalog (`katalog.felder`), die Stellungen der
 * Schalter ebenso (`katalog.pfahl`), samt dem Grenzwert von η_a -- quer der
 * einer Berechnung: R_tr,k wird immer gerechnet.
 */

import {
  erklaerung, feld, karte, panel, wahlBlock, wahlSchalter, zahlzeile as feldzeile,
} from './bausteine.js';
import { auswahl, el, zahlfeld } from './dom.js';
import { fallkopf, fallzeile } from './faelle.js';
import {
  ausVorlage, eintragAendern, feldangabe, katalog, materialien, naechsterName,
} from './zustand.js';

const HILFE = {
  situation: {
    zeilen: [
      ['Tiefen', 'ab Oberkante Terrain nach unten: der Kopf in t_K, der Fuss in t_K + L, das Grundwasser in t_w'],
      ['D', 'beim Bohrpfahl verrohrt aussen an der Verrohrung, unverrohrt der des Bohrwerkzeugs (SIA 267:2013, 9.5.2.4.7); beim Mikropfahl der des Verpresskörpers'],
      ['η_a', 'Umrechnungsfaktor des äusseren Widerstands, höchstens 0.7 aus einer Berechnung, 0.9 aus Erfahrung oder einem dynamischen Versuch, 1.0 aus einem statischen Versuch (SIA 267:2013, 9.5.2.2.5); kleiner, wo die Zuverlässigkeit nicht hoch ist (9.5.2.2.6)'],
      ['γ_M,a', '1.3 auf Druck, 1.6 auf Zug (SIA 267:2013, 9.5.2.2.4) -- fest, keine Eingabe'],
      ['η_i', 'Umrechnungsfaktor des inneren Widerstands, in der Regel höchstens 0.8, mit verlässlicher Prüfung der Integrität bis 0.9 (SIA 267:2013, 9.5.2.4.4, 9.5.2.4.9)'],
      ['Mikropfahl', 'es trägt nur das Tragglied aus Stahl, aussen um die Abrostung Δt verkleinert'],
      ['Fuss', 'drainiert (c·N_c + σ\'_v·N_q)·X mit X aus Bild 12.4, undrainiert s_u·N_c mit N_c ≤ 9 aus Bild 12.5 (Kap. 12.5); örtliches Abscheren mit 2/3 von φ\'_k und c\'_k (Kap. 9.2.7)'],
      ['Kopf', 'frei drehbar: ein Moment am Kopf ist Einwirkung; eingespannt, etwa in einer steifen Pfahlkopfplatte: der Kopf dreht sich nicht, das Moment dort ist Reaktion'],
      ['t_red', 'bis in diese Tiefe unter Terrain wächst die Bettung quer linear von null an -- die Norm verlangt nur, sie nahe der Oberfläche abzumindern (SIA 267:2013, 9.5.4.5)'],
      ['R_tr,k', 'Widerstand quer: der kleinste Bruch -- der ganze Pfahl gedreht oder verschoben, oder ein Gelenk, wo das Moment den Biegewiderstand erreicht (SIA 267:2013, 9.4.4.2.2); der Biegewiderstand mit f_ck und f_yk, mal η_i'],
      ['η_a,tr', 'Umrechnungsfaktor quer: R_tr,k wird immer gerechnet, also höchstens 0.7 (SIA 267:2013, 9.5.2.3.2, 9.5.2.2.5)'],
      ['γ_M,a quer', '1.4, der kleinste Wert der Norm (SIA 267:2013, 9.5.2.3.1, (49)) -- fest, keine Eingabe'],
      ['Bettung', 'in keiner Tiefe darf die Bettungskraft der Verläufe den Erdwiderstand p_E,d = η_a,tr·p_E,k/1.4 übersteigen (SIA 267:2013, 9.5.4.5)'],
      ['M im Pfahl', 'in jeder Tiefe |M| ≤ η_i·M_Rd(N/η_i), mit der Normalkraft dort; im Bohrpfahl um die Längszugkraft aus der Querkraft vermindert, F_tVd = |V|·cot α (SIA 262:2025, 4.3.3.4.11)'],
      ['V im Pfahl', 'Bohrpfahl: Fachwerk mit z = 0.9·d, die Wendel zu 70 % von Bügeln (SIA 262:2025, 4.3.3.4.4), α 30° bis 45°, unter Zug ab 40°; Mikropfahl: A_v·f_yd/√3 mit A_v = 2·A/π (SIA 263:2013, 5.1.4.1) -- beides mal η_i'],
    ],
    formel: 'R_a,d = η_a·(R_b,k + R_s,k)/γ_M,a;  R_i,d = η_i·R_mat,d;  R_tr,d = η_a,tr·R_tr,k/γ_M,a',
  },
  schichten: {
    zeilen: [
      ['Folge', 'vom Terrain an nach unten; unter dem Fuss muss noch Boden sein'],
      ['γ', 'eine Raumlast über und unter dem Wasser; darunter zählt γ − γ_w'],
      ['drainiert', 'q_s,k = K·σ\'_v·tan δ, mit δ = k_δ·φ\'_k; rau δ ≈ φ\'_k, K an einem Bohrpfahl höchstens etwa K₀ = 1 − sin φ\'_k (Kap. 12.5)'],
      ['undrainiert', 'q_s,k = α·s_u,k; am Bohrpfahl α ≈ 0.6 in weichem, 0.9 in steifem Ton (Kap. 12.5)'],
      ['eingegeben', 'q_s,k, etwa aus dem geotechnischen Bericht; eine Schicht, die nicht trägt, mit null -- sie hat dann auch längs keine Feder'],
      ['E_s,k', 'Verformungsmodul: am Mantel die Feder 0.42·E_s,k, am Fuss 4.5·E_s,k (Cassan, Kap. 12.8), quer k_s = E_s,k/D (SIA 267:2013, 9.5.4.5, (53)); in der Tragsicherheit E_s,k/1.5 (5.3.2.5)'],
      ['quer', 'Erdwiderstand p_E,k: vorne passiv, hinten aktiv, nach Rankine ohne Reibung am Pfahl -- drainiert mit φ\'_k und c\'_k (Kap. 9.3.5), undrainiert mit s_u,k (Kap. 9.3.6) --, beides auf der Breite 3·D (Kap. 10.8)'],
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

/** Eine Zahl des Pfahls als Feld: Beschriftung mit Symbol, Einheit, Schrittweite. */
function zahlzeile(t, schluessel, text, symbol, { schritt = 1, titel } = {}) {
  return feldzeile('pfahl', t, schluessel, text, symbol, { schritt, titel, aendern: aenderer(t) });
}

/** Ein Schalter aus den Stellungen des Katalogs: das Wort auf dem Knopf, die Erklärung darüber. */
function schalter(gewaehlt, liste, setzen, titel = '') {
  return wahlSchalter({ werte: katalog('pfahl', liste), gewaehlt, setzen, titel });
}

/** Die Wahl eines Materials: eine Auswahlliste, wie beim Durchstanzen. */
function materialfeld(t, schluessel, art, text) {
  return feld(text, auswahl({
    werte: materialien(art).map((m) => ({ wert: m.kennung, beschriftung: m.name || m.sorte })),
    gewaehlt: t[schluessel],
    titel: text,
    beiAenderung: (k) => aenderer(t)((x) => { x[schluessel] = k; }),
  }), '');
}

function querschnittKarte(t) {
  if (t.art === 'bohrpfahl') {
    return karte('Querschnitt', [
      materialfeld(t, 'beton', 'beton', 'Beton'),
      materialfeld(t, 'stahl', 'betonstahl', 'Längsbewehrung'),
      zahlzeile(t, 'n', 'Zahl der Stäbe', 'n'),
      zahlzeile(t, 'phi_l', 'Durchmesser der Stäbe', String.raw`\varnothing_l`, { schritt: 2 }),
      zahlzeile(t, 'c', 'Überdeckung der Wendel', 'c', {
        schritt: 5, titel: 'Mindestens 60 mm verrohrt, 60 mm unverrohrt in Fels oder hartem Boden, 75 mm unverrohrt in weichem Boden (SIA 267:2013, 9.6.3.2.6)',
      }),
      zahlzeile(t, 'phi_w', 'Durchmesser der Wendel', String.raw`\varnothing_w`, { schritt: 2 }),
      zahlzeile(t, 's_w', 'Ganghöhe der Wendel', 's_w', {
        schritt: 10, titel: 'Die grösste längs des Pfahls; in der Regel höchstens 0.40 m, am Kopf 0.10 bis 0.15 m (SIA 267:2013, 9.6.3.2.4)',
      }),
      zahlzeile(t, 'eta_i', 'Umrechnungsfaktor', String.raw`\eta_i`, {
        schritt: 0.05, titel: 'In der Regel höchstens 0.8, mit Prüfung der Integrität bis 0.9',
      }),
    ]);
  }
  const rohr = t.tragglied === 'rohr';
  return karte('Tragglied', [
    materialfeld(t, 'stahl', 'betonstahl', 'Stahl'),
    feld('Tragglied', schalter(t.tragglied, 'tragglieder',
      (w) => aenderer(t)((x) => { x.tragglied = w; }), 'Ein Stahlrohr oder ein Vollstab'), ''),
    zahlzeile(t, 'd_a', rohr ? 'Aussendurchmesser' : 'Durchmesser',
      rohr ? 'd_a' : String.raw`\varnothing`, { schritt: 1 }),
    rohr ? zahlzeile(t, 't_r', 'Wanddicke', 't', { schritt: 0.5 }) : null,
    zahlzeile(t, 'dt', 'Abrostung aussen', String.raw`\Delta t`, {
      schritt: 0.5, titel: 'Zuschlag für die Korrosion statt weiteren Schutzes (SIA 267:2013, 9.6.1.5.2)',
    }),
    zahlzeile(t, 'eta_i', 'Umrechnungsfaktor', String.raw`\eta_i`, {
      schritt: 0.05, titel: 'In der Regel höchstens 0.8, mit Prüfung der Integrität bis 0.9',
    }),
  ].filter(Boolean));
}

function aussenKarte(t) {
  const grundlage = katalog('pfahl', 'grundlagen').find((g) => g.wert === t.grundlage);
  const setzen = (schluessel) => (w) => aenderer(t)((x) => { x[schluessel] = w; });
  const fuss = [];
  if (grundlage?.versuch) {
    fuss.push(
      zahlzeile(t, 'R_ak', 'Widerstand auf Druck', 'R_{a,k}', {
        schritt: 50, titel: 'Der kleinste gemessene Wert (SIA 267:2013, 9.4.4.1.6)',
      }),
      zahlzeile(t, 'R_ak_zug', 'Widerstand auf Zug', 'R_{a,k,Z}', { schritt: 50 }),
    );
  } else {
    fuss.push(wahlBlock('Fuss', schalter(t.spitze, 'spitzen', setzen('spitze'),
      'Ob und wie der Fuss trägt')));
    if (t.spitze === 'eingeben') {
      fuss.push(zahlzeile(t, 'q_b', 'Spitzendruck', 'q_{b,k}', { schritt: 100 }));
    } else if (t.spitze === 'rechnen') {
      fuss.push(feld('Abscheren', schalter(t.abscheren, 'abscheren', setzen('abscheren'),
        'Wie der Boden am Fuss bricht, wenn er drainiert trägt'), ''));
    }
  }
  return karte('Äusserer Widerstand', [
    wahlBlock('Grundlage', schalter(t.grundlage, 'grundlagen', setzen('grundlage'),
      'Worauf R_a,k beruht -- danach richtet sich, wie gross η_a höchstens ist')),
    zahlzeile(t, 'eta_a', 'Umrechnungsfaktor', String.raw`\eta_a`, {
      schritt: 0.05,
      titel: grundlage ? `Höchstens ${grundlage.grenze} (${grundlage.referenz})` : '',
    }),
    ...fuss,
  ]);
}

function querlastKarte(t) {
  const berechnung = katalog('pfahl', 'grundlagen').find((g) => g.wert === 'berechnung');
  return karte('Querlast', [
    feld('Kopf', schalter(t.kopf, 'koepfe', (w) => aenderer(t)((x) => { x.kopf = w; }),
      'Wie der Pfahlkopf gehalten ist'), ''),
    zahlzeile(t, 't_red', 'Abminderung bis', 't_{red}', {
      schritt: 0.5, titel: 'Bis in diese Tiefe unter Terrain wächst die Bettung quer linear von null an (SIA 267:2013, 9.5.4.5)',
    }),
    zahlzeile(t, 'eta_tr', 'Umrechnungsfaktor', String.raw`\eta_{a,tr}`, {
      schritt: 0.05,
      titel: berechnung ? `Höchstens ${berechnung.grenze}: R_tr,k wird immer gerechnet (${berechnung.referenz})` : '',
    }),
  ]);
}

function situationPanel(t) {
  const aendern = aenderer(t);
  const mikro = t.art === 'mikropfahl';
  return panel({
    schluessel: 'pfahl/Situation', titel: 'Pfahl Situation',
    zusatz: erklaerung(HILFE.situation.zeilen, HILFE.situation.formel),
  }, [
    el('div.unterkapitel', {}, [
      feld('Bezeichnung', el('input', {
        type: 'text', value: t.name,
        on: { change: (e) => aendern((x) => { x.name = e.target.value; }) },
      })),
      feld('Pfahl', schalter(t.art, 'arten', (w) => aendern((x) => { x.art = w; }),
        'Bohrpfahl aus Stahlbeton oder Mikropfahl mit einem Tragglied aus Stahl'), ''),
    ]),
    karte('Pfahl', [
      zahlzeile(t, 'D', mikro ? 'Verpresskörper' : 'Durchmesser', 'D', {
        schritt: 50, titel: mikro ? 'Durchmesser des Verpresskörpers: an ihm tragen Mantel und Fuss'
          : 'Verrohrt aussen an der Verrohrung, unverrohrt der des Bohrwerkzeugs (SIA 267:2013, 9.5.2.4.7)',
      }),
      zahlzeile(t, 'L', 'Länge', 'L', { schritt: 0.5 }),
      zahlzeile(t, 't_K', 'Tiefe des Kopfs', 't_K', {
        schritt: 0.5, titel: 'Oberkante Terrain bis zum Pfahlkopf; darüber trägt der Boden nur als Auflast',
      }),
    ]),
    karte('Grundwasser', [
      zahlzeile(t, 't_w', 'Tiefe des Grundwassers', 't_w', {
        schritt: 0.5, titel: 'Oberkante Terrain bis zum höchsten Grundwasserspiegel',
      }),
      zahlzeile(t, 'gamma_w', 'Raumlast Wasser', String.raw`\gamma_w`, { schritt: 0.5 }),
    ]),
    querschnittKarte(t),
    aussenKarte(t),
    querlastKarte(t),
    el('div.unterkapitel', {}, [
      el('div.beschreibung', {}, [
        el('label', { text: 'Beschreibung' }),
        el('textarea', {
          rows: 2, value: t.beschreibung || '',
          on: { change: (e) => aendern((x) => { x.beschreibung = e.target.value; }) },
        }),
      ]),
    ]),
  ]);
}

/** Eine Schicht als Karte: nur die Zahlen, die ihre Stellungen lesen. */
function schichtKarte(t, i) {
  const s = t.schichten[i];
  const aendern = (veraenderer) => eintragAendern(t.kennung, (x) => veraenderer(x.schichten[i]));
  const zahl = (schluessel, text, symbol, mehr = {}) =>
    feldzeile('pfahlschicht', s, schluessel, text, symbol, { ...mehr, aendern });
  const drainiert = s.verhalten === 'drainiert';
  let mantel;
  if (s.mantel === 'eingeben') {
    mantel = [zahl('q_s', 'Mantelreibung', 'q_{s,k}', { schritt: 5 })];
  } else if (drainiert) {
    mantel = [
      zahl('K', 'Erddruckbeiwert', 'K', { schritt: 0.05, titel: 'An einem Bohrpfahl höchstens etwa K₀ = 1 − sin φ\'_k (Kap. 12.5)' }),
      zahl('delta_faktor', 'Wandreibung', String.raw`\delta/\varphi'_k`, { schritt: 0.05, titel: 'Rau etwa 1 (Kap. 12.5)' }),
    ];
  } else {
    mantel = [zahl('alpha', 'Adhäsion', String.raw`\alpha`, { schritt: 0.05, titel: 'Am Bohrpfahl etwa 0.6 in weichem, 0.9 in steifem Ton (Kap. 12.5)' })];
  }
  const weg = el('button.weg', {
    text: '×', title: 'Schicht entfernen',
    on: { click: () => eintragAendern(t.kennung, (x) => { x.schichten.splice(i, 1); }) },
  });
  return karte(`Schicht ${i + 1}`, [
    feld('Bezeichnung', el('input', {
      type: 'text', value: s.name,
      on: { change: (e) => aendern((x) => { x.name = e.target.value; }) },
    })),
    zahl('d', 'Dicke', 'd', { schritt: 0.5 }),
    zahl('gamma', 'Raumlast', String.raw`\gamma`, { schritt: 0.5 }),
    feld('Verhalten', schalter(s.verhalten, 'verhalten', (w) => aendern((x) => { x.verhalten = w; }),
      'Drainiert mit wirksamen Spannungen, undrainiert mit s_u,k'), ''),
    ...(drainiert
      ? [zahl('phi_k', 'Reibungswinkel', String.raw`\varphi'_k`),
        zahl('c_k', 'Kohäsion', "c'_k", { titel: 'Zählt am Fuss und im Erdwiderstand quer' })]
      : [zahl('s_u', 'Scherfestigkeit', 's_{u,k}', { schritt: 5 })]),
    feld('Mantelreibung', schalter(s.mantel, 'mantel', (w) => aendern((x) => { x.mantel = w; }),
      'Gerechnet aus der Schicht oder eingegeben'), ''),
    ...mantel,
    zahl('E_s', 'Verformungsmodul', 'E_{s,k}', {
      schritt: 5, titel: 'Für die Federn: am Mantel 0.42·E, am Fuss 4.5·E (Cassan, Kap. 12.8), quer E/D (SIA 267:2013, (53))',
    }),
  ], { zusatz: weg });
}

function schichtenPanel(t) {
  const neu = () => eintragAendern(t.kennung, (x) => {
    x.schichten.push(ausVorlage('pfahlschicht', { name: naechsterName('Schicht', x.schichten) }));
  });
  const versuch = katalog('pfahl', 'grundlagen').find((g) => g.wert === t.grundlage)?.versuch;
  return panel({
    schluessel: 'pfahl/Schichten', titel: 'Schichten',
    zusatz: erklaerung(HILFE.schichten.zeilen, HILFE.schichten.formel),
  }, [
    versuch ? el('div.leer', { text: 'R_a,k kommt aus dem Versuch: die Schichten gehen nicht in den äusseren Widerstand ein.' }) : null,
    t.schichten.length ? null : el('div.leer', { text: 'Ohne Schicht lässt sich R_a,k nicht rechnen.' }),
    ...t.schichten.map((_, i) => schichtKarte(t, i)),
    el('div.unterkapitel', {}, [
      el('button.knopf-anfuegen', { type: 'button', text: '+ Schicht', on: { click: neu } }),
    ]),
  ].filter(Boolean));
}

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
    zahlen: kraefte(t).map(([schluessel, schritt, titel]) => zahlfeld({
      wert: k[schluessel], schritt, angabe: feldangabe('pfahlkombination', schluessel), titel,
      leer: 0, beiAenderung: (v) => aendern((x) => { x[schluessel] = v; }),
    })),
    entfernenTitel: 'Kombination entfernen',
    entfernen: () => eintragAendern(t.kennung, (x) => { x.kombinationen.splice(i, 1); }),
  });
}

function einwirkungenPanel(t) {
  const neu = () => eintragAendern(t.kennung, (x) => {
    x.kombinationen.push(ausVorlage('pfahlkombination',
      { name: naechsterName('Kombination', x.kombinationen) }));
  });
  return panel({
    schluessel: 'pfahl/Einwirkungen', titel: 'Einwirkungen',
    zusatz: erklaerung(HILFE.einwirkungen.zeilen, HILFE.einwirkungen.formel),
  }, [
    el('div.unterkapitel', {}, [
      t.kombinationen.length
        ? fallkopf(kraefte(t).map(([schluessel]) =>
          `${schluessel} [${feldangabe('pfahlkombination', schluessel).einheit}]`))
        : el('div.leer', { text: 'Ohne Kombination kein Nachweis.' }),
      ...t.kombinationen.map((_, i) => kombinationZeile(t, i)),
      el('button.knopf-anfuegen', { type: 'button', text: '+ Kombination', on: { click: neu } }),
    ]),
  ]);
}

export function pfahlEditor(t) {
  return [situationPanel(t), schichtenPanel(t), einwirkungenPanel(t)];
}
