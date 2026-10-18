"""
Die Spannung-Dehnung-Analyse am gezeichneten Querschnitt.

Gerechnet wird mit denselben Linien wie bei der Platte; geprueft wird darum,
dass der gezeichnete Querschnitt richtig zu ihnen kommt: dass Bild und
Randdehnungen zueinander passen, dass das Ende der M-χ-Linie der Widerstand
desselben Querschnitts ist, dass ein symmetrischer Querschnitt oben wie unten
gleich traegt und dass der Riss beim Rechteck die Formel der Platte ergibt.

Unter reiner Biegung kippt die Nulllinie eines unsymmetrischen Querschnitts,
bis kein Moment um die andere Achse bleibt (Benutzer, 2026-10-17);
«einachsig» bleibt sie parallel zur Achse der Biegung. Das pruefen die Tests
am L des Dateikopfs von :mod:`opencivil.spannungsanalyse.schnitt`.
"""

import math
import unittest

from opencivil import spannungsanalyse as sa
from opencivil.nachweis.rissgroessen import bruttoquerschnitt, rissmoment
from opencivil.querschnitt.gesetzwahl import Rechenart, Rechenwahl
from opencivil.projekt import Projekt, ProjektFehler
from opencivil.projekt.querschnittsanalyse import (
    QASpannungsfallEintrag, QuerschnittsanalyseEintrag,
)
from opencivil.spannungsanalyse import schnittpaar
from opencivil.querschnitt.zugseite import Zugseite
from opencivil.web import dienst


def rechnen(projekt):
    aufbau = projekt.aufbauen()
    return aufbau, aufbau.werk.loese(*aufbau.alle_nachweisziele())


def paar_von(projekt, kennung, seite, wahl=Rechenwahl(art=Rechenart.PARABEL)):
    aufbau, loesung = rechnen(projekt)
    return schnittpaar(aufbau.querschnittsanalysen[kennung], seite,
                       lambda kid: loesung.werte[kid].groesse.si, wahl)


def rechteck(name="Rechteck", *, unten=16, oben=16, einachsig=False):
    """Ein Rechteck 300 × 500 mm, je drei Stäbe unten und oben -- symmetrisch, wenn gleich."""
    p = Projekt(name=name)
    p.beton("C30/37")
    p.stahl("B500B")
    a = QuerschnittsanalyseEintrag(kennung=p.freie_kennung("a"), name="Balken",
                                   einachsig=einachsig)
    a.polygon([[0, 0], [300, 0], [300, 500], [0, 500]], material="b1")
    for z, d in ((50, unten), (450, oben)):
        a.stablinie([50, z], [250, z], art="anzahl", anzahl=3, durchmesser=d, stahl="s1")
    a.lastfall("Feld", M_y_Ed=100.0)
    p.querschnittsanalysen.append(a)
    return p, a.kennung


def l_querschnitt(*, einachsig=False):
    """Das L: Steg 200 × 800, Flansch 600 × 200 unten rechts; sechs ⌀20 unten, zwei ⌀16 oben."""
    p = Projekt(name="L")
    p.beton("C30/37")
    p.stahl("B500B")
    a = QuerschnittsanalyseEintrag(kennung=p.freie_kennung("a"), name="L", einachsig=einachsig)
    a.polygon([[0, 0], [600, 0], [600, 200], [200, 200], [200, 800], [0, 800]], material="b1")
    a.stablinie([50, 50], [550, 50], art="anzahl", anzahl=6, durchmesser=20, stahl="s1")
    a.stablinie([50, 750], [150, 750], art="anzahl", anzahl=2, durchmesser=16, stahl="s1")
    a.lastfall("Feld", M_y_Ed=100.0)
    p.querschnittsanalysen.append(a)
    return p, a.kennung


def widerstand(paar, seite, N):
    """Der Biegewiderstand der Tragsicherheit unter reiner Biegung, ohne Moment um die andere Achse."""
    M_y, M_z = seite.moment
    punkt = paar.querschnitt.in_richtung(N, M_y, M_z)
    return M_y * punkt.M_y + M_z * punkt.M_z


