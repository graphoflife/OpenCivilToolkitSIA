/**
 * app.js -- Verdrahtung der Oberfläche.
 *
 * Hält die drei Tafeln, die Kopfleiste und den Zustand zusammen. Sonst nichts:
 * gerechnet wird im Kern, dargestellt wird in den Tafeln.
 *
 * Nach jeder Eingabeänderung wird von selbst neu gerechnet -- allerdings erst,
 * wenn ein Moment lang nichts mehr getippt wurde. Sonst liefe für jede
 * gedrückte Taste ein vollständiger Nachweis samt Interaktionslinie.
 */

import { api, kernBereitstellen, KernFehler } from './api.js';
import {
  ablageEinrichten, aendern, horchen, projektAendern, zustand,
} from './zustand.js';
import {
  alsDateiSichern, ausDateiLaden, imBrowserAblegen, projektHolen,
} from './ablage.js';
import { el, melden } from './dom.js';
import { baumZeichnen } from './baum.js';
import { berichtZeichnen } from './bericht.js';
import { editorZeichnen } from './editor.js';

const knoten = {};
let rechenUhr = null;

// ===========================================================================
// Rechnen
// ===========================================================================

function zustandsanzeige(text, art = '') {
  knoten.zustandsanzeige.textContent = text;
  knoten.zustandsanzeige.className = `zustandsanzeige ${art}`;
}

async function rechnen({ ziele = null, stillschweigend = false } = {}) {
  if (zustand.rechnetGerade) return;
  aendern({ rechnetGerade: true }, 'rechnen-start');
  knoten.btnRechnen.disabled = true;
  if (!stillschweigend) zustandsanzeige('rechnet …');

  try {
    const antwort = await api.rechnen(zustand.projekt, ziele);
    const hervorgehoben = new Set();
    const verfolgt = ziele?.length === 1 ? ziele[0] : null;
    if (verfolgt && antwort.ketten?.[verfolgt]) {
      for (const id of antwort.ketten[verfolgt].werte) hervorgehoben.add(id);
    }

    aendern({
      loesung: antwort,
      ziele: ziele || [],
      verfolgtesZiel: verfolgt,
      hervorgehoben,
    }, 'loesung');

    if (!antwort.vollstaendig) {
      zustandsanzeige(`${antwort.fehlende.length} Eingaben fehlen`, 'ist-fehler');
    } else if (antwort.urteile.length) {
      const durchgefallen = antwort.urteile.filter((u) => !u.erfuellt).length;
      zustandsanzeige(
        durchgefallen ? `${durchgefallen} Nachweis(e) nicht erfüllt` : 'alle Nachweise erfüllt',
        durchgefallen ? 'ist-fehler' : 'ist-gut');
    } else {
      zustandsanzeige(`${Object.keys(antwort.werte).length} Werte bestimmt`, 'ist-gut');
    }
  } catch (fehler) {
    zustandsanzeige('Fehler', 'ist-fehler');
    melden(fehler.message, true);
    if (fehler instanceof KernFehler && fehler.spur) console.error(fehler.spur);
  } finally {
    aendern({ rechnetGerade: false }, 'rechnen-ende');
    knoten.btnRechnen.disabled = false;
  }
}

/** Rechnet verzögert -- damit Tippen nicht jede Taste zu einem Nachweis macht. */
function spaeterRechnen() {
  clearTimeout(rechenUhr);
  zustandsanzeige('geändert …');
  rechenUhr = setTimeout(() => rechnen({ stillschweigend: true }), 450);
}

// ===========================================================================
// Kopfleiste
// ===========================================================================

/**
 * Legt das Projekt als .json auf die Platte.
 *
 * Im Browser liegt es ohnehin schon -- nach jeder Änderung. Dieser Knopf ist
 * für das, was der Browser nicht kann: eine Datei, die man weitergeben,
 * ablegen und in ein Jahr wieder öffnen kann.
 */
function speichern() {
  try {
    const name = alsDateiSichern(zustand.projekt);
    aendern({ ungespeichert: false }, 'gespeichert');
    melden(`${name} gespeichert.`);
  } catch (fehler) {
    melden(fehler.message, true);
  }
}

async function oeffnen() {
  try {
    const projekt = await ausDateiLaden();
    if (projekt === null) return;  // abgebrochen

    knoten.projektname.value = projekt.name;
    // Kommt aus einer Datei, liegt also bereits auf der Platte.
    imBrowserAblegen(projekt, true);
    aendern({
      projekt,
      ungespeichert: false,
      auswahl: null,
      loesung: null,
      ziele: [],
      hervorgehoben: new Set(),
      verfolgtesZiel: null,
      gewaehlteZiele: new Set(),
      zieleListe: null,
    }, 'start');
    melden(`Projekt «${projekt.name}» geöffnet.`);
    await rechnen();
  } catch (fehler) {
    melden(fehler.message, true);
  }
}

function dialogZeigen(titel, inhalt) {
  knoten.dialogTitel.textContent = titel;
  knoten.dialogInhalt.replaceChildren(inhalt);
  knoten.dialog.showModal();
}

