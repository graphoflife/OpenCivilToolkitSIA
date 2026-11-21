/**
 * cad_app.js -- was jede App mit Zeichenfenster gleich hat.
 *
 * Ein Zeichenfenster gehört zu einem Eintrag des Projekts: es liest und
 * schreibt ihn über seine Kennung, gilt nur im Projekt, in dem es entstand,
 * und wer die Kennung neu vergibt, findet ein leeres. Das steht hier einmal
 * (`cadApp`); die Apps -- Querschnittsanalyse (qa_zeichnung.js),
 * Balkensystem (bs_zeichnung.js), Decke (dk_zeichnung.js), Durchstanzen
 * (ds_zeichnung.js) -- geben nur dazu, was sie selbst wissen. Ebenso
 * einmal:
 *
 *   die Antwort des Kerns   gefragt einmal je Fassung des Projekts, gültig
 *                           nur zu ihr (`frischeAntwort`), seine Meldungen
 *                           je Teil der Zeichnung (`meldungenJe`) -- in
 *                           jeder App ausser dem Durchstanzen, das seinen
 *                           Grundriss aus der letzten Lösung liest
 *   unter der Zeichnung     die Meldungen und die Liste der Teile: je Art
 *                           eine Gruppe, je Teil eine Zeile; markiert, was
 *                           gewählt ist
 *   das schwebende Fenster  die Auswahl nach Listen (`auswahlEigenschaften`),
 *                           Felder für mehrere zugleich («Var»), die Lage
 *                           der Punkte, die Länge einer Linie und die
 *                           Meldungen zu den gewählten
 *
 * Was ein Klick unter der Zeichnung wählt, sagt `waehlbarVon` -- dieselbe
 * Regel wie in der Zeichnung: ein Lager, eine Stütze wählt man über ihren
 * Knoten. Die Zeilen des schwebenden Fensters -- mit Feld und Einheit, mit
 * Schalter -- stehen bei ihm (cad_palette.js).
 *
 * Bis 2026-11-10 stand das Fenster dreimal da, je mit eigenem Leser des
 * Eintrags und eigenem Vergessen; bis 2026-11-20 die Antwort des Kerns, die
 * Liste und das schwebende Fenster.
 */

import {
  VAR, gemeinsam, klappgruppe, mitVar, wahlSchalter,
} from './bausteine.js';
import { zahlText } from './cad_ansicht.js';
import { imSpiel } from './cad_auswahl.js';
import {
  cadBereich, cadFenster, cadVergessen, cadWaehlen,
} from './cad_fenster.js';
import { abstand, auswahlTeil } from './cad_modell.js';
import { cadZeile } from './cad_palette.js';
import { el, svgEl, zahlfeld } from './dom.js';
import {
  beimVergessen, eintragAendern, eintragVon, mitteAendern, zustand,
} from './zustand.js';

/**
 * Die Zeichenfenster einer App. `praefix` trennt sie von denen anderer
 * Apps, `teile(kennung)` liefert, was der Adapter darüber hinaus weiss --
 * Einstellung, Arten, Zeichnen, schwebendes Fenster (cad_fenster.js) und
 * was sie den Kern fragt, wenn sie fragt (`fragen`, siehe `kernFragen`).
 * `einrichten(a)`
 * hängt an das Fenster, was die App an ihm braucht. Wer eine Kennung
 * vergisst (`ansichtVergessen`), vergisst auch ihr Fenster.
 */
export function cadApp(praefix, teile, einrichten = () => {}) {
  const schluessel = (kennung) => `${praefix}:${kennung}`;
  beimVergessen((kennung) => cadVergessen(schluessel(kennung)));
  return (kennung) => {
    const a = cadFenster(schluessel(kennung), () => {
      const projekt = zustand.projekt;
      return {
        gilt: () => zustand.projekt === projekt,
        zeichnung: () => eintragVon(kennung),
        schreiben: (veraenderer) => eintragAendern(kennung, veraenderer),
        tafelNeu: () => mitteAendern(),
        gezeichnet: listeMarkieren,
        geaendert: kernFragen,
        kern: { gefragt: null, antwort: null, fehler: null },
        aufgeklappt: new Set(),
        ...teile(kennung),
      };
    });
    einrichten(a);
    return a;
  };
}

