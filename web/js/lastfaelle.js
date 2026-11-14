/**
 * lastfaelle.js -- Lastfälle und Kombinationen, für Balkensystem und Decke dieselben.
 *
 * Die Fenster «Lastfälle» und «Lastkombinationen» (`lastenKapitel`), und
 * was ein Zeichenfenster mit ihnen tut: welchen Lastfall es zeigt und in
 * welchen es zeichnet (`aktiverLastfall`) -- zu wählen neben den Werkzeugen
 * (`lastfallLeiste`) und im Fenster einer Last (`lastfallZeile`). Dazu die
 * Zeilen der Diagramme, je ein Fall und eine Grösse (`diagrammzeilen`), und
 * wie ein Fall heisst (`fallname`). Was beim Rechnen gilt -- verschiedene
 * Namen, ein Eigengewicht --, prüft der Kern
 * (opencivil/projekt/aufbau/faelle.py). Bis 2026-11-13 stand das im
 * Balkensystem allein.
 *
 * Ein Zeichenfenster gibt dazu seinen Zustand `ansicht`: die Kennung seines
 * Bauteils und den gewählten Lastfall (`{kennung, lastfall}`) --
 * Ansichtssache, nicht Teil des Projekts.
 */

import { wahlSchalter } from './bausteine.js';
import { cadZeile, mitVar } from './cad_app.js';
import {
  auswahl, el, melden, zahlfeld,
} from './dom.js';
import { zeilenstand } from './kapitel.js';
import { anfuegenKnopf } from './nachweise.js';
import {
  aendern, ausVorlage, eintragAendern, eintragVon, naechsteKennung, naechsterName,
} from './zustand.js';

const lastenText = (n) => `${n} ${n === 1 ? 'Last' : 'Lasten'}`;

// ===========================================================================
// Die Fenster
// ===========================================================================

/**
 * Je Lastfall sein Name und wie viele Lasten er hat. `lastenVon(eintrag,
 * lastfall)` zählt sie, `eigengewicht` sagt mit `{text, titel}`, wie das
 * Eigengewicht von selbst kommt.
 */
function lastfaelleInhalt(eintrag, { lastenVon, eigengewicht }) {
  const aendern = (veraenderer) => eintragAendern(eintrag.kennung, veraenderer);
  // Das Eigengewicht kommt von selbst und bleibt: es lässt sich umbenennen,
  // nicht löschen (Benutzer, 2026-10-23).
  const fall = (lf, i) => {
    const n = lastenVon(eintrag, lf.kennung);
    return el('div.bs-fall', {}, [
      el('input', {
        type: 'text', value: lf.name, title: 'Name des Lastfalls -- so steht er im Bericht',
        on: { change: (e) => aendern((s) => { s.lastfaelle[i].name = e.target.value; }) },
      }),
      el('span.bs-fall-zahl', {
        text: lf.eigengewicht ? `von selbst, ${eigengewicht.text}${n ? ` · dazu ${lastenText(n)}` : ''}`
          : lastenText(n),
        title: lf.eigengewicht ? eigengewicht.titel : '',
      }),
      lf.eigengewicht ? el('span') : el('button.weg', {
        type: 'button', text: '×', title: 'Lastfall löschen',
        on: {
          click: () => {
            if (n) {
              melden(`«${lf.name}» hat noch ${lastenText(n)} -- zuerst diese löschen.`, true);
              return;
            }
            aendern((s) => {
              s.lastfaelle.splice(i, 1);
              for (const k of s.kombinationen) delete k.faktoren[lf.kennung];
            });
          },
        },
      }),
    ]);
  };
  const neuerFall = () => aendern((s) => {
    s.lastfaelle.push({ kennung: naechsteKennung(s.lastfaelle, 'LF'), name: naechsterName('Lastfall', s.lastfaelle) });
  });
  return [
    ...eintrag.lastfaelle.map(fall),
    el('button.knopf.knopf-klein', { type: 'button', text: '+ Lastfall', on: { click: neuerFall } }),
  ];
}

