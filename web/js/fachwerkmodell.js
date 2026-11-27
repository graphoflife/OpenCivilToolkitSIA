/**
 * fachwerkmodell.js -- Mittlere Tafel: Eingaben eines Fachwerkmodells, und was rechts von ihm steht.
 *
 * Oben die Scheibe: Bezeichnung, Zeichnung samt Liste, Beschreibung.
 * Darunter die Kachel «Verfahren»: ihre Felder kommen aus dem Kern
 * (`katalog.vorgaben`, opencivil/fachwerkmodell/suche.py), dazu der Knopf,
 * der ein Fachwerk sucht, und wie weit die Suche ist (fw_suche.js).
 *
 * Rechts im Reiter «Diagramme» das Modell als Bild, darin das Fachwerk --
 * während der Suche das der letzten Runde --, in der Zusammenfassung seine
 * Stäbe, die Lager mit ihren Kräften und die Lasten. Gerechnet wird im Kern
 * (opencivil/fachwerkmodell); hier stehen nur seine Zahlen.
 */

import {
  beschreibung, bezeichnung, eingabegruppen, erklaerung, karte, meldungshinweise, panel, tabelle,
} from './bausteine.js';
import { zahlText } from './cad_ansicht.js';
import { listengruppen, listenzeilen, meldungsliste } from './cad_app.js';
import { el, leerzustand } from './dom.js';
import { fachwerkLegende, scheibeBild } from './fw_bild.js';
import {
  anhalten, gezeigtesFachwerk, sucheLaeuft, sucheVon, suchen,
} from './fw_suche.js';
import { zeichenbereich } from './fw_zeichnung.js';
import { gruppenkapitel, kapitelFenster, kapitelPanel } from './kapitel.js';
import {
  eintragAendern, eintragVon, katalog, zustand,
} from './zustand.js';

const HILFE = {
  zeilen: [
    ['Achsen', 'x nach rechts, y nach oben, in m; Lasten in kN'],
    ['Scheibe', 'ein Umriss aus Ecken – liegen mehrere da, ist Material, wo eine von ihnen ist'],
    ['Loch', 'in seinem Innern ist kein Material, auf seinem Rand schon'],
    ['Lager', 'an einem Knoten, am Rand oder innen: fest in x und y, nur in x oder nur in y – zusammen halten sie die Scheibe, so dass sie sich weder verschieben noch drehen kann'],
    ['Last', 'eine Punktlast an einem Knoten, in jeder Richtung: F_h nach rechts, F_v nach unten positiv'],
    ['Material', 'keines und keine Dicke: ohne Bemessung hängen Fachwerk und Kräfte nur von Form, Lagern und Lasten ab'],
  ],
  verfahren: {
    zeilen: [
      ['Ground Structure', 'Knoten in einem Raster über der Scheibe, dazu die Punkte der Lager und Lasten und die Ecken – je zwei Knoten ein möglicher Stab, wenn er ganz im Material liegt'],
      ['Optimierung', 'wählt unter den Fachwerken im Gleichgewicht das mit dem kleinsten V; Runde um Runde kommen die Stäbe dazu, die V noch senken'],
      ['Live', 'nach jeder Runde zeigt das Bild rechts das Fachwerk dieser Runde – «Anhalten» übernimmt es, so wie es ist'],
      ['Ergebnis', 'Zug rot, Druck blau und gestrichelt; zwei Stäbe in einer Flucht durch einen Knoten ohne Last und Lager werden einer'],
    ],
    formel: 'V = Σ l · (w_Z · N⁺ + w_D · N⁻) → min,  w_D = 1',
  },
};

/** Wie ein Lager hält, in Worten des Kerns: «x und y», «nur x». */
const haltText = (halt) => katalog('fachwerkmodell', 'halt').find((h) => h.wert === halt)?.beschriftung ?? halt;

/** Wo ein Knoten liegt, «(2.00, 3.00)» in m -- leer, wenn es ihn nicht gibt. */
function ortText(modell, knoten) {
  const k = modell.knoten.find((x) => x.kennung === knoten);
  return k ? `(${zahlText(k.x, 2)}, ${zahlText(k.y, 2)})` : '';
}

