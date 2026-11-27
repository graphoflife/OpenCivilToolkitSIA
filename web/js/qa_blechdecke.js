/**
 * qa_blechdecke.js -- die Blechverbunddecke im Zeichenfenster der Querschnittsanalyse.
 *
 * Eine Decke ist ein Element mit ihrem Beton (2026-11-27): n Rippen an einem
 * Knoten -- ihrer Ecke links unten, der Unterkante der Rippen --, ihr Beton
 * und ihr Profilblech aus Materialien des Projekts, die Masse des Blechs aus
 * seinem Datenblatt. Eingesetzt wird sie mit der Vorlage
 * «Blechverbunddecke» (qa_vorlagen.js), verschoben wie ein Profil, geändert
 * im schwebenden Fenster. Bewehrung zeichnet man in ihren Beton wie in jedes
 * Polygon. Eine Analyse rechnet höchstens eine Decke; eine zweite meldet
 * der Kern rot.
 *
 * Im schwebenden Fenster stehen die Masse unter ihrem Zeichen, «h_p»; ihr
 * Name ist der Titel des Feldes, und darüber zeigt eine Rippe, was jedes
 * Zeichen meint -- beides vom Kern.
 *
 * WAS HIER GERECHNET WIRD -- UND WAS NICHT:
 * Nichts. Den Umriss ihres Betons, die Linie ihres Blechs, wie dick es ist,
 * d_p und b_0 schickt der Kern mit der Antwort zur Zeichnung
 * (`blechdecken`); mitgeschoben wird es wie jedes Element mit einem Umriss
 * vom Kern (qa_umriss.js). Name, Zeichen, Grenze und Einheit jedes Masses
 * kommen aus dem Kern, auch dass eines ein anderes begrenzt: die Rippe
 * niedriger als die Decke, unten schmaler als ihr Abstand.
 */

import { VAR, materialliste } from './bausteine.js';
import { pfad, zahlText } from './cad_ansicht.js';
import { zahlfeldMitVar } from './cad_app.js';
import { cadZeile } from './cad_palette.js';
import { el, svgEl } from './dom.js';
import { skizze } from './qa_skizze.js';
import { gesehen } from './qa_umriss.js';
import { feldangabe } from './zustand.js';

/** Die Masse einer Decke, in der Folge ihrer Felder, je mit dem Schritt der Pfeile. */
export const MASSE = [['h', 10], ['rippen', 1], ['h_p', 5], ['b_s', 10], ['b_o', 5], ['b_u', 5], ['A_p', 50]];

/** Die zwei Materialien einer Decke und wie ihre Zeile heisst. */
export const STOFFE = [['beton', 'Beton'], ['blech', 'Blech']];

/**
 * Die Art der Elemente, für das allgemeine Fenster: ein Punkt mit einem
 * Umriss vom Kern -- ihrem Beton --, darüber die Linie ihres Blechs.
 * Gefangen wird an jeder Ecke des Betons.
 */
export const BLECHDECKE = {
  liste: 'blechdecken', klasse: 'blechdecke', form: 'punkt', vorsilbe: 'B', rang: 5,
  flaeche: { klasse: 'cad-beton' },
  darueber: blechlinie,
  felder: deckenFelder,
  info: deckenInfo,
  titel: () => 'Blechverbunddecke',
  lage: 'Ecke ',
};

/** Die Linie des Blechs einer Decke im Bild -- oder null, solange der Kern sie nicht kennt. */
function blechlinie(a, e, klassen) {
  const g = gesehen(a, BLECHDECKE, e);
  return g && svgEl('path', {
    d: pfad(a.v, g.info.blech.map(g.schieben), false), class: klassen(e.kennung, 'cad-profilblech'),
  });
}

/**
 * Das Feld eines Masses unter seinem Zeichen, im schwebenden Fenster.
 * `neben` sind die Masse der Decke: ein Mass, das
 * ein anderes begrenzt, weist schon das Feld ab -- bei mehreren gewählten
 * nur gegen ein Mass, das alle gemeinsam haben.
 */
function massfeld(feld, schritt, wert, setzen, neben) {
  const angabe = feldangabe('blechdecke', feld);
  return cadZeile(angabe.zeichen, zahlfeldMitVar({
    wert, titel: angabe.heisst, schritt, angabe, beiAenderung: setzen,
    neben: Object.fromEntries(Object.entries(neben).filter(([, w]) => w !== VAR)),
  }), angabe.einheit || '');
}

/** Die Zeile eines Materials der Decke -- von den Arten, die ihr Feld nimmt. */
function stoffzeile(feld, beschriftung, gewaehlt, setzen) {
  return cadZeile(beschriftung, materialliste({
    art: feldangabe('blechdecke', feld).stoffe, gewaehlt, setzen,
  }));
}

/**
 * Die Felder einer Decke -- für eine gewählte wie für mehrere, wie
 * `felderVon` in qa_zeichnung.js. `info` ist, was der Kern zu einer
 * einzelnen weiss: mit ihm steht ihre Rippe mit den Massen darüber.
 */
export function deckenFelder(wert, setzen, info = null) {
  const neben = Object.fromEntries(MASSE.map(([feld]) => [feld, wert(feld)]));
  return [
    info?.rippe ? el('div.cad-rippenbild', {}, [skizze(info.rippe, 200, 120)]) : null,
    ...STOFFE.map(([feld, beschriftung]) => stoffzeile(feld, beschriftung, wert(feld), setzen(feld))),
    ...MASSE.map(([feld, schritt]) => massfeld(feld, schritt, wert(feld), setzen(feld), neben)),
  ];
}

/** Was der Kern zu einer gezeichneten Decke weiss: ihre Breite, d_p, b_0 und das Blech. */
export function deckenInfo(info) {
  if (!info) return [];
  const w = info.werte;
  return [
    el('p.cad-info', {
      text: `b = ${zahlText(w.b)} mm · d_p = ${zahlText(w.d_p)} mm · b_0 = ${zahlText(w.b_0)} mm`,
    }),
    el('p.cad-info', {
      text: `${info.hinterschnitten ? 'Hinterschnittenes' : 'Offenes'} Blech: t = ${zahlText(w.t, 2)} mm, `
        + `e = ${zahlText(w.e)} mm, A = ${zahlText(w.A, 0)} mm² über die Breite b`,
    }),
  ];
}
