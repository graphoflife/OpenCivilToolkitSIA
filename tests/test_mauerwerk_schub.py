"""
Die Wand aus Mauerwerk, Schritt 14c: die Scheibe -- wie die waagrechten
Lasten zu den Pfeilern kommen und das Moment der lotrechten neben ihren
Mitten -- gegen die Handrechnung, dazu Schub und Gleiten (SIA 266:2015,
4.3.2.2, Gl. (13) und (14)) und die Normalkraft unter Schub mit der
gedrückten Länge (4.3.3.1, Gl. (17)).
"""

import unittest

from opencivil.core.nachweis import OHNE_EINWIRKUNG
from opencivil.mauerwerk import scheibe
from opencivil.mauerwerk.lasten import abtragen
from opencivil.mauerwerk.modell import Oeffnung, Rechteck, Sturzart, Wandlast, pfeiler
from opencivil.mauerwerk.scheibe import anteile, antworten, koepfe, starr_ab
from opencivil.projekt import Projekt
from opencivil.projekt.mauerwerk import rechteck
from tests.test_mauerwerk import zeichnung
from tests.test_mauerwerk_nachweise import TUERE, WAND, mit_lasten, urteile

#: Kalksandstein im Verband, vollfugig: E_xd und G_d in N/m², die Dicke in m.
E_XD, G_D, T_W = 2975e6, 1190e6, 0.175


