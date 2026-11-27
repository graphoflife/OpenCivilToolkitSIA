"""
Die Kurzform eines Nachweises: seine Formeln in zwei, drei Zeilen.

Geprüft wird der Formelbaum -- lesen, einsetzen, kürzen, setzen, rechnen --
und die Kurzform der häufigsten Nachweise der Platte: Biegung bei N = 0,
Querkraft mit und ohne Bügel; dazu die Querkraft im Bohrpfahl. Jede Kurzform rechnet dasselbe wie die
Herleitung; wo das nicht aufginge, bleibt es bei den einzelnen Zeilen.
"""

import math
import unittest

from opencivil.core import formelbaum as fb
from opencivil.core.einheiten import EINHEITSLOS, KN, KNM, MM, MM2, N_PRO_MM2, Groesse
from opencivil.core.kurzform import KURZBREITE, kurzform, normstellen
from opencivil.core.latex import Formelzeile, bruchtiefe, sichtbare_breite
from opencivil.core.protokoll import GleichungBlock, Kurz, Protokoll
from opencivil.core.wert import WertDef
from opencivil.projekt import beispiele
from opencivil.web import dienst


def wert(kennung, symbol, zahl, einheit=EINHEITSLOS, stellen=1):
    return WertDef(kennung, symbol, einheit, stellen=stellen).belegen(Groesse(zahl, einheit))


def baum(ergebnis, vorlage, eingaben, **zusatz):
    return fb.lesen(Formelzeile.bauen(ergebnis, vorlage, eingaben, **zusatz))


#: Die Biegung bei N = 0, wie die Handrechnung sie schreibt.
A_S = wert("A_s", "A_s", 2450.0, MM2, 0)
F_YD = wert("f_yd", "f_{yd}", 435.0, N_PRO_MM2, 0)
B = wert("b", "b", 1000.0, MM)
F_CD = wert("f_cd", "f_{cd}", 20.0, N_PRO_MM2, 0)
D = wert("d", "d", 248.1, MM)
X_SI = A_S.groesse.si * F_YD.groesse.si / (0.85 * B.groesse.si * F_CD.groesse.si)
X = WertDef("x", "x", MM).belegen(Groesse.aus_si(X_SI, MM))
M_SI = A_S.groesse.si * F_YD.groesse.si * (D.groesse.si - 0.85 * X_SI / 2)
M_RD = WertDef("M_Rd", "M_{Rd}", KNM).belegen(Groesse.aus_si(M_SI, KNM))
VORLAGE_X = r"\frac{@A_s \cdot @f_yd}{0.85 \cdot @b \cdot @f_cd}"
VORLAGE_M = r"@A_s \cdot @f_yd \cdot \left(@d - \frac{0.85 \cdot @x}{2}\right)"
EINGABEN = {"A_s": A_S, "f_yd": F_YD, "b": B, "f_cd": F_CD}


