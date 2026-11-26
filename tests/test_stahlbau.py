"""
Tests fuer den Stahlquerschnitt nach SIA 263:2013 (Plan vom 2026-11-25,
Schritt 12): die Querschnittsklasse je Blech, die mitwirkende Breite der
Klasse 4 und die Kennzahlen der Querschnittsanalyse -- Zug, Druck, Biegung
und Querkraft, ohne Knicken und Kippen.

Von Hand, mit f_y aus Tabelle 1 und γ_M1 = 1.05, die Querschnittswerte aus
den Tabellen der Hersteller:

* HEB 300, S355: alle Bleche Klasse 1 -- Flansch c/t = 117.5/19 = 6.2
  ≤ 9 ε = 7.3, Steg 208/11 = 18.9 ≤ 33 ε = 26.9. N_Rd = 355 · 14 908/1.05
  = 5040 kN; M_y,Rd = 355 · 1869 cm³/1.05 = 631.9 kNm, M_z,Rd = 355 · 870.1
  cm³/1.05 = 294.2 kNm; A_v = 14 908 - 2 · 300 · 19 + (11 + 2 · 27) · 19
  = 4743 mm² nach (41a), V_z,Rd = 205 · 4743/1.05 = 926.0 kN; quer dazu
  2 b t_f = 11 400 mm², V_y,Rd = 2225.7 kN.
* HEB 800, S235, gegen die Excel-Datei des Benutzers: N_Rd = 7479 kN,
  M_y,Rd = 2289 kNm, A_v = 16 175 mm² -- dort mit τ_y = 235/√3 = 135.68,
  hier mit 135 N/mm² aus Tabelle 1: V_z,Rd = 135 · 16 175/1.05 = 2079.6 kN.
  Bei Druck ist der Steg mit c/t = 674/17.5 = 38.5 zwischen 38 ε und 42 ε:
  Klasse 3, gerechnet mit dem ganzen Querschnitt wie Klasse 1.
* IPE 600, S355, bei Druck Klasse 4: der Steg 514/12 = 42.8 > 42 ε = 34.2.
  b = 600 - 19 = 581 mm, k = 4, λ_p = (581/12)/(28.4 · 0.814 · 2) = 1.048,
  ρ = 0.9/λ_p = 0.859, A_eff = A - (1 - ρ) · 581 · 12.
* HEA 300, S355: die Flansche c/t = 118.75/14 = 8.5 zwischen 10 ε = 8.1
  und 14 ε = 11.4, Klasse 3: M_y,Rd = 355 · 1260 cm³/1.05 = 426.0 kNm.
* RRK 200 x 200 x 5, S355: c/t = 185/5 = 37 > 42 ε, Klasse 4. Im Kasten
  nach (70): λ_p = 39/(28.4 · 0.814 · 2) = 0.844, ρ = (0.844 - 0.055 · 4)
  /0.844² = 0.876, wo 0.9/λ_p noch 1 gaebe.
* ROR 323.9 x 5, S355: D/t = 64.8 > 90 ε² = 59.6, Klasse 4 -- das Werkzeug
  rechnet es nicht, Druck und Biegung tragen null. V = 205 · 2 · 5 · (323.9
  - 5)/1.05 = 622.6 kN.
* Ein freies Blech 200 x 20: hoechstens Klasse 3, elastisch: M_y,Rd = 355 ·
  200 · 20²/6/1.05 = 4.51 kNm, M_z,Rd = 45.1 kNm; Querkraft traegt es nicht.
* HEB 300 mit einem Blech 300 x 20 darunter: A = 20 908 mm², Schwerpunkt
  45.9 mm unter der Mitte, I_y = 361.4 · 10⁶ mm⁴. Zug oben drueckt das Blech:
  Klasse 3, M = 355 · 361.4 · 10⁶/195.9/1.05 = 623.6 kNm. Zug unten zieht
  es: die plastische Nulllinie liegt 14.85 mm ueber der Unterkante des
  Flanschs, W_pl = 6000 · 24.85 + 4454 · 7.43 + 1245 · 2.08 + 9208 · 222.1
  = 2230 cm³, M = 754.0 kNm.
"""

import math
import unittest

