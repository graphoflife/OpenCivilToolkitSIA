/**
 * diagramm.js -- M-N-Interaktionsdiagramm als SVG.
 *
 * Zeichnet die vom Rechenkern gelieferte Resistenzlinie und trägt die
 * Bemessungspunkte ein. Zu jedem Punkt wird die Strecke zum massgebenden
 * Punkt der Linie gezeigt -- also genau der Weg, in dem der Erfüllungsgrad
 * gemessen wurde. Bei "Normalkraft konstant" ist das eine Waagrechte, bei
 * "Moment konstant" eine Senkrechte, beim kürzesten Abstand die Schräge.
 *
 * Es wird nichts nachgerechnet: sämtliche Koordinaten kommen aus der Lösung.
 */

import { el } from './dom.js';

const NR = 'http://www.w3.org/2000/svg';
const BREITE = 720;
const HOEHE = 520;
const RAND = { oben: 22, rechts: 22, unten: 46, links: 74 };

/** Farbe des vereinfachten Verlaufs -- grün, wie verlangt. */
const GRUEN = '#16794a';

/** Die genaue Resistenzlinie: zurückhaltend, sie ist nur Vergleich. */
const GENAU = '#8895a8';

function svgEl(name, attribute = {}) {
  const knoten = document.createElementNS(NR, name);
  for (const [k, v] of Object.entries(attribute)) {
    if (v !== null && v !== undefined) knoten.setAttribute(k, String(v));
  }
  return knoten;
}

/**
 * Schiebt Beschriftungen so weit auseinander, dass sie sich nicht überdecken.
 *
 * Vier Bewehrungslagen liegen nahe beieinander, teils in derselben Höhe
 * (Grundbewehrung und Zulage) -- ohne Entzerrung liegen die Zettel übereinander
 * und sind unlesbar.
 *
 * Zuerst wird von oben nach unten aufgeschoben, danach, falls unten der Platz
 * ausgeht, alles gemeinsam so weit angehoben, wie es noch reicht. Damit bleibt
 * die Reihenfolge erhalten, und das ist wichtiger als die genaue Höhe: welche
 * Lage gemeint ist, zeigt ohnehin der Anschlussstrich.
 *
 * @param {Array<{soll: number}>} zettel  zu platzierende Beschriftungen
 * @param {number} abstand                kleinster Abstand in Bildpunkten
 */
export function beschriftungenEntzerren(zettel, abstand, oben, unten) {
  const sortiert = [...zettel].sort((a, b) => a.soll - b.soll);

  let letzte = -Infinity;
  for (const z of sortiert) {
    z.y = Math.max(z.soll, letzte + abstand, oben);
    letzte = z.y;
  }

  const ueberstand = letzte - unten;
  if (ueberstand > 0) {
    // Nach oben zurückschieben, aber nur so weit, wie oben Platz bleibt.
    const luft = sortiert[0].y - oben;
    const schub = Math.min(ueberstand, Math.max(luft, 0));
    for (const z of sortiert) z.y -= schub;
  }
  return sortiert;
}

/**
 * Wo die Stäbe eines Postens über die Breite liegen, in Millimetern.
 *
 * Gezeichnet wird die **echte Teilung**: der Abstand zwischen zwei Stäben im
 * Bild ist derselbe, der eingegeben wurde. Eine Zulage mit ⌀12@250 steht damit
 * sichtbar weiter auseinander als eine Grundbewehrung mit ⌀16@150.
 *
 * Das war einmal anders gelöst -- die Stäbe wurden gleichmässig über `b`
 * verteilt. Dann sahen 150 und 140 gleich aus, weil beide auf dieselbe Stabzahl
 * führten und die Zeichnung nur die Zahl kannte, nicht den Abstand.
 *
 * Die Reihe wird in der Breite mittig gesetzt, damit sie nicht einseitig
 * ausfranst, wenn die Teilung nicht glatt aufgeht.
 *
 * `zwischen` setzt die Reihe in die Lücken der anderen: einen Stab weniger,
 * dadurch rückt sie um eine halbe Teilung ein. So wird die Zulage auch wirklich
 * eingelegt. Der Preis ist ein gezeichneter Stab weniger als `b / s` -- in
 * einem Schnittbild ist das verschmerzbar, und die genaue Menge steht ohnehin
 * als Text daneben.
 */
export function stabstellen(breite, bewehrung) {
  const teilung = bewehrung.abstand > 0
    ? bewehrung.abstand
    : breite / Math.max(1, Math.round(bewehrung.anzahl || 0));
  if (!(teilung > 0) || !Number.isFinite(teilung)) return [];

  const anzahl = Math.max(1, Math.round(breite / teilung));
  const spanne = (anzahl - 1) * teilung;
  const anfang = (breite - spanne) / 2;
  return Array.from({ length: anzahl }, (_, i) => anfang + i * teilung);
}

