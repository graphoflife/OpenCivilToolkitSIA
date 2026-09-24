/**
 * nachweise.js -- die untere Hälfte der Plattentafel: was nachgewiesen wird.
 *
 * Vier Kapitel in der Reihenfolge, in der auch der Bericht sie führt:
 * Tragsicherheit (samt Knicken), Duktilität, sprödes Versagen und die
 * Rissbreitenbegrenzung. Dazu das Werkzeug, das die Bewehrung sucht.
 *
 * Eigenes Modul, weil `editor.js` sonst über tausend Zeilen läge und die
 * beiden Hälften wenig miteinander zu tun haben: oben steht, was die Platte
 * *ist* -- Abmessungen, Material, Lagen --, hier steht, was von ihr
 * *verlangt* wird. Geteilt wird nur der Schalter und die Feldzeile, und die
 * stehen in `bausteine.js`.
 *
 * Gerechnet wird hier nichts. Jede Zeile beschreibt eine Eingabe; die Zahlen
 * dazu bildet der Kern, sobald der Nachweis läuft.
 */

import { api } from './api.js';
import { erklaerung, feld, hakenSchalter, lagenwahl, richtungVon, richtungsWahl } from './bausteine.js';
import { auswahl, el, melden, zahlfeld } from './dom.js';
import { aendern, projektAendern, zustand } from './zustand.js';

/**
 * Welche Platte gerade durchsucht wird.
 *
 * Nur das: der Knopf soll währenddessen «sucht …» heissen und nicht zweimal
 * auslösen. Das Ergebnis steht danach in den Lagen und in der
 * Zusammenfassung -- dort sieht man, ob es aufgeht. Ein Satz daneben, grün
 * oder rot, sagte dasselbe ein zweites Mal und blieb stehen, bis man etwas
 * anderes tat.
 *
 * Ausserhalb des Projekts: das ist ein Vorgang und keine Eigenschaft der
 * Platte, und niemand will ihn in der abgelegten Datei.
 */
const laufendeSuche = new Set();

/**
 * Der Knopf, der eine Liste verlängert.
 *
 * Steht unter der Liste und nicht in der Überschrift: dort ist die Stelle,
 * an der die nächste Zeile erscheint, und ein Knopf gehört dorthin, wo seine
 * Wirkung sichtbar wird. Über die ganze Breite und mit gestricheltem Rand --
 * man sieht, dass dort noch etwas hinkommt.
 */
function anfuegenKnopf(text, tun) {
  return el('button.knopf-anfuegen', { text: `+ ${text}`, on: { click: tun } });
}

/**
 * Was am Querschnitt ausgewertet wird, ohne dass es ein Nachweis waere.
 *
 * Eigenes Kapitel, weil hier nichts gegen etwas gehalten wird: kein
 * Erfüllungsgrad, kein Urteil. Unter den Nachweisen zu stehen hiesse, den
 * Unterschied zu verwischen, um den es dabei geht.
 */
export function analysenBlock(querschnitt) {
  return el('div.feldgruppe', {}, [
    el('h3', {}, [el('span', { text: 'Weitere Analysen' }),
      el('span', { text: 'kein Nachweis' })]),
    spannungsBlock(querschnitt),
  ]);
}

