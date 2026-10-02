"""
Die Geometrie gezeichneter Querschnitte, gegen Formeln aus dem Lehrbuch.

Jeder Wert hier lässt sich von Hand nachrechnen: Rechteck, Dreieck, Kreis,
ein L aus zwei Rechtecken. Die Teilungsregel der Stablinien steht mit den
Beispielen da, die auch im Plan und im Zeichenfenster stehen.
"""

import math
import unittest

from opencivil.querschnitt import geometrie as geo
from opencivil.querschnitt.geometrie import Beziehung, GeometrieFehler, Linienart


def rechteck(y0, z0, b, h):
    return [(y0, z0), (y0 + b, z0), (y0 + b, z0 + h), (y0, z0 + h)]


def kreis(r, n, y0=0.0, z0=0.0):
    return [(y0 + r * math.cos(2 * math.pi * k / n),
             z0 + r * math.sin(2 * math.pi * k / n)) for k in range(n)]


class TestFlaechenwerte(unittest.TestCase):

    def test_rechteck(self):
        w = geo.flaechenwerte(rechteck(0, 0, 300, 600))
        self.assertAlmostEqual(w.A, 180000.0)
        self.assertAlmostEqual(w.y_S, 150.0)
        self.assertAlmostEqual(w.z_S, 300.0)
        self.assertAlmostEqual(w.I_y, 300 * 600 ** 3 / 12, delta=1e-3)
        self.assertAlmostEqual(w.I_z, 600 * 300 ** 3 / 12, delta=1e-3)
        self.assertAlmostEqual(w.I_yz, 0.0, delta=1e-3)

    def test_umlaufsinn_ist_gleich(self):
        links = geo.flaechenwerte(rechteck(10, 20, 300, 600))
        rechts = geo.flaechenwerte(list(reversed(rechteck(10, 20, 300, 600))))
        for feld in ("A", "y_S", "z_S", "I_y", "I_z", "I_yz"):
            self.assertAlmostEqual(getattr(links, feld), getattr(rechts, feld),
                                   delta=1e-3, msg=feld)

    def test_rechtwinkliges_dreieck(self):
        b, h = 300.0, 600.0
        w = geo.flaechenwerte([(0, 0), (b, 0), (0, h)])
        self.assertAlmostEqual(w.A, b * h / 2)
        self.assertAlmostEqual(w.y_S, b / 3)
        self.assertAlmostEqual(w.z_S, h / 3)
        self.assertAlmostEqual(w.I_y, b * h ** 3 / 36, delta=1e-2)
        self.assertAlmostEqual(w.I_z, h * b ** 3 / 36, delta=1e-2)
        # Die Katheten liegen auf den Achsen: das Deviationsmoment ist negativ.
        self.assertAlmostEqual(w.I_yz, -b * b * h * h / 72, delta=1e-2)

    def test_kreis_naehert_sich_dem_kreis(self):
        r, n = 200.0, 360
        w = geo.flaechenwerte(kreis(r, n, 50, 80))
        # Das Vieleck selbst: n gleichschenklige Dreiecke.
        self.assertAlmostEqual(w.A, n / 2 * r * r * math.sin(2 * math.pi / n), delta=1e-6)
        self.assertAlmostEqual(w.y_S, 50.0, delta=1e-9)
        self.assertAlmostEqual(w.z_S, 80.0, delta=1e-9)
        self.assertAlmostEqual(w.I_y / (math.pi * r ** 4 / 4), 1.0, delta=1e-3)
        self.assertAlmostEqual(w.I_y, w.I_z, delta=1e-3 * w.I_y)

    def test_l_aus_zwei_rechtecken(self):
        """Ein L als ein Polygon gleich der Summe zweier Rechtecke."""
        l_form = [(0, 0), (400, 0), (400, 100), (100, 100), (100, 500), (0, 500)]
        ganz = geo.flaechenwerte(l_form)
        teile = geo.summe([(1.0, geo.flaechenwerte(rechteck(0, 0, 400, 100))),
                           (1.0, geo.flaechenwerte(rechteck(0, 100, 100, 400)))])
        for feld in ("A", "y_S", "z_S", "I_y", "I_z", "I_yz"):
            self.assertAlmostEqual(getattr(ganz, feld), getattr(teile, feld),
                                   delta=1e-3 * max(1.0, abs(getattr(ganz, feld))),
                                   msg=feld)
        self.assertLess(ganz.I_yz, 0.0)  # Ein L ist unsymmetrisch.

    def test_aussparung_wird_abgezogen(self):
        kasten = geo.summe([(1.0, geo.flaechenwerte(rechteck(0, 0, 400, 600))),
                            (-1.0, geo.flaechenwerte(rechteck(100, 100, 200, 400)))])
        self.assertAlmostEqual(kasten.A, 400 * 600 - 200 * 400)
        self.assertAlmostEqual(kasten.z_S, 300.0)
        self.assertAlmostEqual(kasten.I_y, (400 * 600 ** 3 - 200 * 400 ** 3) / 12,
                               delta=1.0)

    def test_ohne_flaeche_kein_wert(self):
        with self.assertRaises(GeometrieFehler):
            geo.flaechenwerte([(0, 0), (100, 0), (200, 0)])


