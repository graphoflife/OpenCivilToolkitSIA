/**
 * editor.js -- Mittlere Tafel: Eingaben zum ausgewählten Bestandteil.
 *
 * Welcher Editor es ist, welches Fenster über ihm aufgeht und was im Kopf
 * steht, sagt die Zeile seiner App (apps.js); hier steht nur, wie die Tafel
 * gezeichnet wird. Die Editoren stehen bei ihren Apps: material.js,
 * platte.js, querschnittsanalyse.js, balkensystem.js, durchstanzen.js, grundbruch.js,
 * setzung.js und python.js. Bis 2026-10-18 standen der des Materials und der der Platte hier.
 *
 * Angezeigt wird immer der Wert aus der letzten Lösung, nie ein in der
 * Oberfläche nachgerechneter.
 */

import { gewaehlt } from './apps.js';
import { el, ersetzen } from './dom.js';
import { fensterZeigen } from './fenster.js';
import { zustand } from './zustand.js';

/**
 * Zeichnet die mittlere Tafel: den Editor des gewählten Bestandteils und,
 * wenn eines offen ist, sein Fenster darüber.
 */
export function editorZeichnen(behaelter, titelKnoten, hinweisKnoten, fensterGrund) {
  const auswahl = gewaehlt();
  fensterZeigen(fensterGrund, auswahl && zustand.fenster
    ? auswahl.app.fenster?.(auswahl.eintrag, zustand.fenster) : null);

  if (auswahl) {
    const { app, eintrag } = auswahl;
    titelKnoten.textContent = app.name(eintrag);
    hinweisKnoten.textContent = app.hinweis(eintrag);
    return app.editor(behaelter, eintrag);
  }
  titelKnoten.textContent = 'Eingaben';
  hinweisKnoten.textContent = '';
  return ersetzen(behaelter, el('div.leer', {}, [
    el('p', { text: 'Links Bestandteil wählen.' }),
    el('p', { text: 'Neu: + über der Liste links.' }),
  ]));
}
