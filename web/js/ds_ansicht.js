/**
 * ds_ansicht.js -- eine Leiste der Durchstanzbewehrung in der Ansicht.
 *
 * Längs der Leiste geschnitten und massstäblich: die Platte mit ihrer
 * Zugbewehrung -- die Lage längs als Linie, die quer als Punkte --, die
 * Stütze auf der Druckseite, bei der Decke unten, bei der Bodenplatte oben,
 * ein Stahlpilz, wo es einen gibt, und die Elemente der Leiste: Anker mit
 * zwei Köpfen oder Bügelschenkel, die an beiden Enden umbiegen. Hinterlegt
 * ist der Bereich, in dem sie zählen (0.35·d_v bis d_v, Gleichung (68)),
 * auf der Zugseite mit seinen Grenzen bemasst; auf der Druckseite stehen die
 * Abstände der Elemente ab dem Rand der gestützten Fläche, rechts c_v, h_A,
 * c und h.
 *
 * Alle Zahlen kommen aus dem Kern (opencivil/web/durchstanzdaten.py), in mm:
 * x ab dem Rand der gestützten Fläche, z ab der Druckseite. Hier wird nur
 * gezeichnet; Köpfe und Biegungen schematisch, ihre Grösse nach dem
 * Durchmesser.
 */

import { karte } from './bausteine.js';
import { el, svgEl } from './dom.js';
import { BREITE, gruppe, legende, linie, mass, text, zahl } from './gb_skizze.js';

/** Platz neben der Platte, in px: links, rechts für die Masse der Höhe. */
const LINKS = 16;
const RECHTS = 160;
/** Platz über der Zugseite für die Masse des Bereichs, unter der Druckseite für Stütze und Abstände. */
const ZUGSEITE = 54;
const DRUCKSEITE = 74;
/** So weit ragt die Stütze aus der Platte, in px. */
const STUMPF = 62;
/** So weit stehen die Masslinien vor der Platte, in px. */
const ABSTAENDE = 30;
const BEREICH = [17, 36];

/** Eine Zahl in mm, ganz -- so steht sie in der Herleitung. */
const ganz = (x) => zahl(x, 0);

/** «x y» auf eine Stelle. */
const p = (x, y) => `${x.toFixed(1)} ${y.toFixed(1)}`;

function rechteck(x0, y0, x1, y1, klasse) {
  return svgEl('rect', {
    x: Math.min(x0, x1).toFixed(1), y: Math.min(y0, y1).toFixed(1),
    width: Math.abs(x1 - x0).toFixed(1), height: Math.abs(y1 - y0).toFixed(1), class: klasse,
  });
}

/** Eine Bruchlinie von `[x0, y0]` nach `[x1, y1]`, in der Mitte geknickt: dort geht das Bauteil weiter. */
function bruch([x0, y0], [x1, y1]) {
  const l = Math.hypot(x1 - x0, y1 - y0);
  const [ux, uy] = [(x1 - x0) / l, (y1 - y0) / l];
  const [mx, my] = [(x0 + x1) / 2, (y0 + y1) / 2];
  const punkt = (t, q) => p(mx + t * ux - q * uy, my + t * uy + q * ux);
  return svgEl('path', {
    d: `M${p(x0, y0)} L${punkt(-6, 0)} L${punkt(-2, 4)} L${punkt(2, -4)} L${punkt(6, 0)} L${p(x1, y1)}`,
    class: 'ds-bruch',
  });
}

/**
 * Massstab und Lage: was von links nach rechts ins Bild kommt -- die Stütze
 * bis zu ihrer Achse, ist sie weiter als 0.8·h, nur so viel --, und wo die
 * Druckseite liegt. `X(x)` und `Z(z)` bilden mm auf px ab; `aussen` zeigt
 * in px von der Druckseite aus der Platte hinaus.
 */
function abbildung(a) {
  const letzter = a.radien[a.radien.length - 1];
  const rechts = Math.max(letzter, a.zaehlt[1]) + 0.45 * a.h;
  const kurz = a.stuetze.rand - 0.8 * a.h;
  const mitAchse = a.stuetze.achse >= kurz;
  const links = mitAchse ? a.stuetze.achse : kurz;
  const m = (BREITE - LINKS - RECHTS) / (rechts - links);
  const unten = a.druckseite === 'unten';
  const druck = unten ? ZUGSEITE + a.h * m : DRUCKSEITE;
  const aussen = unten ? 1 : -1;
  return {
    m, links, rechts, mitAchse, aussen, letzter,
    hoehe: ZUGSEITE + a.h * m + DRUCKSEITE,
    X: (x) => LINKS + (x - links) * m,
    Z: (z) => druck - aussen * z * m,
  };
}

