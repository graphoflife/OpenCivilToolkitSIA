/**
 * qa_zeichnung.js -- das Zeichenfenster der Querschnittsanalyse: der Adapter.
 *
 * Das allgemeine Fenster (`cad_fenster.js`) kennt nur Knoten und Elemente
 * in drei Formen. Was sie im Querschnitt sind, steht hier -- je Art ein
 * Werkzeug mit eigenem Knopf (Benutzer, 2026-10-23):
 *
 *   Polygon      eine Fläche mit Beton -- oder ohne Material eine Aussparung
 *   Bewehrung    eine Linie mit Stäben (nach Anzahl, Teilung oder verschmiert)
 *                oder ein einzelner Stab -- wie, sagt der Schalter in ihrem
 *                Fenster
 *   Spannstahl   ein Spannglied je Klick (qa_spannglied.js)
 *   (Profil)     ein Stahlprofil der Tabelle -- ohne Werkzeug: eingesetzt
 *                wird es mit der Vorlage «Stahlprofil» (qa_profile.js)
 *   Schubwand    eine Linie mit Dicke und Bügeln
 *   Hilfslinie   eine Linie, die nicht mitrechnet
 *   Hilfspunkt   ein Knoten ohne Element, zum Fangen
 *
 * Im schwebenden Fenster steht immer nur eine Art: beim Zeichnen die des
 * Werkzeugs, bei der Auswahl die des Gewählten. Eine gezeichnete Linie
 * wechselt ihre Art nicht -- bis 2026-10-23 tat sie das über ein
 * Auswahlfeld «Art», und die Linie hiess im Knopf nur «Linie».
 *
 * WAS HIER GERECHNET WIRD -- UND WAS NICHT:
 * Nichts, was in die Rechnung geht. Die Stäbe einer Linie und ihre
 * tatsächliche Teilung, der Schwerpunkt, die Zellen der Schubwände, welches
 * Polygon in welchem liegt, jede Meldung und jeder Name («Linie 2») kommen
 * vom Kern über die Anfrage `geometrie` -- auch das gerückte Polygon der
 * Überdeckung und wohin «Überdeckung beachten» die Bewehrung schiebt. Diese
 * Antwort gilt nur, solange die Zeichnung dieselbe ist, nach der gefragt
 * wurde.
 */

import { api } from './api.js';
import {
  VAR, hakenSchalter, materialliste, mitBild, mitVar, wahlSchalter,
} from './bausteine.js';
import {
  nachBild, pfad, text, zahlText,
} from './cad_ansicht.js';
import {
  auswahlEigenschaften, cadApp, cadBereichMitListe, frischeAntwort, jaNein, kernfehler, laengenzeile,
  lagefelder, meldungenJe, meldungszeilen, mitTitel, umrissVon, vorgabe, zahlfeldMitVar, zugleich,
} from './cad_app.js';
import { cadZeile } from './cad_palette.js';
import {
  abstand, eckeSchluessel, knotenname,
} from './cad_modell.js';
import {
  PROFIL, profilFang, profilFelder, profilInfo, profilPfad, profilUmriss,
} from './qa_profile.js';
import {
  SPANNGLIED, SPANNSTAHL, gliedFelder, gliedInfo, gliedText, gliedVorgabe, vorgabePruefen,
} from './qa_spannglied.js';
import { vorlageOeffnen } from './qa_vorlagen.js';
import { sinnbild } from './sinnbilder.js';
import {
  el, melden, svgEl, zahlfeld,
} from './dom.js';
import {
  ausVorlage, eintragVon, feldangabe, katalog, materialien, mitteAendern, zustand,
} from './zustand.js';

/**
 * Die Arten des Querschnitts, für das allgemeine Fenster. Eine Bewehrung
 * lässt sich nicht teilen: die Stäbe zweier Hälften wären andere als die
 * des Ganzen (n Stäbe je Hälfte, oder ein doppelter Stab in der Mitte).
 * Umgekehrt tauschen Start- und Endeisen mit -- die Stäbe bleiben, wo sie
 * sind.
 *
 * `rang`: welche Ecke ein Klick nimmt, wo mehrere aufeinander liegen und
 * keines ihrer Elemente gewählt ist -- zuerst die Bewehrung, dann die
 * anderen Linien, zuletzt die Flächen; je Art die zuletzt gezeichnete.
 *
 * `klasse`: unter welchem Namen der Katalog Vorlage und Felder der Elemente
 * führt (`ausVorlage`, `feldangabe`).
 */
const ARTEN = [
  { liste: 'flaechen', klasse: 'flaeche', form: 'flaeche', vorsilbe: 'F', rang: 4 },
  { liste: 'staebe', klasse: 'stab', form: 'punkt', vorsilbe: 'S', rang: 1 },
  SPANNGLIED,
  {
    liste: 'stablinien', klasse: 'stablinie', form: 'linie', vorsilbe: 'L', rang: 0, teilbar: false,
    umkehren: (e) => { [e.starteisen, e.endeisen] = [e.endeisen, e.starteisen]; },
  },
  { liste: 'schubwaende', klasse: 'schubwand', form: 'linie', vorsilbe: 'L', rang: 2 },
  { liste: 'hilfslinien', klasse: 'hilfslinie', form: 'linie', vorsilbe: 'L', rang: 3 },
  PROFIL,
];

/** Unter welchem Namen der Katalog die Elemente einer Liste führt. */
function klasseVon(liste) {
  return ARTEN.find((x) => x.liste === liste).klasse;
}

/**
 * Die Arten von Material, die ein Feld einer Liste nimmt -- vom Kern
 * (`materialfeld`): eine Fläche Beton, Baustahl oder Holz, ein Stab Betonstahl.
 */
function stoffeVon(liste, feld) {
  return feldangabe(klasseVon(liste), feld).stoffe;
}

/** Ob es das Material `kennung` von einer der `arten` gibt. */
function gibt(arten, kennung) {
  return arten.some((art) => materialien(art).some((m) => m.kennung === kennung));
}

/** Das erste Material der ersten der `arten`, von der es eines gibt -- oder undefined. */
function erstes(arten) {
  return arten.map((art) => materialien(art)[0]?.kennung).find(Boolean);
}

