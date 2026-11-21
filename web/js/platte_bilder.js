/**
 * platte_bilder.js -- die Bilder einer Stahlbeton-Platte und ihre Karten.
 *
 * Der Querschnitt mit seinen vier Bewehrungslagen und den Bügeln, das
 * M-N-Interaktionsdiagramm mit den Bemessungspunkten und dem Weg, auf dem
 * der Erfüllungsgrad gemessen wurde, die M-V-Kurven mit ihrer Normalkraft
 * und die Neigungskurven -- und die Karten, in denen der Reiter «Diagramme»
 * sie zeigt (`plattenkarten`). Bis 2026-11-10 standen die Bilder in
 * diagramm.js und die Karten in bericht.js.
 *
 * Es wird nichts nachgerechnet: sämtliche Koordinaten kommen aus der Lösung,
 * jedes Diagramm mit seinen Grössen (opencivil/web/diagrammdaten.py) -- aus
 * ihnen stehen Achsentitel und Zahlen da.
 * Ändert man die Normalkraft einer M-V-Kurve, rechnet der Kern sie neu.
 */

import {
  achsenkreuz, achsentitel, bemessungspunkt, legende, masszahl, NR, punkt, schrittweite, strich,
  urteilsfarbe, urteilslegende,
} from './achsen.js';
import { karte } from './bausteine.js';
import { beschriftungenEntzerren } from './diagramm.js';
import {
  el, stilfarbe, svgEl, zahlfeld,
} from './dom.js';
import { spannungskarten } from './spannungsbild.js';
import { eintragAendern, eintragVon, feldangabe } from './zustand.js';

const BREITE = 720;
const HOEHE = 520;
const RAND = { oben: 22, rechts: 22, unten: 46, links: 74 };

/** Die Vergleichslinie: zurückhaltend, sie ist nur Vergleich. */
const VERGLEICH = '#8895a8';

/** Die massgebende Resistenzlinie -- gegen sie wird nachgewiesen. */
const MASSGEBEND = '#1f5fa8';

/** Die eigene Linie des Knickens, wenn es anders wählt als die Tragsicherheit. */
const KNICKLINIE = '#9a5b13';

// ===========================================================================
// Die Karten
// ===========================================================================

/**
 * Die Karten einer Platte: ihr Querschnitt, die Interaktionslinien, die
 * Querkraftkurven und die Spannung-Dehnung-Analysen.
 */
export function plattenkarten(kennung, eintrag, loesung) {
  const eigene = Object.values(loesung.linien || {}).filter((linie) => linie.bauteil === kennung);
  const querschnitt = querschnittZeichnen(eintrag, loesung.werte || {});
  return [
    karte('Querschnitt', [querschnitt], { bild: querschnitt }),
    ...eigene.map((linie) => diagrammZeichnen(linie))
      .map((bild) => karte('M-N-Interaktionsdiagramm', [bild], { bild })),
    ...querkraftkurven(loesung, kennung),
    ...neigungskurven(loesung, kennung),
    ...spannungskarten(kennung, loesung),
  ];
}

/**
 * Die M-V-Kurven einer Platte -- bis zu vier.
 *
 * Je Tragrichtung und Momentenvorzeichen eine, aber nur dort, wo auch ein
 * Querkraftnachweis geführt wurde. Der Kern sagt selbst, welche es gibt; hier
 * wird nichts abgeleitet.
 *
 * Unter jeder Kurve steht die Normalkraft, für die sie gilt: ein Feld der
 * Platte, gespeichert mit dem Projekt. Wer es ändert, ändert das Projekt, und
 * der Kern rechnet die Kurve neu -- die Formel bleibt dort, wo sie hingehört.
 * Leer gilt die des ersten Falls; was gilt, sagt der Hinweis des Kerns. Die
 * Zahl im Feld kommt aus dem Projekt, nicht aus der Antwort des Kerns -- dort
 * steht nur, womit gerechnet ist. Bis 2026-11-20 hatte die Kurve eine eigene
 * Anfrage und die Normalkraft lebte neben dem Projekt: nach dem Neuladen
 * sprang sie still zurück.
 */
function querkraftkurven(loesung, querschnitt) {
  const alle = Object.entries(loesung.querkraftkurven || {})
    .filter(([, k]) => k.querschnitt === querschnitt);
  const angabe = feldangabe('querschnitt', 'querkraftkurve_normalkraft');
  const gewaehlt = eintragVon(querschnitt)?.querkraftkurve_normalkraft ?? null;

  return alle.map(([, kurve]) => {
    const bild = querkraftkurveZeichnen(kurve);
    return karte(`Querkraft über Moment – ${kurve.name}`, [
      bild,
      el('div.kurvenfuss', {}, [
        el('span.kurvenfuss-name', { text: 'gilt für N_Ed =' }),
        zahlfeld({
          wert: gewaehlt, schritt: 50, angabe,
          leer: null, platzhalter: String(kurve.N_Ed),
          titel: `N in ${angabe.einheit}, Zug positiv; leer: die des ersten Falls. `
            + 'Nur Punkte mit genau diesem N liegen auf der Kurve.',
          beiAenderung: (v) => eintragAendern(querschnitt, (q) => {
            q.querkraftkurve_normalkraft = v;
          }),
        }),
        el('span.einheit', { text: angabe.einheit }),
        el('span.kurvenhinweis', { text: kurve.hinweis }),
      ]),
    ], { bild });
  });
}

/**
 * Die Neigungskurven einer Platte -- nur mit Querkraftbewehrung.
 *
 * Dann hängt der Widerstand nicht mehr am Moment, sondern an der Neigung der
 * Druckdiagonalen; an die Stelle der M-V-Kurve tritt dieses Bild. Ein Bild je
 * statischer Höhe und Neigungsbereich -- beides hängt am einzelnen Fall, und
 * der Kern sagt selbst, welche Bilder es gibt.
 */
