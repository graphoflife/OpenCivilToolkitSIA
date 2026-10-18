/**
 * nachweise.js -- die Nachweise, die Platte und gezeichneter Querschnitt
 * gleich führen, Kapitel für Kapitel.
 *
 * Knicken, Duktilität, sprödes Versagen, Rissbreite bei Zwang, die beiden
 * Stahlspannungen und die sechs Spannung-Dehnung-Analysen: jedes Kapitel
 * öffnet sich in einem eigenen Fenster (`kapitel.js`). Hier steht, welche
 * Kapitel beide Bauteile haben (`nachweisKapitel`, `analysenKapitel`), und
 * was in den Fenstern steht -- `…Inhalt(e, ort)` liefert die Knoten. Was bei
 * einem Bauteil anders ist, sagt sein Ort: `PLATTE` in `plattenkapitel.js`,
 * `ORT` in `querschnittsanalyse.js`. Bis 2026-10-17 führte jedes Bauteil
 * seine eigene Liste, mit eigenen Fragezeichen, die schon Verschiedenes
 * sagten.
 *
 * Was nur die Platte hat -- die Tragsicherheit mit der Querkraft, die
 * Verformung --, steht in `plattenkapitel.js`, die Suche ihrer Bewehrung in
 * `bewehrungssuche.js`; was nur der gezeichnete Querschnitt hat, in
 * `querschnittsanalyse.js`.
 *
 * Gerechnet wird hier nichts. Jede Zeile beschreibt eine Eingabe; die Zahlen
 * dazu bildet der Kern, sobald der Nachweis läuft.
 */

import { erklaerung, feld, hakenSchalter } from './bausteine.js';
import { auswahl, el, zahlfeld } from './dom.js';
import { gebrauchsstand, schalter, zeilenstand } from './kapitel.js';
import { ausVorlage, feldangabe, naechsterName, projektAendern, zustand } from './zustand.js';

// ===========================================================================
// Die Kapitel -- je ein Knopf, die Eingaben im Fenster (kapitel.js)
// ===========================================================================

/**
 * Die Nachweise, die Platte und gezeichneter Querschnitt gleich führen, als
 * Kapitel: Knicken, Duktilität, sprödes Versagen, Riss bei Zwang und die
 * beiden Stahlspannungen. Davor steht bei jedem Bauteil seine Tragsicherheit
 * -- die Platte fragt dort nach Bügeln, der gezeichnete Querschnitt nach
 * Schubwänden --, bei der Platte danach die Verformung.
 *
 * `ort` sagt, was beim Bauteil anders ist (`PLATTE` in plattenkapitel.js,
 * `ORT` in querschnittsanalyse.js). Knicken und
 * Stahlspannung rechnen beide Bauteile gleich: das Gemeinsame ihrer Hilfe
 * steht hier, und der Ort fügt seine Zeilen an. Duktilität, sprödes
 * Versagen und Zwang rechnet jedes Bauteil auf seine Weise -- ihre Hilfe
 * kommt ganz vom Ort.
 */