/**
 * Verschiebt eine ganze Stabreihe so, dass sie den vorhandenen am besten ausweicht.
 *
 * Die Reihe wird **als Ganzes** gerückt, nie einzelne Stäbe. Das ist der
 * Unterschied, auf den es ankommt: einzeln zu rücken hielte zwar alle Kreise
 * auseinander, verböge aber die Teilung -- eine Zulage mit ⌀12@250 sähe dann
 * aus wie ⌀12@267. Die Teilung ist aber genau das, was man im Bild ablesen
 * können soll.
 *
 * Gesucht wird der Versatz mit dem grössten Abstand zum nächsten vorhandenen
 * Stab, innerhalb dessen, was der Rand hergibt. Bei gleicher Teilung kommt
 * dabei von selbst die halbe Teilung heraus -- die Zulage landet in den Lücken,
 * so wie sie auch eingelegt wird.
 *
 * @param {number[]} stellen      Sollstellen der neuen Reihe, in mm
 * @param {number[]} vorhanden    Stellen der schon gezeichneten Reihen, in mm
 * @param {number}   spielraum    wie weit die Reihe höchstens rücken darf, in mm
 */
export function besterVersatz(stellen, vorhanden, spielraum, schritte = 48) {
  if (!stellen.length || !vorhanden.length || spielraum <= 0) return 0;

  const abstandBei = (versatz) => Math.min(...stellen.map((s) =>
    Math.min(...vorhanden.map((v) => Math.abs(s + versatz - v)))));

  let bester = 0;
  let weiteste = abstandBei(0);
  for (let i = 1; i <= schritte; i++) {
    for (const richtung of [1, -1]) {
      const versatz = richtung * spielraum * (i / schritte);
      const abstand = abstandBei(versatz);
      if (abstand > weiteste + 1e-9) {
        weiteste = abstand;
        bester = versatz;
      }
    }
  }
  return bester;
}

/**
 * Wie weit eine Reihe rücken darf, ohne aus dem Querschnitt zu laufen.
 *
 * Höchstens eine halbe Teilung -- weiter zu rücken brächte nichts, weil sich
 * das Bild dann wiederholt.
 */
export function spielraum(breite, stellen, randabstand) {
  if (stellen.length === 0) return 0;
  const links = stellen[0] - randabstand;
  const rechts = breite - randabstand - stellen[stellen.length - 1];
  const halbeTeilung = stellen.length > 1
    ? (stellen[1] - stellen[0]) / 2
    : breite / 2;
  return Math.max(0, Math.min(links, rechts, halbeTeilung));
}

/** Sucht einen runden Schrittabstand für die Achsenteilung. */
function schrittweite(spanne, zielAnzahl = 8) {
  const roh = spanne / zielAnzahl;
  const groesse = 10 ** Math.floor(Math.log10(Math.abs(roh) || 1));
  const rest = roh / groesse;
  const gewaehlt = rest >= 5 ? 10 : rest >= 2 ? 5 : rest >= 1 ? 2 : 1;
  return gewaehlt * groesse;
}

/**
 * Zeichnet den Plattenquerschnitt mit seinen vier Bewehrungslagen.
 *
 * Gezeigt wird ein Schnitt senkrecht zur x-Achse: Stäbe in x-Richtung sind
 * angeschnitten (Kreise), Stäbe in y-Richtung laufen in der Schnittebene
 * (Balken). Sämtliche Höhenlagen stammen aus der Lösung -- hier wird nichts
 * nachgerechnet.
 */
