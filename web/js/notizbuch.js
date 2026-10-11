/**
 * notizbuch.js -- die Dokumentation oben neben «Rechnen»: das Notizbuch.
 *
 * VERANTWORTUNG:
 * Zeigt den Ordner notizbuch/ als eigene Ansicht über den Tafeln: links Suche
 * und Inhalt, rechts die Seite. Dieselben Dateien liest Obsidian als Tresor;
 * hier zerlegt sie markdown.js, und notizbuch_seite.js baut die Seite.
 *
 * WELCHE SEITEN ES GIBT:
 * GitHub Pages zeigt keinen Ordnerinhalt. Das Verzeichnis web/kern/
 * notizbuch.json schreibt die Brücke -- mit Name, Pfad und Art jeder Seite,
 * in der Folge des Baums. Die Seiten selbst kommen ohne Marke und ohne
 * Zwischenspeicher: eine in Obsidian geänderte Notiz steht nach dem
 * Hochladen gleich da.
 *
 * ADRESSE:
 * `#notizbuch/<Name>` öffnet eine Seite, `#notizbuch/<Name>#<Überschrift>`
 * ihren Abschnitt, `#notizbuch` den Anfang. Jeder Link ist ein gewöhnlicher
 * Link auf eine solche Adresse; so gehen Zurück-Knopf und Lesezeichen von
 * selbst. Einzige Quelle dessen, was zu sehen ist, ist die Adresse.
 *
 * UNABHÄNGIG VOM RECHNEN:
 * Die Ansicht hat ihren eigenen Zustand und hängt nicht an zustand.js. Die
 * Tafeln zeichnen bei jeder Eingabe neu -- das Notizbuch soll dabei nicht
 * jedes Mal seine Formeln neu setzen.
 */

import { el, ersetzen } from './dom.js';
import { anker, zerlegen } from './markdown.js';
import { bloeckeZeichnen, seitentitel } from './notizbuch_seite.js';

/** Das Projektverzeichnis -- dort liegt notizbuch/, lokal wie auf GitHub Pages. */
const WURZEL = new URL('../../', import.meta.url);

const knoten = {};
let verzeichnis = null;
/** Die Namen aller Seiten, sobald das Verzeichnis da ist -- für `seiteVorhanden`. */
let bekannt = null;
const texte = new Map();
let offen = false;
let angezeigt = null;

/** Wie eine Seite heisst, die erzeugt ist -- als Zeile unter ihrem Titel. */
const HERKUNFT = {
  formel: 'Erzeugt aus dem Code · Theorie von Hand',
  thema: 'Erzeugt aus dem Code · Theorie von Hand',
  verzeichnis: 'Erzeugt aus dem Code',
  modul: 'Erzeugt aus den Docstrings',
};

/**
 * @param knoepfe  was das Notizbuch öffnet und schliesst: der Knopf in der
 *   Kopfleiste und, auf dem Telefon, die vierte Wahl unten
 * @param ansicht  der leere Platz dafür, `<section id="notizbuch">`
 */
export function notizbuchEinrichten({ knoepfe, ansicht }) {
  Object.assign(knoten, { knoepfe, ansicht, fenstertitel: document.title });
  knoten.suche = el('input.nb-suche', {
    type: 'search', placeholder: 'Suchen: Name, Zeichen, Thema …',
    'aria-label': 'Im Notizbuch suchen',
    on: { input: sucheZeigen, keydown: sucheTaste },
  });
  knoten.baum = el('nav.nb-baum', { 'aria-label': 'Inhalt des Notizbuchs' });
  knoten.leiste = el('div.nb-leiste', {}, [
    el('div.nb-leiste-kopf', {}, [
      knoten.suche,
      el('button.knopf.knopf-zart.nb-schliessen', {
        text: '×', title: 'Schliessen (Esc)', 'aria-label': 'Notizbuch schliessen',
        on: { click: schliessen },
      }),
    ]),
    knoten.baum,
  ]);
  knoten.seite = el('article.nb-seite');
  knoten.inhaltKnopf = el('button.knopf.nb-inhalt-knopf', {
    text: 'Inhalt', on: { click: () => knoten.ansicht.classList.toggle('nb-leiste-offen') },
  });
  ersetzen(ansicht, knoten.leiste, el('div.nb-lesespalte', {}, [knoten.inhaltKnopf, knoten.seite]));

  for (const knopf of knoepfe) {
    knopf.addEventListener('click', () => {
      if (offen) schliessen();
      else location.hash = 'notizbuch';
    });
  }
  // Wer auf dem Telefon unten eine Tafel wählt, will sie sehen.
  document.getElementById('tafelwahl')?.addEventListener('click', (e) => {
    if (offen && e.target.closest('[data-tafel]')) schliessen();
  });
  ansicht.addEventListener('keydown', taste);
  window.addEventListener('hashchange', folgen);
  // Gleich laden, nicht erst beim Öffnen: die Herleitung fragt danach, ob
  // es zu einer Formel eine Seite gibt. Es ist klein.
  verzeichnisLaden().catch(() => {});
  folgen();
}