export function nachweisKapitel(ort) {
  // Die beiden Stahlspannungen sind dieselbe Rechnung mit anderer Grenze.
  const stahlspannung = [
    ['Werte', 'nach Rechenwahl; Vorgabe charakteristisch (f_ck, f_yk), elastisch'],
    ['φ', 'nach Rechenwahl → E_c,eff = E_cm / (1 + φ), präzise und elastisch'],
  ];
  return [
    {
      schluessel: 'knicken',
      name: 'Knicken', titel: 'Knicken', bezug: ort.bezug,
      hilfe: {
        zeilen: [
          ['Weg', 'verformtes System: e_0d + e_1d + e_2d, iteriert über die Krümmung'],
          ['N_Rd', 'grösste Druckkraft mit Gleichgewichtslage'],
          ['Verformung', 'e_2d immer präzise; φ und Werte nach Wahl, Vorgabe Bemessung (f_cd, f_yd)'],
          ['Widerstand', 'Rechenwahl für N_Rd(M_Ed = N_Ed·e_tot), ohne Handrechnung; '
            + 'Vorgabe 0.85·x, Bemessung'],
          ['φ', 'je Wahl, nur präzise → E_c,eff = E_cm / (1 + φ)'],
          ...ort.hilfe.knicken.zeilen,
        ],
        formel: 'α_eff = N_Rd / |N_Ed|',
      },
      inhalt: (e) => knickInhalt(e, ort),
      stand: (e) => zeilenstand(e.knickfaelle, 'Fall', 'Fälle', 'kein Fall'),
    },
    {
      schluessel: 'duktilitaet',
      name: 'Duktilität', titel: 'Duktilitätsnachweis', hilfe: ort.hilfe.duktilitaet,
      inhalt: (e) => duktilitaetInhalt(e, ort),
      stand: (e) => schalter(!!e.duktilitaet),
    },
    {
      schluessel: 'sproede',
      name: 'Sprödes Versagen', titel: 'Nachweis gegen sprödes Versagen',
      hilfe: ort.hilfe.sproede,
      inhalt: (e) => sproedeInhalt(e, ort),
      stand: (e) => schalter(!!e.sproede),
    },
    {
      schluessel: 'zwang',
      name: 'Riss bei Zwang', titel: 'Rissbreitenbegrenzung bei Zwang', hilfe: ort.hilfe.zwang,
      inhalt: (e) => zwangInhalt(e, ort),
      // Die Begrenzung auf 500 mm ist kein eigener Nachweis, sie ändert den
      // auf Normalkraft.
      stand: (e) => {
        const teile = [e.zwaengung ? 'N' : null, e.zwaengung_biegung ? 'M' : null].filter(Boolean);
        return { an: teile.length > 0, text: teile.length ? `auf ${teile.join(' und ')}` : 'aus' };
      },
    },
    {
      schluessel: 'quasistaendig',
      name: 'Stahlspannung quasi-ständig',
      titel: 'Stahlspannungsbegrenzung bei quasi-ständigen Lastfällen', bezug: ort.bezug,
      hilfe: {
        zeilen: [...ort.hilfe.quasistaendig.zeilen, ...stahlspannung],
        formel: 'σ_s ≤ σ_s,adm (Tab. 17)',
      },
      inhalt: (e) => quasistaendigInhalt(e, ort),
      stand: (e) => gebrauchsstand(e.quasistaendig),
    },
    {
      schluessel: 'haeufig',
      name: 'Fliessen häufig', titel: 'Verhindern des Fliessens für häufige Lastfälle',
      bezug: ort.bezug,
      hilfe: {
        zeilen: [
          ...ort.hilfe.haeufig.zeilen, ['Grenze', 'je Stahl aus seinem f_yd'], ...stahlspannung,
        ],
        formel: 'σ_s ≤ f_yd − 80 N/mm²',
      },
      inhalt: (e) => haeufigInhalt(e, ort),
      stand: (e) => (fliessenGefordert(e) ? gebrauchsstand(e.haeufig)
        : { an: false, text: 'entfällt' }),
    },
  ];
}

/**
 * Die sechs Spannung-Dehnung-Analysen als Kapitel, je Art aus dem Katalog:
 * der Name auf dem Knopf kurz, über dem Fenster lang.
 */
export function analysenKapitel(ort) {
  return (zustand.katalog?.spannungsanalyse?.arten || []).map((a) => ({
    schluessel: a.wert,
    name: a.beschriftung, titel: a.titel,
    bezug: (e) => `Spannung-Dehnung-Analyse · ${ort.bezug(e)}`,
    inhalt: (e) => analyseInhalt(e, a.wert, ort),
    stand: (e) => zeilenstand((e.spannungsfaelle || []).filter((k) => k.art === a.wert),
      'Bild', 'Bilder', 'kein Bild'),
  }));
}

// ===========================================================================
// Was in den Fenstern steht
// ===========================================================================

/**
 * Der Knopf, der eine Liste verlängert.
 *
 * Steht unter der Liste und nicht in der Überschrift: dort ist die Stelle,
 * an der die nächste Zeile erscheint, und ein Knopf gehört dorthin, wo seine
 * Wirkung sichtbar wird. Über die ganze Breite und mit gestricheltem Rand --
 * man sieht, dass dort noch etwas hinkommt.
 */
export function anfuegenKnopf(text, tun) {
  return el('button.knopf-anfuegen', { text: `+ ${text}`, on: { click: tun } });
}

/**
 * Ändert das Bauteil im Projekt -- für die Fenster, die an ihm schreiben.
 * `ort.liste` sagt, in welcher Liste des Projekts es steht.
 */
export function anBauteil(eintrag, ort) {
  return (veraenderer) => projektAendern((p) => {
    veraenderer(p[ort.liste].find((x) => x.kennung === eintrag.kennung));
  });
}

