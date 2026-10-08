/**
 * qa_zeichnung.js -- das Zeichenfenster der Querschnittsanalyse: der Adapter.
 *
 * Das allgemeine Fenster (`cad_fenster.js`) kennt nur Knoten und Elemente
 * in drei Formen. Was sie im Querschnitt sind, steht hier:
 *
 *   Fläche      Polygon mit Beton -- oder ohne Material eine Aussparung
 *   Punkt       ein Stab, mit ⌀ und Stahl
 *   Linie       eine Bewehrung, eine Schubwand oder eine Hilfslinie
 *
 * Eine Linie wechselt ihre Art im schwebenden Fenster: der Eintrag wandert in
 * die andere Liste und behält Kennung, Anfang und Ende. Was die andere Art an
 * Eigenschaften hatte, merkt sich das Fenster für den Rückweg.
 *
 * WAS HIER GERECHNET WIRD -- UND WAS NICHT:
 * Nichts, was in die Rechnung geht. Die Stäbe einer Linie und ihre
 * tatsächliche Teilung, der Schwerpunkt, die Zellen der Schubwände, welches
 * Polygon in welchem liegt, jede Meldung und jeder Name («Linie 2») kommen
 * vom Kern über die Anfrage `geometrie`. Diese Antwort gilt nur, solange die
 * Zeichnung dieselbe ist, nach der gefragt wurde.
 */

import { api } from './api.js';
import { hakenSchalter } from './bausteine.js';
import {
  nachBild, pfad, text, zahlText,
} from './cad_ansicht.js';
import { cadBereich, cadFenster, cadVergessen, cadWaehlen } from './cad_fenster.js';
import { abstand } from './cad_modell.js';
import {
  auswahl, el, melden, svgEl, zahlfeld,
} from './dom.js';
import { aendern, ausVorlage, projektAendern, zustand } from './zustand.js';

/**
 * Die Arten des Querschnitts, für das allgemeine Fenster. Eine Bewehrung
 * lässt sich nicht teilen: die Stäbe zweier Hälften wären andere als die
 * des Ganzen (n Stäbe je Hälfte, oder ein doppelter Stab in der Mitte).
 * Umgekehrt tauschen Start- und Endeisen mit -- die Stäbe bleiben, wo sie
 * sind.
 */
const ARTEN = [
  { liste: 'flaechen', form: 'flaeche', vorsilbe: 'F' },
  { liste: 'staebe', form: 'punkt', vorsilbe: 'S' },
  {
    liste: 'stablinien', form: 'linie', vorsilbe: 'L', teilbar: false,
    umkehren: (e) => { [e.starteisen, e.endeisen] = [e.endeisen, e.starteisen]; },
  },
  { liste: 'schubwaende', form: 'linie', vorsilbe: 'L' },
  { liste: 'hilfslinien', form: 'linie', vorsilbe: 'L' },
];

/** Was eine Linie sein kann -- ihre Liste und ihre Vorlage im Katalog. */
const LINIENARTEN = [
  { wert: 'stablinien', text: 'Bewehrung', vorlage: 'stablinie' },
  { wert: 'schubwaende', text: 'Schubwand', vorlage: 'schubwand' },
  { wert: 'hilfslinien', text: 'Hilfslinie', vorlage: 'hilfslinie' },
];
const LINIENLISTEN = LINIENARTEN.map((x) => x.wert);

/** Felder, die eine Linie ausmachen und nicht ihre Art: sie wandern beim Wechsel mit. */
const LINIENKERN = ['kennung', 'von', 'bis'];

function eintragVon(kennung) {
  return zustand.projekt?.querschnittsanalysen?.find((x) => x.kennung === kennung) || null;
}

/** Ändert die Analyse -- der eine Weg, auf dem das Fenster ins Projekt schreibt. */
function schreiben(kennung, veraenderer) {
  projektAendern((p) => veraenderer(p.querschnittsanalysen.find((x) => x.kennung === kennung)));
}

// ===========================================================================
// Das Fenster einer Analyse
// ===========================================================================

/**
 * Das Zeichenfenster einer Analyse, samt der Liste darunter. Die Tafel ruft
 * das bei jedem Neubau.
 */
export function zeichenbereich(analyse, uebersichtBauen) {
  const a = fensterVon(analyse.kennung);
  const unten = el('div.qa-uebersicht-huelle');
  a.qa.uebersichtKnoten = unten;
  a.qa.uebersichtBauen = uebersichtBauen;
  const bereich = cadBereich(a, [unten]);
  uebersichtZeichnen(a);
  return bereich;
}

export function fensterVon(kennung) {
  const a = cadFenster(`qa:${kennung}`, () => adapter(kennung));
  // Was die Analyse an der Ansicht braucht: Vorgaben, Antwort des Kerns, Namen.
  a.qa = a.adapter.qa;
  return a;
}