async function berichtErzeugen() {
  zustandsanzeige('erzeuge Bericht …');
  try {
    const antwort = await api.bericht(zustand.projekt, zustand.ziele);

    // Das .tex ist auf beiden Wegen dasselbe. Nur der Server kann es zusätzlich
    // ablegen und übersetzen -- im Browser gibt es keine TeX-Maschine.
    let meldung = 'Das LaTeX steht bereit. In Overleaf einfügen oder herunterladen.';
    if (antwort.pdf_pfad) meldung = `PDF erzeugt mit ${antwort.maschine}: ${antwort.pdf_pfad}`;
    else if (antwort.tex_pfad) meldung = `LaTeX geschrieben: ${antwort.tex_pfad}\n(${antwort.meldung})`;

    dialogZeigen('Bericht', el('div', {}, [
      el('p', { text: meldung, style: { whiteSpace: 'pre-wrap' } }),
      el('div.reihe', { style: { margin: '10px 0' } }, [
        el('button.knopf', {
          text: 'LaTeX in die Zwischenablage',
          on: {
            click: async () => {
              await navigator.clipboard.writeText(antwort.tex);
              melden('LaTeX kopiert – lässt sich direkt in Overleaf einfügen.');
            },
          },
        }),
        el('a.knopf', {
          text: '.tex herunterladen',
          download: `${antwort.dateiname || 'bericht'}.tex`,
          href: URL.createObjectURL(new Blob([antwort.tex], { type: 'application/x-tex' })),
        }),
      ]),
      el('pre', { text: antwort.tex }),
    ]));
    zustandsanzeige('Bericht bereit', 'ist-gut');
  } catch (fehler) {
    zustandsanzeige('Fehler', 'ist-fehler');
    melden(fehler.message, true);
  }
}

// ===========================================================================
// Tafelbreiten
// ===========================================================================

function griffeEinrichten() {
  for (const griff of document.querySelectorAll('.griff')) {
    griff.addEventListener('mousedown', (start) => {
      start.preventDefault();
      griff.classList.add('ist-aktiv');
      const welche = griff.dataset.griff === 'links' ? '--breite-links' : '--breite-mitte';
      const anfang = parseInt(
        getComputedStyle(document.documentElement).getPropertyValue(welche), 10);

      const bewegen = (e) => {
        const neu = Math.min(Math.max(anfang + e.clientX - start.clientX, 200), 720);
        document.documentElement.style.setProperty(welche, `${neu}px`);
      };
      const loslassen = () => {
        griff.classList.remove('ist-aktiv');
        document.removeEventListener('mousemove', bewegen);
        document.removeEventListener('mouseup', loslassen);
      };
      document.addEventListener('mousemove', bewegen);
      document.addEventListener('mouseup', loslassen);
    });
  }
}

// ===========================================================================
// Zeichnen
// ===========================================================================

/** Die drei scrollbaren Tafeln. */
function tafeln() {
  return [knoten.baum, knoten.editor, knoten.bericht];
}

/**
 * Merkt sich, welches Bedienelement den Fokus hat -- und woran man es wiedererkennt.
 *
 * Beim Neuzeichnen wird der Knoten weggeworfen und ein gleich aussehender
 * gebaut. Eine Kennung tragen die Felder nicht, also wird über die Stelle in
 * der Reihenfolge gesucht und anschliessend geprüft, ob dort wirklich dasselbe
 * Feld steht. Stimmt eines der Merkmale nicht -- etwa weil eine Zeile
 * dazugekommen ist --, bleibt der Fokus lieber weg, als im falschen Zahlenfeld
 * zu landen.
 */
const BEDIENBAR = 'input, select, textarea';

function fokusMerken() {
  const aktiv = document.activeElement;
  if (!aktiv || !aktiv.matches?.(BEDIENBAR)) return null;
  const tafel = tafeln().find((t) => t?.contains(aktiv));
  if (!tafel) return null;

  return {
    tafel,
    stelle: [...tafel.querySelectorAll(BEDIENBAR)].indexOf(aktiv),
    art: aktiv.type,
    titel: aktiv.title,
    wert: aktiv.value,
    von: aktiv.selectionStart,
    bis: aktiv.selectionEnd,
  };
}

function fokusZurueck(merkmal) {
  if (!merkmal || merkmal.stelle < 0) return;
  const feld = [...merkmal.tafel.querySelectorAll(BEDIENBAR)][merkmal.stelle];
  if (!feld || feld.type !== merkmal.art || feld.title !== merkmal.titel
      || feld.value !== merkmal.wert) return;

  feld.focus({ preventScroll: true });
  // Zahlenfelder erlauben selectionStart nur bei manchen Eingabearten.
  try {
    if (merkmal.von !== null) feld.setSelectionRange(merkmal.von, merkmal.bis);
  } catch {
    /* nicht alle Feldarten können das -- dann eben ohne Schreibmarke */
  }
}

