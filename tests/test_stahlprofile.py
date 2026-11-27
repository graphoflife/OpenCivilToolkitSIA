"""
Die Stahlprofile: ihre Formeln gegen die Tabelle des Benutzers, ihre Umrisse,
und ein Profil als Querschnitt im Balkensystem.
"""

import math
import unittest

from opencivil.core.einheiten import CM, CM2, CM4, MM2
from opencivil.projekt import Projekt
from opencivil.projekt.lesen import ProjektFehler
from opencivil.stahlprofile.tabelle import PROFILE, PROFILREIHEN, profil
from tests.profilwerte import WERTE
from tests.unfertig import meldung

GROESSEN = ("A", "I_y", "I_z", "I_T", "e_y")
EINHEITEN = {"A": CM2, "I_y": CM4, "I_z": CM4, "I_T": CM4, "e_y": CM}


def gerechnet(name):
    p = profil(name)
    return p.form.kennwerte(p.masse)


def flaeche(punkte):
    return abs(sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1)
                   in zip(punkte, punkte[1:] + punkte[:1]))) / 2


class TestTabelle(unittest.TestCase):
    def test_jedes_profil_der_tabelle(self):
        """
        Jedes Profil der Tabelle des Benutzers, dazu die RRW aus dem Katalog
        und je Reihe aus Vollstahl ihre Vorgabe.
        """
        dazu = ("RRW", "VKT", "RND", "FL")
        self.assertEqual({n for n, p in PROFILE.items() if p.reihe not in dazu}, set(WERTE))
        self.assertEqual({r.kurz: len(r.profile) for r in PROFILREIHEN},
                         {"IPE": 18, "HEA": 24, "HEB": 24, "HEM": 24, "UPE": 14, "UNP": 17,
                          "RRK": 306, "RRW": 481, "ROR": 239, "VKT": 1, "RND": 1, "FL": 1})
        for r in PROFILREIHEN:
            with self.subTest(reihe=r.kurz):
                self.assertTrue(all(p.name.startswith(f"{r.kurz} ") for p in r.profile))

    def test_rechnet_wie_die_tabelle(self):
        """
        I, UPE und ROR mit denselben Formeln wie die Tabelle -- beim RRK sind
        dort die Beiwerte der Zwickel genau, hier gerundet: auf 2·10⁻⁵.
        """
        for name, werte in WERTE.items():
            if name.startswith("UNP"):
                continue
            w = gerechnet(name)
            for groesse, soll in zip(GROESSEN, werte):
                if soll is not None:
                    with self.subTest(profil=name, groesse=groesse):
                        ist = w[groesse].in_einheit(EINHEITEN[groesse])
                        self.assertAlmostEqual(ist / soll, 1.0, delta=2e-5)

    def test_unp_trifft_die_werte_der_tabelle(self):
        """
        Die Tabelle hat beim UNP keine Formeln, nur Werte mit drei Stellen:
        geneigte Flansche und Ecken wie im rechten Winkel treffen sie so gut.
        """
        grenzen = {"A": 0.006, "I_y": 0.006, "I_z": 0.014, "e_y": 0.01}
        for name, werte in WERTE.items():
            if not name.startswith("UNP"):
                continue
            w = gerechnet(name)
            for groesse, soll in zip(GROESSEN, werte):
                if groesse in grenzen:
                    with self.subTest(profil=name, groesse=groesse):
                        ist = w[groesse].in_einheit(EINHEITEN[groesse])
                        self.assertLess(abs(ist / soll - 1.0), grenzen[groesse])

    def test_radien_der_rrk(self):
        """Wie in der Tabelle: bis t = 6 mm 2t und t, bis 10 mm 2.5t und 1.5t, darüber 3t und 2t."""
        for name, r_o, r_i in (("RRK 100 x 100 x 6", 12.0, 6.0),
                               ("RRK 100 x 100 x 6.3", 15.75, 9.45),
                               ("RRK 200 x 200 x 10", 25.0, 15.0),
                               ("RRK 200 x 200 x 12.5", 37.5, 25.0)):
            with self.subTest(profil=name):
                m = profil(name).masse
                self.assertAlmostEqual(m["r_o"], r_o)
                self.assertAlmostEqual(m["r_i"], r_i)

    def test_rrw(self):
        """
        Die Radien 1.5t und t; das RRW 200 x 100 x 8 von Hand mit den Zwickeln
        der Tabelle -- r_o = 12, r_i = 8 --, das kleinste und das groesste.
        """
        m = profil("RRW 200 x 100 x 8").masse
        self.assertEqual((m["r_o"], m["r_i"]), (12.0, 8.0))
        w = gerechnet("RRW 200 x 100 x 8")
        A = 2 * 8 * (200 + 100 - 16) - 4 * 0.2146 * (12 ** 2 - 8 ** 2)
        self.assertAlmostEqual(w["A"].in_einheit(MM2), A, places=6)
        self.assertAlmostEqual(A, 4475.328, places=3)

        def zwickel(r, a):
            return 0.00755 * r ** 4 + 0.2146 * r ** 2 * a ** 2

        I_y = ((100 * 200 ** 3 - 84 * 184 ** 3) / 12 - 4 * zwickel(12, 100 - 0.2234 * 12)
               + 4 * zwickel(8, 100 - 8 - 0.2234 * 8))
        self.assertAlmostEqual(w["I_y"].in_einheit(CM4), I_y / 1e4, places=6)
        self.assertAlmostEqual(I_y / 1e4, 2233.6, places=1)
        rrw = next(r for r in PROFILREIHEN if r.kurz == "RRW")
        namen = [p.name for p in rrw.profile]
        self.assertEqual((namen[0], namen[-1]), ("RRW 80 x 80 x 5", "RRW 500 x 300 x 16"))
        self.assertIn("RRW 120 x 60 x 3.6", namen)
        self.assertNotIn("RRW 110 x 60 x 8", namen)

    def test_neigung_der_unp(self):
        """Bis h = 300 mm 8 % und t_f bei b/2, darüber 5 % und t_f in der Mitte des Flanschs."""
        self.assertEqual((profil("UNP 300").masse["p"], profil("UNP 300").masse["c"]), (8.0, 50.0))
        self.assertEqual((profil("UNP 320").masse["p"], profil("UNP 320").masse["c"]), (5.0, 57.0))
        w = gerechnet("UNP 300")
        self.assertAlmostEqual(w["t_1"].si * 1000, 16 + 0.08 * (50 - 10))
        self.assertAlmostEqual(w["t_2"].si * 1000, 16 - 0.08 * (100 - 50))

    def test_unbekanntes_profil(self):
        with self.assertRaisesRegex(KeyError, "«HEB 333» gibt es nicht"):
            profil("HEB 333")


