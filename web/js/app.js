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

/**
 * Was gerechnet werden soll, sobald der laufende Durchgang fertig ist.
 *
 * `null`, solange nichts wartet. Es wird immer nur der jüngste Wunsch
 * aufbewahrt -- ältere sind ohnehin überholt, denn gerechnet wird stets mit der
 * Beschreibung, wie sie in dem Augenblick aussieht.
 */
let nachgereicht = null;

// ===========================================================================
// Rechnen
// ===========================================================================

function zustandsanzeige(text, art = '') {
  knoten.zustandsanzeige.textContent = text;
  knoten.zustandsanzeige.className = `zustandsanzeige ${art}`;
}

/** Ein einzelner Durchgang: hinschicken, Antwort übernehmen, Stand melden. */
async function einDurchgang(ziele) {
  zustandsanzeige('rechnet …');
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
      const fehlt = antwort.fehlende.length;
      zustandsanzeige(fehlt === 1 ? 'Eine Eingabe fehlt' : `${fehlt} Eingaben fehlen`,
        'ist-fehler');
    } else if (antwort.urteile.length) {
      const durchgefallen = antwort.urteile.filter((u) => !u.erfuellt).length;
      zustandsanzeige(
        durchgefallen === 0 ? 'alle Nachweise erfüllt'
          : durchgefallen === 1 ? 'ein Nachweis nicht erfüllt'
            : `${durchgefallen} Nachweise nicht erfüllt`,
        durchgefallen ? 'ist-fehler' : 'ist-gut');
    } else {
      zustandsanzeige(`${Object.keys(antwort.werte).length} Werte bestimmt`, 'ist-gut');
    }
  } catch (fehler) {
    zustandsanzeige('Fehler', 'ist-fehler');
    melden(fehler.message, true);
    if (fehler instanceof KernFehler && fehler.spur) console.error(fehler.spur);
  }
}

/**
 * Rechnet -- und rechnet gleich noch einmal, wenn währenddessen etwas geändert wurde.
 *
 * Ein Durchgang ist nicht sofort zu Ende: beim lokalen Server liegt eine
 * Anfrage dazwischen, und in dieser Zeit läuft die Oberfläche weiter. Wer
 * genau dann eine Zahl ändert, löste bisher einen Aufruf aus, der
 * stillschweigend verworfen wurde -- angezeigt wurde danach das Urteil zur
 * *vorherigen* Zahl, und oben stand «geändert …». Der Wunsch wird deshalb
 * aufbewahrt statt weggeworfen.
 *
 * Auch der Riegel selbst gehört in den Schutz von `finally`: bliebe er nach
 * einem Fehler beim Neuzeichnen stehen, wäre jede weitere Rechnung für immer
 * gesperrt -- auch die von Hand angestossene.
 */
async function rechnen({ ziele = null } = {}) {
  if (zustand.rechnetGerade) {
    nachgereicht = { ziele };
    return;
  }

  try {
    aendern({ rechnetGerade: true }, 'rechnen-start');
    knoten.btnRechnen.disabled = true;

    let auftrag = { ziele };
    while (auftrag) {
      nachgereicht = null;
      await einDurchgang(auftrag.ziele);
      auftrag = nachgereicht;
    }
  } finally {
    nachgereicht = null;
    aendern({ rechnetGerade: false }, 'rechnen-ende');
    knoten.btnRechnen.disabled = false;
  }
}

