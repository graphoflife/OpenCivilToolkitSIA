/**
 * dk_schnitt.js -- das Bild längs eines Schnitts durch eine Decke.
 *
 * Ein Schnitt ist eine Linie im Grundriss (dk_zeichnung.js). Sein Bild
 * zeigt eine Grösse der Platte längs ihm wie an einem Balken des
 * Balkensystems (Benutzer, 2026-11-16) -- ebenso das Bild eines Trägers
 * sein M oder V, auf den Lagern, auf denen er liegt --, in zwei Zeilen:
 *
 *   oben    die Achse mit den Lagern, die er kreuzt -- Linienlager und
 *           Stützen ein Dreieck, eingespannt ein Balken mit Schraffur, eine
 *           Symmetrieachse strichpunktiert --, die Träger als Band;
 *           neben den Platten ist die Achse gestrichelt;
 *   unten   der Verlauf, positive Werte unten: das Moment auf der Zugseite,
 *           wie im Balkensystem an der gestrichelten Faser. Neben den
 *           Platten ist er unterbrochen; wo ein Lager steht, quert ein
 *           Strich seine Achse.
 *
 * Angeschrieben sind die Werte an den Enden der Stücke in einer Platte und
 * der grösste und der kleinste, mit Punkt und ihrer Stelle s ab dem Anfang
 * des Schnitts. Beschriftung und Zeiger teilt das Bild mit dem
 * Balkensystem (bs_diagramme.js).
 *
 * Gerechnet wird hier nichts: Stellen, Werte, Extremwerte und Lager kommen
 * fertig aus dem Kern (opencivil/decke/schnitt.py). An einem Sprung stehen
 * zwei Werte an derselben Stelle -- der Verlauf steht dort senkrecht. Für
 * den Zeiger wird zwischen den dichten Proben nur gerade verbunden.
 */

import { anschreiben, pfad, zeigerEinrichten } from './bs_diagramme.js';
import { lagerSymbol } from './bs_symbole.js';
import { zahlText } from './cad_ansicht.js';
import { el, svgEl } from './dom.js';

const BREITE = 640;
/** Platz links und rechts der Achse, in Bildpunkten: für die Werte an den Enden. */
const SEITE = 48;
/** So weit steht der grösste Wert von der Achse ab, in Bildpunkten. */
const AUSSCHLAG = 64;
/** Über und unter dem Verlauf Platz für seine Werte -- eine Zahl und ihre Stelle. */
const ZAHLEN = 32;
/** Unter der Achse des Systems Platz für die Lager und ihre Namen, in Bildpunkten. */
const SYSTEM_UNTEN = 44;
/** Ein Träger ist ein Band so hoch, in Bildpunkten -- darüber je Zeile ein Name. */
const BAND = 12;
const NAMENSZEILE = 12;
/** Stellen der angeschriebenen Werte. */
const STELLEN = 1;

/** Die Farbe eines Verlaufs: Momente -- m_x der Platte, M eines Trägers -- wie M, Querkräfte wie V im Balkensystem. */
const familie = (groesse) => (/^m/i.test(groesse) ? 'bs-d-m' : 'bs-d-v');

function schrift([x, y], inhalt, klasse, anker = 'middle') {
  const t = svgEl('text', { x: x.toFixed(1), y: y.toFixed(1), class: klasse, 'text-anchor': anker });
  t.textContent = inhalt;
  return t;
}

const strich = (p, q, klasse) => svgEl('path', { d: pfad([p, q]), class: klasse });

/**
 * Die Lager an derselben Stelle als eines -- wo der Schnitt durch eine Ecke
 * zweier Wände geht: es hält, was eines von ihnen hält.
 */
function lagerstellen(lager) {
  const heraus = [];
  for (const l of lager) {
    const da = heraus.find((x) => x.u === l.u);
    if (da) {
      da.namen.push(l.name);
      da.vertikal ||= l.vertikal;
      da.eingespannt ||= l.eingespannt;
    } else heraus.push({ u: l.u, namen: [l.name], vertikal: l.vertikal, eingespannt: l.eingespannt });
  }
  return heraus;
}

