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

/** Die eine Suche: in welchem Projekt, für welches Modell, ob sie läuft und anhalten soll, die letzte Antwort. */
const suche = {
  projekt: null, kennung: null, laeuft: false, anhalten: false, antwort: null, fehler: '',
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
    projekt, kennung, laeuft: true, anhalten: false, antwort: null, fehler: '',
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
    // Angehalten oder fertig: das Fachwerk der letzten Runde -- ob fertig gesucht, sagt es selbst.
    const gefunden = suche.antwort?.gefunden;
    if (gefunden && da()) eintragAendern(kennung, (e) => { e.fachwerk = gefunden; });
  } catch (fehler) {
    suche.fehler = fehler.message || String(fehler);
  }
  suche.laeuft = false;
  aendern();
}

/** Hält die laufende Suche nach dieser Runde an: was sie gab, wird abgelegt. */
export function anhalten() {
  if (!suche.laeuft) return;
  suche.anhalten = true;
  aendern();
}

/**
 * Das Fachwerk, das gilt (Dateikopf), und wie es dazu kam: `{fachwerk,
 * runden, fertig, im_modell, moeglich, laeuft, meldungen}` -- `meldungen`
 * ist, was zu ihm zu sagen ist. Null, wenn keines gilt. `daten` sind die
 * Zeichendaten der letzten Rechnung.
 */
export function gezeigtesFachwerk(kennung, daten) {
  const s = sucheVon(kennung);
  const a = s?.antwort;
  const ausSuche = a?.fachwerk && (s.laeuft
    || (daten?.stand !== 'gefunden' && daten?.abdruck === a.gefunden?.abdruck));
  if (ausSuche) {
    return {
      ...a.stand, fachwerk: a.fachwerk, runden: a.stand.runde, fertig: a.fertig, laeuft: s.laeuft,
      meldungen: a.meldungen,
    };
  }
  const f = daten?.fachwerk;
  if (!f) return null;
  return {
    fachwerk: f, runden: f.runden, fertig: f.fertig, im_modell: f.im_modell, moeglich: f.moeglich,
    laeuft: false, meldungen: daten.zum_fachwerk,
  };
}
