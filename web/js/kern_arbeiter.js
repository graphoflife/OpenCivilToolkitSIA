/**
 * kern_arbeiter.js -- Pyodide in einem eigenen Faden.
 *
 * Startet Python (WebAssembly), legt die Quelldateien aus `opencivil/` in sein
 * Dateisystem und ruft darin `bearbeite_json` eines Dienstes auf -- je
 * Nachricht eine Anfrage, der Reihe nach. Der Dienst ist der Rechenkern
 * (`opencivil.web.dienst`) oder, in einem Faden für sich, die Konsole der App
 * «Python» (`opencivil.konsole.dienst`). Der Hauptfaden (`kern.js`) schickt
 * Name und Rumpf als JSON und bekommt die Antwort als JSON zurück, genau wie
 * über HTTP.
 *
 * WARUM EIN EIGENER FADEN:
 * Im Hauptfaden hielt jeder Aufruf die Seite an, so lange er rechnete. Beim
 * Beispiel waren das Zehntelsekunden; die Dickensuche einer Platte mit allen
 * Nachweisen braucht bis zu einer halben Minute. Hier rechnet Python, und die
 * Oberfläche bleibt bedienbar: der Laufbalken läuft, die Seite scrollt.
 *
 * ÜBERSETZT VOM LETZTEN BESUCH:
 * Beim Einbinden übersetzt Python jede Quelldatei, und das ist rund die
 * Hälfte des Einlesens. Einige Sekunden nach dem Start legt der Faden das
 * Übersetzte in einen Speicher des Browsers; beim nächsten Besuch kommt es
 * vor dem Einbinden wieder an seinen Ort, und Python prüft jedes Stück am
 * Inhalt seiner Quelle (`opencivil/web/uebersetzt.py` sagt, wie und warum).
 * Gibt es keinen Speicher oder geht dabei etwas schief, startet der Kern wie
 * ohne, nur langsamer.
 *
 * Nachrichten vom Hauptfaden: zuerst `start` mit der Adresse der Kernquellen
 * und dem Dienst, dann je Anfrage eine. Nachrichten an den
 * Hauptfaden: `fortschritt` (für den Ladeschirm), `bereit` oder `gescheitert`
 * (einmal, nach dem Start), `antwort` (je Anfrage).
 *
 * Die Importtafel aus index.html gilt in einem Faden nicht. Darum bindet
 * dieser keine eigenen Module ein -- sie kämen ohne Versionsmarke.
 */

/** Verzeichnis, in das die Quelldateien im Dateisystem von Pyodide wandern. */
const EINHAENGEPUNKT = '/kern';

const PYODIDE = new URL('../vendor/pyodide/', import.meta.url);

/**
 * Der Speicher des Browsers für das Übersetzte, darin je Dienst ein Stück.
 * `sw.js` kennt den Namen, damit sein Aufräumen den Speicher stehen lässt.
 */
const UEBERSETZT = 'opencivil-uebersetzt';

/** Das Stück im Dateisystem von Pyodide, auf dem Weg aus dem Speicher und hinein. */
const STUECK = '/tmp/uebersetzt';

/** So lange nach dem Start wird das Übersetzte abgelegt: nicht auf dessen Weg. */
const ABLEGEN_NACH_MS = 3000;

const melden = (nachricht) => self.postMessage(nachricht);

/**
 * Jetzt, in Millisekunden seit 1970. Die Uhr eines Fadens zählt ab seinem
 * eigenen Start; so lässt sie sich mit der der Seite vergleichen.
 */
const jetzt = () => performance.timeOrigin + performance.now();

/** Ein Fehler mit Spur -- wie `KernFehler` im Hauptfaden, aber als Daten verschickbar. */
function startfehler(meldung, spur = '') {
  return Object.assign(new Error(meldung), { spur });
}

