/**
 * balkensystem.js -- Mittlere Tafel: Eingaben eines Balkensystems, eben
 * oder im Raum.
 *
 * Von oben nach unten:
 *
 *     System          Bezeichnung, Zeichnung samt Liste, Beschreibung
 *     Eingaben        fünf Knöpfe, je mit einem Fenster (`KAPITEL`):
 *                     Material -- die Materialien als Tabelle --,
 *                     Querschnitte -- je einer eine Zeile mit Bild, jeder
 *                     mit eigenem Fenster --, Lastfälle, Lastkombinationen
 *                     und die Statik-Analyse -- die Diagramme rechts, je
 *                     Zeile ein Fall und eine Grösse, wie in der
 *                     Spannung-Dehnung-Analyse
 *
 * Gerechnet wird nichts: die Kennwerte der Querschnitte, die Steifigkeiten
 * und alles Weitere bildet der Kern; hier stehen nur seine Zahlen.
 *
 * Das 2D- und das 3D-Balkensystem teilen sich diese Tafel. Was eine Art
 * anders hat -- die Kennwerte eines Querschnitts und eines Materials, die
 * Linienlager, die Diagramme --, sagt ihr Katalog (bs_teile.js); wie sie es
 * erklärt, auch ihre Vorzeichen und deren kleines Bild, bs_texte.js.
 */

import { formelText } from './achsen.js';
import {
  bauteilliste, bezeichnung, erklaerung, feld, materialliste, namensfeld, panel, wahlBlock, wahlSchalter,
} from './bausteine.js';
import {
  knotenlastart, lagertext, lastart, lastrichtung, materialname, systemart, systemkatalog, systemliste,
} from './bs_teile.js';
import { texte } from './bs_texte.js';
import { zeichenbereich } from './bs_zeichnung.js';
import { listengruppen, listenzeilen, meldungsliste } from './cad_app.js';
import {
  auswahl, el, melden, svgEl, undListe, zahlfeld,
} from './dom.js';
import { fenster, fensterOeffnen } from './fenster.js';
import { kapitelFenster, kapitelPanel, zeilenstand } from './kapitel.js';
import { diagrammzeilen, lastenKapitel, lastfallWaehlen } from './lastfaelle.js';
import { rechenwahlZeile } from './nachweise.js';
import { plattenmaterialien } from './plattenkapitel.js';
import { werkstoffeVon } from './qa_zeichnung.js';
import {
  ausVorlage, eintragAendern, eintragVon, feldangabe, istSandbox, katalog, kennwertId,
  naechsterName, neueKennung, zustand,
} from './zustand.js';

// ===========================================================================
// Unter der Zeichnung
// ===========================================================================

/**
 * Meldungen des Kerns und je Linie, Lager und Last eine Zeile (cad_app.js)
 * -- ein Klick wählt im Fenster, ein Lager über seinen Knoten; bei einer
 * Last zeigt die Zeichnung dann ihren Lastfall.
 */
