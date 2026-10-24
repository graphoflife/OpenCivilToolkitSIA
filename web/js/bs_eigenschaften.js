/**
 * bs_eigenschaften.js -- das schwebende Fenster im Zeichenfenster eines
 * Balkensystems.
 *
 * Was ein Werkzeug als Nächstes anlegt (`neuEigenschaften`) und was gewählt
 * ist (`eigenschaften`): je Knoten, Linie oder Last ihre Felder. Sind
 * mehrere gewählt, ändert das Fenster alle zugleich -- was sie gemeinsam
 * haben, steht da, sonst «Var» (Benutzer, 2026-10-24).
 *
 * Vom Zeichenfenster kennt es nur `a`: den Zustand (`a.bs`), das Modell
 * (`a.modell`) und den Adapter (`a.adapter`), über den es die Zeichnung
 * liest, den Lastfall wählt, nach der Übersicht des Kerns fragt und Linien
 * umkehrt. So hängt `bs_zeichnung.js` an dieser Datei und nicht umgekehrt.
 * Gerechnet wird hier nichts.
 */

import { wahlBlock, wahlSchalter } from './bausteine.js';
import { katalog, lastart, lastVon, materialname, zugseite } from './bs_teile.js';
import { zahlText } from './cad_ansicht.js';
import { abstand, auswahlTeil } from './cad_modell.js';
import { auswahl, el, zahlfeld } from './dom.js';
import { ausVorlage } from './zustand.js';

/** Was ein Lager je Richtung kann -- die Feder heisst an einer Linie Bettung. */
const HALT = [
  { wert: 'frei', beschriftung: 'frei' },
  { wert: 'fest', beschriftung: 'fest' },
  { wert: 'feder', beschriftung: 'Feder' },
];

/** Das Material, das eine neue Linie bekommt: das gewählte, sonst das erste des Systems. */
export function vorgabeMaterial(a, z) {
  return a.bs.vorgaben.linie.material || z.stabmaterialien?.[0]?.kennung || '';
}

function zeile(beschriftung, eingabe, einheit = '') {
  return el('label.cad-zeile', {}, [
    el('span', { text: beschriftung }), eingabe, einheit ? el('span.einheit', { text: einheit }) : el('span'),
  ]);
}

/**
 * Eine Richtung des Lagers mit ihrem Schalter -- frei, fest oder Feder. Die
 * Beschriftung ist ein Zeichen (x, z, φ) und braucht nur eine schmale
 * Spalte. Ein «div», kein «label»: ein Klick auf das Zeichen löste sonst die
 * erste Stellung aus.
 */
function richtungszeile(beschriftung, schalter) {
  return el('div.cad-zeile.ist-richtung', {}, [el('span', { text: beschriftung }), schalter]);
}

/** Wie `zeile`, für einen Schalter -- ebenso ein «div», kein «label». */
function schalterzeile(beschriftung, schalter, zusatz = '') {
  return el('div.cad-zeile', {}, [
    el('span', { text: beschriftung }), schalter, zusatz ? el('span.einheit', { text: zusatz }) : el('span'),
  ]);
}

/**
 * Mehrere zugleich (Benutzer, 2026-10-24): was die gewählten gemeinsam
 * haben, steht da -- unterscheiden sie sich, steht «Var», und was man dann
 * wählt oder tippt, gilt für alle.
 */
const VAR = '*var*';

/** Der gemeinsame Wert der gewählten -- oder VAR. */
function gemeinsam(werte) {
  return werte.every((w) => w === werte[0]) ? werte[0] : VAR;
}

/** Die Stellungen eines Schalters oder einer Liste -- bei VAR mit «Var» vorneweg. */
function mitVar(werte, gewaehlt) {
  return gewaehlt === VAR ? [{
    wert: VAR, beschriftung: 'Var', titel: 'Die gewählten unterscheiden sich -- was man wählt, gilt für alle',
  }, ...werte] : werte;
}

/** Ein Zahlenfeld, auch für mehrere: bei VAR leer, mit «Var» darin. */
function zahlfeldMitVar({ wert, platzhalter, ...rest }) {
  return zahlfeld({ ...rest, wert: wert === VAR ? null : wert, platzhalter: wert === VAR ? 'Var' : platzhalter });
}

