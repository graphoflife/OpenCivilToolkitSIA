/**
 * mathe.js -- Formeln setzen und in die Zwischenablage legen.
 *
 * KaTeX ist mitgeliefert (web/vendor/katex), nicht von einem CDN geladen. Eine
 * Bemessung, die sich ohne Internet nicht mehr anzeigen lässt, wäre für die
 * Baustelle wertlos.
 *
 * WEG NACH WORD:
 * KaTeX erzeugt neben der HTML-Darstellung auch MathML. Legt man dieses als
 * `text/html` in die Zwischenablage, fügt Word es als richtige, weiter
 * bearbeitbare Formel ein -- nicht als Bild und nicht als Text. Als Rückfall
 * liegt zusätzlich das rohe LaTeX als `text/plain` bereit; damit kommt der
 * Formeleditor von Word 365 ebenfalls zurecht, und Overleaf sowieso.
 */

const KATEX_EINSTELLUNGEN = {
  throwOnError: false,
  displayMode: true,
  strict: false,
  trust: true,
  macros: {
    '\\diameter': '\\varnothing',
  },
};

/** Setzt LaTeX in einen Knoten. Bei Fehlern erscheint der Quelltext. */
export function setzen(latex, ziel, { displayMode = true } = {}) {
  if (!window.katex) {
    ziel.textContent = latex;
    return ziel;
  }
  try {
    window.katex.render(latex, ziel, { ...KATEX_EINSTELLUNGEN, displayMode });
  } catch (fehler) {
    ziel.textContent = latex;
    ziel.title = `Formel nicht darstellbar: ${fehler.message}`;
  }
  return ziel;
}

/** Wie `setzen`, gibt aber einen neuen `<span>` zurück. */
export function span(latex, { displayMode = false } = {}) {
  const knoten = document.createElement('span');
  setzen(latex, knoten, { displayMode });
  return knoten;
}

/** Das reine MathML einer Formel, oder null wenn KaTeX es nicht liefert. */
export function alsMathML(latex) {
  if (!window.katex) return null;
  try {
    const markup = window.katex.renderToString(latex, {
      ...KATEX_EINSTELLUNGEN, output: 'mathml',
    });
    const huelle = document.createElement('div');
    huelle.innerHTML = markup;
    const mathe = huelle.querySelector('math');
    if (!mathe) return null;
    // Word braucht den Namensraum ausdrücklich am Element.
    if (!mathe.getAttribute('xmlns')) {
      mathe.setAttribute('xmlns', 'http://www.w3.org/1998/Math/MathML');
    }
    mathe.setAttribute('display', 'block');
    return mathe.outerHTML;
  } catch {
    return null;
  }
}

async function inZwischenablage(teile, rueckfallText) {
  if (navigator.clipboard && window.ClipboardItem && teile) {
    try {
      await navigator.clipboard.write([new window.ClipboardItem(teile)]);
      return true;
    } catch { /* unten weiter */ }
  }
  if (navigator.clipboard?.writeText) {
    try {
      await navigator.clipboard.writeText(rueckfallText);
      return true;
    } catch { /* unten weiter */ }
  }
  // Letzter Ausweg für Browser ohne Zwischenablage-Rechte.
  const feld = document.createElement('textarea');
  feld.value = rueckfallText;
  feld.style.position = 'fixed';
  feld.style.opacity = '0';
  document.body.append(feld);
  feld.select();
  const geklappt = document.execCommand('copy');
  feld.remove();
  return geklappt;
}

/** Legt das rohe LaTeX in die Zwischenablage (Overleaf, Word-Formeleditor). */
export function kopiereLatex(latex) {
  return inZwischenablage(
    { 'text/plain': new Blob([latex], { type: 'text/plain' }) },
    latex);
}

/** Legt die Formel als MathML ab -- Word fügt sie als Gleichung ein. */
export function kopiereFuerWord(latex) {
  const mathml = alsMathML(latex);
  if (!mathml) return kopiereLatex(latex);
  return inZwischenablage(
    {
      'text/html': new Blob([mathml], { type: 'text/html' }),
      'text/plain': new Blob([latex], { type: 'text/plain' }),
    },
    latex);
}
