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

export function leeren(knoten) {
  while (knoten.firstChild) knoten.removeChild(knoten.firstChild);
  return knoten;
}

export function ersetzen(knoten, ...kinder) {
  leeren(knoten).append(...kinder.filter(Boolean));
  return knoten;
}

/** Zahlenfeld mit einheitlichem Verhalten. */
export function zahlfeld({ wert, schritt = 1, min, max, beiAenderung, titel, readonly }) {
  return el('input', {
    type: 'number',
    value: wert ?? '',
    step: schritt,
    min, max, title: titel, readOnly: !!readonly,
    on: {
      change: (e) => {
        const roh = e.target.value.trim();
        beiAenderung(roh === '' ? null : Number(roh));
      },
    },
  });
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
