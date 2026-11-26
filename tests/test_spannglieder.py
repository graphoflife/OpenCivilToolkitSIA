"""
Spannglieder in der Querschnittsanalyse (opencivil.querschnitt.spannglieder).

Das Beispiel von Hand: ein Rechteck 300 × 600 mm aus C30/37, ohne
Betonstahl, mit vier Litzen Y1860 ⌀15.7 bei z = 100 mm -- d = 500 mm,
e = 200 mm unter dem Schwerpunkt. Nach Vorgabe:

    A_p   = 4 · 150                  =  600 mm²
    σ_p0  = 0.70 · 1860              = 1302 N/mm²
    σ_p∞  = 0.85 · 1302              = 1106.7 N/mm²
    ε_p   = 1106.7 / 195 000         = 5.675 ‰      (Litzen: E_p = 195 kN/mm²)
    P∞    = 600 · 1106.7             = 664.02 kN

Im Bruch, mit dem Spannungsblock (f_cd = 20 N/mm², f_pd = 1600/1.15):

    mit Vordehnung     T = A_p · f_pd            = 834.8 kN
    schlaff            T = A_p · (f_pd − σ_p∞)   = 170.8 kN
    ohne Verbund       T = P∞                    = 664.0 kN
    M_Rd = T · (d − T / (2 · b · f_cd))

Und das Rissmoment, mit der Vorspannung am gezogenen Rand:

    M_Riss = (k_t · f_ctm + P∞/A + P∞ · e / W) · W     k_t = 1/(1 + 0.5 · 0.2)
"""

import math
import unittest

from opencivil.material.spannstahl import SPANNSTAHLSORTEN
from opencivil.nachweis.gebrauchsebene import gebrauchsebene
from opencivil.nachweis.rissgroessen import bruttoquerschnitt, rissmoment
from opencivil.nachweis.spannungsbegrenzung import VORGABE
from opencivil.projekt.projekt import Projekt
from opencivil.projekt.querschnittsanalyse import QuerschnittsanalyseEintrag
from opencivil.querschnitt.biegung import EINACHSIG
from opencivil.querschnitt.spannglieder import (
    ANTEIL_NACH_VERLUSTEN, ANTEIL_SPANNEN, FesteSpannung, Restfestigkeit,
    VorgedehnterSpannstahl, flaechendurchmesser, grenze_nach_spannen, grenzen_verletzt,
    vorspannung,
)
from opencivil.querschnitt.werkstoffgesetz import Spannstahlgesetz
from opencivil.web import api, dienst

F_PD = 1600e6 / 1.15
SIGMA_PINF = 0.85 * 0.70 * 1860e6
A_P = 600e-6
B, D, F_CD = 0.3, 0.5, 20e6
W = 0.3 * 0.6 ** 2 / 6
K_T = 1.0 / (1.0 + 0.5 * 0.2)


def projekt(wirkung="vordehnung", verbund="mit", *, staebe=False, rechenart="block",
            **felder) -> Projekt:
    """Das Beispiel von Hand -- mit den fünf Stäben der Vorlage, wenn ``staebe``."""
    p = Projekt(name="Spannglied")
    p.beton()
    p.stahl()
    p.spannstahl("Y1860")
    a = p.analyse("Balken", beton="b1", stahl="s1", rechenarten={"b1": rechenart}, **felder)
    if not staebe:
        a.staebe.clear()
        a.stablinien.clear()
    a.spannglied(150.0, 100.0, stahl="sp1", durchmesser=15.7, anzahl=4,
                 wirkung=wirkung, verbund=verbund)
    a.lastfall("Feld", M_y_Ed=300.0)
    return p


def urteil(ergebnis, art: str, fall: str):
    return next(u for u in ergebnis.urteile_von("a1") if u.art == art and u.fall == fall)


def biegewiderstand(T: float) -> float:
    """M_Rd in Nm mit dem Spannungsblock, wenn der Spannstahl die Kraft ``T`` trägt."""
    return T * (D - T / (2.0 * B * F_CD))


def geloest(p: Projekt):
    """Der Aufbau und die Lösung der Analyse a1 -- ohne ihre Nachweise."""
    aufbau = p.aufbauen()
    loesung = aufbau.werk.loese(*aufbau.ziele_von("a1"))
    return aufbau.querschnittsanalysen["a1"], lambda kid: loesung.werte[kid].groesse.si


