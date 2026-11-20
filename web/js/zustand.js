/**
 * zustand.js -- Der Zustand der Oberfläche an einer Stelle.
 *
 * Enthält die Projekte, das letzte Rechenergebnis und die Auswahl. Wer etwas
 * ändert, ruft `aendern()`, `mitteAendern()` oder, für die Eingaben,
 * `projektAendern()` und `mappeAendern()`; wer darauf reagieren will, meldet
 * sich mit `horchen()` an. Mehr Mechanik braucht es hier nicht.
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
  /**
   * Die Projekte, die zusammen gespeichert und geöffnet werden:
   * `{projekte: [...]}`, wie `Mappe.als_dict()` im Kern -- jedes heisst
   * anders (opencivil/projekt/mappe.py).
   */
  mappe: null,
  /** Das gezeigte Projekt: eines aus `mappe.projekte`, keine Kopie. */
  projekt: null,
  /**
   * Die Fassung des Projekts: zählt jede Änderung (`projektAendern`) und
   * jedes andere Projekt (`projektSetzen`). Wer eine Antwort des Kerns
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
   * eine Eingabe, die der Kern abweist, soll nicht die Zahlen von vorher
   * als gültig stehen lassen. Einem Bauteil, dem nur noch etwas fehlt,
   * geschieht das nicht mehr: es steht in `loesung.unfertige`.
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
};

/**
 * Wählt links eine App -- unter den Knöpfen steht dann ihre Liste -- und
 * darin den Eintrag, der dort zuletzt gewählt war, sonst den ersten des
 * Projekts; die Sandbox nur, wenn es keinen gibt. `eintraege` ist die Liste
 * der App; ist sie leer, ist nichts gewählt.
 */
export function appWaehlen(app, eintraege) {
  const kennungen = eintraege.map((e) => e.kennung);
  const kennung = kennungen.includes(zustand.zuletzt[app]) ? zustand.zuletzt[app]
    : kennungen.find((k) => !istSandbox(k)) ?? kennungen[0];
  aendern({ app, fenster: null, auswahl: kennung ? { art: app, kennung } : null });
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
  aendern({ auswahl, fenster: null, ...(auswahl ? { app: auswahl.art } : {}) });
}

/** Meldet `rueckruf` an: er erfährt 'alles', 'mitte', 'projekt' oder 'neu' -- siehe `aendern`. */
export function horchen(rueckruf) {
  zuhoerer.add(rueckruf);
  return () => zuhoerer.delete(rueckruf);
}

/**
 * Was nach jeder Änderung mit der Mappe geschehen soll: `ablegen(mappe,
 * gewaehlt, gesichert)` -- die Projekte, die Stelle des gezeigten und ob
 * dieser Stand als Datei auf der Platte liegt.
 *
 * Eingehängt wird von `app.js` das Ablegen im Browser. Hier steht nur der
 * Haken, damit dieser Baustein nichts von der Ablage wissen muss -- und damit
 * es genau eine Stelle gibt, an der eine Änderung vorbeikommt.
 */
let ablegen = () => {};

export function ablageEinrichten(rueckruf) {
  ablegen = rueckruf;
}

function ablegenJetzt() {
  ablegen(zustand.mappe, zustand.mappe.projekte.indexOf(zustand.projekt), !zustand.ungespeichert);
}

/**
 * Ändert den Zustand und zeichnet alles neu; gerechnet wird nicht. Ohne
 * `teil` zeichnet es bloss neu, etwa wenn eine Antwort des Kerns da ist.
 *
 * Wer horcht (`horchen`), erfährt, was neu ist: 'alles', 'mitte'
 * (`mitteAendern`), 'projekt' (`projektAendern`) oder 'neu', ein anderes
 * Projekt (`projektSetzen`). Bis 2026-11-20 gab jeder Aufruf einen «Anlass»
 * mit, einen freien Text; von rund sechzehn wirkten drei -- zwei zeichneten
 * nur die Mitte, einer rechnete.
 */
