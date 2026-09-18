/**
 * editor.js -- Mittlere Tafel: Eingaben zum ausgewählten Bestandteil.
 *
 * NORMSORTE ODER EIGENES MATERIAL:
 * Eine unveränderte Normsorte ist gesperrt -- kein Feld lässt sich anfassen.
 * Wer abweichen will, drückt „Material modifizieren"; das Material bekommt
 * dann einen eigenen Namen (C30/37_1) und wird änderbar. So kann keine
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

import { auswahl, el, ersetzen, melden, zahlfeld } from './dom.js';

/**
 * Lieferbare Stabdurchmesser in mm.
 *
 * Oberhalb von 22 mm wird die Reihe grober -- deshalb eine Liste und kein
 * gleichmässiger Schritt.
 */
const DURCHMESSER = [6, 8, 10, 12, 14, 16, 18, 20, 22, 26, 30, 34, 40];
import { span } from './mathe.js';
import {
  gewaehltesMaterial, gewaehlterQuerschnitt, kennwertId, projektAendern, zustand,
} from './zustand.js';

const ART_TEXT = { beton: 'Beton', betonstahl: 'Betonstahl' };

function gerechnet(id) {
  return zustand.loesung?.werte?.[id] || null;
}

/**
 * Eine Zeile Beschriftung – Eingabe – Einheit.
 *
 * `beschriftung` ist entweder Klartext oder eine Liste von Knoten. Letzteres
 * für Symbole, die tiefgestellte Teile haben: `D_max` als blosser Text gelesen
 * hiesse, den Index zu unterschlagen.
 */
function feld(beschriftung, eingabe, einheit, titel) {
  const istText = typeof beschriftung === 'string';
  return el('div.feld', {}, [
    istText
      ? el('label', { text: beschriftung, title: titel || beschriftung })
      : el('label', { title: titel || '' }, beschriftung),
    eingabe,
    el('span.einheit', { text: einheit || '' }),
  ]);
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
    titel: gesperrt ? 'Normsorte – erst modifizieren, dann änderbar'
      : (vorlage.berechnet && !istUeberschrieben ? 'Wird gerechnet. Haken setzen zum Überschreiben.' : ''),
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
      title: gesperrt ? 'Normsorte – erst modifizieren' : 'Von Hand überschreiben',
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
      text: '↺', title: 'Auf den Sorten- bzw. Normwert zurücksetzen',
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
  const sorten = material.art === 'beton'
    ? zustand.katalog.betonsorten : zustand.katalog.stahlsorten;
  const vorlagen = zustand.katalog.kennwerte[material.art] || [];
  const gesperrt = !material.eigenstaendig;
  const anzahlUeberschrieben = Object.keys(material.ueberschreibungen).length;

  const kopf = gesperrt
    ? el('div.gesperrt-hinweis', {}, [
      el('div', { style: { flex: '1 1 220px' } }, [
        el('b', { text: `Normsorte ${material.sorte}` }),
        'Sämtliche Kennwerte stammen aus der Norm und sind gesperrt. Nur so darf '
        + 'diese Bezeichnung im Bericht stehen.',
      ]),
      el('button.knopf', {
        text: 'Material modifizieren',
        title: 'Macht daraus ein eigenständiges Material mit eigenem Namen',
        on: { click: () => materialLoesen(material) },
      }),
    ])
    : el('div.gesperrt-hinweis', {
      style: { background: 'var(--warn-hell)', borderColor: 'var(--warn)' },
    }, [
      el('div', { style: { flex: '1 1 220px' } }, [
        el('b', { text: 'Eigenständiges Material' }),
        `Abgeleitet von ${material.sorte}. Die Kennwerte sind änderbar und `
        + 'entsprechen nicht mehr zwingend der Norm.',
      ]),
    ]);

  return [
    kopf,
    el('div.feldgruppe', {}, [
      el('h3', { text: 'Material' }),
      feld('Bezeichnung', el('input', {
        type: 'text', value: material.name, disabled: gesperrt,
        title: gesperrt ? 'Eine Normsorte trägt zwingend ihre Sortenbezeichnung' : '',
        on: { change: (e) => nameAendern(material, e.target.value, e.target) },
      })),
      feld('Sorte', auswahl({
        werte: sorten.map((s) => ({ wert: s.sorte, beschriftung: s.sorte })),
        gewaehlt: material.sorte,
        beiAenderung: (neu) => sorteAendern(material, neu, vorlagen),
      })),
    ]),

    el('div.feldgruppe', {}, [
      el('h3', {}, [el('span', { text: 'Grundwerte' }),
        el('span', { text: 'aus Sortentabelle und Norm' })]),
      ...vorlagen.filter((v) => !v.berechnet).map((v) => kennwertZeile(material, v)),
    ]),

    el('div.feldgruppe', {}, [
      el('h3', {}, [
        el('span', { text: 'Abgeleitete Kennwerte' }),
        anzahlUeberschrieben
          ? el('button.knopf.knopf-zart', {
            text: `${anzahlUeberschrieben} überschrieben — zurücksetzen`,
            on: {
              click: () => projektAendern((p) => {
                p.materialien.find((x) => x.kennung === material.kennung).ueberschreibungen = {};
              }),
            },
          })
          : el('span', { text: gesperrt ? 'gesperrt' : 'Haken setzen zum Überschreiben' }),
      ]),
      ...vorlagen.filter((v) => v.berechnet).map((v) => kennwertZeile(material, v)),
    ]),
  ];
}

