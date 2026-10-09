/**
 * spannungsbild.js -- was im Querschnitt geschieht, gezeichnet.
 *
 * Bilder zu den vier Fragen aus `opencivil/spannungsanalyse.py`:
 *
 *   Dehnung und Spannung über die Höhe   -- für «aus N und M» und «aus Dehnungen»
 *   Momenten-Krümmungs-Linie M–χ         -- bei festgehaltener Normalkraft
 *   Normalkraft-Dehnungs-Linie N–ε       -- bei festgehaltenem Moment
 *
 * Die Höhe läuft nach unten, wie man einen Schnitt zeichnet: z = 0 ist die
 * Oberkante. Das ist dieselbe Achse, die der Löser und der Lagenaufbau
 * benutzen -- ein Bild, das sie umdrehte, passte nicht zum Nachweis daneben.
 *
 * Gerechnet wird hier nichts. Alle Zahlen kommen fertig aus dem Kern; diese
 * Datei setzt Striche.
 */

import { achsenkreuz, formelText } from './achsen.js';
import { beschriftungenEntzerren } from './diagramm.js';
import { el, svgEl } from './dom.js';
import { span } from './mathe.js';
import { zustand } from './zustand.js';

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

  daten.append(formelText(svgEl('text', {
    x: RAND.links, y: 14, 'font-size': 11, 'font-weight': 600, fill: SCHRIFT,
  }), titel));

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

/**
 * Was eine Linie ausmacht, je Art: wie Kraft und Verformung heissen, in
 * welcher Einheit sie stehen, und was festgehalten wird. Die Namen in der
 * Schreibweise von `formelText`, für KaTeX daneben dieselben noch einmal.
 */
const LINIEN = {
  moment_kruemmung: {
    kraft: 'M', kraftEinheit: 'kNm', verformungEinheit: '1/m', stellen: 4,
    verformung: (index) => (index ? `χ_{${index}}` : 'χ'),
    latex: (index) => (index ? `\\chi_{${index}}` : '\\chi'),
    fest: ['N', 'kN'], achse: 'χ [1/m]',
  },
  normalkraft_dehnung: {
    kraft: 'N', kraftEinheit: 'kN', verformungEinheit: '‰', stellen: 2,
    verformung: (index) => (index ? `ε_{m,${index}}` : 'ε_m'),
    latex: (index) => (index ? `\\varepsilon_{m,${index}}` : '\\varepsilon_{m}'),
    fest: ['M', 'kNm'], achse: 'ε_m [‰]   (auf halber Höhe)',
  },
};

/** Zeilenabstand der Namen an den Eckpunkten. */
const ZEILE = 12.5;

/** Ungefähre Breite einer Zeile -- ohne Satzzeichen des Formelsatzes, ein Index schmaler. */
function zeilenbreite(zeile) {
  const index = [...zeile.matchAll(/_\{([^}]*)\}|_([A-Za-z0-9]+)/g)]
    .reduce((summe, m) => summe + (m[1] ?? m[2]).length, 0);
  const alles = zeile.replace(/[_{}]/g, '').length;
  return 6.3 * (alles - index) + 4.8 * index;
}

/**
 * Die Namen der Eckpunkte, ohne dass sie einander decken. Jeder probiert der
 * Reihe nach einige Lagen um seinen Punkt -- unten rechts, unten links, oben
 * links, oben rechts, dann weiter unten -- und nimmt die erste, die im Feld
 * liegt und keinen schon gesetzten Namen berührt. Passt keine, steht er an
 * der ersten, ins Feld geschoben.
 *
 * Eine Ecke: `px`, `py`, `zeilen` (die erste in Farbe, die übrigen zart),
 * `farbe`.
 */
