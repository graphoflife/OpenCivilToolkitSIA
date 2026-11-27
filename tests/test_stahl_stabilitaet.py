"""
Tests fuer Knicken und Kippen eines Stahlstabs nach SIA 263:2013 (Plan vom
2026-11-25, Schritte 12c und 12d).

Von Hand, S355 mit f_y = 355 N/mm², γ_M1 = 1.05, E = 210 000 N/mm² und
G = 81 000 N/mm²; Flaeche und Traegheitsmomente aus dem Umriss des
Werkzeugs, I_T aus seiner Torsion:

* HEB 300 unter Druck: je Achse N_cr = π² E I/L_K², λ̄ = √(f_y A/N_cr), χ nach
  (8) -- um y mit Kurve b, um z mit c, denn (h - t_f)/b = 0.94 liegt unter 1.2.
* HEB 300 mit Druck und Moment, nur um y knickend: (50) mit ω nach 5.1.9.1.
* IPE 600 mit M_y allein, L_D = 6 m: σ_cr,D = √(σ_Dv² + σ_Dw²) nach (91) bis (93),
  der Druckgurt der Flansch und ein Drittel der halben Steghoehe (Figur 40);
  χ_D nach (10) mit α_D = 0.21.
* HEM 180 wie in der Excel-Datei «Stabilitätsnachweise» des Benutzers:
  N_Ed = -1385 kN, M_y = -57 kNm, M_z = 7.53 kNm, alle Laengen 3.63 m -- die
  linke Seite von (51) ist dort 0.58283.
"""

import json
import math
import unittest

from opencivil.core.nachweis import OHNE_EINWIRKUNG
from opencivil.projekt import Projekt
from opencivil.projekt.lesen import ProjektFehler
from opencivil.querschnitt.zugseite import Zugseite
from opencivil.stahlbau import stabilitaet as st
from opencivil.stahlbau import widerstand as wd
from opencivil.stahlbau.querschnitt import Stahlquerschnitt
from opencivil.stahlprofile import tabelle
from opencivil.web.api import katalog
from tests.test_stahlbau import kennzahlen
from tests.test_stahlprofile_qa import analyse, projekt, zeichnung

E = 210000.0
G = 81000.0
F_Y = 355.0
F = F_Y / 1.05
EPS = math.sqrt(235.0 / F_Y)

#: So weit darf die Rechnung von der Hand abweichen -- beide mit denselben Kennwerten.
GENAU = 1e-9

#: Die beiden Schalen eines Kastens aus zwei UPE 200, Rücken an Rücken.
ZWEI_UPE = ((-60, 0, "UPE 200", {"gespiegelt": True}), (60, 0, "UPE 200", {}))


def stab(*profile, **kurven):
    """
    Der Stab einer Analyse aus ``profile`` -- S355, gerechnet mit ``f_y/γ_M1``
    -- und je Achse die gewaehlte Kurve, sonst die des Profils.
    """
    p = projekt()
    a = analyse(p, *profile)
    aufbau = p.aufbauen()
    q = aufbau.teile[a.kennung].objekt
    I_T = aufbau.werk.loese(q.d_torsion.id).wert(q.d_torsion.id).groesse.si * 1e12
    stahl = Stahlquerschnitt(q.flaechen, q.eltern)
    w = stahl.werte()
    return st.Stab(stahl, [F], [F_Y], [EPS], E=E, G=G, I={"y": w.I_y, "z": w.I_z}, I_T=I_T,
                   bezug=(w.y_S, w.z_S), biegung=q.biegung,
                   kurven={a: kurven.get(a, st.Knickkurve.PROFIL) for a in ("y", "z")},
                   profil=st.einzelprofil((f.kennung, f.profil) for f in q.flaechen))


