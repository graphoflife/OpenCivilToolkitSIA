/**
 * platte.js -- der Editor einer Stahlbeton-Platte: Abmessungen, Bewehrung
 * und die Knöpfe ihrer Kapitel.
 *
 * BEWEHRUNG:
 * Vier Lagen, von unten nach oben. Die Eingabemaske ist genauso gestapelt --
 * die 1. Lage steht unten, direkt über der unteren Überdeckung. Jede Lage hat
 * eine Grundbewehrung und eine Zulage. Die Richtung der 1. und der 4. Lage ist
 * wählbar; die 2. und die 3. bekommen zwingend die Gegenrichtung.
 *
 * Angezeigt wird immer der Wert aus der letzten Lösung, nie ein in der
 * Oberfläche nachgerechneter. Bis 2026-10-18 stand der Editor in editor.js,
 * zusammen mit dem des Materials.
 */

import {
  beschreibung, bezeichnung, feld, panel, wahlSchalter, zweiSchalter,
} from './bausteine.js';
import { auswahl, el, zahlfeld } from './dom.js';
import { span } from './mathe.js';
import { kapitelFenster, kapitelPanel } from './kapitel.js';
import { partnerVon, richtungSetzen, richtungVon } from './lagen.js';
import { plattenKapitel } from './plattenkapitel.js';
import { eintragAendern, feldangabe, katalog, materialien } from './zustand.js';


/**
 * Ein Bewehrungsposten auf einer Zeile:
 *
 *     ×  Grund   ⌀ [18] @ [150] mm   [B500B]
 *
 * Am Ende der Schalter «mm | Stk»: «mm» heisst Teilung, «Stk» Stabzahl --
 * das Trennzeichen wechselt mit (`@` bzw. `×`).
 *
 * Das × vorne setzt den Durchmesser auf null und nimmt den Posten damit heraus.
 * Es ist nur rot, solange es etwas zu entfernen gibt; bei leerem Posten bleibt
 * es blass, statt ganz zu verschwinden -- sonst rutschte die Zeile bei jeder
 * Eingabe um seine Breite.
 */
function postenZeile(querschnitt, nummer, welcher, beschriftung) {
  const posten = querschnitt.lagen[nummer - 1][welcher];
  const ueberAbstand = posten.art === 'teilung';
  const leer = !(posten.durchmesser > 0);

  const aendern = (veraenderer) => eintragAendern(querschnitt.kennung,
    (q) => veraenderer(q.lagen[nummer - 1][welcher]));

  return el('div.postenzeile', { class: leer ? 'ist-leer' : '' }, [
    el('button.weg', {
      text: '×',
      class: leer ? 'ist-stumpf' : '',
      disabled: leer,
      title: `${beschriftung}bewehrung der ${nummer}. Lage entfernen`,
      on: { click: () => aendern((x) => { x.durchmesser = 0; }) },
    }),
    el('span.postenname', { text: beschriftung }),
    el('span.zeichen', { text: '⌀' }),
    zahlfeld({
      wert: posten.durchmesser || null, stufen: katalog('durchmesser'),
      angabe: feldangabe('posten', 'durchmesser'),
      titel: '⌀ in mm; leer oder 0: keine Bewehrung',
      leer: 0,
      beiAenderung: (v) => aendern((x) => { x.durchmesser = v; }),
    }),
    el('span.zeichen', { text: ueberAbstand ? '@' : '×' }),
    ueberAbstand
      ? zahlfeld({
        wert: posten.abstand, schritt: 25, angabe: feldangabe('posten', 'abstand'), titel: 'Teilung in mm',
        beiAenderung: (v) => aendern((x) => { x.abstand = v; }),
      })
      : zahlfeld({
        wert: posten.anzahl, schritt: 1, angabe: feldangabe('posten', 'anzahl'), titel: 'Stabzahl je b',
        beiAenderung: (v) => aendern((x) => { x.anzahl = v; }),
      }),
    einheitsSchalter(posten.art, (art) => aendern((x) => { x.art = art; })),
  ]);
}

