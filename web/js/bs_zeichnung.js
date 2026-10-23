/**
 * bs_zeichnung.js -- das Zeichenfenster eines Balkensystems: der Adapter.
 *
 * Gezeichnet werden Knoten und Linien, in Metern, x nach rechts und z nach
 * oben. Eine Linie ist ein Stab, sobald sie «Stab» ist und Querschnitt und
 * Material hat; daneben kann sie ein Linienlager sein, quer und längs. Lager
 * und Knotenlasten sind eigene Einträge an einem Knoten -- so überstehen sie
 * das Zusammenführen von Knoten --, gewählt wird aber der Knoten: das
 * schwebende Fenster zeigt an ihm sein Lager und die Lasten des gewählten
 * Lastfalls. Die Lasten auf einem Stab stehen an seiner Linie und gehen mit
 * ihr, wenn sie kopiert oder gelöscht wird.
 *
 * VERBUNDEN:
 * Ein Rahmen hängt an seinen Knoten (`verbunden` im Zeichenfenster): ein
 * Klick an einem Knoten wählt den Knoten, ein verschobener Stab nimmt seine
 * Knoten mit, und die Stäbe daneben bleiben angeschlossen.
 *
 * WAS HIER GERECHNET WIRD -- UND WAS NICHT:
 * Nichts, was in die Rechnung geht. Teilen und Umkehren schickt die Linie an
 * den Kern (Anfrage `balkensystem_bearbeiten`): dabei entstehen Lastwerte --
 * der Wert einer Trapezlast am Schnitt, gespiegelte Stellen. Die Meldungen,
 * die Knoten ohne Drehsteifigkeit und was sich bewegt, wenn das System
 * beweglich ist, kommen vom Kern (Anfrage `balkensystem_verlauf`) und gelten
 * nur, solange die Zeichnung dieselbe ist, nach der gefragt wurde. Gezeichnet
 * wird hier -- auch die Länge eines Lastpfeils, die nur dem Auge dient.
 */

import { api } from './api.js';
import { wahlBlock, wahlSchalter } from './bausteine.js';
import { nachBild, zahlText } from './cad_ansicht.js';
import { imSpiel } from './cad_auswahl.js';
import { cadBereich, cadFenster, cadVergessen, cadWaehlen } from './cad_fenster.js';
import { abstand, auswahlTeil } from './cad_modell.js';
import {
  GROESSE, faserSymbol, gelenkSymbol, imBild, kraftpfeil, lagerSymbol, linienlagerSymbol,
  momentSymbol, streckenlast, streckenmoment, unbestimmtSymbol,
} from './bs_symbole.js';
import {
  auswahl, el, melden, svgEl, zahlfeld,
} from './dom.js';
import { aendern, ausVorlage, projektAendern, zustand } from './zustand.js';

/**
 * Die Arten des Systems. Gewählt werden nur Linien und Knoten: ein Lager und
 * eine Knotenlast gehören ihrem Knoten (`waehlbar`).
 */
const ARTEN = [
  { liste: 'linien', form: 'linie', vorsilbe: 'L', rang: 0 },
  { liste: 'lager', form: 'punkt', vorsilbe: 'A', rang: 1 },
  { liste: 'knotenlasten', form: 'punkt', vorsilbe: 'P', rang: 2 },
];

/** Meter statt Millimeter, zwei Werkzeuge, ein Rahmen hängt an seinen Knoten. */
const EINSTELLUNG = {
  werkzeuge: [
    { name: 'linie', text: 'Linie', zeichen: 'cad-linie', taste: 'l', form: 'linie',
      titel: 'Linie -- ein Stab, wenn im Fenster «Stab» an ist' },
    { name: 'knoten', text: 'Knoten', zeichen: 'cad-knoten', taste: 'k', form: 'knoten' },
  ],
  einheit: 'm',
  raster: { stufen: [0.05, 0.1, 0.25, 0.5, 1, 2], vorgabe: 0.5 },
  stellen: 3,
  massstab: [0.2, 20000],
  verbunden: true,
};

/** Was ein Lager je Richtung kann -- die Feder heisst an einer Linie Bettung. */
const HALT = [
  { wert: 'frei', beschriftung: 'frei' },
  { wert: 'fest', beschriftung: 'fest' },
  { wert: 'feder', beschriftung: 'Feder' },
];

export function eintragVon(kennung) {
  return zustand.projekt?.balkensysteme?.find((x) => x.kennung === kennung) || null;
}

/** Ändert das System -- der eine Weg, auf dem das Fenster ins Projekt schreibt. */
function schreiben(kennung, veraenderer) {
  projektAendern((p) => veraenderer(p.balkensysteme.find((x) => x.kennung === kennung)));
}

/** Was der Katalog zum Balkensystem weiss: Lastarten, Richtungen, Lagerarten, Einheiten. */
function katalog() {
  return zustand.katalog?.balkensystem || {
    lastarten: [], richtungen: [], knotenrichtungen: [], lagerarten: [], federeinheiten: {},
  };
}

function lastart(wert) {
  return katalog().lastarten.find((x) => x.wert === wert) || { beschriftung: wert, einheit: '' };
}

