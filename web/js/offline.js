/**
 * offline.js -- Die Seite auch ohne Netz.
 *
 * Wo im Browser gerechnet wird -- auf GitHub Pages --, meldet die Seite den
 * Service Worker an (`sw.js` im Wurzelverzeichnis). Er legt in einen Speicher,
 * was sie zum Starten braucht; danach geht sie auch ohne Netz auf, und
 * schneller. Erst wenn der Kern bereit ist: beim ersten Besuch holt er sonst
 * dieselben 18 MB ein zweites Mal, gleichzeitig mit der Seite.
 *
 * Rechnet ein Server (`python3 start_ui.py`), braucht es ihn nicht -- und er
 * stünde beim Entwickeln im Weg: eine geänderte Datei, deren Marke noch die
 * alte ist, käme aus seinem Speicher. Darum meldet die Seite dort einen ab,
 * der noch angemeldet ist.
 */

/** @param {boolean} imBrowser  ob der Kern im Browser rechnet und nicht auf einem Server */
export function offlineEinrichten(imBrowser) {
  const dienst = navigator.serviceWorker;
  if (!dienst) return;   // ohne sicheren Ursprung, oder ein Browser ohne
  if (imBrowser) {
    dienst.register(new URL('../../sw.js', import.meta.url)).catch((fehler) => {
      console.warn('Ohne Netz geht die Seite nicht auf:', fehler);
    });
  } else {
    dienst.getRegistrations().then((alle) => alle.forEach((r) => r.unregister()));
  }
}
