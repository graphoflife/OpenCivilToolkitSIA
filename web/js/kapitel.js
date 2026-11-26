/**
 * kapitel.js -- die Kapitel eines Bauteils als Knöpfe, jedes mit seinem Fenster.
 *
 * Unter den Panels eines Bauteils stehen keine langen Eingabelisten, sondern
 * Knöpfe, in Gruppen: Nachweise, Analysen, Werkzeug. Ein Knopf zeigt sein
 * Zeichen, seinen Namen und darunter klein, was eingestellt ist --
 * «2 Einwirkungen», «aus». Ein Klick öffnet das Fenster mit den Eingaben
 * (`fenster.js`).
 *
 * Welche Kapitel ein Bauteil hat, sagt seine Art: die Platte in
 * `plattenkapitel.js`, die Querschnittsanalyse in `querschnittsanalyse.js`
 * -- die Nachweise, die beide gleich führen, und die Analysen baut für
 * beide `nachweise.js`. Hier steht nur, wie Knopf und Fenster daraus
 * werden. Ein Kapitel ist ein Eintrag mit
 *
 *   schluessel   zugleich der Name seines Zeichens (sinnbilder.js)
 *   name         auf dem Knopf -- mit weichem Trennstrich, wo ein Wort
 *                breiter ist als der Knopf
 *   titel        über dem Fenster
 *   bezug(e)     worauf sich die Eingaben beziehen, unter dem Titel (nicht jedes)
 *   hilfe        was hinter dem Fragezeichen steht: {zeilen, formel} (nicht jedes)
 *   inhalt(e)    die Knoten des Fensters
 *   stand(e)     die kleine Zeile des Knopfs: {an, text}
 *
 * `e` ist der Eintrag des Bauteils, wie er im Projekt steht.
 *
 * Wo die Eingaben eines Bauteils selbst Kacheln sind -- Durchstanzen,
 * Grundbruch, Setzung, Pfahl, Erdbeben (Benutzer, 2026-11-25) --, wird
 * jede Gruppe der Vorgaben des Kerns ein Kapitel (`gruppenkapitel`): ihr
 * Titel, ihre Felder, auf der Kachel klein ihre wichtigsten Werte.
 */

import { erklaerung, karte, panel } from './bausteine.js';
import { el } from './dom.js';
import { fenster, fensterOeffnen } from './fenster.js';
import { span } from './mathe.js';
import { sinnbild } from './sinnbilder.js';

/** «1 Einwirkung», «3 Einwirkungen». */
function anzahl(n, eins, mehr) {
  return `${n} ${n === 1 ? eins : mehr}`;
}

/** Wie viele Zeilen einer Liste gerechnet werden -- ausgeschaltete stehen nur da. */
export const eingeschaltet = (liste) => (liste || []).filter((k) => k.aktiv !== false).length;

/** Eine Liste als Stand: «2 Fälle», ohne eingeschaltete Zeile `keins` -- «kein Fall». */
export function zeilenstand(liste, eins, mehr, keins) {
  const n = eingeschaltet(liste);
  return { an: n > 0, text: n ? anzahl(n, eins, mehr) : keins };
}

/** Ein Schalter als Stand: ein oder aus. */
export const schalter = (an) => ({ an, text: an ? 'ein' : 'aus' });

/**
 * Ein Stand, dem noch etwas fehlt: der Knopf sagt, was -- nicht «1 Fall» in
 * Blau, wenn kein Fall rechnen kann (Benutzer, 2026-11-19: ein unfertiger
 * Zustand sagt am Ort, was fehlt). `fehlt` leer: der Stand, wie er ist.
 */
export function standOhne(stand, fehlt) {
  return stand.an && fehlt ? { an: false, text: fehlt } : stand;
}

/** Dasselbe im Fenster, über den Fällen, grau wie alles, was nur fehlt -- oder nichts. */
export function fehltHinweis(fehlt) {
  return fehlt ? el('p.hinweis', { text: `Noch ${fehlt} – so rechnet kein Fall.` }) : null;
}

/**
 * Was eine Gebrauchsliste rechnet: der Anteil der Tragsicherheit, wenn er
 * eingeschaltet ist, und die eigenen Lastfälle -- «60 % + 1 Fall».
 * Abgeleitet wird aus den eingeschalteten `einwirkungen` der Tragsicherheit;
 * ohne eine rechnet der Anteil nichts. Bis 2026-11-19 stand dann trotzdem
 * «60 %» in Blau.
 */
export function gebrauchsstand(liste, einwirkungen) {
  const eigene = eingeschaltet(liste.faelle);
  const teile = [
    liste.aus_tragsicherheit && eingeschaltet(einwirkungen) ? `${liste.anteil} %` : null,
    eigene ? anzahl(eigene, 'Fall', 'Fälle') : null,
  ].filter(Boolean);
  if (teile.length) return { an: true, text: teile.join(' + ') };
  return { an: false, text: liste.aus_tragsicherheit ? 'keine Einwirkung' : 'kein Fall' };
}

