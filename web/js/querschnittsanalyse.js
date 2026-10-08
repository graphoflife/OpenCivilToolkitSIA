/**
 * querschnittsanalyse.js -- Mittlere Tafel: Eingaben einer Querschnittsanalyse.
 *
 * Von oben nach unten:
 *
 *     Querschnitt     Bezeichnung, Zeichnung samt Liste, Beschreibung
 *     Werkstoffe      je Material im Querschnitt: Rechenwerte und Gesetz
 *     Schubwände      Neigungsgrenzen, k_c, Längszugkraft
 *     Nachweise       Lastfälle; Duktilität und sprödes Versagen
 *
 * Wie bei der Platte steht hier oben, was der Querschnitt *ist*, und unten,
 * was von ihm *verlangt* wird. Gerechnet wird nichts: jede Zeile beschreibt
 * eine Eingabe, die Zahlen dazu bildet der Kern.
 *
 * VORZEICHEN: N > 0 Zug. Ein positives Moment zieht auf der negativen Seite
 * seiner Achse -- M_y > 0 unten, M_z > 0 links. V_y und V_z wirken in
 * Achsrichtung, T im Gegenuhrzeigersinn. Das kleine Bild neben den
 * Lastfällen zeigt es.
 */

import { erklaerung, feld, hakenSchalter, panel } from './bausteine.js';
import { auswahl, el, svgEl, zahlfeld } from './dom.js';
import { span } from './mathe.js';
import { uebersicht } from './qa_uebersicht.js';
import { zeichenbereich } from './qa_zeichnung.js';
import {
  ausVorlage, naechsterName, projektAendern, zustand,
} from './zustand.js';

/** Was hinter den Fragezeichen steht -- Stichworte wie bei der Platte. */
const HILFE = {
  tragsicherheit: {
    zeilen: [
      ['M-N', 'Dehnungsebene über Fasern; schief: die Nulllinie dreht, bis M_Rd in Richtung M_Ed zeigt'],
      ['V+T', 'elastisch auf die Schubwände verteilt (Federn b_w·l), Zellen nach Bredt; je Wand Fachwerk'],
      ['Werte', 'je Material nach Wahl unter «Werkstoffe»'],
    ],
    formel: 'α_eff = Widerstand / Einwirkung ≥ 1',
  },
  duktilitaet: {
    zeilen: [
      ['Weg', 'reine Biegung (N = 0) je Richtung: Zug unten, oben, links, rechts'],
      ['x, d', 'senkrecht zur Nulllinie, ab dem gedrücktesten Betonpunkt'],
      ['einachsig', 'nur Zug unten und oben'],
    ],
    formel: 'x/d ≤ Grenze',
  },
  sproede: {
    zeilen: [
      ['Weg', 'M_Rd bei N = 0 je Richtung gegen das Rissmoment des Bruttoquerschnitts'],
      ['Werte', 'M_Rd nach Werkstoffwahl, M_Riss mit f_ct,eff = k_t·f_ctm'],
    ],
    formel: 'M_Rd(N = 0) ≥ M_Riss = f_ct,eff · W',
  },
  schubwaende: {
    zeilen: [
      ['Wand', 'eine Linie über dem Querschnitt, Länge = Hebelarm'],
      ['α', 'ganzgradig zwischen α_min und α_max; bei Normalzug α_min = 40°'],
      ['Längszug', 'ΔN = |V|·cot α je Wand, in der Wandmitte; geht in M-N ein'],
    ],
    formel: 'V_Rd = min(A_sw/s·l·f_sd·cot α ; b_w·l·k_c·f_cd·sin α·cos α)',
  },
};

function hilfe(schluessel) {
  const { zeilen, formel } = HILFE[schluessel];
  return erklaerung(zeilen, formel);
}

/**
 * Die Spalten eines Lastfalls. `zweiachsig`: nur bei schiefer Biegung --
 * einachsig zählen M_z und V_y nicht, also stehen sie auch nicht da.
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
  { feld: 'T_Ed', symbol: 'T', schritt: 5, titel: 'Torsion in kNm – positiv im Gegenuhrzeigersinn' },
];

function spalten(analyse) {
  return SPALTEN.filter((s) => !(analyse.einachsig && s.zweiachsig));
}

/** Ändert die Analyse mit dieser Kennung -- der eine Weg, auf dem hier etwas geändert wird. */
function aendernAn(kennung, veraenderer) {
  projektAendern((p) => {
    veraenderer(p.querschnittsanalysen.find((a) => a.kennung === kennung));
  });
}

/**
 * Jedes Material, auf das die Analyse verweist -- in der Reihenfolge des
 * ersten Auftretens, wie im Kern (`QuerschnittsanalyseEintrag.materialien`).
 * Gebraucht für die Werkstoffwahl und beim Löschen eines Materials.
 */
