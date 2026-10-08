/**
 * cad_modell.js -- Knoten und Elemente einer Zeichnung, ohne Bild.
 *
 * Eine Zeichnung ist ein Objekt mit einer Liste `knoten` und je Elementart
 * einer weiteren Liste. Was es für Arten gibt, sagt die App: jede Art nennt
 * ihre Liste, ihre Vorsilbe für Kennungen und ihre Form --
 *
 *   'punkt'    an einem Knoten           Feld `knoten` (eine Kennung)
 *   'linie'    von einem zum anderen     Felder `von`, `bis`
 *   'flaeche'  ein Umriss aus Knoten     Feld `knoten` (eine Liste)
 *
 * Zwei Regeln gelten wie im Kern (`opencivil/projekt/netz.py`), damit das
 * Fenster nichts anlegt, was der Kern anders sähe: eine Kennung kommt nie
 * wieder (die grösste plus eins), und genau gleiche Koordinaten sind ein
 * Knoten. Der Kern hängt nicht von diesen Funktionen ab; sie sind Eingabehilfe.
 *
 * Alles hier ändert die übergebene Zeichnung -- gerufen wird es in einem
 * `veraenderer`, der das Projekt ändert.
 */

/** Auf einen Millionstel Millimeter: getippte Abstände sollen keine Rundungsreste hinterlassen. */
export const rund = (x) => Math.round(x * 1e6) / 1e6;

/** Die Zahl hinter der Vorsilbe -- oder null. */
function nummer(kennung, vorsilbe) {
  if (typeof kennung !== 'string' || !kennung.startsWith(vorsilbe)) return null;
  const rest = kennung.slice(vorsilbe.length);
  return /^\d+$/.test(rest) ? Number(rest) : null;
}

/**
 * Die Werkzeuge auf einer Zeichnung, für die Arten und Achsen einer App.
 * `achsen` sind die Feldnamen der Koordinaten eines Knotens, etwa ['y', 'z'].
 */
