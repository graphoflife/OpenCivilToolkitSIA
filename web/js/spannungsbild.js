/**
 * spannungsbild.js -- was im Querschnitt geschieht, als Diagramm.
 *
 * Diagramme zu den sechs Fragen aus `opencivil/spannungsanalyse.py`:
 *
 *   Dehnung und Spannung über die Höhe   -- für «aus N und M» und «aus Dehnungen»
 *   Momenten-Krümmungs-Linie M–χ         -- bei festgehaltener Normalkraft
 *   Normalkraft-Dehnungs-Linie N–ε       -- bei festgehaltenem Moment
 *   Äquivalenter E-Modul M–E_eq, N–E_eq  -- dieselben Linien, umgerechnet
 *
 * Gezeichnet wie das M-N-Interaktionsdiagramm und die Querkraftkurven:
 * gleich gross, mit Gitter und Teilung an beiden Achsen, darunter die
 * Legende, und über den Punkten steht beim Darüberfahren, was sie sind
 * (Benutzer, 2026-10-16). Vorher waren es kleine Bilder ohne Teilung, mit
 * den Grösstwerten an den Achsen. Dehnung und Spannung stehen in einem
 * Diagramm: zwei Felder nebeneinander mit derselben Höhenachse -- die
 * Nulllinie läuft durch beide.
 *
 * Die Höhe läuft nach unten, wie man einen Schnitt zeichnet: z = 0 ist die
 * Oberkante. Das ist dieselbe Achse, die der Löser und der Lagenaufbau
 * benutzen -- ein Bild, das sie umdrehte, passte nicht zum Nachweis daneben.
 *
 * Gerechnet wird hier nichts. Alle Zahlen kommen fertig aus dem Kern; diese
 * Datei setzt Striche.
 */

import { achsenkreuz, formelText, NR, schrittweite } from './achsen.js';
import { karte } from './bausteine.js';
import { beschriftungenEntzerren } from './diagramm.js';
import { el, svgEl } from './dom.js';
import { span } from './mathe.js';
import { zustand } from './zustand.js';

/** Dieselbe Grösse und derselbe Rand wie das M-N-Interaktionsdiagramm. */
const BREITE = 720;
const HOEHE = 520;
const RAND = { oben: 22, rechts: 22, unten: 46, links: 74 };

/** Wo das Feld der Dehnung endet und das der Spannung beginnt. */
const TEILUNG_FELDER = 384;

const ZUG = '#b3261e';
const DRUCK = '#1d4ed8';
const STAHL = '#b45309';
const NULLLINIE = '#16794a';
const LINIE = '#16794a';
const VERGLEICH = '#8895a8';
const SCHRIFT = '#1a1f27';

/** So weit reicht der Wertebereich über den grössten Wert hinaus: Platz für seine Zahl. */
const SPIELRAUM = 1.25;

/** Weiss hinterlegt, damit eine Zahl auch über einem Strich lesbar bleibt. */
const HOF = { 'paint-order': 'stroke', stroke: '#fff', 'stroke-width': 3 };

/** Die Schrift der Zahlen und Namen im Diagramm -- wie im M-N-Diagramm. */
const SCHRIFTGROESSE = 11;

/**
 * Die Teilung einer Achse mit so vielen Nachkommastellen, wie ihr Schritt
 * verlangt: eine Krümmung von 0.004 1/m hiesse mit ganzen Zahlen überall 0.
 */
function teilung([a, b], ziel = 8) {
  const schritt = schrittweite(Math.abs(b - a) || 1, ziel);
  const stellen = Math.max(0, Math.ceil(-Math.log10(schritt) - 1e-9));
  return { ziel, format: (v) => zahl(v, stellen) };
}

/** Eine Zahl ohne «-0.0». */
function zahl(wert, stellen) {
  return (Math.abs(wert) < 0.5 * 10 ** -stellen ? 0 : wert).toFixed(stellen);
}

/** Eine Zahl mit Einheit, «-» als Minus. */
function mitEinheit(wert, stellen, einheit) {
  return `${zahl(wert, stellen).replace('-', '−')} ${einheit}`;
}

/** Ein Text im Diagramm, als Formel gesetzt, mit weissem Hof. */
function beschriftung(attribute, inhalt) {
  return formelText(svgEl('text', {
    'font-size': SCHRIFTGROESSE, fill: SCHRIFT, ...HOF, ...attribute,
  }), inhalt);
}

/** Ein Tooltip für einen Punkt -- wie im M-N-Diagramm über `title`. */
function mitTitel(knoten, text) {
  const titel = svgEl('title');
  titel.textContent = text;
  knoten.append(titel);
  return knoten;
}

