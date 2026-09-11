/**
 * ablage.js -- Wo die Eingaben bleiben.
 *
 * Drei Wege, und alle drei mit derselben Beschreibung: dem JSON, das
 * `Projekt.als_dict()` im Kern liefert.
 *
 *   1. Im Browser. Jede Änderung landet im localStorage, das Fenster darf
 *      also zugehen. Das ist kein Speichern im eigentlichen Sinn -- es ist
 *      das Netz darunter.
 *   2. Als Datei auf die Platte, über den Download des Browsers.
 *   3. Von der Platte zurück, über einen Dateiwähler.
 *
 * GEPRÜFT WIRD IM KERN:
 * Was aus der Ablage oder von der Platte kommt, geht durch `api.pruefen()` --
 * also durch `Projekt.aus_dict()` in Python. Damit greifen dieselbe Umwandlung
 * alter Formate und dieselben Prüfungen wie überall sonst. Eine zweite,
 * nachgebaute Prüfung in JavaScript gäbe es hier fast geschenkt, und sie wäre
 * genau darum falsch: sie würde irgendwann von der echten abweichen.
 */

import { api } from './api.js';

const SCHLUESSEL = 'opencivil.projekt';

// ===========================================================================
// Browser
// ===========================================================================

/**
 * Legt die Beschreibung im Browser ab. Scheitert still -- es ist nur das Netz.
 *
 * `gesichert` merkt sich, ob dieser Stand schon als Datei auf der Platte liegt.
 * Dadurch stimmt der Punkt am Speichern-Knopf auch nach einem Neuladen noch:
 * ohne diese Notiz sähe jeder frisch geöffnete Tab so aus, als wäre alles
 * gesichert -- und das wäre schlicht gelogen.
 */
export function imBrowserAblegen(projekt, gesichert = false) {
  try {
    localStorage.setItem(SCHLUESSEL, JSON.stringify(
      { fassung: 1, gesichert, projekt }));
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
 * @returns {{projekt: Object, gesichert: boolean}|null}
 */
export function ausDemBrowser() {
  try {
    const roh = localStorage.getItem(SCHLUESSEL);
    if (!roh) return null;
    const inhalt = JSON.parse(roh);
    // Ohne Umschlag ist es eine Ablage aus der Zeit vor dieser Notiz --
    // dann gilt der Stand als ungesichert, was die vorsichtigere Annahme ist.
    return inhalt?.fassung === 1
      ? { projekt: inhalt.projekt, gesichert: !!inhalt.gesichert }
      : { projekt: inhalt, gesichert: false };
  } catch (fehler) {
    console.warn('Die Ablage im Browser ist unlesbar:', fehler);
    return null;
  }
}

export function ablageLeeren() {
  try {
    localStorage.removeItem(SCHLUESSEL);
  } catch {
    /* egal */
  }
}

/**
 * Holt die Beschreibung, mit der die Oberfläche startet.
 *
 * Erst der Browser, sonst das Beispiel. Ist das Abgelegte unbrauchbar, sagt
 * der Kern warum -- dann kommt das Beispiel, und der Grund wird gemeldet.
 *
 * @returns {Promise<{projekt: Object, gesichert: boolean,
 *                    herkunft: 'ablage'|'beispiel', hinweis: string}>}
 */
export async function projektHolen() {
  const abgelegt = ausDemBrowser();
  if (abgelegt) {
    try {
      const { projekt } = await api.pruefen(abgelegt.projekt);
      return {
        projekt, gesichert: abgelegt.gesichert, herkunft: 'ablage', hinweis: '',
      };
    } catch (fehler) {
      // Nicht löschen: vielleicht lässt es sich noch retten, und ein
      // stillschweigend geleerter Speicher wäre das schlechtere Ergebnis.
      return {
        projekt: await api.beispiel(),
        gesichert: true,
        herkunft: 'beispiel',
        hinweis: `Das abgelegte Projekt liess sich nicht lesen (${fehler.message}). `
               + 'Es wurde nicht gelöscht; die Oberfläche startet mit dem Beispiel.',
      };
    }
  }
  return {
    projekt: await api.beispiel(), gesichert: true,
    herkunft: 'beispiel', hinweis: '',
  };
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
 * Bietet die Beschreibung als .json zum Herunterladen an.
 *
 * Eingerückt geschrieben: die Datei soll sich lesen und in einer Versions-
 * verwaltung vernünftig vergleichen lassen, nicht bloss klein sein.
 */
export function alsDateiSichern(projekt) {
  const text = JSON.stringify(projekt, null, 2);
  const adresse = URL.createObjectURL(
    new Blob([text], { type: 'application/json' }));

  const verweis = document.createElement('a');
  verweis.href = adresse;
  verweis.download = `${dateiname(projekt.name)}.json`;
  document.body.append(verweis);
  verweis.click();
  verweis.remove();
  // Erst freigeben, wenn der Browser den Download angenommen hat.
  setTimeout(() => URL.revokeObjectURL(adresse), 30000);

  // Dieser Stand liegt jetzt auf der Platte -- das merkt sich die Ablage, damit
  // der Punkt am Speichern-Knopf auch morgen noch die Wahrheit sagt.
  imBrowserAblegen(projekt, true);

  return verweis.download;
}

/**
 * Lässt eine Datei wählen und gibt die geprüfte Beschreibung zurück.
 *
 * @returns {Promise<Object|null>} null, wenn abgebrochen wurde
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
        const { projekt } = await api.pruefen(roh);
        erfuellen(projekt);
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
