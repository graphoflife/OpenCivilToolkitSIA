/**
 * cad_befehle.js -- was mit den Punkten geschieht, die die Eingabe liefert.
 *
 * Ein Befehl fragt nach Punkten und baut daraus etwas: einen Knoten, eine
 * Linie, einen Umriss, eine Verschiebung. Wie ein Punkt entsteht, weiss er
 * nicht -- das ist in `cad_eingabe.js` für alle gleich. Was er anlegt, fragt
 * er die App (`a.adapter`): eine Linie ist im Querschnitt eine Bewehrung,
 * eine Schubwand oder eine Hilfslinie, je nachdem, was im Fenster eingestellt
 * ist.
 *
 * Jeder Befehl hat dieselbe Gestalt:
 *
 *   frage(a)          was er gerade braucht -- steht im schwebenden Fenster
 *   hinweis           was er sonst kann -- steht in der Statuszeile (nicht jeder)
 *   punkt(a, erg)     ein Punkt ist da: {p, art, knoten?}
 *   vorschau(a, g)    was er bis zum Zeiger zeigt
 *   enter(a)          Enter ohne getippte Werte: fertig, schliessen
 *   zurueck(a)        Esc: einen Schritt zurück -- false, wenn nichts mehr da ist
 *   rueckschritt(a)   Rücktaste: den letzten Punkt weg
 *
 * Jede Änderung geht durch `a.aendern(veraenderer, {auswahl})`: ein Schritt
 * für «Rückgängig» je fertigem Stück, nie je Zwischenpunkt.
 */

import {
  nachBild, pfad, text, zahlText,
} from './cad_ansicht.js';
import { abstand } from './cad_modell.js';
import { svgEl } from './dom.js';
import { NAEHE } from './cad_eingabe.js';

/** Ein Zettel am Zeiger: Länge und Abstände des Stücks, das gerade entsteht. */
function zettel(g, [x, y], zeilen) {
  zeilen.forEach((z, i) => g.append(text(x + 14, y + 18 + i * 13, z, 'cad-zetteltext', 'start')));
}

function streckenzettel(a, g, p, q) {
  const [x, y] = a.adapter.achsen;
  zettel(g, nachBild(a.v, q), [
    `L = ${zahlText(abstand(p, q))}`,
    `Δ${x} = ${zahlText(q[0] - p[0])}  Δ${y} = ${zahlText(q[1] - p[1])}`,
  ]);
}

/** Ein Knoten für einen Punkt der Eingabe -- der gefangene, wenn es einer war. */
function knotenFuer(a, z, erg) {
  if (erg.knoten && (z.knoten || []).some((k) => k.kennung === erg.knoten)) return erg.knoten;
  return a.modell.knotenAn(z, erg.p);
}

// ===========================================================================
// Knoten
// ===========================================================================

export function knotenBefehl() {
  return {
    name: 'knoten',
    neu: 'knoten',
    frage: (a) => `${a.adapter.neuText(a, 'knoten')}: Punkt setzen`,
    punkt(a, erg) {
      let neu = null;
      a.aendern((z) => {
        const k = knotenFuer(a, z, erg);
        neu = a.adapter.punktAnlegen(a, z, k) || k;
      }, { auswahl: () => [neu] });
      a.eingabe.bezug = erg.p;
    },
    vorschau(a, g) {
      const f = a.zeiger?.fang;
      if (f) a.adapter.punktVorschau?.(a, g, f.p);
    },
    enter: () => false,
    zurueck: () => false,
  };
}

// ===========================================================================
// Linie -- als Kette: das Ende ist der nächste Anfang
// ===========================================================================

export function linienBefehl() {
  return {
    name: 'linie',
    neu: 'linie',
    start: null,
    frage(a) {
      return `${a.adapter.neuText(a, 'linie')}: ${this.start ? 'Endpunkt' : 'Anfangspunkt'}`;
    },
    punkt(a, erg) {
      if (!this.start) {
        this.start = erg;
      } else if (abstand(this.start.p, erg.p) > 1e-9) {
        const start = this.start;
        let neu = null;
        a.aendern((z) => {
          const von = knotenFuer(a, z, start);
          const bis = knotenFuer(a, z, erg);
          neu = a.adapter.linieAnlegen(a, z, von, bis);
        }, { auswahl: () => [neu] });
        this.start = { ...erg, knoten: undefined };
      }
      a.eingabe.bezug = erg.p;
    },
    vorschau(a, g) {
      const f = a.zeiger?.fang;
      if (!this.start || !f) return;
      a.adapter.linienVorschau?.(a, g, this.start.p, f.p);
      g.append(svgEl('path', { d: pfad(a.v, [this.start.p, f.p], false), class: 'cad-entwurf' }));
      streckenzettel(a, g, this.start.p, f.p);
    },
    enter() {
      if (!this.start) return false;
      this.start = null;
      return true;
    },
    zurueck() {
      if (!this.start) return false;
      this.start = null;
      return true;
    },
  };
}

// ===========================================================================
// Polygon -- ein Umriss, der eine Fläche wird
// ===========================================================================

