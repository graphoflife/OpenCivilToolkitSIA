/**
 * qa_vorlagen.js -- die Werkzeuge, die etwas Fertiges an einem Punkt
 * einsetzen: «Vorlage» (Rechteck, T-Balken, Doppel-T, Trapez, Hohlkasten,
 * Platte mit Aufbeton, Kreis), «Stahlprofil» und «Blechverbunddecke».
 *
 * Jedes hat seinen eigenen Knopf (Benutzer, 2026-11-27). Seine Felder
 * stehen in der Seitenleiste, über ihnen eine Skizze mit Masslinien, die
 * sich ändert, während man tippt. Ein Klick in die Zeichnung setzt ein, mit
 * allem, was die Punkteingabe kann; Enter ohne Zahlen heisst Ursprung. Was
 * schon gezeichnet ist, bleibt, und das Eingesetzte ist danach gewählt.
 * Bis 2026-11-27 öffnete T ein Fenster «Vorlage» in der Zeichnung, Profil
 * und Decke standen dort unter den Vorlagen, und eingesetzt wurde mit dem
 * Knopf «Einsetzen».
 *
 * Die Vorlagen stehen im Kern (`opencivil/querschnitt/vorlagen.py`), und nur
 * dort. Hier wird gewählt und gezeigt: die Skizze kommt aus der Anfrage
 * `vorlage`, eingesetzt wird mit dem Baukasten des Kerns über
 * `vorlage_einsetzen`.
 *
 * Die Bewehrung je Lage mit Durchmesser und Teilung, die Bügel ebenso, und
 * die Überdeckung c_nom bis zum äussersten Stab (Benutzer, 2026-11-27).
 * Unter jeder Lage steht, was aus ihr wird -- «→ 3 Stäbe, Abstand 95 mm»,
 * vom Kern mit der Skizze geschickt. Ist «Bewehrung» aus, sind ihre Felder
 * grau und gesperrt, ebenso die der Bügel ohne Schubwände; bis dahin blieben
 * sie offen, ohne etwas zu bewirken.
 *
 * Das Stahlprofil setzt ein Profil ein, keine Fläche (Plan vom 2026-11-25):
 * Reihe, Grösse, Baustahl, Drehung und ob gespiegelt, wie in der
 * Seitenleiste eines gezeichneten (qa_profile.js). Seine Mitte kommt an den
 * Punkt -- bei den anderen die Ecke unten links. Ebenso setzt die
 * Blechverbunddecke eine Decke ein, mit ihren Massen und Materialien
 * (qa_blechdecke.js); unter ihrer Skizze steht eine Rippe mit ihren Massen.
 *
 * Die Skizzen zeichnet qa_skizze.js.
 */

import { api } from './api.js';
import { hakenSchalter, materialliste, wahlBlock } from './bausteine.js';
import { pfad } from './cad_ansicht.js';
import { cadZeile, schalterzeile } from './cad_palette.js';
import { el, grenzeVerletzt, melden, svgEl, zahlfeld } from './dom.js';
import { groessenZeilen, reihenSchalter } from './profilwahl.js';
import { BLECHDECKE, MASSE, STOFFE } from './qa_blechdecke.js';
import { PROFIL, drehZeilen } from './qa_profile.js';
import { skizze } from './qa_skizze.js';
import { umrissEinsetzen } from './qa_umriss.js';
import {
  ausVorlage, eintragVon, feldangabe, katalog, materialien, zustand,
} from './zustand.js';

/** Die Vorlagen aus Flächen, wie der Kern sie kennt: Rechteck, T-Balken, … Kreis. */
function vorlagen() {
  return katalog('querschnittsanalyse', 'vorlagen');
}

/** Wie ein Stahlprofil in einer Skizze aussieht: aus Baustahl, ein Stück mit seinem Loch. */
const PROFILBILD = { flaeche: 'cad-baustahl', einStueck: true };

/**
 * Was zuletzt eingestellt war -- je Analyse in der Ansicht, nicht im
 * Projekt. `masse` trägt alle Zahlen, auch Überdeckung, Lagen und Bügel;
 * was fehlt, gilt nach der Vorgabe der Vorlage. `stoffe` sind die zweiten
 * Materialien, etwa der Aufbeton.
 */
function wahlVon(a) {
  a.qa.vorlage = a.qa.vorlage || {
    art: 'rechteck', masse: {}, bewehrung: true, schubwaende: true, stoffe: {},
  };
  return a.qa.vorlage;
}

