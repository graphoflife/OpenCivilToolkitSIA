/**
 * zeichnen.js -- die Bilder aus der App «Python», gezeichnet wie die übrigen
 * Diagramme.
 *
 * Ein Skript beschreibt sein Bild mit `import zeichnen as plt` -- Reihen,
 * Achsen, Titel (`opencivil/konsole/zeichnen.py`). Hier wird daraus ein SVG
 * mit demselben Achsenkreuz wie überall (`achsen.js`): Linien, Punkte,
 * Balken, Hilfslinien, eine Legende und beim Darüberfahren der nächste Wert.
 *
 * Gerechnet wird nichts, was in eine Rechnung eingeht: nur der Bereich der
 * Achsen und wo ein Punkt im Bild liegt.
 */

import { achsenkreuz, schrittweite } from './achsen.js';
import { el, svgEl } from './dom.js';

const BREITE = 560;
const HOEHE = 340;

/** Die Farben der Reihen ohne eigene -- dieselbe Folge wie bei matplotlib. */
const FARBEN = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
  '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'];

const STRICHMUSTER = { '--': '6 4', ':': '1.5 3', '-.': '6 3 1.5 3' };

/** Zahlen für Achsen und Zettel: so viele Stellen, wie die Teilung braucht. */
function zahl(v, schritt) {
  const stellen = Math.max(0, Math.min(6, -Math.floor(Math.log10(Math.abs(schritt) || 1))));
  return v.toFixed(stellen).replace('-', '−');
}

/** Der Bereich einer Achse: was die Daten brauchen, mit etwas Luft -- oder was das Skript vorgibt. */
function bereich(werte, vorgabe, { mitNull = false } = {}) {
  const endliche = werte.filter((v) => v !== null && Number.isFinite(v));
  if (mitNull) endliche.push(0);
  let [a, b] = endliche.length ? [Math.min(...endliche), Math.max(...endliche)] : [0, 1];
  if (a === b) [a, b] = [a - (Math.abs(a) || 1) * 0.5, b + (Math.abs(b) || 1) * 0.5];
  const luft = (b - a) * 0.05;
  return [vorgabe?.[0] ?? a - luft, vorgabe?.[1] ?? b + luft];
}

/** Die Stücke einer Linie zwischen den Lücken -- je Stück eine Folge von Bildpunkten. */
function stuecke(reihe, x, y) {
  const heraus = [];
  let stueck = [];
  reihe.x.forEach((xi, i) => {
    const yi = reihe.y[i];
    if (xi === null || yi === null) {
      if (stueck.length) heraus.push(stueck);
      stueck = [];
    } else {
      stueck.push([x(xi), y(yi)]);
    }
  });
  if (stueck.length) heraus.push(stueck);
  return heraus;
}

function marke(art, [px, py], groesse, farbe) {
  const r = groesse / 2;
  if (art === 's') return svgEl('rect', { x: px - r, y: py - r, width: 2 * r, height: 2 * r, fill: farbe });
  if (art === '^') return svgEl('path', { d: `M${px} ${py - r}L${px + r} ${py + r}L${px - r} ${py + r}Z`, fill: farbe });
  if (art === 'D') return svgEl('path', { d: `M${px} ${py - r}L${px + r} ${py}L${px} ${py + r}L${px - r} ${py}Z`, fill: farbe });
  if (art === 'x') return svgEl('path', { d: `M${px - r} ${py - r}L${px + r} ${py + r}M${px - r} ${py + r}L${px + r} ${py - r}`, stroke: farbe, 'stroke-width': 1.6 });
  if (art === '+') return svgEl('path', { d: `M${px - r} ${py}H${px + r}M${px} ${py - r}V${py + r}`, stroke: farbe, 'stroke-width': 1.6 });
  return svgEl('circle', { cx: px, cy: py, r: art === '.' ? Math.max(1.5, r / 2.5) : r, fill: farbe });
}

