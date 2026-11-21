/**
 * erdbeben.js -- Mittlere Tafel: Eingaben eines Gebäudes im Erdbeben.
 *
 * Von oben nach unten:
 *
 *     Erdbeben Gebäude    Bezeichnung; Standort und Bauwerk, Verhaltensbeiwert,
 *                         Grundschwingzeit und Regelmässigkeit je als Karte;
 *                         Beschreibung
 *     Geschosse           von unten nach oben: Höhe, G_k, Q_k und ψ₂
 *     Wände               je eine oder mehrere gleiche: Querschnittsanalyse,
 *                         Lage im Grundriss, Anzahl und η_EI
 *
 * Gerechnet wird nichts: die Kräfte stehen rechts in der Zusammenfassung und
 * im Bild unter «Diagramme». Felder, Zeichen, Einheiten und Grenzen kommen
 * aus dem Katalog (`katalog.vorgaben`, `katalog.felder`), die Stellungen der
 * Schalter und die Kriterien der Regelmässigkeit ebenso
 * (`katalog.erdbeben`, opencivil/erdbeben/ersatzkraft.py). Warum eine Wand
 * nicht rechnet, sagt der Kern an ihr (`zeichendaten`,
 * opencivil/web/erdbebendaten.py).
 */

import {
  bauteilliste, bezeichnung, eingabekarten, erklaerung, karte, mitBild, panel,
  vorgabefelder, vorgabetitel, wahlBlock, wahlSchalter,
} from './bausteine.js';
import { el, zahlfeld } from './dom.js';
import { anfuegenKnopf, fallkopf, fallzeile } from './faelle.js';
import {
  ausVorlage, eintragAendern, feldangabe, istSandbox, katalog, zustand,
} from './zustand.js';

const HILFE = {
  gebaeude: {
    zeilen: [
      ['Zone', 'die Erdbebenzone des Standorts – sie gibt a_gd (16.2.1)'],
      ['Baugrund', 'die Klasse A bis E – sie gibt S, T_B, T_C und T_D (Tabelle 24); für F '
        + 'braucht es eine Standortstudie'],
      ['BWK', 'die Bauwerksklasse I bis III – sie gibt γ_f (Tabelle 25)'],
      ['q', 'der Verhaltensbeiwert je Richtung: wie duktil das Tragwerk ist'],
      ['T₁', 'aus der Auslenkung der Wände (40) oder von Hand'],
      ['regelmässig', 'nur dann gilt das Ersatzkraftverfahren (16.5.2.1), sonst das '
        + 'Antwortspektrenverfahren (16.5.3.1)'],
    ],
    formel: 'F_d = S_d(T₁)·ΣW',
  },
  geschosse: {
    zeilen: [
      ['Folge', 'von unten nach oben, ab der Einspannung – bei steifen Untergeschossen darf sie '
        + 'auf dem Erdgeschoss liegen (16.5.1.7)'],
      ['W', 'das Gewicht des Geschosses, G_k + ψ₂·Q_k: es wirkt auf der Höhe seiner Decke'],
    ],
    formel: 'F_d,i = z_i·W_i / Σ z_j·W_j · F_d',
  },
  waende: {
    zeilen: [
      ['Querschnitt', 'aus einer Querschnittsanalyse des Projekts: I_y, I_z und E_cm ihres Betons'],
      ['Lage', '0°: y der Analyse liegt in x des Gebäudes, 90°: in y'],
      ['η_EI', 'der Anteil der ungerissenen Biegesteifigkeit, der gilt'],
      ['Verteilung', 'jede Wand trägt nach ihrem Anteil an EI – nach Vorgabe, nicht nachgeschlagen'],
    ],
    formel: 'EI = n·η_EI·E_cm·I',
  },
};

/** Ein Schalter für eine Wahl des Gebäudes -- die Stellungen aus dem Katalog. */
function wahl(h, aendern, liste, feldname, titel, werte = katalog('erdbeben', liste)) {
  return wahlSchalter({
    werte, gewaehlt: h[feldname], titel,
    setzen: (w) => aendern((x) => { x[feldname] = w; }),
  });
}