/** Die gewählte Vorlage aus Flächen -- eine, die es nicht mehr gibt, wird die erste. */
function gewaehlteVorlage(a) {
  const w = wahlVon(a);
  const v = vorlagen().find((x) => x.schluessel === w.art) || vorlagen()[0];
  w.art = v.schluessel;
  return v;
}

// ===========================================================================
// Die Werkzeuge
// ===========================================================================

/**
 * Ein Werkzeug für die Knöpfe des Zeichenfensters (cad_fenster.js) -- mit
 * seinem eigenen Befehl. `hinweis` sagt, was an den Punkt kommt.
 */
function werkzeug(name, text, zeichen, taste, titel, hinweis) {
  return { name, text, zeichen, taste, titel, befehl: () => einsetzBefehl(name, hinweis) };
}

/** Die drei Werkzeuge, unter ihrem Namen. */
export const VORLAGEN = {
  stahlprofil: werkzeug('stahlprofil', 'Stahlprofil', 'cad-stahlprofil', 'i',
    'Stahlprofil: ein Walzprofil der Tabelle aus Baustahl, gedreht und gespiegelt',
    'Die Mitte des Profils kommt an den Punkt'),
  // Mit weichen Trennstrichen: auf dem Knopf bricht der Name in zwei Zeilen.
  blechdecke: werkzeug('blechdecke', 'Blech­verbund­decke', 'cad-blechdecke', 'd',
    'Blechverbunddecke: Beton auf einem Profilblech, die Masse aus dem Datenblatt',
    'Die Ecke links unten – die Unterkante der Rippen – kommt an den Punkt'),
  vorlage: werkzeug('vorlage', 'Vorlage', 'cad-vorlage', 't',
    'Vorlage: ein Querschnitt zum Anfangen, etwa Rechteck, T-Balken oder Kreis – mit Bewehrung je Lage',
    'Die Ecke unten links kommt an den Punkt'),
};

/** Was das Werkzeug einsetzt, in Worten -- für die Frage in der Seitenleiste. */
export function vorlagenText(a, name) {
  if (name === 'stahlprofil') return a.qa.vorlagenprofil?.profil || 'Stahlprofil';
  if (name === 'blechdecke') return 'Blechverbunddecke';
  return gewaehlteVorlage(a).name;
}

/**
 * Der Befehl eines der drei Werkzeuge: ein Punkt, an den kommt, was die
 * Seitenleiste zeigt (`a.qa.vorlagen.art`). Die Vorschau zeigt die Umrisse
 * der Skizze am Zeiger. Hat der Kern zu den Massen keine Skizze -- sie
 * passen nicht zusammen --, setzt ein Klick nichts ein, und die
 * Seitenleiste sagt rot, warum.
 */
function einsetzBefehl(name, hinweis) {
  const hinein = (a, p) => {
    const art = a.qa.vorlagen?.art;
    if (!art || !a.qa.vorlagenteile) return;
    art.hinein(p);
    a.ende();
  };
  return {
    name,
    neu: name,
    frage: (a) => `${vorlagenText(a, name)}: Einsetzpunkt`,
    hinweis: `${hinweis} · Enter ohne Zahlen: Ursprung`,
    // Was die Seitenleiste zeigt, wird mit dem Werkzeug neu gebaut -- und
    // bis der Kern die Skizze dazu schickt, gibt es nichts einzusetzen.
    start(a) {
      a.qa.vorlagen = null;
      a.qa.vorlagenteile = null;
    },
    punkt: (a, erg) => hinein(a, erg.p),
    vorschau(a, g) {
      const teile = a.qa.vorlagenteile;
      const f = a.zeiger?.fang;
      if (!teile || !f) return;
      const hin = (p) => [p[0] + f.p[0], p[1] + f.p[1]];
      for (const p of teile.polygone) {
        g.append(svgEl('path', { d: pfad(a.v, p.punkte.map(hin)), class: 'cad-verschoben' }));
      }
      for (const l of [...teile.stablinien, ...teile.schubwaende]) {
        g.append(svgEl('path', { d: pfad(a.v, [hin(l.von), hin(l.bis)], false), class: 'cad-verschoben' }));
      }
    },
    // Enter ohne Zahlen: am Ursprung. Passen die Masse nicht, bleibt das Werkzeug.
    enter(a) {
      hinein(a, [0, 0]);
      return true;
    },
    zurueck: () => false,
  };
}

