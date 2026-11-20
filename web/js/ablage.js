/**
 * ablage.js -- Wo die Eingaben bleiben.
 *
 * Drei Wege, und alle drei mit derselben Beschreibung: dem JSON, das
 * `Mappe.als_dict()` im Kern liefert -- alle Projekte zusammen,
 * `{projekte: [...]}`.
 *
 *   1. Im Browser. Jede Änderung landet im localStorage, das Fenster darf
 *      also zugehen. Das ist kein Speichern im eigentlichen Sinn -- es ist
 *      das Netz darunter. Dazu, welches Projekt gezeigt war. Die Sandboxen
 *      beginnen beim Laden der Seite trotzdem neu (Benutzer, 2026-11-20).
 *   2. Als Datei auf die Platte, über den Download des Browsers.
 *   3. Von der Platte zurück, über einen Dateiwähler. Eine Datei mit einem
 *      einzelnen Projekt, wie bis 2026-11-20 gespeichert, liest der Kern als
 *      Mappe mit diesem einen.
 *
 * GEPRÜFT WIRD IM KERN:
 * Was aus der Ablage oder von der Platte kommt, geht durch
 * `api.mappeOeffnen()` -- also durch `Mappe.aus_dict()` in Python. Damit
 * greifen dieselben Prüfungen wie überall sonst. Eine zweite, nachgebaute
 * Prüfung in JavaScript gäbe es hier fast geschenkt, und sie wäre genau
 * darum falsch: sie würde irgendwann von der echten abweichen.
 *
 * WAS SICH NICHT ÖFFNEN LÄSST, BLEIBT:
 * Lehnt der Kern den abgelegten Stand ab -- oder ist er gar kein JSON --,
 * startet die Oberfläche mit dem Beispiel. Die erste Änderung legt das
 * Beispiel auf denselben Platz; darum wird der Stand vorher als Rohtext unter
 * eigenem Schlüssel aufbewahrt, bis der Benutzer ihn herunterlädt oder
 * verwirft (`gerettete`). Bis 2026-10-17 hiess es hier «Nicht gelöscht», und
 * die erste Änderung löschte ihn doch.
 */

import { api } from './api.js';

const SCHLUESSEL = 'opencivil.mappe';

/**
 * Bis 2026-11-20 lag im Browser ein einzelnes Projekt, unter diesem
 * Schlüssel. Fehlt die Mappe, wird es ihr erstes Projekt; sobald sie
 * abgelegt ist, geht er weg.
 */
const FRUEHER = 'opencivil.projekt';

/** Die Stände, die sich nicht öffnen liessen -- eine Liste, als Rohtext. */
const GERETTET = 'opencivil.projekt.unlesbar';

/**
 * Was sich nicht öffnen liess und im Browser nicht aufbewahrt werden konnte
 * (voller Speicher). Solange etwas darin steht, legt die Ablage nichts ab:
 * sie überschriebe den einzigen Stand.
 */
const nichtAufbewahrt = [];

// ===========================================================================
// Browser
// ===========================================================================

/**
 * Legt die Mappe im Browser ab, mit der Stelle des gezeigten Projekts
 * (`gewaehlt`). Scheitert still -- es ist nur das Netz.
 *
 * `gesichert` merkt sich, ob dieser Stand schon als Datei auf der Platte liegt.
 * Dadurch stimmt der Punkt am Speichern-Knopf auch nach einem Neuladen noch:
 * ohne diese Notiz sähe jeder frisch geöffnete Tab so aus, als wäre alles
 * gesichert -- und das wäre schlicht gelogen.
 */
export function imBrowserAblegen(mappe, gewaehlt, gesichert) {
  if (nichtAufbewahrt.length) return false;
  try {
    localStorage.setItem(SCHLUESSEL, JSON.stringify(
      { fassung: 1, gesichert, gewaehlt, mappe }));
    localStorage.removeItem(FRUEHER);
    return true;
  } catch (fehler) {
    // Privater Modus oder voller Speicher. Kein Grund, die Arbeit anzuhalten;
    // auf die Platte kommt es ohnehin erst mit "Speichern".
    console.warn('Ablegen im Browser nicht möglich:', fehler);
    return false;
  }
}

/**
 * Was im Browser liegt -- oder null. Wirft nicht.
 *
 * Dabei steht immer der Rohtext, wie er dalag: lässt sich der Stand nicht
 * öffnen, wird genau er aufbewahrt. Ist er kein JSON, sagt `fehler` es.
 * Liegt nur das einzelne Projekt von früher da, ist `mappe` dieses Projekt:
 * der Kern liest es als Mappe mit ihm.
 *
 * @returns {{roh: string, mappe?: Object, gewaehlt?: number, gesichert?: boolean,
 *   fehler?: string}|null}
 */