/** Die Legende oben rechts im Feld: je Reihe mit Namen ein Strich in ihrer Farbe. */
function legende(reihen, feld) {
  const benannt = reihen.filter((r) => r.name);
  if (!benannt.length) return null;
  const zeilen = 16;
  const breite = 24 + Math.max(...benannt.map((r) => r.name.length)) * 6.6;
  const g = svgEl('g', { transform: `translate(${feld.rechts - breite - 8} ${feld.oben + 8})` });
  g.append(svgEl('rect', {
    width: breite, height: benannt.length * zeilen + 6, rx: 4,
    fill: 'rgba(255,255,255,.88)', stroke: '#d4d9e1',
  }));
  benannt.forEach((r, i) => {
    const mitte = 11 + i * zeilen;
    if (r.art === 'balken') {
      g.append(svgEl('rect', { x: 6, y: mitte - 4, width: 12, height: 8, fill: r.farbe }));
    } else {
      if (r.strich) {
        g.append(svgEl('line', {
          x1: 4, y1: mitte, x2: 20, y2: mitte, stroke: r.farbe, 'stroke-width': 2,
          'stroke-dasharray': STRICHMUSTER[r.strich] || null,
        }));
      }
      if (r.marke) g.append(marke(r.marke, [12, mitte], 6, r.farbe));
    }
    const text = svgEl('text', { x: 24, y: mitte + 4, 'font-size': 11, fill: '#1a1f27' });
    text.textContent = r.name;
    g.append(text);
  });
  return g;
}

/**
 * Ein Bild aus seiner Beschreibung -- als Knoten für die Konsole: Titel,
 * das SVG und ein Zettel, der beim Darüberfahren den nächsten Punkt nennt.
 */
export function bildZeichnen(bild) {
  // Jede Reihe mit ihrer Farbe -- die ohne eigene der Reihe nach.
  let naechste = 0;
  const reihen = bild.reihen.map((r) => ({ ...r, farbe: r.farbe || FARBEN[naechste++ % FARBEN.length] }));
  const balken = reihen.filter((r) => r.art === 'balken');

  const alleX = reihen.flatMap((r) => r.x);
  const alleY = reihen.flatMap((r) => r.y);
  for (const h of bild.hilfslinien) (h.achse === 'x' ? alleX : alleY).push(h.wert);
  // Balken stehen auf null und brauchen links und rechts ihre halbe Breite.
  const halbe = balken.length ? Math.max(...balken.map((r) => r.breite ?? 0.8)) / 2 : 0;
  const xb = bereich([...alleX, ...(halbe ? [Math.min(...alleX) - halbe, Math.max(...alleX) + halbe] : [])],
    bild.xbereich);
  const yb = bereich(alleY, bild.ybereich, { mitNull: balken.length > 0 });

  const kategorien = bild.kategorien;
  const xTeilung = kategorien
    ? { schritt: 1, format: (v) => kategorien[Math.round(v)] ?? '' }
    : { ziel: 7, format: (v) => zahl(v, schrittweite(xb[1] - xb[0], 7)) };
  const { svg, daten, x, y, feld } = achsenkreuz({
    breite: BREITE, hoehe: HOEHE,
    rand: { oben: bild.titel ? 30 : 14, rechts: 16, unten: bild.xlabel ? 44 : 30, links: bild.ylabel ? 64 : 50 },
    x: { bereich: xb, teilung: bild.gitter || kategorien ? xTeilung : { ...xTeilung, nurStriche: true }, null: true, titel: bild.xlabel },
    y: { bereich: yb, teilung: { ziel: 6, format: (v) => zahl(v, schrittweite(yb[1] - yb[0], 6)) }, null: true, titel: bild.ylabel },
    attribute: { class: 'py-bild-svg', role: 'img', 'aria-label': bild.titel || 'Diagramm' },
    rahmen: true,
  });

  if (bild.titel) {
    const titel = svgEl('text', {
      x: (feld.links + feld.rechts) / 2, y: 18, 'text-anchor': 'middle',
      'font-size': 13, 'font-weight': 600, fill: '#1a1f27',
    });
    titel.textContent = bild.titel;
    svg.append(titel);
  }

  // Zuerst die Hilfslinien, darüber Balken, Linien und Punkte.
  for (const h of bild.hilfslinien) {
    const senkrecht = h.achse === 'x';
    daten.append(svgEl('line', {
      x1: senkrecht ? x(h.wert) : feld.links, x2: senkrecht ? x(h.wert) : feld.rechts,
      y1: senkrecht ? feld.oben : y(h.wert), y2: senkrecht ? feld.unten : y(h.wert),
      stroke: h.farbe || '#5c6773', 'stroke-width': 1.2,
      'stroke-dasharray': STRICHMUSTER[h.strich] || null,
    }));
  }
  balken.forEach((r, k) => {
    // Mehrere Balkenreihen stehen nebeneinander, nicht übereinander.
    const breite = (r.breite ?? 0.8) / balken.length;
    r.x.forEach((xi, i) => {
      const yi = r.y[i];
      if (xi === null || yi === null) return;
      const links = xi - (r.breite ?? 0.8) / 2 + k * breite;
      daten.append(svgEl('rect', {
        x: x(links), width: Math.max(1, x(links + breite) - x(links)),
        y: Math.min(y(0), y(yi)), height: Math.abs(y(yi) - y(0)),
        fill: r.farbe, 'fill-opacity': r.deckung ?? 1,
      }));
    });
  });
  for (const r of reihen) {
    if (r.art === 'balken') continue;
    if (r.strich) {
      for (const stueck of stuecke(r, x, y)) {
        daten.append(svgEl('polyline', {
          points: stueck.map(([px, py]) => `${px.toFixed(1)},${py.toFixed(1)}`).join(' '),
          fill: 'none', stroke: r.farbe, 'stroke-width': r.breite ?? 1.8,
          'stroke-opacity': r.deckung ?? 1, 'stroke-linejoin': 'round',
          'stroke-dasharray': STRICHMUSTER[r.strich] || null,
        }));
      }
    }
    if (r.marke) {
      const groesse = r.groesse ?? 6;
      r.x.forEach((xi, i) => {
        if (xi === null || r.y[i] === null) return;
        const m = marke(r.marke, [x(xi), y(r.y[i])], groesse, r.farbe);
        m.setAttribute('opacity', r.deckung ?? 1);
        daten.append(m);
      });
    }
  }
  if (bild.legende) {
    const l = legende(reihen, feld);
    if (l) svg.append(l);
  }

  const huelle = el('div.py-bild', {}, [svg]);
  zeigerEinrichten(huelle, svg, reihen, x, y, kategorien);
  return huelle;
}

