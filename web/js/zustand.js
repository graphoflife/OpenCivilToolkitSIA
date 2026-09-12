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
  reiter: 'nachweise',
  /** 'gesamt' oder 'seite' -- ob nur der gewählte Bestandteil gezeigt wird. */
  umfang: 'gesamt',
  /** Ob im Betondiagramm der vereinfachte Spannungsblock mitgezeichnet wird. */
  zeigeVereinfacht: true,
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
  /**
   * Je M-V-Kurve die eingestellte Normalkraft in kN.
   *
   * Ansichtssache, kein Teil des Projekts: sie sagt nichts über das
   * Bauwerk, sondern nur, welchen Schnitt durch die Fläche man gerade
   * sehen will. Darum hier und nicht in der Projektbeschreibung.
   */
  kurvenNormalkraft: {},
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
 * Was nach jeder Eingabeänderung mit der Beschreibung geschehen soll.
 *
 * Eingehängt wird von `app.js` das Ablegen im Browser. Hier steht nur der
 * Haken, damit dieser Baustein nichts von der Ablage wissen muss -- und damit
 * es genau eine Stelle gibt, an der eine Änderung vorbeikommt.
 */
let ablegen = () => {};

export function ablageEinrichten(rueckruf) {
  ablegen = rueckruf;
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

/**
 * Ändert die Projektbeschreibung.
 *
 * Der einzige Weg, auf dem sich Eingaben ändern -- deshalb steht hier auch das
 * Ablegen im Browser. `ungespeichert` heisst: seit der letzten Datei auf der
 * Platte hat sich etwas getan. Im Browser liegt es da längst.
 */
export function projektAendern(veraenderer, anlass = 'projekt') {
  veraenderer(zustand.projekt);
  ablegen(zustand.projekt);
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