/**
 * Die Zeile eines Nachweises mit *einem* Schalter: Duktilität, sprödes
 * Versagen und die Zeilen der Zwängung. Vorne der Schalter, dann die Marke,
 * die der Ort davor setzt (`ort.marke`: bei der Platte die Tragrichtung x),
 * der Name, dahinter wahlweise ein Feld -- die Grenze x/d, das φ der
 * Zwängung auf Biegung -- und zuletzt, was der Ort zum Nachweis sagt
 * (`ort.hinweis`). `name` sagt, woran gemessen wird, `was` im Titel des
 * Schalters, was er führt.
 *
 * Bei der Platte werden die beiden x-Lagen gerechnet, in der
 * Zusammenfassung steht die ungünstigere. Vorher stand hier ein Schalter je
 * Lage -- vier Haken für eine Frage, und drei davon betrafen Lagen, die
 * niemand nachweist. Die y-Lagen stehen im Querschnitt, weil sie die
 * statische Höhe von x bestimmen; ein Nachweis fragt nicht nach ihnen.
 *
 * `nachweis: false` für einen Schalter, der keinen eigenen Nachweis führt,
 * sondern einen anderen ändert -- die Begrenzung auf 500 mm: ohne Marke und
 * ohne Hinweis.
 */
function schalterZeile(eintrag, ort, {
  feld, name, was = 'Nachweis', zusatz = null, nachweis = true,
}) {
  const vorne = nachweis ? ort.marke() : null;
  const art = vorne ? (zusatz ? '.mit-feld' : '') : (zusatz ? '.mit-grenze' : '.ist-breit');
  return el(`div.duktilitaetszeile${art}`, {}, [
    hakenSchalter(!!eintrag[feld],
      (wert) => anBauteil(eintrag, ort)((e) => { e[feld] = wert; }), was),
    vorne,
    el('span.postenname', { text: name }),
    zusatz,
    el('span.kurvenhinweis', { text: nachweis ? ort.hinweis(eintrag, feld) : '' }),
  ]);
}

/**
 * Unter Duktilität und sprödem Versagen, wo der Ort sagt, womit sie rechnen
 * (`ort.rechenwerte`) -- beim gezeichneten Querschnitt mit den Werten der
 * Tragsicherheit. Bei der Platte steht es im Fragezeichen.
 */
function rechenwerteSatz(ort) {
  return ort.rechenwerte ? el('p.qa-erlaeuterung', { text: ort.rechenwerte }) : null;
}

/** Duktilität: ein Schalter und die Grenze x/d. */
function duktilitaetInhalt(eintrag, ort) {
  return [
    schalterZeile(eintrag, ort, {
      feld: 'duktilitaet', name: 'Max. x/d',
      // Vorgabe und Höchstwert der Grenze kennt der Kern. Leer gelassen
      // bleibt der bisherige Wert -- eine Grenze von null gäbe es nicht.
      zusatz: zahlfeld({
        wert: eintrag.x_d_max, schritt: 0.05, min: 0.05,
        max: zustand.katalog?.duktilitaet?.hoechstens,
        titel: `Grenze der Druckzonenhöhe x/d; höchstens ${
          zustand.katalog?.duktilitaet?.hoechstens ?? '–'}`,
        beiAenderung: (v) => anBauteil(eintrag, ort)((e) => { e.x_d_max = v; }),
      }),
    }),
    rechenwerteSatz(ort),
  ];
}

/** Sprödes Versagen: ein Schalter. */
function sproedeInhalt(eintrag, ort) {
  return [
    schalterZeile(eintrag, ort, { feld: 'sproede', name: 'Rissmoment' }),
    rechenwerteSatz(ort),
  ];
}

/**
 * Knicken -- Druckkraft, Moment 1. Ordnung, Länge und Knicklänge je Fall.
 *
 * Bei der Platte nur in x-Richtung: eine Knicklänge gehört zu einer
 * Tragrichtung, und in y wäre die Breite der Platte die Länge. Der
 * gezeichnete Querschnitt wählt je Fall die Zugseite, zu der sich der Stab
 * biegt -- `ort.knick.richtung` baut die Auswahl; sie steht oben neben dem
 * Namen, die vier Zahlen bleiben darunter. `ort.knick` sagt auch die Köpfe
 * und Titel der Spalten.
 */