from opencivil.bericht.markdown import als_markdown
from opencivil.projekt.aufbau.querschnittsanalyse import ohne_nachweise
from opencivil.querschnitt import geometrie as geo
from opencivil.querschnitt.bauweise import Bauweise
from opencivil.stahlbau import klasse as kl
from opencivil.stahlbau.querschnitt import kleinste_breite
from opencivil.stahlbau.schub import kritisch, tau_beulen
from opencivil.stahlprofile.bleche import Halterung, bleche
from opencivil.stahlprofile.lage import Profillage
from tests.test_stahlprofile_qa import analyse, projekt

#: So weit duerfen Umriss und Tabelle auseinander liegen (wie in test_stahlprofile_qa).
GRENZE = 0.005

EPS_355 = math.sqrt(235.0 / 355.0)


def rechteck(y_0, z_0, b, h):
    return [[y_0, z_0], [y_0 + b, z_0], [y_0 + b, z_0 + h], [y_0, z_0 + h]]


def kennzahlen(*profile, polygone=(), stahl=None):
    """Die Kennzahlen einer Analyse in kN, kNm und Klassen -- dazu Aufbau und Analyse."""
    p = projekt()
    if stahl is not None:
        p.baustahl(stahl)
    a = analyse(p, *profile, polygone=polygone)
    if stahl is not None:
        for profil in a.profile:
            profil.stahl = "st2"
    aufbau = p.aufbauen()
    teil = aufbau.teile[a.kennung]
    loesung = aufbau.werk.loese(*[k.definition.id for k in teil.kennzahlen])
    werte = {}
    for k in teil.kennzahlen:
        w = loesung.wert(k.definition.id)
        werte[k.definition.id.rsplit(".", 1)[1]] = w.in_einheit(w.einheit)
    return werte, aufbau, a


class TestGrenzen(unittest.TestCase):
    """Tabellen 5a und 5b, mit ε."""

    def test_epsilon(self):
        self.assertAlmostEqual(kl.epsilon(235.0), 1.0)
        self.assertAlmostEqual(kl.epsilon(355.0), 0.8136, places=4)

    def test_beidseitig_gedrueckt(self):
        g = kl.grenzen(Halterung.BEIDSEITIG, 1.0, 1.0, 1.0)
        for ist, soll in zip(g.werte, (33.0, 38.0, 42.0)):
            self.assertAlmostEqual(ist, soll)

    def test_beidseitig_gebogen(self):
        """Um die Mitte: α = 0.5, ψ = -1 -- 72 ε, 83 ε und 124 ε, stetig zu 42 ε/(0.67 + 0.33 ψ)."""
        g = kl.grenzen(Halterung.BEIDSEITIG, EPS_355, 0.5, -1.0)
        for ist, soll in zip(g.werte, (72.0, 83.0, 124.0)):
            self.assertAlmostEqual(ist / EPS_355, soll)
        self.assertAlmostEqual(42.0 / (0.67 - 0.33), 124.0, delta=0.6)

    def test_einseitig_und_rohr(self):
        for ist, soll in zip(kl.grenzen(Halterung.EINSEITIG, 1.0, 1.0, 1.0).werte, (9.0, 10.0, 14.0)):
            self.assertAlmostEqual(ist, soll)
        for ist, soll in zip(kl.grenzen(Halterung.ROHR, EPS_355, 1.0, 1.0).werte, (50.0, 70.0, 90.0)):
            self.assertAlmostEqual(ist / EPS_355 ** 2, soll)

    def test_nicht_gedrueckt_keine_grenze(self):
        g = kl.grenzen(Halterung.BEIDSEITIG, 1.0, 0.0, None)
        self.assertEqual(g.werte, (kl.OHNE, kl.OHNE, kl.OHNE))
        self.assertEqual(g.klasse(1000.0), 1)

    def test_die_kleinste_klasse_die_eingehalten_ist(self):
        g = kl.Grenzen((33.0, 38.0, 42.0))
        self.assertEqual([g.klasse(s) for s in (20.0, 33.0, 35.0, 42.0, 42.1)], [1, 1, 2, 3, 4])


