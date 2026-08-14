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

function postenBlock(querschnitt, nummer, welcher, beschriftung) {
  const lage = querschnitt.lagen[nummer - 1];
  const posten = lage[welcher];
  const ueberAbstand = posten.abstand !== null && posten.abstand !== undefined;

  const aendern = (veraenderer) => projektAendern((p) => {
    veraenderer(p.querschnitte.find((x) => x.kennung === querschnitt.kennung)
      .lagen[nummer - 1][welcher]);
  });

  return el('div.posten', {}, [
    el('div.posten-titel', { text: beschriftung }),
    el('div.posten-reihe', {}, [
      feld('⌀', zahlfeld({
        wert: posten.durchmesser, schritt: 2, min: 0,
        titel: '0 = nicht vorhanden',
        beiAenderung: (v) => aendern((x) => { x.durchmesser = v ?? 0; }),
      }), 'mm'),
      ueberAbstand
        ? feld('Teilung s', zahlfeld({
          wert: posten.abstand, schritt: 25, min: 1,
          beiAenderung: (v) => aendern((x) => { x.abstand = v ?? 150; }),
        }), 'mm')
        : feld('Anzahl n', zahlfeld({
          wert: posten.anzahl, schritt: 1, min: 1,
          beiAenderung: (v) => aendern((x) => { x.anzahl = v ?? 1; }),
        }), 'Stk'),
    ]),
    feld('Angabe über', auswahl({
      werte: [{ wert: 'abstand', beschriftung: 'Teilung' },
        { wert: 'anzahl', beschriftung: 'Stabzahl' }],
      gewaehlt: ueberAbstand ? 'abstand' : 'anzahl',
      beiAenderung: (v) => aendern((x) => {
        if (v === 'abstand') { x.abstand = x.abstand || 150; x.anzahl = null; }
        else { x.anzahl = x.anzahl || 5; x.abstand = null; }
      }),
    })),
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
        ? el('select', {
          style: { width: 'auto', padding: '1px 6px', fontSize: '11px' },
          title: `Die ${partner}. Lage bekommt zwingend die Gegenrichtung`,
          on: {
            change: (e) => projektAendern((p) => {
              const q = p.querschnitte.find((x) => x.kennung === querschnitt.kennung);
              if (nummer === 1) q.richtung_lage1 = e.target.value;
              else q.richtung_lage4 = e.target.value;
            }),
          },
        }, [
          el('option', { value: 'x', text: 'x-Richtung', selected: richtung === 'x' }),
          el('option', { value: 'y', text: 'y-Richtung', selected: richtung === 'y' }),
        ])
        : el('span.richtung', { text: `${richtung}-Richtung` }),
      waehlbar ? null : el('span.fest', { text: `folgt aus der ${partner}. Lage` }),
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
    postenBlock(querschnitt, nummer, 'grund', 'Grundbewehrung'),
    postenBlock(querschnitt, nummer, 'zulage', 'Zulage'),
  ]);
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

function kombinationZeile(querschnitt, index) {
  const k = querschnitt.kombinationen[index];
  const aendern = (veraenderer) => projektAendern((p) => {
    veraenderer(p.querschnitte.find((x) => x.kennung === querschnitt.kennung).kombinationen[index]);
  });

  return el('div.kombination', {}, [
    el('div.lage-kopf', {}, [
      el('input', {
        type: 'text', value: k.name,
        style: { border: 'none', background: 'transparent', fontWeight: '700', padding: '0' },
        on: { change: (e) => aendern((x) => { x.name = e.target.value; }) },
      }),
      el('button.knopf.knopf-zart.knopf-gefahr', {
        text: '×', title: 'Kombination entfernen',
        on: {
          click: () => projektAendern((p) => {
            p.querschnitte.find((x) => x.kennung === querschnitt.kennung)
              .kombinationen.splice(index, 1);
          }),
        },
      }),
    ]),
    el('div.posten-reihe', {}, [
      feld('M_Ed', zahlfeld({
        wert: k.M_Ed, schritt: 10,
        beiAenderung: (v) => aendern((x) => { x.M_Ed = v ?? 0; }),
      }), 'kNm'),
      feld('N_Ed', zahlfeld({
        wert: k.N_Ed, schritt: 10, titel: 'Zug positiv, Druck negativ',
        beiAenderung: (v) => aendern((x) => { x.N_Ed = v ?? 0; }),
      }), 'kN'),
    ]),
    feld('Massstab', auswahl({
      werte: zustand.katalog.erfuellungsarten.map((a) => ({ wert: a.wert, beschriftung: a.beschriftung })),
      gewaehlt: k.art,
      beiAenderung: (v) => aendern((x) => { x.art = v; }),
    })),
  ]);
}

function plattenEditor(querschnitt) {
  const betone = zustand.projekt.materialien.filter((m) => m.art === 'beton');
  const aendern = (veraenderer) => projektAendern((p) => {
    veraenderer(p.querschnitte.find((x) => x.kennung === querschnitt.kennung));
  });

  return [
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
    ]),

    el('div.feldgruppe', {}, [
      el('h3', {}, [el('span', { text: 'Bewehrung' }),
        el('span', { text: 'von unten nach oben' })]),
      // Die Maske ist gestapelt wie der Querschnitt: oben die 4. Lage,
      // unten die 1. -- so steht auf dem Bildschirm, was im Bauteil liegt.
      ueberdeckungsBlock(querschnitt, 'oben'),
      lagenBlock(querschnitt, 4),
      lagenBlock(querschnitt, 3),
      lagenBlock(querschnitt, 2),
      lagenBlock(querschnitt, 1),
      ueberdeckungsBlock(querschnitt, 'unten'),
    ]),

    el('div.feldgruppe', {}, [
      el('h3', {}, [
        el('span', { text: 'Schnittgrössen' }),
        el('button.knopf.knopf-zart', {
          text: '+ Kombination',
          on: {
            click: () => aendern((q) => q.kombinationen.push({
              name: `Kombination ${q.kombinationen.length + 1}`,
              M_Ed: 100, N_Ed: 0, art: 'N_konstant',
            })),
          },
        }),
      ]),
      el('p', {
        text: 'Jede Kombination wird in beiden Tragrichtungen geprüft, in denen '
            + 'Bewehrung liegt.',
        style: { fontSize: '12px', color: 'var(--schrift-zart)', margin: '0 0 8px' },
      }),
      ...(querschnitt.kombinationen.length
        ? querschnitt.kombinationen.map((_, i) => kombinationZeile(querschnitt, i))
        : [el('div.leer', { text: 'Ohne Schnittgrössen kein Nachweis.' })]),
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
