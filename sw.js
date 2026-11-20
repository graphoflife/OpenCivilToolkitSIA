/**
 * sw.js -- Die Seite auch ohne Netz: ein Service Worker.
 *
 * Wer die Seite einmal geöffnet hat, öffnet sie danach auch ohne Netz -- und
 * schneller: was sie zum Starten braucht, liegt in einem Speicher des
 * Browsers (Cache Storage) und kommt von dort, ohne zu fragen. Gerechnet wird
 * ohnehin im Browser. Angemeldet wird er von `web/js/offline.js`, nur wo kein
 * Server rechnet.
 *
 * Er liegt im Wurzelverzeichnis, nicht unter web/: ein Service Worker gilt
 * nur für Seiten unter seinem Ordner, und auch die Wurzel soll ohne Netz
 * aufgehen -- sie ist die veröffentlichte Adresse und leitet auf web/ weiter.
 *
 * WAS WOHER KOMMT:
 * - Was eine Marke trägt (`?v=…`): aus dem Speicher. Eine geänderte Datei
 *   hat eine neue Marke, also eine neue Adresse; eine alte Fassung kann so
 *   nie kommen.
 * - Was unter web/vendor/ liegt -- Pyodide, KaTeX, die Schrift --: aus dem
 *   Speicher, je Ordner einem, benannt nach der Marke seines Inhalts. Eine
 *   Veröffentlichung, die Pyodide nicht anrührt, lässt seine 13 MB liegen.
 * - Die Seiten selbst, das Manifest und das Zeichen: zuerst aus dem Netz,
 *   ohne Netz aus dem Speicher. So kommt nach einer Veröffentlichung die neue
 *   Seite mit den neuen Marken.
 * - Das Notizbuch ebenso; in den Speicher kommt eine Seite, sobald man sie
 *   einmal geöffnet hat.
 * - Alles andere, etwa die Anfragen an einen Server: wie ohne ihn.
 *
 * NEUE FASSUNG:
 * Was in den Speicher gehört, schreibt die Brücke unten zwischen die beiden
 * Kommentare (`opencivil/web/bruecke.py`). Ändert sich etwas, ändert sich
 * diese Datei, und der Browser installiert sie neu: sie legt nach, was
 * fehlt, und räumt weg, was nicht mehr dazugehört. Nur ihre eigenen Speicher
 * (`opencivil-…`): auf github.io teilen sich alle Seiten eines Kontos einen
 * Ursprung, und damit die Speicher. Einen davon füllt der Faden des Kerns
 * selbst, mit dem, was Python übersetzt hat (`web/js/kern_arbeiter.js`).
 */

