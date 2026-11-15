/**
 * cad_raum.js -- das Zeichenfenster im Raum: Blickrichtung und Arbeitsebene.
 *
 * Eine App mit drei Achsen (das 3D-Balkensystem) sieht ihre Zeichnung
 * parallel projiziert, aus einer Richtung, die sich drehen lässt: mit der
 * rechten Maustaste ziehen, oder ein Knopf für eine der Ansichten -- 3D,
 * Grundriss x-y, Ansicht x-z, Ansicht y-z. Wohin ein Klick ins Leere zeigt,
 * sagt die Arbeitsebene: der Grundriss in einer Höhe z, die Ansicht x-z bei
 * einem y, die Ansicht y-z bei einem x. Auf ihr liegt das Raster. Knoten,
 * Linien und ihre Punkte fangen, wo sie auch liegen; mit X, Y und Z bindet
 * man an eine Achse durch den Bezugspunkt -- so entsteht eine Stütze auf
 * dem Grundriss --, und E legt die Arbeitsebene durch den gefangenen
 * Punkt.
 *
 * Wer eine der Ansichten x-y, x-z oder y-z wählt, zeichnet danach in ihrer
 * Ebene: die Arbeitsebene geht mit, in der Lage, die sie zuletzt hatte.
 *
 * Die Ansicht stellt nur dar: nichts davon geht in die Zeichnung, und nichts
 * wird abgelegt.
 */

import { wahlSchalter } from './bausteine.js';
import {
  blickrichtung, nachBild, nachWelt, rasterschritt, richtungImBild, text,
} from './cad_ansicht.js';
import { el, svgEl } from './dom.js';

/** Die Arbeitsebenen: die Achse, die auf ihr senkrecht steht, und wie sie heissen. */
export const EBENEN = [
  { achse: 2, kurz: 'x-y', name: 'Grundriss: die Ebene x-y in einer Höhe z' },
  { achse: 1, kurz: 'x-z', name: 'Ansicht x-z: die Ebene bei einem y' },
  { achse: 0, kurz: 'y-z', name: 'Ansicht y-z: die Ebene bei einem x' },
];

/**
 * Die Ansichten: aus welcher Richtung man blickt -- Azimut ab x gegen y und
 * Höhe über dem Grundriss, in Grad -- und in welcher Ebene man danach
 * zeichnet. Schräg von oben liegt x nach rechts unten, y nach rechts oben.
 */
export const ANSICHTEN = [
  { name: '3d', text: '3D', titel: 'Schräg von oben', azimut: -50, hoehe: 30, ebene: null },
  { name: 'oben', text: 'x-y', titel: 'Grundriss: von oben', azimut: -90, hoehe: 90, ebene: 2 },
  { name: 'vorne', text: 'x-z', titel: 'Ansicht x-z: von vorne, aus −y', azimut: -90, hoehe: 0, ebene: 1 },
  { name: 'seite', text: 'y-z', titel: 'Ansicht y-z: von der Seite, aus +x', azimut: 0, hoehe: 0, ebene: 0 },
];

/** Wie viele Grad ein Bildpunkt Ziehen dreht. */
const GRAD_JE_PUNKT = 0.4;

/**
 * Die Richtungen nach rechts und nach oben im Bild, in der Zeichnung -- für
 * eine Blickrichtung aus Azimut und Höhe. Rechts liegt immer waagrecht.
 */
export function basisAus({ azimut, hoehe }) {
  const [a, h] = [azimut, hoehe].map((w) => (w * Math.PI) / 180);
  const rechts = [-Math.sin(a), Math.cos(a), 0];
  const blick = [Math.cos(h) * Math.cos(a), Math.cos(h) * Math.sin(a), Math.sin(h)];
  const oben = [
    blick[1] * rechts[2] - blick[2] * rechts[1],
    blick[2] * rechts[0] - blick[0] * rechts[2],
    blick[0] * rechts[1] - blick[1] * rechts[0],
  ];
  return [rechts, oben];
}

