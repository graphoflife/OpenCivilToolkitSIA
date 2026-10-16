/**
 * bericht.js -- Rechte Tafel: das Rechenergebnis.
 *
 * Drei Sichten auf dieselbe Lösung:
 *   Zusammenfassung  je Bauteil ein Panel mit Angaben, Bewehrung, der Tabelle
 *                    der Urteile und Erfüllungsgrade; das Auge je Zeile zeigt
 *                    genau diesen Nachweis
 *   Diagramme        oben eine Leiste mit einer Vorschau je Diagramm,
 *                    darunter das gewählte gross
 *   Herleitung       die Mitschrift des Rechenkerns, je Abschnitt ein Panel;
 *                    jede Formel führt zu ihrer Seite in der Dokumentation
 *
 * Gebaut aus denselben Panels und Karten wie die Eingaben (`panel`, `karte`
 * in bausteine.js): graue Fläche, weisse Karten mit blauer Kante, ein Klick
 * auf den Kopf klappt zu (Benutzer, 2026-10-16).
 *
 * Sämtliche Zahlen und Formeln stammen unverändert aus der Lösung. Die
 * Oberfläche formatiert nichts nach -- sonst stünde am Bildschirm etwas
 * anderes als im Bericht.
 */

import { karte, panel } from './bausteine.js';
import { el, ersetzen, leerzustand, melden, svgEl, zahlfeld } from './dom.js';
import { setzen, span } from './mathe.js';
import { werkzeugleiste } from './kopierleiste.js';
import { adresse, seiteVorhanden } from './notizbuch.js';
import {
  diagrammZeichnen, kurveZeichnen, neigungskurveZeichnen,
  querkraftkurveZeichnen, querschnittZeichnen,
} from './diagramm.js';
import { analyseKarten } from './qa_diagramme.js';
import { systemKarten, systemZusammenfassung } from './bs_diagramme.js';
import { situationKarten } from './gb_zeichnung.js';
import { spannungsfallZeichnen } from './spannungsbild.js';
import { api } from './api.js';
import { ARTEN } from './arten.js';
import { aendern, namensraum, zustand } from './zustand.js';

// ===========================================================================
// Bausteine
// ===========================================================================

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
  // Zur Seite der Formel im Notizbuch: Theorie, Normstelle, Grössen.
  if (block.formelseite && seiteVorhanden(block.formelseite)) {
    huelle.querySelector('.gleichung-werkzeug').prepend(el('a.knopf.knopf-zart', {
      href: adresse(block.formelseite), text: 'Formel',
      title: `In der Formelsammlung: ${block.formelseite}`,
    }));
  }

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
 * Eine Überschrift innerhalb eines Abschnitts der Mitschrift.
 *
 * Ein Titel mit Namensraum -- ein neuer Bestandteil, ein Baustoff, eine
 * Platte -- steht hier nie: er ist der Kopf seines Panels (`abschnitte`).
 * Die Ebene sagt nur noch die Tiefe *innerhalb* eines Abschnitts.
 */
function titelZeichnen(block) {
  return el(`div.b-untertitel${block.ebene >= 3 ? '.ist-tief' : ''}`,
    { text: block.text });
}

function lueckenPanel(loesung) {
  if (!loesung.fehlende?.length) return null;
  return panel({ schluessel: 'bericht/fehlende', titel: 'Fehlende Eingaben' }, [karte(null, [
    el('p.b-text', { text: 'Es fehlen:' }),
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
  ])]);
}

/**
 * Die Panels der rechten Tafel, untereinander wie die der mittleren und so
 * breit wie `--berichtbreite` (Stilblatt). `klasse` trägt in den Diagrammen,
 * wie viele nebeneinander stehen.
 */
