/**
 * cad_fenster.js -- das Zeichenfenster: Rahmen, Knöpfe, Maus und Tasten.
 *
 * Allgemein gebaut: was gezeichnet wird, sagt eine App über ihren «Adapter»
 * (für den Querschnitt `qa_zeichnung.js`, für das Balkensystem
 * `bs_zeichnung.js`). Das Fenster kennt nur Knoten und Elemente in drei
 * Formen -- Punkt, Linie, Fläche -- und die Mechanik, mit der man sie
 * zeichnet, wählt und ändert. Hier steht, was sie zusammenhält; die Teile
 * stehen daneben: das Modell ohne Bild in cad_modell.js, die Ansicht in
 * cad_ansicht.js, Fangen und Punkteingabe in cad_eingabe.js, Treffen, Wählen
 * und Hervorheben in cad_auswahl.js, die Befehle in cad_befehle.js, Ändern
 * und Rückgängig in cad_verlauf.js, die Seitenleiste neben der Zeichnung
 * in cad_palette.js.
 *
 * WAS DER ADAPTER EINSTELLT (mit Vorgabe, siehe `EINSTELLUNG`):
 * die Werkzeuge -- je eines mit Namen, Zeichen, Taste und der Form, die es
 * zeichnet (Punkt, Linie, Polygon) --, die Einheit und die Stufen des Rasters, wie viele
 * Nachkommastellen eine Lage zeigt, die Grenzen des Massstabs -- und ob die
 * Zeichnung «verbunden» ist. Im Querschnitt gehört eine Ecke ihrem Element:
 * wer eine Bewehrungslinie verschiebt, nimmt die Polygonecke darunter nicht
 * mit. Ein Rahmen dagegen hängt an seinen Knoten: ein Klick an einem Knoten
 * wählt den Knoten, und ein verschobener Stab nimmt seine Knoten mit -- und
 * mit ihnen, was an ihnen hängt. Dazu kann der Adapter sagen, was sich nicht
 * wählen lässt (`waehlbar`), und Teilen und Umkehren selbst übernehmen
 * (`teilen`, `umkehren`, `linieTeilen`) -- etwa, weil der Kern dabei
 * Lastwerte rechnet.
 *
 * ANHÄNGE:
 * Was eine App an Elemente hängt und selbst zeichnet -- die Lasten des
 * Balkensystems --, ist kein Element des Fensters. Wählen und löschen lässt
 * es sich trotzdem, wenn der Adapter es sagt (`anhaenge`): was ein Klick
 * trifft (`treffer`), ob eine Kennung dazugehört (`hat`), wie es gelöscht
 * wird (`loeschen`) und wo es im Bild liegt (`rahmen`). Verschoben und
 * kopiert wird es nicht; es geht mit seinem Element. Angelegt wird es mit
 * einem Werkzeug der Form «anhang»: ein Klick auf ein Element oder einen
 * Knoten (`anhangAnlegen`).
 *
 * WENIGE KNÖPFE:
 * Oben stehen die Werkzeuge der App, je mit Zeichen (sinnbilder.js) -- im
 * Querschnitt etwa «Querschnitt zeichnen», Bewehrung, Stahlprofil und
 * Vorlage, im Rahmen Linie und Knoten. Dazu Rückgängig, Wiederholen, «Alles
 * zeigen» F und Vollbild. Ein Werkzeug legt genau eine Art an; was es
 * anlegt, stellt die Seitenleiste neben der Zeichnung ein, und eine andere
 * Art ist ein anderes Werkzeug. Einen Knopf zum Wählen gibt es nicht: Wählen
 * ist der Grundzustand, Esc führt dorthin zurück. Alles Weitere steht neben
 * der Auswahl oder in der Seitenleiste.
 *
 * ALLES ZEIGEN:
 * Was ins Bild gehört, sagt der Adapter (`umriss`). Kennt er einen Teil
 * davon erst aus der Antwort des Kerns -- die Masse eines Profils --, sagt er
 * es (`umrissVollstaendig`): dann passt das Fenster nach der Antwort noch
 * einmal ein, wenn bis dahin niemand die Ansicht bewegt hat.
 *
 * EIN BLEIBENDES FENSTER:
 * Die Tafel wird nach jeder Änderung neu gebaut, das Fenster nicht -- es
 * entsteht einmal je Zeichnung und wird jedes Mal wieder eingehängt. Ein
 * halb gezeichnetes Polygon, der Massstab und «Rückgängig» überstehen so
 * jede Rechnung, die zwischendurch fertig wird.
 *
 * IM RAUM:
 * Hat der Adapter drei Achsen, sieht man die Zeichnung parallel projiziert
 * (cad_raum.js): die rechte Maustaste dreht sie, die Knöpfe oben haben die
 * Ansichten, die Seitenleiste die Arbeitsebene, und E legt diese durch
 * den gefangenen Punkt. Auf dem Handy wird nur mit den Knöpfen
 * gedreht.
 *
 * ZWEI EBENEN:
 * Das Modell wird nur gezeichnet, wenn es sich ändert oder die Ansicht
 * wandert. Zeiger, Fangzeichen und Vorschau liegen darüber und folgen der
 * Maus -- je Bild einmal, nicht je Ereignis.
 */