// ===========================================================================
// Die Antwort des Kerns
// ===========================================================================

/**
 * Fragt den Kern nach der Zeichnung, wenn sie sich seit der letzten Frage
 * geändert hat -- einmal je Fassung des Projekts: die Antwort hängt auch an
 * Materialien und Querschnitten, die sich anderswo ändern. Kommt eine
 * Antwort zu spät -- es wurde inzwischen wieder gefragt --, gilt sie nicht.
 * Was gefragt wird, sagt der Adapter (`fragen`), was von der Antwort bleibt
 * (`nehmen`) und was danach ausser Zeichnung und Liste neu soll
 * (`beantwortet`). Scheitert die Frage, steht ihr Grund unter der Zeichnung
 * (`kernfehler`), und keine alte Antwort bleibt stehen.
 */
function kernFragen(a) {
  const {
    kern: k, fragen, nehmen = (_, antwort) => antwort, beantwortet = () => {},
  } = a.adapter;
  if (!fragen || !a.adapter.zeichnung()) return;
  const jetzt = zustand.fassung;
  if (k.gefragt === jetzt) return;
  k.gefragt = jetzt;
  fragen(a).then((antwort) => {
    if (k.gefragt !== jetzt) return;
    k.antwort = { ...nehmen(a, antwort), fassung: jetzt };
    k.fehler = null;
  }, (fehler) => {
    if (k.gefragt !== jetzt) return;
    k.antwort = null;
    k.fehler = { text: fehler.message, fassung: jetzt };
  }).then(() => {
    if (k.gefragt !== jetzt) return;
    a.neuZeichnen();
    listeZeichnen(a);
    beantwortet(a);
  });
}

/**
 * Die Antwort des Kerns, wenn sie zur Zeichnung gehört, wie sie jetzt ist --
 * sonst null, und das Fenster fragt. So kommt die Antwort auch, wo die
 * Zeichnung nicht zu sehen ist: die Materialien einer Querschnittsanalyse
 * für einen Stab, der aus ihr kommt. Die letzte Antwort, auch eine, die
 * nicht mehr passt, steht in `a.adapter.kern.antwort` -- für ein Bild, das
 * blass stehen bleibt, bis die nächste da ist.
 */
export function frischeAntwort(a) {
  const { antwort } = a.adapter.kern;
  if (antwort?.fassung === zustand.fassung) return antwort;
  kernFragen(a);
  return null;
}

/** Warum die Antwort zur jetzigen Zeichnung ausbleibt -- leer, solange nichts schiefging. */
export function kernfehler(a) {
  const { fehler } = a.adapter.kern;
  return fehler?.fassung === zustand.fassung ? `Die Zeichnung ist nicht geprüft: ${fehler.text}` : '';
}

/**
 * Was der Kern zur Zeichnung meldet, solange seine Antwort zu ihr gehört.
 * Was dazugehört, darf die App sagen (`meldungen` des Adapters): die Decke
 * nimmt die des Lastfalls dazu, den das Fenster zeigt.
 */
export function kernmeldungen(a) {
  const antwort = frischeAntwort(a);
  if (!antwort) return [];
  return a.adapter.meldungen?.(a, antwort) ?? antwort.meldungen ?? [];
}

/**
 * Was der Kern je Teil der Zeichnung meldet: `fehler(k)`, ob an ihm etwas
 * falsch ist -- das steht rot --, und `texte(k)` alle seine Sätze, für den
 * Titel. Was nur fehlt, färbt nicht.
 */
