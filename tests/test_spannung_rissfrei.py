"""
Die Spannung-Dehnung-Analysen eines Querschnitts ohne Beton (2026-11-26):
aus Holz oder Baustahl reisst er nicht, und seine Linie laeuft ohne Sprung
bis zum Bruch. Im Verbund rechnen sie noch nicht.

Von Hand, das Rechteck 200 × 400 mm: A = 80 000 mm², W = 200 · 400² / 6
= 5.333 · 10⁶ mm³, I = 1 066.7 · 10⁶ mm⁴.

Holz C24 mit Bemessungswerten (SIA 265:2012, Tabelle 6): f_t,0,d = 8,
f_c,0,d = 12, E_0,mean = 11 000 N/mm².

* M-chi ohne Normalkraft: der gezogene Rand bricht zuerst,
  M_Rd = 8 · 5.333 · 10⁶ = 42.67 kNm, chi_u = 2 · (8 / 11 000) / 0.4 m
  = 0.003636 1/m.
* M-chi mit N = -300 kN: sigma_N = -3.75 N/mm², der gedrueckte Rand
  erreicht f_c,0,d bei M = (12 - 3.75) · W = 44.00 kNm. Linear endet die
  Linie dort; elastisch-plastisch fliesst er dort und traegt weiter, bis der
  gezogene Rand bei 0.727 ‰ bricht. Am Ende ist der Rand oben bei
  -1.476 ‰: 70.0 mm plastisch (12 · 70.0 · 200 = 167.9 kN), 198.0 mm
  elastisch gedrueckt (237.6 kN), 132.0 mm gezogen (105.6 kN). Das gibt
  N = -299.9 kN und M = 16.47 + 15.21 + 27.71 = 59.4 kNm.
* N-eps auf Zug: N_Rd = 8 · 80 000 = 640 kN.

Baustahl S355 mit Bemessungswerten: f_yd = 355 / 1.05 = 338.1 N/mm²,
E_a = 210 000 N/mm².

* M_el = 338.1 · 5.333 · 10⁶ = 1 803 kNm, M_pl = 338.1 · 200 · 400² / 4
  = 2 705 kNm. Die Linie endet bei der Grenzdehnung kurz vor M_pl.
* N_pl = 338.1 · 80 000 = 27 048 kN.

Der aequivalente Modul ist, solange keine Faser fliesst, der Modul des
Materials -- bis auf die Fasern: gerechnet wird je Streifen in seiner
Mitte, und so fehlen 0.03 % (E · (1 - 1/n²)).
"""

import unittest

from opencivil import spannungsanalyse as sa
from opencivil.core.protokoll import GleichungBlock, Protokoll, TextBlock, TitelBlock
from opencivil.projekt import Projekt, QuerschnittsanalyseEintrag
from opencivil.web import dienst
from opencivil.web.api import katalog

RECHTECK = [[0, 0], [200, 0], [200, 400], [0, 400]]
BLECH = [[50, 100], [150, 100], [150, 300], [50, 300]]
W = 200 * 400 ** 2 / 6 * 1e-9
F_YD = 355e6 / 1.05


def projekt(material, holz="linear"):
    """Das Rechteck aus ``material`` mit je einem Fall jeder Art."""
    p = Projekt(name="Ohne Beton")
    p.beton("C30/37")
    p.stahl("B500B")
    p.baustahl("S355")
    p.holz("C24")
    a = QuerschnittsanalyseEintrag.neu(kennung="a1", name="Rechteck")
    a.polygon(RECHTECK, material=material)
    a.spannungsfall("Biegung", art="moment_kruemmung", N_Ed=0.0)
    a.spannungsfall("Biegung mit Druck", art="moment_kruemmung", N_Ed=-300.0)
    a.spannungsfall("Zug", art="normalkraft_dehnung", M_Ed=0.0)
    a.spannungsfall("Steifigkeit", art="moment_emodul", N_Ed=0.0)
    a.spannungsfall("Bild", art="schnittgroessen", N_Ed=0.0, M_Ed=20.0)
    for s in a.spannungsfaelle:
        s.holzrechnungen = {"h1": holz}
    p.querschnittsanalysen.append(a)
    return p


def analysen(p, protokoll=None):
    """Je Fall die Auswertung, nach seinem Namen."""
    aufbau = p.aufbauen()
    loesung = aufbau.werk.loese(*aufbau.alle_ziele())
    return {a.fall.name: a for a in sa.analysen(aufbau, loesung, protokoll)["a1"]}