export function polygonBefehl() {
  return {
    name: 'polygon',
    neu: 'flaeche',
    hinweis: 'Rücktaste nimmt den letzten Punkt zurück',
    punkte: [],
    frage(a) {
      const n = this.punkte.length;
      if (!n) return `${a.adapter.neuText(a, 'flaeche')}: erster Punkt`;
      return n < 3 ? `Punkt ${n + 1}` : `Punkt ${n + 1} -- oder Enter schliesst`;
    },
    punkt(a, erg) {
      const n = this.punkte.length;
      if (n >= 3) {
        const erster = this.punkte[0];
        const zu = (erg.knoten && erg.knoten === erster.knoten)
          || abstand(nachBild(a.v, erster.p), nachBild(a.v, erg.p)) <= NAEHE * 0.5;
        if (zu) { this.schliessen(a); return; }
      }
      const letzter = this.punkte[n - 1];
      if (!letzter || abstand(letzter.p, erg.p) > 1e-9) this.punkte.push(erg);
      a.eingabe.bezug = erg.p;
    },
    schliessen(a) {
      if (this.punkte.length < 3) return;
      const punkte = this.punkte;
      this.punkte = [];
      let neu = null;
      a.aendern((z) => {
        const knoten = punkte.map((erg) => knotenFuer(a, z, erg));
        neu = a.adapter.flaecheAnlegen(a, z, knoten);
      }, { auswahl: () => [neu] });
    },
    vorschau(a, g) {
      const f = a.zeiger?.fang;
      const punkte = this.punkte.map((x) => x.p);
      if (!punkte.length) return;
      const bis = f ? [...punkte, f.p] : punkte;
      g.append(svgEl('path', { d: pfad(a.v, bis, false), class: 'cad-entwurf' }));
      if (f && punkte.length >= 2) {
        g.append(svgEl('path', { d: pfad(a.v, [f.p, punkte[0]], false), class: 'cad-entwurf-schluss' }));
      }
      for (const p of punkte) {
        const [x, y] = nachBild(a.v, p);
        g.append(svgEl('circle', { cx: x, cy: y, r: 3, class: 'cad-entwurfpunkt' }));
      }
      if (f) streckenzettel(a, g, punkte.at(-1), f.p);
    },
    enter(a) {
      if (this.punkte.length < 3) return false;
      this.schliessen(a);
      return true;
    },
    zurueck() {
      if (!this.punkte.length) return false;
      this.punkte = [];
      return true;
    },
    rueckschritt(a) {
      this.punkte.pop();
      a.eingabe.bezug = this.punkte.at(-1)?.p || null;
      return true;
    },
  };
}

// ===========================================================================
// Verschieben und Kopieren -- Basispunkt, dann Ziel
// ===========================================================================

/** Die Geometrie einer Auswahl, um sie verschoben vorzuzeigen. */
function auswahlGeometrie(a) {
  const z = a.adapter.zeichnung();
  const m = a.modell;
  const lagen = m.lagen(z);
  const strecken = [];
  const punkte = [];
  for (const { art, e } of m.elemente(z)) {
    if (!a.auswahl.has(e.kennung)) continue;
    const orte = m.verweise(art, e).map((k) => lagen.get(k)).filter(Boolean);
    if (art.form === 'punkt') punkte.push(...orte);
    else if (art.form === 'linie') strecken.push(orte);
    else strecken.push([...orte, orte[0]]);
  }
  for (const k of z.knoten || []) if (a.auswahl.has(k.kennung)) punkte.push(m.lage(k));
  return { strecken, punkte };
}

function bewegungsBefehl(kopie) {
  return {
    name: kopie ? 'kopieren' : 'verschieben',
    kopie,
    basis: null,
    anzahl: 1,
    frage(a) {
      const was = kopie ? 'Kopieren' : 'Verschieben';
      return this.basis ? `${was}: Zielpunkt` : `${was}: Basispunkt`;
    },
    punkt(a, erg) {
      if (!this.basis) {
        this.basis = erg.p;
        a.eingabe.bezug = erg.p;
        return;
      }
      const d = [erg.p[0] - this.basis[0], erg.p[1] - this.basis[1]];
      const auswahl = new Set(a.auswahl);
      let ergebnis = null;
      a.aendern((z) => {
        if (kopie) {
          ergebnis = a.modell.kopieren(z, auswahl, d, Math.max(1, Math.round(this.anzahl) || 1));
        } else {
          a.modell.verschieben(z, a.modell.knotenDer(z, auswahl), d);
          ergebnis = [...auswahl];
        }
      }, { auswahl: () => ergebnis });
      this.basis = null;
      a.eingabe.bezug = erg.p;
      a.ende();
    },
    vorschau(a, g) {
      const f = a.zeiger?.fang;
      if (!this.basis || !f) return;
      const d = [f.p[0] - this.basis[0], f.p[1] - this.basis[1]];
      const { strecken, punkte } = auswahlGeometrie(a);
      const n = kopie ? Math.max(1, Math.round(this.anzahl) || 1) : 1;
      for (let i = 1; i <= n; i += 1) {
        const schieben = (p) => [p[0] + d[0] * i, p[1] + d[1] * i];
        for (const s of strecken) {
          g.append(svgEl('path', { d: pfad(a.v, s.map(schieben), false), class: 'cad-verschoben' }));
        }
        for (const p of punkte) {
          const [x, y] = nachBild(a.v, schieben(p));
          g.append(svgEl('circle', { cx: x, cy: y, r: 3.5, class: 'cad-verschoben' }));
        }
      }
      g.append(svgEl('path', { d: pfad(a.v, [this.basis, f.p], false), class: 'cad-vektor' }));
      streckenzettel(a, g, this.basis, f.p);
    },
    enter: () => false,
    zurueck() {
      if (!this.basis) return false;
      this.basis = null;
      return true;
    },
  };
}

export const verschiebenBefehl = () => bewegungsBefehl(false);
export const kopierenBefehl = () => bewegungsBefehl(true);
