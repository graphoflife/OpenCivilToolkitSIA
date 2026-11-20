/**
 * apps.js -- die Apps der linken Tafel, je eine Zeile.
 *
 * Eine App hat links einen Knopf: die Materialien, die neun Bauteilarten
 * (ARTEN, arten.js) und Python. Was Baum, Editor und rechte Tafel von ihr
 * wissen müssen, steht in ihrer Zeile: ihre Liste im Projekt und die Gruppen
 * unter dem Knopf, wie ein Eintrag heisst und was rechts in ihm steht, wie er
 * entsteht und wie er weggeht, sein Editor, sein Fenster, was er rechts
 * zeigt und ob er in die Rechnung eingeht (`rechnet`). Die gemeinsamen
 * Abläufe schlagen nur noch hier nach.
 *
 * Bis 2026-10-18 liefen Material und Python als Sonderwege durch baum.js,
 * editor.js, zustand.js und app.js, und was eine Bauteilart im Baum und im
 * Editor ausmacht, stand in sieben Tabellen.
 */

import { ARTEN, artVon } from './arten.js';
import {
  el, ersetzen, melden, undListe,
} from './dom.js';
import { api } from './api.js';
import { sandboxHinweis, unfertigHinweis } from './bausteine.js';
import { materialAnlegen, materialKopieren } from './materialwahl.js';
import { materialEditor, materialHinweis } from './material.js';
import { plattenEditor, plattenFenster } from './platte.js';
import { analyseEditor, analyseFenster } from './querschnittsanalyse.js';
import { balkensystemEditor, balkensystemFenster } from './balkensystem.js';
import {
  deckeEditor, deckeFenster, deckenKarten, deckenZusammenfassung,
} from './decke.js';
import { durchstanzEditor } from './durchstanzen.js';
import { grundbruchEditor } from './grundbruch.js';
import { setzungEditor } from './setzung.js';
import { pfahlEditor } from './pfahl.js';
import { erdbebenEditor } from './erdbeben.js';
import { skriptZeichnen } from './python.js';
import { variablenZeichnen } from './variablen.js';
import { plattenkarten } from './platte_bilder.js';
import { analyseKarten } from './qa_diagramme.js';
import { spannungskarten } from './spannungsbild.js';
import { systemKarten, systemZusammenfassung } from './bs_diagramme.js';
import { durchstanzKarten } from './ds_grundriss.js';
import { situationKarten } from './gb_zeichnung.js';
import { setzungKarten } from './sz_zeichnung.js';
import { pfahlKarten } from './pf_zeichnung.js';
import { erdbebenKarten } from './eb_zeichnung.js';
import {
  ansichtVergessen, eintragVon, freieKennung, istSandbox, katalog, kopieName, naechsterName,
  projektAendern, waehlen, zustand,
} from './zustand.js';

// ===========================================================================
// Entstehen und Weggehen -- für alle Apps gleich
// ===========================================================================

/**
 * Ein neuer Eintrag nach der Vorlage des Kerns für seine Liste (`katalog.neu`).
 *
 * Gesetzt wird nur, was der Kern nicht wissen kann: die Kennung, der Name
 * und die Materialien des Projekts -- je Feld das erste seiner Art, wie der
 * Kern sagt (`katalog.erste_materialien`); nach derselben Regel baut er die
 * Sandbox. `braucht` nennt die Arten, ohne die es nicht geht: die, die der
 * Eintrag nimmt, oder die, ohne die sich nichts zeichnen lässt. Die Vorlage
 * stand einmal hier, zwanzig Felder der Platte, die von Hand mit den
 * Vorgaben in opencivil/projekt/platte.py gleichgehalten werden mussten; als
 * sich die Vorgaben änderten, brachten neue Platten Nachweise eingeschaltet
 * mit, die überall sonst aus waren. Kopiert, nicht die Vorlage selbst: sonst
 * teilten sich alle neuen Platten dieselben Lagen, und die zweite änderte
 * die erste mit.
 */
