"""
Tests für die Querschnitte und Materialien der Balkensysteme: welches
Material ein Stab nimmt, auch das seines Querschnitts, das Bildchen jedes
Querschnitts, die Felder je Art und E_eq aus einer Platte oder
Querschnittsanalyse. Bis 2026-11-20 standen sie in tests/test_balkensystem.py,
das damit über tausend Zeilen hatte.
"""

import unittest

from opencivil.projekt import BalkensystemEintrag, Projekt, QuerschnittsanalyseEintrag
from opencivil.projekt.balkensystem import StabmaterialEintrag
from opencivil.projekt.balkensystem3d import RaummaterialEintrag
from opencivil.projekt.staebe import MATERIAL_DES_QUERSCHNITTS
from opencivil.querschnitt.platte import Richtung
from opencivil.querschnitt.zugseite import Zugseite
from opencivil.spannungsanalyse.linie import moment_kruemmung
from opencivil.spannungsanalyse.modul import aequivalenter_modul
from opencivil.spannungsanalyse.platte import loeserpaar
from opencivil.spannungsanalyse.schnitt import schnittpaar
from opencivil.web import dienst
from opencivil.web.api import katalog
from tests.traeger import traeger
from tests.unfertig import meldung


class TestMaterialien(unittest.TestCase):
    """
    Die Materialien eines Systems (Benutzer, 2026-10-24): ein Beton des
    Projekts -- E_cm und die Dichte des Stahlbetons von ihm --, ein
    Baustahl des Projekts -- E_a und ρ_a -- oder ein eigenes mit E und
    Dichte von Hand.
    """

    def meldungen(self, p):
        return [m.text for m in p.rechnen().balkensystem("r1").ergebnis.meldungen if m.haelt_an]

    def test_eigenes_material_rechnet_mit_seinem_e(self):
        p = traeger()
        s = p.balkensysteme[0]
        s.linien[0].material = s.eigenes_material("Weich", E=10000.0, rho=2500.0).kennung
        e = p.rechnen()
        EI = 10000e6 * 0.3 * 0.6 ** 3 / 12
        self.assertAlmostEqual(e.wert("balkensystem.r1.Q1.M2.EI").groesse.si, EI, delta=1e-9 * EI)
        # Die Durchbiegung in der Mitte, nach unten positiv: 5 q L⁴ / (384 EI).
        w = e.balkensystem("r1").verlaeufe("G")["L1"].extrem("f_z").groesst[1]
        self.assertAlmostEqual(w, 5 * 10e3 * 6 ** 4 / (384 * EI), delta=1e-6)

    def test_ein_querschnitt_aus_zwei_materialien(self):
        """Derselbe Querschnitt aus Beton und aus Stahl: verschieden steif, verschieden schwer."""
        p = traeger()
        s = p.balkensysteme[0]
        s.lastfaelle[0].eigengewicht = True
        stahl = s.eigenes_material("Stahl", E=200000.0, rho=7850.0)
        q = s.querschnitt("Gleich", "rechteck", b=100.0, h=100.0)
        s.linie((6, 0), (8, 0), querschnitt=q, material="M1")
        s.linie((8, 0), (10, 0), querschnitt=q, material=stahl)
        s.lager_an((10, 0), "verschieblich")
        e = p.rechnen()
        E_cm = e.wert("beton.b1.E_cm").groesse.si
        self.assertAlmostEqual(e.wert("balkensystem.r1.Q2.M1.EA").groesse.si, E_cm * 0.01,
                               delta=1e-9 * E_cm)
        self.assertAlmostEqual(e.wert("balkensystem.r1.Q2.M2.EA").groesse.si, 200000e6 * 0.01,
                               delta=1e-6)
        self.assertAlmostEqual(e.wert("balkensystem.r1.Q2.M1.g_k").groesse.si, 250.0)
        self.assertAlmostEqual(e.wert("balkensystem.r1.Q2.M2.g_k").groesse.si, 785.0)

    def test_eigenes_material_beginnt_mit_dem_ersten_beton(self):
        """C25/30: E_cm = 10 000 · ∛33 = 32 075 N/mm², G_cm = E_cm / 2.4 = 13 365 N/mm², ρ_sb = 2500 kg/m³."""
        eben, raum = StabmaterialEintrag(art="eigen"), RaummaterialEintrag(art="eigen")
        self.assertEqual((eben.E, eben.rho), (32075.0, 2500.0))
        self.assertEqual((raum.E, raum.rho, raum.G), (32075.0, 2500.0, 13365.0))
        self.assertEqual(katalog()["vorlagen"]["raummaterial"]["G"], 13365.0)

    def test_baukasten_und_herleitung(self):
        s = BalkensystemEintrag(kennung="r1", name="T")
        beton = s.beton("b1")
        self.assertIs(s.beton("b1"), beton)                    # einmal je Beton
        holz = s.eigenes_material("Holz", E=11000.0, rho=500.0)
        self.assertEqual([(m.kennung, m.art) for m in s.stabmaterialien],
                         [("M1", "beton"), ("M2", "eigen")])
        self.assertEqual((holz.name, holz.E, holz.rho), ("Holz", 11000.0, 500.0))
        self.assertEqual(s.materialien(), ["b1"])
        p = traeger()
        s = p.balkensysteme[0]
        s.linien[0].material = s.eigenes_material("Holz", E=11000.0, rho=500.0).kennung
        text = str(p.rechnen().bericht())
        self.assertIn("E-Modul, «Holz» (von Hand)", text)
        self.assertIn("Biegesteifigkeit, «R» aus Holz", text)

    def test_eine_meldung_je_material(self):
        """
        Ein Material, das nicht trägt, nennt alle Stäbe, die es nehmen, in
        einer Meldung -- bis 2026-11-19 stand sie je Stab da.
        """
        p = traeger()
        s = p.balkensysteme[0]
        s.linie((6, 0), (9, 0), querschnitt=s.linien[0].querschnitt, material=s.linien[0].material)
        s.linie((9, 0), (12, 0), querschnitt=s.linien[0].querschnitt, material=s.linien[0].material)
        s.stabmaterialien[0].stoff = ""
        meldungen = [m for m in p.rechnen().balkensystem("r1").ergebnis.meldungen if m.haelt_an]
        self.assertEqual([m.text for m in meldungen],
                         ["L1, L2 und L3 nehmen einen Beton des Projekts, aber es ist noch keiner "
                          "gewählt."])
        self.assertEqual(meldungen[0].elemente, ("L1", "L2", "L3", s.linien[0].querschnitt, "M1"))
        self.assertEqual((meldungen[0].fehler, meldungen[0].unfertig), (False, True))

    def test_der_beton_ist_ein_verweis(self):
        """
        Den Beton eines Materials löscht man nicht; zeigt es ins Leere, rechnet
        das System nicht und sagt es am Stab, nach derselben Regel wie bei
        jedem Bauteil -- grau und ohne Kennungen, die der Benutzer nirgends
        sieht (bis 2026-11-19 «das Material M1, aber das Material 'b7'»). Bis
        2026-11-19 hielt das auch das ganze System an, und das Zeichenfenster
        bekam nur einen Fehler.
        """
        p = traeger()
        self.assertEqual(p.verweise("b1"), [p.balkensysteme[0]])
        p.balkensysteme[0].stabmaterialien[0].stoff = "b7"
        self.assertEqual(self.meldungen(p), ["L1 nimmt einen Beton des Projekts, aber das gewählte "
                                             "Material gibt es nicht mehr – eines wählen."])
        antwort = dienst.bearbeite("balkensystem_verlauf", {"projekt": p.als_dict(), "kennung": "r1"})
        self.assertEqual(antwort.status, 200)

    def test_baustahl_des_projekts(self):
        """E_a = 210 000 N/mm² und ρ_a = 7850 kg/m³ (SIA 263:2013, 3.2.2.1)."""
        p = traeger()
        p.baustahl("S355")
        s = p.balkensysteme[0]
        s.lastfaelle[0].eigengewicht = True
        stahl = s.baustahl("st1")
        self.assertIs(s.baustahl("st1"), stahl)                # einmal je Baustahl
        s.linien[0].material = stahl.kennung
        e = p.rechnen()
        EI = 210000e6 * 0.3 * 0.6 ** 3 / 12
        self.assertAlmostEqual(e.wert("balkensystem.r1.Q1.M2.EI").groesse.si, EI, delta=1e-9 * EI)
        self.assertAlmostEqual(e.wert("balkensystem.r1.Q1.M2.g_k").groesse.si,
                               7850 * 10 * 0.18, delta=1e-9)
        self.assertEqual(p.verweise("st1"), [s])
        self.assertIn("E_a des Baustahls", str(p.rechnen().bericht()))

    def test_ein_beton_ist_kein_baustahl(self):
        p = traeger()
        p.balkensysteme[0].stabmaterialien[0].art = "baustahl"
        meldungen = self.meldungen(p)
        self.assertEqual(len(meldungen), 1)
        self.assertIn("«C30/37» ist kein Baustahl", meldungen[0])

    def test_betonstahl_ist_kein_material_der_staebe(self):
        p = traeger()                                   # mit B500B als s1
        p.balkensysteme[0].stabmaterialien[0].stoff = "s1"
        meldungen = self.meldungen(p)
        self.assertEqual(len(meldungen), 1)
        self.assertEqual(meldungen, ["L1 nimmt «B500B», aber «B500B» ist kein Beton."])

    def test_ohne_beton(self):
        p = traeger()
        p.balkensysteme[0].stabmaterialien[0].stoff = ""
        meldungen = self.meldungen(p)
        self.assertEqual(len(meldungen), 1)
        self.assertIn("es ist noch keiner gewählt", meldungen[0])

    def test_null_ist_kein_e_modul(self):
        p = traeger()
        s = p.balkensysteme[0]
        s.linien[0].material = s.eigenes_material("Weich", E=10000.0, rho=0.0).kennung
        s.stabmaterialien[-1].E = 0.0
        self.assertRegex(meldung(Projekt.aus_dict(p.als_dict())), "E-Modul")


