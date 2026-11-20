/**
 * bs_eigenschaften.js -- das schwebende Fenster im Zeichenfenster eines
 * Balkensystems.
 *
 * Was ein Werkzeug als Nächstes anlegt (`neuEigenschaften`) und was gewählt
 * ist (`eigenschaften`): je Knoten, Linie oder Last ihre Felder. Sind
 * mehrere gewählt, ändert das Fenster alle zugleich -- was sie gemeinsam
 * haben, steht da, sonst «Var» (Benutzer, 2026-10-24).
 *
 * Vom Zeichenfenster kennt es nur `a`: den Zustand (`a.bs`, mit der Art des
 * Systems), das Modell (`a.modell`) und den Adapter (`a.adapter`), über den
 * es die Zeichnung liest und Linien umkehrt. Welche Felder ein Lager, ein
 * Linienlager und eine Last haben, sagt der Katalog der Art -- eben und im
 * Raum derselbe Code. Was jedes Fenster mit Zeichnung gleich hat -- die
 * Auswahl nach Listen, Felder für mehrere, die Lage der Knoten, die
 * Meldungen --, steht in cad_app.js. So hängt `bs_zeichnung.js` an dieser
 * Datei und nicht umgekehrt.
 * Gerechnet wird hier nichts.
 */

import {
  VAR, gemeinsam, mitVar, wahlBlock, wahlSchalter,
} from './bausteine.js';
import {
  knotenlastart, lastart, lastVon, materialname, systemkatalog,
} from './bs_teile.js';
import { texte } from './bs_texte.js';
import {
  auswahlEigenschaften, frischeAntwort, jaNein, laengenzeile, lagefelder, meldungszeilen, vorgabe,
  zahlfeldMitVar, zugleich,
} from './cad_app.js';
import { cadZeile, schalterzeile } from './cad_palette.js';
import { auswahl, el } from './dom.js';
import { aktiverLastfall, lastfallWaehlen, lastfallZeile } from './lastfaelle.js';
import { ausVorlage, feldangabe } from './zustand.js';

/** Was ein Lager je Richtung kann -- die Feder heisst an einer Linie Bettung. */
const HALT = [
  { wert: 'frei', beschriftung: 'frei' },
  { wert: 'fest', beschriftung: 'fest' },
  { wert: 'feder', beschriftung: 'Feder' },
];

/**
 * Das Material, das eine neue Linie bekommt: das gewählte, solange es das
 * gibt, sonst das erste des Systems.
 */
export function vorgabeMaterial(a, z) {
  const v = a.bs.vorgaben.linie.material;
  const gibt = v === systemkatalog(a.bs.art, 'material_des_querschnitts')
    || (z.stabmaterialien || []).some((m) => m.kennung === v);
  return gibt ? v : z.stabmaterialien?.[0]?.kennung || '';
}

/**
 * Der Querschnitt, den eine neue Linie bekommt: der gewählte, solange es ihn
 * gibt, sonst der erste des Systems; «– kein Stab –» nur, wenn man es wählt.
 * Bis 2026-11-19 galt, was beim Öffnen der erste war: ein neues System
 * zeichnete auch mit Querschnitt jede Linie als «kein Stab», und ein
 * gelöschter blieb die Vorgabe -- die Linie bekam ihn trotzdem.
 */
export function vorgabeQuerschnitt(a, z) {
  const v = a.bs.vorgaben.linie.querschnitt;
  if (v === '') return '';
  const alle = z.querschnitte || [];
  return alle.some((q) => q.kennung === v) ? v : alle[0]?.kennung || '';
}

/**
 * Eine Richtung des Lagers mit ihrem Schalter -- frei, fest oder Feder. Die
 * Beschriftung ist ein Zeichen (x, z, φ, φ_x) und braucht nur eine schmale
 * Spalte. Ein «div», kein «label»: ein Klick auf das Zeichen löste sonst die
 * erste Stellung aus.
 */
