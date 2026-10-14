"""
Die Bauteilarten der Oberflaeche (``web/js/arten.js``) gegen den Steckbrief
des Kerns (``BAUTEILE``): Liste, Vorsilbe und Namensraum stehen an beiden
Stellen und muessen gleich sein.

Das Modul wird node als ``data:``-Adresse gegeben, wie in
``test_markdown_js.py``. Ohne node wird uebersprungen.
"""

import base64
import json
import shutil
import subprocess
import unittest
from pathlib import Path

from opencivil.projekt import BAUTEILE

WURZEL = Path(__file__).resolve().parents[1]
NODE = shutil.which("node")

PROGRAMM = r"""
const m = await import('data:text/javascript;base64,%s');
process.stdout.write(JSON.stringify(m.ARTEN));
"""


@unittest.skipUnless(NODE, "ohne node")
class TestArtenWieImKern(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        modul = base64.b64encode((WURZEL / "web" / "js" / "arten.js").read_bytes()).decode()
        lauf = subprocess.run([NODE, "--input-type=module", "-e", PROGRAMM % modul],
                              capture_output=True, text=True, timeout=60)
        if lauf.returncode:
            raise AssertionError(lauf.stderr)
        cls.arten = json.loads(lauf.stdout)

    def test_dieselben_arten_in_derselben_reihenfolge(self):
        self.assertEqual([a["liste"] for a in self.arten], [art.liste for art in BAUTEILE])

    def test_vorsilbe_und_namensraum_wie_im_kern(self):
        for js, kern in zip(self.arten, BAUTEILE):
            with self.subTest(art=kern.name):
                self.assertEqual(js["vorsilbe"], kern.vorsilbe)
                # Die Auswahl nennt eine Bauteilart wie den Anfang ihres
                # Namensraums -- daran grenzt die rechte Tafel ein.
                self.assertEqual(js["art"], kern.raum)


if __name__ == "__main__":
    unittest.main()
