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
from opencivil.projekt import Projekt, SpannungsfallEintrag
from opencivil.querschnitt.platte import Richtung
from opencivil.web import dienst


def loeserpaar():
    """
    Dieselbe Platte, zweimal -- gerissen und ungerissen.

    Ueber :func:`spannungsanalyse.loeserpaar`, dieselbe Funktion, die auch
    die Oberflaeche benutzt. Hier stand einmal eine eigene Kopie davon; der
    Test pruefte dann seine Kopie und nicht das, was gezeichnet wird.
    """
    aufbau = Projekt.beispiel().aufbauen()
    loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
    paar = sa.loeserpaar(aufbau.querschnitte["q1"], Richtung.X,
                         lambda kid: loesung.werte[kid].groesse.si)
    return paar


class TestDieDreiPassenZueinander(unittest.TestCase):
    def setUp(self):
        paar = loeserpaar()
        self.gerissen, self.ungerissen = paar.gerissen, paar.ungerissen

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
        # Und die unterste Lage liegt bei grossem z.
        erste = max(bild.stahl, key=lambda s: s.z)
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
        unten = max(bild.stahl, key=lambda s: s.z)
        oben = min(bild.stahl, key=lambda s: s.z)
        self.assertGreater(abs(unten.kraft), abs(oben.kraft))

    def test_eine_unmoegliche_kombination_sagt_das(self):
        bild = sa.aus_schnittgroessen(self.gerissen, N=0.0, M=5000e3)
        self.assertFalse(bild.konvergiert)
        self.assertIn("Gleichgewichtslage", bild.hinweis)

    def test_eine_dehnung_jenseits_der_gesetze_wird_gemeldet(self):
        bild = sa.aus_dehnungen(self.gerissen, eps_oben=-0.05, eps_unten=0.2)
        self.assertTrue(bild.hinweis)


