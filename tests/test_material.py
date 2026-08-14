"""Tests fuer Beton und Betonstahl nach SIA 262:2025."""

import math
import unittest

from opencivil.core.einheiten import EINHEITSLOS, N_PRO_MM2, PROZENT, Groesse
from opencivil.core.rechenwerk import Rechenwerk
from opencivil.core.wert import Quelle
from opencivil.material.beton import BETONSORTEN, beton, beton_frei
from opencivil.material.betonstahl import STAHLSORTEN, betonstahl


def werk_mit(baustoff) -> Rechenwerk:
    werk = Rechenwerk()
    baustoff.ins_rechenwerk(werk)
    return werk


class TestBeton(unittest.TestCase):
    def setUp(self):
        self.c30 = beton("C30/37")
        self.werk = werk_mit(self.c30)

    def w(self, kurzname: str) -> Groesse:
        loesung = self.werk.loese(self.c30.id_von(kurzname))
        return loesung.groesse(self.c30.id_von(kurzname))

    def test_sortenwerte(self):
        self.assertAlmostEqual(self.w("f_ck").in_einheit(N_PRO_MM2), 30.0)
        self.assertAlmostEqual(self.w("f_ctm").in_einheit(N_PRO_MM2), 2.9)

    def test_eta_fc_gedeckelt_bei_eins(self):
        """Fuer f_ck < 40 N/mm^2 waere (40/f_ck)^(1/3) > 1 -- der Deckel greift."""
        self.assertAlmostEqual(self.w("eta_fc").in_einheit(EINHEITSLOS), 1.0)

    def test_eta_fc_unter_eins_bei_hoher_festigkeit(self):
        c50 = beton("C50/60")
        werk = werk_mit(c50)
        eta = werk.loese(c50.id_von("eta_fc")).groesse(c50.id_von("eta_fc"))
        self.assertAlmostEqual(eta.in_einheit(EINHEITSLOS), (40 / 50) ** (1 / 3))
        self.assertLess(eta.in_einheit(EINHEITSLOS), 1.0)

    def test_f_cd(self):
        self.assertAlmostEqual(self.w("f_cd").in_einheit(N_PRO_MM2), 1.0 * 30 / 1.5)

    def test_f_cm(self):
        self.assertAlmostEqual(self.w("f_cm").in_einheit(N_PRO_MM2), 38.0)

    def test_tau_cd_empirisch(self):
        self.assertAlmostEqual(
            self.w("tau_cd").in_einheit(N_PRO_MM2), 0.3 * math.sqrt(30) / 1.5
        )

    def test_e_cm_empirisch(self):
        self.assertAlmostEqual(
            self.w("E_cm").in_einheit(N_PRO_MM2), 10000 * 38 ** (1 / 3), places=6
        )

    def test_e_cd(self):
        self.assertAlmostEqual(
            self.w("E_cd").in_einheit(N_PRO_MM2), 10000 * 38 ** (1 / 3), places=6
        )

    def test_k_sigma(self):
        erwartet = (10000 * 38 ** (1 / 3)) / (400 * 20.0)
        self.assertAlmostEqual(self.w("k_sigma").in_einheit(EINHEITSLOS), erwartet, places=6)

    def test_empirische_annahme_wird_vermerkt(self):
        loesung = self.werk.loese(self.c30.id_von("tau_cd"))
        texte = [b.text for b in loesung.protokoll.alle_bloecke() if hasattr(b, "text")]
        self.assertTrue(any("Empirische Formel" in t for t in texte))
        self.assertTrue(any("N/mm^2" in t for t in texte))

    def test_alle_sorten_rechnen_durch(self):
        for sorte in BETONSORTEN:
            with self.subTest(sorte=sorte):
                b = beton(sorte)
                loesung = werk_mit(b).loese_alles()
                self.assertTrue(loesung.vollstaendig, msg=str(loesung.nicht_berechenbar))
                self.assertGreater(loesung.groesse(b.id_von("f_cd")).si, 0)

    def test_unbekannte_sorte(self):
        with self.assertRaises(ValueError):
            beton("C99/100")

    def test_abweichender_kennwert(self):
        eigen = beton("C30/37", abweichungen={"f_ck": Groesse(32, N_PRO_MM2)})
        werk = werk_mit(eigen)
        self.assertAlmostEqual(
            werk.loese(eigen.id_von("f_cd")).groesse(eigen.id_von("f_cd")).in_einheit(N_PRO_MM2),
            32 / 1.5,
        )

    def test_teilsicherheitsbeiwert_ist_anpassbar(self):
        eigen = beton("C30/37", abweichungen={"gamma_c": Groesse(1.2, EINHEITSLOS)})
        werk = werk_mit(eigen)
        self.assertAlmostEqual(
            werk.loese(eigen.id_von("f_cd")).groesse(eigen.id_von("f_cd")).in_einheit(N_PRO_MM2),
            30 / 1.2,
        )

    def test_freier_beton(self):
        eigen = beton_frei(
            "Recyclingbeton",
            {"f_ck": Groesse(28, N_PRO_MM2), "f_ctm": Groesse(2.7, N_PRO_MM2)},
        )
        loesung = werk_mit(eigen).loese_alles()
        self.assertTrue(loesung.vollstaendig)