import {
  ansichtNeu, einpassen, nachBild, rasterZeichnen, zoomen,
} from './cad_ansicht.js';
import { abstand, auswahlTeil, cadModell, mitte } from './cad_modell.js';
import {
  eingabeLeeren, eingabeNeu, fangen, getipptPunkt, hilfenZeichnen, klickPunkt, taste as eingabeTaste,
  zeigerFang,
} from './cad_eingabe.js';
import {
  anhangBefehl, knotenBefehl, knotenEinfuegenBefehl, kopierenBefehl, linienBefehl,
  polygonBefehl, verschiebenBefehl,
} from './cad_befehle.js';
import {
  hervorheben, istAnhang, klickWaehlen, leisteZeichnen, ohneAnhaenge, rahmenWaehlen, treffer,
} from './cad_auswahl.js';
import { lageZeichnen, paletteBauen, paletteZeichnen } from './cad_palette.js';
import {
  ansichtsleiste, drehen, drehpunkt, ebeneDurch, raumEinrichten, raumRaster,
} from './cad_raum.js';
import { aendern, aktualisieren, vorwaerts, zurueck } from './cad_verlauf.js';
import { el, svgEl } from './dom.js';
import { sinnbild } from './sinnbilder.js';

/**
 * Was ein Adapter einstellen kann, und was gilt, wenn er nichts sagt -- die
 * Werte der Querschnittsanalyse. `massstab`: kleinster und grösster, in
 * Bildpunkten je Einheit.
 *
 * Ein Werkzeug ist `{name, text, zeichen, taste, form, titel?, bereit?}`:
 * `zeichen` ein Sinnbild, `form` was es zeichnet -- 'knoten', 'linie' oder
 * 'polygon', oder `(a) => form`, wo die Seitenleiste es umstellt (die Bewehrung
 * als Linie oder als Punkt). Statt der Form kann es seinen Befehl selbst
 * bauen, `befehl(a)` -- die Vorlagen des Querschnitts, die an einem Punkt
 * eingesetzt werden. Gibt `bereit(a)` falsch, startet es nicht und sagt
 * selbst, warum -- eine Last ohne Lastfall. Was es anlegt, weiss nur seine App.
 */
const EINSTELLUNG = {
  werkzeuge: [],
  einheit: 'mm',
  raster: { stufen: [1, 5, 10, 25, 50, 100], vorgabe: 10 },
  stellen: 1,
  massstab: [1e-3, 80],
  verbunden: false,
};
/** Ab wie viel Bewegung ein Druck ein Ziehen ist und kein Klick -- px. */
const ZITTERN = 4;
/** Unter diesem Schlüssel merkt sich der Browser die Höhe der Zeichnung. */
const HOEHE = 'opencivil.cad.hoehe';

