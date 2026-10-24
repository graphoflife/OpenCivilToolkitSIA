/**
 * balkensystem.js -- Mittlere Tafel: Eingaben eines 2D-Balkensystems.
 *
 * Von oben nach unten:
 *
 *     System          Bezeichnung, Zeichnung samt Liste, Beschreibung
 *     Eingaben        fünf Knöpfe, je mit einem Fenster (`KAPITEL`):
 *                     Material -- die Materialien als Tabelle --,
 *                     Querschnitte -- je einer eine Zeile mit Bild, jeder
 *                     mit eigenem Fenster --, Lastfälle, Lastkombinationen
 *                     und die Statik-Analyse -- die Diagramme rechts, je
 *                     Zeile ein Fall und eine Grösse, wie in der
 *                     Spannung-Dehnung-Analyse
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
  erklaerung, feld, klappgruppe, panel, wahlBlock, wahlSchalter,
} from './bausteine.js';
import { materialname } from './bs_teile.js';
import {
  eintragVon, lastfallWaehlen, passendeUebersicht, waehlen, zeichenbereich,
} from './bs_zeichnung.js';
import {
  auswahl, el, melden, svgEl, zahlfeld,
} from './dom.js';
import { fenster, fensterOeffnen } from './fenster.js';
import { kapitelFenster, kapitelPanel, zeilenstand } from './kapitel.js';
import { anfuegenKnopf, rechenwahlZeile } from './nachweise.js';
import {
  ausVorlage, feldangabe, kennwertId, naechsterName, projektAendern, zustand,
} from './zustand.js';

const HILFE = {
  vorzeichen: {
    zeilen: [
      ['Achsen', 'x nach rechts, z nach oben; Verschiebungen positiv entlang der Achsen'],
      ['Drehung', 'im Gegenuhrzeigersinn positiv, ebenso Momentlasten'],
      ['Lasten', 'positiv in Pfeilrichtung: senkrecht nach unten, waagrecht nach rechts, quer zur gestrichelten Faser, längs vom Anfang zum Ende'],
      ['N, V, M', 'nach Baustatik: N > 0 Zug, M > 0 zieht an der gestrichelten Faser, dM/dx = V − m'],
      ['Faser', 'die Zugseite: an einer neuen Linie unten, an einer senkrechten links -- im Fenster des Stabs umzuschalten; die Lasten bleiben dabei, wo sie wirken'],
    ],
    formel: 'Lagerkraft nach oben positiv',
  },
  materialien: {
    zeilen: [
      ['Beton', 'einer aus dem Projekt: E = E_cm und ρ des Stahlbetons, die Bewehrung steckt darin -- zu ändern in der App «Materialien»'],
      ['eigenes', 'E und ρ von Hand, etwa für Stahl oder Holz'],
      ['ρ', 'für das Eigengewicht ρ · g · A, mit g = 10 m/s²'],
      ['gemäss Querschnitt', 'wählt man an der Linie: der Beton ihrer Platte oder Analyse'],
    ],
    formel: 'g_k = ρ · g · A   g = 10 m/s²',
  },
  querschnitte: {
    zeilen: [
      ['Vorlage', 'A und I nach den Formeln der Vorlage, Masse in mm'],
      ['Platte', 'ein Streifen b × h der gewählten Platte'],
      ['Analyse', 'A und I_y des Bruttoquerschnitts'],
      ['E-Modul', 'vom Material des Stabs -- «gemäss Querschnitt» E₀ = E_cm des Betons der Platte oder Analyse, bei einer Analyse auf Wunsch E_eq bei N und M, für EA und EI'],
      ['E_eq', 'wie die Linie M–E_eq der Spannung-Dehnung-Analyse: ungerissen bis zum Rissmoment, darüber gerissen; M > 0 zieht unten -- bei einer Platte immer in x-Richtung, Zug unten'],
      ['Steifigkeit', 'EA, EI am ungerissenen Bruttoquerschnitt -- nach Vorgabe'],
    ],
    formel: 'EA = E · A   EI = E · I',
  },
  statik: {
    zeilen: [
      ['Fall', 'ein Lastfall oder eine Kombination -- gerechnet wird jeder Fall'],
      ['M, V, N', 'je Stab der Verlauf, positiv auf der Seite der gestrichelten Faser'],
      ['Verschiebung', 'das verschobene System, überhöht -- je Stab die grösste Durchbiegung gegen die Sehne'],
      ['Verdrehung', 'je Stab die Verdrehung φ des Querschnitts in mrad, im Gegenuhrzeigersinn positiv'],
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
  // Jede Gruppe klappt auf und zu, zu Beginn zu (Benutzer, 2026-10-24).
  const offen = a.bs.aufgeklappt || (a.bs.aufgeklappt = new Set());
  for (const [titel, zeilen] of [['Linien', linien], ['Lager', lager], ['Lasten', lasten]]) {
    if (zeilen.length) teile.push(klappgruppe(titel, zeilen, offen, 'bs-elemente'));
  }
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
    text(150, 68, 'gestrichelte Faser: die Zugseite'),
    text(150, 84, 'M > 0 zieht dort · N > 0 ist Zug'),
  );
  return s;
}

function systemGruppe(system) {
  const aendern = (veraenderer) => aendernAn(system.kennung, veraenderer);
  return panel({
    schluessel: 'balkensystem/System', titel: 'System', zusatz: 'x nach rechts, z nach oben, m',
    breit: true,
  }, [
    // Der Lastfall der Zeichnung steht in ihrer Leiste, neben «Last».
    feld('Bezeichnung', el('input', {
      type: 'text', value: system.name,
      on: { change: (e) => aendern((s) => { s.name = e.target.value; }) },
    }), erklaerung(HILFE.vorzeichen.zeilen, HILFE.vorzeichen.formel)),
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
 * Die Materialien der Stäbe als Tabelle (Benutzer, 2026-10-24): je Zeile
 * ein Beton des Projekts -- E und ρ von ihm, gesperrt, gerechnet vom Kern
 * -- oder ein eigenes mit E und ρ von Hand. Betonstahl steht nicht zur
 * Wahl: aus ihm ist kein Stab. Daneben, welche Linien es nehmen.
 */
