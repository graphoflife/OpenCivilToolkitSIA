"""
Tests fuer die Verbundstuetze nach SIA 264:2014, 5.3 (Plan vom 2026-11-25,
Schritt 14c): die Art nach Tabelle 7, was 5.3.1 und 5.3.2 vom Querschnitt
verlangen, das Knicken nach (15), die Biegung nach Theorie 2. Ordnung mit
(24) und (25) und die zweiachsige Biegung.

Von Hand, ein HEB 300 aus S355, ganz einbetoniert in 500 × 500 mm aus
C30/37, mit vier ⌀20 aus B500B bei y, z = ±200 mm -- Flaeche und
Traegheitsmomente des Profils aus dem Umriss des Werkzeugs, ein Stab als
Quadrat seiner Flaeche, der Beton ohne beide:

* (14) A_a 355/1.05 + A_c 0.85 · 30/1.5 + A_s 500/1.15; (16) dasselbe mit
  γ = 1; (13) δ = A_a f_yd/N_pl,Rd.
* (19) E_c,eff = E_cm/(1 + 0.6 · 2), E_cm = 10000 · 38^(1/3) nach SIA 262,
  (10).
* (17) E_a I_a + 0.6 E_c,eff I_c + E_s I_s, (20) π² EI/L_K², (16) λ̄, χ nach
  SIA 263, (8): um y Kurve b, um z c (Tabelle 7); (15) χ N_pl,Rd.
* (22) 0.9 (E_a I_a + 0.5 E_c,eff I_c + E_s I_s), (23) mit der Laenge der
  Stuetze, (24) k = max(1, ω k_0) mit k_0 = 1/(1 - |N|/N_cr,eff), e_0 = L/200
  um y: M_II = k |M| + k_0 |N| e_0; (25) 0.9 μ_d M_pl,Rd/M_II.
* Rechteckige Spannungsbloecke einer doppelsymmetrischen Stuetze: bei
  N = -0.85 f_cd A_c traegt sie dasselbe Moment wie ohne Normalkraft, bei
  der Haelfte das groesste, f_yd W_pl,a + f_sd W_pl,s + 0.85 f_cd W_pl,c/2
  -- W_pl,a aus dem Biegewiderstand des Profils allein.
"""

import math
import unittest

from opencivil.core.nachweis import OHNE_EINWIRKUNG
from opencivil.material.basis import Baustoffart
from opencivil.nachweis.qa_verbund_kennzahlen import verbund_von
from opencivil.nachweis.qa_verbund_stuetze import NICHT_GEDRUECKT
from opencivil.projekt import Projekt
from opencivil.projekt.lesen import ProjektFehler, feldangaben
from opencivil.projekt.stabilitaet import QAStabilitaetEintrag
from opencivil.querschnitt.vorlagen import kreispunkte
from opencivil.stahlbau import stabilitaet as st
from opencivil.stahlprofile.lage import Profillage
from opencivil.verbund import stuetze as vs
from tests.test_stahl_stabilitaet import chi, texte
from tests.test_stahlbau import rechteck
from tests.test_stahlprofile_qa import analyse, meldungen, projekt, zeichnung
from tests.test_verbund import stahl_allein

#: Die Festigkeiten in N/mm², mit der Wahl der Tragsicherheit und mit γ = 1.
F_A, F_A_K = 355.0 / 1.05, 355.0
F_C, F_C_K = 0.85 * 30.0 / 1.5, 0.85 * 30.0
F_S, F_S_K = 500.0 / 1.15, 500.0

#: Die Elastizitaetsmoduln in N/mm² -- E_cm von C30/37 nach SIA 262, (10).
E_A, E_S = 210000.0, 200000.0
E_CM = 10000.0 * 38.0 ** (1.0 / 3.0)

EPS = math.sqrt(235.0 / 355.0)

#: Ein ⌀20, in mm².
STAB = math.pi * 10.0 ** 2

HEB = (0, 0, "HEB 300", {})
BLOCK = (rechteck(-250, -250, 500, 500), "b1")
ECKEN = ((200, 200), (-200, 200), (200, -200), (-200, -200))