export function meldungenJe(a) {
  const je = new Map();
  for (const m of kernmeldungen(a)) {
    for (const k of m.elemente) je.set(k, [...(je.get(k) || []), m]);
  }
  return {
    fehler: (k) => (je.get(k) || []).some((m) => m.fehler),
    texte: (k) => (je.get(k) || []).map((m) => m.text),
  };
}

/** Die Meldungen zu diesen Teilen, im schwebenden Fenster: rot, was falsch ist, grau, was nur fehlt. */
export function meldungszeilen(a, kennungen) {
  return kernmeldungen(a).filter((m) => m.elemente.some((k) => kennungen.includes(k)))
    .map((m) => el(m.fehler ? 'p.cad-meldung' : 'p.cad-hinweis-klein', { text: m.text }));
}

// ===========================================================================
// Unter der Zeichnung
// ===========================================================================

/**
 * Das Fenster mit der Liste darunter: `bauen(a)` liefert ihren Inhalt.
 * Gebaut wird sie hier, wenn die Tafel neu entsteht -- dann fragt das
 * Fenster auch den Kern, wenn sich nicht die Zeichnung geändert hat, aber
 * ein Material oder Querschnitt --, und mit `listeZeichnen`, wenn der Kern
 * antwortet; was im Fenster gewählt ist, markiert sie ohne Neubau
 * (`listeMarkieren`).
 */
export function cadBereichMitListe(a, bauen) {
  a.liste = { knoten: el('div.qa-uebersicht-huelle'), bauen };
  const bereich = cadBereich(a, [a.liste.knoten]);
  kernFragen(a);
  listeZeichnen(a);
  return bereich;
}

export function listeZeichnen(a) {
  if (a.liste) a.liste.knoten.replaceChildren(...a.liste.bauen(a).filter(Boolean));
}

/** Markiert in der Liste, was im Fenster gewählt ist -- ohne sie neu zu bauen. */
export function listeMarkieren(a) {
  const spiel = imSpiel(a);
  for (const z of a.liste?.knoten.querySelectorAll('[data-kennung]') || []) {
    z.classList.toggle('ist-gewaehlt', spiel.has(z.dataset.kennung));
  }
}

/**
 * Was ein Klick unter der Zeichnung wählt -- auf eine Meldung oder eine
 * Zeile der Liste --, wie ein Klick in die Zeichnung: einen Knoten, einen
 * Anhang (eine Last im Balkensystem) und ein Element selbst; einen Punkt,
 * den der Adapter nicht wählen lässt (`waehlbar`) -- ein Lager, eine
 * Stütze --, über seinen Knoten. Was nicht in der Zeichnung steht, etwa ein
 * Querschnitt, wählt nichts (null).
 */
function waehlbarVon(a, z, kennung) {
  if (a.adapter.anhaenge?.hat(z, kennung)) return kennung;
  const da = a.modell.verzeichnis(z).get(kennung);
  if (!da) return null;
  const selbst = da.art === null || da.art.form !== 'punkt' || (a.adapter.waehlbar?.(da.art, da.e) ?? true);
  return selbst ? kennung : da.e.knoten;
}

/**
 * Über der Liste, was der Kern sagt: warum er nicht geantwortet hat, sonst
 * seine Meldungen -- rot, was falsch ist, grau, was nur fehlt. Ein Klick
 * wählt, was eine nennt.
 */
export function meldungsliste(a) {
  const kaputt = kernfehler(a);
  if (kaputt) return el('div.qa-meldungen', {}, [el('div.qa-meldung', { text: kaputt })]);
  const meldungen = kernmeldungen(a);
  if (!meldungen.length) return null;
  const z = a.adapter.zeichnung();
  return el('div.qa-meldungen', {}, meldungen.map((m) => el('button.qa-meldung', {
    type: 'button', text: m.text, class: m.fehler ? '' : 'ist-hinweis', title: 'Wählt, was die Meldung nennt',
    on: { click: () => cadWaehlen(a, [...new Set(m.elemente.map((k) => waehlbarVon(a, z, k)).filter(Boolean))]) },
  })));
}

