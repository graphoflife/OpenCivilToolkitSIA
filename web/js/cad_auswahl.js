/**
 * cad_auswahl.js -- was der Zeiger trifft, und wie eine Auswahl entsteht.
 *
 * Gezogen wird nichts: ein Element wählt man aus und verschiebt es danach
 * mit einem Befehl, mit Basispunkt und Ziel. Wer eine Ecke an eine bestimmte
 * Stelle will, tippt sie ins schwebende Fenster.
 *
 *   Klick              wählt, was unter dem Zeiger liegt: eine Ecke vor
 *                      Punkten vor Linien vor Flächen, die kleinste zuerst.
 *                      Liegen Ecken aufeinander, immer nur eine (`treffer`)
 *   noch ein Klick     an derselben Stelle: das nächste darunter
 *   Shift+Klick        nimmt dazu oder weg
 *   Rahmen ziehen      nach rechts: was ganz drin liegt, und jede Ecke im
 *                      Rahmen; nach links: auch, was er schneidet (wie in
 *                      AxisVM und AutoCAD)
 */

import { nachBild, nachWelt } from './cad_ansicht.js';
import {
  abstand, auswahlTeil, aufStrecke, flaecheVon, innen, schnitt,
} from './cad_modell.js';
import { NAEHE } from './cad_eingabe.js';
import { el } from './dom.js';

/** Die Elemente, um die es gerade geht: die gewählten, und wem eine gewählte Ecke gehört. */
export function imSpiel(a) {
  return new Set([...a.auswahl].map((s) => auswahlTeil(s).kennung));
}

/**
 * Alles unter dem Zeiger, in der Reihenfolge, in der es gewählt wird -- je
 * Eintrag der Schlüssel der Auswahl.
 *
 * Zuerst die Ecken, die nächste Stelle zuerst. Liegen dort mehrere Ecken
 * aufeinander, kommt zuerst die eines Elements, um das es gerade geht (es
 * ist gewählt, oder eine seiner Ecken); sonst nach dem Rang seiner Art, den
 * die App vorgibt (`art.rang`), und innerhalb der Art das zuletzt gezeichnete
 * -- die höchste Nummer. Ein Klick wählt so immer genau eine Ecke; ein
 * zweiter an derselben Stelle die nächste. Danach Punkte, Linien und Flächen
 * unter dem Zeiger, das kleinste zuerst.
 */
export function treffer(a, bild) {
  const z = a.adapter.zeichnung();
  const m = a.modell;
  const lagen = m.lagen(z);
  const welt = nachWelt(a.v, bild);
  const weit = NAEHE / a.v.massstab;
  const spiel = imSpiel(a);
  const rang = (x) => x.art.rang ?? m.arten.indexOf(x.art);
  const nummer = (x) => Number(String(x.e.kennung).replace(/^\D+/, '')) || 0;
  const vorrang = (p, q) => (Number(spiel.has(q.e.kennung)) - Number(spiel.has(p.e.kennung)))
    || (rang(p) - rang(q)) || (nummer(q) - nummer(p)) || (p.i - q.i);

  const an = new Map();
  for (const x of m.ecken(z)) an.set(x.knoten, [...(an.get(x.knoten) || []), x]);
  const liste = [];
  const nahe = (z.knoten || []).map((k) => ({ k, d: abstand(welt, m.lage(k)) }))
    .filter((x) => x.d <= weit).sort((p, q) => p.d - q.d);
  for (const { k } of nahe) {
    const ecken = an.get(k.kennung) || [];
    // Ein Knoten, an dem nichts hängt, ist selbst zu wählen.
    if (!ecken.length) liste.push(k.kennung);
    for (const x of [...ecken].sort(vorrang)) if (!liste.includes(x.schluessel)) liste.push(x.schluessel);
  }

  const punkte = [];
  const linien = [];
  const flaechen = [];
  for (const { art, e } of m.elemente(z)) {
    const orte = m.verweise(art, e).map((k) => lagen.get(k));
    if (orte.some((p) => !p)) continue;
    if (art.form === 'punkt') {
      const r = Math.max(weit, a.adapter.trefferradius?.(art, e) || 0);
      const d = abstand(welt, orte[0]);
      if (d <= r) punkte.push({ kennung: e.kennung, d });
    } else if (art.form === 'linie') {
      const d = abstand(welt, aufStrecke(welt, orte[0], orte[1]).q);
      if (d <= Math.max(weit, a.adapter.trefferradius?.(art, e) || 0)) linien.push({ kennung: e.kennung, d });
    } else if (orte.length >= 3 && innen(welt, orte)) {
      flaechen.push({ kennung: e.kennung, d: Math.abs(flaecheVon(orte)) });
    }
  }
  const nach = (x, y) => x.d - y.d;
  for (const gruppe of [punkte, linien, flaechen]) {
    for (const x of gruppe.sort(nach)) if (!liste.includes(x.kennung)) liste.push(x.kennung);
  }
  return liste;
}