// ===========================================================================
// Die Seitenleiste
// ===========================================================================

/**
 * Was die Seitenleiste zu einem der drei Werkzeuge zeigt -- `{inhalt,
 * schluessel}` wie die Vorgaben der anderen Werkzeuge (qa_zeichnung.js).
 * `vorgaben` sind die der Zeichnung, geprüft gegen das Projekt: aus ihrem
 * Material sind die Flächen, aus ihrem Stahl die Bewehrung. Wie eine Fläche
 * aussieht, sagt `flaechenklasse(material)`.
 *
 * Gebaut wird nur, wenn sich mehr als ein Mass geändert hat: die
 * Seitenleiste fragt bei jedem Zeichnen danach, und jeder Bau fragt den Kern
 * nach der Skizze. Ein Mass ändert nur die Skizze (`holen`); eine andere
 * Vorlage oder ein Material baut alles neu (`neu`).
 */
export function vorlagenInhalt(a, name, { vorgaben, flaechenklasse }) {
  const schluessel = JSON.stringify([
    name, a.qa.vorlagenstand || 0, vorgaben.flaechen.material, vorgaben.stablinien.stahl,
  ]);
  if (a.qa.vorlagen?.schluessel === schluessel) return a.qa.vorlagen;
  const neu = () => {
    a.qa.vorlagenstand = (a.qa.vorlagenstand || 0) + 1;
    a.neuZeichnen();
  };
  const bild = el('div.cad-vorlagenskizze');
  const meldung = el('p.cad-meldung', { hidden: true });
  let art = null;

  // Die Skizze kommt vom Kern. Kommt eine Antwort zu spät -- es wurde
  // inzwischen wieder getippt --, gilt sie nicht mehr. Mit ihr ändert sich
  // die Vorschau am Zeiger.
  const holen = () => {
    const nr = (a.qa.vorlagenfrage || 0) + 1;
    a.qa.vorlagenfrage = nr;
    bild.classList.add('ist-alt');
    api.vorlage(art.anfrage()).then((antwort) => {
      if (a.qa.vorlagenfrage !== nr) return;
      meldung.hidden = !antwort.fehler;
      meldung.textContent = antwort.fehler || '';
      a.qa.vorlagenteile = antwort.teile || null;
      if (antwort.teile) {
        bild.classList.remove('ist-alt');
        bild.replaceChildren(skizze(antwort.teile, 276, 140, art.bild));
        art.beantwortet?.(antwort);
      }
      // Ohne Teile auch keine Stabzahlen: nie eine alte stehen lassen.
      art.stabzahlen?.(antwort.teile?.lagen || {});
      a.obenBald();
    }).catch((fehler) => melden(fehler.message, true));
  };

  const eigene = {
    stahlprofil: () => profilvorlage(a, neu, holen),
    blechdecke: () => deckenvorlage(a, neu, holen),
  };
  art = eigene[name]?.() || flaechenvorlage(a, { vorgaben, flaechenklasse, neu, holen });
  a.qa.vorlagen = {
    schluessel,
    art,
    inhalt: [el('div.cad-vorlage', {}, [
      name === 'vorlage' ? vorlagenwahl(a, neu) : null, bild, ...art.zeilen, meldung,
    ].filter(Boolean))],
  };
  holen();
  return a.qa.vorlagen;
}

/** Die Vorlagen aus Flächen als kleine Bilder -- die gewählte hervorgehoben. */
function vorlagenwahl(a, neu) {
  const gewaehlt = gewaehlteVorlage(a).schluessel;
  return el('div.cad-vorlagen', {}, vorlagen().map((x) => el('button.cad-vorlagenknopf', {
    type: 'button', title: x.name, class: x.schluessel === gewaehlt ? 'ist-an' : '',
    on: { click: () => { wahlVon(a).art = x.schluessel; neu(); } },
  }, [skizze(x.skizze, 52, 36, { masse: false }), el('span', { text: x.name })])));
}

/**
 * Mit oder ohne, etwa «Bewehrung» -- ein Schalter wie in den Eigenschaften
 * der Zeichnung, kein Haken (Benutzer, 2026-11-19). Umschalten baut die
 * Seitenleiste neu (`neu`): es sperrt die Felder, die dann nichts bewirken.
 */
