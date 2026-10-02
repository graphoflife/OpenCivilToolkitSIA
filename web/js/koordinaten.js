/**
 * koordinaten.js -- das Koordinatenfenster neben der Zeichnung.
 *
 * Es zeigt, was im Zeichenfenster gerade dran ist:
 *
 *   ein Werkzeug      das neue Element als Zahlen -- Punkt für Punkt, ohne
 *                     Maus, mit «nächster Punkt» und Enter;
 *   eine Auswahl      ihre Lage und Eigenschaften, jede Zahl änderbar;
 *   nichts            die Querschnittswerte des Kerns und alle Elemente
 *                     zum Anklicken.
 *
 * Absolut oder relativ: relativ steht jeder Punkt als Abstand zum vorigen,
 * das Ende einer Linie oder Wand als Abstand zu ihrem Anfang. Geändert wird
 * immer nur der Punkt in der Zeile -- die anderen bleiben, wo sie sind.
 *
 * Gerechnet wird hier nichts: die Stäbe einer Linie, ihre tatsächliche
 * Teilung, die Querschnittswerte stehen so da, wie der Kern sie meldet.
 */

import { hakenSchalter } from './bausteine.js';
import { el, zahlfeld } from './dom.js';
import { span } from './mathe.js';
import {
  anlegen, ansichtVon, elementname, entwurfSchliessen, entwurfSetzen, kreispunkte,
  linienText, passendeGeometrie, rechteckpunkte, vorgabeMerken, waehlen, zahlText,
  zeichnungAendern,
} from './zeichenfenster.js';
import { aendern, zustand } from './zustand.js';

const LISTEN = {
  flaeche: 'flaechen', stab: 'staebe', linie: 'stablinien', wand: 'schubwaende',
};

const NEU_TITEL = {
  polygon: 'Neues Polygon', rechteck: 'Neues Rechteck', kreis: 'Neuer Kreis',
  stab: 'Neuer Stab', linie: 'Neue Stablinie', wand: 'Neue Schubwand',
};

/** Eine Koordinate, wie sie im Feld steht: auf Tausendstel gerundet, ohne Nullen dahinter. */
function rund(wert) {
  return Number(Number(wert).toFixed(3));
}

/** Ein Zahlenfeld für eine Koordinate. Die Pfeile springen um das Raster. */
function koordinate(a, wert, titel, beiAenderung, kennzeichen) {
  const feld = zahlfeld({ wert: rund(wert), schritt: a.raster, titel, beiAenderung });
  if (kennzeichen) (feld.querySelector('input') || feld).dataset.feld = kennzeichen;
  return feld;
}

function auswahlliste(werte, gewaehlt, titel, beiAenderung) {
  return el('select', {
    title: titel, on: { change: (e) => beiAenderung(e.target.value) },
  }, werte.map(({ wert, beschriftung }) => el('option', {
    value: wert, text: beschriftung, selected: wert === gewaehlt,
  })));
}

function stoffe(art) {
  return zustand.projekt.materialien.filter((m) => m.art === art)
    .map((m) => ({ wert: m.kennung, beschriftung: m.name || m.sorte }));
}

/** Beschriftung -- Eingabe -- Einheit, eng gesetzt. */
function zeile(beschriftung, eingabe, einheit = '') {
  return el('div.ko-zeile', {}, [
    el('span.ko-name', {}, [].concat(beschriftung)),
    eingabe,
    el('span.einheit', { text: einheit }),
  ]);
}

/** Zwei Felder nebeneinander: y und z eines Punkts. */
function punktzeile(a, beschriftung, p, setzen, { bezug = null, kennzeichen = '' } = {}) {
  const relativ = a.relativ && bezug;
  const anzeige = relativ ? [p[0] - bezug[0], p[1] - bezug[1]] : p;
  const aus = (i) => (w) => {
    const neu = [...p];
    neu[i] = relativ ? bezug[i] + w : w;
    setzen(neu);
  };
  return el('div.ko-punkt', {}, [
    el('span.ko-name', { text: beschriftung }),
    koordinate(a, anzeige[0], relativ ? 'Δy zum Bezugspunkt, mm' : 'y in mm', aus(0),
      kennzeichen && `${kennzeichen}-y`),
    koordinate(a, anzeige[1], relativ ? 'Δz zum Bezugspunkt, mm' : 'z in mm', aus(1),
      kennzeichen && `${kennzeichen}-z`),
  ]);
}