/** Für eine neu angelegte Analyse: nichts von einer früheren mit derselben Kennung. */
export function fensterVergessen(kennung) {
  cadVergessen(`qa:${kennung}`);
}

/** Wählt Elemente von aussen -- aus der Liste oder einer Meldung. */
export function waehlen(kennung, kennungen) {
  cadWaehlen(fensterVon(kennung), kennungen);
}

/** Die Antwort des Kerns -- nur, wenn sie zur Zeichnung passt, die gerade zu sehen ist. */
export function passendeGeometrie(a) {
  const g = a.qa.geometrie;
  return g && g.abdruck === abdruck(eintragVon(a.qa.kennung)) ? g : null;
}

/** Die Zeichnung und welche Materialien es gibt: davon hängt die Antwort des Kerns ab. */
function abdruck(analyse) {
  if (!analyse) return '';
  const stoffe = zustand.projekt.materialien.map((m) => [m.kennung, m.art]);
  return JSON.stringify([...ARTEN.map((x) => analyse[x.liste] || []), analyse.knoten || [], stoffe]);
}

function uebersichtZeichnen(a) {
  const ziel = a.qa.uebersichtKnoten;
  if (ziel && a.qa.uebersichtBauen) ziel.replaceChildren(...a.qa.uebersichtBauen(a));
}

/** Markiert in der Liste, was im Fenster gewählt ist -- ohne sie neu zu bauen. */
function auswahlMarkieren(a) {
  for (const z of a.qa.uebersichtKnoten?.querySelectorAll('[data-kennung]') || []) {
    z.classList.toggle('ist-gewaehlt', a.auswahl.has(z.dataset.kennung));
  }
}

// ===========================================================================
// Der Adapter
// ===========================================================================

function vorgabenNeu() {
  const beton = zustand.projekt.materialien.find((m) => m.art === 'beton');
  const stahl = zustand.projekt.materialien.find((m) => m.art === 'betonstahl');
  const mit = (art, felder = {}) => ausVorlage(art, felder);
  return {
    knoten: { art: 'stab' },
    stab: mit('stab', { stahl: stahl?.kennung || '' }),
    linie: { art: 'stablinien' },
    stablinien: mit('stablinie', { stahl: stahl?.kennung || '' }),
    schubwaende: mit('schubwand', { stahl: stahl?.kennung || '' }),
    hilfslinien: mit('hilfslinie'),
    flaeche: mit('flaeche', { material: beton?.kennung || '' }),
  };
}

function adapter(kennung) {
  const projekt = zustand.projekt;
  const qa = {
    kennung, vorgaben: vorgabenNeu(), geometrie: null, gefragt: null, gemerkt: new Map(),
  };
  return {
    qa,
    achsen: ['y', 'z'],
    arten: ARTEN,
    gilt: () => zustand.projekt === projekt,
    zeichnung: () => eintragVon(kennung),
    schreiben: (veraenderer) => schreiben(kennung, veraenderer),
    tafelNeu: () => aendern({}, 'zeichnung'),
    name: elementname,
    neuText: (a, werkzeug) => neuText(a.qa, werkzeug),
    punktAnlegen,
    linieAnlegen,
    flaecheAnlegen,
    zeichnen,
    punktVorschau,
    linienVorschau,
    fangpunkte: (a) => {
      const g = passendeGeometrie(a);
      return g?.brutto ? [{ p: [g.brutto.y_S, g.brutto.z_S] }] : [];
    },
    trefferradius: (art, e) => {
      if (art.liste === 'staebe' || art.liste === 'stablinien') return (e.durchmesser || 0) / 2;
      return 0;
    },
    umriss: () => umriss(eintragVon(kennung)),
    geaendert: geometrieHolen,
    gezeichnet: auswahlMarkieren,
    eigenschaften,
    neuEigenschaften,
    aktionen,
  };
}

/** Der Name eines Elements, wie er im Bericht steht -- vom Kern. Knoten heissen nach ihrer Kennung. */
export function elementname(a, kennung) {
  if (!kennung) return '';
  if (/^K\d+$/.test(kennung)) return `Knoten ${kennung}`;
  return a.qa.namen?.get(kennung) || kennung;
}

export function stoffname(kennung) {
  const m = zustand.projekt.materialien.find((x) => x.kennung === kennung);
  return m ? (m.name || m.sorte) : '–';
}

function neuText(qa, werkzeug) {
  const v = qa.vorgaben;
  if (werkzeug === 'knoten') {
    return v.knoten.art === 'stab' ? `Stab ⌀${zahlText(v.stab.durchmesser)}` : 'Knoten';
  }
  if (werkzeug === 'linie') return LINIENARTEN.find((x) => x.wert === v.linie.art).text;
  return v.flaeche.material ? `Fläche ${stoffname(v.flaeche.material)}` : 'Aussparung';
}