class TestBildUndDehnungen(unittest.TestCase):
    def test_hin_und_zurueck(self):
        """
        Aus N und M eine Ebene, ihre Randdehnungen zurück: wieder N und M --
        einachsig, wo die Randdehnungen die Ebene ganz beschreiben.
        """
        p = Projekt.beispiel()
        p.querschnittsanalysen[0].einachsig = True
        for seite, N, M in ((Zugseite.UNTEN, -200e3, 150e3), (Zugseite.LINKS, -100e3, 40e3),
                            (Zugseite.OBEN, 0.0, 40e3)):
            paar = paar_von(p, "a1", seite)
            g = paar.gerissen
            hin = sa.aus_schnittgroessen(paar.ebenen().gerissen, N=N, M=M, art=paar.wahl.art)
            with self.subTest(seite=seite.value):
                self.assertTrue(hin.konvergiert)
                zurueck = sa.aus_dehnungen(g, eps_oben=hin.eps_m + hin.chi * g.oben,
                                           eps_unten=hin.eps_m + hin.chi * g.unten)
                self.assertAlmostEqual(zurueck.N, N, delta=max(500.0, abs(N) * 1e-4))
                self.assertAlmostEqual(zurueck.M, M, delta=max(500.0, abs(M) * 1e-4))

    def test_staebe_gleicher_tiefe_sind_eine_lage(self):
        """Die drei Stäbe der unteren Linie haben dieselbe Dehnung: eine Lage im Bild."""
        p, kennung = rechteck()
        paar = paar_von(p, kennung, Zugseite.UNTEN)
        lagen = paar.gerissen.lagen
        self.assertEqual(len(lagen), 2)
        self.assertAlmostEqual(lagen[1].a_s, 3 * math.pi * 0.016 ** 2 / 4, places=12)
        self.assertEqual(lagen[1].text, "Linie 1")
        self.assertAlmostEqual(lagen[1].z, 0.45, places=9)


class TestDieLinie(unittest.TestCase):
    def test_ende_ist_der_widerstand_desselben_querschnitts(self):
        """
        Das Ende der M-χ-Linie ist der Bruchzustand des Querschnitts bei
        derselben Normalkraft: unter reiner Biegung -- am Unterzug kippt die
        Nulllinie bei Zug links, er ist oben breiter als unten --, einachsig
        in der festen Richtung.
        """
        for einachsig in (False, True):
            p = Projekt.beispiel()
            p.querschnittsanalysen[0].einachsig = einachsig
            for seite in (Zugseite.UNTEN, Zugseite.LINKS):
                paar = paar_von(p, "a1", seite)
                n_y, n_z = math.cos(seite.psi), math.sin(seite.psi)
                for N in (0.0, -300e3):
                    linie = sa.moment_kruemmung(paar, N=N)
                    if einachsig:
                        punkt = paar.querschnitt.bei_normalkraft(seite.psi, N)
                        traegt = -(n_z * punkt.M_y + n_y * punkt.M_z)
                    else:
                        traegt = widerstand(paar, seite, N)
                    with self.subTest(einachsig=einachsig, seite=seite.value, N=N / 1e3):
                        self.assertAlmostEqual(linie.bruch.kraft / traegt, 1.0, delta=2e-3)

    def test_symmetrisch_traegt_oben_wie_unten(self):
        p, kennung = rechteck()
        unten = sa.moment_kruemmung(paar_von(p, kennung, Zugseite.UNTEN), N=0.0)
        oben = sa.moment_kruemmung(paar_von(p, kennung, Zugseite.OBEN), N=0.0)
        self.assertAlmostEqual(oben.bruch.kraft / unten.bruch.kraft, 1.0, delta=1e-3)
        self.assertAlmostEqual(oben.riss, unten.riss, places=6)

    def test_mehr_bewehrung_unten_traegt_unten_mehr(self):
        p, kennung = rechteck(unten=20, oben=12)
        unten = sa.moment_kruemmung(paar_von(p, kennung, Zugseite.UNTEN), N=0.0)
        oben = sa.moment_kruemmung(paar_von(p, kennung, Zugseite.OBEN), N=0.0)
        self.assertGreater(unten.bruch.kraft, 1.5 * oben.bruch.kraft)


class TestDerRiss(unittest.TestCase):
    def setUp(self):
        p, kennung = rechteck()
        self.paar = paar_von(p, kennung, Zugseite.UNTEN)
        aufbau, loesung = rechnen(p)
        self.f_ctm = loesung.werte["beton.b1.f_ctm"].groesse.si

    def test_rissmoment_wie_beim_rechteck(self):
        """Am Rechteck b·h: M_Riss = k_t·f_ctm·b·h²/6, k_t für ein Drittel der Höhe."""
        b, h = 0.3, 0.5
        k_t = 1.0 / (1.0 + 0.5 * h / 3.0)
        self.assertAlmostEqual(self.paar.M_Riss, k_t * self.f_ctm * b * h ** 2 / 6.0, delta=1e-3)
        # Druck hebt es um N·h/6, wie bei der Platte.
        self.assertAlmostEqual(self.paar.rissmoment_bei(-100e3) - self.paar.M_Riss,
                               100e3 * h / 6.0, delta=1e-3)

    def test_rissnormalkraft_wie_beim_rechteck(self):
        """Unter Zug reisst die kleinere Abmessung, t = min(h; b) (Benutzer, 2026-10-17)."""
        b, h = 0.3, 0.5
        k_t = 1.0 / (1.0 + 0.5 * min(h, b))
        self.assertAlmostEqual(self.paar.rissnormalkraft_bei(0.0), k_t * self.f_ctm * b * h,
                               delta=1e-3)
        # Ein Moment senkt sie, gleich in welche Richtung -- das Rechteck ist symmetrisch.
        for M in (20e3, -20e3):
            self.assertAlmostEqual(self.paar.rissnormalkraft_bei(M),
                                   k_t * self.f_ctm * b * h - 6.0 * abs(M) / h, delta=1e-3)

    def test_aequivalenter_modul_am_bruttoquerschnitt(self):
        self.assertAlmostEqual(self.paar.I_c, 0.3 * 0.5 ** 3 / 12.0, places=12)
        self.assertAlmostEqual(self.paar.A_c, 0.3 * 0.5, places=12)


