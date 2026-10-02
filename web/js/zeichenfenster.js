/**
 * zeichenfenster.js -- das Zeichenfenster der Querschnittsanalyse.
 *
 * Polygone mit Material, Aussparungen, Stäbe, Stablinien und Schubwände --
 * gezeichnet mit der Maus oder dem Finger, in mm, y nach rechts und z nach
 * oben. Dazu Raster und Fang, Zoom an der Zeigerstelle, Verschieben,
 * Auswählen und Ziehen, Rückgängig und ein Vollbild.
 *
 * WAS HIER GERECHNET WIRD -- UND WAS NICHT:
 * Raster, Fang, Zoom, Masslinien und das Treffen eines Elements mit dem
 * Zeiger sind Eingabehilfen; sie stehen hier. Was in die Rechnung geht,
 * kommt vom Kern über die Anfrage `geometrie`: die Stäbe einer Linie und
 * ihre tatsächliche Teilung, der Schwerpunkt, die Zellen der Schubwände,
 * welches Polygon in welchem liegt und jede Meldung. Diese Antwort gilt nur,
 * solange die Zeichnung dieselbe ist, nach der gefragt wurde -- sonst wird
 * sie nicht gezeigt, statt etwas Veraltetes als gültig hinzustellen.
 *
 * EIN BLEIBENDES FENSTER:
 * Die mittlere Tafel wird nach jeder Änderung neu gebaut. Das Fenster nicht:
 * es entsteht einmal je Analyse und wird bei jedem Neubau wieder eingehängt.
 * Werkzeug, Massstab, ein halb gezeichnetes Polygon und der Verlauf für
 * «Rückgängig» überstehen so jede Rechnung, die zwischendurch fertig wird.
 * Ins Projekt geht eine Änderung erst beim Loslassen, nie während des
 * Ziehens.
 */

import { api } from './api.js';
import { el, melden, svgEl, zahlfeld } from './dom.js';
import { aendern, ausVorlage, projektAendern, zustand } from './zustand.js';

/** Je Elementart die Liste der Beschreibung und der Name im Kern. */
const LISTEN = {
  flaeche: 'flaechen', stab: 'staebe', linie: 'stablinien', wand: 'schubwaende',
};
const ZEICHENFELDER = Object.values(LISTEN);

/** Wie nah der Zeiger an etwas sein muss, um es zu treffen oder zu fangen -- px. */
const NAEHE = 9;
/** Ab wie viel Bewegung ein Druck ein Ziehen ist und kein Klick -- px. */
const ZITTERN = 4;
/** Die Raster, die zur Wahl stehen -- mm. */
const RASTER = [1, 5, 10, 25, 50, 100];
/** In wie viele Ecken ein Kreis zerlegt wird. */
const KREISECKEN = 48;
/** Wie viele Schritte «Rückgängig» zurückreicht. */
const VERLAUF = 100;

const WERKZEUGE = [
  { name: 'waehlen', zeichen: '↖', text: 'Wählen', taste: 'v' },
  { name: 'polygon', zeichen: '▱', text: 'Polygon', taste: 'p' },
  { name: 'rechteck', zeichen: '▭', text: 'Rechteck', taste: 'r' },
  { name: 'kreis', zeichen: '◯', text: 'Kreis', taste: 'k' },
  { name: 'stab', zeichen: '•', text: 'Stab', taste: 's' },
  { name: 'linie', zeichen: '⋯', text: 'Linie', taste: 'l' },
  { name: 'wand', zeichen: '▥', text: 'Schubwand', taste: 'w' },
];

/** Welche Elementart ein Werkzeug anlegt. */
const ANLEGEN = {
  polygon: 'flaeche', rechteck: 'flaeche', kreis: 'flaeche',
  stab: 'stab', linie: 'linie', wand: 'wand',
};

// ===========================================================================
// Zustand je Analyse
// ===========================================================================

/** Kennung der Analyse -> ihre Ansicht. Keine Projektdaten: nichts davon wird abgelegt. */
const ansichten = new Map();

/** Die Ansicht, die gerade Tasten bekommt -- die zuletzt angeklickte. */
let aktive = null;

export function ansichtVon(kennung) {
  let a = ansichten.get(kennung);
  // Ein anderes Projekt -- geöffnet oder neu geladen -- kann dieselben
  // Kennungen tragen. Sein Verlauf und seine Auswahl gehören nicht hierher.
  if (a && a.projekt !== zustand.projekt) a = null;
  if (!a) {
    a = {
      kennung,
      projekt: zustand.projekt,
      massstab: null,          // px je mm; null: noch nie eingepasst
      ursprung: [0, 0],        // wo der Nullpunkt im Bild liegt, px
      breite: 0, hoehe: 0,     // Grösse des Bildes, px
      werkzeug: 'waehlen',
      auswahl: null,           // {art, index, ecke?}
      entwurf: null,           // was gerade gezeichnet wird
      ziehen: null,            // {art, index, element}: Vorschau beim Ziehen
      druck: null,             // laufender Druck auf das Bild
      finger: new Map(),       // Berührungen, für das Kneifen
      kneifen: null,
      zeiger: null,            // {bild, welt, fang} -- letzte Zeigerlage
      leertaste: false,
      raster: 10, fang: true,
      relativ: false,          // Koordinatenfenster: absolut oder relativ
      vollbild: false,
      vorlageOffen: false,
      rueck: [], vor: [],      // Verlauf als Abdrücke der Zeichnung
      geometrie: null,         // letzte Antwort des Kerns
      gefragt: null,           // Abdruck der letzten Anfrage
      vorgaben: null,          // je Elementart die Werte für das nächste neue
      knoten: null, teile: null,
      kurzhinweis: '', kurzUhr: null,
    };
    ansichten.set(kennung, a);
  }
  return a;
}

/** Für eine neu angelegte Analyse: nichts von einer früheren mit derselben Kennung. */
export function ansichtVergessen(kennung) {
  if (aktive === ansichten.get(kennung)) aktive = null;
  ansichten.delete(kennung);
}

function eintragVon(kennung) {
  return zustand.projekt?.querschnittsanalysen?.find((x) => x.kennung === kennung) || null;
}

/** Die Zeichnung als Text: die vier Listen, sonst nichts. */
function stand(analyse) {
  return JSON.stringify(ZEICHENFELDER.map((f) => analyse[f]));
}

/** Was die Antwort des Kerns ausserdem abhängig macht: welche Materialien es gibt. */
function abdruck(analyse) {
  const stoffe = zustand.projekt.materialien.map((m) => [m.kennung, m.art]);
  return `${stand(analyse)}|${JSON.stringify(stoffe)}`;
}

/**
 * Ändert die Zeichnung und merkt sich den Stand davor -- der eine Weg, auf
 * dem Fenster und Koordinaten die Zeichnung ändern. Der Stand wird *vor*
 * der Änderung abgelegt: das Neuzeichnen, das sie auslöst, soll den Knopf
 * «Rückgängig» schon anbieten.
 */
export function zeichnungAendern(kennung, veraenderer) {
  const a = ansichtVon(kennung);
  const vorher = stand(eintragVon(kennung));
  a.rueck.push(vorher);
  if (a.rueck.length > VERLAUF) a.rueck.shift();
  const vor = a.vor;
  a.vor = [];
  projektAendern((p) => {
    veraenderer(p.querschnittsanalysen.find((x) => x.kennung === kennung));
  });
  if (stand(eintragVon(kennung)) === vorher) {
    a.rueck.pop();
    a.vor = vor;
  }
}

function standSetzen(a, text) {
  const werte = JSON.parse(text);
  a.auswahl = null;
  a.entwurf = null;
  projektAendern((p) => {
    const x = p.querschnittsanalysen.find((y) => y.kennung === a.kennung);
    ZEICHENFELDER.forEach((f, i) => { x[f] = werte[i]; });
  });
}

function zurueck(a) {
  if (!a.rueck.length) return;
  a.vor.push(stand(eintragVon(a.kennung)));
  standSetzen(a, a.rueck.pop());
}

function vorwaerts(a) {
  if (!a.vor.length) return;
  a.rueck.push(stand(eintragVon(a.kennung)));
  standSetzen(a, a.vor.pop());
}

/** Wählt ein Element -- oder nichts. Die Koordinaten daneben zeigen es. */
export function waehlen(kennung, auswahl) {
  const a = ansichtVon(kennung);
  a.auswahl = auswahl;
  zeichnen(a);
  aendern({}, 'zeichnung');
}

/**
 * Die Werte für das nächste neue Element je Art -- aus den Vorlagen des
 * Kerns, mit dem ersten Beton und dem ersten Betonstahl des Projekts.
 */
function vorgabenSetzen(a) {
  const beton = zustand.projekt.materialien.find((m) => m.art === 'beton');
  const stahl = zustand.projekt.materialien.find((m) => m.art === 'betonstahl');
  const mit = (art, felder = {}) => ausVorlage(art, felder);
  a.vorgaben = {
    flaeche: mit('flaeche', { material: beton?.kennung || '' }),
    stab: mit('stab', { stahl: stahl?.kennung || '' }),
    linie: mit('stablinie', { stahl: stahl?.kennung || '' }),
    wand: mit('schubwand', { stahl: stahl?.kennung || '' }),
  };
}

/** «Polygon 2», «Aussparung 3», «Stab 1» -- so heissen die Elemente beim Kern. */
export function elementname(analyse, art, index) {
  if (art === 'flaeche') {
    return `${analyse.flaechen[index]?.material ? 'Polygon' : 'Aussparung'} ${index + 1}`;
  }
  return `${{ stab: 'Stab', linie: 'Linie', wand: 'Wand' }[art]} ${index + 1}`;
}

/** Umgekehrt: aus «Linie 2» die Art und die Stelle in der Liste. */
export function elementAusName(name) {
  const treffer = /^(Polygon|Aussparung|Stab|Linie|Wand) (\d+)$/.exec(name || '');
  if (!treffer) return null;
  const art = {
    Polygon: 'flaeche', Aussparung: 'flaeche', Stab: 'stab', Linie: 'linie', Wand: 'wand',
  }[treffer[1]];
  return { art, index: Number(treffer[2]) - 1 };
}

/**
 * Die Antwort des Kerns -- aber nur, wenn sie zur Zeichnung passt, die
 * gerade zu sehen ist. Beim Ziehen ist das nie der Fall: dann fehlen
 * Schwerpunkt, Zellen und Meldungen, bis die neue Antwort da ist.
 */