def fall(name="Fall", N=0.0, M_y=0.0, M_z=0.0, **laengen):
    """Ein Fall in kN und kNm wie an der Oberflaeche, die Laengen in m."""
    return st.Stabfall(name, N=N * 1e3, M_y=M_y * 1e3, M_z=M_z * 1e3, **laengen)


def chi(lam, alpha, lam_0):
    """(8) mit λ̄_0 = 0.2 und (10) mit 0.4, von Hand."""
    phi = 0.5 * (1.0 + alpha * (lam - lam_0) + lam ** 2)
    return min(1.0, 1.0 / (phi + math.sqrt(phi ** 2 - lam ** 2)))


def nachweise(*profile, faelle, einachsig=False, **kurven):
    """Die Urteile je Fall durch das ganze Projekt, dazu die Loesung."""
    p = projekt()
    a = analyse(p, *profile)
    a.einachsig = einachsig
    for achse, k in kurven.items():
        setattr(a, f"knickkurve_{achse}", k)
    for name, werte in faelle.items():
        a.stabilitaetsfall(name, **werte)
    aufbau = p.aufbauen()
    loesung = aufbau.werk.loese(*aufbau.teile[a.kennung].ziele())
    return {u.fall: u for u in loesung.urteile if u.art == "Stab"}, loesung


def texte(loesung):
    """Was das Protokoll in Worten sagt -- Titel, Erklaerungen und Hinweise."""
    return " ".join(str(getattr(b, "titel", "") or getattr(b, "text", ""))
                    for b in loesung.protokoll.bloecke)


class TestHilfen(unittest.TestCase):
    def test_abminderung(self):
        """Bis λ̄_0 kein Abzug; bei λ̄ = 1 auf Kurve b 0.597, wie in der Tabelle der Kurven."""
        self.assertEqual(st.abminderung(0.2, 0.34, 0.2)[1], 1.0)
        self.assertEqual(st.abminderung(0.4, 0.21, 0.4)[1], 1.0)
        phi, x = st.abminderung(1.0, 0.34, 0.2)
        self.assertAlmostEqual(phi, 1.136)
        self.assertAlmostEqual(x, 0.5970, delta=1e-4)

    def test_eta(self):
        """(94): eins beim konstanten Moment; unter ψ = -0.5 bleibt der Wert dort."""
        self.assertAlmostEqual(st.eta(1.0), 1.0)
        self.assertAlmostEqual(st.eta(0.0), 1.75)
        self.assertAlmostEqual(st.eta(-0.5), 2.35)
        self.assertAlmostEqual(st.eta(-1.0), 2.35)

    def test_omega(self):
        self.assertAlmostEqual(st.omega(1.0), 1.0)
        self.assertAlmostEqual(st.omega(0.0), 0.6)
        self.assertAlmostEqual(st.omega(-1.0), 0.4)

    def test_kurven_der_figur_7(self):
        """Um die starke und um die schwache Achse -- RRK und RRW, dieselbe Form, kalt und warm."""
        for name, kurven in (("IPE 600", "ab"), ("HEB 300", "bc"), ("HEM 180", "bc"),
                             ("ROR 219.1 x 8", "aa"), ("RRK 200 x 100 x 8", "cc"),
                             ("RRW 200 x 100 x 8", "aa"), ("UPE 200", "cc"), ("UNP 200", "cc")):
            with self.subTest(profil=name):
                profil = tabelle.profil(name)
                self.assertEqual(st.kurve(profil, True)[0] + st.kurve(profil, False)[0], kurven)
        self.assertEqual(st.kurve(tabelle.profil("RRW 200 x 100 x 8"), True)[1],
                         "warmgefertigtes Hohlprofil")

    def test_jede_reihe_hat_ihre_kurve(self):
        """Wer eine Reihe dazunimmt, die kein I ist, muss ihr eine Kurve geben."""
        for reihe in tabelle.PROFILREIHEN:
            with self.subTest(reihe=reihe.kurz):
                self.assertIn(st.kurve(reihe.profile[0], True)[0], "abcd")

    def test_druckgurt_eines_i(self):
        """Der Flansch und ein Drittel der halben Hoehe zwischen den Flanschen, ohne Ausrundung."""
        g = st.druckgurt(tabelle.profil("IPE 600"))
        steg = (600 - 2 * 19) / 2 / 3
        I = 19 * 220 ** 3 / 12 + steg * 12 ** 3 / 12
        self.assertAlmostEqual(g.A, 220 * 19 + 12 * steg)
        self.assertAlmostEqual(g.I, I)
        self.assertAlmostEqual(g.i, math.sqrt(I / (220 * 19 + 12 * steg)))

    def test_druckgurt_eines_rechteckrohrs(self):
        """Zwei Stege im Abstand (b - t)/2 von der Mitte."""
        g = st.druckgurt(tabelle.profil("RRK 200 x 100 x 8"))
        steg = (200 - 2 * 8) / 2 / 3
        self.assertAlmostEqual(g.A, 100 * 8 + 2 * 8 * steg)
        self.assertAlmostEqual(g.I, 8 * 100 ** 3 / 12
                               + 2 * (steg * 8 ** 3 / 12 + 8 * steg * 46 ** 2))

    def test_ohne_druckgurt(self):
        """Ohne starke Achse oder nicht doppelsymmetrisch: kein Kippen nach Anhang B."""
        for name in ("RRK 200 x 200 x 8", "UPE 200", "ROR 219.1 x 8"):
            with self.subTest(profil=name):
                self.assertIsNone(st.druckgurt(tabelle.profil(name)))

    def test_nur_ein_einziges_profil_hat_kurven(self):
        self.assertEqual(stab((0, 0, "HEB 300", {})).profil.name, "HEB 300")
        self.assertIsNone(stab(*ZWEI_UPE).profil)


