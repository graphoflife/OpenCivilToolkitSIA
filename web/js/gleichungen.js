/**
 * gleichungen.js -- ein Blatt analytischer Gleichungen im Editor.
 *
 * Zeile für Zeile wie in Mathcad: ein Formelfeld (MathLive) je Zeile, rechts
 * das Ergebnis aus dem Kern; darüber ein Raster mit Bausteinen zum Einfügen.
 * Enter legt eine neue Zeile an, Backspace auf einer leeren Zeile nimmt sie
 * weg. Gerechnet und gesetzt wird im Kern -- hier steht kein Zeichen Mathematik.
 *
 * DIE ANSICHT BLEIBT STEHEN:
 * Die Tafeln werden bei jeder Änderung neu gezeichnet. Ein Formelfeld verlöre
 * dabei Fokus und Cursor, mitten im Tippen. Diese Ansicht behält darum ihre
 * Knoten, solange die Zeilen dieselben bleiben (gleiche Zahl, gleiche Arten),
 * und frischt nur Werte, Ergebnisse und Fehler auf. Neu gebaut wird erst,
 * wenn eine Zeile dazukommt oder wegfällt.
 *
 * MathLive wird erst geladen, wenn ein Blatt offen ist -- 840 KB, die sonst
 * niemand braucht. Seine Schriften sind die von KaTeX, byte-gleich.
 */

import { el, melden } from './dom.js';
import { setzen, span } from './mathe.js';
import { projektAendern, zustand } from './zustand.js';

// ===========================================================================
// MathLive
// ===========================================================================

let mathlive = null;

/** MathLive 0.110.0 (MIT), einmal geladen, sobald ein Blatt offen ist. */
function mathliveLaden() {
  mathlive = mathlive || import('../vendor/mathlive/mathlive.min.mjs')
    .then((modul) => {
      modul.MathfieldElement.fontsDirectory = new URL('../vendor/katex/fonts/', import.meta.url).href;
      modul.MathfieldElement.soundsDirectory = null;
      return modul;
    })
    .catch((fehler) => {
      melden(`Formeleditor nicht ladbar: ${fehler.message}`, true);
      throw fehler;
    });
  return mathlive;
}

/**
 * Kürzel beim Tippen: «kN» wird zur Einheit, nicht zu k mal N. Welche
 * Einheiten es gibt, sagt der Kern. Nur Namen aus mehreren Buchstaben -- ein
 * einzelnes m oder N bleibt eine Variable; dafür gibt es das Raster. Und
 * nicht «min»: das ist in MathLive schon die Funktion.
 */
function kuerzel() {
  return Object.fromEntries((zustand.katalog?.einheiten || [])
    .filter((e) => e.length > 1 && e !== 'min')
    .map((e) => [e, `\\mathrm{${e}}`]));
}

// ===========================================================================
// Raster
// ===========================================================================

/** [Beschriftung, was eingefügt wird] -- #0 ist die Auswahl, #? eine Leerstelle. */
const RASTER = [
  ['Struktur', [
    [String.raw`\frac{a}{b}`, String.raw`\frac{#0}{#?}`],
    ['x^{n}', '#@^{#?}'],
    ['x_{i}', '#@_{#?}'],
    [String.raw`\sqrt{x}`, String.raw`\sqrt{#0}`],
    [String.raw`\sqrt[n]{x}`, String.raw`\sqrt[#?]{#0}`],
    ['(x)', String.raw`\left(#0\right)`],
    ['|x|', String.raw`\left|#0\right|`],
    [String.raw`\cdot`, String.raw`\cdot`],
  ]],
  ['Funktionen', ['sin', 'cos', 'tan', 'arctan', 'ln', 'log', 'exp', 'min', 'max']
    .map((f) => [`\\${f}`, `\\${f}\\left(#0\\right)`])
    .concat([[String.raw`\pi`, String.raw`\pi`]])],
  ['Griechisch', ['alpha', 'beta', 'gamma', 'delta', 'varepsilon', 'eta', 'theta',
    'lambda', 'mu', 'nu', 'rho', 'sigma', 'tau', 'varphi', 'chi', 'psi', 'omega',
    'Delta', 'Sigma'].map((g) => [`\\${g}`, `\\${g}`])],
  ['Einheiten', [
    ...['mm', 'cm', 'm', 'kN', 'N', 'kNm', 'MPa'].map((e) => [`\\mathrm{${e}}`, `\\mathrm{${e}}`]),
    [String.raw`\mathrm{kN}/\mathrm{m}`, String.raw`\mathrm{kN}/\mathrm{m}`],
    [String.raw`\mathrm{kN}/\mathrm{m}^{2}`, String.raw`\mathrm{kN}/\mathrm{m}^{2}`],
    [String.raw`\mathrm{N}/\mathrm{mm}^{2}`, String.raw`\mathrm{N}/\mathrm{mm}^{2}`],
    ['{}^{\\circ}', '^{\\circ}'],
    [String.raw`\%`, String.raw`\%`],
  ]],
];