#: Das gefuellte Rohr: ROR 219.1 x 8, innen mit Beton.
ROHR = (0, 0, "ROR 219.1 x 8", {})
ROHRBETON = (kreispunkte((0.0, 0.0), 101.55), "b1")



def fuellung(name):
    """Beton, der das Rohr ``name`` um (0, 0) fuellt: sein Loch, ein Tausendstel kleiner."""
    _, loch = Profillage(name, (0.0, 0.0), 0, False).umrisse
    return [(0.999 * y, 0.999 * z) for y, z in loch], "b1"


#: Die Werte eines Falls wie im Pruefprojekt, in m und %.
STUETZE = {"L_K_y": 6.0, "L_K_z": 6.0, "L": 6.0, "staendig": 60.0}

#: So weit darf die Rechnung von der Hand abweichen -- beide mit denselben Kennwerten.
GENAU = 1e-9

#: So weit die plastische Nulllinie, die das Werkzeug sucht.
PLASTISCH = 1e-6


def bauen(*profile, polygone=(BLOCK,), staebe=ECKEN, durchmesser=20, stahl=None):
    """Projekt und Analyse -- je (y, z) ein Stab aus B500B, ``stahl`` die Sorte der Profile."""
    p = projekt()
    if stahl:
        p.baustahl(stahl)
    a = analyse(p, *(profile or (HEB,)), polygone=polygone)
    if stahl:
        for profil in a.profile:
            profil.stahl = "st2"
    for y, z in staebe:
        a.stab(y, z, durchmesser=durchmesser, stahl="s1")
    return p, a


def verbund(*profile, **kw):
    p, a = bauen(*profile, **kw)
    return verbund_von(p.aufbauen().teile[a.kennung].objekt)


def stuetze(*profile, beton=0.85, **kw):
    """Die Stuetze mit den Festigkeiten von Hand -- ``beton`` der Faktor vor f_cd und f_ck."""
    v = verbund(*profile, **kw)
    je_art = {Baustoffart.BAUSTAHL: (F_A, F_A, F_A_K, E_A),
              Baustoffart.BETON: (0.0, beton * 30.0 / 1.5, beton * 30.0, E_CM),
              Baustoffart.BETONSTAHL: (F_S, F_S, F_S_K, E_S)}
    zug, druck, druck_k, E = zip(*(je_art[v.art(g)] for g in range(len(v.gruppen))))
    art, _ = vs.querschnittsart(v)
    return vs.Stuetze(v, art, vs.Festigkeiten(zug, druck, druck_k, E), eps=EPS, hochfest=False)


def rechnen(s, N_Ed=0.0, M_y_Ed=0.0, M_z_Ed=0.0, kriechzahl=2.0, **werte):
    """Ein Fall der Stuetze ``s`` mit den Feldern der Oberflaeche: kN, kNm, m und %."""
    werte = {**STUETZE, **werte}
    werte["staendig"] /= 100.0
    fall = st.Stabfall("Fall", N=N_Ed * 1e3, M_y=M_y_Ed * 1e3, M_z=M_z_Ed * 1e3, **werte)
    return vs.rechnen(s, fall, kriechzahl, {"y": M_y_Ed * 1e6, "z": M_z_Ed * 1e6})


def nachweise(*profile, faelle, kriechzahl=2.0, einachsig=False, **kw):
    """Die Urteile je Fall durch das ganze Projekt, dazu die Loesung."""
    p, a = bauen(*profile, **kw)
    a.einachsig = einachsig
    a.stuetze_kriechzahl = kriechzahl
    for name, werte in faelle.items():
        a.stabilitaetsfall(name, **werte)
    aufbau = p.aufbauen()
    loesung = aufbau.werk.loese(*aufbau.teile[a.kennung].ziele())
    return {u.fall: u for u in loesung.urteile if u.art == "Stab"}, loesung


