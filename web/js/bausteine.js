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

import {
  auswahl, el, melden, zahlfeld,
} from './dom.js';
import { span } from './mathe.js';
import { sinnbild } from './sinnbilder.js';
import {
  feldangabe, katalog, materialien, panelUmschalten, zustand,
} from './zustand.js';

/**
 * Mehrere zugleich (Benutzer, 2026-10-24): was die gewählten gemeinsam
 * haben, steht da -- unterscheiden sie sich, steht «Var», und was man dann
 * wählt oder tippt, gilt für alle. Bis 2026-11-19 in cad_app.js; hier, weil
 * auch die Materialliste es braucht, die nicht nur Zeichenfenster haben.
 */
export const VAR = '*var*';

/** Der gemeinsame Wert der gewählten -- oder VAR. */
export function gemeinsam(werte) {
  return werte.every((w) => w === werte[0]) ? werte[0] : VAR;
}

/** Die Stellungen eines Schalters oder einer Liste -- bei VAR mit «Var» vorneweg. */
export function mitVar(werte, gewaehlt) {
  return gewaehlt === VAR ? [{
    wert: VAR, beschriftung: 'Var', titel: 'Die gewählten unterscheiden sich – was man wählt, gilt für alle',
  }, ...werte] : werte;
}

/**
 * Die Wahl eines Materials des Projekts -- eine Liste, weil ihre Zahl mit
 * dem Projekt wächst. Was es nicht (mehr) gibt, steht als «– Beton wählen
 * –» da, eine leere Liste als «– noch kein Beton im Projekt –», mehrere
 * verschiedene als «Var». `zusatz` sind Stellungen, die kein Material sind
 * («Aussparung»). Bis 2026-11-19 stand diese Liste fünfmal da, jede mit
 * einem anderen Teil davon: der Pfahl zeigte bei einem gelöschten Beton
 * still den ersten, die Decke bei zwei verschiedenen «– Beton wählen –».
 */
export function materialliste({
  art, gewaehlt, setzen, titel = '', zusatz = [],
}) {
  const stoffe = materialien(art);
  const werte = [...stoffe.map((m) => ({ wert: m.kennung, beschriftung: m.name || m.sorte })), ...zusatz];
  const name = katalog('materialarten', art, 'titel');
  const fehlt = stoffe.length ? `– ${name} wählen –` : `– noch kein ${name} im Projekt –`;
  return auswahl({
    werte: gewaehlt === VAR || werte.some((x) => x.wert === gewaehlt) ? mitVar(werte, gewaehlt)
      : [{ wert: gewaehlt, beschriftung: fehlt }, ...werte],
    gewaehlt,
    titel,
    beiAenderung: setzen,
  });
}

/**
 * Das Feld für den Namen eines Eintrags -- eines Bauteils, eines Lastfalls,
 * einer Schicht, eines Materials. Leer nimmt es nicht an: es sagt es und
 * behält den bisherigen (Benutzer, 2026-11-19: die Bedienung erklärt sich
 * selbst). Bis dahin galt ein leerer Name: bei den meisten Bauteilen hielt
 * er das ganze Projekt an, ein Lastfall ohne Namen liess sein Diagramm
 * ewig «wird gerechnet» sagen.
 *
 * Was getippt ist, gilt, wie getippt. `pruefen` sagt, was ein Name sonst
 * nicht sein darf, und gibt den Grund zurück -- leer heisst: er darf; auch
 * als Versprechen, wenn erst der Kern es weiss (ein Fallname, `fallzeile`).
 * Gleiche Namen von Bauteilen meldet der Kern beim Eintrag, der sie hat.
 */
export function namensfeld({
  wert, setzen, titel, klasse = '', gesperrt = false, pruefen = () => '',
}) {
  return el(`input${klasse}`, {
    type: 'text', value: wert ?? '', title: titel, disabled: gesperrt,
    on: {
      change: async (e) => {
        const name = e.target.value;
        const grund = name.trim() ? await pruefen(name) : 'Ein Name kann nicht leer sein';
        if (!grund) {
          setzen(name);
          return;
        }
        melden(`${grund}: «${wert ?? ''}» bleibt.`, true);
        e.target.value = wert ?? '';
      },
    },
  });
}

