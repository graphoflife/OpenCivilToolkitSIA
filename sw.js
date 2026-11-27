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
    "web/css/10-grundlage.css?v=6bf8fa49c1e8",
    "web/css/20-seite.css?v=fffcb0bfe20c",
    "web/css/30-eingaben.css?v=5bc41d68e1d3",
    "web/css/40-bericht.css?v=9260c2489f98",
    "web/css/50-schmal.css?v=fd221b20ca93",
    "web/css/60-zeichenfenster.css?v=0534b6c63cd4",
    "web/css/70-notizbuch.css?v=5c29ff90c1e1",
    "web/css/80-skizzen.css?v=53ea16d3200b",
    "web/css/90-python.css?v=bec24d055c16",
    "web/js/ablage.js?v=84cbb1c2e67e",
    "web/js/achsen.js?v=aced8f358043",
    "web/js/api.js?v=185ab81155dd",
    "web/js/app.js?v=b0a9990a1352",
    "web/js/apps.js?v=ea263b39ab36",
    "web/js/arten.js?v=452add6cf92b",
    "web/js/balkensystem.js?v=1022d26d8dad",
    "web/js/baum.js?v=97b983cbbf34",
    "web/js/bausteine.js?v=86b394371f4b",
    "web/js/bericht.js?v=e4a8bd9cb271",
    "web/js/bewehrungssuche.js?v=2582eafd0f54",
    "web/js/bs_diagramme.js?v=b94694de6703",
    "web/js/bs_eigenschaften.js?v=c8b092e777db",
    "web/js/bs_symbole.js?v=2de8f1220c79",
    "web/js/bs_teile.js?v=d2faa30329d7",
    "web/js/bs_texte.js?v=6f2bb7462826",
    "web/js/bs_zeichnung.js?v=8c0e0236745a",
    "web/js/cad_ansicht.js?v=ec2a2531b96a",
    "web/js/cad_app.js?v=01f4fdc972a2",
    "web/js/cad_auswahl.js?v=b16821f67104",
    "web/js/cad_befehle.js?v=8e43df749e30",
    "web/js/cad_eingabe.js?v=2c581e18424c",
    "web/js/cad_fenster.js?v=5402f4e59825",
    "web/js/cad_modell.js?v=50d977829c8e",
    "web/js/cad_palette.js?v=9178870a84f2",
    "web/js/cad_raum.js?v=112932116383",
    "web/js/cad_verlauf.js?v=7603b772b8be",
    "web/js/decke.js?v=d55278024d1b",
    "web/js/diagramm.js?v=8f2f000fef51",
    "web/js/dk_eigenschaften.js?v=61db6b70d290",
    "web/js/dk_ergebnis.js?v=05988feaa2cb",
    "web/js/dk_grundriss.js?v=3377f145094a",
    "web/js/dk_schnitt.js?v=1cc553f65830",
    "web/js/dk_zeichnung.js?v=f5a5bd05660c",
    "web/js/dom.js?v=171f61663900",
    "web/js/ds_ansicht.js?v=126bc2761415",
    "web/js/ds_grundriss.js?v=4f1f43cfdf19",
    "web/js/ds_zeichnung.js?v=edfc39294208",
    "web/js/durchstanzen.js?v=c7c418f6d86c",
    "web/js/eb_verlauf.js?v=4c06fa7eff09",
    "web/js/eb_zeichnung.js?v=ee4e558053b0",
    "web/js/editor.js?v=97f3abad7a0d",
    "web/js/einstellungen.js?v=780d2d359a44",
    "web/js/erdbeben.js?v=4c32355702da",
    "web/js/faelle.js?v=885d9e2cebcf",
    "web/js/fallantwort.js?v=cab91f08ea3e",
    "web/js/fenster.js?v=0ba50fee6156",
    "web/js/gb_skizze.js?v=4123c92f9fe4",
    "web/js/gb_zeichnung.js?v=6895f6dc6243",
    "web/js/grundbruch.js?v=1484f761f325",
    "web/js/kapitel.js?v=88a9eefdc91e",
    "web/js/kern.js?v=68a4e9aaa723",
    "web/js/kern_arbeiter.js?v=ee8603262c6b",
    "web/js/konsole.js?v=25434f6b739d",
    "web/js/kopierleiste.js?v=2af7c8ead463",
    "web/js/lagen.js?v=d1de89b1b40b",
    "web/js/lastfaelle.js?v=01ccd2e095b4",
    "web/js/markdown.js?v=95b8ac3d60df",
    "web/js/material.js?v=2526950143bb",
    "web/js/materialwahl.js?v=af7dafa5d791",
    "web/js/mathe.js?v=f218656b8dbb",
    "web/js/nachweise.js?v=ce9e81c53175",
    "web/js/notizbuch.js?v=5079698154ff",
    "web/js/notizbuch_seite.js?v=639209806e79",
    "web/js/offline.js?v=1b6f6c615c08",
    "web/js/pf_querschnitt.js?v=62fc3206c74b",
    "web/js/pf_verlauf.js?v=077aa49f7b6c",
    "web/js/pf_zeichnung.js?v=5f0e72c42071",
    "web/js/pfahl.js?v=783cfa2dbc7c",
    "web/js/platte.js?v=016db10e2ffc",
    "web/js/platte_bilder.js?v=415c593f5f98",
    "web/js/plattenkapitel.js?v=fed707010dce",
    "web/js/profilwahl.js?v=509ceecac884",
    "web/js/projekte.js?v=4cf72047989c",
    "web/js/python.js?v=e36b207b3ea6",
    "web/js/qa_aktionen.js?v=71af5696e4f9",
    "web/js/qa_blechdecke.js?v=7125f492cc90",
    "web/js/qa_diagramme.js?v=a2188b51b5aa",
    "web/js/qa_fallteile.js?v=a5277388bb33",
    "web/js/qa_laengsschub.js?v=357b949905ed",
    "web/js/qa_profile.js?v=26736ac483e5",
    "web/js/qa_schnitt.js?v=a640365d8ef1",
    "web/js/qa_schubfluss.js?v=691bdb0f56b2",
    "web/js/qa_skizze.js?v=8bbc9eeb4669",
    "web/js/qa_spannglied.js?v=1f795516a90f",
    "web/js/qa_stabilitaet.js?v=5ddf2651a727",
    "web/js/qa_uebersicht.js?v=c3b2a2bfaa06",
    "web/js/qa_umriss.js?v=25a6cd0ebff3",
    "web/js/qa_vorlagen.js?v=e4a52d4e623c",
    "web/js/qa_zeichnung.js?v=9372c6fc0067",
    "web/js/querschnittsanalyse.js?v=47c7464dc035",
    "web/js/setzung.js?v=21db1c68db33",
    "web/js/sinnbilder.js?v=fc464c539e6f",
    "web/js/spannungsbild.js?v=5bf6ce4eb080",
    "web/js/sz_zeichnung.js?v=8ce828560c47",
    "web/js/variablen.js?v=7d43b6f38cd9",
    "web/js/zeichnen.js?v=da6e8eec5dc8",
    "web/js/zustand.js?v=3385a39c0f84",
    "web/kern/notizbuch.json?v=a67d2f5d8289",
    "web/kern/quellen.json?v=06bd1a0c11c5"
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