/** Beim Darüberfahren: der nächste Punkt, mit Reihe und Werten. */
function zeigerEinrichten(huelle, svg, reihen, x, y, kategorien) {
  const punkte = reihen.flatMap((r) => r.x.map((xi, i) => (
    xi === null || r.y[i] === null ? null
      : { px: x(xi), py: y(r.y[i]), xi, yi: r.y[i], name: r.name, farbe: r.farbe })))
    .filter(Boolean);
  if (!punkte.length) return;
  const zettel = el('div.py-zettel', { hidden: true });
  const ring = svgEl('circle', { r: 5, fill: 'none', 'stroke-width': 2, visibility: 'hidden' });
  svg.append(ring);
  huelle.append(zettel);
  const verbergen = () => {
    zettel.hidden = true;
    ring.setAttribute('visibility', 'hidden');
  };
  const zeigen = (e) => {
    const rahmen = svg.getBoundingClientRect();
    if (!rahmen.width) return;
    const f = BREITE / rahmen.width;
    const [mx, my] = [(e.clientX - rahmen.left) * f, (e.clientY - rahmen.top) * f];
    let beste = null;
    for (const p of punkte) {
      const d = Math.hypot(p.px - mx, p.py - my);
      if (d <= 24 && (!beste || d < beste.d)) beste = { ...p, d };
    }
    if (!beste) return verbergen();
    const xText = kategorien ? kategorien[Math.round(beste.xi)] : String(+beste.xi.toPrecision(6));
    zettel.replaceChildren(...[beste.name, `x = ${xText}`, `y = ${+beste.yi.toPrecision(6)}`]
      .filter(Boolean).map((t) => el('div', { text: t })));
    zettel.hidden = false;
    ring.setAttribute('cx', beste.px.toFixed(1));
    ring.setAttribute('cy', beste.py.toFixed(1));
    ring.setAttribute('stroke', beste.farbe);
    ring.setAttribute('visibility', 'visible');
    zettel.style.left = `${Math.min(beste.px / f + 12, rahmen.width - 150)}px`;
    zettel.style.top = `${beste.py / f + 12}px`;
    return undefined;
  };
  svg.addEventListener('pointermove', zeigen);
  svg.addEventListener('pointerdown', zeigen);
  svg.addEventListener('pointerleave', verbergen);
}