/**
 * Ein Panel der Eingaben: Kopf mit Titel, darunter der Inhalt.
 *
 * Ein Klick auf den Kopf klappt es zu oder auf -- nur nicht auf einen Knopf
 * darin, der hat seine eigene Aufgabe. `schluessel` sagt, unter welchem
 * Namen das gemerkt wird, «App/Titel», etwa `platte/Bewehrung`. `zusatz`
 * steht rechts im Kopf: ein kurzer Hinweis oder ein Knopf.
 *
 * Die Breite bestimmt nicht das Panel, sondern der Stapel, in dem es steht
 * (`.panelstapel` im Stilblatt). Nur ein Panel mit `breit` -- das der
 * Zeichnung -- wächst mit dem Fenster.
 */
export function panel({
  schluessel, titel, zusatz, breit = false,
}, inhalt) {
  const knopf = el('button.panel-knopf', {
    type: 'button',
    'aria-expanded': String(!zustand.zugeklappt.has(schluessel)),
  }, [el('span.pfeil', { text: '▼' }), titel]);
  const gruppe = el('div.feldgruppe', {
    class: [zustand.zugeklappt.has(schluessel) ? 'ist-zu' : '', breit ? 'ist-breit' : ''].join(' '),
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
 * Eine Karte in einem Panel: weiss, gerahmt, mit der blauen Kante links,
 * darüber klein ihr Titel -- wie die Kapitel der Eingaben. Die rechte Tafel
 * baut ihre Panels aus denselben Karten wie die mittlere (Benutzer,
 * 2026-10-16). Ohne `titel` keine Kopfzeile: eine Karte allein im Panel
 * hätte sonst denselben Titel zweimal. `zusatz` steht rechts im Kopf.
 *
 * `bild` sagt, wo eine Karte ihr Diagramm zeigt: das SVG selbst oder was an
 * seiner Stelle steht -- eine Hülle darum oder ein Leerzustand, der sagt,
 * warum es (noch) keines gibt. Der Bericht liest es mit `bildDer`.
 */
export function karte(titel, inhalt, { zusatz = null, klasse = '', bild = null } = {}) {
  const k = el('div.unterkapitel', { class: klasse }, [
    titel ? el('div.unterkapitel-kopf', {}, [el('span', { text: titel }), zusatz]) : null,
    ...inhalt,
  ]);
  KARTEN.set(k, { titel: titel || '', bild });
  return k;
}

/** Titel und Bild jeder Karte, wie `karte` sie bekam -- gehen mit der Karte. */
const KARTEN = new WeakMap();

/** Der Titel einer Karte aus `karte` -- leer, wenn sie keinen hat. */
export function titelDer(k) {
  return KARTEN.get(k).titel;
}

/**
 * Das Diagramm einer Karte: das SVG, das sie als `bild` nennt, oder das
 * erste in dem, was sie nennt. `null`, wenn sie keines nennt oder dort noch
 * keines steht -- dann ist sie ein Hinweis, kein Diagramm. Bis 2026-11-20
 * galt jede Karte mit irgendeinem SVG als Diagramm, und das erste wurde die
 * Vorschau: auch ein Schalter mit Sinnbild im Kopf der Karte.
 */
export function bildDer(k) {
  const bild = KARTEN.get(k)?.bild;
  if (!bild) return null;
  return bild.localName === 'svg' ? bild : bild.querySelector('svg');
}

/**
 * Was einem Bauteil noch fehlt, an seiner Stelle: über seinem Editor und in
 * der Zusammenfassung. `unfertig` ist sein Eintrag in `loesung.unfertige`
 * (Name und Grund) oder nichts -- dann auch kein Hinweis. Ein unfertiger
 * Zustand ist kein Fehler des Projekts (Benutzer, 2026-11-19): er sagt, was
 * fehlt, und der Rest rechnet weiter.
 */
export function unfertigHinweis(unfertig) {
  return unfertig
    ? el('div.hinweis.hinweis-warnung', {}, [el('b', { text: 'Nichts zu rechnen: ' }), `${unfertig.grund}.`])
    : null;
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
    // Statt einer Einheit darf hier ein Element stehen -- etwa ein «?». Im
    // Label hätte es keinen Platz: das schneidet ab, was übersteht, und mit
    // ihm die Blase der Erklärung.
    einheit instanceof Node
      ? el('span.einheit', {}, [einheit])
      : el('span.einheit', { text: einheit || '' }),
  ]);
}

/**
 * Die Karten einer Maske aus den Vorgaben des Kerns (`katalog.vorgaben`,
 * opencivil/core/vorgaben.py): je Gruppe der Herleitung eine Karte mit
 * ihrem Titel, je Feld eine Zeile -- die kurze Beschriftung mit dem
 * Zeichen, darüber im Titel die Beschreibung, der Hinweis und die
 * Normstelle. Welche Felder eine Gruppe hat, richtet sich nach den Wahlen
 * des Eintrags, die sie nennt; `gelesen`, wo es eine solche Menge gibt,
 * lässt nur die Felder stehen, die der Nachweis liest. `klasse` ist der
 * Name der Klasse im Katalog, `aendern(veraenderer)` schreibt.
 *
 * `dazu` setzt Teile der Maske vor oder hinter die Felder einer Gruppe,
 * unter ihrem Titel: `{ Boden: { vor: [...], nach: [...] } }`. Einen Titel,
 * den es nicht gibt, meldet es, statt die Teile still zu verlieren. Eine
 * Gruppe ohne Felder und ohne Teile fällt weg.
 */
export function eingabekarten(klasse, eintrag, aendern, { gelesen = null, dazu = {} } = {}) {
  return vorgabeteile(klasse, eintrag, aendern, { gelesen, dazu })
    .map(({ titel, inhalt }) => (inhalt.length ? karte(titel, inhalt) : null)).filter(Boolean);
}

/**
 * Dieselben Teile ohne Karten, eine Zeile nach der anderen -- für einen
 * Eintrag, der schon seine Karte hat, etwa eine Schicht des Pfahls. Die
 * Gruppen sagen dann nur, wohin `dazu` seine Teile setzt.
 */
export function eingabezeilen(klasse, eintrag, aendern, { dazu = {} } = {}) {
  return vorgabeteile(klasse, eintrag, aendern, { dazu }).flatMap((g) => g.inhalt);
}

/**
 * Die Gruppen der Vorgaben einzeln, für eine Maske, die sie auf mehrere
 * Tafeln verteilt, wie das Durchstanzen: `zeilen(titel)` gibt die Zeilen
 * einer Gruppe, `vollstaendig()` meldet jede, nach der die Maske nicht
 * fragte -- eine neue Gruppe des Kerns fehlte dort sonst still. `gelesen`
 * wie bei `eingabekarten`.
 */
export function eingabegruppen(klasse, eintrag, aendern, { gelesen = null } = {}) {
  const gruppen = new Map(katalog('vorgaben', klasse).map((g) => [g.titel, g]));
  const gefragt = new Set();
  return {
    zeilen(titel) {
      if (!gruppen.has(titel)) throw keineGruppe(klasse, titel);
      gefragt.add(titel);
      return gruppenzeilen(klasse, eintrag, gruppen.get(titel), aendern, gelesen);
    },
    vollstaendig() {
      const fehlt = [...gruppen.keys()].filter((titel) => !gefragt.has(titel));
      if (fehlt.length) {
        throw new Error(`Die Maske von «${klasse}» zeigt die Vorgaben «${fehlt.join('», «')}» nirgends.`);
      }
    },
  };
}

/** Je Gruppe der Vorgaben ihr Titel und ihre Teile -- siehe `eingabekarten`. */
function vorgabeteile(klasse, eintrag, aendern, { gelesen = null, dazu = {} }) {
  const gruppen = katalog('vorgaben', klasse);
  for (const titel of Object.keys(dazu)) {
    if (!gruppen.some((g) => g.titel === titel)) throw keineGruppe(klasse, titel);
  }
  return gruppen.map((g) => {
    const { vor = [], nach = [] } = dazu[g.titel] || {};
    return {
      titel: g.titel,
      inhalt: [...vor, ...gruppenzeilen(klasse, eintrag, g, aendern, gelesen), ...nach]
        .filter(Boolean),
    };
  });
}

function keineGruppe(klasse, titel) {
  return new Error(`Unter den Vorgaben von «${klasse}» gibt es keine Gruppe «${titel}».`);
}

/** Die Zeilen einer Gruppe für einen Eintrag -- mit `gelesen` nur, was der Nachweis liest. */
function gruppenzeilen(klasse, eintrag, g, aendern, gelesen) {
  return felderDer(g, eintrag).filter((f) => !gelesen || gelesen.has(f.feld))
    .map((f) => vorgabezeile(klasse, eintrag, f, aendern));
}

/**
 * Die Felder einer Gruppe der Vorgaben für einen Eintrag -- nach den Wahlen,
 * die sie nennt. Eine Stellung, die die Wahl nicht kennt, kann nur aus einer
 * Datei kommen; die Prüfung des Kerns meldet sie am Ort, und die Gruppe
 * bleibt leer, bis der Schalter eine Stellung hat.
 */
function felderDer(g, eintrag) {
  return g.felder[g.nach.map((n) => eintrag[n]).join('|')] || [];
}

/**
 * Alle Felder der Vorgaben eines Eintrags, über die Gruppen hinweg -- für
 * eine Maske ohne Karten, etwa eine Zeile je Schicht.
 */
export function vorgabefelder(klasse, eintrag) {
  return katalog('vorgaben', klasse).flatMap((g) => felderDer(g, eintrag));
}

/** Der Titel über einem Feld der Vorgaben: Beschreibung und Hinweis, dahinter die Normstelle. */
export function vorgabetitel(f) {
  return [f.beschreibung, f.hinweis].filter(Boolean).join(' – ') + (f.referenz ? ` (${f.referenz})` : '');
}

/**
 * Ein Feld der Vorgaben als Zeile: die Beschriftung mit dem Zeichen, Einheit
 * und Grenzen aus dem Katalog (`katalog.felder[klasse]`) -- in welcher
 * Einheit der Kern eine Zahl meint, steht an ihrem Feld im Kern und nur dort.
 */
function vorgabezeile(klasse, eintrag, f, aendern) {
  const angabe = feldangabe(klasse, f.feld);
  const titel = vorgabetitel(f);
  return feld([`${f.beschriftung} `, span(f.zeichen)], zahlfeld({
    wert: eintrag[f.feld], schritt: f.schritt, angabe, titel,
    beiAenderung: (v) => aendern((x) => { x[f.feld] = v; }),
  }), angabe.einheit || '', titel);
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

/**
 * Ein Schalter mit zwei Stellungen: ein einziger Knopf, die gewählte Hälfte
 * farbig. Ein Klick irgendwo darauf schaltet um, nicht nur einer auf die
 * andere Hälfte (Benutzer, 2026-10-16). `stellungen` sind zwei
 * `[wert, text, klasse]`; `klasse` trägt die Farbe der Hälfte. `aus`:
 * es gibt noch nichts zu wählen, `titel` sagt warum.
 */
export function zweiSchalter({ stellungen, gewaehlt, setzen, titel, klasse = '', aus = false }) {
  const [[a], [b]] = stellungen;
  return el(`button.schalter${klasse}`, {
    type: 'button', title: titel, disabled: aus,
    on: { click: () => setzen(gewaehlt === a ? b : a) },
  }, stellungen.map(([wert, text, k]) => el('span.schalter-halb', {
    text, class: `${k || ''} ${wert === gewaehlt ? 'ist-an' : ''}`,
  })));
}

/**
 * Ein Schalter mit mehreren Stellungen -- ein Klick wählt seine. Er steht,
 * wo sonst eine Auswahlliste stünde: Auswahllisten gibt es nur für die Wahl
 * eines Materials (Benutzer, 2026-10-23). `werte` sind `{wert, beschriftung,
 * titel?, zeichen?}`; `zeichen` ist ein Sinnbild vor der Beschriftung,
 * `titel` sagt, was der ganze Schalter wählt.
 */
export function wahlSchalter({ werte, gewaehlt, setzen, titel = '', klasse = '' }) {
  return el(`span.schalter${klasse}`, { title: titel }, werte.map((w) => el('button.schalter-halb', {
    type: 'button', title: w.titel || w.beschriftung,
    class: w.wert === gewaehlt ? 'ist-an' : '',
    on: { click: () => { if (w.wert !== gewaehlt) setzen(w.wert); } },
  }, [w.zeichen ? sinnbild(w.zeichen) : null, w.beschriftung])));
}

/**
 * Die Stellungen eines Schalters, je mit ihrem Bild `art-wert` aus
 * sinnbilder.js -- eine Wahl mit Bild, wo Wörter nicht reichen (Benutzer,
 * 2026-11-19). Jede Stellung des Katalogs hat ihres: das prüft
 * tests/test_bauteilarten.py.
 */
export function mitBild(werte, art) {
  return werte.map((w) => ({ ...w, zeichen: `${art}-${w.wert}` }));
}

/**
 * Wie der Boden trägt, drainiert oder undrainiert -- derselbe Schalter im
 * Pfahl und im Grundbruch (Benutzer, 2026-11-19). Die Stellungen und was sie
 * heissen, kommen aus dem Kern (`katalog.verhalten`).
 */
export function verhaltenSchalter(gewaehlt, setzen) {
  return wahlSchalter({
    werte: katalog('verhalten'), gewaehlt, setzen,
    titel: 'Drainiert mit wirksamen Spannungen, undrainiert mit totalen',
  });
}

/**
 * Eine Gruppe einer Liste, die auf- und zuklappt -- zu Beginn zu (Benutzer,
 * 2026-10-24). `offen` merkt sich die Titel der aufgeklappten; das ist
 * Ansichtssache, nicht Teil des Projekts. `klasse` gibt die Namen: die
 * Gruppe, ihr `-titel` und ihre `-zeilen`.
 */
export function klappgruppe(titel, zeilen, offen, klasse) {
  const gruppe = el(`details.${klasse}`, {}, [
    el(`summary.${klasse}-titel`, { text: `${titel} (${zeilen.length})` }),
    el(`div.${klasse}-zeilen`, {}, zeilen),
  ]);
  gruppe.open = offen.has(titel);
  gruppe.addEventListener('toggle', () => { if (gruppe.open) offen.add(titel); else offen.delete(titel); });
  return gruppe;
}

/**
 * Ein Schalter mit vielen oder langen Stellungen unter seiner Beschriftung
 * -- neben ihr fände er keinen Platz, und seine Stellungen brechen um. Ein
 * «div», kein «label»: ein Klick auf den Text löste sonst die erste
 * Stellung aus.
 */
export function wahlBlock(beschriftung, schalter) {
  return el('div.wahlblock', {}, [el('span.wahlblock-titel', { text: beschriftung }), schalter]);
}

/**
 * Zweistellungs-Schalter ja/nein -- grüner Haken, rotes Kreuz.
 *
 * Beide Hälften gleich breit und die Zeichen mittig: ✓ und ✗ sind verschieden
 * breit, und bei symmetrischem Innenabstand wurde der Schalter dadurch schief.
 */
export function hakenSchalter(an, setzen, was = 'Nachweis') {
  // Ein oder aus: «wird geführt» passte zum Nachweis, nicht zu «Bügel
  // mitsuchen» oder «Längszugkraft» (bis 2026-11-19).
  return zweiSchalter({
    stellungen: [[true, '✓', 'ist-ja'], [false, '✗', 'ist-nein']],
    gewaehlt: !!an, setzen, klasse: '.schalter-haken',
    titel: `${was}: ${an ? 'ein – Klicken schaltet aus' : 'aus – Klicken schaltet ein'}`,
  });
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

/** Eine Tabelle: Kopf und Zeilen, je Zelle ein Text -- ausser in der ersten Spalte rechtsbündig, für Zahlen. */
export function tabelle(kopf, zeilen) {
  return el('div.tabelle-huelle', {}, [el('table.bs-tabelle', {}, [
    el('thead', {}, [el('tr', {}, kopf.map((t) => el('th', { text: t })))]),
    el('tbody', {}, zeilen.map((z) => el('tr', {}, z.map((t, i) => el(i ? 'td.bs-zahl' : 'td', { text: t }))))),
  ])]);
}