/**
 * «mm | Stk» hinter der Teilung: ein Schalter wie jeder andere, knapp, damit
 * er in die Zeile passt (Benutzer, 2026-11-20). Bis dahin war es die Einheit
 * selbst, gestrichelt unterstrichen. Umgeschaltet wird nur, welche gilt
 * (`art`); beide Zahlen bleiben stehen, und ihre Vorgaben kommen aus dem
 * Kern -- bis 2026-10-18 setzte das Umschalten hier eigene (5 Stäbe, 150
 * und 200 mm).
 */
function einheitsSchalter(art, setzen) {
  return zweiSchalter({
    stellungen: [['teilung', 'mm'], ['anzahl', 'Stk']], gewaehlt: art, setzen, klasse: '.ist-knapp',
    titel: 'Teilung in mm oder Stabzahl je b – Klicken schaltet um',
  });
}

function lagenBlock(querschnitt, nummer) {
  const lage = querschnitt.lagen[nummer - 1];
  const richtung = richtungVon(querschnitt, nummer);
  const partner = partnerVon(nummer);
  const leer = !(lage.grund.durchmesser > 0 || lage.zulage.durchmesser > 0);

  // Zwei Zeilen je Lage, Grund und Zulage, links Nummer und Richtung;
  // darunter, wo es zwei Posten gibt, ihre Lage zueinander. Der Stahl gilt
  // für alle Lagen und steht oben bei der Platte (Benutzer, 2026-10-24).
  return el('div.lage', { class: `lage-${richtung} ${leer ? 'ist-leer' : ''}` }, [
    el('div.lage-kopf', {}, [
      el('span.lage-name', { text: `${nummer}. Lage` }),
      richtungsSchalter(querschnitt, nummer, richtung, partner),
    ]),
    postenZeile(querschnitt, nummer, 'grund', 'Grund'),
    postenZeile(querschnitt, nummer, 'zulage', 'Zulage'),
    lageSchalter(querschnitt, nummer, lage),
  ]);
}

/**
 * Die Lage von Grundbewehrung und Zulage zueinander, auf einer eigenen Zeile
 * unter den Posten: ein Schalter «ungünstig | günstig» wie jeder andere, je
 * Stellung mit dem Bild der zwei Stäbe im Schnitt, an welcher Kante sie
 * bündig liegen (Benutzer, 2026-11-20). Bis dahin ein einzelner Knopf am
 * Ende der Zeile der Zulage -- er war breiter als seine Spalte und ragte
 * über «mm».
 *
 * Nur sichtbar, wenn die Lage überhaupt zwei Posten hat -- bei einer einzelnen
 * Bewehrung gibt es nichts zueinander zu legen.
 */
function lageSchalter(querschnitt, nummer, lage) {
  if (!(lage.grund?.durchmesser > 0 && lage.zulage?.durchmesser > 0)) return null;

  const seite = nummer <= 2 ? 'unten' : 'oben';
  const gegen = nummer <= 2 ? 'oben' : 'unten';
  const kante = { unten: 'Unterkante', oben: 'Oberkante' };
  return el('div.gunstzeile', {}, [
    el('span.gunstzeile-titel', { text: 'Zulage zur Grundbewehrung' }),
    wahlSchalter({
      werte: [
        { wert: true, beschriftung: 'ungünstig', zeichen: `zulage-${seite}-unguenstig`,
          titel: `Gleiche ${kante[gegen]}, der dünnere Stab rückt nach ${gegen}` },
        { wert: false, beschriftung: 'günstig', zeichen: `zulage-${seite}-guenstig`,
          titel: `Gleiche ${kante[seite]}, jeder um seinen Halbmesser eingerückt` },
      ],
      gewaehlt: lage.unguenstig !== false,
      setzen: (unguenstig) => eintragAendern(querschnitt.kennung, (q) => {
        q.lagen[nummer - 1].unguenstig = unguenstig;
      }),
      titel: 'Wie Grund und Zulage dieser Lage zueinander liegen',
    }),
  ]);
}

/** Zweistellungs-Schalter x|y. Die Partnerlage folgt zwingend der Gegenrichtung. */
function richtungsSchalter(querschnitt, nummer, richtung, partner) {
  // Beide Schalter eines Paars zeigen dasselbe Paar, nur von der anderen
  // Seite -- wie gespeichert wird, weiss lagen.js.
  const setzen = (wert) => eintragAendern(querschnitt.kennung, (q) => richtungSetzen(q, nummer, wert));

  return zweiSchalter({
    stellungen: [['x', 'x', 'ist-x'], ['y', 'y', 'ist-y']], gewaehlt: richtung, setzen,
    titel: `Tragrichtung der ${nummer}. Lage – die ${partner}. bekommt die Gegenrichtung. `
      + 'Klicken schaltet um.',
  });
}


