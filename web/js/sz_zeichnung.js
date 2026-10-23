/**
 * sz_zeichnung.js -- die Situation einer Setzung als Bild.
 *
 * Ein Schnitt quer durch das Fundament, durch den Punkt, unter dem gerechnet
 * wird: die Sohle B breit, darunter die Schichten mit Namen, Dicke und
 * M_E-Werten, rechts in jeder ihr Beitrag zur Setzung, unten der Baugrund,
 * der als unzusammendrückbar gilt. Vom Punkt -- K beim starren, die Mitte
 * beim schlaffen Fundament -- geht die Linie des Einflussfaktors J nach
 * unten, wie die Kurve E in Bild 8.1: welcher Teil der Pressung in welcher
 * Tiefe noch ankommt. Oben rechts der Grundriss L × B mit dem Punkt und dem
 * Schnitt (Bild 8.15). Das starre Fundament steht als Block da, die
 * schlaffe Last als Pressung allein.
 *
 * Masse und Schichten kommen aus dem Eintrag, wie sie eingegeben sind; was
 * der Kern daraus macht -- die Lage des Punktes, J über die Tiefe, die
 * Setzung je Schicht --, aus der Lösung (opencivil/web/setzungsdaten.py).
 * Längen und Tiefen im selben Massstab -- ausser der Baugrund wäre so
 * flach, dass man nichts mehr sieht: dann sind die Tiefen überhöht, und die
 * Legende sagt, wie stark.
 */

import { karte } from './bausteine.js';
import { el, svgEl } from './dom.js';
import {
  BREITE, linie, mass, pfeil, schraffur, text, zahl,
} from './gb_skizze.js';
import { zustand } from './zustand.js';

const RAND = 16;
/** Links Platz für die Tiefen, oben für Pressung und Grundriss, unten für die Schraffur, in px. */
const LINKS = 58;
const OBEN = 100;
const UNTEN = 40;
/** So hoch wird der Baugrund höchstens gezeichnet, in px -- und mindestens. */
const HOEHE = 440;
const MINDESTHOEHE = 200;
/** So dick steht das starre Fundament da, in px -- seine Dicke ist keine Eingabe. */
const DICKE = 26;
/** Der Grundriss oben rechts, höchstens so gross, in px. */
const GRUNDRISS = [118, 58];

/** Wo die Schichten liegen, wie eingegeben: je Schicht Ober- und Unterkante ab der Sohle, in m. */
function lagen(schichten) {
  let oben = 0;
  return schichten.map((schicht) => {
    const lage = { schicht, z_o: oben, z_u: oben + Math.max(schicht.d, 0) };
    oben = lage.z_u;
    return lage;
  });
}

/** Der Grundriss L × B mit dem Punkt und dem Schnitt durch ihn, oben rechts. */
function grundriss(s, d) {
  const L = Math.max(s.L, 1e-3);
  const B = Math.max(s.B, 1e-3);
  const k = Math.min(GRUNDRISS[0] / L, GRUNDRISS[1] / B);
  const [breite, hoehe] = [L * k, B * k];
  const x0 = BREITE - RAND - breite - 4;
  const y0 = RAND + 18;
  const teile = [
    text(x0, y0 - 6, ['Grundriss'], { klasse: 'gb-zart' }),
    svgEl('rect', {
      x: x0.toFixed(1), y: y0.toFixed(1), width: breite.toFixed(1), height: hoehe.toFixed(1),
      class: s.steifigkeit === 'starr' ? 'gb-fundament' : 'sz-lastflaeche',
    }),
    text(x0 + breite, y0 + hoehe + 14, [`L × B = ${zahl(s.L, 2)} × ${zahl(s.B, 2)} m`],
      { anker: 'end', klasse: 'gb-masstext' }),
  ];
  if (d?.lage) {
    // Längs L nach rechts, längs B von unten nach oben, ab der Ecke unten links.
    const [x, y] = [x0 + d.lage[0] * k, y0 + hoehe - d.lage[1] * k];
    teile.push(
      linie([[x, y0 - 3], [x, y0 + hoehe + 3]], 'gb-hilfslinie'),
      svgEl('circle', { cx: x.toFixed(1), cy: y.toFixed(1), r: 3, class: 'sz-punkt' }),
      text(x + 5, y - 4, [d.punkt === 'Mitte' ? 'M' : 'K'], { klasse: 'sz-punkttext' }),
    );
  }
  return teile;
}

/**
 * Der Schnitt: Schichten, Fundament oder Lastfläche, Pressung, Punkt, die
 * Linie von J -- und der Grundriss. `d` ist, was der Kern dazu sagt, oder
 * nichts, solange nicht gerechnet ist.
 */
