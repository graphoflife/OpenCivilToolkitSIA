/**
 * qa_spannglied.js -- das Spannglied im Zeichenfenster der Querschnittsanalyse.
 *
 * Ein Werkzeug «Spannstahl»: ein Glied je Klick, an einem Knoten, aus einem
 * Spannstahl des Projekts. Alles steht am Glied selbst, wie Durchmesser und
 * Material beim Stab (Benutzer, 2026-11-25): welches Erzeugnis seiner Sorte
 * und wie viele davon, wie es wirkt, die Spannungen nach dem Spannen und
 * nach allen Verlusten, der Verbund.
 *
 * Das Erzeugnis wählt eine Zeile je Art -- Draht, Litze, Stab -- mit den
 * Durchmessern, die Tabelle 7 der Sorte nennt (aus dem Katalog des
 * Materials). Gibt es den gewählten in der Sorte nicht, etwa nach dem
 * Wechsel zu einem Stahl, den es nur in Stäben gibt, ist in keiner Zeile
 * einer gewählt, und der Kern sagt grau, dass einer fehlt.
 *
 * WAS HIER GERECHNET WIRD -- UND WAS NICHT:
 * Nichts. Fläche, Spannungen und Spannkraft eines gezeichneten Glieds kommen
 * mit der Antwort des Kerns zur Zeichnung (`spannglieder`), aus derselben
 * Herleitung wie im Bericht -- auch wie gross es sich zeichnet: ein Kreis
 * mit seiner Fläche. Ein leeres Feld der Spannung zeigt grau die Zahl der
 * Vorgabe, sobald der Kern sie kennt; vorher, was die Vorgabe ist
 * («0.70·f_pk», aus dem Katalog).
 */

import { VAR, materialliste, mitBild, mitVar, wahlSchalter } from './bausteine.js';
import { zahlText } from './cad_ansicht.js';
import { zahlfeldMitVar } from './cad_app.js';
import { cadZeile, schalterzeile } from './cad_palette.js';
import { el } from './dom.js';
import {
  ausVorlage, eintragVon, feldangabe, katalog, materialien,
} from './zustand.js';

/** Die Art der Elemente, für das allgemeine Fenster -- ein Punkt wie ein Stab. */
export const SPANNGLIED = { liste: 'spannglieder', klasse: 'spannglied', form: 'punkt', vorsilbe: 'P', rang: 1 };

/** Das Werkzeug, in der Leiste nach der Bewehrung. */
export const SPANNSTAHL = {
  name: 'spannstahl', text: 'Spannstahl', zeichen: 'cad-spannglied', taste: 's', form: 'knoten',
  titel: 'Spannstahl: ein Spannglied je Klick – Drähte, Litzen oder Stäbe',
};

/** Was das Werkzeug als Nächstes anlegt: nach der Vorlage des Kerns, aus dem ersten Spannstahl. */
export function gliedVorgabe() {
  return ausVorlage('spannglied', { stahl: materialien('spannstahl')[0]?.kennung || '' });
}

/** Einem Spannstahl, den es nicht mehr gibt, folgt in der Vorgabe der erste -- wie beim Stab. */
export function vorgabePruefen(v) {
  if (!materialien('spannstahl').some((m) => m.kennung === v.stahl)) {
    v.stahl = materialien('spannstahl')[0]?.kennung || '';
  }
}

/** Die Erzeugnisse der Sorte eines Spannstahls, wie Tabelle 7 sie nennt -- leer ohne Spannstahl. */
function erzeugnisse(stahl) {
  const m = stahl && stahl !== VAR ? eintragVon(stahl) : null;
  if (!m || m.art !== 'spannstahl') return [];
  return katalog('materialarten', 'spannstahl', 'erzeugnisse')[m.sorte] || [];
}

/** Das Erzeugnis eines Glieds -- oder null, solange es keines hat. */
function erzeugnisVon(e) {
  return erzeugnisse(e.stahl).find((x) => x.durchmesser === e.durchmesser) || null;
}

/** Was ein Glied ist, in Worten: «4 × Litze ⌀15.7» -- ohne Erzeugnis nur der Durchmesser. */
export function gliedText(e) {
  const erz = erzeugnisVon(e);
  return `${e.anzahl} × ${erz ? `${erz.beschriftung} ` : ''}⌀${zahlText(e.durchmesser)}`;
}

/**
 * Je Art eine Zeile mit ihren Durchmessern in mm: «Litze ⌀ [12.9 | 15.3 |
 * 15.7]» -- ohne Einheit dahinter, sonst passten vier Stäbe nicht ins
 * Fenster. Gewählt ist, was das Glied hat -- bei mehreren verschiedenen
 * nichts, und ein Satz sagt es.
 */