class TestKnicken(unittest.TestCase):
    """HEB 300 unter Druck -- je Achse seine Kurve."""

    @classmethod
    def setUpClass(cls):
        cls.stab = stab((0, 0, "HEB 300", {}))

    def N_K_Rd(self, achse, L_K, alpha):
        s = self.stab
        N_cr = math.pi ** 2 * E * s.I[achse] / L_K ** 2
        return chi(math.sqrt(F_Y * s.A / N_cr), alpha, 0.2) * s.A * F

    def test_von_hand(self):
        x = st.rechnen(self.stab, fall(N=-2000, L_K_y=6.0, L_K_z=3.0))
        self.assertEqual((x.klasse, x.knicken["y"].kurve, x.knicken["z"].kurve), (1, "b", "c"))
        N_K_Rd = min(self.N_K_Rd("y", 6000, 0.34), self.N_K_Rd("z", 3000, 0.49))
        self.assertAlmostEqual(x.alpha / (N_K_Rd / 2000e3), 1.0, delta=GENAU)
        self.assertEqual(x.N_K_Rd, x.knicken["z"].N_K_Rd)

    def test_gehalten(self):
        """Eine Knicklaenge null: N_cr unendlich, der Querschnitt traegt alles."""
        x = st.rechnen(self.stab, fall(N=-2000))
        self.assertTrue(all(k.gehalten and math.isinf(k.N_cr) for k in x.knicken.values()))
        self.assertAlmostEqual(x.alpha / (self.stab.A * F / 2000e3), 1.0, delta=GENAU)

    def test_druck_und_biegung_nach_50(self):
        """Nur um y knickend, mit ψ_y = 0: ω = 0.6, das Moment verstaerkt um 1/(1 - N/N_cr)."""
        M_Rd = kennzahlen((0, 0, "HEB 300", {}))[0]["M_Rd_unten"] * 1e6
        x = st.rechnen(self.stab, fall(N=-1000, M_y=100, psi_y=0.0, L_K_y=6.0))
        N_cr = math.pi ** 2 * E * self.stab.I["y"] / 6000 ** 2
        n = 1000e3 / self.N_K_Rd("y", 6000, 0.34)
        alpha = (1 - n) / (0.6 / (1 - 1000e3 / N_cr) * 100e6 / M_Rd)
        self.assertAlmostEqual(x.alpha / alpha, 1.0, delta=1e-6)
        self.assertIsNone(x.g51, "ohne Kipplaenge gilt (51) nicht")

    def test_jenseits_der_knicklast(self):
        """Schon N_Ed allein ueber N_K,Rd: α misst die Normalkraft."""
        x = st.rechnen(self.stab, fall(N=-4000, M_y=50, L_K_y=6.0, L_K_z=6.0))
        self.assertAlmostEqual(x.alpha_N, x.N_K_Rd / 4000e3)
        self.assertEqual(x.alpha, x.alpha_N)