/** «F_h = 50.0 kN · F_v = 200.0 kN»: eine Last, wie sie eingegeben ist. */
const lastText = (f) => `F_h = ${zahlText(f.F_h, 1)} kN · F_v = ${zahlText(f.F_v, 1)} kN`;

/** «(2.00, 3.00)»: ein Knoten des Fachwerks, in m. */
const punktText = (p) => `(${zahlText(p.x, 2)}, ${zahlText(p.y, 2)})`;

/** «1 Stab», «36 Stäbe». */
const staebeText = (n) => `${n} ${n === 1 ? 'Stab' : 'Stäbe'}`;

/** Was die letzte Rechnung zu einem Fachwerkmodell zeichnet -- oder null. */
const zeichendaten = (kennung) => zustand.loesung?.zeichendaten?.[kennung] || null;

// ===========================================================================
// Unter der Zeichnung
// ===========================================================================

/** Meldungen des Kerns und je Teil eine Zeile (cad_app.js): ein Klick wählt im Fenster, Lager und Last über ihren Knoten. */
function liste(a) {
  const z = eintragVon(a.fw.kennung);
  if (!z) return [];
  const zeile = (kennung, was, wert = '') => listenzeilen(a)({ kennung, was, wert });
  const ecken = (u) => `${u.knoten.length} Ecken`;
  return [
    meldungsliste(a),
    ...listengruppen(a, [
      ['Scheiben', z.scheiben.map((s) => zeile(s.kennung, ecken(s)))],
      ['Löcher', z.loecher.map((l) => zeile(l.kennung, ecken(l)))],
      ['Lager', z.lager.map((l) => zeile(l.kennung, `an ${l.knoten}`, `hält ${haltText(l.halt)}`))],
      ['Lasten', z.lasten.map((f) => zeile(f.kennung, `an ${f.knoten}`, lastText(f)))],
    ]),
  ];
}

// ===========================================================================
// Die Scheibe
// ===========================================================================

function scheibeGruppe(modell) {
  const aendern = (veraenderer) => eintragAendern(modell.kennung, veraenderer);
  return panel({
    schluessel: 'fachwerkmodell/Scheibe', titel: 'Scheibe', zusatz: 'x nach rechts, y nach oben, m', breit: true,
  }, [
    bezeichnung(modell, aendern, erklaerung(HILFE.zeilen)),
    zeichenbereich(modell, liste),
    el('div.unterkapitel', {}, [beschreibung(modell, aendern)]),
  ]);
}

// ===========================================================================
// Das Verfahren und die Suche
// ===========================================================================

/** Was der Kachel noch fehlt, je Stand des Fachwerks (fachwerkdaten.py, `uebersicht`). */
const FEHLT = {
  '': 'Modell unfertig', keines: 'noch nicht gesucht', veraltet: 'neu zu suchen', unlesbar: 'neu zu suchen',
};

/**
 * Wie weit die Suche ist oder was sie fand, in einer Zeile: «Runde 7: 320
 * von 1528 möglichen Stäben im Modell, 4 kommen dazu – 36 Stäbe, V = 3662.5
 * kNm.», danach «Gefunden nach 20 Runden: …» oder «Angehalten nach Runde 7: …».
 */
function standText(g) {
  const was = `${staebeText(g.fachwerk.staebe.length)}, V = ${zahlText(g.fachwerk.V, 1)} kNm`;
  if (g.laeuft) {
    return `Runde ${g.runden}: ${g.im_modell} von ${g.moeglich} möglichen Stäben im Modell`
      + `${g.dazu ? `, ${g.dazu} kommen dazu` : ''} – ${was}.`;
  }
  if (!g.fertig) return `Angehalten nach Runde ${g.runden}: ${was}.`;
  return `Gefunden nach ${g.runden} ${g.runden === 1 ? 'Runde' : 'Runden'}: ${was}.`;
}