function uebersicht(a) {
  const z = eintragVon(a.bs.kennung);
  if (!z) return [];
  const { art } = a.bs;
  const zeile = listenzeilen(a);
  const name = (q) => z.querschnitte.find((x) => x.kennung === q)?.name || q || '–';
  // Das Material eines Stabs ist eines des Systems -- es heisst, wie es im
  // Fenster «Material» heisst. Bis 2026-11-19 stand hier bei jedem «–»: es
  // wurde unter den Materialien des Projekts gesucht.
  const stoff = (m) => {
    if (m === systemkatalog(art, 'material_des_querschnitts')) return 'gemäss Querschnitt';
    const da = (z.stabmaterialien || []).find((x) => x.kennung === m);
    return da ? materialname(da) : '–';
  };
  const linienlager = systemkatalog(art, 'linienlager');
  const linien = z.linien.map((l) => {
    const gelenke = [l.gelenk_anfang ? 'Anfang' : '', l.gelenk_ende ? 'Ende' : ''].filter(Boolean);
    const lager = linienlager.filter((x) => l[x.feld] !== 'frei')
      .map((x) => `${x.kurz} ${l[x.feld] === 'feder' ? 'gebettet' : 'fest'}`);
    return zeile({
      kennung: l.kennung,
      was: `${l.von} → ${l.bis}`,
      wert: [
        l.querschnitt ? `${name(l.querschnitt)} · ${stoff(l.material)}` : 'kein Stab',
        // Der Drehwinkel β einer Linie im Raum, wenn sie gedreht ist.
        l.drehung ? `β = ${l.drehung}°` : '',
        gelenke.length ? `Gelenk ${gelenke.join(', ')}` : '',
        ...lager,
      ].filter(Boolean).join(' · '),
    });
  });
  const lager = z.lager.map((l) => zeile({ kennung: l.kennung, was: `an ${l.knoten}`, wert: lagertext(art, l) }));
  const lastfall = (lf) => z.lastfaelle.find((x) => x.kennung === lf)?.name || lf;
  const lastzeile = (last, wo, text) => zeile({
    kennung: last.kennung, was: wo, wert: `${text} · ${lastfall(last.lastfall)}`,
    vorher: () => lastfallWaehlen(a, a.bs, last.lastfall),
  });
  // Die Richtung einer Kraft -- im Raum auch die Achse eines Moments; in
  // der Ebene dreht jedes Moment um dieselbe.
  const richtung = (last, kraft) => (kraft || a.bs.raum
    ? ` · ${lastrichtung(art, last.richtung)?.beschriftung || last.richtung}` : '');
  const lasten = [
    ...z.linien.flatMap((l) => l.lasten.map((last) => {
      const la = lastart(art, last.art);
      const wert = last.wert_b === null || last.wert_b === undefined ? `${last.wert_a}` : `${last.wert_a} … ${last.wert_b}`;
      const stelle = la.verteilt ? '' : ` bei ${last.stelle} %`;
      return lastzeile(last, `auf ${l.kennung}`, `${la.beschriftung} ${wert} ${la.einheit}${stelle}${richtung(last, la.kraft)}`);
    })),
    ...z.knotenlasten.map((p) => {
      const la = knotenlastart(art, p.art);
      return lastzeile(p, `an ${p.knoten}`, `${la.beschriftung} ${p.wert} ${la.einheit}${richtung(p, la.kraft)}`);
    }),
  ];
  return [meldungsliste(a), ...listengruppen(a, [['Linien', linien], ['Lager', lager], ['Lasten', lasten]])];
}

// ===========================================================================
// System
// ===========================================================================

function systemGruppe(system) {
  const art = systemart(system.kennung);
  const t = texte(art);
  const aendern = (veraenderer) => eintragAendern(system.kennung, veraenderer);
  return panel({ schluessel: `${art}/System`, titel: 'System', zusatz: t.zusatz, breit: true }, [
    // Der Lastfall der Zeichnung steht in ihrer Leiste, neben «Last».
    bezeichnung(system, aendern, erklaerung(t.hilfe.vorzeichen.zeilen, t.hilfe.vorzeichen.formel)),
    zeichenbereich(system, uebersicht),
    el('div.unterkapitel', {}, [
      el('details.bs-vorzeichen-huelle', {}, [el('summary', { text: 'Vorzeichen' }), t.vorzeichenbild()]),
      el('div.beschreibung', {}, [
        el('label', { text: 'Beschreibung' }),
        el('textarea', {
          rows: 2, value: system.beschreibung || '',
          on: { change: (e) => aendern((s) => { s.beschreibung = e.target.value; }) },
        }),
      ]),
    ]),
  ]);
}

// ===========================================================================
// Materialien
// ===========================================================================

/** Wie weit ein Pfeil im Zahlenfeld eines eigenen Materials springt -- je Kennwert. */
const SCHRITT = { E: 1000, rho: 50, G: 1000 };

/**
 * Die Materialien der Stäbe als Tabelle (Benutzer, 2026-10-24): je Zeile
 * ein Beton oder Baustahl des Projekts -- seine Kennwerte gesperrt,
 * gerechnet vom Kern -- oder ein eigenes mit Kennwerten von Hand: E und ρ,
 * im Raum dazu G. Betonstahl steht nicht zur Wahl: aus ihm ist kein Stab.
 * Daneben, welche Linien es nehmen.
 */