class TestRegeln(unittest.TestCase):
    """Die Vorgaben und die Grenzen der Spannung, in N/mm²."""

    def test_vorgaben(self):
        p0, pinf = vorspannung(1860.0, None, None)
        self.assertAlmostEqual(p0, 1302.0)
        self.assertAlmostEqual(pinf, 1106.7)

    def test_was_eingegeben_ist_gilt(self):
        """σ_p∞ folgt einem eingegebenen σ_p0 -- und ein eingegebenes σ_p∞ bleibt."""
        self.assertEqual(vorspannung(1860.0, 1400.0, None), (1400.0, 0.85 * 1400.0))
        self.assertEqual(vorspannung(1860.0, None, 1000.0), (0.70 * 1860.0, 1000.0))

    def test_grenze_nach_dem_spannen(self):
        """Gl. (22): min(0.75 · 1860; 0.85 · 1600) = min(1395; 1360)."""
        self.assertAlmostEqual(grenze_nach_spannen(1860.0, 1600.0), 1360.0)

    def test_die_vorgabe_haelt_die_grenzen(self):
        self.assertEqual(grenzen_verletzt(1302.0, 1106.7, 1860.0, 1600.0), [])

    def test_jede_grenze_fuer_sich(self):
        zu_hoch, = grenzen_verletzt(1400.0, 1106.7, 1860.0, 1600.0)
        self.assertIn("= 1360 N/mm² (SIA 262:2025, 4.1.5.2.2, Gl. 22)", zu_hoch)
        zu_tief, = grenzen_verletzt(1302.0, 800.0, 1860.0, 1600.0)
        self.assertIn("unter 0.45·f_pk = 837 N/mm²", zu_tief)
        gewachsen, = grenzen_verletzt(1302.0, 1350.0, 1860.0, 1600.0)
        self.assertIn("über σ_p0 = 1302 N/mm²", gewachsen)

    def test_wo_die_vorgabe_ueber_gl_22_liegt(self):
        """
        0.70 · f_pk überschreitet Gl. (22) bei Y1100 (770 > 765) und Y1030
        (721 > 705.5) -- dort steht schon die Vorgabe rot. Offen beim Benutzer
        (TODO); bei allen anderen Sorten hält sie.
        """
        ueber = [sorte for sorte, s in SPANNSTAHLSORTEN.items()
                 if grenzen_verletzt(*vorspannung(s.f_pk, None, None), s.f_pk, s.f_p01k)]
        self.assertEqual(ueber, ["Y1100", "Y1030"])

    def test_gezeichnet_mit_seiner_flaeche(self):
        """Vier Litzen à 150 mm² zeichnen sich als Kreis von 600 mm²."""
        self.assertAlmostEqual(flaechendurchmesser(600.0), math.sqrt(2400.0 / math.pi))


class TestGesetze(unittest.TestCase):
    """Die Gesetze eines Glieds über der Dehnung des Querschnitts an seiner Stelle."""

    def setUp(self):
        self.stahl = Spannstahlgesetz(E_p=195e9, f_pd=F_PD, eps_ud=0.020)
        self.eps_p = SIGMA_PINF / 195e9

    def test_mit_vordehnung(self):
        g = VorgedehnterSpannstahl(stahl=self.stahl, eps_p=self.eps_p)
        self.assertAlmostEqual(g.spannung(0.0), SIGMA_PINF, delta=1.0)
        self.assertEqual(g.spannung(0.010), F_PD)
        self.assertEqual(g.spannung(-self.eps_p - 1e-4), 0.0)              # entspannt
        self.assertEqual(g.spannung(0.020 - self.eps_p + 1e-4), 0.0)       # gerissen
        self.assertAlmostEqual(g.eps_ud, 0.020 - self.eps_p)
        self.assertAlmostEqual(g.eps_yd, F_PD / 195e9 - self.eps_p)

    def test_schlaff_mit_restfestigkeit(self):
        """Um σ_p∞ gesenkt: bei null nichts, gedrückt bis −σ_p∞."""
        g = Restfestigkeit(stahl=self.stahl, eps_p=self.eps_p, sigma_pinf=SIGMA_PINF)
        self.assertAlmostEqual(g.spannung(0.0), 0.0, delta=1.0)
        self.assertAlmostEqual(g.spannung(0.010), F_PD - SIGMA_PINF)
        self.assertEqual(g.spannung(-self.eps_p - 1e-4), -SIGMA_PINF)
        self.assertAlmostEqual(g.eps_ud, 0.020 - self.eps_p)

    def test_ohne_verbund(self):
        """Die Kraft nach allen Verlusten, gleich welche Dehnung -- es fliesst nie."""
        g = FesteSpannung(sigma=SIGMA_PINF)
        for eps in (-0.003, 0.0, 0.010, 0.050):
            self.assertEqual(g.spannung(eps), SIGMA_PINF)
        self.assertEqual(g.eps_yd, math.inf)


