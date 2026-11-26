/**
 * qa_diagramme.js -- die Diagramme einer Querschnittsanalyse.
 *
 * Zuerst der Querschnitt, wie gezeichnet, auch ohne Lastfall: Flächen in
 * der Farbe ihres Baustoffs, Stäbe, Aussenmasse und der Schwerpunkt mit
 * den Achsen y und z -- in den Stilen des Zeichenfensters.
 *
 * Dann das Interaktionsdiagramm -- das einzige: die Fläche aller
 * Bruchzustände im Raum (N, M_y, M_z), geschnitten bei einem festen Wert
 * einer Grösse. Welche zwei auf den Achsen stehen, wird gewählt; die dritte
 * bekommt ihren Wert im Zahlenfeld. Lastfälle in dieser Ebene stehen
 * kräftig, die übrigen blass; liegt auch der Widerstand des Nachweises in
 * ihr, führt ein gestrichelter Weg dorthin. Ein Klick auf einen Lastfall
 * legt den Schnitt durch ihn.
 *
 * Darunter je Lastfall, umschaltbar:
 *
 *   Bruchzustand    der Schnitt mit Nulllinie, Druckzone und der Dehnung
 *                   jedes Stabs -- gezogen kupfer, gedrückt blau;
 *   Schubfluss      je Schubwand ein Pfeil, so lang wie ihr Fluss.
 *
 * Ein Querschnitt ohne Nachweise -- aus Holz etwa -- zeigt nur sich und
 * den Satz des Kerns, warum es nicht mehr gibt.
 *
 * Die Daten kommen aus einer eigenen Anfrage (`analysediagramme`): die
 * Fläche braucht Bruchzustände, die kein Nachweis braucht, und soll nicht
 * jede Rechnung verlangsamen. Gefragt wird erst, wenn die Rechnung zur
 * aktuellen Eingabe durch ist -- dann liegen die Nachweise im Speicher des
 * Kerns, und es kommt nur die Fläche dazu. Bis dahin bleiben die alten
 * Bilder stehen, blass.
 *
 * Gerechnet wird hier nichts: Nulllinie, Druckzone, Dehnungen, Flüsse, die
 * Fläche und die Widerstände kommen fertig aus dem Kern.
 */

import {
  achsenkreuz, bemessungspunkt, flaeche, legende, NR, punkt, strich, urteilsfarbe, urteilslegende,
} from './achsen.js';
import { api } from './api.js';
import { karte, wahlSchalter } from './bausteine.js';
import { zahlText } from './cad_ansicht.js';
import { mitTitel } from './cad_app.js';
import {
  el, leerzustand, svgEl, zahlfeld,
} from './dom.js';
import { aendern, ansichtVon, zustand } from './zustand.js';

const BREITE = 640;
const HOEHE = 470;
const RAND = { oben: 22, rechts: 22, unten: 46, links: 74 };

const ZUG = '#b8622a';
const DRUCK = '#1f5fa8';
const VIOLETT = '#8b5cf6';

/** Die drei Grössen des Interaktionsdiagramms: Achsentitel, Einheit, Feld im Lastfall. */
const GROESSE = {
  N: { titel: 'N [kN]   (Zug positiv)', einheit: 'kN', schritt: 50, feld: 'N_Ed' },
  M_y: { titel: 'M_y [kNm]   (positiv: Zug unten)', einheit: 'kNm', schritt: 10, feld: 'M_y_Ed' },
  M_z: { titel: 'M_z [kNm]   (positiv: Zug links)', einheit: 'kNm', schritt: 10, feld: 'M_z_Ed' },
};

/**
 * Wie nah ein Wert dem festen kommen muss, damit sein Punkt in der Ebene
 * liegt -- ein Tausendstel kN bzw. kNm, weit unter dem, was man sieht. Der
 * Widerstand des Nachweises ist gesucht, nicht eingetippt: er trifft den
 * Wert nur bis auf die Schranke der Suche.
 */
const IN_DER_EBENE = 1e-3;

