/**
 * apps.js -- die Apps der linken Tafel, je eine Zeile.
 *
 * Eine App hat links einen Knopf: die Materialien, die fünf Bauteilarten
 * (ARTEN, arten.js) und Python. Was Baum, Editor und rechte Tafel von ihr
 * wissen müssen, steht in ihrer Zeile: ihre Liste im Projekt und die Gruppen
 * unter dem Knopf, wie ein Eintrag heisst und was rechts in ihm steht, wie er
 * entsteht und wie er weggeht, sein Editor, sein Fenster und was er rechts
 * zeigt. Die gemeinsamen Abläufe schlagen nur noch hier nach.
 *
 * Bis 2026-10-18 liefen Material und Python als Sonderwege durch baum.js,
 * editor.js, zustand.js und app.js, und was eine Bauteilart im Baum und im
 * Editor ausmacht, stand in sieben Tabellen.
 */

import { ARTEN, artVon } from './arten.js';
import { el, ersetzen, melden } from './dom.js';
import { api } from './api.js';
import { fensterVergessen } from './qa_zeichnung.js';
import { fensterVergessen as systemfensterVergessen } from './bs_zeichnung.js';
import { materialAnlegen, materialKopieren } from './materialwahl.js';
import { materialEditor, materialHinweis } from './material.js';
import { plattenEditor, plattenFenster } from './platte.js';
import { analyseEditor, analyseFenster } from './querschnittsanalyse.js';
import { balkensystemEditor, balkensystemFenster } from './balkensystem.js';
import { grundbruchEditor } from './grundbruch.js';
import { setzungEditor } from './setzung.js';
import { skriptZeichnen } from './python.js';
import { variablenZeichnen } from './variablen.js';
import { freieKennung, naechsterName, projektAendern, waehlen, zustand } from './zustand.js';

// ===========================================================================
// Entstehen und Weggehen -- für alle Apps gleich
// ===========================================================================

/**
 * Ein neuer Eintrag nach der Vorlage des Kerns (`katalog[schluessel]`).
 *
 * Gesetzt wird nur, was der Kern nicht wissen kann: die Kennung, der Name
 * und, mit `einrichten`, die Materialien des Projekts -- `braucht` nennt die
 * Arten, ohne die es nicht geht, `fehlt` den Satz dazu. Die Vorlage stand
 * einmal hier, zwanzig Felder der Platte, die von Hand mit den Vorgaben in
 * opencivil/projekt/platte.py gleichgehalten werden mussten; als sich die
 * Vorgaben änderten, brachten neue Platten Nachweise eingeschaltet mit, die
 * überall sonst aus waren. Kopiert, nicht die Vorlage selbst: sonst teilten
 * sich alle neuen Platten dieselben Lagen, und die zweite änderte die erste mit.
 */