class TestWerte(unittest.TestCase):
    """Die Werte eines Glieds, wie der Bericht sie herleitet."""

    def werte(self, p: Projekt):
        e = p.rechnen()
        return {k: e.wert(f"querschnittsanalyse.a1.P1.{k}").groesse.si
                for k in ("A_p", "sigma_p0", "sigma_pinf", "eps_p", "P_inf")}

    def test_von_hand(self):
        w = self.werte(projekt())
        self.assertAlmostEqual(w["A_p"], A_P)
        self.assertAlmostEqual(w["sigma_p0"] / 1e6, 1302.0)
        self.assertAlmostEqual(w["sigma_pinf"] / 1e6, 1106.7)
        self.assertAlmostEqual(w["eps_p"] * 1e3, 5.675, places=3)
        self.assertAlmostEqual(w["P_inf"] / 1e3, 664.02)

    def test_eingegebene_spannungen(self):
        p = projekt()
        g = p.querschnittsanalysen[0].spannglieder[0]
        g.sigma_p0, g.sigma_pinf = 1350.0, 1000.0
        w = self.werte(p)
        self.assertAlmostEqual(w["sigma_p0"] / 1e6, 1350.0)
        self.assertAlmostEqual(w["P_inf"] / 1e3, 600.0)
        self.assertAlmostEqual(w["eps_p"], 1000.0 / 195000.0)

    def test_draehte_mit_ihrem_modul(self):
        """30 Drähte ⌀5.0 à 19.6 mm², mit E_p = 200 kN/mm² statt 195."""
        p = projekt()
        g = p.querschnittsanalysen[0].spannglieder[0]
        g.durchmesser, g.anzahl = 5.0, 30
        w = self.werte(p)
        self.assertAlmostEqual(w["A_p"], 30 * 19.6e-6)
        self.assertAlmostEqual(w["eps_p"], 1106.7 / 200000.0)


class TestBiegewiderstand(unittest.TestCase):
    """M_Rd von Hand mit dem Spannungsblock -- je Wirkung und Verbund, bei M_Ed = 300 kNm."""

    def grad(self, *art) -> float:
        return urteil(projekt(*art).rechnen(), "M-N", "Feld").erfuellungsgrad.si

    def test_mit_vordehnung_bis_f_pd(self):
        self.assertAlmostEqual(self.grad() * 300e3, biegewiderstand(A_P * F_PD), delta=50.0)

    def test_schlaff_nur_was_ueber_sigma_pinf_hinausgeht(self):
        self.assertAlmostEqual(self.grad("restfestigkeit") * 300e3,
                               biegewiderstand(A_P * (F_PD - SIGMA_PINF)), delta=50.0)

    def test_ohne_verbund_die_kraft_nach_allen_verlusten(self):
        self.assertAlmostEqual(self.grad("vordehnung", "ohne") * 300e3,
                               biegewiderstand(A_P * SIGMA_PINF), delta=50.0)

    def test_schlaff_ohne_verbund_traegt_nichts(self):
        self.assertEqual(self.grad("restfestigkeit", "ohne"), 0.0)