export function querschnittZeichnen(eintrag, werte) {
  const zahl = (id) => (werte[id] ? werte[id].zahl : null);
  const h = zahl(eintrag.werte.h);
  const b = zahl(eintrag.werte.b);
  if (!h || !b) return el('div.leer', { text: 'Geometrie noch nicht gerechnet.' });

  const BREITE = 660;
  const RAND = { oben: 26, unten: 40, links: 62, rechts: 168 };
  const zeichenBreite = BREITE - RAND.links - RAND.rechts;
  // Massstab so, dass die Platte gut sichtbar bleibt, ohne die Höhe zu verzerren.
  const massstab = zeichenBreite / b;
  const zeichenHoehe = h * massstab;
  const HOEHE = zeichenHoehe + RAND.oben + RAND.unten;

  const x = (mm) => RAND.links + mm * massstab;
  const y = (mm) => RAND.oben + mm * massstab;

  const svg = svgEl('svg', {
    class: 'qs', viewBox: `0 0 ${BREITE} ${HOEHE}`, xmlns: NR,
    role: 'img', 'aria-label': 'Plattenquerschnitt',
  });

  svg.append(svgEl('rect', {
    x: x(0), y: y(0), width: b * massstab, height: zeichenHoehe,
    fill: '#eceff4', stroke: '#7b8794', 'stroke-width': 1.6,
  }));

  const farbe = { x: '#1f6feb', y: '#b8622a' };
  const zettel = [];
  // Schon gezeichnete Stäbe, in Millimetern -- damit die nächste Reihe weiss,
  // wem sie ausweichen muss.
  const gesetzt = [];

  // Zwei Durchgänge: erst die längs laufenden y-Stäbe, dann die angeschnittenen
  // x-Stäbe darüber. So bleiben die Kreise sichtbar, ohne dass die y-Stäbe
  // durchscheinend gezeichnet werden müssten -- halbdurchsichtig liess sich
  // ihre Dicke nicht mehr ablesen.
  const laengs = eintrag.bewehrung.filter((bew) => bew.richtung === 'y');
  const quer = eintrag.bewehrung.filter((bew) => bew.richtung !== 'y');

  for (const bew of laengs) {
    const z = zahl(bew.z_id);
    if (z === null) continue;
    const dicke = (bew.phi || 12) * massstab;
    // Als Rechteck und nicht als Linie mit runden Enden: die Kappen ragten um
    // einen halben Durchmesser über den Beton hinaus, und genau so weit war
    // der Stab dann zu lang.
    svg.append(svgEl('rect', {
      x: x(0), y: y(z) - dicke / 2, width: b * massstab, height: Math.max(dicke, 1.6),
      fill: farbe.y, opacity: bew.art === 'zulage' ? 0.6 : 0.85,
    }));
    zettel.push({
      soll: y(z), anker: y(z), farbe: farbe.y,
      text: `${bew.lage}. ${bew.art === 'grund' ? 'Grund' : 'Zulage'} `
          + `${bew.menge} (${bew.richtung})`,
    });
  }

  for (const bew of quer) {
    const z = zahl(bew.z_id);
    if (z === null) continue;
    const r = Math.max((bew.phi || 12) * massstab / 2, 1.4);
    const stellen = stabstellen(b, bew);
    // Nur Stäbe auf praktisch gleicher Höhe kommen sich ins Gehege.
    const hindernisse = gesetzt
      .filter((g) => Math.abs(g.y - y(z)) < g.r + r)
      .map((g) => g.mm);
    const versatz = besterVersatz(
      stellen, hindernisse, spielraum(b, stellen, (bew.phi || 12) / 2));

    for (const mm of stellen) {
      const stelle = mm + versatz;
      gesetzt.push({ mm: stelle, y: y(z), r });
      svg.append(svgEl('circle', {
        cx: x(stelle), cy: y(z), r,
        fill: farbe.x, stroke: '#fff', 'stroke-width': 0.6,
        opacity: bew.art === 'zulage' ? 0.75 : 1,
      }));
    }
    zettel.push({
      soll: y(z), anker: y(z), farbe: farbe.x,
      text: `${bew.lage}. ${bew.art === 'grund' ? 'Grund' : 'Zulage'} `
          + `${bew.menge} (${bew.richtung})`,
    });
  }

  for (const z of beschriftungenEntzerren(zettel, 13, RAND.oben, HOEHE - RAND.unten)) {
    const links = BREITE - RAND.rechts + 10;
    // Hat der Zettel ausweichen müssen, zeigt ein Strich auf die wahre Höhe --
    // sonst stünde die Beschriftung auf einer Lage, zu der sie nicht gehört.
    if (Math.abs(z.y - z.anker) > 0.5) {
      svg.append(svgEl('polyline', {
        points: `${x(b) + 3},${z.anker} ${links - 6},${z.anker} `
              + `${links - 3},${z.y} ${links - 1},${z.y}`,
        fill: 'none', stroke: z.farbe, 'stroke-width': 0.8, opacity: 0.5,
      }));
    }
    const beschriftung = svgEl('text', {
      x: links, y: z.y + 3.5, 'font-size': 10.5, fill: z.farbe,
    });
    beschriftung.textContent = z.text;
    svg.append(beschriftung);
  }

  // Höhenmass links
  svg.append(svgEl('line', {
    x1: RAND.links - 16, y1: y(0), x2: RAND.links - 16, y2: y(h),
    stroke: '#56657a', 'stroke-width': 1,
  }));
  for (const [wert, text] of [[0, 'OK'], [h, 'UK']]) {
    svg.append(svgEl('line', {
      x1: RAND.links - 21, y1: y(wert), x2: RAND.links - 11, y2: y(wert),
      stroke: '#56657a', 'stroke-width': 1,
    }));
    const m = svgEl('text', {
      x: RAND.links - 25, y: y(wert) + 4, 'text-anchor': 'end',
      'font-size': 10.5, fill: '#56657a',
    });
    m.textContent = text;
    svg.append(m);
  }
  const masstext = svgEl('text', {
    x: 14, y: RAND.oben + zeichenHoehe / 2, 'font-size': 11, fill: '#16202c',
    'font-weight': 600, 'text-anchor': 'middle',
    transform: `rotate(-90 14 ${RAND.oben + zeichenHoehe / 2})`,
  });
  masstext.textContent = `h = ${h.toFixed(0)} mm`;
  svg.append(masstext);

  const breitentext = svgEl('text', {
    x: RAND.links + (b * massstab) / 2, y: HOEHE - 12,
    'text-anchor': 'middle', 'font-size': 11, fill: '#16202c', 'font-weight': 600,
  });
  breitentext.textContent = `b = ${b.toFixed(0)} mm`;
  svg.append(breitentext);

  return el('div.diagramm-huelle', {}, [
    svg,
    el('div.mn-legende', {}, [
      el('span', {}, [el('i', { style: { background: farbe.x } }), 'x-Richtung (angeschnitten)']),
      el('span', {}, [el('i', {
        style: { background: farbe.y, borderRadius: '1px', height: '3px', opacity: '.7' },
      }), 'y-Richtung (durchgezogen, in der Schnittebene)']),
      el('span', { text: 'blasser = Zulage' }),
    ]),
  ]);
}

