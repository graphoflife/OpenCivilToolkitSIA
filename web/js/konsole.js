/**
 * konsole.js -- die Python-Sitzung der App «Python», in einem eigenen Faden.
 *
 * Der Faden ist derselbe wie beim Rechenkern (`kern_arbeiter.js`), nur mit
 * dem Dienst der Konsole (`opencivil/konsole/dienst.py`). Er startet erst,
 * wenn zum ersten Mal etwas ausgeführt wird: wer nie Python schreibt, lädt
 * nichts. Ein eigener Faden, damit eine Endlosschleife weder die Seite noch
 * den Rechenkern anhält -- «Abbrechen» beendet ihn, und mit ihm die Variablen.
 *
 * Immer im Browser, auch wenn der lokale Server rechnet: Code, den jemand
 * schreibt, läuft nie auf dem Rechner. Über den Server könnte sonst jede
 * Webseite Code auf ihm ausführen.
 *
 * Hier wird nichts gerechnet: Code geht hinein, Ereignisse und Variablen
 * kommen heraus. Was die Konsole zeigt, liegt in `konsole` -- die Ausgaben
 * seit dem letzten Leeren, die Variablen, ob gerade etwas läuft. Es gehört
 * zur Sitzung, nicht zum Projekt: gespeichert werden nur die Skripte.
 */

import { kernStarten } from './kern.js';

export const konsole = {
  /**
   * Was in der Konsole steht, der Reihe nach: die Eingaben und was sie
   * ergaben. `{art, text}` -- art ist 'eingabe', 'ausgabe', 'fehlerausgabe',
   * 'wert', 'fehler' oder 'hinweis' --, ein Bild als `{art: 'bild', bild}`.
   */
  ausgaben: [],
  /** Die Variablen nach dem letzten Lauf: `{name, typ, groesse, wert, lang}`. */
  variablen: [],
  /** Was gerade geschieht: '' (nichts), 'startet' (Python lädt) oder 'laeuft'. */
  stand: '',
  /** Die Eingaben der Konsole, für ↑ und ↓. */
  verlauf: [],
};

/** Versprechen auf den Faden, sobald er einmal gestartet wurde -- sonst null. */
let faden = null;
let neuZeichnen = () => {};

/** Wer gerufen wird, wenn sich etwas ändert -- die App, die neu zeichnet. */
export function konsoleVerbinden(zeichnen) {
  neuZeichnen = zeichnen;
}

function melden(ausgabe) {
  konsole.ausgaben.push(ausgabe);
}

function fadenStarten() {
  if (!faden) {
    faden = kernStarten(() => {}, { modul: 'opencivil.konsole.dienst' });
    faden.catch(() => { faden = null; });
  }
  return faden;
}

/**
 * Führt Code aus -- ein Skript oder eine Zeile der Konsole (`eingabe`). Eins
 * nach dem anderen: solange etwas läuft, geht nichts Neues hinein.
 */
export async function ausfuehren(code, { name = 'Konsole', eingabe = false } = {}) {
  if (konsole.stand) return;
  melden({ art: 'eingabe', text: code, name, eingabe });
  if (eingabe && code.trim() && konsole.verlauf.at(-1) !== code) konsole.verlauf.push(code);
  konsole.stand = faden ? 'laeuft' : 'startet';
  neuZeichnen();
  try {
    const { ruf } = await fadenStarten();
    konsole.stand = 'laeuft';
    neuZeichnen();
    const daten = await ruf('ausfuehren', { code, name, eingabe });
    konsole.ausgaben.push(...daten.ereignisse);
    konsole.variablen = daten.variablen;
  } catch (fehler) {
    // Abgebrochen hat schon gemeldet; alles andere kam aus dem Faden.
    if (!fehler.abgebrochen) melden({ art: 'fehler', text: fehler.message });
  } finally {
    konsole.stand = '';
    neuZeichnen();
  }
}

/**
 * Hält an, was läuft: der Faden wird beendet, ein neuer startet beim
 * nächsten Lauf. Python lässt sich in einem Faden nicht unterbrechen --
 * dafür bräuchte die Seite Kopfzeilen, die GitHub Pages nicht setzt.
 */
export async function abbrechen() {
  if (!faden) return;
  const alt = faden;
  faden = null;
  // Was lief, ist vorbei -- auch wenn seine Antwort nie mehr kommt.
  konsole.stand = '';
  konsole.variablen = [];
  melden({ art: 'hinweis', text: 'Abgebrochen. Die Sitzung beginnt neu, die Variablen sind weg.' });
  try {
    (await alt).beenden();
  } catch {
    /* Er startete gar nicht erst -- dann ist auch nichts zu beenden. */
  }
  neuZeichnen();
}

/** Leert den Namensraum; der Faden bleibt. */
export async function neuStarten() {
  if (konsole.stand) return;
  konsole.variablen = [];
  melden({ art: 'hinweis', text: 'Neu gestartet: alle Variablen sind weg.' });
  if (faden) {
    try {
      const { ruf } = await faden;
      konsole.variablen = (await ruf('zuruecksetzen', {})).variablen;
    } catch (fehler) {
      melden({ art: 'fehler', text: fehler.message });
    }
  }
  neuZeichnen();
}

/** Leert, was in der Konsole steht -- die Variablen bleiben. */
export function leeren() {
  konsole.ausgaben = [];
  neuZeichnen();
}
