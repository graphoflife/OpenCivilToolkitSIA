"""Tests für den Querkraftnachweis."""

import unittest

from opencivil.core.einheiten import EINHEITSLOS, KNM, KN_PRO_M
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

            d     = 249 mm            (Grund ⌀18 in der 2. Lage; darunter
                                       liegt die y-Lage ⌀12, und die Zulage
                                       ⌀12 sitzt bei ungünstiger Lage weiter
                                       innen)
            k_g   = max(1.20; 48/(16+32·1))   = 1.200   ← der Riegel greift
            m_Rd  = 235.9 kNm/m       (Handrechnung bei N_Ed = 0)
            eps_v = 434.8·100/(200000·235.9)  = 0.9214 ‰
            k_d   = 1/(1+0.9214e-3·249·1.200) = 0.7841
            tau_cd= 0.3·sqrt(30)/1.5          = 1.0954 N/mm²
            v_Rd  = 0.7841·1.0954·249         = 213.9 kN/m
        """
        aufbau, _ = urteile(projekt_mit_querkraft())
        erg = aufbau.querkraft["q1.x"].ergebnisse[0]
        self.assertAlmostEqual(erg.d * 1e3, 249.0, places=6)
        self.assertAlmostEqual(erg.eps_v * 1e3, 0.9214, places=4)
        self.assertAlmostEqual(erg.k_d, 0.7841, places=4)
        self.assertAlmostEqual(erg.v_Rd / 1e3, 213.9, delta=0.2)

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
        self.assertEqual(gleichung.formelzeile.symbol, "M_{Rd}")
        self.assertTrue(gleichung.formelzeile.analytisch.startswith(
            r"M_1 + \frac{N_{Ed} - N_1}"))
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

    def test_ohne_v_ed_rechnet_er_still_nur_fuer_das_diagramm(self):
        """
        Kein Urteil in Tabelle und Herleitung -- aber das Bild: ohne Bügel
        die M-V-Kurve, mit Bügeln der Verlauf über die Neigung, beide ohne
        Fallpunkt.
        """
        from opencivil.web import diagrammdaten

        mit_buegeln = projekt_mit_buegeln()
        for k in mit_buegeln.querschnitte[0].kombinationen:
            k.V_Ed = 0.0
        for projekt, bild in ((Projekt.beispiel(), diagrammdaten.querkraftkurven),
                              (mit_buegeln, diagrammdaten.neigungskurven)):
            aufbau = projekt.aufbauen()
            loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
            with self.subTest(bild=bild.__name__):
                self.assertTrue(aufbau.querkraft["q1.x"].still)
                self.assertFalse([u for u in loesung.gefuehrte_urteile if u.art == "V"])
                kurven = bild(aufbau)
                self.assertTrue(kurven)
                self.assertTrue(all(k["faelle"] == [] for k in kurven.values()))

    def test_ohne_v_ed_auch_kein_stiller_mangel(self):
        """
        Unten ohne x-Bewehrung ist V_Rd = 0 -- ohne Querkraft ist das kein
        Mangel. Vorher stand in der Zusammenfassung «Querkraft – ohne
        Einwirkung: nicht erfüllt (α_eff = 0.00), ausgeschaltet».
        """
        projekt = Projekt.beispiel()
        q = projekt.querschnitte[0]
        for nummer in (1, 2):
            if q.richtung_von(nummer).value == "x":
                q.lagen[nummer - 1].grund.durchmesser = 0.0
                q.lagen[nummer - 1].zulage.durchmesser = 0.0
        aufbau = projekt.aufbauen()
        loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
        self.assertTrue(aufbau.querkraft["q1.x"].still)
        self.assertFalse([u for u in loesung.urteile if u.art == "V"])

    def test_erfuellungsgrad_ist_widerstand_durch_einwirkung(self):
        aufbau, gefunden = urteile(projekt_mit_querkraft())
        urteil = gefunden["Querkraft x – Feld"]
        erg = aufbau.querkraft["q1.x"].ergebnisse[0]
        self.assertAlmostEqual(
            urteil.erfuellungsgrad.in_einheit(EINHEITSLOS), erg.v_Rd / 120e3, places=6)



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
        self.assertAlmostEqual(unten, 0.249, places=6)    # untere x-Lage, ⌀18
        self.assertAlmostEqual(oben, 0.252, places=6)     # obere x-Lage, ⌀12
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


# ===========================================================================
# Mit Querkraftbewehrung
# ===========================================================================


def projekt_mit_buegeln(**abweichungen) -> Projekt:
    """Das Beispiel, zusätzlich mit Bügeln ⌀10, Raster 200/200."""
    projekt = projekt_mit_querkraft()
    buegel = projekt.querschnitte[0].querkraftbewehrung
    buegel.durchmesser = 10.0
    buegel.stahl = "s1"
    buegel.abstand_x = 200.0
    buegel.abstand_y = 200.0
    for name, wert in abweichungen.items():
        setattr(buegel, name, wert)
    return projekt


class TestBuegelformeln(unittest.TestCase):
    """Die beiden Formeln für sich, ohne Rechenwerk."""

    werte = dict(a_s=78.54e-6, s_x=0.2, s_y=0.2, d=0.261,
                 f_yd=434.78e6, f_cd=20.0e6, k_c=0.55)

    def test_buegelanteil_von_hand(self):
        """
        V_Rd,s = A/(s_x·s_y) · 0.9·d · f_yd · cot α

               = 78.54e-6/(0.2·0.2) · 0.9·0.261 · 434.78e6 · cot30°
               = 1.9635e-3 · 0.2349 · 434.78e6 · 1.7321
               = 347.3 kN/m
        """
        q = querkraft.buegelwiderstand(alpha=30, **self.werte)
        self.assertAlmostEqual(q.V_Rd_s / 1e3, 347.3, delta=0.2)

    def test_druckdiagonale_von_hand(self):
        """
        V_Rd,c = 0.9·d · k_c · f_cd · sin α · cos α

               = 0.9·0.261 · 0.55 · 20e6 · 0.5 · 0.86603
               = 1118.9 kN/m

        Je Laufmeter, wie V_Ed -- die betrachtete Breite steht nicht darin.
        """
        q = querkraft.buegelwiderstand(alpha=30, **self.werte)
        self.assertAlmostEqual(q.V_Rd_c / 1e3, 1118.9, delta=0.5)

    def test_massgebend_ist_das_kleinere(self):
        q = querkraft.buegelwiderstand(alpha=30, **self.werte)
        self.assertAlmostEqual(q.V_Rd, min(q.V_Rd_s, q.V_Rd_c))

    def test_der_buegelanteil_faellt_mit_steilerer_diagonale(self):
        flach = querkraft.buegelwiderstand(alpha=30, **self.werte)
        steil = querkraft.buegelwiderstand(alpha=45, **self.werte)
        self.assertGreater(flach.V_Rd_s, steil.V_Rd_s)
        self.assertLess(flach.V_Rd_c, steil.V_Rd_c)

    def test_gesucht_wird_das_groesste_kleinere(self):
        """
        Der Widerstand ist das Kleinere von beiden; gesucht ist dessen
        Höchstwert. Von Hand: das Maximum über alle ganzen Grade.
        """
        punkte = querkraft.neigungen(alpha_min=25, alpha_max=60, **self.werte)
        beste = querkraft.beste_neigung(punkte)
        self.assertAlmostEqual(beste.V_Rd, max(q.V_Rd for q in punkte))

    def test_bei_gleichstand_gilt_die_steilere_neigung(self):
        """Sie beansprucht die Druckdiagonale weniger."""
        gleich = [querkraft.Buegelpunkt(alpha=a, V_Rd_s=100.0, V_Rd_c=100.0)
                  for a in (30, 35, 40)]
        self.assertEqual(querkraft.beste_neigung(gleich).alpha, 40)


class TestNachweisMitBuegeln(unittest.TestCase):
    def test_der_widerstand_kommt_aus_dem_fachwerkmodell(self):
        aufbau, gefunden = urteile(projekt_mit_buegeln())
        erg = aufbau.querkraft["q1.x"].ergebnisse[0]
        self.assertIsNotNone(erg.massgebend)
        self.assertAlmostEqual(erg.d * 1e3, 249.0, places=6)
        self.assertAlmostEqual(erg.v_Rd, erg.massgebend.V_Rd)
        self.assertAlmostEqual(erg.v_Rd / 1e3, 331.4, delta=0.5)

    def test_buegel_ersetzen_den_betonanteil(self):
        """Nicht addieren: das wäre ein drittes Modell."""
        _, ohne = urteile(projekt_mit_querkraft())
        _, mit = urteile(projekt_mit_buegeln())
        name = "Querkraft x – Feld"
        summe = (ohne[name].widerstand.groesse.in_einheit(KN_PRO_M)
                 + 347.3)
        self.assertLess(mit[name].widerstand.groesse.in_einheit(KN_PRO_M),
                        summe - 1.0)

    def test_zug_steilt_die_diagonale_auf(self):
        """
        Bei N_Ed > 0 wird α_min auf 40° gehoben -- und α_max notfalls mit,
        damit der Bereich nicht leer wird.
        """
        projekt = projekt_mit_buegeln(alpha_min=30, alpha_max=35)
        projekt.querschnitte[0].kombinationen[0].N_Ed = 400.0
        aufbau, _ = urteile(projekt)
        ergebnisse = {e.fall.name: e for e in aufbau.querkraft["q1.x"].ergebnisse}

        mit_zug = ergebnisse["Feld"]
        self.assertTrue(mit_zug.zug_hebt_alpha)
        self.assertEqual((mit_zug.alpha_min, mit_zug.alpha_max), (40, 40))

        ohne_zug = ergebnisse["Feld mit Druck"]
        self.assertFalse(ohne_zug.zug_hebt_alpha)
        self.assertEqual((ohne_zug.alpha_min, ohne_zug.alpha_max), (30, 35))

    def test_die_statische_hoehe_folgt_dem_momentenvorzeichen(self):
        """Zug oben bei M < 0 -- dann zählt die obere Lage dieser Richtung."""
        aufbau, _ = urteile(projekt_mit_buegeln())
        ergebnisse = {e.fall.name: e for e in aufbau.querkraft["q1.x"].ergebnisse}
        self.assertGreater(ergebnisse["Feld"].fall.M_Ed.si, 0)
        self.assertLess(ergebnisse["Stütze"].fall.M_Ed.si, 0)
        self.assertNotAlmostEqual(
            ergebnisse["Feld"].d, ergebnisse["Stütze"].d, places=6)

    def test_die_stabzahl_wird_zur_teilung(self):
        """s_V,y = b / n -- fünf Bügel auf 1000 mm sind 200 mm Teilung."""
        mit_teilung = projekt_mit_buegeln()
        mit_zahl = projekt_mit_buegeln(abstand_y=None, anzahl_y=5.0)
        a, _ = urteile(mit_teilung)
        b, _ = urteile(mit_zahl)
        self.assertAlmostEqual(a.querkraft["q1.x"].ergebnisse[0].v_Rd,
                               b.querkraft["q1.x"].ergebnisse[0].v_Rd,
                               places=6)

    def test_die_herleitung_zeigt_beide_anteile(self):
        from opencivil.core.protokoll import GleichungBlock

        projekt = projekt_mit_buegeln()
        aufbau = projekt.aufbauen()
        loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
        titel = [b.titel for b in loesung.protokoll.alle_bloecke()
                 if isinstance(b, GleichungBlock)]
        for erwartet in ("Querschnitt eines Bügelschenkels", "Widerstand der Bügel",
                         "Widerstand der Druckdiagonalen", "Querkraftwiderstand"):
            self.assertIn(erwartet, titel)
        # Der bügellose Ansatz darf daneben nicht auch noch dastehen.
        self.assertNotIn("Beiwert für die statische Höhe", titel)
        self.assertNotIn("Dekompressionsmoment und Dehnung", titel)


if __name__ == "__main__":
    unittest.main()
