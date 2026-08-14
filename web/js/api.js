/**
 * api.js -- Zugriff auf den Rechenkern.
 *
 * Die Oberfläche rechnet nichts. Sie schickt die Projektbeschreibung hin und
 * bekommt Werte, Herleitung und Urteile zurück -- fertig formatiert und als
 * fertige LaTeX-Zeichenketten. Das ist der ganze Vertrag.
 */

class ApiFehler extends Error {
  constructor(meldung, status, spur) {
    super(meldung);
    this.name = 'ApiFehler';
    this.status = status;
    this.spur = spur;
  }
}

async function anfrage(pfad, { methode = 'GET', rumpf } = {}) {
  let antwort;
  try {
    antwort = await fetch(pfad, {
      method: methode,
      headers: rumpf ? { 'Content-Type': 'application/json' } : {},
      body: rumpf ? JSON.stringify(rumpf) : undefined,
    });
  } catch (ursache) {
    throw new ApiFehler(
      'Der Rechenkern ist nicht erreichbar. Läuft "python3 start_ui.py" noch?',
      0, String(ursache));
  }

  const text = await antwort.text();
  let daten;
  try {
    daten = text ? JSON.parse(text) : {};
  } catch {
    throw new ApiFehler(`Unlesbare Antwort (${antwort.status})`, antwort.status, text.slice(0, 500));
  }

  if (!antwort.ok) {
    throw new ApiFehler(daten.fehler || `Fehler ${antwort.status}`, antwort.status, daten.spur);
  }
  return daten;
}

export const api = {
  katalog:        ()               => anfrage('/api/katalog'),
  projektLaden:   ()               => anfrage('/api/projekt'),
  projektSichern: (projekt)        => anfrage('/api/projekt', { methode: 'PUT', rumpf: projekt }),
  rechnen:        (projekt, ziele) => anfrage('/api/rechnen', { methode: 'POST', rumpf: { projekt, ziele } }),
  alles:          (projekt)        => anfrage('/api/alles',   { methode: 'POST', rumpf: { projekt } }),
  ziele:          (projekt)        => anfrage('/api/ziele',   { methode: 'POST', rumpf: { projekt } }),
  bericht:        (projekt, ziele) => anfrage('/api/bericht', { methode: 'POST', rumpf: { projekt, ziele } }),
};

export { ApiFehler };