function richtungText(wert) {
  return katalog().richtungen.find((x) => x.wert === wert)?.beschriftung || wert;
}

// ===========================================================================
// Das Fenster eines Systems
// ===========================================================================

/** Das Zeichenfenster eines Systems, samt der Liste darunter. Die Tafel ruft das bei jedem Neubau. */
export function zeichenbereich(system, uebersichtBauen) {
  const a = fensterVon(system.kennung);
  const unten = el('div.qa-uebersicht-huelle');
  a.bs.uebersichtKnoten = unten;
  a.bs.uebersichtBauen = uebersichtBauen;
  const bereich = cadBereich(a, [unten]);
  uebersichtZeichnen(a);
  return bereich;
}

export function fensterVon(kennung) {
  const a = cadFenster(`bs:${kennung}`, () => adapter(kennung));
  a.bs = a.adapter.bs;
  return a;
}

/** Für ein neu angelegtes System: nichts von einem früheren mit derselben Kennung. */
export function fensterVergessen(kennung) {
  cadVergessen(`bs:${kennung}`);
}

/** Wählt Elemente von aussen -- aus der Liste oder einer Meldung. */
export function waehlen(kennung, kennungen) {
  cadWaehlen(fensterVon(kennung), kennungen);
}

/**
 * Der Lastfall, dessen Lasten das Fenster zeigt und bearbeitet -- der
 * gewählte, solange es ihn gibt, sonst der erste. Ansichtssache, nicht Teil
 * des Projekts.
 */
export function aktiverLastfall(kennung) {
  const a = fensterVon(kennung);
  const z = eintragVon(kennung);
  const faelle = z?.lastfaelle || [];
  if (faelle.some((lf) => lf.kennung === a.bs.lastfall)) return a.bs.lastfall;
  return faelle[0]?.kennung || null;
}

export function lastfallWaehlen(kennung, lastfall) {
  const a = fensterVon(kennung);
  a.bs.lastfall = lastfall;
  a.neuZeichnen();
  aendern({}, 'zeichnung');
}

/** Die Antwort des Kerns -- nur, wenn sie zur Zeichnung passt, die gerade zu sehen ist. */
export function passendeUebersicht(a) {
  const u = a.bs.uebersicht;
  return u && u.abdruck === abdruck(eintragVon(a.bs.kennung)) ? u : null;
}

/** Das System und welche Materialien es gibt: davon hängt die Antwort des Kerns ab. */
function abdruck(system) {
  if (!system) return '';
  const stoffe = zustand.projekt.materialien.map((m) => [m.kennung, m.art]);
  return JSON.stringify([system, stoffe]);
}

function uebersichtZeichnen(a) {
  const ziel = a.bs.uebersichtKnoten;
  if (ziel && a.bs.uebersichtBauen) ziel.replaceChildren(...a.bs.uebersichtBauen(a));
}

/** Markiert in der Liste, was im Fenster gewählt ist -- ohne sie neu zu bauen. */
function auswahlMarkieren(a) {
  const spiel = imSpiel(a);
  for (const z of a.bs.uebersichtKnoten?.querySelectorAll('[data-kennung]') || []) {
    z.classList.toggle('ist-gewaehlt', spiel.has(z.dataset.kennung));
  }
}

// ===========================================================================
// Der Adapter
// ===========================================================================

function vorgabenNeu(system) {
  const beton = zustand.projekt.materialien.find((m) => m.art === 'beton');
  return {
    linie: {
      stab: true,
      querschnitt: system?.querschnitte?.[0]?.kennung || '',
      material: beton?.kennung || '',
    },
  };
}

function adapter(kennung) {
  const projekt = zustand.projekt;
  const bs = {
    kennung, vorgaben: vorgabenNeu(eintragVon(kennung)), uebersicht: null, gefragt: null,
    lastfall: null,
  };
  return {
    bs,
    einstellung: EINSTELLUNG,
    achsen: ['x', 'z'],
    arten: ARTEN,
    gilt: () => zustand.projekt === projekt,
    zeichnung: () => eintragVon(kennung),
    schreiben: (veraenderer) => schreiben(kennung, veraenderer),
    tafelNeu: () => aendern({}, 'zeichnung'),
    name: elementname,
    neuText,
    punktAnlegen: () => null,
    linieAnlegen,
    zeichnen,
    waehlbar: (art) => art.liste === 'linien',
    umriss: () => umriss(eintragVon(kennung)),
    geaendert: uebersichtHolen,
    gezeichnet: auswahlMarkieren,
    eigenschaften,
    neuEigenschaften,
    teilen: (a, kennungen) => kernBearbeiten(a, kennungen
      .filter((k) => k.startsWith('L'))
      .map((linie) => ({ aktion: 'teilen', linie, anteil: 0.5 })), kennungen),
    umkehren: (a, kennungen) => kernBearbeiten(a, [{ aktion: 'umkehren', linien: kennungen }], kennungen),
    linieTeilen: (a, linie, p) => kernBearbeiten(a, [{ aktion: 'teilen', linie, punkt: p }], [linie]),
  };
}