class TestVollstahl(unittest.TestCase):
    """Vierkant-, Rund- und Flachstahl: die Masse stehen im Namen (Benutzer, 2026-11-27)."""

    def test_von_hand(self):
        """Mit den Formeln des Rechtecks und des Kreises der Vorlagen, in cm² und cm⁴."""
        w = gerechnet("VKT 40")
        self.assertAlmostEqual(w["A"].in_einheit(CM2), 16.0)
        self.assertAlmostEqual(w["I_y"].in_einheit(CM4), 40 ** 4 / 12 / 1e4)
        self.assertAlmostEqual(w["I_z"].in_einheit(CM4), 40 ** 4 / 12 / 1e4)
        w = gerechnet("RND 25")
        self.assertAlmostEqual(w["A"].in_einheit(MM2), math.pi * 25 ** 2 / 4)
        self.assertAlmostEqual(w["I_T"].in_einheit(CM4), math.pi * 25 ** 4 / 32 / 1e4)
        w = gerechnet("FL 100 x 10")
        self.assertAlmostEqual(w["A"].in_einheit(CM2), 10.0)
        self.assertAlmostEqual(w["I_y"].in_einheit(CM4), 100 * 10 ** 3 / 12 / 1e4)
        self.assertAlmostEqual(w["I_z"].in_einheit(CM4), 10 * 100 ** 3 / 12 / 1e4)

    def test_jede_zahl_die_geht(self):
        """Der Vierkant gibt seine Seite a als b und h weiter."""
        self.assertEqual(dict(profil("VKT 55").masse), {"a": 55.0, "b": 55.0, "h": 55.0})
        self.assertEqual(dict(profil("RND 12.5").masse), {"d": 12.5})
        self.assertEqual((profil("FL 60 x 8").reihe, dict(profil("FL 60 x 8").masse)),
                         ("FL", {"b": 60.0, "h": 8.0}))

    def test_was_nicht_geht(self):
        """Jeder Name, der nicht geht, sagt warum -- und wie er richtig heisst."""
        for name, grund in (
                ("VKT 40.0", "es heisst «VKT 40»"),
                ("VKT 0", "Das Profil «VKT 0» geht nicht: Seite a muss grösser als null"),
                ("FL 100", "ein Flachstahl heisst wie «FL 100 x 10»"),
                ("RND -5", "ein Rundstahl heisst wie «RND 40», mit Durchmesser d in mm"),
                ("FL 100x10", "mit Breite b und Dicke h in mm")):
            with self.subTest(name=name), self.assertRaisesRegex(KeyError, grund):
                profil(name)