/** Macht aus einer Normsorte ein eigenständiges Material mit eigenem Namen. */
function materialLoesen(material) {
  const vergeben = new Set(zustand.projekt.materialien
    .filter((m) => m.kennung !== material.kennung).map((m) => m.name || m.sorte));
  // Hochzählen an der Sorte, nicht am schon abgeleiteten Namen -- sonst
  // entstünde bei Belegung C30/37_1_1 statt C30/37_2.
  let i = 1;
  while (vergeben.has(`${material.sorte}_${i}`)) i += 1;
  const name = `${material.sorte}_${i}`;

  projektAendern((p) => {
    const m = p.materialien.find((x) => x.kennung === material.kennung);
    m.eigenstaendig = true;
    m.name = name;
  });
  melden(`Material ist jetzt eigenständig und heisst „${name}".`);
}

function nameAendern(material, wunsch, feldKnoten) {
  const name = wunsch.trim();
  const vergeben = zustand.projekt.materialien
    .some((m) => m.kennung !== material.kennung && (m.name || m.sorte) === name);
  if (!name || vergeben) {
    melden(vergeben
      ? `Der Name „${name}" ist schon vergeben. Materialnamen müssen eindeutig sein.`
      : 'Der Name darf nicht leer sein.', true);
    feldKnoten.value = material.name;
    return;
  }
  projektAendern((p) => {
    p.materialien.find((x) => x.kennung === material.kennung).name = name;
  });
}

function sorteAendern(material, neu, vorlagen) {
  // Bei einer Normsorte wandert der Name mit -- er *ist* die Sorte.
  if (!material.eigenstaendig) {
    const vergeben = zustand.projekt.materialien
      .some((m) => m.kennung !== material.kennung && (m.name || m.sorte) === neu);
    if (vergeben) {
      melden(`Die Normsorte „${neu}" ist bereits angelegt.`, true);
      return;
    }
  }
  projektAendern((p) => {
    const m = p.materialien.find((x) => x.kennung === material.kennung);
    m.sorte = neu;
    if (!m.eigenstaendig) m.name = neu;
    for (const v of vorlagen.filter((x) => x.aus_sorte)) delete m.abweichungen[v.kurzname];
  });
}

// ===========================================================================
// Platte
// ===========================================================================

/**
 * Ein Bewehrungsposten auf einer Zeile:
 *
 *     ×  Grund   ⌀ [18] @ [150] mm   [Teilung|Anzahl]
 *
 * Der letzte Schalter legt fest, ob die mittlere Zahl eine Teilung oder eine
 * Stabzahl ist -- das Trennzeichen wechselt mit (`@` bzw. `×`).
 *
 * Das × vorne setzt den Durchmesser auf null und nimmt den Posten damit heraus.
 * Es ist nur rot, solange es etwas zu entfernen gibt; bei leerem Posten bleibt
 * es blass, statt ganz zu verschwinden -- sonst rutschte die Zeile bei jeder
 * Eingabe um seine Breite.
 */