/**
 * Grund- oder Aufriss: ja oder nein, darunter, was «ja» heisst -- in
 * eigenen Worten aus dem Kern. Nein: das Verfahren gilt nicht.
 */
function regelmaessigkeit(h, aendern, r) {
  return el('div.eb-regel', {}, [
    wahlBlock(`${r.beschriftung} (${r.ziffer})`, wahl(h, aendern, null, r.feld,
      'Nein: das Ersatzkraftverfahren gilt nicht – Antwortspektrenverfahren (16.5.3.1)',
      [{ wert: true, beschriftung: 'ja' }, { wert: false, beschriftung: 'nein' }])),
    el('ul.eb-kriterien', {}, r.kriterien.map((text) => el('li', { text }))),
  ]);
}

function gebaeudePanel(h) {
  const aendern = (veraenderer) => eintragAendern(h.kennung, veraenderer);
  return panel({
    schluessel: 'erdbeben/Gebäude', titel: 'Erdbeben Gebäude',
    zusatz: erklaerung(HILFE.gebaeude.zeilen, HILFE.gebaeude.formel),
  }, [
    el('div.unterkapitel', {}, [bezeichnung(h, aendern)]),
    karte('Standort und Bauwerk', [
      wahlBlock('Erdbebenzone', wahl(h, aendern, 'zonen', 'zone', 'Die Zone des Standorts')),
      wahlBlock('Baugrundklasse', wahl(h, aendern, 'baugrund', 'baugrund',
        'Die Klasse des Baugrunds unter dem Gebäude')),
      wahlBlock('Bauwerksklasse', wahl(h, aendern, 'bauwerksklassen', 'bauwerksklasse',
        'Wie wichtig das Gebäude nach einem Beben ist')),
    ]),
    ...eingabekarten('erdbeben', h, aendern, {
      dazu: {
        Grundschwingzeit: {
          vor: [wahl(h, aendern, 'schwingzeiten', 'schwingzeit', 'Woher die Grundschwingzeit T₁ kommt')],
        },
      },
    }),
    karte('Regelmässigkeit', katalog('erdbeben', 'regelmaessigkeit')
      .map((r) => regelmaessigkeit(h, aendern, r))),
    el('div.unterkapitel', {}, [
      el('div.beschreibung', {}, [
        el('label', { text: 'Beschreibung' }),
        el('textarea', {
          rows: 2, value: h.beschreibung || '',
          on: { change: (e) => aendern((x) => { x.beschreibung = e.target.value; }) },
        }),
      ]),
    ]),
  ]);
}

/** Die Zahlen einer Zeile, je ein Feld der Vorgaben von `klasse`. */
function zahlen(klasse, teil, aendern) {
  return vorgabefelder(klasse, teil).map((f) => zahlfeld({
    wert: teil[f.feld], schritt: f.schritt, angabe: feldangabe(klasse, f.feld),
    titel: vorgabetitel(f), beiAenderung: (v) => aendern((x) => { x[f.feld] = v; }),
  }));
}

/** Die Köpfe der Spalten: je Feld der Vorgaben sein Zeichen und die Einheit des Kerns. */
function koepfe(klasse, teil) {
  return vorgabefelder(klasse, teil).map((f) => [f.zeichen, feldangabe(klasse, f.feld).einheit]);
}

function geschossZeile(h, i) {
  const geschoss = h.geschosse[i];
  const aendern = (veraenderer) => eintragAendern(h.kennung, (x) => veraenderer(x.geschosse[i]));
  return fallzeile({
    fall: geschoss, aendern, nameTitel: 'Bezeichnung des Geschosses',
    vorn: el('span.schicht-nummer', { text: String(i + 1), title: `${i + 1}. Geschoss über der Einspannung` }),
    zahlen: zahlen('geschoss', geschoss, aendern),
    entfernenTitel: 'Geschoss entfernen',
    entfernen: () => eintragAendern(h.kennung, (x) => { x.geschosse.splice(i, 1); }),
  });
}

