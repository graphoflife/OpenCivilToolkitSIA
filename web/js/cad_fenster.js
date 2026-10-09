/**
 * cad_fenster.js -- das Zeichenfenster: Rahmen, Knöpfe, Tasten, Rückgängig.
 *
 * Allgemein gebaut: was gezeichnet wird, sagt eine App über ihren «Adapter»
 * (für den Querschnitt `qa_zeichnung.js`). Das Fenster kennt nur Knoten und
 * Elemente in drei Formen -- Punkt, Linie, Fläche -- und die Mechanik, mit
 * der man sie zeichnet, wählt und ändert. Ein Grundriss bekäme einen anderen
 * Adapter und dasselbe Fenster.
 *
 * WENIGE KNÖPFE:
 * Oben stehen Polygon P, Linie L, Knoten K und, wenn die App welche hat,
 * Vorlagen T. Dazu Rückgängig, Wiederholen, «Alles zeigen» F und Vollbild.
 * Einen Knopf zum Wählen gibt es nicht: Wählen ist der Grundzustand, Esc
 * führt dorthin zurück. Alles Weitere steht neben der Auswahl oder im
 * schwebenden Fenster.
 *
 * EIN BLEIBENDES FENSTER:
 * Die Tafel wird nach jeder Änderung neu gebaut, das Fenster nicht -- es
 * entsteht einmal je Zeichnung und wird jedes Mal wieder eingehängt. Ein
 * halb gezeichnetes Polygon, der Massstab und «Rückgängig» überstehen so
 * jede Rechnung, die zwischendurch fertig wird.
 *
 * ZWEI EBENEN:
 * Das Modell wird nur gezeichnet, wenn es sich ändert oder die Ansicht
 * wandert. Zeiger, Fangzeichen und Vorschau liegen darüber und folgen der
 * Maus -- je Bild einmal, nicht je Ereignis.
 */

import {
  ansichtNeu, einpassen, nachBild, pfad, rasterZeichnen, zahlText, zoomen,
} from './cad_ansicht.js';
import { abstand, auswahlTeil, cadModell } from './cad_modell.js';
import {
  eingabeLeeren, eingabeNeu, fangen, feldnamen, felderLeeren, getipptPunkt, hilfenZeichnen, hilfstext,
  klickPunkt, taste as eingabeTaste,
} from './cad_eingabe.js';
import {
  knotenBefehl, knotenEinfuegenBefehl, kopierenBefehl, linienBefehl, polygonBefehl,
  verschiebenBefehl,
} from './cad_befehle.js';
import { klickWaehlen, leisteZeichnen, rahmenWaehlen, treffer } from './cad_auswahl.js';
import { paletteBauen } from './cad_palette.js';
import { el, svgEl } from './dom.js';

/** Die Raster, die zur Wahl stehen. */
const RASTER = [1, 5, 10, 25, 50, 100];
/** Ab wie viel Bewegung ein Druck ein Ziehen ist und kein Klick -- px. */
const ZITTERN = 4;
/** Wie viele Schritte «Rückgängig» zurückreicht. */
const VERLAUF = 100;
/** Unter diesem Schlüssel merkt sich der Browser die Höhe der Zeichnung. */
const HOEHE = 'opencivil.cad.hoehe';

const WERKZEUGE = [
  { name: 'polygon', zeichen: '▱', text: 'Polygon', taste: 'p', bauen: polygonBefehl },
  { name: 'linie', zeichen: '╱', text: 'Linie', taste: 'l', bauen: linienBefehl },
  { name: 'knoten', zeichen: '•', text: 'Knoten', taste: 'k', bauen: knotenBefehl },
];

/** Schlüssel -> Fenster. Keine Projektdaten: nichts davon wird abgelegt. */
const fenster = new Map();

/** Das Fenster, das gerade Tasten und das Mausrad bekommt -- das zuletzt angeklickte. */
let aktive = null;

/**
 * Das Fenster zu `schluessel` -- gebaut beim ersten Mal. `adapterBauen`
 * liefert den Adapter der App; gilt er nicht mehr (ein anderes Projekt ist
 * offen), entsteht das Fenster neu.
 */
export function cadFenster(schluessel, adapterBauen) {
  let a = fenster.get(schluessel);
  if (a && !a.adapter.gilt()) {
    abbauen(a);
    a = null;
  }
  if (!a) {
    a = neu(adapterBauen());
    fenster.set(schluessel, a);
  }
  return a;
}

/** Für eine neu angelegte Zeichnung: nichts von einer früheren mit demselben Schlüssel. */
export function cadVergessen(schluessel) {
  const a = fenster.get(schluessel);
  if (a) abbauen(a);
  fenster.delete(schluessel);
}

/** Ein Fenster, das nicht mehr gebraucht wird: seine Hörer am Browserfenster und sein Beobachter gehen mit. */
function abbauen(a) {
  if (aktive === a) aktive = null;
  a.abbruch.abort();
  a.beobachter.disconnect();
}

