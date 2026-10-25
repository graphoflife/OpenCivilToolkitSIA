/**
 * bs_teile.js -- was Zeichnung, schwebendes Fenster und Panels eines
 * Balkensystems gemeinsam brauchen.
 *
 * Der Katalog des Kerns zum Balkensystem und die Art einer Last darin, die
 * Last zu einer Kennung, die Zugseite einer Linie und der Name eines
 * Materials. Dazu das System selbst, die Antwort des Kerns, solange sie zur
 * Zeichnung passt, und der Lastfall, den ein Zeichenfenster zeigt: was ein
 * Fenster betrifft, nimmt das Fenster `a` (bs_zeichnung.js), nicht seine
 * Kennung -- so liest das schwebende Fenster es ohne Umweg über den Adapter.
 * Nichts davon rechnet: es liest die Beschreibung, den Katalog und die
 * Materialien des Projekts.
 */

import { ARTEN as BAUTEILARTEN } from './arten.js';
import { aendern, zustand } from './zustand.js';

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

/** Das System mit dieser Kennung, wie es gerade im Projekt steht -- oder null. */
export function eintragVon(kennung) {
  return zustand.projekt?.balkensysteme?.find((x) => x.kennung === kennung) || null;
}

/**
 * Wovon jede Antwort des Kerns zu einem System abhängt: das System, die
 * Materialien und die Bauteile, deren Querschnitt es nimmt. Ändert sich
 * davon etwas -- etwa eine Dichte oder die Höhe einer Platte --, gilt sie
 * nicht mehr: die Übersicht samt dem gezeichneten Eigengewicht, die
 * Verläufe in den Diagrammen.
 */
export function abdruckVon(kennung) {
  const system = eintragVon(kennung);
  const bezuege = (system?.querschnitte || []).map((q) => q.bezug).filter(Boolean);
  const bauteile = BAUTEILARTEN.flatMap((a) => zustand.projekt[a.liste] || [])
    .filter((b) => bezuege.includes(b.kennung));
  return JSON.stringify([system, zustand.projekt.materialien, bauteile]);
}

/** Die Antwort des Kerns -- nur, wenn sie zur Zeichnung passt, die gerade zu sehen ist. */
export function passendeUebersicht(a) {
  const u = a.bs.uebersicht;
  return u && u.abdruck === abdruckVon(a.bs.kennung) ? u : null;
}

/**
 * Der Lastfall, dessen Lasten das Fenster zeigt und bearbeitet -- der
 * gewählte, solange es ihn gibt, sonst der erste. Ansichtssache, nicht Teil
 * des Projekts.
 */
export function aktiverLastfall(a) {
  const faelle = eintragVon(a.bs.kennung)?.lastfaelle || [];
  // «– kein Lastfall –»: die Zeichnung zeigt keine Lasten.
  if (a.bs.lastfall === '') return null;
  if (faelle.some((lf) => lf.kennung === a.bs.lastfall)) return a.bs.lastfall;
  // Zuerst das Eigengewicht (Benutzer, 2026-10-24).
  return (faelle.find((lf) => lf.eigengewicht) || faelle[0])?.kennung || null;
}

/** Zeigt im Fenster die Lasten dieses Lastfalls -- '' heisst keine. */
export function lastfallWaehlen(a, lastfall) {
  a.bs.lastfall = lastfall;
  a.neuZeichnen();
  aendern({}, 'zeichnung');
}
