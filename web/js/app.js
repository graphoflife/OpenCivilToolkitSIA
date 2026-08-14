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

import { api, ApiFehler } from './api.js';
import { el, melden } from './dom.js';
import { baumZeichnen } from './baum.js';
import { berichtZeichnen } from './bericht.js';
import { editorZeichnen } from './editor.js';
import { aendern, horchen, zustand } from './zustand.js';

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
    if (fehler instanceof ApiFehler && fehler.spur) console.error(fehler.spur);
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

async function speichern() {
  try {
    await api.projektSichern(zustand.projekt);
    aendern({ ungespeichert: false }, 'gespeichert');
    melden('Projekt gespeichert.');
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
    const meldung = antwort.pdf_pfad
      ? `PDF erzeugt mit ${antwort.maschine}: ${antwort.pdf_pfad}`
      : `LaTeX geschrieben: ${antwort.tex_pfad}\n(${antwort.meldung})`;

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
          download: `${zustand.projekt.name || 'bericht'}.tex`,
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

function allesZeichnen(anlass) {
  baumZeichnen(knoten.baum);
  editorZeichnen(knoten.editor, knoten.editorTitel, knoten.editorHinweis);
  // Der Reiter 'Ziel wählen' liefert eine Liste (oder null für 'alles').
  berichtZeichnen(knoten.bericht, (ziele) => rechnen({ ziele }));

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

async function starten() {
  Object.assign(knoten, {
    baum: document.getElementById('baum'),
    editor: document.getElementById('editor'),
    editorTitel: document.getElementById('editor-titel'),
    editorHinweis: document.getElementById('editor-hinweis'),
    bericht: document.getElementById('bericht'),
    projektname: document.getElementById('projektname'),
    zustandsanzeige: document.getElementById('zustandsanzeige'),
    btnRechnen: document.getElementById('btn-rechnen'),
    btnSpeichern: document.getElementById('btn-speichern'),
    btnBericht: document.getElementById('btn-bericht'),
    dialog: document.getElementById('dialog'),
    dialogTitel: document.getElementById('dialog-titel'),
    dialogInhalt: document.getElementById('dialog-inhalt'),
    reiterKnoepfe: [...document.querySelectorAll('.reiter-knopf')],
  });

  knoten.btnRechnen.addEventListener('click', () => rechnen());
  knoten.btnSpeichern.addEventListener('click', speichern);
  knoten.btnBericht.addEventListener('click', berichtErzeugen);
  document.getElementById('dialog-schliessen')
    .addEventListener('click', () => knoten.dialog.close());

  knoten.projektname.addEventListener('change', (e) => {
    zustand.projekt.name = e.target.value;
    aendern({ ungespeichert: true }, 'name');
  });

  for (const k of knoten.reiterKnoepfe) {
    k.addEventListener('click', () => aendern({ reiter: k.dataset.reiter }, 'reiter'));
  }
  for (const k of document.querySelectorAll('#umfang .schalter-halb')) {
    k.addEventListener('click', () => aendern({ umfang: k.dataset.umfang }, 'umfang'));
  }

  griffeEinrichten();
  horchen(allesZeichnen);

  try {
    const [katalog, projekt] = await Promise.all([api.katalog(), api.projektLaden()]);
    knoten.projektname.value = projekt.name;
    aendern({ katalog, projekt }, 'start');
    await rechnen();
  } catch (fehler) {
    zustandsanzeige('Kern nicht erreichbar', 'ist-fehler');
    melden(fehler.message, true);
  }
}

document.addEventListener('DOMContentLoaded', starten);
