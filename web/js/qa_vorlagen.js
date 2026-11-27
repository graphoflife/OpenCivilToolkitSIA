/**
 * qa_vorlagen.js -- ein Querschnitt aus einer Vorlage: Rechteck, T-Balken,
 * Hohlkasten, Kreis -- oder ein Stahlprofil, eine Blechverbunddecke.
 *
 * T oder der Knopf «Vorlage» öffnet ein Fenster oben links in der Zeichnung.
 * Oben stehen die Vorlagen als kleine Bilder, darunter ihre Masse als Felder
 * und eine Skizze mit Masslinien, die sich ändert, während man tippt.
 * «Einsetzen» fragt nach dem Einsetzpunkt, mit allem, was die Punkteingabe
 * kann; Enter ohne Zahlen heisst Ursprung. Die Vorlage kommt dazu: was schon
 * gezeichnet ist, bleibt.
 *
 * Die Vorlagen stehen im Kern (`opencivil/querschnitt/vorlagen.py`), und nur
 * dort. Hier wird gewählt und gezeigt: die Skizze kommt aus der Anfrage
 * `vorlage`, eingesetzt wird mit dem Baukasten des Kerns über
 * `vorlage_einsetzen`.
 *
 * Die Vorlage «Stahlprofil» setzt ein Profil ein, keine Fläche (Plan vom
 * 2026-11-25): Reihe, Grösse, Baustahl, Drehung und ob gespiegelt, wie im
 * schwebenden Fenster eines gezeichneten (qa_profile.js). Ihre Mitte kommt
 * an den Einsetzpunkt -- bei den anderen die Ecke unten links. Ebenso setzt
 * die Vorlage «Blechverbunddecke» eine Decke ein, mit ihren Massen und
 * Materialien (qa_blechdecke.js); unter ihrer Skizze steht eine Rippe mit
 * ihren Massen.
 *
 * Die Skizzen zeichnet qa_skizze.js.
 */

import { api } from './api.js';
import { hakenSchalter, materialliste, wahlBlock } from './bausteine.js';
import { pfad } from './cad_ansicht.js';
import { schalterzeile } from './cad_palette.js';
import { el, grenzeVerletzt, melden, svgEl, zahlfeld } from './dom.js';
import { groessenListe, reihenSchalter } from './profilwahl.js';
import { BLECHDECKE, MASSE, STOFFE } from './qa_blechdecke.js';
import { PROFIL, drehZeilen } from './qa_profile.js';
import { skizze } from './qa_skizze.js';
import { umrissEinsetzen } from './qa_umriss.js';
import {
  ausVorlage, eintragVon, feldangabe, katalog, materialien, zustand,
} from './zustand.js';

/** Die Vorlagen, wie der Kern sie kennt. */
function vorlagen() {
  return katalog('querschnittsanalyse', 'vorlagen');
}

/** Die Vorlage, die ein Stahlprofil einsetzt: ihr Schlüssel, ihr Name, ihr Bild. */
function stahlprofil() {
  return katalog('querschnittsanalyse', 'profil');
}

/** Die Vorlage, die eine Blechverbunddecke einsetzt: ihr Schlüssel, ihr Name, ihr Bild. */
function blechdecke() {
  return katalog('querschnittsanalyse', 'blechdecke');
}

/** Wie ein Stahlprofil in einer Skizze aussieht: aus Baustahl, ein Stück mit seinem Loch. */
const PROFILBILD = { flaeche: 'cad-baustahl', einStueck: true };

/** Der Achsabstand der Stäbe vom Rand -- ein Mass aller Vorlagen. */
function randabstand() {
  return katalog('querschnittsanalyse', 'randabstand');
}

/** Was zuletzt eingestellt war -- je Analyse in der Ansicht, nicht im Projekt. */
function wahlVon(a) {
  a.qa.vorlage = a.qa.vorlage || {
    art: 'rechteck', masse: {}, randabstand: randabstand().vorgabe, bewehrung: true,
    schubwaende: true,
  };
  return a.qa.vorlage;
}