/** Die Befehle hinter den Formen eines Werkzeugs. */
const BEFEHLE = {
  knoten: knotenBefehl, linie: linienBefehl, polygon: polygonBefehl, anhang: anhangBefehl,
};

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
  const einstellung = { ...EINSTELLUNG, ...adapter.einstellung };
  const a = {
    adapter,
    einstellung,
    modell: cadModell({ ...adapter, verbunden: einstellung.verbunden }),
    listen: ['knoten', ...adapter.arten.map((x) => x.liste)],
    v: ansichtNeu(einstellung.massstab),
    raster: einstellung.raster.vorgabe,
    fang: true,
    befehl: null,
    auswahl: new Set(),
    eingabe: eingabeNeu(adapter.achsen.length),
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
    nachfassen: null,    // die Ansicht nach «Alles zeigen», solange dem Umriss noch etwas fehlt
    letzterKlick: null,
    anker: null,         // der zuletzt angeklickte Knoten: dort beginnt der Vektor beim Verschieben
    knoten: null,
    teile: null,
    bildUhr: null,
  };
  a.aendern = (veraenderer, optionen) => aendern(a, veraenderer, optionen);
  a.ende = () => befehlEnde(a);
  a.aktionen = () => aktionen(a);
  a.starten = (befehl) => starten(a, befehl);
  a.werkzeugStarten = (name) => werkzeugStarten(a, name);
  a.neuZeichnen = () => zeichnen(a);
  a.obenBald = () => obenBald(a);
  a.getipptLiefern = () => getipptLiefern(a);
  // Mit drei Achsen: eine Ansicht, die sich drehen lässt, und eine Arbeitsebene.
  if (adapter.achsen.length === 3) raumEinrichten(a);
  bauen(a);
  return a;
}

// ===========================================================================
// Befehle
// ===========================================================================

function starten(a, befehl) {
  a.befehl = befehl;
  eingabeLeeren(a.eingabe);
  a.eingabe.bezug = null;
  a.letzterKlick = null;
  befehl.start?.(a);
  zeichnen(a);
}

function befehlEnde(a) {
  a.befehl = null;
  eingabeLeeren(a.eingabe);
  zeichnen(a);
}

/**
 * Startet ein Werkzeug der App -- mit seinem eigenen Befehl oder dem Befehl
 * seiner Form, die es gerade hat. Wer in der Seitenleiste die Form
 * umstellt, startet es neu.
 */
function werkzeugStarten(a, name) {
  const w = a.einstellung.werkzeuge.find((x) => x.name === name);
  if (!w || w.bereit?.(a) === false) return;
  starten(a, w.befehl ? w.befehl(a) : BEFEHLE[typeof w.form === 'function' ? w.form(a) : w.form](w.name));
}

/** Ein fertiger Punkt geht an den Befehl; danach sind die Hilfen wieder frei. */
function punktLiefern(a, erg) {
  const befehl = a.befehl;
  if (!befehl) return;
  befehl.punkt(a, erg);
  eingabeLeeren(a.eingabe);
  zeichnen(a);
}

