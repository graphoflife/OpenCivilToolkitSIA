/**
 * profilwahl.js -- die Wahl eines Stahlprofils: die Reihe als Schalter mit
 * Bild, die Grösse als Liste -- beim Vollstahl als Zahlen.
 *
 * Dieselbe Wahl beim Stahlprofil eines Stabs im Balkensystem und beim
 * Profil im gezeichneten Querschnitt einer Analyse (Plan vom 2026-11-25).
 * Die Reihen und ihre Profile kommen aus dem Katalog (`profilreihen`), je
 * Reihe mit der Skizze ihres mittleren Profils: das Bild in ihrem Schalter.
 * Die Masse kennt nur der Kern.
 *
 * Vierkant-, Rund- und Flachstahl haben keine Tabelle (Benutzer,
 * 2026-11-27): je Mass ein Zahlenfeld, mit seiner Grenze aus dem Kern
 * (`frei` der Reihe), und der Name entsteht aus den Zahlen -- «FL 100 x 10».
 * Wie er gebaut ist, sagt opencivil/stahlprofile/tabelle.py; ob er geht,
 * prüft nur der Kern.
 *
 * Wer die Reihe wechselt, bekommt ihr erstes Profil -- das kleinste, beim
 * Vollstahl die Vorgabe. Ein Name ohne Reihe -- mehrere gewählte mit
 * verschiedenen Profilen, oder einer, der nicht geht -- hat keine Reihe
 * gewählt und keine Grösse: was fehlt, sagt der Ort, an dem die Wahl steht.
 */

import { wahlSchalter } from './bausteine.js';
import { auswahl, svgEl, zahlfeld } from './dom.js';
import { katalog } from './zustand.js';

/**
 * Die Zahlen im Namen eines Profils aus Vollstahl, in der Folge seiner Masse
 * -- «FL 100 x 10» gibt [100, 10] --, sonst null.
 */
function zahlenVon(reihe, profil) {
  const vorne = `${reihe.kurz} `;
  if (typeof profil !== 'string' || !profil.startsWith(vorne)) return null;
  const zahlen = profil.slice(vorne.length).split(' x ').map(Number);
  return zahlen.length === reihe.frei.length && zahlen.every(Number.isFinite) ? zahlen : null;
}

/** Der Name eines Profils aus Vollstahl, aus seinen Zahlen -- `zahlenVon` rückwärts. */
function nameAus(reihe, zahlen) {
  return `${reihe.kurz} ${zahlen.map(String).join(' x ')}`;
}

/** Die Reihe eines Profils -- «HEB 300» gehört zu HEB, «FL 100 x 10» zu FL --, sonst null. */
export function reiheVon(profil) {
  return katalog('profilreihen').find((r) => (r.frei.length
    ? zahlenVon(r, profil) !== null : r.profile.includes(profil))) || null;
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

/**
 * Die Grösse von `profil` als Zeilen, je gebaut mit `zeile(beschriftung,
 * eingabe, einheit, titel)`, wie der Ort sie hat: aus der Tabelle eine
 * Liste, beim Vollstahl je Mass ein Zahlenfeld. Ohne Reihe keine.
 */
export function groessenZeilen(profil, setzen, zeile) {
  const reihe = reiheVon(profil);
  if (!reihe) return [];
  if (!reihe.frei.length) {
    return [zeile('Profil', auswahl({
      werte: reihe.profile.map((name) => ({ wert: name, beschriftung: name })),
      gewaehlt: profil,
      titel: `${reihe.beschreibung} – Masse nach der Tabelle`,
      beiAenderung: setzen,
    }))];
  }
  const zahlen = zahlenVon(reihe, profil);
  return reihe.frei.map((m, i) => zeile(m.beschriftung, zahlfeld({
    wert: zahlen[i], schritt: m.schritt, angabe: m.angabe, titel: `${reihe.beschreibung} – ${m.heisst}`,
    beiAenderung: (w) => setzen(nameAus(reihe, zahlen.map((z, j) => (j === i ? w : z)))),
  }), m.angabe.einheit, m.heisst));
}
