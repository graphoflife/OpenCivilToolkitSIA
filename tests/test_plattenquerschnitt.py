"""
Tests fuer den Plattenquerschnitt: Werkstoffgesetze, Dehnungsebene und die
Werte des Querschnitts. Der M-N-Nachweis auf ihm steht in
tests/test_nachweis_mn.py; bis 2026-11-20 stand beides dort.
"""

import math
import unittest

from opencivil.core.einheiten import KNM, MM, MM2, Groesse
from opencivil.core.rechenwerk import Rechenwerk
from opencivil.material.betonstahl import betonstahl
from opencivil.nachweis.biegung_normalkraft import BiegungNormalkraft, Schnittgroessen
from opencivil.nachweis.linie import MOMENT, schnitte
from opencivil.querschnitt.platte import Bewehrungslage, Bewehrungsposten, Richtung
from opencivil.querschnitt.werkstoffgesetz import Betongesetz, Dehnungsebene, Stahlgesetz
from tests.platten import einfache_platte, lage, platte, symmetrische_platte


class TestWerkstoffgesetz(unittest.TestCase):
    def setUp(self):
        self.beton = Betongesetz(f_cd=20e6, eps_c1d=0.002, eps_c2d=0.0035, k_sigma=4.2)
        self.stahl = Stahlgesetz(E_s=200e9, f_yd=434.8e6, f_yd_druck=434.8e6, eps_ud=0.045)

    def test_beton_nimmt_keinen_zug(self):
        self.assertEqual(self.beton.spannung(0.001), 0.0)

    def test_beton_erreicht_f_cd_im_plateau(self):
        self.assertAlmostEqual(self.beton.spannung(-0.003), -20e6)
        self.assertAlmostEqual(self.beton.spannung(-0.0035), -20e6)

    def test_beton_parabelast_steigt_monoton(self):
        werte = [self.beton.spannung(-e / 10000) for e in range(0, 21)]
        for a, b in zip(werte, werte[1:]):
            self.assertLessEqual(b, a + 1e-6)

    def test_beton_bei_null(self):
        self.assertAlmostEqual(self.beton.spannung(0.0), 0.0)

    def test_stahl_elastisch(self):
        self.assertAlmostEqual(self.stahl.spannung(0.001), 200e9 * 0.001)

    def test_stahl_fliesst(self):
        self.assertAlmostEqual(self.stahl.spannung(0.01), 434.8e6)
        self.assertAlmostEqual(self.stahl.spannung(-0.01), -434.8e6)


class TestDehnungsebene(unittest.TestCase):
    def test_durch_zwei_punkte(self):
        ebene = Dehnungsebene.durch_zwei_punkte(0.0045, 0.26, -0.0035, 0.0, h=0.3)
        self.assertAlmostEqual(ebene.bei(0.0), -0.0035)
        self.assertAlmostEqual(ebene.bei(0.26), 0.0045)

    def test_nulllinie(self):
        ebene = Dehnungsebene(eps_oben=-0.0035, eps_unten=0.0035, h=0.3)
        self.assertAlmostEqual(ebene.nulllinie, 0.15)

    def test_gleichmaessige_dehnung_hat_keine_nulllinie(self):
        ebene = Dehnungsebene(eps_oben=0.002, eps_unten=0.002, h=0.3)
        self.assertEqual(ebene.nulllinie, float("inf"))


