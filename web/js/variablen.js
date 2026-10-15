/**
 * variablen.js -- der Variablen-Beobachter rechts, wenn ein Skript gewählt ist.
 *
 * Wie in Spyder: rechts statt der Berechnung die Variablen der Sitzung, je
 * mit Name, Typ, Grösse und Wert (Benutzer, 2026-10-15). Was darin steht,
 * liefert die Sitzung nach jedem Lauf (`opencivil/konsole/sitzung.py`); hier
 * wird es nur gezeigt. Je Variable zwei Zeilen statt einer Tabelle: die
 * rechte Tafel ist oft schmal. Ein Klick klappt den ganzen Wert auf.
 */

import { el, ersetzen } from './dom.js';
import { konsole } from './konsole.js';

/** Welche Variablen aufgeklappt sind -- über das Neuzeichnen nach einem Lauf hinweg. */
const offen = new Set();

function variable(v) {
  const knoten = el('details.py-variable', { open: offen.has(v.name) }, [
    el('summary', {}, [
      el('span.py-v-name', { text: v.name }),
      el('span.py-v-typ', { text: [v.typ, v.groesse].filter(Boolean).join(' · ') }),
      el('code.py-v-wert', { text: v.wert }),
    ]),
    el('pre.py-v-lang', { text: v.lang }),
  ]);
  knoten.addEventListener('toggle', () => {
    if (knoten.open) offen.add(v.name);
    else offen.delete(v.name);
  });
  return knoten;
}

export function variablenZeichnen(behaelter) {
  const variablen = konsole.variablen;
  if (!variablen.length) {
    return ersetzen(behaelter, el('div.leer', {}, [
      el('p', { text: 'Noch keine Variablen.' }),
      el('p', { text: 'Was ein Skript oder die Konsole anlegt, steht hier.' }),
    ]));
  }
  return ersetzen(behaelter, el('div.blatt.py-variablen', {}, variablen.map(variable)));
}
