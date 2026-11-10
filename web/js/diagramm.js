/**
 * diagramm.js -- die Kurve eines Werkstoffgesetzes und die Hilfe, Beschriftungen
 * zu entzerren.
 *
 * Zeichnet die σ-ε-Linie, die der Rechenkern liefert -- wo es einen gibt, mit
 * dem vereinfachten Verlauf daneben. Die Bilder einer Platte -- Querschnitt,
 * M-N-Interaktionsdiagramm, M-V- und Neigungskurven -- stehen in
 * platte_bilder.js; bis 2026-11-10 standen sie hier, in einer Datei von fast
 * tausend Zeilen.
 *
 * Es wird nichts nachgerechnet: sämtliche Koordinaten kommen aus der Lösung.
 */

import { achsenkreuz, NR } from './achsen.js';
import { el, svgEl } from './dom.js';

/** Farbe des vereinfachten Verlaufs -- grün, wie verlangt. */
const GRUEN = '#16794a';

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

  const eps = punkte.map((p) => p.eps);
  const sig = punkte.map((p) => p.sigma);
  // Der Nullpunkt gehört immer ins Bild, sonst hängt die Kurve im Nichts.
  const spanne = (werte, luft = 0.08) => {
    const min = Math.min(0, ...werte);
    const max = Math.max(0, ...werte);
    const d = (max - min) || 1;
    return [min - d * luft, max + d * luft];
  };

  const { svg, daten, x, y } = achsenkreuz({
    breite: 560, hoehe: 360, rand: { oben: 18, rechts: 22, unten: 40, links: 68 },
    attribute: { class: 'mn', xmlns: NR, role: 'img', 'aria-label': gesetz.titel },
    x: {
      bereich: spanne(eps), teilung: { ziel: 6, format: (v) => Number(v.toFixed(2)) },
      null: true, titel: gesetz.x_titel,
    },
    y: { bereich: spanne(sig), teilung: { ziel: 6 }, null: true, titel: gesetz.y_titel },
  });

  // Kurve
  daten.append(svgEl('polyline', {
    points: punkte.map((p) => `${x(p.eps).toFixed(2)},${y(p.sigma).toFixed(2)}`).join(' '),
    fill: 'none', stroke: '#1f6feb', 'stroke-width': 2.2,
    'stroke-linejoin': 'round', 'stroke-linecap': 'round',
  }));

  // Vereinfachter Verlauf (Spannungsblock), sofern der Kern einen liefert.
  if (gesetz.vereinfacht && zeigeVereinfacht) {
    daten.append(svgEl('polyline', {
      points: gesetz.vereinfacht.punkte
        .map((p) => `${x(p.eps).toFixed(2)},${y(p.sigma).toFixed(2)}`).join(' '),
      fill: 'none', stroke: GRUEN, 'stroke-width': 2,
      'stroke-linejoin': 'miter', 'stroke-linecap': 'butt',
    }));
  }

  // Marken für die Grenzdehnungen
  for (const marke of gesetz.marken || []) {
    daten.append(svgEl('line', {
      x1: x(marke.eps), y1: y(0), x2: x(marke.eps), y2: y(marke.sigma),
      stroke: '#8895a8', 'stroke-width': 1, 'stroke-dasharray': '3 3',
    }));
    daten.append(svgEl('circle', {
      cx: x(marke.eps), cy: y(marke.sigma), r: 3.2,
      fill: '#fff', stroke: '#1f6feb', 'stroke-width': 1.6,
    }));
    const t = svgEl('text', {
      x: x(marke.eps), y: y(marke.sigma) + (marke.sigma < 0 ? 15 : -8),
      'text-anchor': 'middle', 'font-size': 10.5, fill: '#0d4ba8', 'font-weight': 600,
    });
    t.textContent = marke.text;
    daten.append(t);
  }

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

