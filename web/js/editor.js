/**
 * editor.js -- Mittlere Tafel: Eingaben zum ausgewählten Bestandteil.
 *
 * NORMSORTE ODER EIGENES MATERIAL:
 * Eine Normsorte nach SIA ist gesperrt -- kein Feld lässt sich anfassen, auch
 * die Sorte nicht. Wer abweichen will, legt ein eigenes Material an
 * (materialwahl.js): es heisst BE1 oder S1 und ist änderbar. So kann keine
 * abgewandelte Festigkeit unter einer Normbezeichnung im Bericht landen.
 *
 * BEWEHRUNG:
 * Vier Lagen, von unten nach oben. Die Eingabemaske ist genauso gestapelt --
 * die 1. Lage steht unten, direkt über der unteren Überdeckung. Jede Lage hat
 * eine Grundbewehrung und eine Zulage. Die Richtung der 1. und der 4. Lage ist
 * wählbar; die 2. und die 3. bekommen zwingend die Gegenrichtung.
 *
 * Angezeigt wird immer der Wert aus der letzten Lösung, nie ein in der
 * Oberfläche nachgerechneter.
 */

import { feld, panel, zweiSchalter } from './bausteine.js';
import { auswahl, el, ersetzen, melden, zahlfeld } from './dom.js';
import { span } from './mathe.js';
import { fensterZeigen } from './fenster.js';
import {
  analysenKapitel, anzahl, eingeschaltet, gebrauchsstand, kapitelFenster, kapitelPanel, schalter,
} from './kapitel.js';
import { partnerVon, richtungSetzen, richtungVon } from './lagen.js';
import {
  analyseInhalt, automatikInhalt, duktilitaetInhalt, fliessenGefordert, haeufigInhalt,
  hilfe, jeB, knickInhalt, quasistaendigInhalt, sproedeInhalt, sucheLaeuft,
  tragsicherheitInhalt, verformungInhalt, zwangInhalt,
} from './nachweise.js';
import { analyseEditor, analyseFenster } from './querschnittsanalyse.js';
import { balkensystemEditor } from './balkensystem.js';
import { grundbruchEditor } from './grundbruch.js';
import { skriptZeichnen } from './python.js';
import {
  aendern, gewaehltesBauteil, gewaehltesMaterial, gewaehltesSkript, kennwertId,
  projektAendern, zustand,
} from './zustand.js';

const ART_TEXT = { beton: 'Beton', betonstahl: 'Betonstahl' };

/** Der Editor jeder Bauteilart (ARTEN, arten.js) -- fehlt einer, scheitert es laut. */
const EDITOREN = {
  querschnitt: plattenEditor,
  querschnittsanalyse: analyseEditor,
  balkensystem: balkensystemEditor,
  grundbruch: grundbruchEditor,
};

function gerechnet(id) {
  return zustand.loesung?.werte?.[id] || null;
}


// ===========================================================================
// Material
// ===========================================================================

