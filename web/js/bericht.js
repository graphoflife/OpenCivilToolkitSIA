/**
 * bericht.js -- Rechte Tafel: das Rechenergebnis.
 *
 * Fünf Sichten auf dieselbe Lösung:
 *   Herleitung  die Mitschrift des Rechenkerns, Formel für Formel
 *   Zusammenfassung  je Platte eine Tabelle mit Urteilen und Erfüllungsgraden
 *   Diagramm    die M-N-Interaktionslinie
 *   Werte       alle bestimmten Grössen mit ihrer Herkunft
 *   Ziel wählen einen Wert anfordern und zurückverfolgen, was dafür nötig ist
 *
 * Sämtliche Zahlen und Formeln stammen unverändert aus der Lösung. Die
 * Oberfläche formatiert nichts nach -- sonst stünde am Bildschirm etwas
 * anderes als im Bericht.
 */

import { el, ersetzen, leerzustand, melden, zahlfeld } from './dom.js';
import { kopiereFuerWord, kopiereLatex, setzen } from './mathe.js';
import {
  diagrammZeichnen, kurveZeichnen, querkraftkurveZeichnen, querschnittZeichnen,
} from './diagramm.js';
import { api } from './api.js';
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

/**
 * Die beiden Kopierknöpfe. Stehen an jedem Block, der LaTeX hergibt --
 * Gleichung wie Tabelle. Einmal geschrieben, damit sie überall dieselben sind.
 */
function werkzeugleiste(latex, was = 'Formel') {
  return el('div.gleichung-werkzeug', {}, [
    werkzeugKnopf('Word', `Als ${was} für Word kopieren (MathML)`, async () => {
      await kopiereFuerWord(latex);
      melden(`${was} kopiert – in Word mit Strg+V einfügen.`);
    }),
    werkzeugKnopf('TeX', 'LaTeX-Quelltext kopieren', async () => {
      await kopiereLatex(latex);
      melden('LaTeX kopiert.');
    }),
  ]);
}

function gleichungBlock(block) {
  // Ein Block kann mehrere Werte tragen (siehe `gruppenBilden`). Hervorgehoben
  // wird er, sobald einer davon zur verfolgten Kette gehört.
  const ids = block.wert_ids || (block.wert_id ? [block.wert_id] : []);
  const hervorgehoben = ids.some((id) => zustand.hervorgehoben.has(id));
  const latex = block.latex;

  const huelle = el('div.gleichung', {
    class: hervorgehoben ? 'ist-hervorgehoben' : '',
    dataset: { wertId: ids.join(' ') },
  }, [
    (block.titel || block.referenz)
      ? el('div.gleichung-kopf', {}, [
        block.titel ? el('span.gleichung-titel', { text: block.titel }) : null,
        block.referenz ? el('span.gleichung-ref', { text: block.referenz }) : null,
      ])
      : null,
    el('div.gleichung-mathe'),
    werkzeugleiste(latex),
  ]);

  setzen(latex, huelle.querySelector('.gleichung-mathe'));
  return huelle;
}

function tabellenBlock(block) {
  return el('div.tabelle-block', {}, [
    block.titel
      ? el('div.gleichung-kopf', {}, [
        el('span.gleichung-titel', { text: block.titel }),
      ])
      : null,
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
    block.latex ? werkzeugleiste(block.latex, 'Tabelle') : null,
  ]);
}

/**
 * Legt aufeinanderfolgende Blöcke derselben Gruppe zu **einem** Block zusammen.
 *
 * Vier Zeilen `h = 300 mm`, `b = 1000 mm`, … untereinander sind kein Nachweis,
 * sondern eine Liste. Der zusammengelegte Block ist eine gewöhnliche Gleichung
 * wie jede andere -- gleiche Gestalt, gleiche Kopierknöpfe. Ein eigenes
 * Aussehen wäre ein zweites Konzept für dieselbe Sache gewesen.
 *
 * Zusammengelegt wird erst **hier**, nicht im Kern. Das ist der Punkt: bei
 * einer Rückverfolgung läuft nur, was gebraucht wird, also entstehen dort auch
 * nur die Blöcke der gebrauchten Werte. Der zusammengelegte Block enthält
 * damit von selbst genau sie -- und `wert_ids` hält fest, welche.
 */
