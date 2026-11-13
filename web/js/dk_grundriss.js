/**
 * dk_grundriss.js -- der Grundriss einer Decke, gezeichnet.
 *
 * Was eine Decke im Bild zeigt, im Zeichenfenster wie auf ihrer Karte im
 * Reiter «Diagramme»: die Platten, die Zonen, die Unterzüge, die
 * Linienlager mit ihrem Zeichen und die Stützen -- und darunter, was der
 * Kern dazu sagt (`daten`, die Antwort auf `decke_zeichnung`): wie die Last
 * auf die zwei Richtungen geht oder wo die Streifen verlaufen. Beide Bilder
 * rufen dieselbe Funktion, jedes mit seiner Ansicht `v` (cad_ansicht.js).
 *
 * ZEICHEN DER LINIENLAGER:
 *   vertikal gehalten            eine kräftige Linie
 *   dazu eingespannt             zu beiden Seiten schraffiert
 *   eingespannt, nicht vertikal  strichpunktiert, wie eine Symmetrieachse
 *   weder noch                   fein gepunktet -- es hält nichts
 *
 * FARBEN DER AUFTEILUNG:
 * Richtung 1 orange, Richtung 2 gelb -- die Farben von x und y, denn so
 * liegen die Richtungen, solange niemand sie dreht. Dazwischen gemischt
 * nach dem Anteil; eine Zone in ihrem eigenen.
 *
 * Gerechnet wird hier nichts, was in die Rechnung geht: die Flächen der
 * Aufteilung, die Grenzen der Streifen, die Bänder der Unterzüge und die
 * Stützenbereiche kommen vom Kern. Hier stehen nur Lagen fürs Auge -- wo
 * eine Beschriftung steht, wie gross eine Stütze im Bild ist.
 */

import { nachBild, pfad, zahlText } from './cad_ansicht.js';
import { mitTitel } from './cad_app.js';
import { flaecheVon, innen } from './cad_modell.js';
import { el, svgEl } from './dom.js';

/** So klein wird eine Stütze im Bild höchstens, in px -- sonst verschwände sie beim Herauszoomen. */
const STUETZE_MINDESTENS = 7;
/** Der Abstand der Schraffur an einem eingespannten Rand, in px. */
const SCHRAFFUR = 7;

/** Die Farbe eines Anteils in Richtung 1, in %: orange bei 100, gelb bei 0, dazwischen gemischt. */
function mischung(anteil) {
  const s = Math.max(0, Math.min(100, anteil));
  return `color-mix(in srgb, var(--richtung-x) ${s.toFixed(1)}%, var(--richtung-y))`;
}

const anteilFarbe = (anteil) => `fill: ${mischung(anteil)}`;

/** Was die Farben der Aufteilung heissen -- unter der Zeichnung und unter ihrem Bild. */
export function legende() {
  const eintrag = (anteil, text) => el('span.dk-legende-eintrag', {}, [
    el('span.dk-legende-farbe', { style: { background: mischung(anteil) } }), text,
  ]);
  return el('div.dk-legende', {}, [
    eintrag(100, 'ganz in Richtung 1'), eintrag(50, 'je zur Hälfte'), eintrag(0, 'ganz in Richtung 2'),
  ]);
}

/** «70 / 30 %»: der Anteil in Richtung 1 und der Rest in Richtung 2. */
export function anteilText(anteil) {
  return `${zahlText(anteil, 0)} / ${zahlText(100 - anteil, 0)} %`;
}

function text(p, inhalt, klasse) {
  const t = svgEl('text', { x: p[0].toFixed(1), y: p[1].toFixed(1), class: klasse });
  t.textContent = inhalt;
  return t;
}

/** Der Schwerpunkt eines Vielecks -- ohne Fläche der Mittelwert seiner Ecken. */
function schwerpunkt(punkte) {
  let a = 0;
  let sx = 0;
  let sy = 0;
  punkte.forEach((p, i) => {
    const q = punkte[(i + 1) % punkte.length];
    const k = p[0] * q[1] - q[0] * p[1];
    a += k;
    sx += (p[0] + q[0]) * k;
    sy += (p[1] + q[1]) * k;
  });
  if (Math.abs(a) < 1e-12) {
    return [0, 1].map((i) => punkte.reduce((s, p) => s + p[i], 0) / punkte.length);
  }
  return [sx / (3 * a), sy / (3 * a)];
}

/**
 * Wo die Beschriftung eines Umrisses steht: in seinem Schwerpunkt -- liegt
 * der draussen, wie in manchem L, im grössten Eckdreieck, dessen
 * Schwerpunkt drin liegt.
 */
