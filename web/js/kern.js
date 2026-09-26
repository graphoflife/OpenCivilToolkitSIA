/**
 * kern.js -- Der Rechenkern im Browser, in Python.
 *
 * Startet Pyodide (Python als WebAssembly), lädt die Quelldateien aus
 * `opencivil/` nach und ruft darin `opencivil.web.dienst.bearbeite_json` auf.
 * Das ist derselbe Code, den `python3 start_ui.py` auf dem Rechner ausführt --
 * Zeile für Zeile dieselben Dateien, nicht eine Nachbildung in JavaScript.
 *
 * WARUM DAS SO SEIN MUSS:
 * Ein Werkzeug für Tragwerksnachweise darf nicht zwei Rechenwege haben, die
 * auseinanderdriften können. Gäbe es hier eine JavaScript-Fassung der Formeln,
 * wäre die Frage "welche stimmt?" nie zu beantworten. Also gibt es sie nicht.
 *
 * WAS HIER NICHT PASSIERT:
 * Gerechnet wird nichts, geprüft wird nichts, und keine Formel steht in dieser
 * Datei. Sie schaufelt Zeichenketten hin und her, mehr nicht.
 *
 * HAUPTFADEN:
 * Pyodide läuft im selben Faden wie die Oberfläche, ein Aufruf hält sie also
 * kurz an. Ein voller Durchgang des Beispielprojekts braucht in CPython 57 ms,
 * unter WebAssembly ein Mehrfaches davon -- spürbar, aber kein Grund für die
 * Umstände eines Arbeiterfadens. Sollte das Projekt einmal deutlich grösser
 * werden, wäre ein Web Worker der nächste Schritt.
 */

/** Verzeichnis, in das die Quelldateien im Dateisystem von Pyodide wandern. */
const EINHAENGEPUNKT = '/kern';

/** Das Projektverzeichnis, von dieser Datei aus gesehen (web/js/ -> ../../). */
const WURZEL = new URL('../../', import.meta.url);

const PYODIDE = new URL('../vendor/pyodide/', import.meta.url);
const MANIFEST = new URL('../kern/dateien.json', import.meta.url);

export class KernFehler extends Error {
  constructor(meldung, spur = '') {
    super(meldung);
    this.name = 'KernFehler';
    this.spur = spur;
  }
}

/**
 * Holt die Liste der Quelldateien und legt sie ins Dateisystem von Pyodide.
 *
 * Die Liste kommt aus `web/kern/dateien.json` und wird von
 * `opencivil/web/bruecke.py` geschrieben; ein Test wacht darüber, dass sie zu
 * den vorhandenen Dateien passt. Deshalb steht hier keine einzige
 * Dateiliste -- veraltete Abschriften wären genau die Art Fehler, die man erst
 * auf der veröffentlichten Seite bemerkt.
 *
 * VERSIONSMARKEN:
 * Jede Datei steht dort mit einer Marke (Prüfsumme ihres Inhalts) und wird als
 * `…py?v=Marke` geholt. Eine geänderte Datei hat so eine neue Adresse: der
 * Browser kann keine alte Fassung aus dem Zwischenspeicher nehmen, während die
 * übrigen schon neu sind.
 *
 * Das Verzeichnis selbst kommt dagegen wie jede andere Datei, auch aus dem
 * Zwischenspeicher. Es soll so alt sein wie die Oberfläche, die es liest --
 * GitHub Pages speichert beide zehn Minuten. An jedem Speicher vorbei geholt,
 * träfe nach einer Veröffentlichung eine noch gespeicherte alte Oberfläche
 * auf den neuen Kern.
 */
