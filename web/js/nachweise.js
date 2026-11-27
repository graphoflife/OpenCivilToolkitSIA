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

import { erklaerung, feld, hakenSchalter, mitBild, wahlSchalter } from './bausteine.js';
import { el, zahlfeld } from './dom.js';
import {
  anfuegenKnopf, fallkopf, fallzeile, formelkopf,
} from './faelle.js';
import {
  eingeschaltet, fehltHinweis, gebrauchsstand, schalter, standOhne, zeilenstand,
} from './kapitel.js';
import { mitFormelzeichen } from './mathe.js';
import {
  ausVorlage, eintragAendern, eintragVon, feldangabe, katalog, naechsterName,
} from './zustand.js';

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
    ['Werte', 'je Material nach Rechenwahl; Vorgabe charakteristisch (f_ck, f_yk), präzise'],
    ['φ', 'nach Rechenwahl → E_c,eff = E_cm / (1 + φ), nur präzise'],
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
      stand: (e) => standOhne(zeilenstand(e.knickfaelle, 'Fall', 'Fälle', 'kein Fall'), ort.knick.fehlt(e)),
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
      stand: (e) => gebrauchsstand(e.quasistaendig, e[ort.gebrauch.aus]),
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
      stand: (e) => (fliessenGefordert(e) ? gebrauchsstand(e.haeufig, e[ort.gebrauch.aus])
        : { an: false, text: 'entfällt' }),
    },
  ];
}

/**
 * Die sechs Spannung-Dehnung-Analysen als Kapitel, je Art aus dem Katalog:
 * der Name auf dem Knopf kurz, über dem Fenster lang.
 */
export function analysenKapitel(ort) {
  return katalog('spannungsanalyse', 'arten').map((a) => ({
    schluessel: a.wert,
    name: a.beschriftung, titel: a.titel,
    bezug: (e) => `Spannung-Dehnung-Analyse · ${(ort.bezugAnalyse || ort.bezug)(e)}`,
    inhalt: (e) => analyseInhalt(e, a.wert, ort),
    stand: (e) => zeilenstand((e.spannungsfaelle || []).filter((k) => k.art === a.wert),
      'Diagramm', 'Diagramme', 'kein Diagramm'),
  }));
}

// ===========================================================================
// Was in den Fenstern steht
// ===========================================================================

/**
 * Die Zeile eines Nachweises mit *einem* Schalter: Duktilität, sprödes
 * Versagen und die Zeilen der Zwängung. Vorne der Schalter, dann die Marke,
 * die der Ort davor setzt (`ort.marke`: bei der Platte die Tragrichtung x),
 * der Name, dahinter wahlweise ein Feld -- der Beiwert der Grenze x/d, das φ der
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
 * ohne Hinweis. `ohneWirkung` sagt, warum er gerade nichts ändert: dann
 * steht die Zeile blass da, mit dem Satz an der Stelle des Hinweises.
 */