/** Kopf über den Punktzeilen: was die beiden Spalten sind. */
function spaltenkopf(a, erste = '#') {
  return el('div.ko-punkt.ist-kopf', {}, [
    el('span', { text: erste }),
    el('span', { text: a.relativ ? 'Δy / y' : 'y' }),
    el('span', { text: a.relativ ? 'Δz / z' : 'z' }),
  ]);
}

/**
 * Die Punkte eines Polygons als Tabelle. Relativ steht ab dem zweiten Punkt
 * der Abstand zum vorigen. `setzen(k, p)` ändert einen Punkt, `weg(k)` nimmt
 * ihn heraus -- solange danach noch ein Dreieck bleibt.
 */
function punktliste(a, punkte, setzen, weg, mindestens = 3) {
  return [
    spaltenkopf(a),
    ...punkte.map((p, k) => {
      const z = punktzeile(a, String(k + 1), p, (neu) => setzen(k, neu),
        { bezug: k > 0 ? punkte[k - 1] : null });
      z.append(el('button.weg', {
        text: '×', title: 'Punkt entfernen', type: 'button',
        class: punkte.length > mindestens ? '' : 'ist-stumpf',
        disabled: punkte.length <= mindestens,
        on: { click: () => weg(k) },
      }));
      return z;
    }),
  ];
}

/**
 * «Nächster Punkt»: zwei leere Felder und ein Knopf. Enter in einem der
 * Felder fügt an und setzt den Zeiger wieder ins erste -- so lässt sich ein
 * ganzes Polygon tippen.
 */
function naechsterPunkt(a, letzter, anfuegen) {
  const kennzeichen = 'naechst';
  const feld = (achse) => el('input', {
    type: 'number', step: 'any', placeholder: a.relativ && letzter ? `Δ${achse}` : achse,
    title: a.relativ && letzter ? `Abstand zum letzten Punkt in ${achse}, mm` : `${achse} in mm`,
    dataset: { feld: `${kennzeichen}-${achse}` },
    on: { keydown: (e) => { if (e.key === 'Enter') { e.preventDefault(); los(); } } },
  });
  const y = feld('y');
  const z = feld('z');
  const los = () => {
    if (y.value.trim() === '' || z.value.trim() === '') {
      (y.value.trim() === '' ? y : z).focus();
      return;
    }
    const roh = [Number(y.value), Number(z.value)];
    const p = a.relativ && letzter ? [letzter[0] + roh[0], letzter[1] + roh[1]] : roh;
    anfuegen(p);
    // Nach dem Neubau der Tafel wieder ins erste Feld.
    setTimeout(() => document.querySelector(`input[data-feld="${kennzeichen}-y"]`)?.focus());
  };
  return el('div.ko-punkt.ist-neu', {}, [
    el('span.ko-name', { text: '+' }), y, z,
    el('button.knopf.knopf-klein', { type: 'button', text: 'Punkt', title: 'Punkt anfügen (Enter)', on: { click: los } }),
  ]);
}

function schalterAbsolut(a) {
  const setzen = (relativ) => { a.relativ = relativ; aendern({}, 'zeichnung'); };
  return el('span.schalter', { title: 'Koordinaten absolut oder relativ zum vorigen Punkt' }, [
    el('button.schalter-halb', {
      type: 'button', text: 'absolut', class: a.relativ ? '' : 'ist-an',
      on: { click: () => { if (a.relativ) setzen(false); } },
    }),
    el('button.schalter-halb', {
      type: 'button', text: 'relativ', class: a.relativ ? 'ist-an' : '',
      on: { click: () => { if (!a.relativ) setzen(true); } },
    }),
  ]);
}

