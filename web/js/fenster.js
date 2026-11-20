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
 *
 * Was eine Antwort braucht, bevor es weitergeht -- ein neues Material, eine
 * Rückfrage --, steht in einem Fenster über der ganzen Seite
 * (`dialogFenster`), mit demselben Kopf.
 */

import { el, ersetzen } from './dom.js';
import { sinnbild } from './sinnbilder.js';
import { mitteAendern, zustand } from './zustand.js';

/** Der Grund, auf dem das Fenster liegt -- gesetzt von `fensterEinrichten`. */
let grundKnoten = null;

/**
 * Öffnet das Fenster und gibt ihm den Fokus: der nächste Tab führt in seine
 * Eingaben und nicht in die Tafel darunter.
 */
export function fensterOeffnen(schluessel) {
  mitteAendern({ fenster: schluessel });
  grundKnoten?.querySelector('.fenster')?.focus({ preventScroll: true });
}

export function fensterSchliessen() {
  if (zustand.fenster) mitteAendern({ fenster: null });
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
 * `breit` ist sie, wo eine Zeile mehr Zahlen trägt als ein Panel fasst --
 * die Mitte wird dann so lange breiter (Stilblatt, `.fenster.ist-breit`).
 */
export function fenster({
  titel, zeichen, zusatz, hilfe, inhalt, breit = false,
}) {
  return el('div.fenster', {
    class: breit ? 'ist-breit' : '', role: 'dialog', 'aria-label': titel, tabIndex: -1,
  }, [
    fensterkopf({ titel, zeichen, zusatz, hilfe, schliessen: fensterSchliessen }),
    el('div.fenster-inhalt', {}, inhalt),
  ]);
}

function fensterkopf({
  titel, zeichen, zusatz, hilfe = null, schliessen,
}) {
  return el('div.fenster-kopf', {}, [
    sinnbild(zeichen),
    el('div.fenster-titel', {}, [
      el('span', { text: titel }),
      zusatz ? el('span.fenster-zusatz', { text: zusatz }) : null,
    ]),
    hilfe,
    el('button.fenster-zu', {
      type: 'button', text: '×', title: 'Schliessen (Esc)', on: { click: schliessen },
    }),
  ]);
}

/**
 * Ein Fenster über der ganzen Seite, das erst zugeht, wenn man es schliesst:
 * mit ×, Esc oder einem Klick daneben. Danach ist es weg. `klasse` ist die
 * eigene Klasse, `.materialwahl`; `inhalt(schliessen)` baut, was darin
 * steht -- ein Knopf darin schliesst es mit `schliessen()`.
 */
export function dialogFenster({
  titel, zeichen, zusatz, klasse, inhalt,
}) {
  const dialog = el(`dialog.fenster.dialogfenster${klasse}`, { 'aria-label': titel });
  const schliessen = () => dialog.close();
  dialog.addEventListener('close', () => dialog.remove());
  dialog.addEventListener('click', (e) => { if (e.target === dialog) schliessen(); });
  dialog.append(
    fensterkopf({ titel, zeichen, zusatz, schliessen }),
    el('div.fenster-inhalt', {}, inhalt(schliessen)),
  );
  document.body.append(dialog);
  dialog.showModal();
  return dialog;
}

/**
 * Fragt, bevor etwas geschieht, das sich nicht zurücknehmen lässt: über den
 * Knöpfen `text`, je Wahl ein Knopf mit dem, was er bewirkt, daneben. Gibt
 * den `wert` der gewählten zurück -- null, wenn das Fenster ohne Wahl zuging
 * (Abbrechen, Esc, daneben geklickt).
 *
 * @param {{titel: string, zeichen: string, zusatz?: string, text: string,
 *   wahlen: Array<{wert: string, knopf: string, erklaerung: string, gefahr?: boolean}>}} frage
 * @returns {Promise<string|null>}
 */
export function rueckfrage({
  titel, zeichen, zusatz, text, wahlen,
}) {
  return new Promise((erfuellen) => {
    let gewaehlt = null;
    const dialog = dialogFenster({
      titel,
      zeichen,
      zusatz,
      klasse: '.rueckfrage',
      inhalt: (schliessen) => [
        el('p.rueckfrage-text', { text }),
        ...wahlen.map((w) => el('div.rueckfrage-wahl', {}, [
          el(`button.knopf${w.gefahr ? '.knopf-gefahr' : '.knopf-haupt'}`, {
            type: 'button',
            text: w.knopf,
            on: {
              click: () => {
                gewaehlt = w.wert;
                schliessen();
              },
            },
          }),
          el('span.rueckfrage-erklaerung', { text: w.erklaerung }),
        ])),
        el('div.rueckfrage-fuss', {}, [
          el('button.knopf', { type: 'button', text: 'Abbrechen', on: { click: schliessen } }),
        ]),
      ],
    });
    dialog.addEventListener('close', () => erfuellen(gewaehlt));
  });
}