class TestLageUndPruefung(unittest.TestCase):

    def test_innen_rand_aussen(self):
        q = rechteck(0, 0, 300, 600)
        self.assertEqual(geo.lage((150, 300), q), 1)
        self.assertEqual(geo.lage((300, 200), q), 0)
        self.assertEqual(geo.lage((0, 0), q), 0)
        self.assertEqual(geo.lage((301, 200), q), -1)

    def test_nicht_konvex(self):
        l_form = [(0, 0), (400, 0), (400, 100), (100, 100), (100, 500), (0, 500)]
        self.assertEqual(geo.lage((50, 400), l_form), 1)
        self.assertEqual(geo.lage((300, 300), l_form), -1)

    def test_fliege_kreuzt_sich(self):
        with self.assertRaisesRegex(GeometrieFehler, "kreuzen sich"):
            geo.polygon_pruefen([(0, 0), (100, 100), (100, 0), (0, 100)], "Polygon 1")

    def test_zu_wenig_punkte_und_doppelte(self):
        with self.assertRaisesRegex(GeometrieFehler, "mindestens drei"):
            geo.polygon_pruefen([(0, 0), (100, 0)], "Polygon 1")
        with self.assertRaisesRegex(GeometrieFehler, "aufeinander"):
            geo.polygon_pruefen([(0, 0), (100, 0), (100, 0), (0, 100)], "Polygon 1")

    def test_abstand_zum_rand(self):
        self.assertAlmostEqual(geo.abstand_zum_rand((40, 300), rechteck(0, 0, 300, 600)), 40)


class TestBeziehung(unittest.TestCase):

    aussen = rechteck(0, 0, 400, 600)

    def test_loch_innen(self):
        self.assertIs(geo.beziehung(rechteck(100, 100, 200, 400), self.aussen),
                      Beziehung.ERSTES_IM_ZWEITEN)
        self.assertIs(geo.beziehung(self.aussen, rechteck(100, 100, 200, 400)),
                      Beziehung.ZWEITES_IM_ERSTEN)

    def test_kerbe_am_rand_liegt_innen(self):
        """Eine Aussparung, die am Rand ansetzt, gehört in das Polygon."""
        kerbe = rechteck(0, 500, 100, 100)  # oben links in der Ecke
        self.assertIs(geo.beziehung(kerbe, self.aussen), Beziehung.ERSTES_IM_ZWEITEN)

    def test_angrenzend_ist_getrennt(self):
        nachbar = rechteck(400, 0, 300, 600)  # teilt die rechte Kante
        self.assertIs(geo.beziehung(nachbar, self.aussen), Beziehung.GETRENNT)
        self.assertIs(geo.beziehung(rechteck(1000, 0, 100, 100), self.aussen),
                      Beziehung.GETRENNT)

    def test_teilweise_ueberlappend(self):
        self.assertIs(geo.beziehung(rechteck(300, 100, 300, 100), self.aussen),
                      Beziehung.UEBERLAPPEND)

    def test_deckungsgleich_ueberlappt(self):
        self.assertIs(geo.beziehung(list(self.aussen), self.aussen),
                      Beziehung.UEBERLAPPEND)

    def test_verschachteln_waehlt_das_kleinste(self):
        polygone = [rechteck(0, 0, 1000, 1000), rechteck(100, 100, 800, 800),
                    rechteck(200, 200, 100, 100), rechteck(2000, 0, 100, 100)]
        eltern = geo.verschachteln(polygone, ["P1", "P2", "P3", "P4"])
        self.assertEqual(eltern, (None, 0, 1, None))

    def test_ueberlappung_meldet_beide(self):
        with self.assertRaisesRegex(GeometrieFehler, "P1 und P2"):
            geo.verschachteln([rechteck(0, 0, 400, 600), rechteck(300, 100, 300, 100)],
                              ["P1", "P2"])

    def test_innerstes(self):
        polygone = [rechteck(0, 0, 1000, 1000), rechteck(100, 100, 800, 800)]
        self.assertEqual(geo.innerstes((500, 500), polygone), 1)
        self.assertEqual(geo.innerstes((50, 500), polygone), 0)
        self.assertIsNone(geo.innerstes((1500, 500), polygone))


class TestImBeton(unittest.TestCase):
    """Beton aussen, eine Aussparung innen: was trägt, sagt die Liste."""

    polygone = [rechteck(0, 0, 400, 600), rechteck(100, 100, 200, 400)]
    traegt = [True, False]

    def test_stab_im_beton(self):
        self.assertTrue(geo.stab_liegt_in((50, 50), 10, self.polygone, self.traegt))

    def test_stab_schneidet_den_rand(self):
        self.assertFalse(geo.stab_liegt_in((5, 50), 10, self.polygone, self.traegt))
        self.assertFalse(geo.stab_liegt_in((95, 300), 10, self.polygone, self.traegt))

    def test_stab_in_der_aussparung_oder_draussen(self):
        self.assertFalse(geo.stab_liegt_in((200, 300), 10, self.polygone, self.traegt))
        self.assertFalse(geo.stab_liegt_in((500, 300), 10, self.polygone, self.traegt))

    def test_wand_neben_der_aussparung(self):
        self.assertTrue(geo.strecke_liegt_in((50, 0), (50, 600), self.polygone, self.traegt))

    def test_wand_durch_die_aussparung(self):
        self.assertFalse(geo.strecke_liegt_in((0, 300), (400, 300), self.polygone, self.traegt))