/** Wie ein Element heisst: nach seiner Kennung, mit der Art davor. */
export function elementname(a, kennung) {
  if (!kennung) return '';
  if (/^K\d+$/.test(kennung)) return `Knoten ${kennung}`;
  if (/^L\d+$/.test(kennung)) {
    const l = eintragVon(a.bs.kennung)?.linien.find((x) => x.kennung === kennung);
    return `${l?.stab ? 'Stab' : 'Linie'} ${kennung}`;
  }
  return kennung;
}

function neuText(a, werkzeug) {
  if (werkzeug === 'linie') return a.bs.vorgaben.linie.stab ? 'Stab' : 'Linie';
  return 'Knoten';
}

function linieAnlegen(a, z, von, bis) {
  const kennung = a.modell.naechsteKennung(z, 'L');
  const v = a.bs.vorgaben.linie;
  z.linien.push({
    ...ausVorlage('systemlinie'), kennung, von, bis,
    stab: v.stab, querschnitt: v.stab ? v.querschnitt : '', material: v.stab ? v.material : '',
  });
  return kennung;
}

/** Was im Bild sein soll: alle Knoten -- sonst ein Feld von 6 × 4 m. */
function umriss(system) {
  const k = system?.knoten || [];
  if (!k.length) return [[0, 0], [6, 4]];
  const xs = k.map((x) => x.x);
  const zs = k.map((x) => x.z);
  return [[Math.min(...xs), Math.min(...zs)], [Math.max(...xs), Math.max(...zs)]];
}

// ===========================================================================
// Der Kern
// ===========================================================================

/**
 * Fragt den Kern nach dem System, wenn es sich seit der letzten Frage
 * geändert hat. Kommt eine Antwort zu spät -- es wurde inzwischen wieder
 * gefragt --, gilt sie nicht mehr.
 */
function uebersichtHolen(a) {
  const system = eintragVon(a.bs.kennung);
  if (!system) return;
  const jetzt = abdruck(system);
  if (a.bs.gefragt === jetzt) return;
  a.bs.gefragt = jetzt;
  api.balkensystemVerlauf(zustand.projekt, a.bs.kennung).then((antwort) => {
    if (a.bs.gefragt !== jetzt) return;
    a.bs.uebersicht = { ...antwort.uebersicht, abdruck: jetzt };
    a.neuZeichnen();
    uebersichtZeichnen(a);
  }).catch((fehler) => {
    if (a.bs.gefragt !== jetzt) return;
    // Ein Verweis, den es nicht gibt, hält das ganze Projekt auf -- dann
    // steht der Satz des Kerns unter der Zeichnung.
    a.bs.uebersicht = { fehler: fehler.message, meldungen: [], abdruck: jetzt };
    a.neuZeichnen();
    uebersichtZeichnen(a);
  });
}

/**
 * Lässt den Kern Linien teilen oder umkehren -- Auftrag für Auftrag, jeder
 * auf dem Ergebnis des vorigen -- und übernimmt das Ergebnis in einem
 * Schritt, den man rückgängig machen kann. Hat sich die Zeichnung
 * inzwischen geändert, gilt die Antwort nicht.
 */
function kernBearbeiten(a, auftraege, auswahlDanach = []) {
  if (!auftraege.length) return;
  const kennung = a.bs.kennung;
  const vorher = abdruck(eintragVon(kennung));
  const projekt = structuredClone(zustand.projekt);
  const neu = [];
  const schritt = (i) => {
    if (i >= auftraege.length) return Promise.resolve();
    return api.balkensystemBearbeiten(projekt, kennung, auftraege[i]).then((antwort) => {
      const stelle = projekt.balkensysteme.findIndex((x) => x.kennung === kennung);
      projekt.balkensysteme[stelle] = antwort.balkensystem;
      neu.push(...antwort.neu);
      return schritt(i + 1);
    });
  };
  schritt(0).then(() => {
    if (abdruck(eintragVon(kennung)) !== vorher) {
      melden('Die Zeichnung hat sich inzwischen geändert – bitte noch einmal.', true);
      return;
    }
    const fertig = projekt.balkensysteme.find((x) => x.kennung === kennung);
    a.aendern((z) => {
      for (const liste of a.listen) z[liste] = fertig[liste];
    }, { auswahl: () => [...auswahlDanach, ...neu] });
  }).catch((fehler) => melden(fehler.message, true));
}

/** Je Element, das eine Meldung nennt, ihre Sätze. */
function meldungenJe(u) {
  const je = new Map();
  for (const m of u?.meldungen || []) {
    for (const k of m.elemente) je.set(k, [...(je.get(k) || []), m]);
  }
  return je;
}