/*
 * Was sich die Ansicht je Analyse merkt (`ansichtVon`): `diagramme`, die
 * letzte Antwort {frage, fassung, schnitt, daten, alt, fehler, uhr};
 * `gezeigt`, der Name des gezeigten Lastfalls; `schnitt`, was das
 * Interaktionsdiagramm zeigt.
 */

/**
 * Was das Interaktionsdiagramm zeigt: die Achsen und je Grösse ihr Wert,
 * wenn sie die feste ist. Ein Wert bleibt stehen, wenn die Achsen wechseln
 * -- wer zurückschaltet, findet ihn wieder.
 */
function wahlVon(kennung) {
  const ansicht = ansichtVon(kennung);
  ansicht.schnitt ??= { x: 'M_y', y: 'N', werte: { N: 0, M_y: 0, M_z: 0 } };
  return ansicht.schnitt;
}

/** Die Grösse, die auf keiner Achse steht. */
function festVon(wahl) {
  return Object.keys(GROESSE).find((g) => g !== wahl.x && g !== wahl.y);
}

/**
 * Fragt nach den Diagrammen -- aber erst, wenn gerade nicht gerechnet wird.
 * Läuft die Rechnung noch, wartet die Anfrage; danach liegen die Nachweise
 * im Speicher des Kerns, und es kommt nur die Fläche dazu.
 */
