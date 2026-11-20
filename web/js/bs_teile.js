/**
 * bs_teile.js -- was Zeichnung, schwebendes Fenster und Panels eines
 * Balkensystems gemeinsam brauchen.
 *
 * Ein Balkensystem ist eben (2D) oder räumlich (3D); beide nutzen dieselben
 * Module. Was eine Art anders hat, sagt ihr Katalog (`systemkatalog`): die
 * Achsen, die Felder eines Lagers, die Linienlager, die Richtungen der
 * Lasten, die Grössen der Ergebnisse. Welche Art ein System ist, sagt die
 * Liste des Projekts, in der es steht (`systemart`).
 *
 * Dazu die Art einer Last nach dem Katalog des Kerns, die Last zu einer
 * Kennung, die Zugseite einer Linie in der Ebene und der Name eines
 * Materials -- und die Antwort des Kerns, solange sie zur Fassung des
 * Projekts passt: was ein Fenster betrifft, nimmt das Fenster `a`
 * (bs_zeichnung.js), nicht seine Kennung -- so liest das schwebende Fenster
 * es ohne Umweg über den Adapter. Den Lastfall, den ein Fenster zeigt, führt
 * lastfaelle.js. Nichts davon rechnet: es liest die Beschreibung, den
 * Katalog und die Materialien des Projekts.
 */

import { ARTEN } from './arten.js';
import { eintragVon, katalog, zustand } from './zustand.js';

/** Die Art eines Systems -- 'balkensystem' oder 'balkensystem3d': die der Liste, in der es steht. */
export function systemart(kennung) {
  return ARTEN.find((x) => (zustand.projekt?.[x.liste] || []).some((e) => e.kennung === kennung))?.art;
}

/**
 * Was der Kern im Katalog einer Art von Balkensystem sagt -- beide haben
 * dieselben Schlüssel (opencivil/web/systemkatalog.py).
 */
export function systemkatalog(art, ...pfad) {
  return katalog(art, ...pfad);
}

/** Ob eine Art von Balkensystem im Raum liegt: drei Achsen statt zwei. */
export function raeumlich(art) {
  return systemkatalog(art, 'achsen').length === 3;
}

/** Die Liste des Projekts, in der die Systeme einer Art stehen. */
export function systemliste(art) {
  return ARTEN.find((x) => x.art === art).liste;
}

/** Die Art einer Last auf einem Stab nach dem Katalog: wie sie heisst, ob verteilt, ob eine Kraft, ihre Einheit. */
export function lastart(art, wert) {
  return systemkatalog(art, 'lastarten').find((x) => x.wert === wert) || { beschriftung: wert, einheit: '' };
}

/** Die Art einer Last an einem Knoten -- Kraft oder Moment -- mit denselben Angaben. */
export function knotenlastart(art, wert) {
  return systemkatalog(art, 'knotenlastarten').find((x) => x.wert === wert) || { beschriftung: wert, einheit: '' };
}

/** Eine Richtung einer Last nach dem Katalog -- mit Vektor im System oder der Achse des Stabs. */
export function lastrichtung(art, wert) {
  return systemkatalog(art, 'richtungen').find((x) => x.wert === wert) || null;
}

/** Wie ein Lager hält, je Richtung: «x fest · z fest · φ frei». */
export function lagertext(art, lager) {
  return systemkatalog(art, 'lagerfelder').map((x) => `${x.zeichen} ${lager[x.feld]}`).join(' · ');
}

/** «A und I», «A, I_y, I_z und I_T» -- die Kennwerte eines Querschnitts in Worten. */
export function undListe(namen) {
  return namen.length > 1 ? `${namen.slice(0, -1).join(', ')} und ${namen.at(-1)}` : namen.join('');
}

/** Die Last zu einer Kennung -- `{last, linie}` oder `{last, knoten}` -- oder null. */
export function lastVon(z, kennung) {
  for (const l of z.linien) {
    const last = l.lasten.find((x) => x.kennung === kennung);
    if (last) return { last, linie: l };
  }
  const p = z.knotenlasten.find((x) => x.kennung === kennung);
  return p ? { last: p, knoten: p.knoten } : null;
}

/**
 * Wie ein Material des Systems heisst: ein Beton oder Baustahl wie im
 * Projekt, ein eigenes mit seinem Namen.
 */
export function materialname(m) {
  if (m.art === 'eigen') return m.name || m.kennung;
  const stoff = eintragVon(m.stoff);
  return stoff ? stoff.name || stoff.sorte : `– kein ${katalog('materialarten', m.art, 'titel')} –`;
}

/** Die Antwort des Kerns -- nur, wenn sie zur Zeichnung passt, die gerade zu sehen ist. */
export function passendeUebersicht(a) {
  const u = a.bs.uebersicht;
  return u && u.fassung === zustand.fassung ? u : null;
}
