/**
 * bs_zeichnung.js -- das Zeichenfenster eines Balkensystems: der Adapter.
 *
 * Gezeichnet werden Knoten und Linien, in Metern, x nach rechts und z nach
 * oben. Eine Linie ist ein Stab, sobald sie einen Querschnitt hat; daneben
 * kann sie ein Linienlager sein, quer und längs (die Bettung, im Fenster
 * eingeklappt). Lager sind eigene Einträge an einem Knoten -- so überstehen
 * sie das Zusammenführen von Knoten --, gewählt wird aber der Knoten.
 *
 * ZUGSEITE:
 * Die gestrichelte Faser liegt rechts der Laufrichtung einer Linie. Eine
 * neue Linie läuft darum nach rechts, eine senkrechte nach unten: ihre
 * Zugseite liegt unten bzw. links (Benutzer, 2026-10-24). Der Schalter
 * «Zugseite» im Fenster kehrt die Linie um, wie «Umkehren».
 *
 * LASTEN:
 * Jede Last ist für sich zu wählen und zu löschen, ein Anhang des
 * Zeichenfensters (`anhaenge`): ein Klick auf ihren Pfeil, ihr Band oder ihre
 * Zahl (Benutzer, 2026-10-23). Angelegt wird sie mit dem Werkzeug «Last» --
 * ein Klick auf eine Linie, eine Einzellast oder ein Moment auch an einen
 * Knoten; eine Einzellast auf einer Linie steht dort, wo geklickt wurde, in
 * % der Linie. Gezeigt werden die Lasten des gewählten Lastfalls. Die Lasten
 * auf einem Stab stehen an seiner Linie und gehen mit ihr, wenn sie kopiert,
 * geteilt oder gelöscht wird; die an einem Knoten sind eigene Einträge an
 * ihm.
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
import { ARTEN as BAUTEILARTEN } from './arten.js';
import { wahlBlock, wahlSchalter } from './bausteine.js';
import { nachBild, zahlText } from './cad_ansicht.js';
import { imSpiel } from './cad_auswahl.js';
import { cadBereich, cadFenster, cadVergessen, cadWaehlen } from './cad_fenster.js';
import { NAEHE } from './cad_eingabe.js';
import {
  abstand, aufStrecke, auswahlTeil, innen,
} from './cad_modell.js';
import {
  GROESSE, faserSymbol, gelenkSymbol, imBild, kraftpfeil, lagerSymbol, linienlagerSymbol,
  momentSymbol, streckenlast, streckenmoment, unbestimmtSymbol,
} from './bs_symbole.js';
import {
  auswahl, el, melden, svgEl, zahlfeld,
} from './dom.js';
import { aendern, ausVorlage, projektAendern, zustand } from './zustand.js';

/**
 * Die Arten des Systems. Gewählt werden Linien und Knoten: ein Lager gehört
 * seinem Knoten (`waehlbar`). Eine Knotenlast wählt man an ihrem Pfeil, wie
 * jede Last (`anhaenge`).
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
      titel: 'Linie -- ein Stab, sobald sie einen Querschnitt hat' },
    { name: 'knoten', text: 'Knoten', zeichen: 'cad-knoten', taste: 'k', form: 'knoten' },
    { name: 'last', text: 'Last', zeichen: 'cad-last', taste: 'q', form: 'anhang',
      titel: 'Last -- auf eine Linie klicken, eine Einzellast oder ein Moment auch an einen Knoten' },
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

// ===========================================================================
// Das Fenster eines Systems
// ===========================================================================

/**
 * Das Zeichenfenster eines Systems, samt der Liste darunter. Die Tafel ruft
 * das bei jedem Neubau -- dann fragt es auch den Kern, wenn sich nicht die
 * Zeichnung geändert hat, aber ein Querschnitt oder Material.
 */
export function zeichenbereich(system, uebersichtBauen) {
  const a = fensterVon(system.kennung);
  const unten = el('div.qa-uebersicht-huelle');
  a.bs.uebersichtKnoten = unten;
  a.bs.uebersichtBauen = uebersichtBauen;
  const bereich = cadBereich(a, [unten]);
  uebersichtHolen(a);
  uebersichtZeichnen(a);
  lastfallLeiste(a);
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
  // «– kein Lastfall –»: die Zeichnung zeigt keine Lasten.
  if (a.bs.lastfall === '') return null;
  if (faelle.some((lf) => lf.kennung === a.bs.lastfall)) return a.bs.lastfall;
  // Zuerst das Eigengewicht (Benutzer, 2026-10-24).
  return (faelle.find((lf) => lf.eigengewicht) || faelle[0])?.kennung || null;
}

