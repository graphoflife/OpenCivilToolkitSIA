/**
 * spannungsbild.js -- was im Querschnitt geschieht, gezeichnet.
 *
 * Drei Bilder zu den drei Fragen aus `opencivil/spannungsanalyse.py`:
 *
 *   Dehnung und Spannung über die Höhe   -- für «aus N und M» und «aus Dehnungen»
 *   Momenten-Krümmungs-Linie             -- für die dritte
 *
 * Die Höhe läuft nach unten, wie man einen Schnitt zeichnet: z = 0 ist die
 * Oberkante. Das ist dieselbe Achse, die der Löser und der Lagenaufbau
 * benutzen -- ein Bild, das sie umdrehte, passte nicht zum Nachweis daneben.
 *
 * Gerechnet wird hier nichts. Alle Zahlen kommen fertig aus dem Kern; diese
 * Datei setzt Striche.
 */

import { el, svgEl } from './dom.js';

const BREITE = 300;
const HOEHE = 250;
const RAND = { oben: 24, unten: 34, links: 44, rechts: 14 };

const ZUG = '#b3261e';
const DRUCK = '#1d4ed8';
const STAHL = '#b45309';
const ACHSE = '#8895a8';
const SCHRIFT = '#1a1f27';

/** Ein Rahmen mit Nulllinie und beschrifteten Achsen -- beide Bilder teilen ihn. */
function tafel({ titel, einheit, werte, hoeheMm }) {
  const svg = svgEl('svg', {
    viewBox: `0 0 ${BREITE} ${HOEHE}`, class: 'sd-bild',
    preserveAspectRatio: 'xMidYMid meet',
  });
  const breite = BREITE - RAND.links - RAND.rechts;
  const hoehe = HOEHE - RAND.oben - RAND.unten;

  // Der Wertebereich wird um null herum aufgespannt: eine Spannungsverteilung
  // ohne sichtbare Nulllinie sagt nicht, wo Druck aufhört und Zug anfängt.
  const grenze = Math.max(1e-9, ...werte.map(Math.abs));
  const x = (w) => RAND.links + breite * (0.5 + 0.5 * w / (grenze * 1.15));
  const y = (z) => RAND.oben + hoehe * (z / hoeheMm);

  svg.append(svgEl('rect', {
    x: RAND.links, y: RAND.oben, width: breite, height: hoehe,
    fill: 'none', stroke: ACHSE, 'stroke-width': 1,
  }));
  svg.append(svgEl('line', {
    x1: x(0), y1: RAND.oben, x2: x(0), y2: RAND.oben + hoehe,
    stroke: ACHSE, 'stroke-width': 1, 'stroke-dasharray': '3 3',
  }));

  const kopf = svgEl('text', {
    x: RAND.links, y: 14, 'font-size': 11, 'font-weight': 600, fill: SCHRIFT,
  });
  kopf.textContent = titel;
  svg.append(kopf);

  for (const [wert, anker] of [[-grenze, 'start'], [grenze, 'end']]) {
    const marke = svgEl('text', {
      x: x(wert), y: HOEHE - 20, 'text-anchor': anker,
      'font-size': 9.5, fill: ACHSE,
    });
    marke.textContent = `${wert.toFixed(wert && Math.abs(wert) < 10 ? 2 : 0)}`;
    svg.append(marke);
  }
  const eh = svgEl('text', {
    x: x(0), y: HOEHE - 6, 'text-anchor': 'middle', 'font-size': 9.5, fill: ACHSE,
  });
  eh.textContent = einheit;
  svg.append(eh);

  for (const z of [0, hoeheMm]) {
    const marke = svgEl('text', {
      x: RAND.links - 5, y: y(z) + (z ? 3 : 8), 'text-anchor': 'end',
      'font-size': 9.5, fill: ACHSE,
    });
    marke.textContent = `${z.toFixed(0)}`;
    svg.append(marke);
  }
  return { svg, x, y };
}