// ===========================================================================
// Zustand der Ansicht
// ===========================================================================

/** Die gebaute Ansicht -- sie überdauert das Neuzeichnen, siehe oben. */
let ansicht = null;
/** Welche Zeile nach dem nächsten Bauen den Fokus bekommt. */
let fokusWunsch = null;
/** Das Formelfeld, in das das Raster einfügt. */
let letztesFeld = null;
/** Das Raster hängt an keiner Zeile: einmal gebaut, bei jedem Neubau wieder eingehängt. */
let rasterKnoten = null;
let uebernahmeUhr = null;

function blattVon(kennung) {
  return zustand.projekt.gleichungen.find((b) => b.kennung === kennung);
}

/** Woran die Ansicht merkt, dass sie neu gebaut werden muss. */
function strukturVon(blatt) {
  return blatt.zeilen.map((z) => z.art).join('|');
}

/**
 * Getipptes gleich ins Projekt, gerechnet und gespeichert erst nach einer
 * kurzen Pause -- sonst zeichnete jede Taste die Herleitung neu.
 */
function spaeterUebernehmen() {
  clearTimeout(uebernahmeUhr);
  uebernahmeUhr = setTimeout(() => projektAendern(() => {}), 400);
}

function sofortUebernehmen(veraenderer) {
  clearTimeout(uebernahmeUhr);
  projektAendern(veraenderer);
}

/** Eine leere Zeile -- «formel», «projektwert» oder «text»; die Felder sagt der Kern. */
export function neueZeile(art = 'formel') {
  return { ...zustand.katalog.neue_gleichungszeile, art };
}

function zeileEinfuegen(kennung, index, art = 'formel') {
  fokusWunsch = index;
  sofortUebernehmen(() => blattVon(kennung).zeilen.splice(index, 0, neueZeile(art)));
}

function zeileEntfernen(kennung, index) {
  fokusWunsch = Math.max(0, index - 1);
  sofortUebernehmen(() => blattVon(kennung).zeilen.splice(index, 1));
}

// ===========================================================================
// Bauen
// ===========================================================================

function formelfeld(latex, beiEingabe, { klein = false } = {}) {
  // Der Anfangswert als Inhalt, nicht als Eigenschaft: vor dem Laden von
  // MathLive ist das Element noch kein Formelfeld, und eine gesetzte
  // Eigenschaft verdeckte später die des Formelfelds.
  const feld = el(`math-field.gl-feld${klein ? '.ist-klein' : ''}`, {
    'math-virtual-keyboard-policy': 'manual',
    text: latex,
  });
  feld.addEventListener('input', () => beiEingabe(feld.value));
  feld.addEventListener('focusin', () => { letztesFeld = feld; });
  customElements.whenDefined('math-field').then(() => {
    feld.inlineShortcuts = { ...feld.inlineShortcuts, ...kuerzel() };
    feld.menuItems = [];
  });
  return feld;
}

function formelzeile(zeile, kennung, index) {
  const feld = formelfeld(zeile().latex, (wert) => {
    zeile().latex = wert;
    spaeterUebernehmen();
  });
  // In der Fangphase: sonst hätte MathLive das letzte Zeichen schon gelöscht,
  // und Backspace auf «x» nähme gleich die ganze Zeile mit.
  feld.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      zeile().latex = feld.value;
      zeileEinfuegen(kennung, index + 1);
    } else if (e.key === 'Backspace' && !feld.value && blattVon(kennung).zeilen.length > 1) {
      e.preventDefault();
      zeileEntfernen(kennung, index);
    }
  }, true);
  const einheit = el('input.gl-einheit', {
    type: 'text', value: zeile().einheit, placeholder: 'Einheit',
    title: 'Einheit des Ergebnisses, z.B. kN/m^2 -- leer: frei',
    on: { change: (e) => sofortUebernehmen(() => { zeile().einheit = e.target.value.trim(); }) },
  });
  return { art: 'formel', feld, einheit, knoten: [feld, einheit] };
}

function projektwertzeile(zeile) {
  const name = formelfeld(zeile().name, (wert) => {
    zeile().name = wert;
    spaeterUebernehmen();
  }, { klein: true });
  const auswahl = el('select.gl-projektwert', {
    title: 'Gerechneter Wert des Projekts',
    on: {
      change: (e) => sofortUebernehmen(() => {
        zeile().wert_id = e.target.value;
        if (!zeile().name) zeile().name = namensvorschlag(e.target.value);
      }),
    },
  });
  return { art: 'projektwert', feld: name, auswahl, knoten: [auswahl, name] };
}

