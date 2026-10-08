/**
 * cad_palette.js -- das schwebende Fenster im Zeichenfenster.
 *
 * Steht anfangs unten rechts in der Zeichnung und lässt sich an seinem Kopf
 * verschieben. Wohin man es gestellt hat, merkt sich der Browser -- als
 * Abstand von unten rechts, damit es beim Vergrössern dort bleibt. Es bleibt
 * immer ganz im Bild und lässt sich auf seinen Kopf zuklappen.
 *
 * Was darin steht, setzt das Zeichenfenster je nach Lage: in Ruhe die
 * Koordinaten des Zeigers, während eines Befehls seine Frage und die
 * Eingabefelder, bei einer Auswahl deren Eigenschaften.
 */

import { el } from './dom.js';

const ABLAGE = 'opencivil.cad.palette';

function gemerkt() {
  try {
    return { rechts: 10, unten: 10, zu: false, ...JSON.parse(localStorage.getItem(ABLAGE) || '{}') };
  } catch {
    return { rechts: 10, unten: 10, zu: false };
  }
}

function merken(lage) {
  try {
    localStorage.setItem(ABLAGE, JSON.stringify(lage));
  } catch {
    // Privater Modus: dann gilt es bis zum Neuladen.
  }
}

/** Das schwebende Fenster, eingehängt in `flaeche`. */
export function paletteBauen(flaeche) {
  const lage = gemerkt();
  const titel = el('span.cad-palette-titel');
  const zu = el('button.cad-palette-zu', {
    type: 'button', title: 'Zuklappen', text: '–',
  });
  const griff = el('span.cad-palette-griff', { text: '⠿', title: 'Verschieben' });
  const kopf = el('div.cad-palette-kopf', {}, [griff, titel, zu]);
  const koerper = el('div.cad-palette-koerper');
  const knoten = el('div.cad-palette', {}, [kopf, koerper]);
  flaeche.append(knoten);

  const halten = () => {
    const b = flaeche.clientWidth;
    const h = flaeche.clientHeight;
    if (!b || !h) return;
    const w = knoten.offsetWidth;
    const hh = knoten.offsetHeight;
    lage.rechts = Math.min(Math.max(2, lage.rechts), Math.max(2, b - w - 2));
    lage.unten = Math.min(Math.max(2, lage.unten), Math.max(2, h - hh - 2));
    knoten.style.right = `${lage.rechts}px`;
    knoten.style.bottom = `${lage.unten}px`;
  };

  const zuklappen = (wert) => {
    lage.zu = wert;
    knoten.classList.toggle('ist-zu', wert);
    zu.textContent = wert ? '+' : '–';
    zu.title = wert ? 'Aufklappen' : 'Zuklappen';
    merken(lage);
    halten();
  };
  zu.addEventListener('click', () => zuklappen(!lage.zu));
  zuklappen(lage.zu);

  kopf.addEventListener('pointerdown', (start) => {
    if (start.target === zu || start.button !== 0) return;
    start.preventDefault();
    const anfang = { ...lage };
    const bewegen = (e) => {
      lage.rechts = anfang.rechts - (e.clientX - start.clientX);
      lage.unten = anfang.unten - (e.clientY - start.clientY);
      halten();
    };
    const los = () => {
      window.removeEventListener('pointermove', bewegen);
      window.removeEventListener('pointerup', los);
      merken(lage);
    };
    window.addEventListener('pointermove', bewegen);
    window.addEventListener('pointerup', los);
  });

  return {
    knoten,
    halten,
    /** Auf, wenn es zu ist -- etwa, weil jemand Zahlen tippt, die hineingehören. */
    aufklappen() {
      if (lage.zu) zuklappen(false);
    },
    /** Titel und Inhalt setzen -- Felder mit Fokus bleiben, wenn `schluessel` gleich ist. */
    setzen(text, inhalt, schluessel = null) {
      titel.textContent = text;
      if (schluessel !== null && koerper.dataset.schluessel === schluessel) return;
      koerper.dataset.schluessel = schluessel ?? '';
      koerper.replaceChildren(...inhalt.filter(Boolean));
      halten();
    },
    koerper,
  };
}
