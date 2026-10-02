/**
 * qa_diagramme.js -- die Diagramme einer Querschnittsanalyse.
 *
 * Oben das Interaktionsdiagramm: die Fläche aller Bruchzustände im Raum
 * (N, M_y, M_z), geschnitten bei einem festen Wert einer Grösse. Welche zwei
 * auf den Achsen stehen, wird gewählt; die dritte bekommt ihren Wert im
 * Zahlenfeld. Lastfälle in dieser Ebene stehen kräftig, die übrigen blass.
 *
 * Darunter je Lastfall, umschaltbar:
 *
 *   Bruchzustand    der Schnitt mit Nulllinie, Druckzone und der Dehnung
 *                   jedes Stabs -- gezogen kupfer, gedrückt blau;
 *   M-N             die Linie in der Ebene des Lastfalls, mit Einwirkung
 *                   und Widerstand bei N_Ed;
 *   M_y-M_z         bei schiefer Biegung: der Widerstand rundum bei N_Ed;
 *   Schubfluss      je Stück einer Wand ein Pfeil, so lang wie der Fluss.
 *
 * Die Daten kommen aus einer eigenen Anfrage (`analysediagramme`): die
 * Kurven brauchen Bruchzustände, die kein Nachweis braucht, und sollen nicht
 * jede Rechnung verlangsamen. Gefragt wird erst, wenn die Rechnung zur
 * aktuellen Eingabe durch ist -- dann liegen die Nachweise im Speicher des
 * Kerns, und es kommen nur die Kurven dazu. Bis dahin bleiben die alten
 * Bilder stehen, blass.
 *
 * Gerechnet wird hier nichts: Nulllinie, Druckzone, Dehnungen, Flüsse und
 * Kurven kommen fertig aus dem Kern.
 */

import { achsenkreuz, NR } from './achsen.js';
import { api } from './api.js';
import {
  auswahl, el, leerzustand, svgEl, zahlfeld,
} from './dom.js';
import { aendern, zustand } from './zustand.js';

const BREITE = 640;
const HOEHE = 470;
const RAND = { oben: 22, rechts: 22, unten: 46, links: 74 };

const ZUG = '#b8622a';
const DRUCK = '#1f5fa8';
const GUT = '#1a7f45';
const SCHLECHT = '#b3261e';
const VIOLETT = '#8b5cf6';

/** Kennung -> {abdruck, daten, alt, fehler, uhr}: die letzte Antwort je Analyse. */
const vorrat = new Map();

/** Kennung -> Name des gezeigten Lastfalls. Ansichtssache, nicht Teil des Projekts. */
const gezeigt = new Map();

/** Die drei Grössen des Interaktionsdiagramms: Achsentitel, Einheit, Feld im Lastfall. */
const GROESSE = {
  N: { titel: 'N [kN]   (Zug positiv)', einheit: 'kN', schritt: 50, feld: 'N_Ed' },
  M_y: { titel: 'M_y [kNm]   (positiv: Zug unten)', einheit: 'kNm', schritt: 10, feld: 'M_y_Ed' },
  M_z: { titel: 'M_z [kNm]   (positiv: Zug links)', einheit: 'kNm', schritt: 10, feld: 'M_z_Ed' },
};

/**
 * Kennung -> was das Interaktionsdiagramm zeigt: die Achsen und je Grösse
 * ihr Wert, wenn sie die feste ist. Ein Wert bleibt stehen, wenn die Achsen
 * wechseln -- wer zurückschaltet, findet ihn wieder.
 */
const schnittwahl = new Map();

function wahlVon(kennung) {
  if (!schnittwahl.has(kennung)) {
    schnittwahl.set(kennung, { x: 'M_y', y: 'N', werte: { N: 0, M_y: 0, M_z: 0 } });
  }
  return schnittwahl.get(kennung);
}

/** Die Grösse, die auf keiner Achse steht. */
function festVon(wahl) {
  return Object.keys(GROESSE).find((g) => g !== wahl.x && g !== wahl.y);
}