/** Die Nachweiskapitel einer Platte, von der Tragsicherheit bis zum Riss. */
export function nachweiseBlock(querschnitt) {
  const aendernAn = (veraenderer) => projektAendern((p) => {
    veraenderer(p.querschnitte.find((x) => x.kennung === querschnitt.kennung));
  });
  return el('div.feldgruppe', {}, [
    el('h3', { text: 'Nachweise' }),
    el('div.unterkapitel', {}, [
      el('div.unterkapitel-kopf', {}, [
        el('span', { text: 'Tragsicherheitsnachweise' }),
      ]),
      querschnitt.kombinationen.length
        ? el('div.einwirkung.ist-kopf', {}, [
          el('span'),
          el('span', { text: 'Bezeichnung' }),
          el('span', { text: 'M_Ed [kNm]' }),
          el('span', { text: 'N_Ed [kN]' }),
          el('span', { text: 'V_Ed [kN/m]' }),
          el('span', { text: 'Ri.' }),
          el('span'),
        ])
        : null,
      ...(querschnitt.kombinationen.length
        ? querschnitt.kombinationen.map((_, i) => einwirkungZeile(querschnitt, i))
        : [el('div.leer', { text: 'Ohne Einwirkung kein Nachweis.' })]),
      anfuegenKnopf('Einwirkung', () => aendernAn((q) => q.kombinationen.push({
        name: `Fall ${q.kombinationen.length + 1}`,
        M_Ed: 30, N_Ed: 0, V_Ed: 0, art: 'automatisch', richtung: 'x',
      }))),
    ]),

    lagenkapitel(querschnitt, {
      titel: 'Duktilitätsnachweise',
      feld: 'duktilitaet',
      // Die beiden äusseren Lagen: sie tragen Feld- und Stützmoment, und dort
      // entscheidet sich, ob der Querschnitt sein Versagen ankündigt.
      vorgabe: [false, false, false, false],
      hinweis: {
        text: 'Begrenzt die Druckzonenhöhe, damit der Querschnitt sein '
          + 'Versagen ankündigt: die Bewehrung fliesst, bevor der Beton '
          + 'bricht. Gerechnet ohne Normalkraft.',
        formel: 'x / d ≤ 0.35   bei M_Ed = 0',
      },
      beschriftung: (n) => `Duktilität ${n}. Lage`,
      was: 'Nachweis',
    }),

    lagenkapitel(querschnitt, {
      titel: 'Nachweise gegen sprödes Versagen',
      feld: 'sproede_lagen',
      vorgabe: [false, false, false, false],
      hinweis: {
        text: 'Die Bewehrung muss aufnehmen, was der Beton im Augenblick des '
          + 'Reissens abgibt. Sonst reisst und versagt der Querschnitt '
          + 'gleichzeitig, ohne Vorankündigung.',
        formel: 'M_Rd(N_Ed = 0) ≥ M_Riss = f_ct,eff · h²·b / 6',
      },
      beschriftung: (n) => `Rissmoment ${n}. Lage`,
      was: 'Nachweis',
    }),

    mindestbewehrungsBlock(querschnitt),
    knickBlock(querschnitt),
  ]);
}

function einwirkungZeile(querschnitt, index) {
  const k = querschnitt.kombinationen[index];
  const aendern = (veraenderer) => projektAendern((p) => {
    veraenderer(p.querschnitte.find((x) => x.kennung === querschnitt.kennung).kombinationen[index]);
  });

  const zahl = (feld, titel, schritt = 10) => zahlfeld({
    wert: k[feld], schritt, titel,
    beiAenderung: (v) => aendern((x) => { x[feld] = v ?? 0; }),
  });

  const an = k.aktiv !== false;
  return el('div.einwirkung', { class: an ? '' : 'ist-aus' }, [
    hakenSchalter(an, (wert) => aendern((x) => { x.aktiv = wert; }), 'Lastfall'),
    el('input.ew-name', {
      type: 'text', value: k.name, title: 'Bezeichnung der Einwirkung',
      on: { change: (e) => aendern((x) => { x.name = e.target.value; }) },
    }),
    zahl('M_Ed', 'Bemessungsmoment in kNm'),
    zahl('N_Ed', 'Normalkraft in kN – Zug positiv, Druck negativ'),
    zahl('V_Ed', 'Querkraft in kN/m – 0 heisst: kein Querkraftnachweis'),
    richtungsWahl(k.richtung || 'beide',
      (wert) => aendern((x) => { x.richtung = wert; })),
    el('button.weg', {
      text: '×', title: 'Einwirkung entfernen',
      on: {
        click: () => projektAendern((p) => {
          p.querschnitte.find((x) => x.kennung === querschnitt.kennung)
            .kombinationen.splice(index, 1);
        }),
      },
    }),
  ]);
}

/**
 * Ein Kapitel mit vier Lagenschaltern -- dieselbe Gestalt wie die Duktilität.
 *
 * Drei Nachweise sind so gebaut (Duktilität, sprödes Versagen, Zwängung auf
 * Biegung); dreimal dieselben zwanzig Zeilen wären dreimal dieselbe Gelegenheit
 * auseinanderzulaufen.
 */