export function passendeGeometrie(a, analyse, daten = null) {
  const g = a.geometrie;
  if (!g || g.abdruck !== abdruck(analyse)) return null;
  if (daten && JSON.stringify(ZEICHENFELDER.map((f) => daten[f])) !== g.stand) return null;
  return g;
}

/**
 * Fragt den Kern nach der Zeichnung, wenn sie sich seit der letzten Frage
 * geändert hat. Kommt eine Antwort zu spät -- es wurde inzwischen wieder
 * gefragt --, gilt sie nicht mehr.
 */
function geometrieHolen(a, analyse) {
  const jetzt = abdruck(analyse);
  if (a.gefragt === jetzt) return;
  a.gefragt = jetzt;
  const zeichnung = JSON.parse(stand(analyse));
  api.geometrie(zustand.projekt, a.kennung).then((antwort) => {
    if (a.gefragt !== jetzt) return;
    a.geometrie = {
      ...antwort,
      abdruck: jetzt,
      stand: JSON.stringify(zeichnung),
      zeichnung: Object.fromEntries(ZEICHENFELDER.map((f, i) => [f, zeichnung[i]])),
    };
    zeichnen(a);
    aendern({}, 'zeichnung');
  }).catch((fehler) => {
    if (a.gefragt === jetzt) melden(fehler.message, true);
  });
}

// ===========================================================================
// Bild und Welt
// ===========================================================================

const nachBild = (a, [y, z]) => [a.ursprung[0] + a.massstab * y, a.ursprung[1] - a.massstab * z];
const nachWelt = (a, [x, h]) => [(x - a.ursprung[0]) / a.massstab, (a.ursprung[1] - h) / a.massstab];

/** Eine Zahl, wie sie im Fenster steht: höchstens eine Nachkommastelle. */
export function zahlText(wert, stellen = 1) {
  return String(Number(Number(wert).toFixed(stellen)));
}

function abstand(p, q) {
  return Math.hypot(p[0] - q[0], p[1] - q[1]);
}

/** Der nächste Punkt auf der Strecke a-b -- und wie weit er entlang liegt (0 bis 1). */
function aufStrecke(p, s, e) {
  const [dy, dz] = [e[0] - s[0], e[1] - s[1]];
  const l2 = dy * dy + dz * dz;
  const t = l2 ? Math.max(0, Math.min(1, ((p[0] - s[0]) * dy + (p[1] - s[1]) * dz) / l2)) : 0;
  return { q: [s[0] + t * dy, s[1] + t * dz], t };
}