// ===========================================================================
// Anlegen -- nach den Vorgaben im schwebenden Fenster
// ===========================================================================

function punktAnlegen(a, z, knoten) {
  const v = a.qa.vorgaben;
  if (v.knoten.art !== 'stab') return null;
  const kennung = a.modell.naechsteKennung(z, 'S');
  z.staebe.push({ ...structuredClone(v.stab), kennung, knoten });
  return kennung;
}

function linieAnlegen(a, z, von, bis) {
  const v = a.qa.vorgaben;
  const liste = v.linie.art;
  const kennung = a.modell.naechsteKennung(z, 'L');
  z[liste].push({ ...structuredClone(v[liste]), kennung, von, bis });
  return kennung;
}

function flaecheAnlegen(a, z, knoten) {
  const kennung = a.modell.naechsteKennung(z, 'F');
  z.flaechen.push({ ...structuredClone(a.qa.vorgaben.flaeche), kennung, knoten });
  return kennung;
}

/** Was im Bild sein soll: alle Knoten -- sonst ein Meter im Quadrat. */
function umriss(analyse) {
  const k = analyse?.knoten || [];
  if (!k.length) return [[0, 0], [1000, 1000]];
  const ys = k.map((x) => x.y);
  const zs = k.map((x) => x.z);
  return [[Math.min(...ys), Math.min(...zs)], [Math.max(...ys), Math.max(...zs)]];
}

// ===========================================================================
// Der Kern
// ===========================================================================

/**
 * Fragt den Kern nach der Zeichnung, wenn sie sich seit der letzten Frage
 * geändert hat. Kommt eine Antwort zu spät -- es wurde inzwischen wieder
 * gefragt --, gilt sie nicht mehr.
 */
function geometrieHolen(a) {
  const analyse = eintragVon(a.qa.kennung);
  if (!analyse) return;
  const jetzt = abdruck(analyse);
  if (a.qa.gefragt === jetzt) return;
  a.qa.gefragt = jetzt;
  api.geometrie(zustand.projekt, a.qa.kennung).then((antwort) => {
    if (a.qa.gefragt !== jetzt) return;
    a.qa.geometrie = { ...antwort, abdruck: jetzt };
    const namen = new Map();
    for (const liste of [antwort.polygone, antwort.staebe, antwort.linien, antwort.waende, antwort.hilfslinien]) {
      for (const x of liste || []) namen.set(x.kennung, x.element);
    }
    a.qa.namen = namen;
    a.neuZeichnen();
    uebersichtZeichnen(a);
  }).catch((fehler) => {
    if (a.qa.gefragt === jetzt) melden(fehler.message, true);
  });
}

/** Je Element, das eine Meldung nennt, ihre Sätze. */
function fehlerhafte(g) {
  const je = new Map();
  for (const m of g?.meldungen || []) {
    for (const k of m.elemente) je.set(k, [...(je.get(k) || []), m.text]);
  }
  return je;
}

function mitMeldung(knoten, texte) {
  if (texte?.length) {
    const t = svgEl('title');
    t.textContent = texte.join('\n');
    knoten.append(t);
  }
  return knoten;
}

// ===========================================================================
// Zeichnen
// ===========================================================================

/** Ein Stab: ein Kreis in seinem Durchmesser, aber nie kleiner als ein Punkt. */
function stabKreis(a, p, durchmesser, klasse) {
  const [x, y] = nachBild(a.v, p);
  return svgEl('circle', {
    cx: x.toFixed(1), cy: y.toFixed(1),
    r: Math.max(2.4, (a.v.massstab * durchmesser) / 2).toFixed(1), class: klasse,
  });
}

/** Die Ecken des Bandes einer Schubwand: die Achse, um b_w/2 nach beiden Seiten versetzt. */
function band(von, bis, dicke) {
  const l = abstand(von, bis);
  if (!l) return null;
  const n = [(-(bis[1] - von[1]) / l) * (dicke / 2), ((bis[0] - von[0]) / l) * (dicke / 2)];
  return [
    [von[0] + n[0], von[1] + n[1]], [bis[0] + n[0], bis[1] + n[1]],
    [bis[0] - n[0], bis[1] - n[1]], [von[0] - n[0], von[1] - n[1]],
  ];
}

/**
 * Was an einer Stablinie steht -- aus der Antwort des Kerns, also mit der
 * tatsächlichen Teilung: «3 ⌀16 @ 142.9 (gewählt 150)».
 */