function neigungskurven(loesung, querschnitt) {
  const alle = Object.entries(loesung.neigungskurven || {})
    .filter(([, k]) => k.querschnitt === querschnitt);

  return alle.map(([, kurve]) => {
    const bild = neigungskurveZeichnen(kurve);
    return karte(`Querkraft über Neigung – ${kurve.name}`, [
      bild,
      el('div.kurvenfuss', {}, [
        el('span.kurvenfuss-name', { text: `d = ${masszahl(kurve.d, kurve.groessen.d)}` }),
        el('span.kurvenhinweis', {
          text: kurve.zug
            ? `Normalzug: α_min = ${masszahl(kurve.alpha_min, kurve.groessen.alpha)}`
              + ' – unter Zug mindestens 40°. Ausserhalb der Grenzen ist die Kurve blass gezeichnet.'
            : 'Ausserhalb von α_min und α_max ist die Kurve blass gezeichnet.',
        }),
      ]),
    ], { bild });
  });
}

// ===========================================================================
// Die Bilder
// ===========================================================================

/**
 * Wo die Stäbe eines Postens über die Breite liegen, in Millimetern.
 *
 * Gezeichnet wird die **echte Teilung**: der Abstand zwischen zwei Stäben im
 * Bild ist derselbe, der eingegeben wurde. Eine Zulage mit ⌀12@250 steht damit
 * sichtbar weiter auseinander als eine Grundbewehrung mit ⌀16@150.
 *
 * Das war einmal anders gelöst -- die Stäbe wurden gleichmässig über `b`
 * verteilt. Dann sahen 150 und 140 gleich aus, weil beide auf dieselbe Stabzahl
 * führten und die Zeichnung nur die Zahl kannte, nicht den Abstand.
 *
 * Die Reihe wird in der Breite mittig gesetzt, damit sie nicht einseitig
 * ausfranst, wenn die Teilung nicht glatt aufgeht.
 *
 * `zwischen` setzt die Reihe in die Lücken der anderen: einen Stab weniger,
 * dadurch rückt sie um eine halbe Teilung ein. So wird die Zulage auch wirklich
 * eingelegt. Der Preis ist ein gezeichneter Stab weniger als `b / s` -- in
 * einem Schnittbild ist das verschmerzbar, und die genaue Menge steht ohnehin
 * als Text daneben.
 */
export function stabstellen(breite, bewehrung) {
  const teilung = bewehrung.abstand > 0
    ? bewehrung.abstand
    : breite / Math.max(1, Math.round(bewehrung.anzahl || 0));
  if (!(teilung > 0) || !Number.isFinite(teilung)) return [];

  const anzahl = Math.max(1, Math.round(breite / teilung));
  const spanne = (anzahl - 1) * teilung;
  const anfang = (breite - spanne) / 2;
  return Array.from({ length: anzahl }, (_, i) => anfang + i * teilung);
}

/**
 * Verschiebt eine ganze Stabreihe so, dass sie den vorhandenen am besten ausweicht.
 *
 * Die Reihe wird **als Ganzes** gerückt, nie einzelne Stäbe. Das ist der
 * Unterschied, auf den es ankommt: einzeln zu rücken hielte zwar alle Kreise
 * auseinander, verböge aber die Teilung -- eine Zulage mit ⌀12@250 sähe dann
 * aus wie ⌀12@267. Die Teilung ist aber genau das, was man im Bild ablesen
 * können soll.
 *
 * Gesucht wird der Versatz mit dem grössten Abstand zum nächsten vorhandenen
 * Stab, innerhalb dessen, was der Rand hergibt. Bei gleicher Teilung kommt
 * dabei von selbst die halbe Teilung heraus -- die Zulage landet in den Lücken,
 * so wie sie auch eingelegt wird.
 *
 * @param {number[]} stellen      Sollstellen der neuen Reihe, in mm
 * @param {number[]} vorhanden    Stellen der schon gezeichneten Reihen, in mm
 * @param {number}   spielraum    wie weit die Reihe höchstens rücken darf, in mm
 */
export function besterVersatz(stellen, vorhanden, spielraum, schritte = 48) {
  if (!stellen.length || !vorhanden.length || spielraum <= 0) return 0;

  const abstandBei = (versatz) => Math.min(...stellen.map((s) =>
    Math.min(...vorhanden.map((v) => Math.abs(s + versatz - v)))));

  let bester = 0;
  let weiteste = abstandBei(0);
  for (let i = 1; i <= schritte; i++) {
    for (const richtung of [1, -1]) {
      const versatz = richtung * spielraum * (i / schritte);
      const abstand = abstandBei(versatz);
      if (abstand > weiteste + 1e-9) {
        weiteste = abstand;
        bester = versatz;
      }
    }
  }
  return bester;
}

/**
 * Wie weit eine Reihe rücken darf, ohne aus dem Querschnitt zu laufen.
 *
 * Höchstens eine halbe Teilung -- weiter zu rücken brächte nichts, weil sich
 * das Bild dann wiederholt.
 */
export function spielraum(breite, stellen, randabstand) {
  if (stellen.length === 0) return 0;
  const links = stellen[0] - randabstand;
  const rechts = breite - randabstand - stellen[stellen.length - 1];
  const halbeTeilung = stellen.length > 1
    ? (stellen[1] - stellen[0]) / 2
    : breite / 2;
  return Math.max(0, Math.min(links, rechts, halbeTeilung));
}