/** Ein Klick ohne Befehl: wählen, dazunehmen, durchschalten. */
export function klickWaehlen(a, bild, e) {
  const liste = treffer(a, bild);
  const gleicheStelle = a.letzterKlick && abstand(a.letzterKlick.bild, bild) <= 3;
  let ziel = liste[0] || null;
  if (gleicheStelle && liste.length > 1) {
    const vorher = a.letzterKlick.ziel;
    ziel = liste[(liste.indexOf(vorher) + 1) % liste.length];
  }
  a.letzterKlick = { bild, ziel };
  if (e.shiftKey) {
    if (ziel) {
      if (a.auswahl.has(ziel)) {
        a.auswahl.delete(ziel);
      } else {
        a.auswahl.add(ziel);
        // Eine Ecke eines ganz gewählten Elements: nun sind es seine Ecken.
        const { kennung, i } = auswahlTeil(ziel);
        if (i !== null) a.auswahl.delete(kennung);
      }
    }
  } else {
    a.auswahl = new Set(ziel ? [ziel] : []);
  }
}

/** Liegt die Strecke p-q ganz oder teilweise im Rechteck? */
function streckeImRechteck(p, q, [y0, z0, y1, z1], ganz) {
  const drin = (x) => x[0] >= y0 && x[0] <= y1 && x[1] >= z0 && x[1] <= z1;
  if (ganz) return drin(p) && drin(q);
  if (drin(p) || drin(q)) return true;
  const ecken = [[y0, z0], [y1, z0], [y1, z1], [y0, z1]];
  return ecken.some((c, i) => schnitt([p, q], [c, ecken[(i + 1) % 4]]));
}

/**
 * Was ein Rahmen wählt. `start` und `ende` in Bildpunkten: nach rechts
 * gezogen, was ganz drin liegt -- und jede Ecke im Rahmen, auch die, die
 * genau aufeinander liegen. So zieht man die rechte Kante eines
 * Querschnitts samt allem, was dort endet, mit einem Rahmen auf. Nach links
 * gezogen jedes Element, das er schneidet. Dazu freie Knoten im Rahmen.
 */
export function rahmenWaehlen(a, start, ende, dazu) {
  const ganz = ende[0] >= start[0];
  const p = nachWelt(a.v, start);
  const q = nachWelt(a.v, ende);
  const rechteck = [Math.min(p[0], q[0]), Math.min(p[1], q[1]), Math.max(p[0], q[0]), Math.max(p[1], q[1])];
  const z = a.adapter.zeichnung();
  const m = a.modell;
  const lagen = m.lagen(z);
  const neu = new Set(dazu ? a.auswahl : []);
  const ganzDrin = new Set();
  for (const { art, e } of m.elemente(z)) {
    const orte = m.verweise(art, e).map((k) => lagen.get(k));
    if (orte.some((x) => !x)) continue;
    let gewaehlt;
    if (art.form === 'punkt') gewaehlt = streckeImRechteck(orte[0], orte[0], rechteck, true);
    else if (art.form === 'linie') gewaehlt = streckeImRechteck(orte[0], orte[1], rechteck, ganz);
    else {
      const kanten = orte.map((x, i) => [x, orte[(i + 1) % orte.length]]);
      gewaehlt = ganz ? kanten.every(([s, t]) => streckeImRechteck(s, t, rechteck, true))
        : kanten.some(([s, t]) => streckeImRechteck(s, t, rechteck, false))
          || innen([rechteck[0], rechteck[1]], orte);
    }
    if (gewaehlt) {
      neu.add(e.kennung);
      ganzDrin.add(e.kennung);
    }
  }
  const drin = (q) => q && streckeImRechteck(q, q, rechteck, true);
  if (ganz) {
    for (const x of m.ecken(z)) {
      if (!ganzDrin.has(x.e.kennung) && drin(lagen.get(x.knoten))) neu.add(x.schluessel);
    }
  }
  const benutzung = m.benutzung(z);
  for (const k of z.knoten || []) if (!benutzung.get(k.kennung) && drin(m.lage(k))) neu.add(k.kennung);
  a.auswahl = neu;
}