function knickInhalt(eintrag, ort) {
  const faelle = eintrag.knickfaelle || [];
  const aendern = anBauteil(eintrag, ort);
  const knick = ort.knick;

  return [
    // Zwei Wahlen: womit die Verformung gerechnet wird und womit der
    // Querschnitt widersteht. Ohne Handrechnung: beim Knicken zählt die
    // Normalkraft genau. Die Verformung nur präzise -- mit dem
    // Spannungsblock wäre die Ausmitte nahe der Grenzkraft nicht eindeutig.
    rechenwahlZeile('Verformung (e_2d)', eintrag.knicken_wahl_verformung,
      (veraenderer) => aendern((q) => veraenderer(q.knicken_wahl_verformung)),
      { arten: 'verformungsarten' }),
    rechenwahlZeile('Widerstand (N_Rd)', eintrag.knicken_wahl_widerstand,
      (veraenderer) => aendern((q) => veraenderer(q.knicken_wahl_widerstand)),
      { arten: 'faserarten' }),
    faelle.length
      ? el('div.einwirkung.ist-knick.ist-kopf', {}, [
        el('span'),
        el('span', { text: 'Bezeichnung' }),
        ...knick.kopf.map((text) => el('span', { text })),
        el('span'),
      ])
      : null,
    ...(faelle.length
      ? faelle.map((_, i) => knickZeile(eintrag, ort, i))
      : [el('div.leer', { text: knick.leer })]),
    anfuegenKnopf('Knicknachweis', () => aendern((q) => {
      q.knickfaelle = q.knickfaelle || [];
      q.knickfaelle.push(
        ausVorlage(knick.vorlage, { name: naechsterName('Knicken', q.knickfaelle) }));
    })),
  ];
}

function knickZeile(eintrag, ort, index) {
  const k = (eintrag.knickfaelle || [])[index];
  const aendern = (veraenderer) => anBauteil(eintrag, ort)((e) => veraenderer(e.knickfaelle[index]));
  const titel = ort.knick.titel;
  // Eine Länge null gibt es nicht -- geleert bleibt der bisherige Wert.
  const zahl = (feld, schritt) => zahlfeld({
    wert: k[feld], schritt, titel: titel[feld],
    beiAenderung: (v) => aendern((x) => { x[feld] = v; }),
  });

  const aktiv = k.aktiv !== false;
  const richtung = ort.knick.richtung;
  return el(`div.einwirkung.ist-knick${richtung ? '.mit-zugseite' : ''}`, {
    class: aktiv ? '' : 'ist-aus',
  }, [
    hakenSchalter(aktiv, (wert) => aendern((x) => { x.aktiv = wert; }), 'Knicknachweis'),
    el('input.ew-name', {
      type: 'text', value: k.name, title: 'Bezeichnung des Knicknachweises',
      on: { change: (e) => aendern((x) => { x.name = e.target.value; }) },
    }),
    zahl('N_Ed', 50),
    zahl('M_Ed_1', 10),
    zahl('laenge', 0.5),
    zahl('knicklaenge', 0.5),
    richtung ? richtung(k, (wert) => aendern((x) => { x.richtung = wert; })) : null,
    el('button.weg', {
      text: '×', title: 'Knicknachweis entfernen',
      on: {
        click: () => anBauteil(eintrag, ort)((e) => { e.knickfaelle.splice(index, 1); }),
      },
    }),
  ]);
}

/**
 * Die Rissanforderung als erste Zeile der drei Rissnachweise -- Zwang,
 * quasi-ständig, häufig. Sie gehört dem Bauteil, nicht dem Nachweis: in
 * einem der drei Fenster gewählt, gilt sie in allen. Vorher stand sie oben
 * bei der Platte, weit weg von den Nachweisen, die sie brauchen (Benutzer,
 * 2026-10-16).
 */
function rissanforderungZeile(eintrag, ort) {
  return feld('Rissanforderung', auswahl({
    werte: (zustand.katalog?.rissanforderungen || []).map((r) => ({
      wert: r.wert, beschriftung: r.beschriftung,
    })),
    gewaehlt: eintrag.rissanforderung || 'normal',
    titel: 'Bestimmt σ_s,adm (Tab. 17)',
    beiAenderung: (v) => anBauteil(eintrag, ort)((e) => { e.rissanforderung = v; }),
  }), erklaerung([
    ['Gilt für', 'alle Rissnachweise: Riss bei Zwang, Stahlspannung quasi-ständig '
      + 'und Fliessen häufig. Hier geändert, ändert sie sich in allen dreien.'],
    ['Bestimmt', 'σ_s,adm nach Tab. 17 und ob «Fliessen häufig» gefordert ist'],
  ]));
}

/** Die gewählte Rissanforderung aus dem Katalog -- oder nichts, wenn er fehlt. */
function anforderung(querschnitt) {
  return (zustand.katalog?.rissanforderungen || [])
    .find((r) => r.wert === (querschnitt.rissanforderung || 'normal'));
}