function stapel(inhalt, klasse = '') {
  return el('div.berichtstapel', { class: klasse }, inhalt);
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
  // Gewählt, aber noch nicht (neu) gerechnet -- siehe `verfolgen` in app.js.
  if (verfolgung && !verfolgung.loesung) return leerzustand('rechnet …', verfolgung.name);
  const loesung = verfolgung?.loesung || gesamt;
  if (!loesung.protokoll?.length) {
    return leerzustand('Noch nichts gerechnet.', 'Oben «Rechnen».');
  }
  const raum = verfolgung ? null : eingrenzung();
  const leer = !verfolgung && ohneAuswahl();
  if (leer) return leer;
  const bloecke = nurAbschnitt(loesung.protokoll, raum);
  if (!bloecke.length) {
    return leerzustand('Nichts gerechnet für diesen Bestandteil.');
  }

  return stapel([
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
    ...abschnitte(bloecke).map((a) => panel({
      schluessel: `bericht/herleitung/${a.raum || a.titel}`, titel: a.titel,
    }, kapitelkarten(a.bloecke))),
    lueckenPanel(loesung),
  ]);
}

/**
 * Ein Abschnitt der Mitschrift in Karten: je Kapitel -- ein Titel der Ebene
 * 2, etwa «Querkraft – x-Richtung» -- eine Karte mit ihm im Kopf, wie die
 * Kapitel der Eingaben. Was vor dem ersten steht, die Angaben des
 * Bestandteils, bekommt eine Karte ohne Kopf.
 */
function kapitelkarten(bloecke) {
  const kapitel = [];
  for (const block of bloecke) {
    if (block.art === 'titel' && block.ebene <= 2) {
      kapitel.push({ titel: block.text, bloecke: [] });
    } else {
      if (!kapitel.length) kapitel.push({ titel: null, bloecke: [] });
      kapitel.at(-1).bloecke.push(block);
    }
  }
  return kapitel.map((k) => karte(k.titel, bloeckeZeichnen(k.bloecke)));
}

/**
 * Die Mitschrift in Abschnitte geteilt: je Bestandteil einer -- ein Baustoff,
 * eine Platte --, eröffnet von einem Titel mit Namensraum. Der Titel wird
 * zum Kopf des Panels; was vor dem ersten steht, bildet einen Abschnitt
 * «Herleitung».
 */
function abschnitte(bloecke) {
  const heraus = [];
  for (const block of bloecke) {
    if (block.art === 'titel' && block.raum) {
      heraus.push({ titel: block.text, raum: block.raum, bloecke: [] });
    } else {
      if (!heraus.length) heraus.push({ titel: 'Herleitung', raum: null, bloecke: [] });
      heraus.at(-1).bloecke.push(block);
    }
  }
  return heraus;
}

/**
 * Was eine Bauteilart ohne Nachweise in der Zusammenfassung zeigt -- je Art
 * (ARTEN, arten.js).
 */
const UEBERSICHTEN = { balkensystem: systemZusammenfassung };

/**
 * Die Zusammenfassung: je Bauteil eine Tabelle, in der Reihenfolge von ARTEN
 * -- wie im Bericht.
 *
 * Welche Bauteile erscheinen, steuert der Schalter *Gesamt / Aktuelle Seite*.
 * Ist ein Material gewählt und "Aktuelle Seite" aktiv, bleibt sie leer -- ein
 * Baustoff hat keine Nachweise, und ein willkürlich herausgegriffenes Bauteil
 * zu zeigen wäre irreführend.
 */