export function linienText(linie, info) {
  if (!info || !info.punkte) return '';
  const n = info.punkte.length;
  if (linie.art === 'flaeche') {
    return `As = ${zahlText(info.flaeche, 0)} mm² (${zahlText(info.je_meter, 0)} mm²/m)`;
  }
  const teilung = info.teilung === null || info.teilung === undefined ? '' : zahlText(info.teilung);
  if (linie.art === 'teilung') {
    const gewaehlt = zahlText(linie.teilung);
    return `${n} ⌀${zahlText(linie.durchmesser)} @ ${teilung}`
      + (teilung === gewaehlt ? '' : ` (gewählt ${gewaehlt})`);
  }
  return `${n} ⌀${zahlText(linie.durchmesser)}${teilung ? ` @ ${teilung}` : ''}`;
}

/** Wie tief ein Polygon verschachtelt ist -- Eltern zuerst, damit Kinder darüber liegen. */
function tiefe(polygone, i) {
  let t = 0;
  let j = polygone?.[i]?.eltern;
  while (j !== null && j !== undefined && t < 50) {
    t += 1;
    j = polygone[j]?.eltern;
  }
  return t;
}

function zeichnen(a, g) {
  const z = eintragVon(a.qa.kennung);
  const geo = passendeGeometrie(a);
  const roh = a.qa.geometrie;
  const fehler = fehlerhafte(geo);
  const lagen = a.modell.lagen(z);
  const ort = (k) => lagen.get(k);
  const klassen = (kennung, ...weitere) => [...weitere, fehler.has(kennung) ? 'ist-fehler' : ''].join(' ');

  const schraffur = svgEl('pattern', {
    id: `qa-schraffur-${a.qa.kennung}`, patternUnits: 'userSpaceOnUse',
    width: 7, height: 7, patternTransform: 'rotate(45)',
  });
  schraffur.append(svgEl('line', { x1: 0, y1: 0, x2: 0, y2: 7, class: 'cad-schraffurstrich' }));
  const defs = svgEl('defs');
  defs.append(schraffur);
  g.append(defs);

  // Flächen: die äusseren zuerst. Die Tiefe kommt vom Kern -- auch aus einer
  // älteren Antwort, solange es gleich viele Polygone sind.
  const tiefeVon = new Map();
  if (roh?.polygone?.length === z.flaechen.length) {
    roh.polygone.forEach((p, i) => tiefeVon.set(p.kennung, tiefe(roh.polygone, i)));
  }
  const flaechen = [...z.flaechen].sort((p, q) => (tiefeVon.get(p.kennung) || 0) - (tiefeVon.get(q.kennung) || 0));
  for (const f of flaechen) {
    const punkte = f.knoten.map(ort);
    if (punkte.length < 2 || punkte.some((p) => !p)) continue;
    g.append(mitMeldung(svgEl('path', {
      d: pfad(a.v, punkte), class: klassen(f.kennung, f.material ? 'cad-beton' : 'cad-loch'),
    }), fehler.get(f.kennung)));
  }

  for (const zelle of geo?.zellen || []) {
    g.append(svgEl('path', {
      d: pfad(a.v, zelle.punkte), class: 'cad-zelle', fill: `url(#qa-schraffur-${a.qa.kennung})`,
    }));
  }

  for (const w of z.schubwaende) {
    const [p, q] = [ort(w.von), ort(w.bis)];
    if (!p || !q) continue;
    const ecken = band(p, q, Math.max(w.dicke, 0));
    if (ecken) {
      g.append(mitMeldung(svgEl('path', { d: pfad(a.v, ecken), class: klassen(w.kennung, 'cad-wand') }),
        fehler.get(w.kennung)));
    }
    g.append(svgEl('path', { d: pfad(a.v, [p, q], false), class: klassen(w.kennung, 'cad-wandachse') }));
  }

  for (const h of z.hilfslinien || []) {
    const [p, q] = [ort(h.von), ort(h.bis)];
    if (p && q) g.append(svgEl('path', { d: pfad(a.v, [p, q], false), class: 'cad-hilfslinie' }));
  }

  const linieninfo = new Map((geo?.linien || []).map((x) => [x.kennung, x]));
  for (const l of z.stablinien) {
    const [p, q] = [ort(l.von), ort(l.bis)];
    if (!p || !q) continue;
    const flaechig = l.art === 'flaeche';
    g.append(mitMeldung(svgEl('path', {
      d: pfad(a.v, [p, q], false),
      class: klassen(l.kennung, flaechig ? 'cad-linie-flaeche' : 'cad-linie'),
    }), fehler.get(l.kennung)));
    const info = linieninfo.get(l.kennung);
    if (!info) continue;
    if (!flaechig) for (const s of info.punkte) g.append(stabKreis(a, s, l.durchmesser, klassen(l.kennung, 'cad-stab')));
    const beschriftung = linienText(l, info);
    if (beschriftung) {
      const [x0, y0] = nachBild(a.v, p);
      const [x1, y1] = nachBild(a.v, q);
      const lang = Math.hypot(x1 - x0, y1 - y0) || 1;
      // Links der Laufrichtung, also bei einer Linie nach rechts oberhalb.
      const [nx, ny] = [(y1 - y0) / lang, -(x1 - x0) / lang];
      const versatz = 9 + (flaechig ? 3 : Math.max(2.4, (a.v.massstab * l.durchmesser) / 2));
      g.append(text((x0 + x1) / 2 + nx * versatz, (y0 + y1) / 2 + ny * versatz + 4,
        beschriftung, `cad-beschriftung cad-linientext ${fehler.has(l.kennung) ? 'ist-fehler' : ''}`));
    }
  }

  for (const s of z.staebe) {
    const p = ort(s.knoten);
    if (p) g.append(mitMeldung(stabKreis(a, p, s.durchmesser, klassen(s.kennung, 'cad-stab')), fehler.get(s.kennung)));
  }

  const masse = masseZeichnen(a, z, ort);
  if (masse) g.append(masse);
  if (geo?.brutto) {
    const [x, y] = nachBild(a.v, [geo.brutto.y_S, geo.brutto.z_S]);
    const s = svgEl('g', { class: 'cad-schwerpunkt' });
    s.append(
      svgEl('circle', { cx: x, cy: y, r: 6 }),
      svgEl('path', { d: `M${x - 9} ${y} H${x + 9} M${x} ${y - 9} V${y + 9}` }),
      text(x + 9, y - 7, 'S', 'cad-schwerpunkttext', 'start'),
    );
    g.append(s);
  }
}

