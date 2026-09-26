/**
 * dom.js -- Kleine Helfer für den Aufbau von DOM-Bäumen.
 *
 * Kein Rahmenwerk, keine Übersetzung: die Oberfläche ist klein genug, dass
 * ausgeschriebenes DOM lesbarer bleibt als eine Vorlagensprache -- und sie
 * läuft ohne Bauschritt direkt im Browser.
 *
 * Durchgehend wird `textContent` gesetzt und nie `innerHTML` mit fremden
 * Zeichenketten. Namen von Materialien und Nachweisen kommen vom Benutzer und
 * dürfen kein Markup einschleusen können.
 */

/**
 * Baut ein Element.
 * @param {string} tag        z.B. 'div' oder 'div.klasse.andere'
 * @param {Object} [eigen]    Attribute; `class`, `text`, `html`, `dataset`,
 *                            `on` (Ereignisse) und `style` werden gesondert behandelt
 * @param {Array}  [kinder]
 */
export function el(tag, eigen = {}, kinder = []) {
  const [name, ...klassen] = tag.split('.');
  const knoten = document.createElement(name || 'div');
  if (klassen.length) knoten.classList.add(...klassen);

  for (const [schluessel, wert] of Object.entries(eigen)) {
    if (wert === null || wert === undefined || wert === false) continue;
    if (schluessel === 'class') knoten.classList.add(...String(wert).split(' ').filter(Boolean));
    else if (schluessel === 'text') knoten.textContent = String(wert);
    else if (schluessel === 'html') knoten.innerHTML = wert;
    else if (schluessel === 'dataset') Object.assign(knoten.dataset, wert);
    else if (schluessel === 'style') Object.assign(knoten.style, wert);
    else if (schluessel === 'on') {
      for (const [art, hoerer] of Object.entries(wert)) knoten.addEventListener(art, hoerer);
    } else if (schluessel in knoten) knoten[schluessel] = wert;
    else knoten.setAttribute(schluessel, wert);
  }

  for (const kind of [].concat(kinder)) {
    if (kind === null || kind === undefined || kind === false) continue;
    knoten.append(kind instanceof Node ? kind : document.createTextNode(String(kind)));
  }
  return knoten;
}

/**
 * Dasselbe für SVG: eigener Namensraum, sonst zeichnet der Browser nichts.
 *
 * Steht neben `el`, weil es dieselbe Aufgabe hat. Vorher lag es in
 * `diagramm.js` -- solange dort alles gezeichnet wurde, fiel das nicht auf.
 */
export function svgEl(name, attribute = {}) {
  const knoten = document.createElementNS('http://www.w3.org/2000/svg', name);
  for (const [k, v] of Object.entries(attribute)) {
    if (v !== null && v !== undefined) knoten.setAttribute(k, String(v));
  }
  return knoten;
}

/**
 * Eine Farbe aus dem Stil, etwa `stilfarbe('richtung-x')` für `--richtung-x`.
 *
 * Für die Zeichnungen, die ihre Farben als SVG-Attribut setzen: sie nehmen
 * den fertigen Wert aus `stil.css`, damit jede Farbe nur dort festgelegt ist.
 * Vorher stand das Blau der x-Lagen einmal im Stil und einmal hier -- und
 * eine neue Farbe hätte die Maske umgefärbt und das Querschnittsbild nicht.
 */
export function stilfarbe(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(`--${name}`).trim();
}

export function leeren(knoten) {
  while (knoten.firstChild) knoten.removeChild(knoten.firstChild);
  return knoten;
}

export function ersetzen(knoten, ...kinder) {
  leeren(knoten).append(...kinder.filter(Boolean));
  return knoten;
}

/**
 * Nächster Wert in einer Richtung -- entweder aus einer Stufenliste oder in
 * gleichmässigen Schritten.
 *
 * Bei Stufen wird der nächste Listeneintrag genommen, bei gleichmässigen
 * Schritten das nächste Vielfache. Ein Wert zwischen zwei Stufen rastet also
 * beim ersten Druck ein, statt die Zwischenlage mitzuschleppen.
 *
 * Nach unten ist hier nichts begrenzt. Wo null die Grenze ist -- Durchmesser,
 * Teilung, Stabzahl --, sagt das Feld es über `min`. Eine eingebaute Sperre bei
 * null hielt dagegen auch die Schnittgrössen fest, und ein Moment darf negativ
 * sein.
 */