/** Je Kombination eine Zeile: je Lastfall ein Beiwert, von Hand. */
function kombinationenInhalt(eintrag) {
  const aendern = (veraenderer) => eintragAendern(eintrag.kennung, veraenderer);
  const kombination = (k, i) => el('tr', {}, [
    el('td', {}, [el('input', {
      type: 'text', value: k.name,
      on: { change: (e) => aendern((s) => { s.kombinationen[i].name = e.target.value; }) },
    })]),
    ...eintrag.lastfaelle.map((lf) => el('td', {}, [zahlfeld({
      wert: k.faktoren[lf.kennung] ?? 0, schritt: 0.05,
      titel: `Beiwert für «${lf.name}» -- 0: zählt nicht`,
      beiAenderung: (w) => aendern((s) => { s.kombinationen[i].faktoren[lf.kennung] = w; }),
    })])),
    el('td', {}, [el('button.weg', {
      type: 'button', text: '×', title: 'Kombination löschen',
      on: { click: () => aendern((s) => { s.kombinationen.splice(i, 1); }) },
    })]),
  ]);
  const neueKombination = () => aendern((s) => {
    s.kombinationen.push({
      kennung: naechsteKennung(s.kombinationen, 'LK'),
      name: naechsterName('Kombination', s.kombinationen),
      faktoren: Object.fromEntries(s.lastfaelle.map((lf) => [lf.kennung, 1.0])),
    });
  });
  if (!eintrag.lastfaelle.length) return [el('p.bs-leer', { text: 'Zuerst einen Lastfall anlegen.' })];
  return [
    eintrag.kombinationen.length ? el('div.tabelle-huelle', {}, [el('table.bs-kombinationen', {}, [
      el('thead', {}, [el('tr', {}, [
        el('th', { text: 'Kombination' }),
        ...eintrag.lastfaelle.map((lf) => el('th', { text: lf.name })),
        el('th'),
      ])]),
      el('tbody', {}, eintrag.kombinationen.map(kombination)),
    ])]) : el('p.bs-leer', { text: 'Noch keine Kombination.' }),
    el('button.knopf.knopf-klein', { type: 'button', text: '+ Kombination', on: { click: neueKombination } }),
  ];
}

/**
 * Die Gruppe «Lasten» unter den Eingaben eines Bauteils: die Knöpfe
 * Lastfälle und Lastkombinationen (kapitel.js). `optionen` wie bei
 * `lastfaelleInhalt`.
 */
export function lastenKapitel(optionen) {
  return {
    titel: 'Lasten',
    kapitel: [
      {
        schluessel: 'lastfaelle', name: 'Lastfälle', titel: 'Lastfälle',
        inhalt: (e) => lastfaelleInhalt(e, optionen),
        stand: (e) => zeilenstand(e.lastfaelle, 'Lastfall', 'Lastfälle', 'kein Lastfall'),
      },
      {
        schluessel: 'kombinationen', name: 'Lastkombi­nationen', titel: 'Lastkombinationen',
        inhalt: kombinationenInhalt,
        stand: (e) => zeilenstand(e.kombinationen, 'Kombination', 'Kombinationen', 'keine'),
      },
    ],
  };
}

// ===========================================================================
// Im Zeichenfenster
// ===========================================================================

/**
 * Der Lastfall, dessen Lasten das Fenster zeigt und bearbeitet -- der
 * gewählte, solange es ihn gibt, sonst der mit dem Eigengewicht, sonst der
 * erste. '' heisst keiner: dann zeigt es keine Lasten.
 */
export function aktiverLastfall(ansicht) {
  const faelle = eintragVon(ansicht.kennung)?.lastfaelle || [];
  if (ansicht.lastfall === '') return null;
  if (faelle.some((lf) => lf.kennung === ansicht.lastfall)) return ansicht.lastfall;
  // Zuerst das Eigengewicht (Benutzer, 2026-10-24).
  return (faelle.find((lf) => lf.eigengewicht) || faelle[0])?.kennung || null;
}

/** Zeigt im Fenster die Lasten dieses Lastfalls -- '' heisst keine. */
export function lastfallWaehlen(a, ansicht, lastfall) {
  ansicht.lastfall = lastfall;
  a.neuZeichnen();
  aendern({}, 'zeichnung');
}

/** Der Lastfall für eine neue Last -- ohne einen sagt eine Meldung, wo er zu wählen ist. */
export function lastfallFuerNeue(ansicht) {
  const lf = aktiverLastfall(ansicht);
  if (!lf) melden('Für eine Last zuerst oben in der Leiste einen Lastfall wählen.', true);
  return lf;
}

/**
 * Die Wahl des Lastfalls in der Leiste des Fensters (Benutzer, 2026-10-24):
 * dessen Lasten zeigt und bearbeitet die Zeichnung -- oder «– kein
 * Lastfall –». Neu bei jedem Neubau der Tafel, damit sie jeden Lastfall
 * kennt. Eine Wahl aus dem Projekt, darum eine Liste.
 */