/** Woran die Diagramme hängen: die Analyse und die Materialien. */
function abdruckVon(kennung) {
  const analyse = zustand.projekt.querschnittsanalysen?.find((a) => a.kennung === kennung);
  return JSON.stringify([analyse, zustand.projekt.materialien]);
}

/**
 * Fragt nach den Diagrammen -- aber erst, wenn gerade nicht gerechnet wird.
 * Läuft die Rechnung noch, wartet die Anfrage; danach liegen die Nachweise
 * im Speicher des Kerns, und es kommen nur die Kurven dazu.
 */
function anfordern(kennung, eintrag, verzug = 600) {
  clearTimeout(eintrag.uhr);
  eintrag.uhr = setTimeout(() => {
    if (vorrat.get(kennung) !== eintrag) return;
    if (zustand.rechnetGerade) {
      anfordern(kennung, eintrag);
      return;
    }
    api.analysediagramme(zustand.projekt, kennung, eintrag.schnitt).then((antwort) => {
      if (vorrat.get(kennung) !== eintrag) return;
      eintrag.daten = antwort.diagramme;
      aendern({}, 'diagramm');
    }).catch((fehler) => {
      if (vorrat.get(kennung) !== eintrag) return;
      eintrag.fehler = fehler.message;
      aendern({}, 'diagramm');
    });
  }, verzug);
}

// ===========================================================================
// Querschnitt
// ===========================================================================

/** Massstab und Lage des Schnitts im Bild: y nach rechts, z nach oben. */
function bildrahmen(zeichnung, breite, hoehe, rand = 34) {
  const punkte = zeichnung.polygone.flatMap((p) => p.punkte);
  const ys = punkte.map((p) => p[0]);
  const zs = punkte.map((p) => p[1]);
  const [y0, y1, z0, z1] = [Math.min(...ys), Math.max(...ys), Math.min(...zs), Math.max(...zs)];
  const m = Math.min((breite - 2 * rand) / ((y1 - y0) || 1), (hoehe - 2 * rand) / ((z1 - z0) || 1));
  const ox = breite / 2 - m * (y0 + y1) / 2;
  const oy = hoehe / 2 + m * (z0 + z1) / 2;
  return { m, bild: ([y, z]) => [ox + m * y, oy - m * z] };
}

function pfad(bild, punkte, zu = true) {
  return punkte.map((p, i) => {
    const [x, y] = bild(p);
    return `${i ? 'L' : 'M'}${x.toFixed(1)} ${y.toFixed(1)}`;
  }).join(' ') + (zu ? ' Z' : '');
}

function text(x, y, inhalt, attribute = {}) {
  const t = svgEl('text', {
    x: x.toFixed(1), y: y.toFixed(1), 'font-size': 11, fill: '#3b4757', ...attribute,
  });
  t.textContent = inhalt;
  return t;
}

/** Die Polygone, Eltern zuerst: Beton grau, Aussparungen weiss. */
function polygoneZeichnen(gruppe, zeichnung, bild) {
  for (const p of [...zeichnung.polygone].sort((a, b) => a.tiefe - b.tiefe)) {
    gruppe.append(svgEl('path', {
      d: pfad(bild, p.punkte),
      fill: p.material ? '#dde2e8' : '#fff', stroke: '#7b8794', 'stroke-width': 1.2,
      'stroke-dasharray': p.material ? null : '5 3',
    }));
  }
}

function schwerpunktZeichnen(gruppe, zeichnung, bild) {
  const [x, y] = bild(zeichnung.schwerpunkt);
  gruppe.append(
    svgEl('circle', { cx: x, cy: y, r: 5, fill: '#fff', stroke: '#16202c', 'stroke-width': 1.1 }),
    svgEl('path', { d: `M${x - 8} ${y} H${x + 8} M${x} ${y - 8} V${y + 8}`, stroke: '#16202c' }),
    text(x + 8, y - 6, 'S', { 'font-weight': 700, fill: '#16202c' }),
  );
}

/**
 * Der Bruchzustand im Schnitt: Druckzone getönt, Nulllinie gestrichelt, die
 * Stäbe nach dem Vorzeichen ihrer Dehnung gefärbt.
 */
