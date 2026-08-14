/**
 * zustand.js -- Der Zustand der Oberfläche an einer Stelle.
 *
 * Enthält die Projektbeschreibung, das letzte Rechenergebnis und die Auswahl.
 * Wer etwas ändert, ruft `aendern()`; wer darauf reagieren will, meldet sich
 * mit `horchen()` an. Mehr Mechanik braucht es hier nicht.
 *
 * Die Projektbeschreibung ist die einzige Wahrheit über die Eingaben; alles
 * Gerechnete kommt ausschliesslich aus `loesung` und wird nie in der Oberfläche
 * nachgerechnet.
 */

const zuhoerer = new Set();

export const zustand = {
  projekt: null,
  katalog: null,
  loesung: null,
  /** Kennungen der Ziele, die zuletzt angefordert wurden. */
  ziele: [],
  /** Was links ausgewählt ist: {art: 'material'|'querschnitt', kennung}. */
  auswahl: null,
  /** Welcher Reiter rechts offen ist. */
  reiter: 'herleitung',
  /** Wert-IDs, die hervorgehoben werden (Rückverfolgung eines Ziels). */
  hervorgehoben: new Set(),
  /** Für welches Ziel die Rückverfolgung gerade gilt. */
  verfolgtesZiel: null,
  rechnetGerade: false,
  ungespeichert: false,
  /** Aufgeklappte Kapitel im Baum. */
  offen: new Set(['materialien', 'beton', 'betonstahl', 'platten']),
  /** Angehakte Ziele im Reiter "Ziel wählen". */
  gewaehlteZiele: new Set(),
  zieleListe: null,
};

/** Klappt ein Kapitel auf oder zu. */
export function umschalten(kapitel) {
  if (zustand.offen.has(kapitel)) zustand.offen.delete(kapitel);
  else zustand.offen.add(kapitel);
  aendern({}, 'baum');
}

export function horchen(rueckruf) {
  zuhoerer.add(rueckruf);
  return () => zuhoerer.delete(rueckruf);
}

/**
 * Ändert den Zustand und benachrichtigt alle Zuhörer.
 * @param {Object} teil    zu übernehmende Felder
 * @param {string} anlass  kurze Kennzeichnung, damit Ansichten selektiv neu bauen können
 */
export function aendern(teil, anlass = 'allgemein') {
  Object.assign(zustand, teil);
  for (const rueckruf of zuhoerer) rueckruf(anlass);
}

/** Ändert die Projektbeschreibung und merkt sich, dass ungespeichert ist. */
export function projektAendern(veraenderer, anlass = 'projekt') {
  veraenderer(zustand.projekt);
  aendern({ ungespeichert: true }, anlass);
}

// -- Zugriffshilfen ---------------------------------------------------------

export function gewaehltesMaterial() {
  if (zustand.auswahl?.art !== 'material') return null;
  return zustand.projekt.materialien.find((m) => m.kennung === zustand.auswahl.kennung) || null;
}

export function gewaehlterQuerschnitt() {
  if (zustand.auswahl?.art !== 'querschnitt') return null;
  return zustand.projekt.querschnitte.find((q) => q.kennung === zustand.auswahl.kennung) || null;
}

export function materialien(art) {
  return zustand.projekt.materialien.filter((m) => m.art === art);
}

export function freieKennung(vorsilbe) {
  const vergeben = new Set([
    ...zustand.projekt.materialien.map((m) => m.kennung),
    ...zustand.projekt.querschnitte.map((q) => q.kennung),
  ]);
  let i = 1;
  while (vergeben.has(`${vorsilbe}${i}`)) i += 1;
  return `${vorsilbe}${i}`;
}

/** Der Namensraum eines Materials im Rechenwerk, z.B. `beton.b1`. */
export function namensraum(art, kennung) {
  return `${art}.${kennung}`;
}

/** Wert-ID eines Materialkennwerts. */
export function kennwertId(material, kurzname) {
  return `${namensraum(material.art, material.kennung)}.${kurzname}`;
}