function nachVorlage(a, braucht = Object.values(katalog('erste_materialien', a.liste))) {
  const erstes = (art) => zustand.projekt.materialien.find((m) => m.art === art);
  const fehlen = [...new Set(braucht)].filter((art) => !erstes(art));
  if (fehlen.length) {
    melden(`Zuerst ${undListe(fehlen.map((art) => katalog('materialarten', art, 'titel')))} anlegen.`,
      true);
    return;
  }
  const kennung = freieKennung(a.vorsilbe);
  projektAendern((p) => {
    p[a.liste] = p[a.liste] || [];
    const neu = {
      ...structuredClone(katalog('neu', a.liste)), kennung,
      name: naechsterName(katalog('staemme', a.liste), p[a.liste]),
    };
    for (const [pfad, art] of Object.entries(katalog('erste_materialien', a.liste))) {
      const weg = pfad.split('/');
      const feld = weg.pop();
      weg.reduce((ziel, schritt) => ziel[schritt], neu)[feld] = erstes(art)?.kennung ?? '';
    }
    p[a.liste].push(neu);
  });
  waehlen({ art: a.app, kennung });
}

/**
 * Löscht einen Eintrag, wenn kein Bauteil mehr auf ihn zeigt -- sonst sagt
 * es, welche. Wer worauf zeigt, weiss der Kern (`Projekt.verweise`); eine
 * eigene Liste hier kannte bis 2026-10-17 den Bügelstahl nicht, und der
 * nächste Lauf scheiterte am gelöschten Stahl.
 */
async function loeschenWennFrei(liste, eintrag, satz) {
  let verweise;
  try {
    ({ verweise } = await api.verweise(zustand.projekt, eintrag.kennung));
  } catch (fehler) {
    melden(`Nicht gelöscht: ${fehler.message}`, true);
    return;
  }
  if (verweise.length) {
    melden(`${satz}: ${verweise.map((v) => v.name).join(', ')}`, true);
    return;
  }
  entfernen(liste, eintrag);
}

/**
 * Eine Kopie gleich hinter dem Original: alles wie dort, nur Kennung und Name
 * neu -- «Decke über EG (Kopie)» (Benutzer, 2026-10-19). Kopiert, nicht
 * verwiesen: sonst änderte die Kopie das Original mit. Die Kopie der Sandbox
 * ist ein gewöhnlicher Eintrag und heisst wie ein neuer, «Platte 1»
 * (Benutzer, 2026-11-20).
 */
function kopieren(a, eintrag) {
  const kennung = freieKennung(a.vorsilbe);
  projektAendern((p) => {
    const liste = p[a.liste];
    const i = liste.findIndex((x) => x.kennung === eintrag.kennung);
    const name = istSandbox(eintrag.kennung)
      ? naechsterName(katalog('staemme', a.liste), liste) : kopieName(liste[i].name, liste);
    liste.splice(i + 1, 0, { ...structuredClone(liste[i]), kennung, name });
  });
  waehlen({ art: a.app, kennung });
}

/**
 * ↺ an der Sandbox, ohne Rückfrage (Benutzer, 2026-11-20): der Kern baut sie
 * neu, wie beim Laden der Seite -- Kennung, Name und Platz bleiben. Was sich
 * die Ansichten zu ihr merkten, geht mit dem alten Inhalt.
 */
async function zuruecksetzen(a, sandbox) {
  const { projekt } = zustand;
  let eintrag;
  try {
    ({ eintrag } = await api.sandboxZuruecksetzen(projekt, a.liste));
  } catch (fehler) {
    melden(`Nicht zurückgesetzt: ${fehler.message}`, true);
    return;
  }
  // Inzwischen ein anderes Projekt gezeigt: dessen Einträge bleiben, wie sie sind.
  if (zustand.projekt !== projekt) return;
  ansichtVergessen(sandbox.kennung);
  projektAendern((p) => {
    const i = p[a.liste].findIndex((x) => x.kennung === sandbox.kennung);
    if (i >= 0) p[a.liste][i] = eintrag;
  });
  melden('Die Sandbox beginnt neu.');
}

/**
 * Einen Eintrag aus einer Liste des Projekts -- und aus der Auswahl, wenn er
 * gewählt war. Was sich die Ansichten zu ihm merkten, geht mit.
 */
function entfernen(liste, eintrag) {
  ansichtVergessen(eintrag.kennung);
  projektAendern((p) => {
    p[liste] = p[liste].filter((x) => x.kennung !== eintrag.kennung);
  });
  if (zustand.auswahl?.kennung === eintrag.kennung) waehlen(null);
}