/** Ja oder nein als Schalter -- auch für mehrere, dann mit «Var». */
function jaNein(wert, setzen, titel) {
  return wahlSchalter({
    werte: mitVar([{ wert: true, beschriftung: 'ja' }, { wert: false, beschriftung: 'nein' }], wert),
    gewaehlt: wert === VAR ? VAR : Boolean(wert), setzen, titel,
  });
}

/** Ob ein Querschnitt ein Material mitbringt -- eine Platte oder Analyse; das sagt der Katalog. */
function bringtMaterial(q) {
  return Boolean(katalog().querschnittsarten?.find((x) => x.wert === q?.art)?.bringt_material);
}

/**
 * Die Querschnitte des Systems -- und «kein Stab»: dann ist die Linie nur
 * eine Linie, etwa für eine Bettung. Nimmt die Linie das Material ihres
 * Querschnitts, stehen nur die da, die eines mitbringen (Benutzer,
 * 2026-10-24) -- und der gewählte.
 */
function querschnittWahl(z, gewaehlt, setzen, material = '') {
  const nurMitMaterial = material === katalog().material_des_querschnitts;
  const werte = [
    { wert: '', beschriftung: '– kein Stab –' },
    ...(z.querschnitte || []).filter((q) => !nurMitMaterial || bringtMaterial(q) || q.kennung === gewaehlt)
      .map((q) => ({ wert: q.kennung, beschriftung: q.name || q.kennung })),
  ];
  return auswahl({ werte: mitVar(werte, gewaehlt), gewaehlt, titel: 'Die Querschnitte: Knopf «Querschnitte» unter der Zeichnung', beiAenderung: setzen });
}

/**
 * Das Material einer Linie: eines des Systems -- oder «gemäss Querschnitt»,
 * wenn ihr Querschnitt eines mitbringt (`bringt`: Platte, Analyse).
 */
function materialWahl(z, bringt, gewaehlt, setzen) {
  const eigenes = katalog().material_des_querschnitts;
  const werte = [
    ...(z.stabmaterialien || []).map((m) => ({ wert: m.kennung, beschriftung: materialname(m) })),
    ...(bringt || gewaehlt === eigenes ? [{ wert: eigenes, beschriftung: 'gemäss Querschnitt' }] : []),
  ];
  return auswahl({
    werte: gewaehlt === VAR || werte.some((x) => x.wert === gewaehlt) ? mitVar(werte, gewaehlt)
      : [{ wert: gewaehlt, beschriftung: '– Material wählen –' }, ...werte],
    gewaehlt,
    titel: 'Die Materialien: Knopf «Material» unter der Zeichnung -- «gemäss Querschnitt»: der Beton der Platte oder Analyse',
    beiAenderung: setzen,
  });
}

/**
 * Der Lastfall, in den das Werkzeug zeichnet und dessen Lasten die
 * Zeichnung zeigt -- eine Wahl aus dem Projekt, darum eine Liste.
 */
function lastfallWahl(a, z, gewaehlt, setzen, titel) {
  if (!z.lastfaelle.length) {
    return el('p.cad-hinweis-klein', { text: 'Für Lasten zuerst unter «Lastfälle» einen Lastfall anlegen.' });
  }
  return zeile('Lastfall', auswahl({
    werte: mitVar(z.lastfaelle.map((x) => ({ wert: x.kennung, beschriftung: x.name })), gewaehlt),
    gewaehlt, titel, beiAenderung: setzen,
  }));
}

/**
 * Die Felder einer Last: Richtung, Wert -- verteilt Anfang und Ende --,
 * die Stelle einer einzelnen in % der Linie, und ob eine verteilte je Meter
 * Projektion zählt. `last` ist die Last, die Vorgabe des Werkzeugs oder das
 * Gemeinsame mehrerer Lasten derselben Art (mit VAR, wo sie sich
 * unterscheiden); `setzen(feld, wert)` schreibt; `aufLinie`: liegt sie auf
 * einer Linie (sonst an einem Knoten oder noch nirgends).
 */