function neu(adapter) {
  const a = {
    adapter,
    modell: cadModell(adapter),
    listen: ['knoten', ...adapter.arten.map((x) => x.liste)],
    v: ansichtNeu(),
    raster: 10,
    fang: true,
    befehl: null,
    auswahl: new Set(),
    eingabe: eingabeNeu(),
    zeiger: null,
    druck: null,
    finger: new Map(),
    kneifen: null,
    leertaste: false,
    rueck: [],
    vor: [],
    version: 0,
    stand: null,
    vollbild: false,
    einpassen: false,
    letzterKlick: null,
    knoten: null,
    teile: null,
    bildUhr: null,
    dialog: null,        // ein Fenster der App in der Zeichnung, etwa die Vorlagen: {schliessen}
  };
  a.aendern = (veraenderer, optionen) => aendern(a, veraenderer, optionen);
  a.ende = () => befehlEnde(a);
  a.aktionen = () => aktionen(a);
  a.starten = (befehl) => starten(a, befehl);
  a.neuZeichnen = () => zeichnen(a);
  bauen(a);
  return a;
}

// ===========================================================================
// Ändern und Rückgängig
// ===========================================================================

/** Die Zeichnung als Text: die Listen, sonst nichts. */
function stand(a) {
  const z = a.adapter.zeichnung();
  return JSON.stringify(a.listen.map((l) => z?.[l] || []));
}

/**
 * Ändert die Zeichnung und merkt sich den Stand davor -- ein Schritt für
 * «Rückgängig». `auswahl` liefert nach der Änderung, was danach gewählt sein
 * soll (etwa das eben angelegte Element); gesetzt wird es noch, bevor die
 * Tafel neu gezeichnet wird.
 */
function aendern(a, veraenderer, { auswahl = null } = {}) {
  const vorher = stand(a);
  const vorherAuswahl = [...a.auswahl];
  const vor = a.vor;
  a.vor = [];
  a.adapter.schreiben((z) => {
    for (const l of a.listen) z[l] = z[l] || [];
    veraenderer(z);
    if (auswahl) a.auswahl = new Set((auswahl() || []).filter(Boolean));
  });
  if (stand(a) === vorher) {
    a.vor = vor;
    return;
  }
  a.rueck.push({ stand: vorher, auswahl: vorherAuswahl });
  if (a.rueck.length > VERLAUF) a.rueck.shift();
  aktualisieren(a);
}

function standSetzen(a, eintrag) {
  const werte = JSON.parse(eintrag.stand);
  a.auswahl = new Set(eintrag.auswahl);
  a.adapter.schreiben((z) => { a.listen.forEach((l, i) => { z[l] = werte[i]; }); });
  aktualisieren(a);
}

function zurueck(a) {
  if (!a.rueck.length) return;
  a.vor.push({ stand: stand(a), auswahl: [...a.auswahl] });
  standSetzen(a, a.rueck.pop());
}

function vorwaerts(a) {
  if (!a.vor.length) return;
  a.rueck.push({ stand: stand(a), auswahl: [...a.auswahl] });
  standSetzen(a, a.vor.pop());
}

/**
 * Die Zeichnung hat sich geändert -- von hier oder von aussen (Rückgängig,
 * eine geladene Datei): Fang neu sammeln, verschwundene Auswahl weg, die App
 * fragen lassen, was der Kern dazu sagt.
 */
function aktualisieren(a) {
  const jetzt = stand(a);
  if (jetzt !== a.stand) {
    a.stand = jetzt;
    a.version += 1;
    const z = a.adapter.zeichnung() || {};
    a.auswahl = new Set([...a.auswahl].filter((k) => a.modell.gibt(z, k)));
    a.adapter.geaendert?.(a);
  }
  zeichnen(a);
}

function loeschen(a) {
  if (!a.auswahl.size) return;
  const weg = new Set(a.auswahl);
  aendern(a, (z) => a.modell.loeschen(z, weg), { auswahl: () => [] });
}

// ===========================================================================
// Befehle
// ===========================================================================

function starten(a, befehl) {
  a.dialog?.schliessen();
  a.befehl = befehl;
  eingabeLeeren(a.eingabe);
  a.eingabe.bezug = null;
  a.letzterKlick = null;
  zeichnen(a);
}

function befehlEnde(a) {
  a.befehl = null;
  eingabeLeeren(a.eingabe);
  zeichnen(a);
}

/** Ein fertiger Punkt geht an den Befehl; danach sind die Hilfen wieder frei. */
function punktLiefern(a, erg) {
  const befehl = a.befehl;
  if (!befehl) return;
  befehl.punkt(a, erg);
  eingabeLeeren(a.eingabe);
  zeichnen(a);
}

/** Ändert jedes gewählte Element einer Form -- ein Schritt für Rückgängig. */
function jedesGewaehlte(a, form, tun) {
  const auswahl = new Set(a.auswahl);
  const neu = [];
  aendern(a, (z) => {
    for (const { art, e } of [...a.modell.elemente(z)]) {
      if (auswahl.has(e.kennung) && art.form === form) neu.push(tun(z, art, e));
    }
  }, { auswahl: () => [...auswahl, ...neu] });
}

/** Teilt jede gewählte Linie in der Mitte. */
function teilen(a) {
  jedesGewaehlte(a, 'linie', (z, art, e) => {
    const lagen = a.modell.lagen(z);
    const [p, q] = [lagen.get(e.von), lagen.get(e.bis)];
    return p && q ? a.modell.linieTeilen(z, art, e, [(p[0] + q[0]) / 2, (p[1] + q[1]) / 2]) : null;
  });
}

/** Gibt es etwas zu kopieren -- ein ganzes Element oder einen Knoten? Einzelne Ecken kopiert es nicht. */
function kopierbar(a) {
  return [...a.auswahl].some((s) => auswahlTeil(s).i === null);
}