export function benutzteMaterialien(analyse) {
  const gesehen = [];
  const kennungen = [
    ...analyse.flaechen.map((f) => f.material),
    ...analyse.staebe.map((s) => s.stahl),
    ...analyse.stablinien.map((l) => l.stahl),
    ...analyse.schubwaende.map((w) => w.stahl),
  ];
  for (const k of kennungen) if (k && !gesehen.includes(k)) gesehen.push(k);
  return gesehen;
}

// ===========================================================================
// Querschnitt
// ===========================================================================

function querschnittGruppe(analyse) {
  const aendern = (veraenderer) => aendernAn(analyse.kennung, veraenderer);
  return panel({
    schluessel: 'analyse/Querschnitt', titel: 'Querschnitt', zusatz: 'y nach rechts, z nach oben, mm',
    breit: true,
  }, [
    feld('Bezeichnung', el('input', {
      type: 'text', value: analyse.name,
      on: { change: (e) => aendern((a) => { a.name = e.target.value; }) },
    })),
    zeichenbereich(analyse, uebersicht),
    el('div.unterkapitel', {}, [
      // Freier Text, der in keine Rechnung eingeht -- wie bei der Platte.
      el('div.beschreibung', { style: { marginTop: 0 } }, [
        el('label', { text: 'Beschreibung' }),
        el('textarea', {
          rows: 2, value: analyse.beschreibung || '',
          on: { change: (e) => aendern((a) => { a.beschreibung = e.target.value; }) },
        }),
      ]),
    ]),
  ]);
}

// ===========================================================================
// Werkstoffe
// ===========================================================================

/**
 * Je Material im Querschnitt eine Zeile: Bemessungs- oder charakteristische
 * Werte, beim Beton dazu das Gesetz. Die Beschriftungen kommen aus dem Kern,
 * die Vorgaben einer fehlenden Wahl aus seiner Vorlage.
 */
function werkstoffGruppe(analyse) {
  const kennungen = benutzteMaterialien(analyse);
  const wahlen = zustand.katalog?.querschnittsanalyse || {};
  const vorgabe = zustand.katalog?.neue_zeilen?.werkstoffwahl || {};

  const setzen = (material, feldname, wert) => aendernAn(analyse.kennung, (a) => {
    let w = a.werkstoffwahl.find((x) => x.material === material);
    if (!w) {
      w = ausVorlage('werkstoffwahl', { material });
      a.werkstoffwahl.push(w);
    }
    w[feldname] = wert;
  });

  const zeile = (kennung) => {
    const material = zustand.projekt.materialien.find((m) => m.kennung === kennung);
    if (!material) return null;
    const wahl = analyse.werkstoffwahl.find((w) => w.material === kennung) || vorgabe;
    const istBeton = material.art === 'beton';
    return el('div.werkstoffzeile', { class: istBeton ? 'ist-beton' : 'ist-stahl' }, [
      el('span.werkstoffname', { text: material.name || material.sorte }),
      auswahl({
        werte: wahlen.werkstoffsaetze || [],
        gewaehlt: wahl.satz,
        titel: 'Rechenwerte: Bemessung (f_cd, f_yd) oder charakteristisch (f_ck, f_yk)',
        beiAenderung: (v) => setzen(kennung, 'satz', v),
      }),
      istBeton
        ? auswahl({
          werte: wahlen.betongesetze || [],
          gewaehlt: wahl.betongesetz,
          titel: 'Spannungs-Dehnungs-Beziehung des Betons',
          beiAenderung: (v) => setzen(kennung, 'betongesetz', v),
        })
        : el('span'),
    ]);
  };

  return panel({
    schluessel: 'analyse/Werkstoffe', titel: 'Werkstoffe', zusatz: 'je Material im Querschnitt',
  }, [
    el('div.unterkapitel', {}, kennungen.length
      ? kennungen.map(zeile)
      : [el('div.leer', { text: 'Noch kein Material im Querschnitt.' })]),
  ]);
}

// ===========================================================================
// Schubwände
// ===========================================================================