function postenZeile(querschnitt, nummer, welcher, beschriftung) {
  const posten = querschnitt.lagen[nummer - 1][welcher];
  const ueberAbstand = posten.abstand !== null && posten.abstand !== undefined;
  const leer = !(posten.durchmesser > 0);

  const aendern = (veraenderer) => projektAendern((p) => {
    veraenderer(p.querschnitte.find((x) => x.kennung === querschnitt.kennung)
      .lagen[nummer - 1][welcher]);
  });

  return el('div.postenzeile', { class: leer ? 'ist-leer' : '' }, [
    el('button.postenweg', {
      text: '×',
      class: leer ? '' : 'ist-scharf',
      disabled: leer,
      title: `${beschriftung}bewehrung der ${nummer}. Lage entfernen`,
      on: { click: () => aendern((x) => { x.durchmesser = 0; }) },
    }),
    el('span.postenname', { text: beschriftung }),
    el('span.zeichen', { text: '⌀' }),
    zahlfeld({
      wert: posten.durchmesser || null, stufen: DURCHMESSER, min: 0,
      titel: 'Stabdurchmesser in mm – leer oder 0 bedeutet: keine Bewehrung',
      beiAenderung: (v) => aendern((x) => { x.durchmesser = v ?? 0; }),
    }),
    el('span.zeichen', { text: ueberAbstand ? '@' : '×' }),
    ueberAbstand
      ? zahlfeld({
        wert: posten.abstand, schritt: 25, min: 25, titel: 'Teilung in mm',
        beiAenderung: (v) => aendern((x) => { x.abstand = v ?? 150; }),
      })
      : zahlfeld({
        wert: posten.anzahl, schritt: 1, min: 1, titel: 'Stabzahl auf der Breite b',
        beiAenderung: (v) => aendern((x) => { x.anzahl = v ?? 1; }),
      }),
    el('span.einheit', { text: ueberAbstand ? 'mm' : 'Stk' }),
    el('button.knopf.knopf-zart.umschalter', {
      text: ueberAbstand ? 'Teilung' : 'Anzahl',
      title: 'Zwischen Teilung und Stabzahl wechseln',
      on: {
        click: () => aendern((x) => {
          if (ueberAbstand) { x.anzahl = x.anzahl || 5; x.abstand = null; }
          else { x.abstand = x.abstand || 150; x.anzahl = null; }
        }),
      },
    }),
  ]);
}

function lagenBlock(querschnitt, nummer) {
  const lage = querschnitt.lagen[nummer - 1];
  const staehle = zustand.projekt.materialien.filter((m) => m.art === 'betonstahl');
  const waehlbar = nummer === 1 || nummer === 4;
  const richtung = richtungVon(querschnitt, nummer);
  const partner = { 1: 2, 2: 1, 3: 4, 4: 3 }[nummer];
  const leer = !(lage.grund.durchmesser > 0 || lage.zulage.durchmesser > 0);

  return el('div.lage', { class: `lage-${richtung} ${leer ? 'ist-leer' : ''}` }, [
    el('div.lage-kopf', {}, [
      el('span', { text: `${nummer}. Lage` }),
      waehlbar
        ? richtungsSchalter(querschnitt, nummer, richtung, partner)
        : el('span.richtung', {
          text: richtung,
          title: `Gegenrichtung zur ${partner}. Lage – dort einstellbar`,
        }),
      el('span', { style: { marginLeft: 'auto' } }),
      // Links vom Stahl: die Lage der Stäbe zueinander gehört zur Geometrie
      // der Lage, nicht zum Werkstoff.
      lageSchalter(querschnitt, nummer, lage),
      el('select', {
        style: { width: 'auto', padding: '1px 6px', fontSize: '11px' },
        title: 'Betonstahl dieser Lage',
        on: {
          change: (e) => projektAendern((p) => {
            p.querschnitte.find((x) => x.kennung === querschnitt.kennung)
              .lagen[nummer - 1].stahl = e.target.value;
          }),
        },
      }, staehle.map((s) => el('option', {
        value: s.kennung, text: s.name || s.sorte, selected: lage.stahl === s.kennung,
      }))),
    ]),
    postenZeile(querschnitt, nummer, 'grund', 'Grund'),
    postenZeile(querschnitt, nummer, 'zulage', 'Zulage'),
  ]);
}