class TestKippendeNulllinie(unittest.TestCase):
    """Das L: unter reiner Biegung kippt seine Nulllinie, einachsig nicht."""

    @classmethod
    def setUpClass(cls):
        p, kennung = l_querschnitt()
        cls.unten = paar_von(p, kennung, Zugseite.UNTEN)
        cls.linie = sa.moment_kruemmung(cls.unten, N=0.0)
        p, kennung = l_querschnitt(einachsig=True)
        cls.einachsig = paar_von(p, kennung, Zugseite.UNTEN)

    def test_jede_ebene_ist_reine_biegung(self):
        """Kein Moment um die andere Achse -- nachgerechnet am Querschnitt, in M_y und M_z."""
        gerissen = self.unten.ebenen().gerissen
        for chi, e in ((0.001, gerissen.zur_kruemmung(0.001, 0.0)),
                       (0.005, gerissen.zur_kruemmung(0.005, 0.0)),
                       (self.linie.bruch.verformung, self.linie.bruch.ebene)):
            r = self.unten.querschnitt.richtung(Zugseite.UNTEN.psi + e.neigung)
            k = r.fasern.kraefte(e.eps_m, e.chi)
            M_y, M_z = r.momente(k.N, k.M, k.M_quer)
            with self.subTest(chi=chi):
                self.assertLess(abs(e.neigung), math.radians(90.0))
                self.assertNotEqual(e.neigung, 0.0)
                self.assertAlmostEqual(M_y, e.M, delta=1e-6 * abs(e.M))
                self.assertLess(abs(M_z), 1e-5 * abs(M_y))
                self.assertAlmostEqual(e.kruemmung, chi, delta=1e-12)

    def test_ende_ist_der_widerstand_unter_reiner_biegung(self):
        p, kennung = l_querschnitt()
        for seite, N in ((Zugseite.UNTEN, -500e3), (Zugseite.OBEN, 200e3),
                         (Zugseite.LINKS, 0.0), (Zugseite.RECHTS, -500e3)):
            paar = paar_von(p, kennung, seite)
            linie = sa.moment_kruemmung(paar, N=N)
            with self.subTest(seite=seite.value, N=N / 1e3):
                self.assertIsNotNone(linie.fliessen)
                self.assertAlmostEqual(linie.bruch.kraft / widerstand(paar, seite, N), 1.0,
                                       delta=2e-3)
        self.assertAlmostEqual(self.linie.bruch.kraft / widerstand(self.unten, Zugseite.UNTEN, 0.0),
                               1.0, delta=2e-3)

    def test_rissmoment_wie_beim_sproeden_versagen(self):
        """Dieselbe Ecke, dasselbe W -- am L nur halb so viel wie mit waagrechter Nulllinie."""
        aufbau, loesung = rechnen(l_querschnitt()[0])
        analyse = next(iter(aufbau.querschnittsanalysen.values()))
        brutto = bruttoquerschnitt(analyse, lambda kid: loesung.werte[kid].groesse.si)
        riss = rissmoment(brutto, 1.0, 0.0)
        self.assertEqual(self.unten.M_Riss, riss.M_Riss)
        self.assertEqual(self.linie.riss, riss.M_Riss)
        self.assertEqual(riss.ecke.punkt, (0, 0))
        self.assertLess(self.unten.M_Riss, 0.55 * self.einachsig.M_Riss)

    def test_einachsig_bleibt_die_nulllinie_waagrecht(self):
        linie = sa.moment_kruemmung(self.einachsig, N=0.0)
        self.assertEqual(linie.bruch.ebene.neigung, 0.0)
        # W = I_y/v, v bis zum unteren Rand: z_S = 300 mm.
        self.assertAlmostEqual(self.einachsig.W, self.einachsig.I / 0.3, delta=1e-12)

    def test_symmetrisch_kippt_nichts(self):
        """Am Rechteck trifft schon die Zugseite: dieselbe Linie wie einachsig, Stelle für Stelle."""
        kippend = paar_von(rechteck(unten=20)[0], "a1", Zugseite.UNTEN)
        fest = paar_von(rechteck(unten=20, einachsig=True)[0], "a1", Zugseite.UNTEN)
        a, b = sa.moment_kruemmung(kippend, N=-100e3), sa.moment_kruemmung(fest, N=-100e3)
        self.assertEqual([(p.kraft, p.verformung) for p in a.punkte],
                         [(p.kraft, p.verformung) for p in b.punkte])
        self.assertEqual(a.bruch.ebene.neigung, 0.0)

    def test_das_bild_nennt_die_neigung(self):
        bild = sa.aus_schnittgroessen(self.unten.ebenen().gerissen, N=0.0, M=150e3,
                                      art=self.unten.wahl.art)
        self.assertTrue(bild.konvergiert)
        self.assertAlmostEqual(bild.M, 150e3, delta=50.0)
        self.assertLess(bild.neigung, math.radians(-30.0))
        self.assertIn("gedreht", bild.hinweis)

    def test_der_reine_betonquerschnitt_kippt_mit(self):
        """
        I_c = I_y − I_yz²/I_z: so zeigt der ungerissene L, was ein ungerissener
        Rechteckquerschnitt zeigt -- E_c,eff und etwas für den Stahl.
        """
        b = self.unten.brutto
        self.assertAlmostEqual(self.unten.I_c, b.I_y - b.I_yz ** 2 / b.I_z, delta=1e-15)
        kippend = sa.aequivalenter_modul(self.linie, I_c=self.unten.I_c, A_c=self.unten.A_c,
                                         E_cm=self.unten.E_cm)
        fest = sa.aequivalenter_modul(sa.moment_kruemmung(self.einachsig, N=0.0),
                                      I_c=self.einachsig.I_c, A_c=self.einachsig.A_c,
                                      E_cm=self.einachsig.E_cm)
        self.assertAlmostEqual(kippend.ungerissen / fest.ungerissen, 1.0, delta=0.01)


