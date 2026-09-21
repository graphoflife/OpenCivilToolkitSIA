"""
Den Querschnitt ansehen, ohne ihn nachzuweisen.

Geprüft wird nicht, ob eine Zahl stimmt -- die käme aus demselben
Faserintegral wie die Nachweise und wäre dort schon geprüft. Geprüft wird,
dass die drei Auswertungen **zueinander** passen: wer aus N und M eine Ebene
bekommt und sie zurückgibt, muss wieder bei N und M landen. Genau das ist der
Grund, warum es sie gibt.
"""

import unittest

from opencivil import spannungsanalyse as sa
from opencivil.nachweis.querschnittsloeser import (
    Querschnittsloeser, Stahllage, beton_nichtlinear, stahl_bilinear)
from opencivil.nachweis.sproedes_versagen import rissmoment
from opencivil.projekt import Projekt, SpannungsfallEintrag
from opencivil.querschnitt.platte import Richtung
from opencivil.web import dienst


def loeserpaar():
    """Dieselbe Platte, zweimal -- gerissen und ungerissen."""
    aufbau = Projekt.beispiel().aufbauen()
    loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
    qs = aufbau.querschnitte["q1"]

    def wert(kid):
        return loesung.werte[kid].groesse.si

    posten = qs.posten_in_richtung(Richtung.X)
    lagen = [Stahllage(a_s=wert(a), z=wert(z), nummer=lage.nummer)
             for lage, _, _, a, z in posten]
    stahl = posten[0][0].stahl
    E_c_eff = wert(qs.beton.id_von("E_cm")) / (1.0 + wert(qs.id_von("kriechzahl")))
    h, b = wert(qs.id_von("h")), wert(qs.id_breite(Richtung.X))
    gemeinsam = dict(
        h=h, b=b, lagen=lagen,
        stahl=stahl_bilinear(E_s=wert(stahl.id_von("E_s")),
                             f_sd=wert(stahl.id_von("f_yd")),
                             eps_ud=wert(stahl.id_von("eps_ud"))),
        eps_druck=wert(qs.beton.id_von("eps_c2d")),
        eps_zug=wert(stahl.id_von("eps_ud")))
    gerissen = Querschnittsloeser(
        beton=beton_nichtlinear(f_cd=wert(qs.beton.id_von("f_cd")), E_c=E_c_eff,
                                eps_c1d=wert(qs.beton.id_von("eps_c1d")),
                                eps_c2d=wert(qs.beton.id_von("eps_c2d"))),
        **gemeinsam)
    ungerissen = Querschnittsloeser(
        beton=sa.beton_ungerissen(E_c=E_c_eff), **gemeinsam)
    M_Riss = rissmoment(h=h, b=b, f_ctm=wert(qs.beton.id_von("f_ctm"))).M_Riss
    return gerissen, ungerissen, M_Riss