/**
 * Je Träger die Zeile seines Namens über den Bändern, von unten gezählt:
 * die erste, in der er keinen anderen deckt -- die schmalen zuerst, nahe
 * ihrem Band. Läuft der Schnitt in einem Träger, stünde dessen Name
 * sonst auf dem eines kreuzenden.
 */
function namenszeilen(traeger, X) {
  const belegt = [];
  const zeile = new Map();
  for (const u of [...traeger].sort((a, b) => (a.bis - a.von) - (b.bis - b.von))) {
    const mitte = (X(u.von) + X(u.bis)) / 2;
    const halb = u.name.length * 3.5 + 4;
    let i = belegt.findIndex((z) => z.every(([l, r]) => mitte + halb < l || mitte - halb > r));
    if (i < 0) i = belegt.push([]) - 1;
    belegt[i].push([mitte - halb, mitte + halb]);
    zeile.set(u, i);
  }
  return zeile;
}

/** Die Zeile des Systems: die Achse, die Träger und die Lager mit ihren Namen. */
function system(svg, s, X, y, yVerlauf, zeilen) {
  svg.append(strich([X(0), y], [X(s.L), y], 'dk-s-achse ist-daneben'));
  for (const [u0, u1] of s.stuecke) svg.append(strich([X(u0), y], [X(u1), y], 'dk-s-achse'));
  for (const u of s.traeger) {
    svg.append(svgEl('rect', {
      x: X(u.von).toFixed(1), y: (y - BAND / 2).toFixed(1), width: (X(u.bis) - X(u.von)).toFixed(1),
      height: BAND, class: 'dk-s-traeger',
    }), schrift([(X(u.von) + X(u.bis)) / 2, y - BAND / 2 - 4 - NAMENSZEILE * zeilen.get(u)], u.name, 'dk-s-name'));
  }
  for (const l of lagerstellen(s.lager)) {
    // Ein Lager, das nichts hält, zeigt nichts.
    if (!l.vertikal && !l.eingespannt) continue;
    const x = X(l.u);
    // Auf der Achse des Verlaufs ein Strich, wo das Lager steht -- ein Lot
    // dorthin liefe durch die Zahlen über ihm.
    svg.append(strich([x, yVerlauf - 5], [x, yVerlauf + 5], 'dk-s-marke'));
    svg.append(l.vertikal
      ? lagerSymbol([x, y], { x: 'fest', z: 'fest', phi: l.eingespannt ? 'fest' : 'frei' }, 'dk-s-lager')
      : strich([x, y - 14], [x, y + 22], 'dk-s-symmetrie'));
    svg.append(schrift([x, y + SYSTEM_UNTEN - 6], l.namen.join(', '), 'dk-s-name'));
  }
}

/** Je Stück in einer Platte seine Proben: `[u, Wert]`, aufsteigend. */
function stuecke(s, werte) {
  return s.stuecke.map(([u0, u1]) => s.stellen.map((u, i) => [u, werte[i]]).filter(([u]) => u >= u0 && u <= u1));
}

/** Der Wert an der Stelle u -- zwischen zwei Proben gerade verbunden; neben den Platten null. */
function wertBei(teile, u) {
  for (const proben of teile) {
    if (!proben.length || u < proben[0][0] || u > proben[proben.length - 1][0]) continue;
    for (let i = 1; i < proben.length; i += 1) {
      const [[ua, wa], [ub, wb]] = [proben[i - 1], proben[i]];
      if (u <= ub) return ub > ua ? wa + ((wb - wa) * (u - ua)) / (ub - ua) : wb;
    }
    return proben[proben.length - 1][1];
  }
  return null;
}

/**
 * Das Bild der Grösse `groesse` längs des Schnitts `s` -- wie der Kern ihn
 * schickt (deckendaten.py) --, `zeichen` und `einheit` für den Zeiger.
 * Gibt die Hülle mit dem Bild zurück.
 */