function lagenkapitel(querschnitt, {
  titel, feld, hinweis, beschriftung, was,
  vorgabe = [true, false, false, false],
}) {
  const wahl = lagenwahl(querschnitt[feld], vorgabe);

  const setzen = (nummer, wert) => projektAendern((p) => {
    const q = p.querschnitte.find((x) => x.kennung === querschnitt.kennung);
    q[feld] = lagenwahl(q[feld], vorgabe);
    q[feld][nummer - 1] = wert;
  });

  return el('div.unterkapitel', {}, [
    el('div.unterkapitel-kopf', {}, [
      el('span', { text: titel }),
      hinweis ? erklaerung(hinweis.text, hinweis.formel) : null,
    ]),
    ...[1, 2, 3, 4].map((nummer) => {
      const lage = querschnitt.lagen[nummer - 1];
      const leer = !(lage.grund.durchmesser > 0 || lage.zulage.durchmesser > 0);
      const richtung = richtungVon(querschnitt, nummer);
      // Schalter ganz links, wie bei den Tragsicherheitsnachweisen: das Auge
      // sucht die Spalte einmal und findet sie danach in jedem Kapitel.
      return el('div.duktilitaetszeile', {}, [
        hakenSchalter(wahl[nummer - 1], (wert) => setzen(nummer, wert), was),
        el('span.richtung', {
          text: richtung, class: `lage-${richtung}`,
          title: `Tragrichtung der ${nummer}. Lage`,
        }),
        el('span.postenname', { text: beschriftung(nummer) }),
        // Ein eingeschalteter Nachweis an einer leeren Lage ist kein Fehler
        // der Eingabe -- er wird geführt und meldet selbst, dass er nicht
        // geht. Hier steht es trotzdem, damit man es beim Einschalten sieht.
        el('span.kurvenhinweis', {
          text: (wahl[nummer - 1] && leer) ? 'Lage nicht definiert' : '',
        }),
      ]);
    }),
  ]);
}

/**
 * Knicken -- Druckkraft, Moment 1. Ordnung, Länge und Knicklänge je Fall.
 *
 * Nur in x-Richtung: eine Knicklänge gehört zu einer Tragrichtung, und in y
 * wäre die Breite der Platte die Länge.
 */
function knickBlock(querschnitt) {
  const faelle = querschnitt.knickfaelle || [];
  const aendern = (veraenderer) => projektAendern((p) => {
    veraenderer(p.querschnitte.find((x) => x.kennung === querschnitt.kennung));
  });

  return el('div.unterkapitel', {}, [
    el('div.unterkapitel-kopf', {}, [el('span', { text: 'Knicken' })]),
    faelle.length
      ? el('div.einwirkung.ist-knick.ist-kopf', {}, [
        el('span'),
        el('span', { text: 'Bezeichnung' }),
        el('span', { text: 'N_Ed,x [kN]' }),
        el('span', { text: 'M_Ed,1,x [kNm]' }),
        el('span', { text: 'l [m]' }),
        el('span', { text: 'l_cr [m]' }),
        el('span'),
      ])
      : null,
    ...(faelle.length
      ? faelle.map((_, i) => knickZeile(querschnitt, i))
      : [el('div.leer', { text: 'Kein Knicknachweis – nur in x-Richtung möglich.' })]),
    anfuegenKnopf('Knicknachweis', () => aendern((q) => {
      q.knickfaelle = q.knickfaelle || [];
      q.knickfaelle.push({
        name: `Stütze ${q.knickfaelle.length + 1}`,
        N_Ed: -500, M_Ed_1: 20, laenge: 3, knicklaenge: 3, aktiv: true,
      });
    })),
  ]);
}