/**
 * Was neben einer Auswahl angeboten wird -- nur, was für sie geht: erst das
 * Allgemeine, dann das der App, zuletzt Löschen.
 */
function aktionen(a) {
  const z = a.adapter.zeichnung();
  const m = a.modell;
  const gewaehlt = [...m.elemente(z)].filter(({ e }) => a.auswahl.has(e.kennung));
  const nurLinien = gewaehlt.length > 0 && gewaehlt.length === a.auswahl.size
    && gewaehlt.every(({ art }) => art.form === 'linie');
  const einzeln = gewaehlt.length === 1 && a.auswahl.size === 1 ? gewaehlt[0] : null;
  const teilbar = (x) => x.art.form === 'flaeche' || (x.art.form === 'linie' && x.art.teilbar !== false);
  return [
    { zeichen: '⇢', text: 'Verschieben', taste: 'V', tun: () => starten(a, verschiebenBefehl()) },
    kopierbar(a) ? { zeichen: '⧉', text: 'Kopieren', taste: 'C', tun: () => starten(a, kopierenBefehl()) } : null,
    nurLinien && gewaehlt.every(teilbar) ? {
      zeichen: '⫶', text: 'Teilen', titel: 'In der Mitte teilen: zwei Linien mit denselben Eigenschaften',
      tun: () => teilen(a),
    } : null,
    einzeln && teilbar(einzeln) ? {
      zeichen: '+', text: 'Knoten', titel: 'Einen Knoten in eine Kante einfügen',
      tun: () => starten(a, knotenEinfuegenBefehl(einzeln.e.kennung)),
    } : null,
    nurLinien ? {
      zeichen: '⇄', text: 'Umkehren', titel: 'Anfang und Ende tauschen',
      tun: () => jedesGewaehlte(a, 'linie', (zz, art, e) => { m.umkehren(art, e); }),
    } : null,
    ...(a.adapter.aktionen?.(a) || []),
    { zeichen: '✕', text: 'Löschen', taste: 'Entf', tun: () => loeschen(a) },
  ].filter(Boolean);
}

// ===========================================================================
// Zeichnen
// ===========================================================================

/**
 * Passt alles ins Bild -- und lässt dabei die Ecke frei, in der das
 * schwebende Fenster steht: daneben oder darüber, je nachdem, was weniger
 * Massstab kostet. So liegt nach «Alles zeigen» nichts darunter.
 */
function allesZeigen(a) {
  const umriss = a.adapter.umriss(a);
  const pal = a.teile.palette.knoten;
  let frei = [0, 0];
  if (pal.offsetWidth && a.v.breite) {
    const breit = a.v.breite - pal.offsetLeft;
    const hoch = a.v.hoehe - pal.offsetTop;
    const massstab = (f) => {
      einpassen(a.v, umriss, { frei: f });
      return a.v.massstab;
    };
    frei = massstab([breit, 0]) >= massstab([0, hoch]) ? [breit, 0] : [0, hoch];
  }
  einpassen(a.v, umriss, { frei });
  zeichnen(a);
}

/**
 * Die Auswahl, hervorgehoben: über dem Modell, unter dem Zeiger. Eine
 * gewählte Ecke als volles Quadrat, und dünn gestrichelt das Element, dem
 * sie gehört -- so sieht man, wessen Ecke es ist, wo mehrere aufeinander
 * liegen.
 */
function hervorheben(a, kennungen, klasse) {
  const g = svgEl('g', { class: klasse });
  if (!kennungen.size) return g;
  const z = a.adapter.zeichnung();
  const m = a.modell;
  const lagen = m.lagen(z);
  const quadrat = (p, extra = '') => {
    const [x, y] = nachBild(a.v, p);
    return svgEl('rect', { x: x - 4.5, y: y - 4.5, width: 9, height: 9, class: extra });
  };
  for (const k of z.knoten || []) if (kennungen.has(k.kennung)) g.append(quadrat(m.lage(k)));
  const eigner = new Set();
  for (const x of m.ecken(z)) {
    const p = lagen.get(x.knoten);
    if (!p || x.art.form === 'punkt' || !kennungen.has(x.schluessel)) continue;
    g.append(quadrat(p, 'cad-ecke'));
    eigner.add(x.e.kennung);
  }
  for (const { art, e } of m.elemente(z)) {
    const ganz = kennungen.has(e.kennung);
    if (!ganz && !eigner.has(e.kennung)) continue;
    const orte = m.verweise(art, e).map((k) => lagen.get(k));
    if (orte.some((p) => !p)) continue;
    if (!ganz) {
      g.prepend(svgEl('path', { d: pfad(a.v, orte, art.form === 'flaeche'), class: 'cad-eigner' }));
      continue;
    }
    if (art.form === 'punkt') {
      const [x, y] = nachBild(a.v, orte[0]);
      const r = Math.max(5, (a.adapter.trefferradius?.(art, e) || 0) * a.v.massstab + 3);
      g.append(svgEl('circle', { cx: x, cy: y, r }));
    } else {
      g.append(svgEl('path', { d: pfad(a.v, orte, art.form === 'flaeche') }));
    }
  }
  return g;
}