function gruppenBilden(bloecke) {
  const heraus = [];
  for (const block of bloecke) {
    const letzte = heraus[heraus.length - 1];
    if (block.art !== 'gleichung' || !block.gruppe) {
      heraus.push(block);
    } else if (letzte?.gruppe === block.gruppe) {
      letzte.latex += ` \\qquad ${block.latex}`;
      letzte.wert_ids.push(block.wert_id);
    } else {
      heraus.push({
        art: 'gleichung',
        gruppe: block.gruppe,
        titel: block.gruppe,
        referenz: block.referenz,
        latex: block.latex,
        wert_ids: [block.wert_id],
      });
    }
  }
  return heraus;
}

function bloeckeZeichnen(rohbloecke) {
  const knoten = [];
  for (const block of gruppenBilden(rohbloecke)) {
    if (block.art === 'titel') {
      knoten.push(titelZeichnen(block));
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
      knoten.push(el('div.b-untertitel.ist-tief', { text: block.titel }));
      knoten.push(...bloeckeZeichnen(block.bloecke));
    }
  }
  return knoten;
}

/**
 * Eine Überschrift der Mitschrift.
 *
 * Welche Art es ist, sagt der Block selbst: trägt er einen Namensraum, beginnt
 * hier ein neuer Bestandteil -- ein Baustoff, eine Platte. Alles andere
 * gliedert innerhalb.
 *
 * Vorher entschied die Ebene darüber, und die ist bei einem Abschnitt und bei
 * «Querkraft – x-Richtung» dieselbe. Beide sahen also gleich aus, und die
 * Mitschrift wirkte flach, wo sie es nicht ist. Die Ebene bleibt, aber nur
 * noch für die Tiefe *innerhalb* eines Abschnitts.
 */
function titelZeichnen(block) {
  if (block.raum) return el('div.b-titel', { text: block.text });
  return el(`div.b-untertitel${block.ebene >= 3 ? '.ist-tief' : ''}`,
    { text: block.text });
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

/**
 * Schneidet die Mitschrift auf einen Namensraum zu.
 *
 * Die Blöcke liegen flach hintereinander; ein Abschnitt reicht von seinem Titel
 * bis zum nächsten. Welcher Titel einen eröffnet und zu welchem Bestandteil er
 * gehört, sagt der Kern selbst mit `raum` -- ein Vergleich über Anzeigetexte
 * bräche, sobald jemand eine Überschrift umformuliert, und zwar stumm.
 */
function nurAbschnitt(bloecke, raum) {
  if (!raum) return bloecke;
  const gewaehlt = [];
  let drin = false;
  for (const block of bloecke) {
    if (block.art === 'titel' && block.raum) drin = imRaum(raum, block.raum);
    if (drin) gewaehlt.push(block);
  }
  return gewaehlt;
}

function herleitung(loesung) {
  if (!loesung.protokoll?.length) {
    return leerzustand('Noch nichts gerechnet.', 'Oben auf "Rechnen" klicken.');
  }
  const raum = eingrenzung();
  if (zustand.umfang === 'seite' && !raum) {
    return leerzustand('Nichts ausgewählt.',
      'Links einen Bestandteil wählen – oder oben auf "Gesamt" umschalten.');
  }
  const bloecke = nurAbschnitt(loesung.protokoll, raum);
  if (!bloecke.length) {
    return leerzustand('Für diesen Bestandteil wurde nichts gerechnet.');
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
    ...bloeckeZeichnen(bloecke),
    lueckenBanner(loesung),
  ]);
}

/**
 * Die Zusammenfassung: je Plattenquerschnitt eine Tabelle.
 *
 * Welche Platten erscheinen, steuert der Schalter *Gesamt / Aktuelle Seite*.
 * Ist ein Material gewählt und "Aktuelle Seite" aktiv, bleibt sie leer -- ein
 * Baustoff hat keine Nachweise, und eine willkürlich herausgegriffene Platte
 * zu zeigen wäre irreführend.
 */