/**
 * Die Wahl des Lastfalls gleich neben dem Werkzeug «Last» (Benutzer,
 * 2026-10-24): dessen Lasten zeigt und bearbeitet die Zeichnung -- oder
 * «– kein Lastfall –». Neu bei jedem Neubau der Tafel, damit sie jeden
 * Lastfall kennt.
 */
function lastfallLeiste(a) {
  const huelle = a.bs.lastfallHuelle;
  if (!huelle) return;
  const faelle = eintragVon(a.bs.kennung)?.lastfaelle || [];
  huelle.replaceChildren(auswahl({
    werte: [{ wert: '', beschriftung: '– kein Lastfall –' },
      ...faelle.map((x) => ({ wert: x.kennung, beschriftung: x.name }))],
    gewaehlt: aktiverLastfall(a.bs.kennung) || '',
    titel: 'Dessen Lasten zeigt und bearbeitet die Zeichnung',
    beiAenderung: (w) => lastfallWaehlen(a.bs.kennung, w),
  }));
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
  return u && u.abdruck === abdruckVon(a.bs.kennung) ? u : null;
}

/**
 * Wovon jede Antwort des Kerns zu einem System abhängt: das System, die
 * Materialien und die Bauteile, deren Querschnitt es nimmt. Ändert sich
 * davon etwas -- etwa eine Dichte oder die Höhe einer Platte --, gilt sie
 * nicht mehr: die Übersicht samt dem gezeichneten Eigengewicht hier, die
 * Verläufe in den Diagrammen.
 */
export function abdruckVon(kennung) {
  const system = eintragVon(kennung);
  const bezuege = (system?.querschnitte || []).map((q) => q.bezug).filter(Boolean);
  const bauteile = BAUTEILARTEN.flatMap((a) => zustand.projekt[a.liste] || [])
    .filter((b) => bezuege.includes(b.kennung));
  return JSON.stringify([system, zustand.projekt.materialien, bauteile]);
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
      querschnitt: system?.querschnitte?.[0]?.kennung || '',
      material: beton?.kennung || '',
    },
    last: {
      art: 'linienlast', richtung: 'senkrecht', wert_a: 10, wert_b: null,
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
    leisteZusatz: () => {
      bs.lastfallHuelle = el('span.bs-lastfallwahl');
      return bs.lastfallHuelle;
    },
    name: elementname,
    neuText,
    punktAnlegen: () => null,
    linieAnlegen,
    anhangAnlegen: lastAnlegen,
    zeichnen,
    waehlbar: (art) => art.liste === 'linien',
    anhaenge: {
      hat: (z, kennung) => Boolean(z && lastVon(z, kennung)),
      treffer: lastenGetroffen,
      // Knotenlasten sind Elemente des Fensters, die löscht es selbst.
      loeschen: (z, weg) => {
        for (const l of z.linien) l.lasten = l.lasten.filter((x) => !weg.has(x.kennung));
      },
      rahmen: lastenRahmen,
    },
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
    return `${l?.querschnitt ? 'Stab' : 'Linie'} ${kennung}`;
  }
  if (/^P\d+$/.test(kennung)) return `Last ${kennung}`;
  return kennung;
}

function neuText(a, werkzeug) {
  if (werkzeug === 'linie') return a.bs.vorgaben.linie.querschnitt ? 'Stab' : 'Linie';
  if (werkzeug === 'last') return lastart(a.bs.vorgaben.last.art).beschriftung;
  return 'Knoten';
}

/**
 * Wo die gestrichelte Faser einer Linie von p nach q liegt, ihre Zugseite:
 * rechts der Laufrichtung -- 'unten' oder 'oben', an einer senkrechten
 * 'links' oder 'rechts'. Lagen [x, z] der Zeichnung.
 */
function zugseite(p, q) {
  const [dx, dz] = [q[0] - p[0], q[1] - p[1]];
  if (Math.abs(dx) <= 1e-9 * Math.hypot(dx, dz)) return dz > 0 ? 'rechts' : 'links';
  return dx > 0 ? 'unten' : 'oben';
}