function knickZeile(querschnitt, index) {
  const k = (querschnitt.knickfaelle || [])[index];
  const aendern = (veraenderer) => projektAendern((p) => {
    veraenderer(p.querschnitte.find((x) => x.kennung === querschnitt.kennung)
      .knickfaelle[index]);
  });
  const zahl = (feld, titel, schritt) => zahlfeld({
    wert: k[feld], schritt, titel,
    beiAenderung: (v) => aendern((x) => { x[feld] = v ?? 0; }),
  });

  const aktiv = k.aktiv !== false;
  return el('div.einwirkung.ist-knick', { class: aktiv ? '' : 'ist-aus' }, [
    hakenSchalter(aktiv, (wert) => aendern((x) => { x.aktiv = wert; }), 'Knicknachweis'),
    el('input.ew-name', {
      type: 'text', value: k.name, title: 'Bezeichnung des Knicknachweises',
      on: { change: (e) => aendern((x) => { x.name = e.target.value; }) },
    }),
    zahl('N_Ed', 'Druckkraft in kN – negativ, in x-Richtung', 50),
    zahl('M_Ed_1', 'Moment 1. Ordnung in kNm, um die y-Achse (Tragrichtung x)', 10),
    zahl('laenge', 'Systemlänge in m – geht in die Schiefstellung ein', 0.5),
    zahl('knicklaenge', 'Knicklänge in m', 0.5),
    el('button.weg', {
      text: '×', title: 'Knicknachweis entfernen',
      on: {
        click: () => projektAendern((p) => {
          p.querschnitte.find((x) => x.kennung === querschnitt.kennung)
            .knickfaelle.splice(index, 1);
        }),
      },
    }),
  ]);
}

/**
 * Mindestbewehrung: was angesetzt wird und wogegen.
 *
 * Zwei Teile. Oben die Zwängung -- eine Annahme über das Tragwerk, nicht über
 * die Platte, darum ausgeschaltet, bis jemand sie trifft. Unten die häufigen
 * Lastfälle, gegen die später die Stahlspannung begrenzt wird.
 *
 * Gerechnet wird hier nichts: die 70-%-Regel steht als Satz da, die Zahlen
 * dazu bildet der Kern, sobald der Nachweis läuft.
 */
/** Die gewählte Rissanforderung aus dem Katalog -- oder nichts, wenn er fehlt. */
function anforderung(querschnitt) {
  return (zustand.katalog?.rissanforderungen || [])
    .find((r) => r.wert === (querschnitt.rissanforderung || 'normal'));
}

/** «normaler», «erhöhter» … -- klein geschrieben, für den Satz im Hinweis. */
function anforderungstext(querschnitt) {
  const a = anforderung(querschnitt);
  return a ? `${a.beschriftung.toLowerCase()}er` : 'dieser';
}

