/**
 * baum.js -- Linke Tafel: die Bestandteile des Projekts.
 *
 * Gliederung::
 *
 *     Materialien
 *         Beton
 *         Betonstahl
 *     Stahlbeton-Platten
 *
 * Jedes Kapitel lässt sich zuklappen; die Werkzeuge sitzen rechts in der
 * Kapitelleiste. Beim Löschen eines Materials wird geprüft, ob eine Platte es
 * noch braucht -- sonst wäre die Beschreibung anschliessend widersprüchlich,
 * und der Rechenkern müsste einen Fehler melden, den die Oberfläche hätte
 * verhindern können.
 */

import { el, ersetzen, melden } from './dom.js';
import {
  aendern, freieKennung, naechsterName, projektAendern, umschalten, zustand,
} from './zustand.js';

const SINNBILD = {
  materialien: '▣',   // ▣
  beton: '■',         // ■
  betonstahl: '≡',    // ≡
  platten: '▬',       // ▬
};

// ===========================================================================
// Bausteine
// ===========================================================================

function kapitel({ schluessel, titel, klasse, anzahl, werkzeuge, kinder, oben }) {
  const zu = !zustand.offen.has(schluessel);
  return el('div.baum-gruppe', {}, [
    el('div.baum-kopf', {
      class: `${klasse || ''} ${zu ? 'ist-zu' : ''} ${oben ? 'baum-kopf-oben' : ''}`,
      on: { click: () => umschalten(schluessel) },
    }, [
      el('span.pfeil', { text: '▼' }),
      el('span.titel', { text: titel }),
      anzahl !== undefined ? el('span.zaehler', { text: String(anzahl) }) : null,
      el('span.sinnbild', { text: SINNBILD[schluessel] || '' }),
      werkzeuge ? el('span.werkzeuge', {
        on: { click: (e) => e.stopPropagation() },
      }, [].concat(werkzeuge)) : null,
    ]),
    zu ? null : el('div.baum-koerper', {}, kinder),
  ]);
}

function eintrag(m, art) {
  const aktiv = zustand.auswahl?.art === art && zustand.auswahl.kennung === m.kennung;
  const istMaterial = art === 'material';
  return el('div.baum-eintrag', {
    class: `${aktiv ? 'ist-aktiv' : ''} baum-eintrag-${
      istMaterial ? (m.art === 'beton' ? 'beton' : 'stahl') : 'platte'}`,
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
    el('span.art', { text: istMaterial ? m.sorte : `${m.h}×${m.b} mm` }),
    el('button.knopf.knopf-zart.knopf-gefahr', {
      text: '×', title: 'Entfernen',
      on: {
        click: (e) => {
          e.stopPropagation();
          istMaterial ? materialLoeschen(m) : platteLoeschen(m);
        },
      },
    }),
  ]);
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
  const benutztVon = zustand.projekt.querschnitte.filter((q) =>
    q.beton === material.kennung || q.lagen.some((l) => l.stahl === material.kennung));
  if (benutztVon.length) {
    melden(`„${material.name || material.sorte}" verwendet von: `
      + benutztVon.map((q) => q.name).join(', '), true);
    return;
  }
  projektAendern((p) => {
    p.materialien = p.materialien.filter((m) => m.kennung !== material.kennung);
  });
  if (zustand.auswahl?.kennung === material.kennung) aendern({ auswahl: null }, 'auswahl');
}

function platteLoeschen(platte) {
  projektAendern((p) => {
    p.querschnitte = p.querschnitte.filter((q) => q.kennung !== platte.kennung);
  });
  if (zustand.auswahl?.kennung === platte.kennung) aendern({ auswahl: null }, 'auswahl');
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
    p.materialien.push({
      kennung, art, sorte: frei.sorte, name: frei.sorte,
      eigenstaendig: false, abweichungen: {}, ueberschreibungen: {},
    });
  });
  aendern({ auswahl: { art: 'material', kennung } }, 'auswahl');
}

function platteAnlegen() {
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
  const kennung = freieKennung('q');
  projektAendern((p) => {
    // Kopie, nicht die Vorlage selbst: sonst teilten sich alle neuen Platten
    // dieselben Lagen, und die zweite änderte die erste mit.
    const platte = structuredClone(vorlage);
    platte.kennung = kennung;
    platte.name = naechsterName('Platte', p.querschnitte);
    platte.beton = beton.kennung;
    platte.querkraftbewehrung.stahl = stahl.kennung;
    platte.lagen.forEach((l) => { l.stahl = stahl.kennung; });
    p.querschnitte.push(platte);
  });
  aendern({ auswahl: { art: 'querschnitt', kennung } }, 'auswahl');
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
          klasse: 'baum-kopf-beton',
          anzahl: betone.length,
          werkzeuge: knopf('+', 'Beton hinzufügen', () => materialAnlegen('beton')),
          kinder: betone.length
            ? betone.map((m) => eintrag(m, 'material'))
            : [leerzeile('kein Beton')],
        }),
        kapitel({
          schluessel: 'betonstahl',
          titel: 'Betonstahl',
          klasse: 'baum-kopf-stahl',
          anzahl: staehle.length,
          werkzeuge: knopf('+', 'Betonstahl hinzufügen', () => materialAnlegen('betonstahl')),
          kinder: staehle.length
            ? staehle.map((m) => eintrag(m, 'material'))
            : [leerzeile('kein Betonstahl')],
        }),
      ]),
    ],
  });

  const platten = kapitel({
    schluessel: 'platten',
    titel: 'Stahlbeton-Platten',
    klasse: 'baum-kopf-platte',
    anzahl: p.querschnitte.length,
    oben: true,
    werkzeuge: knopf('+', 'Platte hinzufügen', platteAnlegen),
    kinder: p.querschnitte.length
      ? p.querschnitte.map((q) => eintrag(q, 'querschnitt'))
      : [leerzeile('keine Platte')],
  });

  ersetzen(behaelter, materialien, platten);
}