export function diagrammZeichnen(linie) {
  const punkte = linie.punkte;
  const hand = linie.handpunkte || [];
  if (!punkte?.length) return el('div.leer', { text: 'Keine Resistenzlinie vorhanden.' });

  const alleM = [...punkte, ...hand].map((p) => p.M);
  const alleN = [...punkte, ...hand].map((p) => p.N);
  for (const k of linie.kombinationen) { alleM.push(k.M_Ed); alleN.push(k.N_Ed); }

  const spielraum = 0.08;
  const mSpanne = (Math.max(...alleM) - Math.min(...alleM)) || 1;
  const nSpanne = (Math.max(...alleN) - Math.min(...alleN)) || 1;
  const mMin = Math.min(...alleM) - mSpanne * spielraum;
  const mMax = Math.max(...alleM) + mSpanne * spielraum;
  const nMin = Math.min(...alleN) - nSpanne * spielraum;
  const nMax = Math.max(...alleN) + nSpanne * spielraum;

  const zeichenBreite = BREITE - RAND.links - RAND.rechts;
  const zeichenHoehe = HOEHE - RAND.oben - RAND.unten;
  const x = (m) => RAND.links + ((m - mMin) / (mMax - mMin)) * zeichenBreite;
  const y = (n) => RAND.oben + (1 - (n - nMin) / (nMax - nMin)) * zeichenHoehe;

  const svg = svgEl('svg', {
    class: 'mn', viewBox: `0 0 ${BREITE} ${HOEHE}`,
    xmlns: NR, role: 'img',
    'aria-label': 'M-N-Interaktionsdiagramm',
  });

  // -- Gitter und Achsen --------------------------------------------------
  const gitter = svgEl('g');
  const mSchritt = schrittweite(mMax - mMin);
  const nSchritt = schrittweite(nMax - nMin);

  for (let m = Math.ceil(mMin / mSchritt) * mSchritt; m <= mMax; m += mSchritt) {
    gitter.append(svgEl('line', {
      x1: x(m), y1: RAND.oben, x2: x(m), y2: HOEHE - RAND.unten,
      stroke: '#e6e9ee', 'stroke-width': 1,
    }));
    const beschriftung = svgEl('text', {
      x: x(m), y: HOEHE - RAND.unten + 16, 'text-anchor': 'middle',
      'font-size': 11, fill: '#5c6773',
    });
    beschriftung.textContent = Math.round(m);
    gitter.append(beschriftung);
  }
  for (let n = Math.ceil(nMin / nSchritt) * nSchritt; n <= nMax; n += nSchritt) {
    gitter.append(svgEl('line', {
      x1: RAND.links, y1: y(n), x2: BREITE - RAND.rechts, y2: y(n),
      stroke: '#e6e9ee', 'stroke-width': 1,
    }));
    const beschriftung = svgEl('text', {
      x: RAND.links - 8, y: y(n) + 4, 'text-anchor': 'end',
      'font-size': 11, fill: '#5c6773',
    });
    beschriftung.textContent = Math.round(n);
    gitter.append(beschriftung);
  }
  svg.append(gitter);

  // Nulllinien kräftiger, damit Zug und Druck auf einen Blick trennbar sind.
  if (nMin < 0 && nMax > 0) {
    svg.append(svgEl('line', {
      x1: RAND.links, y1: y(0), x2: BREITE - RAND.rechts, y2: y(0),
      stroke: '#b8c0cc', 'stroke-width': 1.5,
    }));
  }
  if (mMin < 0 && mMax > 0) {
    svg.append(svgEl('line', {
      x1: x(0), y1: RAND.oben, x2: x(0), y2: HOEHE - RAND.unten,
      stroke: '#b8c0cc', 'stroke-width': 1.5,
    }));
  }

  // -- Die beiden Resistenzlinien ------------------------------------------
  // Die genaue Linie ist nur Vergleich: dünn, ohne Füllung. Gefüllt und kräftig
  // ist das Polygon aus der Handrechnung -- das ist die Linie, gegen die
  // nachgewiesen wird, und sie soll den Blick auf sich ziehen.
  svg.append(svgEl('polygon', {
    points: punkte.map((p) => `${x(p.M).toFixed(2)},${y(p.N).toFixed(2)}`).join(' '),
    fill: 'none', stroke: GENAU, 'stroke-width': 1.3,
    'stroke-dasharray': '6 3', 'stroke-linejoin': 'round', opacity: 0.8,
  }));

  if (hand.length) {
    svg.append(svgEl('polygon', {
      points: hand.map((p) => `${x(p.M).toFixed(2)},${y(p.N).toFixed(2)}`).join(' '),
      fill: 'rgba(31,95,168,.07)', stroke: '#1f5fa8', 'stroke-width': 2,
      'stroke-linejoin': 'round',
    }));
    for (const p of hand) {
      const ecke = svgEl('circle', {
        cx: x(p.M), cy: y(p.N), r: 3, fill: '#1f5fa8',
        stroke: '#fff', 'stroke-width': 1.2,
      });
      const t = svgEl('title');
      t.textContent = `${p.name}\nM = ${p.M.toFixed(1)} kNm, N = ${p.N.toFixed(1)} kN`;
      ecke.append(t);
      svg.append(ecke);
    }
  }

  // -- Bemessungspunkte ----------------------------------------------------
  for (const k of linie.kombinationen) {
    const farbe = k.innerhalb ? '#1a7f45' : '#b3261e';

    if (k.widerstand) {
      svg.append(svgEl('line', {
        x1: x(k.M_Ed), y1: y(k.N_Ed), x2: x(k.widerstand.M), y2: y(k.widerstand.N),
        stroke: farbe, 'stroke-width': 1.4, 'stroke-dasharray': '5 3', opacity: .75,
      }));
      svg.append(svgEl('circle', {
        cx: x(k.widerstand.M), cy: y(k.widerstand.N), r: 3.5,
        fill: '#fff', stroke: farbe, 'stroke-width': 1.6,
      }));
    }

    const punkt = svgEl('circle', {
      cx: x(k.M_Ed), cy: y(k.N_Ed), r: 6,
      fill: farbe, stroke: '#fff', 'stroke-width': 2,
    });
    const titel = svgEl('title');
    const grad = Number.isFinite(k.erfuellungsgrad) ? k.erfuellungsgrad.toFixed(3) : '∞';
    titel.textContent =
      `${k.name}\nM_Ed = ${k.M_Ed.toFixed(1)} kNm, N_Ed = ${k.N_Ed.toFixed(1)} kN`
      + `\nErfüllungsgrad α_eff = ${grad} (${k.massstab_text})`
      + `\n${k.innerhalb ? 'erfüllt' : 'NICHT erfüllt'}`;
    punkt.append(titel);
    svg.append(punkt);

    const beschriftung = svgEl('text', {
      x: x(k.M_Ed) + 9, y: y(k.N_Ed) - 8,
      'font-size': 11, 'font-weight': 600, fill: farbe,
    });
    beschriftung.textContent = k.name;
    svg.append(beschriftung);
  }

  // -- Achsenbeschriftung --------------------------------------------------
  const xTitel = svgEl('text', {
    x: RAND.links + zeichenBreite / 2, y: HOEHE - 8,
    'text-anchor': 'middle', 'font-size': 12, fill: '#1a1f27', 'font-weight': 600,
  });
  xTitel.textContent = 'M [kNm]';
  svg.append(xTitel);

  const yTitel = svgEl('text', {
    x: 16, y: RAND.oben + zeichenHoehe / 2,
    'text-anchor': 'middle', 'font-size': 12, fill: '#1a1f27', 'font-weight': 600,
    transform: `rotate(-90 16 ${RAND.oben + zeichenHoehe / 2})`,
  });
  yTitel.textContent = 'N [kN]   (Zug positiv)';
  svg.append(yTitel);

  return el('div.diagramm-huelle', {}, [
    svg,
    el('div.mn-legende', {}, [
      el('span', {}, [el('i', { style: { background: '#1f5fa8' } }),
        'Resistenzlinie aus Handrechnung (massgebend)']),
      el('span', {}, [el('i', {
        style: { background: GENAU, height: '3px', borderRadius: '1px' },
      }), 'Präzise Resistenzlinie (nur Vergleich)']),
      el('span', {}, [el('i', { style: { background: '#1a7f45' } }), 'erfüllt']),
      el('span', {}, [el('i', { style: { background: '#b3261e' } }), 'nicht erfüllt']),
      el('span', { text: '– – –  gemessener Weg zur Linie' }),
    ]),
  ]);
}