/** Ob der Nachweis gegen Fliessen gefordert ist -- das weiss der Kern über den Katalog. */
function fliessenGefordert(querschnitt) {
  return anforderung(querschnitt)?.fliessnachweis !== false;
}

/**
 * Rissbreite bei Zwang: Normalkraft, Biegung mit ihrem eigenen φ, und die
 * Begrenzung der rissaktiven Dicke. Eine Annahme über das Tragwerk, nicht
 * über das Bauteil -- darum ausgeschaltet, bis jemand sie trifft.
 *
 * Der Zeilentitel sagt schon, was der Schalter tut. Die Spalte rechts
 * wiederholte das in einem ganzen Satz und machte die Tafel breit.
 */
function zwangInhalt(eintrag, ort) {
  return [
    rissanforderungZeile(eintrag, ort),
    schalterZeile(eintrag, ort, {
      feld: 'zwaengung', name: 'Zwängung auf Normalkraft', was: 'Zwängung',
    }),
    // Die Zwängung auf Biegung rechnet am gerissenen Querschnitt -- mit
    // ihrem eigenen φ, nicht dem des Bauteils.
    schalterZeile(eintrag, ort, {
      feld: 'zwaengung_biegung', name: 'Zwängung auf Biegung', was: 'Zwängung',
      zusatz: el('span.zeilenfeld', {}, [
        el('span.zeichen', { text: 'φ' }),
        zahlfeld({
          wert: eintrag.zwaengung_biegung_kriechzahl ?? 0, schritt: 0.1, min: 0, leer: 0,
          titel: 'Kriechzahl φ der Zwängung auf Biegung: E_c,eff = E_cm / (1 + φ)',
          beiAenderung: (v) => anBauteil(eintrag, ort)((e) => {
            e.zwaengung_biegung_kriechzahl = v;
          }),
        }),
      ]),
    }),
    // Ändert nur die Zwängung auf Normalkraft: die Dicke, über die der
    // Querschnitt unter Zug reisst.
    schalterZeile(eintrag, ort, {
      feld: 'zwaengung_begrenzt', name: 'Begrenzung auf 500 mm', was: 'Zwängung',
      nachweis: false,
    }),
  ];
}

/** Die Stahlspannung unter quasi-ständigen Lastfällen -- begrenzt aus der Rissbreite. */
function quasistaendigInhalt(eintrag, ort) {
  return gebrauchsKapitel(eintrag, ort, {
    feld: 'quasistaendig', wort: 'quasi-ständig', neu: 'Quasi-ständig',
  });
}

/** Das Fliessen unter häufigen Lastfällen -- gefordert nur bei erhöhter und hoher Anforderung. */
function haeufigInhalt(eintrag, ort) {
  return gebrauchsKapitel(eintrag, ort, {
    feld: 'haeufig', wort: 'häufig', neu: 'Häufig',
    // Bei normaler Anforderung steht in Tabelle 17 ein Strich: der
    // Nachweis entfällt, und damit auch alles, was unten eingetragen wird.
    // Ohne diesen Satz nimmt die Maske Lastfälle entgegen und rechnet sie
    // stillschweigend nicht -- man sucht das Ergebnis in der
    // Zusammenfassung und findet nichts. Was gefordert ist, sagt der Kern
    // über den Katalog; hier steht keine zweite Fassung der Norm. Nur
    // dieses Kapitel: das quasi-ständige läuft immer.
    hinweis: fliessenGefordert(eintrag) ? null
      : `Rissanforderung «${anforderung(eintrag)?.beschriftung ?? '–'}» → `
        + 'Tab. 17: kein Nachweis. Für den Nachweis oben «Erhöht» oder «Hoch» wählen.',
  });
}

/**
 * Ein Stahlspannungsnachweis unter Gebrauchslast: Rechenwahl, der Anteil
 * der Tragsicherheitseinwirkungen und die eigenen Lastfälle.
 *
 * Zweimal gebraucht -- quasi-ständig gegen die Rissbreite, häufig gegen das
 * Fliessen. Im Kern sind beide dieselbe Rechnung mit anderer Grenze, hier
 * dieselbe Maske mit anderen Feldern. Eine Kopie davon stünde in der
 * Oberfläche genau so, wie sie im Kern vermieden wurde.
 *
 * `feld` ist die Gebrauchsliste des Bauteils -- `haeufig` oder
 * `quasistaendig`, je mit `anteil`, `aus_tragsicherheit` und `faelle`. Was
 * ein Fall trägt und welche Rechenarten gelten, sagt `ort.gebrauch`: bei der
 * Platte M und N, beim gezeichneten Querschnitt N, M_y und M_z.
 *
 * Der Anteil steht in der Schalterzeile und nicht darunter: «[✓] [60] % der
 * Tragsicherheitseinwirkungen» liest sich als ein Satz, und man sieht beim
 * Einschalten, womit gerechnet wird. Seine Vorgabe kommt aus dem Kern -- die
 * Datei läuft beim Laden durch ihn und bringt den Wert immer mit.
 */
