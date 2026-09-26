/**
 * kern_arbeiter.js -- Pyodide in einem eigenen Faden.
 *
 * Startet Python (WebAssembly), legt die Quelldateien aus `opencivil/` in sein
 * Dateisystem und ruft darin `opencivil.web.dienst.bearbeite_json` auf -- je
 * Nachricht eine Anfrage, der Reihe nach. Der Hauptfaden (`kern.js`) schickt
 * Name und Rumpf als JSON und bekommt die Antwort als JSON zurück, genau wie
 * über HTTP.
 *
 * WARUM EIN EIGENER FADEN:
 * Im Hauptfaden hielt jeder Aufruf die Seite an, so lange er rechnete. Beim
 * Beispiel waren das Zehntelsekunden; die Dickensuche einer Platte mit allen
 * Nachweisen braucht bis zu einer halben Minute. Hier rechnet Python, und die
 * Oberfläche bleibt bedienbar: der Laufbalken läuft, die Seite scrollt.
 *
 * Nachrichten an den Hauptfaden: `fortschritt` (für den Ladeschirm), `bereit`
 * oder `gescheitert` (einmal, nach dem Start), `antwort` (je Anfrage).
 */

/** Verzeichnis, in das die Quelldateien im Dateisystem von Pyodide wandern. */
const EINHAENGEPUNKT = '/kern';

/** Das Projektverzeichnis, von dieser Datei aus gesehen (web/js/ -> ../../). */
const WURZEL = new URL('../../', import.meta.url);

const PYODIDE = new URL('../vendor/pyodide/', import.meta.url);
const MANIFEST = new URL('../kern/dateien.json', import.meta.url);

const melden = (nachricht) => self.postMessage(nachricht);

/** Ein Fehler mit Spur -- wie `KernFehler` im Hauptfaden, aber als Daten verschickbar. */
function startfehler(meldung, spur = '') {
  return Object.assign(new Error(meldung), { spur });
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
    throw startfehler(
      `Kernverzeichnis fehlt (${antwort.status}) → «python3 -m opencivil.web.bruecke».`);
  }
  const { dateien } = await antwort.json();
  const eintraege = Object.entries(dateien || {});
  if (!eintraege.length) throw startfehler('Kernverzeichnis leer.');

  // Erst alle holen, dann alle schreiben: die Anfragen laufen so nebeneinander
  // statt hintereinander, was bei gut fünfzig Dateien deutlich ausmacht.
  const geladen = await Promise.all(eintraege.map(async ([name, marke]) => {
    const datei = await fetch(new URL(`${name}?v=${marke}`, WURZEL));
    if (!datei.ok) throw startfehler(`Kerndatei nicht erreichbar: ${name} (${datei.status})`);
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

/** Python laden, den Kern einhängen, den Dienst einbinden -- und melden, dass es geht. */
async function starten() {
  melden({ art: 'fortschritt', text: 'Python wird geladen …' });

  let loadPyodide;
  try {
    ({ loadPyodide } = await import(new URL('pyodide.mjs', PYODIDE).href));
  } catch (ursache) {
    throw startfehler(
      'Pyodide nicht ladbar. Fehlt web/vendor/pyodide? → '
      + '«python3 werkzeug/pyodide_holen.py».', String(ursache));
  }

  const pyodide = await loadPyodide({
    indexURL: PYODIDE.href,
    // Was Python ausgibt, gehört in die Entwicklerkonsole und nicht ins Nichts.
    stdout: (zeile) => console.log('[Python]', zeile),
    stderr: (zeile) => console.warn('[Python]', zeile),
  });

  melden({ art: 'fortschritt', text: 'Rechenkern wird eingelesen …' });
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
    throw startfehler('Rechenkern nicht einbindbar.', String(ursache));
  }

  const fassung = pyodide.runPython('import sys; sys.version.split()[0]');
  console.info(
    `Rechenkern bereit: Python ${fassung} über Pyodide, ${anzahl} Quelldateien.`);
  melden({ art: 'bereit', fassung });
  return dienst;
}

const dienstBereit = starten().catch((fehler) => {
  melden({ art: 'gescheitert', meldung: fehler.message, spur: fehler.spur || '' });
  return null;
});

/**
 * Eine Anfrage: `{nr, name, rumpf}`, der Rumpf schon als JSON. Hinein und
 * heraus geht JSON -- genau wie über HTTP; so bekommt die Oberfläche auf beiden
 * Wegen dieselben Daten, bis aufs Zeichen. Der Reihe nach, weil Python in
 * diesem Faden eines nach dem anderen tut.
 */
self.onmessage = async ({ data: { nr, name, rumpf } }) => {
  const dienst = await dienstBereit;
  if (!dienst) return;   // Der Start ist gescheitert; das ist schon gemeldet.
  try {
    melden({ art: 'antwort', nr, roh: dienst.bearbeite_json(name, rumpf) });
  } catch (ursache) {
    // Hierher kommt nur, was bearbeite_json selbst umbringt -- der Dienst
    // fängt sonst alles ab und gibt es als Antwort zurück.
    melden({ art: 'antwort', nr, absturz: String(ursache) });
  }
};
