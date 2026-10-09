"""
Den Querschnitt ansehen, ohne ihn nachzuweisen.

Geprüft wird nicht, ob eine Zahl stimmt -- die käme aus demselben
Faserintegral wie die Nachweise und wäre dort schon geprüft. Geprüft wird,
dass die Auswertungen **zueinander** passen: wer aus N und M eine Ebene
bekommt und sie zurückgibt, muss wieder bei N und M landen; wo eine Linie
endet, muss eine Grenzdehnung erreicht sein; und wo die Linie so rechnet wie
die Handrechnung -- Spannungsblock, ohne Druckbewehrung --, muss dasselbe
herauskommen.
"""

import dataclasses
import unittest

from opencivil import spannungsanalyse as sa
from opencivil.core.protokoll import GleichungBlock, Protokoll, TitelBlock
from opencivil.nachweis.querschnittsloeser import Werkstoffsatz
from opencivil.projekt import Projekt, ProjektFehler, SpannungsfallEintrag
from opencivil.querschnitt.platte import KRIECHZAHL, Richtung
from opencivil.web import dienst


def rechnen(projekt=None):
    """Aufbau und Lösung -- vom Beispiel, wenn kein Projekt gegeben ist."""
    aufbau = (projekt or Projekt.beispiel()).aufbauen()
    return aufbau, aufbau.werk.loese(*aufbau.alle_nachweisziele())


def loeserpaar(projekt=None, **wahl):
    """
    Die Platte q1 in x, zweimal -- gerissen und ungerissen.

    Ueber :func:`spannungsanalyse.loeserpaar`, dieselbe Funktion, die auch
    die Oberflaeche benutzt. Hier stand einmal eine eigene Kopie davon; der
    Test pruefte dann seine Kopie und nicht das, was gezeichnet wird.
    """
    aufbau, loesung = rechnen(projekt)
    return sa.loeserpaar(aufbau.querschnitte["q1"], Richtung.X,
                         lambda kid: loesung.werte[kid].groesse.si, **wahl)


def platte(name, **felder):
    """Ein Projekt mit einer Platte -- C30/37, B500B, ein Feldmoment."""
    projekt = Projekt(name=name)
    projekt.beton("C30/37")
    projekt.stahl("B500B")
    projekt.platte("Decke", h=300, **felder).einwirkung("Feld", M_Ed=100)
    return projekt