/**
 * Wo die Bügelstriche stehen, in mm ab dem linken Rand.
 *
 * `soll` ist die Reihe in ihrer Teilung, schon als Ganzes so verschoben, dass
 * sie den Stäben am besten ausweicht (siehe `besterVersatz`) -- die Teilung
 * soll man ablesen können. Trifft danach noch ein Strich einen x-Stab, rückt
 * er allein an den Rand des Kreises, auf die nächste freie Seite: so, wie ein
 * Bügelschenkel neben dem Längsstab liegt und nicht durch ihn hindurch.
 * `kreise` in mm ({mm, r}), `luft` der halbe Strich samt Abstand.
 */
function buegelStellen(soll, kreise, luft, breite) {
  const frei = (mm) => kreise.every((k) => Math.abs(mm - k.mm) >= k.r + luft);
  return soll.map((mm) => [mm, ...kreise.flatMap((k) => [k.mm - k.r - luft, k.mm + k.r + luft])]
    .filter((stelle) => stelle >= 0 && stelle <= breite)
    .sort((a, c) => Math.abs(a - mm) - Math.abs(c - mm))
    .find(frei) ?? mm);
}

/**
 * Zeichnet den Plattenquerschnitt mit seinen vier Bewehrungslagen.
 *
 * Gezeigt wird ein Schnitt senkrecht zur x-Achse: Stäbe in x-Richtung sind
 * angeschnitten (Kreise), Stäbe in y-Richtung laufen in der Schnittebene
 * (Balken). Die Bügel stehen senkrecht, von der Unterkante der 1. bis zur
 * Oberkante der 4. Lage, im Abstand ihrer Teilung in y -- in dieser Richtung
 * läuft der Schnitt. Sämtliche Höhenlagen stammen aus der Lösung -- hier wird
 * nichts nachgerechnet.
 */