export function naechsteStufe(wert, richtung, { stufen, schritt = 1 } = {}) {
  const jetzt = Number.isFinite(wert) ? wert : 0;

  if (stufen?.length) {
    const sortiert = [...stufen].sort((a, b) => a - b);
    const naechster = richtung > 0
      ? sortiert.find((s) => s > jetzt + 1e-9)
      : [...sortiert].reverse().find((s) => s < jetzt - 1e-9);
    return naechster ?? (richtung > 0 ? sortiert.at(-1) : sortiert[0]);
  }

  // Auf das nächste Vielfache von `schritt` einrasten -- gerundet auf die
  // Stellen des Schritts: 6 · 0.05 ist in Gleitkomma 0.30000000000000004, und
  // genau das stand dann im Feld.
  const stufe = richtung > 0
    ? Math.floor(jetzt / schritt + 1e-9) + 1
    : Math.ceil(jetzt / schritt - 1e-9) - 1;
  const stellen = (String(schritt).split('.')[1] || '').length;
  return Number((stufe * schritt).toFixed(stellen));
}

/**
 * Zahlenfeld mit einheitlichem Verhalten.
 *
 * Die Pfeile sind eigene Knöpfe statt des Browser-Drehfelds, weil das nur
 * gleichmässige Schritte kann. Durchmesser springen aber von 22 auf 26 und
 * von 30 auf 34 -- eine Liste, kein Raster.
 *
 * @param {number[]} [stufen]  erlaubte Werte; sonst wird `schritt` verwendet
 */
export function zahlfeld({
  wert, schritt = 1, stufen, min, max, beiAenderung, titel, readonly,
}) {
  const melden = (neu) => beiAenderung(neu);

  const feld = el('input', {
    type: 'number',
    value: wert ?? '',
    step: 'any',
    min, max, title: titel, readOnly: !!readonly,
    on: {
      change: (e) => {
        const roh = e.target.value.trim();
        melden(roh === '' ? null : Number(roh));
      },
      keydown: (e) => {
        if (readonly || (e.key !== 'ArrowUp' && e.key !== 'ArrowDown')) return;
        e.preventDefault();
        ruecken(e.key === 'ArrowUp' ? 1 : -1);
      },
    },
  });

  const ruecken = (richtung) => {
    if (readonly) return;
    const jetzt = feld.value.trim() === '' ? null : Number(feld.value);
    let neu = naechsteStufe(jetzt ?? 0, richtung, { stufen, schritt });
    if (min !== undefined && min !== null) neu = Math.max(neu, min);
    if (max !== undefined && max !== null) neu = Math.min(neu, max);
    feld.value = String(neu);
    melden(neu);
  };

  if (readonly) return feld;

  const pfeil = (zeichen, richtung, beschriftung) => el('button.zahlpfeil', {
    text: zeichen, type: 'button', tabIndex: -1, title: beschriftung,
    on: { click: (e) => { e.preventDefault(); ruecken(richtung); } },
  });

  return el('div.zahlfeld', {}, [
    feld,
    el('div.zahlpfeile', {}, [
      pfeil('▴', 1, 'grösser'),
      pfeil('▾', -1, 'kleiner'),
    ]),
  ]);
}

export function auswahl({ werte, gewaehlt, beiAenderung, titel }) {
  return el('select', {
    title: titel,
    on: { change: (e) => beiAenderung(e.target.value) },
  }, werte.map(({ wert, beschriftung }) =>
    el('option', { value: wert, text: beschriftung, selected: wert === gewaehlt })));
}

/** Kurze Rückmeldung am unteren Bildschirmrand. */
export function melden(text, istFehler = false) {
  const melder = document.getElementById('melder');
  const zettel = el('div', { text, class: istFehler ? 'ist-fehler' : '' });
  melder.append(zettel);
  setTimeout(() => zettel.remove(), istFehler ? 6000 : 2800);
}

export function leerzustand(...zeilen) {
  return el('div.leer', {}, zeilen.map((z) => el('p', { text: z })));
}