/**
 * Was zur Suche zu sagen ist, im Fenster und auf den Karten rechts: wie weit
 * sie ist oder was sie fand und was der Kern dazu meldet -- warum sie nicht
 * beginnen konnte, solange das Modell dasselbe ist, oder dass noch keines
 * gesucht ist.
 */
function suchzeilen(kennung, daten) {
  const s = sucheVon(kennung);
  if (s?.fehler) return [el('p.hinweis.hinweis-warnung', { text: `Die Suche brach ab: ${s.fehler}` })];
  const a = s?.antwort;
  if (s && !s.laeuft && a && !a.fachwerk && a.abdruck && a.abdruck === daten?.abdruck) {
    return meldungshinweise(a.meldungen);
  }
  const g = gezeigtesFachwerk(kennung, daten);
  if (g) return [el('p.fw-suchstand', { text: standText(g) }), ...meldungshinweise(g.meldungen)];
  if (s?.laeuft) return [el('p.fw-suchstand', { text: 'Runde 1: Raster und mögliche Stäbe werden gelegt …' })];
  return meldungshinweise(daten?.zum_fachwerk);
}

/** Der Knopf, der sucht -- während der Suche mit laufendem Balken --, daneben «Anhalten». */
function suchleiste(modell, daten) {
  const s = sucheVon(modell.kennung);
  const laeuft = Boolean(s?.laeuft);
  const anderes = sucheLaeuft() && !laeuft;
  const bereit = Boolean(daten?.bereit);
  const titel = laeuft ? 'Sucht Runde um Runde, bis keine Stäbe mehr dazukommen'
    : anderes ? 'Es sucht schon ein anderes Fachwerkmodell'
      : bereit ? 'Sucht Runde um Runde, bis keine Stäbe mehr dazukommen'
        : 'Erst, wenn das Modell vollständig ist – was fehlt, steht unter der Zeichnung';
  return el('div.fw-suchleiste', {}, [
    el('button.knopf.knopf-haupt', {
      type: 'button', class: laeuft ? 'ist-am-suchen' : '', title: titel,
      disabled: laeuft || anderes || !bereit,
      on: { click: () => suchen(modell.kennung) },
    }, laeuft ? [el('span.laufbalken'), el('span', { text: 'sucht …' })]
      : [el('span', { text: 'Fachwerk suchen' })]),
    laeuft ? el('button.knopf', {
      type: 'button', text: s.anhalten ? 'hält an …' : 'Anhalten', disabled: s.anhalten,
      title: 'Nach dieser Runde anhalten – ihr Fachwerk wird übernommen', on: { click: anhalten },
    }) : null,
  ]);
}

/** Die Kachel «Verfahren»: die Felder des Kerns, darunter Knopf und Stand der Suche. */
function kapitel(modell) {
  const aendern = (veraenderer) => eintragAendern(modell.kennung, veraenderer);
  const vorgaben = eingabegruppen('fachwerkmodell', modell, aendern);
  const daten = zeichendaten(modell.kennung);
  const s = sucheVon(modell.kennung);
  const runde = s?.laeuft ? `sucht, Runde ${s.antwort?.stand?.runde ?? 1}` : '';
  const kacheln = [gruppenkapitel(vorgaben, 'Verfahren', {
    zeichen: 'fw-verfahren', hilfe: HILFE.verfahren, werte: ['rasterweite'],
    wort: runde || 'Ground Structure', fehlt: runde || !daten ? '' : FEHLT[daten.stand] ?? '',
    nach: [el('div.fw-suche', {}, [suchleiste(modell, daten), ...suchzeilen(modell.kennung, daten)])],
  })];
  vorgaben.vollstaendig();
  return [{ titel: '', kapitel: kacheln.filter(Boolean) }];
}

export function fachwerkEditor(modell) {
  return [scheibeGruppe(modell),
    kapitelPanel(modell, kapitel(modell), { schluessel: 'fachwerkmodell/Eingaben', titel: 'Eingaben' })];
}

/** Das offene Fenster eines Fachwerkmodells -- oder null. */
export function fachwerkFenster(modell, schluessel) {
  return kapitelFenster(modell, kapitel(modell), schluessel);
}

