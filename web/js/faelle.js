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
 * brechen sie um.
 *
 * Jede Zelle trägt ihre Klasse, und danach setzt das Stilblatt sie. Bis
 * 2026-10-18 stand die Zeile siebenmal da, und das Stilblatt setzte ihre
 * Zellen nach ihrer Nummer (`:nth-child`, sechzehn Regeln): eine Zelle mehr
 * verschob alle danach.
 */

import { api } from './api.js';
import { hakenSchalter, namensfeld } from './bausteine.js';
import { el } from './dom.js';
import { span } from './mathe.js';
import { zustand } from './zustand.js';

/**
 * Eine Zeile. `fall` ist der Eintrag, `aendern(veraenderer)` ändert ihn im
 * Projekt; Schalter und Name gehen darüber -- fehlt `aktiv`, ist der Fall an.
 * `was` heisst der Fall am Schalter («Lastfall wird geführt»), `nameTitel`
 * und `entfernenTitel` sagen, was Name und Kreuz tun. `vorn` steht statt des
 * Schalters da, wo es keinen gibt: die Nummer einer Schicht -- eine Schicht
 * lässt sich nicht ausschalten, ohne dass die darunter nach oben rückten.
 *
 * `liste` sagt, wo der Fall steht -- `{ kennung, pfad, index }`, das Bauteil,
 * seine Liste («knickfaelle», «verformung.faelle») und die Stelle darin.
 * Dann weist das Namensfeld einen Namen ab, der dort schon vergeben ist, und
 * sagt, wo der andere steht (`nameFrei`). Ohne `liste` darf jeder Name
 * doppelt stehen: die Schichten einer Setzung.
 */
export function fallzeile({
  fall, aendern, was, nameTitel, zahlen, entfernen, entfernenTitel, liste = null,
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
    namensfeld({
      wert: fall.name, titel: nameTitel, klasse: '.fall-name',
      pruefen: liste ? (name) => nameFrei(liste, name) : undefined,
      setzen: (name) => aendern((x) => { x.name = name; }),
    }),
    oben ? el('div.fall-oben', {}, [oben]) : null,
    el('div.fall-zahlen', {}, zahlen),
    unten ? el('div.fall-unten', {}, unten) : null,
    el('button.weg.fall-weg', { text: '×', title: entfernenTitel, on: { click: entfernen } }),
  ]);
}

/**
 * Warum der Kern den Namen an dieser Stelle abwiese -- leer, wenn er ihn
 * nimmt; dieselbe Regel wie vor dem Rechnen (`fallname` im Dienst). Antwortet
 * der Kern nicht, gilt der Name: vor dem Rechnen fragt er ohnehin.
 */
async function nameFrei({ kennung, pfad, index }, name) {
  try {
    return (await api.fallname(zustand.projekt, kennung, pfad, index, name)).grund;
  } catch {
    return '';
  }
}

/**
 * Der Kopf über den Zeilen: je Zahlenspalte ihre Beschriftung -- als Text,
 * als Formelzeichen (ein Knoten) oder als Formelzeichen mit Einheit
 * (`['M_{Ed}', 'kNm']`). Ein Formelzeichen bleibt, wie es ist: gross
 * geschrieben würde aus M_y ein M_Y, aus ε ein E und aus l ein L. Dieselben
 * Spalten wie die Zeilen darunter -- und dieselbe `klasse`, wo das Stilblatt
 * sie umbrechen lässt.
 */
export function fallkopf(koepfe, { spalten = koepfe.length, klasse = '' } = {}) {
  return el(`div.fallzeile.fallkopf${klasse}`, { style: { '--felder': spalten } }, [
    el('div.fall-zahlen', {}, koepfe.map((kopf) => (typeof kopf === 'string'
      ? el('span', { text: kopf })
      : el('span.ist-formel', {}, [Array.isArray(kopf) ? formelkopf(...kopf) : kopf])))),
  ]);
}

/**
 * Ein Formelzeichen mit seiner Einheit: «M_Ed [kNm]», das Zeichen gesetzt.
 * Bis 2026-11-19 standen die Köpfe der Platte als Text da und wurden gross
 * geschrieben: «M_ED [KNM]», «L_CR [M]».
 */
export function formelkopf(zeichen, einheit = '') {
  return el('span', {}, [span(zeichen), einheit ? ` [${einheit}]` : '']);
}
