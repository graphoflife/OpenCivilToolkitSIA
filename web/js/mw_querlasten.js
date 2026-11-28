/**
 * mw_querlasten.js -- die Querlasten einer Wand aus Mauerwerk: die Kachel «Querlasten».
 *
 * Eine Querlast wirkt quer zur Wand, gleichmässig über ihre ganze Ansicht,
 * in einem Lastfall. Man zeichnet sie nicht, man legt sie hier an: je eine
 * Karte mit ihrem Lastfall -- eine Wahl aus dem Projekt, darum eine Liste --
 * und ihrer Art (`katalog.mauerwerk.querlastarten`):
 *
 *     von Hand    p in kN/m², etwa Wind: positiv zur Seite, von der aus man
 *                 die Ansicht sieht
 *     Erdbeben    Zone, Baugrund und Bauwerksklasse wie im Erdbeben
 *                 (`katalog.erdbeben`), der Verhaltensbeiwert q des
 *                 Gebäudes (`katalog.mauerwerk.verhaltensbeiwerte`) und wo
 *                 die Wand in ihm steht, z_a und h. Die Ersatzkraft p_E nach
 *                 SIA 261, Gl. (49), rechnet der Kern: sie steht darunter,
 *                 sobald er sie kennt (`zeichendaten.ersatzkraefte`), dazu
 *                 grau, was er zum Erdbeben sagt (`zeichendaten.zum_erdbeben`).
 *
 * Eine neue Querlast kommt in den letzten Lastfall ohne Eigengewicht --
 * gibt es keinen, ist keiner gewählt, und der Kern sagt es grau. Im
 * Zeichenfenster stehen die Querlasten des gezeigten Lastfalls über der
 * Wand (mw_bild.js). Gerechnet wird hier nichts; Zeichen, Einheiten und
 * Grenzen der Felder sagt der Kern (`katalog.felder`).
 */

import {
  feld, karte, meldungshinweise, wahlBlock, wahlSchalter,
} from './bausteine.js';
import { zahlText } from './cad_ansicht.js';
import { auswahl, el, zahlfeld } from './dom.js';
import { zeilenstand } from './kapitel.js';
import { span } from './mathe.js';
import {
  ausVorlage, eintragAendern, feldangabe, katalog, neueKennung, zustand,
} from './zustand.js';

/** Was der Kern zur Wand sagt -- oder null, solange er nicht gerechnet hat. */
const zeichendaten = (kennung) => zustand.loesung?.zeichendaten?.[kennung] || null;

/** Die Stellungen eines Schalters der Wand, wie der Kern sie nennt. */
const stellungen = (liste) => katalog('mauerwerk', liste);

const HILFE = [
  ['Querlast', 'quer zur Wand, gleichmässig über ihre ganze Ansicht, in einem Lastfall – mehrere im selben Lastfall zählen zusammen'],
  ['Lastfall', 'wie bei den Lasten der Zeichnung: die Kombinationen geben ihm seinen Beiwert'],
  ['z_a', 'wie hoch die Mitte der Wand über dem Fundament liegt – dort greift die Ersatzkraft an'],
  ['h', 'wie hoch das Gebäude über dem Fundament ist'],
  ['Nachweis', 'die Querlast trägt ein lotrechtes Gewölbe zwischen Kopf und Fuss, mit gehaltenen Rändern auch ein waagrechtes – das stärkere gilt'],
];

/** Die Hilfe: die Zeilen oben, dann je Stellung der Art und von q, was der Kern dazu sagt. */
const hilfe = () => ({
  zeilen: [...HILFE, ...['querlastarten', 'verhaltensbeiwerte']
    .flatMap((liste) => stellungen(liste).map((s) => [s.beschriftung, s.titel]))],
  formel: 'p_E = γ_f·a_gd·S·g_k/(g·q_a)·[3·(1 + z_a/h) − 0.5]',
});

/** Ein Schalter einer Querlast -- `werte` die Stellungen des Kerns. */
function schalter(q, aendern, werte, feldname, titel) {
  return wahlSchalter({
    werte, gewaehlt: q[feldname], titel, setzen: (w) => aendern((x) => { x[feldname] = w; }),
  });
}

/** «Höhe über dem Fundament z_a»: der Name des Kerns, sein Zeichen gesetzt. */
function beschriftung({ heisst, zeichen }) {
  return zeichen && heisst.endsWith(` ${zeichen}`) ? [heisst.slice(0, -zeichen.length), span(zeichen)] : heisst;
}

/** Ein Zahlenfeld einer Querlast, mit Namen, Zeichen, Einheit und Grenzen des Kerns. */
function zahl(q, aendern, feldname, schritt, titel) {
  const angabe = feldangabe('wandquerlast', feldname);
  return feld(beschriftung(angabe), zahlfeld({
    wert: q[feldname], schritt, angabe, neben: q, titel,
    beiAenderung: (v) => aendern((x) => { x[feldname] = v; }),
  }), angabe.einheit, `${angabe.heisst} – ${titel}`);
}