export function schnittbild(s, groesse, { zeichen, einheit }) {
  const werte = s.werte[groesse];
  const hoch = Math.max(0, ...werte);
  const tief = Math.min(0, ...werte);
  const weit = Math.max(hoch, -tief);
  const k = weit > 0 ? AUSSCHLAG / weit : 0;
  const kx = (BREITE - 2 * SEITE) / s.L;
  const X = (u) => SEITE + u * kx;
  const zeilen = namenszeilen(s.traeger, X);
  const ySystem = 12 + (zeilen.size ? BAND / 2 + 4 + NAMENSZEILE * Math.max(...zeilen.values()) + 10 : 0);
  const yVerlauf = ySystem + SYSTEM_UNTEN + (tief < 0 ? ZAHLEN - tief * k : 12);
  const Y = (w) => yVerlauf + w * k;
  const hoehe = Math.round(yVerlauf + hoch * k + (hoch > 0 ? ZAHLEN : 12));
  const svg = svgEl('svg', { viewBox: `0 0 ${BREITE} ${hoehe}`, class: 'bs-diagramm dk-s-bild' });
  system(svg, s, X, ySystem, yVerlauf, zeilen);

  const klasse = familie(groesse);
  const teile = stuecke(s, werte);
  for (const [[u0, u1], proben] of s.stuecke.map((st, i) => [st, teile[i]])) {
    svg.append(strich([X(u0), yVerlauf], [X(u1), yVerlauf], 'bs-d-system'));
    if (!proben.length) continue;
    const kurve = proben.map(([u, w]) => [X(u), Y(w)]);
    svg.append(svgEl('path', {
      d: `${pfad([[X(proben[0][0]), yVerlauf], ...kurve, [X(proben[proben.length - 1][0]), yVerlauf]])} Z`,
      class: `bs-d-flaeche ${klasse}`,
    }), svgEl('path', { d: pfad(kurve), class: `bs-d-kurve ${klasse}` }));
  }

  // Angeschrieben, was zählt: die Enden jedes Stücks, dann die Extremwerte im Feld.
  const zaehlt = (w) => Math.abs(w) >= weit * 0.01 && zahlText(Math.abs(w), STELLEN) !== '0';
  const seite = (w) => (w >= 0 ? [0, 1] : [0, -1]);
  const e = s.extreme[groesse];
  const spitzen = e ? [e.groesst, e.kleinst] : [];
  const enden = teile.flatMap((proben) => (proben.length ? [proben[0], proben[proben.length - 1]] : []));
  for (const [u, w] of enden) {
    if (!zaehlt(w)) continue;
    const spitze = spitzen.some((x) => x.u === u && x.wert === w);
    anschreiben(svg, [X(u), Y(w)], seite(w), zahlText(w, STELLEN), { punkt: spitze, klasse });
  }
  const gezeigt = [];
  for (const { u, wert: w } of spitzen) {
    if (!zaehlt(w) || enden.some(([ue]) => ue === u) || gezeigt.includes(u)) continue;
    gezeigt.push(u);
    anschreiben(svg, [X(u), Y(w)], seite(w), zahlText(w, STELLEN), { punkt: true, stelle: u, klasse, buchstabe: 's' });
  }

  const huelle = el('div.bs-diagramm-huelle', {}, [svg]);
  zeigerEinrichten(huelle, svg, ([px]) => {
    const u = (px - SEITE) / kx;
    if (u < -0.01 * s.L || u > 1.01 * s.L) return null;
    const am = Math.max(0, Math.min(s.L, u));
    const w = wertBei(teile, am);
    if (w === null) return { ort: [X(am), yVerlauf], text: [`s = ${zahlText(am, 2)} m`, 'neben den Platten'] };
    return { ort: [X(am), Y(w)], text: [`s = ${zahlText(am, 2)} m`, `${zeichen} = ${zahlText(w, STELLEN)} ${einheit}`] };
  });
  return huelle;
}