class TestFormelbaum(unittest.TestCase):

    def test_liest_rechnet_und_setzt(self):
        a, b, c = wert("a", "a", 3.0), wert("b", "b", 4.0), wert("c", "c", 9.0)
        t = baum(wert("e", "e", 3.0), r"\frac{@a \cdot @b}{2} - \sqrt{@c}",
                 {"a": a, "b": b, "c": c})
        self.assertAlmostEqual(fb.rechnen(t), 3.0)
        self.assertEqual(fb.symbolisch(t), r"\frac{a \cdot b}{2} - \sqrt{c}")

    def test_einsetzen_kuerzt_was_in_zaehler_und_nenner_steht(self):
        """Die 0.85 des Spannungsblocks steht in x und in M_Rd -- eingesetzt hebt sie sich."""
        x = baum(X, VORLAGE_X, EINGABEN)
        m = baum(M_RD, VORLAGE_M, {**EINGABEN, "d": D, "x": X})
        eingesetzt = fb.einsetzen(m, "x", x)
        self.assertEqual(
            fb.symbolisch(eingesetzt),
            r"A_s \cdot f_{yd} \cdot \left(d - \frac{A_s \cdot f_{yd}}{2 \cdot b \cdot f_{cd}}\right)")
        self.assertTrue(math.isclose(fb.rechnen(eingesetzt), M_SI, rel_tol=1e-12))
        self.assertIn(r"2 \cdot 1000\,\mathrm{mm}", fb.numerisch(eingesetzt))

    def test_in_ein_empirisches_blatt_wird_nicht_eingesetzt(self):
        """d steht in k_d als blanke Zahl in mm -- eine Formel in SI dafür wäre falsch."""
        eps, k_g = wert("eps", r"\varepsilon_v", 0.003), wert("k_g", "k_g", 1.2)
        k_d = 1 / (1 + 0.003 * 248.1 * 1.2)
        t = baum(wert("k_d", "k_d", k_d), r"\frac{1}{1 + @eps \cdot @d \cdot @k_g}",
                 {"eps": eps, "d": D, "k_g": k_g}, empirisch={"d": MM})
        self.assertTrue(math.isclose(fb.rechnen(t), k_d, rel_tol=1e-12))
        self.assertEqual(fb.einsetzen(t, "d", fb.Zahl(1.0, "1")), t)
        self.assertEqual(fb.empirische(t), [("d", MM)])

    def test_min_betrag_und_winkel(self):
        a, b = wert("a", "a", 5.0), wert("b", "b", -2.0)
        w = WertDef("w", r"\alpha").belegen(Groesse(math.pi / 6, EINHEITSLOS))
        t = baum(wert("e", "e", 1.0), r"\min\left[@a;\ \left|@b\right|\right] \cdot \sin @w",
                 {"a": a, "b": b, "w": w})
        self.assertAlmostEqual(fb.rechnen(t), 1.0)
        self.assertEqual(fb.symbolisch(t),
                         r"\min\left[a;\ \left|b\right|\right] \cdot \sin \alpha")

    def test_hochzahlen_bleiben_wie_geschrieben(self):
        """Aus (a/b)^2 wird nicht a^2/b^2, aus der Kubikwurzel keine Hochzahl 1/3."""
        a, b = wert("a", "a", 8.0), wert("b", "b", 2.0)
        t = baum(wert("e", "e", 16.0), r"\left(\frac{@a}{@b}\right)^{2}", {"a": a, "b": b})
        self.assertEqual(fb.symbolisch(t), r"\left(\frac{a}{b}\right)^{2}")
        t = baum(wert("e", "e", 2.0), r"\sqrt[3]{@a}", {"a": a})
        self.assertEqual(fb.symbolisch(t), r"\sqrt[3]{a}")
        self.assertAlmostEqual(fb.rechnen(t), 2.0)

    def test_eine_negative_zahl_hinter_einem_rechenzeichen_in_klammern(self):
        a, b = wert("a", "a", 10.0, KN), wert("b", "b", -5.0, KN)
        t = baum(wert("e", "e", 15.0, KN), r"@a - @b", {"a": a, "b": b})
        self.assertEqual(fb.numerisch(t),
                         r"10\,\mathrm{kN} - \left(-5\,\mathrm{kN}\right)")

    def test_was_er_nicht_liest(self):
        f_ck = wert("f_ck", "f_{ck}", 30.0, N_PRO_MM2)
        for vorlage in (r"@f_ck + 8\,\mathrm{N}/\mathrm{mm}^{2}", r"\sum F_i",
                        r"1 - \frac{@f_ck}{147^\circ}"):
            with self.subTest(vorlage=vorlage), self.assertRaises(fb.Unlesbar):
                baum(f_ck, vorlage, {"f_ck": f_ck})


