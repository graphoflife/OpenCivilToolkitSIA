/**
 * markdown.js -- Markdown in einen Baum zerlegen, so wie Obsidian es liest.
 *
 * Die Seiten des Notizbuchs (notizbuch/) sind Markdown: Obsidian liest den
 * Ordner als Tresor, die Oberfläche zeigt ihn unter «Formelsammlung». Eine
 * fremde Bibliothek gibt es dafür nicht; dieses Modul zerlegt, was der
 * Generator schreibt und was man in Obsidian gewöhnlich tippt:
 *
 *   Kopf (---), Überschriften, Absätze, fett, kursiv, Code, durchgestrichen,
 *   markiert, Listen (verschachtelt, nummeriert, Aufgaben), Codeblöcke,
 *   Tabellen, Zitate, Callouts (> [!info]), Linien, Formeln ($ und $$),
 *   Links ([[Seite]], [[Seite#Abschnitt|Text]], [Text](Ziel)) und Bilder.
 *
 * Kommentare (%%…%% und <!-- … -->) fallen weg. HTML wird nie ausgeführt:
 * es bleibt Text.
 *
 * REIN:
 * Keine Imports, kein DOM. Heraus kommt ein Baum aus gewöhnlichen Objekten
 * -- node prüft ihn im Test (tests/test_markdown_js.py) über jede Seite des
 * Notizbuchs, notizbuch_seite.js baut daraus die Seite.
 *
 * ZEILENUMBRÜCHE:
 * Wie in Obsidian mit «strengen Zeilenumbrüchen» (notizbuch/.obsidian):
 * ein einfacher Umbruch ist ein Leerzeichen, zwei Leerzeichen oder ein «\»
 * am Zeilenende brechen um.
 *
 * BEWUSST NICHT:
 * Setext-Überschriften, Referenzlinks, Fussnoten, Block-Kennungen (^id) und
 * eingebettete Notizen -- die erscheinen als Link.
 */