/**
 * Ob es diese Seite gibt. Solange das Verzeichnis lädt: ja -- im Zweifel
 * steht der Link da, und die Seite sagt, wenn sie fehlt.
 */
export function seiteVorhanden(name) {
  return bekannt === null || bekannt.has(name.normalize('NFC').toLowerCase());
}

// ---------------------------------------------------------------------------
// Adresse
// ---------------------------------------------------------------------------

/** Was die Adresse verlangt: `{name, abschnitt}`, oder `null` -- dann ist das Notizbuch zu. */
function gewuenscht() {
  const hash = location.hash.slice(1);
  if (hash !== 'notizbuch' && !hash.startsWith('notizbuch/')) return null;
  const rest = hash.slice('notizbuch/'.length);
  const trenner = rest.indexOf('#');
  const teil = (s) => { try { return decodeURIComponent(s); } catch { return s; } };
  return {
    name: teil(trenner < 0 ? rest : rest.slice(0, trenner)),
    abschnitt: trenner < 0 ? null : teil(rest.slice(trenner + 1)),
  };
}

/** Die Adresse einer Seite, für Links und den Zurück-Knopf. */
export function adresse(name, abschnitt = null) {
  return `#notizbuch/${encodeURIComponent(name)}${abschnitt ? `#${encodeURIComponent(abschnitt)}` : ''}`;
}

async function folgen() {
  const ziel = gewuenscht();
  if (!ziel) {
    zeigen(false);
    return;
  }
  zeigen(true);
  try {
    const v = await verzeichnisLaden();
    const name = ziel.name || v.start;
    await seiteZeigen(name, ziel.abschnitt);
  } catch (fehler) {
    ersetzen(knoten.seite, el('p.nb-fehlt', { text: `Das Notizbuch ist nicht ladbar: ${fehler.message}` }));
  }
}

function zeigen(ja) {
  if (offen === ja) return;
  offen = ja;
  knoten.ansicht.hidden = !ja;
  for (const knopf of knoten.knoepfe) {
    knopf.setAttribute('aria-pressed', String(ja));
    knopf.classList.toggle('ist-aktiv', ja);
  }
  if (ja) {
    document.body.dataset.notizbuch = '';
    knoten.ansicht.focus({ preventScroll: true });
  } else {
    delete document.body.dataset.notizbuch;
    document.title = knoten.fenstertitel;
  }
}

function schliessen() {
  // Die Adresse ohne Notizbuch -- der Zurück-Knopf öffnet es wieder.
  history.pushState(null, '', location.pathname + location.search);
  folgen();
}

function taste(e) {
  // Tasten bleiben hier: hinter dem Notizbuch löschte sonst Entf im
  // Zeichenfenster, was dort gewählt ist.
  e.stopPropagation();
  if (e.key !== 'Escape') return;
  if (e.target === knoten.suche && knoten.suche.value) {
    knoten.suche.value = '';
    sucheZeigen();
    return;
  }
  schliessen();
}

// ---------------------------------------------------------------------------
// Verzeichnis und Seiten
// ---------------------------------------------------------------------------

function verzeichnisLaden() {
  verzeichnis ??= fetch(import.meta.resolve('../kern/notizbuch.json'))
    .then((r) => {
      if (!r.ok) throw new Error(`Verzeichnis: ${r.status}`);
      return r.json();
    })
    .then((v) => {
      v.nachName = new Map(v.seiten.map((s) => [s.name.normalize('NFC').toLowerCase(), s]));
      v.nachPfad = new Map(v.seiten.map((s) => [s.pfad, s]));
      bekannt = new Set(v.nachName.keys());
      baumZeichnen(v);
      return v;
    })
    .catch((fehler) => {
      verzeichnis = null;
      throw fehler;
    });
  return verzeichnis;
}