// ===========================================================================
// Die Legende
// ===========================================================================

/** Ein Strichmuster als kleine Probe für die Legende. */
function strich(farbe, { muster = null, breite = 2.2 } = {}) {
  const probe = svgEl('svg', { width: 26, height: 10, viewBox: '0 0 26 10', 'aria-hidden': 'true' });
  probe.append(svgEl('line', {
    x1: 1, y1: 5, x2: 25, y2: 5, stroke: farbe, 'stroke-width': breite,
    'stroke-dasharray': muster,
  }));
  return probe;
}

/** Ein Punkt für die Legende: gefüllt, oder hohl wie die Ecken der Linien. */
function punkt(farbe, hohl = false) {
  return el('i', {
    style: hohl ? { background: '#fff', border: `2px solid ${farbe}`, boxSizing: 'border-box' }
      : { background: farbe },
  });
}

/** Eine Fläche für die Legende: Druck oder Zug. */
function flaeche(farbe) {
  return el('i', {
    style: {
      background: farbe, opacity: 0.35, borderRadius: '2px', border: `1px solid ${farbe}`,
    },
  });
}

function legende(eintraege) {
  return el('div.mn-legende', {}, eintraege.map(([probe, text]) => el('span', {}, [probe, text])));
}

// ===========================================================================
// Dehnung und Spannung über die Höhe
// ===========================================================================