function zusammenfassung(loesung) {
  const querschnitte = loesung.zuordnung?.querschnitte || {};
  const raum = eingrenzung();

  const gezeigt = Object.entries(querschnitte).filter(
    ([, eintrag]) => imRaum(raum, eintrag.namensraum));
  if (raum && !gezeigt.length) {
    return leerzustand('Kein Querschnitt gewählt.',
      'Links eine Platte wählen – oder oben auf "Gesamt" umschalten.');
  }
  if (!gezeigt.length) {
    return el('div.blatt', {}, [
      leerzustand('Kein Querschnitt vorhanden.'),
      lueckenBanner(loesung),
    ]);
  }

  const tabellen = loesung.zusammenfassungen || {};

  const blaetter = gezeigt.map(([kennung, eintrag]) => {
    // Zeilen und LaTeX kommen fertig aus dem Kern. Sie hier ein zweites Mal
    // zusammenzustellen hiesse, dieselbe Tabelle zweimal zu pflegen -- einmal
    // fürs Auge, einmal für den Kopierknopf.
    const tabelle = tabellen[kennung];

    return el('div.blatt', {}, [
      el('div.b-titel', { text: `Zusammenfassung – ${eintrag.name}` }),
      tabelle
        ? el('div.tabelle-block', {}, [
          el('div.tabelle-huelle', {}, [
            el('table.nachweis-tabelle', {}, [
              el('thead', {}, [el('tr', {}, tabelle.kopf.map((zelle) => {
                const th = el('th');
                setzen(zelle, th, { displayMode: false });
                return th;
              }))]),
              el('tbody', {}, tabelle.zeilen.map((zeile) => el('tr', {
                class: zeile.erfuellt ? 'ist-gut' : 'ist-schlecht',
                title: zeile.begruendung || '',
              }, zeile.zellen.map((zelle, i) => {
                const td = el('td', { class: i === 0 ? '' : 'zahl' });
                setzen(zelle, td, { displayMode: false });
                return td;
              })))),
            ]),
          ]),
          werkzeugleiste(tabelle.latex, 'Tabelle'),
        ])
        : el('div.leer', { text: 'Für diese Platte wurde kein Nachweis gerechnet.' }),
      plattenkennzahlen(eintrag, loesung),
    ]);
  });

  return el('div', {}, blaetter.concat([lueckenBanner(loesung)].filter(Boolean)));
}

/**
 * Die beiden Angaben zur Ausführung unter der Tabelle.
 *
 * Beide kommen fertig aus dem Kern -- hier wird nichts gerechnet, auch nicht
 * "nur schnell" das Bewehrungsmass aus den Flächen.
 */
function plattenkennzahlen(eintrag, loesung) {
  const zeigen = [
    ['Bewehrungsmass', eintrag.werte?.bewehrungsmass, 'Stahldichte 7850 kg/m³'],
    ['Höhe der Distanzhalter', eintrag.werte?.distanzhalter,
      'OK innere untere Lage bis UK innere obere Lage'],
  ];
  const zeilen = zeigen
    .map(([beschriftung, id, erklaerung]) => [beschriftung, loesung.werte?.[id], erklaerung])
    .filter(([, wert]) => wert);
  if (!zeilen.length) return null;

  return el('div.kennzahlen', {}, zeilen.map(([beschriftung, wert, erklaerung]) =>
    el('div.kennzahl', { title: erklaerung }, [
      el('span.kennzahl-name', { text: beschriftung }),
      el('span.kennzahl-wert', { text: `${wert.wert} ${wert.einheit}` }),
    ])));
}

function diagrammSicht(loesung) {
  const raum = eingrenzung();
  const linien = loesung.linien || {};
  const querschnitte = loesung.zuordnung?.querschnitte || {};
  const gesetze = loesung.werkstoffgesetze || {};
  const blaetter = [];

  // -- Werkstoffgesetze ---------------------------------------------------
  for (const [kennung, gesetz] of Object.entries(gesetze)) {
    if (!imRaum(raum, `${gesetz.art}.${kennung}`)) continue;
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
    if (!imRaum(raum, eintrag.namensraum)) continue;
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
      ...querkraftkurven(loesung, kennung),
    ]));
  }

  if (!blaetter.length) return leerzustand('Noch nichts zu zeichnen.');
  return el('div', {}, blaetter);
}

/**
 * Stellt eine Kurve auf eine andere Normalkraft um.
 *
 * Gerechnet wird im Kern, nicht hier: `v_Rd` hängt über `m_Rd(N_Ed)` an der
 * Resistenzlinie, und die Formel steht im Querkraftnachweis. Die Oberfläche
 * fragt nach und zeichnet, was zurückkommt.
 */
