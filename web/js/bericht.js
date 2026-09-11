/**
 * bericht.js -- Rechte Tafel: das Rechenergebnis.
 *
 * Fünf Sichten auf dieselbe Lösung:
 *   Herleitung  die Mitschrift des Rechenkerns, Formel für Formel
 *   Nachweise   Urteile und Erfüllungsgrade
 *   Diagramm    die M-N-Interaktionslinie
 *   Werte       alle bestimmten Grössen mit ihrer Herkunft
 *   Ziel wählen einen Wert anfordern und zurückverfolgen, was dafür nötig ist
 *
 * Sämtliche Zahlen und Formeln stammen unverändert aus der Lösung. Die
 * Oberfläche formatiert nichts nach -- sonst stünde am Bildschirm etwas
 * anderes als im Bericht.
 */

import { el, ersetzen, leerzustand, melden } from './dom.js';
import { kopiereFuerWord, kopiereLatex, setzen, span } from './mathe.js';
import { diagrammZeichnen, kurveZeichnen, querschnittZeichnen } from './diagramm.js';
import { aendern, zustand } from './zustand.js';

// ===========================================================================
// Bausteine
// ===========================================================================

function werkzeugKnopf(text, titel, tun) {
  return el('button.knopf.knopf-zart', {
    text, title: titel,
    on: {
      click: async (e) => { e.stopPropagation(); await tun(); },
    },
  });
}

function gleichungBlock(block) {
  const hervorgehoben = block.wert_id && zustand.hervorgehoben.has(block.wert_id);
  const latex = block.latex;

  const huelle = el('div.gleichung', {
    class: hervorgehoben ? 'ist-hervorgehoben' : '',
    dataset: { wertId: block.wert_id || '' },
  }, [
    (block.titel || block.referenz)
      ? el('div.gleichung-kopf', {}, [
        block.titel ? el('span.gleichung-titel', { text: block.titel }) : null,
        block.referenz ? el('span.gleichung-ref', { text: block.referenz }) : null,
      ])
      : null,
    el('div.gleichung-mathe'),
    el('div.gleichung-werkzeug', {}, [
      werkzeugKnopf('Word', 'Als Formel für Word kopieren (MathML)', async () => {
        await kopiereFuerWord(latex);
        melden('Formel kopiert – in Word mit Strg+V einfügen.');
      }),
      werkzeugKnopf('TeX', 'LaTeX-Quelltext kopieren', async () => {
        await kopiereLatex(latex);
        melden('LaTeX kopiert.');
      }),
    ]),
  ]);

  setzen(latex, huelle.querySelector('.gleichung-mathe'));
  return huelle;
}

function tabellenBlock(block) {
  return el('div', {}, [
    block.titel ? el('div.tabelle-titel', { text: block.titel }) : null,
    el('div.tabelle-huelle', {}, [
      el('table.gitter', {}, [
        el('thead', {}, [
          el('tr', {}, block.kopf.map((zelle) => {
            const th = el('th');
            setzen(zelle, th, { displayMode: false });
            return th;
          })),
        ]),
        el('tbody', {}, block.zeilen.map((zeile) => el('tr', {}, zeile.map((zelle) => {
          const td = el('td');
          // Zellen können Symbole enthalten; reine Zahlen setzt KaTeX unverändert.
          setzen(zelle, td, { displayMode: false });
          return td;
        })))),
      ]),
    ]),
  ]);
}

function bloeckeZeichnen(bloecke) {
  const knoten = [];
  for (const block of bloecke) {
    if (block.art === 'titel') {
      knoten.push(el(`div.b-titel${block.ebene >= 3 ? '.b-titel-3' : ''}`, { text: block.text }));
    } else if (block.art === 'text') {
      knoten.push(el('p.b-text', { text: block.text }));
    } else if (block.art === 'gleichung') {
      knoten.push(gleichungBlock(block));
    } else if (block.art === 'tabelle') {
      knoten.push(tabellenBlock(block));
    } else if (block.art === 'hinweis') {
      knoten.push(el(`div.hinweis.hinweis-${block.hinweisart}`, {}, [
        el('b', { text: `${block.beschriftung}: ` }),
        block.text,
      ]));
    } else if (block.art === 'unterprotokoll') {
      knoten.push(el('div.b-titel.b-titel-3', { text: block.titel }));
      knoten.push(...bloeckeZeichnen(block.bloecke));
    }
  }
  return knoten;
}