/** Die gefüllte Fläche zwischen Nulllinie und Verlauf -- Druck und Zug getrennt. */
function verlauf(daten, x, y, punkte, hol) {
  for (const [vorzeichen, farbe] of [[-1, DRUCK], [1, ZUG]]) {
    const teil = punkte.map((p) => (Math.sign(hol(p)) === vorzeichen ? hol(p) : 0));
    if (!teil.some((w) => w !== 0)) continue;
    const ecken = punkte.map((p, i) => `${x(teil[i]).toFixed(1)},${y(p.z).toFixed(1)}`);
    daten.append(svgEl('polygon', {
      points: [`${x(0)},${y(punkte[0].z)}`, ...ecken,
        `${x(0)},${y(punkte[punkte.length - 1].z)}`].join(' '),
      fill: farbe, 'fill-opacity': 0.16, stroke: farbe, 'stroke-width': 1.6,
    }));
  }
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
function anschreiben(daten, x, feld, zettel, stellen) {
  const oben = feld.oben + 10;
  const unten = feld.unten - 3;
  for (const seite of [-1, 1]) {
    const teil = zettel.filter((z) => (zahl(z.wert, stellen) < 0 ? -1 : 1) === seite);
    if (!teil.length) continue;
    for (const z of beschriftungenEntzerren(teil, 13, oben, unten)) {
      const px = x(z.wert) + seite * 6;
      if (Math.abs(z.y - z.soll) > 2) {
        daten.append(svgEl('line', {
          x1: x(z.wert), y1: z.punkt, x2: px - seite, y2: z.y - 4,
          stroke: z.farbe, 'stroke-width': 0.8, 'stroke-opacity': 0.7,
        }));
      }
      daten.append(beschriftung({
        x: px, y: z.y, 'text-anchor': seite < 0 ? 'end' : 'start',
        'font-weight': 600, fill: z.farbe,
      }, zahl(z.wert, stellen)));
    }
  }
}

/**
 * Ein Feld des Diagramms: Dehnung oder Spannung über die Höhe, mit den
 * Bewehrungslagen darin. `links` sagt, ob es die Höhenachse trägt -- das
 * rechte Feld teilt sie, ohne sie ein zweites Mal anzuschreiben.
 */
function hoehenfeld(bild, {
  breite, rand, titel, hol, stahlHol, stellen, einheit, links,
}) {
  // Um null herum aufgespannt: eine Spannungsverteilung ohne sichtbare
  // Nulllinie sagt nicht, wo Druck aufhört und Zug anfängt.
  const werte = [...bild.beton.map(hol), ...bild.stahl.map(stahlHol)];
  const grenze = Math.max(1e-9, ...werte.map(Math.abs)) * SPIELRAUM;
  const bereich = [-grenze, grenze];
  const { svg, daten, x, y, feld } = achsenkreuz({
    breite, hoehe: HOEHE, rand,
    attribute: { x: links ? 0 : TEILUNG_FELDER, y: 0, width: breite, height: HOEHE },
    x: { bereich, teilung: teilung(bereich, 6), null: true, titel },
    // Die Höhe läuft nach unten. Das rechte Feld zieht dieselben Linien,
    // ohne Zahlen daran.
    y: {
      bereich: [bild.h, 0],
      teilung: links ? teilung([0, bild.h], 8) : { ziel: 8, format: () => '' },
      titel: links ? 'z [mm]  (ab Oberkante)' : null,
    },
  });
  verlauf(daten, x, y, bild.beton, hol);

  if (bild.nulllinie !== null && bild.nulllinie !== undefined) {
    daten.append(svgEl('line', {
      x1: feld.links, y1: y(bild.nulllinie), x2: feld.rechts, y2: y(bild.nulllinie),
      stroke: NULLLINIE, 'stroke-width': 1.4, 'stroke-dasharray': '6 4',
    }));
    if (!links) {
      daten.append(beschriftung({
        x: feld.rechts - 4, y: y(bild.nulllinie) - 5, 'text-anchor': 'end', fill: NULLLINIE,
      }, `x = ${bild.nulllinie.toFixed(0)} mm`));
    }
  }

  for (const lage of bild.stahl) {
    const wert = stahlHol(lage);
    daten.append(svgEl('line', {
      x1: x(0), y1: y(lage.z), x2: x(wert), y2: y(lage.z), stroke: STAHL, 'stroke-width': 2.4,
    }));
    daten.append(mitTitel(svgEl('circle', {
      cx: x(wert), cy: y(lage.z), r: 4.5, fill: STAHL, stroke: '#fff', 'stroke-width': 1.5,
    }), `${lage.name || `${lage.nummer}. Lage`} – ${lage.a_s.toFixed(0)} mm², z = ${lage.z.toFixed(0)} mm\n`
      + `ε = ${lage.eps.toFixed(3)} ‰, σ = ${lage.sigma.toFixed(0)} N/mm²\n`
      + `F = ${lage.kraft.toFixed(1)} kN`));
  }

  // Der Beton am Rand: zuoberst knapp unter, zuunterst knapp über der Kante.
  const betonfarbe = (w) => (w < 0 ? DRUCK : w > 0 ? ZUG : VERGLEICH);
  const kopf = bild.beton[0];
  const fuss = bild.beton[bild.beton.length - 1];
  for (const [p, wo] of [[kopf, 'Oberkante'], [fuss, 'Unterkante']]) {
    daten.append(mitTitel(svgEl('circle', {
      cx: x(hol(p)), cy: y(p.z), r: 3.5, fill: betonfarbe(hol(p)), stroke: '#fff', 'stroke-width': 1.2,
    }), `Beton an der ${wo}: ${zahl(hol(p), stellen)} ${einheit}`));
  }
  anschreiben(daten, x, feld, [
    { wert: hol(kopf), punkt: y(0), soll: y(0) + 12, farbe: betonfarbe(hol(kopf)) },
    { wert: hol(fuss), punkt: y(bild.h), soll: y(bild.h) - 4, farbe: betonfarbe(hol(fuss)) },
    ...bild.stahl.map((lage) => ({
      wert: stahlHol(lage), punkt: y(lage.z), soll: y(lage.z) + 4, farbe: STAHL,
    })),
  ], stellen);
  return svg;
}

/**
 * Dehnung und Spannung über die Höhe in einem Diagramm: links die Dehnung,
 * rechts die Spannung, beide an derselben Höhenachse (Benutzer, 2026-10-16).
 * Zwei Felder statt zweier Achsen in einem: die Einheiten sind verschieden,
 * und übereinander gezeichnet läse man die eine Kurve an der Achse der
 * anderen.
 */
function verteilungsbild(bild) {
  const svg = svgEl('svg', {
    class: 'mn', xmlns: NR, viewBox: `0 0 ${BREITE} ${HOEHE}`, role: 'img',
    'aria-label': 'Dehnung und Spannung über die Höhe',
  });
  svg.append(
    hoehenfeld(bild, {
      breite: TEILUNG_FELDER, rand: { ...RAND, rechts: 16 }, links: true,
      titel: 'Dehnung ε [‰]', einheit: '‰', stellen: 2,
      hol: (p) => p.eps, stahlHol: (s) => s.eps,
    }),
    hoehenfeld(bild, {
      breite: BREITE - TEILUNG_FELDER, rand: { ...RAND, links: 16 }, links: false,
      titel: 'Spannung σ [N/mm²]', einheit: 'N/mm²', stellen: 1,
      hol: (p) => p.sigma, stahlHol: (s) => s.sigma,
    }),
  );
  return el('div.diagramm-huelle', {}, [
    svg,
    legende([
      [flaeche(DRUCK), 'Druck im Beton'],
      [flaeche(ZUG), 'Zug im Beton'],
      [punkt(STAHL), 'Bewehrungslage'],
      [strich(NULLLINIE, { muster: '6 4', breite: 1.6 }), 'Nulllinie'],
    ]),
  ]);
}

// ===========================================================================
// Die Linien: M–χ, N–ε, M–E_eq, N–E_eq
// ===========================================================================

/*
 * Was eine Linie zeigt, bringt sie mit (`kurve.groessen`, aus dem Kern): die
 * laufende Kraft, die festgehaltene und die Verformung bzw. den Modul, je mit
 * Zeichen, Einheit und Stellen -- dort, wo der Kern ihre Zahlen auch
 * skaliert. Bis 2026-10-18 stand dasselbe hier ein zweites Mal, je Art
 * (LINIEN, MODULE), und das Vielfache von E_cm rechnete die Oberfläche.
 */

/**
 * Ein Zeichen mit Index, in der Schreibweise von `formelText` oder für KaTeX:
 * χ_{u}, ε_{m,u} -- ein vorhandener Index wird ergänzt, nicht ersetzt.
 */
function mitIndex(groesse, index, latex = false) {
  const zeichen = latex ? groesse.latex : groesse.zeichen;
  const m = zeichen.match(/^(.*?)_\{?([^}]*)\}?$/);
  return m ? `${m[1]}_{${m[2]},${index}}` : `${zeichen}_{${index}}`;
}

