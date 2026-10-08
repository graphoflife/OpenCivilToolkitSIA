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

/** Unter diesem Schlüssel merkt sich der Browser die zugeklappten Panels. */
const ZUGEKLAPPT = 'opencivil.zugeklappt';

/** Die zugeklappten Panels vom letzten Mal -- leer, wenn der Browser nichts hergibt. */
function zugeklappteLesen() {
  try {
    return new Set(JSON.parse(localStorage.getItem(ZUGEKLAPPT)) || []);
  } catch {
    return new Set();
  }
}

export const zustand = {
  projekt: null,
  katalog: null,
  loesung: null,
  /**
   * Der eine Nachweis, den das Auge in der Zusammenfassung zeigt:
   * `{ziel, name, loesung}` -- ein Teillauf neben der Gesamtlösung. Nur die
   * Herleitung liest ihn.
   */
  verfolgung: null,
  /**
   * Die ganze Formelsammlung, `[{thema, bloecke}]` -- an kein Projekt
   * gebunden, einmal geladen (siehe `formelsammlung` in bericht.js).
   */
  formelsammlung: null,
  /**
   * Was links ausgewählt ist:
   * {art: 'material'|'querschnitt'|'querschnittsanalyse'|'blatt', kennung}.
   */
  auswahl: null,
  /** Welcher Reiter rechts offen ist. */
  reiter: 'nachweise',
  /** 'gesamt' oder 'seite' -- ob nur der gewählte Bestandteil gezeigt wird. */
  // Die aktuelle Seite ist die Vorgabe: wer links eine Platte wählt, will in
  // aller Regel deren Nachweise sehen und nicht die des ganzen Projekts.
  umfang: 'seite',
  diagrammspalten: 1,
  /** Ob im Betondiagramm der vereinfachte Spannungsblock mitgezeichnet wird. */
  zeigeVereinfacht: true,
  rechnetGerade: false,
  /**
   * Warum die letzte Eingabe sich nicht rechnen liess -- oder null. Die
   * Lösung bleibt dann die von davor, und die rechte Tafel sagt es dazu:
   * ein Bauteil mit unfertiger Zeichnung soll nicht die Zahlen von vorher
   * als gültig stehen lassen.
   */
  rechenfehler: null,
  ungespeichert: false,
  /** Aufgeklappte Kapitel im Baum. */
  offen: new Set(['materialien', 'beton', 'betonstahl', 'platten', 'analysen', 'gleichungen']),
  /**
   * Zugeklappte Panels der Eingaben, je App und Titel: «platte/Bewehrung».
   *
   * Ansichtssache wie `offen`, aber im Browser gemerkt: wer die Bewehrung
   * zuklappt, will sie nach dem Neuladen nicht wieder offen finden. Es gilt
   * für jede Platte gleich -- es sagt, was man sehen will, nicht welche
   * Platte.
   */
  zugeklappt: zugeklappteLesen(),
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

/**
 * Klappt ein Panel der Eingaben auf oder zu und merkt es sich im Browser.
 * Gibt zurück, ob es jetzt zu ist.
 *
 * Ohne `aendern()`: es ändert sich nur, ob ein Panel offen ist, und das setzt
 * der Aufrufer gleich am Knoten. Neu zu zeichnen hiesse, den ganzen Editor
 * und den Bericht wegen eines Pfeils neu zu bauen.
 */
export function panelUmschalten(schluessel) {
  const zu = !zustand.zugeklappt.has(schluessel);
  if (zu) zustand.zugeklappt.add(schluessel);
  else zustand.zugeklappt.delete(schluessel);
  try {
    localStorage.setItem(ZUGEKLAPPT, JSON.stringify([...zustand.zugeklappt]));
  } catch {
    // Privater Modus oder voller Speicher: dann gilt es bis zum Neuladen.
  }
  return zu;
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

export function gewaehlteAnalyse() {
  if (zustand.auswahl?.art !== 'querschnittsanalyse') return null;
  return zustand.projekt.querschnittsanalysen?.find(
    (a) => a.kennung === zustand.auswahl.kennung) || null;
}

export function gewaehltesBlatt() {
  if (zustand.auswahl?.art !== 'blatt') return null;
  return zustand.projekt.gleichungen?.find((b) => b.kennung === zustand.auswahl.kennung) || null;
}

export function materialien(art) {
  return zustand.projekt.materialien.filter((m) => m.art === art);
}

export function freieKennung(vorsilbe) {
  const vergeben = new Set([
    ...zustand.projekt.materialien.map((m) => m.kennung),
    ...zustand.projekt.querschnitte.map((q) => q.kennung),
    ...(zustand.projekt.querschnittsanalysen || []).map((a) => a.kennung),
    ...(zustand.projekt.gleichungen || []).map((b) => b.kennung),
  ]);
  let i = 1;
  while (vergeben.has(`${vorsilbe}${i}`)) i += 1;
  return `${vorsilbe}${i}`;
}

/**
 * Eine neue Zeile nach der Vorlage des Kerns (`katalog.neue_zeilen`) -- mit
 * dem, was nur die Oberfläche weiss: Name, Kennung. Eine Kopie, nicht die
 * Vorlage selbst: sonst teilten sich zwei Materialien dieselben Abweichungen.
 */
export function ausVorlage(art, felder) {
  return { ...structuredClone(zustand.katalog.neue_zeilen[art]), ...felder };
}

/**
 * «Tragsicherheit 3» -- die kleinste Nummer, die in der Liste noch frei ist.
 *
 * Nicht `länge + 1`: nach dem Löschen eines Eintrags ergäbe das einen Namen,
 * den es schon gibt, und der Kern weist doppelte Namen ab.
 */
export function naechsterName(stamm, eintraege) {
  const vergeben = new Set(eintraege.map((e) => e.name));
  let i = 1;
  while (vergeben.has(`${stamm} ${i}`)) i += 1;
  return `${stamm} ${i}`;
}

/** Der Namensraum eines Bestandteils im Rechenwerk: `beton.b1`, `querschnitt.q1`. */
export function namensraum(art, kennung) {
  return `${art}.${kennung}`;
}

/** Wert-ID eines Materialkennwerts. */
export function kennwertId(material, kurzname) {
  return `${namensraum(material.art, material.kennung)}.${kurzname}`;
}