function schubwandGruppe(analyse) {
  const aendern = (veraenderer) => aendernAn(analyse.kennung, veraenderer);
  return panel({
    schluessel: 'analyse/Schubwände', titel: 'Schubwände', zusatz: 'Querkraft und Torsion',
  }, [
    el('div.unterkapitel', {}, [
      el('div.unterkapitel-kopf', {}, [el('span', { text: 'Fachwerk je Wand' }),
        hilfe('schubwaende')]),
      el('div.neigungszeile', {}, [
        el('span.postenname', { text: 'Neigung' }),
        span(String.raw`\alpha_{min}`),
        zahlfeld({
          wert: analyse.alpha_min, schritt: 1, min: 1, max: 89,
          titel: 'Kleinste Neigung der Druckdiagonalen, ganze °; bei Normalzug 40°',
          beiAenderung: (v) => aendern((a) => { a.alpha_min = Math.round(v); }),
        }),
        el('span.einheit', { text: '°' }),
        span(String.raw`\alpha_{max}`),
        zahlfeld({
          wert: analyse.alpha_max, schritt: 1, min: 1, max: 89,
          titel: 'Grösste Neigung der Druckdiagonalen, ganze °',
          beiAenderung: (v) => aendern((a) => { a.alpha_max = Math.round(v); }),
        }),
        el('span.einheit', { text: '°' }),
      ]),
      feld(['Druckdiagonale ', span('k_c')], zahlfeld({
        wert: analyse.k_c, schritt: 0.05, min: 0,
        titel: 'Abminderung f_cd in der Druckdiagonalen',
        beiAenderung: (v) => aendern((a) => { a.k_c = v; }),
      }), '', 'Abminderung f_cd in der Druckdiagonalen'),
      el('div.duktilitaetszeile.ist-breit', {}, [
        hakenSchalter(!!analyse.laengszugkraft,
          (wert) => aendern((a) => { a.laengszugkraft = wert; }), 'Längszugkraft'),
        el('span.postenname', { text: 'Längszugkraft aus Querkraft und Torsion berücksichtigen' }),
        el('span'),
      ]),
    ]),
  ]);
}

// ===========================================================================
// Nachweise
// ===========================================================================

function nachweisGruppe(analyse) {
  const aendern = (veraenderer) => aendernAn(analyse.kennung, veraenderer);
  const faelle = analyse.lastfaelle;

  return panel({
    schluessel: 'analyse/Nachweise', titel: 'Nachweise', zusatz: 'N, V in kN · M, T in kNm',
  }, [

    el('div.unterkapitel', {}, [
      el('div.unterkapitel-kopf', {}, [
        el('span', { text: 'Tragsicherheitsnachweise' }),
        hilfe('tragsicherheit'),
      ]),
      el('div.qa-kopfzeile', {}, [
        el('div.qa-schalter', {}, [
          el('div.duktilitaetszeile.ist-breit', {}, [
            hakenSchalter(!!analyse.einachsig,
              (wert) => aendern((a) => { a.einachsig = wert; }), 'Einachsige Biegung'),
            el('span.postenname', { text: 'nur einachsig (Biegung um y)' }),
            el('span'),
          ]),
          el('p.qa-erlaeuterung', {
            text: analyse.einachsig
              ? 'Nulllinie waagrecht; M_z und V_y zählen nicht.'
              : 'N, M_y und M_z gleichzeitig; die Nulllinie liegt schief.',
          }),
        ]),
        vorzeichenbild(analyse.einachsig),
      ]),
      faelle.length ? lastfallKopf(analyse) : null,
      ...(faelle.length
        ? faelle.map((_, i) => lastfallZeile(analyse, i))
        : [el('div.leer', { text: 'Ohne Lastfall kein Nachweis.' })]),
      el('button.knopf-anfuegen', {
        text: '+ Lastfall',
        on: {
          click: () => aendern((a) => a.lastfaelle.push(
            ausVorlage('qa_lastfall', { name: naechsterName('Tragsicherheit', a.lastfaelle) }))),
        },
      }),
    ]),

    el('div.unterkapitel', {}, [
      el('div.unterkapitel-kopf', {}, [el('span', { text: 'Duktilitätsnachweis' }),
        hilfe('duktilitaet')]),
      el('div.duktilitaetszeile.mit-grenze', {}, [
        hakenSchalter(!!analyse.duktilitaet,
          (wert) => aendern((a) => { a.duktilitaet = wert; }), 'Nachweis'),
        el('span.postenname', { text: 'Max. x/d' }),
        zahlfeld({
          wert: analyse.x_d_max, schritt: 0.05, min: 0.05,
          max: zustand.katalog?.duktilitaet?.hoechstens,
          titel: `Grenze der Druckzonenhöhe x/d; höchstens ${
            zustand.katalog?.duktilitaet?.hoechstens ?? '–'}`,
          beiAenderung: (v) => aendern((a) => { a.x_d_max = v; }),
        }),
        el('span.kurvenhinweis', { text: richtungstext(analyse) }),
      ]),
    ]),

    el('div.unterkapitel', {}, [
      el('div.unterkapitel-kopf', {}, [el('span', { text: 'Nachweis gegen sprödes Versagen' }),
        hilfe('sproede')]),
      el('div.duktilitaetszeile.ist-breit', {}, [
        hakenSchalter(!!analyse.sproede,
          (wert) => aendern((a) => { a.sproede = wert; }), 'Nachweis'),
        el('span.postenname', { text: 'Rissmoment' }),
        el('span.kurvenhinweis', { text: richtungstext(analyse) }),
      ]),
    ]),
  ]);
}

