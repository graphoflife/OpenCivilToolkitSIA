"""
Das Zahlenfeld weist ab, was der Kern abwiese (``grenzeVerletzt`` in
``web/js/dom.js``), mit dessen Worten aus dem Katalog: eine Zahl ausserhalb
ihrer Grenzen und eine jenseits des Feldes, das sie begrenzt -- α_min nicht
ueber α_max, α_max nicht unter α_min (Benutzer, 2026-11-19: was ein Feld
gegen ein anderes begrenzt, weist schon das Feld ab).

Das Modul wird node als ``data:``-Adresse gegeben, wie in
``test_zustand_js.py``. Ohne node wird uebersprungen.
"""

import base64
import json
import shutil
import subprocess
import unittest
from pathlib import Path

from opencivil.web.api import katalog

WURZEL = Path(__file__).resolve().parents[1]
NODE = shutil.which("node")

PROGRAMM = r"""
const d = await import('data:text/javascript;base64,%s');
const felder = %s;
const [kleinste, groesste] = [felder.alpha_min, felder.alpha_max];
const buegel = { alpha_min: 30, alpha_max: 45 };
process.stdout.write(JSON.stringify({
  min_ueber_max: d.grenzeVerletzt(kleinste, 50, buegel),
  min_gleich_max: d.grenzeVerletzt(kleinste, 45, buegel),
  max_unter_min: d.grenzeVerletzt(groesste, 25, buegel),
  max_gleich_min: d.grenzeVerletzt(groesste, 30, buegel),
  ausserhalb: d.grenzeVerletzt(kleinste, 95, buegel),
}));
"""


@unittest.skipUnless(NODE, "ohne node")
class TestGrenzeGegenEinAnderesFeld(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        modul = base64.b64encode((WURZEL / "web" / "js" / "dom.js").read_bytes()).decode()
        felder = json.dumps(katalog()["felder"]["querkraftbewehrung"], ensure_ascii=False)
        lauf = subprocess.run([NODE, "--input-type=module", "-e", PROGRAMM % (modul, felder)],
                              capture_output=True, text=True, timeout=60)
        if lauf.returncode:
            raise AssertionError(lauf.stderr)
        cls.ergebnis = json.loads(lauf.stdout)

    def test_die_kleinste_nicht_ueber_der_groessten(self):
        self.assertEqual(self.ergebnis["min_ueber_max"],
                         "α_min darf nicht grösser sein als α_max")
        self.assertEqual(self.ergebnis["min_gleich_max"], "")

    def test_die_groesste_nicht_unter_der_kleinsten(self):
        self.assertEqual(self.ergebnis["max_unter_min"],
                         "α_max darf nicht kleiner sein als α_min")
        self.assertEqual(self.ergebnis["max_gleich_min"], "")

    def test_die_eigenen_grenzen_zuerst(self):
        self.assertEqual(self.ergebnis["ausserhalb"],
                         "α_min muss mindestens 1° und höchstens 89° sein")


if __name__ == "__main__":
    unittest.main()