function mindestbewehrungsBlock(querschnitt) {
  const aus70 = querschnitt.haeufige_aus_tragsicherheit !== false;
  const faelle = querschnitt.haeufige || [];
  // Ob dieser Nachweis überhaupt gefordert ist, weiss der Kern.
  const gefordert = anforderung(querschnitt)?.spannungsnachweis !== false;

  const aendern = (veraenderer) => projektAendern((p) => {
    veraenderer(p.querschnitte.find((x) => x.kennung === querschnitt.kennung));
  });

  // Der Zeilentitel sagt schon, was der Schalter tut. Die Spalte rechts
  // wiederholte das in einem ganzen Satz und machte die Tafel breit.
  // Mit Richtungsmarke wie die Lagenzeilen: dieselbe Angabe soll überall
  // gleich aussehen, sonst liest man sie zweimal verschieden.
  const zwaengung = (feld, beschriftung, richtung = null) => el(
    `div.duktilitaetszeile${richtung ? '' : '.ist-breit'}`, {}, [
      hakenSchalter(!!querschnitt[feld],
        (wert) => aendern((q) => { q[feld] = wert; }), 'Zwängung'),
      richtung
        ? el('span.richtung', {
          text: richtung, class: `lage-${richtung}`,
          title: `Zwängung in ${richtung}-Richtung`,
        })
        : null,
      el('span.postenname', { text: beschriftung }),
      el('span.kurvenhinweis', { text: '' }),
    ]);

  return el('div.unterkapitel', {}, [
    el('div.unterkapitel-kopf', {}, [
      el('span', { text: 'Nachweise der Rissbreitenbegrenzung' }),
    ]),

    el('div.unterkapitel-kopf', { style: { marginTop: '8px' } }, [
      el('span', { text: 'Rissbreiten Begrenzung bei Zwang' }),
      erklaerung(
        'Wird eine Verformung aufgezwungen – Schwinden, Temperatur, eine '
        + 'Stütze, die nicht nachgibt –, reisst der Beton, und die Bewehrung '
        + 'muss die freiwerdende Kraft aufnehmen, ohne dass der Riss zu '
        + 'breit wird. Die zulässige Stahlspannung folgt aus der '
        + 'Rissbreite nach Tabelle 17.',
        'σ_s,adm ≥ N_Riss / A_s   mit   N_Riss = h_eff/2 · b · f_ct,eff'),
    ]),
    zwaengung('zwaengung_x', 'Zwängung auf Normalkraft', 'x'),
    zwaengung('zwaengung_y', 'Zwängung auf Normalkraft', 'y'),
    zwaengung('zwaengung_begrenzt', 'Begrenzung auf 500 mm'),

    // Ohne eigene Überschrift: die vier Zeilen schreiben ihren Nachweis selbst
    // aus und stehen unter derselben Aufschrift wie die Normalkraft-Zwängung.
    ...lagenkapitel(querschnitt, {
      feld: 'zwaengung_biegung_lagen',
      vorgabe: [false, false, false, false],
      beschriftung: (n) => `Zwängung auf Biegung ${n}. Lage`,
      was: 'Nachweis',
    }).childNodes,

    el('div.unterkapitel-kopf', { style: { marginTop: '8px' } }, [
      el('span', { text: 'Verhindern des Fliessens für häufige Lastfälle' }),
      erklaerung(
        'Unter häufiger Einwirkung darf die Bewehrung nicht fliessen – sonst '
        + 'bleiben Risse und Durchbiegung dauerhaft. Gerechnet am gerissenen '
        + 'Querschnitt, gezählt nur die gezogene Bewehrung.',
        'σ_s ≤ f_yd − 80 N/mm²'),
    ]),

    // Bei normaler Anforderung steht in Tabelle 17 ein Strich: der Nachweis
    // entfällt, und damit auch alles, was unten eingetragen wird. Ohne diesen
    // Satz nimmt die Maske Lastfälle entgegen und rechnet sie stillschweigend
    // nicht -- man sucht das Ergebnis in der Zusammenfassung und findet nichts.
    // Was gefordert ist, sagt der Kern über den Katalog; hier steht keine
    // zweite Fassung der Norm.
    gefordert ? null : el('p.hinweis.hinweis-annahme', {
      text: `Bei ${anforderungstext(querschnitt)} Rissanforderung verlangt `
        + 'SIA 262 Tabelle 17 diesen Nachweis nicht. Er wird nicht geführt – '
        + 'weder die 70 % noch eigene Lastfälle. Stelle die Rissanforderung '
        + 'oben auf «Erhöht» oder «Hoch», wenn du ihn brauchst.',
    }),

    el('div.duktilitaetszeile.ist-breit', {}, [
      hakenSchalter(aus70, (wert) => aendern((q) => {
        q.haeufige_aus_tragsicherheit = wert;
      }), 'Ableitung'),
      el('span.postenname', { text: '70 % der Tragsicherheitseinwirkungen' }),
      el('span.kurvenhinweis', { text: '' }),
    ]),

    // Die abgeleiteten Fälle und eigene schliessen sich nicht aus: wer die
    // 70 % nimmt, kann trotzdem einen Fall von Hand dazustellen, den keine
    // Tragsicherheitskombination abbildet.
    ...[
      faelle.length
        ? el('div.einwirkung.ist-kopf.ist-haeufig', {}, [
          el('span'),
          el('span', { text: 'Bezeichnung' }),
          el('span', { text: 'M_Ed [kNm]' }),
          el('span', { text: 'N_Ed [kN]' }),
          el('span', { text: 'Ri.' }),
          el('span'),
        ])
        : null,
      ...(faelle.length
        ? faelle.map((_, i) => haeufigZeile(querschnitt, i))
        : [el('div.leer', {
          text: aus70
            ? 'Nur die abgeleiteten Fälle.'
            : 'Noch kein häufiger Lastfall.',
        })]),
      anfuegenKnopf('Lastfall', () => aendern((q) => {
        q.haeufige = q.haeufige || [];
        q.haeufige.push({
          name: `Häufig ${q.haeufige.length + 1}`,
          M_Ed: 0, N_Ed: 0, richtung: 'beide', aktiv: true,
        });
      })),
    ],
  ]);
}