class TestKippen(unittest.TestCase):
    """IPE 600 mit M_y allein: der Druckgurt oben, das Moment zieht unten."""

    @classmethod
    def setUpClass(cls):
        cls.stab = stab((0, 0, "IPE 600", {}))
        cls.M_pl = kennzahlen((0, 0, "IPE 600", {}))[0]["M_Rd_unten"] * 1e6

    def test_von_hand(self):
        s = self.stab
        x = st.rechnen(s, fall(M_y=300, L_D=6.0))
        W_el = s.I["y"] / 300
        sigma_Dv = math.pi / (6000 * W_el) * math.sqrt(G * s.I_T * E * s.I["z"])
        i_g = st.druckgurt(tabelle.profil("IPE 600")).i
        sigma_Dw = math.pi ** 2 * E / (6000 / i_g) ** 2
        M_cr = W_el * math.hypot(sigma_Dv, sigma_Dw)
        chi_D = chi(math.sqrt(self.M_pl * 1.05 / M_cr), 0.21, 0.4)
        k = x.kippen
        self.assertEqual((k.seite, k.eta), (Zugseite.UNTEN, 1.0))
        self.assertAlmostEqual(k.M_cr / M_cr, 1.0, delta=GENAU)
        self.assertAlmostEqual(x.alpha / (chi_D * self.M_pl / 300e6), 1.0, delta=1e-6)
        self.assertEqual(x.alpha, x.alpha_9)

    def test_die_momentenverteilung(self):
        """ψ = 0: η = 1.75 -- die Kipplaenge des Druckgurts wird kuerzer."""
        k = st.rechnen(self.stab, fall(M_y=300, psi_y=0.0, L_D=6.0)).kippen
        self.assertAlmostEqual(k.eta, 1.75)
        self.assertAlmostEqual(k.L_K, 6000 / math.sqrt(1.75))

    def test_mit_der_normalkraft_kippt_die_klasse_4_ohne_saint_venant(self):
        """
        Wie das Beispiel «Beulen»: der Steg in Klasse 4, (62) und (63) -- die
        Imperfektion nach Spalte EE mit der Knicklaenge, um y Kurve a, um z b.
        """
        x = st.rechnen(self.stab, fall(N=-3500, M_y=30, L_K_y=3.0, L_K_z=1.5, L_D=1.5))
        self.assertEqual((x.klasse, x.kippen.sigma_Dv), (4, 0.0))
        self.assertEqual(x.w_0, {"y": 3000 / 300, "z": 1500 / 250})
        self.assertEqual([g.verstaerkt for g in x.g62], ["y", "z"])
        self.assertEqual(x.alpha, min(g.alpha for g in x.g62))

    def test_klasse_4_ohne_moment(self):
        """Symmetrisch, ohne Versatz: 5.3.8 mit A_eff -- ohne (62) und (63)."""
        x = st.rechnen(self.stab, fall(N=-3000, L_K_y=6.0, L_K_z=1.5))
        self.assertEqual((x.klasse, x.g62, x.mit_versatz), (4, [], False))
        A_eff = x.wirksam.A_eff
        N_K_Rd = min(chi(math.sqrt(F_Y * A_eff / (math.pi ** 2 * E * self.stab.I[a] / L ** 2)),
                         alpha, 0.2) * A_eff * F
                     for a, L, alpha in (("y", 6000, 0.21), ("z", 1500, 0.34)))
        self.assertAlmostEqual(x.alpha / (N_K_Rd / 3000e3), 1.0, delta=GENAU)

    def test_ein_rechteckrohr_kippt_kaum(self):
        """Geschlossen: der Anteil nach Saint-Venant ist gross, χ_D fast eins."""
        x = st.rechnen(stab((0, 0, "RRK 200 x 100 x 8", {})), fall(M_y=40, L_D=8.0))
        self.assertGreater(x.kippen.sigma_Dv, 50 * x.kippen.sigma_Dw)
        self.assertGreater(x.kippen.chi, 0.99)