class TestKurzformDerPlatte(unittest.TestCase):
    """Die drei häufigsten Nachweise der Platte, so wie das Auge sie oben zeigt."""

    @classmethod
    def setUpClass(cls):
        cls.aufbau = beispiele.jeder_nachweis().aufbauen()

    def kurz(self, ziel):
        return kurzform(self.aufbau.werk.loese(ziel).protokoll, ziel)

    def test_biegung_in_einer_formel(self):
        zeilen = self.kurz("querschnitt.q1.nachweis.mn.x.Feld.erfuellungsgrad")
        self.assertEqual([z.titel for z in zeilen],
                         ["Momentenwiderstand bei reiner Biegung", "Erfüllungsgrad"])
        m = zeilen[0].formelzeile
        # Unter dem Symbol, unter dem der Erfüllungsgrad ihn braucht.
        self.assertEqual(m.symbol, "M_{Rd}")
        self.assertEqual(m.analytisch, (
            r"A_{s,2,x} \cdot f_{yd} \cdot \left(d_{2,x} - "
            r"\frac{A_{s,2,x} \cdot f_{yd}}{2 \cdot b \cdot f_{cd}}\right)"))
        self.assertEqual(m.ergebnis, r"230.6\,\mathrm{kNm}")
        self.assertIn(r"\Rightarrow", zeilen[1].latex)

    def test_negatives_moment(self):
        zeilen = self.kurz("querschnitt.q1.nachweis.mn.x.Stütze.erfuellungsgrad")
        self.assertTrue(zeilen[0].formelzeile.analytisch.startswith("-A_{s,3,x}"))
        self.assertEqual(zeilen[0].formelzeile.ergebnis, r"-78.3\,\mathrm{kNm}")

    def test_querkraft_mit_buegeln_in_drei_formeln(self):
        zeilen = self.kurz("querschnitt.q1.nachweis.querkraft.x.Feld.erfuellungsgrad")
        self.assertEqual([z.formelzeile.symbol for z in zeilen][:2],
                         ["V_{Rd,s}", "V_{Rd,c}"])
        self.assertIn(r"\min\left[V_{Rd,s};\ V_{Rd,c}\right]", zeilen[2].formelzeile.analytisch)
        self.assertEqual(len(zeilen), 3)

    def test_plattenquerkraft_in_drei_formeln(self):
        """Die Dehnung, der Widerstand mit k_d darin, der Erfüllungsgrad --
        plastisch (Feld) wie elastisch (Rand) gleich gebaut."""
        for ziel, ergebnis in (("Feld", r"80.8\,\mathrm{kN}/\mathrm{m}"),
                               ("Rand", r"106.2\,\mathrm{kN}/\mathrm{m}")):
            with self.subTest(ziel=ziel):
                zeilen = self.kurz(f"querschnitt.q2.nachweis.querkraft.x.{ziel}.erfuellungsgrad")
                self.assertEqual(len(zeilen), 3)
                self.assertEqual(zeilen[0].formelzeile.symbol, r"\varepsilon_v")
                v = zeilen[1]
                self.assertEqual(v.formelzeile.analytisch,
                                 r"\frac{\tau_{cd} \cdot d_v}{1 + \varepsilon_v \cdot d \cdot k_g}")
                # d geht als blanke Zahl in mm ein -- das steht dahinter.
                self.assertIn(r"d\ \text{in}\ \mathrm{mm}", v.latex)
                self.assertEqual(v.formelzeile.ergebnis, ergebnis)
                # Die Normstellen beider Zeilen, die Norm einmal.
                self.assertEqual(v.referenz.count("SIA 262:2025"), 1)
                self.assertEqual(v.referenz.count(";"), 1)

    def test_jede_eingesetzte_formel_bleibt_schmal_und_flach(self):
        for ziel in ("querschnitt.q1.nachweis.mn.x.Feld.erfuellungsgrad",
                     "querschnitt.q1.nachweis.querkraft.x.Feld.erfuellungsgrad",
                     "querschnitt.q2.nachweis.querkraft.x.Feld.erfuellungsgrad",
                     "querschnitt.q2.nachweis.querkraft.x.Rand.erfuellungsgrad"):
            for z in self.kurz(ziel):
                with self.subTest(ziel=ziel, titel=z.titel):
                    self.assertLessEqual(sichtbare_breite(z.formelzeile.analytisch), KURZBREITE)
                    self.assertLessEqual(bruchtiefe(z.formelzeile.analytisch), 1)

    def test_was_sich_nicht_kuerzen_laesst_hat_keine(self):
        """Interpoliert zwischen zwei Eckpunkten: dort gibt es keine kurze Formel."""
        self.assertEqual(self.kurz("querschnitt.q1.nachweis.mn.x.Feld_mit_Druck.erfuellungsgrad"), [])
        self.assertEqual(self.kurz("gibt.es.nicht"), [])


