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
 * schickt der Kern mit der Antwort zur Zeichnung (`profile`). Hier wird das
 * nur mitgeschoben: um das, was sein Knoten seit der Antwort gewandert ist,
 * bis die nächste da ist.
 */

import {
  VAR, hakenSchalter, materialliste, mitVar, wahlBlock, wahlSchalter,
} from './bausteine.js';
import { pfad, zahlText } from './cad_ansicht.js';
import { jaNein } from './cad_app.js';
import { cadZeile, schalterzeile } from './cad_palette.js';
import { el } from './dom.js';
import { groessenListe, reihenSchalter } from './profilwahl.js';
import { feldangabe, katalog } from './zustand.js';

/**
 * Die Art der Elemente, für das allgemeine Fenster: ein Punkt mit Fläche
 * (`profilUmriss`). Liegen Ecken aufeinander, kommt das Profil nach den
 * Flächen dran.
 */
export const PROFIL = { liste: 'profile', klasse: 'profil', form: 'punkt', vorsilbe: 'R', rang: 5 };

/**
 * Was der Kern zuletzt über ein Profil sagte -- auch in einer älteren
 * Antwort: es ist nur das Bild --, und wie seine Punkte mit dem Knoten
 * mitgehen. Null, solange er es nicht kennt: vor der ersten Antwort, oder
 * bei einem Namen, den die Tabelle nicht hat.
 */
function gesehen(a, e) {
  const info = a.adapter.kern.antwort?.profile?.find((x) => x.kennung === e.kennung);
  const p = a.modell.lagen(a.adapter.zeichnung()).get(e.knoten);
  if (!info || !p) return null;
  const [dy, dz] = [p[0] - info.lage[0], p[1] - info.lage[1]];
  return { info, schieben: ([y, z]) => [y + dy, z + dz] };
}

/** Die Umrisse eines Profils in der Zeichnung, der erste aussen, die weiteren Löcher -- oder null. */
export function profilUmriss(a, e) {
  const g = gesehen(a, e);
  return g && g.info.umriss.map((teil) => teil.map(g.schieben));
}

/** Woran der Zeiger an den Profilen fängt: die Ecken und Seitenmitten ihres Rahmens. */
export function profilFang(a, z) {
  return (z.profile || []).flatMap((e) => {
    const g = gesehen(a, e);
    return g ? g.info.fang.map((p) => ({ p: g.schieben(p) })) : [];
  });
}

/** Der Pfad eines Profils im Bild, sein Loch gerade-ungerade ausgespart -- oder null. */
export function profilPfad(a, e) {
  const teile = profilUmriss(a, e);
  return teile && teile.map((teil) => pfad(a.v, teil)).join(' ');
}

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

/** Setzt ein Profil `e` mit seiner Mitte an `p` ein -- an einen neuen Knoten oder einen, der dort liegt. */
export function profilEinsetzen(a, e, p) {
  let neu = null;
  a.aendern((z) => {
    const knoten = a.modell.knotenAn(z, p);
    neu = a.modell.naechsteKennung(z, PROFIL.vorsilbe);
    z.profile.push({ ...structuredClone(e), kennung: neu, knoten });
  }, { auswahl: () => [neu] });
}
