/**
 * cad_verlauf.js -- Ändern und Rückgängig im Zeichenfenster.
 *
 * Jede Änderung der Zeichnung geht durch `aendern`: es merkt sich den Stand
 * davor -- die Listen der Zeichnung als Text und was gewählt war --, bis zu
 * 100 Schritte zurück. Wer zurückgeht, kann wieder vorwärts, bis er etwas
 * Neues ändert. Nach jeder Änderung, auch einer von aussen
 * (`aktualisieren`), zählt das Fenster seine Version weiter, vergisst aus
 * der Auswahl, was es nicht mehr gibt, und lässt die App fragen, was der
 * Kern dazu sagt.
 */

import { istAnhang } from './cad_auswahl.js';

/** Wie viele Schritte «Rückgängig» zurückreicht. */
const VERLAUF = 100;

/** Die Zeichnung als Text: die Listen, sonst nichts. */
function stand(a) {
  const z = a.adapter.zeichnung();
  return JSON.stringify(a.listen.map((l) => z?.[l] || []));
}

/**
 * Ändert die Zeichnung und merkt sich den Stand davor -- ein Schritt für
 * «Rückgängig». `auswahl` liefert nach der Änderung, was danach gewählt sein
 * soll (etwa das eben angelegte Element); gesetzt wird es noch, bevor die
 * Tafel neu gezeichnet wird.
 */
export function aendern(a, veraenderer, { auswahl = null } = {}) {
  const vorher = stand(a);
  const vorherAuswahl = [...a.auswahl];
  const vor = a.vor;
  a.vor = [];
  a.adapter.schreiben((z) => {
    for (const l of a.listen) z[l] = z[l] || [];
    veraenderer(z);
    if (auswahl) a.auswahl = new Set((auswahl() || []).filter(Boolean));
  });
  if (stand(a) === vorher) {
    a.vor = vor;
    return;
  }
  a.rueck.push({ stand: vorher, auswahl: vorherAuswahl });
  if (a.rueck.length > VERLAUF) a.rueck.shift();
  aktualisieren(a);
}

function standSetzen(a, eintrag) {
  const werte = JSON.parse(eintrag.stand);
  a.auswahl = new Set(eintrag.auswahl);
  a.adapter.schreiben((z) => { a.listen.forEach((l, i) => { z[l] = werte[i]; }); });
  aktualisieren(a);
}

export function zurueck(a) {
  if (!a.rueck.length) return;
  a.vor.push({ stand: stand(a), auswahl: [...a.auswahl] });
  standSetzen(a, a.rueck.pop());
}

export function vorwaerts(a) {
  if (!a.vor.length) return;
  a.rueck.push({ stand: stand(a), auswahl: [...a.auswahl] });
  standSetzen(a, a.vor.pop());
}

/**
 * Die Zeichnung hat sich geändert -- von hier oder von aussen (Rückgängig,
 * eine geladene Datei): Fang neu sammeln, verschwundene Auswahl weg, die App
 * fragen lassen, was der Kern dazu sagt.
 */
export function aktualisieren(a) {
  const jetzt = stand(a);
  if (jetzt !== a.stand) {
    a.stand = jetzt;
    a.version += 1;
    const z = a.adapter.zeichnung() || {};
    // Ein Anhang ist kein Element des Modells; ob es ihn noch gibt, weiss
    // die App. Bis 2026-10-25 fiel er hier weg: jede Änderung an einer Last
    // auf einer Linie schloss ihr Fenster.
    a.auswahl = new Set([...a.auswahl].filter((k) => a.modell.gibt(z, k) || istAnhang(a, k)));
    a.adapter.geaendert?.(a);
  }
  a.neuZeichnen();
}
