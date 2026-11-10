/**
 * cad_app.js -- was jede App mit Zeichenfenster gleich hat.
 *
 * Ein Zeichenfenster gehört zu einem Eintrag des Projekts: es liest und
 * schreibt ihn über seine Kennung, gilt nur im Projekt, in dem es entstand,
 * und wer die Kennung neu vergibt, findet ein leeres. Das steht hier einmal
 * (`cadApp`); die Apps -- Querschnittsanalyse (qa_zeichnung.js),
 * Balkensystem (bs_zeichnung.js), Durchstanzen (ds_zeichnung.js) -- geben
 * nur dazu, was sie selbst wissen. Dazu die Liste unter dem Fenster, die
 * markiert, was gewählt ist, und die Bausteine der schwebenden Fenster: eine
 * Zeile mit Feld und Einheit, die Felder für die Lage eines Punktes, was
 * «Alles zeigen» ins Bild nimmt und die Meldungen des Kerns als Titel.
 *
 * Bis 2026-11-10 stand das dreimal da, je mit eigenem Leser des Eintrags
 * und eigenem Vergessen.
 */

import { imSpiel } from './cad_auswahl.js';
import {
  cadBereich, cadFenster, cadVergessen, cadWaehlen,
} from './cad_fenster.js';
import { el, svgEl, zahlfeld } from './dom.js';
import {
  aendern, beimVergessen, eintragAendern, eintragVon, zustand,
} from './zustand.js';

/**
 * Die Zeichenfenster einer App. `praefix` trennt sie von denen anderer
 * Apps, `teile(kennung)` liefert, was der Adapter darüber hinaus weiss --
 * Einstellung, Arten, Zeichnen, schwebendes Fenster (cad_fenster.js).
 * `einrichten(a)` hängt an das Fenster, was die App an ihm braucht. Wer eine
 * Kennung vergisst (`ansichtVergessen`), vergisst auch ihr Fenster.
 */
export function cadApp(praefix, teile, einrichten = () => {}) {
  const schluessel = (kennung) => `${praefix}:${kennung}`;
  beimVergessen((kennung) => cadVergessen(schluessel(kennung)));
  const fensterVon = (kennung) => {
    const a = cadFenster(schluessel(kennung), () => {
      const projekt = zustand.projekt;
      return {
        gilt: () => zustand.projekt === projekt,
        zeichnung: () => eintragVon(kennung),
        schreiben: (veraenderer) => eintragAendern(kennung, veraenderer),
        tafelNeu: () => aendern({}, 'zeichnung'),
        gezeichnet: listeMarkieren,
        ...teile(kennung),
      };
    });
    einrichten(a);
    return a;
  };
  return {
    fensterVon,
    /** Wählt Elemente von aussen -- aus einer Liste oder einer Meldung. */
    waehlen: (kennung, kennungen) => cadWaehlen(fensterVon(kennung), kennungen),
  };
}

/**
 * Das Fenster mit der Liste darunter: `bauen(a)` liefert ihre Zeilen, je eine
 * mit `data-kennung`. Gebaut wird sie hier, wenn die Tafel neu entsteht, und
 * mit `listeZeichnen`, wenn der Kern antwortet; was im Fenster gewählt ist,
 * markiert sie ohne Neubau (`listeMarkieren`).
 */
export function cadBereichMitListe(a, bauen) {
  a.liste = { knoten: el('div.qa-uebersicht-huelle'), bauen };
  const bereich = cadBereich(a, [a.liste.knoten]);
  listeZeichnen(a);
  return bereich;
}

export function listeZeichnen(a) {
  if (a.liste) a.liste.knoten.replaceChildren(...a.liste.bauen(a));
}

/** Markiert in der Liste, was im Fenster gewählt ist -- ohne sie neu zu bauen. */
export function listeMarkieren(a) {
  const spiel = imSpiel(a);
  for (const z of a.liste?.knoten.querySelectorAll('[data-kennung]') || []) {
    z.classList.toggle('ist-gewaehlt', spiel.has(z.dataset.kennung));
  }
}

/** Ein Teil der Zeichnung mit den Meldungen des Kerns als Titel -- zu lesen beim Darüberfahren. */
export function mitTitel(knoten, texte) {
  if (texte?.length) {
    const t = svgEl('title');
    t.textContent = texte.join('\n');
    knoten.append(t);
  }
  return knoten;
}

/** Eine Zeile im schwebenden Fenster: Beschriftung, Feld, Einheit. */
export function cadZeile(beschriftung, eingabe, einheit = '') {
  return el('label.cad-zeile', {}, [
    el('span', { text: beschriftung }), eingabe, einheit ? el('span.einheit', { text: einheit }) : el('span'),
  ]);
}

/**
 * Zwei Felder für die Lage eines Punktes `p`, benannt nach den Achsen des
 * Fensters. Geändert wird nur, was `schluessel` wählt -- eine Ecke oder ein
 * Knoten --, was sonst dort liegt, bleibt.
 */
export function lagefelder(a, p, schluessel) {
  const setzen = (achse) => (w) => a.aendern((z) => {
    a.modell.verschieben(z, new Set([schluessel]), achse === 0 ? [w - p[0], 0] : [0, w - p[1]]);
  });
  return a.adapter.achsen.map((name, achse) => cadZeile(name, zahlfeld({
    wert: p[achse], schritt: a.raster, beiAenderung: setzen(achse),
  }), a.einstellung.einheit));
}

/** Was «Alles zeigen» ins Bild nimmt: die Punkte -- ohne Punkte das Feld `vorgabe`. */
export function umrissVon(punkte, vorgabe) {
  if (!punkte.length) return vorgabe;
  const xs = punkte.map((p) => p[0]);
  const ys = punkte.map((p) => p[1]);
  return [[Math.min(...xs), Math.min(...ys)], [Math.max(...xs), Math.max(...ys)]];
}
