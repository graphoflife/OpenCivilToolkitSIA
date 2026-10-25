/**
 * python.js -- die App «Python»: ein Skript und darunter die Konsole.
 *
 * Oben der Code des gewählten Skripts, darunter die Konsole: was die Läufe
 * ausgegeben haben, und eine Zeile für einzelne Befehle. Die Variablen stehen
 * rechts (`variablen.js`). Gerechnet wird in einem eigenen Faden
 * (`konsole.js`); die Sitzung gilt für alle Skripte, wie in Spyder.
 *
 * DIE ANSICHT BLEIBT STEHEN:
 * Solange dasselbe Skript gewählt ist, wird der Code nicht neu gezeichnet --
 * sonst spränge bei jedem Zeichen der Cursor. Erneuert wird nur, was in der
 * Konsole dazukam. Gespeichert wird der Code kurz nach dem Tippen und vor
 * jedem Lauf.
 */

import { panel } from './bausteine.js';
import { el, ersetzen } from './dom.js';
import { abbrechen, ausfuehren, konsole, leeren, neuStarten } from './konsole.js';
import { bildZeichnen } from './zeichnen.js';
import { eintragAendern, zustand } from './zustand.js';

/** So viel wird eingerückt -- wie in PEP 8. */
const EINZUG = '    ';

/** Die stehende Ansicht: das Skript, seine Knoten, wie viel der Konsole schon steht. */
let ansicht = null;

/** Wartet, bis das Tippen eine Weile ruht, und speichert dann. */
let speichernNach = null;

/** Das Skript, wie es gerade im Projekt steht -- die Ansicht hält nur seine Kennung. */
function skriptVon(kennung) {
  return (zustand.projekt?.skripte || []).find((s) => s.kennung === kennung) || null;
}

function codeSpeichern(kennung, code) {
  clearTimeout(speichernNach);
  speichernNach = null;
  if (skriptVon(kennung)?.code === code) return;
  // Als «skript»: das rechnet nichts neu, ein Skript geht in keine Rechnung.
  eintragAendern('skripte', kennung, (s) => { s.code = code; }, 'skript');
}

function laufen(kennung) {
  const code = ansicht.code.value;
  codeSpeichern(kennung, code);
  const skript = skriptVon(kennung);
  ausfuehren(code, { name: skript?.name || kennung });
}

// ===========================================================================
// Der Code
// ===========================================================================

/** Ersetzt die Auswahl im Textfeld -- so, dass Rückgängig im Browser es kennt. */
function einsetzen(feld, text) {
  feld.focus();
  if (!document.execCommand('insertText', false, text)) {
    feld.setRangeText(text, feld.selectionStart, feld.selectionEnd, 'end');
    feld.dispatchEvent(new Event('input'));
  }
}

/**
 * Tasten im Code: Tab rückt ein, Umschalt+Tab aus, Enter behält den Einzug
 * der Zeile und rückt nach einem Doppelpunkt ein, Strg+Enter führt aus.
 */
function codeTasten(e, kennung) {
  const feld = e.target;
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    e.preventDefault();
    laufen(kennung);
  } else if (e.key === 'Tab' && !e.shiftKey && feld.selectionStart === feld.selectionEnd) {
    e.preventDefault();
    einsetzen(feld, EINZUG);
  } else if (e.key === 'Tab' && e.shiftKey) {
    e.preventDefault();
    const anfang = feld.value.lastIndexOf('\n', feld.selectionStart - 1) + 1;
    const weg = feld.value.slice(anfang, anfang + EINZUG.length).match(/^ */)[0].length;
    if (weg) {
      feld.setSelectionRange(anfang, anfang + weg);
      einsetzen(feld, '');
    }
  } else if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    const anfang = feld.value.lastIndexOf('\n', feld.selectionStart - 1) + 1;
    const zeile = feld.value.slice(anfang, feld.selectionStart);
    const einzug = zeile.match(/^ */)[0] + (zeile.trimEnd().endsWith(':') ? EINZUG : '');
    einsetzen(feld, `\n${einzug}`);
  }
}

