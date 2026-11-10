"""
Jede Bauteilart steht in jedem Verzeichnis, das nach Art fragt.

Eine Bauteilart hat ihren Steckbrief in :data:`~opencivil.projekt.aufbau.BAUTEILE`.
Was der Bericht und die Oberflaeche je Art brauchen, steht in ihren
Schichten -- der Kern kennt sie nicht. Fehlt dort eine Art, soll es laut
werden und nicht still: kein leeres Bild, keine Tabelle ohne Kopf, kein Knopf
ohne Zeichen. Wo es beim Laden nicht geht, prueft es dieser Test.
"""

import re
import unittest
from pathlib import Path

from opencivil.bericht.zusammenfassung import ANGABEN
from opencivil.projekt.aufbau import BAUTEILE
from opencivil.web.zeichendaten import ZEICHENDATEN

WURZEL = Path(__file__).resolve().parents[1]
JS = WURZEL / "web" / "js"


class TestJedeArtIstVerzeichnet(unittest.TestCase):
    def test_was_ueber_der_nachweistabelle_steht(self):
        """Auch eine Art ohne Nachweise steht da -- mit ``None``."""
        self.assertEqual(set(ANGABEN), {a.name for a in BAUTEILE})

    def test_was_die_oberflaeche_zeichnet(self):
        self.assertEqual(set(ZEICHENDATEN), {a.name for a in BAUTEILE})


class TestSinnbilder(unittest.TestCase):
    """Jedes Zeichen, das die Oberflaeche nennt, gibt es in sinnbilder.js -- sonst bliebe der Knopf leer."""

    def test_jedes_genannte_zeichen_gibt_es(self):
        quelltext = (JS / "sinnbilder.js").read_text(encoding="utf-8")
        tabelle = quelltext[quelltext.index("const ZEICHEN = {"):]
        tabelle = tabelle[:tabelle.index("\n};\n")]
        vorhanden = set(re.findall(r"^  '?([a-z_-]+)'?: \{", tabelle, flags=re.M))
        genannt = {(pfad.name, m.group(1))
                   for pfad in JS.glob("*.js")
                   for muster in (r"zeichen: '([a-z_-]+)'", r"sinnbild\('([a-z_-]+)'\)")
                   for m in re.finditer(muster, pfad.read_text(encoding="utf-8"))}
        self.assertGreater(len(genannt), 10)
        for datei, zeichen in sorted(genannt):
            with self.subTest(datei=datei, zeichen=zeichen):
                self.assertIn(zeichen, vorhanden)


if __name__ == "__main__":
    unittest.main()
