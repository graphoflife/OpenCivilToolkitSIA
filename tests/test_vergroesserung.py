"""
Der Vergrösserungsfaktor der Durchbiegung w/w_c -- SIA 262:2025, 4.4.3.2.5.

    w/w_c = (1 - 20 rho') / (10 rho^0.7) · (0.75 + 0.1 phi) · (h/d)^3

In x, je für Zug unten und Zug oben; rho' ist das rho der Gegenseite, mit
d' vom gezogenen Rand bis zur Gegenlage. phi ist die Kriechzahl der Platte.
"""

import unittest

from opencivil.projekt import Projekt


def werte(projekt):
    aufbau = projekt.aufbauen()
    loesung = aufbau.werk.loese(*aufbau.berichtsziele())
    return loesung


def faktor(loesung, kennung, seite):
    wert = loesung.werte.get(f"querschnitt.{kennung}.w_wc_{seite}")
    return None if wert is None else wert.groesse.si


class TestBeispiel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loesung = werte(Projekt.beispiel())

    def test_die_zahlen_des_beispiels(self):
        """Unten 2450 mm² in 248.1 mm, oben 754 mm² in 252 mm, phi = 2."""
        self.assertEqual(round(faktor(self.loesung, "q1", "unten"), 2), 4.00)
        self.assertEqual(round(faktor(self.loesung, "q1", "oben"), 2), 7.52)

    def test_von_hand(self):
        """⌀18 + ⌀12 je @150 unten in 249 und 246 mm, ⌀12@150 oben in 48 mm."""
        import math
        a18, a12 = (math.pi * d * d / 4 * 1000 / 150 for d in (18, 12))
        d_u = (a18 * 249 + a12 * 246) / (a18 + a12)
        rho_u, rho_o = (a18 + a12) / (1000 * d_u), a12 / (1000 * 252)
        unten = (1 - 20 * rho_o) / (10 * rho_u ** 0.7) * (0.75 + 0.2) * (300 / d_u) ** 3
        oben = (1 - 20 * rho_u) / (10 * rho_o ** 0.7) * (0.75 + 0.2) * (300 / 252) ** 3
        self.assertAlmostEqual(faktor(self.loesung, "q1", "unten"), unten, places=9)
        self.assertAlmostEqual(faktor(self.loesung, "q1", "oben"), oben, places=9)

    def test_die_normstelle_steht_in_der_herleitung(self):
        bloecke = [b for b in self.loesung.protokoll.alle_bloecke()
                   if "Vergrösserungsfaktor" in getattr(b, "titel", "")]
        self.assertTrue(bloecke)
        self.assertTrue(all(b.referenz == "SIA 262:2025, 4.4.3.2.5" for b in bloecke))


class TestSonderfaelle(unittest.TestCase):
    def test_die_kriechzahl_der_platte_wirkt_linear(self):
        projekt = Projekt.beispiel()
        projekt.querschnitte[0].kriechzahl = 0.0
        null = faktor(werte(projekt), "q1", "unten")
        self.assertAlmostEqual(null / faktor(werte(Projekt.beispiel()), "q1", "unten"),
                               0.75 / 0.95, places=12)

    def test_ohne_obere_x_lage_ist_rho_strich_null(self):
        projekt = Projekt()
        projekt.beton("C30/37")
        projekt.stahl("B500B")
        platte = projekt.platte("Nur unten", h=250, x=[12, 0], y=[10, 10])
        platte.einwirkung("Feld", M_Ed=30)
        loesung = werte(projekt)
        k = platte.kennung
        self.assertIsNotNone(faktor(loesung, k, "unten"))
        self.assertIsNone(faktor(loesung, k, "oben"))
        rho = loesung.werte[f"querschnitt.{k}.lage.2g.a_s"].groesse.si / (
            1.0 * loesung.werte[f"querschnitt.{k}.lage.2g.z"].groesse.si)
        d = loesung.werte[f"querschnitt.{k}.lage.2g.z"].groesse.si
        erwartet = 1.0 / (10 * rho ** 0.7) * (0.75 + 0.1 * platte.kriechzahl) * (0.25 / d) ** 3
        self.assertAlmostEqual(faktor(loesung, k, "unten"), erwartet, places=9)

    def test_ohne_x_kein_faktor(self):
        projekt = Projekt()
        projekt.beton("C30/37")
        projekt.stahl("B500B")
        platte = projekt.platte("Ohne x", h=250, x=[0, 0], y=[12, 12])
        loesung = werte(projekt)
        self.assertIsNone(faktor(loesung, platte.kennung, "unten"))
        self.assertIsNone(faktor(loesung, platte.kennung, "oben"))


if __name__ == "__main__":
    unittest.main()
