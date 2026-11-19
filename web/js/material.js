/**
 * material.js -- der Editor eines Materials: Bezeichnung und Kennwerte.
 *
 * NORMSORTE ODER EIGENES MATERIAL:
 * Eine Normsorte nach SIA ist gesperrt -- kein Feld lässt sich anfassen, auch
 * die Sorte nicht. Wer abweichen will, legt ein eigenes Material an
 * (materialwahl.js): es heisst BE1, S1 oder ST1 und ist änderbar. So kann keine
 * abgewandelte Festigkeit unter einer Normbezeichnung im Bericht landen.
 *
 * Angezeigt wird immer der Wert aus der letzten Lösung, nie ein in der
 * Oberfläche nachgerechneter. Bis 2026-10-18 stand der Editor in editor.js,
 * zusammen mit dem der Platte.
 */

import { feld, namensfeld, panel } from './bausteine.js';
import { el, zahlfeld } from './dom.js';
import { span } from './mathe.js';
import { eintragAendern, katalog, kennwertId, zustand } from './zustand.js';

function gerechnet(id) {
  return zustand.loesung?.werte?.[id] || null;
}

/**
 * Ein Kennwert eines Materials als Zeile: bei einer Normsorte gesperrt, bei
 * einem eigenen änderbar, ein gerechneter mit Haken zum Überschreiben.
 */
function kennwertZeile(material, vorlage) {
  const gesperrt = !material.eigenstaendig;
  const wert = gerechnet(kennwertId(material, vorlage.kurzname));
  const istUeberschrieben = vorlage.kurzname in material.ueberschreibungen;
  const istAbweichend = vorlage.kurzname in material.abweichungen;

  let anzeige = null;
  if (istUeberschrieben) anzeige = material.ueberschreibungen[vorlage.kurzname];
  else if (istAbweichend) anzeige = material.abweichungen[vorlage.kurzname];
  else if (wert) anzeige = Number(wert.zahl.toFixed(vorlage.stellen));

  const schreibbar = !gesperrt && (!vorlage.berechnet || istUeberschrieben);

  const eingabe = zahlfeld({
    wert: anzeige,
    schritt: vorlage.stellen >= 3 ? 0.001 : (vorlage.stellen >= 1 ? 0.1 : 1),
    // Über null, wie der Kern es verlangt: bis 2026-11-19 führten die
    // Pfeile bis 0, und das Material rechnete nicht mehr.
    angabe: vorlage.angabe,
    readonly: !schreibbar,
    titel: gesperrt ? 'Normsorte nach SIA – nicht änderbar'
      : (vorlage.berechnet && !istUeberschrieben ? 'Wird gerechnet. Haken setzen zum Überschreiben.' : ''),
    // Leer: die eigene Zahl weg, der Wert der Sorte gilt wieder.
    leer: null,
    beiAenderung: (neu) => eintragAendern(material.kennung, (m) => {
      const topf = vorlage.berechnet ? m.ueberschreibungen : m.abweichungen;
      if (neu === null) delete topf[vorlage.kurzname];
      else topf[vorlage.kurzname] = neu;
    }),
  });

  // Überschrieben wird der gerechnete Wert. Fehlt er, weil das Material
  // nicht rechnet, gibt es nichts zu überschreiben -- bis 2026-11-19 setzte
  // der Haken dann eine 0, die der Kern abweist.
  const ohneWert = !istUeberschrieben && anzeige === null;
  const schalter = vorlage.berechnet
    ? el('input', {
      type: 'checkbox', checked: istUeberschrieben, disabled: gesperrt || ohneWert,
      title: gesperrt ? 'Normsorte nach SIA – nicht änderbar'
        : (ohneWert ? 'Noch kein gerechneter Wert – überschreiben lässt er sich, sobald er gerechnet ist'
          : 'Von Hand überschreiben'),
      on: {
        change: (e) => eintragAendern(material.kennung, (m) => {
          if (e.target.checked) m.ueberschreibungen[vorlage.kurzname] = anzeige;
          else delete m.ueberschreibungen[vorlage.kurzname];
        }),
      },
    })
    : el('span');

  const zuruecksetzen = (istAbweichend && !vorlage.berechnet && !gesperrt)
    ? el('button.knopf.knopf-zart', {
      text: '↺', title: 'Sortenwert zurücksetzen',
      on: {
        click: () => eintragAendern(material.kennung, (m) => {
          delete m.abweichungen[vorlage.kurzname];
        }),
      },
    })
    : el('span');

  return el('div.kennwert', {
    class: istUeberschrieben ? 'ist-ueberschrieben' : '',
    title: [vorlage.beschreibung, vorlage.referenz].filter(Boolean).join(' — '),
  }, [
    schalter,
    el('span.bezeichnung', {}, [span(vorlage.symbol), ' ', el('small', { text: vorlage.beschreibung })]),
    eingabe,
    el('span.einheit', { text: vorlage.einheit === '-' ? '' : vorlage.einheit }),
    zuruecksetzen,
  ]);
}

