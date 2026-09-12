"""Tests fuer das Einheitensystem."""

import math
import unittest

from opencivil.core.einheiten import (
    CM2, DIMENSIONSLOS, EINHEITSLOS, GRAD, KG_PRO_M3, KN, KNM, KNM_PRO_M, KN_PRO_M,
    M, MM, MM2, MPA, N, N_PRO_MM2, PROMILLE, PROZENT, SPANNUNG,
    DimensionsFehler, Dimension, Einheit, Groesse,
    einheit, empirisch, null, summe,
)


class TestDimension(unittest.TestCase):
    def test_algebra(self):
        laenge = Dimension(laenge=1)
        self.assertEqual(laenge * laenge, Dimension(laenge=2))
        self.assertEqual(laenge / laenge, DIMENSIONSLOS)
        self.assertEqual(laenge**3, Dimension(laenge=3))

    def test_gebrochene_exponenten(self):
        """Wurzeln muessen darstellbar sein, sonst scheitern empirische Formeln."""
        halbe = SPANNUNG**0.5
        self.assertEqual(halbe * halbe, SPANNUNG)

    def test_spannung_ist_kraft_pro_flaeche(self):
        self.assertEqual(KN.dimension / MM2.dimension, MPA.dimension)


class TestEinheit(unittest.TestCase):
    def test_zusammensetzung(self):
        kn_pro_m = KN / M
        self.assertEqual(kn_pro_m.dimension, KN_PRO_M.dimension)
        self.assertAlmostEqual(kn_pro_m.faktor, KN_PRO_M.faktor)

    def test_mpa_gleich_n_pro_mm2(self):
        """Die beiden Schreibweisen muessen numerisch identisch sein."""
        self.assertEqual(MPA.dimension, N_PRO_MM2.dimension)
        self.assertAlmostEqual(MPA.faktor, N_PRO_MM2.faktor)

    def test_latex(self):
        self.assertEqual(MM.als_latex(), r"\,\mathrm{mm}")
        self.assertEqual(MM2.als_latex(), r"\,\mathrm{mm}^{2}")
        self.assertEqual(EINHEITSLOS.als_latex(), "")

    def test_katalog(self):
        self.assertIs(einheit("MPa"), MPA)
        with self.assertRaises(Exception):
            einheit("Furlong")


class TestGroesseGrundlagen(unittest.TestCase):
    def test_speicherung_in_si(self):
        h = Groesse(300, MM)
        self.assertAlmostEqual(h.si, 0.3)
        self.assertAlmostEqual(h.in_einheit(MM), 300.0)
        self.assertAlmostEqual(h.in_einheit(M), 0.3)

    def test_anzeige_aendert_das_resultat_nicht(self):
        h = Groesse(300, MM)
        self.assertEqual(h, h.als(M))
        self.assertAlmostEqual(h.als(M).in_einheit(MM), 300.0)

    def test_addition_gleiche_dimension(self):
        gesamt = Groesse(300, MM) + Groesse(0.2, M)
        self.assertAlmostEqual(gesamt.in_einheit(MM), 500.0)
        # Anzeige-Einheit kommt vom linken Operanden.
        self.assertEqual(gesamt.anzeige, MM)

    def test_addition_falsche_dimension_wirft(self):
        with self.assertRaises(DimensionsFehler):
            Groesse(300, MM) + Groesse(30, MPA)

    def test_multiplikation_kombiniert_dimensionen(self):
        flaeche = Groesse(300, MM) * Groesse(1000, MM)
        self.assertEqual(flaeche.dimension, MM2.dimension)
        self.assertAlmostEqual(flaeche.in_einheit(MM2), 300000.0)

    def test_kraft_mal_hebelarm_gibt_moment(self):
        moment = Groesse(100, KN) * Groesse(2, M)
        self.assertEqual(moment.dimension, KNM.dimension)
        self.assertAlmostEqual(moment.in_einheit(KNM), 200.0)

    def test_spannung_mal_flaeche_gibt_kraft(self):
        kraft = Groesse(500, MPA) * Groesse(1000, MM2)
        self.assertEqual(kraft.dimension, KN.dimension)
        self.assertAlmostEqual(kraft.in_einheit(KN), 500.0)

    def test_division_durch_zahl(self):
        self.assertAlmostEqual((Groesse(300, MM) / 2).in_einheit(MM), 150.0)

    def test_kehrwert(self):
        kruemmung = 1 / Groesse(10, M)
        self.assertAlmostEqual(kruemmung.si, 0.1)
        self.assertEqual(kruemmung.dimension, DIMENSIONSLOS / M.dimension)

    def test_wurzel(self):
        self.assertAlmostEqual((Groesse(4, MM2)).wurzel().in_einheit(MM), 2.0)

    def test_negation_und_betrag(self):
        self.assertAlmostEqual((-Groesse(5, KN)).in_einheit(KN), -5.0)
        self.assertAlmostEqual(abs(Groesse(-5, KN)).in_einheit(KN), 5.0)