def ebene_am_ende(paar, linie):
    """Mitteldehnung und Krümmung beim Bruch einer M-χ-Linie."""
    chi = linie.bruch.verformung
    return paar.gerissen.mitteldehnung(chi, linie.fest), chi


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
        # Einmal für alle: die Linie kostet eine halbe Sekunde, und jeder
        # Test liest sie nur.
        cls.paar = loeserpaar()
        cls.kurve = sa.moment_kruemmung(cls.paar, N=0.0)

    def test_sie_reicht_von_null_bis_zum_bruch(self):
        punkte = self.kurve.punkte
        self.assertAlmostEqual(punkte[0].kraft, 0.0, delta=1.0)
        self.assertAlmostEqual(punkte[-1].kraft, self.kurve.bruch.kraft, delta=1.0)
        self.assertEqual(punkte[-1].verformung, self.kurve.bruch.verformung)

    def test_am_ende_ist_eine_grenzdehnung_erreicht(self):
        """
        Am Beispiel der Beton am oberen Rand bei −ε_c2d -- und eine Spur mehr
        Krümmung hat kein Gleichgewicht mehr. Bis 2026-10-09 endete die Linie
        dort, wo die Suche des Lösers aufgab: bei χ = 0.040 statt 0.057 1/m,
        mit −2.7 ‰ am Rand und 234.6 statt 235.4 kNm.
        """
        bruch = self.kurve.bruch
        self.assertAlmostEqual(bruch.eps_oben, -0.0035, delta=1e-7)
        self.assertIn("Beton am oberen Rand", bruch.massgebend)
        self.assertIn("−3.50 ‰", bruch.massgebend)
        eps_m, chi = ebene_am_ende(self.paar, self.kurve)
        self.assertAlmostEqual(eps_m - chi * self.paar.gerissen.h / 2, bruch.eps_oben, places=9)
        self.assertIsNone(self.paar.gerissen.mitteldehnung(chi * 1.001, 0.0))
        self.assertAlmostEqual(chi, 0.0565, delta=0.0005)
        self.assertAlmostEqual(bruch.kraft / 1e3, 235.4, delta=0.1)

    def test_der_fliessbeginn_liegt_bei_der_fliessdehnung(self):
        """
        Beim Fliessbeginn steht die am stärksten gezogene Lage genau auf
        ε_y = f_yd/E_s; das Moment wächst danach noch -- M_Rd,u gehört ans
        Ende, nicht hierher.
        """
        fliessen = self.kurve.fliessen
        chi = fliessen.verformung
        eps_m = self.paar.gerissen.mitteldehnung(chi, 0.0)
        halb = self.paar.gerissen.h / 2.0
        eps_s = max(eps_m + chi * (l.z - halb) for l in self.paar.gerissen.lagen)
        self.assertAlmostEqual(eps_s, self.paar.eps_y, delta=1e-9)
        self.assertLess(fliessen.kraft, self.kurve.bruch.kraft)
        self.assertIn(chi, [p.verformung for p in self.kurve.punkte])
        # Am Beispiel 224.6 kNm bei 0.0147 1/m.
        self.assertAlmostEqual(fliessen.kraft / 1e3, 224.6, delta=0.1)

    def test_die_kruemmung_waechst_mit_dem_moment(self):
        """
        Auch über den Sprung: Moment und Krümmung fallen nirgends zurück. Auf
        dem Plateau bis auf das, was die Suche offen lässt -- Bruchteile
        eines Newtonmeters.
        """
        punkte = self.kurve.punkte
        for vor, nach in zip(punkte, punkte[1:]):
            self.assertGreaterEqual(nach.kraft, vor.kraft - 0.01)
            self.assertGreater(nach.verformung, vor.verformung)

    def test_ungerissen_ist_steifer_als_gerissen(self):
        """Zustand I krümmt sich weniger -- darum springt die Linie beim Reissen nach rechts."""
        for p in self.kurve.punkte[1:]:
            if p.verformung_I is None:
                continue
            with self.subTest(M=round(p.kraft / 1e3)):
                self.assertLessEqual(p.verformung_I, p.verformung_II + 1e-12)

    def test_unter_dem_rissmoment_gilt_der_ungerissene_zustand(self):
        unten = [p for p in self.kurve.punkte if 0 < p.kraft < self.kurve.riss]
        self.assertTrue(unten)
        for p in unten:
            with self.subTest(M=round(p.kraft / 1e3)):
                self.assertFalse(p.gerissen)
                self.assertEqual(p.verformung, p.verformung_I)

    def test_darueber_gilt_der_gerissene_zustand(self):
        oben = [p for p in self.kurve.punkte if p.kraft > self.kurve.riss + 1.0]
        self.assertTrue(oben)
        for p in oben:
            with self.subTest(M=round(p.kraft / 1e3)):
                self.assertTrue(p.gerissen)
                self.assertEqual(p.verformung, p.verformung_II)

    def test_beim_rissmoment_springt_die_kruemmung(self):
        """
        Das waagrechte Stück: zwei Punkte beim selben Moment, vorher
        ungerissen, nachher gerissen. Vorher stand hier eine Linie mit
        Zugversteifung, die beim Rissmoment ohne Sprung weiterlief.
        """
        vor, nach = self.kurve.sprung
        self.assertEqual(vor.kraft, self.kurve.riss)
        self.assertAlmostEqual(nach.kraft, self.kurve.riss, delta=1.0)
        self.assertEqual(vor.verformung, vor.verformung_I)
        self.assertEqual(nach.verformung, nach.verformung_II)
        # Am Beispiel knapp das Doppelte: 0.00134 auf 0.00263 1/m.
        self.assertGreater(nach.verformung, 1.5 * vor.verformung)

    def test_das_rissmoment_gilt_bei_der_normalkraft_der_linie(self):
        """
        Beim Rissmoment erreicht der gezogene Rand des ungerissenen
        Querschnitts seine Zugspannung -- bei jeder Normalkraft fast dieselbe.
        Vorher galt immer das Rissmoment ohne Normalkraft: bei 200 kN Druck
        stand der Rand dann bei 1.65 statt 2.17 N/mm².
        """
        def randspannung(N):
            bild = sa.aus_schnittgroessen(self.paar.ungerissen, N=N,
                                          M=self.paar.rissmoment_bei(N))
            return bild.beton[-1].sigma
        ohne = randspannung(0.0)
        for N in (-200e3, 100e3):
            with self.subTest(N=N / 1e3):
                self.assertAlmostEqual(randspannung(N) / ohne, 1.0, delta=0.05)
        # Druck hebt das Rissmoment, Zug senkt es -- um N·h/6.
        self.assertAlmostEqual(sa.moment_kruemmung(self.paar, N=-200e3).riss - self.paar.M_Riss,
                               200e3 * self.paar.gerissen.h / 6.0, places=6)

    def test_reisst_schon_die_normalkraft_ist_alles_gerissen(self):
        """
        Am Beispiel erst ab gut 828 kN Zug, und schon ab rund 840 kN gibt es
        gar keine Gleichgewichtslage mehr -- zu eng für einen Test über N.
        Darum hier das Rissmoment direkt.
        """
        kurve = sa.moment_kruemmung(dataclasses.replace(self.paar, M_Riss=-1e3), N=0.0)
        self.assertTrue(kurve.punkte)
        self.assertTrue(all(p.gerissen for p in kurve.punkte))
        self.assertIsNone(kurve.sprung)
        self.assertIn("gerissen", kurve.hinweis)

    def test_liegt_das_rissmoment_ueber_m_rd_bleibt_alles_ungerissen(self):
        zu_hoch = dataclasses.replace(self.paar, M_Riss=10 * self.kurve.bruch.kraft)
        kurve = sa.moment_kruemmung(zu_hoch, N=0.0)
        self.assertTrue(kurve.punkte)
        self.assertFalse(any(p.gerissen for p in kurve.punkte))
        self.assertIsNone(kurve.sprung)
        self.assertIn("sprödes", kurve.hinweis)

    def test_druck_erhoeht_den_widerstand(self):
        self.assertGreater(sa.moment_kruemmung(self.paar, N=-300e3).bruch.kraft,
                           self.kurve.bruch.kraft)

    def test_zu_viel_druck_laesst_nichts_uebrig(self):
        kaputt = sa.moment_kruemmung(self.paar, N=-1e8)
        self.assertFalse(kaputt.tragfaehig)
        self.assertIn("Gleichgewichtslage", kaputt.hinweis)