function richtungszeile(beschriftung, schalter) {
  return el('div.cad-zeile.ist-richtung', {}, [el('span', { text: beschriftung }), schalter]);
}

/** Ob ein Querschnitt ein Material mitbringt -- eine Platte oder Analyse; das sagt der Katalog. */
function bringtMaterial(art, q) {
  return Boolean(systemkatalog(art, 'querschnittsarten').find((x) => x.wert === q?.art)?.bringt_material);
}

/**
 * Die Querschnitte des Systems -- und «kein Stab»: dann ist die Linie nur
 * eine Linie, etwa für eine Bettung. Nimmt die Linie das Material ihres
 * Querschnitts, stehen nur die da, die eines mitbringen (Benutzer,
 * 2026-10-24) -- und der gewählte.
 */
function querschnittWahl(art, z, gewaehlt, setzen, material = '') {
  const nurMitMaterial = material === systemkatalog(art, 'material_des_querschnitts');
  const werte = [
    { wert: '', beschriftung: (z.querschnitte || []).length ? '– kein Stab –' : '– kein Stab: noch kein Querschnitt –' },
    ...(z.querschnitte || []).filter((q) => !nurMitMaterial || bringtMaterial(art, q) || q.kennung === gewaehlt)
      .map((q) => ({ wert: q.kennung, beschriftung: q.name || q.kennung })),
  ];
  return auswahl({ werte: mitVar(werte, gewaehlt), gewaehlt, titel: 'Die Querschnitte: Knopf «Querschnitte» unter der Zeichnung', beiAenderung: setzen });
}

/**
 * Warum die Liste der Querschnitte kürzer ist: mit dem Material «gemäss
 * Querschnitt» stehen nur die zur Wahl, die einen Beton mitbringen. Bis
 * 2026-11-19 fehlten die anderen ohne ein Wort.
 */
function nurMitMaterialHinweis(art, z, material) {
  const fehlen = material === systemkatalog(art, 'material_des_querschnitts')
    && (z.querschnitte || []).some((q) => !bringtMaterial(art, q));
  return fehlen ? el('p.cad-hinweis-klein', {
    text: 'Mit dem Material «gemäss Querschnitt» stehen nur Querschnitte aus einer Platte oder '
      + 'Querschnittsanalyse zur Wahl – nur sie bringen einen Beton mit.',
  }) : null;
}

/**
 * Das Material einer Linie: eines des Systems -- oder «gemäss Querschnitt»,
 * wenn ihr Querschnitt eines mitbringt (`bringt`: Platte, Analyse).
 */
function materialWahl(art, z, bringt, gewaehlt, setzen) {
  const eigenes = systemkatalog(art, 'material_des_querschnitts');
  const werte = [
    ...(z.stabmaterialien || []).map((m) => ({ wert: m.kennung, beschriftung: materialname(m) })),
    ...(bringt || gewaehlt === eigenes ? [{ wert: eigenes, beschriftung: 'gemäss Querschnitt' }] : []),
  ];
  return auswahl({
    werte: gewaehlt === VAR || werte.some((x) => x.wert === gewaehlt) ? mitVar(werte, gewaehlt)
      : [{ wert: gewaehlt, beschriftung: werte.length ? '– Material wählen –' : '– noch kein Material im System –' }, ...werte],
    gewaehlt,
    titel: 'Die Materialien: Knopf «Material» unter der Zeichnung – «gemäss Querschnitt»: der Beton der Platte oder Analyse',
    beiAenderung: setzen,
  });
}