/** Die Knoten: klein, damit sie die Zeichnung nicht zudecken -- aber treffbar. */
function knotenZeichnen(a) {
  const g = svgEl('g', { class: 'cad-knotenpunkte' });
  const z = a.adapter.zeichnung();
  for (const k of z.knoten || []) {
    const [x, y] = nachBild(a.v, a.modell.lage(k));
    g.append(svgEl('circle', { cx: x.toFixed(1), cy: y.toFixed(1), r: 2 }));
  }
  return g;
}

/** Das Modell: Raster, die Elemente der App, Knoten, Auswahl. */
function zeichnen(a) {
  if (!a.knoten) return;
  const z = a.adapter.zeichnung();
  if (!z) return;
  // Noch nie gemessen, aber schon eingehängt: jetzt messen -- in einem
  // verborgenen Reiter meldet sich der Beobachter sonst nie.
  if (!a.v.breite && a.knoten.isConnected) {
    groesseMessen(a);
    return;
  }
  knoepfeZeichnen(a);
  if (!a.v.massstab || !a.v.breite) return;
  const app = svgEl('g');
  a.adapter.zeichnen(a, app);
  a.teile.modell.replaceChildren(
    rasterZeichnen(a.v, a.raster, a.adapter.achsen),
    app,
    knotenZeichnen(a),
    hervorheben(a, a.auswahl, 'cad-auswahl'),
  );
  obenZeichnen(a);
  // Erst das schwebende Fenster: die Leiste weicht ihm aus, in seiner neuen Grösse.
  paletteZeichnen(a);
  leisteZeichnen(a);
  statusZeichnen(a);
  a.adapter.gezeichnet?.(a);
}

/** Die obere Ebene: Hervorhebung unter dem Zeiger, Vorschau, Hilfen, Rahmen. */
function obenZeichnen(a) {
  if (!a.teile) return;
  const g = svgEl('g');
  if (!a.befehl && a.zeiger?.bild && !a.druck) {
    const unter = treffer(a, a.zeiger.bild)[0];
    if (unter && !a.auswahl.has(unter)) g.append(hervorheben(a, new Set([unter]), 'cad-unter'));
  }
  if (a.befehl) a.befehl.vorschau(a, g);
  hilfenZeichnen(a, g);
  const r = a.druck?.rahmen;
  if (r) {
    const [x0, y0] = a.druck.start;
    const [x1, y1] = r;
    g.append(svgEl('rect', {
      x: Math.min(x0, x1), y: Math.min(y0, y1), width: Math.abs(x1 - x0), height: Math.abs(y1 - y0),
      class: x1 >= x0 ? 'cad-rahmen' : 'cad-rahmen ist-kreuzend',
    }));
  }
  a.teile.oben.replaceChildren(g);
  lageZeichnen(a);
}

/** Je Bild einmal: der Zeiger bewegt sich öfter, als der Schirm zeichnet. */
function obenBald(a) {
  if (a.bildUhr) return;
  a.bildUhr = requestAnimationFrame(() => {
    a.bildUhr = null;
    obenZeichnen(a);
  });
}

// ===========================================================================
// Schwebendes Fenster, Knöpfe, Statuszeile
// ===========================================================================

/** Die Koordinaten des Zeigers -- in der Ruhe oben im schwebenden Fenster. */
function lageZeichnen(a) {
  const ziel = a.teile.lage;
  if (!ziel) return;
  const f = a.zeiger?.fang || (a.zeiger?.bild && fangen(a, a.zeiger.bild));
  const [x, y] = a.adapter.achsen;
  ziel.textContent = f ? `${x} ${zahlText(f.p[0])}   ${y} ${zahlText(f.p[1])}` : '';
}

/** Ein Feld der Punkteingabe: schmal, rechtsbündig, ohne Pfeile. */
function eingabefeld(a, i, name) {
  const feld = el('input.cad-eingabe', {
    type: 'text', inputMode: 'decimal', value: a.eingabe.felder[i], placeholder: name,
    title: name, autocomplete: 'off',
    on: {
      input: (e) => { a.eingabe.felder[i] = e.target.value; },
      keydown: (e) => {
        // Buchstaben gehören den Hilfen, auch wenn ein Feld den Fokus hat.
        if (e.key.length === 1 && /[a-zA-Z]/.test(e.key) && !e.ctrlKey && !e.metaKey) {
          if (eingabeTaste(a, e)) {
            e.preventDefault();
            zeichnen(a);
          }
        }
      },
    },
  });
  feld.dataset.feld = String(i);
  return feld;
}

function hilfsknopf(a, zeichen, titel, tun, an = false) {
  return el('button.cad-hilfe', {
    type: 'button', title: titel, class: an ? 'ist-an' : '',
    on: { click: (e) => { e.preventDefault(); tun(); zeichnen(a); } },
  }, [zeichen]);
}