// ===========================================================================
// Die Zeilen
// ===========================================================================

/**
 * Die Zeile einer Bauteilart (ARTEN): Knopf, Liste und Wörter aus arten.js,
 * dazu was nur die Oberfläche kennt -- auch ihre Karten im Reiter
 * «Diagramme» (`karten(kennung, eintrag, loesung)`) und, wo sie keine
 * Nachweise führt, was die Zusammenfassung statt der Tabelle zeigt
 * (`uebersicht(kennung)`). Fehlt eines davon, meldet sich das beim Laden.
 * Ein Bauteil geht nur weg, wenn kein Balkensystem mehr seinen Querschnitt
 * nimmt. `braucht` sagt, welche Materialien «+» verlangt -- ohne Angabe die,
 * die ein neuer Eintrag nimmt (`nachVorlage`).
 */
function bauteil(name, {
  kurztext, braucht, editor, karten, uebersicht = null, fenster = null,
}) {
  const a = artVon(name);
  if (!karten) throw new Error(`apps.js: «${name}» hat keine Karten für die Diagramme.`);
  if (!a.nachweise && !uebersicht) {
    throw new Error(`apps.js: «${name}» führt keine Nachweise und hat keine Übersicht.`);
  }
  const zeile = {
    app: a.art, liste: a.liste, knopf: a.knopf, zeichen: a.zeichen,
    vorsilbe: a.vorsilbe,
    gruppen: (p) => [{
      titel: a.titel, leer: a.leer, eintraege: p[a.liste] || [],
      plus: { titel: `${a.einzahl} hinzufügen`, tun: () => nachVorlage(zeile, braucht) },
    }],
    name: (e) => e.name,
    kurztext,
    loeschen: (e) => loeschenWennFrei(a.liste, e, `„${e.name}" ist Querschnitt in`),
    kopieren: (e) => kopieren(zeile, e),
    zuruecksetzen: (e) => zuruecksetzen(zeile, e),
    hinweis: () => a.bezeichnung,
    editor: mitHinweis(a.liste, editor),
    fenster,
    karten,
    uebersicht,
  };
  return zeile;
}

/**
 * Die Eingaben eines Eintrags aus ``liste`` -- und darüber, was ihm noch
 * fehlt, dort, wo man es nachträgt (Benutzer, 2026-11-19): einem Material
 * wie einem Bauteil. Bei der Sandbox zuoberst, wozu sie da ist.
 */
function mitHinweis(liste, editor) {
  return (behaelter, e) => ersetzen(behaelter, sandboxHinweis(e),
    unfertigHinweis(zustand.loesung?.unfertige?.[liste]?.[e.kennung]), ...editor(e));
}

/**
 * Die Materialien: unter dem Knopf eine Liste je Art. Im Eintrag steht keine
 * Sorte -- eine Normsorte heisst wie sie, ein eigenes Material trägt keine
 * (Benutzer, 2026-10-16) --, aber ob es eine Normsorte ist.
 */
const MATERIAL = {
  app: 'material', liste: 'materialien', knopf: 'Materialien', zeichen: 'material',
  gruppen: (p) => Object.entries(katalog('materialarten'))
    .map(([art, { titel }]) => ({
      titel, leer: `kein ${titel}`, eintraege: p.materialien.filter((m) => m.art === art),
      plus: { titel: `${titel} hinzufügen`, tun: () => materialAnlegen(art) },
    })),
  name: (m) => m.name || m.sorte,
  marke: (m) => (m.eigenstaendig
    ? el('span.eigen', { text: 'eigen' })
    : el('span.sia', { text: 'SIA', title: 'Normsorte nach SIA – nicht änderbar' })),
  kurztext: () => '',
  loeschen: (m) => loeschenWennFrei('materialien', m, `„${m.name || m.sorte}" verwendet von`),
  kopieren: materialKopieren,
  hinweis: materialHinweis,
  editor: mitHinweis('materialien', materialEditor),
};

/**
 * «300×600 mm» -- Breite und Höhe dessen, was gezeichnet ist. Die
 * Platte zeigt an derselben Stelle h × b; eine Analyse hat statt zweier
 * Masse die Ecken ihrer Flächen, und die äussersten davon sind dasselbe.
 * Ohne Fläche heisst sie «leer» nur, wenn auch keine Bewehrung da ist.
 */