function bruchbild(daten, fall) {
  const z = daten.zeichnung;
  const b = fall.bruch;
  const { m, bild } = bildrahmen(z, BREITE, HOEHE);
  const svg = svgEl('svg', {
    viewBox: `0 0 ${BREITE} ${HOEHE}`, class: 'qs', xmlns: NR, role: 'img',
    'aria-label': `Bruchzustand ${fall.name}`,
  });
  const g = svgEl('g');
  polygoneZeichnen(g, z, bild);
  // Die gedrückte Fläche je Polygon, wieder Eltern zuerst: eine Aussparung
  // nimmt auch der Druckzone ihre Fläche.
  for (const zone of [...b.druckzone].sort((a, c) => a.tiefe - c.tiefe)) {
    g.append(svgEl('path', {
      d: pfad(bild, zone.punkte),
      fill: zone.material ? 'rgba(31,95,168,.22)' : '#fff', stroke: 'none',
    }));
  }
  for (const l of z.flaechenlinien) {
    g.append(svgEl('path', {
      d: pfad(bild, [l.von, l.bis], false), stroke: ZUG, 'stroke-width': 4, 'stroke-linecap': 'round',
    }));
  }
  if (b.nulllinie) {
    const [[x0, y0], [x1, y1]] = b.nulllinie.map(bild);
    g.append(svgEl('line', {
      x1: x0, y1: y0, x2: x1, y2: y1, stroke: '#16202c', 'stroke-width': 1.6, 'stroke-dasharray': '8 4',
    }));
    g.append(text(x1 + 4, y1 - 5, 'Nulllinie', { 'font-weight': 600, fill: '#16202c' }));
  }
  for (const s of b.staebe) {
    const [x, y] = bild([s.y, s.z]);
    const gezogen = s.eps > 0;
    const kreis = svgEl('circle', {
      cx: x, cy: y, r: Math.max(2.6, (m * s.d) / 2),
      fill: gezogen ? ZUG : '#fff', stroke: gezogen ? '#7a3d14' : DRUCK, 'stroke-width': 1.4,
    });
    const t = svgEl('title');
    t.textContent = `ε = ${s.eps.toFixed(2)} ‰ (${gezogen ? 'Zug' : 'Druck'})`;
    kreis.append(t);
    g.append(kreis);
  }
  schwerpunktZeichnen(g, z, bild);
  svg.append(g);
  return el('div.diagramm-huelle', {}, [
    svg,
    el('div.mn-legende', {}, [
      el('span', {}, [el('i', { style: { background: 'rgba(31,95,168,.35)', borderRadius: '2px' } }),
        `Druckzone, x = ${b.x.toFixed(1)} mm`]),
      el('span', {}, [el('i', { style: { background: ZUG } }), 'Stab gezogen']),
      el('span', {}, [el('i', { style: { background: '#fff', border: `1.5px solid ${DRUCK}` } }),
        'Stab gedrückt']),
      b.d > 0 ? el('span', { text: `d = ${b.d.toFixed(1)} mm` }) : null,
    ]),
  ]);
}

/**
 * Der Schubfluss: die Wände als Band, je Stück ein Pfeil in Richtung des
 * Flusses, so lang wie er stark ist. Eine Wand, die nicht hält, ist rot.
 */