export function aendern(teil = {}) {
  Object.assign(zustand, teil);
  weitersagen('alles');
}

/**
 * Ändert, was nur die mittlere Tafel zeigt -- ein Fenster auf oder zu, eine
 * Wahl im Zeichenfenster -- und zeichnet nur sie neu. Baum und Bericht sähen
 * danach aus wie vorher, und die Herleitung neu zu setzen kostet mit jeder
 * Formel mehr.
 */
export function mitteAendern(teil = {}) {
  Object.assign(zustand, teil);
  weitersagen('mitte');
}

function weitersagen(was) {
  for (const rueckruf of zuhoerer) rueckruf(was);
}

/**
 * Ändert die Projektbeschreibung. Danach wird gerechnet, wenn sich geändert
 * hat, was in die Rechnung eingeht (app.js, `rechenstand`).
 *
 * Der einzige Weg, auf dem sich Eingaben ändern -- deshalb steht hier auch das
 * Ablegen im Browser. `ungespeichert` heisst: seit der letzten Datei auf der
 * Platte hat sich etwas getan. Im Browser liegt es da längst.
 */
export function projektAendern(veraenderer) {
  veraenderer(zustand.projekt);
  Object.assign(zustand, { ungespeichert: true, fassung: zustand.fassung + 1 });
  ablegenJetzt();
  weitersagen('projekt');
}

/**
 * Ändert die Mappe -- ein Projekt dazu, eines weg -- und zeigt danach
 * `gezeigt`, eines ihrer Projekte.
 */
export function mappeAendern(veraenderer, gezeigt) {
  veraenderer(zustand.mappe);
  zustand.ungespeichert = true;
  projektSetzen(gezeigt);
}

/** Je Projekt, wie man es verliess: die App, die Auswahl, je App der zuletzt gewählte Eintrag. */
const verlassen = new WeakMap();

/**
 * Zeigt ein Projekt der Mappe: beim Start, beim Öffnen einer Datei, beim
 * Wechsel oben links. `weiteres` setzt, was dazugehört: die Mappe, den
 * Katalog, ob sie gespeichert ist.
 *
 * Was zum vorigen gehörte, gilt nicht mehr: keine Ansicht weiss noch etwas
 * von ihm (`ansichtVon`), seine Lösung und sein Fenster sind weg -- ohne
 * Lösung steht rechts, dass gerechnet wird, nicht die Zahlen des anderen.
 * Wer zu einem Projekt zurückkehrt, findet es, wie er es verliess: dieselbe
 * App, derselbe Eintrag. Gerechnet wird sofort ('neu', `horchen`).
 */
export function projektSetzen(projekt, weiteres = {}) {
  if (zustand.projekt) {
    verlassen.set(zustand.projekt,
      { app: zustand.app, auswahl: zustand.auswahl, zuletzt: zustand.zuletzt });
  }
  ansichten.clear();
  Object.assign(zustand, {
    projekt,
    fassung: zustand.fassung + 1,
    loesung: null,
    verfolgung: null,
    rechenfehler: null,
    fenster: null,
    auswahl: null,
    zuletzt: {},
    ...verlassen.get(projekt),
    ...weiteres,
  });
  ablegenJetzt();
  weitersagen('neu');
}

/** Je Kennung, was sich die Ansichten merken -- siehe `ansichtVon`. */
const ansichten = new Map();

/**
 * Was sich die Ansichten zu einem Eintrag merken: den gezeigten Fall, den
 * Schnitt eines Diagramms, die letzte Antwort des Kerns. Ansichtssache, nicht
 * Teil des Projekts. Wer einen Eintrag löscht, vergisst es
 * (`ansichtVergessen`); ein neuer hat eine Kennung, die es nie gab
 * (`freieKennung`), und damit nichts vom alten.
 */
export function ansichtVon(kennung) {
  if (!ansichten.has(kennung)) ansichten.set(kennung, {});
  return ansichten.get(kennung);
}

