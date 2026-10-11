/**
 * notizbuch_seite.js -- eine Seite des Notizbuchs als DOM.
 *
 * Baut aus dem Baum von markdown.js die Seite: mit `el()` und KaTeX, nie
 * über `innerHTML`. Die Notizen schreibt man in Obsidian; was dort steht,
 * darf auf der Seite nichts ausführen. Links führen nur ins Notizbuch, auf
 * http(s) oder an eine Mailadresse -- ein `javascript:` bleibt Text.
 *
 * Wohin ein Link führt, weiss diese Datei nicht: das sagt `hilfe` aus
 * notizbuch.js, das das Verzeichnis kennt.
 */

import { el } from './dom.js';
import { setzen, span } from './mathe.js';
import { klartext } from './markdown.js';
import { werkzeugleiste } from './kopierleiste.js';

/** Was ein Callout ohne eigenen Titel heisst, wie in Obsidian. */
const CALLOUT_TITEL = {
  info: 'Info', note: 'Notiz', abstract: 'Übersicht', summary: 'Übersicht', tip: 'Tipp',
  warning: 'Warnung', caution: 'Achtung', danger: 'Gefahr', error: 'Fehler',
  question: 'Frage', example: 'Beispiel', quote: 'Zitat', todo: 'Aufgabe', success: 'Erledigt',
};

const BILD = /\.(png|jpe?g|gif|svg|webp)$/i;
const SICHER = /^(https?:|mailto:)/i;
const SCHEMA = /^[a-z][a-z0-9+.-]*:/i;

/**
 * @param bloecke  aus `zerlegen(text).bloecke`
 * @param hilfe    `{ wiki(ziel, anker) -> {href, vorhanden}, relativ(pfad) -> {href, vorhanden},
 *                    bild(pfad) -> url|null }`
 */
export function bloeckeZeichnen(bloecke, hilfe) {
  return bloecke.map((b) => block(b, hilfe)).filter(Boolean);
}

function block(b, hilfe) {
  switch (b.art) {
    case 'ueberschrift':
      return el(`h${Math.min(b.stufe + 1, 6)}.nb-ueberschrift`,
        { id: `nb-${b.anker}` }, zeile(b.inhalt, hilfe));
    case 'absatz':
      return el('p', {}, zeile(b.inhalt, hilfe));
    case 'liste':
      return liste(b, hilfe);
    case 'code':
      return el('pre.nb-code', {}, [el('code', {
        text: b.text, class: b.sprache ? `sprache-${b.sprache}` : null,
      })]);
    case 'mathe':
      return formel(b.latex);
    case 'tabelle':
      return tabelle(b, hilfe);
    case 'zitat':
      return el('blockquote.nb-zitat', {}, bloeckeZeichnen(b.bloecke, hilfe));
    case 'callout':
      return callout(b, hilfe);
    case 'linie':
      return el('hr');
    default:
      return null;
  }
}

function formel(latex) {
  const huelle = el('div.nb-formel', {}, [
    el('div.gleichung-mathe'),
    werkzeugleiste({ latex, markdown: `$$\n${latex}\n$$` }),
  ]);
  setzen(latex, huelle.querySelector('.gleichung-mathe'));
  return huelle;
}

function liste(b, hilfe) {
  const punkte = b.punkte.map((p) => {
    // Ein Punkt aus einem Absatz steht ohne Absatz da -- sonst stünde jede
    // Zeile einer gewöhnlichen Liste mit Abstand.
    const inhalt = p.bloecke.length === 1 && p.bloecke[0].art === 'absatz'
      ? zeile(p.bloecke[0].inhalt, hilfe)
      : bloeckeZeichnen(p.bloecke, hilfe);
    if (p.aufgabe === null) return el('li', {}, inhalt);
    return el('li.nb-aufgabe', {}, [
      el('input', { type: 'checkbox', checked: p.aufgabe, disabled: true, 'aria-hidden': 'true' }),
      el('span', {}, inhalt),
    ]);
  });
  return b.geordnet
    ? el('ol', { start: b.start !== 1 ? b.start : null }, punkte)
    : el('ul', {}, punkte);
}