function materialienInhalt(system) {
  const aendern = (veraenderer) => aendernAn(system.kennung, veraenderer);
  const betone = zustand.projekt.materialien.filter((m) => m.art === 'beton');
  const kennwerte = zustand.katalog?.balkensystem?.betonkennwerte || {};
  const angabe = (feldname) => feldangabe('stabmaterial', feldname);
  const gesperrt = (beton, kurz) => {
    const wert = beton ? zustand.loesung?.werte?.[kennwertId(beton, kennwerte[kurz])] : null;
    return el('span.bs-gesperrt', { text: wert ? wert.wert : '–', title: 'Vom Beton des Projekts -- zu ändern in der App «Materialien»' });
  };
  const zeile = (m, i) => {
    const setzen = (feldname) => (wert) => aendern((s) => { s.stabmaterialien[i][feldname] = wert; });
    const benutzt = system.linien.filter((l) => l.material === m.kennung).map((l) => l.kennung);
    const weg = () => {
      if (benutzt.length) {
        melden(`«${materialname(m)}» trägt noch ${benutzt.join(', ')}.`, true);
        return;
      }
      aendern((s) => { s.stabmaterialien.splice(i, 1); });
    };
    const beton = betone.find((b) => b.kennung === m.beton);
    const zellen = m.art === 'beton' ? [
      auswahl({
        werte: [...(beton ? [] : [{ wert: m.beton, beschriftung: '– Beton wählen –' }]),
          ...betone.map((b) => ({ wert: b.kennung, beschriftung: b.name || b.sorte }))],
        gewaehlt: m.beton, titel: 'Ein Beton des Projekts', beiAenderung: setzen('beton'),
      }),
      el('span.bs-material-art', { text: 'Beton' }),
      gesperrt(beton, 'E'), gesperrt(beton, 'rho'),
    ] : [
      el('input', {
        type: 'text', value: m.name, title: 'Name des Materials -- so steht es im Bericht',
        on: { change: (e) => setzen('name')(e.target.value) },
      }),
      el('span.bs-material-art', { text: 'eigenes' }),
      zahlfeld({ wert: m.E, schritt: 1000, angabe: angabe('E'), titel: 'E-Modul von Hand', beiAenderung: setzen('E') }),
      zahlfeld({ wert: m.rho, schritt: 50, angabe: angabe('rho'), titel: 'Dichte für das Eigengewicht', beiAenderung: setzen('rho') }),
    ];
    return el('tr', {}, [
      ...zellen.map((z) => el('td', {}, [z])),
      el('td.bs-benutzt', { text: benutzt.join(', ') || '–', title: benutzt.length ? `trägt ${benutzt.join(', ')}` : 'trägt keinen Stab' }),
      el('td', {}, [el('button.weg', { type: 'button', text: '×', title: 'Material löschen', on: { click: weg } })]),
    ]);
  };
  const neu = (art) => aendern((s) => {
    s.stabmaterialien.push({
      ...structuredClone(zustand.katalog.neue_zeilen.stabmaterial),
      kennung: naechsteKennung(s.stabmaterialien, 'M'), art,
      ...(art === 'beton' ? { beton: betone[0]?.kennung || '' }
        : { name: naechsterName('Material', s.stabmaterialien) }),
    });
  });
  const kopf = [['Material'], ['Art'], ['E', angabe('E').einheit], ['ρ', angabe('rho').einheit], ['trägt'], ['']];
  return [
    system.stabmaterialien.length ? el('div.tabelle-huelle', {}, [el('table.bs-materialien', {}, [
      el('thead', {}, [el('tr', {}, kopf.map(([text, einheit]) => el('th', {}, [
        text, einheit ? el('span.einheit', { text: ` ${einheit}` }) : null,
      ].filter(Boolean))))]),
      el('tbody', {}, system.stabmaterialien.map(zeile)),
    ])]) : el('p.bs-leer', { text: 'Noch kein Material -- ein Stab braucht eines.' }),
    el('div.bs-knopfreihe', {}, [
      el('button.knopf.knopf-klein', {
        type: 'button', text: '+ Beton', title: 'Ein Beton aus dem Projekt',
        disabled: !betone.length, on: { click: () => neu('beton') },
      }),
      el('button.knopf.knopf-klein', {
        type: 'button', text: '+ eigenes Material', title: 'E-Modul und Dichte von Hand',
        on: { click: () => neu('eigen') },
      }),
    ]),
  ];
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

/**
 * Ein kleines Bild eines Querschnitts: sein Umriss vom Kern, in die Box
 * eingepasst -- Aussparungen gerade-ungerade gefüllt. Ohne Umriss
 * (Kennwerte von Hand, ein Querschnitt, der nicht geht) die Kennwerte als
 * Zeichen.
 */
function umrissBild(system, q, breite, hoehe) {
  const polygone = zustand.loesung?.stabumrisse?.[system.kennung]?.[q.kennung] || [];
  const svg = svgEl('svg', { viewBox: `0 0 ${breite} ${hoehe}`, width: breite, height: hoehe, class: 'bs-umriss', 'aria-hidden': 'true' });
  const punkte = polygone.flat();
  if (!punkte.length) {
    const t = svgEl('text', { x: breite / 2, y: hoehe / 2 + 4, class: 'bs-umriss-text' });
    t.textContent = q.art === 'kennwerte' ? 'A, I' : '?';
    svg.append(t);
    return svg;
  }
  const ys = punkte.map((p) => p[0]);
  const zs = punkte.map((p) => p[1]);
  const [y0, y1, z0, z1] = [Math.min(...ys), Math.max(...ys), Math.min(...zs), Math.max(...zs)];
  const rand = 3;
  const m = Math.min((breite - 2 * rand) / Math.max(y1 - y0, 1e-9), (hoehe - 2 * rand) / Math.max(z1 - z0, 1e-9));
  const [oy, oz] = [(breite - m * (y1 - y0)) / 2, (hoehe - m * (z1 - z0)) / 2];
  const d = polygone.map((poly) => `M${poly.map(([y, z]) => `${(oy + m * (y - y0)).toFixed(1)} ${(hoehe - oz - m * (z - z0)).toFixed(1)}`).join(' L')} Z`).join(' ');
  svg.append(svgEl('path', { d, 'fill-rule': 'evenodd', class: 'bs-umriss-flaeche' }));
  return svg;
}

/** Die Masse einer Vorlage mit ihren Vorgaben, aus dem Katalog. */
function vorgabenDer(schluessel) {
  return Object.fromEntries((VORLAGEN().find((v) => v.schluessel === schluessel)?.masse || [])
    .map((m) => [m.schluessel, m.vorgabe]));
}

/** Woher ein Querschnitt kommt, in Worten -- mit den Massen einer Vorlage. */
function herkunftText(q) {
  if (q.art === 'vorlage') {
    const vorlage = VORLAGEN().find((v) => v.schluessel === q.vorlage);
    const masse = (vorlage?.masse || []).map((m) => `${m.symbol} ${q.masse?.[m.schluessel] ?? m.vorgabe}`);
    return `${vorlage?.name || q.vorlage} · ${masse.join(' · ')} mm`;
  }
  if (q.art === 'kennwerte') return 'Kennwerte von Hand';
  const liste = q.art === 'platte' ? zustand.projekt.querschnitte : (zustand.projekt.querschnittsanalysen || []);
  const bezug = liste.find((x) => x.kennung === q.bezug);
  return `${q.art === 'platte' ? 'Platte' : 'Analyse'} ${bezug ? `«${bezug.name}»` : '– nicht gewählt –'}`;
}

/** Der Schlüssel des Fensters eines Querschnitts. */
const fensterVon = (kennung) => `querschnitt:${kennung}`;

/**
 * Ein Querschnitt als kompakte Zeile (Benutzer, 2026-10-24): links das
 * Bild -- ein Klick öffnet ihn im Fenster --, daneben Name, A und I und
 * woher er kommt.
 */
function querschnittZeile(system, q, i) {
  const benutzt = system.linien.filter((l) => l.querschnitt === q.kennung).map((l) => l.kennung);
  // Ohne A und I sagt die Meldung des Kerns, was dem Querschnitt fehlt.
  const werte = kennwerte(system, q);
  const fehler = (zustand.loesung?.balkensysteme?.[system.kennung]?.meldungen || [])
    .find((m) => m.fehler && m.elemente.includes(q.kennung));
  const weg = () => {
    if (benutzt.length) {
      melden(`«${q.name}» trägt noch ${benutzt.join(', ')}.`, true);
      return;
    }
    aendernAn(system.kennung, (s) => { s.querschnitte.splice(i, 1); });
  };
  return el('div.bs-qzeile', {}, [
    el('button.bs-qbild', {
      type: 'button', title: 'Bearbeiten: woher A und I kommen, Masse',
      on: { click: () => fensterOeffnen(fensterVon(q.kennung)) },
    }, [umrissBild(system, q, 44, 44)]),
    el('div.bs-qmitte', {}, [
      el('input.bs-qname', {
        type: 'text', value: q.name, title: 'Name des Querschnitts',
        on: { change: (e) => aendernAn(system.kennung, (s) => { s.querschnitte[i].name = e.target.value; }) },
      }),
      werte ? el('div.bs-kennwerte', { text: werte })
        : el('div.bs-qfehler', { text: fehler?.text || 'A und I: –', title: fehler?.text || '' }),
      el('div.bs-benutzt', { text: `${herkunftText(q)} · ${benutzt.length ? `trägt ${benutzt.join(', ')}` : 'trägt keinen Stab'}` }),
    ]),
    el('button.weg', { type: 'button', text: '×', title: 'Querschnitt löschen', on: { click: weg } }),
  ]);
}

/**
 * Das Fenster eines Querschnitts -- beim Anlegen und mit einem Klick auf
 * sein Bild (Benutzer, 2026-10-24): woher A und I kommen, die Vorlage als
 * Auswahlliste mit ihrem Bild und den Massen, die Kennwerte, die Platte
 * oder Analyse -- und das E der Stäbe «gemäss Querschnitt».
 */
function querschnittFenster(system, kennung) {
  const i = system.querschnitte.findIndex((x) => x.kennung === kennung);
  if (i < 0) return null;
  const q = system.querschnitte[i];
  const aendern = (veraenderer) => aendernAn(system.kennung, (s) => veraenderer(s.querschnitte[i], s));
  const setzen = (feldname) => (wert) => aendern((x) => { x[feldname] = wert; });
  const zeilen = [
    feld('Name', el('input', {
      type: 'text', value: q.name, title: 'Name des Querschnitts',
      on: { change: (e) => setzen('name')(e.target.value) },
    })),
    wahlBlock('A und I aus', wahlSchalter({
      werte: QUERSCHNITTSARTEN().map((x) => ({ wert: x.wert, beschriftung: x.kurz, titel: x.beschriftung })),
      gewaehlt: q.art, titel: 'Woher A und I kommen',
      // Die Masse gehören zur Art: eine Vorlage bekommt ihre Vorgaben,
      // Kennwerte beginnen leer -- bis 2026-10-24 blieben b und h stehen,
      // und «einen Kennwert «b» gibt es nicht» war die Folge.
      setzen: (w) => aendern((x) => {
        x.art = w;
        if (w === 'vorlage') x.masse = vorgabenDer(x.vorlage);
        if (w === 'kennwerte') x.masse = {};
      }),
    })),
  ];
  if (q.art === 'vorlage') {
    const vorlage = VORLAGEN().find((v) => v.schluessel === q.vorlage) || VORLAGEN()[0];
    // Die Vorlage als Auswahlliste, daneben ihr Bild mit den Massen dieses
    // Querschnitts (Benutzer, 2026-10-24).
    zeilen.push(el('div.bs-qvorlage', {}, [
      feld('Vorlage', auswahl({
        werte: VORLAGEN().map((v) => ({ wert: v.schluessel, beschriftung: v.name })),
        gewaehlt: q.vorlage,
        titel: 'Die Form des Querschnitts',
        beiAenderung: (w) => aendern((x) => {
          x.vorlage = w;
          // Die Masse der neuen Vorlage, mit ihren Vorgaben -- die alten passten nicht.
          x.masse = vorgabenDer(w);
        }),
      })),
      umrissBild(system, q, 120, 90),
    ]));
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
    zeilen.push(el('div.bs-qvorlage', {}, [
      feld(q.art === 'platte' ? 'Platte' : 'Analyse', auswahl({
        werte: [{ wert: '', beschriftung: '– wählen –' }, ...liste.map((x) => ({ wert: x.kennung, beschriftung: x.name }))],
        gewaehlt: q.bezug,
        beiAenderung: setzen('bezug'),
      })),
      umrissBild(system, q, 120, 90),
    ]));
  }
  // Welches E ein Stab hat, der das Material dieses Querschnitts nimmt --
  // nur, wenn einer das tut, und nur, wo es mehr als E₀ gibt: E_eq hat nur
  // eine Analyse (Benutzer, 2026-10-24). Welche Stellungen es gibt, sagt der
  // Katalog; die gewählte bleibt sichtbar, auch wo sie nicht mehr passt --
  // die Meldung des Kerns sagt dann warum.
  const eigenes = zustand.katalog?.balkensystem?.material_des_querschnitts;
  const module = E_MODULE().filter((x) => x.arten.includes(q.art) || x.wert === q.e_modul);
  const mitEigenem = system.linien.some((l) => l.querschnitt === q.kennung && l.material === eigenes);
  if (mitEigenem && module.length > 1) {
    zeilen.push(wahlBlock('E-Modul', wahlSchalter({
      werte: module.map((x) => ({ wert: x.wert, beschriftung: x.beschriftung, titel: x.titel })),
      gewaehlt: q.e_modul, titel: 'Das E der Stäbe «gemäss Querschnitt»', setzen: setzen('e_modul'),
    })));
  }
  if (mitEigenem && q.e_modul === 'e_eq') {
    const eq = (veraenderer) => aendern((x) => veraenderer(x.eq));
    const zahl = (name, schritt, titel) => feld(name, zahlfeld({
      wert: q.eq[name], schritt, leer: 0, titel,
      beiAenderung: (w) => eq((x) => { x[name] = w; }),
    }), feldangabe('modul', name).einheit);
    zeilen.push(
      zahl('N', 50, 'Normalkraft, bei der E_eq gilt -- Zug positiv'),
      zahl('M', 10, q.art === 'platte'
        ? 'Moment, bei dem E_eq gilt -- bei einer Platte in x-Richtung mit Zug unten, nicht negativ'
        : 'Moment, bei dem E_eq gilt -- positiv zieht es unten, an der gestrichelten Faser'),
      rechenwahlZeile('Rechenwerte wie in der Analyse', q.eq, eq,
        { arten: 'faserarten', phiImmer: true }),
    );
  }
  const werte = kennwerte(system, q);
  if (werte) zeilen.push(el('p.bs-kennwerte', { text: werte }));
  return fenster({
    titel: 'Querschnitt', zeichen: 'querschnitte', zusatz: `${system.name} · ${q.name}`,
    hilfe: erklaerung(HILFE.querschnitte.zeilen, HILFE.querschnitte.formel),
    inhalt: [
      el('button.knopf.knopf-klein.bs-zurueck', {
        type: 'button', text: '← alle Querschnitte', on: { click: () => fensterOeffnen('querschnitte') },
      }),
      ...zeilen,
    ],
  });
}

/** Je Querschnitt eine Zeile; ein neuer öffnet gleich sein Fenster. */
function querschnitteInhalt(system) {
  const neu = () => {
    const kennung = naechsteKennung(system.querschnitte, 'Q');
    aendernAn(system.kennung, (s) => {
      s.querschnitte.push({
        ...structuredClone(zustand.katalog.neue_zeilen.stabquerschnitt),
        kennung, name: naechsterName('Querschnitt', s.querschnitte),
      });
    });
    fensterOeffnen(fensterVon(kennung));
  };
  return [
    ...(system.querschnitte.length ? system.querschnitte.map((q, i) => querschnittZeile(system, q, i))
      : [el('p.bs-leer', { text: 'Noch kein Querschnitt.' })]),
    el('button.knopf.knopf-klein', { type: 'button', text: '+ Querschnitt', on: { click: neu } }),
  ];
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

function lastfaelleInhalt(system) {
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
  const neuerFall = () => aendern((s) => {
    const kennung = naechsteKennung(s.lastfaelle, 'LF');
    s.lastfaelle.push({ kennung, name: naechsterName('Lastfall', s.lastfaelle) });
  });
  return [
    ...system.lastfaelle.map(fall),
    el('button.knopf.knopf-klein', { type: 'button', text: '+ Lastfall', on: { click: neuerFall } }),
  ];
}

/** Je Kombination eine Zeile: je Lastfall ein Beiwert, von Hand. */
function kombinationenInhalt(system) {
  const aendern = (veraenderer) => aendernAn(system.kennung, veraenderer);
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
  const neueKombination = () => aendern((s) => {
    s.kombinationen.push({
      kennung: naechsteKennung(s.kombinationen, 'LK'),
      name: naechsterName('Kombination', s.kombinationen),
      faktoren: Object.fromEntries(s.lastfaelle.map((lf) => [lf.kennung, 1.0])),
    });
  });
  if (!system.lastfaelle.length) return [el('p.bs-leer', { text: 'Zuerst einen Lastfall anlegen.' })];
  return [
    system.kombinationen.length ? el('div.tabelle-huelle', {}, [el('table.bs-kombinationen', {}, [
      el('thead', {}, [el('tr', {}, [
        el('th', { text: 'Kombination' }),
        ...system.lastfaelle.map((lf) => el('th', { text: lf.name })),
        el('th'),
      ])]),
      el('tbody', {}, system.kombinationen.map(kombination)),
    ])]) : el('p.bs-leer', { text: 'Noch keine Kombination.' }),
    el('button.knopf.knopf-klein', { type: 'button', text: '+ Kombination', on: { click: neueKombination } }),
  ];
}

// ===========================================================================
// Die Knöpfe der Eingaben
// ===========================================================================

/**
 * Material, Querschnitte, Lastfälle, Kombinationen und die Statik-Analyse
 * als Knöpfe, jeder mit seinem Fenster -- wie die Kapitel der
 * Querschnittsanalyse (Benutzer, 2026-10-24). Unter dem Namen klein, wie
 * viele es gibt.
 */
const KAPITEL = [
  {
    titel: 'Tragwerk',
    kapitel: [
      {
        schluessel: 'material', name: 'Material', titel: 'Materialien', hilfe: HILFE.materialien,
        inhalt: materialienInhalt,
        stand: (s) => zeilenstand(s.stabmaterialien, 'Material', 'Materialien', 'kein Material'),
      },
      {
        schluessel: 'querschnitte', name: 'Querschnitte', titel: 'Querschnitte', hilfe: HILFE.querschnitte,
        inhalt: querschnitteInhalt,
        stand: (s) => zeilenstand(s.querschnitte, 'Querschnitt', 'Querschnitte', 'kein Querschnitt'),
      },
    ],
  },
  {
    titel: 'Lasten',
    kapitel: [
      {
        schluessel: 'lastfaelle', name: 'Lastfälle', titel: 'Lastfälle', inhalt: lastfaelleInhalt,
        stand: (s) => zeilenstand(s.lastfaelle, 'Lastfall', 'Lastfälle', 'kein Lastfall'),
      },
      {
        schluessel: 'kombinationen', name: 'Lastkombi\u00adnationen', titel: 'Lastkombinationen',
        inhalt: kombinationenInhalt,
        stand: (s) => zeilenstand(s.kombinationen, 'Kombination', 'Kombinationen', 'keine'),
      },
    ],
  },
  {
    titel: 'Analyse',
    kapitel: [
      {
        schluessel: 'statik', name: 'Statik-Analyse', titel: 'Statik-Analyse', hilfe: HILFE.statik,
        inhalt: statikInhalt,
        stand: (s) => zeilenstand(s.diagramme, 'Diagramm', 'Diagramme', 'kein Diagramm'),
      },
    ],
  },
];

/** Die Fenster des Systems, nach ihrem Schlüssel: die Kapitel und je Querschnitt seines. */
export function balkensystemFenster(system, schluessel) {
  const [art, kennung] = String(schluessel).split(':');
  return art === 'querschnitt' && kennung ? querschnittFenster(system, kennung)
    : kapitelFenster(system, KAPITEL, schluessel);
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
 * wählen –» da. Ein Knopf mit Fenster wie die Eingaben (Benutzer,
 * 2026-10-24).
 */
function statikInhalt(system) {
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
  return [
    ...(system.diagramme.length ? system.diagramme.map(zeile)
      : [el('div.leer', { text: 'Noch kein Diagramm.' })]),
    anfuegenKnopf('Diagramm', () => aendern((s) => {
      s.diagramme.push(ausVorlage('statikdiagramm', {
        fall: s.kombinationen[0]?.kennung || s.lastfaelle[0]?.kennung || '',
      }));
    })),
  ];
}

// ===========================================================================

export function balkensystemEditor(system) {
  return [systemGruppe(system),
    kapitelPanel(system, KAPITEL, { schluessel: 'balkensystem/Eingaben', titel: 'Eingaben' })];
}
