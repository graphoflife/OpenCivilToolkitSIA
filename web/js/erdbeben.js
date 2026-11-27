/**
 * erdbeben.js -- Mittlere Tafel: Eingaben eines Gebäudes im Erdbeben.
 *
 * Von oben nach unten:
 *
 *     Gebäude    Bezeichnung und Beschreibung
 *     Eingaben   je eine Kachel mit Sinnbild und dem Wichtigsten
 *                (Benutzer, 2026-11-25), ein Klick öffnet ihr Fenster:
 *                Standort und Bauwerk, Verhaltensbeiwert, Grundschwingzeit,
 *                Regelmässigkeit, die Geschosse -- Höhe, G_k, Q_k und ψ₂ --
 *                und je Geschoss sein Kern: eine Querschnittsanalyse mit
 *                allen Wänden in x und in y, dazu η_EI
 *
 * Beide Listen stehen von oben nach unten, wie das Gebäude: das Dach oben,
 * das unterste Geschoss zuunterst (Benutzer, 2026-11-27; bis dahin von unten
 * nach oben). Gezählt wird weiter ab der Einspannung, das unterste ist 1.
 * Ein neues Geschoss kommt oben dazu und übernimmt Kern und η_EI des
 * obersten: wer aufstockt, baut meist auf demselben Kern weiter.
 *
 * Gerechnet wird nichts: die Kräfte stehen rechts in der Zusammenfassung und
 * im Bild unter «Diagramme». Felder, Zeichen, Einheiten und Grenzen kommen
 * aus dem Katalog (`katalog.vorgaben`, `katalog.felder`), die Stellungen der
 * Schalter und die Kriterien der Regelmässigkeit ebenso
 * (`katalog.erdbeben`, opencivil/erdbeben/ersatzkraft.py). Warum der Kern
 * eines Geschosses nicht rechnet, sagt der Kern der Software an ihm
 * (`zeichendaten`, opencivil/web/erdbebendaten.py).
 */

import {
  bauteilliste, beschreibung, bezeichnung, eingabegruppen, karte, panel, vorgabefelder,
  vorgabetitel, wahlBlock, wahlSchalter,
} from './bausteine.js';
import { el, zahlfeld } from './dom.js';
import { anfuegenKnopf, fallkopf, fallzeile } from './faelle.js';
import {
  gruppenkapitel, kapitelFenster, kapitelPanel, standOhne, zeilenstand,
} from './kapitel.js';
import {
  ausVorlage, eintragAendern, feldangabe, istSandbox, katalog, zustand,
} from './zustand.js';