function mitOhne(text, an, setzen) {
  return schalterzeile(text, hakenSchalter(an, setzen, text));
}

/**
 * Zeilen, die nur mit einem Schalter etwas bewirken: ist er aus, sind sie
 * grau und gesperrt -- ein `fieldset` sperrt Felder und Pfeile zusammen.
 */
function gesperrt(aus, zeilen) {
  return el('fieldset.cad-sperre', { disabled: aus }, zeilen);
}

/**
 * Das Feld eines Masses: ein Zahlenfeld, das schon beim Tippen meldet --
 * die Skizze soll mitgehen. Grenze, Satz und Einheit kommen mit dem Mass
 * aus dem Kern (`angabe`), wie bei jedem Feld; `mass.titel` ist sein
 * Titel, wo die Zeile nur ein Zeichen zeigt.
 *
 * Beim Tippen geht nur eine Zahl in die Skizze, die das Feld auch nimmt.
 * Nimmt es eine nicht, zeigt es wieder die zuletzt übernommene: die
 * Seitenleiste baut sich beim Tippen nicht neu, und das Feld kennt sonst
 * nur die Zahl, mit der es aufging. Begrenzt ein Mass ein anderes -- die
 * Rippe einer Decke ist niedriger als die Decke --, stehen die Masse in
 * `neben`.
 */
function massFeld(mass, wert, setzen, neben = {}) {
  let gilt = wert;
  const nehmen = (x) => {
    gilt = x;
    setzen(x);
  };
  const feld = zahlfeld({
    wert, schritt: mass.schritt, angabe: mass.angabe, titel: mass.titel, neben, beiAenderung: nehmen,
  });
  const eingabe = feld.querySelector('input');
  eingabe?.addEventListener('input', (e) => {
    const w = Number(e.target.value);
    if (e.target.value.trim() !== '' && Number.isFinite(w) && !grenzeVerletzt(mass.angabe, w, neben)) nehmen(w);
  });
  eingabe?.addEventListener('change', () => { eingabe.value = String(gilt); });
  return feld;
}

/** Die Zeile eines Masses: sein Name, sein Feld, seine Einheit. */
function massZeile(mass, wert, setzen, neben = {}) {
  return cadZeile(mass.heisst, massFeld(mass, wert, setzen, neben), mass.angabe.einheit || '');
}

/**
 * Die Zeile einer Lage -- oder der Bügel: Durchmesser und Teilung, beim
 * Kreis Durchmesser und Anzahl, je mit dem kurzen Zeichen des Kerns
 * (`lage.kurz`: ⌀, s, n) und ihrer Einheit; der ganze Name ist der Titel
 * des Feldes. Die Zahlen stehen in `masse` der Wahl.
 */
function lagenZeile(lage, masse, holen) {
  const felder = lage.masse.flatMap((m, i) => [
    el('span', { text: lage.kurz[i] }),
    massFeld({ ...m, titel: m.heisst }, masse[m.schluessel] ?? m.vorgabe, (x) => {
      masse[m.schluessel] = x;
      holen();
    }),
    m.angabe.einheit ? el('span.einheit', { text: m.angabe.einheit }) : null,
  ]);
  return el('div.cad-zeile', {}, [el('span', { text: lage.name }), el('div.cad-lage', {}, felder), el('span')]);
}

/**
 * Eine Vorlage aus Flächen -- Rechteck, T-Balken, … Kreis: ihre Masse, das
 * Material der Flächen, ein zweites, wo sie eines zur Wahl stellt (der
 * Aufbeton), und die Bewehrung. Bewehrung und Schubwände liegen nur im
 * Beton (Benutzer, 2026-11-25): aus Holz oder Baustahl kommt die Vorlage
 * ohne, und ihre Schalter warten, bis das Material wieder Beton ist.
 *
 * Die Überdeckung zählt für Stäbe und Wände: sie ist nur gesperrt, wenn
 * beide aus sind.
 */