function beschriftungsort(punkte) {
  const s = schwerpunkt(punkte);
  if (innen(s, punkte)) return s;
  let beste = null;
  punkte.forEach((p, i) => {
    const dreieck = [punkte.at(i - 1), p, punkte[(i + 1) % punkte.length]];
    const m = schwerpunkt(dreieck);
    const flaeche = Math.abs(flaecheVon(dreieck));
    if (innen(m, punkte) && (!beste || flaeche > beste.flaeche)) beste = { m, flaeche };
  });
  return beste?.m || s;
}

/**
 * Die Schraffur eines eingespannten Randes: kurze schräge Striche zu beiden
 * Seiten der Linie `p`–`q` (Bildpunkte).
 */
function schraffur(p, q) {
  const lang = Math.hypot(q[0] - p[0], q[1] - p[1]);
  if (lang < 1) return '';
  const t = [(q[0] - p[0]) / lang, (q[1] - p[1]) / lang];
  const n = [-t[1], t[0]];
  const teile = [];
  for (let s = SCHRAFFUR / 2; s < lang; s += SCHRAFFUR) {
    const m = [p[0] + t[0] * s, p[1] + t[1] * s];
    for (const seite of [1, -1]) {
      const a = [m[0] + n[0] * 2.5 * seite, m[1] + n[1] * 2.5 * seite];
      const b = [a[0] + (n[0] * 5 - t[0] * 4) * seite, a[1] + (n[1] * 5 - t[1] * 4) * seite];
      teile.push(`M${a[0].toFixed(1)} ${a[1].toFixed(1)} L${b[0].toFixed(1)} ${b[1].toFixed(1)}`);
    }
  }
  return teile.join(' ');
}

/** Wie ein Linienlager im Bild heisst -- seine Klasse nach dem, was es hält. */
function lagerKlasse(l) {
  if (l.vertikal) return 'dk-lager';
  return l.eingespannt ? 'dk-lager ist-symmetrie' : 'dk-lager ist-frei';
}

/**
 * Was der Kern unter die Teile legt. `was`: 'aufteilung' -- die Flächen
 * mit ihrem Anteil in Richtung 1 --, 'streifen' -- die Grenzen der
 * Streifen, die Stützenbereiche -- oder 'nichts'.
 */
function unterlage(v, daten, was) {
  const g = svgEl('g', { class: daten?.veraltet ? 'dk-unterlage ist-veraltet' : 'dk-unterlage' });
  if (!daten?.gerechnet) return g;
  if (was === 'aufteilung') {
    for (const f of daten.anteile) {
      g.append(mitTitel(svgEl('path', { d: pfad(v, f.ecken), class: 'dk-anteil', style: anteilFarbe(f.anteil) }),
        [`Richtung 1 / 2: ${anteilText(f.anteil)}`]));
    }
  } else if (was === 'streifen') {
    for (const s of daten.grenzen) {
      g.append(svgEl('path', { d: pfad(v, s.punkte, false), class: `dk-grenze ist-richtung-${s.richtung}` }));
    }
    for (const b of daten.stuetzenbereiche) {
      g.append(mitTitel(svgEl('path', { d: pfad(v, b.ecken), class: 'dk-stuetzenbereich' }),
        [`Stützenbereich ${b.name}`]));
    }
  }
  return g;
}

/**
 * Der ganze Grundriss: die Flächen der Platten, darüber die Unterlage des
 * Kerns, die Zonen, die Umrisse, die Unterzüge, die Linienlager, die
 * Stützen und die Namen. `fehler(kennung)` und `texte(kennung)` sagen, was
 * der Kern an einem Teil meldet -- rot, und als Titel beim Darüberfahren.
 */