/**
 * Wie ein Polygon aussieht: in der Farbe seines Materials, ohne eines als
 * Aussparung. Eines, das es nicht gibt oder das nicht passt, wie Beton --
 * seine Meldung sagt, was fehlt.
 */
function flaechenklasse(material) {
  if (!material) return 'cad-loch';
  const art = eintragVon(material)?.art;
  return stoffeVon('flaechen', 'material').includes(art) ? `cad-${art}` : 'cad-beton';
}

/** Die Listen, deren Elemente Linien sind -- sie haben Anfang und Ende. */
const LINIENLISTEN = ARTEN.filter((x) => x.form === 'linie').map((x) => x.liste);

/**
 * Die Werkzeuge, in der Folge ihrer Knöpfe. Die Bewehrung zeichnet als
 * Linie oder als Punkt, je nach dem Schalter in ihrem Fenster
 * (`vorgaben.bewehrung`).
 */
const WERKZEUGE = [
  { name: 'polygon', text: 'Polygon', zeichen: 'cad-polygon', taste: 'p', form: 'polygon',
    titel: 'Polygon: eine Fläche aus Beton, Baustahl oder Holz – oder eine Aussparung' },
  { name: 'bewehrung', text: 'Bewehrung', zeichen: 'cad-bewehrung', taste: 'b',
    form: (a) => (a.qa.vorgaben.bewehrung === 'punkt' ? 'knoten' : 'linie'),
    titel: 'Bewehrung: eine Linie mit Stäben oder einzelne Stäbe' },
  SPANNSTAHL,
  { name: 'schubwand', text: 'Schubwand', zeichen: 'cad-schubwand', taste: 'w', form: 'linie',
    titel: 'Schubwand: eine Wand mit Bügeln, für Querkraft und Torsion' },
  { name: 'hilfspunkt', text: 'Hilfspunkt', zeichen: 'cad-hilfspunkt', taste: 'k', form: 'knoten',
    titel: 'Hilfspunkt: ein Knoten ohne Element, zum Fangen' },
  { name: 'hilfslinie', text: 'Hilfslinie', zeichen: 'cad-hilfslinie', taste: 'h', form: 'linie',
    titel: 'Hilfslinie: rechnet nicht mit – geschlossen wird sie zur Fläche' },
];

/** Welche Liste eine Linie des Werkzeugs füllt. */
const LINIE_VON = { bewehrung: 'stablinien', schubwand: 'schubwaende', hilfslinie: 'hilfslinien' };

// ===========================================================================
// Das Fenster einer Analyse
// ===========================================================================

/**
 * Das Zeichenfenster einer Analyse, samt der Liste darunter. Die Tafel ruft
 * das bei jedem Neubau.
 */
export function zeichenbereich(analyse, listeBauen) {
  return cadBereichMitListe(fensterVon(analyse.kennung), listeBauen);
}

/**
 * Die Zeichenfenster der Analysen, je Kennung eines (cad_app.js). Was die
 * Analyse an der Ansicht braucht -- Vorgaben, Antwort des Kerns, Namen --,
 * hängt als `a.qa` am Fenster.
 */
const fensterVon = cadApp('qa', adapter, (a) => { a.qa = a.adapter.qa; });

/**
 * Die Materialien, auf die die Analyse zeigt, wie der Kern sie zählt
 * (`QuerschnittsanalyseEintrag.materialien`, mit der Antwort zur Zeichnung)
 * -- null, solange die Antwort zur jetzigen Zeichnung aussteht.
 */
export function materialienVon(kennung) {
  return frischeAntwort(fensterVon(kennung))?.materialien ?? null;
}

/**
 * Für die Werte je Material einer Rechenwahl (`werkstoffzeilen` in
 * nachweise.js): die Materialien der Analyse -- und solange sie fehlen,
 * warum. Auch für ein Balkensystem, dessen Querschnitt aus ihr kommt.
 */
export function werkstoffeVon(kennung) {
  const materialien = materialienVon(kennung);
  return {
    materialien,
    wartet: (materialien === null && kernfehler(fensterVon(kennung))) || 'Der Kern liest die Zeichnung …',
  };
}

/**
 * Was der Kern zuletzt über die Bauweise sagte: eine Angabe der letzten
 * Antwort, auch einer älteren -- sonst sprängen die Kacheln bei jeder
 * Änderung um, bis die neue da ist.
 */
function bauweisenangabe(kennung, schluessel) {
  const a = fensterVon(kennung);
  return (frischeAntwort(a) || a.adapter.kern.antwort)?.[schluessel] || '';
}

/** Die Bauweise des Querschnitts: «stahlbeton», «stahl», «verbund», «holz» -- leer ohne. */
export function bauweiseVon(kennung) {
  return bauweisenangabe(kennung, 'bauweise');
}

/**
 * Warum der Querschnitt keinen Nachweis hat -- er ist aus mehreren
 * Hölzern: «einen Holzquerschnitt aus mehreren Hölzern …». Leer bei allen
 * anderen.
 */
export function ohneNachweiseVon(kennung) {
  return bauweisenangabe(kennung, 'ohne_nachweise');
}

/**
 * Warum der Querschnitt keine Spannung-Dehnung-Analyse hat -- im Verbund:
 * «Einen Verbundquerschnitt rechnen …». Leer bei allen anderen.
 */
export function ohneAnalysenVon(kennung) {
  return bauweisenangabe(kennung, 'ohne_analysen');
}

/**
 * Was der Kern zu den Knickspannungskurven sagt: `eigene` je Achse die des
 * einzigen Profils, `{kurve, grund}` -- leer, wo der Querschnitt mehr ist
 * als ein Profil --, `fehlen` als Satz, welche den Fällen von Knicken und
 * Kippen fehlt, leer, wo keine fehlt.
 */
export function knickkurvenVon(kennung) {
  return {
    eigene: bauweisenangabe(kennung, 'knickkurven'),
    fehlen: bauweisenangabe(kennung, 'knickkurven_fehlen'),
  };
}

// ===========================================================================
// Der Adapter
// ===========================================================================

/**
 * Was die Werkzeuge als Nächstes anlegen, je Liste -- dazu, ob die Bewehrung
 * als Linie oder als Punkt zeichnet. Ansichtssache, nicht Teil des Projekts.
 */