class Hand:
    """Die Stuetze des Dateikopfs von Hand, in N und mm."""

    def __init__(self, s, staendig=0.6, kriechzahl=2.0):
        profil = s.der_art(Baustoffart.BAUSTAHL)[0]
        self.A_a, self.I_a = profil.A, {"y": profil.I_y, "z": profil.I_z}
        self.A_s = 4.0 * STAB
        self.I_s = 4.0 * (STAB * 200.0 ** 2 + STAB ** 2 / 12.0)
        self.A_c = 500.0 ** 2 - self.A_a - self.A_s
        self.I_c = {a: 500.0 ** 4 / 12.0 - self.I_a[a] - self.I_s for a in "yz"}
        self.N_pl_Rd = self.A_a * F_A + self.A_c * F_C + self.A_s * F_S
        self.N_pl_Rk = self.A_a * F_A_K + self.A_c * F_C_K + self.A_s * F_S_K
        self.E_c = E_CM / (1.0 + staendig * kriechzahl)

    def EI(self, a, beton):
        return E_A * self.I_a[a] + beton * self.E_c * self.I_c[a] + E_S * self.I_s

    def N_K(self, a, L_K):
        """(15) um ``a`` mit der Knicklaenge in mm."""
        lam = math.sqrt(self.N_pl_Rk * L_K ** 2 / (math.pi ** 2 * self.EI(a, 0.6)))
        return chi(lam, 0.34 if a == "y" else 0.49, 0.2) * self.N_pl_Rd

    def M_II(self, a, N, M, L, psi=1.0):
        """Das Moment 2. Ordnung um ``a`` -- ``N`` in N, ``M`` in N mm als Betraege, ``L`` in mm."""
        N_cr = math.pi ** 2 * 0.9 * self.EI(a, 0.5) / L ** 2
        k_0 = 1.0 / (1.0 - N / N_cr)
        k = max(1.0, max(0.4, 0.6 + 0.4 * psi) * k_0)
        return k * M + k_0 * N * L / (200.0 if a == "y" else 150.0)


class TestArt(unittest.TestCase):
    """Tabelle 7 -- die Art liest das Werkzeug an der Zeichnung."""

    def test_ganz_einbetoniert(self):
        self.assertEqual(vs.querschnittsart(verbund()), (vs.Art.EINBETONIERT, ""))

    def test_kammerbetoniert(self):
        """Beton im umschreibenden Rechteck: das Profil verdraengt ihn, er bleibt in den Kammern."""
        v = verbund(polygone=[(rechteck(-150, -150, 300, 300), "b1")], staebe=())
        self.assertEqual(vs.querschnittsart(v), (vs.Art.KAMMERBETONIERT, ""))

    def test_gefuellte_rohre(self):
        for profil in (ROHR, (0, 0, "RRK 200 x 200 x 10", {})):
            with self.subTest(profil=profil[2]):
                v = verbund(profil, polygone=[fuellung(profil[2])], staebe=())
                self.assertEqual(vs.querschnittsart(v), (vs.Art.ROHR, ""))

    def test_ein_leeres_rohr_sagt_es(self):
        """Das Rohr im Beton, innen leer: das Loch liegt im Rohr, nicht im Beton."""
        v = verbund(ROHR, polygone=[(rechteck(-150, -150, 300, 300), "b1")], staebe=())
        self.assertEqual(vs.querschnittsart(v),
                         (None, vs.LEERES_ROHR.format(name="ROR 219.1 x 8")))

    def test_andere_kennt_tabelle_7_nicht(self):
        for was, profile, polygone in (
                ("Rohr mit Beton daneben", (ROHR,),
                 [(rechteck(-150, -150, 300, 300), "b1"), ROHRBETON]),
                ("zwei Profile", ((-200, 0, "HEB 300", {}), (200, 0, "HEB 300", {})),
                 [(rechteck(-400, -200, 800, 400), "b1")]),
                ("ein U", ((0, 0, "UPE 200", {}),), [BLOCK]),
                ("Träger unter einer Platte", ((0, 150, "IPE 300", {}),),
                 [(rechteck(-750, 300, 1500, 120), "b1")])):
            with self.subTest(was=was):
                self.assertEqual(vs.querschnittsart(verbund(*profile, polygone=polygone,
                                                            staebe=())),
                                 (None, vs.NICHT_IN_TABELLE))

    def test_beton_auf_der_wand_eines_rohrs(self):
        """
        Ein Kreis mit dem Aussendurchmesser liegt im Umriss des Rohrs und
        ersetzte seinen Stahl -- rot am Ort, statt still fast ohne Stahl zu
        rechnen.
        """
        p, a = bauen(ROHR, polygone=[(kreispunkte((0.0, 0.0), 109.55), "b1")], staebe=())
        self.assertEqual(meldungen(zeichnung(p, a)), [(
            "Polygon 1 liegt auf dem Stahl von Profil 1 und ersetzte ihn dort. Beton, der ein "
            "Rohr füllt, liegt ganz in seinem Loch.", True)])