/**
 * Die Felder einer Last: Richtung, Wert -- verteilt Anfang und Ende --,
 * die Stelle einer einzelnen in % der Linie, und ob eine verteilte je Meter
 * Projektion zählt. `wert(feld)` ist der Wert der Last, der Vorgabe des
 * Werkzeugs oder das Gemeinsame mehrerer Lasten derselben Art (VAR, wo sie
 * sich unterscheiden); `setzen(feld)(w)` schreibt; `ort`: wo sie liegt --
 * 'linie', 'knoten' oder, als Vorgabe des Werkzeugs, noch nirgends (null).
 * Eine Stelle hat nur eine Last auf einer Linie: bis 2026-11-20 zeigte
 * auch eine an einem Knoten das Feld, und eine Zahl darin hielt das System
 * an. Eine Richtung hat in der Ebene nur eine Kraft, im Raum auch ein
 * Moment: es dreht um sie.
 */
function lastFelder(a, wert, setzen, ort) {
  const amKnoten = ort === 'knoten';
  const aufLinie = ort === 'linie';
  const art = (amKnoten ? knotenlastart : lastart)(a.bs.art, wert('art'));
  const alle = systemkatalog(a.bs.art, 'richtungen');
  const knotenrichtungen = systemkatalog(a.bs.art, 'knotenrichtungen');
  const richtungen = amKnoten ? alle.filter((x) => knotenrichtungen.includes(x.wert)) : alle;
  const wertFeld = amKnoten ? 'wert' : 'wert_a';
  const text = texte(a.bs.art);
  return [
    art.kraft || a.bs.raum ? wahlBlock(art.kraft ? 'Richtung' : 'Drehachse', wahlSchalter({
      werte: mitVar(richtungen, wert('richtung')), gewaehlt: wert('richtung'), setzen: setzen('richtung'),
      titel: art.kraft ? text.kraftrichtung : text.momentrichtung, klasse: '.ist-umbruch',
    })) : null,
    cadZeile(art.verteilt ? 'Anfang' : 'Wert', zahlfeldMitVar({
      wert: wert(wertFeld), schritt: 5,
      titel: art.kraft ? 'Positiv in Pfeilrichtung' : text.momentsinn,
      beiAenderung: setzen(wertFeld),
    }), art.einheit),
    art.verteilt ? cadZeile('Ende', zahlfeldMitVar({
      wert: wert('wert_b'), schritt: 5, leer: null, platzhalter: 'wie Anfang',
      titel: 'Wert am Ende der Linie – leer: wie am Anfang', beiAenderung: setzen('wert_b'),
    }), art.einheit) : null,
    !art.verteilt && aufLinie ? cadZeile('Stelle', zahlfeldMitVar({
      wert: wert('stelle'), schritt: 5, angabe: feldangabe(a.bs.klassen.stablast, 'stelle'),
      titel: 'Wo die Last steht: in % der Linie ab ihrem Anfang', beiAenderung: setzen('stelle'),
    }), '%') : null,
    art.verteilt && art.kraft && alle.find((x) => x.wert === wert('richtung'))?.im_system && aufLinie
      ? schalterzeile('projiziert', jaNein(wert('projiziert'), setzen('projiziert'),
        text.projiziert), 'je m Projektion') : null,
  ];
}

