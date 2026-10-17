"""
Knicken am gezeichneten Querschnitt.

Das Verfahren ist das der Platte; geprueft wird, dass der gezeichnete
Querschnitt richtig zu ihm kommt. Am Rechteck mit derselben Bewehrung muss
herauskommen, was die Platte rechnet -- dieselbe Grenzkraft. Dazu, was nur
er kennt: die Zugseite, zu der sich der Stab biegt, und die statische Hoehe
in dieser Richtung.
"""

import math
import unittest

from opencivil.nachweis.knicken import VERFORMUNG, WIDERSTAND
from opencivil.nachweis.qa_knicken import knickstab
from opencivil.projekt import Projekt, ProjektFehler
from opencivil.projekt.querschnittsanalyse import QAKnickEintrag, QuerschnittsanalyseEintrag
from opencivil.querschnitt.schnittanalyse import querschnitt_nach_wahl
from opencivil.querschnitt.zugseite import Zugseite


def stuetze(b=400, h=400):
    """Ein Rechteck b × h, je drei ⌀20 oben und unten, 50 mm vom Rand -- C30/37, B500B."""
    p = Projekt(name="Knicken")
    p.beton("C30/37")
    p.stahl("B500B")
    a = QuerschnittsanalyseEintrag(kennung="a1", name="Stütze")
    a.polygon([[0, 0], [b, 0], [b, h], [0, h]], material="b1")
    for z in (50, h - 50):
        a.stablinie([50, z], [b - 50, z], art="anzahl", anzahl=3, durchmesser=20, stahl="s1")
    p.querschnittsanalysen.append(a)
    return p, a


def urteile(projekt, *ids):
    aufbau = projekt.aufbauen()
    loesung = aufbau.werk.loese(*[f(aufbau).id for f in ids])
    return aufbau, {u.fall: u for u in loesung.urteile}


class TestWieDiePlatte(unittest.TestCase):
    def test_dieselbe_grenzkraft(self):
        """400 × 400 mit je drei ⌀20 -- die Platte mit 3 Stäben auf 400 mm rechnet dasselbe."""
        p, a = stuetze()
        platte = p.platte("Platte", h=400, b=400, x=(20, 20), y=(0, 0), teilung=400 / 3,
                          x_innen=False, ueberdeckung_unten=40, ueberdeckung_oben=40)
        platte.knickfall("Stütze", N_Ed=-1500.0, M_Ed_1=30.0, laenge=4.0)
        a.knickfall("Stütze", N_Ed=-1500.0, M_Ed_1=30.0, laenge=4.0)
        aufbau = p.aufbauen()
        loesung = aufbau.werk.loese(aufbau.knicken["q1"].id, aufbau.qa_knicken["a1"].id)
        n_rd = [u.widerstand.groesse.si for u in loesung.urteile]
        self.assertEqual(len(n_rd), 2)
        self.assertAlmostEqual(n_rd[1] / n_rd[0], 1.0, delta=1e-3)


class TestJeRichtung(unittest.TestCase):
    def test_symmetrisch_oben_wie_unten(self):
        p, a = stuetze()
        a.knickfall("unten", N_Ed=-1500.0, M_Ed_1=30.0, laenge=4.0)
        a.knickfall("oben", N_Ed=-1500.0, M_Ed_1=30.0, laenge=4.0, richtung="oben")
        _, gefunden = urteile(p, lambda au: au.qa_knicken["a1"])
        self.assertAlmostEqual(gefunden["unten"].widerstand.groesse.si,
                               gefunden["oben"].widerstand.groesse.si, delta=1.0)

    def test_statische_hoehe_in_zugrichtung(self):
        """300 breit, 500 hoch, Stäbe 50 mm vom Rand: d = 450 mm in z, 250 mm in y."""
        p, a = stuetze(b=300, h=500)
        a.knickfall("K", N_Ed=-500.0)
        aufbau = p.aufbauen()
        loesung = aufbau.werk.loese(aufbau.qa_knicken["a1"].id)
        q, _, _ = querschnitt_nach_wahl(aufbau.querschnittsanalysen["a1"],
                                        lambda kid: loesung.werte[kid].groesse.si, VERFORMUNG)
        for seite, d in ((Zugseite.UNTEN, 0.45), (Zugseite.OBEN, 0.45),
                         (Zugseite.LINKS, 0.25), (Zugseite.RECHTS, 0.25)):
            with self.subTest(seite=seite.value):
                self.assertAlmostEqual(knickstab(q, q, seite).d, d, places=9)

    def test_laenger_knickt_frueher(self):
        p, a = stuetze()
        a.knickfall("kurz", N_Ed=-1500.0, M_Ed_1=30.0, laenge=3.0)
        a.knickfall("lang", N_Ed=-1500.0, M_Ed_1=30.0, laenge=9.0)
        _, gefunden = urteile(p, lambda au: au.qa_knicken["a1"])
        self.assertLess(gefunden["lang"].widerstand.groesse.si,
                        gefunden["kurz"].widerstand.groesse.si)

    def test_ohne_druck_kein_nachweis(self):
        p, a = stuetze()
        a.knickfall("Zug", N_Ed=200.0)
        _, gefunden = urteile(p, lambda au: au.qa_knicken["a1"])
        self.assertTrue(gefunden["Zug"].erfuellt)
        self.assertTrue(math.isinf(gefunden["Zug"].erfuellungsgrad.si))


class TestBeschreibung(unittest.TestCase):
    def test_hin_und_zurueck(self):
        p, a = stuetze()
        a.knickfall("K", N_Ed=-800.0, M_Ed_1=12.0, laenge=4.0, knicklaenge=2.8, richtung="rechts")
        a.knicken_wahl_verformung.kriechzahl = 2.0
        self.assertEqual(QuerschnittsanalyseEintrag.aus_dict(a.als_dict()), a)

    def test_unbekannte_zugseite(self):
        with self.assertRaises(ProjektFehler):
            QAKnickEintrag.aus_dict({"name": "K", "richtung": "hinten"})

    def test_ausgeschaltet_kein_nachweis(self):
        p, a = stuetze()
        a.knickfall("K", N_Ed=-800.0).aktiv = False
        self.assertEqual(p.aufbauen().qa_knicken, {})

    def test_vorgaben_wie_bei_der_platte(self):
        _, a = stuetze()
        self.assertEqual(a.knicken_wahl_verformung.wahl, VERFORMUNG)
        self.assertEqual(a.knicken_wahl_widerstand.wahl, WIDERSTAND)


if __name__ == "__main__":
    unittest.main()
