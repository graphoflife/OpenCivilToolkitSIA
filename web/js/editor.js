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
import { span } from './mathe.js';
import {
  gewaehltesMaterial, gewaehlterQuerschnitt, kennwertId, projektAendern, zustand,
} from './zustand.js';

const ART_TEXT = { beton: 'Beton', betonstahl: 'Betonstahl' };

function gerechnet(id) {
  return zustand.loesung?.werte?.[id] || null;
}

function feld(beschriftung, eingabe, einheit) {
  return el('div.feld', {}, [
    el('label', { text: beschriftung, title: beschriftung }),
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
 *     Grund   ⌀ [18] @ [150] mm   [Teilung|Anzahl]
 *
 * Der letzte Schalter legt fest, ob die mittlere Zahl eine Teilung oder eine
 * Stabzahl ist -- das Trennzeichen wechselt mit (`@` bzw. `×`).
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
    el('span.postenname', { text: beschriftung }),
    el('span.zeichen', { text: '⌀' }),
    zahlfeld({
      wert: posten.durchmesser || null, schritt: 2, min: 0,
      titel: 'Stabdurchmesser in mm – leer oder 0 bedeutet: keine Bewehrung',
      beiAenderung: (v) => aendern((x) => { x.durchmesser = v ?? 0; }),
    }),
    el('span.zeichen', { text: ueberAbstand ? '@' : '×' }),
    ueberAbstand
      ? zahlfeld({
        wert: posten.abstand, schritt: 25, min: 1, titel: 'Teilung in mm',
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
 * Der Massstab fehlt bewusst: der Kern rechnet beide und nimmt den
 * ungünstigeren -- welcher das war, steht beim Nachweis.
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
        feld('Grösstkorn D_max', zahlfeld({
          wert: querschnitt.d_max, schritt: 4, min: 1,
          titel: 'Geht in den Querkraftwiderstand ein',
          beiAenderung: (v) => aendern((q) => { q.d_max = v ?? 32; }),
        }), 'mm'),
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
      ]),
    ]),

    el('div.feldgruppe', {}, [
      el('h3', { text: 'Nachweise' }),
      el('div.unterkapitel', {}, [
        el('div.unterkapitel-kopf', {}, [
          el('span', { text: 'Einwirkungen' }),
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
        el('p', {
          text: 'V_Ed = 0 bedeutet: kein Querkraftnachweis. Der Massstab für den '
              + 'Erfüllungsgrad wird selbst gewählt – gerechnet werden beide, '
              + 'gezeigt der ungünstigere.',
          style: { fontSize: '11.5px', color: 'var(--schrift-zart)', margin: '6px 0 0' },
        }),
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