/** Der Teil des Fensters, der während eines Befehls nach dem Punkt fragt. */
function punkteingabe(a) {
  const pe = a.eingabe;
  const [n1, n2] = feldnamen(a);
  const modus = (wert, text, titel) => el('button.schalter-halb', {
    type: 'button', text, title: titel, class: pe.modus === wert ? 'ist-an' : '',
    on: { click: () => { pe.modus = wert; felderLeeren(pe); zeichnen(a); } },
  });
  const [x, y] = a.adapter.achsen;
  const fake = (k) => ({ key: k, preventDefault() {} });
  return [
    pe.bindung
      ? el('div.cad-bindung-zeile', {}, [
        el('span.cad-bindungsmarke', { text: pe.bindung.text }),
        el('button.weg', {
          type: 'button', text: '×', title: 'Bindung lösen (Esc)',
          on: { click: () => { pe.bindung = null; zeichnen(a); } },
        }),
      ])
      : el('span.schalter.cad-modus', {}, [
        modus('rel', 'Δ', 'Relativ zum Bezugspunkt'),
        modus('abs', 'abs', 'Absolut'),
        modus('polar', 'L∠', 'Länge und Winkel ab dem Bezugspunkt'),
      ]),
    el('div.cad-felder', {}, [
      eingabefeld(a, 0, n1),
      n2 ? eingabefeld(a, 1, n2) : null,
      el('button.knopf.knopf-klein', {
        type: 'button', text: '↵', title: 'Punkt setzen (Enter)',
        on: { click: () => getipptLiefern(a) },
      }),
    ]),
    el('div.cad-hilfen', {}, [
      hilfsknopf(a, 'R', 'Bezugspunkt auf den gefangenen Punkt (R)', () => eingabeTaste(a, fake('r'))),
      hilfsknopf(a, x.toUpperCase(), `Entlang ${x} (${x.toUpperCase()})`, () => eingabeTaste(a, fake(x)),
        pe.bindung?.art === 'achse' && pe.bindung.r[0] === 1),
      hilfsknopf(a, y.toUpperCase(), `Entlang ${y} (${y.toUpperCase()})`, () => eingabeTaste(a, fake(y)),
        pe.bindung?.art === 'achse' && pe.bindung.r[1] === 1),
      hilfsknopf(a, '∥', 'Parallel zu einer Linie (P)', () => eingabeTaste(a, fake('p')),
        pe.warten === 'parallel' || pe.bindung?.art === 'parallel'),
      hilfsknopf(a, '⊥', 'Senkrecht zu einer Linie (S)', () => eingabeTaste(a, fake('s')),
        pe.warten === 'senkrecht' || pe.bindung?.art === 'senkrecht'),
      hilfsknopf(a, 'M', 'Mitte zweier Punkte (M)', () => eingabeTaste(a, fake('m')),
        pe.warten?.art === 'mitte'),
    ]),
    a.befehl?.kopie ? el('label.cad-zeile', {}, [
      el('span', { text: 'Anzahl' }),
      el('input', {
        type: 'number', min: 1, step: 1, value: a.befehl.anzahl,
        on: { input: (e) => { a.befehl.anzahl = Number(e.target.value) || 1; obenBald(a); } },
      }),
    ]) : null,
  ];
}

/**
 * Das schwebende Fenster. Neu gebaut wird sein Inhalt nur, wenn sich die
 * Lage ändert -- nicht bei jeder Zeigerbewegung, sonst verlöre ein Feld beim
 * Tippen den Fokus.
 */
function paletteZeichnen(a) {
  const pal = a.teile.palette;
  if (a.befehl) {
    const pe = a.eingabe;
    const neuTeil = a.befehl.neu ? a.adapter.neuEigenschaften?.(a, a.befehl.neu) : null;
    const schluessel = JSON.stringify([
      'befehl', a.befehl.name, pe.modus, pe.runde, pe.bindung?.text, pe.warten?.art || pe.warten,
      a.befehl.kopie ? a.befehl.anzahl : null, neuTeil?.schluessel ?? null,
    ]);
    pal.setzen(hilfstext(a) || a.befehl.frage(a), [
      ...punkteingabe(a),
      neuTeil ? el('div.cad-neu', {}, neuTeil.inhalt) : null,
    ], schluessel);
    return;
  }
  if (a.auswahl.size) {
    const teil = a.adapter.eigenschaften(a);
    pal.setzen(teil.titel, teil.inhalt, JSON.stringify(['auswahl', a.version, [...a.auswahl], teil.schluessel ?? null]));
    return;
  }
  const raster = el('select.cad-raster', {
    title: 'Raster: daran fängt der Zeiger',
    on: { change: (e) => { a.raster = Number(e.target.value); zeichnen(a); } },
  }, RASTER.map((r) => el('option', { value: r, text: `${r} mm`, selected: r === a.raster })));
  const fang = el('input', {
    type: 'checkbox', checked: a.fang, title: 'Fang an Knoten, Linien und Raster (Alt hält ihn an)',
    on: { change: (e) => { a.fang = e.target.checked; zeichnen(a); } },
  });
  a.teile.lage = el('span.cad-lage');
  pal.setzen('Zeiger', [
    a.teile.lage,
    el('div.cad-ruhe', {}, [
      el('label', {}, ['Raster ', raster]),
      el('label', {}, [fang, ' Fang']),
    ]),
  ], JSON.stringify(['ruhe', a.raster, a.fang]));
  if (!a.teile.lage.isConnected) a.teile.lage = pal.koerper.querySelector('.cad-lage');
  lageZeichnen(a);
}

function statusZeichnen(a) {
  let satz;
  if (a.befehl) {
    satz = `${a.befehl.hinweis ? `${a.befehl.hinweis} · ` : ''}R Bezugspunkt · Y/Z Achse · `
      + 'P/S parallel/senkrecht · M Mitte · Ziffern tippen · Esc zurück';
  } else if (a.auswahl.size) {
    satz = 'V verschieben · C kopieren · Entf löschen · Shift+Klick nimmt dazu · Esc wählt ab';
  } else {
    satz = 'Klick wählt, noch ein Klick das darunter · Rahmen ziehen wählt mehrere · Mausrad zoomt';
  }
  a.teile.hinweis.textContent = a.kurzhinweis || satz;
}