export function querschnittZeichnen(eintrag, werte) {
  const zahl = (id) => (werte[id] ? werte[id].zahl : null);
  const h = zahl(eintrag.werte.h);
  const b = zahl(eintrag.werte.b);
  const mass = (name, id) => `${name} = ${masszahl(werte[id].zahl, werte[id], 0)}`;
  if (!h || !b) return el('div.leer', { text: 'Geometrie fehlt.' });

  const BREITE = 660;
  const RAND = { oben: 26, unten: 40, links: 62, rechts: 168 };
  const zeichenBreite = BREITE - RAND.links - RAND.rechts;
  // Massstab so, dass die Platte gut sichtbar bleibt, ohne die Höhe zu verzerren.
  const massstab = zeichenBreite / b;
  const zeichenHoehe = h * massstab;
  const HOEHE = zeichenHoehe + RAND.oben + RAND.unten;

  const x = (mm) => RAND.links + mm * massstab;
  const y = (mm) => RAND.oben + mm * massstab;

  const svg = svgEl('svg', {
    class: 'qs', viewBox: `0 0 ${BREITE} ${HOEHE}`, xmlns: NR,
    role: 'img', 'aria-label': 'Plattenquerschnitt',
  });

  svg.append(svgEl('rect', {
    x: x(0), y: y(0), width: b * massstab, height: zeichenHoehe,
    fill: '#eceff4', stroke: '#7b8794', 'stroke-width': 1.6,
  }));

  // Dieselben Farben wie die Lagen in der Maske -- aus dem Stil. Die
  // Beschriftung in der tiefen Fassung: gelbe Schrift auf Weiss liest niemand.
  const farbe = { x: stilfarbe('richtung-x'), y: stilfarbe('richtung-y') };
  const schrift = { x: stilfarbe('richtung-x-tief'), y: stilfarbe('richtung-y-tief') };
  const violett = stilfarbe('beide');
  const zettel = [];
  // Schon gezeichnete Stäbe, in Millimetern -- damit die nächste Reihe weiss,
  // wem sie ausweichen muss.
  const gesetzt = [];

  // Zwei Durchgänge: erst die längs laufenden y-Stäbe, dann die angeschnittenen
  // x-Stäbe darüber. So bleiben die Kreise sichtbar, ohne dass die y-Stäbe
  // durchscheinend gezeichnet werden müssten -- halbdurchsichtig liess sich
  // ihre Dicke nicht mehr ablesen.
  const laengs = eintrag.bewehrung.filter((bew) => bew.richtung === 'y');
  const quer = eintrag.bewehrung.filter((bew) => bew.richtung !== 'y');

  for (const bew of laengs) {
    const z = zahl(bew.z_id);
    if (z === null) continue;
    const dicke = (bew.phi || 12) * massstab;
    // Als Rechteck und nicht als Linie mit runden Enden: die Kappen ragten um
    // einen halben Durchmesser über den Beton hinaus, und genau so weit war
    // der Stab dann zu lang.
    svg.append(svgEl('rect', {
      x: x(0), y: y(z) - dicke / 2, width: b * massstab, height: Math.max(dicke, 1.6),
      fill: farbe.y, opacity: bew.art === 'zulage' ? 0.6 : 0.85,
    }));
    zettel.push({
      soll: y(z), anker: y(z), farbe: farbe.y, schrift: schrift.y,
      text: `${bew.lage}. ${bew.art === 'grund' ? 'Grund' : 'Zulage'} `
          + `${bew.menge} (${bew.richtung})`,
    });
  }

  // Die Bügel liegen unter den x-Stäben. Gezogen werden ihre Striche aber
  // erst, wenn die Kreise stehen -- ausweichen können sie nur Kreisen, die es
  // schon gibt. Darum hier nur der Platz in der Zeichenfolge.
  const buegelSchicht = svgEl('g');
  svg.append(buegelSchicht);

  for (const bew of quer) {
    const z = zahl(bew.z_id);
    if (z === null) continue;
    const r = Math.max((bew.phi || 12) * massstab / 2, 1.4);
    const stellen = stabstellen(b, bew);
    // Nur Stäbe auf praktisch gleicher Höhe kommen sich ins Gehege.
    const hindernisse = gesetzt
      .filter((g) => Math.abs(g.y - y(z)) < g.r + r)
      .map((g) => g.mm);
    const versatz = besterVersatz(
      stellen, hindernisse, spielraum(b, stellen, (bew.phi || 12) / 2));

    for (const mm of stellen) {
      const stelle = mm + versatz;
      gesetzt.push({ mm: stelle, y: y(z), r });
      svg.append(svgEl('circle', {
        cx: x(stelle), cy: y(z), r,
        fill: farbe.x, stroke: '#fff', 'stroke-width': 0.6,
        opacity: bew.art === 'zulage' ? 0.75 : 1,
      }));
    }
    zettel.push({
      soll: y(z), anker: y(z), farbe: farbe.x, schrift: schrift.x,
      text: `${bew.lage}. ${bew.art === 'grund' ? 'Grund' : 'Zulage'} `
          + `${bew.menge} (${bew.richtung})`,
    });
  }

  // Die Bügel: Teilung in y oder Anzahl über die Breite, wie eingegeben.
  const phiV = zahl(eintrag.werte['querkraft.phi']);
  const kanten = eintrag.bewehrung
    .map((bew) => ({ z: zahl(bew.z_id), r: (bew.phi || 12) / 2 }))
    .filter((k) => k.z !== null);
  const mitBuegeln = phiV > 0 && kanten.length > 0;
  if (mitBuegeln) {
    const oben = Math.min(...kanten.map((k) => k.z - k.r));    // OK 4. Lage
    const unten = Math.max(...kanten.map((k) => k.z + k.r));   // UK 1. Lage
    const sY = zahl(eintrag.werte['querkraft.s_y']);
    const reihe = stabstellen(b, sY ? { abstand: sY } : { anzahl: zahl(eintrag.werte['querkraft.n_y']) });
    const versatz = besterVersatz(reihe, gesetzt.map((g) => g.mm), spielraum(b, reihe, phiV / 2));
    const buegelbreite = Math.max(phiV * massstab, 1.2);
    const kreise = gesetzt.map((g) => ({ mm: g.mm, r: g.r / massstab }));
    const soll = reihe.map((mm) => mm + versatz);
    for (const mm of buegelStellen(soll, kreise, (buegelbreite / 2 + 1) / massstab, b)) {
      buegelSchicht.append(svgEl('line', {
        x1: x(mm), y1: y(oben), x2: x(mm), y2: y(unten),
        stroke: violett, 'stroke-width': buegelbreite,
      }));
    }
  }

  for (const z of beschriftungenEntzerren(zettel, 13, RAND.oben, HOEHE - RAND.unten)) {
    const links = BREITE - RAND.rechts + 10;
    // Hat der Zettel ausweichen müssen, zeigt ein Strich auf die wahre Höhe --
    // sonst stünde die Beschriftung auf einer Lage, zu der sie nicht gehört.
    if (Math.abs(z.y - z.anker) > 0.5) {
      svg.append(svgEl('polyline', {
        points: `${x(b) + 3},${z.anker} ${links - 6},${z.anker} `
              + `${links - 3},${z.y} ${links - 1},${z.y}`,
        fill: 'none', stroke: z.farbe, 'stroke-width': 0.8, opacity: 0.5,
      }));
    }
    const beschriftung = svgEl('text', {
      x: links, y: z.y + 3.5, 'font-size': 10.5, fill: z.schrift,
    });
    beschriftung.textContent = z.text;
    svg.append(beschriftung);
  }

  // Höhenmass links
  svg.append(svgEl('line', {
    x1: RAND.links - 16, y1: y(0), x2: RAND.links - 16, y2: y(h),
    stroke: '#56657a', 'stroke-width': 1,
  }));
  for (const [wert, text] of [[0, 'OK'], [h, 'UK']]) {
    svg.append(svgEl('line', {
      x1: RAND.links - 21, y1: y(wert), x2: RAND.links - 11, y2: y(wert),
      stroke: '#56657a', 'stroke-width': 1,
    }));
    const m = svgEl('text', {
      x: RAND.links - 25, y: y(wert) + 4, 'text-anchor': 'end',
      'font-size': 10.5, fill: '#56657a',
    });
    m.textContent = text;
    svg.append(m);
  }
  const masstext = svgEl('text', {
    x: 14, y: RAND.oben + zeichenHoehe / 2, 'font-size': 11, fill: '#16202c',
    'font-weight': 600, 'text-anchor': 'middle',
    transform: `rotate(-90 14 ${RAND.oben + zeichenHoehe / 2})`,
  });
  masstext.textContent = mass('h', eintrag.werte.h);
  svg.append(masstext);

  const breitentext = svgEl('text', {
    x: RAND.links + (b * massstab) / 2, y: HOEHE - 12,
    'text-anchor': 'middle', 'font-size': 11, fill: '#16202c', 'font-weight': 600,
  });
  breitentext.textContent = mass('b', eintrag.werte.b);
  svg.append(breitentext);

  return el('div.diagramm-huelle', {}, [
    svg,
    legende([
      [punkt(farbe.x), 'x-Richtung (angeschnitten)'],
      [strich(farbe.y, { breite: 3 }), 'y-Richtung (durchgezogen, in der Schnittebene)'],
      // Der Bügel steht im Bild senkrecht, und so auch seine Probe.
      mitBuegeln ? [el('i', {
        style: { background: violett, borderRadius: '1px', width: '3px', height: '12px' },
      }), 'Querkraftbewehrung (Abstand wie Teilung y)'] : null,
      'blasser = Zulage',
    ]),
  ]);
}

