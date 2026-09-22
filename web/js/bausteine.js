/**
 * bausteine.js -- kleine Bedienteile, die mehr als eine Tafel braucht.
 *
 * Hier steht, was Editor und Nachweistafel gemeinsam benutzen: die
 * Feldzeile, der Ja/Nein-Schalter, die Richtungswahl. Sie lagen vorher in
 * `editor.js`, und als die Nachweise ein eigenes Modul bekamen, hätten die
 * beiden sich gegenseitig importieren müssen. Ein drittes Modul, das keines
 * von beiden kennt, ist der Ausweg -- und der richtige Ort für Teile, die
 * ohnehin niemandem im Besonderen gehören.
 */

import { el } from './dom.js';
import { span } from './mathe.js';

/**
 * Eine Zeile Beschriftung – Eingabe – Einheit.
 *
 * `beschriftung` ist entweder Klartext oder eine Liste von Knoten. Letzteres
 * für Symbole, die tiefgestellte Teile haben: `D_max` als blosser Text gelesen
 * hiesse, den Index zu unterschlagen.
 */
export function feld(beschriftung, eingabe, einheit, titel) {
  const istText = typeof beschriftung === 'string';
  return el('div.feld', {}, [
    istText
      ? el('label', { text: beschriftung, title: titel || beschriftung })
      : el('label', { title: titel || '' }, beschriftung),
    eingabe,
    el('span.einheit', { text: einheit || '' }),
  ]);
}

export function richtungVon(querschnitt, nummer) {
  const gegen = (r) => (r === 'x' ? 'y' : 'x');
  return {
    1: querschnitt.richtung_lage1,
    2: gegen(querschnitt.richtung_lage1),
    3: gegen(querschnitt.richtung_lage4),
    4: querschnitt.richtung_lage4,
  }[nummer];
}

/**
 * Eine Einwirkung auf einer Zeile:
 *
 *     [Name] M_Ed [.] N_Ed [.] V_Ed [.] [x|y|beide] [×]
 *
 * Der Massstab fehlt bewusst: der Kern misst waagrecht, ausser nahe den
 * Spitzen der Resistenzlinie -- dort senkrecht. Welcher Weg gegriffen hat,
 * steht beim Nachweis.
 */
/**
 * Dreistellungs-Schalter für die Tragrichtung einer Einwirkung.
 *
 * Dieselben Farben wie bei den Lagen -- x blau, y kupfer -- damit man beim
 * Blick auf die Maske nicht überlegen muss, welche Richtung welche ist. `x+y`
 * bekommt ein sanftes Violett: die Mischung aus beiden.
 */
export function richtungsWahl(gewaehlt, setzen, nur = null) {
  // `nur` schränkt die Stellungen ein. Ein Querschnittsbild zeigt einen
  // Schnitt, und der liegt in einer Richtung -- «beide» wäre dort keine
  // Antwort, sondern zwei.
  const stellungen = [
    ['x', 'x', 'nur x-Richtung'],
    ['y', 'y', 'nur y-Richtung'],
    ['beide', 'x+y', 'beide Tragrichtungen'],
  ].filter(([wert]) => !nur || nur.includes(wert));
  return el('span.schalter.schalter-richtung', {
    title: 'In welcher Tragrichtung nachgewiesen wird',
  }, stellungen.map(([wert, text, beschreibung]) => el('button.schalter-halb', {
    text,
    title: beschreibung,
    class: `ist-${wert}${gewaehlt === wert ? ' ist-an' : ''}`,
    on: { click: () => { if (gewaehlt !== wert) setzen(wert); } },
  })));
}

/** Genau vier Schalter, auch wenn die Beschreibung älter ist als der Nachweis. */
export function lagenwahl(vorhanden, vorgabe) {
  const liste = Array.isArray(vorhanden) ? vorhanden : [];
  return vorgabe.map((v, i) => (i < liste.length ? !!liste[i] : v));
}

/**
 * Zweistellungs-Schalter ja/nein -- grüner Haken, rotes Kreuz.
 *
 * Beide Hälften gleich breit und die Zeichen mittig: ✓ und ✗ sind verschieden
 * breit, und bei symmetrischem Innenabstand wurde der Schalter dadurch schief.
 */
export function hakenSchalter(an, setzen, was = 'Nachweis') {
  return el('span.schalter.schalter-haken', {
    title: an ? `${was} wird geführt` : `${was} wird nicht geführt`,
  }, [
    el('button.schalter-halb.ist-ja', {
      text: '✓', title: `${was} führen`,
      class: an ? 'ist-an' : '',
      on: { click: () => { if (!an) setzen(true); } },
    }),
    el('button.schalter-halb.ist-nein', {
      text: '✗', title: `${was} nicht führen`,
      class: an ? '' : 'ist-an',
      on: { click: () => { if (an) setzen(false); } },
    }),
  ]);
}

/**
 * Ein Fragezeichen, das seine Erklärung beim Darüberfahren zeigt.
 *
 * Die Erklärungen standen vorher offen neben den Kapitelüberschriften --
 * «x / d ≤ 0.35 bei M_Ed = 0» und ähnliches. Richtig, aber laut: wer die
 * Maske bedient, liest sie beim ersten Mal und danach nie wieder, und
 * breiter machen sie die Tafel jedes Mal.
 *
 * `text` ist die kurze Fassung, `formel` die Bedingung in einer Zeile.
 */
export function erklaerung(text, formel = '') {
  const zettel = el('span.erklaerung', { title: `${text}${formel ? `\n\n${formel}` : ''}` }, [
    el('span.erklaerung-zeichen', { text: '?' }),
    el('span.erklaerung-blase', {}, [
      el('span', { text }),
      formel ? el('code', { text: formel }) : null,
    ]),
  ]);
  return zettel;
}