// Versionsmarken: geschrieben von «python3 -m opencivil.web.bruecke», nicht von Hand ändern
const VORRAT = {
  "seiten": [
    "./",
    "web/",
    "web/manifest.webmanifest",
    "web/favicon.svg"
  ],
  "dateien": [
    "web/css/10-grundlage.css?v=db6a0e46496a",
    "web/css/20-seite.css?v=f4bc09e7c470",
    "web/css/30-eingaben.css?v=bf3c5c1c4c64",
    "web/css/40-bericht.css?v=c59f9e849747",
    "web/css/50-schmal.css?v=7dd2e94f221d",
    "web/css/60-zeichenfenster.css?v=5dc76e64b43f",
    "web/css/70-notizbuch.css?v=5714743196a8",
    "web/css/80-skizzen.css?v=09325f7bf052",
    "web/css/90-python.css?v=bec24d055c16",
    "web/js/ablage.js?v=2cff59319161",
    "web/js/achsen.js?v=aced8f358043",
    "web/js/api.js?v=e90276978a0c",
    "web/js/app.js?v=4c3c18267cf6",
    "web/js/apps.js?v=209ea3e93879",
    "web/js/arten.js?v=901a5bbbd1ab",
    "web/js/balkensystem.js?v=a69906b3f5ca",
    "web/js/baum.js?v=97b983cbbf34",
    "web/js/bausteine.js?v=3f4474bf5a3d",
    "web/js/bericht.js?v=fccd0b6a0101",
    "web/js/bewehrungssuche.js?v=2582eafd0f54",
    "web/js/bs_diagramme.js?v=b94694de6703",
    "web/js/bs_eigenschaften.js?v=a234c29f8f4d",
    "web/js/bs_symbole.js?v=2de8f1220c79",
    "web/js/bs_teile.js?v=b071f2e79591",
    "web/js/bs_texte.js?v=7222ee764a0f",
    "web/js/bs_zeichnung.js?v=cbe0ecf1f9ad",
    "web/js/cad_ansicht.js?v=bb6d2920530a",
    "web/js/cad_app.js?v=5d0bcf43880d",
    "web/js/cad_auswahl.js?v=e6d55150be42",
    "web/js/cad_befehle.js?v=57f736dd693a",
    "web/js/cad_eingabe.js?v=9d6c86ab188b",
    "web/js/cad_fenster.js?v=380134243493",
    "web/js/cad_modell.js?v=50d977829c8e",
    "web/js/cad_palette.js?v=093d67d4548d",
    "web/js/cad_raum.js?v=2ef16c41d520",
    "web/js/cad_verlauf.js?v=7603b772b8be",
    "web/js/decke.js?v=ea8095699950",
    "web/js/diagramm.js?v=2b56ba98c6b5",
    "web/js/dk_eigenschaften.js?v=7bcd9ef19de8",
    "web/js/dk_ergebnis.js?v=05988feaa2cb",
    "web/js/dk_grundriss.js?v=99d63c3c5697",
    "web/js/dk_schnitt.js?v=1cc553f65830",
    "web/js/dk_zeichnung.js?v=618ccb6403bb",
    "web/js/dom.js?v=77e2ae9b8099",
    "web/js/ds_grundriss.js?v=a6eb3f49f942",
    "web/js/ds_zeichnung.js?v=232bf46b0015",
    "web/js/durchstanzen.js?v=10bb84202adb",
    "web/js/eb_zeichnung.js?v=f3972b138b6e",
    "web/js/editor.js?v=97f3abad7a0d",
    "web/js/erdbeben.js?v=d83b4f1b07f3",
    "web/js/faelle.js?v=ba9d53707ce9",
    "web/js/fallantwort.js?v=cab91f08ea3e",
    "web/js/fenster.js?v=6e4ffffaa66c",
    "web/js/gb_skizze.js?v=4123c92f9fe4",
    "web/js/gb_zeichnung.js?v=6895f6dc6243",
    "web/js/grundbruch.js?v=959a960e9947",
    "web/js/kapitel.js?v=5943ba037490",
    "web/js/kern.js?v=68a4e9aaa723",
    "web/js/kern_arbeiter.js?v=ee8603262c6b",
    "web/js/konsole.js?v=25434f6b739d",
    "web/js/kopierleiste.js?v=2af7c8ead463",
    "web/js/lagen.js?v=d1de89b1b40b",
    "web/js/lastfaelle.js?v=68c0629d7657",
    "web/js/markdown.js?v=95b8ac3d60df",
    "web/js/material.js?v=2b0b6df5094e",
    "web/js/materialwahl.js?v=e65fae366d80",
    "web/js/mathe.js?v=f218656b8dbb",
    "web/js/nachweise.js?v=41504154e283",
    "web/js/notizbuch.js?v=90792350d729",
    "web/js/notizbuch_seite.js?v=639209806e79",
    "web/js/offline.js?v=1b6f6c615c08",
    "web/js/pf_verlauf.js?v=077aa49f7b6c",
    "web/js/pf_zeichnung.js?v=c3bcabe521ec",
    "web/js/pfahl.js?v=930816b6e1e2",
    "web/js/platte.js?v=4cf167228a53",
    "web/js/platte_bilder.js?v=12f4aa7c4c13",
    "web/js/plattenkapitel.js?v=f62212e054df",
    "web/js/projekte.js?v=4cf72047989c",
    "web/js/python.js?v=e36b207b3ea6",
    "web/js/qa_diagramme.js?v=0ab6cf606cb4",
    "web/js/qa_uebersicht.js?v=4754b00bc7eb",
    "web/js/qa_vorlagen.js?v=3c2ad6420088",
    "web/js/qa_zeichnung.js?v=ec26f8b1f6cf",
    "web/js/querschnittsanalyse.js?v=34e2b87d1c6e",
    "web/js/setzung.js?v=40745af6b5b4",
    "web/js/sinnbilder.js?v=425908683a4d",
    "web/js/spannungsbild.js?v=90450a9a0b05",
    "web/js/sz_zeichnung.js?v=8ce828560c47",
    "web/js/variablen.js?v=7d43b6f38cd9",
    "web/js/zeichnen.js?v=da6e8eec5dc8",
    "web/js/zustand.js?v=04a6b50b3e76",
    "web/kern/notizbuch.json?v=36443b3ff750",
    "web/kern/quellen.json?v=c921d07fe37b"
  ],
  "fremd": {
    "web/vendor/jetbrains-mono/": {
      "marke": "cd30e5f41e08",
      "dateien": [
        "web/vendor/jetbrains-mono/JetBrainsMono-Variable.woff2"
      ]
    },
    "web/vendor/katex/": {
      "marke": "f8d5d22b3057",
      "dateien": [
        "web/vendor/katex/fonts/KaTeX_AMS-Regular.woff2",
        "web/vendor/katex/fonts/KaTeX_Caligraphic-Bold.woff2",
        "web/vendor/katex/fonts/KaTeX_Caligraphic-Regular.woff2",
        "web/vendor/katex/fonts/KaTeX_Fraktur-Bold.woff2",
        "web/vendor/katex/fonts/KaTeX_Fraktur-Regular.woff2",
        "web/vendor/katex/fonts/KaTeX_Main-Bold.woff2",
        "web/vendor/katex/fonts/KaTeX_Main-BoldItalic.woff2",
        "web/vendor/katex/fonts/KaTeX_Main-Italic.woff2",
        "web/vendor/katex/fonts/KaTeX_Main-Regular.woff2",
        "web/vendor/katex/fonts/KaTeX_Math-BoldItalic.woff2",
        "web/vendor/katex/fonts/KaTeX_Math-Italic.woff2",
        "web/vendor/katex/fonts/KaTeX_SansSerif-Bold.woff2",
        "web/vendor/katex/fonts/KaTeX_SansSerif-Italic.woff2",
        "web/vendor/katex/fonts/KaTeX_SansSerif-Regular.woff2",
        "web/vendor/katex/fonts/KaTeX_Script-Regular.woff2",
        "web/vendor/katex/fonts/KaTeX_Size1-Regular.woff2",
        "web/vendor/katex/fonts/KaTeX_Size2-Regular.woff2",
        "web/vendor/katex/fonts/KaTeX_Size3-Regular.woff2",
        "web/vendor/katex/fonts/KaTeX_Size4-Regular.woff2",
        "web/vendor/katex/fonts/KaTeX_Typewriter-Regular.woff2",
        "web/vendor/katex/katex.min.css",
        "web/vendor/katex/katex.min.js"
      ]
    },
    "web/vendor/pyodide/": {
      "marke": "94b0be0c39de",
      "dateien": [
        "web/vendor/pyodide/pyodide-lock.json",
        "web/vendor/pyodide/pyodide.asm.mjs",
        "web/vendor/pyodide/pyodide.asm.wasm",
        "web/vendor/pyodide/pyodide.mjs",
        "web/vendor/pyodide/python_stdlib.zip"
      ]
    }
  }
};
// Ende der Versionsmarken