/** Die Zeilennummern neben dem Code -- so viele, wie er Zeilen hat. */
function nummernSetzen() {
  const anzahl = ansicht.code.value.split('\n').length;
  if (ansicht.nummern.childElementCount === anzahl) return;
  ersetzen(ansicht.nummern, ...Array.from({ length: anzahl }, (_, i) => el('div', { text: String(i + 1) })));
}

// ===========================================================================
// Die Konsole
// ===========================================================================

const ART_KLASSE = {
  ausgabe: 'py-aus', fehlerausgabe: 'py-fehleraus', wert: 'py-wert', fehler: 'py-fehler',
  hinweis: 'py-hinweis',
};

function ausgabeKnoten(a) {
  if (a.art === 'bild') return bildZeichnen(a.bild);
  if (a.art === 'eingabe') {
    return a.eingabe
      ? el('pre.py-eingabe', { text: a.text.split('\n').map((z, i) => `${i ? '... ' : '>>> '}${z}`).join('\n') })
      : el('div.py-lauf', { text: `▶ ${a.name}` });
  }
  return el(`pre.${ART_KLASSE[a.art] || 'py-aus'}`, { text: a.text });
}

/** Hängt an, was seit dem letzten Mal dazukam -- und fängt neu an, wenn geleert wurde. */
function konsoleAuffrischen() {
  const { ausgabe } = ansicht;
  if (konsole.ausgaben.length < ansicht.gezeigt) {
    ausgabe.replaceChildren();
    ansicht.gezeigt = 0;
  }
  const unten = ausgabe.scrollHeight - ausgabe.scrollTop - ausgabe.clientHeight < 24;
  for (const a of konsole.ausgaben.slice(ansicht.gezeigt)) ausgabe.append(ausgabeKnoten(a));
  ansicht.gezeigt = konsole.ausgaben.length;
  ansicht.leer.hidden = ansicht.gezeigt > 0;
  // Wer unten war, bleibt unten; wer zurückgerollt hat, wird nicht weggezogen.
  if (unten) ausgabe.scrollTop = ausgabe.scrollHeight;

  const laeuft = Boolean(konsole.stand);
  ansicht.stand.textContent = konsole.stand === 'startet'
    ? 'Python wird geladen …' : laeuft ? 'Läuft …' : '';
  ansicht.stand.hidden = !laeuft;
  ansicht.ausfuehren.disabled = laeuft;
  ansicht.abbrechen.disabled = !laeuft;
  ansicht.eingabe.disabled = laeuft;
}

/** Die Zeile der Konsole: Enter führt aus, Umschalt+Enter bricht um, ↑ und ↓ blättern. */
function eingabeTasten(e) {
  const feld = e.target;
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    const code = feld.value;
    if (!code.trim()) return;
    feld.value = '';
    ansicht.verlaufStelle = null;
    ausfuehren(code, { name: 'Konsole', eingabe: true });
    return;
  }
  const oben = e.key === 'ArrowUp' && !feld.value.slice(0, feld.selectionStart).includes('\n');
  const unten = e.key === 'ArrowDown' && !feld.value.slice(feld.selectionEnd).includes('\n');
  if (!(oben || unten) || !konsole.verlauf.length) return;
  e.preventDefault();
  const n = konsole.verlauf.length;
  const stelle = ansicht.verlaufStelle ?? n;
  const neu = Math.max(0, Math.min(n, stelle + (oben ? -1 : 1)));
  ansicht.verlaufStelle = neu;
  feld.value = neu < n ? konsole.verlauf[neu] : '';
}

// ===========================================================================

/** Ein Textfeld für Code: ohne Rechtschreibprüfung und ohne Grossschreibung am Anfang. */
function codefeld(tag, eigen) {
  const feld = el(tag, { autocapitalize: 'off', autocomplete: 'off', ...eigen });
  feld.spellcheck = false;
  return feld;
}

