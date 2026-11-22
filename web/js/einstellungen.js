/**
 * einstellungen.js -- das Zahnrad oben rechts.
 *
 * Was selten gebraucht wird und nicht aus Versehen geschehen soll, steht
 * hinter dem Zahnrad, in einem Fenster über der ganzen Seite -- nicht offen
 * in der Kopfleiste (Benutzer, 2026-11-22). Heute ist es eines: alles
 * zurücksetzen, was die Seite im Browser abgelegt hat
 * (`allesZuruecksetzen`, ablage.js). Das Fenster sagt, was dabei weggeht,
 * mit den Namen der Projekte; wer etwas behalten will, speichert es im
 * selben Fenster als Datei. Zurückgesetzt wird erst nach einer Rückfrage.
 *
 * Das Fenster braucht den Kern nicht: es geht auch auf, wenn er nicht
 * startet -- gerade dann kann ein Neubeginn helfen.
 */

import { el, undListe } from './dom.js';
import { dialogFenster, rueckfrage } from './fenster.js';
import { allesZuruecksetzen, gerettete } from './ablage.js';
import { sinnbild } from './sinnbilder.js';
import { zustand } from './zustand.js';

/**
 * @param knopf      das Zahnrad in der Kopfleiste
 * @param speichern  was «Speichern» daneben tut -- dieselbe Funktion, keine zweite
 */
export function einstellungenEinrichten(knopf, { speichern }) {
  knopf.append(sinnbild('einstellungen'));
  knopf.addEventListener('click', () => einstellungenZeigen(speichern));
}

function einstellungenZeigen(speichern) {
  dialogFenster({
    titel: 'Einstellungen',
    zeichen: 'einstellungen',
    klasse: '.einstellungen',
    inhalt: (schliessen) => [
      el('h3', { text: 'Alles zurücksetzen' }),
      el('p', { text: wasWeggeht() }),
      el('p', {
        text: 'Was die Seite für den Betrieb ohne Netz geladen hat, bleibt. Wer etwas '
          + 'behalten will, speichert es vorher als Datei; «Öffnen» holt es zurück.',
      }),
      el('div.einstellungen-knoepfe', {}, [
        // Ohne Kern gibt es noch keine Projekte, die sich speichern liessen.
        zustand.mappe ? el('button.knopf', {
          type: 'button', text: 'Alle Projekte speichern', on: { click: speichern },
        }) : null,
        el('button.knopf.knopf-gefahr', {
          type: 'button',
          text: 'Alles zurücksetzen …',
          on: {
            click: () => {
              schliessen();
              zuruecksetzenFragen();
            },
          },
        }),
      ]),
    ],
  });
}

/**
 * Was weggeht, mit Namen: «die 2 Projekte «Wohnhaus» und «Halle» mit ihren
 * Sandboxen, einen aufbewahrten Stand und …».
 */
function wasWeggeht() {
  const namen = (zustand.mappe?.projekte ?? []).map((p) => `«${p.name}»`);
  let projekte = 'alle Projekte mit ihren Sandboxen';
  if (namen.length === 1) projekte = `das Projekt ${namen[0]} mit seinen Sandboxen`;
  else if (namen.length) projekte = `die ${namen.length} Projekte ${undListe(namen)} mit ihren Sandboxen`;
  const n = gerettete().length;
  let aufbewahrt = '';
  if (n === 1) aufbewahrt = ', einen aufbewahrten Stand';
  else if (n) aufbewahrt = `, ${n} aufbewahrte Stände`;
  return `Löscht alles, was diese Seite in deinem Browser abgelegt hat: ${projekte}${aufbewahrt} `
    + 'und die Einstellungen der Oberfläche, etwa wo die Werkzeuge im Zeichenfenster stehen '
    + 'und welche Bereiche zugeklappt sind. Danach beginnt die Seite wie beim ersten Besuch, '
    + 'mit dem Beispiel.';
}

async function zuruecksetzenFragen() {
  const wahl = await rueckfrage({
    titel: 'Alles zurücksetzen',
    zeichen: 'einstellungen',
    text: zustand.ungespeichert
      ? 'Der jetzige Stand ist noch nicht als Datei gespeichert. Zurücksetzen lässt sich '
        + 'nicht zurücknehmen.'
      : 'Zurücksetzen lässt sich nicht zurücknehmen.',
    wahlen: [{
      wert: 'zuruecksetzen',
      knopf: 'Zurücksetzen',
      erklaerung: 'Alles im Browser geht weg; die Seite beginnt neu, mit dem Beispiel.',
      gefahr: true,
    }],
  });
  if (wahl === 'zuruecksetzen') allesZuruecksetzen();
}
