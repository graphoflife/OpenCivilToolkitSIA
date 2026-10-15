/**
 * baum.js -- Linke Tafel: die Apps und die Bestandteile des Projekts.
 *
 * Oben je App ein Knopf mit Zeichen, wie die Kapitel einer Platte in der
 * Mitte (Benutzer, 2026-10-15): Materialien, Stahlbeton-Platten,
 * Querschnittsanalyse, 2D Balkensysteme, Python. Darunter steht die Liste der
 * gewählten App, mit «+» zum Anlegen -- bei den Materialien je eine für
 * Beton und Betonstahl. Darüber, zuoberst in der Tafel, der Name des
 * Projekts (index.html).
 *
 * Beim Löschen eines Materials wird geprüft, ob eine Platte,
 * eine Querschnittsanalyse oder ein Balkensystem es noch braucht -- und beim
 * Löschen einer Platte oder Analyse, ob ein Balkensystem ihren Querschnitt
 * nimmt. Sonst wäre die Beschreibung anschliessend widersprüchlich, und der
 * Rechenkern müsste einen Fehler melden, den die Oberfläche hätte verhindern
 * können.
 */

import { ARTEN, artVon } from './arten.js';
import { el, ersetzen, melden } from './dom.js';
import { sinnbild } from './sinnbilder.js';
import { benutzteMaterialien } from './querschnittsanalyse.js';
import { fensterVergessen } from './qa_zeichnung.js';
import { benutzteBauteile, benutzteMaterialien as systemMaterialien } from './balkensystem.js';
import { fensterVergessen as systemfensterVergessen } from './bs_zeichnung.js';
import {
  appWaehlen, ausVorlage, freieKennung, gewaehlteApp, naechsterName, projektAendern, waehlen,
  zustand,
} from './zustand.js';

// ===========================================================================
// Bausteine
// ===========================================================================

/**
 * Die Apps, je ein Knopf: das Material, dann die Bauteilarten (ARTEN). `app`
 * ist, wie die Auswahl ihre Einträge nennt; `liste`, wie viele es gibt -- auf
 * dem Knopf steht nur die Zahl, «1 Querschnittsanalyse» passte nicht hinein.
 */
const APPS = [
  { app: 'material', knopf: 'Materialien', zeichen: 'material', liste: (p) => p.materialien },
  ...ARTEN.map((a) => ({
    app: a.art, knopf: a.knopf, zeichen: a.zeichen, liste: (p) => p[a.liste] || [],
  })),
  { app: 'skript', knopf: 'Python', zeichen: 'python', liste: (p) => p.skripte || [] },
];

function appKnopf(a, p, gewaehlt) {
  return el('button.kachel.app-kachel', {
    type: 'button', class: gewaehlt ? 'ist-gewaehlt' : '', 'aria-pressed': String(gewaehlt),
    title: a.knopf.replace(/\u00AD/g, ''),
    on: { click: () => appWaehlen(a.app) },
  }, [
    sinnbild(a.zeichen),
    el('span.kachel-name', { text: a.knopf }),
    el('span.kachel-stand', { text: String(a.liste(p).length) }),
  ]);
}

/** Eine Liste unter den Knöpfen: Titel, Zahl und «+», darunter die Einträge. */
function liste({ titel, eintraege, art, plus, leer }) {
  return el('div.baum-gruppe', {}, [
    el('div.baum-kopf', {}, [
      el('span.titel', { text: titel }),
      el('span.zaehler', { text: String(eintraege.length) }),
      el('span.werkzeuge', {}, [plus]),
    ]),
    el('div.baum-koerper', {},
      eintraege.length ? eintraege.map((e) => eintrag(e, art)) : [leerzeile(leer)]),
  ]);
}

/** Was rechts im Eintrag eines Bauteils steht -- je Bauteilart (ARTEN). */
const KURZTEXT = {
  querschnitt: (q) => `${q.h}×${q.b} mm`,
  querschnittsanalyse: umriss,
  balkensystem: (s) => {
    const staebe = s.linien.filter((l) => l.stab).length;
    return `${staebe} ${staebe === 1 ? 'Stab' : 'Stäbe'}`;
  },
};