function loeschen(a) {
  if (!a.auswahl.size) return;
  const weg = new Set(a.auswahl);
  aendern(a, (z) => {
    a.modell.loeschen(z, weg);
    a.adapter.anhaenge?.loeschen(z, weg);
  }, { auswahl: () => [] });
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

/** Teilt jede gewählte Linie in der Mitte -- oder lässt es den Adapter tun. */
function teilen(a) {
  if (a.adapter.teilen) {
    a.adapter.teilen(a, [...a.auswahl]);
    return;
  }
  jedesGewaehlte(a, 'linie', (z, art, e) => {
    const lagen = a.modell.lagen(z);
    const [p, q] = [lagen.get(e.von), lagen.get(e.bis)];
    return p && q ? a.modell.linieTeilen(z, art, e, mitte(p, q)) : null;
  });
}

/**
 * Gibt es etwas zu kopieren -- ein ganzes Element oder einen Knoten?
 * Einzelne Ecken kopiert es nicht, Anhänge auch nicht: sie gehen mit ihrem
 * Element.
 */
function kopierbar(a) {
  return [...a.auswahl].some((s) => auswahlTeil(s).i === null && !istAnhang(a, s));
}

/**
 * Was neben einer Auswahl angeboten wird -- nur, was für sie geht: erst das
 * Allgemeine, dann das der App, zuletzt Löschen.
 */
function aktionen(a) {
  const z = a.adapter.zeichnung();
  const m = a.modell;
  // Nur Anhänge gewählt: verschieben, kopieren, teilen lässt sich da nichts.
  if ([...a.auswahl].every((s) => istAnhang(a, s))) {
    return [{ zeichen: '✕', text: 'Löschen', taste: 'Entf', tun: () => loeschen(a) }];
  }
  const gewaehlt = [...m.elemente(z)].filter(({ e }) => a.auswahl.has(e.kennung));
  const nurLinien = gewaehlt.length > 0 && gewaehlt.length === a.auswahl.size
    && gewaehlt.every(({ art }) => art.form === 'linie');
  const einzeln = gewaehlt.length === 1 && a.auswahl.size === 1 ? gewaehlt[0] : null;
  const teilbar = (x) => x.art.form === 'flaeche' || (x.art.form === 'linie' && x.art.teilbar !== false);
  return [
    { zeichen: '⇢', text: 'Verschieben', taste: 'V',
      tun: () => { if (ohneAnhaenge(a)) starten(a, verschiebenBefehl()); } },
    kopierbar(a) ? { zeichen: '⧉', text: 'Kopieren', taste: 'C',
      tun: () => { if (ohneAnhaenge(a)) starten(a, kopierenBefehl()); } } : null,
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
      tun: () => (a.adapter.umkehren
        ? a.adapter.umkehren(a, [...a.auswahl])
        : jedesGewaehlte(a, 'linie', (zz, art, e) => { m.umkehren(art, e); })),
    } : null,
    ...(a.adapter.aktionen?.(a) || []),
    { zeichen: '✕', text: 'Löschen', taste: 'Entf', tun: () => loeschen(a) },
  ].filter(Boolean);
}

// ===========================================================================
// Zeichnen
// ===========================================================================

/**
 * Passt alles ins Bild. Bis 2026-11-27 liess es die Ecke frei, in der das
 * schwebende Fenster stand; die Seitenleiste steht neben der Zeichnung.
 */
function allesZeigen(a) {
  einpassen(a.v, a.adapter.umriss(a));
  a.nachfassen = a.adapter.umrissVollstaendig?.(a) === false ? ansichtStand(a.v) : null;
  zeichnen(a);
}

