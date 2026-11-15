/**
 * cad_palette.js -- das schwebende Fenster im Zeichenfenster.
 *
 * Steht anfangs oben rechts in der Zeichnung und lässt sich an seinem Kopf
 * verschieben. Wohin man es gestellt hat, merkt sich der Browser -- als
 * Abstand von oben rechts: wechselt der Inhalt, bleibt die obere Kante
 * stehen und nur die untere wandert (Benutzer, 2026-10-23; bis dahin war es
 * umgekehrt). Es bleibt immer ganz im Bild und lässt sich auf seinen Kopf
 * zuklappen.
 *
 * Was darin steht, setzt `paletteZeichnen` je nach Lage: in Ruhe die
 * Koordinaten des Zeigers, Raster und Fang; während eines Befehls seine
 * Frage, die Eingabefelder -- je Achse eines -- und die Hilfen; bei einer
 * Auswahl, was die App zu ihr zeigt. Die Zeilen darin (`cadZeile`,
 * `schalterzeile`) sind dieselben, aus denen die Apps ihre Eigenschaften
 * bauen.
 */

import { wahlSchalter } from './bausteine.js';
import { zahlText } from './cad_ansicht.js';
import {
  feldeinheiten, feldnamen, felderLeeren, hilfstext, taste as eingabeTaste, zeigerFang,
} from './cad_eingabe.js';
import { el } from './dom.js';

const ABLAGE = 'opencivil.cad.palette';

function gemerkt() {
  try {
    return { rechts: 10, oben: 10, zu: false, ...JSON.parse(localStorage.getItem(ABLAGE) || '{}') };
  } catch {
    return { rechts: 10, oben: 10, zu: false };
  }
}

function merken(lage) {
  try {
    localStorage.setItem(ABLAGE, JSON.stringify(lage));
  } catch {
    // Privater Modus: dann gilt es bis zum Neuladen.
  }
}

/** Das schwebende Fenster, eingehängt in `flaeche`. */
export function paletteBauen(flaeche) {
  const lage = gemerkt();
  const titel = el('span.cad-palette-titel');
  const zu = el('button.cad-palette-zu', {
    type: 'button', title: 'Zuklappen', text: '–',
  });
  const griff = el('span.cad-palette-griff', { text: '⠿', title: 'Verschieben' });
  const kopf = el('div.cad-palette-kopf', {}, [griff, titel, zu]);
  const koerper = el('div.cad-palette-koerper');
  const knoten = el('div.cad-palette', {}, [kopf, koerper]);
  flaeche.append(knoten);

  // Reicht das Fenster über den unteren Rand, rückt es hinauf, bis es ganz zu
  // sehen ist. Gemerkt bleibt die gewählte Lage: schrumpft der Inhalt wieder,
  // kehrt es dorthin zurück.
  const unterstes = () => Math.max(2, flaeche.clientHeight - knoten.offsetHeight - 2);
  const halten = () => {
    const b = flaeche.clientWidth;
    if (!b || !flaeche.clientHeight) return;
    lage.rechts = Math.min(Math.max(2, lage.rechts), Math.max(2, b - knoten.offsetWidth - 2));
    knoten.style.right = `${lage.rechts}px`;
    knoten.style.top = `${Math.min(Math.max(2, lage.oben), unterstes())}px`;
  };

  const zuklappen = (wert) => {
    lage.zu = wert;
    knoten.classList.toggle('ist-zu', wert);
    zu.textContent = wert ? '+' : '–';
    zu.title = wert ? 'Aufklappen' : 'Zuklappen';
    merken(lage);
    halten();
  };
  zu.addEventListener('click', () => zuklappen(!lage.zu));
  zuklappen(lage.zu);

  kopf.addEventListener('pointerdown', (start) => {
    if (start.target === zu || start.button !== 0) return;
    start.preventDefault();
    // Von dort, wo es steht -- auch wenn es gerade hinaufgerückt ist.
    const anfang = { ...lage, oben: knoten.offsetTop };
    const bewegen = (e) => {
      lage.rechts = anfang.rechts - (e.clientX - start.clientX);
      lage.oben = Math.min(Math.max(2, anfang.oben + (e.clientY - start.clientY)), unterstes());
      halten();
    };
    const los = () => {
      window.removeEventListener('pointermove', bewegen);
      window.removeEventListener('pointerup', los);
      merken(lage);
    };
    window.addEventListener('pointermove', bewegen);
    window.addEventListener('pointerup', los);
  });

  return {
    knoten,
    halten,
    /** Auf, wenn es zu ist -- etwa, weil jemand Zahlen tippt, die hineingehören. */
    aufklappen() {
      if (lage.zu) zuklappen(false);
    },
    /** Titel und Inhalt setzen -- Felder mit Fokus bleiben, wenn `schluessel` gleich ist. */
    setzen(text, inhalt, schluessel = null) {
      titel.textContent = text;
      if (schluessel !== null && koerper.dataset.schluessel === schluessel) return;
      koerper.dataset.schluessel = schluessel ?? '';
      koerper.replaceChildren(...inhalt.filter(Boolean));
      halten();
    },
    koerper,
  };
}