function schubbild(daten, fall) {
  const z = daten.zeichnung;
  const s = fall.schub;
  const { m, bild } = bildrahmen(z, BREITE, HOEHE, 46);
  const svg = svgEl('svg', {
    viewBox: `0 0 ${BREITE} ${HOEHE}`, class: 'qs', xmlns: NR, role: 'img',
    'aria-label': `Schubfluss ${fall.name}`,
  });
  const g = svgEl('g');
  polygoneZeichnen(g, z, bild);
  const urteil = new Map(s.waende.map((w) => [w.name, w]));
  for (const w of z.waende) {
    const l = Math.hypot(w.bis[0] - w.von[0], w.bis[1] - w.von[1]) || 1;
    const n = [(-(w.bis[1] - w.von[1]) / l) * (w.dicke / 2), ((w.bis[0] - w.von[0]) / l) * (w.dicke / 2)];
    const ecken = [
      [w.von[0] + n[0], w.von[1] + n[1]], [w.bis[0] + n[0], w.bis[1] + n[1]],
      [w.bis[0] - n[0], w.bis[1] - n[1]], [w.von[0] - n[0], w.von[1] - n[1]],
    ];
    const gut = urteil.get(w.name)?.erfuellt !== false;
    g.append(svgEl('path', {
      d: pfad(bild, ecken), fill: gut ? 'rgba(139,92,246,.14)' : 'rgba(179,38,30,.14)',
      stroke: gut ? VIOLETT : SCHLECHT, 'stroke-opacity': 0.6,
    }));
  }
  // Pfeillänge: der stärkste Fluss bekommt 70 px, alle anderen im Verhältnis.
  const groesster = Math.max(...s.stuecke.map((x) => Math.abs(x.q)), 1e-9);
  for (const stueck of s.stuecke) {
    if (Math.abs(stueck.q) < 1e-6 * groesster) continue;
    const [ax, ay] = bild(stueck.von);
    const [bx, by] = bild(stueck.bis);
    const lang = Math.hypot(bx - ax, by - ay) || 1;
    const richtung = [((bx - ax) / lang) * Math.sign(stueck.q), ((by - ay) / lang) * Math.sign(stueck.q)];
    const laenge = Math.min(70 * Math.abs(stueck.q) / groesster, lang * 0.8);
    const [mx, my] = [(ax + bx) / 2, (ay + by) / 2];
    const [x0, y0] = [mx - (richtung[0] * laenge) / 2, my - (richtung[1] * laenge) / 2];
    const [x1, y1] = [mx + (richtung[0] * laenge) / 2, my + (richtung[1] * laenge) / 2];
    const winkel = Math.atan2(richtung[1], richtung[0]);
    const spitze = (w) => `${(x1 - 9 * Math.cos(winkel + w)).toFixed(1)},${(y1 - 9 * Math.sin(winkel + w)).toFixed(1)}`;
    const gut = urteil.get(stueck.wand)?.erfuellt !== false;
    const farbe = gut ? '#5b3fb8' : SCHLECHT;
    g.append(
      svgEl('line', { x1: x0, y1: y0, x2: x1, y2: y1, stroke: farbe, 'stroke-width': 2.2 }),
      svgEl('polygon', { points: `${x1.toFixed(1)},${y1.toFixed(1)} ${spitze(0.4)} ${spitze(-0.4)}`, fill: farbe }),
    );
    // Die Zahl quer neben dem Pfeil, auf der Seite zur Mitte des Bildes hin.
    const quer = [-richtung[1], richtung[0]];
    const t = text(mx + quer[0] * 14, my + quer[1] * 14 + 4, `${Math.abs(stueck.q).toFixed(1)}`, {
      'text-anchor': 'middle', 'font-weight': 600, fill: farbe,
      'paint-order': 'stroke', stroke: '#fff', 'stroke-width': 3,
    });
    g.append(t);
  }
  schwerpunktZeichnen(g, z, bild);
  svg.append(g);
  return el('div.diagramm-huelle', {}, [
    svg,
    el('div.mn-legende', {}, [
      el('span', { text: 'Pfeile: Schubfluss q in kN/m, in seiner Richtung' }),
      ...s.waende.map((w) => el('span', {
        style: { color: w.erfuellt ? 'inherit' : SCHLECHT },
        text: `${w.name}: |q| ≤ ${w.q_max.toFixed(1)}, v_Rd = ${w.v_Rd.toFixed(1)} (α = ${w.alpha}°)`,
      })),
    ]),
  ]);
}

// ===========================================================================
// Interaktionsdiagramm
// ===========================================================================

function achsenwahl(kennung, achse) {
  const wahl = wahlVon(kennung);
  return auswahl({
    werte: Object.keys(GROESSE).map((g) => ({ wert: g, beschriftung: g })),
    gewaehlt: wahl[achse],
    titel: achse === 'x' ? 'Grösse auf der waagrechten Achse' : 'Grösse auf der senkrechten Achse',
    beiAenderung: (neu) => {
      // Steht die Grösse schon auf der anderen Achse, tauschen die beiden.
      const andere = achse === 'x' ? 'y' : 'x';
      if (wahl[andere] === neu) wahl[andere] = wahl[achse];
      wahl[achse] = neu;
      aendern({}, 'diagramm');
    },
  });
}