// ===========================================================================
// Das Fenster
// ===========================================================================

function zeile(beschriftung, eingabe, einheit = '') {
  return el('label.cad-zeile', {}, [
    el('span', { text: beschriftung }), eingabe, einheit ? el('span.einheit', { text: einheit }) : el('span'),
  ]);
}

/**
 * Mit oder ohne, etwa «Bewehrung» -- ein Schalter wie in den Eigenschaften
 * der Zeichnung, kein Haken (Benutzer, 2026-11-19). Das Fenster zeichnet
 * sich beim Umschalten nicht neu, nur die Skizze: darum ersetzt sich die
 * Zeile selbst.
 */
function mitOhne(text, an, setzen) {
  const zeile = schalterzeile(text, hakenSchalter(an, (x) => {
    setzen(x);
    zeile.replaceWith(mitOhne(text, x, setzen));
  }, text));
  return zeile;
}

/**
 * Die Zeile eines Masses: ein Zahlenfeld, das schon beim Tippen meldet --
 * die Skizze soll mitgehen. Name, Grenze, Satz und Einheit kommen mit dem
 * Mass aus dem Kern (`angabe`), wie bei jedem Feld; steht statt des Namens
 * ein Zeichen da, ist der Name sein Titel (`mass.titel`).
 *
 * Beim Tippen geht nur eine Zahl in die Skizze, die das Feld auch nimmt.
 * Nimmt es eine nicht, zeigt es wieder die zuletzt übernommene: das Fenster
 * zeichnet sich beim Tippen nicht neu, und das Feld kennt sonst nur die
 * Zahl, mit der es aufging. Begrenzt ein Mass ein anderes -- die Rippe
 * einer Decke ist niedriger als die Decke --, stehen die Masse in `neben`.
 */
function massZeile(mass, wert, setzen, neben = {}) {
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
  return zeile(mass.heisst, feld, mass.angabe.einheit || '');
}

/**
 * Öffnet das Fenster der Vorlagen -- oder schliesst es, wenn es schon offen
 * ist. `vorgaben` sind die der Zeichnung, geprüft gegen das Projekt: aus
 * ihrem Material sind die Flächen, aus ihrem Stahl die Bewehrung. Wie eine
 * Fläche aussieht, sagt `flaechenklasse(material)`.
 */
export function vorlageOeffnen(a, vorgaben, flaechenklasse) {
  if (a.dialog) {
    a.dialog.schliessen();
    return;
  }
  if (!vorlagen().length) return;
  const knoten = el('div.cad-dialog', { role: 'dialog', 'aria-label': 'Vorlage' });
  const schliessen = () => {
    knoten.remove();
    a.dialog = null;
  };
  a.dialog = { schliessen };
  a.teile.flaeche.append(knoten);
  vorlageZeichnen(a, knoten, vorgaben, flaechenklasse);
}