// ===========================================================================
// Ein neues Element
// ===========================================================================

/**
 * Was das gewählte Werkzeug als Nächstes anlegt, als Zahlen. Die Werte
 * bleiben in der Ansicht stehen -- wer zwei gleiche Rechtecke braucht,
 * drückt zweimal.
 */
function neuesElement(a, analyse) {
  const k = analyse.kennung;
  a.eingabe = a.eingabe || {};
  const e = a.eingabe;
  const knopf = (text, tun, titel = '') => el('button.knopf.knopf-klein.knopf-haupt', {
    type: 'button', text, title: titel, on: { click: tun },
  });
  const merken = (schluessel, vorgabe) => {
    e[schluessel] = e[schluessel] || structuredClone(vorgabe);
    return e[schluessel];
  };
  // Jede Zahl gleich neu zeigen: die Felder einer Zeile bauen auf dem Stand
  // beim Zeichnen auf, und ein zweites Feld derselben Zeile soll den ersten
  // Wert schon kennen.
  const setzer = (r, feld) => (wert) => { r[feld] = wert; aendern({}, 'zeichnung'); };

  switch (a.werkzeug) {
    case 'polygon': {
      const punkte = a.entwurf?.art === 'polygon' ? a.entwurf.punkte : [];
      return [
        punkte.length
          ? punktliste(a, punkte, (i, p) => {
            const neu = punkte.map((q) => [...q]);
            neu[i] = p;
            entwurfSetzen(k, neu);
          }, (i) => entwurfSetzen(k, punkte.filter((_, j) => j !== i)), 0)
          : el('p.ko-hinweis', { text: 'Punkte im Bild klicken oder hier eintippen.' }),
        naechsterPunkt(a, punkte.at(-1), (p) => entwurfSetzen(k, [...punkte, p])),
        el('div.ko-knoepfe', {}, [
          el('button.knopf.knopf-klein', {
            type: 'button', text: 'Verwerfen', disabled: !punkte.length,
            on: { click: () => entwurfSetzen(k, []) },
          }),
          knopf('Schliessen', () => entwurfSchliessen(k), 'Polygon schliessen (Enter im Bild)'),
        ]),
      ].flat();
    }
    case 'rechteck': {
      const r = merken('rechteck', { ecke: [0, 0], b: 300, h: 600 });
      return [
        punktzeile(a, 'Ecke unten links', r.ecke, setzer(r, 'ecke')),
        zeile('Breite b', zahlfeld({ wert: r.b, schritt: a.raster, min: 0, beiAenderung: setzer(r, 'b') }), 'mm'),
        zeile('Höhe h', zahlfeld({ wert: r.h, schritt: a.raster, min: 0, beiAenderung: setzer(r, 'h') }), 'mm'),
        el('div.ko-knoepfe', {}, [knopf('Anlegen', () => {
          if (r.b > 0 && r.h > 0) anlegen(k, 'flaeche', { punkte: rechteckpunkte(r.ecke, r.b, r.h) });
        })]),
      ];
    }
    case 'kreis': {
      const r = merken('kreis', { mitte: [250, 250], d: 500 });
      return [
        punktzeile(a, 'Mitte', r.mitte, setzer(r, 'mitte')),
        zeile('Durchmesser D', zahlfeld({ wert: r.d, schritt: a.raster, min: 0, beiAenderung: setzer(r, 'd') }), 'mm'),
        el('div.ko-knoepfe', {}, [knopf('Anlegen', () => {
          if (r.d > 0) anlegen(k, 'flaeche', { punkte: kreispunkte(r.mitte, r.d / 2) });
        })]),
      ];
    }
    case 'stab': {
      const r = merken('stab', { p: [0, 0] });
      return [
        punktzeile(a, 'Lage', r.p, setzer(r, 'p')),
        el('div.ko-knoepfe', {}, [knopf('Setzen', () => anlegen(k, 'stab', { p: r.p }))]),
      ];
    }
    default: {
      // Stablinie oder Schubwand: Anfang und Ende. Hat die Maus den Anfang
      // schon gesetzt, steht er hier.
      const r = merken(a.werkzeug, { von: [0, 0], bis: [1000, 0] });
      if (a.entwurf?.von) r.von = [...a.entwurf.von];
      return [
        spaltenkopf(a, ''),
        punktzeile(a, 'Anfang', r.von, setzer(r, 'von')),
        punktzeile(a, 'Ende', r.bis, setzer(r, 'bis'), { bezug: r.von }),
        el('div.ko-knoepfe', {}, [knopf('Anlegen', () => {
          if (r.von[0] !== r.bis[0] || r.von[1] !== r.bis[1]) {
            anlegen(k, a.werkzeug, { von: r.von, bis: r.bis });
          }
        })]),
      ];
    }
  }
}