class TestScheibe(unittest.TestCase):
    """Das Gleichgewicht des starren Teils über den Öffnungen."""

    def test_zwei_gleiche_pfeiler(self):
        """
        Zwei Pfeiler, je 1 m breit und 2 m hoch, ihre Mitten 3 m auseinander,
        H = 100 kN auf 2 m. Je Pfeiler Φ = 12 · E · I · 1.2 / (G · A · h²) =
        0.75, k_uu = k_up = 37.19, k_pp = 58.88 und k_a = 260.3 MN. Aus dem
        Gleichgewicht Θ = −8.232e-5 und u = 1.427e-3 m am Kopf: je 50 kN
        Querkraft, am Kopf 48.21 kNm, am Fuss 100 − 48.21 = 51.79 kNm, und
        ±260.3 · 8.232e-5 · 1.5 = ±32.14 kN -- rechts gedrückt, links
        entlastet. Zusammen halten sie H · 2 m = 2 · 51.79 + 3 · 32.14 kNm.
        """
        wand = Rechteck(0, 0, 4, 2.7)
        tor = Oeffnung("O1", ((1, 0), (3, 0), (3, 2), (1, 2)), Sturzart.BETON, 0.2, 0.15)
        pf = pfeiler(wand, [tor])
        r = antworten(pf, koepfe(wand, [tor], pf), 0.0, [Wandlast("H", 2, 2, 2.0, 0, 0, 100e3)],
                      E_XD, G_D, T_W)
        (V1, N1, M1), (V2, N2, M2) = r["P1"], r["P2"]
        for V, N, M in ((V1, -N1, M1), (V2, N2, M2)):
            self.assertAlmostEqual(V, 50e3, delta=0.01)
            self.assertAlmostEqual(N, 32.143e3, delta=1)
            self.assertAlmostEqual(M, 51.786e3, delta=1)
        self.assertAlmostEqual(M1 + M2 + 1.5 * (N2 - N1), 200e3, delta=0.01)

    def test_ein_pfeiler_ist_ein_kragarm(self):
        """Ohne Öffnung trägt die ganze Wand als ein Pfeiler: V = H, M_z = H · y, kein N."""
        wand = Rechteck(0, 0, 3, 2.5)
        pf = pfeiler(wand, [])
        (V, N, M), = antworten(pf, koepfe(wand, [], pf), 0.0,
                               [Wandlast("H", 1, 1, 1.2, 0, 0, 10e3)], E_XD, G_D, T_W).values()
        self.assertAlmostEqual(V, 10e3, delta=1e-6)
        self.assertAlmostEqual(N, 0.0, delta=1e-6)
        self.assertAlmostEqual(M, 12e3, delta=1e-6)

    def test_starr_ueber_der_hoechsten_oeffnung(self):
        """Die Köpfe am oberen Rand der höchsten Öffnung neben dem Pfeiler -- sonst an der Krone."""
        fenster = Oeffnung("O2", ((4, 1), (5, 1), (5, 2.4), (4, 2.4)), Sturzart.BETON, 0.2, 0.15)
        self.assertEqual(starr_ab(WAND, [TUERE, fenster]), 2.4)
        self.assertEqual(starr_ab(WAND, []), 0.0)
        pf = pfeiler(WAND, [TUERE, fenster])
        self.assertEqual(koepfe(WAND, [TUERE, fenster], pf), {"P1": 2.1, "P2": 2.4, "P3": 2.4})
        self.assertEqual(koepfe(WAND, [], pfeiler(WAND, [])), {"P1": 2.7})

    def test_das_moment_der_lotrechten_lasten(self):
        """
        q = 10 kN/m auf der Krone, wie in TestLastabtrag: P1, Mitte bei 1 m,
        trägt 18.5 kN bei 0.925 m und 6.5 kN am Auflager bei 1.925 m, P2, Mitte
        bei 4.5 m, 28.5 kN bei 4.575 m und 6.5 kN bei 3.075 m. M_v = −1.39 +
        6.01 + 2.14 − 9.26 = −2.5 kNm; die Pfeiler, 2 und 3 m breit, bekommen
        davon 8/35 und 27/35 -- ohne waagrechte Last keine Querkraft.
        """
        pf = pfeiler(WAND, [TUERE])
        a = abtragen(WAND, [TUERE], pf, [Wandlast("q", 0, 6, 2.7, 60e3)], 0.0)
        self.assertAlmostEqual(a.M_v, -2.5e3)
        self.assertEqual(anteile(pf), {"P1": 8 / 35, "P2": 27 / 35})
        scheibe.abtragen(a, WAND, [TUERE], pf, [], E_XD, G_D, T_W)
        self.assertAlmostEqual(a.M_z["P1"], -2.5e3 * 8 / 35)
        self.assertAlmostEqual(a.M_z["P2"], -2.5e3 * 27 / 35)
        self.assertEqual(a.V, {"P1": 0.0, "P2": 0.0})

    def test_eine_punktlast_neben_der_mitte(self):
        """10 kN bei 0.4 m auf P1, dessen Mitte bei 1 m liegt: M_v = 10 · (0.4 − 1) = −6 kNm."""
        a = abtragen(WAND, [TUERE], pfeiler(WAND, [TUERE]), [Wandlast("Q", 0.4, 0.4, 2.7, 10e3)],
                     0.0)
        self.assertAlmostEqual(a.M_v, -6e3)


def wand_mit_wind(p, e=0.0, H=100.0):
    """
    Eine Wand ohne Öffnung, 6 × 2.7 m, aus Kalksandstein im Verband und
    vollfugig, 175 mm dick, am Fuss eingespannt: 40 kN/m Auflast mit der
    Ausmitte ``e`` in mm und ``H`` in kN an der Krone -- in «GZT Wind» mit
    1.0 · Eigengewicht + 1.0 · Auflast + 1.5 · Wind.
    """
    p.mauerwerk("MK")
    w = p.wand("Wand", t=175, mauerung="verband", stossfugen="vollfugig", fuss="eingespannt")
    w.wand(rechteck(0, 0, 6, 2.7))
    w.standardfaelle()
    eigengewicht, auflast, _ = w.lastfaelle
    w.linienlast(auflast, (0, 2.7), (6, 2.7), wert=40, e=e)
    wind = w.lastfall("Wind")
    w.kombination("GZT Wind", (eigengewicht, 1.0), (auflast, 1.0), (wind, 1.5))
    w.punktlast(wind, (6, 2.7), wert=0, H=H)
    return w