export function ausDemBrowser() {
  let roh;
  let frueher = false;
  try {
    roh = localStorage.getItem(SCHLUESSEL);
    if (!roh) {
      roh = localStorage.getItem(FRUEHER);
      frueher = true;
    }
  } catch (fehler) {
    console.warn('Die Ablage im Browser ist nicht erreichbar:', fehler);
    return null;
  }
  if (!roh) return null;
  try {
    const inhalt = JSON.parse(roh);
    return frueher
      ? { roh, mappe: inhalt?.projekt, gewaehlt: 0, gesichert: !!inhalt?.gesichert }
      : { roh, mappe: inhalt?.mappe, gewaehlt: inhalt?.gewaehlt, gesichert: !!inhalt?.gesichert };
  } catch (fehler) {
    return { roh, fehler: `Kein lesbares JSON (${fehler.message}).` };
  }
}

/** Die aufbewahrten Stände im Browser -- leer, wenn es keine gibt. */
function aufbewahrte() {
  try {
    const liste = JSON.parse(localStorage.getItem(GERETTET) || '[]');
    return Array.isArray(liste) ? liste : [];
  } catch {
    return [];
  }
}

/**
 * Bewahrt einen Stand auf, der sich nicht öffnen liess -- bevor irgendetwas
 * seinen Platz überschreibt. Derselbe Rohtext steht nur einmal da. Gelingt
 * es nicht, bleibt er im Speicher der Seite, und die Ablage schreibt nichts
 * mehr, bis er verworfen ist.
 */
function retten(roh, grund) {
  const eintrag = { zeit: new Date().toISOString(), grund, roh };
  try {
    const liste = aufbewahrte();
    if (liste.some((e) => e.roh === roh)) return;
    localStorage.setItem(GERETTET, JSON.stringify([...liste, eintrag]));
  } catch (fehler) {
    console.warn('Der unlesbare Stand liess sich im Browser nicht aufbewahren:', fehler);
    nichtAufbewahrt.push(eintrag);
  }
}

/**
 * Die Stände, die sich nicht öffnen liessen, älteste zuerst. `aufbewahrt`
 * sagt, ob einer im Browser liegt oder nur in dieser Seite.
 *
 * @returns {Array<{zeit: string, grund: string, roh: string, aufbewahrt: boolean}>}
 */
export function gerettete() {
  return [
    ...aufbewahrte().map((e) => ({ ...e, aufbewahrt: true })),
    ...nichtAufbewahrt.map((e) => ({ ...e, aufbewahrt: false })),
  ];
}

/** Bietet einen geretteten Stand als Datei an -- unverändert, wie er dalag. */
export function geretteteHerunterladen(eintrag) {
  let name = '';
  try {
    const inhalt = JSON.parse(eintrag.roh);
    name = (inhalt?.mappe?.projekte?.[0] ?? inhalt?.projekt ?? inhalt)?.name || '';
  } catch {
    /* kein JSON: dann ohne Namen */
  }
  const zeit = eintrag.zeit.slice(0, 16).replace(/[-:T]/g, '');
  herunterladen(eintrag.roh, `${dateiname(name)}-unlesbar-${zeit}.json`);
}

/** Verwirft einen geretteten Stand -- danach darf die Ablage wieder schreiben. */
export function geretteteVerwerfen(eintrag) {
  const i = nichtAufbewahrt.findIndex((e) => e.zeit === eintrag.zeit && e.roh === eintrag.roh);
  if (i >= 0) {
    nichtAufbewahrt.splice(i, 1);
    return;
  }
  try {
    const liste = aufbewahrte().filter((e) => e.zeit !== eintrag.zeit || e.roh !== eintrag.roh);
    if (liste.length) localStorage.setItem(GERETTET, JSON.stringify(liste));
    else localStorage.removeItem(GERETTET);
  } catch (fehler) {
    console.warn('Verwerfen nicht möglich:', fehler);
  }
}

/**
 * Holt die Mappe, mit der die Oberfläche startet, und welches ihrer
 * Projekte gezeigt war.
 *
 * Erst der Browser, sonst das Beispiel. Lässt sich das Abgelegte nicht
 * öffnen, wird es aufbewahrt (`gerettete`), bevor das Beispiel kommt -- die
 * Oberfläche zeigt es an, solange es da ist. Jede Sandbox beginnt neu.
 *
 * @returns {Promise<{mappe: Object, gewaehlt: number, gesichert: boolean}>}
 */