/**
 * Die Bügel -- ein Raster über die ganze Platte, unterhalb der Lagen, und
 * gebaut wie eine Lage: zwei Zeilen, links der Name. Ihr Stahl ist der der
 * Platte, oben unter dem Beton (Benutzer, 2026-10-24).
 *
 *     Bügel  ×  x  ⌀ [10] @ [200] mm
 *                y         @ [200] mm
 *
 * Die Neigung der Druckdiagonalen und k_c stehen im Fenster der
 * Tragsicherheit: sie gehören zur Rechnung, nicht zur Bewehrung.
 *
 * In y darf statt der Teilung eine Stabzahl über die betrachtete Breite
 * stehen, in x nicht: der Widerstand gilt je Laufmeter, und eine Stabzahl
 * hätte darin keinen Bezug. Bis 2026-11-19 hiess es am Feld, mit ihr gebe
 * es nur noch Nachweise in x -- nachgewiesen wird aber ohnehin nur x.
 */
function querkraftBlock(querschnitt) {
  // Vollständig: jede Platte kommt durch den Kern, und der setzt die Bügel
  // mit allen Feldern.
  const buegel = querschnitt.querkraftbewehrung;
  const ueberAbstand = buegel.art_y === 'teilung';
  const leer = !(buegel.durchmesser > 0);

  const aendern = (veraenderer) => eintragAendern(querschnitt.kennung,
    (q) => veraenderer(q.querkraftbewehrung));

  return el('div.lage.lage-querkraft', { class: leer ? 'ist-leer' : '' }, [
    el('div.lage-kopf', {}, [el('span.lage-name', { text: 'Bügel' })]),
    el('div.postenzeile', { class: leer ? 'ist-leer' : '' }, [
      el('button.weg', {
        text: '×',
        class: leer ? 'ist-stumpf' : '',
        disabled: leer,
        title: 'Querkraftbewehrung entfernen',
        on: { click: () => aendern((x) => { x.durchmesser = 0; }) },
      }),
      el('span.postenname', { text: 'x' }),
      el('span.zeichen', { text: '⌀' }),
      zahlfeld({
        wert: buegel.durchmesser || null, stufen: katalog('durchmesser'),
        angabe: feldangabe('querkraftbewehrung', 'durchmesser'),
        titel: 'Bügel-⌀ in mm; leer oder 0: keine Bügel',
        leer: 0,
        beiAenderung: (v) => aendern((x) => { x.durchmesser = v; }),
      }),
      el('span.zeichen', { text: '@' }),
      zahlfeld({
        wert: buegel.abstand_x, schritt: 25, angabe: feldangabe('querkraftbewehrung', 'abstand_x'),
        titel: 'Bügelteilung x in mm',
        beiAenderung: (v) => aendern((x) => { x.abstand_x = v; }),
      }),
      el('span.einheit', { text: 'mm' }),
    ]),
    el('div.postenzeile', { class: leer ? 'ist-leer' : '' }, [
      el('span'),
      el('span.postenname', { text: 'y' }),
      el('span'),
      el('span'),
      el('span.zeichen', { text: ueberAbstand ? '@' : '×' }),
      ueberAbstand
        ? zahlfeld({
          wert: buegel.abstand_y, schritt: 25, angabe: feldangabe('querkraftbewehrung', 'abstand_y'),
          titel: 'Bügelteilung y in mm',
          beiAenderung: (v) => aendern((x) => { x.abstand_y = v; }),
        })
        : zahlfeld({
          wert: buegel.anzahl_y, schritt: 1, angabe: feldangabe('querkraftbewehrung', 'anzahl_y'),
          titel: 'Bügelzahl je b',
          beiAenderung: (v) => aendern((x) => { x.anzahl_y = v; }),
        }),
      einheitsSchalter(buegel.art_y, (art) => aendern((x) => { x.art_y = art; })),
    ]),
  ]);
}