/** Einen Satz kurz in die Statuszeile -- etwa, warum das Mausrad nicht zoomt. */
function kurzMelden(a, satz) {
  a.kurzhinweis = satz;
  clearTimeout(a.kurzUhr);
  a.kurzUhr = setTimeout(() => { a.kurzhinweis = ''; statusZeichnen(a); }, 2600);
  statusZeichnen(a);
}

function knopf(zeichen, beschriftung, titel, tun, klasse = '') {
  return el('button.cad-knopf', {
    type: 'button', title: titel, class: klasse,
    on: { click: (e) => { e.preventDefault(); tun(); } },
  }, [el('span.cad-zeichen', { text: zeichen }), beschriftung ? el('span.cad-text', { text: beschriftung }) : null]);
}

function vollbildSetzen(a, an) {
  a.vollbild = an;
  a.einpassen = true;
  // Das Bild springt unter dem Zeiger weg: was er zuletzt traf, gilt nicht mehr.
  a.zeiger = null;
  a.adapter.tafelNeu();
}

function leisteBauen(a) {
  const werkzeuge = WERKZEUGE.map((w) => {
    const k = knopf(w.zeichen, w.text, `${w.text} (${w.taste.toUpperCase()})`, () => starten(a, w.bauen()));
    k.dataset.werkzeug = w.name;
    return k;
  });
  const vorlage = a.adapter.vorlageOeffnen
    ? knopf('⊞', 'Vorlage', 'Querschnitt aus einer Vorlage (T)', () => a.adapter.vorlageOeffnen(a))
    : null;
  const rueck = knopf('↶', '', 'Rückgängig (Strg+Z)', () => zurueck(a));
  const vor = knopf('↷', '', 'Wiederholen (Strg+Y)', () => vorwaerts(a));
  const alles = knopf('⤧', 'Alles', 'Alles zeigen (F)', () => allesZeigen(a), 'ist-ansicht');
  const gross = knopf('⤢', 'Vollbild', 'Vollbild ein/aus', () => vollbildSetzen(a, !a.vollbild), 'ist-ansicht');
  a.teile.knoepfe = { werkzeuge, rueck, vor, gross };
  return [
    ...werkzeuge, vorlage, el('span.cad-trenner'), rueck, vor,
    el('span.cad-luecke'), alles, gross,
  ];
}

function knoepfeZeichnen(a) {
  const k = a.teile.knoepfe;
  for (const w of k.werkzeuge) w.classList.toggle('ist-an', w.dataset.werkzeug === a.befehl?.name);
  k.rueck.disabled = !a.rueck.length;
  k.vor.disabled = !a.vor.length;
  k.gross.classList.toggle('ist-an', a.vollbild);
  k.gross.querySelector('.cad-text').textContent = a.vollbild ? 'Zurück' : 'Vollbild';
  a.teile.bild.classList.toggle('ist-befehl', !!a.befehl);
}

// ===========================================================================
// Bedienen
// ===========================================================================

function bildlage(a, e) {
  const r = a.teile.bild.getBoundingClientRect();
  return [e.clientX - r.left, e.clientY - r.top];
}

/** Die getippten Werte als Punkt -- oder, ohne, das Enter des Befehls. */
function getipptLiefern(a) {
  const erg = getipptPunkt(a);
  if (erg?.fehler) {
    kurzMelden(a, erg.fehler);
    return;
  }
  if (erg) {
    // Der Fokus geht an die Zeichnung zurück: Strg+Z und die Buchstaben
    // gelten wieder ihr. Die nächste Ziffer holt ihn ins Feld.
    if (document.activeElement?.closest?.('.cad-palette')) document.activeElement.blur();
    punktLiefern(a, erg);
    return;
  }
  if (a.befehl && !a.befehl.enter(a)) befehlEnde(a);
  zeichnen(a);
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
        massstab: a.v.massstab, ursprung: [...a.v.ursprung],
      };
      a.druck = null;
      return;
    }
    if (a.finger.size > 2) return;
  }
  if (a.druck || !a.v.massstab) return;
  const schieben = e.button === 1 || (e.button === 0 && a.leertaste);
  if (e.button !== 0 && !schieben) return;
  if (e.button === 1) e.preventDefault();
  // Ein Feld im schwebenden Fenster gibt seinen Fokus ab: der Klick gehört der Zeichnung.
  if (document.activeElement?.closest?.('.cad-palette')) document.activeElement.blur();
  a.druck = {
    id: e.pointerId, start: bild, ursprung: [...a.v.ursprung], schieben, bewegt: false,
    beruehrung: e.pointerType === 'touch', rahmen: null,
  };
}