class TestRissmoment(unittest.TestCase):
    """
    Die Vorspannung drückt den Rand, der unter dem Moment reisst -- mit oder
    ohne Verbund. Schlaff angesetzt steht sie in den Lastfällen, nicht hier.
    """

    MIT_VORSPANNUNG = (K_T * 2.9e6 + 664.02e3 / 0.18 + 664.02e3 * 0.2 / W) * W

    def rissmoment(self, *art):
        analyse, wert = geloest(projekt(*art))
        return rissmoment(bruttoquerschnitt(analyse, wert), 1.0, 0.0)

    def test_mit_vordehnung_von_hand(self):
        for verbund in ("mit", "ohne"):
            with self.subTest(verbund=verbund):
                riss = self.rissmoment("vordehnung", verbund)
                self.assertAlmostEqual(riss.M_Riss, self.MIT_VORSPANNUNG, delta=1.0)
                self.assertEqual(riss.ecke.punkt[1], 0.0)

    def test_schlaff_ohne_vorspannung(self):
        riss = self.rissmoment("restfestigkeit")
        self.assertEqual(riss.sigma_p, 0.0)
        self.assertAlmostEqual(riss.M_Riss, K_T * 2.9e6 * W, delta=1.0)

    def test_sproedes_versagen_misst_daran(self):
        grad = urteil(projekt(sproede=True).rechnen(), "Riss", "Zug unten").erfuellungsgrad.si
        self.assertAlmostEqual(grad, biegewiderstand(A_P * F_PD) / self.MIT_VORSPANNUNG,
                               delta=1e-3)


class TestOhneLast(unittest.TestCase):
    """
    Ohne Last verformt sich ein vorgespannter Querschnitt schon: er krümmt sich
    vom Glied weg, und der gestauchte Beton nimmt dem Glied etwas von σ_p∞.
    Ohne Glied bleibt die Ebene genau null.
    """

    def ebene(self, p: Projekt):
        analyse, wert = geloest(p)
        q, _, _ = analyse.querschnitt(wert, VORGABE)
        return gebrauchsebene(q, N=0.0, M_y=0.0, M_z=0.0, biegung=EINACHSIG)

    def test_mit_vordehnung(self):
        e = self.ebene(projekt())
        self.assertTrue(e.konvergiert)
        self.assertLess(e.chi, 0.0)
        self.assertAlmostEqual(e.N, 0.0, delta=10.0)
        self.assertAlmostEqual(e.M_y, 0.0, delta=10.0)
        self.assertLess(e.sigma_s[-1], SIGMA_PINF)
        self.assertGreater(e.sigma_s[-1], 0.95 * SIGMA_PINF)

    def test_ohne_glied(self):
        p = projekt(staebe=True)
        p.querschnittsanalysen[0].spannglieder.clear()
        e = self.ebene(p)
        self.assertEqual((e.eps_m, e.chi), (0.0, 0.0))


class TestNachweise(unittest.TestCase):
    """Was die Nachweise am Betonstahl mit einem Spannglied tun."""

    def test_duktilitaet_mit_spannstahl_in_der_zugzone(self):
        """4.1.4.2.5 nennt Betonstahl der Klassen B und C -- über x/d kein Nachweis."""
        u = urteil(projekt(duktilitaet=True).rechnen(), "x/d", "Zug unten")
        self.assertFalse(u.erfuellt)
        self.assertIn("Spannstahl Y1860 in der Zugzone", u.begruendung)

    def test_die_stahlspannung_gilt_dem_betonstahl(self):
        """Mit den Stäben der Vorlage begrenzt sie deren Spannung; ohne sie gibt es nichts zu begrenzen."""
        for staebe, erwartet in ((True, "Linie 1: σ_s ="), (False, "Ohne Betonstahl")):
            with self.subTest(staebe=staebe):
                p = projekt(staebe=staebe)
                p.querschnittsanalysen[0].quasistaendig.lastfall("Dauer", M_y_Ed=150.0)
                begruendungen = [u.begruendung for u in p.rechnen().urteile_von("a1")
                                 if u.fall == "Dauer"]
                self.assertEqual(len(begruendungen), 1)
                self.assertIn(erwartet, begruendungen[0])