/** Wo das Diagramm schneidet: die Achsen und der Wert der dritten Grösse. */
function schnittsteuerung(kennung, einachsig) {
  if (einachsig) {
    return el('p.qa-schnitthinweis', {
      text: 'Einachsig: M_y über N, die Nulllinie bleibt waagrecht; M_z zählt nicht.',
    });
  }
  const wahl = wahlVon(kennung);
  const fest = festVon(wahl);
  return el('div.qa-schnittwahl', {}, [
    el('label', {}, ['x-Achse ', achsenwahl(kennung, 'x')]),
    el('label', {}, ['y-Achse ', achsenwahl(kennung, 'y')]),
    el('label', {}, [
      `bei ${fest} = `,
      zahlfeld({
        wert: wahl.werte[fest], schritt: GROESSE[fest].schritt, leer: 0,
        titel: `Fester Wert von ${fest} in ${GROESSE[fest].einheit}; die Fläche wird dort geschnitten`,
        beiAenderung: (v) => { wahl.werte[fest] = v; aendern({}, 'diagramm'); },
      }),
      ` ${GROESSE[fest].einheit}`,
    ]),
  ]);
}

/**
 * Das Bild: der Schnitt durch die Fläche, dazu jeder Lastfall. In dieser
 * Ebene liegt einer, wenn seine feste Grösse den Wert hat -- dann kräftig,
 * grün oder rot wie sein Nachweis. Sonst blass: er gehört zu einem anderen
 * Schnitt. Zwei Momente auf den Achsen bekommen denselben Massstab.
 */
function interaktionsbild(i, faelle, x, y, einachsig) {
  const wert = (f, g) => f[GROESSE[g].feld];
  const punkte = i.punkte.map((p) => [p[x], p[y]]);
  if (!punkte.length) {
    return leerzustand(`Bei ${i.fest} = ${i.wert} ${GROESSE[i.fest].einheit} gibt es keinen Bruchzustand`,
      'Die Ebene trifft die Fläche der Widerstände nicht.');
  }
  const passt = (f) => einachsig || Math.abs(wert(f, i.fest) - i.wert) < 1e-6;
  const alleX = [...punkte.map((q) => q[0]), ...faelle.map((f) => wert(f, x))];
  const alleY = [...punkte.map((q) => q[1]), ...faelle.map((f) => wert(f, y))];
  let rx = bereich(alleX);
  let ry = bereich(alleY);
  let breite = BREITE;
  if (x !== 'N' && y !== 'N') {
    const r = Math.max(...alleX.map(Math.abs), ...alleY.map(Math.abs)) * 1.12 || 1;
    rx = [-r, r];
    ry = [-r, r];
    breite = HOEHE + 52;
  }
  const { svg, daten: g, x: sx, y: sy } = achsenkreuz({
    breite, hoehe: HOEHE, rand: RAND,
    attribute: { class: 'mn', xmlns: NR, role: 'img', 'aria-label': `Interaktionsdiagramm ${y} über ${x}` },
    x: { bereich: rx, teilung: {}, null: true, titel: GROESSE[x].titel },
    y: { bereich: ry, teilung: {}, null: true, titel: GROESSE[y].titel },
  });
  g.append(svgEl('polygon', {
    points: punkte.map(([a, b]) => `${sx(a).toFixed(2)},${sy(b).toFixed(2)}`).join(' '),
    fill: 'rgba(31,95,168,.07)', stroke: '#1f5fa8', 'stroke-width': 2, 'stroke-linejoin': 'round',
  }));
  // Die blassen zuerst, damit die kräftigen obenauf liegen.
  for (const f of [...faelle].sort((a, b) => passt(a) - passt(b))) {
    const drin = passt(f);
    const farbe = drin ? (f.erfuellt ? GUT : SCHLECHT) : '#8895a8';
    const punkt = svgEl('circle', {
      cx: sx(wert(f, x)), cy: sy(wert(f, y)), r: drin ? 6 : 5,
      fill: farbe, stroke: '#fff', 'stroke-width': 2, opacity: drin ? 1 : 0.45,
    });
    const t = svgEl('title');
    t.textContent = `${f.name}\nN = ${f.N_Ed.toFixed(1)} kN, M_y = ${f.M_y_Ed.toFixed(1)} kNm, `
      + `M_z = ${f.M_z_Ed.toFixed(1)} kNm\n`
      + (drin ? `α_eff = ${f.grad_text} – ${f.erfuellt ? 'erfüllt' : 'NICHT erfüllt'}`
        : `liegt nicht in dieser Ebene (${i.fest} = ${wert(f, i.fest).toFixed(1)})`);
    punkt.append(t);
    g.append(punkt);
    g.append(text(sx(wert(f, x)) + 9, sy(wert(f, y)) - 8, f.name, {
      'font-weight': 600, fill: farbe, opacity: drin ? 1 : 0.6,
    }));
  }
  return el('div.diagramm-huelle', {}, [
    svg,
    el('div.mn-legende', {}, [
      el('span', {}, [el('i', { style: { background: '#1f5fa8' } }),
        einachsig ? 'Bruchzustände, Nulllinie waagrecht'
          : `Bruchzustände bei ${i.fest} = ${i.wert} ${GROESSE[i.fest].einheit}`]),
      el('span', {}, [el('i', { style: { background: GUT } }), 'erfüllt']),
      el('span', {}, [el('i', { style: { background: SCHLECHT } }), 'nicht erfüllt']),
      einachsig ? null : el('span', {}, [el('i', { style: { background: '#8895a8', opacity: 0.45 } }),
        `blass: anderes ${i.fest}`]),
    ]),
  ]);
}