/** Die Felder für das, was ein Werkzeug als Nächstes anlegt. */
export function neuEigenschaften(a, werkzeug) {
  const z = a.adapter.zeichnung();
  const neu = () => a.neuZeichnen();
  let inhalt = [];
  if (werkzeug === 'linie') {
    const v = a.bs.vorgaben.linie;
    const art = a.bs.art;
    const querschnitt = vorgabeQuerschnitt(a, z);
    inhalt = [
      cadZeile('Querschnitt', querschnittWahl(art, z, querschnitt, (w) => { v.querschnitt = w; neu(); }, vorgabeMaterial(a, z))),
      nurMitMaterialHinweis(art, z, vorgabeMaterial(a, z)),
      querschnitt ? cadZeile('Material', materialWahl(art, z, bringtMaterial(art, z.querschnitte.find((q) => q.kennung === querschnitt)),
        vorgabeMaterial(a, z), (w) => { v.material = w; neu(); })) : null,
    ];
  } else if (werkzeug === 'last') {
    const { wert, setzen } = vorgabe(a, a.bs.vorgaben.last);
    // Der Lastfall steht oben neben «Last»; hier nur, wenn keiner gewählt ist.
    inhalt = [
      aktiverLastfall(a.bs) ? null : el('p.cad-hinweis-klein', {
        text: 'Kein Lastfall gewählt – oben neben «Last» einen wählen.',
      }),
      wahlBlock('Art', wahlSchalter({
        werte: systemkatalog(a.bs.art, 'lastarten').map((x) => ({ wert: x.wert, beschriftung: x.beschriftung, titel: `${x.beschriftung} in ${x.einheit}` })),
        gewaehlt: wert('art'), setzen: setzen('art'), klasse: '.ist-umbruch',
        titel: 'Verteilt liegt eine Last auf der ganzen Linie; einzeln dort, wo geklickt wird, oder an einem Knoten',
      })),
      ...lastFelder(a, wert, setzen, null),
    ];
  }
  return {
    inhalt: inhalt.filter(Boolean),
    schluessel: JSON.stringify([werkzeug, a.bs.vorgaben, aktiverLastfall(a.bs),
      (z.querschnitte || []).map((q) => [q.kennung, q.name, q.art]),
      (z.stabmaterialien || []).map((m) => [m.kennung, materialname(m)])]),
  };
}

/** Was gewählt ist (cad_app.js): Knoten, Linien oder Lasten. */
export function eigenschaften(a) {
  return auswahlEigenschaften(a, {
    knoten: knotenEigenschaften, linien: linienEigenschaften, anhaenge: lastEigenschaften,
  }, [aktiverLastfall(a.bs), a.bs.bettungOffen]);
}


// -- Knoten ------------------------------------------------------------------

/** Welche Vorwahl ein Lager trifft -- 'kein', eine der Lagerarten oder 'eigen'. */
function lagerart(art, lager) {
  if (!lager) return 'kein';
  const felder = systemkatalog(art, 'lagerfelder');
  const treffer = systemkatalog(art, 'lagerarten').find((x) => felder.every(({ feld }) => x[feld] === lager[feld]));
  return treffer ? treffer.wert : 'eigen';
}

function lagerSetzen(a, z, knoten, wahl) {
  z.lager = z.lager.filter((l) => l.knoten !== knoten || wahl !== 'kein');
  if (wahl === 'kein') return;
  let lager = z.lager.find((l) => l.knoten === knoten);
  if (!lager) {
    lager = { ...ausVorlage(a.bs.klassen.lager), kennung: a.modell.naechsteKennung(z, 'A'), knoten };
    z.lager.push(lager);
  }
  const vorwahl = systemkatalog(a.bs.art, 'lagerarten').find((x) => x.wert === wahl);
  for (const { feld } of vorwahl ? systemkatalog(a.bs.art, 'lagerfelder') : []) lager[feld] = vorwahl[feld];
}