/** Die gefüllte Fläche zwischen Nulllinie und Verlauf -- Druck und Zug getrennt. */
function verlauf(svg, x, y, punkte, hol) {
  for (const [vorzeichen, farbe] of [[-1, DRUCK], [1, ZUG]]) {
    const teil = punkte.map((p) => (Math.sign(hol(p)) === vorzeichen ? hol(p) : 0));
    if (!teil.some((w) => w !== 0)) continue;
    const ecken = punkte.map((p, i) => `${x(teil[i]).toFixed(1)},${y(p.z).toFixed(1)}`);
    svg.append(svgEl('polygon', {
      points: [`${x(0)},${y(punkte[0].z)}`, ...ecken,
        `${x(0)},${y(punkte[punkte.length - 1].z)}`].join(' '),
      fill: farbe, 'fill-opacity': .16, stroke: farbe, 'stroke-width': 1.4,
    }));
  }
}

/** Dehnung oder Spannung über die Höhe, mit den Bewehrungslagen darin. */
function ueberDieHoehe(bild, { titel, einheit, hol, stahlHol }) {
  const werte = [...bild.beton.map(hol), ...bild.stahl.map(stahlHol)];
  const { svg, x, y } = tafel({ titel, einheit, werte, hoeheMm: bild.h });
  verlauf(svg, x, y, bild.beton, hol);

  if (bild.nulllinie !== null && bild.nulllinie !== undefined) {
    svg.append(svgEl('line', {
      x1: RAND.links, y1: y(bild.nulllinie), x2: BREITE - RAND.rechts,
      y2: y(bild.nulllinie), stroke: '#16794a', 'stroke-width': 1.2,
      'stroke-dasharray': '5 3',
    }));
    const marke = svgEl('text', {
      x: BREITE - RAND.rechts - 2, y: y(bild.nulllinie) - 3,
      'text-anchor': 'end', 'font-size': 9.5, fill: '#16794a',
    });
    marke.textContent = `x = ${bild.nulllinie.toFixed(0)} mm`;
    svg.append(marke);
  }

  for (const lage of bild.stahl) {
    const wert = stahlHol(lage);
    svg.append(svgEl('line', {
      x1: x(0), y1: y(lage.z), x2: x(wert), y2: y(lage.z),
      stroke: STAHL, 'stroke-width': 2,
    }));
    const punkt = svgEl('circle', {
      cx: x(wert), cy: y(lage.z), r: 3, fill: STAHL,
    });
    const titelKnoten = svgEl('title');
    titelKnoten.textContent =
      `${lage.nummer}. Lage – ${lage.a_s.toFixed(0)} mm²\n`
      + `ε = ${lage.eps.toFixed(3)} ‰, σ = ${lage.sigma.toFixed(0)} N/mm²\n`
      + `F = ${lage.kraft.toFixed(1)} kN`;
    punkt.append(titelKnoten);
    svg.append(punkt);
  }
  return svg;
}

/** Die Momenten-Krümmungs-Linie: beide Zustände und was dazwischen gilt. */
function momentenlinie(kurve) {
  const svg = svgEl('svg', {
    viewBox: `0 0 ${BREITE * 2} ${HOEHE}`, class: 'sd-bild sd-breit',
    preserveAspectRatio: 'xMidYMid meet',
  });
  const breite = BREITE * 2 - RAND.links - RAND.rechts;
  const hoehe = HOEHE - RAND.oben - RAND.unten;
  const chiMax = Math.max(1e-9, ...kurve.punkte.map((p) => p.chi));
  const mMax = Math.max(1e-9, kurve.M_Rd);
  const x = (chi) => RAND.links + breite * (chi / (chiMax * 1.05));
  const y = (m) => RAND.oben + hoehe * (1 - m / (mMax * 1.05));

  svg.append(svgEl('rect', {
    x: RAND.links, y: RAND.oben, width: breite, height: hoehe,
    fill: 'none', stroke: ACHSE, 'stroke-width': 1,
  }));

  const linie = (hol, farbe, breiteStrich, muster) => {
    const punkte = kurve.punkte.filter((p) => hol(p) !== null && hol(p) !== undefined);
    if (punkte.length < 2) return;
    svg.append(svgEl('polyline', {
      points: punkte.map((p) => `${x(hol(p)).toFixed(2)},${y(p.M).toFixed(2)}`).join(' '),
      fill: 'none', stroke: farbe, 'stroke-width': breiteStrich,
      'stroke-dasharray': muster || null,
    }));
  };
  linie((p) => p.chi_I, ACHSE, 1.2, '4 3');
  linie((p) => p.chi_II, ACHSE, 1.2, '2 3');
  linie((p) => p.chi, '#16794a', 2.2);

  if (kurve.M_Riss > 0 && kurve.M_Riss < mMax) {
    svg.append(svgEl('line', {
      x1: RAND.links, y1: y(kurve.M_Riss), x2: BREITE * 2 - RAND.rechts,
      y2: y(kurve.M_Riss), stroke: ZUG, 'stroke-width': 1.2, 'stroke-dasharray': '5 3',
    }));
    const marke = svgEl('text', {
      x: RAND.links + 4, y: y(kurve.M_Riss) - 4, 'font-size': 10, fill: ZUG,
    });
    marke.textContent = `M_Riss = ${kurve.M_Riss.toFixed(1)} kNm`;
    svg.append(marke);
  }

  for (const [text, px, py, anker] of [
    ['χ [1/m]', RAND.links + breite / 2, HOEHE - 8, 'middle'],
    ['M [kNm]', 12, RAND.oben + hoehe / 2, 'middle'],
  ]) {
    const t = svgEl('text', {
      x: px, y: py, 'text-anchor': anker, 'font-size': 11,
      'font-weight': 600, fill: SCHRIFT,
      transform: anker === 'middle' && px === 12
        ? `rotate(-90 12 ${RAND.oben + hoehe / 2})` : null,
    });
    t.textContent = text;
    svg.append(t);
  }
  for (const [wert, px, py, anker] of [
    [chiMax.toFixed(4), RAND.links + breite, HOEHE - 22, 'end'],
    [mMax.toFixed(0), RAND.links - 5, RAND.oben + 8, 'end'],
  ]) {
    const t = svgEl('text', {
      x: px, y: py, 'text-anchor': anker, 'font-size': 9.5, fill: ACHSE,
    });
    t.textContent = wert;
    svg.append(t);
  }
  return svg;
}