function tabelle(b, hilfe) {
  const ausrichten = (k) => ({ links: 'left', mitte: 'center', rechts: 'right' }[b.ausrichtung[k]] ?? null);
  const zelle = (tag, inhalt, k) => el(tag, { style: ausrichten(k) ? { textAlign: ausrichten(k) } : null },
    zeile(inhalt, hilfe));
  return el('div.nb-tabelle', {}, [el('table', {}, [
    el('thead', {}, [el('tr', {}, b.kopf.map((z, k) => zelle('th', z, k)))]),
    el('tbody', {}, b.zeilen.map((r) => el('tr', {}, r.map((z, k) => zelle('td', z, k))))),
  ])]);
}

function callout(b, hilfe) {
  const titel = b.titel.length ? zeile(b.titel, hilfe)
    : [CALLOUT_TITEL[b.typ] ?? b.typ.charAt(0).toUpperCase() + b.typ.slice(1)];
  const inhalt = el('div.nb-callout-inhalt', {}, bloeckeZeichnen(b.bloecke, hilfe));
  const klasse = `nb-callout.nb-callout-${b.typ.replace(/[^a-z-]/g, '')}`;
  if (!b.falten) {
    return el(`div.${klasse}`, {}, [el('div.nb-callout-titel', {}, titel), inhalt]);
  }
  return el(`details.${klasse}`, { open: b.falten === '+' }, [
    el('summary.nb-callout-titel', {}, titel), inhalt,
  ]);
}

// ---------------------------------------------------------------------------
// Innerhalb einer Zeile
// ---------------------------------------------------------------------------

function zeile(knoten, hilfe) {
  return knoten.map((k) => stueck(k, hilfe));
}

function stueck(k, hilfe) {
  switch (k.art) {
    case 'text':
      return document.createTextNode(k.text);
    case 'umbruch':
      return el('br');
    case 'fett':
      return el('strong', {}, zeile(k.inhalt, hilfe));
    case 'kursiv':
      return el('em', {}, zeile(k.inhalt, hilfe));
    case 'durch':
      return el('s', {}, zeile(k.inhalt, hilfe));
    case 'markiert':
      return el('mark', {}, zeile(k.inhalt, hilfe));
    case 'code':
      return el('code.nb-codestueck', { text: k.text });
    case 'mathe':
      return k.abgesetzt ? formel(k.latex) : span(k.latex);
    case 'wiki':
      return wiki(k, hilfe);
    case 'link':
      return link(k, hilfe);
    case 'bild':
      return bild(k.ziel, k.alt, k.breite, hilfe);
    default:
      return document.createTextNode('');
  }
}

function wiki(k, hilfe) {
  if (k.einbetten && BILD.test(k.ziel)) {
    return bild(k.ziel, k.ziel, parseInt(k.text, 10) || null, hilfe);
  }
  const anzeige = k.text ?? (k.anker ? `${k.ziel} › ${k.anker}` : k.ziel);
  const ziel = hilfe.wiki(k.ziel, k.anker);
  if (!ziel.vorhanden) {
    return el('span.nb-fehlt', { text: anzeige, title: `Seite «${k.ziel}» gibt es nicht` });
  }
  return el('a.nb-link', { href: ziel.href, text: anzeige });
}

function link(k, hilfe) {
  const inhalt = zeile(k.inhalt, hilfe);
  if (SICHER.test(k.ziel)) {
    return el('a.nb-link.nb-aussen', { href: k.ziel, target: '_blank', rel: 'noopener noreferrer' },
      inhalt);
  }
  if (SCHEMA.test(k.ziel)) return el('span', {}, inhalt);
  const ziel = hilfe.relativ(k.ziel);
  if (!ziel.vorhanden) return el('span.nb-fehlt', { title: `«${k.ziel}» gibt es nicht` }, inhalt);
  return el('a.nb-link', { href: ziel.href }, inhalt);
}

function bild(pfad, alt, breite, hilfe) {
  const url = SICHER.test(pfad) ? pfad : hilfe.bild(pfad);
  if (!url) return el('span.nb-fehlt', { text: alt || pfad, title: `Bild «${pfad}» gibt es nicht` });
  return el('img.nb-bild', { src: url, alt: alt || '', width: breite || null, loading: 'lazy' });
}

/**
 * Titel und Rumpf einer Seite: beginnt sie mit einer Überschrift erster
 * Stufe, ist das ihr Titel; sonst ihr Name, wie Obsidian ihn über die Seite
 * schreibt.
 */
export function seitentitel(bloecke, name) {
  const erste = bloecke[0];
  return erste?.art === 'ueberschrift' && erste.stufe === 1
    ? { titel: klartext(erste.inhalt), rumpf: bloecke.slice(1) }
    : { titel: name, rumpf: bloecke };
}
