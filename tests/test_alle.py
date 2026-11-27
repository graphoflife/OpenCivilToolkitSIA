"""
Das Startprogramm aller Tests (``python3 -m tests.alle``) liest richtig, was
unittest je Testdatei schreibt. Läse es einen Fehlschlag als «OK», ginge ein
Commit mit Fehlern still durch -- genau das soll es nie.
"""

import unittest
from unittest import mock

from tests import alle


def gelesen(ausgabe: str, code: int) -> alle.Lauf:
    """Was das Programm aus einer Ausgabe von unittest und ihrem Rückgabewert macht."""
    prozess = mock.Mock(stdout=ausgabe, returncode=code)
    with mock.patch.object(alle.subprocess, "run", return_value=prozess):
        return alle.laufen("tests.test_probe")


class TestLesen(unittest.TestCase):

    def test_alles_gut(self):
        lauf = gelesen("....\n------\nRan 4 tests in 0.120s\n\nOK\n", 0)
        self.assertEqual((lauf.tests, lauf.fehlschlaege, lauf.fehler, lauf.gut), (4, 0, 0, True))

    def test_gut_auch_mit_ausgelassenen(self):
        self.assertTrue(gelesen("Ran 2 tests in 0.001s\n\nOK (skipped=1)\n", 0).gut)

    def test_fehlschlaege_und_fehler_zaehlen_getrennt(self):
        lauf = gelesen("F.E\n======\nFAIL: test_a\nOK so weit\n------\n"
                       "Ran 3 tests in 0.100s\n\nFAILED (failures=1, errors=1)\n", 1)
        self.assertEqual((lauf.tests, lauf.fehlschlaege, lauf.fehler, lauf.gut), (3, 1, 1, False))

    def test_ein_absturz_beim_import_ist_ein_fehler(self):
        lauf = gelesen("Traceback (most recent call last):\nImportError: kein Modul\n", 1)
        self.assertEqual((lauf.fehler, lauf.gut), (1, False))

    def test_ein_rueckgabewert_ungleich_null_ist_nie_gut(self):
        """Etwa wenn keine Tests liefen: unittest sagt dann 5, und es steht kein «OK»."""
        self.assertFalse(gelesen("\nRan 0 tests in 0.000s\n\nNO TESTS RAN\n", 5).gut)


class TestWahl(unittest.TestCase):

    def test_drei_schreibweisen_derselben_datei(self):
        self.assertEqual(alle.module(["test_alle", "tests.test_alle", "tests/test_alle.py"]),
                         ["tests.test_alle"] * 3)

    def test_eine_datei_die_es_nicht_gibt(self):
        with self.assertRaises(SystemExit) as fehler:
            alle.module(["test_gibt_es_nicht"])
        self.assertIn("«test_gibt_es_nicht» gibt es nicht", str(fehler.exception))

    def test_ohne_gemessene_dauer_zuerst(self):
        namen = ["tests.test_alle", "tests.test_speicher"]
        self.assertEqual(alle.reihenfolge(namen, {"tests.test_speicher": 60.0}),
                         ["tests.test_alle", "tests.test_speicher"])
        self.assertEqual(alle.reihenfolge(namen, {"tests.test_speicher": 60.0,
                                                  "tests.test_alle": 1.0}),
                         ["tests.test_speicher", "tests.test_alle"])


if __name__ == "__main__":
    unittest.main()