class TestKurzformDesPfahls(unittest.TestCase):
    """Die Querkraft im Bohrpfahl: Wendel, Druckdiagonalen, der Erfüllungsgrad mit dem Minimum."""

    @classmethod
    def setUpClass(cls):
        cls.aufbau = beispiele.jeder_nachweis().aufbauen()

    def kurz(self, ziel):
        return kurzform(self.aufbau.werk.loese(ziel).protokoll, ziel)

    def test_querkraft_im_bohrpfahl_in_drei_formeln(self):
        zeilen = self.kurz("pfahl.t1.nachweis.innen_quer.Druck.querkraft")
        self.assertEqual([z.formelzeile.symbol for z in zeilen][:2], ["V_{Rd,s}", "V_{Rd,c}"])
        grad = zeilen[2].formelzeile
        self.assertEqual(grad.analytisch, (
            r"\frac{\eta_i \cdot \min\left[V_{Rd,s};\ V_{Rd,c}\right]}{\left|V\right|}"))
        self.assertEqual(grad.ergebnis, "1.79")
        self.assertEqual(len(zeilen), 3)
        # Mit η_i geht seine Normstelle in die Zeile.
        self.assertIn("SIA 267:2013", zeilen[2].referenz)
        for z in zeilen:
            with self.subTest(titel=z.titel):
                self.assertLessEqual(sichtbare_breite(z.formelzeile.analytisch), KURZBREITE)
                self.assertLessEqual(bruchtiefe(z.formelzeile.analytisch), 1)

    def test_der_mikropfahl_hat_keine(self):
        """Sein Widerstand ist schon zwei kurze Zeilen; gekennzeichnet ist dort nichts."""
        self.assertEqual(self.kurz("pfahl.t4.nachweis.innen_quer.Zug.querkraft"), [])