/**
 * Eine neue Linie mit den Vorgaben des Werkzeugs. Ihre Zugseite liegt
 * unten, an einer senkrechten links (Benutzer, 2026-10-24): sie läuft dafür
 * nach rechts bzw. nach unten, wie herum man sie auch zeichnet.
 */
function linieAnlegen(a, z, von, bis) {
  const kennung = a.modell.naechsteKennung(z, 'L');
  const v = a.bs.vorgaben.linie;
  const lagen = a.modell.lagen(z);
  if (['oben', 'rechts'].includes(zugseite(lagen.get(von), lagen.get(bis)))) [von, bis] = [bis, von];
  z.linien.push({
    ...ausVorlage('systemlinie'), kennung, von, bis,
    querschnitt: v.querschnitt, material: v.querschnitt ? v.material : '',
  });
  return kennung;
}

// ===========================================================================
// Lasten
// ===========================================================================

/** Jede Last des Systems -- auf den Linien und an den Knoten. */
function alleLasten(z) {
  return [...z.linien.flatMap((l) => l.lasten), ...z.knotenlasten];
}

/** Die Last zu einer Kennung -- `{last, linie}` oder `{last, knoten}` -- oder null. */
function lastVon(z, kennung) {
  for (const l of z.linien) {
    const last = l.lasten.find((x) => x.kennung === kennung);
    if (last) return { last, linie: l };
  }
  const p = z.knotenlasten.find((x) => x.kennung === kennung);
  return p ? { last: p, knoten: p.knoten } : null;
}

/** Die nächste Kennung einer Last: die grösste plus eins, wie im Kern -- Stab- und Knotenlasten zählen zusammen. */
function naechsteLast(z) {
  const nummern = alleLasten(z).map((x) => Number(String(x.kennung).replace(/^P/, '')) || 0);
  return `P${Math.max(0, ...nummern) + 1}`;
}

/**
 * Eine Last, wo geklickt wurde -- im gewählten Lastfall, nach den Vorgaben
 * des Werkzeugs. Eine Einzellast oder ein Moment an einem Knoten, wenn er
 * getroffen ist; sonst auf der nächsten Linie: verteilt auf der ganzen,
 * einzeln dort, wo geklickt wurde. Gibt die Kennung zurück, oder null.
 */
function lastAnlegen(a, z, erg) {
  const lf = aktiverLastfall(a.bs.kennung);
  if (!lf) {
    melden('Für eine Last zuerst oben neben «Last» einen Lastfall wählen.', true);
    return null;
  }
  const v = a.bs.vorgaben.last;
  const art = lastart(v.art);
  const weit = NAEHE / a.v.massstab;
  if (!art.verteilt) {
    const knoten = erg.knoten || z.knoten.find((k) => abstand([k.x, k.z], erg.p) <= weit)?.kennung;
    if (knoten) {
      const kennung = naechsteLast(z);
      z.knotenlasten.push({
        ...ausVorlage('knotenlast'), kennung, knoten, lastfall: lf,
        art: v.art === 'moment' ? 'moment' : 'kraft',
        richtung: katalog().knotenrichtungen.includes(v.richtung) ? v.richtung : 'senkrecht',
        wert: v.wert_a,
      });
      return kennung;
    }
  }
  const lagen = a.modell.lagen(z);
  let beste = null;
  for (const l of z.linien) {
    const [p, q] = [lagen.get(l.von), lagen.get(l.bis)];
    if (!p || !q) continue;
    const { q: fuss, t } = aufStrecke(erg.p, p, q);
    const d = abstand(fuss, erg.p);
    if (d <= weit && (!beste || d < beste.d)) beste = { l, t, d };
  }
  if (!beste) {
    melden(art.verteilt ? 'Eine verteilte Last gehört auf eine Linie -- dort klicken.'
      : 'Auf eine Linie oder einen Knoten klicken.');
    return null;
  }
  const kennung = naechsteLast(z);
  beste.l.lasten.push({
    ...ausVorlage('stablast'), kennung, lastfall: lf, art: v.art, richtung: v.richtung,
    wert_a: v.wert_a, wert_b: art.verteilt ? v.wert_b : null,
    // In % der Linie, auf ein Zehntel -- dort, wo geklickt wurde.
    ...(art.verteilt ? {} : { stelle: Math.round(beste.t * 1000) / 10 }),
  });
  return kennung;
}

