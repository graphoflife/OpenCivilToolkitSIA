/**
 * material.js -- der Editor eines Materials: Bezeichnung und Kennwerte.
 *
 * NORMSORTE ODER EIGENES MATERIAL:
 * Eine Normsorte nach SIA ist gesperrt -- kein Feld lässt sich anfassen, auch
 * die Sorte nicht. Wer abweichen will, legt ein eigenes Material an
 * (materialwahl.js): es heisst BE1 oder S1 und ist änderbar. So kann keine
 * abgewandelte Festigkeit unter einer Normbezeichnung im Bericht landen.
 *
 * Angezeigt wird immer der Wert aus der letzten Lösung, nie ein in der
 * Oberfläche nachgerechneter. Bis 2026-10-18 stand der Editor in editor.js,
 * zusammen mit dem der Platte.
 */

import { feld, panel } from './bausteine.js';
import { el, melden, zahlfeld } from './dom.js';
import { span } from './mathe.js';
import { kennwertId, projektAendern, zustand } from './zustand.js';

/** Wie die Arten über dem Editor heissen. */
const ART_TEXT = { beton: 'Beton', betonstahl: 'Betonstahl' };

function gerechnet(id) {
  return zustand.loesung?.werte?.[id] || null;
}


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
    // Ein Baustoffkennwert ist nie negativ. Die Schnittgrössen daneben schon,
    // darum sagt es jedes Feld für sich und nicht die Pfeillogik für alle.
    min: 0,
    readonly: !schreibbar,
    titel: gesperrt ? 'Normsorte nach SIA – nicht änderbar'
      : (vorlage.berechnet && !istUeberschrieben ? 'Wird gerechnet. Haken setzen zum Überschreiben.' : ''),
    // Leer: die eigene Zahl weg, der Wert der Sorte gilt wieder.
    leer: null,
    beiAenderung: (neu) => projektAendern((p) => {
      const m = p.materialien.find((x) => x.kennung === material.kennung);
      const topf = vorlage.berechnet ? m.ueberschreibungen : m.abweichungen;
      if (neu === null) delete topf[vorlage.kurzname];
      else topf[vorlage.kurzname] = neu;
    }),
  });

  const schalter = vorlage.berechnet
    ? el('input', {
      type: 'checkbox', checked: istUeberschrieben, disabled: gesperrt,
      title: gesperrt ? 'Normsorte nach SIA – nicht änderbar' : 'Von Hand überschreiben',
      on: {
        change: (e) => projektAendern((p) => {
          const m = p.materialien.find((x) => x.kennung === material.kennung);
          if (e.target.checked) m.ueberschreibungen[vorlage.kurzname] = anzeige ?? 0;
          else delete m.ueberschreibungen[vorlage.kurzname];
        }),
      },
    })
    : el('span');

  const zuruecksetzen = (istAbweichend && !vorlage.berechnet && !gesperrt)
    ? el('button.knopf.knopf-zart', {
      text: '↺', title: 'Sortenwert zurücksetzen',
      on: {
        click: () => projektAendern((p) => {
          delete p.materialien.find((x) => x.kennung === material.kennung)
            .abweichungen[vorlage.kurzname];
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
  const vorlagen = zustand.katalog.kennwerte[material.art] || [];
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
        ' · Kennwerte nach SIA 262:2025, nicht änderbar. Abweichen: links «+» '
        + '→ eigenes Material.',
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
      feld('Bezeichnung', el('input', {
        type: 'text', value: material.name || material.sorte, disabled: gesperrt,
        title: gesperrt ? 'Eine Normsorte trägt zwingend ihre Sortenbezeichnung' : '',
        on: { change: (e) => nameAendern(material, e.target.value, e.target) },
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
            click: () => projektAendern((p) => {
              p.materialien.find((x) => x.kennung === material.kennung).ueberschreibungen = {};
            }),
          },
        })
        : (gesperrt ? 'gesperrt' : 'Haken setzen zum Überschreiben'),
    }, vorlagen.filter((v) => v.berechnet).map((v) => kennwertZeile(material, v))),
  ];
}

function nameAendern(material, wunsch, feldKnoten) {
  const name = wunsch.trim();
  const vergeben = zustand.projekt.materialien
    .some((m) => m.kennung !== material.kennung && (m.name || m.sorte) === name);
  if (!name || vergeben) {
    melden(vergeben
      ? `Name „${name}" schon vergeben.`
      : 'Name leer.', true);
    feldKnoten.value = material.name;
    return;
  }
  projektAendern((p) => {
    p.materialien.find((x) => x.kennung === material.kennung).name = name;
  });
}

/** Was über dem Editor steht: die Art, und ob es eine Normsorte ist. */
export function materialHinweis(material) {
  return `${ART_TEXT[material.art] || ''}`
    + (material.eigenstaendig ? ' · eigenes Material' : ' · Normsorte SIA');
}