function bewegen(a, e) {
  const bild = bildlage(a, e);
  if (a.kneifen && a.finger.has(e.pointerId)) {
    a.finger.set(e.pointerId, bild);
    if (a.finger.size < 2) return;
    const [p, q] = [...a.finger.values()];
    const k = a.kneifen;
    const mitte = [(p[0] + q[0]) / 2, (p[1] + q[1]) / 2];
    a.v.massstab = k.massstab;
    a.v.ursprung = [k.ursprung[0] + mitte[0] - k.mitte[0], k.ursprung[1] + mitte[1] - k.mitte[1]];
    zoomen(a.v, (abstand(p, q) || 1) / k.abstand, mitte);
    zeichnen(a);
    return;
  }
  const d = a.druck;
  a.zeiger = { bild, fang: a.befehl ? fangen(a, bild, { frei: e.altKey, gerade: e.shiftKey }) : null };
  if (!d) {
    obenBald(a);
    return;
  }
  if (e.pointerId !== d.id) return;
  if (!d.bewegt && abstand(bild, d.start) < ZITTERN) return;
  d.bewegt = true;
  // Mit der Maus auf leerer Fläche ohne Befehl: ein Rahmen. Sonst: die Ansicht schieben.
  if (!d.schieben && !a.befehl && !d.beruehrung) {
    d.rahmen = bild;
    obenBald(a);
    return;
  }
  a.v.ursprung = [d.ursprung[0] + bild[0] - d.start[0], d.ursprung[1] + bild[1] - d.start[1]];
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
  if (d.rahmen) {
    rahmenWaehlen(a, d.start, d.rahmen, e.shiftKey);
    zeichnen(a);
    return;
  }
  if (d.bewegt || d.schieben) {
    zeichnen(a);
    return;
  }
  if (a.befehl) {
    const erg = klickPunkt(a, bild, e);
    if (erg) punktLiefern(a, erg);
    else zeichnen(a);
    return;
  }
  klickWaehlen(a, bild, e);
  zeichnen(a);
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
  zoomen(a.v, Math.exp(-e.deltaY * zeilen * 0.0015), bildlage(a, e));
  zeichnen(a);
}

/** Die Tasten des aktiven Fensters. */
function taste(e) {
  const a = aktive;
  if (!a || !a.knoten?.isConnected) return;
  if (e.key === 'Escape' && a.dialog) {
    e.preventDefault();
    a.dialog.schliessen();
    return;
  }
  const imFeld = e.target.closest?.('input, select, textarea, [contenteditable]');
  const inPalette = e.target.closest?.('.cad-palette');
  if (imFeld && !inPalette) return;
  if ((e.key === 'Enter' || e.key === ' ') && e.target.closest?.('button')) return;
  const strg = e.ctrlKey || e.metaKey;
  const k = e.key.length === 1 ? e.key.toLowerCase() : e.key;

  if (strg && (k === 'z' || k === 'y') && !imFeld) {
    e.preventDefault();
    if (k === 'y' || e.shiftKey) vorwaerts(a); else zurueck(a);
    return;
  }
  if (strg || e.altKey) return;

  if (a.befehl) {
    if (k === 'Enter') {
      e.preventDefault();
      getipptLiefern(a);
      return;
    }
    if (k === 'Escape') {
      e.preventDefault();
      if (!eingabeTaste(a, e) && !a.befehl.zurueck(a)) befehlEnde(a);
      if (imFeld) e.target.blur();
      zeichnen(a);
      return;
    }
    if (imFeld) return;
    if (k === 'Backspace') {
      e.preventDefault();
      a.befehl.rueckschritt?.(a);
      zeichnen(a);
      return;
    }
    if (eingabeTaste(a, e)) {
      e.preventDefault();
      zeichnen(a);
      return;
    }
    // Ziffern gehen ins erste Feld -- das Zeichen selbst landet dort. Ist
    // das schwebende Fenster zu, geht es dafür auf.
    if (/^[0-9.,-]$/.test(e.key)) {
      a.teile.palette.aufklappen();
      a.teile.palette.koerper.querySelector('input[data-feld="0"]')?.focus();
      return;
    }
  }
  if (imFeld) return;

  switch (k) {
    case 'Escape':
      if (a.befehl) befehlEnde(a);
      else if (a.auswahl.size) a.auswahl = new Set();
      else if (a.vollbild) { vollbildSetzen(a, false); return; }
      break;
    case 'Delete':
    case 'Backspace':
      loeschen(a);
      break;
    case ' ':
      a.leertaste = true;
      break;
    case 'f':
      allesZeigen(a);
      break;
    case 'v':
      if (!a.auswahl.size) return;
      starten(a, verschiebenBefehl());
      break;
    case 'c':
      if (!kopierbar(a)) return;
      starten(a, kopierenBefehl());
      break;
    case 't':
      if (!a.adapter.vorlageOeffnen) return;
      a.adapter.vorlageOeffnen(a);
      break;
    default: {
      const w = WERKZEUGE.find((x) => x.taste === k);
      if (!w) return;
      starten(a, w.bauen());
    }
  }
  e.preventDefault();
  zeichnen(a);
}

document.addEventListener('keydown', taste);
document.addEventListener('keyup', (e) => {
  if (e.key === ' ' && aktive) aktive.leertaste = false;
});
// Ein Druck ausserhalb des Fensters und dessen, was die App daneben stellt:
// Tasten gehören wieder der Seite.
document.addEventListener('pointerdown', (e) => {
  if (aktive && !aktive.knoten?.closest('.zeichenbereich')?.contains(e.target)) aktive = null;
}, true);

// ===========================================================================
// Aufbau
// ===========================================================================

function groesseMessen(a) {
  const { clientWidth: b, clientHeight: h } = a.teile.flaeche;
  if (!b || !h || (b === a.v.breite && h === a.v.hoehe)) return;
  if (a.v.massstab && a.v.breite) {
    // Die Mitte bleibt, wo sie war.
    a.v.ursprung = [a.v.ursprung[0] + (b - a.v.breite) / 2, a.v.ursprung[1] + (h - a.v.hoehe) / 2];
  }
  a.v.breite = b;
  a.v.hoehe = h;
  a.teile.bild.setAttribute('viewBox', `0 0 ${b} ${h}`);
  a.teile.palette.halten();
  if (!a.v.massstab || a.einpassen) {
    a.einpassen = false;
    allesZeigen(a);
  } else {
    zeichnen(a);
  }
}

