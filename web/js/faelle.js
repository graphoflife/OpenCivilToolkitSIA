/**
 * faelle.js -- die Zeile eines Falls, für alle Listen dieselbe.
 *
 * Einwirkungen und Gebrauchsfälle, Verformungsfälle, Knicknachweise,
 * Analysen, die Kombinationen des Grundbruchs, die Lastfälle des
 * gezeichneten Querschnitts und die Schichten unter einer Setzung: jede
 * Liste hat dieselbe Zeile -- oben Schalter,
 * Name und Entfernen, darunter die Zahlen, je unter ihrem Kopf (`fallkopf`).
 * Was eine Liste mehr hat, steht an fester Stelle: neben dem Namen (`oben`,
 * die Zugseite beim Knicken) oder in einer Zeile darunter (`unten`, Werte und
 * Rechenart einer Analyse). Stehen mehr Zahlen da als Spalten (`spalten`),
 * brechen sie um -- beim Lastfall des gezeichneten Querschnitts drei je Zeile.
 *
 * Jede Zelle trägt ihre Klasse, und danach setzt das Stilblatt sie. Bis
 * 2026-10-18 stand die Zeile siebenmal da, und das Stilblatt setzte ihre
 * Zellen nach ihrer Nummer (`:nth-child`, sechzehn Regeln): eine Zelle mehr
 * verschob alle danach.
 */

import { hakenSchalter } from './bausteine.js';
import { el } from './dom.js';

/**
 * Eine Zeile. `fall` ist der Eintrag, `aendern(veraenderer)` ändert ihn im
 * Projekt; Schalter und Name gehen darüber -- fehlt `aktiv`, ist der Fall an.
 * `was` heisst der Fall am Schalter («Lastfall wird geführt»), `nameTitel`
 * und `entfernenTitel` sagen, was Name und Kreuz tun. `vorn` steht statt des
 * Schalters da, wo es keinen gibt: die Nummer einer Schicht -- eine Schicht
 * lässt sich nicht ausschalten, ohne dass die darunter nach oben rückten.
 */
export function fallzeile({
  fall, aendern, was, nameTitel, zahlen, entfernen, entfernenTitel,
  oben = null, unten = null, spalten = zahlen.length, klasse = '', vorn = null,
}) {
  const an = vorn !== null || fall.aktiv !== false;
  const schalter = vorn
    || hakenSchalter(an, (wert) => aendern((x) => { x.aktiv = wert; }), was);
  schalter.classList.add('fall-schalter');
  return el(`div.fallzeile${klasse}`, {
    class: `${an ? '' : 'ist-aus'} ${oben ? 'mit-oben' : ''}`, style: { '--felder': spalten },
  }, [
    schalter,
    el('input.fall-name', {
      type: 'text', value: fall.name, title: nameTitel,
      on: {
        change: (e) => {
          const name = e.target.value;
          aendern((x) => { x.name = name; });
        },
      },
    }),
    oben ? el('div.fall-oben', {}, [oben]) : null,
    el('div.fall-zahlen', {}, zahlen),
    unten ? el('div.fall-unten', {}, unten) : null,
    el('button.weg.fall-weg', { text: '×', title: entfernenTitel, on: { click: entfernen } }),
  ]);
}

/**
 * Der Kopf über den Zeilen: je Zahlenspalte ihre Beschriftung, als Text oder
 * als Formelzeichen (ein Knoten) -- das bleibt, wie es ist: gross
 * geschrieben würde aus M_y ein M_Y. Dieselben Spalten wie die Zeilen darunter.
 */
export function fallkopf(koepfe, { spalten = koepfe.length } = {}) {
  return el('div.fallzeile.fallkopf', { style: { '--felder': spalten } }, [
    el('div.fall-zahlen', {}, koepfe.map((kopf) => (typeof kopf === 'string'
      ? el('span', { text: kopf }) : el('span.ist-formel', {}, [kopf])))),
  ]);
}