function materialienInhalt(system) {
  const art = systemart(system.kennung);
  const aendern = (veraenderer) => eintragAendern(system.kennung, veraenderer);
  // Je Art des Projekts, aus der ein Stab sein kann, die Kennwerte, die er nimmt.
  const kennwerte = systemkatalog(art, 'stabkennwerte');
  const spalten = systemkatalog(art, 'materialkennwerte');
  const klasse = systemkatalog(art, 'klassen', 'material');
  const titel = (stoffart) => katalog('materialarten', stoffart, 'titel');
  const stoffe = (stoffart) => zustand.projekt.materialien.filter((m) => m.art === stoffart);
  const angabe = (feldname) => feldangabe(klasse, feldname);
  const gesperrt = (stoff, kurz) => {
    const wert = stoff ? zustand.loesung?.werte?.[kennwertId(stoff, kennwerte[stoff.art][kurz])] : null;
    return el('span.bs-gesperrt', { text: wert ? wert.wert : '–', title: 'Vom Material des Projekts – zu ändern in der App «Materialien»' });
  };
  const ausDemProjekt = (m, setzen) => {
    const stoff = stoffe(m.art).find((s) => s.kennung === m.stoff);
    return [
      materialliste({
        art: m.art, gewaehlt: m.stoff, titel: `Ein ${titel(m.art)} des Projekts`, setzen: setzen('stoff'),
      }),
      el('span.bs-material-art', { text: titel(m.art) }),
      ...spalten.map((k) => gesperrt(stoff, k.kurz)),
    ];
  };
  const eigenes = (m, setzen) => [
    namensfeld({
      wert: m.name, setzen: setzen('name'), titel: 'Name des Materials – so steht es im Bericht',
    }),
    el('span.bs-material-art', { text: 'eigenes' }),
    ...spalten.map((k) => zahlfeld({
      wert: m[k.kurz], schritt: SCHRITT[k.kurz], angabe: angabe(k.kurz), titel: `${k.beschreibung} von Hand`,
      beiAenderung: setzen(k.kurz),
    })),
  ];
  const zeile = (m, i) => {
    const setzen = (feldname) => (wert) => aendern((s) => { s.stabmaterialien[i][feldname] = wert; });
    const benutzt = system.linien.filter((l) => l.material === m.kennung).map((l) => l.kennung);
    const weg = () => {
      if (benutzt.length) {
        melden(`«${materialname(m)}» trägt noch ${benutzt.join(', ')}.`, true);
        return;
      }
      aendern((s) => { s.stabmaterialien.splice(i, 1); });
    };
    const zellen = m.art === 'eigen' ? eigenes(m, setzen) : ausDemProjekt(m, setzen);
    return el('tr', {}, [
      ...zellen.map((z) => el('td', {}, [z])),
      el('td.bs-benutzt', { text: benutzt.join(', ') || '–', title: benutzt.length ? `trägt ${benutzt.join(', ')}` : 'trägt keinen Stab' }),
      el('td', {}, [el('button.weg', { type: 'button', text: '×', title: 'Material löschen', on: { click: weg } })]),
    ]);
  };
  const neu = (stoffart) => aendern((s) => {
    s.stabmaterialien.push(ausVorlage(klasse, {
      kennung: neueKennung(s, 'M', s.stabmaterialien), art: stoffart,
      ...(stoffart === 'eigen' ? { name: naechsterName('Material', s.stabmaterialien) }
        : { stoff: stoffe(stoffart)[0]?.kennung || '' }),
    }));
  });
  const kopf = [['Material'], ['Art'], ...spalten.map((k) => [k.zeichen, angabe(k.kurz).einheit]), ['trägt'], ['']];
  const fehlt = (stoffart) => `Im Projekt gibt es keinen ${titel(stoffart)} – anlegen in der App «Materialien»`;
  return [
    system.stabmaterialien.length ? el('div.tabelle-huelle', {}, [el('table.bs-materialien', {}, [
      el('thead', {}, [el('tr', {}, kopf.map(([text, einheit]) => el('th', {}, [
        text, einheit ? el('span.einheit', { text: ` ${einheit}` }) : null,
      ].filter(Boolean))))]),
      el('tbody', {}, system.stabmaterialien.map(zeile)),
    ])]) : el('p.bs-leer', { text: 'Noch kein Material – ein Stab braucht eines.' }),
    el('div.bs-knopfreihe', {}, [
      ...Object.keys(kennwerte).map((stoffart) => el('button.knopf.knopf-klein', {
        type: 'button', text: `+ ${titel(stoffart)}`,
        title: stoffe(stoffart).length ? `Ein ${titel(stoffart)} aus dem Projekt` : fehlt(stoffart),
        disabled: !stoffe(stoffart).length, on: { click: () => neu(stoffart) },
      })),
      el('button.knopf.knopf-klein', {
        type: 'button', text: '+ eigenes Material', title: `${undListe(spalten.map((k) => k.beschreibung))} von Hand`,
        on: { click: () => neu('eigen') },
      }),
    ]),
    // Warum ein Knopf gesperrt ist, sichtbar -- der Tooltip allein fehlt
    // auf dem Tablet (bis 2026-11-19).
    ...Object.keys(kennwerte).filter((stoffart) => !stoffe(stoffart).length)
      .map((stoffart) => el('p.hinweis', { text: `${fehlt(stoffart)}.` })),
  ];
}

