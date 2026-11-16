/**
 * bs_texte.js -- was ein Balkensystem erklärt, eben und im Raum.
 *
 * Die Hilfen der Eingaben (`HILFE`), die Titel einiger Felder des
 * schwebenden Fensters und das kleine Bild der Vorzeichen -- je Art eines
 * Balkensystems, unter ihrem Namen (`texte(art)`). Was beide gleich haben,
 * steht einmal da. Alles andere -- welche Felder, Richtungen und Grössen es
 * gibt -- sagt der Katalog des Kerns; hier stehen nur Worte und ein Bild.
 */

import { svgEl } from './dom.js';

const GEMEINSAM = {
  fall: ['Fall', 'ein Lastfall oder eine Kombination -- gerechnet wird jeder Fall'],
  angeschrieben: ['Angeschrieben', 'die Werte an den Enden und je Stab die grössten, mit Punkt und Stelle'],
  material: [
    ['Beton', 'einer aus dem Projekt: E = E_cm und ρ des Stahlbetons, die Bewehrung steckt darin -- zu ändern in der App «Materialien»'],
    ['Baustahl', 'einer aus dem Projekt: E = E_a und ρ_a (SIA 263:2013, 3.2.2.1)'],
  ],
  rho: ['ρ', 'für das Eigengewicht ρ · g · A, mit g = 10 m/s²'],
};

/** Ein kleines Bild der Vorzeichen in der Ebene: Achsen, Drehsinn, ein Stab mit Faser, M > 0. */
function vorzeichenbildEben() {
  const { s, pfeil, text } = bildMit('0 0 300 92');
  s.append(
    pfeil('M20 70 H70 M64 66 L70 70 L64 74'), text(74, 74, 'x'),
    pfeil('M20 70 V20 M16 26 L20 20 L24 26'), text(16, 14, 'z'),
    svgEl('path', { d: 'M48 40 A12 12 0 1 0 36 52', class: 'bs-vz-pfeil' }),
    pfeil('M36 52 L42 50 M36 52 L39 46'), text(52, 38, 'φ, M ↺'),
    svgEl('path', { d: 'M120 46 H270', class: 'bs-vz-stab' }),
    svgEl('path', { d: 'M135 51 H255', class: 'bs-vz-faser' }),
    text(120, 36, 'Anfang'), text(240, 36, 'Ende'),
    pfeil('M195 14 V40 M191 34 L195 40 L199 34'), text(201, 22, 'Last ↓ positiv'),
    text(150, 68, 'gestrichelte Faser: die Zugseite'),
    text(150, 84, 'M > 0 zieht dort · N > 0 ist Zug'),
  );
  return s;
}

/**
 * Ein kleines Bild der Vorzeichen im Raum: die Achsen des Systems, wie die
 * Zeichnung sie schräg von oben zeigt -- x nach rechts unten, y nach rechts
 * oben, z nach oben --, und ein Stab mit seinen Achsen: x längs, z nach
 * unten zur gestrichelten Faser, y auf den Betrachter zu.
 */
function vorzeichenbildRaum() {
  const { s, pfeil, text } = bildMit('0 0 300 100');
  // Ein Pfeil von (x, y) in Richtung (dx, dy), `l` lang, mit Spitze.
  const achse = (x, y, [dx, dy], l, name) => {
    const [ex, ey] = [x + dx * l, y + dy * l];
    const [nx, ny] = [-dy, dx];
    const spitze = (seite) => `${(ex - dx * 6 + nx * 3.5 * seite).toFixed(1)} ${(ey - dy * 6 + ny * 3.5 * seite).toFixed(1)}`;
    return [pfeil(`M${x} ${y} L${ex.toFixed(1)} ${ey.toFixed(1)} M${spitze(1)} L${ex.toFixed(1)} ${ey.toFixed(1)} L${spitze(-1)}`),
      text(ex + dx * 9 - 3, ey + dy * 9 + 4, name)];
  };
  s.append(
    ...achse(30, 66, [0.92, 0.39], 40, 'x'),
    ...achse(30, 66, [0.86, -0.51], 36, 'y'),
    ...achse(30, 66, [0, -1], 40, 'z'),
    text(14, 92, 'Drehung im Rechtssinn'),
    svgEl('path', { d: 'M140 34 H285', class: 'bs-vz-stab' }),
    svgEl('path', { d: 'M150 39 H275', class: 'bs-vz-faser' }),
    text(140, 22, 'Anfang'), text(258, 22, 'Ende'),
    ...achse(182, 34, [1, 0], 26, 'x'),
    ...achse(182, 34, [0, 1], 24, 'z'),
    svgEl('circle', { cx: 166, cy: 52, r: 4.5, class: 'bs-vz-pfeil' }),
    svgEl('circle', { cx: 166, cy: 52, r: 1.2, class: 'bs-vz-punkt' }),
    text(150, 56, 'y'),
    text(218, 58, 'Faser auf der Seite von z'),
    text(218, 74, 'M_y > 0 zieht dort'),
    text(218, 90, 'N > 0 ist Zug'),
  );
  return s;
}