/** Breite und Höhe dessen, was Material hat -- eine Masslinie unten, eine links. */
function masseZeichnen(a, z, ort) {
  const punkte = z.flaechen.filter((f) => f.material).flatMap((f) => f.knoten.map(ort)).filter(Boolean);
  if (punkte.length < 2) return null;
  const ys = punkte.map((p) => p[0]);
  const zs = punkte.map((p) => p[1]);
  const [y0, y1, z0, z1] = [Math.min(...ys), Math.max(...ys), Math.min(...zs), Math.max(...zs)];
  const [xl, hu] = nachBild(a.v, [y0, z0]);
  const [xr, ho] = nachBild(a.v, [y1, z1]);
  const g = svgEl('g');
  const unten = Math.min(hu + 22, a.v.hoehe - 8);
  const links = Math.max(xl - 22, 8);
  if (xr - xl > 30) {
    g.append(
      svgEl('path', {
        d: `M${xl} ${unten} H${xr} M${xl} ${unten - 5} V${unten + 5} M${xr} ${unten - 5} V${unten + 5}`,
        class: 'cad-mass',
      }),
      text((xl + xr) / 2, unten - 4, zahlText(y1 - y0), 'cad-masstext'),
    );
  }
  if (hu - ho > 30) {
    const t = text(links - 4, (hu + ho) / 2, zahlText(z1 - z0), 'cad-masstext');
    t.setAttribute('transform', `rotate(-90 ${(links - 4).toFixed(1)} ${((hu + ho) / 2).toFixed(1)})`);
    g.append(svgEl('path', {
      d: `M${links} ${ho} V${hu} M${links - 5} ${ho} H${links + 5} M${links - 5} ${hu} H${links + 5}`,
      class: 'cad-mass',
    }), t);
  }
  return g;
}

function punktVorschau(a, g, p) {
  const v = a.qa.vorgaben;
  if (v.knoten.art === 'stab') g.append(stabKreis(a, p, v.stab.durchmesser, 'cad-stab cad-geist'));
}

function linienVorschau(a, g, p, q) {
  const v = a.qa.vorgaben;
  if (v.linie.art !== 'schubwaende') return;
  const ecken = band(p, q, v.schubwaende.dicke);
  if (ecken) g.append(svgEl('path', { d: pfad(a.v, ecken), class: 'cad-wand cad-geist' }));
}

// ===========================================================================
// Felder im schwebenden Fenster
// ===========================================================================

function zeile(beschriftung, eingabe, einheit = '') {
  return el('label.cad-zeile', {}, [
    el('span', { text: beschriftung }), eingabe, einheit ? el('span.einheit', { text: einheit }) : el('span'),
  ]);
}

function materialwahl(art, gewaehlt, setzen, mitLoch = false) {
  return auswahl({
    werte: [
      ...zustand.projekt.materialien.filter((m) => m.art === art)
        .map((m) => ({ wert: m.kennung, beschriftung: m.name || m.sorte })),
      ...(mitLoch ? [{ wert: '', beschriftung: 'Aussparung' }] : []),
    ],
    gewaehlt,
    beiAenderung: setzen,
  });
}