/** Dieser Ordner: alle Pfade in `VORRAT` gehen von ihm aus. */
const BASIS = new URL('./', self.location);

const VORSILBE = 'opencivil-';
const SPEICHER = {
  dateien: `${VORSILBE}dateien`,
  seiten: `${VORSILBE}seiten`,
  notizbuch: `${VORSILBE}notizbuch`,
  // Den füllt der Faden des Kerns; hier steht er, damit ihn das Aufräumen
  // stehen lässt.
  uebersetzt: `${VORSILBE}uebersetzt`,
};

const adresse = (pfad) => new URL(pfad, BASIS).href;

/** Der Speicher eines Ordners unter web/vendor/, benannt nach der Marke seines Inhalts. */
const fremdSpeicher = (ordner) => `${VORSILBE}${ordner.split('/').at(-2)}-${VORRAT.fremd[ordner].marke}`;

/** Unter welcher Adresse eine Seite im Speicher liegt: «web/index.html» ist «web/». */
const seitenSchluessel = (url) => url.origin + url.pathname.replace(/index\.html$/, '');

// ===========================================================================
// Installieren und aufräumen
// ===========================================================================

self.addEventListener('install', (ereignis) => {
  // Sofort an die Stelle des alten: der hat nichts, was die Seite noch braucht.
  ereignis.waitUntil(anlegen().then(() => self.skipWaiting()));
});

