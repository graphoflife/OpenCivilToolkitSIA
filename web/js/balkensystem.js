/**
 * balkensystem.js -- Mittlere Tafel: Eingaben eines 2D-Balkensystems.
 *
 * Von oben nach unten:
 *
 *     System          Bezeichnung, Lastfall der Zeichnung, Zeichnung samt
 *                     Liste, Beschreibung
 *     Querschnitte    je Querschnitt: Vorlage mit Massen, Kennwerte von Hand,
 *                     aus einer Platte oder aus einer Querschnittsanalyse
 *     Lastfälle       die Fälle und ihre Kombinationen mit Beiwerten
 *
 * Gerechnet wird nichts: A und I, die Steifigkeiten und alles Weitere bildet
 * der Kern; hier stehen nur seine Zahlen.
 *
 * VORZEICHEN: x nach rechts, z nach oben, Drehungen und Momentlasten im
 * Gegenuhrzeigersinn. Kraftlasten sind positiv in Pfeilrichtung --
 * senkrecht nach unten, quer zur gestrichelten Faser. Die Schnittgrössen
 * nach Baustatik: N > 0 ist Zug, M > 0 zieht an der gestrichelten Faser.
 * Das kleine Bild unter «Vorzeichen» zeigt es.
 */

import {
  erklaerung, feld, panel, wahlBlock, wahlSchalter,
} from './bausteine.js';
import {
  aktiverLastfall, eintragVon, lastfallWaehlen, passendeUebersicht, waehlen, zeichenbereich,
} from './bs_zeichnung.js';
import {
  auswahl, el, melden, svgEl, zahlfeld,
} from './dom.js';
import { naechsterName, projektAendern, zustand } from './zustand.js';

const HILFE = {
  vorzeichen: {
    zeilen: [
      ['Achsen', 'x nach rechts, z nach oben; Verschiebungen positiv entlang der Achsen'],
      ['Drehung', 'im Gegenuhrzeigersinn positiv, ebenso Momentlasten'],
      ['Lasten', 'positiv in Pfeilrichtung: senkrecht nach unten, waagrecht nach rechts, quer zur gestrichelten Faser, längs vom Anfang zum Ende'],
      ['N, V, M', 'nach Baustatik: N > 0 Zug, M > 0 zieht an der gestrichelten Faser, dM/dx = V − m'],
      ['Faser', 'rechts der Laufrichtung -- «Umkehren» legt sie auf die andere Seite'],
    ],
    formel: 'Lagerkraft nach oben positiv',
  },
  querschnitte: {
    zeilen: [
      ['Vorlage', 'A und I nach den Formeln der Vorlage, Masse in mm'],
      ['Platte', 'ein Streifen b × h der gewählten Platte'],
      ['Analyse', 'A und I_y des Bruttoquerschnitts'],
      ['Steifigkeit', 'EA, EI mit E_cm bzw. E_s am ungerissenen Bruttoquerschnitt -- nach Vorgabe'],
    ],
    formel: 'EA = E · A   EI = E · I',
  },
};

/** Ändert das System mit dieser Kennung -- der eine Weg, auf dem hier etwas geändert wird. */
function aendernAn(kennung, veraenderer) {
  projektAendern((p) => veraenderer(p.balkensysteme.find((s) => s.kennung === kennung)));
}

// ===========================================================================
// Unter der Zeichnung
// ===========================================================================

