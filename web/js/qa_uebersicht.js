/**
 * qa_uebersicht.js -- die Liste unter dem Zeichenfenster: was gezeichnet ist.
 *
 * Nur zum Lesen -- bearbeitet wird im Zeichenfenster. Von oben nach unten:
 *
 *   Meldungen          was der Kern an der Zeichnung beanstandet
 *   Querschnitt        A, y_S, z_S und I_y, I_z, I_yz, brutto
 *   Elemente           je Art eine Gruppe, je Element eine Zeile
 *
 * Ein Klick auf eine Meldung oder eine Zeile wählt das Element im Fenster.
 * Jede Zahl steht so in der Eingabe oder kommt vom Kern; gerechnet wird hier
 * nichts.
 */

import { zahlText } from './cad_ansicht.js';
import { imSpiel } from './cad_auswahl.js';
import { el } from './dom.js';
import { span } from './mathe.js';
import {
  elementname, linienText, passendeGeometrie, stoffname, waehlen,
} from './qa_zeichnung.js';

/** Eine Zeile: Name, was es ist, und rechts die eine Zahl, die zählt. */
function zeile(a, fehler, kennung, was, wert = '') {
  return el('button.qa-element', {
    type: 'button',
    class: [fehler.has(kennung) ? 'ist-fehler' : '', imSpiel(a).has(kennung) ? 'ist-gewaehlt' : ''].join(' '),
    dataset: { kennung },
    title: fehler.get(kennung)?.join('\n') || 'Im Zeichenfenster wählen',
    on: { click: () => waehlen(a.qa.kennung, [kennung]) },
  }, [
    el('span.qa-element-name', { text: elementname(a, kennung) }),
    el('span.qa-element-was', { text: was }),
    el('span.qa-element-wert', { text: wert }),
  ]);
}

function gruppe(titel, zeilen) {
  if (!zeilen.length) return null;
  return el('div.qa-gruppe', {}, [el('div.qa-gruppentitel', { text: titel }), ...zeilen]);
}

/** Die Werte des Bruttoquerschnitts in zwei Spalten, die Ziffern untereinander. */
function werte(b) {
  const wert = (symbol, zahl, einheit) => [
    el('span.qa-wert-symbol', {}, [span(symbol)]),
    el('span.qa-wert-zahl', { text: zahl }),
    el('span.qa-wert-einheit', { text: einheit }),
  ];
  const traeg = (w) => zahlText(w / 1e6, 1);
  return el('div.qa-werte', { title: 'Bruttoquerschnitt, vom Kern gerechnet' }, [
    ...wert('A', zahlText(b.A, 0), 'mm²'), ...wert('I_y', traeg(b.I_y), '10⁶ mm⁴'),
    ...wert('y_S', zahlText(b.y_S), 'mm'), ...wert('I_z', traeg(b.I_z), '10⁶ mm⁴'),
    ...wert('z_S', zahlText(b.z_S), 'mm'), ...wert('I_{yz}', traeg(b.I_yz), '10⁶ mm⁴'),
  ]);
}

/** Die Liste zur Analyse des Fensters `a`. */
export function uebersicht(a) {
  const z = a.adapter.zeichnung();
  if (!z) return [];
  const g = passendeGeometrie(a);
  const fehler = new Map();
  for (const m of g?.meldungen || []) {
    for (const k of m.elemente) fehler.set(k, [...(fehler.get(k) || []), m.text]);
  }
  const lagen = a.modell.lagen(z);
  const lage = (k) => {
    const p = lagen.get(k);
    return p ? `(${zahlText(p[0])}, ${zahlText(p[1])})` : '';
  };
  const linieninfo = new Map((g?.linien || []).map((x) => [x.kennung, x]));
  const wandinfo = new Map((g?.waende || []).map((x) => [x.kennung, x]));

  const teile = [];
  if (g?.meldungen?.length) {
    teile.push(el('div.qa-meldungen', {}, g.meldungen.map((m) => el('button.qa-meldung', {
      type: 'button', text: m.text, title: 'Im Zeichenfenster wählen',
      on: { click: () => waehlen(a.qa.kennung, m.elemente) },
    }))));
  }
  if (g?.brutto) teile.push(werte(g.brutto));

  const gruppen = [
    gruppe('Flächen', z.flaechen.map((f) => zeile(a, fehler, f.kennung,
      f.material ? stoffname(f.material) : 'nimmt Fläche weg', `${f.knoten.length} Ecken`))),
    gruppe('Stäbe', z.staebe.map((s) => zeile(a, fehler, s.kennung,
      `⌀${zahlText(s.durchmesser)} ${stoffname(s.stahl)}`, lage(s.knoten)))),
    gruppe('Bewehrung', z.stablinien.map((l) => {
      const info = linieninfo.get(l.kennung);
      return zeile(a, fehler, l.kennung, linienText(l, info) || '–',
        info?.punkte ? `A_s ${zahlText(info.flaeche, 0)} mm²` : '');
    })),
    gruppe('Schubwände', z.schubwaende.map((w) => {
      const info = wandinfo.get(w.kennung);
      return zeile(a, fehler, w.kennung,
        `b_w ${zahlText(w.dicke)} · ⌀${zahlText(w.durchmesser)} @ ${zahlText(w.teilung)} · ${w.schnitte}-schnittig`,
        info ? `A_sw/s ${zahlText(info.a_sw_s, 0)} mm²/m` : '');
    })),
    gruppe('Hilfslinien', (z.hilfslinien || []).map((h) => zeile(a, fehler, h.kennung,
      `${h.von} – ${h.bis}`))),
  ].filter(Boolean);

  teile.push(gruppen.length
    ? el('div.qa-elemente', {}, gruppen)
    : el('p.qa-leer', { text: 'Noch nichts gezeichnet: Polygon P, Linie L oder Knoten K.' }));
  return teile;
}