/**
 * Welche Lasten ein Klick trifft, die nächste zuerst: ihre Formen im Bild
 * stehen vom letzten Zeichnen da (`a.bs.lastformen`), dazu ihre Zahl. Ein
 * Band zählt nicht bis an seine Linie heran und ein Pfeil nicht bis an seine
 * Spitze: dort soll ein Klick die Linie oder den Knoten treffen.
 */
function lastenGetroffen(a, bild) {
  const ecke = a.teile.bild.getBoundingClientRect();
  const treffer = [];
  for (const f of a.bs.lastformen || []) {
    let d = f.formen.reduce((m, x) => Math.min(m, formAbstand(x, bild)), Infinity);
    const r = f.text?.isConnected ? f.text.getBoundingClientRect() : null;
    if (r && bild[0] >= r.left - ecke.left - 2 && bild[0] <= r.right - ecke.left + 2
        && bild[1] >= r.top - ecke.top - 2 && bild[1] <= r.bottom - ecke.top + 2) d = 0;
    if (d <= 0) treffer.push({ kennung: f.kennung, d: abstand(bild, f.mitte) });
  }
  return treffer.sort((p, q) => p.d - q.d).map((x) => x.kennung);
}

/** Null, wenn der Bildpunkt die Form trifft -- sonst etwas Positives. */
function formAbstand(form, p) {
  if (form.art === 'band') {
    const [a, b] = form.linie;
    const vonLinie = abstand(p, aufStrecke(p, a, b).q);
    return innen(p, form.punkte) && vonLinie >= 4 ? 0 : 1;
  }
  if (form.art === 'strecke') {
    return abstand(p, aufStrecke(p, form.von, form.bis).q) <= 5 ? 0 : 1;
  }
  // Ein Bogen: auf dem Ring um seinen Mittelpunkt.
  return Math.abs(abstand(p, form.mitte) - form.r) <= 5 ? 0 : 1;
}