function gebrauchsKapitel(eintrag, ort, {
  feld, wort, neu, hinweis,
}) {
  const liste = eintrag[feld];
  const abgeleitet = !!liste.aus_tragsicherheit;
  const faelle = liste.faelle;
  const aendern = (veraenderer) => anBauteil(eintrag, ort)((e) => veraenderer(e[feld]));
  const spalten = ort.gebrauch.spalten(eintrag);

  return [
    rissanforderungZeile(eintrag, ort),
    hinweis ? el('p.hinweis.hinweis-annahme', { text: hinweis }) : null,
    rechenwahlZeile('Rechenwahl', liste.wahl,
      (veraenderer) => aendern((l) => veraenderer(l.wahl)), { arten: ort.gebrauch.arten }),

    el('div.duktilitaetszeile.ist-anteil', {}, [
      hakenSchalter(abgeleitet, (wert) => aendern((l) => {
        l.aus_tragsicherheit = wert;
      }), 'Ableitung'),
      zahlfeld({
        wert: liste.anteil, schritt: 5, min: 5, max: 100,
        titel: `Anteil der Tragsicherheitseinwirkungen als ${wort}, in %`,
        // Leer gelassen bleibt der bisherige Wert -- eine Null wäre kein
        // Anteil, und der Kern wiese sie ohnehin zurück.
        beiAenderung: (v) => aendern((l) => { l.anteil = v; }),
      }),
      el('span.postenname', { text: '% der Tragsicherheitseinwirkungen' }),
      el('span.kurvenhinweis', { text: '' }),
    ]),

    // Die abgeleiteten Fälle und eigene schliessen sich nicht aus: wer den
    // Anteil nimmt, kann trotzdem einen Fall von Hand dazustellen, den keine
    // Tragsicherheitskombination abbildet.
    faelle.length
      ? el('div.einwirkung.ist-kopf', { style: { '--felder': spalten.length } }, [
        el('span'),
        el('span', { text: 'Bezeichnung' }),
        ...spalten.map((s) => el('span', { text: s.kopf })),
        el('span'),
      ])
      : null,
    ...(faelle.length
      ? faelle.map((_, i) => gebrauchsfallZeile(eintrag, ort, spalten, feld, wort, i))
      : [el('div.leer', {
        text: abgeleitet
          ? 'Nur die abgeleiteten Fälle.'
          : `Noch kein ${wort}er Lastfall.`,
      })]),
    anfuegenKnopf('Lastfall', () => aendern((l) => {
      l.faelle.push(ausVorlage(ort.gebrauch.vorlage, { name: naechsterName(neu, l.faelle) }));
    })),
  ];
}

/** Ein Lastfall unter Gebrauchslast auf einer Zeile -- wie eine Einwirkung, ohne Querkraft. */
function gebrauchsfallZeile(eintrag, ort, spalten, feld, wort, index) {
  const k = eintrag[feld].faelle[index];
  const aendern = (veraenderer) => anBauteil(eintrag, ort)((e) => veraenderer(e[feld].faelle[index]));

  const aktiv = k.aktiv !== false;
  return el('div.einwirkung', {
    class: aktiv ? '' : 'ist-aus', style: { '--felder': spalten.length },
  }, [
    hakenSchalter(aktiv, (wert) => aendern((x) => { x.aktiv = wert; }), 'Lastfall'),
    el('input.ew-name', {
      type: 'text', value: k.name, title: `Bezeichnung des ${wort}en Lastfalls`,
      on: { change: (e) => aendern((x) => { x.name = e.target.value; }) },
    }),
    ...spalten.map((s) => zahlfeld({
      wert: k[s.feld], schritt: s.schritt, titel: s.titel(wort), leer: 0,
      beiAenderung: (v) => aendern((x) => { x[s.feld] = v; }),
    })),
    el('button.weg', {
      text: '×', title: `${wort[0].toUpperCase()}${wort.slice(1)}en Lastfall entfernen`,
      on: {
        click: () => anBauteil(eintrag, ort)((e) => { e[feld].faelle.splice(index, 1); }),
      },
    }),
  ]);
}