function lastFelder(last, setzen, { aufLinie = true, amKnoten = false } = {}) {
  const art = amKnoten ? { kraft: last.art === 'kraft', verteilt: false, einheit: last.art === 'kraft' ? 'kN' : 'kNm' }
    : lastart(last.art);
  const richtungen = amKnoten
    ? katalog().richtungen.filter((x) => katalog().knotenrichtungen.includes(x.wert))
    : katalog().richtungen;
  const wertFeld = amKnoten ? 'wert' : 'wert_a';
  return [
    art.kraft ? wahlBlock('Richtung', wahlSchalter({
      werte: mitVar(richtungen, last.richtung), gewaehlt: last.richtung, setzen: (w) => setzen('richtung', w),
      titel: 'Positiv in Pfeilrichtung: senkrecht nach unten, quer zur gestrichelten Faser, längs vom Anfang zum Ende',
      klasse: '.ist-wortlaut.ist-umbruch',
    })) : null,
    zeile(art.verteilt ? 'Anfang' : 'Wert', zahlfeldMitVar({
      wert: last[wertFeld], schritt: 5,
      titel: art.kraft ? 'Positiv in Pfeilrichtung' : 'Ein Moment positiv im Gegenuhrzeigersinn',
      beiAenderung: (w) => setzen(wertFeld, w),
    }), art.einheit),
    art.verteilt ? zeile('Ende', zahlfeldMitVar({
      wert: last.wert_b, schritt: 5, leer: null, platzhalter: 'wie Anfang',
      titel: 'Wert am Ende der Linie -- leer: wie am Anfang', beiAenderung: (w) => setzen('wert_b', w),
    }), art.einheit) : null,
    !art.verteilt && aufLinie ? zeile('Stelle', zahlfeldMitVar({
      wert: last.stelle, schritt: 5, min: 0, max: 100,
      titel: 'Wo die Last steht: in % der Linie ab ihrem Anfang', beiAenderung: (w) => setzen('stelle', w),
    }), '%') : null,
    art.verteilt && art.kraft && ['senkrecht', 'waagrecht'].includes(last.richtung) && aufLinie
      ? schalterzeile('projiziert', jaNein(last.projiziert, (w) => setzen('projiziert', w),
        'Senkrecht und waagrecht je Meter Projektion statt je Meter Stab'), 'je m Projektion') : null,
  ];
}

/** Die Felder für das, was ein Werkzeug als Nächstes anlegt. */
export function neuEigenschaften(a, werkzeug) {
  const z = a.adapter.zeichnung();
  const neu = () => a.neuZeichnen();
  let inhalt = [];
  if (werkzeug === 'linie') {
    const v = a.bs.vorgaben.linie;
    inhalt = [
      zeile('Querschnitt', querschnittWahl(z, v.querschnitt, (w) => { v.querschnitt = w; neu(); }, vorgabeMaterial(a, z))),
      v.querschnitt ? zeile('Material', materialWahl(z, bringtMaterial(z.querschnitte.find((q) => q.kennung === v.querschnitt)),
        vorgabeMaterial(a, z), (w) => { v.material = w; neu(); })) : null,
    ];
  } else if (werkzeug === 'last') {
    const v = a.bs.vorgaben.last;
    // Der Lastfall steht oben neben «Last»; hier nur, wenn keiner gewählt ist.
    inhalt = [
      a.adapter.lastfall() ? null : el('p.cad-hinweis-klein', {
        text: 'Kein Lastfall gewählt -- oben neben «Last» einen wählen.',
      }),
      wahlBlock('Art', wahlSchalter({
        werte: katalog().lastarten.map((x) => ({ wert: x.wert, beschriftung: x.beschriftung, titel: `${x.beschriftung} in ${x.einheit}` })),
        gewaehlt: v.art, setzen: (w) => { v.art = w; neu(); }, klasse: '.ist-wortlaut.ist-umbruch',
        titel: 'Verteilt liegt eine Last auf der ganzen Linie; einzeln dort, wo geklickt wird, oder an einem Knoten',
      })),
      ...lastFelder(v, (feld, w) => { v[feld] = w; neu(); }, { aufLinie: false }),
    ];
  }
  return {
    inhalt: [el('div.cad-neu-titel', { text: 'Neu' }), ...inhalt.filter(Boolean)],
    schluessel: JSON.stringify([werkzeug, a.bs.vorgaben, a.adapter.lastfall()]),
  };
}