/** Ein häufiger Lastfall auf einer Zeile -- wie eine Einwirkung, ohne Querkraft. */
function haeufigZeile(querschnitt, index) {
  const k = (querschnitt.haeufige || [])[index];
  const aendern = (veraenderer) => projektAendern((p) => {
    veraenderer(p.querschnitte.find((x) => x.kennung === querschnitt.kennung)
      .haeufige[index]);
  });

  const aktiv = k.aktiv !== false;
  return el('div.einwirkung.ist-haeufig', { class: aktiv ? '' : 'ist-aus' }, [
    hakenSchalter(aktiv, (wert) => aendern((x) => { x.aktiv = wert; }), 'Lastfall'),
    el('input.ew-name', {
      type: 'text', value: k.name, title: 'Bezeichnung des häufigen Lastfalls',
      on: { change: (e) => aendern((x) => { x.name = e.target.value; }) },
    }),
    zahlfeld({
      wert: k.M_Ed, schritt: 10, titel: 'Moment unter häufiger Einwirkung, in kNm',
      beiAenderung: (v) => aendern((x) => { x.M_Ed = v ?? 0; }),
    }),
    zahlfeld({
      wert: k.N_Ed, schritt: 10,
      titel: 'Normalkraft unter häufiger Einwirkung, in kN – Zug positiv',
      beiAenderung: (v) => aendern((x) => { x.N_Ed = v ?? 0; }),
    }),
    richtungsWahl(k.richtung || 'beide',
      (wert) => aendern((x) => { x.richtung = wert; })),
    el('button.weg', {
      text: '×', title: 'Häufigen Lastfall entfernen',
      on: {
        click: () => projektAendern((p) => {
          p.querschnitte.find((x) => x.kennung === querschnitt.kennung)
            .haeufige.splice(index, 1);
        }),
      },
    }),
  ]);
}



/**
 * Die Bewehrung suchen lassen, statt sie zu setzen.
 *
 * Ein einzelner Knopf, kein Automatismus im Hintergrund: was hier
 * herauskommt, wird in die Lagen darunter geschrieben und steht dann da wie
 * eine Eingabe von Hand -- man sieht es, kann es ändern und kann es lassen.
 * Eine Bewehrung, die sich bei jeder Zahl neu setzt, wäre keine Eingabe mehr.
 *
 * Gesucht wird gegen die Nachweise, die eingeschaltet sind. Die Schalter
 * weiter unten steuern damit unmittelbar, wonach gesucht wird.
 */
export function automatikBlock(querschnitt) {
  const aendern = (veraenderer) => projektAendern((p) => {
    veraenderer(p.querschnitte.find((x) => x.kennung === querschnitt.kennung));
  });
  const moden = [
    { wert: 'grund_ohne', beschriftung: 'Grundbewehrung ohne Kräfte' },
    { wert: 'grund_mit', beschriftung: 'Grundbewehrung mit Kräften' },
    { wert: 'grund_ohne_zulage_mit',
      beschriftung: 'Grund ohne Kräfte, Zulage mit Kräften' },
  ];
  const quer = querschnitt.automatik_querkraft === true;

  // Die Teilungen als Text: «100, 150» liest und tippt sich schneller als
  // eine Liste aus Zahlenfeldern mit Plus- und Minusknöpfen.
  const teilungsfeld = (feld, titel) => el('input.ew-name', {
    type: 'text', value: (querschnitt[feld] || []).join(', '), title: titel,
    on: {
      change: (e) => aendern((q) => {
        q[feld] = e.target.value.split(/[^0-9.]+/)
          .map(Number).filter((x) => x > 0);
      }),
    },
  });

  return el('div.feldgruppe', {}, [
    el('h3', {}, [el('span', { text: 'Bewehrung ermitteln' }),
      el('span', { text: 'kleinste Stahlfläche' })]),
    el('div.unterkapitel', {}, [
      feld('Modus', auswahl({
        werte: moden, gewaehlt: querschnitt.automatik_modus || 'grund_ohne',
        titel: 'Ohne Kräfte bleiben Duktilität, sprödes Versagen und die '
          + 'Rissbreitenbegrenzung – das, was eine Platte unabhängig von der '
          + 'Belastung braucht.',
        beiAenderung: (v) => aendern((q) => { q.automatik_modus = v; }),
      })),
      feld('Teilungen', teilungsfeld('automatik_teilungen',
        'Liste in mm, durch Komma getrennt. Grundbewehrung und Zulage einer '
        + 'Lage bekommen dieselbe Teilung.'), 'mm'),
      feld('Mindestdurchmesser', zahlfeld({
        wert: querschnitt.automatik_mindestdurchmesser ?? 10, schritt: 2, min: 0,
        titel: 'Dünner baut die Suche nicht ein. Eine Lage ganz wegzulassen '
          + 'bleibt erlaubt – gemeint ist, dass ein vorhandener Stab nicht '
          + 'dünner wird als das, was man verlegen will.',
        beiAenderung: (v) => aendern((q) => {
          q.automatik_mindestdurchmesser = v ?? 10;
        }),
      }), 'mm'),
      el('div.duktilitaetszeile.ist-breit', {}, [
        hakenSchalter(quer, (wert) => aendern((q) => {
          q.automatik_querkraft = wert;
        }), 'Bügelsuche'),
        el('span.postenname', { text: 'Querkraftbewehrung mitsuchen' }),
        el('span.kurvenhinweis', { text: '' }),
      ]),
      ...(quer ? [feld('Bügelteilungen',
        teilungsfeld('automatik_querkraft_teilungen',
          'Liste in mm. Das Bügelraster ist quadratisch: s_x = s_y.'), 'mm')] : []),
      automatikLeiste(querschnitt.kennung),
    ]),
  ]);
}