/** Zeilenabstand der Namen an den Eckpunkten. */
const ZEILE = 14;

/** Ungefähre Breite einer Zeile -- ohne Satzzeichen des Formelsatzes, ein Index schmaler. */
function zeilenbreite(zeile) {
  const index = [...zeile.matchAll(/_\{([^}]*)\}|_([A-Za-z0-9]+)/g)]
    .reduce((summe, m) => summe + (m[1] ?? m[2]).length, 0);
  const alles = zeile.replace(/[_{}]/g, '').length;
  return 6.7 * (alles - index) + 5.1 * index;
}

/**
 * Die Namen der Eckpunkte, ohne dass sie einander decken. Jeder probiert der
 * Reihe nach einige Lagen um seinen Punkt -- unten rechts, unten links, oben
 * links, oben rechts, dann weiter unten -- und nimmt die erste, die im Feld
 * liegt und keinen schon gesetzten Namen berührt. Sind die Lagen am Punkt
 * besetzt -- zwei Ecken dicht beisammen --, rückt er schrittweise höher, und
 * ein feiner Strich zeigt, wohin er gehört. Passt keine, steht er an der
 * ersten, ins Feld geschoben.
 *
 * Eine Ecke: `px`, `py`, `zeilen` (die erste in Farbe, die übrigen zart),
 * `farbe`. Über dem Punkt steht beim Darüberfahren dasselbe.
 */
function eckenAnschreiben(daten, feld, ecken) {
  const gesetzt = [];
  const frei = (k) => k.links >= feld.links + 2 && k.rechts <= feld.rechts - 2
    && k.oben >= feld.oben + 2 && k.unten <= feld.unten - 2
    && gesetzt.every((g) => k.rechts + 3 < g.links || k.links - 3 > g.rechts
      || k.unten + 2 < g.oben || k.oben - 2 > g.unten);
  for (const { px, py, zeilen, farbe } of ecken) {
    const breite = Math.max(...zeilen.map(zeilenbreite));
    const hoehe = (zeilen.length - 1) * ZEILE + 12;
    const lagen = [[1, 17], [-1, 17], [-1, -9 - hoehe + 12], [1, -9 - hoehe + 12],
      [-1, 21 + hoehe], [1, 21 + hoehe], [-1, 25 + 2 * hoehe]];
    // Weiter oben, je eine Höhe mehr -- mit Strich zum Punkt.
    const nah = lagen.length;
    for (let n = 1; n <= 8; n += 1) {
      const dy = -9 - hoehe + 12 - n * (hoehe + 6);
      lagen.push([-1, dy], [1, dy]);
    }
    const kasten = ([seite, dy]) => {
      const x = px + seite * 8;
      return {
        x, y: py + dy, seite,
        links: seite > 0 ? x : x - breite, rechts: seite > 0 ? x + breite : x,
        oben: py + dy - 10, unten: py + dy - 10 + hoehe,
      };
    };
    const wahl = lagen.findIndex((lage) => frei(kasten(lage)));
    let k = wahl >= 0 ? kasten(lagen[wahl]) : null;
    if (!k) {
      k = kasten(lagen[0]);
      const schub = Math.min(0, feld.rechts - 2 - k.rechts) + Math.max(0, feld.links + 2 - k.links);
      Object.assign(k, { x: k.x + schub, links: k.links + schub, rechts: k.rechts + schub });
    } else if (wahl >= nah) {
      daten.append(svgEl('line', {
        x1: px, y1: py, x2: k.seite > 0 ? k.links : k.rechts, y2: k.unten,
        stroke: farbe, 'stroke-width': 0.8, opacity: 0.6,
      }));
    }
    gesetzt.push(k);
    daten.append(mitTitel(svgEl('circle', {
      cx: px, cy: py, r: 4.5, fill: '#fff', stroke: farbe, 'stroke-width': 2,
    }), zeilen.map((z) => z.replace(/_\{([^}]*)\}/g, '_$1')).join('\n')));
    zeilen.forEach((zeile, i) => {
      daten.append(beschriftung({
        x: k.x, y: k.y + i * ZEILE, 'text-anchor': k.seite > 0 ? 'start' : 'end',
        'font-size': i ? SCHRIFTGROESSE - 1 : SCHRIFTGROESSE, 'font-weight': i ? 400 : 600,
        fill: i ? SCHRIFT : farbe,
      }, zeile));
    });
  }
}