/**
 * Die Felder einer Elementart. `werte` ist das Element (oder die Vorgabe),
 * `setzen(feld, wert)` schreibt -- beim gewählten Element ins Projekt, bei
 * der Vorgabe in die Ansicht.
 */
function felderVon(liste, werte, setzen) {
  const durchmesser = zustand.katalog?.durchmesser;
  const zahl = (feld, titel, optionen = {}) => zahlfeld({
    wert: werte[feld], titel, schritt: 1, min: 0, ...optionen,
    beiAenderung: (w) => setzen(feld, w),
  });
  const stahl = () => zeile('Stahl', materialwahl('betonstahl', werte.stahl, (w) => setzen('stahl', w)));
  const haken = (text, feld) => el('div.cad-zeile', {}, [
    el('span', { text }), hakenSchalter(werte[feld] !== false, (w) => setzen(feld, w), text), el('span'),
  ]);
  if (liste === 'staebe') {
    return [zeile('⌀', zahl('durchmesser', 'Stabdurchmesser', { stufen: durchmesser }), 'mm'), stahl()];
  }
  if (liste === 'stablinien') {
    const arten = zustand.katalog?.querschnittsanalyse?.linienarten || [];
    const art = werte.art;
    return [
      zeile('Verteilung', auswahl({
        werte: arten.map((x) => ({ wert: x.wert, beschriftung: x.beschriftung })),
        gewaehlt: art,
        titel: 'verschmiert: eine Stahlfläche; Anzahl: n Stäbe; Teilung: Abstand, gerundet auf einen, der aufgeht',
        beiAenderung: (w) => setzen('art', w),
      })),
      art === 'flaeche' ? zeile('A_s', zahl('flaeche', 'Stahlfläche der ganzen Linie', { schritt: 100 }), 'mm²') : null,
      art === 'anzahl' ? zeile('n', zahl('anzahl', 'Anzahl Stäbe', { min: 1 })) : null,
      art === 'teilung' ? zeile('s', zahl('teilung', 'Gewünschte Teilung', { schritt: 25, min: 1 }), 'mm') : null,
      art !== 'flaeche' ? zeile('⌀', zahl('durchmesser', 'Stabdurchmesser', { stufen: durchmesser }), 'mm') : null,
      art !== 'flaeche' ? haken('Starteisen', 'starteisen') : null,
      art !== 'flaeche' ? haken('Endeisen', 'endeisen') : null,
      stahl(),
    ];
  }
  if (liste === 'schubwaende') {
    const schnitte = zustand.katalog?.querschnittsanalyse?.schnitte || [1, 2, 3, 4, 5, 6, 7, 8];
    return [
      zeile('b_w', zahl('dicke', 'Dicke der Schubwand', { schritt: 10, min: 1 }), 'mm'),
      zeile('Bügel ⌀', zahl('durchmesser', 'Bügeldurchmesser; 0: ohne Bügel', { stufen: durchmesser }), 'mm'),
      zeile('s', zahl('teilung', 'Bügelteilung in Längsrichtung', { schritt: 25, min: 1 }), 'mm'),
      zeile('Schnitte', auswahl({
        werte: schnitte.map((n) => ({ wert: String(n), beschriftung: String(n) })),
        gewaehlt: String(werte.schnitte),
        titel: 'Wie viele Bügelschenkel die Wand kreuzen',
        beiAenderung: (w) => setzen('schnitte', Number(w)),
      })),
      stahl(),
    ];
  }
  if (liste === 'flaechen') {
    return [zeile('Material', materialwahl('beton', werte.material, (w) => setzen('material', w), true))];
  }
  return [];
}

/** Die Wahl der Linienart -- beim Neuen wie beim Gewählten dieselbe. */
function linienartwahl(gewaehlt, setzen) {
  return zeile('Art', auswahl({
    werte: LINIENARTEN.map((x) => ({ wert: x.wert, beschriftung: x.text })),
    gewaehlt,
    titel: 'Bewehrung, Schubwand oder Hilfslinie -- eine Hilfslinie rechnet nicht mit',
    beiAenderung: setzen,
  }));
}

