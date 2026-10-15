/**
 * fenster.js -- ein Fenster über der Eingabespalte.
 *
 * Was zu viel Platz bräuchte, um immer offen dazustehen, öffnet sich auf
 * Knopfdruck in einem Fenster: Kopf mit Titel und Schliessen, darunter die
 * Eingaben. Es legt sich über die mittlere Tafel. Baum und Ergebnisse
 * bleiben sichtbar, damit man sieht, was eine Eingabe bewirkt.
 *
 * Welches offen ist, steht in `zustand.fenster`: der Schlüssel des
 * Kapitels, Ansichtssache und nicht Teil des Projekts. Es gehört immer zum
 * gewählten Bauteil -- wer ein anderes wählt, schliesst es (`waehlen` in
 * `zustand.js`). Gezeichnet wird es mit dem Editor neu, wie alles andere.
 * Der graue Grund darunter bleibt dabei stehen: er ist der Knoten, der
 * rollt, und so retten Bildlauf und Fokus wie bei den Tafeln (`app.js`).
 *
 * Schliessen: mit ×, mit Escape oder mit einem Klick neben das Fenster.
 */

import { el, ersetzen } from './dom.js';
import { sinnbild } from './sinnbilder.js';
import { aendern, zustand } from './zustand.js';

/** Der Grund, auf dem das Fenster liegt -- gesetzt von `fensterEinrichten`. */
let grundKnoten = null;

/**
 * Öffnet das Fenster und gibt ihm den Fokus: der nächste Tab führt in seine
 * Eingaben und nicht in die Tafel darunter.
 */
export function fensterOeffnen(schluessel) {
  aendern({ fenster: schluessel }, 'fenster');
  grundKnoten?.querySelector('.fenster')?.focus({ preventScroll: true });
}

export function fensterSchliessen() {
  if (zustand.fenster) aendern({ fenster: null }, 'fenster');
}

/** Einmal beim Start: Escape und ein Klick auf den Grund schliessen. */
export function fensterEinrichten(grund) {
  grundKnoten = grund;
  grund.addEventListener('click', (e) => {
    if (e.target === grund) fensterSchliessen();
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && zustand.fenster) fensterSchliessen();
  });
}

/** Legt das Fenster auf den Grund -- ohne Fenster verschwindet auch der Grund. */
export function fensterZeigen(grund, karte) {
  grund.hidden = !karte;
  ersetzen(grund, karte);
}

/**
 * Die Karte: Kopf mit Zeichen, Titel und Schliessen, darunter die Eingaben.
 * `zusatz` steht klein unter dem Titel, `hilfe` (ein «?») rechts davon.
 */
export function fenster({
  titel, zeichen, zusatz, hilfe, inhalt,
}) {
  return el('div.fenster', { role: 'dialog', 'aria-label': titel, tabIndex: -1 }, [
    el('div.fenster-kopf', {}, [
      sinnbild(zeichen),
      el('div.fenster-titel', {}, [
        el('span', { text: titel }),
        zusatz ? el('span.fenster-zusatz', { text: zusatz }) : null,
      ]),
      hilfe,
      el('button.fenster-zu', {
        type: 'button', text: '×', title: 'Schliessen (Esc)',
        on: { click: fensterSchliessen },
      }),
    ]),
    el('div.fenster-inhalt', {}, inhalt),
  ]);
}