/** Liegt p im Polygon? Gerade-ungerade-Regel -- nur zum Treffen mit dem Zeiger. */
function innen(p, punkte) {
  let drin = false;
  for (let i = 0, j = punkte.length - 1; i < punkte.length; j = i, i += 1) {
    const [yi, zi] = punkte[i];
    const [yj, zj] = punkte[j];
    if ((zi > p[1]) !== (zj > p[1])
        && p[0] < ((yj - yi) * (p[1] - zi)) / (zj - zi) + yi) drin = !drin;
  }
  return drin;
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

/** Die Zeichnung, wie sie gerade zu sehen ist -- beim Ziehen mit dem gezogenen Element. */
function zeichenDaten(a, analyse) {
  const daten = Object.fromEntries(ZEICHENFELDER.map((f) => [f, analyse[f]]));
  if (a.ziehen) {
    const liste = [...daten[LISTEN[a.ziehen.art]]];
    liste[a.ziehen.index] = a.ziehen.element;
    daten[LISTEN[a.ziehen.art]] = liste;
  }
  return daten;
}

/** Was im Bild zu sehen sein soll: alles, was gezeichnet ist, sonst ein Meter im Quadrat. */
function umriss(daten) {
  const punkte = [
    ...daten.flaechen.flatMap((f) => f.punkte),
    ...daten.staebe.map((s) => [s.y, s.z]),
    ...daten.stablinien.flatMap((l) => [l.von, l.bis]),
    ...daten.schubwaende.flatMap((w) => [w.von, w.bis]),
  ];
  if (!punkte.length) return [[0, 0], [1000, 1000]];
  const ys = punkte.map((p) => p[0]);
  const zs = punkte.map((p) => p[1]);
  return [[Math.min(...ys), Math.min(...zs)], [Math.max(...ys), Math.max(...zs)]];
}

/** Alles ins Bild -- mit Rand für die Masslinien. */
function allesZeigen(a) {
  const analyse = eintragVon(a.kennung);
  if (!analyse || !a.breite) return;
  const [[y0, z0], [y1, z1]] = umriss(zeichenDaten(a, analyse));
  const rand = 46;
  const b = Math.max(y1 - y0, 1);
  const h = Math.max(z1 - z0, 1);
  a.massstab = Math.max(1e-3, Math.min((a.breite - 2 * rand) / b, (a.hoehe - 2 * rand) / h));
  a.ursprung = [
    a.breite / 2 - a.massstab * (y0 + y1) / 2,
    a.hoehe / 2 + a.massstab * (z0 + z1) / 2,
  ];
  zeichnen(a);
}

/** Zoomt um `faktor` und hält dabei den Weltpunkt unter `bild` fest. */
function zoomen(a, faktor, bild) {
  const neu = Math.min(80, Math.max(1e-3, a.massstab * faktor));
  const f = neu / a.massstab;
  a.ursprung = [bild[0] - (bild[0] - a.ursprung[0]) * f, bild[1] - (bild[1] - a.ursprung[1]) * f];
  a.massstab = neu;
}

// ===========================================================================
// Fang
// ===========================================================================

/**
 * Wohin ein Zeigerpunkt fängt: an einen Punkt der Zeichnung (Ecke,
 * Kantenmitte, Stab, Ende einer Linie oder Wand, Schwerpunkt), sonst an eine
 * Kante oder Wandachse, sonst ans Raster. `ohne` nimmt das gezogene Element
 * aus -- eine Ecke soll nicht an sich selbst fangen.
 *
 * Auf einer schrägen Kante bleibt der Punkt genau auf ihr, ungerundet: eine
 * Wand, die auf einer anderen endet, muss genau auf deren Achse liegen, sonst
 * erkennt der Kern die Zelle nicht.
 */
function fangen(a, bild, { ohne = null, bezug = null, gerade = false, frei = false } = {}) {
  let welt = nachWelt(a, bild);
  const raster = (v) => Math.round(v / a.raster) * a.raster;

  // Shift: waagrecht oder senkrecht zum vorigen Punkt.
  if (gerade && bezug) {
    const waagrecht = Math.abs(welt[0] - bezug[0]) >= Math.abs(welt[1] - bezug[1]);
    welt = waagrecht ? [welt[0], bezug[1]] : [bezug[0], welt[1]];
    if (!a.fang || frei) return { p: welt, art: 'frei' };
    return {
      p: waagrecht ? [raster(welt[0]), bezug[1]] : [bezug[0], raster(welt[1])], art: 'raster',
    };
  }
  if (!a.fang || frei) return { p: welt, art: 'frei' };

  const analyse = eintragVon(a.kennung);
  const daten = zeichenDaten(a, analyse);
  const weit = NAEHE / a.massstab;
  const fremd = (art, index) => !ohne || ohne.art !== art || ohne.index !== index;

  let bester = null;
  const pruefen = (p, art) => {
    const d = abstand(welt, p);
    if (d <= weit && (!bester || d < bester.d)) bester = { p, d, art };
  };

  daten.flaechen.forEach((f, i) => f.punkte.forEach((p, k) => {
    if (fremd('flaeche', i) || ohne.ecke !== k) pruefen(p, 'punkt');
    const q = f.punkte[(k + 1) % f.punkte.length];
    if (fremd('flaeche', i)) pruefen([(p[0] + q[0]) / 2, (p[1] + q[1]) / 2], 'mitte');
  }));
  daten.staebe.forEach((s, i) => { if (fremd('stab', i)) pruefen([s.y, s.z], 'punkt'); });
  daten.stablinien.forEach((l, i) => {
    if (fremd('linie', i)) { pruefen(l.von, 'punkt'); pruefen(l.bis, 'punkt'); }
  });
  daten.schubwaende.forEach((w, i) => {
    if (fremd('wand', i)) { pruefen(w.von, 'punkt'); pruefen(w.bis, 'punkt'); }
  });
  const g = passendeGeometrie(a, analyse, daten);
  if (g?.brutto) pruefen([g.brutto.y_S, g.brutto.z_S], 'punkt');
  if (bester) return bester;

  const kanten = [];
  daten.flaechen.forEach((f, i) => {
    if (!fremd('flaeche', i)) return;
    f.punkte.forEach((p, k) => kanten.push([p, f.punkte[(k + 1) % f.punkte.length]]));
  });
  daten.schubwaende.forEach((w, i) => { if (fremd('wand', i)) kanten.push([w.von, w.bis]); });
  daten.stablinien.forEach((l, i) => { if (fremd('linie', i)) kanten.push([l.von, l.bis]); });
  for (const [s, e] of kanten) {
    const { q } = aufStrecke(welt, s, e);
    const d = abstand(welt, q);
    if (d > weit * 0.8 || (bester && d >= bester.d)) continue;
    // Auf einer waagrechten oder senkrechten Kante darf die freie Richtung
    // ans Raster -- der Punkt bleibt trotzdem genau auf der Kante.
    let p = q;
    if (Math.abs(e[1] - s[1]) < 1e-9) p = [raster(q[0]), s[1]];
    else if (Math.abs(e[0] - s[0]) < 1e-9) p = [s[0], raster(q[1])];
    // Gerundet über das Ende hinaus: dann eben ungerundet.
    if (abstand(aufStrecke(p, s, e).q, p) > 1e-9) p = q;
    bester = { p, d, art: 'kante' };
  }
  if (bester) return bester;
  return { p: [raster(welt[0]), raster(welt[1])], art: 'raster' };
}

// ===========================================================================
// Zeichnen
// ===========================================================================

function pfad(a, punkte, zu = true) {
  return punkte.map((p, i) => {
    const [x, y] = nachBild(a, p);
    return `${i ? 'L' : 'M'}${x.toFixed(1)} ${y.toFixed(1)}`;
  }).join(' ') + (zu ? ' Z' : '');
}

function text(x, y, inhalt, klasse = 'zf-beschriftung', anker = 'middle') {
  const t = svgEl('text', { x: x.toFixed(1), y: y.toFixed(1), 'text-anchor': anker, class: klasse });
  t.textContent = inhalt;
  return t;
}

/** Die Rasterlinien, so dicht, dass sie nicht verschwimmen: das Raster mal 1, 2, 5, 10 … */
function rasterZeichnen(a) {
  const g = svgEl('g');
  let schritt = a.raster;
  for (let i = 1; schritt * a.massstab < 14 && i < 30; i += 1) {
    schritt = a.raster * [1, 2, 5][i % 3] * 10 ** Math.floor(i / 3);
  }
  const [y0, z1] = nachWelt(a, [0, 0]);
  const [y1, z0] = nachWelt(a, [a.breite, a.hoehe]);
  let fein = '';
  let grob = '';
  const fuenf = schritt * 5;
  for (let y = Math.ceil(y0 / schritt) * schritt; y <= y1; y += schritt) {
    const x = nachBild(a, [y, 0])[0].toFixed(1);
    const d = `M${x} 0 V${a.hoehe}`;
    if (Math.abs(y / fuenf - Math.round(y / fuenf)) < 1e-6) grob += d; else fein += d;
  }
  for (let z = Math.ceil(z0 / schritt) * schritt; z <= z1; z += schritt) {
    const h = nachBild(a, [0, z])[1].toFixed(1);
    const d = `M0 ${h} H${a.breite}`;
    if (Math.abs(z / fuenf - Math.round(z / fuenf)) < 1e-6) grob += d; else fein += d;
  }
  const [nx, nh] = nachBild(a, [0, 0]);
  g.append(
    svgEl('path', { d: fein, class: 'zf-raster-fein' }),
    svgEl('path', { d: grob, class: 'zf-raster-grob' }),
    svgEl('path', { d: `M0 ${nh} H${a.breite} M${nx} 0 V${a.hoehe}`, class: 'zf-achse' }),
    text(a.breite - 6, nh - 5, 'y', 'zf-achstext', 'end'),
    text(nx + 6, 12, 'z', 'zf-achstext', 'start'),
  );
  return g;
}

/** Wie tief ein Polygon verschachtelt ist -- Eltern zuerst, damit Kinder darüber liegen. */
function tiefe(g, i) {
  let t = 0;
  let j = g?.polygone?.[i]?.eltern;
  while (j !== null && j !== undefined && t < 50) {
    t += 1;
    j = g.polygone[j]?.eltern;
  }
  return t;
}

function istGewaehlt(a, art, index) {
  return a.auswahl?.art === art && a.auswahl.index === index;
}

/**
 * Die Verschachtelung aus der letzten Antwort -- auch während eines Ziehens,
 * solange es gleich viele Polygone sind. Beim Ziehen eines Polygons über
 * eine Aussparung hinweg ist sie kurz falsch; schlimmer wäre, die Aussparung
 * dabei unter ihrem Polygon verschwinden zu sehen.
 */
function reihenfolge(a, daten) {
  const roh = a.geometrie;
  const reihe = daten.flaechen.map((_, i) => i);
  if (roh?.polygone?.length === daten.flaechen.length) {
    reihe.sort((i, j) => tiefe(roh, i) - tiefe(roh, j));
  }
  return reihe;
}

function flaechenZeichnen(a, analyse, daten, g, fehler) {
  const gruppe = svgEl('g');
  const reihe = reihenfolge(a, daten);
  for (const i of reihe) {
    const f = daten.flaechen[i];
    if (f.punkte.length < 2) continue;
    const name = elementname(analyse, 'flaeche', i);
    const klassen = [
      f.material ? 'zf-beton' : 'zf-loch',
      fehler.has(name) ? 'ist-fehler' : '',
      istGewaehlt(a, 'flaeche', i) ? 'ist-gewaehlt' : '',
    ];
    gruppe.append(meldungAn(svgEl('path', { d: pfad(a, f.punkte), class: klassen.join(' ') }),
      fehler.get(name)));
  }
  return gruppe;
}

function zellenZeichnen(a, g) {
  const gruppe = svgEl('g');
  for (const zelle of g?.zellen || []) {
    gruppe.append(svgEl('path', {
      d: pfad(a, zelle.punkte), class: 'zf-zelle', fill: `url(#zf-schraffur-${a.kennung})`,
    }));
  }
  return gruppe;
}

function waendeZeichnen(a, analyse, daten, fehler) {
  const gruppe = svgEl('g');
  daten.schubwaende.forEach((w, i) => {
    const name = elementname(analyse, 'wand', i);
    const ecken = band(w.von, w.bis, Math.max(w.dicke, 0));
    const gewaehlt = istGewaehlt(a, 'wand', i);
    const klasse = [fehler.has(name) ? 'ist-fehler' : '', gewaehlt ? 'ist-gewaehlt' : ''].join(' ');
    if (ecken) {
      gruppe.append(meldungAn(svgEl('path', { d: pfad(a, ecken), class: `zf-wand ${klasse}` }),
        fehler.get(name)));
    }
    gruppe.append(svgEl('path', { d: pfad(a, [w.von, w.bis], false), class: `zf-wandachse ${klasse}` }));
    // Die gewählte Wand sagt, was sie ist -- die Teilung sieht man im
    // Schnitt nicht.
    if (gewaehlt) {
      const [x, y] = nachBild(a, [(w.von[0] + w.bis[0]) / 2, (w.von[1] + w.bis[1]) / 2]);
      gruppe.append(text(x, y - 8, `b_w ${zahlText(w.dicke)} · ⌀${zahlText(w.durchmesser)} @ ${
        zahlText(w.teilung)} · ${w.schnitte}-schnittig`, 'zf-beschriftung zf-wandtext'));
    }
  });
  return gruppe;
}

/** Ein Stab: ein Kreis in seinem Durchmesser, aber nie kleiner als ein Punkt. */
function stabKreis(a, p, durchmesser, klasse) {
  const [x, y] = nachBild(a, p);
  return svgEl('circle', {
    cx: x.toFixed(1), cy: y.toFixed(1),
    r: Math.max(2.4, (a.massstab * durchmesser) / 2).toFixed(1), class: klasse,
  });
}

/**
 * Was an einer Stablinie steht -- aus der Antwort des Kerns, also mit der
 * tatsächlichen Teilung: «⌀16 @ 142.9 (gewählt 150)».
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

function linienZeichnen(a, analyse, daten, fehler) {
  const g = a.geometrie;
  const gruppe = svgEl('g');
  daten.stablinien.forEach((l, i) => {
    const name = elementname(analyse, 'linie', i);
    const klasse = [
      fehler.has(name) ? 'ist-fehler' : '',
      istGewaehlt(a, 'linie', i) ? 'ist-gewaehlt' : '',
    ].join(' ');
    const flaechig = l.art === 'flaeche';
    gruppe.append(meldungAn(svgEl('path', {
      d: pfad(a, [l.von, l.bis], false),
      class: `${flaechig ? 'zf-linie-flaeche' : 'zf-linie'} ${klasse}`,
    }), fehler.get(name)));
    // Die Stäbe der Linie kennt nur der Kern. Seine Antwort gilt für diese
    // Linie, solange sie so aussieht wie beim Fragen -- auch während eine
    // andere gezogen wird.
    const info = g?.linien?.[i];
    const passt = info && g.zeichnung.stablinien[i]
      && JSON.stringify(g.zeichnung.stablinien[i]) === JSON.stringify(l);
    if (!passt) return;
    if (!flaechig) {
      for (const p of info.punkte) gruppe.append(stabKreis(a, p, l.durchmesser, `zf-stab ${klasse}`));
    }
    const beschriftung = linienText(l, info);
    if (beschriftung) {
      const [x0, y0] = nachBild(a, l.von);
      const [x1, y1] = nachBild(a, l.bis);
      const lang = Math.hypot(x1 - x0, y1 - y0) || 1;
      // Links der Laufrichtung, also bei einer Linie nach rechts oberhalb.
      const [nx, ny] = [(y1 - y0) / lang, -(x1 - x0) / lang];
      const versatz = 9 + (flaechig ? 3 : Math.max(2.4, (a.massstab * l.durchmesser) / 2));
      gruppe.append(text((x0 + x1) / 2 + nx * versatz, (y0 + y1) / 2 + ny * versatz + 4,
        beschriftung, `zf-beschriftung zf-linientext ${klasse}`));
    }
  });
  return gruppe;
}

function staebeZeichnen(a, analyse, daten, fehler) {
  const gruppe = svgEl('g');
  daten.staebe.forEach((s, i) => {
    const name = elementname(analyse, 'stab', i);
    const klasse = [
      'zf-stab', fehler.has(name) ? 'ist-fehler' : '', istGewaehlt(a, 'stab', i) ? 'ist-gewaehlt' : '',
    ].join(' ');
    gruppe.append(meldungAn(stabKreis(a, [s.y, s.z], s.durchmesser, klasse), fehler.get(name)));
  });
  return gruppe;
}

/** Breite und Höhe dessen, was Material hat -- eine Masslinie unten, eine links. */
function masseZeichnen(a, daten) {
  const punkte = daten.flaechen.flatMap((f) => f.punkte);
  if (punkte.length < 2) return null;
  const ys = punkte.map((p) => p[0]);
  const zs = punkte.map((p) => p[1]);
  const [y0, y1, z0, z1] = [Math.min(...ys), Math.max(...ys), Math.min(...zs), Math.max(...zs)];
  const [xl, hu] = nachBild(a, [y0, z0]);
  const [xr, ho] = nachBild(a, [y1, z1]);
  const gruppe = svgEl('g');
  const unten = Math.min(hu + 22, a.hoehe - 8);
  const links = Math.max(xl - 22, 8);
  if (xr - xl > 30) {
    gruppe.append(
      svgEl('path', {
        d: `M${xl} ${unten} H${xr} M${xl} ${unten - 5} V${unten + 5} M${xr} ${unten - 5} V${unten + 5}`,
        class: 'zf-mass',
      }),
      text((xl + xr) / 2, unten - 4, zahlText(y1 - y0), 'zf-masstext'),
    );
  }
  if (hu - ho > 30) {
    const t = text(links - 4, (hu + ho) / 2, zahlText(z1 - z0), 'zf-masstext');
    t.setAttribute('transform', `rotate(-90 ${(links - 4).toFixed(1)} ${((hu + ho) / 2).toFixed(1)})`);
    gruppe.append(
      svgEl('path', {
        d: `M${links} ${ho} V${hu} M${links - 5} ${ho} H${links + 5} M${links - 5} ${hu} H${links + 5}`,
        class: 'zf-mass',
      }),
      t,
    );
  }
  return gruppe;
}

function schwerpunktZeichnen(a, g) {
  if (!g?.brutto) return null;
  const [x, y] = nachBild(a, [g.brutto.y_S, g.brutto.z_S]);
  const gruppe = svgEl('g', { class: 'zf-schwerpunkt' });
  gruppe.append(
    svgEl('circle', { cx: x, cy: y, r: 6 }),
    svgEl('path', { d: `M${x - 9} ${y} H${x + 9} M${x} ${y - 9} V${y + 9}` }),
    text(x + 9, y - 7, 'S', 'zf-schwerpunkttext', 'start'),
  );
  return gruppe;
}

/** Die Griffe des gewählten Elements: Ecken, Kantenmitten, Enden. */
function griffe(a, daten) {
  const w = a.auswahl;
  if (!w) return [];
  if (w.art === 'flaeche') {
    const punkte = daten.flaechen[w.index]?.punkte || [];
    // Kantenmitten nur bei wenigen Ecken: ein Kreis hätte sonst fast hundert
    // Griffe, und keiner liesse sich mehr treffen.
    const mitten = punkte.length <= 24 ? punkte : [];
    return [
      ...punkte.map((p, k) => ({ griff: 'ecke', ecke: k, p })),
      ...mitten.map((p, k) => {
        const q = punkte[(k + 1) % punkte.length];
        return { griff: 'mitte', ecke: k, p: [(p[0] + q[0]) / 2, (p[1] + q[1]) / 2] };
      }),
    ];
  }
  if (w.art === 'linie' || w.art === 'wand') {
    const e = daten[LISTEN[w.art]][w.index];
    return e ? [{ griff: 'von', p: e.von }, { griff: 'bis', p: e.bis }] : [];
  }
  return [];
}

function auswahlZeichnen(a, daten) {
  if (!a.auswahl || a.werkzeug !== 'waehlen') return null;
  const gruppe = svgEl('g');
  if (a.auswahl.art === 'stab') {
    const s = daten.staebe[a.auswahl.index];
    if (s) {
      const [x, y] = nachBild(a, [s.y, s.z]);
      gruppe.append(svgEl('circle', {
        cx: x, cy: y, r: Math.max(2.4, (a.massstab * s.durchmesser) / 2) + 4, class: 'zf-ring',
      }));
    }
  }
  for (const h of griffe(a, daten)) {
    const [x, y] = nachBild(a, h.p);
    if (h.griff === 'mitte') {
      gruppe.append(svgEl('circle', { cx: x, cy: y, r: 3.5, class: 'zf-mittelgriff' }));
    } else {
      const gewaehlt = h.griff === 'ecke' && a.auswahl.ecke === h.ecke;
      gruppe.append(svgEl('rect', {
        x: x - 4, y: y - 4, width: 8, height: 8,
        class: `zf-griff${gewaehlt ? ' ist-gewaehlt' : ''}`,
      }));
    }
  }
  return gruppe;
}

/** Ein Zettel am Zeiger: Länge und Abstände des Stücks, das gerade entsteht. */
function zettel(a, x, y, zeilen) {
  const gruppe = svgEl('g', { class: 'zf-zettel' });
  zeilen.forEach((z, i) => gruppe.append(text(x + 14, y + 18 + i * 13, z, 'zf-zetteltext', 'start')));
  return gruppe;
}

function entwurfZeichnen(a) {
  const e = a.entwurf;
  const zeiger = a.zeiger?.fang?.p;
  if (!e && !(a.werkzeug === 'stab' && zeiger)) return null;
  const gruppe = svgEl('g');
  const [zx, zy] = zeiger ? nachBild(a, zeiger) : [0, 0];
  const strecke = (p, q) => [
    `L = ${zahlText(abstand(p, q))}`, `Δy = ${zahlText(q[0] - p[0])}  Δz = ${zahlText(q[1] - p[1])}`,
  ];

  if (a.werkzeug === 'stab' && zeiger) {
    gruppe.append(stabKreis(a, zeiger, a.vorgaben.stab.durchmesser, 'zf-stab zf-geist'));
  } else if (e.art === 'polygon') {
    const punkte = zeiger ? [...e.punkte, zeiger] : e.punkte;
    gruppe.append(svgEl('path', { d: pfad(a, punkte, false), class: 'zf-entwurf' }));
    if (zeiger && e.punkte.length >= 2) {
      gruppe.append(svgEl('path', { d: pfad(a, [zeiger, e.punkte[0]], false), class: 'zf-entwurf-schluss' }));
    }
    for (const p of e.punkte) {
      const [x, y] = nachBild(a, p);
      gruppe.append(svgEl('circle', { cx: x, cy: y, r: 3, class: 'zf-entwurfpunkt' }));
    }
    if (zeiger) gruppe.append(zettel(a, zx, zy, strecke(e.punkte.at(-1), zeiger)));
  } else if (e.art === 'rechteck' && zeiger) {
    const [p, q] = [e.ecke, zeiger];
    gruppe.append(svgEl('path', {
      d: pfad(a, [p, [q[0], p[1]], q, [p[0], q[1]]]), class: 'zf-entwurf',
    }));
    gruppe.append(zettel(a, zx, zy, [`${zahlText(Math.abs(q[0] - p[0]))} × ${zahlText(Math.abs(q[1] - p[1]))}`]));
  } else if (e.art === 'kreis' && zeiger) {
    const r = abstand(e.mitte, zeiger);
    const [mx, my] = nachBild(a, e.mitte);
    gruppe.append(svgEl('circle', { cx: mx, cy: my, r: r * a.massstab, class: 'zf-entwurf' }));
    gruppe.append(zettel(a, zx, zy, [`D = ${zahlText(2 * r)}`]));
  } else if ((e.art === 'linie' || e.art === 'wand') && zeiger) {
    if (e.art === 'wand') {
      const ecken = band(e.von, zeiger, a.vorgaben.wand.dicke);
      if (ecken) gruppe.append(svgEl('path', { d: pfad(a, ecken), class: 'zf-wand zf-geist' }));
    }
    gruppe.append(svgEl('path', { d: pfad(a, [e.von, zeiger], false), class: 'zf-entwurf' }));
    gruppe.append(zettel(a, zx, zy, strecke(e.von, zeiger)));
  }
  return gruppe;
}

function fangZeichnen(a) {
  const f = a.zeiger?.fang;
  if (!f || (a.werkzeug === 'waehlen' && !a.ziehen)) return null;
  const [x, y] = nachBild(a, f.p);
  if (f.art === 'punkt' || f.art === 'mitte') {
    return svgEl('rect', { x: x - 5, y: y - 5, width: 10, height: 10, class: 'zf-fang' });
  }
  if (f.art === 'kante') {
    return svgEl('path', { d: `M${x} ${y - 6} L${x + 6} ${y} L${x} ${y + 6} L${x - 6} ${y} Z`, class: 'zf-fang' });
  }
  return svgEl('path', { d: `M${x - 5} ${y} H${x + 5} M${x} ${y - 5} V${y + 5}`, class: 'zf-fang' });
}

/** Je Element, das eine Meldung nennt, ihre Sätze -- es wird rot gezeichnet. */
function fehlerhafte(g) {
  const je = new Map();
  for (const m of g?.meldungen || []) {
    for (const name of m.elemente) je.set(name, [...(je.get(name) || []), m.text]);
  }
  return je;
}

/** Die Meldung als Zettel am Element: beim Darüberfahren steht da, was nicht stimmt. */
function meldungAn(knoten, texte) {
  if (texte?.length) {
    const t = svgEl('title');
    t.textContent = texte.join('\n');
    knoten.append(t);
  }
  return knoten;
}

/** Zeichnet das Bild neu -- aus dem Projekt, der Ansicht und der passenden Antwort des Kerns. */
function zeichnen(a) {
  const analyse = eintragVon(a.kennung);
  if (!analyse || !a.knoten) return;
  leisteZeichnen(a);
  statusZeichnen(a);
  // Noch nie gemessen, aber schon eingehängt: jetzt messen. Der Beobachter
  // meldet sich erst beim nächsten Bildaufbau, und den gibt es in einem
  // verborgenen Reiter nicht.
  if (!a.breite && a.knoten.isConnected) {
    groesseMessen(a);
    return;
  }
  if (!a.massstab || !a.breite) return;

  const daten = zeichenDaten(a, analyse);
  const g = passendeGeometrie(a, analyse, daten);
  const fehler = fehlerhafte(g);

  const schraffur = svgEl('pattern', {
    id: `zf-schraffur-${a.kennung}`, patternUnits: 'userSpaceOnUse',
    width: 7, height: 7, patternTransform: 'rotate(45)',
  });
  schraffur.append(svgEl('line', { x1: 0, y1: 0, x2: 0, y2: 7, class: 'zf-schraffurstrich' }));
  const defs = svgEl('defs');
  defs.append(schraffur);

  a.teile.bild.replaceChildren(...[
    defs,
    rasterZeichnen(a),
    flaechenZeichnen(a, analyse, daten, g, fehler),
    zellenZeichnen(a, g),
    waendeZeichnen(a, analyse, daten, fehler),
    linienZeichnen(a, analyse, daten, fehler),
    staebeZeichnen(a, analyse, daten, fehler),
    masseZeichnen(a, daten),
    schwerpunktZeichnen(a, g),
    auswahlZeichnen(a, daten),
    entwurfZeichnen(a),
    fangZeichnen(a),
  ].filter(Boolean));
  a.teile.bild.classList.toggle('ist-waehlen', a.werkzeug === 'waehlen');
}

// ===========================================================================
// Leiste, Optionen, Statuszeile
// ===========================================================================

function hinweis(a) {
  if (a.kurzhinweis) return a.kurzhinweis;
  const e = a.entwurf;
  switch (a.werkzeug) {
    case 'polygon':
      if (!e) return 'Ersten Punkt klicken.';
      return e.punkte.length < 3
        ? 'Nächsten Punkt klicken. Esc bricht ab, ⌫ nimmt den letzten zurück.'
        : 'Weiter klicken. Schliessen: Doppelklick, Enter oder Startpunkt. Esc bricht ab.';
    case 'rechteck': return e ? 'Gegenüberliegende Ecke klicken.' : 'Erste Ecke klicken.';
    case 'kreis': return e ? 'Punkt auf dem Rand klicken.' : 'Mittelpunkt klicken.';
    case 'stab': return `Klicken setzt einen Stab ⌀${zahlText(a.vorgaben.stab.durchmesser)}.`;
    case 'linie': return e ? 'Ende der Stablinie klicken.' : 'Anfang der Stablinie klicken.';
    case 'wand': return e ? 'Ende klicken -- von Gurt zu Gurt.' : 'Anfang der Schubwand klicken.';
    default:
      return a.auswahl
        ? 'Ziehen verschiebt, Griffe ändern die Form. Entf löscht, Esc wählt ab.'
        : 'Element anklicken. Leere Fläche ziehen verschiebt die Ansicht, Mausrad zoomt.';
  }
}

function statusZeichnen(a) {
  const f = a.zeiger?.fang;
  a.teile.lage.textContent = f ? `y = ${zahlText(f.p[0])}   z = ${zahlText(f.p[1])} mm` : '';
  a.teile.hinweis.textContent = hinweis(a);
}

/** Einen Satz kurz in die Statuszeile -- etwa, warum das Mausrad nicht zoomt. */
function kurzMelden(a, satz) {
  a.kurzhinweis = satz;
  clearTimeout(a.kurzUhr);
  a.kurzUhr = setTimeout(() => { a.kurzhinweis = ''; statusZeichnen(a); }, 2600);
  statusZeichnen(a);
}

function knopf(zeichen, beschriftung, titel, tun) {
  return el('button.zf-knopf', {
    type: 'button', title: titel,
    on: { click: (e) => { e.preventDefault(); tun(); } },
  }, [el('span.zf-zeichen', { text: zeichen }), beschriftung ? el('span.zf-text', { text: beschriftung }) : null]);
}

/**
 * Vollbild ein oder aus. Das Bild wird danach neu eingepasst: im Vollbild
 * soll der Querschnitt die Fläche füllen, zurück in der Tafel wieder ganz
 * zu sehen sein.
 */
function vollbildSetzen(a, an) {
  a.vollbild = an;
  a.einpassen = true;
  aendern({}, 'zeichnung');
}

function werkzeugWaehlen(a, name) {
  a.werkzeug = name;
  a.entwurf = null;
  a.vorlageOffen = false;
  vorlageZeichnen(a);
  optionenZeichnen(a);
  zeichnen(a);
  aendern({}, 'zeichnung');
}

function leisteBauen(a) {
  const werkzeuge = WERKZEUGE.map((w) => {
    const k = knopf(w.zeichen, w.text, `${w.text} (${w.taste.toUpperCase()})`,
      () => werkzeugWaehlen(a, w.name));
    k.dataset.werkzeug = w.name;
    return k;
  });
  const trenner = () => el('span.zf-trenner');
  const rueck = knopf('↶', '', 'Rückgängig (Strg+Z)', () => zurueck(a));
  const vor = knopf('↷', '', 'Wiederholen (Strg+Y)', () => vorwaerts(a));
  const vorlage = knopf('⊞', 'Vorlage', 'Querschnitt aus einer Vorlage', () => {
    a.vorlageOffen = !a.vorlageOffen;
    a.entwurf = null;
    vorlageZeichnen(a);
    zeichnen(a);
  });
  const raster = el('select.zf-raster', {
    title: 'Raster: daran fängt der Zeiger',
    on: {
      change: (e) => { a.raster = Number(e.target.value); zeichnen(a); },
    },
  }, RASTER.map((r) => el('option', { value: r, text: `${r} mm` })));
  const fang = el('input', {
    type: 'checkbox', title: 'Fang an Raster, Ecken und Kanten (Alt hält ihn an)',
    on: { change: (e) => { a.fang = e.target.checked; zeichnen(a); } },
  });
  const alles = knopf('⤧', 'Alles', 'Alles zeigen (F)', () => allesZeigen(a));
  const gross = knopf('⤢', 'Vollbild', 'Vollbild ein/aus', () => vollbildSetzen(a, !a.vollbild));
  a.teile.knoepfe = { werkzeuge, rueck, vor, vorlage, raster, fang, gross };
  return [
    ...werkzeuge.slice(0, 4), vorlage, trenner(),
    ...werkzeuge.slice(4), trenner(),
    rueck, vor, trenner(),
    el('label.zf-wahl', { title: 'Raster' }, ['Raster ', raster]),
    el('label.zf-wahl', { title: 'Fang' }, [fang, ' Fang']),
    trenner(),
    alles, gross,
  ];
}

function leisteZeichnen(a) {
  const k = a.teile.knoepfe;
  for (const w of k.werkzeuge) w.classList.toggle('ist-an', w.dataset.werkzeug === a.werkzeug);
  k.vorlage.classList.toggle('ist-an', a.vorlageOffen);
  k.rueck.disabled = !a.rueck.length;
  k.vor.disabled = !a.vor.length;
  k.raster.value = String(a.raster);
  k.fang.checked = a.fang;
  k.gross.classList.toggle('ist-an', a.vollbild);
  k.gross.querySelector('.zf-text').textContent = a.vollbild ? 'Zurück' : 'Vollbild';
}

/**
 * Die Einstellungen des gewählten Werkzeugs -- womit das nächste Element
 * angelegt wird. Ein angelegtes Element ändert man danach in den
 * Koordinaten; was man dort ändert, gilt auch für das nächste.
 *
 * Neu gebaut wird die Zeile nur, wenn sich etwas an ihr geändert hat: sie
 * steht im bleibenden Fenster, und eine offene Auswahlliste soll nicht
 * zuklappen, weil nebenan eine Rechnung fertig wurde.
 */
function optionenZeichnen(a) {
  const ziel = a.teile.optionen;
  const art = ANLEGEN[a.werkzeug];
  const stoffe = zustand.projekt.materialien.map((m) => [m.kennung, m.art, m.name || m.sorte]);
  const schluessel = JSON.stringify([art, art ? a.vorgaben[art] : null, stoffe]);
  if (ziel.dataset.schluessel === schluessel) return;
  ziel.dataset.schluessel = schluessel;
  if (!art) {
    ziel.replaceChildren();
    ziel.hidden = true;
    return;
  }
  ziel.hidden = false;
  const v = a.vorgaben[art];
  const setzen = (feld, wert) => { v[feld] = wert; optionenZeichnen(a); zeichnen(a); };
  const materialwahl = (artName, feld, titel, mitLoch = false) => el('select', {
    title: titel, on: { change: (e) => setzen(feld, e.target.value) },
  }, [
    ...zustand.projekt.materialien.filter((m) => m.art === artName).map((m) => el('option', {
      value: m.kennung, text: m.name || m.sorte, selected: v[feld] === m.kennung,
    })),
    mitLoch ? el('option', { value: '', text: 'Aussparung', selected: !v[feld] }) : null,
  ]);
  const zahl = (feld, titel, { stufen, schritt = 1, min = 0 } = {}) => zahlfeld({
    wert: v[feld], stufen, schritt, min, titel, beiAenderung: (w) => setzen(feld, w),
  });
  const beschriftet = (beschriftung, eingabe, einheit = '') => el('label.zf-option', {}, [
    el('span', { text: beschriftung }), eingabe, einheit ? el('span.einheit', { text: einheit }) : null,
  ]);
  const haken = (feld, beschriftung) => el('label.zf-option', {}, [
    el('input', {
      type: 'checkbox', checked: !!v[feld], on: { change: (e) => setzen(feld, e.target.checked) },
    }), beschriftung,
  ]);
  const durchmesser = zustand.katalog?.durchmesser;
  const stahl = () => materialwahl('betonstahl', 'stahl', 'Betonstahl');

  const teile = {
    flaeche: () => [
      beschriftet('Material', materialwahl('beton', 'material',
        'Material des nächsten Polygons; ohne Material ist es eine Aussparung', true)),
    ],
    stab: () => [
      beschriftet('⌀', zahl('durchmesser', 'Stabdurchmesser', { stufen: durchmesser }), 'mm'),
      stahl(),
    ],
    linie: () => {
      const arten = zustand.katalog?.querschnittsanalyse?.linienarten || [];
      const art2 = v.art;
      return [
        el('select', {
          title: 'Fläche: verschmiert; Anzahl: n Stäbe; Teilung: Abstand, gerundet auf einen, der aufgeht',
          on: { change: (e) => setzen('art', e.target.value) },
        }, arten.map((x) => el('option', {
          value: x.wert, text: x.beschriftung, selected: x.wert === art2,
        }))),
        art2 === 'flaeche'
          ? beschriftet('As', zahl('flaeche', 'Stahlfläche der ganzen Linie', { schritt: 100 }), 'mm²')
          : null,
        art2 === 'anzahl' ? beschriftet('n', zahl('anzahl', 'Anzahl Stäbe', { min: 1 })) : null,
        art2 === 'teilung'
          ? beschriftet('s', zahl('teilung', 'Gewünschte Teilung', { schritt: 25, min: 1 }), 'mm')
          : null,
        art2 !== 'flaeche'
          ? beschriftet('⌀', zahl('durchmesser', 'Stabdurchmesser', { stufen: durchmesser }), 'mm')
          : null,
        art2 !== 'flaeche' ? haken('starteisen', 'Starteisen') : null,
        art2 !== 'flaeche' ? haken('endeisen', 'Endeisen') : null,
        stahl(),
      ];
    },
    wand: () => [
      beschriftet('b_w', zahl('dicke', 'Dicke der Schubwand', { schritt: 10, min: 1 }), 'mm'),
      beschriftet('⌀', zahl('durchmesser', 'Bügeldurchmesser; 0: ohne Bügel', { stufen: durchmesser }), 'mm'),
      beschriftet('s', zahl('teilung', 'Bügelteilung in Längsrichtung', { schritt: 25, min: 1 }), 'mm'),
      beschriftet('Schnitte', el('select', {
        title: 'Wie viele Bügelschenkel die Wand kreuzen',
        on: { change: (e) => setzen('schnitte', Number(e.target.value)) },
      }, (zustand.katalog?.querschnittsanalyse?.schnitte || [1, 2, 3, 4, 5, 6, 7, 8]).map((n) => el('option', {
        value: n, text: String(n), selected: n === v.schnitte,
      })))),
      stahl(),
    ],
  };
  ziel.replaceChildren(el('span.zf-optionstitel', { text: 'Neu:' }), ...teile[art]().filter(Boolean));
}

// ===========================================================================
// Vorlagen
// ===========================================================================

/**
 * Querschnitte zum Anfangen. Jede Vorlage kennt ihre Masse und baut daraus
 * Polygone -- auf Wunsch mit Bewehrung und Schubwänden. Eingesetzt ersetzt
 * sie die ganze Zeichnung; «Rückgängig» holt die alte zurück.
 */
const VORLAGEN = {
  rechteck: {
    name: 'Rechteck',
    masse: [['b', 'Breite b', 300], ['h', 'Höhe h', 600]],
    bauen: ({ b, h }, r, neu) => ({
      flaechen: [neu.flaeche([[0, 0], [b, 0], [b, h], [0, h]])],
      stablinien: [
        neu.linie([r, r], [b - r, r], { art: 'anzahl', anzahl: 3, durchmesser: 20 }),
        neu.linie([r, h - r], [b - r, h - r], { art: 'anzahl', anzahl: 2, durchmesser: 12 }),
      ],
      schubwaende: [neu.wand([b / 2, r], [b / 2, h - r], b)],
    }),
  },
  tbalken: {
    name: 'T-Balken',
    masse: [['b', 'Flanschbreite b', 1200], ['h', 'Höhe h', 700],
      ['b_w', 'Stegbreite b_w', 300], ['h_f', 'Flanschdicke h_f', 200]],
    bauen: ({
      b, h, b_w: bw, h_f: hf,
    }, r, neu) => {
      const y0 = (b - bw) / 2;
      return {
        flaechen: [neu.flaeche([[y0, 0], [y0 + bw, 0], [y0 + bw, h - hf], [b, h - hf], [b, h],
          [0, h], [0, h - hf], [y0, h - hf]])],
        stablinien: [
          neu.linie([y0 + r, r], [y0 + bw - r, r], { art: 'anzahl', anzahl: 3, durchmesser: 20 }),
          neu.linie([r, h - r], [b - r, h - r], { art: 'teilung', teilung: 150, durchmesser: 12 }),
        ],
        schubwaende: [neu.wand([b / 2, r], [b / 2, h - hf / 2], bw)],
      };
    },
  },
  hohlkasten: {
    name: 'Hohlkasten',
    masse: [['b', 'Breite b', 1200], ['h', 'Höhe h', 800], ['t', 'Wanddicke t', 200]],
    bauen: ({ b, h, t }, r, neu) => {
      const m = t / 2;
      return {
        flaechen: [
          neu.flaeche([[0, 0], [b, 0], [b, h], [0, h]]),
          neu.flaeche([[t, t], [b - t, t], [b - t, h - t], [t, h - t]], ''),
        ],
        stablinien: [
          neu.linie([r, r], [b - r, r], { art: 'teilung', teilung: 150, durchmesser: 16 }),
          neu.linie([r, h - r], [b - r, h - r], { art: 'teilung', teilung: 150, durchmesser: 16 }),
        ],
        // Die Wände auf den Mittellinien, Ende an Ende: sie umschliessen die
        // Zelle, und die Torsion läuft um sie herum.
        schubwaende: [
          neu.wand([m, m], [b - m, m], t), neu.wand([b - m, m], [b - m, h - m], t),
          neu.wand([b - m, h - m], [m, h - m], t), neu.wand([m, h - m], [m, m], t),
        ],
      };
    },
  },
  kreis: {
    name: 'Kreis',
    masse: [['D', 'Durchmesser D', 500]],
    bauen: ({ D }, r, neu) => ({
      flaechen: [neu.flaeche(kreispunkte([D / 2, D / 2], D / 2))],
      staebe: Array.from({ length: 8 }, (_, k) => neu.stab([
        D / 2 + (D / 2 - r) * Math.cos((k * Math.PI) / 4),
        D / 2 + (D / 2 - r) * Math.sin((k * Math.PI) / 4),
      ])),
    }),
  },
};

/** Ein Kreis als Vieleck. Die Ecken liegen auf dem Kreis; was das an Fläche kostet, sagt der Kern. */
function kreispunkte(mitte, r) {
  return Array.from({ length: KREISECKEN }, (_, k) => {
    const w = (2 * Math.PI * k) / KREISECKEN;
    return [Number((mitte[0] + r * Math.cos(w)).toFixed(3)), Number((mitte[1] + r * Math.sin(w)).toFixed(3))];
  });
}

/** Elemente nach den Vorgaben der Ansicht -- die Vorlagen und die Werkzeuge bauen damit. */
function bauhelfer(a) {
  const v = a.vorgaben;
  return {
    flaeche: (punkte, material = v.flaeche.material) => ({ ...structuredClone(v.flaeche), punkte, material }),
    stab: ([y, z]) => ({ ...structuredClone(v.stab), y, z }),
    linie: (von, bis, felder = {}) => ({ ...structuredClone(v.linie), von, bis, ...felder }),
    wand: (von, bis, dicke = v.wand.dicke) => ({ ...structuredClone(v.wand), von, bis, dicke }),
  };
}

function vorlageZeichnen(a) {
  const ziel = a.teile.vorlage;
  if (!a.vorlageOffen) {
    ziel.hidden = true;
    ziel.replaceChildren();
    return;
  }
  ziel.hidden = false;
  a.vorlagewahl = a.vorlagewahl || { art: 'rechteck', werte: {}, randabstand: 50, bewehrung: true };
  const w = a.vorlagewahl;
  const vorlage = VORLAGEN[w.art];
  const zahl = (wert, setzen) => el('input', {
    type: 'number', value: wert, min: 1, step: 'any',
    on: { change: (e) => { if (Number(e.target.value) > 0) setzen(Number(e.target.value)); } },
  });
  const zeile = (beschriftung, eingabe) => el('label.zf-vorlagezeile', {}, [
    el('span', { text: beschriftung }), eingabe, el('span.einheit', { text: 'mm' }),
  ]);
  ziel.replaceChildren(
    el('div.zf-vorlagekopf', {}, [
      el('b', { text: 'Vorlage' }),
      el('select', {
        on: { change: (e) => { w.art = e.target.value; vorlageZeichnen(a); } },
      }, Object.entries(VORLAGEN).map(([schluessel, v]) => el('option', {
        value: schluessel, text: v.name, selected: schluessel === w.art,
      }))),
    ]),
    ...vorlage.masse.map(([schluessel, beschriftung, vorgabe]) => zeile(beschriftung,
      zahl(w.werte[schluessel] ?? vorgabe, (v) => { w.werte[schluessel] = v; }))),
    el('label.zf-vorlagehaken', {}, [
      el('input', {
        type: 'checkbox', checked: w.bewehrung,
        on: { change: (e) => { w.bewehrung = e.target.checked; vorlageZeichnen(a); } },
      }),
      ` mit Bewehrung${w.art === 'kreis' ? '' : ' und Schubwänden'}`,
    ]),
    w.bewehrung ? zeile('Achsabstand der Stäbe', zahl(w.randabstand, (v) => { w.randabstand = v; })) : null,
    el('p.zf-vorlagehinweis', { text: 'Ersetzt die ganze Zeichnung. Rückgängig: Strg+Z.' }),
    el('div.zf-vorlageknoepfe', {}, [
      el('button.knopf.knopf-klein', {
        type: 'button', text: 'Abbrechen',
        on: { click: () => { a.vorlageOffen = false; vorlageZeichnen(a); zeichnen(a); } },
      }),
      el('button.knopf.knopf-klein.knopf-haupt', {
        type: 'button', text: 'Einsetzen', on: { click: () => vorlageEinsetzen(a) },
      }),
    ]),
  );
}

function vorlageEinsetzen(a) {
  const w = a.vorlagewahl;
  const vorlage = VORLAGEN[w.art];
  const masse = Object.fromEntries(vorlage.masse.map(([k, , v]) => [k, w.werte[k] ?? v]));
  const teile = vorlage.bauen(masse, w.randabstand, bauhelfer(a));
  a.vorlageOffen = false;
  a.auswahl = null;
  a.entwurf = null;
  vorlageZeichnen(a);
  zeichnungAendern(a.kennung, (x) => {
    x.flaechen = teile.flaechen;
    x.staebe = w.bewehrung ? teile.staebe || [] : [];
    x.stablinien = w.bewehrung ? teile.stablinien || [] : [];
    x.schubwaende = w.bewehrung ? teile.schubwaende || [] : [];
  });
  allesZeigen(a);
}

// ===========================================================================
// Bedienen
// ===========================================================================

/** Wo ein Zeigerereignis im Bild liegt, px. */
function bildlage(a, e) {
  const r = a.teile.bild.getBoundingClientRect();
  return [e.clientX - r.left, e.clientY - r.top];
}

/**
 * Was unter dem Zeiger liegt: zuerst die Griffe des gewählten Elements,
 * dann Stäbe, Linien, Wandachsen und zuletzt Polygone, das innerste zuerst.
 */
function treffer(a, bild) {
  const analyse = eintragVon(a.kennung);
  const daten = zeichenDaten(a, analyse);
  const welt = nachWelt(a, bild);
  const weit = NAEHE / a.massstab;

  if (a.auswahl) {
    for (const h of griffe(a, daten)) {
      if (abstand(nachBild(a, h.p), bild) <= NAEHE) return { ...a.auswahl, ...h };
    }
  }
  for (let i = daten.staebe.length - 1; i >= 0; i -= 1) {
    const s = daten.staebe[i];
    if (abstand(welt, [s.y, s.z]) <= Math.max(weit, s.durchmesser / 2)) {
      return { art: 'stab', index: i, griff: 'ganz' };
    }
  }
  for (let i = daten.stablinien.length - 1; i >= 0; i -= 1) {
    const l = daten.stablinien[i];
    if (abstand(welt, aufStrecke(welt, l.von, l.bis).q) <= Math.max(weit, l.durchmesser / 2)) {
      return { art: 'linie', index: i, griff: 'ganz' };
    }
  }
  for (let i = daten.schubwaende.length - 1; i >= 0; i -= 1) {
    const w = daten.schubwaende[i];
    if (abstand(welt, aufStrecke(welt, w.von, w.bis).q) <= weit) {
      return { art: 'wand', index: i, griff: 'ganz' };
    }
  }
  // Das innerste zuerst: die Reihenfolge des Zeichnens, umgekehrt.
  for (const i of reihenfolge(a, daten).reverse()) {
    if (innen(welt, daten.flaechen[i].punkte)) return { art: 'flaeche', index: i, griff: 'ganz' };
  }
  return null;
}

/** Das Element, verschoben um d -- für das Ziehen eines ganzen Elements. */
function verschoben(art, element, [dy, dz]) {
  const neu = structuredClone(element);
  const schieben = (p) => [p[0] + dy, p[1] + dz];
  if (art === 'flaeche') neu.punkte = neu.punkte.map(schieben);
  else if (art === 'stab') { neu.y += dy; neu.z += dz; } else {
    neu.von = schieben(neu.von);
    neu.bis = schieben(neu.bis);
  }
  return neu;
}

/** Die Vorschau eines Ziehens: das Element, wie es nach dem Loslassen wäre. */
function ziehVorschau(a, ziel, bild, e) {
  const analyse = eintragVon(a.kennung);
  const element = analyse[LISTEN[ziel.art]][ziel.index];
  if (!element) return null;
  const frei = e.altKey;
  if (ziel.griff === 'ganz') {
    const start = nachWelt(a, a.druck.start);
    const jetzt = nachWelt(a, bild);
    let d = [jetzt[0] - start[0], jetzt[1] - start[1]];
    if (a.fang && !frei) d = d.map((v) => Math.round(v / a.raster) * a.raster);
    return verschoben(ziel.art, element, d);
  }
  const neu = structuredClone(element);
  if (ziel.griff === 'ecke' || ziel.griff === 'mitte') {
    const k = ziel.griff === 'ecke' ? ziel.ecke : ziel.ecke + 1;
    const n = neu.punkte.length;
    const nachbar = neu.punkte[ziel.griff === 'ecke' ? (k + n - 1) % n : ziel.ecke];
    const f = fangen(a, bild, {
      ohne: { art: ziel.art, index: ziel.index, ecke: ziel.griff === 'ecke' ? k : -1 },
      bezug: nachbar, gerade: e.shiftKey, frei,
    });
    a.zeiger = { bild, fang: f };
    if (ziel.griff === 'mitte') neu.punkte.splice(k, 0, f.p);
    else neu.punkte[k] = f.p;
    return neu;
  }
  // Ein Ende einer Linie oder Wand.
  const anderes = ziel.griff === 'von' ? neu.bis : neu.von;
  const f = fangen(a, bild, {
    ohne: { art: ziel.art, index: ziel.index }, bezug: anderes, gerade: e.shiftKey, frei,
  });
  a.zeiger = { bild, fang: f };
  neu[ziel.griff] = f.p;
  return neu;
}

function anfuegen(a, art, element) {
  const analyse = eintragVon(a.kennung);
  a.auswahl = { art, index: analyse[LISTEN[art]].length };
  zeichnungAendern(a.kennung, (x) => { x[LISTEN[art]].push(element); });
}

function polygonSchliessen(a) {
  const e = a.entwurf;
  if (e?.art !== 'polygon' || e.punkte.length < 3) return;
  a.entwurf = null;
  anfuegen(a, 'flaeche', bauhelfer(a).flaeche(e.punkte));
}

/** Ein Klick -- je nach Werkzeug ein Punkt, ein Element oder eine Auswahl. */
function klicken(a, bild, e) {
  const neu = bauhelfer(a);
  const bezug = a.entwurf?.punkte?.at(-1) || a.entwurf?.von || a.entwurf?.ecke || a.entwurf?.mitte;
  const f = fangen(a, bild, { bezug, gerade: e.shiftKey, frei: e.altKey });
  const p = f.p;
  const ent = a.entwurf;

  switch (a.werkzeug) {
    case 'polygon': {
      if (!ent) {
        a.entwurf = { art: 'polygon', punkte: [p] };
      } else {
        const erster = nachBild(a, ent.punkte[0]);
        const letzter = nachBild(a, ent.punkte.at(-1));
        // Auf den Startpunkt geklickt oder doppelt geklickt: zu.
        if (ent.punkte.length >= 3
            && (abstand(erster, bild) <= NAEHE || abstand(letzter, nachBild(a, p)) <= 3)) {
          polygonSchliessen(a);
          return;
        }
        if (abstand(letzter, nachBild(a, p)) > 3) ent.punkte.push(p);
      }
      break;
    }
    case 'rechteck': {
      if (!ent) a.entwurf = { art: 'rechteck', ecke: p };
      else if (Math.abs(p[0] - ent.ecke[0]) > 1e-9 && Math.abs(p[1] - ent.ecke[1]) > 1e-9) {
        const q = ent.ecke;
        a.entwurf = null;
        anfuegen(a, 'flaeche', neu.flaeche([q, [p[0], q[1]], p, [q[0], p[1]]]));
        return;
      }
      break;
    }
    case 'kreis': {
      if (!ent) a.entwurf = { art: 'kreis', mitte: p };
      else if (abstand(ent.mitte, p) > 1e-9) {
        a.entwurf = null;
        anfuegen(a, 'flaeche', neu.flaeche(kreispunkte(ent.mitte, abstand(ent.mitte, p))));
        return;
      }
      break;
    }
    case 'stab':
      anfuegen(a, 'stab', neu.stab(p));
      return;
    case 'linie':
    case 'wand': {
      if (!ent) a.entwurf = { art: a.werkzeug, von: p };
      else if (abstand(ent.von, p) > 1e-9) {
        a.entwurf = null;
        anfuegen(a, a.werkzeug, a.werkzeug === 'linie' ? neu.linie(ent.von, p) : neu.wand(ent.von, p));
        return;
      }
      break;
    }
    default:
      break;
  }
  a.zeiger = { bild, fang: f };
  zeichnen(a);
  // Die Koordinaten daneben zeigen den Entwurf -- auch sie sollen den Punkt sehen.
  aendern({}, 'zeichnung');
}

function auswahlLoeschen(a) {
  const w = a.auswahl;
  if (!w) return;
  const analyse = eintragVon(a.kennung);
  const element = analyse[LISTEN[w.art]][w.index];
  if (!element) return;
  // Eine gewählte Ecke geht allein -- solange ein Polygon übrig bleibt.
  if (w.art === 'flaeche' && w.ecke !== undefined && element.punkte.length > 3) {
    a.auswahl = { art: w.art, index: w.index };
    zeichnungAendern(a.kennung, (x) => { x.flaechen[w.index].punkte.splice(w.ecke, 1); });
    return;
  }
  a.auswahl = null;
  zeichnungAendern(a.kennung, (x) => { x[LISTEN[w.art]].splice(w.index, 1); });
}

function druecken(a, e) {
  aktive = a;
  const bild = bildlage(a, e);
  if (e.pointerType === 'touch') {
    a.finger.set(e.pointerId, bild);
    if (a.finger.size === 2) {
      // Zwei Finger: kneifen und schieben. Was der erste begonnen hat, gilt nicht.
      const [p, q] = [...a.finger.values()];
      a.kneifen = {
        abstand: abstand(p, q) || 1, mitte: [(p[0] + q[0]) / 2, (p[1] + q[1]) / 2],
        massstab: a.massstab, ursprung: [...a.ursprung],
      };
      a.druck = null;
      a.ziehen = null;
      return;
    }
    if (a.finger.size > 2) return;
  }
  if (a.druck || !a.massstab) return;
  const schieben = e.button === 1 || (e.button === 0 && a.leertaste);
  if (e.button !== 0 && !schieben) return;
  // Die mittlere Taste schiebt hier die Ansicht und soll nicht den Bildlauf
  // des Browsers starten. Sonst kein preventDefault: ein Eingabefeld der
  // Koordinaten soll seinen Fokus abgeben und seine Zahl übernehmen.
  if (e.button === 1) e.preventDefault();
  a.druck = {
    id: e.pointerId, start: bild, ursprung: [...a.ursprung], schieben, bewegt: false, ziel: null,
  };
  if (!schieben && a.werkzeug === 'waehlen') {
    const ziel = treffer(a, bild);
    a.druck.ziel = ziel;
    if (ziel && !(istGewaehlt(a, ziel.art, ziel.index) && ziel.griff !== 'ganz')) {
      const vorher = a.auswahl;
      a.auswahl = { art: ziel.art, index: ziel.index };
      a.druck.neueAuswahl = !vorher || vorher.art !== ziel.art || vorher.index !== ziel.index;
      zeichnen(a);
    }
  }
}

function bewegen(a, e) {
  const bild = bildlage(a, e);
  if (a.kneifen && a.finger.has(e.pointerId)) {
    a.finger.set(e.pointerId, bild);
    if (a.finger.size < 2) return;
    const [p, q] = [...a.finger.values()];
    const k = a.kneifen;
    const mitte = [(p[0] + q[0]) / 2, (p[1] + q[1]) / 2];
    a.massstab = k.massstab;
    a.ursprung = [k.ursprung[0] + mitte[0] - k.mitte[0], k.ursprung[1] + mitte[1] - k.mitte[1]];
    zoomen(a, (abstand(p, q) || 1) / k.abstand, mitte);
    zeichnen(a);
    return;
  }
  const d = a.druck;
  if (!d) {
    // Nur schweben: Lage und Fang zeigen.
    const bezug = a.entwurf?.punkte?.at(-1) || a.entwurf?.von || a.entwurf?.ecke || a.entwurf?.mitte;
    a.zeiger = { bild, fang: fangen(a, bild, { bezug, gerade: e.shiftKey, frei: e.altKey }) };
    zeichnen(a);
    return;
  }
  if (e.pointerId !== d.id) return;
  if (!d.bewegt && abstand(bild, d.start) < ZITTERN) return;
  d.bewegt = true;
  if (d.schieben || !d.ziel) {
    a.ursprung = [d.ursprung[0] + bild[0] - d.start[0], d.ursprung[1] + bild[1] - d.start[1]];
    zeichnen(a);
    return;
  }
  const element = ziehVorschau(a, d.ziel, bild, e);
  if (element) a.ziehen = { art: d.ziel.art, index: d.ziel.index, element };
  zeichnen(a);
}

function loslassen(a, e) {
  if (e.pointerType === 'touch') {
    a.finger.delete(e.pointerId);
    if (a.kneifen) {
      if (!a.finger.size) a.kneifen = null;
      return;
    }
  }
  const d = a.druck;
  if (!d || e.pointerId !== d.id) return;
  a.druck = null;
  const bild = bildlage(a, e);
  if (d.bewegt) {
    if (a.ziehen) {
      const { art, index, element } = a.ziehen;
      a.ziehen = null;
      if (d.ziel.griff === 'mitte') a.auswahl = { art, index, ecke: d.ziel.ecke + 1 };
      zeichnungAendern(a.kennung, (x) => { x[LISTEN[art]][index] = element; });
    } else {
      zeichnen(a);
    }
    return;
  }
  if (d.schieben) return;
  if (a.werkzeug === 'waehlen') {
    const z = d.ziel;
    if (!z) a.auswahl = null;
    else if (z.griff === 'ecke') a.auswahl = { art: z.art, index: z.index, ecke: z.ecke };
    zeichnen(a);
    aendern({}, 'zeichnung');
    return;
  }
  klicken(a, bild, e);
}

function rad(a, e) {
  // Das Mausrad gehört der Tafel, bis man ins Fenster geklickt hat -- sonst
  // bliebe man beim Blättern an der Zeichnung hängen. Mit Strg zoomt es immer.
  if (aktive !== a && !e.ctrlKey && !a.vollbild) {
    kurzMelden(a, 'Zum Zoomen ins Fenster klicken -- oder Strg + Mausrad.');
    return;
  }
  e.preventDefault();
  const zeilen = e.deltaMode === 1 ? 16 : 1;
  zoomen(a, Math.exp(-e.deltaY * zeilen * 0.0015), bildlage(a, e));
  zeichnen(a);
}

function taste(e) {
  const a = aktive;
  if (!a || !a.knoten?.isConnected) return;
  if (e.target.closest?.('input, select, textarea, [contenteditable]')) return;
  if ((e.key === 'Enter' || e.key === ' ') && e.target.closest?.('button')) return;
  const strg = e.ctrlKey || e.metaKey;
  const zeichen = e.key.length === 1 ? e.key.toLowerCase() : e.key;

  if (strg && (zeichen === 'z' || zeichen === 'y')) {
    e.preventDefault();
    if (zeichen === 'y' || e.shiftKey) vorwaerts(a); else zurueck(a);
    return;
  }
  if (strg || e.altKey) return;

  switch (zeichen) {
    case 'Escape':
      if (a.entwurf) {
        a.entwurf = null;
        aendern({}, 'zeichnung');
      } else if (a.vorlageOffen) { a.vorlageOffen = false; vorlageZeichnen(a); } else if (a.auswahl) {
        a.auswahl = null;
        aendern({}, 'zeichnung');
      } else if (a.vollbild) {
        vollbildSetzen(a, false);
      } else if (a.werkzeug !== 'waehlen') { werkzeugWaehlen(a, 'waehlen'); return; }
      break;
    case 'Enter':
      polygonSchliessen(a);
      break;
    case 'Backspace':
      if (a.entwurf?.art === 'polygon') {
        a.entwurf.punkte.pop();
        if (!a.entwurf.punkte.length) a.entwurf = null;
        aendern({}, 'zeichnung');
        break;
      }
      auswahlLoeschen(a);
      break;
    case 'Delete':
      auswahlLoeschen(a);
      break;
    case ' ':
      a.leertaste = true;
      break;
    case 'f':
      allesZeigen(a);
      break;
    default: {
      const w = WERKZEUGE.find((x) => x.taste === zeichen);
      if (!w) return;
      werkzeugWaehlen(a, w.name);
      e.preventDefault();
      return;
    }
  }
  e.preventDefault();
  zeichnen(a);
}

document.addEventListener('keydown', taste);
document.addEventListener('keyup', (e) => {
  if (e.key === ' ' && aktive) aktive.leertaste = false;
});
// Ein Druck ausserhalb des Fensters: Tasten gehören wieder der Seite.
document.addEventListener('pointerdown', (e) => {
  if (aktive && !aktive.knoten?.contains(e.target)) aktive = null;
}, true);

// ===========================================================================
// Aufbau
// ===========================================================================

function groesseMessen(a) {
  const { clientWidth: b, clientHeight: h } = a.teile.flaeche;
  if (!b || !h || (b === a.breite && h === a.hoehe)) return;
  if (a.massstab && a.breite) {
    // Die Mitte bleibt, wo sie war.
    a.ursprung = [a.ursprung[0] + (b - a.breite) / 2, a.ursprung[1] + (h - a.hoehe) / 2];
  }
  a.breite = b;
  a.hoehe = h;
  a.teile.bild.setAttribute('viewBox', `0 0 ${b} ${h}`);
  if (!a.massstab || a.einpassen) {
    a.einpassen = false;
    allesZeigen(a);
  } else {
    zeichnen(a);
  }
}

function brettBauen(a) {
  const bild = svgEl('svg', { class: 'zf-bild', role: 'img', 'aria-label': 'Zeichnung des Querschnitts' });
  const vorlage = el('div.zf-vorlage', { hidden: true });
  const flaeche = el('div.zf-flaeche', {}, [bild, vorlage]);
  const optionen = el('div.zf-optionen', { hidden: true });
  const lage = el('span.zf-lage');
  const hinweisknoten = el('span.zf-hinweis');
  a.teile = {
    bild, flaeche, vorlage, optionen, lage, hinweis: hinweisknoten,
  };
  const leiste = el('div.zf-leiste', {}, leisteBauen(a));
  a.knoten = el('div.zeichenfenster', {}, [
    leiste, optionen, flaeche, el('div.zf-status', {}, [lage, hinweisknoten]),
  ]);
  a.knoten.addEventListener('pointerdown', () => { aktive = a; });

  bild.addEventListener('pointerdown', (e) => druecken(a, e));
  // Bewegen und Loslassen am Fenster des Browsers: das Bild wird bei jedem
  // Neubau der Tafel kurz ab- und wieder eingehängt, und ein Ziehen soll
  // das überstehen.
  window.addEventListener('pointermove', (e) => {
    if (a.druck || a.kneifen || e.target === bild || bild.contains(e.target)) bewegen(a, e);
  });
  window.addEventListener('pointerup', (e) => loslassen(a, e));
  window.addEventListener('pointercancel', (e) => {
    a.finger.delete(e.pointerId);
    if (!a.finger.size) a.kneifen = null;
    if (a.druck?.id === e.pointerId) { a.druck = null; a.ziehen = null; zeichnen(a); }
  });
  bild.addEventListener('pointerleave', () => {
    if (!a.druck) { a.zeiger = null; zeichnen(a); }
  });
  bild.addEventListener('wheel', (e) => rad(a, e), { passive: false });
  bild.addEventListener('contextmenu', (e) => e.preventDefault());
  // Festgehalten an der Ansicht: ein Beobachter, auf den nichts mehr zeigt,
  // darf der Browser wegräumen -- und dann misst niemand mehr.
  a.beobachter = new ResizeObserver(() => groesseMessen(a));
  a.beobachter.observe(flaeche);
}

/** Die Auswahl zeigt auf ein Element, das es nicht mehr gibt: weg damit. */
function auswahlPruefen(a, analyse) {
  const w = a.auswahl;
  if (!w) return;
  const element = analyse[LISTEN[w.art]]?.[w.index];
  if (!element) a.auswahl = null;
  else if (w.ecke !== undefined && w.ecke >= (element.punkte?.length ?? 0)) {
    a.auswahl = { art: w.art, index: w.index };
  }
}

/**
 * Das Zeichenfenster einer Analyse, samt dem, was daneben steht -- im
 * Vollbild rechts, sonst darunter. Die Tafel ruft das bei jedem Neubau;
 * das Fenster selbst entsteht nur einmal.
 */
export function zeichenbereich(analyse, seite = []) {
  const a = ansichtVon(analyse.kennung);
  if (!a.vorgaben) vorgabenSetzen(a);
  if (!a.knoten) brettBauen(a);
  auswahlPruefen(a, analyse);
  optionenZeichnen(a);
  geometrieHolen(a, analyse);
  zeichnen(a);
  return el('div.zeichenbereich', { class: a.vollbild ? 'ist-vollbild' : '' }, [
    a.knoten,
    el('div.zf-seite', {}, seite),
  ]);
}

// ===========================================================================
// Für das Koordinatenfenster
// ===========================================================================

/** Ein neues Element nach den Vorgaben, an der angegebenen Lage -- danach gewählt. */
export function anlegen(kennung, art, lage) {
  const a = ansichtVon(kennung);
  const neu = bauhelfer(a);
  const element = {
    flaeche: () => neu.flaeche(lage.punkte),
    stab: () => neu.stab(lage.p),
    linie: () => neu.linie(lage.von, lage.bis),
    wand: () => neu.wand(lage.von, lage.bis),
  }[art]();
  anfuegen(a, art, element);
}

/** Der Entwurf eines Polygons, von den Koordinaten aus geändert. */
export function entwurfSetzen(kennung, punkte) {
  const a = ansichtVon(kennung);
  a.entwurf = punkte.length ? { art: 'polygon', punkte } : null;
  zeichnen(a);
  aendern({}, 'zeichnung');
}

export function entwurfSchliessen(kennung) {
  polygonSchliessen(ansichtVon(kennung));
}

/**
 * Merkt sich eine Eigenschaft für das nächste neue Element derselben Art:
 * wer einen Stab auf ⌀ 20 stellt, setzt den nächsten auch mit ⌀ 20.
 */
export function vorgabeMerken(kennung, art, feld, wert) {
  const a = ansichtVon(kennung);
  if (!a.vorgaben?.[art]) return;
  a.vorgaben[art][feld] = wert;
  optionenZeichnen(a);
}

/** Die Ecken eines Rechtecks und eines Kreises -- wie die Werkzeuge sie anlegen. */
export function rechteckpunkte([y, z], b, h) {
  return [[y, z], [y + b, z], [y + b, z + h], [y, z + h]];
}
export { kreispunkte };

/** Die Meldungen des Kerns zur Zeichnung -- ein Klick wählt das Element. */
export function meldungenBlock(analyse) {
  const a = ansichtVon(analyse.kennung);
  const g = passendeGeometrie(a, analyse);
  if (!g?.meldungen?.length) return null;
  return el('div.zf-meldungen', {}, g.meldungen.map((m) => {
    const ziel = elementAusName(m.elemente[0]);
    return el('button.zf-meldung', {
      type: 'button', text: m.text, disabled: !ziel,
      title: ziel ? 'Element wählen' : '',
      on: {
        click: () => {
          if (!ziel) return;
          a.werkzeug = 'waehlen';
          waehlen(analyse.kennung, ziel);
        },
      },
    });
  }));
}