export function diagrammZeichnen(linie) {
  const { M: gM, N: gN } = linie.groessen;
  const massgebend = linie.massgebend;
  const vergleich = linie.vergleich;
  const knicklinie = linie.knicklinie;
  if (!massgebend?.punkte?.length) return el('div.leer', { text: 'Keine Resistenzlinie.' });
  const alle = [...massgebend.punkte, ...(vergleich?.punkte || []), ...(knicklinie?.punkte || [])];

  const alleM = alle.map((p) => p.M);
  const alleN = alle.map((p) => p.N);
  for (const k of linie.kombinationen) { alleM.push(k.M_Ed); alleN.push(k.N_Ed); }
  // Auch die Knickpunkte: sonst liegt der mit dem grössten Moment zweiter
  // Ordnung ausserhalb des gezeichneten Bereichs.
  for (const k of (linie.knickfaelle || [])) {
    alleM.push(k.M_Ed_1, k.M_Ed_II, k.M_bei_N_Rd);
    alleN.push(k.N_Ed, -Math.abs(k.N_Rd));
  }

  const spielraum = 0.08;
  const mSpanne = (Math.max(...alleM) - Math.min(...alleM)) || 1;
  const nSpanne = (Math.max(...alleN) - Math.min(...alleN)) || 1;
  const mMin = Math.min(...alleM) - mSpanne * spielraum;
  const mMax = Math.max(...alleM) + mSpanne * spielraum;
  const nMin = Math.min(...alleN) - nSpanne * spielraum;
  const nMax = Math.max(...alleN) + nSpanne * spielraum;

  const { svg, daten, x, y } = achsenkreuz({
    breite: BREITE, hoehe: HOEHE, rand: RAND,
    attribute: {
      class: 'mn', xmlns: NR, role: 'img', 'aria-label': 'M-N-Interaktionsdiagramm',
    },
    x: { bereich: [mMin, mMax], teilung: {}, null: true, titel: achsentitel(gM) },
    y: {
      bereich: [nMin, nMax], teilung: {}, null: true, titel: `${achsentitel(gN)}   (Zug positiv)`,
    },
  });

  // -- Die beiden Resistenzlinien ------------------------------------------
  // Die Vergleichslinie: dünn, ohne Füllung. Gefüllt und kräftig ist die
  // massgebende -- gegen sie wird nachgewiesen, und sie soll den Blick auf
  // sich ziehen. Eckpunkte mit Namen hat nur das Polygon der Handrechnung.
  const zug = (punkte) => punkte.map((p) => `${x(p.M).toFixed(2)},${y(p.N).toFixed(2)}`).join(' ');
  if (vergleich?.punkte?.length) {
    daten.append(svgEl('polygon', {
      points: zug(vergleich.punkte),
      fill: 'none', stroke: VERGLEICH, 'stroke-width': 1.3,
      'stroke-dasharray': '6 3', 'stroke-linejoin': 'round', opacity: 0.8,
    }));
  }
  if (knicklinie?.punkte?.length) {
    daten.append(svgEl('polygon', {
      points: zug(knicklinie.punkte),
      fill: 'none', stroke: KNICKLINIE, 'stroke-width': 1.4,
      'stroke-dasharray': '2 3', 'stroke-linejoin': 'round', opacity: 0.9,
    }));
  }
  daten.append(svgEl('polygon', {
    points: zug(massgebend.punkte),
    fill: 'rgba(31,95,168,.07)', stroke: MASSGEBEND, 'stroke-width': 2,
    'stroke-linejoin': 'round',
  }));
  if (massgebend.ecken) {
    for (const p of massgebend.punkte) {
      const ecke = svgEl('circle', {
        cx: x(p.M), cy: y(p.N), r: 3, fill: MASSGEBEND,
        stroke: '#fff', 'stroke-width': 1.2,
      });
      const t = svgEl('title');
      t.textContent = `${p.name}\nM = ${masszahl(p.M, gM)}, N = ${masszahl(p.N, gN)}`;
      ecke.append(t);
      daten.append(ecke);
    }
  }

  // -- Bemessungspunkte ----------------------------------------------------
  for (const k of linie.kombinationen) {
    bemessungspunkt(daten, {
      ein: [x(k.M_Ed), y(k.N_Ed)],
      widerstand: k.widerstand ? [x(k.widerstand.M), y(k.widerstand.N)] : null,
      farbe: urteilsfarbe(k.innerhalb),
      name: k.name,
      // Der Grad kommt fertig gesetzt aus dem Kern: gerundet stuende bei
      // 0.9996 «1.000» neben «NICHT erfüllt».
      titel: `${k.name}\nM_Ed = ${masszahl(k.M_Ed, gM)}, N_Ed = ${masszahl(k.N_Ed, gN)}`
        + `\nErfüllungsgrad α_eff = ${k.grad_text} (${k.massstab_text})`
        + `\n${k.innerhalb ? 'erfüllt' : 'NICHT erfüllt'}`,
    });
  }

  // -- Knicknachweise ------------------------------------------------------
  // Drei Punkte und eine Kette dazwischen:
  //   1. Einwirkung 1. Ordnung   (M_Ed,1  | N_Ed)
  //   2. am verformten System    (M_Ed,II | N_Ed)   -- der Zuwachs
  //   3. Widerstand              (M_Rd    | N_Rd)   -- auf der Linie
  // Die Strecke 1-2 ist, was Schiefstellung und Verformung dazulegen; die
  // Strecke 2-3, wie weit es bis zum Versagen noch ist.
  for (const k of (linie.knickfaelle || [])) {
    const farbe = urteilsfarbe(k.erfuellt);
    const eins = [x(k.M_Ed_1), y(k.N_Ed)];
    const zwei = [x(k.M_Ed_II), y(k.N_Ed)];
    const drei = [x(k.M_bei_N_Rd), y(-Math.abs(k.N_Rd))];

    for (const [von, bis, muster] of [[eins, zwei, '2 3'], [zwei, drei, '5 4']]) {
      daten.append(svgEl('line', {
        x1: von[0], y1: von[1], x2: bis[0], y2: bis[1],
        stroke: farbe, 'stroke-width': 1.6, 'stroke-dasharray': muster, opacity: .85,
      }));
    }

    // Erster Punkt: klein und hohl -- die Einwirkung vor der Verformung.
    daten.append(svgEl('circle', {
      cx: eins[0], cy: eins[1], r: 3.5,
      fill: '#fff', stroke: farbe, 'stroke-width': 1.6,
    }));

    // Zweiter: gefüllte Raute, das ist die massgebende Einwirkung.
    const s = 6;
    const raute = svgEl('polygon', {
      points: [[zwei[0], zwei[1] - s], [zwei[0] + s, zwei[1]],
        [zwei[0], zwei[1] + s], [zwei[0] - s, zwei[1]]]
        .map((q) => q.map((v) => v.toFixed(2)).join(',')).join(' '),
      fill: farbe, stroke: '#fff', 'stroke-width': 2,
    });
    const kt = svgEl('title');
    kt.textContent =
      `Knicken – ${k.name}\nN_Ed = ${masszahl(k.N_Ed, gN)}`
      + `\nM_Ed,1 = ${masszahl(k.M_Ed_1, gM)} → M_Ed,II = ${masszahl(k.M_Ed_II, gM)}`
      + `\nN_Rd = ${masszahl(k.N_Rd, gN)} bei M = ${masszahl(k.M_bei_N_Rd, gM)}`
      + `\nα_eff = ${k.grad_text} – ${k.erfuellt ? 'erfüllt' : 'NICHT erfüllt'}`;
    raute.append(kt);
    daten.append(raute);

    // Dritter: der Widerstandspunkt, wie bei den Kombinationen hohl.
    daten.append(svgEl('circle', {
      cx: drei[0], cy: drei[1], r: 4.5,
      fill: '#fff', stroke: farbe, 'stroke-width': 1.8,
    }));

    const marke = svgEl('text', {
      x: zwei[0] + 9, y: zwei[1] + 14,
      'font-size': 11, 'font-weight': 600, fill: farbe,
    });
    marke.textContent = `K: ${k.name}`;
    daten.append(marke);
  }

  return el('div.diagramm-huelle', {}, [
    svg,
    legende([
      [strich(MASSGEBEND, { breite: 2 }), `Resistenzlinie: ${massgebend.beschriftung} (massgebend)`],
      vergleich ? [strich(VERGLEICH, { muster: '6 3', breite: 1.3 }),
        `${vergleich.beschriftung} (nur Vergleich)`] : null,
      knicklinie ? [strich(KNICKLINIE, { muster: '2 3', breite: 1.4 }),
        `Knicken: ${knicklinie.beschriftung}`] : null,
      ...urteilslegende(),
      '– – –  gemessener Weg zur Linie',
    ]),
  ]);
}