class TestGroesseNull(unittest.TestCase):
    def test_null_ist_neutrales_element(self):
        """Sonst waere das Aufsummieren einer anfangs leeren Liste umstaendlich."""
        self.assertAlmostEqual((Groesse(300, MM) + Groesse(0, EINHEITSLOS)).in_einheit(MM), 300.0)
        self.assertAlmostEqual((Groesse(0, EINHEITSLOS) + Groesse(300, MM)).in_einheit(MM), 300.0)

    def test_nicht_null_zahl_wirft(self):
        with self.assertRaises(DimensionsFehler):
            Groesse(300, MM) + 5

    def test_summe_leer(self):
        self.assertAlmostEqual(summe([], MM2).in_einheit(MM2), 0.0)

    def test_summe(self):
        flaechen = [Groesse(100, MM2), Groesse(2, CM2)]
        self.assertAlmostEqual(summe(flaechen).in_einheit(MM2), 300.0)

    def test_builtin_sum_funktioniert(self):
        self.assertAlmostEqual(sum([Groesse(1, KN), Groesse(2, KN)]).in_einheit(KN), 3.0)


class TestGroesseVergleiche(unittest.TestCase):
    def test_vergleich(self):
        self.assertTrue(Groesse(1, M) > Groesse(999, MM))
        self.assertTrue(Groesse(1000, MM) >= Groesse(1, M))
        self.assertEqual(Groesse(1000, MM), Groesse(1, M))

    def test_vergleich_falsche_dimension_wirft(self):
        with self.assertRaises(DimensionsFehler):
            Groesse(1, M) > Groesse(1, KN)

    def test_nahe(self):
        self.assertTrue(Groesse(1.0000001, M).nahe(Groesse(1, M), rel=1e-5))
        self.assertFalse(Groesse(1.1, M).nahe(Groesse(1, M), rel=1e-5))


class TestGroesseFormatierung(unittest.TestCase):
    def test_nachlaufende_nullen_entfallen(self):
        self.assertEqual(Groesse(18.70, MPA).formatiert(2), "18.7")
        self.assertEqual(Groesse(300, MM).formatiert(0), "300")
        self.assertEqual(Groesse(0, MM).formatiert(2), "0")

    def test_latex_mit_einheit(self):
        self.assertEqual(Groesse(16.67, MPA).als_latex(1), r"16.7\,\mathrm{MPa}")
        self.assertEqual(Groesse(1.5, EINHEITSLOS).als_latex(2), "1.5")

    def test_umrechnung_bei_formatierung(self):
        self.assertEqual(Groesse(0.3, M).formatiert(0, MM), "300")

    def test_float_nur_dimensionslos(self):
        self.assertAlmostEqual(float(Groesse(1.5, EINHEITSLOS)), 1.5)
        with self.assertRaises(DimensionsFehler):
            float(Groesse(300, MM))

    def test_prozent_und_grad(self):
        self.assertAlmostEqual(Groesse(4.5, PROZENT).si, 0.045)
        self.assertAlmostEqual(Groesse(45, GRAD).si, math.pi / 4)