class TestKurzformRegeln(unittest.TestCase):
    """An einer kleinen Mitschrift von Hand: was eingesetzt wird und was nicht."""

    def setUp(self):
        self.a, self.b = wert("a", "a", 2.0), wert("b", "b", 3.0)
        self.p = Protokoll()

    def grad(self, y):
        """Der Abschluss: alpha = y / 7."""
        sieben = wert("z", "z", 7.0)
        alpha = wert("alpha", r"\alpha", y.groesse.si / 7.0, stellen=2)
        self.p.formel(alpha, r"\frac{@y}{@z}", {"y": y, "z": sieben})
        return kurzform(self.p, "alpha")

    def test_eingesetzt_wird_nur_was_nachgerechnet_aufgeht(self):
        """Eine Zeile, deren Formel nicht ihr Ergebnis gibt, geht nirgends ein."""
        x = wert("x", "x", 6.0)
        self.p.formel(x, r"@a + @b", {"a": self.a, "b": self.b}, kurz=Kurz.EINSETZEN)
        y = wert("y", "y", 7.0)
        self.p.formel(y, r"@x + 1", {"x": x}, kurz=Kurz.ZEILE)
        zeilen = self.grad(y)
        self.assertEqual([z.wert_id for z in zeilen], ["x", "y", "alpha"])
        self.assertEqual(zeilen[1].formelzeile.analytisch, "x + 1")

    def test_eingesetzt_wenn_es_aufgeht(self):
        x = wert("x", "x", 6.0)
        self.p.formel(x, r"@a \cdot @b", {"a": self.a, "b": self.b}, kurz=Kurz.EINSETZEN)
        y = wert("y", "y", 7.0)
        self.p.formel(y, r"@x + 1", {"x": x}, kurz=Kurz.ZEILE)
        zeilen = self.grad(y)
        self.assertEqual([z.wert_id for z in zeilen], ["y", "alpha"])
        self.assertEqual(zeilen[0].formelzeile.analytisch, r"a \cdot b + 1")

    def test_zu_breit_wird_eine_eigene_zeile(self):
        namen = [f"c_{{{i}}}" for i in range(12)]
        teile = {f"c{i}": wert(f"c{i}", n, 1.0) for i, n in enumerate(namen)}
        x = wert("x", "x", 12.0)
        self.p.formel(x, " + ".join(f"@c{i}" for i in range(12)), teile, kurz=Kurz.EINSETZEN)
        y = wert("y", "y", 14.0)
        self.p.formel(y, r"@x + @a", {"x": x, "a": self.a}, kurz=Kurz.ZEILE)
        zeilen = self.grad(y)
        self.assertEqual([z.wert_id for z in zeilen], ["x", "y", "alpha"])

    def test_kein_bruch_im_bruch(self):
        """``x = a/b`` in ``y = 1/(1 + x)`` gäbe einen Bruch im Nenner: x bleibt eine Zeile."""
        x = wert("x", "x", 2.0 / 3.0)
        self.p.formel(x, r"\frac{@a}{@b}", {"a": self.a, "b": self.b}, kurz=Kurz.EINSETZEN)
        y = wert("y", "y", 0.6)
        self.p.formel(y, r"\frac{1}{1 + @x}", {"x": x}, kurz=Kurz.ZEILE)
        zeilen = self.grad(y)
        self.assertEqual([z.wert_id for z in zeilen], ["x", "y", "alpha"])
        self.assertEqual(zeilen[1].formelzeile.analytisch, r"\frac{1}{1 + x}")

    def test_eine_weitergabe_wird_uebersprungen(self):
        """``R = M``: die Zeile von M steht unter dem Symbol R."""
        m = wert("m", "M_{0}", 7.0)
        self.p.formel(m, r"@a \cdot @b + 1", {"a": self.a, "b": self.b}, kurz=Kurz.ZEILE)
        r = wert("r", "R", 7.0)
        self.p.formel(r, "@P", {"P": m})
        zeilen = self.grad(r)
        self.assertEqual([z.wert_id for z in zeilen], ["m", "alpha"])
        self.assertEqual(zeilen[0].formelzeile.symbol, "R")
        self.assertTrue(zeilen[0].latex.startswith("R = "))

    def test_ohne_gekennzeichnete_zeilen_keine_kurzform(self):
        y = wert("y", "y", 6.0)
        self.p.formel(y, r"@a \cdot @b", {"a": self.a, "b": self.b})
        self.assertEqual(self.grad(y), [])

    def test_normstellen_ohne_wiederholung(self):
        self.assertEqual(
            normstellen(["SIA 262:2025, 4.3.3.2.1, (35)", "", "SIA 262:2025, 4.3.3.2.3, (41)",
                         "SIA 262:2025, 4.3.3.2.3, (41); 4.3.3.2.6"]),
            "SIA 262:2025, 4.3.3.2.1, (35); 4.3.3.2.3, (41); 4.3.3.2.6")


class TestDienst(unittest.TestCase):

    def test_das_auge_bekommt_die_kurzform(self):
        ziel = "querschnitt.q1.nachweis.mn.x.Feld.erfuellungsgrad"
        rumpf = {"projekt": beispiele.jeder_nachweis().als_dict()}
        antwort = dienst.bearbeite("rechnen", {**rumpf, "ziele": [ziel]})
        self.assertEqual(antwort.status, 200)
        kurz = antwort.daten["kurzform"]
        self.assertEqual([k["art"] for k in kurz], ["gleichung", "gleichung"])
        self.assertIn(r"\frac{A_{s,2,x} \cdot f_{yd}}{2 \cdot b \cdot f_{cd}}", kurz[0]["latex"])
        self.assertIn("$$", kurz[0]["markdown"])
        # Eine eingesetzte Formel steht nicht in der Formelsammlung.
        self.assertNotIn("formelseite", kurz[0])


if __name__ == "__main__":
    unittest.main()