function vorgabenNeu() {
  const mit = (liste, felder = {}) => ausVorlage(klasseVon(liste), felder);
  const stahl = (liste) => mit(liste, { stahl: erstes(stoffeVon(liste, 'stahl')) || '' });
  return {
    bewehrung: 'linie',
    staebe: stahl('staebe'),
    stablinien: stahl('stablinien'),
    schubwaende: stahl('schubwaende'),
    hilfslinien: mit('hilfslinien'),
    flaechen: mit('flaechen', { material: erstes(stoffeVon('flaechen', 'material')) || '' }),
    spannglieder: gliedVorgabe(),
  };
}

/**
 * Die Vorgaben, geprüft gegen das Projekt: einem Material, das es nicht
 * mehr gibt, folgt das erste, das das Feld nimmt -- wie in einem neuen
 * Fenster. Bis 2026-11-19 blieb ein gelöschter Stahl in der Vorgabe, und
 * jeder neue Stab verwies ins Leere. Gibt es keines, bleibt der alte
 * Verweis stehen: ohne Material wäre das Polygon still eine Aussparung.
 */
function vorgaben(a) {
  const v = a.qa.vorgaben;
  for (const liste of ['staebe', 'stablinien', 'schubwaende']) {
    const arten = stoffeVon(liste, 'stahl');
    if (!gibt(arten, v[liste].stahl)) v[liste].stahl = erstes(arten) || '';
  }
  const arten = stoffeVon('flaechen', 'material');
  if (v.flaechen.material && !gibt(arten, v.flaechen.material)) {
    v.flaechen.material = erstes(arten) || v.flaechen.material;
  }
  vorgabePruefen(v.spannglieder);
  return v;
}

/**
 * Was der Adapter einer Analyse über die gemeinsame Grundlage hinaus weiss
 * (cad_app.js). Den Kern fragt er nach der Zeichnung (Anfrage `geometrie`);
 * aus der Antwort behält er die Namen der Elemente, und ein offenes Fenster
 * baut sich neu -- es zeigt vielleicht, was erst jetzt feststeht, die
 * Materialien einer Rechenwahl (`werkstoffeVon`) oder warum sie fehlen.
 * Gleich welches Fenster: auch der Querschnitt eines Balkensystems wählt
 * die Werte je Material der Analyse, aus der er kommt.
 */
function adapter(kennung) {
  const qa = { kennung, vorgaben: vorgabenNeu(), namen: new Map() };
  return {
    qa,
    einstellung: { werkzeuge: WERKZEUGE },
    achsen: ['y', 'z'],
    arten: ARTEN,
    name: elementname,
    neuText: (a, werkzeug) => neuText(a.qa, werkzeug),
    punktAnlegen,
    linieAnlegen,
    flaecheAnlegen,
    zeichnen,
    punktVorschau,
    linienVorschau,
    // Der Schwerpunkt und die Ecken der Überdeckung (Benutzer, 2026-10-23),
    // dazu der Rahmen jedes Profils: so legt sich eine Platte auf den Flansch.
    fangpunkte: (a) => {
      const g = frischeAntwort(a);
      return [
        ...(g?.brutto ? [{ p: [g.brutto.y_S, g.brutto.z_S] }] : []),
        ...(g?.polygone || []).flatMap((x) => (x.ueberdeckung || []).map((p) => ({ p }))),
        ...profilFang(a, eintragVon(kennung)),
      ];
    },
    trefferradius: (a, art, e) => {
      if (art.liste === 'staebe' || art.liste === 'stablinien') return (e.durchmesser || 0) / 2;
      if (art.liste === 'spannglieder') return gliedDurchmesser(a, e) / 2;
      return 0;
    },
    punktUmriss: (a, art, e) => (art === PROFIL ? profilUmriss(a, e) : null),
    umriss: (a) => umriss(a, eintragVon(kennung)),
    // Die Masse eines Profils kennt nur der Kern: bis zu seiner Antwort fehlt es im Umriss.
    umrissVollstaendig: (a) => (eintragVon(kennung)?.profile || []).every((e) => profilUmriss(a, e)),
    fragen: () => api.geometrie(zustand.projekt, kennung),
    nehmen: (a, antwort) => {
      a.qa.namen = new Map([antwort.polygone, antwort.profile, antwort.staebe, antwort.spannglieder,
        antwort.linien, antwort.waende, antwort.hilfslinien].flatMap((liste) => (liste || []).map((x) => [x.kennung, x.element])));
      // Aus Holz oder Stahl statt Beton: die Analyse zeigt andere Kacheln
      // (`bauweiseVon`, `ohneNachweiseVon`, `ohneAnalysenVon`) -- und der
      // Kachel «Knicken und Kippen» fehlt eine Kurve oder nicht mehr.
      const vorher = a.adapter.kern.antwort;
      a.qa.andereKacheln = ['bauweise', 'ohne_nachweise', 'ohne_analysen', 'knickkurven_fehlen']
        .some((s) => antwort[s] !== (vorher?.[s] ?? ''));
      return antwort;
    },
    beantwortet: (a) => { if (zustand.fenster || a.qa.andereKacheln) mitteAendern(); },
    eigenschaften,
    neuEigenschaften,
    aktionen,
    // Woraus die Vorlage ist und wie ihre Flächen aussehen, sagt die Zeichnung.
    vorlageOeffnen: (a) => vorlageOeffnen(a, vorgaben(a), flaechenklasse),
  };
}

/** Der Name eines Elements, wie er im Bericht steht -- vom Kern. Knoten heissen nach ihrer Kennung. */
export function elementname(a, kennung) {
  if (!kennung) return '';
  return knotenname(kennung) ?? (a.qa.namen.get(kennung) || kennung);
}

export function stoffname(kennung) {
  const m = eintragVon(kennung);
  return m ? (m.name || m.sorte) : '–';
}

/** Was das Werkzeug als Nächstes anlegt, in Worten -- für die Frage im schwebenden Fenster. */
function neuText(qa, werkzeug) {
  const v = qa.vorgaben;
  if (werkzeug === 'polygon') {
    return v.flaechen.material ? `Fläche ${stoffname(v.flaechen.material)}` : 'Aussparung';
  }
  if (werkzeug === 'bewehrung') {
    return v.bewehrung === 'punkt' ? `Stab ⌀${zahlText(v.staebe.durchmesser)}` : 'Linienbewehrung';
  }
  if (werkzeug === 'spannstahl') return `Spannglied ${gliedText(v.spannglieder)}`;
  return WERKZEUGE.find((w) => w.name === werkzeug)?.text || '';
}