/** Wo die Auswahl im Bild liegt -- [x0, y0, x1, y1] oder null. */
function auswahlRahmen(a) {
  if (!a.auswahl.size) return null;
  const z = a.adapter.zeichnung();
  const m = a.modell;
  const lagen = m.lagen(z);
  const punkte = [];
  for (const k of z.knoten || []) if (a.auswahl.has(k.kennung)) punkte.push(m.lage(k));
  for (const x of m.ecken(z)) {
    const p = lagen.get(x.knoten);
    if (p && (a.auswahl.has(x.e.kennung) || a.auswahl.has(x.schluessel))) punkte.push(p);
  }
  if (!punkte.length) return null;
  const bild = punkte.map((p) => nachBild(a.v, p));
  const xs = bild.map((p) => p[0]);
  const ys = bild.map((p) => p[1]);
  return [Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys)];
}

/**
 * Die kleine Leiste neben der Auswahl: nur, was für sie geht. Steht oben
 * rechts an der Auswahl, im Bild gehalten, und weicht dem schwebenden
 * Fenster aus.
 */
export function leisteZeichnen(a) {
  const ziel = a.teile.leiste;
  const r = a.befehl ? null : auswahlRahmen(a);
  if (!r) {
    ziel.hidden = true;
    return;
  }
  // Neu gebaut nur, wenn sich Zeichnung oder Auswahl geändert haben -- beim
  // Verschieben der Ansicht wandert die Leiste bloss mit.
  const schluessel = JSON.stringify([a.version, [...a.auswahl]]);
  if (ziel.dataset.schluessel !== schluessel) {
    ziel.dataset.schluessel = schluessel;
    ziel.replaceChildren(...a.aktionen().map((x) => el('button.cad-aktion', {
      type: 'button', title: x.titel || x.text,
      on: { click: (e) => { e.preventDefault(); x.tun(); } },
    }, [el('span.cad-aktionszeichen', { text: x.zeichen }), el('span', { text: x.text }),
      x.taste ? el('kbd', { text: x.taste }) : null])));
  }
  ziel.hidden = false;
  const breite = ziel.offsetWidth || 260;
  const hoehe = ziel.offsetHeight || 30;
  let x = r[2] + 12;
  let y = r[1] - hoehe - 8;
  if (y < 4) y = r[3] + 10;
  if (x + breite > a.v.breite - 4) x = Math.max(4, r[0] - breite - 12);
  y = Math.min(Math.max(4, y), a.v.hoehe - hoehe - 4);
  // Dem schwebenden Fenster ausweichen.
  const pal = a.teile.palette.knoten;
  if (!pal.hidden) {
    const p = [pal.offsetLeft, pal.offsetTop, pal.offsetLeft + pal.offsetWidth, pal.offsetTop + pal.offsetHeight];
    const ueberlappt = x < p[2] && x + breite > p[0] && y < p[3] && y + hoehe > p[1];
    if (ueberlappt) y = Math.max(4, p[1] - hoehe - 6);
  }
  ziel.style.left = `${Math.round(x)}px`;
  ziel.style.top = `${Math.round(y)}px`;
}
