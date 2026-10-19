/**
 * baum.js -- Linke Tafel: die Apps und die Bestandteile des Projekts.
 *
 * Oben je App ein Knopf mit Zeichen, wie die Kapitel einer Platte in der
 * Mitte (Benutzer, 2026-10-15): Materialien, Stahlbeton-Platten,
 * Querschnittsanalyse, 2D Balkensysteme, Grundbruch, Python. Darunter steht
 * die Liste der gewählten App, mit «+» zum Anlegen -- bei den Materialien je
 * eine für Beton und Betonstahl. Darüber, zuoberst in der Tafel, der Name des
 * Projekts (index.html).
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
import { appWaehlen, gewaehlteApp, waehlen, zustand } from './zustand.js';

// ===========================================================================
// Bausteine
// ===========================================================================

/**
 * Ein Knopf je App. Das Zeichen ist blau, sobald es darin etwas gibt -- wie
 * bei den Kapiteln einer Platte, die etwas rechnen; die gewählte App trägt
 * dazu Grund und Rand der Auswahl. Auf dem Knopf steht nur die Zahl ihrer
 * Einträge, «1 Querschnittsanalyse» passte nicht hinein.
 */
function appKnopf(a, p, gewaehlt) {
  const eintraege = p[a.liste] || [];
  return el('button.kachel.app-kachel', {
    type: 'button', 'aria-pressed': String(gewaehlt),
    class: `${gewaehlt ? 'ist-gewaehlt' : ''} ${eintraege.length ? 'ist-an' : ''}`,
    title: a.knopf.replace(/\u00AD/g, ''),
    on: { click: () => appWaehlen(a.app, eintraege) },
  }, [
    sinnbild(a.zeichen),
    el('span.kachel-name', { text: a.knopf }),
    el('span.kachel-stand', { text: String(eintraege.length) }),
  ]);
}

/** Eine Liste unter den Knöpfen: Titel, Zahl und «+», darunter die Einträge. */
function liste(a, { titel, eintraege, plus, leer }) {
  return el('div.baum-gruppe', {}, [
    el('div.baum-kopf', {}, [
      el('span.titel', { text: titel }),
      el('span.zaehler', { text: String(eintraege.length) }),
      el('span.werkzeuge', {}, [el('button.knopf.knopf-zart', {
        text: '+', title: plus.titel, on: { click: plus.tun },
      })]),
    ]),
    el('div.baum-koerper', {},
      eintraege.length ? eintraege.map((e) => eintrag(a, e)) : [leerzeile(leer)]),
  ]);
}

/** Ein Eintrag: sein Name, beim Material ob es eine Normsorte ist, rechts sein Kurztext. */
function eintrag(a, e) {
  const aktiv = zustand.auswahl?.art === a.app && zustand.auswahl.kennung === e.kennung;
  return el('div.baum-eintrag', {
    class: aktiv ? 'ist-aktiv' : '',
    on: { click: () => waehlen({ art: a.app, kennung: e.kennung }) },
  }, [
    el('span.name', { text: a.name(e), title: a.name(e) }),
    a.marke?.(e) ?? null,
    el('span.art', { text: a.kurztext(e) }),
    el('button.knopf.knopf-zart', {
      text: '⧉', title: 'Kopieren',
      on: {
        click: (ereignis) => {
          ereignis.stopPropagation();
          a.kopieren(e);
        },
      },
    }),
    el('button.knopf.knopf-zart.knopf-gefahr', {
      text: '×', title: 'Entfernen',
      on: {
        click: (ereignis) => {
          ereignis.stopPropagation();
          a.loeschen(e);
        },
      },
    }),
  ]);
}

function leerzeile(text) {
  return el('div', {
    text, style: { padding: '5px 10px', color: 'var(--schrift-zart)', fontSize: '12.5px' },
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