function pfadAdresse(pfad) {
  return new URL(`notizbuch/${pfad.split('/').map(encodeURIComponent).join('/')}`, WURZEL);
}

function textLaden(seite) {
  if (!texte.has(seite.pfad)) {
    texte.set(seite.pfad, fetch(pfadAdresse(seite.pfad), { cache: 'no-cache' })
      .then((r) => {
        if (!r.ok) throw new Error(`${seite.pfad}: ${r.status}`);
        return r.text();
      })
      .catch((fehler) => {
        texte.delete(seite.pfad);
        throw fehler;
      }));
  }
  return texte.get(seite.pfad);
}

async function seiteZeigen(name, abschnitt) {
  const v = await verzeichnisLaden();
  const seite = v.nachName.get(name.normalize('NFC').toLowerCase());
  baumMarkieren(seite);
  knoten.ansicht.classList.remove('nb-leiste-offen');
  if (!seite) {
    angezeigt = null;
    ersetzen(knoten.seite, el('h1', { text: name }),
      el('p.nb-fehlt', { text: 'Diese Seite gibt es im Notizbuch nicht.' }));
    return;
  }
  if (angezeigt !== seite.pfad) {
    const text = await textLaden(seite);
    const { kopf, bloecke } = zerlegen(text);
    const { titel, rumpf } = seitentitel(bloecke, seite.name);
    const ordner = seite.pfad.split('/').slice(0, -1);
    ersetzen(knoten.seite,
      el('div.nb-pfad', { text: ordner.join(' › ') || 'Notizbuch' }),
      el('h1.nb-titel', { text: titel }),
      kopf.erzeugt && HERKUNFT[seite.art] ? el('div.nb-herkunft', { text: HERKUNFT[seite.art] }) : null,
      ...bloeckeZeichnen(rumpf, hilfeFuer(seite, v)));
    angezeigt = seite.pfad;
    document.title = `${titel} · ${knoten.fenstertitel}`;
  }
  const stelle = abschnitt ? document.getElementById(`nb-${anker(abschnitt)}`) : null;
  if (stelle) stelle.scrollIntoView({ block: 'start' });
  else knoten.seite.parentElement.scrollTop = 0;
}