export function materialEditor(material) {
  const vorlagen = katalog('materialarten', material.art, 'kennwerte');
  const gesperrt = !material.eigenstaendig;
  const anzahlUeberschrieben = Object.keys(material.ueberschreibungen).length;

  // Eine Normsorte bleibt, wie sie ist -- es gibt keinen Weg, sie zu ändern,
  // auch nicht ihre Sorte (Benutzer, 2026-10-16). Ein eigenes Material trägt
  // keine Sorte; seine Vorlage zählt nur beim Anlegen.
  const kopf = gesperrt
    ? el('div.gesperrt-hinweis', {}, [
      el('span.sia', { text: 'SIA' }),
      el('div', { style: { flex: '1 1 220px' } }, [
        el('b', { text: `Normsorte ${material.sorte}` }),
        ` · ${katalog('materialarten', material.art, 'grundlage')}; nicht `
        + 'änderbar. Abweichen: links «+» → eigenes Material.',
      ]),
    ])
    : el('div.gesperrt-hinweis', {
      style: { background: 'var(--warn-hell)', borderColor: 'var(--warn)' },
    }, [
      el('div', { style: { flex: '1 1 220px' } }, [
        el('b', { text: 'Eigenes Material' }),
        ' · Die Kennwerte sind änderbar und entsprechen nicht zwingend der Norm.',
      ]),
    ]);

  return [
    kopf,
    panel({ schluessel: 'material/Material', titel: 'Material' }, [
      feld('Bezeichnung', namensfeld({
        wert: material.name || material.sorte, gesperrt,
        titel: gesperrt ? 'Eine Normsorte trägt zwingend ihre Sortenbezeichnung' : '',
        pruefen: (name) => {
          if (katalog('materialarten', material.art, 'anlegen').includes(name)) {
            return `Den Namen «${name}» trägt eine Normsorte`;
          }
          return vergeben(material, name) ? `Den Namen «${name}» trägt schon ein anderes Material` : '';
        },
        setzen: (name) => eintragAendern(material.kennung, (m) => { m.name = name; }),
      })),
    ]),

    panel({ schluessel: 'material/Grundwerte', titel: 'Grundwerte', zusatz: 'Sortentabelle, Norm' },
      vorlagen.filter((v) => !v.berechnet).map((v) => kennwertZeile(material, v))),

    panel({
      schluessel: 'material/Abgeleitete Kennwerte',
      titel: 'Abgeleitete Kennwerte',
      zusatz: anzahlUeberschrieben
        ? el('button.knopf.knopf-zart', {
          text: `${anzahlUeberschrieben} überschrieben — zurücksetzen`,
          on: {
            click: () => eintragAendern(material.kennung, (m) => { m.ueberschreibungen = {}; }),
          },
        })
        : (gesperrt ? 'gesperrt' : 'Haken setzen zum Überschreiben'),
    }, vorlagen.filter((v) => v.berechnet).map((v) => kennwertZeile(material, v))),
  ];
}

/**
 * Ob ein anderes Material schon so heisst. Zwei gleich benannte hielten das
 * ganze Projekt an -- im Bericht liesse sich nicht erkennen, welches gemeint
 * ist (`Projekt.regeln`); darum weist schon das Feld den Namen ab. Ebenso
 * den einer Normsorte: ein eigenes Material darf nicht so heissen
 * (`MaterialEintrag.regeln`), bis 2026-11-19 merkte man es erst am Bauteil,
 * das nicht mehr rechnete.
 */
function vergeben(material, name) {
  return zustand.projekt.materialien
    .some((m) => m.kennung !== material.kennung && (m.name || m.sorte) === name);
}

/** Was über dem Editor steht: die Art, und ob es eine Normsorte ist. */
export function materialHinweis(material) {
  return katalog('materialarten', material.art, 'titel')
    + (material.eigenstaendig ? ' · eigenes Material' : ' · Normsorte SIA');
}