/**
 * Baut die Zeilen der Liste: `zeile({kennung, name, was, wert, vorher})` --
 * wie das Teil heisst (sonst seine Kennung), was es ist, rechts eine Zahl.
 * Rot steht, was der Kern an ihm beanstandet, mit seinen Sätzen als Titel.
 * Ein Klick wählt es im Fenster -- nach `vorher`, etwa dem Lastfall einer
 * Last, damit sie zu sehen ist.
 */
export function listenzeilen(a) {
  const z = a.adapter.zeichnung();
  const { fehler, texte } = meldungenJe(a);
  const spiel = imSpiel(a);
  return ({
    kennung, name = kennung, was = '', wert = '', vorher = () => {},
  }) => {
    const waehlt = waehlbarVon(a, z, kennung);
    return el('button.cad-element', {
      type: 'button',
      class: [fehler(kennung) ? 'ist-fehler' : '', spiel.has(waehlt) ? 'ist-gewaehlt' : ''].join(' '),
      dataset: { kennung: waehlt ?? '' },
      title: texte(kennung).join('\n') || 'Im Zeichenfenster wählen',
      on: {
        click: () => {
          vorher();
          cadWaehlen(a, waehlt ? [waehlt] : []);
        },
      },
    }, [
      el('span.cad-element-name', { text: name }),
      el('span.cad-element-was', { text: was }),
      el('span.cad-element-wert', { text: wert }),
    ]);
  };
}

/**
 * Ob in der Zeichnung noch gar nichts steht, auch kein Knoten. Dann sagt es
 * die Liste darunter, samt den Werkzeugen (`listengruppen`) -- und kein
 * Hinweis über dem Editor sagt es noch einmal (`mitHinweis` in apps.js).
 */
export function nichtsGezeichnet(z) {
  return !z?.knoten.length;
}

/**
 * Die Liste der Teile: je Art eine Gruppe aus `[titel, zeilen]`, die auf-
 * und zuklappt -- zu Beginn zu, und das merkt sich das Fenster (Benutzer,
 * 2026-10-24). Ist noch nichts gezeichnet (`nichtsGezeichnet`), sagt sie,
 * womit man beginnt: die Werkzeuge mit ihren Tasten.
 */
export function listengruppen(a, gruppen) {
  const da = gruppen.filter(([, zeilen]) => zeilen.length);
  if (da.length) return da.map(([titel, zeilen]) => klappgruppe(titel, zeilen, a.adapter.aufgeklappt, 'cad-elemente'));
  if (!nichtsGezeichnet(a.adapter.zeichnung())) return [];
  const werkzeuge = a.einstellung.werkzeuge.map((w) => `${w.text} ${w.taste.toUpperCase()}`).join(', ');
  return [el('p.leer-zeile', {
    text: `Noch nichts gezeichnet: ${werkzeuge}${a.adapter.vorlageOeffnen ? ' – oder eine Vorlage T' : ''}.`,
  })];
}

// ===========================================================================
// Das schwebende Fenster
// ===========================================================================

/**
 * Das schwebende Fenster zur Auswahl. Sie zerfällt nach Listen -- Knoten
 * unter 'knoten', Anhänge unter 'anhaenge', Ecken für sich --, und ist
 * alles aus einer, baut `je[liste](a, z, kennungen)` -- sonst
 * `je.sonst(a, z, kennungen, liste)` -- Titel und Inhalt; gewählte Ecken
 * baut `je.ecken(a, z, schluessel)`. Knoten und Ecken zeigen ohne eigenen
 * Bau ihre Lage. Verschiedenes zugleich -- und was keinen eigenen Bau hat
 * -- sagt nur, was damit geht. Neu gebaut wird das Fenster, wenn die Antwort des Kerns kommt
 * -- die Meldungen darin sind ihre -- und wenn sich `zusatz` ändert.
 */
