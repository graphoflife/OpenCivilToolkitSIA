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

import { achsenkreuz } from './achsen.js';
import { beschriftungenEntzerren } from './diagramm.js';
import { el, svgEl } from './dom.js';

const BREITE = 300;
const HOEHE = 250;
const RAND = { oben: 24, unten: 34, links: 44, rechts: 14 };

const ZUG = '#b3261e';
const DRUCK = '#1d4ed8';
const STAHL = '#b45309';
const ACHSE = '#8895a8';
const SCHRIFT = '#1a1f27';

/**
 * So weit reicht der Wertebereich über den grössten Wert hinaus: Platz für
 * seine Zahl daneben, auch bei «-435.0».
 */
const SPIELRAUM = 1.4;

/** Weiss hinterlegt, damit eine Zahl auch über einem Strich lesbar bleibt. */
const HOF = { 'paint-order': 'stroke', stroke: '#fff', 'stroke-width': 3 };

/**
 * Ein Rahmen mit Nulllinie und den Grenzwerten an den Achsen -- beide Bilder
 * teilen ihn. Ohne Gitter: gezeigt wird ein Verlauf, abgelesen werden die
 * Zahlen darüber.
 */
function tafel({ titel, einheit, werte, hoeheMm }) {
  // Der Wertebereich wird um null herum aufgespannt: eine Spannungsverteilung
  // ohne sichtbare Nulllinie sagt nicht, wo Druck aufhört und Zug anfängt.
  // Die Höhe läuft nach unten, darum der Bereich von hoeheMm nach 0.
  const grenze = Math.max(1e-9, ...werte.map(Math.abs));
  const { svg, daten, x, y } = achsenkreuz({
    breite: BREITE, hoehe: HOEHE, rand: RAND, rahmen: true,
    attribute: { class: 'sd-bild', preserveAspectRatio: 'xMidYMid meet' },
    x: { bereich: [-grenze * SPIELRAUM, grenze * SPIELRAUM] },
    y: { bereich: [hoeheMm, 0] },
  });
  const hoehe = HOEHE - RAND.oben - RAND.unten;

  daten.append(svgEl('line', {
    x1: x(0), y1: RAND.oben, x2: x(0), y2: RAND.oben + hoehe,
    stroke: ACHSE, 'stroke-width': 1, 'stroke-dasharray': '3 3',
  }));

  const kopf = svgEl('text', {
    x: RAND.links, y: 14, 'font-size': 11, 'font-weight': 600, fill: SCHRIFT,
  });
  kopf.textContent = titel;
  daten.append(kopf);

  for (const [wert, anker] of [[-grenze, 'start'], [grenze, 'end']]) {
    const marke = svgEl('text', {
      x: x(wert), y: HOEHE - 20, 'text-anchor': anker,
      'font-size': 9.5, fill: ACHSE,
    });
    marke.textContent = `${wert.toFixed(wert && Math.abs(wert) < 10 ? 2 : 0)}`;
    daten.append(marke);
  }
  const eh = svgEl('text', {
    x: x(0), y: HOEHE - 6, 'text-anchor': 'middle', 'font-size': 9.5, fill: ACHSE,
  });
  eh.textContent = einheit;
  daten.append(eh);

  for (const z of [0, hoeheMm]) {
    const marke = svgEl('text', {
      x: RAND.links - 5, y: y(z) + (z ? 3 : 8), 'text-anchor': 'end',
      'font-size': 9.5, fill: ACHSE,
    });
    marke.textContent = `${z.toFixed(0)}`;
    daten.append(marke);
  }
  return { svg, daten, x, y };
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

/** Eine Zahl ohne «-0.0». */
function zahl(wert, stellen) {
  return (Math.abs(wert) < 0.5 * 10 ** -stellen ? 0 : wert).toFixed(stellen);
}

/**
 * Die Zahlen, nach denen man fragt: der Beton zuoberst und zuunterst, jede
 * Stahllage. Neben den Punkt, auf die Seite seines Vorzeichens. Stehen zwei zu
 * nah -- zwei Lagen wenige Millimeter übereinander --, rückt eine weg, und ein
 * Strich zeigt, wohin sie gehört.
 *
 * Ein Zettel: `wert`, `punkt` (die Höhe des Punkts im Bild), `soll` (wo die
 * Grundlinie der Zahl stehen möchte) und `farbe`.
 */
function anschreiben(daten, x, zettel, stellen) {
  const oben = RAND.oben + 9;
  const unten = HOEHE - RAND.unten - 3;
  for (const seite of [-1, 1]) {
    const teil = zettel.filter((z) => (zahl(z.wert, stellen) < 0 ? -1 : 1) === seite);
    if (!teil.length) continue;
    for (const z of beschriftungenEntzerren(teil, 11, oben, unten)) {
      const px = x(z.wert) + seite * 5;
      if (Math.abs(z.y - z.soll) > 2) {
        daten.append(svgEl('line', {
          x1: x(z.wert), y1: z.punkt, x2: px - seite * 1, y2: z.y - 3.5,
          stroke: z.farbe, 'stroke-width': .8, 'stroke-opacity': .7,
        }));
      }
      const t = svgEl('text', {
        x: px, y: z.y, 'text-anchor': seite < 0 ? 'end' : 'start',
        'font-size': 9.5, 'font-weight': 600, fill: z.farbe, ...HOF,
      });
      t.textContent = zahl(z.wert, stellen);
      daten.append(t);
    }
  }
}

/** Dehnung oder Spannung über die Höhe, mit den Bewehrungslagen darin. */
function ueberDieHoehe(bild, { titel, einheit, hol, stahlHol, stellen }) {
  const werte = [...bild.beton.map(hol), ...bild.stahl.map(stahlHol)];
  const { svg, daten, x, y } = tafel({ titel, einheit, werte, hoeheMm: bild.h });
  verlauf(daten, x, y, bild.beton, hol);

  if (bild.nulllinie !== null && bild.nulllinie !== undefined) {
    daten.append(svgEl('line', {
      x1: RAND.links, y1: y(bild.nulllinie), x2: BREITE - RAND.rechts,
      y2: y(bild.nulllinie), stroke: '#16794a', 'stroke-width': 1.2,
      'stroke-dasharray': '5 3',
    }));
    const marke = svgEl('text', {
      x: BREITE - RAND.rechts - 2, y: y(bild.nulllinie) - 3,
      'text-anchor': 'end', 'font-size': 9.5, fill: '#16794a',
    });
    marke.textContent = `x = ${bild.nulllinie.toFixed(0)} mm`;
    daten.append(marke);
  }

  for (const lage of bild.stahl) {
    const wert = stahlHol(lage);
    daten.append(svgEl('line', {
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
    daten.append(punkt);
  }

  // Der Beton am Rand: zuoberst knapp unter, zuunterst knapp über der Kante.
  const betonfarbe = (w) => (w < 0 ? DRUCK : w > 0 ? ZUG : ACHSE);
  const kopfwert = hol(bild.beton[0]);
  const fusswert = hol(bild.beton[bild.beton.length - 1]);
  anschreiben(daten, x, [
    { wert: kopfwert, punkt: y(0), soll: y(0) + 9, farbe: betonfarbe(kopfwert) },
    { wert: fusswert, punkt: y(bild.h), soll: y(bild.h) - 3, farbe: betonfarbe(fusswert) },
    ...bild.stahl.map((lage) => ({
      wert: stahlHol(lage), punkt: y(lage.z), soll: y(lage.z) + 3.5, farbe: STAHL,
    })),
  ], stellen);
  return svg;
}

/** Ein Punkt der Linie mit seinem Namen daneben. */
function marke(daten, px, py, inhalt, { farbe, dx, dy, anker }) {
  daten.append(svgEl('circle', {
    cx: px, cy: py, r: 3.2, fill: '#fff', stroke: farbe, 'stroke-width': 1.6,
  }));
  const t = svgEl('text', {
    x: px + dx, y: py + dy, 'text-anchor': anker, 'font-size': 10.5,
    'font-weight': 600, fill: farbe, ...HOF,
  });
  t.textContent = inhalt;
  daten.append(t);
}

/**
 * Die Momenten-Krümmungs-Linie: ungerissen bis M_Riss, dort waagrecht nach
 * rechts -- der Querschnitt reisst, beim selben Moment krümmt er sich mehr --,
 * darüber gerissen bis M_Rd. Gestrichelt die beiden Zustände je für sich.
 */
function momentenlinie(kurve) {
  const chiMax = Math.max(1e-9, ...kurve.punkte.map((p) => p.chi));
  const mMax = Math.max(1e-9, kurve.M_Rd);
  const { svg, daten, x, y, feld } = achsenkreuz({
    breite: BREITE * 2, hoehe: HOEHE, rand: RAND, rahmen: true,
    attribute: { class: 'sd-bild sd-breit', preserveAspectRatio: 'xMidYMid meet' },
    x: { bereich: [0, chiMax * 1.05], titel: 'χ [1/m]' },
    y: { bereich: [0, mMax * 1.05], titel: 'M [kNm]' },
    schrift: { teilung: 9.5, titel: 11 }, titelLinks: 12,
  });

  const linie = (hol, farbe, breiteStrich, muster) => {
    const punkte = kurve.punkte.filter((p) => hol(p) !== null && hol(p) !== undefined);
    if (punkte.length < 2) return;
    daten.append(svgEl('polyline', {
      points: punkte.map((p) => `${x(hol(p)).toFixed(2)},${y(p.M).toFixed(2)}`).join(' '),
      fill: 'none', stroke: farbe, 'stroke-width': breiteStrich,
      'stroke-dasharray': muster || null,
    }));
  };
  linie((p) => p.chi_I, ACHSE, 1.2, '4 3');
  linie((p) => p.chi_II, ACHSE, 1.2, '2 3');
  linie((p) => p.chi, '#16794a', 2.2);

  // Der Riss: unter dem waagrechten Stück, wo die Linie nicht hinkommt.
  if (kurve.riss) {
    const { M, chi_vor: vor, chi_nach: nach } = kurve.riss;
    daten.append(svgEl('circle', {
      cx: x(vor), cy: y(M), r: 2.4, fill: ZUG,
    }));
    marke(daten, x(nach), y(M), `M_Riss = ${M.toFixed(1)} kNm`,
      { farbe: ZUG, dx: 7, dy: 14, anker: 'start' });
  }
  // Das Ende: M_Rd, darunter -- über der Linie bleibt bis zum Rahmen kein Platz.
  const ende = kurve.punkte[kurve.punkte.length - 1];
  marke(daten, x(ende.chi), y(ende.M), `M_Rd = ${ende.M.toFixed(1)} kNm`,
    { farbe: '#16794a', dx: -4, dy: 16, anker: 'end' });

  // Ohne Gitter: an den Achsen stehen nur die Grösstwerte.
  for (const [wert, px, py, anker] of [
    [chiMax.toFixed(4), feld.rechts, HOEHE - 22, 'end'],
    [mMax.toFixed(0), feld.links - 5, feld.oben + 8, 'end'],
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
        text: 'Durchgezogen: der Querschnitt – ungerissen bis M_Riss, dann der Sprung, '
          + 'darüber gerissen (ohne Zugversteifung) · lang gestrichelt: immer ungerissen (I) '
          + '· kurz gestrichelt: immer gerissen, ohne f_ct (II)',
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
        titel: 'Dehnung ε [‰]', einheit: '‰', stellen: 2,
        hol: (p) => p.eps, stahlHol: (s) => s.eps,
      }),
      ueberDieHoehe(b, {
        titel: 'Spannung σ [N/mm²]', einheit: 'N/mm²', stellen: 1,
        hol: (p) => p.sigma, stahlHol: (s) => s.sigma,
      }),
    ]),
    b.hinweis ? el('p.hinweis', { text: b.hinweis }) : null,
  ]);
}
