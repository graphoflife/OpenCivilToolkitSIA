/**
 * materialwahl.js -- das Fenster «Neues Material».
 *
 * Ein neues Material ist eines von zwei (Benutzer, 2026-10-16):
 *
 *     Normsorte nach SIA   heisst wie die Sorte, C30/37, und bleibt, wie sie
 *                          ist -- nichts daran lässt sich ändern, auch die
 *                          Sorte nicht
 *     eigenes Material     nimmt eine Sorte als Vorlage, heisst BE1, BE2 ...
 *                          (Betonstahl S1 ..., Baustahl ST1 ...) und seine
 *                          Kennwerte sind änderbar; eine Sorte trägt es nicht
 *
 * Wie eine Art heisst, womit Kennungen und Namen eigener Materialien
 * beginnen und in welcher Folge die Sorten stehen, sagt der Katalog des
 * Kerns (`materialarten`).
 */

import { karte } from './bausteine.js';
import { auswahl, el, melden } from './dom.js';
import { dialogFenster } from './fenster.js';
import { ausVorlage, freieKennung, katalog, projektAendern, waehlen, zustand } from './zustand.js';

/** Was der Katalog über eine Materialart sagt. */
const artVon = (art) => katalog('materialarten', art);

/** Der erste freie Name eines eigenen Materials -- BE1, BE2 ... */
function eigenerName(art) {
  const vorsilbe = artVon(art).eigene;
  const vergeben = new Set(zustand.projekt.materialien.map((m) => m.name || m.sorte));
  let i = 1;
  while (vergeben.has(`${vorsilbe}${i}`)) i += 1;
  return `${vorsilbe}${i}`;
}

function anlegen(schliessen, art, sorte, eigen) {
  const kennung = freieKennung(artVon(art).kennung);
  const name = eigen ? eigenerName(art) : sorte;
  projektAendern((p) => {
    p.materialien.push(ausVorlage('material', {
      kennung, art, sorte, name, eigenstaendig: eigen,
    }));
  });
  schliessen();
  waehlen({ art: 'material', kennung });
  melden(eigen ? `«${name}» angelegt, nach ${sorte}.` : `Normsorte ${sorte} angelegt.`);
}

/**
 * Die Kopie eines Materials ist immer ein eigenes (Benutzer, 2026-10-19):
 * eine Normsorte gibt es im Projekt nur einmal. Sie heisst wie jedes eigene
 * BE2, S3 ..., steht gleich hinter dem Original, nimmt dessen Sorte als
 * Vorlage und seine Abweichungen mit.
 */
export function materialKopieren(material) {
  const kennung = freieKennung(artVon(material.art).kennung);
  const name = eigenerName(material.art);
  projektAendern((p) => {
    const i = p.materialien.findIndex((x) => x.kennung === material.kennung);
    p.materialien.splice(i + 1, 0, {
      ...structuredClone(p.materialien[i]), kennung, name, eigenstaendig: true,
    });
  });
  waehlen({ art: 'material', kennung });
  melden(`«${name}» angelegt, eine Kopie von ${material.name || material.sorte}.`);
}

/** Öffnet das Fenster für ein neues Material dieser Art: 'beton', 'betonstahl' oder 'baustahl'. */
export function materialAnlegen(art) {
  const { titel, grundlage, anlegen: sorten } = artVon(art);
  const vergeben = new Set(zustand.projekt.materialien.map((m) => m.name || m.sorte));
  const frei = sorten.filter((s) => !vergeben.has(s));
  let norm = frei[0];
  let vorlage = sorten[0];

  dialogFenster({
    titel: `Neuer ${titel}`,
    zeichen: 'material',
    zusatz: 'Normsorte nach SIA oder eigenes Material',
    klasse: '.materialwahl',
    inhalt: (schliessen) => [
      karte('Normsorte nach SIA', frei.length ? [
        el('p.materialwahl-text', {
          text: `${grundlage}. Das Material heisst wie die Sorte und lässt `
            + 'sich danach nicht mehr ändern – auch die Sorte nicht.',
        }),
        el('div.materialwahl-zeile', {}, [
          auswahl({
            werte: frei.map((s) => ({ wert: s, beschriftung: s })),
            gewaehlt: norm, titel: 'Sorte',
            beiAenderung: (s) => { norm = s; },
          }),
          el('button.knopf.knopf-haupt', {
            type: 'button', text: 'Normsorte anlegen',
            on: { click: () => anlegen(schliessen, art, norm, false) },
          }),
        ]),
      ] : [el('p.materialwahl-text', {
        text: 'Alle Normsorten stehen schon im Projekt – jede braucht es nur einmal.',
      })]),
      karte(`Eigener ${titel}`, [
        el('p.materialwahl-text', {
          text: `Die Kennwerte einer Sorte als Vorlage, danach frei änderbar. Das Material `
            + `heisst ${eigenerName(art)} und trägt keine Sorte.`,
        }),
        el('div.materialwahl-zeile', {}, [
          el('span.materialwahl-marke', { text: 'Vorlage' }),
          auswahl({
            werte: sorten.map((s) => ({ wert: s, beschriftung: s })),
            gewaehlt: vorlage, titel: 'Vorlage der Kennwerte',
            beiAenderung: (s) => { vorlage = s; },
          }),
          el('button.knopf', {
            type: 'button', text: `${eigenerName(art)} anlegen`,
            on: { click: () => anlegen(schliessen, art, vorlage, true) },
          }),
        ]),
      ]),
    ],
  });
}