function flaechenvorlage(a, { vorgaben, flaechenklasse, neu, holen }) {
  const w = wahlVon(a);
  const v = gewaehlteVorlage(a);
  const { material } = vorgaben.flaechen;
  const bewehrt = eintragVon(material)?.art === katalog('querschnittsanalyse', 'bewehrt');
  w.stoffe = w.stoffe || {};
  for (const s of v.stoffe) w.stoffe[s.schluessel] = gueltigesMaterial(s.arten, w.stoffe[s.schluessel]);
  const anfrage = () => structuredClone({
    ...w, bewehrung: bewehrt && w.bewehrung, schubwaende: bewehrt && w.schubwaende,
  });
  const waende = v.hat_waende;
  const zahl = (m) => massZeile(m, w.masse[m.schluessel] ?? m.vorgabe,
    (x) => { w.masse[m.schluessel] = x; holen(); });
  // Unter jeder Lage, was aus ihr wird -- gesetzt, sobald die Skizze kommt.
  const stabzahlen = Object.fromEntries(v.lagen.map((l) => [l.schluessel, el('p.cad-hinweis-klein.cad-stabzahl')]));
  const bewehrung = () => [
    gesperrt(!w.bewehrung && !(waende && w.schubwaende), [zahl(katalog('querschnittsanalyse', 'ueberdeckung'))]),
    mitOhne('Bewehrung', w.bewehrung, (x) => { w.bewehrung = x; neu(); }),
    gesperrt(!w.bewehrung, v.lagen.flatMap((l) => [
      lagenZeile(l, w.masse, holen), el('div.cad-zeile', {}, [el('span'), stabzahlen[l.schluessel]]),
    ])),
    ...(waende ? [
      mitOhne('Schubwände', w.schubwaende, (x) => { w.schubwaende = x; neu(); }),
      gesperrt(!w.schubwaende, [lagenZeile(katalog('querschnittsanalyse', 'buegel'), w.masse, holen)]),
    ] : []),
  ];
  return {
    anfrage,
    bild: { flaeche: flaechenklasse(material) },
    stabzahlen: (lagen) => {
      for (const [schluessel, p] of Object.entries(stabzahlen)) {
        p.textContent = lagen[schluessel] ? `→ ${lagen[schluessel]}` : '';
      }
    },
    zeilen: [
      ...v.masse.map(zahl),
      cadZeile('Material', materialliste({
        art: feldangabe('flaeche', 'material').stoffe, gewaehlt: material,
        titel: 'Woraus die Flächen der Vorlage sind – so auch die nächste gezeichnete',
        setzen: (x) => { vorgaben.flaechen.material = x; neu(); },
      })),
      ...v.stoffe.map((s) => cadZeile(s.beschriftung, materialliste({
        art: s.arten, gewaehlt: w.stoffe[s.schluessel], titel: s.titel,
        setzen: (x) => { w.stoffe[s.schluessel] = x; neu(); },
      }))),
      ...(bewehrt ? bewehrung() : [el('p.hinweis', {
        text: `${waende ? 'Bewehrung und Schubwände liegen' : 'Bewehrung liegt'} nur im Beton – `
          + 'die Vorlage kommt ohne.',
      })]),
    ],
    hinein: (p) => einsetzen(a, anfrage(), p, { material, stahl: vorgaben.stablinien.stahl }),
  };
}

/**
 * Das Stahlprofil: ein Profil an seiner Mitte, keine Fläche -- Reihe und
 * Grösse, Baustahl, Drehung und Spiegeln, wie in der Seitenleiste eines
 * gezeichneten. Was eingestellt ist, bleibt je Analyse in der Ansicht
 * (`a.qa.vorlagenprofil`), wie die Masse der Vorlagen; einem Baustahl, den
 * es nicht mehr gibt, folgt der erste.
 *
 * Drehung und Spiegeln stehen nur da, wo sie das Profil ändern: das sagt
 * die Skizze des Kerns. Bis sie da ist, gilt, was die letzte sagte -- sonst
 * verschwänden die Schalter bei jedem Klick. Sie ändern nur die Skizze,
 * Reihe, Grösse und Stahl alles.
 */