/** Wo die gewählten Lasten im Bild liegen -- [x0, y0, x1, y1] oder null. */
function lastenRahmen(a) {
  const ecke = a.teile.bild.getBoundingClientRect();
  const rahmen = (a.bs.lastformen || []).filter((f) => a.auswahl.has(f.kennung) && f.knoten.isConnected)
    .map((f) => f.knoten.getBoundingClientRect());
  if (!rahmen.length) return null;
  return [Math.min(...rahmen.map((r) => r.left)) - ecke.left, Math.min(...rahmen.map((r) => r.top)) - ecke.top,
    Math.max(...rahmen.map((r) => r.right)) - ecke.left, Math.max(...rahmen.map((r) => r.bottom)) - ecke.top];
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
  const jetzt = abdruckVon(a.bs.kennung);
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
  const vorher = abdruckVon(kennung);
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
    if (abdruckVon(kennung) !== vorher) {
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
    const klasse = [l.querschnitt ? 'bs-stab' : 'bs-linie', fehler(l.kennung) || beweglich.has(l.kennung) ? 'ist-fehler' : ''].join(' ');
    linien.append(mitTitel(svgEl('path', {
      d: `M${p[0].toFixed(1)} ${p[1].toFixed(1)} L${q[0].toFixed(1)} ${q[1].toFixed(1)}`, class: klasse,
    }), texte(l.kennung)));
    if (!l.querschnitt) continue;
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
  a.bs.lastformen = [];
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
 * zur grössten. Je Last merkt sich das Fenster ihr Zeichen und seine Formen
 * zum Wählen (`a.bs.lastformen`); eine gewählte steht blau. Bekommt der
 * Lastfall das Eigengewicht, steht es grau dabei -- je Stab vom Kern, nicht
 * zu wählen und nicht zu löschen.
 */
function lastenZeichnen(a, z, lf, lagen) {
  const g = svgEl('g', { class: 'bs-lasten' });
  const formen = [];
  const ablegen = (kennung, zeichen) => {
    zeichen.classList.add('bs-lastgruppe');
    if (a.auswahl.has(kennung)) zeichen.classList.add('ist-gewaehlt');
    g.append(zeichen);
    const punkte = zeichen.formen.flatMap((f) => f.punkte || (f.von ? [f.von, f.bis] : [f.mitte]));
    const mitte = [0, 1].map((i) => punkte.reduce((s, p) => s + p[i], 0) / punkte.length);
    formen.push({ kennung, knoten: zeichen, formen: zeichen.formen, mitte, text: zeichen.querySelector('text') });
  };
  const eigen = z.lastfaelle.find((x) => x.kennung === lf)?.eigengewicht
    ? passendeUebersicht(a)?.eigengewicht || {} : {};
  const groesste = { linienlast: Math.max(0, ...Object.values(eigen)), linienmoment: 0 };
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
    const gk = eigen[l.kennung];
    if (gk) {
      const lang = (gk * GROESSE.pfeil) / (groesste.linienlast || 1);
      g.append(streckenlast(ort(0), ort(L), imBild([0, -1]), lang, lang,
        `g_k = ${wertText(gk, 'kN/m')}`, 'bs-last bs-eigengewicht'));
    }
    for (const last of l.lasten) {
      if (last.lastfall !== lf) continue;
      const art = lastart(last.art);
      const r = imBild(richtungVon(last.richtung, c, s));
      // Eine verteilte Last liegt auf der ganzen Linie, eine einzelne an ihrer Stelle.
      const stelle = ort((last.stelle / 100) * L);
      if (last.art === 'linienlast') {
        const wb = last.wert_b ?? last.wert_a;
        const massstab = GROESSE.pfeil / (groesste.linienlast || 1);
        ablegen(last.kennung, streckenlast(ort(0), ort(L), r, last.wert_a * massstab, wb * massstab,
          last.wert_b === null || last.wert_b === undefined || last.wert_b === last.wert_a
            ? wertText(last.wert_a, art.einheit)
            : `${zahlText(last.wert_a, 2)} … ${wertText(wb, art.einheit)}`));
      } else if (last.art === 'einzellast') {
        const richtung = last.wert_a >= 0 ? r : [-r[0], -r[1]];
        ablegen(last.kennung, kraftpfeil(stelle, richtung, 38, wertText(Math.abs(last.wert_a), art.einheit)));
      } else if (last.art === 'moment') {
        ablegen(last.kennung, momentSymbol(stelle, last.wert_a, wertText(last.wert_a, art.einheit)));
      } else {
        ablegen(last.kennung, streckenmoment(ort(0), ort(L), last.wert_a, wertText(last.wert_a, art.einheit)));
      }
    }
  }
  for (const p of z.knotenlasten) {
    if (p.lastfall !== lf) continue;
    const q = lagen.get(p.knoten);
    if (!q) continue;
    const ort = nachBild(a.v, q);
    if (p.art === 'moment') {
      ablegen(p.kennung, momentSymbol(ort, p.wert, wertText(p.wert, 'kNm'), 'bs-last bs-knotenlast'));
    } else {
      const r = imBild(p.richtung === 'waagrecht' ? [1, 0] : [0, -1]);
      const richtung = p.wert >= 0 ? r : [-r[0], -r[1]];
      ablegen(p.kennung, kraftpfeil(ort, richtung, 40, wertText(Math.abs(p.wert), 'kN'), 'bs-last bs-knotenlast'));
    }
  }
  a.bs.lastformen = formen;
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

/** Wie `zeile`, für einen Schalter -- ebenso ein «div», kein «label». */
function schalterzeile(beschriftung, schalter) {
  return el('div.cad-zeile', {}, [el('span', { text: beschriftung }), schalter, el('span')]);
}

function haken(an, setzen, titel = '') {
  return el('input', {
    type: 'checkbox', checked: !!an, title: titel,
    on: { change: (e) => setzen(e.target.checked) },
  });
}

/** Die Querschnitte des Systems -- und «kein Stab»: dann ist die Linie nur eine Linie, etwa für eine Bettung. */
function querschnittWahl(z, gewaehlt, setzen) {
  const werte = [
    { wert: '', beschriftung: '– kein Stab –' },
    ...(z.querschnitte || []).map((q) => ({ wert: q.kennung, beschriftung: q.name || q.kennung })),
  ];
  return auswahl({ werte, gewaehlt, titel: 'Die Querschnitte stehen unter der Zeichnung', beiAenderung: setzen });
}

/**
 * Das Material einer Linie: eines aus dem Projekt -- oder «gemäss
 * Querschnitt», wenn ihr Querschnitt eines mitbringt (Platte, Analyse).
 */
function materialWahl(z, querschnitt, gewaehlt, setzen) {
  const eigenes = katalog().material_des_querschnitts;
  const art = z.querschnitte.find((q) => q.kennung === querschnitt)?.art;
  const bringt = katalog().querschnittsarten?.find((x) => x.wert === art)?.bringt_material;
  return auswahl({
    werte: [
      ...(bringt || gewaehlt === eigenes ? [{ wert: eigenes, beschriftung: 'gemäss Querschnitt' }] : []),
      ...zustand.projekt.materialien.map((m) => ({ wert: m.kennung, beschriftung: m.name || m.sorte })),
    ],
    gewaehlt,
    titel: 'E_cm beim Beton, E_s beim Stahl -- «gemäss Querschnitt»: der Beton der Platte oder Analyse',
    beiAenderung: setzen,
  });
}

/**
 * Der Lastfall, in den das Werkzeug zeichnet und dessen Lasten die
 * Zeichnung zeigt -- eine Wahl aus dem Projekt, darum eine Liste.
 */
function lastfallWahl(a, z, gewaehlt, setzen, titel) {
  if (!z.lastfaelle.length) {
    return el('p.cad-hinweis-klein', { text: 'Für Lasten zuerst im Panel «Lastfälle» einen Lastfall anlegen.' });
  }
  return zeile('Lastfall', auswahl({
    werte: z.lastfaelle.map((x) => ({ wert: x.kennung, beschriftung: x.name })),
    gewaehlt, titel, beiAenderung: setzen,
  }));
}

/**
 * Die Felder einer Last: Richtung, Wert -- verteilt Anfang und Ende --,
 * die Stelle einer einzelnen in % der Linie, und ob eine verteilte je Meter
 * Projektion zählt. `last` ist die Last oder die Vorgabe des Werkzeugs,
 * `setzen(feld, wert)` schreibt; `aufLinie`: liegt sie auf einer Linie (sonst
 * an einem Knoten oder noch nirgends).
 */
function lastFelder(last, setzen, { aufLinie = true, amKnoten = false } = {}) {
  const art = amKnoten ? { kraft: last.art === 'kraft', verteilt: false, einheit: last.art === 'kraft' ? 'kN' : 'kNm' }
    : lastart(last.art);
  const richtungen = amKnoten
    ? katalog().richtungen.filter((x) => katalog().knotenrichtungen.includes(x.wert))
    : katalog().richtungen;
  const wertFeld = amKnoten ? 'wert' : 'wert_a';
  return [
    art.kraft ? wahlBlock('Richtung', wahlSchalter({
      werte: richtungen, gewaehlt: last.richtung, setzen: (w) => setzen('richtung', w),
      titel: 'Positiv in Pfeilrichtung: senkrecht nach unten, quer zur gestrichelten Faser, längs vom Anfang zum Ende',
      klasse: '.ist-wortlaut.ist-umbruch',
    })) : null,
    zeile(art.verteilt ? 'Anfang' : 'Wert', zahlfeld({
      wert: last[wertFeld], schritt: 5,
      titel: art.kraft ? 'Positiv in Pfeilrichtung' : 'Ein Moment positiv im Gegenuhrzeigersinn',
      beiAenderung: (w) => setzen(wertFeld, w),
    }), art.einheit),
    art.verteilt ? zeile('Ende', zahlfeld({
      wert: last.wert_b, schritt: 5, leer: null, platzhalter: 'wie Anfang',
      titel: 'Wert am Ende der Linie -- leer: wie am Anfang', beiAenderung: (w) => setzen('wert_b', w),
    }), art.einheit) : null,
    !art.verteilt && aufLinie ? zeile('Stelle', zahlfeld({
      wert: last.stelle, schritt: 5, min: 0, max: 100,
      titel: 'Wo die Last steht: in % der Linie ab ihrem Anfang', beiAenderung: (w) => setzen('stelle', w),
    }), '%') : null,
    art.verteilt && art.kraft && ['senkrecht', 'waagrecht'].includes(last.richtung) && aufLinie
      ? zeile('projiziert', haken(last.projiziert, (w) => setzen('projiziert', w)),
        'je Meter Projektion statt je Meter Stab') : null,
  ];
}

/** Die Felder für das, was ein Werkzeug als Nächstes anlegt. */
function neuEigenschaften(a, werkzeug) {
  const z = eintragVon(a.bs.kennung);
  const neu = () => a.neuZeichnen();
  let inhalt = [];
  if (werkzeug === 'linie') {
    const v = a.bs.vorgaben.linie;
    inhalt = [
      zeile('Querschnitt', querschnittWahl(z, v.querschnitt, (w) => { v.querschnitt = w; neu(); })),
      v.querschnitt ? zeile('Material', materialWahl(z, v.querschnitt, v.material, (w) => { v.material = w; neu(); })) : null,
    ];
  } else if (werkzeug === 'last') {
    const v = a.bs.vorgaben.last;
    // Der Lastfall steht oben neben «Last»; hier nur, wenn keiner gewählt ist.
    inhalt = [
      aktiverLastfall(a.bs.kennung) ? null : el('p.cad-hinweis-klein', {
        text: 'Kein Lastfall gewählt -- oben neben «Last» einen wählen.',
      }),
      wahlBlock('Art', wahlSchalter({
        werte: katalog().lastarten.map((x) => ({ wert: x.wert, beschriftung: x.beschriftung, titel: `${x.beschriftung} in ${x.einheit}` })),
        gewaehlt: v.art, setzen: (w) => { v.art = w; neu(); }, klasse: '.ist-wortlaut.ist-umbruch',
        titel: 'Verteilt liegt eine Last auf der ganzen Linie; einzeln dort, wo geklickt wird, oder an einem Knoten',
      })),
      ...lastFelder(v, (feld, w) => { v[feld] = w; neu(); }, { aufLinie: false }),
    ];
  }
  return {
    inhalt: [el('div.cad-neu-titel', { text: 'Neu' }), ...inhalt.filter(Boolean)],
    schluessel: JSON.stringify([werkzeug, a.bs.vorgaben, aktiverLastfall(a.bs.kennung)]),
  };
}

function eigenschaften(a) {
  const z = eintragVon(a.bs.kennung);
  const kennungen = [...a.auswahl].map((s) => auswahlTeil(s).kennung);
  const lasten = kennungen.filter((k) => lastVon(z, k));
  const knoten = kennungen.filter((k) => z.knoten.some((x) => x.kennung === k));
  const linien = kennungen.filter((k) => z.linien.some((x) => x.kennung === k));
  const schluessel = JSON.stringify([aktiverLastfall(a.bs.kennung), Boolean(passendeUebersicht(a)), a.bs.bettungOffen]);
  if (lasten.length && lasten.length === kennungen.length) return { ...lastEigenschaften(a, z, lasten), schluessel };
  if ((knoten.length && linien.length) || lasten.length) {
    return {
      titel: `${kennungen.length} gewählt`,
      inhalt: [el('p.cad-hinweis-klein', { text: 'Verschiedenes zugleich -- verschieben mit V, löschen mit Entf.' })],
      schluessel,
    };
  }
  if (knoten.length) return { ...knotenEigenschaften(a, z, knoten), schluessel };
  if (linien.length) return { ...linienEigenschaften(a, z, linien), schluessel };
  return { titel: '', inhalt: [] };
}

function meldungszeilen(a, kennungen) {
  const u = passendeUebersicht(a);
  return (u?.meldungen || []).filter((m) => m.elemente.some((k) => kennungen.includes(k)))
    .map((m) => el(m.fehler ? 'p.cad-meldung' : 'p.cad-hinweis-klein', { text: m.text }));
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

function knotenEigenschaften(a, z, knoten) {
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
  inhalt.push(...lagerFelder(a, z, knoten));
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

/**
 * Die Zugseite der gewählten Linien als Schalter -- solange sie alle
 * senkrecht oder alle nicht senkrecht liegen. Umschalten kehrt eine Linie
 * im Kern um: die Faser wechselt die Seite, die Lasten bleiben, wo sie
 * wirken, und die Gelenke an ihren Knoten.
 */
function zugseitenzeile(a, z, linien) {
  const lagen = a.modell.lagen(z);
  const seiten = new Map(z.linien.filter((l) => linien.includes(l.kennung))
    .map((l) => [l.kennung, zugseite(lagen.get(l.von), lagen.get(l.bis))]));
  const stellungen = [['unten', 'oben'], ['links', 'rechts']]
    .find((paar) => [...seiten.values()].every((s) => paar.includes(s)));
  if (!stellungen) return null;
  const verschieden = new Set(seiten.values()).size > 1;
  return schalterzeile('Zugseite', wahlSchalter({
    werte: stellungen.map((s) => ({ wert: s, beschriftung: s })),
    gewaehlt: verschieden ? '' : [...seiten.values()][0],
    titel: 'Die gestrichelte Faser: dort zieht ein positives Moment',
    setzen: (w) => kernBearbeiten(a, [{
      aktion: 'umkehren', linien: linien.filter((k) => seiten.get(k) !== w),
    }], linien),
  }));
}

/**
 * Eine Linie: Querschnitt -- «kein Stab» heisst nur eine Linie --, beim
 * Stab das Material, die Zugseite und die Gelenke. Die Bettung steht
 * eingeklappt darunter: sie braucht man selten (Benutzer, 2026-10-23).
 */
function linienEigenschaften(a, z, linien) {
  const e = z.linien.find((x) => x.kennung === linien[0]);
  const setzen = (feld) => (wert) => a.aendern((zz) => {
    for (const l of zz.linien) {
      if (!linien.includes(l.kennung)) continue;
      l[feld] = wert;
      // Ein neuer Stab bekommt das Material, das das Werkzeug vorgibt -- sonst fehlte es ihm.
      if (feld === 'querschnitt' && wert && !l.material) l.material = a.bs.vorgaben.linie.material;
    }
  });
  const inhalt = [zeile('Querschnitt', querschnittWahl(z, e.querschnitt, setzen('querschnitt')))];
  if (e.querschnitt) {
    inhalt.push(
      zeile('Material', materialWahl(z, e.querschnitt, e.material, setzen('material'))),
      zugseitenzeile(a, z, linien),
      zeile('Gelenk Anfang', haken(e.gelenk_anfang, setzen('gelenk_anfang'), 'Kein Moment am Anfang')),
      zeile('Gelenk Ende', haken(e.gelenk_ende, setzen('gelenk_ende'), 'Kein Moment am Ende')),
    );
  }
  const gebettet = e.quer !== 'frei' || e.laengs !== 'frei';
  inhalt.push(el('button.cad-aufklapper', {
    type: 'button', text: `${a.bs.bettungOffen ? '▾' : '▸'} Bettung${gebettet ? ' · gesetzt' : ''}`,
    title: 'Linienlager quer und längs: fest oder gebettet',
    on: { click: () => { a.bs.bettungOffen = !a.bs.bettungOffen; a.neuZeichnen(); } },
  }));
  if (a.bs.bettungOffen) inhalt.push(...lagerAnLinie(a, linien, e));
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

// -- Lasten ------------------------------------------------------------------

/**
 * Eine gewählte Last: ihr Lastfall und ihre Felder. Ändert man den
 * Lastfall, zeigt die Zeichnung danach dessen Lasten -- sonst
 * verschwände die Last unter dem Zeiger.
 */
function lastEigenschaften(a, z, kennungen) {
  if (kennungen.length > 1) {
    return {
      titel: `${kennungen.length} Lasten`,
      inhalt: [el('p.cad-hinweis-klein', { text: 'Mehrere Lasten -- einzeln bearbeiten, löschen mit Entf.' })],
    };
  }
  const [kennung] = kennungen;
  const da = lastVon(z, kennung);
  const amKnoten = Boolean(da.knoten);
  const setzen = (feld, wert) => a.aendern((zz) => {
    const neu = lastVon(zz, kennung);
    if (neu) neu.last[feld] = wert;
  });
  const art = amKnoten ? (da.last.art === 'moment' ? 'Moment' : 'Kraft') : lastart(da.last.art).beschriftung;
  return {
    titel: `${elementname(a, kennung)} · ${art}`,
    inhalt: [
      lastfallWahl(a, z, da.last.lastfall, (w) => {
        setzen('lastfall', w);
        lastfallWaehlen(a.bs.kennung, w);
      }, 'Zu welchem Lastfall die Last gehört'),
      ...lastFelder(da.last, setzen, { amKnoten }),
      el('p.cad-info', { text: amKnoten ? `an ${da.knoten}` : `auf ${elementname(a, da.linie.kennung)}` }),
      ...meldungszeilen(a, [kennung]),
    ].filter(Boolean),
  };
}