function automatikLeiste(kennung) {
  const laeuft = laufendeSuche.has(kennung);
  return el('div.automatik-leiste', {}, [
    el('button.knopf.knopf-haupt', {
      text: laeuft ? 'sucht …' : 'Bewehrung ermitteln',
      title: 'Sucht einmalig und schreibt das Ergebnis in die Lagen',
      disabled: laeuft,
      on: { click: () => bewehrungErmitteln(kennung) },
    }),
  ]);
}

/** Einmal suchen und das Ergebnis in die Lagen schreiben. */
async function bewehrungErmitteln(kennung) {
  laufendeSuche.add(kennung);
  aendern({}, 'bewehrungssuche-start');
  try {
    const antwort = await api.bewehrungSuchen(zustand.projekt, kennung);
    if (antwort.gefunden) {
      // Der Kern gibt das fertige Projekt zurück -- übernommen wird es als
      // eine Änderung, damit ein Rückgängig sie als eine zurücknimmt.
      projektAendern((p) => {
        const alt = p.querschnitte.findIndex((x) => x.kennung === kennung);
        const neu = antwort.projekt?.querschnitte?.find((x) => x.kennung === kennung);
        if (alt >= 0 && neu) p.querschnitte[alt] = neu;
      });
    } else {
      // Nichts gefunden heisst: die Lagen bleiben, wie sie waren. Das sieht
      // man nicht von selbst, also sagt es die Meldungszeile oben -- dort,
      // wo auch sonst steht, was schiefging.
      melden(antwort.begruendung, true);
    }
  } catch (fehler) {
    melden(String(fehler.message || fehler), true);
  } finally {
    // Zuletzt und immer. Hing das Neuzeichnen am Zweig, blieb der Knopf auf
    // «sucht …» stehen, und man musste ein zweites Mal drücken.
    laufendeSuche.delete(kennung);
    aendern({}, 'bewehrungssuche-ende');
  }
}

/**
 * Spannung-Dehnung-Analyse: drei Fragen an denselben Querschnitt.
 *
 * Kein Nachweis -- es wird nichts gegen etwas gehalten. Darum auch keine
 * Erfüllungsgrade in der Zusammenfassung; die Bilder stehen im eigenen
 * Reiter. Was jede Zeile braucht, hängt an ihrer Art, und die Felder
 * wechseln entsprechend: eine Zeile, die nach N und M fragt, soll nicht
 * daneben zwei Dehnungsfelder zeigen, die sie nicht liest.
 */
function spannungsBlock(querschnitt) {
  const faelle = querschnitt.spannungsfaelle || [];
  const aendern = (veraenderer) => projektAendern((p) => {
    veraenderer(p.querschnitte.find((x) => x.kennung === querschnitt.kennung));
  });

  return el('div.unterkapitel', {}, [
    el('div.unterkapitel-kopf', {}, [
      el('span', { text: 'Spannung-Dehnung-Analyse' }),
    ]),
    ...(faelle.length
      ? faelle.map((_, i) => spannungsZeile(querschnitt, i))
      : [el('div.leer', { text: 'Keine Analyse angelegt.' })]),
    anfuegenKnopf('Analyse', () => aendern((q) => {
      q.spannungsfaelle = q.spannungsfaelle || [];
      q.spannungsfaelle.push({
        name: `Bild ${q.spannungsfaelle.length + 1}`,
        art: 'schnittgroessen', richtung: 'x',
        N_Ed: 0, M_Ed: 30, eps_oben: -1, eps_unten: 2, aktiv: true,
      });
    })),
  ]);
}