/**
 * Zweistellungs-Schalter für die Lage von Grundbewehrung und Zulage zueinander.
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

  return el('span.schalter.schalter-gunst', {
    title: untere
      ? 'Ungünstig: gleiche Oberkante, der dünnere Stab rückt nach oben. '
        + 'Günstig: gleiche Unterkante, jeder um seinen Halbmesser eingerückt.'
      : 'Ungünstig: gleiche Unterkante, der dünnere Stab rückt nach unten. '
        + 'Günstig: gleiche Oberkante, jeder um seinen Halbmesser eingerückt.',
  }, [
    el('button.schalter-halb', {
      text: 'ungünstig',
      class: ist ? 'ist-an' : '',
      on: { click: () => { if (!ist) setzen(true); } },
    }),
    el('button.schalter-halb', {
      text: 'günstig',
      class: ist ? '' : 'ist-an',
      on: { click: () => { if (ist) setzen(false); } },
    }),
  ]);
}

/** Zweistellungs-Schalter x|y. Die Partnerlage folgt zwingend der Gegenrichtung. */
function richtungsSchalter(querschnitt, nummer, richtung, partner) {
  const setzen = (wert) => projektAendern((p) => {
    const q = p.querschnitte.find((x) => x.kennung === querschnitt.kennung);
    if (nummer === 1) q.richtung_lage1 = wert;
    else q.richtung_lage4 = wert;
  });

  return el('span.schalter', {
    title: `Tragrichtung der ${nummer}. Lage – die ${partner}. bekommt die Gegenrichtung`,
  }, ['x', 'y'].map((wert) => el('button.schalter-halb', {
    text: wert,
    class: richtung === wert ? 'ist-an' : '',
    on: { click: () => { if (richtung !== wert) setzen(wert); } },
  })));
}

function richtungVon(querschnitt, nummer) {
  const gegen = (r) => (r === 'x' ? 'y' : 'x');
  return {
    1: querschnitt.richtung_lage1,
    2: gegen(querschnitt.richtung_lage1),
    3: gegen(querschnitt.richtung_lage4),
    4: querschnitt.richtung_lage4,
  }[nummer];
}

/**
 * Die Bügel einer Platte, mit allen Feldern belegt.
 *
 * Eine Beschreibung aus der Zeit vor der Querkraftbewehrung hat das Feld
 * nicht; der Kern setzt dann seine Vorgaben ein. Stünde in der Maske derweil
 * ein leeres Feld, rechnete das Werkzeug mit einer Zahl, die nirgends steht --
 * dieselbe Falle wie damals bei `h = 0`. Darum wird hier gefüllt, und zwar
 * mit denselben Werten, die der Kern einsetzen würde.
 */
function buegelVon(querschnitt, staehle) {
  const vorhanden = querschnitt.querkraftbewehrung || {};
  const gesetzt = (wert, vorgabe) => (wert === undefined ? vorgabe : wert);
  return {
    durchmesser: gesetzt(vorhanden.durchmesser, 0),
    stahl: vorhanden.stahl || staehle[0]?.kennung || '',
    abstand_x: gesetzt(vorhanden.abstand_x, 200),
    // Genau eines von abstand_y und anzahl_y ist gesetzt. Fehlen beide, gilt
    // die Teilung -- wie bei den Lagen.
    abstand_y: (vorhanden.abstand_y === undefined && vorhanden.anzahl_y == null)
      ? 200 : gesetzt(vorhanden.abstand_y, null),
    anzahl_y: gesetzt(vorhanden.anzahl_y, null),
    alpha_min: gesetzt(vorhanden.alpha_min, 30),
    alpha_max: gesetzt(vorhanden.alpha_max, 45),
  };
}

/**
 * Die Bügel -- ein Raster über die ganze Platte, unterhalb der Lagen.
 *
 *     ×  ⌀ [10]   x: [200]   y: [200] mm [Teilung|Anzahl]
 *     Neigung  α_min [30]°   α_max [45]°
 *
 * Die Namensspalte fehlt: über der Zeile steht «Querkraftbewehrung», und die
 * zusätzliche Teilung braucht den Platz.
 *
 * In y darf statt der Teilung eine Stabzahl über die betrachtete Breite
 * stehen, in x nicht: der Widerstand gilt je Laufmeter, und eine Stabzahl
 * hätte darin keinen Bezug. Wer sie angibt, bekommt nur noch Nachweise in
 * x-Richtung -- der Nachweis sagt es dann selbst.
 */
