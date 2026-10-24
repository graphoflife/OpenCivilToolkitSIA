/**
 * balkensystem.js -- Mittlere Tafel: Eingaben eines 2D-Balkensystems.
 *
 * Von oben nach unten:
 *
 *     System          Bezeichnung, Lastfall der Zeichnung, Zeichnung samt
 *                     Liste, Beschreibung
 *     Materialien     je Material des Projekts sein E-Modul und seine Dichte
 *                     -- die Zeilen der App «Materialien»
 *     Querschnitte    je Querschnitt: Vorlage mit Massen, Kennwerte von Hand,
 *                     aus einer Platte oder aus einer Querschnittsanalyse;
 *                     sein E-Modul vom Material oder als Zahl
 *     Lastfälle       die Fälle und ihre Kombinationen mit Beiwerten
 *     Statik-Analyse  die Diagramme rechts: je Zeile ein Fall und eine
 *                     Grösse, wie in der Spannung-Dehnung-Analyse
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
import { ART_TEXT, kennwertZeile } from './material.js';
import { anfuegenKnopf, rechenwahlZeile } from './nachweise.js';
import {
  ausVorlage, feldangabe, naechsterName, projektAendern, zustand,
} from './zustand.js';

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
  materialien: {
    zeilen: [
      ['E', 'E_cm beim Beton, E_s beim Stahl -- ausser ein Querschnitt hat seinen E-Modul als Zahl'],
      ['ρ', 'beim Beton die Dichte des Stahlbetons: die Bewehrung steckt darin'],
      ['Ändern', 'bei einem eigenen Material hier oder in der App «Materialien» -- eine Normsorte bleibt, wie sie ist'],
    ],
    formel: 'g_k = ρ · g · A   g = 10 m/s²',
  },
  querschnitte: {
    zeilen: [
      ['Vorlage', 'A und I nach den Formeln der Vorlage, Masse in mm'],
      ['Platte', 'ein Streifen b × h der gewählten Platte'],
      ['Analyse', 'A und I_y des Bruttoquerschnitts'],
      ['E-Modul', 'vom Material des Stabs (E_cm bzw. E_s), als Zahl oder -- aus einer Analyse -- als E_eq bei N und M; Zahl und E_eq gelten für jeden Stab mit diesem Querschnitt, für EA und EI'],
      ['E_eq', 'wie die Linie M–E_eq der Analyse: ungerissen bis zum Rissmoment, darüber gerissen; M > 0 zieht unten'],
      ['Steifigkeit', 'EA, EI am ungerissenen Bruttoquerschnitt -- nach Vorgabe'],
    ],
    formel: 'EA = E · A   EI = E · I',
  },
  statik: {
    zeilen: [
      ['Fall', 'ein Lastfall oder eine Kombination -- gerechnet wird jeder Fall'],
      ['M, V, N', 'je Stab der Verlauf, positiv auf der Seite der gestrichelten Faser'],
      ['Verschiebung', 'das verschobene System, überhöht -- je Stab die grösste Durchbiegung gegen die Sehne'],
      ['Lager', 'die Lagerkräfte auf das Tragwerk'],
      ['Angeschrieben', 'die Werte an den Enden und je Stab die grössten, mit Punkt und Stelle'],
    ],
  },
};

/** Ändert das System mit dieser Kennung -- der eine Weg, auf dem hier etwas geändert wird. */
function aendernAn(kennung, veraenderer) {
  projektAendern((p) => veraenderer(p.balkensysteme.find((s) => s.kennung === kennung)));
}

// ===========================================================================
// Unter der Zeichnung
// ===========================================================================

