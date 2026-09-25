/**
 * bericht.js -- Rechte Tafel: das Rechenergebnis.
 *
 * Drei Sichten auf dieselbe Lösung:
 *   Zusammenfassung  je Platte eine Tabelle mit Urteilen und Erfüllungsgraden;
 *                    das Auge je Zeile zeigt genau diesen Nachweis
 *   Diagramme        Interaktionslinien, Kurven, Querschnitt
 *   Herleitung       die Mitschrift des Rechenkerns, Formel für Formel
 *
 * Sämtliche Zahlen und Formeln stammen unverändert aus der Lösung. Die
 * Oberfläche formatiert nichts nach -- sonst stünde am Bildschirm etwas
 * anderes als im Bericht.
 */

import { el, ersetzen, leerzustand, melden, svgEl, zahlfeld } from './dom.js';
import {
  kopiereFuerWord, kopiereTabelleFuerWord, kopiereText, setzen,
} from './mathe.js';
import {
  diagrammZeichnen, kurveZeichnen, neigungskurveZeichnen,
  querkraftkurveZeichnen, querschnittZeichnen,
} from './diagramm.js';
import { spannungsfallZeichnen } from './spannungsbild.js';
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
 * Die drei Kopierknöpfe Word, TeX und MD. Stehen an jedem Block, der LaTeX
 * hergibt -- Gleichung wie Tabelle. Einmal geschrieben, damit sie überall
 * dieselben sind.
 *
 * @param block  `{latex, markdown}`, bei einer Tabelle dazu `{kopf, zeilen}`:
 *   Word bekommt dann eine echte Tabelle statt einer Formel. Das Markdown
 *   kommt fertig aus dem Kern -- der Block, wie er im Markdown-Bericht steht.
 */
function werkzeugleiste(block) {
  const tabelle = block.kopf !== undefined;
  const was = tabelle ? 'Tabelle' : 'Formel';
  return el('div.gleichung-werkzeug', {}, [
    werkzeugKnopf('Word', `Als ${was} für Word kopieren`, async () => {
      await (tabelle
        ? kopiereTabelleFuerWord(block.kopf, block.zeilen)
        : kopiereFuerWord(block.latex));
      melden(`${was} kopiert – in Word mit Strg+V einfügen.`);
    }),
    werkzeugKnopf('TeX', 'LaTeX-Quelltext kopieren', async () => {
      await kopiereText(block.latex);
      melden('LaTeX kopiert.');
    }),
    block.markdown
      ? werkzeugKnopf('MD', 'Als Markdown kopieren', async () => {
        await kopiereText(block.markdown);
        melden('Markdown kopiert.');
      })
      : null,
  ]);
}

function gleichungBlock(block) {
  // Ein Block kann mehrere Werte tragen (siehe `gruppenBilden`).
  const ids = block.wert_ids || (block.wert_id ? [block.wert_id] : []);
  const latex = block.latex;

  const huelle = el('div.gleichung', {
    dataset: { wertId: ids.join(' ') },
  }, [
    (block.titel || block.referenz)
      ? el('div.gleichung-kopf', {}, [
        block.titel ? el('span.gleichung-titel', { text: block.titel }) : null,
        block.referenz ? el('span.gleichung-ref', { text: block.referenz }) : null,
      ])
      : null,
    el('div.gleichung-mathe'),
    werkzeugleiste(block),
  ]);

  setzen(latex, huelle.querySelector('.gleichung-mathe'));
  return huelle;
}

/**
 * Setzt eine Tabellenzelle: Text als Text, nur eine Formel mit KaTeX.
 *
 * Welche Art eine Zelle hat, sagt der Kern (`{text}` oder `{mathe}`). Früher
 * war jede Zelle LaTeX, und reiner Text musste per regulärem Ausdruck aus
 * `\text{…}` zurückgelesen werden.
 */
function zelleSetzen(zelle, knoten) {
  if (zelle.mathe !== undefined) setzen(zelle.mathe, knoten, { displayMode: false });
  else knoten.textContent = zelle.text;
  return knoten;
}

/**
 * Wie eine Spalte ausgerichtet ist -- so, wie der Kern es angibt, in der
 * Schreibweise von LaTeX (``L`` ist links und darf umbrechen). Ohne Angabe
 * bleibt es beim Stil: Zahlen rechts, die erste Spalte links.
 */
function spaltenausrichtung(ausrichtung, i) {
  return { l: 'left', L: 'left', c: 'center', r: 'right' }[(ausrichtung || '')[i]] || '';
}