/** Welche Materialien ein Bauteil braucht -- je Bauteilart. */
const MATERIALIEN = {
  querschnitt: (q) => [q.beton, ...q.lagen.map((l) => l.stahl)],
  querschnittsanalyse: benutzteMaterialien,
  balkensystem: systemMaterialien,
};

/** Welche Bauteile ein Bauteil als Querschnitt nimmt -- das tut nur ein Balkensystem. */
const BEZUEGE = { balkensystem: benutzteBauteile };

/** Wie ein neues Bauteil entsteht -- je Bauteilart. */
const ANLEGEN = {
  querschnitt: platteAnlegen,
  querschnittsanalyse: analyseAnlegen,
  balkensystem: systemAnlegen,
};

/** Was rechts im Eintrag steht, wie er aussieht und wie er weggeht -- je Art. */
const ART = {
  material: (m) => ({ text: m.sorte, loeschen: materialLoeschen }),
  skript: (s) => {
    const zeilen = (s.code || '').split('\n').filter((z) => z.trim()).length;
    return { text: `${zeilen} ${zeilen === 1 ? 'Zeile' : 'Zeilen'}`, loeschen: () => entfernen('skripte', s) };
  },
  ...Object.fromEntries(ARTEN.map((a) => [a.art, (e) => ({
    text: KURZTEXT[a.art](e), loeschen: () => bauteilLoeschen(a, e),
  })])),
};

function eintrag(m, art) {
  const aktiv = zustand.auswahl?.art === art && zustand.auswahl.kennung === m.kennung;
  const istMaterial = art === 'material';
  const { text, loeschen } = ART[art](m);
  return el('div.baum-eintrag', {
    class: aktiv ? 'ist-aktiv' : '',
    on: { click: () => waehlen({ art, kennung: m.kennung }) },
  }, [
    el('span.name', {
      text: istMaterial ? (m.name || m.sorte) : m.name,
      title: istMaterial ? (m.name || m.sorte) : m.name,
    }),
    istMaterial && m.eigenstaendig ? el('span.eigen', { text: 'eigen' }) : null,
    istMaterial && !m.eigenstaendig
      ? el('span.schloss', { text: '\u{1F512}', title: 'Normsorte – Kennwerte gesperrt' })
      : null,
    el('span.art', { text }),
    el('button.knopf.knopf-zart.knopf-gefahr', {
      text: '×', title: 'Entfernen',
      on: {
        click: (e) => {
          e.stopPropagation();
          loeschen(m);
        },
      },
    }),
  ]);
}

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

function leerzeile(text) {
  return el('div', {
    text, style: { padding: '5px 10px', color: 'var(--schrift-zart)', fontSize: '12.5px' },
  });
}

// ===========================================================================
// Aktionen
// ===========================================================================

function materialLoeschen(material) {
  const benutztVon = ARTEN.flatMap((a) => (zustand.projekt[a.liste] || []).filter((e) =>
    MATERIALIEN[a.art](e).includes(material.kennung)));
  if (benutztVon.length) {
    melden(`„${material.name || material.sorte}" verwendet von: `
      + benutztVon.map((q) => q.name).join(', '), true);
    return;
  }
  entfernen('materialien', material);
}

/** Ein Bauteil -- ausser ein Balkensystem nimmt noch seinen Querschnitt. */
function bauteilLoeschen(art, eintrag) {
  const benutztVon = ARTEN.flatMap((a) => (zustand.projekt[a.liste] || []).filter((e) =>
    (BEZUEGE[a.art]?.(e) || []).includes(eintrag.kennung)));
  if (benutztVon.length) {
    melden(`„${eintrag.name}" ist Querschnitt in: ${benutztVon.map((s) => s.name).join(', ')}`, true);
    return;
  }
  entfernen(art.liste, eintrag);
}