class TestQuerschnitt(unittest.TestCase):
    """Flaechen, Traegheitsmomente, (14), (16), (13) und die Kurven -- siehe Dateikopf."""

    @classmethod
    def setUpClass(cls):
        cls.s = stuetze()
        cls.h = Hand(cls.s)

    def test_der_beton_ohne_profil_und_staebe(self):
        beton = self.s.der_art(Baustoffart.BETON)[0]
        stahl = self.s.der_art(Baustoffart.BETONSTAHL)[0]
        for ist, soll in ((beton.A, self.h.A_c), (beton.I_y, self.h.I_c["y"]),
                          (beton.I_z, self.h.I_c["z"]), (stahl.A, self.h.A_s),
                          (stahl.I_y, self.h.I_s), (stahl.I_z, self.h.I_s)):
            self.assertAlmostEqual(ist / soll, 1.0, delta=GENAU)

    def test_normalkraft_von_hand(self):
        self.assertAlmostEqual(self.s.N_pl() / self.h.N_pl_Rd, 1.0, delta=GENAU)
        self.assertAlmostEqual(self.s.N_pl(charakteristisch=True) / self.h.N_pl_Rk, 1.0,
                               delta=GENAU)
        self.assertAlmostEqual(self.s.delta, self.h.A_a * F_A / self.h.N_pl_Rd, delta=GENAU)
        self.assertEqual(self.s.fehlt, "")

    def test_kurven_der_tabelle_7(self):
        self.assertEqual(self.s.kurve("y")[:2], ("b", 200.0))
        self.assertEqual(self.s.kurve("z")[:2], ("c", 150.0))

    def test_gedreht_tauschen_die_kurven(self):
        s = stuetze((0, 0, "HEB 300", {"drehung": 90}))
        self.assertEqual((s.kurve("y")[0], s.kurve("z")[0]), ("c", "b"))


class TestRohr(unittest.TestCase):
    """Im gefuellten Rohr der Beton mit 1.0 (5.3.2.5), die Kurve nach ρ_s (Tabelle 7)."""

    def test_bis_3_prozent_kurve_a(self):
        s = stuetze(ROHR, polygone=[ROHRBETON], beton=1.0, durchmesser=16,
                    staebe=((60, 0), (-60, 0), (0, 60), (0, -60)))
        self.assertLess(s.rho_s, 0.03)
        self.assertEqual(s.kurve("y")[:2], ("a", 300.0))
        self.assertEqual(s.anteil_s, 1.0)

    def test_ueber_6_prozent_zaehlt_der_betonstahl_mit_6(self):
        """Acht ⌀20 auf r = 70 mm: ρ_s ueber 6 %, Kurve b und hoechstens 0.06 A_c f_sd (5.3.2.2)."""
        s = stuetze(ROHR, polygone=[ROHRBETON], beton=1.0, staebe=kreispunkte((0, 0), 70.0, 8))
        A_a = s.flaeche(Baustoffart.BAUSTAHL)
        A_c = s.flaeche(Baustoffart.BETON)
        self.assertAlmostEqual(s.rho_s, 8.0 * STAB / A_c, delta=GENAU)
        self.assertGreater(s.rho_s, 0.06)
        self.assertEqual(s.kurve("z")[:2], ("b", 200.0))
        self.assertAlmostEqual(s.N_pl() / (A_a * F_A + A_c * 20.0 + 0.06 * A_c * F_S), 1.0,
                               delta=GENAU)