function tabellenBlock(block) {
  const zelle = (inhalt, art, i) => zelleSetzen(inhalt, el(art, {
    style: { textAlign: spaltenausrichtung(block.ausrichtung, i) },
  }));
  return el('div.tabelle-block', {}, [
    block.titel
      ? el('div.gleichung-kopf', {}, [
        el('span.gleichung-titel', { text: block.titel }),
      ])
      : null,
    el('div.tabelle-huelle', {}, [
      el('table.gitter', {}, [
        el('thead', {}, [
          el('tr', {}, block.kopf.map((inhalt, i) => zelle(inhalt, 'th', i))),
        ]),
        el('tbody', {}, block.zeilen.map((zeile) => el('tr', {},
          zeile.map((inhalt, i) => zelle(inhalt, 'td', i))))),
      ]),
    ]),
    block.latex ? werkzeugleiste(block) : null,
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
      // Im Markdown-Bericht stehen die Angaben einzeln; zusammengelegt wird
      // nur hier. Der MD-Knopf liefert darum die Blöcke, wie sie dort stehen.
      letzte.markdown += `\n\n${block.markdown}`;
      letzte.wert_ids.push(block.wert_id);
    } else {
      heraus.push({
        art: 'gleichung',
        gruppe: block.gruppe,
        titel: block.gruppe,
        referenz: block.referenz,
        latex: block.latex,
        markdown: block.markdown,
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

/**
 * Die Herleitung -- ganz, oder nur der eine Nachweis, den das Auge in der
 * Zusammenfassung gewählt hat (`zustand.verfolgung`). Der zeigt alles, was er
 * braucht, auch die Baustoffe ausserhalb der gewählten Platte; darum gilt
 * dann kein Seitenfilter.
 */
function herleitung(gesamt) {
  const verfolgung = zustand.verfolgung;
  const loesung = verfolgung?.loesung || gesamt;
  if (!loesung.protokoll?.length) {
    return leerzustand('Noch nichts gerechnet.', 'Oben auf "Rechnen" klicken.');
  }
  const raum = verfolgung ? null : eingrenzung();
  if (!verfolgung && zustand.umfang === 'seite' && !raum) {
    return leerzustand('Nichts ausgewählt.',
      'Links einen Bestandteil wählen – oder oben auf "Gesamt" umschalten.');
  }
  const bloecke = nurAbschnitt(loesung.protokoll, raum);
  if (!bloecke.length) {
    return leerzustand('Für diesen Bestandteil wurde nichts gerechnet.');
  }

  return el('div.blatt', {}, [
    verfolgung
      ? el('div.hinweis.hinweis-annahme.verfolgung', {}, [
        el('b', { text: verfolgung.name }),
        el('span', { text: ` · ${loesung.reihenfolge.length} Rechenschritte` }),
        el('button.knopf.knopf-klein', {
          text: 'ganze Herleitung',
          on: { click: () => aendern({ verfolgung: null }, 'verfolgung') },
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
function zusammenfassung(loesung, verfolgen) {
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
      // Was die Platte ist und wie sie bewehrt ist, steht über der Tabelle --
      // als gewöhnliche Gleichung und gewöhnliche Tabelle, mit denselben
      // Kopierknöpfen wie alles andere.
      tabelle?.angaben ? gleichungBlock(tabelle.angaben) : null,
      tabelle?.bewehrung ? tabellenBlock(tabelle.bewehrung) : null,
      tabelle
        ? el('div.tabelle-block', {}, [
          el('div.tabelle-huelle', {}, [nachweistabelle(tabelle, verfolgen)]),
          werkzeugleiste({
            latex: tabelle.latex,
            markdown: tabelle.markdown,
            kopf: tabelle.kopf,
            zeilen: tabelle.zeilen.map((z) => z.zellen),
          }),
          // Ein Widerstand von null erklärt sich nicht von selbst. Der Grund
          // steht deshalb unter der Tabelle und nicht bloss im Tooltip, nach
          // Grund gebündelt -- die Sätze kommen fertig aus dem Kern, derselbe
          // Wortlaut wie im Bericht.
          ...(tabelle.hinweise || []).map((text) => el('p.hinweis', { text })),
          // Ausgeschaltete Nachweise: sie laufen mit, stehen aber nicht in
          // der Tabelle und nicht in der Herleitung. Geht einer nicht auf,
          // steht es hier -- leise, denn geführt wird er ja nicht.
          ...(tabelle.stille || []).map((s) => el('p.stiller-hinweis', { text: s.text })),
        ])
        : el('div.leer', { text: 'Für diese Platte wurde kein Nachweis gerechnet.' }),
      plattenkennzahlen(eintrag, loesung),
    ]);
  });

  return el('div', {}, blaetter.concat([lueckenBanner(loesung)].filter(Boolean)));
}

/**
 * Die Nachweistabelle der Oberfläche: keine Zelle mit mehr als zwei Zeilen.
 *
 * Widerstand und Einwirkung stehen übereinander in einer Zelle -- welche
 * Spalten das sind, sagt der Kern (`stapel_spalten`); der Bericht und der
 * Kopierknopf behalten beide Spalten. Texte werden an der ausgewogensten
 * Wortgrenze in zwei Zeilen geteilt, und keine Zeile bricht weiter um. Die
 * Tabelle ist darum nie schmaler als dieser Inhalt; ist die Tafel schmaler,
 * rollt die Hülle.
 *
 * Zuletzt je Zeile ein Auge: genau dieser Nachweis in der Herleitung.
 */
function nachweistabelle(tabelle, verfolgen) {
  const [oben, unten] = tabelle.stapel_spalten || [];
  const zelle = (inhalte, art, i) => {
    // Links oder rechts sagt der Kern -- dieselbe Ausrichtung, die auch das
    // LaTeX bekommt.
    const rechts = spaltenausrichtung(tabelle.ausrichtung, i) !== 'left';
    // Welche Spalte der Erfüllungsgrad ist, sagt der Kern. Sie trägt das
    // Urteil allein.
    const istGrad = art === 'td' && i === tabelle.grad_spalte;
    const knoten = el(art, {
      class: [rechts ? 'zahl' : 'links', istGrad ? 'grad' : ''].filter(Boolean).join(' '),
    });
    knoten.append(...inhalte.flatMap(zeilenVon).map((z) => zelleSetzen(z, el('span.zeile'))));
    return knoten;
  };
  const reihe = (zellen, art) => zellen.flatMap((inhalt, i) => {
    if (i === unten) return [];
    return [zelle(i === oben ? [inhalt, zellen[unten]] : [inhalt], art, i)];
  });

  const auge = (zeile) => {
    const name = zeile.zellen.slice(0, 2).map((z) => z.text).filter(Boolean).join(' – ');
    return el('td.auge-zelle', {}, [el('button.auge', {
      title: 'Spezifischen Nachweis zeigen',
      'aria-label': `Spezifischen Nachweis zeigen: ${name}`,
      class: zustand.verfolgung?.ziel === zeile.ziel ? 'ist-an' : '',
      on: { click: () => verfolgen(zeile.ziel, name) },
    }, [augenbild()])]);
  };

  return el('table.nachweis-tabelle', {}, [
    el('thead', {}, [el('tr', {}, [...reihe(tabelle.kopf, 'th'), el('th')])]),
    el('tbody', {}, tabelle.zeilen.map((zeile) => el('tr', {
      class: zeile.erfuellt ? 'ist-gut' : 'ist-schlecht',
      title: zeile.begruendung || '',
    }, [...reihe(zeile.zellen, 'td'), zeile.ziel ? auge(zeile) : el('td')]))),
  ]);
}

/** Ein Auge als Strichzeichnung -- in der Schriftfarbe, also auch dunkel lesbar. */
function augenbild() {
  const bild = svgEl('svg', {
    viewBox: '0 0 24 24', width: 16, height: 16, 'aria-hidden': 'true',
    fill: 'none', stroke: 'currentColor', 'stroke-width': 1.8,
    'stroke-linecap': 'round', 'stroke-linejoin': 'round',
  });
  bild.append(
    svgEl('path', { d: 'M1.5 12S5.5 5 12 5s10.5 7 10.5 7-4 7-10.5 7S1.5 12 1.5 12z' }),
    svgEl('circle', { cx: 12, cy: 12, r: 3 }),
  );
  return bild;
}

/**
 * Eine Zelle als Zeilen: Formeln bleiben ganz, Text wird an der
 * ausgewogensten Wortgrenze geteilt -- aber nur, wenn das die Spalte
 * spürbar schmaler macht. «Tragsicherheit 1» bleibt beisammen,
 * «Biegung und Normalkraft» wird «Biegung und / Normalkraft».
 */
function zeilenVon(zelle) {
  if (zelle.mathe !== undefined) return [zelle];
  const woerter = zelle.text.split(' ');
  let beste = null;
  for (let i = 1; i < woerter.length; i += 1) {
    const zeilen = [woerter.slice(0, i).join(' '), woerter.slice(i).join(' ')];
    const breite = Math.max(...zeilen.map((z) => z.length));
    if (!beste || breite < beste.breite) beste = { breite, zeilen };
  }
  if (!beste || beste.breite > 0.75 * zelle.text.length) return [zelle];
  return beste.zeilen.map((text) => ({ text }));
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

/**
 * Spannung-Dehnung-Analyse -- noch ohne Inhalt.
 *
 * Das Panel steht, damit klar ist, wohin die Auswertung der Dehnungsebenen
 * gehört: der Querschnittslöser liefert zu jeder Schnittgrössenkombination
 * ein ε_m und ein χ, und daraus liesse sich der ganze Spannungsverlauf über
 * die Höhe zeichnen. Was genau gezeigt wird, ist noch offen -- darum steht
 * hier bewusst ein leerer Platz und keine erfundene Darstellung.
 */

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

  // -- Querschnitt, Interaktionslinien und Spannungsbilder ----------------
  const analysen = loesung.spannungsanalysen || {};
  for (const [kennung, eintrag] of Object.entries(querschnitte)) {
    if (!imRaum(raum, eintrag.namensraum)) continue;
    const eigene = Object.entries(linien)
      .filter(([schluessel]) => schluessel.split('.')[0] === kennung);
    blaetter.push(el('div.blatt', {}, [
      el('div.b-titel', { text: `Querschnitt – ${eintrag.name}` }),
      querschnittZeichnen(eintrag, loesung.werte || {}),
      ...eigene.flatMap(([, linie]) => [
        el('div.b-titel', {
          text: `M-N-Interaktionsdiagramm – ${eintrag.name}`,
        }),
        diagrammZeichnen(linie),
      ]),
      ...querkraftkurven(loesung, kennung),
      ...neigungskurven(loesung, kennung),
      ...(analysen[kennung] || []).map(spannungsfallZeichnen),
    ]));
  }

  if (!blaetter.length) return leerzustand('Noch nichts zu zeichnen.');
  // Wie viele Blätter nebeneinander -- der Schalter steht über allem, weil er
  // für alle gilt und nicht für eines.
  return el('div', {}, [spaltenwahl(), el('div.blaetter', {
    class: `ist-${zustand.diagrammspalten || 1}`,
  }, blaetter)]);
}

/** Wie viele Diagramme nebeneinander stehen -- eins, zwei oder drei. */
function spaltenwahl() {
  const jetzt = zustand.diagrammspalten || 1;
  return el('div.spaltenwahl', {}, [
    el('span', { text: 'Diagramme nebeneinander' }),
    el('span.schalter', {}, [1, 2, 3].map((n) => el('button.schalter-halb', {
      text: String(n),
      class: n === jetzt ? 'ist-an' : '',
      title: `${n} Diagramm${n > 1 ? 'e' : ''} je Zeile`,
      on: { click: () => aendern({ diagrammspalten: n }, 'diagramm') },
    }))),
  ]);
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
    // Wer zweimal kurz hintereinander weiterstellt, hat zwei Anfragen
    // unterwegs -- und die ältere darf die jüngere nicht überholen. Sonst
    // stünde unter der Kurve die eine Normalkraft und gezeichnet wäre die
    // andere.
    if (zustand.kurvenNormalkraft[kennung] !== N_Ed) return;
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
      text: `Querkraft über Moment – ${kurve.name}`,
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

/**
 * Die Neigungskurven einer Platte -- nur mit Querkraftbewehrung.
 *
 * Dann hängt der Widerstand nicht mehr am Moment, sondern an der Neigung der
 * Druckdiagonalen; an die Stelle der M-V-Kurve tritt dieses Bild. Ein Bild je
 * statischer Höhe und Neigungsbereich -- beides hängt am einzelnen Fall, und
 * der Kern sagt selbst, welche Bilder es gibt.
 */
function neigungskurven(loesung, querschnitt) {
  const alle = Object.entries(loesung.neigungskurven || {})
    .filter(([, k]) => k.querschnitt === querschnitt);

  return alle.flatMap(([, kurve]) => [
    el('div.b-titel', {
      text: `Querkraft über Neigung – ${kurve.name}`,
    }),
    neigungskurveZeichnen(kurve),
    el('div.kurvenfuss', {}, [
      el('span.kurvenfuss-name', { text: `d = ${kurve.d.toFixed(1)} mm` }),
      el('span.kurvenhinweis', {
        text: kurve.zug
          ? `Normalzug: α_min ist auf ${kurve.alpha_min}° angehoben. `
            + 'Ausserhalb der Grenzen ist die Kurve blass gezeichnet.'
          : 'Ausserhalb von α_min und α_max ist die Kurve blass gezeichnet.',
      }),
    ]),
  ]);
}

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

export function berichtZeichnen(behaelter, { verfolgen }) {
  const loesung = zustand.loesung;

  if (!loesung) {
    return ersetzen(behaelter, leerzustand(
      'Noch nichts gerechnet.',
      'Oben auf "Rechnen" klicken.'));
  }

  const sichten = {
    nachweise: () => zusammenfassung(loesung, verfolgen),
    diagramm: () => diagrammSicht(loesung),
    herleitung: () => herleitung(loesung),
  };
  return ersetzen(behaelter, (sichten[zustand.reiter] || sichten.nachweise)());
}
