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
from opencivil.core.rechenobjekt import Rechenobjekt
from opencivil.projekt import Projekt
from opencivil.projekt.aufbau import BAUTEILE
from opencivil.projekt.eintraege import BauteilEintrag
from opencivil.web.zeichendaten import ZEICHENDATEN

WURZEL = Path(__file__).resolve().parents[1]
JS = WURZEL / "web" / "js"


class TestJedeArtIstVerzeichnet(unittest.TestCase):
    def test_was_ueber_der_nachweistabelle_steht(self):
        """Auch eine Art ohne Nachweise steht da -- mit ``None``."""
        self.assertEqual(set(ANGABEN), {a.name for a in BAUTEILE})

    def test_was_die_oberflaeche_zeichnet(self):
        self.assertEqual(set(ZEICHENDATEN), {a.name for a in BAUTEILE})


class TestVertraege(unittest.TestCase):
    """Was jede Art kann, steht in einer Klasse -- nicht in jeder Art von Hand."""

    def test_jeder_eintrag_sagt_worauf_er_zeigt(self):
        for art in BAUTEILE:
            with self.subTest(art=art.name):
                self.assertTrue(issubclass(art.eintrag, BauteilEintrag))

    def test_jedes_gebaute_bauteil_und_jeder_baustoff_ist_ein_rechenobjekt(self):
        aufbau = Projekt.jeder_nachweis().aufbauen()
        self.assertEqual({t.art.name for t in aufbau.teile.values()}, {a.name for a in BAUTEILE})
        for kennung, teil in aufbau.teile.items():
            with self.subTest(teil=kennung):
                self.assertIsInstance(teil.objekt, Rechenobjekt)
        for baustoff in aufbau.baustoffe.values():
            self.assertIsInstance(baustoff, Rechenobjekt)

    def test_ein_unbekannter_kurzname_nennt_die_bekannten(self):
        teil = Projekt.beispiel().aufbauen().teile["g1"].objekt
        with self.assertRaisesRegex(KeyError, r"Grundbruch '.*' kennt keinen Wert 'x'\. Bekannt: "):
            teil.id_von("x")


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
