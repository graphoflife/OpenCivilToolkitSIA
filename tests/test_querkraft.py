"""Tests für den Querkraftnachweis."""

import unittest

from opencivil.core.einheiten import EINHEITSLOS, KN, KNM, KN_PRO_M, Groesse
from opencivil.nachweis import querkraft
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
        # Auch das Querkrafturteil trägt den Namensraum seines Nachweises --
        # die Zusammenfassung gruppiert danach nach Platten.
        for name, urteil in gefunden.items():
            self.assertTrue(urteil.raum.startswith("querschnitt.q1."), f"{name}: {urteil.raum}")
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

    def ergebnis_bei(self, N_Ed: float):
        """Der Querkraftfall 'Feld' bei dieser Normalkraft in kN."""
        projekt = projekt_mit_querkraft()
        projekt.querschnitte[0].kombinationen[0].N_Ed = N_Ed
        aufbau, _ = urteile(projekt)
        return aufbau.querkraft["q1.x"].ergebnisse[0]

    def test_zug_zaehlt_beim_dekompressionsmoment_nicht(self):
        """m_Dd = |min(N_Ed; 0)| · h/6 -- entlastend wirkt nur Druck."""
        self.assertEqual(self.ergebnis_bei(+200.0).m_Dd, 0.0)
        self.assertEqual(self.ergebnis_bei(0.0).m_Dd, 0.0)
        self.assertAlmostEqual(self.ergebnis_bei(-300.0).m_Dd, 300e3 * 0.3 / 6)

    def test_zugkraft_wird_gerechnet_statt_ausgeschlossen(self):
        """
        Eine Normalzugkraft setzte v_Rd früher kurzerhand auf null.

        Nötig ist das nicht: m_Dd wird über min(N_Ed; 0) von selbst null, und
        der kleinere Momentenwiderstand bei Zug senkt den Widerstand ohnehin --
        der Nachweis läuft also unverändert durch.
        """
        zug = self.ergebnis_bei(+200.0)
        ohne = self.ergebnis_bei(0.0)

        self.assertGreater(zug.v_Rd, 0.0)
        self.assertLess(zug.v_Rd, ohne.v_Rd)
        # Die Begründung ist die gewöhnliche Rechnung, keine Ausnahmemeldung.
        self.assertIn("v_Rd = k_d", zug.begruendung)
        self.assertNotIn("Zugkraft", zug.begruendung)

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

    def test_m_rd_wird_im_querkraftnachweis_hergeleitet(self):
        """
        Der Momentenwiderstand darf auch hier nicht vom Himmel fallen.

        Er hängt von der wirkenden Normalkraft ab, also muss dastehen, zwischen
        welchen Eckpunkten des Polygons interpoliert wurde -- dieselbe
        Herleitung wie beim M-N-Nachweis, geschrieben von derselben Stelle.
        """
        from opencivil.core.protokoll import GleichungBlock, TabellenBlock

        projekt = projekt_mit_querkraft()
        projekt.querschnitte[0].kombinationen[0].N_Ed = -300.0
        aufbau = projekt.aufbauen()
        loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
        erg = aufbau.querkraft["q1.x"].ergebnisse[0]

        # Nur der Abschnitt des Querkraftnachweises, ab seinem ersten Fall.
        bloecke = loesung.protokoll.nach_abschnitten()
        beginn = next(i for i, b in enumerate(bloecke)
                      if getattr(b, "text", "") == "Querkraftnachweis – Feld")
        abschnitt = bloecke[beginn:beginn + 12]

        gleichung = next(
            b for b in abschnitt
            if isinstance(b, GleichungBlock) and "Momentenwiderstand bei" in b.titel)
        self.assertIn(r"M_{Rd} = M_1 + \frac{N_{Ed} - N_1}", gleichung.latex)
        # Die geschriebene Zahl ist die, mit der gerechnet wird.
        self.assertIn(f"{erg.m_Rd / 1e3:.1f}", gleichung.latex)

        tabelle = next(
            b for b in abschnitt
            if isinstance(b, TabellenBlock) and b.titel == "Stützpunkte der Interpolation")
        self.assertEqual(len(tabelle.zeilen), 2)

    def test_der_betrag_steht_in_der_dehnungsformel(self):
        """
        Bei negativem Moment ist m_Rd negativ, gerechnet wird mit dem Betrag.

        Ohne die Betragsstriche zeigte die Interpolation darüber -83.9 und die
        Dehnungsformel darunter 83.9 -- zwei Zahlen für dieselbe Grösse.
        """
        from opencivil.core.protokoll import GleichungBlock

        projekt = projekt_mit_querkraft()
        projekt.querschnitte[0].kombinationen[0].M_Ed = -50.0
        aufbau = projekt.aufbauen()
        loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())

        dehnung = next(
            b for b in loesung.protokoll.nach_abschnitten()
            if isinstance(b, GleichungBlock) and b.titel == "Dehnung auf halber Höhe")
        self.assertIn(r"\left|m_{Rd}(N_{Ed})\right|", dehnung.latex)
        self.assertIn(r"\left|m_{Ed}\right|", dehnung.latex)

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