/** Eine Analysezeile. Die Zahlenfelder richten sich nach der gewählten Art. */
function spannungsZeile(querschnitt, index) {
  const k = (querschnitt.spannungsfaelle || [])[index];
  const aendern = (veraenderer) => projektAendern((p) => {
    veraenderer(p.querschnitte.find((x) => x.kennung === querschnitt.kennung)
      .spannungsfaelle[index]);
  });
  const zahl = (feld, titel, schritt) => zahlfeld({
    wert: k[feld], schritt, titel,
    beiAenderung: (v) => aendern((x) => { x[feld] = v ?? 0; }),
  });
  const aktiv = k.aktiv !== false;

  // Je Art andere Felder -- und immer zwei, damit die Zeilen untereinander
  // dieselbe Gestalt behalten.
  // Je Art andere Felder -- und andere Beschriftungen darüber. Ohne sie
  // stünden dort zwei namenlose Zahlen, und ob die erste eine Kraft oder
  // eine Dehnung ist, sähe man erst am Ergebnis.
  const bauplan = {
    schnittgroessen: {
      kopf: ['N_Ed [kN]', 'M_Ed [kNm]'],
      felder: () => [
        zahl('N_Ed', 'Normalkraft in kN – Zug positiv', 50),
        zahl('M_Ed', 'Moment in kNm', 10),
      ],
    },
    dehnungen: {
      kopf: ['ε oben [‰]', 'ε unten [‰]'],
      felder: () => [
        zahl('eps_oben', 'Randdehnung oben in ‰ – Zug positiv', 0.5),
        zahl('eps_unten', 'Randdehnung unten in ‰ – Zug positiv', 0.5),
      ],
    },
    moment_kruemmung: {
      kopf: ['N_Ed [kN]', ''],
      felder: () => [
        zahl('N_Ed', 'Normalkraft in kN – Zug positiv', 50),
        el('span.kurvenhinweis', { text: '0 … M_Rd' }),
      ],
    },
  }[k.art] || { kopf: ['', ''], felder: () => [el('span'), el('span')] };

  return el('div.einwirkung.ist-spannung', { class: aktiv ? '' : 'ist-aus' }, [
    hakenSchalter(aktiv, (wert) => aendern((x) => { x.aktiv = wert; }), 'Analyse'),
    el('input.ew-name', {
      type: 'text', value: k.name, title: 'Bezeichnung der Analyse',
      on: { change: (e) => aendern((x) => { x.name = e.target.value; }) },
    }),
    auswahl({
      werte: [
        { wert: 'schnittgroessen', beschriftung: 'N, M' },
        { wert: 'dehnungen', beschriftung: 'ε oben/unten' },
        { wert: 'moment_kruemmung', beschriftung: 'M–χ' },
      ],
      gewaehlt: k.art || 'schnittgroessen',
      titel: 'Was eingegeben wird – und damit, was herauskommt',
      beiAenderung: (v) => aendern((x) => { x.art = v; }),
    }),
    // Beschriftung über dem Feld, nicht daneben: so bleibt das Raster der
    // Zeile dasselbe, gleich welche Art gewählt ist.
    ...bauplan.felder().map((eingabe, i) => el('div.mit-kopf', {}, [
      el('span.spaltenkopf', { text: bauplan.kopf[i] || '' }),
      eingabe,
    ])),
    richtungsWahl(k.richtung || 'x', (wert) => aendern((x) => { x.richtung = wert; }),
      ['x', 'y']),
    el('button.weg', {
      text: '×', title: 'Analyse entfernen',
      on: {
        click: () => projektAendern((p) => {
          p.querschnitte.find((x) => x.kennung === querschnitt.kennung)
            .spannungsfaelle.splice(index, 1);
        }),
      },
    }),
  ]);
}