/**
 * Eine Art der Spannung-Dehnung-Analyse: die Bilder dieser Art, und ein
 * Knopf für ein weiteres.
 *
 * Kein Nachweis -- es wird nichts gegen etwas gehalten. Darum auch keine
 * Erfüllungsgrade in der Zusammenfassung; die Bilder stehen im eigenen
 * Reiter. Jede Art hat ihr Fenster, und was eine Zeile fragt, hängt an der
 * Art: eine Zeile, die nach N und M fragt, soll nicht daneben zwei
 * Dehnungsfelder zeigen, die sie nicht liest. Die Bilder aller Arten
 * stehen in einer Liste der Platte; jede Zeile behält ihre Stelle darin.
 */
function analyseInhalt(eintrag, art, ort) {
  const stellen = (eintrag.spannungsfaelle || [])
    .map((k, i) => (k.art === art ? i : -1))
    .filter((i) => i >= 0);

  return [
    ...(stellen.length
      ? stellen.map((i) => spannungsZeile(eintrag, i, ort))
      : [el('div.leer', { text: 'Noch kein Bild.' })]),
    anfuegenKnopf('Bild', () => projektAendern((p) => {
      const e = p[ort.liste].find((x) => x.kennung === eintrag.kennung);
      e.spannungsfaelle = e.spannungsfaelle || [];
      e.spannungsfaelle.push(
        ausVorlage(ort.vorlage, { name: naechsterName('Bild', e.spannungsfaelle), art }));
    })),
  ];
}

/** Ein Feld mit seiner Beschriftung darüber -- eine Formel bleibt klein geschrieben. */
export function mitKopf(kopf, eingabe, formel = false) {
  return el('div.mit-kopf', {}, [
    el('span.spaltenkopf', { text: kopf, class: formel ? 'ist-formel' : '' }), eingabe,
  ]);
}

/**
 * Die Felder einer Rechenwahl: Kriechzahl φ, Werte und Rechenart -- in jedem
 * Kapitel und in jeder Analyse dieselben drei. `ziel` trägt die Felder
 * `kriechzahl`, `werkstoffsatz` und `rechenart`, `aendern` ändert es im
 * Projekt. `arten` sagt, welche Rechenarten gelten: `rechenarten`, bei den
 * Stahlspannungen `spannungsarten`, beim Knicken und in den Analysen
 * `faserarten` (ohne Handrechnung), bei der Verformung des Knickens
 * `verformungsarten` (nur präzise). Wirkt φ bei der gewählten Art
 * nicht, steht das Feld blass da -- es bleibt aber stehen, damit die Zahl
 * nicht verloren geht, wenn man die Art wieder wechselt. `phiImmer`: in den
 * Analysen rechnet der ungerissene Teil immer mit E_cm/(1+φ), dort wirkt φ
 * bei jeder Art.
 */
function rechenwahlFelder(ziel, aendern, { arten = 'rechenarten', phiImmer = false } = {}) {
  const katalog = zustand.katalog?.rechenwahl || {};
  const liste = katalog[arten] || [];
  const art = liste.find((a) => a.wert === ziel.rechenart);
  // In schmalen Zeilen stehen die kurzen Namen; der lange steht im Titel.
  const kurz = (l) => (l || []).map((e) => ({ wert: e.wert, beschriftung: e.kurz }));
  const phi = mitKopf('φ', zahlfeld({
    wert: ziel.kriechzahl ?? 0, schritt: 0.1, min: 0, leer: 0,
    titel: phiImmer
      ? 'Kriechzahl φ – wirkt auf den ungerissenen Teil, präzise auch auf den gerissenen'
      : 'Kriechzahl φ – wirkt präzise und elastisch',
    beiAenderung: (v) => aendern((x) => { x.kriechzahl = v; }),
  }), true);
  if (art && !art.mit_kriechzahl && !phiImmer) phi.classList.add('ist-ohne-wirkung');
  return [
    phi,
    mitKopf('Werte', auswahl({
      werte: kurz(katalog.werkstoffsaetze),
      gewaehlt: ziel.werkstoffsatz,
      titel: 'Bemessungswerte (f_cd, f_yd) oder charakteristische (f_ck, f_yk)',
      beiAenderung: (v) => aendern((x) => { x.werkstoffsatz = v; }),
    })),
    mitKopf('Rechenart', auswahl({
      werte: kurz(liste),
      gewaehlt: ziel.rechenart,
      titel: liste.map((a) => a.beschriftung).join(' · '),
      beiAenderung: (v) => aendern((x) => { x.rechenart = v; }),
    })),
  ];
}

