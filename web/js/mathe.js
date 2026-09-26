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
 *
 * Eine Tabelle geht als HTML-Tabelle hinüber, nicht als Formel: Word fügt
 * dann eine echte Tabelle ein, in der nur die Formelzellen Formeln sind.
 */

const KATEX_EINSTELLUNGEN = {
  throwOnError: false,
  displayMode: true,
  strict: false,
  // Kein \href, kein \htmlClass: nichts im Bericht braucht sie, und ein
  // Blatt trägt Getipptes bis hierher -- als Baum neu gesetzt, trotzdem.
  trust: false,
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

/**
 * Das reine MathML einer Formel, oder null wenn KaTeX es nicht liefert.
 * `abgesetzt` wie eine Gleichung für sich; in einer Tabellenzelle nicht.
 */
export function alsMathML(latex, { abgesetzt = true } = {}) {
  if (!window.katex) return null;
  try {
    const markup = window.katex.renderToString(latex, {
      ...KATEX_EINSTELLUNGEN, displayMode: abgesetzt, output: 'mathml',
    });
    const huelle = document.createElement('div');
    huelle.innerHTML = markup;
    const mathe = huelle.querySelector('math');
    if (!mathe) return null;
    // Word braucht den Namensraum ausdrücklich am Element.
    if (!mathe.getAttribute('xmlns')) {
      mathe.setAttribute('xmlns', 'http://www.w3.org/1998/Math/MathML');
    }
    mathe.setAttribute('display', abgesetzt ? 'block' : 'inline');
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

/**
 * Legt Text in die Zwischenablage: rohes LaTeX (Overleaf, Formeleditor von
 * Word 365) oder Markdown.
 */
export function kopiereText(text) {
  return inZwischenablage(
    { 'text/plain': new Blob([text], { type: 'text/plain' }) },
    text);
}

/** Legt die Formel als MathML ab -- Word fügt sie als Gleichung ein. */
export function kopiereFuerWord(latex) {
  const mathml = alsMathML(latex);
  if (!mathml) return kopiereText(latex);
  return inZwischenablage(
    {
      'text/html': new Blob([mathml], { type: 'text/html' }),
      'text/plain': new Blob([latex], { type: 'text/plain' }),
    },
    latex);
}

/**
 * Legt eine Tabelle ab, die Word als **Tabelle** einfügt.
 *
 * Textzellen stehen als Text in einer HTML-Tabelle, Formelzellen als MathML.
 * Als eine einzige Formel -- eine Matrix -- liesse sich die Tabelle in Word
 * weder umbrechen noch wie eine Tabelle bearbeiten. Als Rückfall liegt sie
 * mit Tabulatoren getrennt bereit, Formelzellen als LaTeX; so nimmt sie
 * auch Excel.
 *
 * @param kopf    Zellen der Kopfzeile, je `{text}` oder `{mathe}`
 * @param zeilen  Zeilen aus ebensolchen Zellen
 */
export function kopiereTabelleFuerWord(kopf, zeilen) {
  const tabelle = document.createElement('table');
  tabelle.setAttribute('border', '1');
  tabelle.style.borderCollapse = 'collapse';
  const zeileAnlegen = (teil, zellen, art) => {
    const tr = teil.insertRow();
    for (const zelle of zellen) {
      const td = document.createElement(art);
      const mathml = zelle.mathe !== undefined
        ? alsMathML(zelle.mathe, { abgesetzt: false }) : null;
      if (mathml) td.innerHTML = mathml;
      else td.textContent = zelle.mathe ?? zelle.text;
      tr.append(td);
    }
  };
  // Die Kopfzeile im thead: als Kopf ausgezeichnet, nicht bloss als erste Zeile.
  zeileAnlegen(tabelle.createTHead(), kopf, 'th');
  const rumpf = tabelle.createTBody();
  for (const zeile of zeilen) zeileAnlegen(rumpf, zeile, 'td');

  const tabulatoren = [kopf, ...zeilen]
    .map((zellen) => zellen.map((z) => z.mathe ?? z.text).join('\t'))
    .join('\n');
  return inZwischenablage(
    {
      'text/html': new Blob([tabelle.outerHTML], { type: 'text/html' }),
      'text/plain': new Blob([tabulatoren], { type: 'text/plain' }),
    },
    tabulatoren);
}