function kennwertZeile(material, vorlage) {
  const gesperrt = !material.eigenstaendig;
  const wert = gerechnet(kennwertId(material, vorlage.kurzname));
  const istUeberschrieben = vorlage.kurzname in material.ueberschreibungen;
  const istAbweichend = vorlage.kurzname in material.abweichungen;

  let anzeige = null;
  if (istUeberschrieben) anzeige = material.ueberschreibungen[vorlage.kurzname];
  else if (istAbweichend) anzeige = material.abweichungen[vorlage.kurzname];
  else if (wert) anzeige = Number(wert.zahl.toFixed(vorlage.stellen));

  const schreibbar = !gesperrt && (!vorlage.berechnet || istUeberschrieben);

  const eingabe = zahlfeld({
    wert: anzeige,
    schritt: vorlage.stellen >= 3 ? 0.001 : (vorlage.stellen >= 1 ? 0.1 : 1),
    // Ein Baustoffkennwert ist nie negativ. Die Schnittgrössen daneben schon,
    // darum sagt es jedes Feld für sich und nicht die Pfeillogik für alle.
    min: 0,
    readonly: !schreibbar,
    titel: gesperrt ? 'Normsorte nach SIA – nicht änderbar'
      : (vorlage.berechnet && !istUeberschrieben ? 'Wird gerechnet. Haken setzen zum Überschreiben.' : ''),
    // Leer: die eigene Zahl weg, der Wert der Sorte gilt wieder.
    leer: null,
    beiAenderung: (neu) => projektAendern((p) => {
      const m = p.materialien.find((x) => x.kennung === material.kennung);
      const topf = vorlage.berechnet ? m.ueberschreibungen : m.abweichungen;
      if (neu === null) delete topf[vorlage.kurzname];
      else topf[vorlage.kurzname] = neu;
    }),
  });

  const schalter = vorlage.berechnet
    ? el('input', {
      type: 'checkbox', checked: istUeberschrieben, disabled: gesperrt,
      title: gesperrt ? 'Normsorte nach SIA – nicht änderbar' : 'Von Hand überschreiben',
      on: {
        change: (e) => projektAendern((p) => {
          const m = p.materialien.find((x) => x.kennung === material.kennung);
          if (e.target.checked) m.ueberschreibungen[vorlage.kurzname] = anzeige ?? 0;
          else delete m.ueberschreibungen[vorlage.kurzname];
        }),
      },
    })
    : el('span');

  const zuruecksetzen = (istAbweichend && !vorlage.berechnet && !gesperrt)
    ? el('button.knopf.knopf-zart', {
      text: '↺', title: 'Sortenwert zurücksetzen',
      on: {
        click: () => projektAendern((p) => {
          delete p.materialien.find((x) => x.kennung === material.kennung)
            .abweichungen[vorlage.kurzname];
        }),
      },
    })
    : el('span');

  return el('div.kennwert', {
    class: istUeberschrieben ? 'ist-ueberschrieben' : '',
    title: [vorlage.beschreibung, vorlage.referenz].filter(Boolean).join(' — '),
  }, [
    schalter,
    el('span.bezeichnung', {}, [span(vorlage.symbol), ' ', el('small', { text: vorlage.beschreibung })]),
    eingabe,
    el('span.einheit', { text: vorlage.einheit === '-' ? '' : vorlage.einheit }),
    zuruecksetzen,
  ]);
}

function materialEditor(material) {
  const vorlagen = zustand.katalog.kennwerte[material.art] || [];
  const gesperrt = !material.eigenstaendig;
  const anzahlUeberschrieben = Object.keys(material.ueberschreibungen).length;

  // Eine Normsorte bleibt, wie sie ist -- es gibt keinen Weg, sie zu ändern,
  // auch nicht ihre Sorte (Benutzer, 2026-10-16). Ein eigenes Material trägt
  // keine Sorte; seine Vorlage zählt nur beim Anlegen.
  const kopf = gesperrt
    ? el('div.gesperrt-hinweis', {}, [
      el('span.sia', { text: 'SIA' }),
      el('div', { style: { flex: '1 1 220px' } }, [
        el('b', { text: `Normsorte ${material.sorte}` }),
        ' · Kennwerte nach SIA 262:2025, nicht änderbar. Abweichen: links «+» '
        + '→ eigenes Material.',
      ]),
    ])
    : el('div.gesperrt-hinweis', {
      style: { background: 'var(--warn-hell)', borderColor: 'var(--warn)' },
    }, [
      el('div', { style: { flex: '1 1 220px' } }, [
        el('b', { text: 'Eigenes Material' }),
        ' · Die Kennwerte sind änderbar und entsprechen nicht zwingend der Norm.',
      ]),
    ]);

  return [
    kopf,
    panel({ schluessel: 'material/Material', titel: 'Material' }, [
      feld('Bezeichnung', el('input', {
        type: 'text', value: material.name || material.sorte, disabled: gesperrt,
        title: gesperrt ? 'Eine Normsorte trägt zwingend ihre Sortenbezeichnung' : '',
        on: { change: (e) => nameAendern(material, e.target.value, e.target) },
      })),
    ]),

    panel({ schluessel: 'material/Grundwerte', titel: 'Grundwerte', zusatz: 'Sortentabelle, Norm' },
      vorlagen.filter((v) => !v.berechnet).map((v) => kennwertZeile(material, v))),

    panel({
      schluessel: 'material/Abgeleitete Kennwerte',
      titel: 'Abgeleitete Kennwerte',
      zusatz: anzahlUeberschrieben
        ? el('button.knopf.knopf-zart', {
          text: `${anzahlUeberschrieben} überschrieben — zurücksetzen`,
          on: {
            click: () => projektAendern((p) => {
              p.materialien.find((x) => x.kennung === material.kennung).ueberschreibungen = {};
            }),
          },
        })
        : (gesperrt ? 'gesperrt' : 'Haken setzen zum Überschreiben'),
    }, vorlagen.filter((v) => v.berechnet).map((v) => kennwertZeile(material, v))),
  ];
}

