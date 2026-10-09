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
 * Knoten. Der Kern hängt nicht von diesen Funktionen ab; sie sind
 * Eingabehilfe.
 *
 * EINE ECKE GEHÖRT IHREM ELEMENT:
 * Dass zwei Elemente sich einen Knoten teilen, ist Ablage, nicht Bedeutung.
 * Gewählt wird eine Ecke eines Elements («F1#2», die dritte Ecke von F1),
 * und verschoben wird, was gewählt ist: hängt an einem Knoten auch etwas,
 * das nicht mitkommt, bekommt das Bewegte einen eigenen Knoten. Wer eine
 * Bewehrungslinie verschiebt, deren Ende auf einer Polygonecke liegt, nimmt
 * die Ecke also nicht mit. Wer beide will, wählt beide -- mit einem Rahmen.
 *
 * Eine Art kann sagen, was mit ihr nicht geht oder was dazugehört:
 * `teilbar: false` (eine Linie, die man nicht teilen darf) und
 * `umkehren(e)` (was beim Umkehren mit getauscht wird).
 *
 * Alles hier ändert die übergebene Zeichnung -- gerufen wird es in einem
 * `veraenderer`, der das Projekt ändert.
 */

/** Auf einen Millionstel Millimeter: getippte Abstände sollen keine Rundungsreste hinterlassen. */
export const rund = (x) => Math.round(x * 1e6) / 1e6;

/** Der Schlüssel einer Ecke in der Auswahl: Element und Nummer der Ecke, «F1#2». */
export const eckeSchluessel = (kennung, i) => `${kennung}#${i}`;

/**
 * Was ein Schlüssel der Auswahl meint: `{kennung, i}` -- ein Element oder
 * ein Knoten (`i` null), oder die Ecke `i` eines Elements.
 */
export function auswahlTeil(schluessel) {
  const [kennung, i] = String(schluessel).split('#');
  return { kennung, i: i === undefined ? null : Number(i) };
}

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

  /** Setzt den `i`-ten Verweis eines Elements; ein Punkt hat nur den einen. */
  function verweisSetzen(art, e, i, k) {
    if (art.form === 'punkt') e.knoten = k;
    else if (art.form === 'linie') {
      if (i === 0) e.von = k; else e.bis = k;
    } else e.knoten[i] = k;
  }

  /**
   * Jede Ecke jedes Elements, mit ihrem Schlüssel für die Auswahl. Ein Punkt
   * hat keine eigenen Ecken: wählt man ihn, ist er selbst gewählt.
   */
  function ecken(z) {
    const liste = [];
    for (const { art, e } of elemente(z)) {
      verweise(art, e).forEach((k, i) => liste.push({
        schluessel: art.form === 'punkt' ? e.kennung : eckeSchluessel(e.kennung, i),
        art, e, i, knoten: k,
      }));
    }
    return liste;
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

  /** Gibt es noch, was der Schlüssel meint -- Element, Ecke oder Knoten? */
  function gibt(z, schluessel) {
    const { kennung, i } = auswahlTeil(schluessel);
    const da = verzeichnis(z).get(kennung);
    if (!da) return false;
    return i === null || (da.art !== null && i < verweise(da.art, da.e).length);
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
   * die anderen gehen, ihre Elemente hängen danach am ersten. Ablage, nicht
   * Bedeutung -- verschoben wird ohnehin je Element (`verschieben`).
   */
  function zusammenfuehren(z) {
    const orte = new Map();
    for (const k of z.knoten || []) {
      const schluessel = `${k[a]}|${k[b]}`;
      orte.set(schluessel, [...(orte.get(schluessel) || []), k.kennung]);
    }
    const weg = new Set();
    for (const [erster, ...andere] of orte.values()) {
      for (const k of andere) {
        umhaengen(z, k, erster);
        weg.add(k);
      }
    }
    if (weg.size) z.knoten = z.knoten.filter((k) => !weg.has(k.kennung));
  }

  /**
   * Löscht, was gewählt ist (Schlüssel wie in der Auswahl). Ein Element geht
   * ganz. Eine Ecke geht aus ihrem Umriss, solange drei bleiben; eine Linie
   * ohne ihr Ende ist keine mehr und geht ganz. Ein Knoten nimmt mit, was an
   * ihm hängt. Knoten, an denen danach nichts mehr hängt, gehen mit -- wenn
   * vorher etwas an ihnen hing.
   */
  function loeschen(z, ziele) {
    const knotenWeg = new Set((z.knoten || []).filter((k) => ziele.has(k.kennung))
      .map((k) => k.kennung));
    const eckenWeg = new Map();
    for (const s of ziele) {
      const { kennung, i } = auswahlTeil(s);
      if (i !== null) eckenWeg.set(kennung, new Set([...(eckenWeg.get(kennung) || []), i]));
    }
    const frei = new Set();
    for (const art of arten) {
      z[art.liste] = (z[art.liste] || []).filter((e) => {
        const ref = verweise(art, e);
        const weg = (k, i) => knotenWeg.has(k) || Boolean(eckenWeg.get(e.kennung)?.has(i));
        const betroffen = ref.some(weg);
        if (ziele.has(e.kennung) || (betroffen && art.form !== 'flaeche')) {
          ref.forEach((k) => frei.add(k));
          return false;
        }
        if (!betroffen) return true;
        ref.forEach((k, i) => { if (weg(k, i)) frei.add(k); });
        e.knoten = ref.filter((k, i) => !weg(k, i));
        if (new Set(e.knoten).size >= 3) return true;
        e.knoten.forEach((k) => frei.add(k));
        return false;
      });
    }
    const n = benutzung(z);
    z.knoten = (z.knoten || []).filter((k) => !knotenWeg.has(k.kennung)
      && !(frei.has(k.kennung) && !n.get(k.kennung)));
  }

  /**
   * Verschiebt, was gewählt ist, um `d` -- ganze Elemente, einzelne Ecken,
   * freie Knoten (Schlüssel wie in der Auswahl). Bewegt wird je Element:
   * hängt an einem Knoten auch etwas, das nicht mitkommt, bekommen die
   * bewegten Ecken einen eigenen, und der alte bleibt liegen. Danach ist, was
   * genau aufeinander liegt, wieder ein Knoten.
   */
  function verschieben(z, ziele, d) {
    const nutzer = new Map();
    const mit = new Map();
    for (const x of ecken(z)) {
      nutzer.set(x.knoten, (nutzer.get(x.knoten) || 0) + 1);
      if (ziele.has(x.e.kennung) || ziele.has(x.schluessel)) mit.set(x.knoten, [...(mit.get(x.knoten) || []), x]);
    }
    const knoten = new Map((z.knoten || []).map((k) => [k.kennung, k]));
    // Ein gewählter Knoten geht ganz, mit allem, was an ihm hängt.
    const bewegt = new Set([...ziele].filter((s) => knoten.has(s)).map((s) => knoten.get(s)));
    for (const [kennung, ecke] of mit) {
      const k = knoten.get(kennung);
      if (!k || bewegt.has(k)) continue;
      if (ecke.length === nutzer.get(kennung)) {
        bewegt.add(k);
        continue;
      }
      const eigener = { ...k, kennung: naechsteKennung(z, 'K') };
      z.knoten.push(eigener);
      ecke.forEach((x) => verweisSetzen(x.art, x.e, x.i, eigener.kennung));
      bewegt.add(eigener);
    }
    for (const k of bewegt) {
      k[a] = rund(k[a] + d[0]);
      k[b] = rund(k[b] + d[1]);
    }
    zusammenfuehren(z);
  }

  /**
   * Teilt eine Linie am Punkt `p`: sie endet dort, und eine zweite mit
   * denselben Eigenschaften läuft von dort zum alten Ende. Die zweite kommt
   * ans Ende der Liste -- die Namen der übrigen bleiben. Gibt ihre Kennung
   * zurück, oder null, wenn `p` ein Ende ist.
   */
  function linieTeilen(z, art, e, p) {
    const mitte = knotenAn(z, p);
    if (mitte === e.von || mitte === e.bis) return null;
    const zweite = { ...structuredClone(e), kennung: naechsteKennung(z, art.vorsilbe), von: mitte };
    e.bis = mitte;
    z[art.liste].push(zweite);
    return zweite.kennung;
  }

  /** Eine Ecke mehr im Umriss: `p` zwischen Ecke `i` und der nächsten. Gibt den Knoten zurück. */
  function eckeEinfuegen(z, e, i, p) {
    const k = knotenAn(z, p);
    if (e.knoten.includes(k)) return null;
    e.knoten.splice(i + 1, 0, k);
    return k;
  }

  /** Anfang und Ende einer Linie tauschen -- und was die App dazu tauscht (`art.umkehren`). */
  function umkehren(art, e) {
    [e.von, e.bis] = [e.bis, e.von];
    art.umkehren?.(e);
  }

  /**
   * Kopiert die gewählten Elemente und freien Knoten `anzahl` mal, je um `d`
   * weiter; einzelne Ecken kopiert es nicht. Die Kopien bekommen eigene
   * Knoten -- ausser dort, wo schon einer liegt. Gibt die Kennungen der
   * Kopien zurück.
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
    verschieben, kopieren, linieTeilen, eckeEinfuegen, umkehren, ecken, gibt,
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