export function auswahlEigenschaften(a, je, zusatz = null) {
  const bau = { knoten: knotenEigenschaften, ecken: eckenEigenschaften, ...je };
  const z = a.adapter.zeichnung();
  const verzeichnis = a.modell.verzeichnis(z);
  const listen = new Map();
  const ecken = [];
  for (const s of a.auswahl) {
    const { kennung, i } = auswahlTeil(s);
    let liste = null;
    if (i !== null) ecken.push(s);
    else if (a.adapter.anhaenge?.hat(z, kennung)) liste = 'anhaenge';
    else if (verzeichnis.has(kennung)) liste = verzeichnis.get(kennung).art?.liste ?? 'knoten';
    if (liste) listen.set(liste, [...(listen.get(liste) || []), kennung]);
  }
  const schluessel = JSON.stringify([Boolean(frischeAntwort(a)), zusatz]);
  const anzahl = ecken.length + [...listen.values()].reduce((n, k) => n + k.length, 0);
  if (!anzahl) return { titel: '', inhalt: [] };
  if (ecken.length === anzahl) return { schluessel, ...bau.ecken(a, z, ecken) };
  const [[liste, kennungen] = []] = listen;
  const bauen = listen.size === 1 && !ecken.length && (bau[liste] || bau.sonst);
  if (bauen) return { schluessel, ...bauen(a, z, kennungen, liste) };
  return {
    titel: `${anzahl} gewählt`,
    inhalt: [el('p.cad-hinweis-klein', {
      text: ecken.length ? 'Elemente und einzelne Ecken – verschieben mit V.'
        : 'Verschiedenes zugleich – verschieben mit V, löschen mit Entf.',
    })],
    schluessel,
  };
}

/** Gewählte Knoten, wenn die App nichts dazu sagt: ihre Lage, bei mehreren mit «Var». */
function knotenEigenschaften(a, z, knoten) {
  return {
    titel: knoten.length === 1 ? a.adapter.name(a, knoten[0]) : `${knoten.length} Knoten`,
    inhalt: lagefelder(a, z, knoten),
  };
}

/**
 * Gewählte Ecken -- in einer Zeichnung, deren Teile nicht an gemeinsamen
 * Knoten hängen: ihre Lage, bei mehreren mit «Var». Geändert wird nur die
 * Ecke, was sonst am selben Punkt liegt, bleibt. Eine Linie hat Anfang und
 * Ende statt Ecken.
 */
function eckenEigenschaften(a, z, schluessel) {
  const einzeln = schluessel.length === 1;
  const { kennung, i } = auswahlTeil(schluessel[0]);
  const linie = a.modell.verzeichnis(z).get(kennung)?.art?.form === 'linie';
  const ecke = linie ? (i === 0 ? 'Anfang' : 'Ende') : `Ecke ${i + 1}`;
  return {
    titel: einzeln ? `${a.adapter.name(a, kennung)} · ${ecke}` : `${schluessel.length} Ecken`,
    inhalt: [
      ...lagefelder(a, z, schluessel),
      el('p.cad-hinweis-klein', {
        text: einzeln ? 'Nur diese Ecke – was sonst an diesem Punkt liegt, bleibt.'
          : 'Nur diese Ecken – was sonst an ihren Punkten liegt, bleibt.',
      }),
    ],
  };
}

/**
 * Die gewählten Einträge einer Liste, zum Ändern zugleich: `wert(feld)` ist,
 * was sie gemeinsam haben, sonst VAR; `setzen(feld)(w)` schreibt in alle --
 * `dazu(e, feld, zz)` darf an jedem mehr ändern.
 */
export function zugleich(a, z, liste, kennungen, dazu = () => {}) {
  const gewaehlt = z[liste].filter((e) => kennungen.includes(e.kennung));
  return {
    gewaehlt,
    wert: (feld) => gemeinsam(gewaehlt.map((e) => e[feld])),
    setzen: (feld) => (w) => a.aendern((zz) => {
      for (const e of zz[liste]) {
        if (!kennungen.includes(e.kennung)) continue;
        e[feld] = w;
        dazu(e, feld, zz);
      }
    }),
  };
}