async function normalkraftWaehlen(kennung, N_Ed) {
  const gewaehlt = { ...zustand.kurvenNormalkraft, [kennung]: N_Ed };
  aendern({ kurvenNormalkraft: gewaehlt }, 'kurve');
  try {
    const antwort = await api.querkraftkurven(zustand.projekt, gewaehlt);
    // In die vorhandene Lösung einsetzen statt sie zu ersetzen: alles andere
    // -- Herleitung, Werte, Urteile -- gilt unverändert weiter.
    aendern({
      loesung: { ...zustand.loesung, querkraftkurven: antwort.querkraftkurven },
    }, 'kurve');
  } catch (fehler) {
    melden(fehler.message, true);
  }
}

/**
 * Die M-V-Kurven einer Platte -- bis zu vier.
 *
 * Je Tragrichtung und Momentenvorzeichen eine, aber nur dort, wo auch ein
 * Querkraftnachweis geführt wurde. Der Kern sagt selbst, welche es gibt; hier
 * wird nichts abgeleitet.
 *
 * Unter jeder Kurve steht die Normalkraft, für die sie gilt. Ändert man sie,
 * rechnet der Kern die Kurve neu -- die Formel bleibt dort, wo sie hingehört.
 */
function querkraftkurven(loesung, querschnitt) {
  const alle = Object.entries(loesung.querkraftkurven || {})
    .filter(([, k]) => k.querschnitt === querschnitt);

  return alle.flatMap(([kennung, kurve]) => [
    el('div.b-titel', {
      text: `Querkraft über Moment – ${kurve.name}, ${kurve.richtung}-Richtung`,
    }),
    querkraftkurveZeichnen(kurve),
    el('div.kurvenfuss', {}, [
      el('span.kurvenfuss-name', { text: 'gilt für N_Ed =' }),
      zahlfeld({
        wert: kurve.N_Ed, schritt: 50,
        titel: 'Normalkraft in kN – Zug positiv. Nur Bemessungspunkte mit '
             + 'genau dieser Normalkraft liegen auf dieser Kurve.',
        beiAenderung: (v) => normalkraftWaehlen(kennung, v ?? 0),
      }),
      el('span.einheit', { text: 'kN' }),
      el('span.kurvenhinweis', {
        text: 'Punkte mit abweichender Normalkraft sind blass gezeichnet.',
      }),
    ]),
  ]);
}

function werteSicht(loesung, beiZielwahl) {
  let eintraege = Object.values(loesung.werte || {});
  if (!eintraege.length) return leerzustand('Noch keine Werte bestimmt.');
  const raum = eingrenzung();
  if (raum) eintraege = eintraege.filter((w) => imRaum(raum, w.id));
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
/**
 * Der Namensraum des links gewählten Bestandteils -- `beton.b1`,
 * `querschnitt.q1`. Null, wenn nichts gewählt ist.
 */
function raumDerAuswahl() {
  const wahl = zustand.auswahl;
  if (!wahl) return null;
  if (wahl.art === 'material') {
    const m = zustand.projekt.materialien.find((x) => x.kennung === wahl.kennung);
    return m ? `${m.art}.${m.kennung}` : null;
  }
  return `querschnitt.${wahl.kennung}`;
}

/**
 * Auf welchen Namensraum die Ansicht eingegrenzt ist -- null heisst: alles.
 *
 * Die eine Stelle, an der «Gesamt / Aktuelle Seite» gelesen wird. Vorher stand
 * dieselbe Frage fünfmal da, jede Sicht mit einem anderen Schlüssel: einmal
 * über den Abschnittstitel, einmal über die Querschnittskennung, zweimal über
 * `auswahl.art` und einmal über den Namensraum. Ein sechster Bestandteil hätte
 * fünf Stellen gebraucht.
 */
function eingrenzung() {
  return zustand.umfang === 'seite' ? raumDerAuswahl() : null;
}

/** Gehört etwas mit diesem Namensraum in die Ansicht? */
function imRaum(raum, id) {
  return !raum || id === raum || id.startsWith(`${raum}.`);
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
    nachweise: () => zusammenfassung(loesung),
    diagramm: () => diagrammSicht(loesung),
    herleitung: () => herleitung(loesung),
    werte: () => werteSicht(loesung, beiZielwahl),
  };
  return ersetzen(behaelter, (sichten[zustand.reiter] || sichten.nachweise)());
}