function nameAendern(material, wunsch, feldKnoten) {
  const name = wunsch.trim();
  const vergeben = zustand.projekt.materialien
    .some((m) => m.kennung !== material.kennung && (m.name || m.sorte) === name);
  if (!name || vergeben) {
    melden(vergeben
      ? `Name „${name}" schon vergeben.`
      : 'Name leer.', true);
    feldKnoten.value = material.name;
    return;
  }
  projektAendern((p) => {
    p.materialien.find((x) => x.kennung === material.kennung).name = name;
  });
}

// ===========================================================================
// Platte
// ===========================================================================

/**
 * Ein Bewehrungsposten auf einer Zeile:
 *
 *     ×  Grund   ⌀ [18] @ [150] mm   [B500B]
 *
 * Die Einheit ist zugleich der Umschalter: «mm» heisst Teilung, «Stk»
 * Stabzahl -- das Trennzeichen wechselt mit (`@` bzw. `×`). Ein eigener Knopf
 * dafür kostete jede Zeile eine Spalte. `ende` steht ganz rechts: bei der
 * Grundbewehrung der Stahl, bei der Zulage die Lage der Stäbe zueinander.
 *
 * Das × vorne setzt den Durchmesser auf null und nimmt den Posten damit heraus.
 * Es ist nur rot, solange es etwas zu entfernen gibt; bei leerem Posten bleibt
 * es blass, statt ganz zu verschwinden -- sonst rutschte die Zeile bei jeder
 * Eingabe um seine Breite.
 */
function postenZeile(querschnitt, nummer, welcher, beschriftung, ende = null) {
  const posten = querschnitt.lagen[nummer - 1][welcher];
  const ueberAbstand = posten.abstand !== null && posten.abstand !== undefined;
  const leer = !(posten.durchmesser > 0);

  const aendern = (veraenderer) => projektAendern((p) => {
    veraenderer(p.querschnitte.find((x) => x.kennung === querschnitt.kennung)
      .lagen[nummer - 1][welcher]);
  });

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
      wert: posten.durchmesser || null, stufen: zustand.katalog.durchmesser, min: 0,
      titel: '⌀ in mm; leer oder 0: keine Bewehrung',
      leer: 0,
      beiAenderung: (v) => aendern((x) => { x.durchmesser = v; }),
    }),
    el('span.zeichen', { text: ueberAbstand ? '@' : '×' }),
    ueberAbstand
      ? zahlfeld({
        wert: posten.abstand, schritt: 25, min: 25, titel: 'Teilung in mm',
        beiAenderung: (v) => aendern((x) => { x.abstand = v; }),
      })
      : zahlfeld({
        wert: posten.anzahl, schritt: 1, min: 1, titel: 'Stabzahl je b',
        beiAenderung: (v) => aendern((x) => { x.anzahl = v; }),
      }),
    einheitsSchalter(ueberAbstand, 'je b', () => aendern((x) => {
      if (ueberAbstand) { x.anzahl = x.anzahl || 5; x.abstand = null; }
      else { x.abstand = x.abstand || 150; x.anzahl = null; }
    })),
    ende || el('span'),
  ]);
}

/**
 * Die Einheit hinter einer Teilung, die zugleich umschaltet: «mm» ist eine
 * Teilung, «Stk» eine Stabzahl.
 */
function einheitsSchalter(ueberAbstand, bezug, umschalten) {
  return el('button.einheit-knopf', {
    text: ueberAbstand ? 'mm' : 'Stk',
    title: ueberAbstand
      ? `Teilung in mm – klicken für Stabzahl ${bezug}`
      : `Stabzahl ${bezug} – klicken für Teilung in mm`,
    on: { click: umschalten },
  });
}