/**
 * Der Lastfall einer Querlast: eine Liste der Lastfälle der Wand. Zeigt
 * sie auf keinen, steht das als erste Zeile da, bis man einen wählt.
 */
function lastfallListe(w, q, aendern) {
  const faelle = w.lastfaelle.map((lf) => ({ wert: lf.kennung, beschriftung: lf.name }));
  const da = faelle.some((f) => f.wert === q.lastfall);
  return auswahl({
    werte: da ? faelle : [{ wert: q.lastfall, beschriftung: '– Lastfall wählen –' }, ...faelle],
    gewaehlt: q.lastfall, titel: 'In welchem Lastfall die Querlast wirkt',
    beiAenderung: (v) => aendern((x) => { x.lastfall = v; }),
  });
}

/**
 * Was eine Querlast des Erdbebens braucht: der Standort wie im Erdbeben, q
 * des Gebäudes, z_a und h -- darunter p_E, sobald der Kern es kennt.
 */
function erdbebenZeilen(w, q, aendern) {
  const p = zeichendaten(w.kennung)?.ersatzkraefte?.[q.kennung];
  return [
    wahlBlock('Erdbebenzone', schalter(q, aendern, katalog('erdbeben', 'zonen'), 'zone', 'Die Zone des Standorts')),
    wahlBlock('Baugrundklasse', schalter(q, aendern, katalog('erdbeben', 'baugrund'), 'baugrund',
      'Die Klasse des Baugrunds unter dem Gebäude')),
    wahlBlock('Bauwerksklasse', schalter(q, aendern, katalog('erdbeben', 'bauwerksklassen'), 'bauwerksklasse',
      'Wie wichtig das Gebäude nach einem Beben ist')),
    wahlBlock('Verhaltensbeiwert q des Gebäudes', schalter(q, aendern, stellungen('verhaltensbeiwerte'), 'q',
      'Mit welchem q das Gebäude im Erdbeben rechnet')),
    zahl(q, aendern, 'z_a', 0.1, 'bis zur Mitte der Wand'),
    zahl(q, aendern, 'h', 0.5, 'über dem Fundament'),
    p === undefined ? null : el('p.karte-hinweis', {
      text: `→ p_E = ${zahlText(p, 2)} kN/m², in beiden Richtungen`,
    }),
  ];
}

/** Die Karte einer Querlast: Lastfall, Art und was diese braucht. */
function querlastKarte(w, i) {
  const q = w.querlasten[i];
  const aendern = (veraenderer) => eintragAendern(w.kennung, (x) => veraenderer(x.querlasten[i]));
  const weg = el('button.weg', {
    type: 'button', text: '×', title: 'Querlast löschen',
    on: { click: () => eintragAendern(w.kennung, (x) => { x.querlasten.splice(i, 1); }) },
  });
  return karte(`Querlast ${q.kennung}`, [
    feld('Lastfall', lastfallListe(w, q, aendern), ''),
    wahlBlock('Art', schalter(q, aendern, stellungen('querlastarten'), 'art', 'Woher die Querlast kommt')),
    ...(q.art === 'erdbeben' ? erdbebenZeilen(w, q, aendern)
      : [zahl(q, aendern, 'wert', 0.1, 'positiv zur Seite, von der aus man die Ansicht sieht')]),
  ].filter(Boolean), { zusatz: weg });
}

/** Eine neue Querlast nach der Vorlage des Kerns, im letzten Lastfall ohne Eigengewicht. */
function neueQuerlast(w) {
  eintragAendern(w.kennung, (x) => {
    const lastfall = x.lastfaelle.filter((lf) => !lf.eigengewicht).at(-1)?.kennung ?? '';
    x.querlasten.push(ausVorlage('wandquerlast', {
      kennung: neueKennung(x, katalog('mauerwerk', 'vorsilben').querlasten, x.querlasten), lastfall,
    }));
  });
}

/** Die Kachel «Querlasten» in der Gruppe «Lasten» (lastfaelle.js). */
export const QUERLASTEN = {
  schluessel: 'mw-querlasten',
  name: 'Querlasten', titel: 'Querlasten',
  hilfe,
  inhalt: (w) => [
    ...meldungshinweise(zeichendaten(w.kennung)?.zum_erdbeben),
    w.querlasten.length ? null : el('div.leer', {
      text: 'Noch keine Querlast – quer zur Wand wirkt nichts.',
    }),
    ...w.querlasten.map((_, i) => querlastKarte(w, i)),
    el('div.unterkapitel', {}, [el('button.knopf-anfuegen', {
      type: 'button', text: '+ Querlast', title: 'Eine Querlast anlegen, von Hand oder aus dem Erdbeben',
      on: { click: () => neueQuerlast(w) },
    })]),
  ].filter(Boolean),
  stand: (w) => zeilenstand(w.querlasten, 'Querlast', 'Querlasten', 'keine'),
};