async function quellenEinhaengen(pyodide) {
  const antwort = await fetch(MANIFEST);
  if (!antwort.ok) {
    throw new KernFehler(
      `Kernverzeichnis fehlt (${antwort.status}) → «python3 -m opencivil.web.bruecke».`);
  }
  const { dateien } = await antwort.json();
  const eintraege = Object.entries(dateien || {});
  if (!eintraege.length) throw new KernFehler('Kernverzeichnis leer.');

  // Erst alle holen, dann alle schreiben: die Anfragen laufen so nebeneinander
  // statt hintereinander, was bei gut fünfzig Dateien deutlich ausmacht.
  const geladen = await Promise.all(eintraege.map(async ([name, marke]) => {
    const datei = await fetch(new URL(`${name}?v=${marke}`, WURZEL));
    if (!datei.ok) throw new KernFehler(`Kerndatei nicht erreichbar: ${name} (${datei.status})`);
    return [name, await datei.text()];
  }));

  const kodierer = new TextEncoder();
  for (const [name, inhalt] of geladen) {
    const pfad = `${EINHAENGEPUNKT}/${name}`;
    pyodide.FS.mkdirTree(pfad.slice(0, pfad.lastIndexOf('/')));
    pyodide.FS.writeFile(pfad, kodierer.encode(inhalt));
  }
  return eintraege.length;
}

/**
 * Startet Python im Browser und liefert eine Schnittstelle zum Rechendienst.
 *
 * @param {(text: string) => void} [fortschritt]  bekommt kurze Standmeldungen
 * @returns {Promise<{ruf: Function, art: string, fassung: string}>}
 */
export async function kernStarten(fortschritt = () => {}) {
  fortschritt('Python wird geladen …');

  let loadPyodide;
  try {
    ({ loadPyodide } = await import(new URL('pyodide.mjs', PYODIDE).href));
  } catch (ursache) {
    throw new KernFehler(
      'Pyodide nicht ladbar. Fehlt web/vendor/pyodide? → '
      + '«python3 werkzeug/pyodide_holen.py».', String(ursache));
  }

  const pyodide = await loadPyodide({
    indexURL: PYODIDE.href,
    // Was Python ausgibt, gehört in die Entwicklerkonsole und nicht ins Nichts.
    stdout: (zeile) => console.log('[Python]', zeile),
    stderr: (zeile) => console.warn('[Python]', zeile),
  });

  fortschritt('Rechenkern wird eingelesen …');
  const anzahl = await quellenEinhaengen(pyodide);

  pyodide.runPython(`
import sys
if ${JSON.stringify(EINHAENGEPUNKT)} not in sys.path:
    sys.path.insert(0, ${JSON.stringify(EINHAENGEPUNKT)})
`);

  let dienst;
  try {
    dienst = pyodide.pyimport('opencivil.web.dienst');
  } catch (ursache) {
    throw new KernFehler(
      'Rechenkern nicht einbindbar.', String(ursache));
  }

  const fassung = pyodide.runPython('import sys; sys.version.split()[0]');
  console.info(
    `Rechenkern bereit: Python ${fassung} über Pyodide, ${anzahl} Quelldateien.`);
  fortschritt('');

  /**
   * Führt eine Anfrage im Kern aus.
   *
   * Hinein und heraus geht JSON -- genau wie über HTTP. Dass beide Wege
   * dieselbe Wandlung durchlaufen, ist Absicht: so bekommt die Oberfläche in
   * beiden Fällen dieselben Daten, bis aufs Zeichen.
   */
  function ruf(name, rumpf = {}) {
    let roh;
    try {
      roh = dienst.bearbeite_json(name, JSON.stringify(rumpf));
    } catch (ursache) {
      // Hierher kommt nur, was bearbeite_json selbst umbringt -- der Dienst
      // fängt sonst alles ab und gibt es als Antwort zurück.
      throw new KernFehler(`Rechenkern abgebrochen: ${ursache}`, String(ursache));
    }

    const umschlag = JSON.parse(roh);
    if (umschlag.status >= 400) {
      throw new KernFehler(
        umschlag.daten.fehler || `Fehler ${umschlag.status}`, umschlag.daten.spur);
    }
    return umschlag.daten;
  }

  return { ruf, art: 'pyodide', fassung };
}
