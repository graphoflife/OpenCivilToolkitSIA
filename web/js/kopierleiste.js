/**
 * kopierleiste.js -- die Knöpfe Word, TeX und MD an einer Formel oder Tabelle.
 *
 * Stehen an jedem Block, der LaTeX hergibt: in der Herleitung und im
 * Notizbuch. Einmal geschrieben, damit sie überall dieselben sind.
 */

import { el, melden } from './dom.js';
import { kopiereFuerWord, kopiereTabelleFuerWord, kopiereText } from './mathe.js';

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