/** Platte und Stütze aus Beton, ohne Fuge dazwischen; ein Pilz darin. */
function beton(a, b) {
  const { X, Z, aussen } = b;
  const [x0, x1, rand] = [X(b.links), X(b.rechts), X(a.stuetze.rand)];
  const fuss = Z(0) + aussen * STUMPF;
  const teile = [
    rechteck(x0, Z(0), x1, Z(a.h), 'ds-beton'),
    rechteck(x0, Z(0), rand, fuss, 'ds-beton'),
    linie([[x0, Z(a.h)], [x1, Z(a.h)]], 'ds-kante'),
    linie([[rand, Z(0)], [x1, Z(0)]], 'ds-kante'),
    linie([[rand, Z(0)], [rand, fuss]], 'ds-kante'),
    bruch([x1, Z(a.h)], [x1, Z(0)]),
    bruch([x0, fuss], [rand, fuss]),
    b.mitAchse
      ? linie([[x0, Z(a.h) - aussen * 10], [x0, fuss + aussen * 10]], 'ds-achslinie')
      : bruch([x0, Z(a.h)], [x0, fuss]),
  ];
  if (rand - x0 > 52) {
    teile.push(text((x0 + rand) / 2, Z(0) + aussen * STUMPF * 0.55 + 4, ['Stütze'],
      { anker: 'middle', klasse: 'gb-zart' }));
  }
  if (a.pilz) teile.push(rechteck(x0, Z(0), X(0), Z(a.pilz.hoehe), 'ds-pilz'));
  return teile;
}

/** Die beiden Lagen der Zugbewehrung: längs eine Linie, quer Punkte im Abstand ihrer Stäbe. */
function biegebewehrung(a, b) {
  const { X, Z, m } = b;
  const teile = [];
  for (const l of a.lagen) {
    const y = Z(a.h - l.tiefe);
    const r = Math.max((l.durchmesser * m) / 2, 1.3);
    if (l.laengs) {
      teile.push(svgEl('path', {
        d: `M${p(X(b.links), y)} H${X(b.rechts).toFixed(1)}`, class: 'ds-biegestab',
        'stroke-width': (2 * r).toFixed(1),
      }));
      continue;
    }
    // Im Takt der Stäbe, ab der halben Teilung vom Rand der Stütze.
    const start = a.stuetze.rand + l.abstand / 2
      - Math.ceil((a.stuetze.rand - b.links) / l.abstand) * l.abstand;
    for (let x = start; x < b.rechts; x += l.abstand) {
      if (x <= b.links) continue;
      teile.push(svgEl('circle', { cx: X(x).toFixed(1), cy: y.toFixed(1), r: r.toFixed(1), class: 'ds-biegepunkt' }));
    }
  }
  return teile;
}

/** Ein Anker: der Schaft und zwei Köpfe, dreimal so breit wie er. */
function kopfanker(x, fuss, kopf, dicke) {
  const s = Math.sign(fuss - kopf);
  const [breite, stark] = [3 * dicke, Math.max(0.6 * dicke, 2)];
  return [
    svgEl('path', { d: `M${p(x, fuss)} L${p(x, kopf)}`, class: 'ds-element', 'stroke-width': dicke.toFixed(1) }),
    rechteck(x - breite / 2, fuss, x + breite / 2, fuss - s * stark, 'ds-kopf'),
    rechteck(x - breite / 2, kopf, x + breite / 2, kopf + s * stark, 'ds-kopf'),
  ];
}

/** Ein Bügelschenkel: an beiden Enden ein Halbkreis nach aussen, um die Bewehrung. */
function buegelschenkel(x, fuss, kopf, dicke) {
  const s = Math.sign(fuss - kopf);
  const r = Math.max(1.4 * dicke, 3.5);
  const dreh = s > 0 ? 0 : 1;
  return svgEl('path', {
    d: `M${p(x + 2 * r, kopf + s * r)} A${r.toFixed(1)} ${r.toFixed(1)} 0 0 ${dreh} ${p(x, kopf + s * r)} `
      + `L${p(x, fuss - s * r)} A${r.toFixed(1)} ${r.toFixed(1)} 0 0 ${dreh} ${p(x + 2 * r, fuss - s * r)}`,
    class: 'ds-buegel', 'stroke-width': dicke.toFixed(1),
  });
}