class TestBeschreibung(unittest.TestCase):
    def test_hin_und_zurueck_als_datei(self):
        a = QuerschnittsanalyseEintrag(kennung="a1", name="A")
        a.spannungsfall("Links", art="moment_kruemmung", N_Ed=-50.0, richtung="links",
                        kriechzahl=1.5, rechenart="block")
        wieder = QuerschnittsanalyseEintrag.aus_dict(a.als_dict())
        self.assertEqual(wieder.spannungsfaelle, a.spannungsfaelle)
        self.assertIsInstance(wieder.spannungsfaelle[0], QASpannungsfallEintrag)

    def test_vorgabe_ist_zug_unten(self):
        self.assertEqual(QASpannungsfallEintrag.aus_dict({"name": "x"}).richtung, "unten")

    def test_unbekannte_zugseite_wird_gemeldet(self):
        with self.assertRaises(ProjektFehler) as fehler:
            QASpannungsfallEintrag.aus_dict({"name": "x", "richtung": "x"})
        self.assertIn("'x' gibt es als 'richtung' nicht. Möglich sind: unten, oben, links, "
                      "rechts", str(fehler.exception))

    def test_gleiche_namen_werden_gemeldet(self):
        p, kennung = rechteck()
        a = p.querschnittsanalysen[0]
        a.spannungsfall("Bild")
        a.spannungsfall("Bild", richtung="oben")
        with self.assertRaises(ProjektFehler):
            p.aufbauen()


class TestDurchDenDienst(unittest.TestCase):
    def test_die_analyse_kommt_mit_der_rechnung(self):
        p = Projekt.beispiel()
        p.querschnittsanalysen[0].spannungsfall("Steifigkeit", art="moment_kruemmung")
        antwort = dienst.rechnen({"projekt": p.als_dict()})
        faelle = antwort["spannungsanalysen"]["a1"]
        self.assertEqual(len(faelle), 1)
        fall = faelle[0]
        self.assertTrue(fall["moeglich"])
        self.assertEqual(fall["richtung_text"], "Zug unten")
        self.assertEqual(fall["bezugsort"], "im Schwerpunkt")
        self.assertGreater(fall["kurve"]["bruch"]["kraft"], 0.0)

    def test_fassade(self):
        p = Projekt.beispiel()
        p.querschnittsanalysen[0].spannungsfall("Bild", N_Ed=-100.0, M_Ed=100.0)
        bild, = p.rechnen().analysen()["a1"]
        self.assertTrue(bild.bild.konvergiert)
        self.assertAlmostEqual(bild.bild.M, 100e3, delta=50.0)


if __name__ == "__main__":
    unittest.main()