// ===========================================================================
// Ein gewähltes Element
// ===========================================================================

function elementBlock(a, analyse, g) {
  const { art, index } = a.auswahl;
  const k = analyse.kennung;
  const element = analyse[LISTEN[art]][index];
  if (!element) return [];
  const aendernAm = (veraenderer) => zeichnungAendern(k, (x) => veraenderer(x[LISTEN[art]][index]));
  // Eine Eigenschaft (nicht die Lage) gilt auch für das nächste neue Element.
  const eigenschaft = (feld) => (wert) => {
    vorgabeMerken(k, art, feld, wert);
    aendernAm((x) => { x[feld] = wert; });
  };
  const durchmesser = zustand.katalog?.durchmesser;
  const stahlwahl = () => zeile('Stahl', auswahlliste(stoffe('betonstahl'), element.stahl,
    'Betonstahl', eigenschaft('stahl')));

  const teile = [];
  if (art === 'flaeche') {
    teile.push(zeile('Material', auswahlliste(
      [...stoffe('beton'), { wert: '', beschriftung: 'Aussparung' }], element.material,
      'Beton -- oder Aussparung: ohne Material nimmt das Polygon Fläche weg',
      eigenschaft('material'))));
    teile.push(...punktliste(a, element.punkte,
      (i, p) => aendernAm((x) => { x.punkte[i] = p; }),
      (i) => {
        a.auswahl = { art, index };
        aendernAm((x) => { x.punkte.splice(i, 1); });
      }));
    teile.push(naechsterPunkt(a, element.punkte.at(-1),
      (p) => aendernAm((x) => { x.punkte.push(p); })));
  } else if (art === 'stab') {
    teile.push(
      spaltenkopf(a, ''),
      punktzeile(a, 'Lage', [element.y, element.z], ([y, z]) => aendernAm((x) => { x.y = y; x.z = z; })),
      zeile('⌀', zahlfeld({
        wert: element.durchmesser, stufen: durchmesser, min: 1, titel: 'Stabdurchmesser',
        beiAenderung: eigenschaft('durchmesser'),
      }), 'mm'),
      stahlwahl(),
    );
  } else {
    teile.push(
      spaltenkopf(a, ''),
      punktzeile(a, 'Anfang', element.von, (p) => aendernAm((x) => { x.von = p; })),
      punktzeile(a, 'Ende', element.bis, (p) => aendernAm((x) => { x.bis = p; }), { bezug: element.von }),
    );
    if (art === 'linie') teile.push(...linienFelder(element, eigenschaft, durchmesser));
    else teile.push(...wandFelder(element, eigenschaft, durchmesser));
    teile.push(stahlwahl());
    const info = infoZeile(art, element, index, g);
    if (info) teile.push(info);
  }
  teile.push(el('div.ko-knoepfe', {}, [
    el('button.knopf.knopf-klein.knopf-gefahr', {
      type: 'button', text: 'Löschen', title: 'Element löschen (Entf im Bild)',
      on: {
        click: () => {
          a.auswahl = null;
          zeichnungAendern(k, (x) => { x[LISTEN[art]].splice(index, 1); });
        },
      },
    }),
  ]));
  return teile;
}