/**
 * Eine Zeile «Rechenwahl» unter einem Kapitelkopf: ein kleiner Titel, darunter
 * die drei Felder. Beim Knicken stehen zwei solche Zeilen, mit «Verformung»
 * und «Widerstand» als Titel. `aendern` bekommt eine Funktion, die die Wahl
 * selbst ändert.
 */
export function rechenwahlZeile(titel, ziel, aendern, optionen) {
  return el('div.rechenwahl', {}, [
    el('span.rechenwahl-titel', { text: titel }),
    ...rechenwahlFelder(ziel, aendern, optionen),
  ]);
}

/**
 * Eine Analyse als kleine Karte: oben der Name, darunter ihre Zahlen, φ und
 * die Richtung, zuunterst Werte und Rechenart. Die Zahlenfelder richten sich
 * nach der Art -- die steht über dem Fenster und wird hier nicht gewählt.
 */
function spannungsZeile(eintrag, index, ort) {
  const k = (eintrag.spannungsfaelle || [])[index];
  const liste = (p) => p[ort.liste].find((x) => x.kennung === eintrag.kennung).spannungsfaelle;
  const aendern = (veraenderer) => projektAendern((p) => veraenderer(liste(p)[index]));
  const [oben, unten] = ort.raender(k);
  const zahl = (feld, titel, schritt) => zahlfeld({
    wert: k[feld], schritt, titel, leer: 0,
    beiAenderung: (v) => aendern((x) => { x[feld] = v; }),
  });
  const aktiv = k.aktiv !== false;

  // Welche Felder die Frage braucht, sagt der Kern (`katalog.spannungsanalyse`),
  // ebenso ihre Einheiten (`katalog.felder`). Hier steht nur, wie ein Feld über
  // seiner Zahl heisst, sein Titel und sein Schritt. Immer zwei Spalten, damit
  // die Zeilen untereinander dieselbe Gestalt behalten: eine Linie hat nur die
  // festgehaltene Zahl, daneben steht, wie weit sie läuft. Bis 2026-10-18 stand
  // je Art ein eigener Bauplan hier, mit den Einheiten darin.
  const frage = (zustand.katalog?.spannungsanalyse?.arten || []).find((a) => a.wert === k.art);
  const linie = frage?.groessen;
  const FELDER = {
    N_Ed: { kopf: 'N_Ed', schritt: 50, titel: (e) => `Normalkraft in ${e} – Zug positiv` },
    M_Ed: { kopf: 'M_Ed', schritt: 10, titel: (e) => `Moment in ${e}${linie ? ', festgehalten' : ''}` },
    eps_oben: { kopf: `ε ${oben}`, schritt: 0.5, titel: (e) => `Randdehnung ${oben} in ${e} – Zug positiv` },
    eps_unten: { kopf: `ε ${unten}`, schritt: 0.5, titel: (e) => `Randdehnung ${unten} in ${e} – Zug positiv` },
  };
  const spalten = (frage?.eingaben || []).map((feld) => {
    const { einheit } = feldangabe('spannungsfall', feld);
    const f = FELDER[feld];
    return mitKopf(`${f.kopf} [${einheit}]`, zahl(feld, f.titel(einheit), f.schritt));
  });
  if (linie) {
    spalten.push(mitKopf('', el('span.kurvenhinweis', { text: `0 … ${linie.kraft.zeichen}_Rd` })));
  }
  // Womit gerechnet wird -- je Analyse, wie in den Kapiteln, aber ohne
  // Handrechnung: eine Linie rechnet die Normalkraft genau.
  const [phi, werte, rechenart] = rechenwahlFelder(
    k, aendern, { arten: 'faserarten', phiImmer: true });

  return el('div.einwirkung.ist-spannung', { class: aktiv ? '' : 'ist-aus' }, [
    hakenSchalter(aktiv, (wert) => aendern((x) => { x.aktiv = wert; }), 'Analyse'),
    el('input.ew-name', {
      type: 'text', value: k.name, title: 'Bezeichnung der Analyse',
      on: { change: (e) => aendern((x) => { x.name = e.target.value; }) },
    }),
    // Beschriftung über dem Feld, nicht daneben: so bleibt das Raster der
    // Zeile dasselbe, gleich welche Art es ist.
    ...spalten,
    phi,
    ort.richtung(k, (wert) => aendern((x) => { x.richtung = wert; })),
    werte,
    rechenart,
    el('button.weg', {
      text: '×', title: 'Analyse entfernen',
      on: { click: () => projektAendern((p) => { liste(p).splice(index, 1); }) },
    }),
  ]);
}