function lagenBlock(querschnitt, nummer) {
  const lage = querschnitt.lagen[nummer - 1];
  const staehle = zustand.projekt.materialien.filter((m) => m.art === 'betonstahl');
  const richtung = richtungVon(querschnitt, nummer);
  const partner = partnerVon(nummer);
  const leer = !(lage.grund.durchmesser > 0 || lage.zulage.durchmesser > 0);

  // Zwei Zeilen je Lage, Grund und Zulage. Was die Lage selbst angeht, steht
  // am Rand: links Nummer und Richtung, rechts der Stahl und die Lage der
  // Stäbe zueinander.
  return el('div.lage', { class: `lage-${richtung} ${leer ? 'ist-leer' : ''}` }, [
    el('div.lage-kopf', {}, [
      el('span.lage-name', { text: `${nummer}. Lage` }),
      richtungsSchalter(querschnitt, nummer, richtung, partner),
    ]),
    // Gewählt wird der Stahl nur an der x-Lage; die y-Lage derselben Seite
    // bekommt ihn mit. Nachgewiesen wird nur x -- eine eigene Wahl in y
    // stünde da, ohne dass ein Nachweis nach ihr fragt, und eine verborgene
    // könnte unbemerkt vom Rest abweichen.
    postenZeile(querschnitt, nummer, 'grund', 'Grund', richtung === 'x' ? el('select.stahlwahl', {
      title: 'Betonstahl dieser Seite – x- und y-Lage',
      on: {
        change: (e) => projektAendern((p) => {
          const q = p.querschnitte.find((x) => x.kennung === querschnitt.kennung);
          q.lagen[nummer - 1].stahl = e.target.value;
          q.lagen[partner - 1].stahl = e.target.value;
        }),
      },
    }, staehle.map((s) => el('option', {
      value: s.kennung, text: s.name || s.sorte, selected: lage.stahl === s.kennung,
    }))) : null),
    postenZeile(querschnitt, nummer, 'zulage', 'Zulage', lageSchalter(querschnitt, nummer, lage)),
  ]);
}

/**
 * Die Lage von Grundbewehrung und Zulage zueinander: ein Knopf, der zeigt,
 * was gilt, und umschaltet. Als Paar «ungünstig | günstig» war er breiter
 * als die Zahlen der Zeile.
 *
 * Nur sichtbar, wenn die Lage überhaupt zwei Posten hat -- bei einer einzelnen
 * Bewehrung gibt es nichts zueinander zu legen.
 */
function lageSchalter(querschnitt, nummer, lage) {
  if (!(lage.grund?.durchmesser > 0 && lage.zulage?.durchmesser > 0)) return null;

  const setzen = (unguenstig) => projektAendern((p) => {
    p.querschnitte.find((x) => x.kennung === querschnitt.kennung)
      .lagen[nummer - 1].unguenstig = unguenstig;
  });
  const ist = lage.unguenstig !== false;
  const untere = nummer <= 2;

  return el('button.gunst-knopf', {
    text: ist ? 'ungünstig' : 'günstig',
    class: ist ? '' : 'ist-guenstig',
    title: (untere
      ? 'Ungünstig: gleiche Oberkante, der dünnere Stab rückt nach oben. '
        + 'Günstig: gleiche Unterkante, jeder um seinen Halbmesser eingerückt.'
      : 'Ungünstig: gleiche Unterkante, der dünnere Stab rückt nach unten. '
        + 'Günstig: gleiche Oberkante, jeder um seinen Halbmesser eingerückt.')
      + ' Klicken schaltet um.',
    on: { click: () => setzen(!ist) },
  });
}

/** Zweistellungs-Schalter x|y. Die Partnerlage folgt zwingend der Gegenrichtung. */
function richtungsSchalter(querschnitt, nummer, richtung, partner) {
  // Beide Schalter eines Paars zeigen dasselbe Paar, nur von der anderen
  // Seite -- wie gespeichert wird, weiss lagen.js.
  const setzen = (wert) => projektAendern((p) => {
    richtungSetzen(p.querschnitte.find((x) => x.kennung === querschnitt.kennung),
      nummer, wert);
  });

  return zweiSchalter({
    stellungen: [['x', 'x', 'ist-x'], ['y', 'y', 'ist-y']], gewaehlt: richtung, setzen,
    titel: `Tragrichtung der ${nummer}. Lage – die ${partner}. bekommt die Gegenrichtung. `
      + 'Klicken schaltet um.',
  });
}


