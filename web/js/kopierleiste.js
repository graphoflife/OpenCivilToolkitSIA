/**
 * kopierleiste.js -- die Knöpfe Word, TeX und MD an einer Formel oder Tabelle.
 *
 * Stehen an jedem Block, der LaTeX hergibt: in der Herleitung und im
 * Notizbuch. Einmal geschrieben, damit sie überall dieselben sind.
 */

import { el, melden } from './dom.js';
import {
  kopiereFormelnFuerWord, kopiereFuerWord, kopiereTabelleFuerWord, kopiereText,
} from './mathe.js';

export function werkzeugKnopf(text, titel, tun) {
  return el('button.knopf.knopf-zart', {
    text, title: titel,
    on: {
      click: async (e) => { e.stopPropagation(); await tun(); },
    },
  });
}

/**
 * Die drei Kopierknöpfe.
 *
 * @param block  `{latex, markdown}`, bei einer Tabelle dazu `{kopf, zeilen}`:
 *   Word bekommt dann eine echte Tabelle statt einer Formel. Das Markdown
 *   kommt fertig aus dem Kern -- der Block, wie er im Markdown-Bericht steht.
 */
export function werkzeugleiste(block) {
  const tabelle = block.kopf !== undefined;
  const was = tabelle ? 'Tabelle' : 'Formel';
  return el('div.gleichung-werkzeug', {}, [
    werkzeugKnopf('Word', `Als ${was} für Word kopieren`, async () => {
      await (tabelle
        ? kopiereTabelleFuerWord(block.kopf, block.zeilen)
        : kopiereFuerWord(block.latex));
      melden(`${was} kopiert → in Word Strg+V.`);
    }),
    werkzeugKnopf('TeX', 'LaTeX-Quelltext kopieren', async () => {
      await kopiereText(block.latex);
      melden('LaTeX kopiert.');
    }),
    block.markdown
      ? werkzeugKnopf('MD', 'Als Markdown kopieren', async () => {
        await kopiereText(block.markdown);
        melden('Markdown kopiert.');
      })
      : null,
  ]);
}

/**
 * Dieselben drei Knöpfe für mehrere Formeln auf einmal -- die Kurzform
 * eines Nachweises. Word bekommt jede als eigene Gleichung, mit Titel und
 * Normstelle davor; TeX jede in `\[ … \]`.
 *
 * @param bloecke  Gleichungen `{titel, referenz, latex, markdown}`
 */
export function formelnLeiste(bloecke) {
  const titel = (b) => [b.titel, b.referenz ? `(${b.referenz})` : ''].filter(Boolean).join(' ');
  return el('div.formeln-werkzeug', {}, [
    werkzeugKnopf('Word', 'Alle Formeln für Word kopieren', async () => {
      await kopiereFormelnFuerWord(bloecke.map((b) => ({ titel: titel(b), latex: b.latex })));
      melden('Formeln kopiert → in Word Strg+V.');
    }),
    werkzeugKnopf('TeX', 'Alle Formeln als LaTeX kopieren', async () => {
      await kopiereText(bloecke.map((b) => `\\[\n${b.latex}\n\\]`).join('\n\n'));
      melden('LaTeX kopiert.');
    }),
    werkzeugKnopf('MD', 'Alle Formeln als Markdown kopieren', async () => {
      await kopiereText(bloecke.map((b) => b.markdown).join('\n\n'));
      melden('Markdown kopiert.');
    }),
  ]);
}