#: Die Wand mit Wind im GZT: N = 3.15 kN/m² · 16.2 m² + 40 kN/m · 6 m, V = 1.5 · 100 kN und
#: M_z = V · 2.7 m -- in N und N·m.
N_WIND, V_WIND = 3.15e3 * 16.2 + 240e3, 150e3
M_WIND = V_WIND * 2.7
#: Die gedrückte Länge dazu, l_2 = l_w − 2 · M_z / N = 3.217 m (Gl. (13) und (17)).
L_2 = 6.0 - 2.0 * M_WIND / N_WIND


class TestSchubUndGleiten(unittest.TestCase):
    """Die Druckstrebe nach Gl. (13), das Gleiten nach Gl. (14) -- am Fuss des Pfeilers."""

    def test_die_druckstrebe(self):
        """
        tan α = 150 / 291.03, cos² α = 0.7901; mittig trägt die ganze Dicke:
        N_Rd = 1.36 N/mm² · 3217 mm · 175 mm · 0.7901 = 604.9 kN.
        """
        p = Projekt(name="Probe")
        u = urteile(p, wand_mit_wind(p))["Schub – P1 – GZT Wind"]
        self.assertAlmostEqual(u.einwirkung.groesse.si, N_WIND, delta=1)
        cos2 = 1.0 / (1.0 + (V_WIND / N_WIND) ** 2)
        self.assertAlmostEqual(u.widerstand.groesse.si, 1.36e6 * L_2 * T_W * cos2, delta=5)
        self.assertAlmostEqual(u.widerstand.groesse.si, 604.9e3, delta=100)
        self.assertTrue(u.erfuellt)

    def test_das_gleiten(self):
        """V_Rd = μ_d · N_xd = 0.6 · 291.03 = 174.6 kN gegen V_d = 150 kN."""
        p = Projekt(name="Probe")
        u = urteile(p, wand_mit_wind(p))["Gleiten – P1 – GZT Wind"]
        self.assertAlmostEqual(u.einwirkung.groesse.si, V_WIND, delta=1)
        self.assertAlmostEqual(u.widerstand.groesse.si, 0.6 * N_WIND, delta=1)
        self.assertTrue(u.erfuellt)

    def test_ausmittig_eine_duennere_strebe(self):
        """Mit 20 mm Ausmitte am Kopf trägt höchstens t_w − 2 · 20 mm, mindestens 0.25 · t_w."""
        p = Projekt(name="Probe")
        u = urteile(p, wand_mit_wind(p, e=20))["Schub – P1 – GZT Wind"]
        cos2 = 1.0 / (1.0 + (V_WIND / N_WIND) ** 2)
        t_nom = u.widerstand.groesse.si / (1.36e6 * L_2 * cos2)
        self.assertLessEqual(t_nom, T_W - 0.040 + 1e-9)
        self.assertGreaterEqual(t_nom, 0.25 * T_W)

    def test_zu_viel_moment(self):
        """H = 400 kN: l_2 = 6 − 2 · 1620 / 291.03 m < 0 -- nichts trägt, und es gleitet."""
        p = Projekt(name="Probe")
        u = urteile(p, wand_mit_wind(p, H=400))
        self.assertEqual(u["Schub – P1 – GZT Wind"].widerstand.groesse.si, 0.0)
        self.assertTrue(u["Schub – P1 – GZT Wind"].verfehlt)
        self.assertTrue(u["Gleiten – P1 – GZT Wind"].verfehlt)

    def test_nur_wo_eine_last_schiebt(self):
        """Im GZT ohne Wind kein Schub und kein Gleiten -- die Normalkraft schon."""
        p = Projekt(name="Probe")
        u = urteile(p, wand_mit_wind(p))
        self.assertIn("Normalkraft – P1 – GZT", u)
        self.assertNotIn("Schub – P1 – GZT", u)
        self.assertNotIn("Gleiten – P1 – GZT", u)

    def test_ohne_querkraft_kein_nachweis(self):
        """Zwei gleiche Lasten gegeneinander: «Keine Einwirkung → kein Nachweis.»"""
        p = Projekt(name="Probe")
        w = wand_mit_wind(p)
        w.punktlast(w.lastfaelle[3], (0, 2.7), wert=0, H=-100)
        u = urteile(p, w)
        for name in ("Schub – P1 – GZT Wind", "Gleiten – P1 – GZT Wind"):
            with self.subTest(name=name):
                self.assertEqual(u[name].begruendung, OHNE_EINWIRKUNG)

    def test_ein_pfeiler_ohne_druck(self):
        """Nur Wind, ohne lotrechte Last: grau, nicht rot -- ohne Druck kein Schub."""
        p = Projekt(name="Probe")
        w = wand_mit_wind(p)
        w.kombination("Nur Wind", (w.lastfaelle[3], 1.5))
        u = urteile(p, w)["Schub – P1 – Nur Wind"]
        self.assertTrue(u.offen)
        self.assertFalse(u.verfehlt)
        self.assertIn("Der Pfeiler P1 ist nicht gedrückt", u.begruendung)

    def test_ohne_waagrechte_last_weder_schub_noch_gleiten(self):
        p = Projekt(name="Probe")
        p.mauerwerk("MK")
        namen = urteile(p, mit_lasten(p))
        self.assertTrue(namen)
        self.assertFalse([n for n in namen if n.startswith(("Schub", "Gleiten"))])