/** Meldungen des Kerns und je Linie und Lager eine Zeile -- ein Klick wählt im Fenster. */
function uebersicht(a) {
  const z = eintragVon(a.bs.kennung);
  if (!z) return [];
  const u = passendeUebersicht(a);
  const teile = [];
  if (u?.fehler) teile.push(el('div.qa-meldungen', {}, [el('div.qa-meldung', { text: u.fehler })]));
  const meldungen = u?.meldungen || [];
  if (meldungen.length) {
    teile.push(el('div.qa-meldungen', {}, meldungen.map((m) => el('button.qa-meldung', {
      type: 'button', text: m.text, class: m.fehler ? '' : 'ist-hinweis',
      title: 'Wählt die Elemente, die die Meldung nennt',
      on: { click: () => waehlen(a.bs.kennung, m.elemente.filter((k) => /^[KL]\d+$/.test(k))) },
    }))));
  }
  const name = (q) => z.querschnitte.find((x) => x.kennung === q)?.name || q || '–';
  const stoff = (m) => {
    const da = zustand.projekt.materialien.find((x) => x.kennung === m);
    return da ? (da.name || da.sorte) : '–';
  };
  const zeile = (kennung, links, rechts, waehlbar = kennung) => el('div.bs-element', {
    dataset: { kennung },
    on: { click: () => waehlen(a.bs.kennung, [waehlbar]) },
  }, [el('span.bs-element-name', { text: kennung }), el('span', { text: links }), el('span.bs-element-zusatz', { text: rechts })]);
  const linien = z.linien.map((l) => {
    const gelenke = [l.gelenk_anfang ? 'Anfang' : '', l.gelenk_ende ? 'Ende' : ''].filter(Boolean);
    const lager = [l.quer !== 'frei' ? `quer ${l.quer === 'feder' ? 'gebettet' : 'fest'}` : '',
      l.laengs !== 'frei' ? `längs ${l.laengs === 'feder' ? 'gebettet' : 'fest'}` : ''].filter(Boolean);
    return zeile(l.kennung, `${l.von} → ${l.bis}`, [
      l.stab ? `${name(l.querschnitt)} · ${stoff(l.material)}` : 'kein Stab',
      gelenke.length ? `Gelenk ${gelenke.join(', ')}` : '',
      ...lager,
    ].filter(Boolean).join(' · '));
  });
  const lager = z.lager.map((l) => zeile(l.kennung, `an ${l.knoten}`,
    `x ${l.x} · z ${l.z} · φ ${l.phi}`, l.knoten));
  if (linien.length) teile.push(el('div.bs-elemente', {}, [el('div.bs-elemente-titel', { text: 'Linien' }), ...linien]));
  if (lager.length) teile.push(el('div.bs-elemente', {}, [el('div.bs-elemente-titel', { text: 'Lager' }), ...lager]));
  return teile;
}

// ===========================================================================
// System
// ===========================================================================

/** Ein kleines Bild der Vorzeichen: Achsen, Drehsinn, ein Stab mit Faser, M > 0. */
function vorzeichenbild() {
  const s = svgEl('svg', { viewBox: '0 0 300 92', class: 'bs-vorzeichen', role: 'img', 'aria-label': 'Vorzeichen' });
  const pfeil = (d) => svgEl('path', { d, class: 'bs-vz-pfeil' });
  const text = (x, y, t, k = '') => {
    const e = svgEl('text', { x, y, class: `bs-vz-text ${k}` });
    e.textContent = t;
    return e;
  };
  s.append(
    pfeil('M20 70 H70 M64 66 L70 70 L64 74'), text(74, 74, 'x'),
    pfeil('M20 70 V20 M16 26 L20 20 L24 26'), text(16, 14, 'z'),
    svgEl('path', { d: 'M48 40 A12 12 0 1 0 36 52', class: 'bs-vz-pfeil' }),
    pfeil('M36 52 L42 50 M36 52 L39 46'), text(52, 38, 'φ, M ↺'),
    svgEl('path', { d: 'M120 46 H270', class: 'bs-vz-stab' }),
    svgEl('path', { d: 'M135 51 H255', class: 'bs-vz-faser' }),
    text(120, 36, 'Anfang'), text(240, 36, 'Ende'),
    pfeil('M195 14 V40 M191 34 L195 40 L199 34'), text(201, 22, 'Last ↓ positiv'),
    text(150, 68, 'gestrichelte Faser: rechts der Laufrichtung'),
    text(150, 84, 'M > 0 zieht dort · N > 0 ist Zug'),
  );
  return s;
}