class TestEmpirisch(unittest.TestCase):
    """
    Empirische Normformeln: SIA 262:2025, 2.4.2.4

        tau_cd = 0.3 * sqrt(f_ck) / gamma_c    mit f_ck in N/mm^2
    """

    def test_tau_cd(self):
        erg = empirisch(
            lambda f_ck, gamma_c: 0.3 * math.sqrt(f_ck) / gamma_c,
            ergebnis=N_PRO_MM2,
            f_ck=(Groesse(30, MPA), N_PRO_MM2),
            gamma_c=(Groesse(1.5, EINHEITSLOS), EINHEITSLOS),
        )
        self.assertAlmostEqual(erg.wert.in_einheit(MPA), 0.3 * math.sqrt(30) / 1.5)

    def test_eingabe_wird_in_geforderte_einheit_umgerechnet(self):
        """f_ck in kN/m^2 angegeben muss dasselbe Resultat liefern."""
        erg = empirisch(
            lambda f_ck, gamma_c: 0.3 * math.sqrt(f_ck) / gamma_c,
            ergebnis=N_PRO_MM2,
            f_ck=(Groesse(30000, einheit("kN/m^2")), N_PRO_MM2),
            gamma_c=(Groesse(1.5, EINHEITSLOS), EINHEITSLOS),
        )
        self.assertAlmostEqual(erg.wert.in_einheit(MPA), 0.3 * math.sqrt(30) / 1.5)

    def test_falsche_dimension_wirft(self):
        with self.assertRaises(DimensionsFehler):
            empirisch(
                lambda f_ck: math.sqrt(f_ck),
                ergebnis=N_PRO_MM2,
                f_ck=(Groesse(30, MM), N_PRO_MM2),
            )

    def test_annahmen_werden_protokolliert(self):
        erg = empirisch(
            lambda f_ck, gamma_c: 0.3 * math.sqrt(f_ck) / gamma_c,
            ergebnis=N_PRO_MM2,
            f_ck=(Groesse(30, MPA), N_PRO_MM2),
            gamma_c=(Groesse(1.5, EINHEITSLOS), EINHEITSLOS),
        )
        text = erg.annahmen_text()
        self.assertIn("f_ck in N/mm²", text)
        self.assertIn("Resultat ist in N/mm²", text)
        self.assertIn(r"\mathrm{N}/\mathrm{mm}^{2}", erg.annahmen_latex())

    def test_paar_pflicht(self):
        with self.assertRaises(TypeError):
            empirisch(lambda f_ck: f_ck, ergebnis=MPA, f_ck=Groesse(30, MPA))


class TestPlattenEinheiten(unittest.TestCase):
    """Auf den Laufmeter bezogene Groessen, wie bei Platten ueblich."""

    def test_moment_pro_meter(self):
        m_rd = Groesse(120, KNM_PRO_M)
        self.assertAlmostEqual(m_rd.in_einheit(KNM_PRO_M), 120.0)
        # kNm/m hat dieselbe Dimension wie eine Kraft
        self.assertEqual(m_rd.dimension, N.dimension)

    def test_moment_pro_meter_mal_breite(self):
        gesamt = Groesse(120, KNM_PRO_M) * Groesse(2.5, M)
        self.assertAlmostEqual(gesamt.in_einheit(KNM), 300.0)


if __name__ == "__main__":
    unittest.main()


class TestBeschriftung(unittest.TestCase):
    """
    Die lesbare Schreibweise für die Oberfläche.

    Der ``name`` bleibt ASCII -- er ist der Schlüssel im Katalog. Daneben steht
    die Form, die ein Mensch lesen soll; ohne sie stand in der Werteliste und
    an den Eingabefeldern ``N/mm^2``, während die Herleitung ``N/mm²`` setzte.
    """

    def test_potenzen_werden_hochgestellt(self):
        self.assertEqual(MM2.beschriftung, "mm²")
        self.assertEqual(N_PRO_MM2.beschriftung, "N/mm²")
        self.assertEqual(KG_PRO_M3.beschriftung, "kg/m³")

    def test_der_name_bleibt_ascii(self):
        """Er dient als Schlüssel -- wer ihn ändert, findet die Einheit nicht mehr."""
        self.assertEqual(N_PRO_MM2.name, "N/mm^2")
        self.assertIs(einheit("N/mm^2"), N_PRO_MM2)

    def test_promille_gibt_seine_beschriftung_selbst_an(self):
        """Aus 'promille' liesse sich '‰' nicht ableiten."""
        self.assertEqual(PROMILLE.beschriftung, "‰")

    def test_einfache_namen_bleiben_wie_sie_sind(self):
        self.assertEqual(MM.beschriftung, "mm")
        self.assertEqual(KNM.beschriftung, "kNm")
        self.assertEqual(PROZENT.beschriftung, "%")

    def test_zusammengesetzte_einheiten_erben_die_beschriftung(self):
        self.assertEqual((KN / MM2).beschriftung, "kN/mm²")
        self.assertEqual((MM**2).beschriftung, "mm²")