class TestMaterialDesQuerschnitts(unittest.TestCase):
    """
    «gemäss Querschnitt»: eine Linie nimmt das Material, das ihre Platte oder
    Querschnittsanalyse mitbringt (Benutzer, 2026-10-23).
    """

    def projekt(self, art):
        """Der Träger und daneben ein Stab aus einer Platte oder Analyse in C25/30."""
        p = traeger()
        p.beton("C25/30")
        bezug = (p.platte("Decke", h=250, beton="b2") if art == "platte"
                 else p.analyse("Unterzug", beton="b2"))
        s = p.balkensysteme[0]
        q = s.querschnitt_aus("Aus dem Bauteil", art, bezug)
        s.linie((6, 0), (9, 0), querschnitt=q, material=MATERIAL_DES_QUERSCHNITTS)
        s.lager_an((9, 0), "verschieblich")
        return p, q

    def meldungen(self, p):
        return [m.text for m in p.rechnen().balkensystem("r1").ergebnis.meldungen if m.haelt_an]

    def test_platte_und_analyse_bringen_ihren_beton(self):
        for art in ("platte", "analyse"):
            with self.subTest(art=art):
                p, q = self.projekt(art)
                e = p.rechnen()
                self.assertTrue(e.balkensystem("r1").ergebnis.gueltig,
                                e.balkensystem("r1").ergebnis.meldungen)
                quer, material = e.aufbau.balkensysteme["r1"].paare["L2"]
                self.assertEqual((quer, material.stoff.name), (q.kennung, "C25/30"))
                A = e.wert(f"balkensystem.r1.{q.kennung}.A").groesse.si
                self.assertAlmostEqual(
                    e.wert(f"balkensystem.r1.{q.kennung}.{MATERIAL_DES_QUERSCHNITTS}.EA").groesse.si,
                    e.wert("beton.b2.E_cm").groesse.si * A, delta=1e-3)

    def test_eine_vorlage_bringt_keines(self):
        p = traeger()
        p.balkensysteme[0].linien[0].material = MATERIAL_DES_QUERSCHNITTS
        meldungen = self.meldungen(p)
        self.assertEqual(len(meldungen), 1)
        self.assertIn("L1 nimmt das Material gemäss Querschnitt", meldungen[0])
        self.assertIn("nach Vorlage", meldungen[0])

    def test_zwei_betone_in_der_analyse(self):
        p, q = self.projekt("analyse")
        p.querschnittsanalysen[0].polygon([(300, 0), (600, 0), (600, 200), (300, 200)],
                                          material="b1")
        meldungen = self.meldungen(p)
        self.assertEqual(len(meldungen), 1)
        self.assertIn("C25/30 und C30/37", meldungen[0])

    def test_eine_leere_analyse(self):
        p, q = self.projekt("analyse")
        p.querschnittsanalysen[0] = QuerschnittsanalyseEintrag.neu(kennung="a1", name="Leer")
        meldungen = self.meldungen(p)
        self.assertTrue(any("gemäss Querschnitt" in m
                            and "«Leer» rechnet nicht (noch nichts gezeichnet)" in m
                            for m in meldungen), meldungen)