/**
 * Zeichnet eine Spannungs-Dehnungs-Beziehung.
 *
 * Die Punktfolge kommt fertig aus dem Rechenkern und stammt aus demselben
 * Werkstoffgesetz, das auch die Querschnittsintegration verwendet -- die Kurve
 * zeigt also, womit tatsächlich gerechnet wurde, und nicht eine nachgebaute
 * Fassung.
 *
 * Vorzeichen wie überall: Zug positiv. Der Beton liegt damit im dritten
 * Quadranten, der Stahl spannt sich über beide. Die Achsen laufen deshalb
 * durch den Nullpunkt.
 */
export function kurveZeichnen(gesetz, { zeigeVereinfacht = true, beiUmschalten } = {}) {
  const punkte = gesetz.punkte || [];
  if (!punkte.length) return el('div.leer', { text: 'Keine Kurve vorhanden.' });

  const BREITE = 560;
  const HOEHE = 360;
  const RAND = { oben: 18, rechts: 22, unten: 40, links: 68 };
  const zBreite = BREITE - RAND.links - RAND.rechts;
  const zHoehe = HOEHE - RAND.oben - RAND.unten;

  const eps = punkte.map((p) => p.eps);
  const sig = punkte.map((p) => p.sigma);
  // Der Nullpunkt gehört immer ins Bild, sonst hängt die Kurve im Nichts.
  const spanne = (werte, luft = 0.08) => {
    const min = Math.min(0, ...werte);
    const max = Math.max(0, ...werte);
    const d = (max - min) || 1;
    return [min - d * luft, max + d * luft];
  };
  const [xMin, xMax] = spanne(eps);
  const [yMin, yMax] = spanne(sig);

  const x = (v) => RAND.links + ((v - xMin) / (xMax - xMin)) * zBreite;
  const y = (v) => RAND.oben + (1 - (v - yMin) / (yMax - yMin)) * zHoehe;

  const svg = svgEl('svg', {
    class: 'mn', viewBox: `0 0 ${BREITE} ${HOEHE}`, xmlns: NR,
    role: 'img', 'aria-label': gesetz.titel,
  });

  // Gitter
  const xs = schrittweite(xMax - xMin, 6);
  const ys = schrittweite(yMax - yMin, 6);
  for (let v = Math.ceil(xMin / xs) * xs; v <= xMax; v += xs) {
    svg.append(svgEl('line', {
      x1: x(v), y1: RAND.oben, x2: x(v), y2: HOEHE - RAND.unten,
      stroke: '#e6e9ee', 'stroke-width': 1,
    }));
    const t = svgEl('text', {
      x: x(v), y: HOEHE - RAND.unten + 15, 'text-anchor': 'middle',
      'font-size': 10.5, fill: '#5c6773',
    });
    t.textContent = Number(v.toFixed(2));
    svg.append(t);
  }
  for (let v = Math.ceil(yMin / ys) * ys; v <= yMax; v += ys) {
    svg.append(svgEl('line', {
      x1: RAND.links, y1: y(v), x2: BREITE - RAND.rechts, y2: y(v),
      stroke: '#e6e9ee', 'stroke-width': 1,
    }));
    const t = svgEl('text', {
      x: RAND.links - 7, y: y(v) + 4, 'text-anchor': 'end',
      'font-size': 10.5, fill: '#5c6773',
    });
    t.textContent = Math.round(v);
    svg.append(t);
  }

  // Nullachsen
  for (const [a, b, c, d] of [
    [RAND.links, y(0), BREITE - RAND.rechts, y(0)],
    [x(0), RAND.oben, x(0), HOEHE - RAND.unten],
  ]) {
    svg.append(svgEl('line', {
      x1: a, y1: b, x2: c, y2: d, stroke: '#b4becd', 'stroke-width': 1.4,
    }));
  }

  // Kurve
  svg.append(svgEl('polyline', {
    points: punkte.map((p) => `${x(p.eps).toFixed(2)},${y(p.sigma).toFixed(2)}`).join(' '),
    fill: 'none', stroke: '#1f6feb', 'stroke-width': 2.2,
    'stroke-linejoin': 'round', 'stroke-linecap': 'round',
  }));

  // Vereinfachter Verlauf (Spannungsblock), sofern der Kern einen liefert.
  if (gesetz.vereinfacht && zeigeVereinfacht) {
    svg.append(svgEl('polyline', {
      points: gesetz.vereinfacht.punkte
        .map((p) => `${x(p.eps).toFixed(2)},${y(p.sigma).toFixed(2)}`).join(' '),
      fill: 'none', stroke: GRUEN, 'stroke-width': 2,
      'stroke-linejoin': 'miter', 'stroke-linecap': 'butt',
    }));
  }

  // Marken für die Grenzdehnungen
  for (const marke of gesetz.marken || []) {
    svg.append(svgEl('line', {
      x1: x(marke.eps), y1: y(0), x2: x(marke.eps), y2: y(marke.sigma),
      stroke: '#8895a8', 'stroke-width': 1, 'stroke-dasharray': '3 3',
    }));
    svg.append(svgEl('circle', {
      cx: x(marke.eps), cy: y(marke.sigma), r: 3.2,
      fill: '#fff', stroke: '#1f6feb', 'stroke-width': 1.6,
    }));
    const t = svgEl('text', {
      x: x(marke.eps), y: y(marke.sigma) + (marke.sigma < 0 ? 15 : -8),
      'text-anchor': 'middle', 'font-size': 10.5, fill: '#0d4ba8', 'font-weight': 600,
    });
    t.textContent = marke.text;
    svg.append(t);
  }

  // Achsenbeschriftung
  const xt = svgEl('text', {
    x: RAND.links + zBreite / 2, y: HOEHE - 6, 'text-anchor': 'middle',
    'font-size': 11.5, fill: '#16202c', 'font-weight': 600,
  });
  xt.textContent = gesetz.x_titel;
  svg.append(xt);

  const yt = svgEl('text', {
    x: 14, y: RAND.oben + zHoehe / 2, 'text-anchor': 'middle',
    'font-size': 11.5, fill: '#16202c', 'font-weight': 600,
    transform: `rotate(-90 14 ${RAND.oben + zHoehe / 2})`,
  });
  yt.textContent = gesetz.y_titel;
  svg.append(yt);

  if (!gesetz.vereinfacht) return el('div.diagramm-huelle', {}, [svg]);

  const schalter = el('label.kurvenschalter', {
    title: gesetz.vereinfacht.beschreibung || '',
  }, [
    el('input', {
      type: 'checkbox',
      checked: zeigeVereinfacht,
      on: { change: (e) => beiUmschalten?.(e.target.checked) },
    }),
    el('i', { style: { background: GRUEN } }),
    el('span', { text: gesetz.vereinfacht.titel }),
  ]);

  return el('div.diagramm-huelle', {}, [
    svg,
    el('div.mn-legende', {}, [
      el('span', {}, [el('i', { style: { background: '#1f6feb' } }), gesetz.titel]),
      schalter,
      zeigeVereinfacht && gesetz.vereinfacht.beschreibung
        ? el('span', {
          text: gesetz.vereinfacht.beschreibung,
          style: { color: 'var(--schrift-zart)' },
        })
        : null,
    ]),
  ]);
}