/**
 * Meldungen des Kerns und je Linie, Lager und Last eine Zeile -- ein Klick
 * wählt im Fenster; bei einer Last zeigt die Zeichnung dann ihren Lastfall.
 */
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
    if (m === zustand.katalog?.balkensystem?.material_des_querschnitts) return 'gemäss Querschnitt';
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
      l.querschnitt ? `${name(l.querschnitt)} · ${stoff(l.material)}` : 'kein Stab',
      gelenke.length ? `Gelenk ${gelenke.join(', ')}` : '',
      ...lager,
    ].filter(Boolean).join(' · '));
  });
  const lager = z.lager.map((l) => zeile(l.kennung, `an ${l.knoten}`,
    `x ${l.x} · z ${l.z} · φ ${l.phi}`, l.knoten));
  const lastfall = (lf) => z.lastfaelle.find((x) => x.kennung === lf)?.name || lf;
  const lastzeile = (last, wo, text) => el('div.bs-element', {
    dataset: { kennung: last.kennung },
    on: {
      click: () => {
        lastfallWaehlen(a.bs.kennung, last.lastfall);
        waehlen(a.bs.kennung, [last.kennung]);
      },
    },
  }, [el('span.bs-element-name', { text: last.kennung }), el('span', { text: wo }),
    el('span.bs-element-zusatz', { text: `${text} · ${lastfall(last.lastfall)}` })]);
  const arten = zustand.katalog?.balkensystem?.lastarten || [];
  const lasten = [
    ...z.linien.flatMap((l) => l.lasten.map((last) => {
      const art = arten.find((x) => x.wert === last.art);
      const wert = last.wert_b === null || last.wert_b === undefined ? `${last.wert_a}` : `${last.wert_a} … ${last.wert_b}`;
      const stelle = art?.verteilt ? '' : ` bei ${last.stelle} %`;
      return lastzeile(last, `auf ${l.kennung}`, `${art?.beschriftung || last.art} ${wert} ${art?.einheit || ''}${stelle}`);
    })),
    ...z.knotenlasten.map((p) => lastzeile(p, `an ${p.knoten}`,
      `${p.art === 'moment' ? 'Moment' : 'Kraft'} ${p.wert} ${p.art === 'moment' ? 'kNm' : 'kN'}`)),
  ];
  if (linien.length) teile.push(el('div.bs-elemente', {}, [el('div.bs-elemente-titel', { text: 'Linien' }), ...linien]));
  if (lager.length) teile.push(el('div.bs-elemente', {}, [el('div.bs-elemente-titel', { text: 'Lager' }), ...lager]));
  if (lasten.length) teile.push(el('div.bs-elemente', {}, [el('div.bs-elemente-titel', { text: 'Lasten' }), ...lasten]));
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
// Materialien
// ===========================================================================

/**
 * Jedes Material des Projekts mit dem, womit ein Stab aus ihm rechnet --
 * welche Kennwerte das sind, sagt der Katalog. Die Zeilen sind die der App
 * «Materialien»: bei einer Normsorte gesperrt, bei einem eigenen Material
 * hier wie dort zu ändern.
 */
function materialienGruppe(system) {
  const relevant = zustand.katalog?.balkensystem?.kennwerte || {};
  const staebe = zustand.loesung?.zuordnung?.balkensysteme?.[system.kennung]?.materialien || {};
  const block = (m) => {
    const vorlagen = (relevant[m.art] || [])
      .map((kurz) => (zustand.katalog.kennwerte[m.art] || []).find((v) => v.kurzname === kurz))
      .filter(Boolean);
    // Welche Stäbe es trägt, sagt der Kern -- er kennt auch das Material
    // einer Linie «gemäss Querschnitt».
    const benutzt = Object.entries(staebe).filter(([, k]) => k === m.kennung).map(([stab]) => stab);
    return el('div.bs-material', {}, [
      el('div.bs-material-kopf', {}, [
        el('span.bs-material-name', { text: m.name || m.sorte }),
        el('span.bs-material-art', {
          text: `${ART_TEXT[m.art] || m.art} · ${m.eigenstaendig ? 'eigenes Material' : 'Normsorte'}`,
        }),
      ]),
      ...vorlagen.map((v) => kennwertZeile(m, v)),
      el('p.bs-benutzt', { text: benutzt.length ? `trägt ${benutzt.join(', ')}` : 'trägt keinen Stab' }),
    ]);
  };
  const materialien = zustand.projekt.materialien;
  return panel({
    schluessel: 'balkensystem/Materialien', titel: 'Materialien',
    zusatz: erklaerung(HILFE.materialien.zeilen, HILFE.materialien.formel),
  }, materialien.length ? materialien.map(block)
    : [el('p.bs-leer', { text: 'Noch kein Material -- links unter «Materialien» mit «+» anlegen.' })]);
}