class TestUmrisse(unittest.TestCase):
    """Je Querschnitt sein Umriss für das Bildchen in seiner Zeile (Benutzer, 2026-10-24)."""

    def test_vorlage_platte_analyse_und_kennwerte(self):
        p = traeger()
        s = p.balkensysteme[0]
        s.querschnitt_aus("Streifen", "platte", p.platte("Decke", h=250))
        s.querschnitt_aus("Unterzug", "analyse", p.analyse("Unterzug"))
        s.querschnitt_mit_kennwerten("Von Hand", A=1000.0, I=10.0)
        s.querschnitt("Unmöglich", "rechteck", h=0.0)
        umrisse = dienst.bearbeite("rechnen", {"projekt": p.als_dict()}).daten["zeichendaten"]["r1"]["umrisse"]
        # Das Rechteck 300 × 600 mit seinen Massen, der Streifen 1000 × 250 der Platte.
        self.assertEqual(umrisse["Q1"], [[[0.0, 0.0], [300.0, 0.0], [300.0, 600.0], [0.0, 600.0]]])
        self.assertEqual(umrisse["Q2"], [[[0.0, 0.0], [1000.0, 0.0], [1000.0, 250.0], [0.0, 250.0]]])
        self.assertEqual([len(polygon) for polygon in umrisse["Q3"]], [4])
        # Kennwerte von Hand haben keine Form, ein unmöglicher Querschnitt auch nicht.
        self.assertEqual((umrisse["Q4"], umrisse["Q5"]), ([], []))


