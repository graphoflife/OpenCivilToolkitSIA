"""
Die Breite gilt nur in x -- in y wird immer je Laufmeter gerechnet.

Eine Platte hat eine Angabe ``b``, und die beschreibt einen Streifen in
x-Richtung. Die Bewehrung in y liegt quer dazu und ist mit ihrer Teilung auf
den Laufmeter bezogen; sie hat von ``b`` nichts mitbekommen. Wer beide
Richtungen mit derselben Breite rechnet, bekommt bei b = 2000 mm in y den
doppelten Widerstand aus derselben Bewehrung.

Geprüft wird darum nicht eine Zahl, sondern ein Verhalten: was passiert, wenn
man ``b`` verdoppelt? In x muss sich alles mitbewegen, in y nichts.
"""

import unittest

from opencivil.projekt import Projekt
from opencivil.querschnitt.platte import BREITE_Y_MM, Richtung


def geloest(b_mm: float):
    projekt = Projekt.beispiel()
    q = projekt.querschnitte[0]
    q.b = b_mm
    # Die Beispielplatte trägt in beiden Richtungen: 2. und 3. Lage in x,
    # 1. und 4. in y. Genau das braucht dieser Test -- nachgewiesen wird zwar
    # nur x, aber die y-Bewehrung steht im Querschnitt und muss ihre eigene
    # Breite behalten.
    aufbau = projekt.aufbauen()
    return aufbau, aufbau.werk.loese(*aufbau.alle_nachweisziele())


def wert(loesung, kennung: str) -> float:
    return loesung.werte[kennung].groesse.si


class TestBreiteJeRichtung(unittest.TestCase):
    def setUp(self):
        self.einfach, self.l1 = geloest(1000.0)
        self.doppelt, self.l2 = geloest(2000.0)

    # -- Die Angabe selbst --------------------------------------------------

    def test_die_breite_in_y_haengt_nicht_an_der_eingabe(self):
        qs = self.doppelt.querschnitte["q1"]
        self.assertAlmostEqual(wert(self.l2, qs.id_von("b")), 2.0)
        self.assertAlmostEqual(wert(self.l2, qs.id_breite(Richtung.Y)),
                               BREITE_Y_MM / 1000.0)

    def test_id_breite_trennt_die_richtungen(self):
        qs = self.einfach.querschnitte["q1"]
        self.assertEqual(qs.id_breite(Richtung.X), qs.id_von("b"))
        self.assertNotEqual(qs.id_breite(Richtung.Y), qs.id_von("b"))

    # -- Bewehrungsquerschnitte ---------------------------------------------

    def _flaeche(self, loesung, marke: str) -> float:
        return wert(loesung, f"querschnitt.q1.lage.{marke}.a_s")

    def test_die_x_lage_waechst_mit_der_breite(self):
        """⌀18@150 auf 2000 mm sind doppelt so viel Stahl wie auf 1000 mm."""
        self.assertAlmostEqual(self._flaeche(self.l2, "2g"),
                               2.0 * self._flaeche(self.l1, "2g"), places=9)

    def test_die_y_lage_bleibt_wie_sie_war(self):
        self.assertAlmostEqual(self._flaeche(self.l2, "1g"),
                               self._flaeche(self.l1, "1g"), places=9)

    # -- Widerstände --------------------------------------------------------

    def _m_rd(self, aufbau, loesung, richtung: str) -> float:
        """M_Rd bei N_Ed = 0 -- der Eckwert, den die Bewehrung allein trägt."""
        nachweis = aufbau.nachweise[f"q1.{richtung}"]
        return wert(loesung, nachweis.d_eckwerte["M_Rd_N0_pos"].id)

    def test_der_momentenwiderstand_in_x_verdoppelt_sich(self):
        self.assertAlmostEqual(self._m_rd(self.doppelt, self.l2, "x"),
                               2.0 * self._m_rd(self.einfach, self.l1, "x"),
                               delta=10.0)

    # Einen Momentenwiderstand in y gibt es nicht mehr -- dort wird nichts
    # nachgewiesen. Dass die y-Bewehrung von `b` unberührt bleibt, prüft
    # `test_die_y_lage_bleibt_wie_sie_war` an der Fläche selbst; das ist die
    # Grösse, aus der ein Widerstand entstünde.

    # -- Bezogene Grössen ---------------------------------------------------

    def test_die_druckzonenhoehe_ist_von_der_breite_unabhaengig(self):
        """
        x = A_s·f_sd/(b·f_cd): stehen A_s und b in derselben Richtung, kürzt
        sich die Breite heraus. Genau das ist die Probe darauf, dass keine der
        beiden Grössen aus der falschen Richtung kommt.
        """
        for lage in (2, 3):  # beide in x -- die Duktilität läuft nur dort
            a = next(e for e in self.einfach.duktilitaet["q1"].ergebnisse
                     if e.lage.nummer == lage)
            b = next(e for e in self.doppelt.duktilitaet["q1"].ergebnisse
                     if e.lage.nummer == lage)
            with self.subTest(lage=lage):
                self.assertAlmostEqual(a.verhaeltnis, b.verhaeltnis, places=9)

    def test_das_bewehrungsmass_bleibt_dasselbe(self):
        """
        Dieselbe Platte, nur ein breiterer Streifen: je Kubikmeter Beton liegt
        gleich viel Stahl. Wäre die y-Lage mit b gerechnet, stiege die Zahl.
        """
        qs = self.einfach.querschnitte["q1"]
        self.assertAlmostEqual(wert(self.l1, qs.d_bewehrungsmass.id),
                               wert(self.l2, qs.d_bewehrungsmass.id),
                               places=6)


if __name__ == "__main__":
    unittest.main()