/**
 * «M–E_eq» mit tiefgestelltem eq: was hinter einem Unterstrich steht, ist
 * ein Index.
 */
function mitIndex(text) {
  return text.split(/_(\w+)/).map((teil, i) => (i % 2 ? el('sub', { text: teil }) : teil));
}

/**
 * Eine Gruppe der Vorgaben als Kapitel. `vorgaben` sind die Gruppen des
 * Eintrags (`eingabegruppen` in bausteine.js), `titel` die Gruppe. Auf der
 * Kachel stehen ihr Sinnbild `zeichen`, ihr Titel -- oder `name`, wo ein
 * Wort einen weichen Trennstrich braucht -- und klein darunter `wort` und
 * die Werte der Felder `werte`, soweit sie gelten: «φ_k = 30°, c_k = 0
 * kN/m²». Das Fenster heisst wie die Gruppe oder `fenster` und zeigt `vor`,
 * ihre Zeilen und `nach`. `fehlt` sagt grau auf der Kachel, was ihr noch
 * fehlt, etwa «kein Beton».
 *
 * Eine Gruppe, die nach den Wahlen nichts zu zeigen hat, wird keine Kachel
 * (null) -- etwa die Sohlreibung im undrainierten Boden.
 */
export function gruppenkapitel(vorgaben, titel, {
  zeichen, name = titel, fenster: fenstertitel = titel, wort = '', werte = [], vor = [],
  nach = [], hilfe = null, fehlt = '',
}) {
  const zeilen = [...vor, ...vorgaben.zeilen(titel), ...nach].filter(Boolean);
  if (!zeilen.length) return null;
  const teile = [wort, ...vorgaben.werte(titel, werte).map(kachelwert)].filter(Boolean);
  return {
    schluessel: zeichen,
    name,
    titel: fenstertitel,
    hilfe,
    inhalt: () => [karte('', zeilen)],
    stand: () => standOhne({ an: true, text: teile.flatMap((t, i) => (i ? [', ', t] : [t])) }, fehlt),
  };
}

/** Ein Wert auf einer Kachel: «φ_k = 30°» -- er bricht nicht um, nur zwischen zweien. */
function kachelwert({ zeichen, wert, einheit }) {
  return el('span.kachel-wert', {}, [
    span(`${zeichen} = ${wert}`), einheit === '°' || !einheit ? einheit : ` ${einheit}`,
  ]);
}

function kachel(eintrag, kapitel) {
  const { an, text } = kapitel.stand(eintrag);
  return el('button.kachel', {
    type: 'button', class: an ? 'ist-an' : '', title: kapitel.titel,
    'aria-haspopup': 'dialog',
    on: { click: () => fensterOeffnen(kapitel.schluessel) },
  }, [
    sinnbild(kapitel.schluessel),
    el('span.kachel-name', {}, mitIndex(kapitel.name)),
    el('span.kachel-stand', {}, Array.isArray(text) ? text : [text]),
  ]);
}

/**
 * Das Panel der Knöpfe: je Gruppe `{titel, kapitel}` eine Überschrift und
 * ihre Knöpfe -- ohne Titel ohne Überschrift. `schluessel` merkt sich, ob
 * das Panel zugeklappt ist.
 */
export function kapitelPanel(eintrag, gruppen, { schluessel, titel }) {
  return panel({ schluessel, titel }, gruppen.flatMap((g) => [
    g.titel ? el('div.kachel-gruppe', { text: g.titel }) : null,
    el('div.kacheln', {}, g.kapitel.map((k) => kachel(eintrag, k))),
  ]));
}

/**
 * Das offene Fenster eines Bauteils -- oder null, wenn der Schlüssel zu
 * keinem seiner Kapitel gehört. Unter dem Titel steht der Name des Bauteils
 * und, wo Schnittgrössen eingegeben werden, worauf sie sich beziehen. Ein
 * Fragezeichen hat es, wo das Kapitel eine Hilfe mitbringt -- die Analysen
 * und die Suche haben keine.
 */
export function kapitelFenster(eintrag, gruppen, schluessel) {
  const kapitel = gruppen.flatMap((g) => g.kapitel).find((k) => k.schluessel === schluessel);
  if (!kapitel) return null;
  const { hilfe } = kapitel;
  return fenster({
    titel: kapitel.titel,
    zeichen: kapitel.schluessel,
    zusatz: [eintrag.name, kapitel.bezug?.(eintrag)].filter(Boolean).join(' · '),
    hilfe: hilfe ? erklaerung(hilfe.zeilen, hilfe.formel) : null,
    inhalt: kapitel.inhalt(eintrag),
    breit: !!kapitel.breit,
  });
}
