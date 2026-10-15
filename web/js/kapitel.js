/**
 * kapitel.js -- die Kapitel eines Bauteils als Knöpfe, jedes mit seinem Fenster.
 *
 * Unter den Panels eines Bauteils stehen keine langen Eingabelisten, sondern
 * Knöpfe, in Gruppen: Nachweise, Analysen, Werkzeug. Ein Knopf zeigt sein
 * Zeichen, seinen Namen und darunter klein, was eingestellt ist --
 * «2 Einwirkungen», «aus». Ein Klick öffnet das Fenster mit den Eingaben
 * (`fenster.js`).
 *
 * Welche Kapitel ein Bauteil hat, sagt seine Art: die Platte in `editor.js`,
 * die Querschnittsanalyse in `querschnittsanalyse.js`. Hier steht nur, wie
 * Knopf und Fenster daraus werden. Ein Kapitel ist ein Eintrag mit
 *
 *   schluessel   zugleich der Name seines Zeichens (sinnbilder.js) und
 *                seines Fragezeichens
 *   name         auf dem Knopf -- mit weichem Trennstrich, wo ein Wort
 *                breiter ist als der Knopf
 *   titel        über dem Fenster
 *   bezug(e)     worauf sich die Eingaben beziehen, unter dem Titel (nicht jedes)
 *   inhalt(e)    die Knoten des Fensters
 *   stand(e)     die kleine Zeile des Knopfs: {an, text}
 *
 * `e` ist der Eintrag des Bauteils, wie er im Projekt steht.
 */

import { panel } from './bausteine.js';
import { el } from './dom.js';
import { fenster, fensterOeffnen } from './fenster.js';
import { sinnbild } from './sinnbilder.js';
import { zustand } from './zustand.js';

/** «1 Einwirkung», «3 Einwirkungen». */
export function anzahl(n, eins, mehr) {
  return `${n} ${n === 1 ? eins : mehr}`;
}

/** Wie viele Zeilen einer Liste gerechnet werden -- ausgeschaltete stehen nur da. */
export const eingeschaltet = (liste) => (liste || []).filter((k) => k.aktiv !== false).length;

/** Ein Schalter als Stand: ein oder aus. */
export const schalter = (an) => ({ an, text: an ? 'ein' : 'aus' });

/**
 * Was eine Gebrauchsliste rechnet: der Anteil der Tragsicherheit, wenn er
 * eingeschaltet ist, und die eigenen Lastfälle -- «60 % + 1 Fall».
 */
export function gebrauchsstand(liste) {
  const eigene = eingeschaltet(liste.faelle);
  const teile = [
    liste.aus_tragsicherheit ? `${liste.anteil} %` : null,
    eigene ? anzahl(eigene, 'Fall', 'Fälle') : null,
  ].filter(Boolean);
  return { an: teile.length > 0, text: teile.join(' + ') || 'kein Fall' };
}

/**
 * Die sechs Spannung-Dehnung-Analysen als Kapitel, je Art aus dem Katalog:
 * der Name auf dem Knopf kurz, über dem Fenster lang. `inhalt(e, art)` baut
 * das Fenster, `bezug(e)` steht unter seinem Titel.
 */
export function analysenKapitel({ inhalt, bezug }) {
  return (zustand.katalog?.spannungsanalyse?.arten || []).map((a) => ({
    schluessel: a.wert,
    name: a.beschriftung, titel: a.titel,
    bezug: (e) => `Spannung-Dehnung-Analyse · ${bezug(e)}`,
    inhalt: (e) => inhalt(e, a.wert),
    stand: (e) => {
      const n = eingeschaltet((e.spannungsfaelle || []).filter((k) => k.art === a.wert));
      return { an: n > 0, text: n ? anzahl(n, 'Bild', 'Bilder') : 'kein Bild' };
    },
  }));
}

/**
 * «M–E_eq» mit tiefgestelltem eq: was hinter einem Unterstrich steht, ist
 * ein Index.
 */
function mitIndex(text) {
  return text.split(/_(\w+)/).map((teil, i) => (i % 2 ? el('sub', { text: teil }) : teil));
}

function kachel(eintrag, kapitel) {
  const { an, text } = kapitel.stand(eintrag);
  return el('button.kachel', {
    type: 'button', class: an ? 'ist-an' : '', title: kapitel.titel,
    'aria-haspopup': 'dialog',
    on: { click: () => fensterOeffnen(kapitel.schluessel) },
  }, [
    sinnbild(kapitel.schluessel),
    el('span.kachel-name', {}, mitIndex(kapitel.name)),
    el('span.kachel-stand', { text }),
  ]);
}

/**
 * Das Panel der Knöpfe: je Gruppe `{titel, kapitel}` eine Überschrift und
 * ihre Knöpfe. `schluessel` merkt sich, ob das Panel zugeklappt ist.
 */
export function kapitelPanel(eintrag, gruppen, { schluessel, titel }) {
  return panel({ schluessel, titel }, gruppen.flatMap((g) => [
    el('div.kachel-gruppe', { text: g.titel }),
    el('div.kacheln', {}, g.kapitel.map((k) => kachel(eintrag, k))),
  ]));
}

/**
 * Das offene Fenster eines Bauteils -- oder null, wenn der Schlüssel zu
 * keinem seiner Kapitel gehört. Unter dem Titel steht der Name des Bauteils
 * und, wo Schnittgrössen eingegeben werden, worauf sie sich beziehen.
 * `hilfe(schluessel)` liefert das Fragezeichen, oder null.
 */
export function kapitelFenster(eintrag, gruppen, schluessel, hilfe) {
  const kapitel = gruppen.flatMap((g) => g.kapitel).find((k) => k.schluessel === schluessel);
  if (!kapitel) return null;
  return fenster({
    titel: kapitel.titel,
    zeichen: kapitel.schluessel,
    zusatz: [eintrag.name, kapitel.bezug?.(eintrag)].filter(Boolean).join(' · '),
    hilfe: hilfe(kapitel.schluessel),
    inhalt: kapitel.inhalt(eintrag),
  });
}
