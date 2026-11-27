/**
 * ds_zeichnung.js -- das Zeichenfenster einer Durchstanzstelle: der Adapter.
 *
 * Gezeichnet werden Aussparungen: Polygone im Grundriss, in mm, x nach
 * rechts, y nach oben, die Achse der Stütze im Ursprung -- wie im Kern
 * (opencivil/projekt/durchstanzen.py). Ein Werkzeug zeichnet sie, ein
 * zweites setzt Hilfspunkte zum Fangen. Ecken und Knoten verschiebt man wie
 * im Querschnitt: wählen, dann V oder die Felder in der Seitenleiste.
 *
 * Darunter liegt, was der Kern zuletzt gerechnet hat: Stütze oder Wand,
 * Plattenrand und Nachweisschnitt (ds_grundriss.js). Die Ecken der Stütze
 * fangen den Zeiger. Ändert sich eine Aussparung, rechnet die nächste Lösung
 * den Schnitt neu -- bis dahin steht der alte da.
 *
 * WAS HIER GERECHNET WIRD -- UND WAS NICHT:
 * Nichts, was in die Rechnung geht. Ob eine Aussparung den Schnitt mindert,
 * wie weit ihr Schatten reicht und ob sie gültig ist, sagt der Kern.
 */

import { auswahlEigenschaften, cadApp, umrissVon } from './cad_app.js';
import { nachBild, nachWelt } from './cad_ansicht.js';
import { cadBereich } from './cad_fenster.js';
import { knotenname } from './cad_modell.js';
import { el } from './dom.js';
import { aussparungTeile, grundrissTeile, grundrissUmfang } from './ds_grundriss.js';
import { eintragVon, zustand } from './zustand.js';

/** Eine Art: die Aussparung, eine Fläche aus Knoten. */
const ARTEN = [{ liste: 'aussparungen', form: 'flaeche', vorsilbe: 'A', rang: 0 }];

/** In mm, wie der Querschnitt -- aber mit dem Raster eines Grundrisses. */
const EINSTELLUNG = {
  werkzeuge: [
    { name: 'aussparung', text: 'Aussparung', zeichen: 'cad-polygon', taste: 'a', form: 'polygon',
      titel: 'Aussparung: die Ecken der Reihe nach – Enter oder ein Klick auf die erste schliesst' },
    { name: 'hilfspunkt', text: 'Hilfspunkt', zeichen: 'cad-hilfspunkt', taste: 'k', form: 'knoten',
      titel: 'Hilfspunkt: ein Knoten ohne Aussparung, zum Fangen' },
  ],
  einheit: 'mm',
  raster: { stufen: [5, 10, 25, 50, 100, 250], vorgabe: 50 },
  stellen: 0,
  massstab: [0.01, 20],
};

/** Was der Kern zuletzt zu dieser Stelle gerechnet hat -- oder null. */
function situationVon(kennung) {
  return zustand.loesung?.zeichendaten?.[kennung] || null;
}

/** Das Zeichenfenster einer Stelle, samt einer Zeile darunter. Die Tafel ruft das bei jedem Neubau. */
export function zeichenbereich(stelle) {
  return cadBereich(fensterVon(stelle.kennung), [el('p.cad-hinweis-klein', {
    text: 'Ausgezogen, was vom Nachweisschnitt zählt; gestrichelt, was nicht zählt. '
      + 'Der Schnitt kommt aus der letzten Rechnung.',
  })]);
}

/** Was der Adapter einer Stelle über die gemeinsame Grundlage hinaus weiss (cad_app.js). */
function adapter(kennung) {
  return {
    einstellung: EINSTELLUNG,
    achsen: ['x', 'y'],
    arten: ARTEN,
    name: elementname,
    neuText: (a, werkzeug) => (werkzeug === 'aussparung' ? 'Aussparung' : 'Hilfspunkt'),
    // Ein Hilfspunkt ist der Knoten selbst und legt nichts an.
    punktAnlegen: () => null,
    flaecheAnlegen: (a, z, knoten) => {
      const neu = a.modell.naechsteKennung(z, 'A');
      z.aussparungen.push({ kennung: neu, knoten });
      return neu;
    },
    zeichnen: (a, g) => zeichnen(a, g, kennung),
    fangpunkte: () => (situationVon(kennung)?.umriss || []).map((p) => ({ p })),
    umriss: () => umriss(kennung),
    eigenschaften,
  };
}

/** Die Zeichenfenster der Durchstanzstellen, je Kennung eines. */
const fensterVon = cadApp('ds', adapter);

/** «Aussparung A1», «Knoten K3». */
function elementname(a, kennung) {
  return knotenname(kennung) ?? (/^A\d+$/.test(kennung) ? `Aussparung ${kennung}` : kennung);
}

/**
 * Unten der Grundriss aus der letzten Lösung, darin die Aussparungen, wie sie
 * gerade gezeichnet sind -- auch die, die der Kern noch nicht kennt.
 */
function zeichnen(a, g, kennung) {
  const z = eintragVon(kennung);
  const lagen = a.modell.lagen(z);
  const aussparungen = (z.aussparungen || [])
    .map((f) => f.knoten.map((k) => lagen.get(k)))
    .filter((punkte) => punkte.length >= 2 && punkte.every(Boolean));
  const bild = (p) => nachBild(a.v, p);
  const s = situationVon(kennung);
  if (s) {
    const sicht = [nachWelt(a.v, [0, a.v.hoehe]), nachWelt(a.v, [a.v.breite, 0])];
    g.append(...grundrissTeile(s, bild, sicht, aussparungen));
  } else {
    for (const punkte of aussparungen) g.append(...aussparungTeile(punkte.map(bild)));
  }
}

/** Was «Alles zeigen» ins Bild nimmt: der Grundriss der letzten Lösung und alle Knoten. */
function umriss(kennung) {
  const s = situationVon(kennung);
  const punkte = (eintragVon(kennung)?.knoten || []).map((k) => [k.x, k.y]);
  if (s) punkte.push(...grundrissUmfang(s));
  return umrissVon(punkte, [[-1000, -1000], [1000, 1000]]);
}

/**
 * Die Seitenleiste zur Auswahl (cad_app.js): Ecken und Knoten mit
 * ihrer Lage, Aussparungen mit dem, was man mit ihnen tun kann.
 */
function eigenschaften(a) {
  return auswahlEigenschaften(a, { sonst: aussparungEigenschaften });
}

/** Gewählte Aussparungen: was man mit ihnen tun kann -- Felder haben sie keine. */
function aussparungEigenschaften(a, z, kennungen) {
  const einzeln = kennungen.length === 1;
  return {
    titel: einzeln ? elementname(a, kennungen[0]) : `${kennungen.length} Aussparungen`,
    inhalt: [el('p.cad-hinweis-klein', {
      text: einzeln ? 'Eine Ecke verschiebt man, indem man auf sie klickt; die ganze Aussparung mit V. '
        + 'Entf löscht sie.' : 'Verschieben mit V, kopieren mit C, löschen mit Entf.',
    })],
  };
}