function zahlenzeile(eintraege) {
  return el('div.sd-zahlen', {}, eintraege.map(([name, wert]) =>
    el('span', {}, [el('b', { text: `${name} ` }), wert])));
}

/** Ein Fall: Überschrift, Zahlen, Bilder. */
export function spannungsfallZeichnen(fall) {
  if (!fall.moeglich) {
    return el('div.sd-fall', {}, [
      el('div.sd-kopf', { text: `${fall.name} – ${fall.titel}` }),
      el('p.hinweis', { text: fall.hinweis }),
    ]);
  }

  const kopf = el('div.sd-kopf', {
    text: `${fall.name} – ${fall.titel} (${fall.richtung})`,
  });

  if (fall.kurve) {
    const k = fall.kurve;
    return el('div.sd-fall', {}, [
      kopf,
      zahlenzeile([
        ['N =', `${k.N.toFixed(1)} kN`],
        ['M_Riss =', `${k.M_Riss.toFixed(1)} kNm`],
        ['M_Rd =', `${k.M_Rd.toFixed(1)} kNm`],
      ]),
      k.punkte.length ? momentenlinie(k) : null,
      el('p.sd-legende', {
        text: 'Durchgezogen: mit Zugversteifung. Lang gestrichelt: ungerissen '
          + '(Zustand I). Kurz gestrichelt: gerissen ohne Betonzugfestigkeit '
          + '(Zustand II).',
      }),
      k.hinweis ? el('p.hinweis', { text: k.hinweis }) : null,
    ]);
  }

  const b = fall.bild;
  if (!b.konvergiert) {
    return el('div.sd-fall', {}, [kopf, el('p.hinweis', { text: b.hinweis })]);
  }
  return el('div.sd-fall', {}, [
    kopf,
    zahlenzeile([
      ['N =', `${b.N.toFixed(1)} kN`],
      ['M =', `${b.M.toFixed(1)} kNm`],
      ['ε_m =', `${b.eps_m.toFixed(3)} ‰`],
      ['χ =', `${b.chi.toFixed(5)} 1/m`],
      ['x =', b.nulllinie === null ? '–' : `${b.nulllinie.toFixed(0)} mm`],
    ]),
    el('div.sd-paar', {}, [
      ueberDieHoehe(b, {
        titel: 'Dehnung ε [‰]', einheit: '‰',
        hol: (p) => p.eps, stahlHol: (s) => s.eps,
      }),
      ueberDieHoehe(b, {
        titel: 'Spannung σ [N/mm²]', einheit: 'N/mm²',
        hol: (p) => p.sigma, stahlHol: (s) => s.sigma,
      }),
    ]),
    b.hinweis ? el('p.hinweis', { text: b.hinweis }) : null,
  ]);
}
