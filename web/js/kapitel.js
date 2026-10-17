/**
 * kapitel.js -- die Kapitel eines Bauteils als Knöpfe, jedes mit seinem Fenster.
 *
 * Unter den Panels eines Bauteils stehen keine langen Eingabelisten, sondern
 * Knöpfe, in Gruppen: Nachweise, Analysen, Werkzeug. Ein Knopf zeigt sein
 * Zeichen, seinen Namen und darunter klein, was eingestellt ist --
 * «2 Einwirkungen», «aus». Ein Klick öffnet das Fenster mit den Eingaben
 * (`fenster.js`).
 *
 * Welche Kapitel ein Bauteil hat, sagt seine Art: die Platte in
 * `plattenkapitel.js`, die Querschnittsanalyse in `querschnittsanalyse.js`
 * -- die Nachweise, die beide gleich führen, und die Analysen baut für
 * beide `nachweise.js`. Hier steht nur, wie Knopf und Fenster daraus
 * werden. Ein Kapitel ist ein Eintrag mit
 *
 *   schluessel   zugleich der Name seines Zeichens (sinnbilder.js)
 *   name         auf dem Knopf -- mit weichem Trennstrich, wo ein Wort
 *                breiter ist als der Knopf
 *   titel        über dem Fenster
 *   bezug(e)     worauf sich die Eingaben beziehen, unter dem Titel (nicht jedes)
 *   hilfe        was hinter dem Fragezeichen steht: {zeilen, formel} (nicht jedes)
 *   inhalt(e)    die Knoten des Fensters
 *   stand(e)     die kleine Zeile des Knopfs: {an, text}
 *
 * `e` ist der Eintrag des Bauteils, wie er im Projekt steht.
 */

import { erklaerung, panel } from './bausteine.js';
import { el } from './dom.js';
import { fenster, fensterOeffnen } from './fenster.js';
import { sinnbild } from './sinnbilder.js';

/** «1 Einwirkung», «3 Einwirkungen». */
function anzahl(n, eins, mehr) {
  return `${n} ${n === 1 ? eins : mehr}`;
}

/** Wie viele Zeilen einer Liste gerechnet werden -- ausgeschaltete stehen nur da. */
const eingeschaltet = (liste) => (liste || []).filter((k) => k.aktiv !== false).length;

/** Eine Liste als Stand: «2 Fälle», ohne eingeschaltete Zeile `keins` -- «kein Fall». */
export function zeilenstand(liste, eins, mehr, keins) {
  const n = eingeschaltet(liste);
  return { an: n > 0, text: n ? anzahl(n, eins, mehr) : keins };
}

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
 * und, wo Schnittgrössen eingegeben werden, worauf sie sich beziehen. Ein
 * Fragezeichen hat es, wo das Kapitel eine Hilfe mitbringt -- die Analysen
 * und die Suche haben keine.
 */
export function kapitelFenster(eintrag, gruppen, schluessel) {
  const kapitel = gruppen.flatMap((g) => g.kapitel).find((k) => k.schluessel === schluessel);
  if (!kapitel) return null;
  const { hilfe } = kapitel;
  return fenster({
    titel: kapitel.titel,
    zeichen: kapitel.schluessel,
    zusatz: [eintrag.name, kapitel.bezug?.(eintrag)].filter(Boolean).join(' · '),
    hilfe: hilfe ? erklaerung(hilfe.zeilen, hilfe.formel) : null,
    inhalt: kapitel.inhalt(eintrag),
  });
}
