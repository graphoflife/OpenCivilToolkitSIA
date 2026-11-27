/**
 * qa_spannglied.js -- das Spannglied im Zeichenfenster der Querschnittsanalyse.
 *
 * Ein Werkzeug «Spannstahl»: ein Glied je Klick, an einem Knoten, aus einem
 * Spannstahl des Projekts. Alles steht am Glied selbst, wie Durchmesser und
 * Material beim Stab (Benutzer, 2026-11-25): wie viel Stahl, wie es wirkt,
 * die Faktoren der Spannungen nach dem Spannen und nach allen Verlusten, der
 * Verbund.
 *
 * WIE VIEL STAHL (Benutzer, 2026-11-27):
 * Ein Schalter «Menge» wählt, woher die Fläche kommt. Aus einem Erzeugnis:
 * je Art -- Draht, Litze, Stab -- eine Zeile mit den Durchmessern, die
 * Tabelle 7 der Sorte nennt (aus dem Katalog des Materials), und die Anzahl.
 * Eingegeben: die Fläche A_p und die Art, unter denen der Sorte. Gibt es das
 * Gewählte in der Sorte nicht, etwa nach dem Wechsel zu einem Stahl, den es
 * nur in Stäben gibt, ist nichts gewählt, und der Kern sagt grau, was fehlt.
 *
 * DIE SPANNUNGEN (Benutzer, 2026-11-27):
 * Eingegeben sind Faktoren, je höchstens 1, als Zeile wie die Formel:
 * «σ_p0 = [0.70] · f_pk = 1302 N/mm²». Wie die Zeile steht, sagt der
 * Katalog; die Spannung dahinter kommt vom Kern, sobald er das Glied kennt.
 * Bis 2026-11-27 waren σ_p0 und σ_p∞ selbst die Felder.
 *
 * WAS HIER GERECHNET WIRD -- UND WAS NICHT:
 * Nichts. Fläche, Spannungen und Spannkraft eines gezeichneten Glieds kommen
 * mit der Antwort des Kerns zur Zeichnung (`spannglieder`), aus derselben
 * Herleitung wie im Bericht -- auch wie gross es sich zeichnet: ein Kreis
 * mit seiner Fläche.
 *
 * Die Neigung β_p zählt nur mit Vordehnung: welche Wirkung sie zulässt und
 * was ihr Feld sagt, steht im Katalog. Schlaff steht an ihrer Stelle ein
 * Satz, warum sie fehlt -- die Zahl bleibt am Glied, für den Weg zurück.
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

/** Die Arten der Sorte eines Spannstahls, für die eingegebene Fläche -- wie Tabelle 7 sie nennt. */
function artenVon(stahl) {
  const da = new Set(erzeugnisse(stahl).map((x) => x.art));
  return katalog('querschnittsanalyse', 'spannglied').arten.filter((a) => da.has(a.wert));
}

/**
 * Was ein Glied ist, in Worten: «4 × Litze ⌀15.7» -- ohne Erzeugnis nur der
 * Durchmesser; mit eingegebener Fläche «Litzen A_p 1800 mm²».
 */
export function gliedText(e) {
  if (e.flaechenangabe === 'flaeche') {
    const art = katalog('querschnittsanalyse', 'spannglied').arten.find((a) => a.wert === e.art);
    return `${art ? `${art.mehrzahl} ` : ''}A_p ${zahlText(e.flaeche)} mm²`;
  }
  const erz = erzeugnisVon(e);
  return `${e.anzahl} × ${erz ? `${erz.beschriftung} ` : ''}⌀${zahlText(e.durchmesser)}`;
}

/** Was statt der Felder steht, solange kein einzelner Spannstahl gewählt ist -- sonst null. */
function ohneStahl(stahl, wofuer) {
  if (stahl === VAR) {
    return el('p.cad-hinweis-klein', {
      text: `Die gewählten haben verschiedene Spannstähle – erst einen wählen, dann ihr${wofuer}.`,
    });
  }
  if (!erzeugnisse(stahl).length) {
    return el('p.cad-hinweis-klein', { text: 'Erst einen Spannstahl wählen – dann seine Drähte, Litzen oder Stäbe.' });
  }
  return null;
}

/**
 * Je Art eine Zeile mit ihren Durchmessern in mm: «Litze ⌀ [12.9 | 15.3 |
 * 15.7]» -- ohne Einheit dahinter, sonst passten vier Stäbe nicht ins
 * Fenster. Gewählt ist, was das Glied hat -- bei mehreren verschiedenen
 * nichts, und ein Satz sagt es.
 */