class TestWasFehlt(unittest.TestCase):
    """Was 5.3.1 und 5.3.2 verlangen, der erste Grund -- am Querschnitt, nicht je Fall."""

    def test_unsymmetrisch(self):
        s = stuetze(staebe=((200, 200), (-200, 200)))
        self.assertIn("Doppelsymmetrisch muss die Stütze sein (5.3.2.1): der Schwerpunkt von "
                      "«B500B» liegt 200.0 mm neben der Mitte des Profils.", s.fehlt)

    def test_h_zu_b(self):
        s = stuetze(polygone=[(rechteck(-850, -160, 1700, 320), "b1")], staebe=())
        self.assertEqual(s.fehlt, "h/b = 320/1700 = 0.19 liegt nicht zwischen 0.2 und 5 "
                                  "(5.3.2.3).")

    def test_tabelle_6(self):
        """RRK 350 x 250 x 6 aus S355: h/t = 58.3 über 52 ε = 42.3."""
        s = stuetze((0, 0, "RRK 350 x 250 x 6", {}), polygone=[fuellung("RRK 350 x 250 x 6")],
                    staebe=())
        self.assertIs(s.art, vs.Art.ROHR)
        self.assertTrue(s.fehlt.startswith("h/t = 58.3 über 42.3 nach Tabelle 6"), s.fehlt)

    def test_zu_wenig_stahl(self):
        s = stuetze((0, 0, "HEB 100", {}), polygone=[(rechteck(-300, -300, 600, 600), "b1")],
                    staebe=())
        self.assertLess(s.delta, 0.2)
        self.assertIn("als Stahlbetonstütze nachweisen (5.3.1.2)", s.fehlt)


class TestPlastisch(unittest.TestCase):
    """Rechteckige Spannungsbloecke (Figur 7) -- siehe Dateikopf."""

    @classmethod
    def setUpClass(cls):
        cls.s = stuetze()
        cls.h = Hand(cls.s)
        k = stahl_allein(HEB)
        cls.W_a = {"y": k["M_Rd_unten"] * 1e6 / F_A, "z": k["M_Rd_links"] * 1e6 / F_A}

    def test_bei_der_druckkraft_des_betons_wie_ohne(self):
        for a in "yz":
            with self.subTest(achse=a):
                M_0, _ = self.s.M_pl(a, 1.0, 0.0)
                M_C, _ = self.s.M_pl(a, 1.0, -F_C * self.h.A_c)
                self.assertAlmostEqual(M_C / M_0, 1.0, delta=PLASTISCH)

    def test_bei_der_haelfte_das_groesste(self):
        W_s = 4.0 * STAB * 200.0
        for a in "yz":
            with self.subTest(achse=a):
                W_c = 500.0 ** 3 / 4.0 - self.W_a[a] - W_s
                M, lage = self.s.M_pl(a, 1.0, -0.5 * F_C * self.h.A_c)
                self.assertAlmostEqual(M / (F_A * self.W_a[a] + F_S * W_s + 0.5 * F_C * W_c),
                                       1.0, delta=PLASTISCH)
                self.assertAlmostEqual(lage, 0.0, delta=1e-3)

    def test_ueber_n_pl_traegt_er_nichts(self):
        self.assertGreater(self.s.M_pl("y", 1.0, -0.999 * self.h.N_pl_Rd)[0], 0.0)
        self.assertEqual(self.s.M_pl("y", 1.0, -1.001 * self.h.N_pl_Rd), (0.0, None))