// ===========================================================================
// Querschnitte
// ===========================================================================

/** Die Reihe eines Profils -- «HEB 300» gehört zu HEB. */
function reiheVon(art, profil) {
  const reihen = systemkatalog(art, 'profilreihen');
  return reihen.find((r) => r.profile.includes(profil)) || reihen[0];
}

/** Die Kennwerte eines Querschnitts in Worten: «A und I», im Raum «A, I_y, I_z und I_T». */
const kennwertnamen = (art) => undListe(systemkatalog(art, 'kennwerte').map((k) => k.kurz));

/**
 * Die Materialien der Platte oder Querschnittsanalyse, aus der ein
 * Querschnitt kommt -- für sie wählt E_eq seine Werte, wie in ihren eigenen
 * Kapiteln. Ist noch keine gewählt, sagt es die Zeile.
 */
function werkstoffeDerQuelle(q) {
  const kennung = q[q.art];
  if (!kennung) {
    const welche = q.art === 'platte' ? 'Platte' : 'Querschnittsanalyse';
    return { materialien: [], leer: `Noch keine ${welche} gewählt.` };
  }
  return q.art === 'platte' ? { materialien: plattenmaterialien(eintragVon(kennung)) } : werkstoffeVon(kennung);
}

/**
 * Was der Kern zu einem Querschnitt gerechnet hat: seine Kennwerte, wie der
 * Katalog sie nennt -- und sein eigenes E --, oder nichts.
 */
function kennwerte(system, q) {
  const art = systemart(system.kennung);
  const zuordnung = zustand.loesung?.zuordnung?.[systemliste(art)]?.[system.kennung];
  const ids = zuordnung?.querschnitte?.[q.kennung];
  const werte = zustand.loesung?.werte || {};
  if (!ids) return null;
  const text = (id) => (werte[id] ? `${werte[id].wert} ${werte[id].einheit}` : '–');
  const E = zuordnung.module?.[q.kennung];
  return [...systemkatalog(art, 'kennwerte').map((k) => `${k.kurz} = ${text(ids[k.kurz])}`),
    ...(E ? [`E = ${text(E)}`] : [])].join(' · ');
}

/** Was der Kern zu einem Querschnitt meldet -- was ihm fehlt, oder ein Hinweis. */
function meldungenZu(system, q) {
  return (zustand.loesung?.zeichendaten?.[system.kennung]?.uebersicht?.meldungen || [])
    .filter((m) => m.elemente.includes(q.kennung));
}

/**
 * Ein kleines Bild eines Querschnitts: sein Umriss vom Kern, in die Box
 * eingepasst -- Aussparungen gerade-ungerade gefüllt. Ohne Umriss bei
 * Kennwerten von Hand ihre Namen, je zwei auf einer Zeile -- in der Ebene
 * «A, I», im Raum «A, I_y» und «I_z, I_T» --, sonst ein Fragezeichen: ein
 * Querschnitt, der nicht geht, oder noch ohne Platte oder Analyse.
 */
function umrissBild(system, q, breite, hoehe) {
  const polygone = zustand.loesung?.zeichendaten?.[system.kennung]?.umrisse?.[q.kennung] || [];
  const svg = svgEl('svg', { viewBox: `0 0 ${breite} ${hoehe}`, width: breite, height: hoehe, class: 'bs-umriss', 'aria-hidden': 'true' });
  const punkte = polygone.flat();
  if (!punkte.length) {
    const namen = q.art === 'kennwerte'
      ? systemkatalog(systemart(system.kennung), 'kennwerte').map((k) => k.kurz) : ['?'];
    const zeilen = [];
    for (let i = 0; i < namen.length; i += 2) zeilen.push(namen.slice(i, i + 2).join(', '));
    zeilen.forEach((zeile, i) => svg.append(formelText(svgEl('text', {
      x: breite / 2, y: hoehe / 2 + 4 + (i - (zeilen.length - 1) / 2) * 13, class: 'bs-umriss-text',
    }), zeile)));
    return svg;
  }
  const ys = punkte.map((p) => p[0]);
  const zs = punkte.map((p) => p[1]);
  const [y0, y1, z0, z1] = [Math.min(...ys), Math.max(...ys), Math.min(...zs), Math.max(...zs)];
  const rand = 3;
  const m = Math.min((breite - 2 * rand) / Math.max(y1 - y0, 1e-9), (hoehe - 2 * rand) / Math.max(z1 - z0, 1e-9));
  const [oy, oz] = [(breite - m * (y1 - y0)) / 2, (hoehe - m * (z1 - z0)) / 2];
  const d = polygone.map((poly) => `M${poly.map(([y, z]) => `${(oy + m * (y - y0)).toFixed(1)} ${(hoehe - oz - m * (z - z0)).toFixed(1)}`).join(' L')} Z`).join(' ');
  svg.append(svgEl('path', { d, 'fill-rule': 'evenodd', class: 'bs-umriss-flaeche' }));
  return svg;
}