class TestGegenDieHandrechnung(unittest.TestCase):
    """
    Die Handrechnung des M-N-Nachweises setzt den Spannungsblock 0.85·x an
    und lässt gedrückten Stahl weg. Rechnet die Linie mit Bemessungswerten
    und dem Block an einer Platte ohne Druckbewehrung, rechnet sie dasselbe
    -- und muss dasselbe M_Rd(N = 0) finden.
    """

    def widerstand(self, projekt):
        aufbau, loesung = rechnen(projekt)
        eckwert = aufbau.nachweise["q1.x"].d_eckwerte["M_Rd_N0_pos"]
        paar = sa.loeserpaar(aufbau.querschnitte["q1"], Richtung.X,
                             lambda kid: loesung.werte[kid].groesse.si, gesetz="block")
        return (sa.moment_kruemmung(paar, N=0.0).bruch.kraft,
                loesung.werte[eckwert.id].groesse.si)

    def test_ohne_druckbewehrung_ist_es_die_handrechnung(self):
        linie, hand = self.widerstand(platte("Ohne Druckbewehrung", x=[18, 0], y=[12, 12]))
        # Am Stück 170.0 kNm.
        self.assertAlmostEqual(linie / hand, 1.0, delta=0.001)

    def test_mit_druckbewehrung_traegt_die_linie_mehr(self):
        """Am Beispiel 236.2 statt 235.9 kNm: der obere Stahl trägt mit."""
        linie, hand = self.widerstand(None)
        self.assertGreater(linie, hand)


