/**
 * achsen.js -- ein Achsenkreuz für alle Diagramme.
 *
 * Massstab, Gitter mit Teilung, Nulllinien, Rahmen und Achsentitel: was jedes
 * Diagramm braucht und vorher jedes selbst baute, sechsmal fast gleich und mit
 * kleinen Abweichungen, die niemand gewollt hatte. Die Diagramme zeichnen nur
 * noch ihre Daten hinein.
 *
 * Die Reihenfolge im Bild ist fest: Gitter und Nulllinien zuunterst, darüber
 * die Daten (`daten`), zuoberst die Achsentitel.
 *
 * Titel und Zahlen setzen die Bilder aus den Grössen des Kerns zusammen
 * (`achsentitel`, `masszahl`): Zeichen, Einheit und Stellen kommen mit den
 * Daten. Bis 2026-11-20 schrieb jedes Bild sie selbst, und die Pfahlskizze
 * sagte kN/m², wo die Maske kPa zeigt.
 *
 * Dazu, was mehrere Diagramme gleich zeichnen: den Bemessungspunkt mit
 * seinem Weg zum Widerstand, die Farbe eines Urteils und die Legende unter
 * dem Bild (`bemessungspunkt`, `urteilsfarbe`, `legende`).
 */

import { el, stilfarbe, svgEl } from './dom.js';

export const NR = 'http://www.w3.org/2000/svg';

const GITTER = '#e6e9ee';
const NULLLINIE = '#b8c0cc';
const TEILUNG = '#5c6773';
const TITEL = '#1a1f27';
const RAHMEN = '#8895a8';
/** Wie weit ein Strich der Teilung ohne Gitter aus dem Rahmen ragt. */
const STRICH = 4;

/** «M [kNm]» -- der Achsentitel einer Grösse des Kerns (`Anzeigegroesse`). */
export const achsentitel = (g) => `${g.zeichen} [${g.einheit}]`;

/**
 * «12.3 kNm», «30°» -- eine Zahl mit der Einheit, die der Kern ihr gibt:
 * einer Grösse (`Anzeigegroesse`) mit deren Stellen, oder eines Felds
 * (`feldangabe`) mit `stellen`.
 */
export function masszahl(wert, angabe, stellen = angabe.stellen) {
  const { einheit = '', klebt = false } = angabe;
  return `${Number(wert).toFixed(stellen)}${einheit && !klebt ? ' ' : ''}${einheit}`;
}

/** Sucht einen runden Schrittabstand für die Achsenteilung. */
export function schrittweite(spanne, zielAnzahl = 8) {
  const roh = spanne / zielAnzahl;
  const groesse = 10 ** Math.floor(Math.log10(Math.abs(roh) || 1));
  const rest = roh / groesse;
  const gewaehlt = rest >= 5 ? 10 : rest >= 2 ? 5 : rest >= 1 ? 2 : 1;
  return gewaehlt * groesse;
}

/** Der Schritt einer Teilung: fest, sonst ein runder aus `ziel` Strichen. */
function schrittDerTeilung([a, b], { ziel = 8, schritt } = {}) {
  return schritt ?? schrittweite(Math.abs(b - a), ziel);
}

/** Die Striche einer Teilung: runde Vielfache im Bereich, aufsteigend. */
function striche(bereich, teilung) {
  const von = Math.min(...bereich);
  const bis = Math.max(...bereich);
  const s = schrittDerTeilung(bereich, teilung);
  const heraus = [];
  for (let v = Math.ceil(von / s) * s; v <= bis; v += s) heraus.push(v);
  return heraus;
}

/**
 * Die Schrift einer Teilung ohne eigene: so viele Nachkommastellen, wie ihr
 * Schritt verlangt -- ganze Zahlen machten aus 0.5 eine 1 --, ohne «-0».
 */
function schriftDerTeilung(bereich, teilung) {
  const stellen = Math.max(0, Math.ceil(-Math.log10(schrittDerTeilung(bereich, teilung)) - 1e-9));
  return (v) => (Math.abs(v) < 0.5 * 10 ** -stellen ? 0 : v).toFixed(stellen);
}

function text(inhalt, attribute) {
  const knoten = svgEl('text', attribute);
  knoten.textContent = inhalt;
  return knoten;
}

/** Griechische Buchstaben, gross und klein, dazu ϑ, ϕ und ϵ. */
const GRIECHISCH = /([\u0391-\u03A9\u03B1-\u03C9\u03D1\u03D5\u03F5]+)/;