/** Rechnet verzögert -- damit Tippen nicht jede Taste zu einem Nachweis macht. */
function spaeterRechnen() {
  clearTimeout(rechenUhr);
  zustandsanzeige('geändert …');
  rechenUhr = setTimeout(() => rechnen(), 450);
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

/** Mindestbreite jeder Tafel in Pixeln. Darunter wird nichts mehr lesbar. */
const MINDESTBREITE = { links: 200, mitte: 260, rechts: 280 };

/**
 * Die beiden Griffe zwischen den Tafeln.
 *
 * Ein Griff bewegt **eine** Grenze: er nimmt der einen Tafel, was er der
 * anderen gibt. Die dritte bleibt, wo sie ist.
 *
 * Vorher zog der linke Griff nur `--breite-links` nach. Die mittlere Tafel
 * behielt ihre Pixelbreite und rutschte mit, also ging die Änderung zu Lasten
 * der rechten Tafel -- die als `1fr` schlicht den Rest bekommt. Wer die rechte
 * schmaler wollte, musste am linken Griff ziehen. Genau das soll nicht sein.
 *
 * Die rechte Tafel hat keine eigene Variable; ihre Breite ergibt sich. Der
 * rechte Griff begrenzt sich deshalb an dem, was übrig bliebe.
 */
function griffeEinrichten() {
  const wurzel = document.documentElement;

  for (const griff of document.querySelectorAll('.griff')) {
    const links = griff.dataset.griff === 'links';

    griff.addEventListener('mousedown', (start) => {
      start.preventDefault();
      griff.classList.add('ist-aktiv');

      // Gemessen statt gerechnet: die rechte Tafel hat keine eigene Variable,
      // und zwischen den Tafeln liegen noch die Griffe. Was tatsächlich auf dem
      // Schirm steht, weiss nur das Layout selbst.
      const [tLinks, tMitte, tRechts] = [...document.querySelectorAll('.tafel')]
        .map((t) => t.getBoundingClientRect().width);

      // Wie weit der Griff nach links und rechts darf, bevor eine der beiden
      // angrenzenden Tafeln ihre Mindestbreite unterschreitet. Nie negativ:
      // ist ohnehin kein Platz mehr, bewegt sich eben nichts.
      const luft = (breite, art) => Math.max(0, breite - MINDESTBREITE[art]);
      const [schrumpft, waechst] = links
        ? [luft(tLinks, 'links'), luft(tMitte, 'mitte')]
        : [luft(tMitte, 'mitte'), luft(tRechts, 'rechts')];
      const anfangLinks = tLinks;
      const anfangMitte = tMitte;

      const bewegen = (e) => {
        const weg = Math.min(Math.max(e.clientX - start.clientX, -schrumpft), waechst);
        if (links) {
          wurzel.style.setProperty('--breite-links', `${anfangLinks + weg}px`);
          wurzel.style.setProperty('--breite-mitte', `${anfangMitte - weg}px`);
        } else {
          wurzel.style.setProperty('--breite-mitte', `${anfangMitte + weg}px`);
        }
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

  // selectionStart wirft bei manchen Eingabearten (Zahlenfeldern etwa) statt
  // null zu liefern -- deshalb abgesichert.
  let von = null;
  let bis = null;
  try {
    von = aktiv.selectionStart;
    bis = aktiv.selectionEnd;
  } catch {
    /* diese Feldart kennt keine Schreibmarke */
  }

  return {
    tafel,
    stelle: [...tafel.querySelectorAll(BEDIENBAR)].indexOf(aktiv),
    art: aktiv.type,
    titel: aktiv.title,
    wert: aktiv.value,
    von,
    bis,
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
 * Elemente, an denen sich die Ansicht festhalten kann.
 *
 * Überschriften, Absätze, Formeln, Tabellentitel -- alles, was eine Stelle im
 * Bericht benennt und sich beim Neuzeichnen wiedererkennen lässt.
 */
const ANKER = '.b-titel, .b-untertitel, .b-text, .gleichung, .angabengruppe,'
            + ' .tabelle-titel, .hinweis, .kennwert, .feld';

/**
 * Merkt sich, welcher Inhalt gerade oben in der Tafel steht.
 *
 * Die blosse Scrollposition genügt nicht: die Herleitung wird beim Ändern
 * einer Zahl länger oder kürzer -- eine Eingabe liess sie um über 600 Bildpunkte
 * schrumpfen. Bei gleicher Scrollposition steht dann anderer Inhalt da, und
 * genau das sieht aus wie ein Sprung. Festgehalten wird deshalb nicht die
 * Position, sondern der Inhalt.
 */
function ankerMerken(tafel) {
  if (!tafel || tafel.scrollTop <= 0) return null;
  const oben = tafel.getBoundingClientRect().top;
  const gezaehlt = new Map();

  for (const k of tafel.querySelectorAll(ANKER)) {
    const schluessel = (k.textContent || '').trim().slice(0, 80);
    const nummer = gezaehlt.get(schluessel) || 0;
    gezaehlt.set(schluessel, nummer + 1);
    if (!schluessel) continue;
    const versatz = k.getBoundingClientRect().top - oben;
    // Der erste, der nicht schon oben hinausgeschoben ist.
    if (versatz >= 0) return { schluessel, nummer, versatz };
  }
  return null;
}

function ankerZurueck(tafel, anker) {
  if (!anker) return false;
  const oben = tafel.getBoundingClientRect().top;
  let nummer = 0;

  for (const k of tafel.querySelectorAll(ANKER)) {
    if ((k.textContent || '').trim().slice(0, 80) !== anker.schluessel) continue;
    if (nummer++ !== anker.nummer) continue;
    tafel.scrollTop += (k.getBoundingClientRect().top - oben) - anker.versatz;
    return true;
  }
  return false;
}

/**
 * Zeichnet neu, ohne die Ansicht zu verwerfen.
 *
 * Jede Eingabe baut die Tafeln komplett neu auf. Dabei fallen Scrollposition
 * und Fokus weg, und die Länge des Inhalts ändert sich obendrein. Hier wird
 * beides um das Neuzeichnen herumgerettet: zuerst über den Anker, und wo
 * keiner wiederzufinden ist, wenigstens über die alte Scrollposition.
 */
function ohneSprung(zeichnen) {
  const vorher = tafeln().map((t) => ({
    tafel: t, stand: t?.scrollTop ?? 0, anker: ankerMerken(t),
  }));
  const merkmal = fokusMerken();

  zeichnen();

  for (const { tafel, stand, anker } of vorher) {
    if (!tafel) continue;
    if (!ankerZurueck(tafel, anker) && tafel.scrollTop !== stand) {
      tafel.scrollTop = stand;
    }
  }
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