/** Die Masse einer Vorlage mit ihren Vorgaben, aus dem Katalog. */
function vorgabenDer(art, schluessel) {
  return Object.fromEntries((systemkatalog(art, 'vorlagen').find((v) => v.schluessel === schluessel)?.masse || [])
    .map((m) => [m.schluessel, m.vorgabe]));
}

/** Der kurze Name der Art eines Querschnitts -- wie in ihrem Schalter, aus dem Katalog. */
const artKurz = (art, q) => systemkatalog(art, 'querschnittsarten').find((x) => x.wert === q.art)?.kurz || q.art;

/**
 * Woher ein Querschnitt kommt, in Worten -- mit den Massen einer Vorlage;
 * ein Profil in der Ebene mit der Achse, um die es sich biegt. Im Raum
 * biegt es sich um beide.
 */
function herkunftText(art, q) {
  if (q.art === 'vorlage') {
    const vorlage = systemkatalog(art, 'vorlagen').find((v) => v.schluessel === q.vorlage);
    const masse = (vorlage?.masse || []).map((m) => `${m.symbol} ${q.masse?.[m.schluessel] ?? m.vorgabe}`);
    return `${vorlage?.name || q.vorlage} · ${masse.join(' · ')} mm`;
  }
  if (q.art === 'profil') return q.achse ? `${q.profil} · um ${q.achse}` : q.profil;
  if (q.art === 'kennwerte') return 'Kennwerte von Hand';
  const liste = q.art === 'platte' ? zustand.projekt.querschnitte : (zustand.projekt.querschnittsanalysen || []);
  // Die Platte steht in «platte», die Analyse in «analyse»: Felder wie ihre Art.
  const bezug = liste.find((x) => x.kennung === q[q.art]);
  return `${artKurz(art, q)} ${bezug ? `«${bezug.name}»` : '– nicht gewählt –'}`;
}

/** Der Schlüssel des Fensters eines Querschnitts. */
const fensterVon = (kennung) => `querschnitt:${kennung}`;

/**
 * Ein Querschnitt als kompakte Zeile (Benutzer, 2026-10-24): links das
 * Bild -- ein Klick öffnet ihn im Fenster --, daneben Name, A und I und
 * woher er kommt.
 */
function querschnittZeile(system, q, i) {
  const art = systemart(system.kennung);
  const benutzt = system.linien.filter((l) => l.querschnitt === q.kennung).map((l) => l.kennung);
  // Ohne Kennwerte sagt die Meldung des Kerns, was dem Querschnitt fehlt.
  const werte = kennwerte(system, q);
  const fehler = meldungenZu(system, q).find((m) => m.fehler);
  const weg = () => {
    if (benutzt.length) {
      melden(`«${q.name}» trägt noch ${benutzt.join(', ')}.`, true);
      return;
    }
    eintragAendern(system.kennung, (s) => { s.querschnitte.splice(i, 1); });
  };
  return el('div.bs-qzeile', {}, [
    el('button.bs-qbild', {
      type: 'button', title: `Bearbeiten: woher ${kennwertnamen(art)} kommen, Masse`,
      on: { click: () => fensterOeffnen(fensterVon(q.kennung)) },
    }, [umrissBild(system, q, 44, 44)]),
    el('div.bs-qmitte', {}, [
      namensfeld({
        wert: q.name, titel: 'Name des Querschnitts', klasse: '.bs-qname',
        setzen: (name) => eintragAendern(system.kennung, (s) => { s.querschnitte[i].name = name; }),
      }),
      werte ? el('div.bs-kennwerte', { text: werte })
        : el('div.bs-qfehler', { text: fehler?.text || `${kennwertnamen(art)}: –`, title: fehler?.text || '' }),
      el('div.bs-benutzt', { text: `${herkunftText(art, q)} · ${benutzt.length ? `trägt ${benutzt.join(', ')}` : 'trägt keinen Stab'}` }),
    ]),
    el('button.weg', { type: 'button', text: '×', title: 'Querschnitt löschen', on: { click: weg } }),
  ]);
}