function linienFelder(l, eigenschaft, durchmesser) {
  const arten = zustand.katalog?.querschnittsanalyse?.linienarten || [];
  const flaechig = l.art === 'flaeche';
  return [
    zeile('Art', auswahlliste(arten, l.art,
      'Fläche: verschmiert; Anzahl: n Stäbe; Teilung: Abstand, gerundet auf einen, der aufgeht',
      eigenschaft('art'))),
    flaechig ? zeile(['A', el('sub', { text: 's' })], zahlfeld({
      wert: l.flaeche, schritt: 100, min: 0, titel: 'Stahlfläche der ganzen Linie',
      beiAenderung: eigenschaft('flaeche'),
    }), 'mm²') : null,
    l.art === 'anzahl' ? zeile('Anzahl n', zahlfeld({
      wert: l.anzahl, schritt: 1, min: 1, titel: 'Anzahl Stäbe', beiAenderung: eigenschaft('anzahl'),
    })) : null,
    l.art === 'teilung' ? zeile('Teilung s', zahlfeld({
      wert: l.teilung, schritt: 25, min: 1, titel: 'Gewünschte Teilung; gerundet auf eine, die aufgeht',
      beiAenderung: eigenschaft('teilung'),
    }), 'mm') : null,
    flaechig ? null : zeile('⌀', zahlfeld({
      wert: l.durchmesser, stufen: durchmesser, min: 1, titel: 'Stabdurchmesser',
      beiAenderung: eigenschaft('durchmesser'),
    }), 'mm'),
    flaechig ? null : el('div.ko-zeile.ist-haken', {}, [
      el('span.ko-name', { text: 'Starteisen' }),
      hakenSchalter(!!l.starteisen, eigenschaft('starteisen'), 'Starteisen'),
      el('span'),
    ]),
    flaechig ? null : el('div.ko-zeile.ist-haken', {}, [
      el('span.ko-name', { text: 'Endeisen' }),
      hakenSchalter(!!l.endeisen, eigenschaft('endeisen'), 'Endeisen'),
      el('span'),
    ]),
  ].filter(Boolean);
}

function wandFelder(w, eigenschaft, durchmesser) {
  const schnitte = zustand.katalog?.querschnittsanalyse?.schnitte || [1, 2, 3, 4, 5, 6, 7, 8];
  return [
    zeile(['Dicke ', span('b_w')], zahlfeld({
      wert: w.dicke, schritt: 10, min: 1, titel: 'Dicke der Schubwand', beiAenderung: eigenschaft('dicke'),
    }), 'mm'),
    zeile('Bügel ⌀', zahlfeld({
      wert: w.durchmesser, stufen: durchmesser, min: 0, titel: 'Bügeldurchmesser; 0: ohne Bügel',
      leer: 0, beiAenderung: eigenschaft('durchmesser'),
    }), 'mm'),
    zeile('Teilung s', zahlfeld({
      wert: w.teilung, schritt: 25, min: 1, titel: 'Bügelteilung in Längsrichtung des Bauteils',
      beiAenderung: eigenschaft('teilung'),
    }), 'mm'),
    zeile('Schnitte', auswahlliste(schnitte.map((n) => ({ wert: String(n), beschriftung: String(n) })),
      String(w.schnitte), 'Wie viele Bügelschenkel die Wand kreuzen',
      (v) => eigenschaft('schnitte')(Number(v)))),
  ];
}

/** Was der Kern zu einer Linie oder Wand sagt -- nur, solange es zur Zeichnung passt. */
function infoZeile(art, element, index, g) {
  if (!g) return null;
  if (art === 'linie') {
    const info = g.linien?.[index];
    if (!info?.punkte) return null;
    const text = element.art === 'flaeche'
      ? `${linienText(element, info)} · L = ${zahlText(info.laenge)} mm`
      : `${linienText(element, info)} · As = ${zahlText(info.flaeche, 0)} mm² (${
        zahlText(info.je_meter, 0)} mm²/m)`;
    return el('p.ko-info', { text });
  }
  const info = g.waende?.[index];
  if (!info) return null;
  return el('p.ko-info', {
    text: `l = ${zahlText(info.laenge)} mm · asw = ${zahlText(info.a_sw_s, 0)} mm²/m`,
  });
}

