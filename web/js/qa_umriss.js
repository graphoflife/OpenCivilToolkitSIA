/**
 * qa_umriss.js -- Elemente der Querschnittsanalyse, deren Umriss nur der Kern kennt.
 *
 * Das sind das Stahlprofil (qa_profile.js) und die Blechverbunddecke
 * (qa_blechdecke.js). Beide hängen an einem Knoten -- das Profil mit seiner
 * Mitte, die Decke mit ihrer Ecke links unten -- und zeigen sich wie eine
 * Fläche: ein Klick in sie wählt sie, verschoben werden sie mit dem Knoten.
 *
 * WAS HIER GERECHNET WIRD -- UND WAS NICHT:
 * Nichts. Den Umriss, woran der Zeiger fängt und was sonst zum Bild gehört
 * -- die Linie eines Blechs --, schickt der Kern mit der Antwort zur
 * Zeichnung, unter dem Namen ihrer Liste (`profile`, `blechdecken`), dazu
 * die Lage, zu der es gehört. Hier wird es nur mitgeschoben: um das, was
 * der Knoten seit der Antwort gewandert ist, bis die nächste da ist.
 *
 * Bis 2026-11-27 konnte das nur das Profil, und die Zeichnung fragte an
 * acht Stellen eigens nach ihm.
 *
 * JEDE ART SAGT (neben dem, was das allgemeine Fenster von ihr wissen will):
 *   flaeche        wie ihre Fläche aussieht: `klasse`, beim Profil mit
 *                  `fill-rule`, damit sein Loch ausgespart bleibt
 *   darueber(...)  was über allen Flächen zu ihr gehört, oder nichts
 *   felder(...)    ihre Felder in der Seitenleiste, wie `felderVon`
 *   info(info)     was der Kern zu einer gewählten weiss, als Zeilen
 *   titel(e)       was sie ist, für den Titel des Fensters -- ohne e: mehrere
 *   lage           was ihr Knoten ist, vor «y» und «z»: «Mitte », «Ecke »
 */

/**
 * Was der Kern zuletzt über das Element `e` der Art `art` sagte -- auch in
 * einer älteren Antwort: es ist nur das Bild --, und wie seine Punkte mit dem
 * Knoten mitgehen. Null, solange er es nicht kennt: vor der ersten Antwort,
 * oder bei einem Profil, das die Tabelle nicht hat.
 */
export function gesehen(a, art, e) {
  const info = a.adapter.kern.antwort?.[art.liste]?.find((x) => x.kennung === e.kennung);
  const p = a.modell.lagen(a.adapter.zeichnung()).get(e.knoten);
  if (!info || !p) return null;
  const [dy, dz] = [p[0] - info.lage[0], p[1] - info.lage[1]];
  return { info, schieben: ([y, z]) => [y + dy, z + dz] };
}

/** Die Umrisse eines Elements in der Zeichnung, der erste aussen, die weiteren Löcher -- oder null. */
export function umrissVon(a, art, e) {
  const g = gesehen(a, art, e);
  return g && g.info.umriss.map((teil) => teil.map(g.schieben));
}

/** Woran der Zeiger an den Elementen der `arten` in der Zeichnung `z` fängt. */
export function fangVon(a, arten, z) {
  return arten.flatMap((art) => (z?.[art.liste] || []).flatMap((e) => {
    const g = gesehen(a, art, e);
    return g ? g.info.fang.map((p) => ({ p: g.schieben(p) })) : [];
  }));
}

/** Die äusseren Umrisse aller Elemente der `arten` -- für die Masse und den Rahmen des Bilds. */
export function aussenVon(a, arten, z) {
  return arten.flatMap((art) => (z?.[art.liste] || []).flatMap((e) => umrissVon(a, art, e)?.[0] || []));
}

/**
 * Setzt ein Element `e` der Art `art` mit seinem Knoten an `p` ein -- an
 * einen neuen Knoten oder einen, der dort liegt -- und wählt es.
 */
export function umrissEinsetzen(a, art, e, p) {
  let neu = null;
  a.aendern((z) => {
    const knoten = a.modell.knotenAn(z, p);
    neu = a.modell.naechsteKennung(z, art.vorsilbe);
    z[art.liste] = [...(z[art.liste] || []), { ...structuredClone(e), kennung: neu, knoten }];
  }, { auswahl: () => [neu] });
}