/**
 * Die Bügel -- ein Raster über die ganze Platte, unterhalb der Lagen, und
 * gebaut wie eine Lage: zwei Zeilen, links der Name, rechts der Stahl.
 *
 *     Bügel  ×  x  ⌀ [10] @ [200] mm    [B500B]
 *                y         @ [200] mm
 *
 * Die Neigung der Druckdiagonalen und k_c stehen im Fenster der
 * Tragsicherheit: sie gehören zur Rechnung, nicht zur Bewehrung.
 *
 * In y darf statt der Teilung eine Stabzahl über die betrachtete Breite
 * stehen, in x nicht: der Widerstand gilt je Laufmeter, und eine Stabzahl
 * hätte darin keinen Bezug. Wer sie angibt, bekommt nur noch Nachweise in
 * x-Richtung -- der Nachweis sagt es dann selbst.
 */
function querkraftBlock(querschnitt) {
  const staehle = zustand.projekt.materialien.filter((m) => m.art === 'betonstahl');
  // Vollständig: jede Platte kommt durch den Kern, und der setzt die Bügel
  // mit allen Feldern. Bügel ohne Stahl meldet der Kern beim Rechnen.
  const buegel = querschnitt.querkraftbewehrung;
  const ueberAbstand = buegel.abstand_y !== null && buegel.abstand_y !== undefined;
  const leer = !(buegel.durchmesser > 0);

  const aendern = (veraenderer) => projektAendern((p) => {
    veraenderer(p.querschnitte.find((x) => x.kennung === querschnitt.kennung)
      .querkraftbewehrung);
  });

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
        wert: buegel.durchmesser || null, stufen: zustand.katalog.durchmesser, min: 0,
        titel: 'Bügel-⌀ in mm; leer oder 0: keine Bügel',
        leer: 0,
        beiAenderung: (v) => aendern((x) => { x.durchmesser = v; }),
      }),
      el('span.zeichen', { text: '@' }),
      zahlfeld({
        wert: buegel.abstand_x, schritt: 25, min: 25,
        titel: 'Bügelteilung x in mm',
        beiAenderung: (v) => aendern((x) => { x.abstand_x = v; }),
      }),
      el('span.einheit', { text: 'mm' }),
      el('select.stahlwahl', {
        title: 'Betonstahl der Bügel',
        on: {
          change: (e) => aendern((x) => { x.stahl = e.target.value; }),
        },
      }, staehle.map((s) => el('option', {
        value: s.kennung, text: s.name || s.sorte, selected: buegel.stahl === s.kennung,
      }))),
    ]),
    el('div.postenzeile', { class: leer ? 'ist-leer' : '' }, [
      el('span'),
      el('span.postenname', { text: 'y' }),
      el('span'),
      el('span'),
      el('span.zeichen', { text: ueberAbstand ? '@' : '×' }),
      ueberAbstand
        ? zahlfeld({
          wert: buegel.abstand_y, schritt: 25, min: 25,
          titel: 'Bügelteilung y in mm',
          beiAenderung: (v) => aendern((x) => { x.abstand_y = v; }),
        })
        : zahlfeld({
          wert: buegel.anzahl_y, schritt: 1, min: 1,
          titel: 'Bügelzahl je b; dann nur Nachweise in x',
          beiAenderung: (v) => aendern((x) => { x.anzahl_y = v; }),
        }),
      einheitsSchalter(ueberAbstand, 'je b – dann nur Nachweise in x', () => aendern((x) => {
        if (ueberAbstand) { x.anzahl_y = x.anzahl_y || 5; x.abstand_y = null; }
        else { x.abstand_y = x.abstand_y || 200; x.anzahl_y = null; }
      })),
      el('span'),
    ]),
  ]);
}

function ueberdeckungsBlock(querschnitt, welche) {
  const unten = welche === 'unten';
  const aendern = (v) => projektAendern((p) => {
    const q = p.querschnitte.find((x) => x.kennung === querschnitt.kennung);
    if (unten) q.ueberdeckung_unten = v;
    else q.ueberdeckung_oben = v;
  });
  return el('div.ueberdeckung', {}, [
    feld(`Überdeckung ${welche}`, zahlfeld({
      wert: unten ? querschnitt.ueberdeckung_unten : querschnitt.ueberdeckung_oben,
      schritt: 5, min: 0, beiAenderung: aendern,
    }), 'mm'),
  ]);
}



