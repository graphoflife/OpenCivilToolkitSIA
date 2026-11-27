/**
 * qa_schubfluss.js -- die Kachel «Schubfluss» der Querschnittsanalyse.
 *
 * Eigene Lastfälle mit N, V_z und M_y, einachsig um y (Benutzer,
 * 2026-11-27), je mit ihrer Rechenwahl wie eine Spannung-Dehnung-Analyse:
 * die Kriechzahl, je Material die Werte, je Beton die Rechenart. Gerechnet
 * wird in jedem Schnitt der Zeichnung (Werkzeug «Schnitt», qa_schnitt.js)
 * der Schubfluss v -- die Kraft je Meter, die durch den Schnitt in den
 * abgetrennten Teil geht -- und τ = v/b_i. Nur die Einwirkung, ohne
 * Widerstand: ob eine Fuge, die Dübel oder eine Naht ihn tragen, steht
 * nicht hier. Die Ergebnisse stehen in der Zusammenfassung.
 *
 * Jede Querschnittsanalyse hat die Kachel, gleich aus welchem Material:
 * ein Plattenbalken, eine Aufdopplung, ein Verbundträger, eine Naht. Ohne
 * Schnitt sagt sie, dass einer fehlt, grau -- die Fälle bleiben stehen.
 */

import { el, zahlfeld } from './dom.js';
import { anfuegenKnopf, fallzeile } from './faelle.js';
import { fehltHinweis, standOhne, zeilenstand } from './kapitel.js';
import { mitKopf, rechenwahlFelder } from './nachweise.js';
import { werkstoffeVon } from './qa_zeichnung.js';
import { ausVorlage, eintragAendern, feldangabe } from './zustand.js';

/** Unter welchem Namen der Katalog Vorlage und Felder eines Falls führt. */
const KLASSE = 'schubflussfall';

/** Was einem Fall fehlt, solange die Zeichnung keinen Schnitt hat -- sonst nichts. */
function fehlt(analyse) {
  return (analyse.schnitte || []).length ? '' : 'kein Schnitt';
}

/** Die Felder eines Falls: je Schnittgrösse ihr Kopf, ihr Titel und ihr Schritt. */
const FELDER = [
  { feld: 'N_Ed', kopf: 'N_{Ed}', schritt: 50, titel: 'Normalkraft – Zug positiv' },
  { feld: 'V_z_Ed', kopf: 'V_{z,Ed}', schritt: 50, titel: 'Querkraft in z' },
  { feld: 'M_y_Ed', kopf: 'M_{y,Ed}', schritt: 10, titel: 'Moment um y – positiv zieht es unten' },
];

/**
 * Ein Fall als Zeile: Name, N, V_z, M_y und φ, darunter je Material die
 * Werte und je Beton die Rechenart -- wie bei einer Spannung-Dehnung-Analyse.
 */
function fallZeile(analyse, index) {
  const k = analyse.schubflussfaelle[index];
  const aendern = (veraenderer) => eintragAendern(analyse.kennung,
    (e) => veraenderer(e.schubflussfaelle[index]));
  const zahlen = FELDER.map(({ feld, kopf, schritt, titel }) => {
    const angabe = feldangabe(KLASSE, feld);
    return mitKopf([kopf, angabe.einheit], zahlfeld({
      wert: k[feld], schritt, leer: 0, angabe, titel: `${titel}, in ${angabe.einheit}`,
      beiAenderung: (v) => aendern((x) => { x[feld] = v; }),
    }));
  });
  const [phi, werte] = rechenwahlFelder(k, aendern, {
    phiImmer: true, werkstoffe: { ...werkstoffeVon(analyse.kennung), klasse: KLASSE },
  });
  return fallzeile({
    fall: k, aendern, was: 'Lastfall', nameTitel: 'Bezeichnung des Lastfalls',
    liste: { kennung: analyse.kennung, pfad: 'schubflussfaelle', index },
    zahlen: [...zahlen, phi].filter(Boolean),
    unten: [werte],
    entfernenTitel: 'Lastfall entfernen',
    entfernen: () => eintragAendern(analyse.kennung, (e) => { e.schubflussfaelle.splice(index, 1); }),
    klasse: '.ist-spannung',
  });
}

/** Das Fenster: was gerechnet wird, was fehlt, die Fälle und der Knopf für einen weiteren. */
function inhalt(analyse) {
  const faelle = analyse.schubflussfaelle || [];
  return [
    el('p.qa-erlaeuterung', {
      text: 'Je Schnitt der Zeichnung und je Lastfall: der Schubfluss v, die Kraft je Meter, '
        + 'die durch den Schnitt in den abgetrennten Teil geht, und τ = v/b_i über seine Länge '
        + 'im Material. Nur die Einwirkung, ohne Widerstand. Die Ergebnisse stehen in der '
        + 'Zusammenfassung.',
    }),
    fehltHinweis(fehlt(analyse)),
    ...(faelle.length ? faelle.map((_, i) => fallZeile(analyse, i))
      : [el('div.leer', { text: 'Noch kein Lastfall.' })]),
    anfuegenKnopf('Lastfall', (name) => eintragAendern(analyse.kennung, (e) => {
      e.schubflussfaelle = e.schubflussfaelle || [];
      e.schubflussfaelle.push(ausVorlage(KLASSE, { name: name(e.schubflussfaelle) }));
    })),
  ].filter(Boolean);
}

/** Die Kachel, für jede Bauweise dieselbe. */
export const SCHUBFLUSS = {
  schluessel: 'schubfluss',
  name: 'Schubfluss',
  titel: 'Schubfluss in den Schnitten',
  bezug: () => 'N und V_z in kN · M_y in kNm · einachsig um y',
  hilfe: {
    zeilen: [
      ['Schnitt', 'eine Strecke quer durch den Querschnitt; der Pfeil zeigt auf den Teil, den sie abtrennt'],
      ['v', 'wächst M über Δx = 10 mm um V·Δx, wächst die Kraft F′ im abgetrennten Teil um ΔF′ – sie kommt durch den Schnitt'],
      ['F′', 'aus zwei Dehnungsebenen des ganzen Querschnitts, gerissen, mit der Rechenwahl des Falls; elastisch ist v = V·S′/I'],
      ['b_i', 'die Länge, auf der der Schnitt Material von Material trennt'],
    ],
    formel: 'v = ΔF′/Δx, τ = v/b_i',
  },
  inhalt,
  stand: (analyse) => standOhne(zeilenstand(analyse.schubflussfaelle, 'Lastfall', 'Lastfälle', 'kein Lastfall'),
    fehlt(analyse)),
};