function eckenAnschreiben(daten, feld, ecken) {
  const gesetzt = [];
  const frei = (k) => k.links >= feld.links + 2 && k.rechts <= feld.rechts - 2
    && k.oben >= feld.oben + 2 && k.unten <= feld.unten - 2
    && gesetzt.every((g) => k.rechts + 3 < g.links || k.links - 3 > g.rechts
      || k.unten + 2 < g.oben || k.oben - 2 > g.unten);
  for (const { px, py, zeilen, farbe } of ecken) {
    const breite = Math.max(...zeilen.map(zeilenbreite));
    const hoehe = (zeilen.length - 1) * ZEILE + 11;
    const lagen = [[1, 15], [-1, 15], [-1, -8 - hoehe + 11], [1, -8 - hoehe + 11],
      [-1, 19 + hoehe], [1, 19 + hoehe], [-1, 23 + 2 * hoehe]];
    const kasten = ([seite, dy]) => {
      const x = px + seite * 7;
      return {
        x, y: py + dy, seite,
        links: seite > 0 ? x : x - breite, rechts: seite > 0 ? x + breite : x,
        oben: py + dy - 9, unten: py + dy - 9 + hoehe,
      };
    };
    let k = lagen.map(kasten).find(frei);
    if (!k) {
      k = kasten(lagen[0]);
      const schub = Math.min(0, feld.rechts - 2 - k.rechts) + Math.max(0, feld.links + 2 - k.links);
      Object.assign(k, { x: k.x + schub, links: k.links + schub, rechts: k.rechts + schub });
    }
    gesetzt.push(k);
    daten.append(svgEl('circle', {
      cx: px, cy: py, r: 3.2, fill: '#fff', stroke: farbe, 'stroke-width': 1.6,
    }));
    zeilen.forEach((zeile, i) => {
      daten.append(formelText(svgEl('text', {
        x: k.x, y: k.y + i * ZEILE, 'text-anchor': k.seite > 0 ? 'start' : 'end',
        'font-size': i ? 9.5 : 10.5, 'font-weight': i ? 400 : 600,
        fill: i ? SCHRIFT : farbe, ...HOF,
      }), zeile));
    });
  }
}

/** Eine Zahl mit Einheit, «-» als Minus. */
function mitEinheit(wert, stellen, einheit) {
  return `${zahl(wert, stellen).replace('-', '−')} ${einheit}`;
}

/**
 * Eine Linie: ungerissen bis zum Riss, dort waagrecht nach rechts -- der
 * Querschnitt reisst, bei derselben Kraft verformt er sich mehr --, darüber
 * gerissen bis zum Bruch. Gestrichelt die beiden Zustände je für sich. An
 * den Ecken Riss, Fliessbeginn und Ende, je mit Kraft und Verformung.
 */
function linienbild(fall) {
  const k = fall.kurve;
  const art = LINIEN[fall.art];
  const ende = k.punkte[k.punkte.length - 1];
  const verformungen = k.punkte.map((p) => p.verformung);
  const vMin = Math.min(0, ...verformungen);
  const vMax = Math.max(1e-9, ...verformungen);
  const kMax = Math.max(1e-9, ...k.punkte.map((p) => p.kraft));
  const spanne = vMax - vMin;
  const { svg, daten, x, y, feld } = achsenkreuz({
    breite: BREITE * 2, hoehe: HOEHE, rand: RAND, rahmen: true,
    attribute: { class: 'sd-bild sd-breit', preserveAspectRatio: 'xMidYMid meet' },
    x: { bereich: [vMin - (vMin < 0 ? 0.05 * spanne : 0), vMax + 0.05 * spanne], titel: art.achse },
    y: { bereich: [0, kMax * 1.05], titel: `${art.kraft} [${art.kraftEinheit}]` },
    schrift: { teilung: 9.5, titel: 11 }, titelLinks: 12,
  });

  const linie = (hol, farbe, breiteStrich, muster) => {
    const punkte = k.punkte.filter((p) => hol(p) !== null && hol(p) !== undefined);
    if (punkte.length < 2) return;
    daten.append(svgEl('polyline', {
      points: punkte.map((p) => `${x(hol(p)).toFixed(2)},${y(p.kraft).toFixed(2)}`).join(' '),
      fill: 'none', stroke: farbe, 'stroke-width': breiteStrich,
      'stroke-dasharray': muster || null,
    }));
  };
  linie((p) => p.verformung_I, ACHSE, 1.2, '4 3');
  linie((p) => p.verformung_II, ACHSE, 1.2, '2 3');
  linie((p) => p.verformung, '#16794a', 2.2);

  const v = (wert) => mitEinheit(wert, art.stellen, art.verformungEinheit);
  const f = (wert) => mitEinheit(wert, 1, art.kraftEinheit);
  const kennwert = fall.wahl?.satz === 'charakteristisch' ? 'Rk' : 'Rd';
  const ecken = [];
  // Das Ende zuerst: es steht am Rand, und die anderen weichen ihm aus.
  // Endet die Linie ungerissen, trägt der Querschnitt den Riss nicht; dann
  // gilt dort ihre letzte Verformung, nicht die gerissene des Bruchs.
  if (ende && k.bruch) {
    ecken.push({
      px: x(ende.verformung), py: y(ende.kraft), farbe: '#16794a',
      zeilen: ende.gerissen
        ? [`${art.kraft}_{${kennwert},u} = ${f(k.bruch.kraft)}`,
          `${art.verformung('u')} = ${v(k.bruch.verformung)}`, k.bruch.massgebend]
        : [`${art.kraft}_{${kennwert},u} = ${f(k.bruch.kraft)}`,
          `${art.verformung('')} = ${v(ende.verformung)}`],
    });
  }
  if (k.fliessen) {
    ecken.push({
      px: x(k.fliessen.verformung), py: y(k.fliessen.kraft), farbe: STAHL,
      zeilen: [`${art.kraft}_y = ${f(k.fliessen.kraft)}`,
        `${art.verformung('y')} = ${v(k.fliessen.verformung)}`],
    });
  }
  // Der Riss: ein Punkt vor dem waagrechten Stück, der Name an seinem Ende.
  if (k.sprung) {
    daten.append(svgEl('circle', {
      cx: x(k.sprung.vor), cy: y(k.sprung.kraft), r: 2.4, fill: ZUG,
    }));
    ecken.push({
      px: x(k.sprung.nach), py: y(k.sprung.kraft), farbe: ZUG,
      zeilen: [`${art.kraft}_{Riss} = ${f(k.sprung.kraft)}`,
        `${art.verformung('')} = ${zahl(k.sprung.vor, art.stellen)} → ${v(k.sprung.nach)}`],
    });
  }
  eckenAnschreiben(daten, feld, ecken);

  // Ohne Gitter: an den Achsen stehen nur die Grösstwerte.
  for (const [wert, px, py, anker] of [
    [vMax.toFixed(art.stellen), feld.rechts, HOEHE - 22, 'end'],
    [kMax.toFixed(0), feld.links - 5, feld.oben + 8, 'end'],
  ]) {
    const t = svgEl('text', {
      x: px, y: py, 'text-anchor': anker, 'font-size': 9.5, fill: ACHSE,
    });
    t.textContent = wert;
    svg.append(t);
  }
  return svg;
}

