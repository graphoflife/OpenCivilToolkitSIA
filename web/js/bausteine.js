/**
 * bausteine.js -- kleine Bedienteile, die mehr als eine Tafel braucht.
 *
 * Hier steht, was Editor und Nachweistafel gemeinsam benutzen: die
 * Feldzeile, der Ja/Nein-Schalter, die Richtungswahl. Sie lagen vorher in
 * `editor.js`, und als die Nachweise ein eigenes Modul bekamen, hätten die
 * beiden sich gegenseitig importieren müssen. Ein drittes Modul, das keines
 * von beiden kennt, ist der Ausweg -- und der richtige Ort für Teile, die
 * ohnehin niemandem im Besonderen gehören.
 */

import { el } from './dom.js';
import { span } from './mathe.js';
import { panelUmschalten, zustand } from './zustand.js';

/**
 * Ein Panel der Eingaben: Kopf mit Titel, darunter der Inhalt.
 *
 * Ein Klick auf den Kopf klappt es zu oder auf -- nur nicht auf einen Knopf
 * darin, der hat seine eigene Aufgabe. `schluessel` sagt, unter welchem
 * Namen das gemerkt wird, «App/Titel», etwa `platte/Bewehrung`. `zusatz`
 * steht rechts im Kopf: ein kurzer Hinweis oder ein Knopf.
 *
 * Die Breite bestimmt nicht das Panel, sondern der Stapel, in dem es steht
 * (`.panelstapel` im Stilblatt).
 */
export function panel({ schluessel, titel, zusatz }, inhalt) {
  const knopf = el('button.panel-knopf', {
    type: 'button',
    'aria-expanded': String(!zustand.zugeklappt.has(schluessel)),
  }, [el('span.pfeil', { text: '▼' }), titel]);
  const gruppe = el('div.feldgruppe', {
    class: zustand.zugeklappt.has(schluessel) ? 'ist-zu' : '',
  }, [
    el('h3', {
      on: {
        click: (e) => {
          const anderes = e.target.closest('button, input, select, a');
          if (anderes && anderes !== knopf) return;
          const zu = panelUmschalten(schluessel);
          gruppe.classList.toggle('ist-zu', zu);
          knopf.setAttribute('aria-expanded', String(!zu));
        },
      },
    }, [
      knopf,
      typeof zusatz === 'string' ? el('span', { text: zusatz }) : zusatz,
    ]),
    ...inhalt,
  ]);
  return gruppe;
}

/**
 * Eine Zeile Beschriftung – Eingabe – Einheit.
 *
 * `beschriftung` ist entweder Klartext oder eine Liste von Knoten. Letzteres
 * für Symbole, die tiefgestellte Teile haben: `D_max` als blosser Text gelesen
 * hiesse, den Index zu unterschlagen.
 */
export function feld(beschriftung, eingabe, einheit, titel) {
  const istText = typeof beschriftung === 'string';
  return el('div.feld', {}, [
    istText
      ? el('label', { text: beschriftung, title: titel || beschriftung })
      : el('label', { title: titel || '' }, beschriftung),
    eingabe,
    el('span.einheit', { text: einheit || '' }),
  ]);
}

/**
 * Eine Einwirkung auf einer Zeile:
 *
 *     [Name] M_Ed [.] N_Ed [.] V_Ed [.] [x|y|beide] [×]
 *
 * Der Massstab fehlt bewusst: der Kern misst waagrecht, ausser nahe den
 * Spitzen der Resistenzlinie -- dort senkrecht. Welcher Weg gegriffen hat,
 * steht beim Nachweis.
 */
/**
 * Dreistellungs-Schalter für die Tragrichtung einer Einwirkung.
 *
 * Dieselben Farben wie bei den Lagen -- x blau, y kupfer -- damit man beim
 * Blick auf die Maske nicht überlegen muss, welche Richtung welche ist. `x+y`
 * bekommt ein sanftes Violett: die Mischung aus beiden.
 */
