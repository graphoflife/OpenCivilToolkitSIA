/**
 * profilwahl.js -- die Wahl eines Stahlprofils: die Reihe als Schalter mit
 * Bild, die Grösse als Liste.
 *
 * Dieselbe Wahl beim Stahlprofil eines Stabs im Balkensystem und beim
 * Profil im gezeichneten Querschnitt einer Analyse (Plan vom 2026-11-25).
 * Die Reihen und ihre Profile kommen aus dem Katalog (`profilreihen`), je
 * Reihe mit der Skizze ihres mittleren Profils: das Bild in ihrem Schalter.
 * Die Masse kennt nur der Kern.
 *
 * Wer die Reihe wechselt, bekommt ihr erstes Profil -- das kleinste. Ein
 * Name ohne Reihe -- mehrere gewählte mit verschiedenen Profilen, oder einer,
 * den die Tabelle nicht kennt -- hat keine Reihe gewählt und keine Liste der
 * Grössen: was fehlt, sagt der Ort, an dem die Wahl steht.
 */

import { wahlSchalter } from './bausteine.js';
import { auswahl, svgEl } from './dom.js';
import { katalog } from './zustand.js';

/** Die Reihe eines Profils -- «HEB 300» gehört zu HEB --, sonst null. */
export function reiheVon(profil) {
  return katalog('profilreihen').find((r) => r.profile.includes(profil)) || null;
}

/**
 * Das Bild einer Reihe im Schalter: der Umriss ihres mittleren Profils,
 * voll in der Farbe der Schrift wie ein Sinnbild (sinnbilder.js) -- das Loch
 * eines Rohrs gerade-ungerade ausgespart.
 */
function reihenbild(skizze) {
  const teile = skizze.polygone.map((p) => p.punkte);
  const ys = teile.flat().map((p) => p[0]);
  const zs = teile.flat().map((p) => p[1]);
  const [y0, y1, z0, z1] = [Math.min(...ys), Math.max(...ys), Math.min(...zs), Math.max(...zs)];
  const s = 20 / Math.max(y1 - y0, z1 - z0, 1e-9);
  const [oy, oz] = [12 - (s * (y0 + y1)) / 2, 12 + (s * (z0 + z1)) / 2];
  const d = teile.map((t) => `M${t.map(([y, z]) => `${(oy + s * y).toFixed(2)} ${(oz - s * z).toFixed(2)}`)
    .join(' L')} Z`).join(' ');
  const svg = svgEl('svg', { viewBox: '0 0 24 24', class: 'sinnbild', 'aria-hidden': 'true' });
  svg.append(svgEl('path', { d, fill: 'currentColor', 'fill-rule': 'evenodd' }));
  return svg;
}

/**
 * Die Reihen als Schalter, je mit ihrem Bild über dem Namen -- sie brechen
 * um, wo der Platz nicht reicht: gewählt die von `profil`. `klasse` wie bei
 * `wahlSchalter`.
 */
export function reihenSchalter(profil, setzen, klasse = '') {
  const reihen = katalog('profilreihen');
  return wahlSchalter({
    werte: reihen.map((r) => ({
      wert: r.kurz, beschriftung: r.kurz, titel: r.beschreibung, bild: reihenbild(r.skizze),
    })),
    gewaehlt: reiheVon(profil)?.kurz ?? null,
    titel: 'Die Reihe der Stahlprofile',
    klasse: `.ist-reihen${klasse}`,
    setzen: (kurz) => setzen(reihen.find((r) => r.kurz === kurz).profile[0]),
  });
}

/** Die Grössen der Reihe von `profil` als Liste -- null ohne Reihe. */
export function groessenListe(profil, setzen) {
  const reihe = reiheVon(profil);
  if (!reihe) return null;
  return auswahl({
    werte: reihe.profile.map((name) => ({ wert: name, beschriftung: name })),
    gewaehlt: profil,
    titel: `${reihe.beschreibung} – Masse nach der Tabelle`,
    beiAenderung: setzen,
  });
}