class TestUmriss(unittest.TestCase):
    def test_flaeche_des_umrisses(self):
        """Das Bild zeigt, was die Formeln rechnen: seine Fläche ist A, bis auf 1 %."""
        for name, p in PROFILE.items():
            with self.subTest(profil=name):
                aussen, *loecher = p.form.umriss(p.masse)
                bild = flaeche(aussen) - sum(flaeche(loch) for loch in loecher)
                self.assertAlmostEqual(bild / gerechnet(name)["A"].in_einheit(MM2), 1.0, delta=0.01)


def stahltraeger(name="HEB 300", achse="y"):
    """Ein Einfeldträger von 6 m aus S355 mit 10 kN/m."""
    p = Projekt(name="Stahlträger")
    p.baustahl("S355")
    s = p.balkensystem("Träger")
    q = s.stahlprofil("Träger", name, achse)
    linie = s.linie((0, 0), (6, 0), querschnitt=q, material=s.baustahl("st1"))
    s.lager_an((0, 0), "gelenkig")
    s.lager_an((6, 0), "verschieblich")
    s.stablast(s.lastfall("G"), linie, wert=10.0)
    return p


class TestImBalkensystem(unittest.TestCase):
    def EI(self, p):
        return p.rechnen().wert("balkensystem.r1.Q1.M1.EI").groesse.si

    def test_um_die_starke_achse(self):
        I_y = WERTE["HEB 300"][1] * 1e-8
        self.assertAlmostEqual(self.EI(stahltraeger()) / (210000e6 * I_y), 1.0, delta=1e-9)

    def test_um_die_schwache_achse(self):
        I_z = WERTE["HEB 300"][2] * 1e-8
        self.assertAlmostEqual(self.EI(stahltraeger(achse="z")) / (210000e6 * I_z), 1.0, delta=1e-9)

    def test_nur_was_der_stab_braucht(self):
        """Um y braucht der Stab I_y -- I_z, d_K und I_T rechnet erst das räumliche System."""
        werte = stahltraeger().rechnen().loesung.werte
        self.assertIn("balkensystem.r1.Q1.I_y", werte)
        for kurz in ("I_z", "d_K", "I_T"):
            self.assertNotIn(f"balkensystem.r1.Q1.{kurz}", werte)

    def test_eigengewicht_aus_der_flaeche(self):
        p = stahltraeger()
        p.balkensysteme[0].lastfaelle[0].eigengewicht = True
        g_k = p.rechnen().wert("balkensystem.r1.Q1.M1.g_k").groesse.si
        self.assertAlmostEqual(g_k, 7850 * 10 * WERTE["HEB 300"][0] * 1e-4, delta=1e-9)

    def test_im_bericht(self):
        bericht = stahltraeger("UNP 200", "z").rechnen().bericht()
        self.assertIn("UNP 200, um z, die schwache Achse", bericht)

    def test_speichern_und_laden(self):
        p = stahltraeger("RRK 200 x 100 x 8", "z")
        wieder = Projekt.aus_dict(p.als_dict())
        self.assertEqual(wieder, p)
        q = wieder.balkensysteme[0].querschnitte[0]
        self.assertEqual((q.art, q.profil, q.achse), ("profil", "RRK 200 x 100 x 8", "z"))

    def test_vollstahl(self):
        """Ein Flachstahl hochkant: um z gebogen, mit I_z = h b³/12."""
        I_z = 10 * 100 ** 3 / 12 * 1e-12
        self.assertAlmostEqual(self.EI(stahltraeger("FL 100 x 10", "z")) / (210000e6 * I_z), 1.0,
                               delta=1e-9)

    def test_unbekanntes_profil(self):
        with self.assertRaisesRegex(ProjektFehler, "«HEB 333» gibt es nicht"):
            stahltraeger("HEB 333")
        p = stahltraeger()
        p.balkensysteme[0].querschnitte[0].profil = "HEB 333"
        self.assertIn("der Querschnitt «Träger»: Ein Profil «HEB 333» gibt es nicht.", meldung(p))
        p.balkensysteme[0].querschnitte[0].profil = "VKT 0"
        self.assertIn("der Querschnitt «Träger»: Das Profil «VKT 0» geht nicht", meldung(p))


if __name__ == "__main__":
    unittest.main()