class TestQuerschnitt(unittest.TestCase):
    def setUp(self):
        self.platte = einfache_platte()
        self.werk = Rechenwerk()
        self.platte.ins_rechenwerk(self.werk)

    def test_bewehrungsflaeche(self):
        wid = self.platte.id_von("lage.1g.a_s")
        a_s = self.werk.loese(wid).groesse(wid)
        erwartet = math.pi * 18**2 / 4 * (1000 / 150)
        self.assertAlmostEqual(a_s.in_einheit(MM2), erwartet, places=3)

    def test_statische_hoehe(self):
        wid = self.platte.id_von("lage.1g.z")
        z = self.werk.loese(wid).groesse(wid)
        # z ab Oberkante: h - (c + phi/2) = 300 - (30 + 9)
        self.assertAlmostEqual(z.in_einheit(MM), 261.0)

    def test_obere_lage_zaehlt_von_oben(self):
        platte = symmetrische_platte()
        werk = Rechenwerk()
        platte.ins_rechenwerk(werk)
        loesung = werk.loese(platte.id_von("lage.4g.z"), platte.id_von("lage.1g.z"))
        self.assertAlmostEqual(loesung.groesse(platte.id_von("lage.4g.z")).in_einheit(MM), 38.0)
        self.assertAlmostEqual(loesung.groesse(platte.id_von("lage.1g.z")).in_einheit(MM), 262.0)

    def test_lagenstapelung(self):
        """Die 2. Lage liegt um den grössten Durchmesser der 1. weiter innen."""
        qs = platte([
            lage(1, Richtung.X, phi=20.0),
            lage(2, Richtung.Y, phi=16.0),
            lage(3, Richtung.X),
            lage(4, Richtung.Y),
        ])
        werk = Rechenwerk()
        qs.ins_rechenwerk(werk)
        loesung = werk.loese(qs.id_von("lage.1g.z"), qs.id_von("lage.2g.z"))
        # 1. Lage: 30 + 20/2 = 40 -> z = 260
        self.assertAlmostEqual(loesung.groesse(qs.id_von("lage.1g.z")).in_einheit(MM), 260.0)
        # 2. Lage: 30 + 20 + 16/2 = 58 -> z = 242
        self.assertAlmostEqual(loesung.groesse(qs.id_von("lage.2g.z")).in_einheit(MM), 242.0)

    def _lage_mit_zulage(self, unguenstig: bool):
        """1. Lage: Grund ⌀20 und Zulage ⌀12, Überdeckung 30 mm."""
        lagen = [
            lage(1, Richtung.X, phi=20.0, zulage=12.0),
            lage(2, Richtung.Y), lage(3, Richtung.X), lage(4, Richtung.Y),
        ]
        lagen[0].unguenstig = unguenstig
        qs = platte(lagen)
        werk = Rechenwerk()
        qs.ins_rechenwerk(werk)
        loesung = werk.loese(qs.id_von("lage.1g.z"), qs.id_von("lage.1z.z"))
        return (loesung.groesse(qs.id_von("lage.1g.z")).in_einheit(MM),
                loesung.groesse(qs.id_von("lage.1z.z")).in_einheit(MM))

    def test_guenstige_lage_laesst_die_aeusseren_kanten_fluchten(self):
        """
        Beide berühren dieselbe Hüllebene, je um ihren eigenen Halbmesser
        eingerückt. Die Zulage liegt damit weiter aussen und hat mehr Hebelarm.
        """
        grund, zulage = self._lage_mit_zulage(unguenstig=False)
        self.assertAlmostEqual(grund, 300 - (30 + 10))
        self.assertAlmostEqual(zulage, 300 - (30 + 6))

    def test_unguenstige_lage_laesst_die_inneren_kanten_fluchten(self):
        """
        Der dünnere Stab rückt zur Plattenmitte, bis seine innere Kante mit
        der des dickeren fluchtet. Das ist die Vorgabe: auf der Baustelle
        lässt sich nicht steuern, welche Kante fluchtet.
        """
        grund, zulage = self._lage_mit_zulage(unguenstig=True)
        self.assertAlmostEqual(grund, 300 - (30 + 10))
        # Zulage: Rand = 30 + 20 - 6 = 44  ->  d = 256
        self.assertAlmostEqual(zulage, 300 - (30 + 20 - 6))
        # Innere Kanten auf gleicher Höhe -- das ist die Aussage.
        self.assertAlmostEqual(grund - 20 / 2, zulage - 12 / 2)

    def test_unguenstig_ist_die_vorgabe(self):
        self.assertTrue(lage(1, Richtung.X, phi=20.0, zulage=12.0).unguenstig)

    def test_zulage_zaehlt_zur_flaeche(self):
        qs = platte([
            lage(1, Richtung.X, phi=18.0, zulage=12.0),
            lage(2, Richtung.Y), lage(3, Richtung.X), lage(4, Richtung.Y),
        ])
        werk = Rechenwerk()
        qs.ins_rechenwerk(werk)
        loesung = werk.loese(qs.id_von("lage.1g.a_s"), qs.id_von("lage.1z.a_s"))
        self.assertAlmostEqual(
            loesung.groesse(qs.id_von("lage.1z.a_s")).in_einheit(MM2),
            math.pi * 12**2 / 4 * (1000 / 150), places=3)

    def test_stabzahl_statt_abstand(self):
        qs = platte([
            Bewehrungslage(1, Richtung.X, betonstahl("B500B"),
                           grund=Bewehrungsposten(Groesse(18, MM), anzahl=7)),
            lage(2, Richtung.Y), lage(3, Richtung.X), lage(4, Richtung.Y),
        ])
        werk = Rechenwerk()
        qs.ins_rechenwerk(werk)
        wid = qs.id_von("lage.1g.a_s")
        self.assertAlmostEqual(
            werk.loese(wid).groesse(wid).in_einheit(MM2), math.pi * 18**2 / 4 * 7, places=3)

    def test_ohne_bewehrung_verboten(self):
        with self.assertRaises(ValueError):
            platte([lage(n, Richtung.X if n in (1, 4) else Richtung.Y) for n in range(1, 5)])

    def test_gekoppelte_richtungen_erzwungen(self):
        """Die 1. und die 2. Lage müssen entgegengesetzte Richtungen haben."""
        with self.assertRaises(ValueError) as ctx:
            platte([
                lage(1, Richtung.X, phi=16.0),
                lage(2, Richtung.X, phi=16.0),   # falsch: gleiche Richtung
                lage(3, Richtung.Y), lage(4, Richtung.X),
            ])
        self.assertIn("entgegengesetzte", str(ctx.exception))

    def test_falsche_lagenzahl_verboten(self):
        with self.assertRaises(ValueError):
            platte([lage(1, Richtung.X, phi=16.0), lage(2, Richtung.Y)])

    def test_richtungen_trennen_die_bewehrung(self):
        qs = platte([
            lage(1, Richtung.X, phi=18.0),
            lage(2, Richtung.Y, phi=12.0),
            lage(3, Richtung.Y), lage(4, Richtung.X),
        ])
        self.assertEqual(len(qs.posten_in_richtung(Richtung.X)), 1)
        self.assertEqual(len(qs.posten_in_richtung(Richtung.Y)), 1)
        self.assertEqual(qs.richtungen_mit_bewehrung, [Richtung.X, Richtung.Y])

    def test_querbewehrung_traegt_nicht_zum_moment_bei(self):
        """
        Eine Lage in y-Richtung darf den Widerstand um x nicht erhöhen -- sonst
        wäre die Bemessung auf der unsicheren Seite.
        """
        def m_rd(qs) -> float:
            werk = Rechenwerk()
            qs.ins_rechenwerk(werk)
            nachweis = BiegungNormalkraft(
                qs, [Schnittgroessen("F", M_Ed=Groesse(1, KNM))], Richtung.X)
            werk.registriere(nachweis)
            befund = werk.loese(nachweis.d_eckwerte["M_Rd_max"].id).befund(nachweis)
            return max(schnitte(befund.linie, MOMENT, 0.0))

        ohne = m_rd(platte([
            lage(1, Richtung.X, phi=18.0), lage(2, Richtung.Y),
            lage(3, Richtung.Y), lage(4, Richtung.X)]))
        mit_quer = m_rd(platte([
            lage(1, Richtung.X, phi=18.0), lage(2, Richtung.Y, phi=20.0),
            lage(3, Richtung.Y), lage(4, Richtung.X)]))
        self.assertAlmostEqual(ohne, mit_quer, places=6)

    def test_lagenaufbau_wird_protokolliert(self):
        from opencivil.core.protokoll import TabellenBlock

        loesung = self.werk.loese(self.platte.id_von("lage.1g.z"))
        tabellen = [
            b for b in loesung.protokoll.alle_bloecke() if isinstance(b, TabellenBlock)
        ]
        self.assertTrue(any("Randabstände" in t.titel for t in tabellen))


if __name__ == "__main__":
    unittest.main()