/**
 * Zeichnet den Querkraftwiderstand über dem Moment -- ein Bild je Tragrichtung.
 *
 * Die Waagrechte ist vorzeichenbehaftet: rechts das positive Moment (Zug
 * unten), links das negative (Zug oben). Beide Äste im selben Bild, weil sie
 * dieselbe Platte beschreiben; getrennt liessen sie sich schlecht vergleichen.
 *
 * Sie treffen sich bei M_Ed = 0 nicht unbedingt: jeder misst mit seiner
 * eigenen statischen Höhe. Das ist kein Zeichenfehler, sondern die Platte.
 *
 * JENSEITS VON m_Rd:
 * Jeder Ast läuft 20 kNm über seinen Momentenwiderstand hinaus. Dort fliesst
 * die Bewehrung, ε_v springt auf einen festen Wert und der Widerstand bleibt
 * danach konstant -- gestrichelt gezeichnet, damit der Absatz nicht wie ein
 * Rechenfehler aussieht.
 *
 * AUSGEGRAUT:
 * Ein Bemessungspunkt gehört nur dann auf diese Kurve, wenn seine Normalkraft
 * die eingestellte ist. Sonst läge er dort, wo er nicht hingehört. Statt ihn
 * wegzulassen, wird er blass gezeichnet -- er ist ja vorhanden, nur eben zu
 * einer anderen Kurve.
 *
 * Gerechnet wird nichts: die Punkte kommen aus dem Kern, aus derselben
 * Funktion wie der Nachweis.
 */
