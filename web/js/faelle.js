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
 * brechen sie um; `schmal` sind die Spalten in einem schmalen Fenster.
 * Unter der Liste steht der Knopf, der sie verlängert
 * (`anfuegenKnopf`), und was er anlegt, heisst wie er.
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
import { naechsterName, zustand } from './zustand.js';

/**
 * Eine Zeile. `fall` ist der Eintrag, `aendern(veraenderer)` ändert ihn im
 * Projekt; Schalter und Name gehen darüber -- fehlt `aktiv`, ist der Fall an.
 * `was` heisst der Fall am Schalter («Lastfall wird geführt»), `nameTitel`
 * und `entfernenTitel` sagen, was Name und Kreuz tun. `vorn` steht statt des
 * Schalters da, wo es keinen gibt: die Nummer einer Schicht -- eine Schicht
 * lässt sich nicht ausschalten, ohne dass die darunter nach oben rückten.
 *
 * Mit `nameFest` steht der Name nur da, ohne Feld, und ohne `entfernen`
 * fehlt das Kreuz: die Geschosse eines Gebäudes in der Kachel «Kern» --
 * Name und Folge gehören dort den Geschossen, der Kern wählt nur je eines.
 *
 * `liste` sagt, wo der Fall steht -- `{ kennung, pfad, index }`, das Bauteil,
 * seine Liste («knickfaelle», «verformung.faelle») und die Stelle darin.
 * Dann weist das Namensfeld einen Namen ab, der dort schon vergeben ist, und
 * sagt, wo der andere steht (`nameFrei`). Ohne `liste` darf jeder Name
 * doppelt stehen: die Schichten einer Setzung.
 *
 * `spalten` Zahlen stehen nebeneinander, die übrigen darunter. Mit `schmal`
 * sind es in einem Fenster unter 600 px nur so viele (`.bricht-um` im
 * Stilblatt): die sechs Lasten des gezeichneten Querschnitts stehen dann zu
 * dritt, ein Fall von Knicken und Kippen bricht vor den Momenten um.
 */
export function fallzeile({
  fall, aendern, was, nameTitel, zahlen, entfernen = null, entfernenTitel = '', liste = null,
  oben = null, unten = null, spalten = zahlen.length, schmal = null, klasse = '', vorn = null,
  nameFest = false,
}) {
  const an = vorn !== null || fall.aktiv !== false;
  const schalter = vorn
    || hakenSchalter(an, (wert) => aendern((x) => { x.aktiv = wert; }), was);
  schalter.classList.add('fall-schalter');
  return el(`div.fallzeile${klasse}`, {
    class: `${an ? '' : 'ist-aus'} ${oben ? 'mit-oben' : ''} ${schmal ? 'bricht-um' : ''}`,
    style: spaltenstil(spalten, schmal),
  }, [
    schalter,
    nameFest ? el('span.fall-name', { text: fall.name, title: nameTitel }) : namensfeld({
      wert: fall.name, titel: nameTitel, klasse: '.fall-name',
      pruefen: liste ? (name) => nameFrei(liste, name) : undefined,
      setzen: (name) => aendern((x) => { x.name = name; }),
    }),
    oben ? el('div.fall-oben', {}, [oben]) : null,
    el('div.fall-zahlen', {}, zahlen),
    unten ? el('div.fall-unten', {}, unten) : null,
    entfernen ? el('button.weg.fall-weg', { text: '×', title: entfernenTitel, on: { click: entfernen } })
      : null,
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
 * Spalten wie die Zeilen darunter, auch im schmalen Fenster (`schmal`).
 */
export function fallkopf(koepfe, { spalten = koepfe.length, schmal = null } = {}) {
  return el('div.fallzeile.fallkopf', {
    class: schmal ? 'bricht-um' : '', style: spaltenstil(spalten, schmal),
  }, [
    el('div.fall-zahlen', {}, koepfe.map((kopf) => (typeof kopf === 'string'
      ? el('span', { text: kopf })
      : el('span.ist-formel', {}, [Array.isArray(kopf) ? formelkopf(...kopf) : kopf])))),
  ]);
}

/** Wie viele Zahlen nebeneinander stehen -- und im schmalen Fenster, wo es eines gibt. */
function spaltenstil(spalten, schmal) {
  return schmal ? { '--felder': spalten, '--felder-schmal': schmal } : { '--felder': spalten };
}

/**
 * Ein Formelzeichen mit seiner Einheit: «M_Ed [kNm]», das Zeichen gesetzt.
 * Bis 2026-11-19 standen die Köpfe der Platte als Text da und wurden gross
 * geschrieben: «M_ED [KNM]», «L_CR [M]».
 */
export function formelkopf(zeichen, einheit = '') {
  return el('span', {}, [span(zeichen), einheit ? ` [${einheit}]` : '']);
}

/**
 * Der Knopf, der eine Liste verlängert: «+ Schicht».
 *
 * Steht unter der Liste und nicht in der Überschrift: dort ist die Stelle,
 * an der die nächste Zeile erscheint, und ein Knopf gehört dorthin, wo seine
 * Wirkung sichtbar wird. Wächst eine Liste nach oben -- die Geschosse eines
 * Gebäudes, von oben nach unten wie das Gebäude --, steht er darum über ihr.
 * Über die ganze Breite und mit gestricheltem Rand -- man sieht, dass dort
 * noch etwas hinkommt; `titel` sagt, was er mitbringt.
 *
 * Was er anlegt, heisst wie er, mit der kleinsten freien Nummer: «+ Schicht»
 * gibt «Schicht 1», dann «Schicht 2» (Benutzer, 2026-11-20 -- bis dahin gab
 * «+ Einwirkung» eine «Tragsicherheit 1»). `tun` bekommt dafür
 * `name(liste)`. Nur ein Gebrauchsfall heisst nach seiner Art, «Häufig 1»:
 * so will es der Benutzer.
 */
export function anfuegenKnopf(text, tun, { titel = null } = {}) {
  const name = (liste) => naechsterName(text, liste);
  return el('button.knopf-anfuegen', {
    type: 'button', text: `+ ${text}`, title: titel, on: { click: () => tun(name) },
  });
}