const HILFE = {
  standort: {
    zeilen: [
      ['Zone', 'die Erdbebenzone des Standorts – sie gibt a_gd (16.2.1)'],
      ['Baugrund', 'die Klasse A bis E – sie gibt S, T_B, T_C und T_D (Tabelle 24); für F '
        + 'braucht es eine Standortstudie'],
      ['BWK', 'die Bauwerksklasse I bis III – sie gibt γ_f (Tabelle 25)'],
    ],
    formel: 'F_d = S_d(T₁)·ΣW',
  },
  verhalten: {
    zeilen: [['q', 'der Verhaltensbeiwert je Richtung: wie duktil das Tragwerk ist']],
  },
  schwingzeit: {
    zeilen: [['T₁', 'aus der Auslenkung des Kerns (40) oder von Hand']],
  },
  regelmaessigkeit: {
    zeilen: [['regelmässig', 'nur dann gilt das Ersatzkraftverfahren (16.5.2.1), sonst das '
      + 'Antwortspektrenverfahren (16.5.3.1)']],
  },
  geschosse: {
    zeilen: [
      ['Folge', 'von oben nach unten, wie das Gebäude; gezählt ab der Einspannung – bei steifen '
        + 'Untergeschossen darf sie auf dem Erdgeschoss liegen (16.5.1.7)'],
      ['W', 'das Gewicht des Geschosses, G_k + ψ₂·Q_k: es wirkt auf der Höhe seiner Decke'],
      ['Neu', 'ein neues Geschoss kommt oben dazu, mit Kern und η_EI des obersten'],
    ],
    formel: 'F_d,i = z_i·W_i / Σ z_j·W_j · F_d',
  },
  kern: {
    zeilen: [
      ['Kern', 'je Geschoss eine Querschnittsanalyse des Projekts: der ganze Kern mit allen '
        + 'Wänden in x und in y, gezeichnet, wie er im Grundriss liegt – y der Analyse in x des '
        + 'Gebäudes, z in y; der Beton gibt E_cm'],
      ['Teile', 'Wände, die keine Kante teilen, biegen sich je um ihren eigenen Schwerpunkt: '
        + 'ihre I zählen ohne Steiner-Anteil – nach Vorgabe, nicht nachgeschlagen'],
      ['η_EI', 'der Anteil der ungerissenen Biegesteifigkeit, der gilt'],
      ['Verteilung', 'am Fuss trägt jeder Teil nach seinem Anteil an I – nach Vorgabe, nicht '
        + 'nachgeschlagen'],
    ],
    formel: 'EI_i = η_EI,i·E_cm,i·I_i',
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

function kopfPanel(h) {
  const aendern = (veraenderer) => eintragAendern(h.kennung, veraenderer);
  return panel({ schluessel: 'erdbeben/Gebäude', titel: 'Gebäude' }, [
    el('div.unterkapitel', {}, [bezeichnung(h, aendern), beschreibung(h, aendern)]),
  ]);
}

/** Das Wort einer Stellung, wie der Katalog es nennt: «Z2», «aus dem Kern». */
function wortVon(liste, wert) {
  return katalog('erdbeben', liste).find((w) => w.wert === wert)?.beschriftung || '';
}

/** Zone, Baugrund und Bauwerksklasse: je ein Schalter. */
const STANDORT = {
  schluessel: 'standort',
  name: 'Standort und Bauwerk', titel: 'Standort und Bauwerk',
  hilfe: HILFE.standort,
  inhalt: (h) => {
    const aendern = (veraenderer) => eintragAendern(h.kennung, veraenderer);
    return [karte('', [
      wahlBlock('Erdbebenzone', wahl(h, aendern, 'zonen', 'zone', 'Die Zone des Standorts')),
      wahlBlock('Baugrundklasse', wahl(h, aendern, 'baugrund', 'baugrund',
        'Die Klasse des Baugrunds unter dem Gebäude')),
      wahlBlock('Bauwerksklasse', wahl(h, aendern, 'bauwerksklassen', 'bauwerksklasse',
        'Wie wichtig das Gebäude nach einem Beben ist')),
    ])];
  },
  stand: (h) => ({
    an: true,
    text: `Zone ${wortVon('zonen', h.zone)}, Baugrund ${wortVon('baugrund', h.baugrund)}, `
      + `BWK ${wortVon('bauwerksklassen', h.bauwerksklasse)}`,
  }),
};

/**
 * Grund- und Aufriss, je ja oder nein. Ist einer nicht regelmässig, gilt
 * das Ersatzkraftverfahren nicht: die Kachel sagt es grau.
 */
const REGELMAESSIGKEIT = {
  schluessel: 'regelmaessigkeit',
  name: 'Regel\u00admässigkeit', titel: 'Regelmässigkeit',
  hilfe: HILFE.regelmaessigkeit,
  inhalt: (h) => {
    const aendern = (veraenderer) => eintragAendern(h.kennung, veraenderer);
    return [karte('', katalog('erdbeben', 'regelmaessigkeit')
      .map((r) => regelmaessigkeit(h, aendern, r)))];
  },
  stand: (h) => {
    const nicht = katalog('erdbeben', 'regelmaessigkeit').find((r) => !h[r.feld]);
    return nicht ? { an: false, text: `${nicht.beschriftung}: nein` }
      : { an: true, text: 'regelmässig' };
  },
};

/** Die Titel der beiden Gruppen eines Geschosses, wie im Katalog: Lasten und Kern. */
const GESCHOSS = 'Geschoss';
const KERN = 'Kern';

/** Die Zahlen einer Zeile, je ein Feld der Vorgaben von `klasse` in `gruppe`. */
function zahlen(klasse, teil, aendern, gruppe) {
  return vorgabefelder(klasse, teil, gruppe).map((f) => zahlfeld({
    wert: teil[f.feld], schritt: f.schritt, angabe: feldangabe(klasse, f.feld),
    titel: vorgabetitel(f), beiAenderung: (v) => aendern((x) => { x[f.feld] = v; }),
  }));
}

/** Die Köpfe der Spalten: je Feld der Vorgaben sein Zeichen und die Einheit des Kerns. */
function koepfe(klasse, teil, gruppe) {
  return vorgabefelder(klasse, teil, gruppe)
    .map((f) => [f.zeichen, feldangabe(klasse, f.feld).einheit]);
}

/** Die Stellen der Geschosse von oben nach unten, wie das Gebäude: das Dach zuerst. */
function vonOben(h) {
  return h.geschosse.map((_, i) => i).reverse();
}

/** Die Nummer eines Geschosses, gezählt ab der Einspannung -- wie in der Herleitung. */
function nummer(i) {
  return el('span.schicht-nummer', {
    text: String(i + 1), title: `${i + 1}. Geschoss über der Einspannung`,
  });
}

function geschossZeile(h, i) {
  const geschoss = h.geschosse[i];
  const aendern = (veraenderer) => eintragAendern(h.kennung, (x) => veraenderer(x.geschosse[i]));
  return fallzeile({
    fall: geschoss, aendern, nameTitel: 'Bezeichnung des Geschosses', vorn: nummer(i),
    zahlen: zahlen('geschoss', geschoss, aendern, GESCHOSS),
    entfernenTitel: 'Geschoss entfernen',
    entfernen: () => eintragAendern(h.kennung, (x) => { x.geschosse.splice(i, 1); }),
  });
}

/**
 * Ein neues Geschoss, oben auf das Gebäude: mit Kern und η_EI des obersten,
 * die Lasten aus der Vorlage.
 */
function aufstocken(h) {
  return anfuegenKnopf('Geschoss', (name) => eintragAendern(h.kennung, (x) => {
    const oben = x.geschosse[x.geschosse.length - 1];
    x.geschosse.push(ausVorlage('geschoss', {
      name: name(x.geschosse), ...(oben ? { kern: oben.kern, eta_EI: oben.eta_EI } : {}),
    }));
  }), { titel: 'Ein Geschoss oben anfügen – mit Kern und η_EI des obersten' });
}

/** Die Geschosse: je eine Zeile, von oben nach unten wie das Gebäude. */
const GESCHOSSE = {
  schluessel: 'geschosse',
  name: 'Geschosse', titel: 'Geschosse',
  hilfe: HILFE.geschosse,
  inhalt: (h) => [el('div.unterkapitel', {}, [
    h.geschosse.length
      ? el('div.eb-folge', { text: 'Von oben nach unten, wie das Gebäude – gezählt ab der Einspannung' })
      : el('div.leer', { text: 'Noch kein Geschoss – ohne Geschoss keine Ersatzkraft.' }),
    aufstocken(h),
    h.geschosse.length ? fallkopf(koepfe('geschoss', h.geschosse[0], GESCHOSS)) : null,
    ...vonOben(h).map((i) => geschossZeile(h, i)),
  ].filter(Boolean))],
  stand: (h) => zeilenstand(h.geschosse, 'Geschoss', 'Geschosse', 'kein Geschoss'),
};

/**
 * Was der Kern der Software zum Kern eines Geschosses sagt -- nur, wenn es
 * zu dessen jetziger Querschnittsanalyse gehört: nach einer anderen Wahl
 * gilt es nicht mehr.
 */
function kernbefund(h, i) {
  const m = zustand.loesung?.zeichendaten?.[h.kennung]?.kerne?.[i];
  return m && m.analyse === h.geschosse[i].kern ? m : null;
}

/** Die Meldung am Geschoss: rot, was falsch ist, grau, was nur fehlt. */
function kernmeldung(h, i) {
  const m = kernbefund(h, i);
  if (!m) return null;
  return el('div.qa-meldung', {
    text: `${m.grund[0].toUpperCase()}${m.grund.slice(1)}.`, class: m.fehler ? '' : 'ist-hinweis',
  });
}

/**
 * Je Geschoss sein Kern: die Querschnittsanalyse und η_EI. Name und Folge
 * gehören den Geschossen -- hier stehen sie nur da, ohne Kreuz.
 */
function kernZeile(h, i) {
  const geschoss = h.geschosse[i];
  const aendern = (veraenderer) => eintragAendern(h.kennung, (x) => veraenderer(x.geschosse[i]));
  return fallzeile({
    fall: geschoss, aendern, nameFest: true, spalten: 3, vorn: nummer(i),
    nameTitel: 'Das Geschoss – Name und Folge unter «Geschosse»',
    zahlen: zahlen('geschoss', geschoss, aendern, KERN),
    unten: [
      wahlBlock('Querschnittsanalyse', bauteilliste({
        alle: zustand.projekt.querschnittsanalysen || [], gewaehlt: geschoss.kern,
        inSandbox: istSandbox(h.kennung),
        titel: 'Der Kern des Geschosses: alle Wände in x und in y, wie im Grundriss – y der '
          + 'Analyse in x des Gebäudes',
        setzen: (v) => aendern((x) => { x.kern = v; }),
      })),
      kernmeldung(h, i),
    ].filter(Boolean),
  });
}

/** Was auf der Kachel steht: der Name des Kerns, wo alle denselben haben, sonst wie viele. */
function kernstand(h) {
  const gewaehlt = [...new Set(h.geschosse.map((g) => g.kern).filter(Boolean))];
  if (!h.geschosse.length) return { an: false, text: 'kein Geschoss' };
  if (!gewaehlt.length) return { an: false, text: 'ohne Kern' };
  const analyse = (zustand.projekt.querschnittsanalysen || []).find((a) => a.kennung === gewaehlt[0]);
  return {
    an: true,
    text: gewaehlt.length > 1 ? `${gewaehlt.length} Querschnitte` : analyse?.name || 'gelöscht',
  };
}

/**
 * Der Kern: je Geschoss, von oben nach unten, seine Querschnittsanalyse
 * und η_EI. Was der Kern der Software dazu sagt, steht am Geschoss -- und
 * das erste davon grau auf der Kachel.
 */
const KERNE = {
  schluessel: 'kern',
  name: 'Kern', titel: 'Kern',
  hilfe: HILFE.kern,
  inhalt: (h) => [el('div.unterkapitel', {}, h.geschosse.length ? [
    el('div.eb-folge', { text: 'Je Geschoss sein Kern, von oben nach unten – ohne Kern in allen '
      + 'gilt nur T₁ von Hand, und die Kräfte bleiben ohne Verteilung' }),
    fallkopf(koepfe('geschoss', h.geschosse[0], KERN), { spalten: 3 }),
    ...vonOben(h).map((i) => kernZeile(h, i)),
  ] : [el('div.leer', { text: 'Noch kein Geschoss – erst unter «Geschosse» eines anlegen.' })])],
  stand: (h) => {
    const i = vonOben(h).find((j) => kernbefund(h, j));
    return standOhne(kernstand(h), i === undefined ? ''
      : `${h.geschosse[i].name}: ${kernbefund(h, i).grund}`);
  },
};

/** Die Kacheln: Standort, je Gruppe der Vorgaben eine, Regelmässigkeit, Geschosse, Kern. */
function kapitel(h) {
  const aendern = (veraenderer) => eintragAendern(h.kennung, veraenderer);
  const vorgaben = eingabegruppen('erdbeben', h, aendern);
  const kacheln = [
    STANDORT,
    gruppenkapitel(vorgaben, 'Verhaltensbeiwert', {
      zeichen: 'verhaltensbeiwert', name: 'Verhaltens\u00adbeiwert', werte: ['q_x', 'q_y'],
      hilfe: HILFE.verhalten,
    }),
    gruppenkapitel(vorgaben, 'Grundschwingzeit', {
      zeichen: 'schwingzeit', name: 'Grund\u00adschwingzeit',
      wort: h.schwingzeit === 'hand' ? '' : wortVon('schwingzeiten', h.schwingzeit),
      werte: ['T1_x', 'T1_y'], hilfe: HILFE.schwingzeit,
      vor: [wahl(h, aendern, 'schwingzeiten', 'schwingzeit', 'Woher die Grundschwingzeit T₁ kommt')],
    }),
    REGELMAESSIGKEIT,
    GESCHOSSE,
    KERNE,
  ];
  vorgaben.vollstaendig();
  return [{ titel: '', kapitel: kacheln.filter(Boolean) }];
}

export function erdbebenEditor(h) {
  return [kopfPanel(h),
    kapitelPanel(h, kapitel(h), { schluessel: 'erdbeben/Kapitel', titel: 'Eingaben' })];
}

/** Das offene Fenster eines Gebäudes -- oder null. */
export function erdbebenFenster(h, schluessel) {
  return kapitelFenster(h, kapitel(h), schluessel);
}