/**
 * Ein leeres Diagramm für eine Linie: so gross wie das M-N-Diagramm, mit
 * Gitter und Teilung an beiden Achsen.
 */
function linienkreuz(xBereich, yBereich, xTitel, yTitel, beschreibung) {
  return achsenkreuz({
    breite: BREITE, hoehe: HOEHE, rand: RAND,
    attribute: { class: 'mn', xmlns: NR, role: 'img', 'aria-label': beschreibung },
    x: { bereich: xBereich, teilung: teilung(xBereich), null: true, titel: xTitel },
    y: { bereich: yBereich, teilung: teilung(yBereich), null: true, titel: yTitel },
  });
}

/** Eine Polylinie aus den Punkten, bei denen `hol` einen Wert hat. */
function zug(daten, punkte, px, py, { farbe, breite, muster = null }) {
  const da = punkte.filter((p) => px(p) !== null && py(p) !== null);
  if (da.length < 2) return;
  daten.append(svgEl('polyline', {
    points: da.map((p) => `${px(p).toFixed(2)},${py(p).toFixed(2)}`).join(' '),
    fill: 'none', stroke: farbe, 'stroke-width': breite, 'stroke-dasharray': muster,
    'stroke-linejoin': 'round',
  }));
}

/** Die Legende unter jeder Linie: was durchgezogen und was gestrichelt ist, und die Ecken. */
function linienlegende(K, kennwert) {
  return legende([
    [strich(LINIE), 'Querschnitt: ungerissen bis zum Riss, darüber gerissen (ohne Zugversteifung)'],
    [strich(VERGLEICH, { muster: '6 4', breite: 1.4 }), 'ungerissen (I), bis zum Riss'],
    [strich(VERGLEICH, { muster: '2 3', breite: 1.4 }), 'immer gerissen, ohne f_ct (II)'],
    [punkt(ZUG, true), 'Riss'],
    [punkt(STAHL, true), `${K}_y: Fliessbeginn`],
    [punkt(LINIE, true), `${K}_${kennwert}: Ende der Linie, der Widerstand – wie in der `
      + 'Tragsicherheit, wenn sie gleich wählt'],
  ]);
}

/**
 * Eine Linie: ungerissen bis zum Riss, dort waagrecht nach rechts -- der
 * Querschnitt reisst, bei derselben Kraft verformt er sich mehr --, darüber
 * gerissen bis zum Bruch. Gestrichelt die beiden Zustände je für sich. An
 * den Ecken Riss, Fliessbeginn und Ende, je mit Kraft und Verformung.
 */