/** In welchen Richtungen Duktilität und sprödes Versagen geführt werden. */
function richtungstext(analyse) {
  return analyse.einachsig ? 'Zug unten und oben' : 'Zug unten, oben, links, rechts';
}

/**
 * Ein Lastfall: Schalter, Name, die Schnittgrössen, Entfernen. Die Zahlen
 * stehen in einem eigenen Raster -- in der schmalen Tafel unter dem Namen,
 * in der breiten daneben. Der Kopf trägt nur ihre Symbole; die Einheiten
 * stehen in der Überschrift des Kapitels.
 */
function lastfallKopf(analyse) {
  return el('div.qa-fall.ist-kopf', { style: { '--felder': spalten(analyse).length } }, [
    el('span'),
    el('span.qa-name', { text: 'Bezeichnung' }),
    el('div.qa-zahlen', {}, spalten(analyse).map((s) => el('span', {}, [span(s.symbol)]))),
    el('span'),
  ]);
}

function lastfallZeile(analyse, index) {
  const fall = analyse.lastfaelle[index];
  const aendern = (veraenderer) => aendernAn(analyse.kennung,
    (a) => veraenderer(a.lastfaelle[index]));
  const an = fall.aktiv !== false;

  return el('div.qa-fall', {
    class: an ? '' : 'ist-aus', style: { '--felder': spalten(analyse).length },
  }, [
    hakenSchalter(an, (wert) => aendern((x) => { x.aktiv = wert; }), 'Lastfall'),
    el('input.ew-name.qa-name', {
      type: 'text', value: fall.name, title: 'Bezeichnung des Lastfalls',
      on: { change: (e) => aendern((x) => { x.name = e.target.value; }) },
    }),
    el('div.qa-zahlen', {}, spalten(analyse).map((s) => zahlfeld({
      // Eine Last, die man leert, ist keine Last.
      wert: fall[s.feld], schritt: s.schritt, titel: s.titel, leer: 0,
      beiAenderung: (v) => aendern((x) => { x[s.feld] = v; }),
    }))),
    el('button.weg', {
      text: '×', title: 'Lastfall entfernen',
      on: {
        click: () => aendernAn(analyse.kennung, (a) => { a.lastfaelle.splice(index, 1); }),
      },
    }),
  ]);
}

/**
 * Das kleine Bild der Vorzeichen: Achsen mit V_y und V_z, der Drehsinn von
 * T, und dick die Kanten, die ein positives Moment zieht.
 */
function vorzeichenbild(einachsig) {
  const bild = svgEl('svg', {
    viewBox: '0 0 168 120', width: 168, height: 120, class: 'vorzeichenbild',
    role: 'img',
    'aria-label': einachsig
      ? 'Vorzeichen: N > 0 Zug, M_y > 0 Zug unten, V_z nach oben, T im Gegenuhrzeigersinn'
      : 'Vorzeichen: N > 0 Zug, M_y > 0 Zug unten, M_z > 0 Zug links, V_y nach rechts, '
        + 'V_z nach oben, T im Gegenuhrzeigersinn',
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

  // T im Gegenuhrzeigersinn -- ein Bogen um S mit Spitze am Ende.
  const rad = 13;
  const punkt = (w) => [sx + rad * Math.cos(w), sy - rad * Math.sin(w)];
  const [ax, ay] = punkt(-0.6);
  const [ex, ey] = punkt(3.6);
  bild.append(svgEl('path', {
    d: `M ${ax} ${ay} A ${rad} ${rad} 0 1 0 ${ex} ${ey}`, class: 'vz-drehung',
  }));
  const tangente = 3.6 + Math.PI / 2;
  const spitze = (w) => `${ex - 6 * Math.cos(tangente + w)},${ey + 6 * Math.sin(tangente + w)}`;
  bild.append(svgEl('polygon', {
    points: `${ex},${ey} ${spitze(0.5)} ${spitze(-0.5)}`, class: 'vz-drehspitze',
  }));
  bild.append(text(sx + rad + 4, sy + rad + 4, 'T', 'vz-achstext', 'start'));
  bild.append(svgEl('circle', { cx: sx, cy: sy, r: 2.2, class: 'vz-schwerpunkt' }));

  return el('div.vorzeichen', { title: 'N > 0: Zug. Bezugspunkt: Schwerpunkt S' }, [bild]);
}

// ===========================================================================

/** Die mittlere Tafel für eine Querschnittsanalyse. */
export function analyseEditor(analyse) {
  return [
    querschnittGruppe(analyse),
    werkstoffGruppe(analyse),
    schubwandGruppe(analyse),
    nachweisGruppe(analyse),
  ];
}