/** Die Vorgaben für das, was ein Werkzeug als Nächstes anlegt. */
function neuEigenschaften(a, werkzeug) {
  const v = a.qa.vorgaben;
  const neu = () => a.neuZeichnen();
  const vorgabeSetzen = (liste) => (feld, wert) => { v[liste][feld] = wert; neu(); };
  let inhalt = [];
  if (werkzeug === 'knoten') {
    inhalt = [
      zeile('Art', auswahl({
        werte: [{ wert: 'stab', beschriftung: 'Stab' }, { wert: 'punkt', beschriftung: 'nur Knoten' }],
        gewaehlt: v.knoten.art,
        beiAenderung: (w) => { v.knoten.art = w; neu(); },
      })),
      ...(v.knoten.art === 'stab' ? felderVon('staebe', v.stab, vorgabeSetzen('stab')) : []),
    ];
  } else if (werkzeug === 'linie') {
    inhalt = [
      linienartwahl(v.linie.art, (w) => { v.linie.art = w; neu(); }),
      ...felderVon(v.linie.art, v[v.linie.art], vorgabeSetzen(v.linie.art)),
    ];
  } else if (werkzeug === 'flaeche') {
    inhalt = felderVon('flaechen', v.flaeche, vorgabeSetzen('flaeche'));
  }
  return {
    inhalt: [el('div.cad-neu-titel', { text: 'Neu' }), ...inhalt.filter(Boolean)],
    schluessel: JSON.stringify([werkzeug, v]),
  };
}

/** In welcher Liste ein Element steht -- und das Element selbst. */
function finden(z, kennung) {
  for (const art of ARTEN) {
    const e = (z[art.liste] || []).find((x) => x.kennung === kennung);
    if (e) return { liste: art.liste, e };
  }
  const k = (z.knoten || []).find((x) => x.kennung === kennung);
  return k ? { liste: 'knoten', e: k } : null;
}

/**
 * Wechselt die Art einer Linie: der Eintrag wandert in die andere Liste,
 * mit Kennung, Anfang und Ende. Was er an Eigenschaften der alten Art hatte,
 * merkt sich die Ansicht -- wer zurückwechselt, findet es wieder.
 */
function linienartWechseln(a, kennung, nach) {
  a.aendern((z) => {
    const da = finden(z, kennung);
    if (!da || da.liste === nach) return;
    const kern = Object.fromEntries(LINIENKERN.map((f) => [f, da.e[f]]));
    const rest = Object.fromEntries(Object.entries(da.e).filter(([f]) => !LINIENKERN.includes(f)));
    a.qa.gemerkt.set(`${kennung}|${da.liste}`, rest);
    const frueher = a.qa.gemerkt.get(`${kennung}|${nach}`);
    const vorlage = LINIENARTEN.find((x) => x.wert === nach).vorlage;
    const stahl = rest.stahl || a.qa.vorgaben.stablinien.stahl;
    const basis = frueher || { ...ausVorlage(vorlage), ...(nach === 'hilfslinien' ? {} : { stahl }) };
    z[da.liste] = z[da.liste].filter((x) => x.kennung !== kennung);
    z[nach].push({ ...structuredClone(basis), ...kern });
  });
}

/** Die Eigenschaften der Auswahl -- änderbar, bei mehreren gleicher Art für alle zugleich. */
function eigenschaften(a) {
  const z = eintragVon(a.qa.kennung);
  const gewaehlt = [...a.auswahl].map((k) => finden(z, k)).filter(Boolean);
  if (!gewaehlt.length) return { titel: '', inhalt: [] };
  const listen = new Set(gewaehlt.map((x) => x.liste));
  if (listen.size > 1) {
    return {
      titel: `${gewaehlt.length} Elemente`,
      inhalt: [el('p.cad-hinweis-klein', { text: 'Verschiedene Arten -- gemeinsame Eigenschaften gibt es nur bei gleicher Art.' })],
    };
  }
  const liste = [...listen][0];
  const kennungen = gewaehlt.map((x) => x.e.kennung);
  const setzen = (feld, wert) => a.aendern((zz) => {
    for (const k of kennungen) {
      const da = finden(zz, k);
      if (da) da.e[feld] = wert;
    }
  });
  const e = gewaehlt[0].e;
  const mehrere = gewaehlt.length > 1;
  let titel = `${elementname(a, e.kennung)} · ${artText(liste, e)}`;
  if (mehrere) titel = `${gewaehlt.length} × ${artText(liste, e)}`;
  else if (liste === 'knoten') titel = elementname(a, e.kennung);

  if (liste === 'knoten') {
    const lageSetzen = (i) => (w) => a.aendern((zz) => {
      const ziele = new Set(kennungen);
      const k = zz.knoten.find((x) => ziele.has(x.kennung));
      if (!k) return;
      const d = i === 0 ? [w - k.y, 0] : [0, w - k.z];
      a.modell.verschieben(zz, ziele, d);
    });
    return {
      titel,
      inhalt: mehrere ? [el('p.cad-hinweis-klein', { text: 'Mehrere Knoten: verschieben mit V.' })] : [
        zeile('y', zahlfeld({ wert: e.y, schritt: a.raster, beiAenderung: lageSetzen(0) }), 'mm'),
        zeile('z', zahlfeld({ wert: e.z, schritt: a.raster, beiAenderung: lageSetzen(1) }), 'mm'),
        el('p.cad-hinweis-klein', { text: 'Was an diesem Knoten hängt, geht mit.' }),
      ],
    };
  }
  const inhalt = [];
  if (LINIENLISTEN.includes(liste)) {
    inhalt.push(linienartwahl(liste, (w) => kennungen.forEach((k) => linienartWechseln(a, k, w))));
  }
  inhalt.push(...felderVon(liste, e, setzen));
  if (!mehrere) inhalt.push(...infozeilen(a, liste, e));
  // Neu, sobald die Antwort des Kerns da ist: die Zeilen darunter kommen von ihm.
  return { titel, inhalt: inhalt.filter(Boolean), schluessel: Boolean(passendeGeometrie(a)) };
}