function ueberdeckungsBlock(querschnitt, welche) {
  const unten = welche === 'unten';
  const aendern = (v) => eintragAendern(querschnitt.kennung, (q) => {
    if (unten) q.ueberdeckung_unten = v;
    else q.ueberdeckung_oben = v;
  });
  return el('div.ueberdeckung', {}, [
    feld(`Überdeckung ${welche}`, zahlfeld({
      wert: unten ? querschnitt.ueberdeckung_unten : querschnitt.ueberdeckung_oben,
      schritt: 5, angabe: feldangabe('querschnitt', `ueberdeckung_${welche}`), beiAenderung: aendern,
    }), 'mm'),
  ]);
}

export function plattenEditor(querschnitt) {
  const betone = materialien('beton');
  const staehle = materialien('betonstahl');
  const aendern = (veraenderer) => eintragAendern(querschnitt.kennung, veraenderer);

  return [
    panel({ schluessel: 'platte/Platte', titel: 'Platte' }, [
      // Eine Karte mit blauer Kante wie die Lagen und die Nachweiskapitel:
      // ohne sie stand die Platte als einzige blosse Feldliste da.
      el('div.unterkapitel', {}, [
        bezeichnung(querschnitt, aendern),
        feld('Beton', auswahl({
          werte: betone.map((b) => ({ wert: b.kennung, beschriftung: b.name || b.sorte })),
          gewaehlt: querschnitt.beton,
          beiAenderung: (v) => aendern((q) => { q.beton = v; }),
        })),
        // Ein Stahl für die ganze Platte, Lagen und Bügel (Benutzer, 2026-10-24).
        feld('Stahl', auswahl({
          werte: staehle.map((s) => ({ wert: s.kennung, beschriftung: s.name || s.sorte })),
          gewaehlt: querschnitt.stahl,
          titel: 'Betonstahl der Platte – aller Lagen und der Bügel',
          beiAenderung: (v) => aendern((q) => { q.stahl = v; }),
        })),
        feld('Dicke h', zahlfeld({
          wert: querschnitt.h, schritt: 10, angabe: feldangabe('querschnitt', 'h'),
          beiAenderung: (v) => aendern((q) => { q.h = v; }),
        }), 'mm'),
        feld(['Breite ', span('b_x')], zahlfeld({
          wert: querschnitt.b, schritt: 100, angabe: feldangabe('querschnitt', 'b'),
          titel: 'Streifen in x: A_s, M und N je b. y: je 1000 mm',
          beiAenderung: (v) => aendern((q) => { q.b = v; }),
        }), 'mm'),
        // Grösstkorn, k_c und Einlage stehen im Fenster der
        // Tragsicherheit: nur die Querkraft braucht sie. Die Kriechzahl des
        // Vergrösserungsfaktors steht im Fenster der Verformung.
        // Freier Text, der in keine Rechnung eingeht. Ohne ein solches Feld
        // landen solche Sätze im Namen der Platte.
        beschreibung(querschnitt, aendern, { zeilen: 3 }),
      ]),
    ]),

    panel({ schluessel: 'platte/Bewehrung', titel: 'Bewehrung', zusatz: 'von unten nach oben' }, [
      ueberdeckungsBlock(querschnitt, 'oben'),
      lagenBlock(querschnitt, 4),
      lagenBlock(querschnitt, 3),
      lagenBlock(querschnitt, 2),
      lagenBlock(querschnitt, 1),
      ueberdeckungsBlock(querschnitt, 'unten'),
      // Die Bügel stehen unter den Lagen: sie greifen über die ganze Höhe
      // und gehören in keine davon.
      querkraftBlock(querschnitt),
    ]),

    // Nachweise, Analysen und die Suche der Bewehrung: je ein Knopf, die
    // Eingaben im Fenster -- welche es sind, steht in plattenkapitel.js.
    kapitelPanel(querschnitt, plattenKapitel(),
      { schluessel: 'platte/Kapitel', titel: 'Nachweise und Analysen' }),
  ];
}

/** Das Fenster eines Kapitels der Platte -- über den Eingaben. */
export function plattenFenster(querschnitt, schluessel) {
  return kapitelFenster(querschnitt, plattenKapitel(), schluessel);
}
