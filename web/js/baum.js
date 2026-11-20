/**
 * baum.js -- Linke Tafel: die Apps und die Bestandteile des Projekts.
 *
 * Oben je App ein Knopf mit Zeichen, wie die Kapitel einer Platte in der
 * Mitte (Benutzer, 2026-10-15): Materialien, Stahlbeton-Platten,
 * Querschnittsanalyse, 2D Balkensysteme, Grundbruch, Setzung, Python. Darunter steht
 * die Liste der gewählten App, mit «+» zum Anlegen -- bei den Materialien je
 * eine für Beton und Betonstahl. Darüber, zuoberst in der Tafel, der Name des
 * gezeigten Projekts (index.html) und die Reiter aller Projekte (projekte.js).
 *
 * Zuoberst in jeder Liste ausser den Materialien steht die Sandbox, golden
 * (Benutzer, 2026-11-20): zum Ausprobieren, mit ↺ statt ×.
 *
 * Beim Löschen eines Materials wird geprüft, ob eine Platte,
 * eine Querschnittsanalyse oder ein Balkensystem es noch braucht -- und beim
 * Löschen einer Platte oder Analyse, ob ein Balkensystem ihren Querschnitt
 * nimmt. Sonst wäre die Beschreibung anschliessend widersprüchlich, und der
 * Rechenkern müsste einen Fehler melden, den die Oberfläche hätte verhindern
 * können.
 *
 * Was eine App zeigt und wie ihre Einträge entstehen und weggehen, steht in
 * ihrer Zeile (apps.js); hier wird nur gezeichnet.
 */

import { APPS, appVon } from './apps.js';
import { el, ersetzen } from './dom.js';
import { sinnbild } from './sinnbilder.js';
import {
  appWaehlen, gewaehlteApp, istSandbox, waehlen, zustand,
} from './zustand.js';

// ===========================================================================
// Bausteine
// ===========================================================================

/**
 * Ein Knopf je App. Das Zeichen ist blau, sobald es darin etwas gibt -- wie
 * bei den Kapiteln einer Platte, die etwas rechnen; die gewählte App trägt
 * dazu Grund und Rand der Auswahl. Auf dem Knopf steht nur die Zahl ihrer
 * Einträge, «1 Querschnittsanalyse» passte nicht hinein. Die Sandbox zählt
 * nicht: sie steht in jeder App, und jedes Zeichen sagte sonst «hier gibt es
 * etwas».
 */
function appKnopf(a, p, gewaehlt) {
  const eintraege = p[a.liste] || [];
  const zahl = eigene(eintraege);
  return el('button.kachel.app-kachel', {
    type: 'button', 'aria-pressed': String(gewaehlt),
    class: `${gewaehlt ? 'ist-gewaehlt' : ''} ${zahl ? 'ist-an' : ''}`,
    title: a.knopf.replace(/\u00AD/g, ''),
    on: { click: () => appWaehlen(a.app, eintraege) },
  }, [
    sinnbild(a.zeichen),
    el('span.kachel-name', { text: a.knopf }),
    el('span.kachel-stand', { text: String(zahl) }),
  ]);
}

/**
 * Eine Liste unter den Knöpfen: Titel, Zahl und «+», darunter die Einträge.
 * Die Zahl ohne die Sandbox, wie auf dem Knopf der App.
 */
function liste(a, { titel, eintraege, plus, leer }) {
  return el('div.baum-gruppe', {}, [
    el('div.baum-kopf', {}, [
      el('span.titel', { text: titel }),
      el('span.zaehler', { text: String(eigene(eintraege)) }),
      el('span.werkzeuge', {}, [el('button.knopf.knopf-zart', {
        text: '+', title: plus.titel, on: { click: plus.tun },
      })]),
    ]),
    el('div.baum-koerper', {},
      eintraege.length ? eintraege.map((e) => eintrag(a, e)) : [el('div.leer-zeile', { text: leer })]),
  ]);
}

/**
 * Ein Eintrag: sein Name, beim Material ob es eine Normsorte ist, rechts sein
 * Kurztext. Die Sandbox trägt ↺ statt × -- sie lässt sich zurücksetzen, nicht
 * löschen.
 */
function eintrag(a, e) {
  const aktiv = zustand.auswahl?.art === a.app && zustand.auswahl.kennung === e.kennung;
  const sandbox = istSandbox(e.kennung);
  return el('div.baum-eintrag', {
    class: `${aktiv ? 'ist-aktiv' : ''} ${sandbox ? 'ist-sandbox' : ''}`,
    on: { click: () => waehlen({ art: a.app, kennung: e.kennung }) },
  }, [
    el('span.name', {
      text: a.name(e),
      title: sandbox ? 'Zum Ausprobieren – nicht im Bericht, nach jedem Laden der Seite neu'
        : a.name(e),
    }),
    a.marke?.(e) ?? null,
    el('span.art', { text: a.kurztext(e) }),
    knopf('⧉', sandbox ? 'Kopieren – die Kopie ist ein gewöhnlicher Eintrag' : 'Kopieren',
      () => a.kopieren(e)),
    sandbox
      ? knopf('↺', 'Zurücksetzen – die Sandbox beginnt neu', () => a.zuruecksetzen(e))
      : knopf('×', 'Entfernen', () => a.loeschen(e), '.knopf-gefahr'),
  ]);
}

/** Wie viele Einträge einer Liste zum Projekt gehören -- alle ausser der Sandbox. */
const eigene = (eintraege) => eintraege.filter((e) => !istSandbox(e.kennung)).length;

/** Ein kleiner Knopf am Eintrag -- sein Klick wählt den Eintrag nicht. */
function knopf(text, title, tun, klasse = '') {
  return el(`button.knopf.knopf-zart${klasse}`, {
    text, title,
    on: {
      click: (ereignis) => {
        ereignis.stopPropagation();
        tun();
      },
    },
  });
}

// ===========================================================================

/**
 * Zeichnet die linke Tafel: die Knöpfe der Apps in `knoepfe`, die Listen der
 * gewählten darunter in `behaelter` -- beim Material eine je Art.
 */
export function baumZeichnen(knoepfe, behaelter) {
  const p = zustand.projekt;
  if (!p) {
    ersetzen(knoepfe);
    return ersetzen(behaelter, el('div.leer', { text: 'Projekt wird geladen …' }));
  }
  const gewaehlt = appVon(gewaehlteApp());
  ersetzen(knoepfe, el('div.kacheln', {}, APPS.map((a) => appKnopf(a, p, a === gewaehlt))));
  return ersetzen(behaelter, ...gewaehlt.gruppen(p).map((g) => liste(gewaehlt, g)));
}
