/**
 * qa_uebersicht.js -- die Liste unter dem Zeichenfenster: was gezeichnet ist.
 *
 * Nur zum Lesen -- bearbeitet wird im Zeichenfenster. Von oben nach unten:
 *
 *   Meldungen          was der Kern an der Zeichnung beanstandet
 *   Querschnitt        A, y_S, z_S und I_y, I_z, I_yz, brutto
 *   Elemente           je Art eine Gruppe, je Element eine Zeile -- jede
 *                      klappt auf und zu, zu Beginn zu
 *
 * Meldungen, Gruppen und Zeilen baut cad_app.js, wie im Balkensystem und in
 * der Decke; ein Klick wählt das Element im Fenster. Jede Zahl steht so in
 * der Eingabe oder kommt vom Kern; gerechnet wird hier nichts.
 */

import { zahlText } from './cad_ansicht.js';
import {
  frischeAntwort, listengruppen, listenzeilen, meldungsliste,
} from './cad_app.js';
import { el } from './dom.js';
import { span } from './mathe.js';
import { elementname, linienText, stoffname } from './qa_zeichnung.js';

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

/** Die Liste zur Analyse des Fensters `a`: je Element sein Name, was es ist, und rechts die eine Zahl, die zählt. */
export function uebersicht(a) {
  const z = a.adapter.zeichnung();
  if (!z) return [];
  const g = frischeAntwort(a);
  const lagen = a.modell.lagen(z);
  const lage = (k) => {
    const p = lagen.get(k);
    return p ? `(${zahlText(p[0])}, ${zahlText(p[1])})` : '';
  };
  const linieninfo = new Map((g?.linien || []).map((x) => [x.kennung, x]));
  const wandinfo = new Map((g?.waende || []).map((x) => [x.kennung, x]));
  const zeile = listenzeilen(a);
  const element = (kennung, was, wert = '') => zeile({ kennung, name: elementname(a, kennung), was, wert });
  return [
    meldungsliste(a),
    g?.brutto ? werte(g.brutto) : null,
    ...listengruppen(a, [
      ['Flächen', z.flaechen.map((f) => element(f.kennung,
        f.material ? stoffname(f.material) : 'nimmt Fläche weg', `${f.knoten.length} Ecken`))],
      ['Stäbe', z.staebe.map((s) => element(s.kennung,
        `⌀${zahlText(s.durchmesser)} ${stoffname(s.stahl)}`, lage(s.knoten)))],
      ['Bewehrung', z.stablinien.map((l) => {
        const info = linieninfo.get(l.kennung);
        return element(l.kennung, linienText(l, info) || '–', info?.punkte ? `A_s ${zahlText(info.flaeche, 0)} mm²` : '');
      })],
      ['Schubwände', z.schubwaende.map((w) => {
        const info = wandinfo.get(w.kennung);
        return element(w.kennung,
          `b_w ${zahlText(w.dicke)} · ⌀${zahlText(w.durchmesser)} @ ${zahlText(w.teilung)} · ${w.schnitte}-schnittig`,
          info ? `A_sw/s ${zahlText(info.a_sw_s, 0)} mm²/m` : '');
      })],
      ['Hilfslinien', (z.hilfslinien || []).map((h) => element(h.kennung, `${h.von} – ${h.bis}`))],
    ]),
  ];
}