function aufbauen(skript) {
  const { kennung } = skript;
  const code = codefeld('textarea.py-code', {
    value: skript.code || '', 'aria-label': 'Python-Code', wrap: 'off',
    on: {
      keydown: (e) => codeTasten(e, kennung),
      input: (e) => {
        nummernSetzen();
        clearTimeout(speichernNach);
        speichernNach = setTimeout(() => codeSpeichern(kennung, e.target.value), 600);
      },
      scroll: (e) => { ansicht.nummern.scrollTop = e.target.scrollTop; },
    },
  });
  const nummern = el('div.py-nummern', { 'aria-hidden': 'true' });
  const name = el('input', {
    type: 'text', value: skript.name || '', title: 'Name des Skripts',
    on: {
      change: (e) => eintragAendern('skripte', kennung, (s) => {
        s.name = e.target.value.trim() || s.name;
      }, 'skript'),
    },
  });
  const ausfuehrenKnopf = el('button.knopf.knopf-haupt', {
    type: 'button', text: '▶ Ausführen', title: 'Das ganze Skript ausführen (Strg+Enter)',
    on: { click: () => laufen(kennung) },
  });
  const abbrechenKnopf = el('button.knopf', {
    type: 'button', text: '■ Abbrechen',
    title: 'Hält an, was läuft -- die Sitzung beginnt neu, die Variablen sind weg',
    on: { click: abbrechen },
  });
  const ausgabe = el('div.py-ausgabe', { role: 'log', 'aria-live': 'polite' });
  const leer = el('p.py-leer', { text: 'Noch nichts ausgeführt. Strg+Enter im Code führt das Skript aus.' });
  const stand = el('div.py-stand', { hidden: true });
  const eingabe = codefeld('textarea.py-zeile', {
    rows: 1, placeholder: '>>> Befehl, Enter führt aus', 'aria-label': 'Befehl für die Konsole',
    on: { keydown: eingabeTasten },
  });

  const wurzel = el('div.py-app', {}, [
    panel({ schluessel: 'python/Skript', titel: 'Skript', zusatz: 'Python im Browser' }, [
      el('div.py-kopf', {}, [name, ausfuehrenKnopf, abbrechenKnopf]),
      el('div.py-editor', {}, [nummern, code]),
      el('p.py-tipp', {
        text: 'numpy, pandas, die Standardbibliothek und opencivil lassen sich einbinden; '
          + 'Diagramme mit «import zeichnen as plt» -- plot, scatter, bar, xlabel, legend … '
          + 'wie bei matplotlib.',
      }),
    ]),
    panel({ schluessel: 'python/Konsole', titel: 'Konsole', zusatz: 'gilt für alle Skripte' }, [
      el('div.py-konsole', {}, [leer, ausgabe, stand]),
      el('div.py-eingabezeile', {}, [eingabe]),
      el('div.py-kopf', {}, [
        el('button.knopf', {
          type: 'button', text: 'Neu starten', title: 'Alle Variablen löschen',
          on: { click: neuStarten },
        }),
        el('button.knopf', {
          type: 'button', text: 'Leeren', title: 'Die Ausgaben löschen -- die Variablen bleiben',
          on: { click: leeren },
        }),
      ]),
    ]),
  ]);
  return {
    kennung, wurzel, code, nummern, name, ausgabe, leer, stand, eingabe,
    ausfuehren: ausfuehrenKnopf, abbrechen: abbrechenKnopf, gezeigt: 0, verlaufStelle: null,
  };
}

/**
 * Zeichnet das Skript in den Behälter -- oder lässt die stehende Ansicht, wo
 * sie noch gilt, und frischt nur die Konsole auf.
 */
export function skriptZeichnen(behaelter, skript) {
  if (!ansicht || ansicht.kennung !== skript.kennung || !behaelter.contains(ansicht.wurzel)) {
    ansicht = aufbauen(skript);
    ersetzen(behaelter, ansicht.wurzel);
  }
  // Was im Projekt steht, gilt -- ausser jemand tippt gerade oder hat eben
  // getippt, und das Speichern steht noch aus.
  if (document.activeElement !== ansicht.name) ansicht.name.value = skript.name || '';
  if (!speichernNach && document.activeElement !== ansicht.code
      && ansicht.code.value !== (skript.code || '')) {
    ansicht.code.value = skript.code || '';
  }
  nummernSetzen();
  konsoleAuffrischen();
}
