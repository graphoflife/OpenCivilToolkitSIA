"""
Tests fuer die Verduebelung nach SIA 264:2014, 6.1 (Plan vom 2026-11-25,
Schritt 14b): Kopfbolzenduebel, ihr Schubwiderstand, der
Verduebelungsgrad gegen (29) und die Teilverduebelung.

Von Hand, am IPE 300 aus S355 unter der Platte 1500 × 120 mm aus C30/37
wie in :mod:`tests.test_verbund`, mit Duebeln ⌀19, f_u = 450 N/mm²:

* (30): 0.29 · 19² · √(30 · E_cm) / 1.25, E_cm = 10000 · 38^(1/3) nach
  SIA 262, (10); (31): 0.8 · 450 · π · 19²/4 / 1.25 -- (31) ist kleiner.
* Bei voller Verduebelung liegt die Nulllinie in der Platte: der Beton
  traegt N_c,f = N_a = A_a f_yd, die Duebel muessen das tragen,
  N_f = N_a / P_Rd. η = N / N_f.
* (29) mit L_e = 10 m: 1 - 355/355 · (0.75 - 0.3) = 0.55.
* Teilverduebelt traegt die Platte nur F = N · P_Rd, gedrueckt ueber
  a = F/(1500 · 17); das Profil zieht N_a - 2 C_a, mit C_a = (N_a - F)/2
  im oberen Flansch, t = C_a/(150 f_yd) tief. Um z = 0:
  M = -N_a · 150 + 2 C_a (300 - t/2) + F (420 - a/2).
"""

import math
import unittest

from opencivil.bericht.markdown import als_markdown
from opencivil.core.bereich import Bereich
from opencivil.core.einheiten import MM
from opencivil.nachweis.qa_verbund import (
    KAMMER, NEGATIV, OHNE_ANZAHL, OHNE_L_E, OHNE_MOMENT, UNSYMMETRISCH,
)
from opencivil.nachweis.qa_verbund_kennzahlen import verbund_von
from opencivil.projekt.lesen import feldangaben
from opencivil.projekt.querschnittsanalyse import QuerschnittsanalyseEintrag
from opencivil.verbund import duebel as vd
from opencivil.verbund.querschnitt import IN_DER_KAMMER
from tests.test_stahlbau import rechteck
from tests.unfertig import meldung
from tests.test_stahlprofile_qa import analyse, projekt
from tests.test_verbund import BETON, F_355, GENAU, IPE, PLATTE, grad, stahl_allein

#: Der Elastizitaetsmodul von C30/37 und C20/25 nach SIA 262, (10), in N/mm².
E_CM_30 = 10000.0 * 38.0 ** (1.0 / 3.0)
E_CM_20 = 10000.0 * 28.0 ** (1.0 / 3.0)

#: (31) mit ⌀19 und f_u = 450 N/mm², in N.
P_SCHAFT = 0.8 * 450.0 * math.pi * 19.0 ** 2 / 4.0 / 1.25

#: Der Betonstahl der Platte, ⌀20 B500B, gezogen in N.
T_STAB = math.pi * 10.0 ** 2 * 500.0 / 1.15

#: Das HEA 300 mit Beton zwischen den Flanschen und der Platte darueber.
HEA = (0, 145, "HEA 300", {})
KAMMERBETON = ([(-150, 0), (150, 0), (150, 290), (750, 290), (750, 410), (-750, 410),
                (-750, 290), (-150, 290)], "b1")


def rechnen(*profile, faelle, polygone=(PLATTE,), duebel=None, staebe=()):
    """
    Wie :func:`tests.test_verbund.rechnen`, mit Kopfbolzenduebeln --
    ``duebel`` ihre Felder, ``staebe`` je (y, z) ein ⌀20 B500B --, dazu der
    Bericht als Markdown.
    """
    p = projekt()
    p.beton("C20/25")
    p.beton("C50/60")
    a = analyse(p, *(profile or (IPE,)), polygone=polygone)
    a.einachsig = True
    a.verduebelung = vd.Verduebelung.KOPFBOLZEN
    for feld, wert in (duebel or {}).items():
        setattr(a, feld, wert)
    for y, z in staebe:
        a.stab(y, z, durchmesser=20, stahl="s1")
    for name, werte in faelle.items():
        a.lastfall(name, **werte)
    aufbau = p.aufbauen()
    teil = aufbau.teile[a.kennung]
    loesung = aufbau.werk.loese(*teil.ziele())
    werte = {}
    for k in teil.kennzahlen:
        w = loesung.wert(k.definition.id)
        werte[k.definition.id.rsplit(".", 1)[1]] = w.in_einheit(w.einheit)
    urteile = {(u.art, u.fall): u for u in loesung.urteile}
    return werte, urteile, als_markdown(loesung), verbund_von(teil.objekt)