function querkraftBlock(querschnitt) {
  const staehle = zustand.projekt.materialien.filter((m) => m.art === 'betonstahl');
  const buegel = buegelVon(querschnitt, staehle);
  const ueberAbstand = buegel.abstand_y !== null && buegel.abstand_y !== undefined;
  const leer = !(buegel.durchmesser > 0);

  const aendern = (veraenderer) => projektAendern((p) => {
    const q = p.querschnitte.find((x) => x.kennung === querschnitt.kennung);
    // Erst vervollständigen, dann ändern: eine Beschreibung aus der Zeit vor
    // den Bügeln hat das Feld gar nicht, und ein leeres Eingabefeld neben
    // einer Rechnung mit stiller Vorgabe ist genau der Widerspruch, den
    // niemand sieht.
    q.querkraftbewehrung = buegelVon(q, staehle);
    veraenderer(q.querkraftbewehrung);
  });

  return el('div.lage.lage-querkraft', { class: leer ? 'ist-leer' : '' }, [
    el('div.lage-kopf', {}, [
      el('span', { text: 'Querkraftbewehrung' }),
      el('span', { style: { marginLeft: 'auto' } }),
      el('select', {
        style: { width: 'auto', padding: '1px 6px', fontSize: '11px' },
        title: 'Betonstahl der Bügel',
        on: {
          change: (e) => aendern((x) => { x.stahl = e.target.value; }),
        },
      }, staehle.map((s) => el('option', {
        value: s.kennung, text: s.name || s.sorte, selected: buegel.stahl === s.kennung,
      }))),
    ]),

    el('div.postenzeile.postenzeile-quer', { class: leer ? 'ist-leer' : '' }, [
      el('button.postenweg', {
        text: '×',
        class: leer ? '' : 'ist-scharf',
        disabled: leer,
        title: 'Querkraftbewehrung entfernen',
        on: { click: () => aendern((x) => { x.durchmesser = 0; }) },
      }),
      el('span.zeichen', { text: '⌀' }),
      zahlfeld({
        wert: buegel.durchmesser || null, stufen: DURCHMESSER, min: 0,
        titel: 'Bügeldurchmesser in mm – leer oder 0 bedeutet: keine Querkraftbewehrung',
        beiAenderung: (v) => aendern((x) => { x.durchmesser = v ?? 0; }),
      }),
      el('span.zeichen', { text: 'x:' }),
      zahlfeld({
        wert: buegel.abstand_x, schritt: 25, min: 25,
        titel: 'Bügelteilung in x-Richtung, in mm',
        beiAenderung: (v) => aendern((x) => { x.abstand_x = v ?? 200; }),
      }),
      el('span.zeichen', { text: 'y:' }),
      ueberAbstand
        ? zahlfeld({
          wert: buegel.abstand_y, schritt: 25, min: 25,
          titel: 'Bügelteilung in y-Richtung, in mm',
          beiAenderung: (v) => aendern((x) => { x.abstand_y = v ?? 200; }),
        })
        : zahlfeld({
          wert: buegel.anzahl_y, schritt: 1, min: 1,
          titel: 'Bügelzahl über die Breite b – dann sind nur Nachweise in '
               + 'x-Richtung möglich',
          beiAenderung: (v) => aendern((x) => { x.anzahl_y = v ?? 1; }),
        }),
      el('span.einheit', { text: ueberAbstand ? 'mm' : 'Stk' }),
      el('button.knopf.knopf-zart.umschalter', {
        text: ueberAbstand ? 'Teilung' : 'Anzahl',
        title: 'In y-Richtung zwischen Teilung und Stabzahl wechseln. Eine '
             + 'Stabzahl lässt nur Nachweise in x-Richtung zu.',
        on: {
          click: () => aendern((x) => {
            if (ueberAbstand) { x.anzahl_y = x.anzahl_y || 5; x.abstand_y = null; }
            else { x.abstand_y = x.abstand_y || 200; x.anzahl_y = null; }
          }),
        },
      }),
    ]),

    el('div.neigungszeile', {}, [
      el('span.postenname', { text: 'Neigung' }),
      span(String.raw`\alpha_{min}`),
      zahlfeld({
        wert: buegel.alpha_min, schritt: 1, min: 1, max: 89,
        titel: 'Kleinste Neigung der Druckdiagonalen in Grad (ganzzahlig)',
        beiAenderung: (v) => aendern((x) => { x.alpha_min = Math.round(v ?? 30); }),
      }),
      el('span.einheit', { text: '°' }),
      span(String.raw`\alpha_{max}`),
      zahlfeld({
        wert: buegel.alpha_max, schritt: 1, min: 1, max: 89,
        titel: 'Grösste Neigung der Druckdiagonalen in Grad (ganzzahlig)',
        beiAenderung: (v) => aendern((x) => { x.alpha_max = Math.round(v ?? 45); }),
      }),
      el('span.einheit', { text: '°' }),
    ]),
  ]);
}