function lueckenBanner(loesung) {
  if (!loesung.fehlende?.length) return null;
  return el('div', { class: 'abstand-oben' }, [
    el('div.b-titel', { text: 'Fehlende Eingaben' }),
    el('p.b-text', { text: 'Damit weitergerechnet werden kann, werden gebraucht:' }),
    ...loesung.fehlende.map((f) => el('div.luecke', {}, [
      el('div', {}, [
        el('b', { text: f.beschreibung }),
        f.einheit ? ` [${f.einheit}]` : '',
      ]),
      el('div', {}, [el('code', { text: f.id })]),
      f.pfad?.length
        ? el('div.pfad', { text: `benötigt für: ${f.pfad.join(' → ')}` })
        : null,
    ])),
  ]);
}

// ===========================================================================
// Sichten
// ===========================================================================

function herleitung(loesung) {
  if (!loesung.protokoll?.length) {
    return leerzustand('Noch nichts gerechnet.', 'Oben auf "Rechnen" klicken.');
  }
  const verfolgt = zustand.verfolgtesZiel;
  return el('div.blatt', {}, [
    verfolgt
      ? el('div.hinweis.hinweis-annahme', {}, [
        el('b', { text: 'Rückverfolgung: ' }),
        `Hervorgehoben ist, was für ${verfolgt} gebraucht wurde `
        + `(${loesung.reihenfolge.length} Rechenschritte). `,
        el('button.knopf.knopf-klein', {
          text: 'aufheben',
          on: {
            click: () => aendern(
              { verfolgtesZiel: null, hervorgehoben: new Set() }, 'hervorhebung'),
          },
        }),
      ])
      : null,
    ...(loesung.warnungen || []).map((w) => el('div.hinweis.hinweis-warnung', {}, [
      el('b', { text: 'Warnung: ' }), w,
    ])),
    ...bloeckeZeichnen(loesung.protokoll),
    lueckenBanner(loesung),
  ]);
}

function nachweise(loesung) {
  const alle = (loesung.urteile || []).filter(gehoertZurAuswahl);
  if (!alle.length) {
    return el('div.blatt', {}, [
      leerzustand('Keine Nachweise gerechnet.',
        'Einer Platte Einwirkungen zuweisen und "Rechnen" drücken.'),
      lueckenBanner(loesung),
    ]);
  }

  // Nach Platte gruppieren: jede Platte bekommt ihre eigene Tabelle.
  const nachPlatte = new Map();
  for (const u of alle) {
    const schluessel = plattenNameZu(u, loesung) || 'Sonstige';
    if (!nachPlatte.has(schluessel)) nachPlatte.set(schluessel, []);
    nachPlatte.get(schluessel).push(u);
  }

  const zelle = (u, seite) => {
    const w = u[seite];
    if (!w) return el('td.zahl', { text: '—' });
    const inhalt = el('td.zahl');
    inhalt.append(span(`${w.symbol} = `), `${w.wert} ${w.einheit}`);
    return inhalt;
  };

  return el('div', {}, [...nachPlatte.entries()].map(([platte, urteile]) =>
    el('div.blatt', {}, [
      el('div.b-titel', { text: `Nachweise – ${platte}` }),
      el('div.tabelle-huelle', {}, [
        el('table.nachweis-tabelle', {}, [
          el('thead', {}, [el('tr', {}, [
            el('th', { text: 'Nachweis' }),
            el('th', { text: 'Widerstand' }),
            el('th', { text: 'Einwirkung' }),
            el('th', {}, [span(String.raw`\alpha_{eff}`)]),
            el('th', { text: '' }),
          ])]),
          el('tbody', {}, urteile.map((u) => el('tr', {
            class: u.erfuellt ? 'ist-gut' : 'ist-schlecht',
            title: u.begruendung || '',
          }, [
            el('td', { text: u.name }),
            zelle(u, 'widerstand'),
            zelle(u, 'einwirkung'),
            el('td.zahl.grad', { text: u.erfuellungsgrad ?? '\u221e' }),
            el('td', {}, [el('span', {
              class: u.erfuellt ? 'marke-gut' : 'marke-schlecht',
              text: u.erfuellt ? 'erfüllt' : 'nicht erfüllt',
            })]),
          ]))),
        ]),
      ]),
    ])).concat([lueckenBanner(loesung)].filter(Boolean)));
}