function umriss(analyse) {
  const ecken = new Set(analyse.flaechen.flatMap((f) => f.knoten));
  const punkte = (analyse.knoten || []).filter((k) => ecken.has(k.kennung)).map((k) => [k.y, k.z]);
  if (!punkte.length) {
    const bewehrt = ['staebe', 'stablinien', 'schubwaende'].some((liste) => analyse[liste]?.length);
    return bewehrt ? 'ohne Polygon' : 'leer';
  }
  const spanne = (i) => Math.max(...punkte.map((p) => p[i])) - Math.min(...punkte.map((p) => p[i]));
  return `${Number(spanne(0).toFixed(1))}×${Number(spanne(1).toFixed(1))} mm`;
}

const PLATTE = bauteil('querschnitt', {
  kurztext: (q) => `${q.h}×${q.b} mm`,
  editor: plattenEditor,
  karten: plattenkarten,
  fenster: plattenFenster,
});

/**
 * Leer, aus dem Kern (Benutzer, 2026-10-19): gezeichnet wird danach, das
 * Rechteck gibt es als Vorlage im Zeichenfenster. Beton und Betonstahl
 * braucht es erst zum Zeichnen -- verlangt werden sie schon hier, sonst
 * stünde man vor einem Fenster, in dem nichts geht.
 */
const ANALYSE = bauteil('querschnittsanalyse', {
  kurztext: umriss,
  braucht: ['beton', 'betonstahl'],
  editor: analyseEditor,
  karten: (kennung, eintrag, loesung) => [
    ...analyseKarten(kennung), ...spannungskarten(kennung, loesung)],
  fenster: analyseFenster,
});

/**
 * Leer, aus dem Kern (Benutzer, 2026-10-19) -- bis auf ein Material: der
 * erste Beton des Projekts, damit ein gezeichneter Stab gleich eines hat
 * (`MitStaeben.neu` im Kern). Das 2D- und das 3D-Balkensystem sind dieselbe
 * App, je mit ihrer Liste und ihrem Katalog (bs_teile.js).
 */
const balkensystem = (art) => bauteil(art, {
  kurztext: (s) => {
    const staebe = s.linien.filter((l) => l.querschnitt).length;
    return `${staebe} ${staebe === 1 ? 'Stab' : 'Stäbe'}`;
  },
  editor: balkensystemEditor,
  karten: systemKarten,
  uebersicht: systemZusammenfassung,
  fenster: balkensystemFenster,
});
const SYSTEM = balkensystem('balkensystem');
const SYSTEM3D = balkensystem('balkensystem3d');

/**
 * Leer, aus dem Kern -- gezeichnet wird danach. Einen Beton braucht erst
 * die erste Platte; verlangt wird er schon hier, sonst stünde man vor
 * einem Fenster, in dem keine Platte rechnet.
 */
const DECKE = bauteil('decke', {
  kurztext: (d) => `${d.platten.length} ${d.platten.length === 1 ? 'Platte' : 'Platten'}`,
  braucht: ['beton'],
  editor: deckeEditor,
  karten: deckenKarten,
  uebersicht: deckenZusammenfassung,
  fenster: deckeFenster,
});

/**
 * Eine Innenstütze mit den Vorgaben des Kerns, ohne Einwirkung -- Beton und
 * Betonstahl die ersten des Projekts, wie bei der Platte. Die Liste nennt sie
 * nach der Vorlage des Katalogs für ihre Lage und Form: «⌀{D} mm».
 */
const DURCHSTANZEN = bauteil('durchstanzen', {
  kurztext: (d) => katalog('durchstanzen', 'lagen').find((l) => l.wert === d.lage)
    .kurz[d.form].replace(/\{(\w+)\}/g, (_, k) => d[k]),
  editor: durchstanzEditor,
  karten: durchstanzKarten,
});

/** Ein Fundament mit den Vorgaben des Kerns und einer Kombination -- ohne Material. */
const GRUNDBRUCH = bauteil('grundbruch', {
  kurztext: (g) => `${g.b}×${g.L} m`,
  editor: grundbruchEditor,
  karten: situationKarten,
});