/**
 * Das Fenster eines Querschnitts -- beim Anlegen und mit einem Klick auf
 * sein Bild (Benutzer, 2026-10-24): woher A und I kommen, die Vorlage als
 * Auswahlliste mit ihrem Bild und den Massen, die Kennwerte, die Platte
 * oder Analyse -- und das E der Stäbe «gemäss Querschnitt».
 */
function querschnittFenster(system, kennung) {
  const i = system.querschnitte.findIndex((x) => x.kennung === kennung);
  if (i < 0) return null;
  const art = systemart(system.kennung);
  const vorlagen = systemkatalog(art, 'vorlagen');
  const q = system.querschnitte[i];
  const aendern = (veraenderer) => eintragAendern(system.kennung, (s) => veraenderer(s.querschnitte[i], s));
  const setzen = (feldname) => (wert) => aendern((x) => { x[feldname] = wert; });
  const zeilen = [
    feld('Name', namensfeld({ wert: q.name, setzen: setzen('name'), titel: 'Name des Querschnitts' })),
    wahlBlock(`${kennwertnamen(art)} aus`, wahlSchalter({
      werte: systemkatalog(art, 'querschnittsarten').map((x) => ({ wert: x.wert, beschriftung: x.kurz, titel: x.beschriftung })),
      gewaehlt: q.art, titel: `Woher ${kennwertnamen(art)} kommen`,
      // Jede Art hat ihre eigenen Felder: umschalten heisst nur die Art
      // setzen, und wer zurückschaltet, findet ihre alten Zahlen (Benutzer,
      // 2026-11-19). Bis dahin teilten sich die Arten Masse und Bezug, und
      // hier wurde abgeräumt, was der Kern sonst ablehnte -- dreimal
      // nachgebessert.
      setzen: setzen('art'),
    })),
  ];
  if (q.art === 'vorlage') {
    const vorlage = vorlagen.find((v) => v.schluessel === q.vorlage) || vorlagen[0];
    // Die Vorlage als Auswahlliste, daneben ihr Bild mit den Massen dieses
    // Querschnitts (Benutzer, 2026-10-24).
    zeilen.push(el('div.bs-qvorlage', {}, [
      feld('Vorlage', auswahl({
        werte: vorlagen.map((v) => ({ wert: v.schluessel, beschriftung: v.name })),
        gewaehlt: q.vorlage,
        titel: 'Die Form des Querschnitts',
        beiAenderung: (w) => aendern((x) => {
          x.vorlage = w;
          // Die Masse der neuen Vorlage, mit ihren Vorgaben -- die alten passten nicht.
          x.masse = vorgabenDer(art, w);
        }),
      })),
      umrissBild(system, q, 120, 90),
    ]));
    // Grenze, Satz und Einheit jedes Masses kommen mit ihm aus dem Kern.
    for (const m of vorlage?.masse || []) {
      zeilen.push(feld(m.beschriftung, zahlfeld({
        wert: q.masse?.[m.schluessel] ?? m.vorgabe, schritt: m.schritt, angabe: m.angabe,
        titel: m.heisst,
        beiAenderung: (w) => aendern((x) => { x.masse = { ...x.masse, [m.schluessel]: w }; }),
      }), m.angabe.einheit));
    }
  } else if (q.art === 'profil') {
    // Die Reihe als Schalter, die Grösse als Liste mit dem Bild daneben --
    // wie die Vorlage (Benutzer, 2026-10-24) -- und in der Ebene die Achse.
    const reihen = systemkatalog(art, 'profilreihen');
    const reihe = reiheVon(art, q.profil);
    const achsen = systemkatalog(art, 'profilachsen');
    zeilen.push(
      wahlBlock('Reihe', wahlSchalter({
        werte: reihen.map((r) => ({ wert: r.kurz, beschriftung: r.kurz, titel: r.beschreibung })),
        gewaehlt: reihe.kurz, titel: 'Die Reihe der Stahlprofile',
        setzen: (kurz) => setzen('profil')(reihen.find((r) => r.kurz === kurz).profile[0]),
      })),
      el('div.bs-qvorlage', {}, [
        feld('Profil', auswahl({
          werte: reihe.profile.map((name) => ({ wert: name, beschriftung: name })),
          gewaehlt: q.profil, titel: `${reihe.beschreibung} – Masse nach der Tabelle`,
          beiAenderung: setzen('profil'),
        })),
        umrissBild(system, q, 120, 90),
      ]),
      // Wie geschrieben: die Achsen heissen y und z, nicht Y und Z.
      achsen.length ? wahlBlock('Biegung', wahlSchalter({
        werte: achsen, gewaehlt: q.achse, titel: 'Um welche Achse sich das Profil im Rahmen biegt',
        setzen: setzen('achse'),
      })) : null,
    );
  } else if (q.art === 'kennwerte') {
    zeilen.push(...systemkatalog(art, 'kennwerte').map((k) => feld(k.kurz, zahlfeld({
      wert: q.kennwerte?.[k.kurz] ?? 0, schritt: k.kurz === 'A' ? 1000 : 10, angabe: k.angabe,
      titel: k.beschriftung,
      beiAenderung: (w) => aendern((x) => { x.kennwerte = { ...x.kennwerte, [k.kurz]: w }; }),
    }), k.angabe.einheit, k.beschriftung)));
  } else {
    const alle = q.art === 'platte' ? zustand.projekt.querschnitte : (zustand.projekt.querschnittsanalysen || []);
    zeilen.push(el('div.bs-qvorlage', {}, [
      feld(artKurz(art, q), bauteilliste({
        alle, gewaehlt: q[q.art], setzen: setzen(q.art), inSandbox: istSandbox(system.kennung),
      })),
      umrissBild(system, q, 120, 90),
    ]));
  }
  // Welches E ein Stab hat, der das Material dieses Querschnitts nimmt --
  // nur, wenn einer das tut, und nur, wo es mehr als E₀ gibt: E_eq hat nur
  // einer aus einer Platte oder Analyse (Benutzer, 2026-10-24). Welche
  // Stellungen es gibt, sagt der Katalog; bei einer Form wartet die Wahl,
  // bis der Querschnitt zurückschaltet.
  const eigenes = systemkatalog(art, 'material_des_querschnitts');
  const module = systemkatalog(art, 'e_module').filter((x) => x.arten.includes(q.art));
  const mitEigenem = system.linien.some((l) => l.querschnitt === q.kennung && l.material === eigenes);
  if (mitEigenem && module.length > 1) {
    zeilen.push(wahlBlock('E-Modul', wahlSchalter({
      werte: module.map((x) => ({ wert: x.wert, beschriftung: x.beschriftung, titel: x.titel })),
      gewaehlt: q.e_modul, titel: 'Das E der Stäbe «gemäss Querschnitt»', setzen: setzen('e_modul'),
    })));
  } else if (module.length > 1) {
    // Sonst sucht man den Schalter (bis 2026-11-19 ohne ein Wort).
    zeilen.push(el('p.hinweis', {
      text: 'Ob E₀ oder E_eq, wählt man hier, sobald ein Stab das Material «gemäss Querschnitt» '
        + 'nimmt – sonst gilt das E seines Materials.',
    }));
  }
  if (mitEigenem && module.some((x) => x.wert === 'e_eq') && q.e_modul === 'e_eq') {
    const eq = (veraenderer) => aendern((x) => veraenderer(x.eq));
    const zahl = (name, schritt, titel) => feld(name, zahlfeld({
      wert: q.eq[name], schritt, leer: 0, titel,
      beiAenderung: (w) => eq((x) => { x[name] = w; }),
    }), feldangabe('modul', name).einheit);
    zeilen.push(
      zahl('N', 50, 'Normalkraft, bei der E_eq gilt – Zug positiv'),
      zahl('M', 10, q.art === 'platte'
        ? 'Moment, bei dem E_eq gilt – bei einer Platte in x-Richtung mit Zug unten, nicht negativ'
        : 'Moment, bei dem E_eq gilt – positiv zieht es unten, an der gestrichelten Faser'),
      rechenwahlZeile('Rechenwerte wie in der Analyse', q.eq, eq, {
        arten: 'faserarten', phiImmer: true, werkstoffe: { ...werkstoffeDerQuelle(q), klasse: 'modul' },
      }),
    );
  }
  // Die Kennwerte, wie der Kern sie rechnete, und was er zum Querschnitt
  // meldet: was ihm fehlt, oder dass y und z keine Hauptachsen sind. Bis
  // 2026-11-19 stand ohne Kennwerte nichts da -- oder noch die Werte der
  // Art vor dem Umschalten.
  const werte = kennwerte(system, q);
  if (werte) zeilen.push(el('p.bs-kennwerte', { text: werte }));
  zeilen.push(...meldungenZu(system, q).map((m) => el('p', {
    class: m.fehler ? 'hinweis hinweis-warnung' : 'hinweis', text: m.text,
  })));
  return fenster({
    titel: 'Querschnitt', zeichen: 'querschnitte', zusatz: `${system.name} · ${q.name}`,
    hilfe: erklaerung(texte(art).hilfe.querschnitte.zeilen, texte(art).hilfe.querschnitte.formel),
    inhalt: [
      el('button.knopf.knopf-klein.bs-zurueck', {
        type: 'button', text: '← alle Querschnitte', on: { click: () => fensterOeffnen('querschnitte') },
      }),
      ...zeilen,
    ],
  });
}