function ueberdeckungsBlock(querschnitt, welche) {
  const unten = welche === 'unten';
  const aendern = (v) => projektAendern((p) => {
    const q = p.querschnitte.find((x) => x.kennung === querschnitt.kennung);
    if (unten) q.ueberdeckung_unten = v ?? 30;
    else q.ueberdeckung_oben = v ?? 30;
  });
  return el('div.ueberdeckung', {}, [
    feld(`Überdeckung ${welche}`, zahlfeld({
      wert: unten ? querschnitt.ueberdeckung_unten : querschnitt.ueberdeckung_oben,
      schritt: 5, min: 0, beiAenderung: aendern,
    }), 'mm'),
  ]);
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
function einwirkungZeile(querschnitt, index) {
  const k = querschnitt.kombinationen[index];
  const aendern = (veraenderer) => projektAendern((p) => {
    veraenderer(p.querschnitte.find((x) => x.kennung === querschnitt.kennung).kombinationen[index]);
  });

  const zahl = (feld, titel, schritt = 10) => zahlfeld({
    wert: k[feld], schritt, titel,
    beiAenderung: (v) => aendern((x) => { x[feld] = v ?? 0; }),
  });

  return el('div.einwirkung', {}, [
    el('input.ew-name', {
      type: 'text', value: k.name, title: 'Bezeichnung der Einwirkung',
      on: { change: (e) => aendern((x) => { x.name = e.target.value; }) },
    }),
    zahl('M_Ed', 'Bemessungsmoment in kNm'),
    zahl('N_Ed', 'Normalkraft in kN – Zug positiv, Druck negativ'),
    zahl('V_Ed', 'Querkraft in kN/m – 0 heisst: kein Querkraftnachweis'),
    el('select.ew-richtung', {
      title: 'In welcher Tragrichtung nachgewiesen wird',
      on: { change: (e) => aendern((x) => { x.richtung = e.target.value; }) },
    }, (zustand.katalog.richtungen || []).map((r) => el('option', {
      value: r.wert, text: r.wert, title: r.beschriftung,
      selected: (k.richtung || 'beide') === r.wert,
    }))),
    el('button.knopf.knopf-zart.knopf-gefahr', {
      text: '×', title: 'Einwirkung entfernen',
      on: {
        click: () => projektAendern((p) => {
          p.querschnitte.find((x) => x.kennung === querschnitt.kennung)
            .kombinationen.splice(index, 1);
        }),
      },
    }),
  ]);
}

function plattenEditor(querschnitt) {
  const betone = zustand.projekt.materialien.filter((m) => m.art === 'beton');
  const aendern = (veraenderer) => projektAendern((p) => {
    veraenderer(p.querschnitte.find((x) => x.kennung === querschnitt.kennung));
  });

  return [
    // Platte und Bewehrung stehen nebeneinander -- beides gehört zur Geometrie
    // und wird beim Bemessen gemeinsam gelesen.
    el('div.zweispaltig', {}, [
      el('div.feldgruppe', {}, [
        el('h3', { text: 'Platte' }),
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
          beiAenderung: (v) => aendern((q) => { q.h = v ?? 300; }),
        }), 'mm'),
        feld('Breite b', zahlfeld({
          wert: querschnitt.b, schritt: 100, min: 10,
          titel: 'Mit b = 1000 mm gelten alle Schnittgrössen pro Laufmeter.',
          beiAenderung: (v) => aendern((q) => { q.b = v ?? 1000; }),
        }), 'mm'),
        feld(['Grösstkorn ', span('D_{max}')], zahlfeld({
          wert: querschnitt.d_max, schritt: 4, min: 1,
          titel: 'Geht in den Querkraftwiderstand ein',
          beiAenderung: (v) => aendern((q) => { q.d_max = v ?? 32; }),
        }), 'mm', 'Grösstkorndurchmesser – geht in den Querkraftwiderstand ein'),
        feld(['Druckdiagonale ', span('k_c')], zahlfeld({
          wert: querschnitt.k_c ?? 0.55, schritt: 0.05, min: 0,
          titel: 'Abminderung der Betondruckfestigkeit in der Druckdiagonalen – '
               + 'geht nur mit Querkraftbewehrung ein',
          beiAenderung: (v) => aendern((q) => { q.k_c = v ?? 0.55; }),
        }), '', 'Abminderung der Betondruckfestigkeit in der Druckdiagonalen'),
        feld('Einlagenhöhe', zahlfeld({
          wert: querschnitt.einlagenhoehe, schritt: 5, min: 0,
          titel: 'Verringert d_v, sofern h/6 < e < d',
          beiAenderung: (v) => aendern((q) => { q.einlagenhoehe = v ?? 0; }),
        }), 'mm'),
      ]),

      el('div.feldgruppe', {}, [
        el('h3', {}, [el('span', { text: 'Bewehrung' }),
          el('span', { text: 'von unten nach oben' })]),
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
    ]),

    el('div.feldgruppe', {}, [
      el('h3', { text: 'Nachweise' }),
      el('div.unterkapitel', {}, [
        el('div.unterkapitel-kopf', {}, [
          el('span', { text: 'Tragsicherheitsnachweise' }),
          el('button.knopf.knopf-zart', {
            text: '+ Einwirkung',
            on: {
              click: () => aendern((q) => q.kombinationen.push({
                name: `Fall ${q.kombinationen.length + 1}`,
                M_Ed: 100, N_Ed: 0, V_Ed: 0,
                art: 'automatisch', richtung: 'x',
              })),
            },
          }),
        ]),
        querschnitt.kombinationen.length
          ? el('div.einwirkung.ist-kopf', {}, [
            el('span', { text: 'Bezeichnung' }),
            el('span', { text: 'M_Ed [kNm]' }),
            el('span', { text: 'N_Ed [kN]' }),
            el('span', { text: 'V_Ed [kN/m]' }),
            el('span', { text: 'Ri.' }),
            el('span'),
          ])
          : null,
        ...(querschnitt.kombinationen.length
          ? querschnitt.kombinationen.map((_, i) => einwirkungZeile(querschnitt, i))
          : [el('div.leer', { text: 'Ohne Einwirkung kein Nachweis.' })]),
      ]),
    ]),
  ];
}
// ===========================================================================

export function editorZeichnen(behaelter, titelKnoten, hinweisKnoten) {
  const material = gewaehltesMaterial();
  const querschnitt = gewaehlterQuerschnitt();

  if (material) {
    titelKnoten.textContent = material.name || material.sorte;
    hinweisKnoten.textContent = `${ART_TEXT[material.art] || ''}`
      + (material.eigenstaendig ? ' · eigenständig' : ' · Normsorte');
    return ersetzen(behaelter, ...materialEditor(material));
  }
  if (querschnitt) {
    titelKnoten.textContent = querschnitt.name;
    hinweisKnoten.textContent = 'Stahlbeton-Platte';
    return ersetzen(behaelter, ...plattenEditor(querschnitt));
  }
  titelKnoten.textContent = 'Eingaben';
  hinweisKnoten.textContent = '';
  return ersetzen(behaelter, el('div.leer', {}, [
    el('p', { text: 'Links einen Bestandteil auswählen.' }),
    el('p', { text: 'Materialien und Platten legst du über das + im Kapitelkopf an.' }),
  ]));
}