export async function mappeHolen() {
  const abgelegt = ausDemBrowser();
  if (!abgelegt) return beispiel();
  let grund = abgelegt.fehler;
  if (!grund) {
    try {
      const { mappe } = await api.mappeOeffnen(abgelegt.mappe, true);
      const { gewaehlt } = abgelegt;
      return {
        mappe,
        gewaehlt: Number.isInteger(gewaehlt) && gewaehlt < mappe.projekte.length ? gewaehlt : 0,
        gesichert: abgelegt.gesichert,
      };
    } catch (fehler) {
      grund = fehler.message;
    }
  }
  retten(abgelegt.roh, grund);
  return beispiel();
}

/** Die Mappe mit dem Beispiel des Kerns -- der Start, wenn nichts abgelegt ist. */
async function beispiel() {
  return { mappe: { projekte: [await api.beispiel()] }, gewaehlt: 0, gesichert: true };
}

// ===========================================================================
// Platte
// ===========================================================================

/** Macht aus einem Projektnamen einen brauchbaren Dateinamen. */
export function dateiname(name) {
  const gesaeubert = [...(name || '')]
    .map((z) => (/[\p{L}\p{N}\-_]/u.test(z) ? z : '_'))
    .join('')
    .replace(/_+/g, '_')
    .replace(/^_|_$/g, '');
  return gesaeubert || 'projekt';
}

/**
 * Bietet die Mappe als .json zum Herunterladen an: mit einem Projekt unter
 * seinem Namen, mit mehreren als «Projekte 2026-11-20».
 *
 * Eingerückt geschrieben: die Datei soll sich lesen und in einer Versions-
 * verwaltung vernünftig vergleichen lassen, nicht bloss klein sein.
 */
export function alsDateiSichern(mappe, gewaehlt) {
  const { projekte } = mappe;
  const heute = new Date();
  const datum = [heute.getFullYear(), heute.getMonth() + 1, heute.getDate()]
    .map((z) => String(z).padStart(2, '0')).join('-');
  const name = herunterladen(JSON.stringify(mappe, null, 2),
    `${dateiname(projekte.length === 1 ? projekte[0].name : `Projekte ${datum}`)}.json`);
  // Dieser Stand liegt jetzt auf der Platte -- das merkt sich die Ablage, damit
  // der Punkt am Speichern-Knopf auch morgen noch die Wahrheit sagt.
  imBrowserAblegen(mappe, gewaehlt, true);
  return name;
}

/** Bietet einen Text als Datei zum Herunterladen an und gibt ihren Namen zurück. */
function herunterladen(text, name) {
  const adresse = URL.createObjectURL(
    new Blob([text], { type: 'application/json' }));
  const verweis = document.createElement('a');
  verweis.href = adresse;
  verweis.download = name;
  document.body.append(verweis);
  verweis.click();
  verweis.remove();
  // Erst freigeben, wenn der Browser den Download angenommen hat.
  setTimeout(() => URL.revokeObjectURL(adresse), 30000);
  return name;
}

/**
 * Lässt eine Datei wählen und gibt die geprüfte Mappe zurück, mit dem Namen
 * der Datei.
 *
 * @returns {Promise<{mappe: Object, datei: string}|null>} null, wenn abgebrochen wurde
 */
export function ausDateiLaden() {
  return new Promise((erfuellen, ablehnen) => {
    const waehler = document.createElement('input');
    waehler.type = 'file';
    waehler.accept = 'application/json,.json';

    waehler.addEventListener('change', async () => {
      const datei = waehler.files?.[0];
      waehler.remove();
      if (!datei) return erfuellen(null);

      try {
        const roh = JSON.parse(await datei.text());
        // Die Sandboxen wie gespeichert; fehlt eine, legt der Kern sie an.
        const { mappe } = await api.mappeOeffnen(roh);
        erfuellen({ mappe, datei: datei.name });
      } catch (fehler) {
        ablehnen(new Error(
          `«${datei.name}» ist keine brauchbare Projektdatei: ${fehler.message}`));
      }
    });

    // Bricht der Benutzer den Dateiwähler ab, kommt gar kein Ereignis -- in
    // den meisten Browsern jedenfalls. Das Versprechen bliebe dann offen, was
    // niemandem schadet: es hängt keine Sperre daran.
    waehler.addEventListener('cancel', () => {
      waehler.remove();
      erfuellen(null);
    });

    document.body.append(waehler);
    waehler.click();
  });
}
