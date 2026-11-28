/**
 * lastfaelle.js -- Lastfälle und Kombinationen, für Balkensystem, Decke und Wand dieselben.
 *
 * Die Fenster «Lastfälle» und «Lastkombinationen» (`lastenKapitel`), und
 * was ein Zeichenfenster mit ihnen tut: welchen Lastfall es zeigt und in
 * welchen es zeichnet (`aktiverLastfall`) -- zu wählen neben den Werkzeugen
 * (`lastfallLeiste`) und im Fenster einer Last (`lastfallZeile`) --, und die
 * Punktlast an einem Knoten, die man in dessen Fenster setzt
 * (`punktlastFelder`). Dazu die Zeilen der Diagramme, je ein Fall und eine
 * Grösse (`diagrammzeilen`), und wie ein Fall heisst (`fallname`). Was beim
 * Rechnen gilt -- verschiedene Namen, ein Eigengewicht --, prüft der Kern
 * (opencivil/projekt/aufbau/faelle.py). Bis 2026-11-13 stand das im
 * Balkensystem allein, die Punktlast am Knoten bis 2026-11-28 in der Decke.
 *
 * Ein Zeichenfenster gibt dazu seinen Zustand `ansicht`: die Kennung seines
 * Bauteils und den gewählten Lastfall (`{kennung, lastfall}`) --
 * Ansichtssache, nicht Teil des Projekts --, für die Punktlast auch, was
 * sein Werkzeug vorgibt (`vorgaben.punktlasten`) und womit die Kennungen
 * beginnen (`vorsilben.punktlasten`).
 */

import {
  gemeinsam, mitVar, namensfeld, wahlSchalter,
} from './bausteine.js';
import { jaNein, meldungszeilen, zugleich } from './cad_app.js';
import { cadZeile, schalterzeile } from './cad_palette.js';
import {
  auswahl, el, melden, zahlfeld,
} from './dom.js';
import { anfuegenKnopf } from './faelle.js';
import { zeilenstand } from './kapitel.js';
import {
  ausVorlage, eintragAendern, eintragVon, mitteAendern, naechsterName, neueKennung,
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
      namensfeld({
        wert: lf.name, titel: 'Name des Lastfalls – so steht er im Bericht',
        setzen: (name) => aendern((s) => { s.lastfaelle[i].name = name; }),
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
              melden(`«${lf.name}» hat noch ${lastenText(n)} – zuerst diese löschen.`, true);
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
    s.lastfaelle.push({ kennung: neueKennung(s, 'LF', s.lastfaelle), name: naechsterName('Lastfall', s.lastfaelle) });
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
    el('td', {}, [namensfeld({
      wert: k.name, setzen: (name) => aendern((s) => { s.kombinationen[i].name = name; }),
    })]),
    ...eintrag.lastfaelle.map((lf) => el('td', {}, [zahlfeld({
      wert: k.faktoren[lf.kennung] ?? 0, schritt: 0.05,
      titel: `Beiwert für «${lf.name}» – 0: zählt nicht`,
      beiAenderung: (w) => aendern((s) => { s.kombinationen[i].faktoren[lf.kennung] = w; }),
    })])),
    el('td', {}, [el('button.weg', {
      type: 'button', text: '×', title: 'Kombination löschen',
      on: { click: () => aendern((s) => { s.kombinationen.splice(i, 1); }) },
    })]),
  ]);
  const neueKombination = () => aendern((s) => {
    s.kombinationen.push({
      kennung: neueKennung(s, 'LK', s.kombinationen),
      name: naechsterName('Kombination', s.kombinationen),
      faktoren: Object.fromEntries(s.lastfaelle.map((lf) => [lf.kennung, 1.0])),
    });
  });
  if (!eintrag.lastfaelle.length) return [el('p.leer-zeile', { text: 'Zuerst einen Lastfall anlegen.' })];
  return [
    eintrag.kombinationen.length ? el('div.tabelle-huelle', {}, [el('table.bs-kombinationen', {}, [
      el('thead', {}, [el('tr', {}, [
        el('th', { text: 'Kombination' }),
        ...eintrag.lastfaelle.map((lf) => el('th', { text: lf.name })),
        el('th'),
      ])]),
      el('tbody', {}, eintrag.kombinationen.map(kombination)),
    ])]) : el('p.leer-zeile', { text: 'Noch keine Kombination.' }),
    el('button.knopf.knopf-klein', { type: 'button', text: '+ Kombination', on: { click: neueKombination } }),
  ];
}