export function cadModell({ arten, achsen }) {
  const [a, b] = achsen;
  const artVon = new Map(arten.map((x) => [x.liste, x]));

  const lage = (k) => [k[a], k[b]];

  /** Jedes Element mit seiner Art. */
  function* elemente(z) {
    for (const art of arten) {
      for (const e of z[art.liste] || []) yield { art, e };
    }
  }

  /** Auf welche Knoten ein Element zeigt. */
  function verweise(art, e) {
    if (art.form === 'punkt') return [e.knoten];
    if (art.form === 'linie') return [e.von, e.bis];
    return [...(e.knoten || [])];
  }

  /** Kennung -> [a, b] aller Knoten. */
  function lagen(z) {
    return new Map((z.knoten || []).map((k) => [k.kennung, lage(k)]));
  }

  /** Kennung -> {art, e} aller Elemente; Knoten mit art null. */
  function verzeichnis(z) {
    const v = new Map((z.knoten || []).map((k) => [k.kennung, { art: null, e: k }]));
    for (const x of elemente(z)) v.set(x.e.kennung, x);
    return v;
  }

  function naechsteKennung(z, vorsilbe) {
    let groesste = 0;
    const listen = vorsilbe === 'K' ? [z.knoten || []]
      : arten.filter((x) => x.vorsilbe === vorsilbe).map((x) => z[x.liste] || []);
    for (const liste of listen) {
      for (const e of liste) groesste = Math.max(groesste, nummer(e.kennung, vorsilbe) ?? 0);
    }
    return `${vorsilbe}${groesste + 1}`;
  }

  /** Der Knoten an `p` -- angelegt, wenn es dort noch keinen gibt. */
  function knotenAn(z, p) {
    const [u, w] = [rund(p[0]), rund(p[1])];
    const da = (z.knoten || []).find((k) => k[a] === u && k[b] === w);
    if (da) return da.kennung;
    const kennung = naechsteKennung(z, 'K');
    z.knoten = z.knoten || [];
    z.knoten.push({ kennung, [a]: u, [b]: w });
    return kennung;
  }

  /** Wie viele Elemente an jedem Knoten hängen. */
  function benutzung(z) {
    const n = new Map();
    for (const { art, e } of elemente(z)) {
      for (const k of new Set(verweise(art, e))) n.set(k, (n.get(k) || 0) + 1);
    }
    return n;
  }

  /** Ersetzt in allen Elementen den Verweis `alt` durch `neu`. */
  function umhaengen(z, alt, neu, nur = null) {
    for (const { art, e } of elemente(z)) {
      if (nur && !nur.has(e.kennung)) continue;
      if (art.form === 'punkt' && e.knoten === alt) e.knoten = neu;
      if (art.form === 'linie') {
        if (e.von === alt) e.von = neu;
        if (e.bis === alt) e.bis = neu;
      }
      if (art.form === 'flaeche') e.knoten = e.knoten.map((k) => (k === alt ? neu : k));
    }
  }

  /**
   * Führt Knoten mit genau gleichen Koordinaten zusammen: der erste bleibt,
   * die anderen gehen, ihre Elemente hängen danach am ersten.
   */
  function zusammenfuehren(z) {
    const erster = new Map();
    const weg = new Set();
    for (const k of z.knoten || []) {
      const schluessel = `${k[a]}|${k[b]}`;
      if (!erster.has(schluessel)) {
        erster.set(schluessel, k.kennung);
      } else {
        umhaengen(z, k.kennung, erster.get(schluessel));
        weg.add(k.kennung);
      }
    }
    if (weg.size) z.knoten = z.knoten.filter((k) => !weg.has(k.kennung));
  }

  /**
   * Löscht Elemente und Knoten. Ein Knoten nimmt mit, was an ihm hängt: ein
   * Punkt- oder Linienelement ganz, aus einem Umriss nur seine Ecke --
   * solange drei bleiben. Ein gelöschtes Element nimmt seine Knoten mit,
   * wenn sonst nichts mehr an ihnen hängt.
   */
  function loeschen(z, kennungen) {
    const knotenWeg = new Set((z.knoten || []).filter((k) => kennungen.has(k.kennung))
      .map((k) => k.kennung));
    const frei = new Set();
    for (const art of arten) {
      const liste = z[art.liste] || [];
      z[art.liste] = liste.filter((e) => {
        const ziele = verweise(art, e);
        if (kennungen.has(e.kennung)) {
          ziele.forEach((k) => frei.add(k));
          return false;
        }
        if (art.form === 'flaeche') {
          const rest = e.knoten.filter((k) => !knotenWeg.has(k));
          if (rest.length !== e.knoten.length) {
            e.knoten = rest;
            return new Set(rest).size >= 3;
          }
          return true;
        }
        return !ziele.some((k) => knotenWeg.has(k));
      });
    }
    const n = benutzung(z);
    z.knoten = (z.knoten || []).filter((k) => !knotenWeg.has(k.kennung)
      && !(frei.has(k.kennung) && !n.get(k.kennung)));
  }

  /** Die Knoten einer Auswahl: die gewählten und die der gewählten Elemente. */
  function knotenDer(z, kennungen) {
    const ziel = new Set();
    for (const k of z.knoten || []) if (kennungen.has(k.kennung)) ziel.add(k.kennung);
    for (const { art, e } of elemente(z)) {
      if (kennungen.has(e.kennung)) verweise(art, e).forEach((k) => ziel.add(k));
    }
    return ziel;
  }

  /** Verschiebt Knoten um `d`; was danach genau auf einem anderen liegt, wird eins mit ihm. */
  function verschieben(z, knoten, d) {
    for (const k of z.knoten || []) {
      if (!knoten.has(k.kennung)) continue;
      k[a] = rund(k[a] + d[0]);
      k[b] = rund(k[b] + d[1]);
    }
    zusammenfuehren(z);
  }

  /**
   * Kopiert die gewählten Elemente `anzahl` mal, je um `d` weiter. Die Kopien
   * bekommen eigene Knoten -- ausser dort, wo schon einer liegt. Gibt die
   * Kennungen der Kopien zurück.
   */
  function kopieren(z, kennungen, d, anzahl = 1) {
    const neu = [];
    const lage0 = lagen(z);
    const gewaehlt = [...elemente(z)].filter(({ e }) => kennungen.has(e.kennung));
    const einzelne = (z.knoten || []).filter((k) => kennungen.has(k.kennung));
    for (let i = 1; i <= anzahl; i += 1) {
      const versatz = [d[0] * i, d[1] * i];
      const nach = (k) => {
        const p = lage0.get(k);
        return knotenAn(z, [p[0] + versatz[0], p[1] + versatz[1]]);
      };
      for (const k of einzelne) neu.push(nach(k.kennung));
      for (const { art, e } of gewaehlt) {
        const kopie = structuredClone(e);
        kopie.kennung = naechsteKennung(z, art.vorsilbe);
        if (art.form === 'punkt') kopie.knoten = nach(e.knoten);
        if (art.form === 'linie') { kopie.von = nach(e.von); kopie.bis = nach(e.bis); }
        if (art.form === 'flaeche') kopie.knoten = e.knoten.map(nach);
        z[art.liste].push(kopie);
        neu.push(kopie.kennung);
      }
    }
    return neu;
  }

  return {
    arten, achsen, artVon, lage, elemente, verweise, lagen, verzeichnis,
    naechsteKennung, knotenAn, benutzung, umhaengen, zusammenfuehren, loeschen,
    knotenDer, verschieben, kopieren,
  };
}

