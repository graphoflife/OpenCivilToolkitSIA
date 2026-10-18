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
  alsDateiSichern, ausDateiLaden, gerettete, geretteteHerunterladen, geretteteVerwerfen,
  imBrowserAblegen, projektHolen,
} from './ablage.js';
import { el, inhaltMarkieren, melden } from './dom.js';
import { baumZeichnen } from './baum.js';
import { berichtZeichnen } from './bericht.js';
import { konsoleVerbinden } from './konsole.js';
import { appVon } from './apps.js';
import { editorZeichnen } from './editor.js';
import { fensterEinrichten } from './fenster.js';
import { notizbuchEinrichten } from './notizbuch.js';

const knoten = {};
let rechenUhr = null;

/**
 * Ob noch einmal gerechnet werden soll, sobald der laufende Durchgang fertig
 * ist. Ein Merker genügt: gerechnet wird stets mit der Beschreibung, wie sie
 * in dem Augenblick aussieht -- ältere Wünsche sind ohnehin überholt.
 */
let nachgereicht = false;

// ===========================================================================
// Rechnen
// ===========================================================================

function zustandsanzeige(text, art = '') {
  knoten.zustandsanzeige.textContent = text;
  knoten.zustandsanzeige.className = `zustandsanzeige ${art}`;
}