/** Zu welcher Platte ein Urteil gehört -- über die Zuordnung der Lösung. */
function plattenNameZu(urteil, loesung) {
  const qs = loesung.zuordnung?.querschnitte || {};
  for (const eintrag of Object.values(qs)) {
    // Die Urteilsnamen tragen die Richtung, die Zuordnung den Plattennamen.
    if (Object.keys(eintrag.nachweise || {}).some((r) =>
      urteil.name.includes(` ${r} –`))) return eintrag.name;
  }
  return Object.values(qs)[0]?.name || '';
}

/** Filtert auf den links gewählten Bestandteil, wenn "Aktuelle Seite" aktiv ist. */
function gehoertZurAuswahl(urteil) {
  if (zustand.umfang !== 'seite') return true;
  const wahl = zustand.auswahl;
  if (!wahl) return true;
  if (wahl.art !== 'querschnitt') return false;   // Materialien haben keine Nachweise
  const name = zustand.projekt.querschnitte.find((q) => q.kennung === wahl.kennung)?.name;
  return !!name && (zustand.loesung?.zuordnung?.querschnitte?.[wahl.kennung]?.name === name);
}

function diagrammSicht(loesung) {
  const linien = loesung.linien || {};
  const querschnitte = loesung.zuordnung?.querschnitte || {};
  const gesetze = loesung.werkstoffgesetze || {};
  const blaetter = [];

  // -- Werkstoffgesetze ---------------------------------------------------
  for (const [kennung, gesetz] of Object.entries(gesetze)) {
    if (zustand.umfang === 'seite' && zustand.auswahl
        && !(zustand.auswahl.art === 'material' && zustand.auswahl.kennung === kennung)) {
      continue;
    }
    blaetter.push(el('div.blatt', {}, [
      el('div.b-titel', { text: `${gesetz.titel} – ${gesetz.name}` }),
      gesetz.referenz
        ? el('p.b-text', {
          text: gesetz.referenz,
          style: { fontSize: '12px', color: 'var(--schrift-zart)', margin: '0 0 6px' },
        })
        : null,
      kurveZeichnen(gesetz, {
        zeigeVereinfacht: zustand.zeigeVereinfacht,
        beiUmschalten: (an) => aendern({ zeigeVereinfacht: an }, 'diagramm'),
      }),
    ]));
  }

  // -- Querschnitt und Interaktionslinien ---------------------------------
  for (const [kennung, eintrag] of Object.entries(querschnitte)) {
    if (zustand.umfang === 'seite' && zustand.auswahl
        && !(zustand.auswahl.art === 'querschnitt' && zustand.auswahl.kennung === kennung)) {
      continue;
    }
    const eigene = Object.entries(linien)
      .filter(([schluessel]) => schluessel.split('.')[0] === kennung);
    blaetter.push(el('div.blatt', {}, [
      el('div.b-titel', { text: `Querschnitt – ${eintrag.name}` }),
      querschnittZeichnen(eintrag, loesung.werte || {}),
      ...eigene.flatMap(([, linie]) => [
        el('div.b-titel', {
          text: `M-N-Interaktionsdiagramm – ${eintrag.name}, ${linie.richtung}-Richtung`,
        }),
        diagrammZeichnen(linie),
      ]),
    ]));
  }

  if (!blaetter.length) return leerzustand('Noch nichts zu zeichnen.');
  return el('div', {}, blaetter);
}