class TestFall(unittest.TestCase):
    """Je Fall von Hand -- die Stuetze des Dateikopfs, 6 m lang, 60 % staendig, φ = 2."""

    @classmethod
    def setUpClass(cls):
        cls.s = stuetze()
        cls.h = Hand(cls.s)

    def widerstand(self, a, N):
        """``μ_d M_pl,Rd`` um ``a`` bei ``N`` in N, aus den Spannungsbloecken."""
        M_pl, _ = self.s.M_pl(a, 1.0, 0.0)
        return min(1.0, self.s.M_pl(a, 1.0, N)[0] / M_pl) * M_pl

    def test_einachsig(self):
        x = rechnen(self.s, -6000.0, M_y_Ed=200.0)
        self.assertEqual(list(x.knicken), ["z"])
        self.assertAlmostEqual(x.knicken["z"].N_K_Rd / self.h.N_K("z", 6000.0), 1.0, delta=GENAU)
        M_II = self.h.M_II("y", 6e6, 200e6, 6000.0)
        self.assertAlmostEqual(x.biegung["y"].M_II / M_II, 1.0, delta=GENAU)
        name, grad = x.massgebend
        self.assertEqual(name, "(25) um y")
        self.assertAlmostEqual(grad, 0.9 * self.widerstand("y", -6e6) / M_II, delta=GENAU)
        self.assertEqual(x.fehlt, "")

    def test_zweiachsig_linear(self):
        """ψ_y = 0.5: ω = 0.8, k_y = max(1; 0.8 k_0); beide Achsen mit Imperfektion."""
        x = rechnen(self.s, -4000.0, M_y_Ed=150.0, M_z_Ed=60.0, psi_y=0.5)
        self.assertEqual(x.knicken, {})
        summe = sum(self.h.M_II(a, 4e6, M * 1e6, 6000.0, psi) / self.widerstand(a, -4e6)
                    for a, M, psi in (("y", 150.0, 0.5), ("z", 60.0, 1.0)))
        self.assertEqual(x.massgebend[0], "(25) zweiachsig")
        self.assertAlmostEqual(x.massgebend[1], 0.9 / summe, delta=GENAU)

    def test_zentrisch(self):
        x = rechnen(self.s, -5000.0, L_K_z=4.0)
        self.assertEqual(x.biegung, {})
        grade = dict(x.grade)
        self.assertAlmostEqual(grade["(15) um y"], self.h.N_K("y", 6000.0) / 5e6, delta=GENAU)
        self.assertAlmostEqual(grade["(15) um z"], self.h.N_K("z", 4000.0) / 5e6, delta=GENAU)

    def test_gehalten(self):
        """L_K,y = 0: um y knickt nichts, das Moment waechst nicht, keine Imperfektion."""
        x = rechnen(self.s, -5000.0, M_y_Ed=100.0, L_K_y=0.0)
        b = x.biegung["y"]
        self.assertTrue(b.gehalten)
        self.assertEqual((b.k, b.e_0, b.M_II), (1.0, 0.0, 100e6))
        self.assertEqual(x.massgebend[0], "(15) um z")

    def test_ohne_kriechen(self):
        x = rechnen(self.s, -5000.0, kriechzahl=0.0)
        self.assertEqual(list(x.E_c.values()), [E_CM])

    def test_knickt_aus(self):
        """L = 12 m: N_cr,eff um y liegt unter 9000 kN -- rot, N_cr,eff/|N_Ed|."""
        x = rechnen(self.s, -9000.0, M_y_Ed=100.0, L_K_y=12.0, L_K_z=1.0, L=12.0)
        b = x.biegung["y"]
        self.assertTrue(b.knickt_aus)
        N_cr = math.pi ** 2 * 0.9 * self.h.EI("y", 0.5) / 12000.0 ** 2
        self.assertEqual(x.massgebend[0], "(24) um y: N_Ed erreicht N_cr,eff")
        self.assertAlmostEqual(x.massgebend[1], N_cr / 9e6, delta=GENAU)
        self.assertLess(x.massgebend[1], 1.0)

    def test_knicklaenge_laenger_als_die_stuetze(self):
        """Nur um eine Achse mit Moment: (24) gilt fuer die unverschiebliche Stuetze."""
        x = rechnen(self.s, -3000.0, M_y_Ed=100.0, L_K_y=8.0)
        self.assertEqual(x.fehlt, "Die Knicklänge L_K,y = 8.00 m ist länger als die Stütze, "
                                  "L = 6.00 m: unverschieblich gehalten, wie (24) es verlangt, "
                                  "ist sie höchstens so lang (5.3.4.1). Die Länge der Stütze "
                                  "angeben.")
        self.assertEqual(rechnen(self.s, -3000.0, M_y_Ed=100.0, L_K_z=8.0).fehlt, "")

    def test_zu_schlank(self):
        x = rechnen(self.s, -500.0, L_K_y=30.0, L_K_z=30.0, L=30.0)
        lam = math.sqrt(self.h.N_pl_Rk * 30000.0 ** 2 / (math.pi ** 2 * self.h.EI("y", 0.6)))
        self.assertEqual(x.fehlt, f"λ̄_y = {lam:.2f} liegt über 2: dort endet das vereinfachte "
                                  f"Verfahren der Norm (5.3.2.1), ein anderes rechnet das "
                                  f"Werkzeug nicht.")