function geschossePanel(h) {
  return panel({
    schluessel: 'erdbeben/Geschosse', titel: 'Geschosse',
    zusatz: erklaerung(HILFE.geschosse.zeilen, HILFE.geschosse.formel),
  }, [
    el('div.unterkapitel', {}, [
      h.geschosse.length
        ? [el('div.eb-folge', { text: 'Von unten nach oben, ab der Einspannung' }),
          fallkopf(koepfe('geschoss', h.geschosse[0]))]
        : el('div.leer', { text: 'Noch kein Geschoss – ohne Geschoss keine Ersatzkraft.' }),
      ...h.geschosse.map((_, i) => geschossZeile(h, i)),
      anfuegenKnopf('Geschoss', (name) => eintragAendern(h.kennung, (x) => {
        x.geschosse.push(ausVorlage('geschoss', { name: name(x.geschosse) }));
      })),
    ].flat()),
  ]);
}

/**
 * Was der Kern zu einer Wand sagt -- nur, wenn es zu ihrer jetzigen
 * Querschnittsanalyse gehört: nach einer anderen Wahl gilt es nicht mehr.
 */
function wandmeldung(h, i) {
  const m = zustand.loesung?.zeichendaten?.[h.kennung]?.waende?.[i];
  if (!m || m.analyse !== h.waende[i].analyse) return null;
  return el('div.qa-meldung', { text: `${m.grund[0].toUpperCase()}${m.grund.slice(1)}.`, class: m.fehler ? '' : 'ist-hinweis' });
}

function wandZeile(h, i) {
  const wand = h.waende[i];
  const aendern = (veraenderer) => eintragAendern(h.kennung, (x) => veraenderer(x.waende[i]));
  return fallzeile({
    fall: wand, aendern, nameTitel: 'Bezeichnung der Wand', spalten: 4,
    vorn: el('span.schicht-nummer', { text: String(i + 1), title: `Wand ${i + 1}` }),
    zahlen: zahlen('tragwand', wand, aendern),
    unten: [
      wahlBlock('Querschnittsanalyse', bauteilliste({
        alle: zustand.projekt.querschnittsanalysen || [], gewaehlt: wand.analyse,
        inSandbox: istSandbox(h.kennung),
        titel: 'Die Querschnittsanalyse der Wand: I_y, I_z und E_cm ihres Betons',
        setzen: (v) => aendern((x) => { x.analyse = v; }),
      })),
      wahlBlock('Lage im Grundriss', wahlSchalter({
        werte: mitBild(katalog('erdbeben', 'lagen'), 'wandlage'), gewaehlt: wand.lage,
        titel: 'Wie die Wand im Grundriss liegt – y und z ihrer Querschnittsanalyse gegen x und y',
        setzen: (v) => aendern((x) => { x.lage = v; }),
      })),
      wandmeldung(h, i),
    ].filter(Boolean),
    entfernenTitel: 'Wand entfernen',
    entfernen: () => eintragAendern(h.kennung, (x) => { x.waende.splice(i, 1); }),
  });
}

function waendePanel(h) {
  return panel({
    schluessel: 'erdbeben/Wände', titel: 'Wände',
    zusatz: erklaerung(HILFE.waende.zeilen, HILFE.waende.formel),
  }, [
    el('div.unterkapitel', {}, [
      h.waende.length
        ? fallkopf(koepfe('tragwand', h.waende[0]), { spalten: 4 })
        : el('div.leer', { text: 'Noch keine Wand – ohne Wand gilt nur T₁ von Hand, und die Kräfte bleiben ohne Verteilung.' }),
      ...h.waende.map((_, i) => wandZeile(h, i)),
      anfuegenKnopf('Wand', (name) => eintragAendern(h.kennung, (x) => {
        x.waende.push(ausVorlage('tragwand', { name: name(x.waende) }));
      })),
    ]),
  ]);
}

export function erdbebenEditor(h) {
  return [gebaeudePanel(h), geschossePanel(h), waendePanel(h)];
}
