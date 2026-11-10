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
  /**
   * Die Fassung des Projekts: zählt jede Änderung (`projektAendern`) und
   * jedes neue Projekt (`projektSetzen`). Wer eine Antwort des Kerns
   * aufbewahrt, merkt sich die Fassung, zu der er gefragt hat; stimmt sie
   * nicht mehr, fragt er neu. Ob sich für ihn etwas geändert hat, weiss der
   * Kern (speicher.py) -- bis 2026-11-10 entschieden das hier drei Abdrücke
   * von Hand, jeder mit seiner eigenen Liste dessen, wovon er abhängt.
   */
  fassung: 0,
  katalog: null,
  loesung: null,
  /**
   * Der eine Nachweis, den das Auge in der Zusammenfassung zeigt:
   * `{ziel, name, loesung}` -- ein Teillauf neben der Gesamtlösung. Nur die
   * Herleitung liest ihn.
   */
  verfolgung: null,
  /**
   * Was links ausgewählt ist: {art, kennung} -- `art` ist die App des
   * Eintrags, wie apps.js sie nennt: 'material', 'skript' oder eine
   * Bauteilart (ARTEN, arten.js).
   */
  auswahl: null,
  /**
   * Welches Fenster über den Eingaben offen ist -- der Schlüssel eines
   * Kapitels (kapitel.js) oder null. Ansichtssache; es gehört zum gewählten
   * Bauteil und geht zu, sobald ein anderes gewählt wird (`waehlen`).
   */
  fenster: null,
  /** Welcher Reiter rechts offen ist. */
  reiter: 'nachweise',
  /** 'gesamt' oder 'seite' -- ob nur der gewählte Bestandteil gezeigt wird. */
  // Die aktuelle Seite ist die Vorgabe: wer links eine Platte wählt, will in
  // aller Regel deren Nachweise sehen und nicht die des ganzen Projekts.
  umfang: 'seite',
  /**
   * Welches Diagramm gross steht: `{schluessel, gruppe, index}` -- siehe
   * `diagrammSicht` in bericht.js. Null: das erste.
   */
  diagrammWahl: null,
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
  /**
   * Die Stände, die sich beim Start nicht öffnen liessen (`gerettete` in
   * ablage.js) -- die rechte Tafel bietet sie an, bis sie verworfen sind.
   */
  gerettet: [],
  /**
   * Welche App links gewählt ist: 'material', 'skript' oder die Art eines
   * Bauteils -- wie die Auswahl sie nennt. Wer einen Eintrag wählt, wählt
   * seine App mit (`waehlen`); null heisst: die der Auswahl, sonst die Platten.
   */
  app: null,
  /**
   * Je App die Kennung des Eintrags, der dort zuletzt gewählt war: wer
   * zurückwechselt, findet ihn wieder (Benutzer, 2026-10-16).
   */
  zuletzt: {},
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

/**
 * Wählt links eine App -- unter den Knöpfen steht dann ihre Liste -- und
 * darin den Eintrag, der dort zuletzt gewählt war, sonst den ersten.
 * `eintraege` ist die Liste der App; ist sie leer, ist nichts gewählt.
 */
export function appWaehlen(app, eintraege) {
  const kennungen = eintraege.map((e) => e.kennung);
  const kennung = kennungen.includes(zustand.zuletzt[app]) ? zustand.zuletzt[app] : kennungen[0];
  aendern({ app, fenster: null, auswahl: kennung ? { art: app, kennung } : null }, 'auswahl');
}