class TestHolz(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.linear = analysen(projekt("h1"))
        cls.plastisch = analysen(projekt("h1", "plastisch"))

    def test_ohne_riss_bis_zum_bruch(self):
        linie = self.linear["Biegung"].kurve
        self.assertIsNone(linie.riss)
        self.assertIsNone(linie.sprung)
        self.assertTrue(linie.am_bruch)
        self.assertTrue(all(not p.gerissen and p.verformung_I is None
                            for p in linie.punkte))

    def test_der_gezogene_rand_bricht(self):
        bruch = self.linear["Biegung"].kurve.bruch
        self.assertAlmostEqual(bruch.kraft / 1e3, 8 * W * 1e3, places=1)
        self.assertAlmostEqual(bruch.verformung, 2 * 8 / 11000 / 0.4, places=5)
        self.assertEqual(bruch.massgebend, "Holz C24, Rand unten bei 0.73 ‰")

    def test_linear_ist_m_gleich_e_i_chi(self):
        linie = self.linear["Biegung"].kurve
        EI = 11000e6 * 200 * 400 ** 3 / 12 * 1e-12
        for p in linie.punkte[1:]:
            self.assertAlmostEqual(p.kraft / (EI * p.verformung), 1.0, delta=1e-3)

    def test_linear_endet_unter_druck_am_gedrueckten_rand(self):
        linie = self.linear["Biegung mit Druck"].kurve
        self.assertAlmostEqual(linie.bruch.kraft / 1e3, (12 - 3.75) * W * 1e3, places=1)
        self.assertIsNone(linie.fliessen)
        self.assertIn("Rand oben", linie.bruch.massgebend)
        self.assertEqual(linie.hinweis, self.linear["Biegung"].paar.OHNE_FLIESSEN)

    def test_plastisch_fliesst_er_und_traegt_weiter(self):
        linie = self.plastisch["Biegung mit Druck"].kurve
        self.assertAlmostEqual(linie.fliessen.kraft / 1e3, 44.0, places=1)
        self.assertAlmostEqual(linie.bruch.kraft / 1e3, 59.4, delta=0.1)
        self.assertAlmostEqual(linie.bruch.eps_oben * 1e3, -1.476, delta=0.002)
        self.assertIn("Rand unten", linie.bruch.massgebend)

    def test_ohne_normalkraft_aendert_plastisch_nichts(self):
        """Auf Zug bricht das Holz, bevor der Druck fliesst: f_t,0,d < f_c,0,d."""
        self.assertAlmostEqual(self.plastisch["Biegung"].kurve.bruch.kraft,
                               self.linear["Biegung"].kurve.bruch.kraft, delta=1.0)

    def test_zug(self):
        self.assertAlmostEqual(self.linear["Zug"].kurve.bruch.kraft / 1e3, 640.0, places=1)

    def test_der_modul_ist_e_0_mean(self):
        modul = self.linear["Steifigkeit"].kurve
        self.assertEqual(modul.bezug.zeichen, "E_{0,mean}")
        self.assertAlmostEqual(modul.bezug.E / 1e6, 11000.0)
        for p in modul.punkte[1:]:
            self.assertAlmostEqual(p.modul / modul.bezug.E, 1.0, delta=1e-3)

    def test_das_bild_ohne_bewehrung(self):
        bild = self.linear["Bild"].bild
        self.assertEqual(bild.stahl, [])
        self.assertAlmostEqual(bild.flaeche[-1].sigma / 1e6, 20e3 / W / 1e6, delta=0.05)


class TestStahl(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.faelle = analysen(projekt("st1"))

    def test_fliessen_bei_m_el_ende_kurz_vor_m_pl(self):
        linie = self.faelle["Biegung"].kurve
        self.assertIsNone(linie.riss)
        self.assertAlmostEqual(linie.fliessen.kraft / (F_YD * W), 1.0, delta=1e-3)
        M_pl = F_YD * 200 * 400 ** 2 / 4 * 1e-9
        self.assertTrue(0.99 * M_pl < linie.bruch.kraft < M_pl)
        self.assertTrue(linie.bruch.massgebend.startswith("Baustahl S355, Rand "))

    def test_n_pl(self):
        self.assertAlmostEqual(self.faelle["Zug"].kurve.bruch.kraft / (F_YD * 0.08), 1.0,
                               delta=1e-4)

    def test_der_modul_faellt_erst_beim_fliessen(self):
        modul = self.faelle["Steifigkeit"].kurve
        self.assertEqual(modul.bezug.zeichen, "E_a")
        self.assertAlmostEqual(modul.bezug.E / 1e6, 210000.0)
        self.assertAlmostEqual(modul.fliessen / modul.bezug.E, 1.0, delta=1e-3)
        self.assertLess(modul.ende, 0.2 * modul.bezug.E)


class TestHerleitung(unittest.TestCase):
    def test_holz_ohne_riss(self):
        p = Protokoll()
        analysen(projekt("h1", "plastisch"), p)
        titel = [b.text for b in p.bloecke if isinstance(b, TitelBlock)]
        self.assertIn(f"{sa.THEMA}: Biegung mit Druck", titel)
        texte = " ".join(b.text for b in p.bloecke if isinstance(b, TextBlock))
        self.assertIn("Ohne Beton reisst der Querschnitt nicht", texte)
        self.assertIn("Das Holz rechnet immer mit Bemessungswerten.", texte)
        formeln = [b.titel for b in p.bloecke if isinstance(b, GleichungBlock)]
        self.assertIn("Dehnung bei Fliessbeginn, C24", formeln)
        self.assertFalse([t for t in formeln if "Riss" in t])


class TestOberflaeche(unittest.TestCase):
    """Was die Seite bekommt: ohne Riss, ohne Kriechzahl, mit dem Modul des Materials."""

    @classmethod
    def setUpClass(cls):
        def faelle(material):
            antwort = dienst.bearbeite("rechnen", {"projekt": projekt(material).als_dict()})
            return {f["name"]: f for f in antwort.daten["spannungsanalysen"]["a1"]}
        cls.holz, cls.stahl = faelle("h1"), faelle("st1")

    def test_werkstoff_und_wahl(self):
        for faelle, werkstoff, rechenart in ((self.holz, "Holz", "Linear bis zum Bruch"),
                                             (self.stahl, "Baustahl", "")):
            with self.subTest(werkstoff=werkstoff):
                fall = faelle["Biegung"]
                self.assertEqual(fall["werkstoff"], werkstoff)
                self.assertEqual(fall["wahl"]["phi"], None)
                self.assertEqual(fall["wahl"]["werte"], "Bemessungswerte")
                self.assertEqual(fall["wahl"]["rechenart"], rechenart)

    def test_die_linie_ohne_riss(self):
        kurve = self.holz["Biegung"]["kurve"]
        self.assertEqual((kurve["riss"], kurve["sprung"], kurve["am_bruch"]), (None, None, True))

    def test_der_bezug_des_moduls(self):
        bezug = self.holz["Steifigkeit"]["kurve"]["bezug"]
        self.assertEqual((bezug["zeichen"], bezug["text"], bezug["wert"]),
                         ("E_{0,mean}", "E_0,mean", 11000.0))
        self.assertTrue(bezug["hinweis"].endswith("ist es E_0,mean."))

    def test_das_bild_mit_flaeche(self):
        bild = self.stahl["Bild"]["bild"]
        self.assertGreater(len(bild["flaeche"]), 2)
        self.assertEqual(bild["stahl"], [])

    def test_der_katalog(self):
        wahl = katalog()["rechenwahl"]
        self.assertEqual(wahl["satztitel"]["baustahl"],
                         "Bemessungswert f_yd oder charakteristischer f_y")
        self.assertNotIn("holz", wahl["satztitel"])
        self.assertEqual([h["wert"] for h in wahl["holzrechnungen"]], ["linear", "plastisch"])


class TestVerbund(unittest.TestCase):
    """Beton mit einem Blech aus Baustahl: die Analysen warten auf SIA 264."""

    def setUp(self):
        self.p = projekt("b1")
        a = self.p.querschnittsanalysen[0]
        a.polygon(BLECH, material="st1")
        a.stab(100, 50, durchmesser=20, stahl="s1")

    def test_keine_analyse(self):
        self.assertNotIn("a1", self.p.aufbauen().spannungsfaelle)

    def test_der_satz_fuer_die_kacheln(self):
        antwort = dienst.geometrie({"projekt": self.p.als_dict(), "kennung": "a1"})
        self.assertEqual(antwort["ohne_analysen"],
                         "Einen Verbundquerschnitt rechnen die Spannung-Dehnung-Analysen noch "
                         "nicht.")
        holz = dienst.geometrie({"projekt": projekt("h1").als_dict(), "kennung": "a1"})
        self.assertEqual(holz["ohne_analysen"], "")


if __name__ == "__main__":
    unittest.main()