function artText(liste, e) {
  return {
    knoten: 'Knoten', staebe: 'Stab', stablinien: 'Bewehrung', schubwaende: 'Schubwand',
    hilfslinien: 'Hilfslinie', flaechen: e.material ? stoffname(e.material) : 'Aussparung',
  }[liste];
}

/** Was der Kern zum Element sagt -- tatsächliche Teilung, Länge, A_sw/s, Meldungen. */
function infozeilen(a, liste, e) {
  const geo = passendeGeometrie(a);
  const zeilen = [];
  const lagen = a.modell.lagen(eintragVon(a.qa.kennung));
  if (LINIENLISTEN.includes(liste)) {
    const [p, q] = [lagen.get(e.von), lagen.get(e.bis)];
    if (p && q) zeilen.push(`L = ${zahlText(abstand(p, q))} mm`);
  }
  if (liste === 'stablinien') {
    const info = geo?.linien?.find((x) => x.kennung === e.kennung);
    if (info?.punkte) zeilen.push(`${linienText(e, info)} · A_s ${zahlText(info.flaeche, 0)} mm²`);
  }
  if (liste === 'schubwaende') {
    const info = geo?.waende?.find((x) => x.kennung === e.kennung);
    if (info) zeilen.push(`A_sw/s = ${zahlText(info.a_sw_s, 0)} mm²/m`);
  }
  if (liste === 'flaechen') zeilen.push(`${e.knoten.length} Ecken`);
  const meldungen = (geo?.meldungen || []).filter((m) => m.elemente.includes(e.kennung));
  return [
    ...zeilen.map((t) => el('p.cad-info', { text: t })),
    ...meldungen.map((m) => el('p.cad-meldung', { text: m.text })),
  ];
}

// ===========================================================================
// Was neben der Auswahl angeboten wird
// ===========================================================================

/**
 * Die gewählten Hilfslinien als ein geschlossener Umriss -- seine Knoten der
 * Reihe nach, oder null. Jede Ecke hat genau zwei Linien, und alle hängen
 * zusammen.
 */
function umlauf(z, kennungen) {
  const linien = (z.hilfslinien || []).filter((h) => kennungen.has(h.kennung));
  if (linien.length < 3 || linien.length !== kennungen.size) return null;
  const nachbarn = new Map();
  for (const h of linien) {
    if (h.von === h.bis) return null;
    nachbarn.set(h.von, [...(nachbarn.get(h.von) || []), h.bis]);
    nachbarn.set(h.bis, [...(nachbarn.get(h.bis) || []), h.von]);
  }
  if ([...nachbarn.values()].some((n) => n.length !== 2)) return null;
  const start = linien[0].von;
  const reihe = [start];
  let vorher = null;
  let jetzt = start;
  for (;;) {
    const weiter = nachbarn.get(jetzt).find((k) => k !== vorher);
    if (weiter === start) break;
    if (reihe.includes(weiter)) return null;
    reihe.push(weiter);
    vorher = jetzt;
    jetzt = weiter;
  }
  return reihe.length === nachbarn.size ? reihe : null;
}

function aktionen(a) {
  const z = eintragVon(a.qa.kennung);
  const liste = [];
  const reihe = umlauf(z, a.auswahl);
  if (reihe) {
    liste.push({
      zeichen: '▱', text: 'Fläche bilden', titel: 'Die geschlossenen Hilfslinien werden eine Fläche',
      tun: () => {
        const weg = new Set(a.auswahl);
        let neu = null;
        a.aendern((zz) => {
          neu = flaecheAnlegen(a, zz, reihe);
          zz.hilfslinien = zz.hilfslinien.filter((h) => !weg.has(h.kennung));
        }, { auswahl: () => [neu] });
      },
    });
  }
  return liste;
}