function werteSicht(loesung, beiZielwahl) {
  let eintraege = Object.values(loesung.werte || {});
  if (!eintraege.length) return leerzustand('Noch keine Werte bestimmt.');
  if (zustand.umfang === 'seite' && zustand.auswahl) {
    const raum = raumDerAuswahl();
    if (raum) eintraege = eintraege.filter((w) => w.id.startsWith(`${raum}.`));
  }
  eintraege.sort((a, b) => a.id.localeCompare(b.id, 'de'));

  // Nur Werte, die aus einer Berechnung stammen, taugen als Ziel -- eine
  // Eingabe zurückzuverfolgen hätte keinen Inhalt.
  const waehlbar = eintraege.filter((w) => w.quelle === 'berechnet');
  const gewaehlt = zustand.gewaehlteZiele;
  const setzeAuswahl = (ids) => aendern({ gewaehlteZiele: new Set(ids) }, 'zielauswahl');
  const umschalten = (id) => {
    const neu = new Set(gewaehlt);
    if (neu.has(id)) neu.delete(id); else neu.add(id);
    setzeAuswahl(neu);
  };

  const leiste = el('div.ziel-leiste', {}, [
    el('input', {
      type: 'checkbox',
      checked: gewaehlt.size > 0 && gewaehlt.size === waehlbar.length,
      indeterminate: gewaehlt.size > 0 && gewaehlt.size < waehlbar.length,
      title: 'Alle berechneten Werte an- oder abwählen',
      on: { change: (e) => setzeAuswahl(e.target.checked ? waehlbar.map((w) => w.id) : []) },
    }),
    el('span', {}, [
      el('span.anzahl', { text: String(gewaehlt.size) }),
      ` von ${waehlbar.length} berechneten Werten als Ziel gewählt`,
    ]),
    el('span', { style: { marginLeft: 'auto' } }),
    el('button.knopf.knopf-haupt', {
      text: 'Gewählte zurückverfolgen',
      disabled: gewaehlt.size === 0,
      on: { click: () => beiZielwahl([...gewaehlt]) },
    }),
    el('button.knopf', {
      text: 'Alles rechnen',
      on: { click: () => beiZielwahl(null) },
    }),
  ]);

  const kette = zustand.verfolgtesZiel && loesung?.ketten?.[zustand.verfolgtesZiel];

  return el('div.blatt', {}, [
    el('div.b-titel', { text: `Werte (${eintraege.length})` }),
    el('p.b-text', {
      text: 'Berechnete Werte lassen sich anhaken und zurückverfolgen: der Kern '
          + 'löst rückwärts auf und rechnet nur, was dafür nötig ist.',
    }),
    leiste,
    kette
      ? el('div.hinweis.hinweis-annahme', {}, [
        el('div', {}, [el('b', { text: `Für ${zustand.verfolgtesZiel} nötig:` })]),
        el('div', { text: `${kette.berechnungen.length} Rechenschritte, ${kette.werte.length} Werte` }),
        el('ol.kettenliste', {}, kette.berechnungen.map((b) => el('li', { text: b }))),
      ])
      : null,
    el('div.tabelle-huelle', {}, [
      el('table.werteliste', {}, [
        el('thead', {}, [el('tr', {}, [
          el('th', { text: '' }),
          el('th', { text: 'Bezeichnung' }),
          el('th', { text: 'Symbol' }),
          el('th', { text: 'Wert', style: { textAlign: 'right' } }),
          el('th', { text: 'Einheit' }),
          el('th', { text: 'Herkunft' }),
        ])]),
        el('tbody', {}, eintraege.map((w) => {
          const symbol = el('td');
          setzen(w.symbol, symbol, { displayMode: false });
          const istWaehlbar = w.quelle === 'berechnet';
          return el('tr', {
            class: [
              zustand.hervorgehoben.has(w.id) ? 'ist-hervorgehoben' : '',
              gewaehlt.has(w.id) ? 'ist-gewaehlt' : '',
            ].join(' '),
            title: w.referenz || '',
          }, [
            el('td', {}, [istWaehlbar
              ? el('input', {
                type: 'checkbox', checked: gewaehlt.has(w.id),
                title: 'Als Rechenziel wählen',
                on: { change: () => umschalten(w.id) },
              })
              : el('span', { text: '', title: 'Eingabe – nicht zurückverfolgbar' })]),
            el('td', {}, [
              el('div', { text: w.beschreibung || w.kurzname }),
              el('div.kennung', { text: w.id }),
            ]),
            symbol,
            el('td.zahl', { text: w.wert }),
            el('td', { text: w.einheit }),
            el('td', {}, [el('span', {
              class: `quelle-marke quelle-${w.quelle}`, text: w.quelle_text,
            })]),
          ]);
        })),
      ]),
    ]),
  ]);
}

/** Namensraum des links gewählten Bestandteils, für den Seitenfilter. */
function raumDerAuswahl() {
  const wahl = zustand.auswahl;
  if (!wahl) return null;
  if (wahl.art === 'material') {
    const m = zustand.projekt.materialien.find((x) => x.kennung === wahl.kennung);
    return m ? `${m.art}.${m.kennung}` : null;
  }
  return `querschnitt.${wahl.kennung}`;
}

// ===========================================================================

export function berichtZeichnen(behaelter, beiZielwahl) {
  const loesung = zustand.loesung;

  if (!loesung) {
    return ersetzen(behaelter, leerzustand(
      'Noch nichts gerechnet.',
      'Oben auf "Rechnen" klicken.'));
  }

  const sichten = {
    nachweise: () => nachweise(loesung),
    diagramm: () => diagrammSicht(loesung),
    herleitung: () => herleitung(loesung),
    werte: () => werteSicht(loesung, beiZielwahl),
  };
  return ersetzen(behaelter, (sichten[zustand.reiter] || sichten.nachweise)());
}