class TestNormalkraftUnterSchub(unittest.TestCase):
    """Gl. (17): steht die Normalkraft quer zur Wand ausmittig, trägt nur die gedrückte Länge."""

    def widerstand(self, e, H):
        p = Projekt(name="Probe")
        return urteile(p, wand_mit_wind(p, e=e, H=H))["Normalkraft – P1 – GZT Wind"].widerstand

    def test_ausmittig_mit_der_gedrueckten_laenge(self):
        """
        k_N hängt nicht von der Länge ab: N_xRd schrumpft mit l_2 / l_w = 3.217 / 6
        -- bis auf die Toleranz, mit der k_N gesucht wird.
        """
        mit, ohne = self.widerstand(20, 100), self.widerstand(20, 0)
        self.assertAlmostEqual(mit.groesse.si / ohne.groesse.si, L_2 / 6.0, delta=1e-4)

    def test_mittig_bleibt_gl_11(self):
        """Ohne Ausmitte quer zur Wand die ganze Länge: k_N = 1, N_xRd = 6 · 0.175 · 2975 kN."""
        self.assertAlmostEqual(self.widerstand(0, 100).groesse.si, 6 * T_W * 2975e3, delta=1)


class TestWaagrechteLastenPruefen(unittest.TestCase):

    def test_unter_der_hoechsten_oeffnung_rot(self):
        """Zwischen den Öffnungen hält die Wand nicht zusammen: dort rechnet das Werkzeug kein H."""
        p = Projekt(name="Probe")
        p.mauerwerk("MK")
        w = mit_lasten(p)
        w.punktlast(w.lastfaelle[1], (0.4, 1.0), wert=0, H=10)
        self.assertEqual([(m["text"], m["fehler"]) for m in zeichnung(p, w)["meldungen"]],
                         [("Die Last PL1 schiebt waagrecht tiefer als der obere Rand der Öffnung "
                           "O1 – das Werkzeug rechnet waagrechte Lasten nur über den Öffnungen, "
                           "wo die Wand zusammenhält, etwa an der Decke.", True)])

    def test_an_der_krone_keine_meldung(self):
        p = Projekt(name="Probe")
        p.mauerwerk("MK")
        w = mit_lasten(p)
        w.punktlast(w.lastfaelle[1], (6, 2.7), wert=0, H=10)
        self.assertEqual(zeichnung(p, w)["meldungen"], [])


if __name__ == "__main__":
    unittest.main()