function systemGruppe(system) {
  const aendern = (veraenderer) => aendernAn(system.kennung, veraenderer);
  const lf = aktiverLastfall(system.kennung);
  return panel({
    schluessel: 'balkensystem/System', titel: 'System', zusatz: 'x nach rechts, z nach oben, m',
    breit: true,
  }, [
    feld('Bezeichnung', el('input', {
      type: 'text', value: system.name,
      on: { change: (e) => aendern((s) => { s.name = e.target.value; }) },
    })),
    feld('Lastfall', system.lastfaelle.length ? auswahl({
      werte: system.lastfaelle.map((x) => ({ wert: x.kennung, beschriftung: x.name })),
      gewaehlt: lf,
      titel: 'Dessen Lasten zeigt und bearbeitet die Zeichnung',
      beiAenderung: (w) => lastfallWaehlen(system.kennung, w),
    }) : el('span.bs-leer', { text: 'kein Lastfall -- im Panel «Lastfälle» anlegen' }), erklaerung(HILFE.vorzeichen.zeilen, HILFE.vorzeichen.formel)),
    zeichenbereich(system, uebersicht),
    el('div.unterkapitel', {}, [
      el('details.bs-vorzeichen-huelle', {}, [el('summary', { text: 'Vorzeichen' }), vorzeichenbild()]),
      el('div.beschreibung', {}, [
        el('label', { text: 'Beschreibung' }),
        el('textarea', {
          rows: 2, value: system.beschreibung || '',
          on: { change: (e) => aendern((s) => { s.beschreibung = e.target.value; }) },
        }),
      ]),
    ]),
  ]);
}

// ===========================================================================
// Querschnitte
// ===========================================================================

const QUERSCHNITTSARTEN = () => zustand.katalog?.balkensystem?.querschnittsarten || [];
const VORLAGEN = () => zustand.katalog?.balkensystem?.vorlagen || [];

/** Was der Kern zu einem Querschnitt gerechnet hat: A und I, oder nichts. */
function kennwerte(system, q) {
  const ids = zustand.loesung?.zuordnung?.balkensysteme?.[system.kennung]?.querschnitte?.[q.kennung];
  const werte = zustand.loesung?.werte || {};
  if (!ids) return null;
  const text = (id) => (werte[id] ? `${werte[id].wert} ${werte[id].einheit}` : '–');
  return `A = ${text(ids.A)} · I = ${text(ids.I)}`;
}

