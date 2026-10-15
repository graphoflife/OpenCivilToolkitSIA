/**
 * kapitel.js -- die Kapitel einer Platte als Knöpfe, jedes mit seinem Fenster.
 *
 * Unter der Bewehrung stehen keine langen Eingabelisten mehr, sondern
 * Knöpfe: die sieben Nachweise, die sechs Spannung-Dehnung-Analysen und die
 * Suche nach der Bewehrung. Ein Knopf zeigt sein Zeichen, seinen Namen und
 * darunter klein, was eingestellt ist -- «2 Einwirkungen», «aus». Ein Klick
 * öffnet das Fenster mit den Eingaben (`fenster.js`); was darin steht,
 * liefert `nachweise.js`.
 *
 * Jedes Kapitel steht hier einmal, mit allem, was Knopf und Fenster von ihm
 * wissen müssen. Die Analysen kommen aus dem Katalog des Kerns: ihre Namen
 * stehen dort, wo sie gerechnet werden.
 */

import { panel } from './bausteine.js';
import { el } from './dom.js';
import { fenster, fensterOeffnen } from './fenster.js';
import {
  analyseInhalt, automatikInhalt, duktilitaetInhalt, fliessenGefordert, haeufigInhalt,
  hilfe, jeB, knickInhalt, quasistaendigInhalt, sproedeInhalt, sucheLaeuft,
  tragsicherheitInhalt, zwangInhalt,
} from './nachweise.js';
import { sinnbild } from './sinnbilder.js';
import { zustand } from './zustand.js';

/** «1 Einwirkung», «3 Einwirkungen». */
function anzahl(n, eins, mehr) {
  return `${n} ${n === 1 ? eins : mehr}`;
}

const eingeschaltet = (liste) => (liste || []).filter((k) => k.aktiv !== false).length;

/** Ein Schalter als Stand: ein oder aus. */
const schalter = (an) => ({ an, text: an ? 'ein' : 'aus' });

/**
 * Was eine Gebrauchsliste rechnet: der Anteil der Tragsicherheit, wenn er
 * eingeschaltet ist, und die eigenen Lastfälle -- «60 % + 1 Fall».
 */
function gebrauchsstand(liste) {
  const eigene = eingeschaltet(liste.faelle);
  const teile = [
    liste.aus_tragsicherheit ? `${liste.anteil} %` : null,
    eigene ? anzahl(eigene, 'Fall', 'Fälle') : null,
  ].filter(Boolean);
  return { an: teile.length > 0, text: teile.join(' + ') || 'kein Fall' };
}

/** Worauf sich die Eingaben beziehen, unter dem Titel des Fensters. */
const mitQuerkraft = (q) => `${jeB(q)} · V je m`;

/**
 * Die Nachweise. Der Schlüssel nennt zugleich ihr Zeichen (sinnbilder.js)
 * und ihr Fragezeichen (`hilfe`). `name` steht auf dem Knopf -- mit weichem
 * Trennstrich, wo ein Wort breiter ist als der Knopf --, `titel` über dem
 * Fenster; `bezug` sagt, worauf sich die Schnittgrössen beziehen -- nur wo
 * welche eingegeben werden. `stand` liefert die kleine Zeile des Knopfs:
 * `{an, text}`.
 */