function massstab(s) {
  const schichten = lagen(s.schichten);
  const tiefe = schichten.length ? schichten[schichten.length - 1].z_u : 0;
  const B = Math.max(s.B, 1e-3);
  const spanne = BREITE - LINKS - RAND;
  const k = tiefe > 0 ? Math.min(spanne / (2.2 * B), HOEHE / tiefe) : spanne / (2.2 * B);
  const kTiefe = tiefe > 0 ? Math.max(k, MINDESTHOEHE / tiefe) : k;
  return { schichten, tiefe, B, spanne, k, kTiefe, ueberhoehung: kTiefe / k };
}

function situationsbild(s, d) {
  const { schichten, tiefe, B, spanne, k, kTiefe } = massstab(s);
  const sichtbar = spanne / k;
  const links = (sichtbar - B) / 2;
  const y0 = RAND + OBEN;
  const px = ([x, z]) => [LINKS + x * k, y0 + z * kTiefe];
  const hoehe = Math.round(y0 + tiefe * kTiefe + (schichten.length ? UNTEN : 12) + RAND);
  const svg = svgEl('svg', {
    viewBox: `0 0 ${BREITE} ${hoehe}`, class: 'gb-bild', role: 'img',
    'aria-label': `Situation der Setzung ${s.name}`,
  });
  const zeichne = (...teile) => svg.append(...teile.filter(Boolean));
  const setzungen = d?.schichten || [];

  // -- Schichten: Bänder, Grenzen, Tiefen links, Beschriftung und Setzung --
  const rechts = BREITE - RAND;
  let letzteTiefe = -Infinity;
  schichten.forEach(({ schicht, z_o, z_u }, i) => {
    const [a, e] = [px([0, z_o]), px([sichtbar, z_u])];
    const dicke = e[1] - a[1];
    zeichne(svgEl('rect', {
      x: a[0].toFixed(1), y: a[1].toFixed(1), width: (e[0] - a[0]).toFixed(1),
      height: dicke.toFixed(1), class: `sz-schicht sz-schicht-${i % 2}`,
    }));
    if (dicke >= 36) {
      zeichne(
        text(a[0] + 6, a[1] + 17, [schicht.name], { klasse: 'sz-name' }),
        text(a[0] + 6, a[1] + 32, [`d = ${zahl(schicht.d, 2)} m · M`, { unten: 'E' },
          ` = ${zahl(schicht.M_E, 1)} · M'`, { unten: 'E' }, ` = ${zahl(schicht.M_E_strich, 1)} MN/m²`],
        { klasse: 'gb-zart' }),
      );
    } else if (dicke >= 16) {
      zeichne(text(a[0] + 6, a[1] + dicke / 2 + 4, [schicht.name], { klasse: 'sz-name' }));
    }
    const beitrag = setzungen[i];
    if (beitrag && dicke >= 16) {
      zeichne(text(rechts - 6, a[1] + Math.min(17, dicke / 2 + 4), [`s = ${zahl(beitrag.s, 1)} mm`],
        { anker: 'end', klasse: 'sz-setzung' }));
    }
    // Die Tiefe an jeder Grenze, wo sie nicht in die vorige liefe.
    for (const z of i === 0 ? [z_o, z_u] : [z_u]) {
      const y = px([0, z])[1];
      if (y - letzteTiefe >= 13) {
        zeichne(
          linie([[LINKS - 5, y], [LINKS, y]], 'sz-strich'),
          text(LINKS - 8, y + 4, [`${zahl(z, 2)} m`], { anker: 'end', klasse: 'gb-masstext' }),
        );
        letzteTiefe = y;
      }
    }
  });
  if (schichten.length) {
    const fuss = [px([0, tiefe]), px([sichtbar, tiefe])];
    zeichne(
      schraffur([fuss.map(([x, y]) => [x, y + 1])]),
      linie(fuss, 'gb-gelaende'),
      text(rechts - 6, fuss[0][1] + 24, ['unzusammendrückbar'], { anker: 'end', klasse: 'gb-zart' }),
    );
  }
  zeichne(linie([px([0, 0]), px([sichtbar, 0])], 'gb-gelaende'));

  // -- Fundament oder Lastfläche, darüber die Pressung und das Mass B ------
  const [l, r] = [px([links, 0]), px([links + B, 0])];
  const starr = s.steifigkeit === 'starr';
  const oberkante = starr ? l[1] - DICKE : l[1];
  if (starr) {
    zeichne(svgEl('rect', {
      x: l[0].toFixed(1), y: oberkante.toFixed(1), width: (r[0] - l[0]).toFixed(1),
      height: DICKE, class: 'gb-fundament',
    }));
  } else {
    zeichne(linie([[l[0], l[1] - 1.5], [r[0], r[1] - 1.5]], 'sz-lastlinie'));
  }
  // Pfeile nur, wo eine Pressung ist -- eine neue Berechnung hat keine.
  const n = s.q_W + s.q_E > 0 ? Math.max(3, Math.min(14, Math.round((r[0] - l[0]) / 22))) : 0;
  for (let i = 0; i < n; i += 1) {
    const x = l[0] + (r[0] - l[0]) * (i + 0.5) / n;
    zeichne(pfeil([x, oberkante - 22], [x, oberkante - 1], 'gb-auflast'));
  }
  // Die Pressung links neben den Pfeilen, das Mass B über ihnen.
  zeichne(
    text(l[0] - 8, oberkante - 8,
      ['q', { unten: 'W' }, ' + q', { unten: 'E' }, ` = ${zahl(s.q_W, 1)} + ${zahl(s.q_E, 1)} kN/m²`],
      { anker: 'end', klasse: 'gb-lasttext' }),
    linie([[l[0], oberkante - 4], [l[0], oberkante - 40]], 'gb-masshilfe'),
    linie([[r[0], oberkante - 4], [r[0], oberkante - 40]], 'gb-masshilfe'),
    mass([l[0], oberkante - 34], [r[0], oberkante - 34], ['B = ', zahl(s.B, 2), ' m']),
  );

  // -- Der Punkt und die Linie von J ----------------------------------------
  if (d?.lage && d.linie?.length) {
    const p = px([links + d.lage[1], 0]);
    const unten = px([links + d.lage[1], tiefe]);
    // J = 1 reicht bis vor die Setzungen am rechten Rand -- mit Platz für «J = 1».
    const breite = Math.max(40, rechts - 150 - p[0]);
    const kurve = d.linie.map(([z, J]) => [p[0] + J * breite, y0 + z * kTiefe]);
    zeichne(
      svgEl('path', {
        d: `M${p[0].toFixed(1)} ${p[1].toFixed(1)} ${kurve.map(([x, y]) => `L${x.toFixed(1)} ${y.toFixed(1)}`).join(' ')} L${unten[0].toFixed(1)} ${unten[1].toFixed(1)} Z`,
        class: 'sz-flaeche',
      }),
      linie([p, unten], 'gb-hilfslinie'),
      linie(kurve, 'sz-linie'),
      svgEl('circle', { cx: p[0].toFixed(1), cy: p[1].toFixed(1), r: 3.5, class: 'sz-punkt' }),
      text(p[0] - 6, p[1] + 15, [d.punkt === 'Mitte' ? 'M' : 'K'], { anker: 'end', klasse: 'sz-punkttext' }),
      text(kurve[0][0] + 5, kurve[0][1] + 14, ['J = 1'], { klasse: 'sz-linientext' }),
    );
    const ende = kurve[kurve.length - 1];
    zeichne(text(ende[0] + 5, ende[1] - 5, [`J = ${zahl(d.J_fuss, 3)}`], { klasse: 'sz-linientext' }));
  }

  zeichne(...grundriss(s, d));
  return svg;
}