/** Ein Index: so tief und so gross, gemessen an der Schrift daneben. */
const INDEX = { tiefe: 0.3, groesse: 0.75 };

/**
 * Setzt `inhalt` in einen SVG-Textknoten -- als Formel, soweit es eine ist:
 * griechische Buchstaben in der kursiven Formelschrift von KaTeX, `_y` und
 * `_{Rd,u}` tiefgestellt. Gibt den Knoten zurück.
 *
 * JetBrains Mono zeichnet χ fast wie x. In einem Bild, in dem beide stehen --
 * die Krümmung und die Druckzonenhöhe --, hiess das raten.
 */
export function formelText(knoten, inhalt) {
  // Nach einem Index muss die Schrift wieder hoch -- mit dem Stück danach.
  let hoch = false;
  for (const teil of String(inhalt).split(/(_\{[^}]*\}|_[A-Za-z0-9]+)/)) {
    if (!teil) continue;
    const index = teil.startsWith('_');
    let ziel = knoten;
    if (index) {
      ziel = svgEl('tspan', {
        'font-size': `${INDEX.groesse * 100}%`, dy: `${INDEX.tiefe / INDEX.groesse}em`,
      });
    } else if (hoch) {
      ziel = svgEl('tspan', { dy: `${-INDEX.tiefe}em` });
    }
    if (ziel !== knoten) knoten.append(ziel);
    hoch = index;
    (index ? teil.replace(/^_\{?|\}$/g, '') : teil).split(GRIECHISCH).forEach((stueck, i) => {
      if (!stueck) return;
      if (i % 2) {
        const zeichen = svgEl('tspan', { 'font-family': 'KaTeX_Math', 'font-style': 'italic' });
        zeichen.textContent = stueck;
        ziel.append(zeichen);
      } else {
        ziel.append(document.createTextNode(stueck));
      }
    });
  }
  return knoten;
}

/**
 * Ein leeres Diagramm.
 *
 * @param {object} o
 * @param {number} o.breite   Breite des Bildes (viewBox)
 * @param {number} o.hoehe    Höhe des Bildes
 * @param {{oben: number, rechts: number, unten: number, links: number}} o.rand
 *   Platz um das Feld, für Teilung und Titel
 * @param {object} o.x   die waagrechte Achse, `o.y` die senkrechte, je mit
 *   - `bereich: [a, b]` -- a liegt links bzw. unten. Umgekehrt angegeben läuft
 *     die Achse andersherum, etwa die Höhe eines Schnitts nach unten.
 *   - `teilung` -- Gitter mit beschrifteten Strichen: `{ziel, schritt,
 *     format, nurStriche}`. `schritt` fest, sonst ein runder aus `ziel`
 *     Strichen; ohne `format` mit so vielen Nachkommastellen, wie der Schritt
 *     verlangt. Mit `nurStriche` keine Linien über das Feld, nur kurze
 *     Striche am Rand. Ohne `teilung` weder Gitter noch Striche.
 *   - `null` -- die Nulllinie betonen, sofern sie im Bereich liegt
 *   - `titel` -- der Achsentitel
 * @param {object} [o.attribute]  Attribute des svg-Elements
 * @param {boolean} [o.rahmen]    das Feld umrahmen
 * @param {{teilung: number, titel: number}} [o.schrift]  Schriftgrössen
 * @param {number} [o.titelLinks]  Abstand des senkrechten Titels vom Rand
 * @returns {{svg, daten, x: Function, y: Function, feld: object}}
 *   `daten` ist die Gruppe, in die das Diagramm zeichnet.
 */
