/**
 * baum.js -- Linke Tafel: die Bestandteile des Projekts.
 *
 * Materialien und Querschnitte anlegen, auswählen und löschen. Beim Löschen
 * eines Materials wird geprüft, ob ein Querschnitt es noch braucht -- sonst
 * wäre die Projektbeschreibung anschliessend widersprüchlich, und der
 * Rechenkern müsste einen Fehler melden, den die Oberfläche hätte verhindern
 * können.
 */

import { el, ersetzen, leerzustand, melden } from './dom.js';
import {
  aendern, freieKennung, projektAendern, zustand,
} from './zustand.js';

function eintrag({ kennung, name, art, punktklasse, aktiv, beiWahl, beiLoeschen }) {
  return el('div.baum-eintrag', {
    class: aktiv ? 'ist-aktiv' : '',
    on: { click: beiWahl },
  }, [
    el(`span.punkt.${punktklasse}`),
    el('span.name', { text: name || kennung, title: name || kennung }),
    el('span.art', { text: art }),
    el('button.knopf.knopf-zart.knopf-gefahr', {
      text: '×',
      title: 'Entfernen',
      on: {
        click: (e) => { e.stopPropagation(); beiLoeschen(); },
      },
    }),
  ]);
}

function materialLoeschen(material) {
  const benutztVon = zustand.projekt.querschnitte.filter((q) =>
    q.beton === material.kennung
    || [...q.lagen_unten, ...q.lagen_oben].some((l) => l.stahl === material.kennung));

  if (benutztVon.length) {
    melden(
      `"${material.name || material.kennung}" wird noch verwendet von: `
      + benutztVon.map((q) => q.name).join(', '), true);
    return;
  }
  projektAendern((p) => {
    p.materialien = p.materialien.filter((m) => m.kennung !== material.kennung);
  });
  if (zustand.auswahl?.kennung === material.kennung) aendern({ auswahl: null }, 'auswahl');
}

function querschnittLoeschen(querschnitt) {
  projektAendern((p) => {
    p.querschnitte = p.querschnitte.filter((q) => q.kennung !== querschnitt.kennung);
  });
  if (zustand.auswahl?.kennung === querschnitt.kennung) aendern({ auswahl: null }, 'auswahl');
}

function materialAnlegen(art) {
  const kennung = freieKennung(art === 'beton' ? 'b' : 's');
  const sorte = art === 'beton'
    ? (zustand.katalog?.betonsorten?.[4]?.sorte || 'C30/37')
    : (zustand.katalog?.stahlsorten?.[1]?.sorte || 'B500B');
  projektAendern((p) => {
    p.materialien.push({
      kennung, art, sorte, name: sorte, abweichungen: {}, ueberschreibungen: {},
    });
  });
  aendern({ auswahl: { art: 'material', kennung } }, 'auswahl');
}

function querschnittAnlegen() {
  const beton = zustand.projekt.materialien.find((m) => m.art === 'beton');
  const stahl = zustand.projekt.materialien.find((m) => m.art === 'betonstahl');
  if (!beton || !stahl) {
    melden('Zuerst je ein Beton- und ein Betonstahlmaterial anlegen.', true);
    return;
  }
  const kennung = freieKennung('q');
  projektAendern((p) => {
    p.querschnitte.push({
      kennung,
      name: `Querschnitt ${p.querschnitte.length + 1}`,
      beton: beton.kennung,
      h: 300, b: 1000,
      ueberdeckung_unten: 30, ueberdeckung_oben: 30,
      lagen_unten: [{ durchmesser: 16, stahl: stahl.kennung, abstand: 150, anzahl: null, lichter_abstand: 0 }],
      lagen_oben: [],
      kombinationen: [{ name: 'Feld', M_Ed: 100, N_Ed: 0, art: 'N_konstant' }],
    });
  });
  aendern({ auswahl: { art: 'querschnitt', kennung } }, 'auswahl');
}

function gruppe(titel, knopf, kinder) {
  return el('div.baum-gruppe', {}, [
    el('div.baum-kopf', {}, [el('span', { text: titel }), knopf]),
    ...(kinder.length ? kinder : [el('div.leer', { text: '—', style: { padding: '6px 2px', textAlign: 'left' } })]),
  ]);
}

export function baumZeichnen(behaelter) {
  const p = zustand.projekt;
  if (!p) return ersetzen(behaelter, leerzustand('Projekt wird geladen …'));

  const betone = p.materialien.filter((m) => m.art === 'beton');
  const staehle = p.materialien.filter((m) => m.art === 'betonstahl');

  const machEintrag = (m) => eintrag({
    kennung: m.kennung,
    name: m.name || m.sorte,
    art: m.sorte,
    punktklasse: m.art === 'beton' ? 'punkt-beton' : 'punkt-stahl',
    aktiv: zustand.auswahl?.art === 'material' && zustand.auswahl.kennung === m.kennung,
    beiWahl: () => aendern({ auswahl: { art: 'material', kennung: m.kennung } }, 'auswahl'),
    beiLoeschen: () => materialLoeschen(m),
  });

  ersetzen(behaelter,
    gruppe('Beton',
      el('button.knopf.knopf-zart', { text: '+ Beton', on: { click: () => materialAnlegen('beton') } }),
      betone.map(machEintrag)),

    gruppe('Betonstahl',
      el('button.knopf.knopf-zart', { text: '+ Stahl', on: { click: () => materialAnlegen('betonstahl') } }),
      staehle.map(machEintrag)),

    gruppe('Querschnitte',
      el('button.knopf.knopf-zart', { text: '+ Querschnitt', on: { click: querschnittAnlegen } }),
      p.querschnitte.map((q) => eintrag({
        kennung: q.kennung,
        name: q.name,
        art: `${q.h}×${q.b} mm`,
        punktklasse: 'punkt-qs',
        aktiv: zustand.auswahl?.art === 'querschnitt' && zustand.auswahl.kennung === q.kennung,
        beiWahl: () => aendern({ auswahl: { art: 'querschnitt', kennung: q.kennung } }, 'auswahl'),
        beiLoeschen: () => querschnittLoeschen(q),
      }))));
}