const ZAUN = /^( {0,3})(`{3,}|~{3,})[ \t]*([^`\s]*)[^`]*$/;
const UEBERSCHRIFT = /^ {0,3}(#{1,6})(?:[ \t]+(.*?))?(?:[ \t]+#+)?[ \t]*$/;
const LINIE = /^ {0,3}([-*_])(?:[ \t]*\1){2,}[ \t]*$/;
const ZITAT = /^ {0,3}> ?(.*)$/;
const PUNKT = /^( *)([-*+]|\d{1,9}[.)])( +|$)(.*)$/;
const TRENNER = /^ *\|? *:?-+:? *(\| *:?-+:? *)*\|? *$/;
const CALLOUT = /^\[!([^\]\s]+)\]([+-]?)[ \t]*(.*)$/;
const AUFGABE = /^\[([ xX])\](?:[ \t]+|$)/;
const SATZZEICHEN = /[!-/:-@[-`{-~]/;
const BUCHSTABE = /[\p{L}\p{N}]/u;

/**
 * Zerlegt eine ganze Seite: ``{kopf, bloecke}``. Der Kopf sind die
 * Eigenschaften zwischen den beiden ``---`` am Anfang.
 */
export function zerlegen(text) {
  let rest = String(text ?? '').replace(/\r\n?/g, '\n');
  let kopf = {};
  if (rest.startsWith('---\n')) {
    const ende = rest.indexOf('\n---', 3);
    if (ende >= 0 && (rest[ende + 4] === '\n' || ende + 4 === rest.length)) {
      kopf = kopfLesen(rest.slice(4, ende));
      rest = rest.slice(ende + 5);
    }
  }
  const zeilen = rest.split('\n').map(einrueckungAusschreiben);
  const bloecke = bloeckeLesen(zeilen);
  ankerVergeben(bloecke);
  return { kopf, bloecke };
}

/** Der Anker einer Überschrift: so heisst sie in ``[[Seite#Überschrift]]``. */
export function anker(text) {
  return String(text).normalize('NFC').toLowerCase()
    .replace(/[#^|:%[\]]/g, ' ').trim().replace(/\s+/g, '-');
}

/** Der Text eines Stücks Zeile, ohne Auszeichnung -- für Anker und Suche. */
export function klartext(knoten) {
  return knoten.map((k) => {
    if (k.art === 'text' || k.art === 'code') return k.text;
    if (k.art === 'mathe') return k.latex;
    if (k.art === 'wiki') return k.text ?? (k.anker ? `${k.ziel} ${k.anker}` : k.ziel);
    if (k.art === 'umbruch') return ' ';
    if (k.inhalt) return klartext(k.inhalt);
    return k.alt ?? '';
  }).join('');
}

// ---------------------------------------------------------------------------
// Kopf
// ---------------------------------------------------------------------------

function kopfLesen(text) {
  const kopf = {};
  let liste = null;
  for (const zeile of text.split('\n')) {
    const punkt = /^\s+-\s*(.*)$/.exec(zeile);
    if (punkt && liste) {
      liste.push(kopfWert(punkt[1]));
      continue;
    }
    const m = /^([^:\s][^:]*):\s*(.*)$/.exec(zeile);
    if (!m) continue;
    const [, schluessel, wert] = m;
    if (wert === '') {
      liste = kopf[schluessel.trim()] = [];
    } else {
      liste = null;
      kopf[schluessel.trim()] = kopfWert(wert);
    }
  }
  return kopf;
}

function kopfWert(wert) {
  const w = wert.trim();
  if (w.startsWith('[') && w.endsWith(']')) {
    return w.slice(1, -1).split(',').map((t) => kopfWert(t)).filter((t) => t !== '');
  }
  if (w.startsWith('"') && w.endsWith('"') && w.length >= 2) {
    try { return JSON.parse(w); } catch { return w.slice(1, -1); }
  }
  if (w.startsWith("'") && w.endsWith("'") && w.length >= 2) {
    return w.slice(1, -1).replace(/''/g, "'");
  }
  if (w === 'true' || w === 'false') return w === 'true';
  return w;
}

// ---------------------------------------------------------------------------
// Blöcke
// ---------------------------------------------------------------------------

/** Tabulatoren am Zeilenanfang als Leerzeichen, auf Vielfache von vier. */
function einrueckungAusschreiben(zeile) {
  const m = /^[ \t]+/.exec(zeile);
  if (!m || !m[0].includes('\t')) return zeile;
  let breite = 0;
  for (const z of m[0]) breite = z === '\t' ? breite + 4 - (breite % 4) : breite + 1;
  return ' '.repeat(breite) + zeile.slice(m[0].length);
}

function einzug(zeile) {
  return zeile.length - zeile.trimStart().length;
}

function istMatheZeile(zeile) {
  const t = zeile.trim();
  return t === '$$' || (t.startsWith('$$') && t.endsWith('$$') && t.length > 4);
}

function istTabelle(zeilen, i) {
  return zeilen[i].includes('|') && i + 1 < zeilen.length
    && zeilen[i + 1].includes('-') && zeilen[i + 1].includes('|')
    && TRENNER.test(zeilen[i + 1]);
}

/** Ob eine Zeile einen neuen Block beginnt -- dann setzt sie keinen Absatz fort. */
function beginntBlock(zeile) {
  return ZAUN.test(zeile) || UEBERSCHRIFT.test(zeile) || LINIE.test(zeile)
    || ZITAT.test(zeile) || PUNKT.test(zeile) || istMatheZeile(zeile);
}

function bloeckeLesen(zeilen) {
  const bloecke = [];
  let absatz = null;
  const absatzEnde = () => {
    if (absatz) bloecke.push({ art: 'absatz', inhalt: inline(absatz.join('\n')) });
    absatz = null;
  };

  let i = 0;
  while (i < zeilen.length) {
    const zeile = zeilen[i];
    if (!zeile.trim()) {
      absatzEnde();
      i += 1;
      continue;
    }
    const kommentar = kommentarZeilen(zeilen, i);
    if (kommentar) {
      absatzEnde();
      i += kommentar;
      continue;
    }
    let m;
    if ((m = ZAUN.exec(zeile))) {
      absatzEnde();
      i = zaunLesen(zeilen, i, m, bloecke);
      continue;
    }
    if (istMatheZeile(zeile)) {
      absatzEnde();
      i = matheLesen(zeilen, i, bloecke);
      continue;
    }
    if ((m = UEBERSCHRIFT.exec(zeile))) {
      absatzEnde();
      bloecke.push({ art: 'ueberschrift', stufe: m[1].length, inhalt: inline(m[2] ?? '') });
      i += 1;
      continue;
    }
    if (LINIE.test(zeile)) {
      absatzEnde();
      bloecke.push({ art: 'linie' });
      i += 1;
      continue;
    }
    if (ZITAT.test(zeile)) {
      absatzEnde();
      i = zitatLesen(zeilen, i, bloecke);
      continue;
    }
    if (istTabelle(zeilen, i)) {
      absatzEnde();
      i = tabelleLesen(zeilen, i, bloecke);
      continue;
    }
    if ((m = PUNKT.exec(zeile)) && (!absatz || unterbricht(m))) {
      absatzEnde();
      i = listeLesen(zeilen, i, bloecke);
      continue;
    }
    if (!absatz && einzug(zeile) >= 4) {
      i = eingerueckterCode(zeilen, i, bloecke);
      continue;
    }
    (absatz ??= []).push(zeile);
    i += 1;
  }
  absatzEnde();
  return bloecke;
}

/** Ein Listenpunkt unterbricht einen Absatz nur, wenn er etwas enthält -- nummeriert nur mit 1. */
function unterbricht(m) {
  if (!m[4].trim()) return false;
  return !/\d/.test(m[2]) || parseInt(m[2], 10) === 1;
}

/** Wie viele Zeilen ein Kommentar über ganze Zeilen einnimmt -- 0: keiner. */
function kommentarZeilen(zeilen, i) {
  const t = zeilen[i].trim();
  for (const [auf, zu] of [['<!--', '-->'], ['%%', '%%']]) {
    if (!t.startsWith(auf)) continue;
    const ende = t.indexOf(zu, auf.length);
    if (ende >= 0) return t.slice(ende + zu.length).trim() ? 0 : 1;
    let k = i + 1;
    while (k < zeilen.length && !zeilen[k].includes(zu)) k += 1;
    return Math.min(k + 1, zeilen.length) - i;
  }
  return 0;
}

function zaunLesen(zeilen, i, m, bloecke) {
  const [, rand, zaun, sprache] = m;
  const text = [];
  let k = i + 1;
  const schluss = new RegExp(`^ {0,3}${zaun[0] === '`' ? '`' : '~'}{${zaun.length},}[ \\t]*$`);
  while (k < zeilen.length && !schluss.test(zeilen[k])) {
    const z = zeilen[k];
    text.push(z.slice(Math.min(rand.length, einzug(z))));
    k += 1;
  }
  bloecke.push({ art: 'code', sprache, text: text.join('\n') });
  return k + 1;
}

function matheLesen(zeilen, i, bloecke) {
  const t = zeilen[i].trim();
  if (t !== '$$') {
    bloecke.push({ art: 'mathe', latex: t.slice(2, -2).trim() });
    return i + 1;
  }
  const latex = [];
  let k = i + 1;
  while (k < zeilen.length && !zeilen[k].trim().endsWith('$$')) {
    latex.push(zeilen[k]);
    k += 1;
  }
  if (k < zeilen.length) latex.push(zeilen[k].trim().slice(0, -2));
  bloecke.push({ art: 'mathe', latex: latex.join('\n').trim() });
  return k + 1;
}

function zitatLesen(zeilen, i, bloecke) {
  const innen = [];
  let k = i;
  while (k < zeilen.length && ZITAT.test(zeilen[k])) {
    innen.push(ZITAT.exec(zeilen[k])[1]);
    k += 1;
  }
  const kopf = CALLOUT.exec(innen[0]);
  if (kopf) {
    bloecke.push({
      art: 'callout', typ: kopf[1].toLowerCase(), falten: kopf[2],
      titel: inline(kopf[3]), bloecke: bloeckeLesen(innen.slice(1)),
    });
  } else {
    bloecke.push({ art: 'zitat', bloecke: bloeckeLesen(innen) });
  }
  return k;
}

/** Die Zellen einer Tabellenzeile. Ein ``\|`` ist ein Strich und trennt nicht. */
function zellen(zeile) {
  let s = zeile.trim();
  if (s.startsWith('|')) s = s.slice(1);
  if (s.endsWith('|') && !s.endsWith('\\|')) s = s.slice(0, -1);
  const teile = [];
  let jetzt = '';
  for (let k = 0; k < s.length; k += 1) {
    if (s[k] === '\\' && s[k + 1] === '|') {
      jetzt += '|';
      k += 1;
    } else if (s[k] === '|') {
      teile.push(jetzt.trim());
      jetzt = '';
    } else {
      jetzt += s[k];
    }
  }
  teile.push(jetzt.trim());
  return teile;
}

function tabelleLesen(zeilen, i, bloecke) {
  const kopf = zellen(zeilen[i]);
  const ausrichtung = zellen(zeilen[i + 1]).map((z) => {
    const links = z.startsWith(':');
    const rechts = z.endsWith(':');
    if (links && rechts) return 'mitte';
    if (rechts) return 'rechts';
    return links ? 'links' : '';
  });
  const breite = kopf.length;
  const passend = (reihe) => Array.from({ length: breite }, (_, k) => inline(reihe[k] ?? ''));
  const reihen = [];
  let k = i + 2;
  while (k < zeilen.length && zeilen[k].trim() && zeilen[k].includes('|')) {
    reihen.push(passend(zellen(zeilen[k])));
    k += 1;
  }
  bloecke.push({
    art: 'tabelle', ausrichtung: Array.from({ length: breite }, (_, j) => ausrichtung[j] ?? ''),
    kopf: passend(kopf), zeilen: reihen,
  });
  return k;
}

function listeLesen(zeilen, i, bloecke) {
  const erste = PUNKT.exec(zeilen[i]);
  const geordnet = /\d/.test(erste[2]);
  const rand = erste[1].length;
  const liste = { art: 'liste', geordnet, start: geordnet ? parseInt(erste[2], 10) : 1, punkte: [] };
  let k = i;
  while (k < zeilen.length) {
    const m = PUNKT.exec(zeilen[k]);
    if (!m || /\d/.test(m[2]) !== geordnet || m[1].length < rand || m[1].length > rand + 3) break;
    // Mehr als vier Leerzeichen nach dem Zeichen: der Inhalt beginnt nach einem.
    const abstand = m[3].length > 4 || !m[4] ? 1 : m[3].length;
    const tiefe = m[1].length + m[2].length + abstand;
    const inhalt = [m[3].length > 4 ? ' '.repeat(m[3].length - 1) + m[4] : m[4]];
    k += 1;
    let leer = false;
    while (k < zeilen.length) {
      const z = zeilen[k];
      if (!z.trim()) {
        inhalt.push('');
        leer = true;
      } else if (einzug(z) >= tiefe) {
        inhalt.push(z.slice(tiefe));
        leer = false;
      } else if (!leer && !beginntBlock(z) && !istTabelle(zeilen, k)) {
        // Faule Fortsetzung: die Zeile gehört noch zum Absatz davor.
        inhalt.push(z.trimStart());
      } else {
        break;
      }
      k += 1;
    }
    while (inhalt.length > 1 && !inhalt[inhalt.length - 1].trim()) inhalt.pop();
    let aufgabe = null;
    const a = AUFGABE.exec(inhalt[0]);
    if (a) {
      aufgabe = a[1] !== ' ';
      inhalt[0] = inhalt[0].slice(a[0].length);
    }
    liste.punkte.push({ aufgabe, bloecke: bloeckeLesen(inhalt) });
  }
  bloecke.push(liste);
  return k;
}

function eingerueckterCode(zeilen, i, bloecke) {
  const text = [];
  let k = i;
  while (k < zeilen.length && (!zeilen[k].trim() || einzug(zeilen[k]) >= 4)) {
    text.push(zeilen[k].slice(Math.min(4, einzug(zeilen[k]))));
    k += 1;
  }
  while (text.length && !text[text.length - 1].trim()) text.pop();
  bloecke.push({ art: 'code', sprache: '', text: text.join('\n') });
  return k;
}

/** Jede Überschrift bekommt ihren Anker; doppelte zählen weiter: -2, -3. */
function ankerVergeben(bloecke) {
  const vergeben = new Map();
  const gehen = (liste) => {
    for (const b of liste) {
      if (b.art === 'ueberschrift') {
        const grund = anker(klartext(b.inhalt));
        const n = (vergeben.get(grund) ?? 0) + 1;
        vergeben.set(grund, n);
        b.anker = n === 1 ? grund : `${grund}-${n}`;
      }
      if (b.bloecke) gehen(b.bloecke);
      if (b.punkte) b.punkte.forEach((p) => gehen(p.bloecke));
    }
  };
  gehen(bloecke);
}

// ---------------------------------------------------------------------------
// Innerhalb einer Zeile
// ---------------------------------------------------------------------------

/** Zerlegt Text innerhalb eines Blocks in Stücke: Text, Auszeichnung, Formeln, Links. */
export function inline(text) {
  const knoten = [];
  let puffer = '';
  const textAus = () => {
    if (puffer) knoten.push({ art: 'text', text: puffer });
    puffer = '';
  };
  const setzen = (stueck, ende) => {
    textAus();
    knoten.push(stueck);
    return ende;
  };

  let i = 0;
  while (i < text.length) {
    const c = text[i];
    if (c === '\\' && i + 1 < text.length && SATZZEICHEN.test(text[i + 1])) {
      puffer += text[i + 1];
      i += 2;
      continue;
    }
    if (c === '\n') {
      if (/ {2,}$/.test(puffer) || puffer.endsWith('\\')) {
        puffer = puffer.replace(/(?: {2,}|\\)$/, '');
        textAus();
        knoten.push({ art: 'umbruch' });
      } else {
        puffer = puffer.replace(/ +$/, '') + ' ';
      }
      i += 1;
      while (text[i] === ' ') i += 1;
      continue;
    }
    let treffer = null;
    if (c === '`') treffer = codeAb(text, i);
    else if (c === '$') treffer = matheAb(text, i);
    else if (c === '<' && text.startsWith('<!--', i)) treffer = kommentarAb(text, i, '<!--', '-->');
    else if (c === '%' && text.startsWith('%%', i)) treffer = kommentarAb(text, i, '%%', '%%');
    else if (c === '<') treffer = autolinkAb(text, i);
    else if (c === '[' && text[i + 1] === '[') treffer = wikiAb(text, i, false);
    else if (c === '!' && text.startsWith('![[', i)) treffer = wikiAb(text, i + 1, true);
    else if (c === '!' && text[i + 1] === '[') treffer = linkAb(text, i + 1, true);
    else if (c === '[') treffer = linkAb(text, i, false);
    else if (c === 'h' && (i === 0 || /[\s(«]/.test(text[i - 1]))) treffer = adresseAb(text, i);
    else if ('*_~='.includes(c)) treffer = auszeichnungAb(text, i);
    if (treffer) {
      i = treffer.stueck ? setzen(treffer.stueck, treffer.ende) : treffer.ende;
      continue;
    }
    puffer += c;
    i += 1;
  }
  textAus();
  return knoten;
}

function codeAb(text, i) {
  let lauf = 1;
  while (text[i + lauf] === '`') lauf += 1;
  const zaun = '`'.repeat(lauf);
  let j = i + lauf;
  while ((j = text.indexOf(zaun, j)) >= 0) {
    if (text[j + lauf] !== '`' && text[j - 1] !== '`') break;
    while (text[j] === '`') j += 1;
  }
  if (j < 0) return { stueck: { art: 'text', text: zaun }, ende: i + lauf };
  let inhalt = text.slice(i + lauf, j).replace(/\n/g, ' ');
  if (/^ .*[^ ].* $/.test(inhalt)) inhalt = inhalt.slice(1, -1);
  return { stueck: { art: 'code', text: inhalt }, ende: j + lauf };
}

function matheAb(text, i) {
  if (text.startsWith('$$', i)) {
    const j = text.indexOf('$$', i + 2);
    if (j < 0 || !text.slice(i + 2, j).trim()) return null;
    return { stueck: { art: 'mathe', latex: text.slice(i + 2, j).trim(), abgesetzt: true },
             ende: j + 2 };
  }
  const nach = text[i + 1];
  if (!nach || /\s/.test(nach) || nach === '$') return null;
  for (let j = i + 1; j < text.length; j += 1) {
    if (text[j] === '\\') {
      j += 1;
      continue;
    }
    if (text[j] !== '$') continue;
    if (/\s/.test(text[j - 1]) || /\d/.test(text[j + 1] ?? '')) return null;
    return { stueck: { art: 'mathe', latex: text.slice(i + 1, j) }, ende: j + 1 };
  }
  return null;
}

function kommentarAb(text, i, auf, zu) {
  const j = text.indexOf(zu, i + auf.length);
  return j < 0 ? null : { stueck: null, ende: j + zu.length };
}

function autolinkAb(text, i) {
  const m = /^<(https?:\/\/[^\s<>]+|mailto:[^\s<>]+)>/.exec(text.slice(i));
  if (!m) return null;
  return { stueck: { art: 'link', ziel: m[1], inhalt: [{ art: 'text', text: m[1].replace(/^mailto:/, '') }] },
           ende: i + m[0].length };
}

function adresseAb(text, i) {
  const m = /^https?:\/\/[^\s<>]*[^\s<>.,;:!?'"»)\]]/.exec(text.slice(i));
  if (!m) return null;
  return { stueck: { art: 'link', ziel: m[0], inhalt: [{ art: 'text', text: m[0] }] },
           ende: i + m[0].length };
}

/** ``[[Ziel#Anker|Text]]`` ab der ersten Klammer; ``einbetten`` bei ``![[…]]``. */
function wikiAb(text, i, einbetten) {
  const ende = text.indexOf(']]', i + 2);
  if (ende < 0) return null;
  const innen = text.slice(i + 2, ende);
  if (!innen.trim() || innen.includes('\n') || innen.includes('[[')) return null;
  const strich = innen.search(/(?<!\\)\|/);
  const ort = (strich < 0 ? innen : innen.slice(0, strich)).replace(/\\\|/g, '|');
  const anzeige = strich < 0 ? null : innen.slice(strich + 1).trim();
  const raute = ort.indexOf('#');
  return {
    stueck: {
      art: 'wiki', einbetten,
      ziel: (raute < 0 ? ort : ort.slice(0, raute)).trim(),
      anker: raute < 0 ? null : ort.slice(raute + 1).trim(),
      text: anzeige || null,
    },
    ende: ende + 2,
  };
}

/** ``[Text](Ziel)`` ab der eckigen Klammer, oder ein Bild ``![Text](Ziel)``. */
function linkAb(text, i, bild) {
  let tiefe = 0;
  let j = i;
  for (; j < text.length; j += 1) {
    if (text[j] === '\\') {
      j += 1;
    } else if (text[j] === '[') {
      tiefe += 1;
    } else if (text[j] === ']') {
      tiefe -= 1;
      if (tiefe === 0) break;
    }
  }
  if (j >= text.length || text[j + 1] !== '(') return null;
  const etikett = text.slice(i + 1, j);
  let k = j + 2;
  let ziel;
  if (text[k] === '<') {
    const zu = text.indexOf('>', k);
    if (zu < 0) return null;
    ziel = text.slice(k + 1, zu);
    k = zu + 1;
  } else {
    let klammern = 0;
    const anfang = k;
    for (; k < text.length; k += 1) {
      if (text[k] === '(') klammern += 1;
      else if (text[k] === ')' && klammern-- === 0) break;
      else if (/\s/.test(text[k])) break;
    }
    ziel = text.slice(anfang, k);
  }
  const zu = text.indexOf(')', k);
  if (zu < 0) return null;
  const ende = zu + 1;
  if (bild) {
    const [alt, breite] = etikett.split('|');
    return { stueck: { art: 'bild', ziel, alt: alt.trim(), breite: parseInt(breite, 10) || null },
             ende };
  }
  return { stueck: { art: 'link', ziel, inhalt: inline(etikett) }, ende };
}

const AUSZEICHNUNG = [['**', 'fett'], ['__', 'fett'], ['~~', 'durch'], ['==', 'markiert'],
  ['*', 'kursiv'], ['_', 'kursiv']];

function auszeichnungAb(text, i) {
  for (const [zeichen, art] of AUSZEICHNUNG) {
    if (!text.startsWith(zeichen, i)) continue;
    const lang = zeichen.length;
    const nach = text[i + lang];
    if (!nach || /\s/.test(nach)) continue;
    if (zeichen[0] === '_' && i > 0 && BUCHSTABE.test(text[i - 1])) continue;
    for (let j = text.indexOf(zeichen, i + lang + 1); j >= 0; j = text.indexOf(zeichen, j + 1)) {
      const vor = text[j - 1];
      if (/\s/.test(vor) || vor === '\\') continue;
      if (lang === 1 && (text[j + 1] === zeichen || text[j - 1] === zeichen)) continue;
      if (zeichen[0] === '_' && BUCHSTABE.test(text[j + lang] ?? '')) continue;
      return { stueck: { art, inhalt: inline(text.slice(i + lang, j)) }, ende: j + lang };
    }
  }
  return null;
}
