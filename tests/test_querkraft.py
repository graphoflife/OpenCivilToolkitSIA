"""Tests für den Querkraftnachweis."""

import unittest

from opencivil.core.einheiten import EINHEITSLOS, KN, KNM, KN_PRO_M, Groesse
from opencivil.projekt import Projekt


def projekt_mit_querkraft(**abweichungen) -> Projekt:
    projekt = Projekt.beispiel()
    q = projekt.querschnitte[0]
    for name, wert in abweichungen.items():
        setattr(q, name, wert)
    for k in q.kombinationen:
        k.V_Ed = 120.0
        k.richtung = "x"
    return projekt


def urteile(projekt: Projekt):
    aufbau = projekt.aufbauen()
    loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
    return aufbau, {u.name: u for u in loesung.urteile}


class TestQuerkraft(unittest.TestCase):
    def test_handrechnung(self):
        """
        Feld, x-Richtung, M_Ed = 100 kNm, N_Ed = 0:

            d     = 264 mm            (Zulage ⌀12 auf der Hülle der 1. Lage)
            k_g   = 48/(16+32*1)      = 1.0
            eps_v = 434.8*100/(200000*252.4)  = 0.861 ‰
            k_d   = 1/(1+0.861e-3*264*1.0)    = 0.815
            tau_cd= 0.3*sqrt(30)/1.5          = 1.095 N/mm^2
            v_Rd  = 0.815*1.095*264           = 236 kN/m
        """
        aufbau, gefunden = urteile(projekt_mit_querkraft())
        erg = aufbau.querkraft["q1.x"].ergebnisse[0]
        self.assertAlmostEqual(erg.d * 1e3, 264.0, places=6)
        self.assertAlmostEqual(erg.k_d, 0.815, places=2)
        self.assertAlmostEqual(erg.v_Rd / 1e3, 235.6, delta=1.0)

    def test_zugkraft_schliesst_den_widerstand_aus(self):
        projekt = projekt_mit_querkraft()
        projekt.querschnitte[0].kombinationen[0].N_Ed = 200.0   # Zug
        aufbau, gefunden = urteile(projekt)
        erg = aufbau.querkraft["q1.x"].ergebnisse[0]
        self.assertEqual(erg.v_Rd, 0.0)
        self.assertFalse(erg.erfuellt)
        self.assertIn("Zugkraft", erg.begruendung)

    def test_m_rd_wird_bei_der_wirkenden_normalkraft_genommen(self):
        """
        In eps_v gehört m_Rd(N_Ed), nicht m_Rd(0). Bei Druck liegt der
        Momentenwiderstand höher, eps_v also tiefer und v_Rd höher --
        m_Rd(0) anzusetzen wäre auf der falschen Seite konservativ und
        zudem schlicht eine andere Grösse.
        """
        projekt = projekt_mit_querkraft()
        projekt.querschnitte[0].kombinationen[0].N_Ed = -300.0
        aufbau, _ = urteile(projekt)
        erg = aufbau.querkraft["q1.x"].ergebnisse[0]

        # Der angesetzte Widerstand ist der bei N_Ed, nicht der bei N = 0.
        nachweis = aufbau.nachweise["q1.x"]
        loesung = aufbau.werk.loese(
            nachweis.d_m_rd[erg.fall.name].id,
            nachweis.d_eckwerte["M_Rd_N0_pos"].id)
        bei_n_ed = loesung.groesse(nachweis.d_m_rd[erg.fall.name].id).in_einheit(KNM)
        bei_null = loesung.groesse(nachweis.d_eckwerte["M_Rd_N0_pos"].id).in_einheit(KNM)

        self.assertGreater(bei_n_ed, bei_null)          # Druck hebt den Widerstand
        self.assertAlmostEqual(erg.m_Rd / 1e3, bei_n_ed, places=3)
        self.assertNotAlmostEqual(erg.m_Rd / 1e3, bei_null, places=1)

    def test_dekompressionsmoment(self):
        """m_Dd = |N_Ed| * h / 6 -- bei 300 kN und h = 300 mm also 15 kNm."""
        projekt = projekt_mit_querkraft()
        projekt.querschnitte[0].kombinationen[0].N_Ed = -300.0
        aufbau, _ = urteile(projekt)
        self.assertAlmostEqual(
            aufbau.querkraft["q1.x"].ergebnisse[0].m_Dd / 1e3, 15.0, places=6)

    def test_moment_unter_dekompression_gibt_vollen_widerstand(self):
        """Bleibt m_Ed unter m_Dd, ist der Querschnitt ungerissen: eps_v = 0."""
        projekt = projekt_mit_querkraft()
        k = projekt.querschnitte[0].kombinationen[0]
        k.M_Ed, k.N_Ed = 5.0, -2000.0      # m_Dd = 100 kNm > m_Ed
        aufbau, _ = urteile(projekt)
        erg = aufbau.querkraft["q1.x"].ergebnisse[0]
        self.assertEqual(erg.eps_v, 0.0)
        self.assertAlmostEqual(erg.k_d, 1.0, places=9)

    def test_druck_erhoeht_den_widerstand(self):
        """Das Dekompressionsmoment senkt eps_v und hebt damit k_d."""
        ohne = projekt_mit_querkraft()
        mit = projekt_mit_querkraft()
        mit.querschnitte[0].kombinationen[0].N_Ed = -300.0
        a1, _ = urteile(ohne)
        a2, _ = urteile(mit)
        self.assertGreater(a2.querkraft["q1.x"].ergebnisse[0].v_Rd,
                           a1.querkraft["q1.x"].ergebnisse[0].v_Rd)

    def test_einlagenhoehe_wirkt_nur_im_fenster(self):
        """d_v = d - e nur, wenn h/6 < e < d. Sonst bleibt d_v = d."""
        klein = projekt_mit_querkraft(einlagenhoehe=20.0)     # < h/6 = 50
        drin = projekt_mit_querkraft(einlagenhoehe=80.0)      # 50 < 80 < 264
        a1, _ = urteile(klein)
        a2, _ = urteile(drin)
        e1 = a1.querkraft["q1.x"].ergebnisse[0]
        e2 = a2.querkraft["q1.x"].ergebnisse[0]
        self.assertAlmostEqual(e1.d_v, e1.d)
        self.assertAlmostEqual(e2.d_v * 1e3, e2.d * 1e3 - 80.0, places=6)

    def test_groesstkorn_wirkt(self):
        klein = projekt_mit_querkraft(d_max=16.0)
        gross = projekt_mit_querkraft(d_max=32.0)
        a1, _ = urteile(klein)
        a2, _ = urteile(gross)
        # Grösseres Korn -> kleineres k_g -> grösseres k_d -> mehr Widerstand
        self.assertGreater(a2.querkraft["q1.x"].ergebnisse[0].v_Rd,
                           a1.querkraft["q1.x"].ergebnisse[0].v_Rd)

    def test_ohne_v_ed_kein_querkraftnachweis(self):
        projekt = Projekt.beispiel()   # V_Ed überall 0
        aufbau = projekt.aufbauen()
        self.assertEqual(aufbau.querkraft, {})

    def test_erfuellungsgrad_ist_widerstand_durch_einwirkung(self):
        aufbau, gefunden = urteile(projekt_mit_querkraft())
        urteil = gefunden["Querkraft x – Feld"]
        erg = aufbau.querkraft["q1.x"].ergebnisse[0]
        self.assertAlmostEqual(
            urteil.erfuellungsgrad.in_einheit(EINHEITSLOS), erg.v_Rd / 120e3, places=6)


if __name__ == "__main__":
    unittest.main()