class TestGleichung51(unittest.TestCase):
    """HEM 180 wie in der Excel-Datei des Benutzers."""

    EXCEL = {"N": -1385, "M_y": -57, "M_z": 7.53, "L_K_y": 3.63, "L_K_z": 3.63, "L_D": 3.63}

    @classmethod
    def setUpClass(cls):
        cls.stab = stab((0, 0, "HEM 180", {}))

    def test_wie_die_excel_datei(self):
        x = st.rechnen(self.stab, fall(**self.EXCEL))
        g = x.g51
        self.assertEqual((x.klasse, g.s, g.w), (1, "y", "z"))
        self.assertAlmostEqual(g.a ** g.beta + g.c ** g.beta, 0.58283, delta=0.002)
        self.assertAlmostEqual(g.beta, 0.4 + 1385e3 / (self.stab.A * F) + 186 / (200 - 24),
                               delta=GENAU)
        self.assertEqual(x.alpha, g.alpha, "die guenstigere von (50) und (51)")
        self.assertGreater(g.alpha, x.alpha_50)

    def test_nur_wo_51_gilt(self):
        """Ist das Kippen oder das Knicken aus der Ebene verhindert, gilt (50) allein."""
        for gehalten in ("L_D", "L_K_z"):
            with self.subTest(gehalten=gehalten):
                x = st.rechnen(self.stab, fall(**{**self.EXCEL, gehalten: 0.0}))
                self.assertIsNone(x.g51)
                self.assertEqual(x.alpha, min(x.alpha_50, x.alpha_9 or math.inf))


class TestWasFehlt(unittest.TestCase):
    """Ohne einzelnes Profil keine Kurve und kein Kippen -- grau, mit dem Grund."""

    def test_ohne_profil_fehlen_die_kurven(self):
        s = stab(*ZWEI_UPE)
        self.assertEqual(st.rechnen(s, fall(N=-600, L_K_y=4.0, L_K_z=4.0)).fehlt,
                         st.KURVE_FEHLT.format(
                             was="Die Knickspannungskurven um y und um z fehlen",
                             wahl="je eine wählen"))
        self.assertEqual(st.rechnen(s, fall(N=-600, L_K_y=4.0)).fehlt,
                         st.KURVE_FEHLT.format(was="Die Knickspannungskurve um y fehlt",
                                               wahl="eine wählen"))

    def test_gewaehlte_kurven(self):
        s = stab(*ZWEI_UPE, y=st.Knickkurve.C, z=st.Knickkurve.B)
        x = st.rechnen(s, fall(N=-600, L_K_y=4.0, L_K_z=4.0))
        self.assertEqual((x.fehlt, x.knicken["y"].kurve, x.knicken["y"].grund),
                         ("", "c", "gewählt"))
        self.assertEqual(st.rechnen(s, fall(N=-600, M_y=20, L_K_y=4.0, L_D=3.0)).fehlt,
                         st.KIPPEN_FEHLT)

    def test_ein_u_kippt_nicht_nach_anhang_b(self):
        s = stab((0, 0, "UPE 200", {}))
        self.assertEqual(st.rechnen(s, fall(M_y=20, L_D=3.0)).fehlt, st.KIPPEN_FEHLT)
        self.assertEqual(st.rechnen(s, fall(M_y=20)).fehlt, "", "gehalten kippt es nicht")

    def test_ein_rundrohr_der_klasse_4(self):
        s = stab((0, 0, "ROR 762 x 6", {}))
        self.assertEqual(st.rechnen(s, fall(N=-1000, L_K_y=4.0, L_K_z=4.0)).fehlt,
                         wd.ROHR_KLASSE_4)