function bildMit(viewBox) {
  const s = svgEl('svg', { viewBox, class: 'bs-vorzeichen', role: 'img', 'aria-label': 'Vorzeichen' });
  const pfeil = (d) => svgEl('path', { d, class: 'bs-vz-pfeil' });
  const text = (x, y, t, k = '') => {
    const e = svgEl('text', { x, y, class: `bs-vz-text ${k}` });
    e.textContent = t;
    return e;
  };
  return { s, pfeil, text };
}

const TEXTE = {
  balkensystem: {
    zusatz: 'x nach rechts, z nach oben, m',
    vorzeichenbild: vorzeichenbildEben,
    kraftrichtung: 'Positiv in Pfeilrichtung: senkrecht nach unten, quer zur gestrichelten Faser, längs vom Anfang zum Ende',
    momentsinn: 'Ein Moment positiv im Gegenuhrzeigersinn',
    projiziert: 'Senkrecht und waagrecht je Meter Projektion statt je Meter Stab',
    gelenk: 'Kein Moment',
    hilfe: {
      vorzeichen: {
        zeilen: [
          ['Achsen', 'x nach rechts, z nach oben; Verschiebungen positiv entlang der Achsen'],
          ['Drehung', 'im Gegenuhrzeigersinn positiv, ebenso Momentlasten'],
          ['Lasten', 'positiv in Pfeilrichtung: senkrecht nach unten, waagrecht nach rechts, quer zur gestrichelten Faser, längs vom Anfang zum Ende'],
          ['N, V, M', 'nach Baustatik: N > 0 Zug, M > 0 zieht an der gestrichelten Faser, dM/dx = V − m'],
          ['Faser', 'die Zugseite: an einer neuen Linie unten, an einer senkrechten links -- im Fenster des Stabs umzuschalten; die Lasten bleiben dabei, wo sie wirken'],
        ],
        formel: 'Lagerkraft nach oben positiv',
      },
      materialien: {
        zeilen: [
          ...GEMEINSAM.material,
          ['eigenes', 'E und ρ von Hand, etwa für Holz'],
          GEMEINSAM.rho,
          ['gemäss Querschnitt', 'wählt man an der Linie: der Beton ihrer Platte oder Analyse'],
        ],
        formel: 'g_k = ρ · g · A   g = 10 m/s²',
      },
      querschnitte: {
        zeilen: [
          ['Vorlage', 'A und I nach den Formeln der Vorlage, Masse in mm'],
          ['Profil', 'ein Stahlprofil aus der Tabelle -- A und I_y oder I_z aus seinen Massen, in cm² und cm⁴; y ist die starke Achse, der Steg liegt dann in der Ebene des Rahmens'],
          ['Platte', 'ein Streifen b × h der gewählten Platte'],
          ['Aus QS Analyse', 'A und I_y des Bruttoquerschnitts der gewählten Querschnittsanalyse'],
          ['E-Modul', 'vom Material des Stabs -- «gemäss Querschnitt» E₀ = E_cm des Betons der Platte oder Analyse, bei einer Analyse auf Wunsch E_eq bei N und M, für EA und EI (für EA eine Näherung)'],
          ['E_eq', 'wie die Linie M–E_eq der Spannung-Dehnung-Analyse: ungerissen bis zum Rissmoment, darüber gerissen; M > 0 zieht unten -- bei einer Platte immer in x-Richtung, Zug unten'],
          ['Steifigkeit', 'EA, EI am Bruttoquerschnitt, beim Beton ungerissen und ohne Bewehrung (SIA 262:2025, 4.1.4.1.3); Theorie 1. Ordnung'],
        ],
        formel: 'EA = E · A   EI = E · I',
      },
      statik: {
        zeilen: [
          GEMEINSAM.fall,
          ['M, V, N', 'je Stab der Verlauf, positiv auf der Seite der gestrichelten Faser'],
          ['Verschiebung', 'das verschobene System, überhöht -- je Stab die grösste Durchbiegung gegen die Sehne, kurzzeitig und ungerissen; die Norm misst gegenüber den Auflagern (SIA 262:2025, 4.4.3.1.1)'],
          ['Verdrehung', 'je Stab die Verdrehung φ des Querschnitts in mrad, im Gegenuhrzeigersinn positiv'],
          ['Lager', 'die Lagerkräfte auf das Tragwerk'],
          GEMEINSAM.angeschrieben,
        ],
      },
    },
  },
  balkensystem3d: {
    zusatz: 'x und y waagrecht, z nach oben, m',
    vorzeichenbild: vorzeichenbildRaum,
    kraftrichtung: 'Positiv in Pfeilrichtung: senkrecht nach unten, in x, y oder z des Systems, längs vom Anfang zum Ende, quer in y oder z des Stabs',
    momentrichtung: 'Um welche Achse das Moment dreht: senkrecht nach unten, x, y oder z des Systems, längs -- ein Torsionsmoment -- oder quer in y oder z des Stabs',
    momentsinn: 'Ein Moment positiv im Rechtssinn um seine Drehachse',
    projiziert: 'In einer Richtung des Systems je Meter Projektion statt je Meter Stab -- wie Schnee auf einem geneigten Dach',
    gelenk: 'Keine Momente, wie ein Kugelgelenk',
    hilfe: {
      vorzeichen: {
        zeilen: [
          ['Achsen', 'x und y waagrecht, z nach oben, ein Rechtssystem; Verschiebungen positiv entlang der Achsen'],
          ['Drehung', 'im Rechtssinn um ihre Achse, ebenso Momentlasten'],
          ['Lasten', 'positiv in Pfeilrichtung: senkrecht nach unten, in x, y oder z des Systems, längs vom Anfang zum Ende, quer in y oder z des Stabs'],
          ['Stab', 'x vom Anfang zum Ende, z nach unten in der lotrechten Ebene durch den Stab, y = z × x; an einem lotrechten Stab ist y die Achse −y des Systems. Der Drehwinkel β dreht y und z im Rechtssinn um x'],
          ['N, V, M, T', 'N > 0 Zug; M_y > 0 zieht an der gestrichelten Faser, auf der Seite von z; M_z > 0 an der Seite von y; T dreht im Rechtssinn um x'],
          ['Faser', 'auf der Seite von z: an einem Stab, der waagrecht liegt, unten -- «Umkehren» tauscht Anfang und Ende und dreht β so, dass der Querschnitt bleibt, wie er steht'],
          ['Ansicht', 'drehen: mit der rechten Maustaste ziehen, oder mit der linken bei gedrückter Alt-Taste -- Alt mit einem Klick setzt einen Punkt ohne Fangen; oder ein Knopf: 3D, x-y, x-z, y-z; E legt die Arbeitsebene durch den gefangenen Punkt'],
        ],
        formel: 'Lagerkraft positiv entlang der Achsen des Systems',
      },
      materialien: {
        zeilen: [
          ...GEMEINSAM.material,
          ['G', 'der Schubmodul für die Torsion: G_cm = E_cm / (2 · (1 + ν_c)) des Betons, G_a des Baustahls (SIA 263:2013, 3.2.2.1)'],
          ['eigenes', 'E, ρ und G von Hand, etwa für Holz'],
          GEMEINSAM.rho,
        ],
        formel: 'g_k = ρ · g · A   g = 10 m/s²',
      },
      querschnitte: {
        zeilen: [
          ['Vorlage', 'A, I_y, I_z und I_T nach den Formeln der Vorlage, Masse in mm'],
          ['Profil', 'ein Stahlprofil aus der Tabelle -- y ist die starke Achse; bei β = 0 steht der Steg in der lotrechten Ebene des Stabs, gedreht wird mit dem Drehwinkel β der Linie'],
          ['Kennwerte', 'A, I_y, I_z und I_T von Hand'],
          ['Steifigkeit', 'EA, EI_y, EI_z und GI_T am Bruttoquerschnitt, beim Beton ungerissen und ohne Bewehrung (SIA 262:2025, 4.1.4.1.3); Theorie 1. Ordnung, Torsion nach St. Venant ohne Wölbkrafttorsion'],
        ],
        formel: 'EA = E · A   EI_y = E · I_y   GI_T = G · I_T',
      },
      statik: {
        zeilen: [
          GEMEINSAM.fall,
          ['N, V, M, T', 'je Stab der Verlauf: M_y und V_z zur Seite von z des Stabs, M_z und V_y zur Seite von y; N und T dort, wo man sie besser sieht'],
          ['Verschiebung', 'das verschobene System, überhöht -- je Stab die grössten Durchbiegungen f_y und f_z gegen die Sehne, kurzzeitig und ungerissen'],
          ['Lager', 'die Lagerkräfte und -momente auf das Tragwerk'],
          ['Ansicht', 'über jedem Diagramm: 3D, x-y, x-z oder y-z -- nur fürs Auge, sie wird nicht gespeichert'],
          GEMEINSAM.angeschrieben,
        ],
      },
    },
  },
};

/** Die Texte einer Art von Balkensystem. */
export function texte(art) {
  return TEXTE[art];
}
