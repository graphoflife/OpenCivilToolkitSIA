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
    else if (schluessel === 'style') stileSetzen(knoten, wert);
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
 * Die Stile eines Knotens -- eigene Eigenschaften (`--felder`) über
 * `setProperty`: `Object.assign` setzt sie nicht, und bis 2026-10-18 kam so
 * das `--felder` der Gebrauchsfälle nie an.
 */
function stileSetzen(knoten, stile) {
  for (const [eigenschaft, wert] of Object.entries(stile)) {
    if (eigenschaft.startsWith('--')) knoten.style.setProperty(eigenschaft, wert);
    else knoten.style[eigenschaft] = wert;
  }
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
 * den fertigen Wert aus dem Stil (`web/css/`), damit jede Farbe nur dort festgelegt ist.
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
 * Warum der Kern eine Zahl abwiese -- leer, wenn er sie nimmt. `angabe` sind
 * die Grenzen ihres Feldes aus dem Katalog (`feldangabe`): «Teilung muss
 * grösser als null sein». Begrenzt sie ein anderes Feld desselben Eintrags
 * (`bis_feld`, `ab_feld`: α_min nicht über α_max; `quer_zu`: zwei
 * Richtungen mindestens 5° auseinander, als Linien), steht dessen Zahl in
 * `neben`, dem Eintrag.
 */
export function grenzeVerletzt(angabe, zahl, neben = {}) {
  if (angabe.ganz && !Number.isInteger(zahl)) return 'Nur ganze Zahlen';
  const {
    ueber, ab, bis, unter, bis_feld: hoch, ab_feld: tief, quer_zu: quer,
  } = angabe;
  const draussen = (ueber !== undefined && !(zahl > ueber)) || (ab !== undefined && !(zahl >= ab))
    || (bis !== undefined && !(zahl <= bis)) || (unter !== undefined && !(zahl < unter));
  if (draussen) return `${angabe.heisst} ${angabe.verlangt}`;
  // Ein leeres Nachbarfeld begrenzt nichts -- wie im Kern (Bereich.grund_gegen):
  // «zahl > null» hiesse in JavaScript «zahl > 0».
  const da = (feld) => neben[feld] !== undefined && neben[feld] !== null;
  if (hoch && da(hoch.feld) && zahl > neben[hoch.feld]) return hoch.satz;
  if (tief && da(tief.feld) && zahl < neben[tief.feld]) return tief.satz;
  if (quer && da(quer.feld) && linienabstand(zahl, neben[quer.feld]) < quer.mindestens) return quer.satz;
  return '';
}

/** Wie weit zwei Winkel in Grad als Linien auseinander liegen, 0° bis 90° -- 180° weiter ist dieselbe. */
function linienabstand(a, b) {
  const d = Math.abs(a - b) % 180;
  return Math.min(d, 180 - d);
}

/** Die engste der Grenzen, die es gibt -- `wahl` ist Math.max für unten, Math.min für oben. */
function engste(wahl, ...grenzen) {
  const da = grenzen.filter((g) => g !== undefined && g !== null);
  return da.length ? wahl(...da) : undefined;
}

/**
 * Zahlenfeld mit einheitlichem Verhalten.
 *
 * Die Pfeile sind eigene Knöpfe statt des Browser-Drehfelds, weil das nur
 * gleichmässige Schritte kann. Durchmesser springen aber von 22 auf 26 und
 * von 30 auf 34 -- eine Liste, kein Raster.
 *
 * Ein geleertes Feld behält seinen bisherigen Wert. Eigene Vorgaben kennt die
 * Oberfläche nicht -- die stehen im Kern, und vorher stand hier dieselbe Zahl
 * ein zweites Mal (`q.h = v ?? 300`). Nur wo leer etwas heisst, sagt das Feld
 * es mit `leer`: `0` für «keins» (kein Stab, keine Last), `null` für «zurück
 * zum Normwert».
 *
 * Was der Kern über das Feld weiss (`angabe`, aus `katalog.felder`), gilt
 * hier: die Pfeile gehen bis zu seinen Grenzen -- eine ausgeschlossene rückt
 * um einen Schritt nach innen, «grösser als null» heisst beim Schritt 0.1 ab
 * 0.1 --, und eine Zahl ausserhalb nimmt das Feld nicht an, ebenso eine
 * Kommazahl in einem Feld für ganze. Es sagt es mit den Worten des Kerns und
 * behält seinen Wert: bis 2026-10-18 rundete die Oberfläche eine Neigung von
 * 37.5° still auf 38°, bis 2026-11-19 hielt eine Stelle von 150 % erst beim
 * Rechnen ihr Bauteil an. Ebenso gegen ein anderes Feld, das es begrenzt --
 * α_min nicht über α_max --, wenn `neben` den Eintrag mit dessen Zahl gibt.
 *
 * @param {number[]} [stufen]  erlaubte Werte; sonst wird `schritt` verwendet
 * @param {number|null} [leer] was ein geleertes Feld meldet; fehlt es, bleibt
 *                             der bisherige Wert
 * @param {string} [platzhalter] blass im leeren Feld -- was dann gilt
 * @param {Object} [angabe]    was der Kern über das Feld weiss: Grenzen, ganz
 * @param {Object} [neben]     der Eintrag des Feldes, für die Grenze gegen ein
 *                             anderes Feld (`grenzeVerletzt`)
 */
export function zahlfeld({
  wert, schritt = 1, stufen, min, max, beiAenderung, titel, readonly, leer, platzhalter,
  angabe = {}, neben = {},
}) {
  const unten = engste(Math.max,
    min ?? angabe.ab ?? (angabe.ueber === undefined ? undefined : angabe.ueber + schritt),
    angabe.ab_feld && neben[angabe.ab_feld.feld]);
  const oben = engste(Math.min,
    max ?? angabe.bis ?? (angabe.unter === undefined ? undefined : angabe.unter - schritt),
    angabe.bis_feld && neben[angabe.bis_feld.feld]);
  const uebernehmen = (neu, getippt = String(neu)) => {
    const grund = neu === null ? '' : grenzeVerletzt(angabe, neu, neben);
    if (!grund) {
      beiAenderung(neu);
      return;
    }
    melden(`${grund}: ${getippt} ist nicht übernommen.`, true);
    feld.value = wert ?? '';
  };

  const feld = el('input', {
    type: 'number',
    value: wert ?? '',
    step: 'any',
    min: unten, max: oben, title: titel, readOnly: !!readonly, placeholder: platzhalter,
    on: {
      change: (e) => {
        const roh = e.target.value.trim();
        if (roh !== '') uebernehmen(Number(roh), roh);
        else if (leer !== undefined) uebernehmen(leer, 'ein leeres Feld');
        else e.target.value = wert ?? '';
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
    if (unten !== undefined && unten !== null) neu = Math.max(neu, unten);
    if (oben !== undefined && oben !== null) neu = Math.min(neu, oben);
    feld.value = String(neu);
    uebernehmen(neu);
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

/**
 * Ein Klick in ein Text- oder Zahlenfeld markiert seinen ganzen Inhalt: wer
 * dann tippt, ersetzt ihn (Benutzer, 2026-10-18). Erst ein zweiter Klick
 * setzt den Cursor an eine Stelle. Mehrzeilige Felder -- eine Beschreibung,
 * ein Skript -- bleiben aussen vor: dort ersetzte ein Tastendruck den ganzen
 * Text.
 *
 * Markiert wird beim Fokus, für die ganze Seite an einer Stelle. Fokussiert
 * ein Klick das Feld, hebt der Browser die Markierung beim Loslassen wieder
 * auf und setzt den Cursor -- dieses eine Loslassen wird darum abgefangen.
 * Über die Tastatur (Tab) kommt man ohnehin markiert hinein.
 */
export function inhaltMarkieren() {
  let geklickt = null;
  document.addEventListener('mousedown', (e) => {
    geklickt = einzeilig(e.target) && e.target !== document.activeElement ? e.target : null;
  }, true);
  document.addEventListener('focusin', (e) => {
    if (einzeilig(e.target)) e.target.select();
  });
  document.addEventListener('mouseup', (e) => {
    if (geklickt && e.target === geklickt) e.preventDefault();
    geklickt = null;
  }, true);
}

/** Ein Feld, in das man eine Zeile tippt: Text, Zahl oder Suche. */
function einzeilig(knoten) {
  return knoten instanceof HTMLInputElement && ['text', 'number', 'search'].includes(knoten.type);
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

/** «A und I», «A, I_y, I_z und I_T» -- Namen in einem Satz. */
export function undListe(namen) {
  return namen.length > 1 ? `${namen.slice(0, -1).join(', ')} und ${namen.at(-1)}` : namen.join('');
}