function anfordern(kennung, eintrag, verzug = 600) {
  clearTimeout(eintrag.uhr);
  eintrag.uhr = setTimeout(() => {
    if (ansichtVon(kennung).diagramme !== eintrag) return;
    if (zustand.rechnetGerade) {
      anfordern(kennung, eintrag);
      return;
    }
    api.analysediagramme(zustand.projekt, kennung, eintrag.schnitt).then((antwort) => {
      if (ansichtVon(kennung).diagramme !== eintrag) return;
      eintrag.daten = antwort.diagramme;
      aendern();
    }).catch((fehler) => {
      if (ansichtVon(kennung).diagramme !== eintrag) return;
      eintrag.fehler = fehler.message;
      aendern();
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

/** Der Schwerpunkt S -- wie im Zeichenfenster (qa_zeichnung.js), in allen Bildern gleich. */
function schwerpunktZeichnen(gruppe, zeichnung, bild) {
  const [x, y] = bild(zeichnung.schwerpunkt);
  const s = svgEl('g', { class: 'cad-schwerpunkt' });
  s.append(
    svgEl('circle', { cx: x.toFixed(1), cy: y.toFixed(1), r: 6 }),
    svgEl('path', { d: `M${(x - 9).toFixed(1)} ${y.toFixed(1)} H${(x + 9).toFixed(1)} `
      + `M${x.toFixed(1)} ${(y - 9).toFixed(1)} V${(y + 9).toFixed(1)}` }),
    text(x + 9, y - 7, 'S', { class: 'cad-schwerpunkttext', fill: null, 'font-size': null }),
  );
  gruppe.append(s);
}

/** So hoch steht ein Querschnitt höchstens im Bild, in px -- ein flacher bekommt weniger. */
const QS_HOEHE = 420;
/** Platz um den Schnitt, in px: links und unten für die Masse, oben und rechts für z und y. */
const QS_RAND = { oben: 28, rechts: 34, unten: 48, links: 52 };

/** Eine Probe für die Legende im Stil des Zeichenfensters: Fläche, Stab oder Linie. */
function probe(klasse, form = 'flaeche') {
  const svg = svgEl('svg', {
    width: 18, height: 12, viewBox: '0 0 18 12', 'aria-hidden': 'true', class: 'qs-probe',
  });
  svg.append({
    flaeche: () => svgEl('rect', { x: 1, y: 1, width: 16, height: 10, class: klasse }),
    stab: () => svgEl('circle', { cx: 9, cy: 6, r: 4, class: klasse }),
    linie: () => svgEl('path', { d: 'M2 6 H16', class: klasse }),
  }[form]());
  return svg;
}

/** Namen ohne Doppel, in der Folge ihres ersten Auftretens. */
const einmal = (namen) => [...new Set(namen)];

/** Die Aussenmasse dessen, was Material hat: unten die Breite, links die Höhe -- wie im Zeichenfenster. */
function aussenmasse(gruppe, zeichnung, bild) {
  const ecken = zeichnung.polygone.filter((p) => p.material).flatMap((p) => p.punkte);
  if (!ecken.length) return;
  const ys = ecken.map((p) => p[0]);
  const zs = ecken.map((p) => p[1]);
  const [y0, y1, z0, z1] = [Math.min(...ys), Math.max(...ys), Math.min(...zs), Math.max(...zs)];
  const [xl, hu] = bild([y0, z0]);
  const [xr, ho] = bild([y1, z1]);
  const unten = hu + 24;
  const links = xl - 24;
  const breite = text((xl + xr) / 2, unten - 5, zahlText(y1 - y0),
    { class: 'cad-masstext', 'text-anchor': 'middle', fill: null, 'font-size': null });
  const hoehe = text(links - 5, (hu + ho) / 2, zahlText(z1 - z0), {
    class: 'cad-masstext', 'text-anchor': 'middle', fill: null, 'font-size': null,
    transform: `rotate(-90 ${(links - 5).toFixed(1)} ${((hu + ho) / 2).toFixed(1)})`,
  });
  gruppe.append(
    svgEl('path', {
      d: `M${xl.toFixed(1)} ${unten.toFixed(1)} H${xr.toFixed(1)} `
        + `M${xl.toFixed(1)} ${(unten - 5).toFixed(1)} v10 M${xr.toFixed(1)} ${(unten - 5).toFixed(1)} v10 `
        + `M${links.toFixed(1)} ${ho.toFixed(1)} V${hu.toFixed(1)} `
        + `M${(links - 5).toFixed(1)} ${ho.toFixed(1)} h10 M${(links - 5).toFixed(1)} ${hu.toFixed(1)} h10`,
      class: 'cad-mass',
    }),
    breite, hoehe,
  );
}

/**
 * Der Querschnitt, wie gezeichnet -- auch ohne Lastfall: die Flächen in der
 * Farbe ihres Baustoffs, Aussparungen gestrichelt, Stäbe, verschmierte
 * Linien und Spannglieder -- diese so gross wie ihre Fläche --, unten und
 * links die Aussenmasse dessen, was Material hat, und der
 * Schwerpunkt S mit den Achsen y und z, um die die Momente drehen. Die
 * Masse in mm.
 */
function querschnittbild(z) {
  const R = QS_RAND;
  const ecken = z.polygone.flatMap((p) => p.punkte);
  const ys = ecken.map((p) => p[0]);
  const zs = ecken.map((p) => p[1]);
  const [y0, y1, z0, z1] = [Math.min(...ys), Math.max(...ys), Math.min(...zs), Math.max(...zs)];
  const m = Math.min((BREITE - R.links - R.rechts) / ((y1 - y0) || 1),
    (QS_HOEHE - R.oben - R.unten) / ((z1 - z0) || 1));
  const hoehe = Math.round(R.oben + R.unten + m * (z1 - z0));
  const ox = R.links + (BREITE - R.links - R.rechts - m * (y1 - y0)) / 2 - m * y0;
  const oy = R.oben + m * z1;
  const bild = ([y, w]) => [ox + m * y, oy - m * w];
  const svg = svgEl('svg', {
    viewBox: `0 0 ${BREITE} ${hoehe}`, class: 'qs', xmlns: NR, role: 'img', 'aria-label': 'Querschnitt',
  });
  const g = svgEl('g');
  for (const p of [...z.polygone].sort((a, b) => a.tiefe - b.tiefe)) {
    g.append(mitTitel(svgEl('path', {
      d: pfad(bild, p.punkte), class: p.material ? `cad-${p.material}` : 'cad-loch',
    }), [`${p.name}: ${p.stoff || 'Aussparung'}`]));
  }
  // Die Achsen durch den Schwerpunkt, etwas über den Schnitt hinaus.
  const [sx, sy] = bild(z.schwerpunkt);
  const [xl, hu] = bild([y0, z0]);
  const [xr, ho] = bild([y1, z1]);
  g.append(
    svgEl('path', {
      d: `M${(xl - 12).toFixed(1)} ${sy.toFixed(1)} H${(xr + 14).toFixed(1)} `
        + `M${sx.toFixed(1)} ${(hu + 12).toFixed(1)} V${(ho - 14).toFixed(1)}`,
      class: 'cad-achse',
    }),
    text(xr + 18, sy + 4, 'y', { class: 'cad-achstext', fill: null, 'font-size': null }),
    text(sx + 5, ho - 16, 'z', { class: 'cad-achstext', fill: null, 'font-size': null }),
  );
  for (const l of z.flaechenlinien) {
    g.append(mitTitel(svgEl('path', { d: pfad(bild, [l.von, l.bis], false), class: 'cad-linie-flaeche' }),
      [`${l.name}: ${l.stahl}, verschmiert`]));
  }
  for (const s of z.staebe) {
    const [x, y] = bild([s.y, s.z]);
    g.append(mitTitel(svgEl('circle', {
      cx: x.toFixed(1), cy: y.toFixed(1), r: Math.max(2.4, (m * s.d) / 2).toFixed(1), class: 'cad-stab',
    }), [`${s.name}: ⌀${s.d} ${s.stahl}`]));
  }
  for (const s of z.spannglieder) {
    const [x, y] = bild([s.y, s.z]);
    g.append(mitTitel(svgEl('circle', {
      cx: x.toFixed(1), cy: y.toFixed(1), r: Math.max(2.4, (m * s.d) / 2).toFixed(1), class: 'cad-spannglied',
    }), [`${s.name}: ${s.stahl}`]));
  }
  aussenmasse(g, z, bild);
  schwerpunktZeichnen(g, z, bild);
  svg.append(g);
  const [yS, zS] = z.schwerpunkt;
  const flaechen = z.polygone.filter((p) => p.material);
  return el('div.diagramm-huelle', {}, [
    svg,
    legende([
      ...einmal(flaechen.map((p) => `${p.material}|${p.stoff}`)).map((schluessel) => {
        const [art, stoff] = schluessel.split('|');
        return [probe(`cad-${art}`), stoff];
      }),
      z.polygone.some((p) => !p.material) ? [probe('cad-loch'), 'Aussparung'] : null,
      ...einmal(z.staebe.map((s) => s.stahl)).map((stahl) => [probe('cad-stab', 'stab'), `Stäbe ${stahl}`]),
      ...einmal(z.flaechenlinien.map((l) => l.stahl))
        .map((stahl) => [probe('cad-linie-flaeche', 'linie'), `verschmiert ${stahl}`]),
      ...einmal(z.spannglieder.map((s) => s.stahl))
        .map((stahl) => [probe('cad-spannglied', 'stab'), `Spannglieder ${stahl}`]),
      `S: y = ${zahlText(yS)} mm, z = ${zahlText(zS)} mm · Masse in mm`,
    ]),
  ]);
}

/**
 * Der Bruchzustand im Schnitt: Druckzone getönt, Nulllinie gestrichelt, die
 * Stäbe nach dem Vorzeichen ihrer Dehnung gefärbt. Ein Spannglied steht in
 * seiner eigenen Farbe: gezogen ist es fast immer, auch wo der Beton an
 * seiner Stelle gestaucht ist -- sein Titel nennt die Dehnung des Betons.
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
  for (const s of b.spannglieder) {
    const [x, y] = bild([s.y, s.z]);
    g.append(mitTitel(svgEl('circle', { cx: x, cy: y, r: Math.max(2.6, (m * s.d) / 2), class: 'cad-spannglied' }),
      [`ε = ${s.eps.toFixed(2)} ‰ – die Dehnung des Betons an seiner Stelle`]));
  }
  schwerpunktZeichnen(g, z, bild);
  svg.append(g);
  return el('div.diagramm-huelle', {}, [
    svg,
    legende([
      [flaeche(DRUCK), `Druckzone, x = ${b.x.toFixed(1)} mm`],
      [punkt(ZUG), 'Stab gezogen'],
      [punkt(DRUCK, { hohl: true }), 'Stab gedrückt'],
      b.spannglieder.length ? [probe('cad-spannglied', 'stab'), 'Spannglied'] : null,
      b.d > 0 ? `d = ${b.d.toFixed(1)} mm` : null,
    ]),
  ]);
}

/**
 * Der Schubfluss: je Schubwand, wie der Nachweis sie sieht -- an ihren
 * Knoten geteilt --, ein Band und ein Pfeil in Richtung ihres Flusses, so
 * lang wie er stark ist. Eine Wand, die nicht hält, ist rot.
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
  for (const w of s.waende) {
    const l = Math.hypot(w.bis[0] - w.von[0], w.bis[1] - w.von[1]) || 1;
    const n = [(-(w.bis[1] - w.von[1]) / l) * (w.dicke / 2), ((w.bis[0] - w.von[0]) / l) * (w.dicke / 2)];
    const ecken = [
      [w.von[0] + n[0], w.von[1] + n[1]], [w.bis[0] + n[0], w.bis[1] + n[1]],
      [w.bis[0] - n[0], w.bis[1] - n[1]], [w.von[0] - n[0], w.von[1] - n[1]],
    ];
    const farbe = w.erfuellt !== false ? VIOLETT : urteilsfarbe(false);
    g.append(svgEl('path', {
      d: pfad(bild, ecken), fill: farbe, 'fill-opacity': 0.14, stroke: farbe, 'stroke-opacity': 0.6,
    }));
  }
  // Pfeillänge: der stärkste Fluss bekommt 70 px, alle anderen im Verhältnis.
  const groesster = Math.max(...s.waende.map((w) => Math.abs(w.q)), 1e-9);
  for (const w of s.waende) {
    if (Math.abs(w.q) < 1e-6 * groesster) continue;
    const [ax, ay] = bild(w.von);
    const [bx, by] = bild(w.bis);
    const lang = Math.hypot(bx - ax, by - ay) || 1;
    const richtung = [((bx - ax) / lang) * Math.sign(w.q), ((by - ay) / lang) * Math.sign(w.q)];
    const laenge = Math.min(70 * Math.abs(w.q) / groesster, lang * 0.8);
    const [mx, my] = [(ax + bx) / 2, (ay + by) / 2];
    const [x0, y0] = [mx - (richtung[0] * laenge) / 2, my - (richtung[1] * laenge) / 2];
    const [x1, y1] = [mx + (richtung[0] * laenge) / 2, my + (richtung[1] * laenge) / 2];
    const winkel = Math.atan2(richtung[1], richtung[0]);
    const spitze = (w) => `${(x1 - 9 * Math.cos(winkel + w)).toFixed(1)},${(y1 - 9 * Math.sin(winkel + w)).toFixed(1)}`;
    const farbe = w.erfuellt !== false ? '#5b3fb8' : urteilsfarbe(false);
    g.append(
      svgEl('line', { x1: x0, y1: y0, x2: x1, y2: y1, stroke: farbe, 'stroke-width': 2.2 }),
      svgEl('polygon', { points: `${x1.toFixed(1)},${y1.toFixed(1)} ${spitze(0.4)} ${spitze(-0.4)}`, fill: farbe }),
    );
    // Die Zahl quer neben dem Pfeil, auf der Seite zur Mitte des Bildes hin.
    const quer = [-richtung[1], richtung[0]];
    const t = text(mx + quer[0] * 14, my + quer[1] * 14 + 4, `${Math.abs(w.q).toFixed(1)}`, {
      'text-anchor': 'middle', 'font-weight': 600, fill: farbe,
      'paint-order': 'stroke', stroke: '#fff', 'stroke-width': 3,
    });
    g.append(t);
  }
  schwerpunktZeichnen(g, z, bild);
  svg.append(g);
  return el('div.diagramm-huelle', {}, [
    svg,
    legende([
      'Pfeile: Schubfluss q in kN/m, in seiner Richtung',
      // Was geneigte Spannglieder selbst tragen -- die Wände tragen den Rest.
      s.V_p == null ? null
        : `Geneigte Spannglieder: V_p = ${s.V_p.toFixed(1)} kN – die Wände tragen V_z − V_p`,
      // Je Wand ihre ganze Kraft gegen ihren Widerstand, nicht je Meter.
      ...s.waende.map((w) => el('span', {
        style: { color: w.erfuellt ? 'inherit' : 'var(--schlecht)' },
        text: `${w.name}: V_Ed = ${w.V_Ed.toFixed(1)} kN, V_Rd = ${w.V_Rd.toFixed(1)} kN, `
          + `α_eff = ${w.grad_text} (α = ${w.alpha}°)`,
      })),
    ]),
  ]);
}

// ===========================================================================
// Interaktionsdiagramm
// ===========================================================================

function achsenwahl(kennung, achse) {
  const wahl = wahlVon(kennung);
  return wahlSchalter({
    werte: Object.keys(GROESSE).map((g) => ({ wert: g, beschriftung: g, titel: GROESSE[g].titel })),
    gewaehlt: wahl[achse],
    titel: achse === 'x' ? 'Grösse auf der waagrechten Achse' : 'Grösse auf der senkrechten Achse',
    setzen: (neu) => {
      // Steht die Grösse schon auf der anderen Achse, tauschen die beiden.
      const andere = achse === 'x' ? 'y' : 'x';
      if (wahl[andere] === neu) wahl[andere] = wahl[achse];
      wahl[achse] = neu;
      aendern();
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
    // Kein «label» um die Schalter: ein Klick auf den Text löste sonst ihre
    // erste Stellung aus.
    el('span.qa-achsenwahl', {}, ['x-Achse ', achsenwahl(kennung, 'x')]),
    el('span.qa-achsenwahl', {}, ['y-Achse ', achsenwahl(kennung, 'y')]),
    el('label', {}, [
      `bei ${fest} = `,
      zahlfeld({
        wert: wahl.werte[fest], schritt: GROESSE[fest].schritt, leer: 0,
        titel: `Fester Wert von ${fest} in ${GROESSE[fest].einheit}; die Fläche wird dort geschnitten`,
        beiAenderung: (v) => { wahl.werte[fest] = v; aendern(); },
      }),
      ` ${GROESSE[fest].einheit}`,
    ]),
  ]);
}

function bereich(werte, spiel = 0.08) {
  const min = Math.min(...werte);
  const max = Math.max(...werte);
  const spanne = (max - min) || 1;
  return [min - spanne * spiel, max + spanne * spiel];
}

/**
 * Das Bild: der Schnitt durch die Fläche, dazu jeder Lastfall. In dieser
 * Ebene liegt einer, wenn seine feste Grösse den Wert hat -- dann kräftig,
 * grün oder rot wie sein Nachweis. Sonst blass: er gehört zu einem anderen
 * Schnitt. Liegt auch sein Widerstand in der Ebene, zeigt ein gestrichelter
 * Weg, wie der Nachweis gemessen hat: bei N_Ed, in Richtung des Moments.
 * Zwei Momente auf den Achsen bekommen denselben Massstab.
 */
function interaktionsbild(kennung, i, faelle, x, y, einachsig) {
  const wert = (f, g) => f[GROESSE[g].feld];
  const punkte = i.punkte.map((p) => [p[x], p[y]]);
  if (!punkte.length) {
    return leerzustand(`Bei ${i.fest} = ${i.wert} ${GROESSE[i.fest].einheit} gibt es keinen Bruchzustand`,
      'Die Ebene trifft die Fläche der Widerstände nicht.');
  }
  const passt = (f) => einachsig || Math.abs(wert(f, i.fest) - i.wert) <= IN_DER_EBENE;
  const mitWeg = (f) => passt(f) && f.widerstand
    && (einachsig || Math.abs(f.widerstand[i.fest] - i.wert) <= IN_DER_EBENE);
  // Ein Klick legt den Schnitt durch den Lastfall. Einachsig gibt es nur
  // eine Ebene, und in ihr liegen alle.
  const durchLegen = (f) => {
    if (einachsig) return;
    wahlVon(kennung).werte[i.fest] = wert(f, i.fest);
    aendern();
  };
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
    const kreis = bemessungspunkt(g, {
      ein: [sx(wert(f, x)), sy(wert(f, y))],
      widerstand: mitWeg(f) ? [sx(f.widerstand[x]), sy(f.widerstand[y])] : null,
      // Ein Fall ohne Einwirkung hat nichts nachzuweisen: grau, mit seinem Satz.
      farbe: drin && !f.hinweis ? urteilsfarbe(f.erfuellt) : '#8895a8',
      name: f.name,
      titel: `${f.name}\nN = ${f.N_Ed.toFixed(1)} kN, M_y = ${f.M_y_Ed.toFixed(1)} kNm, `
        + `M_z = ${f.M_z_Ed.toFixed(1)} kNm\n`
        + (drin ? f.hinweis || `α_eff = ${f.grad_text} – ${f.erfuellt ? 'erfüllt' : 'NICHT erfüllt'}`
          : `liegt nicht in dieser Ebene (${i.fest} = ${wert(f, i.fest).toFixed(1)})`)
        + (einachsig ? '' : `\nKlick: Schnitt durch diesen Lastfall (${i.fest} = ${wert(f, i.fest).toFixed(1)})`),
      deckung: drin ? 1 : 0.45,
    });
    if (!einachsig) kreis.style.cursor = 'pointer';
    kreis.addEventListener('click', () => durchLegen(f));
  }
  return el('div.diagramm-huelle', {}, [
    svg,
    legende([
      [strich('#1f5fa8', { breite: 2 }), einachsig ? 'Bruchzustände, Nulllinie waagrecht'
        : `Bruchzustände bei ${i.fest} = ${i.wert} ${GROESSE[i.fest].einheit}`],
      ...urteilslegende(),
      einachsig ? null : [punkt('#8895a8', { deckung: 0.45 }),
        `blass: anderes ${i.fest} – Klick legt den Schnitt durch ihn`],
      faelle.some(mitWeg) ? '– – –  Weg zum Widerstand des Nachweises' : null,
    ]),
  ]);
}

function interaktionskarte(kennung, daten, veraltet) {
  const wahl = wahlVon(kennung);
  const x = daten.einachsig ? 'M_y' : wahl.x;
  const y = daten.einachsig ? 'N' : wahl.y;
  // Die alte Fläche nur bis zur Antwort, und nur bei derselben festen
  // Grösse: nach einem Wechsel der Achsen läge sonst der Schnitt bei
  // M_z = 0 in den Achsen M_y und N (bis 2026-11-19).
  const anderer = veraltet && !daten.einachsig && daten.interaktion?.fest !== festVon(wahl);
  let bild = leerzustand('Kein Interaktionsdiagramm.');
  if (anderer) bild = leerzustand('Der Schnitt für die neuen Achsen wird gerechnet …');
  else if (daten.interaktion) {
    bild = interaktionsbild(kennung, daten.interaktion, daten.faelle, x, y, daten.einachsig);
  }
  return karte('Interaktionsdiagramm', [
    schnittsteuerung(kennung, daten.einachsig),
    el('div', { class: veraltet ? 'ist-veraltet' : '' }, [bild]),
  ], { bild });
}

// ===========================================================================

function fallwahl(kennung, faelle, name) {
  if (faelle.length < 2) return null;
  return el('span.schalter.qa-fallwahl', { title: 'Lastfall wählen' }, faelle.map((f) => el('button.schalter-halb', {
    type: 'button', text: f.name, class: f.name === name ? 'ist-an' : '',
    on: { click: () => { ansichtVon(kennung).gezeigt = f.name; aendern(); } },
  })));
}

/**
 * Die Karten einer Analyse für den Reiter «Diagramme» -- das Panel darum
 * baut bericht.js. Fragt nach, wenn sich das Projekt oder der Schnitt seit
 * der letzten Frage geändert hat; ob sich für diese Analyse etwas geändert
 * hat, weiss der Kern.
 */
export function analyseKarten(kennung) {
  const ansicht = ansichtVon(kennung);
  const wahl = wahlVon(kennung);
  const schnitt = { fest: festVon(wahl), wert: wahl.werte[festVon(wahl)] };
  const frage = `${zustand.fassung}|${schnitt.fest}|${schnitt.wert}`;
  let eintrag = ansicht.diagramme;
  if (!eintrag || eintrag.frage !== frage) {
    // Nur der Schnitt geändert: gleich fragen -- gerechnet ist schon alles.
    const nurSchnitt = eintrag?.fassung === zustand.fassung;
    const alt = eintrag?.daten || eintrag?.alt || null;
    eintrag = {
      frage, fassung: zustand.fassung, schnitt, daten: null, alt, fehler: null, uhr: null,
    };
    ansicht.diagramme = eintrag;
    anfordern(kennung, eintrag, nurSchnitt ? 80 : 600);
  }
  const daten = eintrag.daten || eintrag.alt;
  if (eintrag.fehler) {
    return [karte(null, [el('p.hinweis.hinweis-warnung', { text: eintrag.fehler })])];
  }
  if (!daten) return [karte(null, [leerzustand('Diagramme werden gerechnet …')])];
  const veraltet = !eintrag.daten;
  const umriss = querschnittbild(daten.zeichnung);
  const querschnitt = karte('Querschnitt', [umriss],
    { bild: umriss.querySelector('svg'), klasse: veraltet ? 'ist-veraltet' : '' });
  if (daten.ohne_nachweis) return [querschnitt, karte(null, [leerzustand(daten.ohne_nachweis)])];
  const interaktion = interaktionskarte(kennung, daten, veraltet);
  if (!daten.faelle.length) {
    return [querschnitt, interaktion, karte('Lastfall', [leerzustand('Kein Lastfall.')])];
  }

  const gewaehlt = daten.faelle.find((f) => f.name === ansicht.gezeigt) || daten.faelle[0];
  const bildkarte = (t, bild) => karte(`${t} – ${gewaehlt.name}`, [bild],
    { bild, klasse: veraltet ? 'ist-veraltet' : '' });
  // Die Wahl des Falls gilt für die Bilder darunter -- über die ganze Breite.
  const kopf = karte('Lastfall', [
    el('div.qa-fallkopf', {}, [
      fallwahl(kennung, daten.faelle, gewaehlt.name),
      el('span', {
        text: `N = ${gewaehlt.N_Ed.toFixed(1)} kN · M_y = ${gewaehlt.M_y_Ed.toFixed(1)} kNm`
          + (daten.einachsig ? '' : ` · M_z = ${gewaehlt.M_z_Ed.toFixed(1)} kNm`)
          + (daten.laengszug ? ' (mit Längszugkraft)' : ''),
      }),
      veraltet ? el('span.qa-nachfuehren', { text: 'wird nachgeführt …' }) : null,
    ]),
  ], { klasse: 'ist-breit' });
  return [
    querschnitt,
    interaktion,
    kopf,
    // Ohne Bild sagt die Karte, warum -- bis 2026-11-19 fehlte sie still. Den
    // Schubfluss zeigt sie nur, wo der Kern etwas zu sagen hat: ohne
    // Schubwand und ohne Querkraft ist Schub kein Thema.
    gewaehlt.bruch ? bildkarte('Bruchzustand', bruchbild(daten, gewaehlt))
      : bildkarte('Bruchzustand', leerzustand(gewaehlt.ohne_bruch || 'Kein Bruchzustand.')),
    gewaehlt.schub ? bildkarte('Schubfluss', schubbild(daten, gewaehlt))
      : gewaehlt.ohne_schub ? bildkarte('Schubfluss', leerzustand(gewaehlt.ohne_schub)) : null,
  ].filter(Boolean);
}