function querschnittBlock(system, q, i) {
  const aendern = (veraenderer) => aendernAn(system.kennung, (s) => veraenderer(s.querschnitte[i], s));
  const setzen = (feldname) => (wert) => aendern((x) => { x[feldname] = wert; });
  const benutzt = system.linien.filter((l) => l.stab && l.querschnitt === q.kennung).map((l) => l.kennung);
  const weg = () => {
    if (benutzt.length) {
      melden(`«${q.name}» trägt noch ${benutzt.join(', ')}.`, true);
      return;
    }
    aendernAn(system.kennung, (s) => { s.querschnitte.splice(i, 1); });
  };
  // Woher A und I kommen, als Schalter unter dem Namen: neben ihm fänden
  // vier Stellungen keinen Platz.
  const zeilen = [
    el('div.bs-querschnitt-kopf', {}, [
      el('input', {
        type: 'text', value: q.name, title: 'Name des Querschnitts',
        on: { change: (e) => setzen('name')(e.target.value) },
      }),
      el('button.weg', { type: 'button', text: '×', title: 'Querschnitt löschen', on: { click: weg } }),
    ]),
    wahlBlock('A und I aus', wahlSchalter({
      werte: QUERSCHNITTSARTEN().map((x) => ({ wert: x.wert, beschriftung: x.kurz, titel: x.beschriftung })),
      gewaehlt: q.art, titel: 'Woher A und I kommen', setzen: setzen('art'),
    })),
  ];
  if (q.art === 'vorlage') {
    const vorlage = VORLAGEN().find((v) => v.schluessel === q.vorlage) || VORLAGEN()[0];
    zeilen.push(wahlBlock('Vorlage', wahlSchalter({
      werte: VORLAGEN().map((v) => ({ wert: v.schluessel, beschriftung: v.name })),
      gewaehlt: q.vorlage,
      klasse: '.ist-umbruch',
      setzen: (w) => aendern((x) => {
        x.vorlage = w;
        // Die Masse der neuen Vorlage, mit ihren Vorgaben -- die alten passten nicht.
        x.masse = Object.fromEntries((VORLAGEN().find((v) => v.schluessel === w)?.masse || [])
          .map((m) => [m.schluessel, m.vorgabe]));
      }),
    })));
    for (const m of vorlage?.masse || []) {
      zeilen.push(feld(m.beschriftung, zahlfeld({
        wert: q.masse?.[m.schluessel] ?? m.vorgabe, schritt: 10, min: 0,
        titel: `${m.beschriftung} ${m.symbol} in mm`,
        beiAenderung: (w) => aendern((x) => { x.masse = { ...x.masse, [m.schluessel]: w }; }),
      }), 'mm'));
    }
  } else if (q.art === 'kennwerte') {
    const kennwert = (schluessel, text, einheit) => feld(text, zahlfeld({
      wert: q.masse?.[schluessel] ?? 0, schritt: schluessel === 'A' ? 1000 : 10, min: 0,
      beiAenderung: (w) => aendern((x) => { x.masse = { ...x.masse, [schluessel]: w }; }),
    }), einheit);
    zeilen.push(kennwert('A', 'Fläche A', 'mm²'), kennwert('I', 'Trägheitsmoment I', '10⁶ mm⁴'));
  } else {
    const liste = q.art === 'platte' ? zustand.projekt.querschnitte : (zustand.projekt.querschnittsanalysen || []);
    zeilen.push(feld(q.art === 'platte' ? 'Platte' : 'Analyse', auswahl({
      werte: [{ wert: '', beschriftung: '– wählen –' }, ...liste.map((x) => ({ wert: x.kennung, beschriftung: x.name }))],
      gewaehlt: q.bezug,
      beiAenderung: setzen('bezug'),
    })));
  }
  const werte = kennwerte(system, q);
  if (werte) zeilen.push(el('p.bs-kennwerte', { text: werte }));
  if (benutzt.length) zeilen.push(el('p.bs-benutzt', { text: `trägt ${benutzt.join(', ')}` }));
  return el('div.bs-querschnitt', {}, zeilen);
}

function querschnitteGruppe(system) {
  const neu = () => aendernAn(system.kennung, (s) => {
    s.querschnitte.push({
      ...structuredClone(zustand.katalog.neue_zeilen.stabquerschnitt),
      kennung: naechsteKennung(s.querschnitte, 'Q'), name: naechsterName('Querschnitt', s.querschnitte),
    });
  });
  return panel({
    schluessel: 'balkensystem/Querschnitte', titel: 'Querschnitte',
    zusatz: erklaerung(HILFE.querschnitte.zeilen, HILFE.querschnitte.formel),
  }, [
    ...system.querschnitte.map((q, i) => querschnittBlock(system, q, i)),
    el('button.knopf.knopf-klein', { type: 'button', text: '+ Querschnitt', on: { click: neu } }),
  ]);
}

// ===========================================================================
// Lastfälle und Kombinationen
// ===========================================================================

/** Die nächste Kennung einer Liste: die grösste bisherige plus eins -- eine Kennung kommt nie wieder. */
function naechsteKennung(liste, vorsilbe) {
  const nummern = liste.map((x) => Number(String(x.kennung).slice(vorsilbe.length)))
    .filter(Number.isInteger);
  return `${vorsilbe}${Math.max(0, ...nummern) + 1}`;
}

