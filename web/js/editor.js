/**
 * editor.js -- Mittlere Tafel: Eingaben zum ausgewählten Bestandteil.
 *
 * ZWEI ARTEN VON KENNWERTEN:
 * Was aus der Sortentabelle oder als Normvorgabe kommt, ist unmittelbar
 * änderbar -- es landet in `abweichungen`. Was gerechnet wird, steht
 * schreibgeschützt da, bis man es ausdrücklich überschreibt; dann landet es in
 * `ueberschreibungen`, und der Rechenkern überspringt die zugehörige
 * Berechnung samt allem, was nur für sie gebraucht wurde.
 *
 * Angezeigt wird immer der Wert aus der letzten Lösung, nie ein in der
 * Oberfläche nachgerechneter. Solange noch nicht gerechnet wurde, steht dort
 * ein Strich -- lieber nichts als eine Zahl, für die niemand geradesteht.
 */

import { auswahl, el, ersetzen, leerzustand, zahlfeld } from './dom.js';
import { span } from './mathe.js';
import {
  gewaehltesMaterial, gewaehlterQuerschnitt, kennwertId, projektAendern, zustand,
} from './zustand.js';

const ART_TEXT = { beton: 'Beton', betonstahl: 'Betonstahl' };

/** Der gerechnete Wert zu einer Wert-ID, oder null. */
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
  const id = kennwertId(material, vorlage.kurzname);
  const wert = gerechnet(id);
  const istUeberschrieben = vorlage.kurzname in material.ueberschreibungen;
  const istAbweichend = vorlage.kurzname in material.abweichungen;

  // Anzuzeigende Zahl: was der Benutzer gesetzt hat, sonst das Rechenergebnis.
  let anzeige = null;
  if (istUeberschrieben) anzeige = material.ueberschreibungen[vorlage.kurzname];
  else if (istAbweichend) anzeige = material.abweichungen[vorlage.kurzname];
  else if (wert) anzeige = Number(wert.zahl.toFixed(vorlage.stellen));

  const schreibbar = !vorlage.berechnet || istUeberschrieben;

  const eingabe = zahlfeld({
    wert: anzeige,
    schritt: vorlage.stellen >= 3 ? 0.001 : (vorlage.stellen >= 1 ? 0.1 : 1),
    readonly: !schreibbar,
    titel: schreibbar ? '' : 'Wird gerechnet. Zum Ändern links überschreiben.',
    beiAenderung: (neu) => projektAendern((p) => {
      const m = p.materialien.find((x) => x.kennung === material.kennung);
      const topf = vorlage.berechnet ? m.ueberschreibungen : m.abweichungen;
      if (neu === null) delete topf[vorlage.kurzname];
      else topf[vorlage.kurzname] = neu;
    }),
  });

  // Nur gerechnete Kennwerte bekommen den Überschreiben-Schalter.
  const schalter = vorlage.berechnet
    ? el('input', {
      type: 'checkbox',
      checked: istUeberschrieben,
      title: 'Von Hand überschreiben',
      on: {
        change: (e) => projektAendern((p) => {
          const m = p.materialien.find((x) => x.kennung === material.kennung);
          if (e.target.checked) {
            m.ueberschreibungen[vorlage.kurzname] = anzeige ?? 0;
          } else {
            delete m.ueberschreibungen[vorlage.kurzname];
          }
        }),
      },
    })
    : el('span');

  const zuruecksetzen = (istAbweichend && !vorlage.berechnet)
    ? el('button.knopf.knopf-zart', {
      text: '↺',
      title: 'Auf den Sorten- bzw. Normwert zurücksetzen',
      on: {
        click: () => projektAendern((p) => {
          const m = p.materialien.find((x) => x.kennung === material.kennung);
          delete m.abweichungen[vorlage.kurzname];
        }),
      },
    })
    : el('span');

  return el('div.kennwert', {
    class: istUeberschrieben ? 'ist-ueberschrieben' : '',
    title: [vorlage.beschreibung, vorlage.referenz].filter(Boolean).join(' — '),
  }, [
    schalter,
    el('span.bezeichnung', {}, [
      span(vorlage.symbol),
      ' ',
      el('small', { text: vorlage.beschreibung }),
    ]),
    eingabe,
    el('span.einheit', { text: vorlage.einheit === '-' ? '' : vorlage.einheit }),
    zuruecksetzen,
  ]);
}