/** Richtet die Ansicht eines Fensters für den Raum ein: schräg von oben, gezeichnet im Grundriss bei z = 0. */
export function raumEinrichten(a) {
  const start = ANSICHTEN[0];
  a.raum = { drehung: { azimut: start.azimut, hoehe: start.hoehe }, lagen: [0, 0, 0] };
  a.v.basis = basisAus(a.raum.drehung);
  a.v.ebene = { achse: 2, lage: 0 };
}

/** Wählt die Arbeitsebene -- in der Lage, die sie zuletzt hatte, oder in `lage`. */
export function ebeneSetzen(a, achse, lage = a.raum.lagen[achse]) {
  a.raum.lagen[achse] = lage;
  a.v.ebene = { achse, lage };
}

/** E: die Arbeitsebene durch einen Punkt, in ihrer Richtung. */
export function ebeneDurch(a, p) {
  ebeneSetzen(a, a.v.ebene.achse, p[a.v.ebene.achse]);
}

/** Die Mitte dessen, was «Alles zeigen» ins Bild nimmt -- um sie dreht die Ansicht. */
export function drehpunkt(a) {
  const [klein, gross] = a.adapter.umriss(a);
  return klein.map((w, i) => (w + gross[i]) / 2);
}

/**
 * Dreht die Ansicht um `dx` und `dy` Bildpunkte Ziehen -- um den Punkt
 * `um`, der dabei im Bild bleibt, wo er war. Die Höhe hält bei ±90°: über
 * den Scheitel hinaus stünde die Zeichnung auf dem Kopf.
 */
export function drehen(a, dx, dy, um) {
  const d = a.raum.drehung;
  const vorher = nachBild(a.v, um);
  d.azimut = (d.azimut - dx * GRAD_JE_PUNKT) % 360;
  d.hoehe = Math.max(-90, Math.min(90, d.hoehe + dy * GRAD_JE_PUNKT));
  a.v.basis = basisAus(d);
  const nachher = nachBild(a.v, um);
  a.v.ursprung = [a.v.ursprung[0] + vorher[0] - nachher[0], a.v.ursprung[1] + vorher[1] - nachher[1]];
}

/** Eine der Ansichten -- mit ihrer Arbeitsebene, und alles im Bild. */
export function ansichtSetzen(a, name, allesZeigen) {
  const x = ANSICHTEN.find((w) => w.name === name);
  a.raum.drehung = { azimut: x.azimut, hoehe: x.hoehe };
  a.v.basis = basisAus(a.raum.drehung);
  if (x.ebene !== null) ebeneSetzen(a, x.ebene);
  allesZeigen();
}

/** Welche der Ansichten gerade gilt -- oder null, wenn gedreht wurde. */
function ansichtJetzt(a) {
  const d = a.raum.drehung;
  return ANSICHTEN.find((x) => Math.abs(x.azimut - d.azimut) < 1e-6 && Math.abs(x.hoehe - d.hoehe) < 1e-6)?.name ?? null;
}

/**
 * Die Knöpfe der Ansichten für die Leiste über der Zeichnung: ein Schalter,
 * an ist die Ansicht, die gerade gilt -- keine, wenn gedreht wurde. Neu
 * gebaut wird er nur, wenn sich das ändert (`zeichnen`, nach jedem Bild).
 * Die Arbeitsebene stellt das schwebende Fenster ein (cad_palette.js).
 */
export function ansichtsleiste(a, allesZeigen) {
  const knoten = el('span.cad-ansichten');
  let gezeigt;
  const zeichnen = () => {
    const jetzt = ansichtJetzt(a);
    if (knoten.firstChild && jetzt === gezeigt) return;
    gezeigt = jetzt;
    knoten.replaceChildren(wahlSchalter({
      werte: ANSICHTEN.map((x) => ({ wert: x.name, beschriftung: x.text, titel: x.titel })),
      gewaehlt: jetzt, titel: 'Ansicht -- drehen mit der rechten Maustaste',
      setzen: (name) => ansichtSetzen(a, name, allesZeigen), klasse: '.cad-wahl.ist-wortlaut',
    }));
  };
  zeichnen();
  return { knoten, zeichnen };
}

/** Die Richtung einer Achse -- 1 in ihr, 0 in den anderen. */
const achse = (i) => [0, 1, 2].map((j) => (j === i ? 1 : 0));