/**
 * Holt die Quelldateien des Kerns, alle in einem Stück: `[[Pfad, Inhalt], …]`.
 *
 * Das Paket, `web/kern/quellen.json`, schreibt `opencivil/web/bruecke.py`;
 * ein Test wacht darüber, dass es zu den vorhandenen Dateien passt. Deshalb
 * steht hier keine einzige Dateiliste -- veraltete Abschriften wären genau die
 * Art Fehler, die man erst auf der veröffentlichten Seite bemerkt. Darin liegt
 * auch das Verzeichnis `web/kern/dateien.json`: die Konsole liest dort,
 * welche Fremdpakete beiliegen.
 *
 * Bis 2026-11-20 kam jede Datei für sich, nach dem Verzeichnis. Auf GitHub
 * kostet jede Anfrage ihre Zeit, und 214 laufen nicht alle zugleich.
 *
 * VERSIONSMARKE:
 * Das Paket hat seine Marke in der Importtafel von index.html, wie jedes Modul
 * der Oberfläche. Es ist damit genau so alt wie die Seite, die es liest. An
 * jedem Speicher vorbei geholt, träfe nach einer Veröffentlichung eine noch
 * gespeicherte alte Seite auf den neuen Kern.
 *
 * @param {string} adresse  Adresse von `web/kern/quellen.json`, mit Marke
 */
async function quellenHolen(adresse) {
  const antwort = await fetch(adresse);
  if (!antwort.ok) {
    throw startfehler(
      `Kernquellen fehlen (${antwort.status}) → «python3 -m opencivil.web.bruecke».`);
  }
  const dateien = Object.entries((await antwort.json()).dateien || {});
  if (!dateien.length) throw startfehler('Kernquellen leer.');
  return dateien;
}

/** Legt die Quelldateien ins Dateisystem von Pyodide, unter `EINHAENGEPUNKT`. */
function quellenEinhaengen(pyodide, dateien) {
  for (const [name, inhalt] of dateien) {
    const pfad = `${EINHAENGEPUNKT}/${name}`;
    pyodide.FS.mkdirTree(pfad.slice(0, pfad.lastIndexOf('/')));
    pyodide.FS.writeFile(pfad, inhalt);
  }
}

/**
 * Setzt das Übersetzte vom letzten Besuch an seinen Ort, bevor Python den
 * Kern einbindet, und gibt zurück, wie viele Dateien es waren. Ohne Speicher
 * -- `caches` gibt es nur über https und auf dem eigenen Rechner -- oder ohne
 * Stück: keine, und Python übersetzt wie sonst.
 */
async function uebersetztesEinsetzen(pyodide, schluessel) {
  if (!self.caches) return 0;
  try {
    const gespeichert = await (await caches.open(UEBERSETZT)).match(schluessel);
    if (!gespeichert) return 0;
    pyodide.FS.writeFile(STUECK, new Uint8Array(await gespeichert.arrayBuffer()));
    return pyodide.pyimport('opencivil.web.uebersetzt').einsetzen(STUECK, EINHAENGEPUNKT);
  } catch (ursache) {
    console.warn('Das Übersetzte vom letzten Besuch ist nicht lesbar; Python übersetzt neu.', ursache);
    return 0;
  }
}

/** Packt das Übersetzte und legt es ab -- nur, wenn sich etwas geändert hat. */
async function uebersetztesAblegen(pyodide, schluessel) {
  if (!self.caches) return;
  try {
    if (!pyodide.pyimport('opencivil.web.uebersetzt').packen(STUECK, EINHAENGEPUNKT)) return;
    await (await caches.open(UEBERSETZT)).put(schluessel, new Response(pyodide.FS.readFile(STUECK)));
  } catch (ursache) {
    console.warn('Das Übersetzte ist nicht abgelegt; der nächste Start übersetzt neu.', ursache);
  }
}

/**
 * Python laden, den Kern einhängen, den Dienst einbinden -- und melden, dass
 * es geht. Die Quellen kommen nebenher, während Python lädt: erst zum
 * Einhängen braucht es Python.
 */