/** Die Zeilen unter dem Bild: der Punkt, die Setzung gegen die zulässige, was J zeigt. */
function legende(s, d) {
  const zeilen = [];
  if (!d) {
    zeilen.push('Noch nicht gerechnet.');
  } else if (!d.lage) {
    zeilen.push('Ohne Schicht keine Setzung.');
  } else {
    zeilen.push(d.punkt === 'Mitte'
      ? 'Schlaff: gerechnet unter der Mitte – dort ist die Setzung am grössten (Kap. 8.10).'
      : `Starr: gerechnet im Punkt K, ${zahl(d.lage[0], 2)} m längs L und ${zahl(d.lage[1], 2)} m `
        + 'längs B von einer Ecke – seine Setzung ist die mittlere des Fundaments (Bild 8.15).');
    zeilen.push(`s = s_W + s_E = ${zahl(d.s_W, 1)} + ${zahl(d.s_E, 1)} = ${zahl(d.s, 1)} mm `
      + `${d.erfuellt ? '≤' : '>'} s_zul = ${zahl(d.s_zul, 1)} mm – `
      + `${d.erfuellt ? 'erfüllt' : 'nicht erfüllt'}, α = ${d.grad}`);
    zeilen.push("Die Linie zeigt J über die Tiefe: Δσ'_z = J · q. Am Fuss der untersten Schicht "
      + `noch J = ${zahl(d.J_fuss, 3)}; darunter gilt der Baugrund als unzusammendrückbar.`);
  }
  const { ueberhoehung } = massstab(s);
  if (ueberhoehung > 1.05) zeilen.push(`Tiefen ${zahl(ueberhoehung, 1)}-fach überhöht.`);
  zeilen.push(`Länge des Fundaments L = ${zahl(s.L, 2)} m, senkrecht zum Schnitt.`);
  return el('div.gb-legende', {}, zeilen.map((z) => el('p', { text: z })));
}

/** Die Karte einer Setzung im Reiter «Diagramme». Das Panel darum baut bericht.js. */
export function setzungKarten(kennung) {
  const s = (zustand.projekt?.setzungen || []).find((x) => x.kennung === kennung);
  if (!s) return [];
  const d = zustand.loesung?.setzungen?.[kennung];
  return [karte('Situation', [
    el('div.gb-bildhuelle', {}, [situationsbild(s, d)]),
    legende(s, d),
  ], { klasse: 'ist-breit' })];
}