/**
 * Das Raster auf der Arbeitsebene, so weit man sie sieht, und die drei
 * Achsen durch den Ursprung -- unten links ein kleines Achsenkreuz, das die
 * Richtungen zeigt. Sieht man die Ebene fast von der Seite, bleibt das
 * Raster weg: seine Linien fielen zusammen.
 */
export function raumRaster(a) {
  const v = a.v;
  const g = svgEl('g', { class: 'cad-raster' });
  const { achse: quer, lage } = v.ebene;
  const [i, j] = [0, 1, 2].filter((k) => k !== quer);
  if (Math.abs(blickrichtung(v)[quer]) > 0.08) {
    const ecken = [[0, 0], [v.breite, 0], [0, v.hoehe], [v.breite, v.hoehe]].map((b) => nachWelt(v, b));
    const spanne = (k) => [Math.min(...ecken.map((p) => p[k])), Math.max(...ecken.map((p) => p[k]))];
    const punkt = (u, w) => {
      const p = [0, 0, 0];
      p[i] = u;
      p[j] = w;
      p[quer] = lage;
      return nachBild(v, p);
    };
    let fein = '';
    let grob = '';
    for (const [k, l, umgekehrt] of [[i, j, false], [j, i, true]]) {
      const [k0, k1] = spanne(k);
      const [l0, l1] = spanne(l);
      let schritt = rasterschritt(a.raster, Math.hypot(...richtungImBild(v, achse(k))));
      // Nie mehr als 300 Linien je Richtung -- so weit reicht eine Ebene fast von der Seite.
      while ((k1 - k0) / schritt > 300) schritt *= 10;
      const fuenf = schritt * 5;
      for (let u = Math.ceil(k0 / schritt) * schritt; u <= k1; u += schritt) {
        const [p, q] = umgekehrt ? [punkt(l0, u), punkt(l1, u)] : [punkt(u, l0), punkt(u, l1)];
        const d = `M${p[0].toFixed(1)} ${p[1].toFixed(1)} L${q[0].toFixed(1)} ${q[1].toFixed(1)}`;
        if (Math.abs(u / fuenf - Math.round(u / fuenf)) < 1e-6) grob += d; else fein += d;
      }
    }
    g.append(svgEl('path', { d: fein, class: 'cad-raster-fein' }), svgEl('path', { d: grob, class: 'cad-raster-grob' }));
  }
  // Die Achsen durch den Ursprung, über das ganze Bild.
  const o = nachBild(v, [0, 0, 0]);
  const lang = Math.hypot(v.breite, v.hoehe) * 2;
  let d = '';
  for (let k = 0; k < 3; k += 1) {
    const r = richtungImBild(v, achse(k));
    const l = Math.hypot(...r);
    if (l < 1e-6) continue;
    d += `M${(o[0] - (r[0] / l) * lang).toFixed(1)} ${(o[1] - (r[1] / l) * lang).toFixed(1)} `
      + `L${(o[0] + (r[0] / l) * lang).toFixed(1)} ${(o[1] + (r[1] / l) * lang).toFixed(1)}`;
  }
  g.append(svgEl('path', { d, class: 'cad-achse' }), achsenkreuz(v, a.adapter.achsen));
  return g;
}

/**
 * Unten links im Bild der Ansicht `v` die Achsen `namen`, wie sie dort
 * liegen -- je 26 Bildpunkte lang, wenn sie quer zum Blick liegen. Auch die
 * Diagramme im Raum zeigen es.
 */
export function achsenkreuz(v, namen) {
  const g = svgEl('g', { class: 'cad-achsenkreuz' });
  const o = [30, v.hoehe - 30];
  namen.forEach((name, k) => {
    const r = richtungImBild(v, achse(k)).map((x) => (x / v.massstab) * 26);
    const ende = [o[0] + r[0], o[1] + r[1]];
    g.append(
      svgEl('path', { d: `M${o[0]} ${o[1]} L${ende[0].toFixed(1)} ${ende[1].toFixed(1)}`, class: 'cad-achsenpfeil' }),
      text(o[0] + r[0] * 1.35, o[1] + r[1] * 1.35 + 4, name, 'cad-achstext'),
    );
  });
  return g;
}
