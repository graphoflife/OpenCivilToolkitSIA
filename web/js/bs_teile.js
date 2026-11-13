/**
 * bs_teile.js -- was Zeichnung, schwebendes Fenster und Panels eines
 * Balkensystems gemeinsam brauchen.
 *
 * Die Art einer Last nach dem Katalog des Kerns, die Last zu einer
 * Kennung, die Zugseite einer Linie und der Name eines Materials. Dazu die
 * Antwort des Kerns, solange sie zur Fassung des Projekts passt: was ein
 * Fenster betrifft, nimmt das Fenster `a` (bs_zeichnung.js), nicht seine
 * Kennung -- so liest das schwebende Fenster es ohne Umweg über den
 * Adapter. Den Lastfall, den ein Fenster zeigt, führt lastfaelle.js.
 * Nichts davon rechnet: es liest die Beschreibung, den Katalog und die
 * Materialien des Projekts.
 */

import { eintragVon, katalog, zustand } from './zustand.js';

export function lastart(wert) {
  return katalog('balkensystem', 'lastarten').find((x) => x.wert === wert) || { beschriftung: wert, einheit: '' };
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
 * Wo die gestrichelte Faser einer Linie von p nach q liegt, ihre Zugseite:
 * rechts der Laufrichtung -- 'unten' oder 'oben', an einer senkrechten
 * 'links' oder 'rechts'. Lagen [x, z] der Zeichnung.
 */
export function zugseite(p, q) {
  const [dx, dz] = [q[0] - p[0], q[1] - p[1]];
  if (Math.abs(dx) <= 1e-9 * Math.hypot(dx, dz)) return dz > 0 ? 'rechts' : 'links';
  return dx > 0 ? 'unten' : 'oben';
}

/** Wie ein Material des Systems heisst: ein Beton wie im Projekt, ein eigenes mit seinem Namen. */
export function materialname(m) {
  if (m.art !== 'beton') return m.name || m.kennung;
  const beton = eintragVon(m.beton);
  return beton ? beton.name || beton.sorte : '– kein Beton –';
}

/** Die Antwort des Kerns -- nur, wenn sie zur Zeichnung passt, die gerade zu sehen ist. */
export function passendeUebersicht(a) {
  const u = a.bs.uebersicht;
  return u && u.fassung === zustand.fassung ? u : null;
}