function profilvorlage(a, neu, holen) {
  a.qa.vorlagenprofil = a.qa.vorlagenprofil || ausVorlage('profil');
  const e = a.qa.vorlagenprofil;
  const stoffe = feldangabe('profil', 'stahl').stoffe;
  gibtMaterial(e, 'profil', 'stahl');
  const setzen = (feld) => (x) => { e[feld] = x; neu(); };
  const drehen = el('div.cad-gruppe');
  const zeigen = () => drehen.replaceChildren(...drehZeilen((feld) => e[feld], (feld) => (x) => {
    e[feld] = x;
    zeigen();
    holen();
  }, a.qa.profilform));
  zeigen();
  return {
    anfrage: () => ({
      art: katalog('querschnittsanalyse', 'profil').schluessel,
      profil: e.profil, drehung: e.drehung, gespiegelt: e.gespiegelt,
    }),
    bild: PROFILBILD,
    beantwortet: (antwort) => {
      a.qa.profilform = { drehbar: antwort.drehbar, spiegelbar: antwort.spiegelbar };
      zeigen();
    },
    zeilen: [
      wahlBlock('Reihe', reihenSchalter(e.profil, setzen('profil'), '.cad-wahl')),
      ...groessenZeilen(e.profil, setzen('profil'), cadZeile),
      cadZeile('Stahl', materialliste({
        art: stoffe, gewaehlt: e.stahl, titel: 'Woraus das Profil ist', setzen: setzen('stahl'),
      })),
      drehen,
    ],
    hinein: (p) => umrissEinsetzen(a, PROFIL, e, p),
  };
}

/**
 * Die Blechverbunddecke: eine Decke an ihrer Ecke links unten, keine
 * Fläche -- ihr Beton, ihr Blech und die Masse aus dem Datenblatt, wie in
 * der Seitenleiste einer gezeichneten. Was eingestellt ist, bleibt je
 * Analyse in der Ansicht (`a.qa.vorlagendecke`). Unter der Skizze der
 * ganzen Decke steht eine Rippe mit ihren Massen: in der ganzen wären sie
 * nicht zu lesen. Die Masse ändern nur die Skizzen, ein Material alles.
 */
function deckenvorlage(a, neu, holen) {
  a.qa.vorlagendecke = a.qa.vorlagendecke || ausVorlage('blechdecke');
  const e = a.qa.vorlagendecke;
  for (const [feld] of STOFFE) gibtMaterial(e, 'blechdecke', feld);
  const rippe = el('div.cad-vorlagenskizze');
  return {
    anfrage: () => ({
      art: katalog('querschnittsanalyse', 'blechdecke').schluessel,
      ...Object.fromEntries(MASSE.map(([feld]) => [feld, e[feld]])),
    }),
    beantwortet: (antwort) => rippe.replaceChildren(skizze(antwort.rippe, 276, 150)),
    zeilen: [
      rippe,
      ...STOFFE.map(([feld, beschriftung]) => cadZeile(beschriftung, materialliste({
        art: feldangabe('blechdecke', feld).stoffe, gewaehlt: e[feld],
        setzen: (x) => { e[feld] = x; neu(); },
      }))),
      ...MASSE.map(([feld, schritt]) => {
        const angabe = feldangabe('blechdecke', feld);
        return massZeile({ heisst: angabe.zeichen, titel: angabe.heisst, schritt, angabe }, e[feld],
          (x) => { e[feld] = x; holen(); }, e);
      }),
    ],
    hinein: (p) => umrissEinsetzen(a, BLECHDECKE, e, p),
  };
}

/**
 * Das Material `gewaehlt`, wenn es eines der `arten` im Projekt ist -- sonst
 * das erste, das passt, wie in einem neuen Fenster. Gibt es keines, bleibt
 * der Verweis: die Liste sagt dann, dass es im Projekt noch keines gibt.
 */
function gueltigesMaterial(arten, gewaehlt) {
  if (arten.some((art) => materialien(art).some((m) => m.kennung === gewaehlt))) return gewaehlt;
  return arten.map((art) => materialien(art)[0]?.kennung).find(Boolean) || gewaehlt;
}

/** Folgt dem Material im Feld `feld` des Eintrags `e` der Klasse `klasse` (`gueltigesMaterial`). */
function gibtMaterial(e, klasse, feld) {
  e[feld] = gueltigesMaterial(feldangabe(klasse, feld).stoffe, e[feld]);
}

/** Setzt eine Vorlage aus Flächen ein -- ihre Flächen aus `material`, ihre Bewehrung aus `stahl`. */
async function einsetzen(a, wahl, ursprung, { material, stahl }) {
  try {
    const antwort = await api.vorlageEinsetzen(zustand.projekt, a.qa.kennung, wahl, ursprung, material, stahl);
    a.aendern((z) => { Object.assign(z, antwort.elemente); }, { auswahl: () => antwort.neu });
  } catch (fehler) {
    melden(fehler.message, true);
  }
}
