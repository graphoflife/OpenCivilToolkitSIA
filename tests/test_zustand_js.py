"""
Der Zugriff der Oberflaeche auf die Eintraege des Projekts (``web/js/zustand.js``):
ein Eintrag wird ueber seine Kennung gefunden und geaendert, gleich in welcher
Liste er steht -- und gibt es ihn nicht mehr, geschieht nichts.

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
const anlaesse = [];
z.ablageEinrichten((p) => abgelegt.push(JSON.stringify(p)));
z.horchen((anlass) => anlaesse.push(anlass));
z.zustand.projekt = {
  name: 'Probe',
  materialien: [{ kennung: 'b1', name: 'C30/37' }],
  durchstanzstellen: [{ kennung: 'd1', V_d: 0 }],
};
const ergebnis = {
  gefunden: [z.eintragVon('b1')?.name, z.eintragVon('d1')?.V_d, z.eintragVon('x9')],
};
z.eintragAendern('d1', (d) => { d.V_d = 500; });
ergebnis.geaendert = [z.zustand.projekt.durchstanzstellen[0].V_d, abgelegt.length, anlaesse];
z.eintragAendern('x9', () => { throw new Error('nie gerufen'); });
ergebnis.ohne = [abgelegt.length, anlaesse.length];
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

    def test_gefunden_in_jeder_liste(self):
        self.assertEqual(self.ergebnis["gefunden"], ["C30/37", 0, None])

    def test_geaendert_abgelegt_und_gemeldet(self):
        self.assertEqual(self.ergebnis["geaendert"], [500, 1, ["projekt"]])

    def test_ohne_eintrag_geschieht_nichts(self):
        """Weder abgelegt noch gerechnet -- etwa ein verzögertes Speichern nach dem Löschen."""
        self.assertEqual(self.ergebnis["ohne"], [1, 1])


if __name__ == "__main__":
    unittest.main()