export function eigenschaften(a) {
  const z = a.adapter.zeichnung();
  const kennungen = [...a.auswahl].map((s) => auswahlTeil(s).kennung);
  const lasten = kennungen.filter((k) => lastVon(z, k));
  const knoten = kennungen.filter((k) => z.knoten.some((x) => x.kennung === k));
  const linien = kennungen.filter((k) => z.linien.some((x) => x.kennung === k));
  const schluessel = JSON.stringify([a.adapter.lastfall(), Boolean(a.adapter.passendeUebersicht()), a.bs.bettungOffen]);
  if (lasten.length && lasten.length === kennungen.length) return { ...lastEigenschaften(a, z, lasten), schluessel };
  if ((knoten.length && linien.length) || lasten.length) {
    return {
      titel: `${kennungen.length} gewählt`,
      inhalt: [el('p.cad-hinweis-klein', { text: 'Verschiedenes zugleich -- verschieben mit V, löschen mit Entf.' })],
      schluessel,
    };
  }
  if (knoten.length) return { ...knotenEigenschaften(a, z, knoten), schluessel };
  if (linien.length) return { ...linienEigenschaften(a, z, linien), schluessel };
  return { titel: '', inhalt: [] };
}

function meldungszeilen(a, kennungen) {
  const u = a.adapter.passendeUebersicht();
  return (u?.meldungen || []).filter((m) => m.elemente.some((k) => kennungen.includes(k)))
    .map((m) => el(m.fehler ? 'p.cad-meldung' : 'p.cad-hinweis-klein', { text: m.text }));
}


// -- Knoten ------------------------------------------------------------------

/** Welche Vorwahl ein Lager trifft -- 'kein', eine der Lagerarten oder 'eigen'. */
function lagerart(lager) {
  if (!lager) return 'kein';
  const treffer = katalog().lagerarten.find((x) => x.x === lager.x && x.z === lager.z && x.phi === lager.phi);
  return treffer ? treffer.wert : 'eigen';
}

function lagerSetzen(a, z, knoten, art) {
  z.lager = z.lager.filter((l) => l.knoten !== knoten || art !== 'kein');
  if (art === 'kein') return;
  let lager = z.lager.find((l) => l.knoten === knoten);
  if (!lager) {
    lager = { ...ausVorlage('lager'), kennung: a.modell.naechsteKennung(z, 'A'), knoten };
    z.lager.push(lager);
  }
  const vorwahl = katalog().lagerarten.find((x) => x.wert === art);
  if (vorwahl) Object.assign(lager, { x: vorwahl.x, z: vorwahl.z, phi: vorwahl.phi });
}

function lagerFelder(a, z, knoten) {
  const lager = knoten.map((k) => z.lager.find((l) => l.knoten === k) || null);
  const art = gemeinsam(lager.map(lagerart));
  const setzen = (w) => a.aendern((zz) => { for (const k of knoten) lagerSetzen(a, zz, k, w); });
  const werte = [
    { wert: 'kein', beschriftung: 'kein', titel: 'Kein Lager' },
    ...katalog().lagerarten.map((x) => ({ wert: x.wert, beschriftung: x.wert })),
    { wert: 'eigen', beschriftung: 'je Richtung', titel: 'Je Richtung frei, fest oder eine Feder' },
  ];
  const zeilen = [wahlBlock('Lager', wahlSchalter({
    werte: mitVar(werte, art), gewaehlt: art, setzen, klasse: '.ist-umbruch', titel: 'Lager des Knotens',
  }))];
  // Je Richtung nur, wenn alle gewählten ein Lager haben -- sonst stünde da,
  // was nur für einige gilt.
  if (lager.some((l) => !l)) return zeilen;
  const einheiten = katalog().federeinheiten;
  const richtungSetzen = (feld) => (wert) => a.aendern((zz) => {
    for (const l of zz.lager) if (knoten.includes(l.knoten)) l[feld] = wert;
  });
  for (const [feld, name] of [['x', 'x'], ['z', 'z'], ['phi', 'φ']]) {
    const halt = gemeinsam(lager.map((l) => l[feld]));
    zeilen.push(richtungszeile(name, wahlSchalter({
      werte: mitVar(HALT, halt), gewaehlt: halt, setzen: richtungSetzen(feld), titel: `Halt in ${name}`,
    })));
    if (halt === 'feder') {
      zeilen.push(zeile(`  k_${name}`, zahlfeldMitVar({
        wert: gemeinsam(lager.map((l) => l[`k_${feld}`])), schritt: 1000, min: 0,
        titel: `Federsteifigkeit in ${name}`, beiAenderung: richtungSetzen(`k_${feld}`),
      }), einheiten[`k_${feld}`] || ''));
    }
  }
  return zeilen;
}