/** Die App, deren Liste links steht. */
export function gewaehlteApp() {
  return zustand.app || zustand.auswahl?.art || 'querschnitt';
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

/**
 * Wählt einen Bestandteil -- `{art, kennung}` oder null. Ein offenes Fenster
 * gehört zum bisher gewählten und geht dabei zu.
 */
export function waehlen(auswahl) {
  if (auswahl) zustand.zuletzt[auswahl.art] = auswahl.kennung;
  aendern({ auswahl, fenster: null, ...(auswahl ? { app: auswahl.art } : {}) }, 'auswahl');
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
  aendern({ ungespeichert: true, fassung: zustand.fassung + 1 }, anlass);
}

/**
 * Ein neues Projekt -- beim Start und beim Öffnen einer Datei. `weiteres`
 * setzt, was dazugehört: den Katalog, ob es gespeichert ist, die Auswahl.
 * Keine Ansicht weiss danach noch etwas vom vorigen (`ansichtVon`).
 */
export function projektSetzen(projekt, weiteres = {}) {
  ansichten.clear();
  aendern({ projekt, fassung: zustand.fassung + 1, ...weiteres }, 'start');
}

/** Je Kennung, was sich die Ansichten merken -- siehe `ansichtVon`. */
const ansichten = new Map();

/**
 * Was sich die Ansichten zu einem Eintrag merken: den gezeigten Fall, den
 * Schnitt eines Diagramms, die letzte Antwort des Kerns. Ansichtssache, nicht
 * Teil des Projekts. Wer einen Eintrag anlegt, kopiert oder löscht, vergisst
 * es (`ansichtVergessen`) -- ein neuer Eintrag mit einer Kennung, die es
 * schon gab, zeigt nichts vom alten.
 */
export function ansichtVon(kennung) {
  if (!ansichten.has(kennung)) ansichten.set(kennung, {});
  return ansichten.get(kennung);
}

export function ansichtVergessen(kennung) {
  ansichten.delete(kennung);
}

/**
 * Der Eintrag mit dieser Kennung, in welcher Liste des Projekts er auch
 * steht -- oder null. Kennungen sind im Projekt eindeutig (`freieKennung`),
 * darum braucht es den Namen der Liste nicht.
 */
export function eintragVon(kennung) {
  for (const liste of Object.values(zustand.projekt || {})) {
    const eintrag = Array.isArray(liste) && liste.find((e) => e?.kennung === kennung);
    if (eintrag) return eintrag;
  }
  return null;
}

/**
 * Ändert den Eintrag mit dieser Kennung -- der eine Weg, auf dem eine App
 * ihren Eintrag ändert. Gibt es ihn nicht mehr, etwa wenn ein verzögertes
 * Speichern erst nach dem Löschen kommt, geschieht nichts: weder abgelegt
 * noch gerechnet.
 */
export function eintragAendern(kennung, veraenderer, anlass = 'projekt') {
  const eintrag = eintragVon(kennung);
  if (eintrag) projektAendern(() => veraenderer(eintrag), anlass);
}

// -- Zugriffshilfen ---------------------------------------------------------

export function materialien(art) {
  return zustand.projekt.materialien.filter((m) => m.art === art);
}

/**
 * Die kleinste freie Kennung mit dieser Vorsilbe: «q3». Frei heisst, kein
 * Eintrag einer Liste des Projekts trägt sie -- gleich welcher App; eine
 * neue App braucht dafür hier nichts.
 */
export function freieKennung(vorsilbe) {
  const vergeben = new Set(Object.values(zustand.projekt)
    .filter(Array.isArray)
    .flatMap((liste) => liste.map((e) => e?.kennung)));
  let i = 1;
  while (vergeben.has(`${vorsilbe}${i}`)) i += 1;
  return `${vorsilbe}${i}`;
}

/**
 * Was der Kern im Katalog unter diesem Pfad sagt: `katalog('balkensystem',
 * 'lastarten')`. Der Katalog kommt beim Start mit dem Projekt (app.js), wer
 * ein Projekt vor sich hat, hat auch ihn. Fehlt ein Schlüssel, passen Kern
 * und Oberfläche nicht zusammen: das meldet sich mit dem Pfad, statt still
 * einen leeren Schalter zu zeigen. Welche Pfade es gibt, prüft
 * test_katalog_js.py.
 */
export function katalog(...pfad) {
  let wert = zustand.katalog;
  if (!wert) throw new Error('Der Katalog ist noch nicht geladen.');
  for (const [i, schluessel] of pfad.entries()) {
    wert = wert[schluessel];
    if (wert === undefined) throw new Error(`Im Katalog fehlt ${pfad.slice(0, i + 1).join('.')}.`);
  }
  return wert;
}

/**
 * Was der Kern über ein Feld weiss (`katalog.felder`): Einheit, Grenzen, ob
 * ganz. Ein Feld ohne Angabe -- ein Text, eine Kennung -- gibt `{}`. Für
 * `zahlfeld({angabe})`.
 */
export function feldangabe(art, feld) {
  return katalog('felder', art)[feld] || {};
}

/**
 * Eine neue Zeile nach der Vorlage des Kerns (`katalog.neue_zeilen`) -- mit
 * dem, was nur die Oberfläche weiss: Name, Kennung. Eine Kopie, nicht die
 * Vorlage selbst: sonst teilten sich zwei Materialien dieselben Abweichungen.
 */
export function ausVorlage(art, felder) {
  return { ...structuredClone(katalog('neue_zeilen', art)), ...felder };
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