/**
 * Wer zu einer Kennung ausserhalb von `ansichtVon` etwas aufbewahrt -- die
 * Zeichenfenster (cad_app.js) --, meldet hier, wie er es vergisst.
 */
const vergesser = [];

export function beimVergessen(rueckruf) {
  vergesser.push(rueckruf);
}

export function ansichtVergessen(kennung) {
  ansichten.delete(kennung);
  for (const rueckruf of vergesser) rueckruf(kennung);
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
export function eintragAendern(kennung, veraenderer) {
  const eintrag = eintragVon(kennung);
  if (eintrag) projektAendern(() => veraenderer(eintrag));
}

/**
 * Ist dieser Eintrag die Sandbox seiner App? Welche es ist, hält das Projekt
 * je Liste (`sandboxen`, opencivil/projekt/projekt.py): eine Kopie ist so von
 * selbst ein gewöhnlicher Eintrag.
 */
export function istSandbox(kennung) {
  return Object.values(zustand.projekt?.sandboxen ?? {}).includes(kennung);
}

/**
 * Gehört ein Name im Rechenwerk -- `querschnitt.q1.biegung` -- zu einer
 * Sandbox? Was das ganze Projekt zusammenfasst, lässt sie aus, wie der
 * Bericht: «Gesamt» und der Stand oben rechts.
 */
export function inSandbox(id) {
  return istSandbox(String(id).split('.')[1]);
}

// -- Zugriffshilfen ---------------------------------------------------------

export function materialien(art) {
  return zustand.projekt.materialien.filter((m) => m.art === art);
}

/** Die Zahl hinter der Vorsilbe -- «LF12» gibt 12 -- oder null. */
export function nummer(kennung, vorsilbe) {
  if (typeof kennung !== 'string' || !kennung.startsWith(vorsilbe)) return null;
  const rest = kennung.slice(vorsilbe.length);
  return /^\d+$/.test(rest) ? Number(rest) : null;
}

/**
 * Eine neue Kennung «LF4» -- über jeder, die `besitzer` je vergeben hat:
 * eine Kennung kommt nie wieder (Benutzer, 2026-11-19). An ihr hängen
 * Lasten, Beiwerte, Diagrammzeilen; bis dahin bekam eine neue die Nummer
 * der zuletzt gelöschten und still, was auf jene zeigte. Der Besitzer --
 * das Projekt oder ein Bauteil -- merkt sich je Vorsilbe die höchste
 * (`vergeben`), wie im Kern (`neue_kennung` in opencivil/projekt/netz.py).
 * `eintraege` sind die vorhandenen: eine Datei ohne Zählung hat nur sie.
 */
export function neueKennung(besitzer, vorsilbe, eintraege) {
  const n = Math.max(besitzer.vergeben?.[vorsilbe] ?? 0,
    ...eintraege.map((e) => nummer(e?.kennung, vorsilbe) ?? 0)) + 1;
  besitzer.vergeben = { ...besitzer.vergeben, [vorsilbe]: n };
  return `${vorsilbe}${n}`;
}

/**
 * Die Kennung eines neuen Eintrags des Projekts: «q3», nie vergeben in
 * einer Liste des Projekts -- gleich welcher App; eine neue App braucht
 * dafür hier nichts.
 */
export function freieKennung(vorsilbe) {
  const p = zustand.projekt;
  return neueKennung(p, vorsilbe, Object.values(p).filter(Array.isArray).flat());
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
 * Eine neue Zeile nach der Vorlage des Kerns (`katalog.vorlagen`, je Klasse
 * von Einträgen unter demselben Namen wie ihre Feldangaben) -- mit
 * dem, was nur die Oberfläche weiss: Name, Kennung. Eine Kopie, nicht die
 * Vorlage selbst: sonst teilten sich zwei Materialien dieselben Abweichungen.
 */
export function ausVorlage(art, felder) {
  return { ...structuredClone(katalog('vorlagen', art)), ...felder };
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