class TestDieDreiPassenZueinander(unittest.TestCase):
    def setUp(self):
        self.gerissen, self.ungerissen, self.M_Riss = loeserpaar()

    def test_die_ebene_erzeugt_die_eingegebenen_schnittgroessen(self):
        """Die Probe -- dieselbe, die auch in den Herleitungen steht."""
        for N, M in ((0.0, 150e3), (-500e3, 120e3), (200e3, 60e3), (0.0, -60e3)):
            bild = sa.aus_schnittgroessen(self.gerissen, N=N, M=M)
            with self.subTest(N=N / 1e3, M=M / 1e3):
                self.assertTrue(bild.konvergiert)
                self.assertAlmostEqual(bild.N, N, delta=max(500.0, abs(N) * 1e-4))
                self.assertAlmostEqual(bild.M, M, delta=max(500.0, abs(M) * 1e-4))

    def test_hin_und_zurueck(self):
        """
        Aus N und M eine Ebene, aus deren Randdehnungen wieder N und M. Das
        ist die Zusage, die die beiden Richtungen überhaupt verbindet.
        """
        hin = sa.aus_schnittgroessen(self.gerissen, N=-300e3, M=140e3)
        zurueck = sa.aus_dehnungen(
            self.gerissen,
            eps_oben=hin.beton[0].eps, eps_unten=hin.beton[-1].eps)
        self.assertAlmostEqual(zurueck.eps_m, hin.eps_m, places=9)
        self.assertAlmostEqual(zurueck.chi, hin.chi, places=9)
        self.assertAlmostEqual(zurueck.N / 1e3, hin.N / 1e3, places=3)
        self.assertAlmostEqual(zurueck.M / 1e3, hin.M / 1e3, places=3)

    def test_die_hoehenachse_zeigt_nach_unten(self):
        """
        z = 0 ist die Oberkante -- dieselbe Achse wie im Lagenaufbau. Wäre sie
        gedreht, stünde das Bild kopf und passte nicht zum Nachweis daneben.
        """
        bild = sa.aus_schnittgroessen(self.gerissen, N=0.0, M=150e3)
        oben, unten = bild.beton[0], bild.beton[-1]
        self.assertEqual(oben.z, 0.0)
        self.assertGreater(unten.z, oben.z)
        # Positives Moment: unten gezogen, oben gedrückt.
        self.assertLess(oben.eps, 0.0)
        self.assertGreater(unten.eps, 0.0)
        # Und die 1. Lage liegt unten, also bei grossem z.
        erste = next(s for s in bild.stahl if s.nummer == 1)
        self.assertGreater(erste.z, self.gerissen.h / 2.0)
        self.assertGreater(erste.sigma, 0.0)

    def test_der_beton_traegt_keinen_zug(self):
        bild = sa.aus_schnittgroessen(self.gerissen, N=0.0, M=150e3)
        gezogen = [f for f in bild.beton if f.eps > 0]
        self.assertTrue(gezogen)
        self.assertTrue(all(f.sigma == 0.0 for f in gezogen))

    def test_die_nulllinie_liegt_zwischen_den_raendern(self):
        bild = sa.aus_schnittgroessen(self.gerissen, N=0.0, M=150e3)
        self.assertIsNotNone(bild.nulllinie)
        self.assertGreater(bild.nulllinie, 0.0)
        self.assertLess(bild.nulllinie, self.gerissen.h)

    def test_ohne_kruemmung_gibt_es_keine_nulllinie(self):
        """Reiner Druck: alles auf einer Seite, und dann steht dort nichts."""
        bild = sa.aus_dehnungen(self.gerissen, eps_oben=-0.001, eps_unten=-0.001)
        self.assertIsNone(bild.nulllinie)
        self.assertAlmostEqual(bild.chi, 0.0, places=12)
        self.assertLess(bild.N, 0.0)

    def test_gleichmaessiger_druck_erzeugt_trotzdem_ein_moment(self):
        """
        Weil die Bewehrung nicht symmetrisch liegt: unten ⌀18 + ⌀12, oben nur
        ⌀12. Dieselbe Dehnung erzeugt unten mehr Kraft, und die sitzt auf dem
        längeren Hebel. Ein Bild, das hier null zeigte, hätte den Stahl
        vergessen.
        """
        bild = sa.aus_dehnungen(self.gerissen, eps_oben=-0.001, eps_unten=-0.001)
        self.assertNotAlmostEqual(bild.M / 1e3, 0.0, delta=5.0)
        unten = next(s for s in bild.stahl if s.nummer == 1)
        oben = next(s for s in bild.stahl if s.nummer == 4)
        self.assertGreater(abs(unten.kraft), abs(oben.kraft))

    def test_eine_unmoegliche_kombination_sagt_das(self):
        bild = sa.aus_schnittgroessen(self.gerissen, N=0.0, M=5000e3)
        self.assertFalse(bild.konvergiert)
        self.assertIn("Gleichgewichtslage", bild.hinweis)

    def test_eine_dehnung_jenseits_der_gesetze_wird_gemeldet(self):
        bild = sa.aus_dehnungen(self.gerissen, eps_oben=-0.05, eps_unten=0.2)
        self.assertTrue(bild.hinweis)