/** Einen Eintrag aus einer Liste des Projekts -- und aus der Auswahl, wenn er gewählt war. */
function entfernen(liste, eintrag) {
  projektAendern((p) => {
    p[liste] = p[liste].filter((x) => x.kennung !== eintrag.kennung);
  });
  if (zustand.auswahl?.kennung === eintrag.kennung) waehlen(null);
}

/** Ein neues Skript -- nach der Vorlage des Kerns, mit einem Diagramm darin. */
function skriptAnlegen() {
  const vorlage = zustand.katalog?.neues_skript;
  if (!vorlage) {
    melden('Katalog noch nicht geladen.', true);
    return;
  }
  const kennung = freieKennung('p');
  projektAendern((p) => {
    p.skripte = p.skripte || [];
    p.skripte.push({ ...vorlage, kennung, name: naechsterName('Skript', p.skripte) });
  }, 'skript');
  waehlen({ art: 'skript', kennung });
}

/**
 * Ein neues Material: die erste Sorte in der Reihenfolge des Kerns, die es im
 * Projekt noch nicht gibt -- beim Beton C25/30, dann aufwärts, beim Stahl
 * B500B, dann die übrigen.
 */
function materialAnlegen(art) {
  const kennung = freieKennung(art === 'beton' ? 'b' : 's');
  const vergeben = new Set(zustand.projekt.materialien.map((m) => m.name || m.sorte));
  // Eine Normsorte darf es nur einmal geben -- der Name ist ihre Kennzeichnung.
  const frei = (zustand.katalog?.anlegen?.[art] || []).find((sorte) => !vergeben.has(sorte));
  if (!frei) {
    melden('Alle Normsorten angelegt. Abwandeln: Material öffnen → '
      + '«Material modifizieren».', true);
    return;
  }
  projektAendern((p) => {
    p.materialien.push(ausVorlage('material', { kennung, art, sorte: frei, name: frei }));
  });
  waehlen({ art: 'material', kennung });
}

function platteAnlegen(art) {
  const beton = zustand.projekt.materialien.find((m) => m.art === 'beton');
  const stahl = zustand.projekt.materialien.find((m) => m.art === 'betonstahl');
  if (!beton || !stahl) {
    melden('Zuerst Beton und Betonstahl anlegen.', true);
    return;
  }
  // Die Vorlage kommt aus dem Kern. Sie stand einmal hier -- zwanzig Felder,
  // die von Hand mit den Vorgaben in opencivil/projekt/platte.py
  // gleichgehalten werden mussten. Als sich die Vorgaben änderten, blieb
  // diese Kopie stehen, und neue Platten brachten Nachweise eingeschaltet
  // mit, die überall sonst aus waren. Gesetzt wird hier nur noch, was der
  // Kern nicht wissen kann: die Kennung, der Name und welche Materialien es
  // im Projekt gibt.
  const vorlage = zustand.katalog?.neue_platte;
  if (!vorlage) {
    melden('Katalog noch nicht geladen.', true);
    return;
  }
  const kennung = freieKennung(art.vorsilbe);
  projektAendern((p) => {
    // Kopie, nicht die Vorlage selbst: sonst teilten sich alle neuen Platten
    // dieselben Lagen, und die zweite änderte die erste mit.
    const platte = structuredClone(vorlage);
    platte.kennung = kennung;
    platte.name = naechsterName(art.stamm, p[art.liste]);
    platte.beton = beton.kennung;
    platte.querkraftbewehrung.stahl = stahl.kennung;
    platte.lagen.forEach((l) => { l.stahl = stahl.kennung; });
    p[art.liste].push(platte);
  });
  waehlen({ art: art.art, kennung });
}

/**
 * Eine neue Querschnittsanalyse -- wie die Platte nach der Vorlage des Kerns:
 * ein Rechteck mit Stäben und einem Lastfall. Gesetzt wird nur, was der Kern
 * nicht wissen kann: Kennung, Name und die Materialien des Projekts.
 */