/** Je Querschnitt eine Zeile; ein neuer öffnet gleich sein Fenster. */
function querschnitteInhalt(system) {
  const klasse = systemkatalog(systemart(system.kennung), 'klassen', 'querschnitt');
  const neu = () => {
    let kennung;
    eintragAendern(system.kennung, (s) => {
      kennung = neueKennung(s, 'Q', s.querschnitte);
      s.querschnitte.push(ausVorlage(klasse, { kennung, name: naechsterName('Querschnitt', s.querschnitte) }));
    });
    fensterOeffnen(fensterVon(kennung));
  };
  return [
    ...(system.querschnitte.length ? system.querschnitte.map((q, i) => querschnittZeile(system, q, i))
      : [el('p.bs-leer', { text: 'Noch kein Querschnitt.' })]),
    el('button.knopf.knopf-klein', { type: 'button', text: '+ Querschnitt', on: { click: neu } }),
  ];
}

// ===========================================================================
// Die Knöpfe der Eingaben
// ===========================================================================

/**
 * Material, Querschnitte, Lastfälle, Kombinationen und die Statik-Analyse
 * als Knöpfe, jeder mit seinem Fenster -- wie die Kapitel der
 * Querschnittsanalyse (Benutzer, 2026-10-24). Unter dem Namen klein, wie
 * viele es gibt. Dieselben für beide Arten, mit den Hilfen der Art.
 */