class TestWahl(unittest.TestCase):
    """Kriechzahl, Wertesatz und Betongesetz -- je Analyse gewählt."""

    @classmethod
    def setUpClass(cls):
        cls.platte = loeserpaar()

    def test_ohne_eigene_kriechzahl_gilt_die_der_platte(self):
        self.assertEqual(self.platte.phi, KRIECHZAHL)
        self.assertFalse(self.platte.phi_eigen)
        self.assertIn("phi", self.platte.ids)

    def test_die_kriechzahl_der_analyse_gilt(self):
        """Ohne Kriechen ist der Beton steifer, und die Linie krümmt sich weniger."""
        eigen = loeserpaar(phi=0.0)
        self.assertEqual(eigen.phi, 0.0)
        self.assertTrue(eigen.phi_eigen)
        self.assertNotIn("phi", eigen.ids)
        steif = eigen.ungerissen.loese(N_Ed=0.0, M_Ed=20e3).chi
        weich = self.platte.ungerissen.loese(N_Ed=0.0, M_Ed=20e3).chi
        self.assertLess(steif, 0.5 * weich)

    def test_charakteristisch_traegt_mehr(self):
        """f_ck und f_yk statt f_cd und f_yd: Widerstand und Fliessbeginn liegen höher."""
        k = loeserpaar(satz=Werkstoffsatz.CHARAKTERISTISCH)
        self.assertGreater(k.eps_y, self.platte.eps_y)
        self.assertGreater(sa.moment_kruemmung(k, N=0.0).bruch.kraft,
                           sa.moment_kruemmung(self.platte, N=0.0).bruch.kraft)

    def test_eine_alte_datei_rechnet_wie_vorher(self):
        """Ohne die neuen Felder: die Kriechzahl der Platte, Bemessungswerte, die Parabel."""
        alt = SpannungsfallEintrag.aus_dict({"name": "alt", "art": "moment_kruemmung"})
        self.assertIsNone(alt.kriechzahl)
        self.assertEqual(alt.werkstoffsatz, "bemessung")
        self.assertEqual(alt.betongesetz, "parabel")
        projekt = Projekt.beispiel()
        projekt.querschnitte[0].spannungsfaelle = [alt]
        analyse = projekt.rechnen().analysen()["q1"][0]
        self.assertFalse(analyse.paar.phi_eigen)
        self.assertEqual(analyse.paar.phi, KRIECHZAHL)
        self.assertIs(analyse.paar.satz, Werkstoffsatz.BEMESSUNG)
        self.assertEqual(analyse.paar.gesetz, "parabel")

    def test_was_es_nicht_gibt_meldet_sich(self):
        for feld, wert in (("art", "kreis"), ("werkstoffsatz", "mittel"),
                           ("betongesetz", "dreieck"), ("kriechzahl", -1.0)):
            with self.subTest(feld=feld):
                with self.assertRaises(ProjektFehler):
                    SpannungsfallEintrag.aus_dict({"name": "x", feld: wert})
        with self.assertRaises(ProjektFehler):
            Projekt.beispiel().querschnitte[0].spannungsfall("x", betongesetz="dreieck")

    def test_eine_leere_kriechzahl_ist_die_der_platte(self):
        """Die Oberfläche schickt ein leeres Feld als leeren Text."""
        self.assertIsNone(SpannungsfallEintrag.aus_dict({"name": "x", "kriechzahl": ""}).kriechzahl)