class TestImProjekt(unittest.TestCase):
    """Der Nachweis rechnet wie die Stuetze von Hand -- mit den Kennwerten der Materialien."""

    def test_wie_von_hand(self):
        s = stuetze()
        faelle = {"Einachsig": {"N_Ed": -6000.0, "M_y_Ed": 200.0},
                  "Zweiachsig": {"N_Ed": -4000.0, "M_y_Ed": 150.0, "M_z_Ed": 60.0, "psi_y": 0.5},
                  "Zentrisch": {"N_Ed": -5000.0, "L_K_z": 4.0},
                  "Um y gehalten": {"N_Ed": -5000.0, "M_y_Ed": 100.0, "L_K_y": 0.0}}
        urteile, _ = nachweise(faelle={n: {**STUETZE, **w} for n, w in faelle.items()})
        for name, werte in faelle.items():
            with self.subTest(fall=name):
                was, grad = rechnen(s, **werte).massgebend
                u = urteile[name]
                self.assertTrue(u.erfuellt)
                self.assertAlmostEqual(u.erfuellungsgrad.si / grad, 1.0, delta=GENAU)
                self.assertEqual(u.begruendung, f"{was}, bei N_Ed = {werte['N_Ed']:.1f} kN.")

    def test_gehalten_und_zentrisch_ganz_von_hand(self):
        h = Hand(stuetze())
        urteile, _ = nachweise(faelle={
            "Gehalten": {**STUETZE, "N_Ed": -5000.0, "M_y_Ed": 100.0, "L_K_y": 0.0},
            "Zentrisch": {**STUETZE, "N_Ed": -5000.0, "L_K_z": 4.0}})
        self.assertAlmostEqual(urteile["Gehalten"].erfuellungsgrad.si,
                               h.N_K("z", 6000.0) / 5e6, delta=GENAU)
        self.assertAlmostEqual(urteile["Zentrisch"].erfuellungsgrad.si,
                               min(h.N_K("y", 6000.0), h.N_K("z", 4000.0)) / 5e6, delta=GENAU)

    def test_einachsig_zaehlt_m_z_nicht(self):
        werte = {**STUETZE, "N_Ed": -4000.0, "M_y_Ed": 150.0}
        einachsig, _ = nachweise(einachsig=True, faelle={"E": {**werte, "M_z_Ed": 60.0}})
        ohne, _ = nachweise(faelle={"E": werte})
        self.assertAlmostEqual(einachsig["E"].erfuellungsgrad.si, ohne["E"].erfuellungsgrad.si)

    def test_ohne_druck(self):
        """Ohne Druck ist es kein Fall der Stuetze: ∞, und der Satz sagt warum."""
        urteile, _ = nachweise(faelle={"Biegung": {**STUETZE, "M_y_Ed": 100.0},
                                       "Leer": dict(STUETZE)})
        self.assertEqual(urteile["Biegung"].hinweis, NICHT_GEDRUECKT)
        self.assertEqual(urteile["Leer"].hinweis, OHNE_EINWIRKUNG)
        for u in urteile.values():
            self.assertTrue(math.isinf(u.erfuellungsgrad.si))

    def test_was_fehlt_steht_grau_am_fall(self):
        urteile, loesung = nachweise(faelle={
            "Lang": {**STUETZE, "N_Ed": -3000.0, "M_y_Ed": 100.0, "L_K_y": 8.0},
            "Gut": {**STUETZE, "N_Ed": -3000.0}})
        u = urteile["Lang"]
        self.assertFalse(u.erfuellt)
        self.assertTrue(u.hinweis.startswith("Die Knicklänge L_K,y = 8.00 m ist länger"))
        self.assertIn(u.hinweis, texte(loesung))
        self.assertTrue(urteile["Gut"].erfuellt)

    def test_am_querschnitt_grau_fuer_jeden_fall(self):
        urteile, _ = nachweise((0, 150, "IPE 300", {}), staebe=(),
                               polygone=[(rechteck(-750, 300, 1500, 120), "b1")],
                               faelle={"A": {**STUETZE, "N_Ed": -1000.0},
                                       "B": {**STUETZE, "N_Ed": -500.0, "M_y_Ed": 50.0}})
        for u in urteile.values():
            self.assertEqual((u.erfuellt, u.hinweis), (False, vs.NICHT_IN_TABELLE))

    def test_rohr_mit_1_0(self):
        """Zentrisch, Kurve a: χ N_pl,Rd mit dem Beton 1.0 f_cd, ohne Kriechen."""
        staebe = ((60, 0), (-60, 0), (0, 60), (0, -60))
        s = stuetze(ROHR, polygone=[ROHRBETON], beton=1.0, durchmesser=16, staebe=staebe)
        urteile, loesung = nachweise(ROHR, polygone=[ROHRBETON], durchmesser=16, staebe=staebe,
                                     kriechzahl=0.0, faelle={"Druck": {
                                         **STUETZE, "N_Ed": -1500.0, "L_K_y": 3.5,
                                         "L_K_z": 3.5, "L": 3.5}})
        E = {Baustoffart.BAUSTAHL: E_A, Baustoffart.BETON: 0.6 * E_CM, Baustoffart.BETONSTAHL: E_S}
        N_K = []
        for a in "yz":
            EI = sum(E[w.art] * w.I(a) for w in s.werkstoffe)
            lam = math.sqrt(s.N_pl(charakteristisch=True) * 3500.0 ** 2 / (math.pi ** 2 * EI))
            N_K.append(chi(lam, 0.21, 0.2) * s.N_pl())
        self.assertAlmostEqual(urteile["Druck"].erfuellungsgrad.si, min(N_K) / 1.5e6,
                               delta=GENAU)
        self.assertIn("der Beton im gefüllten Rohr mit 1.0", texte(loesung))

    def test_s460_mit_0_8(self):
        _, loesung = nachweise(stahl="S460", faelle={
            "E": {**STUETZE, "N_Ed": -6000.0, "M_y_Ed": 200.0}})
        self.assertIn("Widerstand um y nach (25), S420 oder S460: 0.8", texte(loesung))


