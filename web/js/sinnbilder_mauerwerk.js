/**
 * sinnbilder_mauerwerk.js -- die Zeichen der Wand aus Mauerwerk.
 *
 * Gebaut wie die Zeichen in sinnbilder.js -- 24 × 24, Pfade, Kreise, volle
 * Flächen, gestrichelt, was nur eine Grenze meint --, und dort unter ihrem
 * Namen zu haben (`sinnbild`). Eine eigene Datei, damit sinnbilder.js nicht
 * über 1000 Zeilen wächst: ihr Knopf links, die Werkzeuge des
 * Zeichenfensters, ihre Kacheln und die Bilder ihrer Schalter. Ein Plan
 * zeigt Mauerwerk in der Ansicht, Stein auf Stein; wie es über die Dicke
 * gemauert ist und wie ein Rand gehalten ist, sieht man von oben.
 *
 * Ohne Imports: tests/test_bauteilarten.py liest die Namen aus dem Text.
 */

export const ZEICHEN = {
  // -- Der Knopf links und die Werkzeuge ------------------------------------

  // Eine Wand Stein auf Stein, die Fugen versetzt, unten eine Türe.
  mauerwerk: {
    pfade: ['M3 4h18v16H3z', 'M3 8h18 M3 12h18 M3 16h6 M15 16h6', 'M9 12v8 M15 12v8',
      'M9 4v4 M15 4v4 M6 8v4 M12 8v4 M18 8v4 M6 12v4 M18 12v4'],
  },
  // Eine Wand: ein Rechteck aus zwei Ecken, darin Steine.
  'cad-mauer': {
    pfade: ['M3.5 19V5h17v14z', 'M3.5 9.7h17 M3.5 14.3h17',
      'M9 5v4.7 M15 5v4.7 M12 9.7v4.6 M9 14.3V19 M15 14.3V19'],
    voll: [[3.5, 19, 1.5], [20.5, 5, 1.5]],
  },
  // Eine Öffnung: ein Rechteck aus zwei Ecken in der Wand, darüber ihr Sturz.
  'cad-oeffnung': {
    pfade: ['M3 21V3h18v18', 'M8.5 21V11h7v10', 'M7 8h10v3H7z'],
    voll: [[8.5, 21, 1.4], [15.5, 11, 1.4]],
  },

  // -- Die Kacheln -------------------------------------------------------

  // Die Wand im Schnitt, Stein auf Stein, darunter ihre Dicke.
  'mw-wand': {
    pfade: ['M8 3h8v14H8z', 'M8 6.5h8 M8 10h8 M8 13.5h8', 'M8 20.5h8 M8 19v3 M16 19v3'],
  },
  // Die Wand in der Ansicht, oben und unten gehalten, gestrichelt die Ränder links und rechts.
  'mw-raender': {
    pfade: ['M7 6h10v12H7z', 'M4 6h16 M6 6l2-3 M10 6l2-3 M14 6l2-3 M18 6l2-3',
      'M4 18h16 M6 21l2-3 M10 21l2-3 M14 21l2-3 M18 21l2-3'],
    strich: ['M4 8.5v7 M20 8.5v7'],
  },
  // Die Wand im Schnitt, von der Seite gedrückt: Pfeile quer zu ihr.
  'mw-querlasten': {
    pfade: ['M14 3h5.5v18H14z', 'M14 7.5h5.5 M14 12h5.5 M14 16.5h5.5',
      'M3 7h8.5 M9.2 4.9l2.3 2.1-2.3 2.1', 'M3 12h8.5 M9.2 9.9l2.3 2.1-2.3 2.1',
      'M3 17h8.5 M9.2 14.9l2.3 2.1-2.3 2.1'],
  },

  // -- Die Stellungen der Schalter -----------------------------------------

  // Von oben: ein Stein über die ganze Dicke, Stoss an Stoss.
  'mauerung-einstein': {
    pfade: ['M2.5 9h19v6h-19z', 'M8.5 9v6 M15.5 9v6'],
  },
  // Von oben: zwei Steine über die Dicke, ihre Fugen versetzt, ein Binder quer durch beide.
  'mauerung-verband': {
    pfade: ['M2.5 7h19v10h-19z', 'M2.5 12h7.5 M14 12h7.5', 'M10 7v10 M14 7v10', 'M6 7v5 M18 12v5'],
  },
  // Zwei Lagen Steine, die Lagerfuge dazwischen voll Mörtel, die Stossfugen leer.
  'stossfugen-nicht_vollfugig': {
    pfade: ['M2.5 5h19v14h-19z'],
    flaechen: ['M2.5 11.3h19v1.4h-19z'],
    strich: ['M9 5v6.3 M15 12.7V19'],
  },
  // Dieselben Lagen, auch die Stossfugen voll Mörtel.
  'stossfugen-vollfugig': {
    pfade: ['M2.5 5h19v14h-19z'],
    flaechen: ['M2.5 11.3h19v1.4h-19z M8.3 5h1.4v6.3H8.3z M14.3 12.7h1.4V19h-1.4z'],
  },
  // Das Ende der Wand auf einem Gelenk, darunter der Grund: es kann sich drehen.
  'halterung-gelenkig': {
    pfade: ['M9.5 3v10 M14.5 3v10 M9.5 13h5', 'M3.5 18.5h17',
      'M6 18.5l-2.5 3 M10 18.5l-2.5 3 M14 18.5l-2.5 3 M18 18.5l-2.5 3'],
    kreise: [[12, 15.8, 2.5]],
  },
  // Das Ende der Wand fest im Grund: es kann sich nicht drehen.
  'halterung-eingespannt': {
    pfade: ['M9.5 3v12.5 M14.5 3v12.5', 'M3.5 15.5h17',
      'M4 20l3.5-4.5 M8.5 20l3.5-4.5 M13 20l3.5-4.5 M17.5 20l3-3.9'],
  },
  // Von oben: die Wand endet frei -- quer zu ihr kann ihr Rand ausweichen.
  'seitenrand-frei': {
    pfade: ['M2.5 10h14v4h-14z', 'M19.5 7v10 M18 15.5l1.5 1.5 1.5-1.5 M18 8.5L19.5 7 21 8.5'],
  },
  // Von oben: eine Querwand hält den Rand der Wand.
  'seitenrand-gehalten': {
    pfade: ['M2.5 10h14v4h-14z', 'M16.5 4h4v16h-4z'],
  },
  // Über der Öffnung ein Balken aus Beton, Kies darin, beidseits aufgelegt.
  'sturz-beton': {
    pfade: ['M3 7h18v4.5H3z', 'M6.5 11.5V21 M17.5 11.5V21'],
    kreise: [[7, 9.2, 0.7], [11.5, 9.2, 0.7], [16, 9.2, 0.7]],
  },
  // Über der Öffnung ein dünnes Sturzbrett, darauf Mauerwerk, das mitträgt.
  'sturz-vorfabriziert': {
    pfade: ['M3 10h18v2H3z', 'M3 10V3.5h18V10 M3 6.8h18 M8 3.5v3.3 M16 3.5v3.3 M12 6.8V10',
      'M6.5 12V21 M17.5 12V21'],
  },
};