function interaktionsblatt(kennung, name, daten, veraltet) {
  const wahl = wahlVon(kennung);
  const x = daten.einachsig ? 'M_y' : wahl.x;
  const y = daten.einachsig ? 'N' : wahl.y;
  return el('div.blatt', {}, [
    el('div.b-titel', { text: `Interaktionsdiagramm – ${name}` }),
    schnittsteuerung(kennung, daten.einachsig),
    el('div', { class: veraltet ? 'ist-veraltet' : '' }, [
      daten.interaktion ? interaktionsbild(daten.interaktion, daten.faelle, x, y, daten.einachsig)
        : leerzustand('Kein Interaktionsdiagramm.'),
    ]),
  ]);
}

// ===========================================================================
// Kurven
// ===========================================================================

function bereich(werte, spiel = 0.08) {
  const min = Math.min(...werte);
  const max = Math.max(...werte);
  const spanne = (max - min) || 1;
  return [min - spanne * spiel, max + spanne * spiel];
}

/** Einwirkung und Widerstand bei N_Ed, mit dem Weg dazwischen. */
function bemessungspunkt(daten, x, y, ed, rd, fall) {
  const farbe = fall.erfuellt ? GUT : SCHLECHT;
  if (rd) {
    daten.append(svgEl('line', {
      x1: x(ed[0]), y1: y(ed[1]), x2: x(rd[0]), y2: y(rd[1]),
      stroke: farbe, 'stroke-width': 1.4, 'stroke-dasharray': '5 3', opacity: 0.75,
    }));
    daten.append(svgEl('circle', {
      cx: x(rd[0]), cy: y(rd[1]), r: 4, fill: '#fff', stroke: farbe, 'stroke-width': 1.6,
    }));
  }
  const punkt = svgEl('circle', {
    cx: x(ed[0]), cy: y(ed[1]), r: 6, fill: farbe, stroke: '#fff', 'stroke-width': 2,
  });
  const t = svgEl('title');
  t.textContent = `${fall.name}\nα_eff = ${fall.grad_text} – ${fall.erfuellt ? 'erfüllt' : 'NICHT erfüllt'}`;
  punkt.append(t);
  daten.append(punkt);
  daten.append(text(x(ed[0]) + 9, y(ed[1]) - 8, fall.name, { 'font-weight': 600, fill: farbe }));
}