/** Die Zahlen über dem Bild, die Namen als Formel: χ ist dort kein x. */
function zahlenzeile(eintraege) {
  return el('div.sd-zahlen', {}, eintraege.map(([latex, wert]) =>
    el('span', {}, [el('b', {}, [span(`${latex} =`)]), ` ${wert}`])));
}

/** Womit gerechnet wurde -- die Kriechzahl auch dann, wenn sie die der Platte ist. */
function wahlzeile(wahl) {
  if (!wahl) return null;
  const katalog = zustand.katalog?.spannungsanalyse || {};
  const name = (liste, wert) => (liste || []).find((e) => e.wert === wert)?.beschriftung ?? wert;
  return el('div.sd-wahl-text', {}, [
    span('\\varphi'),
    ` = ${wahl.phi.toFixed(2)}${wahl.phi_eigen ? '' : ' (Platte)'} · `
      + `${name(katalog.werkstoffsaetze, wahl.satz)} · ${name(katalog.betongesetze, wahl.gesetz)}`,
  ]);
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
    const art = LINIEN[fall.art];
    const K = art.kraft;
    const kennwert = fall.wahl?.satz === 'charakteristisch' ? 'Rk' : 'Rd';
    const kraft = (wert) => mitEinheit(wert, 1, art.kraftEinheit);
    return el('div.sd-fall', {}, [
      kopf,
      wahlzeile(fall.wahl),
      zahlenzeile([
        [art.fest[0], mitEinheit(k.fest, 1, art.fest[1])],
        [`${K}_{Riss}`, kraft(k.riss)],
        ...(k.fliessen ? [[`${K}_{y}`, kraft(k.fliessen.kraft)]] : []),
        ...(k.bruch ? [[`${K}_{${kennwert},u}`, kraft(k.bruch.kraft)],
          [art.latex('u'), mitEinheit(k.bruch.verformung, art.stellen, art.verformungEinheit)]]
          : []),
      ]),
      k.punkte.length ? linienbild(fall) : null,
      el('p.sd-legende', {
        text: 'Durchgezogen: der Querschnitt – ungerissen bis zum Riss, dann der Sprung, '
          + 'darüber gerissen (ohne Zugversteifung) · lang gestrichelt: immer ungerissen (I) '
          + '· kurz gestrichelt: immer gerissen, ohne f_ct (II)',
      }),
      k.hinweis ? el('p.hinweis', { text: k.hinweis }) : null,
    ]);
  }

  const b = fall.bild;
  if (!b.konvergiert) {
    return el('div.sd-fall', {}, [kopf, wahlzeile(fall.wahl), el('p.hinweis', { text: b.hinweis })]);
  }
  return el('div.sd-fall', {}, [
    kopf,
    wahlzeile(fall.wahl),
    zahlenzeile([
      ['N', mitEinheit(b.N, 1, 'kN')],
      ['M', mitEinheit(b.M, 1, 'kNm')],
      ['\\varepsilon_{m}', mitEinheit(b.eps_m, 3, '‰')],
      ['\\chi', mitEinheit(b.chi, 5, '1/m')],
      ['x', b.nulllinie === null ? '–' : mitEinheit(b.nulllinie, 0, 'mm')],
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