class TestNormalkraftDehnung(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Symmetrisch bewehrt: ⌀18 aussen oben und unten, ⌀12 innen in y.
        # Mit ⌀12 aussen trüge der Stahl nur 656 kN, und der Querschnitt
        # risse erst bei 829 kN -- er bliebe bis zum Bruch ungerissen.
        cls.sym = loeserpaar(platte("Symmetrisch", x=[18, 18], y=[12, 12]))
        cls.kurve = sa.normalkraft_dehnung(cls.sym, M=0.0)

    def test_ohne_moment_reisst_er_bei_f_ct_eff_mal_b_mal_h(self):
        h, b = self.sym.gerissen.h, self.sym.gerissen.b
        self.assertAlmostEqual(self.kurve.riss, self.sym.f_ct_eff * b * h, delta=1e-6)

    def test_das_moment_senkt_die_rissnormalkraft(self):
        """Dieselbe Bedingung wie beim Rissmoment -- das Vorzeichen zählt nicht."""
        h = self.sym.gerissen.h
        for M in (20e3, -20e3):
            with self.subTest(M=M / 1e3):
                self.assertAlmostEqual(self.sym.rissnormalkraft_bei(M),
                                       self.kurve.riss - 6.0 * 20e3 / h, delta=1e-6)

    def test_symmetrisch_traegt_am_ende_der_ganze_stahl(self):
        """N_Rd = Σ A_s · f_yd -- und die Lagen stehen auf ε_ud."""
        f_yd = self.sym.gerissen.stahl(0.01)
        summe = sum(l.a_s for l in self.sym.gerissen.lagen) * f_yd
        bruch = self.kurve.bruch
        self.assertAlmostEqual(bruch.kraft / summe, 1.0, delta=1e-6)
        eps_ud = max(g.eps_max for g in self.sym.gerissen.grenzen.grenzen
                     if g.eps_max != float("inf"))
        self.assertAlmostEqual(bruch.verformung, eps_ud, delta=1e-9)
        self.assertIn("Stahl der", bruch.massgebend)

    def test_die_linie_steigt_und_springt_beim_riss(self):
        punkte = self.kurve.punkte
        for vor, nach in zip(punkte, punkte[1:]):
            self.assertGreaterEqual(nach.kraft, vor.kraft - 0.01)
            self.assertGreaterEqual(nach.verformung, vor.verformung)
        vor, nach = self.kurve.sprung
        self.assertEqual(vor.kraft, self.kurve.riss)
        self.assertGreater(nach.verformung, 2.0 * vor.verformung)

    def test_mit_moment_und_unsymmetrisch_endet_sie_im_beton(self):
        """
        Das Beispiel hat unten 2450, oben 754 mm² Stahl. Bei 20 kNm um die
        halbe Höhe fliessen beide Lagen, und der untere Rand wird gedrückt,
        bis er −ε_c2d erreicht -- bei 1030 kN, nicht bei Σ A_s · f_yd =
        1393 kN. Die erreichte man nur beim Moment, das der Stahlschwerpunkt
        verlangt, rund 71 kNm.
        """
        paar = loeserpaar()
        kurve = sa.normalkraft_dehnung(paar, M=20e3)
        self.assertIn("Beton am unteren Rand", kurve.bruch.massgebend)
        self.assertAlmostEqual(kurve.bruch.kraft / 1e3, 1030.0, delta=1.0)
        self.assertLess(kurve.fliessen.kraft, kurve.bruch.kraft)

    def test_traegt_er_das_moment_nicht_gibt_es_keine_linie(self):
        kurve = sa.normalkraft_dehnung(self.sym, M=1e9)
        self.assertFalse(kurve.tragfaehig)
        self.assertIn("Moment allein", kurve.hinweis)


class TestHerleitung(unittest.TestCase):
    def test_jede_linie_schreibt_wie_sie_entstand(self):
        projekt = Projekt.beispiel()
        decke = projekt.querschnitte[0]
        decke.spannungsfall("Biegung", art="moment_kruemmung")
        decke.spannungsfall("Zug", art="normalkraft_dehnung", M_Ed=20.0)
        decke.spannungsfall("Bild", art="schnittgroessen", M_Ed=100.0)
        aufbau, loesung = rechnen(projekt)
        p = Protokoll()
        sa.analysen(aufbau, loesung, p)
        titel = [b.text for b in p.bloecke if isinstance(b, TitelBlock)]
        self.assertEqual(titel, [f"{sa.THEMA}: Biegung", f"{sa.THEMA}: Zug"])
        latex = " ".join(b.latex for b in p.bloecke if isinstance(b, GleichungBlock))
        self.assertIn(r"\chi_{u}", latex)
        self.assertIn(r"N_{Riss}(M)", latex)
        self.assertTrue(all(b.thema == sa.THEMA for b in p.bloecke
                            if not isinstance(b, TitelBlock)))


class TestUeberDenDienst(unittest.TestCase):
    def antwort(self, *faelle):
        projekt = Projekt.beispiel()
        projekt.querschnitte[0].spannungsfaelle = list(faelle)
        return dienst.bearbeite("rechnen", {"projekt": projekt.als_dict()})

    def test_alle_vier_arten_kommen_durch(self):
        antwort = self.antwort(
            SpannungsfallEintrag(name="A", art="schnittgroessen", M_Ed=150.0),
            SpannungsfallEintrag(name="B", art="dehnungen",
                                 eps_oben=-1.5, eps_unten=3.0),
            SpannungsfallEintrag(name="C", art="moment_kruemmung", N_Ed=-200.0),
            SpannungsfallEintrag(name="D", art="normalkraft_dehnung", M_Ed=20.0,
                                 kriechzahl=1.0, betongesetz="block"))
        self.assertEqual(antwort.status, 200)
        faelle = antwort.daten["spannungsanalysen"]["q1"]
        self.assertEqual([f["name"] for f in faelle], ["A", "B", "C", "D"])
        self.assertIn("bild", faelle[0])
        self.assertIn("bild", faelle[1])
        # In Zeichengrössen: mm, Promille, kN.
        self.assertAlmostEqual(faelle[0]["bild"]["M"], 150.0, delta=0.5)
        self.assertAlmostEqual(faelle[0]["bild"]["h"], 300.0, delta=0.1)
        # Das Rissmoment bei N = -200 kN: 41.4 + 200·0.3/6 = 51.4 kNm, und
        # dort springt die Linie.
        kurve = faelle[2]["kurve"]
        self.assertAlmostEqual(kurve["riss"], 51.4, delta=0.1)
        self.assertEqual(kurve["sprung"]["kraft"], kurve["riss"])
        self.assertGreater(kurve["sprung"]["nach"], kurve["sprung"]["vor"])
        self.assertLess(kurve["fliessen"]["kraft"], kurve["bruch"]["kraft"])
        self.assertIn("massgebend", kurve["bruch"])
        self.assertEqual(faelle[2]["wahl"], {"phi": KRIECHZAHL, "phi_eigen": False,
                                             "satz": "bemessung", "gesetz": "parabel"})
        # Die N-ε-Linie in kN und Promille: N_Riss(20 kNm) = (41.4 - 20)·6/0.3.
        kurve = faelle[3]["kurve"]
        self.assertAlmostEqual(kurve["riss"], (41.43 - 20.0) * 20.0, delta=1.0)
        self.assertGreater(kurve["bruch"]["verformung"], 1.0)
        self.assertEqual(faelle[3]["wahl"]["phi"], 1.0)
        self.assertTrue(faelle[3]["wahl"]["phi_eigen"])
        self.assertEqual(faelle[3]["wahl"]["gesetz"], "block")

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