export function lastfallLeiste(a, ansicht, huelle) {
  if (!huelle) return;
  const faelle = eintragVon(ansicht.kennung)?.lastfaelle || [];
  huelle.replaceChildren(auswahl({
    werte: [{ wert: '', beschriftung: '– kein Lastfall –' },
      ...faelle.map((x) => ({ wert: x.kennung, beschriftung: x.name }))],
    gewaehlt: aktiverLastfall(ansicht) || '',
    titel: 'Dessen Lasten zeigt und bearbeitet die Zeichnung',
    beiAenderung: (w) => lastfallWaehlen(a, ansicht, w),
  }));
}

/**
 * Der Lastfall gewählter Lasten im schwebenden Fenster -- mit «Var», wenn
 * sie sich unterscheiden. `eintrag` ist das Bauteil, `setzen(lastfall)`
 * schreibt.
 */
export function lastfallZeile(eintrag, gewaehlt, setzen, titel) {
  if (!eintrag.lastfaelle.length) {
    return el('p.cad-hinweis-klein', { text: 'Für Lasten zuerst unter «Lastfälle» einen Lastfall anlegen.' });
  }
  return cadZeile('Lastfall', auswahl({
    werte: mitVar(eintrag.lastfaelle.map((x) => ({ wert: x.kennung, beschriftung: x.name })), gewaehlt),
    gewaehlt, titel, beiAenderung: setzen,
  }));
}

// ===========================================================================
// Die Diagramme
// ===========================================================================

/** Der Name eines Falls -- Lastfall oder Kombination -- aus seiner Kennung; `null`, wenn es ihn nicht gibt. */
export function fallname(eintrag, kennung) {
  return [...eintrag.lastfaelle, ...eintrag.kombinationen].find((f) => f.kennung === kennung)?.name ?? null;
}

/**
 * Welche Diagramme rechts stehen -- wie in der Spannung-Dehnung-Analyse: je
 * Zeile ein Fall, Lastfall oder Kombination, und was das Diagramm von ihm
 * zeigt (Benutzer, 2026-10-23), im Balkensystem wie in der Decke. Gerechnet
 * wird damit nichts, das Bauteil rechnet jeden Fall. Ein Fall, den es nicht
 * mehr gibt, steht als «– Fall wählen –» da. `groessen` sind die Stellungen
 * des Schalters aus dem Katalog, `vorlage` die Art einer neuen Zeile.
 */
export function diagrammzeilen(eintrag, { groessen, vorlage }) {
  const aendern = (veraenderer) => eintragAendern(eintrag.kennung, veraenderer);
  const faelle = [
    ...eintrag.lastfaelle.map((lf) => ({ wert: lf.kennung, beschriftung: lf.name })),
    ...eintrag.kombinationen.map((k) => ({ wert: k.kennung, beschriftung: `${k.name} (Kombination)` })),
  ];
  const zeile = (d, i) => el('div.bs-diagrammzeile', {}, [
    el('div.bs-diagrammzeile-kopf', {}, [
      auswahl({
        werte: faelle.some((f) => f.wert === d.fall) ? faelle
          : [{ wert: d.fall, beschriftung: '– Fall wählen –' }, ...faelle],
        gewaehlt: d.fall,
        titel: 'Welcher Lastfall oder welche Kombination',
        beiAenderung: (w) => aendern((s) => { s.diagramme[i].fall = w; }),
      }),
      el('button.weg', {
        type: 'button', text: '×', title: 'Diagramm löschen',
        on: { click: () => aendern((s) => { s.diagramme.splice(i, 1); }) },
      }),
    ]),
    wahlSchalter({
      werte: groessen.map((g) => ({ wert: g.wert, beschriftung: g.beschriftung, titel: g.titel })),
      gewaehlt: d.groesse, titel: 'Was das Diagramm zeigt',
      setzen: (w) => aendern((s) => { s.diagramme[i].groesse = w; }),
    }),
  ]);
  return [
    ...(eintrag.diagramme.length ? eintrag.diagramme.map(zeile)
      : [el('div.leer', { text: 'Noch kein Diagramm.' })]),
    anfuegenKnopf('Diagramm', () => aendern((s) => {
      s.diagramme.push(ausVorlage(vorlage, {
        fall: s.kombinationen[0]?.kennung || s.lastfaelle[0]?.kennung || '',
      }));
    })),
  ];
}