class TestMomentenKruemmung(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Einmal für alle: die Linie kostet über eine Sekunde, und jeder Test
        # liest sie nur.
        cls.paar = loeserpaar()
        cls.gerissen, cls.ungerissen = cls.paar.gerissen, cls.paar.ungerissen
        cls.M_Riss = cls.paar.M_Riss
        cls.kurve = sa.moment_kruemmung(
            cls.gerissen, cls.ungerissen, N=0.0, M_Riss=cls.M_Riss)

    def kurve_bei(self, N):
        return sa.moment_kruemmung(self.gerissen, self.ungerissen,
                                   N=N, M_Riss=self.paar.rissmoment_bei(N))

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
        """Auch über den Sprung: Moment und Krümmung fallen nirgends zurück."""
        for liste in ([p.M for p in self.kurve.punkte], [p.chi for p in self.kurve.punkte]):
            self.assertEqual(liste, sorted(liste))

    def test_ungerissen_ist_steifer_als_gerissen(self):
        """Zustand I krümmt sich weniger -- darum springt die Linie beim Reissen nach rechts."""
        for p in self.kurve.punkte[1:]:
            with self.subTest(M=round(p.M / 1e3)):
                self.assertLessEqual(p.chi_I, p.chi_II + 1e-12)

    def test_unter_dem_rissmoment_gilt_der_ungerissene_zustand(self):
        unten = [p for p in self.kurve.punkte if 0 < p.M < self.M_Riss]
        self.assertTrue(unten)
        for p in unten:
            with self.subTest(M=round(p.M / 1e3)):
                self.assertFalse(p.gerissen)
                self.assertEqual(p.chi, p.chi_I)

    def test_darueber_gilt_der_gerissene_zustand(self):
        oben = [p for p in self.kurve.punkte if p.M > self.M_Riss]
        self.assertTrue(oben)
        for p in oben:
            with self.subTest(M=round(p.M / 1e3)):
                self.assertTrue(p.gerissen)
                self.assertEqual(p.chi, p.chi_II)

    def test_beim_rissmoment_springt_die_kruemmung(self):
        """
        Das waagrechte Stück: zwei Punkte beim selben Moment, vorher
        ungerissen, nachher gerissen. Vorher stand hier eine Linie mit
        Zugversteifung, die beim Rissmoment ohne Sprung weiterlief.
        """
        vor, nach = self.kurve.riss
        self.assertEqual(vor.M, self.M_Riss)
        self.assertEqual(nach.M, self.M_Riss)
        self.assertEqual(vor.chi, vor.chi_I)
        self.assertEqual(nach.chi, nach.chi_II)
        # Am Beispiel knapp das Doppelte: 0.00134 auf 0.00263 1/m.
        self.assertGreater(nach.chi, 1.5 * vor.chi)
        self.assertEqual(sum(1 for p in self.kurve.punkte if p.M == self.M_Riss), 2)

    def test_das_rissmoment_gilt_bei_der_normalkraft_der_linie(self):
        """
        Beim Rissmoment erreicht der gezogene Rand des ungerissenen
        Querschnitts seine Zugspannung -- bei jeder Normalkraft fast dieselbe.
        Vorher galt immer das Rissmoment ohne Normalkraft: bei 200 kN Druck
        stand der Rand dann bei 1.65 statt 2.17 N/mm².
        """
        def randspannung(N):
            bild = sa.aus_schnittgroessen(self.ungerissen, N=N,
                                          M=self.paar.rissmoment_bei(N))
            return bild.beton[-1].sigma
        ohne = randspannung(0.0)
        for N in (-200e3, 100e3):
            with self.subTest(N=N / 1e3):
                self.assertAlmostEqual(randspannung(N) / ohne, 1.0, delta=0.05)
        # Druck hebt das Rissmoment, Zug senkt es -- um N·h/6.
        self.assertAlmostEqual(self.kurve_bei(-200e3).M_Riss - self.M_Riss,
                               200e3 * self.gerissen.h / 6.0, places=6)

    def test_reisst_schon_die_normalkraft_ist_alles_gerissen(self):
        """
        Am Beispiel erst ab gut 828 kN Zug, und schon ab rund 840 kN gibt es
        gar keine Gleichgewichtslage mehr -- zu eng für einen Test über N.
        Darum hier das Rissmoment direkt.
        """
        kurve = sa.moment_kruemmung(self.gerissen, self.ungerissen,
                                    N=0.0, M_Riss=-1e3)
        self.assertTrue(kurve.punkte)
        self.assertTrue(all(p.gerissen for p in kurve.punkte))
        self.assertIsNone(kurve.riss)
        self.assertIn("gerissen", kurve.hinweis)

    def test_liegt_das_rissmoment_ueber_m_rd_bleibt_alles_ungerissen(self):
        kurve = sa.moment_kruemmung(self.gerissen, self.ungerissen,
                                    N=0.0, M_Riss=10 * self.kurve.M_Rd)
        self.assertTrue(kurve.punkte)
        self.assertFalse(any(p.gerissen for p in kurve.punkte))
        self.assertIsNone(kurve.riss)
        self.assertIn("sprödes", kurve.hinweis)

    def test_druck_erhoeht_den_widerstand(self):
        self.assertGreater(self.kurve_bei(-300e3).M_Rd, self.kurve.M_Rd)

    def test_zu_viel_druck_laesst_nichts_uebrig(self):
        kaputt = self.kurve_bei(-1e8)
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
        # Das Rissmoment bei N = -200 kN: 41.4 + 200·0.3/6 = 51.4 kNm, und
        # dort springt die Linie.
        kurve = faelle[2]["kurve"]
        self.assertAlmostEqual(kurve["M_Riss"], 51.4, delta=0.1)
        self.assertEqual(kurve["riss"]["M"], kurve["M_Riss"])
        self.assertGreater(kurve["riss"]["chi_nach"], kurve["riss"]["chi_vor"])

    def test_ein_ausgeschalteter_fall_wird_nicht_gerechnet(self):
        antwort = self.antwort(
            SpannungsfallEintrag(name="A", art="schnittgroessen", M_Ed=150.0),
            SpannungsfallEintrag(name="Aus", art="schnittgroessen", aktiv=False))
        self.assertEqual([f["name"] for f in
                          antwort.daten["spannungsanalysen"]["q1"]], ["A"])

    def test_eine_unbewehrte_richtung_sagt_warum(self):
        projekt = Projekt.beispiel()
        q = projekt.querschnitte[0]
        # x nach aussen legen und die y-Lagen leeren -- dann gibt es in y
        # nichts, woraus sich ein Bild bauen liesse.
        q.richtung_lage1 = q.richtung_lage4 = "x"
        for nummer in (2, 3):
            q.lagen[nummer - 1].grund.durchmesser = 0
            q.lagen[nummer - 1].zulage.durchmesser = 0
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