// ===========================================================================
// Querschnitte
// ===========================================================================

const QUERSCHNITTSARTEN = () => zustand.katalog?.balkensystem?.querschnittsarten || [];
const VORLAGEN = () => zustand.katalog?.balkensystem?.vorlagen || [];
const E_MODULE = () => zustand.katalog?.balkensystem?.e_module || [];

/** Was der Kern zu einem Querschnitt gerechnet hat: A und I -- und sein eigenes E --, oder nichts. */
function kennwerte(system, q) {
  const zuordnung = zustand.loesung?.zuordnung?.balkensysteme?.[system.kennung];
  const ids = zuordnung?.querschnitte?.[q.kennung];
  const werte = zustand.loesung?.werte || {};
  if (!ids) return null;
  const text = (id) => (werte[id] ? `${werte[id].wert} ${werte[id].einheit}` : '–');
  const E = zuordnung.module?.[q.kennung];
  return `A = ${text(ids.A)} · I = ${text(ids.I)}${E ? ` · E = ${text(E)}` : ''}`;
}

function querschnittBlock(system, q, i) {
  const aendern = (veraenderer) => aendernAn(system.kennung, (s) => veraenderer(s.querschnitte[i], s));
  const setzen = (feldname) => (wert) => aendern((x) => { x[feldname] = wert; });
  const benutzt = system.linien.filter((l) => l.querschnitt === q.kennung).map((l) => l.kennung);
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
  // Welche Stellungen es gibt, sagt der Katalog je Art -- E_eq nur aus einer
  // Analyse. Die gewählte bleibt sichtbar, auch wo sie nicht mehr passt: die
  // Meldung des Kerns sagt dann warum.
  zeilen.push(wahlBlock('E-Modul', wahlSchalter({
    werte: E_MODULE().filter((x) => x.arten.includes(q.art) || x.wert === q.e_modul)
      .map((x) => ({ wert: x.wert, beschriftung: x.beschriftung, titel: x.titel })),
    gewaehlt: q.e_modul, titel: 'Woher E kommt', setzen: setzen('e_modul'),
  })));
  if (q.e_modul === 'zahl') {
    zeilen.push(feld('E', zahlfeld({
      wert: q.E, schritt: 1000, min: 0,
      titel: 'E-Modul von Hand -- für jeden Stab mit diesem Querschnitt, aus welchem Material auch immer',
      beiAenderung: setzen('E'),
    }), feldangabe('stabquerschnitt', 'E').einheit));
  } else if (q.e_modul === 'e_eq') {
    const eq = (veraenderer) => aendern((x) => veraenderer(x.eq));
    const zahl = (name, schritt, titel) => feld(name, zahlfeld({
      wert: q.eq[name], schritt, leer: 0, titel,
      beiAenderung: (w) => eq((x) => { x[name] = w; }),
    }), feldangabe('modul', name).einheit);
    zeilen.push(
      zahl('N', 50, 'Normalkraft, bei der E_eq gilt -- Zug positiv'),
      zahl('M', 10, 'Moment, bei dem E_eq gilt -- positiv zieht es unten, an der gestrichelten Faser'),
      rechenwahlZeile('Rechenwerte wie in der Analyse', q.eq, eq,
        { arten: 'faserarten', phiImmer: true }),
    );
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
  // Das Eigengewicht kommt von selbst und bleibt: es lässt sich umbenennen,
  // nicht löschen (Benutzer, 2026-10-23).
  const fall = (lf, i) => el('div.bs-fall', {}, [
    el('input', {
      type: 'text', value: lf.name, title: 'Name des Lastfalls -- so steht er im Bericht',
      on: { change: (e) => aendern((s) => { s.lastfaelle[i].name = e.target.value; }) },
    }),
    el('span.bs-fall-zahl', {
      text: lf.eigengewicht
        ? `von selbst, ρ · g · A${lastenVon(lf.kennung) ? ` · dazu ${lastenText(lastenVon(lf.kennung))}` : ''}`
        : lastenText(lastenVon(lf.kennung)),
      title: lf.eigengewicht ? 'Je Stab Dichte mal g = 10 m/s² mal Fläche -- beim Beton die Dichte des Stahlbetons' : '',
    }),
    lf.eigengewicht ? el('span') : el('button.weg', {
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
// Statik-Analyse
// ===========================================================================

const DIAGRAMMGROESSEN = () => zustand.katalog?.balkensystem?.diagrammgroessen || [];

/**
 * Welche Diagramme rechts stehen -- wie in der Spannung-Dehnung-Analyse: je
 * Zeile ein Fall, Lastfall oder Kombination, und was das Diagramm von ihm
 * zeigt (Benutzer, 2026-10-23). Gerechnet wird damit nichts, das System
 * rechnet jeden Fall. Ein Fall, den es nicht mehr gibt, steht als «– Fall
 * wählen –» da.
 */
function statikGruppe(system) {
  const aendern = (veraenderer) => aendernAn(system.kennung, veraenderer);
  const faelle = [
    ...system.lastfaelle.map((lf) => ({ wert: lf.kennung, beschriftung: lf.name })),
    ...system.kombinationen.map((k) => ({ wert: k.kennung, beschriftung: `${k.name} (Kombination)` })),
  ];
  const zeile = (d, i) => el('div.bs-diagrammzeile', {}, [
    el('div.bs-diagrammzeile-kopf', {}, [
      auswahl({
        werte: faelle.some((f) => f.wert === d.fall) ? faelle
          : [{ wert: d.fall, beschriftung: '– Fall wählen –' }, ...faelle],
        gewaehlt: d.fall,
        titel: 'Welcher Lastfall oder welche Kombination',
        beiAenderung: (w) => aendern((s) => { s.diagramme[i].fall = w; }),
      }),
      el('button.weg', {
        type: 'button', text: '×', title: 'Diagramm löschen',
        on: { click: () => aendern((s) => { s.diagramme.splice(i, 1); }) },
      }),
    ]),
    wahlSchalter({
      werte: DIAGRAMMGROESSEN().map((g) => ({ wert: g.wert, beschriftung: g.beschriftung, titel: g.titel })),
      gewaehlt: d.groesse, titel: 'Was das Diagramm zeigt',
      setzen: (w) => aendern((s) => { s.diagramme[i].groesse = w; }),
    }),
  ]);
  return panel({
    schluessel: 'balkensystem/Statik', titel: 'Statik-Analyse',
    zusatz: erklaerung(HILFE.statik.zeilen),
  }, [
    ...(system.diagramme.length ? system.diagramme.map(zeile)
      : [el('div.leer', { text: 'Noch kein Diagramm.' })]),
    anfuegenKnopf('Diagramm', () => aendern((s) => {
      s.diagramme.push(ausVorlage('statikdiagramm', {
        fall: s.kombinationen[0]?.kennung || s.lastfaelle[0]?.kennung || '',
      }));
    })),
  ]);
}

// ===========================================================================

export function balkensystemEditor(system) {
  return [systemGruppe(system), materialienGruppe(system), querschnitteGruppe(system),
    lastfaelleGruppe(system), statikGruppe(system)];
}