// ===========================================================================
// Die Kapitel der Platte -- je ein Knopf, die Eingaben im Fenster (kapitel.js)
// ===========================================================================

/** Worauf sich die Eingaben beziehen, unter dem Titel des Fensters. */
const mitQuerkraft = (q) => `${jeB(q)} · V je m`;

const NACHWEISE = [
  {
    schluessel: 'tragsicherheit',
    name: 'Trag\u00adsicherheit', titel: 'Tragsicherheitsnachweise', bezug: mitQuerkraft,
    inhalt: tragsicherheitInhalt,
    stand: (q) => {
      const n = eingeschaltet(q.kombinationen);
      return { an: n > 0, text: n ? anzahl(n, 'Einwirkung', 'Einwirkungen') : 'keine Einwirkung' };
    },
  },
  {
    schluessel: 'knicken',
    name: 'Knicken', titel: 'Knicken', bezug: jeB,
    inhalt: knickInhalt,
    stand: (q) => {
      const n = eingeschaltet(q.knickfaelle);
      return { an: n > 0, text: n ? anzahl(n, 'Fall', 'Fälle') : 'kein Fall' };
    },
  },
  {
    schluessel: 'duktilitaet',
    name: 'Duktilität', titel: 'Duktilitätsnachweis',
    inhalt: duktilitaetInhalt,
    stand: (q) => schalter(!!q.duktilitaet),
  },
  {
    schluessel: 'sproede',
    name: 'Sprödes Versagen', titel: 'Nachweis gegen sprödes Versagen',
    inhalt: sproedeInhalt,
    stand: (q) => schalter(!!q.sproede),
  },
  {
    schluessel: 'zwang',
    name: 'Riss bei Zwang', titel: 'Rissbreitenbegrenzung bei Zwang',
    inhalt: zwangInhalt,
    // Die Begrenzung auf 500 mm ist kein eigener Nachweis, sie ändert die
    // beiden anderen.
    stand: (q) => {
      const teile = [q.zwaengung ? 'N' : null, q.zwaengung_biegung ? 'M' : null].filter(Boolean);
      return { an: teile.length > 0, text: teile.length ? `auf ${teile.join(' und ')}` : 'aus' };
    },
  },
  {
    schluessel: 'quasistaendig',
    name: 'Stahlspannung quasi-ständig',
    titel: 'Stahlspannungsbegrenzung bei quasi-ständigen Lastfällen', bezug: jeB,
    inhalt: quasistaendigInhalt,
    stand: (q) => gebrauchsstand(q.quasistaendig),
  },
  {
    schluessel: 'haeufig',
    name: 'Fliessen häufig', titel: 'Verhindern des Fliessens für häufige Lastfälle',
    bezug: jeB,
    inhalt: haeufigInhalt,
    stand: (q) => (fliessenGefordert(q) ? gebrauchsstand(q.haeufig)
      : { an: false, text: 'entfällt' }),
  },
  {
    schluessel: 'verformung',
    name: 'Verformung', titel: 'Begrenzung der Durchbiegung',
    bezug: () => 'w in mm · L in m · nur x',
    inhalt: verformungInhalt,
    stand: (q) => {
      const n = eingeschaltet(q.verformung?.faelle);
      return { an: n > 0, text: n ? anzahl(n, 'Fall', 'Fälle') : 'kein Fall' };
    },
  },
];

const SUCHE = {
  schluessel: 'automatik',
  name: 'Bewehrung suchen', titel: 'Automatische Bewehrung',
  inhalt: automatikInhalt,
  stand: (q) => (sucheLaeuft(q.kennung) ? { an: true, text: 'sucht …' }
    : { an: false, text: q.automatik_dicke ? 'mit Dicke' : '' }),
};

function plattenKapitel() {
  return [
    { titel: 'Nachweise', kapitel: NACHWEISE },
    { titel: 'Spannung-Dehnung-Analysen', kapitel: analysenKapitel({ inhalt: analyseInhalt, bezug: jeB }) },
    { titel: 'Werkzeug', kapitel: [SUCHE] },
  ];
}

