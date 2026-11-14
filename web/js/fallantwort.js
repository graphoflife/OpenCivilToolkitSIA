/**
 * fallantwort.js -- die Bilder eines Falls, beim Kern erfragt.
 *
 * Balkensystem und Decke fragen nach den Bildern eines Falls -- Lastfall
 * oder Kombination -- mit einer eigenen Anfrage, erst wenn jemand sie sehen
 * will: sie sind gross, und mit jeder Rechnung mitgeliefert, machten sie
 * jede Eingabe langsamer. Hier steht einmal, wie das geht.
 *
 * Je Bauteil merkt sich die Ansicht (`ansichtVon`) unter `antworten` je
 * Fall die letzte Antwort: {fassung, fall, daten, alt, fehler, uhr}. Nach
 * einer Änderung am Projekt wird neu gefragt; bis die neue Antwort da ist,
 * gilt die alte. Gefragt wird erst, wenn gerade nicht gerechnet wird: dann
 * liegt das Bauteil im Speicher des Kerns. Zeigen zwei Bilder denselben
 * Fall, teilen sie sich die Antwort.
 */

import { aendern, ansichtVon, zustand } from './zustand.js';

/** Je Fall die letzte Antwort zu diesem Bauteil. */
function antwortenVon(kennung) {
  const ansicht = ansichtVon(kennung);
  ansicht.antworten ??= new Map();
  return ansicht.antworten;
}

/** Fragt nach den Bildern -- `fragen(fall)` gibt die Antwort des Kerns als Promise. */
function anfordern(kennung, eintrag, fragen, verzug = 500) {
  const gilt = () => antwortenVon(kennung).get(eintrag.fall) === eintrag;
  clearTimeout(eintrag.uhr);
  eintrag.uhr = setTimeout(() => {
    if (!gilt()) return;
    if (zustand.rechnetGerade) {
      anfordern(kennung, eintrag, fragen);
      return;
    }
    fragen(eintrag.fall).then((antwort) => {
      if (!gilt()) return;
      eintrag.daten = antwort;
      aendern({}, 'diagramm');
    }).catch((fehler) => {
      if (!gilt()) return;
      eintrag.fehler = fehler.message;
      aendern({}, 'diagramm');
    });
  }, verzug);
}

/**
 * Die Antwort des Kerns zu einem Fall eines Bauteils -- neu erfragt mit
 * `fragen(fall)`, wenn es keine gibt oder sich das Projekt seither geändert
 * hat. `daten` ist die neue Antwort, solange sie fehlt `alt` die letzte.
 */
export function antwortZu(kennung, fall, fragen) {
  let eintrag = antwortenVon(kennung).get(fall);
  if (!eintrag || eintrag.fassung !== zustand.fassung) {
    const alt = eintrag?.daten || eintrag?.alt || null;
    eintrag = { fassung: zustand.fassung, fall, daten: null, alt, fehler: null, uhr: null };
    antwortenVon(kennung).set(fall, eintrag);
    anfordern(kennung, eintrag, fragen, alt ? 500 : 80);
  }
  return eintrag;
}