function knotenEigenschaften(a, z, knoten) {
  const gewaehlt = z.knoten.filter((x) => knoten.includes(x.kennung));
  // Eine getippte Lage gilt für alle gewählten -- so stehen sie danach in
  // einer Flucht.
  const lageSetzen = (feld) => (w) => a.aendern((zz) => {
    for (const kennung of knoten) {
      const da = zz.knoten.find((x) => x.kennung === kennung);
      if (da) a.modell.verschieben(zz, new Set([kennung]), feld === 'x' ? [w - da.x, 0] : [0, w - da.z]);
    }
  });
  const inhalt = ['x', 'z'].map((feld) => zeile(feld, zahlfeldMitVar({
    wert: gemeinsam(gewaehlt.map((k) => k[feld])), schritt: a.raster, beiAenderung: lageSetzen(feld),
  }), 'm'));
  inhalt.push(...lagerFelder(a, z, knoten));
  const u = a.adapter.passendeUebersicht();
  for (const k of knoten) {
    if (u?.unbestimmt?.includes(k)) inhalt.push(el('p.cad-hinweis-klein', { text: `${k}: ${u.unbestimmt_text}.` }));
  }
  inhalt.push(...meldungszeilen(a, knoten));
  return {
    titel: knoten.length === 1 ? `Knoten ${knoten[0]}` : `${knoten.length} Knoten`,
    inhalt: inhalt.filter(Boolean),
  };
}

// -- Linien ------------------------------------------------------------------

function lagerAnLinie(a, linien, wert) {
  const einheiten = katalog().federeinheiten;
  const setzen = (feld) => (w) => a.aendern((zz) => {
    for (const l of zz.linien) if (linien.includes(l.kennung)) l[feld] = w;
  });
  const werte = HALT.map((x) => (x.wert === 'feder' ? { ...x, beschriftung: 'Bettung' } : x));
  const zeilen = [];
  for (const [feld, name, titel] of [
    ['quer', 'Lager quer', 'Quer zur Linie, auf der Seite der gestrichelten Faser: fest -- der Stab biegt sich nicht --, oder gebettet'],
    ['laengs', 'Lager längs', 'Längs der Linie: fest oder gebettet']]) {
    const halt = wert(feld);
    zeilen.push(wahlBlock(name, wahlSchalter({ werte: mitVar(werte, halt), gewaehlt: halt, titel, setzen: setzen(feld) })));
    if (halt === 'feder') {
      zeilen.push(zeile(`  k_${feld === 'quer' ? '⊥' : '∥'}`, zahlfeldMitVar({
        wert: wert(`k_${feld}`), schritt: 1000, min: 0, titel: 'Bettungsziffer je Meter Stab',
        beiAenderung: setzen(`k_${feld}`),
      }), einheiten[`k_${feld}`] || ''));
    }
  }
  return zeilen;
}

/**
 * Die Zugseite der gewählten Linien als Schalter -- solange sie alle
 * senkrecht oder alle nicht senkrecht liegen. Umschalten kehrt eine Linie
 * im Kern um: die Faser wechselt die Seite, die Lasten bleiben, wo sie
 * wirken, und die Gelenke an ihren Knoten.
 */