async function starten(adresse, modul) {
  melden({ art: 'fortschritt', text: 'Python wird geladen …' });
  // Wann jeder Schritt fertig war -- die Seite schreibt es in die Konsole.
  const zeiten = {};
  const quellen = quellenHolen(adresse).then((dateien) => {
    zeiten['Quellen geholt'] = jetzt();
    return dateien;
  });
  // Scheitert das Holen, während Python noch lädt, gilt es erst, wenn auf die
  // Quellen gewartet wird -- und wird dort gemeldet, nicht vorher als
  // unbehandelt.
  quellen.catch(() => {});

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
  zeiten['Python geladen'] = jetzt();

  melden({ art: 'fortschritt', text: 'Rechenkern wird eingelesen …' });
  const dateien = await quellen;
  quellenEinhaengen(pyodide, dateien);

  // Python soll das Übersetzte schreiben: es kommt in den Speicher (oben).
  pyodide.runPython(`
import sys
if ${JSON.stringify(EINHAENGEPUNKT)} not in sys.path:
    sys.path.insert(0, ${JSON.stringify(EINHAENGEPUNKT)})
sys.dont_write_bytecode = False
`);
  // Nur ein Name im Speicher, keine Datei auf dem Server.
  const schluessel = new URL(`../kern/uebersetzt/${modul}`, import.meta.url).href;
  const uebersetzt = await uebersetztesEinsetzen(pyodide, schluessel);
  if (uebersetzt) zeiten['Übersetztes eingesetzt'] = jetzt();

  let dienst;
  try {
    dienst = pyodide.pyimport(modul);
  } catch (ursache) {
    throw startfehler(`${modul} nicht einbindbar.`, String(ursache));
  }

  zeiten['Kern eingelesen'] = jetzt();
  setTimeout(() => uebersetztesAblegen(pyodide, schluessel), ABLEGEN_NACH_MS);
  const fassung = pyodide.runPython('import sys; sys.version.split()[0]');
  const davon = uebersetzt ? `, ${uebersetzt} übersetzt vom letzten Besuch` : '';
  console.info(`${modul} bereit: Python ${fassung} über Pyodide, ${dateien.length} Dateien${davon}.`);
  melden({ art: 'bereit', fassung, zeiten });
  return dienst;
}

/** Versprechen auf den Dienst, gesetzt mit der Startnachricht; `null`, wenn der Start scheitert. */
let dienstBereit;

/**
 * Die erste Nachricht startet: `{art: 'start', quellen, modul}`. Jede
 * weitere ist eine Anfrage: `{nr, name, rumpf}`, der Rumpf schon als JSON.
 * Hinein und heraus geht JSON -- genau wie über HTTP; so bekommt die
 * Oberfläche auf beiden Wegen dieselben Daten, bis aufs Zeichen. Der Reihe
 * nach, weil Python in diesem Faden eines nach dem anderen tut. Die Antwort
 * wird abgewartet: die Konsole lädt erst Pakete, bevor sie ausführt.
 */
self.onmessage = async ({ data }) => {
  if (data.art === 'start') {
    dienstBereit = starten(data.quellen, data.modul).catch((fehler) => {
      melden({ art: 'gescheitert', meldung: fehler.message, spur: fehler.spur || '' });
      return null;
    });
    return;
  }
  const { nr, name, rumpf } = data;
  const dienst = await dienstBereit;
  if (!dienst) return;   // Der Start ist gescheitert; das ist schon gemeldet.
  try {
    melden({ art: 'antwort', nr, roh: await dienst.bearbeite_json(name, rumpf) });
  } catch (ursache) {
    // Hierher kommt nur, was bearbeite_json selbst umbringt -- der Dienst
    // fängt sonst alles ab und gibt es als Antwort zurück.
    melden({ art: 'antwort', nr, absturz: String(ursache) });
  }
};
