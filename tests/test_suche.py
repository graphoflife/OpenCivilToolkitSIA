"""Tests für die Nullstellensuche (opencivil/core/suche.py)."""

import math
import unittest

from opencivil.core.suche import Halbieren, Illinois, eingrenzen, illinois


class Zaehler:
    """Eine steigende Funktion mit Nullstelle bei 2^(1/3), die ihre Aufrufe zählt."""

    def __init__(self):
        self.aufrufe = 0

    def __call__(self, x):
        self.aufrufe += 1
        return x ** 3 - 2.0


WURZEL = 2.0 ** (1.0 / 3.0)


class TestHalbierenUndIllinois(unittest.TestCase):
    def test_beide_finden_die_stelle_bis_auf_die_schranke(self):
        for suche in (Halbieren(), Illinois()):
            with self.subTest(suche=type(suche).__name__):
                x = suche.finde(Zaehler(), 0.0, 2.0, 1e-12)
                self.assertAlmostEqual(x, WURZEL, delta=1e-11)

    def test_illinois_braucht_weniger_schritte(self):
        halbiert, sekante = Zaehler(), Zaehler()
        Halbieren().finde(halbiert, 0.0, 2.0, 1e-12)
        Illinois().finde(sekante, 0.0, 2.0, 1e-12)
        self.assertLess(sekante.aufrufe * 2, halbiert.aufrufe)

    def test_ohne_wert_unterwegs_keine_stelle(self):
        def loecherig(x):
            return None if 0.5 < x < 1.5 else x - 1.0
        for suche in (Halbieren(), Illinois()):
            with self.subTest(suche=type(suche).__name__):
                self.assertIsNone(suche.finde(loecherig, 0.0, 2.0, 1e-12))

    def test_eine_null_am_rand_wird_nicht_gesucht(self):
        f = Zaehler()
        self.assertEqual(Illinois().finde(f, WURZEL, 2.0, 1e-12, f_unten=0.0, f_oben=6.0),
                         WURZEL)
        self.assertEqual(f.aufrufe, 0)


class TestIllinoisMitBeigabe(unittest.TestCase):
    def test_die_beigabe_der_besten_stelle(self):
        beigabe = illinois(lambda x: (x - 0.3, f"bei {x:.6f}"), 0.0, -0.3, 1.0, 0.7,
                           schranke_x=1e-12, schranke_f=1e-9)
        self.assertEqual(beigabe, "bei 0.300000")

    def test_nan_beendet_die_suche(self):
        aufrufe = []

        def f(x):
            aufrufe.append(x)
            return (math.nan if len(aufrufe) > 1 else x * x - 0.3), len(aufrufe)

        self.assertEqual(illinois(f, 0.0, -0.3, 1.0, 0.7, schranke_x=1e-12,
                                  schranke_f=1e-12), 1)
        self.assertEqual(len(aufrufe), 2)


class TestEingrenzen(unittest.TestCase):
    def test_von_unterhalb_mit_wachsenden_schritten(self):
        unten, oben, f_unten, f_oben = eingrenzen(Zaehler(), 0.0, -2.0, 0.1, faktor=2.0)
        self.assertLess(f_unten, 0.0)
        self.assertGreater(f_oben, 0.0)
        self.assertLess(unten, WURZEL)
        self.assertGreater(oben, WURZEL)

    def test_von_oberhalb_kommt_das_fenster_geordnet(self):
        unten, oben, f_unten, f_oben = eingrenzen(Zaehler(), 3.0, 25.0, 0.1, faktor=2.0)
        self.assertLess(unten, WURZEL)
        self.assertLess(WURZEL, oben)
        self.assertLess(f_unten, 0.0 < f_oben)

    def test_am_rand_ohne_vorzeichenwechsel_nichts(self):
        self.assertIsNone(eingrenzen(Zaehler(), 0.0, -2.0, 0.1, faktor=2.0, oben=1.0))

    def test_ohne_wert_unterwegs_nichts(self):
        self.assertIsNone(eingrenzen(lambda x: None, 0.0, -2.0, 0.1, faktor=2.0))

    def test_eine_null_am_anfang_ist_schon_das_fenster(self):
        self.assertEqual(eingrenzen(Zaehler(), WURZEL, 0.0, 0.1, faktor=2.0),
                         (WURZEL, WURZEL, 0.0, 0.0))


if __name__ == "__main__":
    unittest.main()