class TestBeulwerte(unittest.TestCase):
    """Tabelle 9 -- k₁ und k₂ der Tabelle 5b treffen die einseitig gestuetzten Spalten auf 1 %."""

    def test_beidseitig(self):
        for psi, soll in ((1.0, 4.0), (0.0, 7.79), (-1.0, 23.9)):
            self.assertAlmostEqual(kl.beulwert(Halterung.BEIDSEITIG, psi), soll, delta=0.01)
        self.assertEqual(kl.beulwert(Halterung.BEIDSEITIG, -2.0),
                         kl.beulwert(Halterung.BEIDSEITIG, -1.2))

    def test_freier_rand_gedrueckt(self):
        for psi, soll in ((1.0, 0.426), (0.0, 0.567), (-1.0, 0.851)):
            ist = kl.beulwert(Halterung.EINSEITIG, psi, frei_gedrueckt=True)
            self.assertAlmostEqual(ist / soll, 1.0, delta=0.01)

    def test_gehaltener_rand_gedrueckt(self):
        for psi, soll in ((1.0, 0.426), (0.0, 1.702)):
            self.assertAlmostEqual(kl.beulwert(Halterung.EINSEITIG, psi) / soll, 1.0, delta=0.015)
        self.assertEqual(kl.k_2(-3.0), kl.k_2(-1.0))

    def test_abminderung(self):
        lambda_p = kl.plattenschlankheit(581.0, 12.0, EPS_355, 4.0)
        self.assertAlmostEqual(lambda_p, 1.048, places=3)
        self.assertAlmostEqual(kl.abminderung(lambda_p), 0.859, places=3)
        self.assertEqual(kl.abminderung(0.5), 1.0)

    def test_im_kasten_genauer(self):
        """(70): auch wo 0.9/λ_p nichts abmindert, mindert es im Kasten."""
        lambda_p = kl.plattenschlankheit(195.0, 5.0, EPS_355, 4.0)
        self.assertAlmostEqual(lambda_p, 0.844, places=3)
        self.assertEqual(kl.abminderung(lambda_p), 1.0)
        self.assertAlmostEqual(kl.abminderung_kasten(lambda_p, 1.0), 0.876, places=3)


class TestSchubbeulen(unittest.TestCase):
    def test_gedrungen_bis_tau_y(self):
        self.assertEqual(tau_beulen(100.0, 10.0, E=210000.0, tau_y=205.0), 205.0)

    def test_schlank_nach_13(self):
        """b/t = 100: τ_cr = 5.34 · 0.9 · 210 000/100² = 100.93, τ = 0.9 √(100.93 · 205) = 129.46."""
        self.assertAlmostEqual(kritisch(1000.0, 10.0, E=210000.0), 100.93, places=2)
        self.assertAlmostEqual(tau_beulen(1000.0, 10.0, E=210000.0, tau_y=205.0), 129.46, places=2)


class TestHilfen(unittest.TestCase):
    def test_jenseits_einer_geraden(self):
        """Vom Quadrat 0..10 liegt oberhalb z = 4 ein Rechteck 10 x 6 mit dem Schwerpunkt (5, 7)."""
        A, s_y, s_z = geo.jenseits([(0, 0), (10, 0), (10, 10), (0, 10)], (0.0, 1.0), 4.0)
        self.assertAlmostEqual(A, 60.0)
        self.assertAlmostEqual(s_y / A, 5.0)
        self.assertAlmostEqual(s_z / A, 7.0)
        self.assertEqual(geo.jenseits([(0, 0), (10, 0), (10, 10), (0, 10)], (0.0, 1.0), 20.0)[0], 0.0)

    def test_kleinste_breite_der_huelle(self):
        self.assertAlmostEqual(kleinste_breite([(0, 0), (300, 0), (300, 50), (0, 50)]), 50.0)
        # Ein Winkel: es zaehlt die Huelle, nicht der Schenkel -- quer zur
        # Kante von (100, 10) nach (10, 100), 110/√2 bis zur Ecke.
        winkel = [(0, 0), (100, 0), (100, 10), (10, 10), (10, 100), (0, 100)]
        self.assertAlmostEqual(kleinste_breite(winkel), 110.0 / math.sqrt(2.0))

    def test_die_bleche_eines_heb(self):
        namen = [(b.name, b.halterung) for b in bleche(Profillage("HEB 300"))]
        self.assertEqual(namen, [
            ("Flansch oben, links", Halterung.EINSEITIG), ("Flansch oben, rechts", Halterung.EINSEITIG),
            ("Flansch unten, links", Halterung.EINSEITIG), ("Flansch unten, rechts", Halterung.EINSEITIG),
            ("Steg", Halterung.BEIDSEITIG)])
        steg = bleche(Profillage("HEB 300"))[-1]
        self.assertAlmostEqual(steg.c, 300.0 - 2 * 19.0 - 2 * 27.0)
        self.assertAlmostEqual(steg.b, 300.0 - 19.0)

    def test_gedreht_heissen_die_bleche_nach_ihrer_lage(self):
        namen = [b.name for b in bleche(Profillage("HEB 300", drehung=90))]
        self.assertIn("Flansch links, oben", namen)

    def test_nur_das_rechteckrohr_ist_ein_kasten(self):
        self.assertTrue(all(b.kasten for b in bleche(Profillage("RRK 200 x 200 x 5"))))
        self.assertFalse(any(b.kasten for b in bleche(Profillage("HEB 300"))))


