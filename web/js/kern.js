/**
 * kern.js -- Der Rechenkern im Browser, in Python.
 *
 * Startet Pyodide (Python als WebAssembly) mit den Quelldateien aus
 * `opencivil/` und ruft darin `opencivil.web.dienst.bearbeite_json` auf.
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
 * EIN EIGENER FADEN:
 * Python läuft in einem Web Worker (`kern_arbeiter.js`). Im selben Faden wie
 * die Oberfläche hielt jeder Aufruf die Seite an -- beim Beispiel für
 * Zehntelsekunden, bei der Dickensuche einer Platte mit allen Nachweisen für
 * bis zu eine halbe Minute. Hier bleibt die Vermittlung: jede Anfrage bekommt
 * eine Nummer, und die Antwort mit derselben Nummer löst ihr Versprechen ein.
 */

export class KernFehler extends Error {
  constructor(meldung, spur = '') {
    super(meldung);
    this.name = 'KernFehler';
    this.spur = spur;
  }
}

/**
 * Startet Python in einem eigenen Faden und liefert eine Schnittstelle zum
 * Rechendienst, sobald er bereit ist.
 *
 * @param {(text: string) => void} [fortschritt]  bekommt kurze Standmeldungen
 * @returns {Promise<{ruf: Function, art: string, fassung: string}>}
 */
export function kernStarten(fortschritt = () => {}) {
  const arbeiter = new Worker(new URL('./kern_arbeiter.js', import.meta.url),
    { type: 'module' });
  /** Nummer der Anfrage -> ihr Versprechen, bis die Antwort da ist. */
  const offen = new Map();
  let nummer = 0;

  /**
   * Führt eine Anfrage im Kern aus. Hinein und heraus geht JSON -- genau wie
   * über HTTP, damit die Oberfläche auf beiden Wegen dieselben Daten bekommt.
   */
  function ruf(name, rumpf = {}) {
    return new Promise((aufloesen, ablehnen) => {
      nummer += 1;
      offen.set(nummer, { aufloesen, ablehnen });
      arbeiter.postMessage({ nr: nummer, name, rumpf: JSON.stringify(rumpf) });
    });
  }

  function beantworten({ nr, roh, absturz }) {
    const anfrage = offen.get(nr);
    offen.delete(nr);
    if (!anfrage) return;
    if (absturz !== undefined) {
      anfrage.ablehnen(new KernFehler(`Rechenkern abgebrochen: ${absturz}`, absturz));
      return;
    }
    const umschlag = JSON.parse(roh);
    if (umschlag.status >= 400) {
      anfrage.ablehnen(new KernFehler(
        umschlag.daten.fehler || `Fehler ${umschlag.status}`, umschlag.daten.spur));
    } else {
      anfrage.aufloesen(umschlag.daten);
    }
  }

  return new Promise((bereit, gescheitert) => {
    arbeiter.onmessage = ({ data }) => {
      if (data.art === 'antwort') beantworten(data);
      else if (data.art === 'fortschritt') fortschritt(data.text);
      else if (data.art === 'bereit') {
        fortschritt('');
        bereit({ ruf, art: 'pyodide', fassung: data.fassung });
      } else if (data.art === 'gescheitert') {
        gescheitert(new KernFehler(data.meldung, data.spur));
      }
    };
    // Stirbt der Faden selbst -- etwa weil die Datei fehlt --, dann für alle,
    // die noch warten: niemand soll auf eine Antwort warten, die nicht kommt.
    arbeiter.onerror = (ereignis) => {
      const fehler = new KernFehler(
        `Rechenkern abgestürzt: ${ereignis.message || 'Faden nicht startbar'}`);
      gescheitert(fehler);
      for (const { ablehnen } of offen.values()) ablehnen(fehler);
      offen.clear();
    };
  });
}