/** Ein einzelner Durchgang: hinschicken, Antwort übernehmen, Stand melden. */
async function einDurchgang() {
  zustandsanzeige('rechnet …');
  try {
    const antwort = await api.rechnen(zustand.projekt);
    // Der gezeigte Einzelnachweis rechnet mit: sonst stünde in der Herleitung
    // eine Zahl von vor der letzten Eingabe. Aber nur, wenn die Herleitung zu
    // sehen ist -- sonst beim nächsten Blick darauf. Beides kommt in einem
    // Zug an, statt die Tafeln zweimal zu zeichnen.
    const v = zustand.verfolgung;
    const verfolgung = !v ? null
      : zustand.reiter === 'herleitung' ? await teillauf(v) : { ...v, loesung: null };
    // Inzwischen aufgehoben oder ein anderes Auge gewählt: das gilt.
    aendern({
      loesung: antwort,
      verfolgung: zustand.verfolgung === v ? verfolgung : zustand.verfolgung,
      rechenfehler: null,
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
    aendern({ rechenfehler: fehler.message }, 'rechenfehler');
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
async function rechnen() {
  if (zustand.rechnetGerade) {
    nachgereicht = true;
    return;
  }

  try {
    aendern({ rechnetGerade: true }, 'rechnen-start');
    knoten.btnRechnen.disabled = true;

    do {
      nachgereicht = false;
      await einDurchgang();
    } while (nachgereicht);
  } finally {
    nachgereicht = false;
    aendern({ rechnetGerade: false }, 'rechnen-ende');
    knoten.btnRechnen.disabled = false;
  }
}

/**
 * Das Auge in der Zusammenfassung: genau diesen Nachweis mit allem, was er
 * braucht -- als Teillauf *neben* der Gesamtlösung. Zusammenfassung,
 * Diagramme und Bericht bleiben vollständig; nur die Herleitung zeigt ihn.
 * Gibt es das Ziel nicht mehr (Fall gelöscht), endet die Verfolgung still: null.
 */
async function teillauf({ ziel, name }) {
  try {
    return { ziel, name, loesung: await api.rechnen(zustand.projekt, [ziel]) };
  } catch {
    return null;
  }
}

async function verfolgen(ziel, name) {
  const neu = await teillauf({ ziel, name });
  // Inzwischen aufgehoben oder ein anderes Auge gewählt: dann nicht.
  if (zustand.verfolgung?.ziel === ziel) aendern({ verfolgung: neu }, 'verfolgung');
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
      fenster: null,
      loesung: null,
      verfolgung: null,
    }, 'start');
    melden(`Projekt «${projekt.name}» geöffnet.`);
    await rechnen();
  } catch (fehler) {
    melden(fehler.message, true);
  }
}

// ===========================================================================
// Tafelbreiten
// ===========================================================================

/** Mindestbreite der Tafeln links und rechts in Pixeln. Darunter wird nichts mehr lesbar. */
const MINDESTBREITE = { links: 200, rechts: 280 };

/**
 * Wie breit die mittlere Tafel mindestens sein muss, damit ein Panel ganz
 * hineinpasst: ihre Breite ohne den Platz für Inhalt, plus ein Panel.
 */
function mindestensMitte(mitte) {
  const stapel = document.getElementById('editor');
  const stil = getComputedStyle(stapel);
  const innen = stapel.clientWidth - parseFloat(stil.paddingLeft) - parseFloat(stil.paddingRight);
  const panel = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--panelbreite')) || 420;
  return mitte - innen + panel;
}

/**
 * Die zwei Griffe zwischen den Tafeln.
 *
 * Der linke verstellt den Baum, der rechte die Eingaben. Was eine der beiden
 * gewinnt, gibt die Berechnung rechts her: sie bekommt als `1fr` den Rest.
 *
 * Die Panels der Eingaben behalten ihre Breite. Zieht man die mittlere
 * Tafel breiter, stehen sie in ihrer Mitte; nur die Zeichnung der
 * Querschnittsanalyse füllt sie dann aus (`data-mitte` am Raster).
 * Schmaler als ein Panel lässt sie sich nicht ziehen -- es würde
 * abgeschnitten. Solange niemand an diesem Griff war, ist sie so breit wie
 * ihre Panels.
 *
 * Bis 2026-10-08 gab es den rechten Griff schon einmal. Er fiel weg, als die
 * Panels nicht mehr mit der Tafel wuchsen: breiter gab nur leeren Platz am
 * rechten Rand. Seit die Panels in der Mitte stehen, ist er wieder da.
 */
function griffeEinrichten() {
  const wurzel = document.documentElement;
  const raster = document.getElementById('raster');

  for (const griff of document.querySelectorAll('.griff')) {
    griff.addEventListener('mousedown', (start) => {
      start.preventDefault();
      griff.classList.add('ist-aktiv');

      // Gemessen statt gerechnet: die rechte Tafel hat keine eigene Variable.
      // Was tatsächlich auf dem Schirm steht, weiss nur das Layout selbst.
      const [links, mitte, rechts] = [...document.querySelectorAll('.tafel')]
        .map((t) => t.getBoundingClientRect().width);

      // Wie weit der Griff nach links und rechts darf, bevor eine Tafel ihre
      // Mindestbreite unterschreitet. Nie negativ: ist ohnehin kein Platz
      // mehr, bewegt sich eben nichts.
      const waechst = Math.max(0, rechts - MINDESTBREITE.rechts);
      const mittig = griff.dataset.griff === 'mitte';
      const breite = mittig ? mitte : links;
      const schrumpft = Math.max(0, breite - (mittig ? mindestensMitte(mitte) : MINDESTBREITE.links));

      const bewegen = (e) => {
        const weg = Math.min(Math.max(e.clientX - start.clientX, -schrumpft), waechst);
        if (mittig) raster.dataset.mitte = 'gezogen';
        wurzel.style.setProperty(mittig ? '--breite-mitte' : '--breite-links', `${breite + weg}px`);
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

/**
 * Auf schmalen Geräten steht immer eine Tafel allein -- hier wird gewechselt.
 *
 * Drei Tafeln nebeneinander sind am Schreibtisch richtig und auf dem Telefon
 * unbrauchbar: bei 375 px blieb für die rechte nichts übrig, und Herleitung,
 * Zusammenfassung und Diagramme waren schlicht nicht erreichbar.
 *
 * Welche Tafel gilt, steht als `data-tafel` am Raster. Das Umschalten ist
 * darum eine reine Anzeigefrage und geht nicht durch den Zustand: es ändert
 * nichts am Projekt, und eine Rechnung soll es auch nicht auslösen.
 */
function tafelwahlEinrichten() {
  const wahl = document.getElementById('tafelwahl');
  const raster = document.getElementById('raster');
  if (!wahl || !raster) return;

  raster.dataset.tafel = 'mitte';
  wahl.addEventListener('click', (e) => {
    const knopf = e.target.closest('[data-tafel]');
    if (!knopf) return;
    raster.dataset.tafel = knopf.dataset.tafel;
    for (const k of wahl.querySelectorAll('[data-tafel]')) {
      k.classList.toggle('ist-aktiv', k === knopf);
    }
    // Jede Tafel scrollt für sich. Ohne das stünde man nach dem Wechsel
    // mitten im Text, den man beim letzten Mal verlassen hat.
    raster.querySelector(`.tafel-${knopf.dataset.tafel} .tafel-inhalt`)
      ?.scrollTo({ top: 0 });
  });
}

// ===========================================================================
// Zeichnen
// ===========================================================================

/** Was beim Neuzeichnen rollt: die drei Tafeln und das Fenster über den Eingaben. */
function tafeln() {
  return [knoten.baum, knoten.editor, knoten.fenster, knoten.bericht];
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
const ANKER = '.feldgruppe > h3, .unterkapitel-kopf, .b-untertitel, .b-text, .gleichung,'
            + ' .angabengruppe, .tabelle-titel, .hinweis, .kennwert, .feld';

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

/**
 * Anlässe, die nur die mittlere Tafel betreffen: eine Auswahl im
 * Zeichenfenster, eine Antwort des Kerns zur Zeichnung. Baum und Bericht
 * sähen danach aus wie vorher -- und die Herleitung neu zu setzen kostet
 * mit jeder Formel mehr.
 */
const NUR_MITTE = new Set(['zeichnung', 'fenster']);

/**
 * Die rechte Tafel: die Berechnung -- oder was die App des Gewählten selbst
 * rechts zeigt (apps.js, `rechts`): bei Python die Variablen der Sitzung,
 * wie in Spyder (Benutzer, 2026-10-15). Dann gelten Umfang und Reiter nicht.
 */
function rechtsZeichnen() {
  const eigen = appVon(zustand.auswahl?.art)?.rechts;
  knoten.berichtTitel.textContent = eigen ? eigen.titel : 'Berechnung';
  knoten.tafelRechts.textContent = eigen ? eigen.titel : 'Berechnung';
  knoten.umfang.hidden = Boolean(eigen);
  knoten.reiter.hidden = Boolean(eigen);
  if (eigen) {
    eigen.zeichnen(knoten.bericht);
  } else {
    berichtZeichnen(knoten.bericht, {
      verfolgen: (ziel, name) => {
        // Reiter und Platzhalter in einem Zug: sonst zeichnete der Wechsel
        // erst die ganze Herleitung, die der Teillauf gleich ersetzt.
        aendern({ reiter: 'herleitung', verfolgung: { ziel, name, loesung: null } }, 'verfolgung');
        verfolgen(ziel, name);
      },
    });
  }
  // Über allem, in beiden Sichten: ein Stand, der sich nicht öffnen liess.
  knoten.bericht.prepend(...zustand.gerettet.map(geretteterStand));
}

/**
 * Ein Stand, der sich beim Start nicht öffnen liess: warum, und was damit
 * geschehen soll. Er bleibt aufbewahrt, bis er verworfen ist.
 */
function geretteterStand(eintrag) {
  const wann = new Date(eintrag.zeit).toLocaleString('de-CH');
  return el('div.hinweis.hinweis-warnung', {}, [
    el('b', { text: 'Abgelegter Stand nicht geöffnet: ' }),
    `${eintrag.grund} Er ist aufbewahrt (${wann}); gezeigt wird das Beispiel. `,
    eintrag.aufbewahrt
      ? ''
      : 'Der Browser hat keinen Platz, ihn abzulegen -- bis er heruntergeladen '
        + 'oder verworfen ist, legt die Seite nichts im Browser ab. ',
    el('button.knopf.knopf-klein', {
      text: 'Als Datei herunterladen', on: { click: () => geretteteHerunterladen(eintrag) },
    }),
    ' ',
    el('button.knopf.knopf-klein', {
      text: 'Verwerfen',
      on: {
        click: () => {
          geretteteVerwerfen(eintrag);
          aendern({ gerettet: gerettete() }, 'gerettet');
        },
      },
    }),
  ]);
}

function allesZeichnen(anlass) {
  const nurMitte = NUR_MITTE.has(anlass);
  ohneSprung(() => {
    if (!nurMitte) baumZeichnen(knoten.apps, knoten.baum);
    editorZeichnen(knoten.editor, knoten.editorTitel, knoten.editorHinweis, knoten.fenster);
    if (!nurMitte) rechtsZeichnen();
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
    apps: document.getElementById('apps'),
    baum: document.getElementById('baum'),
    editor: document.getElementById('editor'),
    editorTitel: document.getElementById('editor-titel'),
    editorHinweis: document.getElementById('editor-hinweis'),
    fenster: document.getElementById('fenster'),
    bericht: document.getElementById('bericht'),
    berichtTitel: document.getElementById('bericht-titel'),
    tafelRechts: document.querySelector('#tafelwahl [data-tafel="rechts"]'),
    umfang: document.getElementById('umfang'),
    reiter: document.getElementById('reiter'),
    projektname: document.getElementById('projektname'),
    zustandsanzeige: document.getElementById('zustandsanzeige'),
    kernanzeige: document.getElementById('kernanzeige'),
    btnRechnen: document.getElementById('btn-rechnen'),
    btnSpeichern: document.getElementById('btn-speichern'),
    btnOeffnen: document.getElementById('btn-oeffnen'),
    // Nur die Reiter der Berechnung -- die Tafelwahl unten sieht gleich aus,
    // trägt aber kein `data-reiter` und setzte den Reiter sonst auf nichts.
    reiterKnoepfe: [...document.querySelectorAll('#reiter .reiter-knopf')],
  });

  knoten.btnRechnen.addEventListener('click', () => rechnen());
  knoten.btnSpeichern.addEventListener('click', speichern);
  knoten.btnOeffnen.addEventListener('click', oeffnen);

  knoten.projektname.addEventListener('change', (e) => {
    projektAendern((p) => { p.name = e.target.value; }, 'name');
  });

  for (const k of knoten.reiterKnoepfe) {
    k.addEventListener('click', () => {
      aendern({ reiter: k.dataset.reiter }, 'reiter');
      // Der Einzelnachweis rechnet erst nach, wenn die Herleitung zu sehen ist.
      const v = zustand.verfolgung;
      if (k.dataset.reiter === 'herleitung' && v && !v.loesung) verfolgen(v.ziel, v.name);
    });
  }
  // Ein Klick irgendwo auf den Schalter schaltet um, wie bei jedem mit zwei Stellungen.
  knoten.umfang.addEventListener('click', () => aendern(
    { umfang: zustand.umfang === 'seite' ? 'gesamt' : 'seite' }, 'umfang'));

  griffeEinrichten();
  tafelwahlEinrichten();
  // Ein Klick in ein Feld markiert seinen Inhalt -- Tippen ersetzt ihn.
  inhaltMarkieren();
  fensterEinrichten(knoten.fenster);
  ablageEinrichten(imBrowserAblegen);
  horchen(allesZeichnen);
  // Die Konsole meldet, wenn ein Lauf etwas ergab -- gerechnet wird dabei nichts.
  konsoleVerbinden(() => aendern({}, 'konsole'));
  // Vor dem Kern: das Notizbuch braucht ihn nicht, und eine Adresse
  // #notizbuch/… soll auch dann aufgehen, wenn Pyodide noch lädt.
  notizbuchEinrichten({
    knoepfe: [document.getElementById('btn-dokumentation'),
      document.getElementById('tafel-dokumentation')],
    ansicht: document.getElementById('notizbuch'),
  });

  try {
    // Erst den Kern -- ohne ihn lässt sich nicht einmal die Beschreibung prüfen.
    const kern = await kernBereitstellen(ladeanzeige);
    knoten.kernanzeige.textContent = kern.beschriftung;

    const [katalog, abgelegt] = await Promise.all([api.katalog(), projektHolen()]);

    knoten.projektname.value = abgelegt.projekt.name;
    aendern({
      katalog,
      projekt: abgelegt.projekt,
      ungespeichert: !abgelegt.gesichert,
      gerettet: gerettete(),
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
