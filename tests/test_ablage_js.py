"""
Was die Seite im Browser ablegt (``web/js``), liegt unter einem Schlüssel mit
der Vorsilbe, die «Alles zurücksetzen» hinter dem Zahnrad wegnimmt
(``allesZuruecksetzen`` in ``ablage.js``). Ein Schlüssel ohne sie überlebte
das Zurücksetzen still -- etwa die Lage der Werkzeuge im Zeichenfenster.
"""

import re
import unittest
from pathlib import Path

WURZEL = Path(__file__).resolve().parents[1]
JS = WURZEL / "web" / "js"

#: Ein Zugriff auf den Speicher des Browsers und sein Schlüssel: eine feste
#: Zeichenkette oder der Name einer Konstanten.
ZUGRIFF = re.compile(
    r"localStorage\.(?:getItem|setItem|removeItem)\(\s*([A-Za-z_$][\w$]*|'[^']*'|\"[^\"]*\"|`[^`]*`)")


def schluessel_im_browser():
    """Je Zugriff Datei und Schlüssel -- ohne die Schleife, die zurücksetzt."""
    gefunden = []
    for datei in sorted(JS.glob("*.js")):
        text = datei.read_text(encoding="utf-8")
        for zeile in text.splitlines():
            for argument in ZUGRIFF.findall(zeile):
                if argument[0] in "'\"`":
                    gefunden.append((datei.name, argument[1:-1]))
                elif ".startsWith(VORSILBE)" not in zeile:
                    konstante = re.search(rf"const {re.escape(argument)}\s*=\s*'([^']*)'", text)
                    gefunden.append((datei.name, konstante.group(1) if konstante else None))
    return gefunden


class TestSchluesselImBrowser(unittest.TestCase):
    def test_jeder_schluessel_traegt_die_vorsilbe(self):
        """Die Mappe, aufbewahrte Stände, Zeichenfenster und Zugeklapptes -- alle gehen weg."""
        ablage = (JS / "ablage.js").read_text(encoding="utf-8")
        vorsilbe = re.search(r"const VORSILBE = '([^']+)'", ablage).group(1)
        gefunden = schluessel_im_browser()
        self.assertGreaterEqual(len({s for _, s in gefunden}), 5, gefunden)
        for datei, schluessel in gefunden:
            with self.subTest(datei=datei, schluessel=schluessel):
                self.assertIsNotNone(schluessel, "der Schlüssel ist keine feste Zeichenkette")
                self.assertTrue(schluessel.startswith(vorsilbe))

    def test_nur_ueber_die_methoden(self):
        """``localStorage[x]`` und ``localStorage.x`` gingen am Test oben vorbei."""
        for datei in sorted(JS.glob("*.js")):
            text = datei.read_text(encoding="utf-8")
            with self.subTest(datei=datei.name):
                self.assertEqual(re.findall(r"localStorage\s*\[", text), [])
                self.assertEqual(
                    re.findall(r"localStorage\.(?!getItem|setItem|removeItem)\w+", text), [])


if __name__ == "__main__":
    unittest.main()