/** Die M-N-Linie in der Ebene des Lastfalls. */
function mnBild(daten, fall) {
  const mn = fall.mn;
  const ms = [...mn.punkte.map((p) => p.M), mn.einwirkung.M];
  const ns = [...mn.punkte.map((p) => p.N), mn.einwirkung.N];
  const schief = mn.richtung !== null && mn.richtung !== undefined;
  const { svg, daten: g, x, y } = achsenkreuz({
    breite: BREITE, hoehe: HOEHE, rand: RAND,
    attribute: { class: 'mn', xmlns: NR, role: 'img', 'aria-label': `M-N ${fall.name}` },
    x: {
      bereich: bereich(ms), teilung: {}, null: true,
      titel: schief ? 'M in Richtung der Einwirkung [kNm]' : GROESSE.M_y.titel,
    },
    y: { bereich: bereich(ns), teilung: {}, null: true, titel: GROESSE.N.titel },
  });
  g.append(svgEl('polygon', {
    points: mn.punkte.map((p) => `${x(p.M).toFixed(2)},${y(p.N).toFixed(2)}`).join(' '),
    fill: 'rgba(31,95,168,.07)', stroke: '#1f5fa8', 'stroke-width': 2, 'stroke-linejoin': 'round',
  }));
  bemessungspunkt(g, x, y, [mn.einwirkung.M, mn.einwirkung.N],
    mn.widerstand ? [mn.widerstand.M, mn.widerstand.N] : null, fall);
  return el('div.diagramm-huelle', {}, [
    svg,
    el('div.mn-legende', {}, [
      el('span', {}, [el('i', { style: { background: '#1f5fa8' } }),
        schief ? `Dehnungsfächer bei ψ = ${mn.neigung.toFixed(1)}° und gegenüber`
          : 'Dehnungsfächer, Nulllinie waagrecht']),
      el('span', {}, [el('i', { style: { background: fall.erfuellt ? GUT : SCHLECHT } }),
        `Einwirkung, α_eff = ${fall.grad_text}`]),
      schief ? el('span', { text: `Momentenrichtung ${mn.richtung.toFixed(1)}° zur y-Achse` }) : null,
    ]),
  ]);
}

/**
 * Der Widerstand rundum bei N_Ed -- M_y waagrecht, M_z senkrecht, beide im
 * selben Massstab: ein Kreis bleibt ein Kreis.
 */
function konturBild(daten, fall) {
  const k = fall.kontur;
  const alle = [...k.punkte.flatMap((p) => [p.M_y, p.M_z]), fall.M_y_Ed, fall.M_z_Ed];
  const r = Math.max(...alle.map(Math.abs)) * 1.12 || 1;
  const seite = 470;
  const { svg, daten: g, x, y } = achsenkreuz({
    breite: seite + 52, hoehe: seite, rand: { oben: 22, rechts: 22, unten: 46, links: 74 },
    attribute: { class: 'mn', xmlns: NR, role: 'img', 'aria-label': `M_y-M_z ${fall.name}` },
    x: { bereich: [-r, r], teilung: {}, null: true, titel: 'M_y [kNm]' },
    y: { bereich: [-r, r], teilung: {}, null: true, titel: 'M_z [kNm]' },
  });
  g.append(svgEl('polygon', {
    points: k.punkte.map((p) => `${x(p.M_y).toFixed(2)},${y(p.M_z).toFixed(2)}`).join(' '),
    fill: 'rgba(31,95,168,.07)', stroke: '#1f5fa8', 'stroke-width': 2, 'stroke-linejoin': 'round',
  }));
  bemessungspunkt(g, x, y, [fall.M_y_Ed, fall.M_z_Ed],
    k.widerstand ? [k.widerstand.M_y, k.widerstand.M_z] : null, fall);
  return el('div.diagramm-huelle', {}, [
    svg,
    el('div.mn-legende', {}, [
      el('span', {}, [el('i', { style: { background: '#1f5fa8' } }),
        `Widerstand bei N = ${k.N.toFixed(1)} kN, je Neigung der Nulllinie`]),
      el('span', { text: 'M_y > 0: Zug unten · M_z > 0: Zug links' }),
    ]),
  ]);
}