function vorlageZeichnen(a, knoten, vorgaben, flaechenklasse) {
  const w = wahlVon(a);
  const alle = [...vorlagen(), stahlprofil(), blechdecke()];
  const v = alle.find((x) => x.schluessel === w.art) || alle[0];
  w.art = v.schluessel;
  const neu = () => vorlageZeichnen(a, knoten, vorgaben, flaechenklasse);

  const bild = el('div.cad-vorlagenskizze');
  const meldung = el('p.cad-meldung', { hidden: true });
  const einsetzen = el('button.knopf.knopf-klein.knopf-haupt', {
    type: 'button', text: 'Einsetzen', title: 'Danach den Einsetzpunkt wählen – Enter: Ursprung',
    on: {
      click: () => {
        const teile = a.qa.vorlagenteile;
        if (!teile) return;
        a.dialog?.schliessen();
        a.starten(einsetzenBefehl(v.name, teile, art));
      },
    },
  });

  // Die Skizze kommt vom Kern. Kommt eine Antwort zu spät -- es wurde
  // inzwischen wieder getippt --, gilt sie nicht mehr.
  const holen = () => {
    const nr = (a.qa.vorlagenfrage || 0) + 1;
    a.qa.vorlagenfrage = nr;
    bild.classList.add('ist-alt');
    api.vorlage(art.anfrage()).then((antwort) => {
      if (a.qa.vorlagenfrage !== nr) return;
      meldung.hidden = !antwort.fehler;
      meldung.textContent = antwort.fehler || '';
      einsetzen.disabled = !antwort.teile;
      a.qa.vorlagenteile = antwort.teile;
      if (antwort.teile) {
        bild.classList.remove('ist-alt');
        bild.replaceChildren(skizze(antwort.teile, 276, 140, art.bild));
        art.beantwortet?.(antwort);
      }
    }).catch((fehler) => melden(fehler.message, true));
  };

  const eigene = {
    [stahlprofil().schluessel]: () => profilvorlage(a, neu, holen),
    [blechdecke().schluessel]: () => deckenvorlage(a, neu, holen),
  };
  const art = eigene[v.schluessel]?.() || flaechenvorlage(a, w, v, { vorgaben, flaechenklasse, neu, holen });
  knoten.replaceChildren(
    el('div.cad-dialog-kopf', {}, [
      el('span', { text: 'Vorlage' }),
      el('button.cad-palette-zu', {
        type: 'button', text: '×', title: 'Schliessen (Esc)', on: { click: () => a.dialog?.schliessen() },
      }),
    ]),
    el('div.cad-vorlagen', {}, alle.map((x) => el('button.cad-vorlagenknopf', {
      type: 'button', title: x.name, class: x.schluessel === v.schluessel ? 'ist-an' : '',
      on: { click: () => { w.art = x.schluessel; neu(); } },
    }, [
      skizze(x.skizze, 52, 36, { masse: false, ...(x.schluessel === stahlprofil().schluessel ? PROFILBILD : {}) }),
      el('span', { text: x.name }),
    ]))),
    bild,
    ...art.zeilen,
    meldung,
    el('div.cad-dialog-fuss', {}, [einsetzen]),
  );
  holen();
}

/**
 * Eine Vorlage aus Flächen -- Rechteck, T-Balken, Hohlkasten, Kreis: ihre
 * Masse, das Material der Flächen und die Bewehrung. Bewehrung und
 * Schubwände liegen nur im Beton (Benutzer, 2026-11-25): aus Holz oder
 * Baustahl kommt die Vorlage ohne, und ihre Schalter warten, bis das
 * Material wieder Beton ist. Eine Masse ändert nur die Skizze (`holen`),
 * ein Material das ganze Fenster (`neu`).
 */
function flaechenvorlage(a, w, v, { vorgaben, flaechenklasse, neu, holen }) {
  const { material } = vorgaben.flaechen;
  const bewehrt = eintragVon(material)?.art === katalog('querschnittsanalyse', 'bewehrt');
  const anfrage = () => structuredClone({
    ...w, bewehrung: bewehrt && w.bewehrung, schubwaende: bewehrt && w.schubwaende,
  });
  const waende = v.hat_waende;
  return {
    anfrage,
    bild: { flaeche: flaechenklasse(material) },
    zeilen: [
      ...v.masse.map((m) => massZeile(m, w.masse[m.schluessel] ?? m.vorgabe,
        (x) => { w.masse[m.schluessel] = x; holen(); })),
      zeile('Material', materialliste({
        art: feldangabe('flaeche', 'material').stoffe, gewaehlt: material,
        titel: 'Woraus die Flächen der Vorlage sind – so auch das nächste Polygon',
        setzen: (x) => { vorgaben.flaechen.material = x; neu(); },
      })),
      ...(bewehrt ? [
        massZeile(randabstand(), w.randabstand, (x) => { w.randabstand = x; holen(); }),
        mitOhne('Bewehrung', w.bewehrung, (x) => { w.bewehrung = x; holen(); }),
        waende ? mitOhne('Schubwände', w.schubwaende, (x) => { w.schubwaende = x; holen(); }) : null,
      ] : [el('p.hinweis', {
        text: `${waende ? 'Bewehrung und Schubwände liegen' : 'Bewehrung liegt'} nur im Beton – `
          + 'die Vorlage kommt ohne.',
      })]),
    ],
    hinweis: 'Die Ecke unten links kommt an den Punkt',
    hinein: (p) => einsetzen(a, anfrage(), p, { material, stahl: vorgaben.stablinien.stahl }),
  };
}