function erzeugnisZeilen(wert, setzen) {
  const stahl = wert('stahl');
  if (stahl === VAR) {
    return [el('p.cad-hinweis-klein', {
      text: 'Die gewählten haben verschiedene Spannstähle – erst einen wählen, dann ihr Erzeugnis.',
    })];
  }
  const liste = erzeugnisse(stahl);
  if (!liste.length) {
    return [el('p.cad-hinweis-klein', { text: 'Erst einen Spannstahl wählen – dann seine Drähte, Litzen oder Stäbe.' })];
  }
  const durchmesser = wert('durchmesser');
  const arten = [...new Set(liste.map((x) => x.art))];
  return [
    ...arten.map((art) => {
      const je = liste.filter((x) => x.art === art);
      return schalterzeile(`${je[0].beschriftung} ⌀`, wahlSchalter({
        werte: je.map((x) => ({
          wert: x.durchmesser, beschriftung: zahlText(x.durchmesser),
          titel: `${x.bezeichnung}: ⌀${zahlText(x.durchmesser)} mm, ${zahlText(x.flaeche)} mm² je ${x.beschriftung}`,
        })),
        gewaehlt: durchmesser, setzen: setzen('durchmesser'),
        titel: `${je[0].beschriftung}: Durchmesser in mm nach Tabelle 7`, klasse: '.cad-wahl.ist-eng',
      }));
    }),
    durchmesser === VAR ? el('p.cad-hinweis-klein', {
      text: 'Die gewählten unterscheiden sich im Erzeugnis – was man wählt, gilt für alle.',
    }) : null,
  ];
}

/**
 * Die Felder eines Glieds -- für die Vorgabe des Werkzeugs wie für gewählte
 * Glieder, wie `felderVon` in qa_zeichnung.js. `info` ist, was der Kern zu
 * einem einzelnen weiss: mit ihm zeigt ein leeres Feld der Spannung die Zahl
 * der Vorgabe. Die Grenzen jeder Zahl kommen aus dem Kern.
 */
export function gliedFelder(wert, setzen, info = null) {
  const sp = katalog('querschnittsanalyse', 'spannglied');
  const angabe = (feld) => feldangabe('spannglied', feld);
  const neben = { sigma_p0: wert('sigma_p0'), sigma_pinf: wert('sigma_pinf') };
  const spannung = (feld, titel) => {
    const gerechnet = info?.werte?.[feld];
    return cadZeile(angabe(feld).heisst, zahlfeldMitVar({
      wert: wert(feld), titel: `${titel} – leer: ${sp.vorgaben[feld]}`, schritt: 10,
      angabe: angabe(feld), neben: Object.fromEntries(Object.entries(neben).filter(([, w]) => w !== VAR)),
      leer: null, platzhalter: gerechnet === undefined ? sp.vorgaben[feld] : zahlText(gerechnet, 0),
      beiAenderung: setzen(feld),
    }), angabe(feld).einheit);
  };
  const schalter = (feld, stellungen, titel, bild = null) => wahlSchalter({
    werte: mitVar((bild ? mitBild(stellungen, bild) : stellungen).map((x) => ({
      ...x, beschriftung: x.kurz || x.beschriftung,
    })), wert(feld)),
    gewaehlt: wert(feld), setzen: setzen(feld), titel, klasse: bild ? '.cad-wahl.ist-gross' : '.cad-wahl',
  });
  return [
    cadZeile('Stahl', materialliste({ art: 'spannstahl', gewaehlt: wert('stahl'), setzen: setzen('stahl') })),
    ...erzeugnisZeilen(wert, setzen),
    cadZeile(angabe('anzahl').heisst, zahlfeldMitVar({
      wert: wert('anzahl'), titel: 'Wie viele Drähte, Litzen oder Stäbe das Glied hat', schritt: 1,
      angabe: angabe('anzahl'), beiAenderung: setzen('anzahl'),
    })),
    schalter('wirkung', sp.wirkungen, 'Wie das Glied im Widerstand zählt', 'wirkung'),
    spannung('sigma_p0', 'Spannung nach dem Spannen'),
    spannung('sigma_pinf', 'Spannung nach allen Verlusten'),
    schalterzeile('Verbund', schalter('verbund', sp.verbunde, 'Ob das Glied mit dem Beton verbunden ist')),
  ];
}

/** Was der Kern zu einem gezeichneten Glied weiss -- Erzeugnis, Fläche, Spannkraft --, als Zeilen. */
export function gliedInfo(e, info) {
  const w = info?.werte;
  if (!w) return [];
  const vordehnung = e.verbund === 'mit' ? ` · ε_p = ${zahlText(w.eps_p, 2)} ‰` : '';
  return [
    `${w.erzeugnis} · A_p = ${zahlText(w.A_p, 0)} mm²`,
    `σ_p∞ = ${zahlText(w.sigma_pinf, 0)} N/mm²${vordehnung} · P∞ = ${zahlText(w.P_inf, 0)} kN`,
  ].map((t) => el('p.cad-info', { text: t }));
}