export function querkraftkurveZeichnen(kurve) {
  const { M: gM, v: gv, N: gN } = kurve.groessen;
  const aeste = kurve.aeste || [];
  const faelle = kurve.faelle || [];
  if (!aeste.length) {
    return el('div.leer', {
      text: 'Kein Momentenwiderstand bei diesem N → keine Kurve.',
    });
  }

  const passt = (fall) => Math.abs(fall.N_Ed - kurve.N_Ed) < 1e-6;
  const alleP = aeste.flatMap((a) => a.punkte);
  const alleM = [0, ...alleP.map((p) => p.M_Ed), ...faelle.map((f) => f.M_Ed)];
  const alleV = [0, ...alleP.map((p) => p.v_Rd), ...faelle.map((f) => f.V_Ed)];

  const mMin = Math.min(...alleM) * 1.04;
  const mMax = Math.max(...alleM) * 1.04;
  const vMax = Math.max(...alleV) * 1.12;

  // Die Nulllinie trennt Zug unten von Zug oben und gehört betont.
  const { svg, daten, x, y, feld } = achsenkreuz({
    breite: BREITE, hoehe: HOEHE, rand: RAND,
    attribute: {
      class: 'mv', xmlns: NR, role: 'img', 'aria-label': 'Querkraftwiderstand über dem Moment',
    },
    x: { bereich: [mMin, mMax], teilung: {}, null: true, titel: achsentitel(gM) },
    y: { bereich: [0, vMax], teilung: {}, titel: achsentitel(gv) },
  });

  for (const [m, text] of [[mMin, 'Zug oben'], [mMax, 'Zug unten']]) {
    const t = svgEl('text', {
      x: x(m / 2), y: feld.unten - 7, 'text-anchor': 'middle',
      'font-size': 11, fill: '#8895a8',
    });
    t.textContent = text;
    daten.append(t);
  }

  // -- Die Äste ------------------------------------------------------------
  for (const ast of aeste) {
    daten.append(svgEl('line', {
      x1: x(ast.m_Rd), y1: feld.oben, x2: x(ast.m_Rd), y2: feld.unten,
      stroke: '#1f5fa8', 'stroke-width': 1.4, 'stroke-dasharray': '4 4', opacity: .7,
    }));
    const marke = svgEl('text', {
      x: x(ast.m_Rd) + (ast.seite === 'unten' ? -6 : 6), y: feld.oben + 13,
      'text-anchor': ast.seite === 'unten' ? 'end' : 'start',
      'font-size': 11, 'font-weight': 600, fill: '#1f5fa8',
    });
    marke.textContent = `${kurve.m_name || 'm_Rd'} = ${masszahl(ast.m_Rd, gM)}`;
    daten.append(marke);

    // Zwei Züge: bis m_Rd durchgezogen, darüber gestrichelt.
    for (const gestrichelt of [false, true]) {
      const teil = ast.punkte.filter((p) => p.plastisch === gestrichelt);
      if (teil.length < 2) continue;
      daten.append(svgEl('polyline', {
        points: teil.map((p) => `${x(p.M_Ed).toFixed(2)},${y(p.v_Rd).toFixed(2)}`).join(' '),
        fill: 'none', stroke: '#1f5fa8', 'stroke-width': 2.2,
        'stroke-linejoin': 'round', 'stroke-dasharray': gestrichelt ? '7 4' : null,
      }));
    }
  }

  // -- Marken --------------------------------------------------------------
  // Je Ast der Wert genau bei m_Rd und die Waagrechte danach, dazu einmal der
  // Höchstwert. Mehr Zahlen im Bild helfen niemandem.
  const marken = [];
  const hoechst = alleP.reduce((a, b) => (b.v_Rd > a.v_Rd ? b : a));
  marken.push([hoechst, 'max v_Rd', true]);
  for (const ast of aeste) {
    const elastisch = ast.punkte.filter((p) => !p.plastisch);
    const plastisch = ast.punkte.filter((p) => p.plastisch);
    if (elastisch.length) marken.push([elastisch.at(-1), `v_Rd bei ${kurve.m_name || 'm_Rd'}`, true]);
    if (plastisch.length) marken.push([plastisch[0], 'v_Rd nach Fliessbeginn', false]);
  }
  for (const [p, name, oben] of marken) {
    daten.append(svgEl('circle', {
      cx: x(p.M_Ed), cy: y(p.v_Rd), r: 4,
      fill: '#fff', stroke: '#1f5fa8', 'stroke-width': 2,
    }));
    const rechts = x(p.M_Ed) > feld.links + (feld.rechts - feld.links) * 0.62;
    const t = svgEl('text', {
      x: x(p.M_Ed) + (rechts ? -8 : 8),
      y: y(p.v_Rd) + (oben ? -9 : 17),
      'text-anchor': rechts ? 'end' : 'start',
      'font-size': 11, 'font-weight': 600, fill: '#1f5fa8',
    });
    t.textContent = `${name} = ${masszahl(p.v_Rd, gv)}`;
    daten.append(t);
  }

  // -- Bemessungspunkte ----------------------------------------------------
  // Senkrecht von der Einwirkung hinauf zum Widerstand auf der Kurve.
  for (const f of faelle) {
    const gilt = passt(f);
    bemessungspunkt(daten, {
      ein: [x(f.M_Ed), y(f.V_Ed)],
      widerstand: [x(f.M_Ed), y(f.v_Rd)],
      farbe: urteilsfarbe(f.erfuellt),
      name: f.name,
      titel: `${f.name}\nM_Ed = ${masszahl(f.M_Ed, gM)}, |V_Ed| = ${masszahl(f.V_Ed, gv)}`
        + `\nN_Ed = ${masszahl(f.N_Ed, gN)}, v_Rd = ${masszahl(f.v_Rd, gv)}`
        + `\n${f.erfuellt ? 'erfüllt' : 'NICHT erfüllt'}`
        + (f.begruendung ? `\n${f.begruendung}` : '')
        + (gilt ? '' : `\nGilt für N_Ed = ${masszahl(f.N_Ed, gN)}, `
                     + `gezeigt ist ${masszahl(kurve.N_Ed, gN)}.`),
      unten: true,
      deckung: gilt ? 1 : 0.28,
    });
  }

  return svg;
}

/**
 * Der Querkraftwiderstand über der Neigung der Druckdiagonalen.
 *
 * Zwei Äste: die Bügel (blau) werden mit flacherer Diagonale stärker, die
 * Druckdiagonale selbst (orange) ist bei 45° am stärksten. Massgebend ist
 * überall das Kleinere von beiden -- die dicke Linie darunter.
 *
 * AUSSERHALB DER GRENZEN:
 * Gezeichnet wird über den ganzen Achsenbereich, blass jedoch, wo die Neigung
 * ausserhalb von α_min und α_max liegt. Ein dort abgeschnittener Ast liesse
 * offen, ob die Kurve endet oder der Bereich.
 *
 * Gerechnet wird nichts: die Punkte kommen aus dem Kern, aus derselben
 * Funktion wie der Nachweis.
 */
