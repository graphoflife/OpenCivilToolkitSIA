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
        self.assertIn("V_Rd = k_d", zug.begruendung)
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

    Ein Bild je Tragrichtung, mit beiden Ästen -- rechts das positive Moment
    (Zug unten), links das negative (Zug oben).

    Wichtigste Eigenschaft ist nicht der Verlauf, sondern dass er aus derselben
    Funktion stammt wie der Nachweis. Eine Kurve, die neben ihren eigenen
    Punkten herläuft, wäre schlimmer als keine.
    """

    def aufbau(self, **abweichungen):
        projekt = projekt_mit_querkraft(**abweichungen)
        a = projekt.aufbauen()
        a.werk.loese(*a.alle_nachweisziele())
        return a

    def ast(self, kurve, positiv):
        return next((a for a in kurve["aeste"] if a["moment_positiv"] is positiv), None)

    def test_beide_aeste_in_einem_bild(self):
        """Das Beispiel hat Feld und Stütze, also Zug unten und Zug oben."""
        kurve = self.aufbau().querkraft["q1.x"].kurve(0.0)
        self.assertEqual([a["moment_positiv"] for a in kurve["aeste"]], [True, False])

    def test_der_negative_ast_liegt_links(self):
        kurve = self.aufbau().querkraft["q1.x"].kurve(0.0)
        for ast in kurve["aeste"]:
            vz = 1 if ast["moment_positiv"] else -1
            self.assertTrue(all(M * vz >= 0 for M, _, _ in ast["punkte"]))
            self.assertGreater(ast["m_Rd"] * vz, 0.0)

    def test_jeder_ast_nimmt_seine_eigene_statische_hoehe(self):
        """
        Zug unten misst zur untersten Lage, Zug oben zur obersten. Beide aus
        derselben Richtung, aber von verschiedenen Seiten.
        """
        kurve = self.aufbau().querkraft["q1.x"].kurve(0.0)
        unten = self.ast(kurve, True)["d"]
        oben = self.ast(kurve, False)["d"]
        self.assertAlmostEqual(unten, 0.261, places=6)    # 1. Lage, ⌀18
        self.assertAlmostEqual(oben, 0.264, places=6)     # 4. Lage, ⌀12
        self.assertNotAlmostEqual(unten, oben)

    def test_fuenfzig_punkte_je_ast_von_null_bis_m_rd_plus_zwanzig(self):
        """
        Fünfzig gleichmässige Stützstellen, dazu die beiden Seiten des Sprungs
        bei m_Rd -- ohne die stünde an der Marke der Wert des Nachbarpunkts.
        """
        from opencivil.nachweis.querkraft import KURVENPUNKTE, KURVENZUGABE

        ast = self.ast(self.aufbau().querkraft["q1.x"].kurve(0.0), True)
        self.assertEqual(len(ast["punkte"]), KURVENPUNKTE + 2)
        self.assertAlmostEqual(ast["punkte"][0][0], 0.0)
        self.assertAlmostEqual(ast["punkte"][-1][0], ast["m_Rd"] + KURVENZUGABE)

    def test_der_sprung_liegt_genau_auf_m_rd(self):
        ast = self.ast(self.aufbau().querkraft["q1.x"].kurve(0.0), True)
        letzter_elastisch = [M for M, _, p in ast["punkte"] if not p][-1]
        erster_plastisch = [M for M, _, p in ast["punkte"] if p][0]
        self.assertAlmostEqual(letzter_elastisch, ast["m_Rd"], places=9)
        self.assertAlmostEqual(erster_plastisch, ast["m_Rd"], places=2)

    def test_die_kurve_trifft_den_nachweis(self):
        """
        Der Bemessungspunkt liegt auf der Kurve -- nicht ungefähr, sondern
        weil beide dieselbe Funktion rufen.
        """
        a = self.aufbau()
        qk = a.querkraft["q1.x"]
        erg = qk.ergebnisse[0]                       # Feld: M_Ed = 100, N_Ed = 0
        ast = self.ast(qk.kurve(erg.fall.N_Ed.si), True)

        d, d_v = qk.beiwerte.hoehen(True)
        punkt = querkraft.widerstand(
            M_Ed=erg.fall.M_Ed.si, N_Ed=erg.fall.N_Ed.si, h=qk.beiwerte.h,
            d=d, d_v=d_v, tau_cd=qk.beiwerte.tau_cd, f_yd=qk.beiwerte.f_yd,
            E_s=qk.beiwerte.E_s, k_g=qk.beiwerte.k_g, m_Rd=abs(ast["m_Rd"]))
        self.assertAlmostEqual(punkt.v_Rd, erg.v_Rd, places=6)

    def test_jenseits_des_widerstands_faellt_die_kurve(self):
        """
        Über m_Rd fliesst die Bewehrung: eps_v springt auf 1.5·f_yd/E_s und
        bleibt dort. Der Widerstand fällt einmal und läuft dann waagrecht.
        """
        ast = self.ast(self.aufbau().querkraft["q1.x"].kurve(0.0), True)
        elastisch = [v for _, v, plastisch in ast["punkte"] if not plastisch]
        plastisch = [v for _, v, p in ast["punkte"] if p]

        self.assertTrue(plastisch, "kein plastischer Ast gezeichnet")
        self.assertLess(max(plastisch), min(elastisch))
        self.assertEqual(elastisch, sorted(elastisch, reverse=True))
        for v in plastisch:
            self.assertAlmostEqual(v, plastisch[0], places=6)

    def test_der_plastische_wert_folgt_der_fliessdehnung(self):
        """eps_v = 1.5 · f_yd/E_s, von Hand nachgerechnet."""
        from opencivil.nachweis.querkraft import PLASTISCH

        qk = self.aufbau().querkraft["q1.x"]
        ast = self.ast(qk.kurve(0.0), True)
        d, d_v = qk.beiwerte.hoehen(True)

        eps_v = PLASTISCH * qk.beiwerte.f_yd / qk.beiwerte.E_s
        k_d = 1.0 / (1.0 + eps_v * d * 1e3 * qk.beiwerte.k_g)
        erwartet = k_d * (qk.beiwerte.tau_cd / 1e6) * d_v * 1e3 * 1e3

        plastisch = [v for _, v, p in ast["punkte"] if p]
        self.assertAlmostEqual(plastisch[0], erwartet, places=6)

    def test_ohne_moment_ist_der_widerstand_am_groessten(self):
        ast = self.ast(self.aufbau().querkraft["q1.x"].kurve(0.0), True)
        werte = [v for _, v, _ in ast["punkte"]]
        self.assertEqual(werte[0], max(werte))

    def test_druck_hebt_die_ganze_kurve(self):
        """Eine Normaldruckkraft entlastet über m_Dd und hebt m_Rd."""
        qk = self.aufbau().querkraft["q1.x"]
        ohne = self.ast(qk.kurve(0.0), True)
        mit = self.ast(qk.kurve(-300e3), True)
        self.assertGreater(mit["m_Rd"], ohne["m_Rd"])

    def test_ohne_zugbewehrung_gibt_es_den_ast_nicht(self):
        """
        Liegt auf der gezogenen Seite nichts, gibt es kein d -- und ohne d
        keinen Widerstand. Ein gezeichneter Ast waere erfunden.
        """
        nur_unten = projekt_mit_querkraft()
        for lage in nur_unten.querschnitte[0].lagen[2:]:
            lage.grund.durchmesser = 0.0
            lage.zulage.durchmesser = 0.0
        a = nur_unten.aufbauen()
        a.werk.loese(*a.alle_nachweisziele())

        kurve = a.querkraft["q1.x"].kurve(0.0)
        self.assertEqual([ast["moment_positiv"] for ast in kurve["aeste"]], [True])

    def test_ausserhalb_der_resistenzlinie_gibt_es_keinen_ast(self):
        kurve = self.aufbau().querkraft["q1.x"].kurve(99_000e3)
        self.assertEqual(kurve["aeste"], [])


class TestVorzeichenDerQuerkraft(unittest.TestCase):
    """
    Ob die Querkraft positiv oder negativ angegeben ist, spielt keine Rolle --
    gerechnet und verglichen wird mit dem Betrag.
    """

    def ergebnis(self, V_Ed: float):
        projekt = projekt_mit_querkraft()
        projekt.querschnitte[0].kombinationen[0].V_Ed = V_Ed
        aufbau = projekt.aufbauen()
        loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
        erg = aufbau.querkraft["q1.x"].ergebnisse[0]
        urteil = next(u for u in loesung.urteile
                      if u.name == f"Querkraft x – {erg.fall.name}")
        return erg, urteil

    def test_das_vorzeichen_aendert_nichts(self):
        plus, u_plus = self.ergebnis(+120.0)
        minus, u_minus = self.ergebnis(-120.0)
        self.assertAlmostEqual(plus.erfuellungsgrad, minus.erfuellungsgrad)
        self.assertEqual(plus.erfuellt, minus.erfuellt)
        self.assertAlmostEqual(plus.v_Rd, minus.v_Rd)

    def test_die_einwirkung_im_urteil_ist_der_betrag(self):
        """
        Stünde dort -120, teilte der Leser den Widerstand durch eine negative
        Zahl und bekäme etwas anderes als den danebenstehenden Erfüllungsgrad.
        """
        _, urteil = self.ergebnis(-120.0)
        self.assertAlmostEqual(urteil.einwirkung.groesse.in_einheit(KN_PRO_M), 120.0)
        # Betragsstriche stehen nicht am Symbol: die Zahl daneben ist
        # ohnehin der Betrag, und zwei Zeichen fuer dieselbe Aussage
        # machen die Tabelle nur breiter.
        self.assertEqual(urteil.einwirkung.symbol, "V_{Ed,x}")