export function achsenkreuz({
  breite, hoehe, rand, x: xAchse, y: yAchse, attribute = {},
  rahmen = false, schrift = { teilung: 11, titel: 12 }, titelLinks = 16,
}) {
  const feld = {
    links: rand.links, rechts: breite - rand.rechts,
    oben: rand.oben, unten: hoehe - rand.unten,
  };
  const feldBreite = feld.rechts - feld.links;
  const feldHoehe = feld.unten - feld.oben;
  const [x0, x1] = xAchse.bereich;
  const [y0, y1] = yAchse.bereich;
  // Ein Bereich ohne Ausdehnung zeichnete sonst alles ins Unendliche.
  const x = (v) => feld.links + ((v - x0) / ((x1 - x0) || 1)) * feldBreite;
  const y = (v) => feld.oben + (1 - (v - y0) / ((y1 - y0) || 1)) * feldHoehe;

  const svg = svgEl('svg', { ...attribute, viewBox: `0 0 ${breite} ${hoehe}` });

  if (rahmen) {
    svg.append(svgEl('rect', {
      x: feld.links, y: feld.oben, width: feldBreite, height: feldHoehe,
      fill: 'none', stroke: RAHMEN, 'stroke-width': 1,
    }));
  }

  if (xAchse.teilung || yAchse.teilung) {
    const gitter = svgEl('g');
    const format = (achse) => achse.teilung.format || schriftDerTeilung(achse.bereich, achse.teilung);
    // Je Strich der Teilung eine Linie über das Feld -- oder, mit
    // `nurStriche`, ein kurzer Strich aus dem Rahmen. Bis 2026-11-20 las das
    // hier niemand, und `plt.grid(False)` liess das Gitter stehen.
    const linie = (achse, ganz, kurz) => svgEl('line', achse.teilung.nurStriche
      ? { ...kurz, stroke: RAHMEN, 'stroke-width': 1 }
      : { ...ganz, stroke: GITTER, 'stroke-width': 1 });
    if (xAchse.teilung) {
      for (const v of striche(xAchse.bereich, xAchse.teilung)) {
        gitter.append(linie(xAchse,
          { x1: x(v), y1: feld.oben, x2: x(v), y2: feld.unten },
          { x1: x(v), y1: feld.unten, x2: x(v), y2: feld.unten + STRICH }));
        gitter.append(text(format(xAchse)(v), {
          x: x(v), y: feld.unten + schrift.teilung + 5, 'text-anchor': 'middle',
          'font-size': schrift.teilung, fill: TEILUNG,
        }));
      }
    }
    if (yAchse.teilung) {
      for (const v of striche(yAchse.bereich, yAchse.teilung)) {
        gitter.append(linie(yAchse,
          { x1: feld.links, y1: y(v), x2: feld.rechts, y2: y(v) },
          { x1: feld.links - STRICH, y1: y(v), x2: feld.links, y2: y(v) }));
        gitter.append(text(format(yAchse)(v), {
          x: feld.links - 8, y: y(v) + 4, 'text-anchor': 'end',
          'font-size': schrift.teilung, fill: TEILUNG,
        }));
      }
    }
    svg.append(gitter);
  }

  // Nulllinien kräftiger, damit Zug und Druck auf einen Blick trennbar sind.
  const umfasstNull = ([a, b]) => Math.min(a, b) < 0 && Math.max(a, b) > 0;
  if (yAchse.null && umfasstNull(yAchse.bereich)) {
    svg.append(svgEl('line', {
      x1: feld.links, y1: y(0), x2: feld.rechts, y2: y(0),
      stroke: NULLLINIE, 'stroke-width': 1.5,
    }));
  }
  if (xAchse.null && umfasstNull(xAchse.bereich)) {
    svg.append(svgEl('line', {
      x1: x(0), y1: feld.oben, x2: x(0), y2: feld.unten,
      stroke: NULLLINIE, 'stroke-width': 1.5,
    }));
  }

  const daten = svgEl('g');
  svg.append(daten);

  // Die Titel als Formel: «χ [1/m]», «M_Ed [kNm]».
  const titel = { 'text-anchor': 'middle', 'font-size': schrift.titel, fill: TITEL, 'font-weight': 600 };
  if (xAchse.titel) {
    svg.append(formelText(svgEl('text', {
      ...titel, x: feld.links + feldBreite / 2, y: hoehe - 8,
    }), xAchse.titel));
  }
  if (yAchse.titel) {
    const mitte = feld.oben + feldHoehe / 2;
    svg.append(formelText(svgEl('text', {
      ...titel, x: titelLinks, y: mitte, transform: `rotate(-90 ${titelLinks} ${mitte})`,
    }), yAchse.titel));
  }

  return { svg, daten, x, y, feld };
}

// ===========================================================================
// Was mehrere Diagramme gleich zeichnen
// ===========================================================================

/**
 * Die Farbe eines Urteils: grün, wenn erfüllt, sonst rot -- dieselbe wie in
 * den Tabellen (`--gut`, `--schlecht` in 10-grundlage.css). Bis 2026-11-20 stand das
 * Paar in den Bildern als eigene Zahl, ein wenig anders als in den Tabellen.
 */
export const urteilsfarbe = (erfuellt) => stilfarbe(erfuellt ? 'gut' : 'schlecht');