class TestSchubwiderstand(unittest.TestCase):
    """P_Rd nach 6.1.2.1: der kleinere aus (30) und (31)."""

    def test_versagen_des_duebels(self):
        k, _, _, _ = rechnen(faelle={})
        stauchung = 0.29 * 19.0 ** 2 * math.sqrt(30.0 * E_CM_30) / 1.25
        self.assertGreater(stauchung, P_SCHAFT)
        self.assertAlmostEqual(k["P_Rd"], P_SCHAFT / 1e3, delta=1e-3)

    def test_betonstauchung_im_schwachen_beton(self):
        """⌀16 in C20/25: (30) ist kleiner -- der schwaechste Beton zaehlt."""
        platte = (rechteck(-750, 300, 1500, 120), "b2")
        k, _, text, _ = rechnen(faelle={}, polygone=(platte,), duebel={"duebel_d": 16.0})
        stauchung = 0.29 * 16.0 ** 2 * math.sqrt(20.0 * E_CM_20) / 1.25
        schaft = 0.8 * 450.0 * math.pi * 16.0 ** 2 / 4.0 / 1.25
        self.assertLess(stauchung, schaft)
        self.assertAlmostEqual(k["P_Rd"], stauchung / 1e3, delta=1e-3)
        self.assertIn("Betonstauchung, C20/25", text)

    def test_f_u_zaehlt_hoechstens_500(self):
        """f_u = 520 in C50/60: (31) mit 500 N/mm² ist kleiner als (30)."""
        platte = (rechteck(-750, 300, 1500, 120), "b3")
        k, _, text, _ = rechnen(faelle={}, polygone=(platte,), duebel={"duebel_f_u": 520.0})
        schaft = 0.8 * 500.0 * math.pi * 19.0 ** 2 / 4.0 / 1.25
        E_cm = 10000.0 * 58.0 ** (1.0 / 3.0)
        self.assertLess(schaft, 0.29 * 19.0 ** 2 * math.sqrt(50.0 * E_cm) / 1.25)
        self.assertAlmostEqual(k["P_Rd"], schaft / 1e3, delta=1e-3)
        self.assertIn("(31) rechnet mit höchstens 500 N/mm²", text)

    def test_ohne_kopfbolzen_keine_kennzahl(self):
        p = projekt()
        a = analyse(p, IPE, polygone=(PLATTE,))
        teil = p.aufbauen().teile[a.kennung]
        self.assertNotIn("P_Rd", [k.definition.id.rsplit(".", 1)[1] for k in teil.kennzahlen])