class TestImProjekt(unittest.TestCase):
    """Der Nachweis rechnet wie der Stab -- mit den Kennwerten des Baustahls."""

    def test_wie_der_stab(self):
        urteile, loesung = nachweise((0, 0, "HEM 180", {}), faelle={
            "Excel": {"N_Ed": -1385, "M_y_Ed": -57, "M_z_Ed": 7.53, "L_K_y": 3.63,
                      "L_K_z": 3.63, "L_D": 3.63}})
        x = st.rechnen(stab((0, 0, "HEM 180", {})), fall(**TestGleichung51.EXCEL))
        u = urteile["Excel"]
        self.assertTrue(u.erfuellt)
        self.assertAlmostEqual(u.erfuellungsgrad.si / x.alpha, 1.0, delta=1e-9)
        self.assertEqual(u.begruendung, "Klasse 1, massgebend (51), bei N_Ed = -1385.0 kN.")

    def test_einachsig_zaehlt_m_z_nicht(self):
        werte = {"N_Ed": -1000, "M_y_Ed": 100, "L_K_y": 5, "L_K_z": 5, "L_D": 5}
        einachsig, _ = nachweise((0, 0, "HEB 300", {}), einachsig=True,
                                 faelle={"E": {**werte, "M_z_Ed": 50}})
        ohne, _ = nachweise((0, 0, "HEB 300", {}), faelle={"E": werte})
        self.assertAlmostEqual(einachsig["E"].erfuellungsgrad.si, ohne["E"].erfuellungsgrad.si)

    def test_was_fehlt_steht_grau_am_fall(self):
        urteile, loesung = nachweise(*ZWEI_UPE, faelle={"Zwei": {"N_Ed": -600, "L_K_y": 4,
                                                                 "L_K_z": 0, "L_D": 0}})
        u = urteile["Zwei"]
        satz = st.KURVE_FEHLT.format(was="Die Knickspannungskurve um y fehlt", wahl="eine wählen")
        self.assertEqual((u.erfuellt, u.hinweis), (False, satz))
        self.assertIn(satz, texte(loesung))

    def test_ohne_einwirkung(self):
        urteile, _ = nachweise((0, 0, "HEB 300", {}), faelle={"Leer": {}})
        self.assertEqual(urteile["Leer"].hinweis, OHNE_EINWIRKUNG)
        self.assertTrue(math.isinf(urteile["Leer"].erfuellungsgrad.si))

    def test_sehr_schlank(self):
        """λ_K = L_K/i ueber 200: ein Hinweis, gerechnet wird trotzdem."""
        urteile, loesung = nachweise((0, 0, "IPE 600", {}), faelle={
            "Schlank": {"N_Ed": -100, "L_K_y": 6, "L_K_z": 15, "L_D": 0}})
        self.assertTrue(urteile["Schlank"].erfuellt)
        self.assertIn("über 200", texte(loesung))