function schalterZeile(eintrag, ort, {
  feld, name, was = 'Nachweis', zusatz = null, nachweis = true, ohneWirkung = '',
}) {
  const vorne = nachweis ? ort.marke() : null;
  const art = vorne ? (zusatz ? '.mit-feld' : '') : (zusatz ? '.mit-grenze' : '.ist-breit');
  return el(`div.duktilitaetszeile${art}`, { class: ohneWirkung ? 'ist-ohne-wirkung' : '' }, [
    hakenSchalter(!!eintrag[feld],
      (wert) => eintragAendern(eintrag.kennung, (e) => { e[feld] = wert; }), was),
    vorne,
    el('span.postenname', { text: name }),
    zusatz,
    el('span.kurvenhinweis', { text: nachweis ? ort.hinweis(eintrag, feld) : ohneWirkung }),
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

/** Duktilität: ein Schalter und der Beiwert k der Grenze x/d ≤ k·435/f_yd. */
function duktilitaetInhalt(eintrag, ort) {
  return [
    schalterZeile(eintrag, ort, {
      feld: 'duktilitaet', name: 'x/d ≤ k·435/f_yd, k =',
      // Vorgabe und Höchstwert des Beiwerts stehen am Feld im Kern: die
      // Vorgabe in der Vorlage des Eintrags, der Höchstwert in seiner
      // Grenze. Leer gelassen bleibt der bisherige Wert.
      zusatz: zahlfeld({
        wert: eintrag.x_d_max, schritt: 0.05, angabe: feldangabe(ort.klasse, 'x_d_max'),
        titel: `Beiwert k der Grenze x/d ≤ k · 435 N/mm² / f_yd (SIA 262:2025, 4.1.4.2.5); `
          + `Vorgabe ${katalog('vorlagen', ort.klasse).x_d_max}, `
          + `höchstens ${feldangabe(ort.klasse, 'x_d_max').bis}`,
        beiAenderung: (v) => eintragAendern(eintrag.kennung, (e) => { e.x_d_max = v; }),
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
  const aendern = (veraenderer) => eintragAendern(eintrag.kennung, veraenderer);
  const knick = ort.knick;

  return [
    // Zwei Wahlen: womit die Verformung gerechnet wird und womit der
    // Querschnitt widersteht. Ohne Handrechnung: beim Knicken zählt die
    // Normalkraft genau. Die Verformung nur präzise -- mit dem
    // Spannungsblock wäre die Ausmitte nahe der Grenzkraft nicht eindeutig.
    rechenwahlZeile('Verformung (e_2d)', eintrag.knicken_wahl_verformung,
      (veraenderer) => aendern((q) => veraenderer(q.knicken_wahl_verformung)),
      { werkstoffe: { ...ort.werkstoffe(eintrag), klasse: 'knickverformungswahl' } }),
    rechenwahlZeile('Widerstand (N_Rd)', eintrag.knicken_wahl_widerstand,
      (veraenderer) => aendern((q) => veraenderer(q.knicken_wahl_widerstand)),
      { werkstoffe: { ...ort.werkstoffe(eintrag), klasse: 'knickwiderstandswahl' } }),
    faelle.length ? fehltHinweis(knick.fehlt(eintrag)) : null,
    faelle.length ? fallkopf(knick.kopf) : null,
    ...(faelle.length
      ? faelle.map((_, i) => knickZeile(eintrag, ort, i))
      : [el('div.leer', { text: knick.leer })]),
    anfuegenKnopf('Knicknachweis', (name) => aendern((q) => {
      q.knickfaelle = q.knickfaelle || [];
      q.knickfaelle.push(ausVorlage(knick.vorlage, { name: name(q.knickfaelle) }));
    })),
  ];
}

function knickZeile(eintrag, ort, index) {
  const k = (eintrag.knickfaelle || [])[index];
  const aendern = (veraenderer) => eintragAendern(eintrag.kennung, (e) => veraenderer(e.knickfaelle[index]));
  const titel = ort.knick.titel;
  // Eine Länge null gibt es nicht -- geleert bleibt der bisherige Wert.
  const zahl = (feld, schritt) => zahlfeld({
    wert: k[feld], schritt, titel: titel[feld], angabe: feldangabe(ort.knick.vorlage, feld),
    beiAenderung: (v) => aendern((x) => { x[feld] = v; }),
  });

  // Beim gezeichneten Querschnitt steht die Zugseite oben neben dem Namen:
  // «Zug unten» braucht mehr Platz als eine Zahl.
  const richtung = ort.knick.richtung;
  return fallzeile({
    fall: k, aendern, was: 'Knicknachweis', nameTitel: 'Bezeichnung des Knicknachweises',
    liste: { kennung: eintrag.kennung, pfad: 'knickfaelle', index },
    oben: richtung ? richtung(k, (wert) => aendern((x) => { x.richtung = wert; })) : null,
    zahlen: [zahl('N_Ed', 50), zahl('M_Ed_1', 10), zahl('laenge', 0.5), zahl('knicklaenge', 0.5)],
    entfernenTitel: 'Knicknachweis entfernen',
    entfernen: () => eintragAendern(eintrag.kennung, (e) => { e.knickfaelle.splice(index, 1); }),
  });
}

/**
 * Die Rissanforderung als erste Zeile der drei Rissnachweise -- Zwang,
 * quasi-ständig, häufig. Sie gehört dem Bauteil, nicht dem Nachweis: in
 * einem der drei Fenster gewählt, gilt sie in allen. Vorher stand sie oben
 * bei der Platte, weit weg von den Nachweisen, die sie brauchen (Benutzer,
 * 2026-10-16).
 */
function rissanforderungZeile(eintrag, ort) {
  return feld('Rissanforderung', wahlSchalter({
    werte: katalog('rissanforderungen').map((r) => ({
      wert: r.wert, beschriftung: r.beschriftung,
    })),
    gewaehlt: eintrag.rissanforderung || 'normal',
    titel: 'Bestimmt σ_s,adm (Tab. 17)',
    setzen: (v) => eintragAendern(eintrag.kennung, (e) => { e.rissanforderung = v; }),
  }), erklaerung([
    ['Gilt für', 'alle Rissnachweise: Riss bei Zwang, Stahlspannung quasi-ständig '
      + 'und Fliessen häufig. Hier geändert, ändert sie sich in allen dreien.'],
    ['Bestimmt', 'σ_s,adm nach Tab. 17 und ob «Fliessen häufig» gefordert ist'],
  ]));
}

/** Die gewählte Rissanforderung aus dem Katalog -- oder nichts, wenn er fehlt. */
function anforderung(querschnitt) {
  return katalog('rissanforderungen')
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
        el('span.zeilenfeld-name', {}, [kriechzahlName(ort.klasse, 'zwaengung_biegung_kriechzahl')]),
        zahlfeld({
          wert: eintrag.zwaengung_biegung_kriechzahl ?? 0, schritt: 0.1, leer: 0,
          angabe: feldangabe(ort.klasse, 'zwaengung_biegung_kriechzahl'),
          titel: 'Kriechzahl φ der Zwängung auf Biegung: E_c,eff = E_cm / (1 + φ)',
          beiAenderung: (v) => eintragAendern(eintrag.kennung, (e) => {
            e.zwaengung_biegung_kriechzahl = v;
          }),
        }),
      ]),
    }),
    // Ändert nur die Zwängung auf Normalkraft: die Dicke, über die der
    // Querschnitt unter Zug reisst.
    // Bis 2026-11-19 stand sie auch ohne die Zwängung auf Normalkraft da,
    // als wirkte sie.
    schalterZeile(eintrag, ort, {
      feld: 'zwaengung_begrenzt', name: 'Begrenzung auf 500 mm', was: 'Zwängung',
      nachweis: false,
      ohneWirkung: eintrag.zwaengung ? '' : 'wirkt nur mit der Zwängung auf Normalkraft',
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
  const aendern = (veraenderer) => eintragAendern(eintrag.kennung, (e) => veraenderer(e[feld]));
  const spalten = ort.gebrauch.spalten(eintrag);

  return [
    rissanforderungZeile(eintrag, ort),
    hinweis ? el('p.hinweis.hinweis-annahme', { text: hinweis }) : null,
    rechenwahlZeile('Rechenwahl', liste.wahl,
      (veraenderer) => aendern((l) => veraenderer(l.wahl)), {
        werkstoffe: { ...ort.werkstoffe(eintrag), klasse: ort.gebrauch.wahl },
      }),

    el('div.duktilitaetszeile.ist-anteil', {}, [
      hakenSchalter(abgeleitet, (wert) => aendern((l) => {
        l.aus_tragsicherheit = wert;
      }), 'Ableitung'),
      zahlfeld({
        wert: liste.anteil, schritt: 5, angabe: feldangabe(ort.gebrauch.liste, 'anteil'),
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
    faelle.length ? fallkopf(spalten.map((s) => s.kopf)) : null,
    ...(faelle.length
      ? faelle.map((_, i) => gebrauchsfallZeile(eintrag, ort, spalten, feld, wort, i))
      : [el('div.leer', {
        text: !abgeleitet ? `Noch kein ${wort}er Lastfall.`
          : eingeschaltet(eintrag[ort.gebrauch.aus]) ? 'Nur die abgeleiteten Fälle.'
            : 'Noch keine eingeschaltete Einwirkung der Tragsicherheit – abgeleitet wird nichts.',
      })]),
    // Ein neuer Gebrauchsfall heisst nach seiner Art, «Häufig 1», nicht wie
    // der Knopf (Benutzer, 2026-11-20).
    anfuegenKnopf('Lastfall', () => aendern((l) => {
      l.faelle.push(ausVorlage(ort.gebrauch.vorlage, { name: naechsterName(neu, l.faelle) }));
    })),
  ];
}

/** Ein Lastfall unter Gebrauchslast auf einer Zeile -- wie eine Einwirkung, ohne Querkraft. */
function gebrauchsfallZeile(eintrag, ort, spalten, feld, wort, index) {
  const k = eintrag[feld].faelle[index];
  const aendern = (veraenderer) => eintragAendern(eintrag.kennung, (e) => veraenderer(e[feld].faelle[index]));

  return fallzeile({
    fall: k, aendern, was: 'Lastfall', nameTitel: `Bezeichnung des ${wort}en Lastfalls`,
    liste: { kennung: eintrag.kennung, pfad: `${feld}.faelle`, index },
    zahlen: spalten.map((s) => zahlfeld({
      wert: k[s.feld], schritt: s.schritt, titel: s.titel(wort), leer: 0,
      beiAenderung: (v) => aendern((x) => { x[s.feld] = v; }),
    })),
    entfernenTitel: `${wort[0].toUpperCase()}${wort.slice(1)}en Lastfall entfernen`,
    entfernen: () => eintragAendern(eintrag.kennung, (e) => { e[feld].faelle.splice(index, 1); }),
  });
}

/**
 * Eine Art der Spannung-Dehnung-Analyse: die Diagramme dieser Art, und ein
 * Knopf für ein weiteres -- «+ Diagramm», nicht «+ Bild» (Benutzer,
 * 2026-10-23), wie in der Statik-Analyse des Balkensystems.
 *
 * Kein Nachweis -- es wird nichts gegen etwas gehalten. Darum auch keine
 * Erfüllungsgrade in der Zusammenfassung; die Diagramme stehen im eigenen
 * Reiter. Jede Art hat ihr Fenster, und was eine Zeile fragt, hängt an der
 * Art: eine Zeile, die nach N und M fragt, soll nicht daneben zwei
 * Dehnungsfelder zeigen, die sie nicht liest. Die Diagramme aller Arten
 * stehen in einer Liste der Platte; jede Zeile behält ihre Stelle darin.
 */
function analyseInhalt(eintrag, art, ort) {
  const stellen = (eintrag.spannungsfaelle || [])
    .map((k, i) => (k.art === art ? i : -1))
    .filter((i) => i >= 0);

  return [
    ...(stellen.length
      ? stellen.map((i) => spannungsZeile(eintrag, i, ort))
      : [el('div.leer', { text: 'Noch kein Diagramm.' })]),
    anfuegenKnopf('Diagramm', (name) => eintragAendern(eintrag.kennung, (e) => {
      e.spannungsfaelle = e.spannungsfaelle || [];
      e.spannungsfaelle.push(ausVorlage(ort.vorlage, { name: name(e.spannungsfaelle), art }));
    })),
  ];
}

/**
 * Ein Feld mit seiner Beschriftung darüber -- eine Formel bleibt klein
 * geschrieben, ein Formelzeichen mit Einheit (`['N_{Ed}', 'kN']`) gesetzt.
 */
export function mitKopf(kopf, eingabe) {
  let zelle;
  if (Array.isArray(kopf)) zelle = el('span.spaltenkopf.mit-zeichen', {}, [formelkopf(...kopf)]);
  else if (kopf instanceof Node) zelle = el('span.spaltenkopf', {}, [kopf]);
  else zelle = el('span.spaltenkopf', { text: kopf });
  return el('div.mit-kopf', {}, [zelle, eingabe]);
}

/**
 * Die Kriechzahl, überall gleich: «Kriechzahl φ», wie der Kern das Feld
 * nennt, φ in der Formelschrift (Benutzer, 2026-11-20). Bis dahin stand hier
 * ein φ allein, bei der Zwängung auf Biegung ein φ in anderer Schrift und
 * nur bei der Verformung das Wort.
 */
export function kriechzahlName(klasse, feldname = 'kriechzahl') {
  return mitFormelzeichen(feldangabe(klasse, feldname).heisst);
}

/**
 * Die Rechenarten, die die Wahl der Klasse `klasse` anbietet, in der Folge
 * ihres Feldes (`feldangabe(klasse, 'rechenarten').wahl`) -- als Stellungen
 * eines Schalters: ihr Bild, der kurze Name, der lange im Titel. Das Bild
 * zeigt, wie die Art den Beton rechnet (sinnbilder.js, `rechenart-…`).
 */
function rechenartStellungen(klasse) {
  const alle = katalog('rechenwahl', 'rechenarten') || [];
  return mitBild((feldangabe(klasse, 'rechenarten').wahl || [])
    .map((wert) => alle.find((e) => e.wert === wert))
    .filter(Boolean)
    .map((e) => ({ wert: e.wert, beschriftung: e.kurz, titel: e.beschriftung })), 'rechenart');
}

/**
 * Je Material eine Zeile: sein Name und womit es rechnet, mit Bemessungs-
 * oder mit charakteristischen Werten -- beim Beton darunter seine
 * Rechenart. So wählt seit 2026-11-20 jedes Modul die Werte je Material
 * (Benutzer: die Darstellung der Querschnittsanalyse überall), seit
 * 2026-11-25 auch die Rechenart je Beton (Benutzer: unter dem Beton, in
 * jedem Modul). Bietet das Kapitel nur eine Art an, wie die Verformung
 * beim Knicken, steht kein Schalter. Das Holz hat keinen Wertesatz -- nur
 * Bemessungswerte, darum kein Titel im Katalog (`satztitel`) --, in einer
 * Analyse aber den Schalter, wie es rechnet: linear oder auf Druck
 * elastisch-plastisch (seit 2026-11-26).
 *
 * `ziel` hält `werkstoffsaetze`, `rechenarten` und `holzrechnungen`, je
 * Kennung eines Materials seine Wahl; was eines ohne eigene wählt, sagt der
 * Kern (`feldangabe(klasse, …).vorgabe`) -- und ob die Klasse die Wahl hat. `materialien` sind die Kennungen der
 * Materialien des Bauteils -- `null`, solange der Kern sie nicht kennt, dann
 * sagt `wartet` warum; leer sagt es `leer`. Eine Wahl schreibt nur die
 * Materialien, die das Bauteil jetzt hat: die eines ausgewechselten fällt
 * dabei weg und kehrt mit ihm nicht still zurück. `mitRechenart: false`
 * lässt die Rechenart des Betons weg, wo er immer gleich rechnet -- im
 * Verbund plastisch.
 */
export function werkstoffzeilen(ziel, aendern, {
  materialien, klasse, wartet = 'Der Kern sucht die Materialien …',
  leer = 'Noch kein Material im Querschnitt.', mitRechenart = true,
}) {
  // «Je Material», nicht «Werte»: unter dem Beton steht auch seine
  // Rechenart, unter dem Holz nur, wie es rechnet.
  const kopf = el('span.spaltenkopf', { text: 'Je Material' });
  if (materialien === null) return el('div.werkstoffzeilen', {}, [kopf, el('div.leer', { text: wartet })]);
  if (!materialien.length) return el('div.werkstoffzeilen', {}, [kopf, el('div.leer', { text: leer })]);

  const gewaehlt = (feld, kennung) => ziel[feld]?.[kennung] ?? feldangabe(klasse, feld).vorgabe;
  const setzen = (feld, kennung, wert) => aendern((x) => {
    const bisher = x[feld] || {};
    x[feld] = Object.fromEntries(materialien
      .filter((k) => k === kennung || k in bisher)
      .map((k) => [k, k === kennung ? wert : bisher[k]]));
  });
  // Im Schalter die kurzen Namen, die langen in den Titeln seiner Stellungen.
  const kurz = (l) => (l || []).map((e) => ({ wert: e.wert, beschriftung: e.kurz, titel: e.beschriftung }));
  const arten = mitRechenart ? rechenartStellungen(klasse) : [];
  const hoelzer = 'vorgabe' in feldangabe(klasse, 'holzrechnungen')
    ? kurz(katalog('rechenwahl', 'holzrechnungen')) : [];
  const zeile = (kennung) => {
    const material = eintragVon(kennung);
    if (!material) return null;
    const satz = katalog('rechenwahl', 'satztitel')?.[material.art];
    return el('div.werkstoffzeile', { class: `ist-${material.art}` }, [
      el('span.werkstoffname', { text: material.name || material.sorte }),
      satz ? wahlSchalter({
        werte: kurz(katalog('rechenwahl', 'werkstoffsaetze')),
        gewaehlt: gewaehlt('werkstoffsaetze', kennung),
        titel: satz,
        setzen: (v) => setzen('werkstoffsaetze', kennung, v),
      }) : null,
      material.art === 'beton' && arten.length > 1 ? wahlSchalter({
        werte: arten,
        gewaehlt: gewaehlt('rechenarten', kennung),
        titel: 'Wie der Beton gerechnet wird',
        setzen: (v) => setzen('rechenarten', kennung, v),
      }) : null,
      material.art === 'holz' && hoelzer.length ? wahlSchalter({
        werte: hoelzer,
        gewaehlt: gewaehlt('holzrechnungen', kennung),
        titel: 'Wie das Holz rechnet – immer mit Bemessungswerten',
        setzen: (v) => setzen('holzrechnungen', kennung, v),
      }) : null,
    ]);
  };
  return el('div.werkstoffzeilen', {}, [kopf, ...materialien.map(zeile)]);
}

/**
 * Die Felder einer Rechenwahl: Kriechzahl φ und je Material die Werte, je
 * Beton die Rechenart -- in jedem Kapitel und in jeder Analyse dieselben.
 * `ziel` trägt die Felder `kriechzahl`, `werkstoffsaetze` und
 * `rechenarten`, `aendern` ändert es im Projekt; `werkstoffe` sagt, welche
 * Materialien das Bauteil hat und zu welcher Klasse des Kerns die Wahl
 * gehört -- deren Feld sagt, welche Rechenarten gelten (`werkstoffzeilen`).
 * Wirkt φ bei keiner gewählten Art, steht das Feld blass da -- es bleibt
 * aber stehen, damit die Zahl nicht verloren geht, wenn man die Art wieder
 * wechselt. `phiImmer`: in den Analysen rechnet der ungerissene Teil immer
 * mit E_cm/(1+φ), dort wirkt φ bei jeder Art -- ebenso im Schubfluss
 * (qa_schubfluss.js). Ohne Beton kriecht nichts: dann steht statt des
 * Feldes `null` (seit 2026-11-26, Holz und Stahl).
 */
export function rechenwahlFelder(ziel, aendern, { phiImmer = false, werkstoffe }) {
  const { klasse, materialien } = werkstoffe;
  const alle = katalog('rechenwahl', 'rechenarten') || [];
  const vorgabe = feldangabe(klasse, 'rechenarten').vorgabe;
  const betone = (materialien || []).filter((k) => eintragVon(k)?.art === 'beton');
  if (materialien?.length && !betone.length) return [null, werkstoffzeilen(ziel, aendern, werkstoffe)];
  const wirkt = betone.some((k) => alle.find((a) => a.wert === (ziel.rechenarten?.[k] ?? vorgabe))
    ?.mit_kriechzahl);
  const phi = mitKopf(kriechzahlName('rechenwahl'), zahlfeld({
    wert: ziel.kriechzahl ?? 0, schritt: 0.1, leer: 0, angabe: feldangabe('rechenwahl', 'kriechzahl'),
    titel: phiImmer
      ? 'Kriechzahl φ – wirkt auf den ungerissenen Teil, präzise auch auf den gerissenen'
      : 'Kriechzahl φ – wirkt nur präzise',
    beiAenderung: (v) => aendern((x) => { x.kriechzahl = v; }),
  }));
  if (betone.length && !wirkt && !phiImmer) phi.classList.add('ist-ohne-wirkung');
  return [phi, werkstoffzeilen(ziel, aendern, werkstoffe)];
}

/**
 * Eine Zeile «Rechenwahl» unter einem Kapitelkopf: ein kleiner Titel, darunter
 * die Felder. Beim Knicken stehen zwei solche Zeilen, mit «Verformung»
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
  const aendern = (veraenderer) => eintragAendern(eintrag.kennung,
    (e) => veraenderer(e.spannungsfaelle[index]));
  const [oben, unten] = ort.raender(k);
  const zahl = (feld, titel, schritt) => zahlfeld({
    wert: k[feld], schritt, titel, leer: 0, angabe: feldangabe(ort.vorlage, feld),
    beiAenderung: (v) => aendern((x) => { x[feld] = v; }),
  });

  // Welche Felder die Frage braucht, sagt der Kern (`katalog.spannungsanalyse`),
  // ebenso ihre Einheiten (`katalog.felder`). Hier steht nur, wie ein Feld über
  // seiner Zahl heisst, sein Titel und sein Schritt. Immer zwei Spalten, damit
  // die Zeilen untereinander dieselbe Gestalt behalten: eine Linie hat nur die
  // festgehaltene Zahl, daneben steht, wie weit sie läuft. Bis 2026-10-18 stand
  // je Art ein eigener Bauplan hier, mit den Einheiten darin.
  const frage = katalog('spannungsanalyse', 'arten').find((a) => a.wert === k.art);
  const linie = frage?.groessen;
  const FELDER = {
    N_Ed: { kopf: 'N_{Ed}', schritt: 50, titel: (e) => `Normalkraft in ${e} – Zug positiv` },
    M_Ed: { kopf: 'M_{Ed}', schritt: 10, titel: (e) => `Moment in ${e}${linie ? ', festgehalten' : ''}` },
    eps_oben: {
      kopf: `\\varepsilon\\ \\text{${oben}}`, schritt: 0.5,
      titel: (e) => `Randdehnung ${oben} in ${e} – Zug positiv`,
    },
    eps_unten: {
      kopf: `\\varepsilon\\ \\text{${unten}}`, schritt: 0.5,
      titel: (e) => `Randdehnung ${unten} in ${e} – Zug positiv`,
    },
  };
  const spalten = (frage?.eingaben || []).map((feld) => {
    const { einheit } = feldangabe(ort.vorlage, feld);
    const f = FELDER[feld];
    return mitKopf([f.kopf, einheit], zahl(feld, f.titel(einheit), f.schritt));
  });
  if (linie) {
    spalten.push(mitKopf('', el('span.kurvenhinweis', { text: `0 … ${linie.kraft.zeichen}_Rd` })));
  }
  // Womit gerechnet wird -- je Analyse, wie in den Kapiteln, aber ohne
  // Handrechnung: eine Linie rechnet die Normalkraft genau.
  const [phi, werte] = rechenwahlFelder(k, aendern, {
    phiImmer: true, werkstoffe: { ...ort.werkstoffe(eintrag), klasse: ort.vorlage },
  });

  // Beschriftung über dem Feld, nicht daneben: so bleibt das Raster der
  // Zeile dasselbe, gleich welche Art es ist. Werte und Rechenart je Material
  // darunter, über die ganze Breite -- in einer Zeile wären sie abgeschnitten.
  return fallzeile({
    fall: k, aendern, was: 'Analyse', nameTitel: 'Bezeichnung der Analyse',
    liste: { kennung: eintrag.kennung, pfad: 'spannungsfaelle', index },
    zahlen: [...spalten, phi, ort.richtung(k, (wert) => aendern((x) => { x.richtung = wert; }))]
      .filter(Boolean),
    unten: [werte],
    entfernenTitel: 'Analyse entfernen',
    entfernen: () => eintragAendern(eintrag.kennung, (e) => { e.spannungsfaelle.splice(index, 1); }),
    klasse: '.ist-spannung',
  });
}
