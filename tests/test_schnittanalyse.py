"""
Die Spannung-Dehnung-Analyse am gezeichneten Querschnitt.

Gerechnet wird mit denselben Linien wie bei der Platte; geprueft wird darum,
dass der gezeichnete Querschnitt richtig zu ihnen kommt: dass Bild und
Randdehnungen zueinander passen, dass das Ende der M-χ-Linie der Widerstand
desselben Querschnitts ist, dass ein symmetrischer Querschnitt oben wie unten
gleich traegt und dass der Riss beim Rechteck die Formel der Platte ergibt.
"""

import math
import unittest

from opencivil import spannungsanalyse as sa
from opencivil.nachweis.rechenwahl import Rechenart, Rechenwahl
from opencivil.projekt import Projekt, ProjektFehler
from opencivil.projekt.querschnittsanalyse import (
    QASpannungsfallEintrag, QuerschnittsanalyseEintrag,
)
from opencivil.querschnitt.schnittanalyse import Zugseite, schnittpaar
from opencivil.web import dienst


def rechnen(projekt):
    aufbau = projekt.aufbauen()
    return aufbau, aufbau.werk.loese(*aufbau.alle_nachweisziele())


def paar_von(projekt, kennung, seite, wahl=Rechenwahl(art=Rechenart.PARABEL)):
    aufbau, loesung = rechnen(projekt)
    return schnittpaar(aufbau.querschnittsanalysen[kennung], seite,
                       lambda kid: loesung.werte[kid].groesse.si, wahl)


def rechteck(name="Rechteck", *, unten=16, oben=16):
    """Ein Rechteck 300 × 500 mm, je drei Stäbe unten und oben -- symmetrisch, wenn gleich."""
    p = Projekt(name=name)
    p.beton("C30/37")
    p.stahl("B500B")
    a = QuerschnittsanalyseEintrag(kennung=p.freie_kennung("a"), name="Balken")
    a.polygon([[0, 0], [300, 0], [300, 500], [0, 500]], material="b1")
    for z, d in ((50, unten), (450, oben)):
        a.stablinie([50, z], [250, z], art="anzahl", anzahl=3, durchmesser=d, stahl="s1")
    a.lastfall("Feld", M_y_Ed=100.0)
    p.querschnittsanalysen.append(a)
    return p, a.kennung


class TestBildUndDehnungen(unittest.TestCase):
    def test_hin_und_zurueck(self):
        """Aus N und M eine Ebene, ihre Randdehnungen zurück: wieder N und M."""
        p = Projekt.beispiel()
        for seite, N, M in ((Zugseite.UNTEN, -200e3, 150e3), (Zugseite.LINKS, -100e3, 40e3),
                            (Zugseite.OBEN, 0.0, 40e3)):
            paar = paar_von(p, "a1", seite)
            g = paar.gerissen
            hin = sa.aus_schnittgroessen(g, N=N, M=M)
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
        """Das Ende der M-χ-Linie ist der Bruchzustand des Querschnitts bei derselben Normalkraft."""
        p = Projekt.beispiel()
        for seite in (Zugseite.UNTEN, Zugseite.LINKS):
            paar = paar_von(p, "a1", seite)
            n_y, n_z = math.cos(seite.psi), math.sin(seite.psi)
            for N in (0.0, -300e3):
                linie = sa.moment_kruemmung(paar, N=N)
                punkt = paar.querschnitt.bei_normalkraft(seite.psi, N)
                widerstand = -(n_z * punkt.M_y + n_y * punkt.M_z)
                with self.subTest(seite=seite.value, N=N / 1e3):
                    self.assertAlmostEqual(linie.bruch.kraft / widerstand, 1.0, delta=2e-3)

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
        b, h = 0.3, 0.5
        k_t = 1.0 / (1.0 + 0.5 * h)
        self.assertAlmostEqual(self.paar.rissnormalkraft_bei(0.0), k_t * self.f_ctm * b * h,
                               delta=1e-3)
        # Ein Moment senkt sie, gleich in welche Richtung -- das Rechteck ist symmetrisch.
        for M in (20e3, -20e3):
            self.assertAlmostEqual(self.paar.rissnormalkraft_bei(M),
                                   k_t * self.f_ctm * b * h - 6.0 * abs(M) / h, delta=1e-3)

    def test_aequivalenter_modul_am_bruttoquerschnitt(self):
        self.assertAlmostEqual(self.paar.I_c, 0.3 * 0.5 ** 3 / 12.0, places=12)
        self.assertAlmostEqual(self.paar.A_c, 0.3 * 0.5, places=12)


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
        self.assertIn("Zugseite", str(fehler.exception))

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