export function richtungsWahl(gewaehlt, setzen, nur = null) {
  // `nur` schränkt die Stellungen ein. Ein Querschnittsbild zeigt einen
  // Schnitt, und der liegt in einer Richtung -- «beide» wäre dort keine
  // Antwort, sondern zwei.
  const stellungen = [
    ['x', 'x', 'nur x-Richtung'],
    ['y', 'y', 'nur y-Richtung'],
    ['beide', 'x+y', 'beide Tragrichtungen'],
  ].filter(([wert]) => !nur || nur.includes(wert));
  return el('span.schalter.schalter-richtung', {
    title: 'In welcher Tragrichtung nachgewiesen wird',
  }, stellungen.map(([wert, text, beschreibung]) => el('button.schalter-halb', {
    text,
    title: beschreibung,
    class: `ist-${wert}${gewaehlt === wert ? ' ist-an' : ''}`,
    on: { click: () => { if (gewaehlt !== wert) setzen(wert); } },
  })));
}

/** Genau vier Schalter, auch wenn die Beschreibung älter ist als der Nachweis. */
export function lagenwahl(vorhanden, vorgabe) {
  const liste = Array.isArray(vorhanden) ? vorhanden : [];
  return vorgabe.map((v, i) => (i < liste.length ? !!liste[i] : v));
}

/**
 * Zweistellungs-Schalter ja/nein -- grüner Haken, rotes Kreuz.
 *
 * Beide Hälften gleich breit und die Zeichen mittig: ✓ und ✗ sind verschieden
 * breit, und bei symmetrischem Innenabstand wurde der Schalter dadurch schief.
 */
export function hakenSchalter(an, setzen, was = 'Nachweis') {
  return el('span.schalter.schalter-haken', {
    title: an ? `${was} wird geführt` : `${was} wird nicht geführt`,
  }, [
    el('button.schalter-halb.ist-ja', {
      text: '✓', title: `${was} führen`,
      class: an ? 'ist-an' : '',
      on: { click: () => { if (!an) setzen(true); } },
    }),
    el('button.schalter-halb.ist-nein', {
      text: '✗', title: `${was} nicht führen`,
      class: an ? '' : 'ist-an',
      on: { click: () => { if (an) setzen(false); } },
    }),
  ]);
}

/**
 * Ein Fragezeichen, das seine Erklärung zeigt -- beim Darüberfahren oder auf
 * Tipp.
 *
 * Die Erklärungen standen vorher offen neben den Kapitelüberschriften --
 * «x / d ≤ 0.35 bei M_Ed = 0» und ähnliches. Richtig, aber laut: wer die
 * Maske bedient, liest sie beim ersten Mal und danach nie wieder, und
 * breiter machen sie die Tafel jedes Mal.
 *
 * Ein Knopf und kein `span`: auf dem Telefon gibt es kein Darüberfahren, und
 * ohne Klick wäre die Erklärung dort gar nicht zu bekommen. Das `title`-
 * Attribut ist weg -- es zeigte dieselbe Erklärung ein zweites Mal, als
 * Systemblase über der eigenen.
 *
 * `zeilen` sind Stichwortzeilen `[[schluessel, text], …]`, `formel` die
 * Bedingung in einer Zeile.
 */
export function erklaerung(zeilen, formel = '') {
  const blase = el('span.erklaerung-blase', {}, [
    el('span.erklaerung-zeilen', {}, zeilen.map(([schluessel, text]) =>
      el('span', {}, [el('b', { text: `${schluessel}: ` }), text]))),
    formel ? el('code', { text: formel }) : null,
  ]);
  const zeichen = el('button.erklaerung-zeichen', {
    text: '?', type: 'button',
    'aria-label': 'Erklärung anzeigen', 'aria-expanded': 'false',
  });
  const zettel = el('span.erklaerung', {}, [zeichen, blase]);

  zeichen.addEventListener('click', (e) => {
    e.stopPropagation();
    const offen = zettel.classList.toggle('ist-offen');
    zeichen.setAttribute('aria-expanded', String(offen));
    // Immer nur eine offen -- sonst stapeln sich die Blasen übereinander und
    // man weiss nicht mehr, welche zu welchem Titel gehört.
    if (offen) {
      for (const andere of document.querySelectorAll('.erklaerung.ist-offen')) {
        if (andere !== zettel) andere.classList.remove('ist-offen');
      }
    }
  });
  return zettel;
}