/**
 * Zeichnet den Querkraftwiderstand über dem Moment.
 *
 * Der Widerstand hängt über ε_v vom Moment ab und über m_Rd(N_Ed) von der
 * Normalkraft. Die Kurve zeigt den ersten Zusammenhang; die zweite Grösse wird
 * festgehalten und ist unter dem Diagramm einstellbar.
 *
 * JENSEITS VON m_Rd:
 * Die Kurve läuft 20 kNm über den Momentenwiderstand hinaus. Dort fliesst die
 * Bewehrung, ε_v wächst sprunghaft und der Widerstand fällt -- genau das ist
 * der Grund, überhaupt so weit zu zeichnen.
 *
 * AUSGEGRAUT:
 * Ein Bemessungspunkt gehört nur dann auf diese Kurve, wenn seine Normalkraft
 * die eingestellte ist. Sonst läge er dort, wo er nicht hingehört. Statt ihn
 * wegzulassen, wird er blass gezeichnet -- er ist ja vorhanden, nur eben zu
 * einer anderen Kurve.
 *
 * Gerechnet wird nichts: die Punkte kommen aus dem Kern, aus derselben
 * Funktion wie der Nachweis.
 */
export function querkraftkurveZeichnen(kurve) {
  const punkte = kurve.punkte || [];
  if (!punkte.length) {
    return el('div.leer', {
      text: 'Bei dieser Normalkraft besteht kein Momentenwiderstand – '
          + 'die Kurve lässt sich nicht bilden.',
    });
  }

  const passt = (fall) => Math.abs(fall.N_Ed - kurve.N_Ed) < 1e-6;
  const faelle = kurve.faelle || [];

  const alleM = [0, ...punkte.map((p) => p.M_Ed), ...faelle.map((f) => f.M_Ed)];
  const alleV = [0, ...punkte.map((p) => p.v_Rd), ...faelle.map((f) => f.V_Ed)];
  const mMax = Math.max(...alleM) * 1.04;
  const vMax = Math.max(...alleV) * 1.10;

  const zeichenBreite = BREITE - RAND.links - RAND.rechts;
  const zeichenHoehe = HOEHE - RAND.oben - RAND.unten;
  const x = (m) => RAND.links + (m / mMax) * zeichenBreite;
  const y = (v) => RAND.oben + (1 - v / vMax) * zeichenHoehe;

  const svg = svgEl('svg', {
    class: 'mv', viewBox: `0 0 ${BREITE} ${HOEHE}`, xmlns: NR, role: 'img',
    'aria-label': 'Querkraftwiderstand über dem Moment',
  });

  // -- Gitter --------------------------------------------------------------
  const gitter = svgEl('g');
  const mSchritt = schrittweite(mMax);
  const vSchritt = schrittweite(vMax);
  for (let m = 0; m <= mMax; m += mSchritt) {
    gitter.append(svgEl('line', {
      x1: x(m), y1: RAND.oben, x2: x(m), y2: HOEHE - RAND.unten,
      stroke: '#e6e9ee', 'stroke-width': 1,
    }));
    const t = svgEl('text', {
      x: x(m), y: HOEHE - RAND.unten + 16, 'text-anchor': 'middle',
      'font-size': 11, fill: '#5c6773',
    });
    t.textContent = Math.round(m);
    gitter.append(t);
  }
  for (let v = 0; v <= vMax; v += vSchritt) {
    gitter.append(svgEl('line', {
      x1: RAND.links, y1: y(v), x2: BREITE - RAND.rechts, y2: y(v),
      stroke: '#e6e9ee', 'stroke-width': 1,
    }));
    const t = svgEl('text', {
      x: RAND.links - 8, y: y(v) + 4, 'text-anchor': 'end',
      'font-size': 11, fill: '#5c6773',
    });
    t.textContent = Math.round(v);
    gitter.append(t);
  }
  svg.append(gitter);

  // -- m_Rd als senkrechte Marke ------------------------------------------
  if (kurve.m_Rd) {
    svg.append(svgEl('line', {
      x1: x(kurve.m_Rd), y1: RAND.oben, x2: x(kurve.m_Rd), y2: HOEHE - RAND.unten,
      stroke: '#1f5fa8', 'stroke-width': 1.4, 'stroke-dasharray': '4 4', opacity: .7,
    }));
    const marke = svgEl('text', {
      x: x(kurve.m_Rd) - 6, y: RAND.oben + 13, 'text-anchor': 'end',
      'font-size': 11, 'font-weight': 600, fill: '#1f5fa8',
    });
    marke.textContent = `m_Rd = ${kurve.m_Rd.toFixed(1)}`;
    svg.append(marke);
  }

  // -- Die Kurve -----------------------------------------------------------
  // Zwei Züge: bis m_Rd durchgezogen, darüber -- wo die Bewehrung fliesst --
  // gestrichelt. Der Sprung dazwischen ist die Aussage des Diagramms.
  const zug = (auswahl, gestrichelt) => {
    const teil = punkte.filter(auswahl);
    if (teil.length < 2) return;
    svg.append(svgEl('polyline', {
      points: teil.map((p) => `${x(p.M_Ed).toFixed(2)},${y(p.v_Rd).toFixed(2)}`).join(' '),
      fill: 'none', stroke: '#1f5fa8', 'stroke-width': 2.2,
      'stroke-linejoin': 'round', 'stroke-dasharray': gestrichelt ? '7 4' : null,
    }));
  };
  zug((p) => !p.plastisch, false);
  zug((p) => p.plastisch, true);

  // -- Die drei Marken -----------------------------------------------------
  // Der Höchstwert (Moment null), der letzte Wert vor dem Fliessen und die
  // Waagrechte danach. Die beiden letzten stehen beieinander und benennen den
  // Sprung, um den es hier geht.
  const elastisch = punkte.filter((p) => !p.plastisch);
  const plastisch = punkte.filter((p) => p.plastisch);
  const marken = [
    [punkte.reduce((a, b) => (b.v_Rd > a.v_Rd ? b : a)), 'max v_Rd', true],
    [elastisch.at(-1), 'v_Rd bei M_Ed = m_Rd', true],
    [plastisch[0], 'v_Rd nach Fliessbeginn', false],
  ];
  for (const [p, name, oben] of marken) {
    if (!p) continue;
    svg.append(svgEl('circle', {
      cx: x(p.M_Ed), cy: y(p.v_Rd), r: 4,
      fill: '#fff', stroke: '#1f5fa8', 'stroke-width': 2,
    }));
    const rechts = x(p.M_Ed) > BREITE * 0.62;
    const t = svgEl('text', {
      x: x(p.M_Ed) + (rechts ? -8 : 8),
      y: y(p.v_Rd) + (oben ? -9 : 17),
      'text-anchor': rechts ? 'end' : 'start',
      'font-size': 11, 'font-weight': 600, fill: '#1f5fa8',
    });
    t.textContent = `${name} = ${p.v_Rd.toFixed(1)} kN/m`;
    svg.append(t);
  }

  // -- Bemessungspunkte ----------------------------------------------------
  for (const f of faelle) {
    const gilt = passt(f);
    const farbe = f.erfuellt ? '#1a7f45' : '#b3261e';
    const deckung = gilt ? 1 : 0.28;

    // Senkrechte von der Einwirkung hinauf zum Widerstand auf der Kurve.
    svg.append(svgEl('line', {
      x1: x(f.M_Ed), y1: y(f.V_Ed), x2: x(f.M_Ed), y2: y(f.v_Rd),
      stroke: farbe, 'stroke-width': 1.4, 'stroke-dasharray': '5 3',
      opacity: 0.75 * deckung,
    }));
    svg.append(svgEl('circle', {
      cx: x(f.M_Ed), cy: y(f.v_Rd), r: 3.5,
      fill: '#fff', stroke: farbe, 'stroke-width': 1.6, opacity: deckung,
    }));

    const punkt = svgEl('circle', {
      cx: x(f.M_Ed), cy: y(f.V_Ed), r: 6,
      fill: farbe, stroke: '#fff', 'stroke-width': 2, opacity: deckung,
    });
    const titel = svgEl('title');
    titel.textContent =
      `${f.name}\nM_Ed = ${f.M_Ed.toFixed(1)} kNm, V_Ed = ${f.V_Ed.toFixed(1)} kN/m`
      + `\nN_Ed = ${f.N_Ed.toFixed(1)} kN, v_Rd = ${f.v_Rd.toFixed(1)} kN/m`
      + `\n${f.erfuellt ? 'erfüllt' : 'NICHT erfüllt'}`
      + (gilt ? '' : `\nGilt für N_Ed = ${f.N_Ed.toFixed(1)} kN, `
                   + `gezeigt ist ${kurve.N_Ed.toFixed(1)} kN.`);
    punkt.append(titel);
    svg.append(punkt);

    const beschriftung = svgEl('text', {
      x: x(f.M_Ed) + 9, y: y(f.V_Ed) + 16,
      'font-size': 11, 'font-weight': 600, fill: farbe, opacity: deckung,
    });
    beschriftung.textContent = f.name;
    svg.append(beschriftung);
  }

  // -- Achsenbeschriftung --------------------------------------------------
  const xTitel = svgEl('text', {
    x: RAND.links + zeichenBreite / 2, y: HOEHE - 8,
    'text-anchor': 'middle', 'font-size': 12, fill: '#1a1f27', 'font-weight': 600,
  });
  xTitel.textContent = 'M_Ed [kNm]   (Betrag)';
  svg.append(xTitel);

  const yTitel = svgEl('text', {
    x: 16, y: RAND.oben + zeichenHoehe / 2,
    'text-anchor': 'middle', 'font-size': 12, fill: '#1a1f27', 'font-weight': 600,
    transform: `rotate(-90 16 ${RAND.oben + zeichenHoehe / 2})`,
  });
  yTitel.textContent = 'v_Rd [kN/m]';
  svg.append(yTitel);

  return svg;
}