/** Ein Fundament ohne Pressung, mit einer Schicht aus dem Kern -- ohne Material. */
const SETZUNG = bauteil('setzung', {
  kurztext: (s) => `${s.B}×${s.L} m`,
  editor: setzungEditor,
  karten: setzungKarten,
});

/**
 * Ein Bohrpfahl mit den Vorgaben des Kerns, einer Schicht und einer
 * Kombination -- Beton und Betonstahl die ersten des Projekts, wie bei der
 * Platte. Ein Mikropfahl braucht den Beton nicht; angelegt wird aber als
 * Bohrpfahl. Die Liste nennt Durchmesser und Länge: «⌀900 mm, 10 m».
 */
const PFAHL = bauteil('pfahl', {
  kurztext: (t) => `⌀${t.D} mm, ${t.L} m`,
  editor: pfahlEditor,
  karten: pfahlKarten,
});

/**
 * Ein Gebäude mit den Vorgaben des Kerns, einem Geschoss ohne Last und einer
 * Wand ohne Querschnittsanalyse -- ohne Material: das nimmt die Wand aus ihrer
 * Analyse. Die Liste nennt, wie viele: «4 Geschosse, 2 Wände».
 */
const ERDBEBEN = bauteil('erdbeben', {
  kurztext: (h) => `${h.geschosse.length} ${h.geschosse.length === 1 ? 'Geschoss' : 'Geschosse'}, `
    + `${h.waende.length} ${h.waende.length === 1 ? 'Wand' : 'Wände'}`,
  editor: erdbebenEditor,
  karten: erdbebenKarten,
});

/**
 * Python: ein Skript je Eintrag, nach der Vorlage des Kerns mit einem
 * Diagramm darin. Rechts stehen statt der Berechnung die Variablen der
 * Sitzung, wie in Spyder (Benutzer, 2026-10-15) -- Umfang und Reiter gelten
 * dann nicht.
 */
const SKRIPT = {
  app: 'skript', liste: 'skripte', knopf: 'Python', zeichen: 'python',
  vorsilbe: 'p',
  gruppen: (p) => [{
    titel: 'Python-Skripte', leer: 'kein Skript', eintraege: p.skripte || [],
    plus: { titel: 'Skript hinzufügen', tun: () => nachVorlage(SKRIPT) },
  }],
  name: (s) => s.name,
  kurztext: (s) => {
    const zeilen = (s.code || '').split('\n').filter((z) => z.trim()).length;
    return `${zeilen} ${zeilen === 1 ? 'Zeile' : 'Zeilen'}`;
  },
  loeschen: (s) => entfernen('skripte', s),
  kopieren: (s) => kopieren(SKRIPT, s),
  zuruecksetzen: (s) => zuruecksetzen(SKRIPT, s),
  hinweis: () => 'Python',
  editor: skriptZeichnen,
  rechts: { titel: 'Variablen', zeichnen: variablenZeichnen },
  // Ein Skript geht in keine Rechnung ein: es zu ändern, anzulegen, zu
  // kopieren oder zu löschen rechnet nicht neu (app.js, `rechenstand`).
  rechnet: false,
};

/** Die Apps, in der Folge ihrer Knöpfe: das Material, die Bauteilarten wie ARTEN, Python. */
export const APPS = [
  MATERIAL, PLATTE, ANALYSE, SYSTEM, SYSTEM3D, DECKE, DURCHSTANZEN, GRUNDBRUCH, SETZUNG, PFAHL,
  ERDBEBEN, SKRIPT,
];

/** Die App, wie die Auswahl sie nennt: 'material', 'skript' oder eine Bauteilart. */
export function appVon(name) {
  return APPS.find((a) => a.app === name);
}

// Eine Bauteilart ohne Zeile hätte keinen Knopf und keinen Editor -- lieber
// laut beim Laden als still beim ersten Klick.
const ohneZeile = ARTEN.filter((a) => !appVon(a.art)).map((a) => a.art);
if (ohneZeile.length) throw new Error(`apps.js: keine Zeile für ${ohneZeile.join(', ')}.`);

/** Der gewählte Eintrag samt seiner App -- `{app, eintrag}`, oder null. */
export function gewaehlt() {
  const app = appVon(zustand.auswahl?.art);
  const eintrag = app && eintragVon(zustand.auswahl.kennung);
  return eintrag ? { app, eintrag } : null;
}
