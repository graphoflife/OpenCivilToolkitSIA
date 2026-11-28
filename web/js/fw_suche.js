/**
 * fw_suche.js -- die Suche nach einem Fachwerk, Runde um Runde.
 *
 * Die Seite rechnet nichts: sie fragt den Kern nach der nächsten Runde
 * (`api.fachwerkSuchen`) und gibt ihm den Zustand der letzten zurück, bis
 * er «fertig» sagt oder jemand «Anhalten» drückt. Nach jeder Runde zeigt
 * sie das Fachwerk, das die Runde gab; am Ende legt sie es im Eintrag ab
 * (`fachwerk`) -- von da an rechnet die Rechnung es nach wie jede andere
 * Eingabe und erkennt an seinem Abdruck, ob es noch zum Modell passt.
 *
 * Beim Verfahren SIMP gibt eine Runde einige Schritte der Form, noch ohne
 * Fachwerk; das liest der Kern erst, wenn die Form fertig ist. Hält jemand
 * vorher an, fragt die Seite ein letztes Mal, mit `abschliessen`: dann
 * liest er es aus der Form, wie sie ist (`liest`).
 *
 * Es läuft höchstens eine Suche zugleich. Wer das Modell während der Suche
 * ändert, ändert, was die nächste Runde bekommt: der Kern beginnt von vorn,
 * weil der Zustand nicht mehr zum Modell passt. Verschwindet das Modell --
 * gelöscht, ein anderes Projekt gewählt --, hört die Suche auf und legt
 * nichts ab.
 *
 * WELCHES FACHWERK GILT (`gezeigtesFachwerk`): solange gesucht wird, das der
 * letzten Runde. Danach das nachgerechnete der Rechnung -- bis sie das
 * eben gefundene nachgerechnet hat aber noch das der Suche, wenn es zum
 * Modell der letzten Rechnung gehört (gleicher Abdruck): sonst stünde für
 * einen Augenblick «Noch kein Fachwerk gesucht» da.
 */

import { api } from './api.js';
import { aendern, eintragAendern, eintragVon, zustand } from './zustand.js';

/**
 * Die eine Suche: in welchem Projekt, für welches Modell, ob sie läuft,
 * anhalten soll und schon das Fachwerk aus der Form liest, die letzte Antwort.
 */
const suche = {
  projekt: null, kennung: null, laeuft: false, anhalten: false, liest: false, antwort: null, fehler: '',
};

/** Die Suche dieses Fachwerkmodells im gezeigten Projekt -- laufend oder die letzte --, sonst null. */
export const sucheVon = (kennung) => (
  suche.kennung === kennung && suche.projekt === zustand.projekt ? suche : null);

/** Ob gerade eine Suche läuft, gleich für welches Modell. */
export const sucheLaeuft = () => suche.laeuft;

/** Sucht ein Fachwerk für das Modell `kennung`, bis der Kern fertig ist oder jemand anhält. */
export async function suchen(kennung) {
  if (suche.laeuft) return;
  const { projekt } = zustand;
  Object.assign(suche, {
    projekt, kennung, laeuft: true, anhalten: false, liest: false, antwort: null, fehler: '',
  });
  aendern();
  const da = () => zustand.projekt === projekt && eintragVon(kennung);
  let stand = null;
  try {
    while (!suche.anhalten && da()) {
      const antwort = await api.fachwerkSuchen(projekt, kennung, stand);
      suche.antwort = antwort;
      aendern();
      if (antwort.fertig) break;
      stand = antwort.zustand;
    }
    // Angehalten, und die Form hat noch kein Fachwerk: der Kern liest es aus ihr, wie sie ist.
    if (suche.antwort && !suche.antwort.gefunden && stand && da()) {
      suche.liest = true;
      aendern();
      suche.antwort = await api.fachwerkSuchen(projekt, kennung, stand, true);
    }
    // Angehalten oder fertig: das Fachwerk der letzten Runde -- ob fertig gesucht, sagt es selbst.
    const gefunden = suche.antwort?.gefunden;
    if (gefunden && da()) eintragAendern(kennung, (e) => { e.fachwerk = gefunden; });
  } catch (fehler) {
    suche.fehler = fehler.message || String(fehler);
  }
  suche.laeuft = false;
  suche.liest = false;
  aendern();
}

/** Hält die laufende Suche nach dieser Runde an: was sie gab, wird abgelegt. */
export function anhalten() {
  if (!suche.laeuft) return;
  suche.anhalten = true;
  aendern();
}

/**
 * Das Fachwerk, das gilt (Dateikopf), und wie es dazu kam: `{verfahren,
 * fachwerk, form, runden, fertig, im_modell, moeglich, laeuft, liest,
 * meldungen}` -- beim Verfahren SIMP `runden` die Schritte, `form` die
 * Form, und während der Schritte `fachwerk` noch null; `meldungen` ist, was
 * zum Fachwerk zu sagen ist. Null, wenn keines gilt. `daten` sind die
 * Zeichendaten der letzten Rechnung.
 */
export function gezeigtesFachwerk(kennung, daten) {
  const s = sucheVon(kennung);
  const a = s?.antwort;
  const ausSuche = (a?.fachwerk || a?.form) && (s.laeuft
    || (daten?.stand !== 'gefunden' && daten?.abdruck === a.gefunden?.abdruck));
  if (ausSuche) {
    return {
      ...a.stand, verfahren: a.verfahren, fachwerk: a.fachwerk, form: a.form,
      runden: a.stand.runde ?? a.stand.schritt, fertig: a.fertig, laeuft: s.laeuft, liest: s.liest,
      meldungen: a.meldungen,
    };
  }
  const f = daten?.fachwerk;
  if (!f) return null;
  return {
    verfahren: daten.verfahren, fachwerk: f, form: daten.form, runden: f.runden, fertig: f.fertig,
    im_modell: f.im_modell, moeglich: f.moeglich, laeuft: false, liest: false, meldungen: daten.zum_fachwerk,
  };
}