function analyseAnlegen(art) {
  const beton = zustand.projekt.materialien.find((m) => m.art === 'beton');
  const stahl = zustand.projekt.materialien.find((m) => m.art === 'betonstahl');
  if (!beton || !stahl) {
    melden('Zuerst Beton und Betonstahl anlegen.', true);
    return;
  }
  const vorlage = zustand.katalog?.neue_querschnittsanalyse;
  if (!vorlage) {
    melden('Katalog noch nicht geladen.', true);
    return;
  }
  const kennung = freieKennung(art.vorsilbe);
  fensterVergessen(kennung);
  projektAendern((p) => {
    const analyse = structuredClone(vorlage);
    analyse.kennung = kennung;
    p[art.liste] = p[art.liste] || [];
    analyse.name = naechsterName(art.stamm, p[art.liste]);
    analyse.flaechen.forEach((f) => { f.material = beton.kennung; });
    for (const liste of [analyse.staebe, analyse.stablinien, analyse.schubwaende]) {
      liste.forEach((x) => { x.stahl = stahl.kennung; });
    }
    p[art.liste].push(analyse);
  });
  waehlen({ art: art.art, kennung });
}

/**
 * Ein neues Balkensystem -- nach der Vorlage des Kerns ein Einfeldträger
 * mit einem Lastfall. Gesetzt wird nur, was der Kern nicht wissen kann:
 * Kennung, Name und der Beton der Linien.
 */
function systemAnlegen(art) {
  const beton = zustand.projekt.materialien.find((m) => m.art === 'beton');
  if (!beton) {
    melden('Zuerst einen Beton anlegen.', true);
    return;
  }
  const vorlage = zustand.katalog?.neues_balkensystem;
  if (!vorlage) {
    melden('Katalog noch nicht geladen.', true);
    return;
  }
  const kennung = freieKennung(art.vorsilbe);
  systemfensterVergessen(kennung);
  projektAendern((p) => {
    const system = structuredClone(vorlage);
    system.kennung = kennung;
    p[art.liste] = p[art.liste] || [];
    system.name = naechsterName(art.stamm, p[art.liste]);
    system.linien.forEach((l) => { if (l.stab) l.material = beton.kennung; });
    p[art.liste].push(system);
  });
  waehlen({ art: art.art, kennung });
}

// ===========================================================================

/**
 * Zeichnet die linke Tafel: die Knöpfe der Apps in `knoepfe`, die Liste der
 * gewählten darunter in `behaelter`.
 */
export function baumZeichnen(knoepfe, behaelter) {
  const p = zustand.projekt;
  if (!p) {
    ersetzen(knoepfe);
    return ersetzen(behaelter, el('div.leer', { text: 'Projekt wird geladen …' }));
  }
  const app = gewaehlteApp();
  ersetzen(knoepfe, el('div.kacheln', {}, APPS.map((a) => appKnopf(a, p, a.app === app))));

  const plus = (titel, tun) => el('button.knopf.knopf-zart', {
    text: '+', title: titel, on: { click: tun },
  });
  if (app === 'material') {
    return ersetzen(behaelter, ...[['beton', 'Beton', 'kein Beton'],
      ['betonstahl', 'Betonstahl', 'kein Betonstahl']].map(([art, titel, leer]) => liste({
      titel, art: 'material', leer,
      eintraege: p.materialien.filter((m) => m.art === art),
      plus: plus(`${titel} hinzufügen`, () => materialAnlegen(art)),
    })));
  }
  if (app === 'skript') {
    return ersetzen(behaelter, liste({
      titel: 'Python-Skripte', art: 'skript', leer: 'kein Skript', eintraege: p.skripte || [],
      plus: plus('Skript hinzufügen', skriptAnlegen),
    }));
  }
  const a = artVon(app);
  return ersetzen(behaelter, liste({
    titel: a.titel, art: a.art, leer: a.leer, eintraege: p[a.liste] || [],
    plus: plus(`${a.einzahl} hinzufügen`, () => ANLEGEN[a.art](a)),
  }));
}