// ===========================================================================
// Nichts gewählt
// ===========================================================================

/** Die Querschnittswerte des Kerns und alle Elemente zum Anklicken. */
function uebersicht(a, analyse, g) {
  const k = analyse.kennung;
  const teile = [];
  const b = g?.brutto;
  if (b) {
    const wert = (symbol, zahl, einheit) => el('div.ko-wert', {}, [
      span(symbol), el('span', { text: ` = ${zahl} ${einheit}` }),
    ]);
    teile.push(el('div.ko-werte', { title: 'Bruttoquerschnitt, vom Kern gerechnet' }, [
      wert('A', zahlText(b.A, 0), 'mm²'),
      wert('y_S', zahlText(b.y_S), 'mm'),
      wert('z_S', zahlText(b.z_S), 'mm'),
      wert('I_y', zahlText(b.I_y / 1e6, 1), '·10⁶ mm⁴'),
      wert('I_z', zahlText(b.I_z / 1e6, 1), '·10⁶ mm⁴'),
      wert('I_{yz}', zahlText(b.I_yz / 1e6, 1), '·10⁶ mm⁴'),
    ]));
  }
  const fehler = new Set((g?.meldungen || []).flatMap((m) => m.elemente));
  const beschreibung = {
    flaeche: (f) => (f.material
      ? zustand.projekt.materialien.find((m) => m.kennung === f.material)?.name || f.material
      : 'nimmt Fläche weg'),
    stab: (s) => `⌀${zahlText(s.durchmesser)} bei (${zahlText(s.y)}, ${zahlText(s.z)})`,
    linie: (l, i) => linienText(l, g?.linien?.[i]) || l.art,
    wand: (w) => `b_w = ${zahlText(w.dicke)} · ⌀${zahlText(w.durchmesser)} @ ${zahlText(w.teilung)}`,
  };
  const reihen = Object.entries(LISTEN).flatMap(([art, liste]) => analyse[liste].map((x, i) => {
    const name = elementname(analyse, art, i);
    return el('button.ko-element', {
      type: 'button', class: fehler.has(name) ? 'ist-fehler' : '',
      on: { click: () => waehlen(k, { art, index: i }) },
    }, [el('span.ko-elementname', { text: name }), el('span', { text: beschreibung[art](x, i) })]);
  }));
  teile.push(reihen.length
    ? el('div.ko-elemente', {}, reihen)
    : el('p.ko-hinweis', { text: 'Noch nichts gezeichnet. Ein Werkzeug wählen oder eine Vorlage nehmen.' }));
  return teile;
}

// ===========================================================================

/** Das Koordinatenfenster zur Analyse -- je nach Werkzeug und Auswahl. */
export function koordinatenfenster(analyse) {
  const a = ansichtVon(analyse.kennung);
  const g = passendeGeometrie(a, analyse);
  let titel;
  let inhalt;
  if (a.werkzeug !== 'waehlen') {
    titel = NEU_TITEL[a.werkzeug];
    inhalt = neuesElement(a, analyse);
  } else if (a.auswahl && analyse[LISTEN[a.auswahl.art]][a.auswahl.index]) {
    titel = elementname(analyse, a.auswahl.art, a.auswahl.index);
    inhalt = elementBlock(a, analyse, g);
  } else {
    titel = 'Querschnitt';
    inhalt = uebersicht(a, analyse, g);
  }
  return el('div.koordinaten', {}, [
    el('div.ko-kopf', {}, [el('b', { text: titel }), schalterAbsolut(a)]),
    ...inhalt,
  ]);
}