/** Wie Links einer Seite aufgelöst werden -- nach Name, oder relativ zu ihrem Ordner. */
function hilfeFuer(seite, v) {
  const ordner = seite.pfad.split('/').slice(0, -1);
  const aufloesen = (pfad) => {
    const teile = [...ordner];
    for (const t of decodeURI(pfad).split('/')) {
      if (t === '..') teile.pop();
      else if (t && t !== '.') teile.push(t);
    }
    return teile.join('/');
  };
  return {
    wiki(ziel, abschnitt) {
      const treffer = ziel ? v.nachName.get(ziel.normalize('NFC').toLowerCase())
        ?? v.nachPfad.get(`${ziel}.md`) : seite;
      return treffer ? { vorhanden: true, href: adresse(treffer.name, abschnitt) }
        : { vorhanden: false };
    },
    relativ(ziel) {
      const [pfad, abschnitt] = ziel.split('#');
      if (!pfad) return { vorhanden: true, href: adresse(seite.name, abschnitt) };
      const voll = aufloesen(pfad);
      const treffer = v.nachPfad.get(voll) ?? v.nachPfad.get(`${voll}.md`);
      if (treffer) return { vorhanden: true, href: adresse(treffer.name, abschnitt) };
      // Ausserhalb des Notizbuchs: die Datei selbst, so wie die Seite sie ausliefert.
      if (ordner.length + 1 <= (pfad.match(/\.\.\//g) || []).length) {
        return { vorhanden: true, href: new URL(voll.replace(/^(\.\.\/)+/, ''), WURZEL).href };
      }
      return { vorhanden: false };
    },
    bild(pfad) {
      const voll = aufloesen(pfad);
      const da = v.anhaenge.includes(voll) ? voll
        : v.anhaenge.find((a) => a.split('/').pop() === pfad.split('/').pop());
      return da ? pfadAdresse(da).href : null;
    },
  };
}

// ---------------------------------------------------------------------------
// Inhalt und Suche
// ---------------------------------------------------------------------------

/** Der Baum in der Folge des Verzeichnisses: Ordner, darin Seiten. */
function baumZeichnen(v) {
  const wurzel = { kinder: new Map(), seiten: [] };
  for (const s of v.seiten) {
    let ort = wurzel;
    for (const teil of s.pfad.split('/').slice(0, -1)) {
      if (!ort.kinder.has(teil)) ort.kinder.set(teil, { name: teil, kinder: new Map(), seiten: [] });
      ort = ort.kinder.get(teil);
    }
    ort.seiten.push(s);
  }
  const eintrag = (s) => el('a.nb-eintrag', { href: adresse(s.name), dataset: { pfad: s.pfad } }, [
    s.name,
  ]);
  const ordnerZeichnen = (ort, tiefe) => {
    // Die Ordnerseite -- sie heisst wie ihr Ordner -- ist der Ordner selbst.
    const eigene = ort.seiten.find((s) => s.name === ort.name);
    const uebrige = ort.seiten.filter((s) => s !== eigene);
    const anzahl = uebrige.length + [...ort.kinder.values()].reduce((n, k) => n + k.seiten.length, 0);
    // Zu, bis eine Seite darin gezeigt wird: Python allein hat achtzig.
    return el('details.nb-ordner', { dataset: { ordner: ort.name, tiefe: String(tiefe) } }, [
      el('summary', {}, [
        eigene ? eintrag(eigene) : el('span.nb-ordnername', { text: ort.name }),
        el('span.nb-anzahl', { text: String(anzahl) }),
      ]),
      ...[...ort.kinder.values()].map((k) => ordnerZeichnen(k, tiefe + 1)),
      ...uebrige.map(eintrag),
    ]);
  };
  ersetzen(knoten.baum,
    ...wurzel.seiten.map(eintrag),
    ...[...wurzel.kinder.values()].map((k) => ordnerZeichnen(k, 0)));
}

function baumMarkieren(seite) {
  for (const a of knoten.baum.querySelectorAll('[aria-current]')) a.removeAttribute('aria-current');
  if (!seite) return;
  const eintrag = [...knoten.baum.querySelectorAll('a.nb-eintrag')]
    .find((a) => a.dataset.pfad === seite.pfad);
  if (!eintrag) return;
  eintrag.setAttribute('aria-current', 'page');
  for (let d = eintrag.closest('details'); d; d = d.parentElement.closest('details')) d.open = true;
}

/** Für die Suche gleich: klein, ohne Umlaute, ohne die Zeichen von LaTeX. */
function sucheNormal(text) {
  return String(text).normalize('NFC').toLowerCase()
    .replace(/ä/g, 'ae').replace(/ö/g, 'oe').replace(/ü/g, 'ue').replace(/ß/g, 'ss')
    .replace(/[\\{}_^$\s]/g, '');
}

function treffer(v, frage) {
  const f = sucheNormal(frage);
  if (!f) return [];
  const rang = (s) => {
    const name = sucheNormal(s.name);
    if (name.startsWith(f)) return 0;
    if (name.includes(f)) return 1;
    if ((s.zeichen ?? []).some((z) => sucheNormal(z).includes(f))) return 2;
    if ([...(s.themen ?? []), ...(s.stichworte ?? []), s.kurz ?? '']
      .some((t) => sucheNormal(t).includes(f))) return 3;
    return null;
  };
  return v.seiten.map((s) => [rang(s), s]).filter(([r]) => r !== null)
    .sort((a, b) => a[0] - b[0]).map(([, s]) => s);
}

async function sucheZeigen() {
  const v = await verzeichnisLaden();
  const frage = knoten.suche.value.trim();
  if (!frage) {
    baumZeichnen(v);
    baumMarkieren(v.nachPfad.get(angezeigt));
    return;
  }
  const liste = treffer(v, frage);
  ersetzen(knoten.baum, liste.length
    ? el('div.nb-treffer', {}, liste.slice(0, 60).map((s) => el('a.nb-eintrag', {
      href: adresse(s.name), dataset: { pfad: s.pfad },
    }, [s.name, el('span.nb-art', { text: s.art })])))
    : el('p.nb-leer', { text: 'Nichts gefunden.' }));
}

async function sucheTaste(e) {
  if (e.key !== 'Enter') return;
  const erster = knoten.baum.querySelector('a.nb-eintrag');
  if (erster) location.hash = erster.getAttribute('href');
}