export function neigungskurveZeichnen(kurve) {
  const { alpha: gAlpha, V: gV } = kurve.groessen;
  const punkte = kurve.punkte || [];
  const faelle = kurve.faelle || [];
  if (punkte.length < 2) {
    return el('div.leer', { text: 'Kein Neigungsbereich.' });
  }

  const BUEGEL = '#1f5fa8';
  const DIAGONALE = '#c96a1b';

  const alleV = [0, ...punkte.map((p) => p.V_Rd_s), ...punkte.map((p) => p.V_Rd_c),
    ...faelle.map((f) => f.V_Ed)];
  const aMin = punkte[0].alpha;
  const aMax = punkte.at(-1).alpha;
  const vMax = Math.max(...alleV) * 1.12 || 1;

  const { svg, daten, x, y, feld } = achsenkreuz({
    breite: BREITE, hoehe: HOEHE, rand: RAND,
    attribute: {
      class: 'mv', xmlns: NR, role: 'img',
      'aria-label': 'Querkraftwiderstand über der Neigung der Druckdiagonalen',
    },
    x: {
      bereich: [aMin, aMax],
      // Ganze Grade: eine Teilung in halben stünde für eine Genauigkeit, die
      // die Suche nicht hat -- sie geht gradweise.
      teilung: {
        schritt: Math.max(1, schrittweite((aMax - aMin) || 1)),
        format: (a) => masszahl(Math.round(a), gAlpha),
      },
      titel: `${gAlpha.zeichen} – Neigung der Druckdiagonalen [${gAlpha.einheit}]`,
    },
    y: { bereich: [0, vMax], teilung: {}, titel: achsentitel(gV) },
  });

  // -- Der zulässige Bereich -----------------------------------------------
  daten.append(svgEl('rect', {
    x: x(kurve.alpha_min), y: feld.oben,
    width: Math.max(0, x(kurve.alpha_max) - x(kurve.alpha_min)),
    height: feld.unten - feld.oben,
    fill: '#1f6feb', opacity: 0.05,
  }));
  for (const [a, text] of [[kurve.alpha_min, 'α_min'], [kurve.alpha_max, 'α_max']]) {
    daten.append(svgEl('line', {
      x1: x(a), y1: feld.oben, x2: x(a), y2: feld.unten,
      stroke: '#8895a8', 'stroke-width': 1.3, 'stroke-dasharray': '4 4',
    }));
    const t = svgEl('text', {
      x: x(a) + 5, y: feld.oben + 13, 'font-size': 11, fill: '#5c6773',
    });
    t.textContent = `${text} = ${masszahl(a, gAlpha)}`;
    daten.append(t);
  }

  // -- Die beiden Äste ------------------------------------------------------
  // Je Ast zwei Züge: innerhalb der Grenzen kräftig, ausserhalb blass. Der
  // Übergang gehört zu beiden, sonst klaffte an der Grenze eine Lücke.
  const zug = (wert, farbe, drin) => {
    const teil = punkte.filter((p, i) => p.im_bereich === drin
      || (punkte[i - 1] && punkte[i - 1].im_bereich === drin)
      || (punkte[i + 1] && punkte[i + 1].im_bereich === drin));
    const stuecke = [];
    let lauf = [];
    for (const p of punkte) {
      if (teil.includes(p)) lauf.push(p);
      else if (lauf.length) { stuecke.push(lauf); lauf = []; }
    }
    if (lauf.length) stuecke.push(lauf);
    return stuecke.filter((s) => s.length > 1).map((s) => svgEl('polyline', {
      points: s.map((p) => `${x(p.alpha).toFixed(2)},${y(p[wert]).toFixed(2)}`).join(' '),
      fill: 'none', stroke: farbe, 'stroke-width': drin ? 2.4 : 1.6,
      'stroke-linejoin': 'round', opacity: drin ? 1 : 0.3,
    }));
  };
  for (const [wert, farbe] of [['V_Rd_c', DIAGONALE], ['V_Rd_s', BUEGEL]]) {
    for (const drin of [false, true]) daten.append(...zug(wert, farbe, drin));
  }

  // Der massgebende Verlauf: das Kleinere von beiden, als kräftige Linie.
  const drin = punkte.filter((p) => p.im_bereich);
  if (drin.length > 1) {
    daten.append(svgEl('polyline', {
      points: drin.map((p) => `${x(p.alpha).toFixed(2)},${y(p.V_Rd).toFixed(2)}`).join(' '),
      fill: 'none', stroke: '#16202c', 'stroke-width': 3.2,
      'stroke-linejoin': 'round', opacity: 0.85,
    }));
  }

  for (const [wert, farbe, text] of [
    ['V_Rd_s', BUEGEL, 'V_Rd,s (Bügel)'],
    ['V_Rd_c', DIAGONALE, 'V_Rd,c (Druckdiagonale)'],
  ]) {
    const letzter = punkte.at(-1);
    const t = svgEl('text', {
      x: x(letzter.alpha) - 6, y: y(letzter[wert]) - 8, 'text-anchor': 'end',
      'font-size': 11, 'font-weight': 600, fill: farbe,
    });
    t.textContent = text;
    daten.append(t);
  }

  // -- Die Bemessungsfälle --------------------------------------------------
  // Senkrecht von der Einwirkung hinauf zum Widerstand bei diesem α.
  for (const f of faelle) {
    bemessungspunkt(daten, {
      ein: [x(f.alpha), y(f.V_Ed)],
      widerstand: [x(f.alpha), y(f.V_Rd)],
      farbe: urteilsfarbe(f.erfuellt),
      name: `${f.name} · V_Ed = ${masszahl(f.V_Ed, gV)}`,
      titel: `${f.name}\nV_Ed = ${masszahl(f.V_Ed, gV)} bei α = ${masszahl(f.alpha, gAlpha)}`
        + `\nV_Rd = ${masszahl(f.V_Rd, gV)}`
        + `\n${f.erfuellt ? 'erfüllt' : 'NICHT erfüllt'}`
        + (f.begruendung ? `\n${f.begruendung}` : ''),
      unten: true,
    });
  }

  return svg;
}
