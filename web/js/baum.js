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
import { aendern, freieKennung, projektAendern, umschalten, zustand } from './zustand.js';

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
    melden(`„${material.name || material.sorte}" wird noch verwendet von: `
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
    melden('Alle Normsorten dieser Art sind bereits angelegt. Zum Abwandeln ein '
      + 'bestehendes Material öffnen und „Material modifizieren" wählen.', true);
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
    melden('Zuerst je ein Beton- und ein Betonstahlmaterial anlegen.', true);
    return;
  }
  const kennung = freieKennung('q');
  const lage = (phi) => ({
    stahl: stahl.kennung,
    grund: { durchmesser: phi, abstand: 150, anzahl: null },
    // Auch die leere Zulage wird über die Teilung geführt -- das ist der
    // Regelfall bei Platten und die Stellung, in der das Feld erscheint.
    zulage: { durchmesser: 0, abstand: 150, anzahl: null },
  });
  projektAendern((p) => {
    p.querschnitte.push({
      kennung,
      name: `Platte ${p.querschnitte.length + 1}`,
      beton: beton.kennung,
      h: 300, b: 1000,
      // Grösstkorn und Einlagenhöhe gehören zur Platte und gehen in den
      // Querkraftwiderstand ein. Ohne Vorgabe stünden die Felder leer da und
      // der Nachweis meldete eine fehlende Eingabe.
      d_max: 32, einlagenhoehe: 0, k_c: 0.55,
      // Ohne Durchmesser: keine Querkraftbewehrung. Die übrigen Felder stehen
      // trotzdem da, damit die Maske beim Eintragen eines Durchmessers nicht
      // mit leeren Teilungen dasteht.
      querkraftbewehrung: {
        durchmesser: 0, stahl: stahl.kennung,
        abstand_x: 200, abstand_y: 200, anzahl_y: null,
        alpha_min: 30, alpha_max: 45,
      },
      ueberdeckung_unten: 30, ueberdeckung_oben: 30,
      richtung_lage1: 'x', richtung_lage4: 'x',
      // Nur aussen bewehrt: die 1. und die 4. Lage tragen, die beiden inneren
      // sind erst einmal nicht da. Was man nicht braucht, soll man wegnehmen
      // müssen und nicht wegnehmen dürfen.
      lagen: [lage(12), lage(0), lage(0), lage(12)],
      // Die beiden äusseren Lagen tragen Feld- und Stützmoment; dort
      // entscheidet sich, ob der Querschnitt sein Versagen ankündigt.
      duktilitaet: [true, false, false, true],
      // Eine Zwängung ist eine Annahme über das Tragwerk, keine Eigenschaft
      // der Platte -- wer sie braucht, schaltet sie ein.
      rissanforderung: 'normal', kriechzahl: 2.0,
      zwaengung_x: false, zwaengung_y: false, zwaengung_begrenzt: false,
      haeufige_aus_tragsicherheit: true, haeufige: [],
      // 'automatisch': beide Massstäbe werden gerechnet, massgebend ist der
      // kleinere Erfüllungsgrad. Eine feste Wahl hier hätte die neue Platte
      // vom Regelfall ausgenommen.
      kombinationen: [{ name: 'Feld', M_Ed: 100, N_Ed: 0, art: 'automatisch', richtung: 'x' }],
    });
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