class TestBetonUeberschreiben(unittest.TestCase):
    def test_ueberschreiben_kappt_den_zweig(self):
        c30 = beton("C30/37")
        werk = werk_mit(c30)
        werk.setze(c30.id_von("f_cd"), Groesse(15, N_PRO_MM2))
        loesung = werk.loese(c30.id_von("k_sigma"))
        self.assertEqual(loesung.wert(c30.id_von("f_cd")).quelle, Quelle.UEBERSCHRIEBEN)
        # eta_fc und gamma_c werden nicht mehr gebraucht.
        self.assertFalse(loesung.hat(c30.id_von("eta_fc")))
        self.assertAlmostEqual(
            loesung.groesse(c30.id_von("k_sigma")).in_einheit(EINHEITSLOS),
            (10000 * 38 ** (1 / 3)) / (400 * 15),
            places=6,
        )


class TestBetonstahl(unittest.TestCase):
    def setUp(self):
        self.b500b = betonstahl("B500B")
        self.werk = werk_mit(self.b500b)

    def w(self, kurzname: str) -> Groesse:
        wid = self.b500b.id_von(kurzname)
        return self.werk.loese(wid).groesse(wid)

    def test_f_yd(self):
        self.assertAlmostEqual(self.w("f_yd").in_einheit(N_PRO_MM2), 500 / 1.15)

    def test_f_yd_druck(self):
        self.assertAlmostEqual(self.w("f_yd_druck").in_einheit(N_PRO_MM2), 500 / 1.15)

    def test_fliessdehnung(self):
        self.assertAlmostEqual(
            self.w("eps_yd").in_einheit(PROZENT), (500 / 1.15) / 200000 * 100, places=6
        )

    def test_dehnungen_als_prozent(self):
        self.assertAlmostEqual(self.w("eps_uk").in_einheit(PROZENT), 5.0)
        self.assertAlmostEqual(self.w("eps_ud").in_einheit(PROZENT), 4.5)

    def test_alle_sorten_rechnen_durch(self):
        for sorte in STAHLSORTEN:
            with self.subTest(sorte=sorte):
                s = betonstahl(sorte)
                loesung = werk_mit(s).loese_alles()
                self.assertTrue(loesung.vollstaendig, msg=str(loesung.nicht_berechenbar))

    def test_b700b(self):
        s = betonstahl("B700B")
        werk = werk_mit(s)
        self.assertAlmostEqual(
            werk.loese(s.id_von("f_yd")).groesse(s.id_von("f_yd")).in_einheit(N_PRO_MM2),
            700 / 1.15,
        )


class TestMehrereMaterialien(unittest.TestCase):
    """Zwei Materialien im selben Modell duerfen sich nicht ins Gehege kommen."""

    def test_zwei_betone_nebeneinander(self):
        werk = Rechenwerk()
        c25 = beton("C25/30").ins_rechenwerk(werk)
        c40 = beton("C40/50").ins_rechenwerk(werk)
        loesung = werk.loese(c25.id_von("f_cd"), c40.id_von("f_cd"))
        self.assertAlmostEqual(
            loesung.groesse(c25.id_von("f_cd")).in_einheit(N_PRO_MM2), 25 / 1.5
        )
        self.assertAlmostEqual(
            loesung.groesse(c40.id_von("f_cd")).in_einheit(N_PRO_MM2), 40 / 1.5
        )

    def test_gleiche_sorte_zweimal_mit_eigenem_praefix(self):
        werk = Rechenwerk()
        a = beton("C30/37", praefix="decke.beton").ins_rechenwerk(werk)
        b = beton("C30/37", praefix="wand.beton").ins_rechenwerk(werk)
        self.assertNotEqual(a.id_von("f_cd"), b.id_von("f_cd"))
        werk.setze(a.id_von("f_ck"), Groesse(35, N_PRO_MM2))
        loesung = werk.loese(a.id_von("f_cd"), b.id_von("f_cd"))
        self.assertAlmostEqual(
            loesung.groesse(a.id_von("f_cd")).in_einheit(N_PRO_MM2), 35 / 1.5
        )
        self.assertAlmostEqual(
            loesung.groesse(b.id_von("f_cd")).in_einheit(N_PRO_MM2), 30 / 1.5
        )

    def test_beton_und_stahl_zusammen(self):
        werk = Rechenwerk()
        c30 = beton("C30/37").ins_rechenwerk(werk)
        b500 = betonstahl("B500B").ins_rechenwerk(werk)
        loesung = werk.loese_alles()
        self.assertTrue(loesung.vollstaendig)
        self.assertTrue(loesung.hat(c30.id_von("f_cd")))
        self.assertTrue(loesung.hat(b500.id_von("f_yd")))


if __name__ == "__main__":
    unittest.main()