function textzeile(zeile) {
  const text = el('input.gl-text', {
    type: 'text', value: zeile().text, placeholder: 'Text',
    on: { change: (e) => sofortUebernehmen(() => { zeile().text = e.target.value; }) },
  });
  return { art: 'text', text, knoten: [text] };
}

const BAUER = { formel: formelzeile, projektwert: projektwertzeile, text: textzeile };

function aufbauen(blatt) {
  const kennung = blatt.kennung;
  const zeilen = blatt.zeilen.map((z, i) => {
    const teil = (BAUER[z.art] || formelzeile)(() => blattVon(kennung).zeilen[i], kennung, i);
    teil.ergebnis = el('div.gl-ergebnis');
    teil.wurzel = el(`div.gl-zeile.ist-${z.art}`, {}, [
      el('span.gl-nummer', { text: String(i + 1) }),
      el('div.gl-eingabe', {}, teil.knoten),
      teil.ergebnis,
      el('button.weg', {
        text: '×', title: 'Zeile entfernen',
        on: { click: () => zeileEntfernen(kennung, i) },
      }),
    ]);
    return teil;
  });

  const name = el('input.gl-name', {
    type: 'text', value: blatt.name, title: 'Name des Blatts',
    on: {
      change: (e) => sofortUebernehmen(() => {
        blattVon(kennung).name = e.target.value.trim() || blattVon(kennung).name;
      }),
    },
  });
  const anfuegen = (text, art) => el('button.knopf-anfuegen', {
    text: `+ ${text}`, on: { click: () => zeileEinfuegen(kennung, blattVon(kennung).zeilen.length, art) },
  });

  return {
    kennung,
    struktur: strukturVon(blatt),
    name,
    zeilen,
    wurzel: el('div.gl-blatt', {}, [
      el('div.feldgruppe', {}, [
        el('h3', {}, [el('span', { text: 'Blatt' }),
          el('span', { text: 'Enter: neue Zeile · kN, mm, MPa direkt tippen' })]),
        name,
        (rasterKnoten ??= raster()),
        el('div.gl-zeilen', {}, zeilen.map((z) => z.wurzel)),
        el('div.gl-anfuegen', {}, [
          anfuegen('Formel', 'formel'), anfuegen('Projektwert', 'projektwert'),
          anfuegen('Text', 'text'),
        ]),
      ]),
    ]),
  };
}