class TestQuerkraftkurve(unittest.TestCase):
    """
    Die M-V-Kurve: Querkraftwiderstand über dem Moment, bei festem N_Ed.

    Wichtigste Eigenschaft ist nicht ihr Verlauf, sondern dass sie aus
    derselben Funktion stammt wie der Nachweis. Eine Kurve, die neben ihren
    eigenen Punkten herläuft, wäre schlimmer als keine.
    """

    def aufbau(self, **abweichungen):
        projekt = projekt_mit_querkraft(**abweichungen)
        a = projekt.aufbauen()
        a.werk.loese(*a.alle_nachweisziele())
        return a

    def test_fuenfzig_punkte_von_null_bis_m_rd_plus_zwanzig(self):
        from opencivil.nachweis.querkraft import KURVENPUNKTE, KURVENZUGABE

        kurve = self.aufbau().querkraft["q1.x"].kurve(0.0, moment_positiv=True)
        self.assertEqual(len(kurve["punkte"]), KURVENPUNKTE)
        self.assertAlmostEqual(kurve["punkte"][0][0], 0.0)
        self.assertAlmostEqual(kurve["punkte"][-1][0], kurve["m_Rd"] + KURVENZUGABE)

    def test_die_kurve_trifft_den_nachweis(self):
        """
        Der Bemessungspunkt liegt auf der Kurve -- nicht ungefähr, sondern
        weil beide dieselbe Funktion rufen.
        """
        a = self.aufbau()
        qk = a.querkraft["q1.x"]
        erg = qk.ergebnisse[0]                       # Feld: M_Ed = 100, N_Ed = 0
        kurve = qk.kurve(erg.fall.N_Ed.si, moment_positiv=True)

        # Denselben Punkt direkt rechnen und mit dem Nachweis vergleichen.
        d, d_v = qk.beiwerte.hoehen(True)
        punkt = querkraft.widerstand(
            M_Ed=erg.fall.M_Ed.si, N_Ed=erg.fall.N_Ed.si, h=qk.beiwerte.h,
            d=d, d_v=d_v, tau_cd=qk.beiwerte.tau_cd, f_yd=qk.beiwerte.f_yd,
            E_s=qk.beiwerte.E_s, k_g=qk.beiwerte.k_g, m_Rd=kurve["m_Rd"])
        self.assertAlmostEqual(punkt.v_Rd, erg.v_Rd, places=6)

    def test_jenseits_des_widerstands_faellt_die_kurve(self):
        """
        Über m_Rd fliesst die Bewehrung: eps_v springt, k_d sinkt. Genau
        dieser Knick ist der Grund, 20 kNm weiter zu zeichnen.
        """
        kurve = self.aufbau().querkraft["q1.x"].kurve(0.0, moment_positiv=True)
        elastisch = [v for _, v, plastisch in kurve["punkte"] if not plastisch]
        plastisch = [v for _, v, p in kurve["punkte"] if p]

        self.assertTrue(plastisch, "kein plastischer Ast gezeichnet")
        self.assertLess(max(plastisch), min(elastisch))
        # Und innerhalb jedes Astes fällt der Widerstand mit wachsendem Moment.
        self.assertEqual(elastisch, sorted(elastisch, reverse=True))

    def test_ohne_moment_ist_der_widerstand_am_groessten(self):
        kurve = self.aufbau().querkraft["q1.x"].kurve(0.0, moment_positiv=True)
        werte = [v for _, v, _ in kurve["punkte"]]
        self.assertEqual(werte[0], max(werte))

    def test_druck_hebt_die_ganze_kurve(self):
        """Eine Normaldruckkraft entlastet über m_Dd und hebt m_Rd."""
        qk = self.aufbau().querkraft["q1.x"]
        ohne = qk.kurve(0.0, moment_positiv=True)
        mit = qk.kurve(-300e3, moment_positiv=True)
        self.assertGreater(mit["m_Rd"], ohne["m_Rd"])

    def test_es_gibt_nur_kurven_zu_vorhandenen_faellen(self):
        """
        Ohne einen Fall mit negativem Moment gibt es keine Kurve für «Zug
        oben» -- sie wäre eine Aussage über etwas, das niemand wissen wollte.
        """
        # Das Beispiel hat eine Stütze mit negativem Moment -- also beide.
        self.assertEqual(self.aufbau().querkraft["q1.x"].momentenrichtungen,
                         [True, False])

        nur_feld = projekt_mit_querkraft()
        for k in nur_feld.querschnitte[0].kombinationen:
            k.M_Ed = abs(k.M_Ed)
        a = nur_feld.aufbauen()
        a.werk.loese(*a.alle_nachweisziele())
        self.assertEqual(a.querkraft["q1.x"].momentenrichtungen, [True])

    def test_ausserhalb_der_resistenzlinie_gibt_es_keine_kurve(self):
        qk = self.aufbau().querkraft["q1.x"]
        self.assertIsNone(qk.kurve(99_000e3, moment_positiv=True))
