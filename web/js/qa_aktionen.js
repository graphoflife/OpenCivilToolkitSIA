/**
 * qa_aktionen.js -- was das Zeichenfenster der Querschnittsanalyse neben der Auswahl anbietet.
 *
 * Gewählte Bewehrung lässt sich in die Überdeckung schieben, gewählte
 * Hilfslinien, die einen Umriss schliessen, werden eine Fläche -- je ein
 * Knopf neben der Auswahl (cad_fenster.js). Bis 2026-11-27 stand das in
 * qa_zeichnung.js.
 *
 * WAS HIER GERECHNET WIRD -- UND WAS NICHT:
 * Wohin die Überdeckung einen Stab schiebt, sagt der Kern in seiner Antwort
 * zur Zeichnung (`ueberdeckt`); hier wird er nur dorthin verschoben. Ob die
 * Hilfslinien einen Umriss schliessen, ist Zeichnen, keine Rechnung.
 */

import { frischeAntwort } from './cad_app.js';
import { eckeSchluessel } from './cad_modell.js';
import { melden } from './dom.js';
import { eintragVon } from './zustand.js';

/**
 * Die gewählten Hilfslinien als ein geschlossener Umriss -- seine Knoten der
 * Reihe nach, oder null. Jede Ecke hat genau zwei Linien, und alle hängen
 * zusammen.
 */
function umlauf(z, kennungen) {
  const linien = (z.hilfslinien || []).filter((h) => kennungen.has(h.kennung));
  if (linien.length < 3 || linien.length !== kennungen.size) return null;
  const nachbarn = new Map();
  for (const h of linien) {
    if (h.von === h.bis) return null;
    nachbarn.set(h.von, [...(nachbarn.get(h.von) || []), h.bis]);
    nachbarn.set(h.bis, [...(nachbarn.get(h.bis) || []), h.von]);
  }
  if ([...nachbarn.values()].some((n) => n.length !== 2)) return null;
  const start = linien[0].von;
  const reihe = [start];
  let vorher = null;
  let jetzt = start;
  for (;;) {
    const weiter = nachbarn.get(jetzt).find((k) => k !== vorher);
    if (weiter === start) break;
    if (reihe.includes(weiter)) return null;
    reihe.push(weiter);
    vorher = jetzt;
    jetzt = weiter;
  }
  return reihe.length === nachbarn.size ? reihe : null;
}

/**
 * Schiebt die gewählte Bewehrung in die Überdeckung -- dorthin, wo der Kern
 * sagt (`ueberdeckt` in seiner Antwort zur Zeichnung). Ein Stab als Ganzes,
 * eine Linie Ende für Ende; was sonst am selben Knoten hängt, bleibt liegen.
 * Ein Schritt für «Rückgängig».
 */
function ueberdeckungBeachten(a, bewehrung) {
  const geo = frischeAntwort(a);
  if (!geo) {
    melden('Die Zeichnung wird noch geprüft – gleich noch einmal.');
    return;
  }
  const ziele = new Map([...geo.staebe, ...geo.spannglieder, ...geo.linien].map((x) => [x.kennung, x.ueberdeckt]));
  const lagen = a.modell.lagen(eintragVon(a.qa.kennung));
  const schritte = [];
  for (const { art, e } of bewehrung) {
    const ziel = ziele.get(e.kennung);
    if (!ziel) continue;
    const enden = art.form === 'punkt' ? [[e.kennung, e.knoten, ziel]]
      : [[eckeSchluessel(e.kennung, 0), e.von, ziel[0]], [eckeSchluessel(e.kennung, 1), e.bis, ziel[1]]];
    for (const [schluessel, knoten, p] of enden) {
      const q = lagen.get(knoten);
      const d = [p[0] - q[0], p[1] - q[1]];
      if (Math.hypot(d[0], d[1]) > 1e-6) schritte.push([schluessel, d]);
    }
  }
  if (!schritte.length) {
    melden(bewehrung.some(({ e }) => ziele.get(e.kennung))
      ? 'Die Bewehrung liegt schon in der Überdeckung.'
      : 'Für diese Bewehrung gilt keine Überdeckung, oder das Polygon ist dafür zu klein.');
    return;
  }
  a.aendern((zz) => {
    for (const [schluessel, d] of schritte) a.modell.verschieben(zz, new Set([schluessel]), d);
  });
}

/**
 * Was neben der Auswahl angeboten wird: «Überdeckung beachten», wo
 * Bewehrung gewählt ist und ein Polygon eine Überdeckung hat, «Fläche
 * bilden», wo die gewählten Hilfslinien einen Umriss schliessen.
 */
export function aktionen(a) {
  const z = eintragVon(a.qa.kennung);
  const liste = [];
  // Bewehrung gewählt, und ein Polygon hat eine Überdeckung: sie beachten.
  const verzeichnis = a.modell.verzeichnis(z);
  const bewehrung = [...a.auswahl].map((k) => verzeichnis.get(k))
    .filter((x) => x && ['staebe', 'spannglieder', 'stablinien'].includes(x.art?.liste));
  if (bewehrung.length && z.flaechen.some((f) => f.ueberdeckung > 0)) {
    liste.push({
      zeichen: '⇲', text: 'Überdeckung beachten',
      titel: 'Die Bewehrung so verschieben, dass sie mit ihrem Radius gerade ganz in der Überdeckung liegt',
      tun: () => ueberdeckungBeachten(a, bewehrung),
    });
  }
  const reihe = umlauf(z, a.auswahl);
  if (reihe) {
    // Was entsteht, sagt die Vorgabe des Werkzeugs Polygon -- bis 2026-11-19
    // sagte der Knopf es nicht.
    const entsteht = a.adapter.neuText(a, 'polygon');
    liste.push({
      zeichen: '▱', text: 'Fläche bilden',
      titel: `Die geschlossenen Hilfslinien werden eine ${entsteht} – wie die Vorgabe des Werkzeugs Polygon`,
      tun: () => {
        const weg = new Set(a.auswahl);
        let neu = null;
        a.aendern((zz) => {
          neu = a.adapter.flaecheAnlegen(a, zz, reihe);
          zz.hilfslinien = zz.hilfslinien.filter((h) => !weg.has(h.kennung));
        }, { auswahl: () => [neu] });
      },
    });
  }
  return liste;
}

