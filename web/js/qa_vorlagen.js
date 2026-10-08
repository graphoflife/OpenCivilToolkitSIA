/**
 * qa_vorlagen.js -- ein Querschnitt aus einer Vorlage: Rechteck, T-Balken,
 * Hohlkasten, Kreis.
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
 */

import { api } from './api.js';
import { pfad } from './cad_ansicht.js';
import { el, melden, svgEl, zahlfeld } from './dom.js';
import { zustand } from './zustand.js';

function katalog() {
  return zustand.katalog?.querschnittsanalyse?.vorlagen || [];
}

/** Was zuletzt eingestellt war -- je Analyse in der Ansicht, nicht im Projekt. */
function wahlVon(a) {
  a.qa.vorlage = a.qa.vorlage || {
    art: 'rechteck', masse: {}, randabstand: 50, bewehrung: true, schubwaende: true,
  };
  return a.qa.vorlage;
}

// ===========================================================================
// Die Skizze
// ===========================================================================

/** Alle Punkte der Teile -- für den Rahmen der Skizze. */
function punkteVon(teile) {
  return [
    ...teile.polygone.flatMap((p) => p.punkte),
    ...teile.staebe.map((s) => s.lage),
  ];
}

/** Eine Masslinie neben dem Bauteil, auf der Seite, die der Kern nennt. */
function masslinie(g, m, nach) {
  const ab = 12;
  const [dx, dy] = { unten: [0, ab], oben: [0, -ab], links: [-ab, 0], rechts: [ab, 0] }[m.seite] || [0, ab];
  const [x0, y0] = nach(m.von);
  const [x1, y1] = nach(m.bis);
  const [p, q] = [[x0 + dx, y0 + dy], [x1 + dx, y1 + dy]];
  const kurz = (x, y) => (dx ? `M${x - 3} ${y} H${x + 3}` : `M${x} ${y - 3} V${y + 3}`);
  g.append(svgEl('path', {
    d: `M${x0} ${y0} L${p[0]} ${p[1]} M${x1} ${y1} L${q[0]} ${q[1]} M${p[0]} ${p[1]} L${q[0]} ${q[1]} `
      + `${kurz(...p)} ${kurz(...q)}`,
    class: 'cad-mass',
  }));
  const [mx, my] = [(p[0] + q[0]) / 2, (p[1] + q[1]) / 2];
  const t = svgEl('text', { class: 'cad-masstext', 'text-anchor': 'middle' });
  t.textContent = m.text;
  if (dx) {
    const x = mx + (dx < 0 ? -4 : 11);
    t.setAttribute('x', x);
    t.setAttribute('y', my);
    t.setAttribute('transform', `rotate(-90 ${x} ${my})`);
  } else {
    t.setAttribute('x', mx);
    t.setAttribute('y', my + (dy > 0 ? 11 : -4));
  }
  g.append(t);
}

/**
 * Die Teile einer Vorlage als kleines Bild, `breite` × `hoehe` px -- mit
 * Masslinien, wenn `masse`, sonst als Bildchen für ihren Knopf.
 */
function skizze(teile, breite, hoehe, { masse = true } = {}) {
  const bild = svgEl('svg', {
    viewBox: `0 0 ${breite} ${hoehe}`, width: breite, height: hoehe, class: 'cad-skizze',
  });
  const punkte = punkteVon(teile);
  if (!punkte.length) return bild;
  const ys = punkte.map((p) => p[0]);
  const zs = punkte.map((p) => p[1]);
  const [y0, y1, z0, z1] = [Math.min(...ys), Math.max(...ys), Math.min(...zs), Math.max(...zs)];
  const rand = masse ? 30 : 3;
  const s = Math.min((breite - 2 * rand) / Math.max(y1 - y0, 1), (hoehe - 2 * rand) / Math.max(z1 - z0, 1));
  const ox = (breite - s * (y1 - y0)) / 2 - s * y0;
  const oy = (hoehe + s * (z1 - z0)) / 2 + s * z0;
  const v = { massstab: s, ursprung: [ox, oy] };
  const nach = (p) => [ox + s * p[0], oy - s * p[1]];
  const g = svgEl('g');
  for (const p of teile.polygone) {
    g.append(svgEl('path', { d: pfad(v, p.punkte), class: p.aussparung ? 'cad-loch' : 'cad-beton' }));
  }
  for (const w of teile.schubwaende) {
    g.append(svgEl('path', {
      d: pfad(v, [w.von, w.bis], false), class: 'cad-skizze-wand',
      'stroke-width': Math.max(1, w.dicke * s).toFixed(1),
    }));
  }
  for (const l of teile.stablinien) g.append(svgEl('path', { d: pfad(v, [l.von, l.bis], false), class: 'cad-linie' }));
  for (const st of teile.staebe) {
    const [x, y] = nach(st.lage);
    g.append(svgEl('circle', { cx: x, cy: y, r: Math.max(1.5, (st.durchmesser * s) / 2), class: 'cad-stab' }));
  }
  if (masse) for (const m of teile.masslinien) masslinie(g, m, nach);
  bild.append(g);
  return bild;
}

// ===========================================================================
// Das Fenster
// ===========================================================================

function zeile(beschriftung, eingabe, einheit = '') {
  return el('label.cad-zeile', {}, [
    el('span', { text: beschriftung }), eingabe, einheit ? el('span.einheit', { text: einheit }) : el('span'),
  ]);
}

/** Ein Haken «mit …». */
function haken(text, an, setzen) {
  return el('label.cad-wahl', {}, [
    el('input', { type: 'checkbox', checked: an, on: { change: (e) => setzen(e.target.checked) } }),
    text,
  ]);
}