// ===========================================================================
// Zeilen
// ===========================================================================

/** Eine Zeile im schwebenden Fenster: Beschriftung, Feld, Einheit. */
export function cadZeile(beschriftung, eingabe, einheit = '') {
  return el('label.cad-zeile', {}, [
    el('span', { text: beschriftung }), eingabe, einheit ? el('span.einheit', { text: einheit }) : el('span'),
  ]);
}

/** Wie `cadZeile`, für einen Schalter -- ein «div», kein «label»: ein Klick auf den Text löste sonst die erste Stellung aus. */
export function schalterzeile(beschriftung, schalter, zusatz = '') {
  return el('div.cad-zeile', {}, [
    el('span', { text: beschriftung }), schalter, zusatz ? el('span.einheit', { text: zusatz }) : el('span'),
  ]);
}

// ===========================================================================
// Inhalt
// ===========================================================================

/** Die Koordinaten des Zeigers, mit Einheit -- in der Ruhe oben im schwebenden Fenster. */
export function lageZeichnen(a) {
  const ziel = a.teile.lage;
  if (!ziel) return;
  const f = zeigerFang(a);
  const { stellen: s, einheit: e } = a.einstellung;
  ziel.textContent = f ? a.adapter.achsen.map((x, i) => `${x} ${zahlText(f.p[i], s)} ${e}`).join('   ') : '';
}

/** Ein Feld der Punkteingabe: schmal, rechtsbündig, ohne Pfeile. */
function eingabefeld(a, i, name) {
  const feld = el('input.cad-eingabe', {
    type: 'text', inputMode: 'decimal', value: a.eingabe.felder[i], placeholder: name,
    title: name, autocomplete: 'off',
    on: {
      input: (e) => { a.eingabe.felder[i] = e.target.value; },
      keydown: (e) => {
        // Buchstaben gehören den Hilfen, auch wenn ein Feld den Fokus hat.
        if (e.key.length === 1 && /[a-zA-Z]/.test(e.key) && !e.ctrlKey && !e.metaKey) {
          if (eingabeTaste(a, e)) {
            e.preventDefault();
            a.neuZeichnen();
          }
        }
      },
    },
  });
  feld.dataset.feld = String(i);
  return feld;
}

function hilfsknopf(a, zeichen, titel, tun, an = false) {
  return el('button.cad-hilfe', {
    type: 'button', title: titel, class: an ? 'ist-an' : '',
    on: { click: (e) => { e.preventDefault(); tun(); a.neuZeichnen(); } },
  }, [zeichen]);
}