const lastenText = (n) => `${n} ${n === 1 ? 'Last' : 'Lasten'}`;

function lastfaelleGruppe(system) {
  const aendern = (veraenderer) => aendernAn(system.kennung, veraenderer);
  const lastenVon = (lf) => system.linien.reduce((n, l) => n + l.lasten.filter((x) => x.lastfall === lf).length, 0)
    + system.knotenlasten.filter((x) => x.lastfall === lf).length;
  const fall = (lf, i) => el('div.bs-fall', {}, [
    el('input', {
      type: 'text', value: lf.name, title: 'Name des Lastfalls -- so steht er im Bericht',
      on: { change: (e) => aendern((s) => { s.lastfaelle[i].name = e.target.value; }) },
    }),
    el('span.bs-fall-zahl', { text: lastenText(lastenVon(lf.kennung)) }),
    el('button.weg', {
      type: 'button', text: '×', title: 'Lastfall löschen',
      on: {
        click: () => {
          const n = lastenVon(lf.kennung);
          if (n) {
            melden(`«${lf.name}» hat noch ${lastenText(n)} -- zuerst diese löschen.`, true);
            return;
          }
          aendern((s) => {
            s.lastfaelle.splice(i, 1);
            for (const k of s.kombinationen) delete k.faktoren[lf.kennung];
          });
        },
      },
    }),
  ]);
  const kombination = (k, i) => el('tr', {}, [
    el('td', {}, [el('input', {
      type: 'text', value: k.name,
      on: { change: (e) => aendern((s) => { s.kombinationen[i].name = e.target.value; }) },
    })]),
    ...system.lastfaelle.map((lf) => el('td', {}, [zahlfeld({
      wert: k.faktoren[lf.kennung] ?? 0, schritt: 0.05,
      titel: `Beiwert für «${lf.name}» -- 0: zählt nicht`,
      beiAenderung: (w) => aendern((s) => { s.kombinationen[i].faktoren[lf.kennung] = w; }),
    })])),
    el('td', {}, [el('button.weg', {
      type: 'button', text: '×', title: 'Kombination löschen',
      on: { click: () => aendern((s) => { s.kombinationen.splice(i, 1); }) },
    })]),
  ]);
  const neuerFall = () => aendern((s) => {
    const kennung = naechsteKennung(s.lastfaelle, 'LF');
    s.lastfaelle.push({ kennung, name: naechsterName('Lastfall', s.lastfaelle) });
  });
  const neueKombination = () => aendern((s) => {
    s.kombinationen.push({
      kennung: naechsteKennung(s.kombinationen, 'LK'),
      name: naechsterName('Kombination', s.kombinationen),
      faktoren: Object.fromEntries(s.lastfaelle.map((lf) => [lf.kennung, 1.0])),
    });
  });
  return panel({ schluessel: 'balkensystem/Lastfälle', titel: 'Lastfälle und Kombinationen' }, [
    ...system.lastfaelle.map(fall),
    el('button.knopf.knopf-klein', { type: 'button', text: '+ Lastfall', on: { click: neuerFall } }),
    system.kombinationen.length ? el('div.tabelle-huelle', {}, [el('table.bs-kombinationen', {}, [
      el('thead', {}, [el('tr', {}, [
        el('th', { text: 'Kombination' }),
        ...system.lastfaelle.map((lf) => el('th', { text: lf.name })),
        el('th'),
      ])]),
      el('tbody', {}, system.kombinationen.map(kombination)),
    ])]) : null,
    system.lastfaelle.length
      ? el('button.knopf.knopf-klein', { type: 'button', text: '+ Kombination', on: { click: neueKombination } })
      : null,
  ]);
}

// ===========================================================================

export function balkensystemEditor(system) {
  return [systemGruppe(system), querschnitteGruppe(system), lastfaelleGruppe(system)];
}