/** Wo die Ansicht steht -- um zu sehen, ob sie seit «Alles zeigen» bewegt wurde. */
function ansichtStand(v) {
  return JSON.stringify([v.massstab, v.ursprung, v.basis]);
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
  if (a.nachfassen && a.adapter.umrissVollstaendig(a)) {
    const unbewegt = a.nachfassen === ansichtStand(a.v);
    a.nachfassen = null;
    if (unbewegt) {
      allesZeigen(a);
      return;
    }
  }
  const app = svgEl('g');
  a.adapter.zeichnen(a, app);
  a.teile.modell.replaceChildren(
    a.raum ? raumRaster(a) : rasterZeichnen(a.v, a.raster, a.adapter.achsen),
    app,
    knotenZeichnen(a),
    hervorheben(a, a.auswahl, 'cad-auswahl'),
  );
  obenZeichnen(a);
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
// Knöpfe und Statuszeile
// ===========================================================================

function statusZeichnen(a) {
  let satz;
  if (a.befehl) {
    const achsen = a.adapter.achsen.map((x) => x.toUpperCase()).join('/');
    satz = `${a.befehl.hinweis ? `${a.befehl.hinweis} · ` : ''}R Bezugspunkt · ${achsen} Achse · `
      + `${a.raum ? 'E Ebene durch den Punkt · ' : ''}P/S parallel/senkrecht · M Mitte · Ziffern tippen · Esc zurück`;
  } else if (a.auswahl.size) {
    satz = 'V verschieben · C kopieren · Entf löschen · Shift+Klick nimmt dazu · Esc wählt ab';
  } else {
    satz = `Klick wählt, noch ein Klick das darunter · Rahmen ziehen wählt mehrere · Mausrad zoomt${
      a.raum ? ' · rechte Maustaste dreht' : ''}`;
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

/** Ein Knopf oben im Fenster: sein Sinnbild und, wo Platz ist, ein Wort. */
function knopf(zeichen, beschriftung, titel, tun, klasse = '') {
  return el('button.cad-knopf', {
    type: 'button', title: titel, 'aria-label': titel, class: klasse,
    on: { click: (e) => { e.preventDefault(); tun(); } },
  }, [sinnbild(zeichen), beschriftung ? el('span.cad-text', { text: beschriftung }) : null]);
}

function vollbildSetzen(a, an) {
  a.vollbild = an;
  a.einpassen = true;
  // Das Bild springt unter dem Zeiger weg: was er zuletzt traf, gilt nicht mehr.
  a.zeiger = null;
  a.adapter.tafelNeu();
}

function leisteBauen(a) {
  const werkzeuge = a.einstellung.werkzeuge.map((w) => {
    const titel = `${w.titel || w.text} (${w.taste.toUpperCase()})`;
    const k = knopf(w.zeichen, w.text, titel, () => werkzeugStarten(a, w.name), 'ist-gross');
    k.dataset.werkzeug = w.name;
    return k;
  });
  // Rückgängig und die Ansicht nur als Zeichen, zu zweit übereinander: so
  // stehen die Werkzeuge mit ihren Wörtern in einer Zeile.
  const rueck = knopf('cad-rueckgaengig', '', 'Rückgängig (Strg+Z)', () => zurueck(a));
  const vor = knopf('cad-wiederholen', '', 'Wiederholen (Strg+Y)', () => vorwaerts(a));
  const alles = knopf('cad-alles', '', 'Alles zeigen (F)', () => allesZeigen(a));
  const gross = knopf('cad-vollbild', '', 'Vollbild', () => vollbildSetzen(a, !a.vollbild));
  // Im Raum die Ansichten: 3D, x-y, x-z, y-z.
  const ansichten = a.raum ? ansichtsleiste(a, () => allesZeigen(a)) : null;
  a.teile.knoepfe = { werkzeuge, rueck, vor, gross, ansichten };
  // Was die App gleich neben ihre Werkzeuge stellt -- das Balkensystem die
  // Wahl des Lastfalls. Sie füllt es selbst, so oft sich etwas ändert.
  const zusatz = a.adapter.leisteZusatz?.(a) || null;
  return [
    ...werkzeuge, zusatz, ansichten?.knoten, el('span.cad-luecke'),
    el('div.cad-ansicht', {}, [rueck, vor, alles, gross]),
  ];
}

function knoepfeZeichnen(a) {
  const k = a.teile.knoepfe;
  for (const w of k.werkzeuge) w.classList.toggle('ist-an', w.dataset.werkzeug === a.befehl?.name);
  k.rueck.disabled = !a.rueck.length;
  k.vor.disabled = !a.vor.length;
  k.gross.classList.toggle('ist-an', a.vollbild);
  k.gross.title = a.vollbild ? 'Vollbild verlassen (Esc)' : 'Vollbild';
  k.gross.setAttribute('aria-label', k.gross.title);
  k.ansichten?.zeichnen();
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
        abstand: abstand(p, q) || 1, mitte: mitte(p, q),
        massstab: a.v.massstab, ursprung: [...a.v.ursprung],
      };
      a.druck = null;
      return;
    }
    if (a.finger.size > 2) return;
  }
  if (a.druck || !a.v.massstab) return;
  const schieben = e.button === 1 || (e.button === 0 && a.leertaste);
  // Im Raum dreht die rechte Maustaste die Ansicht -- um die Mitte der
  // Zeichnung --, ebenso die linke mit Alt (Benutzer, 2026-11-16). Mit Alt
  // geklickt statt gezogen bleibt es ein Klick: ein Punkt ohne Fangen.
  const dreht = a.raum && (e.button === 2 || (e.button === 0 && e.altKey))
    ? { um: drehpunkt(a), zuletzt: bild, klick: e.button === 0 } : null;
  if (e.button !== 0 && !schieben && !dreht) return;
  if (e.button === 1) e.preventDefault();
  // Ein Feld in der Seitenleiste gibt seinen Fokus ab: der Klick gehört der Zeichnung.
  if (document.activeElement?.closest?.('.cad-palette')) document.activeElement.blur();
  a.druck = {
    id: e.pointerId, start: bild, ursprung: [...a.v.ursprung], schieben, dreht, bewegt: false,
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
    const m = mitte(p, q);
    a.v.massstab = k.massstab;
    a.v.ursprung = [k.ursprung[0] + m[0] - k.mitte[0], k.ursprung[1] + m[1] - k.mitte[1]];
    zoomen(a.v, (abstand(p, q) || 1) / k.abstand, m);
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
  if (d.dreht) {
    drehen(a, bild[0] - d.dreht.zuletzt[0], bild[1] - d.dreht.zuletzt[1], d.dreht.um);
    d.dreht.zuletzt = bild;
    zeichnen(a);
    return;
  }
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
  if (d.bewegt || d.schieben || (d.dreht && !d.dreht.klick)) {
    zeichnen(a);
    return;
  }
  if (a.befehl) {
    const erg = klickPunkt(a, bild, e);
    if (erg?.fehler) kurzMelden(a, erg.fehler);
    if (erg?.p) punktLiefern(a, erg);
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
    kurzMelden(a, 'Zum Zoomen ins Fenster klicken – oder Strg + Mausrad.');
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
    const eigene = a.befehl.tasten?.find((t) => t.taste === k);
    if (eigene) {
      e.preventDefault();
      eigene.tun(a, a.befehl);
      zeichnen(a);
      return;
    }
    if (eingabeTaste(a, e)) {
      e.preventDefault();
      zeichnen(a);
      return;
    }
    // Ziffern gehen ins erste Feld -- das Zeichen selbst landet dort.
    if (/^[0-9.,-]$/.test(e.key)) {
      a.teile.palette.koerper.querySelector('input[data-feld="0"]')?.focus();
      return;
    }
  }
  if (imFeld) return;

  // Im Raum legt E die Arbeitsebene durch den gefangenen Punkt -- vor den
  // Werkzeugen: in der Ebene ist E eines (die Punktlast der Decke).
  if (k === 'e' && a.raum) {
    const p = zeigerFang(a)?.p;
    if (p) ebeneDurch(a, p);
    e.preventDefault();
    zeichnen(a);
    return;
  }

  switch (k) {
    case 'Escape':
      if (a.befehl) befehlEnde(a);
      else if (a.auswahl.size) {
        a.auswahl = new Set();
        a.anker = null;
      }
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
      if (!ohneAnhaenge(a)) return;
      starten(a, verschiebenBefehl());
      break;
    case 'c':
      if (!kopierbar(a) || !ohneAnhaenge(a)) return;
      starten(a, kopierenBefehl());
      break;
    default: {
      const w = a.einstellung.werkzeuge.find((x) => x.taste === k);
      if (!w) return;
      werkzeugStarten(a, w.name);
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
    if (a.nachfassen) a.nachfassen = ansichtStand(a.v);
  }
  a.v.breite = b;
  a.v.hoehe = h;
  a.teile.bild.setAttribute('viewBox', `0 0 ${b} ${h}`);
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
    bild, modell, oben, flaeche, leiste, hinweis, lage: null, palette: paletteBauen(),
  };
  const knoepfe = el('div.cad-knoepfe', {}, leisteBauen(a));
  const hoehengriff = el('div.cad-hoehengriff', { title: 'Höhe der Zeichnung ziehen' });
  // Die Zeichnung mit ihrem Griff, daneben -- oder im schmalen Fenster
  // darunter -- die Seitenleiste (cad_palette.js).
  const mitte = el('div.cad-mitte', {}, [
    el('div.cad-zeichnung', {}, [flaeche, hoehengriff]), a.teile.palette.knoten,
  ]);
  a.knoten = el('div.cad', {}, [knoepfe, mitte, el('div.cad-status', {}, [hinweis])]);
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
  a.anker = null;
  zeichnen(a);
}