function lagerFelder(a, z, knoten) {
  const lager = knoten.map((k) => z.lager.find((l) => l.knoten === k) || null);
  const art = gemeinsam(lager.map((l) => lagerart(a.bs.art, l)));
  const setzen = (w) => a.aendern((zz) => { for (const k of knoten) lagerSetzen(a, zz, k, w); });
  // «je Richtung» ist keine Vorwahl, sondern was die Richtungen darunter
  // ergeben, wenn sie zu keiner passen -- es steht nur dann da. Bis
  // 2026-11-19 war es ein Knopf: ohne Lager legte er ein gelenkiges an, mit
  // Lager tat er nichts.
  const werte = [
    { wert: 'kein', beschriftung: 'kein', titel: 'Kein Lager' },
    ...systemkatalog(a.bs.art, 'lagerarten').map((x) => ({ wert: x.wert, beschriftung: x.wert })),
    ...(art === 'eigen' ? [{ wert: 'eigen', beschriftung: 'je Richtung', titel: 'Die Richtungen darunter passen zu keiner Vorwahl' }] : []),
  ];
  const zeilen = [wahlBlock('Lager', wahlSchalter({
    werte: mitVar(werte, art), gewaehlt: art, setzen, klasse: '.ist-umbruch',
    titel: 'Lager des Knotens – gelenkig hält jede Verschiebung, verschieblich nur die lotrechte, '
      + 'eingespannt alles; darunter jede Richtung für sich',
  }))];
  // Je Richtung nur, wenn alle gewählten ein Lager haben -- sonst stünde da,
  // was nur für einige gilt.
  if (lager.some((l) => !l)) return zeilen;
  const { wert, setzen: richtungSetzen } = zugleich(a, z, 'lager', lager.map((l) => l.kennung));
  for (const { feld, zeichen } of systemkatalog(a.bs.art, 'lagerfelder')) {
    const halt = wert(feld);
    zeilen.push(richtungszeile(zeichen, wahlSchalter({
      werte: mitVar(HALT, halt), gewaehlt: halt, setzen: richtungSetzen(feld), titel: `Halt in ${zeichen}`,
    })));
    if (halt === 'feder') {
      const angabe = feldangabe(a.bs.klassen.lager, `k_${feld}`);
      zeilen.push(cadZeile(`  k_${zeichen}`, zahlfeldMitVar({
        wert: wert(`k_${feld}`), schritt: 1000, angabe,
        titel: `Federsteifigkeit in ${zeichen}`, beiAenderung: richtungSetzen(`k_${feld}`),
      }), angabe.einheit));
    }
  }
  return zeilen;
}

/**
 * Gewählte Knoten: ihre Lage (cad_app.js), ihr Lager, ob sie sich drehen
 * können, und die Meldungen zu ihnen und ihren Lagern -- hier tippt man ihr
 * k. Bis 2026-11-19 standen die Meldungen nur unter der Zeichnung.
 */
function knotenEigenschaften(a, z, knoten) {
  const u = frischeAntwort(a);
  const lager = z.lager.filter((l) => knoten.includes(l.knoten)).map((l) => l.kennung);
  return {
    titel: knoten.length === 1 ? `Knoten ${knoten[0]}` : `${knoten.length} Knoten`,
    inhalt: [
      ...lagefelder(a, z, knoten),
      ...lagerFelder(a, z, knoten),
      ...knoten.filter((k) => u?.unbestimmt?.includes(k))
        .map((k) => el('p.cad-hinweis-klein', { text: `${k}: ${u.unbestimmt_text}.` })),
      ...meldungszeilen(a, [...knoten, ...lager]),
    ].filter(Boolean),
  };
}

// -- Linien ------------------------------------------------------------------

function lagerAnLinie(a, wert, setzen) {
  const werte = HALT.map((x) => (x.wert === 'feder' ? { ...x, beschriftung: 'Bettung' } : x));
  const zeilen = [];
  for (const { feld, beschriftung, zeichen, titel } of systemkatalog(a.bs.art, 'linienlager')) {
    const halt = wert(feld);
    zeilen.push(wahlBlock(beschriftung, wahlSchalter({ werte: mitVar(werte, halt), gewaehlt: halt, titel, setzen: setzen(feld) })));
    if (halt === 'feder') {
      const angabe = feldangabe(a.bs.klassen.linie, `k_${feld}`);
      zeilen.push(cadZeile(`  k_${zeichen}`, zahlfeldMitVar({
        wert: wert(`k_${feld}`), schritt: 1000, angabe, titel: 'Bettungsziffer je Meter Stab',
        beiAenderung: setzen(`k_${feld}`),
      }), angabe.einheit));
    }
  }
  return zeilen;
}

/**
 * Wohin die Achse z einer Linie in der Ebene zeigt -- dort liegt ihre
 * gestrichelte Faser: 'unten' oder 'oben', an einer senkrechten 'links' oder
 * 'rechts'. Ohne Achsen vom Kern null.
 */