/**
 * Zeichnet neu, ohne die Ansicht zu verwerfen.
 *
 * Jede Eingabe baut die Tafeln komplett neu auf. Dabei fallen die
 * Scrollposition und der Fokus weg -- die Seite sprang bei jedem Enter nach
 * oben. Hier wird beides um das Neuzeichnen herumgerettet.
 */
function ohneSprung(zeichnen) {
  const stand = tafeln().map((t) => t?.scrollTop ?? 0);
  const merkmal = fokusMerken();

  zeichnen();

  tafeln().forEach((t, i) => {
    if (t && t.scrollTop !== stand[i]) t.scrollTop = stand[i];
  });
  fokusZurueck(merkmal);
}

function allesZeichnen(anlass) {
  ohneSprung(() => {
    baumZeichnen(knoten.baum);
    editorZeichnen(knoten.editor, knoten.editorTitel, knoten.editorHinweis);
    // Der Reiter 'Ziel wählen' liefert eine Liste (oder null für 'alles').
    berichtZeichnen(knoten.bericht, (ziele) => rechnen({ ziele }));
  });

  knoten.btnSpeichern.textContent = zustand.ungespeichert ? 'Speichern •' : 'Speichern';
  for (const k of knoten.reiterKnoepfe) {
    k.classList.toggle('ist-aktiv', k.dataset.reiter === zustand.reiter);
  }
  for (const k of document.querySelectorAll('#umfang .schalter-halb')) {
    k.classList.toggle('ist-an', k.dataset.umfang === zustand.umfang);
  }

  // Eingaben geändert -> neu rechnen. Nicht bei blossem Blättern und nicht,
  // während schon gerechnet wird.
  if (anlass === 'projekt') spaeterRechnen();
}

// ===========================================================================
// Start
// ===========================================================================

/** Die Startanzeige, solange Python noch lädt. */
function ladeanzeige(text) {
  const schirm = document.getElementById('ladeschirm');
  if (!schirm) return;
  if (text === '') {
    schirm.remove();
    return;
  }
  document.getElementById('ladetext').textContent = text;
}

async function starten() {
  Object.assign(knoten, {
    baum: document.getElementById('baum'),
    editor: document.getElementById('editor'),
    editorTitel: document.getElementById('editor-titel'),
    editorHinweis: document.getElementById('editor-hinweis'),
    bericht: document.getElementById('bericht'),
    projektname: document.getElementById('projektname'),
    zustandsanzeige: document.getElementById('zustandsanzeige'),
    kernanzeige: document.getElementById('kernanzeige'),
    btnRechnen: document.getElementById('btn-rechnen'),
    btnSpeichern: document.getElementById('btn-speichern'),
    btnOeffnen: document.getElementById('btn-oeffnen'),
    btnBericht: document.getElementById('btn-bericht'),
    dialog: document.getElementById('dialog'),
    dialogTitel: document.getElementById('dialog-titel'),
    dialogInhalt: document.getElementById('dialog-inhalt'),
    reiterKnoepfe: [...document.querySelectorAll('.reiter-knopf')],
  });

  knoten.btnRechnen.addEventListener('click', () => rechnen());
  knoten.btnSpeichern.addEventListener('click', speichern);
  knoten.btnOeffnen.addEventListener('click', oeffnen);
  knoten.btnBericht.addEventListener('click', berichtErzeugen);
  document.getElementById('dialog-schliessen')
    .addEventListener('click', () => knoten.dialog.close());

  knoten.projektname.addEventListener('change', (e) => {
    projektAendern((p) => { p.name = e.target.value; }, 'name');
  });

  for (const k of knoten.reiterKnoepfe) {
    k.addEventListener('click', () => aendern({ reiter: k.dataset.reiter }, 'reiter'));
  }
  for (const k of document.querySelectorAll('#umfang .schalter-halb')) {
    k.addEventListener('click', () => aendern({ umfang: k.dataset.umfang }, 'umfang'));
  }

  griffeEinrichten();
  ablageEinrichten(imBrowserAblegen);
  horchen(allesZeichnen);

  try {
    // Erst den Kern -- ohne ihn lässt sich nicht einmal die Beschreibung prüfen.
    const kern = await kernBereitstellen(ladeanzeige);
    knoten.kernanzeige.textContent = kern.beschriftung;

    const [katalog, abgelegt] = await Promise.all([api.katalog(), projektHolen()]);
    if (abgelegt.hinweis) melden(abgelegt.hinweis, true);

    knoten.projektname.value = abgelegt.projekt.name;
    aendern({
      katalog,
      projekt: abgelegt.projekt,
      ungespeichert: !abgelegt.gesichert,
    }, 'start');
    await rechnen();
  } catch (fehler) {
    ladeanzeige('');
    zustandsanzeige('Kern nicht bereit', 'ist-fehler');
    melden(fehler.message, true);
    if (fehler instanceof KernFehler && fehler.spur) console.error(fehler.spur);
  }
}

document.addEventListener('DOMContentLoaded', starten);