/** Das Raster: Bausteine zum Einfügen in das zuletzt benutzte Formelfeld. */
function raster() {
  const einfuegen = (latex) => {
    const feld = letztesFeld?.isConnected ? letztesFeld
      : ansicht?.zeilen.find((z) => z.art === 'formel')?.feld;
    if (!feld || typeof feld.insert !== 'function') return;
    feld.focus();
    feld.insert(latex, { selectionMode: 'placeholder', focus: true });
    feld.dispatchEvent(new Event('input'));
  };
  return el('div.gl-raster', {}, RASTER.map(([gruppe, bausteine]) => el('div.gl-gruppe', {}, [
    el('span.gl-gruppenname', { text: gruppe }),
    ...bausteine.map(([beschriftung, latex]) => el('button.gl-baustein', {
      type: 'button', title: latex.replace(/#[0?@]/g, '…'),
      // mousedown statt click: sonst verlöre das Formelfeld den Fokus, bevor
      // eingefügt wird, und die Auswahl darin wäre weg.
      on: { mousedown: (e) => { e.preventDefault(); einfuegen(latex); } },
    }, [span(beschriftung)])),
  ])));
}

// ===========================================================================
// Auffrischen
// ===========================================================================

/** «f_{cd}» für f_cd des Betons -- der Kern schlägt nur vor, was er auch liest. */
function namensvorschlag(id) {
  return zustand.loesung?.werte?.[id]?.blattname || '';
}

/** Die Werte, die ein Blatt lesen kann -- nach Bestandteil gruppiert. */
function wertgruppen() {
  const loesung = zustand.loesung;
  if (!loesung?.werte) return [];
  const namen = {};
  for (const m of Object.values(loesung.zuordnung?.materialien || {})) namen[m.namensraum] = m.name;
  for (const q of Object.values(loesung.zuordnung?.querschnitte || {})) namen[q.namensraum] = q.name;
  const gruppen = new Map();
  for (const w of Object.values(loesung.werte)) {
    const raum = w.id.split('.').slice(0, 2).join('.');
    if (!(raum in namen)) continue;
    if (!gruppen.has(raum)) gruppen.set(raum, []);
    gruppen.get(raum).push(w);
  }
  return [...gruppen].map(([raum, werte]) => [namen[raum], werte]);
}

function auswahlFuellen(auswahl, gewaehlt) {
  const gruppen = wertgruppen();
  const schluessel = `${gewaehlt}|${gruppen.map(([n, w]) => n + w.length).join()}`;
  if (auswahl.dataset.schluessel === schluessel) return;
  auswahl.dataset.schluessel = schluessel;
  auswahl.replaceChildren(
    el('option', { value: '', text: '– Wert wählen –' }),
    ...gruppen.map(([name, werte]) => el('optgroup', { label: name }, werte.map((w) => el('option', {
      value: w.id, text: `${w.beschreibung || w.kurzname} – ${w.wert} ${w.einheit}`.trim(),
      selected: w.id === gewaehlt,
    })))));
  if (gewaehlt && auswahl.value !== gewaehlt) {
    auswahl.prepend(el('option', { value: gewaehlt, text: `${gewaehlt} (fehlt)`, selected: true }));
  }
}

function ergebnisSetzen(knoten, zeilenergebnis) {
  const inhalt = zeilenergebnis?.fehler ? `!${zeilenergebnis.fehler}`
    : (zeilenergebnis?.ergebnis ? `=${zeilenergebnis.ergebnis}` : '');
  if (knoten.dataset.inhalt === inhalt) return;
  knoten.dataset.inhalt = inhalt;
  knoten.classList.toggle('ist-fehler', !!zeilenergebnis?.fehler);
  if (zeilenergebnis?.fehler) knoten.textContent = zeilenergebnis.fehler;
  else if (zeilenergebnis?.ergebnis) setzen(`= ${zeilenergebnis.ergebnis}`, knoten, { displayMode: false });
  else knoten.textContent = '';
}

function hatFokus(knoten) {
  return knoten === document.activeElement || knoten.contains(document.activeElement);
}

/** Ein Formelfeld auf den Stand des Projekts -- nicht, während jemand darin tippt. */
function feldSetzen(feld, wert) {
  if (!hatFokus(feld) && feld.value !== undefined && feld.value !== wert) feld.value = wert;
}

function auffrischen(blatt) {
  if (!hatFokus(ansicht.name)) ansicht.name.value = blatt.name;
  const ergebnisse = zustand.loesung?.gleichungen?.[blatt.kennung] || [];
  ansicht.zeilen.forEach((teil, i) => {
    const zeile = blatt.zeilen[i];
    if (teil.art === 'formel') {
      feldSetzen(teil.feld, zeile.latex);
      if (!hatFokus(teil.einheit)) teil.einheit.value = zeile.einheit;
    } else if (teil.art === 'projektwert') {
      auswahlFuellen(teil.auswahl, zeile.wert_id);
      feldSetzen(teil.feld, zeile.name);
    } else if (!hatFokus(teil.text)) {
      teil.text.value = zeile.text;
    }
    // Ein Ergebnis gehört zur gerechneten Fassung. Weicht die Zeile davon ab
    // -- getippt, noch nicht gerechnet --, stünde sonst ein altes Ergebnis da.
    ergebnisSetzen(teil.ergebnis, ergebnisse[i]);
  });
}

/**
 * Den Fokus aus der alten Ansicht nehmen, bevor sie verschwindet. MathLive
 * merkt sich das Feld mit Fokus und meldet es beim nächsten Fokus ab -- ist es
 * da schon aus dem Dokument, wirft das, und die neue Zeile bekommt keinen Cursor.
 */
function loslassen() {
  if (ansicht && hatFokus(ansicht.wurzel)) document.activeElement.blur();
}

function fokusNachholen() {
  if (fokusWunsch === null) return;
  const teil = ansicht.zeilen[Math.min(fokusWunsch, ansicht.zeilen.length - 1)];
  fokusWunsch = null;
  const ziel = teil?.feld || teil?.text;
  if (!ziel) return;
  // Der Cursor ans Ende: nach Backspace geht es in der Zeile davor weiter.
  customElements.whenDefined('math-field').then(() => requestAnimationFrame(() => {
    ziel.focus();
    if (ziel === teil.text) ziel.setSelectionRange(ziel.value.length, ziel.value.length);
    else ziel.executeCommand('moveToMathfieldEnd');
  }));
}

// ===========================================================================

/**
 * Zeichnet das Blatt in den Behälter -- oder lässt die stehende Ansicht, wo
 * sie ist, und frischt sie nur auf.
 */
export function blattZeichnen(behaelter, blatt) {
  mathliveLaden();
  if (!ansicht || ansicht.kennung !== blatt.kennung || ansicht.struktur !== strukturVon(blatt)) {
    loslassen();
    ansicht = aufbauen(blatt);
  }
  if (behaelter.firstChild !== ansicht.wurzel || behaelter.childNodes.length !== 1) {
    behaelter.replaceChildren(ansicht.wurzel);
  }
  auffrischen(blatt);
  fokusNachholen();
}