function zugseite(achsen) {
  if (!achsen) return null;
  const [x, z] = achsen.z;
  if (Math.abs(z) > 1e-9) return z < 0 ? 'unten' : 'oben';
  return x < 0 ? 'links' : 'rechts';
}

/**
 * In der Ebene: die Zugseite der gewählten Linien als Schalter -- solange
 * der Kern ihre Achsen geschickt hat und sie alle senkrecht oder alle nicht
 * senkrecht liegen. Umschalten kehrt eine Linie im Kern um: die Faser
 * wechselt die Seite, die Lasten bleiben, wo sie wirken, und die Gelenke an
 * ihren Knoten.
 */
function zugseitenzeile(a, z, linien) {
  const seiten = new Map(z.linien.filter((l) => linien.includes(l.kennung))
    .map((l) => [l.kennung, zugseite(a.bs.achsen[l.kennung])]));
  const stellungen = [['unten', 'oben'], ['links', 'rechts']]
    .find((paar) => [...seiten.values()].every((s) => paar.includes(s)));
  if (!stellungen) return null;
  const seite = gemeinsam([...seiten.values()]);
  return schalterzeile('Zugseite', wahlSchalter({
    werte: mitVar(stellungen.map((s) => ({ wert: s, beschriftung: s })), seite),
    gewaehlt: seite,
    titel: 'Die gestrichelte Faser: dort zieht ein positives Moment',
    setzen: (w) => a.adapter.umkehren(a, linien.filter((k) => seiten.get(k) !== w), linien),
  }));
}

/**
 * Im Raum: der Drehwinkel β der gewählten Linien -- er dreht y und z des
 * Stabs um seine Achse, mit ihnen die gestrichelte Faser und die
 * Linienlager quer.
 */
function drehwinkelzeile(a, wert, setzen) {
  const angabe = feldangabe(a.bs.klassen.linie, 'drehung');
  return cadZeile('Drehwinkel β', zahlfeldMitVar({
    wert: wert('drehung'), schritt: 15, angabe, beiAenderung: setzen('drehung'),
    titel: 'Wie weit der Querschnitt um die Achse des Stabs gedreht ist – er dreht y und z des Stabs, die gestrichelte Faser und die Linienlager quer',
  }), angabe.einheit);
}

/**
 * Eine Linie: Querschnitt -- «kein Stab» heisst nur eine Linie --, beim
 * Stab das Material, die Zugseite oder im Raum der Drehwinkel β und die
 * Gelenke. Die Bettung steht eingeklappt darunter: sie braucht man selten
 * (Benutzer, 2026-10-23).
 */