// ===========================================================================

function fallwahl(kennung, faelle, name) {
  if (faelle.length < 2) return null;
  return el('span.schalter.qa-fallwahl', { title: 'Lastfall wählen' }, faelle.map((f) => el('button.schalter-halb', {
    type: 'button', text: f.name, class: f.name === name ? 'ist-an' : '',
    on: { click: () => { gezeigt.set(kennung, f.name); aendern({}, 'diagramm'); } },
  })));
}

/**
 * Die Blätter einer Analyse für den Reiter «Diagramme». Fragt nach, wenn
 * die gezeigten Daten nicht mehr zur Eingabe passen.
 */
export function analyseBlaetter(kennung, name) {
  const wahl = wahlVon(kennung);
  const schnitt = { fest: festVon(wahl), wert: wahl.werte[festVon(wahl)] };
  const projektabdruck = abdruckVon(kennung);
  const abdruck = `${projektabdruck}|${schnitt.fest}|${schnitt.wert}`;
  let eintrag = vorrat.get(kennung);
  if (!eintrag || eintrag.abdruck !== abdruck) {
    // Nur der Schnitt geändert: gleich fragen -- gerechnet ist schon alles.
    const nurSchnitt = eintrag?.projektabdruck === projektabdruck;
    const alt = eintrag?.daten || eintrag?.alt || null;
    eintrag = {
      abdruck, projektabdruck, schnitt, daten: null, alt, fehler: null, uhr: null,
    };
    vorrat.set(kennung, eintrag);
    anfordern(kennung, eintrag, nurSchnitt ? 80 : 600);
  }
  const daten = eintrag.daten || eintrag.alt;
  const titel = (t) => el('div.b-titel', { text: `${t} – ${name}` });
  if (eintrag.fehler) {
    return [el('div.blatt', {}, [titel('Diagramme'), el('p.hinweis.hinweis-warnung', { text: eintrag.fehler })])];
  }
  if (!daten) return [el('div.blatt', {}, [titel('Diagramme'), leerzustand('Diagramme werden gerechnet …')])];
  const interaktion = interaktionsblatt(kennung, name, daten, !eintrag.daten);
  if (!daten.faelle.length) {
    return [interaktion, el('div.blatt', {}, [titel('Lastfall'), leerzustand('Kein Lastfall.')])];
  }

  const gewaehlt = daten.faelle.find((f) => f.name === gezeigt.get(kennung)) || daten.faelle[0];
  const veraltet = !eintrag.daten;
  const blatt = (t, inhalt) => el('div.blatt', { class: veraltet ? 'ist-veraltet' : '' }, [
    el('div.b-titel', { text: `${t} – ${gewaehlt.name}` }), inhalt]);
  const kopf = el('div.blatt', {}, [
    titel('Lastfall'),
    el('div.qa-fallkopf', {}, [
      fallwahl(kennung, daten.faelle, gewaehlt.name),
      el('span', {
        text: `N = ${gewaehlt.N_Ed.toFixed(1)} kN · M_y = ${gewaehlt.M_y_Ed.toFixed(1)} kNm`
          + (daten.einachsig ? '' : ` · M_z = ${gewaehlt.M_z_Ed.toFixed(1)} kNm`)
          + (daten.laengszug ? ' (mit Längszugkraft)' : ''),
      }),
      veraltet ? el('span.qa-nachfuehren', { text: 'wird nachgeführt …' }) : null,
    ]),
  ]);
  return [
    interaktion,
    kopf,
    gewaehlt.bruch ? blatt('Bruchzustand', bruchbild(daten, gewaehlt)) : null,
    blatt('M-N in der Ebene des Lastfalls', mnBild(daten, gewaehlt)),
    gewaehlt.kontur ? blatt('M_y-M_z bei N_Ed', konturBild(daten, gewaehlt)) : null,
    gewaehlt.schub ? blatt('Schubfluss', schubbild(daten, gewaehlt)) : null,
  ].filter(Boolean);
}