/**
 * Die Vorlage «Stahlprofil»: ein Profil an seiner Mitte, keine Fläche --
 * Reihe und Grösse, Baustahl, Drehung und Spiegeln, wie im schwebenden
 * Fenster eines gezeichneten. Was eingestellt ist, bleibt je Analyse in der
 * Ansicht (`a.qa.vorlagenprofil`), wie die Masse der anderen; einem
 * Baustahl, den es nicht mehr gibt, folgt der erste.
 *
 * Drehung und Spiegeln stehen nur da, wo sie das Profil ändern: das sagt
 * die Skizze des Kerns. Bis sie da ist, gilt, was die letzte sagte -- sonst
 * verschwänden die Schalter bei jedem Klick. Sie ändern nur die Skizze,
 * Reihe, Grösse und Stahl das ganze Fenster.
 */
function profilvorlage(a, neu, holen) {
  a.qa.vorlagenprofil = a.qa.vorlagenprofil || ausVorlage('profil');
  const e = a.qa.vorlagenprofil;
  const stoffe = feldangabe('profil', 'stahl').stoffe;
  gibtMaterial(e, 'profil', 'stahl');
  const setzen = (feld) => (x) => { e[feld] = x; neu(); };
  const drehen = el('div.cad-dialog-gruppe');
  const zeigen = () => drehen.replaceChildren(...drehZeilen((feld) => e[feld], (feld) => (x) => {
    e[feld] = x;
    zeigen();
    holen();
  }, a.qa.profilform));
  zeigen();
  const groessen = groessenListe(e.profil, setzen('profil'));
  return {
    anfrage: () => ({
      art: stahlprofil().schluessel, profil: e.profil, drehung: e.drehung, gespiegelt: e.gespiegelt,
    }),
    bild: PROFILBILD,
    beantwortet: (antwort) => {
      a.qa.profilform = { drehbar: antwort.drehbar, spiegelbar: antwort.spiegelbar };
      zeigen();
    },
    zeilen: [
      wahlBlock('Reihe', reihenSchalter(e.profil, setzen('profil'), '.cad-wahl')),
      groessen ? zeile('Profil', groessen) : null,
      zeile('Stahl', materialliste({
        art: stoffe, gewaehlt: e.stahl, titel: 'Woraus das Profil ist', setzen: setzen('stahl'),
      })),
      drehen,
    ],
    hinweis: 'Die Mitte des Profils kommt an den Punkt',
    hinein: (p) => umrissEinsetzen(a, PROFIL, e, p),
  };
}

/**
 * Die Vorlage «Blechverbunddecke»: eine Decke an ihrer Ecke links unten,
 * keine Fläche -- ihr Beton, ihr Blech und die Masse aus dem Datenblatt,
 * wie im schwebenden Fenster einer gezeichneten. Was eingestellt ist, bleibt
 * je Analyse in der Ansicht (`a.qa.vorlagendecke`). Unter der Skizze der
 * ganzen Decke steht eine Rippe mit ihren Massen: in der ganzen wären sie
 * nicht zu lesen. Die Masse ändern nur die Skizzen, ein Material das ganze
 * Fenster.
 */