// ===========================================================================
// Anlegen -- nach den Vorgaben im schwebenden Fenster
// ===========================================================================

/** Ein Stab der Bewehrung oder ein Spannglied -- ein Hilfspunkt ist der Knoten selbst und legt nichts an. */
function punktAnlegen(a, z, knoten, werkzeug) {
  const liste = { bewehrung: 'staebe', spannstahl: 'spannglieder' }[werkzeug];
  if (!liste) return null;
  const art = ARTEN.find((x) => x.liste === liste);
  const kennung = a.modell.naechsteKennung(z, art.vorsilbe);
  z[art.liste].push({ ...structuredClone(vorgaben(a)[art.liste]), kennung, knoten });
  return kennung;
}

function linieAnlegen(a, z, von, bis, werkzeug) {
  const liste = LINIE_VON[werkzeug];
  const kennung = a.modell.naechsteKennung(z, 'L');
  z[liste].push({ ...structuredClone(vorgaben(a)[liste]), kennung, von, bis });
  return kennung;
}

function flaecheAnlegen(a, z, knoten) {
  const kennung = a.modell.naechsteKennung(z, 'F');
  z.flaechen.push({ ...structuredClone(vorgaben(a).flaechen), kennung, knoten });
  return kennung;
}

/** Was im Bild sein soll: alle Knoten und Profile -- sonst ein Meter im Quadrat. */
function umriss(a, analyse) {
  return umrissVon([...(analyse?.knoten || []).map((k) => [k.y, k.z]),
    ...(analyse?.profile || []).flatMap((e) => profilUmriss(a, e)?.[0] || [])], [[0, 0], [1000, 1000]]);
}

// ===========================================================================
// Zeichnen
// ===========================================================================

/**
 * Wie gross ein Spannglied sich zeichnet -- ein Kreis mit seiner Fläche, vom
 * Kern; solange er sie nicht kennt, sein Nenndurchmesser. Auch eine ältere
 * Antwort taugt dafür: es ist nur das Bild.
 */
function gliedDurchmesser(a, e) {
  return a.adapter.kern.antwort?.spannglieder?.find((x) => x.kennung === e.kennung)?.durchmesser ?? e.durchmesser;
}

