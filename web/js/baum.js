/**
 * baum.js -- Linke Tafel: die Bestandteile des Projekts.
 *
 * Gliederung::
 *
 *     Materialien
 *         Beton
 *         Betonstahl
 *     Stahlbeton-Platten
 *     Querschnittsanalyse
 *     2D Balkensysteme
 *     Analytische Gleichungen
 *
 * Jedes Kapitel lässt sich zuklappen; die Werkzeuge sitzen rechts in der
 * Kapitelleiste. Beim Löschen eines Materials wird geprüft, ob eine Platte,
 * eine Querschnittsanalyse oder ein Balkensystem es noch braucht -- und beim
 * Löschen einer Platte oder Analyse, ob ein Balkensystem ihren Querschnitt
 * nimmt. Sonst wäre die Beschreibung anschliessend widersprüchlich, und der
 * Rechenkern müsste einen Fehler melden, den die Oberfläche hätte verhindern
 * können.
 */

import { ARTEN } from './arten.js';
import { el, ersetzen, melden } from './dom.js';
import { neueZeile } from './gleichungen.js';
import { benutzteMaterialien } from './querschnittsanalyse.js';
import { fensterVergessen } from './qa_zeichnung.js';
import { benutzteBauteile, benutzteMaterialien as systemMaterialien } from './balkensystem.js';
import { fensterVergessen as systemfensterVergessen } from './bs_zeichnung.js';
import {
  aendern, ausVorlage, freieKennung, naechsterName, projektAendern, umschalten, zustand,
} from './zustand.js';

// ===========================================================================
// Bausteine
// ===========================================================================

function kapitel({ schluessel, titel, anzahl, werkzeuge, kinder, oben }) {
  const zu = !zustand.offen.has(schluessel);
  return el('div.baum-gruppe', {}, [
    el('div.baum-kopf', {
      class: `${zu ? 'ist-zu' : ''} ${oben ? 'baum-kopf-oben' : ''}`,
      on: { click: () => umschalten(schluessel) },
    }, [
      el('span.pfeil', { text: '▼' }),
      el('span.titel', { text: titel }),
      anzahl !== undefined ? el('span.zaehler', { text: String(anzahl) }) : null,
      werkzeuge ? el('span.werkzeuge', {
        on: { click: (e) => e.stopPropagation() },
      }, [].concat(werkzeuge)) : null,
    ]),
    zu ? null : el('div.baum-koerper', {}, kinder),
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
  blatt: (b) => ({
    text: `${b.zeilen.length} ${b.zeilen.length === 1 ? 'Zeile' : 'Zeilen'}`,
    loeschen: () => entfernen('gleichungen', b),
  }),
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
    on: { click: () => aendern({ auswahl: { art, kennung: m.kennung } }, 'auswahl') },
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
  if (zustand.auswahl?.kennung === eintrag.kennung) aendern({ auswahl: null }, 'auswahl');
}

function blattAnlegen() {
  const kennung = freieKennung('g');
  projektAendern((p) => {
    p.gleichungen = p.gleichungen || [];
    p.gleichungen.push({
      kennung, name: naechsterName('Blatt', p.gleichungen),
      zeilen: [neueZeile()],
    });
  });
  aendern({ auswahl: { art: 'blatt', kennung } }, 'auswahl');
}

function materialAnlegen(art) {
  const kennung = freieKennung(art === 'beton' ? 'b' : 's');
  const liste = art === 'beton' ? zustand.katalog?.betonsorten : zustand.katalog?.stahlsorten;
  const vergeben = new Set(zustand.projekt.materialien.map((m) => m.name || m.sorte));
  // Eine Normsorte darf es nur einmal geben -- der Name ist ihre Kennzeichnung.
  const frei = (liste || []).find((s) => !vergeben.has(s.sorte));
  if (!frei) {
    melden('Alle Normsorten angelegt. Abwandeln: Material öffnen → '
      + '«Material modifizieren».', true);
    return;
  }
  projektAendern((p) => {
    p.materialien.push(ausVorlage('material', {
      kennung, art, sorte: frei.sorte, name: frei.sorte,
    }));
  });
  aendern({ auswahl: { art: 'material', kennung } }, 'auswahl');
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
  aendern({ auswahl: { art: art.art, kennung } }, 'auswahl');
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
  aendern({ auswahl: { art: art.art, kennung } }, 'auswahl');
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
  aendern({ auswahl: { art: art.art, kennung } }, 'auswahl');
}

// ===========================================================================

export function baumZeichnen(behaelter) {
  const p = zustand.projekt;
  if (!p) return ersetzen(behaelter, el('div.leer', { text: 'Projekt wird geladen …' }));

  const betone = p.materialien.filter((m) => m.art === 'beton');
  const staehle = p.materialien.filter((m) => m.art === 'betonstahl');

  const knopf = (text, titel, tun) => el('button.knopf.knopf-zart', {
    text, title: titel, on: { click: tun },
  });

  const materialien = kapitel({
    schluessel: 'materialien',
    titel: 'Materialien',
    anzahl: p.materialien.length,
    oben: true,
    kinder: [
      el('div.baum-unter', {}, [
        kapitel({
          schluessel: 'beton',
          titel: 'Beton',
          anzahl: betone.length,
          werkzeuge: knopf('+', 'Beton hinzufügen', () => materialAnlegen('beton')),
          kinder: betone.length
            ? betone.map((m) => eintrag(m, 'material'))
            : [leerzeile('kein Beton')],
        }),
        kapitel({
          schluessel: 'betonstahl',
          titel: 'Betonstahl',
          anzahl: staehle.length,
          werkzeuge: knopf('+', 'Betonstahl hinzufügen', () => materialAnlegen('betonstahl')),
          kinder: staehle.length
            ? staehle.map((m) => eintrag(m, 'material'))
            : [leerzeile('kein Betonstahl')],
        }),
      ]),
    ],
  });

  // Je Bauteilart ein Kapitel, in der Reihenfolge von ARTEN.
  const bauteile = ARTEN.map((a) => {
    const eintraege = p[a.liste] || [];
    return kapitel({
      schluessel: a.kapitel,
      titel: a.titel,
      anzahl: eintraege.length,
      oben: true,
      werkzeuge: knopf('+', `${a.einzahl} hinzufügen`, () => ANLEGEN[a.art](a)),
      kinder: eintraege.length
        ? eintraege.map((e) => eintrag(e, a.art))
        : [leerzeile(a.leer)],
    });
  });

  const blaetter = p.gleichungen || [];
  const gleichungen = kapitel({
    schluessel: 'gleichungen',
    titel: 'Analytische Gleichungen',
    anzahl: blaetter.length,
    oben: true,
    werkzeuge: knopf('+', 'Blatt hinzufügen', blattAnlegen),
    kinder: blaetter.length ? blaetter.map((b) => eintrag(b, 'blatt')) : [leerzeile('kein Blatt')],
  });

  ersetzen(behaelter, materialien, ...bauteile, gleichungen);
}
