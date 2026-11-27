/**
 * qa_profile.js -- das Stahlprofil im Zeichenfenster der Querschnittsanalyse.
 *
 * Ein Profil bleibt ein Profil (Benutzer, 2026-11-25): eine Grösse einer
 * Reihe der Tabelle, an einem Knoten -- seiner Mitte --, aus einem Baustahl
 * des Projekts, gedreht und gespiegelt. Eingesetzt wird es mit der Vorlage
 * «Stahlprofil» (qa_vorlagen.js), verschoben wie ein Stab, geändert im
 * schwebenden Fenster. Freie Bleche zeichnet man als Polygon aus Baustahl.
 *
 * Reihe und Grösse wählt man wie beim Stahlprofil im Balkensystem
 * (profilwahl.js). Drehung und Spiegeln stehen nur da, wo sie das Profil
 * ändern -- ein Rundrohr dreht sich nicht, ein I spiegelt sich nicht --:
 * das sagt der Kern.
 *
 * WAS HIER GERECHNET WIRD -- UND WAS NICHT:
 * Nichts. Den Umriss eines Profils -- gedreht, gespiegelt, mit seinem Loch
 * --, seine Fläche, seine Masse von aussen und woran der Zeiger fängt,
 * schickt der Kern mit der Antwort zur Zeichnung (`profile`); mitgeschoben
 * wird es wie jedes Element mit einem Umriss vom Kern (qa_umriss.js).
 */

import {
  VAR, hakenSchalter, materialliste, mitVar, wahlBlock, wahlSchalter,
} from './bausteine.js';
import { zahlText } from './cad_ansicht.js';
import { jaNein } from './cad_app.js';
import { cadZeile, schalterzeile } from './cad_palette.js';
import { el } from './dom.js';
import { groessenListe, reihenSchalter } from './profilwahl.js';
import { feldangabe, katalog } from './zustand.js';

/**
 * Die Art der Elemente, für das allgemeine Fenster: ein Punkt mit einem
 * Umriss vom Kern (qa_umriss.js), aus Baustahl, sein Loch gerade-ungerade
 * ausgespart. Gefangen wird an den Ecken und Seitenmitten seines Rahmens.
 * Liegen Ecken aufeinander, kommt das Profil nach den Flächen dran.
 */
export const PROFIL = {
  liste: 'profile', klasse: 'profil', form: 'punkt', vorsilbe: 'R', rang: 5,
  flaeche: { klasse: 'cad-baustahl', 'fill-rule': 'evenodd' },
  felder: profilFelder,
  info: profilInfo,
  titel: (e) => (e ? e.profil : 'Stahlprofil'),
  lage: 'Mitte ',
};

/**
 * Drehung und Spiegeln -- nur, wo sie das Profil ändern: das sagt `info`
 * vom Kern (`drehbar`, `spiegelbar`). Ohne `info` -- bei mehreren gewählten
 * -- stehen beide da. Beim U ist gespiegelt dasselbe wie um 180° gedreht;
 * beides bleibt, wie man es denkt. Die vier Drehungen stehen unter ihrem
 * Namen, wie jede Wahl mit mehr als zwei Stellungen im schwebenden Fenster:
 * neben ihm hätten sie dort keinen Platz.
 */
export function drehZeilen(wert, setzen, info = null) {
  const titel = 'Gespiegelt an der senkrechten Achse durch die Mitte – beim U der Rücken rechts';
  const gespiegelt = wert('gespiegelt');
  return [
    info?.drehbar === false ? null : wahlBlock('Drehung', wahlSchalter({
      werte: mitVar(katalog('querschnittsanalyse', 'profil', 'drehungen'), wert('drehung')),
      gewaehlt: wert('drehung'), setzen: setzen('drehung'),
      titel: 'Um die Mitte gedreht, gegen den Uhrzeigersinn', klasse: '.cad-wahl.ist-eng',
    })),
    info?.spiegelbar === false ? null : schalterzeile('Gespiegelt', gespiegelt === VAR
      ? jaNein(VAR, setzen('gespiegelt'), titel) : hakenSchalter(gespiegelt, setzen('gespiegelt'), titel)),
  ].filter(Boolean);
}

/**
 * Die Felder eines Profils -- für ein gewähltes wie für mehrere, wie
 * `felderVon` in qa_zeichnung.js. `info` ist, was der Kern zu einem
 * einzelnen weiss.
 */
export function profilFelder(wert, setzen, info = null) {
  const profil = wert('profil');
  const groessen = groessenListe(profil, setzen('profil'));
  return [
    wahlBlock('Reihe', reihenSchalter(profil, setzen('profil'), '.cad-wahl')),
    groessen ? cadZeile('Profil', groessen) : null,
    profil === VAR ? el('p.cad-hinweis-klein', {
      text: 'Die gewählten sind verschiedene Profile – eine Reihe wählen, dann gilt ihr kleinstes für alle.',
    }) : null,
    cadZeile('Stahl', materialliste({
      art: feldangabe('profil', 'stahl').stoffe, gewaehlt: wert('stahl'), setzen: setzen('stahl'),
    })),
    ...drehZeilen(wert, setzen, info),
  ];
}

/** Was der Kern zu einem gezeichneten Profil weiss -- seine Masse von aussen und seine Fläche. */
export function profilInfo(info) {
  if (!info) return [];
  return [el('p.cad-info', {
    text: `${zahlText(info.breite)} × ${zahlText(info.hoehe)} mm · A = ${zahlText(info.A, 0)} mm²`,
  })];
}