function erzeugnisZeilen(wert, setzen) {
  const stahl = wert('stahl');
  const fehlt = ohneStahl(stahl, ' Erzeugnis');
  if (fehlt) return [fehlt];
  const liste = erzeugnisse(stahl);
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
 * einem einzelnen weiss: mit ihm steht hinter jedem Faktor seine Spannung.
 * Die Grenzen jeder Zahl kommen aus dem Kern.
 */
export function gliedFelder(wert, setzen, info = null) {
  const sp = katalog('querschnittsanalyse', 'spannglied');
  const angabe = (feld) => feldangabe('spannglied', feld);
  const schalter = (feld, stellungen, titel, bild = null) => wahlSchalter({
    werte: mitVar((bild ? mitBild(stellungen, bild) : stellungen).map((x) => ({
      ...x, beschriftung: x.kurz || x.beschriftung,
    })), wert(feld)),
    gewaehlt: wert(feld), setzen: setzen(feld), titel, klasse: bild ? '.cad-wahl.ist-gross' : '.cad-wahl',
  });
  // «σ_p0 = [0.70] · f_pk = 1302 N/mm²» -- die Zahl hinten erst, wenn der Kern sie kennt.
  const faktor = (f) => {
    const gerechnet = info?.werte?.[f.spannung];
    return cadZeile(f.vor, zahlfeldMitVar({
      wert: wert(f.feld), titel: f.titel, schritt: 0.01, angabe: angabe(f.feld), beiAenderung: setzen(f.feld),
    }), gerechnet === undefined ? f.nach : `${f.nach} = ${zahlText(gerechnet, 0)} N/mm²`);
  };
  return [
    cadZeile('Stahl', materialliste({ art: 'spannstahl', gewaehlt: wert('stahl'), setzen: setzen('stahl') })),
    schalterzeile('Menge', schalter('flaechenangabe', sp.angaben, 'Woher die Fläche des Glieds kommt')),
    ...mengenZeilen(wert, setzen, schalter),
    schalter('wirkung', sp.wirkungen, 'Wie das Glied im Widerstand zählt', 'wirkung'),
    ...sp.faktoren.map(faktor),
    schalterzeile('Verbund', schalter('verbund', sp.verbunde, 'Ob das Glied mit dem Beton verbunden ist')),
    ...neigungZeilen(wert, setzen, sp),
  ];
}

/**
 * Was zur Wahl der Menge gehört: aus einem Erzeugnis seine Zeilen und die
 * Anzahl, eingegeben die Fläche und die Art. Haben mehrere Gewählte
 * verschiedene, sagt es ein Satz.
 */
function mengenZeilen(wert, setzen, schalter) {
  const angabe = (feld) => feldangabe('spannglied', feld);
  const zahl = (feld, titel, schritt) => cadZeile(angabe(feld).zeichen || angabe(feld).heisst, zahlfeldMitVar({
    wert: wert(feld), titel, schritt, angabe: angabe(feld), beiAenderung: setzen(feld),
  }), angabe(feld).einheit);
  const menge = wert('flaechenangabe');
  if (menge === VAR) {
    return [el('p.cad-hinweis-klein', {
      text: 'Die gewählten unterscheiden sich in der Menge – erst eine wählen, dann gelten ihre Felder für alle.',
    })];
  }
  if (menge === 'erzeugnis') {
    return [...erzeugnisZeilen(wert, setzen), zahl('anzahl', 'Wie viele Drähte, Litzen oder Stäbe das Glied hat', 1)];
  }
  const fehlt = ohneStahl(wert('stahl'), 'e Art');
  return [
    zahl('flaeche', 'Die Fläche des ganzen Glieds', 10),
    fehlt || schalterzeile('Art', schalter('art', artenVon(wert('stahl')), 'Draht, Litze oder Stab: daran hängt E_p')),
  ];
}

/** Das Feld der Neigung mit seinem Satz darunter -- oder, wo sie nicht zählt, warum. */
function neigungZeilen(wert, setzen, sp) {
  const wirkung = wert('wirkung');
  const zaehlt = wirkung === VAR || sp.wirkungen.some((w) => w.wert === wirkung && w.neigung);
  if (!zaehlt) return [el('p.cad-hinweis-klein', { text: sp.neigung.ohne })];
  const angabe = feldangabe('spannglied', 'neigung');
  return [
    cadZeile(angabe.heisst, zahlfeldMitVar({
      wert: wert('neigung'), titel: sp.neigung.titel, schritt: 1, angabe, beiAenderung: setzen('neigung'),
    }), angabe.einheit),
    el('p.cad-hinweis-klein', { text: sp.neigung.hinweis }),
  ];
}

/** Was der Kern zu einem gezeichneten Glied weiss -- Erzeugnis, Fläche, Spannkraft --, als Zeilen. */
export function gliedInfo(e, info) {
  const w = info?.werte;
  if (!w) return [];
  const vordehnung = e.verbund === 'mit' ? ` · ε_p = ${zahlText(w.eps_p, 2)} ‰` : '';
  return [
    `${w.bezeichnung} · A_p = ${zahlText(w.A_p, 0)} mm²`,
    `σ_p∞ = ${zahlText(w.sigma_pinf, 0)} N/mm²${vordehnung} · P∞ = ${zahlText(w.P_inf, 0)} kN`,
    // Nur geneigt mit Vordehnung: was es von einem gleich gerichteten V_z trägt.
    w.V_p === undefined ? null
      : `β_p = ${zahlText(e.neigung, 1)}° · lotrecht P∞·sin β_p = ${zahlText(w.V_p, 1)} kN`,
  ].filter(Boolean).map((t) => el('p.cad-info', { text: t }));
}