function linienbild(fall) {
  const k = fall.kurve;
  const { kraft: K, verformung: V } = k.groessen;
  const ende = k.punkte[k.punkte.length - 1];
  const verformungen = k.punkte.map((p) => p.verformung);
  const vMin = Math.min(0, ...verformungen);
  const vMax = Math.max(1e-9, ...verformungen);
  const kMax = Math.max(1e-9, ...k.punkte.map((p) => p.kraft));
  const spanne = vMax - vMin;
  const { svg, daten, x, y, feld } = linienkreuz(
    [vMin - (vMin < 0 ? 0.05 * spanne : 0), vMax + 0.05 * spanne], [0, kMax * 1.08],
    `${V.zeichen} [${V.einheit}]${V.am_bezugsort ? `   (${fall.bezugsort})` : ''}`,
    `${K.zeichen} [${K.einheit}]`, fall.titel);

  const wert = (hol) => (p) => {
    const v = hol(p);
    return v === null || v === undefined ? null : x(v);
  };
  const kraft = (p) => y(p.kraft);
  zug(daten, k.punkte, wert((p) => p.verformung_I), kraft,
    { farbe: VERGLEICH, breite: 1.4, muster: '6 4' });
  zug(daten, k.punkte, wert((p) => p.verformung_II), kraft,
    { farbe: VERGLEICH, breite: 1.4, muster: '2 3' });
  zug(daten, k.punkte, wert((p) => p.verformung), kraft, { farbe: LINIE, breite: 2.4 });

  const v = (w) => mitEinheit(w, V.stellen, V.einheit);
  const f = (w) => mitEinheit(w, 1, K.einheit);
  const kennwert = fall.wahl?.index || 'Rd';
  const ecken = [];
  // Das Ende zuerst: es steht am Rand, und die anderen weichen ihm aus.
  // Endet die Linie ungerissen, trägt der Querschnitt den Riss nicht; dann
  // gilt dort ihre letzte Verformung, nicht die gerissene des Bruchs.
  if (ende && k.bruch) {
    ecken.push({
      px: x(ende.verformung), py: y(ende.kraft), farbe: LINIE,
      zeilen: ende.gerissen
        ? [`${K.zeichen}_{${kennwert}} = ${f(k.bruch.kraft)}`,
          `${mitIndex(V, 'u')} = ${v(k.bruch.verformung)}`, k.bruch.massgebend]
        : [`${K.zeichen}_{${kennwert}} = ${f(k.bruch.kraft)}`,
          `${V.zeichen} = ${v(ende.verformung)}`],
    });
  }
  // Der Fliessbeginn heisst M_y bzw. N_y, wie seine Verformung; das Ende
  // M_Rd bzw. N_Rd -- mit charakteristischen Werten Rk --, wie der
  // Widerstand der Tragsicherheit bei derselben Rechenwahl.
  if (k.fliessen) {
    ecken.push({
      px: x(k.fliessen.verformung), py: y(k.fliessen.kraft), farbe: STAHL,
      zeilen: [`${K.zeichen}_{y} = ${f(k.fliessen.kraft)}`,
        `${mitIndex(V, 'y')} = ${v(k.fliessen.verformung)}`],
    });
  }
  // Der Riss: ein Punkt vor dem waagrechten Stück, der Name an seinem Ende.
  if (k.sprung) {
    daten.append(svgEl('circle', {
      cx: x(k.sprung.vor), cy: y(k.sprung.kraft), r: 3, fill: ZUG,
    }));
    ecken.push({
      px: x(k.sprung.nach), py: y(k.sprung.kraft), farbe: ZUG,
      zeilen: [`${K.zeichen}_{Riss} = ${f(k.sprung.kraft)}`,
        `${V.zeichen} = ${zahl(k.sprung.vor, V.stellen)} → ${v(k.sprung.nach)}`],
    });
  }
  eckenAnschreiben(daten, feld, ecken);
  return el('div.diagramm-huelle', {}, [svg, linienlegende(K.zeichen, kennwert)]);
}

/**
 * Der äquivalente E-Modul über der laufenden Kraft: ungerissen fast
 * waagrecht, beim Riss senkrecht hinunter -- bei derselben Kraft ein anderer
 * Modul --, darüber gerissen bis zum Bruch. Gestrichelt die beiden Zustände
 * je für sich, der ungerissene nur bis zum Riss. An jeder Ecke der Modul und
 * sein Vielfaches von E_cm: am Anfang, vor und nach dem Riss, beim
 * Fliessbeginn und am Ende.
 */