/** Die Vorgabe `v` eines Werkzeugs zum Ändern, wie bei `zugleich`: sie gilt dem, was es als Nächstes anlegt. */
export function vorgabe(a, v) {
  return {
    wert: (feld) => v[feld],
    setzen: (feld) => (w) => {
      v[feld] = w;
      a.neuZeichnen();
    },
  };
}

/** Ein Zahlenfeld, auch für mehrere: bei VAR leer, mit «Var» darin. */
export function zahlfeldMitVar({ wert, platzhalter, ...rest }) {
  return zahlfeld({ ...rest, wert: wert === VAR ? null : wert, platzhalter: wert === VAR ? 'Var' : platzhalter });
}

/** Ja oder nein als Schalter -- auch für mehrere, dann mit «Var». */
export function jaNein(wert, setzen, titel) {
  return wahlSchalter({
    werte: mitVar([{ wert: true, beschriftung: 'ja' }, { wert: false, beschriftung: 'nein' }], wert),
    gewaehlt: wert === VAR ? VAR : Boolean(wert), setzen, titel,
  });
}

/**
 * Je Achse ein Feld für die Lage der gewählten Punkte -- Knoten oder Ecken,
 * je ihr Schlüssel der Auswahl: was sie gemeinsam haben, sonst «Var». Eine
 * getippte Lage gilt für alle, so stehen sie danach in einer Flucht; an
 * einer Ecke ändert sie nur die Ecke, was sonst dort liegt, bleibt.
 */
export function lagefelder(a, z, schluessel) {
  const lagen = a.modell.lagen(z);
  const verzeichnis = a.modell.verzeichnis(z);
  const punkte = schluessel.map((s) => {
    const { kennung, i } = auswahlTeil(s);
    const da = verzeichnis.get(kennung);
    return [s, lagen.get(i === null ? kennung : da && a.modell.verweise(da.art, da.e)[i])];
  }).filter(([, p]) => p);
  const setzen = (achse) => (w) => a.aendern((zz) => {
    for (const [s, p] of punkte) a.modell.verschieben(zz, new Set([s]), p.map((x, i) => (i === achse ? w - x : 0)));
  });
  return a.adapter.achsen.map((name, achse) => cadZeile(name, zahlfeldMitVar({
    wert: gemeinsam(punkte.map(([, p]) => p[achse])), schritt: a.raster, beiAenderung: setzen(achse),
  }), a.einstellung.einheit));
}

/** Wie lang eine Linie ist und von wo nach wo -- im Fenster einer einzelnen. */
export function laengenzeile(a, z, e) {
  const lagen = a.modell.lagen(z);
  const [p, q] = [lagen.get(e.von), lagen.get(e.bis)];
  if (!p || !q) return null;
  return el('p.cad-info', {
    text: `L = ${zahlText(abstand(p, q), a.einstellung.stellen)} ${a.einstellung.einheit} · ${e.von} → ${e.bis}`,
  });
}

/** Ein Teil der Zeichnung mit den Meldungen des Kerns als Titel -- zu lesen beim Darüberfahren. */
export function mitTitel(knoten, texte) {
  if (texte?.length) {
    const t = svgEl('title');
    t.textContent = texte.join('\n');
    knoten.append(t);
  }
  return knoten;
}

/**
 * Was «Alles zeigen» ins Bild nimmt: die kleinsten und grössten
 * Koordinaten der Punkte -- ohne Punkte das Feld `vorgabe`.
 */
export function umrissVon(punkte, vorgabe) {
  if (!punkte.length) return vorgabe;
  const spalten = punkte[0].map((_, i) => punkte.map((p) => p[i]));
  return [spalten.map((s) => Math.min(...s)), spalten.map((s) => Math.max(...s))];
}