/**
 * Die Höhe der Zeichnung am Griff darunter -- gemerkt im Browser, für jede
 * Zeichnung dieselbe. Gesetzt als Variable, nicht als Höhe: im Vollbild
 * füllt die Zeichnung den Platz, und eine feste Höhe stünde dem im Weg.
 */
function hoeheEinrichten(flaeche, griff) {
  const setzen = (h) => flaeche.style.setProperty('--cad-hoehe', `${Math.round(Math.min(1600, Math.max(240, h)))}px`);
  try {
    const gemerkt = Number(localStorage.getItem(HOEHE));
    if (gemerkt) setzen(gemerkt);
  } catch {
    // Privater Modus: dann gilt die Vorgabe.
  }
  griff.addEventListener('pointerdown', (start) => {
    start.preventDefault();
    griff.classList.add('ist-aktiv');
    const anfang = flaeche.getBoundingClientRect().height;
    const bewegen = (e) => setzen(anfang + e.clientY - start.clientY);
    const los = () => {
      griff.classList.remove('ist-aktiv');
      window.removeEventListener('pointermove', bewegen);
      window.removeEventListener('pointerup', los);
      try {
        localStorage.setItem(HOEHE, String(parseFloat(flaeche.style.getPropertyValue('--cad-hoehe'))));
      } catch {
        // Privater Modus: dann gilt sie bis zum Neuladen.
      }
    };
    window.addEventListener('pointermove', bewegen);
    window.addEventListener('pointerup', los);
  });
}

function bauen(a) {
  const bild = svgEl('svg', { class: 'cad-bild', role: 'img', 'aria-label': 'Zeichnung' });
  const modell = svgEl('g');
  const oben = svgEl('g');
  bild.append(modell, oben);
  const leiste = el('div.cad-leiste', { hidden: true });
  const flaeche = el('div.cad-flaeche', {}, [bild, leiste]);
  const hinweis = el('span.cad-hinweis');
  a.teile = {
    bild, modell, oben, flaeche, leiste, hinweis, lage: null,
  };
  a.teile.palette = paletteBauen(flaeche);
  const knoepfe = el('div.cad-knoepfe', {}, leisteBauen(a));
  const hoehengriff = el('div.cad-hoehengriff', { title: 'Höhe der Zeichnung ziehen' });
  a.knoten = el('div.cad', {}, [knoepfe, flaeche, hoehengriff, el('div.cad-status', {}, [hinweis])]);
  hoeheEinrichten(flaeche, hoehengriff);
  a.knoten.addEventListener('pointerdown', () => { aktive = a; });

  bild.addEventListener('pointerdown', (e) => druecken(a, e));
  // Bewegen und Loslassen am Browserfenster: das Bild wird bei jedem Neubau
  // der Tafel kurz ab- und wieder eingehängt, und ein Rahmen soll das
  // überstehen. Abgemeldet werden sie mit dem Fenster (`abbauen`).
  a.abbruch = new AbortController();
  const nurSolange = { signal: a.abbruch.signal };
  window.addEventListener('pointermove', (e) => {
    if (a.druck || a.kneifen || e.target === bild || bild.contains(e.target)) bewegen(a, e);
  }, nurSolange);
  window.addEventListener('pointerup', (e) => loslassen(a, e), nurSolange);
  window.addEventListener('pointercancel', (e) => {
    a.finger.delete(e.pointerId);
    if (!a.finger.size) a.kneifen = null;
    if (a.druck?.id === e.pointerId) { a.druck = null; zeichnen(a); }
  }, nurSolange);
  bild.addEventListener('pointerleave', () => {
    if (!a.druck) { a.zeiger = null; obenBald(a); }
  });
  bild.addEventListener('wheel', (e) => rad(a, e), { passive: false });
  bild.addEventListener('contextmenu', (e) => e.preventDefault());
  // Festgehalten am Fenster: einen Beobachter, auf den nichts mehr zeigt,
  // darf der Browser wegräumen -- und dann misst niemand mehr.
  a.beobachter = new ResizeObserver(() => groesseMessen(a));
  a.beobachter.observe(flaeche);
}

/**
 * Das Fenster samt dem, was die App daneben stellt -- im Vollbild rechts,
 * sonst darunter. Die Tafel ruft das bei jedem Neubau; das Fenster selbst
 * entsteht nur einmal.
 */
export function cadBereich(a, seite = []) {
  aktualisieren(a);
  return el('div.zeichenbereich', { class: a.vollbild ? 'ist-vollbild' : '' }, [
    a.knoten,
    el('div.cad-seite', {}, seite),
  ]);
}

/**
 * Wählt Elemente von aussen -- etwa aus der Liste unter dem Fenster. Die
 * Tasten gehören danach dem Fenster: Entf löscht, was eben gewählt wurde.
 */
export function cadWaehlen(a, kennungen) {
  aktive = a;
  a.befehl = null;
  eingabeLeeren(a.eingabe);
  a.auswahl = new Set(kennungen);
  zeichnen(a);
}