function plattenEditor(querschnitt) {
  const betone = zustand.projekt.materialien.filter((m) => m.art === 'beton');
  const aendern = (veraenderer) => projektAendern((p) => {
    veraenderer(p.querschnitte.find((x) => x.kennung === querschnitt.kennung));
  });

  return [
    panel({ schluessel: 'platte/Platte', titel: 'Platte' }, [
      // Eine Karte mit blauer Kante wie die Lagen und die Nachweiskapitel:
      // ohne sie stand die Platte als einzige blosse Feldliste da.
      el('div.unterkapitel', {}, [
        feld('Bezeichnung', el('input', {
          type: 'text', value: querschnitt.name,
          on: { change: (e) => aendern((q) => { q.name = e.target.value; }) },
        })),
        feld('Beton', auswahl({
          werte: betone.map((b) => ({ wert: b.kennung, beschriftung: b.name || b.sorte })),
          gewaehlt: querschnitt.beton,
          beiAenderung: (v) => aendern((q) => { q.beton = v; }),
        })),
        feld('Dicke h', zahlfeld({
          wert: querschnitt.h, schritt: 10, min: 10,
          beiAenderung: (v) => aendern((q) => { q.h = v; }),
        }), 'mm'),
        feld(['Breite ', span('b_x')], zahlfeld({
          wert: querschnitt.b, schritt: 100, min: 10,
          titel: 'Streifen in x: A_s, M und N je b. y: je 1000 mm',
          beiAenderung: (v) => aendern((q) => { q.b = v; }),
        }), 'mm'),
        // Grösstkorn, k_c und Einlagenhöhe stehen im Fenster der
        // Tragsicherheit: nur die Querkraft braucht sie. Die Kriechzahl des
        // Vergrösserungsfaktors steht im Fenster der Verformung.
        // Freier Text, der in keine Rechnung eingeht. Ohne ein solches Feld
        // landen solche Sätze im Namen der Platte.
        el('div.beschreibung', {}, [
          el('label', { text: 'Beschreibung' }),
          el('textarea', {
            rows: 3, value: querschnitt.beschreibung || '',
            on: {
              change: (e) => aendern((q) => { q.beschreibung = e.target.value; }),
            },
          }),
        ]),
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
    // Eingaben im Fenster.
    kapitelPanel(querschnitt, plattenKapitel(),
      { schluessel: 'platte/Kapitel', titel: 'Nachweise und Analysen' }),
  ];
}

// ===========================================================================

/** Das Fenster eines Kapitels, je Bauteilart -- das Balkensystem hat keine. */
const FENSTER = {
  querschnitt: (q, schluessel) => kapitelFenster(q, plattenKapitel(), schluessel, hilfe),
  querschnittsanalyse: analyseFenster,
};

/**
 * Zeichnet die mittlere Tafel: den Editor des gewählten Bestandteils und,
 * wenn eines offen ist, sein Fenster darüber.
 */
export function editorZeichnen(behaelter, titelKnoten, hinweisKnoten, fensterGrund) {
  const bauteil = gewaehltesBauteil();
  fensterZeigen(fensterGrund, bauteil && zustand.fenster
    ? FENSTER[bauteil.art.art]?.(bauteil.eintrag, zustand.fenster) : null);

  const material = gewaehltesMaterial();
  if (material) {
    titelKnoten.textContent = material.name || material.sorte;
    hinweisKnoten.textContent = `${ART_TEXT[material.art] || ''}`
      + (material.eigenstaendig ? ' · eigenes Material' : ' · Normsorte SIA');
    return ersetzen(behaelter, ...materialEditor(material));
  }
  if (bauteil) {
    titelKnoten.textContent = bauteil.eintrag.name;
    hinweisKnoten.textContent = bauteil.art.bezeichnung;
    return ersetzen(behaelter, ...EDITOREN[bauteil.art.art](bauteil.eintrag));
  }
  const skript = gewaehltesSkript();
  if (skript) {
    titelKnoten.textContent = skript.name;
    hinweisKnoten.textContent = 'Python';
    return skriptZeichnen(behaelter, skript);
  }
  titelKnoten.textContent = 'Eingaben';
  hinweisKnoten.textContent = '';
  return ersetzen(behaelter, el('div.leer', {}, [
    el('p', { text: 'Links Bestandteil wählen.' }),
    el('p', { text: 'Neu: + über der Liste links.' }),
  ]));
}