const kapitelVon = (art) => [
  {
    titel: 'Tragwerk',
    kapitel: [
      {
        schluessel: 'material', name: 'Material', titel: 'Materialien', hilfe: texte(art).hilfe.materialien,
        inhalt: materialienInhalt,
        stand: (s) => zeilenstand(s.stabmaterialien, 'Material', 'Materialien', 'kein Material'),
      },
      {
        schluessel: 'querschnitte', name: 'Querschnitte', titel: 'Querschnitte', hilfe: texte(art).hilfe.querschnitte,
        inhalt: querschnitteInhalt,
        stand: (s) => zeilenstand(s.querschnitte, 'Querschnitt', 'Querschnitte', 'kein Querschnitt'),
      },
    ],
  },
  lastenKapitel({
    lastenVon: (s, lf) => s.linien.reduce((n, l) => n + l.lasten.filter((x) => x.lastfall === lf).length, 0)
      + s.knotenlasten.filter((x) => x.lastfall === lf).length,
    eigengewicht: {
      text: 'ρ · g · A',
      titel: 'Je Stab Dichte mal g = 10 m/s² mal Fläche – beim Beton die Dichte des Stahlbetons',
    },
  }),
  {
    titel: 'Analyse',
    kapitel: [
      {
        schluessel: 'statik', name: 'Statik-Analyse', titel: 'Statik-Analyse', hilfe: texte(art).hilfe.statik,
        inhalt: statikInhalt,
        stand: (s) => zeilenstand(s.diagramme, 'Diagramm', 'Diagramme', 'kein Diagramm'),
      },
    ],
  },
];

/** Die Fenster des Systems, nach ihrem Schlüssel: die Kapitel und je Querschnitt seines. */
export function balkensystemFenster(system, schluessel) {
  const [wo, kennung] = String(schluessel).split(':');
  return wo === 'querschnitt' && kennung ? querschnittFenster(system, kennung)
    : kapitelFenster(system, kapitelVon(systemart(system.kennung)), schluessel);
}

// ===========================================================================
// Statik-Analyse
// ===========================================================================

/**
 * Welche Diagramme rechts stehen -- je Zeile ein Fall und was das Diagramm
 * von ihm zeigt (`diagrammzeilen`, Benutzer, 2026-10-23). Ein Knopf mit
 * Fenster wie die Eingaben (Benutzer, 2026-10-24).
 */
function statikInhalt(system) {
  const art = systemart(system.kennung);
  return diagrammzeilen(system, {
    groessen: () => systemkatalog(art, 'diagrammgroessen'), vorlage: systemkatalog(art, 'klassen', 'diagramm'),
  });
}

// ===========================================================================

export function balkensystemEditor(system) {
  const art = systemart(system.kennung);
  return [systemGruppe(system),
    kapitelPanel(system, kapitelVon(art), { schluessel: `${art}/Eingaben`, titel: 'Eingaben' })];
}