// ===========================================================================
// Rechts: Diagramme und Zusammenfassung
// ===========================================================================

/** Ein frisches Modell, in Diagrammen und Zusammenfassung gleich. */
function ohneScheibe() {
  return karte(null, [leerzustand('Noch keine Scheibe.', 'Zeichnen im Fenster mit «Scheibe».')]);
}

/**
 * Die Karte eines Fachwerkmodells im Reiter «Diagramme»: das Modell als
 * Bild, darin das Fachwerk, das gilt (fw_suche.js) -- darüber, was der Kern
 * meldet und wie weit die Suche ist. Das Panel darum baut bericht.js.
 */
export function fachwerkKarten(kennung) {
  const modell = eintragVon(kennung);
  if (!modell?.scheiben.length) return [ohneScheibe()];
  const daten = zeichendaten(kennung);
  const g = gezeigtesFachwerk(kennung, daten);
  const bild = scheibeBild(modell, g?.fachwerk);
  return [karte(g ? 'Fachwerk' : 'Scheibe', [
    ...meldungshinweise(daten?.meldungen), ...suchzeilen(kennung, daten),
    el('div.gb-bildhuelle', {}, [bild]), g ? fachwerkLegende() : null,
  ].filter(Boolean), { bild, klasse: 'ist-breit' })];
}

/** Die Stäbe des Fachwerks, nach der Grösse ihrer Kraft, wie der Kern sie ordnet. */
function staebeKarte(fachwerk) {
  const k = fachwerk.knoten;
  return karte(staebeText(fachwerk.staebe.length), [tabelle(['Stab', 'von [m]', 'bis [m]', 'l [m]', 'N [kN]', ''],
    fachwerk.staebe.map((s, i) => [String(i + 1), punktText(k[s.von]), punktText(k[s.bis]), zahlText(s.l, 2),
      zahlText(s.N, 1), s.N > 0 ? 'Zug' : 'Druck']))]);
}

/** Die Lager, wie sie eingegeben sind -- mit Fachwerk auch, was sie aufnehmen. */
function lagerKarte(modell, fachwerk) {
  const kraft = new Map((fachwerk?.lagerkraefte || []).map((r) => [r.lager, r]));
  const kopf = ['Lager', 'Ort [m]', 'hält', ...(fachwerk ? ['R_x [kN] →', 'R_y [kN] ↑'] : [])];
  return karte('Lager', [tabelle(kopf, modell.lager.map((l) => {
    const r = kraft.get(l.kennung);
    const zeile = [l.kennung, ortText(modell, l.knoten), haltText(l.halt)];
    return fachwerk ? [...zeile, r ? zahlText(r.R_x, 1) : '–', r ? zahlText(r.R_y, 1) : '–'] : zeile;
  }))]);
}

/**
 * Die Zusammenfassung eines Fachwerkmodells: was der Kern meldet, wie weit
 * die Suche ist, die Stäbe des Fachwerks, die Lager mit ihren Kräften und
 * die Lasten, wie sie eingegeben sind. Das Panel darum baut bericht.js.
 */
export function fachwerkZusammenfassung(kennung) {
  const modell = eintragVon(kennung);
  const daten = zeichendaten(kennung);
  if (!modell?.scheiben.length) return [ohneScheibe()];
  if (!daten) return [karte(null, [leerzustand('Noch nicht gerechnet.')])];
  const g = gezeigtesFachwerk(kennung, daten);
  const zeilen = [...meldungshinweise(daten.meldungen), ...suchzeilen(kennung, daten)];
  return [
    zeilen.length ? karte('Fachwerk', zeilen) : null,
    g ? staebeKarte(g.fachwerk) : null,
    modell.lager.length ? lagerKarte(modell, g?.fachwerk) : null,
    modell.lasten.length ? karte('Lasten', [tabelle(['Last', 'Ort [m]', 'F_h [kN] →', 'F_v [kN] ↓'],
      modell.lasten.map((f) => [f.kennung, ortText(modell, f.knoten), zahlText(f.F_h, 1), zahlText(f.F_v, 1)]))])
      : null,
  ].filter(Boolean);
}