/**
 * Die Gruppe «Lasten» unter den Eingaben eines Bauteils: die Knöpfe
 * Lastfälle und Lastkombinationen (kapitel.js). `optionen` wie bei
 * `lastfaelleInhalt`; `dazu` sind Kapitel, die ein Bauteil zwischen beiden
 * mehr hat -- die Querlasten der Wand, die man nicht zeichnet.
 */
export function lastenKapitel({ dazu = [], ...optionen }) {
  return {
    titel: 'Lasten',
    kapitel: [
      {
        schluessel: 'lastfaelle', name: 'Lastfälle', titel: 'Lastfälle',
        inhalt: (e) => lastfaelleInhalt(e, optionen),
        stand: (e) => zeilenstand(e.lastfaelle, 'Lastfall', 'Lastfälle', 'kein Lastfall'),
      },
      ...dazu,
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
  mitteAendern();
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

/** Was dort steht, wo Lasten hingehören, das Bauteil aber noch keinen Lastfall hat. */
export function ohneLastfall() {
  return el('p.cad-hinweis-klein', { text: 'Für Lasten zuerst unter «Lastfälle» einen Lastfall anlegen.' });
}

/**
 * Der Lastfall gewählter Lasten in der Seitenleiste -- mit «Var», wenn
 * sie sich unterscheiden. `eintrag` ist das Bauteil, `setzen(lastfall)`
 * schreibt.
 */
export function lastfallZeile(eintrag, gewaehlt, setzen, titel) {
  if (!eintrag.lastfaelle.length) return ohneLastfall();
  return cadZeile('Lastfall', auswahl({
    werte: mitVar(eintrag.lastfaelle.map((x) => ({ wert: x.kennung, beschriftung: x.name })), gewaehlt),
    gewaehlt, titel, beiAenderung: setzen,
  }));
}

/** Der Lastfall, den das Fenster zeigt, als Eintrag -- oder null. */
export function gezeigterLastfall(ansicht) {
  const lf = aktiverLastfall(ansicht);
  return eintragVon(ansicht.kennung)?.lastfaelle.find((x) => x.kennung === lf) || null;
}

/**
 * In welchen Lastfall die Lasten gehen -- eine Zeile über ihren Feldern --,
 * oder was fehlt: keiner gewählt, oder es gibt noch keinen. Ohne Lastfall
 * fehlten in der Decke «q überall» und die Punktlast bis 2026-11-19 ohne ein Wort.
 */
export function lastfallText(ansicht) {
  const lf = gezeigterLastfall(ansicht);
  if (lf) return el('p.cad-info', { text: `Lastfall «${lf.name}»` });
  return eintragVon(ansicht.kennung)?.lastfaelle.length
    ? el('p.cad-hinweis-klein', { text: 'Kein Lastfall gewählt – oben in der Leiste einen wählen.' })
    : ohneLastfall();
}

// ===========================================================================
// Die Punktlast an einem Knoten
// ===========================================================================

/**
 * Setzt an einen Knoten eine Punktlast nach der Vorgabe des Werkzeugs, im
 * Lastfall `lastfall` -- oder nimmt die dieses Lastfalls weg. Je Knoten und
 * Lastfall höchstens eine.
 */
export function punktlastSetzen(a, ansicht, z, knoten, an, lastfall) {
  const hier = (e) => e.knoten === knoten && e.lastfall === lastfall;
  if (!an) z.punktlasten = z.punktlasten.filter((e) => !hier(e));
  else if (!z.punktlasten.some(hier)) {
    z.punktlasten.push({
      ...structuredClone(ansicht.vorgaben.punktlasten),
      kennung: a.modell.naechsteKennung(z, ansicht.vorsilben.punktlasten), knoten, lastfall,
    });
  }
}

/**
 * Die Punktlast der gewählten Knoten im gezeigten Lastfall, im Fenster der
 * Knoten: ein Schalter, dann -- hat jeder gewählte Knoten eine -- ihre Felder,
 * `felder(wert, setzen)`. Man wählt sie nicht für sich, wie eine Stütze in
 * der Decke oder ein Lager im Balkensystem.
 */
export function punktlastFelder(a, ansicht, z, knoten, felder) {
  const lf = gezeigterLastfall(ansicht);
  if (!lf) return [lastfallText(ansicht)];
  const lasten = knoten.map((k) => z.punktlasten.find((e) => e.knoten === k && e.lastfall === lf.kennung) || null);
  const zeilen = [lastfallText(ansicht), schalterzeile('Punktlast', jaNein(gemeinsam(lasten.map(Boolean)), (w) => a.aendern((zz) => {
    for (const k of knoten) punktlastSetzen(a, ansicht, zz, k, w, lf.kennung);
  }), `Eine Punktlast an diesem Knoten im Lastfall «${lf.name}»`))];
  if (lasten.some((e) => !e)) return zeilen;
  const kennungen = lasten.map((e) => e.kennung);
  const { wert, setzen } = zugleich(a, z, 'punktlasten', kennungen);
  return [...zeilen, ...felder(wert, setzen), ...meldungszeilen(a, kennungen)];
}

// ===========================================================================
// Die Diagramme
// ===========================================================================

/** Der Name eines Falls -- Lastfall oder Kombination -- aus seiner Kennung; `null`, wenn es ihn nicht gibt. */
export function fallname(eintrag, kennung) {
  return [...eintrag.lastfaelle, ...eintrag.kombinationen].find((f) => f.kennung === kennung)?.name ?? null;
}

/**
 * Was eine Diagrammzeile ohne ihren Fall sagt: er ist gelöscht -- oder es
 * ist keiner gewählt. Eine Kennung kommt nie wieder (`neueKennung`): die
 * Zeile zeigt ins Leere, bis man einen anderen wählt, und sagt es am Ort
 * (Benutzer, 2026-11-19).
 */
export function ohneFall(zeile) {
  return zeile.fall ? 'Der gewählte Fall ist gelöscht.' : 'Kein Fall gewählt.';
}

/**
 * Welche Diagramme rechts stehen -- wie in der Spannung-Dehnung-Analyse: je
 * Zeile ein Fall, Lastfall oder Kombination, und was das Diagramm von ihm
 * zeigt (Benutzer, 2026-10-23), im Balkensystem wie in der Decke. Gerechnet
 * wird damit nichts, das Bauteil rechnet jeden Fall. Ein Fall, den es nicht
 * mehr gibt, steht als «– gelöscht, einen Fall wählen –» da. `groessen(zeile)` gibt die
 * Stellungen des Schalters aus dem Katalog -- je Zeile, denn in der Decke
 * hat ein Träger andere als die Platte --, `vorlage` die Art einer neuen
 * Zeile.
 * `zusatz(zeile, aendern)` gibt, was ein Bauteil unter dem Fall mehr
 * wählen lässt -- die Decke, wo das Bild hinsieht --, oder null.
 */
export function diagrammzeilen(eintrag, { groessen, vorlage, zusatz = () => null }) {
  const aendern = (veraenderer) => eintragAendern(eintrag.kennung, veraenderer);
  const faelle = [
    ...eintrag.lastfaelle.map((lf) => ({ wert: lf.kennung, beschriftung: lf.name })),
    ...eintrag.kombinationen.map((k) => ({ wert: k.kennung, beschriftung: `${k.name} (Kombination)` })),
  ];
  const zeile = (d, i) => el('div.bs-diagrammzeile', {}, [
    el('div.bs-diagrammzeile-kopf', {}, [
      auswahl({
        werte: faelle.some((f) => f.wert === d.fall) ? faelle
          : [{ wert: d.fall, beschriftung: d.fall ? '– gelöscht, einen Fall wählen –' : '– Fall wählen –' },
            ...faelle],
        gewaehlt: d.fall,
        titel: 'Welcher Lastfall oder welche Kombination',
        beiAenderung: (w) => aendern((s) => { s.diagramme[i].fall = w; }),
      }),
      el('button.weg', {
        type: 'button', text: '×', title: 'Diagramm löschen',
        on: { click: () => aendern((s) => { s.diagramme.splice(i, 1); }) },
      }),
    ]),
    zusatz(d, (veraenderer) => aendern((s) => veraenderer(s.diagramme[i]))),
    wahlSchalter({
      werte: groessen(d).map((g) => ({ wert: g.wert, beschriftung: g.beschriftung, titel: g.titel })),
      gewaehlt: d.groesse, titel: 'Was das Diagramm zeigt',
      setzen: (w) => aendern((s) => { s.diagramme[i].groesse = w; }),
      klasse: '.ist-umbruch',
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
