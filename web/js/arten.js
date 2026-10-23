/**
 * arten.js -- die Bauteilarten der Oberfläche, je einmal.
 *
 * Was man von einer Art wissen muss, ohne ihre App zu kennen: ihre Liste im
 * Projekt, wie Auswahl und Rechenkern sie nennen, ihr Knopf links und wie
 * ein neuer Eintrag heisst. Wer alle Bauteile durchgeht -- Kennungen,
 * Baum, Editor, Zusammenfassung, Diagramme --, geht diese Liste durch; eine
 * neue Art kommt hier dazu und in ihre eigenen Module.
 *
 * Liste, Vorsilbe und Namensraum stehen ebenso im Kern, im Steckbrief
 * `BAUTEILE` (opencivil/projekt/aufbau/__init__.py); tests/test_arten_js.py hält
 * beide gleich. Ohne Imports, damit der Test das Modul in node laden kann.
 */

export const ARTEN = [
  {
    /** Wie die Auswahl sie nennt -- und der Anfang ihres Namensraums: querschnitt.q1. */
    art: 'querschnitt',
    /** Ihre Liste im Projekt. */
    liste: 'querschnitte',
    /** Womit ihre Kennungen beginnen. */
    vorsilbe: 'q',
    /** Ihr Knopf links: das Zeichen (sinnbilder.js) und der Name, mit weichem Trennstrich. */
    zeichen: 'platte',
    knopf: 'Stahlbeton-Platten',
    titel: 'Stahlbeton-Platten',
    /** Was über ihrem Editor steht. */
    bezeichnung: 'Stahlbeton-Platte',
    einzahl: 'Platte',
    /** Wie ein neuer Eintrag heisst: «Platte 3». */
    stamm: 'Platte',
    leer: 'keine Platte',
    /** Ob sie Nachweise führt -- dann steht in der Zusammenfassung ihre Tabelle. */
    nachweise: true,
  },
  {
    art: 'querschnittsanalyse',
    liste: 'querschnittsanalysen',
    vorsilbe: 'a',
    zeichen: 'analyse',
    knopf: 'Querschnitts\u00ADanalyse',
    titel: 'Querschnittsanalyse',
    bezeichnung: 'Querschnittsanalyse',
    einzahl: 'Querschnittsanalyse',
    stamm: 'Querschnitt',
    leer: 'keine Querschnittsanalyse',
    nachweise: true,
  },
  {
    art: 'balkensystem',
    liste: 'balkensysteme',
    vorsilbe: 'r',
    zeichen: 'balkensystem',
    knopf: '2D Balken\u00ADsysteme',
    titel: '2D Balkensysteme',
    bezeichnung: '2D-Balkensystem',
    einzahl: 'Balkensystem',
    stamm: 'System',
    leer: 'kein Balkensystem',
    nachweise: false,
  },
  {
    art: 'grundbruch',
    liste: 'grundbrueche',
    vorsilbe: 'g',
    zeichen: 'grundbruch',
    knopf: 'Grundbruch',
    titel: 'Grundbruch',
    bezeichnung: 'Grundbruch und Gleiten',
    einzahl: 'Grundbruch',
    stamm: 'Fundament',
    leer: 'kein Grundbruch',
    nachweise: true,
  },
  {
    art: 'setzung',
    liste: 'setzungen',
    vorsilbe: 'w',
    zeichen: 'setzung',
    knopf: 'Setzung',
    titel: 'Setzung',
    bezeichnung: 'Setzungsberechnung',
    einzahl: 'Setzung',
    stamm: 'Fundament',
    leer: 'keine Setzung',
    nachweise: true,
  },
];

/** Die Art, die die Auswahl so nennt -- `undefined` beim Material. */
export function artVon(name) {
  return ARTEN.find((a) => a.art === name);
}