class TestZeichnung(unittest.TestCase):
    """Was die Kachel und das Fenster vom Kern erfahren."""

    def test_die_kurven_des_profils(self):
        """Um 90° gedreht ist z die starke Achse: um y Kurve c, um z b."""
        p = projekt()
        antwort = zeichnung(p, analyse(p, (0, 0, "HEB 300", {"drehung": 90})))
        self.assertEqual(antwort["knickkurven"], {
            "y": {"kurve": "c", "grund": "Walzprofil um die schwache Achse"},
            "z": {"kurve": "b", "grund": "Walzprofil um die starke Achse"}})
        self.assertEqual(antwort["knickkurven_fehlen"], "")

    def test_was_fehlt_nur_mit_einem_fall(self):
        """Ohne Fall fehlt nichts; ein ausgeschalteter zaehlt nicht."""
        p = projekt()
        a = analyse(p, *ZWEI_UPE)
        self.assertEqual((zeichnung(p, a)["knickkurven"], zeichnung(p, a)["knickkurven_fehlen"]),
                         (None, ""))
        a.stabilitaetsfall("Zwei", N_Ed=-600, L_K_y=4, L_K_z=0, L_D=0)
        a.stabilitaetsfall("Aus", N_Ed=-600, L_K_y=4, L_K_z=4, L_D=0, aktiv=False)
        self.assertEqual(zeichnung(p, a)["knickkurven_fehlen"],
                         st.KURVE_FEHLT.format(was="Die Knickspannungskurve um y fehlt",
                                               wahl="eine wählen"))

    def test_ohne_stahl(self):
        p = projekt()
        a = analyse(p, polygone=[([[-200, -200], [200, -200], [200, 200], [-200, 200]], "b1")])
        antwort = zeichnung(p, a)
        self.assertEqual((antwort["knickkurven"], antwort["knickkurven_fehlen"]), (None, ""))


class TestEintrag(unittest.TestCase):
    def test_im_katalog(self):
        k = katalog()
        self.assertEqual([s["wert"] for s in k["querschnittsanalyse"]["knickkurven"]],
                         ["profil", "a", "b", "c", "d"])
        json.dumps(k)

    def test_grenzen(self):
        """
        Zug, ψ ausserhalb von -1 bis 1 und eine negative Laenge weist schon das
        Feld ab -- vor dem Rechnen sagt es die Meldung mit dem Namen des Falls.
        """
        for werte, heisst in (({"N_Ed": 100}, "Normalkraft N_Ed"), ({"psi_y": 1.5}, "ψ_y"),
                              ({"psi_z": -1.5}, "ψ_z"), ({"L_K_y": -1}, "Knicklänge L_K,y"),
                              ({"L_D": -2}, "Kipplänge L_D")):
            with self.subTest(werte=werte):
                p = projekt()
                analyse(p, (0, 0, "HEB 300", {})).stabilitaetsfall("Falsch", **werte)
                with self.assertRaisesRegex(ProjektFehler,
                                            f"Stabilitätsnachweis 'Falsch': .*{heisst}"):
                    p.inhalt_pruefen()

    def test_speichern_und_laden(self):
        p = projekt()
        a = analyse(p, (0, 0, "HEB 300", {}))
        a.knickkurve_y = st.Knickkurve.C
        a.stabilitaetsfall("Feld", N_Ed=-500, M_y_Ed=80, psi_y=-0.5, L_K_y=6, L_K_z=3, L_D=3)
        wieder = Projekt.aus_dict(p.als_dict()).querschnittsanalysen[0]
        self.assertEqual((wieder.knickkurve_y, wieder.knickkurve_z),
                         (st.Knickkurve.C, st.Knickkurve.PROFIL))
        self.assertEqual(wieder.stabilitaetsfaelle, a.stabilitaetsfaelle)
        self.assertEqual(wieder.stabfaelle()[0],
                         st.Stabfall("Feld", N=-500e3, M_y=80e3, psi_y=-0.5, L_K_y=6.0,
                                     L_K_z=3.0, L_D=3.0, L=3.0))


if __name__ == "__main__":
    unittest.main()