class TestJeArtEigeneFelder(unittest.TestCase):
    """
    Jede Art eines Querschnitts hat ihre eigenen Felder: wer umschaltet,
    setzt nur die Art, und nach dem Zurückschalten stehen die alten Zahlen
    wieder da (Benutzer, 2026-11-19). Bis dahin teilten sich die Arten Masse
    und Bezug, und die Oberfläche räumte beim Umschalten ab.
    """

    def test_umschalten_ist_nur_die_art(self):
        p = traeger()
        q = p.balkensysteme[0].querschnitte[0]
        q.kennwerte = {"A": 1000.0, "I": 10.0}
        q.platte = p.platte("Decke", h=250).kennung
        # A in m²: der Streifen 1000 × 250 der Platte, 1000 mm² von Hand, das Rechteck 300 × 600.
        for art, A in (("platte", 0.25), ("kennwerte", 1e-3), ("vorlage", 0.18), ("platte", 0.25)):
            with self.subTest(art=art):
                q.art = art
                e = p.rechnen()
                self.assertAlmostEqual(e.wert(f"balkensystem.r1.{q.kennung}.A").groesse.si, A)


class TestEeq(unittest.TestCase):
    """
    E_eq aus einer Querschnittsanalyse bei N und M -- an derselben Stelle wie
    ihre Linie M–E_eq, für EA und EI jedes Stabs mit dem Querschnitt
    (Benutzer, 2026-10-23).
    """

    def projekt(self, **eq):
        """
        Der Träger, sein Stab mit dem Querschnitt der Analyse «Unterzug» und
        ihrem Material -- E_eq gilt für einen Stab gemäss Querschnitt.
        """
        p = traeger()
        s = p.balkensysteme[0]
        q = s.querschnitt_aus("Unterzug", "analyse", p.analyse("Unterzug"), E_eq=eq)
        s.linien[0].querschnitt = q.kennung
        s.linien[0].material = MATERIAL_DES_QUERSCHNITTS
        return p, q

    def linie(self, e, q, N=0.0):
        """Die Linie M–E_eq der Analyse selbst, gerechnet wie in ihrer Spannung-Dehnung-Analyse."""
        werte = e.loesung.werte
        paar = schnittpaar(e.aufbau.querschnittsanalysen["a1"], Zugseite.UNTEN,
                           lambda kid: werte[kid].groesse.si, q.eq.wahl)
        return aequivalenter_modul(moment_kruemmung(paar, N=N), I_c=paar.I_c, A_c=paar.A_c,
                                   E_cm=paar.E_cm)

    def test_ungerissen_wie_der_anfang_der_linie(self):
        p, q = self.projekt(M=0.0)
        e = p.rechnen()
        E = e.wert(f"balkensystem.r1.{q.kennung}.E").groesse.si
        self.assertAlmostEqual(E, self.linie(e, q).ungerissen, delta=1e-6 * E)

    def test_gerissen_auf_der_linie(self):
        """Bei 80 kNm gerissen: zwischen den beiden Punkten der Linie daneben, und weicher als ungerissen."""
        p, q = self.projekt(M=80.0)
        e = p.rechnen()
        E = e.wert(f"balkensystem.r1.{q.kennung}.E").groesse.si
        punkte = [pt for pt in self.linie(e, q).punkte if pt.gerissen and pt.modul is not None]
        vor = max((pt for pt in punkte if pt.kraft <= 80e3), key=lambda pt: pt.kraft)
        nach = min((pt for pt in punkte if pt.kraft >= 80e3), key=lambda pt: pt.kraft)
        self.assertLessEqual(min(vor.modul, nach.modul), E)
        self.assertLessEqual(E, max(vor.modul, nach.modul))
        self.assertLess(E, self.linie(e, q).ungerissen)
        # Dasselbe E für EA und EI.
        A = e.wert(f"balkensystem.r1.{q.kennung}.A").groesse.si
        self.assertAlmostEqual(
            e.wert(f"balkensystem.r1.{q.kennung}.{MATERIAL_DES_QUERSCHNITTS}.EA").groesse.si,
            E * A, delta=1e-6 * E * A)

    def test_ein_material_des_systems_nimmt_sein_e(self):
        """Mit dem Beton des Systems statt dem des Querschnitts gilt E_cm -- E_eq zählt nicht."""
        p, q = self.projekt(M=80.0)
        p.balkensysteme[0].linien[0].material = "M1"
        e = p.rechnen()
        A, E_cm = (e.wert(i).groesse.si for i in (f"balkensystem.r1.{q.kennung}.A", "beton.b1.E_cm"))
        self.assertAlmostEqual(e.wert(f"balkensystem.r1.{q.kennung}.M1.EA").groesse.si,
                               E_cm * A, delta=1e-9 * E_cm * A)

    def test_zu_grosses_moment_ist_eine_meldung(self):
        """Kein E_eq über dem Biegewiderstand: das System rechnet nicht und sagt warum."""
        p, q = self.projekt(M=1000.0)
        ergebnis = p.rechnen().balkensystem("r1").ergebnis
        self.assertFalse(ergebnis.gueltig)
        meldungen = [m.text for m in ergebnis.meldungen if m.fehler]
        self.assertEqual(len(meldungen), 1)
        self.assertIn("kein E_eq", meldungen[0])
        self.assertIn("Biegewiderstand", meldungen[0])

    def test_bei_einer_form_wartet_die_wahl(self):
        """
        E_eq gibt es nur aus einer Platte oder Analyse. Schaltet der
        Querschnitt auf eine Form, wartet die Wahl, statt dass er nicht
        rechnet; zurück bei der Analyse gilt wieder E_eq. Bis 2026-11-20
        setzte die Oberfläche sie beim Umschalten zurück.
        """
        p, q = self.projekt(M=80.0)
        q.art = "vorlage"
        self.assertIsNone(q.fehler())
        q.art = "analyse"
        self.assertIn("E-Modul, «Unterzug» (E_eq)", str(p.rechnen().bericht()))

    def test_herleitung(self):
        p, q = self.projekt(M=80.0)
        text = str(p.rechnen().bericht())
        for wort in ("Äquivalenter E-Modul, «Unterzug»", "der Querschnitt gilt gerissen",
                     "E-Modul, «Unterzug» (E_eq)", "Biegesteifigkeit, «Unterzug» mit E_eq"):
            self.assertIn(wort, text)