function modulbild(fall) {
  const k = fall.kurve;
  const { kraft: K, modul: M } = k.groessen;
  const werte = k.punkte.flatMap((p) => [p.modul, p.modul_I, p.modul_II])
    .filter((v) => v !== null && v !== undefined);
  const eMax = Math.max(1e-9, ...werte);
  const kMax = Math.max(1e-9, ...k.punkte.map((p) => p.kraft));
  const { svg, daten, x, y, feld } = linienkreuz(
    [0, kMax * 1.05], [0, eMax * 1.1], `${K.zeichen} [${K.einheit}]`,
    `${M.zeichen} [${M.einheit}]`, fall.titel);

  const modul = (hol) => (p) => {
    const v = hol(p);
    return v === null || v === undefined ? null : y(v);
  };
  const kraft = (p) => x(p.kraft);
  zug(daten, k.punkte, kraft, modul((p) => p.modul_I),
    { farbe: VERGLEICH, breite: 1.4, muster: '6 4' });
  zug(daten, k.punkte, kraft, modul((p) => p.modul_II),
    { farbe: VERGLEICH, breite: 1.4, muster: '2 3' });
  zug(daten, k.punkte, kraft, modul((p) => p.modul), { farbe: LINIE, breite: 2.4 });

  const f = (wert) => mitEinheit(wert, 1, K.einheit);
  // Ein Modul mit seinem Vielfachen von E_cm, beides aus dem Kern: an den
  // Ecken `{wert, vielfaches}`, je Punkt die beiden nebeneinander.
  const e = (m) => `${zahl(m.wert, 0)} ${M.einheit} = ${m.vielfaches.toFixed(2)}·E_{cm}`;
  const amPunkt = (p) => ({ wert: p.modul, vielfaches: p.vielfaches });
  const kennwert = fall.wahl?.index || 'Rd';
  const gueltig = k.punkte.filter((p) => p.modul !== null && p.modul !== undefined);
  const ende = gueltig[gueltig.length - 1];
  const anfang = gueltig[0];
  const ecken = [];
  // Das Ende zuerst: es steht am Rand, und die anderen weichen ihm aus.
  if (ende && k.bruch) {
    ecken.push({
      px: x(ende.kraft), py: y(ende.modul), farbe: LINIE,
      zeilen: ende.gerissen
        ? [`${K.zeichen}_{${kennwert}} = ${f(k.bruch.kraft)}`, `E_{eq} = ${e(amPunkt(ende))}`,
          k.bruch.massgebend]
        : [`${K.zeichen}_{${kennwert}} = ${f(k.bruch.kraft)}`, `E_{eq} = ${e(amPunkt(ende))}`],
    });
  }
  if (k.fliessen && k.fliessen.modul !== null) {
    ecken.push({
      px: x(k.fliessen.kraft), py: y(k.fliessen.modul.wert), farbe: STAHL,
      zeilen: [`${K.zeichen}_{y} = ${f(k.fliessen.kraft)}`,
        `E_{eq} = ${e(k.fliessen.modul)}`],
    });
  }
  // Der Riss hat zwei Ecken bei derselben Kraft: ungerissen davor, gerissen
  // danach -- jede mit ihrem Modul.
  if (k.sprung && k.sprung.vor !== null && k.sprung.nach !== null) {
    ecken.push({
      px: x(k.sprung.kraft), py: y(k.sprung.nach.wert), farbe: ZUG,
      zeilen: [`${K.zeichen}_{Riss} = ${f(k.sprung.kraft)}`,
        `E_{eq,II} = ${e(k.sprung.nach)}`],
    });
    ecken.push({
      px: x(k.sprung.kraft), py: y(k.sprung.vor.wert), farbe: ZUG,
      zeilen: [`E_{eq,I} = ${e(k.sprung.vor)}`],
    });
  }
  // Der Anfang: ungerissen der Modul ohne laufende Kraft, gerissen der des
  // ersten Punkts.
  if (anfang && anfang !== ende) {
    ecken.push({
      px: x(anfang.kraft), py: y(anfang.modul), farbe: anfang.gerissen ? LINIE : VERGLEICH,
      zeilen: [`${K.zeichen} = ${f(anfang.kraft)}`, `E_{eq} = ${e(amPunkt(anfang))}`],
    });
  }
  eckenAnschreiben(daten, feld, ecken);
  return el('div.diagramm-huelle', {}, [
    svg,
    linienlegende(K.zeichen, kennwert),
    el('p.karte-hinweis', {
      text: 'E_eq: der E-Modul, den der reine Betonquerschnitt – ungerissen, ohne Stahl, '
        + 'elastisch – bräuchte, um sich gleich stark zu verformen; gezählt ab dem Zustand '
        + 'ohne laufende Kraft.',
    }),
  ]);
}

// ===========================================================================
// Ein Fall als Karte
// ===========================================================================

/** Die Zahlen über dem Diagramm, die Namen als Formel: χ ist dort kein x. */
function zahlenzeile(eintraege) {
  return el('div.sd-zahlen', {}, eintraege.map(([latex, wert]) =>
    el('span', {}, [el('b', {}, [span(`${latex} =`)]), ` ${wert}`])));
}