/** Der Teil des Fensters, der während eines Befehls nach dem Punkt fragt -- je Achse ein Feld und eine Taste. */
function punkteingabe(a) {
  const pe = a.eingabe;
  const einheiten = feldeinheiten(a);
  const modus = (wert, text, titel) => el('button.schalter-halb', {
    type: 'button', text, title: titel, class: pe.modus === wert ? 'ist-an' : '',
    on: { click: () => { pe.modus = wert; felderLeeren(pe); a.neuZeichnen(); } },
  });
  const fake = (k) => ({ key: k, preventDefault() {} });
  return [
    pe.bindung
      ? el('div.cad-bindung-zeile', {}, [
        el('span.cad-bindungsmarke', { text: pe.bindung.text }),
        el('button.weg', {
          type: 'button', text: '×', title: 'Bindung lösen (Esc)',
          on: { click: () => { pe.bindung = null; a.neuZeichnen(); } },
        }),
      ])
      : el('span.schalter.cad-modus', {}, [
        modus('rel', 'Δ', 'Relativ zum Bezugspunkt'),
        modus('abs', 'abs', 'Absolut'),
        modus('polar', 'L∠', 'Länge und Winkel ab dem Bezugspunkt'),
      ]),
    el('div.cad-felder', {}, [
      ...feldnamen(a).flatMap((name, i) => (name
        ? [eingabefeld(a, i, name), el('span.einheit', { text: einheiten[i] })] : [])),
      el('button.knopf.knopf-klein', {
        type: 'button', text: '↵', title: 'Punkt setzen (Enter)',
        on: { click: () => a.getipptLiefern() },
      }),
    ]),
    el('div.cad-hilfen', {}, [
      // Was der Befehl selbst an Tasten hat -- beim Verschieben D.
      ...(a.befehl?.tasten || []).map((t) => hilfsknopf(
        a, t.zeichen, t.titel, () => t.tun(a, a.befehl), t.an?.(a.befehl))),
      hilfsknopf(a, 'R', 'Bezugspunkt auf den gefangenen Punkt (R)', () => eingabeTaste(a, fake('r'))),
      ...a.adapter.achsen.map((x, i) => hilfsknopf(
        a, x.toUpperCase(), `Entlang ${x} (${x.toUpperCase()})`, () => eingabeTaste(a, fake(x)),
        pe.bindung?.art === 'achse' && pe.bindung.achse === i)),
      hilfsknopf(a, '∥', 'Parallel zu einer Linie (P)', () => eingabeTaste(a, fake('p')),
        pe.warten === 'parallel' || pe.bindung?.art === 'parallel'),
      hilfsknopf(a, '⊥', 'Senkrecht zu einer Linie (S)', () => eingabeTaste(a, fake('s')),
        pe.warten === 'senkrecht' || pe.bindung?.art === 'senkrecht'),
      hilfsknopf(a, 'M', 'Mitte zweier Punkte (M)', () => eingabeTaste(a, fake('m')),
        pe.warten?.art === 'mitte'),
    ]),
    a.befehl?.kopie ? el('label.cad-zeile', {}, [
      el('span', { text: 'Anzahl' }),
      el('input', {
        type: 'number', min: 1, step: 1, value: a.befehl.anzahl,
        on: { input: (e) => { a.befehl.anzahl = Number(e.target.value) || 1; a.obenBald(); } },
      }),
    ]) : null,
  ];
}

/**
 * Füllt das schwebende Fenster. Neu gebaut wird sein Inhalt nur, wenn sich
 * die Lage ändert -- nicht bei jeder Zeigerbewegung, sonst verlöre ein Feld
 * beim Tippen den Fokus.
 */
export function paletteZeichnen(a) {
  const pal = a.teile.palette;
  if (a.befehl) {
    const pe = a.eingabe;
    const neuTeil = a.befehl.neu ? a.adapter.neuEigenschaften?.(a, a.befehl.neu) : null;
    const schluessel = JSON.stringify([
      'befehl', a.befehl.name, pe.modus, pe.runde, pe.bindung?.text, pe.warten?.art || pe.warten,
      a.befehl.kopie ? a.befehl.anzahl : null, neuTeil?.schluessel ?? null,
      (a.befehl.tasten || []).map((t) => !!t.an?.(a.befehl)),
    ]);
    pal.setzen(hilfstext(a) || a.befehl.frage(a), [
      ...punkteingabe(a),
      neuTeil ? el('div.cad-neu', {}, neuTeil.inhalt) : null,
    ], schluessel);
    return;
  }
  if (a.auswahl.size) {
    const teil = a.adapter.eigenschaften(a);
    pal.setzen(teil.titel, teil.inhalt, JSON.stringify(['auswahl', a.version, [...a.auswahl], teil.schluessel ?? null]));
    return;
  }
  // Das Raster als Schalter mit seinen Stufen: Auswahllisten gibt es nur für
  // die Wahl eines Materials (Benutzer, 2026-10-23).
  const raster = wahlSchalter({
    werte: a.einstellung.raster.stufen.map((r) => ({ wert: r, beschriftung: String(r) })),
    gewaehlt: a.raster, setzen: (w) => { a.raster = w; a.neuZeichnen(); },
    titel: `Raster in ${a.einstellung.einheit}: daran fängt der Zeiger`, klasse: '.cad-wahl.cad-rasterwahl',
  });
  const fang = el('input', {
    type: 'checkbox', checked: a.fang, title: 'Fang an Knoten, Linien und Raster (Alt hält ihn an)',
    on: { change: (e) => { a.fang = e.target.checked; a.neuZeichnen(); } },
  });
  a.teile.lage = el('span.cad-lage');
  pal.setzen('Zeiger', [
    a.teile.lage,
    el('div.cad-ruhe', {}, [
      el('span', { text: `Raster in ${a.einstellung.einheit}` }), el('label', {}, [fang, ' Fang']),
    ]),
    raster,
  ], JSON.stringify(['ruhe', a.raster, a.fang]));
  if (!a.teile.lage.isConnected) a.teile.lage = pal.koerper.querySelector('.cad-lage');
  lageZeichnen(a);
}