function linienEigenschaften(a, z, linien) {
  // Ein neuer Stab bekommt das Material, das das Werkzeug vorgibt -- sonst fehlte es ihm.
  const { gewaehlt, wert, setzen } = zugleich(a, z, 'linien', linien, (l, feld, zz) => {
    if (feld === 'querschnitt' && l.querschnitt && !l.material) l.material = vorgabeMaterial(a, zz);
  });
  const art = a.bs.art;
  const staebe = gewaehlt.filter((l) => l.querschnitt);
  const material = gemeinsam(staebe.map((l) => l.material));
  const inhalt = [
    cadZeile('Querschnitt', querschnittWahl(art, z, wert('querschnitt'), setzen('querschnitt'), material)),
    nurMitMaterialHinweis(art, z, material),
  ];
  if (staebe.length) {
    // «gemäss Querschnitt» nur, wenn jeder Querschnitt der gewählten Stäbe eines mitbringt.
    const bringt = staebe.every((l) => bringtMaterial(art, z.querschnitte.find((q) => q.kennung === l.querschnitt)));
    const { gelenk } = texte(art);
    inhalt.push(
      cadZeile('Material', materialWahl(art, z, bringt, material, setzen('material'))),
      a.bs.raum ? null : zugseitenzeile(a, z, linien),
      schalterzeile('Gelenk Anfang', jaNein(wert('gelenk_anfang'), setzen('gelenk_anfang'), `${gelenk} am Anfang`)),
      schalterzeile('Gelenk Ende', jaNein(wert('gelenk_ende'), setzen('gelenk_ende'), `${gelenk} am Ende`)),
    );
  }
  // Im Raum dreht β jede Linie -- mit einem Linienlager auch eine ohne Stab.
  if (a.bs.raum) inhalt.push(drehwinkelzeile(a, wert, setzen));
  const linienlager = systemkatalog(art, 'linienlager');
  const gebettet = gewaehlt.some((l) => linienlager.some(({ feld }) => l[feld] !== 'frei'));
  inhalt.push(el('button.cad-aufklapper', {
    type: 'button', text: `${a.bs.bettungOffen ? '▾' : '▸'} Bettung${gebettet ? ' · gesetzt' : ''}`,
    title: `Linienlager ${linienlager.map((x) => x.kurz).join(', ')}: fest oder gebettet`,
    on: { click: () => { a.bs.bettungOffen = !a.bs.bettungOffen; a.neuZeichnen(); } },
  }));
  if (a.bs.bettungOffen) inhalt.push(...lagerAnLinie(a, wert, setzen));
  if (gewaehlt.length === 1) inhalt.push(laengenzeile(a, z, gewaehlt[0]));
  inhalt.push(...meldungszeilen(a, linien));
  return {
    titel: gewaehlt.length === 1 ? a.adapter.name(a, gewaehlt[0].kennung) : `${gewaehlt.length} Linien`,
    inhalt: inhalt.filter(Boolean),
  };
}

// -- Lasten ------------------------------------------------------------------

/**
 * Die gewählten Lasten: ihr Lastfall und -- sind sie von derselben Art --
 * ihre Felder, mit «Var», wo sie sich unterscheiden. Ändert man den
 * Lastfall, zeigt die Zeichnung danach dessen Lasten -- sonst verschwände
 * die Last unter dem Zeiger.
 */
function lastEigenschaften(a, z, kennungen) {
  const da = kennungen.map((k) => lastVon(z, k));
  // Die Lasten hängen an ihren Linien, nicht in einer Liste -- darum nicht `zugleich`.
  const wert = (feld) => gemeinsam(da.map((d) => d.last[feld]));
  const setzen = (feld) => (w) => a.aendern((zz) => {
    for (const k of kennungen) {
      const neu = lastVon(zz, k);
      if (neu) neu.last[feld] = w;
    }
  });
  const amKnoten = gemeinsam(da.map((d) => Boolean(d.knoten)));
  const inhalt = [lastfallZeile(z, wert('lastfall'), (w) => {
    setzen('lastfall')(w);
    lastfallWaehlen(a, a.bs, w);
  }, 'Zu welchem Lastfall die Lasten gehören')];
  if (amKnoten !== VAR && wert('art') !== VAR) {
    inhalt.push(...lastFelder(a, wert, setzen, amKnoten ? 'knoten' : 'linie'));
  } else {
    inhalt.push(el('p.cad-hinweis-klein', { text: 'Verschiedene Arten – ihre Werte einzeln bearbeiten.' }));
  }
  if (da.length === 1) {
    inhalt.push(el('p.cad-info', { text: da[0].knoten ? `an ${da[0].knoten}` : `auf ${a.adapter.name(a, da[0].linie.kennung)}` }));
  }
  inhalt.push(...meldungszeilen(a, kennungen));
  const artText = (amKnoten ? knotenlastart : lastart)(a.bs.art, da[0].last.art).beschriftung;
  return {
    titel: da.length === 1 ? `${a.adapter.name(a, kennungen[0])} · ${artText}` : `${da.length} Lasten`,
    inhalt: inhalt.filter(Boolean),
  };
}
