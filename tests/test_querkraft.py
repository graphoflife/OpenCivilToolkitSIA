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
        Feld, x-Richtung, M_Ed = 100 kNm/m, N_Ed = 0, von Hand nachgerechnet:

            d     = 261 mm            (Grund ⌀18; die Zulage ⌀12 liegt bei
                                       ungünstiger Lage weiter innen)
            k_g   = max(1.20; 48/(16+32·1))   = 1.200   ← der Riegel greift
            m_Rd  = 248.7 kNm/m       (Handrechnung bei N_Ed = 0)
            eps_v = 434.8·100/(200000·248.7)  = 0.8741 ‰
            k_d   = 1/(1+0.8741e-3·261·1.200) = 0.7851
            tau_cd= 0.3·sqrt(30)/1.5          = 1.0954 N/mm²
            v_Rd  = 0.7851·1.0954·261         = 224.5 kN/m
        """
        aufbau, gefunden = urteile(projekt_mit_querkraft())
        erg = aufbau.querkraft["q1.x"].ergebnisse[0]
        self.assertAlmostEqual(erg.d * 1e3, 261.0, places=6)
        self.assertAlmostEqual(erg.eps_v * 1e3, 0.8741, places=4)
        self.assertAlmostEqual(erg.k_d, 0.7851, places=4)
        self.assertAlmostEqual(erg.v_Rd / 1e3, 224.5, delta=0.2)

    def test_k_g_hat_einen_unteren_riegel(self):
        """
        k_g = max(1.20; 48/(16 + D_max · …)).

        Ohne den Riegel ergäbe D_max = 32 mm bei C30/37 genau 1.0; der Riegel
        hebt das auf 1.20 und senkt damit k_d -- er liegt auf der sicheren
        Seite.
        """
        from opencivil.nachweis.querkraft import K_G_MINDEST

        aufbau, _ = urteile(projekt_mit_querkraft())
        nachweis = aufbau.querkraft["q1.x"]
        # Der Beiwert steckt in k_d; rückgerechnet muss er den Riegel treffen.
        erg = nachweis.ergebnisse[0]
        k_g = (1.0 / erg.k_d - 1.0) / (erg.eps_v * erg.d * 1e3)
        self.assertAlmostEqual(k_g, K_G_MINDEST, places=6)
        self.assertAlmostEqual(K_G_MINDEST, 1.20)

    def test_zug_zaehlt_beim_dekompressionsmoment_nicht(self):
        """
        m_Dd = |min(N_Ed; 0)| · h/6 -- eine Zugkraft entlastet nicht.

        Geprüft an der Formel selbst, weil eine Normalzugkraft den
        Querkraftnachweis ohnehin ausschliesst und m_Dd dann gar nicht mehr
        gebraucht wird.
        """
        h = 0.3
        fuer = lambda N: abs(min(N, 0.0)) * h / 6.0
        self.assertAlmostEqual(fuer(-300e3), 300e3 * 0.3 / 6)   # Druck zählt
        self.assertEqual(fuer(+300e3), 0.0)                      # Zug nicht
        self.assertEqual(fuer(0.0), 0.0)

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
        In eps_v gehört m_Rd(N_Ed), nicht m_Rd(0) -- es ist schlicht eine
        andere Grösse.

        Geprüft wird genau das: der angesetzte Widerstand ist der bei der
        wirkenden Normalkraft. In welche Richtung er dabei vom Wert bei N = 0
        abweicht, hängt von der Form der Resistenzlinie ab und ist hier nicht
        die Aussage -- auf dem Polygon der Handrechnung senkt Druck ihn,
        auf der genauen Linie hebt er ihn.
        """
        projekt = projekt_mit_querkraft()
        projekt.querschnitte[0].kombinationen[0].N_Ed = -300.0
        aufbau, _ = urteile(projekt)
        erg = aufbau.querkraft["q1.x"].ergebnisse[0]

        nachweis = aufbau.nachweise["q1.x"]
        loesung = aufbau.werk.loese(
            nachweis.d_m_rd[erg.fall.name].id,
            nachweis.d_eckwerte["M_Rd_N0_pos"].id)
        bei_n_ed = loesung.groesse(nachweis.d_m_rd[erg.fall.name].id).in_einheit(KNM)
        bei_null = loesung.groesse(nachweis.d_eckwerte["M_Rd_N0_pos"].id).in_einheit(KNM)

        self.assertAlmostEqual(erg.m_Rd / 1e3, bei_n_ed, places=3)
        self.assertNotAlmostEqual(erg.m_Rd / 1e3, bei_null, places=1)

        # Und der Wert stimmt mit der Interpolation auf dem Polygon überein --
        # der Querkraftnachweis rechnet damit auf derselben Linie wie der
        # M-N-Nachweis, nicht auf einer eigenen.
        from opencivil.nachweis.linie import MOMENT, schnitte
        erwartet = max(schnitte(nachweis.handlinie, MOMENT, -300e3))
        self.assertAlmostEqual(erg.m_Rd, erwartet, delta=1.0)

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