const NACHWEISE = [
  {
    schluessel: 'tragsicherheit',
    name: 'Trag\u00adsicherheit', titel: 'Tragsicherheitsnachweise', bezug: mitQuerkraft,
    inhalt: tragsicherheitInhalt,
    stand: (q) => {
      const n = eingeschaltet(q.kombinationen);
      return { an: n > 0, text: n ? anzahl(n, 'Einwirkung', 'Einwirkungen') : 'keine Einwirkung' };
    },
  },
  {
    schluessel: 'knicken',
    name: 'Knicken', titel: 'Knicken', bezug: jeB,
    inhalt: knickInhalt,
    stand: (q) => {
      const n = eingeschaltet(q.knickfaelle);
      return { an: n > 0, text: n ? anzahl(n, 'Fall', 'Fälle') : 'kein Fall' };
    },
  },
  {
    schluessel: 'duktilitaet',
    name: 'Duktilität', titel: 'Duktilitätsnachweis',
    inhalt: duktilitaetInhalt,
    stand: (q) => schalter(!!q.duktilitaet),
  },
  {
    schluessel: 'sproede',
    name: 'Sprödes Versagen', titel: 'Nachweis gegen sprödes Versagen',
    inhalt: sproedeInhalt,
    stand: (q) => schalter(!!q.sproede),
  },
  {
    schluessel: 'zwang',
    name: 'Riss bei Zwang', titel: 'Rissbreitenbegrenzung bei Zwang',
    inhalt: zwangInhalt,
    // Die Begrenzung auf 500 mm ist kein eigener Nachweis, sie ändert die
    // beiden anderen.
    stand: (q) => {
      const teile = [q.zwaengung ? 'N' : null, q.zwaengung_biegung ? 'M' : null].filter(Boolean);
      return { an: teile.length > 0, text: teile.length ? `auf ${teile.join(' und ')}` : 'aus' };
    },
  },
  {
    schluessel: 'quasistaendig',
    name: 'Stahlspannung quasi-ständig',
    titel: 'Stahlspannungsbegrenzung bei quasi-ständigen Lastfällen', bezug: jeB,
    inhalt: quasistaendigInhalt,
    stand: (q) => gebrauchsstand(q.quasistaendig),
  },
  {
    schluessel: 'haeufig',
    name: 'Fliessen häufig', titel: 'Verhindern des Fliessens für häufige Lastfälle',
    bezug: jeB,
    inhalt: haeufigInhalt,
    stand: (q) => (fliessenGefordert(q) ? gebrauchsstand(q.haeufig)
      : { an: false, text: 'entfällt' }),
  },
];

/**
 * Die Analysen, je Art aus dem Katalog: der Name auf dem Knopf kurz, über
 * dem Fenster lang, und darunter, wozu es gehört.
 */
function analysen() {
  return (zustand.katalog?.spannungsanalyse?.arten || []).map((a) => ({
    schluessel: a.wert,
    name: a.beschriftung, titel: a.titel,
    bezug: (q) => `Spannung-Dehnung-Analyse · ${jeB(q)}`,
    inhalt: (q) => analyseInhalt(q, a.wert),
    stand: (q) => {
      const n = eingeschaltet((q.spannungsfaelle || []).filter((k) => k.art === a.wert));
      return { an: n > 0, text: n ? anzahl(n, 'Bild', 'Bilder') : 'kein Bild' };
    },
  }));
}

const SUCHE = {
  schluessel: 'automatik',
  name: 'Bewehrung suchen', titel: 'Automatische Bewehrung',
  inhalt: automatikInhalt,
  stand: (q) => (sucheLaeuft(q.kennung) ? { an: true, text: 'sucht …' }
    : { an: false, text: q.automatik_dicke ? 'mit Dicke' : '' }),
};

function alleKapitel() {
  return [...NACHWEISE, ...analysen(), SUCHE];
}

/**
 * «M–E_eq» mit tiefgestelltem eq: was hinter einem Unterstrich steht, ist
 * ein Index.
 */
function mitIndex(text) {
  return text.split(/_(\w+)/).map((teil, i) => (i % 2 ? el('sub', { text: teil }) : teil));
}

function kachel(querschnitt, kapitel) {
  const { an, text } = kapitel.stand(querschnitt);
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

function gruppe(titel, querschnitt, kapitel) {
  return [
    el('div.kachel-gruppe', { text: titel }),
    el('div.kacheln', {}, kapitel.map((k) => kachel(querschnitt, k))),
  ];
}

/** Das Panel unter der Bewehrung: drei Gruppen von Knöpfen. */
export function kapitelPanel(querschnitt) {
  return panel({ schluessel: 'platte/Kapitel', titel: 'Nachweise und Analysen' }, [
    ...gruppe('Nachweise', querschnitt, NACHWEISE),
    ...gruppe('Spannung-Dehnung-Analysen', querschnitt, analysen()),
    ...gruppe('Werkzeug', querschnitt, [SUCHE]),
  ]);
}

/**
 * Das offene Fenster einer Platte -- oder null, wenn der Schlüssel zu keinem
 * Kapitel gehört. Unter dem Titel steht der Name der Platte und, wo M und N
 * eingegeben werden, worauf sie sich beziehen.
 */
export function plattenFenster(querschnitt, schluessel) {
  const kapitel = alleKapitel().find((k) => k.schluessel === schluessel);
  if (!kapitel) return null;
  return fenster({
    titel: kapitel.titel,
    zeichen: kapitel.schluessel,
    zusatz: [querschnitt.name, kapitel.bezug?.(querschnitt)].filter(Boolean).join(' · '),
    hilfe: hilfe(kapitel.schluessel),
    inhalt: kapitel.inhalt(querschnitt),
  });
}