self.addEventListener('activate', (ereignis) => {
  ereignis.waitUntil(aufraeumen().then(() => self.clients.claim()));
});

/**
 * Legt in den Speicher, was dort fehlt -- die Seiten jedes Mal neu. Scheitert
 * eine Anfrage, scheitert die Installation, und der Browser versucht es beim
 * nächsten Besuch wieder: halb angelegt hiesse, ohne Netz fehlte etwas.
 */
async function anlegen() {
  const seiten = await caches.open(SPEICHER.seiten);
  await seiten.addAll(VORRAT.seiten.map(adresse));
  await nachlegen(SPEICHER.dateien, VORRAT.dateien);
  for (const [ordner, { dateien }] of Object.entries(VORRAT.fremd)) {
    await nachlegen(fremdSpeicher(ordner), dateien);
  }
}

async function nachlegen(name, pfade) {
  const speicher = await caches.open(name);
  const fehlt = [];
  for (const pfad of pfade) {
    if (!(await speicher.match(adresse(pfad)))) fehlt.push(adresse(pfad));
  }
  await speicher.addAll(fehlt);
}

/** Löscht die eigenen Speicher, die nicht mehr dazugehören, und die Dateien mit alten Marken. */
async function aufraeumen() {
  const gueltig = new Set([
    ...Object.values(SPEICHER), ...Object.keys(VORRAT.fremd).map(fremdSpeicher)]);
  for (const name of await caches.keys()) {
    if (name.startsWith(VORSILBE) && !gueltig.has(name)) await caches.delete(name);
  }
  const dateien = await caches.open(SPEICHER.dateien);
  const heute = new Set(VORRAT.dateien.map(adresse));
  for (const anfrage of await dateien.keys()) {
    if (!heute.has(anfrage.url)) await dateien.delete(anfrage);
  }
}

// ===========================================================================
// Anfragen
// ===========================================================================

self.addEventListener('fetch', (ereignis) => {
  const anfrage = ereignis.request;
  const url = new URL(anfrage.url);
  if (anfrage.method !== 'GET' || !url.href.startsWith(BASIS.href)) return;
  const pfad = url.pathname.slice(BASIS.pathname.length);
  const fremd = Object.keys(VORRAT.fremd).find((ordner) => pfad.startsWith(ordner));
  if (url.searchParams.has('v')) {
    ereignis.respondWith(ausDemSpeicher(ereignis, SPEICHER.dateien));
  } else if (fremd) {
    ereignis.respondWith(ausDemSpeicher(ereignis, fremdSpeicher(fremd)));
  } else if (anfrage.mode === 'navigate' || VORRAT.seiten.includes(pfad)) {
    ereignis.respondWith(ausDemNetz(ereignis, SPEICHER.seiten, seitenSchluessel(url)));
  } else if (pfad.startsWith('notizbuch/')) {
    ereignis.respondWith(ausDemNetz(ereignis, SPEICHER.notizbuch, url.href));
  }
});

/**
 * Legt eine Antwort in den Speicher, ohne sie aufzuhalten: die Seite bekommt
 * sie sofort, Stück für Stück, während die Kopie in den Speicher läuft --
 * Pyodide übersetzt seine 9.6 MB schon, während sie noch kommen.
 */
function ablegen(ereignis, speicher, schluessel, antwort) {
  if (antwort.ok) ereignis.waitUntil(speicher.put(schluessel, antwort.clone()));
  return antwort;
}

/** Aus dem Speicher; fehlt es dort, aus dem Netz -- und dann in den Speicher. */
async function ausDemSpeicher(ereignis, name) {
  const speicher = await caches.open(name);
  const gespeichert = await speicher.match(ereignis.request);
  if (gespeichert) return gespeichert;
  return ablegen(ereignis, speicher, ereignis.request, await fetch(ereignis.request));
}

/** Aus dem Netz, und dann in den Speicher; ohne Netz aus dem Speicher. */
async function ausDemNetz(ereignis, name, schluessel) {
  const speicher = await caches.open(name);
  try {
    return ablegen(ereignis, speicher, schluessel, await fetch(ereignis.request));
  } catch (fehler) {
    const gespeichert = await speicher.match(schluessel);
    if (gespeichert) return gespeichert;
    throw fehler;
  }
}