/** Womit gerechnet wurde: Kriechzahl, Werte, Rechenart. */
function wahlzeile(wahl) {
  if (!wahl) return null;
  const katalog = zustand.katalog?.rechenwahl || {};
  const name = (liste, wert) => (liste || []).find((e) => e.wert === wert)?.beschriftung ?? wert;
  return el('div.sd-wahl-text', {}, [
    span('\\varphi'),
    ` = ${wahl.phi.toFixed(2)} · `
      + `${name(katalog.werkstoffsaetze, wahl.satz)} · ${name(katalog.rechenarten, wahl.rechenart)}`,
  ]);
}

/** Der Inhalt eines Falls: Zahlen und Diagramm -- je nachdem, was er fragt. */
function inhalt(fall) {
  if (!fall.moeglich) return [el('p.hinweis', { text: fall.hinweis })];

  if (fall.kurve?.groessen.modul) {
    const k = fall.kurve;
    const { kraft: Kg, fest: F, modul: M } = k.groessen;
    const K = Kg.zeichen;
    const kennwert = fall.wahl?.index || 'Rd';
    const kraft = (wert) => mitEinheit(wert, 1, Kg.einheit);
    const modul = (m) => (m === null || m === undefined ? '–'
      : `${mitEinheit(m.wert, 0, M.einheit)} = ${m.vielfaches.toFixed(2)}·E_cm`);
    return [
      wahlzeile(fall.wahl),
      zahlenzeile([
        [F.zeichen, mitEinheit(k.fest, 1, F.einheit)],
        [`${K}_{Riss}`, kraft(k.riss)],
        ...(k.sprung ? [['E_{eq,I}', modul(k.sprung.vor)], ['E_{eq,II}', modul(k.sprung.nach)]]
          : []),
        ...(k.fliessen ? [[`${K}_{y}`, kraft(k.fliessen.kraft)],
          ['E_{eq,y}', modul(k.fliessen.modul)]] : []),
        ...(k.bruch ? [[`${K}_{${kennwert}}`, kraft(k.bruch.kraft)],
          ['E_{eq,u}', modul(k.bruch.modul)]] : []),
        ['E_{cm}', mitEinheit(k.E_cm, 0, M.einheit)],
      ]),
      k.punkte.length ? modulbild(fall) : null,
      k.hinweis ? el('p.hinweis', { text: k.hinweis }) : null,
    ];
  }

  if (fall.kurve) {
    const k = fall.kurve;
    const { kraft: Kg, fest: F, verformung: V } = k.groessen;
    const K = Kg.zeichen;
    const kennwert = fall.wahl?.index || 'Rd';
    const kraft = (wert) => mitEinheit(wert, 1, Kg.einheit);
    return [
      wahlzeile(fall.wahl),
      zahlenzeile([
        [F.zeichen, mitEinheit(k.fest, 1, F.einheit)],
        [`${K}_{Riss}`, kraft(k.riss)],
        ...(k.fliessen ? [[`${K}_{y}`, kraft(k.fliessen.kraft)]] : []),
        ...(k.bruch ? [[`${K}_{${kennwert}}`, kraft(k.bruch.kraft)],
          [mitIndex(V, 'u', true), mitEinheit(k.bruch.verformung, V.stellen, V.einheit)]]
          : []),
      ]),
      k.punkte.length ? linienbild(fall) : null,
      k.hinweis ? el('p.hinweis', { text: k.hinweis }) : null,
    ];
  }

  const b = fall.bild;
  if (!b.konvergiert) return [wahlzeile(fall.wahl), el('p.hinweis', { text: b.hinweis })];
  return [
    wahlzeile(fall.wahl),
    zahlenzeile([
      ['N', mitEinheit(b.N, 1, 'kN')],
      ['M', mitEinheit(b.M, 1, 'kNm')],
      ['\\varepsilon_{m}', mitEinheit(b.eps_m, 3, '‰')],
      ['\\chi', mitEinheit(b.chi, 5, '1/m')],
      ['x', b.nulllinie === null ? '–' : mitEinheit(b.nulllinie, 0, 'mm')],
    ]),
    verteilungsbild(b),
    b.hinweis ? el('p.hinweis', { text: b.hinweis }) : null,
  ];
}

/** Ein Fall als Karte: Name und Frage im Kopf, darunter Zahlen und Diagramm. */
export function spannungsfallZeichnen(fall) {
  const titel = fall.moeglich
    ? `${fall.name} – ${fall.titel} (${fall.richtung_text})`
    : `${fall.name} – ${fall.titel}`;
  return karte(titel, inhalt(fall));
}