function deckenvorlage(a, neu, holen) {
  a.qa.vorlagendecke = a.qa.vorlagendecke || ausVorlage('blechdecke');
  const e = a.qa.vorlagendecke;
  for (const [feld] of STOFFE) gibtMaterial(e, 'blechdecke', feld);
  const rippe = el('div.cad-vorlagenskizze');
  return {
    anfrage: () => ({
      art: blechdecke().schluessel, ...Object.fromEntries(MASSE.map(([feld]) => [feld, e[feld]])),
    }),
    beantwortet: (antwort) => rippe.replaceChildren(skizze(antwort.rippe, 276, 150)),
    zeilen: [
      rippe,
      ...STOFFE.map(([feld, beschriftung]) => zeile(beschriftung, materialliste({
        art: feldangabe('blechdecke', feld).stoffe, gewaehlt: e[feld],
        setzen: (x) => { e[feld] = x; neu(); },
      }))),
      ...MASSE.map(([feld, schritt]) => {
        const angabe = feldangabe('blechdecke', feld);
        return massZeile({ heisst: angabe.zeichen, titel: angabe.heisst, schritt, angabe }, e[feld],
          (x) => { e[feld] = x; holen(); }, e);
      }),
    ],
    hinweis: 'Die Ecke links unten – die Unterkante der Rippen – kommt an den Punkt',
    hinein: (p) => umrissEinsetzen(a, BLECHDECKE, e, p),
  };
}

/**
 * Gibt es das Material im Feld `feld` des Eintrags `e` der Klasse `klasse`
 * nicht mehr, folgt ihm das erste, das das Feld nimmt -- wie in einem neuen
 * Fenster. Gibt es keines, bleibt der Verweis: die Liste sagt dann, dass es
 * im Projekt noch keines gibt.
 */
function gibtMaterial(e, klasse, feld) {
  const stoffe = feldangabe(klasse, feld).stoffe;
  if (!stoffe.some((art) => materialien(art).some((m) => m.kennung === e[feld]))) {
    e[feld] = stoffe.map((art) => materialien(art)[0]?.kennung).find(Boolean) || e[feld];
  }
}

// ===========================================================================
// Einsetzen
// ===========================================================================

/** Setzt die Vorlage ein -- ihre Flächen aus `stoffe.material`, ihre Bewehrung aus `stoffe.stahl`. */
async function einsetzen(a, wahl, ursprung, { material, stahl }) {
  try {
    const antwort = await api.vorlageEinsetzen(zustand.projekt, a.qa.kennung, wahl, ursprung, material, stahl);
    a.aendern((z) => { Object.assign(z, antwort.elemente); }, { auswahl: () => antwort.neu });
  } catch (fehler) {
    melden(fehler.message, true);
  }
}

/**
 * Der Befehl nach «Einsetzen»: ein Punkt, an den die Vorlage kommt -- bei
 * den Flächen und der Decke ihre Ecke unten links, beim Profil seine Mitte; was dort
 * hinkommt, sagt `art.hinweis`, eingesetzt wird mit `art.hinein(p)`.
 * Die Vorschau zeigt die Umrisse der Skizze am Zeiger.
 */
function einsetzenBefehl(name, teile, art) {
  return {
    name: 'vorlage',
    frage: () => `${name}: Einsetzpunkt`,
    hinweis: `${art.hinweis} · Enter ohne Zahlen: Ursprung`,
    punkt(a, erg) {
      art.hinein(erg.p);
      a.ende();
    },
    vorschau(a, g) {
      const f = a.zeiger?.fang;
      if (!f) return;
      const hin = (p) => [p[0] + f.p[0], p[1] + f.p[1]];
      for (const p of teile.polygone) {
        g.append(svgEl('path', { d: pfad(a.v, p.punkte.map(hin)), class: 'cad-verschoben' }));
      }
      for (const l of [...teile.stablinien, ...teile.schubwaende]) {
        g.append(svgEl('path', { d: pfad(a.v, [hin(l.von), hin(l.bis)], false), class: 'cad-verschoben' }));
      }
    },
    enter() {
      art.hinein([0, 0]);
      return false;
    },
    zurueck: () => false,
  };
}