function materialEditor(material) {
  const sorten = material.art === 'beton'
    ? zustand.katalog.betonsorten
    : zustand.katalog.stahlsorten;
  const vorlagen = zustand.katalog.kennwerte[material.art] || [];

  const grundlagen = vorlagen.filter((v) => !v.berechnet);
  const abgeleitete = vorlagen.filter((v) => v.berechnet);

  const anzahlUeberschrieben = Object.keys(material.ueberschreibungen).length;

  return [
    el('div.feldgruppe', {}, [
      el('h3', { text: 'Material' }),
      feld('Bezeichnung', el('input', {
        type: 'text',
        value: material.name,
        on: {
          change: (e) => projektAendern((p) => {
            p.materialien.find((x) => x.kennung === material.kennung).name = e.target.value;
          }),
        },
      })),
      feld('Sorte', auswahl({
        werte: sorten.map((s) => ({ wert: s.sorte, beschriftung: s.sorte })),
        gewaehlt: material.sorte,
        beiAenderung: (neu) => projektAendern((p) => {
          const m = p.materialien.find((x) => x.kennung === material.kennung);
          m.sorte = neu;
          // Sortenabhängige Abweichungen verlieren mit der Sorte ihren Sinn.
          for (const v of vorlagen.filter((x) => x.aus_sorte)) delete m.abweichungen[v.kurzname];
        }),
      })),
    ]),

    el('div.feldgruppe', {}, [
      el('h3', {}, [
        el('span', { text: 'Grundwerte' }),
        el('span', {
          text: 'aus Sortentabelle und Norm',
          style: { fontWeight: '400', textTransform: 'none', letterSpacing: '0' },
        }),
      ]),
      ...grundlagen.map((v) => kennwertZeile(material, v)),
    ]),

    el('div.feldgruppe', {}, [
      el('h3', {}, [
        el('span', { text: 'Abgeleitete Kennwerte' }),
        anzahlUeberschrieben
          ? el('button.knopf.knopf-zart', {
            text: `${anzahlUeberschrieben} überschrieben — alle zurücksetzen`,
            on: {
              click: () => projektAendern((p) => {
                p.materialien.find((x) => x.kennung === material.kennung).ueberschreibungen = {};
              }),
            },
          })
          : el('span', {
            text: 'Haken setzen zum Überschreiben',
            style: { fontWeight: '400', textTransform: 'none', letterSpacing: '0' },
          }),
      ]),
      ...abgeleitete.map((v) => kennwertZeile(material, v)),
    ]),
  ];
}

// ===========================================================================
// Querschnitt
// ===========================================================================