class TestEeqPlatte(unittest.TestCase):
    """
    E_eq aus einer Platte: immer in x-Richtung, Zug unten (Benutzer,
    2026-10-24) -- an derselben Stelle wie die Linie M–E_eq der Platte.
    """

    def projekt(self, **eq):
        """Der Träger mit dem Streifen der Platte «Decke» (h = 250 mm, M_Riss = 29 kNm)."""
        p = traeger()
        s = p.balkensysteme[0]
        q = s.querschnitt_aus("Streifen", "platte", p.platte("Decke", h=250), E_eq=eq)
        s.linien[0].querschnitt = q.kennung
        s.linien[0].material = MATERIAL_DES_QUERSCHNITTS
        return p, q

    def linie(self, e, q):
        """Die Linie M–E_eq der Platte in x, gerechnet wie in ihrer Spannung-Dehnung-Analyse."""
        werte = e.loesung.werte
        paar = loeserpaar(e.aufbau.querschnitte["q1"], Richtung.X,
                          lambda kid: werte[kid].groesse.si, q.eq.wahl)
        return aequivalenter_modul(moment_kruemmung(paar, N=0.0), I_c=paar.I_c, A_c=paar.A_c,
                                   E_cm=paar.E_cm)

    def test_ungerissen_wie_der_anfang_der_linie(self):
        p, q = self.projekt(M=20.0)
        e = p.rechnen()
        E = e.wert(f"balkensystem.r1.{q.kennung}.E").groesse.si
        self.assertAlmostEqual(E, self.linie(e, q).ungerissen, delta=1e-6 * E)

    def test_gerissen_auf_der_linie(self):
        p, q = self.projekt(M=40.0)
        e = p.rechnen()
        E = e.wert(f"balkensystem.r1.{q.kennung}.E").groesse.si
        punkte = [pt for pt in self.linie(e, q).punkte if pt.gerissen and pt.modul is not None]
        vor = max((pt for pt in punkte if pt.kraft <= 40e3), key=lambda pt: pt.kraft)
        nach = min((pt for pt in punkte if pt.kraft >= 40e3), key=lambda pt: pt.kraft)
        self.assertLessEqual(min(vor.modul, nach.modul), E)
        self.assertLessEqual(E, max(vor.modul, nach.modul))
        A = e.wert(f"balkensystem.r1.{q.kennung}.A").groesse.si
        self.assertAlmostEqual(
            e.wert(f"balkensystem.r1.{q.kennung}.{MATERIAL_DES_QUERSCHNITTS}.EA").groesse.si,
            E * A, delta=1e-6 * E * A)

    def test_ein_negatives_moment_hat_keines(self):
        p, q = self.projekt(M=-10.0)
        meldungen = [m.text for m in p.rechnen().balkensystem("r1").ergebnis.meldungen if m.fehler]
        self.assertEqual(len(meldungen), 1)
        self.assertIn("negatives Moment hat keines", meldungen[0])

    def test_herleitung(self):
        p, q = self.projekt(M=40.0)
        text = str(p.rechnen().bericht())
        self.assertIn("Platte «Decke», x-Richtung, Zug unten", text)
        self.assertIn("der Querschnitt gilt gerissen", text)