/**
 * Ein Bemessungspunkt: die Einwirkung als gefüllter Punkt mit ihrem Namen
 * daneben, dazu -- wo es ihn gibt -- der Widerstand als hohler Punkt und der
 * gestrichelte Weg dorthin. Bis 2026-11-20 zeichnete ihn jedes Bild selbst,
 * viermal mit kleinen Abweichungen in Grösse und Strich.
 *
 * @param {SVGElement} daten  die Gruppe, in die gezeichnet wird
 * @param {object} p
 * @param {number[]} p.ein           die Einwirkung `[x, y]`, im Bild
 * @param {number[]} [p.widerstand]  der Widerstand `[x, y]`, im Bild
 * @param {string} p.farbe           meist die des Urteils (`urteilsfarbe`)
 * @param {string} p.name            die Beschriftung neben dem Punkt
 * @param {string} p.titel           was beim Darüberfahren steht
 * @param {boolean} [p.unten]        die Beschriftung unter statt über dem Punkt
 * @param {number} [p.deckung]       blass, wo der Punkt nicht zum gezeigten Bild gehört
 * @returns {SVGElement} der Punkt -- für einen Klick auf ihn
 */
export function bemessungspunkt(daten, {
  ein, widerstand = null, farbe, name, titel, unten = false, deckung = 1,
}) {
  if (widerstand) {
    daten.append(
      svgEl('line', {
        x1: ein[0], y1: ein[1], x2: widerstand[0], y2: widerstand[1],
        stroke: farbe, 'stroke-width': 1.4, 'stroke-dasharray': '5 3', opacity: 0.75 * deckung,
      }),
      svgEl('circle', {
        cx: widerstand[0], cy: widerstand[1], r: 3.5,
        fill: '#fff', stroke: farbe, 'stroke-width': 1.6, opacity: deckung,
      }),
    );
  }
  const kreis = svgEl('circle', {
    cx: ein[0], cy: ein[1], r: 6, fill: farbe, stroke: '#fff', 'stroke-width': 2, opacity: deckung,
  });
  const hinweis = svgEl('title');
  hinweis.textContent = titel;
  kreis.append(hinweis);
  daten.append(kreis, text(name, {
    x: ein[0] + 9, y: ein[1] + (unten ? 16 : -8),
    'font-size': 11, 'font-weight': 600, fill: farbe, opacity: deckung,
  }));
  return kreis;
}

/**
 * Die Legende unter einem Diagramm. Ein Eintrag ist ein Paar `[probe, text]`
 * mit einer Probe aus `strich`, `punkt` oder `flaeche`, ein Text allein oder
 * schon ein fertiger Knoten; `null` fällt weg. Bis 2026-11-20 baute jedes
 * Bild sie von Hand, mit Punkten auch für Linien.
 */
export function legende(eintraege) {
  return el('div.mn-legende', {}, eintraege.map((e) => {
    if (typeof e === 'string') return el('span', { text: e });
    return Array.isArray(e) ? el('span', {}, e) : e;
  }));
}

/** Die beiden Einträge jedes Bilds mit Urteilen. */
export const urteilslegende = () => [
  [punkt(urteilsfarbe(true)), 'erfüllt'], [punkt(urteilsfarbe(false)), 'nicht erfüllt'],
];

/** Ein Strich für die Legende, mit Muster und Breite der Linie im Bild. */
export function strich(farbe, { muster = null, breite = 2.2 } = {}) {
  const probe = svgEl('svg', { width: 26, height: 10, viewBox: '0 0 26 10', 'aria-hidden': 'true' });
  probe.append(svgEl('line', {
    x1: 1, y1: 5, x2: 25, y2: 5, stroke: farbe, 'stroke-width': breite,
    'stroke-dasharray': muster,
  }));
  return probe;
}

/** Ein Punkt für die Legende: gefüllt, oder hohl wie ein Widerstand; `deckung` macht ihn blass. */
export function punkt(farbe, { hohl = false, deckung = 1 } = {}) {
  const stil = hohl ? { background: '#fff', border: `2px solid ${farbe}`, boxSizing: 'border-box' }
    : { background: farbe };
  return el('i', { style: { ...stil, opacity: String(deckung) } });
}

/** Eine Fläche für die Legende, etwa Druck oder Zug. */
export function flaeche(farbe) {
  return el('i', {
    style: {
      background: farbe, opacity: 0.35, borderRadius: '2px', border: `1px solid ${farbe}`,
    },
  });
}