function lageZeile(querschnitt, seite, index) {
  const liste = seite === 'unten' ? querschnitt.lagen_unten : querschnitt.lagen_oben;
  const lage = liste[index];
  const staehle = zustand.projekt.materialien.filter((m) => m.art === 'betonstahl');

  const aendern = (veraenderer) => projektAendern((p) => {
    const q = p.querschnitte.find((x) => x.kennung === querschnitt.kennung);
    veraenderer((seite === 'unten' ? q.lagen_unten : q.lagen_oben)[index]);
  });

  const ueberAbstand = lage.abstand !== null && lage.abstand !== undefined;

  return el('div.lage', {}, [
    el('div.lage-kopf', {}, [
      el('span', { text: `${index + 1}. Lage ${seite}` }),
      el('div.reihe', {}, [
        index > 0 ? el('button.knopf.knopf-zart', {
          text: '↑', title: 'Weiter nach aussen',
          on: {
            click: () => projektAendern((p) => {
              const q = p.querschnitte.find((x) => x.kennung === querschnitt.kennung);
              const l = seite === 'unten' ? q.lagen_unten : q.lagen_oben;
              [l[index - 1], l[index]] = [l[index], l[index - 1]];
            }),
          },
        }) : null,
        el('button.knopf.knopf-zart.knopf-gefahr', {
          text: '×', title: 'Lage entfernen',
          on: {
            click: () => projektAendern((p) => {
              const q = p.querschnitte.find((x) => x.kennung === querschnitt.kennung);
              (seite === 'unten' ? q.lagen_unten : q.lagen_oben).splice(index, 1);
            }),
          },
        }),
      ]),
    ]),

    el('div.lage-reihe', {}, [
      feld('⌀', zahlfeld({
        wert: lage.durchmesser, schritt: 2, min: 1,
        beiAenderung: (v) => aendern((l) => { l.durchmesser = v ?? 1; }),
      }), 'mm'),
      feld('Stahl', auswahl({
        werte: staehle.map((s) => ({ wert: s.kennung, beschriftung: s.name || s.sorte })),
        gewaehlt: lage.stahl,
        beiAenderung: (v) => aendern((l) => { l.stahl = v; }),
      })),
    ]),

    el('div.lage-reihe', {}, [
      feld('Angabe', auswahl({
        werte: [
          { wert: 'abstand', beschriftung: 'Stababstand' },
          { wert: 'anzahl', beschriftung: 'Stabzahl' },
        ],
        gewaehlt: ueberAbstand ? 'abstand' : 'anzahl',
        beiAenderung: (v) => aendern((l) => {
          if (v === 'abstand') { l.abstand = l.abstand || 150; l.anzahl = null; }
          else { l.anzahl = l.anzahl || 5; l.abstand = null; }
        }),
      })),
      ueberAbstand
        ? feld('s', zahlfeld({
          wert: lage.abstand, schritt: 25, min: 1,
          beiAenderung: (v) => aendern((l) => { l.abstand = v ?? 150; }),
        }), 'mm')
        : feld('n', zahlfeld({
          wert: lage.anzahl, schritt: 1, min: 1,
          beiAenderung: (v) => aendern((l) => { l.anzahl = v ?? 1; }),
        }), 'Stk'),
    ]),

    feld('Lichter Abstand zur vorigen Lage', zahlfeld({
      wert: lage.lichter_abstand, schritt: 5, min: 0,
      beiAenderung: (v) => aendern((l) => { l.lichter_abstand = v ?? 0; }),
    }), 'mm'),
  ]);
}

function lagenGruppe(querschnitt, seite) {
  const liste = seite === 'unten' ? querschnitt.lagen_unten : querschnitt.lagen_oben;
  const staehle = zustand.projekt.materialien.filter((m) => m.art === 'betonstahl');

  return el('div.feldgruppe', {}, [
    el('h3', {}, [
      el('span', { text: `Bewehrung ${seite}` }),
      el('button.knopf.knopf-zart', {
        text: '+ Lage',
        disabled: !staehle.length,
        on: {
          click: () => projektAendern((p) => {
            const q = p.querschnitte.find((x) => x.kennung === querschnitt.kennung);
            (seite === 'unten' ? q.lagen_unten : q.lagen_oben).push({
              durchmesser: 12, stahl: staehle[0].kennung,
              abstand: 150, anzahl: null, lichter_abstand: 0,
            });
          }),
        },
      }),
    ]),
    ...(liste.length
      ? liste.map((_, i) => lageZeile(querschnitt, seite, i))
      : [el('div.leer', { text: 'keine Lage', style: { padding: '8px', textAlign: 'left' } })]),
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
        style: { border: 'none', background: 'transparent', fontWeight: '600', padding: '0' },
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
    el('div.lage-reihe', {}, [
      feld('M_Ed', zahlfeld({
        wert: k.M_Ed, schritt: 10,
        beiAenderung: (v) => aendern((x) => { x.M_Ed = v ?? 0; }),
      }), 'kNm'),
      feld('N_Ed', zahlfeld({
        wert: k.N_Ed, schritt: 10,
        titel: 'Zug positiv, Druck negativ',
        beiAenderung: (v) => aendern((x) => { x.N_Ed = v ?? 0; }),
      }), 'kN'),
    ]),
    feld('Massstab', auswahl({
      werte: zustand.katalog.erfuellungsarten.map((a) => ({
        wert: a.wert, beschriftung: a.beschriftung,
      })),
      gewaehlt: k.art,
      beiAenderung: (v) => aendern((x) => { x.art = v; }),
    })),
  ]);
}