export function grundriss(v, decke, daten, { was = 'aufteilung', fehler = () => false, texte = () => [] } = {}) {
  const g = svgEl('g', { class: 'dk-grundriss' });
  const lagen = new Map((decke.knoten || []).map((k) => [k.kennung, [k.x, k.y]]));
  const orte = (knoten) => {
    const punkte = knoten.map((k) => lagen.get(k));
    return punkte.some((p) => !p) ? null : punkte;
  };
  const klasse = (grund, kennung) => (fehler(kennung) ? `${grund} ist-fehler` : grund);

  const flaechen = svgEl('g');
  const umrisse = svgEl('g');
  const zonen = svgEl('g');
  const namen = svgEl('g', { class: 'dk-namen' });
  for (const p of decke.platten || []) {
    const punkte = orte(p.knoten);
    if (!punkte || punkte.length < 3) continue;
    flaechen.append(svgEl('path', { d: pfad(v, punkte), class: 'dk-platte-flaeche' }));
    umrisse.append(mitTitel(svgEl('path', { d: pfad(v, punkte), class: klasse('dk-platte', p.kennung) }),
      texte(p.kennung)));
    namen.append(text(nachBild(v, beschriftungsort(punkte)), `${p.kennung} · ${zahlText(p.h, 0)} mm`, 'dk-name'));
  }
  for (const z of decke.zonen || []) {
    const punkte = orte(z.knoten);
    if (!punkte || punkte.length < 3) continue;
    if (was === 'aufteilung') {
      // Weiss darunter: die Zone zeigt ihren Anteil, nicht den, den sie ersetzt.
      zonen.append(svgEl('path', { d: pfad(v, punkte), class: 'dk-zone-grund' }),
        svgEl('path', { d: pfad(v, punkte), class: 'dk-anteil', style: anteilFarbe(z.anteil) }));
    }
    zonen.append(mitTitel(svgEl('path', { d: pfad(v, punkte), class: klasse('dk-zone', z.kennung) }),
      [`Zone ${z.kennung}: Richtung 1 / 2 ${anteilText(z.anteil)}`, ...texte(z.kennung)]));
    // Eine Zeile tiefer als ihr Ort: liegt sie mitten in einer Platte, stünde sie sonst auf deren Namen.
    const [x, y] = nachBild(v, beschriftungsort(punkte));
    namen.append(text([x, y + 14], `${z.kennung} · ${anteilText(z.anteil)}`, 'dk-name ist-zone'));
  }

  const traeger = svgEl('g');
  const baender = new Map((daten?.gerechnet ? daten.unterzuege : []).map((u) => [u.name, u.ecken]));
  for (const u of decke.unterzuege || []) {
    const punkte = orte([u.von, u.bis]);
    if (!punkte) continue;
    const band = baender.get(u.kennung);
    if (band) traeger.append(svgEl('path', { d: pfad(v, band), class: 'dk-unterzug-band' }));
    traeger.append(mitTitel(svgEl('path', { d: pfad(v, punkte, false), class: klasse('dk-unterzug', u.kennung) }),
      [`Unterzug ${u.kennung}: b = ${zahlText(u.breite, 2)} m, Stufe ${u.stufe}`, ...texte(u.kennung)]));
    // Bei einem Viertel: in der Mitte stünde der Name oft auf dem der Platte, am Ende auf dem einer Stütze.
    const [p, q] = punkte.map((x) => nachBild(v, x));
    namen.append(text([p[0] + (q[0] - p[0]) / 4 + 6, p[1] + (q[1] - p[1]) / 4 - 6], u.kennung, 'dk-name ist-klein'));
  }

  const lager = svgEl('g');
  for (const l of decke.linienlager || []) {
    const punkte = orte([l.von, l.bis]);
    if (!punkte) continue;
    const [p, q] = punkte.map((x) => nachBild(v, x));
    if (l.eingespannt && l.vertikal) lager.append(svgEl('path', { d: schraffur(p, q), class: 'dk-schraffur' }));
    lager.append(mitTitel(svgEl('path', { d: pfad(v, punkte, false), class: klasse(lagerKlasse(l), l.kennung) }),
      [`Linienlager ${l.kennung}: ${l.vertikal ? 'vertikal gehalten' : 'vertikal frei'}, `
        + `${l.eingespannt ? 'eingespannt' : 'frei drehbar'}`, ...texte(l.kennung)]));
  }

  const stuetzen = svgEl('g');
  for (const s of decke.stuetzen || []) {
    const ort = lagen.get(s.knoten);
    if (!ort) continue;
    const [x, y] = nachBild(v, ort);
    const b = Math.max(STUETZE_MINDESTENS, (s.b_x / 1000) * v.massstab);
    const h = Math.max(STUETZE_MINDESTENS, (s.b_y / 1000) * v.massstab);
    stuetzen.append(mitTitel(svgEl('rect', {
      x: (x - b / 2).toFixed(1), y: (y - h / 2).toFixed(1), width: b.toFixed(1), height: h.toFixed(1),
      class: klasse('dk-stuetze', s.kennung),
    }), [`Stütze ${s.kennung}: ${zahlText(s.b_x, 0)} × ${zahlText(s.b_y, 0)} mm`, ...texte(s.kennung)]));
    namen.append(text([x + b / 2 + 3, y - h / 2 - 3], s.kennung, 'dk-name ist-klein'));
  }

  g.append(flaechen, unterlage(v, daten, was), zonen, umrisse, traeger, lager, stuetzen, namen);
  return g;
}
