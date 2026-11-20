"""
Der Zustand der Oberflaeche (``web/js/zustand.js``): ein Eintrag wird ueber
seine Kennung gefunden und geaendert, gleich in welcher Liste er steht -- und
gibt es ihn nicht mehr, geschieht nichts. Jede Aenderung zaehlt die Fassung
des Projekts, wer horcht, erfaehrt, ob alles, nur die Mitte oder das Projekt
neu ist, ein anderes Projekt leert, was sich die Ansichten merkten, und wer
zurueckkehrt, findet seine Auswahl wieder. Der Katalog nennt einen fehlenden
Schluessel mit seinem Pfad.

Das Modul wird node als ``data:``-Adresse gegeben, wie in
``test_arten_js.py``. Ohne node wird uebersprungen.
"""

import base64
import json
import shutil
import subprocess
import unittest
from pathlib import Path

WURZEL = Path(__file__).resolve().parents[1]
NODE = shutil.which("node")

PROGRAMM = r"""
const z = await import('data:text/javascript;base64,%s');
const abgelegt = [];
const gemeldet = [];
z.ablageEinrichten((p) => abgelegt.push(JSON.stringify(p)));
z.horchen((was) => gemeldet.push(was));
const probe = {
  name: 'Probe',
  materialien: [{ kennung: 'b1', name: 'C30/37' }],
  durchstanzstellen: [{ kennung: 'd1', V_d: 0 }],
};
z.projektSetzen(probe, { mappe: { projekte: [probe] } });
const gestartet = [JSON.parse(abgelegt[0]), [...gemeldet]];
abgelegt.length = 0;
gemeldet.length = 0;
const ergebnis = {
  gestartet,
  gefunden: [z.eintragVon('b1')?.name, z.eintragVon('d1')?.V_d, z.eintragVon('x9')],
};
z.eintragAendern('d1', (d) => { d.V_d = 500; });
ergebnis.geaendert = [z.zustand.projekt.durchstanzstellen[0].V_d, abgelegt.length, [...gemeldet]];
z.eintragAendern('x9', () => { throw new Error('nie gerufen'); });
ergebnis.ohne = [abgelegt.length, gemeldet.length];
z.aendern({ reiter: 'diagramm' });
z.mitteAendern({ fenster: 'f1' });
z.aendern();
ergebnis.wege = [gemeldet.slice(1), z.zustand.reiter, z.zustand.fenster, abgelegt.length];

const f0 = z.zustand.fassung;
z.eintragAendern('d1', (d) => { d.V_d = 600; });
z.ansichtVon('d1').gezeigt = 'LF1';
z.ansichtVon('b1').gezeigt = 'LF2';
z.ansichtVergessen('b1');
const vorNeuem = [z.zustand.fassung - f0, z.ansichtVon('d1').gezeigt ?? null,
                  z.ansichtVon('b1').gezeigt ?? null];
z.waehlen({ art: 'durchstanzen', kennung: 'd1' });
const neu = { name: 'Neu', materialien: [] };
z.mappeAendern((m) => m.projekte.push(neu), neu);
ergebnis.fassung = [...vorNeuem, z.zustand.fassung - f0, z.ansichtVon('d1').gezeigt ?? null,
                    z.zustand.projekt.name];
ergebnis.zurueck = [z.zustand.auswahl, JSON.parse(abgelegt.at(-1)).projekte.length];
z.projektSetzen(probe, { katalog: { a: { b: [1] } } });
ergebnis.zurueck.push(z.zustand.auswahl, z.zustand.app, z.zustand.projekt.name);

const meldung = (f) => { try { f(); return null; } catch (e) { return e.message; } };
ergebnis.katalog = [z.katalog('a', 'b'), meldung(() => z.katalog('a', 'c')),
                    meldung(() => z.katalog('x'))];
process.stdout.write(JSON.stringify(ergebnis));
"""


@unittest.skipUnless(NODE, "ohne node")
class TestEintraegeUeberIhreKennung(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        modul = base64.b64encode((WURZEL / "web" / "js" / "zustand.js").read_bytes()).decode()
        lauf = subprocess.run([NODE, "--input-type=module", "-e", PROGRAMM % modul],
                              capture_output=True, text=True, timeout=60)
        if lauf.returncode:
            raise AssertionError(lauf.stderr)
        cls.ergebnis = json.loads(lauf.stdout)

    def test_der_start_legt_die_mappe_ab(self):
        """Das gezeigte Projekt gehoert zur Mappe; abgelegt wird sie, nicht das Projekt."""
        mappe, gemeldet = self.ergebnis["gestartet"]
        self.assertEqual([p["name"] for p in mappe["projekte"]], ["Probe"])
        self.assertEqual(gemeldet, ["neu"])

    def test_gefunden_in_jeder_liste(self):
        self.assertEqual(self.ergebnis["gefunden"], ["C30/37", 0, None])

    def test_geaendert_abgelegt_und_gemeldet(self):
        self.assertEqual(self.ergebnis["geaendert"], [500, 1, ["projekt"]])

    def test_drei_wege(self):
        """
        Alles neu, nur die Mitte neu -- beides ohne Ablegen und Rechnen --
        und das Projekt geaendert (oben). Bis 2026-11-20 gab jeder Aufruf
        einen freien «Anlass» mit, und drei davon wirkten.
        """
        self.assertEqual(self.ergebnis["wege"], [["alles", "mitte", "alles"], "diagramm", "f1", 1])

    def test_ohne_eintrag_geschieht_nichts(self):
        """Weder abgelegt noch gerechnet -- etwa ein verzögertes Speichern nach dem Löschen."""
        self.assertEqual(self.ergebnis["ohne"], [1, 1])

    def test_fassung_und_ansichten(self):
        """
        Eine Änderung zählt die Fassung um eins; vergessen ist vergessen; ein
        anderes Projekt zählt weiter und leert jede Ansicht.
        """
        self.assertEqual(self.ergebnis["fassung"], [1, "LF1", None, 2, None, "Neu"])

    def test_zurueck_steht_die_auswahl_wieder(self):
        """Das neue Projekt beginnt ohne Auswahl; wer zurückkehrt, findet die seine."""
        auswahl = {"art": "durchstanzen", "kennung": "d1"}
        self.assertEqual(self.ergebnis["zurueck"], [None, 2, auswahl, "durchstanzen", "Probe"])

    def test_katalog_nennt_den_fehlenden_pfad(self):
        self.assertEqual(self.ergebnis["katalog"], [[1], "Im Katalog fehlt a.c.",
                                                    "Im Katalog fehlt x."])


if __name__ == "__main__":
    unittest.main()