function mitTitel(knoten, texte) {
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

/** Ein Wert mit seiner Einheit, wie er an einer Last steht. */
function wertText(wert, einheit) {
  return `${zahlText(wert, 2)} ${einheit}`;
}

/** Die Richtung einer Kraftlast auf einem Stab, in der Zeichnung -- (c, s) seine Laufrichtung. */
function richtungVon(richtung, c, s) {
  return {
    senkrecht: [0, -1], waagrecht: [1, 0], quer: [s, -c], laengs: [c, s],
  }[richtung] || [0, -1];
}

function zeichnen(a, g) {
  const z = eintragVon(a.bs.kennung);
  if (!z) return;
  const u = passendeUebersicht(a);
  const meldungen = meldungenJe(u);
  const fehler = (k) => (meldungen.get(k) || []).some((m) => m.fehler);
  const texte = (k) => (meldungen.get(k) || []).map((m) => m.text);
  const beweglich = new Set(u?.beweglich || []);
  const lagen = a.modell.lagen(z);
  const bild = (k) => {
    const p = lagen.get(k);
    return p ? nachBild(a.v, p) : null;
  };

  // Linienlager unter allem, dann die Linien, ihre Faser und Gelenke.
  const linien = svgEl('g');
  const zeichen = svgEl('g');
  for (const l of z.linien) {
    const [p, q] = [bild(l.von), bild(l.bis)];
    if (!p || !q) continue;
    if (l.quer !== 'frei' || l.laengs !== 'frei') zeichen.append(linienlagerSymbol(p, q, l.quer, l.laengs));
    const klasse = [l.stab ? 'bs-stab' : 'bs-linie', fehler(l.kennung) || beweglich.has(l.kennung) ? 'ist-fehler' : ''].join(' ');
    linien.append(mitTitel(svgEl('path', {
      d: `M${p[0].toFixed(1)} ${p[1].toFixed(1)} L${q[0].toFixed(1)} ${q[1].toFixed(1)}`, class: klasse,
    }), texte(l.kennung)));
    if (!l.stab) continue;
    const faser = faserSymbol(p, q);
    if (faser) zeichen.append(faser);
    const lang = Math.hypot(q[0] - p[0], q[1] - p[1]) || 1;
    const t = [(q[0] - p[0]) / lang, (q[1] - p[1]) / lang];
    if (l.gelenk_anfang) zeichen.append(gelenkSymbol(p, t));
    if (l.gelenk_ende) zeichen.append(gelenkSymbol(q, [-t[0], -t[1]]));
  }
  g.append(zeichen, linien);

  // Lager.
  for (const lager of z.lager) {
    const p = bild(lager.knoten);
    if (p) g.append(mitTitel(lagerSymbol(p, lager, fehler(lager.kennung) ? 'ist-fehler' : ''), texte(lager.kennung)));
  }

  // Die Lasten des gewählten Lastfalls.
  const lf = aktiverLastfall(a.bs.kennung);
  if (lf) g.append(lastenZeichnen(a, z, lf, lagen));

  // Knoten ohne Drehsteifigkeit, bewegliche Knoten.
  for (const k of u?.unbestimmt || []) {
    const p = bild(k);
    if (p) g.append(unbestimmtSymbol(p, `${k}: ${u.unbestimmt_text}`));
  }
  for (const k of z.knoten) {
    const p = bild(k.kennung);
    if (p && beweglich.has(k.kennung)) {
      g.append(mitTitel(svgEl('circle', { cx: p[0], cy: p[1], r: 8, class: 'bs-beweglich' }), texte(k.kennung)));
    }
  }
}

/**
 * Die Lasten eines Lastfalls: auf den Stäben die verteilten als Pfeilband,
 * Einzellasten und Momente einzeln; an den Knoten Kräfte und Momente. Die
 * Pfeillänge der verteilten Lasten folgt ihrem Wert, je Art im Verhältnis
 * zur grössten.
 */
function lastenZeichnen(a, z, lf, lagen) {
  const g = svgEl('g', { class: 'bs-lasten' });
  const groesste = { linienlast: 0, linienmoment: 0 };
  for (const l of z.linien) {
    for (const last of l.lasten) {
      if (last.lastfall !== lf || !(last.art in groesste)) continue;
      groesste[last.art] = Math.max(groesste[last.art], Math.abs(last.wert_a), Math.abs(last.wert_b ?? last.wert_a));
    }
  }
  for (const l of z.linien) {
    const [pa, pb] = [lagen.get(l.von), lagen.get(l.bis)];
    if (!pa || !pb) continue;
    const L = abstand(pa, pb);
    if (!L) continue;
    const [c, s] = [(pb[0] - pa[0]) / L, (pb[1] - pa[1]) / L];
    const ort = (x) => nachBild(a.v, [pa[0] + c * x, pa[1] + s * x]);
    for (const last of l.lasten) {
      if (last.lastfall !== lf) continue;
      const art = lastart(last.art);
      const r = imBild(richtungVon(last.richtung, c, s));
      if (last.art === 'linienlast') {
        const bis = last.bis ?? L;
        const wb = last.wert_b ?? last.wert_a;
        const massstab = GROESSE.pfeil / (groesste.linienlast || 1);
        g.append(streckenlast(ort(last.von), ort(bis), r, last.wert_a * massstab, wb * massstab,
          last.wert_b === null || last.wert_b === undefined || last.wert_b === last.wert_a
            ? wertText(last.wert_a, art.einheit)
            : `${zahlText(last.wert_a, 2)} … ${wertText(wb, art.einheit)}`));
      } else if (last.art === 'einzellast') {
        const richtung = last.wert_a >= 0 ? r : [-r[0], -r[1]];
        g.append(kraftpfeil(ort(last.von), richtung, 38, wertText(Math.abs(last.wert_a), art.einheit)));
      } else if (last.art === 'moment') {
        g.append(momentSymbol(ort(last.von), last.wert_a, wertText(last.wert_a, art.einheit)));
      } else {
        g.append(streckenmoment(ort(last.von), ort(last.bis ?? L), last.wert_a, wertText(last.wert_a, art.einheit)));
      }
    }
  }
  for (const p of z.knotenlasten) {
    if (p.lastfall !== lf) continue;
    const q = lagen.get(p.knoten);
    if (!q) continue;
    const ort = nachBild(a.v, q);
    if (p.art === 'moment') {
      g.append(momentSymbol(ort, p.wert, wertText(p.wert, 'kNm'), 'bs-last bs-knotenlast'));
    } else {
      const r = imBild(p.richtung === 'waagrecht' ? [1, 0] : [0, -1]);
      const richtung = p.wert >= 0 ? r : [-r[0], -r[1]];
      g.append(kraftpfeil(ort, richtung, 40, wertText(Math.abs(p.wert), 'kN'), 'bs-last bs-knotenlast'));
    }
  }
  return g;
}

// ===========================================================================
// Felder im schwebenden Fenster
// ===========================================================================

function zeile(beschriftung, eingabe, einheit = '') {
  return el('label.cad-zeile', {}, [
    el('span', { text: beschriftung }), eingabe, einheit ? el('span.einheit', { text: einheit }) : el('span'),
  ]);
}

/**
 * Eine Richtung des Lagers mit ihrem Schalter -- frei, fest oder Feder. Die
 * Beschriftung ist ein Zeichen (x, z, φ) und braucht nur eine schmale
 * Spalte. Ein «div», kein «label»: ein Klick auf das Zeichen löste sonst die
 * erste Stellung aus.
 */
function richtungszeile(beschriftung, schalter) {
  return el('div.cad-zeile.ist-richtung', {}, [el('span', { text: beschriftung }), schalter]);
}

function haken(an, setzen, titel = '') {
  return el('input', {
    type: 'checkbox', checked: !!an, title: titel,
    on: { change: (e) => setzen(e.target.checked) },
  });
}

function knopf(text, titel, tun) {
  return el('button.knopf.knopf-klein.bs-neu', {
    type: 'button', text, title: titel, on: { click: (e) => { e.preventDefault(); tun(); } },
  });
}

function querschnittWahl(z, gewaehlt, setzen) {
  const werte = (z.querschnitte || []).map((q) => ({ wert: q.kennung, beschriftung: q.name || q.kennung }));
  if (!werte.length) werte.push({ wert: '', beschriftung: '– keiner –' });
  return auswahl({ werte, gewaehlt, titel: 'Die Querschnitte stehen im Panel «Querschnitte»', beiAenderung: setzen });
}

function materialWahl(gewaehlt, setzen) {
  return auswahl({
    werte: zustand.projekt.materialien.map((m) => ({ wert: m.kennung, beschriftung: m.name || m.sorte })),
    gewaehlt,
    titel: 'E_cm beim Beton, E_s beim Stahl',
    beiAenderung: setzen,
  });
}

/** Die Felder für das, was das Linienwerkzeug als Nächstes anlegt. */
function neuEigenschaften(a, werkzeug) {
  const z = eintragVon(a.bs.kennung);
  const v = a.bs.vorgaben.linie;
  const neu = () => a.neuZeichnen();
  let inhalt = [];
  if (werkzeug === 'linie') {
    inhalt = [
      zeile('Stab', haken(v.stab, (w) => { v.stab = w; neu(); }, 'Ein Stab trägt; sonst nur eine Linie, etwa für ein Linienlager')),
      v.stab ? zeile('Querschnitt', querschnittWahl(z, v.querschnitt, (w) => { v.querschnitt = w; neu(); })) : null,
      v.stab ? zeile('Material', materialWahl(v.material, (w) => { v.material = w; neu(); })) : null,
    ];
  }
  return {
    inhalt: [el('div.cad-neu-titel', { text: 'Neu' }), ...inhalt.filter(Boolean)],
    schluessel: JSON.stringify([werkzeug, v]),
  };
}

function eigenschaften(a) {
  const z = eintragVon(a.bs.kennung);
  const kennungen = [...a.auswahl].map((s) => auswahlTeil(s).kennung);
  const knoten = kennungen.filter((k) => z.knoten.some((x) => x.kennung === k));
  const linien = kennungen.filter((k) => z.linien.some((x) => x.kennung === k));
  const lf = aktiverLastfall(a.bs.kennung);
  const schluessel = JSON.stringify([lf, Boolean(passendeUebersicht(a))]);
  if (knoten.length && linien.length) {
    return {
      titel: `${kennungen.length} gewählt`,
      inhalt: [el('p.cad-hinweis-klein', { text: 'Knoten und Linien zugleich -- verschieben mit V, löschen mit Entf.' })],
      schluessel,
    };
  }
  if (knoten.length) return { ...knotenEigenschaften(a, z, knoten, lf), schluessel };
  if (linien.length) return { ...linienEigenschaften(a, z, linien, lf), schluessel };
  return { titel: '', inhalt: [] };
}

function meldungszeilen(a, kennungen) {
  const u = passendeUebersicht(a);
  return (u?.meldungen || []).filter((m) => m.elemente.some((k) => kennungen.includes(k)))
    .map((m) => el(m.fehler ? 'p.cad-meldung' : 'p.cad-hinweis-klein', { text: m.text }));
}

function lastfallName(z, lf) {
  return z.lastfaelle.find((x) => x.kennung === lf)?.name || lf;
}

// -- Knoten ------------------------------------------------------------------

/** Welche Vorwahl ein Lager trifft -- 'kein', eine der Lagerarten oder 'eigen'. */
function lagerart(lager) {
  if (!lager) return 'kein';
  const treffer = katalog().lagerarten.find((x) => x.x === lager.x && x.z === lager.z && x.phi === lager.phi);
  return treffer ? treffer.wert : 'eigen';
}

function lagerSetzen(a, z, knoten, art) {
  z.lager = z.lager.filter((l) => l.knoten !== knoten || art !== 'kein');
  if (art === 'kein') return;
  let lager = z.lager.find((l) => l.knoten === knoten);
  if (!lager) {
    lager = { ...ausVorlage('lager'), kennung: a.modell.naechsteKennung(z, 'A'), knoten };
    z.lager.push(lager);
  }
  const vorwahl = katalog().lagerarten.find((x) => x.wert === art);
  if (vorwahl) Object.assign(lager, { x: vorwahl.x, z: vorwahl.z, phi: vorwahl.phi });
}

function lagerFelder(a, z, knoten) {
  const lager = knoten.map((k) => z.lager.find((l) => l.knoten === k) || null);
  const arten = new Set(lager.map(lagerart));
  const gemeinsam = arten.size === 1 ? [...arten][0] : '';
  const setzen = (art) => a.aendern((zz) => { for (const k of knoten) lagerSetzen(a, zz, k, art); });
  // Haben die gewählten Knoten verschiedene Lager, steht keine Stellung an.
  const werte = [
    { wert: 'kein', beschriftung: 'kein', titel: 'Kein Lager' },
    ...katalog().lagerarten.map((x) => ({ wert: x.wert, beschriftung: x.wert })),
    { wert: 'eigen', beschriftung: 'je Richtung', titel: 'Je Richtung frei, fest oder eine Feder' },
  ];
  const zeilen = [wahlBlock('Lager', wahlSchalter({
    werte, gewaehlt: gemeinsam, setzen, klasse: '.ist-umbruch',
    titel: gemeinsam ? 'Lager des Knotens' : 'Die gewählten Knoten haben verschiedene Lager',
  }))];
  const erstes = lager.find(Boolean);
  if (!erstes || gemeinsam === 'kein') return zeilen;
  const einheiten = katalog().federeinheiten;
  const richtungSetzen = (feld) => (wert) => a.aendern((zz) => {
    for (const l of zz.lager) if (knoten.includes(l.knoten)) l[feld] = wert;
  });
  for (const [feld, name] of [['x', 'x'], ['z', 'z'], ['phi', 'φ']]) {
    const halt = erstes[feld];
    zeilen.push(richtungszeile(name, wahlSchalter({
      werte: HALT, gewaehlt: halt, setzen: richtungSetzen(feld), titel: `Halt in ${name}`,
    })));
    if (halt === 'feder') {
      zeilen.push(zeile(`  k_${name}`, zahlfeld({
        wert: erstes[`k_${feld}`], schritt: 1000, min: 0,
        titel: `Federsteifigkeit in ${name}`, beiAenderung: richtungSetzen(`k_${feld}`),
      }), einheiten[`k_${feld}`] || ''));
    }
  }
  return zeilen;
}

function knotenlastFelder(a, z, knoten, lf) {
  if (!lf) return [el('p.cad-hinweis-klein', { text: 'Für Lasten zuerst im Panel «Lastfälle» einen Lastfall anlegen.' })];
  const zeilen = [el('div.cad-neu-titel', { text: `Lasten · ${lastfallName(z, lf)}` })];
  if (knoten.length === 1) {
    for (const p of z.knotenlasten.filter((x) => x.knoten === knoten[0] && x.lastfall === lf)) {
      const setzen = (wert) => a.aendern((zz) => {
        const da = zz.knotenlasten.find((x) => x.kennung === p.kennung);
        if (da) da.wert = wert;
      });
      const weg = () => a.aendern((zz) => { zz.knotenlasten = zz.knotenlasten.filter((x) => x.kennung !== p.kennung); });
      const beschriftung = p.art === 'moment' ? '↺ Moment' : richtungText(p.richtung);
      zeilen.push(el('div.bs-lastzeile', {}, [
        zeile(beschriftung, zahlfeld({ wert: p.wert, schritt: 5, titel: 'Positiv in Pfeilrichtung, ein Moment im Gegenuhrzeigersinn', beiAenderung: setzen }),
          p.art === 'moment' ? 'kNm' : 'kN'),
        el('button.weg', { type: 'button', text: '×', title: 'Last löschen', on: { click: weg } }),
      ]));
    }
  }
  const neu = (art, richtung) => () => a.aendern((zz) => {
    for (const k of knoten) {
      zz.knotenlasten.push({
        ...ausVorlage('knotenlast'), kennung: a.modell.naechsteKennung(zz, 'P'), knoten: k,
        lastfall: lf, art, richtung,
      });
    }
  });
  zeilen.push(el('div.bs-neue-lasten', {}, [
    knopf('+ ↓ Kraft', 'Eine Kraft nach unten -- an jedem gewählten Knoten', neu('kraft', 'senkrecht')),
    knopf('+ → Kraft', 'Eine Kraft nach rechts', neu('kraft', 'waagrecht')),
    knopf('+ ↺ Moment', 'Ein Moment im Gegenuhrzeigersinn', neu('moment', 'senkrecht')),
  ]));
  return zeilen;
}

function knotenEigenschaften(a, z, knoten, lf) {
  const inhalt = [];
  if (knoten.length === 1) {
    const k = z.knoten.find((x) => x.kennung === knoten[0]);
    const lageSetzen = (i) => (w) => a.aendern((zz) => {
      const da = zz.knoten.find((x) => x.kennung === k.kennung);
      if (!da) return;
      const d = i === 0 ? [w - da.x, 0] : [0, w - da.z];
      a.modell.verschieben(zz, new Set([k.kennung]), d);
    });
    inhalt.push(
      zeile('x', zahlfeld({ wert: k.x, schritt: a.raster, beiAenderung: lageSetzen(0) }), 'm'),
      zeile('z', zahlfeld({ wert: k.z, schritt: a.raster, beiAenderung: lageSetzen(1) }), 'm'),
    );
  }
  inhalt.push(...lagerFelder(a, z, knoten), ...knotenlastFelder(a, z, knoten, lf));
  const u = passendeUebersicht(a);
  for (const k of knoten) {
    if (u?.unbestimmt?.includes(k)) inhalt.push(el('p.cad-hinweis-klein', { text: `${k}: ${u.unbestimmt_text}.` }));
  }
  inhalt.push(...meldungszeilen(a, knoten));
  return {
    titel: knoten.length === 1 ? `Knoten ${knoten[0]}` : `${knoten.length} Knoten`,
    inhalt: inhalt.filter(Boolean),
  };
}

// -- Linien ------------------------------------------------------------------

function lagerAnLinie(a, linien, e) {
  const einheiten = katalog().federeinheiten;
  const setzen = (feld) => (wert) => a.aendern((zz) => {
    for (const l of zz.linien) if (linien.includes(l.kennung)) l[feld] = wert;
  });
  const werte = HALT.map((x) => (x.wert === 'feder' ? { ...x, beschriftung: 'Bettung' } : x));
  const zeilen = [];
  for (const [feld, name, titel] of [
    ['quer', 'Lager quer', 'Quer zur Linie, auf der Seite der gestrichelten Faser: fest -- der Stab biegt sich nicht --, oder gebettet'],
    ['laengs', 'Lager längs', 'Längs der Linie: fest oder gebettet']]) {
    zeilen.push(wahlBlock(name, wahlSchalter({ werte, gewaehlt: e[feld], titel, setzen: setzen(feld) })));
    if (e[feld] === 'feder') {
      zeilen.push(zeile(`  k_${feld === 'quer' ? '⊥' : '∥'}`, zahlfeld({
        wert: e[`k_${feld}`], schritt: 1000, min: 0, titel: 'Bettungsziffer je Meter Stab',
        beiAenderung: setzen(`k_${feld}`),
      }), einheiten[`k_${feld}`] || ''));
    }
  }
  return zeilen;
}

/** Die Felder einer Last auf einem Stab -- je nach Art. */
function stablastFelder(a, linie, i, last) {
  const art = lastart(last.art);
  const setzen = (feld) => (wert) => a.aendern((zz) => {
    const l = zz.linien.find((x) => x.kennung === linie);
    if (l?.lasten[i]) l.lasten[i][feld] = wert;
  });
  const weg = () => a.aendern((zz) => {
    const l = zz.linien.find((x) => x.kennung === linie);
    if (l) l.lasten.splice(i, 1);
  });
  const kopf = el('div.bs-lastkopf', {}, [
    el('span', { text: art.beschriftung }),
    el('button.weg', { type: 'button', text: '×', title: 'Last löschen', on: { click: weg } }),
  ]);
  const zeilen = [kopf];
  if (art.kraft) {
    zeilen.push(wahlBlock('Richtung', wahlSchalter({
      werte: katalog().richtungen, gewaehlt: last.richtung,
      titel: 'Positiv in Pfeilrichtung: senkrecht nach unten, quer zur gestrichelten Faser, längs vom Anfang zum Ende',
      setzen: setzen('richtung'), klasse: '.ist-wortlaut.ist-umbruch',
    })));
  }
  if (art.verteilt) {
    zeilen.push(
      zeile('Anfang', zahlfeld({ wert: last.wert_a, schritt: 5, titel: 'Wert am Anfang des belasteten Bereichs', beiAenderung: setzen('wert_a') }), art.einheit),
      zeile('Ende', zahlfeld({
        wert: last.wert_b, schritt: 5, leer: null, platzhalter: 'wie Anfang',
        titel: 'Wert am Ende -- leer: wie am Anfang', beiAenderung: setzen('wert_b'),
      }), art.einheit),
      zeile('von', zahlfeld({ wert: last.von, schritt: 0.5, min: 0, titel: 'In m ab dem Anfang des Stabs', beiAenderung: setzen('von') }), 'm'),
      zeile('bis', zahlfeld({
        wert: last.bis, schritt: 0.5, min: 0, leer: null, platzhalter: 'Ende',
        titel: 'In m ab dem Anfang -- leer: bis zum Ende', beiAenderung: setzen('bis'),
      }), 'm'),
    );
    if (art.kraft && (last.richtung === 'senkrecht' || last.richtung === 'waagrecht')) {
      zeilen.push(zeile('projiziert', haken(last.projiziert, setzen('projiziert'),
        'Je Meter der Projektion statt je Meter Stab -- wie Schnee auf einem Dach')));
    }
  } else {
    zeilen.push(
      zeile('Wert', zahlfeld({ wert: last.wert_a, schritt: 5, beiAenderung: setzen('wert_a') }), art.einheit),
      zeile('bei', zahlfeld({ wert: last.von, schritt: 0.5, min: 0, titel: 'In m ab dem Anfang des Stabs', beiAenderung: setzen('von') }), 'm'),
    );
  }
  return el('div.bs-lastblock', {}, zeilen);
}

function stablastenFelder(a, z, linien, lf) {
  if (!lf) return [el('p.cad-hinweis-klein', { text: 'Für Lasten zuerst im Panel «Lastfälle» einen Lastfall anlegen.' })];
  const zeilen = [el('div.cad-neu-titel', { text: `Lasten · ${lastfallName(z, lf)}` })];
  if (linien.length === 1) {
    const e = z.linien.find((x) => x.kennung === linien[0]);
    e.lasten.forEach((last, i) => {
      if (last.lastfall === lf) zeilen.push(stablastFelder(a, e.kennung, i, last));
    });
  } else {
    const anzahl = z.linien.filter((l) => linien.includes(l.kennung))
      .reduce((n, l) => n + l.lasten.filter((x) => x.lastfall === lf).length, 0);
    zeilen.push(el('p.cad-hinweis-klein', { text: `${anzahl} Lasten auf den gewählten Linien -- einzeln bearbeiten.` }));
  }
  const neu = (art) => () => a.aendern((zz) => {
    for (const l of zz.linien) {
      if (linien.includes(l.kennung)) l.lasten.push({ ...ausVorlage('stablast'), lastfall: lf, art });
    }
  });
  zeilen.push(el('div.bs-neue-lasten', {}, katalog().lastarten.map((x) => knopf(
    `+ ${x.beschriftung}`, `${x.beschriftung} in ${x.einheit} -- auf jeder gewählten Linie`, neu(x.wert)))));
  return zeilen;
}

function linienEigenschaften(a, z, linien, lf) {
  const e = z.linien.find((x) => x.kennung === linien[0]);
  const setzen = (feld) => (wert) => a.aendern((zz) => {
    for (const l of zz.linien) if (linien.includes(l.kennung)) l[feld] = wert;
  });
  const inhalt = [
    zeile('Stab', haken(e.stab, (w) => a.aendern((zz) => {
      for (const l of zz.linien) {
        if (!linien.includes(l.kennung)) continue;
        l.stab = w;
        // Ein neuer Stab bekommt, was das Werkzeug vorgibt -- sonst fehlte ihm beides.
        if (w && !l.querschnitt) l.querschnitt = a.bs.vorgaben.linie.querschnitt;
        if (w && !l.material) l.material = a.bs.vorgaben.linie.material;
      }
    }), 'Ein Stab trägt; sonst nur eine Linie, etwa für ein Linienlager')),
  ];
  if (e.stab) {
    inhalt.push(
      zeile('Querschnitt', querschnittWahl(z, e.querschnitt, setzen('querschnitt'))),
      zeile('Material', materialWahl(e.material, setzen('material'))),
      zeile('Gelenk Anfang', haken(e.gelenk_anfang, setzen('gelenk_anfang'), 'Kein Moment am Anfang')),
      zeile('Gelenk Ende', haken(e.gelenk_ende, setzen('gelenk_ende'), 'Kein Moment am Ende')),
    );
  }
  inhalt.push(...lagerAnLinie(a, linien, e));
  if (e.stab) inhalt.push(...stablastenFelder(a, z, linien, lf));
  if (linien.length === 1) {
    const lagen = a.modell.lagen(z);
    const [p, q] = [lagen.get(e.von), lagen.get(e.bis)];
    if (p && q) inhalt.push(el('p.cad-info', { text: `L = ${zahlText(abstand(p, q), 3)} m · ${e.von} → ${e.bis}` }));
  }
  inhalt.push(...meldungszeilen(a, linien));
  return {
    titel: linien.length === 1 ? elementname(a, e.kennung) : `${linien.length} Linien`,
    inhalt: inhalt.filter(Boolean),
  };
}
