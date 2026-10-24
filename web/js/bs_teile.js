/**
 * bs_teile.js -- was Zeichnung, schwebendes Fenster und Panels eines
 * Balkensystems gemeinsam brauchen.
 *
 * Der Katalog des Kerns zum Balkensystem und die Art einer Last darin, die
 * Last zu einer Kennung, die Zugseite einer Linie und der Name eines
 * Materials. Nichts davon rechnet: es liest die Beschreibung, den Katalog
 * und die Materialien des Projekts.
 */

import { zustand } from './zustand.js';

/** Was der Katalog zum Balkensystem weiss: Lastarten, Richtungen, Lagerarten, Einheiten. */
export function katalog() {
  return zustand.katalog?.balkensystem || {
    lastarten: [], richtungen: [], knotenrichtungen: [], lagerarten: [], federeinheiten: {},
  };
}

export function lastart(wert) {
  return katalog().lastarten.find((x) => x.wert === wert) || { beschriftung: wert, einheit: '' };
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
  const beton = zustand.projekt.materialien.find((x) => x.kennung === m.beton);
  return beton ? beton.name || beton.sorte : '– kein Beton –';
}