class TestKennzahlen(unittest.TestCase):
    """Die Kennzahlen der Analyse, von Hand -- siehe Dateikopf."""

    def assertNahe(self, ist, soll, grenze=GRENZE):
        self.assertAlmostEqual(ist / soll, 1.0, delta=grenze, msg=f"{ist} statt {soll}")

    def test_heb_300(self):
        k, _, _ = kennzahlen((0, 0, "HEB 300", {}))
        self.assertEqual({n: k[n] for n in k if n.startswith("klasse")},
                         {n: 1.0 for n in ("klasse_druck", "klasse_unten", "klasse_oben",
                                           "klasse_links", "klasse_rechts")})
        self.assertNahe(k["N_Rd_zug"], 355.0 * 14908.0 / 1.05 / 1e3)
        self.assertNahe(k["N_Rd_druck"], -355.0 * 14908.0 / 1.05 / 1e3)
        self.assertNahe(k["M_Rd_unten"], 355.0 * 1869.0 / 1.05 / 1e3)
        self.assertNahe(k["M_Rd_oben"], -355.0 * 1869.0 / 1.05 / 1e3)
        self.assertNahe(k["M_Rd_links"], 355.0 * 870.1 / 1.05 / 1e3)
        self.assertNahe(k["V_z_Rd"], 205.0 * 4743.0 / 1.05 / 1e3)
        self.assertNahe(k["V_y_Rd"], 205.0 * 11400.0 / 1.05 / 1e3, 1e-6)

    def test_heb_800_wie_im_excel(self):
        k, _, _ = kennzahlen((0, 0, "HEB 800", {}), stahl="S235")
        self.assertEqual((k["klasse_druck"], k["klasse_unten"]), (3.0, 1.0))
        self.assertNahe(k["N_Rd_zug"], 7479.0)
        self.assertNahe(k["N_Rd_druck"], -7479.0)
        self.assertNahe(k["M_Rd_unten"], 2289.0)
        self.assertNahe(k["V_z_Rd"], 135.0 * 16175.0 / 1.05 / 1e3)

    def test_ipe_600_bei_druck_mit_wirksamer_flaeche(self):
        k, aufbau, a = kennzahlen((0, 0, "IPE 600", {}))
        self.assertEqual((k["klasse_druck"], k["klasse_unten"]), (4.0, 1.0))
        lambda_p = (581.0 / 12.0) / (28.4 * EPS_355 * 2.0)
        A_eff = 15598.0 - (1.0 - 0.9 / lambda_p) * 581.0 * 12.0
        self.assertNahe(k["N_Rd_druck"], -355.0 * A_eff / 1.05 / 1e3)
        self.assertNahe(k["M_Rd_unten"], 355.0 * 3512.0 / 1.05 / 1e3)
        text = als_markdown(aufbau.werk.loese(f"querschnittsanalyse.{a.kennung}.kennzahlen.N_Rd_druck"),
                            aufbau=aufbau)
        self.assertIn("Mitwirkende Breiten in Klasse 4", text)
        self.assertIn("Profil 1: Steg", text)

    def test_hea_300_elastisch(self):
        k, _, _ = kennzahlen((0, 0, "HEA 300", {}))
        self.assertEqual((k["klasse_druck"], k["klasse_unten"]), (3.0, 3.0))
        self.assertNahe(k["M_Rd_unten"], 355.0 * 1260.0 / 1.05 / 1e3)

    def test_rechteckrohr_als_kasten(self):
        k, aufbau, a = kennzahlen((0, 0, "RRK 200 x 200 x 5", {}))
        A = aufbau.werk.loese(f"querschnittsanalyse.{a.kennung}.A").wert(
            f"querschnittsanalyse.{a.kennung}.A").groesse.si * 1e6
        rho = 0.876
        self.assertEqual(k["klasse_druck"], 4.0)
        self.assertNahe(k["N_Rd_druck"], -355.0 * (A - 4 * (1.0 - rho) * 195.0 * 5.0) / 1.05 / 1e3, 0.002)
        text = als_markdown(aufbau.werk.loese(f"querschnittsanalyse.{a.kennung}.kennzahlen.N_Rd_druck"),
                            aufbau=aufbau)
        self.assertIn("SIA 263:2013, 4.5.3.4; 5.6.4.3, (70)", text)

    def test_rundrohr_der_klasse_4_traegt_nichts(self):
        k, aufbau, a = kennzahlen((0, 0, "ROR 323.9 x 5", {}))
        self.assertEqual((k["klasse_druck"], k["N_Rd_druck"], k["M_Rd_unten"]), (4.0, 0.0, 0.0))
        self.assertGreater(k["N_Rd_zug"], 0.0)
        self.assertNahe(k["V_z_Rd"], 205.0 * 2 * 5.0 * (323.9 - 5.0) / 1.05 / 1e3, 1e-6)
        text = als_markdown(aufbau.werk.loese(f"querschnittsanalyse.{a.kennung}.kennzahlen.N_Rd_druck"),
                            aufbau=aufbau)
        self.assertIn("Ein Rundrohr der Klasse 4 rechnet das Werkzeug nicht", text)

    def test_rundrohr_gedrungen(self):
        k, _, _ = kennzahlen((0, 0, "ROR 219.1 x 8", {}))
        self.assertEqual(k["klasse_druck"], 1.0)

    def test_freies_blech_elastisch_ohne_querkraft(self):
        k, _, _ = kennzahlen(polygone=[(rechteck(-100, -10, 200, 20), "st1")])
        self.assertEqual({k[n] for n in k if n.startswith("klasse")}, {3.0})
        self.assertNahe(k["M_Rd_unten"], 355.0 * 200.0 * 20.0 ** 2 / 6.0 / 1.05 / 1e6)
        self.assertNahe(k["M_Rd_links"], 355.0 * 20.0 * 200.0 ** 2 / 6.0 / 1.05 / 1e6)
        self.assertFalse([n for n in k if n.startswith("V_")])

    def test_ein_dickes_blech_rechnet_mit_der_rechten_spalte(self):
        """50 mm dick: f_y = 335 N/mm² statt 355 (Tabelle 1, t > 40 mm)."""
        k, _, _ = kennzahlen(polygone=[(rechteck(-150, -25, 300, 50), "st1")])
        self.assertNahe(k["N_Rd_zug"], 335.0 * 300.0 * 50.0 / 1.05 / 1e3, 1e-6)

    def test_ein_blech_unter_dem_profil(self):
        """Gedrueckt begrenzt das freie Blech die Klasse, gezogen nicht -- siehe Dateikopf."""
        k, aufbau, a = kennzahlen((0, 0, "HEB 300", {}),
                                  polygone=[(rechteck(-150, -170, 300, 20), "st1")])
        self.assertEqual((k["klasse_druck"], k["klasse_unten"], k["klasse_oben"]), (3.0, 1.0, 3.0))
        self.assertNahe(k["M_Rd_unten"], 754.0)
        self.assertNahe(k["M_Rd_oben"], -623.6)
        text = als_markdown(aufbau.werk.loese(f"querschnittsanalyse.{a.kennung}.kennzahlen.klasse_druck"),
                            aufbau=aufbau)
        self.assertIn("Polygon 1", text)

    def test_der_satz_ohne_nachweise(self):
        satz = ohne_nachweise(Bauweise.STAHL)
        self.assertIn("SIA 263:2013", satz)
        self.assertIn("Kennzahlen", satz)
        self.assertNotIn("--", satz)


if __name__ == "__main__":
    unittest.main()