function elemente(a, b) {
  const { X, Z, m } = b;
  const dicke = Math.max(a.durchmesser * m, 1.6);
  const [fuss, kopf] = [Z(a.c_v), Z(a.c_v + a.h_A)];
  return a.radien.flatMap((r) => (a.form === 'buegel'
    ? [buegelschenkel(X(r), fuss, kopf, dicke)]
    : kopfanker(X(r), fuss, kopf, dicke)));
}

/** Auf der Zugseite: 0.35·d_v und d_v ab dem Rand der gestützten Fläche, je bis zum Bereich. */
function bereichsmasse(a, b) {
  const { X, Z, aussen } = b;
  const zug = Z(a.h);
  const reihe = (k) => zug - aussen * BEREICH[k];
  const [von, bis] = a.zaehlt;
  return gruppe('', [
    linie([[X(0), zug], [X(0), reihe(1) - aussen * 4]], 'gb-masshilfe'),
    linie([[X(von), zug], [X(von), reihe(0) - aussen * 4]], 'gb-masshilfe'),
    linie([[X(bis), zug], [X(bis), reihe(1) - aussen * 4]], 'gb-masshilfe'),
    mass([X(0), reihe(0)], [X(von), reihe(0)], ['0.35·d', { unten: 'v' }, ` = ${ganz(von)}`]),
    mass([X(0), reihe(1)], [X(bis), reihe(1)], ['d', { unten: 'v' }, ` = ${ganz(bis)}`]),
  ]);
}

/** Auf der Druckseite: die Abstände der Elemente, vom Rand der gestützten Fläche an. */
function abstandsmasse(a, b) {
  const { X, Z, aussen } = b;
  const y = Z(0) + aussen * ABSTAENDE;
  const stellen = [0, ...a.radien];
  return gruppe('', [
    ...stellen.map((x) => linie([[X(x), Z(0)], [X(x), y + aussen * 4]], 'gb-masshilfe')),
    ...stellen.slice(1).map((x, i) => mass([X(stellen[i]), y], [X(x), y], [ganz(x - stellen[i])])),
  ]);
}

/** Rechts: c_v, h_A und c, daneben h -- mit Hilfslinien vom letzten Element und von der Platte. */
function hoehenmasse(a, b) {
  const { X, Z } = b;
  const [ende, xa] = [X(b.rechts), X(b.rechts) + 18];
  const xh = xa + 84;
  const oben = a.c_v + a.h_A;
  const hilfe = (z, von, bis) => linie([[von, Z(z)], [bis, Z(z)]], 'gb-masshilfe');
  return gruppe('', [
    hilfe(a.c_v, X(b.letzter), xa + 4), hilfe(oben, X(b.letzter), xa + 4),
    hilfe(a.h - a.c, ende, xa + 4), hilfe(0, ende, xh + 4), hilfe(a.h, ende, xh + 4),
    mass([xa, Z(0)], [xa, Z(a.c_v)], ['c', { unten: 'v' }, ` = ${ganz(a.c_v)}`]),
    mass([xa, Z(a.c_v)], [xa, Z(oben)], ['h', { unten: 'A' }, ` = ${ganz(a.h_A)}`]),
    mass([xa, Z(a.h - a.c)], [xa, Z(a.h)], [`c = ${ganz(a.c)}`]),
    mass([xh, Z(0)], [xh, Z(a.h)], [`h = ${ganz(a.h)}`]),
  ]);
}

/**
 * Die Karte «Durchstanzbewehrung» im Reiter «Diagramme»: eine Leiste in der
 * Ansicht, darunter die Legende des Kerns -- oder nichts, wo es keine
 * Durchstanzbewehrung braucht.
 */
export function ansichtKarte(a) {
  if (!a) return null;
  const b = abbildung(a);
  const svg = svgEl('svg', {
    viewBox: `0 0 ${BREITE} ${b.hoehe.toFixed(0)}`, class: 'gb-bild', role: 'img',
    'aria-label': 'Durchstanzbewehrung in der Ansicht',
  });
  svg.append(
    ...beton(a, b),
    rechteck(b.X(a.zaehlt[0]), b.Z(0), b.X(a.zaehlt[1]), b.Z(a.h), 'ds-zone'),
    ...biegebewehrung(a, b),
    ...elemente(a, b),
    bereichsmasse(a, b),
    abstandsmasse(a, b),
    hoehenmasse(a, b),
  );
  return karte('Durchstanzbewehrung', [el('div.gb-bildhuelle', {}, [svg]), legende(a.legende)],
    { bild: svg, klasse: 'ist-breit' });
}