class TestZeichnung(unittest.TestCase):
    """Was das Zeichenfenster zu den Gliedern bekommt -- aus derselben Herleitung."""

    @classmethod
    def setUpClass(cls):
        p = Projekt(name="Spannglied")
        p.beton()
        p.stahl()
        p.spannstahl("Y1860")
        p.spannstahl("Y1030")
        a = p.analyse("Balken", beton="b1", stahl="s1")
        a.spannglied(150.0, 100.0, stahl="sp1", durchmesser=15.7, anzahl=4)
        a.spannglied(100.0, 100.0, stahl="sp2", durchmesser=15.7)
        a.spannglied(200.0, 100.0, stahl="sp1", durchmesser=12.9, anzahl=2,
                     sigma_p0=1450.0, sigma_pinf=800.0)
        a.spannglied(250.0, 100.0, stahl="b1", durchmesser=15.7)
        a.spannglied(-20.0, 100.0, stahl="", durchmesser=15.7)
        cls.d = dienst.bearbeite("geometrie", {"projekt": p.als_dict(), "kennung": "a1"}).daten
        cls.glieder = {g["kennung"]: g for g in cls.d["spannglieder"]}

    def meldungen(self, kennung):
        return [(m["fehler"], m["text"]) for m in self.d["meldungen"] if kennung in m["elemente"]]

    def test_werte_des_beispiels(self):
        g = self.glieder["P1"]
        self.assertEqual(self.meldungen("P1"), [])
        self.assertEqual(g["werte"]["erzeugnis"], "Y1860S7-15.7")
        self.assertAlmostEqual(g["werte"]["P_inf"], 664.02)
        self.assertAlmostEqual(g["werte"]["eps_p"], 1106.7 / 195.0)
        self.assertAlmostEqual(g["durchmesser"], flaechendurchmesser(600.0))

    def test_ein_fehlendes_erzeugnis_ist_grau(self):
        """Y1030 gibt es nur in Stäben: es fehlt eine Wahl, gezeichnet wird mit ⌀15.7."""
        (fehler, text), = self.meldungen("P2")
        self.assertFalse(fehler)
        self.assertIn("Y1030 gibt es nicht mit ⌀15.7 mm", text)
        self.assertIsNone(self.glieder["P2"]["werte"])
        self.assertEqual(self.glieder["P2"]["durchmesser"], 15.7)
        self.assertFalse(self.d["gueltig"])

    def test_verletzte_grenzen_sind_rot_und_es_rechnet(self):
        meldungen = self.meldungen("P3")
        self.assertEqual([f for f, _ in meldungen], [True, True])
        self.assertIn("Gl. 22", meldungen[0][1])
        self.assertIn("0.45·f_pk", meldungen[1][1])
        self.assertAlmostEqual(self.glieder["P3"]["werte"]["P_inf"], 160.0)

    def test_falsches_material_rot_fehlendes_grau(self):
        self.assertEqual(self.meldungen("P4"), [(True, "Spannglied 4: «C30/37» ist kein Spannstahl.")])
        meldungen = self.meldungen("P5")
        self.assertIn((False, "Spannglied 5: noch kein Material gewählt."), meldungen)
        self.assertTrue(any(f and "nicht ganz im Beton" in t for f, t in meldungen))
        self.assertFalse(self.glieder["P5"]["im_beton"])

    def test_meldungen_nennen_namen(self):
        for m in self.d["meldungen"]:
            self.assertNotRegex(m["text"], r"\bP\d\b")


class TestEintrag(unittest.TestCase):

    def test_rundreise(self):
        a = projekt().querschnittsanalysen[0]
        a.spannglieder[0].sigma_p0 = 1350.0
        self.assertEqual(QuerschnittsanalyseEintrag.aus_dict(a.als_dict()), a)

    def test_kennungen_mit_p(self):
        a = projekt().querschnittsanalysen[0]
        a.spannglied(150.0, 500.0, stahl="sp1")
        self.assertEqual([g.kennung for g in a.spannglieder], ["P1", "P2"])

    def test_der_katalog(self):
        sp = api.katalog()["querschnittsanalyse"]["spannglied"]
        self.assertEqual([(w["wert"], w["kurz"]) for w in sp["wirkungen"]],
                         [("vordehnung", "Vordehnung"), ("restfestigkeit", "schlaff")])
        self.assertEqual([(v["wert"], v["kurz"]) for v in sp["verbunde"]],
                         [("mit", "mit"), ("ohne", "ohne")])
        self.assertEqual(sp["vorgaben"], {"sigma_p0": f"{ANTEIL_SPANNEN:.2f}·f_pk",
                                          "sigma_pinf": f"{ANTEIL_NACH_VERLUSTEN:.2f}·σ_p0"})


if __name__ == "__main__":
    unittest.main()