function zusammenfassung(loesung, verfolgen) {
  const zuordnung = loesung.zuordnung || {};
  const raum = eingrenzung();
  const bauteile = (mitNachweisen) => ARTEN.filter((a) => a.nachweise === mitNachweisen)
    .flatMap((a) => Object.entries(zuordnung[a.liste] || {}).map(([kennung, eintrag]) => (
      { art: a, kennung, eintrag })))
    .filter(({ eintrag }) => imRaum(raum, eintrag.namensraum));

  const gezeigt = bauteile(true);
  // Die Bauteile ohne Nachweise danach -- ein Balkensystem führt keine, aber
  // seine Grenzwerte und Lagerkräfte gehören in die Übersicht.
  const ohne = bauteile(false);
  if (raum && !gezeigt.length && !ohne.length) {
    const arten = ARTEN.map((a) => a.einzahl);
    return leerzustand('Kein Bauteil gewählt.',
      `Links ${arten.slice(0, -1).join(', ')} oder ${arten.at(-1)} wählen oder oben «Gesamt».`);
  }
  if (!gezeigt.length && !ohne.length) {
    return stapel([leerzustand('Kein Bauteil vorhanden.'), lueckenPanel(loesung)]);
  }

  const tabellen = loesung.zusammenfassungen || {};

  // Je Bauteil ein Panel, wie in den Eingaben: darin die Angaben, die
  // Bewehrung, die Nachweise und die Kennzahlen je als Karte.
  const panels = gezeigt.map(({ kennung, eintrag }) => {
    // Zeilen und LaTeX kommen fertig aus dem Kern. Sie hier ein zweites Mal
    // zusammenzustellen hiesse, dieselbe Tabelle zweimal zu pflegen -- einmal
    // fürs Auge, einmal für den Kopierknopf.
    const tabelle = tabellen[kennung];
    const kennzahlen = kennzahlenliste(kennung, loesung);

    return panel({
      schluessel: `bericht/zusammenfassung/${kennung}`, titel: `Zusammenfassung – ${eintrag.name}`,
    }, [
      // Was das Bauteil ist und wie es bewehrt ist, steht über der Tabelle --
      // als gewöhnliche Gleichung und gewöhnliche Tabelle, mit denselben
      // Kopierknöpfen wie alles andere. Ihr Titel steht im Kopf der Karte.
      tabelle?.angaben
        ? karte(tabelle.angaben.titel, [gleichungBlock({ ...tabelle.angaben, titel: '' })],
          { klasse: 'ist-links' })
        : null,
      tabelle?.bewehrung
        ? karte(tabelle.bewehrung.titel, [tabellenBlock({ ...tabelle.bewehrung, titel: '' })])
        : null,
      karte('Nachweise', tabelle
        ? [el('div.tabelle-block', {}, [
          el('div.tabelle-huelle', {}, [nachweistabelle(tabelle, verfolgen)]),
          werkzeugleiste({
            latex: tabelle.latex,
            markdown: tabelle.markdown,
            kopf: tabelle.kopf,
            zeilen: tabelle.zeilen.map((z) => z.zellen),
          }),
        ]),
        // Ein Widerstand von null erklärt sich nicht von selbst. Der Grund
        // steht deshalb unter der Tabelle und nicht bloss im Tooltip, nach
        // Grund gebündelt -- die Sätze kommen fertig aus dem Kern, derselbe
        // Wortlaut wie im Bericht.
        ...(tabelle.hinweise || []).map((text) => el('p.hinweis', { text })),
        // Ausgeschaltete Nachweise: sie laufen mit, stehen aber nicht in
        // der Tabelle und nicht in der Herleitung. Geht einer nicht auf,
        // steht es hier -- leise, denn geführt wird er ja nicht.
        ...(tabelle.stille || []).map((s) => el('p.stiller-hinweis', { text: s.text }))]
        : [el('div.leer', { text: 'Kein Nachweis gerechnet.' })]),
      kennzahlen ? karte('Kennzahlen', [kennzahlen]) : null,
    ]);
  });

  return stapel([
    ...panels,
    ...ohne.map(({ art, kennung, eintrag }) => panel({
      schluessel: `bericht/zusammenfassung/${kennung}`, titel: `Zusammenfassung – ${eintrag.name}`,
    }, UEBERSICHTEN[art.art](kennung))),
    lueckenPanel(loesung),
  ]);
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

  const auge = (zeile) => el('td.auge-zelle', {}, [el('button.auge', {
    title: 'Spezifischen Nachweis zeigen',
    'aria-label': `Spezifischen Nachweis zeigen: ${zeile.bezeichnung}`,
    class: zustand.verfolgung?.ziel === zeile.ziel ? 'ist-an' : '',
    on: { click: () => verfolgen(zeile.ziel, zeile.bezeichnung) },
  }, [augenbild()])]);

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
 * Die Kennzahlen einer Platte unter der Tabelle: Bewehrungsmass,
 * Distanzhalter, die Vergrösserungsfaktoren ω_w und ω_w′, die Eckwerte der
 * Handrechnung und der Querkraftwiderstand bei N_Ed = 0 -- auch ohne
 * Lastfall (Benutzer, 2026-10-16).
 *
 * Liste, Beschriftung und Zahl kommen fertig aus dem Kern
 * (`zusammenfassung.kennzahlen`) -- dieselben wie im Bericht. Hier wird
 * nichts gerechnet und nichts gerundet.
 */
function kennzahlenliste(kennung, loesung) {
  const zeilen = loesung.kennzahlen?.[kennung] || [];
  if (!zeilen.length) return null;
  return el('div.kennzahlen', {}, zeilen.map((k) => el('div.kennzahl', { title: k.erklaerung }, [
    el('span.kennzahl-name', {}, [k.beschriftung]),
    el('span.kennzahl-zeichen', {}, [span(k.symbol)]),
    el('span.kennzahl-wert', { text: k.einheit ? `${k.text} ${k.einheit}` : k.text }),
  ])));
}

/**
 * Die Karten einer Platte: ihr Querschnitt, die Interaktionslinien, die
 * Querkraftkurven und die Spannung-Dehnung-Analysen.
 */
function plattenkarten(kennung, eintrag, loesung) {
  const eigene = Object.values(loesung.linien || {}).filter((linie) => linie.bauteil === kennung);
  return [
    karte('Querschnitt', [querschnittZeichnen(eintrag, loesung.werte || {})]),
    ...eigene.map((linie) => karte('M-N-Interaktionsdiagramm', [diagrammZeichnen(linie)])),
    ...querkraftkurven(loesung, kennung),
    ...neigungskurven(loesung, kennung),
    ...spannungskarten(kennung, loesung),
  ];
}

/** Die Spannung-Dehnung-Analysen eines Bauteils, je eine Karte. */
function spannungskarten(kennung, loesung) {
  return ((loesung.spannungsanalysen || {})[kennung] || []).map(spannungsfallZeichnen);
}

/**
 * Die Karten je Bauteilart (ARTEN, arten.js). Die Diagramme der
 * Querschnittsanalysen und der Balkensysteme kommen aus eigenen Anfragen,
 * siehe qa_diagramme.js und bs_diagramme.js; die Spannung-Dehnung-Analysen
 * eines Querschnitts kommen mit der Rechnung.
 */
const DIAGRAMME = {
  querschnitt: plattenkarten,
  querschnittsanalyse: (kennung, eintrag, loesung) => [
    ...analyseKarten(kennung), ...spannungskarten(kennung, loesung)],
  balkensystem: systemKarten,
  grundbruch: situationKarten,
};

/**
 * Was der Reiter «Diagramme» zeigt, in Gruppen: die Werkstoffgesetze und je
 * Bauteil seine Karten -- eingegrenzt wie die anderen Sichten.
 */
function diagrammgruppen(loesung) {
  const raum = eingrenzung();
  const gruppen = [];
  const gesetzkarten = Object.entries(loesung.werkstoffgesetze || {})
    .filter(([kennung, gesetz]) => imRaum(raum, `${gesetz.art}.${kennung}`))
    .map(([, gesetz]) => karte(`${gesetz.titel} – ${gesetz.name}`, [
      gesetz.referenz ? el('p.karte-hinweis', { text: gesetz.referenz }) : null,
      kurveZeichnen(gesetz, {
        zeigeVereinfacht: zustand.zeigeVereinfacht,
        beiUmschalten: (an) => aendern({ zeigeVereinfacht: an }, 'diagramm'),
      }),
    ]));
  if (gesetzkarten.length) {
    gruppen.push({ schluessel: 'werkstoffe', name: 'Werkstoffe', titel: 'Werkstoffgesetze',
      karten: gesetzkarten });
  }
  for (const art of ARTEN) {
    for (const [kennung, eintrag] of Object.entries(loesung.zuordnung?.[art.liste] || {})) {
      if (imRaum(raum, eintrag.namensraum)) {
        gruppen.push({ schluessel: kennung, name: eintrag.name,
          titel: `Diagramme – ${eintrag.name}`,
          karten: DIAGRAMME[art.art](kennung, eintrag, loesung) });
      }
    }
  }
  return gruppen;
}

/** Der Titel einer Karte, wie er in ihrem Kopf steht -- leer, wenn sie keinen hat. */
function kartentitel(k) {
  return k.querySelector(':scope > .unterkapitel-kopf > span')?.textContent || '';
}

/**
 * Die Diagramme, je eines gross (Benutzer, 2026-10-16). Zuoberst eine Leiste,
 * die quer rollt, mit einer kleinen Vorschau je Diagramm -- ein Knopf; der
 * gewählte steht darunter in voller Breite.
 *
 * Ein Diagramm ist jede Karte mit einem Bild. Die übrigen Karten eines
 * Bauteils -- die Wahl des Falls, ein Hinweis -- stehen über dem Diagramm,
 * das gross gezeigt wird, wenn es zu diesem Bauteil gehört. Hat ein Bauteil
 * (noch) kein Bild, bekommt es einen Knopf ohne Vorschau, der seine Hinweise
 * zeigt. Gemerkt wird die Wahl als Gruppe und Titel; fehlt dieser Titel,
 * gilt dieselbe Stelle in der Gruppe, sonst das erste Diagramm.
 */
function diagrammSicht(loesung) {
  const eintraege = [];
  for (const gruppe of diagrammgruppen(loesung)) {
    const bilder = gruppe.karten.filter((k) => k.querySelector('svg'));
    if (!bilder.length) {
      eintraege.push({ gruppe, karte: null, titel: 'ohne Bild', index: 0,
        schluessel: `${gruppe.schluessel}|` });
      continue;
    }
    const gesehen = {};
    bilder.forEach((k, index) => {
      const titel = kartentitel(k);
      const n = gesehen[titel] = (gesehen[titel] || 0) + 1;
      eintraege.push({ gruppe, karte: k, titel, index,
        schluessel: `${gruppe.schluessel}|${titel}|${n}` });
    });
  }
  if (!eintraege.length) return leerzustand('Noch nichts zu zeichnen.');

  const wahl = zustand.diagrammWahl;
  const gewaehlt = eintraege.find((e) => e.schluessel === wahl?.schluessel)
    || eintraege.find((e) => e.gruppe.schluessel === wahl?.gruppe && e.index === wahl?.index)
    || eintraege[0];
  const mitGruppe = new Set(eintraege.map((e) => e.gruppe.schluessel)).size > 1;
  const { gruppe } = gewaehlt;
  return stapel([
    vorschauleiste(eintraege, gewaehlt, mitGruppe),
    panel({ schluessel: `bericht/diagramm/${gruppe.schluessel}`, titel: gruppe.titel }, [
      ...gruppe.karten.filter((k) => !k.querySelector('svg')),
      gewaehlt.karte,
    ].filter(Boolean)),
  ], 'ist-diagramm');
}

/** Wie weit die Leiste gerollt war -- sie wird bei jedem Zeichnen neu gebaut. */
let leistenstand = 0;

function vorschauleiste(eintraege, gewaehlt, mitGruppe) {
  const leiste = el('div.vorschauleiste', {
    role: 'tablist', 'aria-label': 'Diagramme',
    on: { scroll: (ev) => { leistenstand = ev.target.scrollLeft; } },
  }, eintraege.map((e) => vorschauknopf(e, e === gewaehlt, mitGruppe)));
  // Erst wenn sie im Dokument steht, hat sie eine Breite: dann den alten
  // Stand wiederherstellen und den gewählten Knopf ins Bild holen.
  requestAnimationFrame(() => {
    leiste.scrollLeft = leistenstand;
    const aktiv = leiste.querySelector('.ist-gewaehlt');
    if (aktiv) {
      const links = aktiv.getBoundingClientRect().left - leiste.getBoundingClientRect().left
        + leiste.scrollLeft;
      if (links < leiste.scrollLeft) leiste.scrollLeft = links;
      else if (links + aktiv.offsetWidth > leiste.scrollLeft + leiste.clientWidth) {
        leiste.scrollLeft = links + aktiv.offsetWidth - leiste.clientWidth;
      }
    }
  });
  return leiste;
}

/** Ein Knopf der Leiste: die Vorschau -- eine verkleinerte Kopie des Bildes -- und der Titel. */
function vorschauknopf(e, aktiv, mitGruppe) {
  const bild = e.karte?.querySelector('svg')?.cloneNode(true);
  if (bild) {
    bild.removeAttribute('width');
    bild.removeAttribute('height');
    bild.removeAttribute('style');
    bild.setAttribute('aria-hidden', 'true');
  }
  const name = e.titel || e.gruppe.name;
  return el('button.vorschau', {
    type: 'button', role: 'tab', 'aria-selected': String(aktiv),
    class: aktiv ? 'ist-gewaehlt' : '',
    title: mitGruppe ? `${e.gruppe.name} – ${name}` : name,
    on: {
      click: () => aendern({
        diagrammWahl: { schluessel: e.schluessel, gruppe: e.gruppe.schluessel, index: e.index },
      }, 'diagramm'),
    },
  }, [
    el('span.vorschau-bild', {}, [bild || el('span.vorschau-leer', { text: '…' })]),
    mitGruppe ? el('span.vorschau-gruppe', { text: e.gruppe.name }) : null,
    el('span.vorschau-titel', { text: name }),
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

  return alle.map(([kennung, kurve]) => karte(`Querkraft über Moment – ${kurve.name}`, [
    querkraftkurveZeichnen(kurve),
    el('div.kurvenfuss', {}, [
      el('span.kurvenfuss-name', { text: 'gilt für N_Ed =' }),
      zahlfeld({
        wert: kurve.N_Ed, schritt: 50,
        titel: 'N in kN, Zug positiv. Nur Punkte mit genau diesem N liegen auf der Kurve.',
        leer: 0,
        beiAenderung: (v) => normalkraftWaehlen(kennung, v),
      }),
      el('span.einheit', { text: 'kN' }),
      el('span.kurvenhinweis', {
        text: 'Blass: Punkte mit anderem N.',
      }),
    ]),
  ]));
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

  return alle.map(([, kurve]) => karte(`Querkraft über Neigung – ${kurve.name}`, [
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
  ]));
}

/**
 * Der Namensraum des links gewählten Bestandteils -- `beton.b1`,
 * `querschnitt.q1`, `querschnittsanalyse.a1`. Null, wenn nichts gewählt ist.
 * Bauteile heissen im Rechenwerk wie ihre Art in der Auswahl (ARTEN).
 */
function raumDerAuswahl() {
  const wahl = zustand.auswahl;
  if (!wahl) return null;
  if (wahl.art === 'material') {
    const m = zustand.projekt.materialien.find((x) => x.kennung === wahl.kennung);
    return m ? namensraum(m.art, m.kennung) : null;
  }
  return namensraum(wahl.art, wahl.kennung);
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

/** «Aktuelle Seite», aber links nichts gewählt: der Hinweis dazu, sonst null. */
function ohneAuswahl() {
  return zustand.umfang === 'seite' && !raumDerAuswahl()
    ? leerzustand('Nichts ausgewählt.', 'Links Bestandteil wählen oder oben «Gesamt».')
    : null;
}

/** Gehört etwas mit diesem Namensraum in die Ansicht? */
function imRaum(raum, id) {
  return !raum || id === raum || id.startsWith(`${raum}.`);
}

// ===========================================================================

export function berichtZeichnen(behaelter, { verfolgen }) {
  const loesung = zustand.loesung;
  const sichten = {
    nachweise: () => zusammenfassung(loesung, verfolgen),
    diagramm: () => diagrammSicht(loesung),
    herleitung: () => herleitung(loesung),
  };
  const sicht = sichten[zustand.reiter] || sichten.nachweise;
  // Liess sich die letzte Eingabe nicht rechnen, steht es über allem: was
  // darunter steht, gehört zur Eingabe davor.
  const fehler = zustand.rechenfehler
    ? el('div.hinweis.hinweis-warnung', {}, [
      el('b', { text: 'Nicht gerechnet: ' }), zustand.rechenfehler,
      loesung ? ' Darunter steht das Ergebnis zur Eingabe davor.' : '',
    ])
    : null;
  if (!loesung) {
    return ersetzen(behaelter, fehler, leerzustand('Noch nichts gerechnet.', 'Oben «Rechnen».'));
  }
  return ersetzen(behaelter, fehler, sicht());
}