function querschnittEditor(querschnitt) {
  const betone = zustand.projekt.materialien.filter((m) => m.art === 'beton');
  const aendern = (veraenderer) => projektAendern((p) => {
    veraenderer(p.querschnitte.find((x) => x.kennung === querschnitt.kennung));
  });

  return [
    el('div.feldgruppe', {}, [
      el('h3', { text: 'Querschnitt' }),
      feld('Bezeichnung', el('input', {
        type: 'text', value: querschnitt.name,
        on: { change: (e) => aendern((q) => { q.name = e.target.value; }) },
      })),
      feld('Beton', auswahl({
        werte: betone.map((b) => ({ wert: b.kennung, beschriftung: b.name || b.sorte })),
        gewaehlt: querschnitt.beton,
        beiAenderung: (v) => aendern((q) => { q.beton = v; }),
      })),
      feld('Höhe h', zahlfeld({
        wert: querschnitt.h, schritt: 10, min: 10,
        beiAenderung: (v) => aendern((q) => { q.h = v ?? 300; }),
      }), 'mm'),
      feld('Breite b', zahlfeld({
        wert: querschnitt.b, schritt: 100, min: 10,
        titel: 'Mit b = 1000 mm gelten alle Schnittgrössen pro Laufmeter.',
        beiAenderung: (v) => aendern((q) => { q.b = v ?? 1000; }),
      }), 'mm'),
      feld('Überdeckung unten', zahlfeld({
        wert: querschnitt.ueberdeckung_unten, schritt: 5, min: 0,
        beiAenderung: (v) => aendern((q) => { q.ueberdeckung_unten = v ?? 30; }),
      }), 'mm'),
      feld('Überdeckung oben', zahlfeld({
        wert: querschnitt.ueberdeckung_oben, schritt: 5, min: 0,
        beiAenderung: (v) => aendern((q) => { q.ueberdeckung_oben = v ?? 30; }),
      }), 'mm'),
    ]),

    lagenGruppe(querschnitt, 'unten'),
    lagenGruppe(querschnitt, 'oben'),

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
      ...(querschnitt.kombinationen.length
        ? querschnitt.kombinationen.map((_, i) => kombinationZeile(querschnitt, i))
        : [el('div.leer', {
          text: 'Ohne Schnittgrössen kein Nachweis.',
          style: { padding: '8px', textAlign: 'left' },
        })]),
    ]),
  ];
}

// ===========================================================================

export function editorZeichnen(behaelter, titelKnoten, hinweisKnoten) {
  const material = gewaehltesMaterial();
  const querschnitt = gewaehlterQuerschnitt();

  if (material) {
    titelKnoten.textContent = material.name || material.sorte;
    hinweisKnoten.textContent = ART_TEXT[material.art] || '';
    return ersetzen(behaelter, ...materialEditor(material));
  }
  if (querschnitt) {
    titelKnoten.textContent = querschnitt.name;
    hinweisKnoten.textContent = 'Plattenquerschnitt';
    return ersetzen(behaelter, ...querschnittEditor(querschnitt));
  }
  titelKnoten.textContent = 'Eingaben';
  hinweisKnoten.textContent = '';
  return ersetzen(behaelter, leerzustand(
    'Links einen Bestandteil auswählen.',
    'Oder mit "+ Beton" und "+ Stahl" ein neues Material anlegen.'));
}