class TestMomentenKruemmung(unittest.TestCase):
    def setUp(self):
        self.gerissen, self.ungerissen, self.M_Riss = loeserpaar()
        self.kurve = sa.moment_kruemmung(
            self.gerissen, self.ungerissen, N=0.0, M_Riss=self.M_Riss)

    def test_sie_reicht_von_null_bis_zum_widerstand(self):
        self.assertTrue(self.kurve.punkte)
        self.assertAlmostEqual(self.kurve.punkte[0].M, 0.0, delta=1.0)
        self.assertAlmostEqual(self.kurve.punkte[-1].M, self.kurve.M_Rd, delta=1.0)

    def test_das_groesste_moment_ist_der_biegewiderstand(self):
        """
        Eigenständig gesucht, aber es muss dasselbe sein wie im M-N-Nachweis --
        sonst zeigte das Bild einen anderen Querschnitt als die Tabelle.
        """
        aufbau = Projekt.beispiel().aufbauen()
        loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
        eckwert = aufbau.nachweise["q1.x"].d_eckwerte["M_Rd_N0_pos"]
        self.assertAlmostEqual(self.kurve.M_Rd / 1e3,
                               loesung.werte[eckwert.id].groesse.si / 1e3,
                               delta=2.0)

    def test_die_kruemmung_waechst_mit_dem_moment(self):
        chis = [p.chi for p in self.kurve.punkte]
        self.assertEqual(chis, sorted(chis))

    def test_ungerissen_ist_steifer_als_gerissen(self):
        """Der ganze Grund für die Zugversteifung: Zustand I krümmt sich weniger."""
        for p in self.kurve.punkte[1:]:
            with self.subTest(M=round(p.M / 1e3)):
                self.assertLessEqual(p.chi_I, p.chi_II + 1e-12)

    def test_unter_dem_rissmoment_gilt_der_ungerissene_zustand(self):
        unten = [p for p in self.kurve.punkte if 0 < p.M <= self.M_Riss]
        self.assertTrue(unten)
        for p in unten:
            with self.subTest(M=round(p.M / 1e3)):
                self.assertEqual(p.zeta, 0.0)
                self.assertAlmostEqual(p.chi, p.chi_I, places=12)

    def test_darueber_liegt_sie_zwischen_beiden(self):
        oben = [p for p in self.kurve.punkte if p.M > self.M_Riss * 1.2]
        self.assertTrue(oben)
        for p in oben:
            with self.subTest(M=round(p.M / 1e3)):
                self.assertGreater(p.zeta, 0.0)
                self.assertLessEqual(p.chi, p.chi_II + 1e-12)
                self.assertGreaterEqual(p.chi, p.chi_I - 1e-12)

    def test_druck_erhoeht_den_widerstand(self):
        mit_druck = sa.moment_kruemmung(self.gerissen, self.ungerissen,
                                        N=-300e3, M_Riss=self.M_Riss)
        self.assertGreater(mit_druck.M_Rd, self.kurve.M_Rd)

    def test_zu_viel_druck_laesst_nichts_uebrig(self):
        kaputt = sa.moment_kruemmung(self.gerissen, self.ungerissen,
                                     N=-1e8, M_Riss=self.M_Riss)
        self.assertFalse(kaputt.tragfaehig)
        self.assertIn("Gleichgewichtslage", kaputt.hinweis)


class TestUeberDenDienst(unittest.TestCase):
    def antwort(self, *faelle):
        projekt = Projekt.beispiel()
        projekt.querschnitte[0].spannungsfaelle = list(faelle)
        return dienst.bearbeite("rechnen", {"projekt": projekt.als_dict()})

    def test_alle_drei_arten_kommen_durch(self):
        antwort = self.antwort(
            SpannungsfallEintrag(name="A", art="schnittgroessen", M_Ed=150.0),
            SpannungsfallEintrag(name="B", art="dehnungen",
                                 eps_oben=-1.5, eps_unten=3.0),
            SpannungsfallEintrag(name="C", art="moment_kruemmung", N_Ed=-200.0))
        self.assertEqual(antwort.status, 200)
        faelle = antwort.daten["spannungsanalysen"]["q1"]
        self.assertEqual([f["name"] for f in faelle], ["A", "B", "C"])
        self.assertIn("bild", faelle[0])
        self.assertIn("bild", faelle[1])
        self.assertIn("kurve", faelle[2])
        # In Zeichengrössen: mm, Promille, kN.
        self.assertAlmostEqual(faelle[0]["bild"]["M"], 150.0, delta=0.5)
        self.assertAlmostEqual(faelle[0]["bild"]["h"], 300.0, delta=0.1)

    def test_ein_ausgeschalteter_fall_wird_nicht_gerechnet(self):
        antwort = self.antwort(
            SpannungsfallEintrag(name="A", art="schnittgroessen", M_Ed=150.0),
            SpannungsfallEintrag(name="Aus", art="schnittgroessen", aktiv=False))
        self.assertEqual([f["name"] for f in
                          antwort.daten["spannungsanalysen"]["q1"]], ["A"])

    def test_eine_unbewehrte_richtung_sagt_warum(self):
        projekt = Projekt.beispiel()
        q = projekt.querschnitte[0]
        q.richtung_lage1 = q.richtung_lage4 = "x"
        for nummer in (2, 3):
            q.lagen[nummer - 1].grund.durchmesser = 0
        for k in q.kombinationen:
            k.richtung = "x"
        q.spannungsfaelle = [SpannungsfallEintrag(name="y", richtung="y")]
        antwort = dienst.bearbeite("rechnen", {"projekt": projekt.als_dict()})
        fall = antwort.daten["spannungsanalysen"]["q1"][0]
        self.assertFalse(fall["moeglich"])
        self.assertIn("keine Bewehrung", fall["hinweis"])

    def test_ohne_analyse_steht_die_platte_nicht_in_der_liste(self):
        antwort = dienst.bearbeite(
            "rechnen", {"projekt": Projekt.beispiel().als_dict()})
        self.assertEqual(antwort.daten["spannungsanalysen"], {})


if __name__ == "__main__":
    unittest.main()