/** Ein Zahlenfeld, das schon beim Tippen meldet -- die Skizze soll mitgehen. */
function massfeld(wert, setzen) {
  const feld = zahlfeld({ wert, schritt: 10, min: 1, beiAenderung: setzen });
  feld.querySelector('input')?.addEventListener('input', (e) => {
    const w = Number(e.target.value);
    if (e.target.value.trim() !== '' && Number.isFinite(w)) setzen(w);
  });
  return feld;
}

/** Öffnet das Fenster der Vorlagen -- oder schliesst es, wenn es schon offen ist. */
export function vorlageOeffnen(a) {
  if (a.dialog) {
    a.dialog.schliessen();
    return;
  }
  if (!katalog().length) return;
  const knoten = el('div.cad-dialog', { role: 'dialog', 'aria-label': 'Vorlage' });
  const schliessen = () => {
    knoten.remove();
    a.dialog = null;
  };
  a.dialog = { schliessen };
  a.teile.flaeche.append(knoten);
  vorlageZeichnen(a, knoten);
}

function vorlageZeichnen(a, knoten) {
  const w = wahlVon(a);
  const v = katalog().find((x) => x.schluessel === w.art) || katalog()[0];
  w.art = v.schluessel;
  const neu = () => vorlageZeichnen(a, knoten);

  const bild = el('div.cad-vorlagenskizze');
  const meldung = el('p.cad-meldung', { hidden: true });
  const einsetzen = el('button.knopf.knopf-klein.knopf-haupt', {
    type: 'button', text: 'Einsetzen', title: 'Danach den Einsetzpunkt wählen -- Enter: Ursprung',
    on: {
      click: () => {
        const teile = a.qa.vorlagenteile;
        if (!teile) return;
        a.dialog?.schliessen();
        a.starten(einsetzenBefehl(v.name, structuredClone(w), teile));
      },
    },
  });

  // Die Skizze kommt vom Kern. Kommt eine Antwort zu spät -- es wurde
  // inzwischen wieder getippt --, gilt sie nicht mehr.
  const holen = () => {
    const nr = (a.qa.vorlagenfrage || 0) + 1;
    a.qa.vorlagenfrage = nr;
    bild.classList.add('ist-alt');
    api.vorlage(w).then((antwort) => {
      if (a.qa.vorlagenfrage !== nr) return;
      meldung.hidden = !antwort.fehler;
      meldung.textContent = antwort.fehler || '';
      einsetzen.disabled = !antwort.teile;
      a.qa.vorlagenteile = antwort.teile;
      if (antwort.teile) {
        bild.classList.remove('ist-alt');
        bild.replaceChildren(skizze(antwort.teile, 276, 140));
      }
    }).catch((fehler) => melden(fehler.message, true));
  };

  const waende = v.hat_waende;
  knoten.replaceChildren(
    el('div.cad-dialog-kopf', {}, [
      el('span', { text: 'Vorlage' }),
      el('button.cad-palette-zu', {
        type: 'button', text: '×', title: 'Schliessen (Esc)', on: { click: () => a.dialog?.schliessen() },
      }),
    ]),
    el('div.cad-vorlagen', {}, katalog().map((x) => el('button.cad-vorlagenknopf', {
      type: 'button', title: x.name, class: x.schluessel === v.schluessel ? 'ist-an' : '',
      on: { click: () => { w.art = x.schluessel; neu(); } },
    }, [skizze(x.skizze, 52, 36, { masse: false }), el('span', { text: x.name })]))),
    bild,
    ...v.masse.map((m) => zeile(m.beschriftung,
      massfeld(w.masse[m.schluessel] ?? m.vorgabe, (x) => { w.masse[m.schluessel] = x; holen(); }), 'mm')),
    zeile('Achsabstand', massfeld(w.randabstand, (x) => { w.randabstand = x; holen(); }), 'mm'),
    el('div.cad-wahlen', {}, [
      haken('mit Bewehrung', w.bewehrung, (x) => { w.bewehrung = x; holen(); }),
      waende ? haken('mit Schubwänden', w.schubwaende, (x) => { w.schubwaende = x; holen(); }) : null,
    ]),
    meldung,
    el('div.cad-dialog-fuss', {}, [einsetzen]),
  );
  holen();
}

// ===========================================================================
// Einsetzen
// ===========================================================================

/** Ein Beton und ein Stahl für die Vorlage -- die eingestellten, wenn es welche sind. */
function stoffe(a) {
  const v = a.qa.vorgaben;
  const von = (art, kennung) => zustand.projekt.materialien.find((m) => m.art === art
    && (!kennung || m.kennung === kennung))?.kennung || '';
  return {
    beton: von('beton', v.flaeche.material) || von('beton'),
    stahl: von('betonstahl', v.stablinien.stahl) || von('betonstahl'),
  };
}

async function einsetzen(a, wahl, ursprung) {
  try {
    const { beton, stahl } = stoffe(a);
    const antwort = await api.vorlageEinsetzen(zustand.projekt, a.qa.kennung, wahl, ursprung, beton, stahl);
    a.aendern((z) => { Object.assign(z, antwort.elemente); }, { auswahl: () => antwort.neu });
  } catch (fehler) {
    melden(fehler.message, true);
  }
}

/** Der Befehl nach «Einsetzen»: ein Punkt für die Ecke unten links. */
function einsetzenBefehl(name, wahl, teile) {
  return {
    name: 'vorlage',
    frage: () => `${name}: Einsetzpunkt`,
    hinweis: 'Die Ecke unten links kommt an den Punkt · Enter ohne Zahlen: Ursprung',
    punkt(a, erg) {
      einsetzen(a, wahl, erg.p);
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
    enter(a) {
      einsetzen(a, wahl, [0, 0]);
      return false;
    },
    zurueck: () => false,
  };
}