function nachVorlage(a, schluessel, {
  braucht = [], fehlt = '', einrichten = () => {}, vorher = () => {}, anlass,
} = {}) {
  const stoffe = Object.fromEntries(braucht.map((art) => [
    art, zustand.projekt.materialien.find((m) => m.art === art)]));
  if (braucht.some((art) => !stoffe[art])) {
    melden(fehlt, true);
    return;
  }
  const vorlage = zustand.katalog?.[schluessel];
  if (!vorlage) {
    melden('Katalog noch nicht geladen.', true);
    return;
  }
  const kennung = freieKennung(a.vorsilbe);
  vorher(kennung);
  projektAendern((p) => {
    p[a.liste] = p[a.liste] || [];
    const neu = { ...structuredClone(vorlage), kennung, name: naechsterName(a.stamm, p[a.liste]) };
    einrichten(neu, stoffe);
    p[a.liste].push(neu);
  }, anlass);
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
 * verwiesen: sonst änderte die Kopie das Original mit. `vorher` wie beim
 * Anlegen: ein Zeichenfenster, das diese Kennung schon kannte, vergisst sie.
 */
function kopieren(a, eintrag, { vorher = () => {} } = {}) {
  const kennung = freieKennung(a.vorsilbe);
  vorher(kennung);
  projektAendern((p) => {
    const liste = p[a.liste];
    const i = liste.findIndex((x) => x.kennung === eintrag.kennung);
    liste.splice(i + 1, 0, {
      ...structuredClone(liste[i]), kennung, name: kopieName(liste[i].name, liste),
    });
  });
  waehlen({ art: a.app, kennung });
}

/** «Decke über EG (Kopie)», dann «… (Kopie 2)» -- der erste Name, den die Liste noch nicht hat. */
function kopieName(name, eintraege) {
  const vergeben = new Set(eintraege.map((e) => e.name));
  let kandidat = `${name} (Kopie)`;
  for (let i = 2; vergeben.has(kandidat); i += 1) kandidat = `${name} (Kopie ${i})`;
  return kandidat;
}

/** Einen Eintrag aus einer Liste des Projekts -- und aus der Auswahl, wenn er gewählt war. */
function entfernen(liste, eintrag) {
  projektAendern((p) => {
    p[liste] = p[liste].filter((x) => x.kennung !== eintrag.kennung);
  });
  if (zustand.auswahl?.kennung === eintrag.kennung) waehlen(null);
}

/** Wie man die Teile über einen Editor setzt, der seine Knoten zurückgibt. */
const einsetzen = (editor) => (behaelter, eintrag) => ersetzen(behaelter, ...editor(eintrag));

// ===========================================================================
// Die Zeilen
// ===========================================================================

/**
 * Die Zeile einer Bauteilart (ARTEN): Knopf, Liste und Wörter aus arten.js,
 * dazu was nur die Oberfläche kennt. Ein Bauteil geht nur weg, wenn kein
 * Balkensystem mehr seinen Querschnitt nimmt. `vergessen` lässt das
 * Zeichenfenster einer neuen Kennung vergessen, was es von früher weiss.
 */
function bauteil(name, { kurztext, anlegen, editor, fenster = null, vergessen = () => {} }) {
  const a = artVon(name);
  const zeile = {
    app: a.art, liste: a.liste, knopf: a.knopf, zeichen: a.zeichen,
    vorsilbe: a.vorsilbe, stamm: a.stamm,
    gruppen: (p) => [{
      titel: a.titel, leer: a.leer, eintraege: p[a.liste] || [],
      plus: { titel: `${a.einzahl} hinzufügen`, tun: () => anlegen(zeile) },
    }],
    name: (e) => e.name,
    kurztext,
    loeschen: (e) => loeschenWennFrei(a.liste, e, `„${e.name}" ist Querschnitt in`),
    kopieren: (e) => kopieren(zeile, e, { vorher: vergessen }),
    hinweis: () => a.bezeichnung,
    editor: einsetzen(editor),
    fenster,
  };
  return zeile;
}

/**
 * Die Materialien: unter dem Knopf eine Liste je Art. Im Eintrag steht keine
 * Sorte -- eine Normsorte heisst wie sie, ein eigenes Material trägt keine
 * (Benutzer, 2026-10-16) --, aber ob es eine Normsorte ist.
 */
const MATERIAL = {
  app: 'material', liste: 'materialien', knopf: 'Materialien', zeichen: 'material',
  gruppen: (p) => [['beton', 'Beton', 'kein Beton'], ['betonstahl', 'Betonstahl', 'kein Betonstahl']]
    .map(([art, titel, leer]) => ({
      titel, leer, eintraege: p.materialien.filter((m) => m.art === art),
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
  editor: einsetzen(materialEditor),
};

/**
 * «300×600 mm» -- Breite und Höhe dessen, was gezeichnet ist. Die
 * Platte zeigt an derselben Stelle h × b; eine Analyse hat statt zweier
 * Masse die Ecken ihrer Flächen, und die äussersten davon sind dasselbe.
 */
function umriss(analyse) {
  const ecken = new Set(analyse.flaechen.flatMap((f) => f.knoten));
  const punkte = (analyse.knoten || []).filter((k) => ecken.has(k.kennung)).map((k) => [k.y, k.z]);
  if (!punkte.length) return 'leer';
  const spanne = (i) => Math.max(...punkte.map((p) => p[i])) - Math.min(...punkte.map((p) => p[i]));
  return `${Number(spanne(0).toFixed(1))}×${Number(spanne(1).toFixed(1))} mm`;
}

const PLATTE = bauteil('querschnitt', {
  kurztext: (q) => `${q.h}×${q.b} mm`,
  anlegen: (a) => nachVorlage(a, 'neue_platte', {
    braucht: ['beton', 'betonstahl'], fehlt: 'Zuerst Beton und Betonstahl anlegen.',
    einrichten: (platte, { beton, betonstahl }) => {
      platte.beton = beton.kennung;
      platte.stahl = betonstahl.kennung;
    },
  }),
  editor: plattenEditor,
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
  anlegen: (a) => nachVorlage(a, 'neue_querschnittsanalyse', {
    braucht: ['beton', 'betonstahl'], fehlt: 'Zuerst Beton und Betonstahl anlegen.',
    vorher: fensterVergessen,
  }),
  vergessen: fensterVergessen,
  editor: analyseEditor,
  fenster: analyseFenster,
});

/**
 * Leer, aus dem Kern (Benutzer, 2026-10-19) -- bis auf ein Material: der
 * erste Beton des Projekts, damit ein gezeichneter Stab gleich eines hat.
 */
const SYSTEM = bauteil('balkensystem', {
  kurztext: (s) => {
    const staebe = s.linien.filter((l) => l.querschnitt).length;
    return `${staebe} ${staebe === 1 ? 'Stab' : 'Stäbe'}`;
  },
  anlegen: (a) => nachVorlage(a, 'neues_balkensystem', {
    braucht: ['beton'], fehlt: 'Zuerst einen Beton anlegen.', vorher: systemfensterVergessen,
    einrichten: (s, { beton }) => {
      s.stabmaterialien = [{
        ...structuredClone(zustand.katalog.neue_zeilen.stabmaterial),
        kennung: 'M1', art: 'beton', beton: beton.kennung,
      }];
    },
  }),
  vergessen: systemfensterVergessen,
  editor: balkensystemEditor,
  fenster: balkensystemFenster,
});

/** Ein Fundament mit den Vorgaben des Kerns und einer Kombination -- ohne Material. */
const GRUNDBRUCH = bauteil('grundbruch', {
  kurztext: (g) => `${g.b}×${g.L} m`,
  anlegen: (a) => nachVorlage(a, 'neuer_grundbruch'),
  editor: grundbruchEditor,
});

/** Ein Fundament ohne Pressung, mit einer Schicht aus dem Kern -- ohne Material. */
const SETZUNG = bauteil('setzung', {
  kurztext: (s) => `${s.B}×${s.L} m`,
  anlegen: (a) => nachVorlage(a, 'neue_setzung'),
  editor: setzungEditor,
});

/**
 * Python: ein Skript je Eintrag, nach der Vorlage des Kerns mit einem
 * Diagramm darin. Rechts stehen statt der Berechnung die Variablen der
 * Sitzung, wie in Spyder (Benutzer, 2026-10-15) -- Umfang und Reiter gelten
 * dann nicht.
 */
const SKRIPT = {
  app: 'skript', liste: 'skripte', knopf: 'Python', zeichen: 'python',
  vorsilbe: 'p', stamm: 'Skript',
  gruppen: (p) => [{
    titel: 'Python-Skripte', leer: 'kein Skript', eintraege: p.skripte || [],
    plus: { titel: 'Skript hinzufügen', tun: () => nachVorlage(SKRIPT, 'neues_skript', { anlass: 'skript' }) },
  }],
  name: (s) => s.name,
  kurztext: (s) => {
    const zeilen = (s.code || '').split('\n').filter((z) => z.trim()).length;
    return `${zeilen} ${zeilen === 1 ? 'Zeile' : 'Zeilen'}`;
  },
  loeschen: (s) => entfernen('skripte', s),
  kopieren: (s) => kopieren(SKRIPT, s),
  hinweis: () => 'Python',
  editor: skriptZeichnen,
  rechts: { titel: 'Variablen', zeichnen: variablenZeichnen },
};

/** Die Apps, in der Folge ihrer Knöpfe: das Material, die Bauteilarten wie ARTEN, Python. */
export const APPS = [MATERIAL, PLATTE, ANALYSE, SYSTEM, GRUNDBRUCH, SETZUNG, SKRIPT];

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
  const eintrag = app && (zustand.projekt?.[app.liste] || []).find(
    (e) => e.kennung === zustand.auswahl.kennung);
  return eintrag ? { app, eintrag } : null;
}