function zugseitenzeile(a, z, linien) {
  const lagen = a.modell.lagen(z);
  const seiten = new Map(z.linien.filter((l) => linien.includes(l.kennung))
    .map((l) => [l.kennung, zugseite(lagen.get(l.von), lagen.get(l.bis))]));
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
 * Eine Linie: Querschnitt -- «kein Stab» heisst nur eine Linie --, beim
 * Stab das Material, die Zugseite und die Gelenke. Die Bettung steht
 * eingeklappt darunter: sie braucht man selten (Benutzer, 2026-10-23).
 */
function linienEigenschaften(a, z, linien) {
  const gewaehlt = z.linien.filter((x) => linien.includes(x.kennung));
  const wert = (feld) => gemeinsam(gewaehlt.map((l) => l[feld]));
  const setzen = (feld) => (w) => a.aendern((zz) => {
    for (const l of zz.linien) {
      if (!linien.includes(l.kennung)) continue;
      l[feld] = w;
      // Ein neuer Stab bekommt das Material, das das Werkzeug vorgibt -- sonst fehlte es ihm.
      if (feld === 'querschnitt' && w && !l.material) l.material = vorgabeMaterial(a, zz);
    }
  });
  const staebe = gewaehlt.filter((l) => l.querschnitt);
  const material = gemeinsam(staebe.map((l) => l.material));
  const inhalt = [zeile('Querschnitt', querschnittWahl(z, wert('querschnitt'), setzen('querschnitt'), material))];
  if (staebe.length) {
    // «gemäss Querschnitt» nur, wenn jeder Querschnitt der gewählten Stäbe eines mitbringt.
    const bringt = staebe.every((l) => bringtMaterial(z.querschnitte.find((q) => q.kennung === l.querschnitt)));
    inhalt.push(
      zeile('Material', materialWahl(z, bringt, material, setzen('material'))),
      zugseitenzeile(a, z, linien),
      schalterzeile('Gelenk Anfang', jaNein(wert('gelenk_anfang'), setzen('gelenk_anfang'), 'Kein Moment am Anfang')),
      schalterzeile('Gelenk Ende', jaNein(wert('gelenk_ende'), setzen('gelenk_ende'), 'Kein Moment am Ende')),
    );
  }
  const gebettet = gewaehlt.some((l) => l.quer !== 'frei' || l.laengs !== 'frei');
  inhalt.push(el('button.cad-aufklapper', {
    type: 'button', text: `${a.bs.bettungOffen ? '▾' : '▸'} Bettung${gebettet ? ' · gesetzt' : ''}`,
    title: 'Linienlager quer und längs: fest oder gebettet',
    on: { click: () => { a.bs.bettungOffen = !a.bs.bettungOffen; a.neuZeichnen(); } },
  }));
  if (a.bs.bettungOffen) inhalt.push(...lagerAnLinie(a, linien, wert));
  if (gewaehlt.length === 1) {
    const [e] = gewaehlt;
    const lagen = a.modell.lagen(z);
    const [p, q] = [lagen.get(e.von), lagen.get(e.bis)];
    if (p && q) inhalt.push(el('p.cad-info', { text: `L = ${zahlText(abstand(p, q), 3)} m · ${e.von} → ${e.bis}` }));
  }
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
  const setzen = (feld, wert) => a.aendern((zz) => {
    for (const k of kennungen) {
      const neu = lastVon(zz, k);
      if (neu) neu.last[feld] = wert;
    }
  });
  const amKnoten = gemeinsam(da.map((d) => Boolean(d.knoten)));
  const art = gemeinsam(da.map((d) => d.last.art));
  const inhalt = [lastfallWahl(a, z, gemeinsam(da.map((d) => d.last.lastfall)), (w) => {
    setzen('lastfall', w);
    a.adapter.lastfallWaehlen(w);
  }, 'Zu welchem Lastfall die Lasten gehören')];
  if (amKnoten !== VAR && art !== VAR) {
    const felder = Object.fromEntries(Object.keys(da[0].last)
      .map((feld) => [feld, gemeinsam(da.map((d) => d.last[feld]))]));
    inhalt.push(...lastFelder(felder, setzen, { amKnoten }));
  } else {
    inhalt.push(el('p.cad-hinweis-klein', { text: 'Verschiedene Arten -- ihre Werte einzeln bearbeiten.' }));
  }
  if (da.length === 1) {
    inhalt.push(el('p.cad-info', { text: da[0].knoten ? `an ${da[0].knoten}` : `auf ${a.adapter.name(a, da[0].linie.kennung)}` }));
  }
  inhalt.push(...meldungszeilen(a, kennungen));
  const artText = amKnoten ? (da[0].last.art === 'moment' ? 'Moment' : 'Kraft') : lastart(da[0].last.art).beschriftung;
  return {
    titel: da.length === 1 ? `${a.adapter.name(a, kennungen[0])} · ${artText}` : `${da.length} Lasten`,
    inhalt: inhalt.filter(Boolean),
  };
}