class TestVerduebelungsgrad(unittest.TestCase):
    """η = N / N_f gegen (29) -- im Feld, mit und ohne Angaben."""

    @classmethod
    def setUpClass(cls):
        cls.N_a = stahl_allein()["N_Rd_zug"] * 1e3
        cls.k, cls.urteile, cls.text, _ = rechnen(faelle={
            "genug": {"M_y_Ed": 300.0, "duebelzahl": 20, "L_e": 10.0},
            "zu wenig": {"M_y_Ed": 300.0, "duebelzahl": 10, "L_e": 10.0},
            "kurz": {"M_y_Ed": 300.0, "duebelzahl": 10, "L_e": 5.0},
            "weit": {"M_y_Ed": 300.0, "duebelzahl": 20, "L_e": 30.0},
            "ohne Zahl": {"M_y_Ed": 300.0},
            "ohne L_e": {"M_y_Ed": 300.0, "duebelzahl": 20},
            "Zug": {"N_Ed": 500.0, "duebelzahl": 5},
        })

    def eta(self, anzahl):
        return anzahl * P_SCHAFT / self.N_a

    def test_29_von_hand(self):
        self.assertAlmostEqual(vd.eta_min(355.0, 10.0), 0.55, delta=1e-12)
        self.assertAlmostEqual(vd.eta_min(460.0, 10.0), 1.0 - 355.0 / 460.0 * 0.45, delta=1e-12)
        self.assertEqual(vd.eta_min(355.0, 5.0), 0.4)
        self.assertEqual(vd.eta_min(355.0, 25.5), 1.0)

    def test_genug_duebel(self):
        u = self.urteile["Dübel", "genug"]
        self.assertTrue(u.erfuellt)
        self.assertAlmostEqual(grad(u), self.eta(20) / 0.55, delta=GENAU)

    def test_zu_wenig_duebel(self):
        u = self.urteile["Dübel", "zu wenig"]
        self.assertFalse(u.erfuellt)
        self.assertAlmostEqual(grad(u), self.eta(10) / 0.55, delta=GENAU)

    def test_kurz_bis_0_4(self):
        self.assertAlmostEqual(grad(self.urteile["Dübel", "kurz"]), self.eta(10) / 0.4,
                               delta=GENAU)

    def test_ueber_25_m_voll(self):
        self.assertAlmostEqual(grad(self.urteile["Dübel", "weit"]), self.eta(20), delta=GENAU)

    def test_ohne_zahl_grau_und_voll_verduebelt(self):
        u = self.urteile["Dübel", "ohne Zahl"]
        self.assertEqual((u.erfuellt, u.hinweis), (False, OHNE_ANZAHL))
        self.assertAlmostEqual(grad(self.urteile["M-N", "ohne Zahl"]),
                               self.k["M_Rd_unten"] / 300.0, delta=GENAU)

    def test_ohne_l_e_grau(self):
        u = self.urteile["Dübel", "ohne L_e"]
        self.assertEqual((u.erfuellt, u.hinweis), (False, OHNE_L_E))

    def test_ohne_moment_keine_pruefung(self):
        self.assertNotIn(("Dübel", "Zug"), self.urteile)
        self.assertIn(OHNE_MOMENT, self.text)


class TestTeilverduebelung(unittest.TestCase):
    """Die Platte traegt nur N · P_Rd: M_Rd von Hand."""

    def test_von_hand(self):
        N_a = stahl_allein()["N_Rd_zug"] * 1e3
        k, urteile, text, _ = rechnen(faelle={
            "Feld": {"M_y_Ed": 300.0, "duebelzahl": 10, "L_e": 5.0}})
        F = 10 * P_SCHAFT
        a = F / (1500.0 * BETON)
        C_a = (N_a - F) / 2.0
        t = C_a / (150.0 * F_355)
        self.assertLess(t, 10.7)
        M = (-N_a * 150.0 + 2.0 * C_a * (300.0 - t / 2.0) + F * (420.0 - a / 2.0)) / 1e6
        self.assertLess(M, k["M_Rd_unten"])
        u = urteile["M-N", "Feld"]
        self.assertAlmostEqual(grad(u), M / 300.0, delta=GENAU)
        self.assertTrue(u.begruendung.startswith("Teilverdübelt"))
        self.assertIn("Kräfte mit Teilverdübelung", text)

    def test_genug_duebel_volle_verduebelung(self):
        k, urteile, _, _ = rechnen(faelle={"Feld": {"M_y_Ed": 300.0, "duebelzahl": 30}})
        u = urteile["M-N", "Feld"]
        self.assertAlmostEqual(grad(u), k["M_Rd_unten"] / 300.0, delta=GENAU)
        self.assertTrue(u.begruendung.startswith("Plastisch"))