/** Ein Stab: ein Kreis in seinem Durchmesser, aber nie kleiner als ein Punkt. */
function stabKreis(a, p, durchmesser, klasse) {
  const [x, y] = nachBild(a.v, p);
  return svgEl('circle', {
    cx: x.toFixed(1), cy: y.toFixed(1),
    r: Math.max(2.4, (a.v.massstab * durchmesser) / 2).toFixed(1), class: klasse,
  });
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

/**
 * Was an einer Stablinie steht -- aus der Antwort des Kerns, also mit der
 * tatsächlichen Teilung: «3 ⌀16 @ 142.9 (gewählt 150)».
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

/**
 * Rot, was der Kern beanstandet, mit seinen Sätzen als Titel; was nur noch
 * fehlt -- ein Material, das zu wählen ist --, färbt nicht: die Meldung
 * steht grau unter der Zeichnung, wie im Balkensystem.
 */
function zeichnen(a, g) {
  const z = eintragVon(a.qa.kennung);
  const geo = frischeAntwort(a);
  const roh = a.adapter.kern.antwort;
  const { fehler, texte } = meldungenJe(a);
  const lagen = a.modell.lagen(z);
  const ort = (k) => lagen.get(k);
  const klassen = (kennung, ...weitere) => [...weitere, fehler(kennung) ? 'ist-fehler' : ''].join(' ');

  const schraffur = svgEl('pattern', {
    id: `qa-schraffur-${a.qa.kennung}`, patternUnits: 'userSpaceOnUse',
    width: 7, height: 7, patternTransform: 'rotate(45)',
  });
  schraffur.append(svgEl('line', { x1: 0, y1: 0, x2: 0, y2: 7, class: 'cad-schraffurstrich' }));
  const defs = svgEl('defs');
  defs.append(schraffur);
  g.append(defs);

  // Flächen und Profile: die äusseren zuerst, damit die inneren darüber
  // liegen. Wie tief jedes liegt, sagt der Kern -- auch eine ältere Antwort;
  // was er noch nicht kennt, liegt zuunterst. Ein Profil ist aus Baustahl,
  // sein Loch ausgespart; einen Namen, den die Tabelle nicht kennt, zeigt
  // ein roter Punkt an seiner Mitte.
  const tiefe = new Map([...(roh?.polygone || []), ...(roh?.profile || [])].map((x) => [x.kennung, x.tiefe]));
  const flaechen = [
    ...z.flaechen.map((f) => {
      const punkte = f.knoten.map(ort);
      const gibt = punkte.length >= 2 && punkte.every(Boolean);
      return gibt && { kennung: f.kennung, d: pfad(a.v, punkte), klasse: flaechenklasse(f.material) };
    }),
    ...z.profile.map((e) => {
      const d = profilPfad(a, e);
      return d && { kennung: e.kennung, d, klasse: 'cad-baustahl', 'fill-rule': 'evenodd' };
    }),
  ].filter(Boolean).sort((p, q) => (tiefe.get(p.kennung) ?? 0) - (tiefe.get(q.kennung) ?? 0));
  for (const { kennung, klasse, ...pfadwerte } of flaechen) {
    g.append(mitTitel(svgEl('path', { ...pfadwerte, class: klassen(kennung, klasse) }), texte(kennung)));
  }

  // Die Überdeckung: das gerückte Polygon, gepunktet -- eine Hilfe zum
  // Zeichnen, sie rechnet nicht mit.
  for (const p of geo?.polygone || []) {
    if (p.ueberdeckung) g.append(svgEl('path', { d: pfad(a.v, p.ueberdeckung), class: 'cad-ueberdeckung' }));
  }

  for (const zelle of geo?.zellen || []) {
    g.append(svgEl('path', {
      d: pfad(a.v, zelle.punkte), class: 'cad-zelle', fill: `url(#qa-schraffur-${a.qa.kennung})`,
    }));
  }

  for (const w of z.schubwaende) {
    const [p, q] = [ort(w.von), ort(w.bis)];
    if (!p || !q) continue;
    const ecken = band(p, q, Math.max(w.dicke, 0));
    if (ecken) {
      g.append(mitTitel(svgEl('path', { d: pfad(a.v, ecken), class: klassen(w.kennung, 'cad-wand') }),
        texte(w.kennung)));
    }
    g.append(svgEl('path', { d: pfad(a.v, [p, q], false), class: klassen(w.kennung, 'cad-wandachse') }));
  }

  for (const h of z.hilfslinien || []) {
    const [p, q] = [ort(h.von), ort(h.bis)];
    if (p && q) g.append(svgEl('path', { d: pfad(a.v, [p, q], false), class: 'cad-hilfslinie' }));
  }

  const linieninfo = new Map((geo?.linien || []).map((x) => [x.kennung, x]));
  for (const l of z.stablinien) {
    const [p, q] = [ort(l.von), ort(l.bis)];
    if (!p || !q) continue;
    const flaechig = l.art === 'flaeche';
    g.append(mitTitel(svgEl('path', {
      d: pfad(a.v, [p, q], false),
      class: klassen(l.kennung, flaechig ? 'cad-linie-flaeche' : 'cad-linie'),
    }), texte(l.kennung)));
    const info = linieninfo.get(l.kennung);
    if (!info) continue;
    if (!flaechig) for (const s of info.punkte) g.append(stabKreis(a, s, l.durchmesser, klassen(l.kennung, 'cad-stab')));
    const beschriftung = linienText(l, info);
    if (beschriftung) {
      const [x0, y0] = nachBild(a.v, p);
      const [x1, y1] = nachBild(a.v, q);
      const lang = Math.hypot(x1 - x0, y1 - y0) || 1;
      // Links der Laufrichtung, also bei einer Linie nach rechts oberhalb.
      const [nx, ny] = [(y1 - y0) / lang, -(x1 - x0) / lang];
      const versatz = 9 + (flaechig ? 3 : Math.max(2.4, (a.v.massstab * l.durchmesser) / 2));
      g.append(text((x0 + x1) / 2 + nx * versatz, (y0 + y1) / 2 + ny * versatz + 4,
        beschriftung, klassen(l.kennung, 'cad-beschriftung cad-linientext')));
    }
  }

  for (const s of z.staebe) {
    const p = ort(s.knoten);
    if (p) g.append(mitTitel(stabKreis(a, p, s.durchmesser, klassen(s.kennung, 'cad-stab')), texte(s.kennung)));
  }
  for (const s of z.spannglieder) {
    const p = ort(s.knoten);
    if (p) {
      g.append(mitTitel(stabKreis(a, p, gliedDurchmesser(a, s), klassen(s.kennung, 'cad-spannglied')),
        texte(s.kennung)));
    }
  }
  for (const e of z.profile) {
    const p = ort(e.knoten);
    if (p && !profilUmriss(a, e)) {
      g.append(mitTitel(stabKreis(a, p, 0, klassen(e.kennung, 'cad-baustahl')), texte(e.kennung)));
    }
  }

  const masse = masseZeichnen(a, z, ort);
  if (masse) g.append(masse);
  if (geo?.brutto) {
    const [x, y] = nachBild(a.v, [geo.brutto.y_S, geo.brutto.z_S]);
    const s = svgEl('g', { class: 'cad-schwerpunkt' });
    s.append(
      svgEl('circle', { cx: x, cy: y, r: 6 }),
      svgEl('path', { d: `M${x - 9} ${y} H${x + 9} M${x} ${y - 9} V${y + 9}` }),
      text(x + 9, y - 7, 'S', 'cad-schwerpunkttext', 'start'),
    );
    g.append(s);
  }
}

/** Breite und Höhe dessen, was Material hat -- auch der Profile --: eine Masslinie unten, eine links. */
function masseZeichnen(a, z, ort) {
  const punkte = [...z.flaechen.filter((f) => f.material).flatMap((f) => f.knoten.map(ort)),
    ...z.profile.flatMap((e) => profilUmriss(a, e)?.[0] || [])].filter(Boolean);
  if (punkte.length < 2) return null;
  const ys = punkte.map((p) => p[0]);
  const zs = punkte.map((p) => p[1]);
  const [y0, y1, z0, z1] = [Math.min(...ys), Math.max(...ys), Math.min(...zs), Math.max(...zs)];
  const [xl, hu] = nachBild(a.v, [y0, z0]);
  const [xr, ho] = nachBild(a.v, [y1, z1]);
  const g = svgEl('g');
  const unten = Math.min(hu + 22, a.v.hoehe - 8);
  const links = Math.max(xl - 22, 8);
  if (xr - xl > 30) {
    g.append(
      svgEl('path', {
        d: `M${xl} ${unten} H${xr} M${xl} ${unten - 5} V${unten + 5} M${xr} ${unten - 5} V${unten + 5}`,
        class: 'cad-mass',
      }),
      text((xl + xr) / 2, unten - 4, zahlText(y1 - y0), 'cad-masstext'),
    );
  }
  if (hu - ho > 30) {
    const t = text(links - 4, (hu + ho) / 2, zahlText(z1 - z0), 'cad-masstext');
    t.setAttribute('transform', `rotate(-90 ${(links - 4).toFixed(1)} ${((hu + ho) / 2).toFixed(1)})`);
    g.append(svgEl('path', {
      d: `M${links} ${ho} V${hu} M${links - 5} ${ho} H${links + 5} M${links - 5} ${hu} H${links + 5}`,
      class: 'cad-mass',
    }), t);
  }
  return g;
}

function punktVorschau(a, g, p, werkzeug) {
  if (werkzeug === 'bewehrung') g.append(stabKreis(a, p, a.qa.vorgaben.staebe.durchmesser, 'cad-stab cad-geist'));
  if (werkzeug === 'spannstahl') {
    g.append(stabKreis(a, p, a.qa.vorgaben.spannglieder.durchmesser, 'cad-spannglied cad-geist'));
  }
}

function linienVorschau(a, g, p, q, werkzeug) {
  if (werkzeug !== 'schubwand') return;
  const ecken = band(p, q, a.qa.vorgaben.schubwaende.dicke);
  if (ecken) g.append(svgEl('path', { d: pfad(a.v, ecken), class: 'cad-wand cad-geist' }));
}

// ===========================================================================
// Felder im schwebenden Fenster
// ===========================================================================

/**
 * Die Felder einer Elementart -- für die Vorgabe eines Werkzeugs wie für
 * gewählte Elemente: `wert(feld)` ist der Wert, bei mehreren der gemeinsame
 * oder VAR; `setzen(feld)(w)` schreibt -- beim gewählten Element ins
 * Projekt, bei der Vorgabe in die Ansicht (`zugleich` und `vorgabe` in
 * cad_app.js). `info` ist, was der Kern zu einer gewählten Linie weiss: ihre
 * Stahlfläche steht grau unter den Stäben, aus denen sie kommt -- gerechnet
 * wird sie dort, nicht hier; ebenso zu einem Spannglied. Die Grenzen jeder
 * Zahl kommen aus dem Kern.
 */
function felderVon(liste, wert, setzen, info = null) {
  if (liste === 'spannglieder') return gliedFelder(wert, setzen, info);
  if (liste === 'profile') return profilFelder(wert, setzen, info);
  const durchmesser = katalog('durchmesser');
  const zahl = (feld, titel, optionen = {}) => zahlfeldMitVar({
    wert: wert(feld), titel, schritt: 1, angabe: feldangabe(klasseVon(liste), feld), ...optionen,
    beiAenderung: setzen(feld),
  });
  const stahl = () => cadZeile('Stahl', materialliste({
    art: stoffeVon(liste, 'stahl'), gewaehlt: wert('stahl'), setzen: setzen('stahl'),
  }));
  // Dahinter ein Bild, was die Wahl meint -- etwa der Stab am Anfang der Linie.
  const haken = (beschriftung, feld, bild = null, bildtitel = '') => el('div.cad-zeile', {}, [
    el('span', { text: beschriftung }),
    wert(feld) === VAR ? jaNein(VAR, setzen(feld), beschriftung)
      : hakenSchalter(wert(feld) !== false, setzen(feld), beschriftung),
    bild ? el('span.zeilenbild', { title: bildtitel }, [bild]) : el('span'),
  ]);
  // Verschiedene Arten zugleich gewählt: ihre Felder unterscheiden sich.
  const erstWaehlen = el('p.cad-hinweis-klein', {
    text: 'Die gewählten unterscheiden sich in der Art – erst eine wählen, dann gelten ihre Felder für alle.',
  });
  if (liste === 'staebe') {
    return [cadZeile('⌀', zahl('durchmesser', 'Stabdurchmesser', { stufen: durchmesser }), 'mm'), stahl()];
  }
  if (liste === 'stablinien') {
    const arten = katalog('querschnittsanalyse', 'linienarten');
    const verschmierungen = katalog('querschnittsanalyse', 'verschmierungen');
    const art = wert('art');
    const verschmiert = wert('verschmiert');
    // Verschmiert: die Fläche von Hand -- oder aus ⌀, s und L (Benutzer, 2026-10-24).
    const ausStaeben = art === 'flaeche' && verschmiert === 'staebe';
    const erklaert = {
      flaeche: 'Eine Stahlfläche, über die Linie verschmiert',
      anzahl: 'n Stäbe, gleich verteilt',
      teilung: 'Stäbe im Abstand s – gerundet auf einen, der aufgeht',
    };
    const artWahl = wahlSchalter({
      werte: mitVar(mitBild(arten.map((x) => ({
        wert: x.wert, beschriftung: x.beschriftung, titel: erklaert[x.wert],
      })), 'linie'), art),
      gewaehlt: art, setzen: setzen('art'),
      titel: 'Wie die Stäbe auf der Linie verteilt sind', klasse: '.cad-wahl.ist-gross',
    });
    if (art === VAR) return [artWahl, erstWaehlen, stahl()];
    const verschmierung = art === 'flaeche' ? wahlSchalter({
      werte: mitVar(verschmierungen.map((x) => ({ wert: x.wert, beschriftung: x.beschriftung, titel: x.titel })),
        verschmiert),
      gewaehlt: verschmiert, setzen: setzen('verschmiert'),
      titel: 'Wie die Stahlfläche angegeben ist', klasse: '.cad-wahl',
    }) : null;
    if (verschmiert === VAR && art === 'flaeche') return [artWahl, verschmierung, erstWaehlen, stahl()];
    return [
      artWahl,
      verschmierung,
      art === 'flaeche' && !ausStaeben ? cadZeile('A_s', zahl('flaeche', 'Stahlfläche der ganzen Linie', { schritt: 100 }), 'mm²') : null,
      art === 'anzahl' ? cadZeile('n', zahl('anzahl', 'Anzahl Stäbe')) : null,
      art === 'teilung' ? cadZeile('s', zahl('teilung', 'Gewünschte Teilung', { schritt: 25 }), 'mm') : null,
      art !== 'flaeche' || ausStaeben ? cadZeile('⌀', zahl('durchmesser', 'Stabdurchmesser', { stufen: durchmesser }), 'mm') : null,
      ausStaeben ? cadZeile('s', zahl('teilung', 'Abstand der Stäbe', { schritt: 25 }), 'mm') : null,
      ausStaeben ? cadZeile('L', zahl('laenge', 'Länge, über die die Stäbe liegen – leer: die der Linie', {
        schritt: 100, leer: null, platzhalter: 'Linie',
      }), 'mm') : null,
      ausStaeben ? cadZeile('A_s', zahlfeld({
        wert: info?.punkte ? Math.round(info.flaeche) : null, readonly: true,
        titel: 'Die verschmierte Stahlfläche L/s · π⌀²/4 – vom Kern gerechnet',
      }), 'mm²') : null,
      art !== 'flaeche' ? haken('Starteisen', 'starteisen', sinnbild('linie-starteisen'),
        'Ein Stab genau am Anfang der Linie – aus: der Anfang bleibt frei') : null,
      art !== 'flaeche' ? haken('Endeisen', 'endeisen', sinnbild('linie-endeisen'),
        'Ein Stab genau am Ende der Linie – aus: das Ende bleibt frei') : null,
      stahl(),
    ];
  }
  if (liste === 'schubwaende') {
    const schnitte = katalog('querschnittsanalyse', 'schnitte');
    return [
      cadZeile('b_w', zahl('dicke', 'Dicke der Schubwand', { schritt: 10 }), 'mm'),
      cadZeile('Bügel ⌀', zahl('durchmesser', 'Bügeldurchmesser; 0: ohne Bügel', { stufen: durchmesser }), 'mm'),
      cadZeile('s', zahl('teilung', 'Bügelteilung in Längsrichtung', { schritt: 25 }), 'mm'),
      cadZeile('Schnitte', zahl('schnitte', 'Wie viele Bügelschenkel die Wand kreuzen', {
        min: schnitte[0], max: schnitte.at(-1),
      })),
      stahl(),
    ];
  }
  if (liste === 'flaechen') {
    return [
      cadZeile('Material', materialliste({
        art: stoffeVon('flaechen', 'material'), gewaehlt: wert('material'), setzen: setzen('material'),
        zusatz: [{ wert: '', beschriftung: 'Aussparung' }],
      })),
      cadZeile('c', zahl('ueberdeckung', 'Überdeckung c: das Polygon erscheint so weit nach innen gerückt '
        + '– eine Aussparung nach aussen –, mit Ecken zum Fangen. 0: nicht. Rechnet nicht mit.', {
        schritt: 5,
      }), 'mm'),
    ];
  }
  return [];
}

/**
 * Der Schalter der Bewehrung: eine Linie mit Stäben oder einzelne Stäbe --
 * ein Werkzeug, zwei Formen. Umgestellt startet das Werkzeug neu, mit dem
 * Befehl der anderen Form.
 */
function formWahl(a) {
  const v = a.qa.vorgaben;
  return wahlSchalter({
    werte: [
      { wert: 'linie', beschriftung: 'Linie', zeichen: 'cad-linienbewehrung',
        titel: 'Linienbewehrung: Stäbe auf einer Linie, nach Anzahl, Teilung oder verschmiert' },
      { wert: 'punkt', beschriftung: 'Punkt', zeichen: 'cad-punktbewehrung',
        titel: 'Punktbewehrung: ein Stab je Klick' },
    ],
    gewaehlt: v.bewehrung, titel: 'Wie die Bewehrung gezeichnet wird', klasse: '.cad-wahl',
    setzen: (w) => { v.bewehrung = w; a.werkzeugStarten('bewehrung'); },
  });
}

/** Die Vorgaben für das, was ein Werkzeug als Nächstes anlegt -- nur die seiner Art. */
function neuEigenschaften(a, werkzeug) {
  const v = vorgaben(a);
  const felder = (liste) => {
    const { wert, setzen } = vorgabe(a, v[liste]);
    return felderVon(liste, wert, setzen);
  };
  const hinweis = (text) => el('p.cad-hinweis-klein', { text });
  const inhalt = {
    polygon: () => felder('flaechen'),
    bewehrung: () => [formWahl(a), ...felder(v.bewehrung === 'punkt' ? 'staebe' : 'stablinien')],
    spannstahl: () => felder('spannglieder'),
    schubwand: () => felder('schubwaende'),
    hilfspunkt: () => [hinweis('Ein Knoten ohne Element: daran fängt der Zeiger.')],
    hilfslinie: () => [hinweis('Rechnet nicht mit. Gewählt und geschlossen, werden '
      + 'Hilfslinien zu einer Fläche.')],
  }[werkzeug]?.() || [];
  return { inhalt: inhalt.filter(Boolean), schluessel: JSON.stringify([werkzeug, v]) };
}

/** Was gewählt ist (cad_app.js): Ecken und Knoten mit ihrer Lage, sonst Elemente einer Art. */
function eigenschaften(a) {
  return auswahlEigenschaften(a, { sonst: elementEigenschaften });
}

/**
 * Gewählte Elemente einer Art: ihre Felder, bei mehreren je Feld der
 * gemeinsame Wert oder «Var», wie im Balkensystem und in der Decke -- bis
 * 2026-11-19 standen die Werte des ersten da, und ein getippter Wert galt
 * unsichtbar für alle. Ein einzelnes sagt dazu, was der Kern von ihm weiss.
 */
function elementEigenschaften(a, z, kennungen, liste) {
  const { gewaehlt, wert, setzen } = zugleich(a, z, liste, kennungen);
  // Ein Profil hängt mit seiner Mitte an einem Knoten: ihre Lage steht bei ihm.
  const mitte = liste === 'profile' ? lagefelder(a, z, kennungen, 'Mitte ') : [];
  if (gewaehlt.length > 1) {
    return {
      titel: `${gewaehlt.length} × ${artText(liste, wert('material'))}`,
      inhalt: [...felderVon(liste, wert, setzen), ...mitte].filter(Boolean),
    };
  }
  const [e] = gewaehlt;
  const geo = frischeAntwort(a);
  const info = [...(geo?.linien || []), ...(geo?.spannglieder || []), ...(geo?.profile || [])]
    .find((x) => x.kennung === e.kennung);
  return {
    titel: `${elementname(a, e.kennung)} · ${artText(liste, e.material, e)}`,
    inhalt: [...felderVon(liste, wert, setzen, info), ...mitte, ...infozeilen(a, z, liste, e)].filter(Boolean),
  };
}

/** Was ein Element ist, für den Titel des Fensters -- ein einzelnes Spannglied mit seinem Erzeugnis. */
function artText(liste, material, e = null) {
  return {
    staebe: 'Punktbewehrung', stablinien: 'Linienbewehrung', schubwaende: 'Schubwand', hilfslinien: 'Hilfslinie',
    spannglieder: e ? gliedText(e) : 'Spannglied',
    profile: e ? e.profil : 'Stahlprofil',
    flaechen: material === VAR ? 'Flächen' : (material ? stoffname(material) : 'Aussparung'),
  }[liste];
}

/**
 * Was der Kern zum Element sagt -- tatsächliche Teilung, A_sw/s, Meldungen
 * --, dazu seine Länge. Bleibt von einem Polygon nach der Überdeckung nichts
 * übrig, sagt es das Fenster selbst, rot.
 */
function infozeilen(a, z, liste, e) {
  const geo = frischeAntwort(a);
  const zeilen = [];
  if (liste === 'stablinien') {
    const info = geo?.linien?.find((x) => x.kennung === e.kennung);
    if (info?.punkte) zeilen.push(`${linienText(e, info)} · A_s ${zahlText(info.flaeche, 0)} mm²`);
  }
  if (liste === 'schubwaende') {
    const info = geo?.waende?.find((x) => x.kennung === e.kennung);
    if (info) zeilen.push(`A_sw/s = ${zahlText(info.a_sw_s, 0)} mm²/m`);
  }
  if (liste === 'flaechen') zeilen.push(`${e.knoten.length} Ecken`);
  const polygon = liste === 'flaechen' && geo?.polygone?.find((x) => x.kennung === e.kennung);
  return [
    LINIENLISTEN.includes(liste) ? laengenzeile(a, z, e) : null,
    ...zeilen.map((t) => el('p.cad-info', { text: t })),
    ...(liste === 'spannglieder' ? gliedInfo(e, geo?.spannglieder?.find((x) => x.kennung === e.kennung)) : []),
    ...(liste === 'profile' ? profilInfo(geo?.profile?.find((x) => x.kennung === e.kennung)) : []),
    ...meldungszeilen(a, [e.kennung]),
    e.ueberdeckung > 0 && polygon && !polygon.ueberdeckung
      ? el('p.cad-meldung', { text: 'Die Überdeckung ist zu gross: vom Polygon bleibt nichts übrig.' }) : null,
  ];
}

// ===========================================================================
// Was neben der Auswahl angeboten wird
// ===========================================================================

/**
 * Die gewählten Hilfslinien als ein geschlossener Umriss -- seine Knoten der
 * Reihe nach, oder null. Jede Ecke hat genau zwei Linien, und alle hängen
 * zusammen.
 */
function umlauf(z, kennungen) {
  const linien = (z.hilfslinien || []).filter((h) => kennungen.has(h.kennung));
  if (linien.length < 3 || linien.length !== kennungen.size) return null;
  const nachbarn = new Map();
  for (const h of linien) {
    if (h.von === h.bis) return null;
    nachbarn.set(h.von, [...(nachbarn.get(h.von) || []), h.bis]);
    nachbarn.set(h.bis, [...(nachbarn.get(h.bis) || []), h.von]);
  }
  if ([...nachbarn.values()].some((n) => n.length !== 2)) return null;
  const start = linien[0].von;
  const reihe = [start];
  let vorher = null;
  let jetzt = start;
  for (;;) {
    const weiter = nachbarn.get(jetzt).find((k) => k !== vorher);
    if (weiter === start) break;
    if (reihe.includes(weiter)) return null;
    reihe.push(weiter);
    vorher = jetzt;
    jetzt = weiter;
  }
  return reihe.length === nachbarn.size ? reihe : null;
}

/**
 * Schiebt die gewählte Bewehrung in die Überdeckung -- dorthin, wo der Kern
 * sagt (`ueberdeckt` in seiner Antwort zur Zeichnung). Ein Stab als Ganzes,
 * eine Linie Ende für Ende; was sonst am selben Knoten hängt, bleibt liegen.
 * Ein Schritt für «Rückgängig».
 */
function ueberdeckungBeachten(a, bewehrung) {
  const geo = frischeAntwort(a);
  if (!geo) {
    melden('Die Zeichnung wird noch geprüft – gleich noch einmal.');
    return;
  }
  const ziele = new Map([...geo.staebe, ...geo.spannglieder, ...geo.linien].map((x) => [x.kennung, x.ueberdeckt]));
  const lagen = a.modell.lagen(eintragVon(a.qa.kennung));
  const schritte = [];
  for (const { art, e } of bewehrung) {
    const ziel = ziele.get(e.kennung);
    if (!ziel) continue;
    const enden = art.form === 'punkt' ? [[e.kennung, e.knoten, ziel]]
      : [[eckeSchluessel(e.kennung, 0), e.von, ziel[0]], [eckeSchluessel(e.kennung, 1), e.bis, ziel[1]]];
    for (const [schluessel, knoten, p] of enden) {
      const q = lagen.get(knoten);
      const d = [p[0] - q[0], p[1] - q[1]];
      if (Math.hypot(d[0], d[1]) > 1e-6) schritte.push([schluessel, d]);
    }
  }
  if (!schritte.length) {
    melden(bewehrung.some(({ e }) => ziele.get(e.kennung))
      ? 'Die Bewehrung liegt schon in der Überdeckung.'
      : 'Für diese Bewehrung gilt keine Überdeckung, oder das Polygon ist dafür zu klein.');
    return;
  }
  a.aendern((zz) => {
    for (const [schluessel, d] of schritte) a.modell.verschieben(zz, new Set([schluessel]), d);
  });
}

function aktionen(a) {
  const z = eintragVon(a.qa.kennung);
  const liste = [];
  // Bewehrung gewählt, und ein Polygon hat eine Überdeckung: sie beachten.
  const verzeichnis = a.modell.verzeichnis(z);
  const bewehrung = [...a.auswahl].map((k) => verzeichnis.get(k))
    .filter((x) => x && ['staebe', 'spannglieder', 'stablinien'].includes(x.art?.liste));
  if (bewehrung.length && z.flaechen.some((f) => f.ueberdeckung > 0)) {
    liste.push({
      zeichen: '⇲', text: 'Überdeckung beachten',
      titel: 'Die Bewehrung so verschieben, dass sie mit ihrem Radius gerade ganz in der Überdeckung liegt',
      tun: () => ueberdeckungBeachten(a, bewehrung),
    });
  }
  const reihe = umlauf(z, a.auswahl);
  if (reihe) {
    // Was entsteht, sagt die Vorgabe des Werkzeugs Polygon -- bis 2026-11-19
    // sagte der Knopf es nicht.
    const entsteht = vorgaben(a).flaechen.material ? neuText(a.qa, 'polygon') : 'Aussparung';
    liste.push({
      zeichen: '▱', text: 'Fläche bilden',
      titel: `Die geschlossenen Hilfslinien werden eine ${entsteht} – wie die Vorgabe des Werkzeugs Polygon`,
      tun: () => {
        const weg = new Set(a.auswahl);
        let neu = null;
        a.aendern((zz) => {
          neu = flaecheAnlegen(a, zz, reihe);
          zz.hilfslinien = zz.hilfslinien.filter((h) => !weg.has(h.kennung));
        }, { auswahl: () => [neu] });
      },
    });
  }
  return liste;
}

