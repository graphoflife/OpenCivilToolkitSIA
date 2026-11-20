/**
 * projekte.js -- die Projekte oben links: ein Reiter je Projekt, «+» für ein
 * neues.
 *
 * Ein Klick wählt ein Projekt, und darunter stehen nur dessen Einträge
 * (Benutzer, 2026-11-20). Das gezeigte trägt ×: es entfernt das Projekt nach
 * einer Rückfrage, und nie das letzte -- ohne Projekt gäbe es nichts zu
 * zeigen. Den Namen des gezeigten ändert das Feld darüber (index.html); einen
 * Namen, den schon ein anderes trägt, weist es ab, wie der Kern
 * (opencivil/projekt/mappe.py).
 *
 * Gespeichert, geöffnet und im Browser abgelegt werden alle Projekte
 * zusammen (ablage.js); gerechnet wird je Projekt.
 */

import {
  el, ersetzen, melden, undListe,
} from './dom.js';
import { nameUebernehmen } from './bausteine.js';
import { rueckfrage } from './fenster.js';
import {
  katalog, mappeAendern, naechsterName, projektAendern, projektSetzen, zustand,
} from './zustand.js';

/** Zeichnet die Reiter in `behaelter` und schreibt den Namen des gezeigten ins `namensfeld`. */
export function projekteZeichnen(behaelter, namensfeld) {
  const { mappe, projekt: gezeigt } = zustand;
  if (!mappe) return ersetzen(behaelter);
  // Wer gerade tippt, behält, was er getippt hat.
  if (document.activeElement !== namensfeld) namensfeld.value = gezeigt.name;
  const mehrere = mappe.projekte.length > 1;
  const stoffe = katalog('neu', 'projekte').materialien.map((m) => m.name).join(' und ');
  return ersetzen(behaelter, el('div.projektreihe', { role: 'tablist', 'aria-label': 'Projekte' }, [
    ...mappe.projekte.map((p) => reiter(p, p === gezeigt, mehrere)),
    el('button.knopf.knopf-zart.projekt-neu', {
      type: 'button', text: '+', title: `Neues Projekt – mit ${stoffe} und je App einer Sandbox`,
      on: { click: () => projektNeu(namensfeld) },
    }),
  ]));
}

function reiter(p, gezeigt, mehrere) {
  return el('div.projekt-reiter', { class: gezeigt ? 'ist-aktiv' : '' }, [
    el('button.projekt-knopf', {
      type: 'button', role: 'tab', 'aria-selected': String(gezeigt), text: p.name, title: p.name,
      on: { click: () => { if (!gezeigt) projektSetzen(p); } },
    }),
    gezeigt && mehrere ? el('button.projekt-weg', {
      type: 'button', text: '×', title: `«${p.name}» entfernen`, on: { click: () => entfernen(p) },
    }) : null,
  ]);
}

/**
 * Das Namensfeld über den Reitern: es nimmt keinen leeren Namen und keinen,
 * den ein anderes Projekt schon trägt. Einmal beim Start -- das Feld bleibt
 * stehen, `projekteZeichnen` schreibt nur den Namen hinein.
 */
export function namensfeldEinrichten(feld) {
  feld.addEventListener('change', () => nameUebernehmen(feld, zustand.projekt.name, {
    pruefen: (name) => (zustand.mappe.projekte.some((p) => p !== zustand.projekt && p.name === name)
      ? `«${name}» heisst schon ein anderes Projekt` : ''),
    setzen: (name) => projektAendern((p) => { p.name = name; }),
  }));
}

/**
 * Ein neues Projekt nach der Vorlage des Kerns (`katalog.neu.projekte`),
 * hinter den anderen und gleich gezeigt. Sein Name steht markiert im Feld:
 * wer tippt, benennt es.
 */
function projektNeu(namensfeld) {
  const neu = {
    ...structuredClone(katalog('neu', 'projekte')),
    name: naechsterName('Projekt', zustand.mappe.projekte),
  };
  mappeAendern((m) => m.projekte.push(neu), neu);
  namensfeld.focus();
  namensfeld.select();
  melden(`«${neu.name}» angelegt – den Namen ändert das Feld oben.`);
}

async function entfernen(p) {
  const wahl = await rueckfrage({
    titel: 'Projekt entfernen',
    zeichen: 'projekte',
    zusatz: p.name,
    text: `«${p.name}» geht weg, mit allem, was darin steht. Die anderen Projekte bleiben.`,
    wahlen: [{
      wert: 'entfernen',
      knopf: 'Entfernen',
      gefahr: true,
      erklaerung: 'Zurück kommt es nur aus einer gespeicherten Datei.',
    }],
  });
  if (wahl !== 'entfernen') return;
  const { projekte } = zustand.mappe;
  const i = projekte.indexOf(p);
  mappeAendern((m) => m.projekte.splice(i, 1), projekte[i + 1] ?? projekte[i - 1]);
  melden(`«${p.name}» entfernt.`);
}

/**
 * Öffnet eine Datei mit Projekten (ablage.js, `ausDateiLaden`): fragt, ob
 * sie die bisherigen ersetzen oder hinter ihnen dazukommen. Ein Name, den es
 * schon gibt, bekommt dann eine Nummer: «Halle» wird «Halle 2». Gezeigt wird
 * das erste aus der Datei.
 */
export async function dateiAufnehmen({ mappe, datei }) {
  const namen = (projekte) => undListe(projekte.map((p) => `«${p.name}»`));
  const zahl = mappe.projekte.length;
  const wie = await rueckfrage({
    titel: 'Datei öffnen',
    zeichen: 'projekte',
    zusatz: datei,
    text: `Darin ${zahl === 1 ? 'steht ein Projekt' : `stehen ${zahl} Projekte`}: `
      + `${namen(mappe.projekte)}.`,
    wahlen: [{
      wert: 'ersetzen',
      knopf: 'Alles ersetzen',
      gefahr: true,
      erklaerung: `Statt ${namen(zustand.mappe.projekte)}.${zustand.ungespeichert
        ? ' Was seit dem letzten Speichern geändert ist, geht verloren.' : ''}`,
    }, {
      wert: 'hinzufuegen',
      knopf: 'Hinzufügen',
      erklaerung: 'Hinter den Projekten hier. Ein Name, den es schon gibt, bekommt eine Nummer.',
    }],
  });
  if (wie === 'ersetzen') {
    projektSetzen(mappe.projekte[0], { mappe, ungespeichert: false });
    melden(`«${datei}» geöffnet: ${namen(mappe.projekte)}.`);
  } else if (wie === 'hinzufuegen') {
    const vergeben = new Set(zustand.mappe.projekte.map((p) => p.name));
    const dazu = mappe.projekte.map((p) => {
      let name = p.name;
      for (let n = 2; vergeben.has(name); n += 1) name = `${p.name} ${n}`;
      vergeben.add(name);
      return { ...p, name };
    });
    mappeAendern((m) => m.projekte.push(...dazu), dazu[0]);
    melden(`Aus «${datei}» dazugekommen: ${namen(dazu)}.`);
  }
}