class TestSchnittMitGerade(unittest.TestCase):

    def test_waagrecht_durch_rechteck(self):
        abschnitte = geo.schnitt_mit_gerade(rechteck(0, 0, 300, 600), (0.0, 1.0), 250.0)
        self.assertEqual(len(abschnitte), 1)
        von, bis = abschnitte[0]
        self.assertAlmostEqual(abs(bis - von), 300.0)

    def test_l_hat_zwei_abschnitte(self):
        # Ein U: auf halber Höhe der Schenkel zwei getrennte Stücke.
        u_form = [(0, 0), (500, 0), (500, 400), (400, 400), (400, 100),
                  (100, 100), (100, 400), (0, 400)]
        abschnitte = geo.schnitt_mit_gerade(u_form, (0.0, 1.0), 250.0)
        self.assertEqual(len(abschnitte), 2)
        self.assertAlmostEqual(sum(abs(b - a) for a, b in abschnitte), 200.0)

    def test_schraeg(self):
        n = (math.sqrt(0.5), math.sqrt(0.5))
        quadrat = rechteck(0, 0, 100, 100)
        # Die Diagonale von (100,0) nach (0,100): n·p = 100/√2.
        abschnitte = geo.schnitt_mit_gerade(quadrat, n, 100 / math.sqrt(2) - 1e-9)
        self.assertAlmostEqual(sum(abs(b - a) for a, b in abschnitte),
                               100 * math.sqrt(2), delta=1e-6)


class TestStablinie(unittest.TestCase):

    def test_teilung_wird_gerundet(self):
        linie = geo.stablinie((0, 0), (1000, 0), Linienart.TEILUNG, 150)
        self.assertEqual(linie.felder, 7)
        self.assertAlmostEqual(linie.teilung, 1000 / 7)
        self.assertEqual(len(linie.punkte), 8)
        self.assertEqual(linie.punkte[0], (0.0, 0.0))
        self.assertEqual(linie.punkte[-1], (1000.0, 0.0))

    def test_ohne_enden(self):
        ohne_start = geo.stablinie((0, 0), (1000, 0), Linienart.TEILUNG, 150,
                                   starteisen=False)
        self.assertEqual(len(ohne_start.punkte), 7)
        self.assertAlmostEqual(ohne_start.punkte[0][0], 1000 / 7)
        ohne_beide = geo.stablinie((0, 0), (1000, 0), Linienart.TEILUNG, 150,
                                   starteisen=False, endeisen=False)
        self.assertEqual(len(ohne_beide.punkte), 6)

    def test_kaufmaennisch_gerundet(self):
        """L/s = 2.5 gibt drei Felder -- nicht zwei, wie round() es täte."""
        self.assertEqual(geo.stablinie((0, 0), (1000, 0), Linienart.TEILUNG, 400).felder, 3)

    def test_anzahl(self):
        beide = geo.stablinie((0, 0), (0, 1000), Linienart.ANZAHL, 5)
        self.assertAlmostEqual(beide.teilung, 250.0)
        self.assertEqual(len(beide.punkte), 5)
        keine = geo.stablinie((0, 0), (0, 1000), Linienart.ANZAHL, 5,
                              starteisen=False, endeisen=False)
        self.assertAlmostEqual(keine.teilung, 1000 / 6)
        self.assertEqual(len(keine.punkte), 5)
        mitte = geo.stablinie((0, 0), (0, 1000), Linienart.ANZAHL, 1,
                              starteisen=False, endeisen=False)
        self.assertEqual(mitte.punkte, ((0.0, 500.0),))

    def test_ein_stab_an_beiden_enden_geht_nicht(self):
        with self.assertRaisesRegex(GeometrieFehler, "zugleich"):
            geo.stablinie((0, 0), (1000, 0), Linienart.ANZAHL, 1)

    def test_flaeche_hat_keine_einzelstaebe(self):
        linie = geo.stablinie((0, 0), (1000, 0), Linienart.FLAECHE, 1500)
        self.assertEqual(linie.punkte, ())
        self.assertIsNone(linie.teilung)
        self.assertAlmostEqual(linie.laenge, 1000.0)

    def test_ohne_laenge_oder_menge(self):
        with self.assertRaises(GeometrieFehler):
            geo.stablinie((0, 0), (0, 0), Linienart.TEILUNG, 150)
        with self.assertRaises(GeometrieFehler):
            geo.stablinie((0, 0), (1000, 0), Linienart.TEILUNG, 0)


if __name__ == "__main__":
    unittest.main()