class TestNegativesMoment(unittest.TestCase):
    """6.1.1.6: im negativen Moment volle Verduebelung."""

    def test_gezogener_betonstahl(self):
        _, urteile, text, _ = rechnen(staebe=[(0, 380)], faelle={
            "eins": {"M_y_Ed": -100.0, "duebelzahl": 1},
            "zwei": {"M_y_Ed": -100.0, "duebelzahl": 2, "L_e": 5.0}})
        for name, anzahl in (("eins", 1), ("zwei", 2)):
            with self.subTest(name=name):
                u = urteile["Dübel", name]
                self.assertAlmostEqual(grad(u), anzahl * P_SCHAFT / T_STAB, delta=GENAU)
                self.assertEqual(u.erfuellt, anzahl == 2)
        self.assertIn(NEGATIV, text)

    def test_kammerbeton_zaehlt_zum_stahl(self):
        """
        HEA 300 mit Kammerbeton, oben gezogen: der Kammerbeton ist gedrueckt,
        die Duebel tragen nur den Betonstahl der Platte.
        """
        _, urteile, text, verbund = rechnen(HEA, polygone=(KAMMERBETON,), staebe=[(0, 370)],
                                            faelle={"Stütze": {"M_y_Ed": -200.0,
                                                               "duebelzahl": 10}})
        u = urteile["Dübel", "Stütze"]
        self.assertAlmostEqual(grad(u), 10 * P_SCHAFT / T_STAB, delta=GENAU)
        self.assertIn(KAMMER, text)
        self.assertIn(f"Polygon 1, {IN_DER_KAMMER}", text)
        A_a = stahl_allein(HEA)["N_Rd_zug"] * 1e3 / F_355
        aussen, kammer = verbund.fuge
        beton = [g for g in range(len(verbund.gruppen)) if verbund.gruppen[g].stoff.name
                 == "C30/37"]
        flaeche = sum(s.gewicht * s.werte.A for s in kammer if s.gruppe in beton)
        self.assertAlmostEqual(flaeche, 300.0 * 290.0 - A_a, delta=1e-6 * flaeche)
        # Die Platte, ohne was der Stab in ihr verdraengt.
        self.assertAlmostEqual(sum(s.gewicht * s.werte.A for s in aussen if s.gruppe in beton),
                               1500.0 * 120.0 - math.pi * 10.0 ** 2, delta=1e-3)
        self.assertGreater(verbund.zum_beton[1], 0.0)

    def test_welche_seite(self):
        """Die Nulllinie zieht die Seite des Betons, oder Beton und Betonstahl sind gezogen."""
        oben = (0.0, 200.0)
        self.assertTrue(vd.negativ((0.0, 1.0), oben, -5.0))
        self.assertFalse(vd.negativ((0.0, -1.0), oben, -5.0))
        self.assertTrue(vd.negativ((0.0, -1.0), oben, 5.0))
        self.assertFalse(vd.negativ((0.0, 1.0), None, -5.0))


class TestOhneSymmetrie(unittest.TestCase):
    def test_upe_verlangt_volle_verduebelung(self):
        upe = (0, 150, "UPE 300", {})
        _, urteile, text, verbund = rechnen(upe, faelle={
            "Feld": {"M_y_Ed": 100.0, "duebelzahl": 40, "L_e": 10.0}})
        self.assertFalse(verbund.doppelsymmetrisch)
        self.assertIn(UNSYMMETRISCH, text)
        self.assertTrue(urteile["Dübel", "Feld"].begruendung.endswith("verlangt 1.00."))


class TestFelder(unittest.TestCase):
    """d höchstens h_D/4: am Feld abgewiesen und vor dem Rechnen geprüft (6.1.1.3)."""

    def test_die_angaben_der_maske(self):
        felder = feldangaben(QuerschnittsanalyseEintrag)
        self.assertEqual(felder["duebel_d"]["bis_feld"], {
            "feld": "duebel_h", "faktor": 0.25,
            "satz": "Durchmesser d darf nicht grösser sein als 0.25 · Länge h_D"})
        self.assertEqual(felder["duebel_h"]["ab_feld"], {
            "feld": "duebel_d", "faktor": 4.0,
            "satz": "Länge h_D darf nicht kleiner sein als 4 · Durchmesser d"})
        self.assertEqual((felder["duebel_d"]["ab"], felder["duebel_d"]["bis"]), (16.0, 25.0))

    def test_zu_kurz_haelt_die_rechnung_an(self):
        p = projekt()
        a = analyse(p, IPE, polygone=(PLATTE,))
        a.duebel_d, a.duebel_h = 22.0, 80.0
        self.assertIn("Durchmesser d darf nicht grösser sein als 0.25 · Länge h_D, "
                      "angegeben sind 22 mm und 80 mm.", meldung(p))
        a.duebel_h = 88.0
        with self.assertRaisesRegex(AssertionError, "Alles rechnet"):
            meldung(p)

    def test_ohne_faktor_wie_bisher(self):
        a = Bereich("α_min", bis_feld="alpha_max")
        b = Bereich("α_max")
        self.assertEqual(a.gegen(b), ("α_min darf nicht grösser sein als α_max",
                                      "α_max darf nicht kleiner sein als α_min"))
        d = Bereich("Durchmesser d", einheit=MM, bis_feld="duebel_h", bis_faktor=0.25)
        h = Bereich("Länge h_D", einheit=MM)
        self.assertEqual(d.grund_gegen(25.0, h, 100.0), "")
        self.assertTrue(d.grund_gegen(25.5, h, 100.0))


if __name__ == "__main__":
    unittest.main()
