/**
 * api.js -- Zugriff auf den Rechenkern.
 *
 * Die Oberfläche rechnet nichts. Sie schickt die Projektbeschreibung hin und
 * bekommt Werte, Herleitung und Urteile zurück -- fertig formatiert und als
 * fertige LaTeX-Zeichenketten. Das ist der ganze Vertrag.
 *
 * ZWEI WEGE ZUM SELBEN KERN:
 * Läuft `python3 start_ui.py`, geht die Anfrage über HTTP an das dortige
 * CPython. Sonst -- etwa auf GitHub Pages, wo es keinen Server gibt -- startet
 * `kern.js` Python im Browser. Beide Wege landen in derselben Funktion
 * `opencivil.web.dienst.bearbeite_json`; die Oberfläche merkt keinen
 * Unterschied und darf keinen merken.
 *
 * Welcher Weg es wird, entscheidet ein einziger Versuch: antwortet ein Server,
 * nehmen wir ihn (er startet ohne Ladezeit und kann PDF). Antwortet keiner,
 * rechnet der Browser selbst.
 */

import { kernStarten, KernFehler } from './kern.js';

/** Das Projektverzeichnis, von dieser Datei aus gesehen (web/js/ -> ../../). */
const WURZEL = new URL('../../', import.meta.url);

/** Wie lange auf einen Server gewartet wird, bevor Pyodide übernimmt. */
const PROBE_MS = 1500;

let kern = null;

// ===========================================================================
// Weg 1: ein laufender Server
// ===========================================================================

async function ueberHttp(name, rumpf = {}) {
  let antwort;
  try {
    antwort = await fetch(new URL(`api/${name}`, WURZEL), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(rumpf),
    });
  } catch (ursache) {
    throw new KernFehler('Der Rechenkern ist nicht erreichbar.', String(ursache));
  }

  const text = await antwort.text();
  let daten;
  try {
    daten = text ? JSON.parse(text) : {};
  } catch {
    throw new KernFehler(
      `Unlesbare Antwort (${antwort.status})`, text.slice(0, 500));
  }
  if (!antwort.ok) {
    throw new KernFehler(daten.fehler || `Fehler ${antwort.status}`, daten.spur);
  }
  return daten;
}

/** Horcht kurz, ob ein Server da ist. Wirft nie -- liefert nur ja oder nein. */
async function serverDa() {
  const abbruch = new AbortController();
  const uhr = setTimeout(() => abbruch.abort(), PROBE_MS);
  try {
    const antwort = await fetch(new URL('api/katalog', WURZEL), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: '{}',
      signal: abbruch.signal,
    });
    if (!antwort.ok) return false;
    // GitHub Pages antwortet auf alles -- notfalls mit einer 404-Seite in HTML.
    // Erst wenn wirklich der Katalog zurückkommt, ist es unser Server.
    const daten = await antwort.json();
    return Array.isArray(daten.betonsorten);
  } catch {
    return false;
  } finally {
    clearTimeout(uhr);
  }
}

// ===========================================================================
// Start
// ===========================================================================

/**
 * Sucht den Rechenkern und macht ihn bereit. Muss vor jedem Aufruf laufen.
 *
 * @param {(text: string) => void} [fortschritt]
 * @returns {Promise<{art: 'server'|'pyodide', beschriftung: string}>}
 */
export async function kernBereitstellen(fortschritt = () => {}) {
  fortschritt('Rechenkern wird gesucht …');

  if (await serverDa()) {
    kern = { ruf: ueberHttp, art: 'server' };
    fortschritt('');
    return { art: 'server', beschriftung: 'Kern: lokaler Server' };
  }

  const imBrowser = await kernStarten(fortschritt);
  kern = imBrowser;
  return {
    art: 'pyodide',
    beschriftung: `Kern: Python ${imBrowser.fassung} im Browser`,
  };
}

function ruf(name, rumpf) {
  if (kern === null) {
    throw new KernFehler('Der Rechenkern ist noch nicht bereit.');
  }
  // Der Server antwortet mit einem Versprechen, Pyodide unmittelbar --
  // Promise.resolve bügelt den Unterschied glatt, damit die Oberfläche
  // durchgehend mit await arbeiten kann.
  return Promise.resolve(kern.ruf(name, rumpf));
}

/** Ob gerade im Browser gerechnet wird (statt auf einem Server). */
export function rechnetImBrowser() {
  return kern?.art === 'pyodide';
}

export const api = {
  katalog: () => ruf('katalog', {}),
  /** Das Beispielprojekt -- der Start, wenn nichts abgelegt ist. */
  beispiel: () => ruf('beispiel', {}),
  /** Prüft eine Beschreibung (aus der Ablage oder aus einer Datei). */
  pruefen: (projekt) => ruf('pruefen', { projekt }),
  rechnen: (projekt, ziele) => ruf('rechnen', { projekt, ziele }),
  alles: (projekt) => ruf('alles', { projekt }),
  ziele: (projekt) => ruf('ziele', { projekt }),
  /** M-V-Kurven für selbst gewählte Normalkräfte: {Kennung: N_Ed in kN}. */
  querkraftkurven: (projekt, n_ed) => ruf('querkraftkurven', { projekt, n_ed }),
  bericht: (projekt, ziele) => ruf('bericht', { projekt, ziele }),
  /** Sucht die kleinste Bewehrung und gibt das geänderte Projekt zurück. */
  bewehrungSuchen: (projekt, kennung) =>
    ruf('bewehrung_suchen', { projekt, kennung }),
};

export { KernFehler };