// ===========================================================================
// Ebene Geometrie, nur zum Treffen und Fangen
// ===========================================================================

export function abstand(p, q) {
  return Math.hypot(p[0] - q[0], p[1] - q[1]);
}

/** Der nächste Punkt auf der Strecke s-e -- und wie weit er entlang liegt (0 bis 1). */
export function aufStrecke(p, s, e) {
  const [dy, dz] = [e[0] - s[0], e[1] - s[1]];
  const l2 = dy * dy + dz * dz;
  const t = l2 ? Math.max(0, Math.min(1, ((p[0] - s[0]) * dy + (p[1] - s[1]) * dz) / l2)) : 0;
  return { q: [s[0] + t * dy, s[1] + t * dz], t };
}

/** Der Fusspunkt von p auf der Geraden durch `durch` in Richtung `r` (ohne Grenzen). */
export function aufGerade(p, durch, r) {
  const l2 = r[0] * r[0] + r[1] * r[1] || 1;
  const t = ((p[0] - durch[0]) * r[0] + (p[1] - durch[1]) * r[1]) / l2;
  return [durch[0] + t * r[0], durch[1] + t * r[1]];
}

/** Wo sich zwei Strecken schneiden -- oder null. Berührung an den Enden zählt. */
export function schnitt([p1, p2], [q1, q2]) {
  const r = [p2[0] - p1[0], p2[1] - p1[1]];
  const s = [q2[0] - q1[0], q2[1] - q1[1]];
  const nenner = r[0] * s[1] - r[1] * s[0];
  if (Math.abs(nenner) < 1e-12) return null;
  const t = ((q1[0] - p1[0]) * s[1] - (q1[1] - p1[1]) * s[0]) / nenner;
  const u = ((q1[0] - p1[0]) * r[1] - (q1[1] - p1[1]) * r[0]) / nenner;
  if (t < -1e-9 || t > 1 + 1e-9 || u < -1e-9 || u > 1 + 1e-9) return null;
  return [p1[0] + t * r[0], p1[1] + t * r[1]];
}

/** Liegt p im Polygon? Gerade-ungerade-Regel. */
export function innen(p, punkte) {
  let drin = false;
  for (let i = 0, j = punkte.length - 1; i < punkte.length; j = i, i += 1) {
    const [yi, zi] = punkte[i];
    const [yj, zj] = punkte[j];
    if ((zi > p[1]) !== (zj > p[1])
        && p[0] < ((yj - yi) * (p[1] - zi)) / (zj - zi) + yi) drin = !drin;
  }
  return drin;
}

/** Fläche eines Polygons, mit Vorzeichen -- nur um das kleinere zuerst zu treffen. */
export function flaecheVon(punkte) {
  let s = 0;
  for (let i = 0, j = punkte.length - 1; i < punkte.length; j = i, i += 1) {
    s += punkte[j][0] * punkte[i][1] - punkte[i][0] * punkte[j][1];
  }
  return s / 2;
}
