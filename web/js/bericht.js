/**
 * bericht.js -- Rechte Tafel: das Rechenergebnis.
 *
 * Fünf Sichten auf dieselbe Lösung:
 *   Herleitung  die Mitschrift des Rechenkerns, Formel für Formel
 *   Nachweise   Urteile und Ausnutzungsgrade
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
import { diagrammZeichnen, querschnittZeichnen } from './diagramm.js';
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
  if (!loesung.urteile?.length) {
    return el('div.blatt', {}, [
      leerzustand('Keine Nachweise gerechnet.',
        'Einer Platte Schnittgrössen zuweisen und "Rechnen" drücken.'),
      lueckenBanner(loesung),
    ]);
  }

  const zelle = (u, seite) => {
    const w = u[seite];
    if (!w) return el('td.zahl', { text: '—' });
    const inhalt = el('td.zahl');
    inhalt.append(span(`${w.symbol} = `), `${w.wert} ${w.einheit}`);
    return inhalt;
  };

  return el('div.blatt', {}, [
    el('div.b-titel', { text: 'Nachweise' }),
    el('div.tabelle-huelle', {}, [
      el('table.nachweis-tabelle', {}, [
        el('thead', {}, [el('tr', {}, [
          el('th', { text: 'Nachweis' }),
          el('th', { text: 'Widerstand' }),
          el('th', { text: 'Einwirkung' }),
          el('th', { text: 'Erfüllungsgrad' }),
          el('th', { text: '' }),
        ])]),
        el('tbody', {}, loesung.urteile.map((u) => el('tr', {
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
    el('p.b-text', {
      text: loesung.alle_nachweise_erfuellt
        ? 'Sämtliche Nachweise sind erfüllt.'
        : 'Mindestens ein Nachweis ist nicht erfüllt.',
    }),
    lueckenBanner(loesung),
  ]);
}


function diagrammSicht(loesung) {
  const linien = loesung.linien || {};
  const querschnitte = loesung.zuordnung?.querschnitte || {};
  const kennungen = Object.keys(querschnitte);
  if (!kennungen.length) return leerzustand('Noch keine Platte gerechnet.');

  return el('div', {}, kennungen.map((kennung) => {
    const eintrag = querschnitte[kennung];
    const eigene = Object.entries(linien)
      .filter(([schluessel]) => schluessel.split('.')[0] === kennung);

    return el('div.blatt', {}, [
      el('div.b-titel', { text: `Querschnitt – ${eintrag.name}` }),
      querschnittZeichnen(eintrag, loesung.werte || {}),
      ...eigene.flatMap(([schluessel, linie]) => [
        el('div.b-titel', {
          text: `M-N-Interaktionsdiagramm – ${linie.richtung}-Richtung`,
        }),
        diagrammZeichnen(linie),
      ]),
    ]);
  }));
}


function werteSicht(loesung) {
  const eintraege = Object.values(loesung.werte || {});
  if (!eintraege.length) return leerzustand('Noch keine Werte bestimmt.');
  eintraege.sort((a, b) => a.id.localeCompare(b.id, 'de'));

  return el('div.blatt', {}, [
    el('div.b-titel', { text: `Werte (${eintraege.length})` }),
    el('div.tabelle-huelle', {}, [
      el('table.werteliste', {}, [
        el('thead', {}, [
          el('tr', {}, [
            el('th', { text: 'Bezeichnung' }),
            el('th', { text: 'Symbol' }),
            el('th', { text: 'Wert', style: { textAlign: 'right' } }),
            el('th', { text: 'Einheit' }),
            el('th', { text: 'Herkunft' }),
          ]),
        ]),
        el('tbody', {}, eintraege.map((w) => {
          const symbol = el('td');
          setzen(w.symbol, symbol, { displayMode: false });
          return el('tr', {
            class: zustand.hervorgehoben.has(w.id) ? 'ist-hervorgehoben' : '',
            title: w.referenz || '',
          }, [
            el('td', {}, [
              el('div', { text: w.beschreibung || w.kurzname }),
              el('div.kennung', { text: w.id }),
            ]),
            symbol,
            el('td.zahl', { text: w.wert }),
            el('td', { text: w.einheit }),
            el('td', {}, [
              el('span', {
                class: `quelle-marke quelle-${w.quelle}`,
                text: w.quelle_text,
              }),
            ]),
          ]);
        })),
      ]),
    ]),
  ]);
}

function zieleSicht(loesung, beiZielwahl) {
  const liste = zustand.zieleListe;
  if (!liste) return leerzustand('Ziele werden geladen …');
  if (!liste.length) return leerzustand('Keine berechenbaren Ziele vorhanden.');

  const gewaehlt = zustand.gewaehlteZiele;
  const alleIds = liste.map((z) => z.id);

  const setzeAuswahl = (ids) => {
    aendern({ gewaehlteZiele: new Set(ids) }, 'zielauswahl');
  };
  const umschalten = (id) => {
    const neu = new Set(gewaehlt);
    if (neu.has(id)) neu.delete(id); else neu.add(id);
    setzeAuswahl(neu);
  };

  const nachRaum = new Map();
  for (const ziel of liste) {
    if (!nachRaum.has(ziel.namensraum)) nachRaum.set(ziel.namensraum, []);
    nachRaum.get(ziel.namensraum).push(ziel);
  }

  const leiste = el('div.ziel-leiste', {}, [
    el('input', {
      type: 'checkbox',
      checked: gewaehlt.size === alleIds.length && alleIds.length > 0,
      indeterminate: gewaehlt.size > 0 && gewaehlt.size < alleIds.length,
      title: 'Alle oder keine',
      on: { change: (e) => setzeAuswahl(e.target.checked ? alleIds : []) },
    }),
    el('span', {}, [
      el('span.anzahl', { text: String(gewaehlt.size) }),
      ` von ${alleIds.length} Zielen gewählt`,
    ]),
    el('span', { style: { marginLeft: 'auto' } }),
    el('button.knopf.knopf-haupt', {
      text: 'Gewählte rechnen',
      disabled: gewaehlt.size === 0,
      on: { click: () => beiZielwahl([...gewaehlt]) },
    }),
    el('button.knopf', {
      text: 'Alles rechnen',
      title: 'Alle Nachweise, wie beim Knopf oben',
      on: { click: () => beiZielwahl(null) },
    }),
  ]);

  const kette = zustand.verfolgtesZiel && loesung?.ketten?.[zustand.verfolgtesZiel];

  return el('div.blatt', {}, [
    el('div.b-titel', { text: 'Ziel wählen' }),
    el('p.b-text', {
      text: 'Werte anhaken und rechnen lassen: der Rechenkern löst rückwärts auf, '
          + 'rechnet nur das Nötige und benennt, was fehlt.',
    }),
    leiste,
    kette
      ? el('div.hinweis.hinweis-annahme', {}, [
        el('div', {}, [el('b', { text: `Für ${zustand.verfolgtesZiel} nötig:` })]),
        el('div', { text: `${kette.berechnungen.length} Rechenschritte, ${kette.werte.length} Werte` }),
        el('ol.kettenliste', {}, kette.berechnungen.map((b) => el('li', { text: b }))),
      ])
      : null,

    ...[...nachRaum.entries()].map(([raum, ziele]) => {
      const alleImRaum = ziele.every((z) => gewaehlt.has(z.id));
      return el('div', {}, [
        el('div.zielgruppe-kopf', {}, [
          el('input', {
            type: 'checkbox', checked: alleImRaum,
            title: 'Diese Gruppe an- oder abwählen',
            on: {
              change: (e) => {
                const neu = new Set(gewaehlt);
                for (const z of ziele) {
                  if (e.target.checked) neu.add(z.id); else neu.delete(z.id);
                }
                setzeAuswahl(neu);
              },
            },
          }),
          el('span', { text: raum }),
        ]),
        ...ziele.map((ziel) => {
          const symbol = el('span');
          setzen(ziel.symbol, symbol, { displayMode: false });
          const wert = loesung?.werte?.[ziel.id];
          return el('div.zielzeile', {
            class: gewaehlt.has(ziel.id) ? 'ist-gewaehlt' : '',
            title: ziel.referenz || '',
            on: { click: () => umschalten(ziel.id) },
          }, [
            el('input', {
              type: 'checkbox', checked: gewaehlt.has(ziel.id),
              on: { click: (e) => { e.stopPropagation(); umschalten(ziel.id); } },
            }),
            symbol,
            el('div', {}, [
              el('div.beschreibung', { text: ziel.beschreibung || ziel.id }),
              el('div.kennung', { text: ziel.id }),
            ]),
            el('span', {
              text: wert ? `${wert.wert} ${wert.einheit}` : '—',
              style: {
                fontVariantNumeric: 'tabular-nums',
                color: wert ? '' : 'var(--schrift-zart)',
              },
            }),
          ]);
        }),
      ]);
    }),
  ]);
}


// ===========================================================================

export function berichtZeichnen(behaelter, beiZielwahl) {
  const loesung = zustand.loesung;

  if (!loesung && zustand.reiter !== 'ziele') {
    return ersetzen(behaelter, leerzustand(
      'Noch nichts gerechnet.',
      'Oben auf "Rechnen" klicken.'));
  }

  const sichten = {
    herleitung: () => herleitung(loesung),
    nachweise: () => nachweise(loesung),
    diagramm: () => diagrammSicht(loesung),
    werte: () => werteSicht(loesung),
    ziele: () => zieleSicht(loesung, beiZielwahl),
  };
  return ersetzen(behaelter, (sichten[zustand.reiter] || sichten.herleitung)());
}