class TestEintrag(unittest.TestCase):
    """Die Felder, die nur der Verbund braucht: der staendige Anteil und die Laenge der Stuetze."""

    def test_felder(self):
        felder = feldangaben(QAStabilitaetEintrag)
        self.assertEqual((felder["staendig"]["einheit"], felder["staendig"]["ab"],
                          felder["staendig"]["bis"]), ("%", 0.0, 100.0))
        self.assertEqual((felder["L"]["einheit"], felder["L"]["ab"]), ("m", 0.0))

    def test_grenzen(self):
        for werte, heisst in (({"staendig": 120.0}, "Ständiger Anteil"),
                              ({"L": -1.0}, "Stützenlänge L")):
            with self.subTest(werte=werte):
                p, a = bauen()
                a.stabilitaetsfall("Falsch", **werte)
                with self.assertRaisesRegex(ProjektFehler,
                                            f"Stabilitätsnachweis 'Falsch': .*{heisst}"):
                    p.inhalt_pruefen()

    def test_speichern_und_laden(self):
        p, a = bauen()
        a.stuetze_kriechzahl = 2.5
        a.stabilitaetsfall("Feld", N_Ed=-500, M_y_Ed=80, L_K_y=6, L_K_z=3, L=6, staendig=40)
        wieder = Projekt.aus_dict(p.als_dict()).querschnittsanalysen[0]
        self.assertEqual(wieder.stuetze_kriechzahl, 2.5)
        self.assertEqual(wieder.stabfaelle()[0],
                         st.Stabfall("Feld", N=-500e3, M_y=80e3, L_K_y=6.0, L_K_z=3.0, L_D=3.0,
                                     L=6.0, staendig=0.4))


if __name__ == "__main__":
    unittest.main()
